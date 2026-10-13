"""Lightweight dataclass schemas for config sections."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiffusionCfg:
    model_id: str = "stabilityai/sd-turbo"
    steps: int = 64
    guidance: float = 7.5
    image_size: int = 512


@dataclass(frozen=True)
class TriplaneCfg:
    channels: int = 32
    resolution: int = 128
    num_planes: int = 3


@dataclass(frozen=True)
class DecoderCfg:
    hidden_dim: int = 256
    num_layers: int = 6
    iso_surface: float = 0.0


@dataclass(frozen=True)
class ExportCfg:
    format: str = "glb"
    decimate_ratio: float = 1.0
    smooth_iterations: int = 0