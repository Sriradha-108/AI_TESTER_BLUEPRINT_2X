"""Qdrant vector store manager — 5 collections, hybrid dense+sparse search."""

from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    NamedSparseVector,
    NamedVector,
    PointStruct,
    ScoredPoint,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
    models,
)

COLLECTIONS = [
    "selenium_code",
    "playwright_code",
    "vwo_testcases",
    "vwo_docs",
    "vwo_bugs",
]

DENSE_DIM = 1024


class QdrantStore:
    """Manages five Qdrant collections with hybrid dense+sparse vectors."""

    def __init__(self, qdrant_path: str | None = None, qdrant_url: str | None = None, api_key: str | None = None):
        if qdrant_url:
            self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        else:
            self.client = QdrantClient(path=qdrant_path or "./qdrant_data")

    def ensure_collection(self, name: str) -> None:
        """Create collection if it doesn't exist. Raise on config mismatch."""
        if name not in COLLECTIONS:
            raise ValueError(f"Unknown collection: {name}. Must be one of {COLLECTIONS}")

        existing = self.client.get_collections().collections
        existing_names = [c.name for c in existing]

        if name in existing_names:
            info = self.client.get_collection(name)
            # Check dense vector size
            dense_config = info.config.params.vectors
            if isinstance(dense_config, dict):
                if "dense" in dense_config:
                    if dense_config["dense"].size != DENSE_DIM:
                        raise RuntimeError(
                            f"Collection '{name}' exists with vector size "
                            f"{dense_config['dense'].size} != {DENSE_DIM}. "
                            f"Delete qdrant_data/ and re-ingest."
                        )
            return

        # Create new collection
        self.client.create_collection(
            collection_name=name,
            vectors_config={
                "dense": VectorParams(size=DENSE_DIM, distance=Distance.COSINE),
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(index=SparseIndexParams()),
            },
        )

    def upsert(self, name: str, points: list[PointStruct], batch_size: int = 64) -> None:
        """Upsert points in batches."""
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(collection_name=name, points=batch)

    def count(self, name: str) -> int:
        """Return the number of points in a collection."""
        try:
            info = self.client.get_collection(name)
            return info.points_count or 0
        except Exception:
            return 0

    def hybrid_search(
        self,
        name: str,
        dense_vector,
        sparse_dict: dict[int, float],
        top_k: int = 12,
    ) -> list[ScoredPoint]:
        """Hybrid search using dense + sparse vectors with RRF fusion.

        Uses Qdrant's prefetch + query API for server-side fusion when available,
        falls back to client-side RRF otherwise.
        """
        dense_list = dense_vector.tolist() if hasattr(dense_vector, "tolist") else list(dense_vector)
        sparse_indices = list(sparse_dict.keys())
        sparse_values = list(sparse_dict.values())

        try:
            # Qdrant >= 1.10: use query_points with prefetch for RRF
            results = self.client.query_points(
                collection_name=name,
                prefetch=[
                    models.Prefetch(
                        query=dense_list,
                        using="dense",
                        limit=top_k * 2,
                    ),
                    models.Prefetch(
                        query=models.SparseVector(indices=sparse_indices, values=sparse_values),
                        using="sparse",
                        limit=top_k * 2,
                    ),
                ],
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=top_k,
                with_payload=True,
            )
            return results.points
        except Exception:
            # Fallback: two separate searches + client-side RRF
            return self._fallback_hybrid(name, dense_list, sparse_indices, sparse_values, top_k)

    def _fallback_hybrid(
        self, name: str, dense_list: list, sparse_indices: list, sparse_values: list, top_k: int
    ) -> list[ScoredPoint]:
        """Client-side RRF fusion from two separate searches."""
        k = 60  # RRF constant

        dense_results = self.client.search(
            collection_name=name,
            query_vector=("dense", dense_list),
            limit=top_k * 2,
            with_payload=True,
        )

        sparse_results = self.client.search(
            collection_name=name,
            query_vector=NamedSparseVector(
                name="sparse",
                vector=SparseVector(indices=sparse_indices, values=sparse_values),
            ),
            limit=top_k * 2,
            with_payload=True,
        )

        # RRF fusion
        scores: dict[str, float] = {}
        point_map: dict[str, ScoredPoint] = {}

        for rank, p in enumerate(dense_results):
            pid = str(p.id)
            scores[pid] = scores.get(pid, 0) + 1.0 / (k + rank + 1)
            point_map[pid] = p

        for rank, p in enumerate(sparse_results):
            pid = str(p.id)
            scores[pid] = scores.get(pid, 0) + 1.0 / (k + rank + 1)
            if pid not in point_map:
                point_map[pid] = p

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]
        return [point_map[pid] for pid in sorted_ids]


_store: "QdrantStore | None" = None


def get_store() -> QdrantStore:
    """Get or create the QdrantStore singleton.

    Qdrant local (file-store) mode only allows one client per process,
    so we cache the instance.
    """
    global _store
    if _store is None:
        from backend.lib.settings import settings

        _store = QdrantStore(
            qdrant_path=settings.QDRANT_PATH,
            qdrant_url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
    return _store
