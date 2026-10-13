"""Post-process mesh: weld, smooth, decimate, compute normals."""
from __future__ import annotations

import logging

import trimesh

LOG = logging.getLogger("mesh_studio.optimize")


def optimize_mesh(
    mesh: trimesh.Trimesh,
    weld_tol: float = 1e-4,
    smooth_iterations: int = 0,
    decimate_ratio: float = 1.0,
) -> trimesh.Trimesh:
    """Weld duplicate verts, optionally smooth and decimate."""
    mesh.merge_vertices(merge_tex=True, merge_norm=True)
    mesh.remove_degenerate_faces()
    mesh.remove_duplicate_faces()

    if smooth_iterations > 0:
        trimesh.smoothing.filter_humphrey(mesh, iterations=smooth_iterations)

    if decimate_ratio < 1.0:
        target = max(64, int(len(mesh.faces) * decimate_ratio))
        mesh = mesh.simplify_quadric_decimation(target)

    mesh.fix_normals()
    LOG.info("optimized verts=%d faces=%d", len(mesh.vertices), len(mesh.faces))
    return mesh