"""Zeichnet Schlachtfeld, Gruppen, Bedienleiste und das Aufstellungsmenü."""

from __future__ import annotations

import math

import pygame

from . import config
from .geometry import dist
from .army import MAX_TIERS, OWN_MAX, OWN_MIN, Army, arm_of
from .battle import Battle
from .scenarios import PLACES
from .units import FORMATION_NAMES, PLAYER_TYPES, UNIT_TYPES, Lochos, Side, Stance

T = config.TILE                 # Kachelgröße in Pixeln in der aktuellen Ansicht (Übersicht: kleiner)
MAN_SPACING = config.MAN_SPACING
ROW_SPACING = config.ROW_SPACING
_OX = 0.0                       # linke obere Ecke der Ansicht in Kacheln
_OY = 0.0


def px(p: tuple[float, float]) -> tuple[int, int]:
    return (int(round((p[0] - _OX) * T)), int(round((p[1] - _OY) * T)))


class Camera:
    """Was von der Karte zu sehen ist: Maßstab (1 = Nahansicht, kleiner = Übersicht, bis
    ``MAX_ZOOM`` hineingezoomt) und die linke obere Ecke in Kacheln. Mit zwei Fingern
    (oder dem Mausrad) zoomt man stufenlos; große Karten wechseln per Knopf
    zwischen Übersicht (alles) und Nahansicht."""

    def __init__(self) -> None:
        self.zoom = 1.0
        self.ox = 0.0
        self.oy = 0.0
        self.cols = config.COLS
        self.rows = config.ROWS

    def fit(self, cols: int, rows: int) -> None:
        """Neue Karte: große Karten beginnen in der Übersicht."""
        self.cols, self.rows = cols, rows
        self.zoom = self.overview_zoom()
        self.ox = self.oy = 0.0
        self.clamp()

    def overview_zoom(self) -> float:
        return min(1.0, config.MAP_W / (self.cols * config.TILE), config.MAP_H / (self.rows * config.TILE))

    @property
    def big(self) -> bool:
        return self.overview_zoom() < 1.0

    @property
    def overview(self) -> bool:
        return self.big and self.zoom < 1.0

    def span(self) -> tuple[float, float]:
        t = config.TILE * self.zoom
        return config.MAP_W / t, config.MAP_H / t

    def clamp(self) -> None:
        w, h = self.span()
        self.ox = min(max(self.ox, 0.0), max(0.0, self.cols - w))
        self.oy = min(max(self.oy, 0.0), max(0.0, self.rows - h))

    def to_tiles(self, pos: tuple[int, int]) -> tuple[float, float]:
        t = config.TILE * self.zoom
        return (pos[0] / t + self.ox, pos[1] / t + self.oy)

    @property
    def zoomed_in(self) -> bool:
        """Näher als die ganze Karte bzw. die Nahansicht: Dann gibt es den Knopf zurück."""
        return self.zoom > max(1.0, self.overview_zoom()) + 1e-6

    def zoom_at(self, factor: float, center: tuple[float, float]) -> None:
        """Um ``factor`` zoomen (größer = näher), die Stelle unter ``center`` (Bildpunkte)
        bleibt dabei unter dem Finger."""
        anchor = self.to_tiles(center)
        self.zoom = min(config.MAX_ZOOM, max(self.overview_zoom(), self.zoom * factor))
        t = config.TILE * self.zoom
        self.ox, self.oy = anchor[0] - center[0] / t, anchor[1] - center[1] / t
        self.clamp()

    def zoom_to(self, p: tuple[float, float]) -> None:
        """Nahansicht, die Stelle ``p`` in der Mitte."""
        self.zoom = 1.0
        w, h = self.span()
        self.ox, self.oy = p[0] - w / 2, p[1] - h / 2
        self.clamp()

    def toggle(self, around: tuple[float, float] | None = None) -> None:
        if not self.big:
            self.zoom = 1.0                                 # kleine Karte: zurück zur ganzen Ansicht
            self.ox = self.oy = 0.0
            return
        if self.overview:
            w, h = self.span()
            self.zoom_to(around or (self.ox + w / 2, self.oy + h / 2))
        else:
            self.zoom = self.overview_zoom()
            self.ox = self.oy = 0.0
            self.clamp()

    def pan(self, dx_px: float, dy_px: float) -> None:
        """Um so viele Bildschirmpunkte verschieben (die Karte folgt dem Finger)."""
        t = config.TILE * self.zoom
        self.ox -= dx_px / t
        self.oy -= dy_px / t
        self.clamp()

    def apply(self) -> None:
        global T, _OX, _OY
        T = config.TILE * self.zoom
        _OX, _OY = self.ox, self.oy


