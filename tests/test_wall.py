"""Wall, Leitern, Türme und Tore, an der Festung geprüft.

Die Nordkante der Festung ist gerade wie die frühere Palisade: Wallreihe 9 von x = 10
bis 21, das Nordtor auf 15 und 16, Leitern auf 13 und 18, Wehrtürme an den Ecken (10
und 21). Innen liegt Reihe 10, außen Reihe 8. Die Südkante (Reihe 26, Leitern auf 13
und 18) liegt dem Angreifer gegenüber."""

import random

import pytest

from game import config
from game.battle import Battle, Projectile
from game.geometry import dist
from game.scenarios import FESTUNG, FESTUNG_ANGRIFF
from game.units import Lochos, Man, Side, Stance, UNIT_TYPES, arrange

DT = 1 / 30
NORTH_ROW, SOUTH_ROW = 9, 26


def run(b: Battle, seconds: float) -> None:
    for _ in range(int(seconds / DT)):
        b.update(DT)


def quiet(b: Battle, enemies: bool = True) -> Battle:
    """Ohne Gegner-KI, Türme und Siegprüfung; ``enemies=False``: die Gegner sind fort."""
    b.brain.think = lambda b: None
    b._tower_fire = lambda dt: None
    b._check_outcome = lambda: None
    b.alarm = False
    if not enemies:
        for e in b.units(Side.FEIND):
            e.withdrawn = True
    return b


def defence(seed: int = 1, enemies: bool = False) -> Battle:
    return quiet(Battle(FESTUNG, random.Random(seed)), enemies)


def attack(seed: int = 1, enemies: bool = False) -> Battle:
    return quiet(Battle(FESTUNG_ANGRIFF, random.Random(seed), doctrine="spiegel"), enemies)


def arms(b: Battle, side: Side = Side.STADT) -> tuple[Lochos, Lochos, Lochos]:
    us = b.units(side)
    pick = lambda arm: next(u for u in us if u.arm() == arm)   # noqa: E731
    return pick("hopliten"), pick("peltasten"), pick("reiter")


def put(u: Lochos, x: float, y: float, facing=None) -> None:
    u.x, u.y = x, y
    if facing is not None:
        u.facing = facing
    u.target = None
    u.target_id = None
    u.place_men()


def tower_at(b: Battle, cell) -> None:
    """Ein aufgestellter Belagerungsturm an ``cell`` (außen am Wall), wie ihn das Spiel setzt."""
    b.crossings.add(cell)
    b._foot[cell] = b._ground_step(cell, "aussen")


def foe_group(b: Battle, x: float, y: float, kind: str = "raeuber", n: int = 12) -> Lochos:
    u = b._spawn(Side.FEIND, arrange([Man(UNIT_TYPES[kind]) for _ in range(n)], 6), x, y, "Feind")
    u.stance = Stance.HALTEN
    u.facing = (0.0, 1.0)
    return u


# ------------------------------------------------------------- Wall und Leitern
def test_the_north_edge_is_a_straight_wall_with_gate_ladders_and_towers():
    b = defence()
    row = sorted(c[0] for c in b.blocked if c[1] == NORTH_ROW)
    assert row == [10, 11, 12, 13, 14, 17, 18, 19, 20, 21]
    assert {(13, NORTH_ROW), (18, NORTH_ROW)} <= b.ladders
    north = next(g for g in b.gates if g.normal == (0.0, -1.0))
    assert sorted(north.cells) == [(15, NORTH_ROW), (16, NORTH_ROW)] and north.closed


def test_wall_is_entered_and_left_only_by_ladder():
    b = defence(enemies=True)
    hop, pelt, cav = arms(b)
    foe = foe_group(b, 12.5, 7.5)
    y_in, y_wall, y_out = NORTH_ROW + 1.4, NORTH_ROW + 0.5, NORTH_ROW - 0.4
    assert not b.can_step(pelt, (11.5, y_in), (11.5, y_wall))      # mitten am Wall: nicht hinauf
    assert b.can_step(pelt, (13.5, y_in), (13.5, y_wall))          # an der Leiter: hinauf
    assert not b.can_step(cav, (13.5, y_in), (13.5, y_wall))       # beritten nicht
    assert not b.can_step(foe, (13.5, y_out), (13.5, y_wall))      # von außen führt keine Leiter hinauf
    put(pelt, 14.5, y_wall)
    assert b.on_wall(pelt) and b.can_step(pelt, (14.5, y_wall), (15.5, y_wall))   # oben über das Torhaus
    assert b.is_blocked(15.5, y_wall, cav) and b.is_blocked(15.5, y_wall, foe)
    assert not b.can_step(pelt, (14.5, y_wall), (14.5, y_in))      # herunter nur an der Leiter
    assert b.can_step(pelt, (18.5, y_wall), (18.5, y_in))


