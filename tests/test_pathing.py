"""Eigene Wege der Männer: Zielaufstellung fest, jeder Mann geht für sich dorthin."""

import random

from game import config, pathing
from game.army import Army, GroupSpec, Tier
from game.battle import Battle
from game.geometry import dist
from game.scenarios import SIEDLUNG_WALL, RaiderSpawn, Scenario
from game.units import Side, Stance

DT = 1 / 30


def run(b: Battle, seconds: float) -> None:
    for _ in range(int(seconds / DT)):
        b.update(DT)


def quiet_raid() -> Scenario:
    return Scenario("t", "t", "", role="verteidigung", enemy_kind="raeuber", enemy_default=8, enemy_min=8,
                    enemy_max=8, houses=((2, 17),), raider_spawns=(RaiderSpawn(1.0, 1.0),))


def line_and_block(block_at=(8.0, 11.5), block_width=14) -> tuple[Battle, object, object]:
    """Eine Phalanx (14 breit) steht bei (8, 9) auf ihrem Posten, ein Block dahinter."""
    army = Army(groups=[GroupSpec("Linie", [Tier("schwer", 14), Tier("mittel", 14)]),
                        GroupSpec("Block", [Tier("schwer", 14), Tier("mittel", 13), Tier("leicht", 13)])])
    b = Battle(quiet_raid(), random.Random(0), army=army, ai="einfach")
    b._ai_raiders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    line, block = b.units(Side.STADT)
    for u, pos, width, phalanx in ((line, (8.0, 9.0), 14, True), (block, block_at, block_width, False)):
        u.reform(width)
        u.x, u.y = pos
        u.facing = (0.0, -1.0)
        u.stance = Stance.PHALANX if phalanx else Stance.HALTEN
        u.target = pos if phalanx else None
        u.in_line = phalanx
        u.place_men()
    return b, line, block


def in_ranks(u, p) -> bool:
    """Steht ``p`` zwischen den Männern der Gruppe (im Rechteck ohne seinen Rand)?"""
    along, forward = u.local(p)
    return abs(along) < u.half_w - 0.08 and abs(forward) < u.half_d - 0.08


# ------------------------------------------------------------- Wegefeld
def test_field_leads_around_an_obstacle():
    blocked = bytearray(16 * 16)
    for x in range(2, 14):
        blocked[8 * 16 + x] = 1                            # eine Wand quer über die Mitte, offen an den Rändern
    f = pathing.Field(4.0, 4.0, 0.25, blocked, [(2.0, 0.5)])
    assert f.reachable((2.0, 3.5))
    assert not f.clear((2.0, 3.5), (2.0, 0.5))
    wp = f.waypoint((2.0, 3.5), (2.0, 0.5))
    assert wp[0] < 0.6 or wp[0] > 3.4                      # erst zum Ende der Wand, nicht hinein
    assert f.clear((2.0, 3.5), wp)


def test_field_marks_unreachable_cells():
    blocked = bytearray(16 * 16)
    for x in range(16):
        blocked[8 * 16 + x] = 1                            # ganz zu
    f = pathing.Field(4.0, 4.0, 0.25, blocked, [(2.0, 0.5)])
    assert not f.reachable((2.0, 3.5)) and not f.near_reachable((2.0, 3.5))


