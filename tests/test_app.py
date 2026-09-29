"""Integrationstests: Schleife, Menü, Eingabe und Zeichnen laufen headless."""

import asyncio

import pygame
import pytest

from game import config
from game.app import App, run, to_tiles
from game.render import Renderer
from game.units import UNIT_TYPES, Side, Stance

UNIT_TYPES_SPEED_SCHWER = UNIT_TYPES["schwer"].speed


def make_app(start_in_battle: bool = True) -> App:
    pygame.init()
    surface = pygame.Surface((config.WIDTH, config.HEIGHT))
    return App(Renderer(surface), seed=1, start_in_battle=start_in_battle)


def press(app: App, pos) -> None:
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos))


def pos_of(app: App, unit) -> tuple[int, int]:
    return (int(unit.x * config.TILE), int(unit.y * config.TILE))


def bar(app: App) -> dict[str, tuple[int, int]]:
    """Die Leiste im aktuellen Zustand: Taste -> Mitte des Knopfs."""
    buttons = app.renderer.layout_bar(app.battle, app.paused, app.selected, app.menu_open)
    return {b.key: b.rect.center for b in buttons}


def labels(app: App) -> dict[str, str]:
    return {b.key: b.label for b in app.renderer.layout_bar(app.battle, app.paused, app.selected, app.menu_open)}


def test_run_headless_for_some_frames():
    app = asyncio.run(run(max_frames=30, seed=1))
    assert app.screen == "aufstellung"


def test_menu_sliders_chips_and_blocks():
    app = make_app(start_in_battle=False)
    app.draw()  # legt Knöpfe und Regler an
    tier, track = next(sl for sl in app.renderer.menu_sliders if sl[0] == 0)
    assert app.army.groups[0].tiers[0].count == 14
    # Regler nach links: null, nach rechts: Maximum, Ziehen dazwischen
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(track.x, track.centery)))
    assert app.army.groups[0].tiers[0].count == 0
    app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(track.x + track.w // 2, track.centery)))
    assert app.army.groups[0].tiers[0].count == 7
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(track.right, track.centery)))
    assert app.menu_slider is None
    # Farbpunkt: Typ wechseln, Anzahl wird gekappt
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "kind:0:reiter").rect.center)
    assert app.army.groups[0].tiers[0].kind == "reiter"
    assert app.army.groups[0].tiers[0].count == 0            # Reiter sind alle vergeben
    # Block verschieben, Reihe anlegen und entfernen
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "down:0").rect.center)
    assert app.army.groups[0].tiers[1].kind == "reiter"
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "addrow").rect.center)
    assert len(app.army.groups[0].tiers) == 4
    app.draw()
    assert not any(b.key == "addrow" for b in app.renderer.menu_buttons)
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "delrow:1").rect.center)
    assert len(app.army.groups[0].tiers) == 3
    assert [t.kind for t in app.army.groups[0].tiers] == ["mittel", "leicht", "schwer"]
    # Gruppe anlegen und Schlacht starten
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "add").rect.center)
    assert len(app.army.groups) == 4 and app.menu_group == 3
    app.draw()
    press(app, next(b for b in app.renderer.menu_buttons if b.key == "start").rect.center)
    assert app.screen == "schlacht"
    assert app.battle.men(Side.STADT) == app.own_count      # Vorlage wird auf die Stärke skaliert


def test_tap_selects_moves_and_attacks():
    app = make_app()
    b = app.battle
    unit = b.units(Side.STADT)[0]
    press(app, pos_of(app, unit))
    assert app.selected == {unit.id}
    press(app, (int(2.0 * config.TILE), int(5.0 * config.TILE)))
    assert unit.stance is Stance.HALTEN and unit.target is not None
    assert all(u.target is None for u in b.units(Side.STADT) if u is not unit)
    foe = b.units(Side.FEIND)[2]
    foe.x, foe.y = 8.0, 4.0
    press(app, pos_of(app, foe))
    assert unit.stance is Stance.ANGRIFF and unit.target_id == foe.id
    press(app, pos_of(app, unit))  # erneut tippen hebt die Auswahl auf
    assert app.selected == set()


