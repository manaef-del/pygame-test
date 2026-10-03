"""Eigene Wege der Männer: Zielaufstellung fest, jeder Mann geht für sich dorthin."""

import random

import pytest

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


def line_and_block(block_at=(8.0, 11.5), block_width=14, drill="locker") -> tuple[Battle, object, object]:
    """Eine Phalanx (14 breit) steht bei (8, 9) auf ihrem Posten, ein Block dahinter (im
    Modus ``drill``: locker löst er sich auf, um vorbeizukommen, als Phalanx nicht)."""
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
    block.drill = drill
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


def test_over_the_wall_men_gather_behind_it_then_march_as_a_block():
    """Über den Turm: Drüben sammeln sich die Männer am Fuß der Leiter, über die sie
    hinabsteigen, und die Gruppe schließt sich dort, ohne zu springen; dann marschiert
    sie als Block zum Ziel, und dabei verlässt niemand seinen Platz."""
    b, hop = tower_battle()
    b.command_move([hop], (7.0, 5.5))
    muster = None
    closed_at = None
    left_slots = 0
    for _ in range(int(60 / DT)):
        was_loose = hop.loose
        if hop.muster is not None:
            muster = hop.muster[0]
        b.update(DT)
        if was_loose and not hop.loose and closed_at is None:
            closed_at = hop.pos
        if closed_at is not None and not hop.loose and hop.target is not None:
            left_slots = max(left_slots, sum(1 for m, p in hop.slots() if dist(m.pos, p) > 0.3))
        if closed_at is not None and hop.target is None:
            break
    assert muster is not None and abs(muster[0] - 13.5) < 0.3 and muster[1] < 7.0   # an der Leiter (13, 7), drüben
    assert closed_at is not None and dist(closed_at, muster) < 0.05                  # dort geschlossen, kein Sprung
    assert not hop.loose and dist(hop.pos, (7.0, 5.5)) < 0.15                        # als Block am Ziel
    assert left_slots <= (1 - config.SLOT_SHARE) * hop.men, left_slots            # höchstens die Nachzügler, die nachrücken
    assert any("neu gebildet" in e for e in b.events)


def test_near_target_behind_the_wall_is_the_gathering_place_itself():
    """Liegt das Ziel gleich hinter dem Wall, sammelt man sich dort und nirgends sonst."""
    b, hop = tower_battle()
    b.command_move([hop], (12.5, 5.6))                     # nahe der Leiter (13, 7)
    for _ in range(int(40 / DT)):
        b.update(DT)
        assert hop.muster is None
        if not hop.loose and hop.target is None:
            break
    assert dist(hop.pos, (12.5, 5.6)) < 0.15 and hop.facing == (0.0, -1.0)


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
    hop.drill = "locker"
    b.alarm = False
    b.command_line([hop], (5.0, 4.5), (11.0, 4.5))
    went_loose = False
    for _ in range(int(15 / DT)):
        b.update(DT)
        went_loose = went_loose or hop.loose
    assert went_loose
    b.command_drill([hop], "phalanx")
    for _ in range(int(2 / DT)):
        b.update(DT)
    assert not hop.loose and hop.in_phalanx and dist(hop.pos, (8.0, 4.5)) < 0.1


def test_phalanx_narrows_through_the_gate_and_widens_behind():
    """Eine Phalanx löst sich am offenen Tor nicht auf: Sie wird schmaler und tiefer,
    zieht als Block hindurch und marschiert dahinter wieder in voller Breite auf."""
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
    assert hop.drill == "phalanx"
    b.alarm = False
    b.command_line([hop], (5.0, 4.5), (11.0, 4.5))
    plan_width = b.line[0].width
    narrowest = hop.width
    for _ in range(int(20 / DT)):
        b.update(DT)
        assert not hop.loose                                         # nie Mann für Mann
        narrowest = min(narrowest, hop.width)
        if hop.full_width is not None:
            assert hop.half_w <= b.gate.half_len                     # die Front passt durchs Tor
    assert narrowest < plan_width                                    # im Tor schmaler
    assert hop.width == plan_width and hop.in_phalanx and dist(hop.pos, (8.0, 4.5)) < 0.1


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


