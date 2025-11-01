"""Unit conversion helpers."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class UnitSystem(str, Enum):
    """Supported unit systems."""

    METRIC = "metric"
    IMPERIAL = "imperial"


@dataclass
class UnitPreferences:
    """Current preferred unit system."""

    system: UnitSystem = UnitSystem.METRIC

    @property
    def length_label(self) -> str:
        return "m" if self.system == UnitSystem.METRIC else "ft"

    def to_metric(self, value: float) -> float:
        """Convert value from current unit system to metric meters."""
        if self.system == UnitSystem.METRIC:
            return value
        return value * 0.3048

    def from_metric(self, value: float) -> float:
        """Convert value from metric to the configured unit system."""
        if self.system == UnitSystem.METRIC:
            return value
        return value / 0.3048

