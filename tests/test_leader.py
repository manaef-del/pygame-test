"""Der Anführer: kämpft in der zugeteilten Gruppe mit, hält viel mehr aus, seine
Gruppe nimmt etwas weniger Schaden und flieht später."""

from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest                                                        # noqa: E402

from game import config                                              # noqa: E402
from game.army import Army, GroupSpec, Tier, default_army, scaled_army, split_by_arm   # noqa: E402
from game.battle import Battle                                       # noqa: E402
from kleine_karten import KLEIN_ANGRIFF, KLEIN_OFFEN                    # noqa: E402
from game.units import UNIT_TYPES, Lochos, Man, Side, Stance, arrange   # noqa: E402

DT = 1 / 30


def test_the_default_army_has_one_leader_with_the_hoplites():
    a = default_army()
    assert a.leader_index() == 0 and sum(g.leader for g in a.groups) == 1
    men = a.groups[0].build_men()
    leaders = [m for m in men if m.leader]
    assert len(leaders) == 1 and len(men) == a.groups[0].men() + 1        # zusätzlich zum Vorrat
    chief = leaders[0]
    assert chief.kind.key == "schwer"                                     # Gattung der vordersten Reihe
    assert chief.hp == pytest.approx(UNIT_TYPES["schwer"].hp * config.LEADER_HP_FACTOR)
    assert chief.attack == UNIT_TYPES["schwer"].attack                    # nicht stärker, nur zäher


def test_the_leader_can_be_given_to_another_group_and_survives_deleting_his_group():
    a = default_army()
    a.set_leader(2)
    assert a.leader_index() == 2 and [g.leader for g in a.groups] == [False, False, True]
    reiter = [m for m in a.groups[2].build_men() if m.leader][0]
    assert reiter.kind.cavalry                                            # bei den Reitern reitet er mit
    a.delete_group(2)
    assert a.leader_index() == 0
    assert scaled_army(a, 120).leader_index() == 0                       # skaliert bleibt er, wo er war


def test_splitting_a_mixed_group_keeps_the_leader_with_the_main_part():
    a = Army(groups=[GroupSpec("Alle", [Tier("schwer", 10), Tier("peltast", 8)], leader=True)])
    parts = split_by_arm(a)
    assert [g.leader for g in parts.groups] == [True, False]


def test_battle_places_the_leader_and_the_settlement_has_one_too():
    b = Battle(KLEIN_ANGRIFF, random.Random(1))
    own = [m for u in b.units(Side.STADT) for m in u.all_men() if m.leader]
    foe = [(m, u) for u in b.units(Side.FEIND) for m in u.all_men() if m.leader]
    assert len(own) == 1 and len(foe) == 1
    assert foe[0][1].share(lambda m: m.kind.hoplite) >= 0.5               # bei ihren Hopliten


def group(leader: bool, x: float = 8.0) -> Lochos:
    men = [Man(UNIT_TYPES["mittel"]) for _ in range(20)]
    if leader:
        men[0] = Man(UNIT_TYPES["mittel"], leader=True)
    return Lochos(1 if leader else 2, Side.STADT, arrange(men, 10), x, 9.0, facing=(0.0, -1.0), stance=Stance.HALTEN)


def test_a_group_with_leader_takes_less_damage_and_flees_later():
    b = Battle(KLEIN_OFFEN, random.Random(1))
    raider = b.units(Side.FEIND)[0]
    with_leader, without = group(True), group(False, x=12.0)
    raider.x, raider.y = with_leader.x, with_leader.y - 1.0
    mod_with, _ = b._defense_mod(raider, with_leader)
    raider.x = without.x
    mod_without, _ = b._defense_mod(raider, without)
    assert mod_with == pytest.approx(mod_without * config.LEADER_ARMOR)
    b.lochoi = [with_leader, without]
    for u in (with_leader, without):
        u.morale = u.rout_threshold - 0.05                               # unter der normalen Schwelle ...
    b._morale(DT)
    assert without.stance is Stance.FLUCHT
    assert with_leader.stance is not Stance.FLUCHT                        # ... hält sein Anführer sie noch


def test_the_fall_of_the_leader_is_reported_and_ends_the_bonus():
    b = Battle(KLEIN_OFFEN, random.Random(1))
    hop = next(u for u in b.units(Side.STADT) if u.leader_man() is not None)
    chief = hop.leader_man()
    chief.hp = 0.0
    hop.bury()
    b._morale(DT)
    assert hop.leader_man() is None
    assert any("Anführer ist gefallen" in e for e in b.events)
