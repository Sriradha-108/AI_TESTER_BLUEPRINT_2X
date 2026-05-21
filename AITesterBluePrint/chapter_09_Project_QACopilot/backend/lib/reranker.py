"""BGE Reranker v2 M3 cross-encoder for passage reranking."""

from __future__ import annotations

_reranker: "Reranker | None" = None


class Reranker:
    """Wraps FlagEmbedding FlagReranker for cross-encoder scoring."""

    def __init__(self, model_name: str, device: str = "cpu"):
        from FlagEmbedding import FlagReranker

        self.model = FlagReranker(model_name, use_fp16=(device != "cpu"), device=device)

    def score(self, query: str, passages: list[str]) -> list[float]:
        """Score each passage against the query. Returns list of floats (higher = more relevant)."""
        if not passages:
            return []
        pairs = [[query, p] for p in passages]
        scores = self.model.compute_score(pairs)
        # compute_score may return a single float if only one pair
        if isinstance(scores, (int, float)):
            return [float(scores)]
        return [float(s) for s in scores]


def get_reranker() -> Reranker:
    """Lazy singleton for the reranker."""
    global _reranker
    if _reranker is None:
        from backend.lib.settings import settings

        print(f"[reranker] Loading {settings.RERANK_MODEL} on {settings.EMBED_DEVICE}...")
        _reranker = Reranker(settings.RERANK_MODEL, settings.EMBED_DEVICE)
        print("[reranker] Model loaded.")
    return _reranker
