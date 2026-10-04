"""Hauptschleife, Eingabe und Bildschirmzustand (Aufstellung / Schlacht).

Asynchron, damit dieselbe Schleife nativ und im Browser (pygbag) läuft.
Ein Finger kommt als Mausereignis an; liegen zwei Finger auf, verschieben sie
die Ansicht einer großen Karte (am Rechner: rechte Maustaste, Pfeiltasten).
"""

from __future__ import annotations

import asyncio
import copy
import math
import random

import pygame

from . import config
from .ai import Memory
from .army import OWN_DEFAULT, OWN_MAX, OWN_MIN, Army, default_army, scaled_army
from .battle import Battle
from .render import Renderer
from .scenarios import SCENARIOS
from .units import Side

DRAG_MIN = 0.4  # Kacheln: kürzer ist ein Tipp, kein Bereich
LONG_PRESS = 0.45  # Sekunden: so lange auf einer Gruppenkachel, und sie kommt zur Auswahl dazu
TRI_TAP_TIME = 0.5  # Sekunden: so kurz liegen drei Finger auf, und die Pause schaltet um
TRI_TAP_SLOP = 0.04  # Anteil der Bildschirmbreite: so weit darf ein Finger dabei rutschen


def to_tiles(pos: tuple[int, int]) -> tuple[float, float]:
    return (pos[0] / config.TILE, pos[1] / config.TILE)