def test_drag_draws_line_for_selection():
    app = make_app()
    b = app.battle
    unit = b.units(Side.STADT)[1]
    press(app, pos_of(app, unit))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 300)))
    app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(300, 300)))
    assert app.drag_rect() is not None
    app.draw()                                            # Vorschau zeichnen
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(330, 300)))
    assert len(b.line) == 1 and b.line[0].unit_id == unit.id
    assert unit.stance is Stance.PHALANX and unit.facing == (0.0, -1.0)
    assert unit.width == b.line[0].width
    x0, _ = to_tiles((150, 300))
    x1, _ = to_tiles((330, 300))
    assert abs(b.line[0].center[0] - (x0 + x1) / 2) < 1e-6


def test_buttons_in_bar():
    app = make_app()
    assert "angriff" not in bar(app)                      # ohne Auswahl keine Befehle
    press(app, bar(app)["alle"])
    assert len(app.selected) == len(app.battle.units(Side.STADT))
    assert labels(app)["angriff"] == "Angriff"            # gemischte Auswahl: nur das Gemeinsame
    assert not any(k.startswith("formation:") for k in bar(app))
    press(app, bar(app)["angriff"])
    assert all(u.stance in (Stance.ANGRIFF, Stance.PLAENKELN) for u in app.battle.units(Side.STADT))
    app.tick(1.0)
    assert app.battle.time > 0
    press(app, bar(app)["pause"])
    t = app.battle.time
    app.tick(1.0)
    assert app.battle.time == t
    assert "aufstellung" not in bar(app)                  # liegt hinter dem Menü
    press(app, bar(app)["menue"])
    press(app, bar(app)["aufstellung"])
    assert app.screen == "aufstellung"


def test_context_bar_shows_only_what_the_selection_can_do():
    app = make_app()
    b = app.battle
    hop, pelt, cav = b.units(Side.STADT)
    press(app, bar(app)[f"group:{hop.id}"])                # Gruppenkarte wählt
    assert app.selected == {hop.id}
    lab = labels(app)
    assert lab["angriff"] == "Sturm" and lab["halten"] == "Phalanx bilden"
    assert {"formation:linie", "formation:u", "formation:o"} <= set(lab) and "formation:keil" not in lab
    assert "rammbock" not in lab                           # kein Belagerungsgerät in der Verteidigung
    press(app, bar(app)["formation:o"])
    assert hop.formation == "o"
    press(app, bar(app)[f"group:{cav.id}"])
    lab = labels(app)
    assert lab["angriff"] == "Sturmangriff" and "formation:keil" in lab and "formation:u" not in lab
    press(app, bar(app)[f"group:{pelt.id}"])
    assert labels(app)["angriff"] == "Plänkeln"
    press(app, bar(app)[f"group:{pelt.id}"])               # nochmal: abwählen
    assert app.selected == set()
    press(app, bar(app)["menue"])                          # Menü: Neu erst nach Bestätigung
    assert app.menu_open and "neu" in bar(app)
    app.command("neu")
    assert app.battle is not b
    app.command("neu")                                     # Taste R ohne offenes Menü öffnet nur das Menü
    assert app.menu_open and app.battle.time == 0
    app.draw()


def test_renderer_draws_every_state():
    app = make_app(start_in_battle=False)
    app.draw()                                   # Menü
    app.menu_command("start")
    app.draw()                                   # Alarm
    app.command("alle")
    app.command("halten")
    for _ in range(900):
        app.tick(1 / 30)
    app.draw()                                   # Kampf oder Ergebnis
    app.paused = True
    app.draw()
    app.menu_command("scenario")
    app.menu_command("start")
    app.draw()                                   # Palisade


