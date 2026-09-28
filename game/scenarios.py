"""Szenarien: Verteidigung der eigenen Siedlung und Angriffe.

Bei der Verteidigung kommen Räuber von Norden und plündern. Beim Angriff
steht der Gegner im Norden: eine Räuberhorde oder eine Siedlung mit
derselben Truppenmischung wie die eigene, ohne oder mit Wall. Die
Gegnerstärke wird vor der Schlacht eingestellt.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import config

Cell = tuple[int, int]
Point = tuple[float, float]


@dataclass(frozen=True)
class RaiderSpawn:
    x: float
    y: float
    waypoints: tuple[Point, ...] = ()


@dataclass(frozen=True)
class Scenario:
    key: str
    name: str
    hint: str
    role: str                                  # "verteidigung" oder "angriff"
    enemy_kind: str                            # "raeuber" oder "spiegel"
    enemy_default: int
    enemy_min: int
    enemy_max: int
    houses: tuple[Cell, ...] = ()
    palisade: tuple[Cell, ...] = ()
    gate: Cell | None = None
    gate_closed: bool = False                  # muss aufgebrochen werden
    wall_side: str | None = None               # wer den Wehrgang nutzen darf: "stadt"/"feind"
    ladders: tuple[Cell, ...] = ()             # Wallstücke mit Leiter: nur dort hinauf und hinunter
    raider_spawns: tuple[RaiderSpawn, ...] = ()
    deploy_y: float = 10.5                     # eigene Truppe
    enemy_deploy_y: float = 5.0                # gespiegelte Truppe
    ram_available: bool = False


HOUSES_SOUTH = ((4, 13), (6, 13), (8, 13), (10, 13), (5, 15), (7, 15), (9, 15), (11, 15))
HOUSES_NORTH = ((4, 1), (6, 1), (8, 1), (10, 1), (5, 3), (7, 3), (9, 3), (11, 3))


def _palisade_row(row: int, gate_cols: tuple[int, ...]) -> tuple[Cell, ...]:
    return tuple((c, row) for c in range(config.COLS) if c not in gate_cols)


RAIDS_OPEN = (
    RaiderSpawn(4.5, -1.0), RaiderSpawn(6.5, -2.0), RaiderSpawn(8.5, -1.0), RaiderSpawn(10.5, -2.0),
    RaiderSpawn(12.5, -1.0), RaiderSpawn(7.5, -3.5),
    RaiderSpawn(0.6, -1.0, waypoints=((0.7, 11.5),)), RaiderSpawn(15.4, -1.0, waypoints=((15.3, 11.5),)),
    RaiderSpawn(5.5, -5.0), RaiderSpawn(9.5, -5.0), RaiderSpawn(3.0, -6.5), RaiderSpawn(12.0, -6.5),
)

RAIDS_GATE = tuple(
    RaiderSpawn(x, y, waypoints=((7.5, 6.0),))
    for x, y in (
        (3.5, -1.0), (5.5, -2.0), (7.5, -1.0), (9.5, -2.0), (11.5, -1.0),
        (4.5, -3.5), (7.5, -4.0), (10.5, -3.5), (6.0, -6.0), (9.0, -6.0),
        (3.0, -7.5), (12.0, -7.5), (5.0, -9.0), (10.0, -9.0),
    )
)

HORDE = tuple(
    RaiderSpawn(x, y)
    for x, y in ((4.0, 3.5), (6.5, 2.5), (9.5, 2.5), (12.0, 3.5), (5.0, 5.0), (8.0, 4.5), (11.0, 5.0),
                 (3.0, 1.5), (13.0, 1.5), (7.0, 0.8), (9.5, 6.3), (6.0, 6.3))
)

OFFENE_SIEDLUNG = Scenario(
    key="offen", name="Verteidigung: Offene Siedlung",
    hint="Räuber von Norden, zwei Trupps umgehen die Linie. Tippe eine Gruppe an, dann ziehe ihre Front auf.",
    role="verteidigung", enemy_kind="raeuber", enemy_default=128, enemy_min=32, enemy_max=192,
    houses=HOUSES_SOUTH, raider_spawns=RAIDS_OPEN,
)

PALISADE = Scenario(
    key="palisade", name="Verteidigung: Palisade",
    hint="Das Tor ist zu; die Räuber bauen Rammbock und Turm. Peltasten über die Leitern auf den Wehrgang, Hopliten hinters Tor, Reserve gegen den Turm.",
    role="verteidigung", enemy_kind="raeuber", enemy_default=128, enemy_min=32, enemy_max=224,
    houses=HOUSES_SOUTH, palisade=_palisade_row(8, gate_cols=(7, 8)), gate=(7, 8), gate_closed=True,
    wall_side="stadt", ladders=((2, 8), (13, 8)), raider_spawns=RAIDS_GATE,
)

RAEUBERHORDE = Scenario(
    key="horde", name="Angriff: Räuberhorde",
    hint="Die Horde lagert im Norden. Sie greift an, sobald du ihr nahe kommst.",
    role="angriff", enemy_kind="raeuber", enemy_default=96, enemy_min=16, enemy_max=192,
    raider_spawns=HORDE, deploy_y=15.5,
)

SIEDLUNG_OFFEN = Scenario(
    key="angriff_offen", name="Angriff: Siedlung ohne Wall",
    hint="Die Siedlung stellt dieselben Truppen wie du. Ihre Reiter greifen an, der Rest hält.",
    role="angriff", enemy_kind="spiegel", enemy_default=75, enemy_min=20, enemy_max=150,
    houses=HOUSES_NORTH, deploy_y=15.5, enemy_deploy_y=5.5,
)

SIEDLUNG_WALL = Scenario(
    key="angriff_wall", name="Angriff: Siedlung mit Wall",
    hint="Das Tor ist zu. Wähle eine Gruppe und lass sie Rammbock oder Turm bauen; dann Tor oder Wall antippen.",
    role="angriff", enemy_kind="spiegel", enemy_default=75, enemy_min=20, enemy_max=150,
    houses=HOUSES_NORTH, palisade=_palisade_row(7, gate_cols=(7, 8)), gate=(7, 7), gate_closed=True,
    wall_side="feind", ladders=((2, 7), (13, 7)), deploy_y=15.5, enemy_deploy_y=4.9, ram_available=True,
)

SCENARIOS: tuple[Scenario, ...] = (OFFENE_SIEDLUNG, PALISADE, RAEUBERHORDE, SIEDLUNG_OFFEN, SIEDLUNG_WALL)
