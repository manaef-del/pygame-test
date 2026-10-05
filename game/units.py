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
    dodge: float = 0.0   # Ausweichseite (+1/-1); 0 = noch keine gewählt
    dodge_at: float = -9.0   # wann er zuletzt ausgewichen ist (die Seite gilt noch eine Weile)
    wp: tuple[float, float] | None = None       # eigener Wegpunkt auf dem Weg zum Platz
    wp_until: float = -1.0                      # bis dahin gilt der Wegpunkt
    stall: float = 0.0                          # Sekunden, die er auf seinem Weg nicht vorankommt
    leader: bool = False  # der Anführer: kämpft mit, hält viel mehr aus
    show_dx: float = 0.0  # nur fürs Bild: so weit drängt er gerade von seiner Stelle zum Gegner (Gerangel)
    show_dy: float = 0.0
    jostle_foe: "Man | None" = None   # nur fürs Bild: der Gegner, auf den er gerade drängt ...
    jostle_until: float = -1.0        # ... und wie lange er bei ihm bleibt, ehe er neu wählt
    sx: float | None = None  # nur fürs Bild: geglättete Stelle (ruhig statt zitternd), None = noch keine
    sy: float = 0.0
    rx: float = 0.0          # ... und seine geglättete Lage in der Gruppe (zur Mitte), für die das Bild gilt
    ry: float = 0.0
    ref_id: int = -1         # (die Gruppe, auf deren Mitte sich rx, ry beziehen; -1: aufgelöst)
    flash: float = 0.0    # nur fürs Bild: so lange (Sekunden) blitzt er nach einem Treffer noch auf
    hurt: float = 0.0     # nur fürs Bild: Schaden seit dem letzten Aufblitzen
    rest_slot: tuple[float, float] | None = None   # sein Platz, als er zuletzt näher kam ...
    rest_best: float = 0.0                          # ... wie nah er ihm da war ...
    rest_since: float = 0.0                         # ... und seit wann er nicht näher kommt (dann bleibt er stehen)
    vx: float = 0.0       # geschätzte Geschwindigkeit (Kacheln je Sekunde): danach zielen Werfer vor
    vy: float = 0.0
    mvx: float = 0.0      # seine Schrittgeschwindigkeit (Kacheln je Sekunde): ein Körper mit Masse, der nicht springt
    mvy: float = 0.0
    sfx: float = 0.0      # nur fürs Bild: wohin er schaut (geglättet) – Front der Gruppe, sein Gegner oder sein Weg
    sfy: float = -1.0

    def __post_init__(self) -> None:
        if self.hp == 0.0:
            self.hp = self.kind.hp * (config.LEADER_HP_FACTOR if self.leader else 1.0)
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

    def felt(self, dmg: float) -> None:
        """Nur fürs Bild: hat sich ein spürbarer Treffer angesammelt, blitzt er auf."""
        self.hurt += dmg
        if self.hurt >= config.HIT_FLASH_SHARE * self.kind.hp:
            self.hurt = 0.0
            self.flash = config.HIT_FLASH

    @property
    def wounded(self) -> bool:
        full = self.kind.hp * (config.LEADER_HP_FACTOR if self.leader else 1.0)
        return self.hp < 0.5 * full


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


