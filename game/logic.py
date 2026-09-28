"""Reine Spiellogik ohne Pygame-Fenster.

Alles hier arbeitet mit ``pygame.Rect`` und einfachen Zahlen. Es wird kein
Display benötigt, deshalb lässt sich dieses Modul vollständig mit pytest
testen.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

import pygame

from . import config


@dataclass
class Block:
    """Ein fallender Block."""

    rect: pygame.Rect
    speed: float

    def update(self, dt: float) -> None:
        self.rect.y += round(self.speed * dt)

    def is_off_screen(self, height: int = config.HEIGHT) -> bool:
        return self.rect.top >= height


@dataclass
class Player:
    """Der vom Spieler gesteuerte Balken am unteren Rand."""

    rect: pygame.Rect
    speed: float = config.PLAYER_SPEED

    @classmethod
    def create(cls, width: int = config.WIDTH, height: int = config.HEIGHT) -> "Player":
        rect = pygame.Rect(0, 0, config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
        rect.centerx = width // 2
        rect.bottom = height - config.PLAYER_BOTTOM_MARGIN
        return cls(rect=rect)

    def move(self, direction: int, dt: float, width: int = config.WIDTH) -> None:
        """Bewegt den Spieler. ``direction`` ist -1 (links), 0 oder 1 (rechts)."""
        if direction == 0:
            return
        self.rect.x += round(direction * self.speed * dt)
        self.rect.clamp_ip(pygame.Rect(0, 0, width, self.rect.bottom + 1))


@dataclass
class GameState:
    """Kompletter Zustand einer Spielrunde."""

    width: int = config.WIDTH
    height: int = config.HEIGHT
    rng: random.Random = field(default_factory=random.Random)
    player: Player = field(init=False)
    blocks: list[Block] = field(default_factory=list)
    score: int = 0
    game_over: bool = False
    spawn_interval: float = config.SPAWN_START_INTERVAL
    time_since_spawn: float = 0.0
    elapsed: float = 0.0

    def __post_init__(self) -> None:
        self.player = Player.create(self.width, self.height)

    # ------------------------------------------------------------------ Spawn
    def block_speed(self) -> float:
        return config.BLOCK_START_SPEED + config.BLOCK_SPEED_GAIN * self.score

    def spawn_block(self) -> Block:
        size = self.rng.randint(config.BLOCK_MIN_SIZE, config.BLOCK_MAX_SIZE)
        x = self.rng.randint(0, self.width - size)
        block = Block(rect=pygame.Rect(x, -size, size, size), speed=self.block_speed())
        self.blocks.append(block)
        self.spawn_interval = max(
            config.SPAWN_MIN_INTERVAL, self.spawn_interval * config.SPAWN_INTERVAL_DECAY
        )
        return block

    # ----------------------------------------------------------------- Update
    def update(self, dt: float, direction: int = 0) -> None:
        """Einen Zeitschritt ``dt`` (Sekunden) simulieren."""
        if self.game_over:
            return

        self.elapsed += dt
        self.player.move(direction, dt, self.width)

        self.time_since_spawn += dt
        while self.time_since_spawn >= self.spawn_interval:
            self.time_since_spawn -= self.spawn_interval
            self.spawn_block()

        survivors: list[Block] = []
        for block in self.blocks:
            block.update(dt)
            if block.rect.colliderect(self.player.rect):
                self.game_over = True
                survivors.append(block)
            elif block.is_off_screen(self.height):
                self.score += 1
            else:
                survivors.append(block)
        self.blocks = survivors

    def reset(self) -> None:
        """Neue Runde starten, Zufallsgenerator bleibt erhalten."""
        self.player = Player.create(self.width, self.height)
        self.blocks.clear()
        self.score = 0
        self.game_over = False
        self.spawn_interval = config.SPAWN_START_INTERVAL
        self.time_since_spawn = 0.0
        self.elapsed = 0.0
