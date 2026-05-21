# QA Copilot — Implementation Tasks

This file is the executable checklist for building QA Copilot. Tasks are grouped into the four phases from `Plan.md` and ordered to respect dependencies. Each task references the requirement(s) it satisfies (e.g., `[Req 7.1, 7.2]`).

Conventions:
- All paths are relative to `chapter_09_Project_QACopilot/`.
- A task is "done" when its acceptance line passes locally.
- Each phase ends with a verification step.

---

## Phase 1 — Skeleton, Config, and Ingestion

Goal: project scaffolding, config loading, five working ingest scripts, populated Qdrant store.

- [ ] **1.1 Create directory skeleton**
  - Create empty dirs: `backend/`, `backend/lib/`, `backend/ingest/`, `frontend/`, `frontend/src/`, `frontend/src/components/`, `frontend/src/api/`, `frontend/src/styles/`, `data/csv/`, `data/pdf/`, `data/md/`, `data/generated/selenium/`, `data/generated/playwright/`.
  - Add `__init__.py` to `backend/`, `backend/lib/`, `backend/ingest/`.
  - _[Reference: Design "Directory layout"]_

- [ ] **1.2 Write `.gitignore`**
  - Ignore: `qdrant_data/`, `node_modules/`, `.venv/`, `data/selenium_repo/`, `data/playwright_repo/`, `data/_skip_report.json`, `data/generated/`, `.env`, `__pycache__/`, `*.pyc`, `.DS_Store`.
  - _[Req 20.5, 20.6]_

- [ ] **1.3 Write `.env.example`**
  - Include every variable from design `Settings` class with safe defaults.
  - `GROQ_API_KEY` left blank with a `# REQUIRED` comment.
  - _[Req 18.1, 18.2, 18.3]_

- [ ] **1.4 Write `backend/requirements.txt`**
  - Use the exact pinned dep list from design "Required Python deps" section.
  - _[Design "Configuration & deployment"]_

- [ ] **1.5 Implement `backend/lib/settings.py`**
  - `pydantic-settings` `BaseSettings` class with all fields defined in design.
  - Module-level `settings = Settings()` singleton; raises clear error if `GROQ_API_KEY` missing.
  - _[Req 18.4, 18.5]_

- [ ] **1.6 Implement `backend/lib/embeddings.py`**
  - `BGE_M3_Encoder` class wrapping `FlagEmbedding.BGEM3FlagModel`.
  - Lazy `get_encoder()` singleton.
  - `.encode(texts)` returns `[{"dense": np.ndarray, "sparse": dict[int, float]}, ...]`.
  - _[Design "lib/embeddings.py"]_

- [ ] **1.7 Implement `backend/lib/reranker.py`**
  - `Reranker` class wrapping `FlagEmbedding.FlagReranker`.
  - Lazy `get_reranker()` singleton.
  - `.score(query, passages)` returns list of floats.
  - _[Req 8.4, Design "lib/reranker.py"]_

- [ ] **1.8 Implement `backend/lib/qdrant_store.py`**
  - `COLLECTIONS` constant (5 names).
  - `QdrantStore` class: file-store vs HTTP mode auto-pick from settings.
  - `ensure_collection(name)` — creates with `dense` (size=1024, COSINE) and `sparse` named vectors. Idempotent.
  - On config mismatch, raise `RuntimeError` with instruction to clear `qdrant_data/`.
  - `upsert(name, points)`, `count(name)`, `hybrid_search(name, dense, sparse, top_k)` using Qdrant Query API with prefetch + RRF fusion.
  - _[Req 7.1–7.6, Req 8.1–8.3]_

- [ ] **1.9 Implement `backend/lib/chunking_text.py`**
  - `chunk_testcase_row(row)` — joins row fields with labels, returns `ChunkRecord`.
  - `parse_jira_markdown(path)` — extracts `[KAN-N]` from first line, parses key:value header block, returns `(metadata_dict, body_str)`.
  - `chunk_jira_body(metadata, body, chunk_size, overlap)` — single chunk if ≤1500 chars, else `RecursiveCharacterTextSplitter`.
  - _[Req 3.2, 3.3, 5.2, 5.3, 5.4]_

