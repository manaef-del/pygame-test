"""Tests der Kampflogik. Läuft ohne Pygame."""

import math
import random

import pytest

from game import config
from game.army import OWN_DEFAULT, Army, GroupSpec, Tier, default_army, scaled_army
from game.battle import Battle
from game.geometry import arc, snap4
from game.scenarios import (OFFENE_SIEDLUNG, PALISADE, RAEUBERHORDE, SIEDLUNG_OFFEN, SIEDLUNG_WALL,
                            RaiderSpawn, Scenario)
from game.units import UNIT_TYPES, Lochos, Man, Side, Stance, arrange

DT = 1 / 30


def run(b: Battle, seconds: float) -> None:
    for _ in range(int(seconds / DT)):
        b.update(DT)
        if b.outcome:
            break


def resolve_only(b: Battle, seconds: float) -> None:
    """Nur Kampf und Moral, keine Bewegung: prüft die reine Auflösung."""
    for _ in range(int(seconds / DT)):
        b._combat(DT)
        b._morale(DT)


def men(kind: str, n: int) -> list[Man]:
    return [Man(UNIT_TYPES[kind]) for _ in range(n)]


def army_of(*groups: GroupSpec) -> Army:
    return Army(groups=list(groups))


def raid(men: int, *spawns: tuple[float, float], houses=((2, 17),)) -> Scenario:
    """Kleines Verteidigungsszenario mit Räubern an festen Punkten."""
    return Scenario(
        "t", "t", "", role="verteidigung", enemy_kind="raeuber",
        enemy_default=men, enemy_min=men, enemy_max=men, houses=houses,
        raider_spawns=tuple(RaiderSpawn(x, y) for x, y in spawns),
    )


def dist_of(a, b) -> float:
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


def static_line(raider_y: float, n_raiders: int = 4) -> Battle:
    """Drei Hoplitengruppen in der Linie (Front Nord), Räuber dicht davor oder dahinter,
    jede Räubergruppe genau vor einer Hoplitengruppe (die vierte neben dem Ende)."""
    scn = raid(16 * n_raiders, *((6.0 + i * 1.7, raider_y) for i in range(n_raiders)))
    army = army_of(
        GroupSpec("A", [Tier("schwer", 7), Tier("mittel", 7)]),
        GroupSpec("B", [Tier("schwer", 7), Tier("mittel", 6)]),
        GroupSpec("C", [Tier("mittel", 7), Tier("leicht", 6)]),
    )
    b = Battle(scn, random.Random(0), army=army)
    for i, u in enumerate(b.units(Side.STADT)):
        u.reform(7)
        u.x, u.y = 6.0 + i * 1.7, 9.5
        u.stance = Stance.PHALANX
        u.in_line = True
        u.facing = (0.0, -1.0)
        u.place_men()
    for u in b.units(Side.FEIND):
        u.stance = Stance.ANGRIFF
        u.place_men()
    return b


# ------------------------------------------------------------- Geometrie
def test_arc_classification():
    f = (0.0, -1.0)
    assert arc(f, (0.0, -1.0), 60, 120) == "front"
    assert arc(f, (1.0, 0.0), 60, 120) == "flank"
    assert arc(f, (0.0, 1.0), 60, 120) == "rear"
    assert snap4((0.3, -0.9)) == (0.0, -1.0)


# ------------------------------------------------------------ Aufstellung
def test_default_army_is_three_groups_using_whole_pool():
    a = default_army()
    assert a.valid()
    assert [g.name for g in a.groups] == ["Hopliten", "Peltasten", "Reiter"]
    assert a.remaining() == 0
    assert a.total_men() == a.total == OWN_DEFAULT == 75


def test_army_blocks_share_one_pool_and_swap_freely():
    a = Army(groups=[GroupSpec("G", [Tier("reiter", 5)])], total=30)
    assert a.max_for(0, 0) == 30
    assert a.set_count(0, 0, 50) == 30                       # wird auf den Vorrat gekappt
    assert a.remaining() == 0
    a.set_count(0, 0, 0)                                     # Reiter gestrichen: die Männer sind frei ...
    a.add_tier(0)
    assert a.groups[0].tiers[1].kind == "reiter" and a.groups[0].tiers[1].count == 5
    a.set_kind(0, 1, "schwer")                               # ... und gehen an die Hopliten
    assert a.groups[0].tiers[1].kind == "schwer" and a.groups[0].tiers[1].count == 5
    assert a.set_count(0, 1, 30) == 30 and a.remaining() == 0
    a.move_tier(0, 1, -1)
    assert [t.kind for t in a.groups[0].tiers] == ["schwer", "reiter"]
    a.remove_tier(0, 1)
    assert len(a.groups[0].tiers) == 1 and a.valid()
    b = scaled_army(a, 60)
    assert b.total == 60 and b.total_men() == 60 and b.groups[0].tiers[0].count == 60


def test_tiers_build_men_in_order_and_interleave_when_stretched():
    g = GroupSpec("G", [Tier("schwer", 4), Tier("leicht", 4), Tier("peltast", 4)])
    men_list = g.build_men()
    assert [m.tier for m in men_list] == [0] * 4 + [1] * 4 + [2] * 4
    narrow = arrange(men_list, 4)
    assert ["".join(m.kind.short for m in r) for r in narrow] == ["SSSS", "LLLL", "PPPP"]
    wide = arrange(men_list, 12)
    kinds = [m.kind.short for m in wide[0]]
    assert len(wide) == 1 and kinds[:6] == ["S", "L", "P", "S", "L", "P"]
    again = arrange(wide[0], 4)                              # zurück: Abschnitte wieder getrennt
    assert ["".join(m.kind.short for m in r) for r in again] == ["SSSS", "LLLL", "PPPP"]


def test_battle_deploys_army_groups():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    city = b.units(Side.STADT)
    assert [u.name for u in city] == ["Hopliten", "Peltasten", "Reiter"]
    assert b.men(Side.STADT) == 75 + 1                     # die Vorgabe-Truppe und ihr Anführer
    assert [u.depth for u in city] == [3, 3, 3]
    assert all(0 < u.x < config.COLS for u in city)
    hop = city[0]
    assert [m.kind.key for m in hop.rows[0]] == ["schwer"] * hop.width


# ----------------------------------------------------------- Reihenmodell
def test_damage_hits_exposed_row():
    u = Lochos(1, Side.STADT, [men("schwer", 4), men("peltast", 4)], 5, 5, facing=(0, -1))
    assert u.exposed_row("front") == 0 and u.exposed_row("rear") == 1
    fallen = u.take_damage(1, UNIT_TYPES["peltast"].hp * 2)
    assert fallen == 2 and u.count("peltast") == 2 and u.count("schwer") == 4
    u.take_damage(1, 10)
    assert len(u.rows) == 1 and u.count("peltast") == 0
    # Mit Zufall verteilt sich der Schaden auf mehrere Männer
    v = Lochos(2, Side.STADT, [men("schwer", 4)], 5, 5)
    v.take_damage(0, 3.0, random.Random(3))
    assert v.men == 4 and sum(m.hp for m in v.all_men()) == pytest.approx(4 * 3.0 - 3.0)
    assert sum(1 for m in v.all_men() if m.hp < 3.0) >= 2


def test_group_speed_is_slowest_member():
    fast = Lochos(1, Side.STADT, [men("reiter", 4)], 0, 0)
    mixed = Lochos(2, Side.STADT, [men("reiter", 4), men("schwer", 2)], 0, 0)
    assert fast.speed == UNIT_TYPES["reiter"].speed
    assert mixed.speed == UNIT_TYPES["schwer"].speed


def test_peltasts_behind_throw_while_front_fights():
    u = Lochos(1, Side.STADT, [men("schwer", 4), men("peltast", 4)], 0, 0)
    assert len(u.throwers(engaged=True)) == 4
    front = Lochos(2, Side.STADT, [men("peltast", 4), men("schwer", 4)], 0, 0)
    assert front.throwers(engaged=True) == []
    assert len(front.throwers(engaged=False)) == 4
    for m in front.rows[0]:
        m.ammo = 0
    assert front.throwers(engaged=False) == []


def test_reform_keeps_order_and_changes_rows():
    u = Lochos(1, Side.STADT, [men("schwer", 4), men("peltast", 4)], 0, 0)
    u.reform(2)
    assert u.width == 2 and u.depth == 4
    assert [m.kind.key for m in u.rows[0]] == ["schwer", "schwer"]
    u.reform(8)
    assert u.depth == 1 and u.shield_factor() == 0.5


def test_javelins_fly_and_run_out():
    scn = raid(16, (8.0, 7.0))
    army = army_of(GroupSpec("Peltasten", [Tier("peltast", 15)]))
    b = Battle(scn, random.Random(0), army=army)
    pelt = b.units(Side.STADT)[0]
    raider = b.units(Side.FEIND)[0]
    raider.stance = Stance.HALTEN
    raider.target = None
    pelt.x, pelt.y = 8.0, 9.5
    assert pelt.ammo() == 15 * config.JAVELINS
    b.command_hold()
    b._ai_raiders = lambda: None            # Räuber bleiben stehen
    run(b, 0.1)
    mine = [pr for pr in b.projectiles if pr.target_id == raider.id]
    assert 0 < len(mine) <= 15                                 # erste Salve unterwegs, je Mann ein Speer
    assert len({(round(pr.x, 3), round(pr.y, 3)) for pr in mine}) == len(mine)   # von jedem Peltasten aus
    assert all(pr.target_man is not None for pr in mine)
    assert raider.men == 16                                    # noch kein Einschlag
    assert pelt.ammo() == 15 * config.JAVELINS - 15
    run(b, 3.0)
    assert sum(m.hp for m in raider.all_men()) < 16 * UNIT_TYPES["raeuber"].hp   # Speere sind angekommen
    run(b, 20.0)
    assert pelt.ammo() == 0
    assert raider.men < 16
    assert pelt.stance is Stance.ANGRIFF     # Speere leer, Nahkampf
    assert any("Speere verschossen" in e for e in b.events)


def test_shield_factor_scales_phalanx_bonus():
    b = static_line(raider_y=8.8, n_raiders=1)
    raider = b.units(Side.FEIND)[0]
    hoplites = b.units(Side.STADT)[0]
    cav = Lochos(99, Side.STADT, [men("reiter", 8)], 6.0, 9.5, facing=(0, -1), stance=Stance.PHALANX, in_line=True)
    b.lochoi.append(cav)
    raider.x, raider.y = 6.0, 8.2
    hop_mod, _ = b._defense_mod(raider, hoplites)
    cav_mod, _ = b._defense_mod(raider, cav)
    assert hop_mod < 0.5 < cav_mod


# --------------------------------------------------------- Auflösung
def test_phalanx_holds_from_the_front():
    b = static_line(raider_y=8.8)
    resolve_only(b, 40)
    assert b.fallen(Side.STADT) <= 13, b.report()             # die Räuber rücken vorn nach, das kostet etwas mehr
    assert b.men(Side.FEIND, fighting_only=True) < 32, b.report()


def test_phalanx_breaks_from_the_rear():
    front = static_line(raider_y=8.8)
    rear = static_line(raider_y=10.2)
    resolve_only(front, 20)
    resolve_only(rear, 20)
    assert rear.fallen(Side.STADT) > 2 * front.fallen(Side.STADT), (front.report(), rear.report())
    assert rear.fallen(Side.FEIND) < front.fallen(Side.FEIND)


def test_cavalry_weak_against_phalanx_front_strong_in_the_open():
    b = static_line(raider_y=8.8, n_raiders=1)
    hoplit = b.units(Side.STADT)[1]
    cav = Lochos(99, Side.FEIND, [men("reiter", 8)], hoplit.x, 8.4)
    b.lochoi.append(cav)
    front_rate, _ = b._melee_rate(cav, hoplit)
    hoplit.stance = Stance.HALTEN
    hoplit.in_line = False
    open_rate, _ = b._melee_rate(cav, hoplit)
    assert open_rate > 4 * front_rate


def test_routed_units_take_double_damage():
    b = static_line(raider_y=8.8, n_raiders=1)
    raider = b.units(Side.FEIND)[0]
    hoplit = b.units(Side.STADT)[1]
    normal, _ = b._melee_rate(hoplit, raider)
    raider.stance = Stance.FLUCHT
    fleeing, _ = b._melee_rate(hoplit, raider)
    assert fleeing == pytest.approx(normal * config.ROUTED_DAMAGE)


# ----------------------------------------------------------- Befehle
def test_command_move_and_attack_target_single_group():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    cav = next(u for u in b.units(Side.STADT) if u.name == "Reiter")
    b.command_move([cav], (2.0, 5.0))
    assert cav.stance is Stance.HALTEN and cav.target == (2.0, 5.0)
    others = [u for u in b.units(Side.STADT) if u is not cav]
    assert all(u.target is None for u in others)
    run(b, 4)
    assert abs(cav.x - 2.0) < 0.5 and abs(cav.y - 5.0) < 0.5
    foe = b.units(Side.FEIND)[0]
    b.command_attack_target([cav], foe)
    assert cav.stance is Stance.ANGRIFF and cav.target_id == foe.id
    run(b, 6)
    assert foe.men < 16 or cav.engaged


def test_line_width_depth_and_facing_from_drag():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    hop = b.units(Side.STADT)[0]
    short = b.plan_line([hop], (6.0, 10.5), (7.3, 10.5))
    long = b.plan_line([hop], (3.0, 10.5), (13.0, 10.5))
    assert short[0].facing == (0.0, -1.0)                     # links → rechts: Front nach oben
    assert short[0].width < long[0].width and short[0].depth > long[0].depth
    assert short[0].width * short[0].depth >= hop.men
    reverse = b.plan_line([hop], (13.0, 10.5), (3.0, 10.5))
    assert reverse[0].facing == (0.0, 1.0)                    # rechts → links: Front nach unten
    down = b.plan_line([hop], (8.0, 6.0), (8.0, 12.0))
    assert down[0].facing == (1.0, 0.0)                       # oben → unten: Front nach rechts
    assert b.plan_line([hop], (5.0, 5.0), (5.1, 5.0)) == []   # zu kurz


def test_command_line_reforms_only_selection():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    plans = b.command_line([hop], (3.0, 10.5), (13.0, 10.5))
    assert len(plans) == 1 and hop.width == plans[0].width and hop.depth == plans[0].depth
    assert hop.stance is Stance.PHALANX and hop.facing == (0.0, -1.0)
    assert pelt.stance is Stance.HALTEN and cav.stance is Stance.HALTEN
    run(b, 8)
    assert hop.in_line
    plans = b.command_line(None, (2.0, 12.0), (14.0, 12.0))
    assert len(plans) == 3
    assert sum(p.width for p in plans) <= 12.0 / config.MAN_SPACING


def test_unit_at_finds_group_under_tap():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    u = b.units(Side.STADT)[2]
    assert b.unit_at((u.x + 0.2, u.y - 0.2), Side.STADT) is u
    assert b.unit_at((u.x, u.y), Side.FEIND) is None
    assert b.unit_at((0.5, 5.0), Side.STADT) is None


def test_alarm_waits_for_first_command():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    run(b, 5)
    assert b.time == 0.0
    b.command_hold()
    run(b, 1)
    assert b.time > 0.9


# --------------------------------------------------------- Szenarien
def test_unopposed_raiders_loot_every_house():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1), army=Army(groups=[]))
    b.alarm = False
    run(b, 200)
    assert b.outcome == "niederlage"
    assert b.houses_intact() == 0


def test_phalanx_behind_palisade_beats_larger_force():
    """Phalanx in zwei Gliedern hinter dem Tor, Peltasten auf dem Wehrgang, Reiter als
    Reserve: Steht ein Turm, decken die Reiter den Fuß der nächsten Leiter; die Phalanx
    hält das Tor. (Über acht Startwerte gewinnt das 6-mal; seit der Anführer vorn in der
    Mitte steht, einmal weniger als vorher. Startwert 3 gewinnt mit beiden Aufstellungen.)"""
    b = Battle(PALISADE, random.Random(3), enemy_count=112)
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (6.5, 9.5), (9.5, 9.5))       # Hopliten hinter dem Tor, kurz und tief
    b.command_move([pelt], (3.5, 8.5))                 # Peltasten auf den Wehrgang
    b.command_move([cav], (13.0, 12.5))                # Reiter in Reserve
    covered = False
    for i in range(int(300 / DT)):
        b.update(DT)
        if b.outcome:
            break
        if i % 150 == 0 and b.crossings and not covered and cav.fighting:   # alle fünf Sekunden schaut der Spieler hin
            # ein Turm steht: die Reiter an den Fuß der nächsten Leiter, Front zum Wall
            cx = next(iter(b.crossings))[0] + 0.5
            lx, ly = min(b.ladders, key=lambda c: abs(c[0] + 0.5 - cx))
            b.command_line([cav], (lx + 0.5 - 1.5, ly + 1.7), (lx + 0.5 + 1.5, ly + 1.7))
            covered = True
    r = b.report()
    assert r["ausgang"] == "sieg", r
    assert r["feind_start"] >= 1.3 * r["stadt_start"]
    assert r["stadt_gefallen"] <= 0.4 * r["stadt_start"], r   # die Räuber kommen auch über einen Turm
    assert r["feind_gefallen"] >= 0.4 * r["feind_start"], r
    assert r["haeuser_intakt"] >= 1                            # ohne Reserve plündern die Eingesickerten


