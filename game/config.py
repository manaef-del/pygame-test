"""Zentrale Einstellungen: Bildschirm, Karte, Balance."""

# --- Bildschirm / Karte -------------------------------------------------
COLS = 16
ROWS = 18
TILE = 30
MAP_W = COLS * TILE          # 480
MAP_H = ROWS * TILE          # 540
BAR_H = 52                   # eine Reihe: nur die Befehle für die gewählten Gruppen
WIDTH = MAP_W                # 480
HEIGHT = MAP_H + BAR_H       # 680
FPS = 60

# --- Kampf ----------------------------------------------------------------
LOCHOS_MEN = 8               # Mann je Lochos
ENGAGE_RANGE = 0.6           # Kacheln Lücke zwischen den Formationen: Speerweite, ab hier wird gekämpft
CONTACT_GAP = 0.15           # Kacheln: bis hierhin schließt ein Angreifer auf, Schild an Schild
CONTACT_HOLD = 0.5           # Kacheln über die Speerweite hinaus: wer schon kämpft, kommt so schwer wieder los
SEEK_RANGE = 2.2             # Kacheln: Räuber wenden sich Verteidigern zu
SEPARATION = 0.2             # Zusatzabstand zu den Radien zweier Gruppen
MAN_RADIUS = 0.055           # Kacheln: Platz, den ein Mann für sich hat; näher als zwei Halbmesser kommt ihm keiner (Reihenabstand 0,13)
DETOUR_MARGIN = 0.25         # Kacheln Abstand, mit dem eine Gruppe um eine andere herumgeht
BASE_RATE = 0.09             # Schaden pro Sekunde je Angriffspunkt
CONTACT_REACH = 0.6          # Kacheln von Mann zu Mann: so weit reicht ein Mann an den nächsten Feind (Rechteck an Rechteck stehen die Reihen 0,55 auseinander, um ein Linienende gelegt 0,32); wer weiter weg steht, kämpft nicht mit
ARRIVE_EPS = 0.08

