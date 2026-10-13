"""Mesh export handler: write GLB/OBJ/STL from a trimesh object."""
from __future__ import annotations

import logging
from pathlib import Path

import trimesh

LOG = logging.getLogger("mesh_studio.export")

_SUPPORTED = {".glb", ".gltf", ".obj", ".stl", ".ply"}


def export_mesh(mesh: trimesh.Trimesh, out_path: Path, decimate_ratio: float = 1.0) -> Path:
    """Export mesh to out_path. Decimates if ratio < 1.0."""
    suffix = out_path.suffix.lower()
    if suffix not in _SUPPORTED:
        raise ValueError(f"unsupported export format: {suffix}")

    if decimate_ratio < 1.0:
        target_faces = max(64, int(len(mesh.faces) * decimate_ratio))
        mesh = mesh.simplify_quadric_decimation(target_faces)
        LOG.info("decimated to %d faces", len(mesh.faces))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(out_path.as_posix())
    LOG.info("exported %s verts=%d faces=%d", out_path, len(mesh.vertices), len(mesh.faces))
    return out_path