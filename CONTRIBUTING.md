# Contributing to text-to-3d-mesh-studio

Thanks for wanting to help build text-to-3d-mesh-studio. This is an
open-source text-to-3D mesh generator: you type a prompt, we ship a mesh.

## Dev setup

```bash
git clone https://github.com/<you>/text-to-3d-mesh-studio
cd text-to-3d-mesh-studio
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

GPU users: `pip install -e ".[cuda]"` for xformers + triton.

## Repo layout

- `mesh_studio/bootstrap.py` — device/dtype/weights wiring
- `mesh_studio/cli.py` — Typer entrypoint (`mesh-studio generate`, `mesh-studio serve`)
- `mesh_studio/config/` — YAML loader + dataclass schemas
- `mesh_studio/models/` — triplane generator, SDF mesh decoder
- `mesh_studio/handlers/` — prompt routing, mesh export
- `mesh_studio/services/` — text encoder, mesh extractor, optimizer, UI server
- `mesh_studio/pipelines/` — end-to-end text-to-mesh orchestration
- `mesh_studio/utils/` — tensor ops, mesh IO, logging
- `configs/` — default and low_vram configs
- `tests/` — pytest suite

## Adding a new export format

1. Add the extension to `_SUPPORTED` in `mesh_studio/handlers/export_handler.py`.
2. If it needs a custom writer, add a branch in `export_mesh`.
3. Add a roundtrip test in `tests/`.

## Adding a new decoder

1. Implement a `nn.Module` with `forward(triplane, points) -> sdf`.
2. Register it in `mesh_studio/models/__init__.py`.
3. Wire it in `pipelines/text_to_mesh.py`.
4. Add a geometry test asserting a known shape's area/volume.

## PR checklist

- [ ] `ruff check mesh_studio tests`
- [ ] `mypy mesh_studio`
- [ ] `pytest -q`
- [ ] New behavior has a test
- [ ] No new top-level deps without a note in the PR body

##