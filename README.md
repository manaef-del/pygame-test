# Apoikia – Kampfprobe

Ein eigenständiger Prototyp für die Kampfmechanik von **Apoikia**, dem
Pygame-Koloniespiel. Hier wird nur die taktische Ebene gebaut und im
Browser getestet. Was sich bewährt, wandert später ins Hauptprojekt.

## Was der Prototyp umsetzt

Aus dem Apoikia-Konzept (Teil A·12 und B4) und dem Wirtschaftsregister
(Tabellen 7, 10, 11):

- **Gekämpft wird in Gruppen.** Der Ausgang wird je Gruppe gerechnet.
  Eine Gruppe hat bis zu drei Reihen, jede Reihe beliebig gemischt. Die
  vordere Reihe kämpft im Nahkampf, Hopliten der zweiten Reihe stechen
  mit, Peltasten in hinteren Reihen werfen über die Front. Treffer gehen
  in die Reihe, die dem Angreifer zugewandt ist.
- **Truppentypen:** schwere, mittlere und leichte Hopliten (dunkel-,
  mittel-, hellblau), Peltasten (rot, Fernkampf) und Reiter (grün).
  Räuber sind grau mit rotem Ring. Vorrat: 40 Hopliten, 15 Peltasten,
  20 Reiter.
- **Aufstellung:** Vor der Schlacht werden Gruppen aus dem Vorrat
  zusammengestellt, je Reihe und Typ die Anzahl. Die Reihenfolge der
  Gruppen ist die Reihenfolge von links nach rechts im Aufmarsch.
- **Phalanx:** ein Zug über die Karte markiert den Bereich, dort bildet
  sich die Linie. Stark von vorn, verwundbar in Flanke und Rücken. Der
  Bonus hängt vom Hoplitenanteil der vorderen Reihe ab. Nachbarn stützen
  sich (Schildwall). Sie hält die Stellung und verfolgt nicht.
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

| Szenario | Lage |
|----------|------|
| Offene Siedlung | 75 Mann gegen 8 Räubertrupps zu 16 Mann, zwei davon umgehen die Linie |
| Palisade mit Tor | dieselbe Truppe hinter einer Palisade gegen 12 Räubertrupps |

## Steuerung

| Eingabe | Aktion |
|---------|--------|
| Tippen auf eigene Gruppe | auswählen (erneut tippen: abwählen) |
| Tippen auf die Karte | gewählte Gruppen laufen dorthin |
| Tippen auf Räuber | gewählte Gruppen greifen diese an |
| Ziehen auf der Karte | Bereich für die Phalanx (gewählte Gruppen, sonst alle) |
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
