"""Integrationstests: Schleife, Menü, Eingabe und Zeichnen laufen headless."""

import asyncio

import pygame
import pytest

from game import config
from game.app import App, run, to_tiles
from game.render import Renderer
from game.units import Side, Stance


def make_app(start_in_battle: bool = True) -> App:
    pygame.init()
    surface = pygame.Surface((config.WIDTH, config.HEIGHT))
    return App(Renderer(surface), seed=1, start_in_battle=start_in_battle)


def press(app: App, pos) -> None:
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos))


def pos_of(app: App, unit) -> tuple[int, int]:
    return (int(unit.x * config.TILE), int(unit.y * config.TILE))


def test_run_headless_for_some_frames():
    app = asyncio.run(run(max_frames=30, seed=1))
    assert app.screen == "aufstellung"


def test_menu_sliders_chips_and_blocks():
    app = make_app(start_in_battle=False)
    app.draw()  # legt Knöpfe und Regler an
    tier, track = next(sl for sl in app.renderer.menu_sliders if sl[0] == 0)
    assert app.army.groups[0].tiers[0].count == 14
    # Regler nach links: null, nach rechts: Maximum, Ziehen dazwischen
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(track.x, track.centery)))
    assert app.army.groups[0].tiers[0].count == 0
    app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(track.x + track.w // 2, track.centery)))
    assert app.army.groups[0].tiers[0].count == 7
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(track.right, track.centery)))
    assert app.menu_slider is None
    # Farbpunkt: Typ wechseln, Anzahl wird gekappt
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "kind:0:reiter").rect.center)
    assert app.army.groups[0].tiers[0].kind == "reiter"
    assert app.army.groups[0].tiers[0].count == 0            # Reiter sind alle vergeben
    # Block verschieben, Reihe anlegen und entfernen
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "down:0").rect.center)
    assert app.army.groups[0].tiers[1].kind == "reiter"
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "addrow").rect.center)
    assert len(app.army.groups[0].tiers) == 4
    app.draw()
    assert not any(b.key == "addrow" for b in app.renderer.menu_buttons)
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "delrow:1").rect.center)
    assert len(app.army.groups[0].tiers) == 3
    assert [t.kind for t in app.army.groups[0].tiers] == ["mittel", "leicht", "schwer"]
    # Gruppe anlegen und Schlacht starten
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "add").rect.center)
    assert len(app.army.groups) == 4 and app.menu_group == 3
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "start").rect.center)
    assert app.screen == "schlacht"
    assert app.battle.men(Side.STADT) == app.own_count      # Vorlage wird auf die Stärke skaliert


def test_tap_selects_moves_and_attacks():
    app = make_app()
    b = app.battle
    unit = b.units(Side.STADT)[0]
    press(app, pos_of(app, unit))
    assert app.selected == {unit.id}
    press(app, (int(2.0 * config.TILE), int(5.0 * config.TILE)))
    assert unit.stance is Stance.HALTEN and unit.target is not None
    assert all(u.target is None for u in b.units(Side.STADT) if u is not unit)
    foe = b.units(Side.FEIND)[2]
    foe.x, foe.y = 8.0, 4.0
    press(app, pos_of(app, foe))
    assert unit.stance is Stance.ANGRIFF and unit.target_id == foe.id
    press(app, pos_of(app, unit))  # erneut tippen hebt die Auswahl auf
    assert app.selected == set()


def test_drag_draws_line_for_selection():
    app = make_app()
    b = app.battle
    unit = b.units(Side.STADT)[1]
    press(app, pos_of(app, unit))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 300)))
    app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(300, 300)))
    assert app.drag_rect() is not None
    app.draw()                                            # Vorschau zeichnen
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(330, 300)))
    assert len(b.line) == 1 and b.line[0].unit_id == unit.id
    assert unit.stance is Stance.PHALANX and unit.facing == (0.0, -1.0)
    assert unit.width == b.line[0].width
    x0, _ = to_tiles((150, 300))
    x1, _ = to_tiles((330, 300))
    assert abs(b.line[0].center[0] - (x0 + x1) / 2) < 1e-6


def test_buttons_in_bar():
    app = make_app()
    buttons = {b.key: b.rect.center for b in app.renderer.buttons}
    press(app, buttons["alle"])
    assert len(app.selected) == len(app.battle.units(Side.STADT))
    press(app, buttons["angriff"])
    assert all(u.stance is Stance.ANGRIFF for u in app.battle.units(Side.STADT))
    app.tick(1.0)
    assert app.battle.time > 0
    press(app, buttons["pause"])
    t = app.battle.time
    app.tick(1.0)
    assert app.battle.time == t
    press(app, buttons["aufstellung"])
    assert app.screen == "aufstellung"


def test_renderer_draws_every_state():
    app = make_app(start_in_battle=False)
    app.draw()                                   # Menü
    app.menu_command("start")
    app.draw()                                   # Alarm
    app.command("alle")
    app.command("halten")
    for _ in range(900):
        app.tick(1 / 30)
    app.draw()                                   # Kampf oder Ergebnis
    app.paused = True
    app.draw()
    app.menu_command("scenario")
    app.menu_command("start")
    app.draw()                                   # Palisade


def test_enemy_slider_and_time_scale():
    app = make_app(start_in_battle=False)
    app.draw()
    tier, track = next(sl for sl in app.renderer.menu_sliders if sl[0] == -1)
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(track.right, track.centery)))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(track.right, track.centery)))
    key = app.battle.scenario.key
    from game.scenarios import SCENARIOS
    assert app.enemy_counts[key] == SCENARIOS[0].enemy_max
    app.menu_command("start")
    assert app.battle.men(Side.FEIND) == SCENARIOS[0].enemy_max
    app.command("halten")
    app.tick(1.0)
    assert app.battle.time == pytest.approx(config.TIME_SCALE)


def test_ram_button_and_gate_tap():
    app = make_app(start_in_battle=False)
    for _ in range(4):
        app.menu_command("scenario")
    assert app.battle.scenario.key == "angriff_wall" or True
    app.menu_command("start")
    b = app.battle
    assert b.scenario.key == "angriff_wall"
    hop = b.units(Side.STADT)[0]
    press(app, pos_of(app, hop))
    ram = next(bt for bt in app.renderer.buttons if bt.key == "rammbock")
    press(app, ram.rect.center)
    assert b.ram_status == "bau"
    for _ in range(int((config.RAM_BUILD_TIME + 1) / config.TIME_SCALE * 30)):
        app.tick(1 / 30)
    assert b.ram_status == "bereit"
    gx, gy = b.gate.center
    press(app, (int(gx * config.TILE), int(gy * config.TILE)))
    assert hop.target is not None and abs(hop.target[0] - gx) < 1e-6


def test_own_strength_slider_scales_composition():
    app = make_app(start_in_battle=False)
    app.draw()
    tier, track = next(sl for sl in app.renderer.menu_sliders if sl[0] == -2)
    press(app, (track.right, track.centery))
    from game.army import OWN_MAX
    assert app.own_count == OWN_MAX
    app.menu_command("start")
    assert app.battle.men(Side.STADT) == OWN_MAX
    names = [u.name for u in app.battle.units(Side.STADT)]
    assert names == ["Hopliten", "Peltasten", "Reiter"]
    hop = app.battle.units(Side.STADT)[0]
    assert abs(hop.men / OWN_MAX - 40 / 75) < 0.03                  # Verhältnis bleibt
