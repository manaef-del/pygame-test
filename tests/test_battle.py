"""Tests der Kampflogik. Läuft ohne Pygame."""

import random

import pytest

from game import config
from game.army import POOL, Army, GroupSpec, Tier, default_army, scaled_army
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
    """Drei Hoplitengruppen in der Linie (Front Nord), Räuber dicht davor oder dahinter."""
    scn = raid(16 * n_raiders, *((5.3 + i * 1.7, raider_y) for i in range(n_raiders)))
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
    for u in b.units(Side.FEIND):
        u.stance = Stance.ANGRIFF
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
    assert all(a.remaining(k) == 0 for k in POOL)
    assert a.total_men() == sum(POOL.values()) == 75


def test_army_blocks_respect_pool():
    a = Army(groups=[GroupSpec("G", [Tier("reiter", 5)])])
    assert a.max_for(0, 0) == POOL["reiter"]
    assert a.set_count(0, 0, 50) == POOL["reiter"]          # wird gekappt
    assert a.remaining("reiter") == 0
    a.add_tier(0)
    assert a.groups[0].tiers[1].kind == "schwer" and a.groups[0].tiers[1].count == 5
    a.set_kind(0, 1, "reiter")                               # kein Reiter mehr frei
    assert a.groups[0].tiers[1].count == 0
    a.move_tier(0, 1, -1)
    assert [t.kind for t in a.groups[0].tiers] == ["reiter", "reiter"]
    a.remove_tier(0, 0)
    assert len(a.groups[0].tiers) == 1 and a.remaining("reiter") == 0


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
    assert b.men(Side.STADT) == 75
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
    b = static_line(raider_y=8.4, n_raiders=1)
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
    b = static_line(raider_y=8.4)
    resolve_only(b, 40)
    assert b.fallen(Side.STADT) <= 10, b.report()
    assert b.men(Side.FEIND, fighting_only=True) < 32, b.report()


def test_phalanx_breaks_from_the_rear():
    front = static_line(raider_y=8.4)
    rear = static_line(raider_y=10.6)
    resolve_only(front, 20)
    resolve_only(rear, 20)
    assert rear.fallen(Side.STADT) > 2 * front.fallen(Side.STADT), (front.report(), rear.report())
    assert rear.fallen(Side.FEIND) < front.fallen(Side.FEIND)


def test_cavalry_weak_against_phalanx_front_strong_in_the_open():
    b = static_line(raider_y=8.4, n_raiders=1)
    hoplit = b.units(Side.STADT)[1]
    cav = Lochos(99, Side.FEIND, [men("reiter", 8)], hoplit.x, 8.4)
    b.lochoi.append(cav)
    front_rate, _ = b._melee_rate(cav, hoplit)
    hoplit.stance = Stance.HALTEN
    hoplit.in_line = False
    open_rate, _ = b._melee_rate(cav, hoplit)
    assert open_rate > 4 * front_rate


def test_routed_units_take_double_damage():
    b = static_line(raider_y=8.4, n_raiders=1)
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
    """Phalanx hinter dem Tor, Peltasten auf dem Wehrgang, Reiter als Reserve gegen
    alles, was über den Turm hereinkommt; die Phalanx dreht sich zum nächsten Feind."""
    b = Battle(PALISADE, random.Random(1), enemy_count=112)
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (5.5, 9.5), (10.5, 9.5))     # Hopliten hinter dem Tor
    b.command_move([pelt], (3.5, 8.5))                 # Peltasten auf den Wehrgang
    b.command_move([cav], (13.0, 12.5))                # Reiter in Reserve
    gy = b.gate.center[1]
    covered = False
    for i in range(int(300 / DT)):
        b.update(DT)
        if b.outcome:
            break
        if i % 150 == 0:                                # alle fünf Sekunden schaut der Spieler hin
            if b.crossings and not covered and hop.fighting:
                # ein Turm steht: die Phalanx an den Fuß der nächsten Leiter, Front zum Wall
                cx = next(iter(b.crossings))[0] + 0.5
                lx, ly = min(b.ladders, key=lambda c: abs(c[0] + 0.5 - cx))
                b.command_line([hop], (lx + 0.5 - 2.2, ly + 1.7), (lx + 0.5 + 2.2, ly + 1.7))
                covered = True
            inside = [f for f in b.units(Side.FEIND, fighting_only=True) if f.y > gy + 0.5 and not b.on_wall(f)
                      and hop.rect_distance(f.pos) > 1.5]
            if inside and cav.fighting:
                b.command_attack_target([cav], min(inside, key=lambda f: dist_of(f, cav)))
    r = b.report()
    assert r["ausgang"] == "sieg", r
    assert r["feind_start"] >= 1.3 * r["stadt_start"]
    assert r["stadt_gefallen"] <= 0.4 * r["stadt_start"], r   # die Räuber kommen auch über einen Turm
    assert r["feind_gefallen"] >= 0.4 * r["feind_start"], r
    assert r["haeuser_intakt"] >= 1                            # ohne Reserve plündern die Eingesickerten


