"""Kopflose Schlachten mit gescripteten Spielertaktiken gegen die Gegner-KI.

    python3 tools/simulate.py                 # alle Szenarien, beide KIs, 5 Seeds
    python3 tools/simulate.py --seeds 20 --ai klug --scenario siedlung --tactic linie_aktiv
    python3 tools/simulate.py --lernen 8      # dieselbe Taktik achtmal mit Gedächtnis

Jede Taktik ist eine kleine Funktion, die zu festen Zeitpunkten Befehle gibt,
so wie ein Spieler es tun würde. Ausgabe: Ausgang, Verluste, Dauer, gewählte
Pläne; als Tabelle (Markdown) auf die Konsole.
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game import config                                       # noqa: E402
from game.ai import Memory                                    # noqa: E402
from game.army import Army, GroupSpec, Tier, default_army     # noqa: E402
from game.battle import Battle                                # noqa: E402
from game.scenarios import SCENARIOS                          # noqa: E402
from game.geometry import dist                                # noqa: E402
from game.units import Side, Stance                           # noqa: E402

DT = 1 / 30
LIMIT = 300.0


def groups(b: Battle):
    hop = [u for u in b.units(Side.STADT) if u.share(lambda m: m.kind.hoplite) >= 0.5]
    pelt = [u for u in b.units(Side.STADT) if u.share(lambda m: m.kind.ranged) >= 0.5]
    cav = [u for u in b.units(Side.STADT) if u.share(lambda m: m.kind.cavalry) >= 0.5]
    return hop, pelt, cav


# ------------------------------------------------------------ Truppenmischungen
ARMIES = {
    "standard": lambda: default_army(),                                  # 40 Hopliten, 15 Peltasten, 20 Reiter
    "ohne_reiter": lambda: Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 14), Tier("mittel", 14), Tier("leicht", 12)]),
        GroupSpec("Hopliten II", [Tier("mittel", 10), Tier("leicht", 10)]),
        GroupSpec("Peltasten", [Tier("peltast", 15)]),
    ]),
    "gemischt": lambda: Army(groups=[                                    # eine große gemischte Gruppe
        GroupSpec("Alle", [Tier("schwer", 14), Tier("mittel", 14), Tier("leicht", 12), Tier("peltast", 15), Tier("reiter", 20)]),
    ]),
    "reiterlastig": lambda: Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 14), Tier("mittel", 11)]),
        GroupSpec("Peltasten", [Tier("peltast", 15)]),
        GroupSpec("Reiter", [Tier("reiter", 20)]),
        GroupSpec("Reiter II", [Tier("reiter", 15)]),
    ]),
    "peltastenlastig": lambda: Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 10), Tier("mittel", 10)]),
        GroupSpec("Peltasten", [Tier("peltast", 20)]),
        GroupSpec("Peltasten II", [Tier("peltast", 15)]),
        GroupSpec("Reiter", [Tier("reiter", 20)]),
    ]),
    "zwei_phalangen": lambda: Army(groups=[
        GroupSpec("Phalanx W", [Tier("schwer", 14), Tier("mittel", 8), Tier("leicht", 6)]),
        GroupSpec("Phalanx O", [Tier("mittel", 6), Tier("leicht", 6), Tier("peltast", 15)]),
        GroupSpec("Reiter", [Tier("reiter", 20)]),
    ]),
}


# ---------------------------------------------------------------- Taktiken
# Jede Taktik: dict Zeitpunkt -> Funktion(battle). Zeit 0 = erster Befehl.

def _at(b: Battle, dx: float, dy: float) -> tuple[float, float]:
    """Kartenstelle relativ zur Mitte der Karte (x) und zur eigenen Aufstellung (y)."""
    return (b.cols / 2 + dx, b.scenario.deploy_y + dy)


def t_linie(b: Battle) -> dict:
    """Verteidigung offen: Phalanx quer, Peltasten dahinter, Reiter in Reserve."""
    hop, pelt, cav = groups(b)
    return {
        0: lambda b: (b.command_line(hop, _at(b, -4.0, 0.0), _at(b, 4.0, 0.0)),
                      b.command_line(pelt, _at(b, -3.0, 1.1), _at(b, 3.0, 1.1)),
                      b.command_move(cav, _at(b, 5.5, 2.0))),
    }


def t_schlachtordnung(b: Battle) -> dict:
    """Wie Linie, aber mit einem Zug für alle: Peltasten dahinter, Reiter am rechten Flügel."""
    return {0: lambda b: b.command_line(None, _at(b, -4.0, 0.0), _at(b, 4.0, 0.0))}


def t_linie_reiter_aktiv(b: Battle) -> dict:
    """Wie Linie, aber die Reiter greifen alle 15 s das nächste ungedeckte Ziel an."""
    hop, pelt, cav = groups(b)
    plan = t_linie(b)

    def charge(b: Battle):
        foes = b.units(Side.FEIND, fighting_only=True)
        if not foes or not cav:
            return
        me = cav[0]
        weak = min(foes, key=lambda f: (0 if f.stance is Stance.FLUCHT else 1, f.men, f.rect_distance(me.pos)))
        b.command_attack_target(cav, weak)

    for t in range(15, 200, 15):
        plan[t] = charge
    return plan


def t_linie_aktiv(b: Battle) -> dict:
    """Linie mit Flankenschutz: alle vier Sekunden schaut der Spieler hin. Die Reiter
    greifen die Gruppe an, die der Phalanx in Flanke oder Rücken geht, die Phalanx
    dreht die Front zur stärksten Bedrohung, wenn vorn niemand mehr steht."""
    from game.geometry import arc as arc_of, norm, sub
    hop, pelt, cav = groups(b)
    plan = t_linie(b)

    def react(b: Battle):
        foes = b.units(Side.FEIND, fighting_only=True)
        if not foes:
            return
        for line in hop:
            if not line.fighting:
                continue
            near = [f for f in foes if line.rect_distance(f.pos) <= 3.0]
            side = [f for f in near if arc_of(line.facing, sub(f.pos, line.pos), config.FRONT_ARC, config.REAR_ARC) != "front"]
            front = [f for f in near if f not in side]
            if side and cav and cav[0].fighting:
                b.command_attack_target(cav, min(side, key=lambda f: line.rect_distance(f.pos)))
            elif side and not front and line.in_phalanx:
                threat = max(side, key=lambda f: f.men)
                line.facing = norm(sub(threat.pos, line.pos))      # Front drehen (wie eine neue Linie)
        if cav and cav[0].fighting and cav[0].stance is not Stance.ANGRIFF:
            weak = [f for f in foes if f.stance is Stance.FLUCHT or f.loose]
            if weak:
                b.command_attack_target(cav, min(weak, key=lambda f: f.rect_distance(cav[0].pos)))
    for t in range(4, 240, 4):
        plan[t] = react
    return plan


def t_linie_tief(b: Battle) -> dict:
    """Kurze, tiefe Linie (drei Kacheln, zwei bis drei Glieder) statt einer breiten
    Einer-Reihe, Peltasten dahinter, Reiter als Flankenschutz wie bei linie_aktiv."""
    hop, pelt, cav = groups(b)
    plan = t_linie_aktiv(b)
    plan[0] = lambda b: (b.command_line(hop, _at(b, -1.5, 0.0), _at(b, 1.5, 0.0)),
                         b.command_line(pelt, _at(b, -1.5, 0.9), _at(b, 1.5, 0.9)),
                         b.command_move(cav, _at(b, 4.0, 1.0)))
    return plan


def t_passiv(b: Battle) -> dict:
    return {0: lambda b: b.command_hold(None)}


def t_angriff(b: Battle) -> dict:
    return {0: lambda b: b.command_attack(None)}


def t_vorruecken(b: Battle) -> dict:
    """Angriff: Linie bilden, vorrücken, dann Angriff."""
    hop, pelt, cav = groups(b)
    return {
        0: lambda b: (b.command_line(hop, _at(b, -4.0, -3.5), _at(b, 4.0, -3.5)),
                      b.command_line(pelt, _at(b, -3.0, -2.5), _at(b, 3.0, -2.5)),
                      b.command_move(cav, _at(b, 5.5, -2.0))),
        20: lambda b: (b.command_line(hop, _at(b, -4.0, -7.0), _at(b, 4.0, -7.0)),
                       b.command_line(pelt, _at(b, -3.0, -5.9), _at(b, 3.0, -5.9))),
        45: lambda b: b.command_attack(None),
    }


def t_phalanxstoss(b: Battle) -> dict:
    """Angriff offen: in Formation bis vor die feindliche Linie, dann Phalanx gegen Phalanx."""
    hop, pelt, cav = groups(b)
    foe_y = min((u.y for u in b.units(Side.FEIND)), default=5.0) + 0.5
    cx = b.cols / 2
    return {
        0: lambda b: (b.command_line(hop, _at(b, -4.0, -3.5), _at(b, 4.0, -3.5)),
                      b.command_line(pelt, _at(b, -3.0, -2.5), _at(b, 3.0, -2.5)),
                      b.command_move(cav, _at(b, 5.5, -2.0))),
        20: lambda b: (b.command_line(hop, (cx - 3.5, foe_y + 1.4), (cx + 3.5, foe_y + 1.4)),
                       b.command_line(pelt, (cx - 3.0, foe_y + 2.5), (cx + 3.0, foe_y + 2.5))),
        60: lambda b: b.command_attack(cav),
        **{t: _finish_off for t in range(70, 290, 10)},
    }


def _finish_off(b: Battle) -> None:
    """Steht keine feindliche Phalanx mehr, greifen alle an: Wer sich auf der Agora
    zum letzten Kampf stellt, wird nicht von den Reitern allein bezwungen."""
    foes = b.units(Side.FEIND, fighting_only=True)
    if foes and not any(f.in_phalanx and f.men >= 20 for f in foes):
        b.command_attack([u for u in b.units(Side.STADT, fighting_only=True) if u.stance is not Stance.ANGRIFF])


# ---------------------------------------------------------------- Festung
def _behind(b: Battle, g, depth: float = 2.2) -> tuple[tuple[float, float], tuple[float, float]]:
    """Linie hinter (innen) oder vor (außen, depth < 0) einem Tor, quer zum Durchgang."""
    cx, cy = g.center
    (nx, ny), (tx, ty) = g.normal, g.tangent
    side = -1.0 if depth > 0 else 1.0
    d = abs(depth) + g.half_thick
    mx, my = cx + nx * side * d, cy + ny * side * d
    a, c = (mx - tx * 2.4, my - ty * 2.4), (mx + tx * 2.4, my + ty * 2.4)
    # die Front soll vom Inneren zum Tor schauen: command_line nimmt die Front links der Linie
    fx, fy = c[1] - a[1], -(c[0] - a[0])
    if fx * nx + fy * ny < 0:
        a, c = c, a
    return a, c


def _threatened_gate(b: Battle):
    foes = b.units(Side.FEIND, fighting_only=True)
    rams = [f for f in foes if f.engine == "ram" or f.build_kind == "ram"]
    open_ = [g for g in b.gates if not g.closed]
    if open_:
        return min(open_, key=lambda g: min((dist(f.pos, g.center) for f in foes), default=99.0))
    if rams:
        return min(b.gates, key=lambda g: min(dist(f.pos, g.center) for f in rams))
    return min(b.gates, key=lambda g: min((dist(f.pos, g.center) for f in foes), default=99.0))


def t_festung_tore(b: Battle) -> dict:
    """Festung: die Phalanx hinter das bedrohte Tor, Peltasten auf den Wehrgang darüber,
    Reiter auf der Agora, die Eingedrungene jagen. Alle fünf Sekunden schaut der Spieler hin."""
    hop, pelt, cav = groups(b)
    state = {"gate": None}

    def react(b: Battle):
        g = _threatened_gate(b)
        if g is not state["gate"]:
            state["gate"] = g
            a, c = _behind(b, g)
            if hop and hop[0].fighting:
                b.command_line(hop, a, c)
            wall = [x for x in b.blocked if x not in b.crossings]
            spot = min(wall, key=lambda x: dist((x[0] + 0.5, x[1] + 0.5), g.center) + (0.0 if dist((x[0] + 0.5, x[1] + 0.5), g.center) >= 2.0 else 9.0))
            if pelt and pelt[0].fighting and pelt[0].ammo() > 0:
                b.command_move(pelt, (spot[0] + 0.5, spot[1] + 0.5))
        inside = [f for f in b.units(Side.FEIND, fighting_only=True) if b._wall_level(f.pos) == "innen" and not f.in_phalanx]
        if cav and cav[0].fighting and cav[0].stance is not Stance.ANGRIFF:
            if inside:
                b.command_attack_target(cav, min(inside, key=lambda f: f.men))
            elif dist(cav[0].pos, b.agora) > 2.0 and cav[0].target is None:
                b.command_move(cav, b.agora)
    plan = {0: lambda b: b.command_move(cav, b.agora)}
    for t in range(0, 290, 5):
        plan[t + 0.5] = react
    return plan


def t_festung_angriff_ram(b: Battle) -> dict:
    """Festung angreifen: die Hopliten bauen den Rammbock und rammen das nächste Tor, die
    Peltasten werfen auf den Wehrgang daneben, die Reiter warten; offen: alle hinein."""
    hop, pelt, cav = groups(b)
    me = (b.cols / 2, b.scenario.deploy_y)
    gate = min(b.gates, key=lambda g: dist(g.center, me))
    gx, gy = gate.center
    nx, ny = gate.normal
    stand = (gx + nx * 3.2, gy + ny * 3.2)
    wait = (gx + nx * 8.0, gy + ny * 8.0)
    plan = {
        0: lambda b: (b.command_build(hop, "ram"), b.command_move(pelt, stand), b.command_move(cav, wait)),
        config.RAM_BUILD_TIME + 1: lambda b: b.command_ram_gate(hop, gate),
    }

    def storm(b: Battle):
        if any(not g.closed for g in b.gates):
            b.command_attack([u for u in b.units(Side.STADT, fighting_only=True) if u.stance is not Stance.ANGRIFF])
    for t in range(15, 290, 5):
        plan[t] = storm
    return plan


def t_festung_angriff_turm(b: Battle) -> dict:
    """Festung angreifen über den Turm: Die Hopliten bauen ihn und setzen ihn an die
    Südkante, die Peltasten werfen dort auf den Wehrgang; steht der Turm, steigen
    Hopliten und Peltasten hinüber, sammeln sich drinnen und greifen an. Die Reiter
    warten draußen, bis ein Tor offen ist."""
    hop, pelt, cav = groups(b)
    south = max(x[1] for x in b.blocked)
    cells = [c for c in b.blocked if c[1] == south and b.tower_step(c) is not None and c not in b.ladders]
    wall = min(cells, key=lambda c: abs(c[0] + 0.5 - b.cols / 2)) if cells else None
    stand = (b.cols / 2, south + 3.2)
    state = {"over": False}
    plan = {
        0: lambda b: (b.command_build(hop, "tower"), b.command_move(pelt, stand), b.command_move(cav, (b.cols / 2, south + 8.0))),
        config.TOWER_BUILD_TIME + 1: lambda b: b.command_tower_wall(hop, wall) if wall else None,
    }

    def climb(b: Battle):
        foot = [u for u in hop + pelt if u.fighting]
        if b.crossings and not state["over"]:
            state["over"] = True
            b.command_move(foot, (b.cols / 2, b.rows / 2 + 3.0))
        elif state["over"] and all(b._wall_level(u.pos) == "innen" and not u.loose for u in foot):
            b.command_attack(foot)
        riders = [u for u in cav if u.fighting]
        if any(not g.closed for g in b.gates):
            b.command_attack([u for u in riders if u.stance is not Stance.ANGRIFF and u.engine is None])
        elif riders and not any(u.fighting for u in hop + pelt):
            # die Fußtruppen sind geschlagen: die Reiter sitzen ab und rammen selbst ein Tor
            r = riders[0]
            if r.engine is None and r.building is None:
                b.command_build(riders, "ram")
            elif r.engine == "ram" and r.target is None:
                b.command_ram_gate(riders, min(b.gates, key=lambda g: dist(g.center, r.pos)))
    for t in range(20, 290, 5):
        plan[t] = climb
    return plan


TACTICS = {
    "siedlung": {"linie": t_linie, "schlachtordnung": t_schlachtordnung, "linie_reiter": t_linie_reiter_aktiv, "linie_aktiv": t_linie_aktiv, "linie_tief": t_linie_tief, "passiv": t_passiv, "angriff": t_angriff},
    "siedlung_angriff": {"phalanxstoss": t_phalanxstoss, "vorruecken": t_vorruecken, "angriff": t_angriff},
    "horde": {"vorruecken": t_vorruecken, "angriff": t_angriff},
    "festung": {"tore": t_festung_tore, "passiv": t_passiv},
    "festung_angriff": {"rammbock": t_festung_angriff_ram, "turm": t_festung_angriff_turm},
}


# ----------------------------------------------------------------- Laufen
def _guard_empty_selection(b: Battle) -> None:
    """Eine leere Auswahl bedeutet in Battle „alle“; im Skript soll sie „niemand“ heißen."""
    for name in ("command_move", "command_line", "command_attack_target", "command_build",
                 "command_ram_gate", "command_tower_wall", "command_attack", "command_hold"):
        orig = getattr(b, name)

        def wrapped(units, *args, _orig=orig):
            if units is not None and len(units) == 0:
                return 0
            return _orig(units, *args)
        setattr(b, name, wrapped)


def play(scenario, tactic, seed: int, ai: str, memory: Memory | None = None, enemy_count=None, army: str = "standard",
         doctrine: str | None = None) -> dict:
    b = Battle(scenario, random.Random(seed), ai=ai, memory=memory, enemy_count=enemy_count, army=ARMIES[army](),
               doctrine=doctrine)
    _guard_empty_selection(b)
    schedule = TACTICS[scenario.key][tactic](b)
    steps = int(LIMIT / DT)
    plans: list[str] = []
    for i in range(steps):
        t = i * DT
        for at, fn in list(schedule.items()):
            if t >= at:
                fn(b)
                del schedule[at]
        b.update(DT)
        name = getattr(b.brain, "plan", None)
        if name and (not plans or plans[-1] != name):
            plans.append(name)
        if b.outcome:
            break
    r = b.report()
    r["plaene"] = plans
    r["szenario"] = scenario.key
    r["taktik"] = tactic
    r["ki"] = ai
    r["seed"] = seed
    return r


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    wins = sum(1 for r in rows if r["ausgang"] == "sieg")
    return {
        "n": n,
        "siege": wins,
        "verlust_stadt": sum(r["stadt_gefallen"] / max(1, r["stadt_start"]) for r in rows) / n,
        "verlust_feind": sum(r["feind_gefallen"] / max(1, r["feind_start"]) for r in rows) / n,
        "haeuser": sum((r["haeuser"] - r["haeuser_intakt"]) for r in rows) / n,
        "zeit": sum(r["zeit"] for r in rows) / n,
        "plaene": Counter(p for r in rows for p in dict.fromkeys(r["plaene"])),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--ai", choices=["klug", "einfach", "beide"], default="beide")
    ap.add_argument("--scenario", default=None)
    ap.add_argument("--tactic", default=None)
    ap.add_argument("--lernen", type=int, default=0, help="dieselbe Taktik n-mal mit Gedächtnis")
    ap.add_argument("--enemy", type=int, default=None, help="Gegnerstärke statt Vorgabe des Szenarios")
    ap.add_argument("--army", default="standard", choices=sorted(ARMIES), help="eigene Truppenmischung")
    ap.add_argument("--doctrine", default=None, help="Aufstellung der Siedlung erzwingen (siehe game/doctrine.py)")
    ap.add_argument("--matrix", action="store_true", help="Spieleraufstellung × Gegneraufstellung gegen die Siedlung")
    args = ap.parse_args()

    ais = ["einfach", "klug"] if args.ai == "beide" else [args.ai]
    started = time.time()
    if args.matrix:
        from game.doctrine import DOCTRINES
        pairs = [("siedlung_angriff", "phalanxstoss"), ("festung_angriff", "rammbock")]
        print("| Spieler | Szenario | Gegner | Siege Spieler | Verlust Spieler | Verlust Siedlung | Dauer |")
        print("|---|---|---|---|---|---|---|")
        for army in ARMIES:
            if args.army != "standard" and army != args.army:
                continue
            for key, tactic in pairs:
                scn = next(s for s in SCENARIOS if s.key == key)
                for doctrine in DOCTRINES:
                    rows = [play(scn, tactic, seed, "klug", army=army, doctrine=doctrine) for seed in range(args.seeds)]
                    s = summarize(rows)
                    print(f"| {army} | {key} | {doctrine} | {s['siege']}/{s['n']} | {s['verlust_stadt']:.0%} | "
                          f"{s['verlust_feind']:.0%} | {s['zeit']:.0f} s |", flush=True)
        print(f"\n{time.time() - started:.0f} s Rechenzeit", file=sys.stderr)
        return
    if args.lernen:
        scn = next(s for s in SCENARIOS if s.key == (args.scenario or "siedlung"))
        tactic = args.tactic or next(iter(TACTICS[scn.key]))
        mem = Memory()
        print(f"## Lernen: {scn.key} / {tactic}, {args.lernen} Schlachten hintereinander\n")
        print("| Nr | Ausgang | Stadt gefallen | Feind gefallen | Häuser verloren | Pläne | Gewichte |")
        print("|---|---|---|---|---|---|---|")
        for i in range(args.lernen):
            r = play(scn, tactic, 100 + i, "klug", mem)
            w = {p: round(mem.weight(scn.key, p), 2) for p in mem.gains.get(scn.key, {})}
            print(f"| {i + 1} | {r['ausgang']} | {r['stadt_gefallen']}/{r['stadt_start']} | {r['feind_gefallen']}/{r['feind_start']} "
                  f"| {r['haeuser'] - r['haeuser_intakt']} | {' → '.join(r['plaene'])} | {w} |")
        return

    print(f"Truppe: {args.army}" + (f", Gegner: {args.enemy}" if args.enemy else ""))
    print("| Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |")
    print("|---|---|---|---|---|---|---|---|---|")
    for scn in SCENARIOS:
        if args.scenario and scn.key != args.scenario:
            continue
        for tactic in TACTICS[scn.key]:
            if args.tactic and tactic != args.tactic:
                continue
            for ai in ais:
                rows = [play(scn, tactic, seed, ai, enemy_count=args.enemy, army=args.army, doctrine=args.doctrine) for seed in range(args.seeds)]
                s = summarize(rows)
                plans = ", ".join(f"{p}×{c}" for p, c in s["plaene"].most_common()) if ai == "klug" else "–"
                print(f"| {scn.key} | {tactic} | {ai} | {s['siege']}/{s['n']} | {s['verlust_stadt']:.0%} | "
                      f"{s['verlust_feind']:.0%} | {s['haeuser']:.1f} | {s['zeit']:.0f} s | {plans} |", flush=True)
    print(f"\n{time.time() - started:.0f} s Rechenzeit", file=sys.stderr)


if __name__ == "__main__":
    main()
