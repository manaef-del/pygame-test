"""Szenarien: Verteidigung der eigenen Siedlung und Angriffe.

Bei der Verteidigung kommen Räuber von Norden und plündern. Beim Angriff
steht der Gegner im Norden: eine Räuberhorde oder eine Siedlung mit
derselben Truppenmischung wie die eigene, ohne oder mit Wall. Die
Gegnerstärke wird vor der Schlacht eingestellt.
"""

from __future__ import annotations

import math
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
    agora: tuple[float, float] | None = None   # Platz der Siedlung: hier sammeln sich ihre Verteidiger
    cols: int = config.COLS                    # Kartengröße in Kacheln
    rows: int = config.ROWS
    gates: tuple[tuple[tuple[Cell, ...], Cell], ...] = ()   # weitere Tore: (Kacheln, Richtung nach außen)
    corner_towers: tuple[Cell, ...] = ()       # Wehrtürme auf dem Wall, die Speere werfen
    ring: tuple[Point, ...] = ()               # Ecken eines geschlossenen Walls (Festung), sonst gerade Palisade


# Zwei Häuserblöcke zu je zwei mal zwei, dazwischen eine breite Gasse zur Agora (Häuser sind Hindernisse)
HOUSES_SOUTH = ((4, 13), (5, 13), (4, 14), (5, 14), (10, 13), (11, 13), (10, 14), (11, 14))
HOUSES_NORTH = ((4, 1), (5, 1), (4, 2), (5, 2), (10, 1), (11, 1), (10, 2), (11, 2))
AGORA_SOUTH = (8.0, 17.0)       # hinter den Häusern
AGORA_NORTH = (8.0, 2.5)        # mitten in der Siedlung, zwischen den Häuserreihen (dahinter liegt die Kopfleiste)


def _palisade_row(row: int, gate_cols: tuple[int, ...]) -> tuple[Cell, ...]:
    return tuple((c, row) for c in range(config.COLS) if c not in gate_cols)


RAIDS_GATE = tuple(
    RaiderSpawn(x, y, waypoints=((7.5, 6.0),))
    for x, y in (
        (3.5, -1.0), (5.5, -2.0), (7.5, -1.0), (9.5, -2.0), (11.5, -1.0),
        (4.5, -3.5), (7.5, -4.0), (10.5, -3.5), (6.0, -6.0), (9.0, -6.0),
        (3.0, -7.5), (12.0, -7.5), (5.0, -9.0), (10.0, -9.0),
    )
)

PALISADE = Scenario(
    key="palisade", name="Verteidigung: Palisade",
    hint="Das Tor ist zu; die Räuber bauen Rammbock und Turm. Peltasten über die Leitern auf den Wehrgang, Hopliten hinters Tor, Reserve gegen den Turm.",
    role="verteidigung", enemy_kind="raeuber", enemy_default=128, enemy_min=32, enemy_max=224,
    houses=HOUSES_SOUTH, palisade=_palisade_row(8, gate_cols=(7, 8)), gate=(7, 8), gate_closed=True,
    wall_side="stadt", ladders=((2, 8), (13, 8)), raider_spawns=RAIDS_GATE, agora=AGORA_SOUTH,
)

SIEDLUNG_WALL = Scenario(
    key="angriff_wall", name="Angriff: Siedlung mit Wall",
    hint="Das Tor ist zu. Wähle eine Gruppe und lass sie Rammbock oder Turm bauen; dann Tor oder Wall antippen.",
    role="angriff", enemy_kind="spiegel", enemy_default=75, enemy_min=20, enemy_max=150,
    houses=HOUSES_NORTH, palisade=_palisade_row(7, gate_cols=(7, 8)), gate=(7, 7), gate_closed=True,
    wall_side="feind", ladders=((2, 7), (13, 7)), deploy_y=15.5, enemy_deploy_y=4.9, ram_available=True,
    agora=AGORA_NORTH,
)

