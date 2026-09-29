"""Zentrale Einstellungen: Bildschirm, Karte, Balance."""

# --- Bildschirm / Karte -------------------------------------------------
COLS = 16
ROWS = 18
TILE = 30
MAP_W = COLS * TILE          # 480
MAP_H = ROWS * TILE          # 540
BAR_H = 100
WIDTH = MAP_W                # 480
HEIGHT = MAP_H + BAR_H       # 640
FPS = 60

# --- Kampf ----------------------------------------------------------------
LOCHOS_MEN = 8               # Mann je Lochos
ENGAGE_RANGE = 1.15          # Kacheln: ab hier wird gekämpft
SEEK_RANGE = 2.2             # Kacheln: Räuber wenden sich Verteidigern zu
SEPARATION = 0.2             # Zusatzabstand zu den Radien zweier Gruppen
BASE_RATE = 0.09             # Schaden pro Sekunde je Angriffspunkt
ARRIVE_EPS = 0.08

# Phalanx: wie stark trifft ein Angriff je nach Richtung
PHALANX_FRONT = 0.35
PHALANX_FLANK = 1.0
PHALANX_REAR = 1.8
PHALANX_ATTACK_FRONT = 1.3   # Speere in der Linie
PHALANX_ATTACK_SIDE = 0.4    # umdrehen, einzeln kämpfen
FLANK_FILE = 3               # Männer je Reihe, die sich an der Flanke wehren (und getroffen werden)
PHALANX_SUPPORT = 0.15       # Schildwall: je Nachbar weniger Schaden
PHALANX_SUPPORT_MIN = 0.55
CAVALRY_VS_FRONT = 0.3       # Pferde laufen nicht in Speere
CAVALRY_CHARGE = 1.5         # Reiter gegen Gegner ohne Formation
ROUTED_DAMAGE = 2.0          # Fliehende werden niedergemacht

# Winkel (Grad) für Front / Flanke / Rücken (nur noch für Hilfsrechnungen)
FRONT_ARC = 60
REAR_ARC = 120
ARC_TOLERANCE = 0.25         # Kacheln neben dem Ende der Front, die noch als Front zählen
FLANK_DEPTH = 0.6            # Kacheln vor der Front, ab denen ein Gegner neben dem Ende noch „vorn“ steht
LINE_SEAM = 1.0              # Kacheln Lücke zum Nachbarn, bis zu der die Linie als geschlossen gilt

# Moral
MORALE_REGEN = 0.03          # pro Sekunde, wenn nicht im Kampf
MORALE_REAR_DRAIN = 0.05     # pro Sekunde, Phalanx von hinten angegriffen
MORALE_LOSS_FRONT_PHALANX = 0.5

# Peltasten
JAVELINS = 10                # Würfe je Peltast
VOLLEY_INTERVAL = 1.5        # Sekunden zwischen zwei Salven
JAVELIN_DAMAGE = 0.2         # Schaden je Speer (trifft einen bestimmten Mann)
JAVELIN_RANGE = 3.5          # Kacheln
JAVELIN_SPEED = 14.0         # Kacheln pro Sekunde (Anzeige und Einschlag)

# Sturmangriff der Reiter
CHARGE_RUNUP = 2.0           # Kacheln Anlauf, bevor ein Aufprall wirkt
CHARGE_REACH = 0.6           # Kacheln vor den Reitern: wer dort steht, wird getroffen
CHARGE_PUSH = 0.9            # Kacheln Wegstoßen je Mann, geteilt durch sein Gewicht (Lebenspunkte)
CHARGE_IMPACT = 0.6          # Schaden je gestoßenem Mann, geteilt durch sein Gewicht
CHARGE_SHOCK = 0.08          # Moralverlust der getroffenen Gruppe (von hinten anderthalbfach)
CHARGE_IMPALE = 0.35         # Schaden je Speer der vorderen Reihe, wenn Reiter in eine Phalanxfront rennen
CHARGE_IMPALE_CAP = 0.6      # höchstens so viel je Reiter
CHARGE_SLOW = 0.4            # Geschwindigkeit der Reiter nach dem Aufprall
CHARGE_SLOW_TIME = 2.5       # Sekunden

