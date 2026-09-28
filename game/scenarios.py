"""Szenarien: Karte, Häuser, Palisade, Aufstellung beider Seiten.

Koordinaten sind Kacheln. Häuser und Palisade liegen auf ganzen Kacheln,
Lochoi stehen auf Kachelmitten (z. B. 6.5, 10.5).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import config

Cell = tuple[int, int]
Point = tuple[float, float]


@dataclass(frozen=True)
class UnitSpec:
    kind: str
    x: float
    y: float
    waypoints: tuple[Point, ...] = ()


@dataclass(frozen=True)
class Scenario:
    key: str
    name: str
    hint: str
    houses: tuple[Cell, ...]
    player: tuple[UnitSpec, ...]
    enemies: tuple[UnitSpec, ...]
    palisade: tuple[Cell, ...] = ()
    gate: Cell | None = None


HOUSES = ((4, 13), (6, 13), (8, 13), (10, 13), (5, 15), (7, 15), (9, 15), (11, 15))

PLAYER_DEFAULT = (
    UnitSpec("hoplit", 6.5, 10.5),
    UnitSpec("hoplit", 8.5, 10.5),
    UnitSpec("hoplit", 10.5, 10.5),
    UnitSpec("leichter", 4.5, 10.5),
    UnitSpec("thet", 8.5, 11.5),
)


def _palisade_row(row: int, gate_cols: tuple[int, ...]) -> tuple[Cell, ...]:
    return tuple((c, row) for c in range(config.COLS) if c not in gate_cols)


OFFENE_SIEDLUNG = Scenario(
    key="offen",
    name="Offene Siedlung",
    hint="Räuber von Norden, zwei Trupps umgehen die Linie. Ziehe einen Bereich für die Phalanx.",
    houses=HOUSES,
    player=PLAYER_DEFAULT,
    enemies=(
        UnitSpec("raeuber", 5.5, -1.0),
        UnitSpec("raeuber", 7.5, -1.5),
        UnitSpec("raeuber", 9.5, -1.0),
        UnitSpec("raeuber", 11.5, -1.5),
        UnitSpec("raeuber", 0.5, -1.0, waypoints=((0.6, 11.5),)),
        UnitSpec("raeuber", 15.5, -1.0, waypoints=((15.4, 11.5),)),
    ),
)

PALISADE = Scenario(
    key="palisade",
    name="Palisade mit Tor",
    hint="Deutliche Übermacht, aber nur ein Tor. Stelle die Phalanx dahinter.",
    houses=HOUSES,
    player=PLAYER_DEFAULT,
    enemies=tuple(
        UnitSpec("raeuber", x, y, waypoints=((7.5, 6.0),))
        for x, y in (
            (3.5, -1.0), (5.5, -2.0), (7.5, -1.0), (9.5, -2.0), (11.5, -1.0),
            (4.5, -3.5), (7.5, -4.0), (10.5, -3.5), (7.5, -6.0),
        )
    ),
    palisade=_palisade_row(8, gate_cols=(7, 8)),
    gate=(7, 8),
)

SCENARIOS: tuple[Scenario, ...] = (OFFENE_SIEDLUNG, PALISADE)
