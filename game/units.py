"""Truppentypen, einzelne Männer und die Gruppe (Lochos).

Eine Gruppe besteht aus einer geordneten Liste von Männern (vorn nach
hinten) und einer Breite. Daraus ergeben sich die Reihen: die vordere
Reihe kämpft im Nahkampf, Hopliten der zweiten Reihe stechen über die
Front, Peltasten in hinteren Reihen werfen. Getroffen wird die Reihe,
die dem Angreifer zugewandt ist. Zieht der Spieler die Gruppe breiter
oder schmaler auf, werden die Reihen neu gebildet.
"""

from __future__ import annotations

import math
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
    ranged: bool = False          # wirft Speere
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
    "peltast": UnitType("peltast", "Peltasten", "P", attack=0.6, hp=1.0, speed=1.7,
                        color=config.COLOR_PELTAST, ranged=True, bravery=1.1),
    "reiter": UnitType("reiter", "Reiter", "R", attack=1.4, hp=2.0, speed=3.0,
                       color=config.COLOR_REITER, bravery=0.8, cavalry=True),
    "raeuber": UnitType("raeuber", "Räuber", "X", attack=1.0, hp=1.8, speed=1.5,
                        color=config.COLOR_RAEUBER, bravery=1.3),
}

PLAYER_TYPES = ("schwer", "mittel", "leicht", "peltast", "reiter")
TIERS = ("Vorn", "Mitte", "Hinten")   # Abschnitte der Aufstellung, vorn nach hinten


@dataclass
class Man:
    kind: UnitType
    hp: float = 0.0
    ammo: int = 0
    tier: int = 0        # Abschnitt der Aufstellung (0 = vorn)

    def __post_init__(self) -> None:
        if self.hp == 0.0:
            self.hp = self.kind.hp
        if self.kind.ranged and self.ammo == 0:
            self.ammo = config.JAVELINS


def default_width(n: int) -> int:
    """Breite, wenn niemand eine vorgibt: etwa drei Reihen tief."""
    return max(1, min(n, math.ceil(n / 3)))


def chunk(men: list[Man], width: int) -> list[list[Man]]:
    width = max(1, width)
    return [men[i:i + width] for i in range(0, len(men), width)]


def interleave(row: list[Man]) -> list[Man]:
    """Teilen sich mehrere Abschnitte eine Reihe, wechseln sie sich ab.

    Jeder Mann bekommt einen Platz zwischen 0 und 1 gemäß seiner Position
    innerhalb seines Abschnitts; sortiert nach diesem Platz verteilen sich
    die Abschnitte gleichmäßig über die Reihe.
    """
    by_tier: dict[int, list[Man]] = {}
    for m in row:
        by_tier.setdefault(m.tier, []).append(m)
    if len(by_tier) <= 1:
        return list(row)
    keyed = []
    for tier, ms in by_tier.items():
        for i, m in enumerate(ms):
            keyed.append(((i + 0.5) / len(ms), tier, m))
    keyed.sort(key=lambda t: (t[0], t[1]))
    return [m for _, _, m in keyed]


def arrange(men: list[Man], width: int) -> list[list[Man]]:
    """Reihen bilden: vorderer Abschnitt zuerst, gemischte Reihen abwechselnd."""
    ordered = sorted(men, key=lambda m: m.tier)   # stabil: Reihenfolge im Abschnitt bleibt
    return [interleave(r) for r in chunk(ordered, width)]


