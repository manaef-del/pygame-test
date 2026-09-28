"""Tests der Kampflogik. Läuft ohne Pygame."""

import random

import pytest

from game import config
from game.army import POOL, Army, GroupSpec, default_army
from game.battle import Battle
from game.geometry import arc, snap4
from game.scenarios import OFFENE_SIEDLUNG, PALISADE, EnemySpec, Scenario
from game.units import UNIT_TYPES, Lochos, Man, Side, Stance

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


def static_line(raider_y: float, n_raiders: int = 4) -> Battle:
    """Drei Hoplitengruppen in der Linie (Front Nord), Räuber dicht davor oder dahinter."""
    scn = Scenario(
        "t", "t", "", houses=((2, 17),),
        enemies=tuple(EnemySpec(16, 5.3 + i * 1.7, raider_y) for i in range(n_raiders)),
    )
    army = army_of(
        GroupSpec("A", [{"schwer": 7}, {"mittel": 7}, {}]),
        GroupSpec("B", [{"schwer": 7}, {"mittel": 6}, {}]),
        GroupSpec("C", [{"mittel": 7}, {"leicht": 6}, {}]),
    )
    b = Battle(scn, random.Random(0), army=army)
    for i, u in enumerate(b.units(Side.STADT)):
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
def test_default_army_uses_whole_pool():
    a = default_army()
    assert a.valid()
    assert all(a.remaining(k) == 0 for k in POOL)
    assert a.total_men() == sum(POOL.values()) == 75


def test_army_respects_pool_and_row_limit():
    a = Army(groups=[GroupSpec("G", [{}, {}, {}])])
    for _ in range(POOL["reiter"]):
        assert a.add(0, 0, "reiter") or a.add(0, 1, "reiter") or a.add(0, 2, "reiter")
    assert a.remaining("reiter") == 0
    assert a.add(0, 2, "reiter") is False
    assert a.groups[0].row_size(0) == 8
    assert a.remove(0, 0, "reiter") and a.remaining("reiter") == 1
    assert a.remove(0, 1, "schwer") is False


def test_rows_build_men_with_types():
    g = GroupSpec("G", [{"schwer": 2, "peltast": 1}, {"reiter": 3}, {}])
    rows = g.build_rows()
    assert [len(r) for r in rows] == [3, 3]
    assert [m.kind.key for m in rows[0]] == ["schwer", "schwer", "peltast"]


def test_battle_deploys_army_groups():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    city = b.units(Side.STADT)
    assert [u.name for u in city] == [g.name for g in default_army().groups]
    assert b.men(Side.STADT) == 75
    assert all(0 < u.x < config.COLS for u in city)
    assert len({round(u.x, 1) for u in city}) == len(city)


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
    assert u.ranged_attack(engaged=True) == pytest.approx(4 * 0.6)
    front = Lochos(2, Side.STADT, [men("peltast", 4), men("schwer", 4)], 0, 0)
    assert front.ranged_attack(engaged=True) == 0.0
    assert front.ranged_attack(engaged=False) == pytest.approx(4 * 0.6)


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
    cav = next(u for u in b.units(Side.STADT) if u.name == "Reiter links")
    b.command_move([cav], (2.0, 5.0))
    assert cav.stance is Stance.HALTEN and cav.target == (2.0, 5.0)
    others = [u for u in b.units(Side.STADT) if u is not cav]
    assert all(u.target is None for u in others)
    run(b, 3)
    assert abs(cav.x - 2.0) < 0.5 and abs(cav.y - 5.0) < 0.5
    foe = b.units(Side.FEIND)[0]
    b.command_attack_target([cav], foe)
    assert cav.stance is Stance.ANGRIFF and cav.target_id == foe.id
    run(b, 6)
    assert foe.men < 16 or cav.engaged


def test_command_phalanx_for_selection_only():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    hoplites = [u for u in b.units(Side.STADT) if u.name.startswith("Phalanx")]
    order = b.command_phalanx(3.0, 10.0, 13.0, 11.0, units=hoplites)
    assert order.facing == (0.0, -1.0)
    assert len(order.slots) == 3
    assert all(u.stance is Stance.PHALANX for u in hoplites)
    assert all(u.stance is Stance.HALTEN for u in b.units(Side.STADT) if u not in hoplites)
    run(b, 8)
    assert all(u.in_line for u in hoplites)


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
    b.command_phalanx(4.5, 9.0, 11.5, 10.0)
    run(b, 240)
    r = b.report()
    assert r["ausgang"] == "sieg", r
    assert r["feind_start"] > 2 * r["stadt_start"]
    assert r["stadt_gefallen"] <= 0.2 * r["stadt_start"], r
    assert r["haeuser_intakt"] == r["haeuser"]


def test_open_settlement_phalanx_then_pursuit_wins():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    b.command_phalanx(3.0, 10.0, 13.0, 11.0)
    run(b, 14)
    b.command_attack()
    run(b, 240)
    assert b.outcome == "sieg", b.report()


def test_weak_army_loses_houses():
    """Ein kleiner Haufen hält den Überfall nicht auf."""
    small = army_of(GroupSpec("Wache", [{"leicht": 6}, {}, {}]))
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
    assert final is False and abs(goal[0] - b.gate_center[0]) < 1e-6


def test_nobody_enters_palisade_tiles():
    b = Battle(PALISADE, random.Random(3))
    b.command_attack()
    for _ in range(int(120 / DT)):
        b.update(DT)
        for u in b.lochoi:
            if u.alive and b.inside(u.x, u.y):
                assert not b.is_blocked(u.x, u.y), (u.name, u.x, u.y)
        if b.outcome:
            break


def test_deterministic_with_seed():
    a = Battle(OFFENE_SIEDLUNG, random.Random(7))
    c = Battle(OFFENE_SIEDLUNG, random.Random(7))
    for b in (a, c):
        b.command_phalanx(3.0, 10.0, 13.0, 11.0)
        run(b, 60)
    assert a.report() == c.report()
