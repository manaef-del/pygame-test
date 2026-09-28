# pygame-test

Ein kleines Ausweichspiel („Dodge“) in Pygame, gedacht als Testprojekt.
Rote Blöcke fallen von oben, der blaue Balken weicht aus. Jeder Block, der
unten durchfällt, gibt einen Punkt. Mit der Zeit wird es schneller.

## Steuerung

| Taste            | Aktion            |
|------------------|-------------------|
| ← / → oder A / D | Bewegen           |
| Tippen links / rechts | Bewegen (Touch) |
| R oder Tippen    | Neustart (Game Over) |
| Esc              | Beenden           |

## Starten

```bash
pip install -r requirements.txt
python main.py
```

## Im Browser (iPhone, Tablet)

Der Workflow `.github/workflows/pages.yml` übersetzt das Spiel bei jedem
Push mit [pygbag](https://pygame-web.github.io/) nach WebAssembly und
veröffentlicht es auf GitHub Pages. Einmalig einrichten:

1. Repository → Settings → Pages → Source: **GitHub Actions**.
2. Bei privaten Repositories braucht GitHub Pages einen Pro-, Team- oder
   Enterprise-Plan. Alternativ das Repository auf öffentlich stellen.

Danach ist das Spiel unter `https://<benutzer>.github.io/pygame-test/`
erreichbar. Beim ersten Laden holt der Browser die Python-Laufzeit
(einige MB), danach startet das Spiel per Tipp auf den Bildschirm.

Lokal ausprobieren (baut und startet einen Server auf Port 8000):

```bash
pip install "pygbag==0.9.2"
python -m pygbag .
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
game/app.py       Asynchrone Hauptschleife, Tastatur und Touch
tests/            pytest-Tests (headless)
```
