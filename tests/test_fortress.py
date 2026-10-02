"""Die Festung: große Karte, sechseckiger Wall, drei Tore, Ecktürme, Kamera."""

import math
import random

import pygame
import pytest

from game import config
from game.app import App
from game.battle import Battle
from game.render import Renderer
from game.scenarios import FESTUNG, FESTUNG_ANGRIFF, SCENARIOS
from game.units import Man, Side, Stance, UNIT_TYPES, arrange

DT = 1 / 30


def run(b: Battle, seconds: float) -> None:
    for _ in range(int(seconds / DT)):
        b.update(DT)
        if b.outcome:
            break


def quiet(b: Battle) -> Battle:
    """Ohne die KI des Gegners: nur was der Test befiehlt."""
    b._ai_raiders = lambda: None
    b._ai_defenders = lambda: None
    b.alarm = False
    return b


def clear(b: Battle, keep=()) -> None:
    """Das Feld räumen, bis auf ``keep``; auf jeder Seite bleibt eine Gruppe abseits stehen,
    sonst wäre die Schlacht schon entschieden."""
    parked = {Side.STADT: False, Side.FEIND: False}
    for u in b.lochoi:
        if u in keep:
            parked[u.side] = True
    for u in list(b.lochoi):
        if u in keep:
            continue
        if not parked[u.side]:
            parked[u.side] = True
            spot = b.agora if u.side is Side.STADT else (1.5, 1.5)
            u.x, u.y = spot
            u.target = None
            u.stance = Stance.HALTEN
            u.place_men()
            continue
        u.rows = []
    b.men_start = {side: b.men(side) for side in Side}         # sonst wirkt die Lage aussichtslos


# ------------------------------------------------------------------ Karte
def test_fortress_map_is_four_times_as_big_and_closed():
    b = Battle(FESTUNG, random.Random(1))
    assert (b.cols, b.rows) == (2 * config.COLS, 2 * config.ROWS)
    assert len(b.gates) == 3 and all(g.closed for g in b.gates)
    assert len(b.corner_towers) == 6 and len(b.ladders) >= 6
    assert all(b._wall_level(h.center) == "innen" for h in b.houses)
    # bei geschlossenen Toren kommt man von außen nicht hinein, auch nicht über Eck
    start = (0, 0)
    seen, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (x + dx, y + dy)
                if n in seen or not (0 <= n[0] < b.cols and 0 <= n[1] < b.rows):
                    continue
                if b.is_blocked(n[0] + 0.5, n[1] + 0.5):
                    continue
                if dx and dy and (b.is_blocked(x + dx + 0.5, y + 0.5) and b.is_blocked(x + 0.5, y + dy + 0.5)):
                    continue                                   # nicht zwischen zwei Wallstücken hindurch
                seen.add(n)
                todo.append(n)
    assert not any(b._wall_level((c[0] + 0.5, c[1] + 0.5)) == "innen" for c in seen)
    # jedes Tor führt von außen nach innen
    for g in b.gates:
        assert b._wall_level(b.gate_approach(g, 1.0)) == "aussen"
        assert b._wall_level(b.gate_approach(g, -1.0)) == "innen"


def test_old_maps_keep_their_size():
    for s in SCENARIOS:
        if not s.key.startswith("festung"):
            b = Battle(s, random.Random(1))
            assert (b.cols, b.rows) == (config.COLS, config.ROWS) and not b.ring


# ------------------------------------------------------------------ Wege
def lone_group(b: Battle, side: Side, kind: str, n: int, pos) -> object:
    men = [Man(UNIT_TYPES[kind]) for _ in range(n)]
    u = b._spawn(side, arrange(men, 4), pos[0], pos[1], kind)
    u.stance = Stance.HALTEN
    u.place_men()
    return u


def test_a_group_goes_around_the_closed_fortress():
    b = quiet(Battle(FESTUNG, random.Random(1)))
    u = lone_group(b, Side.FEIND, "raeuber", 8, (16.0, 4.0))
    clear(b, [u])
    u.target = (16.0, 32.0)                                   # genau gegenüber, die Festung dazwischen
    for _ in range(int(60 / DT)):
        b.update(DT)
        assert b._wall_level(u.pos) == "aussen"
        if math.dist(u.pos, u.target) < 0.3:
            break
    assert math.dist(u.pos, (16.0, 32.0)) < 0.5


