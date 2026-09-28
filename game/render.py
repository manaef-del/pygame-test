"""Zeichnet Schlachtfeld, Einheiten und Bedienleiste."""

from __future__ import annotations

import math

import pygame

from . import config
from .battle import Battle
from .units import Lochos, Side, Stance

T = config.TILE


def px(p: tuple[float, float]) -> tuple[int, int]:
    return (int(round(p[0] * T)), int(round(p[1] * T)))


# Feste Verteilung der Männer innerhalb eines Lochos (Kachelbruchteile)
LINE_LAYOUT = [(-0.3, -0.12), (-0.1, -0.12), (0.1, -0.12), (0.3, -0.12),
               (-0.3, 0.12), (-0.1, 0.12), (0.1, 0.12), (0.3, 0.12)]
LOOSE_LAYOUT = [(-0.28, -0.2), (0.05, -0.3), (0.3, -0.05), (-0.1, 0.0),
                (0.2, 0.25), (-0.3, 0.2), (0.0, 0.32), (0.32, -0.3)]


class Button:
    def __init__(self, key: str, label: str, rect: pygame.Rect) -> None:
        self.key = key
        self.label = label
        self.rect = rect


class Renderer:
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small = pygame.font.Font(None, 20)
        self.big = pygame.font.Font(None, 56)
        self.buttons = self._make_buttons()

    @staticmethod
    def _make_buttons() -> list[Button]:
        top = config.MAP_H
        gap = 6
        row_h = (config.BAR_H - 3 * gap) // 2
        w3 = (config.WIDTH - 4 * gap) // 3
        w2 = (config.WIDTH - 3 * gap) // 2
        r1 = top + gap
        r2 = top + 2 * gap + row_h
        return [
            Button("angriff", "Angriff", pygame.Rect(gap, r1, w3, row_h)),
            Button("halten", "Halten", pygame.Rect(2 * gap + w3, r1, w3, row_h)),
            Button("pause", "Pause", pygame.Rect(3 * gap + 2 * w3, r1, w3, row_h)),
            Button("neu", "Neu", pygame.Rect(gap, r2, w2, row_h)),
            Button("szenario", "Szenario wechseln", pygame.Rect(2 * gap + w2, r2, w2, row_h)),
        ]

    # ------------------------------------------------------------ Karte
    def draw(self, battle: Battle, drag: tuple[float, float, float, float] | None, paused: bool) -> None:
        s = self.surface
        s.fill(config.COLOR_BG)
        self._draw_ground(battle)
        self._draw_houses(battle)
        if battle.phalanx is not None:
            x0, y0, x1, y1 = battle.phalanx.rect
            rect = pygame.Rect(px((x0, y0)), (int((x1 - x0) * T), int((y1 - y0) * T)))
            pygame.draw.rect(s, config.COLOR_CITY_DIM, rect, 1)
        for u in sorted(battle.lochoi, key=lambda u: u.y):
            if u.alive:
                self._draw_lochos(u)
        if drag is not None:
            x0, y0, x1, y1 = drag
            rect = pygame.Rect(px((min(x0, x1), min(y0, y1))),
                               (int(abs(x1 - x0) * T), int(abs(y1 - y0) * T)))
            pygame.draw.rect(s, config.COLOR_RECT, rect, 2)
        self._draw_hud(battle, paused)
        self._draw_bar(battle, paused)

    def _draw_ground(self, battle: Battle) -> None:
        s = self.surface
        pygame.draw.rect(s, config.COLOR_GROUND, pygame.Rect(0, 0, config.MAP_W, config.MAP_H))
        for c in range(config.COLS + 1):
            pygame.draw.line(s, config.COLOR_GRID, (c * T, 0), (c * T, config.MAP_H))
        for r in range(config.ROWS + 1):
            pygame.draw.line(s, config.COLOR_GRID, (0, r * T), (config.MAP_W, r * T))
        for cx, cy in battle.blocked:
            pygame.draw.rect(s, config.COLOR_PALISADE, pygame.Rect(cx * T, cy * T + T // 3, T, T // 3))
            for i in range(3):
                pygame.draw.line(s, (90, 60, 30), (cx * T + 5 + i * 10, cy * T + 4),
                                 (cx * T + 5 + i * 10, cy * T + T - 4), 3)
        if battle.gate is not None and battle.gate_center is not None:
            gx, gy = battle.gate_center
            pygame.draw.rect(s, config.COLOR_GATE,
                             pygame.Rect(int(gx * T) - T, int(gy * T) - 4, 2 * T, 8), 2)

    def _draw_houses(self, battle: Battle) -> None:
        s = self.surface
        for h in battle.houses:
            rect = pygame.Rect(h.cx * T + 3, h.cy * T + 3, T - 6, T - 6)
            color = config.COLOR_HOUSE_LOOTED if h.looted else config.COLOR_HOUSE
            pygame.draw.rect(s, color, rect, border_radius=3)
            roof = [(h.cx * T + 2, h.cy * T + 10), (h.cx * T + T // 2, h.cy * T), (h.cx * T + T - 2, h.cy * T + 10)]
            pygame.draw.polygon(s, (150, 90, 50) if not h.looted else (60, 30, 30), roof)
            if h.looted:
                cx, cy = h.cx * T + T // 2, h.cy * T + T // 2
                pygame.draw.polygon(s, config.COLOR_FIRE, [(cx - 6, cy + 8), (cx, cy - 8), (cx + 6, cy + 8)])
            elif h.progress > 0:
                frac = min(1.0, h.progress / config.LOOT_TIME)
                pygame.draw.rect(s, config.COLOR_FIRE, pygame.Rect(h.cx * T + 3, h.cy * T + T - 6, int((T - 6) * frac), 3))

    def _draw_lochos(self, u: Lochos) -> None:
        s = self.surface
        cx, cy = px(u.pos)
        if u.side is Side.STADT:
            color = config.COLOR_CITY_DIM if u.stance is Stance.FLUCHT else config.COLOR_CITY
        else:
            color = config.COLOR_ENEMY_DIM if u.stance is Stance.FLUCHT else config.COLOR_ENEMY
        radius = int(T * 0.46)
        pygame.draw.circle(s, color, (cx, cy), radius, 2)
        if u.in_phalanx:
            layout = LINE_LAYOUT
            ang = math.atan2(u.facing[1], u.facing[0]) + math.pi / 2
        else:
            layout = LOOSE_LAYOUT
            ang = 0.0
        ca, sa = math.cos(ang), math.sin(ang)
        for i in range(min(u.men, len(layout))):
            ox, oy = layout[i]
            rx, ry = ox * ca - oy * sa, ox * sa + oy * ca
            pygame.draw.circle(s, config.COLOR_MEN, (cx + int(rx * T), cy + int(ry * T)), 2)
        if u.in_phalanx:
            # Schildreihe an der Front
            fx, fy = u.facing
            f = (cx + int(fx * radius), cy + int(fy * radius))
            perp = (-fy, fx)
            a = (f[0] + int(perp[0] * radius * 0.9), f[1] + int(perp[1] * radius * 0.9))
            b = (f[0] - int(perp[0] * radius * 0.9), f[1] - int(perp[1] * radius * 0.9))
            pygame.draw.line(s, config.COLOR_SHIELD, a, b, 4)
        if u.kind.ranged_range > 0:
            pygame.draw.circle(s, color, (cx, cy), 3)

    # -------------------------------------------------------------- HUD
    def _draw_hud(self, battle: Battle, paused: bool) -> None:
        s = self.surface
        r = battle.report()
        mins, secs = divmod(int(battle.time), 60)
        text = (f"Stadt {r['stadt_start'] - r['stadt_gefallen']}   "
                f"Räuber {r['feind_start'] - r['feind_gefallen']}   "
                f"Häuser {r['haeuser_intakt']}/{r['haeuser']}   {mins}:{secs:02d}")
        strip = pygame.Surface((config.MAP_W, 26), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 120))
        s.blit(strip, (0, 0))
        s.blit(self.font.render(text, True, config.COLOR_TEXT), (8, 5))

        if battle.outcome is not None:
            panel = pygame.Surface((config.MAP_W, 120), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            s.blit(panel, (0, config.MAP_H // 2 - 70))
            title = "Abgewehrt" if battle.outcome == "sieg" else "Geplündert"
            self._center_text(self.big, title, config.COLOR_TEXT, config.MAP_H // 2 - 40)
            line = (f"Gefallen: Stadt {r['stadt_gefallen']}, Räuber {r['feind_gefallen']}   "
                    f"Häuser verloren: {r['haeuser'] - r['haeuser_intakt']}")
            self._center_text(self.font, line, config.COLOR_TEXT, config.MAP_H // 2 + 8)
            self._center_text(self.small, "Neu = noch einmal", config.COLOR_TEXT_DIM, config.MAP_H // 2 + 34)
        elif battle.alarm:
            self._center_text(self.big, "Alarm!", config.COLOR_TEXT, 60)
            self._wrap_center(self.font, battle.scenario.hint, config.COLOR_TEXT, 110)
        elif paused:
            self._center_text(self.big, "Pause", config.COLOR_TEXT, config.MAP_H // 2 - 20)
        elif battle.events:
            s.blit(self.small.render(battle.events[-1], True, config.COLOR_TEXT_DIM), (8, config.MAP_H - 22))

    def _center_text(self, font: pygame.font.Font, text: str, color, y: int) -> None:
        img = font.render(text, True, color)
        self.surface.blit(img, img.get_rect(center=(config.MAP_W // 2, y)))

    def _wrap_center(self, font: pygame.font.Font, text: str, color, y: int) -> None:
        words = text.split()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if font.size(trial)[0] > config.MAP_W - 32 and cur:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        if cur:
            lines.append(cur)
        for i, line in enumerate(lines):
            self._center_text(font, line, color, y + i * 24)

    def _draw_bar(self, battle: Battle, paused: bool) -> None:
        s = self.surface
        pygame.draw.rect(s, config.COLOR_BAR, pygame.Rect(0, config.MAP_H, config.WIDTH, config.BAR_H))
        for b in self.buttons:
            active = (b.key == "pause" and paused)
            color = config.COLOR_BUTTON_ACTIVE if active else config.COLOR_BUTTON
            pygame.draw.rect(s, color, b.rect, border_radius=6)
            label = "Weiter" if (b.key == "pause" and paused) else b.label
            if b.key == "szenario":
                label = f"Szenario: {battle.scenario.name}"
            img = self.font.render(label, True, config.COLOR_TEXT)
            s.blit(img, img.get_rect(center=b.rect.center))

    def button_at(self, pos: tuple[int, int]) -> str | None:
        for b in self.buttons:
            if b.rect.collidepoint(pos):
                return b.key
        return None
