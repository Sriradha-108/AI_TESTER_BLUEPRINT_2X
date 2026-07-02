# Chapter 16 — Ask-the-Repo (Local RAG over a Code Repo)

A tiny, fully local tool that answers questions about a code repository. It
indexes the repo into a Chroma vector store using **Ollama** embeddings, then
answers questions with a local Ollama chat model. Nothing leaves your machine.

## Contents

| File | Purpose |
|------|---------|
| `repo_qa.py` | The CLI tool (`index` + `ask` commands). |
| `Fine_tune_instruction.md` | Step-by-step student setup guide. |
| `SETUP_GUIDE_FINE_TUNE_QWEN2.5.md.pdf` | Fine-tuning setup reference (PDF). |
| `SKILL.md` | Tiered model orchestration skill notes. |

## Quick start

1. **Install Ollama** — https://ollama.com/download
2. **Pull the models:**
   ```
   ollama pull ministral          # chat model (swap name if the pull fails)
   ollama pull nomic-embed-text   # embedding model
   ```
3. **Install Python deps:**
   ```
   pip install ollama chromadb
   ```
4. **Get a repo to ask about:**
   ```
   git clone https://github.com/PramodDutta/Advance-Playwright-Framework
   ```
5. **Build the index (once):**
   ```
   python repo_qa.py index --repo ./Advance-Playwright-Framework --model ministral
   ```
6. **Ask questions:**
   ```
   python repo_qa.py ask --model ministral -q "How do I run the tests?"
   python repo_qa.py ask --model ministral            # interactive chat
   ```
   Add `-k 10` to retrieve more code chunks per question.

See `Fine_tune_instruction.md` for the full walkthrough and troubleshooting.

## How it works

- **Index:** walks the repo, skips binaries / `node_modules` / `venv` / `.git`,
  splits each text file into overlapping ~1500-char chunks, embeds them with
  `nomic-embed-text`, and stores them in a local Chroma DB (`.repo_qa_db/`).
- **Ask:** embeds your question, retrieves the top-`k` matching chunks, feeds
  them as context to the chat model, and prints the answer plus the list of
  files it looked at.

## Notes

- `ministral` may not be a valid Ollama tag on your install. If `ollama pull`
  fails, run `ollama list` / check the Ollama library and use a valid name
  (e.g. `mistral`), passing it via `--model`.
- The model is small and can be wrong — always double-check important answers
  against the real code.