def test_tower_leads_up_from_outside_and_ladders_down_inside():
    """Der Turm steht außen: hinauf und außen wieder hinunter; nach innen geht es nur über
    die Leitern (beide stehen allen Läufern offen)."""
    b = attack()
    hop, pelt, cav = arms(b)
    tower_at(b, (12, SOUTH_ROW))
    y_out, y_wall, y_in = SOUTH_ROW + 1.4, SOUTH_ROW + 0.5, SOUTH_ROW - 0.4
    assert b.can_step(hop, (12.5, y_out), (12.5, y_wall))          # von außen hinauf
    assert b.can_step(hop, (12.5, y_wall), (12.5, y_out))          # außen wieder hinunter
    assert not b.can_step(hop, (12.5, y_wall), (12.5, y_in))       # am Turm nicht nach innen
    assert b.can_step(hop, (13.5, y_wall), (13.5, y_in))           # die Leiter führt hinein
    assert (12, SOUTH_ROW) not in b.ladders_for(hop, (12.5, y_wall), (12.0, 20.0))
    assert (12, SOUTH_ROW) in b.ladders_for(hop, (12.5, y_wall), (12.0, 31.0))


def test_defenders_follow_over_the_enemy_tower():
    """Ein aufgestellter Belagerungsturm dient beiden Seiten: Die Verteidiger steigen über
    ihre Leiter auf den Wall und über den Turm nach draußen, etwa um Fliehenden
    nachzusetzen (die Tore bleiben zu). Reiter bleiben unten."""
    b = defence()
    hop, pelt, cav = arms(b)
    target = (12.0, NORTH_ROW - 4.0)
    assert b._cut_off(hop, target)
    tower_at(b, (12, NORTH_ROW))                           # ein Turm des Heeres steht am Wall
    assert not b._cut_off(hop, target) and b._cut_off(cav, target)
    assert b.can_step(hop, (12.5, NORTH_ROW + 0.5), (12.5, NORTH_ROW - 0.4))   # über den Turm hinab nach draußen
    b.command_move([hop], target)
    run(b, 60)
    assert hop.target is None and not hop.loose
    assert all(m.y < NORTH_ROW - 0.5 for m in hop.all_men())


def test_peltasts_stay_on_the_wall_when_there_is_no_way_down_outside():
    """Die Leitern führen nur nach innen: Sind die Tore zu, steigen Peltasten, die nach
    draußen sollen, auf den Wehrgang darüber, statt endlos auf und ab zu klettern;
    Reiter warten am Tor."""
    b = defence()
    hop, pelt, cav = arms(b)
    b.command_move([pelt], (16.0, 4.0))
    assert any("kein Weg hinab" in e for e in b.events)
    run(b, 25)
    assert b.on_wall(pelt) and not pelt.loose
    b.command_move([cav], (16.0, 4.0))
    assert any("das Tor ist zu" in e for e in b.events)


def test_peltasts_route_over_ladders_and_walk_over_the_gatehouse():
    b = defence()
    b._volleys = lambda dt: None
    hop, pelt, cav = arms(b)
    put(pelt, 15.5, 11.0, (0.0, -1.0))                    # innen am Wall (südlich davon stehen Häuser)
    spot = (11.5, NORTH_ROW + 0.5)
    goal, final = b.route(pelt, spot)
    assert final is False and abs(goal[0] - 13.5) < 0.6           # erst zur Leiter (bzw. an ihren Fuß)
    b.command_move([pelt], spot)
    run(b, 25)
    assert b.on_wall(pelt) and abs(pelt.x - spot[0]) < 0.4
    b.command_move([pelt], (19.5, NORTH_ROW + 0.5))                # oben über das Torhaus
    run(b, 12)
    assert b.on_wall(pelt) and abs(pelt.x - 19.5) < 0.4
    b.command_move([pelt], (16.5, 11.2))                           # hinunter über die östliche Leiter
    run(b, 25)
    assert not b.on_wall(pelt) and dist(pelt.pos, (16.5, 11.2)) < 0.4


