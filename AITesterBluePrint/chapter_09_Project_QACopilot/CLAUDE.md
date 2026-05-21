# CLAUDE.md — QA Copilot

## Run Commands

```bash
# Install Python deps
pip install -r backend/requirements.txt

# Ingest all sources (clones repos if needed)
python -m backend.ingest.ingest_all

# Ingest individual source
python -m backend.ingest.ingest_testcases
python -m backend.ingest.ingest_selenium
python -m backend.ingest.ingest_playwright
python -m backend.ingest.ingest_pdfs
python -m backend.ingest.ingest_jira

# Start backend
uvicorn backend.main:app --reload --port 8000

# Start frontend
cd frontend && npm install && npm run dev
```

## Architecture

5-collection Qdrant store → LLM intent router → hybrid dense+sparse retrieval → cross-encoder rerank → Groq streaming answer with inline [N] citations → React SSE consumer.

**Key decision points:**
- Router: `backend/lib/router.py` — Groq classifier picks 1-2 collections per query
- Retrieval: `backend/lib/retriever.py` — parallel hybrid search, RRF fusion, rerank
- Answer: `backend/lib/answer_chain.py` — streaming with retry, use-case-specific prompts
- Prompts: `backend/lib/prompts.py` — all system prompts in one file

## How to Add a 6th Source

1. Create `backend/ingest/ingest_<name>.py` (follow existing pattern)
2. Add collection name to `COLLECTIONS` in `backend/lib/qdrant_store.py`
3. Add collection description + example to `ROUTER_SYSTEM` in `backend/lib/prompts.py`

## Payload Schemas per Collection

| Collection | Key metadata fields |
|---|---|
| `selenium_code` | repo, source_path, start_line, end_line, symbol, kind, annotations |
| `playwright_code` | repo, source_path, start_line, end_line, symbol, kind, test_title |
| `vwo_testcases` | tc_id, tc_name, priority, precondition, steps, expected_result |
| `vwo_docs` | doc_title, page, section, source_path |
| `vwo_bugs` | jira_id, summary, status, priority, reporter, assignee, created |

All payloads also include: `source_type`, `text`, `chunk_index`, `source_path`.

## SSE Event Protocol

`POST /api/chat` returns `text/event-stream` with three event types:

```
event: sources
data: {"sources": [...citations], "message_id": "abc"}

event: token
data: {"text": "partial token"}

event: done
data: {"message_id": "abc"}
```

Order: `sources` (once) → `token` (many) → `done` (once).

## Common Pitfalls

1. **Qdrant file-store single-process:** Cannot run ingest and server simultaneously in file-store mode. Stop the server before re-ingesting, or switch to HTTP mode (`QDRANT_URL`).
2. **bge-m3 first load:** Downloads ~2GB on first run. Cached in HuggingFace cache dir after that.
3. **tree-sitter wheels:** `tree-sitter-languages` provides pre-built wheels. If install fails on your platform, try `pip install --no-build-isolation tree-sitter-languages`.
4. **Windows encoding:** The backend forces UTF-8 on Windows. If you see encoding errors, ensure your terminal supports UTF-8.
5. **Groq rate limits:** The answer chain retries 3x with exponential backoff. If you hit persistent limits, reduce `TOP_K_PER_COLLECTION` or switch to a smaller model.

## Reused Patterns

- Chunking and embedding patterns ported from `Chapter_08_RAG/Advance_RAG_Explain/advanced_rag_server.py`
- FastAPI + CORS structure from same file
- CSV row-to-document conversion from `dataframe_to_documents()` in Chapter 8
