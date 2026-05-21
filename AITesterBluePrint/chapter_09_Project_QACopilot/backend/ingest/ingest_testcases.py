"""Ingest VWO test cases CSV into Qdrant vwo_testcases collection."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from backend.ingest import batched, build_point, stable_id
from backend.lib.chunking_text import chunk_testcase_row
from backend.lib.embeddings import get_encoder
from backend.lib.qdrant_store import get_store

COLLECTION = "vwo_testcases"


def main():
    from backend.lib.settings import settings

    store = get_store()
    store.ensure_collection(COLLECTION)

    csv_path = settings.TESTCASES_CSV
    if not csv_path.exists():
        print(f"{COLLECTION}: 0 chunks (CSV not found at {csv_path})")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        print(f"{COLLECTION}: 0 chunks (CSV is empty)")
        return

    # Build chunks — one per row
    all_chunks = []
    for _, row in df.iterrows():
        chunk = chunk_testcase_row(row.to_dict())
        chunk.payload["source_path"] = str(csv_path)
        all_chunks.append(chunk)

    # Embed and upsert
    encoder = get_encoder()
    points = []
    for batch in batched(all_chunks, 32):
        texts = [c.text for c in batch]
        embeddings = encoder.encode(texts)
        for c, emb in zip(batch, embeddings):
            pid = stable_id("tc", c.payload.get("tc_id", ""))
            points.append(build_point(pid, emb["dense"], emb["sparse"], c.payload))

    store.upsert(COLLECTION, points)
    print(f"{COLLECTION}: {len(points)} chunks")


if __name__ == "__main__":
    main()
