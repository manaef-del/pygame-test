"""Truppentypen, einzelne Männer und die Gruppe (Lochos).

Eine Gruppe besteht aus bis zu drei Reihen. Jede Reihe ist eine Liste
von Männern beliebigen Typs. Die vordere Reihe kämpft im Nahkampf,
Hopliten der zweiten Reihe stechen über die Front, Peltasten in den
hinteren Reihen werfen. Getroffen wird die Reihe, die dem Angreifer
zugewandt ist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from . import config


class Side(Enum):
    STADT = "stadt"
    FEIND = "feind"


class Stance(Enum):
    HALTEN = "halten"      # steht, kämpft rundum ohne Formationsbonus
    PHALANX = "phalanx"    # in der Linie, stark von vorn
    ANGRIFF = "angriff"    # verfolgt einen Gegner
    RAUB = "raub"          # Gegner: zieht zu Häusern, plündert
    FLUCHT = "flucht"      # geschlagen, läuft vom Feld


@dataclass(frozen=True)
class UnitType:
    key: str
    name: str
    short: str
    attack: float                 # Nahkampf je Mann
    hp: float                     # Schaden, den ein Mann aushält
    speed: float                  # Kacheln pro Sekunde
    color: tuple[int, int, int]
    ranged_attack: float = 0.0    # Fernkampf je Mann (0 = keiner)
    ranged_range: float = 0.0
    bravery: float = 1.0          # Moralverlust-Faktor, kleiner = tapferer
    hoplite: bool = False         # trägt den Schildwall
    cavalry: bool = False


UNIT_TYPES: dict[str, UnitType] = {
    "schwer": UnitType("schwer", "Schwere Hopliten", "S", attack=1.2, hp=3.0, speed=1.0,
                       color=config.COLOR_HOPLIT_SCHWER, bravery=0.6, hoplite=True),
    "mittel": UnitType("mittel", "Mittlere Hopliten", "M", attack=1.0, hp=2.2, speed=1.2,
                       color=config.COLOR_HOPLIT_MITTEL, bravery=0.7, hoplite=True),
    "leicht": UnitType("leicht", "Leichte Hopliten", "L", attack=0.9, hp=1.5, speed=1.5,
                       color=config.COLOR_HOPLIT_LEICHT, bravery=0.9, hoplite=True),
    "peltast": UnitType("peltast", "Peltasten", "P", attack=0.5, hp=1.0, speed=1.7,
                        color=config.COLOR_PELTAST, ranged_attack=0.6, ranged_range=3.5,
                        bravery=1.1),
    "reiter": UnitType("reiter", "Reiter", "R", attack=1.4, hp=2.0, speed=3.0,
                       color=config.COLOR_REITER, bravery=0.8, cavalry=True),
    "raeuber": UnitType("raeuber", "Räuber", "X", attack=1.0, hp=1.8, speed=1.5,
                        color=config.COLOR_RAEUBER, bravery=1.3),
}

PLAYER_TYPES = ("schwer", "mittel", "leicht", "peltast", "reiter")
MAX_ROWS = 3


@dataclass
class Man:
    kind: UnitType
    hp: float = 0.0

    def __post_init__(self) -> None:
        if self.hp == 0.0:
            self.hp = self.kind.hp


@dataclass
class Lochos:
    """Eine Gruppe: bis zu drei Reihen von Männern, die zusammen handeln."""

    id: int
    side: Side
    rows: list[list[Man]]
    x: float
    y: float
    name: str = ""
    facing: tuple[float, float] = (0.0, -1.0)
    morale: float = 1.0
    stance: Stance = Stance.HALTEN
    target: tuple[float, float] | None = None
    target_id: int | None = None      # verfolgter Gegner
    waypoints: list[tuple[float, float]] = field(default_factory=list)
    in_line: bool = False             # in der Phalanx angekommen
    withdrawn: bool = False           # hat das Feld verlassen
    engaged: bool = False             # in diesem Schritt im Nahkampf
    last_arc: str = ""
    men_start: int = 0
    pool: list[float] = field(default_factory=list)  # angesammelter Schaden je Reihe
    rout_threshold: float = 0.3

    def __post_init__(self) -> None:
        self.rows = [list(r) for r in self.rows if r]
        if self.men_start == 0:
            self.men_start = self.men
        self.pool = [0.0] * len(self.rows)

    # ---------------------------------------------------------- Abfragen
    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def men(self) -> int:
        return sum(len(r) for r in self.rows)

    @property
    def alive(self) -> bool:
        return self.men > 0 and not self.withdrawn

    @property
    def fighting(self) -> bool:
        return self.alive and self.stance is not Stance.FLUCHT

    @property
    def in_phalanx(self) -> bool:
        return self.stance is Stance.PHALANX and self.in_line

    @property
    def speed(self) -> float:
        kinds = {m.kind for r in self.rows for m in r}
        return min((k.speed for k in kinds), default=1.0)

    @property
    def width(self) -> int:
        return max((len(r) for r in self.rows), default=0)

    @property
    def radius(self) -> float:
        """Zeichen- und Abstandsradius in Kacheln."""
        return max(0.4, 0.08 * self.width + 0.12 + 0.07 * (len(self.rows) - 1))

    def count(self, key: str) -> int:
        return sum(1 for r in self.rows for m in r if m.kind.key == key)

    def shield_factor(self) -> float:
        """Anteil der Hopliten in der vorderen Reihe (0..1)."""
        if not self.rows or not self.rows[0]:
            return 0.0
        return sum(1 for m in self.rows[0] if m.kind.hoplite) / len(self.rows[0])

    def has_cavalry(self) -> bool:
        return any(m.kind.cavalry for r in self.rows for m in r)

    def bravery(self) -> float:
        men = [m for r in self.rows for m in r]
        if not men:
            return 1.0
        return sum(m.kind.bravery for m in men) / len(men)

    def summary(self) -> str:
        parts = [f"{self.count(k)}{UNIT_TYPES[k].short}" for k in PLAYER_TYPES if self.count(k)]
        return " ".join(parts) if parts else f"{self.men}"

    # ------------------------------------------------------------ Kampf
    def melee_attack(self) -> float:
        """Angriffspunkte je Sekunde-Einheit: vordere Reihe, Speere der zweiten."""
        if not self.rows:
            return 0.0
        total = sum(m.kind.attack for m in self.rows[0])
        if len(self.rows) > 1:
            total += 0.5 * sum(m.kind.attack for m in self.rows[1] if m.kind.hoplite)
        return total

    def cavalry_share(self) -> float:
        if not self.rows or not self.rows[0]:
            return 0.0
        return sum(1 for m in self.rows[0] if m.kind.cavalry) / len(self.rows[0])

    def ranged_attack(self, engaged: bool) -> float:
        """Fernkampf: hintere Reihen immer, vordere nur ohne Nahkampf."""
        total = 0.0
        for i, row in enumerate(self.rows):
            if i == 0 and engaged:
                continue
            total += sum(m.kind.ranged_attack for m in row)
        return total

    def ranged_range(self) -> float:
        return max((m.kind.ranged_range for r in self.rows for m in r), default=0.0)

    def exposed_row(self, arc: str) -> int:
        """Welche Reihe einen Angriff aus dieser Richtung abbekommt."""
        if not self.rows:
            return 0
        if arc == "rear":
            return len(self.rows) - 1
        if arc == "flank":
            return max(range(len(self.rows)), key=lambda i: len(self.rows[i]))
        return 0

    def take_damage(self, row: int, dmg: float) -> int:
        """Schaden auf eine Reihe; liefert die Zahl der Gefallenen."""
        if not self.rows:
            return 0
        row = min(row, len(self.rows) - 1)
        self.pool[row] += dmg
        fallen = 0
        while self.rows[row] and self.pool[row] >= self.rows[row][0].hp:
            self.pool[row] -= self.rows[row][0].hp
            self.rows[row].pop(0)
            fallen += 1
        if not self.rows[row]:
            # leere Reihe schließen, Rest rückt auf
            del self.rows[row]
            del self.pool[row]
        return fallen
