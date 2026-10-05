"""Tests der Gegner-KI: Lagebericht, Pläne, Gedächtnis. Läuft ohne Pygame."""

import random

from game import config
from game.ai import Brain, Memory, PLAN_NAMES, formed, rear_route
from game.army import Army, GroupSpec, Tier
from game.battle import Battle
from game.scenarios import RaiderSpawn, Scenario
from kleine_karten import KLEIN_ANGRIFF, KLEIN_HORDE, KLEIN_OFFEN
from game.units import UNIT_TYPES, Lochos, Man, Side, Stance

DT = 1 / 30


def run(b: Battle, seconds: float) -> None:
    for _ in range(int(seconds / DT)):
        b.update(DT)
        if b.outcome:
            break


def men(kind: str, n: int) -> list[Man]:
    return [Man(UNIT_TYPES[kind]) for _ in range(n)]


def raid(n: int, *spawns, houses=((2, 17),)) -> Scenario:
    return Scenario(
        "t", "t", "", role="verteidigung", enemy_kind="raeuber",
        enemy_default=n, enemy_min=n, enemy_max=n, houses=houses,
        raider_spawns=tuple(RaiderSpawn(x, y) for x, y in spawns),
    )


def line_army() -> Army:
    return Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 14), Tier("mittel", 14)]),
        GroupSpec("Peltasten", [Tier("peltast", 12)]),
        GroupSpec("Reiter", [Tier("reiter", 10)]),
    ])


# ------------------------------------------------------------ Lagebericht
def test_report_sees_the_phalanx_front_and_exposed_groups():
    b = Battle(raid(32, (6.0, 2.0), (10.0, 2.0)), random.Random(0), army=line_army())
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (5.0, 9.0), (11.0, 9.0))      # Front nach Norden
    b.command_move([pelt], (2.0, 13.0))                  # Peltasten allein, weit weg von den Hopliten
    b.command_move([cav], (13.0, 13.0))
    run(b, 6)
    r = b.brain.report
    assert r.front_blocked and r.line_y is not None and abs(r.line_y - 9.0) < 0.3
    assert hop in r.phalanxes
    assert pelt.id in r.exposed                          # keine Hopliten in der Nähe
    assert cav.id not in r.exposed                       # beritten
    cav.dismount()
    r2 = b.brain._report(b)
    assert cav.id in r2.exposed


def test_target_value_prefers_weak_targets_over_the_phalanx_front():
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0), army=line_army())
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (5.0, 9.0), (11.0, 9.0))
    b.command_move([pelt], (2.0, 12.0))
    run(b, 6)
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 8.0, 6.0                        # vor der Front
    brain = b.brain
    brain.report = brain._report(b)
    assert brain.target_value(b, raider, hop) < 0.6
    assert brain.target_value(b, raider, pelt) >= 2.0
    raider.x, raider.y = 8.0, 12.0                       # im Rücken
    assert brain.target_value(b, raider, hop) > 1.0


def test_flank_route_walks_around_the_front_and_attacks_from_the_side():
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0), army=line_army())
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (5.0, 9.0), (11.0, 9.0))
    run(b, 6)
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 8.0, 6.5
    wp = b.brain.flank_route(b, raider, hop)
    assert wp is not None
    assert abs(wp[0] - 8.0) > hop.half_w                 # seitlich neben der Front
    raider.x, raider.y = hop.x + hop.half_w + 0.7, 9.0   # in der Flanke: direkt angreifen
    assert b.brain.flank_route(b, raider, hop) is None


def test_a_ring_has_no_flank_to_walk_around():
    """Gegen einen Kreis gibt es keinen Weg um die Front: Wer davor steht, greift an,
    statt neben dem Kreis auf eine Flanke zu warten, die es nicht gibt."""
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0), army=line_army())
    hop, pelt, cav = b.units(Side.STADT)
    b.command_formation([hop], "o")
    b.command_ring([hop], (8.0, 9.0), 1.0)
    run(b, 6)
    assert hop.formation == "o" and formed(hop)
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 8.0, 6.0
    assert b.brain.flank_route(b, raider, hop) is None
    assert rear_route(b, raider, hop) is None


