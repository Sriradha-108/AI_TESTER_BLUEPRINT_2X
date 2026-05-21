# QA Copilot — Requirements

## Introduction

QA Copilot is a Retrieval-Augmented Generation (RAG) application built in `chapter_09_Project_QACopilot/` that lets QA engineers ask natural-language questions and receive cited answers grounded in five heterogeneous QA artifacts:

1. Selenium Java/TestNG framework (cloned from `PramodDutta/ATB14xSeleniumAdvanceFrameworks`)
2. Playwright TypeScript framework (cloned from `PramodDutta/Advance-Playwright-Framework`)
3. VWO test case corpus (`data/csv/VWO_TestCase.csv`, 50 login-focused rows currently)
4. VWO product PDFs in `data/pdf/` (PRDs, specs)
5. VWO JIRA bug exports as Markdown in `data/md/` (e.g., `Bug_KAN-2.md`, `Bug_KAN-3.md`)

The system serves three primary use cases for QA engineers:
- **UC1:** Given a JIRA ticket or feature description, generate new test cases.
- **UC2:** Given a scenario, find existing test cases that are similar (deduplication and reuse).
- **UC3:** Given a manual test case, generate Selenium (Java/TestNG) or Playwright (TS) automation code in the style of the reference repos.

The stack is locked: **Groq `openai/gpt-oss-120b`** for chat completion, **Qdrant** vector DB, **`BAAI/bge-m3`** for hybrid dense+sparse embeddings, **`BAAI/bge-reranker-v2-m3`** cross-encoder reranker, **FastAPI** backend, **React + Vite + Tailwind** frontend. Five Qdrant collections (one per source) with an LLM intent router selecting which collections to query per turn.

---

## Requirement 1: Data Ingestion — Selenium Repository

**User Story:** As a QA engineer, I want the Selenium Java/TestNG repository to be auto-cloned and indexed so that I can query against the latest framework code without manual setup.

**Acceptance Criteria:**

1. WHEN the user runs `python -m backend.ingest.ingest_selenium` AND `data/selenium_repo/` is empty, THEN the system SHALL `git clone https://github.com/PramodDutta/ATB14xSeleniumAdvanceFrameworks` into `data/selenium_repo/`.
2. WHEN `data/selenium_repo/` already contains a git repository, THEN the system SHALL run `git pull` to refresh it before chunking.
3. WHEN ingesting, THEN the system SHALL parse every `.java` file using `tree-sitter-java` and emit one chunk per top-level class and per method.
4. Each chunk SHALL carry payload metadata: `repo`, `path`, `start_line`, `end_line`, `symbol`, `kind` (one of `class` | `method`), and `annotations` (TestNG annotations as a list of strings).
5. WHEN chunking completes, THEN the system SHALL upsert all chunks into the `selenium_code` Qdrant collection with both dense and sparse vectors from `bge-m3`.
6. IF a `.java` file fails to parse, THEN the system SHALL log a warning with the file path and continue ingesting the remaining files.
7. WHEN ingest finishes, THEN the system SHALL print a summary line: `selenium_code: <chunk_count> chunks from <file_count> files`.

---

## Requirement 2: Data Ingestion — Playwright Repository

**User Story:** As a QA engineer, I want the Playwright TypeScript repository to be auto-cloned and indexed so that I can query against the latest framework code.

**Acceptance Criteria:**

1. WHEN the user runs `python -m backend.ingest.ingest_playwright` AND `data/playwright_repo/` is empty, THEN the system SHALL `git clone https://github.com/PramodDutta/Advance-Playwright-Framework` into `data/playwright_repo/`.
2. WHEN `data/playwright_repo/` already contains a git repo, THEN the system SHALL run `git pull` to refresh it.
3. WHEN ingesting, THEN the system SHALL parse every `.ts`, `.tsx`, `.js`, and `.jsx` file using `tree-sitter-typescript` and emit one chunk per function, class, and `test(...)` block.
4. Each chunk SHALL carry payload metadata: `repo`, `path`, `start_line`, `end_line`, `symbol`, `kind` (one of `function` | `class` | `test`), and `test_title` (the literal title argument when `kind = test`, else null).
5. WHEN chunking completes, THEN the system SHALL upsert all chunks into the `playwright_code` Qdrant collection with both dense and sparse `bge-m3` vectors.
6. IF a file fails to parse, THEN the system SHALL log a warning and continue.
7. WHEN ingest finishes, THEN the system SHALL print: `playwright_code: <chunk_count> chunks from <file_count> files`.

