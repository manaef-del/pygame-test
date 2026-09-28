# Apoikia – Kampfprobe

Ein eigenständiger Prototyp für die Kampfmechanik von **Apoikia**, dem
Pygame-Koloniespiel. Hier wird nur die taktische Ebene gebaut und im
Browser getestet. Was sich bewährt, wandert später ins Hauptprojekt.

## Was der Prototyp umsetzt

Aus dem Apoikia-Konzept (Teil A·12 und B4) und dem Wirtschaftsregister
(Tabellen 7, 10, 11):

- **Gekämpft wird in Gruppen.** Die kleinste Einheit ist der *Lochos*,
  acht Mann. Der Ausgang wird je Lochos gerechnet, einzelne Kämpfer sind
  nur Darstellung.
- **Der Spieler markiert einen Bereich, keine Figuren.** Ein Zug über die
  Karte zeichnet einen Bereich, dort bildet sich die Phalanx. Die Front
  zeigt automatisch zu den Räubern.
- **Phalanx:** stark von vorn, verwundbar in Flanke und Rücken. Nachbarn
  in der Linie stützen sich gegenseitig (Schildwall). Sie hält die
  Stellung und verfolgt nicht.
- **Freier Angriff** löst die Formation: die Lochoi verfolgen den nächsten
  Gegner, schneller, aber ohne Formationsbonus. Fliehende werden
  niedergemacht.
- **Halten:** stehen bleiben, rundum kämpfen, kein Bonus.
- **Truppentypen nach Hausstufe:** Theten (Schleuderer, Fernkampf),
  Leichte, Hopliten, Reiter (Pferde laufen nicht in Speere).
- **Moral:** Verluste und Angriffe von hinten drücken die Moral; unter
  der Schwelle flieht ein Lochos. Räuber brechen früher als Hopliten.
- **Räuber** ziehen zu den Häusern und plündern, wenn niemand sie stört.
  Ein Teil umgeht die Linie. Sind sie zu geschwächt, ziehen sie ab.
- **Palisade mit Tor:** der einzige Durchgang. Wegfindung leitet durchs Tor.

Abnahme aus dem Konzept (L9), als Tests umgesetzt: *Ein Überfall auf eine
unbefestigte Stadt tut weh. Eine Phalanx hinter Mauern gewinnt gegen eine
deutlich größere Übermacht.*

## Szenarien

| Szenario | Lage |
|----------|------|
| Offene Siedlung | 5 Lochoi (3 Hopliten, Leichte, Theten) gegen 6 Räuber-Lochoi, zwei davon umgehen die Linie |
| Palisade mit Tor | dieselbe Truppe hinter einer Palisade gegen 9 Räuber-Lochoi |

## Steuerung

| Eingabe | Aktion |
|---------|--------|
| Ziehen auf der Karte (Finger oder Maus) | Bereich für die Phalanx |
| Angriff / A | freier Angriff |
| Halten / H | stehen bleiben |
| Pause / Leertaste | anhalten, bei Alarm: losgehen |
| Neu / R | Szenario neu starten |
| Szenario / S | Szenario wechseln |

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
game/units.py       Truppentypen, Lochos
game/geometry.py    Vektoren, Front/Flanke/Rücken
game/scenarios.py   Karten und Aufstellungen
game/battle.py      Simulation: Befehle, KI, Bewegung, Kampf, Moral, Plündern
game/render.py      Zeichnen von Karte, Einheiten, Leiste
game/app.py         Asynchrone Schleife, Touch und Tasten
tests/              pytest (headless)
tools/              Browser-Diagnose für CI
```