# ---------------------------------------------------------------- Pläne
def test_raiders_go_around_or_harass_a_phalanx_but_charge_an_open_settlement():
    b = Battle(KLEIN_OFFEN, random.Random(2))
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (3.0, 10.5), (13.0, 10.5))
    b.command_line([pelt], (5.0, 11.6), (11.0, 11.6))
    b.command_move([cav], (14.0, 12.5))
    run(b, 8)
    assert b.brain.plan in ("umgehen_west", "umgehen_ost", "zermuerben", "flankieren", "ruecken"), b.brain.plan
    assert any(e.startswith("Die Räuber:") for e in b.events)

    b2 = Battle(KLEIN_OFFEN, random.Random(2))
    b2.alarm = False                                       # niemand stellt eine Phalanx
    run(b2, 8)
    assert b2.brain.plan == "frontal"


def test_harassing_raiders_keep_their_distance_until_the_javelins_are_gone():
    b = Battle(KLEIN_OFFEN, random.Random(3), enemy_count=64)
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (3.0, 10.5), (13.0, 10.5))
    b.command_move([pelt], (8.0, 12.0))
    b.command_move([cav], (8.0, 13.0))
    b.brain.memory.gains = {"klein_offen": {"umgehen_west": [-1.0] * 5, "umgehen_ost": [-1.0] * 5}}   # Umgehen ist verbrannt
    run(b, 8)
    assert b.brain.plan == "zermuerben"
    run(b, 12)
    raiders = b.units(Side.FEIND, fighting_only=True)
    assert any(u.ammo() < 10 * u.count("peltast") for u in raiders)     # es wurde geworfen
    assert all(u.stance is not Stance.ANGRIFF for u in raiders if u.ammo() > 0 and not u.engaged)
    assert hop.men >= 26                                                 # die Phalanx wurde nicht gestürmt


def test_horde_sleeps_then_picks_a_plan():
    b = Battle(KLEIN_HORDE, random.Random(1))
    b.command_hold()
    run(b, 3)
    assert b.brain.plan == "lagern" and not b.horde_awake
    hop = b.units(Side.STADT)[0]
    b.command_line([hop], (5.0, 8.5), (11.0, 8.5))
    run(b, 12)
    assert b.horde_awake and b.brain.plan != "lagern"


# ------------------------------------------------------------- Siedlung
def test_settlement_cavalry_ignores_the_phalanx_but_charges_exposed_peltasts():
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (4.0, 9.5), (12.0, 9.5))
    b.command_line([pelt], (5.0, 10.6), (11.0, 10.6))
    b.command_move([cav], (13.5, 11.5))
    run(b, 10)
    enemy = {u.name: u for u in b.units(Side.FEIND)}
    assert enemy["Reiter"].stance is not Stance.ANGRIFF          # nichts Lohnendes in Reichweite
    b.command_move([pelt], (3.0, 7.5))                           # Peltasten allein nach vorn
    charged = False
    for _ in range(int(8 / DT)):
        b.update(DT)
        if enemy["Reiter"].stance is Stance.ANGRIFF and enemy["Reiter"].target_id == pelt.id:
            charged = True
            break
    assert charged


def test_settlement_line_turns_its_front_towards_a_flank_attack():
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    enemy = {u.name: u for u in b.units(Side.FEIND)}
    line = enemy["Hopliten"]
    assert line.facing == (0.0, 1.0)
    b.command_move([hop], (12.5, 6.0))                           # in die Ostflanke
    b.command_move([pelt, cav], (8.0, 15.0))
    run(b, 14)
    assert line.facing[0] > 0.5, line.facing                     # Front nach Osten gedreht
    assert any("drehen die Front" in e for e in b.events)