---

## Requirement 3: Data Ingestion — VWO Test Cases (CSV)

**User Story:** As a QA engineer, I want every row of the VWO test case CSV indexed so that I can search by test case ID, name, steps, or expected result.

**Acceptance Criteria:**

1. WHEN the user runs `python -m backend.ingest.ingest_testcases`, THEN the system SHALL read `data/csv/VWO_TestCase.csv` and treat each row as one chunk.
2. The system SHALL build the chunk text by joining the row's fields with clear labels: `Test Case ID:`, `Test Case Name:`, `Precondition:`, `Test Steps:`, `Expected Result:`, `Priority:`.
3. Each chunk SHALL carry payload metadata: `tc_id`, `tc_name`, `priority`, `precondition`, `steps`, `expected_result`, plus optional `jira_id`, `module`, `severity`, `labels`, `sprint`, `status`, `owner`, `test_type` when those columns are present.
4. The CSV schema SHALL tolerate the current 6-column shape (`Test Case ID, Test Case Name, Precondition, Test Steps, Expected Result, Priority`) AND a future extended schema with the optional fields above; missing optional columns SHALL default to null in the payload.
5. WHEN chunking completes, THEN the system SHALL upsert into the `vwo_testcases` Qdrant collection.
6. WHEN ingest finishes, THEN the system SHALL print: `vwo_testcases: <row_count> chunks`.

---

## Requirement 4: Data Ingestion — VWO PDFs

**User Story:** As a QA engineer, I want product PDFs indexed so that I can ground answers in the official PRDs.

**Acceptance Criteria:**

1. WHEN the user runs `python -m backend.ingest.ingest_pdfs`, THEN the system SHALL extract text from every `.pdf` in `data/pdf/` using PyMuPDF.
2. IF a PDF's total extracted text is shorter than 50 characters, THEN the system SHALL skip it and record an entry in `data/_skip_report.json` with fields `path`, `reason`, `char_count`.
3. WHEN a PDF is processed, THEN the system SHALL split it into chunks of approximately 800 characters with 120-character overlap, preferring header boundaries when detected.
4. Each chunk SHALL carry payload metadata: `doc_title` (filename without extension), `page` (the source page number), `section` (nearest preceding header text, else null), and `source_path`.
5. WHEN chunking completes, THEN the system SHALL upsert into the `vwo_docs` Qdrant collection.
6. WHEN ingest finishes, THEN the system SHALL print: `vwo_docs: <chunk_count> chunks from <pdf_count> pdfs (<skipped> skipped)`.

---

## Requirement 5: Data Ingestion — JIRA Bug Markdown

**User Story:** As a QA engineer, I want JIRA bug exports indexed so that I can ask about open bugs and link new test cases to existing tickets.

**Acceptance Criteria:**

1. WHEN the user runs `python -m backend.ingest.ingest_jira`, THEN the system SHALL read every `.md` file in `data/md/` matching the JIRA export format.
2. The system SHALL parse the JIRA header block to extract metadata fields: `jira_id`, `summary`, `status`, `priority`, `type`, `reporter`, `assignee`, `labels`, `created`, `updated`, `project`, `components`.
3. The `jira_id` SHALL be derived from the leading bracketed token (e.g., `[KAN-2] ...` → `KAN-2`).
4. The system SHALL emit one chunk per file when the body is ≤1500 characters, OR split into multiple chunks of ~1000 chars with ~150 overlap when longer.
5. Each chunk SHALL carry the parsed metadata plus `source_path`.
6. WHEN chunking completes, THEN the system SHALL upsert into the `vwo_bugs` Qdrant collection.
7. WHEN ingest finishes, THEN the system SHALL print: `vwo_bugs: <chunk_count> chunks from <file_count> files`.

