"""Hauptschleife: Fenster, Eingaben, Zeitsteuerung.

Die Schleife ist asynchron, damit sie sowohl nativ (``asyncio.run``) als
auch im Browser über pygbag (WebAssembly) läuft. Im Browser muss jede
Iteration die Kontrolle mit ``await asyncio.sleep(0)`` abgeben.
"""

from __future__ import annotations

import asyncio

import pygame

from . import config
from .logic import GameState
from .render import Renderer


def read_direction(keys) -> int:
    """Liest die Tastatur und liefert -1, 0 oder 1."""
    direction = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        direction -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        direction += 1
    return direction


class TouchControl:
    """Touch- und Maussteuerung: linke Hälfte = links, rechte Hälfte = rechts.

    Solange der Finger (oder die Maustaste) gehalten wird, bewegt sich der
    Spieler. Wird die Position über die Mitte gezogen, wechselt die
    Richtung. Pygbag liefert Touch-Eingaben als Maus- und Finger-Events,
    deshalb werden beide ausgewertet.
    """

    def __init__(self, width: int) -> None:
        self.width = width
        self.direction = 0
        self.pressed = False
        self.tapped = False  # Ein Tipp in diesem Frame (für Neustart)

    def _direction_for_x(self, x: float) -> int:
        return -1 if x < self.width / 2 else 1

    def handle(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._press(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._release()
        elif event.type == pygame.MOUSEMOTION and self.pressed:
            self.direction = self._direction_for_x(event.pos[0])
        elif event.type == pygame.FINGERDOWN:
            self._press(event.x * self.width)
        elif event.type == pygame.FINGERUP:
            self._release()
        elif event.type == pygame.FINGERMOTION and self.pressed:
            self.direction = self._direction_for_x(event.x * self.width)

    def _press(self, x: float) -> None:
        self.pressed = True
        self.tapped = True
        self.direction = self._direction_for_x(x)

    def _release(self) -> None:
        self.pressed = False
        self.direction = 0

    def consume_tap(self) -> bool:
        tapped, self.tapped = self.tapped, False
        return tapped


async def run(max_frames: int | None = None) -> GameState:
    """Startet das Spiel. ``max_frames`` begrenzt die Laufzeit (für Tests)."""
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Dodge – Pygame Test")
    clock = pygame.time.Clock()

    state = GameState()
    renderer = Renderer(screen)
    touch = TouchControl(config.WIDTH)

    running = True
    frames = 0
    while running:
        dt = clock.tick(config.FPS) / 1000.0
        dt = min(dt, 0.05)  # Sprünge nach Pausen begrenzen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and state.game_over:
                    state.reset()
            else:
                touch.handle(event)

        if touch.consume_tap() and state.game_over:
            state.reset()
            touch.direction = 0

        direction = read_direction(pygame.key.get_pressed()) or touch.direction
        state.update(dt, direction)
        renderer.draw(state)
        pygame.display.flip()

        frames += 1
        if max_frames is not None and frames >= max_frames:
            running = False

        await asyncio.sleep(0)  # Pflicht für pygbag/Browser

    pygame.quit()
    return state
