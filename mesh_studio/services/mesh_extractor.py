"""Voxel-grid SDF query + marching cubes to produce a watertight mesh."""
from __future__ import annotations

import logging

import numpy as np
import torch
import trimesh
from skimage import measure

from mesh_studio.models.mesh_decoder import MeshDecoder

LOG = logging.getLogger("mesh_studio.extract")


@torch.inference_mode()
def extract_mesh(
    decoder: MeshDecoder,
    triplane: torch.Tensor,
    resolution: int = 256,
    iso_surface: float = 0.0,
    batch_points: int = 1 << 16,
) -> trimesh.Trimesh:
    """Query the SDF decoder on a dense grid and run marching cubes."""
    device = triplane.device
    lin = torch.linspace(-1.0, 1.0, resolution, device=device)
    gx, gy, gz = torch.meshgrid(lin, lin, lin, indexing="ij")
    points = torch.stack([gx, gy, gz], dim=-1).reshape(1, -1, 3)

    sdf_chunks = []
    for start in range(0, points.shape[1], batch_points):
        chunk = points[:, start : start + batch_points]
        sdf_chunks.append(decoder(triplane, chunk))
    sdf = torch.cat(sdf_chunks, dim=1).reshape(resolution, resolution, resolution)

    sdf_np = sdf.float().cpu().numpy()
    verts, faces, normals, _ = measure.marching_cubes(
        sdf_np, level=iso_surface, spacing=(2.0 / resolution,) * 3
    )
    verts -= (resolution - 1) / resolution
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, vertex_normals=normals, process=True)
    mesh.fix_normals()
    LOG.info("extracted mesh verts=%d faces=%d", len(mesh.vertices), len(mesh.faces))
    return mesh