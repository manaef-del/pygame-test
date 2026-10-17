# Übergabe: Gebäude in 8 Richtungen auf dem 2:1-Isoraster

Kurzfassung der Erkenntnisse und Werkzeuge aus der Arbeit am Iso-Editor,
gedacht als Kontext für eine andere Claude-Sitzung (etwa im Apoikia-Hauptprojekt).

## Worum es geht

Apoikia nutzt vorgerenderte Sprites auf einem 2:1-Isoraster (Kachel doppelt so
breit wie hoch, 1 Blender-Einheit = 1 Kachel). Frage: Können Gebäude nicht nur
in 4, sondern in 8 Richtungen (45°-Schritte) stehen? Antwort: Ja. Die Bilder sind
einfach (8 Kamerawinkel statt 4). Schwierig sind Raster, Tiefensortierung und
Anschlüsse. Dafür gibt es zwei Test-Editoren im Browser, die sich eine Szene teilen:

- 2D (Sprite-Sicht, Tiefensortierung): https://manaef-del.github.io/pygame-test/iso-editor/
- 3D (freie Kamera, Three.js): https://manaef-del.github.io/pygame-test/iso-editor/3d.html
- Quelle: `tools/iso_editor/` (index.html, 3d.html, gemeinsame Logik `iso_common.js`)

## Begriffe und Regeln, wie sie im Editor umgesetzt sind

**Haus.** Mittelpunkt (cx, cy) in Kacheleinheiten, Richtung dir 0..7 (dir·45°),
Grösse w×d (1×2, 2×2, 4×2). Lokale +y-Achse ist die Türseite. Der Grundriss ist
das um dir·45° gedrehte Rechteck um den Mittelpunkt.

**Belegungsmaske.** Für jede Kachel wird der Flächenanteil unter dem Grundriss
berechnet (Abtastung 8×8 Punkte je Kachel). Eine Kachel gilt als *belegt*, wenn
ihr Anteil ≥ Schwelle (Prozent, einstellbar, Standard 50). Kacheln mit Anteil > 0,
aber unter der Schwelle sind *angeschnitten*: frei für Wege und Bäume, die dann
optisch unter die Hausecke geraten. Beispiel 2×2 diagonal auf einer Kachelecke:
4 Kacheln zu 83 % und 8 Kacheln zu 9 %. Schwelle 50 → 4 belegt, Schwelle 5 → 12.
Diagonal auf einer Kachelmitte: 1 Kachel zu 100 %, 4 zu 66 %, 4 zu 9 %, bei
Schwelle 50 also ein Kreuz aus 5 Kacheln. Die Schwelle ist die Spielregel «wie
weit darf ein Gebäude in Nachbarkacheln ragen, bevor die Kachel gesperrt ist».

**Raster.** «Kachel»: gerade Häuser liegen genau auf Kacheln (Mittelpunkt auf
Kachelecke, wenn die halbe Ausdehnung ganzzahlig ist, sonst auf Kachelmitte),
diagonale auf einer Kachelecke. «½ Kachel»: alle Häuser rasten in halben
Kachelschritten ein, auch gerade, so lassen sie sich versetzt und dicht
aneinander bauen. Unabhängig von der Maske dürfen sich Grundrisse berühren,
aber nie überlappen (Trennachsen-Test zweier konvexer Vierecke).

**Eingangskachel.** Türmitte plus 0,6 Kacheln in Türrichtung, dann abgerundet.
Bei diagonalen Häusern liegt sie diagonal vor dem Haus. Wege brauchen deshalb
diagonale Verbindungen (im Editor: Band zwischen schräg benachbarten Wegkacheln;
ohne Band bleibt die Zickzack-Treppe aus Kacheln).

**Tiefensortierung (nur 2D relevant).** Zwei Verfahren zum Vergleich:
«Punkt» = ein Tiefenwert je Haus (x+y des Mittelpunkts), «Spalten» = das
Hausbild wird in Kachelspalten (Breite = halbe Kachelbreite, u = x−y ganzzahlig)
zerschnitten; jede Spalte erhält als Tiefe den vordersten Bodenpunkt (max x+y)
des Grundrisses in dieser Spalte und wird einzeln einsortiert. Bei 2×2 fällt
der Unterschied kaum auf, bei 4×2 diagonal und Bäumen daneben schon.

**Projektion.** sx = (x − y)·TW/2, sy = (x + y)·TH/2 − z·0,55·TW mit TH = TW/2.
Die 3D-Seite reproduziert das exakt mit einer orthografischen Kamera unter 30°
Höhe und 45° Azimut («2:1-Iso-Ansicht»), das ist der Blick vorgerenderter Sprites.

## Empfehlungen für das Hauptprojekt

1. Kachelraster behalten, pro Gebäudetyp und Richtung eine Belegungsmaske aus
   dem Blender-Grundriss rastern (Schwelle als eine Zahl in der Konfiguration).
2. Diagonalen zuerst nur für kleine, annähernd quadratische Bauten zulassen.
3. Grosse diagonale Gebäude beim Rendern in Spalten-Sprites zerschneiden
   (lässt sich in `blatt_bauen.py` automatisieren) und spaltenweise sortieren.
4. Diagonale Wege als eigenen Kachelsatz zeichnen, sonst Zickzack.
5. Die Logik in `tools/iso_editor/iso_common.js` (footprint, maskOf, blockedKeys,
   snapHouse, polysOverlap, entranceTile) ist klein und lässt sich 1:1 nach
   Python übertragen.

## Fertiger Text für einen anderen Claude

> Im Repo manaef-del/pygame-test liegt unter docs/iso-editor-uebergabe.md eine
> Zusammenfassung, wie Gebäude in 8 Richtungen (45°-Schritte) auf dem 2:1-Isoraster
> behandelt werden: Belegungsmaske mit Flächenanteil und Schwelle, Halbkachel-Raster,
> Grundriss-Kollision, Eingangskachel, diagonale Wege, spaltenweise Tiefensortierung.
> Die Referenzlogik steht in tools/iso_editor/iso_common.js (JavaScript), die
> Test-Editoren laufen unter https://manaef-del.github.io/pygame-test/iso-editor/
> (2D) und .../iso-editor/3d.html (3D). Bitte lies die Übergabe, bevor du
> Gebäudeplatzierung oder Sprites für diagonale Gebäude umsetzt.
