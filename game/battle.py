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

from . import config, pathing
from .ai import Memory, make_brain
from .army import Army, arm_of, default_army, scaled_army, split_by_arm
from .doctrine import DOCTRINE_NAMES, choose_doctrine, enemy_army
from .geometry import add, arc, dist, norm, scale, snap4, sub
from .scenarios import Scenario, inside_polygon
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
    normal: Point = (0.0, -1.0)          # Richtung nach außen (waagrecht oder senkrecht)

    @property
    def center(self) -> Point:
        n = len(self.cells)
        return (sum(c[0] for c in self.cells) / n + 0.5, sum(c[1] for c in self.cells) / n + 0.5)

    @property
    def tangent(self) -> Point:
        """Entlang des Walls: nach Osten, bei senkrechtem Durchgang nach Süden."""
        nx, ny = self.normal
        return (abs(ny), abs(nx))

    @property
    def half_len(self) -> float:
        """Halbe Breite des Durchgangs, entlang des Walls."""
        cx, cy = self.center
        tx, ty = self.tangent
        return max(abs((c[0] + 0.5 - cx) * tx + (c[1] + 0.5 - cy) * ty) for c in self.cells) + 0.5

    @property
    def half_thick(self) -> float:
        """Halbe Tiefe des Torhauses, quer zum Wall."""
        cx, cy = self.center
        nx, ny = self.normal
        return max(abs((c[0] + 0.5 - cx) * nx + (c[1] + 0.5 - cy) * ny) for c in self.cells) + 0.5

    @property
    def broken(self) -> bool:
        return self.hp <= 0


