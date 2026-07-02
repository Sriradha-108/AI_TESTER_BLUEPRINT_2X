#!/usr/bin/env python3
"""Ask-the-Repo: a tiny local RAG tool.

Indexes a code repository into a local Chroma vector store using Ollama
embeddings, then answers questions about it with a local Ollama chat model.
Everything runs on your own machine -- no data leaves it.

Usage:
    python repo_qa.py index --repo ./Advance-Playwright-Framework --model ministral
    python repo_qa.py ask   --model ministral -q "How do I run the tests?"
    python repo_qa.py ask   --model ministral            # interactive chat

See Fine_tune_instruction.md for the full setup walkthrough.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import ollama
except ImportError:
    sys.exit("Missing dependency 'ollama'. Run: pip install ollama chromadb")

try:
    import chromadb
except ImportError:
    sys.exit("Missing dependency 'chromadb'. Run: pip install ollama chromadb")


# --- Configuration -----------------------------------------------------------

# Where the vector index lives. Kept next to this script so `ask` finds it
# no matter which directory you run the command from.
SCRIPT_DIR = Path(__file__).resolve().parent
DB_DIR = SCRIPT_DIR / ".repo_qa_db"
COLLECTION_NAME = "repo"

# Small helper model that turns text into vectors (see Step 2 of the guide).
EMBED_MODEL = "nomic-embed-text"

# File types worth indexing. Everything else (binaries, images, lockfiles) is
# skipped so the index stays small and relevant.
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".rs", ".c",
    ".cpp", ".h", ".hpp", ".cs", ".php", ".swift", ".kt", ".scala", ".sh",
    ".ps1", ".sql", ".html", ".css", ".scss", ".vue", ".md", ".txt", ".rst",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".xml",
    ".gradle", ".properties", ".feature", ".dockerfile",
}

# Directories we never want to walk into.
SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__",
    "dist", "build", ".next", ".cache", "target", ".idea", ".vscode",
    "playwright-report", "test-results", ".repo_qa_db",
}

# Chunking: split each file into overlapping windows so retrieval is granular.
CHUNK_CHARS = 1500
CHUNK_OVERLAP = 200


# --- Indexing ----------------------------------------------------------------

def iter_source_files(repo: Path):
    """Yield indexable text files under `repo`."""
    for root, dirs, files in os.walk(repo):
        # Prune skipped directories in place so os.walk doesn't descend.
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = Path(root) / name
            ext = path.suffix.lower()
            if ext in TEXT_EXTENSIONS or name.lower() in {"dockerfile", "makefile"}:
                yield path


def read_text(path: Path) -> str | None:
    """Read a file as UTF-8 text, returning None if it looks binary."""
    try:
        data = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    if "\x00" in data:  # crude binary guard
        return None
    return data


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping character windows."""
    if len(text) <= CHUNK_CHARS:
        return [text]
    chunks = []
    start = 0
    step = CHUNK_CHARS - CHUNK_OVERLAP
    while start < len(text):
        chunks.append(text[start:start + CHUNK_CHARS])
        start += step
    return chunks


def embed(text: str) -> list[float]:
    """Get an embedding vector for a piece of text via Ollama."""
    resp = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return resp["embedding"]


def cmd_index(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        sys.exit(f"Repo folder not found: {repo}\n"
                 "Check the --repo path (see Step 3 of the guide).")

    client = chromadb.PersistentClient(path=str(DB_DIR))
    # Start clean so re-indexing never mixes stale chunks in.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    print(f"Indexing {repo} ...")
    total_chunks = 0
    file_count = 0
    for path in iter_source_files(repo):
        text = read_text(path)
        if not text or not text.strip():
            continue
        rel = path.relative_to(repo).as_posix()
        file_count += 1
        for i, chunk in enumerate(chunk_text(text)):
            try:
                vector = embed(chunk)
            except Exception as exc:
                sys.exit(f"\nCould not reach the embedding model '{EMBED_MODEL}'.\n"
                         f"Is Ollama running and did you `ollama pull {EMBED_MODEL}`?\n"
                         f"Details: {exc}")
            collection.add(
                ids=[f"{rel}::{i}"],
                embeddings=[vector],
                documents=[chunk],
                metadatas=[{"file": rel}],
            )
            total_chunks += 1
        print(f"  indexed {rel} ({file_count} files)", end="\r")

    print(f"\nIndexed {file_count} files into {total_chunks} chunks.")
    print("Done.")


# --- Asking ------------------------------------------------------------------

def get_collection():
    if not DB_DIR.exists():
        sys.exit("No index found. Run the index command first (Step 5 of the guide):\n"
                 "  python repo_qa.py index --repo ./<repo-folder> --model <model>")
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception:
        sys.exit("No index found. Run the index command first (Step 5 of the guide).")


def answer(collection, model: str, question: str, k: int) -> None:
    try:
        q_vec = embed(question)
    except Exception as exc:
        sys.exit(f"Could not reach the embedding model '{EMBED_MODEL}'.\n"
                 f"Is Ollama running? Details: {exc}")

    results = collection.query(query_embeddings=[q_vec], n_results=k)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        print("The index is empty. Re-run the index command.")
        return

    context_blocks = []
    files = []
    for doc, meta in zip(documents, metadatas):
        fname = meta.get("file", "unknown")
        files.append(fname)
        context_blocks.append(f"--- {fname} ---\n{doc}")
    context = "\n\n".join(context_blocks)

    prompt = (
        "You are a helpful assistant answering questions about a code "
        "repository. Use ONLY the code excerpts below to answer. If the "
        "answer isn't in them, say so honestly.\n\n"
        f"Code excerpts:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )

    try:
        resp = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        sys.exit(f"Could not reach the model '{model}'.\n"
                 f"Run `ollama list` to see your exact model name (see the "
                 f"troubleshooting table).\nDetails: {exc}")

    print("\n" + resp["message"]["content"].strip() + "\n")
    unique_files = sorted(set(files))
    print("Files I looked at:")
    for f in unique_files:
        print(f"  - {f}")
    print()


def cmd_ask(args: argparse.Namespace) -> None:
    collection = get_collection()
    if args.question:
        answer(collection, args.model, args.question, args.k)
        return

    print("Ask questions about the repo. Type 'exit' when you're finished.\n")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        answer(collection, args.model, question, args.k)


# --- CLI ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask questions about a code repository using a local Ollama model."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="Build the search index (do this once).")
    p_index.add_argument("--repo", required=True, help="Path to the repo folder.")
    p_index.add_argument("--model", default="ministral", help="Chat model name (unused for indexing, kept for parity).")
    p_index.set_defaults(func=cmd_index)

    p_ask = sub.add_parser("ask", help="Ask a question (or start a chat).")
    p_ask.add_argument("--model", default="ministral", help="Ollama chat model name.")
    p_ask.add_argument("-q", "--question", help="A single question to ask. Omit for interactive mode.")
    p_ask.add_argument("-k", type=int, default=5, help="How many code chunks to retrieve (default 5).")
    p_ask.set_defaults(func=cmd_ask)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