@dataclass
class Lochos:
    """Eine Gruppe: Reihen von Männern, die zusammen handeln."""

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
    in_line: bool = False             # in der Formation angekommen
    withdrawn: bool = False           # hat das Feld verlassen
    engaged: bool = False             # in diesem Schritt im Nahkampf
    last_arc: str = ""
    men_start: int = 0
    pool: list[float] = field(default_factory=list)  # angesammelter Schaden je Reihe
    rout_threshold: float = 0.3
    volley_timer: float = 0.0
    engine: str | None = None         # "ram" oder "tower", wenn fertig gebaut
    build_kind: str | None = None     # was gerade gebaut wird
    building: float | None = None     # bisherige Bauzeit
    tower_cell: tuple[int, int] | None = None   # Wallstück, an das der Turm gesetzt wird
    tower_progress: float = 0.0

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
        base = min((k.speed for k in kinds), default=1.0)
        factor = {"ram": config.RAM_SPEED_FACTOR, "tower": config.TOWER_SPEED_FACTOR}.get(self.engine, 1.0)
        return base * factor

    def wall_capable(self) -> bool:
        """Nur reine Peltastengruppen steigen auf den Wehrgang."""
        men = self.all_men()
        return bool(men) and all(m.kind.ranged for m in men)

    @property
    def width(self) -> int:
        return max((len(r) for r in self.rows), default=0)

    @property
    def depth(self) -> int:
        return len(self.rows)

    @property
    def half_w(self) -> float:
        """Halbe Breite der Formation in Kacheln (entlang der Front)."""
        return max(0.2, self.width * config.MAN_SPACING / 2 + 0.08)

    @property
    def half_d(self) -> float:
        """Halbe Tiefe der Formation in Kacheln (in Blickrichtung)."""
        return max(0.2, self.depth * config.ROW_SPACING / 2 + 0.08)

    @property
    def radius(self) -> float:
        """Umkreis der Formation, für grobe Reichweitenprüfungen."""
        return math.hypot(self.half_w, self.half_d)

    @property
    def core(self) -> float:
        """Kleinster Halbmesser, für Abstandhalten."""
        return min(self.half_w, self.half_d)

    def local(self, p: tuple[float, float]) -> tuple[float, float]:
        """Punkt in Formationskoordinaten: (entlang der Front, in Blickrichtung)."""
        fx, fy = self.facing
        dx, dy = p[0] - self.x, p[1] - self.y
        along = dx * (-fy) + dy * fx
        forward = dx * fx + dy * fy
        return (along, forward)

    def rect_distance(self, p: tuple[float, float]) -> float:
        """Abstand eines Punkts zum Rechteck der Formation (0 = innen)."""
        along, forward = self.local(p)
        ox = max(0.0, abs(along) - self.half_w)
        oy = max(0.0, abs(forward) - self.half_d)
        return math.hypot(ox, oy)

    def corners(self) -> list[tuple[float, float]]:
        fx, fy = self.facing
        ax, ay = -fy, fx
        w, d = self.half_w, self.half_d
        return [
            (self.x + ax * w + fx * d, self.y + ay * w + fy * d),
            (self.x - ax * w + fx * d, self.y - ay * w + fy * d),
            (self.x - ax * w - fx * d, self.y - ay * w - fy * d),
            (self.x + ax * w - fx * d, self.y + ay * w - fy * d),
        ]

    def all_men(self) -> list[Man]:
        return [m for r in self.rows for m in r]

    def count(self, key: str) -> int:
        return sum(1 for m in self.all_men() if m.kind.key == key)

    def share(self, pred) -> float:
        men = self.all_men()
        return sum(1 for m in men if pred(m)) / len(men) if men else 0.0

    def shield_factor(self) -> float:
        """Anteil der Hopliten in der vorderen Reihe (0..1)."""
        if not self.rows or not self.rows[0]:
            return 0.0
        return sum(1 for m in self.rows[0] if m.kind.hoplite) / len(self.rows[0])

    def bravery(self) -> float:
        men = self.all_men()
        return sum(m.kind.bravery for m in men) / len(men) if men else 1.0

    def ammo(self) -> int:
        return sum(m.ammo for m in self.all_men())

    def summary(self) -> str:
        parts = [f"{self.count(k)}{UNIT_TYPES[k].short}" for k in PLAYER_TYPES if self.count(k)]
        return " ".join(parts) if parts else f"{self.men}"

    # -------------------------------------------------------- Formation
    def reform(self, width: int) -> None:
        """Reihen neu bilden: Abschnitte bleiben vorn/hinten, Breite ändert sich."""
        self.rows = arrange(self.all_men(), width)
        self.pool = [0.0] * len(self.rows)

    # ------------------------------------------------------------ Kampf
    def melee_attack(self) -> float:
        """Angriffspunkte: vordere Reihe, dazu Speere der zweiten."""
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

    def throwers(self, engaged: bool) -> list[Man]:
        """Wer wirft: hintere Reihen immer, die vordere nur ohne Nahkampf."""
        out: list[Man] = []
        for i, row in enumerate(self.rows):
            if i == 0 and engaged:
                continue
            out.extend(m for m in row if m.kind.ranged and m.ammo > 0)
        return out

    def exposed_row(self, arc: str) -> int:
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
            del self.rows[row]
            del self.pool[row]
        return fallen