def test_walkway_gap_is_crossed_via_ladders():
    """Ist das Nordtor offen, hat der Wehrgang dort eine Lücke: Peltasten steigen an der
    einen Leiter hinab, gehen unten quer und an der anderen wieder hinauf (statt einmal um
    die ganze Festung), und oben schließen sie sich."""
    b = defence()
    b._volleys = lambda dt: None
    hop, pelt, cav = arms(b)
    put(pelt, 12.5, NORTH_ROW + 0.5, (0.0, -1.0))
    assert b.on_wall(pelt)
    north_gate_open(b)
    goal, final = b.route(pelt, (19.5, NORTH_ROW + 0.5))
    assert not final and abs(goal[0] - 13.5) < 0.6                # erst zur westlichen Leiter hinunter
    b.command_move([pelt], (19.5, NORTH_ROW + 0.5))
    lowest = 0.0
    for _ in range(int(30 / DT)):
        b.update(DT)
        lowest = max(lowest, max(m.y for m in pelt.all_men()))
        if not pelt.loose and pelt.target is None:
            break
    assert b.on_wall(pelt) and abs(pelt.x - 19.5) < 0.4 and not pelt.loose
    assert all(b.cell(m.x, m.y)[0] >= 17 and b.cell(m.x, m.y)[1] == NORTH_ROW for m in pelt.all_men())
    assert lowest < NORTH_ROW + 3.0                                # unten quer, nicht um die Festung herum


def test_climbing_is_a_dense_column_and_men_spread_along_the_wall():
    b = defence()
    b._volleys = lambda dt: None
    hop, pelt, cav = arms(b)
    put(pelt, 15.0, 11.0, (0.0, -1.0))
    b.command_move([pelt], (12.0, NORTH_ROW + 0.5))
    spread_up, t = 0.0, 0.0
    while t < 20 and not (b.on_wall(pelt) and not pelt.loose):
        b.update(DT)
        t += DT
        up = [m for m in pelt.all_men() if b.is_wall_cell(b.cell(m.x, m.y), True)]
        if len(up) >= 6:
            spread_up = max(spread_up, max(m.x for m in up) - min(m.x for m in up))
    assert t < 12                                           # 15 Mann in unter zwölf Sekunden oben
    assert spread_up >= 0.6                                 # schon beim Klettern in einer Reihe längs des Walls
    assert not pelt.loose and all(b.is_wall_cell(b.cell(m.x, m.y), True) for m in pelt.all_men())


def test_crossing_dissolves_formation_and_reforms_inside():
    b = attack()
    hop, pelt, cav = arms(b)
    tower_at(b, (12, SOUTH_ROW))
    put(hop, 12.0, SOUTH_ROW + 3.0, (0.0, -1.0))
    b.command_move([hop], (13.0, SOUTH_ROW - 3.0))
    seen_loose, max_up = False, 0
    for _ in range(int(90 / DT)):
        b.update(DT)
        seen_loose = seen_loose or hop.loose
        max_up = max(max_up, sum(1 for m in hop.all_men() if b.is_wall_cell(b.cell(m.x, m.y), True)))
        for m in hop.all_men():
            assert b.cell(m.x, m.y) not in b.blocked or b.is_wall_cell(b.cell(m.x, m.y), True)
        if seen_loose and not hop.loose and hop.target is None:
            break
    assert seen_loose and max_up >= 1                        # Mann für Mann über den Wehrgang
    assert not hop.loose and all(m.y < SOUTH_ROW - 0.5 for m in hop.all_men())
    assert any("neu gebildet" in e for e in b.events)


