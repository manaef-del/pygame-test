"""Aufstellung: aus dem Vorrat werden Gruppen zusammengestellt.

Jede Gruppe besteht aus Reihen-Blöcken, von vorn nach hinten. Ein Block
hat einen Truppentyp und eine Anzahl. Wie viele echte Reihen daraus
werden, entscheidet die Breite, die der Spieler beim Aufziehen zieht;
landen mehrere Blöcke in einer Reihe, wechseln sich ihre Männer ab.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .units import PLAYER_TYPES, UNIT_TYPES, Man

POOL: dict[str, int] = {"schwer": 14, "mittel": 13, "leicht": 13, "peltast": 15, "reiter": 20}
MAX_GROUPS = 8
MAX_TIERS = 4


@dataclass
class Tier:
    kind: str
    count: int


@dataclass
class GroupSpec:
    name: str
    tiers: list[Tier] = field(default_factory=list)

    def count(self, key: str) -> int:
        return sum(t.count for t in self.tiers if t.kind == key)

    def men(self) -> int:
        return sum(t.count for t in self.tiers)

    def build_men(self) -> list[Man]:
        """Männer in Reihenfolge vorn nach hinten, mit ihrem Abschnitt."""
        out: list[Man] = []
        for i, t in enumerate(self.tiers):
            out.extend(Man(UNIT_TYPES[t.kind], tier=i) for _ in range(t.count))
        return out


@dataclass
class Army:
    groups: list[GroupSpec] = field(default_factory=list)
    pool: dict[str, int] = field(default_factory=lambda: dict(POOL))

    # ------------------------------------------------------------ Vorrat
    def used(self, key: str) -> int:
        return sum(g.count(key) for g in self.groups)

    def remaining(self, key: str) -> int:
        return self.pool.get(key, 0) - self.used(key)

    def max_for(self, group: int, tier: int) -> int:
        """Höchstzahl für diesen Block: Rest im Vorrat plus eigener Bestand."""
        t = self.groups[group].tiers[tier]
        return self.remaining(t.kind) + t.count

    # ------------------------------------------------------------ Blöcke
    def set_count(self, group: int, tier: int, n: int) -> int:
        t = self.groups[group].tiers[tier]
        t.count = max(0, min(n, self.max_for(group, tier)))
        return t.count

    def set_kind(self, group: int, tier: int, key: str) -> None:
        t = self.groups[group].tiers[tier]
        if key == t.kind or key not in self.pool:
            return
        wanted = t.count
        t.kind = key
        t.count = 0
        t.count = min(wanted, self.remaining(key))

    def add_tier(self, group: int) -> bool:
        g = self.groups[group]
        if len(g.tiers) >= MAX_TIERS:
            return False
        key = next((k for k in PLAYER_TYPES if self.remaining(k) > 0), PLAYER_TYPES[0])
        g.tiers.append(Tier(key, min(5, self.remaining(key))))
        return True

    def remove_tier(self, group: int, tier: int) -> None:
        g = self.groups[group]
        if 0 <= tier < len(g.tiers):
            del g.tiers[tier]

    def move_tier(self, group: int, tier: int, delta: int) -> None:
        g = self.groups[group]
        j = tier + delta
        if 0 <= tier < len(g.tiers) and 0 <= j < len(g.tiers):
            g.tiers[tier], g.tiers[j] = g.tiers[j], g.tiers[tier]

    # ----------------------------------------------------------- Gruppen
    def add_group(self) -> bool:
        if len(self.groups) >= MAX_GROUPS:
            return False
        self.groups.append(GroupSpec(f"Gruppe {len(self.groups) + 1}"))
        self.add_tier(len(self.groups) - 1)
        return True

    def delete_group(self, index: int) -> None:
        if 0 <= index < len(self.groups) and len(self.groups) > 1:
            del self.groups[index]
            for i, g in enumerate(self.groups):
                if g.name.startswith("Gruppe "):
                    g.name = f"Gruppe {i + 1}"

    def total_men(self) -> int:
        return sum(g.men() for g in self.groups)

    def valid(self) -> bool:
        return self.total_men() > 0 and all(self.remaining(k) >= 0 for k in self.pool)


def default_army() -> Army:
    """Vorgabe: Hopliten, Peltasten, Reiter – je eine Gruppe."""
    return Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 14), Tier("mittel", 13), Tier("leicht", 13)]),
        GroupSpec("Peltasten", [Tier("peltast", 15)]),
        GroupSpec("Reiter", [Tier("reiter", 20)]),
    ])
