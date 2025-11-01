"""Slope mathematics utilities."""
from __future__ import annotations

import math
from typing import Tuple

from .models import Point


def rise_run_from_heights(distance: float, h1: float, h2: float) -> Tuple[float, float]:
    """Compute rise and run from heights."""
    run = distance
    rise = h2 - h1
    return rise, run


def percent_from_rise_run(rise: float, run: float) -> float:
    if run == 0:
        return math.copysign(math.inf, rise)
    return (rise / run) * 100.0


def angle_from_rise_run(rise: float, run: float) -> float:
    if run == 0:
        return 90.0 if rise > 0 else -90.0
    return math.degrees(math.atan(rise / run))


def ratio_from_rise_run(rise: float, run: float) -> float:
    if rise == 0:
        return math.inf
    return abs(run / rise)


def slope_from_points(start: Point, end: Point) -> Tuple[float, float]:
    rise = end.z - start.z
    run = end.x - start.x
    percent = percent_from_rise_run(rise, run)
    angle = angle_from_rise_run(rise, run)
    return percent, angle


def run_from_rise_and_percent(rise: float, percent: float) -> float:
    if percent == 0:
        return math.inf
    return rise * 100.0 / percent


def rise_from_percent_and_run(percent: float, run: float) -> float:
    return (percent / 100.0) * run


def rise_from_angle_and_run(angle: float, run: float) -> float:
    return math.tan(math.radians(angle)) * run


def percent_from_angle(angle: float) -> float:
    return math.tan(math.radians(angle)) * 100.0


def angle_from_percent(percent: float) -> float:
    return math.degrees(math.atan(percent / 100.0))


def percent_from_ratio(ratio: float) -> float:
    if ratio == 0:
        return math.copysign(math.inf, ratio)
    return 100.0 / ratio


def ratio_from_percent(percent: float) -> float:
    if percent == 0:
        return math.inf
    return 100.0 / abs(percent)


def sanitize_ratio_display(ratio: float) -> str:
    if math.isinf(ratio):
        return "1:∞"
    return f"1:{ratio:.1f}"