- [ ] **1.10 Implement `backend/lib/chunking_md_pdf.py`**
  - `extract_pdf_text(path)` using PyMuPDF, returns `[(page_no, text), ...]`.
  - `is_pdf_too_short(pages)` — total chars < 50.
  - `split_pdf_text(pages, chunk_size, overlap)` — header-aware splitter, preserves source page per chunk; nearest preceding header line stored in `section`.
  - _[Req 4.1, 4.2, 4.3, 4.4]_

- [ ] **1.11 Implement `backend/lib/chunking_code.py`**
  - Use `tree_sitter_languages.get_language("java")` and `get_language("typescript")`.
  - `chunk_java_file(path)` — emit one chunk per top-level class and per method; capture `symbol`, `kind`, `start_line`, `end_line`, `annotations` (collected from preceding annotation nodes).
  - `chunk_ts_file(path)` — emit one chunk per function, class, and `test(...)` call; capture `symbol`, `kind`, `test_title`.
  - On parse error, log warning and return `[]` for that file.
  - _[Req 1.3, 1.4, 1.6, Req 2.3, 2.4, 2.6]_

- [ ] **1.12 Implement `backend/ingest/_git_utils.py`**
  - `ensure_repo(local_dir, url, log)` — clone if absent or `.git` missing, else `git pull --ff-only`.
  - Uses `subprocess.check_call` with `["git", ...]`.
  - _[Req 1.1, 1.2, 2.1, 2.2]_

- [ ] **1.13 Implement common ingest helper**
  - In `backend/ingest/__init__.py`: `stable_id(prefix, *parts) -> str` (md5 hex truncated to 24), `batched(iterable, n)`, `build_point(chunk, dense, sparse)`.
  - _[Design "Point ID strategy", "Common pattern"]_

- [ ] **1.14 Implement `backend/ingest/ingest_selenium.py`**
  - Uses `_git_utils.ensure_repo` for `SELENIUM_REPO_URL`.
  - Walks `data/selenium_repo/**/*.java`, calls `chunk_java_file`, embeds, upserts to `selenium_code`.
  - Final summary print line per design.
  - Has `if __name__ == "__main__": main()`.
  - _[Req 1.1–1.7]_

- [ ] **1.15 Implement `backend/ingest/ingest_playwright.py`**
  - Mirrors 1.14 for Playwright repo; matches `*.ts`, `*.tsx`, `*.js`, `*.jsx`.
  - Upserts to `playwright_code`.
  - _[Req 2.1–2.7]_

- [ ] **1.16 Implement `backend/ingest/ingest_testcases.py`**
  - Reads `TESTCASES_CSV` with `pandas`.
  - One row → one `ChunkRecord` via `chunk_testcase_row`.
  - Tolerates the basic 6-column schema and the extended schema.
  - Upserts to `vwo_testcases`.
  - _[Req 3.1–3.6]_

- [ ] **1.17 Implement `backend/ingest/ingest_pdfs.py`**
  - Iterates `PDFS_DIR/*.pdf`, runs `extract_pdf_text` then `is_pdf_too_short`.
  - On skip, append `{path, reason, char_count}` to `data/_skip_report.json` (rewrite list each run).
  - Upserts to `vwo_docs`.
  - _[Req 4.1–4.6]_

- [ ] **1.18 Implement `backend/ingest/ingest_jira.py`**
  - Iterates `JIRA_MD_DIR/*.md`, runs `parse_jira_markdown` then `chunk_jira_body`.
  - On missing header block, derive `jira_id` from filename (e.g., `Bug_KAN-2.md` → `KAN-2`) and log warning.
  - Upserts to `vwo_bugs`.
  - _[Req 5.1–5.7]_

- [ ] **1.19 Implement `backend/ingest/ingest_all.py`**
  - Runs the five scripts in order.
  - Catches exceptions per step, prints traceback, continues.
  - Final summary table; exit 0/1 per Req 6.4.
  - _[Req 6.1–6.4]_

