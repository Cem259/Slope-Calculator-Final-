"""CSV and JSON persistence helpers."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List, Tuple

from .models import Point, Profile


class CSVProfileError(Exception):
    """Raised when CSV parsing fails."""


def read_basic_csv(path: Path) -> Tuple[float, float, float]:
    """Read a simple CSV with distance, h1, h2 values."""
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"distance", "h1", "h2"}
        if not required.issubset(reader.fieldnames or {}):
            raise CSVProfileError("Missing required columns distance,h1,h2")
        row = next(reader, None)
        if row is None:
            raise CSVProfileError("File is empty")
        try:
            distance = float(row["distance"])
            h1 = float(row["h1"])
            h2 = float(row["h2"])
        except ValueError as exc:
            raise CSVProfileError(f"Invalid numeric value: {exc}") from exc
    return distance, h1, h2


def read_profile_csv(path: Path) -> Profile:
    """Read a polyline profile from CSV."""
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"x", "z"}
        if not required.issubset(reader.fieldnames or {}):
            raise CSVProfileError("Missing required columns x,z")
        points: List[Point] = []
        for idx, row in enumerate(reader, start=2):
            try:
                x = float(row["x"])
                z = float(row["z"])
            except ValueError as exc:
                raise CSVProfileError(f"Row {idx}: {exc}") from exc
            points.append(Point(x=x, z=z))
    if not points:
        raise CSVProfileError("Profile must contain at least one point")
    return Profile(points=points)


def write_profile_csv(path: Path, profile: Profile) -> None:
    """Write profile with per-segment slopes."""
    segments = profile.as_segments()
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["x", "z", "slope_percent", "angle_degrees"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for point, segment in zip(profile.points, segments + [None]):
            writer.writerow(
                {
                    "x": point.x,
                    "z": point.z,
                    "slope_percent": "" if segment is None else f"{segment.slope_percent:.3f}",
                    "angle_degrees": "" if segment is None else f"{segment.angle_degrees:.3f}",
                }
            )


def save_project(path: Path, profile: Profile) -> None:
    data = {"points": [[p.x, p.z] for p in profile.points]}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_project(path: Path) -> Profile:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Profile(points=[Point(x=pt[0], z=pt[1]) for pt in data.get("points", [])])


def profile_from_basic(distance: float, h1: float, h2: float) -> Profile:
    """Create a profile with just start/end points."""
    return Profile(points=[Point(0.0, h1), Point(distance, h2)])


def profile_from_segments(segments: Iterable[Tuple[float, float]]) -> Profile:
    """Create profile from iterable of (x,z)."""
    return Profile(points=[Point(x, z) for x, z in segments])

