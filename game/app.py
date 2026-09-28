"""Hauptschleife, Eingabe und Bildschirmzustand.

Asynchron, damit dieselbe Schleife nativ und im Browser (pygbag) läuft.
Berührungen kommen als Mausereignisse an, deshalb reichen diese.
"""

from __future__ import annotations

import asyncio
import random

import pygame

from . import config
from .battle import Battle
from .render import Renderer
from .scenarios import SCENARIOS

DRAG_MIN = 0.4  # Kacheln: kürzer ist ein Tipp, kein Bereich


def to_tiles(pos: tuple[int, int]) -> tuple[float, float]:
    return (pos[0] / config.TILE, pos[1] / config.TILE)


class App:
    """Zustand der Bedienung, getrennt von der Schleife (testbar)."""

    def __init__(self, renderer: Renderer, seed: int | None = None) -> None:
        self.renderer = renderer
        self.seed = seed
        self.scenario_index = 0
        self.paused = False
        self.drag_start: tuple[float, float] | None = None
        self.drag_now: tuple[float, float] | None = None
        self.running = True
        self.battle = self._new_battle()

    def _new_battle(self) -> Battle:
        rng = random.Random(self.seed) if self.seed is not None else random.Random()
        self.paused = False
        self.drag_start = self.drag_now = None
        return Battle(SCENARIOS[self.scenario_index], rng)

    # ---------------------------------------------------------- Eingabe
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            self._key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._press(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.drag_start is not None:
            self.drag_now = to_tiles(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._release(event.pos)

    def _key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_a:
            self.command("angriff")
        elif key == pygame.K_h:
            self.command("halten")
        elif key == pygame.K_SPACE:
            self.command("pause")
        elif key == pygame.K_r:
            self.command("neu")
        elif key == pygame.K_s:
            self.command("szenario")

    def _press(self, pos: tuple[int, int]) -> None:
        if pos[1] >= config.MAP_H:
            key = self.renderer.button_at(pos)
            if key:
                self.command(key)
            return
        self.drag_start = self.drag_now = to_tiles(pos)

    def _release(self, pos: tuple[int, int]) -> None:
        if self.drag_start is None:
            return
        start, end = self.drag_start, to_tiles(pos)
        self.drag_start = self.drag_now = None
        if abs(end[0] - start[0]) < DRAG_MIN and abs(end[1] - start[1]) < DRAG_MIN:
            return  # Tipp ohne Ziehen
        if self.battle.outcome is None:
            self.battle.command_phalanx(start[0], start[1], end[0], end[1])
            self.paused = False

    def command(self, key: str) -> None:
        b = self.battle
        if key == "angriff" and b.outcome is None:
            b.command_attack()
            self.paused = False
        elif key == "halten" and b.outcome is None:
            b.command_hold()
            self.paused = False
        elif key == "pause":
            if b.alarm:
                b.command_hold()  # Spiel läuft an, Lochoi halten
                self.paused = False
            else:
                self.paused = not self.paused
        elif key == "neu":
            self.battle = self._new_battle()
        elif key == "szenario":
            self.scenario_index = (self.scenario_index + 1) % len(SCENARIOS)
            self.battle = self._new_battle()

    # ------------------------------------------------------------ Takt
    def tick(self, dt: float) -> None:
        if not self.paused:
            self.battle.update(dt)

    def drag_rect(self) -> tuple[float, float, float, float] | None:
        if self.drag_start is None or self.drag_now is None:
            return None
        return (*self.drag_start, *self.drag_now)

    def draw(self) -> None:
        self.renderer.draw(self.battle, self.drag_rect(), self.paused)


async def run(max_frames: int | None = None, seed: int | None = None) -> App:
    """Startet das Spiel. ``max_frames`` begrenzt die Laufzeit (für Tests)."""
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Apoikia – Kampfprobe")
    clock = pygame.time.Clock()
    app = App(Renderer(screen), seed=seed)

    frames = 0
    while app.running:
        dt = min(clock.tick(config.FPS) / 1000.0, 0.05)
        for event in pygame.event.get():
            app.handle_event(event)
        app.tick(dt)
        app.draw()
        pygame.display.flip()

        frames += 1
        if max_frames is not None and frames >= max_frames:
            app.running = False
        await asyncio.sleep(0)  # Pflicht für pygbag/Browser

    pygame.quit()
    return app