class App:
    """Zustand der Bedienung, getrennt von der Schleife (testbar)."""

    def __init__(self, renderer: Renderer, seed: int | None = None, start_in_battle: bool = False,
                 memory: Memory | None = None) -> None:
        self.renderer = renderer
        self.memory = memory or Memory()
        self.seed = seed
        self.scenario_index = 0
        self.army: Army = default_army()
        self.template: Army = copy.deepcopy(self.army)   # Mischung, aus der die Stärke skaliert wird
        self.menu_group = 0
        self.screen = "schlacht" if start_in_battle else "aufstellung"
        self.paused = False
        self.menu_open = False             # Neu und Aufstellung liegen hinter „Menü“
        self.selected: set[int] = set()
        self.drag_start: tuple[float, float] | None = None
        self.drag_now: tuple[float, float] | None = None
        self.running = True
        self.menu_slider: tuple[int, pygame.Rect] | None = None
        self.enemy_counts: dict[str, int] = {s.key: s.enemy_default for s in SCENARIOS}
        self.own_count = OWN_DEFAULT
        self.fingers: dict[int, tuple[float, float]] = {}   # aufliegende Finger (für das Verschieben)
        self.panning = False                                 # zwei Finger liegen auf: kein Tippen, kein Ziehen
        self.pinch_from: tuple | None = None                 # (Abstand, Mitte) der zwei Finger beim letzten Schritt
        self.tri_tap: tuple | None = None                    # (seit wann, Startpunkte) dreier Finger: Tippen schaltet die Pause
        self.pan_from: tuple[int, int] | None = None         # rechte Maustaste: verschieben am Rechner
        self.clock = 0.0                                     # Echtzeit seit dem Start (für langes Drücken)
        self.chip_press: list | None = None                  # [Taste, seit wann, schon erledigt] auf einer Gruppenkachel
        self.arranging: int | None = None                    # Verband, dessen Anordnung gerade bearbeitet wird
        self.arrange_drag: tuple | None = None               # (Gruppe, Fingerposition) beim Anordnen
        self.battle = self._new_battle()

    def _new_battle(self) -> Battle:
        rng = random.Random(self.seed) if self.seed is not None else random.Random()
        self.paused = False
        self.menu_open = False
        self.selected = set()
        self.drag_start = self.drag_now = None
        self._arrange(None)
        scn = SCENARIOS[self.scenario_index]
        army = copy.deepcopy(self.army) if self.army.total_men() else scaled_army(default_army(), self.own_count)
        return Battle(scn, rng, army=army, enemy_count=self.enemy_counts[scn.key], memory=self.memory)

    # ---------------------------------------------------------- Eingabe
    def to_tiles(self, pos: tuple[int, int]) -> tuple[float, float]:
        return self.renderer.camera.to_tiles(pos)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            self._finger(event)
        elif event.type == pygame.KEYDOWN:
            self._key(event.key)
        elif event.type == pygame.MOUSEWHEEL and self.screen == "schlacht":
            self.renderer.camera.zoom_at(1.15 ** event.y, pygame.mouse.get_pos())   # Mausrad: zoomen
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.pan_from = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self.pan_from = None
        elif event.type == pygame.MOUSEMOTION and self.pan_from is not None:
            self.renderer.camera.pan(event.pos[0] - self.pan_from[0], event.pos[1] - self.pan_from[1])
            self.pan_from = event.pos
        elif self.panning:
            if event.type == pygame.MOUSEBUTTONUP:
                self.drag_start = self.drag_now = None    # der Finger war Teil des Verschiebens
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._press(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.menu_slider is not None:
            self._slide(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.arrange_drag is not None:
            self.arrange_drag = (self.arrange_drag[0], event.pos)
            self.renderer.arrange_drag = self.arrange_drag
        elif event.type == pygame.MOUSEMOTION and self.drag_start is not None:
            self.drag_now = self.to_tiles(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._release(event.pos)

    def _pinch(self) -> tuple[float, tuple[float, float]] | None:
        """Abstand der ersten beiden Finger und ihre Mitte, in Bildpunkten."""
        if len(self.fingers) < 2:
            return None
        (x1, y1), (x2, y2) = list(self.fingers.values())[:2]
        a = (x1 * config.WIDTH, y1 * config.HEIGHT)
        b = (x2 * config.WIDTH, y2 * config.HEIGHT)
        return math.hypot(a[0] - b[0], a[1] - b[1]), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)

    def _finger(self, event: pygame.event.Event) -> None:
        """Zwei Finger verschieben die Karte und zoomen (auseinander ziehen = näher); was der
        erste Finger angefangen hat (Tipp, Front aufziehen), fällt dann weg."""
        if event.type == pygame.FINGERDOWN:
            self.fingers[event.finger_id] = (event.x, event.y)
            if len(self.fingers) >= 2 and self.screen == "schlacht":
                self.panning = True
                self.drag_start = self.drag_now = None
                self.pinch_from = self._pinch()
            if len(self.fingers) == 3 and self.screen == "schlacht":
                self.tri_tap = (self.clock, dict(self.fingers))   # drei Finger: vielleicht ein Tipp auf die Pause
            elif len(self.fingers) > 3:
                self.tri_tap = None
        elif event.type == pygame.FINGERMOTION:
            if event.finger_id in self.fingers:
                self.fingers[event.finger_id] = (event.x, event.y)
            if self.tri_tap is not None:
                start = self.tri_tap[1].get(event.finger_id)
                if start is not None and math.hypot(event.x - start[0], event.y - start[1]) > TRI_TAP_SLOP:
                    self.tri_tap = None                      # gewischt, nicht getippt
            now = self._pinch()
            if len(self.fingers) >= 3:
                self.pinch_from = now                        # drei Finger: weder zoomen noch verschieben
            elif self.panning and now is not None and self.pinch_from is not None:
                cam = self.renderer.camera
                (d0, m0), (d1, m1) = self.pinch_from, now
                if d0 > 1.0 and d1 > 1.0:
                    cam.zoom_at(d1 / d0, m1)                 # auseinander: näher, zusammen: weiter weg
                cam.pan(m1[0] - m0[0], m1[1] - m0[1])        # die Karte folgt der Mitte der Finger
                self.pinch_from = now
        else:
            self.fingers.pop(event.finger_id, None)
            self.pinch_from = self._pinch()
            if not self.fingers:
                self.panning = False
                if self.tri_tap is not None and self.clock - self.tri_tap[0] <= TRI_TAP_TIME:
                    self.command("pause")                    # kurz mit drei Fingern getippt: Pause an oder aus
                self.tri_tap = None

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
        elif key == pygame.K_l:
            self.command("drill:locker")
        elif key == pygame.K_p:
            self.command("drill:phalanx")
        elif key == pygame.K_j:
            self.command("jagen")
        elif key == pygame.K_d:
            self.command("teilen")
        elif key == pygame.K_e:
            self.command("vereinen")
        elif key == pygame.K_SPACE:
            self.command("pause")
        elif key == pygame.K_r:
            self.command("neu")
        elif key == pygame.K_m:
            self.command("aufstellung")
        elif key == pygame.K_b:
            self.command("rammbock")
        elif key == pygame.K_t:
            self.command("turm")
        elif key == pygame.K_f:
            self.command("formation")
        elif key == pygame.K_v:
            self.command("verband")
        elif key == pygame.K_z:
            self.command("ansicht")
        elif key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
            step = 3 * config.TILE
            dx = {pygame.K_LEFT: step, pygame.K_RIGHT: -step}.get(key, 0)
            dy = {pygame.K_UP: step, pygame.K_DOWN: -step}.get(key, 0)
            self.renderer.camera.pan(dx, dy)

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
        if self.arranging is not None and self._arrange_press(pos):
            return
        key = self.renderer.button_at(pos, self.battle, self.paused, self.selected, self.menu_open)
        if key and key.startswith("group:"):
            self.chip_press = [key, self.clock, False]   # Tipp wählt beim Loslassen, langes Drücken wählt dazu
            return
        if key:
            self.command(key)                      # Leiste unten, Menü und Pause oben, Gruppenkacheln rechts
            return
        if self.menu_open:
            self.menu_open = False                 # Tipp daneben schließt das Menü
            return
        if pos[1] >= config.MAP_H:
            return
        self.drag_start = self.drag_now = self.to_tiles(pos)

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
            self.army = scaled_army(self.template, self.own_count)   # die Blöcke skalieren mit
            return
        if tier >= len(self.army.groups[self.menu_group].tiers):
            self.menu_slider = None
            return
        maximum = self.army.max_for(self.menu_group, tier)
        self.army.set_count(self.menu_group, tier, round(frac * maximum))
        self._remember()

    def _remember(self) -> None:
        """Die bearbeitete Mischung wird zur Vorlage für das Skalieren."""
        self.template = copy.deepcopy(self.army)

    def _arrange(self, vid: int | None) -> None:
        self.arranging = vid
        self.arrange_drag = None
        self.renderer.arranging = vid
        self.renderer.arrange_drag = None

    def _arrange_press(self, pos: tuple[int, int]) -> bool:
        """Fingerdruck, solange die Tafel zum Anordnen offen ist: „Fertig“ schließt sie, ein
        Sinnbild wird verschoben. Ein Druck außerhalb schließt sie (und gilt dann normal)."""
        layout = self.renderer.arrange_layout(self.battle, self.arranging)
        if layout is None:
            self._arrange(None)
            return False
        if layout["done"].collidepoint(pos):
            self._arrange(None)
            return True
        for _, icons in layout["rows"]:
            for gid, r in icons:
                if r.collidepoint(pos):
                    self.arrange_drag = (gid, pos)
                    self.renderer.arrange_drag = self.arrange_drag
                    return True
        if layout["panel"].collidepoint(pos):
            return True
        key = self.renderer.button_at(pos, self.battle, self.paused, self.selected, self.menu_open)
        if key != "anordnen":
            self._arrange(None)
        return False

    def _release(self, pos: tuple[int, int]) -> None:
        self.menu_slider = None
        if self.chip_press is not None:
            key, _, done = self.chip_press
            self.chip_press = None
            if not done:
                self.command(key)                  # kurzer Tipp: nur diese Gruppe
            return
        if self.arrange_drag is not None:
            gid = self.arrange_drag[0]
            self.arrange_drag = None
            self.renderer.arrange_drag = None
            v = next((x for x in self.battle.verbaende if x.id == self.arranging), None)
            layout = self.renderer.arrange_layout(self.battle, self.arranging)
            if v is not None and layout is not None:
                self.battle.set_verband_rows(v, self.renderer.drop_rows(layout, gid, pos))
            return
        if self.drag_start is None:
            return
        start, end = self.drag_start, self.to_tiles(pos)
        self.drag_start = self.drag_now = None
        cam = self.renderer.camera
        tap = abs(end[0] - start[0]) < DRAG_MIN / cam.zoom and abs(end[1] - start[1]) < DRAG_MIN / cam.zoom
        if tap and cam.overview:
            cam.zoom_to(end)                       # Übersicht: Tippen zoomt dorthin
            return
        if self.battle.outcome is not None:
            return
        if tap:
            self._tap(end)
            return
        if not self.selected:
            self.battle.events.append("Erst eine Gruppe wählen")   # ohne Auswahl verrückt ein Wischen nichts
            return
        sel = self._selection()
        v = self.battle.selected_verband(self.selected)
        if v is not None:
            self.battle.command_verband_line(v, start, end)
            return
        rings = [u for u in sel if u.formation == "o"] if sel else []
        if rings:
            self.battle.command_ring(rings, start, ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5)
            rest = [u for u in sel if u.formation != "o"]
            if rest:
                self.battle.command_line(rest, start, end)
        else:
            self.battle.command_line(sel, start, end)

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
        if not self.selected:
            return
        gate = b.gate_near(p) if b.ring else (b.gate if b.gate is not None and b.gate_at(p) else None)
        if gate is not None and gate.closed:
            b.command_ram_gate(self._selection(), gate)
            return
        cell = b.cell(*p)
        if cell in b.blocked and cell not in b.crossings and b.scenario.ram_available:
            b.command_tower_wall(self._selection(), cell)
            return
        foe = b.unit_at(p, Side.FEIND)
        v = b.selected_verband(self.selected)
        if foe is not None:
            b.command_attack_target(self._selection(), foe)
        elif v is not None:
            b.command_verband_move(v, p)            # der Verband marschiert, die Ordnung bleibt
        else:
            b.command_move(self._selection(), p)

    def _selection(self):
        if not self.selected:
            return None
        return [u for u in self.battle.lochoi if u.id in self.selected and u.fighting]

    def command(self, key: str) -> None:
        b = self.battle
        if key.startswith("group:"):
            uid = int(key.split(":")[1])
            u = b.by_id(uid)
            if u is not None and u.fighting:
                self.selected = set() if self.selected == {uid} else {uid}
            self.menu_open = False
        elif key == "menue":
            self.menu_open = not self.menu_open
        elif key == "teilen" and b.outcome is None:
            sel = self._selection()
            g = b.command_split(sel[0]) if sel and len(sel) == 1 else None
            if g is None:
                b.events.append("Teilen: eine geschlossene Gruppe in Linie wählen")
            else:
                self.selected = {sel[0].id, g.id}            # beide Hälften gewählt; antippen wählt eine
        elif key == "vereinen" and b.outcome is None:
            keep = b.command_merge(self._selection())
            if keep is None:
                b.events.append("Vereinen: zwei oder mehr Gruppen derselben Gattung wählen")
            else:
                self.selected = {keep.id}
        elif key == "jagen" and b.outcome is None:
            sel = self._selection()
            if not b.command_hunt(sel):
                b.events.append("Jagen können nur Reiter")
        elif key in ("angriff", "halten", "formation") or key.startswith(("formation:", "drill:")):
            if b.outcome is not None:
                return
            sel = self._selection()
            if not sel:
                b.events.append("Erst eine Gruppe wählen")
            elif key == "angriff":
                self.selected = {g.id for g in b.command_attack(sel)}   # geteilte Gruppen bleiben gewählt
            elif key == "halten":
                b.command_hold(sel)
            elif key.startswith("formation:"):
                b.command_formation(sel, key.split(":")[1])
            elif key.startswith("drill:"):
                b.command_drill(sel, key.split(":")[1])
            else:
                u = sel[0]
                opts = u.formation_options()
                nxt = opts[(opts.index(u.formation) + 1) % len(opts)] if u.formation in opts else opts[0]
                b.command_formation(sel, nxt)
        elif key.startswith("verband:"):
            v = next((x for x in b.verbaende if x.id == int(key.split(":")[1])), None)
            if v is not None:
                ids = {uid for uid in v.members() if (u := b.by_id(uid)) is not None and u.fighting}
                self.selected = set() if self.selected == ids else ids
            self.menu_open = False
        elif key == "verband" and b.outcome is None:
            v = b.command_verband(self._selection())
            if v is not None:
                self.selected = {uid for uid in v.members()}
        elif key == "aufloesen" and b.outcome is None:
            v = b.selected_verband(self.selected)
            if v is not None and v.id == self.arranging:
                self._arrange(None)
            b.command_dissolve_verband(v)
        elif key == "verlassen" and b.outcome is None:
            b.command_leave_verband(self._selection())
        elif key == "anordnen" and b.outcome is None:
            v = b.selected_verband(self.selected)
            self._arrange(None if v is None or self.arranging == v.id else v.id)
        elif key.startswith("vformation:") and b.outcome is None:
            v = b.selected_verband(self.selected)
            if v is not None:
                b.command_verband_formation(v, key.split(":")[1])
        elif key in ("rammbock", "turm") and b.outcome is None:
            kind = "ram" if key == "rammbock" else "tower"
            sel = self._selection()
            if sel and any(u.engine == kind or u.build_kind == kind for u in sel):
                b.command_drop(sel, kind)          # erneut drücken: ablegen oder Bau abbrechen
            elif sel:
                b.command_build(sel, kind)
        elif key == "ansicht":
            self.renderer.camera.toggle()
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
            if b.outcome is None and not self.menu_open:
                self.menu_open = True          # erst das Menü zeigen, dann Neu: kein Fehlgriff auf dem Handy
            else:
                self.battle = self._new_battle()
        elif key == "aufstellung":
            self.screen = "aufstellung"
            self.menu_open = False
            self.menu_group = min(self.menu_group, len(self.army.groups) - 1)

    # ------------------------------------------------------- Aufstellung
    def menu_command(self, key: str) -> None:
        a = self.army
        if key.startswith("groupsel:"):
            self.menu_group = min(int(key.split(":")[1]), len(a.groups) - 1)
        elif key == "prev":
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
            self.army = scaled_army(default_army(), self.own_count)
            self.menu_group = 0
        elif key == "scenario":
            self.scenario_index = (self.scenario_index + 1) % len(SCENARIOS)
        elif key == "start":
            if a.valid():
                self.screen = "schlacht"
                self.battle = self._new_battle()
        elif key == "addrow":
            a.add_tier(self.menu_group)
        elif key == "leader":
            a.set_leader(self.menu_group)
        elif key.startswith("delrow:"):
            a.remove_tier(self.menu_group, int(key.split(":")[1]))
        elif key.startswith("up:"):
            a.move_tier(self.menu_group, int(key.split(":")[1]), -1)
        elif key.startswith("down:"):
            a.move_tier(self.menu_group, int(key.split(":")[1]), +1)
        elif key.startswith("kind:"):
            _, tier, kind = key.split(":")
            a.set_kind(self.menu_group, int(tier), kind)
        if key not in ("prev", "next", "scenario", "start") and not key.startswith("groupsel:"):
            self._remember()

    # ------------------------------------------------------------ Takt
    def tick(self, dt: float) -> None:
        self.clock += dt
        if self.chip_press is not None and not self.chip_press[2] and self.clock - self.chip_press[1] >= LONG_PRESS:
            self.chip_press[2] = True              # lange gedrückt: die Gruppe kommt zur Auswahl dazu (oder geht)
            uid = int(self.chip_press[0].split(":")[1])
            u = self.battle.by_id(uid)
            if u is not None and u.fighting:
                self.selected = self.selected ^ {uid}
        if self.arranging is not None and not any(v.id == self.arranging for v in self.battle.verbaende):
            self._arrange(None)
        if self.screen == "schlacht" and not self.paused:
            self.battle.update(dt * config.TIME_SCALE)
            self.selected = {i for i in self.selected if (u := self.battle.by_id(i)) and u.fighting}

    def drag_rect(self):
        if self.drag_start is None or self.drag_now is None or not self.selected:
            return None                                   # ohne Auswahl wird keine Linie gezogen
        return (*self.drag_start, *self.drag_now)

    def draw(self) -> None:
        if self.screen == "aufstellung":
            scn = SCENARIOS[self.scenario_index]
            self.renderer.draw_menu(self.army, self.menu_group, scn, self.enemy_counts[scn.key], self.own_count)
        else:
            self.renderer.draw(self.battle, self.drag_rect(), self.paused, self.selected, self.menu_open)


async def run(max_frames: int | None = None, seed: int | None = None) -> App:
    """Startet das Spiel. ``max_frames`` begrenzt die Laufzeit (für Tests)."""
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Apoikia – Kampfprobe")
    clock = pygame.time.Clock()
    app = App(Renderer(screen), seed=seed, memory=Memory.load(config.AI_MEMORY_FILE))

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
