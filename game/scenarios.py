"""Szenarien: Karte, Häuser, Palisade, Räuber. Die eigene Truppe kommt
aus der Aufstellung (game/army.py) und wird im Aufmarschraum platziert."""

from __future__ import annotations

from dataclasses import dataclass

from . import config

Cell = tuple[int, int]
Point = tuple[float, float]


@dataclass(frozen=True)
class EnemySpec:
    men: int
    x: float
    y: float
    waypoints: tuple[Point, ...] = ()
    rows: int = 2


@dataclass(frozen=True)
class Scenario:
    key: str
    name: str
    hint: str
    houses: tuple[Cell, ...]
    enemies: tuple[EnemySpec, ...]
    deploy_y: float = 10.5
    palisade: tuple[Cell, ...] = ()
    gate: Cell | None = None


HOUSES = ((4, 13), (6, 13), (8, 13), (10, 13), (5, 15), (7, 15), (9, 15), (11, 15))


def _palisade_row(row: int, gate_cols: tuple[int, ...]) -> tuple[Cell, ...]:
    return tuple((c, row) for c in range(config.COLS) if c not in gate_cols)


OFFENE_SIEDLUNG = Scenario(
    key="offen",
    name="Offene Siedlung",
    hint="Räuber von Norden, zwei Trupps umgehen die Linie. Tippe eine Gruppe an, dann ziehe ihre Front mit dem Finger auf.",
    houses=HOUSES,
    enemies=(
        EnemySpec(16, 4.5, -1.0),
        EnemySpec(16, 6.5, -2.0),
        EnemySpec(16, 8.5, -1.0),
        EnemySpec(16, 10.5, -2.0),
        EnemySpec(16, 12.5, -1.0),
        EnemySpec(16, 7.5, -3.5),
        EnemySpec(16, 0.6, -1.0, waypoints=((0.7, 11.5),)),
        EnemySpec(16, 15.4, -1.0, waypoints=((15.3, 11.5),)),
    ),
)

PALISADE = Scenario(
    key="palisade",
    name="Palisade mit Tor",
    hint="Deutliche Übermacht, aber nur ein Tor. Zieh die Hopliten dahinter auf.",
    houses=HOUSES,
    enemies=tuple(
        EnemySpec(16, x, y, waypoints=((7.5, 6.0),))
        for x, y in (
            (3.5, -1.0), (5.5, -2.0), (7.5, -1.0), (9.5, -2.0), (11.5, -1.0),
            (4.5, -3.5), (7.5, -4.0), (10.5, -3.5), (6.0, -6.0), (9.0, -6.0),
            (3.0, -7.5), (12.0, -7.5),
        )
    ),
    palisade=_palisade_row(8, gate_cols=(7, 8)),
    gate=(7, 8),
)

SCENARIOS: tuple[Scenario, ...] = (OFFENE_SIEDLUNG, PALISADE)
