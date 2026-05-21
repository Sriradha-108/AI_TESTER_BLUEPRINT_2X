"""AST-aware code chunking using tree-sitter for Java and TypeScript."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from backend.lib.chunking_text import ChunkRecord

logger = logging.getLogger(__name__)


def _get_parser(language: str):
    """Get a tree-sitter parser for the given language."""
    from tree_sitter_languages import get_language, get_parser

    parser = get_parser(language)
    return parser


def chunk_java_file(path: Path) -> list[ChunkRecord]:
    """Parse a Java file and emit one chunk per class and per method.

    Returns empty list on parse failure (logged as warning).
    """
    try:
        source = path.read_bytes()
        parser = _get_parser("java")
        tree = parser.parse(source)
    except Exception as e:
        logger.warning(f"Failed to parse {path}: {e}")
        return []

    source_text = source.decode("utf-8", errors="replace")
    lines = source_text.split("\n")
    chunks: list[ChunkRecord] = []

    root = tree.root_node

    # Find class declarations
    for node in _walk_type(root, "class_declaration"):
        class_name = _get_child_text(node, "name", source)
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        text = _node_text(node, source)

        # Collect annotations on the class
        annotations = _collect_annotations(node, source)

        chunks.append(ChunkRecord(
            text=text,
            payload={
                "source_type": "selenium_code",
                "source_path": str(path),
                "repo": "selenium_repo",
                "start_line": start_line,
                "end_line": end_line,
                "symbol": class_name,
                "kind": "class",
                "annotations": annotations,
                "text": text,
                "chunk_index": len(chunks),
            },
        ))

        # Find methods within this class
        for method_node in _walk_type(node, "method_declaration"):
            method_name = _get_child_text(method_node, "name", source)
            m_start = method_node.start_point[0] + 1
            m_end = method_node.end_point[0] + 1
            m_text = _node_text(method_node, source)
            m_annotations = _collect_annotations(method_node, source)

            chunks.append(ChunkRecord(
                text=m_text,
                payload={
                    "source_type": "selenium_code",
                    "source_path": str(path),
                    "repo": "selenium_repo",
                    "start_line": m_start,
                    "end_line": m_end,
                    "symbol": method_name,
                    "kind": "method",
                    "annotations": m_annotations,
                    "text": m_text,
                    "chunk_index": len(chunks),
                },
            ))

    # If no classes found, treat the whole file as one chunk
    if not chunks and source_text.strip():
        chunks.append(ChunkRecord(
            text=source_text,
            payload={
                "source_type": "selenium_code",
                "source_path": str(path),
                "repo": "selenium_repo",
                "start_line": 1,
                "end_line": len(lines),
                "symbol": path.stem,
                "kind": "file",
                "annotations": [],
                "text": source_text,
                "chunk_index": 0,
            },
        ))

    return chunks


def chunk_ts_file(path: Path) -> list[ChunkRecord]:
    """Parse a TypeScript/JavaScript file and emit one chunk per function, class, or test block.

    Returns empty list on parse failure.
    """
    try:
        source = path.read_bytes()
        # Use typescript parser for both .ts and .js files
        lang = "typescript" if path.suffix in (".ts", ".tsx") else "javascript"
        parser = _get_parser(lang)
        tree = parser.parse(source)
    except Exception as e:
        logger.warning(f"Failed to parse {path}: {e}")
        return []

    source_text = source.decode("utf-8", errors="replace")
    lines = source_text.split("\n")
    chunks: list[ChunkRecord] = []

    root = tree.root_node

    # Find function declarations
    for node in _walk_type(root, "function_declaration"):
        name = _get_child_text(node, "name", source)
        _add_ts_chunk(chunks, node, source, path, name, "function")

    # Find class declarations
    for node in _walk_type(root, "class_declaration"):
        name = _get_child_text(node, "name", source)
        _add_ts_chunk(chunks, node, source, path, name, "class")

    # Find arrow functions assigned to variables (const foo = () => {})
    for node in _walk_type(root, "lexical_declaration"):
        for declarator in _walk_type(node, "variable_declarator"):
            init = declarator.child_by_field_name("value")
            if init and init.type in ("arrow_function", "function"):
                name = _get_child_text(declarator, "name", source)
                _add_ts_chunk(chunks, node, source, path, name, "function")

    # Find test(...) / it(...) / describe(...) calls
    for node in _walk_type(root, "call_expression"):
        fn_node = node.child_by_field_name("function")
        if fn_node:
            fn_name = _node_text(fn_node, source)
            if fn_name in ("test", "it", "describe", "test.describe"):
                args = node.child_by_field_name("arguments")
                test_title = _extract_first_string_arg(args, source) if args else None
                # Use the parent expression_statement if available
                parent = node.parent if node.parent and node.parent.type == "expression_statement" else node
                _add_ts_chunk(chunks, parent, source, path, test_title or fn_name, "test", test_title)

    # If nothing found, treat whole file as one chunk
    if not chunks and source_text.strip():
        chunks.append(ChunkRecord(
            text=source_text,
            payload={
                "source_type": "playwright_code",
                "source_path": str(path),
                "repo": "playwright_repo",
                "start_line": 1,
                "end_line": len(lines),
                "symbol": path.stem,
                "kind": "file",
                "test_title": None,
                "text": source_text,
                "chunk_index": 0,
            },
        ))

    return chunks


# ── Helpers ──────────────────────────────────────────────────────────────────


def _add_ts_chunk(
    chunks: list[ChunkRecord],
    node,
    source: bytes,
    path: Path,
    symbol: str,
    kind: str,
    test_title: str | None = None,
):
    text = _node_text(node, source)
    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1
    chunks.append(ChunkRecord(
        text=text,
        payload={
            "source_type": "playwright_code",
            "source_path": str(path),
            "repo": "playwright_repo",
            "start_line": start_line,
            "end_line": end_line,
            "symbol": symbol,
            "kind": kind,
            "test_title": test_title,
            "text": text,
            "chunk_index": len(chunks),
        },
    ))


def _walk_type(node, type_name: str):
    """Recursively yield all descendant nodes of a given type."""
    if node.type == type_name:
        yield node
    for child in node.children:
        yield from _walk_type(child, type_name)


def _node_text(node, source: bytes) -> str:
    """Extract the text of a tree-sitter node."""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _get_child_text(node, field_name: str, source: bytes) -> str:
    """Get text of a named child field."""
    child = node.child_by_field_name(field_name)
    if child:
        return _node_text(child, source)
    return ""


def _collect_annotations(node, source: bytes) -> list[str]:
    """Collect annotation names preceding a node (Java-specific)."""
    annotations = []
    # Look at siblings before this node
    parent = node.parent
    if not parent:
        return annotations

    found_self = False
    for child in reversed(parent.children):
        if child == node:
            found_self = True
            continue
        if found_self and child.type in ("marker_annotation", "annotation"):
            ann_text = _node_text(child, source).strip()
            annotations.append(ann_text)
        elif found_self and child.type not in ("marker_annotation", "annotation", "modifiers"):
            break

    return annotations


def _extract_first_string_arg(args_node, source: bytes) -> str | None:
    """Extract the first string literal argument from an arguments node."""
    for child in args_node.children:
        if child.type in ("string", "template_string"):
            text = _node_text(child, source)
            # Strip quotes
            return text.strip("'\"`")
    return None
