"""Hauptschleife: Fenster, Eingaben, Zeitsteuerung."""

from __future__ import annotations

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


def run(max_frames: int | None = None) -> GameState:
    """Startet das Spiel. ``max_frames`` begrenzt die Laufzeit (für Tests)."""
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Dodge – Pygame Test")
    clock = pygame.time.Clock()

    state = GameState()
    renderer = Renderer(screen)

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

        state.update(dt, read_direction(pygame.key.get_pressed()))
        renderer.draw(state)
        pygame.display.flip()

        frames += 1
        if max_frames is not None and frames >= max_frames:
            running = False

    pygame.quit()
    return state
