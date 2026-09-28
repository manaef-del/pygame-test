"""Integrationstests: Schleife, Menü, Eingabe und Zeichnen laufen headless."""

import asyncio

import pygame

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


def test_menu_edits_army_and_starts_battle():
    app = make_app(start_in_battle=False)
    app.draw()  # legt die Menüknöpfe an
    before = app.army.groups[0].men()
    key_minus = next(b for b in app.renderer.menu_buttons if b.key == "minus:0:reiter")
    press(app, key_minus.rect.center)
    assert app.army.groups[0].men() == before - 1
    app.draw()
    key_plus = next(b for b in app.renderer.menu_buttons if b.key == "plus:1:reiter")
    press(app, key_plus.rect.center)
    assert app.army.groups[0].men() == before
    assert app.army.groups[0].rows[1]["reiter"] == 1

    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "add").rect.center)
    assert len(app.army.groups) == 7 and app.menu_group == 6
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "start").rect.center)
    assert app.screen == "schlacht"
    assert app.battle.army.groups[0].rows[1]["reiter"] == 1
    assert app.battle.men(Side.STADT) == 75


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


def test_drag_forms_phalanx_for_selection():
    app = make_app()
    b = app.battle
    unit = b.units(Side.STADT)[1]
    press(app, pos_of(app, unit))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 300)))
    app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(300, 320)))
    assert app.drag_rect() is not None
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(330, 330)))
    assert b.phalanx is not None and len(b.phalanx.slots) == 1
    assert unit.stance is Stance.PHALANX
    x0, y0 = to_tiles((150, 300))
    assert (b.phalanx.rect[0], b.phalanx.rect[1]) == (x0, y0)


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
