"""Aufstellungen der Siedlung: Sie kopiert den Spieler nicht mehr, sondern wählt
aus wenigen eigenen Aufstellungen („Doktrinen“) die, die gegen seine Mischung
am besten abschneidet. Die Zuordnung stammt aus dem Simulator
(``tools/simulate.py --matrix``), siehe ``docs/ki-simulation.md``.
"""

from __future__ import annotations

from .army import Army, GroupSpec, Tier, scaled_army
from .units import UNIT_TYPES

# Jede Doktrin als Mischung (Anteile), Gruppen nach Waffengattung getrennt.
DOCTRINES: dict[str, Army] = {
    "spiegel": Army(groups=[]),                                     # dieselbe Mischung wie der Spieler
    "hoplitenwall": Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 25), Tier("mittel", 25), Tier("leicht", 20)]),
        GroupSpec("Peltasten", [Tier("peltast", 30)]),
    ]),
    "schwere_phalanx": Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 45), Tier("mittel", 35)]),
        GroupSpec("Peltasten", [Tier("peltast", 20)]),
    ]),
    "ausgewogen": Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 15), Tier("mittel", 20), Tier("leicht", 15)]),
        GroupSpec("Peltasten", [Tier("peltast", 20)]),
        GroupSpec("Reiter", [Tier("reiter", 30)]),
    ]),
    "reiterlastig": Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 15), Tier("mittel", 15)]),
        GroupSpec("Peltasten", [Tier("peltast", 20)]),
        GroupSpec("Reiter", [Tier("reiter", 50)]),
    ]),
    "peltastenschwarm": Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 15), Tier("mittel", 20)]),
        GroupSpec("Peltasten", [Tier("peltast", 25)]),
        GroupSpec("Peltasten II", [Tier("peltast", 20)]),
        GroupSpec("Reiter", [Tier("reiter", 20)]),
    ]),
}

DOCTRINE_NAMES = {
    "spiegel": "Spiegelbild",
    "hoplitenwall": "Hoplitenwall",
    "schwere_phalanx": "Schwere Phalanx",
    "ausgewogen": "Ausgewogen",
    "reiterlastig": "Reiterlastig",
    "peltastenschwarm": "Peltastenschwarm",
}


def shares(army: Army) -> dict[str, float]:
    """Anteile Hopliten / Peltasten / Reiter an der Truppe (0..1)."""
    total = max(1, army.total_men())
    out = {"hopliten": 0.0, "peltasten": 0.0, "reiter": 0.0}
    for g in army.groups:
        for t in g.tiers:
            kind = UNIT_TYPES[t.kind]
            key = "reiter" if kind.cavalry else ("peltasten" if kind.ranged else "hopliten")
            out[key] += t.count / total
    return out


def classify(army: Army) -> str:
    """Grobe Einordnung der Spielertruppe."""
    s = shares(army)
    if s["reiter"] >= 0.4:
        return "reiterlastig"
    if s["peltasten"] >= 0.4:
        return "peltastenlastig"
    if s["reiter"] < 0.1:
        return "ohne_reiter"
    if len([g for g in army.groups if g.men() > 0]) <= 1:
        return "ein_block"
    return "ausgewogen"


# Aus dem Matrix-Lauf (docs/ki-simulation.md, Lauf 4): Spielerklasse -> Doktrin,
# die den Angriff des Spielers am seltensten durchkommen ließ.
COUNTERS: dict[str, str] = {
    "reiterlastig": "hoplitenwall",      # dichter Wall mit vielen Peltasten gegen Reiter
    "peltastenlastig": "schwere_phalanx",
    "ohne_reiter": "schwere_phalanx",
    "ein_block": "schwere_phalanx",
    "ausgewogen": "schwere_phalanx",
}
MEMORY_KEY = "doktrin"


def choose_doctrine(player: Army, memory=None) -> str:
    """Die Doktrin gegen diese Spielertruppe: aus der Tabelle, oder aus dem
    Gedächtnis, wenn dort eine andere gegen diese Klasse besser abschnitt."""
    cls = classify(player)
    default = COUNTERS.get(cls, "schwere_phalanx")
    if memory is None:
        return default
    key = f"{MEMORY_KEY}:{cls}"
    best, best_w = default, memory.weight(key, default)
    for name in DOCTRINES:
        if name == "spiegel":
            continue
        w = memory.weight(key, name)
        if w > best_w + 0.05:
            best, best_w = name, w
    return best


def enemy_army(player: Army, total: int, doctrine: str | None = None) -> Army:
    """Die Truppe der Siedlung: nach Doktrin, auf ``total`` Mann skaliert."""
    name = doctrine or choose_doctrine(player)
    template = DOCTRINES.get(name)
    if template is None or not template.groups:
        return scaled_army(player, total)
    return scaled_army(template, total)
