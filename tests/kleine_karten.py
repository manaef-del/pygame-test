"""Kleine Testkarten (16 × 18 Kacheln) für Mechaniktests: die früheren Szenarien
„Offene Siedlung“, „Räuberhorde“ und „Siedlung ohne Wall“ in ihrer alten Größe. Im
Spiel gibt es sie nicht mehr; die Tests von Kampf, Moral und Bewegung rechnen auf
ihnen schneller und mit festen Koordinaten."""

from game.scenarios import RaiderSpawn, Scenario

HOUSES_SOUTH = ((4, 13), (5, 13), (4, 14), (5, 14), (10, 13), (11, 13), (10, 14), (11, 14))
HOUSES_NORTH = ((4, 1), (5, 1), (4, 2), (5, 2), (10, 1), (11, 1), (10, 2), (11, 2))
AGORA_SOUTH = (8.0, 17.0)
AGORA_NORTH = (8.0, 2.5)

RAIDS_OPEN = (
    RaiderSpawn(4.5, -1.0), RaiderSpawn(6.5, -2.0), RaiderSpawn(8.5, -1.0), RaiderSpawn(10.5, -2.0),
    RaiderSpawn(12.5, -1.0), RaiderSpawn(7.5, -3.5),
    RaiderSpawn(0.6, -1.0, waypoints=((0.7, 11.5),)), RaiderSpawn(15.4, -1.0, waypoints=((15.3, 11.5),)),
    RaiderSpawn(5.5, -5.0), RaiderSpawn(9.5, -5.0), RaiderSpawn(3.0, -6.5), RaiderSpawn(12.0, -6.5),
)

HORDE = tuple(
    RaiderSpawn(x, y)
    for x, y in ((4.0, 3.5), (6.5, 2.5), (9.5, 2.5), (12.0, 3.5), (5.0, 5.0), (8.0, 4.5), (11.0, 5.0),
                 (3.0, 1.5), (13.0, 1.5), (7.0, 0.8), (9.5, 6.3), (6.0, 6.3))
)

KLEIN_OFFEN = Scenario(
    key="klein_offen", name="Test: kleine offene Siedlung",
    hint="", role="verteidigung", enemy_kind="raeuber", enemy_default=128, enemy_min=32, enemy_max=192,
    houses=HOUSES_SOUTH, raider_spawns=RAIDS_OPEN, agora=AGORA_SOUTH,
)

KLEIN_HORDE = Scenario(
    key="klein_horde", name="Test: kleine Räuberhorde",
    hint="", role="angriff", enemy_kind="raeuber", enemy_default=96, enemy_min=16, enemy_max=192,
    raider_spawns=HORDE, deploy_y=15.5,
)

KLEIN_ANGRIFF = Scenario(
    key="klein_angriff", name="Test: kleine Siedlung im Angriff",
    hint="", role="angriff", enemy_kind="spiegel", enemy_default=75, enemy_min=20, enemy_max=150,
    houses=HOUSES_NORTH, deploy_y=15.5, enemy_deploy_y=5.5, agora=AGORA_NORTH,
)
