"""Kopflose Schlachten mit gescripteten Spielertaktiken gegen die Gegner-KI.

    python3 tools/simulate.py                 # alle Szenarien, beide KIs, 5 Seeds
    python3 tools/simulate.py --seeds 20 --ai klug --scenario palisade --tactic tor_halten
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

def t_linie(b: Battle) -> dict:
    """Verteidigung offen: Phalanx quer, Peltasten dahinter, Reiter in Reserve."""
    hop, pelt, cav = groups(b)
    return {
        0: lambda b: (b.command_line(hop, (4.0, 10.5), (12.0, 10.5)),
                      b.command_line(pelt, (5.0, 11.6), (11.0, 11.6)),
                      b.command_move(cav, (13.5, 12.5))),
    }


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
    plan[0] = lambda b: (b.command_line(hop, (6.5, 10.5), (9.5, 10.5)),
                         b.command_line(pelt, (6.5, 11.4), (9.5, 11.4)),
                         b.command_move(cav, (12.0, 11.5)))
    return plan


def t_passiv(b: Battle) -> dict:
    return {0: lambda b: b.command_hold(None)}


def t_angriff(b: Battle) -> dict:
    return {0: lambda b: b.command_attack(None)}


def t_tor_halten(b: Battle) -> dict:
    """Verteidigung Palisade: Peltasten auf den Wall, Hopliten hinters Tor."""
    hop, pelt, cav = groups(b)
    return {
        0: lambda b: (b.command_line(hop, (5.5, 9.6), (10.5, 9.6)),
                      b.command_move(pelt, (3.5, 8.5)),
                      b.command_move(cav, (13.0, 12.5))),
    }


def t_tor_halten_reserve(b: Battle) -> dict:
    """Wie Tor halten, die Reiter jagen alle 15 s eingedrungene Gruppen."""
    plan = t_tor_halten(b)
    hop, pelt, cav = groups(b)

    def hunt(b: Battle):
        if not cav or b.gate is None:
            return
        inside = [f for f in b.units(Side.FEIND, fighting_only=True) if f.y > b.gate.center[1] + 0.5 and not b.on_wall(f)]
        if inside:
            b.command_attack_target(cav, min(inside, key=lambda f: f.men))
    for t in range(20, 240, 15):
        plan[t] = hunt
    return plan


def t_tor_leiter(b: Battle) -> dict:
    """Wie Tor halten, aber sobald ein Turm steht, stellt sich die Phalanx an den Fuß
    der nächsten Leiter (Front zum Wall); die Reiter jagen, was trotzdem durchkommt."""
    plan = t_tor_halten(b)
    hop, pelt, cav = groups(b)
    state = {"covered": False}

    def react(b: Battle):
        if b.crossings and not state["covered"] and hop and hop[0].fighting:
            cx = next(iter(b.crossings))[0] + 0.5
            lx, ly = min(b.ladders, key=lambda c: abs(c[0] + 0.5 - cx))
            b.command_line(hop, (lx + 0.5 - 2.2, ly + 1.7), (lx + 0.5 + 2.2, ly + 1.7))
            state["covered"] = True
        if not cav or not cav[0].fighting or b.gate is None:
            return
        line = hop[0] if hop else None
        inside = [f for f in b.units(Side.FEIND, fighting_only=True) if f.y > b.gate.center[1] + 0.5 and not b.on_wall(f)
                  and (line is None or line.rect_distance(f.pos) > 1.5)]
        if inside:
            b.command_attack_target(cav, min(inside, key=lambda f: f.rect_distance(cav[0].pos)))
    for t in range(5, 240, 5):
        plan[t] = react
    return plan


def t_vorruecken(b: Battle) -> dict:
    """Angriff: Linie bilden, vorrücken, dann Angriff."""
    hop, pelt, cav = groups(b)
    return {
        0: lambda b: (b.command_line(hop, (4.0, 12.0), (12.0, 12.0)),
                      b.command_line(pelt, (5.0, 13.0), (11.0, 13.0)),
                      b.command_move(cav, (13.5, 13.5))),
        20: lambda b: (b.command_line(hop, (4.0, 8.5), (12.0, 8.5)),
                       b.command_line(pelt, (5.0, 9.6), (11.0, 9.6))),
        45: lambda b: b.command_attack(None),
    }


def t_belagerung(b: Battle) -> dict:
    """Angriff Wall: Hopliten bauen den Rammbock, Reiter den Turm."""
    hop, pelt, cav = groups(b)
    return {
        0: lambda b: (b.command_build(hop, "ram"), b.command_build(cav, "tower"),
                      b.command_move(pelt, (8.0, 13.0))),
        config.RAM_BUILD_TIME + 2: lambda b: b.command_ram_gate(hop),
        config.TOWER_BUILD_TIME + 2: lambda b: b.command_tower_wall(cav, (13, 7)),
        40: lambda b: b.command_attack(None),
    }


def t_phalanxstoss(b: Battle) -> dict:
    """Angriff offen: in Formation bis vor die feindliche Linie, dann Phalanx gegen Phalanx."""
    hop, pelt, cav = groups(b)
    foe_y = min((u.y for u in b.units(Side.FEIND)), default=5.0) + 0.5
    return {
        0: lambda b: (b.command_line(hop, (4.0, 12.0), (12.0, 12.0)),
                      b.command_line(pelt, (5.0, 13.0), (11.0, 13.0)),
                      b.command_move(cav, (13.5, 13.5))),
        20: lambda b: (b.command_line(hop, (4.5, foe_y + 1.4), (11.5, foe_y + 1.4)),
                       b.command_line(pelt, (5.0, foe_y + 2.5), (11.0, foe_y + 2.5))),
        60: lambda b: b.command_attack(cav),
    }


def t_tor_phalanx(b: Battle) -> dict:
    """Angriff Wall: Rammbock ans Tor, danach in Formation durchs Tor, Peltasten hinterher."""
    hop, pelt, cav = groups(b)
    plan = {
        0: lambda b: (b.command_build(hop, "ram"), b.command_move(pelt, (8.0, 11.0)), b.command_move(cav, (8.0, 12.5))),
        config.RAM_BUILD_TIME + 2: lambda b: b.command_ram_gate(hop),
    }

    done = []

    def through(b: Battle):
        if b.gate is not None and not b.gate.closed and not done:
            done.append(True)
            gx, gy = b.gate.center
            b.command_line(hop, (gx - 2.5, gy - 1.6), (gx + 2.5, gy - 1.6))
            b.command_line(pelt, (gx - 1.5, gy - 0.6), (gx + 1.5, gy - 0.6))
    for t in range(12, 90, 2):
        plan[t] = through
    plan[120] = lambda b: b.command_attack(None)
    return plan


TACTICS = {
    "offen": {"linie": t_linie, "linie_reiter": t_linie_reiter_aktiv, "linie_aktiv": t_linie_aktiv, "linie_tief": t_linie_tief, "passiv": t_passiv, "angriff": t_angriff},
    "palisade": {"tor_halten": t_tor_halten, "tor_reserve": t_tor_halten_reserve, "tor_leiter": t_tor_leiter, "passiv": t_passiv},
    "horde": {"vorruecken": t_vorruecken, "angriff": t_angriff},
    "angriff_offen": {"phalanxstoss": t_phalanxstoss, "vorruecken": t_vorruecken, "angriff": t_angriff},
    "angriff_wall": {"tor_phalanx": t_tor_phalanx, "belagerung": t_belagerung},
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
        pairs = [("angriff_offen", "phalanxstoss"), ("angriff_wall", "tor_phalanx")]
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
        scn = next(s for s in SCENARIOS if s.key == (args.scenario or "offen"))
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
