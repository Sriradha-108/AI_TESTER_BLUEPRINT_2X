"""Ingest Selenium Java/TestNG repository into Qdrant selenium_code collection."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running as module: python -m backend.ingest.ingest_selenium
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.ingest import batched, build_point, stable_id
from backend.ingest._git_utils import ensure_repo
from backend.lib.chunking_code import chunk_java_file
from backend.lib.embeddings import get_encoder
from backend.lib.qdrant_store import get_store

COLLECTION = "selenium_code"


def main():
    from backend.lib.settings import settings

    store = get_store()
    store.ensure_collection(COLLECTION)

    # Clone or pull
    ensure_repo(settings.SELENIUM_REPO_DIR, settings.SELENIUM_REPO_URL)

    # Find all .java files
    java_files = list(settings.SELENIUM_REPO_DIR.rglob("*.java"))
    if not java_files:
        print(f"{COLLECTION}: 0 chunks (no .java files found)")
        return

    # Chunk all files
    all_chunks = []
    file_count = 0
    for jf in java_files:
        chunks = chunk_java_file(jf)
        if chunks:
            file_count += 1
            # Make paths relative to repo dir
            for c in chunks:
                rel = str(jf.relative_to(settings.SELENIUM_REPO_DIR)).replace("\\", "/")
                c.payload["source_path"] = rel
            all_chunks.extend(chunks)

    if not all_chunks:
        print(f"{COLLECTION}: 0 chunks from {len(java_files)} files (all failed to parse)")
        return

    # Embed and upsert
    encoder = get_encoder()
    points = []
    for batch in batched(all_chunks, 32):
        texts = [c.text for c in batch]
        embeddings = encoder.encode(texts)
        for c, emb in zip(batch, embeddings):
            pid = stable_id(
                "selenium",
                c.payload.get("source_path", ""),
                c.payload.get("symbol", ""),
                str(c.payload.get("start_line", 0)),
            )
            points.append(build_point(pid, emb["dense"], emb["sparse"], c.payload))

    store.upsert(COLLECTION, points)
    print(f"{COLLECTION}: {len(points)} chunks from {file_count} files")


if __name__ == "__main__":
    main()