def test_memory_weights_plans_by_past_gains(tmp_path):
    m = Memory(path=str(tmp_path / "ki.json"))
    assert m.weight("klein_offen", "frontal") == 1.0
    m.record("klein_offen", "frontal", -0.5)
    m.record("klein_offen", "frontal", -0.5)
    assert m.weight("klein_offen", "frontal") < 1.0
    m.record("klein_offen", "umgehen_west", 0.6)
    assert m.weight("klein_offen", "umgehen_west") > 1.0
    loaded = Memory.load(str(tmp_path / "ki.json"))
    assert loaded.gains == m.gains
    assert Memory.load(str(tmp_path / "fehlt.json")).gains == {}


def test_battle_records_the_plan_result_into_memory():
    mem = Memory()
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0), army=line_army(), memory=mem)
    b.command_attack()
    run(b, 120)
    assert b.outcome is not None
    assert "t" in mem.gains and sum(len(v) for v in mem.gains["t"].values()) >= 1


def test_memory_changes_the_chosen_plan():
    def plan_after(mem: Memory) -> str:
        b = Battle(KLEIN_OFFEN, random.Random(2), memory=mem)
        hop, pelt, cav = b.units(Side.STADT)
        b.command_line([hop], (3.0, 10.5), (13.0, 10.5))
        b.command_move([pelt, cav], (8.0, 12.5))
        run(b, 3)
        return b.brain.plan

    first = plan_after(Memory())
    burnt = Memory(gains={"klein_offen": {first: [-1.0] * 5}})
    assert plan_after(burnt) != first


def test_failed_attack_on_a_phalanx_front_falls_back():
    b = Battle(raid(32, (8.0, 6.5)), random.Random(0), army=Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 30)]),
    ]))
    hop = b.units(Side.STADT)[0]
    b.command_line([hop], (5.0, 9.0), (11.0, 9.0))
    run(b, 4)
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 8.0, 7.6
    b.brain._attack(b, raider, hop)
    raider.morale = 1.0
    run(b, 40)
    assert any("weichen vor der Phalanx zurück" in e for e in b.events)
    assert b.brain.state[raider.id].hard == hop.id


def test_plan_names_are_german_and_shown():
    b = Battle(KLEIN_OFFEN, random.Random(0))
    assert b.enemy_plan == ""
    b.command_hold()
    run(b, 1)
    assert b.enemy_plan == PLAN_NAMES[b.brain.plan]


def test_legacy_ai_still_available():
    b = Battle(KLEIN_OFFEN, random.Random(0), ai="einfach")
    b.command_hold()
    run(b, 2)
    assert b.enemy_plan == "" and not isinstance(b.brain, Brain)
    assert all(u.stance in (Stance.RAUB, Stance.ANGRIFF) for u in b.units(Side.FEIND))


def test_raiders_pin_the_front_and_flank_the_phalanx():
    b = Battle(KLEIN_OFFEN, random.Random(4), enemy_count=96)
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (4.5, 10.5), (11.5, 10.5))
    b.command_move([pelt], (8.0, 12.0))
    b.command_move([cav], (8.0, 13.5))
    b.brain.memory.gains = {"klein_offen": {"ruecken": [-1.0] * 5}}   # der Rückenangriff ist verbrannt: Flanke
    run(b, 6)
    assert b.brain.plan == "flankieren", b.brain.plan
    roles = set(b.brain.roles.values())
    assert roles == {"binden", "flanke"}
    assert b.brain.flank_target == hop.id
    assert any("umfassen" in e for e in b.events)
    arcs = set()
    for _ in range(int(40 / DT)):
        b.update(DT)
        if hop.last_arc:
            arcs.add(hop.last_arc)
        if b.outcome:
            break
    assert "flank" in arcs or "rear" in arcs                # die Phalanx wurde von der Seite getroffen
    assert "front" in arcs                                  # und vorn gebunden