def test_a_group_goes_through_the_open_gate_that_is_nearest():
    b = quiet(Battle(FESTUNG, random.Random(1)))
    sw = b.gates[1]
    sw.closed = False
    sw.hp = 0.0
    u = lone_group(b, Side.FEIND, "raeuber", 8, (3.0, 25.0))
    clear(b, [u])
    inner = b.gate_approach(sw, -1.0)
    goal = ((inner[0] + b.agora[0]) / 2, (inner[1] + b.agora[1]) / 2)   # in der Gasse vom Tor zur Agora
    assert not b.is_blocked(*goal)
    u.target = goal
    passed = False
    for _ in range(int(40 / DT)):
        b.update(DT)
        passed = passed or any(b.gate_of(b.cell(m.x, m.y)) is sw for m in u.all_men())
        if math.dist(u.pos, goal) < 0.3:
            break
    assert passed and math.dist(u.pos, goal) < 0.5


def test_peltasts_walk_the_walkway_round_a_corner():
    b = quiet(Battle(FESTUNG, random.Random(1)))
    pelt = next(u for u in b.units(Side.STADT) if u.name == "Peltasten")
    clear(b, [pelt])
    north = min(b.blocked, key=lambda c: math.dist((c[0] + 0.5, c[1] + 0.5), (13.5, 9.5)))
    b.command_move([pelt], (north[0] + 0.5, north[1] + 0.5))
    run(b, 30)
    assert b.on_wall(pelt)
    west = min(b.blocked, key=lambda c: math.dist((c[0] + 0.5, c[1] + 0.5), (6.5, 16.5)))
    b.command_move([pelt], (west[0] + 0.5, west[1] + 0.5))    # um die Nordwestecke herum, über den Turm
    for _ in range(int(40 / DT)):
        b.update(DT)
        assert all(b._wall_level(m.pos) in ("wall", "innen") for m in pelt.all_men())   # nie nach draußen
        if math.dist(pelt.pos, (west[0] + 0.5, west[1] + 0.5)) < 0.6 and not pelt.loose:
            break
    assert b.on_wall(pelt) and math.dist(pelt.pos, (west[0] + 0.5, west[1] + 0.5)) < 0.8


# ------------------------------------------------------------------ Türme
def test_corner_towers_throw_two_spears_a_second_at_the_nearest_foe():
    b = quiet(Battle(FESTUNG, random.Random(1)))
    t = b.corner_towers[4]                                    # Nordwestecke
    foe = lone_group(b, Side.FEIND, "raeuber", 8, (t.center[0] - 1.0, t.center[1] - 3.5))
    far = lone_group(b, Side.FEIND, "raeuber", 8, (16.0, 1.0))
    clear(b, [foe, far, next(u for u in b.units(Side.STADT))])
    thrown = []
    real = b._tower_fire

    def count(dt):
        n = len(b.projectiles)
        real(dt)
        thrown.extend(b.projectiles[n:])
    b._tower_fire = count
    run(b, 5.0)
    from_t = [p for p in thrown if (p.x, p.y) == t.center]
    assert 9 <= len(from_t) <= 11                              # zwei je Sekunde
    assert all(p.target_id == foe.id for p in thrown)          # keiner auf den außer Reichweite
    assert sum(m.hp for m in foe.all_men()) < 8 * UNIT_TYPES["raeuber"].hp
    assert far.men == 8


def test_a_corner_tower_falls_to_the_enemy_who_stands_on_it():
    b = quiet(Battle(FESTUNG, random.Random(1)))
    t = b.corner_towers[0]
    assert t.owner is Side.STADT
    climber = lone_group(b, Side.FEIND, "raeuber", 1, t.center)
    climber.all_men()[0].x, climber.all_men()[0].y = t.center
    b.update(DT)
    assert t.owner is Side.FEIND
    assert any("Turm" in e for e in b.events)


# ------------------------------------------------------------- Belagerung
def test_player_rams_a_fortress_gate_open():
    b = Battle(FESTUNG_ANGRIFF, random.Random(1))
    b._ai_defenders = lambda: None
    hop = next(u for u in b.units(Side.STADT) if u.name == "Hopliten")
    assert b.command_build([hop], "ram")
    run(b, config.RAM_BUILD_TIME + 0.5)
    sw = b.gates[1]
    assert b.command_ram_gate([hop], sw) == 1
    run(b, 40)
    assert not sw.closed and all(g.closed for g in b.gates if g is not sw)