def test_enemies_dissolve_around_their_own_unless_switched_off(monkeypatch):
    """Die Gegner lösen sich wie die Spielergruppen auf, um an einem ruhenden eigenen
    Haufen vorbeizukommen; mit abgeschaltetem LOOSE_AI gehen sie als Block herum.
    (Ein Umweg ginge hier auch als Block gleich schnell: hier ausgeschaltet.)"""
    monkeypatch.setattr(config, "FORMATION_MARGIN", -100.0)
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
        h = b.units(Side.STADT)[0]
        h.x, h.y = 2.0, 16.0                      # der Feind weit weg
        h.place_men()
        return b, walk
    b, walk = setup()
    b._update_loose(walk)
    assert walk.loose and walk.loose_why == "eigene"
    monkeypatch.setattr(config, "LOOSE_AI", False)
    b, walk = setup()
    b._update_loose(walk)
    assert not walk.loose


def test_enemies_keep_their_order_next_to_a_foe():
    """Steht ein Feind dicht dabei, löst sich ein Gegnerhaufen nicht auf, um an den
    eigenen vorbeizukommen: er geht als Block herum."""
    b = Battle(Scenario("t", "t", "", role="verteidigung", enemy_kind="raeuber", enemy_default=32, enemy_min=32,
                        enemy_max=32, houses=((2, 17),), raider_spawns=(RaiderSpawn(8.0, 5.0), RaiderSpawn(8.0, 8.0))),
               random.Random(0), army=Army(groups=[GroupSpec("H", [Tier("mittel", 10)])]), ai="einfach")
    b._ai_raiders = lambda: None
    b.alarm = False
    stand, walk = b.units(Side.FEIND)[:2]
    for u, pos in ((stand, (8.0, 6.0)), (walk, (8.0, 9.0))):
        u.x, u.y = pos
        u.target = None
        u.target_id = None
        u.stance = Stance.HALTEN
        u.place_men()
    walk.target = (8.0, 3.0)
    h = b.units(Side.STADT)[0]
    h.x, h.y = 10.5, 9.0
    h.place_men()
    b._update_loose(walk)
    assert not walk.loose


def approaching_attacker(b, ring):
    """Der erste Räuberhaufen, der den Kreis angreift, aber noch nicht dran ist, weil eigene
    kämpfende Haufen davor stehen (frühestens nach 13 Sekunden)."""
    run(b, 13)
    for _ in range(int(20 / DT)):
        busy = [u for u in b.units(Side.FEIND, fighting_only=True) if u.engaged]
        cands = [u for u in b.units(Side.FEIND, fighting_only=True)
                 if u.stance is Stance.ANGRIFF and u.target_id == ring.id and not u.engaged
                 and b._detour_plan(u, u.target) is not None]        # eine eigene Gruppe steht im Weg
        if busy and cands:
            return cands[0]
        b.update(DT)
    raise AssertionError("kein Angreifer in dieser Lage")


def test_attacker_keeps_its_detour_side_instead_of_dithering():
    """Ein Haufen, der hinter eigenen kämpfenden Gruppen an einen Kreis will, wählt
    eine Seite und bleibt dabei: er wechselt sie nicht hin und her und kommt voran
    oder wartet geordnet (Umweg-Flackern, docs/ideen.md)."""
    from game.scenarios import OFFENE_SIEDLUNG
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    own = b.units(Side.STADT)
    g = b.command_merge(own)
    b.command_formation([g], "o")
    b.command_ring([g], (7.5, 9.5), 1.0)
    r6 = approaching_attacker(b, g)
    start = r6.pos
    sides = []
    for _ in range(int(10 / DT)):
        b.update(DT)
        if r6.detour_side:
            sides.append(r6.detour_side)
    flips = sum(1 for a, c in zip(sides, sides[1:]) if a != c)
    assert flips == 0, flips
    assert dist(start, r6.pos) > 1.5 or r6.waiting


def test_attacker_waits_when_the_enemy_outline_is_full(monkeypatch):
    """Ist am ganzen Umriss des Gegners kein Platz mehr frei, wartet der Block hinter
    den eigenen Gruppen, statt herumzulaufen."""
    from game.scenarios import OFFENE_SIEDLUNG
    b = Battle(OFFENE_SIEDLUNG, random.Random(1))
    own = b.units(Side.STADT)
    g = b.command_merge(own)
    b.command_formation([g], "o")
    b.command_ring([g], (7.5, 9.5), 1.0)
    r6 = approaching_attacker(b, g)
    monkeypatch.setattr(b, "_free_outline", lambda u, foe: [])
    r6.detour_side = 0.0
    start = r6.pos
    for _ in range(int(2 / DT)):
        b.update(DT)
    assert r6.waiting and dist(start, r6.pos) < 0.2


