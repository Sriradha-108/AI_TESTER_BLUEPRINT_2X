"""QA Copilot — FastAPI backend with SSE chat, health, ingest, and save endpoints."""

from __future__ import annotations

import asyncio
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.lib.settings import settings
from backend.lib.session_store import SessionStore

# ── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(title="QA Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = SessionStore(ttl_minutes=settings.SESSION_TTL_MINUTES)

# ── Lazy-loaded heavy components ─────────────────────────────────────────────

_retriever = None
_groq_client = None


def get_retriever():
    global _retriever
    if _retriever is None:
        from backend.lib.embeddings import get_encoder
        from backend.lib.reranker import get_reranker
        from backend.lib.qdrant_store import get_store
        from backend.lib.retriever import Retriever

        store = get_store()
        encoder = get_encoder()
        reranker = get_reranker()
        _retriever = Retriever(store, encoder, reranker)
    return _retriever


def get_groq():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client


# ── Request/Response models ──────────────────────────────────────────────────


class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str
    force_collections: list[str] | None = None
    framework: str | None = None  # "selenium" | "playwright" | "auto" | None


class SaveRequest(BaseModel):
    message_id: str
    framework: str | None = None
    tc_id: str | None = None
    overwrite: bool = False


class IngestResponse(BaseModel):
    status: str
    detail: str


# ── Background task: session eviction ────────────────────────────────────────


@app.on_event("startup")
async def start_eviction_loop():
    async def evict_loop():
        while True:
            await asyncio.sleep(60)
            sessions.evict_stale()

    asyncio.create_task(evict_loop())


# ── Endpoints ────────────────────────────────────────────────────────────────