def test_raiders_go_around_and_fall_on_the_rear():
    b = Battle(KLEIN_OFFEN, random.Random(4), enemy_count=96)
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (4.5, 10.5), (11.5, 10.5))
    b.command_move([pelt], (8.0, 12.0))
    b.command_move([cav], (8.0, 13.5))
    b.brain.memory.gains = {"klein_offen": {"flankieren": [-1.0] * 5, "umgehen_west": [-1.0] * 5,
                                      "umgehen_ost": [-1.0] * 5, "zermuerben": [-1.0] * 5}}
    run(b, 6)
    assert b.brain.plan == "ruecken", b.brain.plan
    assert set(b.brain.roles.values()) == {"binden", "flanke"}
    assert any("in den Rücken" in e for e in b.events)
    rear_hit = False
    for _ in range(int(40 / DT)):
        b.update(DT)
        if hop.last_arc == "rear":
            rear_hit = True
            break
        if b.outcome:
            break
    assert rear_hit                                          # jemand ist ganz herumgelaufen
    hop2 = Lochos(90, Side.STADT, [men("mittel", 12)], 8.0, 6.0, facing=(0.0, -1.0), stance=Stance.PHALANX, in_line=True)
    assert b.brain._room_behind(b, hop2) >= 2.0
    hop3 = Lochos(91, Side.STADT, [men("mittel", 12)], 8.0, 17.4, facing=(0.0, -1.0), stance=Stance.PHALANX, in_line=True)
    assert b.brain._room_behind(b, hop3) < 1.0                # mit dem Rücken am Kartenrand: kein Platz


def test_settlement_splits_mixed_groups_by_arm():
    from game.army import split_by_arm
    army = Army(groups=[GroupSpec("Alle", [Tier("schwer", 20), Tier("peltast", 10), Tier("reiter", 12)])])
    parts = split_by_arm(army)
    assert [g.name for g in parts.groups] == ["Alle", "Peltasten", "Reiter"]
    assert parts.total_men() == 42
    b = Battle(KLEIN_ANGRIFF, random.Random(1), army=army, enemy_count=42, doctrine="spiegel")
    assert len(b.units(Side.FEIND)) == 3
    assert len(b.units(Side.STADT)) == 3 and len(b.verbaende) == 1   # beim Spieler: je Gattung eine Gruppe, ein Verband


def test_settlement_cavalry_flanks_a_pinned_phalanx():
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    enemy = {u.name: u for u in b.units(Side.FEIND)}
    line = enemy["Hopliten"]
    b.command_move([pelt, cav], (8.0, 15.5))
    b.command_line([hop], (5.0, line.y + line.half_d + 1.0), (11.0, line.y + line.half_d + 1.0))
    seen = False
    for _ in range(int(45 / DT)):
        b.update(DT)
        if enemy["Reiter"].stance is Stance.ANGRIFF and enemy["Reiter"].target_id == hop.id:
            seen = True
        if seen and hop.last_arc in ("flank", "rear"):
            break
    assert seen                                             # die Reiter greifen die gebundene Phalanx an
    assert hop.last_arc in ("flank", "rear")                # und zwar von der Seite


# ------------------------------------------------------------- Doktrinen
def test_doctrine_classifies_the_players_army():
    from game.doctrine import classify, shares
    from game.army import default_army
    std = default_army()
    s = shares(std)
    assert abs(s["hopliten"] - 40 / 75) < 0.01 and abs(s["reiter"] - 20 / 75) < 0.01
    assert classify(std) == "ausgewogen"
    assert classify(Army(groups=[GroupSpec("H", [Tier("schwer", 40)]), GroupSpec("P", [Tier("peltast", 20)])])) == "ohne_reiter"
    assert classify(Army(groups=[GroupSpec("R", [Tier("reiter", 40)]), GroupSpec("H", [Tier("schwer", 20)])])) == "reiterlastig"
    assert classify(Army(groups=[GroupSpec("Alle", [Tier("schwer", 30), Tier("peltast", 15), Tier("reiter", 20)])])) == "ein_block"
    assert classify(Army(groups=[GroupSpec("P", [Tier("peltast", 40)]), GroupSpec("H", [Tier("schwer", 20)]), GroupSpec("R", [Tier("reiter", 10)])])) == "peltastenlastig"