def test_player_sets_a_siege_tower_and_climbs_into_the_fortress():
    b = Battle(FESTUNG_ANGRIFF, random.Random(1))
    b._ai_defenders = lambda: None
    hop = next(u for u in b.units(Side.STADT) if u.name == "Hopliten")
    clear(b, [hop])
    b.corner_towers = []                                      # hier geht es nur ums Übersteigen
    b.command_build([hop], "tower")
    run(b, config.TOWER_BUILD_TIME + 0.5)
    cell = min((c for c in b.blocked if b.tower_step(c) is not None and c[1] >= 24 and c not in b.ladders),
               key=lambda c: abs(c[0] - 15))
    assert b.command_tower_wall([hop], cell) == 1
    run(b, 30)
    assert cell in b.crossings
    b.command_move([hop], b.agora)
    run(b, 60)
    assert b._wall_level(hop.pos) == "innen"
    assert all(b._wall_level(m.pos) == "innen" for m in hop.all_men())


def test_the_army_breaks_into_a_passive_fortress():
    b = Battle(FESTUNG, random.Random(1))
    b.command_hold()
    run(b, 240)
    assert any(not g.closed for g in b.gates) or b.crossings
    assert b.outcome == "niederlage" or b.houses_intact() < len(b.houses)


def test_the_garrison_holds_its_gates_and_reinforces_the_threatened_one():
    b = Battle(FESTUNG_ANGRIFF, random.Random(1))
    lines = [u for u in b.units(Side.FEIND) if u.share(lambda m: m.kind.hoplite) >= 0.5]
    assert lines and all(b._wall_level(u.pos) == "innen" and u.in_phalanx for u in lines)
    hop = next(u for u in b.units(Side.STADT) if u.name == "Hopliten")
    b.command_build([hop], "ram")
    run(b, config.RAM_BUILD_TIME + 0.5)
    sw = b.gates[1]
    b.command_ram_gate([hop], sw)
    run(b, 25)
    near = [u for u in lines if u.alive and math.dist(u.pos, sw.center) <= 6.0]
    assert len(near) >= 2                                      # die zweite Phalanx kommt dazu


# ------------------------------------------------------------------ Kamera
def fortress_app() -> App:
    pygame.init()
    app = App(Renderer(pygame.Surface((config.WIDTH, config.HEIGHT))), seed=1, start_in_battle=True)
    app.scenario_index = next(i for i, s in enumerate(SCENARIOS) if s.key == "festung")
    app.battle = app._new_battle()
    app.draw()
    return app


def test_fortress_starts_in_overview_and_a_tap_zooms_in():
    app = fortress_app()
    cam = app.renderer.camera
    assert cam.big and cam.overview
    assert cam.to_tiles((config.MAP_W, config.MAP_H)) == pytest.approx((app.battle.cols, app.battle.rows))
    pos = (config.MAP_W // 4, config.MAP_H // 2)
    want = cam.to_tiles(pos)
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos))
    assert not cam.overview
    w, h = cam.span()
    assert cam.ox <= want[0] <= cam.ox + w and cam.oy <= want[1] <= cam.oy + h
    app.command("ansicht")
    assert cam.overview


def test_two_fingers_pan_the_close_view_and_cancel_the_drag():
    app = fortress_app()
    cam = app.renderer.camera
    cam.zoom_to((16.0, 18.0))
    ox, oy = cam.ox, cam.oy
    app.handle_event(pygame.event.Event(pygame.FINGERDOWN, touch_id=0, finger_id=1, x=0.4, y=0.4, dx=0.0, dy=0.0))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(192, 272)))
    assert app.drag_start is not None
    app.handle_event(pygame.event.Event(pygame.FINGERDOWN, touch_id=0, finger_id=2, x=0.6, y=0.4, dx=0.0, dy=0.0))
    assert app.panning and app.drag_start is None
    for fid in (1, 2):
        app.handle_event(pygame.event.Event(pygame.FINGERMOTION, touch_id=0, finger_id=fid, x=0.5, y=0.5, dx=0.1, dy=0.1))
    assert cam.ox < ox and cam.oy < oy                        # die Karte folgt den Fingern
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(240, 320)))
    for fid in (1, 2):
        app.handle_event(pygame.event.Event(pygame.FINGERUP, touch_id=0, finger_id=fid, x=0.5, y=0.5, dx=0.0, dy=0.0))
    assert not app.panning
    assert not app.battle.line                                # kein Befehl aus dem Verschieben


