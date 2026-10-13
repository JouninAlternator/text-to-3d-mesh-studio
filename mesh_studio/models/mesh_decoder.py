"""Implicit SDF decoder queried on a voxel grid, then meshed via marching cubes."""
from __future__ import annotations

import torch
import torch.nn as nn


class MeshDecoder(nn.Module):
    """Decodes triplane features + 3D coords into a signed-distance value.

    Input:  triplane [B, 3, C, R, R], points [B, N, 3] in [-1, 1]
    Output: sdf [B, N]
    """

    def __init__(self, channels: int = 32, hidden_dim: int = 256, num_layers: int = 6) -> None:
        super().__init__()
        self.channels = channels
        feat_dim = channels * 3
        layers: list[nn.Module] = []
        in_dim = feat_dim + 3
        for _ in range(num_layers - 1):
            layers += [nn.Linear(in_dim, hidden_dim), nn.SiLU(inplace=True)]
            in_dim = hidden_dim
        layers.append(nn.Linear(hidden_dim, 1))
        self.mlp = nn.Sequential(*layers)

    def _sample_triplane(self, triplane: torch.Tensor, points: torch.Tensor) -> torch.Tensor:
        # Grid-sample each plane along its two in-plane coordinates.
        b, _, c, r, _ = triplane.shape
        n = points.shape[1]
        xy = points[:, :, :2].unsqueeze(1)  # [B,1,N,2]
        xz = points[:, :, [0, 2]].unsqueeze(1)
        yz = points[:, :, [1, 2]].unsqueeze(1)
        feats = []
        for plane_idx, grid in enumerate((xy, xz, yz)):
            sampled = torch.nn.functional.grid_sample(
                triplane[:, plane_idx], grid, mode="bilinear", align_corners=True
            )  # [B,C,N,1]
            feats.append(sampled.squeeze(-1).permute(0, 2, 1))
        return torch.cat(feats, dim=-1)  # [B, N, C*3]

    def forward(self, triplane: torch.Tensor, points: torch.Tensor) -> torch.Tensor:
        feats = self._sample_triplane(triplane, points)
        x = torch.cat([feats, points], dim=-1)
        return self.mlp(x).squeeze(-1)