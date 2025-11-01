"""Backward-compatible entrypoint for the modern application."""
from __future__ import annotations

from app.main import run


def compute_slope(distance: float, h1: float, h2: float) -> float:
    """Compute slope percentage for legacy tests."""
    return ((h2 - h1) / distance) * 100 if distance != 0 else float("inf")


__all__ = ["run", "compute_slope"]
