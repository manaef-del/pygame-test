# Simulation: Spielertaktiken gegen die Gegner-KI

Lauf vom 29. September 2026 mit `python3 tools/simulate.py --seeds 8`
(Stand des Commits, der diese Datei einführt). Jede Zeile sind acht
Schlachten mit den Seeds 0 bis 7, Spielzeit bis 300 s. „einfach“ ist die
alte feste Regelsteuerung, „klug“ die Stufen-KI aus `game/ai.py`.
Verluste sind der Anteil der Startstärke; „Häuser verloren“ zählt nur
bei der Verteidigung. „Pläne“ zählt, in wie vielen der acht Schlachten
ein Plan vorkam.

Die Taktiken sind Skripte in `tools/simulate.py`, die zu festen Zeiten
Befehle geben und danach nicht mehr reagieren. Ein Mensch würde
nachsteuern; die Zahlen zeigen also, wie hart die KI eine starre
Aufstellung bestraft.

## Alle Szenarien, beide KIs

| Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |
|---|---|---|---|---|---|---|---|---|
| offen | linie | einfach | 8/8 | 0% | 38% | 1.0 | 23 s | – |
| offen | linie | klug | 0/8 | 50% | 31% | 8.0 | 47 s | zermuerben×8, umgehen_west×8, frontal×8 |
| offen | linie_reiter | einfach | 8/8 | 0% | 45% | 1.0 | 24 s | – |
| offen | linie_reiter | klug | 7/8 | 31% | 53% | 5.2 | 46 s | zermuerben×8, umgehen_west×8, frontal×8 |
| offen | passiv | einfach | 8/8 | 28% | 38% | 4.0 | 29 s | – |
| offen | passiv | klug | 8/8 | 41% | 38% | 0.0 | 27 s | frontal×8 |
| offen | angriff | einfach | 2/8 | 47% | 39% | 7.8 | 29 s | – |
| offen | angriff | klug | 3/8 | 47% | 51% | 7.6 | 32 s | frontal×8 |
| palisade | tor_halten | einfach | 8/8 | 0% | 68% | 0.0 | 35 s | – |
| palisade | tor_halten | klug | 8/8 | 20% | 75% | 6.1 | 117 s | turm×8, belagern×8, umgehen_west×8, frontal×7, zermuerben×1 |
| palisade | tor_reserve | einfach | 8/8 | 0% | 68% | 0.0 | 35 s | – |
| palisade | tor_reserve | klug | 8/8 | 38% | 75% | 0.9 | 128 s | turm×8, belagern×8, umgehen_west×8, frontal×7, zermuerben×1 |
| palisade | passiv | einfach | 8/8 | 44% | 48% | 0.2 | 48 s | – |
| palisade | passiv | klug | 4/8 | 45% | 42% | 6.8 | 53 s | tor×8, frontal×8 |
| horde | vorruecken | einfach | 8/8 | 0% | 49% | 0.0 | 34 s | – |
| horde | vorruecken | klug | 8/8 | 1% | 52% | 0.0 | 48 s | lagern×8, umgehen_west×8, frontal×7 |
| horde | angriff | einfach | 8/8 | 41% | 49% | 0.0 | 22 s | – |
| horde | angriff | klug | 8/8 | 47% | 47% | 0.0 | 20 s | lagern×8, frontal×8 |
| angriff_offen | phalanxstoss | einfach | 0/8 | 94% | 56% | 0.0 | 84 s | – |
| angriff_offen | phalanxstoss | klug | 8/8 | 31% | 73% | 0.0 | 81 s | halten×8, vorruecken×8 |
| angriff_offen | vorruecken | einfach | 0/8 | 97% | 26% | 0.0 | 62 s | – |
| angriff_offen | vorruecken | klug | 0/8 | 96% | 31% | 0.0 | 60 s | halten×8, vorruecken×8 |
| angriff_offen | angriff | einfach | 0/8 | 86% | 10% | 0.0 | 25 s | – |
| angriff_offen | angriff | klug | 0/8 | 87% | 12% | 0.0 | 24 s | halten×8, vorruecken×8 |
| angriff_wall | tor_phalanx | einfach | 8/8 | 47% | 76% | 0.0 | 98 s | – |
| angriff_wall | tor_phalanx | klug | 1/8 | 81% | 56% | 0.0 | 126 s | halten×8, vorruecken×6 |
| angriff_wall | belagerung | einfach | 0/8 | 27% | 0% | 0.0 | 300 s | – |
| angriff_wall | belagerung | klug | 0/8 | 73% | 43% | 0.0 | 160 s | halten×8, vorruecken×8 |

### Was die Tabelle sagt

- **Offene Siedlung, starre Linie:** Gegen die alte KI reicht die Linie
  (8/8 ohne Verluste). Die kluge KI zermürbt die Phalanx mit Speeren,
  umgeht sie im Westen und plündert alle Häuser (0/8). Sobald die Reiter
  eingreifen (`linie_reiter`), gewinnt der Spieler wieder 7/8, mit
  Verlusten um ein Drittel. Die Linie allein genügt nicht mehr; sie
  braucht eine bewegliche Reserve.
