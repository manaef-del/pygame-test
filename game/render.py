"""Zeichnet Schlachtfeld, Gruppen, Bedienleiste und das Aufstellungsmenü."""

from __future__ import annotations

import math

import pygame

from . import config
from .geometry import dist
from .army import MAX_TIERS, OWN_MAX, OWN_MIN, Army
from .battle import Battle
from .units import FORMATION_NAMES, PLAYER_TYPES, UNIT_TYPES, Lochos, Side, Stance

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
    def __init__(self, key: str, label: str, rect: pygame.Rect, color=None,
                 active: bool = False, sub: str | None = None) -> None:
        self.key = key
        self.label = label
        self.rect = rect
        self.color = color
        self.active = active
        self.sub = sub                     # zweite, kleine Zeile


BAR_GAP = 5
BAR_ROWS = (42,)                           # nur die Befehle für die gewählten Gruppen
CHIP = 44                                  # Kantenlänge der Gruppenkacheln am rechten Kartenrand
CHIP_GAP = 4
CHIP_TOP = 54                              # unter Pause und dem Plan des Gegners
TOP_BTN_H = 28                             # Menü oben links, Pause oben rechts
TOP_BTN_Y = 4
ATTACK_LABEL = {"hopliten": "Sturm", "peltasten": "Plänkeln", "reiter": "Sturmangriff"}