def test_enemies_pass_an_open_gate_man_by_man():
    """Ist das Tor offen und kein Feind davor, löst sich ein Räuberhaufen auf und geht
    Mann für Mann hindurch; mit abgeschaltetem LOOSE_AI geht er als Block."""
    from game.scenarios import PALISADE

    def setup():
        b = Battle(PALISADE, random.Random(1))
        b._ai_raiders = lambda: None
        b.alarm = False
        b.gate.hp = 0.0
        b.gate.closed = False
        for u in b.units(Side.STADT):
            u.x, u.y = 14.5, 16.0                 # die Verteidiger weit weg vom Tor
            u.place_men()
        r = b.units(Side.FEIND)[0]
        gx, gy = b.gate.center
        r.x, r.y = gx + 2.0, gy - 2.5
        r.place_men()
        r.stance = Stance.RAUB
        r.target_id = None
        r.target = (gx, gy + 4.0)
        return b, r
    b, r = setup()
    b._update_loose(r)
    assert r.loose and r.loose_why == "tor"
    config_off = config.LOOSE_AI
    try:
        config.LOOSE_AI = False
        b, r = setup()
        b._update_loose(r)
        assert not r.loose
    finally:
        config.LOOSE_AI = config_off


def test_dissolving_waits_a_step_when_the_field_budget_is_spent():
    """Sind in diesem Takt schon genug Wegefelder gerechnet, löst sich eine Gruppe erst
    im nächsten auf (gegen Ruckeln, wenn viele zugleich ans Tor kommen)."""
    from game.scenarios import PALISADE
    b = Battle(PALISADE, random.Random(1))
    b._ai_raiders = lambda: None
    b.alarm = False
    b.gate.hp = 0.0
    b.gate.closed = False
    for u in b.units(Side.STADT):
        u.x, u.y = 14.5, 16.0
        u.place_men()
    r = b.units(Side.FEIND)[0]
    gx, gy = b.gate.center
    r.x, r.y = gx + 2.0, gy - 2.5
    r.place_men()
    r.stance = Stance.RAUB
    r.target_id = None
    r.target = (gx, gy + 4.0)
    b._field_builds = {b.time: b._field_budget()}
    b._update_loose(r)
    assert not r.loose
    b.time += DT
    b._update_loose(r)
    assert r.loose and r.loose_why == "tor"


def test_small_detour_around_own_group_stays_a_block():
    """Steht eine eigene Gruppe nur am Rand des Weges, geht ein Block im Bogen an ihr
    vorbei, statt sich aufzulösen; die Front zeigt dabei in Marschrichtung."""
    b, line, block = line_and_block(block_at=(11.5, 13.5))
    b.command_move([block], (4.0, 4.0))                    # schräg an der Linie vorbei
    went_loose = False
    facings = []
    for _ in range(int(14 / DT)):
        b.update(DT)
        went_loose = went_loose or block.loose
        closest = min(dist(m.pos, n.pos) for m in block.all_men() for n in line.all_men())
        assert closest >= 2 * config.MAN_RADIUS - 1e-6
        facings.append(block.facing)
    assert not went_loose
    assert dist(block.pos, (4.0, 4.0)) < 0.3
    assert all(f[1] <= 0.05 for f in facings)               # kein Ausschlag zurück nach Süden an der Ecke


def test_phalanx_goes_around_its_own_line_as_a_block():
    """Im Modus Phalanx löst sich der Block vor der stehenden eigenen Linie nicht auf: Er
    geht als Block außen herum und kommt geschlossen am Ziel an."""
    b, line, block = line_and_block(drill="phalanx")
    b.command_move([block], (8.0, 6.0))
    for _ in range(int(20 / DT)):
        b.update(DT)
        assert not block.loose
        closest = min(dist(m.pos, n.pos) for m in block.all_men() for n in line.all_men())
        assert closest >= 2 * config.MAN_RADIUS - 1e-6
    assert dist(block.pos, (8.0, 6.0)) < 0.3


def test_big_detour_still_goes_man_by_man():
    """Steht die eigene Gruppe quer vor dem Weg, wäre der Umweg als Block groß: Dann löst
    sich die Gruppe auf und geht Mann für Mann vorbei (wie bisher)."""
    b, line, block = line_and_block()
    b.command_move([block], (8.0, 6.0))
    went_loose = False
    for _ in range(int(3 / DT)):
        b.update(DT)
        went_loose = went_loose or block.loose
    assert went_loose
