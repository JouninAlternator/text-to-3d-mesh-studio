"""End-to-end text-to-3D pipeline: prompt -> triplane -> SDF grid -> mesh."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import trimesh

from mesh_studio.bootstrap import RuntimeProfile
from mesh_studio.handlers.export_handler import export_mesh
from mesh_studio.handlers.prompt_router import route_prompt
from mesh_studio.models.mesh_decoder import MeshDecoder
from mesh_studio.models.triplane_net import TriplaneGenerator
from mesh_studio.services.mesh_extractor import extract_mesh
from mesh_studio.services.mesh_optimizer import optimize_mesh
from mesh_studio.services.text_encoder import encode_text

LOG = logging.getLogger("mesh_studio.pipeline")


@dataclass
class MeshResult:
    mesh: trimesh.Trimesh
    prompt: str

    @property
    def vertex_count(self) -> int:
        return len(self.mesh.vertices)

    @property
    def face_count(self) -> int:
        return len(self.mesh.faces)

    def export(self, out_path: Path) -> Path:
        return export_mesh(self.mesh, Path(out_path))


class TextToMeshPipeline:
    """Orchestrates encoding, triplane generation, SDF query, meshing, optimize."""

    def __init__(self, cfg: dict, profile: RuntimeProfile) -> None:
        self.cfg = cfg
        self.profile = profile
        tcfg = cfg["triplane"]
        dcfg = cfg["decoder"]
        self.generator = TriplaneGenerator(
            text_dim=cfg["diffusion"].get("text_dim", 1024),
            channels=tcfg["channels"],
            resolution=tcfg["resolution"],
        ).to(profile.device, dtype=profile.dtype)
        self.decoder = MeshDecoder(
            channels=tcfg["channels"],
            hidden_dim=dcfg["hidden_dim"],
            num_layers=dcfg["num_layers"],
        ).to(profile.device, dtype=profile.dtype)
        self.generator.eval()
        self.decoder.eval()

    def run(self, prompt: str, steps: int = 64, guidance: float = 7.5, resolution: int = 256) -> MeshResult:
        intent = route_prompt(prompt)
        LOG.info("intent positive=%r negative=%r", intent.positive, intent.negative)

        text_emb = encode_text(intent.positive, self.cfg["diffusion"]["model_id"], self.profile.device)
        text_emb = text_emb.to(self.profile.dtype)
        triplane = self.generator(text_emb)

        mesh = extract_mesh(
            self.decoder,
            triplane,
            resolution=resolution,
            iso_surface=self.cfg["decoder"]["iso_surface"],
        )
        mesh = optimize_mesh(
            mesh,
            smooth_iterations=self.cfg["export"].get("smooth_iterations", 0),
            decimate_ratio=self.cfg["export"].get("decimate_ratio", 1.0),
        )
        return MeshResult(mesh=mesh, prompt=prompt)