# Handgemenge: Binden und Lösen
MAN_BIND_REACH = 0.7         # Kacheln zum Gegner, bis zu denen ein Mann im Handgemenge steht
BOUND_LEASH = 1.2            # Kacheln: so weit darf sich die Gruppe von einem gebundenen Mann entfernen, dann reißt er sich los
ENGAGED_SPEED = 0.33         # Geschwindigkeit einer Gruppe im Nahkampf
DISENGAGE_TIME = 4.0         # Sekunden nach dem Lösen, in denen die Gruppe verwundbar ist
DISENGAGE_TIME_MOUNTED = 1.0 # Reiter lösen sich leichter
DISENGAGE_DAMAGE = 1.5       # Schaden in dieser Zeit (wie von hinten, ohne Formationsbonus)
SLOT_TOLERANCE = 0.25        # Kacheln: so nah müssen die Männer an ihren Plätzen stehen, damit die Phalanx steht
SLOT_SHARE = 0.85            # Anteil der Männer, der dafür auf seinem Platz stehen muss
BOUND_SHUFFLE = 0.6          # Kacheln: so weit rückt ein gebundener Mann noch auf seinen Platz nach

# Männer
MAN_CATCHUP = 1.6            # Männer holen ihren Platz schneller ein, als die Gruppe läuft
DAMAGE_QUANTUM = 0.1         # Schaden wird in Häppchen auf einzelne Männer verteilt
DISMOUNTED_SPEED = 1.2       # abgesessene Reiter
DISMOUNTED_ATTACK = 1.0

# Formation
MAN_SPACING = 0.13           # Kacheln zwischen Männern einer Reihe
ROW_SPACING = 0.19           # Kacheln zwischen Reihen

# Zeit
TIME_SCALE = 0.5             # Spielzeit je Echtzeit (halbe Geschwindigkeit)

# Wall und Tor
WALL_RANGE_BONUS = 1.0       # Peltasten auf dem Wehrgang werfen weiter
WALL_MELEE_FACTOR = 0.3      # Nahkampf von unten gegen den Wehrgang und zurück
GATE_HP = 100.0
RAM_BUILD_TIME = 8.0         # Sekunden Spielzeit
RAM_DPS = 12.0               # Schaden am Tor je Sekunde
RAM_SPEED_FACTOR = 0.7
RAM_REACH = 0.9              # Abstand zum Tor, ab dem gerammt wird
TOWER_BUILD_TIME = 12.0
TOWER_SPEED_FACTOR = 0.6
TOWER_DEPLOY_TIME = 3.0      # Sekunden am Wall, bis der Übergang steht
TOWER_REACH = 0.7
CLIMB_RATE = 3.0             # Männer je Sekunde, die eine Leiter oder ein Turm durchlässt (dichte Kolonne)
BARRIER_MARGIN = 0.25        # Kacheln: so nah an einer feindlichen Formation kommt niemand vorbei
FOLLOW_LAG = 2.5             # Kacheln: so weit darf die Gruppe ihren Männern beim Klettern vorauseilen
ENEMY_RALLY_DISTANCE = 2.6   # Kacheln vor dem Tor, wo Räuber warten und bauen
HORDE_TRIGGER = 4.0          # Kacheln: ab hier stürmt die Horde
CAVALRY_TRIGGER = 5.0        # Kacheln: ab hier greifen feindliche Reiter an