# Phalanx: wie stark trifft ein Angriff je nach Richtung
PHALANX_FRONT = 0.35
PHALANX_FLANK = 1.0
PHALANX_REAR = 1.8
PHALANX_FRONT_O = 0.55       # Kreis: rundum Front, ohne den Rückhalt der Glieder
RING_ATTACK_SHARE = 0.6      # Anteil aller Männer, die im Kreis kämpfen
PHALANX_ATTACK_FRONT = 1.3   # Speere in der Linie
SECOND_ROW_SPEARS = 0.5      # Anteil, mit dem die Hopliten der zweiten Reihe über die Schultern mitstechen
PHALANX_ATTACK_SIDE = 0.4    # umdrehen, einzeln kämpfen
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
MORALE_SCALE = 1.6           # Moralverlust je Gefallenem = SCALE / Startstärke * Tapferkeit * Richtung
MORALE_REGEN = 0.03          # pro Sekunde, wenn nicht im Kampf
MORALE_REAR_DRAIN = 0.05     # pro Sekunde, Phalanx von hinten angegriffen
MORALE_LOSS_FRONT_PHALANX = 0.8
MORALE_CONTAGION = 0.12      # Moralverlust, wenn eine Nachbargruppe flieht
MORALE_CONTAGION_RANGE = 3.0
MORALE_HOPELESS_OWN = 0.4    # eigene Seite unter diesem Anteil ...
MORALE_HOPELESS_FOE = 0.6    # ... und der Gegner noch über diesem: die Schlacht ist aussichtslos
MORALE_HOPELESS_DRAIN = 0.03 # Moralverlust je Sekunde in aussichtsloser Lage
ROUT_THRESHOLD_CITY = 0.35   # Flucht unter dieser Moral (Räuber 0.4, Siedlung 0.3)
LEADER_HP_FACTOR = 5.0       # Trefferpunkte des Anführers: so viel wie fünf Männer seiner Gattung
LEADER_ARMOR = 0.85          # Schaden an seiner Gruppe, solange er lebt (leichte Rüstung, Ordnung)
LEADER_COURAGE = 0.1         # so viel tiefer liegt die Fluchtschwelle seiner Gruppe
AGORA_RADIUS = 0.9           # Kacheln: Halbmesser der Agora
RALLY_RADIUS = 1.3           # Kacheln um den Sammelpunkt, in denen sich Fliehende sammeln
RALLY_SAFE = 2.0             # Kacheln Lücke: so nah darf kein kämpfender Feind sein, sonst sammelt sich niemand
RALLY_REGEN = 0.04           # Moral je Sekunde beim Sammeln
LAST_STAND_RANGE = 1.0       # Kacheln Lücke: so nah gesetzt, kehren Verteidiger auf der Agora um (Angreifer verlassen das Feld)
RALLY_MORALE = 0.6           # ab dieser Moral nimmt eine gesammelte Gruppe wieder Befehle an
RALLY_EDGE = 1.5             # Kacheln vom eigenen Kartenrand, wo sich Angreifer sammeln

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
CHARGE_FOOT = 0.4            # Fußvolk stößt mit diesem Anteil der Wirkung
CHARGE_WEDGE = 1.8           # Keil: halb so viele Getroffene, dafür so viel härter
STAND_TURN_RATE = 3.14       # rad/s: Schwenken im Stand (halbe Umdrehung je Sekunde), alle Gattungen
ABOUT_TURN = 2.1             # rad (120°): ab hier wird kehrtgemacht (Reihen tauschen statt Plätze wechseln)
MOVE_TURN_TOLERANCE = 0.8    # rad (45°): erst wenn die Richtung so grob stimmt, geht es los
CAVALRY_ACCEL = 2.5          # Kacheln/s²: Reiter fahren an
CAVALRY_BRAKE = 4.0          # Kacheln/s²: Reiter bremsen vor dem Ziel
CAVALRY_TURN_RATE = 6.0      # rad/s im Schritt; geteilt durch das Tempo darüber (Bogen wächst mit dem Tempo)
CHARGE_BRAKE = 6.0           # Kacheln/s²: der Feind bremst die Reiter beim Eindringen
CHARGE_PENETRATION = 0.8     # Kacheln: so weit tragen die Reiter höchstens in den Feind hinein
CHARGE_SLOW = 0.4            # Geschwindigkeit der Reiter nach dem Aufprall
CHARGE_SLOW_TIME = 2.5       # Sekunden

# Freier Angriff je Waffengattung
SKIRMISH_NEAR = 1.6          # Kacheln: näher lassen Peltasten den Feind nicht heran
SKIRMISH_FAR = 0.4           # Kacheln unter der Wurfweite, auf die sie herangehen
HITRUN_DISTANCE = 3.0        # Kacheln, auf die sich Reiter nach dem Stoß absetzen
HITRUN_TIME = 5.0            # Sekunden, längstens