@app.get("/api/health")
async def health():
    """Return collection counts and model info."""
    from backend.lib.qdrant_store import get_store, COLLECTIONS

    store = get_store()
    counts = {}
    for name in COLLECTIONS:
        counts[name] = store.count(name)

    return {
        "status": "ok",
        "collections": counts,
        "groq_model": settings.GROQ_MODEL,
        "embed_model": settings.EMBED_MODEL,
        "rerank_model": settings.RERANK_MODEL,
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Chat endpoint with SSE streaming."""
    from backend.lib.query_rewriter import rewrite
    from backend.lib.router import route
    from backend.lib.answer_chain import detect_use_case, stream_answer

    session = sessions.get_or_create(req.session_id)

    # 1. Rewrite query using history
    rewritten = rewrite(session.history, req.message, get_groq(), settings.GROQ_MODEL)

    # 2. Detect use case
    use_case = detect_use_case(rewritten, req.framework)

    # 3. Route to collections
    collections = route(rewritten, req.force_collections, use_case, get_groq(), settings.GROQ_MODEL)

    # 4. Retrieve
    retriever = get_retriever()
    rerank_top_k = settings.RERANK_TOP_K
    if use_case == "find_similar":
        rerank_top_k = settings.RERANK_TOP_K_SIMILARITY

    chunks = retriever.retrieve(
        rewritten,
        collections,
        top_k_per_collection=settings.TOP_K_PER_COLLECTION,
        rerank_top_k=rerank_top_k,
        min_score=settings.MIN_RERANK_SCORE,
    )

    # 5. Generate message ID and store context
    message_id = str(uuid.uuid4())[:8]
    session.last_message_id = message_id
    session.last_chunks = chunks
    session.last_use_case = use_case
    session.last_framework = req.framework

    # 6. Stream response
    async def generate():
        # Send sources first
        citations = [c.to_citation() for i, c in enumerate(chunks)]
        for i, cit in enumerate(citations):
            cit["id"] = i + 1
        sources_event = json.dumps({"sources": citations, "message_id": message_id})
        yield f"event: sources\ndata: {sources_event}\n\n"

        # Stream tokens
        full_response = []
        async for token in stream_answer(
            user_query=req.message,
            rewritten_query=rewritten,
            history=session.history,
            chunks=chunks,
            use_case=use_case,
            framework=req.framework,
            groq_api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
        ):
            full_response.append(token)
            token_event = json.dumps({"text": token})
            yield f"event: token\ndata: {token_event}\n\n"

        # Update session history
        response_text = "".join(full_response)
        session.history.append({"role": "user", "content": req.message})
        session.history.append({"role": "assistant", "content": response_text})
        session.last_response_text = response_text

        # Done event
        done_event = json.dumps({"message_id": message_id})
        yield f"event: done\ndata: {done_event}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/ingest/{source}")
async def ingest(source: str):
    """Run an ingest script. source: selenium|playwright|testcases|pdfs|jira|all"""
    import importlib
    from concurrent.futures import ThreadPoolExecutor

    valid_sources = {"selenium", "playwright", "testcases", "pdfs", "jira", "all"}
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail=f"Invalid source: {source}. Must be one of {valid_sources}")

    module_name = f"backend.ingest.ingest_{source}"

    try:
        mod = importlib.import_module(module_name)
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Failed to import {module_name}: {e}")

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        try:
            await loop.run_in_executor(pool, mod.main)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ingest failed: {e}")

    return IngestResponse(status="ok", detail=f"Ingest '{source}' completed successfully.")


@app.post("/api/save")
async def save(req: SaveRequest):
    """Save generated content to disk."""
    from backend.lib.safe_paths import safe_resolve

    session = sessions.get_by_message_id(req.message_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session/message not found. Generate content first.")

    response_text = session.last_response_text
    use_case = session.last_use_case
    framework = req.framework or session.last_framework

    if not response_text:
        raise HTTPException(status_code=400, detail="No generated content to save.")

    if use_case == "generate_tc":
        # Append generated test case rows to CSV
        target = settings.TESTCASES_CSV.parent / "VWO_TestCase_generated.csv"
        target_resolved = safe_resolve(target)

        # Extract CSV/table content from response
        rows = _extract_tc_rows(response_text)
        if not rows:
            raise HTTPException(status_code=400, detail="Could not extract test case rows from response.")

        # Write or append
        write_header = not target_resolved.exists()
        target_resolved.parent.mkdir(parents=True, exist_ok=True)
        with open(target_resolved, "a", encoding="utf-8") as f:
            if write_header:
                f.write("Test Case ID,Test Case Name,Precondition,Test Steps,Expected Result,Priority\n")
            for row in rows:
                f.write(row + "\n")

        return {"written_path": str(target_resolved), "rows_appended": len(rows)}

    elif use_case == "generate_code":
        # Write code file
        if not framework or framework == "auto":
            framework = "playwright"  # default

        tc_id = req.tc_id or "generated"
        ext = "java" if framework == "selenium" else "ts"
        target = settings.GENERATED_DIR / framework / f"{tc_id}.{ext}"
        target_resolved = safe_resolve(target)

        if target_resolved.exists() and not req.overwrite:
            raise HTTPException(
                status_code=409,
                detail=f"File already exists: {target_resolved}. Set overwrite=true to replace.",
            )

        # Extract code block from response
        code = _extract_code_block(response_text, "java" if framework == "selenium" else "typescript")
        if not code:
            raise HTTPException(status_code=400, detail="Could not extract code block from response.")

        target_resolved.parent.mkdir(parents=True, exist_ok=True)
        target_resolved.write_text(code, encoding="utf-8")

        return {"written_path": str(target_resolved)}

    else:
        raise HTTPException(status_code=400, detail="No saveable content detected in this response.")


# ── Helpers ──────────────────────────────────────────────────────────────────


def _extract_code_block(text: str, lang: str) -> str | None:
    """Extract the first fenced code block matching the language."""
    # Try specific language fence
    pattern = rf"```(?:{lang}|{lang[:2]})\s*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Try any code fence
    match = re.search(r"```\w*\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return None


def _extract_tc_rows(text: str) -> list[str]:
    """Extract test case rows from generated text (CSV lines or table rows)."""
    rows = []

    # Try to find CSV-like lines (TC_* prefix)
    for line in text.split("\n"):
        line = line.strip()
        if re.match(r"TC_\w+", line) and "," in line:
            rows.append(line)

    if rows:
        return rows

    # Try markdown table rows
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("|") and "TC_" in line:
            # Remove leading/trailing pipes and split
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 4:
                rows.append(",".join(cells))

    return rows


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("  QA Copilot — Backend Starting")
    print(f"  Model: {settings.GROQ_MODEL}")
    print(f"  Qdrant: {settings.QDRANT_URL or settings.QDRANT_PATH}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
