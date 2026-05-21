"""Ingest Playwright TypeScript repository into Qdrant playwright_code collection."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.ingest import batched, build_point, stable_id
from backend.ingest._git_utils import ensure_repo
from backend.lib.chunking_code import chunk_ts_file
from backend.lib.embeddings import get_encoder
from backend.lib.qdrant_store import get_store

COLLECTION = "playwright_code"
EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}


def main():
    from backend.lib.settings import settings

    store = get_store()
    store.ensure_collection(COLLECTION)

    # Clone or pull
    ensure_repo(settings.PLAYWRIGHT_REPO_DIR, settings.PLAYWRIGHT_REPO_URL)

    # Find all TS/JS files (skip node_modules)
    all_files = [
        f for f in settings.PLAYWRIGHT_REPO_DIR.rglob("*")
        if f.suffix in EXTENSIONS and "node_modules" not in str(f)
    ]

    if not all_files:
        print(f"{COLLECTION}: 0 chunks (no TS/JS files found)")
        return

    # Chunk all files
    all_chunks = []
    file_count = 0
    for tf in all_files:
        chunks = chunk_ts_file(tf)
        if chunks:
            file_count += 1
            for c in chunks:
                rel = str(tf.relative_to(settings.PLAYWRIGHT_REPO_DIR)).replace("\\", "/")
                c.payload["source_path"] = rel
            all_chunks.extend(chunks)

    if not all_chunks:
        print(f"{COLLECTION}: 0 chunks from {len(all_files)} files (all failed to parse)")
        return

    # Embed and upsert
    encoder = get_encoder()
    points = []
    for batch in batched(all_chunks, 32):
        texts = [c.text for c in batch]
        embeddings = encoder.encode(texts)
        for c, emb in zip(batch, embeddings):
            pid = stable_id(
                "playwright",
                c.payload.get("source_path", ""),
                c.payload.get("symbol", ""),
                str(c.payload.get("start_line", 0)),
            )
            points.append(build_point(pid, emb["dense"], emb["sparse"], c.payload))

    store.upsert(COLLECTION, points)
    print(f"{COLLECTION}: {len(points)} chunks from {file_count} files")


if __name__ == "__main__":
    main()
