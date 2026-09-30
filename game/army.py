"""Aufstellung: aus dem Vorrat werden Gruppen zusammengestellt.

Jede Gruppe besteht aus Reihen-Blöcken, von vorn nach hinten. Ein Block
hat einen Truppentyp und eine Anzahl. Wie viele echte Reihen daraus
werden, entscheidet die Breite, die der Spieler beim Aufziehen zieht;
landen mehrere Blöcke in einer Reihe, wechseln sich ihre Männer ab.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .units import PLAYER_TYPES, UNIT_TYPES, Man

MAX_GROUPS = 8
MAX_TIERS = 4
OWN_DEFAULT = 75
OWN_MIN = 10
OWN_MAX = 200


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
    """Die Truppe: Gruppen aus Blöcken, gespeist aus einem gemeinsamen Vorrat
    (die Truppenstärke). Jede Gattung darf davon so viel nehmen, wie noch frei
    ist; wer die Reiter streicht, kann die Männer bei den Hopliten einsetzen."""

    groups: list[GroupSpec] = field(default_factory=list)
    total: int = OWN_DEFAULT

    # ------------------------------------------------------------ Vorrat
    def used(self, key: str | None = None) -> int:
        if key is None:
            return sum(g.men() for g in self.groups)
        return sum(g.count(key) for g in self.groups)

    def remaining(self, key: str | None = None) -> int:
        return self.total - self.used()

    def max_for(self, group: int, tier: int) -> int:
        """Höchstzahl für diesen Block: Rest im Vorrat plus eigener Bestand."""
        t = self.groups[group].tiers[tier]
        return self.remaining() + t.count

    # ------------------------------------------------------------ Blöcke
    def set_count(self, group: int, tier: int, n: int) -> int:
        t = self.groups[group].tiers[tier]
        t.count = max(0, min(n, self.max_for(group, tier)))
        return t.count

    def set_kind(self, group: int, tier: int, key: str) -> None:
        t = self.groups[group].tiers[tier]
        if key in UNIT_TYPES:
            t.kind = key                      # die Männer bleiben, nur die Gattung wechselt

    def add_tier(self, group: int) -> bool:
        g = self.groups[group]
        if len(g.tiers) >= MAX_TIERS:
            return False
        key = g.tiers[-1].kind if g.tiers else PLAYER_TYPES[0]
        g.tiers.append(Tier(key, max(0, min(5, self.remaining()))))
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
        return self.total_men() > 0 and self.used() <= self.total


def scaled_army(source: Army, total: int) -> Army:
    """Dieselbe Mischung wie ``source``, auf ``total`` Mann skaliert; Blöcke,
    die dabei leer würden, bleiben mit einem Mann erhalten, wenn sie besetzt waren."""
    base = source.total_men()
    if base <= 0 or total <= 0:
        return Army(groups=[], total=max(0, total))
    groups: list[GroupSpec] = []
    rounded_total = 0
    for g in source.groups:
        tiers = [Tier(t.kind, max(1, round(t.count * total / base)) if t.count > 0 else 0) for t in g.tiers]
        tiers = [t for t in tiers if t.count > 0]
        rounded_total += sum(t.count for t in tiers)
        if tiers:
            groups.append(GroupSpec(g.name, tiers))
    # Rundungsdifferenz auf den größten Block
    if groups and rounded_total != total:
        biggest = max((t for g in groups for t in g.tiers), key=lambda t: t.count)
        biggest.count = max(1, biggest.count + (total - rounded_total))
    return Army(groups=groups, total=total)


def default_army() -> Army:
    """Vorgabe: Hopliten, Peltasten, Reiter – je eine Gruppe."""
    return Army(groups=[
        GroupSpec("Hopliten", [Tier("schwer", 14), Tier("mittel", 13), Tier("leicht", 13)]),
        GroupSpec("Peltasten", [Tier("peltast", 15)]),
        GroupSpec("Reiter", [Tier("reiter", 20)]),
    ], total=OWN_DEFAULT)


def arm_of(kind: str) -> str:
    t = UNIT_TYPES[kind]
    return "reiter" if t.cavalry else ("peltasten" if t.ranged else "hopliten")


def split_by_arm(army: Army, min_men: int = 4) -> Army:
    """Die Siedlung ordnet gemischte Gruppen nach Waffengattung: Hopliten, Peltasten
    und Reiter je als eigene Gruppe, damit sie getrennt geführt werden können.
    Zu kleine Abschnitte bleiben bei den Hopliten."""
    out: list[GroupSpec] = []
    for g in army.groups:
        parts: dict[str, list[Tier]] = {}
        for t in g.tiers:
            if t.count > 0:
                parts.setdefault(arm_of(t.kind), []).append(Tier(t.kind, t.count))
        if len(parts) <= 1:
            out.append(GroupSpec(g.name, [Tier(t.kind, t.count) for t in g.tiers if t.count > 0]))
            continue
        main = "hopliten" if "hopliten" in parts else next(iter(parts))
        for arm, tiers in parts.items():
            n = sum(t.count for t in tiers)
            if arm != main and n < min_men:
                parts[main].extend(tiers)
        for arm, tiers in parts.items():
            if arm != main and sum(t.count for t in tiers) < min_men:
                continue
            name = g.name if arm == main else {"reiter": "Reiter", "peltasten": "Peltasten", "hopliten": "Hopliten"}[arm]
            out.append(GroupSpec(name, tiers))
    return Army(groups=out)