# -------------------------------------------------- Umgehen eigener Gruppen
def test_block_flows_around_a_standing_line_man_by_man():
    """Der Block löst sich vor der stehenden Linie auf, die Männer gehen links und
    rechts eng an ihr vorbei und schließen sich am Ziel wieder: kein großer Bogen,
    die Linie wird nicht verschoben, kein Mann tritt in sie hinein."""
    b, line, block = line_and_block()
    origin = [m.pos for m in line.all_men()]
    b.command_move([block], (8.0, 6.0))
    went_loose = False
    inside = False
    path = {id(m): 0.0 for m in block.all_men()}
    last = {id(m): m.pos for m in block.all_men()}
    for _ in range(int(12 / DT)):
        b.update(DT)
        went_loose = went_loose or block.loose
        inside = inside or any(in_ranks(line, m.pos) for m in block.all_men())
        closest = min(dist(m.pos, n.pos) for m in block.all_men() for n in line.all_men())
        assert closest >= 2 * config.MAN_RADIUS - 1e-6
        for m in block.all_men():
            path[id(m)] += dist(m.pos, last[id(m)])
            last[id(m)] = m.pos
    assert went_loose and not block.loose
    assert dist(block.pos, (8.0, 6.0)) < 0.05 and block.on_slots(0.2, 0.95)
    assert not inside
    assert max(dist(a, m.pos) for a, m in zip(origin, line.all_men())) < 1e-6
    assert sum(path.values()) / len(path) < 1.4 * 5.5, sum(path.values()) / len(path)   # vorher fast 14 Kacheln


def test_detour_stays_close_to_the_standing_group():
    """Wer an einer stehenden Gruppe vorbeigeht, hält nur wenig Abstand zu ihr."""
    b, line, block = line_and_block()
    b.command_move([block], (8.0, 6.0))
    widest = 0.0
    for _ in range(int(12 / DT)):
        b.update(DT)
        for m in block.all_men():
            if abs(m.y - line.y) < 0.3:                    # auf Höhe der Linie: wie weit außen?
                widest = max(widest, abs(m.x - line.x) - line.half_w)
    assert widest < 0.6, widest


def test_attack_stays_a_block():
    """Ein Angriff löst sich nicht auf, um eigene Gruppen herumzugehen: hinter
    kämpfenden steht man im Block an."""
    b, line, block = line_and_block()
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 8.0, 3.0
    raider.place_men()
    b.command_attack_target([block], raider)
    for _ in range(int(3 / DT)):
        b.update(DT)
        assert not block.loose


def test_dissolved_group_is_where_its_men_are():
    """Eine aufgelöste Gruppe ist dort, wo ihre Männer gehen, nicht am Ziel und nicht
    mitten in der Gruppe, um die sie herumgehen."""
    b, line, block = line_and_block()
    b.command_move([block], (8.0, 6.0))
    for _ in range(int(5 / DT)):
        b.update(DT)
        if block.loose:
            xs, ys = [m.x for m in block.all_men()], [m.y for m in block.all_men()]
            assert min(xs) - 0.1 <= block.x <= max(xs) + 0.1 and min(ys) - 0.1 <= block.y <= max(ys) + 0.1
            assert line.rect_distance(block.pos) > 0.0


# ------------------------------------------------------------ Über den Wall
def tower_battle() -> tuple[Battle, object]:
    b = Battle(SIEDLUNG_WALL, random.Random(1), ai="einfach", doctrine="spiegel", enemy_count=12)
    for i, e in enumerate(b.units(Side.FEIND)):
        e.x, e.y = 1.5 + i * 0.1, 0.8 + i * 0.1
        e.target = None
        e.stance = Stance.HALTEN
        e.place_men()
    b._ai_defenders = lambda: None
    b._volleys = lambda dt: None
    hop = b.units(Side.STADT)[0]
    b.command_build([hop], "tower")
    run(b, config.TOWER_BUILD_TIME + 1)
    b.command_tower_wall([hop], (9, 7))
    for _ in range(int(40 / DT)):
        b.update(DT)
        if b.crossings:
            break
    return b, hop


def test_over_the_wall_men_take_their_places_once():
    """Über den Turm: Wer drüben seinen Platz erreicht hat, bleibt dort. Die Gruppe
    springt nicht zu ihren Männern und schwenkt am Ende nicht; ihre Front zeigt vom
    Wall weg."""
    b, hop = tower_battle()
    b.command_move([hop], (7.0, 5.5))
    hist = {id(m): [] for m in hop.all_men()}
    for _ in range(int(40 / DT)):
        b.update(DT)
        for m in hop.all_men():
            hist[id(m)].append(m.pos)
        if not hop.loose and dist(hop.pos, (7.0, 5.5)) < 0.05 and hop.on_slots(0.2, 0.95):
            break
    assert not hop.loose and dist(hop.pos, (7.0, 5.5)) < 0.05
    assert hop.facing == (0.0, -1.0)
    w = int(1.0 / DT)
    rewalk = 0.0
    for h in hist.values():
        settled = next((j for j in range(w, len(h)) if dist(h[j - w], h[j]) < 0.02 and h[j][1] < 7.0), len(h) - 1)
        rewalk += sum(dist(h[j], h[j + 1]) for j in range(settled, len(h) - 1))
    assert rewalk / len(hist) < 0.15, rewalk / len(hist)
    assert any("neu gebildet" in e for e in b.events)


