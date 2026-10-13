"""Text encoder service wrapping a CLIP-style model for prompt conditioning."""
from __future__ import annotations

import functools
import logging

import torch
from transformers import CLIPTextModel, CLIPTokenizer

LOG = logging.getLogger("mesh_studio.text")


@functools.lru_cache(maxsize=2)
def _load(model_id: str, device_str: str):
    tokenizer = CLIPTokenizer.from_pretrained(model_id)
    model = CLIPTextModel.from_pretrained(model_id)
    model.eval()
    device = torch.device(device_str)
    model.to(device)
    return tokenizer, model


@torch.inference_mode()
def encode_text(prompt: str, model_id: str, device: torch.device) -> torch.Tensor:
    """Encode a prompt into a [1, D] CLIP text embedding."""
    tokenizer, model = _load(model_id, str(device))
    tokens = tokenizer(
        prompt, padding="max_length", truncation=True, max_length=77, return_tensors="pt"
    ).to(device)
    out = model(**tokens).last_hidden_state
    pooled = out.mean(dim=1)  # mean-pool over tokens
    LOG.debug("encoded prompt len=%d dim=%d", len(prompt), pooled.shape[-1])
    return pooled