---

## Requirement 6: Ingestion Orchestration

**User Story:** As a QA engineer, I want a single command that re-indexes everything so that I don't have to remember five script names.

**Acceptance Criteria:**

1. WHEN the user runs `python -m backend.ingest.ingest_all`, THEN the system SHALL execute the five ingest scripts in this order: `selenium`, `playwright`, `testcases`, `pdfs`, `jira`.
2. IF any individual ingest step raises an exception, THEN the system SHALL log the failure with traceback AND continue with the remaining steps.
3. WHEN orchestration completes, THEN the system SHALL print a final summary table showing chunk counts per collection AND the overall success/failure count.
4. The orchestrator SHALL exit with status code `0` if all five succeeded, `1` if any failed.

---

## Requirement 7: Vector Store — Qdrant Configuration

**User Story:** As a QA engineer, I want a local-by-default vector store so that I can run the project without standing up extra infrastructure.

**Acceptance Criteria:**

1. The system SHALL create five Qdrant collections: `selenium_code`, `playwright_code`, `vwo_testcases`, `vwo_docs`, `vwo_bugs`.
2. Each collection SHALL be configured with named vectors: a dense vector of size 1024 (cosine) AND a sparse vector — both produced by `bge-m3`.
3. WHEN `QDRANT_PATH` is set in `.env`, THEN the system SHALL use Qdrant in file-store (embedded) mode at that path. Default: `./qdrant_data`.
4. WHEN `QDRANT_URL` is set, THEN the system SHALL use HTTP mode and ignore `QDRANT_PATH`.
5. IF a collection already exists with a matching configuration, THEN ingest SHALL upsert into it without recreating.
6. IF a collection exists with mismatched vector configuration, THEN ingest SHALL fail with a clear error message instructing the user to delete `qdrant_data/` or use a different `QDRANT_PATH`.

---

## Requirement 8: Hybrid Retrieval and Reranking

**User Story:** As a QA engineer, I want retrieval that handles both keyword lookups (e.g., `TC_LOGIN_023`) and semantic queries so that I get accurate results regardless of phrasing.

**Acceptance Criteria:**

1. For each query routed to a collection, the retriever SHALL perform hybrid search using both the dense and sparse `bge-m3` vectors.
2. The retriever SHALL fuse dense and sparse results using Reciprocal Rank Fusion (RRF) with `k=60` and return the top `TOP_K_PER_COLLECTION` candidates (default 12).
3. WHEN multiple collections are queried, THEN the per-collection candidate lists SHALL be merged into one pool.
4. The merged pool SHALL be reranked using `BAAI/bge-reranker-v2-m3` against the rewritten query.
5. The retriever SHALL return the top `RERANK_TOP_K` chunks (default 4) to the LLM as grounded context.
6. Each context chunk passed to the LLM SHALL be wrapped in a `<doc id="N" source="..." ...metadata.../>` block so the LLM can cite by `[N]`.

---

## Requirement 9: Intent Router

**User Story:** As a QA engineer, I want the system to automatically pick the right sources for my query so that I don't have to filter by hand every time.

**Acceptance Criteria:**

1. WHEN a user query is received, THEN the system SHALL invoke a Groq `openai/gpt-oss-120b` classifier with a fixed system prompt that lists the five collections and their content.
2. The router SHALL return a JSON array containing 1 or 2 collection names from the allowed set: `["selenium_code", "playwright_code", "vwo_testcases", "vwo_docs", "vwo_bugs"]`.
3. IF the router output is malformed, THEN the system SHALL fall back to querying all five collections.
4. WHEN the user has activated the `SourceFilter` UI control to force one or more collections, THEN the system SHALL bypass the router and use the user's selection.
5. The router prompt SHALL include one example per collection so the model has a stable taxonomy.