def test_gate_line_streams_through_and_forms():
    """Durchs offene Tor gehen die Männer einzeln und stellen sich drüben in die befohlene Linie."""
    b = Battle(SIEDLUNG_WALL, random.Random(1), ai="einfach", doctrine="spiegel", enemy_count=12)
    for i, e in enumerate(b.units(Side.FEIND)):
        e.x, e.y = 1.5 + i * 0.1, 0.8 + i * 0.1
        e.target = None
        e.stance = Stance.HALTEN
        e.place_men()
    b._ai_defenders = lambda: None
    b._volleys = lambda dt: None
    b.gate.closed = False
    b.gate.hp = 0
    hop = b.units(Side.STADT)[0]
    b.alarm = False
    b.command_line([hop], (5.0, 4.5), (11.0, 4.5))
    went_loose = False
    for _ in range(int(15 / DT)):
        b.update(DT)
        went_loose = went_loose or hop.loose
    assert went_loose
    assert not hop.loose and hop.in_phalanx and dist(hop.pos, (8.0, 4.5)) < 0.1


def test_hold_and_merge_close_a_dissolved_group_where_its_men_are():
    """Halten und Vereinen wirken auch auf eine Gruppe, die gerade Mann für Mann
    um eine andere herumgeht: Sie schließt sich dort, wo ihre Männer stehen."""
    b, line, block = line_and_block()
    b.command_move([block], (8.0, 6.0))
    for _ in range(int(1.5 / DT)):
        b.update(DT)
    assert block.loose
    centre = (sum(m.x for m in block.all_men()) / block.men, sum(m.y for m in block.all_men()) / block.men)
    b.command_hold([block])
    assert not block.loose and dist(block.pos, centre) < 0.5
    b2, line2, block2 = line_and_block()
    b2.command_move([block2], (8.0, 6.0))
    for _ in range(int(1.5 / DT)):
        b2.update(DT)
    assert block2.loose
    assert b2.command_merge([line2, block2]) is not None


def test_enemies_walk_around_their_own_as_a_block_unless_switched_on(monkeypatch):
    """Die Gegner gehen (vorerst) als Block um ihre eigenen Haufen herum; mit LOOSE_AI
    lösen auch sie sich dafür auf."""
    def setup():
        b = Battle(Scenario("t", "t", "", role="verteidigung", enemy_kind="raeuber", enemy_default=32, enemy_min=32,
                            enemy_max=32, houses=((2, 17),), raider_spawns=(RaiderSpawn(8.0, 5.0), RaiderSpawn(8.0, 8.0))),
                   random.Random(0), army=Army(groups=[GroupSpec("H", [Tier("mittel", 10)])]), ai="einfach")
        b._ai_raiders = lambda: None
        b._volleys = lambda dt: None
        b.alarm = False
        stand, walk = b.units(Side.FEIND)[:2]
        for u, pos in ((stand, (8.0, 6.0)), (walk, (8.0, 9.0))):
            u.x, u.y = pos
            u.target = None
            u.target_id = None
            u.stance = Stance.HALTEN
            u.place_men()
        walk.target = (8.0, 3.0)
        return b, walk
    b, walk = setup()
    b._update_loose(walk)
    assert not walk.loose
    monkeypatch.setattr(config, "LOOSE_AI", True)
    b, walk = setup()
    b._update_loose(walk)
    assert walk.loose and walk.loose_why == "eigene"