def test_settlement_uses_its_own_doctrine_not_a_copy():
    from game.doctrine import DOCTRINES, enemy_army
    army = Army(groups=[GroupSpec("Alle", [Tier("schwer", 30), Tier("peltast", 15), Tier("reiter", 30)])])
    forced = Battle(KLEIN_ANGRIFF, random.Random(1), army=army, enemy_count=90, doctrine="schwere_phalanx")
    assert forced.doctrine == "schwere_phalanx"
    assert forced.men(Side.FEIND) == 90 + 1          # dazu der Anführer
    assert not any(m.kind.cavalry for u in forced.units(Side.FEIND) for m in u.all_men())   # keine Reiter in der schweren Phalanx
    mirror = Battle(KLEIN_ANGRIFF, random.Random(1), army=army, enemy_count=90, doctrine="spiegel")
    assert sum(1 for u in mirror.units(Side.FEIND) for m in u.all_men() if m.kind.cavalry) == 36   # 30 von 75, auf 90 skaliert
    for name, template in DOCTRINES.items():
        scaled = enemy_army(army, 120, name)
        assert scaled.total_men() == 120, name


def test_settlement_picks_a_counter_for_every_player_class():
    from game.doctrine import COUNTERS, choose_doctrine
    from game.army import default_army
    assert set(COUNTERS) == {"reiterlastig", "peltastenlastig", "ohne_reiter", "ein_block", "ausgewogen"}
    assert all(v != "spiegel" for v in COUNTERS.values())          # die Siedlung kopiert nicht mehr
    b = Battle(KLEIN_ANGRIFF, random.Random(1), army=default_army())
    assert b.doctrine == choose_doctrine(default_army()) != "spiegel"
    assert any("Siedlung stellt" in e for e in b.events)


def test_settlement_learns_a_better_doctrine_from_memory():
    from game.doctrine import MEMORY_KEY, choose_doctrine, classify
    from game.army import default_army
    army = default_army()
    mem = Memory()
    assert choose_doctrine(army, mem) == choose_doctrine(army)
    key = f"{MEMORY_KEY}:{classify(army)}"
    for _ in range(3):
        mem.record(key, choose_doctrine(army), -0.6)          # die Vorgabe hat verloren
        mem.record(key, "reiterlastig", 0.5)                  # eine andere hat gewonnen
    assert choose_doctrine(army, mem) == "reiterlastig"
    b = Battle(KLEIN_ANGRIFF, random.Random(1), army=army, memory=mem)
    assert b.doctrine == "reiterlastig"
    for _ in range(12):                                     # wie ein Spieler: wer sich gesammelt hat, greift wieder an
        b.command_attack()
        run(b, 20)
        if b.outcome is not None:
            break
    assert b.outcome is not None
    assert len(mem.gains[key]["reiterlastig"]) == 4          # der Ausgang wurde gemerkt


# ------------------------------------------------------------- Plänkeln
def test_settlement_peltasts_skirmish_beside_their_own_line_and_hold_when_empty():
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    enemy = {u.name: u for u in b.units(Side.FEIND)}
    ep, eh = enemy["Peltasten"], enemy["Hopliten"]
    b.command_line([hop], (6.0, 8.5), (10.0, 8.5))               # Phalanx vor die Linie der Siedlung
    b.command_move([pelt, cav], (8.0, 15.0))
    hp0 = sum(m.hp for m in hop.all_men())
    skirmished = False
    for _ in range(int(14 / DT)):
        b.update(DT)
        if ep.stance is Stance.PLAENKELN:
            skirmished = True
            assert not (abs(ep.x - eh.x) < eh.half_w and abs(ep.y - eh.y) < eh.half_d + 0.1)   # nie in der eigenen Phalanx
    assert skirmished
    assert ep.ammo() < 10 * ep.men                                # es wurde geworfen
    assert sum(m.hp for m in hop.all_men()) < hp0
    run(b, 14)
    assert ep.ammo() == 0
    assert ep.stance is Stance.HALTEN                             # die Siedlung schickt leere Peltasten nicht ins Handgemenge
    assert hop.men >= 36


