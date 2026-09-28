# pygame-test

Ein kleines Ausweichspiel („Dodge“) in Pygame, gedacht als Testprojekt.
Rote Blöcke fallen von oben, der blaue Balken weicht aus. Jeder Block, der
unten durchfällt, gibt einen Punkt. Mit der Zeit wird es schneller.

## Steuerung

| Taste            | Aktion            |
|------------------|-------------------|
| ← / → oder A / D | Bewegen           |
| R                | Neustart (Game Over) |
| Esc              | Beenden           |

## Starten

```bash
pip install -r requirements.txt
python main.py
```

## Tests

Die Spiellogik in `game/logic.py` ist von der Darstellung getrennt und
läuft ohne Fenster. Die Tests nutzen den SDL-Dummy-Treiber und laufen
damit auch in CI oder Containern.

```bash
pip install -r requirements-dev.txt
pytest
```

## Struktur

```
main.py           Einstiegspunkt
game/config.py    Einstellungen (Größe, Geschwindigkeiten, Farben)
game/logic.py     Spielzustand, Spieler, Blöcke, Kollision
game/render.py    Zeichnen auf eine Surface
game/app.py       Hauptschleife und Eingabe
tests/            pytest-Tests (headless)
```
