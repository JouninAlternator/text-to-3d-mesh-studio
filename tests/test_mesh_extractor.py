"""Smoke tests for SDF decoding + marching cubes on a sphere field."""
from __future__ import annotations

import torch
import trimesh

from mesh_studio.models.mesh_decoder import MeshDecoder
from mesh_studio.services.mesh_extractor import extract_mesh


class _SphereDecoder(MeshDecoder):
    """Decoder stub returning |p| - r so marching cubes yields a sphere."""

    def __init__(self, radius: float = 0.5):
        super().__init__(channels=4, hidden_dim=16, num_layers=2)
        self.radius = radius

    def forward(self, triplane: torch.Tensor, points: torch.Tensor) -> torch.Tensor:
        return points.norm(dim=-1) - self.radius


def test_extract_sphere_geometry():
    decoder = _SphereDecoder(radius=0.5)
    triplane = torch.zeros(1, 3, 4, 8, 8)
    mesh = extract_mesh(decoder, triplane, resolution=32, iso_surface=0.0)
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0
    # Sphere of radius 0.5 has surface area ~4*pi*r^2 ~ 3.14.
    assert 2.0 < mesh.area < 5.0