def test_ai_skirmishers_back_off_from_charging_hoplites():
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    ep = {u.name: u for u in b.units(Side.FEIND)}["Peltasten"]
    b.command_line([hop], (6.0, 8.5), (10.0, 8.5))
    b.command_move([pelt, cav], (8.0, 15.0))
    run(b, 12)
    assert ep.stance is Stance.PLAENKELN
    b.command_attack_target([hop], ep)
    for _ in range(int(6 / DT)):
        b.update(DT)
        assert ep.stance is Stance.PLAENKELN
        assert not ep.engaged                                     # sie weichen aus, bevor die Hopliten sie fassen
    assert ep.men == 15


# ------------------------------------------------------- Gegenmittel der KI
def test_ai_peltasts_skirmish_from_the_open_right_flank():
    """Peltasten der Siedlung gehen an die schildlose rechte Seite der Phalanx und werfen von dort."""
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    ep = {u.name: u for u in b.units(Side.FEIND)}["Peltasten"]
    b.command_line([hop], (6.0, 8.5), (10.0, 8.5))               # Front nach Norden: rechts ist Osten
    b.command_move([pelt, cav], (8.0, 15.0))
    run(b, 16)
    assert ep.stance is Stance.PLAENKELN and ep.flank_throw
    along, _ = hop.local(ep.pos)
    assert along > hop.half_w and b.arc_of(hop, ep.pos) == "flank"
    ammo = ep.ammo()
    run(b, 3)
    assert ep.ammo() < ammo                                       # sie werfen von dort


def test_open_side_spot_only_against_hoplite_phalanxes():
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    ep = {u.name: u for u in b.units(Side.FEIND)}["Peltasten"]
    ep.flank_throw = True
    assert b._open_side_spot(ep, pelt) is None                    # Peltasten haben keinen Schild links
    assert b._open_side_spot(ep, hop) is None                     # noch nicht in Formation


def test_player_peltasts_do_not_seek_the_flank():
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    assert not any(u.flank_throw for u in b.units(Side.STADT))


def cavalry_behind_settlement(pin: bool):
    """Siedlung (Spiegel) mit ihrer Phalanx; die Reiter des Spielers stehen hinter ihr,
    auf Wunsch steht die Phalanx des Spielers dicht vor ihrer Front."""
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    eh = {u.name: u for u in b.units(Side.FEIND)}["Hopliten"]
    if pin:
        b.command_line([hop], (6.0, 8.0), (10.0, 8.0))
    else:
        b.command_move([hop], (8.0, 15.0))
    b.command_move([pelt], (8.0, 15.0))
    cav.x, cav.y = 13.0, 1.2
    cav.place_men()
    b.command_move([cav], (13.0, 1.2))
    run(b, 8)
    return b, hop, cav, eh


def test_ai_phalanx_turns_its_front_to_cavalry_from_behind():
    b, hop, cav, eh = cavalry_behind_settlement(pin=False)
    b.command_attack_target([cav], eh)
    run(b, 10)
    assert eh.formation == "linie"                                # frei vor sich: drehen statt Kreis
    assert any("drehen die Front gegen die Reiter" in e for e in b.events)
    assert any("rennen in die Speere" in e for e in b.events)
    assert eh.men == 41 and cav.men < 20


def test_pinned_ai_phalanx_neither_turns_nor_forms_a_ring():
    """Fußvolk vorn, Reiter hinten, aber nicht klar in Unterzahl: die Front bleibt, kein Kreis."""
    b, hop, cav, eh = cavalry_behind_settlement(pin=True)
    b.command_attack_target([cav], eh)
    run(b, 6)
    assert eh.formation == "linie"
    assert not any("drehen die Front gegen" in e or "Kreis" in e for e in b.events)