def test_men_flow_through_an_open_gate_without_touching_the_wall():
    b = attack()
    hop, pelt, cav = arms(b)
    for g in b.gates:
        g.hp, g.closed = 0.0, False
    gate = min(b.gates, key=lambda g: dist(g.center, hop.pos))
    inside = (gate.center[0] - gate.normal[0] * 3.0, gate.center[1] - gate.normal[1] * 3.0)
    b.command_move([hop], inside)
    for _ in range(int(60 / DT)):
        b.update(DT)
        for m in hop.all_men():
            assert b.cell(m.x, m.y) not in b.blocked            # niemand steckt im Wall
        if hop.target is None and not hop.loose:
            break
    assert hop.target is None and b._wall_level(hop.pos) == "innen"
    assert all(b._wall_level(m.pos) in ("innen", "tor") for m in hop.all_men())   # (die hintersten stehen noch im Tor)


# ------------------------------------------------------------- Kampf am Wall
def test_peltasts_throw_over_the_wall_only_from_the_walkway():
    b = defence()
    hop, pelt, cav = arms(b)
    foe = foe_group(b, 12.5, NORTH_ROW - 1.5)
    put(pelt, 12.5, NORTH_ROW + 1.6)                       # innen am Boden
    assert not b.throw_clear(pelt, foe)
    put(pelt, 12.5, NORTH_ROW + 0.5)                       # oben auf dem Wehrgang
    assert b.on_wall(pelt) and b.throw_clear(pelt, foe)
    b.command_hold([pelt])
    seen = False
    for _ in range(int(2.0 / DT)):
        b.update(DT)
        seen = seen or any(pr.target_id == foe.id for pr in b.projectiles)
    assert seen


def test_the_walkway_is_raised_for_melee():
    """Von unten kommt niemand an den Wehrgang heran, von oben schlägt man hinunter,
    schwächer als am Boden."""
    b = defence()
    hop, pelt, cav = arms(b)
    put(pelt, 12.0, NORTH_ROW + 0.5, (0.0, -1.0))
    foe = foe_group(b, 12.0, NORTH_ROW - 0.5)
    foe.place_men()
    assert b.on_wall(pelt)
    assert not b._in_contact(foe, pelt)                    # der Wehrgang ist erhöht
    assert b._in_contact(pelt, foe)
    rate_down, _ = b._melee_rate(pelt, foe)
    pelt_off = Lochos(99, Side.STADT, [[Man(UNIT_TYPES["peltast"]) for _ in range(15)]], 12.0, 14.0)
    b.lochoi.append(pelt_off)
    put(foe, 12.0, 15.0)
    rate_ground, _ = b._melee_rate(pelt_off, foe)
    assert 0 < rate_down < rate_ground * config.WALL_MELEE_FACTOR + 1e-9


def test_no_phalanx_bonus_on_the_wall():
    b = defence()
    hop, pelt, cav = arms(b)
    put(pelt, 12.0, NORTH_ROW + 0.5, (0.0, -1.0))
    pelt.stance, pelt.in_line = Stance.PHALANX, True
    foe = foe_group(b, 12.0, NORTH_ROW - 0.4)
    assert b.on_wall(pelt) and pelt.in_phalanx
    assert b._formed(pelt) is False
    mod, _ = b._defense_mod(foe, pelt)
    assert mod == 1.0


def test_the_wall_covers_the_walkway_against_spears_from_outside():
    """Wer auf dem Wehrgang steht, ist gegen Speere von außen gedeckt; von innen
    oder unten auf dem Boden nicht."""
    b = defence()
    hop, pelt, cav = arms(b)
    man = pelt.all_men()[0]

    def hit(at, origin):
        man.x, man.y = at
        man.hp = man.kind.hp
        b.projectiles = [Projectile(origin[0], origin[1], man.x, man.y, pelt.id, 0.2, 0.0, 0.1, man)]
        for u in b.lochoi:                                # nur der eine Speer zählt
            u.volley_timer = 99.0
        b._volleys(0.2)
        return man.kind.hp - man.hp

    walkway = (12.5, NORTH_ROW + 0.5)
    outside, inside = (12.5, NORTH_ROW - 2.0), (12.5, NORTH_ROW + 3.0)
    full = hit(walkway, inside)
    assert full > 0.0
    assert hit(walkway, outside) == pytest.approx(config.WALL_COVER_FACTOR * full)
    ground = (12.5, NORTH_ROW + 1.5)
    assert hit(ground, outside) == pytest.approx(hit(ground, inside))       # unten am Boden: keine Deckung


