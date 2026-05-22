"""
Advanced RAG Explorer - Backend Server
Features: CSV/Excel ingestion, ChromaDB + Nomic Embed, FlashRank Re-ranking, Groq LLM
"""

import os
import sys
import json
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# ── Force UTF-8 output on Windows ──────────────────────────────────
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ── Constants ──────────────────────────────────────────────────────
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "adv_chroma_db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"

os.makedirs(CHROMA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── FastAPI App ────────────────────────────────────────────────────
app = FastAPI(title="Advanced RAG Explorer API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ChromaDB Setup ────────────────────────────────────────────────
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(
    name="advanced_test_cases",
    metadata={"hnsw:space": "cosine"},
)

# ── FlashRank Re-ranker (lazy loaded) ─────────────────────────────
_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        try:
            # Use BGE Reranker via SentenceTransformers CrossEncoder
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder('bge-reranker-large')
            print("[OK] BGE Reranker loaded successfully")
        except Exception as e:
            print(f"[WARN] FlashRank unavailable, falling back to no re-ranking: {e}")
            _reranker = "unavailable"
    return _reranker


# ── Embedder (lazy loaded) ─────────────────────────────────────────
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        try:
            _embedder = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
            print("[OK] Nomic Embed (SentenceTransformers) loaded successfully")
        except Exception as e:
            print(f"[WARN] Nomic embed unavailable, using fallback: {e}")
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


# ── Pydantic Models ───────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    top_k_retrieve: int = 20
    top_k_rerank: int = 5
    groq_api_key: Optional[str] = None

class ChunkInfo(BaseModel):
    id: str
    content: str
    source: str
    chunk_index: int
    char_count: int
    row_range: str

class IngestionStats(BaseModel):
    filename: str
    total_rows: int
    total_chunks: int
    chunk_size: int
    chunk_overlap: int
    columns: List[str]
    chunks_preview: List[ChunkInfo]
    collection_total: int

class RerankedChunk(BaseModel):
    rank: int
    content: str
    source: str
    original_rank: int
    retrieval_score: float
    rerank_score: float

class QueryResponse(BaseModel):
    query: str
    chunks_retrieved: int
    chunks_reranked: int
    retrieved_chunks: List[dict]
    reranked_chunks: List[RerankedChunk]
    llm_response: str
    llm_model: str
    pipeline_steps: List[dict]


# ── Helper: Convert DataFrame rows to text documents ──────────────
def dataframe_to_documents(df: pd.DataFrame, source_name: str) -> List[dict]:
    """Convert each row of a DataFrame into a text document with all columns."""
    documents = []
    for idx, row in df.iterrows():
        parts = []
        for col in df.columns:
            value = str(row[col]).strip()
            if value and value.lower() != "nan":
                parts.append(f"{col}: {value}")
        text = "\n".join(parts)
        documents.append({
            "text": text,
            "metadata": {
                "source": source_name,
                "row_index": int(idx),
            }
        })
    return documents


# ── Helper: Chunk documents ───────────────────────────────────────
def chunk_documents(documents: List[dict], chunk_size: int = 800, chunk_overlap: int = 150):
    """Chunk the text documents using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    all_chunks = []
    for doc in documents:
        text = doc["text"]
        if len(text) <= chunk_size:
            # Small enough to be a single chunk
            all_chunks.append({
                "text": text,
                "source": doc["metadata"]["source"],
                "row_start": doc["metadata"]["row_index"],
                "row_end": doc["metadata"]["row_index"],
            })
        else:
            splits = splitter.split_text(text)
            for split in splits:
                all_chunks.append({
                    "text": split,
                    "source": doc["metadata"]["source"],
                    "row_start": doc["metadata"]["row_index"],
                    "row_end": doc["metadata"]["row_index"],
                })
    return all_chunks


# ── API: Upload & Ingest ──────────────────────────────────────────
@app.post("/upload", response_model=IngestionStats)
async def upload_file(
    file: UploadFile = File(...),
    chunk_size: int = Form(default=800),
    chunk_overlap: int = Form(default=150),
):
    """Upload a CSV/Excel file, chunk it, and store in ChromaDB."""
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()

    if ext not in (".csv", ".xlsx", ".xls"):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files (.csv, .xlsx, .xls) are supported.")

    # Save uploaded file
    save_path = os.path.join(UPLOAD_DIR, filename)
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    # Read into DataFrame
    try:
        if ext == ".csv":
            df = pd.read_csv(save_path)
        else:
            df = pd.read_excel(save_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")

    total_rows = len(df)
    columns = list(df.columns)

    # Convert rows to text documents
    documents = dataframe_to_documents(df, source_name=filename)

    # Chunk
    chunks = chunk_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # Prepare for ChromaDB
    ids = []
    texts = []
    metadatas = []
    chunks_preview = []

    source_hash = hashlib.md5(filename.encode()).hexdigest()[:8]

    for i, chunk in enumerate(chunks):
        chunk_id = f"{source_hash}_chunk_{i}"
        ids.append(chunk_id)
        texts.append(chunk["text"])
        metadatas.append({
            "source": chunk["source"],
            "chunk_index": i,
            "row_start": chunk["row_start"],
            "row_end": chunk["row_end"],
            "total_chunks": len(chunks),
            "ingested_at": datetime.now().isoformat(),
        })
        chunks_preview.append(ChunkInfo(
            id=chunk_id,
            content=chunk["text"][:300] + ("..." if len(chunk["text"]) > 300 else ""),
            source=chunk["source"],
            chunk_index=i,
            char_count=len(chunk["text"]),
            row_range=f"Row {chunk['row_start']}–{chunk['row_end']}",
        ))

    # Delete old data from same source to avoid duplicates
    try:
        existing = collection.get(where={"source": filename})
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    # Add to ChromaDB (batch if large)
    batch_size = 500
    for start in range(0, len(ids), batch_size):
        end = min(start + batch_size, len(ids))
        # Generate embeddings for this batch using SentenceTransformers (Nomic)
        batch_texts = texts[start:end]
        embedder = get_embedder()
        batch_embeddings = embedder.encode(batch_texts).tolist()
        
        collection.add(
            ids=ids[start:end],
            documents=batch_texts,
            embeddings=batch_embeddings,
            metadatas=metadatas[start:end],
        )

    return IngestionStats(
        filename=filename,
        total_rows=total_rows,
        total_chunks=len(chunks),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        columns=columns,
        chunks_preview=chunks_preview[:50],  # first 50 for preview
        collection_total=collection.count(),
    )


# ── API: Advanced Query with Re-ranking ───────────────────────────
@app.post("/query", response_model=QueryResponse)
async def advanced_query(request: QueryRequest):
    """Query the Advanced RAG pipeline: Retrieve -> Re-rank -> Generate."""
    query = request.query
    top_k_retrieve = request.top_k_retrieve
    top_k_rerank = request.top_k_rerank
    api_key = request.groq_api_key or GROQ_API_KEY

    pipeline_steps = []

    # ── Step 1: Broad Retrieval from ChromaDB ─────────────────────
    pipeline_steps.append({
        "step": 1,
        "name": "Vector Retrieval (ChromaDB + Nomic Embed)",
        "description": f"Querying ChromaDB for top {top_k_retrieve} chunks using cosine similarity",
        "status": "running"
    })

    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(top_k_retrieve, collection.count() or 1),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChromaDB query failed: {e}")

    if not results or not results["documents"] or not results["documents"][0]:
        raise HTTPException(status_code=404, detail="No documents found. Please upload and ingest data first.")

    retrieved_chunks = []
    for i, doc in enumerate(results["documents"][0]):
        distance = results["distances"][0][i] if results["distances"] else 0
        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
        retrieved_chunks.append({
            "rank": i + 1,
            "content": doc,
            "source": metadata.get("source", "Unknown"),
            "chunk_index": metadata.get("chunk_index", 0),
            "distance": round(float(distance), 4),
            "similarity": round(1 - float(distance), 4),
        })

    pipeline_steps[-1]["status"] = "done"
    pipeline_steps[-1]["result"] = f"Retrieved {len(retrieved_chunks)} chunks"

    # ── Step 2: Re-ranking with FlashRank Cross-Encoder ───────────
    pipeline_steps.append({
        "step": 2,
        "name": "Cross-Encoder Re-ranking (FlashRank)",
        "description": f"Re-scoring top {len(retrieved_chunks)} chunks with a cross-encoder to find the best {top_k_rerank}",
        "status": "running"
    })

    reranked_chunks = []
    reranker = get_reranker()

    if reranker and reranker != "unavailable":
        try:
            passages = [c["content"] for c in retrieved_chunks]
            # CrossEncoder expects list of [query, passage] pairs
            pairs = [[query, passage] for passage in passages]
            scores = reranker.predict(pairs)
            # Sort by score descending
            scored = sorted(zip(retrieved_chunks, scores), key=lambda x: x[1], reverse=True)
            reranked_chunks = []
            for new_rank, (chunk, score) in enumerate(scored[:top_k_rerank]):
                reranked_chunks.append(RerankedChunk(
                    rank=new_rank + 1,
                    content=chunk["content"],
                    source=chunk["source"],
                    original_rank=chunk["rank"],
                    retrieval_score=chunk["similarity"],
                    rerank_score=round(float(score), 4),
                ))
            pipeline_steps[-1]["status"] = "done"
            pipeline_steps[-1]["result"] = f"Re-ranked to top {len(reranked_chunks)} chunks"
        except Exception as e:
            pipeline_steps[-1]["status"] = "error"
            pipeline_steps[-1]["result"] = f"Re-ranking failed: {e}"
            # fallback use top retrieved chunks
            for i, c in enumerate(retrieved_chunks[:top_k_rerank]):
                reranked_chunks.append(RerankedChunk(
                    rank=i + 1,
                    content=c["content"],
                    source=c["source"],
                    original_rank=c["rank"],
                    retrieval_score=c["similarity"],
                    rerank_score=c["similarity"],
                ))
    else:
        # No re‑ranker available, use retrieved order
        for i, c in enumerate(retrieved_chunks[:top_k_rerank]):
            reranked_chunks.append(RerankedChunk(
                rank=i + 1,
                content=c["content"],
                source=c["source"],
                original_rank=c["rank"],
                retrieval_score=c["similarity"],
                rerank_score=c["similarity"],
            ))
        pipeline_steps[-1]["status"] = "skipped"
        pipeline_steps[-1]["result"] = "BGE‑Reranker unavailable, using retrieval scores"

    # ── Step 3: LLM Generation with Groq ──────────────────────────
    pipeline_steps.append({
        "step": 3,
        "name": "LLM Generation (Groq API)",
        "description": f"Sending top {len(reranked_chunks)} re-ranked chunks to {GROQ_MODEL} via Groq",
        "status": "running"
    })

    context = "\n\n---\n\n".join([f"[Chunk {c.rank}] (Source: {c.source}, Re-rank Score: {c.rerank_score})\n{c.content}" for c in reranked_chunks])

    system_prompt = """You are an expert QA Test Engineer. You analyze test case data and answer questions about testing.
When asked to create new test cases, format them with clear fields: Test ID, Title, Steps, Expected Result, Priority.
When asked about existing test cases, reference the exact data from the context provided.
Always be specific and actionable in your responses."""

    user_prompt = f"""Context from the test case database (retrieved and re-ranked by relevance):

{context}

---

User Question: {query}

Please provide a detailed, helpful response based on the context above."""

    llm_response = ""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
            )
            if resp.status_code != 200:
                error_body = resp.json()
                raise Exception(error_body.get("error", {}).get("message", f"HTTP {resp.status_code}"))
            data = resp.json()
            llm_response = data["choices"][0]["message"]["content"]
            pipeline_steps[-1]["status"] = "done"
            pipeline_steps[-1]["result"] = f"Generated response ({len(llm_response)} chars)"
    except Exception as e:
        llm_response = f"Error calling Groq API: {e}"
        pipeline_steps[-1]["status"] = "error"
        pipeline_steps[-1]["result"] = str(e)

    return QueryResponse(
        query=query,
        chunks_retrieved=len(retrieved_chunks),
        chunks_reranked=len(reranked_chunks),
        retrieved_chunks=retrieved_chunks,
        reranked_chunks=reranked_chunks,
        llm_response=llm_response,
        llm_model=GROQ_MODEL,
        pipeline_steps=pipeline_steps,
    )


# ── API: Collection Stats ────────────────────────────────────────
@app.get("/stats")
async def get_stats():
    """Get current ChromaDB collection statistics."""
    count = collection.count()
    sources = set()
    if count > 0:
        try:
            all_data = collection.get(limit=min(count, 1000))
            if all_data and all_data["metadatas"]:
                for m in all_data["metadatas"]:
                    sources.add(m.get("source", "Unknown"))
        except Exception:
            pass

    return {
        "total_chunks": count,
        "total_sources": len(sources),
        "sources": list(sources),
        "collection_name": "advanced_test_cases",
        "embedding_model": "Default (all-MiniLM-L6-v2)",
        "reranker_model": "bge-reranker-large (BGE‑Reranker)",
        "llm_model": GROQ_MODEL,
    }


# ── API: Get all chunks for visualization ────────────────────────
@app.get("/chunks")
async def get_all_chunks(limit: int = 100):
    """Return all stored chunks for UI visualization."""
    count = collection.count()
    if count == 0:
        return {"chunks": [], "total": 0}

    try:
        data = collection.get(limit=min(limit, count))
        chunks = []
        for i, doc in enumerate(data["documents"]):
            meta = data["metadatas"][i] if data["metadatas"] else {}
            chunks.append({
                "id": data["ids"][i],
                "content": doc[:300] + ("..." if len(doc) > 300 else ""),
                "full_content": doc,
                "source": meta.get("source", "Unknown"),
                "chunk_index": meta.get("chunk_index", i),
                "row_start": meta.get("row_start", 0),
                "row_end": meta.get("row_end", 0),
                "char_count": len(doc),
            })
        return {"chunks": chunks, "total": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── API: Health ───────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Advanced RAG Explorer", "version": "2.0"}


# ── Serve the HTML interface ─────────────────────────────────────
@app.get("/")
async def serve_ui():
    html_path = os.path.join(os.path.dirname(__file__), "advanced_rag_explorer.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return HTMLResponse("<h1>Advanced RAG Explorer</h1><p>UI file not found.</p>")


# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  Advanced RAG Explorer - Server Starting")
    print("=" * 60)
    print(f"  ChromaDB:   {CHROMA_DIR}")
    print(f"  Uploads:    {UPLOAD_DIR}")
    print(f"  LLM Model:  {GROQ_MODEL}")
    print(f"  Re-ranker:  BGE‑Reranker (bge-reranker-large)")
    print("=" * 60)
    print("  Open: http://localhost:8001")
    print("  Docs: http://localhost:8001/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8002)
