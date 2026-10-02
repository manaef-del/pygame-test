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
from .ai import Brain, formed
from .geometry import dist, norm, sub
from .units import Lochos, Side, Stance

if TYPE_CHECKING:
    from .battle import Battle, Gate

Point = tuple[float, float]

FORT_PLANS = {
    "aufmarsch": "Aufmarsch",
    "rammen": "Tor rammen",
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
        self.wall_cell: tuple[int, int] | None = None
        self.gate_guard: dict[int, int] = {}          # Verteidigung: Gruppe -> Tor
        self.announced: set[str] = set()

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

    def _choose_wall_cell(self, b: "Battle", gate: "Gate | None") -> tuple[int, int] | None:
        """Ein Wallstück für den Turm: außen frei zugänglich, fern vom gewählten Tor, von
        Türmen und Toren, wo wenige Verteidiger stehen, dem Heer nicht zu fern."""
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
                 - (min(dist(p, gate.center), 10.0) if gate is not None else 0.0))
            if s < best_s:
                best, best_s = c, s
        return best

    def _assign_siege_roles(self, b: "Battle", own: list[Lochos]) -> None:
        hop = [u for u in own if self._arm(u) == "hopliten" and u.id not in self.roles]
        for u in own:
            if u.id in self.roles:
                continue
            arm = self._arm(u)
            if arm == "peltasten":
                self.roles[u.id] = "werfer"
            elif arm == "reiter":
                self.roles[u.id] = "reiter"
        taken = set(self.roles.values())
        gate = b.gates[self.main_gate] if self.main_gate is not None else None
        hop.sort(key=lambda u: dist(u.pos, gate.center) if gate is not None else 0.0)
        for u in hop:
            if "ram" not in taken and gate is not None:
                self.roles[u.id] = "ram"
            elif "turm" not in taken and len(hop) >= 2 and b.blocked:
                self.roles[u.id] = "turm"
            else:
                self.roles[u.id] = "sturm"
            taken.add(self.roles[u.id])

    def _stage(self, b: "Battle", u: Lochos, gate: "Gate", distance: float, spread: float) -> Point:
        cx, cy = gate.center
        (nx, ny), (tx, ty) = gate.normal, gate.tangent
        return b._free_spot((cx + nx * distance + tx * spread, cy + ny * distance + ty * spread), u)

    def _siege(self, b: "Battle") -> None:
        r = self.report
        own = b.units(Side.FEIND, fighting_only=True)
        if not own:
            return
        if self.main_gate is None or not b.gates[self.main_gate].closed and self.plan == "aufmarsch":
            self.main_gate = self._choose_gate(b, own)
        gate = b.gates[self.main_gate] if self.main_gate is not None else (b.gates[0] if b.gates else None)
        self._assign_siege_roles(b, own)
        breach = any(not g.closed for g in b.gates) or bool(b.crossings)
        if breach:
            self._set_plan(b, "sturm")
        elif any(u.engine == "ram" for u in own):
            self._set_plan(b, "rammen")
        else:
            self._set_plan(b, "aufmarsch")
        if self.wall_cell is None or self.wall_cell in b.crossings and not breach:
            self.wall_cell = self._choose_wall_cell(b, gate)
        k_stage = 0
        for u in own:
            if self._retreating(b, u) or self._busy(b, u):
                continue
            role = self.roles.get(u.id, "sturm")
            if role == "ram" and gate is not None and gate.closed:
                self._ram_work(b, u, gate)
                continue
            gates_open = any(not g.closed for g in b.gates)
            if role == "turm" and gates_open and u.engine is not None:
                u.engine = None                           # das Tor ist offen: der Turm wird nicht mehr gebraucht
                u.tower_cell = None
            if role == "turm" and self.wall_cell is not None and self.wall_cell not in b.crossings and not (
                    breach and u.engine is None and u.building is None) and not gates_open:
                self._tower_work(b, u)
                continue
            if breach:
                self._storm(b, u, r)
                continue
            # vor dem Durchbruch: Ausfälle abwehren, sonst warten und werfen
            near = [f for f in r.foes if f.rect_distance(u.pos) <= config.ENGAGE_RANGE + 1.0 and self._same_side(b, u, f)]
            foe = self.pick_target(b, u, near)
            if foe is not None:
                self._attack(b, u, foe)
                continue
            if gate is None:
                continue
            if role == "werfer" and u.ammo() > 0:
                spread = ((k_stage % 3) - 1) * 2.4
                self._go_to(b, u, self._stage(b, u, gate, gate.half_thick + HARASS_DISTANCE, spread))
            else:
                spread = ((k_stage % 5) - 2) * 2.6
                self._go_to(b, u, self._stage(b, u, gate, STAGE_DISTANCE + 1.6 * (k_stage // 5), spread))
            k_stage += 1

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

    def _storm(self, b: "Battle", u: Lochos, r) -> None:
        """Nach dem Durchbruch: auf erreichbare Verteidiger, sonst an die Häuser. Wer
        draußen steht und kein Tor offen hat, steigt über den Turm."""
        if u.engine is not None and u.building is None:
            u.engine = None                                   # das Gerät wird nicht mehr gebraucht
        if u.building is not None:
            b._wake(u)
        gates_open = any(not g.closed for g in b.gates)
        outside = b._wall_level(u.pos) == "aussen" and not b.up(u)
        if outside and not gates_open and b.crossings:
            if self._via_crossing(b, u):
                return
        foes = [f for f in r.foes if self._same_side(b, u, f)]
        if self._skirmish(b, u, foes):
            return
        if u.stance is Stance.PLAENKELN:
            u.stance = Stance.HALTEN
            u.target = None
        foe = self.pick_target(b, u, [f for f in foes if f.rect_distance(u.pos) <= 8.0])
        if foe is not None:
            self._engage(b, u, foe)
            return
        houses = [h for h in b.houses if not h.looted]
        if houses:
            u.stance = Stance.RAUB
            u.target_id = None
            u.in_line = False
            u.target = min(houses, key=lambda h: dist(u.pos, h.center)).center
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
            # Reserve: an die nächste Bedrohung, an einem Turm vor den Fuß der Leiter dort
            t = min(threats, key=lambda p: dist(p, u.pos))
            g = b.gate_near(t, 0.6)
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
