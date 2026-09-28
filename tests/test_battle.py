"""Tests der Kampflogik. Läuft ohne Pygame."""

import random

import pytest

from game import config
from game.battle import Battle
from game.geometry import arc, snap4
from game.scenarios import OFFENE_SIEDLUNG, PALISADE, Scenario, UnitSpec
from game.units import UNIT_TYPES, Lochos, Side, Stance

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


def static_line(raider_y: float, n_raiders: int = 6) -> Battle:
    """Drei Hopliten in der Linie (Front Nord), Räuber dicht davor oder dahinter."""
    scn = Scenario(
        "t", "t", "", houses=((2, 17),),
        player=tuple(UnitSpec("hoplit", 6.5 + i, 9.5) for i in range(3)),
        enemies=tuple(UnitSpec("raeuber", 5.9 + i * 0.65, raider_y) for i in range(n_raiders)),
    )
    b = Battle(scn, random.Random(0))
    for u in b.units(Side.STADT):
        u.stance = Stance.PHALANX
        u.in_line = True
        u.facing = (0.0, -1.0)
    for u in b.units(Side.FEIND):
        u.stance = Stance.ANGRIFF
    return b


# ------------------------------------------------------------- Geometrie
def test_arc_classification():
    f = (0.0, -1.0)  # Front Nord
    assert arc(f, (0.0, -1.0), 60, 120) == "front"
    assert arc(f, (0.5, -1.0), 60, 120) == "front"
    assert arc(f, (1.0, 0.0), 60, 120) == "flank"
    assert arc(f, (0.0, 1.0), 60, 120) == "rear"
    assert snap4((0.3, -0.9)) == (0.0, -1.0)
    assert snap4((-0.9, 0.2)) == (-1.0, 0.0)


# --------------------------------------------------------- Auflösung
def test_phalanx_holds_from_the_front():
    b = static_line(raider_y=8.6)
    resolve_only(b, 40)
    assert b.men(Side.STADT) >= 18, b.report()            # höchstens ein Viertel verloren
    assert b.men(Side.FEIND, fighting_only=True) < 24, b.report()  # Räuber gebrochen


def test_phalanx_breaks_from_the_rear():
    front = static_line(raider_y=8.6)
    rear = static_line(raider_y=10.4)
    resolve_only(front, 20)
    resolve_only(rear, 20)
    assert rear.fallen(Side.STADT) > 2 * front.fallen(Side.STADT), (front.report(), rear.report())
    assert rear.fallen(Side.FEIND) < front.fallen(Side.FEIND)


def test_cavalry_is_weak_against_phalanx_front():
    b = static_line(raider_y=8.6, n_raiders=0)
    hoplit = b.units(Side.STADT)[1]
    cav = Lochos(id=99, side=Side.FEIND, kind=UNIT_TYPES["hippeus"], x=7.5, y=8.6)
    b.lochoi.append(cav)
    front_rate, _ = b._melee_rate(cav, hoplit)
    cav.x, cav.y = 7.5, 10.4
    rear_rate, _ = b._melee_rate(cav, hoplit)
    assert rear_rate > 10 * front_rate


def test_routed_units_take_double_damage_and_flee():
    b = static_line(raider_y=8.6, n_raiders=1)
    raider = b.units(Side.FEIND)[0]
    hoplit = b.units(Side.STADT)[1]
    normal, _ = b._melee_rate(hoplit, raider)
    raider.stance = Stance.FLUCHT
    fleeing, _ = b._melee_rate(hoplit, raider)
    assert fleeing == pytest.approx(normal * config.ROUTED_DAMAGE)


# ----------------------------------------------------------- Befehle
def test_command_phalanx_builds_line_facing_enemy():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    order = b.command_phalanx(5.0, 10.0, 10.0, 11.0)
    assert order.facing == (0.0, -1.0)         # Räuber kommen von Norden
    assert len(order.slots) == 4               # 3 Hopliten + 1 Leichter
    assert all(abs(s[1] - 10.5) < 1e-6 for s in order.slots)
    thet = next(u for u in b.units(Side.STADT) if u.kind.key == "thet")
    assert thet.stance is Stance.HALTEN and thet.target[1] > 10.5  # hinter der Linie
    run(b, 6)
    assert all(u.in_line for u in b.units(Side.STADT) if u.kind.can_phalanx)


def test_alarm_waits_for_first_command():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    run(b, 5)
    assert b.time == 0.0
    b.command_hold()
    run(b, 1)
    assert b.time > 0.9


# --------------------------------------------------------- Szenarien
def test_unopposed_raiders_loot_every_house():
    scn = Scenario("t", "t", "", houses=OFFENE_SIEDLUNG.houses, player=(), enemies=OFFENE_SIEDLUNG.enemies)
    b = Battle(scn, random.Random(1))
    b.alarm = False
    run(b, 200)
    assert b.outcome == "niederlage"
    assert b.houses_intact() == 0


def test_phalanx_behind_palisade_beats_larger_force():
    b = Battle(PALISADE, random.Random(1))
    b.command_phalanx(5.5, 9.0, 10.5, 10.0)
    run(b, 240)
    r = b.report()
    assert r["ausgang"] == "sieg", r
    assert r["feind_start"] > 1.5 * r["stadt_start"]
    assert r["stadt_gefallen"] <= 0.25 * r["stadt_start"], r
    assert r["haeuser_intakt"] == r["haeuser"]


def test_open_settlement_phalanx_then_pursuit_wins():
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    b.command_phalanx(4.5, 10.0, 11.5, 11.0)
    run(b, 14)
    b.command_attack()
    run(b, 240)
    assert b.outcome == "sieg", b.report()


def test_raid_on_open_settlement_hurts():
    """Ohne Befehle wird geplündert."""
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    b.command_hold()
    run(b, 240)
    assert b.houses_intact() < len(b.houses) or b.fallen(Side.STADT) > 0


# ------------------------------------------------------------ Routing
def test_route_goes_through_the_gate():
    b = Battle(PALISADE, random.Random(1))
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 2.5, 6.5
    assert not b.path_clear(raider.pos, (2.5, 12.5))
    goal, final = b.route(raider, (2.5, 12.5))
    assert final is False
    assert abs(goal[0] - b.gate_center[0]) < 1e-6
    # Freies Feld: direkter Weg
    open_b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    u = open_b.units(Side.FEIND)[0]
    assert open_b.route(u, (5.0, 12.0)) == ((5.0, 12.0), True)


def test_nobody_enters_palisade_tiles():
    b = Battle(PALISADE, random.Random(3))
    b.command_attack()
    for _ in range(int(120 / DT)):
        b.update(DT)
        for u in b.lochoi:
            if u.alive and b.inside(u.x, u.y):
                assert not b.is_blocked(u.x, u.y), (u.kind.key, u.x, u.y)
        if b.outcome:
            break


def test_deterministic_with_seed():
    a = Battle(OFFENE_SIEDLUNG, random.Random(7))
    c = Battle(OFFENE_SIEDLUNG, random.Random(7))
    for b in (a, c):
        b.command_phalanx(4.5, 10.0, 11.5, 11.0)
        run(b, 60)
    assert a.report() == c.report()
    assert [(u.x, u.y, u.men) for u in a.lochoi] == [(u.x, u.y, u.men) for u in c.lochoi]
