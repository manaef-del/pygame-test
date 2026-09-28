# Apoikia – Kampfprobe

Ein eigenständiger Prototyp für die Kampfmechanik von **Apoikia**, dem
Pygame-Koloniespiel. Hier wird nur die taktische Ebene gebaut und im
Browser getestet. Was sich bewährt, wandert später ins Hauptprojekt.

## Was der Prototyp umsetzt

Aus dem Apoikia-Konzept (Teil A·12 und B4) und dem Wirtschaftsregister
(Tabellen 7, 10, 11):

- **Gekämpft wird in Gruppen.** Der Ausgang wird je Gruppe gerechnet.
  Eine Gruppe ist eine geordnete Reihe von Männern, beliebig gemischt,
  die in Reihen aufgestellt wird. Die vordere Reihe kämpft im Nahkampf,
  Hopliten der zweiten Reihe stechen mit, Peltasten in hinteren Reihen
  werfen über die Front. Treffer gehen in die Reihe, die dem Angreifer
  zugewandt ist.
- **Truppentypen:** schwere, mittlere und leichte Hopliten (dunkel-,
  mittel-, hellblau), Peltasten (rot) und Reiter (grün). Räuber sind grau
  mit rotem Ring. Vorrat: 40 Hopliten, 15 Peltasten, 20 Reiter.
- **Peltasten** haben zehn Speere je Mann und werfen in Salven. Jeder
  Speer fliegt sichtbar vom werfenden Mann zu einem bestimmten Gegner
  und trifft nur diesen. Sind die Speere verschossen, geht die Gruppe in
  den Nahkampf über.
- **Jeder Mann zählt einzeln.** Er hat eigene Trefferpunkte (verwundete
  Punkte sind dunkler) und eine eigene Position: Er läuft zu seinem
  Platz in der Formation, weicht aber selbst aus, durchs Tor nur durch
  die Öffnung, auf den Wall nur über Leiter oder Turm.
- **Reiter** sitzen ab, sobald sie Rammbock oder Turm bauen oder auf den
  Wehrgang steigen. Die Pferde bleiben als braune Punkte zurück; danach
  sind sie so schnell wie Fußvolk und ohne Reiterbonus. Durch ein
  aufgebrochenes Tor reiten sie beritten.
- **Aufstellung:** Vor der Schlacht werden Gruppen aus dem Vorrat
  zusammengestellt. Eine Gruppe besteht aus Reihen-Blöcken von vorn nach
  hinten, jeder Block mit einem Truppentyp (Farbpunkt) und einer Anzahl
  (Schieberegler). Blöcke lassen sich verschieben, entfernen und
  hinzufügen. Vorgabe: je eine Gruppe Hopliten, Peltasten und Reiter.
- **Front aufziehen:** Gruppe antippen, dann auf der Karte den Finger
  aufsetzen und eine Linie ziehen. Die Linie ist die Front, ihre Länge
  bestimmt die Breite und damit die Zahl der echten Reihen. Landen
  mehrere Blöcke in einer Reihe, wechseln sich ihre Männer ab. Die Gruppe
  schaut senkrecht zur Linie: von links nach rechts gezogen nach oben, so
  wie man hinter ihr steht. Ohne Auswahl teilen sich alle Gruppen die
  Linie.
- **Phalanx:** eine aufgezogene Gruppe hält die Stellung. Stark von vorn,
  verwundbar in Flanke und Rücken. Der Bonus hängt vom Hoplitenanteil der
  vorderen Reihe ab. Nachbarn stützen sich (Schildwall).
- **Freier Angriff** löst die Formation: die Gruppen verfolgen den
  nächsten Gegner, schneller, aber ohne Formationsbonus. Fliehende werden
  niedergemacht. Reiter sind stark gegen Gegner ohne Formation und
  schwach gegen die Front einer Phalanx.
- **Halten:** stehen bleiben, rundum kämpfen, kein Bonus.
- **Moral:** Verluste und Angriffe von hinten drücken die Moral; unter
  der Schwelle flieht ein Lochos. Räuber brechen früher als Hopliten.
- **Räuber** ziehen zu den Häusern und plündern, wenn niemand sie stört.
  Ein Teil umgeht die Linie. Sind sie zu geschwächt, ziehen sie ab.
- **Palisade mit Tor:** der einzige Durchgang. Wegfindung leitet durchs Tor.

Abnahme aus dem Konzept (L9), als Tests umgesetzt: *Ein Überfall auf eine
unbefestigte Stadt tut weh. Eine Phalanx hinter Mauern gewinnt gegen eine
deutlich größere Übermacht.*

## Szenarien

Zwei Regler oben im Aufstellungsmenü setzen die eigene Stärke und die
des Gegners. Die Blöcke und Gruppen sind die Vorlage für die Mischung,
die Gesamtzahl verteilt sich verhältnismäßig darauf. Das Spiel läuft
mit halber Geschwindigkeit (`TIME_SCALE`).