def test_open_settlement_phalanx_then_pursuit_wins():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    b.command_line(None, (3.0, 10.5), (13.0, 10.5))
    run(b, 14)
    b.command_attack()
    run(b, 240)
    assert b.outcome == "sieg", b.report()


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
    b = Battle(SIEDLUNG_OFFEN, random.Random(1), enemy_count=50)
    assert b.men(Side.FEIND) == 50
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
    b = Battle(SIEDLUNG_OFFEN, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    b.command_move([cav], (4.5, 8.0))
    run(b, 6)
    enemy = {u.name: u for u in b.units(Side.FEIND)}
    assert enemy["Hopliten"].stance is Stance.PHALANX and enemy["Hopliten"].in_line
    assert enemy["Reiter"].stance is Stance.ANGRIFF


def test_closed_gate_blocks_and_ram_opens_it():
    b = Battle(SIEDLUNG_WALL, random.Random(1))
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
    b = Battle(SIEDLUNG_WALL, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    assert b.command_build([hop, cav], "ram") == 2
    run(b, config.RAM_BUILD_TIME + 1)
    assert hop.engine == "ram" and cav.engine == "ram" and pelt.engine is None


def test_siege_tower_opens_a_crossing():
    b = Battle(SIEDLUNG_WALL, random.Random(1), ai="einfach")   # Mechanik, nicht Gegnerverhalten
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
    b = Battle(SIEDLUNG_WALL, random.Random(1))
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
    # Auf dem Wall: weiter werfen, im Nahkampf geschützt
    raider.x, raider.y = pelt.x, pelt.y + 1.0
    assert b._in_contact(raider, pelt)
    rate_up, _ = b._melee_rate(raider, pelt)
    pelt_off = Lochos(99, Side.STADT, [men("peltast", 15)], pelt.x, pelt.y + 2.5)
    b.lochoi.append(pelt_off)
    raider.y = pelt_off.y + 1.0
    rate_ground, _ = b._melee_rate(raider, pelt_off)
    assert rate_up == pytest.approx(rate_ground * config.WALL_MELEE_FACTOR)


def test_enemy_peltasts_start_on_the_wall():
    b = Battle(SIEDLUNG_WALL, random.Random(1))
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
    b = Battle(SIEDLUNG_WALL, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    b.gate.closed = False
    b.gate.hp = 0.0
    b.command_move([hop], (8.0, 3.5))
    for _ in range(int(30 / DT)):
        b.update(DT)
        for m in hop.all_men():
            assert b.cell(m.x, m.y) not in b.blocked            # niemand steckt in der Palisade
    assert all(m.y < 7.0 for m in hop.all_men())               # alle sind hindurch


def test_cavalry_dismounts_for_siege_work_and_before_ladders():
    b = Battle(SIEDLUNG_WALL, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    assert cav.speed == UNIT_TYPES["reiter"].speed
    b.command_build([cav], "tower")
    assert cav.mounted_men() == [] and len(b.horses) == 1 and b.horses[0][2] == 20
    assert cav.speed == pytest.approx(config.DISMOUNTED_SPEED)
    assert cav.cavalry_share() == 0.0                           # kein Reiterbonus mehr
    run(b, config.TOWER_BUILD_TIME + 1)
    assert cav.speed == pytest.approx(config.DISMOUNTED_SPEED * config.TOWER_SPEED_FACTOR)


def test_tower_is_one_way_up_from_outside():
    b = Battle(SIEDLUNG_WALL, random.Random(1))
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
    b = Battle(SIEDLUNG_WALL, random.Random(1), ai="einfach")
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
    b = Battle(SIEDLUNG_WALL, random.Random(1))
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
    before = {id(m): m.pos for m in hop.bound_men()}
    b.command_line([hop], (8.0, 9.0), (8.0, 11.0))        # Front nach Osten drehen, Zentrum bleibt in der Leine
    run(b, 4)                                             # (nach etwa sechs Sekunden brechen die Räuber)
    moved = [id(m) for m in hop.all_men() if id(m) in before and dist_of_pt(m.pos, before[id(m)]) > config.BOUND_SHUFFLE + 0.1]
    assert not moved                                      # gebundene Männer rücken höchstens nach, sie gehen nicht weg
    assert not hop.in_phalanx                             # solange Gebundene fehlen, keine Phalanx
    b.command_line([pelt], (9.5, 10.2), (6.5, 10.2))      # die Peltasten dürfen sich umformieren
    run(b, 6)
    assert pelt.in_phalanx


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
    run(b, config.DISENGAGE_TIME + 6.0)
    assert hop.disengage_until <= b.time                  # danach vorbei


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
