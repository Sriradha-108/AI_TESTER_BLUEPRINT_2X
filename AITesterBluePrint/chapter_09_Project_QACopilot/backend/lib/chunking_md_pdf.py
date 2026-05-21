"""PDF text extraction and chunking using PyMuPDF."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.lib.chunking_text import ChunkRecord


def extract_pdf_text(path: Path) -> list[tuple[int, str]]:
    """Extract text from each page of a PDF using PyMuPDF.

    Returns list of (page_number, page_text) tuples. Page numbers are 1-indexed.
    """
    import fitz  # PyMuPDF

    doc = fitz.open(str(path))
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append((i + 1, text))
    doc.close()
    return pages


def is_pdf_too_short(pages: list[tuple[int, str]], min_chars: int = 50) -> bool:
    """Check if total extracted text is below threshold."""
    total = sum(len(text) for _, text in pages)
    return total < min_chars


def split_pdf_text(
    pages: list[tuple[int, str]],
    chunk_size: int = 800,
    overlap: int = 120,
    doc_title: str = "",
    source_path: str = "",
) -> list[ChunkRecord]:
    """Split PDF page texts into chunks, preserving page number and nearest header.

    Uses header-aware separators to prefer splitting at section boundaries.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n# ", "\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[ChunkRecord] = []
    chunk_index = 0

    for page_num, page_text in pages:
        if not page_text.strip():
            continue

        splits = splitter.split_text(page_text)

        current_section = None
        for split in splits:
            # Try to detect section header in this chunk
            lines = split.split("\n")
            for line in lines:
                stripped = line.strip()
                if stripped and (
                    stripped.startswith("#")
                    or (len(stripped) < 80 and stripped.isupper())
                    or (len(stripped) < 80 and stripped.endswith(":"))
                ):
                    current_section = stripped.lstrip("#").strip()
                    break

            payload: dict[str, Any] = {
                "source_type": "vwo_docs",
                "source_path": source_path,
                "doc_title": doc_title,
                "page": page_num,
                "section": current_section,
                "chunk_index": chunk_index,
                "text": split,
            }
            chunks.append(ChunkRecord(text=split, payload=payload))
            chunk_index += 1

    return chunks
