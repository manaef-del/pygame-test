"""Gegner-KI: Lage lesen, einen Plan wählen, aus Verlusten lernen. Kennt kein Pygame.

Drei Stufen:

1. Lagebericht (``Report``): alle halbe Sekunde wird gelesen, wo die Phalanx
   des Spielers steht und wohin sie schaut, welche Gruppen ungedeckt sind
   (Peltasten ohne Hopliten davor, abgesessene Reiter, aufgelöste Formation),
   ob das Tor offen ist und wo ein Turm steht.
2. Pläne (``Brain._choose_plan``): Die Gegnerseite wählt aus wenigen benannten
   Plänen nach Punktzahl: frontal, umgehen (West/Ost), zermürben mit Speeren,
   Tor rammen, Turm an den Wall, belagern; die Siedlung: halten oder
   vorrücken. Alle paar Sekunden wird neu bewertet. Jede Gruppe setzt den
   Plan für sich um: schwache Ziele zuerst, Phalanxfronten werden umlaufen.
3. Gedächtnis (``Memory``): Was in früheren Schlachten Verluste gekostet hat,
   wird beim nächsten Mal schwächer gewichtet. Innerhalb der Schlacht weicht
   eine Gruppe zurück, deren Angriff scheitert, statt bis zur Flucht zu
   kämpfen.

Die einfache alte Steuerung bleibt als ``LegacyBrain`` erhalten, um beide
im Simulator vergleichen zu können.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from . import config
from .geometry import arc, dist, norm, scale, sub
from .units import Lochos, Side, Stance

if TYPE_CHECKING:
    from .battle import Battle

Point = tuple[float, float]

PLAN_NAMES = {
    "frontal": "Frontal",
    "umgehen_west": "Umgehen im Westen",
    "umgehen_ost": "Umgehen im Osten",
    "zermuerben": "Zermürben mit Speeren",
    "flankieren": "Binden und Umfassen",
    "ruecken": "Umgehen und in den Rücken fallen",
    "tor": "Tor rammen",
    "turm": "Rammbock und Turm",
    "belagern": "Belagern",
    "halten": "Stellung halten",
    "vorruecken": "Vorrücken",
    "lagern": "Lagern",
}


# --------------------------------------------------------------- Gedächtnis
@dataclass
class Memory:
    """Erfolg je Szenario und Plan über Schlachten hinweg (Stufe 3).

    ``gains`` speichert je Plan, wie sich Verluste des Gegners und eigene
    Verluste (jeweils als Anteil der Startstärke) während des Plans
    verhalten haben: positiv = der Plan hat sich gelohnt."""

    gains: dict[str, dict[str, list[float]]] = field(default_factory=dict)
    path: str | None = None

    def weight(self, key: str, plan: str) -> float:
        g = self.gains.get(key, {}).get(plan)
        if not g:
            return 1.0
        recent = g[-config.AI_MEMORY_DEPTH:]
        mean = sum(recent) / len(recent)
        return min(config.AI_MEMORY_MAX, max(config.AI_MEMORY_MIN, 1.0 + config.AI_MEMORY_WEIGHT * mean))

    def record(self, key: str, plan: str, gain: float) -> None:
        self.gains.setdefault(key, {}).setdefault(plan, []).append(round(gain, 3))
        self.save()

    def save(self) -> None:
        if not self.path:
            return
        try:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(self.gains, fh)
        except OSError:
            pass

    @classmethod
    def load(cls, path: str | None) -> "Memory":
        if not path:
            return cls()
        path = os.path.expanduser(path)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return cls(gains=data, path=path)
        except (OSError, ValueError):
            pass
        return cls(path=path)


# --------------------------------------------------------------- Lagebericht
@dataclass
class Report:
    time: float
    foes: list[Lochos]                 # kämpfende Spielergruppen
    phalanxes: list[Lochos]            # davon in Formation
    exposed: set[int]                  # ungedeckte Spielergruppen (ids)
    own_strength: float
    foe_strength: float
    front_blocked: bool                # eine Phalanx schaut uns an und steht im Weg
    line_y: float | None               # Höhe der sperrenden Front
    room_west: float                   # Platz neben der Front bis zum Rand
    room_east: float
    foes_west: int
    foes_east: int
    gate_guarded: bool                 # Phalanx dicht hinter dem Tor
    own_ammo: int
    foe_wall_ammo: int                 # Speere der Spieler-Peltasten auf dem Wehrgang
    threat_x: float | None             # Wallszenario: wo der Angriff ansetzt

    @property
    def ratio(self) -> float:
        return self.own_strength / self.foe_strength if self.foe_strength > 0 else 9.0


@dataclass
class GroupState:
    attack_men: int | None = None      # Stärke zu Beginn des laufenden Angriffs
    attack_hp: float = 0.0             # Gesundheit aller Männer zu Beginn des Angriffs
    retreat_until: float = -1.0
    hard: int | None = None            # Ziel, an dem der letzte Angriff scheiterte


def strength(units: list[Lochos]) -> float:
    return sum(m.attack for u in units for m in u.all_men())


def formed(u: Lochos) -> bool:
    return u.in_phalanx


def local_to_world(u: Lochos, along: float, forward: float) -> Point:
    fx, fy = u.facing
    return (u.x - fy * along + fx * forward, u.y + fx * along + fy * forward)


# --------------------------------------------------------------------- KI
class Brain:
    """Die Gegnerseite: liest die Lage, wählt Pläne, gibt Gruppen Befehle."""

    def __init__(self, memory: Memory | None = None) -> None:
        self.memory = memory or Memory()
        self.plan: str | None = None
        self.plan_since = 0.0
        self.next_think = 0.0
        self.next_plan = 0.0
        self.report: Report | None = None
        self.state: dict[int, GroupState] = {}
        self.storm = False               # belagern/tor: losgeschlagen
        self.breach_time: float | None = None
        self.exhausted = False           # zermürben verbraucht
        self.plan_start: tuple[int, int] = (0, 0)   # Gefallene (eigen, Feind) zu Planbeginn
        self.tower_id: int | None = None
        self.tower_cell: tuple[int, int] | None = None
        self.finished = False
        self.gate_was_closed: bool | None = None
        self.front_was_blocked: bool | None = None
        self.roles: dict[int, str] = {}          # flankieren: "binden" oder "flanke" je Gruppe
        self.flank_target: int | None = None
        self.flank_ready = False

    # -- Takt ---------------------------------------------------------------
    def think(self, b: "Battle") -> None:
        self._refresh(b)
        if b.time < self.next_think and self.plan is not None:
            return
        self.next_think = b.time + config.AI_INTERVAL
        self.report = self._report(b)
        self._choose_plan(b)
        if b.scenario.enemy_kind == "raeuber":
            self._orders_raiders(b)
        else:
            self._orders_settlement(b)

    def finish(self, b: "Battle") -> None:
        """Schlacht zu Ende: den laufenden Plan bewerten und merken, bei der
        Siedlung auch die gewählte Aufstellung gegen diese Spielertruppe."""
        if self.finished or self.plan is None:
            return
        self.finished = True
        self._record(b)
        if b.scenario.enemy_kind != "raeuber" and b.doctrine:
            from .doctrine import MEMORY_KEY, classify
            own_start = max(1, b.men_start.get(Side.FEIND, 1))
            foe_start = max(1, b.men_start.get(Side.STADT, 1))
            gain = b.fallen(Side.STADT) / foe_start - b.fallen(Side.FEIND) / own_start
            self.memory.record(f"{MEMORY_KEY}:{classify(b.army)}", b.doctrine, gain)

    def plan_name(self) -> str:
        return PLAN_NAMES.get(self.plan or "", "")

    def _st(self, u: Lochos) -> GroupState:
        return self.state.setdefault(u.id, GroupState())

    def _refresh(self, b: "Battle") -> None:
        """Jeden Schritt: Verfolger folgen ihrem Ziel, Fliehende laufen vom Feld."""
        for u in b.units(Side.FEIND):
            if u.stance is Stance.FLUCHT:
                u.target = b.flee_target(u)
                continue
            if u.stance is Stance.ANGRIFF and u.target_id is not None:
                foe = b.by_id(u.target_id)
                if foe is not None and foe.fighting:
                    u.target = foe.pos

    # -- Lagebericht (Stufe 1) ------------------------------------------------
    def _report(self, b: "Battle") -> Report:
        foes = b.units(Side.STADT, fighting_only=True)
        own = b.units(Side.FEIND, fighting_only=True)
        phalanxes = [u for u in foes if u.stance is Stance.PHALANX and not u.loose]
        if own:
            cx = sum(u.x for u in own) / len(own)
            cy = sum(u.y for u in own) / len(own)
        elif b.gate is not None:
            cx, cy = b.gate.center
        else:
            cx, cy = b.cols / 2, 0.0
        exposed = {u.id for u in foes if self._exposed(b, u, foes)}
        blocking = [
            p for p in phalanxes
            if arc(p.facing, sub((cx, cy), p.pos), config.FRONT_ARC, config.REAR_ARC) == "front"
            and dist(p.pos, (cx, cy)) <= config.AI_FRONT_RANGE
        ]
        line_y = sum(p.y for p in blocking) / len(blocking) if blocking else None
        room_west = min((p.x - p.half_w for p in blocking), default=b.cols / 2)
        room_east = min((b.cols - (p.x + p.half_w) for p in blocking), default=b.cols / 2)
        gate_guarded = False
        if b.gate is not None:
            gx, gy = b.gate.center
            inner = 1.0 if b.wall_side() is Side.STADT else -1.0
            gate_guarded = any(
                (p.y - gy) * inner > 0 and dist(p.pos, (gx, gy)) <= config.AI_GATE_GUARD_RANGE for p in phalanxes
            )
        return Report(
            time=b.time, foes=foes, phalanxes=phalanxes, exposed=exposed,
            own_strength=strength(own), foe_strength=strength(foes),
            front_blocked=bool(blocking), line_y=line_y, room_west=room_west, room_east=room_east,
            foes_west=sum(1 for u in foes if u.x < b.cols / 2), foes_east=sum(1 for u in foes if u.x >= b.cols / 2),
            gate_guarded=gate_guarded, own_ammo=sum(u.ammo() for u in own),
            foe_wall_ammo=sum(u.ammo() for u in foes if b.on_wall(u)),
            threat_x=self._threat_x(b, foes),
        )

    def _exposed(self, b: "Battle", u: Lochos, foes: list[Lochos]) -> bool:
        """Ungedeckt: aufgelöst, Peltasten ohne Hopliten in der Nähe,
        abgesessene Reiter."""
        if u.loose:
            return True
        if u.share(lambda m: m.kind.ranged) >= 0.5 and not b.on_wall(u):
            cover = [f for f in foes if f is not u and f.share(lambda m: m.kind.hoplite) >= 0.5
                     and dist(f.pos, u.pos) <= config.AI_COVER_RANGE]
            return not cover
        if u.share(lambda m: m.kind.cavalry) >= 0.5 and not u.mounted_men():
            return True
        return False

    def _threat_x(self, b: "Battle", foes: list[Lochos]) -> float | None:
        if not b.blocked:
            return None
        for u in foes:
            if u.engine == "tower" and u.tower_cell is not None:
                return u.tower_cell[0] + 0.5
        if b.crossings:
            return sum(c[0] + 0.5 for c in b.crossings) / len(b.crossings)
        if b.gate is not None and any(u.engine == "ram" for u in foes):
            return b.gate.center[0]
        wall_y = next(iter(b.blocked))[1] + 0.5
        near = [u for u in foes if abs(u.y - wall_y) <= config.AI_WALL_WATCH]
        if near:
            return min(near, key=lambda u: abs(u.y - wall_y)).x
        return None

    # -- Ziele und Wege ------------------------------------------------------
    def target_value(self, b: "Battle", u: Lochos, foe: Lochos) -> float:
        """Wie lohnend ist ein Ziel: schwache Ziele hoch, Phalanxfront niedrig."""
        r = self.report
        v = 1.0
        if r is not None and foe.id in r.exposed:
            v = 2.0
        elif formed(foe):
            a = b.arc_of(foe, u.pos)
            v = {"front": 0.45, "flank": 1.1, "rear": 1.3}[a]
            if a == "flank":
                v *= b.shield_side(foe, u.pos, 0.9, 1.1)      # die schildlose rechte Seite lohnt mehr
        if b.on_wall(foe) != b.up(u):
            v *= 0.3
        elif not formed(foe) and r is not None and not any(
                f is not foe and dist(f.pos, foe.pos) <= config.AI_ISOLATION_RANGE for f in r.foes):
            v += 0.5                                   # allein vor der eigenen Linie
        st = self.state.get(u.id)
        if st is not None and st.hard == foe.id:
            v *= 0.5
        if any(o.target_id == foe.id and o.stance is Stance.ANGRIFF for o in b.units(Side.FEIND, True) if o is not u):
            v += 0.2
        return v

    def pick_target(self, b: "Battle", u: Lochos, foes: list[Lochos]) -> Lochos | None:
        best, best_s = None, 0.0
        for f in foes:
            d = f.rect_distance(u.pos)
            s = self.target_value(b, u, f) / (1.0 + d / 3.0)
            if s > best_s:
                best, best_s = f, s
        return best

    def flank_route(self, b: "Battle", u: Lochos, foe: Lochos) -> Point | None:
        return flank_route(b, u, foe)


    def _attack(self, b: "Battle", u: Lochos, foe: Lochos) -> None:
        st = self._st(u)
        if u.target_id != foe.id or st.attack_men is None:
            st.attack_men = u.men
            st.attack_hp = sum(m.hp for m in u.all_men())
        u.stance = Stance.ANGRIFF
        u.in_line = False
        u.target_id = foe.id
        u.target = foe.pos
        u.waypoints = []

    def _go(self, b: "Battle", u: Lochos, p: Point, stance: Stance = Stance.HALTEN) -> None:
        u.stance = stance
        u.in_line = False
        u.target_id = None
        u.target = b._free_spot(p, u)

    def _engage(self, b: "Battle", u: Lochos, foe: Lochos) -> None:
        """Angreifen, aber eine Phalanxfront umgehen, solange man noch nicht im Handgemenge ist."""
        wp = None if b._gap(u, foe) <= config.ENGAGE_RANGE else self.flank_route(b, u, foe)
        if wp is None:
            self._attack(b, u, foe)
        else:
            self._go(b, u, wp)

    def _busy(self, b: "Battle", u: Lochos) -> bool:
        """Im Handgemenge mit dem eigenen Ziel: die Befehle bleiben."""
        if u.stance is not Stance.ANGRIFF or not u.engaged or u.target_id is None:
            return False
        foe = b.by_id(u.target_id)
        return foe is not None and foe.fighting and b._gap(u, foe) <= config.ENGAGE_RANGE

    def _retreating(self, b: "Battle", u: Lochos) -> bool:
        """Stufe 3: Ein gescheiterter Angriff wird abgebrochen, die Gruppe
        sammelt sich außer Reichweite, statt bis zur Flucht zu kämpfen."""
        st = self._st(u)
        if st.retreat_until > b.time:
            return True
        if u.stance is not Stance.ANGRIFF or st.attack_men is None or u.target_id is None:
            return False
        foe = b.by_id(u.target_id)
        if foe is None or not formed(foe):
            return False
        lost = 1.0 - sum(m.hp for m in u.all_men()) / max(1e-6, st.attack_hp)   # Gefallene und Verwundete
        shaken = u.morale <= u.rout_threshold + config.AI_RETREAT_MORALE
        if (lost < config.AI_RETREAT_LOSS and not shaken) or u.morale <= u.rout_threshold + 0.03:
            return False
        if b.arc_of(foe, u.pos) != "front":
            return False
        away = norm(sub(u.pos, foe.pos))
        spot = (u.x + away[0] * config.AI_RETREAT_DISTANCE, u.y + away[1] * config.AI_RETREAT_DISTANCE)
        self._go(b, u, spot)
        st.retreat_until = b.time + config.AI_RETREAT_TIME
        st.attack_men = None
        st.hard = foe.id
        b.events.append(f"{u.name} ({u.side.value}) weichen vor der Phalanx zurück")
        return True

    # -- Pläne (Stufe 2) ------------------------------------------------------
    def _choose_plan(self, b: "Battle") -> None:
        r = self.report
        assert r is not None
        gate_closed = b.gate is not None and b.gate.closed
        breached = self.gate_was_closed and not gate_closed
        self.gate_was_closed = gate_closed
        if breached:
            self.breach_time = b.time
            self.storm = False
        front_changed = self.front_was_blocked is not None and r.front_blocked != self.front_was_blocked
        self.front_was_blocked = r.front_blocked
        due = self.plan is None or b.time >= self.next_plan or breached or front_changed
        if self.plan == "zermuerben" and not self.exhausted:
            if r.own_ammo == 0 or b.time >= self.plan_since + config.AI_HARASS_TIME:
                self.exhausted = True
                due = True
        if self.plan in ("flankieren", "ruecken"):
            target = b.by_id(self.flank_target) if self.flank_target is not None else None
            if target is None or not target.fighting or not formed(target) and not target.engaged:
                due = True
        if self.plan == "belagern" and not self.storm:
            if not r.gate_guarded or b.time >= self.plan_since + config.AI_SIEGE_PATIENCE:
                self.storm = True
                b.events.append("Die Räuber stürmen das Tor")
                due = True
        if not due:
            return
        scores = self._scores(b, r)
        key = b.scenario.key
        for plan in scores:
            scores[plan] *= self.memory.weight(key, plan)
        plan = max(scores, key=lambda p: (scores[p], p))
        self.next_plan = b.time + config.AI_PLAN_INTERVAL
        if plan == self.plan:
            return
        if self.plan is not None:
            self._record(b)
        self.plan = plan
        self.plan_since = b.time
        self.plan_start = (b.fallen(Side.FEIND), b.fallen(Side.STADT))
        self._start_plan(b, plan, r)
        who = "Die Räuber" if b.scenario.enemy_kind == "raeuber" else "Die Siedlung"
        b.events.append(f"{who}: {PLAN_NAMES[plan]}")

    def _scores(self, b: "Battle", r: Report) -> dict[str, float]:
        s: dict[str, float] = {}
        groups = b.units(Side.FEIND, fighting_only=True)
        if b.scenario.enemy_kind != "raeuber":
            s["halten"] = 1.0
            wall_shut = bool(b.blocked) and b.gate is not None and b.gate.closed and not b.crossings
            pelted = any(
                f.share(lambda m: m.kind.ranged) >= 0.5 and f.ammo() > 0
                and any(f.rect_distance(o.pos) <= config.JAVELIN_RANGE + 0.5 for o in groups if formed(o))
                for f in r.foes
            )
            v = 0.6
            if r.ratio >= 1.3 and any(dist(f.pos, o.pos) <= 7.0 for f in r.foes for o in groups):
                v += 0.6
            if pelted:
                v += 0.5
            if wall_shut:
                v -= 1.0
            s["vorruecken"] = v
            return s
        if b.attacking and not b.horde_awake:
            s["lagern"] = 1.0
            return s
        if b.gate is not None and b.gate.closed:
            s["tor"] = 1.0
            if len(groups) >= 2 and b.blocked:
                s["turm"] = 1.2 if (r.gate_guarded or r.foe_wall_ammo > 0) else 0.8
            return s
        if b.gate is not None and r.gate_guarded and not self.storm and self.breach_time is not None:
            s["belagern"] = 1.2                     # vor dem bewachten Tor warten, über den Turm einsickern
            s["frontal"] = 0.9                      # durch die enge Torlücke zählt Übermacht nicht
            return s
        s["frontal"] = 1.0 + (0.8 if r.ratio >= 1.5 else 0.0) - (0.9 if r.front_blocked else 0.0)
        if r.front_blocked:
            n = max(1, len(r.foes))
            reachable = [g for g in groups if not b.on_wall(g) and self._flank_candidate(b, g, r)]
            if len(reachable) >= 2 and r.ratio >= config.AI_FLANK_RATIO:
                mounted = any(g.cavalry_share() > 0 for g in reachable)
                target = self._blocking_phalanx(b, r)
                room = self._room_behind(b, target) if target is not None else 0.0
                s["flankieren"] = 1.3 + (0.2 if mounted else 0.0) + (0.1 if room < config.AI_REAR_ROOM + 1.5 else 0.0)
                if room >= config.AI_REAR_ROOM:
                    # der weitere Weg lohnt sich, wenn hinter der Phalanx Platz ist; Reiter gehen ihn schnell;
                    # bei gleichem Wert entscheidet das Gedächtnis, was zuletzt besser lief
                    s["ruecken"] = 1.3 + (0.3 if mounted else 0.0) + (0.1 if room >= config.AI_REAR_ROOM + 1.5 else 0.0)
            s["umgehen_west"] = 0.9 + (0.3 if r.room_west >= 2.5 else 0.0) - (0.6 if r.room_west < 1.5 else 0.0) \
                - 0.3 * r.foes_west / n
            s["umgehen_ost"] = 0.9 + (0.3 if r.room_east >= 2.5 else 0.0) - (0.6 if r.room_east < 1.5 else 0.0) \
                - 0.3 * r.foes_east / n
            if r.own_ammo > 0 and not self.exhausted:
                s["zermuerben"] = 1.15
        return s

    def _start_plan(self, b: "Battle", plan: str, r: Report) -> None:
        if plan.startswith("umgehen") and r.line_y is not None:
            side_x = 0.8 if plan == "umgehen_west" else b.cols - 0.8
            forward = 1.0 if not b.attacking else -1.0      # Räuber kommen von Norden, die Horde liegt im Norden
            for u in b.units(Side.FEIND, fighting_only=True):
                if self._st(u).retreat_until > b.time or u is self._ram_unit_if(b):
                    continue
                before = r.line_y - forward * 2.0
                behind = r.line_y + forward * 2.0
                first_y = min(u.y, before) if forward > 0 else max(u.y, before)
                u.waypoints = [(side_x, first_y), (side_x, behind)]
                u.stance = Stance.HALTEN
                u.target_id = None
        elif plan == "turm":
            self._assign_tower(b, r)
        elif plan in ("flankieren", "ruecken"):
            self._assign_flank_roles(b, r)
        if plan in ("frontal", "zermuerben", "belagern", "tor", "flankieren", "ruecken"):
            for u in b.units(Side.FEIND, fighting_only=True):
                u.waypoints = []

    def _record(self, b: "Battle") -> None:
        own0, foe0 = self.plan_start
        own_start = max(1, b.men_start.get(Side.FEIND, 1))
        foe_start = max(1, b.men_start.get(Side.STADT, 1))
        gain = (b.fallen(Side.STADT) - foe0) / foe_start - (b.fallen(Side.FEIND) - own0) / own_start
        self.memory.record(b.scenario.key, self.plan, gain)

    # -- Binden und Umfassen --------------------------------------------------
    def _room_behind(self, b: "Battle", target: Lochos) -> float:
        """Freier Raum hinter einer Phalanx bis zum Kartenrand, zur Palisade oder
        zur nächsten Phalanx dahinter (in Kacheln)."""
        fx, fy = target.facing
        room = 0.0
        step = 0.5
        while room < 6.0:
            room += step
            p = (target.x - fx * (target.half_d + room), target.y - fy * (target.half_d + room))
            if not b.inside(*p) or b.is_blocked(p[0], p[1]):
                return room - step
            if any(o is not target and formed(o) and o.rect_distance(p) <= 0.3
                   for o in b.units(Side.STADT, fighting_only=True)):
                return room - step
        return room

    def _flank_candidate(self, b: "Battle", g: Lochos, r: Report) -> bool:
        target = self._blocking_phalanx(b, r)
        return target is not None and b.wall_clear(g.pos, target.pos)

    def _blocking_phalanx(self, b: "Battle", r: Report) -> Lochos | None:
        own = [g for g in b.units(Side.FEIND, fighting_only=True) if not b.on_wall(g)]
        if not own or not r.phalanxes:
            return None
        cx = sum(g.x for g in own) / len(own)
        cy = sum(g.y for g in own) / len(own)
        facing_us = [p for p in r.phalanxes
                     if arc(p.facing, sub((cx, cy), p.pos), config.FRONT_ARC, config.REAR_ARC) == "front"]
        pool = facing_us or r.phalanxes
        return max(pool, key=lambda p: strength([p]) / (1.0 + dist(p.pos, (cx, cy)) / 6.0))

    def _assign_flank_roles(self, b: "Battle", r: Report) -> None:
        """Ein Teil bindet die Front, der Rest (Reiter zuerst) geht um die Flanke."""
        target = self._blocking_phalanx(b, r)
        self.roles = {}
        self.flank_ready = False
        self.flank_target = target.id if target is not None else None
        if target is None:
            return
        groups = [g for g in b.units(Side.FEIND, fighting_only=True) if not b.on_wall(g) and g is not self._ram_unit_if(b)]
        if len(groups) < 2:
            return
        need = config.AI_PIN_SHARE * strength([target])
        # Binden: die Gruppen, die am ehesten vor der Front stehen (nah, Fußvolk, mittig)
        def pin_order(g: Lochos) -> tuple:
            along, forward = target.local(g.pos)
            return (g.cavalry_share() > 0, abs(along), -forward)
        pinned = 0.0
        for g in sorted(groups, key=pin_order):
            if pinned >= need and len([x for x in self.roles.values() if x == "binden"]) >= 1:
                self.roles[g.id] = "flanke"
            else:
                self.roles[g.id] = "binden"
                pinned += strength([g])
        if all(v == "binden" for v in self.roles.values()):
            # Übermacht ohne Rest: die letzte Gruppe geht trotzdem um die Flanke
            last = sorted(groups, key=pin_order)[-1]
            self.roles[last.id] = "flanke"
        what = "fallen in den Rücken von" if self.plan == "ruecken" else "umfassen"
        b.events.append(f"{sum(1 for v in self.roles.values() if v == 'binden')} Gruppe(n) binden, "
                        f"{sum(1 for v in self.roles.values() if v == 'flanke')} {what} {target.name}")

    def _flank_orders(self, b: "Battle", u: Lochos, r: Report, deep: bool = False) -> bool:
        """Binden und Umfassen; mit ``deep`` laufen die Umfassenden ganz herum
        und fallen der Phalanx in den Rücken."""
        target = b.by_id(self.flank_target) if self.flank_target is not None else None
        if target is None or not target.fighting or not self._reachable(b, u, target):
            return False
        role = self.roles.get(u.id)
        if role is None:
            role = self.roles[u.id] = "flanke"
        along, forward = target.local(u.pos)
        in_front = b.arc_of(target, u.pos) == "front"
        if role == "binden":
            if self._skirmish(b, u, [target]):
                return True                             # Peltasten binden mit Speeren, nicht im Handgemenge
            if self.flank_ready or b.time >= self.plan_since + config.AI_PIN_DELAY or not in_front:
                self._attack(b, u, target)
            else:
                keep = target.half_d + config.AI_PIN_DISTANCE
                spot = local_to_world(target, max(-target.half_w, min(target.half_w, along)), keep)
                if dist(u.pos, spot) > 0.4:
                    self._go(b, u, spot)
            return True
        wp = rear_route(b, u, target) if deep else self.flank_route(b, u, target)
        if wp is None:
            self._attack(b, u, target)
        else:
            self._go(b, u, wp)
        arc_now = b.arc_of(target, u.pos)
        if deep:
            if arc_now == "rear" and target.rect_distance(u.pos) <= config.AI_FLANK_MARGIN + 0.7:
                self.flank_ready = True             # jemand steht im Rücken: die Bindenden greifen an
        elif not in_front and target.rect_distance(u.pos) <= config.AI_FLANK_MARGIN + 0.7:
            self.flank_ready = True                 # jemand steht an der Flanke: die Bindenden greifen an
        return True

    # -- Räuber und Horde -----------------------------------------------------
    def _ram_unit_if(self, b: "Battle") -> Lochos | None:
        if b.gate is None or not b.gate.closed or b.enemy_ram_id is None:
            return None
        return b.by_id(b.enemy_ram_id)

    def _assign_tower(self, b: "Battle", r: Report) -> None:
        if b.gate is None or not b.blocked:
            return
        wall_y = b.gate.cells[0][1]
        west = r.foes_west <= r.foes_east
        cell = (1, wall_y) if west else (b.cols - 2, wall_y)
        if cell in b.ladders or cell not in b.blocked:
            cell = (0, wall_y) if west else (b.cols - 1, wall_y)
        ram = self._ram_unit_if(b)
        cands = [u for u in b.units(Side.FEIND, fighting_only=True) if u is not ram and not b.on_wall(u)]
        if not cands:
            return
        u = min(cands, key=lambda g: dist(g.pos, (cell[0] + 0.5, cell[1] + 0.5)))
        self.tower_id = u.id
        self.tower_cell = cell
        u.waypoints = []

    def _drive_tower(self, b: "Battle", u: Lochos) -> None:
        cell = self.tower_cell
        assert cell is not None
        cx, cy = cell[0] + 0.5, cell[1] + 0.5
        outside = -1.0 if b.wall_side() is Side.STADT else 1.0     # Räuber stehen nördlich der Palisade
        if cell in b.crossings:
            return
        if u.engine == "tower":
            u.stance = Stance.HALTEN
            u.target_id = None
            u.tower_cell = cell
            u.target = (cx, cy + outside * (0.5 + u.half_d + 0.3))
            u.face_to = (0.0, -outside)
            return
        if u.building is not None:
            u.target = None
            return
        spot = (cx, cy + outside * config.AI_TOWER_BUILD_DISTANCE)
        if dist(u.pos, spot) > 0.6:
            self._go(b, u, spot)
            return
        u.building = 0.0
        u.build_kind = "tower"
        u.target = None
        b.events.append("Die Räuber bauen einen Belagerungsturm")

    def _rally_spot(self, b: "Battle", u: Lochos, r: Report) -> Point:
        gx, gy = b.gate.center
        outside = -1.0 if b.wall_side() is Side.STADT else 1.0
        far = config.ENEMY_RALLY_DISTANCE
        if r.foe_wall_ammo > 0:
            far = config.JAVELIN_RANGE + config.WALL_RANGE_BONUS + 0.8       # außer Reichweite des Wehrgangs
        far += 0.6 * ((u.id // 5) % 3)
        spread = ((u.id % 5) - 2) * 1.3
        return (gx + spread, gy + outside * far)

    def _orders_raiders(self, b: "Battle") -> None:
        r = self.report
        assert r is not None
        own = b.units(Side.FEIND, fighting_only=True)
        if b.attacking and not b.horde_awake:
            if any(u.rect_distance(f.pos) <= config.HORDE_TRIGGER for u in own for f in r.foes):
                b.horde_awake = True
                b.events.append("Die Horde stürmt")
                self.next_plan = 0.0
                self._choose_plan(b)
            else:
                for u in own:
                    u.stance = Stance.HALTEN
                return
        ram = b._raider_ram_unit()
        tower = b.by_id(self.tower_id) if self.tower_id is not None else None
        if tower is not None and (not tower.fighting or tower is ram):
            tower = None
            self.tower_id = None
        if tower is None and self.tower_cell is not None:
            # ein fertiger (oder halb gebauter) Turm wird an den Wall gefahren, gleich unter welchem Plan
            built = [u for u in own if u.engine == "tower" or (u.building is not None and u.build_kind == "tower")]
            if built:
                tower = built[0]
                self.tower_id = tower.id
        if self.plan == "turm" and tower is None and self.tower_cell not in b.crossings:
            self._assign_tower(b, r)
            tower = b.by_id(self.tower_id) if self.tower_id is not None else None
        gate_open = b.gate is not None and not b.gate.closed
        gathering = (
            self.plan == "tor" and gate_open and self.breach_time is not None
            and b.time < self.breach_time + config.AI_GATHER_TIME
        )
        for u in own:
            if self._retreating(b, u) or self._busy(b, u):
                continue
            if u is ram:
                b._drive_raider_ram(u)
                continue
            if u is tower and self.tower_cell is not None and self.tower_cell not in b.crossings:
                self._drive_tower(b, u)
                continue
            if b.gate is not None and not b.up(u) and (
                (b.gate.closed and self.plan in ("tor", "turm")) or (self.plan == "belagern" and not self.storm) or gathering
            ):
                inside = self._inside_wall(b, u)
                if not inside:
                    foe = self._nearby_foe(b, u, config.ENGAGE_RANGE + 0.3)
                    if foe is not None:
                        self._attack(b, u, foe)
                    elif not self._via_tower(b, u):
                        self._go(b, u, self._rally_spot(b, u, r))
                    continue
            self._fight_or_move(b, u, r)

    def _via_tower(self, b: "Battle", u: Lochos) -> bool:
        """Steht ein Turm, sickern wartende Gruppen darüber ein statt vor dem Tor zu stehen:
        Ziel ist ein Fleck hinter dem Wall am Turm; den Weg über Turm und Leiter sucht
        sich jeder Mann selbst."""
        if not b.crossings or u.engine is not None or u.building is not None:
            return False
        cell = min(b.crossings, key=lambda c: dist(u.pos, (c[0] + 0.5, c[1] + 0.5)))
        u.stance = Stance.HALTEN
        u.in_line = False
        u.target_id = None
        u.target = b._free_spot((cell[0] + 0.5, cell[1] + 0.5 + b._inner_dir() * config.AI_TOWER_LANDING), u)
        u.via = ((cell[0] + 0.5, cell[1] + 0.5), u.target)      # über den Turm, nicht durchs bewachte Tor
        return True

    def _inside_wall(self, b: "Battle", u: Lochos) -> bool:
        """Jenseits des Walls oder schon oben auf dem Wehrgang (oder gerade beim
        Übersteigen: dann gilt die Gruppe als oben)."""
        if b.gate is None:
            return True
        if b.up(u):
            return True
        gy = b.gate.center[1]
        return (u.y > gy) == (b.wall_side() is Side.STADT)

    def _nearby_foe(self, b: "Battle", u: Lochos, reach: float) -> Lochos | None:
        r = self.report
        assert r is not None
        cands = [f for f in r.foes if f.rect_distance(u.pos) <= reach and self._reachable(b, u, f)]
        return self.pick_target(b, u, cands)

    def _reachable(self, b: "Battle", u: Lochos, f: Lochos) -> bool:
        """Gleiche Ebene (Boden oder Wehrgang) und kein Wall dazwischen. Wer gerade
        übersteigt, gilt als oben."""
        if b.on_wall(f) != b.up(u):
            return False
        return b.up(u) or b.wall_clear(u.pos, f.pos)

    def _skirmisher(self, b: "Battle", u: Lochos) -> bool:
        """Peltasten mit Speeren auf dem Boden plänkeln statt zu stürmen."""
        return (u.share(lambda m: m.kind.ranged) >= 0.5 and u.ammo() > 0 and not b.on_wall(u)
                and u.engine is None and u.building is None)

    def _skirmish(self, b: "Battle", u: Lochos, foes: list[Lochos]) -> bool:
        """Plänkeln, wenn ein erreichbarer Gegner nahe genug ist; wer schon
        plänkelt, bleibt etwas länger dabei. Die Schlacht selbst führt die
        Gruppe dann (heran, werfen, ausweichen)."""
        if not self._skirmisher(b, u):
            return False
        reach = config.AI_SKIRMISH_KEEP if u.stance is Stance.PLAENKELN else config.AI_SKIRMISH_SEEK
        if not any(f.rect_distance(u.pos) <= reach and self._reachable(b, u, f) for f in foes):
            return False
        if u.stance is not Stance.PLAENKELN:
            u.stance = Stance.PLAENKELN
            u.in_line = False
            u.target_id = None
            u.target = None
            u.waypoints = []
        return True

    def _fight_or_move(self, b: "Battle", u: Lochos, r: Report) -> None:
        plan = self.plan or "frontal"
        on_wall = b.up(u)
        if plan in ("flankieren", "ruecken") and not on_wall and self._flank_orders(b, u, r, deep=plan == "ruecken"):
            return
        seek = config.SEEK_RANGE if not b.attacking else 99.0
        cands = [f for f in r.foes if f.rect_distance(u.pos) <= seek and self._reachable(b, u, f)]
        if plan.startswith("umgehen") and u.waypoints:
            # unterwegs um die Front: nur ungedeckte Gegner oder Flanke/Rücken angreifen
            cands = [f for f in cands if f.id in r.exposed or not formed(f)
                     or b.arc_of(f, u.pos) != "front"]
            if self._skirmish(b, u, cands):
                return
        elif self._skirmish(b, u, r.foes):
            return
        if u.stance is Stance.PLAENKELN:
            u.stance = Stance.HALTEN                     # kein Gegner mehr in Wurfnähe
            u.target = None
        if plan == "zermuerben" and not on_wall:
            close = self._nearby_foe(b, u, config.ENGAGE_RANGE + 0.4)
            if close is not None:
                self._attack(b, u, close)
                return
            spot = self._harass_spot(b, u, r)
            if spot is not None:
                self._go(b, u, spot)
                return
        foe = self.pick_target(b, u, cands)
        if foe is not None and (not formed(foe) or self.target_value(b, u, foe) >= 0.6 or plan == "frontal"
                                or foe.rect_distance(u.pos) <= config.ENGAGE_RANGE + 0.3):
            self._engage(b, u, foe)
            return
        if u.stance is Stance.ANGRIFF:
            u.stance = Stance.HALTEN
            u.target_id = None
        if u.waypoints:
            if dist(u.pos, u.waypoints[0]) <= 1.0:
                u.waypoints.pop(0)
            if u.waypoints:
                self._go(b, u, u.waypoints[0])
                return
        if not b.attacking:
            u.stance = Stance.RAUB
            u.target_id = None
            house = house_for(b, u)
            u.target = house.center if house is not None else (u.x, -3.0)
            return
        foe = self.pick_target(b, u, [f for f in r.foes if self._reachable(b, u, f)] or r.foes)
        if foe is not None:
            self._engage(b, u, foe)

    def _harass_spot(self, b: "Battle", u: Lochos, r: Report) -> Point | None:
        """Zermürben: mit Speeren vor der Front stehen bleiben, ohne Speere dahinter warten."""
        targets = r.phalanxes or r.foes
        if not targets:
            return None
        p = min(targets, key=lambda f: dist(f.pos, u.pos))
        along, forward = p.local(u.pos)
        has_ammo = u.ammo() > 0
        keep = p.half_d + (config.JAVELIN_RANGE - 0.6 if has_ammo else config.JAVELIN_RANGE + 1.2)
        spread = ((u.id % 5) - 2) * 0.9
        return local_to_world(p, max(-p.half_w, min(p.half_w, along)) + spread, keep if forward >= 0 else -keep)

    # -- Siedlung (gespiegelte Truppe) ---------------------------------------
    def _orders_settlement(self, b: "Battle") -> None:
        r = self.report
        assert r is not None
        own = b.units(Side.FEIND, fighting_only=True)
        wall = bool(b.blocked)
        wall_y = next(iter(b.blocked))[1] + 0.5 if wall else None
        gate_open = b.gate is not None and not b.gate.closed
        inside = [f for f in r.foes if wall and self._foe_inside(b, f)]
        lines = [u for u in own if u.share(lambda m: m.kind.hoplite) >= 0.5 or (
            u.share(lambda m: m.kind.ranged) < 0.5 and u.share(lambda m: m.kind.cavalry) < 0.5)]
        cover_id: int | None = None
        if wall and r.threat_x is not None and lines:
            cover = min(lines, key=lambda u: abs(u.x - r.threat_x))
            cover_id = cover.id
        for u in own:
            if self._retreating(b, u) or self._busy(b, u):
                continue
            cav = u.share(lambda m: m.kind.cavalry) >= 0.5
            pelt = u.share(lambda m: m.kind.ranged) >= 0.5
            if u.stance is Stance.ANGRIFF:
                foe = b.by_id(u.target_id) if u.target_id is not None else None
                if foe is not None and foe.fighting and (self.target_value(b, u, foe) >= 0.6 or u.engaged):
                    continue
                u.stance = Stance.HALTEN
                u.target_id = None
                u.target = None
            if cav:
                self._settlement_cavalry(b, u, r, gate_open, wall)
            elif pelt:
                self._settlement_peltasts(b, u, r, lines, wall_y)
            else:
                self._settlement_line(b, u, r, inside, cover_id, wall_y)

    def _foe_inside(self, b: "Battle", f: Lochos) -> bool:
        if b.gate is None:
            return True
        gy = b.gate.center[1]
        return f.y < gy and not b.on_wall(f)

    def _settlement_cavalry(self, b: "Battle", u: Lochos, r: Report, gate_open: bool, wall: bool) -> None:
        cands = []
        for f in r.foes:
            if b.on_wall(f):
                continue
            d = f.rect_distance(u.pos)
            if d > config.CAVALRY_TRIGGER + 1.5:
                continue
            if wall and not self._foe_inside(b, f) and not gate_open:
                continue
            if not b.wall_clear(u.pos, f.pos):
                continue
            cands.append(f)
        own = b.units(Side.FEIND, fighting_only=True)

        def value(f: Lochos) -> float:
            v = self.target_value(b, u, f)
            if formed(f) and any(o is not u and o.engaged and b._gap(o, f) <= config.ENGAGE_RANGE for o in own):
                v += config.AI_PINNED_BONUS          # von der eigenen Linie gebunden: Flanke frei
            return v

        weak = [f for f in cands if value(f) >= config.AI_CAVALRY_MIN_VALUE]
        foe = max(weak, key=lambda f: value(f) / (1.0 + f.rect_distance(u.pos) / 3.0)) if weak else None
        if foe is not None:
            if formed(foe):
                self._engage(b, u, foe)               # um die Front herum in Flanke oder Rücken
            else:
                self._attack(b, u, foe)
            if u.stance is Stance.ANGRIFF and u.target_id == foe.id:
                b.events.append(f"Reiter der Siedlung stoßen auf {foe.name} vor")
        elif u.stance is Stance.ANGRIFF:
            u.stance = Stance.HALTEN
            u.target_id = None

    def _settlement_peltasts(self, b: "Battle", u: Lochos, r: Report, lines: list[Lochos], wall_y) -> None:
        if wall_y is not None and b.on_wall(u):
            if r.threat_x is None:
                return
            spread = 1.2 * ((u.id % 3) - 1)
            x = min(max(r.threat_x + spread, 1.5), b.cols - 1.5)
            if abs(u.x - x) > 0.8:
                self._go(b, u, (x, wall_y))
            return
        foes = [f for f in r.foes if not b.on_wall(f) and (wall_y is None or self._foe_inside(b, f))]
        if self._skirmish(b, u, foes):
            return
        if u.stance is Stance.PLAENKELN:
            u.stance = Stance.HALTEN
            u.target = None
        if lines and self.plan == "vorruecken":
            line = min(lines, key=lambda l: dist(l.pos, u.pos))
            fx, fy = line.facing
            spot = (line.x - fx * (line.half_d + u.half_d + 0.6), line.y - fy * (line.half_d + u.half_d + 0.6))
            if dist(u.pos, spot) > 0.6:
                self._go(b, u, spot)

    def _settlement_line(self, b: "Battle", u: Lochos, r: Report, inside: list[Lochos],
                         cover_id: int | None, wall_y) -> None:
        if inside:
            foe = self.pick_target(b, u, [f for f in inside if dist(f.pos, u.pos) <= config.AI_SORTIE_RANGE])
            if foe is not None:
                self._engage(b, u, foe)
                return
        if wall_y is not None and u.id == cover_id and r.threat_x is not None:
            spot = (r.threat_x, wall_y - 1.7)
            if dist(u.pos, spot) > 0.7 and not (b.gate is not None and abs(r.threat_x - b.gate.center[0]) < 1.0
                                                and dist(u.pos, spot) < 2.0):
                self._go(b, u, spot, Stance.PHALANX)
                u.face_to = (0.0, 1.0)
                return
        if self.plan == "vorruecken" and r.foes:
            foe = min(r.foes, key=lambda f: dist(f.pos, u.pos))
            if b.on_wall(foe):
                return
            direction = norm(sub(foe.pos, u.pos))
            stop = foe.half_d + u.half_d + config.CONTACT_GAP      # Schild an Schild, nicht davor stehen bleiben
            spot = (foe.x - direction[0] * stop, foe.y - direction[1] * stop)
            closer = dist(spot, foe.pos) < dist(u.pos, foe.pos) - 0.1   # vorrücken heißt nie zurückweichen
            if closer and b.path_clear(u.pos, spot, u) and dist(u.pos, spot) > 0.15:
                self._go(b, u, spot, Stance.PHALANX)
                u.facing = direction
            return
        # halten: die Front zum nächsten Gegner drehen, wenn er in Flanke oder Rücken kommt
        near = [f for f in r.foes if dist(f.pos, u.pos) <= config.AI_REFACE_RANGE and not b.on_wall(f)]
        if near and u.stance is Stance.PHALANX:
            foe = min(near, key=lambda f: dist(f.pos, u.pos))
            if b.arc_of(u, foe.pos) != "front" and u.face_to is None:
                u.face_to = norm(sub(foe.pos, u.pos))      # schwenkt mit derselben Drehrate wie alle
                b.events.append(f"{u.name} der Siedlung drehen die Front")


# ------------------------------------------------------------ alte Steuerung
class LegacyBrain:
    """Die feste Regelsteuerung vor der Stufen-KI, zum Vergleich."""

    plan = None

    def __init__(self, memory: Memory | None = None) -> None:
        self.memory = memory or Memory()

    def plan_name(self) -> str:
        return ""

    def finish(self, b: "Battle") -> None:
        return None

    def think(self, b: "Battle") -> None:
        if b.attacking:
            self._defenders(b)
        else:
            self._raiders(b)

    def _raiders(self, b: "Battle") -> None:
        defenders = b.units(Side.STADT, fighting_only=True)
        ram_unit = b._raider_ram_unit()
        for u in b.units(Side.FEIND):
            if u.stance is Stance.FLUCHT:
                u.target = b.flee_target(u)
                continue
            if u is ram_unit:
                b._drive_raider_ram(u)
                continue
            foe, d = b._nearest(u, defenders)
            if foe is not None and foe.rect_distance(u.pos) <= config.SEEK_RANGE and not b.on_wall(foe):
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
            houses = [h for h in b.houses if not h.looted]
            if houses:
                u.target = min(houses, key=lambda h: dist(u.pos, h.center)).center
            else:
                u.target = (u.x, -3.0)

    def _defenders(self, b: "Battle") -> None:
        attackers = b.units(Side.STADT, fighting_only=True)
        enemies = b.units(Side.FEIND)
        if b.scenario.enemy_kind == "raeuber":
            if not b.horde_awake and any(
                u.rect_distance(a.pos) <= config.HORDE_TRIGGER for u in enemies for a in attackers
            ):
                b.horde_awake = True
                b.events.append("Die Horde stürmt")
            for u in enemies:
                if u.stance is Stance.FLUCHT:
                    u.target = b.flee_target(u)
                    continue
                if b.horde_awake:
                    u.stance = Stance.ANGRIFF
                    foe, _ = b._nearest(u, attackers)
                    u.target_id = foe.id if foe else None
                    u.target = foe.pos if foe else None
            return
        for u in enemies:
            if u.stance is Stance.FLUCHT:
                u.target = b.flee_target(u)
                continue
            if u.stance is Stance.ANGRIFF:
                target = b.by_id(u.target_id) if u.target_id is not None else None
                if target is None or not target.fighting:
                    target, _ = b._nearest(u, attackers)
                    u.target_id = target.id if target else None
                u.target = target.pos if target else None
                continue
            if u.share(lambda m: m.kind.cavalry) >= 0.5:
                foe, _ = b._nearest(u, attackers)
                if foe is not None and foe.rect_distance(u.pos) <= config.CAVALRY_TRIGGER and b.path_clear(u.pos, foe.pos, u):
                    u.stance = Stance.ANGRIFF
                    u.target_id = foe.id
                    u.target = foe.pos


def house_for(b: "Battle", u: Lochos):
    """Das Haus, das ``u`` plündern geht: das nächste, das noch keine andere eigene
    Gruppe ansteuert (sonst drängen sich alle am selben Haus), sonst das nächste."""
    houses = [h for h in b.houses if not h.looted]
    if not houses:
        return None
    taken = {o.target for o in b.units(u.side, fighting_only=True) if o is not u and o.stance is Stance.RAUB}
    free = [h for h in houses if h.center not in taken]
    return min(free or houses, key=lambda h: dist(u.pos, h.center))


def make_brain(kind: str, memory: Memory | None = None):
    return LegacyBrain(memory) if kind == "einfach" else Brain(memory)


def flank_route(b: "Battle", u: Lochos, foe: Lochos) -> Point | None:
    """Steht die Gruppe vor der Front einer Phalanx, liefert dies den
    nächsten Wegpunkt um die Front herum; sonst ``None`` (direkt angreifen)."""
    if not formed(foe):
        return None
    along, forward = foe.local(u.pos)
    if b.arc_of(foe, u.pos) != "front":
        return None
    outer = foe.half_w + config.AI_FLANK_MARGIN

    def clamp(p: Point) -> Point:
        return (min(max(p[0], 0.5), b.cols - 0.5), min(max(p[1], 0.5), b.rows - 0.5))

    # die nähere Seite; steht man etwa mittig vor Hopliten, die schildlose rechte
    right_first = along >= 0 or (abs(along) < 0.5 * foe.half_w and foe.share(lambda m: m.kind.hoplite) >= 0.5)
    for sgn in ((1.0, -1.0) if right_first else (-1.0, 1.0)):
        flank = clamp(local_to_world(foe, sgn * outer, 0.0))       # neben der Flanke, außer Reichweite der Front
        if b.is_blocked(flank[0], flank[1], u):
            continue
        if abs(along) < outer - 0.2:
            cand = clamp(local_to_world(foe, sgn * outer, max(forward, foe.half_d + 0.8)))
        else:
            cand = flank
        if b.is_blocked(cand[0], cand[1], u) or not b.path_clear(u.pos, cand, u):
            continue
        if cand != flank and not b.path_clear(cand, flank, u):
            continue
        return cand
    return None


def rear_route(b: "Battle", u: Lochos, foe: Lochos) -> Point | None:
    """Weg in den Rücken einer Phalanx: vor der Front erst neben die Flanke, von
    dort hinter die Ecke, dann hinter die Mitte; im Rücken ``None`` (angreifen)."""
    if not formed(foe):
        return None
    arc_now = b.arc_of(foe, u.pos)
    if arc_now == "rear":
        return None
    if arc_now == "front":
        return flank_route(b, u, foe)
    along, forward = foe.local(u.pos)
    sgn = 1.0 if along >= 0 else -1.0
    outer = foe.half_w + config.AI_FLANK_MARGIN
    behind = -(foe.half_d + config.AI_FLANK_MARGIN)

    def clamp(p: Point) -> Point:
        return (min(max(p[0], 0.5), b.cols - 0.5), min(max(p[1], 0.5), b.rows - 0.5))

    corner = clamp(local_to_world(foe, sgn * outer, behind))
    centre = clamp(local_to_world(foe, 0.0, behind))
    if forward > behind + 0.3:                    # noch neben der Flanke: erst hinter die Ecke
        cand = corner
    else:
        cand = centre                              # hinter der Ecke: hinter die Mitte
    if b.is_blocked(cand[0], cand[1], u) or not b.path_clear(u.pos, cand, u):
        return flank_route(b, u, foe) if arc_now == "front" else None
    return cand