def test_open_settlement_phalanx_then_pursuit_wins():
    """Kurze, tiefe Linie, Peltasten dahinter, Reiter am Flügel: Alle vier Sekunden
    schaut der Spieler hin, die Reiter fassen, wer der Phalanx in Flanke oder Rücken
    geht, und setzen sich ab, wenn sie selbst umringt sind; die Phalanx dreht die
    Front zur Bedrohung, wenn vorn niemand mehr steht.
    Ist die Hälfte der Räuber gefallen oder geflohen, greifen alle frei an: Reiter
    und Peltasten fassen die Plünderer, die den langsamen Hopliten davonlaufen würden.
    (Über acht Startwerte gewinnt das 6-mal, seit der Anführer vorn in der Mitte steht,
    vorher 7-mal; Startwert 2 gewinnt mit beiden Aufstellungen.)"""
    from game.geometry import norm, sub
    b = Battle(OFFENE_SIEDLUNG, random.Random(2))
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (6.5, 10.5), (9.5, 10.5))
    b.command_line([pelt], (6.5, 11.4), (9.5, 11.4))
    b.command_move([cav], (12.0, 11.5))
    start = b.men(Side.FEIND, fighting_only=True)
    pursuing = False
    for i in range(int(300 / DT)):
        b.update(DT)
        if b.outcome:
            break
        if i % 120 or pursuing:
            continue
        foes = b.units(Side.FEIND, fighting_only=True)
        if not foes:
            continue
        if b.men(Side.FEIND, fighting_only=True) < 0.5 * start:
            b.command_attack()
            pursuing = True
            continue
        if hop.fighting:
            near = [f for f in foes if hop.rect_distance(f.pos) <= 3.0]
            side = [f for f in near if arc(hop.facing, sub(f.pos, hop.pos), config.FRONT_ARC, config.REAR_ARC) != "front"]
            if cav.fighting and len(cav.contacts) >= 2:
                b.command_move([cav], (12.0, 11.5))            # umringt: absetzen und neu anreiten
            elif side and cav.fighting:
                b.command_attack_target([cav], min(side, key=lambda f: hop.rect_distance(f.pos)))
            elif side and len(side) == len(near) and hop.in_phalanx:
                hop.facing = norm(sub(max(side, key=lambda f: f.men).pos, hop.pos))
        if cav.fighting and cav.stance is not Stance.ANGRIFF and cav.target is None:
            weak = [f for f in foes if f.loose or f.stance is Stance.FLUCHT]
            if weak:
                b.command_attack_target([cav], min(weak, key=lambda f: f.rect_distance(cav.pos)))
    assert b.outcome == "sieg", b.report()
    assert b.houses_intact() >= 5         # wer nicht mehr zappelt, kommt um die kurze Linie herum (Lauf 17)
    # die Reserve der Räuber (Lauf 24) kostet hier im Mittel drei Mann mehr (8 Startwerte: 21 statt 18)
    assert b.fallen(Side.STADT) <= 0.35 * 75, b.report()


def test_weak_army_loses_houses():
    """Ein kleiner Haufen hält den Überfall nicht auf."""
    small = army_of(GroupSpec("Wache", [Tier("leicht", 6)]))
    b = Battle(OFFENE_SIEDLUNG, random.Random(1), army=small)
    b.command_hold()
    run(b, 240)
    assert b.outcome == "niederlage"


# ------------------------------------------------------------ Routing
def test_route_goes_through_the_gate():
    b = Battle(PALISADE, random.Random(1))
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 2.5, 6.5
    assert not b.path_clear(raider.pos, (2.5, 12.5))
    goal, final = b.route(raider, (2.5, 12.5))
    assert final is False and goal[1] < b.gate_center[1] - 1.5      # Tor zu: davor warten
    b.gate.closed = False
    goal, final = b.route(raider, (2.5, 12.5))
    assert final is False and abs(goal[0] - b.gate_center[0]) < 1e-6  # Tor offen: hindurch


def test_nobody_enters_palisade_tiles():
    b = Battle(PALISADE, random.Random(3))
    b.command_attack()
    for _ in range(int(120 / DT)):
        b.update(DT)
        for u in b.lochoi:
            if u.alive and b.inside(u.x, u.y):
                assert not b.is_blocked(u.x, u.y, u), (u.name, u.x, u.y)
        if b.outcome:
            break


def test_deterministic_with_seed():
    a = Battle(OFFENE_SIEDLUNG, random.Random(7))
    c = Battle(OFFENE_SIEDLUNG, random.Random(7))
    for b in (a, c):
        b.command_line(None, (3.0, 10.5), (13.0, 10.5))
        run(b, 60)
    assert a.report() == c.report()


# ------------------------------------------------------- Angriff & Gegnerstärke
def test_enemy_count_sets_raider_strength():
    small = Battle(OFFENE_SIEDLUNG, random.Random(1), enemy_count=40)
    big = Battle(OFFENE_SIEDLUNG, random.Random(1), enemy_count=192)
    assert small.men(Side.FEIND) == 40 and big.men(Side.FEIND) == 192
    assert all(8 <= u.men <= 16 for u in small.units(Side.FEIND))
    assert all(u.men == 24 for u in big.units(Side.FEIND))          # größere Haufen bei großer Zahl
    assert len(big.units(Side.FEIND)) == 8
    assert all(u.count("peltast") >= 3 for u in big.units(Side.FEIND))   # gemischt


def test_mirror_army_scales_composition():
    mirror = scaled_army(default_army(), 150)
    assert mirror.total_men() == 150
    assert [g.name for g in mirror.groups] == ["Hopliten", "Peltasten", "Reiter"]
    assert mirror.groups[2].tiers[0].count == 40
    b = Battle(SIEDLUNG_OFFEN, random.Random(1), enemy_count=50, doctrine="spiegel")
    assert b.men(Side.FEIND) == 50 + 1          # dazu der Anführer
    assert all(u.y < 8 for u in b.units(Side.FEIND))     # Gegner im Norden
    assert all(u.y > 12 for u in b.units(Side.STADT))    # Angreifer im Süden


def test_horde_waits_then_charges():
    b = Battle(RAEUBERHORDE, random.Random(1))
    hop = b.units(Side.STADT)[0]
    b.command_hold()
    run(b, 3)
    assert not b.horde_awake and all(u.stance is Stance.HALTEN for u in b.units(Side.FEIND))
    b.command_move([hop], (8.0, 8.5))
    run(b, 12)
    assert b.horde_awake
    assert any(u.stance is Stance.ANGRIFF for u in b.units(Side.FEIND))


