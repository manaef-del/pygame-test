"""Integrationstest: Spiel läuft headless einige Frames durch."""

import asyncio

import pygame

from game.app import TouchControl, read_direction, run
from game.logic import GameState
from game.render import Renderer


def test_run_headless_for_some_frames():
    state = asyncio.run(run(max_frames=30))
    assert isinstance(state, GameState)
    assert state.elapsed > 0


def test_renderer_draws_without_error():
    pygame.init()
    surface = pygame.Surface((480, 640))
    renderer = Renderer(surface)
    state = GameState()
    state.spawn_block()
    renderer.draw(state)
    state.game_over = True
    renderer.draw(state)
    pygame.quit()


def test_read_direction():
    class Keys(dict):
        def __getitem__(self, key):
            return self.get(key, False)

    assert read_direction(Keys()) == 0
    assert read_direction(Keys({pygame.K_LEFT: True})) == -1
    assert read_direction(Keys({pygame.K_d: True})) == 1
    assert read_direction(Keys({pygame.K_LEFT: True, pygame.K_RIGHT: True})) == 0


def test_touch_control_direction_and_tap():
    t = TouchControl(width=480)
    assert t.direction == 0
    t.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 300)))
    assert t.direction == -1
    assert t.consume_tap() is True
    assert t.consume_tap() is False
    t.handle(pygame.event.Event(pygame.MOUSEMOTION, pos=(400, 300)))
    assert t.direction == 1
    t.handle(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(400, 300)))
    assert t.direction == 0
    # Finger-Events liefern normierte Koordinaten 0..1
    t.handle(pygame.event.Event(pygame.FINGERDOWN, x=0.9, y=0.5))
    assert t.direction == 1
    t.handle(pygame.event.Event(pygame.FINGERUP, x=0.9, y=0.5))
    assert t.direction == 0
