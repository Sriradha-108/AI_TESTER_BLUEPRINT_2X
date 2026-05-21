"""Retriever — hybrid search across collections, merge, rerank, return top-k."""

from __future__ import annotations

import itertools
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from backend.lib.embeddings import BGE_M3_Encoder
from backend.lib.qdrant_store import QdrantStore
from backend.lib.reranker import Reranker


@dataclass
class ScoredChunk:
    """A chunk with its reranker score and payload."""
    payload: dict[str, Any]
    score: float

    def to_citation(self) -> dict[str, Any]:
        """Convert to a citation dict for the frontend."""
        p = self.payload
        citation: dict[str, Any] = {
            "source_type": p.get("source_type", "unknown"),
            "source_path": p.get("source_path", ""),
            "score": round(self.score, 4),
        }

        source_type = p.get("source_type", "")
        if source_type in ("selenium_code", "playwright_code"):
            citation["repo"] = p.get("repo", "")
            citation["symbol"] = p.get("symbol", "")
            citation["kind"] = p.get("kind", "")
            citation["start_line"] = p.get("start_line")
            citation["end_line"] = p.get("end_line")
            citation["test_title"] = p.get("test_title")
        elif source_type == "vwo_testcases":
            citation["tc_id"] = p.get("tc_id", "")
            citation["tc_name"] = p.get("tc_name", "")
            citation["priority"] = p.get("priority", "")
        elif source_type == "vwo_docs":
            citation["doc_title"] = p.get("doc_title", "")
            citation["page"] = p.get("page")
            citation["section"] = p.get("section")
        elif source_type == "vwo_bugs":
            citation["jira_id"] = p.get("jira_id", "")
            citation["summary"] = p.get("summary", "")
            citation["status"] = p.get("status", "")
            citation["priority"] = p.get("priority", "")

        # Include text snippet for source panel
        text = p.get("text", "")
        citation["text"] = text[:500] if len(text) > 500 else text

        return citation


class Retriever:
    """Orchestrates hybrid search, merge, and reranking across collections."""

    def __init__(self, store: QdrantStore, encoder: BGE_M3_Encoder, reranker: Reranker):
        self.store = store
        self.encoder = encoder
        self.reranker = reranker

    def retrieve(
        self,
        query: str,
        collections: list[str],
        top_k_per_collection: int = 12,
        rerank_top_k: int = 4,
        min_score: float = 0.3,
    ) -> list[ScoredChunk]:
        """Full retrieval pipeline: embed → parallel hybrid search → merge → rerank → top-k."""
        # 1. Embed query
        emb = self.encoder.encode([query])[0]
        dense = emb["dense"]
        sparse = emb["sparse"]

        # 2. Parallel hybrid search per collection
        def search_collection(name: str):
            return self.store.hybrid_search(name, dense, sparse, top_k=top_k_per_collection)

        with ThreadPoolExecutor(max_workers=len(collections)) as pool:
            results_per = list(pool.map(search_collection, collections))

        # 3. Merge all results
        merged = list(itertools.chain(*results_per))
        if not merged:
            return []

        # 4. Rerank
        passages = [p.payload.get("text", "") for p in merged]
        scores = self.reranker.score(query, passages)

        # 5. Sort and filter
        scored = sorted(zip(merged, scores), key=lambda x: x[1], reverse=True)
        results = []
        for point, score in scored[:rerank_top_k]:
            if score >= min_score or not results:
                # Always include at least one result
                results.append(ScoredChunk(payload=point.payload, score=score))

        return results