def test_a_loose_group_changes_wall_side_only_with_a_clear_majority():
    """Steigt eine aufgelöste Gruppe über den Wall, zählt sie erst als drüben, wenn dort
    klar mehr Männer stehen; bei halb und halb springt ihr Ort nicht hin und her."""
    b = defence()
    u = foe_group(b, 12.0, NORTH_ROW - 2.0, n=16)
    men = u.all_men()
    u.loose = True
    u.centre_level = None
    half = len(men) // 2
    out_y, in_y = NORTH_ROW - 2.0, NORTH_ROW + 3.0
    for i, m in enumerate(men):
        m.x, m.y = (11.5 + 0.1 * (i % 8), out_y if i <= half else in_y)
    first = b._wall_level(b._loose_centre(u))                            # die Mehrheit draußen
    for i, m in enumerate(men):
        if i == half:                                                    # einer mehr drinnen: knapp
            m.y = in_y
    assert b._wall_level(b._loose_centre(u)) == first
    for i, m in enumerate(men):
        m.y = in_y if i % 4 else out_y                                   # drei Viertel drinnen
    assert b._wall_level(b._loose_centre(u)) != first


def test_nobody_stands_inside_the_wall():
    b = Battle(FESTUNG, random.Random(3))
    b.command_attack()
    for _ in range(int(60 / DT)):
        b.update(DT)
        for u in b.lochoi:
            if u.alive and b.inside(u.x, u.y):
                assert not b.is_blocked(u.x, u.y, u), (u.name, u.x, u.y)
        if b.outcome:
            break


# ------------------------------------------------------------- Belagerungsgerät
def test_each_group_builds_its_own_engine():
    b = attack()
    hop, pelt, cav = arms(b)
    assert b.command_build([hop, cav], "ram") == 2
    run(b, config.RAM_BUILD_TIME + 1)
    assert hop.engine == "ram" and cav.engine == "ram" and pelt.engine is None


def test_losing_the_engine_group_loses_the_engine():
    b = attack()
    hop, pelt, cav = arms(b)
    b.command_build([hop], "ram")
    run(b, config.RAM_BUILD_TIME + 1)
    assert hop.engine == "ram"
    hop.morale = 0.0
    b._morale(DT)
    assert hop.stance is Stance.FLUCHT and hop.engine is None


def test_cavalry_dismounts_for_siege_work():
    b = attack()
    hop, pelt, cav = arms(b)
    assert cav.speed == UNIT_TYPES["reiter"].speed
    b.command_build([cav], "tower")
    assert cav.mounted_men() == [] and len(b.horses) == 1 and b.horses[0][2] == cav.men
    assert cav.speed == pytest.approx(config.DISMOUNTED_SPEED)
    assert cav.cavalry_share() == 0.0                           # kein Reiterbonus mehr
    run(b, config.TOWER_BUILD_TIME + 1)
    assert cav.speed == pytest.approx(config.DISMOUNTED_SPEED * config.TOWER_SPEED_FACTOR)


def test_dismounted_cavalry_remounts_at_their_horses():
    b = attack()
    hop, pelt, cav = arms(b)
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


def test_closed_gate_blocks_until_the_ram_breaks_it():
    b = attack()
    hop, pelt, cav = arms(b)
    gate = min(b.gates, key=lambda g: dist(g.center, hop.pos))
    gx, gy = gate.center
    nx, ny = gate.normal
    assert gate.closed and b.is_blocked(gx, gy, hop)
    assert not b.path_clear((gx + 3 * nx, gy + 3 * ny), (gx - 3 * nx, gy - 3 * ny), hop)
    assert b.command_ram_gate([hop], gate) == 0                # ohne Rammbock
    assert b.command_build([hop], "ram") == 1
    assert hop.build_kind == "ram" and hop.building == 0.0
    assert b.command_build([hop], "ram") == 0                  # baut schon
    run(b, config.RAM_BUILD_TIME + 1)
    assert hop.engine == "ram" and hop.speed < UNIT_TYPES["schwer"].speed
    assert b.command_ram_gate([hop], gate) == 1
    for _ in range(int(90 / DT)):
        b.update(DT)
        if not gate.closed:
            break
    assert not gate.closed and gate.hp == 0.0
    assert not b.is_blocked(gx, gy, hop)
    assert any("aufgebrochen" in e for e in b.events)