@dataclass
class CornerTower:
    """Ein Wehrturm auf dem Wall: wirft Speere für seinen Besitzer, solange kein Feind
    oben steht; steht nur der Feind oben, gehört er ihm."""
    cell: tuple[int, int]
    owner: Side | None
    timer: float = 0.0

    @property
    def center(self) -> Point:
        return (self.cell[0] + 0.5, self.cell[1] + 0.5)


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
    target_man: Man | None = None      # auf ihn wurde gezielt; getroffen wird, wer am Einschlag steht
    cover: bool = True                 # Schilde decken (Wurfspeere der Peltasten; nicht von den Ecktürmen herab)

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
class Verband:
    """Mehrere Gruppen in einer Formation: Reihen vorn nach hinten, je Reihe die
    Gruppen von links nach rechts (wie sie auf die Front schauen). Die Gruppen bleiben
    eigenständig (Modus, Moral, Befehle); ein Befehl an den Verband stellt alle auf."""

    id: int
    name: str
    rows: list[list[int]]
    formation: str = "linie"                       # "linie" oder "o" (Ringe ineinander, vorn außen)
    centre: Point | None = None                    # Mitte der vorderen Reihe (Kreis: Mitte), zuletzt befohlen
    facing: Point = (0.0, -1.0)
    length: float | None = None                    # Länge der vorderen Reihe
    slots: dict = field(default_factory=dict)      # Gruppen-id -> ihr Platz (LinePlan oder (Mitte, Halbmesser))

    def members(self) -> list[int]:
        return [uid for row in self.rows for uid in row]


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
    gate: Gate | None = None                          # das (erste) Tor
    gates: list[Gate] = field(default_factory=list)   # alle Tore
    corner_towers: list[CornerTower] = field(default_factory=list)
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
    fallen_marks: list[tuple[Point, float]] = field(default_factory=list)          # nur fürs Bild: wo und wann einer fiel
    climb_budget: dict[tuple[int, int], float] = field(default_factory=dict)       # Durchsatz je Leiter/Turm
    _barrier_cache: dict = field(default_factory=dict)
    _man_grid: dict = field(default_factory=dict)      # Männer je Rasterzelle (0,5 Kacheln), je Schritt neu
    _man_group: dict = field(default_factory=dict)     # id(Mann) -> Gruppen-id, je Schritt neu
    _man_side: dict = field(default_factory=dict)      # id(Mann) -> Seite, je Schritt neu
    leaders: list = field(default_factory=list)        # (Mann, Seite, Gruppenname) der Anführer, für die Meldung bei ihrem Tod
    _fields: dict = field(default_factory=dict)        # Gruppen-id -> (Schlüssel, Zeit, Wegefeld)
    _field_builds: dict = field(default_factory=dict)  # Schlachtzeit -> Zahl der in diesem Takt gerechneten Wegefelder
    _static_grid: tuple | None = None                  # (Tor zu?, Zellraster der festen Hindernisse)
    enemy_ram_id: int | None = None      # Räubergruppe, die den Rammbock baut
    horde_awake: bool = False
    ai: str = config.AI_DEFAULT          # "klug" oder "einfach"
    memory: Memory | None = None         # Gedächtnis der Gegner über Schlachten hinweg
    doctrine: str | None = None          # Aufstellung der Siedlung; None = passend zum Spieler wählen
    _next_id: int = 0
    verbaende: list[Verband] = field(default_factory=list)
    _next_vid: int = 1

    # ------------------------------------------------------------ Aufbau
    def __post_init__(self) -> None:
        s = self.scenario
        if self.enemy_count is None:
            self.enemy_count = s.enemy_default
        self.cols, self.rows = s.cols, s.rows
        self.houses = [House(cx, cy) for cx, cy in s.houses]
        self.house_cells = {(h.cx, h.cy) for h in self.houses}        # Häuser: niemand geht hindurch
        self._ram_cells: set[tuple[int, int]] = set()                  # liegende Rammböcke (Viertelkacheln)
        self._tower_cells: set[tuple[int, int]] = set()                # aufgestellte Türme (Viertelkacheln)
        self._engines_key = (0, 0)
        self._clearance: tuple | None = None                           # Abstandsfeld für die Wege der Blöcke
        self._block_ways: dict = {}
        self._narrow_cache: dict = {}
        self._ring_friends: dict = {}                                  # Gruppe -> Gruppen, deren Ringe in ihrem stehen
        self._group_map: dict = {}                                     # Gruppen-id -> Gruppe, je Schritt neu
        self._pass_choice: dict = {}                                   # Gruppe -> (Ziel, als Block um eigene herum?)
        self._steps_cache: dict = {}                                   # Wehrgang: Schritte von einem Wallstück aus
        self._wall_route: dict = {}                                    # Gruppe -> (Ziel, über die Leitern schneller?)
        self._wall_occ: tuple | None = None                            # (Zeit, Kachel -> gesperrte Seiten) auf dem Wehrgang                                  # Gruppe -> (Ziel, Zeit, passt der Block nicht durch?)
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
            outward = -1.0 if s.wall_side == "stadt" else 1.0      # außen liegt, wo der Angreifer steht
            self.gates.append(Gate(sorted(cells), closed=s.gate_closed, normal=(0.0, outward)))
        for cells, out in s.gates:
            self.gates.append(Gate(list(cells), closed=s.gate_closed, normal=(float(out[0]), float(out[1]))))
        self.gate = self.gates[0] if self.gates else None
        self._gate_of = {c: g for g in self.gates for c in g.cells}
        self.ring = bool(s.ring)
        self._level_of: dict[tuple[int, int], str] = {}
        self._foot: dict[tuple[int, int], tuple[int, int]] = {}      # Leiter/Turm -> Richtung zur Kachel am Fuß
        self._walkway: tuple | None = None
        self._ring_cache: dict = {}
        self._slot_cache: dict = {}
        if self.ring:
            for c in self.ladders:
                self._foot[c] = self._ground_step(c, "innen")
        team = {"stadt": Side.STADT, "feind": Side.FEIND}.get(s.wall_side)
        self.corner_towers = [CornerTower(c, team) for c in s.corner_towers]
        self._deploy_army()
        if s.enemy_kind == "raeuber":
            self._spawn_raiders()
        elif s.enemy_kind == "armee":
            self._spawn_army()
        elif self.ring:
            self._spawn_garrison()
        else:
            self._spawn_mirror()
        self.men_start = {side: self.men(side) for side in Side}
        self.leaders = [(m, u.side, u.name) for u in self.lochoi for m in u.all_men() if m.leader]
        if self.ring:
            from .fortress_ai import FortressBrain
            self.brain = FortressBrain(self.memory)
        else:
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
        """Die eigene Truppe nebeneinander aufstellen. Eine Gruppe mit mehreren Gattungen
        wird je Gattung eine eigene Gruppe; zusammen bilden sie einen Verband."""
        specs = [g for g in self.army.groups if g.men() > 0]
        if not specs:
            return
        parts: list[tuple[int, str, list[Man]]] = []          # (Aufstellungsgruppe, Name, Männer)
        names = {"hopliten": "Hopliten", "peltasten": "Peltasten", "reiter": "Reiter"}
        for k, spec in enumerate(specs):
            by_arm: dict[str, list[Man]] = {}
            for m in spec.build_men():
                by_arm.setdefault(arm_of(m.kind.key), []).append(m)
            for arm, men_ in by_arm.items():
                parts.append((k, spec.name if len(by_arm) == 1 else names[arm], men_))
        rows_units = [arrange(men_, default_width(len(men_))) for _, _, men_ in parts]
        widths = [max(0.9, 2 * Lochos(0, Side.STADT, r, 0, 0).radius + 0.2) for r in rows_units]
        x = self.cols / 2 - sum(widths) / 2
        made: dict[int, list[Lochos]] = {}
        for (k, name, _), rows, w in zip(parts, rows_units, widths):
            u = self._spawn(Side.STADT, rows, min(max(x + w / 2, 0.6), self.cols - 0.6), self.scenario.deploy_y, name)
            made.setdefault(k, []).append(u)
            x += w
        for k, units in made.items():
            if len(units) > 1:
                v = self._new_verband(units, specs[k].name)
                self._form_verband(v, self._verband_anchor(units)[0], v.facing, None, quiet=True)
                for u in units:
                    if u.march is not None:
                        u.reform(u.march[1])
                    u.march = None
                    u.x, u.y = u.target
                    if u.face_to is not None:
                        u.facing = u.face_to
                    u.place_men()

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
        if mirror.groups and mirror.leader_index() is None:
            # auch die Siedlung hat einen Anführer: bei ihrer ersten Hoplitengruppe
            hoplites = [i for i, g in enumerate(mirror.groups) if g.men() and any(UNIT_TYPES[t.kind].hoplite for t in g.tiers)]
            mirror.set_leader(hoplites[0] if hoplites else 0)
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

    @staticmethod
    def _companies(army: Army) -> dict[str, list[tuple[str, list[Man]]]]:
        """Ein Heer in handliche Gruppen je Gattung teilen (Hopliten zu etwa 24, Peltasten
        zu 16, Reiter zu 20 Mann), damit es mehrere Tore zugleich angehen oder halten kann."""
        size = {"hopliten": 24, "peltasten": 16, "reiter": 20}
        names = {"hopliten": "Hopliten", "peltasten": "Peltasten", "reiter": "Reiter"}
        out: dict[str, list[tuple[str, list[Man]]]] = {"hopliten": [], "peltasten": [], "reiter": []}
        for g in split_by_arm(army).groups:
            men = g.build_men()
            if not men:
                continue
            arm = arm_of(men[-1].kind.key)
            k = max(1, round(len(men) / size[arm]))
            for i in range(k):
                part = men[i * len(men) // k:(i + 1) * len(men) // k]
                if part:
                    out[arm].append((names[arm], part))
        return out

    def _spawn_army(self) -> None:
        """Festung: ein Heer aus Hopliten, Peltasten und Reitern rückt von Norden an,
        in der Mischung der eigenen Truppe auf seine Stärke gebracht."""
        army = scaled_army(default_army(), max(1, self.enemy_count))
        if army.leader_index() is None and army.groups:
            army.set_leader(0)
        parts = self._companies(army)
        self.events.append("Ein Heer rückt an: " + ", ".join(
            f"{sum(len(m) for _, m in parts[a])} {n}" for a, n in (("hopliten", "Hopliten"), ("peltasten", "Peltasten"),
                                                                    ("reiter", "Reiter")) if parts[a]))

        def row_of(groups, y, x0, x1, width_men, stance):
            if not groups:
                return
            rows_units = [arrange(men, max(1, min(len(men), width_men))) for _, men in groups]
            widths = [2 * Lochos(0, Side.FEIND, r, 0, 0).half_w + 0.6 for r in rows_units]
            x = (x0 + x1) / 2 - sum(widths) / 2
            for (name, _), rows, w in zip(groups, rows_units, widths):
                u = self._spawn(Side.FEIND, rows, x + w / 2, y, name)
                u.facing = (0.0, 1.0)
                u.stance = stance
                x += w

        cx = self.cols / 2
        row_of(parts["peltasten"], 5.2, cx - 8.0, cx + 8.0, 8, Stance.HALTEN)
        row_of(parts["hopliten"], 3.6, cx - 9.0, cx + 9.0, 8, Stance.HALTEN)
        cav = parts["reiter"]
        for k, (name, men) in enumerate(cav):
            u = self._spawn(Side.FEIND, arrange(men, max(1, min(len(men), 7))),
                            3.0 + 1.5 * (k // 2) if k % 2 == 0 else self.cols - 3.0 - 1.5 * (k // 2), 3.0, name)
            u.facing = (0.0, 1.0)
            u.stance = Stance.HALTEN

    def _spawn_garrison(self) -> None:
        """Festung im Angriff: die Besatzung in der Aufstellung ihrer Doktrin. Hinter jedem
        Tor eine Phalanx (die dem Feind nächsten zuerst), Peltasten auf dem Wehrgang,
        die Reiter als Reserve auf der Agora."""
        self.doctrine = self.doctrine or choose_doctrine(self.army, self.memory)
        mirror = enemy_army(self.army, self.enemy_count, self.doctrine)
        if mirror.groups and mirror.leader_index() is None:
            hoplites = [i for i, g in enumerate(mirror.groups) if g.men() and any(UNIT_TYPES[t.kind].hoplite for t in g.tiers)]
            mirror.set_leader(hoplites[0] if hoplites else 0)
        self.events.append(f"Die Festung stellt: {DOCTRINE_NAMES.get(self.doctrine, self.doctrine)}")
        parts = self._companies(mirror)
        enemy_at = (self.cols / 2, self.scenario.deploy_y)
        gates = sorted(self.gates, key=lambda g: dist(g.center, enemy_at))
        lines = list(parts["hopliten"])
        if 0 < len(lines) < len(gates) and len(lines[0][1]) >= 24:
            name, men = lines.pop(0)                    # ein großer Block teilt sich für zwei Tore
            lines[:0] = [(name, men[: len(men) // 2]), (name, men[len(men) // 2:])]
        for k, (name, men) in enumerate(lines):
            g = gates[k % len(gates)]
            rows = arrange(men, max(1, min(len(men), 8)))
            probe = Lochos(0, Side.FEIND, rows, 0, 0)
            behind = self.gate_approach(g, -1.0, probe.half_d + 0.4 + 1.6 * (k // len(gates)))
            u = self._spawn(Side.FEIND, rows, behind[0], behind[1], name)
            u.facing = g.normal
            u.stance = Stance.PHALANX
            u.in_line = True
        near_ladders = sorted(self.ladders, key=lambda c: dist((c[0] + 0.5, c[1] + 0.5), enemy_at))
        for k, (name, men) in enumerate(parts["peltasten"]):
            c = near_ladders[k % len(near_ladders)] if near_ladders else None
            rows = arrange(men, max(1, min(len(men), 14)))
            if c is None:
                x, y = self.agora
            else:
                x, y = c[0] + 0.5, c[1] + 0.5
            u = self._spawn(Side.FEIND, rows, x, y, name)
            u.stance = Stance.HALTEN
            u.facing = norm(sub(enemy_at, (x, y)))
        ax, ay = self.agora
        for k, (name, men) in enumerate(parts["reiter"]):
            u = self._spawn(Side.FEIND, arrange(men, max(1, min(len(men), 7))), ax + (k - (len(parts["reiter"]) - 1) / 2) * 2.5, ay, name)
            u.facing = (0.0, 1.0)
            u.stance = Stance.HALTEN

    def _spawn(self, side: Side, rows: list[list[Man]], x: float, y: float, name: str) -> Lochos:
        unit = Lochos(id=self._next_id, side=side, rows=rows, x=x, y=y, name=name)
        if self.ring:
            unit.wall_layout = self._wall_slots
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
        if self.ring:
            return self.gate_near(p, tolerance) is not None
        gx, gy = self.gate.center
        half = len(self.gate.cells) / 2
        return abs(p[0] - gx) <= half + tolerance and abs(p[1] - gy) <= 0.5 + tolerance

    def gate_near(self, p: Point, tolerance: float = 0.4) -> Gate | None:
        """Das Tor, auf das ``p`` zeigt (oder None)."""
        for g in self.gates:
            cx, cy = g.center
            (tx, ty), (nx, ny) = g.tangent, g.normal
            along = abs((p[0] - cx) * tx + (p[1] - cy) * ty)
            across = abs((p[0] - cx) * nx + (p[1] - cy) * ny)
            if along <= g.half_len + tolerance and across <= g.half_thick + tolerance:
                return g
        return None

    def gate_of(self, c: tuple[int, int]) -> Gate | None:
        return self._gate_of.get(c)

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
        if not walker:
            return False
        g = self._gate_of.get(c)
        return g is not None and g.closed

    def is_walker(self, u: Lochos) -> bool:
        """Wer den Wehrgang betreten darf: von der Wallseite reine Peltasten über die Leitern
        (in der Festung jede Fußgruppe), Angreifer über einen aufgestellten Turm."""
        if u.side is self.wall_side():
            if self.ring and config.FORT_FOOT_ON_WALL:
                men = u.men
                return men > 0 and 2 * len(u.mounted_men()) < men and u.engine is None   # Festung: alles Fußvolk
            return u.wall_capable()
        if not self.crossings:
            return False
        if self.ring and 2 * len(u.mounted_men()) >= u.men:
            return False                  # Festung: wer im Sattel sitzt, klettert nicht
        return True

    def ladders_for(self, u: Lochos, pos: Point | None = None, target: Point | None = None) -> set[tuple[int, int]]:
        """Auf- und Abstiege: Leitern für alle Läufer; der Turm nur für Angreifer
        und nur zwischen Wehrgang und Außenseite."""
        outside_south = self.wall_side() is Side.FEIND
        ground = target if (pos is not None and self.is_wall_cell(self.cell(*pos), True)) else pos
        if ground is not None and self.is_wall_cell(self.cell(*ground), True):
            ground = None                          # Ziel oben: jeder Auf- oder Abstieg kommt in Frage
        out: set[tuple[int, int]] = set()
        if self.ring:
            level = self._wall_level(ground) if ground is not None else None
            if level is None or level == "innen":
                out |= self.ladders                # Leitern stehen innen
            if u.side is not self.wall_side() and (level is None or level == "aussen"):
                out |= self.crossings              # der Turm steht außen
            return out
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
        if self.ring:
            return self._cell_level(ground_cell) == "innen"
        outside_south = self.wall_side() is Side.FEIND
        return (ground_cell[1] > wall_cell[1]) != outside_south

    def tower_ok(self, wall_cell: tuple[int, int], ground_cell: tuple[int, int]) -> bool:
        """Ein Belagerungsturm steht an der Außenseite des Walls."""
        if self.ring:
            return self._cell_level(ground_cell) == "aussen"
        outside_south = self.wall_side() is Side.FEIND
        return (ground_cell[1] > wall_cell[1]) == outside_south

    def on_wall(self, u: Lochos) -> bool:
        return self.is_wall_cell(self.cell(u.x, u.y), self.is_walker(u))

    def _fights_from_wall(self, u: Lochos) -> bool:
        """Kämpft die Gruppe von oben (vom Wehrgang)? Eine aufgelöste Gruppe nur, wenn
        alle ihre Männer oben stehen; wer schon unten ist, kämpft auf Augenhöhe."""
        if u.loose:
            walker = self.is_walker(u)
            men = u.all_men()
            return bool(men) and all(self.is_wall_cell(self.cell(m.x, m.y), walker) for m in men)
        return self.on_wall(u)

    def crossing(self, u: Lochos) -> bool:
        """Steigt die Gruppe gerade Mann für Mann über den Wall (ihre Männer stehen auf
        verschiedenen Seiten oder oben)? Für die Gegner-KI gilt sie dann als oben."""
        if not (u.loose and u.loose_why == "wall"):
            return False
        levels = {self._wall_level(m.pos) for m in u.all_men()}
        if self.ring:
            levels.discard("tor")
        return len(levels) > 1 or "wall" in levels

    def up(self, u: Lochos) -> bool:
        """Oben auf dem Wall, oder gerade beim Übersteigen."""
        return self.on_wall(u) or self.crossing(u)

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
            return self.tower_ok(wall_cell, ground_cell)   # Turm: nur an der Außenseite des Walls (dort steht er)
        return False

    def wall_connected(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        """Liegen zwei Wallstücke auf demselben Wehrgang ohne Lücke (offenes Tor) dazwischen?"""
        if self.ring:
            comp = self._walkway_parts()
            return a in comp and comp.get(a) == comp.get(b)
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

    def _walkway_parts(self) -> dict[tuple[int, int], int]:
        """Zusammenhängende Stücke des Wehrgangs (Kanten-Nachbarn); ein offenes Tor trennt."""
        key = tuple(g.closed for g in self.gates)
        if self._walkway is not None and self._walkway[0] == key:
            return self._walkway[1]
        cells = set(self.blocked) | {c for g in self.gates if g.closed for c in g.cells}
        comp: dict[tuple[int, int], int] = {}
        for start in cells:
            if start in comp:
                continue
            k = len(comp)
            stack = [start]
            comp[start] = k
            while stack:
                x, y = stack.pop()
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if n in cells and n not in comp:
                        comp[n] = k
                        stack.append(n)
        self._walkway = (key, comp)
        return comp

    def _cell_level(self, c: tuple[int, int]) -> str:
        """Festung: "innen" oder "aussen" für eine Kachel am Boden (fest, einmal gerechnet)."""
        level = self._level_of.get(c)
        if level is None:
            level = "innen" if inside_polygon(self.scenario.ring, c[0] + 0.5, c[1] + 0.5) else "aussen"
            self._level_of[c] = level
        return level

    def _ground_step(self, c: tuple[int, int], level: str) -> tuple[int, int]:
        """Von einem Wallstück der Schritt (dx, dy) zur Kachel am Boden auf der Seite
        ``level``, möglichst geradeaus vom Wall weg."""
        cx, cy = self.scenario.agora or (self.cols / 2, self.rows / 2)
        to_centre = (cx - c[0] - 0.5, cy - c[1] - 0.5)
        best, best_v = (0, 1), -math.inf
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + d[0], c[1] + d[1])
            if n in self.blocked or n in self._gate_of or self._cell_level(n) != level:
                continue
            v = d[0] * to_centre[0] + d[1] * to_centre[1]
            v = v if level == "innen" else -v
            if v > best_v:
                best, best_v = d, v
        return best

    def foot_of(self, c: tuple[int, int]) -> Point:
        """Wo man unten an Leiter oder Turm steht."""
        if not self.ring:
            side = self._inner_dir() if c in self.ladders else -self._inner_dir()
            return (c[0] + 0.5, c[1] + 0.5 + side)
        dx, dy = self._foot.get(c, (0, 1))
        return (c[0] + 0.5 + dx, c[1] + 0.5 + dy)

    def _inner_dir(self) -> float:
        """Richtung (y) von der Palisade zur Innenseite, wo die Leitern stehen."""
        return 1.0 if self.wall_side() is Side.STADT else -1.0

    def wall_side(self) -> Side | None:
        return {"stadt": Side.STADT, "feind": Side.FEIND, None: None}[self.scenario.wall_side]

    def is_blocked(self, x: float, y: float, unit: Lochos | None = None, from_wall: bool | None = None,
                   climber: Lochos | None = None) -> bool:
        """``climber``: wer über einen aufgestellten Turm auf den Wall will, darf in ihn
        hinein (auch wenn der Wall für die Prüfung sonst als Sperre zählt)."""
        c = self.cell(x, y)
        if c in self.house_cells:
            return True
        if self._ram_cells or self._tower_cells:
            q = (math.floor(x * 4), math.floor(y * 4))
            if q in self._ram_cells:
                return True
            if q in self._tower_cells:
                who = climber or unit
                if not (who is not None and who.side is not self.wall_side() and self.is_walker(who)):
                    return True               # in den Turm steigt nur, wer über ihn auf den Wall will
        walker = unit is not None and self.is_walker(unit)
        if c in self.blocked:
            return not walker
        g = self._gate_of.get(c)
        if g is not None:
            if from_wall is None:
                from_wall = unit is not None and self.on_wall(unit)
            if walker and from_wall:
                return False          # oben über das Torhaus
            return g.closed
        return False

    def inside(self, x: float, y: float) -> bool:
        return 0.0 <= x < self.cols and 0.0 <= y < self.rows

    def path_clear(self, a: Point, b: Point, unit: Lochos | None = None, climber: Lochos | None = None) -> bool:
        d = dist(a, b)
        n = max(1, int(d / 0.25))
        for i in range(1, n + 1):
            t = i / n
            if self.is_blocked(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, unit, climber=climber):
                return False
        return True

    def wall_clear(self, a: Point, b: Point) -> bool:
        """Liegt kein Wall und kein geschlossenes Tor zwischen ``a`` und ``b``? (Häuser und
        Gerät zählen hier nicht: um sie herum führt die Wegsuche der Blöcke.)"""
        d = dist(a, b)
        n = max(1, int(d / 0.25))
        for i in range(1, n + 1):
            t = i / n
            c = self.cell(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            if c in self.blocked:
                return False
            g = self._gate_of.get(c)
            if g is not None and g.closed:
                return False
        return True

    def route(self, u: Lochos, target: Point) -> tuple[Point, bool]:
        """Nächster Zielpunkt der Gruppe und ob es schon das eigentliche Ziel ist."""
        return self.route_from(u, u.pos, target)

    def route_from(self, u: Lochos, pos: Point, target: Point) -> tuple[Point, bool]:
        """Wie ``route``, aber von einer beliebigen Position aus (auch für einzelne Männer)."""
        if self.ring:
            return self._route_ring(u, pos, target)
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
                            if self.wall_clear(pos, foot):
                                return foot, False
                            wp = (ladder[0], pos[1])
                            if dist(pos, wp) > 0.1 and self.wall_clear(pos, wp):
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
        if self.blocked and not self.wall_clear(pos, target):
            here, there = self._wall_level(pos), self._wall_level(target)
            if here != "wall" and (there == here or there == "wall"):
                wp = (target[0], pos[1])
                if self.wall_clear(pos, wp) and dist(pos, wp) > 0.1:
                    return wp, False
        # am Boden: Palisade ist für alle eine Sperre, Übergang nur durchs Tor oder über Leiter/Turm
        if self.gate is None and not self.blocked:
            return target, True
        if self.wall_clear(pos, target):
            return target, True
        if self.gate is not None and not self.gate.closed:
            gx, gy = self.gate.center
            if self.cell(*pos) in self.gate.cells:
                above = target[1] > gy         # im Durchgang: auf die Zielseite weiter
            else:
                above = pos[1] < gy
            beyond = (gx, gy + 1.2) if above else (gx, gy - 1.2)
            if self.wall_clear(pos, beyond):
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

    # -------------------------------------------------------- Festung: Wege
    def _route_ring(self, u: Lochos, pos: Point, target: Point) -> tuple[Point, bool]:
        """Wege in der Festung: auf dem Wehrgang an der Brüstung entlang, hinauf und
        hinunter über Leitern (innen) und Türme (außen), am Boden um die Ecken des
        Sechsecks herum und durch das Tor, das am wenigsten Umweg macht."""
        walker = self.is_walker(u) and bool(self.ladders_for(u))
        here, there = self.cell(*pos), self.cell(*target)
        on, want = self.is_wall_cell(here, True), self.is_wall_cell(there, True)
        if walker:
            if on and want and not self.wall_connected(here, there):
                want = False              # Lücke im Wehrgang: erst hinunter, unten weiter, drüben wieder hinauf
            if on and want and self._ladders_faster(u, here, there):
                want = False              # über die Leitern ist es trotz Klettern schneller: hinab, quer, hinauf
            if on and want:
                if self._on_walkway(pos, target):
                    return target, True
                return self._walk_along(pos, there), False
            if on != want or (not on and self._wall_level(pos) != self._wall_level(target)
                              and not any(not g.closed for g in self.gates)):
                ladder = self.nearest_ladder(u, pos, target)
                if ladder is not None:
                    lc = self.cell(*ladder)
                    if on:
                        if lc == here:
                            return self.foot_of(lc), False     # auf der Leiter: hinunter
                        return self._walk_along(pos, lc), False
                    foot = self.foot_of(lc)
                    ax, ay = foot[0] - ladder[0], foot[1] - ladder[1]          # von der Leiter zum Fuß (Länge 1)
                    rx, ry = pos[0] - ladder[0], pos[1] - ladder[1]
                    under = rx * ax + ry * ay > 0 and abs(rx * ay - ry * ax) <= 0.3   # in einer Linie darunter
                    if not under and self.cell(*pos) != lc:
                        wp, _ = self._ground_way(u, pos, foot)
                        return wp, False
                    return ladder, False
                if on != want:
                    return target, True
        if on:
            return target, True               # wer (ohne Erlaubnis) oben steht, geht geradeaus
        return self._ground_way(u, pos, target)

    def _walkway_steps(self, start: tuple[int, int]) -> dict[tuple[int, int], int]:
        """Schritte (Kacheln) über den Wehrgang von ``start`` zu jedem erreichbaren Wallstück."""
        key = (start, tuple(g.closed for g in self.gates))
        hit = self._steps_cache.get(key)
        if hit is not None:
            return hit
        cells = self._walkway_parts()
        steps = {start: 0}
        queue = [start]
        for c in queue:
            for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
                if n in cells and n not in steps:
                    steps[n] = steps[c] + 1
                    queue.append(n)
        if len(self._steps_cache) > 400:
            self._steps_cache.clear()
        self._steps_cache[key] = steps
        return steps

    def _ladders_faster(self, u: Lochos, here: tuple[int, int], there: tuple[int, int]) -> bool:
        """Festung, oben auf dem Wehrgang zu einem anderen Wallstück: oben entlang, oder über
        eine Leiter hinab, unten quer und über eine andere hinauf? Jedes Klettern kostet die
        Zeit, bis alle Männer die Leiter hinter sich haben. Einmal je Ziel entschieden."""
        if not config.WALL_LADDER_SHORTCUT or not self.ladders:
            return False
        key = (there, tuple(g.closed for g in self.gates))
        hit = self._wall_route.get(u.id)
        if hit is not None and hit[0] == key:
            return hit[1]
        from_here, to_there = self._walkway_steps(here), self._walkway_steps(there)
        along = from_here.get(there)
        speed = max(0.1, u.speed)
        climb = (u.men / config.CLIMB_RATE + config.WALL_CLIMB_EXTRA) * speed   # als Wegstrecke
        best = math.inf
        downs = [(c, from_here[c]) for c in self.ladders if c in from_here]
        ups = [(c, to_there[c]) for c in self.ladders if c in to_there]
        for a, da in downs:
            fa = self.foot_of(a)
            for c, dc in ups:
                if c != a:
                    best = min(best, da + climb + dist(fa, self.foot_of(c)) + climb + dc)
        faster = along is not None and best < along
        self._wall_route[u.id] = (key, faster)
        return faster

    def _wall_slots(self, u: Lochos, centre: Point) -> list[tuple[Man, Point]]:
        """Festung: Plätze auf dem Wehrgang um ``centre``, Kachel für Kachel den Wehrgang
        entlang, in vier Rotten mit dem Abstand einer Formation (bis zu 20 Mann je Kachel);
        Leitern und Turmübergänge bleiben frei."""
        men = u.all_men()
        if not men:
            return []
        parts = self._walkway_parts()
        start = self.cell(*centre)
        if start not in parts:
            near = [c for c in parts if abs(c[0] - start[0]) <= 2 and abs(c[1] - start[1]) <= 2]
            if not near:
                return [(m, centre) for m in men]
            start = min(near, key=lambda c: dist((c[0] + 0.5, c[1] + 0.5), centre))
        key = (start, round(centre[0], 1), round(centre[1], 1), len(men), len(self.crossings),
               tuple(g.closed for g in self.gates))
        points = self._slot_cache.get(key)
        if points is None:
            free = [start]
            seen = {start}
            pts: list[Point] = []
            for c in free:
                if c not in self.ladders and c not in self.crossings:
                    # in Rotten quer zum Wehrgang, mit dem Abstand einer Formation (dicht, nicht verstreut)
                    along_x = (c[0] + 1, c[1]) in parts or (c[0] - 1, c[1]) in parts
                    for a_ in config.WALL_ALONG:
                        for q in config.WALL_ACROSS:
                            dx, dy = (a_, q) if along_x else (q, a_)
                            pts.append((c[0] + 0.5 + dx, c[1] + 0.5 + dy))
                if len(pts) >= len(men) + 2 * len(config.WALL_ALONG) * len(config.WALL_ACROSS):
                    break
                for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
                    if n in parts and n not in seen:
                        seen.add(n)
                        free.append(n)
            points = sorted(pts, key=lambda p: dist(p, centre))[:len(men)]
            if len(self._slot_cache) > 2000:
                self._slot_cache.clear()
            self._slot_cache[key] = points
        if len(points) < len(men):
            points = points + [centre] * (len(men) - len(points))
        return list(zip(men, points))

    def _walk_along(self, pos: Point, goal: tuple[int, int]) -> Point:
        """Auf dem Wehrgang zum Wallstück ``goal``: über die Wallstücke dazwischen, nie
        über den Rand hinaus (an den Schrägen geht es treppauf, treppab)."""
        here = self.cell(*pos)
        gp = (goal[0] + 0.5, goal[1] + 0.5)
        if here == goal or self._on_walkway(pos, gp):
            return gp
        cells = self._walkway_parts()
        prev: dict[tuple[int, int], tuple[int, int] | None] = {here: None}
        queue = [here]
        for c in queue:
            if c == goal:
                break
            for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
                if n in cells and n not in prev:
                    prev[n] = c
                    queue.append(n)
        if goal not in prev:
            return gp
        path = [goal]
        while prev[path[-1]] is not None:
            path.append(prev[path[-1]])
        path.reverse()                                    # here ... goal
        best = path[1] if len(path) > 1 else goal
        for c in path[1:]:
            q = (c[0] + 0.5, c[1] + 0.5)
            if not self._on_walkway(pos, q):
                break
            best = c
        return (best[0] + 0.5, best[1] + 0.5)

    def _on_walkway(self, a: Point, b: Point) -> bool:
        n = max(1, int(dist(a, b) / 0.2))
        for i in range(1, n + 1):
            t = i / n
            if not self.is_wall_cell(self.cell(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), True):
                return False
        return True

    def _gate_side(self, g: Gate, p: Point) -> float:
        """+1, wenn ``p`` außerhalb der Festung liegt, sonst -1 (im Tor oder auf dem Wall
        entscheidet die Richtung des Durchgangs)."""
        level = self._wall_level(p)
        if level == "aussen":
            return 1.0
        if level == "innen":
            return -1.0
        cx, cy = g.center
        return 1.0 if (p[0] - cx) * g.normal[0] + (p[1] - cy) * g.normal[1] > 0 else -1.0

    def gate_approach(self, g: Gate, side: float, extra: float = 0.0) -> Point:
        """Ein Punkt vor (``side`` +1: außen) oder hinter dem Tor, mitten im Durchgang."""
        cx, cy = g.center
        d = g.half_thick + 0.7 + extra
        return (cx + g.normal[0] * side * d, cy + g.normal[1] * side * d)

    def _ground_way(self, u: Lochos | None, pos: Point, target: Point) -> tuple[Point, bool]:
        if self.wall_clear(pos, target):
            return target, True
        here = self._wall_level(pos)
        there = self._wall_level(target)
        if here == "tor":
            g = self._gate_of[self.cell(*pos)]
            beyond = self.gate_approach(g, self._gate_side(g, target))
            if self.wall_clear(pos, beyond):
                return beyond, False
            return self.gate_approach(g, -self._gate_side(g, target)), False
        if there in ("wall", "tor"):
            g = self._gate_of.get(self.cell(*target))
            if g is not None:
                there = "aussen" if self._gate_side(g, pos) > 0 else "innen"
            else:
                there = here
        if here == there:
            return self._around_ring(pos, target, here), False
        gates = [g for g in self.gates if not g.closed]
        if gates:
            def cost(g: Gate) -> float:
                s_ = self._gate_side(g, pos)
                return dist(pos, self.gate_approach(g, s_)) + dist(self.gate_approach(g, -s_), target)
            g = min(gates, key=cost)
            s_ = self._gate_side(g, pos)
            near, far = self.gate_approach(g, s_), self.gate_approach(g, -s_)
            if self.wall_clear(pos, far):
                return far, False
            if self.wall_clear(pos, near):
                return near, False
            return self._around_ring(pos, near, here), False
        # alle Tore zu: vor dem nächsten Tor warten (auf der eigenen Seite)
        g = min(self.gates, key=lambda g: dist(pos, g.center) + dist(g.center, target))
        s_ = self._gate_side(g, pos)
        k = (u.id if u is not None else 0)
        spread = ((k % 5) - 2) * 1.3
        far = config.ENEMY_RALLY_DISTANCE + 0.6 * ((k // 5) % 3)
        cx, cy = g.center
        tx, ty = g.tangent
        wait = (cx + g.normal[0] * s_ * far + tx * spread, cy + g.normal[1] * s_ * far + ty * spread)
        wait = self._free_spot(wait, u)
        if self.wall_clear(pos, wait):
            return wait, False
        return self._around_ring(pos, wait, here), False

    def _ring_nodes(self, level: str) -> list[Point]:
        """Umwegpunkte um die Ecken des Sechsecks: außen etwas vor jeder Ecke, innen etwas davor."""
        cx, cy = self.scenario.agora or (self.cols / 2, self.rows / 2)
        out = []
        for vx, vy in self.scenario.ring:
            dx, dy = vx - cx, vy - cy
            r = math.hypot(dx, dy)
            k = (r + 1.6) / r if level == "aussen" else (r - 2.2) / r
            out.append((cx + dx * k, cy + dy * k))
        return out

    def _around_ring(self, pos: Point, target: Point, level: str) -> Point:
        """Nächster Umwegpunkt auf dem kürzesten Weg über die Eckpunkte (Sichtlinien)."""
        key = (self.cell(*pos), (round(target[0], 1), round(target[1], 1)), level,
               tuple(g.closed for g in self.gates))
        hit = self._ring_cache.get(key)
        if hit is not None:
            return hit
        nodes = self._ring_nodes(level)
        n = len(nodes)
        best = {i: dist(pos, nodes[i]) for i in range(n) if self.wall_clear(pos, nodes[i])}
        if not best:
            wp = min(nodes, key=lambda q: dist(pos, q))
            self._ring_cache[key] = wp
            return wp
        first = {i: i for i in best}
        todo = dict(best)
        done: dict[int, float] = {}
        while todo:
            i = min(todo, key=todo.get)
            d = todo.pop(i)
            done[i] = d
            for j in ((i + 1) % n, (i - 1) % n):          # den Ring entlang, Ecke zu Ecke
                if j in done:
                    continue
                nd = d + dist(nodes[i], nodes[j])
                if nd < todo.get(j, math.inf):
                    todo[j] = nd
                    first[j] = first[i]
        ends = [(done[i] + dist(nodes[i], target), i) for i in done if self.wall_clear(nodes[i], target)]
        if ends:
            _, i = min(ends)
        else:
            i = min(done, key=lambda i: done[i] + dist(nodes[i], target))
        wp = nodes[first[i]]
        if len(self._ring_cache) > 4000:
            self._ring_cache.clear()
        self._ring_cache[key] = wp
        return wp

    # ----------------------------------------------- Wege der Blöcke um Hindernisse
    def _clearance_field(self) -> tuple:
        """Abstand jedes Rasterpunkts (alle halbe Kachel: Kachelmitten und -grenzen) zum nächsten
        Haus, Turm oder Rammbock, in Kacheln; neu, wenn sich das Gerät ändert. Punkte auf dem Rand
        eines Hauses haben den Abstand 0, die Mitte einer Gasse von einer Kachel also 0.5. Den Wall
        regelt die Wegwahl über Tore und Leitern."""
        key = (tuple(g.closed for g in self.gates), self._engines_key)
        if self._clearance is not None and self._clearance[0] == key:
            return self._clearance
        step = 0.5
        nx, ny = int(round(self.cols / step)) + 1, int(round(self.rows / step)) + 1
        dist_ = [math.inf] * (nx * ny)
        blocked: set[int] = set()
        for (cx, cy) in self.house_cells:                       # die Ecken und Kantenmitten jedes Hauses
            for i in range(int(round(cx / step)), int(round((cx + 1) / step)) + 1):
                for j in range(int(round(cy / step)), int(round((cy + 1) / step)) + 1):
                    if 0 <= i < nx and 0 <= j < ny:
                        blocked.add(j * nx + i)
        for (qx, qy) in self._ram_cells | self._tower_cells:    # Gerät auf Viertelkacheln: die Punkte drumherum
            for i in range(int(math.floor(qx / 4 / step)), int(math.ceil((qx + 1) / 4 / step)) + 1):
                for j in range(int(math.floor(qy / 4 / step)), int(math.ceil((qy + 1) / 4 / step)) + 1):
                    if 0 <= i < nx and 0 <= j < ny:
                        blocked.add(j * nx + i)
        heap: list[tuple[float, int]] = []
        for k in blocked:
            dist_[k] = 0.0
            heap.append((0.0, k))
        import heapq
        heapq.heapify(heap)
        diag = math.sqrt(2) * step
        while heap:
            d, k = heapq.heappop(heap)
            if d > dist_[k]:
                continue
            i, j = k % nx, k // nx
            for di, dj, c in ((1, 0, step), (-1, 0, step), (0, 1, step), (0, -1, step),
                              (1, 1, diag), (1, -1, diag), (-1, 1, diag), (-1, -1, diag)):
                i2, j2 = i + di, j + dj
                if 0 <= i2 < nx and 0 <= j2 < ny:
                    k2 = j2 * nx + i2
                    if d + c < dist_[k2]:
                        dist_[k2] = d + c
                        heapq.heappush(heap, (d + c, k2))
        self._clearance = (key, nx, ny, step, dist_)
        self._block_ways.clear()
        return self._clearance

    def _room_at(self, p: Point) -> float:
        """Wie weit es von ``p`` bis zum nächsten Hindernis ist (in Kacheln, eher knapp): der
        beste Abstand der Rasterpunkte ringsum, jeweils abzüglich des Wegs bis dorthin."""
        _, nx, ny, step, dist_ = self._clearance_field()
        i0, j0 = int(math.floor(p[0] / step)), int(math.floor(p[1] / step))
        if not (0 <= i0 < nx and 0 <= j0 < ny):
            return math.inf
        best = 0.0
        for i in (i0, i0 + 1):
            for j in (j0, j0 + 1):
                if i < nx and j < ny:
                    best = max(best, dist_[j * nx + i] - math.hypot(p[0] - i * step, p[1] - j * step))
        return best

    def _wide_clear(self, a: Point, b: Point, r: float) -> bool:
        """Kommt eine Gruppe mit dem halben Querschnitt ``r`` geradeaus von ``a`` nach ``b``?
        Nahe am Anfang und am Ziel darf es enger werden (dort steht man an)."""
        d = dist(a, b)
        n = max(1, int(d / 0.25))
        for k in range(1, n + 1):
            t = k / n
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            if dist(p, a) <= 0.8 or dist(p, b) <= 0.8:
                if self.is_blocked(*p):
                    return False                      # eng darf es werden, hindurch geht es nicht
            elif self._room_at(p) < r:
                return False
        return True

    def _block_width(self, u: Lochos) -> float:
        return min(u.half_w, config.BLOCK_CLEARANCE_MAX) + 0.03

    def _obstacle_way(self, u: Lochos, goal: Point) -> Point:
        """Der nächste Wegpunkt eines Blocks um Häuser und Gerät herum: durch Gassen, in
        die er passt (Breite der Front), sonst außen herum. Gesucht wird auf einem
        Halbkachelraster (A*), der Weg gilt eine Weile."""
        if not self.house_cells and not self._ram_cells and not self._tower_cells:
            return goal
        r = self._block_width(u)
        if self._wide_clear(u.pos, goal, r):
            return goal
        _, nx, ny, step, dist_ = self._clearance_field()
        gkey = (int(goal[0] / step), int(goal[1] / step), round(r, 1))
        hit = self._block_ways.get(u.id)
        if hit is not None and hit[0] == gkey and self.time - hit[1] < config.BLOCK_WAY_TIME:
            path = hit[2]
        else:
            path = self._block_path(u.pos, goal, r)
            self._block_ways[u.id] = (gkey, self.time, path)
        if not path:
            return goal
        best = None
        for p in path[:40]:
            if self._wide_clear(u.pos, p, r):
                best = p
            elif best is not None:
                break
        if best is None:                                  # eng um uns: so weit es geradeaus geht
            best = path[0]
            for p in path[1:8]:
                if not self.path_clear(u.pos, p, u):
                    break
                best = p
        if dist(best, goal) < 0.3:
            return goal
        return best

    def _block_path(self, a: Point, b: Point, r: float) -> list[Point]:
        """A* von ``a`` nach ``b`` über das Halbkachelraster mit mindestens ``r`` Abstand zu
        Hindernissen (Start und Ziel selbst dürfen enger liegen)."""
        import heapq
        _, nx, ny, step, dist_ = self._clearance_field()

        def idx(p: Point) -> int | None:
            i, j = int(round(p[0] / step)), int(round(p[1] / step))
            return j * nx + i if 0 <= i < nx and 0 <= j < ny else None
        inside_b = (min(max(b[0], 0.25), self.cols - 0.25), min(max(b[1], 0.25), self.rows - 0.25))
        s, t = idx(a), idx(inside_b)                  # ein Ziel jenseits des Kartenrands (Flucht): bis an den Rand
        if s is None or t is None:
            return []
        end = b
        if dist_[t] == 0.0:
            # das Ziel liegt im Hindernis (ein Haus, das man plündert): bis an die nächste freie Stelle davor
            ti, tj = t % nx, t // nx
            free = [(abs(di) + abs(dj), (tj + dj) * nx + ti + di) for di in range(-3, 4) for dj in range(-3, 4)
                    if 0 <= ti + di < nx and 0 <= tj + dj < ny and dist_[(tj + dj) * nx + ti + di] > 0.0]
            if not free:
                return []
            t = min(free, key=lambda f: (f[0], dist(a, ((f[1] % nx) * step, (f[1] // nx) * step))))[1]
            end = ((t % nx) * step, (t // nx) * step)
        tx, ty = t % nx, t // nx
        ok = lambda k: dist_[k] >= r or dist_[k] > 0 and (                  # noqa: E731
            abs(k % nx - s % nx) + abs(k // nx - s // nx) <= 2 or abs(k % nx - tx) + abs(k // nx - ty) <= 2)
        g = {s: 0.0}
        prev: dict[int, int] = {}
        heap = [(0.0, s)]
        diag = math.sqrt(2)
        seen = 0
        while heap and seen < config.BLOCK_PATH_LIMIT:
            _, k = heapq.heappop(heap)
            if k == t:
                break
            seen += 1
            i, j = k % nx, k // nx
            for di, dj, c in ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                              (1, 1, diag), (1, -1, diag), (-1, 1, diag), (-1, -1, diag)):
                i2, j2 = i + di, j + dj
                if not (0 <= i2 < nx and 0 <= j2 < ny):
                    continue
                k2 = j2 * nx + i2
                if not ok(k2):
                    continue
                if di and dj and not (ok(j * nx + i2) and ok(j2 * nx + i)):
                    continue
                ng = g[k] + c
                if ng < g.get(k2, math.inf):
                    g[k2] = ng
                    prev[k2] = k
                    heapq.heappush(heap, (ng + math.hypot(i2 - tx, j2 - ty), k2))
        if t not in prev:
            return []
        out = []
        k = t
        while k != s:
            out.append(((k % nx) * step, (k // nx) * step))
            k = prev[k]
        out.reverse()
        out[-1] = end
        return out

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
            g = self._gate_of.get(c)
            if g is not None and g.closed:
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
        """Lücke zwischen zwei Formationen: der kleinste Abstand einer Ecke der
        einen zum Rechteck der anderen (bei aufgelösten Gruppen zwischen den Männern)."""
        if a.loose or b.loose:
            men_a, men_b = a.all_men(), b.all_men()
            if men_a and men_b:
                # erst grob über die Umrisse der Männer: weit auseinander genügt eine untere Schranke
                ax0, ax1 = min(m.x for m in men_a), max(m.x for m in men_a)
                ay0, ay1 = min(m.y for m in men_a), max(m.y for m in men_a)
                bx0, bx1 = min(m.x for m in men_b), max(m.x for m in men_b)
                by0, by1 = min(m.y for m in men_b), max(m.y for m in men_b)
                lower = math.hypot(max(0.0, bx0 - ax1, ax0 - bx1), max(0.0, by0 - ay1, ay0 - by1)) - 0.2
                if lower > config.GAP_EXACT:
                    return lower
                r = config.GAP_EXACT + 0.2
                near_a = [m for m in men_a if bx0 - r <= m.x <= bx1 + r and by0 - r <= m.y <= by1 + r]
                near_b = [n for n in men_b if ax0 - r <= n.x <= ax1 + r and ay0 - r <= n.y <= ay1 + r]
                if not near_a or not near_b:
                    return max(lower, config.GAP_EXACT)
                return max(0.0, min(math.hypot(m.x - n.x, m.y - n.y) for m in near_a for n in near_b) - 0.2)
        return max(0.0, min(min(b.rect_distance(c) for c in a.outline()),
                            min(a.rect_distance(c) for c in b.outline())))

    def _in_contact(self, a: Lochos, b: Lochos, held: bool = False) -> bool:
        """Ob ``a`` gegen ``b`` kämpft: Schild an Schild ab einer kleinen Lücke;
        wer schon im Handgemenge steht, kommt erst mit etwas Abstand wieder los.
        Der Wehrgang ist erhöht: von unten kommt niemand an die Männer oben
        heran, von oben schlägt man hinunter."""
        reach = config.ENGAGE_RANGE + (config.CONTACT_HOLD if held else 0.0)
        if self._gap(a, b) > reach:
            return False
        if self.blocked and (a.loose or b.loose):
            return self._men_meet(a, b, reach + 0.2)
        up_a, up_b = self._fights_from_wall(a), self._fights_from_wall(b)
        if up_b and not up_a:
            return False
        if up_a or up_b:
            return True
        return self.wall_clear(a.pos, b.pos)

    def _men_meet(self, a: Lochos, b: Lochos, reach: float) -> bool:
        """Aufgelöste Gruppen am Wall: Kontakt Mann gegen Mann. Es kämpft, wer einen
        Gegner erreicht (``_hit_weight``)."""
        return any(w > 0.0 for w in self._man_weights(a, b, reach).values())

    def _hit_weight(self, m: Man, walker_m: bool, n: Man, walker_n: bool) -> float:
        """Wie gut ``m`` an ``n`` herankommt: auf derselben Ebene voll; von oben vom Wall
        hinab, oder von unten an einen, der auf der Leiter (dem Turm) steht, nur mit der
        Wucht des Kampfes am Wall; an einen oben auf dem Wehrgang von unten gar nicht."""
        cm, cn = self.cell(m.x, m.y), self.cell(n.x, n.y)
        up_m, up_n = self.is_wall_cell(cm, walker_m), self.is_wall_cell(cn, walker_n)
        if up_m == up_n:
            if up_m:
                return 1.0
            lm, ln = self._wall_level(m.pos), self._wall_level(n.pos)
            return 1.0 if lm == ln or "tor" in (lm, ln) else 0.0
        if up_m:
            return config.WALL_MELEE_FACTOR
        return config.WALL_MELEE_FACTOR if cn in self.ladders or cn in self.crossings else 0.0

    def _reachable_men(self, a: Lochos, b: Lochos, men: list[Man], reach: float) -> list[Man]:
        """Die Männer aus ``men`` (von ``b``), an die ein Mann von ``a`` herankommt."""
        walker_a, walker_b = self.is_walker(a), self.is_walker(b)
        attackers = a.all_men()
        return [n for n in men if any(math.hypot(m.x - n.x, m.y - n.y) <= reach
                                      and self._hit_weight(m, walker_a, n, walker_b) > 0.0 for m in attackers)]

    def _man_weights(self, a: Lochos, b: Lochos, reach: float) -> dict[int, float]:
        """Für jeden Mann von ``a``, der einen Gegner aus ``b`` in Reichweite hat: wie gut
        er an ihn herankommt (der beste in Reichweite)."""
        men_b = b.all_men()
        if not men_b:
            return {}
        walker_a, walker_b = self.is_walker(a), self.is_walker(b)
        bx0, bx1 = min(n.x for n in men_b) - reach, max(n.x for n in men_b) + reach
        by0, by1 = min(n.y for n in men_b) - reach, max(n.y for n in men_b) + reach
        out: dict[int, float] = {}
        for m in a.all_men():
            if not (bx0 <= m.x <= bx1 and by0 <= m.y <= by1):
                continue
            best = -1.0
            for n in men_b:
                if math.hypot(m.x - n.x, m.y - n.y) <= reach:
                    best = max(best, self._hit_weight(m, walker_a, n, walker_b))
                    if best >= 1.0:
                        break
            if best >= 0.0:
                out[id(m)] = best
        return out

    # ----------------------------------------------------------- Befehle
    def _selection(self, units: list[Lochos] | None) -> list[Lochos]:
        pool = self.units(Side.STADT, fighting_only=True)
        if not units:
            return pool
        ids = {u.id for u in units}
        return [u for u in pool if u.id in ids]

    def _wake(self, u: Lochos) -> None:
        u.stay_loose = False                      # ein neuer Befehl: wieder als Block, wo es geht
        u.pace = None                             # ein neuer Befehl: das Tempo des Verbands gilt nicht mehr
        u.free_attack = False
        u.stormed = False
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
            if not self.is_wall_cell(self.cell(*u.target), self.is_walker(u)):
                want = u.target
                for _ in range(3):
                    # die Gruppe soll ganz neben Haus und Nachbarn passen, mit der Front, mit der sie
                    # ankommt (in Marschrichtung zum verrückten Platz, nicht zum getippten)
                    way = sub(u.target, u.pos)
                    facing = norm(way) if math.hypot(*way) > 0.5 else u.facing
                    spot = self._fit_spot(u, want, facing)
                    if dist(spot, u.target) < 0.05:
                        break
                    u.target = spot
            if self._cut_off(u, u.target):
                if self.is_walker(u):
                    u.target = self._wall_spot_near(u.target)       # hinab geht es nur nach innen: oben stehen bleiben
                    self.events.append(f"{u.name}: kein Weg hinab nach draußen, auf den Wehrgang darüber")
                else:
                    self.events.append(f"{u.name}: das Tor ist zu, sie warten davor")
        self.events.append(f"{len(sel)} Gruppe(n) unterwegs")

    def _cut_off(self, u: Lochos, p: Point) -> bool:
        """Liegt ``p`` jenseits des Walls, und kommt die Gruppe nicht hinüber? Alle Tore
        zu, kein Turm für sie, und die Leitern führen nur zur Innenseite hinab."""
        if not self.blocked or any(not g.closed for g in self.gates):
            return False
        here, there = self._wall_level(u.pos), self._wall_level(p)
        if here == there or {here, there} & {"wall", "tor"}:
            return False
        if not self.is_walker(u):
            return True
        if self.crossings and u.side is not self.wall_side():
            return False                                    # über den eigenen Turm von außen hinein
        if self.ring:
            return there != "innen"
        for lc in self.ladders:
            for side in (-1, 1):
                ground = (lc[0], lc[1] + side)
                if self.ladder_ok(lc, ground) and self._wall_level((ground[0] + 0.5, ground[1] + 0.5)) == there:
                    return False
        return True

    def _wall_spot_near(self, p: Point) -> Point:
        """Die Mitte des Wallstücks (Wehrgang), das ``p`` am nächsten liegt."""
        cells = [c for c in self.blocked if c not in self._gate_of]
        if not cells:
            return p
        c = min(cells, key=lambda c: (c[0] + 0.5 - p[0]) ** 2 + (c[1] + 0.5 - p[1]) ** 2)
        return (c[0] + 0.5, c[1] + 0.5)

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
        self._settle(u)
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
                g.free_attack = True                  # im Verband: nach dem Kampf zurück an den Platz
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
            self._settle(u)                       # aufgelöst: dort schließen, wo die Männer stehen
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

    def command_drill(self, units: list[Lochos] | None, name: str) -> int:
        """Modus der Hopliten setzen: locker oder Phalanx. Wer steht, bildet mit Phalanx
        an Ort und Stelle die Formation (wie „Halten“); wer
        unterwegs ist, marschiert im neuen Modus weiter. Andere Gattungen kennen keine Modi."""
        if name not in config.DRILLS:
            return 0
        self.alarm = False
        changed = 0
        for u in self._selection(units):
            if u.arm() != "hopliten" or self.on_wall(u):
                continue
            was = u.drill
            u.drill = name
            if u.stance is Stance.ANGRIFF and u.target_id is None:
                u.stance = Stance.HALTEN              # Sturm vorbei: der neue Modus gilt ab hier
                u.target = None
            if name != "locker" and u.target is None and not u.engaged:
                self._settle(u)
                u.stance = Stance.PHALANX
                u.target = u.pos
            if was != name:
                u.in_line = False                     # neue Abstände: die Männer rücken an ihre Plätze
                changed += 1
        if changed:
            self.events.append(f"Modus: {config.DRILL_NAMES[name]}")
        return changed

    def command_formation(self, units: list[Lochos] | None, name: str) -> int:
        """Formation der gewählten Gruppen setzen, wenn ihre Waffengattung sie kennt."""
        changed = 0
        for u in self._selection(units):
            if name in u.formation_options() and u.formation != name:
                u.formation = name
                u.ring_size = 0.0
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

    def command_ram_gate(self, units: list[Lochos] | None, gate: Gate | None = None) -> int:
        """Gruppen mit Rammbock gehen ans Tor und brechen es auf."""
        if self.ring:
            return self._ram_gate_ring(units, gate)
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
            u.face_to = (0.0, -side)
        self.events.append("Rammbock geht ans Tor")
        return len(sel)

    def _ram_gate_ring(self, units: list[Lochos] | None, gate: Gate | None) -> int:
        sel = [u for u in self._selection(units) if u.engine == "ram"]
        if not sel:
            self.events.append("Ohne Rammbock hält das Tor")
            return 0
        if gate is None:
            closed = [g for g in self.gates if g.closed]
            if not closed:
                return 0
            cx = sum(u.x for u in sel) / len(sel)
            cy = sum(u.y for u in sel) / len(sel)
            gate = min(closed, key=lambda g: dist((cx, cy), g.center))
        if not gate.closed:
            return 0
        self.alarm = False
        for i, u in enumerate(sel):
            self.drive_ram(u, gate, (i - (len(sel) - 1) / 2) * 0.8)
        self.events.append("Rammbock geht ans Tor")
        return len(sel)

    def drive_ram(self, u: Lochos, gate: Gate, offset: float = 0.0) -> None:
        """Die Gruppe fährt den Rammbock von außen vor das Tor, die Front zum Tor."""
        cx, cy = gate.center
        (nx, ny), (tx, ty) = gate.normal, gate.tangent
        d = gate.half_thick + u.half_d + 0.35
        u.stance = Stance.HALTEN
        u.in_line = False
        u.target_id = None
        u.ram_gate = self.gates.index(gate)
        u.target = (cx + nx * d + tx * offset, cy + ny * d + ty * offset)
        u.face_to = (-nx, -ny)

    def command_tower_wall(self, units: list[Lochos] | None, cell: tuple[int, int]) -> int:
        """Gruppen mit Turm setzen ihn an dieses Wallstück."""
        if self.ring:
            return self._tower_wall_ring(units, cell)
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
            u.face_to = (0.0, -side)
        self.events.append("Belagerungsturm rollt an den Wall")
        return len(sel)

    def _tower_wall_ring(self, units: list[Lochos] | None, cell: tuple[int, int]) -> int:
        if cell not in self.blocked or cell in self.crossings:
            return 0
        if self.tower_step(cell) is None:
            # dicke Stelle an einer Schräge: das nächste Wallstück, an das der Turm von außen kommt
            near = [c for c in self.blocked if c not in self.crossings and self.tower_step(c) is not None
                    and abs(c[0] - cell[0]) <= 1 and abs(c[1] - cell[1]) <= 1]
            if not near:
                return 0
            cell = min(near, key=lambda c: abs(c[0] - cell[0]) + abs(c[1] - cell[1]))
        sel = [u for u in self._selection(units) if u.engine == "tower"]
        if not sel:
            self.events.append("Ohne Belagerungsturm ist der Wall zu hoch")
            return 0
        self.alarm = False
        for u in sel:
            self.drive_tower(u, cell)
        self.events.append("Belagerungsturm rollt an den Wall")
        return len(sel)

    def landing(self, cell: tuple[int, int]) -> Point | None:
        """Festung: der Platz auf dem Wehrgang gleich neben einem Turmübergang, wo die
        Verteidiger den Ausstieg abriegeln."""
        parts = self._walkway_parts()
        near = [n for n in ((cell[0] + 1, cell[1]), (cell[0] - 1, cell[1]), (cell[0], cell[1] + 1), (cell[0], cell[1] - 1))
                if n in parts and n not in self.crossings and n not in self.ladders]
        if not near:
            return None
        c = near[0]
        return (c[0] + 0.5, c[1] + 0.5)

    def tower_step(self, cell: tuple[int, int]) -> tuple[int, int] | None:
        """Festung: von welcher Seite (dx, dy) ein Turm an dieses Wallstück kommt, oder None,
        wenn es außen keinen Boden daneben gibt (dicke Stelle an einer Schräge)."""
        d = self._ground_step(cell, "aussen")
        n = (cell[0] + d[0], cell[1] + d[1])
        if n in self.blocked or n in self._gate_of or self._cell_level(n) != "aussen":
            return None
        return d

    def drive_tower(self, u: Lochos, cell: tuple[int, int]) -> None:
        """Die Gruppe fährt den Turm von außen an das Wallstück, die Front zum Wall."""
        dx, dy = self.tower_step(cell) or (0, -1)
        cx, cy = cell[0] + 0.5, cell[1] + 0.5
        u.stance = Stance.HALTEN
        u.in_line = False
        u.target_id = None
        u.tower_cell = cell
        u.tower_progress = 0.0
        u.target = (cx + dx * (0.5 + u.half_d + 0.3), cy + dy * (0.5 + u.half_d + 0.3))
        u.face_to = (float(-dx), float(-dy))

    def plan_line(self, units: list[Lochos] | None, start: Point, end: Point) -> list[LinePlan]:
        """Aufstellung entlang einer gezogenen Linie. Gruppen einer Gattung stehen
        nebeneinander; gemischt gilt die Schlachtordnung (``_battle_order``)."""
        sel = self._selection(units)
        if not sel or dist(start, end) < 0.3:
            return []
        if self.in_battle_order(sel):
            return self._battle_order(sel, start, end)
        return self._plan_row(sel, start, end)

    @staticmethod
    def in_battle_order(sel: list[Lochos]) -> bool:
        """Gemischte Gattungen (mit Fußvolk) stellen sich in Schlachtordnung auf."""
        arms = {u.arm() for u in sel}
        return len(arms) > 1 and arms != {"reiter"}

    def _plan_row(self, sel: list[Lochos], start: Point, end: Point) -> list[LinePlan]:
        """Die Gruppen teilen sich die Linie nach ihrer Mannzahl, von links nach rechts
        so, wie sie gerade stehen; die Länge bestimmt die Breite."""
        d = sub(end, start)
        length = dist(start, end)
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
            width = max(1, min(u.men, int(seg / u.man_gap())))
            depth = math.ceil(u.men / width)
            center = add(start, scale(axis, pos + seg / 2))
            plans.append(LinePlan(u.id, self._free_spot(center, u), facing, width, depth, seg))
            pos += seg + gap
        return plans

    def _battle_order(self, sel: list[Lochos], start: Point, end: Point) -> list[LinePlan]:
        """Schlachtordnung für gemischte Gruppen: Hopliten vorn auf der Linie, die
        Peltasten als zweites Treffen dicht dahinter (sie werfen über die Köpfe), die
        Reiter an den Flügeln, zuerst rechts, an der schildlosen Seite der Phalanx.
        Ohne Hopliten stehen die Peltasten vorn."""
        axis = norm(sub(end, start))
        facing = (axis[1], -axis[0])
        back = (-facing[0], -facing[1])
        by_arm: dict[str, list[Lochos]] = {"hopliten": [], "peltasten": [], "reiter": []}
        for u in sel:
            by_arm[u.arm()].append(u)
        front = by_arm["hopliten"] or by_arm["peltasten"]
        second = by_arm["peltasten"] if by_arm["hopliten"] else []
        plans = self._plan_row(front, start, end)
        gaps = {u.id: (u.man_gap(), u.row_gap()) for u in sel}
        front_half = max(p.depth * gaps[p.unit_id][1] for p in plans) / 2
        if second:
            # etwas kürzer als die Front, damit die Enden der Phalanx frei bleiben
            length = dist(start, end)
            trim = length * (1 - config.ORDER_SECOND_SHARE) / 2
            a, b = add(start, scale(axis, trim)), add(end, scale(axis, -trim))
            row = self._plan_row(second, a, b)
            half = max(p.depth * gaps[p.unit_id][1] for p in row) / 2
            shift = scale(back, front_half + config.ORDER_SECOND_GAP + half)
            plans += [LinePlan(p.unit_id, self._free_spot(add(p.center, shift), self.by_id(p.unit_id)),
                               p.facing, p.width, p.depth, p.length) for p in row]
        # Reiter: abwechselnd rechts und links neben die Front, die Fronten bündig
        mid = scale(add(start, end), 0.5)
        along_of = [(p.center[0] - mid[0]) * axis[0] + (p.center[1] - mid[1]) * axis[1] for p in plans[:len(front)]]
        halves = [p.width * gaps[p.unit_id][0] / 2 for p in plans[:len(front)]]
        edges = {1: max(a + h for a, h in zip(along_of, halves)) + config.ORDER_WING_GAP,
                 -1: -min(a - h for a, h in zip(along_of, halves)) + config.ORDER_WING_GAP}
        for k, u in enumerate(sorted(by_arm["reiter"], key=lambda u: -u.men)):
            width = max(1, math.ceil(u.men / config.ORDER_WING_DEPTH))
            depth = math.ceil(u.men / width)
            half_w = width * config.MAN_SPACING / 2
            half_d = depth * config.ROW_SPACING / 2
            for side in ((1, -1) if k % 2 == 0 else (-1, 1)):
                along = edges[side] + half_w
                c = add(add(mid, scale(axis, side * along)), scale(back, half_d - front_half))
                outer = add(c, scale(axis, side * half_w))
                if self.inside(*outer):
                    break
            edges[side] = along + half_w + config.ORDER_WING_GAP
            plans.append(LinePlan(u.id, self._free_spot(c, u), facing, width, depth, 2 * half_w))
        return plans

    def ring_radius_for(self, u: Lochos, wanted: float) -> float:
        return max(u.ring_minimum(), min(config.RING_MAX, wanted))

    def command_ring(self, units: list[Lochos] | None, centre: Point, radius: float) -> int:
        """Kreis ziehen: Mitte am Anfang des Zugs, Halbmesser aus seiner Länge (nie
        enger, als die Männer Platz brauchen). Die Gruppen stehen dann im Kreis fest."""
        self.alarm = False
        sel = [u for u in self._selection(units) if u.formation == "o"]
        for u in sel:
            self._wake(u)
            u.ring_size = self.ring_radius_for(u, radius)
            u.mode = ""
            u.stance = Stance.PHALANX
            u.in_line = False
            u.target_id = None
            u.waypoints = []
            u.target = self._free_spot(centre, u)
        if sel:
            self.events.append(f"Kreis mit Halbmesser {sel[0].ring_size:.1f}")
        return len(sel)

    def command_line(self, units: list[Lochos] | None, start: Point, end: Point) -> list[LinePlan]:
        self.alarm = False
        plans = self.plan_line(units, start, end)
        for plan in plans:
            u = self.by_id(plan.unit_id)
            if u is not None:
                self._take_plan(u, plan, own=False)   # gezogen: genau dort, nur nicht im Haus
        self.line = plans
        if plans:
            what = "Schlachtordnung" if self.in_battle_order(self._selection(units)) else "Aufstellung"
            self.events.append(f"{what}: {len(plans)} Gruppe(n), Front {self._dir_name(snap4(plans[0].facing))}")
        return plans

    def _fit_spot(self, u: Lochos, centre: Point, facing: Point, width: int | None = None,
                  ignore: set[int] | None = None) -> Point:
        return self._fit(u, centre, facing, width, ignore)[0]

    def _fit(self, u: Lochos, centre: Point, facing: Point, width: int | None = None,
             ignore: set[int] | None = None, own: bool = True) -> tuple[Point, bool]:
        """Die Aufstellung so weit verrücken (höchstens 2,5 Kacheln), dass kein Platz in einem
        Haus, im Wall, außerhalb der Karte oder in einer anderen stehenden eigenen Gruppe liegt
        (``ignore``: Gruppen, die ohnehin gleich weggehen); sonst stünden dort Männer daneben,
        und die Phalanx schlösse sich nie."""
        if u.formation != "linie":
            return centre, True
        skip = (ignore or set()) | {u.id}
        others = []                                       # (Gruppe, Versatz): wo sie steht oder gleich stehen wird
        in_place = dist(u.pos, centre) <= u.radius        # an Ort und Stelle drehen oder umformen: nur Haus und Wall zählen
        for o in (self.lochoi if own and not in_place else []):
            if o.id in skip or not o.alive or o.side is not u.side or self.on_wall(o) != self.on_wall(u):
                continue
            if o.target is not None and o.target_id is None and not self._standing(o):
                others.append((o, sub(o.pos, o.target)))  # unterwegs: ihr Ziel ist belegt
            elif not o.loose and self._standing(o):
                others.append((o, (0.0, 0.0)))
        width = max(1, min(u.men, width or u.width or 1))
        depth = max(1, math.ceil(u.men / width))
        gap, rows = u.man_gap(), u.row_gap()
        fx, fy = facing
        ax, ay = -fy, fx
        cols = sorted({0, width - 1, *range(0, width, 2)})
        pts = [((i - (width - 1) / 2) * gap, ((depth - 1) / 2 - r) * rows) for r in range(depth) for i in cols]

        reach = max(width * gap, depth * rows)
        near = [(o, off) for o, off in others if dist(sub(o.pos, off), centre) <= o.radius + reach + 2.6]

        def free(c: Point) -> bool:
            for side, fwd in pts:
                x, y = c[0] + ax * side + fx * fwd, c[1] + ay * side + fy * fwd
                if not self.inside(x, y) or self.is_blocked(x, y, u):
                    return False
                if any(o.rect_distance((x + off[0], y + off[1])) < 0.1 for o, off in near):
                    return False
            return True
        if free(centre):
            return centre, True
        level = self._wall_level(centre) if self.blocked else None
        for k in range(1, 11):
            r = 0.25 * k
            for j in range(16):
                a = 2 * math.pi * j / 16
                c = (centre[0] + math.cos(a) * r, centre[1] + math.sin(a) * r)
                if (level is None or self._wall_level(c) == level) and free(c):
                    return c, True
        return centre, False

    def _take_plan(self, u: Lochos, plan: LinePlan, ignore: set[int] | None = None, own: bool = True) -> None:
        """Eine Gruppe stellt sich wie geplant auf (Mitte, Front, Breite)."""
        if not u.engaged and not self.on_wall(u) and not self.is_wall_cell(self.cell(*plan.center), self.is_walker(u)):
            # nicht halb im Haus oder in anderen; passt die Breite nirgends, schmaler und tiefer
            # (im Handgemenge bleibt die Aufstellung, wo sie ist)
            for w in (plan.width, max(1, round(plan.width * 0.7)), max(1, round(plan.width * 0.5))):
                c, ok = self._fit(u, plan.center, plan.facing, w, ignore, own)
                if ok:
                    if w != plan.width:
                        plan.width, plan.depth = w, math.ceil(u.men / w)
                    plan.center = c
                    break
        self._wake(u)
        u.formation = "linie"
        u.full_width = None
        u.ring_size = 0.0
        u.mode = ""
        u.stance = Stance.PHALANX
        u.in_line = False
        u.target = plan.center
        u.target_id = None
        u.waypoints = []
        if config.MARCH_ARC and not u.loose and dist(u.pos, plan.center) > config.MARCH_MIN:
            u.march = (plan.center, plan.width, plan.facing)   # erst hin, kurz vor dem Ziel aufmarschieren
            u.face_to = None
        else:
            u.march = None
            u.reform(plan.width)
            u.face_to = plan.facing              # die Front schwenkt mit begrenzter Rate dorthin

    # -- Verbände ----------------------------------------------------------
    def verband_of(self, u: Lochos | int | None) -> Verband | None:
        uid = u.id if isinstance(u, Lochos) else u
        return next((v for v in self.verbaende if uid in v.members()), None)

    def selected_verband(self, ids: set[int] | None) -> Verband | None:
        """Der Verband, dessen (kämpfende) Gruppen genau die Auswahl sind."""
        if not ids or len(ids) < 2:
            return None
        for v in self.verbaende:
            mine = {uid for uid in v.members() if (u := self.by_id(uid)) is not None and u.fighting}
            if mine == set(ids):
                return v
        return None

    def verband_units(self, v: Verband, fighting: bool = True) -> list[list[Lochos]]:
        """Die Reihen eines Verbands als Gruppen (nur lebende, ``fighting``: nur kämpfende)."""
        out = []
        for row in v.rows:
            us = [u for uid in row if (u := self.by_id(uid)) is not None and (u.fighting if fighting else u.alive)]
            if us:
                out.append(us)
        return out

    def _new_verband(self, units: list[Lochos], name: str = "") -> Verband:
        for u in units:
            self._leave_verband(u, quiet=True)
        v = Verband(self._next_vid, name or f"Verband {self._next_vid}", self._default_rows(units))
        self._next_vid += 1
        front = max(units, key=lambda u: (u.arm() == "hopliten", u.men))
        v.facing = front.facing
        self.verbaende.append(v)
        return v

    @staticmethod
    def _default_rows(units: list[Lochos]) -> list[list[int]]:
        """Schlachtordnung als Anfang: Hopliten vorn, die Peltasten dahinter, die Reiter an den
        Flügeln der vorderen Reihe (die größte rechts, dann links). Ohne Hopliten stehen die
        Peltasten vorn; reine Reiter nebeneinander."""
        by_arm: dict[str, list[Lochos]] = {"hopliten": [], "peltasten": [], "reiter": []}
        for u in units:
            by_arm[u.arm()].append(u)
        front = by_arm["hopliten"] or by_arm["peltasten"]
        second = by_arm["peltasten"] if by_arm["hopliten"] else []
        ref = max(front or by_arm["reiter"], key=lambda u: u.men)
        fx, fy = ref.facing

        def along(u: Lochos) -> float:
            return u.x * -fy + u.y * fx
        if not front:
            return [[u.id for u in sorted(by_arm["reiter"], key=along)]]
        row = [u.id for u in sorted(front, key=along)]
        for k, u in enumerate(sorted(by_arm["reiter"], key=lambda u: -u.men)):
            if k % 2 == 0:
                row.append(u.id)                  # rechts, an der schildlosen Seite
            else:
                row.insert(0, u.id)
        rows = [row]
        if second:
            rows.append([u.id for u in sorted(second, key=along)])
        return rows

    def _verband_anchor(self, units: list[Lochos]) -> tuple[Point, float]:
        """Wo ein Verband aus diesen Gruppen ungefähr steht: Mitte der Gruppen (nach Mannzahl)."""
        total = sum(u.men for u in units) or 1
        c = (sum(u.x * u.men for u in units) / total, sum(u.y * u.men for u in units) / total)
        return c, 0.0

    def _leave_verband(self, u: Lochos, quiet: bool = False) -> None:
        v = self.verband_of(u)
        if v is None:
            return
        v.rows = [[uid for uid in row if uid != u.id] for row in v.rows]
        v.rows = [row for row in v.rows if row]
        v.slots.pop(u.id, None)
        if not quiet:
            self.events.append(f"{u.name} verlässt {v.name}")
        if len(v.members()) < 2:
            self.verbaende.remove(v)

    def _tidy_verbaende(self) -> None:
        """Gefallene und vom Feld gegangene Gruppen verlassen ihren Verband; mit weniger als
        zwei Gruppen ist er keiner mehr."""
        for v in list(self.verbaende):
            rows = [[uid for uid in row if (u := self.by_id(uid)) is not None and u.alive] for row in v.rows]
            v.rows = [row for row in rows if row]
            if len(v.members()) < 2:
                self.verbaende.remove(v)

    def command_verband(self, units: list[Lochos] | None) -> Verband | None:
        """Die gewählten Gruppen bilden einen Verband (Schlachtordnung) und stellen sich gleich
        dort auf, wo sie stehen."""
        sel = [u for u in self._selection(units)
               if not self.on_wall(u) and u.engine is None and u.building is None]
        if len(sel) < 2:
            return None
        self.alarm = False
        v = self._new_verband(sel)
        centre, _ = self._verband_anchor(sel)
        self._form_verband(v, centre, v.facing, None)
        self.events.append(f"{v.name}: {len(sel)} Gruppen in einer Formation")
        return v

    def command_dissolve_verband(self, v: Verband | None) -> None:
        if v is None or v not in self.verbaende:
            return
        self.verbaende.remove(v)
        self.events.append(f"{v.name} aufgelöst: die Gruppen handeln wieder einzeln")

    def command_leave_verband(self, units: list[Lochos] | None) -> int:
        n = 0
        for u in self._selection(units):
            if self.verband_of(u) is not None:
                self._leave_verband(u)
                n += 1
        return n

    def set_verband_rows(self, v: Verband, rows: list[list[int]]) -> None:
        """Neue Anordnung (vorn nach hinten, links nach rechts); der Verband stellt sich dort
        neu auf, wo er steht."""
        known = set(v.members())
        rows = [[uid for uid in row if uid in known] for row in rows]
        rows = [row for row in rows if row]
        missing = [uid for uid in v.members() if uid not in {x for row in rows for x in row}]
        if missing:
            rows.append(missing)
        v.rows = rows
        self._form_verband(v, v.centre, v.facing, v.length)

    def command_verband_move(self, v: Verband, point: Point) -> None:
        """Der Verband marschiert dorthin: die vordere Reihe (der Kreis) mit ihrer Mitte an den
        Punkt, die Front in Marschrichtung."""
        self.alarm = False
        here = v.centre or self._verband_anchor([u for row in self.verband_units(v) for u in row])[0]
        facing = v.facing
        if dist(here, point) > 0.5:
            facing = norm(sub(point, here))
        self._form_verband(v, point, facing, v.length)
        self.events.append(f"{v.name} marschiert")

    def command_verband_line(self, v: Verband, start: Point, end: Point) -> None:
        """Front des Verbands aufziehen: die vordere Reihe auf der Linie, die anderen dahinter.
        Im Kreis: Mitte am Anfang des Zugs."""
        self.alarm = False
        if v.formation == "o":
            self._form_verband(v, start, v.facing, v.length)
            return
        axis = norm(sub(end, start))
        facing = (axis[1], -axis[0])
        self._form_verband(v, scale(add(start, end), 0.5), facing, dist(start, end))
        self.events.append(f"{v.name}: Front {self._dir_name(snap4(facing))}")

    def command_verband_formation(self, v: Verband, name: str) -> None:
        if name not in ("linie", "o") or v.formation == name:
            return
        v.formation = name
        units = [u for row in self.verband_units(v) for u in row]
        centre = self._verband_anchor(units)[0] if name == "o" else v.centre
        self._form_verband(v, centre, v.facing, v.length)
        self.events.append(f"{v.name}: {'Kreis, Ring in Ring' if name == 'o' else 'Linie'}")

    def verband_plans(self, v: Verband, centre: Point, facing: Point, length: float | None) -> list[LinePlan]:
        """Plätze der Gruppen eines Verbands in Linie: die vordere Reihe mit ihrer Mitte bei
        ``centre`` (Front ``facing``, Länge ``length``), jede weitere dicht dahinter. In einer
        Reihe stehen die Gruppen nebeneinander, die Fronten bündig; Reiter drei Glieder tief,
        die anderen teilen sich den Rest nach Mannzahl."""
        rows = self.verband_units(v)
        if not rows:
            return []
        fx, fy = facing
        axis = (-fy, fx)                                   # nach rechts, wie die Front schaut
        back = (-fx, -fy)
        if length is None:
            length = sum(u.width * u.man_gap() + 0.3 for u in rows[0])
        plans: list[LinePlan] = []
        front_line = centre                                # Mitte der vorderen Kante der Reihe
        for r, row in enumerate(rows):
            row_len = length if r == 0 else length * config.ORDER_SECOND_SHARE
            gap = 0.3
            cav = [u for u in row if u.arm() == "reiter"]
            cav_w = {u.id: max(1, math.ceil(u.men / config.ORDER_WING_DEPTH)) for u in cav}
            rest = [u for u in row if u not in cav]
            cav_len = sum(cav_w[u.id] * u.man_gap() for u in cav)
            share = max(0.3 * len(rest), row_len - cav_len - gap * (len(row) - 1))
            total = sum(u.men for u in rest) or 1
            widths = {}
            for u in row:
                if u in cav:
                    widths[u.id] = cav_w[u.id]
                else:
                    widths[u.id] = max(1, min(u.men, int(share * u.men / total / u.man_gap())))
            segs = [widths[u.id] * u.man_gap() for u in row]
            span = sum(segs) + gap * (len(row) - 1)
            pos = -span / 2
            deepest = 0.0
            for u, seg in zip(row, segs):
                w = widths[u.id]
                depth = math.ceil(u.men / w)
                half_d = depth * u.row_gap() / 2
                c = add(add(front_line, scale(axis, pos + seg / 2)), scale(back, half_d))
                plans.append(LinePlan(u.id, self._free_spot(c, u), facing, w, depth, seg))
                deepest = max(deepest, 2 * half_d)
                pos += seg + gap
            front_line = add(front_line, scale(back, deepest + config.ORDER_SECOND_GAP))
        return plans

    def _form_verband(self, v: Verband, centre: Point | None, facing: Point, length: float | None,
                      quiet: bool = False) -> None:
        """Alle Gruppen des Verbands an ihre Plätze, im Tempo der langsamsten."""
        units = [u for row in self.verband_units(v) for u in row]
        if not units:
            return
        if centre is None:
            centre = self._verband_anchor(units)[0]
        pace = min(u.speed for u in units)
        v.facing = facing
        v.slots = {}
        if v.formation == "o":
            v.centre = centre
            radius = 0.0
            for u in reversed(units):                      # von innen nach außen: die vordere Reihe außen
                self._wake(u)
                u.formation = "o"
                r = max(u.ring_minimum(), radius + (config.ROW_SPACING + 0.05 if radius else 0.0))
                u.ring_size = r
                u.full_width = None
                u.mode = ""
                u.in_line = False
                u.march = None
                u.face_to = None
                u.target_id = None
                u.waypoints = []
                u.pace = pace
                v.slots[u.id] = (centre, r)
                radius = r + u.row_gap() / 2
                u.stance = Stance.PHALANX
                u.target = centre                          # alle Ringe um dieselbe Mitte
            return
        plans = self.verband_plans(v, centre, facing, length)
        v.centre = centre
        v.length = length if length is not None else sum(p.length for p in plans if p.unit_id in v.rows[0]) or None
        members = set(v.members())
        for plan in plans:
            u = self.by_id(plan.unit_id)
            if u is None:
                continue
            self._take_plan(u, plan, members)
            u.pace = pace
            v.slots[u.id] = plan
        if not quiet:
            self.line = plans

    def _return_to_slot(self, v: Verband, u: Lochos) -> None:
        slot = v.slots.get(u.id)
        if slot is None:
            return
        if isinstance(slot, LinePlan):
            self._take_plan(u, slot)
        else:
            centre, r = slot
            self._wake(u)
            u.formation, u.ring_size, u.stance, u.in_line = "o", r, Stance.PHALANX, False
            u.mode, u.target_id, u.target, u.march = "", None, centre, None
        self.events.append(f"{u.name} kehrt in {v.name} zurück")

    def _nested(self, u: Lochos, o: Lochos) -> bool:
        """Zwei Ringe desselben Verbands: sie stehen gewollt ineinander."""
        if not self.verbaende or u.formation != "o" or o.formation != "o":
            return False
        v = self.verband_of(u)
        return v is not None and v.formation == "o" and o.id in v.members()

    def _verband_ring(self, u: Lochos) -> bool:
        """Steht die Gruppe als Ring in einem Verband (Ringe um dieselbe Mitte)?"""
        if u.formation != "o" or not self.verbaende:
            return False
        v = self.verband_of(u)
        return v is not None and v.formation == "o"

    def _verband_upkeep(self) -> None:
        """Wer aus dem Verband heraus frei angegriffen hat, kehrt an seinen Platz zurück,
        sobald kein kämpfender Feind mehr in der Nähe ist (der Gegner flieht oder ist tot)."""
        self._tidy_verbaende()
        self._ring_friends = {}
        for v in self.verbaende:
            if v.formation == "o":
                ids = set(v.members())
                for uid in ids:
                    self._ring_friends[uid] = ids
        if not self.verbaende:
            return
        foes = [f for f in self.lochoi if f.side is Side.FEIND and f.fighting]
        for v in self.verbaende:
            for uid in v.members():
                u = self.by_id(uid)
                if u is None or not u.fighting or not u.free_attack:
                    continue
                if u.engaged:
                    u.stormed = True
                    continue
                if not u.stormed:
                    continue
                if any(f.rect_distance(u.pos) <= config.VERBAND_RETURN for f in foes):
                    continue
                self._return_to_slot(v, u)

    def _free_spot(self, p: Point, unit: Lochos | None = None) -> Point:
        x = min(max(p[0], 0.5), self.cols - 0.5)
        y = min(max(p[1], 0.5), self.rows - 0.5)
        if self.ring and self.is_blocked(x, y, unit):
            # auf dem Wall oder im Tor: daneben auf die Seite, auf der die Gruppe steht
            level = self._wall_level(unit.pos) if unit is not None else None
            for r in (0.8, 1.3, 1.8, 2.5):
                for k in range(8):
                    a = k * math.pi / 4
                    q = (x + math.cos(a) * r, y + math.sin(a) * r)
                    if (self.inside(*q) and not self.is_blocked(*q, unit)
                            and (level not in ("innen", "aussen") or self._wall_level(q) == level)):
                        return q
            return (x, y)
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
        if (len(self.towers), len(self.debris)) != self._engines_key:
            self._mark_engines()
        if self.attacking:
            self._ai_defenders()
        else:
            self._ai_raiders()
        self._ai_city()
        self._verband_upkeep()
        self._skirmishers()
        before = [(m, m.x, m.y) for u in self.lochoi if u.alive for m in u.all_men()]
        self._move(dt)
        self._separate()
        self._track_motion(before, dt)
        self._combat(dt)
        self._volleys(dt)
        if self.corner_towers:
            self._tower_fire(dt)
        self._engines(dt)
        if not self.attacking:
            self._loot(dt)
        self._morale(dt)
        self._check_withdraw()
        self._check_outcome()
        self._show(dt)

    def _mark_engines(self) -> None:
        """Aufgestellte Türme und liegende Rammböcke als Hindernisse (Viertelkacheln)."""
        self._engines_key = (len(self.towers), len(self.debris))
        self._tower_cells = set()
        for x, y in self.towers:
            for qx in range(math.floor((x - 0.35) * 4), math.floor((x + 0.35) * 4) + 1):
                for qy in range(math.floor((y - 0.35) * 4), math.floor((y + 0.35) * 4) + 1):
                    self._tower_cells.add((qx, qy))
        self._ram_cells = set()
        for x, y, fx, fy in self.debris:
            for k in range(-2, 3):
                px_, py_ = x + fx * 0.125 * k, y + fy * 0.125 * k
                self._ram_cells.add((math.floor(px_ * 4), math.floor(py_ * 4)))

    # -- Bild --------------------------------------------------------------
    def _show(self, dt: float) -> None:
        """Nur fürs Bild, die Schlacht rechnet nichts davon: Getroffene blitzen auf,
        wo einer fiel, bleibt kurz ein Fleck, und im Handgemenge drängen die Männer
        sichtbar an ihren Gegner (Gerangel). Wer gebunden ist, tritt an seinen
        Gegner heran; wer in einer kämpfenden Gruppe keinen hat, drängt auf einen
        freien feindlichen Mann in der Nähe, höchstens zwei auf denselben. Die
        Phalanx hält ihre Reihen. Wer zuschlägt und wer getroffen wird, rechnet die
        Schlacht weiter von den Stellen der Männer, nicht von diesem Bild."""
        for u in self.lochoi:
            if u.fell_at:
                self.fallen_marks.extend((p, self.time) for p in u.fell_at)
                u.fell_at.clear()
        self.fallen_marks = [(p, t) for p, t in self.fallen_marks if self.time - t < config.FALLEN_MARK_TIME]
        grid: dict[tuple[int, int], list[tuple[Man, Lochos]]] = {}
        for u in self.lochoi:
            if u.alive:
                for m in u.all_men():
                    if m.flash > 0.0:
                        m.flash = max(0.0, m.flash - dt)
                    grid.setdefault(self._grid_cell(m.x, m.y), []).append((m, u))
        claims: dict[int, int] = {}
        step = config.JOSTLE_SPEED * dt
        reach = config.JOSTLE_REACH
        r = int(math.ceil(reach * 2))
        for u in self.lochoi:
            if not u.alive:
                continue
            men = u.all_men()
            engaged = (u.fighting and not u.in_phalanx
                       and (u.contacts or any(m.bound for m in men)))
            for m in sorted(men, key=lambda m: not m.bound) if engaged else men:
                tx = ty = 0.0
                if engaged:
                    cx, cy = self._grid_cell(m.x, m.y)
                    best, foe = reach, None
                    for gx in range(cx - r, cx + r + 1):
                        for gy in range(cy - r, cy + r + 1):
                            for o, e in grid.get((gx, gy), ()):
                                if e.side is u.side or claims.get(id(o), 0) >= config.JOSTLE_PER_FOE:
                                    continue
                                d = math.hypot(o.x - m.x, o.y - m.y)
                                if d < best:
                                    best, foe = d, o
                    if foe is not None and (not self.blocked or self._wall_level(m.pos) == self._wall_level(foe.pos)):
                        claims[id(foe)] = claims.get(id(foe), 0) + 1
                        fx, fy = foe.x + foe.show_dx, foe.y + foe.show_dy
                        d = math.hypot(fx - m.x, fy - m.y)
                        if d > config.JOSTLE_GAP:
                            k = min(d - config.JOSTLE_GAP, config.JOSTLE_MAX) / d
                            if not self.is_blocked(m.x + (fx - m.x) * k, m.y + (fy - m.y) * k):
                                tx, ty = (fx - m.x) * k, (fy - m.y) * k
                ddx, ddy = tx - m.show_dx, ty - m.show_dy
                d = math.hypot(ddx, ddy)
                if d <= step:
                    m.show_dx, m.show_dy = tx, ty
                else:
                    m.show_dx += ddx * step / d
                    m.show_dy += ddy * step / d

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
            u.face_to = (0.0, 1.0)
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
            if target is None or not target.alive or not self.inside(target.x, target.y) or (
                    not target.fighting and fighting):
                target, _ = self._nearest(u, fighting or foes)     # Geschlagene nicht verfolgen, solange andere kämpfen
                u.target_id = target.id if target else None
            u.target = target.pos if target else None
        for u in self.units(Side.STADT):
            if u.stance is Stance.FLUCHT:
                u.target = self.flee_target(u)

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
        elif u.flank_throw and (spot := self._open_side_spot(u, foe)) is not None:
            u.target = spot                                # erst an die schildlose Seite, dabei wird schon geworfen
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

    def _open_side_spot(self, u: Lochos, foe: Lochos) -> Point | None:
        """Ein Platz auf Wurfweite neben der rechten, schildlosen Flanke einer Hoplitenphalanx,
        solange ``u`` dort noch nicht steht; ``None``: kein solches Ziel, wie gewohnt plänkeln.
        Von links träfen die Speere den Schild."""
        if (not self._formed(foe) or foe.formation == "o" or foe.share(lambda m: m.kind.hoplite) < 0.5
                or self.on_wall(u) or self.on_wall(foe)):
            return None
        along, forward = foe.local(u.pos)
        if along > 0 and self.arc_of(foe, u.pos) == "flank":
            return None                                    # schon an der offenen Seite
        out = foe.half_w + u.half_d + config.JAVELIN_RANGE - config.SKIRMISH_FAR - 0.3
        fx, fy = foe.facing

        def at(a: float, f: float) -> Point:
            return (foe.x - fy * a + fx * f, foe.y + fx * a + fy * f)   # rechts (+a), so wie die Phalanx schaut

        spot = at(out, 0.0)
        if (not self.inside(*spot) or self.is_blocked(*spot, u) or not self.wall_clear(u.pos, spot)
                or self.arc_of(foe, spot) != "flank"):
            return None                                    # am Rand, im Haus, hinter dem Wall, oder ein Nachbar deckt
        if abs(forward) > foe.half_d + 0.3 and along < out - 0.4:
            # vor (oder hinter) der Phalanx: im selben Abstand an ihr entlang nach rechts, dann auf Höhe der Flanke
            slide = at(out, forward)
            if self.inside(*slide) and not self.is_blocked(*slide, u):
                return self._free_spot(slide, u)
        return self._free_spot(spot, u)

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
                a = self.arc_of(f, u.pos)
                v = {"front": 0.3, "flank": 1.2, "rear": 1.4}[a]
                if a == "flank":
                    v *= self.shield_side(f, u.pos, 0.9, 1.1)    # lieber die schildlose rechte Seite
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
            if u.alive and u.face_to is not None and not u.loose and (u.target is None or u.stance is Stance.PHALANX):
                # befohlene Front: im Stand oder als Phalanx auf dem Marsch schwenken; eine Phalanx
                # tauscht dabei keine Reihen, ihre Front bleibt die befohlene
                if self._turn_towards(u, u.face_to, dt, about=u.stance is not Stance.PHALANX) == 0.0:
                    u.face_to = None
            if u.alive and u.loose:
                if u.stance is Stance.FLUCHT and not any(self.inside(m.x, m.y) for m in u.all_men()):
                    u.withdrawn = True            # die Männer sind schon vom Feld
                continue                          # aufgelöst: jeder Mann geht für sich (siehe _move_men)
            if u.alive and u.countermarch_until > self.time and u.stance is not Stance.FLUCHT:
                u.in_line = False
                continue                          # Kontermarsch: die Rotten ziehen durch, die Gruppe steht
            if not u.alive or u.target is None or u.in_phalanx or u.building is not None:
                if u.alive and u.vel > 0.0:
                    self._coast(u, dt)                  # Reiter laufen aus statt auf der Stelle zu stehen
                continue
            speed = u.speed * (1.25 if u.stance is Stance.FLUCHT else 1.0)
            if u.pace is not None and u.stance is not Stance.FLUCHT:
                speed = min(speed, u.pace)              # im Verband: so schnell wie die langsamste Gruppe
            if u.engaged and u.stance is not Stance.FLUCHT:
                speed *= config.ENGAGED_SPEED           # im Handgemenge kommt man kaum vom Fleck
            if u.charge_slow_until > self.time:
                speed *= config.CHARGE_SLOW             # der Aufprall hat die Reiter gebremst
            goal, final = self.route(u, u.target)
            if (not self.on_wall(u) and self._wall_level(goal) == self._wall_level(u.pos)
                    and not any(dist(goal, self.foot_of(c)) < 0.8 for c in self.crossings)):
                way = self._obstacle_way(u, goal)        # um Häuser und Gerät herum, durch Gassen, in die man passt
                if way != goal:
                    goal, final = way, False
            d = dist(u.pos, goal)
            if u.march is not None and u.march[0] != u.target:
                u.march = None                           # ein neuer Befehl gilt
            arc = self._marching(u, final, d)
            if u.march is not None and dist(u.pos, u.target) <= config.MARCH_DEPLOY:
                self._deploy(u)                          # kurz vor dem Ziel: Breite und Front wie befohlen
            if u.mounted_men() and self.is_wall_cell(self.cell(*goal), True) and d <= 1.0:
                self._dismount(u)   # vor Leiter oder Turm wird abgesessen
            stop_at = 0.0
            if u.stance is Stance.ANGRIFF and final:
                target = self.by_id(u.target_id) if u.target_id is not None else None
                withdrawing = u.hitrun_until > self.time                 # Reiter setzen ab: nicht am Feind kleben
                if target is not None and not withdrawing and self._gap(u, target) <= config.CONTACT_GAP \
                        and self._front_reaches(u, target):
                    if self._rides(u) and u.vel > 0.05 and u.ride_in < config.CHARGE_PENETRATION:
                        u.vel = max(0.0, u.vel - config.CHARGE_BRAKE * dt)   # der Schwung trägt in den Feind hinein
                        step = u.vel * dt
                        self._step(u, scale(u.heading, step), through=True)
                        u.ride_in += step
                    else:
                        u.vel = 0.0
                    continue
                u.ride_in = 0.0
                stop_at = 0.0 if target is not None else config.ENGAGE_RANGE
            if d <= max(config.ARRIVE_EPS, stop_at):
                u.vel = 0.0
                if u.stance is Stance.PHALANX and final and d <= config.ARRIVE_EPS + 0.02:
                    if (u.x, u.y) != u.target:
                        u.still_since = self.time                # angekommen: wer später kommt, weicht
                    u.x, u.y = u.target
                    u.in_line = u.on_slots(config.SLOT_TOLERANCE, config.SLOT_SHARE) and all(
                        dist(m.pos, p) <= config.SLOT_TOLERANCE or self._crowding(m, m.pos, p, u.id) is not None
                        for m, p in u.slots() if m.bound
                    )                       # erst wenn (fast) alle stehen, die Gebundenen sicher, oder ihr Platz ist vom Feind besetzt
                elif u.stance in (Stance.HALTEN, Stance.PLAENKELN) and final:
                    u.target = None
                    u.still_since = self.time
                continue
            before = u.pos
            if not self.on_wall(u):
                goal = self._around(u, goal)              # eigene und fremde Gruppen im Weg werden umgangen
                if goal is None:                          # am Gegner ist kein Platz frei: im Block dahinter warten
                    u.waiting = True
                    u.vel = 0.0
                    continue
            if self._rides(u):
                self._ride(u, dt, goal, speed, d)
            elif arc:
                if goal != u.target and dist(goal, u.target) > 0.1:
                    # Umweg um eine eigene Gruppe: ein Stück über den Umwegpunkt hinaus zielen, zum Ziel hin
                    # (sonst schwenkt der Block an der Ecke kurz seitwärts und wieder zurück)
                    goal = add(goal, scale(norm(sub(u.target, goal)), config.MARCH_LOOKAHEAD))
                self._wheel(u, dt, goal, speed, dist(u.pos, goal))   # auf freiem Feld (auch um eigene herum): im Bogen
            else:
                u.vel = 0.0
                step = min(speed * dt, d)
                direction = norm(sub(goal, u.pos))
                if u.stance is Stance.FLUCHT or self.on_wall(u):
                    u.facing = direction                            # Flucht und Wehrgang: ohne Zeremonie
                elif u.stance is not Stance.PHALANX:
                    if abs(self._turn_towards(u, direction, dt)) > config.MOVE_TURN_TOLERANCE:
                        continue                                    # erst schwenken, dann marschieren
                self._step(u, scale(direction, step))
            if u.stance is Stance.ANGRIFF and not u.engaged:
                u.runup += dist(before, u.pos)          # Anlauf für den Sturmangriff
            else:
                u.runup = 0.0
            if u.stance is Stance.FLUCHT and not self.inside(u.x, u.y):
                u.withdrawn = True
        self._move_men(dt)

    def _marching(self, u: Lochos, final: bool, d: float) -> bool:
        """Marschiert die Gruppe im Bogen? Fußvolk als Block auf freiem Feld, unterwegs zu
        einem Ziel ohne Umweg über Wall, Tor oder um Häuser, noch weit genug weg; ein
        Linienbefehl gilt bis kurz vor dem Ziel, ein Marschbefehl auf längeren Wegen."""
        if not config.MARCH_ARC or not final or self.on_wall(u) or u.mounted_men() or u.engine is not None:
            return False
        if u.stance not in (Stance.HALTEN, Stance.RAUB, Stance.PHALANX) or u.engaged:
            return False
        if u.march is not None and u.march[0] == u.target:
            return dist(u.pos, u.target) > config.MARCH_DEPLOY
        return u.stance is not Stance.PHALANX and u.face_to is None and d > config.MARCH_MIN

    def _deploy(self, u: Lochos) -> None:
        """Aufmarschieren: die befohlene Breite und Front einnehmen."""
        _, width, facing = u.march
        u.march = None
        if u.full_width is not None:
            u.full_width = width                  # noch im Engpass: erst dahinter in voller Breite aufmarschieren
        elif width != u.width:
            u.reform(width)
        u.face_to = facing

    def _wheel(self, u: Lochos, dt: float, goal: Point, speed: float, d: float) -> None:
        """Marsch im Bogen: Die Front zeigt in Marschrichtung und schwenkt mit begrenzter
        Rate zum Ziel (eine breite Linie langsamer, ihr äußerer Mann muss mithalten); liegt
        das Ziel weit seitlich, wird langsamer marschiert und enger geschwenkt. Liegt es
        hinter der Gruppe, macht sie kehrt."""
        u.vel = 0.0
        want = norm(sub(goal, u.pos))
        if abs(self._angle_to(u.facing, want)) > config.ABOUT_TURN:
            self._about_turn(u)
        ang = self._angle_to(u.facing, want)
        rate = min(config.MARCH_WHEEL_MAX, config.MARCH_WHEEL / max(0.3, u.half_w)) * config.DRILL_TURN.get(u.drill_kind(), 1.0)
        turn = max(-rate * dt, min(rate * dt, ang))
        fx, fy = u.facing
        c, s_ = math.cos(turn), math.sin(turn)
        u.facing = (fx * c - fy * s_, fx * s_ + fy * c)
        u.heading = u.facing
        rest = abs(ang - turn)
        pace = max(0.15, math.cos(min(rest, math.pi / 2)))   # weit seitlich: fast auf der Stelle schwenken
        self._step(u, scale(u.facing, min(speed * pace * dt, d)))

    def _standing(self, o: Lochos) -> bool:
        """Steht die Gruppe (statt unterwegs zu sein)? Ohne Ziel, angekommen (eine
        Phalanx behält ihr Ziel als Posten), im Handgemenge, wartend oder beim Bauen."""
        if o.engaged or o.waiting or o.building is not None or o.target is None:
            return True
        return o.stance is Stance.PHALANX and dist(o.pos, o.target) <= config.ARRIVE_EPS + 0.05

    def _idle(self, o: Lochos) -> bool:
        """Ruht die Gruppe auf ihrem Platz (ohne Ziel, als Phalanx auf ihrem Posten, beim
        Bauen)? Eine ruhende eigene Gruppe wird nie geschoben, man geht um sie herum."""
        if o.engaged or o.waiting:
            return False
        if o.building is not None or o.target is None:
            return True
        return o.stance is Stance.PHALANX and dist(o.pos, o.target) <= config.ARRIVE_EPS + 0.05

    def _passable(self, o: Lochos) -> bool:
        """Leichte Truppen in lockerer Ordnung lassen eigene Gruppen durch (die Männer
        weichen einander aus), solange sie nicht selbst im Handgemenge stehen."""
        return not o.engaged and not o.waiting and o.share(lambda m: m.kind.ranged) >= 0.5

    def _clear_of_own(self, u: Lochos, p: Point) -> Point:
        """Ein Ziel, auf dem schon eine stehende eigene Gruppe steht, rückt daneben:
        Die befohlene Gruppe hält vor ihr, statt sie wegzuschieben."""
        blockers = [o for o in self.lochoi if o is not u and o.alive and o.side is u.side and not o.loose
                    and self.on_wall(o) == self.on_wall(u) and self._idle(o) and not self._passable(o)]
        if not blockers:
            return p

        final_facing = u.face_to or u.facing                # am Ziel steht man mit der befohlenen Front

        def hit(q: Point) -> Lochos | None:
            return next((o for o in blockers if dist(o.pos, q) <= o.radius + u.radius
                         and self._gap_at(u, q, o, final_facing) < config.SEPARATION), None)
        o = hit(p)
        if o is None:
            return p
        away = sub(p, o.pos) if dist(p, o.pos) > 0.05 else sub(u.pos, o.pos)
        if math.hypot(*away) < 1e-6:
            away = (0.0, 1.0)
        away = norm(away)
        for k in range(1, 61):                            # in Zehntelschritten von ihr weg, bis frei
            q = (p[0] + away[0] * 0.1 * k, p[1] + away[1] * 0.1 * k)
            if not self.inside(*q) or self.is_blocked(*q, u):
                break
            if hit(q) is None:
                return q
        return p

    def _around(self, u: Lochos, goal: Point) -> Point | None:
        """Steht eine eigene Gruppe auf dem Weg (still, als Phalanx auf ihrem Posten,
        kämpfend oder wartend), geht ein Block um sie herum, statt sie zu schieben:
        Zwischenziel neben der Gruppe, auf der Seite, die dem Weg näher liegt. Das gilt
        noch für Angriffe, Fliehende und Gruppen mit Gerät; wer nur marschiert, löst
        sich stattdessen auf und geht Mann für Mann vorbei (``_update_loose``).
        Gruppen, die beide unterwegs sind, gehen einander Mann für Mann aus dem Weg;
        Feinde sind keine Umgehung wert, an ihnen bleibt man hängen und kämpft. Die
        gewählte Seite bleibt, bis man vorbei ist; ein Angriff nimmt die Seite, auf der
        am Gegner noch Platz ist, und ist nirgends mehr Platz, gibt es None: warten."""
        free = None
        side = u.detour_side or None
        if u.target_id is not None:
            foe = self.by_id(u.target_id)
            free = self._free_outline(u, foe) if foe is not None else None
            if free and side is None:
                # auf der Seite herum, auf der am Gegner noch Platz ist
                fp = min(free, key=lambda p: dist(p, u.pos))
                dx, dy = norm(sub(goal, u.pos))
                side = 1.0 if (fp[0] - u.x) * -dy + (fp[1] - u.y) * dx > 0 else -1.0
        sticky = config.DETOUR_STICKY
        # Spiel an der Schwelle: Wer schon ausweicht, gilt erst mit mehr Abstand als vorbei
        plan = self._detour_plan(u, goal, side=side, hyst=config.DETOUR_HYST if sticky and u.detour_on else 0.0)
        u.detour_on = plan is not None
        if plan is None:
            if not sticky or self.time > u.detour_until:
                u.detour_side = 0.0                       # frei: beim nächsten Hindernis wird neu gewählt
            return goal
        if free is not None and not free:
            return None                                   # am Gegner ist kein Platz mehr frei: geordnet dahinter warten
        wp, u.detour_side = plan                          # die Seite bleibt, bis man vorbei ist (kein Hin und Her)
        u.detour_until = self.time + config.DETOUR_MEMORY # und noch kurz danach, falls gleich die nächste Gruppe kommt
        if not self.inside(*wp) or self.is_blocked(*wp) or not self.path_clear(u.pos, wp, u):
            return goal                                   # kein begehbarer Umweg (Palisade, Tor): dahinter anstehen
        return wp

    def _free_outline(self, u: Lochos, foe: Lochos) -> list[Point] | None:
        """Stellen rund um den Gegner, an denen noch keine andere eigene Gruppe steht und
        wenigstens zwei nebeneinander frei sind (Platz zum Anlegen). None: nicht
        bestimmbar (der Gegner ist aufgelöst)."""
        if foe.loose or not foe.alive:
            return None
        out = 0.3
        pts: list[Point] = []
        if foe.formation == "o":
            r = foe.half_w + out
            n = max(12, int(2 * math.pi * r / 0.3))
            pts = [(foe.x + math.cos(2 * math.pi * k / n) * r, foe.y + math.sin(2 * math.pi * k / n) * r) for k in range(n)]
        else:
            fx, fy = foe.facing
            ax, ay = -fy, fx
            hw, hd = foe.half_w + out, foe.half_d + out
            corners = [(-hw, hd), (hw, hd), (hw, -hd), (-hw, -hd)]
            for (a0, f0), (a1, f1) in zip(corners, corners[1:] + corners[:1]):
                n = max(1, int(math.hypot(a1 - a0, f1 - f0) / 0.3))
                for k in range(n):
                    a, f = a0 + (a1 - a0) * k / n, f0 + (f1 - f0) * k / n
                    pts.append((foe.x + ax * a + fx * f, foe.y + ay * a + fy * f))

        def taken(p: Point) -> bool:
            if not self.inside(*p) or self.is_blocked(*p, u):
                return True
            cx, cy = self._grid_cell(*p)
            for gx in (cx - 1, cx, cx + 1):
                for gy in (cy - 1, cy, cy + 1):
                    for m, uid in self._man_grid.get((gx, gy), ()):
                        if uid != u.id and self._man_side.get(id(m)) is u.side and math.hypot(m.x - p[0], m.y - p[1]) < 0.3:
                            return True
            return False
        free = [not taken(p) for p in pts]
        n = len(pts)
        return [p for i, p in enumerate(pts) if free[i] and (free[i - 1] or free[(i + 1) % n])]

    def _detour(self, u: Lochos, goal: Point, idle_only: bool = False) -> Point | None:
        """Zwischenziel neben der nächsten stehenden (``idle_only``: ruhenden) eigenen
        Gruppe, die auf dem Weg nach ``goal`` liegt, oder None, wenn keine im Weg steht."""
        plan = self._detour_plan(u, goal, idle_only)
        return plan[0] if plan is not None else None

    def _detour_plan(self, u: Lochos, goal: Point, idle_only: bool = False,
                     side: float | None = None, hyst: float = 0.0) -> tuple[Point, float] | None:
        """Wie ``_detour``, mit der Seite (+1/-1 quer zum Weg), auf der man vorbeigeht;
        ``side`` gibt sie vor, sonst die Seite, die dem Weg näher liegt. ``hyst``: wer
        schon ausweicht, gilt erst mit so viel mehr Abstand als vorbei (sonst schaltet ein
        Block an der Schwelle jeden Schritt zwischen Umweg und geradem Weg)."""
        d = dist(u.pos, goal)
        if d < 1e-6:
            return None
        direction = norm(sub(goal, u.pos))
        px, py = -direction[1], direction[0]

        steady = config.DETOUR_STICKY and u.stance is not Stance.PHALANX

        def extent(g: Lochos) -> float:
            if g is u and steady:
                return u.half_w                           # wer marschiert, dreht die Front in den Weg: nicht vom Schwenk abhängig
            return self._extent(g, px, py)

        best: tuple[float, Point] | None = None
        for o in self.lochoi:
            if o is u or not o.alive or o.loose or o.side is not u.side or self.on_wall(o) != self.on_wall(u):
                continue
            if self._passable(o) or self._nested(u, o):
                continue                                  # lockere Ordnung (oder Ring im Ring): man geht hindurch
            if not self._standing(o) or (idle_only and not self._idle(o)):
                continue                                  # selbst unterwegs: man weicht sich Mann für Mann aus
            if o.id == u.target_id or o.id in u.contacts:
                continue
            clear = extent(u) + extent(o) + config.DETOUR_MARGIN
            ox, oy = o.x - u.x, o.y - u.y
            along = ox * direction[0] + oy * direction[1]
            if along <= 0.0 or along - o.radius > d:
                continue                                  # hinter uns oder erst hinter dem Ziel
            off = ox * px + oy * py
            if abs(off) >= clear + hyst:
                continue                                  # geht knapp vorbei
            if along > d - o.radius and (u.target_id is not None
                                         or self._gap_at(u, goal, o, u.face_to or (direction if steady else u.facing))
                                         < config.SEPARATION):
                continue                                  # das Ziel liegt bei ihr: Ankunft, oder dahinter kämpft man (anstehen)
            if best is None or along < best[0]:
                s_ = side if side else (1.0 if off < 0 else -1.0)   # vorgegeben, sonst die Seite, die dem Weg näher liegt
                wide = clear + 2.0 * hyst                 # so weit hinaus, dass man dort sicher als vorbei gilt
                wp = (o.x + px * s_ * wide, o.y + py * s_ * wide)
                depth_u = u.half_d if steady else self._extent(u, *direction)
                if along < self._extent(o, *direction) + depth_u + config.DETOUR_MARGIN:
                    # liegt man schon an ihr an: erst seitlich heraus, dann vorbei (nicht über ihre Ecke)
                    lateral = off + s_ * wide
                    wp = (u.x + px * lateral, u.y + py * lateral)
                best = (along, wp, s_)
        return (best[1], best[2]) if best is not None else None

    def _front_reaches(self, u: Lochos, foe: Lochos) -> bool:
        """Erreicht die vordere Reihe den Gegner? Am Rand seines Rechtecks stehen die
        Männer dort, wo seine hintere Reihe kurz ist, noch außer Speerweite; dann
        rückt man weiter auf, bis wirklich Mann gegen Mann steht."""
        if u.loose or not u.rows or foe.loose:
            return True
        distance = self._reach_to(foe)
        return any(distance(m) <= config.CONTACT_REACH for m in u.rows[0])

    def _rides(self, u: Lochos) -> bool:
        """Beritten und im Gelände unterwegs: Bewegung mit Schwung."""
        return bool(u.mounted_men()) and not u.loose and not self.on_wall(u) and u.engine is None

    def _ride(self, u: Lochos, dt: float, goal: Point, top: float, d: float) -> None:
        """Reiter haben Schwung: Sie fahren an, bremsen vor dem Ziel ab und wenden in
        Bögen, deren Halbmesser mit dem Tempo wächst; im Stand drehen sie frei."""
        want = norm(sub(goal, u.pos))
        ang = 0.0
        rest = 0.0
        if (u.vel <= 0.05 or u.heading == (0.0, 0.0)) and u.stance is Stance.FLUCHT:
            head = want                                                     # Flucht: ohne Zeremonie
        elif config.MARCH_ARC:
            if u.vel <= 0.05 or u.heading == (0.0, 0.0):
                if abs(self._angle_to(u.facing, want)) > config.ABOUT_TURN:
                    self._about_turn(u)                                 # das Ziel liegt hinten: kehrt
                u.heading = u.facing
            # im Bogen: anreiten und dabei schwenken; je schneller, desto weiter der Bogen,
            # und ein breiter Block schwenkt langsamer (der äußere Reiter muss mithalten)
            head = u.heading
            ang = self._angle_to(head, want)
            omega = min(config.CAVALRY_TURN_RATE / max(1.0, u.vel), config.CAVALRY_WHEEL / max(0.3, u.half_w))
            turn = max(-omega * dt, min(omega * dt, ang))
            rest = abs(ang - turn)
            ang = turn
            c, s_ = math.cos(ang), math.sin(ang)
            head = (head[0] * c - head[1] * s_, head[0] * s_ + head[1] * c)
        elif u.vel <= 0.05 or u.heading == (0.0, 0.0):
            rest = self._turn_towards(u, want, dt)                 # im Stand schwenken oder kehrtmachen
            u.heading = u.facing
            if abs(rest) > config.MOVE_TURN_TOLERANCE:
                u.vel = 0.0
                return                                              # erst wenden, dann anfahren
            head = want
            rest = 0.0
        else:
            head = u.heading
            ang = math.atan2(head[0] * want[1] - head[1] * want[0], head[0] * want[0] + head[1] * want[1])
            omega = config.CAVALRY_TURN_RATE / max(1.0, u.vel)
            ang = max(-omega * dt, min(omega * dt, ang))
            c, s_ = math.cos(ang), math.sin(ang)
            head = (head[0] * c - head[1] * s_, head[0] * s_ + head[1] * c)
        if u.stance is Stance.ANGRIFF and u.target_id is not None and u.hitrun_until <= self.time:
            want_v = top                                                     # Sturm: nicht vor dem Feind bremsen
        else:
            want_v = min(top, math.sqrt(2.0 * config.CAVALRY_BRAKE * d), 3.0 * d + 0.05)   # Bremsweg, zuletzt weich auslaufen
        if rest > 0.0 and u.vel < 1.0:
            want_v *= max(0.25, math.cos(min(rest, math.pi / 2)))           # beim Anreiten weit seitlich: enger schwenken
        if config.MARCH_ARC and u.stance is not Stance.FLUCHT:
            want_v = min(want_v, self._corner_speed(head, want, d))       # enge Wendung: traben statt Schleife
        if u.vel < want_v:
            u.vel = min(want_v, u.vel + config.CAVALRY_ACCEL * dt)
        else:
            u.vel = max(want_v, u.vel - config.CAVALRY_BRAKE * dt)
        u.heading = head
        if u.stance is not Stance.PHALANX or u.march is not None:
            u.facing = head                                                 # die Front in Reitrichtung
        step = u.vel * dt
        if abs(ang) < 1e-3 and dist(head, want) < 1e-3:
            step = min(step, d)
        self._step(u, scale(head, step))

    @staticmethod
    def _corner_speed(head: Point, want: Point, d: float) -> float:
        """Das höchste Tempo, mit dem Reiter den Punkt in Abstand ``d`` und Richtung ``want``
        noch ohne Schleife erreichen: Der Kreis durch ihn, tangential zur Fahrtrichtung, hat
        den Halbmesser d / (2 sin Winkel); im Galopp wendet man mit Halbmesser v²/K (unter
        Schritttempo v/K). Was schneller ist, Galopp im weiten Bogen oder Trab im engen,
        entscheidet sich so von selbst: getrabt wird nur, wo der Bogen sonst nicht passt."""
        ang = abs(math.atan2(head[0] * want[1] - head[1] * want[0], head[0] * want[0] + head[1] * want[1]))
        if ang < 0.05 or d < 1e-6:
            return float("inf")
        radius = d / (2.0 * math.sin(min(ang, math.pi / 2)))
        k = config.CAVALRY_TURN_RATE
        v = math.sqrt(k * radius) if k * radius >= 1.0 else k * radius
        return max(config.CAVALRY_MIN_TURN_SPEED, v)

    @staticmethod
    def _angle_to(facing: Point, want: Point) -> float:
        """Vorzeichenbehafteter Winkel von der Blickrichtung zur gewünschten Richtung."""
        return math.atan2(facing[0] * want[1] - facing[1] * want[0], facing[0] * want[0] + facing[1] * want[1])

    @staticmethod
    def _stand_turn_rate(u: Lochos) -> float:
        """Wie schnell eine Gruppe im Stand schwenkt (rad/s): so schnell, wie ihr äußerer Mann
        den Bogen gehen kann; eine breite Phalanx dreht also langsamer als ein kleiner Trupp.
        Reiter wenden auf der Stelle ohnehin bedächtig. Ein Kreis hat keine Front zu drehen."""
        rate = config.STAND_TURN_RATE
        if u.formation != "o":
            rate = min(rate, config.TURN_OUTER_PACE * max(0.3, u.speed) / max(0.3, u.half_w))
            if 2 * len(u.mounted_men()) >= max(1, u.men):
                rate = min(rate, config.CAVALRY_STAND_TURN)
        return rate * config.DRILL_TURN.get(u.drill_kind(), 1.0)

    def _turn_towards(self, u: Lochos, want: Point, dt: float, about: bool = True) -> float:
        """Im Stand wenden: Die Front dreht sich mit begrenzter Rate, die Männer
        schwenken auf ihren Plätzen mit. Liegt das Ziel hinter der Gruppe, macht
        sie kehrt: Die Reihen tauschen, jeder Mann bleibt fast auf seinem Platz
        und wendet nur. Liefert den Winkel, der noch fehlt."""
        if u.facing == (0.0, 0.0):
            u.facing = want
            return 0.0
        ang = self._angle_to(u.facing, want)
        if about and abs(ang) > config.ABOUT_TURN and not u.loose:
            self._about_turn(u)
            ang = self._angle_to(u.facing, want)
        limit = self._stand_turn_rate(u) * dt
        if abs(ang) <= limit:
            u.facing = want
            return 0.0
        turn = math.copysign(limit, ang)
        fx, fy = u.facing
        c, s_ = math.cos(turn), math.sin(turn)
        u.facing = (fx * c - fy * s_, fx * s_ + fy * c)
        return ang - turn

    def _about_turn(self, u: Lochos) -> None:
        """Kehrtwendung. Hopliten (außerhalb des Handgemenges) machen einen Kontermarsch: Die
        Front wechselt die Seite, aber dieselben Männer bleiben vorn; jede Rotte zieht durch
        sich selbst hindurch (links bleibt links). Das braucht seine Zeit, solange steht die
        Gruppe ungeordnet."""
        if not config.COUNTERMARCH or u.engaged or u.share(lambda m: m.kind.hoplite) < 0.5:
            # Haufen, Leichte und Reiter haben keine festen Reihen, und im Handgemenge wendet sich
            # jeder dem Feind zu: einfache Kehrtwendung, die hintere Reihe steht dann vorn
            u.rows = [list(reversed(r)) for r in reversed(u.rows)]
            u.facing = (-u.facing[0], -u.facing[1])
            u.heading = u.facing
            u.in_line = False
            return
        u.rows = [list(reversed(r)) for r in u.rows]
        u.facing = (-u.facing[0], -u.facing[1])
        u.heading = u.facing
        u.in_line = False
        u.vel = 0.0
        duration = (config.COUNTERMARCH_BASE + config.COUNTERMARCH_PER_ROW * max(0, len(u.rows) - 1)) / config.DRILL_TURN.get(u.drill_kind(), 1.0)
        u.countermarch_until = self.time + duration

    def _coast(self, u: Lochos, dt: float) -> None:
        """Ohne Ziel: Reiter bremsen ab und rollen dabei noch aus."""
        if not self._rides(u):
            u.vel = 0.0
            return
        u.vel = max(0.0, u.vel - config.CAVALRY_BRAKE * dt)
        if u.vel > 0.0:
            self._step(u, scale(u.heading, u.vel * dt))

    def _wall_level(self, p: Point) -> str:
        """"nord", "sued", "wall" oder "tor": auf welcher Seite der Palisade ein Punkt
        liegt; das offene Tor ist der Durchgang dazwischen."""
        c = self.cell(*p)
        if self.is_wall_cell(c, True):
            return "wall"
        if c in self._gate_of:
            return "tor"
        if self.ring:
            return self._cell_level(c)
        if not self.blocked:
            return "sued"
        wall_y = next(iter(self.blocked))[1]
        return "sued" if c[1] > wall_y else "nord"

    def _update_loose(self, u: Lochos) -> None:
        """Wann eine Gruppe sich auflöst und jeder Mann für sich an seinen Platz in der
        Zielaufstellung geht: über den Wall (Turm, Leiter), durchs Tor und um eigene
        stehende Gruppen herum. Die Zielaufstellung (Mitte und Front) steht dabei
        fest; die Gruppe ist dort, wo ihre Männer sind. Sie schließt sich wieder, sobald
        die Männer angekommen sind oder geschlossen gehen, und zwar dort, wo sie
        stehen, so dass niemand seinen Platz noch einmal verlässt."""
        if not u.alive:
            return
        if (u.target is not None and u.target_id is None and not u.loose and u.stance is not Stance.FLUCHT
                and not u.in_phalanx and u.building is None and u.target != u.target_checked
                and not self._verband_ring(u)):
            u.target = self._clear_of_own(u, u.target)   # besetzter Platz: daneben halten (einmal je Befehl)
            u.target_checked = u.target
        why = self._loose_reason(u)
        if not u.loose:
            if why:
                self._dissolve(u, why)
            elif self._stragglers(u) or self._jammed(u):
                if u.target is None:
                    u.target = u.pos                  # hier bleiben: die Hängenden kommen an ihre Plätze
                u.straggled_at = u.target             # für dieses Ziel nur einmal
                self._dissolve(u, "eigene")           # Männer hängen hinter eigenen Gruppen: jeder sucht sich den Weg
                u.stay_loose = True                   # ... und zwar bis an die Plätze, nicht gleich wieder als Block
                u.stay_since = self.time
            else:
                self._widen_again(u)
            return
        if why:
            if why == "wall" and not u.over_wall:
                u.over_wall = True
                self.events.append(f"{u.name}: Formation aufgelöst, Mann für Mann über den Wall")
            u.loose_why = why
            self._aim_dest(u)
            return
        if self._may_close(u):
            self._close(u)
        else:
            u.loose_why = ""                              # über das Hindernis hinweg: formiert sich noch
            self._aim_dest(u)

    def _loose_reason(self, u: Lochos) -> str:
        """"wall", "tor", "eigene" oder "" (kein Grund, sich aufzulösen)."""
        dest = u.target if u.target is not None else (u.dest if u.loose else None)
        if self.is_walker(u):
            via = self._via(u)
            if via is not None and any(self._wall_level(m.pos) != self._wall_level(u.target) for m in u.all_men()):
                return "wall"                     # befohlen: über diesen Turm, nicht durchs Tor
            centre_up = self.on_wall(u)
            on_route = False
            if dest is not None:
                goal, _ = self.route(u, dest)
                goal_up = self.is_wall_cell(self.cell(*goal), True)
                target_up = self.is_wall_cell(self.cell(*dest), True)
                on_route = (goal_up and not target_up) or (centre_up and not target_up)
            centre_level = self._wall_level(u.pos)
            if self.ring:
                levels = {self._wall_level(m.pos) for m in u.all_men()} | {centre_level}
                levels.discard("tor")             # der Tordurchgang ist keine Wallseite
                if on_route or "wall" in levels or (len(levels) > 1 and not self._keeps_order(u)):
                    return "wall"                 # (eine Phalanx, die als Block durchs Tor zieht, steht kurz auf beiden Seiten)
            elif on_route or any(self._wall_level(m.pos) != centre_level for m in u.all_men()):
                return "wall"                     # der Weg führt über den Wall, oder Männer stehen noch drüben oder oben
        if (u.target is None or u.engine is not None or u.building is not None or u.stance is Stance.FLUCHT
                or u.engaged or self.on_wall(u) or (self._rides(u) and u.target_id is not None)):
            return ""
        if u.target_id is not None:
            return ""                             # ein Angriff bleibt Block: hinter der eigenen kämpfenden Gruppe steht man an
        if u.loose and u.muster is not None:
            return ""                             # erst am Sammelplatz schließen, dann weiter
        if u.side is not Side.STADT and not config.LOOSE_AI:
            return ""                             # die Gegner gehen (vorerst) als Block um ihre Haufen herum und durchs Tor
        why = ""
        open_gates = [g.center for g in self.gates if not g.closed]
        here, there = self._wall_level(u.pos), self._wall_level(u.target)
        through = here != there and "tor" not in (here, there) and "wall" not in (here, there)
        if (self.blocked and open_gates and not self.is_wall_cell(self.cell(*u.target), True)
                and (through or not self.wall_clear(u.pos, u.target))):
            if any(e.side is not u.side and e.fighting and dist(e.pos, gate) <= config.LOOSE_ENEMY_RANGE
                   for e in self.lochoi for gate in open_gates):
                return ""                         # am Tor wird gekämpft: dort hält man die Ordnung und steht an
            why = "tor"                           # durchs offene Tor (oder um ein Wallstück herum)
        elif self.wall_clear(u.pos, u.target) and (
                u.idle_block or (wp := self._detour(u, u.target, idle_only=True)) is not None):
            if u.side is not Side.STADT and any(e.side is not u.side and e.fighting
                                                and e.rect_distance(u.pos) <= config.LOOSE_ENEMY_RANGE
                                                for e in self.lochoi):
                return ""                         # die Gegner halten nahe am Feind die Ordnung und gehen als Block herum
            if not u.idle_block and not u.loose:
                key = (round(u.target[0], 1), round(u.target[1], 1))
                hit = self._pass_choice.get(u.id)
                if hit is None or hit[0] != key:   # einmal je Ziel entschieden (kein Umschwenken unterwegs)
                    hit = self._pass_choice[u.id] = (key, self._block_passes(u, wp))
                if hit[1]:
                    return ""                     # als Block im Bogen herum ist nicht langsamer
            why = "eigene"                        # eine ruhende eigene Gruppe steht im Weg (hinter kämpfenden steht man an)
        if not why and self._narrow_way(u):
            why = "enge"                          # der Block passt nicht durch die Gasse: Mann für Mann statt großem Umweg
        if why in ("tor", "eigene", "enge") and self._keeps_order(u):
            # die Phalanx bleibt zusammen: um eigene Gruppen als Block herum,
            # durch Tor und Gasse schmaler und tiefer statt Mann für Mann
            if why == "eigene" or self._narrow_column(u, why):
                return ""
        if why and self._field_builds.get(self.time, 0) >= self._field_budget():
            return ""                             # in diesem Takt schon genug Wegefelder gerechnet: einen Takt später auflösen
        if why and not self._way_open(u):
            return ""                             # kein Durchkommen (die eigenen kämpfen im Durchgang): als Block anstehen
        return why

    def _jammed(self, u: Lochos) -> bool:
        """Steckt der Block fest? Er hat ein Ziel, kommt aber seit einer Weile nicht vom Fleck
        (etwa zwischen zwei ruhenden eigenen Gruppen), und kein Feind ist nah. Dann löst er
        sich auf, und jeder Mann sucht seinen Weg, statt endlos davor zu stehen."""
        moving = (u.target is not None and u.target_id is None and not u.engaged and u.engine is None
                  and u.building is None and not self.on_wall(u) and u.stance is not Stance.FLUCHT
                  and dist(u.pos, u.target) > 0.5 and u.countermarch_until <= self.time)
        if not moving:
            u.jam_since = -1.0
            return False
        if u.jam_since < 0.0 or dist(u.pos, u.jam_at) > 0.1:
            u.jam_since, u.jam_at = self.time, u.pos
            return False
        waited = self.time - u.jam_since
        if waited < config.JAM_TIME:
            return False
        if any(e.side is not u.side and e.alive and e.rect_distance(u.pos) <= config.LOOSE_ENEMY_RANGE for e in self.lochoi):
            u.jam_since = -1.0
            return False                                  # nahe am Feind bleibt man im Block und steht an
        if self._cut_off(u, u.target):
            u.jam_since = -1.0
            return False                                  # das Tor ist zu: davor warten, nicht auflösen
        if self._field_builds.get(self.time, 0) >= self._field_budget() and waited < config.JAM_TIME + 1.0:
            return False                                  # in diesem Takt schon genug Wegefelder: gleich noch einmal
        u.jam_since = -1.0
        return True

    def _stragglers(self, u: Lochos) -> bool:
        """Die Gruppe steht schon am Ziel, aber ein guter Teil ihrer Männer kommt seit einer
        Weile nicht an seinen Platz (etwa hinter eigenen Gruppen, die dazwischen stehen)?"""
        if (u.target_id is not None or u.engaged or u.stance not in (Stance.PHALANX, Stance.HALTEN)
                or self.on_wall(u) or u.building is not None or (u.target is not None and dist(u.pos, u.target) > 0.2)
                or u.countermarch_until > self.time or u.vel > 0.05 or u.engine is not None
                or any(e.side is not u.side and e.alive and e.rect_distance(u.pos) <= config.LOOSE_ENEMY_RANGE
                       for e in self.lochoi)):
            u.lag_since = -1.0                            # (nahe am Feind bleibt man im Block)
            return False
        if u.straggled_at is not None and u.target is not None and dist(u.straggled_at, u.target) < 0.2:
            return False                                  # für dieses Ziel schon einmal versucht
        far = sum(1 for m, p in u.slots() if dist(m.pos, p) > config.STRAGGLER_DIST and not m.bound)
        if far == 0:
            u.lag_since = -1.0
            return False
        if u.lag_since < 0.0:
            u.lag_since = self.time
            return False
        waited = self.time - u.lag_since
        limit = config.STRAGGLER_TIME if far >= config.STRAGGLER_SHARE * u.men else config.STRAGGLER_TIME_FEW
        if waited < limit:
            return False                                  # viele: nach 1,5 s; einzelne: nach 3 s
        if self._field_builds.get(self.time, 0) >= self._field_budget() and waited < limit + 1.0:
            return False                                  # in diesem Takt schon genug Wegefelder: gleich noch einmal
        u.lag_since = -1.0
        return True

    def _keeps_order(self, u: Lochos) -> bool:
        """Hält die Gruppe auf dem Marsch ihre Ordnung (eine Phalanx in Linie)?"""
        return (config.DRILL_NARROW and not u.loose and u.formation == "linie" and u.stance is not Stance.FLUCHT
                and u.drill_kind() == "phalanx")

    def _narrow_column(self, u: Lochos, why: str) -> bool:
        """Vor Tor oder Gasse schmaler werden, so dass die Front hindurchpasst (die Reihen
        werden tiefer). False, wenn selbst die schmalste Front nicht passt: dann doch Mann
        für Mann."""
        if u.target is None:
            return False
        if why == "tor":
            gates = [g for g in self.gates if not g.closed]
            if not gates:
                return False
            goal, _ = self.route(u, u.target)
            g = min(gates, key=lambda g: dist(g.center, u.pos) + dist(g.center, goal))
            lane = g.half_len
        else:
            thin = self._block_path(u.pos, u.target, config.NARROW_MIN_WIDTH)
            if not thin:
                return False
            inner = [self._room_at(p) for p in thin if dist(p, u.pos) > 0.8 and dist(p, u.target) > 0.8]
            lane = min(inner) if inner else math.inf
        if lane == math.inf:
            return True
        width = int((lane - 0.11) * 2 / u.man_gap() + 1e-6)  # halbe Front plus Rand passt in die halbe Gasse
        if width >= u.width:
            return True                                     # passt schon
        if width < config.DRILL_NARROW_MIN:
            return False
        if u.full_width is None:
            u.full_width = u.width
            self.events.append(f"{u.name}: schmaler, {width} breit durch den Engpass")
        u.reform(width)
        u.in_line = False
        self._narrow_cache.pop(u.id, None)
        return True

    def _widen_again(self, u: Lochos) -> None:
        """Hinter dem Engpass wieder in die volle Breite: sobald alle Männer durchs Tor sind,
        die volle Front hier Platz hat und der Weg zum Ziel für sie frei ist."""
        if u.full_width is None or u.loose or not u.alive:
            return
        if u.full_width <= u.width:
            u.full_width = None
            return
        if int(self.time * 4) % 2 != u.id % 2:
            return                                          # nur jeden zweiten Viertelschritt prüfen
        if u.target is not None and self.blocked and not self.wall_clear(u.pos, u.target):
            return                                          # das Tor kommt noch
        levels = {self._wall_level(m.pos) for m in u.all_men()}
        if len(levels) > 1 or "tor" in levels:
            return                                          # noch im Tor
        half = u.full_width * u.man_gap() / 2 + 0.08
        fx, fy = u.facing
        ax, ay = -fy, fx
        for k in (-1.0, -0.5, 0.0, 0.5, 1.0):
            for f in (-u.half_d, 0.0, u.half_d):
                p = (u.x + ax * half * k + fx * f, u.y + ay * half * k + fy * f)
                if not self.inside(*p) or self.is_blocked(p[0], p[1], u) or self._room_at(p) < 0.05:
                    return
        if u.target is not None and dist(u.pos, u.target) > 0.8:
            r = min(half, config.BLOCK_CLEARANCE_MAX) + 0.03
            if not self._wide_clear(u.pos, u.target, r):
                return
        u.reform(u.full_width)
        u.full_width = None
        u.in_line = False

    def _narrow_way(self, u: Lochos) -> bool:
        """Passt der Block nicht durch eine Gasse zwischen Häusern (oder Gerät), sodass Mann für
        Mann hindurch schneller wäre als außen herum? Gerechnet wird nur, wo die gerade Linie
        für den Block nicht frei ist, und das Ergebnis gilt eine Weile."""
        if (not config.NARROW_LOOSE or u.target is None or not self.house_cells and not self._ram_cells
                and not self._tower_cells):
            return False
        if self.on_wall(u) or not self.wall_clear(u.pos, u.target):
            return False                          # über den Wall oder durchs Tor regeln andere Gründe
        r = self._block_width(u)
        if r <= config.NARROW_MIN_WIDTH or self._wide_clear(u.pos, u.target, r):
            return False
        key = (round(u.target[0], 1), round(u.target[1], 1), round(r, 1))
        hit = self._narrow_cache.get(u.id)
        if hit is not None and hit[0] == key and self.time - hit[1] < config.BLOCK_WAY_TIME:
            return hit[2]

        def length(path: list[Point]) -> float:
            pts = [u.pos] + path
            return sum(dist(a, c) for a, c in zip(pts, pts[1:]))
        wide = self._block_path(u.pos, u.target, r)
        thin = self._block_path(u.pos, u.target, config.NARROW_MIN_WIDTH)
        narrow = bool(thin) and (not wide or self._loose_faster(u, length(wide), length(thin), squeeze=True))
        self._narrow_cache[u.id] = (key, self.time, narrow)
        return narrow

    def _loose_faster(self, u: Lochos, block_len: float, loose_len: float, squeeze: bool = False) -> bool:
        """Was ist schneller: als Block den Weg ``block_len`` (mit Schwenks), oder aufgelöst
        Mann für Mann den Weg ``loose_len`` und am Ende neu formieren (durch eine enge Gasse
        stehen die Männer dazu an)? Aufgelöst wird nur, wenn es merklich schneller ist; bei
        etwa gleicher Zeit hält die Gruppe ihre Ordnung."""
        v = max(0.1, u.speed)
        t_block = block_len / v + config.BLOCK_DETOUR_TIME
        t_loose = loose_len / v + config.LOOSE_REFORM_TIME + (u.men * config.LOOSE_SQUEEZE if squeeze else 0.0)
        return t_loose + config.FORMATION_MARGIN < t_block

    def _block_passes(self, u: Lochos, wp: Point) -> bool:
        """Kommt die Gruppe als Block um die eigene Gruppe herum, die im Weg ruht (über den
        Umweg ``wp`` neben ihr, ohne Wall, Haus oder Kartenrand), und ist das nicht langsamer,
        als sich aufzulösen und neu zu formieren? Nur mit dem Marsch im Bogen."""
        if not config.MARCH_ARC or u.target is None:
            return False
        if not self.inside(*wp) or self.is_blocked(wp[0], wp[1], u):
            return False
        if self._loose_faster(u, dist(u.pos, wp) + dist(wp, u.target), dist(u.pos, u.target)):
            return False                          # Mann für Mann vorbei ist schneller
        r = self._block_width(u)
        return (self.path_clear(u.pos, wp, u) and self.path_clear(wp, u.target, u)
                and self._wide_clear(u.pos, wp, r) and self._wide_clear(wp, u.target, r))

    def _way_open(self, u: Lochos) -> bool:
        """Gibt es für die Männer einen Weg zur Zielaufstellung (um stehende eigene Gruppen herum)?"""
        if u.loose:
            slots, dest, facing = self._dest_slots(u), u.dest, u.dest_facing or u.facing
        else:
            dest = u.target
            facing = u.face_to or (u.facing if u.stance is Stance.PHALANX or dist(u.pos, dest) < 0.3
                                   else norm(sub(dest, u.pos)))
            slots = u.slots_at(dest, facing)
        field_ = self._field(u, slots, dest, facing)
        return any(field_.near_reachable(m.pos) for m in u.all_men())

    @staticmethod
    def _via(u: Lochos) -> Point | None:
        """Der vorgeschriebene Übergang: solange das Ziel dasselbe ist, und danach, bis die
        Gruppe drüben wieder geschlossen ist (wer noch draußen steht, nimmt denselben Weg)."""
        if u.via is not None and u.target is not None and (u.via[1] == u.target or u.loose and u.loose_why == "wall"):
            return u.via[0]
        return None

    def _dissolve(self, u: Lochos, why: str) -> None:
        if u.march is not None and u.march[0] == u.target:
            self._deploy(u)                       # jeder geht einzeln an seinen Platz: gleich in der befohlenen Aufstellung
        if u.full_width is not None:
            u.reform(u.full_width)                # aufgelöst zählt wieder die volle Breite
            u.full_width = None
        u.loose = True
        u.loose_why = why
        u.in_line = False
        u.waiting = False
        u.idle_block = False
        u.vel = 0.0
        u.dest = None
        if why == "wall":
            if u.stance is Stance.PHALANX:
                u.stance = Stance.HALTEN
            u.over_wall = True
            self.events.append(f"{u.name}: Formation aufgelöst, Mann für Mann über den Wall")
        for m in u.all_men():
            m.wp = None
        self._aim_dest(u)

    def _aim_dest(self, u: Lochos) -> None:
        """Zielaufstellung setzen: Mitte am Ziel, Front wie befohlen; sonst zum Feind
        hin, für eine Phalanx wie sie steht, für alle anderen in Marschrichtung. Die
        Front bleibt, solange sich das Ziel nicht verlegt."""
        t = u.target if u.target is not None else (u.dest or u.pos)
        if u.stance is Stance.FLUCHT:
            u.muster = None                               # wer flieht, sammelt sich nicht
        elif u.target is not None and (u.loose_why == "wall" or u.muster is not None):
            m = u.muster
            if m is None or self._wall_level(u.target) != self._wall_level(m[0]):
                m = self._muster_for(u, u.target)
            if m is not None and dist(u.target, m[0]) < config.MUSTER_SKIP:
                m = None                                  # das Ziel liegt gleich hinter dem Wall: dort sammelt man sich
            if m is None:
                u.muster_since = -1.0
            u.muster = m
        if u.muster is not None:
            t = u.muster[0]                               # erst zum Sammelplatz hinter dem Wall
        moved = u.dest is None or dist(t, u.dest) > 0.3
        if moved or u.target_id is not None or u.face_to is not None:
            c = self._men_centre(u)
            if u.muster is not None:
                f = u.muster[1]
            elif u.face_to is not None:
                f = u.face_to
            elif u.loose_why == "wall" and self._wall_level(c) != self._wall_level(t) and dist(t, c) > 0.3:
                if self.ring:
                    f = norm(sub(t, c))                   # über den Wall: die Front zum Ziel
                else:
                    f = (0.0, 1.0 if t[1] > c[1] else -1.0)   # über den Wall: die Front vom Wall weg
            elif u.target_id is not None or u.stance is not Stance.PHALANX:
                f = norm(sub(t, c)) if dist(t, c) > 0.3 else (u.dest_facing or u.facing)
            else:
                f = u.dest_facing or u.facing
            turned = u.dest_facing is None or (f[0] * u.dest_facing[0] + f[1] * u.dest_facing[1]) < 0.94
            u.dest_facing = f
            if turned:
                self._sort_rows(u, f)
        u.dest = t
        u.facing = u.dest_facing

    def _muster_for(self, u: Lochos, target: Point) -> tuple[Point, Point] | None:
        """Sammelplatz hinter dem Wall: am Fuß der Leiter, über die die Männer drüben
        hinabsteigen, mit etwas Abstand zum Wall, die Front zum eigentlichen Ziel. Nur
        solange noch Männer diesseits oder oben stehen."""
        if not self.blocked:
            return None
        side_level = self._wall_level(target)
        if side_level not in ("nord", "sued", "innen", "aussen"):
            return None
        men = u.all_men()
        if not men or all(self._wall_level(m.pos) == side_level for m in men):
            return None
        c = self._men_centre(u)
        via = self._via(u)
        if via is not None:
            ascent = via
        elif self.is_wall_cell(self.cell(*c), True):
            ascent = c
        else:
            ascent = self.nearest_ladder(u, c, target)
        down = self.nearest_ladder(u, ascent, target) if ascent is not None else None
        if self.ring:
            return self._muster_ring(u, target, down or ascent or c)
        x = (down or ascent or c)[0]
        side = 1.0 if side_level == "sued" else -1.0
        wall_y = next(iter(self.blocked))[1]
        y0 = wall_y + 0.5 + side * (0.5 + u.half_d + config.MUSTER_GAP)
        facing = u.face_to or (norm(sub(target, (x, y0))) if dist(target, (x, y0)) > 0.3 else (0.0, side))
        # Ausdehnung der Aufstellung quer zum Wall und längs: so weit vom Wall weg, dass niemand auf ihm steht
        ext_y = abs(facing[1]) * u.half_d + abs(facing[0]) * u.half_w
        ext_x = abs(facing[0]) * u.half_d + abs(facing[1]) * u.half_w
        y0 = wall_y + 0.5 + side * (0.5 + ext_y + config.MUSTER_GAP)
        # nicht auf den Sammelplatz einer anderen Gruppe und nicht in eine stehende eigene: daneben, sonst weiter vom Wall weg
        taken = []
        for g in self.lochoi:
            if g is u or g.side is not u.side or not g.alive:
                continue
            if g.muster is not None:
                (gx, gy), _, (gex, gey) = g.muster
                taken.append((gx, gy, gex, gey))
            elif not g.loose and self._standing(g):
                cs = g.corners()
                taken.append(((min(c[0] for c in cs) + max(c[0] for c in cs)) / 2, (min(c[1] for c in cs) + max(c[1] for c in cs)) / 2,
                              (max(c[0] for c in cs) - min(c[0] for c in cs)) / 2, (max(c[1] for c in cs) - min(c[1] for c in cs)) / 2))

        def free(px: float, py: float) -> bool:
            return all(abs(px - tx) >= ext_x + tex + 0.15 or abs(py - ty) >= ext_y + tey + 0.15 for tx, ty, tex, tey in taken)
        spot = None
        for ring in range(4):
            y = y0 + side * ring * (2 * ext_y + 0.3)
            for k in (0, 1, -1, 2, -2, 3, -3):
                px_ = min(max(x + k * (2 * ext_x + 0.3), ext_x + 0.2), self.cols - ext_x - 0.2)
                if 0.5 <= y <= self.rows - 0.5 and not self.is_blocked(px_, y, u) and free(px_, y):
                    spot = (px_, y)
                    break
            if spot is not None:
                break
        if spot is None:
            spot = (min(max(x, ext_x + 0.2), self.cols - ext_x - 0.2), y0)
        return self._free_spot(spot, u), facing, (ext_x, ext_y)

    def _muster_ring(self, u: Lochos, target: Point, near: Point) -> tuple[Point, Point, Point]:
        """Festung: Sammelplatz vor dem Fuß der Leiter, über die man hinabsteigt, vom Wall
        weg, jede Gruppe auf ihrem eigenen Fleck."""
        level = self._wall_level(target)
        c = self.cell(*near)
        if self.is_wall_cell(c, True):
            foot = self.foot_of(c) if (c in self.ladders or c in self.crossings) else near
        else:
            foot = near
        fx, fy = foot
        dx, dy = norm(sub(foot, (c[0] + 0.5, c[1] + 0.5))) if dist(foot, (c[0] + 0.5, c[1] + 0.5)) > 0.1 else (0.0, 1.0)
        facing = u.face_to or (norm(sub(target, foot)) if dist(target, foot) > 0.3 else (dx, dy))
        ext_n = abs(facing[0] * dx + facing[1] * dy) * u.half_d + abs(-facing[1] * dx + facing[0] * dy) * u.half_w
        ext_t = abs(facing[0] * dx + facing[1] * dy) * u.half_w + abs(-facing[1] * dx + facing[0] * dy) * u.half_d
        ext_x = abs(facing[0]) * u.half_d + abs(facing[1]) * u.half_w
        ext_y = abs(facing[1]) * u.half_d + abs(facing[0]) * u.half_w
        taken = [g.muster[0] for g in self.lochoi if g is not u and g.side is u.side and g.alive and g.muster is not None]
        taken += [g.pos for g in self.lochoi if g is not u and g.side is u.side and g.alive and not g.loose and self._standing(g)]
        tx, ty = -dy, dx
        spot = None
        for ring in range(4):
            d0 = 0.5 + ext_n + config.MUSTER_GAP + ring * (2 * ext_n + 0.3)
            for k in (0, 1, -1, 2, -2, 3, -3):
                off = k * (2 * ext_t + 0.3)
                q = (fx - dx * 0.5 + dx * d0 + tx * off, fy - dy * 0.5 + dy * d0 + ty * off)
                if not self.inside(*q) or self.is_blocked(*q, u) or self._wall_level(q) != level:
                    continue
                if any(dist(q, t) < max(ext_n, ext_t) * 2 + 0.3 for t in taken):
                    continue
                spot = q
                break
            if spot is not None:
                break
        if spot is None:
            spot = foot
        return self._free_spot(spot, u), facing, (ext_x, ext_y)

    @staticmethod
    def _sort_rows(u: Lochos, facing: Point) -> None:
        """Jede Reihe so ordnen, dass jeder Mann den Platz der Zielreihe nimmt, der auf
        seiner Seite liegt: Die Männer laufen dann nebeneinander statt quer durcheinander.
        Wer in welcher Reihe steht, bleibt (vorn bleiben die Schweren)."""
        ax, ay = -facing[1], facing[0]
        for row in u.rows:
            row.sort(key=lambda m: m.x * ax + m.y * ay)

    def _dest_slots(self, u: Lochos) -> list[tuple[Man, Point]]:
        dest = u.dest if u.dest is not None else u.pos
        return u.slots_at(dest, u.dest_facing or u.facing, self._wall_level(dest) == "wall")

    @staticmethod
    def _men_centre(u: Lochos) -> Point:
        men = u.all_men()
        if not men:
            return u.pos
        return (sum(m.x for m in men) / len(men), sum(m.y for m in men) / len(men))

    def _may_close(self, u: Lochos) -> bool:
        """Darf die aufgelöste Gruppe wieder als Block gehen? Ohne Ziel, im Kampf, auf der
        Flucht und beim Angriff sofort; sonst erst, wenn sie angekommen ist oder ihre
        Männer geschlossen gehen (jeder etwa gleich weit hinter seinem Platz)."""
        if u.target is None or u.engaged or u.stance is Stance.FLUCHT or u.target_id is not None:
            return True
        if u.stay_loose and self.time - u.stay_since > config.STAY_LOOSE_MAX:
            u.stay_loose = False                          # lange genug gewartet: wie sonst schließen
        if u.stay_loose:
            slots = self._dest_slots(u)                   # nach einem Stau: erst schließen, wenn alle da sind
            return not slots or all(dist(m.pos, p) <= config.SLOT_TOLERANCE or
                                    (dist(m.pos, p) <= config.BLOCKED_SLOT_REACH and self.is_blocked(p[0], p[1], u))
                                    for m, p in slots)
        if u.loose_why in ("tor", "eigene", "") and not self._way_open(u):
            return True                                   # der Weg ist zu: als Block anstehen
        if u.muster is not None:
            if u.muster_since < 0.0:
                u.muster_since = self.time                # alle drüben: jetzt wird nur noch gesammelt
            elif self.time - u.muster_since > config.MUSTER_WAIT:
                return True                               # lange genug gewartet: als Block weiter, die Letzten rücken nach
        slots = self._dest_slots(u)
        if not slots:
            return True
        lags = [(m.x - p[0], m.y - p[1]) for m, p in slots]
        there = sum(1 for (m, p), (lx, ly) in zip(slots, lags) if math.hypot(lx, ly) <= config.SLOT_TOLERANCE
                    or (math.hypot(lx, ly) <= config.BLOCKED_SLOT_REACH and self.is_blocked(p[0], p[1], u)))
        # (ein Platz im Haus oder im Gerät ist nicht zu erreichen: wer davor steht, ist da)
        if there >= config.SLOT_SHARE * len(lags):
            return True
        mx = sum(l[0] for l in lags) / len(lags)
        my = sum(l[1] for l in lags) / len(lags)
        rest = math.hypot(mx, my)
        if rest < config.LOOSE_CLOSE_DISTANCE:
            return False                                  # das letzte Stück geht jeder selbst: am Ziel steht man dann schon
        if u.stance is not Stance.PHALANX and u.dest_facing is not None:
            ahead = (-mx * u.dest_facing[0] - my * u.dest_facing[1]) / rest
            if ahead < math.cos(config.MOVE_TURN_TOLERANCE):
                return False                              # der Block müsste für den Rest schwenken: lieber so weiter
        return all(math.hypot(lx - mx, ly - my) <= config.LOOSE_COHESION for lx, ly in lags)

    def _close(self, u: Lochos) -> None:
        """Die Gruppe schließt sich dort, wo ihre Männer stehen: Mitte der Zielaufstellung
        plus der mittlere Rückstand der Männer, mit der Front der Zielaufstellung."""
        u.stay_loose = False
        slots = self._dest_slots(u)
        anchor = u.dest if u.dest is not None else u.pos
        there = sum(1 for m, p in slots if dist(m.pos, p) <= config.SLOT_TOLERANCE)
        if slots and there < config.SLOT_SHARE * len(slots):      # angekommen: genau am Ziel, die Letzten rücken nach
            lx = sum(m.x - p[0] for m, p in slots) / len(slots)
            ly = sum(m.y - p[1] for m, p in slots) / len(slots)
            anchor = (anchor[0] + lx, anchor[1] + ly)
        level = self._wall_level(u.pos)
        if not self.inside(*anchor) or self.is_blocked(*anchor, u) or self._wall_level(anchor) != level:
            anchor = u.pos                                # dort, wo der mittlere Mann steht
        u.x, u.y = anchor
        if u.dest_facing is not None:
            u.facing = u.dest_facing
        u.loose = False
        u.loose_why = ""
        u.dest = None
        u.via = None
        u.muster = None
        u.muster_since = -1.0
        u.idle_block = False
        for m in u.all_men():
            m.wp = None
        if u.over_wall:
            self.events.append(f"{u.name}: Formation neu gebildet")
        u.over_wall = False

    def _settle(self, u: Lochos) -> None:
        """Eine aufgelöste Gruppe auf Befehl gleich hier schließen (nicht mitten auf dem Wall)."""
        if u.loose and u.loose_why != "wall":
            self._close(u)

    def _loose_centre(self, u: Lochos) -> Point:
        """Wo die aufgelöste Gruppe ist: im Schwerpunkt der Männer auf der Wallseite,
        auf der die meisten stehen. Liegt er auf keinem begehbaren Fleck dieser Seite
        oder in einer anderen Gruppe (die Männer gehen links und rechts an ihr vorbei),
        beim Mann, der der bisherigen Mitte am nächsten steht."""
        men = u.all_men()
        if not men:
            return u.pos
        if self.blocked:
            levels: dict[str, list[Man]] = {}
            for m in men:
                levels.setdefault(self._wall_level(m.pos), []).append(m)
            level, men = max(levels.items(), key=lambda kv: len(kv[1]))
        else:
            level = None
        c = (sum(m.x for m in men) / len(men), sum(m.y for m in men) / len(men))
        others = [o for o in self.lochoi if o is not u and o.alive and not o.loose]
        if (self.is_blocked(*c, u) or (level is not None and self._wall_level(c) != level)
                or any(o.rect_distance(c) == 0.0 for o in others)):
            # (wer dicht an der anderen Gruppe entlanggeht, steht noch in ihrem Rand: lieber einer weiter außen)
            clear = [m for m in men if not any(o.rect_distance(m.pos) == 0.0 for o in others)] or men
            m = min(clear, key=lambda m: (m.x - u.x) ** 2 + (m.y - u.y) ** 2)
            return (m.x, m.y)
        return c

    def _field(self, u: Lochos, slots: list[tuple[Man, Point]], dest: Point | None = None,
               facing: Point | None = None) -> pathing.Field:
        """Wegefeld zu den Plätzen der Zielaufstellung; Hindernisse sind Palisade,
        geschlossenes Tor und stehende eigene Gruppen (außer lockeren Peltasten).
        Feinde nicht: an ihnen bleibt man hängen und kämpft. Es wird alle
        ``FIELD_REFRESH`` Sekunden neu gerechnet."""
        dest = dest if dest is not None else (u.dest or u.pos)
        facing = facing if facing is not None else (u.dest_facing or u.facing)
        closed = tuple(g.closed for g in self.gates)
        key = (round(dest[0], 1), round(dest[1], 1), round(facing[0], 2), round(facing[1], 2), closed, len(slots),
               self._engines_key)
        cached = self._fields.get(u.id)
        refresh = config.FIELD_REFRESH * (0.8 + 0.4 * ((u.id * 0.618) % 1.0))   # nicht alle Gruppen im selben Takt
        if cached is not None and cached[0] == key and self.time - cached[1] < refresh:
            return cached[2]
        if cached is not None and self._field_builds.get(self.time, 0) >= self._field_budget():
            return cached[2]                              # genug gerechnet in diesem Takt: das bisherige Feld tut es noch
        self._field_builds = {self.time: self._field_builds.get(self.time, 0) + 1}
        cell = config.FIELD_CELL
        key = (closed, self._engines_key)
        if self._static_grid is None or self._static_grid[0] != key:
            self._static_grid = (key, pathing.grid(self.cols, self.rows, cell, lambda x, y: self.is_blocked(x, y)))
        blocked = bytearray(self._static_grid[1])
        margin = config.FIELD_MARGIN
        for o in self.lochoi:
            if o is u or o.side is not u.side or not o.alive or o.loose or self.on_wall(o):
                continue
            if self._passable(o) or not self._standing(o):
                continue                          # wer selbst unterwegs ist, dem weicht man Mann für Mann aus
            pathing.mark(blocked, self.cols, self.rows, cell, o.pos, o.radius + margin + cell,
                         lambda p, o=o: o.rect_distance(p) <= margin)
        edge = cell / 2                                   # Plätze jenseits des Kartenrands (Flucht): an den Rand
        goals = [(min(max(p[0], edge), self.cols - edge), min(max(p[1], edge), self.rows - edge)) for _, p in slots]
        field_ = pathing.Field(self.cols, self.rows, cell, blocked, goals, needed=[m.pos for m in u.all_men()])
        self._fields[u.id] = (key, self.time, field_)
        return field_

    def _field_budget(self) -> int:
        return 1 if self.ring else config.FIELD_BUDGET     # große Karte: jedes Feld kostet mehr

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
        self._man_grid = {}
        self._man_group = {}
        self._man_side = {}
        self._group_map = {u.id: u for u in self.lochoi if u.alive}
        for u in self.lochoi:
            if u.alive:
                for m in u.all_men():
                    self._man_grid.setdefault(self._grid_cell(m.x, m.y), []).append((m, u.id))
                    self._man_group[id(m)] = u.id
                    self._man_side[id(m)] = u.side
        for u in self.lochoi:
            if not u.alive:
                continue
            walker = self.is_walker(u)
            u.file = self.on_wall(u)
            self._bind_men(u)
            if u.loose:
                self._move_loose(u, dt, walker)
                continue
            assault = self._assault_slots(u)
            u.assault_slots = [slot for _, slot in assault] if assault is not None else []
            for man, slot in (assault if assault is not None else u.slots()):
                d = dist(man.pos, slot)
                if assault is not None:               # um den Gegner herum: dicht an seinen Umriss, nie hinein
                    self._man_step(u, man, slot, max(u.speed, man.speed) * config.MAN_CATCHUP * dt, walker, through=True)
                    continue
                if man.bound and dist(slot, man.stand or man.pos) > config.BOUND_SHUFFLE:
                    continue                          # steht im Handgemenge fest, rückt höchstens etwas nach
                if d <= 0.02:
                    if self._crowding(man, man.pos, slot, u.id) is None and self._man_can_step(u, man, man.pos, slot, walker):
                        man.x, man.y = slot
                    continue
                speed = max(u.speed, man.speed) * config.MAN_CATCHUP
                if not self._man_step(u, man, slot, speed * dt, walker, slide=False):
                    goal, _ = self.route_from(u, man.pos, slot)     # Umweg (Tor), statt an der Palisade zu kriechen
                    self._man_step(u, man, goal, speed * dt, walker)

    def _move_loose(self, u: Lochos, dt: float, walker: bool) -> None:
        """Aufgelöst: jeder Mann geht für sich an seinen Platz in der Zielaufstellung.
        Über den Wall führen Leiter und Turm (vor ihnen stellt man sich an), sonst
        sucht er seinen Weg im Wegefeld, um Palisade, eigene stehende Gruppen und
        feindliche Formationen herum. Er geht im Tempo der Gruppe; wer weiter zurück
        ist als die anderen oder noch klettert, holt auf. Die Gruppe steht danach
        dort, wo der mittlere ihrer Männer steht."""
        slots = self._dest_slots(u)
        if not slots:
            return
        dest_level = self._wall_level(u.dest if u.dest is not None else u.pos)
        gate_open = any(not g.closed for g in self.gates)
        via = self._via(u)
        remaining = sorted(dist(m.pos, p) for m, p in slots)
        median = remaining[len(remaining) // 2]
        field_: pathing.Field | None = None
        goals: list[tuple[Man, Point, Point, bool]] = []
        for man, slot in slots:
            d = dist(man.pos, slot)
            if d <= 0.02:
                if self._crowding(man, man.pos, slot, u.id) is None and self._man_can_step(u, man, man.pos, slot, walker):
                    man.x, man.y = slot
                continue
            man_level = self._wall_level(man.pos)
            climbing = walker and (man_level == "wall" or dest_level == "wall" or (
                man_level != dest_level and (via is not None or man.stall > config.STALL_TIME
                                             or "tor" not in (man_level, dest_level) and not gate_open)))
            # (wer auf dem Weg durchs Tor nicht vorankommt, nimmt Leiter oder Turm)
            if climbing and via is not None and man_level not in ("wall", dest_level):
                goal, _ = self.route_from(u, man.pos, via)          # erst auf den vorgeschriebenen Turm
            elif climbing:
                goal, _ = self.route_from(u, man.pos, slot)
            elif man.wp is not None and self.time < man.wp_until and dist(man.pos, man.wp) > 0.05:
                goal = man.wp
            else:
                if field_ is None:
                    field_ = self._field(u, slots)
                goal = field_.waypoint(man.pos, slot)
                man.wp = goal if goal != slot else None
                man.wp_until = self.time + config.WAYPOINT_TIME
            lagging = climbing or man_level != dest_level or d > median + config.LOOSE_LAG
            goals.append((man, goal, slot, lagging))
        # vor einer Leiter anstellen: wer näher ist, steht weiter vorn
        ranks: dict[int, int] = {}
        for cell in {self.cell(*g) for _, g, _, _ in goals}:
            if cell in self.ladders or cell in self.crossings:
                waiting = sorted((m for m, g, _, _ in goals if self.cell(*g) == cell),
                                 key=lambda m: dist(m.pos, (cell[0] + 0.5, cell[1] + 0.5)))
                for rank, m in enumerate(waiting):
                    ranks[id(m)] = rank
        for man, goal, slot, lagging in goals:
            if man.bound and dist(goal, man.stand or man.pos) > config.BOUND_SHUFFLE:
                continue
            goal = self._queue_spot(goal, man, ranks.get(id(man), 0))
            speed = max(u.speed, man.speed) * config.MAN_CATCHUP if lagging else u.speed
            before = man.pos
            # wer über den Wall kommt, bleibt drüben an Feinden hängen (kein Entlanggleiten um sie herum)
            self._man_step(u, man, goal, speed * dt, walker, stick=u.loose_why == "wall")
            man.stall = man.stall + dt if dist(before, man.pos) < 0.2 * speed * dt else 0.0
        u.x, u.y = self._loose_centre(u)

    def _bind_men(self, u: Lochos) -> None:
        """Wer einen feindlichen Mann in Reichweite hat, steht im Handgemenge fest
        (nicht schon, wer nur dem Rechteck des Gegners nahe ist: dort steht vielleicht
        niemand). Zieht die Gruppe weiter als die Leine, reißt er sich los, und die
        Gruppe ist eine Weile verwundbar (Lösen kostet)."""
        up = self.on_wall(u)
        foes = [e for e in self.lochoi if e.side is not u.side and e.fighting and self.on_wall(e) == up
                and dist(e.pos, u.pos) <= e.radius + u.radius + config.MAN_RELEASE_REACH + 1.0]
        if not foes or u.stance is Stance.FLUCHT:
            for m in u.all_men():
                m.bound = False
            return
        released = False
        foe_ids = {e.id for e in foes}
        slot_of = {id(m): p for m, p in (self._dest_slots(u) if u.loose else u.slots())}
        for m in u.all_men():
            # gemessen von der Stelle, an der er gebunden wurde: wer nur nachrückt, läuft nicht davon
            nearest, _ = self._nearest_foe_man(m.stand if m.bound and m.stand else m.pos, foe_ids,
                                               config.MAN_RELEASE_REACH)
            if m.bound:
                if nearest > config.MAN_RELEASE_REACH:
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

    def _nearest_foe_man(self, p: Point, foe_ids: set[int], reach: float) -> tuple[float, Man | None]:
        """Der nächste Mann der Gruppen ``foe_ids`` bis ``reach`` um ``p`` (sonst unendlich, None)."""
        cx, cy = self._grid_cell(*p)
        r = int(math.ceil(reach * 2))
        best, best_m = math.inf, None
        for gx in range(cx - r, cx + r + 1):
            for gy in range(cy - r, cy + r + 1):
                for o, uid in self._man_grid.get((gx, gy), ()):
                    if uid in foe_ids:
                        d = math.hypot(o.x - p[0], o.y - p[1])
                        if d < best:
                            best, best_m = d, o
        return (best, best_m) if best <= reach else (math.inf, None)

    def _queue_spot(self, goal: Point, man: Man, i: int) -> Point:
        """Führt der Weg an eine besetzte Leiter, stellt sich der Mann davor an,
        statt sich mit allen anderen auf denselben Punkt zu stellen."""
        cell = self.cell(*goal)
        if self._wall_level(man.pos) == "wall" or (cell not in self.ladders and cell not in self.crossings):
            return goal
        if i == 0 or (self.climb_budget.get(cell, 1.0) >= 1.0 and dist(man.pos, goal) < 0.9):
            return goal
        if self.ring:
            fx, fy = self.foot_of(cell)
            dx, dy = fx - cell[0] - 0.5, fy - cell[1] - 0.5          # zum Fuß, waagrecht oder senkrecht
            px_, py_ = abs(dy), abs(dx)
            k = 0.75 + (i // 6) * 0.15
            o = ((i % 6) - 2.5) * 0.14
            return (cell[0] + 0.5 + dx * k + px_ * o, cell[1] + 0.5 + dy * k + py_ * o)
        side = 1.0 if man.y > cell[1] + 0.5 else -1.0
        return (cell[0] + 0.5 + ((i % 6) - 2.5) * 0.14, cell[1] + 0.5 + side * (0.75 + (i // 6) * 0.15))

    def _assault_slots(self, u: Lochos) -> list[tuple[Man, Point]] | None:
        """Eine angreifende Gruppe im Handgemenge legt sich um den Gegner: Ihre
        Männer verteilen sich Reihe für Reihe entlang des feindlichen Umrisses,
        um das nächstgelegene Stück herum, also wie ein C um das Ende einer
        Linie. So kommen alle an den Feind, statt hinten im Rechteck zu warten."""
        if u.stance is not Stance.ANGRIFF or u.loose or not u.contacts or self.on_wall(u) or u.formation == "keil":
            return None
        if u.mounted_men():
            return None                                   # Reiter halten ihre Reihen, auch im Sturm
        hoplites = u.share(lambda m: m.kind.hoplite) >= 0.5   # Hopliten bleiben ein Block, nur die Flügel klappen ein
        foe = self.by_id(u.target_id) if u.target_id in u.contacts else self.by_id(u.contacts[0])
        if foe is None or not foe.alive or foe.loose or self.on_wall(foe):
            return None
        fx, fy = foe.facing
        ax, ay = -fy, fx
        W, D = foe.half_w, foe.half_d
        corners = [(-W, D), (W, D), (W, -D), (-W, -D)]          # Front, rechte Seite, Rücken, linke Seite
        normals = [(0.0, 1.0), (1.0, 0.0), (0.0, -1.0), (-1.0, 0.0)]
        lengths = [2 * W, 2 * D, 2 * W, 2 * D]
        perimeter = sum(lengths)

        def local(p: Point) -> tuple[float, float]:
            dx, dy = p[0] - foe.x, p[1] - foe.y
            return (dx * ax + dy * ay, dx * fx + dy * fy)

        def param(p: Point) -> float:
            """Umlaufparameter des Umrisspunkts, der ``p`` am nächsten liegt."""
            al, fw = local(p)
            best, best_d = 0.0, float("inf")
            t = 0.0
            for (c, n, ln) in zip(corners, normals, lengths):
                nxt = corners[(corners.index(c) + 1) % 4]
                # Projektion auf die Kante c -> nxt
                ex, ey = nxt[0] - c[0], nxt[1] - c[1]
                s_ = max(0.0, min(1.0, ((al - c[0]) * ex + (fw - c[1]) * ey) / (ln * ln)))
                qx, qy = c[0] + ex * s_, c[1] + ey * s_
                d = (al - qx) ** 2 + (fw - qy) ** 2
                if d < best_d:
                    best, best_d = t + s_ * ln, d
                t += ln
            return best

        def point(t: float, out: float) -> Point:
            t %= perimeter
            for c, n, ln in zip(corners, normals, lengths):
                if t <= ln:
                    nxt = corners[(corners.index(c) + 1) % 4]
                    al = c[0] + (nxt[0] - c[0]) * t / ln + n[0] * out
                    fw = c[1] + (nxt[1] - c[1]) * t / ln + n[1] * out
                    return (foe.x + ax * al + fx * fw, foe.y + ay * al + fy * fw)
                t -= ln
            return foe.pos
        t0 = param(u.pos)

        def offset_of(t: float) -> float:
            return (t - t0 + perimeter / 2) % perimeter - perimeter / 2

        def offset(m: Man) -> float:
            """Lage des Mannes entlang des Umrisses, relativ zur Mitte des Angriffs."""
            return offset_of(param(m.pos))

        # Nur dort, wo wirklich Feinde stehen: der Umriss wird abgetastet, und ein Stück
        # zählt nur, wenn ein feindlicher Mann daran steht (nicht das leere Rechteck)
        enemy_men = foe.all_men()
        step = config.MAN_SPACING / 2
        manned: list[float] = []
        t = 0.0
        while t < perimeter:
            px_, py_ = point(t, 0.0)
            if any((m.x - px_) ** 2 + (m.y - py_) ** 2 <= config.ASSAULT_MANNED ** 2 for m in enemy_men):
                manned.append(t)
            t += step
        if not manned:
            return None
        # zusammenhängende besetzte Stücke bilden; das nächste davon ist das Ziel
        runs: list[list[float]] = []
        for off in sorted(offset_of(t) for t in manned):
            if runs and off - runs[-1][-1] <= step * 2.5:     # eine einzelne Lücke (etwa an einer Ecke) trennt nicht
                runs[-1].append(off)
            else:
                runs.append([off])
        if len(runs) > 1 and runs[0][0] + perimeter - runs[-1][-1] <= step * 2.5:
            runs[0] = runs.pop() + [o + perimeter for o in runs[0]]     # über den Umlaufanfang hinweg zusammenhängend
        run_near = min(runs, key=lambda r: min(abs(o) for o in r))
        run_near.sort(key=abs)                                # vom nächsten Punkt aus nach außen
        if hoplites:
            return self._wing_slots(u, foe, param, offset_of, point, lengths, perimeter, run_near)
        # Wo schon eine eigene Gruppe am Gegner steht (die früher im Handgemenge war),
        # stellt sich niemand hinein: Man legt sich daneben an das nächste freie Stück
        since = u.contact_since.get(foe.id, self.time)
        band = config.ASSAULT_GAP + 3 * config.ROW_SPACING
        taken: set[int] = set()
        for o in self.lochoi:
            if o is u or o.side is not u.side or not o.alive or foe.id not in o.contacts:
                continue
            o_since = o.contact_since.get(foe.id, self.time)
            if (o_since, o.id) >= (since, u.id):
                continue                                      # wer später kam, weicht
            for q in [n.pos for n in o.all_men()] + o.assault_slots:     # wo sie stehen und wo sie hinwollen
                if foe.rect_distance(q) <= band:
                    k = round((param(q) % perimeter) / step)
                    taken.update((k - 1, k, k + 1))
        if taken:
            free = [o for o in run_near if round(((t0 + o) % perimeter) / step) not in taken]
            pieces: list[list[float]] = []
            for off in sorted(free):
                if pieces and off - pieces[-1][-1] <= step * 2.5:
                    pieces[-1].append(off)
                else:
                    pieces.append([off])
            if not pieces:
                return None                               # kein freies Stück mehr: im Block dahinter warten
            run_near = min(pieces, key=lambda r: min(abs(o) for o in r))
            run_near.sort(key=abs)
        out: list[tuple[Man, Point]] = []
        for k, row in enumerate(u.rows):                      # Reihe für Reihe: die vordere innen, jede behält ihre Nachbarn
            layer = sorted(row, key=offset)
            n = len(layer)
            want = max(1, min(len(run_near), math.ceil(n * config.MAN_SPACING / step)))
            offs = sorted(run_near[:want])                    # das nächste besetzte Stück, relativ zur Angriffsmitte
            span = offs[-1] - offs[0]
            per_rank = max(1, int(span / config.MAN_SPACING) + 1)   # so viele passen nebeneinander
            outward = config.ASSAULT_GAP + k * config.ROW_SPACING
            for i, m in enumerate(layer):
                rank, col = divmod(i, per_rank)               # wer nicht mehr passt, steht eine Reihe weiter hinten
                cols = min(per_rank, n - rank * per_rank)
                tt = t0 + offs[0] + span / 2 + (col - (cols - 1) / 2) * config.MAN_SPACING
                out.append((m, point(tt, outward + rank * len(u.rows) * config.ROW_SPACING)))
        return out

    def _wing_slots(self, u: Lochos, foe: Lochos, param, offset_of, point, lengths, perimeter,
                    manned: list[float]) -> list[tuple[Man, Point]] | None:
        """Stürmende Hopliten gegen einen schmaleren Gegner: Der Block bleibt, nur
        die überstehenden Flügel klappen an den Ecken des Gegners bis an seine
        Flanken ein, nie in seinen Rücken, und nur wenn kein anderer Feind in der
        Nähe steht, dem die eingeklappten Männer den Rücken zukehren würden."""
        others = [e for e in self.lochoi if e.side is not u.side and e is not foe and e.fighting
                  and dist(e.pos, u.pos) <= e.radius + u.radius + config.WING_SAFE]
        if others:
            return None
        rect_slots = u.slots()
        # die Kante des Gegners, an der der Block anliegt, und ihre Ecken (Umlaufparameter)
        t0 = param(u.pos) % perimeter
        start, edge, edge_len = 0.0, 0, lengths[0]
        for i, ln in enumerate(lengths):
            if t0 <= start + ln:
                edge, edge_len = i, ln
                break
            start += ln
        corner_a, corner_b = start, start + edge_len          # in Umlaufrichtung: erst a, dann b
        side_before, side_after = lengths[(edge - 1) % 4], lengths[(edge + 1) % 4]
        manned_set = {round(o, 3) for o in manned}

        def is_manned(t: float) -> bool:
            o = offset_of(t)
            return any(abs(o - m) <= config.MAN_SPACING for m in manned_set)

        pa, pb = point(corner_a, 0.0), point(corner_b, 0.0)
        edge_dir = norm(sub(pb, pa))                          # Richtung der Kante, von Ecke a nach Ecke b
        out: list[tuple[Man, Point]] = []
        for k, row in enumerate(u.rows):
            row_slots = [(m, next(p for mm, p in rect_slots if mm is m)) for m in row]
            # die Reihe bleibt auf ihrem Abstand zum Gegner; die Flügel klappen auf demselben Abstand ein
            outward = min((foe.rect_distance(p) for _, p in row_slots), default=config.ASSAULT_GAP)
            outward = max(config.ASSAULT_GAP, outward)
            beyond_a: list[tuple[float, Man]] = []
            beyond_b: list[tuple[float, Man]] = []
            for m, slot in row_slots:
                t = param(slot) % perimeter
                if corner_a + 0.05 <= t <= corner_b - 0.05:
                    out.append((m, slot))                     # steht dem Gegner gegenüber: bleibt in der Reihe
                else:
                    o = offset_of(t)
                    (beyond_a if o < 0 else beyond_b).append((dist(slot, pa if o < 0 else pb), m))
            for corner, wing, side_len, direction, sign in ((corner_a, beyond_a, side_before, -1.0, -1.0),
                                                              (corner_b, beyond_b, side_after, 1.0, 1.0)):
                wing.sort(key=lambda x: x[0])                 # die der Ecke nächsten klappen zuerst ein
                folded = 0
                standing: list[Man] = []
                for _, m in wing:
                    along_side = (folded + 1) * config.MAN_SPACING
                    t = corner + direction * along_side
                    if along_side <= side_len - config.MAN_SPACING and is_manned(t):   # bis vor die hintere Ecke
                        out.append((m, point(t, outward)))
                        folded += 1
                    else:
                        standing.append(m)
                base = point(corner, outward)
                for i, m in enumerate(standing):              # Flanke voll: schließt in der Reihe zur Ecke auf, keine Lücke
                    out.append((m, (base[0] + edge_dir[0] * sign * (i + 1) * config.MAN_SPACING,
                                    base[1] + edge_dir[1] * sign * (i + 1) * config.MAN_SPACING)))
        return out

    @staticmethod
    def _grid_cell(x: float, y: float) -> tuple[int, int]:
        return (int(x * 2), int(y * 2))

    def _crowding(self, man: Man, a: Point, b: Point, own: int = -1) -> Man | None:
        """Der Mann, dem der Schritt von ``a`` nach ``b`` zu nahe käme: Kein Mann teilt
        seinen Platz mit einem anderen, auch nicht mit einem Fliehenden. Zwischen
        Männern verschiedener Gruppen bleibt es bei zwei Halbmessern; in der eigenen
        Gruppe (``own``) rückt man Schulter an Schulter, bis auf einen. Wer schon zu
        dicht steht, darf sich entfernen."""
        cx, cy = self._grid_cell(*b)
        friends = self._ring_friends.get(own) if self._ring_friends else None
        mover = self._group_map.get(own)
        side = self._man_side.get(id(man)) if mover is not None and mover.loose else None   # nur wer aufgelöst geht
        inside: dict[int, bool] = {}                      # eigene Gruppen, in deren Block er gerade steckt
        near: list[tuple[Man, bool, float, float]] = []
        nearest = {True: float("inf"), False: float("inf")}   # wie dicht er jetzt schon steht: eigene / fremde
        for gx in (cx - 1, cx, cx + 1):
            for gy in (cy - 1, cy, cy + 1):
                for o, uid in self._man_grid.get((gx, gy), ()):
                    if o is man or o.hp <= 0.0:
                        continue
                    if friends and uid in friends and uid != own:
                        continue                          # Ring im Ring desselben Verbands: man tritt aneinander vorbei
                    if uid != own and side is not None and self._man_side.get(id(o)) is side:
                        hit = inside.get(uid)
                        if hit is None:
                            g = self._group_map.get(uid)
                            hit = False
                            if g is not None and not g.loose and g.formation == "linie":
                                along, forward = g.local(man.pos)    # tief im Block, nicht nur an seinem Rand
                                hit = abs(along) < g.half_w - 0.12 and abs(forward) < g.half_d - 0.12
                            inside[uid] = hit
                        if hit:
                            continue                      # in einem eigenen Block eingeschlossen: durch seine Reihen hinaus
                    mine = uid == own
                    da = math.hypot(a[0] - o.x, a[1] - o.y)
                    nearest[mine] = min(nearest[mine], da)
                    near.append((o, mine, da, math.hypot(b[0] - o.x, b[1] - o.y)))
        for o, mine, da, db in near:
            limit = config.MAN_RADIUS if mine else 2 * config.MAN_RADIUS
            # zu nah, und näher als bisher an diesen Mann und als an den nächsten seiner Art:
            # wer schon an einer Reihe steht, darf an ihr entlang, nur nicht hinein
            if db < limit and db < da and db < nearest[mine] - 1e-9:
                return o
        return None

    def _step_aside(self, other: Man, man: Man, move: Point, u: Lochos) -> bool:
        """Steht ein Mann einer eigenen Gruppe in lockerer Ordnung (Peltasten, nicht im
        Handgemenge) im Weg, tritt er seitlich beiseite und lässt durch; danach geht er
        wieder an seinen Platz."""
        gid = self._man_group.get(id(other))
        if gid is None or gid == u.id or self._man_side.get(id(other)) is not u.side:
            return False
        g = self._group_map.get(gid)
        if g is None or not self._passable(g) or other.bound:
            return False
        n = math.hypot(*move)
        if n < 1e-9:
            return False
        mx, my = move[0] / n, move[1] / n
        px, py = -my, mx                                  # quer zum Weg des Durchgehenden
        rel = (other.x - man.x) * px + (other.y - man.y) * py
        side = 1.0 if rel > 0 or (abs(rel) < 1e-6 and id(other) % 2) else -1.0
        push = 2 * config.MAN_RADIUS - abs(rel) + 0.01
        nx, ny = other.x + px * side * push, other.y + py * side * push
        if (not self.inside(nx, ny) or self.is_blocked(nx, ny)
                or self._crowding(other, other.pos, (nx, ny), gid) is not None):
            return False
        other.x, other.y = nx, ny
        g.in_line = False
        return True

    def _shove(self, man: Man, other: Man, u: Lochos) -> bool:
        """Stürmende Reiter drängen einen Mann beiseite, statt vor ihm zu halten."""
        dx, dy = other.x - man.x, other.y - man.y
        d = math.hypot(dx, dy)
        if d < 1e-6:
            dx, dy, d = -u.facing[0], -u.facing[1], 1.0
        push = 2 * config.MAN_RADIUS - d + 0.01
        nx, ny = other.x + dx / d * push, other.y + dy / d * push
        if not self.inside(nx, ny) or self.is_blocked(nx, ny) or self._crowding(other, other.pos, (nx, ny), self._man_group.get(id(other), -1)) is not None:
            return False
        other.x, other.y = nx, ny
        return True

    def _man_step(self, u: Lochos, man: Man, goal: Point, step: float, walker: bool, slide: bool = True,
                  through: bool = False, stick: bool = False) -> bool:
        """Ein Schritt Richtung ``goal``; geht es nicht geradeaus, gleitet er entlang
        (``slide``) oder weicht dem aus, der im Weg steht. Mit ``stick`` gleitet er nicht
        an Feinden entlang: Wer an ihnen ankommt, bleibt hängen."""
        d = dist(man.pos, goal)
        if d < 1e-6:
            return True
        step = min(step, d)
        dx, dy = (goal[0] - man.x) / d * step, (goal[1] - man.y) / d * step
        options = [(man.x + dx, man.y + dy)]
        if slide:
            options += [(man.x + dx, man.y), (man.x, man.y + dy)]
        crowded: Man | None = None
        # erst die Enge prüfen, dann das Gelände: die Leiter zählt einen Aufstieg schon beim Prüfen
        for k, (nx, ny) in enumerate(options):
            if (nx, ny) == (man.x, man.y):
                continue
            blocker = self._crowding(man, man.pos, (nx, ny), u.id)
            if blocker is not None:
                crowded = crowded or blocker
                if stick and k == 0 and self._man_side.get(id(blocker), u.side) is not u.side:
                    break                                # ein Feind im Weg: nicht an ihm entlang
                continue
            if self._man_can_step(u, man, (man.x, man.y), (nx, ny), walker, through):
                man.x, man.y = nx, ny
                man.dodge = 0.0                          # der Weg ist frei
                return True
            if stick and k == 0 and self._walled_off(u, man.pos, (nx, ny), self._barrier_cache.get(u.side, [])):
                break                                    # vor einer feindlichen Formation: nicht an ihr entlang
        if crowded is None or man.bound:
            return False                                 # Gebundene rücken nur nach, sie weichen niemandem aus
        if self._rides(u) and u.ride_in > 0.0 and u.vel > 0.05 and self._shove(man, crowded, u):
            nx, ny = man.x + dx, man.y + dy                 # der Sturm drängt hindurch
            if self._crowding(man, man.pos, (nx, ny), u.id) is None and self._man_can_step(u, man, man.pos, (nx, ny), walker, through):
                man.x, man.y = nx, ny
                return True
        if self._step_aside(crowded, man, (dx, dy), u):
            nx, ny = man.x + dx, man.y + dy                 # der Leichte tritt beiseite: hindurch
            if self._crowding(man, man.pos, (nx, ny), u.id) is None and self._man_can_step(u, man, man.pos, (nx, ny), walker, through):
                man.x, man.y = nx, ny
                return True
        # jemand steht im Weg: an ihm entlang (in Richtung des Ziels), sonst schräg zurück, sonst zurück
        ax, ay = man.x - crowded.x, man.y - crowded.y
        n = math.hypot(ax, ay)
        if n < 1e-6:
            ax, ay, n = -dy, dx, step
        ax, ay = ax / n, ay / n                          # weg vom Blockierer
        tx, ty = -ay, ax                                 # an ihm entlang
        if man.dodge == 0.0:                             # eine Seite wählen und dabei bleiben, bis der Weg frei ist
            along = tx * dx + ty * dy
            man.dodge = (1.0 if along > 0 else -1.0) if abs(along) > 0.2 * step else (1.0 if id(man) % 2 else -1.0)
        tx, ty = tx * man.dodge, ty * man.dodge
        for vx, vy in ((tx, ty), (-tx, -ty), (tx + ax, ty + ay), (-tx + ax, -ty + ay), (ax, ay)):
            m_ = math.hypot(vx, vy)
            nx, ny = man.x + vx / m_ * step, man.y + vy / m_ * step
            if self._crowding(man, man.pos, (nx, ny), u.id) is None and self._man_can_step(u, man, man.pos, (nx, ny), walker, through):
                man.x, man.y = nx, ny
                return True
        return False

    def _man_can_step(self, u: Lochos, man: Man, a: Point, b: Point, walker: bool, through: bool = False) -> bool:
        ca, cb = self.cell(*a), self.cell(*b)
        wa = self.is_wall_cell(ca, walker)
        if self.is_blocked(b[0], b[1], u, from_wall=wa):
            return False
        if self.inside(*a) and not self.inside(*b) and u.stance is not Stance.FLUCHT:
            return False                      # der Kartenrand ist keine Umgehung
        if not through and self._walled_off(u, a, b, self._barrier_cache.get(u.side, [])):
            return False
        wb = self.is_wall_cell(cb, walker)
        if wb and cb != ca and config.WALL_NO_PASSING and u.side in self._wall_occupants().get(cb, ()):
            return False                      # Wehrgang: in eine Kachel, auf der ein Feind steht, kommt man nicht vorbei
        if wa == wb:
            return True
        if man.kind.cavalry and man.mounted:
            return False                      # beritten geht es weder hinauf noch hinunter
        if wb and not u.loose and not self.on_wall(u) and not (
                u.target is not None and self.is_wall_cell(self.cell(*u.target), True)):
            return False                      # ein Block am Boden steigt nicht aus Versehen auf die Leiter
        wall_cell, ground_cell = (ca, cb) if wa else (cb, ca)
        if wall_cell in self.ladders and self.ladder_ok(wall_cell, ground_cell):
            return self._climb(wall_cell)
        if wall_cell in self.crossings and u.side is not self.wall_side():
            return self.tower_ok(wall_cell, ground_cell) and self._climb(wall_cell)
        return False

    def _wall_occupants(self) -> dict:
        """Kachel des Wehrgangs -> Seiten, die dort NICHT hinein dürfen (weil ein Mann der
        Gegenseite darauf steht); einmal je Takt gerechnet. Der Wehrgang ist ein enger Gang:
        Wer weiter will, muss den Feind dort erst werfen."""
        if self._wall_occ is not None and self._wall_occ[0] == self.time:
            return self._wall_occ[1]
        occ: dict = {}
        for u in self.lochoi:
            if not u.alive or not u.fighting:
                continue
            other = Side.FEIND if u.side is Side.STADT else Side.STADT
            for m in u.all_men():
                c = self.cell(m.x, m.y)
                if self.is_wall_cell(c, True):
                    occ.setdefault(c, set()).add(other)
        self._wall_occ = (self.time, occ)
        return occ

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

    def _gap_at(self, u: Lochos, pos: Point, o: Lochos, facing: Point | None = None) -> float:
        """Lücke zwischen ``u`` (gedacht an ``pos``, wahlweise mit anderer Front) und ``o``, wie ``_gap``."""
        fx, fy = facing or u.facing
        ax, ay = -fy, fx

        def rect_distance(p: Point) -> float:
            dx, dy = p[0] - pos[0], p[1] - pos[1]
            if u.formation == "o":
                return max(0.0, math.hypot(dx, dy) - u.half_w)
            along, forward = dx * ax + dy * ay, dx * fx + dy * fy
            return math.hypot(max(0.0, abs(along) - u.half_w), max(0.0, abs(forward) - u.half_d))
        if facing is None or u.formation == "o":
            shifted = [(c[0] - u.x + pos[0], c[1] - u.y + pos[1]) for c in u.outline()]
        else:
            shifted = u.corners_at(pos, facing)
        return max(0.0, min(min(o.rect_distance(c) for c in shifted),
                            min(rect_distance(c) for c in o.outline())))

    @staticmethod
    def _extent(g: Lochos, px: float, py: float) -> float:
        """Halbe Ausdehnung der Formation entlang der Richtung (px, py)."""
        fx, fy = g.facing
        return abs(fx * px + fy * py) * g.half_d + abs(-fy * px + fx * py) * g.half_w

    def _own_in_the_way(self, u: Lochos, pos: Point) -> bool:
        """Führt der Schritt in eine eigene Gruppe hinein? In eine stehende (still, auf
        ihrem Posten, kämpfend, wartend) fährt niemand, auch keine breite Linie: Ist
        kein Umweg begehbar, wartet man dahinter. Gruppen, die beide unterwegs sind,
        weichen sich Mann für Mann aus; durch leichte Truppen geht man hindurch."""
        if u.loose or self.on_wall(u):
            return False
        step = dist(u.pos, pos)
        if step < 1e-9:
            return False
        for o in self.lochoi:
            if o is u or o.side is not u.side or not o.alive or o.loose or self.on_wall(o):
                continue
            if o.waiting and u.target is not None and dist(o.pos, u.target) >= dist(u.pos, u.target):
                continue                                  # ein Wartender hinter uns hält uns nicht auf (sonst warten alle aufeinander)
            if o.waiting and o.blocked_by == u.id and self._gives_way(o, u):
                continue                                  # sie wartet auf uns: wer nicht angreift (etwa zurückweicht), geht zuerst
            if dist(o.pos, pos) > o.radius + u.radius or self._passable(o) or self._nested(u, o):
                continue
            if not self._standing(o):
                continue                                  # unterwegs: man weicht sich Mann für Mann aus
            if self._gap_at(u, pos, o) > 0.0:
                continue
            if not self._idle(o):
                # hinter einer kämpfenden oder wartenden: anstehen, nicht tiefer hinein (seitlich vorbei geht)
                if dist(pos, o.pos) < dist(u.pos, o.pos) - 0.3 * step:
                    u.blocked_by = o.id
                    return True
                continue
            if self._passable(u):
                continue                                  # leichte Truppen dürfen dicht an eine ruhende eigene heran
            # an einer ruhenden Gruppe: hinein nicht, daran entlang und herum schon
            if self._gap(u, o) > 0.05:
                u.idle_block = True
                return True
            tx, ty = o.x - u.x, o.y - u.y
            n = math.hypot(tx, ty)
            if n > 1e-9 and (tx * (pos[0] - u.x) + ty * (pos[1] - u.y)) / (n * step) > 0.5:
                u.idle_block = True
                return True
        return False

    @staticmethod
    def _gives_way(o: Lochos, u: Lochos) -> bool:
        """Warten ``o`` und ``u`` aufeinander, gibt ``o`` den Weg frei: wenn ``u`` keinen
        Feind angreift (sich etwa zurückzieht) und ``o`` schon, sonst die mit der größeren
        Nummer. So löst sich jede gegenseitige Blockade in genau einer Richtung."""
        if (u.target_id is None) != (o.target_id is None):
            return u.target_id is None
        return u.id < o.id

    def _step(self, u: Lochos, delta: Point, through: bool = False) -> None:
        nx, ny = u.x + delta[0], u.y + delta[1]
        u.idle_block = False
        u.blocked_by = None
        if not through and self._walled_off(u, u.pos, (nx, ny), self._barriers(u)):
            return
        if not through and self._own_in_the_way(u, (nx, ny)):
            slide = self._slide_past(u, delta) if u.idle_block else None
            if slide is None:
                u.waiting = True                          # anstehen, bis vorn Platz wird
                u.vel = 0.0
                return
            nx, ny = u.x + slide[0], u.y + slide[1]       # an der Ecke einer ruhenden Gruppe vorbeigleiten
            u.idle_block = False
        u.waiting = False
        if self.can_step(u, u.pos, (nx, ny)):
            u.x, u.y = nx, ny
        elif self.can_step(u, u.pos, (nx, u.y)):
            u.x = nx
        elif self.can_step(u, u.pos, (u.x, ny)):
            u.y = ny

    def _slide_past(self, u: Lochos, delta: Point) -> Point | None:
        """Streift ein Block auf dem Weg zu seinem Ziel die Ecke einer ruhenden eigenen
        Gruppe, gleitet er schräg daran vorbei (bis 60 Grad zur Seite, die von ihr weg
        führt), solange er dem Ziel dabei näherkommt; sonst None (er wartet)."""
        if u.target is None or u.loose or u.engaged or u.target_id is not None or u.side is not Side.STADT:
            return None                                   # nur befohlene Märsche des Spielers, nicht im Angriff
        step = math.hypot(*delta)
        if step < 1e-9:
            return None
        near = [o for o in self.lochoi if o is not u and o.alive and o.side is u.side and not o.loose
                and self._idle(o) and dist(o.pos, u.pos) <= o.radius + u.radius + step]
        if not near:
            return None
        o = min(near, key=lambda o: self._gap(u, o))
        away = sub(u.pos, o.pos)
        here = dist(u.pos, u.target)
        for ang in (0.35, 0.7, 1.05):
            for sgn in (1.0, -1.0):
                a = ang * sgn
                c, s_ = math.cos(a), math.sin(a)
                d2 = (delta[0] * c - delta[1] * s_, delta[0] * s_ + delta[1] * c)
                if d2[0] * away[0] + d2[1] * away[1] <= delta[0] * away[0] + delta[1] * away[1]:
                    continue                              # nur zur Seite, die von ihr weg führt
                q = (u.x + d2[0], u.y + d2[1])
                if dist(q, u.target) > here - 0.3 * step:
                    continue                              # kommt dem Ziel nicht näher
                if self._walled_off(u, u.pos, q, self._barriers(u)) or self._own_in_the_way(u, q):
                    continue
                return d2
        return None

    def _separate(self) -> None:
        alive = [u for u in self.lochoi if u.alive]
        for i, a in enumerate(alive):
            for b in alive[i + 1:]:
                idle_a, idle_b = self._idle(a), self._idle(b)
                if a.side is b.side and not (idle_a and idle_b):
                    continue          # eigene Gruppen drückt niemand weg: wer unterwegs ist, kommt gar nicht erst hinein
                if a.side is b.side and (self._passable(a) or self._passable(b) or self._nested(a, b)):
                    continue          # durch leichte Truppen geht man hindurch (Ringe eines Verbands stehen ineinander)
                if a.side is b.side and (a.engaged or b.engaged):
                    continue          # im Handgemenge drückt man den eigenen Nebenmann nicht weg
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
                direction = norm(sub(b.pos, a.pos))
                move_a = not a.in_phalanx and a.building is None
                move_b = not b.in_phalanx and b.building is None
                if a.side is b.side:
                    # zwei ruhende eigene Gruppen, die sich überlappen: es weicht, wer zuletzt kam
                    if move_a and move_b and a.still_since > b.still_since:
                        move_b = False
                    elif move_a and move_b and b.still_since > a.still_since:
                        move_a = False
                push = overlap if move_a != move_b else overlap / 2
                if move_a:
                    self._step(a, scale(direction, -push))
                if move_b:
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
                if self._in_contact(a, b, held=b.id in previous.get(a.id, ())):
                    pairs.append((a, b))
                    a.engaged = True
                    a.contacts.append(b.id)
                    if b.id not in previous.get(a.id, ()) and a.runup >= config.CHARGE_RUNUP and not a.loose:
                        self._charge(a, b)                # erster Kontakt mit Anlauf: Aufprall
        for u in alive:
            u.contact_since = {bid: u.contact_since.get(bid, self.time) for bid in u.contacts}
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
            if (self.inside(nx, ny) and not self.is_blocked(nx, ny, b) and not self.is_wall_cell(self.cell(nx, ny), True)
                    and self._crowding(m, m.pos, (nx, ny), b.id) is None):
                m.x, m.y = nx, ny                         # weggestoßen, aber nicht in einen anderen hinein
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
                front = config.PHALANX_FRONT_O if b.formation == "o" else config.PHALANX_FRONT
                mod = 1.0 + (front - 1.0) * shield
            elif arc_name == "rear":
                mod = config.PHALANX_REAR
            support = max(config.PHALANX_SUPPORT_MIN, 1.0 - config.PHALANX_SUPPORT * self._line_neighbours(b))
            mod *= support
        if arc_name == "flank":
            mod *= self.shield_side(b, a.pos, config.SHIELD_MELEE_COVER, config.SHIELD_MELEE_OPEN)
        if b.stance is Stance.FLUCHT:
            mod *= config.ROUTED_DAMAGE
        if b.leader_man() is not None:
            mod *= config.LEADER_ARMOR                   # der Anführer hält die Reihen zusammen
        return mod, arc_name

    @staticmethod
    def shield_side(b: Lochos, p: Point, cover: float, open_: float) -> float:
        """Der Hoplitenschild sitzt am linken Arm: Wer Hopliten von ihrer linken Seite
        trifft, trifft den Schild (``cover``), von rechts die ungedeckte Seite (``open_``)."""
        if b.share(lambda m: m.kind.hoplite) < 0.5:
            return 1.0
        along, _ = b.local(p)
        return open_ if along > 0 else cover

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

    def _reach_to(self, foe: Lochos):
        """Abstand eines Mannes zum nächsten Mann des Gegners, von Mann zu Mann gemessen,
        nicht zum Formationsrechteck: Wer sich um ein Linienende legt oder vor seinem
        Rechteck steht, wird dort gefasst, wo er wirklich steht. Das Rechteck dient nur
        als schnelle Vorprüfung (kein Mann des Gegners steht weiter als ``spread``
        davon entfernt)."""
        men = foe.all_men()
        if not men:
            return lambda m: float("inf")
        spread = max(foe.rect_distance(n.pos) for n in men)
        limit = config.CONTACT_REACH + spread

        def distance(m: Man) -> float:
            d = foe.rect_distance(m.pos)
            if d > limit:
                return d
            return min(math.hypot(m.x - n.x, m.y - n.y) for n in men)
        return distance

    def _in_reach(self, men: list[Man], foe: Lochos, extra: float = 0.0) -> list[Man]:
        distance = self._reach_to(foe)
        return [m for m in men if distance(m) <= config.CONTACT_REACH + extra]

    def _melee_rate(self, a: Lochos, b: Lochos) -> tuple[float, str]:
        # Es kämpft nur, wer den Gegner erreicht: die Berührungsbreite entscheidet, nicht die ganze Front
        own_arc = self.arc_of(a, b.pos) if self._formed(a) else "front"
        attack = a.melee_attack_against(self._reach_to(b), config.CONTACT_REACH, own_arc)
        base = attack * config.BASE_RATE
        if a.loose and a.men:
            base *= len(self._present(a, b)) / a.men
        attack_mod = 1.0
        if self._formed(a):
            if own_arc == "front":
                attack_mod = config.PHALANX_ATTACK_FRONT if a.formation == "linie" else 1.0
            # an Flanke und Rücken wehren sich nur die Männer am Rand, die den Gegner erreichen (ohne Speerwand)
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
        if self.blocked and (a.loose or b.loose):
            # am Wall Mann für Mann: wer nur von oben hinab- oder an die Leiter hinaufreicht, trifft schwächer
            weights = self._man_weights(a, b, config.CONTACT_REACH)
            if weights:
                attack_mod *= sum(weights.values()) / len(weights)
        elif self._fights_from_wall(a) != self._fights_from_wall(b):
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
            if self.blocked:                              # am Wall: nur wen der Gegner auch erreicht
                near = self._reachable_men(a, b, near, config.ENGAGE_RANGE + 0.4)
            if not near:
                return
            fallen = b.take_damage_men(near, dmg, self.rng)
        elif self._formed(b) and row_arc in ("flank", "rear"):
            # Flanke und Rücken: es trifft die Männer am Rand, die der Angreifer erreicht, nicht die ganze Reihe
            near = self._in_reach(b.all_men(), a) or sorted(b.all_men(), key=lambda m: dist(m.pos, a.pos))[:2]
            fallen = b.take_damage_men(near, dmg, self.rng)
        else:
            # es trifft, wer den Angreifer erreicht; erreicht ihn niemand, die ganze Reihe
            row = b.exposed_row(row_arc)
            candidates = b.all_men() if b.formation == "o" else b.rows[row] if b.rows else []
            near = self._in_reach(candidates, a) if arc_name != "ranged" else []
            if near:
                fallen = b.take_damage_men(near, dmg, self.rng)
            else:
                fallen = b.take_damage(row, dmg, self.rng)
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
            targets = foe.all_men()
            for m in throwers:
                m.ammo -= 1
                victim = targets[self.rng.randrange(len(targets))]
                (tx, ty), flight = self._aim(m.pos, victim)
                self.projectiles.append(Projectile(m.x, m.y, tx, ty, foe.id, config.JAVELIN_DAMAGE, 0.0, flight, victim))
        for pr in list(self.projectiles):
            pr.progress += dt
            if pr.progress >= pr.total:
                self.projectiles.remove(pr)
                aimed = self.by_id(pr.target_id)
                if aimed is None:
                    continue
                hit = self._struck(aimed.side, (pr.tx, pr.ty))
                if hit is None:
                    continue                                   # daneben: dort steht niemand (mehr)
                man, b = hit
                dmg = pr.dmg * (self._missile_cover(b) if pr.cover else 1.0)
                dmg *= config.LEADER_ARMOR if b.leader_man() is not None else 1.0
                if not b.loose and b.arc_to((pr.x, pr.y)) == "flank":
                    dmg *= self.shield_side(b, (pr.x, pr.y), config.SHIELD_SPEAR_COVER, config.SHIELD_SPEAR_OPEN)
                if self._behind_palisade(man, (pr.x, pr.y)):
                    dmg *= config.WALL_COVER_FACTOR
                fallen = b.hit_man(man, dmg)
                self._after_hit(b, fallen, "ranged", dmg)

    @staticmethod
    def _missile_cover(b: Lochos) -> float:
        """Wie viel ein Wurfspeer bei ``b`` noch ausrichtet: Die Phalanx deckt sich mit
        den Schilden, in lockerer Ordnung trägt jeder seinen Schild für sich."""
        if b.in_phalanx:
            return 1.0 - 0.5 * b.shield_factor()
        if b.drill_kind() == "locker":
            return (1.0 - 0.5 * b.shield_factor()) * config.DRILL_LOOSE_MISSILE
        return 1.0

    def _aim(self, origin: Point, victim: Man) -> tuple[Point, float]:
        """Wohin der Speer fliegt und wie lange: dorthin, wo ``victim`` sein wird, wenn er
        ankommt (aus seiner Bewegung geschätzt), dazu eine Streuung, die mit der
        Entfernung wächst. Wer abrupt wendet oder stehen bleibt, entgeht manchem Wurf."""
        aim = victim.pos
        lead = 0.0
        if config.MISSILE_LEAD:
            for _ in range(2):
                flight = dist(origin, aim) / config.JAVELIN_SPEED
                aim = (victim.x + victim.vx * flight, victim.y + victim.vy * flight)
            lead = dist(aim, victim.pos)
        sigma = (config.MISSILE_SPREAD + config.MISSILE_SPREAD_DIST * dist(origin, aim)
                 + config.MISSILE_LEAD_ERROR * lead)
        land = (aim[0] + self.rng.gauss(0.0, sigma), aim[1] + self.rng.gauss(0.0, sigma))
        return land, max(0.1, dist(origin, land) / config.JAVELIN_SPEED)

    def _struck(self, side: Side, p: Point) -> tuple[Man, Lochos] | None:
        """Der Mann der Seite ``side``, der dem Einschlag bei ``p`` am nächsten steht (höchstens
        einen Trefferhalbmesser entfernt), mit seiner Gruppe."""
        best, best_d = None, config.MISSILE_HIT_RADIUS
        for g in self.lochoi:
            if g.side is not side or not g.alive:
                continue
            for m in g.all_men():
                d = math.hypot(m.x - p[0], m.y - p[1])
                if m.hp > 0 and d <= best_d:
                    best, best_d = (m, g), d
        return best

    def _track_motion(self, before: list[tuple[Man, float, float]], dt: float) -> None:
        """Die Geschwindigkeit jedes Mannes, geglättet über ``MISSILE_LEAD_TIME``: Danach
        zielen die Werfer vor. Ein Sprung (neu aufgestellt) zählt nicht als Lauf."""
        k = min(1.0, dt / config.MISSILE_LEAD_TIME)
        for m, x, y in before:
            vx, vy = (m.x - x) / dt, (m.y - y) / dt
            if vx * vx + vy * vy > 36.0:
                vx = vy = 0.0
            m.vx += (vx - m.vx) * k
            m.vy += (vy - m.vy) * k

    def _tower_fire(self, dt: float) -> None:
        """Wehrtürme: Wer oben steht, gehört dazu. Steht nur der Feind oben, gehört der Turm
        ihm; stehen beide oben, schweigt er. Sonst wirft er alle halbe Sekunde einen Speer
        auf den nächsten Feind in Reichweite, ohne Vorrat."""
        reach = config.TOWER_RANGE
        for t in self.corner_towers:
            cx, cy = t.center
            present = {Side.STADT: 0, Side.FEIND: 0}
            gx, gy = self._grid_cell(cx, cy)
            for x in range(gx - 2, gx + 3):
                for y in range(gy - 2, gy + 3):
                    for m, uid in self._man_grid.get((x, y), ()):
                        if m.hp > 0 and self.cell(m.x, m.y) == t.cell:
                            present[self._man_side[id(m)]] += 1
            if t.owner is None:
                sides = [sd for sd, n in present.items() if n]
                if len(sides) == 1:
                    t.owner = sides[0]
            else:
                foe_side = Side.FEIND if t.owner is Side.STADT else Side.STADT
                if present[foe_side] and not present[t.owner]:
                    t.owner = foe_side
                    who = "Der Feind nimmt" if foe_side is Side.FEIND else "Wir nehmen"
                    self.events.append(f"{who} einen Turm ein")
            if t.owner is None:
                continue
            foe_side = Side.FEIND if t.owner is Side.STADT else Side.STADT
            if present[foe_side]:
                t.timer = 0.0
                continue                                          # umkämpft: niemand wirft
            t.timer += dt
            if t.timer < config.TOWER_THROW_INTERVAL:
                continue
            best, best_d = None, reach
            for u in self.lochoi:
                if u.side is not foe_side or not u.fighting or dist(u.pos, (cx, cy)) > reach + u.radius:
                    continue
                for m in u.all_men():
                    d = math.hypot(m.x - cx, m.y - cy)
                    if d <= best_d:
                        best, best_d = (u, m), d
            if best is None:
                t.timer = config.TOWER_THROW_INTERVAL                 # bereit, sobald einer kommt
                continue
            t.timer -= config.TOWER_THROW_INTERVAL
            u, victim = best
            near = [m for m in u.all_men() if math.hypot(m.x - victim.x, m.y - victim.y) <= 0.8]
            victim = near[self.rng.randrange(len(near))]
            (tx, ty), flight = self._aim((cx, cy), victim)
            self.projectiles.append(Projectile(cx, cy, tx, ty, u.id, config.JAVELIN_DAMAGE, 0.0, flight, victim,
                                               cover=False))

    def _behind_palisade(self, man: Man, origin: Point) -> bool:
        """Steht der Mann auf dem Wehrgang und kam der Speer von außen? Dann deckt ihn
        die Palisade. Von innen (der Seite der Häuser) oder vom Wall selbst nicht."""
        if not self.blocked or not self.is_wall_cell(self.cell(man.x, man.y), True):
            return False
        inside = {self._wall_level((h.cx + 0.5, h.cy + 0.5)) for h in self.houses}
        thrown_from = self._wall_level(origin)
        return thrown_from in ("nord", "sued", "innen", "aussen") and thrown_from not in inside

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
            if self.ring and u.engine in ("ram", "tower"):
                self._engine_ring(u, dt)
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

    def _engine_ring(self, u: Lochos, dt: float) -> None:
        """Festung: Rammbock vor einem geschlossenen Tor, Turm an seinem Wallstück."""
        if u.engine == "ram":
            for g in self.gates:
                if not g.closed:
                    continue
                cx, cy = g.center
                (nx, ny), (tx, ty) = g.normal, g.tangent
                along = abs((u.x - cx) * tx + (u.y - cy) * ty)
                across = abs((u.x - cx) * nx + (u.y - cy) * ny)
                if along <= g.half_len + 0.3 and abs(across - g.half_thick) <= u.half_d + config.RAM_REACH:
                    g.hp -= config.RAM_DPS * dt
                    if g.hp <= 0:
                        g.hp = 0.0
                        g.closed = False
                        self.events.append("Ein Tor ist aufgebrochen!")
                        self._drop_rams(g)
                    return
            return
        if u.tower_cell is None:
            return
        d = self.tower_step(u.tower_cell)
        if d is None:
            return
        cx, cy = u.tower_cell[0] + 0.5, u.tower_cell[1] + 0.5
        along = abs((u.x - cx) * -d[1] + (u.y - cy) * d[0])
        across = (u.x - cx) * d[0] + (u.y - cy) * d[1]
        if along <= 0.6 and abs(across - 0.5) <= u.half_d + config.TOWER_REACH:
            u.tower_progress += dt
            if u.tower_progress >= config.TOWER_DEPLOY_TIME:
                cell = u.tower_cell
                self.crossings.add(cell)
                self._foot[cell] = d
                self.events.append(f"{u.name} hat den Wall überwunden")
                self.towers.append((cx + d[0] * 0.75, cy + d[1] * 0.75))   # Turm bleibt am Wall stehen
                u.engine = None
                u.tower_cell = None
                u.target = (cx, cy)                                         # hinauf auf den Wehrgang

    def _drop_rams(self, gate: Gate | None = None) -> None:
        """Nach dem Durchbruch bleibt der Rammbock liegen, die Gruppen treten
        zur Seite, damit der Durchgang frei ist, und sind wieder schnell."""
        if self.ring and gate is not None:
            cx, cy = gate.center
            tx, ty = gate.tangent
            for u in self.lochoi:
                if u.engine == "ram" and dist(u.pos, gate.center) <= gate.half_thick + u.half_d + 1.5:
                    fx, fy = u.facing
                    # hinter der Gruppe ablegen, nicht im Durchgang (dort wäre er ein Hindernis)
                    self.debris.append((u.x - fx * (u.half_d + 0.4), u.y - fy * (u.half_d + 0.4), fx, fy))
                    u.engine = None
                    u.ram_gate = None
                    if self.enemy_ram_id == u.id:
                        self.enemy_ram_id = None
                    side = 1.0 if (u.x - cx) * tx + (u.y - cy) * ty >= 0 else -1.0
                    u.stance = Stance.HALTEN
                    u.face_to = None
                    u.target = self._free_spot((u.x + tx * side * (u.half_w + 1.6), u.y + ty * side * (u.half_w + 1.6)), u)
            return
        gx = self.gate.center[0] if self.gate else self.cols / 2
        for u in self.lochoi:
            if u.engine == "ram":
                fx, fy = u.facing
                self.debris.append((u.x - fx * (u.half_d + 0.4), u.y - fy * (u.half_d + 0.4), fx, fy))   # nicht im Durchgang
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
    # ------------------------------------------------------------ Sammeln
    @property
    def agora(self) -> Point | None:
        return self.scenario.agora

    def defends(self, u: Lochos) -> bool:
        """Verteidigt ``u`` eine Siedlung mit Agora? Dann flieht die Gruppe nie vom
        Feld, sondern auf die Agora, und kämpft dort bis zum letzten Mann."""
        if self.agora is None:
            return False
        return u.side is (Side.FEIND if self.attacking else Side.STADT)

    def rally_point(self, u: Lochos) -> Point:
        """Wohin eine geschlagene Gruppe flieht, um sich zu sammeln: Verteidiger auf
        die Agora, Angreifer an den eigenen Kartenrand (die Stadt kommt von Süden,
        der Feind von Norden)."""
        if self.defends(u):
            return self.agora
        x = min(max(self._flee_x(u), 1.0), self.cols - 1.0)
        if u.side is Side.STADT:
            return (x, self.rows - config.RALLY_EDGE)
        return (x, config.RALLY_EDGE)

    def flee_target(self, u: Lochos) -> Point:
        """Ziel einer fliehenden Gruppe: der Sammelpunkt, oder vom Feld, wenn sie geht."""
        if u.leaving:
            x = self._flee_x(u)
            return (x, self.rows + 3.0) if u.side is Side.STADT else (x, -3.0)
        return self.rally_point(u)

    @staticmethod
    def _flee_x(u: Lochos) -> float:
        """Geradeaus zum eigenen Rand. Eine aufgelöste Gruppe behält die Richtung, die sie
        hatte, als sie sich auflöste: Ihre Mitte folgt den Männern, und ein Ziel, das
        der Mitte folgte, wanderte mit ihr davon."""
        if not u.loose or u.flee_x is None:
            u.flee_x = u.x
        return u.flee_x

    def _at_agora(self, u: Lochos) -> bool:
        return self.defends(u) and dist(u.pos, self.agora) <= config.RALLY_RADIUS

    def _rally(self, u: Lochos, dt: float, hopeless: bool) -> None:
        """Eine fliehende Gruppe am Sammelpunkt: Ist kein Feind nah, steigt ihre Moral,
        bis sie wieder Befehle annimmt. Verteidiger, die der Feind auf der Agora
        stellt, kehren um und kämpfen bis zum letzten Mann. Angreifer in
        aussichtsloser Lage sammeln sich nicht, sie verlassen das Feld."""
        if u.leaving:
            return
        if not self.defends(u) and hopeless:
            u.leaving = True
            u.target = self.flee_target(u)
            self.events.append(f"{u.name} ({u.side.value}) verlassen das Feld")
            return
        if dist(u.pos, self.rally_point(u)) > config.RALLY_RADIUS:
            return
        nearest = min((self._gap(u, f) for f in self.lochoi if f.side is not u.side and f.fighting
                       and self.on_wall(f) == self.on_wall(u)), default=float("inf"))
        if nearest <= config.LAST_STAND_RANGE:           # der Feind setzt nach
            if self.defends(u):                          # weiter geht es nicht: umkehren und kämpfen
                self._stand_again(u, max(u.morale, u.rout_threshold + 0.05))
                self.events.append(f"{u.name} ({u.side.value}) stellen sich auf der Agora zum letzten Kampf")
            else:                                        # bis an den eigenen Rand verfolgt: vom Feld
                u.leaving = True
                u.target = self.flee_target(u)
                self.events.append(f"{u.name} ({u.side.value}) verlassen das Feld")
            return
        if nearest <= config.RALLY_SAFE:
            return                                       # der Feind ist zu nah zum Sammeln: abwarten
        u.morale = max(u.morale, 0.0) + config.RALLY_REGEN * dt
        if u.morale >= config.RALLY_MORALE:
            self._stand_again(u, u.morale)
            where = "auf der Agora" if self.defends(u) else "am Rand des Feldes"
            self.events.append(f"{u.name} ({u.side.value}) sammeln sich {where}")

    def _stand_again(self, u: Lochos, morale: float) -> None:
        u.stance = Stance.HALTEN
        u.flee_x = None
        u.morale = morale
        u.target = None
        cs = u.corners()                                  # ragt die Aufstellung über den Kartenrand (Agora am Rand): hereinrücken
        dx = max(0.0, 0.05 - min(c[0] for c in cs)) - max(0.0, max(c[0] for c in cs) - (self.cols - 0.05))
        dy = max(0.0, 0.05 - min(c[1] for c in cs)) - max(0.0, max(c[1] for c in cs) - (self.rows - 0.05))
        if dx or dy:
            u.target = (u.x + dx, u.y + dy)
        u.target_id = None
        u.in_line = False
        u.mode = ""
        u.waypoints = []
        u.still_since = self.time

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
        for entry in list(self.leaders):
            man, side, name = entry
            if man.hp <= 0.0:
                self.leaders.remove(entry)
                who = "Unser Anführer" if side is Side.STADT else "Der Anführer des Feindes"
                self.events.append(f"{who} ist gefallen ({name})")
        hopeless = {side: self._hopeless(side) for side in Side}
        broke: list[Lochos] = []
        for u in self.lochoi:
            if not u.alive:
                continue
            if u.stance is Stance.FLUCHT:
                self._rally(u, dt, hopeless[u.side])
                continue
            if not u.engaged:
                u.morale = min(1.0, u.morale + config.MORALE_REGEN * dt)
            if hopeless[u.side]:
                u.morale -= config.MORALE_HOPELESS_DRAIN * u.bravery() * dt
            threshold = u.rout_threshold - (config.LEADER_COURAGE if u.leader_man() is not None else 0.0)
            if u.morale <= threshold and not self._at_agora(u):   # auf der Agora flieht niemand mehr; mit Anführer später
                u.stance = Stance.FLUCHT
                u.in_line = False
                u.target_id = None
                u.leaving = not self.defends(u) and hopeless[u.side]
                u.target = self.flee_target(u)
                self.events.append(f"{u.name} ({u.side.value}) flieht")
                self._lose_engine(u)
                broke.append(u)
        for u in broke:                                  # Ansteckung: wer Nachbarn fliehen sieht, wankt
            for o in self.lochoi:
                if o is not u and o.side is u.side and o.fighting and dist(o.pos, u.pos) <= config.MORALE_CONTAGION_RANGE:
                    o.morale -= config.MORALE_CONTAGION * o.bravery()

    def _check_withdraw(self) -> None:
        start = self.men_start.get(Side.FEIND, 0)
        if self.agora is not None and self.attacking:
            return                                       # die Siedlung zieht nicht ab, sie hält bis zum letzten Mann
        remaining = sum(u.men for u in self.units(Side.FEIND) if u.alive and not u.leaving)   # wer kämpft oder sich sammeln kann
        if start and remaining <= start * config.ENEMY_WITHDRAW_FRACTION:
            for u in self.units(Side.FEIND):
                if u.stance is not Stance.FLUCHT:
                    u.stance = Stance.FLUCHT
                    u.in_line = False
                u.leaving = True                         # der Feind gibt auf: niemand sammelt sich mehr
                u.target = self.flee_target(u)
            if any(u.alive for u in self.units(Side.FEIND)) and "Der Feind zieht ab" not in self.events[-3:]:
                self.events.append("Der Feind zieht ab")

    def _beaten(self, side: Side) -> bool:
        """Eine Seite ist geschlagen, wenn niemand mehr kämpft und keine fliehende
        Gruppe sich noch sammeln kann (wer geht, zählt erst, wenn er vom Feld ist)."""
        for u in self.units(side):
            if not u.alive:
                continue
            if u.fighting:
                return False
            if not u.leaving or self.inside(u.x, u.y):
                return False
        return True

    def _check_outcome(self) -> None:
        enemy_gone = self._beaten(Side.FEIND)
        city_gone = (
            self.men_start.get(Side.STADT, 0)
            and self._beaten(Side.STADT)
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
