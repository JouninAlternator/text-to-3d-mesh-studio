"""Routes raw user prompts into normalized generation intents."""
from __future__ import annotations

import re
from dataclasses import dataclass

_NEGATIVE_PREFIXES = ("without", "no ", "remove", "avoid")


@dataclass(frozen=True)
class GenerationIntent:
    positive: str
    negative: str
    wants_rigging: bool
    wants_texture: bool


def route_prompt(raw: str) -> GenerationIntent:
    """Split a raw prompt into positive/negative and detect feature asks."""
    text = raw.strip()
    if not text:
        raise ValueError("empty prompt")

    negatives: list[str] = []
    positives: list[str] = []
    for clause in re.split(r"[,;]", text):
        c = clause.strip()
        if any(c.lower().startswith(p) for p in _NEGATIVE_PREFIXES):
            negatives.append(c)
        else:
            positives.append(c)

    low = text.lower()
    return GenerationIntent(
        positive=", ".join(positives) or text,
        negative=", ".join(negatives),
        wants_rigging="rig" in low or "skeleton" in low,
        wants_texture=any(k in low for k in ("texture", "pbr", "material", "uv")),
    )