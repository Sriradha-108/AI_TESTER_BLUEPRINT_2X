"""Ingest JIRA bug markdown exports into Qdrant vwo_bugs collection."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.ingest import batched, build_point, stable_id
from backend.lib.chunking_text import chunk_jira_body, parse_jira_markdown
from backend.lib.embeddings import get_encoder
from backend.lib.qdrant_store import get_store

COLLECTION = "vwo_bugs"


def main():
    from backend.lib.settings import settings

    store = get_store()
    store.ensure_collection(COLLECTION)

    md_dir = settings.JIRA_MD_DIR
    if not md_dir.exists():
        print(f"{COLLECTION}: 0 chunks (MD dir not found at {md_dir})")
        return

    md_files = list(md_dir.glob("*.md"))
    if not md_files:
        print(f"{COLLECTION}: 0 chunks (no .md files found)")
        return

    all_chunks = []
    file_count = 0

    for md_path in md_files:
        try:
            metadata, body = parse_jira_markdown(md_path)
            chunks = chunk_jira_body(
                metadata,
                body,
                chunk_size=settings.CHUNK_SIZE,
                overlap=settings.CHUNK_OVERLAP,
            )
            if chunks:
                file_count += 1
                all_chunks.extend(chunks)
        except Exception as e:
            print(f"Warning: Failed to parse {md_path}: {e}")
            continue

    if not all_chunks:
        print(f"{COLLECTION}: 0 chunks from {len(md_files)} files")
        return

    # Embed and upsert
    encoder = get_encoder()
    points = []
    for batch in batched(all_chunks, 32):
        texts = [c.text for c in batch]
        embeddings = encoder.encode(texts)
        for c, emb in zip(batch, embeddings):
            pid = stable_id(
                "jira",
                c.payload.get("jira_id", ""),
                str(c.payload.get("chunk_index", 0)),
            )
            points.append(build_point(pid, emb["dense"], emb["sparse"], c.payload))

    store.upsert(COLLECTION, points)
    print(f"{COLLECTION}: {len(points)} chunks from {file_count} files")


if __name__ == "__main__":
    main()
