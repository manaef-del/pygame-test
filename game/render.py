"""Zeichnet Schlachtfeld, Gruppen, Bedienleiste und das Aufstellungsmenü."""

from __future__ import annotations

import math

import pygame

from . import config
from .army import MAX_TIERS, OWN_MAX, OWN_MIN, Army
from .battle import Battle
from .units import PLAYER_TYPES, UNIT_TYPES, Lochos, Side, Stance

T = config.TILE
MAN_SPACING = config.MAN_SPACING
ROW_SPACING = config.ROW_SPACING


def px(p: tuple[float, float]) -> tuple[int, int]:
    return (int(round(p[0] * T)), int(round(p[1] * T)))


def desaturate(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    """Farbe Richtung Grau mischen (0 = unverändert, 1 = grau)."""
    grey = int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
    return tuple(int(c + (grey - c) * amount) for c in color)


class Button:
    def __init__(self, key: str, label: str, rect: pygame.Rect, color=None) -> None:
        self.key = key
        self.label = label
        self.rect = rect
        self.color = color


class Renderer:
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small = pygame.font.Font(None, 19)
        self.big = pygame.font.Font(None, 56)
        self.buttons: list[Button] = self._battle_buttons()
        self.menu_buttons: list[Button] = []
        self.menu_sliders: list[tuple[int, pygame.Rect]] = []

    # ================================================== Schlacht
    @staticmethod
    def _battle_buttons() -> list[Button]:
        top = config.MAP_H
        gap = 6
        row_h = (config.BAR_H - 3 * gap) // 2
        w4 = (config.WIDTH - 5 * gap) // 4
        w2 = (config.WIDTH - 3 * gap) // 2
        r1 = top + gap
        r2 = top + 2 * gap + row_h
        w3 = (config.WIDTH - 4 * gap) // 3
        return [
            Button("angriff", "Angriff", pygame.Rect(gap, r1, w4, row_h)),
            Button("halten", "Halten", pygame.Rect(2 * gap + w4, r1, w4, row_h)),
            Button("alle", "Alle", pygame.Rect(3 * gap + 2 * w4, r1, w4, row_h)),
            Button("pause", "Pause", pygame.Rect(4 * gap + 3 * w4, r1, w4, row_h)),
            Button("neu", "Neu", pygame.Rect(gap, r2, w4, row_h)),
            Button("aufstellung", "Aufstellung", pygame.Rect(2 * gap + w4, r2, w4, row_h)),
            Button("rammbock", "Rammbock", pygame.Rect(3 * gap + 2 * w4, r2, w4, row_h)),
            Button("turm", "Turm", pygame.Rect(4 * gap + 3 * w4, r2, w4, row_h)),
        ]

    def draw(self, battle: Battle, drag, paused: bool, selected: set[int]) -> None:
        s = self.surface
        s.fill(config.COLOR_BG)
        self._draw_ground(battle)
        self._draw_houses(battle)
        for u in sorted(battle.lochoi, key=lambda u: u.y):
            if u.alive:
                self._draw_lochos(u, u.id in selected)
        for pr in battle.projectiles:
            self._draw_javelin(pr)
        if drag is not None:
            self._draw_line_preview(battle, drag, selected)
        self._draw_hud(battle, paused, selected)
        self._draw_bar(battle, paused, selected)

    def _draw_javelin(self, pr) -> None:
        x, y = pr.pos
        dx, dy = pr.tx - pr.x, pr.ty - pr.y
        l = math.hypot(dx, dy) or 1.0
        ux, uy = dx / l * 0.18, dy / l * 0.18
        a = px((x - ux, y - uy))
        b = px((x + ux, y + uy))
        pygame.draw.line(self.surface, config.COLOR_JAVELIN, a, b, 2)

    def _draw_line_preview(self, battle: Battle, drag, selected: set[int]) -> None:
        """Beim Ziehen: Linie und die daraus entstehende Aufstellung."""
        s = self.surface
        start, end = (drag[0], drag[1]), (drag[2], drag[3])
        pygame.draw.line(s, config.COLOR_RECT, px(start), px(end), 2)
        units = [u for u in battle.lochoi if u.id in selected and u.fighting] if selected else None
        for plan in battle.plan_line(units, start, end):
            fx, fy = plan.facing
            ax, ay = -fy, fx   # entlang der Linie
            half_w = plan.width * MAN_SPACING / 2
            depth = plan.depth * ROW_SPACING
            cx, cy = plan.center
            corners = [
                (cx + ax * half_w, cy + ay * half_w),
                (cx - ax * half_w, cy - ay * half_w),
                (cx - ax * half_w - fx * depth, cy - ay * half_w - fy * depth),
                (cx + ax * half_w - fx * depth, cy + ay * half_w - fy * depth),
            ]
            pygame.draw.polygon(s, config.COLOR_RECT, [px(c) for c in corners], 1)
            tip = px((cx + fx * 0.45, cy + fy * 0.45))
            pygame.draw.line(s, config.COLOR_SHIELD, px((cx, cy)), tip, 2)
            label = self.small.render(f"{plan.width} breit, {plan.depth} tief", True, config.COLOR_RECT)
            lx, ly = px((cx - fx * (depth + 0.35), cy - fy * (depth + 0.35)))
            s.blit(label, label.get_rect(center=(lx, ly)))

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
                pygame.draw.line(s, (90, 60, 30), (cx * T + 5 + i * 10, cy * T + 4), (cx * T + 5 + i * 10, cy * T + T - 4), 3)
        for x, y, fx, fy in battle.debris:
            a = px((x - fx * 0.25, y - fy * 0.25))
            b = px((x + fx * 0.25, y + fy * 0.25))
            pygame.draw.line(s, config.COLOR_RAM, a, b, 6)
        for cx, cy in battle.crossings:
            rect = pygame.Rect(cx * T + 2, cy * T + 2, T - 4, T - 4)
            pygame.draw.rect(s, config.COLOR_CROSSING, rect, border_radius=3)
        for x, y in battle.towers:
            tx, ty = px((x, y))
            body = pygame.Rect(tx - 11, ty - 14, 22, 28)
            pygame.draw.rect(s, config.COLOR_TOWER, body, border_radius=3)
            pygame.draw.rect(s, (90, 60, 30), body, 2)
            for i in range(3):
                pygame.draw.line(s, (90, 60, 30), (body.x + 4, body.y + 7 + i * 7), (body.right - 4, body.y + 7 + i * 7), 2)
        if battle.gate is not None:
            gx, gy = battle.gate.center
            half = len(battle.gate.cells) / 2
            rect = pygame.Rect(int((gx - half) * T), int(gy * T) - 6, int(2 * half * T), 12)
            if battle.gate.closed:
                pygame.draw.rect(s, config.COLOR_GATE_CLOSED, rect, border_radius=3)
                frac = battle.gate.hp / battle.gate.hp_max
                pygame.draw.rect(s, config.COLOR_FIRE, pygame.Rect(rect.x, rect.bottom + 2, int(rect.w * frac), 3))
            else:
                pygame.draw.rect(s, config.COLOR_GATE, rect, 2)

    def _draw_houses(self, battle: Battle) -> None:
        s = self.surface
        for h in battle.houses:
            rect = pygame.Rect(h.cx * T + 3, h.cy * T + 3, T - 6, T - 6)
            pygame.draw.rect(s, config.COLOR_HOUSE_LOOTED if h.looted else config.COLOR_HOUSE, rect, border_radius=3)
            roof = [(h.cx * T + 2, h.cy * T + 10), (h.cx * T + T // 2, h.cy * T), (h.cx * T + T - 2, h.cy * T + 10)]
            pygame.draw.polygon(s, (60, 30, 30) if h.looted else (150, 90, 50), roof)
            if h.looted:
                cx, cy = h.cx * T + T // 2, h.cy * T + T // 2
                pygame.draw.polygon(s, config.COLOR_FIRE, [(cx - 6, cy + 8), (cx, cy - 8), (cx + 6, cy + 8)])
            elif h.progress > 0:
                frac = min(1.0, h.progress / config.LOOT_TIME)
                pygame.draw.rect(s, config.COLOR_FIRE, pygame.Rect(h.cx * T + 3, h.cy * T + T - 6, int((T - 6) * frac), 3))

    def _draw_lochos(self, u: Lochos, selected: bool) -> None:
        s = self.surface
        cx, cy = px(u.pos)
        if u.side is Side.STADT:
            ring = config.COLOR_CITY_DIM if u.stance is Stance.FLUCHT else config.COLOR_CITY
        else:
            ring = config.COLOR_ENEMY_DIM if u.stance is Stance.FLUCHT else config.COLOR_ENEMY
        corners = [px(c) for c in u.corners()]
        if selected:
            pygame.draw.polygon(s, config.COLOR_SELECT, corners, 3)
        else:
            pygame.draw.polygon(s, ring, corners, 1 if u.side is Side.STADT else 2)

        fx, fy = u.facing
        n_rows = len(u.rows)
        for r, row in enumerate(u.rows):
            forward = ((n_rows - 1) / 2 - r) * ROW_SPACING
            n = len(row)
            for i, man in enumerate(row):
                side = (i - (n - 1) / 2) * MAN_SPACING
                ox = fx * forward + (-fy) * side
                oy = fy * forward + fx * side
                color = man.kind.color
                if u.side is Side.FEIND:
                    color = desaturate(color, config.ENEMY_DESATURATION)
                if u.stance is Stance.FLUCHT:
                    color = tuple(c // 2 for c in color)
                pygame.draw.circle(s, color, (cx + int(ox * T), cy + int(oy * T)), 3)
        if u.in_phalanx:
            a, b = corners[0], corners[1]
            pygame.draw.line(s, config.COLOR_SHIELD, a, b, 4)
        kind = u.engine or u.build_kind
        if kind == "ram":
            a = px((u.x + fx * (u.half_d + 0.05), u.y + fy * (u.half_d + 0.05)))
            b = px((u.x + fx * (u.half_d + 0.55), u.y + fy * (u.half_d + 0.55)))
            pygame.draw.line(s, config.COLOR_RAM, a, b, 6)
        elif kind == "tower":
            tx, ty = px((u.x + fx * (u.half_d + 0.35), u.y + fy * (u.half_d + 0.35)))
            pygame.draw.rect(s, config.COLOR_TOWER, pygame.Rect(tx - 7, ty - 9, 14, 18), border_radius=2)
            pygame.draw.rect(s, (90, 60, 30), pygame.Rect(tx - 7, ty - 9, 14, 18), 1)
        if kind is not None:
            if u.building is not None:
                needed = config.RAM_BUILD_TIME if u.build_kind == "ram" else config.TOWER_BUILD_TIME
                frac = min(1.0, u.building / needed)
                bar = pygame.Rect(cx - 15, cy - int(u.half_d * T) - 12, 30, 4)
                pygame.draw.rect(s, config.COLOR_BUTTON, bar)
                pygame.draw.rect(s, config.COLOR_SHIELD, pygame.Rect(bar.x, bar.y, int(30 * frac), 4))
        if u.side is Side.STADT:
            label = self.small.render(str(u.men), True, ring)
            lx, ly = px((u.x - fx * (u.half_d + 0.3), u.y - fy * (u.half_d + 0.3)))
            s.blit(label, label.get_rect(center=(lx, ly)))

    def _draw_hud(self, battle: Battle, paused: bool, selected: set[int]) -> None:
        s = self.surface
        r = battle.report()
        mins, secs = divmod(int(battle.time), 60)
        text = f"Stadt {r['stadt_start'] - r['stadt_gefallen']}   Feind {r['feind_start'] - r['feind_gefallen']}   "
        if not battle.attacking:
            text += f"Häuser {r['haeuser_intakt']}/{r['haeuser']}   "
        if battle.gate is not None:
            text += f"Tor {int(100 * battle.gate.hp / battle.gate.hp_max)}%   " if battle.gate.closed else "Tor offen   "
        text += f"{mins}:{secs:02d}"
        strip = pygame.Surface((config.MAP_W, 26), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 120))
        s.blit(strip, (0, 0))
        s.blit(self.font.render(text, True, config.COLOR_TEXT), (8, 5))

        if battle.outcome is not None:
            panel = pygame.Surface((config.MAP_W, 120), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            s.blit(panel, (0, config.MAP_H // 2 - 70))
            if battle.attacking:
                title = "Sieg" if battle.outcome == "sieg" else "Gescheitert"
            else:
                title = "Abgewehrt" if battle.outcome == "sieg" else "Geplündert"
            self._center_text(self.big, title, config.COLOR_TEXT, config.MAP_H // 2 - 40)
            line = f"Gefallen: Stadt {r['stadt_gefallen']}, Feind {r['feind_gefallen']}"
            if not battle.attacking:
                line += f"   Häuser verloren: {r['haeuser'] - r['haeuser_intakt']}"
            self._center_text(self.font, line, config.COLOR_TEXT, config.MAP_H // 2 + 8)
            self._center_text(self.small, "Neu = noch einmal", config.COLOR_TEXT_DIM, config.MAP_H // 2 + 34)
        elif battle.alarm:
            self._center_text(self.big, "Alarm!", config.COLOR_TEXT, 60)
            self._wrap_center(self.font, battle.scenario.hint, config.COLOR_TEXT, 110)
        elif paused:
            self._center_text(self.big, "Pause", config.COLOR_TEXT, config.MAP_H // 2 - 20)
        else:
            sel = [u for u in battle.lochoi if u.id in selected and u.alive]
            if sel:
                names = ", ".join(f"{u.name} ({u.summary()})" for u in sel[:3])
                if len(sel) > 3:
                    names += f" +{len(sel) - 3}"
                msg = "Gewählt: " + names + "  ·  Tippen = hin, Feind = Angriff, Ziehen = Front, Tor/Wall = Gerät ansetzen"
            elif battle.events:
                msg = battle.events[-1]
            else:
                msg = ""
            self._wrap_left(self.small, msg, config.COLOR_TEXT_DIM, config.MAP_H - 40)

    def _center_text(self, font, text, color, y) -> None:
        img = font.render(text, True, color)
        self.surface.blit(img, img.get_rect(center=(config.MAP_W // 2, y)))

    def _wrap(self, font, text, width) -> list[str]:
        lines, cur = [], ""
        for w in text.split():
            trial = (cur + " " + w).strip()
            if font.size(trial)[0] > width and cur:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        if cur:
            lines.append(cur)
        return lines

    def _wrap_center(self, font, text, color, y) -> None:
        for i, line in enumerate(self._wrap(font, text, config.MAP_W - 32)):
            self._center_text(font, line, color, y + i * 24)

    def _wrap_left(self, font, text, color, y) -> None:
        for i, line in enumerate(self._wrap(font, text, config.MAP_W - 16)[:2]):
            self.surface.blit(font.render(line, True, color), (8, y + i * 18))

    def _draw_bar(self, battle: Battle, paused: bool, selected: set[int]) -> None:
        s = self.surface
        pygame.draw.rect(s, config.COLOR_BAR, pygame.Rect(0, config.MAP_H, config.WIDTH, config.BAR_H))
        sel_units = [u for u in battle.lochoi if u.id in selected and u.fighting]
        for b in self.buttons:
            if b.key in ("rammbock", "turm") and not battle.scenario.ram_available:
                continue
            active = (b.key == "pause" and paused) or (b.key == "alle" and selected)
            label = b.label
            if b.key == "pause":
                label = "Los" if battle.alarm else ("Weiter" if paused else "Pause")
            if b.key == "alle" and selected:
                label = "Keine"
            if b.key in ("rammbock", "turm"):
                kind = "ram" if b.key == "rammbock" else "tower"
                if sel_units and any(u.engine == kind for u in sel_units):
                    label, active = ("Rammbock bereit" if kind == "ram" else "Turm bereit"), True
                elif sel_units and any(u.build_kind == kind for u in sel_units):
                    label, active = "Bau läuft", True
                elif not sel_units:
                    label = ("Rammbock" if kind == "ram" else "Turm") + " (Gruppe wählen)"
                else:
                    label = "Rammbock bauen" if kind == "ram" else "Turm bauen"
            pygame.draw.rect(s, config.COLOR_BUTTON_ACTIVE if active else config.COLOR_BUTTON, b.rect, border_radius=6)
            font = self.font if len(label) <= 12 else self.small
            img = font.render(label, True, config.COLOR_TEXT)
            s.blit(img, img.get_rect(center=b.rect.center))

    def button_at(self, pos: tuple[int, int], battle: Battle | None = None) -> str | None:
        for b in self.buttons:
            if b.key in ("rammbock", "turm") and battle is not None and not battle.scenario.ram_available:
                continue
            if b.rect.collidepoint(pos):
                return b.key
        return None

    # ================================================== Aufstellung
    def draw_menu(self, army: Army, index: int, scenario, enemy_count: int, own_count: int) -> None:
        """Aufstellungsmenü: Szenario, Gegnerstärke, eine Gruppe je Seite mit Reihen-Blöcken."""
        s = self.surface
        s.fill(config.COLOR_MENU_BG)
        self.menu_buttons = []
        self.menu_sliders = []
        W = config.WIDTH
        gap = 6

        self._center_text(self.big, "Aufstellung", config.COLOR_TEXT, 24)
        # Vorrat (Vorlage für die Mischung)
        y, x = 48, 8
        for key in PLAYER_TYPES:
            kind = UNIT_TYPES[key]
            pygame.draw.circle(s, kind.color, (x + 6, y + 8), 5)
            txt = self.small.render(f"{army.remaining(key)}/{army.pool[key]}", True, config.COLOR_TEXT)
            s.blit(txt, (x + 16, y))
            x += 92
        s.blit(self.small.render("Vorlage: noch frei / gesamt", True, config.COLOR_TEXT_DIM), (8, y + 16))

        # Eigene Stärke und Gegnerstärke
        y = 80
        own_label = f"Eigene Truppe: {own_count} Mann"
        enemy_label = ("Räuber" if scenario.enemy_kind == "raeuber" else "Feind (wie deine Truppe)") + f": {enemy_count} Mann"
        for key, label, value, lo, hi, color in (
            (-2, own_label, own_count, OWN_MIN, OWN_MAX, config.COLOR_CITY),
            (-1, enemy_label, enemy_count, scenario.enemy_min, scenario.enemy_max, config.COLOR_ENEMY),
        ):
            s.blit(self.small.render(label, True, config.COLOR_TEXT), (gap + 2, y))
            track = pygame.Rect(230, y + 2, W - gap - 230, 14)
            pygame.draw.rect(s, config.COLOR_BUTTON, track, border_radius=7)
            frac = (value - lo) / max(1, hi - lo)
            pygame.draw.rect(s, color, pygame.Rect(track.x, track.y, max(14, int(track.w * frac)), track.h), border_radius=7)
            pygame.draw.circle(s, config.COLOR_TEXT, (track.x + int(track.w * frac), track.centery), 10)
            self.menu_sliders.append((key, track))
            y += 24

        # Szenario
        y += 2
        self._menu_button("scenario", f"Szenario: {scenario.name}", pygame.Rect(gap, y, W - 2 * gap, 32))
        y += 36

        # Gruppenwahl
        self._menu_button("prev", "<", pygame.Rect(gap, y, 48, 34))
        self._menu_button("next", ">", pygame.Rect(W - gap - 48, y, 48, 34))
        g = army.groups[index]
        title = f"{g.name}  ({index + 1}/{len(army.groups)})  ·  {g.men()} Mann"
        self._center_text(self.font, title, config.COLOR_TEXT, y + 17)

        # Reihen-Blöcke, vorn nach hinten
        y += 40
        block_h = 58
        for i, tier in enumerate(g.tiers):
            kind = UNIT_TYPES[tier.kind]
            panel = pygame.Rect(gap, y, W - 2 * gap, block_h)
            pygame.draw.rect(s, config.COLOR_MENU_PANEL, panel, border_radius=6)
            label = "Vorn" if i == 0 else ("Hinten" if i == len(g.tiers) - 1 else f"Reihe {i + 1}")
            s.blit(self.small.render(label, True, config.COLOR_TEXT_DIM), (gap + 8, y + 6))
            # Typwahl: fünf Farbpunkte
            for k, key in enumerate(PLAYER_TYPES):
                cx, cy = gap + 18 + k * 26, y + 44
                pygame.draw.circle(s, UNIT_TYPES[key].color, (cx, cy), 8)
                if key == tier.kind:
                    pygame.draw.circle(s, config.COLOR_TEXT, (cx, cy), 11, 2)
                self.menu_buttons.append(Button(f"kind:{i}:{key}", key, pygame.Rect(cx - 13, cy - 13, 26, 26)))
            # Anzahl und Regler
            maximum = army.max_for(index, i)
            name = self.small.render(f"{tier.count} {kind.name}  (max. {maximum})", True, config.COLOR_TEXT)
            s.blit(name, (150, y + 6))
            track = pygame.Rect(150, y + 34, 220, 16)
            pygame.draw.rect(s, config.COLOR_BUTTON, track, border_radius=8)
            frac = tier.count / maximum if maximum else 0.0
            if frac > 0:
                pygame.draw.rect(s, kind.color, pygame.Rect(track.x, track.y, max(16, int(track.w * frac)), track.h), border_radius=8)
            knob = (track.x + int(track.w * frac), track.centery)
            pygame.draw.circle(s, config.COLOR_TEXT, knob, 11)
            self.menu_sliders.append((i, track))
            # Verschieben und Entfernen
            bx = W - gap - 92
            self._menu_button(f"up:{i}", "^", pygame.Rect(bx, y + 6, 40, 26))
            self._menu_button(f"down:{i}", "v", pygame.Rect(bx, y + 36, 40, 26))
            self._menu_button(f"delrow:{i}", "x", pygame.Rect(bx + 46, y + 6, 40, 56))
            y += block_h + gap
        if len(g.tiers) < MAX_TIERS:
            self._menu_button("addrow", "+ Reihe", pygame.Rect(gap, y, W - 2 * gap, 36))
            y += 42
        # Gruppen verwalten und Start
        y = config.HEIGHT - 2 * 40 - 3 * gap
        w3 = (W - 4 * gap) // 3
        self._menu_button("add", "+ Gruppe", pygame.Rect(gap, y, w3, 40))
        self._menu_button("del", "Gruppe löschen", pygame.Rect(2 * gap + w3, y, w3, 40))
        self._menu_button("preset", "Vorgabe", pygame.Rect(3 * gap + 2 * w3, y, w3, 40))
        y += 40 + gap
        self._menu_button("start", "Zur Schlacht >", pygame.Rect(gap, y, W - 2 * gap, 40), config.COLOR_BUTTON_ACTIVE)

    def slider_at(self, pos: tuple[int, int]) -> tuple[int, pygame.Rect] | None:
        for tier, rect in self.menu_sliders:
            if rect.inflate(24, 24).collidepoint(pos):
                return tier, rect
        return None

    def _menu_button(self, key: str, label: str, rect: pygame.Rect, color=None) -> None:
        s = self.surface
        pygame.draw.rect(s, color or config.COLOR_BUTTON, rect, border_radius=6)
        font = self.font if len(label) < 18 else self.small
        img = font.render(label, True, config.COLOR_TEXT)
        s.blit(img, img.get_rect(center=rect.center))
        self.menu_buttons.append(Button(key, label, rect, color))

    def menu_button_at(self, pos: tuple[int, int]) -> str | None:
        for b in self.menu_buttons:
            if b.rect.collidepoint(pos):
                return b.key
        return None
