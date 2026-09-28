"""Aufstellung: aus dem Vorrat werden Gruppen mit Reihen zusammengestellt."""

from __future__ import annotations

from dataclasses import dataclass, field

from .units import MAX_ROWS, PLAYER_TYPES, UNIT_TYPES, Man

POOL: dict[str, int] = {"schwer": 14, "mittel": 13, "leicht": 13, "peltast": 15, "reiter": 20}
MAX_PER_ROW = 8
MAX_GROUPS = 8


@dataclass
class GroupSpec:
    name: str
    rows: list[dict[str, int]] = field(default_factory=lambda: [{} for _ in range(MAX_ROWS)])

    def count(self, key: str) -> int:
        return sum(r.get(key, 0) for r in self.rows)

    def row_size(self, r: int) -> int:
        return sum(self.rows[r].values())

    def men(self) -> int:
        return sum(self.row_size(r) for r in range(len(self.rows)))

    def build_rows(self) -> list[list[Man]]:
        """Männer je Reihe, schwere Typen in der Mitte."""
        out: list[list[Man]] = []
        for row in self.rows:
            men: list[Man] = []
            for key in PLAYER_TYPES:
                men.extend(Man(UNIT_TYPES[key]) for _ in range(row.get(key, 0)))
            if men:
                out.append(men)
        return out


@dataclass
class Army:
    groups: list[GroupSpec] = field(default_factory=list)
    pool: dict[str, int] = field(default_factory=lambda: dict(POOL))

    def used(self, key: str) -> int:
        return sum(g.count(key) for g in self.groups)

    def remaining(self, key: str) -> int:
        return self.pool.get(key, 0) - self.used(key)

    def can_add(self, group: int, row: int, key: str) -> bool:
        g = self.groups[group]
        return self.remaining(key) > 0 and g.row_size(row) < MAX_PER_ROW

    def add(self, group: int, row: int, key: str) -> bool:
        if not self.can_add(group, row, key):
            return False
        r = self.groups[group].rows[row]
        r[key] = r.get(key, 0) + 1
        return True

    def remove(self, group: int, row: int, key: str) -> bool:
        r = self.groups[group].rows[row]
        if r.get(key, 0) <= 0:
            return False
        r[key] -= 1
        if r[key] == 0:
            del r[key]
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
    """Vorgabe: drei Phalanx-Gruppen, Peltasten dahinter, Reiter auf den Flügeln."""
    return Army(groups=[
        GroupSpec("Reiter links", [{"reiter": 8}, {}, {}]),
        GroupSpec("Phalanx links", [{"schwer": 7}, {"mittel": 7}, {}]),
        GroupSpec("Phalanx Mitte", [{"schwer": 7}, {"mittel": 6}, {"peltast": 7}]),
        GroupSpec("Phalanx rechts", [{"leicht": 7}, {"leicht": 6}, {"peltast": 8}]),
        GroupSpec("Reiter rechts", [{"reiter": 8}, {}, {}]),
        GroupSpec("Reiter Reserve", [{"reiter": 4}, {}, {}]),
    ])
