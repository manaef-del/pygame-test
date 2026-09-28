"""Hauptschleife, Eingabe und Bildschirmzustand (Aufstellung / Schlacht).

Asynchron, damit dieselbe Schleife nativ und im Browser (pygbag) läuft.
Berührungen kommen als Mausereignisse an, deshalb reichen diese.
"""

from __future__ import annotations

import asyncio
import copy
import random

import pygame

from . import config
from .army import OWN_DEFAULT, OWN_MAX, OWN_MIN, Army, default_army, scaled_army
from .battle import Battle
from .render import Renderer
from .scenarios import SCENARIOS
from .units import Side

DRAG_MIN = 0.4  # Kacheln: kürzer ist ein Tipp, kein Bereich


def to_tiles(pos: tuple[int, int]) -> tuple[float, float]:
    return (pos[0] / config.TILE, pos[1] / config.TILE)


class App:
    """Zustand der Bedienung, getrennt von der Schleife (testbar)."""

    def __init__(self, renderer: Renderer, seed: int | None = None, start_in_battle: bool = False) -> None:
        self.renderer = renderer
        self.seed = seed
        self.scenario_index = 0
        self.army: Army = default_army()
        self.menu_group = 0
        self.screen = "schlacht" if start_in_battle else "aufstellung"
        self.paused = False
        self.selected: set[int] = set()
        self.drag_start: tuple[float, float] | None = None
        self.drag_now: tuple[float, float] | None = None
        self.running = True
        self.menu_slider: tuple[int, pygame.Rect] | None = None
        self.enemy_counts: dict[str, int] = {s.key: s.enemy_default for s in SCENARIOS}
        self.own_count = OWN_DEFAULT
        self.battle = self._new_battle()

    def _new_battle(self) -> Battle:
        rng = random.Random(self.seed) if self.seed is not None else random.Random()
        self.paused = False
        self.selected = set()
        self.drag_start = self.drag_now = None
        scn = SCENARIOS[self.scenario_index]
        army = scaled_army(self.army, self.own_count) if self.army.total_men() else copy.deepcopy(self.army)
        return Battle(scn, rng, army=army, enemy_count=self.enemy_counts[scn.key])

    # ---------------------------------------------------------- Eingabe
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            self._key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._press(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.menu_slider is not None:
            self._slide(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.drag_start is not None:
            self.drag_now = to_tiles(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._release(event.pos)

    def _key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.running = False
        elif self.screen == "aufstellung":
            if key == pygame.K_RETURN:
                self.menu_command("start")
            return
        elif key == pygame.K_a:
            self.command("angriff")
        elif key == pygame.K_h:
            self.command("halten")
        elif key == pygame.K_SPACE:
            self.command("pause")
        elif key == pygame.K_r:
            self.command("neu")
        elif key == pygame.K_m:
            self.command("aufstellung")

    def _press(self, pos: tuple[int, int]) -> None:
        if self.screen == "aufstellung":
            key = self.renderer.menu_button_at(pos)
            if key:
                self.menu_command(key)
                return
            slider = self.renderer.slider_at(pos)
            if slider:
                self.menu_slider = slider
                self._slide(pos)
            return
        if pos[1] >= config.MAP_H:
            key = self.renderer.button_at(pos, self.battle)
            if key:
                self.command(key)
            return
        self.drag_start = self.drag_now = to_tiles(pos)

    def _slide(self, pos: tuple[int, int]) -> None:
        """Schieberegler: Anzahl aus der Fingerposition."""
        tier, rect = self.menu_slider
        frac = min(1.0, max(0.0, (pos[0] - rect.x) / rect.w))
        if tier == -1:
            scn = SCENARIOS[self.scenario_index]
            self.enemy_counts[scn.key] = scn.enemy_min + round(frac * (scn.enemy_max - scn.enemy_min))
            return
        if tier == -2:
            self.own_count = OWN_MIN + round(frac * (OWN_MAX - OWN_MIN))
            return
        if tier >= len(self.army.groups[self.menu_group].tiers):
            self.menu_slider = None
            return
        maximum = self.army.max_for(self.menu_group, tier)
        self.army.set_count(self.menu_group, tier, round(frac * maximum))

    def _release(self, pos: tuple[int, int]) -> None:
        self.menu_slider = None
        if self.drag_start is None:
            return
        start, end = self.drag_start, to_tiles(pos)
        self.drag_start = self.drag_now = None
        if self.battle.outcome is not None:
            return
        if abs(end[0] - start[0]) < DRAG_MIN and abs(end[1] - start[1]) < DRAG_MIN:
            self._tap(end)
            return
        self.battle.command_line(self._selection(), start, end)
        self.paused = False

    def _tap(self, p: tuple[float, float]) -> None:
        """Tipp: eigene Gruppe wählen, Räuber angreifen, sonst hinlaufen."""
        b = self.battle
        own = b.unit_at(p, Side.STADT)
        if own is not None and own.fighting:
            if own.id in self.selected and len(self.selected) == 1:
                self.selected = set()
            else:
                self.selected = {own.id}
            return
        if b.gate is not None and b.gate.closed and b.gate_at(p):
            b.command_ram_gate(self._selection())
            self.paused = False
            return
        if not self.selected:
            return
        foe = b.unit_at(p, Side.FEIND)
        if foe is not None:
            b.command_attack_target(self._selection(), foe)
        else:
            b.command_move(self._selection(), p)
        self.paused = False

    def _selection(self):
        if not self.selected:
            return None
        return [u for u in self.battle.lochoi if u.id in self.selected and u.fighting]

    def command(self, key: str) -> None:
        b = self.battle
        if key == "angriff" and b.outcome is None:
            b.command_attack(self._selection())
            self.paused = False
        elif key == "halten" and b.outcome is None:
            b.command_hold(self._selection())
            self.paused = False
        elif key == "rammbock" and b.outcome is None:
            if b.command_build_ram(self._selection()):
                self.paused = False
        elif key == "alle":
            if self.selected:
                self.selected = set()
            else:
                self.selected = {u.id for u in b.units(Side.STADT, fighting_only=True)}
        elif key == "pause":
            if b.alarm:
                b.alarm = False
                self.paused = False
            else:
                self.paused = not self.paused
        elif key == "neu":
            self.battle = self._new_battle()
        elif key == "aufstellung":
            self.screen = "aufstellung"
            self.menu_group = min(self.menu_group, len(self.army.groups) - 1)

    # ------------------------------------------------------- Aufstellung
    def menu_command(self, key: str) -> None:
        a = self.army
        if key == "prev":
            self.menu_group = (self.menu_group - 1) % len(a.groups)
        elif key == "next":
            self.menu_group = (self.menu_group + 1) % len(a.groups)
        elif key == "add":
            if a.add_group():
                self.menu_group = len(a.groups) - 1
        elif key == "del":
            a.delete_group(self.menu_group)
            self.menu_group = min(self.menu_group, len(a.groups) - 1)
        elif key == "preset":
            self.army = default_army()
            self.menu_group = 0
        elif key == "scenario":
            self.scenario_index = (self.scenario_index + 1) % len(SCENARIOS)
        elif key == "start":
            if a.valid():
                self.screen = "schlacht"
                self.battle = self._new_battle()
        elif key == "addrow":
            a.add_tier(self.menu_group)
        elif key.startswith("delrow:"):
            a.remove_tier(self.menu_group, int(key.split(":")[1]))
        elif key.startswith("up:"):
            a.move_tier(self.menu_group, int(key.split(":")[1]), -1)
        elif key.startswith("down:"):
            a.move_tier(self.menu_group, int(key.split(":")[1]), +1)
        elif key.startswith("kind:"):
            _, tier, kind = key.split(":")
            a.set_kind(self.menu_group, int(tier), kind)

    # ------------------------------------------------------------ Takt
    def tick(self, dt: float) -> None:
        if self.screen == "schlacht" and not self.paused:
            self.battle.update(dt * config.TIME_SCALE)
            self.selected = {i for i in self.selected if (u := self.battle.by_id(i)) and u.fighting}

    def drag_rect(self):
        if self.drag_start is None or self.drag_now is None:
            return None
        return (*self.drag_start, *self.drag_now)

    def draw(self) -> None:
        if self.screen == "aufstellung":
            scn = SCENARIOS[self.scenario_index]
            self.renderer.draw_menu(self.army, self.menu_group, scn, self.enemy_counts[scn.key], self.own_count)
        else:
            self.renderer.draw(self.battle, self.drag_rect(), self.paused, self.selected)


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