# ------------------------------------------------------------- Durchs Tor
def north_gate_open(b: Battle):
    north = next(g for g in b.gates if g.normal == (0.0, -1.0))
    north.hp, north.closed = 0.0, False
    return north


@pytest.mark.parametrize("drill", ["locker", "phalanx"])
def test_a_line_narrows_through_the_gate_and_forms_beyond(drill):
    """Lockere Hopliten wie die Phalanx ziehen als schmale Kolonne durchs offene Tor (keiner
    bleibt links und rechts hängen) und stellen sich drüben in voller Breite auf."""
    b = defence()
    b._volleys = lambda dt: None
    hop, pelt, cav = arms(b)
    hop.drill = drill
    gate = north_gate_open(b)
    put(hop, 16.0, 13.6, (0.0, -1.0))
    b.command_line([hop], (13.0, 6.0), (19.0, 6.0))
    plan_width = b.line[0].width
    went_loose, narrowest = False, hop.width
    for _ in range(int(25 / DT)):
        b.update(DT)
        went_loose = went_loose or hop.loose
        narrowest = min(narrowest, hop.width)
        if hop.full_width is not None:
            assert hop.half_w <= gate.half_len                     # die Front passt durchs Tor
    assert not went_loose and narrowest < plan_width
    assert hop.width == plan_width and all(dist(m.pos, p) < 0.4 for m, p in hop.slots())


def test_enemies_pass_an_open_gate_man_by_man_and_wait_for_the_field_budget():
    """Ist das Tor offen und kein Feind davor, löst sich ein Räuberhaufen auf und geht
    Mann für Mann hindurch; sind in diesem Takt schon genug Wegefelder gerechnet, erst im
    nächsten. Mit abgeschaltetem LOOSE_AI geht er als Block."""
    def setup():
        b = defence()
        gate = north_gate_open(b)
        gx, gy = gate.center
        r = foe_group(b, gx + 2.0, gy - 2.5)
        r.place_men()
        r.stance = Stance.RAUB
        r.target = (gx, gy + 4.0)
        return b, r
    b, r = setup()
    b._update_loose(r)
    assert r.loose and r.loose_why == "tor"
    b, r = setup()
    b._field_builds = {b.time: b._field_budget()}
    b._update_loose(r)
    assert not r.loose
    b.time += DT
    b._update_loose(r)
    assert r.loose and r.loose_why == "tor"
    off = config.LOOSE_AI
    try:
        config.LOOSE_AI = False
        b, r = setup()
        b._update_loose(r)
        assert not r.loose
    finally:
        config.LOOSE_AI = off


def test_groups_queue_behind_their_own_fighting_group():
    """Greifen mehrere Gruppen denselben Feind durch eine Enge an, fährt keine in die
    vordere hinein: Wer nicht mehr an den Feind kommt, wartet im Block dahinter."""
    b = defence(enemies=True)
    b._volleys = lambda dt: None
    hop, pelt, cav = arms(b)
    gate = north_gate_open(b)
    gx, gy = gate.center
    for u in (pelt, cav):
        u.withdrawn = True
    put(hop, gx, gy + 2.2, (0.0, -1.0))
    b.command_formation([hop], "o")
    b.command_ring([hop], (gx, gy + 2.2), 1.2)
    raiders = [foe_group(b, gx - 1.5 + 1.5 * k, gy - 3.0 - 1.2 * k) for k in range(3)]
    for e in b.units(Side.FEIND):
        if e not in raiders:
            e.withdrawn = True
    b.men_start = {side: b.men(side) for side in Side}            # nur diese drei Haufen zählen
    for r in raiders:
        r.place_men()
        r.stance, r.target_id, r.target = Stance.ANGRIFF, hop.id, hop.pos
    run(b, 20)                                                     # das Gedränge am Tor sortiert sich
    alive = [r for r in raiders if r.fighting and not r.loose]
    fighting = [u for u in alive if u.engaged]
    waiting = [u for u in alive if not u.engaged and u.waiting]
    assert fighting and waiting, (len(fighting), len(waiting))
    for w in waiting:
        assert all(b._gap(w, f) >= 0.0 for f in fighting)