---

## Requirement 10: Multi-Turn Chat with Query Rewriting

**User Story:** As a QA engineer, I want to ask follow-up questions naturally without restating the full context every turn.

**Acceptance Criteria:**

1. The backend SHALL maintain per-session chat history in memory keyed by `session_id`.
2. WHEN a query arrives with prior history, THEN the system SHALL invoke a Groq query-rewriter that condenses the latest user turn plus the previous `HISTORY_TURNS` turns (default 4) into a single standalone query.
3. The standalone query — not the raw user message — SHALL be used for routing and retrieval.
4. The original conversation history SHALL still be passed to the answer prompt so the LLM can maintain conversational continuity.
5. WHEN no prior history exists, THEN the rewriter SHALL be skipped and the raw user query used directly.
6. Sessions SHALL expire after 30 minutes of inactivity to bound memory.

---

## Requirement 11: Use Case 1 — Generate Test Cases from JIRA

**User Story:** As a QA engineer, I want to paste or reference a JIRA ticket and receive new test cases so that I can save time on test design.

**Acceptance Criteria:**

1. WHEN the user query references a `jira_id` matching a known bug (e.g., `KAN-2`) OR pastes JIRA-style text, THEN the router SHALL select `vwo_bugs` AND `vwo_testcases` AND `vwo_docs`.
2. The answer prompt SHALL instruct the LLM to produce test cases in the same column shape as `VWO_TestCase.csv`: `Test Case ID, Test Case Name, Precondition, Test Steps, Expected Result, Priority`.
3. The LLM SHALL cite the source JIRA chunk and any reused test-case chunks via inline `[N]` markers.
4. WHEN the user requests "save these to disk" (button or keyword), THEN the backend SHALL append the generated rows to `data/csv/VWO_TestCase_generated.csv`, creating it with headers if it doesn't exist.

---

## Requirement 12: Use Case 2 — Find Similar Test Cases

**User Story:** As a QA engineer, I want to describe a scenario and see existing test cases that already cover it so that I avoid duplicates.

**Acceptance Criteria:**

1. WHEN the user query is phrased as "find similar...", "do we have a test for...", or otherwise matches a similarity-search intent, THEN the router SHALL select `vwo_testcases` only.
2. The retriever SHALL return up to 8 reranked test-case chunks for this intent (overriding the default 4).
3. The answer SHALL list each matching test case with its `tc_id`, `tc_name`, and a one-line summary, plus a `[N]` citation.
4. The response SHALL include a "no close match found" disclaimer when the top reranker score falls below a configurable threshold (`MIN_RERANK_SCORE`, default 0.3).

---

## Requirement 13: Use Case 3 — Generate Automation Code from a Manual Test Case

**User Story:** As a QA engineer, I want to point at a manual test case and get Selenium or Playwright code in the style of our existing frameworks so that I can automate faster.

**Acceptance Criteria:**

1. The user SHALL be able to specify the target framework — `selenium` or `playwright` — either via a UI toggle OR by including the keyword in the query.
2. WHEN the framework is `selenium`, THEN the router SHALL select `vwo_testcases` AND `selenium_code`.
3. WHEN the framework is `playwright`, THEN the router SHALL select `vwo_testcases` AND `playwright_code`.
4. The answer prompt SHALL instruct the LLM to match the conventions present in the retrieved `*_code` chunks (page object names, base classes, helper methods, fixture patterns).
5. The LLM SHALL output a complete, runnable file — including imports, class declaration, and TestNG/Playwright annotations — inside a fenced code block tagged `java` or `typescript`.
6. WHEN the user requests "save to disk", THEN the backend SHALL write the file to `data/generated/<framework>/<TestCaseId>.<java|ts>`, creating directories as needed AND refusing to overwrite an existing file unless the user explicitly confirms.

---