def surround(b, eh, placements):
    """Spielergruppen an feste Plätze um die Siedlungsphalanx (ruhend), die Peltasten der Siedlung weit weg."""
    ep = {u.name: u for u in b.units(Side.FEIND)}["Peltasten"]
    ep.x, ep.y = 1.5, 0.8
    ep.place_men()
    for u, (x, y) in placements:
        u.x, u.y = x, y
        u.place_men()
        b.command_move([u], (x, y))
    b.alarm = False


def test_ring_only_when_outnumbered_and_surrounded():
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    eh = {u.name: u for u in b.units(Side.FEIND)}["Hopliten"]   # 41 Mann bei (8; 5,5), Front nach Süden
    own = b.units(Side.FEIND, fighting_only=True)
    foes = b.units(Side.STADT, fighting_only=True)
    surround(b, eh, [(hop, (8.0, 8.0)), (cav, (8.0, 3.2)), (pelt, (11.5, 5.5))])
    assert b.brain._desperate(b, eh, foes, own)                  # vorn, hinten, rechts; 76 gegen 41
    surround(b, eh, [(hop, (8.0, 8.0)), (cav, (14.0, 15.0)), (pelt, (11.5, 5.5))])
    assert not b.brain._desperate(b, eh, foes, own)              # nur zwei Seiten, 56 gegen 41
    surround(b, eh, [(hop, (6.0, 8.0)), (cav, (10.5, 8.5)), (pelt, (8.0, 8.8))])
    assert not b.brain._desperate(b, eh, foes, own)              # Übermacht, aber alle vorn


def test_surrounded_ai_phalanx_forms_a_ring_and_reforms_after():
    b = Battle(KLEIN_ANGRIFF, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    eh = {u.name: u for u in b.units(Side.FEIND)}["Hopliten"]
    facing = eh.facing
    surround(b, eh, [(hop, (8.0, 8.0)), (cav, (8.0, 3.2)), (pelt, (11.5, 5.5))])
    run(b, 1)
    assert eh.formation == "o"
    assert any("umzingelt und bilden einen Kreis" in e for e in b.events)
    b.command_move([hop, pelt, cav], (8.0, 16.0))
    run(b, 14)                                                    # (die Reiter kommen erst nach gut 10 s los)
    assert eh.formation == "linie"                                # nicht mehr umzingelt: zurück in die Linie
    assert eh.facing[0] * facing[0] + eh.facing[1] * facing[1] > 0.9


def test_cavalry_at_the_front_needs_no_counter():
    b, hop, cav, eh = cavalry_behind_settlement(pin=False)
    cav.x, cav.y = 8.0, 12.0                                      # vor der Front (sie schaut nach Süden)
    cav.place_men()
    b.command_attack_target([cav], eh)
    run(b, 4)
    assert eh.formation == "linie"
    assert not any("Kreis" in e or "drehen die Front gegen" in e for e in b.events)


def test_raiders_do_not_form_rings():
    """Räuber haben keine Schilde und Speere: ein Kreis hält Reiter nicht auf."""
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0), army=line_army())
    assert not any(b.brain._can_brace(b, u) for u in b.units(Side.FEIND))


# ------------------------------------------------------------------- Reserve
def reserve_battle():
    """Vier Räubergruppen, die hinterste (y = -2) ist die Reserve; der Spieler steht als Linie."""
    b = Battle(raid(64, (5.0, 1.0), (8.0, 1.0), (11.0, 1.0), (8.0, -2.0)), random.Random(0), army=line_army())
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (5.0, 11.0), (11.0, 11.0))
    b.command_line([pelt], (6.0, 12.0), (10.0, 12.0))
    b.command_move([cav], (8.0, 14.0))
    return b, hop, pelt, cav