# Gegner-KI (siehe game/ai.py)
AI_DEFAULT = "klug"          # "klug" = Stufen-KI, "einfach" = alte feste Regeln
AI_INTERVAL = 0.5            # Sekunden zwischen zwei Lageberichten
AI_PLAN_INTERVAL = 12.0      # Sekunden, bis ein Plan neu bewertet wird
AI_FRONT_RANGE = 14.0        # Kacheln: so weit zählt eine Phalanx als sperrende Front
AI_GATE_GUARD_RANGE = 3.5    # Kacheln hinter dem Tor: dort gilt es als bewacht
AI_COVER_RANGE = 2.0         # Kacheln: Hopliten so nah decken Peltasten
AI_WALL_WATCH = 4.0          # Kacheln vor dem Wall: Gegner dort gelten als Angriffspunkt
AI_FLANK_MARGIN = 1.3        # Kacheln Abstand beim Umlaufen einer Front
AI_RETREAT_LOSS = 0.35       # Anteil Verluste (Gefallene und Wunden) im Angriff, ab dem eine Gruppe zurückweicht
AI_RETREAT_MORALE = 0.15     # Moralabstand zur Flucht, ab dem eine Gruppe lieber zurückweicht
AI_RETREAT_DISTANCE = 3.0
AI_RETREAT_TIME = 10.0       # Sekunden, die eine zurückgewichene Gruppe sammelt
AI_HARASS_TIME = 30.0        # Sekunden Zermürben, bevor gestürmt wird
AI_FLANK_RATIO = 1.1         # Stärkeverhältnis, ab dem gebunden und umfasst wird
AI_PIN_SHARE = 0.7           # Anteil der Phalanxstärke, den die bindenden Gruppen aufbringen
AI_PIN_DISTANCE = 1.3        # Kacheln vor der Front, wo die Bindenden auf die Umfassung warten
AI_PIN_DELAY = 12.0          # Sekunden, nach denen die Bindenden spätestens angreifen
AI_PINNED_BONUS = 0.5        # Zielwert einer Phalanx, die von der eigenen Linie gebunden ist
AI_SIEGE_PATIENCE = 40.0     # Sekunden Belagern vor dem bewachten Tor
AI_GATHER_TIME = 6.0         # Sekunden nach dem Durchbruch, in denen sich die Räuber sammeln
AI_TOWER_BUILD_DISTANCE = 2.6
AI_ISOLATION_RANGE = 2.5     # Kacheln: eine Gruppe ohne Nachbarn gilt als allein
AI_CAVALRY_MIN_VALUE = 1.4   # Reiter der Siedlung greifen nur so lohnende Ziele an
AI_SORTIE_RANGE = 5.0        # Kacheln: Eingedrungene werden so weit angegriffen
AI_REFACE_RANGE = 5.0        # Kacheln: die Linie dreht die Front zu einem Gegner
AI_MEMORY_DEPTH = 5          # letzte Schlachten, die zählen
AI_MEMORY_WEIGHT = 2.5         # Gewinn oder Verlust eines Plans wirkt kräftig auf die nächste Wahl
AI_MEMORY_MIN = 0.5
AI_MEMORY_MAX = 1.5
AI_MEMORY_FILE = "~/.apoikia_ki.json"

# Plünderung
LOOT_TIME = 4.0              # Sekunden je Haus
LOOT_RANGE = 0.8
ENEMY_WITHDRAW_FRACTION = 0.3  # Räuber ziehen ab, wenn weniger Männer übrig

# --- Farben ---------------------------------------------------------------
COLOR_BG = (18, 18, 24)
COLOR_GROUND = (46, 62, 44)
COLOR_GRID = (52, 70, 50)
COLOR_HOUSE = (196, 150, 74)
COLOR_HOUSE_LOOTED = (70, 40, 34)
COLOR_FIRE = (240, 120, 50)
COLOR_PALISADE = (120, 84, 46)
COLOR_GATE = (150, 110, 60)
COLOR_CITY = (225, 230, 235)      # Ring der eigenen Gruppen
COLOR_CITY_DIM = (110, 115, 120)
COLOR_ENEMY = (240, 90, 90)       # Ring der Räuber
COLOR_ENEMY_DIM = (120, 50, 50)
COLOR_SELECT = (255, 220, 60)
COLOR_HOPLIT_SCHWER = (20, 60, 170)
COLOR_HOPLIT_MITTEL = (60, 120, 230)
COLOR_HOPLIT_LEICHT = (140, 195, 255)
COLOR_PELTAST = (235, 70, 70)
COLOR_REITER = (70, 200, 90)
COLOR_RAEUBER = (200, 200, 200)
ENEMY_DESATURATION = 0.45   # Gegnerische Männer blasser als eigene
COLOR_MEN = (245, 245, 245)
COLOR_MENU_BG = (24, 26, 34)
COLOR_MENU_PANEL = (36, 40, 52)
COLOR_SHIELD = (255, 230, 120)
COLOR_JAVELIN = (245, 220, 170)
COLOR_BOUND = (255, 120, 60)      # Ring um Männer im Handgemenge
COLOR_RAM = (150, 100, 50)
COLOR_TOWER = (180, 130, 70)
COLOR_HORSE = (140, 95, 55)
COLOR_CROSSING = (200, 160, 90)
COLOR_GATE_CLOSED = (110, 70, 30)
COLOR_TEXT = (235, 235, 235)
COLOR_TEXT_DIM = (150, 150, 160)
COLOR_BAR = (28, 28, 36)
COLOR_BUTTON = (60, 64, 80)
COLOR_BUTTON_ACTIVE = (90, 140, 190)
COLOR_RECT = (255, 230, 120)