def test_settlement_defenders_hold_but_cavalry_charges():
    b = Battle(SIEDLUNG_OFFEN, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    b.command_move([cav], (4.5, 8.0))
    run(b, 6)
    enemy = {u.name: u for u in b.units(Side.FEIND)}
    assert enemy["Hopliten"].stance is Stance.PHALANX and enemy["Hopliten"].in_line
    assert enemy["Reiter"].stance is Stance.ANGRIFF


def test_closed_gate_blocks_and_ram_opens_it():
    b = Battle(SIEDLUNG_WALL, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    gx, gy = b.gate.center
    assert b.gate.closed and b.is_blocked(gx, gy, hop)
    assert not b.path_clear((gx, gy + 3), (gx, gy - 3), hop)
    assert b.command_ram_gate([hop]) == 0                # ohne Rammbock
    assert b.command_build([hop], "ram") == 1
    assert hop.build_kind == "ram" and hop.building == 0.0
    assert b.command_build([hop], "ram") == 0             # baut schon
    run(b, config.RAM_BUILD_TIME + 1)
    assert hop.engine == "ram" and hop.building is None
    assert hop.speed < UNIT_TYPES["schwer"].speed
    assert b.command_ram_gate([hop]) == 1
    run(b, 60)
    assert not b.gate.closed and b.gate.hp == 0.0
    assert not b.is_blocked(gx, gy, hop)
    assert any("aufgebrochen" in e for e in b.events)
    assert hop.engine is None and hop.speed == UNIT_TYPES["schwer"].speed   # Rammbock bleibt liegen
    assert len(b.debris) == 1
    assert abs(hop.x - gx) >= 1.2                                            # ist zur Seite getreten


def test_each_group_builds_its_own_engine():
    b = Battle(SIEDLUNG_WALL, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    assert b.command_build([hop, cav], "ram") == 2
    run(b, config.RAM_BUILD_TIME + 1)
    assert hop.engine == "ram" and cav.engine == "ram" and pelt.engine is None


def test_siege_tower_opens_a_crossing():
    b = Battle(SIEDLUNG_WALL, random.Random(1), ai="einfach", doctrine="spiegel")   # Mechanik, nicht Gegnerverhalten
    hop, pelt, cav = b.units(Side.STADT)
    assert b.command_tower_wall([cav], (13, 7)) == 0      # ohne Turm
    assert b.command_build([cav], "tower") == 1
    run(b, config.TOWER_BUILD_TIME + 1)
    assert cav.engine == "tower"
    assert b.command_tower_wall([cav], (13, 7)) == 1
    for _ in range(int(40 / DT)):
        b.update(DT)
        if b.crossings:
            break
    assert (13, 7) in b.crossings
    assert cav.engine is None                             # Turm steht jetzt am Wall
    assert len(b.towers) == 1 and abs(b.towers[0][0] - 13.5) < 1e-6 and b.towers[0][1] > 7.5
    run(b, 25)                                            # ein Mann nach dem anderen hinauf
    assert cav.fighting and b.on_wall(cav)                # Reiter stehen oben auf dem Wehrgang
    assert b.is_walker(hop) and (13, 7) in b.ladders_for(hop)   # Turm ist ein Aufstieg für alle Angreifer
    assert not b.can_step(cav, (13.5, 7.5), (13.5, 6.4)) or (13, 7) in b.ladders_for(cav)
    assert not b.can_step(cav, (10.5, 7.5), (10.5, 6.4))  # mitten auf dem Wall geht es nicht hinunter
    b.command_move([cav], (12.0, 3.0))                    # drüben: Abstieg nur über eine Leiter
    run(b, 35)
    assert cav.fighting and not b.on_wall(cav) and cav.y < 4.0


def test_losing_the_engine_group_loses_the_engine():
    b = Battle(SIEDLUNG_WALL, random.Random(1), doctrine="spiegel")
    hop = b.units(Side.STADT)[0]
    b.command_build([hop], "ram")
    run(b, config.RAM_BUILD_TIME + 1)
    assert hop.engine == "ram"
    hop.morale = 0.0
    b._morale(DT)
    assert hop.stance is Stance.FLUCHT and hop.engine is None


def test_raiders_build_a_ram_against_the_closed_gate():
    b = Battle(PALISADE, random.Random(1))
    assert b.gate.closed
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (5.5, 9.5), (10.5, 9.5))
    opened_at = None
    for _ in range(int(120 / DT)):
        b.update(DT)
        if opened_at is None and not b.gate.closed:
            opened_at = b.time
        if b.outcome:
            break
    assert any("Räuber bauen einen Rammbock" in e for e in b.events)
    assert opened_at is not None and 10 < opened_at < 60


def test_peltasts_throw_over_the_wall_only_from_the_walkway():
    b = Battle(PALISADE, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 8.0, 6.5                          # nördlich der Palisade (Reihe 8)
    pelt.x, pelt.y = 8.0, 9.6                              # südlich, am Boden
    assert not b.throw_clear(pelt, raider)
    pelt.x, pelt.y = 8.5, 8.5                              # auf dem Wehrgang: Torlücke ist bei 7/8, also 3.5
    pelt.x = 3.5
    raider.x = 3.5
    pelt.place_men()                                       # die Gruppe ist, wo ihre Männer sind
    assert b.on_wall(pelt) and b.throw_clear(pelt, raider)
    b.command_hold([pelt])
    b._ai_raiders = lambda: None
    run(b, 0.2)
    assert any(pr.target_id == raider.id for pr in b.projectiles)


def test_only_peltasts_of_wall_side_may_enter_the_wall():
    b = Battle(PALISADE, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    wall_tile = (3.5, 8.5)
    assert not b.is_blocked(*wall_tile, pelt)
    assert b.is_blocked(*wall_tile, hop)
    raider = b.units(Side.FEIND)[0]
    assert b.is_blocked(*wall_tile, raider)
    b.command_move([pelt], wall_tile)
    run(b, 22)                                             # einer nach dem anderen die Leiter hinauf
    assert b.on_wall(pelt) and not pelt.loose
    # Auf dem Wall: weiter werfen; von unten kommt niemand heran, von oben schlägt man hinunter
    raider.loose, raider.target, raider.target_id, raider.stance = False, None, None, Stance.HALTEN
    raider.x, raider.y = pelt.x, pelt.y + 1.0
    raider.place_men()
    assert not b._in_contact(raider, pelt)                # der Wehrgang ist erhöht
    assert b._in_contact(pelt, raider)
    rate_down, _ = b._melee_rate(pelt, raider)
    pelt_off = Lochos(99, Side.STADT, [men("peltast", 15)], pelt.x, pelt.y + 2.5)
    b.lochoi.append(pelt_off)
    raider.y = pelt_off.y + 1.0
    raider.place_men()
    rate_ground, _ = b._melee_rate(pelt_off, raider)
    assert 0 < rate_down < rate_ground * config.WALL_MELEE_FACTOR + 1e-9
    assert b._melee_rate(raider, pelt)[0] > 0 and not b._in_contact(raider, pelt)   # er käme heran, aber nicht hinauf


def test_enemy_peltasts_start_on_the_wall():
    b = Battle(SIEDLUNG_WALL, random.Random(1), doctrine="spiegel")
    pelt = next(u for u in b.units(Side.FEIND) if u.name == "Peltasten")
    assert b.on_wall(pelt)


def test_attack_outcomes():
    b = Battle(RAEUBERHORDE, random.Random(1), enemy_count=16)
    b.command_attack()
    run(b, 120)
    assert b.outcome == "sieg"
    b = Battle(SIEDLUNG_OFFEN, random.Random(1), enemy_count=150, army=army_of(GroupSpec("Wache", [Tier("leicht", 6)])))
    b.command_attack()
    run(b, 120)
    assert b.outcome == "niederlage"


# ------------------------------------------------------------- Leitern
def test_wall_is_entered_and_left_only_by_ladder():
    b = Battle(PALISADE, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    raider = b.units(Side.FEIND)[0]
    assert b.ladders == {(2, 8), (13, 8)}
    # Direkt von unten auf ein Wallstück ohne Leiter: nein; an der Leiter: ja
    assert not b.can_step(pelt, (5.5, 9.4), (5.5, 8.6))
    assert b.can_step(pelt, (2.5, 9.4), (2.5, 8.6))
    assert not b.can_step(hop, (2.5, 9.4), (2.5, 8.6))
    assert not b.can_step(raider, (2.5, 7.6), (2.5, 8.4))
    # Oben entlang, auch über das Torhaus
    pelt.x, pelt.y = 6.5, 8.5
    assert b.on_wall(pelt) and b.can_step(pelt, (6.5, 8.5), (7.5, 8.5))
    assert b.is_blocked(7.5, 8.5, hop) and b.is_blocked(7.5, 8.5, raider)
    # Herunter nur an der Leiter
    assert not b.can_step(pelt, (6.5, 8.5), (6.5, 9.4))
    pelt.x = 13.5
    assert b.can_step(pelt, (13.5, 8.5), (13.5, 9.4))


def test_peltasts_route_over_ladders():
    b = Battle(PALISADE, random.Random(1))
    b._volleys = lambda dt: None                            # keine Speere, kein Nahkampfwechsel
    b._ai_raiders = lambda: None                            # kein Rammbock: das Torhaus bleibt begehbar
    hop, pelt, cav = b.units(Side.STADT)
    goal, final = b.route(pelt, (5.5, 8.5))
    assert final is False and goal[0] == 2.5 and goal[1] >= 8.5   # erst zur Leiter (bzw. an ihren Fuß)
    b.command_move([pelt], (5.5, 8.5))
    run(b, 24)
    assert b.on_wall(pelt) and abs(pelt.x - 5.5) < 0.3
    b.command_move([pelt], (10.5, 8.5))                    # oben über das Tor
    run(b, 6)
    assert b.on_wall(pelt) and abs(pelt.x - 10.5) < 0.3
    b.command_move([pelt], (12.0, 11.0))                   # hinunter über die rechte Leiter
    run(b, 24)
    assert not b.on_wall(pelt) and abs(pelt.x - 12.0) < 0.3
    # Am Boden führt der Weg nach Norden nur durchs Tor, nicht durch die Palisade
    goal, final = b.route(pelt, (12.0, 5.0))
    assert final is False


# ------------------------------------------------------- Einzelne Männer
def test_men_flow_through_the_gate_individually():
    b = Battle(SIEDLUNG_WALL, random.Random(1), ai="einfach", doctrine="spiegel")
    b._ai_defenders = lambda: None                            # Mechanik, nicht Gegnerverhalten
    hop, pelt, cav = b.units(Side.STADT)
    b.gate.closed = False
    b.gate.hp = 0.0
    b.command_move([hop], (8.0, 3.5))
    through = False
    for _ in range(int(30 / DT)):
        b.update(DT)
        for m in hop.all_men():
            assert b.cell(m.x, m.y) not in b.blocked            # niemand steckt in der Palisade
        if all(m.y < 7.0 for m in hop.all_men()):
            through = True                                      # alle sind hindurch (bevor die Linie drüben sie bricht)
            break
    assert through


def test_cavalry_dismounts_for_siege_work_and_before_ladders():
    b = Battle(SIEDLUNG_WALL, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    assert cav.speed == UNIT_TYPES["reiter"].speed
    b.command_build([cav], "tower")
    assert cav.mounted_men() == [] and len(b.horses) == 1 and b.horses[0][2] == 20
    assert cav.speed == pytest.approx(config.DISMOUNTED_SPEED)
    assert cav.cavalry_share() == 0.0                           # kein Reiterbonus mehr
    run(b, config.TOWER_BUILD_TIME + 1)
    assert cav.speed == pytest.approx(config.DISMOUNTED_SPEED * config.TOWER_SPEED_FACTOR)


def test_tower_is_one_way_up_from_outside():
    b = Battle(SIEDLUNG_WALL, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    b.crossings.add((12, 7))
    assert b.can_step(hop, (12.5, 8.6), (12.5, 7.5))            # von außen hinauf
    assert b.can_step(hop, (12.5, 7.5), (12.5, 8.6))            # außen wieder hinunter
    assert not b.can_step(hop, (12.5, 7.5), (12.5, 6.4))        # nach innen nur über Leitern
    assert b.can_step(hop, (13.5, 7.5), (13.5, 6.4))
    assert (12, 7) not in b.ladders_for(hop, (12.5, 7.5), (12.0, 3.0))
    assert (12, 7) in b.ladders_for(hop, (12.5, 7.5), (12.0, 12.0))


# ------------------------------------------------- Überqueren und Aufsitzen
def test_crossing_dissolves_formation_and_reforms_inside():
    b = Battle(SIEDLUNG_WALL, random.Random(1), ai="einfach", doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    enemy_pelt = next(u for u in b.units(Side.FEIND) if u.name == "Peltasten")
    b.crossings.add((12, 7))
    b.update(DT)
    assert not enemy_pelt.loose                              # wer oben steht und bleibt, ist formiert
    b.command_line([hop], (5.0, 13.0), (11.0, 13.0))
    run(b, 6)
    assert hop.in_line
    b.command_move([hop], (10.0, 3.5))
    seen_loose, max_up = False, 0
    for _ in range(int(150 / DT)):
        b.update(DT)
        if hop.loose:
            seen_loose = True
            assert hop.stance is Stance.HALTEN and not hop.in_phalanx
        max_up = max(max_up, sum(1 for m in hop.all_men() if b.is_wall_cell(b.cell(m.x, m.y), True)))
        for m in hop.all_men():
            assert b.cell(m.x, m.y) not in b.blocked or b.is_wall_cell(b.cell(m.x, m.y), True)
        if seen_loose and not hop.loose and hop.target is None:
            break
    assert seen_loose and max_up >= 1                        # Mann für Mann über den Wehrgang
    assert not hop.loose and all(m.y < 6.5 for m in hop.all_men())
    assert any("neu gebildet" in e for e in b.events)


def test_no_phalanx_bonus_on_the_wall():
    b = Battle(PALISADE, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    raider = b.units(Side.FEIND)[0]
    pelt.x, pelt.y = 5.5, 8.5
    pelt.stance, pelt.in_line = Stance.PHALANX, True
    raider.x, raider.y = 5.5, 7.6
    assert b.on_wall(pelt) and pelt.in_phalanx
    assert b._formed(pelt) is False
    mod, _ = b._defense_mod(raider, pelt)
    assert mod == 1.0


def test_dismounted_cavalry_remounts_at_their_horses():
    b = Battle(SIEDLUNG_WALL, random.Random(1), doctrine="spiegel")
    hop, pelt, cav = b.units(Side.STADT)
    b.command_build([cav], "ram")
    assert cav.mounted_men() == []
    run(b, config.RAM_BUILD_TIME + 1)
    assert cav.engine == "ram"
    hx, hy, n = b.horses[0]
    b.command_move([cav], (hx, hy))                           # mit Gerät: kein Aufsitzen
    run(b, 12)
    assert cav.engine == "ram" and cav.mounted_men() == []
    cav.engine = None                                          # Rammbock abgelegt
    b.command_move([cav], (hx + 2.0, hy))
    run(b, 4)
    b.command_move([cav], (hx, hy))
    run(b, 6)
    assert len(cav.mounted_men()) == cav.men and cav.speed == UNIT_TYPES["reiter"].speed
    assert b.horses == []


def test_walkway_gap_is_crossed_via_ladders():
    b = Battle(PALISADE, random.Random(1), ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    hop, pelt, cav = b.units(Side.STADT)
    b.command_move([pelt], (4.5, 8.5))
    run(b, 20)
    assert b.on_wall(pelt) and not pelt.loose
    b.gate.hp = 0.0
    b.gate.closed = False                                  # Tor offen: Lücke im Wehrgang
    goal, final = b.route(pelt, (11.5, 8.5))
    assert not final and goal == (2.5, 8.5)                # erst zur westlichen Leiter hinunter
    b.command_move([pelt], (11.5, 8.5))
    run(b, 45)
    assert b.on_wall(pelt) and abs(pelt.x - 11.5) < 0.4 and not pelt.loose
    assert all(b.cell(m.x, m.y)[0] >= 9 for m in pelt.all_men())


def test_men_cannot_walk_through_an_enemy_phalanx():
    b = Battle(PALISADE, random.Random(1), ai="einfach")
    b._ai_raiders = lambda: None
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (0.0, 10.2), (4.5, 10.2))       # Phalanx vom Kartenrand bis unter die Leiter, Front Nord
    b.command_move([pelt, cav], (12.0, 14.0))
    run(b, 8)
    assert hop.in_phalanx
    b.crossings.add((1, 8))                                # ein Turm steht am Wall
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 1.5, 6.0
    raider.place_men()
    raider.stance = Stance.RAUB
    raider.target = (2.5, 13.5)                            # ein Haus hinter der Phalanx
    b._ai_raiders = lambda: None
    start = raider.men
    for _ in range(int(60 / DT)):
        b.update(DT)
        for m in raider.all_men():
            assert hop.rect_distance(m.pos) > 0.0 or hop.men == 0          # niemand steht in der Formation
        assert hop.rect_distance(raider.pos) > 0.0
        if not raider.alive:
            break
    assert raider.men < start                              # die Phalanx hat sie empfangen


def test_climbing_is_a_dense_column():
    b = Battle(PALISADE, random.Random(1), ai="einfach")
    b._ai_raiders = lambda: None
    hop, pelt, cav = b.units(Side.STADT)
    b.command_move([pelt], (3.5, 8.5))
    run(b, 12)
    assert b.on_wall(pelt) and not pelt.loose              # 15 Mann in unter zwölf Sekunden oben


def test_climbing_men_take_their_places_instead_of_one_point():
    b = Battle(PALISADE, random.Random(1), ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    hop, pelt, cav = b.units(Side.STADT)
    b.command_move([pelt], (4.5, 8.5))
    spread_up = 0.0
    for _ in range(int(20 / DT)):
        b.update(DT)
        up = [m for m in pelt.all_men() if b.is_wall_cell(b.cell(m.x, m.y), True)]
        if len(up) >= 6:
            spread_up = max(spread_up, max(m.x for m in up) - min(m.x for m in up))
    assert spread_up >= 0.6                                # schon beim Klettern in einer Reihe längs des Walls
    assert b.on_wall(pelt) and pelt.file
    xs = [m.x for m in pelt.all_men()]
    assert max(xs) - min(xs) >= 1.5 and all(abs(m.y - 8.5) < 0.2 for m in pelt.all_men())
    b.command_move([pelt], (4.5, 11.0))                    # hinunter: sofort in die Aufstellung
    spread_down = 0.0
    for _ in range(int(25 / DT)):
        b.update(DT)
        down = [m for m in pelt.all_men() if m.y > 9.6]
        if 4 <= len(down) < pelt.men:
            spread_down = max(spread_down, max(m.x for m in down) - min(m.x for m in down))
    assert spread_down >= 0.4                              # die ersten unten stehen schon verteilt
    assert not pelt.loose and not pelt.file


# --------------------------------------------------------- Handgemenge
def melee_pair():
    """Eine Phalanx (Front Nord) mit Peltasten dahinter, ein Räuberhaufen dicht vor der Front."""
    scn = raid(16, (8.0, 3.0))
    army = army_of(GroupSpec("Hopliten", [Tier("schwer", 14), Tier("mittel", 14)]),
                   GroupSpec("Peltasten", [Tier("peltast", 12)]))
    b = Battle(scn, random.Random(0), army=army, ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    hop, pelt = b.units(Side.STADT)
    raider = b.units(Side.FEIND)[0]
    b.command_line([hop], (6.0, 9.0), (10.0, 9.0))
    b.command_line([pelt], (6.5, 10.2), (9.5, 10.2))
    run(b, 6)
    assert hop.in_phalanx
    raider.x, raider.y = 8.0, 9.0 - hop.half_d - raider.half_d - 0.3
    raider.place_men()
    raider.stance = Stance.HALTEN
    raider.target = None
    run(b, 1)
    assert hop.engaged and raider.engaged
    return b, hop, pelt, raider


def test_men_in_melee_are_bound_and_the_phalanx_cannot_turn_in_place():
    b, hop, pelt, raider = melee_pair()
    assert 10 <= len(hop.bound_men()) < hop.men           # wer dem Feind gegenübersteht, ist gebunden
    assert not pelt.bound_men()                           # die Peltasten dahinter nicht
    stands = {id(m): m.stand for m in hop.bound_men() if m.stand}
    b.command_line([hop], (8.0, 9.0), (8.0, 11.0))        # Front nach Osten drehen, Zentrum bleibt in der Leine
    run(b, 4)                                             # (nach etwa sechs Sekunden brechen die Räuber)
    moved = [id(m) for m in hop.all_men() if id(m) in stands and dist_of_pt(m.pos, stands[id(m)]) > config.BOUND_SHUFFLE + 0.1]
    assert not moved                                      # gebundene Männer rücken höchstens nach, sie gehen nicht weg
    assert not hop.in_phalanx                             # solange Gebundene fehlen, keine Phalanx
    b.command_line([pelt], (9.5, 10.2), (6.5, 10.2))      # die Peltasten dürfen sich umformieren
    run(b, 6)
    assert pelt.in_phalanx


def test_men_are_bound_by_enemy_men_not_by_the_enemy_rectangle():
    """Gebunden ist, wer einen feindlichen Mann in Reichweite hat; ein Rechteck, in
    dem niemand steht, bindet nicht."""
    b, hop, pelt, raider = melee_pair()
    for m in hop.bound_men():
        assert min(dist_of_pt(m.stand, o.pos) for o in raider.all_men()) <= config.MAN_RELEASE_REACH
    for o in raider.all_men():                            # die Räuber weichen Mann für Mann zurück, das Rechteck bleibt
        o.y -= 1.5
    b._move_men(DT)
    assert not hop.bound_men()


def test_jostling_is_only_a_picture():
    """Im Handgemenge drängen die Männer im Bild an ihren Gegner, die Phalanx hält
    ihre Reihen; die Schlacht rechnet dasselbe wie ohne das Bild."""
    def fight(show: bool):
        b = Battle(OFFENE_SIEDLUNG, random.Random(1))
        b.command_hold()
        if not show:
            b._show = lambda dt: None
        moved = 0
        before: dict[int, float] = {}
        for _ in range(int(25 / DT)):
            b.update(DT)
            for u in b.lochoi:
                for m in u.all_men():
                    off = (m.show_dx ** 2 + m.show_dy ** 2) ** 0.5
                    assert off <= config.JOSTLE_MAX + 1e-6
                    if u.in_phalanx:
                        assert off <= before.get(id(m), 0.0) + 1e-9     # in der Phalanx drängt keiner vor
                    moved += off > 0.05
                    before[id(m)] = off
        return b, moved
    shown, moved = fight(True)
    plain, _ = fight(False)
    assert moved > 0
    assert [(m.x, m.y, m.hp) for u in shown.lochoi for m in u.all_men()] == \
        [(m.x, m.y, m.hp) for u in plain.lochoi for m in u.all_men()]


def test_a_felt_hit_flashes_and_the_fallen_leave_a_mark():
    b, hop, pelt, raider = melee_pair()
    victim = raider.all_men()[0]
    victim.flash = 0.0
    raider.hit_man(victim, 0.1 * victim.kind.hp)          # ein Kratzer blitzt nicht
    assert victim.flash == 0.0
    raider.hit_man(victim, 0.3 * victim.kind.hp)          # zusammen ein spürbarer Treffer
    assert victim.flash > 0.0
    pos = victim.pos
    raider.hit_man(victim, victim.hp + 1.0)
    b.update(DT)
    assert any(p == pos for p, _ in b.fallen_marks)
    run(b, config.FALLEN_MARK_TIME + 0.5)
    assert not any(p == pos for p, _ in b.fallen_marks)
    assert victim.flash == 0.0 or victim not in raider.all_men()


def test_the_palisade_covers_the_walkway_against_spears_from_outside():
    """Wer auf dem Wehrgang steht, ist gegen Speere von außen gedeckt; von innen
    (der Seite der Häuser) oder unten auf dem Boden nicht."""
    from game.battle import Projectile
    b = Battle(PALISADE, random.Random(1))
    target = next(u for u in b.units(Side.STADT) if u.name == "Peltasten")   # wer auf den Wehrgang darf (ohne Hoplitenschild)
    man = target.all_men()[0]

    def hit(at, origin):
        man.x, man.y = at
        man.hp = man.kind.hp
        b.projectiles = [Projectile(origin[0], origin[1], man.x, man.y, target.id, 0.2, 0.0, 0.1, man)]
        for u in b.lochoi:                                # nur der eine Speer zählt
            u.volley_timer = 99.0
        b._volleys(0.2)
        return man.kind.hp - man.hp

    walkway = (3.5, 8.5)
    outside, inside = (3.5, 6.0), (3.5, 11.0)
    full = hit(walkway, inside)
    assert full > 0.0
    assert hit(walkway, outside) == pytest.approx(config.WALL_COVER_FACTOR * full)
    assert hit((3.5, 9.5), outside) == pytest.approx(hit((3.5, 9.5), inside))       # unten am Boden: keine Deckung


def test_engaged_groups_move_slowly():
    b, hop, pelt, raider = melee_pair()
    y0 = hop.y
    b.command_move([hop], (8.0, 13.0))
    run(b, 2)
    slow = hop.y - y0
    pelt_y0 = pelt.y
    b.command_move([pelt], (8.0, 14.0))
    run(b, 2)
    assert slow < 0.45 * (pelt.y - pelt_y0)               # im Kontakt nur ein Drittel so schnell


def test_disengaging_releases_the_men_and_costs():
    b, hop, pelt, raider = melee_pair()
    b.command_move([hop], (8.0, 14.0))
    bound_before = len(hop.bound_men())
    released_at = None
    for _ in range(int(20 / DT)):
        b.update(DT)
        if hop.disengage_until > b.time:
            released_at = b.time
            break
    assert released_at is not None and 2.0 < released_at - 7.0 < 6.0   # erst nach der Leine, im Kriechtempo
    assert len(hop.bound_men()) < bound_before
    mod, arc_name = b._defense_mod(raider, hop)
    assert arc_name == "rear" and mod == pytest.approx(config.DISENGAGE_DAMAGE)
    run(b, config.DISENGAGE_TIME + 10.0)                  # um die eigenen Peltasten herum, nicht durch sie
    assert hop.disengage_until <= b.time                  # danach vorbei
    assert b._gap(hop, pelt) > 0.0


def test_phalanx_bonus_waits_until_every_man_stands():
    b = Battle(raid(16, (8.0, 2.0)), random.Random(0), army=army_of(GroupSpec("H", [Tier("schwer", 20)])), ai="einfach")
    b._ai_raiders = lambda: None
    hop = b.units(Side.STADT)[0]
    b.command_line([hop], (5.0, 9.0), (11.0, 9.0))
    for _ in range(int(20 / DT)):
        b.update(DT)
        if hop.in_line:
            break
    assert hop.in_phalanx and hop.on_slots(config.SLOT_TOLERANCE)
    for m in hop.all_men()[:5]:
        m.x, m.y = m.x + 1.0, m.y                          # ein Viertel der Männer steht falsch
    hop.in_line = False
    b.update(DT)
    assert not hop.in_line
    run(b, 3)
    assert hop.in_line                                    # sie sind zurück auf ihren Plätzen


def dist_of_pt(a, b) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


# ---------------------------------------------------------- Sturmangriff
def charge_setup(kind: str, facing=(0.0, -1.0), stance=Stance.HALTEN, n: int = 16):
    """Reiter des Spielers mit Anlauf von Osten gegen eine stehende Gegnergruppe."""
    scn = raid(n, (8.0, 9.0))
    army = army_of(GroupSpec("Reiter", [Tier("reiter", 12)]))
    b = Battle(scn, random.Random(0), army=army, ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    cav = b.units(Side.STADT)[0]
    foe = b.units(Side.FEIND)[0]
    foe.rows = arrange(men(kind, n), 8)
    foe.men_start = n
    foe.x, foe.y = 8.0, 9.0
    foe.facing = facing
    foe.stance = stance
    foe.target = None
    foe.place_men()
    if stance is Stance.PHALANX:
        foe.in_line = True
    cav.x, cav.y = 13.5, 9.0
    cav.facing = (-1.0, 0.0)
    cav.place_men()
    b.command_attack_target([cav], foe)
    return b, cav, foe


def test_charge_pushes_men_and_slows_the_riders():
    b, cav, foe = charge_setup("raeuber")
    before = {id(m): m.pos for m in foe.all_men()}
    hp_before = sum(m.hp for m in foe.all_men())
    for _ in range(int(8 / DT)):
        b.update(DT)
        if any("stoßen" in e for e in b.events):
            break
    assert any("in die Flanke" in e for e in b.events), b.events[-3:]
    pushed = [m for m in foe.all_men() if id(m) in before and m.x - before[id(m)][0] < -0.2]   # nach Westen gestoßen
    assert len(pushed) >= 4
    assert sum(m.hp for m in foe.all_men()) < hp_before
    assert foe.morale < 1.0
    assert cav.charge_slow_until > b.time and cav.runup == 0.0


def test_charge_into_a_phalanx_front_impales_the_riders():
    b, cav, foe = charge_setup("schwer", facing=(1.0, 0.0), stance=Stance.PHALANX)
    before = {id(m): m.pos for m in foe.all_men()}
    for _ in range(int(8 / DT)):
        b.update(DT)
        if any("Speere" in e for e in b.events):
            break
    assert any("rennen in die Speere" in e for e in b.events), b.events[-3:]
    assert cav.men < 12                                            # Reiter aufgespießt
    assert all(dist_of_pt(m.pos, before[id(m)]) < 0.05 for m in foe.all_men())   # niemand weggestoßen


def test_light_men_fly_farther_than_heavy_ones():
    def pushed_distance(kind: str) -> float:
        b, cav, foe = charge_setup(kind)
        before = {id(m): m.pos for m in foe.all_men()}
        for _ in range(int(8 / DT)):
            b.update(DT)
            if any("stoßen" in e for e in b.events):
                break
        moved = [dist_of_pt(m.pos, before[id(m)]) for m in foe.all_men() if id(m) in before]
        return max(moved) if moved else 0.0
    assert pushed_distance("peltast") > pushed_distance("schwer") * 1.8


def test_no_charge_without_run_up():
    b, cav, foe = charge_setup("raeuber")
    cav.x, cav.y = foe.x + foe.half_w + cav.half_d + 0.4, 9.0       # steht schon dicht daneben
    cav.place_men()
    run(b, 3)
    assert not any("stoßen" in e for e in b.events)
    assert cav.engaged



# ------------------------------------------------------------------ Moral
def test_city_group_breaks_after_heavy_losses():
    b = Battle(raid(48, (8.0, 3.0)), random.Random(0), army=army_of(GroupSpec("H", [Tier("mittel", 30)])), ai="einfach")
    b._ai_raiders = lambda: None
    hop = b.units(Side.STADT)[0]
    hop.x, hop.y = 8.0, 9.0
    hop.stance = Stance.HALTEN
    hop.place_men()
    fallen_at_rout = None
    for i in range(40):
        hop.take_damage_men(hop.all_men()[:3], 2.2 * 2, b.rng)         # zwei Männer je Schlag
        b._after_hit(hop, 2, "flank", 4.4)
        b._morale(DT)
        if hop.stance is Stance.FLUCHT:
            fallen_at_rout = 30 - hop.men
            break
    assert fallen_at_rout is not None
    assert 8 <= fallen_at_rout <= 16                       # bricht zwischen einem Viertel und der Hälfte


def test_routing_neighbours_shake_the_line():
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0), army=army_of(
        GroupSpec("A", [Tier("mittel", 20)]), GroupSpec("B", [Tier("mittel", 20)])), ai="einfach")
    b._ai_raiders = lambda: None
    a, c = b.units(Side.STADT)
    a.x, a.y, c.x, c.y = 7.0, 9.0, 9.0, 9.0
    a.morale = config.ROUT_THRESHOLD_CITY - 0.01
    b._morale(DT)
    assert a.stance is Stance.FLUCHT
    assert c.morale < 1.0                                  # Ansteckung


def test_hopeless_battle_drains_morale():
    b = Battle(raid(64, (8.0, 3.0)), random.Random(0), army=army_of(GroupSpec("H", [Tier("mittel", 20)])), ai="einfach")
    b._ai_raiders = lambda: None
    hop = b.units(Side.STADT)[0]
    for m in hop.all_men()[:14]:
        m.hp = 0.0
    hop.bury()                                             # nur noch 6 von 20, der Feind steht komplett
    assert b._hopeless(Side.STADT) and not b._hopeless(Side.FEIND)
    m0 = hop.morale
    b._morale(1.0)
    assert hop.morale < m0



# ------------------------------------------------- Formationen und Befehle
def test_formations_geometry_and_arcs():
    u = Lochos(1, Side.STADT, arrange(men("mittel", 20), 7), 5.0, 5.0)
    u.formation = "o"
    assert u.arc_to((5.0, 7.0)) == "front" and u.arc_to((7.0, 5.0)) == "front"
    r = u.ring_radius()
    assert all(abs(dist_of_pt(p, (5.0, 5.0)) - r) < 1e-6 for _, p in u.slots())
    u.formation = "keil"
    assert u.wedge_rows() == 6
    tip = min(u.slots(), key=lambda mp: mp[1][1])[1]
    assert abs(tip[0] - 5.0) < 1e-6                                       # die Spitze liegt vorn in der Mitte
    assert u.formation_options() == ("linie", "o")
    c = Lochos(2, Side.STADT, [men("reiter", 8)], 5.0, 5.0)
    assert c.formation_options() == ("linie", "keil")


def test_ring_is_strong_all_round_but_weaker_in_front():
    b = static_line(raider_y=8.8, n_raiders=1)
    hop = b.units(Side.STADT)[2]                                           # die östliche Gruppe: dort endet die Linie
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = hop.x, hop.y - 1.1
    front_mod, _ = b._defense_mod(raider, hop)
    raider.x, raider.y = hop.x + hop.half_w + 0.5, hop.y                  # in der Flanke
    flank_mod, arc_name = b._defense_mod(raider, hop)
    assert arc_name == "flank" and flank_mod > front_mod
    hop.formation = "o"
    hop.place_men()
    ring_mod, arc_name = b._defense_mod(raider, hop)
    assert arc_name == "front" and front_mod < ring_mod < flank_mod


def test_hold_forms_a_phalanx_in_place_and_line_resets_formation():
    b = Battle(raid(16, (8.0, 2.0)), random.Random(0), army=army_of(GroupSpec("H", [Tier("mittel", 20)])), ai="einfach")
    b._ai_raiders = lambda: None
    hop = b.units(Side.STADT)[0]
    b.command_move([hop], (8.0, 12.0))
    run(b, 3)
    pos = hop.pos
    b.command_hold([hop])
    run(b, 2)
    assert hop.in_phalanx and dist_of_pt(hop.pos, pos) < 0.2
    b.command_formation([hop], "o")
    assert hop.formation == "o" and not hop.in_line
    run(b, 3)
    assert hop.in_phalanx
    b.command_line([hop], (6.0, 12.0), (10.0, 12.0))
    assert hop.formation == "linie"


def test_peltasts_skirmish_keep_distance_then_charge_when_empty():
    b = Battle(raid(16, (8.0, 4.0)), random.Random(0), army=army_of(GroupSpec("P", [Tier("peltast", 12)])), ai="einfach")
    b._ai_raiders = lambda: None
    pelt = b.units(Side.STADT)[0]
    raider = b.units(Side.FEIND)[0]
    raider.stance = Stance.HALTEN
    raider.target = None
    pelt.x, pelt.y = 8.0, 12.0
    pelt.place_men()
    b.command_attack([pelt])
    assert pelt.stance is Stance.PLAENKELN
    thrown = False
    for _ in range(int(12 / DT)):                                         # danach wären die Speere ohnehin verschossen
        b.update(DT)
        raider.x, raider.y = raider.x, raider.y + 0.02                    # der Räuber rückt langsam nach
        raider.place_men()
        if b.projectiles:
            thrown = True
        assert raider.rect_distance(pelt.pos) >= config.SKIRMISH_NEAR - 0.7 or pelt.ammo() == 0
    assert thrown
    for m in pelt.all_men():
        m.ammo = 0
    run(b, 1)
    assert pelt.stance is Stance.ANGRIFF                                    # ohne Speere in den Nahkampf


def test_cavalry_free_attack_charges_the_flank_and_pulls_back():
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0), army=army_of(GroupSpec("R", [Tier("reiter", 16)])), ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    cav = b.units(Side.STADT)[0]
    foe = b.units(Side.FEIND)[0]
    foe.rows = arrange(men("schwer", 24), 12)
    foe.men_start = 24
    foe.x, foe.y, foe.facing, foe.stance, foe.in_line = 8.0, 7.0, (0.0, 1.0), Stance.PHALANX, True
    foe.target = None
    foe.place_men()
    cav.x, cav.y = 8.0, 12.0
    cav.place_men()
    b.command_attack([cav])
    assert cav.mode == "sturm"
    arcs, pulled = set(), False
    for _ in range(int(40 / DT)):
        b.update(DT)
        if foe.last_arc:
            arcs.add(foe.last_arc)
        if cav.hitrun_until > b.time:
            pulled = True
        if pulled and "flank" in arcs | {"rear"}:
            break
    assert "flank" in arcs or "rear" in arcs                              # nicht in die Front
    # nach dem Stoß: von einer stehenden Phalanx abgesetzt, sonst steckt der Stoß in der
    # aufgebrochenen Formation und die Reiter bleiben im Handgemenge
    assert pulled                                                          # nach dem Stoß abgesetzt
    assert cav.men >= 12                                                   # nicht in den Speeren geblieben
    run(b, 4)
    assert b._gap(cav, foe) > 1.5                                          # und wirklich weggeritten


def test_foot_charge_pushes_but_never_a_phalanx_front():
    b, cav, foe = charge_setup("raeuber")
    hop = Lochos(50, Side.STADT, arrange(men("mittel", 16), 8), 13.5, 9.0, facing=(-1.0, 0.0))
    b.lochoi.append(hop)
    cav.x, cav.y = 13.5, 15.0                                             # die Reiter aus dem Weg
    cav.stance = Stance.HALTEN
    cav.target = None
    b.command_attack_target([hop], foe)
    for _ in range(int(8 / DT)):
        b.update(DT)
        if any("stürmen" in e for e in b.events):
            break
    assert any("stürmen in die Flanke" in e for e in b.events), b.events[-3:]
    b2, cav2, foe2 = charge_setup("schwer", facing=(1.0, 0.0), stance=Stance.PHALANX)
    hop2 = Lochos(51, Side.STADT, arrange(men("mittel", 16), 8), 13.5, 9.0, facing=(-1.0, 0.0))
    b2.lochoi.append(hop2)
    cav2.stance = Stance.HALTEN
    cav2.target = None
    cav2.x, cav2.y = 13.5, 15.0
    b2.command_attack_target([hop2], foe2)
    run(b2, 8)
    assert not any("stürmen" in e or "Speere" in e for e in b2.events)  # zu Fuß gegen die Front: nur Handgemenge


def test_wedge_hits_fewer_men_harder():
    def charge(formation: str):
        b, cav, foe = charge_setup("raeuber")
        cav.formation = formation
        cav.place_men()
        before = {id(m): m.pos for m in foe.all_men()}
        for _ in range(int(8 / DT)):
            b.update(DT)
            if any("stoßen" in e for e in b.events):
                break
        moved = [dist_of_pt(m.pos, before[id(m)]) for m in foe.all_men() if id(m) in before and dist_of_pt(m.pos, before[id(m)]) > 0.1]
        return len(moved), max(moved) if moved else 0.0
    n_line, far_line = charge("linie")
    n_wedge, far_wedge = charge("keil")
    assert n_wedge < n_line and far_wedge > far_line


def test_mixed_groups_form_nested_rings_with_alternating_rows():
    rows = [men("schwer", 8), men("mittel", 8), men("leicht", 8), men("reiter", 6), men("peltast", 6)]
    for t, row in enumerate(rows):
        for m in row:
            m.tier = t
    u = Lochos(1, Side.STADT, rows, 5.0, 5.0)
    layers = u.layers()
    assert [len(l) for l in layers] == [24, 6, 6]
    assert [m.kind.key for m in layers[0][:6]] == ["schwer", "mittel", "leicht"] * 2   # Reihen wechseln ab
    assert all(m.kind.cavalry for m in layers[1]) and all(m.kind.ranged for m in layers[2])
    u.formation = "o"
    r_out, r_cav, r_pelt = u.ring_radii()
    assert r_out > r_cav > r_pelt > 0.1
    for m, p in u.slots():
        want = r_pelt if m.kind.ranged else (r_cav if m.kind.cavalry else r_out)
        assert abs(dist_of_pt(p, (5.0, 5.0)) - want) < 1e-6
    assert u.formation_options() == ("linie", "o")
    p = Lochos(2, Side.STADT, [men("peltast", 6), men("reiter", 4)], 5.0, 5.0)
    assert p.formation_options() == ("linie",) and len(p.layers()) == 2   # ohne Schildwand kein Kreis


def test_mixed_group_of_the_muster_becomes_a_verband():
    """Eine Gruppe mit mehreren Gattungen in der Aufstellung wird in der Schlacht je
    Gattung eine eigene Gruppe; zusammen bilden sie einen Verband in Schlachtordnung
    (Hopliten vorn, Reiter am Flügel, Peltasten dahinter). Im freien Angriff geht jede
    in ihrem Tempo los, der Verband bleibt."""
    army = Army(groups=[GroupSpec("Gemischt", [Tier("schwer", 10), Tier("mittel", 10), Tier("peltast", 6), Tier("reiter", 6)])])
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0), army=army, ai="einfach")
    b._ai_raiders = lambda: None
    parts = b.units(Side.STADT)
    assert sorted(p.name for p in parts) == ["Hopliten", "Peltasten", "Reiter"]
    assert not any(b.mixed(p) for p in parts)
    (v,) = b.verbaende
    by = {p.name: p for p in parts}
    assert v.name == "Gemischt" and v.rows == [[by["Hopliten"].id, by["Reiter"].id], [by["Peltasten"].id]]
    assert by["Peltasten"].y > by["Hopliten"].y                               # dahinter (die Front schaut nach Norden)
    assert by["Reiter"].x > by["Hopliten"].x                                  # rechts daneben
    b.command_attack(parts)
    assert by["Hopliten"].stance is Stance.ANGRIFF and by["Peltasten"].stance is Stance.PLAENKELN
    assert by["Reiter"].stance is Stance.ANGRIFF and by["Reiter"].mode == "sturm"
    start = {n: p.y for n, p in by.items()}
    run(b, 3)
    moved = {n: start[n] - p.y for n, p in by.items()}
    assert moved["Reiter"] > moved["Hopliten"] > 0 and moved["Peltasten"] > 0     # jede in ihrem Tempo nach vorn
    assert b.verbaende == [v] and b.fallen(Side.STADT) == 0


# ------------------------------------------------------------ Schwung der Reiter
def open_field_cavalry():
    b = Battle(raid(16, (8.0, 1.0)), random.Random(0), army=army_of(GroupSpec("R", [Tier("reiter", 12)])), ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    cav = b.units(Side.STADT)[0]
    cav.x, cav.y = 8.0, 14.0
    cav.place_men()
    return b, cav


def test_cavalry_accelerates_turns_in_an_arc_and_brakes():
    b, cav = open_field_cavalry()
    b.command_move([cav], (8.0, 6.0))
    run(b, 0.2)
    assert 0.0 < cav.vel < cav.speed and 14.0 - cav.y < cav.speed * 0.2      # fährt an statt sofort zu galoppieren
    run(b, 1.3)
    assert abs(cav.vel - cav.speed) < 1e-6 and cav.heading == (0.0, -1.0)
    y_turn, x_turn = cav.y, cav.x
    b.command_move([cav], (14.0, y_turn))                                    # im Galopp nach Osten
    run(b, 0.3)
    assert cav.y < y_turn - 0.3 and cav.x > x_turn + 0.2                     # Bogen: noch nach Norden, schon nach Osten
    assert cav.vel > 2.0                                                     # ohne anzuhalten
    run(b, 4.0)
    assert dist_of_pt(cav.pos, (14.0, y_turn)) < 0.3 and cav.vel == 0.0
    b.command_move([cav], (cav.x, cav.y - 3.0))
    speeds = []
    for _ in range(int(4 / DT)):
        b.update(DT)
        speeds.append(cav.vel)
        if cav.target is None:
            break
    drops = [a - c for a, c in zip(speeds, speeds[1:])]
    assert max(drops[:-1]) <= config.CAVALRY_BRAKE * DT + 1e-6               # kein Stopp aus vollem Galopp
    assert drops[-1] < 1.2                                                   # der letzte Schritt ist nur noch ein Rest (Schrittgeschwindigkeit)
    assert any(0.5 < v < 2.5 for v in speeds[-20:])                          # es wird ausgerollt


def test_charging_cavalry_rides_into_the_enemy_before_it_stops():
    b, cav, foe = charge_setup("raeuber")
    x_contact = None
    for _ in range(int(8 / DT)):
        b.update(DT)
        if cav.engaged and x_contact is None:
            x_contact = cav.x
        if x_contact is not None and cav.vel == 0.0:
            break
    assert x_contact is not None
    assert x_contact - cav.x > 0.3 and cav.ride_in > 0.3                     # weiter nach Westen in den Feind hinein
    assert cav.ride_in <= config.CHARGE_PENETRATION + 1e-6


# ------------------------------------------------------------ Wenden im Stand
def standing_group(kind: str, n: int = 12, width: int = 6):
    scn = raid(16, (8.0, 1.0))
    army = army_of(GroupSpec("G", [Tier(kind, n)]))
    b = Battle(scn, random.Random(0), army=army, ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    u = b.units(Side.STADT)[0]
    u.rows = arrange(u.all_men(), width)
    u.x, u.y, u.facing = 8.0, 12.0, (0.0, -1.0)
    u.place_men()
    return b, u


def same_men(a, b) -> int:
    return len(set(map(id, a)) & set(map(id, b)))


@pytest.mark.parametrize("kind", ["reiter"])
def test_about_turn_swaps_rows_so_nobody_crosses_the_block(kind):
    """Ohne feste Reihen (Reiter, Leichte) wird sofort kehrtgemacht: Die alte Front steht
    hinten (bis auf den Hauptmann, der in der Mitte bleibt), niemand läuft quer durch."""
    b, u = standing_group(kind)
    front_row = list(u.rows[0])
    before = {id(m): m.pos for m in u.all_men()}
    b.command_move([u], (8.0, 16.0))                                       # das Ziel liegt hinter der Gruppe
    b.update(DT)
    assert u.facing == (0.0, 1.0)                                          # kehrtgemacht, ohne zu schwenken
    assert same_men(u.rows[-1], front_row) >= len(front_row) - 1           # die alte Front ist jetzt hinten
    run(b, 0.3)
    moved = max(dist_of_pt(m.pos, before[id(m)]) for m in u.all_men())
    assert moved < 0.6                                                     # niemand läuft quer durch den Block


def test_short_move_wheels_before_it_marches(monkeypatch):
    """Auf kurzen Wegen (und für Reiter immer) erst schwenken, dann marschieren."""
    monkeypatch.setattr(config, "MARCH_MIN", 10.0)
    b, u = standing_group("mittel")
    b.command_move([u], (14.0, 12.0))                                      # rechtwinklig nach Osten
    x0 = u.x
    run(b, 0.25)
    assert u.facing[0] > 0.3 and u.facing[1] < -0.3                         # mitten im Schwenk
    assert abs(u.x - x0) < 0.05                                            # noch nicht losmarschiert
    run(b, 0.7)
    assert abs(u.facing[0] - 1.0) < 1e-6 and u.x > x0 + 0.1                # ausgerichtet und unterwegs


def test_wide_blocks_wheel_slower_than_small_groups():
    """Wie schnell geordnete Hopliten im Stand schwenken, hängt an ihrer Breite: Der äußere Mann
    muss den Bogen ablaufen. Kleine Trupps drehen flink, eine breite Phalanx braucht ihre Zeit,
    Reiter wenden nie schneller als ihr Höchstwert; Stürmende (und Haufen) drehen sich Mann für Mann."""
    def quarter_turn(kind, n, width, stance=None):
        b, u = standing_group(kind, n, width)
        if stance is not None:
            u.stance = stance
        t = 0.0
        while u.facing != (1.0, 0.0) and t < 10:
            b._turn_towards(u, (1.0, 0.0), DT)
            t += DT
        return t
    small, wide = quarter_turn("schwer", 8, 4), quarter_turn("schwer", 40, 14)
    assert small < 0.8 and wide > 1.5 and wide > 2 * small
    assert quarter_turn("reiter", 20, 10) >= (math.pi / 2) / config.CAVALRY_STAND_TURN - DT
    assert quarter_turn("schwer", 40, 14, Stance.ANGRIFF) < 0.6           # im Sturm dreht sich jeder für sich


def test_wide_block_slides_past_a_neighbours_corner():
    """Eine breite Phalanx, in die Lücke zwischen zwei eigenen Gruppen getippt, streift im
    Bogen die Ecke der Reiter: Sie gleitet schräg daran vorbei, statt stehen zu bleiben
    und sich aufzulösen."""
    scn = raid(4, (1.0, 1.0), houses=())
    army = army_of(GroupSpec("H", [Tier("schwer", 14), Tier("mittel", 13), Tier("leicht", 13)]),
                   GroupSpec("P", [Tier("peltast", 15)]), GroupSpec("R", [Tier("reiter", 20)]))
    b = Battle(scn, random.Random(1), army=army, ai="einfach")
    b._ai_raiders = lambda: None
    b._check_outcome = lambda: None
    b.alarm = False
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (7.0, 12.0), (9.0, 12.0))
    b.command_line([pelt], (9.3, 12.0), (10.6, 12.0))
    b.command_line([cav], (10.9, 12.0), (12.2, 12.0))
    run(b, 8)
    b.command_move([hop], (10.7, 12.0))
    loose = waited = 0
    t = 0.0
    while hop.target is not None and t < 10:
        b.update(DT)
        t += DT
        loose += hop.loose
        waited += hop.waiting
    assert hop.target is None and t < 6.0, t
    assert not loose and waited * DT < 0.5
    assert b._gap(hop, cav) >= 0.0


@pytest.mark.parametrize("by_line", [False, True])
def test_loose_hoplites_shift_man_by_man_keeping_their_front(by_line):
    """Lockere Hopliten, kurz zur Seite verlegt: Sie schwenken nicht erst als Block, jeder geht
    gerade an seinen neuen Platz, die Front bleibt; niemand bleibt hinter einem anderen hängen."""
    b, u = standing_group("schwer", 40, 10)
    u.drill = "locker"
    u.stance, u.in_line, u.target = Stance.PHALANX, False, u.pos
    run(b, 4)
    if by_line:
        b.command_line([u], (10.0, 12.0), (12.0, 12.0))                    # Front Nord, drei Kacheln weiter rechts
    else:
        b.command_move([u], (11.0, 12.0))
    turned = False
    t = 0.0
    while t < 8:
        b.update(DT)
        t += DT
        turned |= abs(u.facing[0]) > 0.2
        if not u.loose and (u.in_line or u.target is None) and math.hypot(u.x - 11.0, u.y - 12.0) < 0.3:
            break
    assert t < 3.5, t
    assert not turned and u.facing == (0.0, -1.0)


def test_short_correction_backwards_steps_without_turning():
    """Ein kurzes Stück zurück (kein Angriff): Die Gruppe rückt, ohne kehrtzumachen; sonst
    dreht sie sich an ihrem Platz, wenn sie hin und her geschoben wird, jedes Mal ganz um."""
    b, u = standing_group("mittel")
    b.command_move([u], (8.0, 12.5))                                       # eine halbe Kachel hinter sich
    for _ in range(int(2 / DT)):
        b.update(DT)
        assert u.facing == (0.0, -1.0)
    assert abs(u.y - 12.5) < 0.1


def test_riders_halt_at_the_house_they_loot_instead_of_circling():
    """Reiter, die ein Haus plündern sollen, halten davor an; sie kreisen nicht um das Haus,
    in das sie nicht hineinkommen."""
    b = Battle(raid(16, (2.0, 2.0), houses=((8, 8),)), random.Random(1),
               army=army_of(GroupSpec("R", [Tier("reiter", 12)])), ai="einfach")
    b._ai_raiders = lambda: None
    b._check_outcome = lambda: None
    b.alarm = False
    cav = b.units(Side.STADT)[0]
    cav.x, cav.y, cav.facing = 8.5, 12.0, (0.0, -1.0)
    cav.place_men()
    cav.stance, cav.target = Stance.RAUB, (8.5, 8.5)                      # mitten im Haus
    run(b, 5)
    turned = 0.0
    last = cav.facing
    for _ in range(int(3 / DT)):
        b.update(DT)
        turned += abs(math.atan2(last[0] * cav.facing[1] - last[1] * cav.facing[0],
                                 last[0] * cav.facing[0] + last[1] * cav.facing[1]))
        last = cav.facing
    assert cav.vel == 0.0 and turned < 0.2 and cav.rect_distance((8.5, 8.5)) <= config.LOOT_RANGE


def test_a_loose_group_changes_wall_side_only_with_a_clear_majority():
    """Steigt eine aufgelöste Gruppe über den Wall, zählt sie erst als drüben, wenn dort
    klar mehr Männer stehen; bei halb und halb springt ihr Ort nicht hin und her."""
    b = Battle(PALISADE, random.Random(1))
    u = next(g for g in b.units(Side.FEIND))
    men = u.all_men()
    gx, gy = b.gate.center
    u.loose = True
    u.centre_level = None
    half = len(men) // 2
    for i, m in enumerate(men):
        m.x, m.y = (2.5 + 0.1 * (i % 8), 6.0) if i <= half else (2.5 + 0.1 * (i % 8), 11.0)
    first = b._wall_level(b._loose_centre(u))                            # die Mehrheit draußen
    for i, m in enumerate(men):
        if i == half:                                                    # einer mehr drinnen: knapp
            m.y = 11.0
    assert b._wall_level(b._loose_centre(u)) == first
    for i, m in enumerate(men):
        m.y = 11.0 if i % 4 else 6.0                                     # drei Viertel drinnen
    assert b._wall_level(b._loose_centre(u)) != first


def test_men_are_drawn_smoothed_within_their_group_but_never_behind_the_march():
    """Nur fürs Bild: Ein Mann, der in seiner Gruppe hin und her zittert, wird ruhig gezeichnet;
    marschiert die Gruppe, hängt sein Bild nicht nach."""
    b, u = standing_group("schwer", 40, 10)
    b.alarm = False
    run(b, 2)
    man = u.rows[1][3]
    home = man.pos
    seen = []
    for k in range(int(2 / DT)):
        man.x = home[0] + (0.05 if k % 2 else -0.05)                   # zittert jeden Takt hin und her
        b.update(DT)
        seen.append(man.sx)
    assert max(seen[10:]) - min(seen[10:]) < 0.03                        # gezeichnet: kaum ein Zucken
    man.x, man.y = home
    b.command_move([u], (8.0, 6.0))
    worst = 0.0
    for _ in range(int(3 / DT)):
        b.update(DT)
        worst = max(worst, max(math.hypot(m.sx - m.x, m.sy - m.y) for m in u.all_men()))
    assert worst < 0.05                                                  # beim Marsch: genau an seiner Stelle


def test_a_formed_group_does_not_correct_tiny_offsets():
    """Ein Mann einer stehenden, geschlossenen Gruppe, der um weniger als eine Zehntelkachel
    neben seinem Platz steht, rückt nicht dauernd nach."""
    b, u = standing_group("schwer", 40, 10)
    b.alarm = False
    u.stance, u.target = Stance.PHALANX, u.pos
    run(b, 3)
    assert u.in_line
    man = u.rows[1][3]
    slot = dict((id(m), p) for m, p in u.slots())[id(man)]
    man.x = slot[0] + 0.06
    run(b, 1)
    assert abs(man.x - (slot[0] + 0.06)) < 1e-9 and u.in_line


def test_foot_marches_in_an_arc_with_its_front_ahead():
    """Fußvolk auf längerem Weg: Es läuft in seiner Blickrichtung an und schwenkt im Marsch
    zum Ziel (ein Bogen), statt erst auf der Stelle zu drehen; die Front zeigt dabei in
    Marschrichtung."""
    b, u = standing_group("mittel")
    b.command_move([u], (14.0, 12.0))                                      # rechtwinklig nach Osten
    y0 = u.y
    path = []
    for _ in range(int(4 / DT)):
        b.update(DT)
        path.append((u.pos, u.facing))
    assert min(p[1] for p, _ in path) < y0 - 0.05                          # erst ein Stück nach Norden: ein Bogen
    moving = [(path[i][0], path[i + 1][0], path[i + 1][1]) for i in range(len(path) - 1)
              if dist_of_pt(path[i][0], path[i + 1][0]) > 1e-3]
    assert all((q[0] - p[0]) * f[0] + (q[1] - p[1]) * f[1] > 0 for p, q, f in moving)   # immer vorwärts
    assert u.facing[0] > 0.95 and u.x > 10.0


def test_line_order_keeps_its_width_and_deploys_at_the_target():
    """Ein Linienbefehl auf längerem Weg: Die Gruppe marschiert in ihrer Breite und nimmt
    die befohlene Breite und Front erst kurz vor dem Ziel ein."""
    b, u = standing_group("mittel", 24, 6)
    b.command_line([u], (2.0, 4.0), (2.0, 8.0))                            # weit links oben, Front nach Osten
    assert u.width == 6 and u.march is not None
    while u.march is not None and b.time < 20:
        b.update(DT)
        if u.march is not None:
            assert u.width == 6
    assert dist_of_pt(u.pos, (2.0, 6.0)) <= config.MARCH_DEPLOY + 0.1
    run(b, 6)
    assert u.in_phalanx and u.facing == (1.0, 0.0) and u.width == len(u.rows[0]) and u.width > 6


def test_standing_cavalry_turns_while_it_starts_to_ride():
    """Reiter im Stand schwenken beim Anreiten (ein enger Bogen), statt erst auf der Stelle
    zu drehen: anfangs fast auf der Stelle, dann ausgerichtet und unterwegs."""
    b, u = standing_group("reiter")
    b.command_move([u], (14.0, 12.0))                                      # rechtwinklig nach Osten
    x0 = u.x
    run(b, 0.15)
    assert u.facing[0] > 0.3 and u.facing[1] < -0.3                         # mitten im Schwenk
    assert abs(u.x - x0) < 0.05                                            # noch kaum vom Fleck
    run(b, 0.5)
    assert u.facing[0] > 0.999 and u.x > x0 + 0.1                          # ausgerichtet und unterwegs


def test_phalanx_wheels_to_its_ordered_front_without_swapping_rows():
    b, u = standing_group("mittel", 12, 6)
    heavy = list(u.rows[0])
    b.command_line([u], (10.0, 12.0), (6.0, 12.0))                         # Front nach Süden, an Ort und Stelle
    assert u.face_to == (0.0, 1.0) and u.facing == (0.0, -1.0)             # noch nicht gesprungen
    run(b, 0.6)
    assert -0.9 < u.facing[1] < 0.9                                        # mitten im Schwenk
    assert u.rows[0][0] is heavy[0]                                        # eine Phalanx tauscht keine Reihen
    run(b, 2.5)
    assert u.facing == (0.0, 1.0) and u.face_to is None


def test_enemy_groups_wheel_and_about_turn_like_the_player():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1), ai="einfach")
    b._ai_raiders = lambda: None
    b.alarm = False
    raider = b.units(Side.FEIND)[0]
    raider.stance, raider.target, raider.target_id = Stance.HALTEN, None, None
    raider.x, raider.y, raider.facing = 8.0, 6.0, (0.0, 1.0)
    raider.place_men()
    front = list(raider.rows[0])
    raider.stance, raider.target = Stance.HALTEN, (8.0, 2.0)              # zurück nach Norden
    b.update(DT)
    assert raider.facing == (0.0, -1.0) and same_men(raider.rows[-1], front) >= len(front) - 1
    raider.target = (10.5, raider.y)                                        # und nun ein kurzes Stück nach Osten
    x0 = raider.x
    run(b, 0.25)
    assert 0.3 < raider.facing[0] < 0.95 and abs(raider.x - x0) < 0.05     # schwenkt erst, marschiert dann


# ------------------------------------------------------------ Kreis ziehen, Nachrücken, Gerangel
def test_ring_size_from_drag_never_tighter_than_the_men_need():
    b, u = standing_group("mittel", 12, 6)
    b.command_formation([u], "o")
    tight = u.ring_minimum()
    assert b.command_ring([u], (8.0, 12.0), 1.5) == 1
    assert abs(u.ring_size - 1.5) < 1e-6 and u.ring_radius() == 1.5 and u.stance is Stance.PHALANX
    run(b, 3)
    assert all(abs(dist_of_pt(p, u.pos) - 1.5) < 1e-6 for _, p in u.slots())
    assert u.in_phalanx
    b.command_ring([u], (8.0, 12.0), 0.1)
    assert u.ring_size == tight                              # enger geht es nicht
    b.command_ring([u], (8.0, 12.0), 9.0)
    assert u.ring_size == config.RING_MAX
    b.command_line([u], (6.0, 12.0), (10.0, 12.0))
    assert u.formation == "linie" and u.ring_size == 0.0


def test_second_row_steps_into_gaps_of_the_first():
    u = Lochos(1, Side.STADT, [men("schwer", 6), men("mittel", 6), men("leicht", 4)], 5.0, 5.0)
    first, second = list(u.rows[0]), list(u.rows[1])
    first[2].hp = 0.0
    first[4].hp = 0.0
    assert u.bury() == 2
    assert len(u.rows[0]) == 6                                 # die Front bleibt voll
    assert sum(1 for m in u.rows[0] if m in second) == 2       # zwei aus der zweiten Reihe rückten vor
    assert len(u.rows[1]) == 6 and len(u.rows[2]) == 2         # hinten wurde es dünner
    assert u.men == 14


def test_attackers_wrap_around_the_end_of_a_line():
    """Räuber greifen das Ostende einer Hoplitenlinie von der Flanke an: ihre Männer
    legen sich wie ein C um das Ende, vorn, seitlich und hinten."""
    scn = raid(16, (13.0, 9.0))
    army = army_of(GroupSpec("Hopliten", [Tier("schwer", 14), Tier("mittel", 14)]))
    b = Battle(scn, random.Random(0), army=army, ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    hop = b.units(Side.STADT)[0]
    raider = b.units(Side.FEIND)[0]
    b.command_line([hop], (5.0, 9.0), (11.0, 9.0))
    run(b, 6)
    assert hop.in_phalanx
    raider.x, raider.y, raider.facing = 13.0, 9.0, (-1.0, 0.0)
    raider.place_men()
    raider.stance = Stance.ANGRIFF
    raider.target_id = hop.id
    raider.target = hop.pos
    run(b, 8)
    assert raider.engaged
    arcs = {hop.arc_to(m.pos) for m in raider.all_men()}
    assert {"front", "flank", "rear"} <= arcs, arcs                       # das C um das Linienende
    near = [m for m in raider.all_men() if hop.rect_distance(m.pos) <= config.ASSAULT_GAP + config.ROW_SPACING + 0.1]
    assert len(near) >= 0.8 * raider.men                                   # (fast) alle sind am Feind
    assert all(hop.rect_distance(m.pos) > 0.0 for m in raider.all_men())   # aber keiner steckt in der Formation


def test_attackers_line_up_at_the_enemy_men_not_at_an_empty_rectangle():
    """Stehen die Männer des Gegners nur in einem Teil seines Rechtecks, reihen sich
    die Angreifer an den Männern auf, nicht am leeren Rest."""
    scn = raid(16, (13.0, 9.0))
    army = army_of(GroupSpec("Hopliten", [Tier("schwer", 14), Tier("mittel", 14)]))
    b = Battle(scn, random.Random(0), army=army, ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    hop = b.units(Side.STADT)[0]
    raider = b.units(Side.FEIND)[0]
    b.command_line([hop], (5.0, 9.0), (11.0, 9.0))
    run(b, 6)
    for m in hop.all_men():                                   # die Männer stehen nur in der Westhälfte
        m.x = min(m.x, 7.9)
    b._move_men = lambda dt: None                             # ... und bleiben dort
    raider.x, raider.y, raider.facing = 10.4, 9.0, (-1.0, 0.0)   # am Ostende des Rechtecks, im Kontakt
    raider.place_men()
    raider.stance = Stance.ANGRIFF
    raider.target_id = hop.id
    raider.target = hop.pos
    b.update(DT)
    slots = b._assault_slots(raider)
    assert slots is not None
    for _, p in slots:
        assert min(dist_of_pt(p, m.pos) for m in hop.all_men()) <= 0.6, p    # jeder Platz liegt bei einem Mann (zweite Reihe dahinter)
    assert all(p[0] < 8.6 for _, p in slots)                                  # keiner am leeren Ostteil des Rechtecks


def wing_setup(second_horde: bool):
    spawns = [(8.0, 6.0)] + ([(11.6, 6.4)] if second_horde else [])
    b = Battle(raid(16 * len(spawns), *spawns), random.Random(0),
               army=army_of(GroupSpec("Hopliten", [Tier("schwer", 20), Tier("mittel", 20)])), ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    hop = b.units(Side.STADT)[0]
    raiders = b.units(Side.FEIND)
    for r in raiders:
        r.stance, r.target = Stance.HALTEN, None
    b.command_line([hop], (5.0, 9.0), (11.0, 9.0))
    run(b, 5)
    b.command_attack([hop])
    for _ in range(int(12 / DT)):
        b.update(DT)
        if hop.engaged:
            break
    run(b, 4)
    assert hop.engaged
    return b, hop, raiders[0]


def test_charging_hoplites_fold_their_wings_around_a_smaller_group():
    b, hop, raider = wing_setup(second_horde=False)
    local = [raider.local(m.pos) for m in hop.all_men()]
    beside = [(al, fw) for al, fw in local if abs(al) > raider.half_w and fw < raider.half_d - 0.05]
    assert len(beside) >= 4                                                 # die Flügel sind eingeklappt, an den Flanken
    assert all(fw >= -raider.half_d - 0.05 for _, fw in local)              # aber nie in den Rücken
    slots = dict((id(m), p) for m, p in hop.slots())
    centre = [m for m in hop.rows[0] if dist_of_pt(m.pos, slots[id(m)]) < 0.1]
    assert len(centre) >= 6                                                 # die Mitte steht in der Reihe
    assert all(raider.rect_distance(m.pos) > 0.0 for m in hop.all_men())
    front = sorted(m.x for m in hop.rows[0] if raider.local(m.pos)[1] >= raider.half_d)
    gaps = [b_ - a_ for a_, b_ in zip(front, front[1:])]
    assert max(gaps) < 2 * config.MAN_SPACING + 0.05                        # keine Lücke in der Reihe


def test_wings_stay_in_line_when_another_horde_is_near():
    b, hop, raider = wing_setup(second_horde=True)
    assert b._assault_slots(hop) is None
    assert all(raider.local(m.pos)[1] >= raider.half_d - 0.05 for m in hop.all_men())   # alle bleiben vor dem Gegner
    assert hop.on_slots(0.3, 0.8)


def test_only_men_within_reach_of_the_enemy_fight():
    """Ein schmaler Haufen am Ende einer langen Linie: nur das Ende kämpft mit."""
    hop = Lochos(1, Side.STADT, arrange(men("mittel", 28), 14), 8.0, 9.0, facing=(0.0, -1.0), stance=Stance.PHALANX, in_line=True)
    raider = Lochos(2, Side.FEIND, arrange(men("raeuber", 16), 8), 9.2, 8.5, facing=(0.0, 1.0), stance=Stance.HALTEN)
    hop.place_men()
    raider.place_men()
    full = hop.melee_attack()
    partial = hop.melee_attack_against(lambda m: raider.surface_distance(m.pos), config.CONTACT_REACH)
    assert 0.3 * full < partial < 0.75 * full                            # ein Teil der Front, nicht alles
    wide = Lochos(3, Side.FEIND, arrange(men("raeuber", 32), 16), 8.0, 8.5, facing=(0.0, 1.0), stance=Stance.HALTEN)
    wide.place_men()
    assert hop.melee_attack_against(lambda m: wide.surface_distance(m.pos), config.CONTACT_REACH) == full
    far = Lochos(4, Side.FEIND, arrange(men("raeuber", 16), 8), 8.0, 6.0, facing=(0.0, 1.0), stance=Stance.HALTEN)
    far.place_men()
    floor = hop.melee_attack_against(lambda m: far.surface_distance(m.pos), config.CONTACT_REACH)
    assert 0 < floor <= 1.0                                                 # außer Reichweite: nur der Notkontakt


def test_second_group_takes_the_next_free_stretch_of_the_outline():
    """Zwei Räubergruppen fallen nacheinander über dasselbe Linienende her: Die
    zweite stellt sich nicht in die erste hinein, sondern daneben an das nächste
    freie Stück des Umrisses; beide kommen an den Feind."""
    scn = raid(32, (13.0, 9.0), (13.0, 10.5))
    army = army_of(GroupSpec("Hopliten", [Tier("schwer", 14), Tier("mittel", 14)]))
    b = Battle(scn, random.Random(0), army=army, ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    hop = b.units(Side.STADT)[0]
    first, second = b.units(Side.FEIND)
    b.command_line([hop], (5.0, 9.0), (11.0, 9.0))
    run(b, 6)
    for r, (x, y) in ((first, (13.0, 9.0)), (second, (13.0, 10.5))):
        r.x, r.y, r.facing = x, y, (-1.0, 0.0)
        r.place_men()
        r.stance = Stance.ANGRIFF
        r.target_id = hop.id
        r.target = hop.pos
    run(b, 10)
    assert first.engaged and second.engaged
    closest = min(dist_of_pt(m.pos, n.pos) for m in first.all_men() for n in second.all_men())
    assert closest > 0.5 * config.MAN_SPACING, closest                    # niemand steht im anderen
    for r in (first, second):
        near = [m for m in r.all_men() if hop.rect_distance(m.pos) <= config.ASSAULT_GAP + 2 * config.ROW_SPACING + 0.1]
        assert len(near) >= 0.8 * r.men, (r.name, len(near))              # beide liegen am Umriss
    assert first.contact_since[hop.id] <= second.contact_since[hop.id]


def test_flank_men_of_every_row_fight_but_only_within_reach():
    """An der Flanke dreht sich um, wer den Gegner erreicht, gleich in welcher
    Reihe er steht; vorn kämpft nur die vordere Reihe (und die Speere der zweiten)."""
    hop = Lochos(1, Side.STADT, arrange(men("mittel", 30), 10), 8.0, 9.0, facing=(0.0, -1.0), stance=Stance.PHALANX, in_line=True)
    hop.place_men()
    east = hop.x + hop.half_w + 0.3
    raider = Lochos(2, Side.FEIND, arrange(men("raeuber", 6), 2), east + 0.2, 9.0, facing=(-1.0, 0.0), stance=Stance.HALTEN)
    raider.place_men()
    b = Battle(raid(16, (13.0, 3.0)), random.Random(0), army=army_of(GroupSpec("H", [Tier("mittel", 10)])))
    distance = b._reach_to(raider)
    flank = hop.melee_attack_against(distance, config.CONTACT_REACH, "flank")
    as_front = hop.melee_attack_against(distance, config.CONTACT_REACH, "front")
    assert 3 * UNIT_TYPES["mittel"].attack <= flank <= 9 * UNIT_TYPES["mittel"].attack, flank   # die äußeren Rotten
    assert as_front < flank                                                # vorn zählt nur die erste Reihe
    assert flank < 0.5 * hop.melee_attack()                                # längst nicht die ganze Front


def test_losses_fall_where_the_enemy_stands():
    """Ein Haufen am Ostende einer langen Reihe (leichtes Volk): Es fallen die
    Männer dort, die Westhälfte bleibt unberührt."""
    hop = Lochos(1, Side.STADT, arrange(men("peltast", 40), 40), 8.0, 9.0, facing=(0.0, -1.0), stance=Stance.PHALANX, in_line=True)
    hop.place_men()
    raider = Lochos(2, Side.FEIND, arrange(men("raeuber", 16), 8), hop.x + hop.half_w - 0.5, hop.y - 0.6, facing=(0.0, 1.0), stance=Stance.ANGRIFF)
    raider.place_men()
    b = Battle(raid(16, (13.0, 3.0)), random.Random(0), army=army_of(GroupSpec("H", [Tier("mittel", 10)])))
    b.lochoi = [hop, raider]
    for _ in range(int(30 / DT)):                                           # nur Kampf, keine Moral (sonst fliehen die Räuber vorher)
        b._combat(DT)
    assert hop.men < 40
    west = [m for m in hop.all_men() if m.x < hop.x - 0.3]
    assert len(west) >= 18, len(west)                                       # (fast) alle 20 der Westhälfte leben noch


# ------------------------------------------------- Niemand steht im anderen
def test_no_two_men_ever_share_a_position():
    """Jeder Mann hat seinen Platz: Zwischen Männern verschiedener Gruppen bleiben
    immer zwei Halbmesser, auch beim Sturm, beim Umfassen und durch Fliehende
    hindurch; in der eigenen Gruppe rückt man höchstens Schulter an Schulter."""
    b = Battle(OFFENE_SIEDLUNG, random.Random(2))
    b.command_attack()
    for i in range(int(40 / DT)):
        b.update(DT)
        if b.outcome:
            break
        if i % 30:
            continue
        men = [(m, u.id) for u in b.lochoi if u.alive for m in u.all_men()]
        for j, (a, ua) in enumerate(men):
            for c, uc in men[j + 1:]:
                least = config.MAN_RADIUS if ua == uc else 2 * config.MAN_RADIUS
                assert dist_of_pt(a.pos, c.pos) >= least - 1e-6, (i / 30, ua, uc, a.pos, c.pos)


def two_own_groups(standing: tuple[float, float], mover: tuple[float, float]) -> tuple[Battle, Lochos, Lochos]:
    b = Battle(raid(16, (14.0, 1.0)), random.Random(0),
               army=army_of(GroupSpec("Steher", [Tier("mittel", 16)]), GroupSpec("Läufer", [Tier("leicht", 16)])), ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    stand, walk = b.units(Side.STADT)
    for u, (x, y) in ((stand, standing), (walk, mover)):
        u.x, u.y = x, y
        u.facing = (0.0, -1.0)
        u.target = None
        u.stance = Stance.HALTEN
        u.place_men()
    return b, stand, walk


def test_group_walks_around_a_standing_friendly_group():
    """Steht eine eigene Gruppe auf dem Weg, geht die befohlene um sie herum; die
    Stehende wird nicht verschoben."""
    b, stand, walk = two_own_groups((8.0, 8.0), (8.0, 12.0))
    b.command_move([walk], (8.0, 4.0))
    origin = stand.pos
    closest = 9.0
    inside = False
    for _ in range(int(20 / DT)):
        b.update(DT)
        closest = min(closest, min(dist_of_pt(m.pos, n.pos) for m in walk.all_men() for n in stand.all_men()))
        inside = inside or any(stand.rect_distance(m.pos) == 0.0 for m in walk.all_men())
    assert dist_of_pt(stand.pos, origin) < 0.05, (origin, stand.pos)          # nicht geschoben
    assert dist_of_pt(walk.pos, (8.0, 4.0)) < 0.3, walk.pos                   # angekommen
    assert not inside and closest >= 2 * config.MAN_RADIUS - 1e-6, closest   # Mann für Mann vorbei, nie ineinander


def test_group_ordered_onto_a_standing_group_halts_beside_it():
    """Wird eine Gruppe genau dorthin befohlen, wo schon eine eigene steht, schiebt
    sie die Stehende nicht weg, sondern hält vor ihr."""
    b, stand, walk = two_own_groups((8.0, 8.0), (8.0, 12.0))
    b.command_move([walk], (8.0, 8.0))
    run(b, 20)
    assert dist_of_pt(stand.pos, (8.0, 8.0)) < 0.05, stand.pos              # nicht verschoben
    assert b._gap(stand, walk) >= config.SEPARATION - 0.05                  # nicht ineinander
    assert walk.y > stand.y and dist_of_pt(walk.pos, (8.0, 8.0)) < 2.0      # davor, von wo sie kam


def test_wide_line_walks_around_a_small_group_instead_of_pushing_it():
    b = Battle(raid(16, (14.0, 1.0)), random.Random(0),
               army=army_of(GroupSpec("Klein", [Tier("mittel", 16)]), GroupSpec("Linie", [Tier("mittel", 40)])), ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    small, wide = b.units(Side.STADT)
    b.command_move([small], (8.0, 8.0))
    run(b, 8)
    wide.x, wide.y, wide.facing, wide.target, wide.stance = 8.0, 14.0, (0.0, -1.0), None, Stance.HALTEN
    wide.place_men()
    origin = small.pos
    b.command_line([wide], (5.0, 3.0), (11.0, 3.0))
    through = False
    for _ in range(int(20 / DT)):
        b.update(DT)
        through = through or small.rect_distance(wide.pos) == 0.0            # mitten hindurch?
    assert dist_of_pt(small.pos, origin) < 0.05, small.pos                  # nicht weggeschoben
    assert not through and abs(wide.y - 3.0) < 0.3                          # außen herum, und angekommen


def test_moving_group_walks_around_a_phalanx_at_its_post():
    """Eine Phalanx behält ihr Ziel als Posten, sie steht trotzdem: Wer vorbei will,
    geht außen herum, statt durch sie hindurch."""
    b = Battle(raid(16, (14.0, 1.0)), random.Random(0),
               army=army_of(GroupSpec("Phalanx", [Tier("mittel", 40)]), GroupSpec("Reiter", [Tier("reiter", 16)])), ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    hop, cav = b.units(Side.STADT)
    b.command_line([hop], (6.0, 8.0), (10.0, 8.0))
    run(b, 8)
    assert hop.in_phalanx and b._standing(hop)
    cav.x, cav.y, cav.facing, cav.target, cav.stance = 8.0, 14.0, (0.0, -1.0), None, Stance.HALTEN
    cav.place_men()
    b.command_move([cav], (8.0, 3.0))
    origin = hop.pos
    through = False
    for _ in range(int(20 / DT)):
        b.update(DT)
        through = through or hop.rect_distance(cav.pos) == 0.0
    assert not through and dist_of_pt(hop.pos, origin) < 0.05
    assert dist_of_pt(cav.pos, (8.0, 3.0)) < 0.3


def test_ring_counts_as_a_circle_for_distances():
    """Der Kreis ist für Abstände ein Kreis, nicht sein umschriebenes Rechteck:
    an seiner Ecke ist noch Platz, am Rand nicht."""
    ring = Lochos(1, Side.STADT, arrange(men("mittel", 24), 8), 8.0, 8.0, facing=(0.0, -1.0), stance=Stance.PHALANX)
    ring.formation = "o"
    ring.place_men()
    r = ring.half_w
    assert ring.rect_distance((8.0 + r * 0.8, 8.0 + r * 0.8)) > 0.05            # die Ecke des Rechtecks liegt außerhalb
    assert ring.rect_distance((8.0 + r * 0.5, 8.0)) == 0.0                       # innen
    assert len(ring.outline()) == 8 and all(abs(dist_of_pt(p, ring.pos) - r) < 1e-6 for p in ring.outline())


def one_ring_group(b: Battle) -> Lochos:
    """Alle eigenen Männer in einer Gruppe (Hopliten außen, Reiter und Peltasten in inneren
    Ringen): so stehen Räuber vor einem Kreis, der die ganze Truppe ist. Im Spiel gibt es
    keine gemischten Gruppen mehr, für den Aufbau dieser Lage genügt es."""
    units = b.units(Side.STADT)
    keep = max(units, key=lambda u: u.men)
    keep.rows = arrange([m for u in units for m in u.all_men()], max(u.width for u in units))
    keep.men_start = keep.men
    for u in units:
        if u is not keep:
            u.rows = []
    b.lochoi = [u for u in b.lochoi if u.rows]
    return keep


def test_groups_queue_behind_their_own_fighting_group():
    """Greifen mehrere eigene Gruppen denselben Feind durch eine Enge an, fährt keine
    in die vordere hinein: Wer nicht mehr an den Feind kommt, wartet im Block dahinter."""
    b = Battle(PALISADE, random.Random(1))
    g = one_ring_group(b)
    b.command_formation([g], "o")
    gx, gy = b.gate.center
    b.command_ring([g], (gx, gy + 2.2), 1.2)
    b.gate.hp = 0.0
    b.gate.closed = False
    run(b, 20)                                                               # das Gedränge am Tor sortiert sich
    raiders = [u for u in b.units(Side.FEIND, fighting_only=True) if not u.loose]
    fighting = [u for u in raiders if u.engaged]
    waiting = [u for u in raiders if not u.engaged and u.waiting]
    assert fighting and waiting, (len(fighting), len(waiting))
    for w in waiting:
        assert w.on_slots(config.SLOT_TOLERANCE + 0.1, 0.6), w.name                  # die Wartenden stehen (weitgehend) im Block
        assert all(b._gap(w, f) >= 0.0 for f in fighting)
    men = [(m, u.id) for u in b.lochoi if u.alive for m in u.all_men()]
    for j, (a, ua) in enumerate(men):
        for c, uc in men[j + 1:]:
            if ua != uc:
                assert dist_of_pt(a.pos, c.pos) >= 2 * config.MAN_RADIUS - 1e-6


def test_hoplites_pass_through_their_own_peltasts_in_loose_order():
    """Peltasten stehen in lockerer Ordnung: Eine Phalanx, die durch sie nach vorn
    rückt, geht hindurch (die Männer weichen einander aus), statt außen herum, und
    schiebt sie nicht weg."""
    b = Battle(raid(16, (14.0, 1.0)), random.Random(0),
               army=army_of(GroupSpec("Hopliten", [Tier("mittel", 40)]), GroupSpec("Peltasten", [Tier("peltast", 15)])), ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    hop, pelt = b.units(Side.STADT)
    b.command_line([pelt], (5.0, 10.6), (11.0, 10.6))
    run(b, 8)
    origin = pelt.pos
    hop.x, hop.y, hop.facing, hop.target, hop.stance = 8.0, 14.0, (0.0, -1.0), None, Stance.HALTEN
    hop.place_men()
    b.command_line([hop], (4.0, 9.5), (12.0, 9.5))
    widest = 0.0
    for _ in range(int(15 / DT)):
        b.update(DT)
        widest = max(widest, abs(hop.x - 8.0))
    assert hop.in_phalanx and abs(hop.y - 9.5) < 0.3
    assert widest < 1.0, widest                                            # kein Umweg um die ganze Linie
    assert dist_of_pt(pelt.pos, origin) < 0.05


# ------------------------------------------------------------- Schildseite
def test_hoplite_shield_covers_the_left_flank():
    """Der Schild sitzt links: von rechts trifft ein Angriff die Hopliten härter als von
    links, Speere von links fangen sich im Schild; bei Räubern ist es gleich."""
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    hop = b.units(Side.STADT)[0]
    hop.x, hop.y, hop.facing = 8.0, 10.0, (0.0, -1.0)            # Front nach Norden: rechts ist Osten
    hop.place_men()
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = hop.x + hop.half_w + 1.0, hop.y          # rechts (Osten)
    right, arc_r = b._defense_mod(raider, hop)
    raider.x = hop.x - hop.half_w - 1.0                           # links (Westen)
    left, arc_l = b._defense_mod(raider, hop)
    assert arc_r == arc_l == "flank"
    assert right == pytest.approx(left * config.SHIELD_MELEE_OPEN / config.SHIELD_MELEE_COVER)
    assert b.shield_side(hop, (hop.x - 2.0, hop.y), config.SHIELD_SPEAR_COVER, config.SHIELD_SPEAR_OPEN) == config.SHIELD_SPEAR_COVER
    assert b.shield_side(raider, (raider.x + 2.0, raider.y), 0.5, 2.0) == 1.0    # Räuber tragen keinen Hoplitenschild


def test_spears_from_the_shield_side_do_less_harm():
    from game.battle import Projectile
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    b.alarm = False
    hop = b.units(Side.STADT)[0]
    hop.x, hop.y, hop.facing = 8.0, 10.0, (0.0, -1.0)
    hop.place_men()
    man = hop.all_men()[-1]

    def hit(origin):
        man.hp = man.kind.hp
        b.projectiles = [Projectile(origin[0], origin[1], man.x, man.y, hop.id, 0.2, 0.0, 0.05, man)]
        for u in b.lochoi:
            u.volley_timer = 99.0
        b._volleys(0.1)
        return man.kind.hp - man.hp
    left = hit((hop.x - hop.half_w - 2.0, hop.y))
    right = hit((hop.x + hop.half_w + 2.0, hop.y))
    assert left == pytest.approx(right * config.SHIELD_SPEAR_COVER / config.SHIELD_SPEAR_OPEN)


# ---------------------------------------------------------- Schlachtordnung

def order_army(cavalry_groups: int = 1) -> Army:
    groups = [GroupSpec("H", [Tier("schwer", 12), Tier("mittel", 12)]),
              GroupSpec("P", [Tier("peltast", 12)])]
    groups += [GroupSpec(f"R{i}", [Tier("reiter", 9)]) for i in range(cavalry_groups)]
    return army_of(*groups)


def by_arm(b: Battle, plans) -> dict:
    out: dict = {}
    for p in plans:
        out.setdefault(b.by_id(p.unit_id).arm(), []).append(p)
    return out


def test_mixed_groups_form_a_battle_order():
    """Hopliten auf der Linie, Peltasten dahinter, Reiter am rechten Flügel."""
    b = Battle(raid(8, (8.0, 1.0)), random.Random(0), army=order_army())
    plans = by_arm(b, b.plan_line(None, (5.0, 12.0), (11.0, 12.0)))   # Front nach Norden
    hop, pelt, cav = plans["hopliten"][0], plans["peltasten"][0], plans["reiter"][0]
    assert hop.center[1] == pytest.approx(12.0)
    hop_back = hop.center[1] + hop.depth * config.ROW_SPACING / 2
    assert pelt.center[1] - pelt.depth * config.ROW_SPACING / 2 > hop_back      # ganz dahinter
    assert abs(pelt.center[0] - hop.center[0]) < 0.1
    assert pelt.width * config.MAN_SPACING < hop.width * config.MAN_SPACING     # Enden der Phalanx frei
    hop_right = hop.center[0] + hop.width * config.MAN_SPACING / 2
    cav_left = cav.center[0] - cav.width * config.MAN_SPACING / 2
    assert 0 < cav_left - hop_right < 1.0                  # rechts daneben, an der schildlosen Seite
    front = lambda p: p.center[1] - p.depth * config.ROW_SPACING / 2
    assert front(cav) == pytest.approx(front(hop))         # Fronten bündig
    assert all(p.facing == (0.0, -1.0) for p in (hop, pelt, cav))


def test_battle_order_right_follows_the_facing():
    """Von Nord nach Süd gezogen schaut die Front nach Osten: rechts ist dann Süden."""
    b = Battle(raid(8, (8.0, 1.0)), random.Random(0), army=order_army())
    plans = by_arm(b, b.plan_line(None, (8.0, 5.0), (8.0, 12.0)))
    hop, pelt, cav = plans["hopliten"][0], plans["peltasten"][0], plans["reiter"][0]
    assert hop.facing == pytest.approx((1.0, 0.0))
    assert pelt.center[0] < hop.center[0]                  # hinten ist Westen
    assert cav.center[1] > hop.center[1] + hop.width * config.MAN_SPACING / 2


def test_second_cavalry_group_takes_the_left_wing():
    b = Battle(raid(8, (8.0, 1.0)), random.Random(0), army=order_army(cavalry_groups=2))
    plans = by_arm(b, b.plan_line(None, (5.0, 12.0), (11.0, 12.0)))
    hop = plans["hopliten"][0]
    xs = sorted(p.center[0] for p in plans["reiter"])
    assert xs[0] < hop.center[0] - hop.width * config.MAN_SPACING / 2
    assert xs[1] > hop.center[0] + hop.width * config.MAN_SPACING / 2


def test_cavalry_wing_moves_left_at_the_map_edge():
    b = Battle(raid(8, (8.0, 1.0)), random.Random(0), army=order_army())
    plans = by_arm(b, b.plan_line(None, (b.cols - 4.0, 12.0), (b.cols - 0.2, 12.0)))
    hop, cav = plans["hopliten"][0], plans["reiter"][0]
    assert cav.center[0] < hop.center[0]


def test_groups_of_one_arm_still_share_the_line():
    """Nur Hopliten: nebeneinander wie bisher, keine zweite Linie."""
    b = static_line(raider_y=2.0)
    plans = b.plan_line(None, (4.0, 10.0), (12.0, 10.0))
    assert len(plans) == 3
    assert all(p.center[1] == pytest.approx(10.0) for p in plans)


def test_battle_order_is_where_the_groups_end_up():
    b = Battle(raid(8, (8.0, 1.0)), random.Random(0), army=order_army())
    b.command_line(None, (5.0, 12.0), (11.0, 12.0))
    run(b, 12.0)
    units = {u.arm(): u for u in b.units(Side.STADT, fighting_only=True)}
    hop, pelt, cav = units["hopliten"], units["peltasten"], units["reiter"]
    assert pelt.y > hop.y + 0.3
    assert cav.x > hop.x + hop.half_w


# ------------------------------------------------------------ Hauptmann und Kontermarsch
def test_commander_stands_front_centre_and_is_succeeded():
    """Der Befehlshaber steht vorn in der Mitte; fällt er, rückt ein Nachfolger dorthin."""
    b, u = standing_group("mittel", 12, 6)
    c = u.commander_man()
    slots = dict((id(m), p) for m, p in u.slots())
    front = [slots[id(m)] for m in u.rows[0]]
    assert c in u.rows[0] and c is u.rows[0][len(u.rows[0]) // 2]          # vorn in der Mitte
    assert abs(sum(p[0] for p in front) / len(front) - slots[id(c)][0]) < 0.1
    c.hp = 0.0
    u.bury()
    nxt = u.commander_man()
    assert nxt is not None and nxt is not c and nxt.hp > 0
    u.slots()
    assert nxt is u.rows[0][len(u.rows[0]) // 2]                            # der Nachfolger rückt vorn in die Mitte


def test_the_leader_commands_his_group_from_the_front_centre():
    """Kämpft der Anführer in einer Gruppe, ist er ihr Befehlshaber und steht vorn in der Mitte."""
    army = army_of(GroupSpec("H", [Tier("schwer", 8), Tier("mittel", 8)], leader=True))
    b = Battle(raid(16, (8.0, 1.0)), random.Random(0), army=army, ai="einfach")
    u = b.units(Side.STADT)[0]
    lead = u.leader_man()
    assert lead is not None and u.commander_man() is lead
    u.slots()
    assert lead is u.rows[0][len(u.rows[0]) // 2]


def test_hoplites_countermarch_and_keep_their_front_rank():
    """Liegt das Ziel hinten, machen Hopliten einen Kontermarsch: dieselben Männer bleiben
    vorn, die Gruppe steht dabei kurz ungeordnet und geht dann los."""
    b, u = standing_group("mittel", 12, 4)
    front = list(u.rows[0])
    b.command_move([u], (8.0, 15.5))                                       # hinter der Gruppe
    b.update(DT)
    assert u.facing == (0.0, 1.0)
    assert set(map(id, u.rows[0])) == set(map(id, front))                 # die vordere Reihe bleibt vorn
    assert u.countermarch_until > b.time and not u.in_phalanx
    y0 = u.y
    run(b, config.COUNTERMARCH_BASE * 0.8)
    assert abs(u.y - y0) < 1e-6                                            # steht, während die Rotten durchziehen
    run(b, 3.0)
    assert u.y > y0 + 0.5                                                  # danach unterwegs
    assert all(p[1] > u.y for m, p in u.slots() if any(m is f for f in front))   # die Vorderen stehen jetzt vorn (Süden)


def test_light_troops_and_melee_turn_about_at_once():
    """Peltasten, Reiter und Räuberhaufen haben keine festen Reihen: Sie wenden sofort, die
    hintere Reihe steht dann vorn."""
    b, u = standing_group("peltast", 12, 4)
    b.command_move([u], (8.0, 15.5))
    b.update(DT)
    assert u.facing == (0.0, 1.0) and u.countermarch_until < b.time


# ------------------------------------------------------------- Modi der Hopliten
def test_drill_sets_spacing_speed_and_phalanx_bonus():
    """Locker: weite Abstände, schneller, ohne Phalanxbonus; Peltasten und Reiter kennen
    keine Modi."""
    hop = Lochos(1, Side.STADT, arrange(men("mittel", 20), 10), 5.0, 5.0)
    hop.stance, hop.in_line = Stance.PHALANX, True
    base_w, base_v = hop.half_w, hop.speed
    assert hop.drill == "phalanx" and hop.in_phalanx
    hop.drill = "locker"
    assert hop.half_w > base_w and hop.speed > base_v and not hop.in_phalanx
    pelt = Lochos(2, Side.STADT, arrange(men("peltast", 10), 5), 5.0, 5.0)
    pelt.drill = "locker"
    assert pelt.drill_kind() == "" and pelt.man_gap() == config.MAN_SPACING


def test_loose_order_suffers_fewer_javelin_hits():
    """Locker gehen viele Speere ins Leere."""
    def damage(drill: str) -> float:
        b = Battle(raid(16, (8.0, 3.0)), random.Random(3), army=army_of(GroupSpec("H", [Tier("mittel", 20)])))
        b._ai_raiders = lambda: None
        b.alarm = False
        (hop,) = b.units(Side.STADT)
        hop.reform(10)
        hop.x, hop.y, hop.facing = 8.0, 9.0, (0.0, -1.0)
        hop.stance, hop.in_line, hop.target = Stance.PHALANX, True, (8.0, 9.0)
        hop.drill = drill
        hop.place_men()
        thrower = b._spawn(Side.FEIND, arrange(men("peltast", 10), 10), 8.0, 7.0, "Werfer")
        thrower.facing = (0.0, 1.0)
        thrower.place_men()
        hp = sum(m.hp for m in hop.all_men())
        for _ in range(int(3 / DT)):
            b._volleys(DT)
        return hp - sum(m.hp for m in hop.all_men())
    assert damage("locker") < damage("phalanx")


def test_javelins_lead_a_running_man_and_miss_one_who_stops(monkeypatch):
    """Werfer zielen dorthin, wo der Mann sein wird: Wer weiterläuft, wird getroffen; wer
    abrupt stehen bleibt, entgeht dem Wurf."""
    from game.battle import Projectile
    b = Battle(raid(16, (8.0, 3.0)), random.Random(3), army=army_of(GroupSpec("H", [Tier("mittel", 20)])))
    (hop,) = b.units(Side.STADT)
    man = hop.all_men()[0]
    man.x, man.y, man.vx, man.vy = 8.0, 9.0, 3.0, 0.0                    # läuft nach Osten
    for k in ("MISSILE_SPREAD", "MISSILE_SPREAD_DIST", "MISSILE_LEAD_ERROR"):
        monkeypatch.setattr(config, k, 0.0)
    (tx, ty), flight = b._aim((8.0, 5.5), man)
    assert tx > 8.0 + 3.0 * 0.2 and abs(tx - (8.0 + 3.0 * flight)) < 0.05 and ty == 9.0   # vorgehalten

    def throw(runs_on: bool) -> float:
        man.x, man.y, man.hp = 8.0, 9.0, man.kind.hp
        b.projectiles = [Projectile(8.0, 5.5, tx, ty, hop.id, 0.2, 0.0, flight, man)]
        for u in b.lochoi:
            u.volley_timer = 99.0
        if runs_on:
            man.x = tx
        b._volleys(flight + 0.01)
        return man.kind.hp - man.hp
    assert throw(True) > 0.0                                            # weitergelaufen: getroffen
    assert throw(False) == 0.0                                          # stehen geblieben: daneben


def hunt_field():
    """Reiter des Spielers in der Mitte, die Räuber weit weg und still."""
    b = Battle(raid(16, (2.0, 2.0)), random.Random(2), army=army_of(GroupSpec("R", [Tier("reiter", 16)])))
    b._ai_raiders = lambda: None
    b._check_outcome = lambda: None
    b.alarm = False
    (cav,) = b.units(Side.STADT)
    cav.x, cav.y, cav.facing = 8.0, 12.0, (0.0, -1.0)
    cav.place_men()
    for r in b.units(Side.FEIND):
        r.x, r.y, r.target, r.stance = 1.0, 1.0, None, Stance.HALTEN
        r.place_men()
    return b, cav


def test_hunting_cavalry_rides_down_fleeing_foes_and_rides_back():
    b, cav = hunt_field()
    prey = b.units(Side.FEIND)[0]
    prey.x, prey.y = 9.0, 7.0
    prey.place_men()
    prey.stance, prey.target = Stance.FLUCHT, (9.0, 7.0)              # flieht, steht aber noch auf dem Feld
    assert b.command_hunt([cav]) == 1 and cav.mode == "jagen"
    men0 = prey.men
    for _ in range(int(6 / DT)):
        prey.stance, prey.target = Stance.FLUCHT, (9.0, 7.0)
        b.update(DT)
    assert prey.men < men0                                             # eingeholt und niedergeritten
    for r in b.units(Side.FEIND):                                     # nun ist nichts mehr zu jagen
        r.x, r.y = 1.0, 1.0
        r.place_men()
        r.stance, r.target = Stance.HALTEN, None
    run(b, 12)
    assert math.dist(cav.pos, (8.0, 12.0)) < 1.0 and cav.mode == "jagen"   # zurück an seinem Platz, weiter auf der Lauer


def test_hunting_cavalry_never_charges_a_closed_phalanx():
    b, cav = hunt_field()
    wall = b._spawn(Side.FEIND, arrange(men("schwer", 16), 8), 8.0, 9.0, "Phalanx")
    wall.facing = (0.0, 1.0)
    wall.place_men()
    wall.stance, wall.in_line, wall.target = Stance.PHALANX, True, wall.pos
    b.command_hunt([cav])
    run(b, 5)
    assert not cav.engaged and wall.men == 16 and math.dist(cav.pos, (8.0, 12.0)) < 0.6
    wall.in_line = False                                               # ungeordnet: nun lohnt der Stoß
    wall.stance = Stance.HALTEN
    for _ in range(int(5 / DT)):
        b.update(DT)
        wall.in_line = False
        if cav.engaged:
            break
    assert cav.engaged or cav.target_id == wall.id


def test_only_cavalry_hunts():
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0))
    hop, pelt, cav = b.units(Side.STADT)
    assert b.command_hunt([hop, pelt]) == 0 and hop.mode == "" and pelt.mode == ""
    assert b.command_hunt([hop, pelt, cav]) == 1 and cav.mode == "jagen"
    b.command_move([cav], (8.0, 10.0))
    assert cav.mode == ""                                              # ein neuer Befehl beendet die Jagd


def test_split_makes_two_groups_that_move_on_their_own():
    """Teilen: Links und rechts der Mitte werden zwei Gruppen, jede mit ihrer Tiefe und ihrer
    Ordnung; niemand verlässt dabei seinen Platz, und beide lassen sich getrennt führen."""
    b, u = standing_group("mittel", 24, 8)
    b.alarm = False
    before = {id(m): m.pos for m in u.all_men()}
    depth = len(u.rows)
    g = b.command_split(u)
    assert g is not None and g in b.lochoi and g.side is u.side
    assert u.men == 12 and g.men == 12 and len(u.rows) == len(g.rows) == depth
    assert all(dist_of_pt(m.pos, before[id(m)]) < 1e-9 for m in u.all_men() + g.all_men())   # alle bleiben stehen
    assert max(m.x for m in g.all_men()) < min(m.x for m in u.all_men())    # die neue Gruppe links
    b.command_move([g], (4.0, 12.0))
    b.command_move([u], (12.0, 12.0))
    run(b, 8)
    assert g.x < 5.0 and u.x > 11.0
    small = standing_group("mittel", 5, 5)[1]
    assert b.command_split(small) is None                                    # zu klein


def test_split_keeps_the_leader_and_the_losses():
    army = army_of(GroupSpec("H", [Tier("schwer", 10), Tier("mittel", 10)], leader=True))
    b = Battle(raid(16, (8.0, 1.0)), random.Random(0), army=army, ai="einfach")
    u = b.units(Side.STADT)[0]
    u.men_start = u.men + 10                                                 # schon zehn verloren
    g = b.command_split(u)
    assert u.leader_man() is not None and g.leader_man() is None
    assert u.men_start + g.men_start >= u.men + g.men + 9


def test_split_halves_merge_back_into_one_group():
    """Zwei gleiche Gruppen (etwa die Hälften einer geteilten) lassen sich wieder vereinen: eine
    Gruppe, so breit wie beide nebeneinander, vorn die Schweren, die Verluste zählen weiter.
    Verschiedene Gattungen lassen sich nicht vereinen."""
    army = army_of(GroupSpec("H", [Tier("schwer", 10), Tier("mittel", 10)], leader=True),
                   GroupSpec("R", [Tier("reiter", 12)]))
    b = Battle(raid(16, (8.0, 1.0)), random.Random(0), army=army, ai="einfach")
    hop, cav = b.units(Side.STADT)
    width, men = hop.width, hop.men
    half = b.command_split(hop)
    keep = b.command_merge([hop, half])
    assert keep is hop and half not in b.lochoi and hop.men == men and hop.width == width
    assert hop.leader_man() is not None and all(m.kind.key == "schwer" for m in hop.rows[0])
    assert b.command_merge([hop, cav]) is None                              # Hopliten und Reiter nicht
    run(b, 4)
    assert hop.in_line


def test_drill_command_forms_up_in_place_and_only_for_hoplites():
    b = Battle(raid(16, (8.0, 3.0)), random.Random(0))
    b._ai_raiders = lambda: None
    hop, pelt, cav = b.units(Side.STADT)
    hop.drill = "locker"
    assert b.command_drill([hop, pelt, cav], "phalanx") == 1
    assert hop.drill == "phalanx" and hop.stance is Stance.PHALANX and hop.target == hop.pos
    assert b.command_drill([pelt, cav], "locker") == 0                # andere Gattungen: ohne Modi
    run(b, 3)
    assert hop.in_phalanx
    b.command_drill([hop], "locker")
    run(b, 2)
    assert not hop.in_phalanx and hop.on_slots(0.25)


# ------------------------------------------------------------- Verbände
def verband_battle():
    b = Battle(raid(16, (8.0, 1.0)), random.Random(0))
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    for r in b.units(Side.FEIND):
        r.x, r.y, r.target, r.stance = 1.0, 1.0, None, Stance.HALTEN
        r.place_men()
    return b


def test_verband_forms_in_battle_order_and_marches_together():
    """Ein Verband stellt sich in Schlachtordnung auf (Hopliten vorn, Reiter rechts daneben,
    Peltasten dahinter) und marschiert im Tempo der langsamsten Gruppe: Die Reiter laufen
    den Hopliten nicht davon, am Ziel steht die Ordnung wieder."""
    b = verband_battle()
    hop, pelt, cav = b.units(Side.STADT)
    v = b.command_verband([hop, pelt, cav])
    assert v.rows == [[hop.id, cav.id], [pelt.id]]
    assert b.selected_verband({hop.id, pelt.id, cav.id}) is v and b.selected_verband({hop.id, cav.id}) is None
    run(b, 6)
    b.command_verband_move(v, (8.0, 6.0))
    spread = 0.0
    for _ in range(int(14 / DT)):
        b.update(DT)
        spread = max(spread, abs(cav.y - hop.y))
    assert spread < 1.0                                               # nebeneinander, nicht vorausgeritten
    assert v.facing[1] < -0.9                                         # Front in Marschrichtung (Norden)
    assert pelt.y > hop.y + hop.half_d and cav.x > hop.x              # Peltasten dahinter, Reiter rechts
    assert abs((hop.y - hop.half_d) - (cav.y - cav.half_d)) < 0.1     # die Fronten bündig
    assert hop.in_phalanx and dist_of_pt(v.centre, (8.0, 6.0)) < 1e-6


def test_verband_rows_can_be_rearranged_and_dissolved():
    b = verband_battle()
    hop, pelt, cav = b.units(Side.STADT)
    v = b.command_verband([hop, pelt, cav])
    b.set_verband_rows(v, [[pelt.id], [cav.id, hop.id]])               # Peltasten vorn, Reiter links hinten
    run(b, 12)
    assert v.rows == [[pelt.id], [cav.id, hop.id]]
    assert pelt.y < hop.y and cav.x < hop.x
    b.command_leave_verband([pelt])                                   # eine Gruppe geht: zwei bleiben
    assert b.verband_of(pelt) is None and v.members() == [cav.id, hop.id]
    b.command_drill([hop], "locker")                                  # Modi gelten weiter je Gruppe
    assert hop.drill == "locker" and b.verband_of(hop) is v
    b.command_dissolve_verband(v)
    assert b.verbaende == []


def test_verband_ring_puts_the_front_row_outside():
    b = verband_battle()
    hop, pelt, cav = b.units(Side.STADT)
    v = b.command_verband([hop, pelt, cav])
    b.command_verband_formation(v, "o")
    run(b, 15)
    assert hop.formation == cav.formation == pelt.formation == "o"
    assert hop.ring_size > cav.ring_size > pelt.ring_size                # vorn außen, dann Reiter, Peltasten innen
    assert dist_of(hop, cav) < 0.2 and dist_of(hop, pelt) < 0.2         # eine Mitte
    assert hop.in_phalanx


def test_verband_member_returns_after_its_storm():
    """Wer aus dem Verband heraus stürmt, kehrt an seinen Platz zurück, sobald kein
    kämpfender Feind mehr in der Nähe ist. Ein einzeln befohlener Marsch lässt die
    Gruppe im Verband (nächster Befehl an den Verband stellt sie wieder auf)."""
    b = verband_battle()
    hop, pelt, cav = b.units(Side.STADT)
    v = b.command_verband([hop, pelt, cav])
    run(b, 6)
    home = v.slots[hop.id].center
    b.command_attack([hop])
    assert hop.free_attack
    hop.stormed = True                                               # war im Handgemenge; der Feind ist weit weg
    b.update(DT)
    assert not hop.free_attack and hop.target == home and hop.stance is Stance.PHALANX
    b.command_move([cav], (12.0, 12.0))
    assert b.verband_of(cav) is v


def test_men_trapped_in_an_own_block_slip_out_to_their_places():
    """Stellt sich ein Verband um (die Peltasten nach vorn), können einzelne Männer in den
    Blöcken der anderen eingeschlossen werden: Sie schlüpfen durch deren Reihen hinaus, und
    wer am Ziel steht, aber nicht an seine Plätze kommt, löst sich auf und sucht den Weg."""
    scn = Scenario("t", "t", "", role="verteidigung", enemy_kind="raeuber", enemy_default=4, enemy_min=4,
                   enemy_max=4, houses=(), raider_spawns=(RaiderSpawn(1.0, 1.0),), cols=24, rows=24, deploy_y=12.0)
    b = Battle(scn, random.Random(1))
    b._ai_raiders = lambda: None
    b._check_outcome = lambda: None
    b.alarm = False
    for r in b.units(Side.FEIND):
        r.withdrawn = True
    hop, pelt, cav = b.units(Side.STADT)
    v = b.command_verband([hop, pelt, cav])
    run(b, 5)
    b.command_verband_formation(v, "o")
    run(b, 5)
    b.command_verband_formation(v, "linie")
    run(b, 5)
    b.set_verband_rows(v, [[pelt.id], [cav.id, hop.id]])
    run(b, 20)
    assert all(u.in_line and not u.loose for u in (hop, pelt, cav))


def test_peltasts_stay_on_the_wall_when_there_is_no_way_down_outside():
    """Die Leitern führen nur zur Innenseite: Ist das Tor zu, steigen Peltasten, die nach
    draußen sollen, auf den Wehrgang darüber, statt endlos auf und ab zu klettern;
    Hopliten warten am Tor."""
    b = Battle(PALISADE, random.Random(1))
    b._ai_raiders = lambda: None
    b._check_outcome = lambda: None
    b.alarm = False
    for r in b.units(Side.FEIND):
        r.withdrawn = True
    hop, pelt, cav = b.units(Side.STADT)
    b.command_move([pelt], (8.0, 4.0))
    assert any("kein Weg hinab" in e for e in b.events)
    run(b, 12)
    assert b.on_wall(pelt) and not pelt.loose
    b.command_move([hop], (8.0, 4.0))
    assert any("das Tor ist zu" in e for e in b.events)


def test_a_group_sent_next_to_a_house_moves_clear_of_it():
    """Liegt das angetippte Ziel so nah an einem Haus, dass Plätze im Haus lägen, rückt die
    Gruppe daneben: Alle Männer finden ihren Platz, keiner steht daneben herum."""
    b = Battle(raid(16, (8.0, 1.0), houses=((8, 6), (9, 6))), random.Random(0))
    b._ai_raiders = lambda: None
    b.alarm = False
    hop, pelt, cav = b.units(Side.STADT)
    b.command_move([hop], (8.9, 7.1))
    assert not any(b.is_blocked(*p) for _, p in hop.slots_at(hop.target, (0.0, -1.0)))
    run(b, 8)
    assert all(dist_of_pt(m.pos, p) <= 0.3 for m, p in hop.slots())


def test_a_jammed_block_dissolves_and_finds_its_way():
    """Kommt ein Block mit Ziel zwei Sekunden lang nicht vom Fleck (etwa zwischen zwei
    ruhenden eigenen Gruppen), löst er sich auf, und jeder Mann sucht seinen Weg; er bleibt
    aufgelöst, bis die Männer an ihren Plätzen sind."""
    b = Battle(raid(16, (8.0, 1.0)), random.Random(0))
    b._ai_raiders = lambda: None
    b.alarm = False
    hop, pelt, cav = b.units(Side.STADT)
    b.command_move([hop], (hop.x, hop.y - 3.0))
    b._own_in_the_way = lambda u, p: True          # festgefahren
    run(b, 3.5)
    assert hop.loose and hop.stay_loose