## Requirement 14: Output Modes — Read-Only and Write-to-Disk

**User Story:** As a QA engineer, I want to choose per query whether the copilot just answers or also writes files so that I stay in control of my repo.

**Acceptance Criteria:**

1. The default output mode SHALL be read-only: the response is shown in the chat with citations, and no files are written.
2. The frontend SHALL display a "Save to disk" button on responses that contain generated test cases (UC1) or generated code (UC3).
3. WHEN the user clicks "Save to disk", THEN the frontend SHALL call a dedicated `POST /api/save` endpoint with the message id and a target path hint.
4. The save endpoint SHALL refuse to write outside the chapter directory (path traversal guard) AND refuse to overwrite existing files unless `overwrite=true` is explicitly passed.
5. After a successful save, the chat SHALL display a confirmation with the absolute path of the written file.

---

## Requirement 15: Citations and Source Panel

**User Story:** As a QA engineer, I want every claim in an answer linked to a source so that I can verify it before trusting the output.

**Acceptance Criteria:**

1. The answer SHALL contain inline `[N]` markers that map 1-to-1 to the context chunks passed to the LLM.
2. The frontend SHALL render `[N]` markers as clickable chips.
3. The frontend SHALL display a `SourcePanel` listing each cited chunk with source-type-specific rendering:
   - `selenium_code` / `playwright_code`: `repo · path:start_line-end_line · symbol`
   - `vwo_testcases`: `tc_id · tc_name · priority`
   - `vwo_docs`: `doc_title · page N · section`
   - `vwo_bugs`: `jira_id · status · priority · summary`
4. WHEN a citation chip is clicked, THEN the corresponding `SourcePanel` card SHALL scroll into view AND highlight briefly.
5. Each source card SHALL be expandable to reveal the full chunk text.

---

## Requirement 16: API Surface

**User Story:** As a developer, I want a stable HTTP API so that the frontend (or future clients) can integrate predictably.

**Acceptance Criteria:**

1. The backend SHALL expose `POST /api/chat` accepting JSON `{ session_id, message, force_collections?: string[], framework?: "selenium"|"playwright" }` and returning a Server-Sent Events stream.
2. The SSE stream SHALL emit events of three kinds: `event: token` (incremental tokens), `event: sources` (one-shot, the citation array), and `event: done` (terminator).
3. The backend SHALL expose `GET /api/health` returning `{ status: "ok", collections: { <name>: <chunk_count> } }`.
4. The backend SHALL expose `POST /api/ingest/<source>` for `<source>` in `{selenium, playwright, testcases, pdfs, jira, all}` returning the ingest summary.
5. The backend SHALL expose `POST /api/save` accepting `{ message_id, target_path?, overwrite?: bool }` and returning `{ written_path }`.
6. CORS SHALL allow the Vite dev origin (default `http://localhost:5173`).

---

## Requirement 17: Frontend — Three-Pane Layout

**User Story:** As a QA engineer, I want a focused chat UI with sources visible alongside answers so that I can read and verify in one view.

**Acceptance Criteria:**

1. The frontend SHALL be a single-page React + Vite + TypeScript + Tailwind app.
2. The layout SHALL have three panes: left sidebar (`SourceFilter` + `IngestStatus`), center chat (`ChatPane`), right source panel (`SourcePanel`).
3. The `ChatPane` SHALL stream tokens via `EventSource` consuming the SSE response from `POST /api/chat` and render Markdown including fenced code blocks with syntax highlighting for `java` and `typescript`.
4. The `SourceFilter` SHALL expose a checkbox per collection; checked collections override the router on subsequent queries.
5. The `IngestStatus` SHALL poll `/api/health` on mount and after manual ingest triggers, displaying chunk counts per collection.
6. Vite SHALL be configured to proxy `/api` to `http://localhost:8000`.

---

## Requirement 18: Configuration via Environment

**User Story:** As a QA engineer, I want to configure the app via a single `.env` file so that I can switch models or paths without code changes.

