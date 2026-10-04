"""Sammeln nach der Flucht: Verteidiger sammeln sich auf der Agora und kämpfen dort
bis zum letzten Mann, Angreifer an ihrem Kartenrand, außer die Lage ist aussichtslos."""

from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from game import config                                              # noqa: E402
from game.battle import Battle                                       # noqa: E402
from game.geometry import dist                                       # noqa: E402
from kleine_karten import KLEIN_ANGRIFF, KLEIN_OFFEN                    # noqa: E402
from game.units import Side, Stance                                  # noqa: E402

DT = 1 / 30


def run(b: Battle, seconds: float) -> None:
    for _ in range(int(seconds / DT)):
        b.update(DT)
        if b.outcome:
            break


def quiet(b: Battle) -> None:
    """Der Gegner steht still und wirft nicht: es geht nur um die Fliehenden."""
    b._ai_raiders = lambda: None
    b._ai_defenders = lambda: None
    b._volleys = lambda dt: None
    b.alarm = False
    for u in b.units(Side.FEIND if not b.attacking else Side.FEIND):
        u.target = None
        u.stance = Stance.HALTEN


def rout(b: Battle, u, morale: float = 0.1) -> None:
    u.morale = morale
    b._morale(DT)
    assert u.stance is Stance.FLUCHT


def test_routed_defenders_run_to_the_agora_and_rally_there():
    b = Battle(KLEIN_OFFEN, random.Random(1))
    quiet(b)
    hop, pelt, cav = b.units(Side.STADT)
    hop.x, hop.y = 8.0, 9.0
    hop.place_men()
    rout(b, hop)
    assert not hop.leaving and hop.target == b.agora                 # zur Agora, nicht vom Feld
    run(b, 40)
    assert hop.alive and b.inside(hop.x, hop.y)
    assert hop.stance is Stance.HALTEN and hop.morale >= config.RALLY_MORALE   # gesammelt, nimmt wieder Befehle an
    assert dist(hop.pos, b.agora) <= config.RALLY_RADIUS
    assert any("sammeln sich auf der Agora" in e for e in b.events)
    assert hop in b.units(Side.STADT, fighting_only=True)


def test_defenders_cornered_on_the_agora_fight_to_the_last_man():
    b = Battle(KLEIN_OFFEN, random.Random(1))
    quiet(b)
    hop, pelt, cav = b.units(Side.STADT)
    ax, ay = b.agora
    hop.x, hop.y = ax, ay - 3.0
    hop.place_men()
    rout(b, hop)                                                      # flieht auf die Agora ...
    hop.x, hop.y = ax, ay                                             # ... und ist dort angekommen
    hop.place_men()
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y, raider.facing = ax, ay - hop.half_d - raider.half_d - 0.3, (0.0, 1.0)
    raider.place_men()
    raider.stance = Stance.ANGRIFF
    raider.target_id = hop.id
    raider.target = hop.pos
    run(b, 1)
    assert hop.stance is not Stance.FLUCHT                            # umgedreht: letzter Kampf
    assert any("letzten Kampf" in e for e in b.events)
    hop.morale = -0.5                                                 # auch ohne Moral: auf der Agora flieht niemand mehr
    run(b, 1)
    assert hop.stance is not Stance.FLUCHT


def test_attackers_rally_at_their_own_edge():
    b = Battle(KLEIN_ANGRIFF, random.Random(1))
    quiet(b)
    hop, pelt, cav = b.units(Side.STADT)
    hop.x, hop.y = 8.0, 10.0
    hop.place_men()
    rout(b, hop)
    assert not hop.leaving
    assert hop.target[1] == b.rows - config.RALLY_EDGE               # die Stadt kommt von Süden
    run(b, 40)
    assert hop.stance is Stance.HALTEN and b.inside(hop.x, hop.y)
    assert any("sammeln sich am Rand des Feldes" in e for e in b.events)


def test_attackers_leave_the_field_when_the_battle_is_hopeless():
    b = Battle(KLEIN_ANGRIFF, random.Random(1))
    quiet(b)
    hop, pelt, cav = b.units(Side.STADT)
    for u in (pelt, cav):                                             # fast alles verloren ...
        for row in u.rows:
            row.clear()
    hop.rows = [row[:5] for row in hop.rows]
    assert b._hopeless(Side.STADT)                                    # ... und der Feind steht noch
    rout(b, hop)
    assert hop.leaving and hop.target[1] > b.rows                    # vom Feld, kein Sammeln
    run(b, 30)
    assert hop.withdrawn or not b.inside(hop.x, hop.y)


def test_the_enemy_settlement_holds_to_the_last_man():
    """Greift der Spieler eine Siedlung an, zieht sie nicht ab: Ihre Geschlagenen
    fliehen auf ihre eigene Agora, nicht vom Feld."""
    b = Battle(KLEIN_ANGRIFF, random.Random(1))
    quiet(b)
    defenders = b.units(Side.FEIND)
    for u in defenders[1:]:
        for row in u.rows:
            row.clear()
    b._check_withdraw()
    assert not any("zieht ab" in e for e in b.events)
    u = defenders[0]
    rout(b, u)
    assert not u.leaving and u.target == b.agora


def test_raiders_rally_unless_they_give_up():
    b = Battle(KLEIN_OFFEN, random.Random(1))
    quiet(b)
    raider = b.units(Side.FEIND)[0]
    raider.x, raider.y = 8.0, 6.0
    raider.place_men()
    rout(b, raider)
    assert not raider.leaving and raider.target[1] == config.RALLY_EDGE   # die Räuber kommen von Norden
    for u in b.units(Side.FEIND)[1:]:                                 # fast alle Räuber gefallen: sie geben auf
        for row in u.rows:
            row.clear()
    b._check_withdraw()
    assert raider.leaving and raider.target[1] < 0


def test_attackers_chased_to_their_edge_leave_the_field():
    b = Battle(KLEIN_ANGRIFF, random.Random(1))
    quiet(b)
    hop, pelt, cav = b.units(Side.STADT)
    rx, ry = 8.0, b.rows - config.RALLY_EDGE
    hop.x, hop.y = rx, ry - 3.0
    hop.place_men()
    rout(b, hop)
    hop.x, hop.y = rx, ry                                             # am eigenen Rand angekommen ...
    hop.place_men()
    foe = b.units(Side.FEIND, fighting_only=True)[0]
    foe.x, foe.y = rx, ry - hop.half_d - foe.half_d - 0.5             # ... und der Feind ist nachgesetzt
    foe.place_men()
    b._morale(DT)
    assert hop.leaving and hop.target[1] > b.rows
