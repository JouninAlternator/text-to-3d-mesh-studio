"""Gradio UI service for interactive text-to-3D generation."""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import gradio as gr

from mesh_studio.bootstrap import resolve_profile
from mesh_studio.pipelines.text_to_mesh import TextToMeshPipeline

LOG = logging.getLogger("mesh_studio.ui")


def build_ui(cfg: dict) -> gr.Blocks:
    profile = resolve_profile(cfg)
    pipe = TextToMeshPipeline(cfg, profile)

    def generate_fn(prompt: str, steps: int, guidance: float, resolution: int):
        if not prompt.strip():
            return None, "prompt required"
        result = pipe.run(prompt, steps=int(steps), guidance=float(guidance), resolution=int(resolution))
        tmp = Path(tempfile.mkdtemp()) / "mesh.glb"
        result.export(tmp)
        return tmp.as_posix(), f"verts={result.vertex_count} faces={result.face_count}"

    with gr.Blocks(title="text-to-3d-mesh-studio") as ui:
        gr.Markdown("# text-to-3d-mesh-studio\nPrompt \u2192 mesh, export GLB.")
        with gr.Row():
            prompt = gr.Textbox(label="Prompt", placeholder="a ceramic teapot, low-poly, matte glaze")
        with gr.Row():
            steps = gr.Slider(16, 128, value=64, step=8, label="Diffusion steps")
            guidance = gr.Slider(1.0, 15.0, value=7.5, step=0.5, label="Guidance")
            resolution = gr.Slider(64, 384, value=256, step=32, label="Grid resolution")
        run_btn = gr.Button("Generate", variant="primary")
        file_out = gr.File(label="Mesh")
        status = gr.Textbox(label="Status")
        run_btn.click(generate_fn, [prompt, steps, guidance, resolution], [file_out, status])
    return ui


def launch_ui(cfg: dict, host: str = "127.0.0.1", port: int = 7860) -> None:
    ui = build_ui(cfg)
    ui.launch(server_name=host, server_port=port, show_error=True)