**Acceptance Criteria:**

1. The repo SHALL include an `.env.example` file at `chapter_09_Project_QACopilot/.env.example` listing every required and optional variable with safe defaults.
2. The required variables SHALL be: `GROQ_API_KEY`.
3. The optional variables with defaults SHALL include: `GROQ_MODEL` (default `openai/gpt-oss-120b`), `QDRANT_PATH` (default `./qdrant_data`), `EMBED_MODEL` (default `BAAI/bge-m3`), `RERANK_MODEL` (default `BAAI/bge-reranker-v2-m3`), `EMBED_DEVICE` (default `cpu`), `SELENIUM_REPO_DIR`, `PLAYWRIGHT_REPO_DIR`, `TESTCASES_CSV`, `PDFS_DIR`, `JIRA_MD_DIR`, `TOP_K_PER_COLLECTION` (12), `RERANK_TOP_K` (4), `CHUNK_SIZE` (1000), `CHUNK_OVERLAP` (150), `HISTORY_TURNS` (4), `MIN_RERANK_SCORE` (0.3).
4. Settings SHALL be loaded once at startup via `backend/lib/settings.py` and injected into modules that need them.
5. WHEN `GROQ_API_KEY` is missing at startup, THEN the backend SHALL fail fast with a clear error.

---

## Requirement 19: Documentation

**User Story:** As a future reader of this chapter, I want a README that walks me through running the project from zero so that I can learn the patterns.

**Acceptance Criteria:**

1. `chapter_09_Project_QACopilot/README.md` SHALL contain: project intro, architecture diagram (Mermaid), prerequisites, install steps, ingest commands, run commands for backend and frontend, five smoke questions (one per collection), and a "how to add a sixth source" section.
2. `chapter_09_Project_QACopilot/CLAUDE.md` SHALL document run commands, the 5-collection architecture, where router decisions live, how to add a sixth source, key payload schemas per collection, the SSE event protocol, and known pitfalls (Qdrant file-store single-process limit, `bge-m3` first-load size, tree-sitter wheel requirements).
3. The repo's root `README.md` SHALL be updated to include a Chapter 9 entry pointing to the new directory.

---

## Requirement 20: Non-Functional — Performance, Robustness, Security

**User Story:** As a QA engineer, I want the system to feel responsive and behave predictably under common failure modes.

**Acceptance Criteria:**

1. End-to-end first-token latency for a 1-collection query on warm caches SHALL be under 3 seconds on a typical developer laptop.
2. Re-running `ingest_all` on unchanged data SHALL be idempotent — chunk counts SHALL remain stable.
3. WHEN Groq returns a rate-limit error, THEN the backend SHALL retry with exponential backoff up to 3 times before surfacing the error to the user.
4. The `POST /api/save` endpoint SHALL reject paths containing `..`, absolute paths outside the chapter directory, and any path resolving outside `data/generated/` or `data/csv/`.
5. Secrets SHALL be loaded only from the environment; `.env` SHALL be listed in `.gitignore`.
6. `qdrant_data/`, `node_modules/`, `.venv/`, `data/selenium_repo/`, `data/playwright_repo/`, and `data/_skip_report.json` SHALL be listed in `.gitignore`.

---

## Open Assumptions (flag if any are wrong)

- The CSV currently has 50 rows with the basic 6-column schema; ingest is designed to scale to several thousand and to handle the extended schema if added later.
- `data/md/` only contains JIRA bug exports of the form `Bug_<KEY>.md`. If other markdown doc types appear, a parser branch will be added.
- The Playwright repo is TypeScript; if it turns out to be JavaScript-only, the same `tree-sitter-typescript` grammar parses it (TS is a superset).
- Local-only is the default (Qdrant file-store, embeddings on CPU). Hosted Qdrant + GPU is a documented switch via `QDRANT_URL` / `EMBED_DEVICE`, not the default.
- The Markdown JIRA exports are the source of truth for now; a future Jira REST API connector is out of scope for this requirements pass.