def shown(man) -> tuple[int, int]:
    """Wo ein Mann gezeichnet wird: an seiner (geglätteten) Stelle, im Gerangel zum Gegner hin verschoben."""
    if man.sx is None:
        return px((man.x + man.show_dx, man.y + man.show_dy))
    return px((man.sx + man.show_dx, man.sy + man.show_dy))


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
VERBAND_HEAD = 14                          # Kopfzeile eines Verbands über seinen Kacheln
TOP_BTN_H = 28                             # Menü oben links, Pause oben rechts
TOP_BTN_Y = 4
ATTACK_LABEL = {"hopliten": "Sturm", "peltasten": "Plänkeln", "reiter": "Sturmangriff"}


class Renderer:
    arranging: int | None = None                  # Verband, dessen Anordnung gerade bearbeitet wird
    arrange_drag: tuple | None = None             # (Gruppe, Fingerposition), die gerade verschoben wird
    _selected: set = set()

    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small = pygame.font.Font(None, 19)
        self.big = pygame.font.Font(None, 56)
        self.buttons: list[Button] = []           # die zuletzt gezeichnete Leiste
        self.menu_buttons: list[Button] = []
        self.menu_sliders: list[tuple[int, pygame.Rect]] = []
        self.camera = Camera()

    # ================================================== Schlacht
    def draw(self, battle: Battle, drag, paused: bool, selected: set[int], menu_open: bool = False) -> None:
        s = self.surface
        s.fill(config.COLOR_BG)
        cam = self.camera
        if (cam.cols, cam.rows) != (battle.cols, battle.rows):
            cam.fit(battle.cols, battle.rows)
        cam.apply()
        s.set_clip(pygame.Rect(0, 0, config.MAP_W, config.MAP_H))
        try:
            self._draw_field(battle, drag, paused, selected)
        finally:
            s.set_clip(None)
            Camera().apply()                          # Leiste und Anzeigen im Bildschirmmaß
        self._draw_hud(battle, paused, selected)
        self._draw_bar(battle, paused, selected, menu_open)
        if self.arranging is not None:
            self._draw_arrange(battle, self.arranging, self.arrange_drag)

    def _draw_field(self, battle: Battle, drag, paused: bool, selected: set[int]) -> None:
        s = self.surface
        self._draw_ground(battle)
        self._draw_houses(battle)
        for p, _ in battle.fallen_marks:                   # wo eben einer fiel
            pygame.draw.circle(s, config.COLOR_FALLEN, px(p), 3)
        frames = paused or drag is not None               # Formationsrechtecke nur in der Pause und beim Aufziehen
        for u in sorted(battle.lochoi, key=lambda u: u.y):
            if u.alive:
                self._draw_lochos(u, u.id in selected, frames)
        for pr in battle.projectiles:
            self._draw_javelin(pr)
        if frames:
            self._draw_destinations(battle, paused, selected)
        if drag is not None:
            self._draw_line_preview(battle, drag, selected)

    def _draw_destinations(self, battle: Battle, paused: bool, selected: set[int]) -> None:
        """Wohin eine eigene Gruppe unterwegs ist: in der Pause für alle, beim Aufziehen
        für die gewählten. Das Rechteck steht am Ziel, so wie die Gruppe dort stehen wird."""
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
                depth = len(rings[0].ring_plan(r))
                label = self.small.render(f"Kreis, {depth} Ring{'e' if depth != 1 else ''}", True, config.COLOR_RECT)
                s.blit(label, label.get_rect(center=px((start[0], start[1] + r + 0.4))))
                units = [u for u in units if u.formation != "o"]
                if not units:
                    return
        plans = battle.plan_line(units, start, end)
        boxes = []                                         # Blöcke als Bildschirmrechtecke: dort keine Schrift
        for plan in plans:
            fx, fy = plan.facing
            ax, ay = -fy, fx   # entlang der Linie
            g = battle.by_id(plan.unit_id)
            half_w = plan.width * (g.man_gap() if g else MAN_SPACING) / 2
            half_d = plan.depth * (g.row_gap() if g else ROW_SPACING) / 2
            cx, cy = plan.center                           # die Mitte des Blocks, wie er stehen wird
            corners = [
                (cx + ax * half_w + fx * half_d, cy + ay * half_w + fy * half_d),
                (cx - ax * half_w + fx * half_d, cy - ay * half_w + fy * half_d),
                (cx - ax * half_w - fx * half_d, cy - ay * half_w - fy * half_d),
                (cx + ax * half_w - fx * half_d, cy + ay * half_w - fy * half_d),
            ]
            pts = [px(c) for c in corners]
            pygame.draw.polygon(s, config.COLOR_RECT, pts, 1)
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            boxes.append(pygame.Rect(min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
            fx0, fy0 = cx + fx * half_d, cy + fy * half_d
            tip = px((fx0 + fx * 0.45, fy0 + fy * 0.45))
            pygame.draw.line(s, config.COLOR_SHIELD, px((fx0, fy0)), tip, 2)
        taken = list(boxes)
        for plan in plans:
            # Beschriftung hinter den Block, sonst daneben oder davor; wo alles belegt ist, keine
            fx, fy = plan.facing
            g = battle.by_id(plan.unit_id)
            half_w = plan.width * (g.man_gap() if g else MAN_SPACING) / 2
            half_d = plan.depth * (g.row_gap() if g else ROW_SPACING) / 2
            cx, cy = plan.center
            label = self.small.render(f"{plan.width} breit, {plan.depth} tief", True, config.COLOR_RECT)
            spots = [(-fx * (half_d + 0.35), -fy * (half_d + 0.35)),          # hinten
                     (fy * (half_w + 0.3), -fx * (half_w + 0.3)),             # links
                     (-fy * (half_w + 0.3), fx * (half_w + 0.3)),             # rechts
                     (fx * (half_d + 0.75), fy * (half_d + 0.75))]            # vorn
            for dx, dy in spots:
                rect = label.get_rect(center=px((cx + dx, cy + dy)))
                if abs(dx * fy - dy * fx) > 1e-6:          # daneben: Schrift beginnt am Block statt mittig
                    rect = label.get_rect(midleft=rect.center) if rect.centerx > px((cx, cy))[0] else \
                        label.get_rect(midright=rect.center)
                if rect.collidelist(taken) < 0:
                    s.blit(label, rect)
                    taken.append(rect)
                    break

    def _draw_ground(self, battle: Battle) -> None:
        s = self.surface
        x0, y0 = px((0, 0))
        x1, y1 = px((battle.cols, battle.rows))
        pygame.draw.rect(s, config.COLOR_GROUND, pygame.Rect(x0, y0, x1 - x0, y1 - y0))
        for c in range(battle.cols + 1):
            x = px((c, 0))[0]
            if 0 <= x <= config.MAP_W:
                pygame.draw.line(s, config.COLOR_GRID, (x, max(0, y0)), (x, min(config.MAP_H, y1)))
        for r in range(battle.rows + 1):
            y = px((0, r))[1]
            if 0 <= y <= config.MAP_H:
                pygame.draw.line(s, config.COLOR_GRID, (max(0, x0), y), (min(config.MAP_W, x1), y))
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
        t = int(round(T))
        post = 3 if t >= 24 else 2
        for cx, cy in battle.blocked:
            x, y = px((cx, cy))
            # geschlossener Wall: jede Kachel voll, Pfähle als dunkle Striche, so wirkt er durchgehend
            pygame.draw.rect(s, config.COLOR_PALISADE, pygame.Rect(x, y, t + 1, t + 1))
            for i in range(2):
                xi = x + t // 4 + i * t // 2
                pygame.draw.line(s, (90, 60, 30), (xi, y + t // 6), (xi, y + t - t // 6), max(1, post - 1))
        for cx, cy in set(battle.ladders) | set(battle.crossings):
            x, y = px((cx, cy))
            rails = (x + 3 * t // 10, x + t - 3 * t // 10)
            for rx in rails:
                pygame.draw.line(s, config.COLOR_CROSSING, (rx, y + t // 15), (rx, y + t - t // 15), 2)
            for i in range(4):
                yi = y + t // 6 + i * 7 * t // 30
                pygame.draw.line(s, config.COLOR_CROSSING, (rails[0], yi), (rails[1], yi), 2)
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
        if battle.ring:
            for g in battle.gates:
                xs = [c[0] for c in g.cells]
                ys = [c[1] for c in g.cells]
                a, b = px((min(xs), min(ys))), px((max(xs) + 1, max(ys) + 1))
                rect = pygame.Rect(a[0] + 2, a[1] + 2, b[0] - a[0] - 4, b[1] - a[1] - 4)
                if g.closed:
                    pygame.draw.rect(s, config.COLOR_GATE_CLOSED, rect, border_radius=3)
                    frac = g.hp / g.hp_max
                    pygame.draw.rect(s, config.COLOR_FIRE, pygame.Rect(rect.x, rect.bottom + 2, int(rect.w * frac), 3))
                else:
                    pygame.draw.rect(s, config.COLOR_GATE, rect, 2)
            for tw in battle.corner_towers:
                x, y = px(tw.center)
                r = max(5, int(T * 0.55))
                color = {Side.STADT: config.COLOR_CITY, Side.FEIND: config.COLOR_ENEMY}.get(tw.owner, config.COLOR_TEXT_DIM)
                pygame.draw.circle(s, config.COLOR_TOWER, (x, y), r)
                pygame.draw.circle(s, (90, 60, 30), (x, y), r, 2)
                pygame.draw.circle(s, color, (x, y), max(2, r // 3))

    def _draw_houses(self, battle: Battle) -> None:
        s = self.surface
        t = int(round(T))
        for h in battle.houses:
            x, y = px((h.cx, h.cy))
            rect = pygame.Rect(x + t // 10, y + t // 10, t - t // 5, t - t // 5)
            pygame.draw.rect(s, config.COLOR_HOUSE_LOOTED if h.looted else config.COLOR_HOUSE, rect, border_radius=3)
            roof = [(x + t // 15, y + t // 3), (x + t // 2, y), (x + t - t // 15, y + t // 3)]
            pygame.draw.polygon(s, (60, 30, 30) if h.looted else (150, 90, 50), roof)
            if h.looted:
                cx, cy = x + t // 2, y + t // 2
                k = max(3, t // 5)
                pygame.draw.polygon(s, config.COLOR_FIRE, [(cx - k, cy + k + 2), (cx, cy - k - 2), (cx + k, cy + k + 2)])
            elif h.progress > 0:
                frac = min(1.0, h.progress / config.LOOT_TIME)
                pygame.draw.rect(s, config.COLOR_FIRE, pygame.Rect(x + t // 10, y + t - t // 5, int((t - t // 5) * frac), 3))

    def _draw_face(self, man, mx: int, my: int, r: int) -> None:
        """Ein kurzer dunkler Strich von der Mitte zum vorderen Rand: wo der Mann hinschaut
        (nur hineingezoomt, wenn die Männer groß genug sind)."""
        if r < 3:
            return
        ex, ey = mx + man.sfx * (r + 1), my + man.sfy * (r + 1)
        pygame.draw.line(self.surface, config.COLOR_FACE, (mx, my), (int(round(ex)), int(round(ey))), 2 if r >= 5 else 1)

    def _draw_horse(self, man, mx: int, my: int, r: int) -> None:
        """Das Pferd unter dem Reiter: ein braunes Oval in seiner Laufrichtung, vorn ein Kopf.
        Der Reiter darüber schaut, wohin er will; das Pferd läuft, wohin es wirklich geht."""
        hx, hy = man.hx, man.hy
        half_l, half_w = 1.05 * r, 0.6 * r
        pts = []
        for k in range(12):
            a = 2 * math.pi * k / 12
            ca, sa = math.cos(a) * half_l, math.sin(a) * half_w
            pts.append((int(round(mx + hx * ca - hy * sa)), int(round(my + hy * ca + hx * sa))))
        pygame.draw.polygon(self.surface, config.COLOR_HORSE, pts)
        head = max(1, int(round(0.45 * r)))
        pygame.draw.circle(self.surface, config.COLOR_HORSE_HEAD,
                           (int(round(mx + hx * (half_l + 0.2 * r))), int(round(my + hy * (half_l + 0.2 * r)))), head)

    def _draw_lochos(self, u: Lochos, selected: bool, frames: bool = True) -> None:
        """Eine Gruppe: ihre Männer, und nur mit ``frames`` (Pause, Aufziehen) ihr
        Formationsrechteck; sonst zeigt ein Ring um jeden Mann, dass sie gewählt ist."""
        s = self.surface
        cx, cy = px(u.pos)
        if u.side is Side.STADT:
            ring = config.COLOR_CITY_DIM if u.stance is Stance.FLUCHT else config.COLOR_CITY
        else:
            ring = config.COLOR_ENEMY_DIM if u.stance is Stance.FLUCHT else config.COLOR_ENEMY
        corners = [px(c) for c in u.corners()]
        fx, fy = u.facing
        if u.loose or not frames:
            # aufgelöst, oder Rechtecke ausgeblendet: nur die Männer (Auswahl als Ringe)
            if selected:
                for man in u.all_men():
                    pygame.draw.circle(s, config.COLOR_SELECT, shown(man), 6, 1)
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
        r_man = max(2, int(round(T * 0.1)))              # in der Übersicht kleiner, hineingezoomt größer
        chief = u.commander_man() if not u.loose else None
        for row in u.rows:
            for man in row:
                color = man.kind.color
                if u.side is Side.FEIND:
                    color = desaturate(color, config.ENEMY_DESATURATION)
                if man.wounded:
                    color = tuple(c // 2 for c in color)
                if u.stance is Stance.FLUCHT:
                    color = tuple(c * 2 // 3 for c in color)
                if man.flash > 0.0:                      # eben getroffen: blitzt hell auf
                    color = config.COLOR_HIT
                mx, my = shown(man)
                if man.kind.cavalry and man.mounted:
                    self._draw_horse(man, mx, my, r_man)
                if man.leader:                           # der Anführer: größer, goldener Ring
                    pygame.draw.circle(s, color, (mx, my), r_man + 1)
                    pygame.draw.circle(s, config.COLOR_LEADER, (mx, my), r_man + 2, 2)
                    self._draw_face(man, mx, my, r_man + 1)
                    continue
                pygame.draw.circle(s, color, (mx, my), r_man)
                self._draw_face(man, mx, my, r_man)
                if man is chief:                         # der Hauptmann: weißer Ring, Richtpunkt der Gruppe
                    pygame.draw.circle(s, config.COLOR_COMMANDER, (mx, my), r_man + 1, 1)
                if man.bound:
                    pygame.draw.circle(s, config.COLOR_BOUND, (mx, my), r_man + 1, 1)
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
        elif battle.scenario.camp:
            text += f"Hütten {r['haeuser_intakt']}/{r['haeuser']}   "
        if battle.ring:
            shut = sum(1 for g in battle.gates if g.closed)
            text += f"Tore {shut}/{len(battle.gates)} zu   "
        text += f"{mins}:{secs:02d}"
        strip = pygame.Surface((config.MAP_W, 26), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 120))
        s.blit(strip, (0, 0))
        room = config.MAP_W - 78 - 84                      # zwischen Menü und Pause
        font = self.font
        if font.size(text)[0] > room:
            text = text.replace("   ", "  ")
            font = self.font if font.size(text)[0] <= room else self.small
        s.blit(font.render(text, True, config.COLOR_TEXT), (78, 9 if font is self.font else 11))
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
        if (self.camera.big or self.camera.zoomed_in) and not menu_open:
            label = "Nah" if self.camera.overview else "Karte"
            out.append(Button("ansicht", label, pygame.Rect(gap, TOP_BTN_Y + TOP_BTN_H + gap, 64, TOP_BTN_H),
                              active=not self.camera.overview))
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
    def chip_order(battle: Battle) -> list[tuple[str, object]]:
        """Reihenfolge der Kacheln: die Gruppen eines Verbands zusammen, vorn nach hinten
        und links nach rechts, mit einer Kopfzeile davor; die anderen einzeln."""
        out: list[tuple[str, object]] = []
        done: set[int] = set()
        for u in battle.units(Side.STADT):
            if u.id in done:
                continue
            v = battle.verband_of(u)
            if v is None:
                out.append(("group", u))
                done.add(u.id)
                continue
            out.append(("verband", v))
            for row in battle.verband_units(v, fighting=False):
                for g in row:
                    out.append(("group", g))
                    done.add(g.id)
        return out

    @staticmethod
    def _chips(battle: Battle, selected: set[int]) -> list[Button]:
        """Eine Kachel je eigene Gruppe, untereinander am rechten Kartenrand,
        oben „Alle“; sie wählen aus und zeigen Gattung, Mannzahl und Moral. Die
        Gruppen eines Verbands stehen beisammen, ein Rahmen mit Kopfzeile umschließt
        sie; die Kopfzeile wählt den ganzen Verband."""
        groups = battle.units(Side.STADT)
        if not groups:
            return []
        x = config.MAP_W - CHIP - 6
        out = [Button("alle", "Keine" if selected else "Alle", pygame.Rect(x, CHIP_TOP, CHIP, CHIP), active=bool(selected))]
        y = CHIP_TOP + CHIP + CHIP_GAP
        chosen = battle.selected_verband(selected)
        for kind, item in Renderer.chip_order(battle):
            h = VERBAND_HEAD if kind == "verband" else CHIP
            if y + h > config.MAP_H - 44:
                break                                     # mehr passt nicht neben die Karte
            if kind == "verband":
                y += 2
                out.append(Button(f"verband:{item.id}", f"V{item.id}", pygame.Rect(x, y, CHIP, VERBAND_HEAD),
                                  active=chosen is item))
                y += VERBAND_HEAD + 2
                continue
            out.append(Button(f"group:{item.id}", str(item.men), pygame.Rect(x, y, CHIP, CHIP), active=item.id in selected))
            y += CHIP + CHIP_GAP
        return out

    def _command_row(self, battle: Battle, sel: list[Lochos], y: int, h: int) -> list[Button]:
        """Befehle je Waffengattung der Auswahl; gemischte Auswahl nur das Gemeinsame."""
        W, gap = config.WIDTH, 6
        arms = {u.arm() for u in sel}
        arm = next(iter(arms)) if len(arms) == 1 else "gemischt"
        mixed = any(battle.mixed(u) for u in sel)                 # gemischte Gruppe: teilt sich beim Angriff
        storming = all(u.stance is Stance.ANGRIFF and u.target_id is None for u in sel)
        items: list[tuple[str, str, float, bool, str | None]] = []          # key, label, Gewicht, aktiv, Unterzeile
        verband = battle.selected_verband({u.id for u in sel})
        if verband is not None:
            # der ganze Verband: Angriff und Halten je Gattung, seine Form, Anordnung, Auflösen
            items = [("angriff", "Angriff", 1.2, False, "je Gattung"), ("halten", "Halten", 1.1, False, None),
                     ("vformation:linie", "Linie", 0.9, verband.formation == "linie", None),
                     ("vformation:o", "Kreis", 0.9, verband.formation == "o", None),
                     ("anordnen", "Anordnen", 1.3, self.arranging == verband.id, None),
                     ("aufloesen", "Auflösen", 1.2, False, "Verband")]
            return self._lay_out(items, y, h)
        if arm == "hopliten" and not mixed:
            # die Modi: locker oder Phalanx, dazu der Sturm
            for name in config.DRILLS:
                items.append((f"drill:{name}", config.DRILL_NAMES[name], 1.0,
                              not storming and all(u.drill == name for u in sel), None))
            items.append(("angriff", ATTACK_LABEL["hopliten"], 1.0, storming, None))
        else:
            items.append(("angriff", "Angriff" if mixed else ATTACK_LABEL.get(arm, "Angriff"), 1.6, False,
                          "je Gattung" if mixed else None))
            items.append(("halten", "Halten", 1.6, False, None))
            if arm == "reiter" and not mixed:
                items.append(("jagen", "Jagen", 1.2, all(u.mode == "jagen" for u in sel), "Fliehende"))
        if len(sel) >= 2:
            items.append(("verband", "Verband", 1.3, False, "bilden"))
        elif battle.verband_of(sel[0]) is not None:
            items.append(("verlassen", "Aus", 1.0, False, "Verband"))
        if len(sel) == 1 and battle.can_split(sel[0]):
            items.append(("teilen", "Teilen", 1.0, False, None))
        elif len(sel) >= 2 and battle.can_merge(sel):
            items.append(("vereinen", "Vereinen", 1.2, False, None))
        engines = battle.scenario.ram_available
        if arm != "gemischt":
            opts = sel[0].formation_options()
            if len(opts) > 1 and len(items) + len(opts) + (2 if engines else 0) > 7:
                # wenig Platz: ein Knopf, der die Formation weiterschaltet
                now = sel[0].formation
                items.append(("formation", FORMATION_NAMES[now], 1.0, False, "wechseln"))
            elif len(opts) > 1:
                for name in opts:
                    items.append((f"formation:{name}", FORMATION_NAMES[name].replace("-Stellung", ""), 0.9,
                                  all(u.formation == name for u in sel), None))
        if engines:
            gate_open = all(not g.closed for g in battle.gates)     # alle Tore offen: kein Rammbock mehr
            for key, kind, name in (("rammbock", "ram", "Rammbock"), ("turm", "tower", "Turm")):
                carrying = any(u.engine == kind for u in sel)
                building = any(u.build_kind == kind for u in sel)
                if kind == "ram" and gate_open and not carrying and not building:
                    continue                                              # das Tor ist schon offen
                sub = "ablegen" if carrying else ("abbrechen" if building else "bauen")
                items.append((key, name, 1.4, carrying or building, sub))
        return self._lay_out(items, y, h)

    @staticmethod
    def _lay_out(items: list, y: int, h: int) -> list[Button]:
        W, gap = config.WIDTH, 6
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
            drill = u.drill_kind()
            if drill == "locker":
                return "locker"
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
        self._selected = selected
        (y2, h2), = self._bar_rows()
        by_id = {u.id: u for u in battle.lochoi}
        self._draw_verband_frames(battle)
        for b in self.buttons:
            if b.key.startswith("group:"):
                self._draw_chip(b, by_id[int(b.key.split(":")[1])])
                continue
            if b.key.startswith("verband:"):
                pygame.draw.rect(s, config.COLOR_SHIELD if b.active else config.COLOR_BUTTON, b.rect, border_radius=4)
                img = self.small.render(b.label, True, config.COLOR_BAR if b.active else config.COLOR_TEXT)
                s.blit(img, img.get_rect(center=b.rect.center))
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
                hint = "Gruppe wählen: Kachel antippen, lange drücken wählt dazu"
            img = self.small.render(hint, True, config.COLOR_TEXT_DIM)
            s.blit(img, img.get_rect(center=(config.WIDTH // 2, y2 + h2 // 2)))

    # ------------------------------------------------ Anordnung eines Verbands
    def arrange_layout(self, battle: Battle, vid: int) -> dict | None:
        """Die Tafel zum Anordnen: je Reihe des Verbands eine Zeile (oben vorn), darin die
        Sinnbilder der Gruppen von links nach rechts; darunter eine leere Zeile für eine neue
        Reihe hinten; oben rechts „Fertig“."""
        v = next((x for x in battle.verbaende if x.id == vid), None)
        if v is None:
            return None
        rows = [[u.id for u in row] for row in battle.verband_units(v, fighting=False)]
        icon, row_h, head = 40, 48, 26
        x0, w = 8, config.MAP_W - CHIP - 26
        h = head + (len(rows) + 1) * row_h + 8
        y0 = config.MAP_H - 8 - h
        panel = pygame.Rect(x0, y0, w, h)
        out_rows = []
        for i, row in enumerate(rows + [[]]):
            rect = pygame.Rect(x0 + 6, y0 + head + i * row_h, w - 12, row_h - 4)
            total = len(row) * icon + max(0, len(row) - 1) * 8
            x = rect.centerx - total // 2
            icons = []
            for gid in row:
                icons.append((gid, pygame.Rect(x, rect.y + (rect.h - icon) // 2, icon, icon)))
                x += icon + 8
            out_rows.append((rect, icons))
        return {"panel": panel, "rows": out_rows[:-1], "new_row": out_rows[-1][0],
                "done": pygame.Rect(panel.right - 76, y0 + 3, 70, 20), "ids": rows}

    @staticmethod
    def drop_rows(layout: dict, gid: int, pos: tuple[int, int]) -> list[list[int]]:
        """Neue Anordnung, wenn die Gruppe ``gid`` bei ``pos`` abgelegt wird: in die Zeile
        unter dem Finger, zwischen die Nachbarn links und rechts; unter der letzten Zeile
        wird sie eine neue Reihe hinten."""
        rows = [[x for x in row if x != gid] for row in layout["ids"]]
        target = None
        for i, (rect, _) in enumerate(layout["rows"]):
            if rect.top - 2 <= pos[1] < rect.bottom + 2:
                target = i
                break
        if target is None:
            if pos[1] >= layout["new_row"].top - 2:
                rows.append([gid])
            elif pos[1] < layout["rows"][0][0].top:
                rows.insert(0, [gid])
            else:
                return layout["ids"]
            return [r for r in rows if r]
        centres = {g: r.centerx for _, icons in layout["rows"] for g, r in icons}
        row = rows[target]
        k = sum(1 for g in row if centres.get(g, 0) < pos[0])
        row.insert(k, gid)
        return [r for r in rows if r]

    def _draw_arrange(self, battle: Battle, vid: int, drag) -> None:
        layout = self.arrange_layout(battle, vid)
        if layout is None:
            return
        s = self.surface
        by_id = {u.id: u for u in battle.lochoi}
        pygame.draw.rect(s, config.COLOR_BAR, layout["panel"], border_radius=8)
        pygame.draw.rect(s, config.COLOR_SHIELD, layout["panel"], 2, border_radius=8)
        title = self.small.render("Anordnung: oben ist vorn", True, config.COLOR_TEXT)
        s.blit(title, (layout["panel"].x + 8, layout["panel"].y + 6))
        done = layout["done"]
        pygame.draw.rect(s, config.COLOR_BUTTON_ACTIVE, done, border_radius=5)
        img = self.small.render("Fertig", True, config.COLOR_TEXT)
        s.blit(img, img.get_rect(center=done.center))
        for i, (rect, icons) in enumerate(layout["rows"]):
            pygame.draw.rect(s, config.COLOR_BUTTON, rect, 1, border_radius=5)
            img = self.small.render("vorn" if i == 0 else f"{i + 1}.", True, config.COLOR_TEXT_DIM)
            s.blit(img, (rect.x + 4, rect.y + 3))
            for gid, r in icons:
                if drag is not None and drag[0] == gid:
                    continue
                u = by_id.get(gid)
                if u is not None:
                    self._draw_chip(Button(f"group:{gid}", str(u.men), r), u)
        rect = layout["new_row"]
        pygame.draw.rect(s, config.COLOR_BUTTON, rect, 1, border_radius=5)
        img = self.small.render("hierher ziehen: neue Reihe hinten", True, config.COLOR_TEXT_DIM)
        s.blit(img, img.get_rect(center=rect.center))
        if drag is not None and drag[0] in by_id:
            r = pygame.Rect(0, 0, 40, 40)
            r.center = drag[1]
            self._draw_chip(Button(f"group:{drag[0]}", str(by_id[drag[0]].men), r, active=True), by_id[drag[0]])

    def _draw_verband_frames(self, battle: Battle) -> None:
        """Ein Rahmen um die Kopfzeile und die Kacheln jedes Verbands."""
        rects: dict[int, pygame.Rect] = {}
        current = None
        for b in self.buttons:
            if b.key.startswith("verband:"):
                current = int(b.key.split(":")[1])
                rects[current] = b.rect.copy()
            elif b.key.startswith("group:") and current is not None:
                v = battle.verband_of(int(b.key.split(":")[1]))
                if v is not None and v.id == current:
                    rects[current].union_ip(b.rect)
                else:
                    current = None
        chosen = battle.selected_verband(self._selected)
        for vid, r in rects.items():
            color = config.COLOR_SHIELD if chosen is not None and chosen.id == vid else config.COLOR_RECT
            pygame.draw.rect(self.surface, color, r.inflate(6, 6), 2, border_radius=7)

    def _arm_symbol(self, arm: str, color, cx: int, cy: int) -> None:
        """Sinnbild der Gattung: Pferdekopf, Wurfspeer oder Rundschild."""
        s = self.surface
        if arm == "reiter":                               # Pferdekopf
            pygame.draw.polygon(s, color, [(cx - 6, cy + 6), (cx + 6, cy + 6), (cx + 2, cy - 6), (cx - 2, cy - 3)])
        elif arm == "peltasten":                          # Wurfspeer
            pygame.draw.line(s, color, (cx - 6, cy + 6), (cx + 5, cy - 5), 2)
            pygame.draw.polygon(s, color, [(cx + 6, cy - 6), (cx + 1, cy - 5), (cx + 5, cy - 1)])
        else:                                             # Rundschild
            pygame.draw.circle(s, color, (cx, cy), 7)
            pygame.draw.circle(s, config.COLOR_BAR, (cx, cy), 7, 1)
            pygame.draw.circle(s, config.COLOR_BAR, (cx, cy), 2)

    def _leader_badge(self, rect: pygame.Rect) -> None:
        pygame.draw.circle(self.surface, config.COLOR_LEADER, (rect.right - 8, rect.y + 8), 4)
        pygame.draw.circle(self.surface, config.COLOR_BAR, (rect.right - 8, rect.y + 8), 4, 1)

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
        self._arm_symbol(u.arm(), color, b.rect.x + 11, b.rect.y + 11)   # Sinnbild oben links
        if u.leader_man() is not None:                    # Abzeichen: der Anführer kämpft hier mit
            self._leader_badge(b.rect)
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

        # oben: Verteidigung oder Angriff
        half = (W - 3 * gap) // 2
        for k, (side, label) in enumerate((("verteidigung", "Verteidigung"), ("angriff", "Angriff"))):
            on = scenario.side == side
            self._menu_button(f"role:{side}", label, pygame.Rect(gap + k * (half + gap), 6, half, 34),
                              config.COLOR_BUTTON_ACTIVE if on else None)
        # Vorrat: ein gemeinsamer Topf für alle Gattungen (im Räuberlager nur leichte Hopliten und Peltasten)
        kinds = scenario.own_kinds or PLAYER_TYPES
        y, x = 48, 8
        for key in kinds:
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
            (-2, own_label, own_count, scenario.own_min or OWN_MIN, scenario.own_max or OWN_MAX, config.COLOR_CITY),
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

        # Schauplatz: Offene Siedlung, Räuberhorde, Festung
        y += 2
        third = (W - (len(PLACES) + 1) * gap) // len(PLACES)
        for k, (where, label) in enumerate(PLACES):
            on = scenario.where == where
            self._menu_button(f"place:{where}", label, pygame.Rect(gap + k * (third + gap), y, third, 32),
                              config.COLOR_BUTTON_ACTIVE if on else None)
        y += 36

        # Gruppenwahl: eine Kachel je Gruppe (Sinnbild und Mannzahl), antippen wählt
        n = len(army.groups)
        tile_w = min(80, (W - 2 * gap - (n - 1) * gap) // max(1, n))
        x0 = (W - (n * tile_w + (n - 1) * gap)) // 2
        for k, grp in enumerate(army.groups):
            rect = pygame.Rect(x0 + k * (tile_w + gap), y, tile_w, 40)
            pygame.draw.rect(s, config.COLOR_BUTTON_ACTIVE if k == index else config.COLOR_BUTTON, rect, border_radius=6)
            tiers = [t for t in grp.tiers if t.count > 0] or grp.tiers
            arms: dict[str, int] = {}
            for t in tiers:
                arms[arm_of(t.kind)] = arms.get(arm_of(t.kind), 0) + t.count
            arm = max(arms, key=arms.get) if arms else "hopliten"
            color = UNIT_TYPES[tiers[0].kind].color if tiers else config.COLOR_CITY
            self._arm_symbol(arm, color, rect.x + 11, rect.y + 11)
            if grp.leader:
                self._leader_badge(rect)
            img = self.font.render(str(grp.men()), True, config.COLOR_TEXT)
            s.blit(img, img.get_rect(bottomright=(rect.right - 4, rect.bottom - 4)))
            self.menu_buttons.append(Button(f"groupsel:{k}", grp.name, rect))
        g = army.groups[index]

        # Reihen-Blöcke, vorn nach hinten
        y += 46
        block_h = 58
        for i, tier in enumerate(g.tiers):
            kind = UNIT_TYPES[tier.kind]
            panel = pygame.Rect(gap, y, W - 2 * gap, block_h)
            pygame.draw.rect(s, config.COLOR_MENU_PANEL, panel, border_radius=6)
            label = "Vorn" if i == 0 else ("Hinten" if i == len(g.tiers) - 1 else f"Reihe {i + 1}")
            s.blit(self.small.render(label, True, config.COLOR_TEXT_DIM), (gap + 8, y + 6))
            # Typwahl: fünf Farbpunkte
            for k, key in enumerate(kinds):
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
        font = self.font if len(label) < 18 and self.font.size(label)[0] <= rect.w - 8 else self.small
        img = font.render(label, True, config.COLOR_TEXT)
        s.blit(img, img.get_rect(center=rect.center))
        self.menu_buttons.append(Button(key, label, rect, color))

    def menu_button_at(self, pos: tuple[int, int]) -> str | None:
        for b in self.menu_buttons:
            if b.rect.collidepoint(pos):
                return b.key
        return None