# Handgemenge: Binden und Lösen
MAN_BIND_REACH = 0.7         # Kacheln zum nächsten feindlichen Mann, bis zu denen ein Mann im Handgemenge steht
MAN_RELEASE_REACH = 1.0      # Kacheln: steht kein feindlicher Mann mehr so nah, ist er wieder frei
ASSAULT_GAP = 0.12           # Kacheln: so dicht legen sich Angreifer um den Umriss des Gegners
ASSAULT_MANNED = 0.3         # Kacheln: ein Stück Umriss zählt nur, wenn ein feindlicher Mann so nah daran steht
WING_SAFE = 3.0              # Kacheln: steht ein weiterer Feind so nah, klappen die Flügel der Hopliten nicht ein
RING_MAX = 3.0               # Kacheln: größter Halbmesser, den man dem Kreis ziehen kann
BOUND_LEASH = 1.2            # Kacheln: so weit darf sich die Gruppe von einem gebundenen Mann entfernen, dann reißt er sich los
ENGAGED_SPEED = 0.33         # Geschwindigkeit einer Gruppe im Nahkampf
DISENGAGE_TIME = 4.0         # Sekunden nach dem Lösen, in denen die Gruppe verwundbar ist
DISENGAGE_TIME_MOUNTED = 1.0 # Reiter lösen sich leichter
DISENGAGE_DAMAGE = 1.5       # Schaden in dieser Zeit (wie von hinten, ohne Formationsbonus)
SLOT_TOLERANCE = 0.25        # Kacheln: so nah müssen die Männer an ihren Plätzen stehen, damit die Phalanx steht
SLOT_SHARE = 0.85            # Anteil der Männer, der dafür auf seinem Platz stehen muss
BOUND_SHUFFLE = 0.6          # Kacheln: so weit rückt ein gebundener Mann noch auf seinen Platz nach

# Gerangel: nur fürs Bild, die Rechnung bleibt bei den Plätzen der Männer
JOSTLE_REACH = 1.5           # Kacheln: so weit sucht ein Mann ohne Gegner nach einem freien feindlichen Mann
JOSTLE_MAX = 1.0             # Kacheln: so weit drängt er höchstens von seiner Stelle weg
JOSTLE_GAP = 0.35            # Kacheln: auf diese Armlänge tritt er an den Gegner heran
JOSTLE_PER_FOE = 2           # höchstens so viele drängen auf denselben Gegner
JOSTLE_SPEED = 1.5           # Kacheln/s: so schnell drängt er vor und zurück
HIT_FLASH = 0.25             # Sekunden: so lange blitzt ein Getroffener auf
HIT_FLASH_SHARE = 0.34       # Anteil seiner Lebenskraft, ab dem ein Treffer aufblitzt (der Schaden kommt in kleinen Häppchen)
FALLEN_MARK_TIME = 2.5       # Sekunden: so lange bleibt ein dunkler Fleck, wo einer fiel

# Männer
MAN_CATCHUP = 1.6            # Männer holen ihren Platz schneller ein, als die Gruppe läuft
DAMAGE_QUANTUM = 0.1         # Schaden wird in Häppchen auf einzelne Männer verteilt
DISMOUNTED_SPEED = 1.2       # abgesessene Reiter
DISMOUNTED_ATTACK = 1.0

# Eigene Wege der Männer (game/pathing.py)
FIELD_CELL = 0.25            # Kacheln je Zelle des Wegefelds
FIELD_REFRESH = 0.5          # Sekunden, nach denen das Wegefeld neu gerechnet wird (Gruppen bewegen sich)
FIELD_MARGIN = 0.12          # Kacheln Abstand, den die Männer um stehende eigene Gruppen halten
FIELD_BUDGET = 2             # so viele Wegefelder werden höchstens in einem Takt neu gerechnet (gegen Ruckeln)
WAYPOINT_TIME = 0.2          # Sekunden, die ein Mann seinen Wegpunkt behält
LOOSE_COHESION = 0.3         # Kacheln: so geschlossen müssen die Männer gehen, damit die Gruppe wieder als Block marschiert
LOOSE_LAG = 0.3              # Kacheln: wer so viel weiter von seinem Platz ist als die Mitte der Gruppe, holt auf
LOOSE_ENEMY_RANGE = 2.5      # Kacheln: steht ein Feind so nah am Tor, geht man im Block hindurch
MUSTER_GAP = 0.4             # Kacheln zwischen Wall und Sammelplatz dahinter
MUSTER_SKIP = 2.5            # Kacheln: liegt das Ziel so nah am Sammelplatz, sammelt man sich gleich am Ziel
MUSTER_WAIT = 8.0            # Sekunden, die drüben auf Nachzügler gewartet wird, bevor die Gruppe als Block weitergeht
LOOSE_AI = False             # auch die Gegner lösen sich zum Umgehen und fürs Tor auf (aus: sie gehen als Block wie bisher; über den Wall steigen alle Mann für Mann)
LOOSE_CLOSE_DISTANCE = 1.5   # Kacheln: so weit vor dem Ziel schließt sich die Gruppe noch zum Block, näher erst am Ziel
GAP_EXACT = 3.0              # Kacheln: weiter auseinander wird die Lücke zwischen aufgelösten Gruppen nur grob gerechnet
STALL_TIME = 1.0             # Sekunden ohne Vorankommen, bis ein Mann statt durchs Tor über Leiter oder Turm geht

