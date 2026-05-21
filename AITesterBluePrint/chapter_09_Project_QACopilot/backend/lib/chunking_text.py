"""Text chunking for CSV test cases and JIRA markdown exports."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class ChunkRecord:
    """A single chunk ready for embedding and upserting."""
    text: str
    payload: dict[str, Any] = field(default_factory=dict)


# ── CSV Test Case Chunking ───────────────────────────────────────────────────


def chunk_testcase_row(row: dict) -> ChunkRecord:
    """Convert a single CSV row dict into a ChunkRecord.

    Handles both the basic 6-column schema and the extended schema.
    """
    # Build readable text from available fields
    parts = []
    field_map = {
        "Test Case ID": "Test Case ID",
        "Test Case Name": "Test Case Name",
        "Precondition": "Precondition",
        "Test Steps": "Test Steps",
        "Expected Result": "Expected Result",
        "Priority": "Priority",
    }

    for csv_col, label in field_map.items():
        val = row.get(csv_col, "")
        if val and str(val).strip() and str(val).strip().lower() != "nan":
            parts.append(f"{label}: {str(val).strip()}")

    text = "\n".join(parts)

    # Build payload metadata
    payload: dict[str, Any] = {
        "source_type": "vwo_testcases",
        "source_path": "",  # set by caller
        "tc_id": str(row.get("Test Case ID", "")).strip(),
        "tc_name": str(row.get("Test Case Name", "")).strip(),
        "priority": str(row.get("Priority", "")).strip(),
        "precondition": str(row.get("Precondition", "")).strip(),
        "steps": str(row.get("Test Steps", "")).strip(),
        "expected_result": str(row.get("Expected Result", "")).strip(),
        "text": text,
    }

    # Extended schema optional fields
    optional_fields = [
        "jira_id", "module", "severity", "labels", "sprint",
        "status", "owner", "test_type",
    ]
    for f in optional_fields:
        val = row.get(f, None)
        if val and str(val).strip() and str(val).strip().lower() != "nan":
            payload[f] = str(val).strip()
        else:
            payload[f] = None

    return ChunkRecord(text=text, payload=payload)


# ── JIRA Markdown Parsing ────────────────────────────────────────────────────


def parse_jira_markdown(path: Path) -> tuple[dict[str, Any], str]:
    """Parse a JIRA-exported markdown file.

    Returns (metadata_dict, body_text).
    Extracts jira_id from the [KEY-N] pattern in the first line.
    """
    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.split("\n")

    metadata: dict[str, Any] = {
        "source_type": "vwo_bugs",
        "source_path": str(path),
    }

    # Extract JIRA ID from first line: [KAN-2] Some title...
    first_line = lines[0] if lines else ""
    jira_match = re.match(r"\[([A-Z]+-\d+)\]\s*(.*)", first_line)
    if jira_match:
        metadata["jira_id"] = jira_match.group(1)
        metadata["summary"] = jira_match.group(2).split("Created:")[0].strip()
    else:
        # Fallback: derive from filename
        stem = path.stem  # e.g., Bug_KAN-2
        id_match = re.search(r"([A-Z]+-\d+)", stem)
        metadata["jira_id"] = id_match.group(1) if id_match else stem
        metadata["summary"] = first_line.strip()

    # Parse key-value pairs from header block
    header_patterns = {
        "status": r"Status:\s*(.+)",
        "priority": r"Priority:\s*(.+)",
        "type": r"Type:\s*(.+?)(?:\s+Priority:|\s*$)",
        "reporter": r"Reporter:\s*(.+?)(?:\s+Assignee:|\s*$)",
        "assignee": r"Assignee:\s*(.+?)(?:\s*$)",
        "project": r"Project:\s*(.+)",
        "components": r"Components:\s*(.+)",
        "labels": r"Labels:\s*(.+)",
        "created": r"Created:\s*(.+?)(?:\s+Updated:|\s*$)",
        "updated": r"Updated:\s*(.+)",
    }

    header_text = "\n".join(lines[:15])  # Header is typically in first 15 lines
    for key, pattern in header_patterns.items():
        match = re.search(pattern, header_text)
        if match:
            val = match.group(1).strip()
            if val and val.lower() != "none":
                metadata[key] = val

    # Body is everything after "Description" line
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip().lower() == "description":
            body_start = i + 1
            break

    if body_start == 0:
        # No explicit Description header — use everything after line 15
        body_start = min(15, len(lines))

    body = "\n".join(lines[body_start:]).strip()

    # Remove trailing "Generated at..." boilerplate
    gen_match = re.search(r"Generated at .+$", body, re.MULTILINE)
    if gen_match:
        body = body[: gen_match.start()].strip()

    return metadata, body


def chunk_jira_body(
    metadata: dict[str, Any],
    body: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[ChunkRecord]:
    """Chunk a JIRA body. One chunk if ≤1500 chars, else split."""
    if not body.strip():
        # Even if body is empty, create one chunk with the summary
        text = f"JIRA {metadata.get('jira_id', 'UNKNOWN')}: {metadata.get('summary', '')}"
        return [ChunkRecord(text=text, payload={**metadata, "text": text, "chunk_index": 0})]

    if len(body) <= 1500:
        text = f"JIRA {metadata.get('jira_id', '')}: {metadata.get('summary', '')}\n\n{body}"
        return [ChunkRecord(text=text, payload={**metadata, "text": text, "chunk_index": 0})]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    splits = splitter.split_text(body)
    chunks = []
    for i, split in enumerate(splits):
        text = f"JIRA {metadata.get('jira_id', '')}: {metadata.get('summary', '')}\n\n{split}"
        chunks.append(ChunkRecord(text=text, payload={**metadata, "text": text, "chunk_index": i}))
    return chunks
