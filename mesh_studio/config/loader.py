"""YAML config loader with env-var override and schema validation."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

_REQUIRED_KEYS = ("device", "diffusion", "triplane", "decoder", "export")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load YAML config and merge MESH_STUDIO_* env overrides."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"config not found: {p}")
    with p.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    for key in _REQUIRED_KEYS:
        if key not in cfg:
            raise ValueError(f"config missing required key: {key}")

    env_device = os.environ.get("MESH_STUDIO_DEVICE")
    if env_device:
        cfg["device"] = env_device
    env_cache = os.environ.get("MESH_STUDIO_CACHE")
    if env_cache:
        cfg["cache_dir"] = env_cache
    return cfg