# Formation
MAN_SPACING = 0.13           # Kacheln zwischen Männern einer Reihe
ROW_SPACING = 0.19           # Kacheln zwischen Reihen

# Zeit
TIME_SCALE = 0.5             # Spielzeit je Echtzeit (halbe Geschwindigkeit)

# Wall und Tor
WALL_RANGE_BONUS = 1.0       # Peltasten auf dem Wehrgang werfen weiter
WALL_MELEE_FACTOR = 0.3      # Nahkampf von unten gegen den Wehrgang und zurück
WALL_COVER_FACTOR = 0.3      # Speere von außen gegen Männer auf dem Wehrgang: die Palisade deckt sie
TOWER_THROW_INTERVAL = 0.5   # Sekunden: ein Wehrturm wirft zwei Speere in der Sekunde
TOWER_RANGE = 6.5            # Kacheln: so weit wirft ein Wehrturm (erhöht, reicht bis vor die Tore)
FORT_STORM_WAIT = 20.0       # Sekunden: so lange sammelt sich das Heer vor einem gesperrten Tor, dann stürmen alle
FORT_GATE_WATCH = 8.0        # Kacheln: steht kein Angreifer so nah an ihrem Tor, verstärkt die Phalanx die bedrohte Stelle
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
AI_TOWER_LANDING = 1.8       # Kacheln hinter dem Wall: dorthin sickern Räuber über einen Turm ein
AI_RETREAT_LOSS = 0.35       # Anteil Verluste (Gefallene und Wunden) im Angriff, ab dem eine Gruppe zurückweicht
AI_RETREAT_MORALE = 0.15     # Moralabstand zur Flucht, ab dem eine Gruppe lieber zurückweicht
AI_RETREAT_DISTANCE = 3.0
AI_RETREAT_TIME = 10.0       # Sekunden, die eine zurückgewichene Gruppe sammelt
AI_SKIRMISH_SEEK = 5.0       # Kacheln: ab hier gehen Peltasten der KI ins Plänkeln über
AI_SKIRMISH_KEEP = 6.5       # Kacheln: bis hierhin bleiben sie dabei (Hysterese)
AI_HARASS_TIME = 30.0        # Sekunden Zermürben, bevor gestürmt wird
AI_FLANK_RATIO = 1.1         # Stärkeverhältnis, ab dem gebunden und umfasst wird
AI_PIN_SHARE = 0.7           # Anteil der Phalanxstärke, den die bindenden Gruppen aufbringen
AI_REAR_ROOM = 2.0           # Kacheln freier Raum hinter einer Phalanx, damit „in den Rücken fallen“ in Frage kommt
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
COLOR_AGORA = (92, 96, 78)          # Pflaster der Agora
COLOR_AGORA_EDGE = (128, 128, 104)
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
COLOR_LEADER = (255, 205, 60)        # Ring um den Anführer
COLOR_JAVELIN = (245, 220, 170)
COLOR_BOUND = (255, 120, 60)      # Ring um Männer im Handgemenge
COLOR_HIT = (255, 250, 235)       # Aufblitzen eines Getroffenen
COLOR_FALLEN = (70, 30, 25)       # Fleck, wo einer fiel
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