# ------------------------------------------------------------------ Festung
FORT_COLS, FORT_ROWS = 2 * config.COLS, 2 * config.ROWS      # viermal so groß
FORT_CENTRE = (FORT_COLS / 2, FORT_ROWS / 2)
FORT_RADIUS = 10.5


def _hexagon(centre: Point, radius: float) -> tuple[Point, ...]:
    """Ecken eines Sechsecks mit waagrechter Ober- und Unterkante, im Uhrzeigersinn
    (auf dem Bildschirm, y nach unten), beginnend im Osten."""
    cx, cy = centre
    h = radius * math.sqrt(3) / 2
    return ((cx + radius, cy), (cx + radius / 2, cy + h), (cx - radius / 2, cy + h),
            (cx - radius, cy), (cx - radius / 2, cy - h), (cx + radius / 2, cy - h))


def inside_polygon(poly: tuple[Point, ...], x: float, y: float) -> bool:
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        if (bx - ax) * (y - ay) - (by - ay) * (x - ax) < 0:
            return False
    return True


def _fortress() -> dict:
    """Ein sechseckiger Wall um die Agora: Wallkacheln sind die inneren Kacheln mit
    einem äußeren Nachbarn (auch über Eck), so hängt der Wall an den Schrägen ohne
    Lücke zusammen. Tore in der Nordkante und in den beiden südlichen Schrägen,
    Wehrtürme an den sechs Ecken, Leitern innen an jeder Kante."""
    poly = _hexagon(FORT_CENTRE, FORT_RADIUS)
    inner = {(x, y) for x in range(FORT_COLS) for y in range(FORT_ROWS) if inside_polygon(poly, x + 0.5, y + 0.5)}
    wall = {c for c in inner if any((c[0] + dx, c[1] + dy) not in inner for dx in (-1, 0, 1) for dy in (-1, 0, 1))}
    cx, cy = FORT_CENTRE

    def nearest_wall(p: Point, pool=None) -> Cell:
        return min(pool or wall, key=lambda c: (c[0] + 0.5 - p[0]) ** 2 + (c[1] + 0.5 - p[1]) ** 2)

    def mid(i: int, t: float = 0.5) -> Point:
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % 6]
        return (ax + (bx - ax) * t, ay + (by - ay) * t)

    # Nordtor: zwei Kacheln mitten in der Oberkante (Kante 4: Nordwest-Ecke -> Nordost-Ecke)
    top_row = min(c[1] for c in wall)
    north = tuple(sorted((x, top_row) for x in (int(cx) - 1, int(cx))))
    gates = [(north, (0, -1))]
    # Südwest- und Südosttor: in den unteren Schrägen (Kanten 2 und 0) zwei Reihen, alle Wallkacheln dort
    for edge, out in ((2, (-1, 0)), (0, (1, 0))):
        mx, my = mid(edge)
        row = int(my)
        cells = tuple(sorted(c for c in wall if c[1] in (row - 1, row) and (c[0] < cx) == (out[0] < 0)))
        gates.append((cells, out))
    gate_cells = {c for cells, _ in gates for c in cells}
    towers = tuple(nearest_wall(v, [c for c in wall if c not in gate_cells]) for v in poly)
    # Leitern: an jeder Kante zwei, innen anliegend, nicht an Tor oder Turm
    ladders = []
    for i in range(6):
        for t in (0.3, 0.7):
            p = mid(i, t)
            pool = [c for c in wall if c not in gate_cells and c not in towers
                    and any((c[0] + dx, c[1] + dy) in inner and (c[0] + dx, c[1] + dy) not in wall
                            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    and all(abs(c[0] - g[0]) + abs(c[1] - g[1]) > 1 for g in gate_cells | set(towers))]
            ladders.append(nearest_wall(p, pool))
    houses = _town(inner - wall, wall | gate_cells, gates, FORT_CENTRE, tuple(set(ladders)))
    return {
        "poly": poly, "palisade": tuple(sorted(wall - gate_cells)), "gates": tuple(gates),
        "towers": towers, "ladders": tuple(sorted(set(ladders))), "houses": houses,
    }


def _town(inner: set, wall: set, gates: list, agora: Point, ladders: tuple) -> tuple[Cell, ...]:
    """Häuser in Blöcken zu zwei mal zwei, mit schmalen Gängen dazwischen. Frei bleiben
    ein Streifen innen am Wall, ein Platz an jeder Leiter, ein Ring um die Agora und je
    eine breite Gasse von jedem Tor zur Agora."""
    ax, ay = agora

    def gate_inside(cells, out) -> Point:
        mx = sum(c[0] + 0.5 for c in cells) / len(cells)
        my = sum(c[1] + 0.5 for c in cells) / len(cells)
        return (mx - out[0] * 1.5, my - out[1] * 1.5)

    def to_segment(p: Point, a: Point, b: Point) -> float:
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
        return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

    streets = [gate_inside(cells, out) for cells, out in gates]

    def free_ground(c: Cell) -> bool:
        p = (c[0] + 0.5, c[1] + 0.5)
        if any(abs(c[0] - w[0]) <= 1 and abs(c[1] - w[1]) <= 1 for w in wall):
            return False                                      # Streifen innen am Wall
        if any(math.hypot(p[0] - lx - 0.5, p[1] - ly - 0.5) < 2.3 for lx, ly in ladders):
            return False                                      # Platz am Fuß jeder Leiter: dort kommt man an und sammelt sich
        if math.hypot(p[0] - ax, p[1] - ay) < 2.9:
            return False                                      # Ring um die Agora
        return all(to_segment(p, g, agora) >= 1.6 for g in streets)   # Gassen zu den Toren
    cand = {c for c in inner if free_ground(c)}
    best: set = set()
    for ox in range(3):
        for oy in range(3):
            hs = {c for c in cand if (c[0] + ox) % 3 != 2 and (c[1] + oy) % 3 != 2}
            hs = {c for c in hs if any((c[0] + dx, c[1] + dy) in hs for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
            if len(hs) > len(best):
                best = hs
    return tuple(sorted(best))


FORT = _fortress()
FORT_ARMY = tuple(
    RaiderSpawn(x, y) for x, y in ((10.0, 3.5), (16.0, 3.0), (22.0, 3.5), (13.0, 5.5), (19.0, 5.5), (7.0, 5.0), (25.0, 5.0))
)

FESTUNG = Scenario(
    key="festung", name="Verteidigung: Festung",
    hint="Ein Heer aus Hopliten, Peltasten und Reitern rückt an. Drei Tore, Türme an den Ecken; "
         "Peltasten über die Leitern auf den Wehrgang. Zwei Finger verschieben die Karte.",
    role="verteidigung", enemy_kind="armee", enemy_default=150, enemy_min=40, enemy_max=300,
    houses=FORT["houses"], palisade=FORT["palisade"], gate_closed=True, wall_side="stadt",
    ladders=FORT["ladders"], raider_spawns=FORT_ARMY, deploy_y=FORT_CENTRE[1] + 1.5, agora=FORT_CENTRE,
    cols=FORT_COLS, rows=FORT_ROWS, gates=FORT["gates"], corner_towers=FORT["towers"], ring=FORT["poly"],
)

FESTUNG_ANGRIFF = Scenario(
    key="festung_angriff", name="Angriff: Festung",
    hint="Die Festung hält drei Tore und sechs Türme. Baue Rammbock oder Turm und tippe dann Tor oder Wall an. "
         "Zwei Finger verschieben die Karte.",
    role="angriff", enemy_kind="spiegel", enemy_default=40, enemy_min=20, enemy_max=150,
    houses=FORT["houses"], palisade=FORT["palisade"], gate_closed=True, wall_side="feind",
    ladders=FORT["ladders"], deploy_y=FORT_ROWS - 3.0, ram_available=True, agora=FORT_CENTRE,
    cols=FORT_COLS, rows=FORT_ROWS, gates=FORT["gates"], corner_towers=FORT["towers"], ring=FORT["poly"],
)

# ------------------------------------------------------- offene Siedlung
# Die Stadt der Festung ohne Wall: dieselben Häuser, Gassen und die Agora, offen nach allen Seiten.
TOWN_HOUSES = FORT["houses"]
TOWN_TOP = min(c[1] for c in TOWN_HOUSES)              # nördlichste Häuserreihe
TOWN_BOTTOM = max(c[1] for c in TOWN_HOUSES) + 1       # Südkante der südlichsten Häuser

RAIDS_TOWN = (
    RaiderSpawn(9.0, -1.0), RaiderSpawn(13.0, -2.0), RaiderSpawn(17.0, -1.0), RaiderSpawn(21.0, -2.0),
    RaiderSpawn(25.0, -1.0), RaiderSpawn(15.0, -3.5),
    RaiderSpawn(1.2, -1.0, waypoints=((1.4, 22.0),)), RaiderSpawn(30.8, -1.0, waypoints=((30.6, 22.0),)),
    RaiderSpawn(11.0, -5.0), RaiderSpawn(19.0, -5.0), RaiderSpawn(6.0, -6.5), RaiderSpawn(24.0, -6.5),
)

OFFENE_SIEDLUNG = Scenario(
    key="siedlung", name="Verteidigung: Offene Siedlung",
    hint="Räuber von Norden, zwei Trupps umgehen die Linie. Tippe eine Gruppe an, dann ziehe ihre Front auf. "
         "Zwei Finger verschieben die Karte.",
    role="verteidigung", enemy_kind="raeuber", enemy_default=128, enemy_min=32, enemy_max=300,
    houses=TOWN_HOUSES, raider_spawns=RAIDS_TOWN, agora=FORT_CENTRE, deploy_y=TOWN_TOP - 2.0,
    cols=FORT_COLS, rows=FORT_ROWS,
)

SIEDLUNG_ANGRIFF = Scenario(
    key="siedlung_angriff", name="Angriff: Offene Siedlung",
    hint="Die Siedlung stellt dieselben Truppen wie du. Ihre Reiter greifen an, der Rest hält. "
         "Zwei Finger verschieben die Karte.",
    role="angriff", enemy_kind="spiegel", enemy_default=75, enemy_min=20, enemy_max=150,
    houses=TOWN_HOUSES, deploy_y=FORT_ROWS - 2.0, enemy_deploy_y=TOWN_BOTTOM + 1.5, agora=FORT_CENTRE,
    cols=FORT_COLS, rows=FORT_ROWS,
)

# Die Horde lagert im Norden einer Karte so groß wie die Festung
HORDE = tuple(
    RaiderSpawn(2.0 * x, 2.0 * y)
    for x, y in ((4.0, 3.5), (6.5, 2.5), (9.5, 2.5), (12.0, 3.5), (5.0, 5.0), (8.0, 4.5), (11.0, 5.0),
                 (3.0, 1.5), (13.0, 1.5), (7.0, 0.8), (9.5, 6.3), (6.0, 6.3))
)

RAEUBERHORDE = Scenario(
    key="horde", name="Angriff: Räuberhorde",
    hint="Die Horde lagert im Norden. Sie greift an, sobald du ihr nahe kommst. Zwei Finger verschieben die Karte.",
    role="angriff", enemy_kind="raeuber", enemy_default=96, enemy_min=16, enemy_max=300,
    raider_spawns=HORDE, deploy_y=FORT_ROWS - 2.5, cols=FORT_COLS, rows=FORT_ROWS,
)

SCENARIOS: tuple[Scenario, ...] = (OFFENE_SIEDLUNG, SIEDLUNG_ANGRIFF, RAEUBERHORDE, FESTUNG, FESTUNG_ANGRIFF)
