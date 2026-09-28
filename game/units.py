"""Truppentypen und der Lochos, die kleinste Kampfeinheit.

Die Typen folgen den Hausstufen aus dem Apoikia-Register: Theten aus
Hütten, Leichte aus Hofhäusern, Hopliten aus Säulenhöfen, Reiter aus
Stadthäusern. Räuber sind der Standardgegner.
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
    ANGRIFF = "angriff"    # freier Angriff, verfolgt
    RAUB = "raub"          # Gegner: zieht zu Häusern, plündert
    FLUCHT = "flucht"      # geschlagen, läuft vom Feld


@dataclass(frozen=True)
class UnitType:
    key: str
    name: str
    attack: float
    defense: float
    speed: float                  # Kacheln pro Sekunde
    men: int = config.LOCHOS_MEN
    ranged_range: float = 0.0     # 0 = kein Fernkampf
    ranged_attack: float = 0.0
    bravery: float = 1.0          # Moralverlust-Faktor, kleiner = tapferer
    rout_threshold: float = 0.3
    can_phalanx: bool = True
    cavalry: bool = False


UNIT_TYPES: dict[str, UnitType] = {
    "hoplit": UnitType("hoplit", "Hopliten", attack=1.0, defense=1.6, speed=1.2, bravery=0.7),
    "leichter": UnitType("leichter", "Leichte", attack=0.8, defense=1.0, speed=1.6, bravery=1.0),
    "thet": UnitType(
        "thet", "Theten", attack=0.5, defense=0.7, speed=1.6,
        ranged_range=3.0, ranged_attack=0.35, bravery=1.2, can_phalanx=False,
    ),
    "hippeus": UnitType(
        "hippeus", "Reiter", attack=1.2, defense=1.0, speed=3.0, men=4,
        bravery=0.9, can_phalanx=False, cavalry=True,
    ),
    "raeuber": UnitType(
        "raeuber", "Räuber", attack=0.9, defense=0.9, speed=1.5,
        bravery=1.3, rout_threshold=0.4,
    ),
}


@dataclass
class Lochos:
    """Etwa acht Mann, die zusammen laufen und zusammen kämpfen."""

    id: int
    side: Side
    kind: UnitType
    x: float
    y: float
    facing: tuple[float, float] = (0.0, -1.0)
    men: int = 0
    men_start: int = 0
    morale: float = 1.0
    stance: Stance = Stance.HALTEN
    target: tuple[float, float] | None = None
    waypoints: list[tuple[float, float]] = field(default_factory=list)
    in_line: bool = False          # in der Phalanx angekommen
    casualties: float = 0.0        # angesammelter Bruchteil eines Mannes
    withdrawn: bool = False        # hat das Feld verlassen
    engaged: bool = False          # in diesem Schritt im Nahkampf
    last_arc: str = ""             # woher der letzte Treffer kam (Anzeige)

    def __post_init__(self) -> None:
        if self.men == 0:
            self.men = self.kind.men
        if self.men_start == 0:
            self.men_start = self.men

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def alive(self) -> bool:
        return self.men > 0 and not self.withdrawn

    @property
    def fighting(self) -> bool:
        return self.alive and self.stance is not Stance.FLUCHT

    @property
    def in_phalanx(self) -> bool:
        return self.stance is Stance.PHALANX and self.in_line