- [ ] **1.20 Phase 1 verification**
  - Stage data: drop the existing `csv/VWO_TestCase.csv`, `pdf/*.pdf`, `md/Bug_*.md` into `data/` (move from current top-level `csv/`, `pdf/`, `md/` if needed).
  - Run: `python -m backend.ingest.ingest_all`.
  - Acceptance:
    - All five collections show non-zero counts in `qdrant_data/`.
    - `data/_skip_report.json` either absent or contains entries only for genuinely empty PDFs.
    - Re-running ingest does not change chunk counts (idempotency, Req 20.2).

---

## Phase 2 — Backend Retrieval & API

Goal: live FastAPI server with chat, health, ingest, and save endpoints.

- [ ] **2.1 Implement `backend/lib/prompts.py`**
  - `ROUTER_SYSTEM`, `REWRITE_SYSTEM`, `ANSWER_SYSTEM` (full prompts from design).
  - Helper `render_context(chunks)` → `<doc id="N" ...>text</doc>` tagged blocks.
  - _[Req 8.6, Req 9.1, Req 10.2, Design "lib/router.py" / "lib/answer_chain.py"]_

- [ ] **2.2 Implement `backend/lib/router.py`**
  - `route(query, force_collections, use_case=None)` — bypass router when `force_collections` set, otherwise call Groq classifier.
  - JSON-array parse with fallback to all-five on malformed output.
  - _[Req 9.1–9.5]_

- [ ] **2.3 Implement `backend/lib/query_rewriter.py`**
  - `rewrite(history, latest)` — skip if no history, otherwise condense via Groq with `temperature=0`.
  - _[Req 10.2, 10.3, 10.5]_

- [ ] **2.4 Implement `backend/lib/retriever.py`**
  - `Retriever.retrieve(query, collections, rerank_top_k)` — hybrid search per collection, merge, rerank, apply `MIN_RERANK_SCORE` gate (with at-least-1 fallback).
  - Parallel collection queries via `ThreadPoolExecutor`.
  - _[Req 8.1–8.6, Req 12.4]_

- [ ] **2.5 Implement `backend/lib/session_store.py`**
  - In-memory `dict[str, SessionState]`.
  - `SessionState` holds `history: list[Turn]`, `last_seen`, `last_chunks`, `last_message_id`, `last_use_case`, `last_framework`.
  - `evict_stale()` removes entries older than `SESSION_TTL_MINUTES`.
  - _[Req 10.1, 10.6]_

- [ ] **2.6 Implement `backend/lib/answer_chain.py`**
  - `detect_use_case(query, framework)` — regex/keyword classifier returning one of `generate_tc | find_similar | generate_code | None`.
  - `stream_answer(...)` async generator yielding `StreamEvent` objects.
  - Groq streaming via `groq.AsyncGroq`; backoff retry (3x) on rate-limit / 5xx.
  - _[Req 11.2, 11.3, Req 12.1–12.4, Req 13.1–13.5, Req 20.3]_

- [ ] **2.7 Implement `backend/lib/safe_paths.py`**
  - `safe_resolve(path)` — guards against traversal, allow-list of write dirs.
  - _[Req 14.4, Req 20.4]_

- [ ] **2.8 Implement `backend/main.py` — FastAPI app**
  - CORS middleware allowing `http://localhost:5173` and `http://localhost:8000`.
  - Background task on startup: periodic `session_store.evict_stale()`.
  - Endpoints:
    - `POST /api/chat` — full pipeline, SSE response with `sources` → `token*` → `done` events.
    - `GET /api/health` — collection counts + model info.
    - `POST /api/ingest/{source}` — runs corresponding script via `run_in_threadpool`.
    - `POST /api/save` — UC1 appends to `VWO_TestCase_generated.csv`, UC3 writes to `data/generated/<framework>/<tc_id>.<ext>`.
  - _[Req 16.1–16.6, Req 14.1–14.5]_

- [ ] **2.9 Phase 2 verification**
  - Run: `uvicorn backend.main:app --reload --port 8000`.
  - Acceptance:
    - `curl http://localhost:8000/api/health` returns the five collection counts.
    - `curl -N -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"session_id":"t1","message":"List High priority test cases for SQL injection"}'` streams SSE with at least one `event: sources` and several `event: token` blocks.
    - Bad save path (`{"target_path":"../../etc/passwd"}`) returns 400.

