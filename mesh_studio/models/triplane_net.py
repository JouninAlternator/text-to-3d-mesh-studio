"""Triplane latent generator: text embedding -> 3 orthogonal feature planes."""
from __future__ import annotations

import torch
import torch.nn as nn

from mesh_studio.utils.tensor_ops import normalize_embeddings


class TriplaneGenerator(nn.Module):
    """Maps a text embedding to a (3, C, R, R) triplane latent.

    Input:  text_emb [B, D]
    Output: triplane [B, 3, C, R, R]
    """

    def __init__(self, text_dim: int = 1024, channels: int = 32, resolution: int = 128) -> None:
        super().__init__()
        self.channels = channels
        self.resolution = resolution
        self.proj = nn.Linear(text_dim, channels * resolution * resolution)
        self.norm = nn.LayerNorm(channels)

    def forward(self, text_emb: torch.Tensor) -> torch.Tensor:
        emb = normalize_embeddings(text_emb)
        flat = self.proj(emb)  # [B, C*R*R]
        plane = flat.view(-1, self.channels, self.resolution, self.resolution)
        plane = self.norm(plane.permute(0, 2, 3, 1)).permute(0, 3, 1, 2)
        # Three orthogonal views share the same base plane then rotate view axis.
        triplane = torch.stack([plane, plane.transpose(-1, -2), plane.flip(-1)], dim=1)
        return triplane.contiguous()