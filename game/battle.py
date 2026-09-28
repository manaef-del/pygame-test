"""Die Kampfsimulation. Kennt kein Pygame.

Grundsätze aus dem Apoikia-Konzept:
- Gerechnet wird je Gruppe (Lochos), nie je Mann. Männer sind Reihen.
- Die Phalanx ist stark von vorn, verwundbar in Flanke und Rücken.
- Freier Angriff löst die Formation: schneller, aber ohne Bonus.
- Der Spieler kann jede Gruppe einzeln schicken, angreifen lassen oder
  in einem markierten Bereich zur Phalanx formieren.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from . import config
from .army import Army, default_army
from .geometry import add, arc, dist, norm, scale, snap4, sub
from .scenarios import Scenario
from .units import UNIT_TYPES, Lochos, Man, Side, Stance, arrange, default_width

Point = tuple[float, float]


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
class Projectile:
    """Ein fliegender Speer, nur Anzeige und verzögerter Einschlag."""

    x: float
    y: float
    tx: float
    ty: float
    target_id: int
    dmg: float
    progress: float = 0.0
    total: float = 1.0   # Sekunden Flugzeit

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
    cols: int = config.COLS
    rows: int = config.ROWS
    houses: list[House] = field(default_factory=list)
    blocked: set[tuple[int, int]] = field(default_factory=set)
    gate: tuple[int, int] | None = None
    gate_center: Point | None = None
    lochoi: list[Lochos] = field(default_factory=list)
    time: float = 0.0
    alarm: bool = True
    outcome: str | None = None
    line: list[LinePlan] = field(default_factory=list)
    projectiles: list[Projectile] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    men_start: dict[Side, int] = field(default_factory=dict)
    _next_id: int = 0

    def __post_init__(self) -> None:
        s = self.scenario
        self.houses = [House(cx, cy) for cx, cy in s.houses]
        self.blocked = set(s.palisade)
        self.gate = s.gate
        self.gate_center = self._gate_center()
        self._deploy_army()
        for spec in s.enemies:
            per_row = math.ceil(spec.men / spec.rows)
            rows = [
                [Man(UNIT_TYPES["raeuber"]) for _ in range(min(per_row, spec.men - r * per_row))]
                for r in range(spec.rows)
            ]
            self._spawn(Side.FEIND, rows, spec.x, spec.y, list(spec.waypoints), "Räuber")
        self.men_start = {side: self.men(side) for side in Side}

    # ------------------------------------------------------------ Aufbau
    def _deploy_army(self) -> None:
        """Gruppen der Aufstellung nebeneinander im Aufmarschraum."""
        specs = [g for g in self.army.groups if g.men() > 0]
        if not specs:
            return
        y = self.scenario.deploy_y
        rows_units = [arrange(spec.build_men(), default_width(spec.men())) for spec in specs]
        widths = [max(0.9, 2 * Lochos(0, Side.STADT, r, 0, 0).radius + 0.2) for r in rows_units]
        total = sum(widths)
        x = self.cols / 2 - total / 2
        for spec, rows, w in zip(specs, rows_units, widths):
            self._spawn(Side.STADT, rows, min(max(x + w / 2, 0.6), self.cols - 0.6), y, [], spec.name)
            x += w

    def _spawn(self, side: Side, rows: list[list[Man]], x: float, y: float,
               waypoints: list[Point], name: str) -> Lochos:
        unit = Lochos(id=self._next_id, side=side, rows=rows, x=x, y=y, name=name)
        self._next_id += 1
        if side is Side.FEIND:
            unit.stance = Stance.RAUB
            unit.facing = (0.0, 1.0)
            unit.waypoints = list(waypoints)
            unit.rout_threshold = 0.4
        self.lochoi.append(unit)
        return unit

    def _gate_center(self) -> Point | None:
        if self.gate is None:
            return None
        gx, gy = self.gate
        cells = [gx]
        for step in (-1, 1):
            c = gx + step
            while 0 <= c < self.cols and (c, gy) not in self.blocked:
                cells.append(c)
                c += step
        return (sum(cells) / len(cells) + 0.5, gy + 0.5)

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
        """Gruppe unter einem Punkt (für Auswahl und Angriffsziel)."""
        best, best_d = None, float("inf")
        for u in self.lochoi:
            if not u.alive or (side is not None and u.side is not side):
                continue
            d = u.rect_distance(p)
            if d <= tolerance and d < best_d:
                best, best_d = u, d
        return best

    def houses_intact(self) -> int:
        return sum(1 for h in self.houses if not h.looted)

    def is_blocked(self, x: float, y: float) -> bool:
        return (int(math.floor(x)), int(math.floor(y))) in self.blocked

    def inside(self, x: float, y: float) -> bool:
        return 0.0 <= x < self.cols and 0.0 <= y < self.rows

    def path_clear(self, a: Point, b: Point) -> bool:
        d = dist(a, b)
        n = max(1, int(d / 0.25))
        for i in range(1, n + 1):
            t = i / n
            if self.is_blocked(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t):
                return False
        return True

    def route(self, u: Lochos, target: Point) -> tuple[Point, bool]:
        """Nächster Zielpunkt und ob es schon das eigentliche Ziel ist."""
        if self.gate_center is None or self.path_clear(u.pos, target):
            return target, True
        gx, gy = self.gate_center
        above = u.y < gy
        beyond = (gx, gy + 1.2) if above else (gx, gy - 1.2)
        if self.path_clear(u.pos, beyond):
            return beyond, False
        return ((gx, gy - 1.2) if above else (gx, gy + 1.2)), False

    def _nearest(self, unit: Lochos, candidates: list[Lochos]) -> tuple[Lochos | None, float]:
        best, best_d = None, float("inf")
        for c in candidates:
            d = dist(unit.pos, c.pos)
            if d < best_d:
                best, best_d = c, d
        return best, best_d

    def enemy_centroid(self, side: Side) -> Point | None:
        foes = self.units(Side.FEIND if side is Side.STADT else Side.STADT, fighting_only=True)
        if not foes:
            return None
        return (sum(u.x for u in foes) / len(foes), sum(u.y for u in foes) / len(foes))

    def _gap(self, a: Lochos, b: Lochos) -> float:
        """Abstand zwischen den Rändern zweier Formationen (0 = berühren sich)."""
        return max(0.0, min(a.rect_distance(b.pos) - b.core, b.rect_distance(a.pos) - a.core))

    def _in_contact(self, a: Lochos, b: Lochos) -> bool:
        return self._gap(a, b) <= config.ENGAGE_RANGE

    # ----------------------------------------------------------- Befehle
    def _selection(self, units: list[Lochos] | None) -> list[Lochos]:
        pool = self.units(Side.STADT, fighting_only=True)
        if not units:
            return pool
        ids = {u.id for u in units}
        return [u for u in pool if u.id in ids]

    def command_move(self, units: list[Lochos] | None, point: Point) -> None:
        """Gruppen zu einem Punkt schicken; dort halten sie."""
        self.alarm = False
        sel = self._selection(units)
        px = min(max(point[0], 0.5), self.cols - 0.5)
        py = min(max(point[1], 0.5), self.rows - 0.5)
        n = len(sel)
        for i, u in enumerate(sel):
            off = (i - (n - 1) / 2) * 1.2
            u.stance = Stance.HALTEN
            u.in_line = False
            u.target_id = None
            u.target = self._free_spot((px + off, py))
        self.events.append(f"{len(sel)} Gruppe(n) unterwegs")

    def command_attack_target(self, units: list[Lochos] | None, enemy: Lochos) -> None:
        """Gruppen greifen eine bestimmte gegnerische Gruppe an."""
        self.alarm = False
        for u in self._selection(units):
            u.stance = Stance.ANGRIFF
            u.in_line = False
            u.target_id = enemy.id
            u.target = enemy.pos
        self.events.append(f"Angriff auf {enemy.name} ({enemy.men} Mann)")

    def command_attack(self, units: list[Lochos] | None = None) -> None:
        """Freier Angriff: nächsten Gegner verfolgen."""
        self.alarm = False
        for u in self._selection(units):
            u.stance = Stance.ANGRIFF
            u.in_line = False
            u.target_id = None
            u.target = None
        self.events.append("Freier Angriff")

    def command_hold(self, units: list[Lochos] | None = None) -> None:
        self.alarm = False
        for u in self._selection(units):
            u.stance = Stance.HALTEN
            u.in_line = False
            u.target_id = None
            u.target = None
        self.events.append("Halten")

    def plan_line(self, units: list[Lochos] | None, start: Point, end: Point) -> list[LinePlan]:
        """Aufstellung entlang einer gezogenen Linie, ohne sie auszuführen.

        Die Linie ist die Front. Ihre Länge bestimmt die Breite und damit
        die Reihenzahl, die Zugrichtung die Blickrichtung: von links nach
        rechts gezogen schaut die Gruppe nach oben, wie man hinter ihr steht.
        """
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
            plans.append(LinePlan(u.id, self._free_spot(center), facing, width, depth, seg))
            pos += seg + gap
        return plans

    def command_line(self, units: list[Lochos] | None, start: Point, end: Point) -> list[LinePlan]:
        """Gruppen entlang der Linie aufziehen und dort die Formation halten."""
        self.alarm = False
        plans = self.plan_line(units, start, end)
        for plan in plans:
            u = self.by_id(plan.unit_id)
            if u is None:
                continue
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

    def _free_spot(self, p: Point) -> Point:
        x = min(max(p[0], 0.5), self.cols - 0.5)
        y = min(max(p[1], 0.5), self.rows - 0.5)
        if self.is_blocked(x, y):
            for dy in (1.0, -1.0, 2.0, -2.0):
                if not self.is_blocked(x, y + dy) and self.inside(x, y + dy):
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
        self._ai_enemies()
        self._ai_city()
        self._move(dt)
        self._separate()
        self._combat(dt)
        self._volleys(dt)
        self._loot(dt)
        self._morale(dt)
        self._check_withdraw()
        self._check_outcome()

    # -- KI ----------------------------------------------------------------
    def _ai_enemies(self) -> None:
        defenders = self.units(Side.STADT, fighting_only=True)
        for u in self.units(Side.FEIND):
            if u.stance is Stance.FLUCHT:
                u.target = (u.x, -3.0)
                continue
            foe, d = self._nearest(u, defenders)
            if foe is not None and foe.rect_distance(u.pos) <= config.SEEK_RANGE:
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
            if not u.alive or u.target is None or u.in_phalanx:
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
        if not self.is_blocked(nx, ny):
            u.x, u.y = nx, ny
        elif not self.is_blocked(nx, u.y):
            u.x = nx
        elif not self.is_blocked(u.x, ny):
            u.y = ny

    def _separate(self) -> None:
        alive = [u for u in self.lochoi if u.alive]
        for i, a in enumerate(alive):
            for b in alive[i + 1:]:
                if a.side is b.side and (a.stance is Stance.PHALANX or b.stance is Stance.PHALANX):
                    continue
                d = dist(a.pos, b.pos)
                if d < 1e-6:
                    continue
                overlap = (a.core + b.core + config.SEPARATION) - self._gap(a, b) - (a.core + b.core)
                if overlap <= 0:
                    continue
                push = overlap / 2
                direction = norm(sub(b.pos, a.pos))
                if not a.in_phalanx:
                    self._step(a, scale(direction, -push))
                if not b.in_phalanx:
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
        hits: list[tuple[Lochos, Lochos, float, str]] = []
        for a, b in pairs:
            rate, arc_name = self._melee_rate(a, b)
            hits.append((a, b, rate * dt, arc_name))
        for a, b, dmg, arc_name in hits:
            self._apply_damage(a, b, dmg, arc_name)

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
            to_b = sub(b.pos, a.pos)
            front = arc(a.facing, to_b, config.FRONT_ARC, config.REAR_ARC) == "front"
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
        return base * attack_mod * defense_mod, arc_name

    def _volleys(self, dt: float) -> None:
        """Peltasten werfen in Salven; Speere fliegen sichtbar und treffen später."""
        alive = [u for u in self.lochoi if u.alive]
        for a in alive:
            if not a.fighting:
                continue
            a.volley_timer = max(0.0, a.volley_timer - dt)
            throwers = a.throwers(a.engaged)
            if not throwers:
                if (a.ammo() == 0 and a.share(lambda m: m.kind.ranged) >= 0.5
                        and a.stance in (Stance.HALTEN, Stance.PHALANX)):
                    a.stance = Stance.ANGRIFF
                    a.in_line = False
                    a.target_id = None
                    self.events.append(f"{a.name}: Speere verschossen, Nahkampf")
                continue
            if a.volley_timer > 0:
                continue
            foes = [b for b in alive if b.side is not a.side and b.fighting]
            foe, d = self._nearest(a, foes)
            if foe is None or foe.rect_distance(a.pos) > config.JAVELIN_RANGE:
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

    def _line_neighbours(self, u: Lochos) -> int:
        return sum(
            1 for o in self.lochoi
            if o is not u and o.side is u.side and o.in_phalanx
            and self._gap(u, o) <= 0.5
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

    def _check_withdraw(self) -> None:
        start = self.men_start.get(Side.FEIND, 0)
        if start and self.men(Side.FEIND, fighting_only=True) <= start * config.ENEMY_WITHDRAW_FRACTION:
            for u in self.units(Side.FEIND, fighting_only=True):
                u.stance = Stance.FLUCHT
                u.in_line = False
            if any(u.alive for u in self.units(Side.FEIND)) and "Räuber ziehen ab" not in self.events[-3:]:
                self.events.append("Räuber ziehen ab")

    def _check_outcome(self) -> None:
        if self.houses_intact() == 0:
            self.outcome = "niederlage"
            self.events.append("Die Siedlung ist geplündert")
            return
        if not self.units(Side.FEIND, fighting_only=True) and not any(
            u.alive and u.stance is Stance.FLUCHT and self.inside(u.x, u.y)
            for u in self.units(Side.FEIND)
        ):
            self.outcome = "sieg"
            self.events.append("Der Überfall ist abgewehrt")
            return
        if (
            self.men_start.get(Side.STADT, 0)
            and not self.units(Side.STADT, fighting_only=True)
            and self.units(Side.FEIND, fighting_only=True)
        ):
            self.outcome = "niederlage"
            self.events.append("Die Verteidiger sind geschlagen")

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
