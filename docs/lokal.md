# Lokal ausführen und ins Hauptprojekt übernehmen

Das Spiel hängt nur von `pygame` ab (Tests zusätzlich von `pytest`). Es ist
für das Hochformat 480×680 gebaut (Handy), läuft aber genauso in einem
Fenster auf dem Computer.

## Holen und starten

```bash
git clone --branch claude/create-test-game-cpnmer https://github.com/manaef-del/pygame-test.git
cd pygame-test
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python main.py                   # das Spiel
python -m pytest -q -n 4         # die Tests (etwa fünf Minuten; -n 4 braucht pytest-xdist, sonst ohne)
```

Browser-Fassung wie auf GitHub Pages: `pip install "pygbag==0.9.2"` und
`python -m pygbag --build --ume_block 0 --can_close 1 .`, das Ergebnis liegt
in `build/web`.

## Ins Hauptprojekt einbauen

Der Ordner `game/` ist in sich geschlossen: keine Abhängigkeit außer
`pygame`, kein Zugriff auf Dateien außerhalb. Einstieg ist `game.app.run()`
(asynchron, wegen pygbag; nativ mit `asyncio.run(run())`, siehe `main.py`).

- `game/battle.py`: die Schlacht (Regeln, Bewegung, Kampf, Wall, Tore)
- `game/units.py`: Gattungen, Männer, Gruppen, Formationen
- `game/scenarios.py`: die Szenarien (Karten, Häuser, Festung, Startaufstellung)
- `game/ai.py`, `game/fortress_ai.py`, `game/doctrine.py`: die Gegner-KI
- `game/app.py`, `game/render.py`: Bedienung (Tippen, Zwei-Finger) und Bild
- `game/config.py`: alle Stellschrauben, mit Kommentaren
- `tools/simulate.py`: Simulation von Spielertaktiken gegen die KI

Zum Übernehmen den Ordner `game/` als Paket kopieren (oder das Repository als
Git-Submodul einbinden) und aus dem Hauptprojekt `game.app.run()` aufrufen,
beziehungsweise für eine eigene Oberfläche `game.battle.Battle` mit einem
Szenario aus `game.scenarios` und einer Armee aus `game.army` erzeugen und
je Takt `update(dt)` rufen; `game/render.py` zeigt, wie der Zustand gezeichnet
wird. Die Tests in `tests/` mitnehmen, sie laufen mit `pythonpath = ["."]`
(siehe `pyproject.toml`).