def assign_min_cost(cost: list[list[float]]) -> list[int]:
    """Zuordnung mit kleinster Gesamtsumme (ungarische Methode, quadratische Matrix):
    Ergebnis[i] = Spalte für Zeile i."""
    n = len(cost)
    INF = float("inf")
    u = [0.0] * (n + 1)
    v = [0.0] * (n + 1)
    p = [0] * (n + 1)            # p[j]: Zeile, die Spalte j hat (1-basiert; 0 = frei)
    way = [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta, j1 = INF, 0
            for j in range(1, n + 1):
                if used[j]:
                    continue
                cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                if cur < minv[j]:
                    minv[j], way[j] = cur, j0
                if minv[j] < delta:
                    delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    out = [0] * n
    for j in range(1, n + 1):
        if p[j]:
            out[p[j] - 1] = j - 1
    return out


def fit_men(rows: list[list[Man]], centre: tuple[float, float], facing: tuple[float, float],
            gap: float, row_gap: float, origin: tuple[float, float] | None = None,
            old_facing: tuple[float, float] | None = None) -> list[list[Man]]:
    """Die Männer so auf die Plätze der Aufstellung (Mitte, Front) verteilen, dass die Wege
    zusammen am kürzesten sind: Jeder geht etwa dorthin, wo er schon steht, und keiner kreuzt
    den anderen. Welche Plätze einem Abschnitt gehören, bleibt; getauscht wird nur innerhalb.
    Schwenkt die Gruppe dabei (``old_facing`` → ``facing``, um ``origin``), zählt, wo jeder
    nach dem Schwenk stünde: Die Männer drehen mit der Formation mit, statt quer durch sie zu
    laufen."""
    fx, fy = facing
    ax, ay = -fy, fx
    ox, oy = origin or centre
    ofx, ofy = old_facing or facing
    c, s = ofx * fx + ofy * fy, ofx * fy - ofy * fx            # Drehung alte Front -> neue Front
    where = {}
    for row in rows:
        for m in row:
            dx, dy = m.x - ox, m.y - oy
            where[id(m)] = (centre[0] + dx * c - dy * s, centre[1] + dx * s + dy * c)
    n_rows = len(rows)
    by_tier: dict[int, list[tuple[int, int]]] = {}            # Abschnitt -> seine Plätze (Reihe, Stelle)
    for r, row in enumerate(rows):
        for i, m in enumerate(row):
            by_tier.setdefault(m.tier, []).append((r, i))
    out = [list(row) for row in rows]
    for places in by_tier.values():
        men = [rows[r][i] for r, i in places]
        if len(men) < 2:
            continue
        spots = []
        for r, i in places:
            forward = ((n_rows - 1) / 2 - r) * row_gap
            side = (i - (len(rows[r]) - 1) / 2) * gap
            spots.append((centre[0] + fx * forward + ax * side, centre[1] + fy * forward + ay * side))
        cost = [[(where[id(m)][0] - sx) ** 2 + (where[id(m)][1] - sy) ** 2 for sx, sy in spots] for m in men]
        for k, j in enumerate(assign_min_cost(cost)):
            r, i = places[j]
            out[r][i] = men[k]
    return out


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
    fell_at: list = field(default_factory=list)   # nur fürs Bild: wo seit dem letzten Takt Männer gefallen sind
    assault_slots: list = field(default_factory=list)   # zuletzt zugewiesene Plätze am feindlichen Umriss (Weltkoordinaten)
    still_since: float = 0.0          # seit wann die Gruppe steht (wer später kam, weicht beim Auseinanderrücken)
    waiting: bool = False             # steht hinter einer eigenen Gruppe an, die kämpft oder steht
    leaving: bool = False             # flieht vom Feld, statt sich zu sammeln (aussichtslos)
    target_checked: tuple | None = None   # Ziel, das schon auf eigene ruhende Gruppen geprüft wurde
    target_cleared: tuple | None = None   # (befohlenes Ziel, wohin es verrückt wurde): kommt derselbe Befehl wieder, gilt dasselbe
    disengage_until: float = -1.0     # bis dahin gilt die Gruppe als vom Feind gelöst (verwundbar)
    runup: float = 0.0                # Reiter: Anlauf seit dem letzten Halt oder Kontakt (Kacheln)
    vel: float = 0.0                  # Reiter: augenblickliches Tempo (Kacheln/s), Schwung
    last_pos: tuple[float, float] | None = None   # Mitte beim letzten Takt der Männerbewegung (daraus die Gruppengeschwindigkeit)
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
    ram_gate: int | None = None                  # Festung: Nummer des Tores, das der Rammbock angeht
    wall_layout: object = field(default=None, repr=False, compare=False)   # Festung: Plätze auf dem Wehrgang
    tower_progress: float = 0.0
    loose: bool = False               # aufgelöst: jeder Mann geht für sich an seinen Platz in der Zielaufstellung
    loose_why: str = ""               # warum: "wall" (über den Wall), "tor" (durchs Tor), "eigene" (um eigene herum), "" (formiert sich)
    dest: tuple[float, float] | None = None          # Mitte der Zielaufstellung, solange aufgelöst
    dest_facing: tuple[float, float] | None = None   # ihre Front
    idle_block: bool = False          # im letzten Schritt von einer ruhenden eigenen Gruppe aufgehalten
    blocked_by: int | None = None     # die eigene Gruppe, hinter der man zuletzt anstand
    over_wall: bool = False           # aufgelöst, um über den Wall zu steigen (für die Meldungen)
    via: tuple | None = None          # (Übergang, Ziel): zu diesem Ziel über diesen Turm oder diese Leiter, nicht durchs Tor
    flee_x: float | None = None       # wohin (x) die Flucht führt, beim Beginn der Flucht festgelegt
    muster: tuple | None = None       # (Mitte, Front, halbe Ausdehnung x/y) des Sammelplatzes hinter dem Wall, bis die Gruppe sich dort geschlossen hat
    muster_since: float = -1.0        # seit wann alle Männer drüben sind und nur noch gesammelt wird
    detour_side: float = 0.0          # Seite (+1/-1 quer zum Weg), auf der der Block um eigene Gruppen herumgeht; 0 = frei
    detour_on: bool = False           # wich im letzten Schritt einer eigenen Gruppe aus
    detour_until: float = -1.0        # bis dahin bleibt die Seite gemerkt, auch wenn gerade nichts im Weg steht
    flank_leg: int = 0                # Plänkler auf dem Weg zur offenen Flanke: 1 = erst seitlich entlang, 2 = nun zur Flanke
    flank_since: float = -1.0         # ... seit wann (gewechselt wird frühestens nach FLANK_LEG_TIME)
    retreat_until: float = -1.0       # Plänkler weichen bis dahin zurück, ohne neu zu entscheiden
    detour_wp: tuple[float, float] | None = None   # der zuletzt genommene Umwegpunkt (gilt noch kurz, auch wenn frei scheint)
    file: bool = False                # auf dem Wehrgang: eine Reihe längs der Palisade
    formation: str = "linie"          # "linie", "o" (Kreis) oder "keil" (Reiter)
    mode: str = ""                    # freier Angriff je Waffengattung: "", "sturm" (Reiter: Stoß und Lösen)
    drill: str = "phalanx"            # Modus der Hopliten: "locker" oder "phalanx" (andere Gattungen: ohne Wirkung)
    full_width: int | None = None     # vor Tor oder Gasse schmaler geworden: so breit war die Front vorher
    pace: float | None = None         # im Verband: so schnell wie die langsamste Gruppe (bis zum nächsten Befehl)
    free_attack: bool = False         # im freien Angriff (Sturm, Plänkeln, Sturmangriff)
    stormed: bool = False             # ... und schon im Handgemenge gewesen
    hunt_home: tuple[float, float] | None = None   # Reiter auf der Jagd: hierher kehren sie zurück, wenn nichts zu jagen ist
    stay_loose: bool = False          # nach einem Stau aufgelöst: erst an den Plätzen wieder Block
    stay_since: float = 0.0
    centre_level: str | None = None   # aufgelöst: auf welcher Wallseite die Gruppe zählt (wechselt erst bei klarer Mehrheit)
    shifted_to: tuple[float, float] | None = None     # Ziel, zu dem sich die lockere Gruppe schon Mann für Mann umgestellt hat
    straggled_at: tuple[float, float] | None = None   # Ziel, für das schon einmal wegen Nachzüglern aufgelöst wurde
    jam_since: float = -1.0           # seit wann der Block mit Ziel nicht vom Fleck kommt
    jam_at: tuple[float, float] = (0.0, 0.0)
    lag_since: float = -1.0           # seit wann die Gruppe am Ziel steht, ihre Männer aber nicht an ihre Plätze kommen
    _hoplite_key: tuple | None = field(default=None, repr=False, compare=False)
    _hoplite_led: bool = field(default=False, repr=False, compare=False)
    hitrun_until: float = -1.0        # Reiter: bis dahin wird vom Feind abgesetzt
    flank_throw: bool = False         # KI-Peltasten: beim Plänkeln an die schildlose rechte Flanke einer Phalanx
    march: tuple | None = None        # (Ziel, Breite, Front): erst im Bogen hin, kurz vor dem Ziel aufmarschieren
    countermarch_until: float = -1.0  # Kontermarsch: bis dahin ziehen die Rotten durch sich hindurch (steht, ungeordnet)
    commander: object = field(default=None, repr=False, compare=False)   # Hauptmann: Mann in der Mitte, Richtpunkt

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
        return self.stance is Stance.PHALANX and self.in_line and not self.loose and self.drill_kind() != "locker"

    def drill_kind(self) -> str:
        """Der Modus, der wirkt: nur bei Hopliten (sonst "")."""
        key = (id(self.rows), self.men)
        if self._hoplite_key != key:                  # neu zählen, wenn sich die Reihen ändern
            men = self.all_men()
            self._hoplite_key = key
            self._hoplite_led = bool(men) and 2 * sum(1 for m in men if m.kind.hoplite) >= len(men)
        return self.drill if self._hoplite_led else ""

    def man_gap(self) -> float:
        """Abstand der Männer in der Reihe, je nach Modus."""
        return config.MAN_SPACING * config.DRILL_SPACING.get(self.drill_kind(), (1.0, 1.0))[0]

    def row_gap(self) -> float:
        """Abstand der Reihen, je nach Modus."""
        return config.ROW_SPACING * config.DRILL_SPACING.get(self.drill_kind(), (1.0, 1.0))[1]

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
        return base * factor * config.DRILL_SPEED.get(self.drill_kind(), 1.0)

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
        gap, rows = self.man_gap(), self.row_gap()
        need = [max(0.12, len(layer) * gap / (2 * math.pi)) for layer in self.layers()]
        if not need:
            return [0.35]
        outer = max(0.35, self.ring_size, max(r + i * rows for i, r in enumerate(need)))
        return [outer - i * rows for i in range(len(need))]

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
        return max(0.2, self.width * self.man_gap() / 2 + 0.08)

    @property
    def half_d(self) -> float:
        """Halbe Tiefe der Formation in Kacheln (in Blickrichtung)."""
        if self.formation == "o":
            return self.ring_radius() + 0.08
        if self.formation == "keil":
            return max(0.2, self.wedge_rows() * config.ROW_SPACING / 2 + 0.08)
        return max(0.2, self.depth * self.row_gap() / 2 + 0.08)

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

    def commander_man(self) -> "Man | None":
        """Der Befehlshaber der Gruppe: steht vorn in der Mitte, an ihm richtet sich die Gruppe
        aus. Kämpft der Anführer in der Gruppe mit, ist er es. Fällt der Befehlshaber (oder ist
        noch keiner bestimmt), übernimmt der Mann, der dem Platz vorn in der Mitte am nächsten
        steht."""
        lead = self.leader_man()
        if lead is not None:
            self.commander = lead
            return lead
        c = self.commander
        if c is not None and c.hp > HP_EPS and any(m is c for row in self.rows for m in row):
            return c
        men = self.all_men()
        if not men:
            self.commander = None
            return None
        if self.formation == "linie" and self.rows and self.rows[0]:
            self.commander = self.rows[0][len(self.rows[0]) // 2]
            return self.commander
        self.commander = min(men, key=lambda m: (m.x - self.x) ** 2 + (m.y - self.y) ** 2)
        return self.commander

    def seat_commander(self) -> None:
        """Der Befehlshaber steht auf dem mittleren Platz der vorderen Reihe (nur in Linie)."""
        if self.formation != "linie" or not self.rows or not self.rows[0]:
            return
        c = self.commander_man()
        if c is None:
            return
        front = self.rows[0]
        mc = len(front) // 2
        if front[mc] is c:
            return
        for row in self.rows:
            for ci, m in enumerate(row):
                if m is c:
                    row[ci], front[mc] = front[mc], row[ci]
                    return

    def leader_man(self) -> "Man | None":
        """Der Anführer, wenn er in dieser Gruppe kämpft und lebt."""
        return next((m for m in self.all_men() if m.leader), None)

    def bravery(self) -> float:
        men = self.all_men()
        return sum(m.kind.bravery for m in men) / len(men) if men else 1.0

    def ammo(self) -> int:
        return sum(m.ammo for m in self.all_men())

    def summary(self) -> str:
        parts = [f"{self.count(k)}{UNIT_TYPES[k].short}" for k in PLAYER_TYPES if self.count(k)]
        return " ".join(parts) if parts else f"{self.men}"

    # -------------------------------------------------------- Formation
    def reform(self, width: int, centre: tuple[float, float] | None = None,
               facing: tuple[float, float] | None = None) -> None:
        """Reihen neu bilden: Abschnitte bleiben vorn/hinten, Breite ändert sich.
        Die Männer behalten ihre Position und laufen zu ihren neuen Plätzen; in der Linie
        werden die Plätze der neuen Aufstellung (``centre``, ``facing``; sonst die jetzige)
        so verteilt, dass die Wege zusammen am kürzesten sind und keiner den anderen kreuzt."""
        rows = arrange(self.all_men(), width)
        if self.formation == "linie" and config.FIT_MEN:
            rows = fit_men(rows, centre or self.pos, facing or self.facing, self.man_gap(), self.row_gap(),
                           origin=self.pos, old_facing=self.facing)
        self.rows = rows

    def slots(self) -> list[tuple[Man, tuple[float, float]]]:
        """Platz jedes Mannes in der Formation (Weltkoordinaten)."""
        return self.slots_at(self.pos, self.facing, self.file)

    def slots_at(self, centre: tuple[float, float], facing: tuple[float, float],
                 file: bool = False) -> list[tuple[Man, tuple[float, float]]]:
        """Die Plätze der Formation um ein beliebiges Zentrum; als ``file`` eine
        einzelne Reihe längs der Palisade (für den Wehrgang)."""
        cx, cy = centre
        out = []
        if file and self.wall_layout is not None:
            return self.wall_layout(self, centre)     # Festung: entlang des Wehrgangs, wie er verläuft
        if file:
            men = self.all_men()
            n = len(men)
            for i, man in enumerate(men):
                out.append((man, (cx + (i - (n - 1) / 2) * config.MAN_SPACING, cy)))
            return out
        fx, fy = facing
        self.seat_commander()
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
        gap, rows = self.man_gap(), self.row_gap()
        for r, row in enumerate(self.rows):
            forward = ((n_rows - 1) / 2 - r) * rows
            n = len(row)
            for i, man in enumerate(row):
                side = (i - (n - 1) / 2) * gap
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
                                                    if m.kind.hoplite and distance(m) <= reach + self.row_gap())
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
        in inneren Ringen), reine Reiter den Keil. Reinen Peltasten hilft der Kreis
        ohne Schildwand nicht: nur die Linie."""
        men = self.all_men()
        if any(not m.kind.cavalry and not m.kind.ranged for m in men):
            return ("linie", "o")
        if men and all(m.kind.cavalry for m in men):
            return ("linie", "keil")
        return ("linie",)

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
            hit = a if a.hp <= c.hp else c
            hit.hp -= q
            hit.felt(q)
            dmg -= q
        return self.bury()

    def hit_man(self, man: Man, dmg: float) -> int:
        """Ein bestimmter Mann wird getroffen (Speer); liefert 1, wenn er fällt."""
        man.hp -= dmg
        man.felt(dmg)
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
            self.fell_at.extend(row[j].pos for j in gaps)
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