def test_old_maps_have_a_fixed_view():
    pygame.init()
    app = App(Renderer(pygame.Surface((config.WIDTH, config.HEIGHT))), seed=1, start_in_battle=True)
    app.draw()
    cam = app.renderer.camera
    assert not cam.big and cam.zoom == 1.0 and (cam.ox, cam.oy) == (0.0, 0.0)
    assert "ansicht" not in {b.key for b in app.renderer.layout_bar(app.battle, False, set())}


# ------------------------------------------------------------- Hindernisse
def test_houses_are_obstacles_and_a_phalanx_takes_the_street_to_the_agora():
    """Niemand läuft durch ein Haus; eine Phalanx vom Nordtor zur Agora nimmt die breite
    Gasse und kommt an."""
    b = quiet(Battle(FESTUNG, random.Random(1)))
    hop = next(u for u in b.units(Side.STADT) if u.name == "Hopliten")
    clear(b, [hop])
    north = b.gates[0]
    start = b.gate_approach(north, -1.0, 0.8)
    hop.x, hop.y = start
    hop.facing = (0.0, 1.0)
    hop.place_men()
    b.command_line([hop], (b.agora[0] + 1.0, b.agora[1] + 2.2), (b.agora[0] - 1.0, b.agora[1] + 2.2))  # Front nach Süden, hinter der Agora
    for _ in range(int(40 / DT)):
        b.update(DT)
        assert not any(b.cell(m.x, m.y) in b.house_cells for m in hop.all_men())
        if hop.in_line:
            break
    assert hop.in_line and math.dist(hop.pos, (b.agora[0], b.agora[1] + 2.2)) < 0.3


def test_a_wide_block_goes_round_houses_it_does_not_fit_between():
    """Zwischen zwei Häusern mit einer Kachel Lücke passt keine breite Front: der Block
    geht außen herum, statt sich hindurchzuquetschen; eine Gruppe mit zwei Mann Front geht
    hindurch (gemessen wird auf Halbkacheln: so schmale Gänge sind für Einzelne gedacht)."""
    from game.scenarios import OFFENE_SIEDLUNG
    from dataclasses import replace
    scn = replace(OFFENE_SIEDLUNG, houses=((7, 10), (9, 10)))      # eine Kachel Lücke bei x = 8
    for width, through in ((14, False), (2, True)):
        b = quiet(Battle(scn, random.Random(1)))
        hop = b.units(Side.STADT)[0]
        clear(b, [hop])
        hop.x, hop.y = 8.5, 13.0
        hop.reform(width)
        hop.facing = (0.0, -1.0)
        hop.place_men()
        hop.stance = Stance.HALTEN
        hop.target = (8.5, 7.0)
        xs = []
        for _ in range(int(25 / DT)):
            b.update(DT)
            if 9.8 <= hop.y <= 11.2:
                xs.append(hop.x)
            if math.dist(hop.pos, (8.5, 7.0)) < 0.3:
                break
        assert math.dist(hop.pos, (8.5, 7.0)) < 0.5
        assert all(b.cell(m.x, m.y) not in b.house_cells for m in hop.all_men())
        went_between = bool(xs) and all(8.0 <= x <= 9.0 for x in xs)
        assert went_between == through, (width, xs[:3])


def test_standing_siege_tower_and_dropped_ram_are_obstacles():
    b = Battle(FESTUNG_ANGRIFF, random.Random(1))
    b.alarm = False
    b.towers.append((20.0, 30.0))
    b.debris.append((24.0, 30.0, 1.0, 0.0))
    b.update(DT)
    defender = next(u for u in b.units(Side.FEIND))
    attacker = next(u for u in b.units(Side.STADT))
    assert b.is_blocked(20.0, 30.0, defender)                   # wer nicht hinauf will, kommt nicht hinein
    assert b.is_blocked(24.0, 30.0) and b.is_blocked(24.2, 30.0)
    assert not b.is_blocked(24.0, 30.5)
    b.crossings.add((15, 26))                                   # steht ein Übergang, steigen die Angreifer in den Turm
    assert not b.is_blocked(20.0, 30.0, attacker)
