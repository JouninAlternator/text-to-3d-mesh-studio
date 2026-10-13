"""Runtime bootstrap: device selection, dtype policy, weight cache wiring."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

import torch

LOG = logging.getLogger("mesh_studio.bootstrap")


@dataclass(frozen=True)
class RuntimeProfile:
    device: torch.device
    dtype: torch.dtype
    vram_budget_gb: float
    weights_dir: Path
    cache_dir: Path


def resolve_profile(cfg: dict) -> RuntimeProfile:
    """Pick device/dtype from config + hardware. Prefers CUDA, falls back to CPU fp32."""
    requested = cfg.get("device", "auto")
    if requested == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(requested)

    if device.type == "cuda":
        # bf16 is stable on Ampere+; fp16 on older cards needs a grad scaler.
        major = torch.cuda.get_device_capability(device)[0]
        dtype = torch.bfloat16 if major >= 8 else torch.float16
        vram = torch.cuda.get_device_properties(device).total_memory / (1024**3)
    else:
        dtype = torch.float32
        vram = 0.0

    weights_dir = Path(cfg.get("weights_dir", "models/weights"))
    cache_dir = Path(cfg.get("cache_dir", "data/mesh_cache"))
    weights_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    LOG.info("profile device=%s dtype=%s vram=%.1fGB", device, dtype, vram)
    return RuntimeProfile(device, dtype, vram, weights_dir, cache_dir)


def seed_everything(seed: int | None) -> None:
    if seed is None:
        return
    import random

    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)