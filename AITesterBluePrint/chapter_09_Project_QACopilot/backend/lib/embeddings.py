"""BGE-M3 encoder producing dense (1024-dim) + sparse vectors in one pass."""

from __future__ import annotations

from typing import Any

import numpy as np

_encoder: "BGE_M3_Encoder | None" = None


class BGE_M3_Encoder:
    """Wraps FlagEmbedding BGEM3FlagModel for hybrid dense+sparse encoding."""

    def __init__(self, model_name: str, device: str = "cpu"):
        from FlagEmbedding import BGEM3FlagModel

        self.model = BGEM3FlagModel(model_name, use_fp16=(device != "cpu"), device=device)

    def encode(self, texts: list[str]) -> list[dict[str, Any]]:
        """Encode texts into dense + sparse representations.

        Returns:
            List of dicts with keys:
                - "dense": np.ndarray of shape (1024,)
                - "sparse": dict[int, float] (token_id -> weight)
        """
        output = self.model.encode(
            texts,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        results = []
        dense_vecs = output["dense_vecs"]
        sparse_list = output["lexical_weights"]

        for i in range(len(texts)):
            dense = np.array(dense_vecs[i], dtype=np.float32)
            # sparse_list[i] is a dict {token_id: weight}
            sparse = {int(k): float(v) for k, v in sparse_list[i].items()}
            results.append({"dense": dense, "sparse": sparse})

        return results


def get_encoder() -> BGE_M3_Encoder:
    """Lazy singleton for the encoder. First call downloads ~2GB model."""
    global _encoder
    if _encoder is None:
        from backend.lib.settings import settings

        print(f"[embeddings] Loading {settings.EMBED_MODEL} on {settings.EMBED_DEVICE}...")
        _encoder = BGE_M3_Encoder(settings.EMBED_MODEL, settings.EMBED_DEVICE)
        print("[embeddings] Model loaded.")
    return _encoder