- **Palisade:** Die Räuber bauen jetzt Rammbock und Turm. Mit 128
  Räubern (neue Vorgabe, vorher 192) hält die Phalanx hinter dem Tor
  (8/8), aber die über den Turm Eingesickerten plündern sechs Häuser,
  wenn niemand sie jagt. Mit Reitern als Reserve bleiben es unter einem
  Haus. Mit 160 Räubern kippt es, mit 192 verliert die starre
  Verteidigung immer.
- **Horde:** kaum Unterschied. Die Horde umgeht die Linie, verliert
  aber genauso.
- **Angriff auf die Siedlung ohne Wall:** Der Phalanxstoß gewinnt
  gegen die kluge Siedlung 8/8 mit 31 % Verlusten, gegen die alte
  0/8. Das liegt an der neuen Reiterregel: die alte KI schickt die
  Reiter blind in die Front, die kluge hält sie zurück, rückt dafür mit
  der Linie vor und lässt sich dann ordentlich schlagen. Freier Angriff
  und „Vorrücken dann Angriff“ verlieren gegen beide.
- **Angriff auf die Siedlung mit Wall:** Bei gleicher Stärke (75 gegen
  75) schlägt die kluge Siedlung den Phalanxstoß durchs Tor (1/8): sie
  deckt das Tor von innen, dreht die Front und rückt vor, während die
  Angreifer noch durch die Lücke drängen. Die alte KI verliert 8/8.
  Mit weniger Verteidigern wird es schaffbar:

| Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |
|---|---|---|---|---|---|---|---|---|
| angriff_wall | tor_phalanx | klug | 8/8 | 21% | 72% | 0.0 | 74 s | halten×8 |
| angriff_wall | tor_phalanx | klug | 8/8 | 43% | 70% | 0.0 | 74 s | halten×8 |

  Die erste Zeile ist 50 Verteidiger, die zweite 60. Empfehlung für den
  Regler: etwa zwei Drittel der eigenen Stärke.

## Lernen über Schlachten hinweg (Stufe 3)

Dieselbe Taktik mehrmals hintereinander mit gemeinsamem Gedächtnis
(`--lernen`). Die Gewichte sind die Faktoren, mit denen die Punktzahl
eines Plans beim nächsten Mal multipliziert wird (0,5 bis 1,5).

## Lernen: offen / linie, 8 Schlachten hintereinander

| Nr | Ausgang | Stadt gefallen | Feind gefallen | Häuser verloren | Pläne | Gewichte |
|---|---|---|---|---|---|---|
| 1 | niederlage | 35/75 | 42/128 | 8 | zermuerben → umgehen_west → frontal | {'zermuerben': 1.0, 'umgehen_west': 0.98, 'frontal': 1.36} |
| 2 | sieg | 28/75 | 56/128 | 1 | frontal → umgehen_west → frontal → umgehen_west | {'zermuerben': 1.0, 'umgehen_west': 0.96, 'frontal': 1.1} |
| 3 | niederlage | 31/75 | 42/128 | 8 | zermuerben → umgehen_west → frontal | {'zermuerben': 1.0, 'umgehen_west': 0.97, 'frontal': 1.13} |
| 4 | niederlage | 55/75 | 23/128 | 8 | zermuerben → umgehen_west → frontal | {'zermuerben': 1.0, 'umgehen_west': 0.98, 'frontal': 1.38} |
| 5 | sieg | 13/75 | 54/128 | 0 | frontal → umgehen_west → frontal → umgehen_west | {'zermuerben': 1.0, 'umgehen_west': 0.96, 'frontal': 1.29} |
| 6 | sieg | 12/75 | 50/128 | 0 | frontal → umgehen_west | {'zermuerben': 1.0, 'umgehen_west': 0.86, 'frontal': 1.22} |
| 7 | sieg | 11/75 | 65/128 | 0 | zermuerben → frontal → umgehen_ost → frontal → umgehen_west | {'zermuerben': 1.0, 'umgehen_west': 0.85, 'frontal': 0.78, 'umgehen_ost': 0.74} |
| 8 | niederlage | 34/75 | 30/128 | 8 | zermuerben → umgehen_west → frontal | {'zermuerben': 1.0, 'umgehen_west': 0.85, 'frontal': 0.98, 'umgehen_ost': 0.74} |

Die Räuber wechseln zwischen Zermürben und Frontal, je nachdem, was
zuletzt mehr gebracht hat; die Ausgänge schwanken entsprechend.

## Lernen: palisade / tor_reserve, 8 Schlachten hintereinander