---

## Phase 3 — Frontend

Goal: working React + Vite + Tailwind app at `http://localhost:5173`.

- [ ] **3.1 Initialize Vite project**
  - `frontend/package.json` per design "Required JS deps".
  - `tsconfig.json` with strict mode, `moduleResolution: "bundler"`.
  - `vite.config.ts` with React plugin and `/api` proxy to `:8000` preserving SSE.
  - `tailwind.config.js`, `postcss.config.js`, `frontend/src/styles/index.css` (`@tailwind` directives).
  - `index.html` with root div.
  - `src/main.tsx` mounting `<App />`.
  - _[Req 17.1, 17.6]_

- [ ] **3.2 Implement `src/api/types.ts`**
  - TypeScript types for `Citation` (discriminated union by `source_type`), `Message`, `ChatRequest`, `HealthResponse`, `SaveRequest`, `SSEEvent`.
  - _[Design "State model"]_

- [ ] **3.3 Implement `src/api/client.ts`**
  - `chatStream(req, callbacks)` — POST to `/api/chat`, parse SSE manually from `ReadableStream`. Callbacks: `onSources`, `onToken`, `onDone`, `onError`.
  - `getHealth()`, `runIngest(source)`, `saveMessage(req)` — typed fetch wrappers.
  - _[Design "ChatPane.tsx" SSE handling]_

- [ ] **3.4 Implement `src/components/IngestStatus.tsx`**
  - Polls `/api/health` on mount.
  - Renders five rows: collection name + count + "Re-ingest" button.
  - "Re-ingest all" button at the bottom.
  - _[Req 17.5]_

- [ ] **3.5 Implement `src/components/SourceFilter.tsx`**
  - Five checkboxes; emits `forceCollections: string[]` upward.
  - Framework toggle (`auto | selenium | playwright`) included here per design.
  - _[Req 9.4, Req 13.1, Req 17.4]_

- [ ] **3.6 Implement `src/components/SourceCard.tsx`**
  - Discriminated rendering by `source_type`, headers per design Req 15.3 layout.
  - Expandable body showing full chunk text.
  - Accepts `ref` for scroll-into-view.
  - _[Req 15.3, 15.5]_

- [ ] **3.7 Implement `src/components/SourcePanel.tsx`**
  - Receives `citations` for the most recent assistant message.
  - Renders `SourceCard` list and exposes `scrollToCard(n)` via `useImperativeHandle`.
  - _[Req 15.3, 15.4]_

- [ ] **3.8 Implement `src/components/MessageBubble.tsx`**
  - Renders user/assistant turn with `react-markdown` + `remark-gfm`.
  - Code fences with syntax highlighting for `java` and `typescript`.
  - Post-processes `[N]` markers into `<button class="citation-chip">` that calls a passed-in `onCitationClick(n)`.
  - Renders `<SaveButton />` if `message.saveable` is set.
  - _[Req 15.1, 15.2, 17.3, Req 14.2]_

- [ ] **3.9 Implement `src/components/SaveButton.tsx`**
  - Calls `saveMessage()` with the message's `saveable` info.
  - On success: green toast with `written_path`. On 409: prompts confirm and retries with `overwrite=true`.
  - _[Req 14.2, 14.3, 14.5]_

- [ ] **3.10 Implement `src/components/ChatPane.tsx`**
  - State: messages, input value, streaming flag.
  - On submit: opens `chatStream`, appends a placeholder assistant message, fills tokens in.
  - Detects use case from response's `source_type`s and message content; sets `saveable` when applicable.
  - _[Req 14.2, Req 17.3]_

- [ ] **3.11 Implement `src/App.tsx`**
  - Three-pane CSS grid layout (Tailwind).
  - Generates a stable `session_id` per browser tab (sessionStorage).
  - Wires `SourceFilter` → `ChatPane` → `SourcePanel`.
  - _[Req 17.1, 17.2]_

