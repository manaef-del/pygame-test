"""Kleine Vektorhilfen ohne Abhängigkeiten."""

from __future__ import annotations

import math

Vec = tuple[float, float]


def dist(a: Vec, b: Vec) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def norm(v: Vec) -> Vec:
    l = math.hypot(v[0], v[1])
    if l < 1e-9:
        return (0.0, 0.0)
    return (v[0] / l, v[1] / l)


def sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1])


def add(a: Vec, b: Vec) -> Vec:
    return (a[0] + b[0], a[1] + b[1])


def scale(v: Vec, s: float) -> Vec:
    return (v[0] * s, v[1] * s)


def angle_deg(a: Vec, b: Vec) -> float:
    """Winkel zwischen zwei Vektoren in Grad (0..180)."""
    a = norm(a)
    b = norm(b)
    d = max(-1.0, min(1.0, a[0] * b[0] + a[1] * b[1]))
    return math.degrees(math.acos(d))


def arc(facing: Vec, to_attacker: Vec, front_arc: float, rear_arc: float) -> str:
    """Aus welcher Richtung kommt ein Angriff: 'front', 'flank' oder 'rear'."""
    a = angle_deg(facing, to_attacker)
    if a <= front_arc:
        return "front"
    if a >= rear_arc:
        return "rear"
    return "flank"


def snap4(v: Vec) -> Vec:
    """Rundet auf eine der vier Hauptrichtungen."""
    if abs(v[0]) >= abs(v[1]):
        return (1.0 if v[0] >= 0 else -1.0, 0.0)
    return (0.0, 1.0 if v[1] >= 0 else -1.0)
