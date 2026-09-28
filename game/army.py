"""Aufstellung: aus dem Vorrat werden Gruppen zusammengestellt.

Jede Gruppe hat drei Abschnitte (vorn, Mitte, hinten). Sie legen die
Reihenfolge der Männer von vorn nach hinten fest. Wie viele Reihen
daraus werden, entscheidet die Breite, die der Spieler beim Aufziehen
der Gruppe zieht.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .units import PLAYER_TYPES, TIERS, UNIT_TYPES, Man

POOL: dict[str, int] = {"schwer": 14, "mittel": 13, "leicht": 13, "peltast": 15, "reiter": 20}
MAX_GROUPS = 8


@dataclass
class GroupSpec:
    name: str
    tiers: list[dict[str, int]] = field(default_factory=lambda: [{} for _ in TIERS])

    def count(self, key: str) -> int:
        return sum(t.get(key, 0) for t in self.tiers)

    def tier_size(self, i: int) -> int:
        return sum(self.tiers[i].values())

    def men(self) -> int:
        return sum(self.tier_size(i) for i in range(len(self.tiers)))

    def build_men(self) -> list[Man]:
        """Männer in Reihenfolge vorn nach hinten."""
        out: list[Man] = []
        for tier in self.tiers:
            for key in PLAYER_TYPES:
                out.extend(Man(UNIT_TYPES[key]) for _ in range(tier.get(key, 0)))
        return out


@dataclass
class Army:
    groups: list[GroupSpec] = field(default_factory=list)
    pool: dict[str, int] = field(default_factory=lambda: dict(POOL))

    def used(self, key: str) -> int:
        return sum(g.count(key) for g in self.groups)

    def remaining(self, key: str) -> int:
        return self.pool.get(key, 0) - self.used(key)

    def can_add(self, group: int, tier: int, key: str) -> bool:
        return self.remaining(key) > 0

    def add(self, group: int, tier: int, key: str, n: int = 1) -> bool:
        n = min(n, self.remaining(key))
        if n <= 0:
            return False
        t = self.groups[group].tiers[tier]
        t[key] = t.get(key, 0) + n
        return True

    def remove(self, group: int, tier: int, key: str, n: int = 1) -> bool:
        t = self.groups[group].tiers[tier]
        if t.get(key, 0) <= 0:
            return False
        t[key] = max(0, t[key] - n)
        if t[key] == 0:
            del t[key]
        return True

    def add_group(self) -> bool:
        if len(self.groups) >= MAX_GROUPS:
            return False
        self.groups.append(GroupSpec(f"Gruppe {len(self.groups) + 1}"))
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
        GroupSpec("Hopliten", [{"schwer": 14}, {"mittel": 13}, {"leicht": 13}]),
        GroupSpec("Peltasten", [{"peltast": 15}, {}, {}]),
        GroupSpec("Reiter", [{"reiter": 20}, {}, {}]),
    ])
