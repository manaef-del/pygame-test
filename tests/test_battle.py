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
    assert 0 < len(b.projectiles) <= 15      # erste Salve unterwegs
    assert raider.men == 16                  # noch kein Einschlag
    assert pelt.ammo() == 15 * config.JAVELINS - 15
    run(b, 3.0)
    assert raider.men < 16                   # Speere sind angekommen
    run(b, 20.0)
    assert pelt.ammo() == 0
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
    b = Battle(PALISADE, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    b.command_line([hop], (5.5, 9.5), (10.5, 9.5))     # Hopliten hinter dem Tor
    b.command_line([pelt], (5.5, 10.6), (10.5, 10.6))  # Peltasten werfen darüber
    b.command_move([cav], (13.0, 12.5))                # Reiter in Reserve
    run(b, 240)
    r = b.report()
    assert r["ausgang"] == "sieg", r
    assert r["feind_start"] > 2 * r["stadt_start"]
    assert r["stadt_gefallen"] <= 0.2 * r["stadt_start"], r
    assert r["haeuser_intakt"] == r["haeuser"]


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
    assert all(6 <= u.men <= 16 for u in small.units(Side.FEIND))
    assert len(big.units(Side.FEIND)) == 12


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


def test_each_group_builds_its_own_engine():
    b = Battle(SIEDLUNG_WALL, random.Random(1))
    hop, pelt, cav = b.units(Side.STADT)
    assert b.command_build([hop, cav], "ram") == 2
    run(b, config.RAM_BUILD_TIME + 1)
    assert hop.engine == "ram" and cav.engine == "ram" and pelt.engine is None


def test_siege_tower_opens_a_crossing():
    b = Battle(SIEDLUNG_WALL, random.Random(1))
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
    assert not b.is_blocked(13.5, 7.5, hop)               # Übergang für alle
    assert cav.engine is None                             # Turm ist verbaut
    run(b, 6)
    assert cav.fighting and cav.y < 7.0                   # Reiter sind drüben


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
    run(b, 12)
    assert b.on_wall(pelt)
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