def test_enemy_slider_and_time_scale():
    app = make_app(start_in_battle=False)
    app.draw()
    tier, track = next(sl for sl in app.renderer.menu_sliders if sl[0] == -1)
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(track.right, track.centery)))
    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(track.right, track.centery)))
    key = app.battle.scenario.key
    from game.scenarios import SCENARIOS
    assert app.enemy_counts[key] == SCENARIOS[0].enemy_max
    app.menu_command("start")
    assert app.battle.men(Side.FEIND) == SCENARIOS[0].enemy_max
    app.command("alle")
    app.command("halten")
    app.tick(1.0)
    assert app.battle.time == pytest.approx(config.TIME_SCALE)


def test_engine_buttons_gate_and_wall_taps():
    app = make_app(start_in_battle=False)
    for _ in range(4):
        app.menu_command("scenario")
    app.menu_command("start")
    b = app.battle
    assert b.scenario.key == "angriff_wall"
    hop, pelt, cav = b.units(Side.STADT)
    assert "rammbock" not in bar(app)                 # ohne Auswahl gibt es den Knopf nicht
    press(app, pos_of(app, hop))
    assert labels(app)["rammbock"] == "Rammbock bauen"
    press(app, bar(app)["rammbock"])
    assert hop.build_kind == "ram"
    press(app, pos_of(app, cav))
    press(app, bar(app)["turm"])
    assert cav.build_kind == "tower"
    for _ in range(int((config.TOWER_BUILD_TIME + 1) / config.TIME_SCALE * 30)):
        app.tick(1 / 30)
    assert hop.engine == "ram" and cav.engine == "tower"
    press(app, pos_of(app, hop))
    gx, gy = b.gate.center
    press(app, (int(gx * config.TILE), int(gy * config.TILE)))
    assert hop.target is not None and abs(hop.target[0] - gx) < 1e-6
    press(app, pos_of(app, cav))
    press(app, (int(3.5 * config.TILE), int(7.5 * config.TILE)))
    assert cav.tower_cell == (3, 7)
    app.draw()


def test_pressing_engine_button_again_drops_it():
    app = make_app(start_in_battle=False)
    for _ in range(4):
        app.menu_command("scenario")
    app.menu_command("start")
    b = app.battle
    hop, pelt, cav = b.units(Side.STADT)
    press(app, pos_of(app, hop))
    press(app, bar(app)["rammbock"])
    assert hop.build_kind == "ram"
    press(app, bar(app)["rammbock"])                   # während des Baus: abbrechen
    assert hop.build_kind is None and hop.building is None
    press(app, bar(app)["rammbock"])
    for _ in range(int((config.RAM_BUILD_TIME + 1) / config.TIME_SCALE * 30)):
        app.tick(1 / 30)
    assert hop.engine == "ram"
    press(app, bar(app)["rammbock"])                   # fertig: liegen lassen
    assert hop.engine is None and len(b.debris) == 1
    assert hop.speed == UNIT_TYPES_SPEED_SCHWER



def test_attack_and_hold_need_a_selection_and_formation_cycles():
    app = make_app()
    b = app.battle
    hop, pelt, cav = b.units(Side.STADT)
    app.command("angriff")
    assert all(u.stance is Stance.HALTEN for u in b.units(Side.STADT))     # ohne Auswahl passiert nichts
    assert "Erst eine Gruppe wählen" in b.events[-1]
    app.selected = {pelt.id}
    app.command("angriff")
    assert pelt.stance is Stance.PLAENKELN and hop.stance is Stance.HALTEN
    app.selected = {cav.id}
    app.command("angriff")
    assert cav.stance is Stance.ANGRIFF and cav.mode == "sturm"
    app.selected = {hop.id}
    app.command("halten")
    assert hop.stance is Stance.PHALANX                                    # Phalanx an Ort und Stelle
    app.command("formation")
    assert hop.formation == "u"
    app.command("formation")
    assert hop.formation == "o"
    app.command("formation")
    assert hop.formation == "linie"
    app.selected = {cav.id}
    app.command("formation")
    assert cav.formation == "keil"
    app.selected = {pelt.id}
    app.command("formation")
    assert pelt.formation == "o"
    app.draw()
