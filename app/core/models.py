"""Domain models for slope profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Point:
    """Represents a single coordinate in a slope profile."""

    x: float
    z: float


@dataclass
class Segment:
    """A segment between two points of the profile."""

    start: Point
    end: Point
    slope_percent: float
    angle_degrees: float


@dataclass
class Profile:
    """A profile consisting of ordered points and derived segments."""

    points: List[Point] = field(default_factory=list)

    def as_segments(self) -> List[Segment]:
        """Create segments using consecutive points."""
        from .slope import slope_from_points

        segments: List[Segment] = []
        for start, end in zip(self.points[:-1], self.points[1:]):
            percent, angle = slope_from_points(start, end)
            segments.append(
                Segment(start=start, end=end, slope_percent=percent, angle_degrees=angle)
            )
        return segments

    @property
    def total_distance(self) -> float:
        """Total horizontal distance covered by the profile."""
        if len(self.points) < 2:
            return 0.0
        return sum(abs(b.x - a.x) for a, b in zip(self.points[:-1], self.points[1:]))

    @property
    def total_rise(self) -> float:
        """Total rise between first and last point."""
        if len(self.points) < 2:
            return 0.0
        return self.points[-1].z - self.points[0].z

