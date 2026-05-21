"""Ingest VWO PDF documents into Qdrant vwo_docs collection."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.ingest import batched, build_point, stable_id
from backend.lib.chunking_md_pdf import extract_pdf_text, is_pdf_too_short, split_pdf_text
from backend.lib.embeddings import get_encoder
from backend.lib.qdrant_store import get_store

COLLECTION = "vwo_docs"


def main():
    from backend.lib.settings import settings

    store = get_store()
    store.ensure_collection(COLLECTION)

    pdf_dir = settings.PDFS_DIR
    if not pdf_dir.exists():
        print(f"{COLLECTION}: 0 chunks (PDF dir not found at {pdf_dir})")
        return

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"{COLLECTION}: 0 chunks (no PDFs found)")
        return

    skip_report: list[dict] = []
    all_chunks = []
    pdf_count = 0

    for pdf_path in pdf_files:
        pages = extract_pdf_text(pdf_path)

        if is_pdf_too_short(pages):
            total_chars = sum(len(t) for _, t in pages)
            skip_report.append({
                "path": str(pdf_path),
                "reason": "too_short",
                "char_count": total_chars,
            })
            continue

        doc_title = pdf_path.stem
        chunks = split_pdf_text(
            pages,
            chunk_size=settings.PDF_CHUNK_SIZE,
            overlap=settings.PDF_CHUNK_OVERLAP,
            doc_title=doc_title,
            source_path=str(pdf_path),
        )
        if chunks:
            pdf_count += 1
            all_chunks.extend(chunks)

    # Write skip report
    skip_path = pdf_dir.parent / "_skip_report.json"
    skip_path.write_text(json.dumps(skip_report, indent=2), encoding="utf-8")

    if not all_chunks:
        print(f"{COLLECTION}: 0 chunks from {len(pdf_files)} pdfs ({len(skip_report)} skipped)")
        return

    # Embed and upsert
    encoder = get_encoder()
    points = []
    for batch in batched(all_chunks, 32):
        texts = [c.text for c in batch]
        embeddings = encoder.encode(texts)
        for c, emb in zip(batch, embeddings):
            pid = stable_id(
                "pdf",
                c.payload.get("source_path", ""),
                str(c.payload.get("page", 0)),
                str(c.payload.get("chunk_index", 0)),
            )
            points.append(build_point(pid, emb["dense"], emb["sparse"], c.payload))

    store.upsert(COLLECTION, points)
    print(f"{COLLECTION}: {len(points)} chunks from {pdf_count} pdfs ({len(skip_report)} skipped)")


if __name__ == "__main__":
    main()