- [ ] **3.12 Phase 3 verification**
  - `cd frontend && npm install && npm run dev`.
  - Open `http://localhost:5173`. Run the five smoke questions from `requirements.md` "Verification" / `Plan.md`:
    1. `selenium_code`: "Show the BasePage waitForElement implementation"
    2. `playwright_code`: "How is the login fixture set up in Playwright?"
    3. `vwo_testcases`: "List High priority test cases for SQL injection scenarios"
    4. `vwo_docs`: "What does the PRD say about login dashboard auth flow?"
    5. `vwo_bugs`: "Show open bugs related to login failures"
  - Acceptance: each answer renders Markdown, has clickable `[N]` chips that scroll the matching `SourceCard` into view, and source cards show source-specific metadata.

---

## Phase 4 — Polish

Goal: docs, end-to-end UC validation, project entry in repo root.

- [ ] **4.1 Verify UC1 — Generate test cases from JIRA**
  - In UI: send "Create test cases from KAN-3".
  - Acceptance: Markdown response contains 3+ rows in CSV column order; `[N]` cites at least one `vwo_bugs` chunk; "Save to disk" button appears; clicking it appends to `data/csv/VWO_TestCase_generated.csv`.
  - _[Req 11.1–11.4]_

- [ ] **4.2 Verify UC2 — Find similar test cases**
  - Send "Do we already have a test for SQL injection in password?".
  - Acceptance: response is bullet list; ≥3 results when matches exist; "no close match found" disclaimer triggers when sending an obviously unrelated query (e.g., "test for paying with bitcoin"); `RERANK_TOP_K_SIMILARITY=8` is honored (≤8 hits).
  - _[Req 12.1–12.4]_

- [ ] **4.3 Verify UC3 — Generate automation code**
  - Toggle framework to `playwright`. Send "Generate Playwright code for TC_LOGIN_009".
  - Acceptance: response contains a complete fenced ```typescript block including imports + `test(...)` block; cites `playwright_code` chunks and `vwo_testcases:TC_LOGIN_009`; Save writes `data/generated/playwright/TC_LOGIN_009.ts`; second save without `overwrite` returns 409.
  - Repeat with framework `selenium` and a different TC; verify file at `data/generated/selenium/<id>.java`.
  - _[Req 13.1–13.6]_

- [ ] **4.4 Performance smoke**
  - Time a 1-collection warm-cache query first-token latency. Acceptance: < 3s on a typical dev laptop.
  - _[Req 20.1]_

- [ ] **4.5 Idempotency check**
  - Run `ingest_all` a second time without changing data. Acceptance: chunk counts unchanged.
  - _[Req 20.2]_

- [ ] **4.6 Write `chapter_09_Project_QACopilot/README.md`**
  - Sections: intro, architecture (Mermaid from design), prerequisites, install, env, ingest, run backend, run frontend, five smoke questions, "How to add a sixth source" (3 steps: ingest script, add to `qdrant_store.COLLECTIONS`, add to router prompt taxonomy).
  - _[Req 19.1]_

- [ ] **4.7 Write `chapter_09_Project_QACopilot/CLAUDE.md`**
  - Per design / Plan.md content list: run commands, big-picture architecture, payload schemas table, SSE event protocol, common pitfalls (Qdrant single-process file-store, `bge-m3` first-load size, tree-sitter wheels), pointers to reused patterns.
  - _[Req 19.2]_

- [ ] **4.8 Update root `README.md`**
  - Add Chapter 9 entry pointing at this directory with one-line description.
  - _[Req 19.3]_

- [ ] **4.9 Optional: `docker-compose.yml`**
  - Single `qdrant` service from design "Optional: Qdrant HTTP mode via Docker". Documented but not required for default flow.
  - _[Design "Configuration & deployment"]_

- [ ] **4.10 Final end-to-end run**
  - Fresh clone simulation: delete `qdrant_data/`, `data/selenium_repo/`, `data/playwright_repo/`, `node_modules/`, `.venv/`. Re-run the full setup commands from README.
  - Acceptance: complete the five smoke questions and the three UC verifications without manual intervention beyond the commands listed in README.

---

## Out of scope (parked)

- Live Jira REST integration (stays in design assumptions).
- Authentication / multi-user sessions.
- Embedding model fine-tuning.
- Persistent session storage (beyond in-memory).
- Test suite — not auto-generated per project goal.
