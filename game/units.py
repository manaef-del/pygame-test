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
    PLAENKELN = "plaenkeln"  # Peltasten: auf Wurfweite heran, werfen, vor Nahkampf ausweichen
    RAUB = "raub"          # Gegner: zieht zu Häusern, plündert
    FLUCHT = "flucht"      # geschlagen, läuft vom Feld


FORMATIONS = ("linie", "o", "keil")
FORMATION_NAMES = {"linie": "Linie", "o": "Kreis", "keil": "Keil"}


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
                       color=config.COLOR_HOPLIT_SCHWER, bravery=0.8, hoplite=True),
    "mittel": UnitType("mittel", "Mittlere Hopliten", "M", attack=1.0, hp=2.2, speed=1.2,
                       color=config.COLOR_HOPLIT_MITTEL, bravery=0.9, hoplite=True),
    "leicht": UnitType("leicht", "Leichte Hopliten", "L", attack=0.9, hp=1.5, speed=1.5,
                       color=config.COLOR_HOPLIT_LEICHT, bravery=1.0, hoplite=True),
    "peltast": UnitType("peltast", "Peltasten", "P", attack=0.6, hp=1.0, speed=1.7,
                        color=config.COLOR_PELTAST, ranged=True, bravery=1.2),
    "reiter": UnitType("reiter", "Reiter", "R", attack=1.4, hp=2.0, speed=3.0,
                       color=config.COLOR_REITER, bravery=0.9, cavalry=True),
    "raeuber": UnitType("raeuber", "Räuber", "X", attack=1.1, hp=2.0, speed=1.5,
                        color=config.COLOR_RAEUBER, bravery=0.8),
}

PLAYER_TYPES = ("schwer", "mittel", "leicht", "peltast", "reiter")
HP_EPS = 1e-6
TIERS = ("Vorn", "Mitte", "Hinten")   # Abschnitte der Aufstellung, vorn nach hinten


