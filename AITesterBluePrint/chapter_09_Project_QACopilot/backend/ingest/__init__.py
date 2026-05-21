"""Ingest utilities shared across all ingest scripts."""

import hashlib
import itertools
from typing import Any, Iterator

from qdrant_client.http.models import PointStruct, SparseVector


def stable_id(prefix: str, *parts: str) -> str:
    """Generate a stable UUID from prefix + parts via MD5.

    Returns a UUID-format string (8-4-4-4-12 hex with hyphens) since
    Qdrant local mode requires valid UUIDs as point IDs.
    """
    raw = ":".join([prefix] + [str(p) for p in parts])
    h = hashlib.md5(raw.encode()).hexdigest()
    # Format as UUID: 8-4-4-4-12
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def batched(iterable, n: int) -> Iterator[list]:
    """Yield successive n-sized chunks from iterable."""
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            break
        yield batch


def build_point(point_id: str, dense, sparse_dict: dict, payload: dict) -> PointStruct:
    """Build a Qdrant PointStruct with named dense + sparse vectors."""
    sparse_indices = list(sparse_dict.keys())
    sparse_values = list(sparse_dict.values())
    return PointStruct(
        id=point_id,
        vector={
            "dense": dense.tolist() if hasattr(dense, "tolist") else list(dense),
            "sparse": SparseVector(indices=sparse_indices, values=sparse_values),
        },
        payload=payload,
    )
