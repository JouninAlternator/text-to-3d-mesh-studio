"""Small tensor utilities used across the pipeline."""
from __future__ import annotations

import torch


def normalize_embeddings(emb: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """L2-normalize the last dimension."""
    norm = emb.norm(p=2, dim=-1, keepdim=True).clamp_min(eps)
    return emb / norm


def chunked(seq, size: int):
    """Yield successive chunks from a sequence."""
    for i in range(0, len(seq), size):
        yield seq[i : i + size]