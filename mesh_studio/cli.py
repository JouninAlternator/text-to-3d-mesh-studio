"""Typer CLI entrypoint for text-to-3d-mesh-studio."""
from __future__ import annotations

import logging
from pathlib import Path

import typer
from rich.console import Console

from mesh_studio.bootstrap import resolve_profile, seed_everything
from mesh_studio.config.loader import load_config
from mesh_studio.pipelines.text_to_mesh import TextToMeshPipeline

app = typer.Typer(add_completion=False, help="Text-to-3D mesh studio")
console = Console()


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Text prompt describing the object"),
    out: Path = typer.Option(Path("exports/out.glb"), "--out", "-o"),
    config: Path = typer.Option(Path("configs/default.yaml"), "--config", "-c"),
    seed: int | None = typer.Option(None, "--seed"),
    steps: int = typer.Option(64, "--steps"),
    guidance: float = typer.Option(7.5, "--guidance"),
    resolution: int = typer.Option(256, "--res", help="Marching-cubes grid resolution"),
) -> None:
    """Generate a 3D mesh from a text prompt and export it."""
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
    cfg = load_config(config)
    seed_everything(seed)
    profile = resolve_profile(cfg)
    pipe = TextToMeshPipeline(cfg, profile)
    result = pipe.run(prompt, steps=steps, guidance=guidance, resolution=resolution)
    result.export(out)
    console.print(f"[green]wrote[/green] {out}  verts={result.vertex_count} faces={result.face_count}")


@app.command()
def serve(
    config: Path = typer.Option(Path("configs/default.yaml"), "--config", "-c"),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(7860, "--port"),
) -> None:
    """Launch the Gradio UI."""
    from mesh_studio.services.ui_server import launch_ui

    launch_ui(load_config(config), host=host, port=port)


if __name__ == "__main__":
    app()