"""Zeichnet einen ``GameState`` auf eine Pygame-Surface."""

from __future__ import annotations

import pygame

from . import config
from .logic import GameState


class Renderer:
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        pygame.font.init()
        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 64)

    def draw(self, state: GameState) -> None:
        s = self.surface
        s.fill(config.COLOR_BG)

        pygame.draw.rect(s, config.COLOR_PLAYER, state.player.rect, border_radius=4)
        for block in state.blocks:
            pygame.draw.rect(s, config.COLOR_BLOCK, block.rect, border_radius=3)

        score = self.font.render(f"Punkte: {state.score}", True, config.COLOR_TEXT)
        s.blit(score, (12, 10))

        if state.game_over:
            self._draw_centered(self.big_font, "GAME OVER", config.COLOR_TEXT, -30)
            self._draw_centered(
                self.font, "R oder Tippen = Neustart", config.COLOR_TEXT_DIM, 30
            )
            self._draw_centered(self.font, "Esc = Beenden", config.COLOR_TEXT_DIM, 60)
        elif state.elapsed < 3.0:
            self._draw_centered(
                self.font, "Links/rechts tippen oder Pfeiltasten",
                config.COLOR_TEXT_DIM, 120,
            )

    def _draw_centered(
        self, font: pygame.font.Font, text: str, color: tuple, dy: int
    ) -> None:
        img = font.render(text, True, color)
        rect = img.get_rect(center=(self.surface.get_width() // 2,
                                    self.surface.get_height() // 2 + dy))
        self.surface.blit(img, rect)
