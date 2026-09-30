"""Die Kampfsimulation. Kennt kein Pygame.

Grundsätze aus dem Apoikia-Konzept:
- Gerechnet wird je Gruppe (Lochos), nie je Mann. Männer sind Reihen.
- Die Phalanx ist stark von vorn, verwundbar in Flanke und Rücken.
- Freier Angriff löst die Formation: schneller, aber ohne Bonus.
- Der Spieler schickt Gruppen einzeln, lässt sie angreifen oder zieht
  ihre Front mit einer Linie auf.

Rollen: Bei der Verteidigung plündern Räuber die Siedlung im Süden. Beim
Angriff steht der Gegner im Norden, hinter einem Wall mit verschlossenem
Tor, das nur ein Rammbock öffnet. Reine Peltastengruppen der Wallseite
dürfen auf den Wehrgang.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from . import config
from .ai import Memory, make_brain
from .army import Army, arm_of, default_army, scaled_army, split_by_arm
from .doctrine import DOCTRINE_NAMES, choose_doctrine, enemy_army
from .geometry import add, arc, dist, norm, scale, snap4, sub
from .scenarios import Scenario
from .units import UNIT_TYPES, Lochos, Man, Side, Stance, arrange, default_width

Point = tuple[float, float]
RAIDER_GROUP = 16


@dataclass
class House:
    cx: int
    cy: int
    progress: float = 0.0
    looted: bool = False

    @property
    def center(self) -> Point:
        return (self.cx + 0.5, self.cy + 0.5)


@dataclass
class Gate:
    cells: list[tuple[int, int]]
    closed: bool
    hp: float = config.GATE_HP
    hp_max: float = config.GATE_HP

    @property
    def center(self) -> Point:
        return (sum(c[0] for c in self.cells) / len(self.cells) + 0.5, self.cells[0][1] + 0.5)

    @property
    def broken(self) -> bool:
        return self.hp <= 0


@dataclass
class Projectile:
    """Ein fliegender Speer, nur Anzeige und verzögerter Einschlag."""

    x: float
    y: float
    tx: float
    ty: float
    target_id: int
    dmg: float
    progress: float = 0.0
    total: float = 1.0
    target_man: Man | None = None

    @property
    def pos(self) -> Point:
        t = min(1.0, self.progress / self.total)
        return (self.x + (self.tx - self.x) * t, self.y + (self.ty - self.y) * t)


@dataclass
class LinePlan:
    """Geplante Aufstellung einer Gruppe entlang einer gezogenen Linie."""

    unit_id: int
    center: Point
    facing: Point
    width: int
    depth: int
    length: float


@dataclass
class Battle:
    scenario: Scenario
    rng: random.Random = field(default_factory=random.Random)
    army: Army = field(default_factory=default_army)
    enemy_count: int | None = None
    cols: int = config.COLS
    rows: int = config.ROWS
    houses: list[House] = field(default_factory=list)
    blocked: set[tuple[int, int]] = field(default_factory=set)
    gate: Gate | None = None
    lochoi: list[Lochos] = field(default_factory=list)
    time: float = 0.0
    alarm: bool = True
    outcome: str | None = None
    line: list[LinePlan] = field(default_factory=list)
    projectiles: list[Projectile] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    men_start: dict[Side, int] = field(default_factory=dict)
    crossings: set[tuple[int, int]] = field(default_factory=set)   # überwundene Wallstücke
    ladders: set[tuple[int, int]] = field(default_factory=set)
    debris: list[tuple[float, float, float, float]] = field(default_factory=list)  # liegen gelassene Rammböcke
    towers: list[tuple[float, float]] = field(default_factory=list)                # am Wall stehende Türme
    horses: list[tuple[float, float, int]] = field(default_factory=list)           # zurückgelassene Pferde
    climb_budget: dict[tuple[int, int], float] = field(default_factory=dict)       # Durchsatz je Leiter/Turm
    _barrier_cache: dict = field(default_factory=dict)
    enemy_ram_id: int | None = None      # Räubergruppe, die den Rammbock baut
    horde_awake: bool = False
    ai: str = config.AI_DEFAULT          # "klug" oder "einfach"
    memory: Memory | None = None         # Gedächtnis der Gegner über Schlachten hinweg
    doctrine: str | None = None          # Aufstellung der Siedlung; None = passend zum Spieler wählen
    _next_id: int = 0

    # ------------------------------------------------------------ Aufbau
    def __post_init__(self) -> None:
        s = self.scenario
        if self.enemy_count is None:
            self.enemy_count = s.enemy_default
        self.houses = [House(cx, cy) for cx, cy in s.houses]
        self.blocked = set(s.palisade)
        self.ladders = set(s.ladders)
        if s.gate is not None:
            gx, gy = s.gate
            cells = [(gx, gy)]
            for step in (-1, 1):
                c = gx + step
                while 0 <= c < self.cols and (c, gy) not in self.blocked:
                    cells.append((c, gy))
                    c += step
            self.gate = Gate(sorted(cells), closed=s.gate_closed)
        self._deploy_army()
        if s.enemy_kind == "raeuber":
            self._spawn_raiders()
        else:
            self._spawn_mirror()
        self.men_start = {side: self.men(side) for side in Side}
        self.brain = make_brain(self.ai, self.memory)

    @property
    def enemy_plan(self) -> str:
        return self.brain.plan_name()

    @property
    def gate_center(self) -> Point | None:
        return self.gate.center if self.gate else None

    @property
    def attacking(self) -> bool:
        return self.scenario.role == "angriff"

    def _deploy_army(self) -> None:
        specs = [g for g in self.army.groups if g.men() > 0]
        if not specs:
            return
        rows_units = [arrange(spec.build_men(), default_width(spec.men())) for spec in specs]
        widths = [max(0.9, 2 * Lochos(0, Side.STADT, r, 0, 0).radius + 0.2) for r in rows_units]
        x = self.cols / 2 - sum(widths) / 2
        for spec, rows, w in zip(specs, rows_units, widths):
            self._spawn(Side.STADT, rows, min(max(x + w / 2, 0.6), self.cols - 0.6), self.scenario.deploy_y, spec.name)
            x += w

    def _spawn_raiders(self) -> None:
        """Räuber in Haufen, bei großer Zahl größere; etwa ein Fünftel Peltasten in der zweiten Reihe."""
        remaining = max(0, self.enemy_count)
        group_size = max(RAIDER_GROUP, min(32, round(self.enemy_count / 8)))
        spawns = list(self.scenario.raider_spawns)
        i = 0
        while remaining > 0 and spawns:
            n = min(group_size, remaining)
            if 0 < remaining - n < 8:
                n = remaining
            spawn = spawns[i % len(spawns)]
            extra = 2.5 * (i // len(spawns))          # weitere Wellen weiter außen
            y = spawn.y - extra if not self.attacking else spawn.y - extra * 0.4
            n_pelt = round(0.2 * n) if n >= 10 else 0
            men = [Man(UNIT_TYPES["raeuber"], tier=0) for _ in range(n - n_pelt)]
            men += [Man(UNIT_TYPES["peltast"], tier=1) for _ in range(n_pelt)]
            rows = arrange(men, math.ceil(n / 2))
            u = self._spawn(Side.FEIND, rows, spawn.x, y, "Räuber")
            u.waypoints = list(spawn.waypoints)
            if self.attacking:
                u.stance = Stance.HALTEN
                u.facing = (0.0, 1.0)
            remaining -= n
            i += 1

    def _spawn_mirror(self) -> None:
        """Die Siedlung stellt dieselbe Mischung wie der Spieler, skaliert."""
        self.doctrine = self.doctrine or choose_doctrine(self.army, self.memory)
        mirror = split_by_arm(enemy_army(self.army, self.enemy_count, self.doctrine))
        self.events.append(f"Die Siedlung stellt: {DOCTRINE_NAMES.get(self.doctrine, self.doctrine)}")
        s = self.scenario
        y_line = s.enemy_deploy_y
        hoplite_specs = [g for g in mirror.groups if g.men() and not all(t.kind in ("peltast", "reiter") for t in g.tiers)]
        pelt_specs = [g for g in mirror.groups if g.men() and all(t.kind == "peltast" for t in g.tiers)]
        cav_specs = [g for g in mirror.groups if g.men() and all(t.kind == "reiter" for t in g.tiers)]
        others = [g for g in mirror.groups if g.men() and g not in hoplite_specs + pelt_specs + cav_specs]

        def place(specs, y, x_from, x_to, facing=(0.0, 1.0), in_line=True, stance=Stance.PHALANX):
            if not specs:
                return
            rows_units = [arrange(g.build_men(), max(1, min(g.men(), int(3.0 / config.MAN_SPACING)))) for g in specs]
            widths = [2 * Lochos(0, Side.FEIND, r, 0, 0).half_w + 0.3 for r in rows_units]
            x = (x_from + x_to) / 2 - sum(widths) / 2
            for g, rows, w in zip(specs, rows_units, widths):
                u = self._spawn(Side.FEIND, rows, min(max(x + w / 2, 0.6), self.cols - 0.6), y, g.name)
                u.facing = facing
                u.stance = stance
                u.in_line = in_line
                x += w

        place(hoplite_specs + others, y_line, 3.0, 13.0)
        if s.palisade and s.gate:
            wall_y = s.gate[1] + 0.5
            for k, g in enumerate(pelt_specs):
                men = g.build_men()
                width = min(len(men), 14)
                rows = arrange(men, width)
                half = Lochos(0, Side.FEIND, rows, 0, 0).half_w
                x = (3.0 + half) if k % 2 == 0 else (13.0 - half)
                u = self._spawn(Side.FEIND, rows, x, wall_y, g.name)
                u.facing = (0.0, 1.0)
                u.stance = Stance.HALTEN
        else:
            place(pelt_specs, y_line - 1.0, 4.0, 12.0, stance=Stance.HALTEN, in_line=False)
        for k, g in enumerate(cav_specs):
            rows = arrange(g.build_men(), max(1, min(g.men(), 7)))
            x = 2.2 if k % 2 == 0 else self.cols - 2.2
            u = self._spawn(Side.FEIND, rows, x, y_line - 0.8, g.name)
            u.facing = (0.0, 1.0)
            u.stance = Stance.HALTEN

    def _spawn(self, side: Side, rows: list[list[Man]], x: float, y: float, name: str) -> Lochos:
        unit = Lochos(id=self._next_id, side=side, rows=rows, x=x, y=y, name=name)
        self._next_id += 1
        if side is Side.FEIND:
            unit.stance = Stance.RAUB
            unit.facing = (0.0, 1.0)
            unit.rout_threshold = 0.4 if self.scenario.enemy_kind == "raeuber" else 0.3
        self.lochoi.append(unit)
        return unit

    # ---------------------------------------------------------- Abfragen
    def units(self, side: Side, fighting_only: bool = False) -> list[Lochos]:
        return [u for u in self.lochoi if u.side is side and (u.fighting if fighting_only else u.alive)]

    def men(self, side: Side, fighting_only: bool = False) -> int:
        return sum(u.men for u in self.units(side, fighting_only))

    def by_id(self, uid: int) -> Lochos | None:
        for u in self.lochoi:
            if u.id == uid:
                return u
        return None

    def unit_at(self, p: Point, side: Side | None = None, tolerance: float = 0.35) -> Lochos | None:
        best, best_d = None, float("inf")
        for u in self.lochoi:
            if not u.alive or (side is not None and u.side is not side):
                continue
            d = u.surface_distance(p)
            if d <= tolerance and d < best_d:
                best, best_d = u, d
        return best

    def gate_at(self, p: Point, tolerance: float = 0.4) -> bool:
        if self.gate is None:
            return False
        gx, gy = self.gate.center
        half = len(self.gate.cells) / 2
        return abs(p[0] - gx) <= half + tolerance and abs(p[1] - gy) <= 0.5 + tolerance

    def houses_intact(self) -> int:
        return sum(1 for h in self.houses if not h.looted)

    def cell(self, x: float, y: float) -> tuple[int, int]:
        return (int(math.floor(x)), int(math.floor(y)))

    def is_wall_cell(self, c: tuple[int, int], walker: bool = False) -> bool:
        """Wallstück einschließlich Turmstellen. Für Wehrgang-Läufer zählt auch
        das geschlossene Torhaus dazu, sie laufen oben über das Tor hinweg.
        Ein aufgebrochenes Tor ist eine Lücke: unten Durchgang, oben Ende des Wehrgangs."""
        if c in self.blocked:
            return True
        return walker and self.gate is not None and self.gate.closed and c in self.gate.cells

    def is_walker(self, u: Lochos) -> bool:
        """Wer den Wehrgang betreten darf: reine Peltasten der Wallseite über
        die Leitern, Angreifer über einen aufgestellten Turm."""
        if u.side is self.wall_side():
            return u.wall_capable()
        return bool(self.crossings)

    def ladders_for(self, u: Lochos, pos: Point | None = None, target: Point | None = None) -> set[tuple[int, int]]:
        """Auf- und Abstiege: Leitern für alle Läufer; der Turm nur für Angreifer
        und nur zwischen Wehrgang und Außenseite."""
        outside_south = self.wall_side() is Side.FEIND
        ground = target if (pos is not None and self.is_wall_cell(self.cell(*pos), True)) else pos
        if ground is not None and self.is_wall_cell(self.cell(*ground), True):
            ground = None                          # Ziel oben: jeder Auf- oder Abstieg kommt in Frage
        out: set[tuple[int, int]] = set()
        for c in self.ladders:                     # Leitern stehen innen
            if ground is None or (ground[1] > c[1] + 0.5) != outside_south:
                out.add(c)
        if u.side is self.wall_side() or not self.crossings:
            return out
        for c in self.crossings:                   # der Turm steht außen
            if ground is None or (ground[1] > c[1] + 0.5) == outside_south:
                out.add(c)
        return out

    def ladder_ok(self, wall_cell: tuple[int, int], ground_cell: tuple[int, int]) -> bool:
        """Leitern führen nur zur Innenseite des Walls."""
        outside_south = self.wall_side() is Side.FEIND
        return (ground_cell[1] > wall_cell[1]) != outside_south

    def on_wall(self, u: Lochos) -> bool:
        return self.is_wall_cell(self.cell(u.x, u.y), self.is_walker(u))

    def can_step(self, u: Lochos, a: Point, b: Point) -> bool:
        """Ein Schritt ist erlaubt, wenn das Ziel frei ist und der Wehrgang
        nur über eine Leiter (oder einen Turm) betreten oder verlassen wird."""
        walker = self.is_walker(u)
        ca = self.cell(*a)
        if self.is_blocked(b[0], b[1], u, from_wall=self.is_wall_cell(ca, walker)):
            return False
        cb = self.cell(*b)
        wa, wb = self.is_wall_cell(ca, walker), self.is_wall_cell(cb, walker)
        if wa == wb:
            return True
        wall_cell, ground_cell = (ca, cb) if wa else (cb, ca)
        if wall_cell in self.ladders and self.ladder_ok(wall_cell, ground_cell):
            return True
        if wall_cell in self.crossings and u.side is not self.wall_side():
            # Turm: nur an der Außenseite des Walls (dort steht er)
            outside_south = self.wall_side() is Side.FEIND
            return (ground_cell[1] > wall_cell[1]) == outside_south
        return False

    def wall_connected(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        """Liegen zwei Wallstücke auf demselben Wehrgang ohne Lücke (offenes Tor) dazwischen?"""
        if a[1] != b[1]:
            return False
        lo, hi = sorted((a[0], b[0]))
        return all(self.is_wall_cell((x, a[1]), True) for x in range(lo, hi + 1))

    def nearest_ladder(self, u: Lochos, p: Point, target: Point) -> Point | None:
        """Der Auf- oder Abstieg, der auf dem Weg liegt: steht man oben, einer, der von
        hier aus über den Wehrgang erreichbar ist; will man hinauf, einer, von dem aus
        das Ziel oben erreichbar ist."""
        ladders = self.ladders_for(u, p, target)
        here, there = self.cell(*p), self.cell(*target)
        if self.is_wall_cell(here, True):
            ladders = {c for c in ladders if self.wall_connected(c, here)}
            if not ladders:
                # kein Abstieg zur Zielseite auf diesem Wallstück: irgendwo hinunter, unten weiter
                ladders = {c for c in set(self.ladders) | self.crossings if self.wall_connected(c, here)}
        elif self.is_wall_cell(there, True):
            ladders = {c for c in ladders if self.wall_connected(c, there)}
        if not ladders:
            return None
        best = min(ladders, key=lambda c: dist(p, (c[0] + 0.5, c[1] + 0.5)) + dist((c[0] + 0.5, c[1] + 0.5), target))
        return (best[0] + 0.5, best[1] + 0.5)

    def _inner_dir(self) -> float:
        """Richtung (y) von der Palisade zur Innenseite, wo die Leitern stehen."""
        return 1.0 if self.wall_side() is Side.STADT else -1.0

    def wall_side(self) -> Side | None:
        return {"stadt": Side.STADT, "feind": Side.FEIND, None: None}[self.scenario.wall_side]

    def is_blocked(self, x: float, y: float, unit: Lochos | None = None, from_wall: bool | None = None) -> bool:
        c = self.cell(x, y)
        walker = unit is not None and self.is_walker(unit)
        if c in self.blocked:
            return not walker
        if self.gate is not None and c in self.gate.cells:
            if from_wall is None:
                from_wall = unit is not None and self.on_wall(unit)
            if walker and from_wall:
                return False          # oben über das Torhaus
            return self.gate.closed
        return False

    def inside(self, x: float, y: float) -> bool:
        return 0.0 <= x < self.cols and 0.0 <= y < self.rows

    def path_clear(self, a: Point, b: Point, unit: Lochos | None = None) -> bool:
        d = dist(a, b)
        n = max(1, int(d / 0.25))
        for i in range(1, n + 1):
            t = i / n
            if self.is_blocked(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, unit):
                return False
        return True

    def route(self, u: Lochos, target: Point) -> tuple[Point, bool]:
        """Nächster Zielpunkt der Gruppe und ob es schon das eigentliche Ziel ist."""
        return self.route_from(u, u.pos, target)

    def route_from(self, u: Lochos, pos: Point, target: Point) -> tuple[Point, bool]:
        """Wie ``route``, aber von einer beliebigen Position aus (auch für einzelne Männer)."""
        walker = self.is_walker(u) and bool(self.ladders_for(u))
        if walker:
            on = self.is_wall_cell(self.cell(*pos), True)
            want = self.is_wall_cell(self.cell(*target), True)
            if on and want and not self.wall_connected(self.cell(*pos), self.cell(*target)):
                want = False          # Lücke im Wehrgang: erst hinunter, unten weiter, drüben wieder hinauf
            if on != want:
                ladder = self.nearest_ladder(u, pos, target)
                if ladder is not None and self.cell(*ladder) != self.cell(*pos):
                    if not on:
                        # unten: erst an den Fuß der Leiter, notfalls seitlich, nie schräg an die Palisade
                        lc = self.cell(*ladder)
                        side = self._inner_dir() if lc in self.ladders else -self._inner_dir()
                        foot = (ladder[0], ladder[1] + side)
                        under = abs(pos[0] - ladder[0]) <= 0.3 and (pos[1] - ladder[1]) * side > 0
                        if not under:
                            if self.path_clear(pos, foot, None):
                                return foot, False
                            wp = (ladder[0], pos[1])
                            if dist(pos, wp) > 0.1 and self.path_clear(pos, wp, None):
                                return wp, False
                    return ladder, False
                if ladder is not None and on:
                    # auf der Leiter: gerade hinunter (Leitern innen, der Turm außen), dann weiter
                    down = self._inner_dir() if self.cell(*ladder) in self.ladders else -self._inner_dir()
                    return (ladder[0], ladder[1] + down), False
                return target, True
            if on and want:
                return target, True
        # am Boden auf derselben Seite: erst seitlich, dann zum Ziel, nicht schräg in die Palisade
        if self.blocked and not self.path_clear(pos, target, None):
            here, there = self._wall_level(pos), self._wall_level(target)
            if here != "wall" and (there == here or there == "wall"):
                wp = (target[0], pos[1])
                if self.path_clear(pos, wp, None) and dist(pos, wp) > 0.1:
                    return wp, False
        # am Boden: Palisade ist für alle eine Sperre, Übergang nur durchs Tor oder über Leiter/Turm
        if self.gate is None and not self.blocked:
            return target, True
        if self.path_clear(pos, target, None):
            return target, True
        if self.gate is not None and not self.gate.closed:
            gx, gy = self.gate.center
            if self.cell(*pos) in self.gate.cells:
                above = target[1] > gy         # im Durchgang: auf die Zielseite weiter
            else:
                above = pos[1] < gy
            beyond = (gx, gy + 1.2) if above else (gx, gy - 1.2)
            if self.path_clear(pos, beyond, None):
                return beyond, False
            return ((gx, gy - 1.2) if above else (gx, gy + 1.2)), False
        if walker:
            ladder = self.nearest_ladder(u, pos, target)   # nächster Aufstieg Richtung Ziel
            if ladder is not None:
                return ladder, False
        if self.gate is not None:
            gx, gy = self.gate.center
            above = pos[1] < gy
            spread = ((u.id % 5) - 2) * 1.3
            far = config.ENEMY_RALLY_DISTANCE + 0.6 * ((u.id // 5) % 3)
            wait = (gx + spread, gy - far) if above else (gx + spread, gy + far)
            return self._free_spot(wait, u), False
        return target, True

    def throw_clear(self, a: Lochos, b: Lochos) -> bool:
        """Über die Palisade oder ein geschlossenes Tor wirft nur, wer auf dem Wehrgang steht."""
        if self.on_wall(a):
            return True
        target_cell = self.cell(b.x, b.y)
        d = dist(a.pos, b.pos)
        n = max(1, int(d / 0.25))
        for i in range(1, n + 1):
            t = i / n
            c = self.cell(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)
            if c == target_cell:
                continue
            if c in self.blocked:
                return False
            if self.gate is not None and self.gate.closed and c in self.gate.cells:
                return False
        return True

    def _nearest(self, unit: Lochos, candidates: list[Lochos]) -> tuple[Lochos | None, float]:
        best, best_d = None, float("inf")
        for c in candidates:
            d = dist(unit.pos, c.pos)
            if d < best_d:
                best, best_d = c, d
        return best, best_d

    def _gap(self, a: Lochos, b: Lochos) -> float:
        if a.loose or b.loose:
            men_a, men_b = a.all_men(), b.all_men()
            if men_a and men_b:
                return max(0.0, min(dist(m.pos, n.pos) for m in men_a for n in men_b) - 0.2)
        return max(0.0, min(a.rect_distance(b.pos) - b.core, b.rect_distance(a.pos) - a.core))

    def _in_contact(self, a: Lochos, b: Lochos) -> bool:
        """Ob ``a`` gegen ``b`` kämpft. Der Wehrgang ist erhöht: von unten kommt
        niemand an die Männer oben heran, von oben schlägt man hinunter."""
        if self._gap(a, b) > config.ENGAGE_RANGE:
            return False
        up_a, up_b = self.on_wall(a), self.on_wall(b)
        if up_b and not up_a:
            return False
        if up_a or up_b:
            return True
        return self.path_clear(a.pos, b.pos)

    # ----------------------------------------------------------- Befehle
    def _selection(self, units: list[Lochos] | None) -> list[Lochos]:
        pool = self.units(Side.STADT, fighting_only=True)
        if not units:
            return pool
        ids = {u.id for u in units}
        return [u for u in pool if u.id in ids]

    def _wake(self, u: Lochos) -> None:
        if u.building is not None:
            self.events.append(f"{u.name}: Bau abgebrochen")
        u.building = None
        u.build_kind = None
        u.tower_cell = None
        u.tower_progress = 0.0

    def command_move(self, units: list[Lochos] | None, point: Point) -> None:
        self.alarm = False
        sel = self._selection(units)
        px = min(max(point[0], 0.5), self.cols - 0.5)
        py = min(max(point[1], 0.5), self.rows - 0.5)
        n = len(sel)
        for i, u in enumerate(sel):
            self._wake(u)
            off = (i - (n - 1) / 2) * 1.2
            u.stance = Stance.HALTEN
            u.mode = ""
            u.in_line = False
            u.target_id = None
            u.target = self._free_spot((px + off, py), u)
        self.events.append(f"{len(sel)} Gruppe(n) unterwegs")

    def command_attack_target(self, units: list[Lochos] | None, enemy: Lochos) -> None:
        self.alarm = False
        for u in self._selection(units):
            self._wake(u)
            u.stance = Stance.ANGRIFF
            u.mode = ""
            u.in_line = False
            u.target_id = enemy.id
            u.target = enemy.pos
        self.events.append(f"Angriff auf {enemy.name} ({enemy.men} Mann)")

    ARM_NAMES = {"hopliten": "Hopliten", "peltasten": "Peltasten", "reiter": "Reiter"}

    def mixed(self, u: Lochos) -> bool:
        return len({arm_of(m.kind.key) for m in u.all_men()}) > 1

    def split_group(self, u: Lochos) -> list[Lochos]:
        """Eine gemischte Gruppe nach Waffengattung teilen. Die Männer bleiben
        stehen und laufen zu den Plätzen ihrer neuen Gruppe; die größte Gattung
        behält Nummer und Gruppe, die anderen werden neue Gruppen."""
        if u.loose or self.on_wall(u) or u.engine is not None or u.building is not None:
            return [u]
        parts: dict[str, list[Man]] = {}
        for m in u.all_men():
            parts.setdefault(arm_of(m.kind.key), []).append(m)
        if len(parts) < 2:
            return [u]
        pos = {id(m): (m.x, m.y) for m in u.all_men()}
        width = max(1, u.width)
        biggest = max(parts, key=lambda k: len(parts[k]))
        out = []
        for arm, men in parts.items():
            rows = arrange(men, min(width, len(men)))
            cx = sum(m.x for m in men) / len(men)
            cy = sum(m.y for m in men) / len(men)
            if arm == biggest:
                g = u
                g.rows = rows
                g.x, g.y = cx, cy
            else:
                g = self._spawn(u.side, rows, cx, cy, self.ARM_NAMES[arm])
                g.facing = u.facing
                g.morale = u.morale
                g.rout_threshold = u.rout_threshold
            g.name = self.ARM_NAMES[arm]
            g.formation = "linie"
            g.file = False
            g.in_line = False
            g.men_start = g.men
            g.target = None
            g.target_id = None
            g.waypoints = []
            g.mode = ""
            for m in men:
                m.x, m.y = pos[id(m)]
            out.append(g)
        self.events.append("Aufgeteilt: " + ", ".join(f"{g.name} {g.men}" for g in out))
        return out

    def command_merge(self, units: list[Lochos] | None) -> Lochos | None:
        """Mehrere Gruppen zu einer vereinen: die Männer bleiben stehen und
        laufen zu den Plätzen der neuen Linie; die größte Gruppe bleibt bestehen."""
        sel = [u for u in self._selection(units)
               if not u.loose and not self.on_wall(u) and u.engine is None and u.building is None]
        if len(sel) < 2:
            return None
        keep = max(sel, key=lambda u: (u.men, -u.id))
        others = [u for u in sel if u is not keep]
        men = [m for u in sel for m in u.all_men()]
        pos = {id(m): (m.x, m.y) for m in men}
        total = len(men)
        morale = sum(u.morale * u.men for u in sel) / total
        keep.rows = arrange(men, max(u.width for u in sel))
        keep.x = sum(m.x for m in men) / total
        keep.y = sum(m.y for m in men) / total
        keep.stance = Stance.HALTEN
        keep.formation = "linie"
        keep.in_line = False
        keep.mode = ""
        keep.target = None
        keep.target_id = None
        keep.waypoints = []
        keep.men_start = keep.men
        keep.morale = morale
        if self.mixed(keep):
            keep.name = "Gemischt"
        for m in men:
            m.x, m.y = pos[id(m)]
        for u in others:
            u.rows = []
        self.lochoi = [u for u in self.lochoi if u not in others]
        self.events.append(f"Vereint: {keep.name} mit {keep.men} Mann")
        return keep

    def command_attack(self, units: list[Lochos] | None = None) -> list[Lochos]:
        """Freier Angriff, je Waffengattung: Hopliten stürmen den nächsten Gegner,
        Peltasten plänkeln (auf Wurfweite heran, werfen, ausweichen), Reiter
        suchen sich Flanke, Rücken oder ungeordnete Gegner, stoßen zu und
        setzen sich wieder ab. Gemischte Gruppen teilen sich dafür nach
        Gattung, so dass jede in ihrem eigenen Tempo losgeht."""
        self.alarm = False
        out: list[Lochos] = []
        for u in self._selection(units):
            for g in self.split_group(u):
                self._wake(g)
                arm = g.arm()
                g.in_line = False
                g.target_id = None
                g.target = None
                g.mode = ""
                if arm == "peltasten" and g.ammo() > 0:
                    g.stance = Stance.PLAENKELN
                else:
                    g.stance = Stance.ANGRIFF
                    if arm == "reiter" and g.mounted_men():
                        g.mode = "sturm"
                        g.hitrun_until = -1.0
                out.append(g)
        self.events.append("Freier Angriff")
        return out

    def command_hold(self, units: list[Lochos] | None = None) -> None:
        """Halten: Hopliten bilden an Ort und Stelle eine Phalanx (Front wie sie
        stehen), andere Gruppen bleiben stehen."""
        self.alarm = False
        for u in self._selection(units):
            self._wake(u)
            u.mode = ""
            u.in_line = False
            u.target_id = None
            if u.arm() == "hopliten" and not self.on_wall(u):
                u.stance = Stance.PHALANX
                u.target = u.pos
            else:
                u.stance = Stance.HALTEN
                u.target = None
        self.events.append("Halten")

    def command_formation(self, units: list[Lochos] | None, name: str) -> int:
        """Formation der gewählten Gruppen setzen, wenn ihre Waffengattung sie kennt."""
        changed = 0
        for u in self._selection(units):
            if name in u.formation_options() and u.formation != name:
                u.formation = name
                u.in_line = False
                changed += 1
        if changed:
            from .units import FORMATION_NAMES
            self.events.append(f"Formation: {FORMATION_NAMES.get(name, name)}")
        return changed

    def command_build(self, units: list[Lochos] | None, kind: str) -> int:
        """Gewählte Gruppen bauen je ein Belagerungsgerät ("ram" oder "tower")."""
        if not self.scenario.ram_available or kind not in ("ram", "tower"):
            return 0
        started = 0
        for u in self._selection(units):
            if u.engine is not None or u.building is not None:
                continue
            self.alarm = False
            u.stance = Stance.HALTEN
            u.in_line = False
            u.target = None
            u.target_id = None
            u.building = 0.0
            u.build_kind = kind
            started += 1
            self._dismount(u)
            self.events.append(f"{u.name} baut {'den Rammbock' if kind == 'ram' else 'den Belagerungsturm'}")
        return started

    def command_drop(self, units: list[Lochos] | None, kind: str) -> int:
        """Gewählte Gruppen legen ihr Gerät ab oder brechen dessen Bau ab."""
        dropped = 0
        for u in self._selection(units):
            if u.build_kind == kind and u.building is not None:
                self._wake(u)
                dropped += 1
            elif u.engine == kind:
                fx, fy = u.facing
                if kind == "ram":
                    self.debris.append((u.x + fx * (u.half_d + 0.3), u.y + fy * (u.half_d + 0.3), fx, fy))
                else:
                    self.towers.append((u.x + fx * (u.half_d + 0.5), u.y + fy * (u.half_d + 0.5)))
                u.engine = None
                u.tower_cell = None
                dropped += 1
                self.events.append(f"{u.name} lassen {'den Rammbock' if kind == 'ram' else 'den Turm'} liegen")
        return dropped

    def _dismount(self, u: Lochos) -> None:
        n = u.dismount()
        if n:
            self.horses.append((u.x, u.y, n))
            self.events.append(f"{u.name} sitzen ab, {n} Pferde bleiben zurück")

    def command_ram_gate(self, units: list[Lochos] | None) -> int:
        """Gruppen mit Rammbock gehen ans Tor und brechen es auf."""
        if self.gate is None or not self.gate.closed:
            return 0
        sel = [u for u in self._selection(units) if u.engine == "ram"]
        if not sel:
            self.events.append("Ohne Rammbock hält das Tor")
            return 0
        self.alarm = False
        gx, gy = self.gate.center
        for i, u in enumerate(sel):
            side = 1.0 if u.y > gy else -1.0
            u.stance = Stance.HALTEN
            u.in_line = False
            u.target_id = None
            u.target = (gx + (i - (len(sel) - 1) / 2) * 0.8, gy + side * (0.5 + u.half_d + 0.35))
            u.facing = (0.0, -side)
        self.events.append("Rammbock geht ans Tor")
        return len(sel)

    def command_tower_wall(self, units: list[Lochos] | None, cell: tuple[int, int]) -> int:
        """Gruppen mit Turm setzen ihn an dieses Wallstück."""
        if cell not in self.blocked or cell in self.crossings:
            return 0
        sel = [u for u in self._selection(units) if u.engine == "tower"]
        if not sel:
            self.events.append("Ohne Belagerungsturm ist der Wall zu hoch")
            return 0
        self.alarm = False
        cx, cy = cell[0] + 0.5, cell[1] + 0.5
        for u in sel:
            side = 1.0 if u.y > cy else -1.0
            u.stance = Stance.HALTEN
            u.in_line = False
            u.target_id = None
            u.tower_cell = cell
            u.tower_progress = 0.0
            u.target = (cx, cy + side * (0.5 + u.half_d + 0.3))
            u.facing = (0.0, -side)
        self.events.append("Belagerungsturm rollt an den Wall")
        return len(sel)

    def plan_line(self, units: list[Lochos] | None, start: Point, end: Point) -> list[LinePlan]:
        sel = self._selection(units)
        if not sel:
            return []
        d = sub(end, start)
        length = dist(start, end)
        if length < 0.3:
            return []
        axis = norm(d)
        facing = (axis[1], -axis[0])
        total_men = sum(u.men for u in sel)
        sel = sorted(sel, key=lambda u: u.x * axis[0] + u.y * axis[1])
        plans: list[LinePlan] = []
        pos = 0.0
        gap = 0.25
        usable = max(0.3, length - gap * (len(sel) - 1))
        for u in sel:
            seg = usable * u.men / total_men
            width = max(1, min(u.men, int(seg / config.MAN_SPACING)))
            depth = math.ceil(u.men / width)
            center = add(start, scale(axis, pos + seg / 2))
            plans.append(LinePlan(u.id, self._free_spot(center, u), facing, width, depth, seg))
            pos += seg + gap
        return plans

    def command_line(self, units: list[Lochos] | None, start: Point, end: Point) -> list[LinePlan]:
        self.alarm = False
        plans = self.plan_line(units, start, end)
        for plan in plans:
            u = self.by_id(plan.unit_id)
            if u is None:
                continue
            self._wake(u)
            u.formation = "linie"
            u.mode = ""
            u.reform(plan.width)
            u.stance = Stance.PHALANX
            u.in_line = False
            u.facing = plan.facing
            u.target = plan.center
            u.target_id = None
            u.waypoints = []
        self.line = plans
        if plans:
            self.events.append(f"Aufstellung: {len(plans)} Gruppe(n), Front {self._dir_name(snap4(plans[0].facing))}")
        return plans

    def _free_spot(self, p: Point, unit: Lochos | None = None) -> Point:
        x = min(max(p[0], 0.5), self.cols - 0.5)
        y = min(max(p[1], 0.5), self.rows - 0.5)
        if self.is_blocked(x, y, unit):
            for dy in (1.0, -1.0, 2.0, -2.0):
                if not self.is_blocked(x, y + dy, unit) and self.inside(x, y + dy):
                    return (x, y + dy)
        return (x, y)

    @staticmethod
    def _dir_name(v: Point) -> str:
        return {(0.0, -1.0): "Nord", (0.0, 1.0): "Süd", (-1.0, 0.0): "West", (1.0, 0.0): "Ost"}.get(v, "?")

    # ------------------------------------------------------------ Update
    def update(self, dt: float) -> None:
        if self.outcome is not None or self.alarm or dt <= 0:
            return
        self.time += dt
        if self.attacking:
            self._ai_defenders()
        else:
            self._ai_raiders()
        self._ai_city()
        self._skirmishers()
        self._move(dt)
        self._separate()
        self._combat(dt)
        self._volleys(dt)
        self._engines(dt)
        if not self.attacking:
            self._loot(dt)
        self._morale(dt)
        self._check_withdraw()
        self._check_outcome()

    # -- KI ----------------------------------------------------------------
    def _ai_raiders(self) -> None:
        self.brain.think(self)

    def _raider_ram_unit(self) -> Lochos | None:
        """Solange das Tor zu ist, baut eine Räubergruppe den Rammbock."""
        if self.gate is None or not self.gate.closed:
            return None
        u = self.by_id(self.enemy_ram_id) if self.enemy_ram_id is not None else None
        if u is not None and u.fighting:
            return u
        candidates = [r for r in self.units(Side.FEIND, fighting_only=True) if not self.on_wall(r)]
        if not candidates:
            self.enemy_ram_id = None
            return None
        gx, gy = self.gate.center
        u = min(candidates, key=lambda r: dist(r.pos, (gx, gy)))
        self.enemy_ram_id = u.id
        u.waypoints = []
        return u

    def _drive_raider_ram(self, u: Lochos) -> None:
        gx, gy = self.gate.center
        rally = (gx, gy - config.ENEMY_RALLY_DISTANCE)
        u.stance = Stance.HALTEN
        u.target_id = None
        if u.engine == "ram":
            u.target = (gx, gy - (0.5 + u.half_d + 0.35))
            u.facing = (0.0, 1.0)
            return
        if u.building is not None:
            u.target = None
            return
        if dist(u.pos, rally) > 0.6:
            u.target = rally
            return
        u.building = 0.0
        u.build_kind = "ram"
        self.events.append("Die Räuber bauen einen Rammbock")

    def _ai_defenders(self) -> None:
        self.brain.think(self)

    def _ai_city(self) -> None:
        foes = self.units(Side.FEIND)
        fighting = [f for f in foes if f.fighting]
        for u in self.units(Side.STADT, fighting_only=True):
            if u.stance is not Stance.ANGRIFF:
                continue
            if u.mode == "sturm":
                self._hit_and_run(u, fighting or foes)
                continue
            target = self.by_id(u.target_id) if u.target_id is not None else None
            if target is None or not target.alive or not self.inside(target.x, target.y):
                target, _ = self._nearest(u, fighting or foes)
                u.target_id = target.id if target else None
            u.target = target.pos if target else None
        for u in self.units(Side.STADT):
            if u.stance is Stance.FLUCHT:
                u.target = (u.x, self.rows + 3.0)

    def _skirmishers(self) -> None:
        """Plänkelnde Gruppen beider Seiten (Spieler wie KI) führt die Schlacht
        selbst: auf Wurfweite heran, werfen, vor dem Nahkampf ausweichen."""
        for side, other in ((Side.STADT, Side.FEIND), (Side.FEIND, Side.STADT)):
            skirmishers = [u for u in self.units(side, fighting_only=True) if u.stance is Stance.PLAENKELN]
            if not skirmishers:
                continue
            foes = self.units(other)
            fighting = [f for f in foes if f.fighting]
            for u in skirmishers:
                self._skirmish(u, fighting or foes)

    def _skirmish(self, u: Lochos, foes: list[Lochos]) -> None:
        """Plänkeln: auf Wurfweite an den nächsten Gegner heran, werfen, und
        zurückweichen, wenn er näher kommt."""
        foe, _ = self._nearest(u, [f for f in foes if self._reachable_level(u, f)] or foes)
        if foe is None:
            u.target = None
            return
        u.target_id = foe.id
        d = foe.rect_distance(u.pos)
        away = norm(sub(u.pos, foe.pos))
        if self._gap(u, foe) < config.SKIRMISH_NEAR:       # Lücke zwischen den Formationen, wie beim Handgemenge
            u.target = self._free_spot((u.x + away[0] * 1.5, u.y + away[1] * 1.5), u)
        elif d > config.JAVELIN_RANGE - config.SKIRMISH_FAR:
            own = [o for o in self.units(u.side, fighting_only=True)
                   if o is not u and self._formed(o) and self.on_wall(o) == self.on_wall(u)]
            wall = next((o for o in own if self._formation_in_the_way(u, foe, [foe, o])), None)
            if wall is None:
                u.target = foe.pos
            elif d <= config.JAVELIN_RANGE:
                u.target = None                            # hinter der eigenen Phalanx: über die Köpfe werfen
            else:
                back = norm(sub(wall.pos, foe.pos))        # dicht hinter die eigene Phalanx rücken ...
                keep = wall.half_d + u.half_d + 0.1
                spot = (wall.x + back[0] * keep, wall.y + back[1] * keep)
                if foe.rect_distance(spot) > config.JAVELIN_RANGE - 0.1:
                    along, _ = wall.local(u.pos)          # ... oder um ihr Ende herum, wenn es dort nicht reicht
                    side = 1.0 if along >= 0 else -1.0
                    fx, fy = wall.facing
                    out = side * (wall.half_w + u.half_w + 0.4)
                    spot = (wall.x - fy * out, wall.y + fx * out)
                u.target = self._free_spot(spot, u)
        else:
            u.target = None                                # stehen und werfen

    def _reachable_level(self, u: Lochos, f: Lochos) -> bool:
        return self.on_wall(u) == self.on_wall(f) or self.on_wall(u)

    def charge_target(self, u: Lochos, foes: list[Lochos]) -> Lochos | None:
        """Lohnendstes Ziel für einen Reiterstoß: ungeordnete oder fliehende
        Gruppen, sonst Flanke oder Rücken einer Phalanx; die Front zuletzt."""
        best, best_s = None, 0.0
        for f in foes:
            if not self._reachable_level(u, f):
                continue
            if self._formation_in_the_way(u, f, foes):
                continue                                   # der Weg führt durch eine andere Phalanx
            if f.stance is Stance.FLUCHT:
                v = 1.6
            elif not self._formed(f):
                v = 1.5
            else:
                v = {"front": 0.3, "flank": 1.2, "rear": 1.4}[self.arc_of(f, u.pos)]
            s = v / (1.0 + f.rect_distance(u.pos) / 3.0)
            if s > best_s:
                best, best_s = f, s
        return best

    def _formation_in_the_way(self, u: Lochos, f: Lochos, foes: list[Lochos]) -> bool:
        others = [e for e in foes if e is not f and self._formed(e)]
        if not others:
            return False
        d = dist(u.pos, f.pos)
        n = max(2, int(d / 0.3))
        for i in range(1, n):
            t = i / n
            p = (u.x + (f.x - u.x) * t, u.y + (f.y - u.y) * t)
            if any(e.rect_distance(p) <= 0.4 for e in others):
                return True
        return False

    def _hit_and_run(self, u: Lochos, foes: list[Lochos]) -> None:
        """Reiter im freien Angriff: Stoß mit Anlauf in Flanke oder Rücken, nach dem
        Aufprall auf eine stehende Phalanx absetzen und neu anlaufen."""
        if u.hitrun_until > self.time:
            return                                          # setzt gerade ab
        if u.hitrun_until >= 0 and u.target is not None and dist(u.pos, u.target) > 0.4:
            return                                          # noch auf dem Weg zum Absetzpunkt
        u.hitrun_until = -1.0
        foe = self.by_id(u.target_id) if u.target_id is not None else None
        if foe is None or not foe.fighting or self._formed(foe) and self.arc_of(foe, u.pos) == "front" and not u.engaged:
            foe = self.charge_target(u, foes)
        if foe is None:
            u.target = None
            return
        u.target_id = foe.id
        if u.engaged and u.charge_slow_until > self.time - 0.5 and foe.stance is not Stance.FLUCHT and not foe.loose:
            # gerade aufgeprallt: lösen und neuen Anlauf nehmen, statt im Handgemenge zu bleiben
            away = norm(sub(u.pos, foe.pos))
            u.target = self._free_spot((u.x + away[0] * config.HITRUN_DISTANCE, u.y + away[1] * config.HITRUN_DISTANCE), u)
            u.hitrun_until = self.time + config.HITRUN_TIME
            return
        if self._formed(foe) and self.arc_of(foe, u.pos) == "front":
            from .ai import flank_route
            wp = flank_route(self, u, foe)
            if wp is not None:
                u.target = wp
                return
        u.target = foe.pos

    # -- Bewegung ----------------------------------------------------------
    def _move(self, dt: float) -> None:
        for u in self.lochoi:
            if u.alive:
                self._update_loose(u)
                self._try_remount(u)
            if not u.alive or u.target is None or u.in_phalanx or u.building is not None:
                if u.alive and u.vel > 0.0:
                    self._coast(u, dt)                  # Reiter laufen aus statt auf der Stelle zu stehen
                continue
            speed = u.speed * (1.25 if u.stance is Stance.FLUCHT else 1.0)
            if u.engaged and u.stance is not Stance.FLUCHT:
                speed *= config.ENGAGED_SPEED           # im Handgemenge kommt man kaum vom Fleck
            if u.charge_slow_until > self.time:
                speed *= config.CHARGE_SLOW             # der Aufprall hat die Reiter gebremst
            goal, final = self.route(u, u.target)
            d = dist(u.pos, goal)
            if u.mounted_men() and self.is_wall_cell(self.cell(*goal), True) and d <= 1.0:
                self._dismount(u)   # vor Leiter oder Turm wird abgesessen
            stop_at = 0.0
            if u.stance is Stance.ANGRIFF and final:
                target = self.by_id(u.target_id) if u.target_id is not None else None
                withdrawing = u.hitrun_until > self.time                 # Reiter setzen ab: nicht am Feind kleben
                if target is not None and not withdrawing and self._gap(u, target) <= config.ENGAGE_RANGE * 0.8:
                    if self._rides(u) and u.vel > 0.05 and u.ride_in < config.CHARGE_PENETRATION:
                        u.vel = max(0.0, u.vel - config.CHARGE_BRAKE * dt)   # der Schwung trägt in den Feind hinein
                        step = u.vel * dt
                        self._step(u, scale(u.heading, step))
                        u.ride_in += step
                    else:
                        u.vel = 0.0
                    continue
                u.ride_in = 0.0
                stop_at = 0.0 if target is not None else config.ENGAGE_RANGE
            if u.stance is Stance.FLUCHT and u.loose and not any(self.inside(m.x, m.y) for m in u.all_men()):
                u.withdrawn = True            # die Männer sind schon vom Feld
                continue
            if u.loose and self._lost_touch(u):
                continue                      # das Zentrum ist zu seinen Männern gesprungen
            if d <= max(config.ARRIVE_EPS, stop_at):
                u.vel = 0.0
                if u.stance is Stance.PHALANX and final and d <= config.ARRIVE_EPS + 0.02:
                    u.x, u.y = u.target
                    u.in_line = u.on_slots(config.SLOT_TOLERANCE, config.SLOT_SHARE) and all(
                        dist(m.pos, p) <= config.SLOT_TOLERANCE for m, p in u.slots() if m.bound
                    )                                                   # erst wenn (fast) alle stehen, die Gebundenen sicher
                elif u.stance in (Stance.HALTEN, Stance.PLAENKELN) and final:
                    u.target = None
                continue
            if u.loose and u.stance is not Stance.FLUCHT and self._stragglers(u, u.target):
                continue                      # die Gruppe wartet auf die Männer, die noch klettern
            before = u.pos
            if self._rides(u):
                self._ride(u, dt, goal, speed, d)
            else:
                u.vel = 0.0
                step = min(speed * dt, d)
                direction = norm(sub(goal, u.pos))
                if u.stance is not Stance.PHALANX:
                    u.facing = direction
                self._step(u, scale(direction, step))
            if u.stance is Stance.ANGRIFF and not u.engaged:
                u.runup += dist(before, u.pos)          # Anlauf für den Sturmangriff
            else:
                u.runup = 0.0
            if u.stance is Stance.FLUCHT and not self.inside(u.x, u.y):
                u.withdrawn = True
        self._move_men(dt)

    def _rides(self, u: Lochos) -> bool:
        """Beritten und im Gelände unterwegs: Bewegung mit Schwung."""
        return bool(u.mounted_men()) and not u.loose and not self.on_wall(u) and u.engine is None

    def _ride(self, u: Lochos, dt: float, goal: Point, top: float, d: float) -> None:
        """Reiter haben Schwung: Sie fahren an, bremsen vor dem Ziel ab und wenden in
        Bögen, deren Halbmesser mit dem Tempo wächst; im Stand drehen sie frei."""
        want = norm(sub(goal, u.pos))
        ang = 0.0
        if u.vel <= 0.05 or u.heading == (0.0, 0.0):
            head = want
        else:
            head = u.heading
            ang = math.atan2(head[0] * want[1] - head[1] * want[0], head[0] * want[0] + head[1] * want[1])
            omega = config.CAVALRY_TURN_RATE / max(1.0, u.vel)
            ang = max(-omega * dt, min(omega * dt, ang))
            c, s_ = math.cos(ang), math.sin(ang)
            head = (head[0] * c - head[1] * s_, head[0] * s_ + head[1] * c)
        want_v = min(top, math.sqrt(2.0 * config.CAVALRY_BRAKE * d), 3.0 * d + 0.05)   # Bremsweg, zuletzt weich auslaufen
        if u.vel < want_v:
            u.vel = min(want_v, u.vel + config.CAVALRY_ACCEL * dt)
        else:
            u.vel = max(want_v, u.vel - config.CAVALRY_BRAKE * dt)
        u.heading = head
        if u.stance is not Stance.PHALANX:
            u.facing = head
        step = u.vel * dt
        if abs(ang) < 1e-3 and dist(head, want) < 1e-3:
            step = min(step, d)
        self._step(u, scale(head, step))

    def _coast(self, u: Lochos, dt: float) -> None:
        """Ohne Ziel: Reiter bremsen ab und rollen dabei noch aus."""
        if not self._rides(u):
            u.vel = 0.0
            return
        u.vel = max(0.0, u.vel - config.CAVALRY_BRAKE * dt)
        if u.vel > 0.0:
            self._step(u, scale(u.heading, u.vel * dt))

    def _lost_touch(self, u: Lochos) -> bool:
        """Aufgelöste Formation: Hat das Zentrum keinen Mann mehr in der Nähe, springt
        es zu dem Mann, der dem Ziel am nächsten ist; die Männer sind die Gruppe."""
        men = u.all_men()
        if not men or any(dist(m.pos, u.pos) <= config.FOLLOW_LAG for m in men):
            return False
        goal = u.target if u.target is not None else u.pos
        lead = min(men, key=lambda m: dist(m.pos, goal))
        u.x, u.y = lead.x, lead.y
        return True

    def _stragglers(self, u: Lochos, destination: Point) -> bool:
        """Aufgelöste Formation: Ist ein Mann deutlich weiter vom Ziel entfernt als
        das Zentrum, wartet die Gruppe auf ihn (Leitern lassen nur einen nach dem anderen durch)."""
        lead = dist(u.pos, destination)
        return any(self._behind(u, m, destination, lead) for m in u.all_men())

    def _behind(self, u: Lochos, m: Man, destination: Point, lead: float) -> bool:
        """Ein Mann ist zurück, wenn er auf einer Wallseite steht, die weder die des
        Zentrums noch die des Ziels ist, noch oben ist, während das Zentrum schon
        drüben steht, oder auf derselben Seite weit hinter dem Zentrum liegt."""
        man_level, centre_level, dest_level = self._wall_level(m.pos), self._wall_level(u.pos), self._wall_level(destination)
        if man_level == centre_level:
            return dist(m.pos, destination) > lead + config.FOLLOW_LAG
        if man_level == "tor":
            return False                       # im Durchgang: er kommt
        if man_level == "wall":
            return centre_level == dest_level
        return man_level != dest_level

    def _wall_level(self, p: Point) -> str:
        """"nord", "sued", "wall" oder "tor": auf welcher Seite der Palisade ein Punkt
        liegt; das offene Tor ist der Durchgang dazwischen."""
        c = self.cell(*p)
        if self.is_wall_cell(c, True):
            return "wall"
        if self.gate is not None and c in self.gate.cells:
            return "tor"
        if not self.blocked:
            return "sued"
        wall_y = next(iter(self.blocked))[1]
        return "sued" if c[1] > wall_y else "nord"

    def _update_loose(self, u: Lochos) -> None:
        """Beim Überqueren der Palisade löst sich die Formation auf: sobald der
        Weg über Turm oder Leiter führt oder noch ein Mann oben ist."""
        if not self.is_walker(u):
            u.loose = False
            return
        center_up = self.on_wall(u)
        on_route = False
        if u.target is not None:
            goal, _ = self.route(u, u.target)
            goal_up = self.is_wall_cell(self.cell(*goal), True)
            target_up = self.is_wall_cell(self.cell(*u.target), True)
            on_route = (goal_up and not target_up) or (center_up and not target_up)
        centre_level = self._wall_level(u.pos)
        split = any(self._wall_level(m.pos) != centre_level for m in u.all_men())
        was = u.loose
        # aufgelöst, solange der Weg über den Wall führt oder Männer und Zentrum nicht
        # auf derselben Seite stehen; wer oben steht und bleibt, ist nicht aufgelöst
        u.loose = on_route or split
        if u.loose and not was:
            u.in_line = False
            if u.stance is Stance.PHALANX:
                u.stance = Stance.HALTEN
            self.events.append(f"{u.name}: Formation aufgelöst, Mann für Mann über den Wall")
        elif was and not u.loose:
            self.events.append(f"{u.name}: Formation neu gebildet")

    def _try_remount(self, u: Lochos) -> None:
        """Abgesessene Reiter ohne Gerät steigen bei ihren Pferden wieder auf."""
        if u.engine is not None or u.building is not None or u.loose:
            return
        if not any(m.kind.cavalry and not m.mounted for m in u.all_men()):
            return
        for i, (hx, hy, n) in enumerate(self.horses):
            if dist(u.pos, (hx, hy)) <= 0.9:
                taken = u.remount(n)
                if taken:
                    rest = n - taken
                    if rest > 0:
                        self.horses[i] = (hx, hy, rest)
                    else:
                        del self.horses[i]
                    self.events.append(f"{u.name} sitzen auf ({taken} Pferde)")
                return

    def _move_men(self, dt: float) -> None:
        """Jeder Mann läuft zu seinem Platz in der Formation, weicht aber einzeln
        aus: durchs Tor nur durch die Öffnung, auf den Wall nur über Leiter oder Turm.
        Bei aufgelöster Formation folgt jeder Mann dem Weg der Gruppe für sich."""
        for c in self.climb_budget:
            self.climb_budget[c] = min(1.0, self.climb_budget[c] + config.CLIMB_RATE * dt)
        self._barrier_cache = {side: [e for e in self.lochoi if e.side is not side and e.fighting and not e.loose]
                               for side in Side}
        for u in self.lochoi:
            if not u.alive:
                continue
            walker = self.is_walker(u)
            u.file = self.on_wall(u)
            self._bind_men(u)
            if u.loose:
                destination = u.target if u.target is not None else u.pos
                lead = dist(u.pos, destination)
                centre_level = self._wall_level(u.pos)
                dest_level = self._wall_level(destination)
                # jeder Mann geht an seinen Platz in der Aufstellung am Ziel, nicht auf einen Punkt
                dest_slots = {id(m): p for m, p in u.slots_at(destination, u.facing, dest_level == "wall")}
                goals: list[tuple[Man, Point]] = []
                for man in u.all_men():
                    slot = dest_slots.get(id(man), destination)
                    if dist(man.pos, slot) <= 0.05:
                        continue
                    man_level = self._wall_level(man.pos)
                    if man_level not in (centre_level, dest_level, "wall", "tor"):
                        # falsche Wallseite: dem Zentrum nach, denselben Weg über Turm oder Leiter
                        goal = self.nearest_ladder(u, man.pos, u.pos)
                        if goal is None:
                            goal, _ = self.route_from(u, man.pos, u.pos)
                    elif man_level == centre_level and dist(man.pos, destination) > lead + config.FOLLOW_LAG:
                        goal, _ = self.route_from(u, man.pos, u.pos)
                    else:
                        goal, _ = self.route_from(u, man.pos, slot)
                    goals.append((man, goal))
                # vor einer Leiter anstellen: wer näher ist, steht weiter vorn
                ranks: dict[int, int] = {}
                for cell in {self.cell(*g) for _, g in goals}:
                    if cell in self.ladders or cell in self.crossings:
                        waiting = sorted((m for m, g in goals if self.cell(*g) == cell), key=lambda m: dist(m.pos, (cell[0] + 0.5, cell[1] + 0.5)))
                        for rank, m in enumerate(waiting):
                            ranks[id(m)] = rank
                for man, goal in goals:
                    if man.bound and dist(goal, man.stand or man.pos) > config.BOUND_SHUFFLE:
                        continue
                    goal = self._queue_spot(goal, man, ranks.get(id(man), 0))
                    speed = max(u.speed, man.speed) * config.MAN_CATCHUP
                    self._man_step(u, man, goal, speed * dt, walker)
                continue
            for man, slot in u.slots():
                d = dist(man.pos, slot)
                if man.bound and dist(slot, man.stand or man.pos) > config.BOUND_SHUFFLE:
                    continue                          # steht im Handgemenge fest, rückt höchstens etwas nach
                if d <= 0.02:
                    if self._man_can_step(u, man, man.pos, slot, walker):
                        man.x, man.y = slot
                    continue
                speed = max(u.speed, man.speed) * config.MAN_CATCHUP
                if not self._man_step(u, man, slot, speed * dt, walker, slide=False):
                    goal, _ = self.route_from(u, man.pos, slot)     # Umweg (Tor), statt an der Palisade zu kriechen
                    self._man_step(u, man, goal, speed * dt, walker)

    def _bind_men(self, u: Lochos) -> None:
        """Wer einen Gegner in Reichweite hat, steht im Handgemenge fest. Zieht die
        Gruppe weiter als die Leine, reißt er sich los, und die Gruppe ist eine
        Weile verwundbar (Lösen kostet)."""
        up = self.on_wall(u)
        foes = [e for e in self.lochoi if e.side is not u.side and e.fighting and self.on_wall(e) == up
                and dist(e.pos, u.pos) <= e.radius + u.radius + config.MAN_BIND_REACH + 1.0]
        if not foes or u.stance is Stance.FLUCHT:
            for m in u.all_men():
                m.bound = False
            return
        released = False
        slot_of = {id(m): p for m, p in u.slots()}
        for m in u.all_men():
            nearest = min(e.surface_distance(m.pos) for e in foes)
            if m.bound:
                if nearest > 2 * config.MAN_BIND_REACH:
                    m.bound = False               # der Gegner ist weg
                    m.anchor = None
                elif m.anchor is not None and dist(u.pos, m.anchor) > config.BOUND_LEASH:
                    m.bound = False               # die Gruppe ist weitergezogen: er reißt sich los
                    m.anchor = None
                    released = True
                continue
            if nearest <= config.MAN_BIND_REACH and dist(m.pos, slot_of.get(id(m), m.pos)) <= config.BOUND_LEASH:
                m.bound = True                    # wer seinem Platz gerade hinterherläuft, wird nicht neu gebunden
                m.anchor = u.pos                  # ein Drehen an Ort und Stelle löst ihn nicht
                m.stand = m.pos
        if released:
            mounted = u.mounted_men()
            span = config.DISENGAGE_TIME_MOUNTED if len(mounted) >= u.men / 2 else config.DISENGAGE_TIME
            u.disengage_until = max(u.disengage_until, self.time + span)

    def _queue_spot(self, goal: Point, man: Man, i: int) -> Point:
        """Führt der Weg an eine besetzte Leiter, stellt sich der Mann davor an,
        statt sich mit allen anderen auf denselben Punkt zu stellen."""
        cell = self.cell(*goal)
        if self._wall_level(man.pos) == "wall" or (cell not in self.ladders and cell not in self.crossings):
            return goal
        if i == 0 or (self.climb_budget.get(cell, 1.0) >= 1.0 and dist(man.pos, goal) < 0.9):
            return goal
        side = 1.0 if man.y > cell[1] + 0.5 else -1.0
        return (cell[0] + 0.5 + ((i % 6) - 2.5) * 0.14, cell[1] + 0.5 + side * (0.75 + (i // 6) * 0.15))

    def _man_step(self, u: Lochos, man: Man, goal: Point, step: float, walker: bool, slide: bool = True) -> bool:
        d = dist(man.pos, goal)
        if d < 1e-6:
            return True
        step = min(step, d)
        dx, dy = (goal[0] - man.x) / d * step, (goal[1] - man.y) / d * step
        options = ((man.x + dx, man.y + dy), (man.x + dx, man.y), (man.x, man.y + dy)) if slide else ((man.x + dx, man.y + dy),)
        for nx, ny in options:
            if (nx, ny) == (man.x, man.y):
                continue
            if self._man_can_step(u, man, (man.x, man.y), (nx, ny), walker):
                man.x, man.y = nx, ny
                return True
        return False

    def _man_can_step(self, u: Lochos, man: Man, a: Point, b: Point, walker: bool) -> bool:
        ca, cb = self.cell(*a), self.cell(*b)
        wa = self.is_wall_cell(ca, walker)
        if self.is_blocked(b[0], b[1], u, from_wall=wa):
            return False
        if self.inside(*a) and not self.inside(*b) and u.stance is not Stance.FLUCHT:
            return False                      # der Kartenrand ist keine Umgehung
        if self._walled_off(u, a, b, self._barrier_cache.get(u.side, [])):
            return False
        wb = self.is_wall_cell(cb, walker)
        if wa == wb:
            return True
        if man.kind.cavalry and man.mounted:
            return False                      # beritten geht es weder hinauf noch hinunter
        wall_cell, ground_cell = (ca, cb) if wa else (cb, ca)
        if wall_cell in self.ladders and self.ladder_ok(wall_cell, ground_cell):
            return self._climb(wall_cell)
        if wall_cell in self.crossings and u.side is not self.wall_side():
            outside_south = self.wall_side() is Side.FEIND
            return (ground_cell[1] > wall_cell[1]) == outside_south and self._climb(wall_cell)
        return False

    def _climb(self, cell: tuple[int, int]) -> bool:
        """Leiter oder Turm lassen nur einen Mann nach dem anderen durch."""
        budget = self.climb_budget.get(cell, 1.0)
        if budget < 1.0:
            self.climb_budget[cell] = budget
            return False
        self.climb_budget[cell] = budget - 1.0
        return True

    def _barriers(self, u: Lochos) -> list[Lochos]:
        """Feindliche Gruppen in Formation, durch die niemand hindurchläuft."""
        return [e for e in self.lochoi if e.side is not u.side and e.fighting and not e.loose]

    def _walled_off(self, u: Lochos, a: Point, b: Point, barriers: list[Lochos]) -> bool:
        """Führt der Schritt in eine feindliche Formation hinein?"""
        for e in barriers:
            if dist(e.pos, b) > e.radius + 0.3:
                continue
            if e.rect_distance(b) <= config.BARRIER_MARGIN < e.rect_distance(a):
                return True
        return False

    def _step(self, u: Lochos, delta: Point) -> None:
        nx, ny = u.x + delta[0], u.y + delta[1]
        if self._walled_off(u, u.pos, (nx, ny), self._barriers(u)):
            return
        if self.can_step(u, u.pos, (nx, ny)):
            u.x, u.y = nx, ny
        elif self.can_step(u, u.pos, (nx, u.y)):
            u.x = nx
        elif self.can_step(u, u.pos, (u.x, ny)):
            u.y = ny

    def _separate(self) -> None:
        alive = [u for u in self.lochoi if u.alive]
        for i, a in enumerate(alive):
            for b in alive[i + 1:]:
                if a.side is b.side and (a.stance is not Stance.HALTEN or b.stance is not Stance.HALTEN):
                    continue          # eigene Gruppen in Bewegung ziehen aneinander vorbei
                if a.loose or b.loose or self.on_wall(a) != self.on_wall(b):
                    continue          # aufgelöste Gruppen: die Männer weichen selbst aus
                if b.id in a.contacts or a.id in b.contacts:
                    continue          # im Handgemenge drückt man sich nicht auseinander
                d = dist(a.pos, b.pos)
                if d < 1e-6:
                    continue
                overlap = config.SEPARATION - self._gap(a, b)
                if overlap <= 0:
                    continue
                push = overlap / 2
                direction = norm(sub(b.pos, a.pos))
                if not a.in_phalanx and a.building is None:
                    self._step(a, scale(direction, -push))
                if not b.in_phalanx and b.building is None:
                    self._step(b, scale(direction, push))

    # -- Kampf -------------------------------------------------------------
    def _combat(self, dt: float) -> None:
        alive = [u for u in self.lochoi if u.alive]
        previous = {u.id: set(u.contacts) for u in alive}
        for u in alive:
            u.engaged = False
            u.contacts = []
        pairs: list[tuple[Lochos, Lochos]] = []
        for a in alive:
            if not a.fighting:
                continue
            for b in alive:
                if b.side is a.side:
                    continue
                if self._in_contact(a, b):
                    pairs.append((a, b))
                    a.engaged = True
                    a.contacts.append(b.id)
                    if b.id not in previous.get(a.id, ()) and a.runup >= config.CHARGE_RUNUP and not a.loose:
                        self._charge(a, b)                # erster Kontakt mit Anlauf: Aufprall
        hits = [(a, b, *self._melee(a, b, dt)) for a, b in pairs]
        for a, b, dmg, arc_name in hits:
            self._apply_damage(a, b, dmg, arc_name)

    def _charge(self, a: Lochos, b: Lochos) -> None:
        """Sturmangriff: Reiter mit Anlauf prallen auf eine Gruppe. In die Front einer
        Phalanx rennen sie in die Speere; sonst stoßen sie einzelne Männer weg
        (leichte weiter als schwere), verletzen sie und erschüttern die Moral.
        Der Aufprall bremst die Reiter selbst."""
        a.runup = 0.0
        a.charge_slow_until = self.time + config.CHARGE_SLOW_TIME
        riders = a.mounted_men()
        mounted = bool(riders)
        strikers = riders if mounted else (a.rows[0] if a.rows else [])
        factor = 1.0 if mounted else config.CHARGE_FOOT
        if a.formation == "keil":
            factor *= config.CHARGE_WEDGE
        arc_name = self.arc_of(b, a.pos)
        if self._formed(b) and arc_name == "front" and b.shield_factor() > 0 and b.rows:
            if not mounted:
                return                                     # Fußvolk läuft nur ins Handgemenge
            spears = sum(1 for m in b.rows[0] if m.kind.hoplite)
            dmg = min(spears * config.CHARGE_IMPALE, len(riders) * config.CHARGE_IMPALE_CAP)
            for m in sorted(riders, key=lambda m: b.rect_distance(m.pos)):   # die vordersten Reiter voll
                q = min(dmg, m.hp)
                m.hp -= q
                dmg -= q
                if dmg <= 0:
                    break
            fallen = a.bury()
            a.morale -= fallen * (1.0 / max(1, a.men_start)) * a.bravery()
            self.events.append(f"{a.name} ({a.side.value}) rennen in die Speere von {b.name}")
            return
        direction = norm(sub(b.pos, a.pos))
        reach = self._gap(a, b) + config.CHARGE_REACH      # die vordersten Männer, auf die die Reiter treffen
        zone = [m for m in b.all_men() if a.rect_distance(m.pos) <= reach]
        zone.sort(key=lambda m: a.rect_distance(m.pos))
        hit_count = max(1, (len(strikers) // 2 if a.formation == "keil" else 2 * len(strikers)))
        zone = zone[:hit_count]
        if not zone:
            return
        for m in zone:
            weight = max(0.5, m.kind.hp)
            push = config.CHARGE_PUSH * factor / weight
            nx, ny = m.x + direction[0] * push, m.y + direction[1] * push
            if self.inside(nx, ny) and not self.is_blocked(nx, ny, b) and not self.is_wall_cell(self.cell(nx, ny), True):
                m.x, m.y = nx, ny                         # weggestoßen
            m.hp -= config.CHARGE_IMPACT * factor / weight
        fallen = b.bury()
        b.in_line = False                                  # die Ordnung ist dahin, bis alle wieder stehen
        shock = config.CHARGE_SHOCK * factor * (1.5 if arc_name == "rear" else 1.0) * b.bravery()
        b.morale -= shock
        self._after_hit(b, fallen, arc_name, config.CHARGE_IMPACT * factor * len(zone))
        where = {"front": "in die Front", "flank": "in die Flanke", "rear": "in den Rücken"}[arc_name]
        verb = "stoßen" if mounted else "stürmen"
        self.events.append(f"{a.name} ({a.side.value}) {verb} {where} von {b.name}: {len(zone)} Mann geworfen")

    def _melee(self, a: Lochos, b: Lochos, dt: float) -> tuple[float, str]:
        rate, arc_name = self._melee_rate(a, b)
        return rate * dt, arc_name

    def _formed(self, u: Lochos) -> bool:
        """Phalanxbonus nur unten in der Formation, nie auf dem Wehrgang."""
        return u.in_phalanx and not self.on_wall(u)

    def _defense_mod(self, a: Lochos, b: Lochos) -> tuple[float, str]:
        arc_name = self.arc_of(b, a.pos)
        mod = 1.0
        if b.disengage_until > self.time:
            # gerade aus dem Handgemenge gelöst: der Gegner hackt in den Rücken
            mod = config.DISENGAGE_DAMAGE * (config.ROUTED_DAMAGE if b.stance is Stance.FLUCHT else 1.0)
            return mod, "rear"
        if self._formed(b):
            shield = b.shield_factor()
            if arc_name == "front":
                front = {"u": config.PHALANX_FRONT_U, "o": config.PHALANX_FRONT_O}.get(b.formation, config.PHALANX_FRONT)
                mod = 1.0 + (front - 1.0) * shield
            elif arc_name == "rear":
                mod = config.PHALANX_REAR
            support = max(config.PHALANX_SUPPORT_MIN, 1.0 - config.PHALANX_SUPPORT * self._line_neighbours(b))
            mod *= support
        if b.stance is Stance.FLUCHT:
            mod *= config.ROUTED_DAMAGE
        return mod, arc_name

    def _present(self, u: Lochos, foe: Lochos) -> list[Man]:
        """Aufgelöste Formation: nur die Männer nahe am Gegner kämpfen."""
        reach = config.ENGAGE_RANGE + 0.4
        return [m for m in u.all_men() if foe.surface_distance(m.pos) <= reach]

    def arc_of(self, u: Lochos, p: Point) -> str:
        """Front, Flanke oder Rücken aus Sicht der Formation; neben dem Ende der
        Front zählt es noch als Front, wenn dort ein Nachbar in der Linie steht."""
        a = u.arc_to(p)
        if a != "flank" or not self._formed(u):
            return a
        along, forward = u.local(p)
        if forward < -u.half_d:
            return a
        for o in self.lochoi:
            if o is u or o.side is not u.side or not o.in_phalanx or self._gap(u, o) > config.LINE_SEAM:
                continue
            o_along, _ = u.local(o.pos)
            if (o_along > 0) == (along > 0):
                return "front"                  # die Linie geht dort weiter
        return a

    def _side_men(self, u: Lochos, arc_name: str) -> int:
        """Wie viele Männer einer Formation können sich zur Flanke oder nach hinten wehren."""
        if arc_name == "rear":
            return len(u.rows[-1]) if u.rows else 0
        return min(u.men, config.FLANK_FILE * u.depth)

    def _melee_rate(self, a: Lochos, b: Lochos) -> tuple[float, str]:
        base = a.melee_attack() * config.BASE_RATE
        if a.loose and a.men:
            base *= len(self._present(a, b)) / a.men
        attack_mod = 1.0
        if self._formed(a):
            own_arc = self.arc_of(a, b.pos)
            if own_arc == "front":
                attack_mod = config.PHALANX_ATTACK_FRONT if a.formation in ("linie", "u") else 1.0
            else:
                # in Formation wehren sich nur die Männer am Rand, wo der Gegner steht
                per_man = a.melee_attack() / max(1, len(a.rows[0]))
                base = min(base, self._side_men(a, own_arc) * per_man * config.BASE_RATE)
        defense_mod, arc_name = self._defense_mod(a, b)
        cav = a.cavalry_share()
        if cav > 0:
            if self._formed(b) and arc_name == "front":
                cav_mod = config.CAVALRY_VS_FRONT * b.shield_factor() + (1 - b.shield_factor())
            elif not b.in_phalanx:
                cav_mod = config.CAVALRY_CHARGE
            else:
                cav_mod = 1.0
            attack_mod *= (1 - cav) + cav * cav_mod
        if self.on_wall(a) != self.on_wall(b):
            attack_mod *= config.WALL_MELEE_FACTOR
        return base * attack_mod * defense_mod, arc_name

    def _line_neighbours(self, u: Lochos) -> int:
        return sum(
            1 for o in self.lochoi
            if o is not u and o.side is u.side and o.in_phalanx and self._gap(u, o) <= 0.5
        )

    def _apply_damage(self, a: Lochos, b: Lochos, dmg: float, arc_name: str) -> None:
        if not b.alive or dmg <= 0:
            return
        row_arc = arc_name if arc_name != "ranged" else "front"
        b.last_arc = arc_name
        if b.loose:
            near = self._present(b, a)
            if not near:
                return
            fallen = b.take_damage_men(near, dmg, self.rng)
        elif self._formed(b) and row_arc in ("flank", "rear"):
            # Flanke und Rücken: es trifft die Männer am Rand, nicht die ganze Reihe
            near = sorted(b.all_men(), key=lambda m: dist(m.pos, a.pos))[:self._side_men(b, row_arc) + 2]
            fallen = b.take_damage_men(near, dmg, self.rng)
        else:
            fallen = b.take_damage(b.exposed_row(row_arc), dmg, self.rng)
        self._after_hit(b, fallen, arc_name, dmg)

    def _after_hit(self, b: Lochos, fallen: int, arc_name: str, dmg: float) -> None:
        if fallen:
            morale_mod = {"rear": 1.5, "flank": 1.2}.get(arc_name, 1.0)
            if b.in_phalanx and arc_name == "front":
                morale_mod = config.MORALE_LOSS_FRONT_PHALANX
            b.morale -= fallen * (config.MORALE_SCALE / max(1, b.men_start)) * b.bravery() * morale_mod
        if b.in_phalanx and arc_name == "rear":
            b.morale -= config.MORALE_REAR_DRAIN * b.bravery() * dmg
        if b.men <= 0:
            b.in_line = False
            self.events.append(f"{b.name} ({b.side.value}) aufgerieben")
            self._lose_engine(b)

    def _volleys(self, dt: float) -> None:
        alive = [u for u in self.lochoi if u.alive]
        for a in alive:
            if not a.fighting:
                continue
            a.volley_timer = max(0.0, a.volley_timer - dt)
            throwers = a.throwers(a.engaged)
            if not throwers:
                if (a.ammo() == 0 and a.share(lambda m: m.kind.ranged) >= 0.5
                        and a.stance in (Stance.HALTEN, Stance.PHALANX, Stance.PLAENKELN) and not self.on_wall(a)
                        and (a.side is Side.STADT or self.scenario.enemy_kind == "raeuber")):
                    a.stance = Stance.ANGRIFF
                    a.in_line = False
                    a.target_id = None
                    self.events.append(f"{a.name}: Speere verschossen, Nahkampf")
                continue
            if a.volley_timer > 0:
                continue
            reach = config.JAVELIN_RANGE + (config.WALL_RANGE_BONUS if self.on_wall(a) else 0.0)
            foes = [b for b in alive if b.side is not a.side and b.fighting
                    and b.rect_distance(a.pos) <= reach and self.throw_clear(a, b)]
            foe, d = self._nearest(a, foes)
            if foe is None:
                continue
            a.volley_timer = config.VOLLEY_INTERVAL
            shield = 1.0 - 0.5 * foe.shield_factor() if foe.in_phalanx else 1.0
            targets = foe.all_men()
            for m in throwers:
                m.ammo -= 1
                victim = targets[self.rng.randrange(len(targets))]
                flight = max(0.1, dist(m.pos, victim.pos) / config.JAVELIN_SPEED)
                self.projectiles.append(Projectile(
                    m.x, m.y, victim.x, victim.y, foe.id, config.JAVELIN_DAMAGE * shield, 0.0, flight, victim,
                ))
        for pr in list(self.projectiles):
            pr.progress += dt
            if pr.progress >= pr.total:
                self.projectiles.remove(pr)
                b = self.by_id(pr.target_id)
                if b is None or not b.alive or pr.target_man is None:
                    continue
                if pr.target_man.hp <= 0 or dist(pr.target_man.pos, (pr.tx, pr.ty)) > 0.35:
                    continue                                   # daneben: der Mann ist nicht mehr dort
                fallen = b.hit_man(pr.target_man, pr.dmg)
                self._after_hit(b, fallen, "ranged", pr.dmg)

    # -- Belagerung: Bau, Rammbock, Turm -----------------------------------
    def _engines(self, dt: float) -> None:
        for u in self.lochoi:
            if not u.fighting:
                continue
            if u.building is not None:
                u.building += dt
                needed = config.RAM_BUILD_TIME if u.build_kind == "ram" else config.TOWER_BUILD_TIME
                if u.building >= needed:
                    u.engine = u.build_kind
                    u.building = None
                    u.build_kind = None
                    what = "Der Rammbock" if u.engine == "ram" else "Der Belagerungsturm"
                    self.events.append(f"{what} von {u.name} ist fertig")
                continue
            if u.engine == "ram" and self.gate is not None and self.gate.closed:
                gx, gy = self.gate.center
                if abs(u.x - gx) <= len(self.gate.cells) / 2 + 0.3 and abs(abs(u.y - gy) - 0.5) <= u.half_d + config.RAM_REACH:
                    self.gate.hp -= config.RAM_DPS * dt
                    if self.gate.hp <= 0:
                        self.gate.hp = 0.0
                        self.gate.closed = False
                        self.events.append("Das Tor ist aufgebrochen!")
                        self._drop_rams()
            elif u.engine == "tower" and u.tower_cell is not None:
                cx, cy = u.tower_cell[0] + 0.5, u.tower_cell[1] + 0.5
                if abs(u.x - cx) <= 0.6 and abs(abs(u.y - cy) - 0.5) <= u.half_d + config.TOWER_REACH:
                    u.tower_progress += dt
                    if u.tower_progress >= config.TOWER_DEPLOY_TIME:
                        self.crossings.add(u.tower_cell)
                        self.events.append(f"{u.name} hat den Wall überwunden")
                        beyond_side = -1.0 if u.y > cy else 1.0
                        self.towers.append((cx, cy - beyond_side * 0.75))   # Turm bleibt am Wall stehen
                        u.engine = None
                        u.tower_cell = None
                        u.target = (cx, cy)                                  # hinauf auf den Wehrgang

    def _drop_rams(self) -> None:
        """Nach dem Durchbruch bleibt der Rammbock liegen, die Gruppen treten
        zur Seite, damit der Durchgang frei ist, und sind wieder schnell."""
        gx = self.gate.center[0] if self.gate else self.cols / 2
        for u in self.lochoi:
            if u.engine == "ram":
                fx, fy = u.facing
                self.debris.append((u.x + fx * (u.half_d + 0.3), u.y + fy * (u.half_d + 0.3), fx, fy))
                u.engine = None
                if self.enemy_ram_id == u.id:
                    self.enemy_ram_id = None
                if u.side is Side.STADT:
                    side = 1.0 if u.x >= gx else -1.0
                    u.stance = Stance.HALTEN
                    u.target = self._free_spot((gx + side * (u.half_w + 1.6), u.y), u)

    def _lose_engine(self, u: Lochos | None) -> None:
        if u is None:
            return
        if u.engine is not None or u.building is not None:
            self.events.append(f"{u.name}: Belagerungsgerät verloren")
        u.engine = None
        u.building = None
        u.build_kind = None
        u.tower_cell = None
        if self.enemy_ram_id == u.id:
            self.enemy_ram_id = None

    # -- Plündern ----------------------------------------------------------
    def _loot(self, dt: float) -> None:
        for u in self.units(Side.FEIND, fighting_only=True):
            if u.engaged:
                continue
            for h in self.houses:
                if h.looted or u.rect_distance(h.center) > config.LOOT_RANGE:
                    continue
                h.progress += dt
                if h.progress >= config.LOOT_TIME:
                    h.looted = True
                    self.events.append(f"Haus ({h.cx},{h.cy}) geplündert")
                break

    # -- Moral -------------------------------------------------------------
    def _hopeless(self, side: Side) -> bool:
        """Die Schlacht ist für eine Seite aussichtslos: sie hat den Großteil
        verloren, der Gegner steht noch weitgehend."""
        own_start = self.men_start.get(side, 0)
        foe = Side.FEIND if side is Side.STADT else Side.STADT
        foe_start = self.men_start.get(foe, 0)
        if not own_start or not foe_start:
            return False
        own = self.men(side, fighting_only=True) / own_start
        theirs = self.men(foe, fighting_only=True) / foe_start
        return own <= config.MORALE_HOPELESS_OWN and theirs >= config.MORALE_HOPELESS_FOE

    def _morale(self, dt: float) -> None:
        hopeless = {side: self._hopeless(side) for side in Side}
        broke: list[Lochos] = []
        for u in self.lochoi:
            if not u.alive or u.stance is Stance.FLUCHT:
                continue
            if not u.engaged:
                u.morale = min(1.0, u.morale + config.MORALE_REGEN * dt)
            if hopeless[u.side]:
                u.morale -= config.MORALE_HOPELESS_DRAIN * u.bravery() * dt
            if u.morale <= u.rout_threshold:
                u.stance = Stance.FLUCHT
                u.in_line = False
                u.target = None
                u.target_id = None
                self.events.append(f"{u.name} ({u.side.value}) flieht")
                self._lose_engine(u)
                broke.append(u)
        for u in broke:                                  # Ansteckung: wer Nachbarn fliehen sieht, wankt
            for o in self.lochoi:
                if o is not u and o.side is u.side and o.fighting and dist(o.pos, u.pos) <= config.MORALE_CONTAGION_RANGE:
                    o.morale -= config.MORALE_CONTAGION * o.bravery()

    def _check_withdraw(self) -> None:
        start = self.men_start.get(Side.FEIND, 0)
        if start and self.men(Side.FEIND, fighting_only=True) <= start * config.ENEMY_WITHDRAW_FRACTION:
            for u in self.units(Side.FEIND, fighting_only=True):
                u.stance = Stance.FLUCHT
                u.in_line = False
            if any(u.alive for u in self.units(Side.FEIND)) and "Der Feind zieht ab" not in self.events[-3:]:
                self.events.append("Der Feind zieht ab")

    def _check_outcome(self) -> None:
        enemy_gone = not self.units(Side.FEIND, fighting_only=True) and not any(
            u.alive and u.stance is Stance.FLUCHT and self.inside(u.x, u.y) for u in self.units(Side.FEIND)
        )
        city_gone = (
            self.men_start.get(Side.STADT, 0)
            and not self.units(Side.STADT, fighting_only=True)
            and self.units(Side.FEIND, fighting_only=True)
        )
        if not self.attacking and self.houses_intact() == 0:
            self.outcome = "niederlage"
            self.events.append("Die Siedlung ist geplündert")
        elif enemy_gone:
            self.outcome = "sieg"
            self.events.append("Der Überfall ist abgewehrt" if not self.attacking else "Der Feind ist geschlagen")
        elif city_gone:
            self.outcome = "niederlage"
            self.events.append("Die Verteidiger sind geschlagen" if not self.attacking else "Der Angriff ist gescheitert")
        if self.outcome is not None:
            self.brain.finish(self)

    # ------------------------------------------------------------ Bericht
    def fallen(self, side: Side) -> int:
        return self.men_start.get(side, 0) - sum(u.men for u in self.lochoi if u.side is side)

    def report(self) -> dict:
        return {
            "zeit": round(self.time, 1),
            "ausgang": self.outcome,
            "stadt_start": self.men_start.get(Side.STADT, 0),
            "stadt_gefallen": self.fallen(Side.STADT),
            "stadt_geflohen": sum(u.men for u in self.lochoi if u.side is Side.STADT and u.stance is Stance.FLUCHT),
            "feind_start": self.men_start.get(Side.FEIND, 0),
            "feind_gefallen": self.fallen(Side.FEIND),
            "haeuser_intakt": self.houses_intact(),
            "haeuser": len(self.houses),
        }