def test_raiders_hold_back_their_rearmost_group():
    b, hop, pelt, cav = reserve_battle()
    run(b, 1)
    reserve = b.by_id(b.brain.reserve_id)
    assert reserve is not None and b.brain.reserve_held
    assert b.brain.reserve_home[1] < -1.0                         # die hinterste Gruppe
    behind = []
    for _ in range(int(12 / DT)):
        b.update(DT)
        if not b.brain.reserve_held:
            break
        others = [o for o in b.units(Side.FEIND, True) if o is not reserve]
        assert reserve.stance is not Stance.ANGRIFF
        assert b.brain.roles.get(reserve.id) is None             # bekommt keine Rolle beim Umfassen
        if b.time > 5.0:
            behind.append(sum(o.y for o in others) / len(others) - reserve.y)
    assert behind and min(behind) > 2.0                           # hinter der Hauptmacht
    assert not b.brain.reserve_held                               # die Umfassung ruft sie
    assert any("Reserve in den Kampf (Umfassung)" in e for e in b.events)


def test_reserve_joins_when_a_foe_comes_close():
    b, hop, pelt, cav = reserve_battle()
    run(b, 6)
    reserve = b.by_id(b.brain.reserve_id)
    b.command_attack_target([cav], reserve)
    for _ in range(int(10 / DT)):
        b.update(DT)
        if not b.brain.reserve_held:
            break
    assert not b.brain.reserve_held
    assert any("Reserve in den Kampf" in e for e in b.events)


def test_reserve_joins_after_its_time():
    b, hop, pelt, cav = reserve_battle()
    run(b, 1)
    b.brain.reserve_since = b.time - config.AI_RESERVE_MAX
    run(b, 1)
    assert not b.brain.reserve_held
    assert any("Reserve in den Kampf (Zeit)" in e for e in b.events)


def test_no_reserve_with_few_groups_or_when_switched_off(monkeypatch):
    b = Battle(raid(32, (6.0, 2.0), (10.0, 2.0)), random.Random(0), army=line_army())
    b.command_move(None, (8.0, 12.0))
    run(b, 1)
    assert not b.brain.reserve_held
    monkeypatch.setattr(config, "AI_RESERVE", False)
    b, *_ = reserve_battle()
    run(b, 1)
    assert not b.brain.reserve_held


def test_a_charging_horde_does_not_wait_in_its_camp():
    """Verteidigung gegen die Räuberhorde: Sie stürmt gleich los, statt zu lagern."""
    from game.scenarios import HORDE_STURM
    b = Battle(HORDE_STURM, random.Random(1))
    assert b.horde_awake
    start = sum(u.y for u in b.units(Side.FEIND)) / len(b.units(Side.FEIND))
    b.command_hold(None)
    for _ in range(int(8 / DT)):
        b.update(DT)
    now = sum(u.y for u in b.units(Side.FEIND)) / len(b.units(Side.FEIND))
    assert now > start + 4.0                                  # auf die eigene Truppe im Süden zu
    assert b.brain.plan != "lagern"


def test_released_reserve_goes_round_the_front_into_the_rear():
    """Wird die Reserve gerufen und steht vor ihr eine geschlossene Phalanx, läuft sie nicht
    frontal hinein, sondern um die Flanke und fällt der Phalanx in Flanke oder Rücken."""
    b, hop, pelt, cav = reserve_battle()
    run(b, 3)
    assert b.brain.reserve_held and hop.in_phalanx
    reserve = b.by_id(b.brain.reserve_id)
    b.brain.reserve_since = b.time - config.AI_RESERVE_MAX
    run(b, 0.6)
    assert not b.brain.reserve_held and b.brain.reserve_flank == hop.id
    assert any("um die Flanke herum" in e for e in b.events)
    hit_from = None
    for _ in range(int(40 / DT)):
        b.update(DT)
        if reserve.engaged and hop.id in reserve.contacts and hit_from is None:
            hit_from = b.arc_of(hop, reserve.pos)
        if reserve.engaged and hit_from is None and {pelt.id, cav.id} & set(reserve.contacts):
            hit_from = "rear"                                  # hinter der Phalanx auf Peltasten oder Reiter gestoßen
        assert not (b.brain.reserve_flank is not None and reserve.stance is Stance.ANGRIFF
                    and b.arc_of(hop, reserve.pos) == "front")       # unterwegs kein Angriff auf die Front
        if hit_from is not None or not reserve.fighting:
            break
    assert hit_from in ("flank", "rear"), hit_from
