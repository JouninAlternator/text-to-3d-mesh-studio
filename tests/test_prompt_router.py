"""Tests for prompt routing."""
from __future__ import annotations

import pytest

from mesh_studio.handlers.prompt_router import route_prompt


def test_positive_only():
    intent = route_prompt("a brass lantern, ornate")
    assert "brass lantern" in intent.positive
    assert intent.negative == ""
    assert intent.wants_texture is False


def test_negative_split():
    intent = route_prompt("a low-poly tree, without leaves")
    assert "without leaves" in intent.negative
    assert "tree" in intent.positive


def test_feature_detection():
    intent = route_prompt("a rigged character with pbr texture")
    assert intent.wants_rigging is True
    assert intent.wants_texture is True


def test_empty_prompt_raises():
    with pytest.raises(ValueError):
        route_prompt("   ")