@dataclass
class Man:
    kind: UnitType
    hp: float = 0.0
    ammo: int = 0
    tier: int = 0        # Abschnitt der Aufstellung (0 = vorn)
    x: float = 0.0       # eigene Position auf der Karte
    y: float = 0.0
    mounted: bool = False
    bound: bool = False  # im Handgemenge: steht fest, bis die Gruppe ihn wegzieht
    anchor: tuple[float, float] | None = None   # Gruppenzentrum, als er gebunden wurde
    stand: tuple[float, float] | None = None    # sein eigener Platz, als er gebunden wurde
    dodge: float = 0.0   # Ausweichseite (+1/-1), solange jemand im Weg steht; 0 = frei

    def __post_init__(self) -> None:
        if self.hp == 0.0:
            self.hp = self.kind.hp
        if self.kind.ranged and self.ammo == 0:
            self.ammo = config.JAVELINS
        if self.kind.cavalry:
            self.mounted = True

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def speed(self) -> float:
        if self.kind.cavalry and not self.mounted:
            return config.DISMOUNTED_SPEED
        return self.kind.speed

    @property
    def attack(self) -> float:
        if self.kind.cavalry and not self.mounted:
            return config.DISMOUNTED_ATTACK
        return self.kind.attack

    @property
    def wounded(self) -> bool:
        return self.hp < 0.5 * self.kind.hp


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
    contacts: list[int] = field(default_factory=list)   # Gegner, mit denen gekämpft wird (ids)
    contact_since: dict[int, float] = field(default_factory=dict)   # seit wann (Schlachtzeit) je Gegner-id
    assault_slots: list = field(default_factory=list)   # zuletzt zugewiesene Plätze am feindlichen Umriss (Weltkoordinaten)
    still_since: float = 0.0          # seit wann die Gruppe steht (wer später kam, weicht beim Auseinanderrücken)
    waiting: bool = False             # steht hinter einer eigenen Gruppe an, die kämpft oder steht
    leaving: bool = False             # flieht vom Feld, statt sich zu sammeln (aussichtslos)
    disengage_until: float = -1.0     # bis dahin gilt die Gruppe als vom Feind gelöst (verwundbar)
    runup: float = 0.0                # Reiter: Anlauf seit dem letzten Halt oder Kontakt (Kacheln)
    vel: float = 0.0                  # Reiter: augenblickliches Tempo (Kacheln/s), Schwung
    heading: tuple[float, float] = (0.0, -1.0)   # Reiter: Fahrtrichtung
    ride_in: float = 0.0              # Reiter: wie weit sie in den Feind hineingetragen wurden
    face_to: tuple[float, float] | None = None   # befohlene Front, auf die die Gruppe schwenkt
    ring_size: float = 0.0            # Kreis: gewünschter äußerer Halbmesser (0 = so eng wie möglich)
    charge_slow_until: float = -1.0   # nach dem Aufprall: bis dahin langsam
    last_arc: str = ""
    men_start: int = 0
    rout_threshold: float = config.ROUT_THRESHOLD_CITY
    volley_timer: float = 0.0
    engine: str | None = None         # "ram" oder "tower", wenn fertig gebaut
    build_kind: str | None = None     # was gerade gebaut wird
    building: float | None = None     # bisherige Bauzeit
    tower_cell: tuple[int, int] | None = None   # Wallstück, an das der Turm gesetzt wird
    tower_progress: float = 0.0
    loose: bool = False               # Formation aufgelöst (Überqueren der Palisade)
    file: bool = False                # auf dem Wehrgang: eine Reihe längs der Palisade
    formation: str = "linie"          # "linie", "o" (Kreis) oder "keil" (Reiter)
    mode: str = ""                    # freier Angriff je Waffengattung: "", "sturm" (Reiter: Stoß und Lösen)
    hitrun_until: float = -1.0        # Reiter: bis dahin wird vom Feind abgesetzt

    def __post_init__(self) -> None:
        self.rows = [list(r) for r in self.rows if r]
        if self.men_start == 0:
            self.men_start = self.men
        self.place_men()

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
        return self.stance is Stance.PHALANX and self.in_line and not self.loose

    def bound_men(self) -> list[Man]:
        return [m for m in self.all_men() if m.bound]

    def on_slots(self, tolerance: float, share: float = 1.0) -> bool:
        """Steht (fast) jeder Mann auf seinem Platz? ``share`` erlaubt ein paar Nachzügler."""
        slots = self.slots()
        if not slots:
            return False
        there = sum(1 for m, (sx, sy) in slots if math.hypot(m.x - sx, m.y - sy) <= tolerance)
        return there >= share * len(slots)

    def surface_distance(self, p: tuple[float, float]) -> float:
        """Abstand eines Punkts zur Gruppe: zum Formationsrechteck, oder bei
        aufgelöster Formation zum nächsten einzelnen Mann."""
        if self.loose:
            men = self.all_men()
            if men:
                return max(0.0, min(math.hypot(m.x - p[0], m.y - p[1]) for m in men) - 0.1)
        return self.rect_distance(p)

    def remount(self, horses: int) -> int:
        """Abgesessene Reiter steigen wieder auf; liefert die Zahl der bestiegenen Pferde."""
        riders = [m for m in self.all_men() if m.kind.cavalry and not m.mounted]
        n = min(horses, len(riders))
        for m in riders[:n]:
            m.mounted = True
        return n

    @property
    def speed(self) -> float:
        base = min((m.speed for m in self.all_men()), default=1.0)
        factor = {"ram": config.RAM_SPEED_FACTOR, "tower": config.TOWER_SPEED_FACTOR}.get(self.engine, 1.0)
        return base * factor

    def mounted_men(self) -> list[Man]:
        return [m for m in self.all_men() if m.kind.cavalry and m.mounted]

    def dismount(self) -> int:
        """Reiter sitzen ab; liefert die Zahl der zurückgelassenen Pferde."""
        riders = self.mounted_men()
        for m in riders:
            m.mounted = False
        return len(riders)

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

    def layers(self) -> list[list[Man]]:
        """Schichten für den Kreis: Fußvolk außen, Reiter in der Mitte,
        Peltasten innen. In jeder Schicht wechseln die Reihen ab (ein Mann der
        ersten, einer der zweiten, einer der dritten, ...), so dass jede
        Rüstungsstufe gleichmäßig über die Front verteilt ist."""
        per_layer: tuple[list[list[Man]], ...] = ([], [], [])
        for row in self.rows:
            parts: tuple[list[Man], ...] = ([], [], [])
            for m in row:
                parts[2 if m.kind.ranged else (1 if m.kind.cavalry else 0)].append(m)
            for layer, part in zip(per_layer, parts):
                if part:
                    layer.append(part)
        out: list[list[Man]] = []
        for rows in per_layer:
            if not rows:
                continue
            merged = [r[i] for i in range(max(len(r) for r in rows)) for r in rows if i < len(r)]
            out.append(merged)
        return out

    def ring_radii(self) -> list[float]:
        """Halbmesser je Schicht, von außen nach innen; die äußere ist so weit,
        dass alle inneren Ringe mit Reihenabstand hineinpassen."""
        need = [max(0.12, len(layer) * config.MAN_SPACING / (2 * math.pi)) for layer in self.layers()]
        if not need:
            return [0.35]
        outer = max(0.35, self.ring_size, max(r + i * config.ROW_SPACING for i, r in enumerate(need)))
        return [outer - i * config.ROW_SPACING for i in range(len(need))]

    def ring_minimum(self) -> float:
        """Der engste Kreis, in dem alle Schichten Platz haben."""
        size, self.ring_size = self.ring_size, 0.0
        try:
            return self.ring_radii()[0]
        finally:
            self.ring_size = size

    def ring_radius(self) -> float:
        return self.ring_radii()[0]

    def wedge_rows(self) -> int:
        k = 1
        while k * (k + 1) // 2 < self.men:
            k += 1
        return k

    @property
    def half_w(self) -> float:
        """Halbe Breite der Formation in Kacheln (entlang der Front)."""
        if self.formation == "o":
            return self.ring_radius() + 0.08
        if self.formation == "keil":
            return max(0.2, self.wedge_rows() * config.MAN_SPACING / 2 + 0.08)
        return max(0.2, self.width * config.MAN_SPACING / 2 + 0.08)

    @property
    def half_d(self) -> float:
        """Halbe Tiefe der Formation in Kacheln (in Blickrichtung)."""
        if self.formation == "o":
            return self.ring_radius() + 0.08
        if self.formation == "keil":
            return max(0.2, self.wedge_rows() * config.ROW_SPACING / 2 + 0.08)
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

    def arc_to(self, p: tuple[float, float]) -> str:
        """Von wo ein Punkt die Formation trifft: "front" oder "rear", wenn er
        innerhalb der Breite der Front liegt, sonst "flank" (neben den Enden).
        Gemessen am Rechteck, nicht am Winkel vom Zentrum: bei einer breiten,
        flachen Linie steht ein Gegner vor ihrem Ende vor der Front, nicht daneben."""
        along, forward = self.local(p)
        if self.formation == "o":
            return "front"                     # der Kreis hat keine Flanke und keinen Rücken
        if abs(along) <= self.half_w + config.ARC_TOLERANCE:
            return "front" if forward >= 0 else "rear"
        if forward > self.half_d + config.FLANK_DEPTH:
            return "front"                     # weit vor dem Ende: noch vor der Speerwand
        return "flank"

    def rect_distance(self, p: tuple[float, float]) -> float:
        """Abstand eines Punkts zum Rechteck der Formation (0 = innen); der Kreis
        zählt als Kreis, nicht als sein umschriebenes Rechteck."""
        if self.formation == "o":
            return max(0.0, math.hypot(p[0] - self.x, p[1] - self.y) - self.half_w)
        along, forward = self.local(p)
        ox = max(0.0, abs(along) - self.half_w)
        oy = max(0.0, abs(forward) - self.half_d)
        return math.hypot(ox, oy)

    def corners(self) -> list[tuple[float, float]]:
        return self.corners_at(self.pos, self.facing)

    def outline(self) -> list[tuple[float, float]]:
        """Randpunkte für Abstandsprüfungen: die Ecken, beim Kreis acht Punkte auf ihm."""
        if self.formation == "o":
            r = self.half_w
            return [(self.x + r * math.cos(k * math.pi / 4), self.y + r * math.sin(k * math.pi / 4)) for k in range(8)]
        return self.corners()

    def corners_at(self, centre: tuple[float, float], facing: tuple[float, float]) -> list[tuple[float, float]]:
        """Die Ecken der Formation um ein beliebiges Zentrum (etwa das Ziel)."""
        cx, cy = centre
        fx, fy = facing
        ax, ay = -fy, fx
        w, d = self.half_w, self.half_d
        return [
            (cx + ax * w + fx * d, cy + ay * w + fy * d),
            (cx - ax * w + fx * d, cy - ay * w + fy * d),
            (cx - ax * w - fx * d, cy - ay * w - fy * d),
            (cx + ax * w - fx * d, cy + ay * w - fy * d),
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
        """Reihen neu bilden: Abschnitte bleiben vorn/hinten, Breite ändert sich.
        Die Männer behalten ihre Position und laufen zu ihren neuen Plätzen."""
        self.rows = arrange(self.all_men(), width)

    def slots(self) -> list[tuple[Man, tuple[float, float]]]:
        """Platz jedes Mannes in der Formation (Weltkoordinaten)."""
        return self.slots_at(self.pos, self.facing, self.file)

    def slots_at(self, centre: tuple[float, float], facing: tuple[float, float],
                 file: bool = False) -> list[tuple[Man, tuple[float, float]]]:
        """Die Plätze der Formation um ein beliebiges Zentrum; als ``file`` eine
        einzelne Reihe längs der Palisade (für den Wehrgang)."""
        cx, cy = centre
        out = []
        if file:
            men = self.all_men()
            n = len(men)
            for i, man in enumerate(men):
                out.append((man, (cx + (i - (n - 1) / 2) * config.MAN_SPACING, cy)))
            return out
        fx, fy = facing
        if self.formation == "o":
            for k, (layer, r) in enumerate(zip(self.layers(), self.ring_radii())):
                n = len(layer)
                for i, man in enumerate(layer):
                    a = 2 * math.pi * (i + 0.5 * k) / max(1, n)    # innere Ringe auf Lücke
                    out.append((man, (cx + math.cos(a) * r, cy + math.sin(a) * r)))
            return out
        if self.formation == "keil":
            men = self.all_men()
            k = self.wedge_rows()
            depth = k * config.ROW_SPACING
            i = 0
            for r in range(k):
                width = min(r + 1, len(men) - i)
                forward = depth / 2 - (r + 0.5) * config.ROW_SPACING
                for j in range(width):
                    side = (j - (width - 1) / 2) * config.MAN_SPACING
                    out.append((men[i], (cx + fx * forward - fy * side, cy + fy * forward + fx * side)))
                    i += 1
                if i >= len(men):
                    break
            return out
        n_rows = len(self.rows)
        for r, row in enumerate(self.rows):
            forward = ((n_rows - 1) / 2 - r) * config.ROW_SPACING
            n = len(row)
            for i, man in enumerate(row):
                side = (i - (n - 1) / 2) * config.MAN_SPACING
                out.append((man, (cx + fx * forward - fy * side, cy + fy * forward + fx * side)))
        return out

    def place_men(self) -> None:
        """Alle Männer sofort auf ihre Plätze setzen."""
        for man, (sx, sy) in self.slots():
            man.x, man.y = sx, sy

    # ------------------------------------------------------------ Kampf
    def melee_attack(self) -> float:
        """Angriffspunkte: vordere Reihe, dazu Speere der zweiten. Im Kreis kämpft
        jeder nach außen, aber ohne den Rückhalt der Glieder."""
        return self.melee_attack_against(lambda m: 0.0, float("inf"))

    def melee_attack_against(self, distance, reach: float, arc: str = "front") -> float:
        """Angriffspunkte gegen einen bestimmten Gegner: Es kämpft nur, wer ihn
        erreicht (``distance`` misst je Mann den Abstand zum Gegner). Vorn die
        vordere Reihe in Reichweite, dazu die Speere der zweiten dahinter; an
        Flanke und Rücken (``arc``) dreht sich jeder Mann in Reichweite um und
        kämpft einzeln, gleich in welcher Reihe er steht; im Kreis jeder in
        Reichweite, ohne den Rückhalt der Glieder. Erreicht ihn niemand, halten
        die zwei nächsten Männer notdürftig den Kontakt."""
        if not self.rows:
            return 0.0
        if self.formation == "o":
            near = [m for m in self.all_men() if distance(m) <= reach]
            return config.RING_ATTACK_SHARE * sum(m.attack for m in near)
        if arc != "front":
            near = [m for m in self.all_men() if distance(m) <= reach]
            if not near:
                near = sorted(self.all_men(), key=distance)[:2]
                return 0.5 * sum(m.attack for m in near)
            return sum(m.attack for m in near)
        front = [m for m in self.rows[0] if distance(m) <= reach]
        total = sum(m.attack for m in front)
        if len(self.rows) > 1:
            total += config.SECOND_ROW_SPEARS * sum(m.attack for m in self.rows[1]
                                                    if m.kind.hoplite and distance(m) <= reach + config.ROW_SPACING)
        if not front:
            nearest = sorted(self.rows[0], key=distance)[:2]
            total = 0.5 * sum(m.attack for m in nearest)
        return total

    def arm(self) -> str:
        """Waffengattung der Mehrheit: "hopliten", "peltasten" oder "reiter"."""
        if self.share(lambda m: m.kind.cavalry) >= 0.5:
            return "reiter"
        if self.share(lambda m: m.kind.ranged) >= 0.5:
            return "peltasten"
        return "hopliten"

    def formation_options(self) -> tuple[str, ...]:
        """Linie immer; mit Fußvolk auch den Kreis (Reiter und Peltasten darin
        in inneren Ringen), reine Reiter den Keil, reine Peltasten den Kreis."""
        men = self.all_men()
        if any(not m.kind.cavalry and not m.kind.ranged for m in men):
            return ("linie", "o")
        if men and all(m.kind.cavalry for m in men):
            return ("linie", "keil")
        return ("linie", "o")

    def cavalry_share(self) -> float:
        """Anteil berittener Männer in der vorderen Reihe."""
        if not self.rows or not self.rows[0]:
            return 0.0
        return sum(1 for m in self.rows[0] if m.kind.cavalry and m.mounted) / len(self.rows[0])

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

    def take_damage(self, row: int, dmg: float, rng=None) -> int:
        """Schaden auf eine Reihe, in Häppchen auf einzelne Männer verteilt;
        liefert die Zahl der Gefallenen."""
        if not self.rows or dmg <= 0:
            return 0
        row = min(row, len(self.rows) - 1)
        return self.take_damage_men(self.rows[row], dmg, rng)

    def take_damage_men(self, men: list[Man], dmg: float, rng=None) -> int:
        """Schaden in Häppchen auf einzelne Männer. Der Druck sammelt sich: von zwei
        zufällig gewählten Männern trifft es den schon angeschlagenen, so fallen
        Männer nach und nach statt alle auf einmal."""
        pick = rng.randrange if rng is not None else (lambda n: 0)
        while dmg > 0:
            living = [m for m in men if m.hp > HP_EPS]
            if not living:
                break
            q = min(config.DAMAGE_QUANTUM, dmg)
            a = living[pick(len(living))]
            c = living[pick(len(living))]
            (a if a.hp <= c.hp else c).hp -= q
            dmg -= q
        return self.bury()

    def hit_man(self, man: Man, dmg: float) -> int:
        """Ein bestimmter Mann wird getroffen (Speer); liefert 1, wenn er fällt."""
        man.hp -= dmg
        return self.bury()

    def bury(self) -> int:
        """Gefallene aus den Reihen nehmen; die Reihe dahinter rückt sofort in die
        Lücke nach, so dass die Front voll bleibt und die letzte Reihe schrumpft."""
        fallen = 0
        width = self.width
        gaps_per_row: list[list[int]] = []
        for row in self.rows:                                # erst alle Gefallenen heraus ...
            gaps = [j for j, m in enumerate(row) if m.hp <= HP_EPS]
            fallen += len(gaps)
            row[:] = [m for m in row if m.hp > HP_EPS]
            gaps_per_row.append(gaps)
        for i, gaps in enumerate(gaps_per_row):              # ... dann an derselben Stelle nachrücken
            for j in gaps:
                self._step_up(i, j)
        for i in range(len(self.rows) - 1):                  # dahinter schließen sich die Reihen wieder
            while len(self.rows[i]) < width and any(self.rows[i + 1:]):
                self._step_up(i, len(self.rows[i]) // 2)
        self.rows = [r for r in self.rows if r]
        return fallen

    def _step_up(self, i: int, j: int) -> None:
        """Ein Mann aus der nächsten besetzten Reihe hinter ``i`` tritt an Stelle ``j``."""
        for k in range(i + 1, len(self.rows)):
            behind = self.rows[k]
            if behind:
                man = behind.pop(min(j, len(behind) - 1))
                self.rows[i].insert(min(j, len(self.rows[i])), man)
                return
