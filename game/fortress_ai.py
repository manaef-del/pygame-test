"""KI für die Festung: ein Heer belagert die sechseckige Festung, oder die
Besatzung hält sie gegen den Spieler. Kennt kein Pygame.

Angriff (das Heer): Eine Hoplitengruppe baut außer Reichweite der Wehrtürme
einen Rammbock und fährt ihn an das Tor, hinter dem die wenigsten Verteidiger
stehen; eine zweite baut einen Belagerungsturm und setzt ihn an ein Wallstück
fern von diesem Tor. Die Peltasten werfen auf die Männer auf dem Wehrgang über
dem Tor, der Rest wartet außer Reichweite. Ist ein Tor offen oder der Turm am
Wall, stürmen alle hinein: auf die Verteidiger, sonst an die Häuser.

Verteidigung (die Besatzung): Hinter jedem Tor eine Phalanx; wird ein Tor
gerammt oder ist es offen, kommt eine zweite dazu. Steht ein feindlicher Turm
am Wall, stellt sich die nächste Phalanx an den Fuß der Leiter dort. Die
Peltasten laufen auf dem Wehrgang dorthin, wo der Angriff ansetzt, die Reiter
warten auf der Agora und fallen über Eingedrungene her, die nicht in
Formation stehen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import config
from .ai import Brain, formed, house_for
from .geometry import dist, norm, sub
from .units import Lochos, Side, Stance

if TYPE_CHECKING:
    from .battle import Battle, Gate

Point = tuple[float, float]

FORT_PLANS = {
    "aufmarsch": "Aufmarsch",
    "rammen": "Tor rammen",
    "belagern": "Vor dem Tor sammeln",
    "sturm": "Sturm in die Festung",
    "halten": "Tore halten",
    "abwehr": "Abwehr am Durchbruch",
}

STAGE_DISTANCE = 7.0       # Kacheln vor dem Tor: dort warten die Stürmer, außer Reichweite der Türme
BUILD_DISTANCE = 7.5       # Kacheln vom Wall: dort wird gebaut
HARASS_DISTANCE = 2.6      # Kacheln vor dem Wall: dort werfen die Peltasten auf den Wehrgang


class FortressBrain(Brain):
    """Beide Seiten der Festung, je nach Rolle des Spielers."""

    def __init__(self, memory=None) -> None:
        super().__init__(memory)
        self.roles: dict[int, str] = {}
        self.main_gate: int | None = None
        self.second_gate: int | None = None
        self.ram_of: dict[int, int] = {}              # Rammbock-Gruppe -> Tor
        self.home: dict[int, int] = {}                # Gruppe -> Tor, vor dem sie wartet
        self.wall_cell: tuple[int, int] | None = None
        self.gate_guard: dict[int, int] = {}          # Verteidigung: Gruppe -> Tor
        self.announced: set[str] = set()
        self.breach_time: float | None = None         # wann das erste Tor fiel (danach stürmt das Heer gesammelt)

    def plan_name(self) -> str:
        return FORT_PLANS.get(self.plan or "", "")

    def think(self, b: "Battle") -> None:
        self._refresh(b)
        if b.time < self.next_think and self.plan is not None:
            return
        self.next_think = b.time + config.AI_INTERVAL
        self.report = self._report(b)
        if b.attacking:
            self._garrison(b)
        else:
            self._siege(b)
        self._brace(b)

    def finish(self, b: "Battle") -> None:
        if self.finished or self.plan is None:
            return
        self.finished = True
        self._record(b)

    def _set_plan(self, b: "Battle", plan: str) -> None:
        if plan == self.plan:
            return
        if self.plan is not None:
            self._record(b)
        self.plan = plan
        self.plan_since = b.time
        self.plan_start = (b.fallen(Side.FEIND), b.fallen(Side.STADT))
        who = "Das Heer" if not b.attacking else "Die Festung"
        b.events.append(f"{who}: {FORT_PLANS[plan]}")

    # ----------------------------------------------------------- Hilfen
    @staticmethod
    def _arm(u: Lochos) -> str:
        if u.share(lambda m: m.kind.cavalry) >= 0.5:
            return "reiter"
        if u.share(lambda m: m.kind.ranged) >= 0.5:
            return "peltasten"
        return "hopliten"

    def _same_side(self, b: "Battle", u: Lochos, f: Lochos) -> bool:
        """Kommt ``u`` an ``f`` heran, ohne Wall dazwischen (oder durch ein offenes Tor,
        über einen Turm)? Auf den Wehrgang kommt nur, wer oben ist."""
        if b.on_wall(f) != b.up(u):
            return False
        if b.up(u):
            return True
        a, c = b._wall_level(u.pos), b._wall_level(f.pos)
        if a == c or "tor" in (a, c):
            return True
        return any(not g.closed for g in b.gates)

    def _wall_men_near(self, b: "Battle", p: Point, side: Side, reach: float) -> float:
        return sum(u.men for u in b.units(side, fighting_only=True)
                   if dist(u.pos, p) <= reach and b._wall_level(u.pos) != "aussen")

    def _go_to(self, b: "Battle", u: Lochos, p: Point, stance: Stance = Stance.HALTEN, eps: float = 0.6) -> None:
        if u.target is not None and dist(u.target, p) <= eps and u.stance is stance:
            return
        if u.target is None and dist(u.pos, p) <= eps and u.stance is stance:
            return
        self._go(b, u, p, stance)

    # =========================================================== Angriff
    def _choose_gate(self, b: "Battle", own: list[Lochos]) -> int | None:
        """Das Tor, hinter dem die wenigsten Verteidiger stehen, nicht zu weit vom Heer."""
        closed = [i for i, g in enumerate(b.gates) if g.closed]
        if not closed:
            return None
        cx = sum(u.x for u in own) / len(own)
        cy = sum(u.y for u in own) / len(own)

        def score(i: int) -> float:
            g = b.gates[i]
            guard = self._wall_men_near(b, g.center, Side.STADT, 5.0)
            return guard + 0.8 * dist((cx, cy), g.center)
        return min(closed, key=score)

    def _choose_wall_cell(self, b: "Battle", avoid: list) -> tuple[int, int] | None:
        """Ein Wallstück für den Turm: außen frei zugänglich, fern von den gerammten Toren,
        von Türmen und Toren, wo wenige Verteidiger stehen, dem Heer nicht zu fern."""
        own = b.units(Side.FEIND, fighting_only=True)
        cx = sum(u.x for u in own) / len(own)
        cy = sum(u.y for u in own) / len(own)
        towers = [t.center for t in b.corner_towers]
        best, best_s = None, float("inf")
        for c in b.blocked:
            if c in b.crossings or b.tower_step(c) is None:
                continue
            p = (c[0] + 0.5, c[1] + 0.5)
            if any(dist(p, g.center) < 3.0 for g in b.gates) or any(dist(p, t) < 2.0 for t in towers):
                continue
            s = (0.6 * dist((cx, cy), p) + 2.0 * self._wall_men_near(b, p, Side.STADT, 4.0)
                 - min((min(dist(p, g.center), 10.0) for g in avoid), default=0.0))
            if s < best_s:
                best, best_s = c, s
        return best

    def _assign_siege_roles(self, b: "Battle", own: list[Lochos]) -> None:
        """Rollen einmal zu Beginn: Rammbock ans beste Tor, mit drei Hoplitengruppen ein
        zweiter an ein anderes Tor, eine Gruppe baut den Turm; Peltasten und Reiter teilen
        sich auf die gerammten Tore auf. Neue Gruppen (geteilt) stürmen mit."""
        if not self.roles:
            ranked = sorted((i for i, g in enumerate(b.gates) if g.closed),
                            key=lambda i: self._gate_score(b, own, i))
            hop = [u for u in own if self._arm(u) == "hopliten"]
            self.main_gate = ranked[0] if ranked else None
            if len(hop) >= 3 and len(ranked) >= 2:
                self.second_gate = ranked[1]
            self.ram_of: dict[int, int] = {}
            self.home: dict[int, int] = {}
            free = list(hop)
            for gi in (self.main_gate, self.second_gate):
                if gi is None or not free:
                    continue
                u = min(free, key=lambda u: dist(u.pos, b.gates[gi].center))
                free.remove(u)
                self.roles[u.id] = "ram"
                self.ram_of[u.id] = gi
                self.home[u.id] = gi
            if free and b.blocked and len(hop) >= 2:
                u = free.pop(0)
                self.roles[u.id] = "turm"
            gates = [g for g in (self.main_gate, self.second_gate) if g is not None]
            k = 0
            for u in own:
                if u.id in self.roles:
                    continue
                arm = self._arm(u)
                self.roles[u.id] = {"peltasten": "werfer", "reiter": "reiter"}.get(arm, "sturm")
                if gates:
                    self.home[u.id] = gates[k % len(gates)]
                    k += 1
        for u in own:
            if u.id not in self.roles:
                self.roles[u.id] = "sturm"
                if self.main_gate is not None:
                    self.home[u.id] = self.main_gate

    def _gate_score(self, b: "Battle", own: list[Lochos], i: int) -> float:
        cx = sum(u.x for u in own) / len(own)
        cy = sum(u.y for u in own) / len(own)
        g = b.gates[i]
        return self._wall_men_near(b, g.center, Side.STADT, 5.0) + 0.8 * dist((cx, cy), g.center)

    def _stage(self, b: "Battle", u: Lochos, gate: "Gate", distance: float, spread: float) -> Point:
        cx, cy = gate.center
        (nx, ny), (tx, ty) = gate.normal, gate.tangent
        return b._free_spot((cx + nx * distance + tx * spread, cy + ny * distance + ty * spread), u)

    def _held(self, b: "Battle", g: "Gate") -> bool:
        """Steht hinter dem offenen Tor eine Phalanx, die den Durchgang sperrt?"""
        inner = b.gate_approach(g, -1.0, 1.5)
        for f in b.units(Side.STADT, fighting_only=True):
            if f.loose or not (f.in_phalanx or f.stance is Stance.PHALANX) or f.men < 8:
                continue
            if f.rect_distance(inner) <= 2.5 and f.facing[0] * g.normal[0] + f.facing[1] * g.normal[1] > 0.3:
                return True
        return False

    def _siege(self, b: "Battle") -> None:
        r = self.report
        own = b.units(Side.FEIND, fighting_only=True)
        if not own:
            return
        self._assign_siege_roles(b, own)
        open_gates = [g for g in b.gates if not g.closed]
        breach = bool(open_gates) or bool(b.crossings)
        if breach and self.breach_time is None:
            self.breach_time = b.time
        entries = [g for g in open_gates if not self._held(b, g)]
        mass = breach and self.breach_time is not None and b.time >= self.breach_time + config.FORT_STORM_WAIT
        if entries or b.crossings or mass:
            self._set_plan(b, "sturm")
        elif breach:
            self._set_plan(b, "belagern")
        elif any(u.engine == "ram" for u in own):
            self._set_plan(b, "rammen")
        else:
            self._set_plan(b, "aufmarsch")
        rams = [b.gates[i] for i in (self.main_gate, self.second_gate) if i is not None]
        if self.wall_cell is None or (self.wall_cell in b.crossings and not breach):
            self.wall_cell = self._choose_wall_cell(b, rams)
        k_stage: dict[int, int] = {}
        for u in own:
            if self._retreating(b, u) or self._busy(b, u):
                continue
            role = self.roles.get(u.id, "sturm")
            gi = self.ram_of.get(u.id) if role == "ram" else None
            if gi is not None and b.gates[gi].closed:
                self._ram_work(b, u, b.gates[gi])
                continue
            if role == "turm" and self.wall_cell is not None and self.wall_cell not in b.crossings and (
                    not breach or u.engine == "tower" or u.building is not None):
                self._tower_work(b, u)
                continue
            if u.engine is not None and u.building is None:
                u.engine = None                               # das Gerät wird nicht mehr gebraucht
                u.tower_cell = None
            if not breach:
                self._before_breach(b, u, r, role, k_stage)
                continue
            if entries or b.crossings or mass:
                self._storm(b, u, r, entries)
                continue
            self._wait_at_breach(b, u, r, role, open_gates, k_stage)

    def _before_breach(self, b: "Battle", u: Lochos, r, role: str, k_stage: dict[int, int]) -> None:
        """Ausfälle abwehren, sonst vor dem eigenen Tor warten (außer Reichweite der Türme)
        oder, mit Speeren, auf den Wehrgang darüber werfen."""
        near = [f for f in r.foes if f.rect_distance(u.pos) <= config.ENGAGE_RANGE + 1.0 and self._same_side(b, u, f)]
        foe = self.pick_target(b, u, near)
        if foe is not None:
            self._attack(b, u, foe)
            return
        gi = self.home.get(u.id, self.main_gate)
        if gi is None:
            return
        gate = b.gates[gi]
        k = k_stage.get(gi, 0)
        k_stage[gi] = k + 1
        if role == "werfer" and u.ammo() > 0:
            self._go_to(b, u, self._stage(b, u, gate, gate.half_thick + HARASS_DISTANCE, ((k % 3) - 1) * 2.4))
        else:
            self._go_to(b, u, self._stage(b, u, gate, STAGE_DISTANCE + 1.6 * (k // 5), ((k % 5) - 2) * 2.6))

    def _wait_at_breach(self, b: "Battle", u: Lochos, r, role: str, open_gates: list, k_stage: dict[int, int]) -> None:
        """Hinter jedem offenen Tor steht eine Phalanx: nicht einzeln hineinlaufen. Die
        Peltasten werfen durch das Tor, die anderen sammeln sich davor, bis eine zweite
        Bresche offen ist oder die Wartezeit um ist; dann gehen alle zugleich."""
        near = [f for f in r.foes if f.rect_distance(u.pos) <= config.ENGAGE_RANGE + 1.0 and self._same_side(b, u, f)]
        foe = self.pick_target(b, u, near)
        if foe is not None:
            self._attack(b, u, foe)
            return
        gate = min(open_gates, key=lambda g: dist(g.center, u.pos))
        if role == "werfer" and u.ammo() > 0:
            foes = [f for f in r.foes if self._same_side(b, u, f)]
            if self._skirmish(b, u, foes):
                return
            self._go_to(b, u, b.gate_approach(gate, 1.0, 0.3))
            return
        k = k_stage.get(id(gate), 0)
        k_stage[id(gate)] = k + 1
        self._go_to(b, u, self._stage(b, u, gate, STAGE_DISTANCE - 1.5 + 1.6 * (k // 5), ((k % 5) - 2) * 2.6))

    def _ram_work(self, b: "Battle", u: Lochos, gate: "Gate") -> None:
        if u.engine == "ram":
            i = b.gates.index(gate)
            if u.ram_gate != i:
                b.drive_ram(u, gate)
            return
        if u.building is not None:
            u.target = None
            return
        spot = self._stage(b, u, gate, BUILD_DISTANCE, 0.0)
        if dist(u.pos, spot) > 0.8:
            self._go_to(b, u, spot)
            return
        u.stance = Stance.HALTEN
        u.target = None
        u.target_id = None
        u.building = 0.0
        u.build_kind = "ram"
        b._dismount(u)
        b.events.append("Das Heer baut einen Rammbock")

    def _tower_work(self, b: "Battle", u: Lochos) -> None:
        cell = self.wall_cell
        assert cell is not None
        d = b.tower_step(cell) or (0, -1)
        cx, cy = cell[0] + 0.5, cell[1] + 0.5
        if u.engine == "tower":
            if u.tower_cell != cell:
                b.drive_tower(u, cell)
            return
        if u.building is not None:
            u.target = None
            return
        out = norm((cx - b.agora[0], cy - b.agora[1])) if b.agora else (float(d[0]), float(d[1]))
        spot = b._free_spot((cx + out[0] * BUILD_DISTANCE, cy + out[1] * BUILD_DISTANCE), u)
        if dist(u.pos, spot) > 0.8:
            self._go_to(b, u, spot)
            return
        u.stance = Stance.HALTEN
        u.target = None
        u.target_id = None
        u.building = 0.0
        u.build_kind = "tower"
        b._dismount(u)
        b.events.append("Das Heer baut einen Belagerungsturm")

    def _storm(self, b: "Battle", u: Lochos, r, entries: list | None = None) -> None:
        """Nach dem Durchbruch: auf erreichbare Verteidiger, sonst an die Häuser. Wer
        draußen steht, geht durch ein Tor, hinter dem keine Phalanx sperrt, sonst über
        den Turm; Reiter nur durch ein freies Tor."""
        if u.building is not None:
            b._wake(u)
        outside = b._wall_level(u.pos) == "aussen" and not b.up(u)
        if outside and entries:
            g = min(entries, key=lambda g: dist(g.center, u.pos))
            front = b.gate_approach(g, 1.0, 0.8)
            if dist(u.pos, front) > 1.5 and not any(dist(u.pos, h.center) < 3.0 for h in b.gates if not h.closed):
                self._go_to(b, u, front)
                return
        elif outside and not entries:
            if self._arm(u) == "reiter":
                if not (self.breach_time is not None and b.time >= self.breach_time + config.FORT_STORM_WAIT):
                    gate = min(b.gates, key=lambda g: dist(g.center, u.pos))
                    self._go_to(b, u, self._stage(b, u, gate, STAGE_DISTANCE, 0.0))
                    return                                # Reiter warten, bis ein Tor frei ist
            elif b.crossings and self._via_crossing(b, u):
                return
        foes = [f for f in r.foes if self._same_side(b, u, f)]
        if self._skirmish(b, u, foes):
            return
        if u.stance is Stance.PLAENKELN:
            u.stance = Stance.HALTEN
            u.target = None
        # wer schon einen Verteidiger angreift, lässt erst mit etwas mehr Abstand von ihm ab (sonst
        # wechselt eine Gruppe an der Schwelle jeden Augenblick zwischen ihm und den Häusern)
        foe = self.pick_target(b, u, [f for f in foes if f.rect_distance(u.pos) <= config.FORT_SEEK_RANGE
                                      + (config.AI_TARGET_HYST if f.id == u.target_id else 0.0)])
        if foe is not None:
            self._engage(b, u, foe)
            return
        house = house_for(b, u)
        if house is not None:
            u.stance = Stance.RAUB
            u.target_id = None
            u.in_line = False
            u.target = house.center
            return
        foe = self.pick_target(b, u, foes or r.foes)
        if foe is not None:
            self._engage(b, u, foe)

    def _via_crossing(self, b: "Battle", u: Lochos) -> bool:
        if u.engine is not None or u.building is not None or not b.is_walker(u):
            return False
        cell = min(b.crossings, key=lambda c: dist(u.pos, (c[0] + 0.5, c[1] + 0.5)))
        down = b.nearest_ladder(u, (cell[0] + 0.5, cell[1] + 0.5), b.agora or u.pos)
        land = b.foot_of(b.cell(*down)) if down is not None else (b.agora or u.pos)
        towards = norm(sub(b.agora, land)) if b.agora else (0.0, 0.0)
        target = b._free_spot((land[0] + towards[0] * config.AI_TOWER_LANDING,
                               land[1] + towards[1] * config.AI_TOWER_LANDING), u)
        if u.via is not None and u.via[1] == u.target:
            return True
        u.stance = Stance.HALTEN
        u.in_line = False
        u.target_id = None
        u.target = target
        u.via = ((cell[0] + 0.5, cell[1] + 0.5), u.target)
        return True

    # ======================================================= Verteidigung
    def _threats(self, b: "Battle") -> list[Point]:
        """Wo der Angriff ansetzt: Rammböcke an Toren, Türme am Wall, Übergänge,
        offene Tore mit Feinden davor."""
        out: list[Point] = []
        foes = b.units(Side.STADT, fighting_only=True)
        for f in foes:
            if f.engine == "ram":
                g = min(b.gates, key=lambda g: dist(g.center, f.pos))
                if dist(g.center, f.pos) <= 6.0:
                    out.append(g.center)
            elif f.engine == "tower" and f.tower_cell is not None:
                out.append((f.tower_cell[0] + 0.5, f.tower_cell[1] + 0.5))
        out += [(c[0] + 0.5, c[1] + 0.5) for c in b.crossings]
        for g in b.gates:
            if not g.closed and any(dist(f.pos, g.center) <= 6.0 for f in foes):
                out.append(g.center)
        return out

    def _garrison(self, b: "Battle") -> None:
        r = self.report
        own = b.units(Side.FEIND, fighting_only=True)
        if not own:
            return
        threats = self._threats(b)
        inside = [f for f in r.foes if b._wall_level(f.pos) in ("innen", "tor") and not b.on_wall(f)]
        self._set_plan(b, "abwehr" if inside or b.crossings or any(not g.closed for g in b.gates) else "halten")
        lines = [u for u in own if self._arm(u) == "hopliten"]
        # jedes Tor bekommt seine Phalanx; die übrigen gehen an die bedrohten Stellen
        for u in lines:
            if u.id not in self.gate_guard or not (0 <= self.gate_guard[u.id] < len(b.gates)):
                free = [i for i in range(len(b.gates)) if i not in self.gate_guard.values()]
                pool = free or list(range(len(b.gates)))
                self.gate_guard[u.id] = min(pool, key=lambda i: dist(u.pos, b.gates[i].center)) if pool else 0
        spare = [u for u in lines if list(self.gate_guard.values()).count(self.gate_guard[u.id]) > 1
                 and u is not min((v for v in lines if self.gate_guard[v.id] == self.gate_guard[u.id]),
                                  key=lambda v: v.id)]
        # eine Phalanx, vor deren Tor niemand steht, hilft dort, wo angegriffen wird
        attackers = b.units(Side.STADT, fighting_only=True)
        for u in lines:
            g = b.gates[self.gate_guard[u.id]] if b.gates else None
            if g is None or u in spare or not threats:
                continue
            quiet = not any(dist(f.pos, g.center) <= config.FORT_GATE_WATCH for f in attackers)
            if quiet and all(dist(t, g.center) > 1.0 for t in threats):
                spare.append(u)
        for u in own:
            if self._retreating(b, u) or self._busy(b, u):
                continue
            arm = self._arm(u)
            if u.stance is Stance.ANGRIFF:
                foe = b.by_id(u.target_id) if u.target_id is not None else None
                if foe is not None and foe.fighting and (u.engaged or dist(foe.pos, u.pos) <= config.AI_SORTIE_RANGE + 2.0) \
                        and self._same_side(b, u, foe):
                    continue
                u.stance = Stance.HALTEN
                u.target_id = None
                u.target = None
            if arm == "reiter":
                self._garrison_cavalry(b, u, inside)
            elif arm == "peltasten":
                self._garrison_peltasts(b, u, r, threats, inside)
            else:
                self._garrison_line(b, u, inside, threats, u in spare)

    def _garrison_line(self, b: "Battle", u: Lochos, inside: list[Lochos], threats: list[Point], spare: bool) -> None:
        close = [f for f in inside if dist(f.pos, u.pos) <= config.AI_SORTIE_RANGE and self._same_side(b, u, f)]
        foe = self.pick_target(b, u, close)
        if foe is not None:
            self._engage(b, u, foe)
            return
        gate = b.gates[self.gate_guard.get(u.id, 0)] if b.gates else None
        post: Point | None = None
        facing: Point | None = None
        if spare and threats:
            # Reserve: an die nächste Bedrohung; an einem Turm hinauf auf den Wehrgang neben den
            # Ausstieg (dort kommt keiner vorbei), ohne Leitern vor den Fuß der Leiter dort
            t = min(threats, key=lambda p: dist(p, u.pos))
            g = b.gate_near(t, 0.6)
            tower = b.cell(*t)
            landing = b.landing(tower) if (b.is_walker(u) and tower in b.blocked) else None
            if landing is not None:
                if dist(u.pos, landing) > 0.5:
                    self._go_to(b, u, landing, Stance.HALTEN, eps=0.4)
                return
            if g is not None:
                post = b.gate_approach(g, -1.0, u.half_d + 2.4)
                facing = g.normal
            else:
                c = b.cell(*t)
                down = b.nearest_ladder(u, t, b.agora) if b.agora else None
                foot = b.foot_of(b.cell(*down)) if down is not None else t
                towards = norm(sub(b.agora, foot)) if b.agora else (0.0, 1.0)
                post = (foot[0] + towards[0] * (u.half_d + 1.2), foot[1] + towards[1] * (u.half_d + 1.2))
                facing = norm(sub(foot, post)) if dist(foot, post) > 0.1 else norm(sub((c[0] + 0.5, c[1] + 0.5), b.agora))
        elif gate is not None:
            post = b.gate_approach(gate, -1.0, u.half_d + 0.4)
            facing = gate.normal
        if post is None:
            return
        post = b._free_spot(post, u)
        if dist(u.pos, post) > 0.5 or u.stance is not Stance.PHALANX:
            if u.target is None or dist(u.target, post) > 0.5 or u.stance is not Stance.PHALANX:
                self._go(b, u, post, Stance.PHALANX)
                u.face_to = facing
        elif facing is not None and u.face_to is None and (u.facing[0] * facing[0] + u.facing[1] * facing[1]) < 0.9:
            u.face_to = facing

    def _garrison_peltasts(self, b: "Battle", u: Lochos, r, threats: list[Point], inside: list[Lochos]) -> None:
        if u.ammo() <= 0:
            if b.on_wall(u) and b.agora is not None:
                self._go_to(b, u, b.agora)
                return
            foes = [f for f in inside if self._same_side(b, u, f) and dist(f.pos, u.pos) <= config.AI_SORTIE_RANGE]
            foe = self.pick_target(b, u, foes)
            if foe is not None:
                self._attack(b, u, foe)
            return
        if inside and not b.on_wall(u):
            if self._skirmish(b, u, [f for f in inside if self._same_side(b, u, f)]):
                return
        foes = b.units(Side.STADT, fighting_only=True)
        if threats:
            focus = min(threats, key=lambda p: dist(p, u.pos))
        elif foes:
            cx = sum(f.x for f in foes) / len(foes)
            cy = sum(f.y for f in foes) / len(foes)
            focus = (cx, cy)
        else:
            return
        # auf den Wehrgang über dem Angriffspunkt, etwas seitlich, nie auf ein Tor
        cells = [c for c in b.blocked if c not in b.crossings]
        if not cells:
            return
        k = (u.id % 3) - 1
        ranked = sorted(cells, key=lambda c: dist((c[0] + 0.5, c[1] + 0.5), focus))
        pick = ranked[min(len(ranked) - 1, 2 + abs(k) * 2)]
        spot = (pick[0] + 0.5, pick[1] + 0.5)
        if not b.on_wall(u) or dist(u.pos, spot) > 1.2:
            self._go_to(b, u, spot, eps=0.3)

    def _garrison_cavalry(self, b: "Battle", u: Lochos, inside: list[Lochos]) -> None:
        cands = [f for f in inside if self._same_side(b, u, f) and (not formed(f) or b.arc_of(f, u.pos) != "front")]
        foe = self.pick_target(b, u, cands)
        if foe is not None:
            self._engage(b, u, foe)
            return
        if b.agora is not None and dist(u.pos, b.agora) > 2.5:
            self._go_to(b, u, b.agora, eps=1.5)
