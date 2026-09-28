"""Die Kampfsimulation. Kennt kein Pygame.

Grundsätze aus dem Apoikia-Konzept:
- Gerechnet wird je Lochos, nie je Mann.
- Der Spieler markiert einen Bereich, dort bildet sich die Phalanx.
- Die Phalanx ist stark von vorn, verwundbar in Flanke und Rücken.
- Freier Angriff löst die Formation: schneller, aber ohne Bonus.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from . import config
from .geometry import add, arc, dist, norm, scale, snap4, sub
from .scenarios import Scenario
from .units import UNIT_TYPES, Lochos, Side, Stance

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
class PhalanxOrder:
    """Die zuletzt gezeichnete Phalanx, für Anzeige und Tests."""

    rect: tuple[float, float, float, float]
    facing: Point
    slots: list[Point]


@dataclass
class Battle:
    scenario: Scenario
    rng: random.Random = field(default_factory=random.Random)
    cols: int = config.COLS
    rows: int = config.ROWS
    houses: list[House] = field(default_factory=list)
    blocked: set[tuple[int, int]] = field(default_factory=set)
    gate: tuple[int, int] | None = None
    lochoi: list[Lochos] = field(default_factory=list)
    time: float = 0.0
    alarm: bool = True            # wartet auf den ersten Befehl
    outcome: str | None = None    # None, "sieg", "niederlage"
    phalanx: PhalanxOrder | None = None
    events: list[str] = field(default_factory=list)
    men_start: dict[Side, int] = field(default_factory=dict)
    _next_id: int = 0

    def __post_init__(self) -> None:
        s = self.scenario
        self.houses = [House(cx, cy) for cx, cy in s.houses]
        self.blocked = set(s.palisade)
        self.gate = s.gate
        self.gate_center = self._gate_center()
        for spec in s.player:
            self._spawn(Side.STADT, spec.kind, spec.x, spec.y, [])
        for spec in s.enemies:
            self._spawn(Side.FEIND, spec.kind, spec.x, spec.y, list(spec.waypoints))
        self.men_start = {side: self.men(side) for side in Side}

    # ------------------------------------------------------------ Aufbau
    def _spawn(self, side: Side, kind: str, x: float, y: float, waypoints: list[Point]) -> Lochos:
        unit = Lochos(id=self._next_id, side=side, kind=UNIT_TYPES[kind], x=x, y=y)
        self._next_id += 1
        if side is Side.FEIND:
            unit.stance = Stance.RAUB
            unit.facing = (0.0, 1.0)
            unit.waypoints = list(waypoints)
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
        return [
            u for u in self.lochoi
            if u.side is side and (u.fighting if fighting_only else u.alive)
        ]

    def men(self, side: Side, fighting_only: bool = False) -> int:
        return sum(u.men for u in self.units(side, fighting_only))

    def houses_intact(self) -> int:
        return sum(1 for h in self.houses if not h.looted)

    def is_blocked(self, x: float, y: float) -> bool:
        return (int(math.floor(x)), int(math.floor(y))) in self.blocked

    def inside(self, x: float, y: float) -> bool:
        return 0.0 <= x < self.cols and 0.0 <= y < self.rows

    def path_clear(self, a: Point, b: Point) -> bool:
        """Liegt eine gesperrte Kachel auf der geraden Strecke?"""
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
        approach = (gx, gy - 1.2) if above else (gx, gy + 1.2)
        return approach, False

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

    # ----------------------------------------------------------- Befehle
    def command_phalanx(self, x0: float, y0: float, x1: float, y1: float) -> PhalanxOrder | None:
        """Bereich markieren; alle einsatzfähigen Lochoi bilden dort die Phalanx."""
        self.alarm = False
        x0, x1 = sorted((max(0.0, x0), min(float(self.cols), x1)))
        y0, y1 = sorted((max(0.0, y0), min(float(self.rows), y1)))
        w, h = max(x1 - x0, 1.0), max(y1 - y0, 1.0)
        center = ((x0 + x1) / 2, (y0 + y1) / 2)

        foe = self.enemy_centroid(Side.STADT) or (center[0], -1.0)
        if w >= h:
            axis = (1.0, 0.0)
            facing = (0.0, -1.0 if foe[1] < center[1] else 1.0)
        else:
            axis = (0.0, 1.0)
            facing = (-1.0 if foe[0] < center[0] else 1.0, 0.0)
        facing = snap4(facing)

        line = [u for u in self.units(Side.STADT, fighting_only=True) if u.kind.can_phalanx]
        others = [u for u in self.units(Side.STADT, fighting_only=True) if not u.kind.can_phalanx]
        per_rank = max(1, int(round(max(w, h))))
        ranks = max(1, math.ceil(len(line) / per_rank)) if line else 1

        slots: list[Point] = []
        for r in range(ranks):
            n = min(per_rank, len(line) - r * per_rank) if line else per_rank
            for i in range(n):
                off = i - (n - 1) / 2
                p = add(add(center, scale(axis, off)), scale(facing, -r * 1.0))
                slots.append(p)
        slots = [self._free_spot(p) for p in slots]

        # Reihenfolge entlang der Linie beibehalten: wer links steht, geht nach links
        along = (lambda p: p[0]) if axis == (1.0, 0.0) else (lambda p: p[1])
        forward = lambda p: round(p[0] * facing[0] + p[1] * facing[1], 3)  # noqa: E731
        ordered_units = sorted(line, key=lambda u: along(u.pos))
        ordered_slots = sorted(slots, key=lambda p: (-forward(p), along(p)))  # vordere Reihe zuerst
        for u, slot in zip(ordered_units, ordered_slots):
            u.stance = Stance.PHALANX
            u.in_line = False
            u.facing = facing
            u.target = slot
            u.waypoints = []

        # Plänkler und Reiter stehen hinter der Linie
        for i, u in enumerate(others):
            off = (i - (len(others) - 1) / 2) * 1.2
            p = add(add(center, scale(axis, off)), scale(facing, -(ranks + 0.6)))
            u.stance = Stance.HALTEN
            u.in_line = False
            u.facing = facing
            u.target = self._free_spot(p)

        self.phalanx = PhalanxOrder(rect=(x0, y0, x1, y1), facing=facing, slots=slots)
        self.events.append(f"Phalanx: {len(slots)} Lochoi, Front {self._dir_name(facing)}")
        return self.phalanx

    def command_attack(self) -> None:
        """Freier Angriff: Formation auflösen, Gegner verfolgen."""
        self.alarm = False
        for u in self.units(Side.STADT, fighting_only=True):
            u.stance = Stance.ANGRIFF
            u.in_line = False
            u.target = None
        self.events.append("Freier Angriff")

    def command_hold(self) -> None:
        """Stehen bleiben, rundum kämpfen, ohne Formationsbonus."""
        self.alarm = False
        for u in self.units(Side.STADT, fighting_only=True):
            u.stance = Stance.HALTEN
            u.in_line = False
            u.target = None
        self.events.append("Halten")

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
            if foe is not None and d <= config.SEEK_RANGE:
                u.stance = Stance.ANGRIFF
                u.target = foe.pos
                continue
            u.stance = Stance.RAUB
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
        foes = self.units(Side.FEIND)  # auch Fliehende werden verfolgt
        for u in self.units(Side.STADT, fighting_only=True):
            if u.stance is Stance.ANGRIFF:
                foe, _ = self._nearest(u, [f for f in foes if f.fighting] or foes)
                u.target = foe.pos if foe else None
        for u in self.units(Side.STADT):
            if u.stance is Stance.FLUCHT:
                u.target = (u.x, self.rows + 3.0)

    # -- Bewegung ----------------------------------------------------------
    def _move(self, dt: float) -> None:
        for u in self.lochoi:
            if not u.alive or u.target is None:
                continue
            if u.in_phalanx:
                continue
            if u.stance in (Stance.HALTEN,) and u.target is None:
                continue
            speed = u.kind.speed * (1.25 if u.stance is Stance.FLUCHT else 1.0)
            goal, final = self.route(u, u.target)
            to = sub(goal, u.pos)
            d = dist(u.pos, goal)
            stop_at = config.ENGAGE_RANGE * 0.8 if (u.stance is Stance.ANGRIFF and final) else 0.0
            if d <= max(config.ARRIVE_EPS, stop_at):
                if u.stance is Stance.PHALANX and final and d <= config.ARRIVE_EPS + 0.02:
                    u.x, u.y = u.target
                    u.in_line = True
                elif u.stance is Stance.HALTEN and final:
                    u.target = None
                continue
            step = min(speed * dt, d)
            direction = norm(to)
            u.facing = direction if u.stance is not Stance.PHALANX else u.facing
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
                    continue  # die Linie ordnet sich über ihre Plätze
                d = dist(a.pos, b.pos)
                if d >= config.SEPARATION or d < 1e-6:
                    continue
                push = (config.SEPARATION - d) / 2
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
        hits: list[tuple[Lochos, Lochos, float, str]] = []
        for a in alive:
            if not a.fighting:
                continue
            foes = [b for b in alive if b.side is not a.side]
            engaged_any = False
            for b in foes:
                d = dist(a.pos, b.pos)
                if d <= config.ENGAGE_RANGE:
                    engaged_any = True
                    rate, arc_name = self._melee_rate(a, b)
                    hits.append((a, b, rate * dt, arc_name))
            a.engaged = engaged_any
            if not engaged_any and a.kind.ranged_range > 0:
                foe, d = self._nearest(a, [f for f in foes if f.fighting])
                if foe is not None and d <= a.kind.ranged_range:
                    hits.append((a, foe, self._ranged_rate(a, foe) * dt, "ranged"))
        for a, b, dmg, arc_name in hits:
            self._apply_damage(a, b, dmg, arc_name)

    def _melee_rate(self, a: Lochos, b: Lochos) -> tuple[float, str]:
        base = a.men * a.kind.attack * config.BASE_RATE
        to_b = sub(b.pos, a.pos)
        # Angreifer in Phalanx: nur nach vorn richtig stark
        attack_mod = 1.0
        if a.in_phalanx:
            attack_mod = (
                config.PHALANX_ATTACK_FRONT
                if arc(a.facing, to_b, config.FRONT_ARC, config.REAR_ARC) == "front"
                else config.PHALANX_ATTACK_SIDE
            )
        # Verteidiger in Phalanx: Richtung entscheidet
        arc_name = "open"
        defense_mod = 1.0
        if b.in_phalanx:
            arc_name = arc(b.facing, sub(a.pos, b.pos), config.FRONT_ARC, config.REAR_ARC)
            defense_mod = {
                "front": config.PHALANX_FRONT,
                "flank": config.PHALANX_FLANK,
                "rear": config.PHALANX_REAR,
            }[arc_name]
            support = max(
                config.PHALANX_SUPPORT_MIN,
                1.0 - config.PHALANX_SUPPORT * self._line_neighbours(b),
            )
            defense_mod *= support
            if a.kind.cavalry and arc_name == "front":
                attack_mod *= config.CAVALRY_VS_FRONT
        if b.stance is Stance.FLUCHT:
            defense_mod *= config.ROUTED_DAMAGE
        return base * attack_mod * defense_mod / b.kind.defense, arc_name

    def _ranged_rate(self, a: Lochos, b: Lochos) -> float:
        base = a.men * a.kind.ranged_attack * config.BASE_RATE
        shield = 0.5 if b.in_phalanx else 1.0
        return base * shield / b.kind.defense

    def _line_neighbours(self, u: Lochos) -> int:
        return sum(
            1 for o in self.lochoi
            if o is not u and o.side is u.side and o.in_phalanx and dist(u.pos, o.pos) <= 1.25
        )

    def _apply_damage(self, a: Lochos, b: Lochos, dmg: float, arc_name: str) -> None:
        if not b.alive:
            return
        b.casualties += dmg
        b.last_arc = arc_name
        morale_mod = {"rear": 1.5, "flank": 1.2}.get(arc_name, 1.0)
        if b.in_phalanx and arc_name == "front":
            morale_mod = config.MORALE_LOSS_FRONT_PHALANX
        while b.casualties >= 1.0 and b.men > 0:
            b.casualties -= 1.0
            b.men -= 1
            b.morale -= (1.0 / b.men_start) * b.kind.bravery * morale_mod
        if b.in_phalanx and arc_name == "rear":
            b.morale -= config.MORALE_REAR_DRAIN * b.kind.bravery * dmg
        if b.men <= 0:
            b.men = 0
            b.in_line = False
            self.events.append(f"{b.kind.name} ({b.side.value}) aufgerieben")

    # -- Plündern ----------------------------------------------------------
    def _loot(self, dt: float) -> None:
        for u in self.units(Side.FEIND, fighting_only=True):
            if u.engaged:
                continue
            for h in self.houses:
                if h.looted or dist(u.pos, h.center) > config.LOOT_RANGE:
                    continue
                h.progress += dt
                if h.progress >= config.LOOT_TIME:
                    h.looted = True
                    self.events.append(f"Haus ({h.cx},{h.cy}) geplündert")
                break

    # -- Moral -------------------------------------------------------------
    def _morale(self, dt: float) -> None:
        for u in self.lochoi:
            if not u.alive:
                continue
            if u.stance is Stance.FLUCHT:
                continue
            if not u.engaged:
                u.morale = min(1.0, u.morale + config.MORALE_REGEN * dt)
            if u.morale <= u.kind.rout_threshold:
                u.stance = Stance.FLUCHT
                u.in_line = False
                u.target = None
                self.events.append(f"{u.kind.name} ({u.side.value}) flieht")

    def _check_withdraw(self) -> None:
        start = self.men_start.get(Side.FEIND, 0)
        if start and self.men(Side.FEIND, fighting_only=True) <= start * config.ENEMY_WITHDRAW_FRACTION:
            for u in self.units(Side.FEIND, fighting_only=True):
                u.stance = Stance.FLUCHT
                u.in_line = False
            if any(u.alive for u in self.units(Side.FEIND)):
                if "Räuber ziehen ab" not in self.events[-3:]:
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
        """Gefallene, unabhängig davon, ob die Einheit noch auf dem Feld ist."""
        return self.men_start.get(side, 0) - sum(u.men for u in self.lochoi if u.side is side)

    def report(self) -> dict:
        return {
            "zeit": round(self.time, 1),
            "ausgang": self.outcome,
            "stadt_start": self.men_start.get(Side.STADT, 0),
            "stadt_gefallen": self.fallen(Side.STADT),
            "stadt_geflohen": sum(
                u.men for u in self.lochoi if u.side is Side.STADT and u.stance is Stance.FLUCHT
            ),
            "feind_start": self.men_start.get(Side.FEIND, 0),
            "feind_gefallen": self.fallen(Side.FEIND),
            "haeuser_intakt": self.houses_intact(),
            "haeuser": len(self.houses),
        }
