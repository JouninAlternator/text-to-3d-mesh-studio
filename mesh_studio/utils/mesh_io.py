"""Mesh load/save shims with format detection."""
from __future__ import annotations

from pathlib import Path

import trimesh


def load_mesh(path: str | Path) -> trimesh.Trimesh:
    """Load a mesh file into a trimesh.Trimesh."""
    mesh = trimesh.load(str(path), force="mesh")
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"not a single mesh: {path}")
    return mesh


def save_mesh(mesh: trimesh.Trimesh, path: str | Path) -> Path:
    """Save a mesh, creating parent dirs."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(out.as_posix())
    return out