class Renderer:
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small = pygame.font.Font(None, 19)
        self.big = pygame.font.Font(None, 56)
        self.buttons: list[Button] = []           # die zuletzt gezeichnete Leiste
        self.menu_buttons: list[Button] = []
        self.menu_sliders: list[tuple[int, pygame.Rect]] = []

    # ================================================== Schlacht
    def draw(self, battle: Battle, drag, paused: bool, selected: set[int], menu_open: bool = False) -> None:
        s = self.surface
        s.fill(config.COLOR_BG)
        self._draw_ground(battle)
        self._draw_houses(battle)
        for u in sorted(battle.lochoi, key=lambda u: u.y):
            if u.alive:
                self._draw_lochos(u, u.id in selected)
        for pr in battle.projectiles:
            self._draw_javelin(pr)
        self._draw_destinations(battle, paused, selected)
        if drag is not None:
            self._draw_line_preview(battle, drag, selected)
        self._draw_hud(battle, paused, selected)
        self._draw_bar(battle, paused, selected, menu_open)

    def _draw_destinations(self, battle: Battle, paused: bool, selected: set[int]) -> None:
        """Wohin eine eigene Gruppe unterwegs ist: in der Pause für alle, sonst für
        die gewählten. Das Rechteck steht am Ziel, so wie die Gruppe dort stehen wird."""
        s = self.surface
        for u in battle.units(Side.STADT, fighting_only=True):
            if u.target is None or (not paused and u.id not in selected):
                continue
            if u.stance is Stance.ANGRIFF or dist(u.pos, u.target) < 0.3:
                continue
            corners = [px(c) for c in u.corners_at(u.target, u.face_to or u.facing)]
            color = config.COLOR_SELECT if u.id in selected else config.COLOR_RECT
            pygame.draw.polygon(s, color, corners, 1)
            pygame.draw.line(s, color, px(u.pos), px(u.target), 1)
            if u.stance is Stance.PHALANX:
                a, b = corners[0], corners[1]
                pygame.draw.line(s, color, a, b, 3)

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
        if units:
            rings = [u for u in units if u.formation == "o"]
            if rings:                                      # Kreis: Mitte am Anfang, Halbmesser aus der Länge
                r = battle.ring_radius_for(rings[0], dist(start, end))
                pygame.draw.circle(s, config.COLOR_RECT, px(start), int(r * T), 1)
                label = self.small.render(f"Kreis, Halbmesser {r:.1f}", True, config.COLOR_RECT)
                s.blit(label, label.get_rect(center=px((start[0], start[1] + r + 0.4))))
                units = [u for u in units if u.formation != "o"]
                if not units:
                    return
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
        if battle.agora is not None:                     # die Agora: gepflasterter Platz, Sammelpunkt der Verteidiger
            ax, ay = px(battle.agora)
            rad = int(config.AGORA_RADIUS * T)
            pygame.draw.circle(s, config.COLOR_AGORA, (ax, ay), rad)
            for i in range(-2, 3):                       # Pflasterfugen
                off = i * rad // 3
                half = int((rad * rad - off * off) ** 0.5)
                pygame.draw.line(s, config.COLOR_AGORA_EDGE, (ax - half, ay + off), (ax + half, ay + off), 1)
            pygame.draw.circle(s, config.COLOR_AGORA_EDGE, (ax, ay), rad, 2)
            label = self.small.render("Agora", True, config.COLOR_AGORA_EDGE)
            s.blit(label, label.get_rect(center=(ax, ay)))
        for cx, cy in battle.blocked:
            pygame.draw.rect(s, config.COLOR_PALISADE, pygame.Rect(cx * T, cy * T + T // 3, T, T // 3))
            for i in range(3):
                pygame.draw.line(s, (90, 60, 30), (cx * T + 5 + i * 10, cy * T + 4), (cx * T + 5 + i * 10, cy * T + T - 4), 3)
        for cx, cy in set(battle.ladders) | set(battle.crossings):
            rails = (cx * T + 9, cx * T + T - 9)
            for rx in rails:
                pygame.draw.line(s, config.COLOR_CROSSING, (rx, cy * T + 2), (rx, cy * T + T - 2), 2)
            for i in range(4):
                pygame.draw.line(s, config.COLOR_CROSSING, (rails[0], cy * T + 5 + i * 7), (rails[1], cy * T + 5 + i * 7), 2)
        for x, y, n in battle.horses:
            for i in range(min(n, 12)):
                ox = ((i * 5) % 7 - 3) * 0.09
                oy = ((i * 3) % 5 - 2) * 0.09
                hx, hy = px((x + ox, y + oy))
                pygame.draw.circle(s, config.COLOR_HORSE, (hx, hy), 3)
        for x, y, fx, fy in battle.debris:
            a = px((x - fx * 0.25, y - fy * 0.25))
            b = px((x + fx * 0.25, y + fy * 0.25))
            pygame.draw.line(s, config.COLOR_RAM, a, b, 6)
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
        fx, fy = u.facing
        if u.loose:
            # aufgelöste Formation: kein Rechteck, nur die Männer (Auswahl als Ringe)
            if selected:
                for man in u.all_men():
                    pygame.draw.circle(s, config.COLOR_SELECT, px(man.pos), 6, 1)
        elif u.formation == "o":
            pygame.draw.circle(s, config.COLOR_SELECT if selected else ring, (cx, cy), int(u.half_w * T), 3 if selected else 1)
        elif u.formation == "keil":
            tip = px((u.x + fx * u.half_d, u.y + fy * u.half_d))
            pygame.draw.polygon(s, config.COLOR_SELECT if selected else ring, [tip, corners[2], corners[3]], 3 if selected else 1)
        elif selected:
            pygame.draw.polygon(s, config.COLOR_SELECT, corners, 3)
        else:
            pygame.draw.polygon(s, ring, corners, 1 if u.side is Side.STADT else 2)

        fx, fy = u.facing
        for row in u.rows:
            for man in row:
                color = man.kind.color
                if u.side is Side.FEIND:
                    color = desaturate(color, config.ENEMY_DESATURATION)
                if man.wounded:
                    color = tuple(c // 2 for c in color)
                if u.stance is Stance.FLUCHT:
                    color = tuple(c * 2 // 3 for c in color)
                mx, my = px(man.pos)
                if man.leader:                           # der Anführer: größer, goldener Ring
                    pygame.draw.circle(s, color, (mx, my), 4)
                    pygame.draw.circle(s, config.COLOR_LEADER, (mx, my), 5, 2)
                    continue
                pygame.draw.circle(s, color, (mx, my), 3)
                if man.bound:
                    pygame.draw.circle(s, config.COLOR_BOUND, (mx, my), 4, 1)
                if man.kind.cavalry and not man.mounted:
                    pygame.draw.circle(s, (20, 40, 20), (mx, my), 1)
        if u.in_phalanx and not u.loose and u.formation != "o":
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
        s.blit(self.font.render(text, True, config.COLOR_TEXT), (78, 9))
        plan = battle.enemy_plan
        if plan and not battle.alarm:
            img = self.small.render(f"Gegner: {plan}", True, config.COLOR_ENEMY)
            s.blit(img, img.get_rect(topright=(config.MAP_W - 8, TOP_BTN_Y + TOP_BTN_H + 4)))

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
            self._center_text(self.small, "Neu = noch einmal, Aufstellung = Truppe ändern", config.COLOR_TEXT_DIM, config.MAP_H // 2 + 34)
        elif battle.alarm:
            self._center_text(self.big, "Alarm!", config.COLOR_TEXT, 60)
            self._wrap_center(self.font, battle.scenario.hint, config.COLOR_TEXT, 110)
        elif paused:
            self._center_text(self.big, "Pause", config.COLOR_TEXT, config.MAP_H // 2 - 20)
        else:
            sel = [u for u in battle.lochoi if u.id in selected and u.alive]
            if sel:
                names = ", ".join(f"{u.name} ({u.summary()}, {FORMATION_NAMES[u.formation]}, Moral {int(u.morale * 100)} %)" for u in sel[:3])
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
        """Mittig im Kartenteil links von der Kachelspalte."""
        width = config.MAP_W - CHIP - 12 - 24
        for i, line in enumerate(self._wrap(font, text, width)):
            img = font.render(line, True, color)
            self.surface.blit(img, img.get_rect(center=(width // 2 + 12, y + i * 24)))

    def _wrap_left(self, font, text, color, y) -> None:
        for i, line in enumerate(self._wrap(font, text, config.MAP_W - 16)[:2]):
            self.surface.blit(font.render(line, True, color), (8, y + i * 18))

    # -- Kontextleiste ------------------------------------------------------
    @staticmethod
    def _bar_rows() -> list[tuple[int, int]]:
        rows, y = [], config.MAP_H + BAR_GAP
        for h in BAR_ROWS:
            rows.append((y, h))
            y += h + BAR_GAP
        return rows

    def layout_bar(self, battle: Battle, paused: bool, selected: set[int], menu_open: bool = False) -> list[Button]:
        """Alle Knöpfe für den aktuellen Zustand: Gruppenkacheln rechts, Menü
        oben links, Pause oben rechts, in der Leiste unten nur die Befehle,
        die die gewählten Gruppen gerade ausführen können."""
        W, gap = config.WIDTH, 6
        (y2, h2), = self._bar_rows()
        out: list[Button] = []
        sel = [u for u in battle.lochoi if u.id in selected and u.fighting]
        out.extend(self._chips(battle, selected))
        # oben links Menü (klappt Neu und Aufstellung darunter auf), oben rechts Pause
        out.append(Button("menue", "Zurück" if menu_open else "Menü", pygame.Rect(gap, TOP_BTN_Y, 64, TOP_BTN_H), active=menu_open))
        pause = "Los" if battle.alarm else ("Weiter" if paused else "Pause")
        out.append(Button("pause", pause, pygame.Rect(W - gap - 72, TOP_BTN_Y, 72, TOP_BTN_H), active=paused or battle.alarm))
        if menu_open:
            y = TOP_BTN_Y + TOP_BTN_H + gap
            out.append(Button("neu", "Neu", pygame.Rect(gap, y, 160, 40), sub="Szenario noch einmal"))
            out.append(Button("aufstellung", "Aufstellung", pygame.Rect(gap, y + 46, 160, 40), sub="Truppe und Szenario"))
        if battle.outcome is not None:
            half = (W - 3 * gap) // 2
            out.append(Button("neu", "Neu", pygame.Rect(gap, y2, half, h2), sub="Szenario noch einmal"))
            out.append(Button("aufstellung", "Aufstellung", pygame.Rect(2 * gap + half, y2, half, h2), sub="Truppe und Szenario"))
        elif sel:
            out.extend(self._command_row(battle, sel, y2, h2))      # auch im Alarm: dort fallen die ersten Befehle
        return out

    @staticmethod
    def _chips(battle: Battle, selected: set[int]) -> list[Button]:
        """Eine Kachel je eigene Gruppe, untereinander am rechten Kartenrand,
        oben „Alle“; sie wählen aus und zeigen Gattung, Mannzahl und Moral."""
        groups = battle.units(Side.STADT)
        if not groups:
            return []
        x = config.MAP_W - CHIP - 6
        out = [Button("alle", "Keine" if selected else "Alle", pygame.Rect(x, CHIP_TOP, CHIP, CHIP), active=bool(selected))]
        y = CHIP_TOP + CHIP + CHIP_GAP
        for u in groups:
            if y + CHIP > config.MAP_H - 44:
                break                                     # mehr passt nicht neben die Karte
            out.append(Button(f"group:{u.id}", str(u.men), pygame.Rect(x, y, CHIP, CHIP), active=u.id in selected))
            y += CHIP + CHIP_GAP
        return out

    def _command_row(self, battle: Battle, sel: list[Lochos], y: int, h: int) -> list[Button]:
        """Befehle je Waffengattung der Auswahl; gemischte Auswahl nur das Gemeinsame."""
        W, gap = config.WIDTH, 6
        arms = {u.arm() for u in sel}
        arm = next(iter(arms)) if len(arms) == 1 else "gemischt"
        mixed = any(battle.mixed(u) for u in sel)                 # gemischte Gruppe: teilt sich beim Angriff
        items: list[tuple[str, str, float, bool, str | None]] = [           # key, label, Gewicht, aktiv, Unterzeile
            ("angriff", "Angriff" if mixed else ATTACK_LABEL.get(arm, "Angriff"), 1.6, False,
             "je Gattung" if mixed else None),
            ("halten", "Phalanx bilden" if arm == "hopliten" else "Halten", 1.6, False, None),
        ]
        if len(sel) >= 2:
            items.append(("vereinen", "Vereinen", 1.4, False, None))
        if arm != "gemischt":
            opts = sel[0].formation_options()
            for name in opts:
                items.append((f"formation:{name}", FORMATION_NAMES[name].replace("-Stellung", ""), 0.9,
                              all(u.formation == name for u in sel), None))
        if battle.scenario.ram_available:
            gate_open = battle.gate is not None and not battle.gate.closed
            for key, kind, name in (("rammbock", "ram", "Rammbock"), ("turm", "tower", "Turm")):
                carrying = any(u.engine == kind for u in sel)
                building = any(u.build_kind == kind for u in sel)
                if kind == "ram" and gate_open and not carrying and not building:
                    continue                                              # das Tor ist schon offen
                sub = "ablegen" if carrying else ("abbrechen" if building else "bauen")
                items.append((key, name, 1.4, carrying or building, sub))
        total = sum(it[2] for it in items)
        unit = (W - gap * (len(items) + 1)) / total
        out, x = [], float(gap)
        for key, label, weight, active, sub in items:
            w = unit * weight
            out.append(Button(key, label, pygame.Rect(int(x), y, int(w), h), active=active, sub=sub))
            x += w + gap
        return out

    @staticmethod
    def _group_state(battle: Battle, u: Lochos) -> str:
        if u.stance is Stance.FLUCHT:
            return "Flucht"
        if u.engine is not None:
            return "Rammbock" if u.engine == "ram" else "Turm"
        if u.building is not None:
            return "baut"
        if u.engaged:
            return "im Kampf"
        if battle.on_wall(u):
            return "Wehrgang"
        if u.stance is Stance.PHALANX:
            return "Phalanx" if u.in_phalanx else "formiert sich"
        if u.stance is Stance.PLAENKELN:
            return "plänkelt"
        if u.stance is Stance.ANGRIFF:
            return "greift an"
        return "unterwegs" if u.target is not None else "hält"

    def _draw_bar(self, battle: Battle, paused: bool, selected: set[int], menu_open: bool = False) -> None:
        s = self.surface
        pygame.draw.rect(s, config.COLOR_BAR, pygame.Rect(0, config.MAP_H, config.WIDTH, config.BAR_H))
        self.buttons = self.layout_bar(battle, paused, selected, menu_open)
        (y2, h2), = self._bar_rows()
        by_id = {u.id: u for u in battle.lochoi}
        for b in self.buttons:
            if b.key.startswith("group:"):
                self._draw_chip(b, by_id[int(b.key.split(":")[1])])
                continue
            if b.key == "alle":
                pygame.draw.rect(s, config.COLOR_BUTTON_ACTIVE if b.active else config.COLOR_BUTTON, b.rect, border_radius=6)
                img = self.small.render(b.label, True, config.COLOR_TEXT)
                s.blit(img, img.get_rect(center=b.rect.center))
                continue
            pygame.draw.rect(s, config.COLOR_BUTTON_ACTIVE if b.active else config.COLOR_BUTTON, b.rect, border_radius=6)
            label, sub = b.label, b.sub
            if not sub and self.small.size(label)[0] > b.rect.w - 6 and " " in label:
                label, sub = label.split(" ", 1)              # passt nicht in eine Zeile: umbrechen
            if sub:
                font = self.font if self.font.size(label)[0] <= b.rect.w - 8 else self.small
                img = font.render(label, True, config.COLOR_TEXT)
                s.blit(img, img.get_rect(center=(b.rect.centerx, b.rect.centery - 7)))
                img = self.small.render(sub, True, config.COLOR_TEXT_DIM if not b.active else config.COLOR_TEXT)
                s.blit(img, img.get_rect(center=(b.rect.centerx, b.rect.centery + 10)))
            else:
                font = self.font if self.font.size(label)[0] <= b.rect.w - 8 else self.small
                img = font.render(label, True, config.COLOR_TEXT)
                s.blit(img, img.get_rect(center=b.rect.center))
        if not any(b.key in ("angriff", "neu") for b in self.buttons):
            if not battle.units(Side.STADT):
                hint = ""
            elif battle.alarm:
                hint = "Gruppe wählen und aufstellen, Los startet die Schlacht"
            else:
                hint = "Gruppe wählen: Kachel rechts oder Gruppe im Feld antippen"
            img = self.small.render(hint, True, config.COLOR_TEXT_DIM)
            s.blit(img, img.get_rect(center=(config.WIDTH // 2, y2 + h2 // 2)))

    def _draw_chip(self, b: Button, u: Lochos) -> None:
        """Gruppenkachel: Sinnbild der Gattung, Mannzahl, Moralbalken; gewählt blau,
        im Kampf orange umrandet, auf der Flucht ausgegraut."""
        s = self.surface
        fleeing = u.stance is Stance.FLUCHT
        pygame.draw.rect(s, config.COLOR_BUTTON_ACTIVE if b.active else config.COLOR_BUTTON, b.rect, border_radius=6)
        if u.engaged and not fleeing:
            pygame.draw.rect(s, config.COLOR_BOUND, b.rect, 2, border_radius=6)
        lead = u.rows[0][0].kind if u.rows and u.rows[0] else None
        color = config.COLOR_CITY if lead is None else lead.color
        if fleeing:
            color = desaturate(color, 0.7)
        cx, cy = b.rect.x + 11, b.rect.y + 11                 # Sinnbild oben links
        arm = u.arm()
        if arm == "reiter":                               # Pferdekopf
            pygame.draw.polygon(s, color, [(cx - 6, cy + 6), (cx + 6, cy + 6), (cx + 2, cy - 6), (cx - 2, cy - 3)])
        elif arm == "peltasten":                          # Wurfspeer
            pygame.draw.line(s, color, (cx - 6, cy + 6), (cx + 5, cy - 5), 2)
            pygame.draw.polygon(s, color, [(cx + 6, cy - 6), (cx + 1, cy - 5), (cx + 5, cy - 1)])
        else:                                             # Rundschild
            pygame.draw.circle(s, color, (cx, cy), 7)
            pygame.draw.circle(s, config.COLOR_BAR, (cx, cy), 7, 1)
            pygame.draw.circle(s, config.COLOR_BAR, (cx, cy), 2)
        if u.leader_man() is not None:                    # Abzeichen: der Anführer kämpft hier mit
            pygame.draw.circle(s, config.COLOR_LEADER, (b.rect.right - 8, b.rect.y + 8), 4)
            pygame.draw.circle(s, config.COLOR_BAR, (b.rect.right - 8, b.rect.y + 8), 4, 1)
        text = config.COLOR_TEXT_DIM if fleeing else config.COLOR_TEXT
        img = self.font.render(b.label, True, text)         # Mannzahl unten rechts
        s.blit(img, img.get_rect(bottomright=(b.rect.right - 4, b.rect.bottom - 6)))
        bar = pygame.Rect(b.rect.x + 4, b.rect.bottom - 5, b.rect.w - 8, 2)
        pygame.draw.rect(s, config.COLOR_BAR, bar)
        m = max(0.0, min(1.0, u.morale))
        pygame.draw.rect(s, (int(200 - 120 * m), int(80 + 100 * m), 70), pygame.Rect(bar.x, bar.y, int(bar.w * m), bar.h))

    def button_at(self, pos: tuple[int, int], battle: Battle | None = None, paused: bool = False,
                  selected: set[int] | None = None, menu_open: bool = False) -> str | None:
        buttons = self.layout_bar(battle, paused, selected or set(), menu_open) if battle is not None else self.buttons
        for b in buttons:
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
        # Vorrat: ein gemeinsamer Topf für alle Gattungen
        y, x = 48, 8
        for key in PLAYER_TYPES:
            kind = UNIT_TYPES[key]
            pygame.draw.circle(s, kind.color, (x + 6, y + 8), 5)
            txt = self.small.render(f"{army.used(key)} {kind.short}", True, config.COLOR_TEXT)
            s.blit(txt, (x + 16, y))
            x += 62
        free = army.remaining()
        note = f"{free} Mann noch frei" if free > 0 else "alle Männer eingeteilt"
        s.blit(self.small.render(note + "  ·  Gattungen frei tauschbar", True, config.COLOR_TEXT_DIM), (8, y + 16))

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
        title = f"{g.name}  ({index + 1}/{len(army.groups)})  ·  {g.men()} Mann" + ("  + Anführer" if g.leader else "")
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
        if g.leader:
            self._menu_button("leader", "Anführer kämpft in dieser Gruppe", pygame.Rect(gap, y, W - 2 * gap, 36),
                              config.COLOR_BUTTON_ACTIVE)
            pygame.draw.circle(s, config.COLOR_LEADER, (gap + 18, y + 18), 6)
        else:
            self._menu_button("leader", "Anführer zu dieser Gruppe holen", pygame.Rect(gap, y, W - 2 * gap, 36))
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
