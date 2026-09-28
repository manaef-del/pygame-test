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
from .army import Army, default_army, scaled_army
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
    enemy_ram_id: int | None = None      # Räubergruppe, die den Rammbock baut
    horde_awake: bool = False
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
        """Räuber in Trupps zu 16, Stellungen aus dem Szenario der Reihe nach."""
        remaining = max(0, self.enemy_count)
        spawns = list(self.scenario.raider_spawns)
        i = 0
        while remaining > 0 and spawns:
            n = min(RAIDER_GROUP, remaining)
            if remaining - n < 6 and remaining - n > 0:
                n = remaining
            spawn = spawns[i % len(spawns)]
            extra = 2.5 * (i // len(spawns))          # weitere Wellen weiter außen
            y = spawn.y - extra if not self.attacking else spawn.y - extra * 0.4
            rows = arrange([Man(UNIT_TYPES["raeuber"]) for _ in range(n)], math.ceil(n / 2))
            u = self._spawn(Side.FEIND, rows, spawn.x, y, "Räuber")
            u.waypoints = list(spawn.waypoints)
            if self.attacking:
                u.stance = Stance.HALTEN
                u.facing = (0.0, 1.0)
            remaining -= n
            i += 1

    def _spawn_mirror(self) -> None:
        """Die Siedlung stellt dieselbe Mischung wie der Spieler, skaliert."""
        mirror = scaled_army(self.army, self.enemy_count)
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
            d = u.rect_distance(p)
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
        das Torhaus dazu, sie laufen oben über das Tor hinweg."""
        if c in self.blocked:
            return True
        return walker and self.gate is not None and c in self.gate.cells

    def is_walker(self, u: Lochos) -> bool:
        """Wer den Wehrgang betreten darf: reine Peltasten der Wallseite über
        die Leitern, Angreifer über einen aufgestellten Turm."""
        if u.side is self.wall_side():
            return u.wall_capable()
        return bool(self.crossings)

    def ladders_for(self, u: Lochos) -> set[tuple[int, int]]:
        """Auf- und Abstiege: Leitern für alle Läufer, Türme nur für Angreifer."""
        if u.side is self.wall_side():
            return set(self.ladders)
        return set(self.ladders) | set(self.crossings)

    def on_wall(self, u: Lochos) -> bool:
        return self.is_wall_cell(self.cell(u.x, u.y), self.is_walker(u))

    def can_step(self, u: Lochos, a: Point, b: Point) -> bool:
        """Ein Schritt ist erlaubt, wenn das Ziel frei ist und der Wehrgang
        nur über eine Leiter (oder einen Turm) betreten oder verlassen wird."""
        walker = self.is_walker(u)
        if self.is_blocked(b[0], b[1], u):
            return False
        ca, cb = self.cell(*a), self.cell(*b)
        wa, wb = self.is_wall_cell(ca, walker), self.is_wall_cell(cb, walker)
        if wa == wb:
            return True
        return (ca if wa else cb) in self.ladders_for(u)

    def nearest_ladder(self, u: Lochos, p: Point, target: Point) -> Point | None:
        ladders = self.ladders_for(u)
        if not ladders:
            return None
        best = min(ladders, key=lambda c: dist(p, (c[0] + 0.5, c[1] + 0.5)) + dist((c[0] + 0.5, c[1] + 0.5), target))
        return (best[0] + 0.5, best[1] + 0.5)

    def wall_side(self) -> Side | None:
        return {"stadt": Side.STADT, "feind": Side.FEIND, None: None}[self.scenario.wall_side]

    def is_blocked(self, x: float, y: float, unit: Lochos | None = None) -> bool:
        c = self.cell(x, y)
        walker = unit is not None and self.is_walker(unit)
        if c in self.blocked:
            return not walker
        if self.gate is not None and c in self.gate.cells:
            if walker and self.on_wall(unit):
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
        """Nächster Zielpunkt und ob es schon das eigentliche Ziel ist."""
        walker = self.is_walker(u) and bool(self.ladders_for(u))
        if walker:
            on = self.on_wall(u)
            want = self.is_wall_cell(self.cell(*target), True)
            if on != want:
                ladder = self.nearest_ladder(u, u.pos, target)
                if ladder is not None and self.cell(*ladder) != self.cell(u.x, u.y):
                    return ladder, False
                return target, True
            if on and want:
                return target, True
        # am Boden: Palisade ist für alle eine Sperre, Übergang nur durchs Tor oder über Leiter/Turm
        if self.gate is None and not self.blocked:
            return target, True
        if self.path_clear(u.pos, target, None):
            return target, True
        if self.gate is not None and not self.gate.closed:
            gx, gy = self.gate.center
            above = u.y < gy
            beyond = (gx, gy + 1.2) if above else (gx, gy - 1.2)
            if self.path_clear(u.pos, beyond, None):
                return beyond, False
            return ((gx, gy - 1.2) if above else (gx, gy + 1.2)), False
        if walker:
            ladder = self.nearest_ladder(u, u.pos, u.pos)   # nächster Aufstieg
            if ladder is not None:
                return ladder, False
        if self.gate is not None:
            gx, gy = self.gate.center
            above = u.y < gy
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
        return max(0.0, min(a.rect_distance(b.pos) - b.core, b.rect_distance(a.pos) - a.core))

    def _in_contact(self, a: Lochos, b: Lochos) -> bool:
        if self._gap(a, b) > config.ENGAGE_RANGE:
            return False
        if self.on_wall(a) or self.on_wall(b):
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
            u.in_line = False
            u.target_id = None
            u.target = self._free_spot((px + off, py), u)
        self.events.append(f"{len(sel)} Gruppe(n) unterwegs")

    def command_attack_target(self, units: list[Lochos] | None, enemy: Lochos) -> None:
        self.alarm = False
        for u in self._selection(units):
            self._wake(u)
            u.stance = Stance.ANGRIFF
            u.in_line = False
            u.target_id = enemy.id
            u.target = enemy.pos
        self.events.append(f"Angriff auf {enemy.name} ({enemy.men} Mann)")

    def command_attack(self, units: list[Lochos] | None = None) -> None:
        self.alarm = False
        for u in self._selection(units):
            self._wake(u)
            u.stance = Stance.ANGRIFF
            u.in_line = False
            u.target_id = None
            u.target = None
        self.events.append("Freier Angriff")

    def command_hold(self, units: list[Lochos] | None = None) -> None:
        self.alarm = False
        for u in self._selection(units):
            self._wake(u)
            u.stance = Stance.HALTEN
            u.in_line = False
            u.target_id = None
            u.target = None
        self.events.append("Halten")

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
            self.events.append(f"{u.name} baut {'den Rammbock' if kind == 'ram' else 'den Belagerungsturm'}")
        return started

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
        defenders = self.units(Side.STADT, fighting_only=True)
        ram_unit = self._raider_ram_unit()
        for u in self.units(Side.FEIND):
            if u.stance is Stance.FLUCHT:
                u.target = (u.x, -3.0)
                continue
            if u is ram_unit:
                self._drive_raider_ram(u)
                continue
            foe, d = self._nearest(u, defenders)
            if foe is not None and foe.rect_distance(u.pos) <= config.SEEK_RANGE and not self.on_wall(foe):
                u.stance = Stance.ANGRIFF
                u.target_id = foe.id
                u.target = foe.pos
                continue
            u.stance = Stance.RAUB
            u.target_id = None
            if u.waypoints:
                if dist(u.pos, u.waypoints[0]) <= 1.0:
                    u.waypoints.pop(0)
                if u.waypoints:
                    u.target = u.waypoints[0]
                    continue
            houses = [h for h in self.houses if not h.looted]
            if houses:
                h = min(houses, key=lambda h: dist(u.pos, h.center))
                u.target = h.center
            else:
                u.target = (u.x, -3.0)

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
        """Gegner beim Angriff: Horde stürmt bei Annäherung, Siedlung hält."""
        attackers = self.units(Side.STADT, fighting_only=True)
        enemies = self.units(Side.FEIND)
        if self.scenario.enemy_kind == "raeuber":
            if not self.horde_awake and any(
                u.rect_distance(a.pos) <= config.HORDE_TRIGGER for u in enemies for a in attackers
            ):
                self.horde_awake = True
                self.events.append("Die Horde stürmt")
            for u in enemies:
                if u.stance is Stance.FLUCHT:
                    u.target = (u.x, -3.0)
                    continue
                if self.horde_awake:
                    u.stance = Stance.ANGRIFF
                    foe, _ = self._nearest(u, attackers)
                    u.target_id = foe.id if foe else None
                    u.target = foe.pos if foe else None
            return
        for u in enemies:
            if u.stance is Stance.FLUCHT:
                u.target = (u.x, -3.0)
                continue
            if u.stance is Stance.ANGRIFF:
                target = self.by_id(u.target_id) if u.target_id is not None else None
                if target is None or not target.fighting:
                    target, _ = self._nearest(u, attackers)
                    u.target_id = target.id if target else None
                u.target = target.pos if target else None
                continue
            if u.share(lambda m: m.kind.cavalry) >= 0.5:
                foe, _ = self._nearest(u, attackers)
                if foe is not None and foe.rect_distance(u.pos) <= config.CAVALRY_TRIGGER and self.path_clear(u.pos, foe.pos, u):
                    u.stance = Stance.ANGRIFF
                    u.target_id = foe.id
                    u.target = foe.pos
            # Hopliten und Peltasten halten ihre Stellung

    def _ai_city(self) -> None:
        foes = self.units(Side.FEIND)
        for u in self.units(Side.STADT, fighting_only=True):
            if u.stance is not Stance.ANGRIFF:
                continue
            target = self.by_id(u.target_id) if u.target_id is not None else None
            if target is None or not target.alive or not self.inside(target.x, target.y):
                target, _ = self._nearest(u, [f for f in foes if f.fighting] or foes)
                u.target_id = target.id if target else None
            u.target = target.pos if target else None
        for u in self.units(Side.STADT):
            if u.stance is Stance.FLUCHT:
                u.target = (u.x, self.rows + 3.0)

    # -- Bewegung ----------------------------------------------------------
    def _move(self, dt: float) -> None:
        for u in self.lochoi:
            if not u.alive or u.target is None or u.in_phalanx or u.building is not None:
                continue
            speed = u.speed * (1.25 if u.stance is Stance.FLUCHT else 1.0)
            goal, final = self.route(u, u.target)
            d = dist(u.pos, goal)
            stop_at = 0.0
            if u.stance is Stance.ANGRIFF and final:
                target = self.by_id(u.target_id) if u.target_id is not None else None
                if target is not None and self._gap(u, target) <= config.ENGAGE_RANGE * 0.8:
                    continue
                stop_at = 0.0 if target is not None else config.ENGAGE_RANGE
            if d <= max(config.ARRIVE_EPS, stop_at):
                if u.stance is Stance.PHALANX and final and d <= config.ARRIVE_EPS + 0.02:
                    u.x, u.y = u.target
                    u.in_line = True
                elif u.stance is Stance.HALTEN and final:
                    u.target = None
                continue
            step = min(speed * dt, d)
            direction = norm(sub(goal, u.pos))
            if u.stance is not Stance.PHALANX:
                u.facing = direction
            self._step(u, scale(direction, step))
            if u.stance is Stance.FLUCHT and not self.inside(u.x, u.y):
                u.withdrawn = True

    def _step(self, u: Lochos, delta: Point) -> None:
        nx, ny = u.x + delta[0], u.y + delta[1]
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
                if a.side is b.side and (a.stance is Stance.PHALANX or b.stance is Stance.PHALANX):
                    continue
                if self.on_wall(a) != self.on_wall(b):
                    continue
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
        for u in alive:
            u.engaged = False
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
        hits = [(a, b, *self._melee(a, b, dt)) for a, b in pairs]
        for a, b, dmg, arc_name in hits:
            self._apply_damage(a, b, dmg, arc_name)

    def _melee(self, a: Lochos, b: Lochos, dt: float) -> tuple[float, str]:
        rate, arc_name = self._melee_rate(a, b)
        return rate * dt, arc_name

    def _defense_mod(self, a: Lochos, b: Lochos) -> tuple[float, str]:
        arc_name = arc(b.facing, sub(a.pos, b.pos), config.FRONT_ARC, config.REAR_ARC)
        mod = 1.0
        if b.in_phalanx:
            shield = b.shield_factor()
            if arc_name == "front":
                mod = 1.0 + (config.PHALANX_FRONT - 1.0) * shield
            elif arc_name == "rear":
                mod = config.PHALANX_REAR
            support = max(config.PHALANX_SUPPORT_MIN, 1.0 - config.PHALANX_SUPPORT * self._line_neighbours(b))
            mod *= support
        if b.stance is Stance.FLUCHT:
            mod *= config.ROUTED_DAMAGE
        return mod, arc_name

    def _melee_rate(self, a: Lochos, b: Lochos) -> tuple[float, str]:
        base = a.melee_attack() * config.BASE_RATE
        attack_mod = 1.0
        if a.in_phalanx:
            front = arc(a.facing, sub(b.pos, a.pos), config.FRONT_ARC, config.REAR_ARC) == "front"
            attack_mod = config.PHALANX_ATTACK_FRONT if front else config.PHALANX_ATTACK_SIDE
        defense_mod, arc_name = self._defense_mod(a, b)
        cav = a.cavalry_share()
        if cav > 0:
            if b.in_phalanx and arc_name == "front":
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
        fallen = b.take_damage(b.exposed_row(row_arc), dmg)
        if fallen:
            morale_mod = {"rear": 1.5, "flank": 1.2}.get(arc_name, 1.0)
            if b.in_phalanx and arc_name == "front":
                morale_mod = config.MORALE_LOSS_FRONT_PHALANX
            b.morale -= fallen * (1.0 / max(1, b.men_start)) * b.bravery() * morale_mod
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
                        and a.stance in (Stance.HALTEN, Stance.PHALANX) and not self.on_wall(a)
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
            flight = max(0.15, d / config.JAVELIN_SPEED)
            for i, m in enumerate(throwers):
                m.ammo -= 1
                jitter = ((i * 7) % 5 - 2) * 0.08
                self.projectiles.append(Projectile(
                    a.x + jitter, a.y - jitter, foe.x + jitter, foe.y + jitter,
                    foe.id, config.JAVELIN_DAMAGE * shield, 0.0, flight,
                ))
        for pr in list(self.projectiles):
            pr.progress += dt
            if pr.progress >= pr.total:
                self.projectiles.remove(pr)
                b = self.by_id(pr.target_id)
                if b is not None and b.alive:
                    self._apply_damage(b, b, pr.dmg, "ranged")

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
    def _morale(self, dt: float) -> None:
        for u in self.lochoi:
            if not u.alive or u.stance is Stance.FLUCHT:
                continue
            if not u.engaged:
                u.morale = min(1.0, u.morale + config.MORALE_REGEN * dt)
            if u.morale <= u.rout_threshold:
                u.stance = Stance.FLUCHT
                u.in_line = False
                u.target = None
                u.target_id = None
                self.events.append(f"{u.name} ({u.side.value}) flieht")
                self._lose_engine(u)

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