| Szenario | Lage |
|----------|------|
| Verteidigung: Offene Siedlung | Räuberhaufen von Norden, zwei umgehen die Linie. Bei großer Zahl größere Haufen, mit einem Fünftel Peltasten |
| Verteidigung: Palisade | Das Tor ist zu, die Räuber bauen vor dem Tor einen Rammbock. Eigene Peltastengruppen dürfen auf den Wehrgang |
| Angriff: Räuberhorde | Die Horde lagert im Norden und stürmt, sobald man ihr nahe kommt |
| Angriff: Siedlung ohne Wall | Der Gegner stellt dieselbe Mischung wie die eigene Truppe, skaliert. Hopliten und Peltasten halten, Reiter greifen an |
| Angriff: Siedlung mit Wall | Wie oben, hinter einer Palisade mit verschlossenem Tor. Peltasten des Gegners stehen auf dem Wehrgang |

**Wehrgang:** Eine reine Peltastengruppe der Wallseite darf auf die
Palisade, aber nur über die Leitern hinauf und hinunter (helle Sprossen
auf der Palisade). Oben läuft sie entlang, auch über das Torhaus. Über
die Palisade wirft nur, wer oben steht, dafür eine Kachel weiter.
Nahkampf gegen den Wehrgang (und von ihm herab) wirkt nur zu einem
Drittel.

**Belagerungsgerät:** Beim Angriff auf die Siedlung mit Wall ist das Tor
verschlossen. Jede gewählte Gruppe kann ein Gerät bauen:
„Rammbock“ (acht Sekunden) oder „Turm“ (zwölf Sekunden). Mit Rammbock
das Tor antippen: die Gruppe geht hin und bricht es auf; nach dem
Durchbruch bleibt der Rammbock liegen und die Gruppe tritt zur Seite,
damit der Durchgang frei ist. Mit Turm ein
Wallstück antippen: die Gruppe rollt hin, setzt den Turm an, und nach
drei Sekunden steht er als Aufstieg auf den Wehrgang. Wer über den Turm
kommt, steht oben auf der Plattform, kann dort entlanglaufen und kämpfen
und kommt nach innen nur über die Leitern der Palisade hinunter (über
den Turm nur zurück nach außen). Fällt
eine Gruppe oder flieht sie, ist ihr Gerät verloren. Bei der
Verteidigung mit Palisade bauen die Räuber selbst einen Rammbock.

## Steuerung

| Eingabe | Aktion |
|---------|--------|
| Tippen auf eigene Gruppe | auswählen (erneut tippen: abwählen) |
| Tippen auf die Karte | gewählte Gruppen laufen dorthin |
| Tippen auf Feind | gewählte Gruppen greifen diese an |
| Tippen auf das Tor | gewählte Gruppen mit Rammbock brechen es auf |
| Tippen auf den Wall | gewählte Gruppen mit Turm setzen ihn dort an |
| Rammbock / B, Turm / T | gewählte Gruppen bauen das Gerät (nur beim Angriff mit Wall) |
| Ziehen auf der Karte | Front aufziehen: Länge = Breite, Richtung = Blickrichtung |
| Angriff / A | freier Angriff (Auswahl, sonst alle) |
| Halten / H | stehen bleiben (Auswahl, sonst alle) |
| Alle / Keine | alle Gruppen wählen oder Auswahl aufheben |
| Pause / Leertaste | anhalten, bei Alarm: losgehen |
| Neu / R | Szenario neu starten |
| Aufstellung / M | zurück ins Aufstellungsmenü |

Das Spiel beginnt im **Alarm** und wartet auf den ersten Befehl.

## Starten

```bash
pip install -r requirements.txt
python main.py
```

## Im Browser (iPhone, Tablet)

Der Workflow `.github/workflows/pages.yml` übersetzt das Spiel bei jedem
Push mit [pygbag](https://pygame-web.github.io/) nach WebAssembly und
veröffentlicht es auf GitHub Pages: https://manaef-del.github.io/pygame-test/

Der Workflow lädt den Build außerdem in einem Headless-Chromium und
schreibt die Browser-Konsole ins Actions-Log (`tools/browser_smoke.py`).

Lokal ausprobieren (baut und startet einen Server auf Port 8000):

```bash
pip install "pygbag==0.9.2"
python -m pygbag .
```

## Tests und Balance

Die Logik in `game/battle.py` kennt kein Pygame. Die Tests prüfen
Geometrie, Auflösung (Front gegen Rücken), Befehle, Routing durchs Tor,
beide Szenarien und Determinismus.

```bash
pip install -r requirements-dev.txt
pytest
```

Alle Balancezahlen stehen in `game/config.py` und `game/units.py`.

## Struktur

```
main.py             Einstiegspunkt
game/config.py      Karte, Balance, Farben
game/units.py       Truppentypen, Männer, Gruppe mit Reihen
game/army.py        Vorrat und Aufstellung (Gruppen, Reihen)
game/geometry.py    Vektoren, Front/Flanke/Rücken
game/scenarios.py   Karten und Aufstellungen
game/battle.py      Simulation: Befehle, KI, Bewegung, Kampf, Moral, Plündern
game/render.py      Zeichnen von Karte, Gruppen, Leiste und Aufstellungsmenü
game/app.py         Asynchrone Schleife, Bildschirme, Auswahl, Touch und Tasten
tests/              pytest (headless)
tools/              Browser-Diagnose für CI
```
