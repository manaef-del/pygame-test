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
PHALANX_SUPPORT = 0.15       # Schildwall: je Nachbar weniger Schaden
PHALANX_SUPPORT_MIN = 0.55
CAVALRY_VS_FRONT = 0.3       # Pferde laufen nicht in Speere
CAVALRY_CHARGE = 1.5         # Reiter gegen Gegner ohne Formation
ROUTED_DAMAGE = 2.0          # Fliehende werden niedergemacht

# Winkel (Grad) für Front / Flanke / Rücken
FRONT_ARC = 60
REAR_ARC = 120

# Moral
MORALE_REGEN = 0.03          # pro Sekunde, wenn nicht im Kampf
MORALE_REAR_DRAIN = 0.05     # pro Sekunde, Phalanx von hinten angegriffen
MORALE_LOSS_FRONT_PHALANX = 0.5

# Peltasten
JAVELINS = 10                # Würfe je Peltast
VOLLEY_INTERVAL = 1.5        # Sekunden zwischen zwei Salven
JAVELIN_DAMAGE = 0.12        # Schaden je Speer
JAVELIN_RANGE = 3.5          # Kacheln
JAVELIN_SPEED = 7.0          # Kacheln pro Sekunde (Anzeige und Einschlag)

# Formation
MAN_SPACING = 0.13           # Kacheln zwischen Männern einer Reihe
ROW_SPACING = 0.19           # Kacheln zwischen Reihen

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
COLOR_MEN = (245, 245, 245)
COLOR_MENU_BG = (24, 26, 34)
COLOR_MENU_PANEL = (36, 40, 52)
COLOR_SHIELD = (255, 230, 120)
COLOR_JAVELIN = (245, 220, 170)
COLOR_TEXT = (235, 235, 235)
COLOR_TEXT_DIM = (150, 150, 160)
COLOR_BAR = (28, 28, 36)
COLOR_BUTTON = (60, 64, 80)
COLOR_BUTTON_ACTIVE = (90, 140, 190)
COLOR_RECT = (255, 230, 120)
