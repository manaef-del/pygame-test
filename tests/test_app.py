"""Integrationstests: Schleife, Eingabe und Zeichnen laufen headless."""

import asyncio

import pygame

from game import config
from game.app import App, run, to_tiles
from game.render import Renderer
from game.units import Side, Stance


def make_app() -> App:
    pygame.init()
    surface = pygame.Surface((config.WIDTH, config.HEIGHT))
    return App(Renderer(surface), seed=1)


def test_run_headless_for_some_frames():
    app = asyncio.run(run(max_frames=30, seed=1))
    assert app.battle is not None


def test_drag_on_map_forms_phalanx():
    app = make_app()
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 300)))
    app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(300, 320)))
    assert app.drag_rect() is not None
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(330, 330)))
    assert app.battle.phalanx is not None
    assert app.battle.alarm is False
    x0, y0, x1, y1 = app.battle.phalanx.rect
    assert (x0, y0) == to_tiles((150, 300)) and (x1, y1) == to_tiles((330, 330))
    assert any(u.stance is Stance.PHALANX for u in app.battle.units(Side.STADT))


def test_tap_without_drag_does_nothing():
    app = make_app()
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 300)))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(153, 302)))
    assert app.battle.phalanx is None
    assert app.battle.alarm is True


def test_buttons_in_bar():
    app = make_app()
    angriff = app.renderer.buttons[0].rect.center
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=angriff))
    assert all(u.stance is Stance.ANGRIFF for u in app.battle.units(Side.STADT))
    app.tick(1.0)
    assert app.battle.time > 0

    pause = next(b for b in app.renderer.buttons if b.key == "pause").rect.center
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pause))
    t = app.battle.time
    app.tick(1.0)
    assert app.battle.time == t

    szenario = next(b for b in app.renderer.buttons if b.key == "szenario").rect.center
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=szenario))
    assert app.battle.scenario.key == "palisade"
    assert app.battle.time == 0.0


def test_renderer_draws_every_state():
    app = make_app()
    app.draw()                                   # Alarm
    app.command("halten")
    for _ in range(600):
        app.tick(1 / 30)
    app.draw()                                   # Kampf oder Ergebnis
    app.paused = True
    app.draw()                                   # Pause
    app.command("szenario")
    app.draw()                                   # Palisade