| Nr | Ausgang | Stadt gefallen | Feind gefallen | Häuser verloren | Pläne | Gewichte |
|---|---|---|---|---|---|---|
| 1 | sieg | 15/75 | 70/128 | 0 | turm → belagern → zermuerben → umgehen_west → zermuerben → umgehen_ost | {'turm': 0.8, 'belagern': 1.4, 'zermuerben': 0.96, 'umgehen_west': 0.73, 'umgehen_ost': 0.5} |
| 2 | sieg | 15/75 | 75/128 | 0 | tor → belagern → zermuerben → frontal → umgehen_west | {'turm': 0.8, 'belagern': 1.19, 'zermuerben': 1.09, 'umgehen_west': 0.61, 'umgehen_ost': 0.5, 'tor': 0.94, 'frontal': 0.5} |
| 3 | sieg | 34/75 | 99/128 | 1 | turm → belagern → frontal → umgehen_west | {'turm': 0.85, 'belagern': 1.2, 'zermuerben': 1.09, 'umgehen_west': 0.68, 'umgehen_ost': 0.5, 'tor': 0.94, 'frontal': 0.5} |
| 4 | niederlage | 34/75 | 80/128 | 8 | turm → belagern → frontal | {'turm': 0.85, 'belagern': 1.22, 'zermuerben': 1.09, 'umgehen_west': 0.68, 'umgehen_ost': 0.5, 'tor': 0.94, 'frontal': 0.5} |
| 5 | sieg | 33/75 | 96/128 | 1 | turm → belagern → frontal → umgehen_west | {'turm': 0.84, 'belagern': 1.2, 'zermuerben': 1.09, 'umgehen_west': 0.72, 'umgehen_ost': 0.5, 'tor': 0.94, 'frontal': 0.5} |
| 6 | sieg | 35/75 | 98/128 | 1 | turm → belagern → frontal → umgehen_west | {'turm': 0.84, 'belagern': 1.17, 'zermuerben': 1.09, 'umgehen_west': 0.74, 'umgehen_ost': 0.5, 'tor': 0.94, 'frontal': 0.5} |
| 7 | sieg | 15/75 | 85/128 | 0 | turm → belagern → zermuerben → umgehen_west | {'turm': 0.84, 'belagern': 1.25, 'zermuerben': 1.09, 'umgehen_west': 0.51, 'umgehen_ost': 0.5, 'tor': 0.94, 'frontal': 0.5} |
| 8 | sieg | 35/75 | 99/128 | 1 | turm → belagern → frontal → umgehen_west | {'turm': 0.82, 'belagern': 1.27, 'zermuerben': 1.09, 'umgehen_west': 0.57, 'umgehen_ost': 0.5, 'tor': 0.94, 'frontal': 0.5} |

Umgehen im Osten und Frontal haben sich nicht gelohnt und stehen auf
dem Minimum; Belagern wird bevorzugt. Die Siege bleiben, weil die
Reiter die Eingesickerten jagen.

## Lernen: angriff_offen / phalanxstoss, 6 Schlachten hintereinander

| Nr | Ausgang | Stadt gefallen | Feind gefallen | Häuser verloren | Pläne | Gewichte |
|---|---|---|---|---|---|---|
| 1 | sieg | 19/75 | 55/75 | 0 | halten → vorruecken → halten | {'halten': 0.5, 'vorruecken': 0.97} |
| 2 | niederlage | 67/75 | 41/75 | 0 | vorruecken | {'halten': 0.5, 'vorruecken': 1.42} |
| 3 | niederlage | 68/75 | 39/75 | 0 | vorruecken | {'halten': 0.5, 'vorruecken': 1.5} |
| 4 | niederlage | 67/75 | 40/75 | 0 | vorruecken | {'halten': 0.5, 'vorruecken': 1.5} |
| 5 | niederlage | 65/75 | 43/75 | 0 | vorruecken | {'halten': 0.5, 'vorruecken': 1.5} |
| 6 | niederlage | 68/75 | 41/75 | 0 | vorruecken | {'halten': 0.5, 'vorruecken': 1.5} |

Deutlichster Effekt: Nach der ersten verlorenen Schlacht steht „Halten“
auf 0,5, die Siedlung rückt von Anfang an vor und trifft die Phalanx,
bevor sie steht. Der gescriptete Phalanxstoß verliert danach jedes Mal.
Ein Spieler müsste die Linie früher schließen oder die Reiter gegen die
vorrückende Linie führen.

## Offene Punkte

- Das Ereignisprotokoll wird beim Klettern von „Formation aufgelöst /
  neu gebildet“ überschwemmt; die Meldungen könnten zusammengefasst
  werden.
- Die Räuber sammeln sich beim Belagern sehr dicht vor dem Turm; eine
  zweite Turmstelle oder Leitern aus eigener Hand wären der nächste
  Schritt.
- Die Siedlung mit Wall macht noch keinen Ausfall durchs offene Tor
  gegen abgesessene oder aufgelöste Gruppen; das wäre der nächste Plan.
