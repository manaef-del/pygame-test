# Simulation: Spielertaktiken gegen die Gegner-KI

## Lauf 6 (29. September 2026): Peltasten der KI plänkeln

Reine Peltastengruppen der Gegnerseite (die Siedlung stellt sie, Räuber
mischen nur ein Fünftel Peltasten in ihre Haufen) plänkeln jetzt wie die
des Spielers: heran auf Wurfweite, werfen, ausweichen, hinter oder neben
der eigenen Phalanx werfen. Vergleich vorher/nachher mit denselben vier
Seeds: Standardtruppe, Angriff ohne Wall, Phalanxstoß, kluge KI, die
Aufstellung der Siedlung erzwungen.

| Gegner | Siege vorher | Verlust Spieler / Siedlung vorher | Dauer vorher | Siege nachher | Verlust Spieler / Siedlung nachher | Dauer nachher |
|---|---|---|---|---|---|---|
| spiegel | 4/4 | 13% / 39% | 78 s | 4/4 | 9% / 34% | 43 s |
| schwere_phalanx | 1/4 | 57% / 49% | 183 s | 0/4 | 58% / 45% | 169 s |
| peltastenschwarm | 4/4 | 10% / 34% | 65 s | 4/4 | 14% / 45% | 72 s |

Der Ausgang ändert sich kaum. Die Peltasten der Siedlung verschießen
ihre Speere jetzt vollständig und früher (die Schlacht gegen das
Spiegelbild ist fast doppelt so schnell vorbei), gegen den
Peltastenschwarm kostet das den Spieler etwas mehr. Dafür verlassen die
Peltasten die Deckung ihrer Linie, um um ihr Ende herum zu werfen, und
werden dort von Reitern und stürmenden Hopliten gefasst: die Siedlung
verliert entsprechend mehr. Gegen anrückende Hopliten halten sie den
Abstand (Peltasten laufen 1,7 gegen 1,0 Kacheln je Sekunde), gegen
Reiter nicht.

## Lauf 5 (29. September 2026): Moral für beide Seiten, erhöhter Wehrgang, eigene Aufstellung der Siedlung

Stand des Commits, der diesen Abschnitt einführt: Gruppen beider Seiten
brechen nach etwa einem Drittel Verlusten aus der Flanke (schwere später),
Nachbarn stecken sich an, eine aussichtslose Seite verliert Moral von
selbst; vom Boden aus kämpft niemand gegen den Wehrgang; die Siedlung
stellt nach Doktrin (meist die schwere Phalanx). Sechs Seeds je Zeile.

| Truppe | Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |
|---|---|---|---|---|---|---|---|---|---|
| standard | offen | linie | klug | 6/6 | 19% | 49% | 0.3 | 32 s | flankieren×6, frontal×6, umgehen_west×4 |
| standard | offen | linie_aktiv | klug | 6/6 | 23% | 48% | 0.0 | 28 s | flankieren×6, frontal×4, umgehen_west×3 |
| standard | horde | vorruecken | klug | 6/6 | 7% | 41% | 0.0 | 43 s | lagern×6, flankieren×6, frontal×6, umgehen_west×6 |
| standard | angriff_offen | phalanxstoss | klug | 0/6 | 51% | 32% | 0.0 | 67 s | halten×6, vorruecken×6 |
| standard | palisade | tor_reserve | klug | 1/6 | 38% | 42% | 3.3 | 71 s | turm×6, belagern×6, frontal×3, flankieren×1, umgehen_west×1 |
| standard | angriff_wall | tor_phalanx | klug | 0/6 | 47% | 31% | 0.0 | 125 s | halten×6, vorruecken×6 |
| ohne_reiter | offen | linie | klug | 6/6 | 4% | 40% | 0.0 | 29 s | flankieren×6, zermuerben×6, umgehen_west×6, frontal×1 |
| ohne_reiter | offen | linie_aktiv | klug | 6/6 | 1% | 45% | 0.2 | 42 s | flankieren×6, zermuerben×6, umgehen_west×6, frontal×4, umgehen_ost×2 |
| ohne_reiter | horde | vorruecken | klug | 6/6 | 10% | 45% | 0.0 | 49 s | lagern×6, flankieren×6, frontal×6, zermuerben×5, umgehen_west×1 |
| ohne_reiter | angriff_offen | phalanxstoss | klug | 0/6 | 42% | 0% | 0.0 | 34 s | halten×6, vorruecken×6 |
| ohne_reiter | palisade | tor_reserve | klug | 6/6 | 3% | 52% | 0.0 | 80 s | turm×6, belagern×6, flankieren×6, umgehen_ost×6 |
| ohne_reiter | angriff_wall | tor_phalanx | klug | 0/6 | 39% | 13% | 0.0 | 39 s | halten×6, vorruecken×6 |
| gemischt | offen | linie | klug | 6/6 | 24% | 31% | 0.0 | 29 s | flankieren×6, umgehen_west×6, frontal×2 |
| gemischt | offen | linie_aktiv | klug | 6/6 | 5% | 68% | 2.2 | 25 s | flankieren×6, frontal×6, umgehen_west×6 |
| gemischt | horde | vorruecken | klug | 6/6 | 9% | 29% | 0.0 | 43 s | lagern×6, flankieren×6, umgehen_west×6 |
| gemischt | angriff_offen | phalanxstoss | klug | 0/6 | 56% | 25% | 0.0 | 70 s | halten×6, vorruecken×3 |
| gemischt | palisade | tor_reserve | klug | 0/6 | 5% | 12% | 8.0 | 56 s | turm×6, belagern×6 |
| gemischt | angriff_wall | tor_phalanx | klug | 0/6 | 43% | 41% | 0.0 | 57 s | halten×6 |
| reiterlastig | offen | linie | klug | 6/6 | 22% | 42% | 2.7 | 37 s | flankieren×6, frontal×6, umgehen_west×2 |
| reiterlastig | offen | linie_aktiv | klug | 6/6 | 17% | 55% | 0.0 | 28 s | flankieren×6, umgehen_west×6 |
| reiterlastig | horde | vorruecken | klug | 6/6 | 7% | 38% | 0.0 | 43 s | lagern×6, flankieren×6, umgehen_west×6, frontal×3 |
| reiterlastig | angriff_offen | phalanxstoss | klug | 0/6 | 47% | 26% | 0.0 | 69 s | halten×6, vorruecken×6 |
| reiterlastig | palisade | tor_reserve | klug | 1/6 | 34% | 47% | 6.7 | 79 s | turm×6, belagern×6, frontal×5, flankieren×1, umgehen_west×1 |
| reiterlastig | angriff_wall | tor_phalanx | klug | 0/6 | 62% | 3% | 0.0 | 270 s | halten×6, vorruecken×6 |
| zwei_phalangen | offen | linie | klug | 1/6 | 28% | 34% | 6.7 | 37 s | flankieren×6, umgehen_west×6, frontal×5 |
| zwei_phalangen | offen | linie_aktiv | klug | 6/6 | 28% | 46% | 0.2 | 30 s | flankieren×6, umgehen_west×5, frontal×2 |
| zwei_phalangen | horde | vorruecken | klug | 6/6 | 17% | 41% | 0.0 | 47 s | lagern×6, flankieren×6, umgehen_west×6, frontal×6 |
| zwei_phalangen | angriff_offen | phalanxstoss | klug | 4/6 | 33% | 38% | 0.0 | 55 s | halten×6, vorruecken×6 |
| zwei_phalangen | palisade | tor_reserve | klug | 0/6 | 42% | 28% | 8.0 | 68 s | turm×6, belagern×6, frontal×6 |
| zwei_phalangen | angriff_wall | tor_phalanx | klug | 0/6 | 50% | 28% | 0.0 | 125 s | halten×6, vorruecken×6 |

### Alle Szenarien, beide KIs (standard, 8 Seeds)

| Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |
|---|---|---|---|---|---|---|---|---|
| offen | linie | einfach | 8/8 | 0% | 27% | 0.0 | 18 s | – |
| offen | linie | klug | 7/8 | 22% | 47% | 1.4 | 33 s | flankieren×8, frontal×8, umgehen_west×6 |
| offen | linie_reiter | einfach | 8/8 | 0% | 27% | 0.0 | 18 s | – |
| offen | linie_reiter | klug | 7/8 | 21% | 50% | 0.0 | 27 s | flankieren×8, umgehen_west×7, frontal×5 |
| offen | linie_aktiv | einfach | 8/8 | 0% | 31% | 0.0 | 18 s | – |
| offen | linie_aktiv | klug | 8/8 | 24% | 48% | 0.0 | 28 s | flankieren×8, frontal×6, umgehen_west×4 |
| offen | linie_tief | einfach | 8/8 | 0% | 44% | 0.0 | 25 s | – |
| offen | linie_tief | klug | 8/8 | 20% | 50% | 0.0 | 27 s | flankieren×8, umgehen_west×7, frontal×2 |
| offen | passiv | einfach | 2/8 | 33% | 24% | 6.8 | 27 s | – |
| offen | passiv | klug | 8/8 | 21% | 25% | 0.6 | 25 s | frontal×8 |
| offen | angriff | einfach | 1/8 | 24% | 31% | 7.9 | 26 s | – |
| offen | angriff | klug | 5/8 | 34% | 43% | 7.4 | 35 s | frontal×8 |
| palisade | tor_halten | einfach | 8/8 | 0% | 48% | 0.0 | 33 s | – |
| palisade | tor_halten | klug | 1/8 | 38% | 30% | 7.0 | 73 s | turm×8, belagern×8, frontal×7, flankieren×1, umgehen_west×1 |
| palisade | tor_reserve | einfach | 8/8 | 0% | 48% | 0.0 | 33 s | – |
| palisade | tor_reserve | klug | 1/8 | 38% | 40% | 2.9 | 69 s | turm×8, belagern×8, frontal×3, flankieren×1, umgehen_west×1 |
| palisade | tor_leiter | einfach | 8/8 | 0% | 48% | 0.0 | 33 s | – |
| palisade | tor_leiter | klug | 5/8 | 29% | 58% | 4.5 | 79 s | turm×8, belagern×8, frontal×7, zermuerben×7, umgehen_ost×7, flankieren×1, umgehen_west×1 |
| palisade | passiv | einfach | 8/8 | 26% | 39% | 0.1 | 43 s | – |
| palisade | passiv | klug | 8/8 | 26% | 38% | 0.1 | 44 s | tor×8, frontal×8 |
| horde | vorruecken | einfach | 8/8 | 0% | 48% | 0.0 | 33 s | – |
| horde | vorruecken | klug | 8/8 | 7% | 42% | 0.0 | 43 s | lagern×8, flankieren×8, frontal×8, umgehen_west×8 |
| horde | angriff | einfach | 8/8 | 19% | 42% | 0.0 | 19 s | – |
| horde | angriff | klug | 8/8 | 28% | 38% | 0.0 | 19 s | lagern×8, frontal×8 |
| angriff_offen | phalanxstoss | einfach | 0/8 | 53% | 4% | 0.0 | 66 s | – |
| angriff_offen | phalanxstoss | klug | 0/8 | 51% | 33% | 0.0 | 67 s | halten×8, vorruecken×8 |
| angriff_offen | vorruecken | einfach | 0/8 | 40% | 0% | 0.0 | 53 s | – |
| angriff_offen | vorruecken | klug | 0/8 | 47% | 7% | 0.0 | 50 s | halten×8, vorruecken×8 |
| angriff_offen | angriff | einfach | 0/8 | 40% | 0% | 0.0 | 18 s | – |
| angriff_offen | angriff | klug | 0/8 | 40% | 0% | 0.0 | 18 s | halten×8, vorruecken×8 |
| angriff_wall | tor_phalanx | einfach | 0/8 | 62% | 12% | 0.0 | 122 s | – |
| angriff_wall | tor_phalanx | klug | 0/8 | 47% | 32% | 0.0 | 125 s | halten×8, vorruecken×8 |
| angriff_wall | belagerung | einfach | 0/8 | 94% | 0% | 0.0 | 300 s | – |
| angriff_wall | belagerung | klug | 0/8 | 51% | 11% | 0.0 | 72 s | halten×8, vorruecken×2 |

### Was sich geändert hat

- **Verteidigung und Horde bleiben, wie sie waren**, mit weniger
  Gefallenen: Gruppen fliehen jetzt, statt bis zum letzten Mann zu
  stehen (Verluste zählen nur Gefallene). Der Leiterfuß bleibt die
  Antwort auf den Turm (5/8), das Tor allein hält nicht (1/8).
- **Angriffe auf die Siedlung gehen mit den Skripten immer verloren.**
  Drei Dinge kommen zusammen: Die Siedlung stellt die schwere Phalanx,
  sie rückt vor, sobald Peltasten sie beschießen, und trifft die Linie
  des Spielers im Anmarsch, bevor sie steht; die gebundenen Männer
  erreichen ihre Plätze nicht mehr, die Gruppe kämpft ohne Bonus und
  bricht nach einem Drittel Verlusten. Ein Test bestätigt, dass eine
  *stehende* Phalanx, die geschlossen anläuft, an der Front sehr wohl
  steht (`in_line` sofort bei Ankunft). Der Fehler der Skripte ist, im
  Wurfbereich der eigenen Peltasten aufzumarschieren.
- **Für den Spieler:** außer Reichweite aufstellen (mehr als fünf
  Kacheln), die Peltasten erst werfen lassen, wenn die Linie steht, den
  Vorstoß der Siedlung stehend empfangen und die Reiter erst dann in die
  Flanke schicken, wenn die feindliche Linie gebunden ist. Reiterlastige
  Truppen haben am Wall keine Chance (3 % Feindverluste in 270 s), ohne
  Reiter fehlt der Flankenstoß.
- Die Zahlen der Angriffe sind also eher zu schlecht; sie messen dumme
  Skripte gegen eine Siedlung, die die Schwächen kennt. Wer sie spielbar
  halten will, setzt den Gegner-Regler auf etwa zwei Drittel.

## Lauf 4 (29. September 2026): Welche Aufstellung schlägt welche

Bisher stellte die Siedlung beim Angriff dieselbe Mischung wie der
Spieler. Für den Wechsel auf eigene Aufstellungen wurde eine Matrix
gespielt: sechs Spielertruppen (je 75 Mann) gegen sechs Aufstellungen
der Siedlung (`game/doctrine.py`, je 75 Mann), Angriff ohne Wall mit
Phalanxstoß und Angriff mit Wall mit Rammbock und Phalanx durchs Tor,
vier Seeds, kluge KI. Schaden sammelt sich seit diesem Lauf auf schon
angeschlagenen Männern, so dass Verluste nach und nach eintreten statt
alle auf einmal.

| Aufstellung der Siedlung | Mischung |
|---|---|
| spiegel | wie der Spieler |
| hoplitenwall | 70 Hopliten (schwer, mittel, leicht), 30 Peltasten, keine Reiter |
| schwere_phalanx | 80 schwere und mittlere Hopliten, 20 Peltasten |
| ausgewogen | 50 Hopliten, 20 Peltasten, 30 Reiter |
| reiterlastig | 30 Hopliten, 20 Peltasten, 50 Reiter |
| peltastenschwarm | 35 Hopliten, 45 Peltasten in zwei Gruppen, 20 Reiter |

| Spieler | Szenario | Gegner | Siege Spieler | Verlust Spieler | Verlust Siedlung | Dauer |
|---|---|---|---|---|---|---|
| standard | angriff_offen | spiegel | 4/4 | 22% | 68% | 69 s |
| standard | angriff_offen | hoplitenwall | 4/4 | 60% | 71% | 84 s |
| standard | angriff_offen | schwere_phalanx | 0/4 | 97% | 49% | 91 s |
| standard | angriff_offen | ausgewogen | 4/4 | 29% | 67% | 78 s |
| standard | angriff_offen | reiterlastig | 3/4 | 26% | 62% | 147 s |
| standard | angriff_offen | peltastenschwarm | 4/4 | 21% | 65% | 67 s |
| standard | angriff_wall | spiegel | 4/4 | 45% | 69% | 55 s |
| standard | angriff_wall | hoplitenwall | 0/4 | 95% | 62% | 121 s |
| standard | angriff_wall | schwere_phalanx | 0/4 | 98% | 49% | 125 s |
| standard | angriff_wall | ausgewogen | 4/4 | 40% | 72% | 54 s |
| standard | angriff_wall | reiterlastig | 4/4 | 27% | 69% | 126 s |
| standard | angriff_wall | peltastenschwarm | 4/4 | 50% | 72% | 50 s |
| ohne_reiter | angriff_offen | spiegel | 4/4 | 8% | 67% | 40 s |
| ohne_reiter | angriff_offen | hoplitenwall | 0/4 | 95% | 2% | 41 s |
| ohne_reiter | angriff_offen | schwere_phalanx | 0/4 | 95% | 1% | 42 s |
| ohne_reiter | angriff_offen | ausgewogen | 0/4 | 93% | 22% | 45 s |
| ohne_reiter | angriff_offen | reiterlastig | 1/4 | 32% | 62% | 237 s |
| ohne_reiter | angriff_offen | peltastenschwarm | 1/4 | 93% | 45% | 49 s |
| ohne_reiter | angriff_wall | spiegel | 3/4 | 73% | 62% | 58 s |
| ohne_reiter | angriff_wall | hoplitenwall | 0/4 | 88% | 38% | 53 s |
| ohne_reiter | angriff_wall | schwere_phalanx | 0/4 | 90% | 21% | 51 s |
| ohne_reiter | angriff_wall | ausgewogen | 1/4 | 87% | 41% | 63 s |
| ohne_reiter | angriff_wall | reiterlastig | 1/4 | 86% | 54% | 138 s |
| ohne_reiter | angriff_wall | peltastenschwarm | 4/4 | 56% | 62% | 46 s |
| gemischt | angriff_offen | spiegel | 0/4 | 72% | 33% | 51 s |
| gemischt | angriff_offen | hoplitenwall | 0/4 | 100% | 31% | 106 s |
| gemischt | angriff_offen | schwere_phalanx | 0/4 | 100% | 31% | 98 s |
| gemischt | angriff_offen | ausgewogen | 0/4 | 74% | 38% | 56 s |
| gemischt | angriff_offen | reiterlastig | 0/4 | 68% | 53% | 47 s |
| gemischt | angriff_offen | peltastenschwarm | 0/4 | 21% | 20% | 33 s |
| gemischt | angriff_wall | spiegel | 4/4 | 14% | 73% | 49 s |
| gemischt | angriff_wall | hoplitenwall | 4/4 | 37% | 64% | 79 s |
| gemischt | angriff_wall | schwere_phalanx | 1/4 | 80% | 62% | 79 s |
| gemischt | angriff_wall | ausgewogen | 4/4 | 13% | 78% | 49 s |
| gemischt | angriff_wall | reiterlastig | 4/4 | 5% | 65% | 44 s |
| gemischt | angriff_wall | peltastenschwarm | 4/4 | 6% | 68% | 44 s |
| reiterlastig | angriff_offen | spiegel | 4/4 | 32% | 64% | 80 s |
| reiterlastig | angriff_offen | hoplitenwall | 0/4 | 96% | 31% | 73 s |
| reiterlastig | angriff_offen | schwere_phalanx | 0/4 | 96% | 31% | 70 s |
| reiterlastig | angriff_offen | ausgewogen | 4/4 | 22% | 64% | 71 s |
| reiterlastig | angriff_offen | reiterlastig | 4/4 | 40% | 65% | 84 s |
| reiterlastig | angriff_offen | peltastenschwarm | 4/4 | 24% | 73% | 66 s |
| reiterlastig | angriff_wall | spiegel | 4/4 | 77% | 66% | 133 s |
| reiterlastig | angriff_wall | hoplitenwall | 0/4 | 97% | 22% | 129 s |
| reiterlastig | angriff_wall | schwere_phalanx | 3/4 | 84% | 70% | 137 s |
| reiterlastig | angriff_wall | ausgewogen | 4/4 | 57% | 73% | 131 s |
| reiterlastig | angriff_wall | reiterlastig | 4/4 | 63% | 67% | 135 s |
| reiterlastig | angriff_wall | peltastenschwarm | 1/4 | 86% | 31% | 114 s |
| zwei_phalangen | angriff_offen | spiegel | 4/4 | 34% | 67% | 47 s |
| zwei_phalangen | angriff_offen | hoplitenwall | 1/4 | 88% | 61% | 92 s |
| zwei_phalangen | angriff_offen | schwere_phalanx | 0/4 | 92% | 41% | 72 s |
| zwei_phalangen | angriff_offen | ausgewogen | 4/4 | 23% | 60% | 53 s |
| zwei_phalangen | angriff_offen | reiterlastig | 4/4 | 49% | 65% | 90 s |
| zwei_phalangen | angriff_offen | peltastenschwarm | 4/4 | 5% | 59% | 40 s |
| zwei_phalangen | angriff_wall | spiegel | 4/4 | 22% | 72% | 51 s |
| zwei_phalangen | angriff_wall | hoplitenwall | 0/4 | 92% | 50% | 126 s |
| zwei_phalangen | angriff_wall | schwere_phalanx | 0/4 | 98% | 49% | 128 s |
| zwei_phalangen | angriff_wall | ausgewogen | 4/4 | 29% | 69% | 126 s |
| zwei_phalangen | angriff_wall | reiterlastig | 4/4 | 30% | 71% | 132 s |
| zwei_phalangen | angriff_wall | peltastenschwarm | 4/4 | 61% | 67% | 55 s |
| peltastenlastig | angriff_offen | spiegel | 4/4 | 2% | 56% | 36 s |
| peltastenlastig | angriff_offen | hoplitenwall | 0/4 | 88% | 29% | 74 s |
| peltastenlastig | angriff_offen | schwere_phalanx | 0/4 | 89% | 31% | 77 s |
| peltastenlastig | angriff_offen | ausgewogen | 4/4 | 48% | 62% | 67 s |
| peltastenlastig | angriff_offen | reiterlastig | 4/4 | 26% | 67% | 94 s |
| peltastenlastig | angriff_offen | peltastenschwarm | 4/4 | 8% | 66% | 39 s |
| peltastenlastig | angriff_wall | spiegel | 4/4 | 64% | 76% | 66 s |
| peltastenlastig | angriff_wall | hoplitenwall | 0/4 | 96% | 32% | 94 s |
| peltastenlastig | angriff_wall | schwere_phalanx | 0/4 | 94% | 19% | 75 s |
| peltastenlastig | angriff_wall | ausgewogen | 0/4 | 87% | 45% | 116 s |
| peltastenlastig | angriff_wall | reiterlastig | 4/4 | 76% | 68% | 110 s |
| peltastenlastig | angriff_wall | peltastenschwarm | 0/4 | 99% | 54% | 53 s |

### Was daraus folgt

- **Schwere Hopliten schlagen fast alles.** Gegen `schwere_phalanx`
  gewinnt kein gescripteter Angriff, weder ohne noch mit Wall, mit einer
  Ausnahme: reiterlastige Angreifer am Wall (3/4), weil die schwere
  Phalanx dort langsam ist und die Reiter das Tor früher durchbrechen.
  `hoplitenwall` ist fast so gut und gegen Reiter noch besser.
- **Reiter der Siedlung sind gegen einen Phalanxstoß wertlos.** Alle
  Aufstellungen mit vielen Reitern (`ausgewogen`, `reiterlastig`,
  `spiegel`) verlieren im Feld 4/4 gegen jede Spielermischung außer der
  großen gemischten Gruppe. Reiter verteidigen schlecht; sie greifen an.
- **Der Peltastenschwarm ist eine Falle**: gegen Fußvolk ohne Reiter
  hält er (Wall 4/4 für den Spieler, aber im Feld 1/4), gegen alles mit
  Reitern nicht.
- **Zuordnung** (`COUNTERS` in `game/doctrine.py`): ausgewogene, reiter-
  lose, peltastenlastige und Ein-Block-Truppen bekommen die schwere
  Phalanx, reiterlastige den Hoplitenwall (mehr Peltasten gegen die
  Reiter, am Wall 0/4 statt 3/4).
- Die Siedlung merkt sich außerdem je Spielerklasse, wie jede
  Aufstellung ausging, und wechselt, wenn eine andere in den letzten
  Schlachten besser abschnitt. Die Meldung „Die Siedlung stellt: …“
  steht zu Beginn im Ereignisprotokoll.
- Für den Spieler heißt das: Gegen die schwere Phalanx hilft der reine
  Phalanxstoß nicht mehr. Gefragt sind Peltasten, die die Front
  beschießen, bevor die Linie anläuft, und Reiter, die die schwere,
  langsame Linie umgehen, sobald sie gebunden ist.

## Lauf 3 (29. September 2026): Handgemenge bindet

Stand des Commits, der diesen Abschnitt einführt: Männer mit einem
Gegner in Reichweite stehen fest, eine Gruppe im Nahkampf kommt nur mit
einem Drittel ihrer Geschwindigkeit vom Fleck, Lösen kostet vier
Sekunden Verwundbarkeit (Reiter eine), und die Phalanx bekommt ihren
Bonus erst, wenn fast alle Männer stehen. Sonst wie Lauf 2.

### Fünf Truppenmischungen (je 75 Mann, sechs Seeds, kluge KI)

| Truppe | Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |
|---|---|---|---|---|---|---|---|---|---|
| standard | offen | linie | klug | 5/6 | 28% | 58% | 1.3 | 40 s | flankieren×6, frontal×6, umgehen_west×5 |
| standard | offen | linie_aktiv | klug | 6/6 | 43% | 54% | 0.2 | 35 s | flankieren×6, umgehen_west×4, frontal×4 |
| standard | horde | vorruecken | klug | 6/6 | 7% | 48% | 0.0 | 44 s | lagern×6, flankieren×6, frontal×6, umgehen_west×6 |
| standard | angriff_offen | phalanxstoss | klug | 6/6 | 18% | 73% | 0.0 | 75 s | halten×6, vorruecken×6 |
| standard | palisade | tor_reserve | klug | 1/6 | 56% | 55% | 5.7 | 88 s | turm×6, belagern×6, frontal×5, flankieren×1, zermuerben×1, umgehen_west×1 |
| standard | angriff_wall | tor_phalanx | klug | 6/6 | 28% | 70% | 0.0 | 52 s | halten×6 |
| ohne_reiter | offen | linie | klug | 6/6 | 8% | 48% | 0.0 | 29 s | flankieren×6, frontal×5, umgehen_ost×4, zermuerben×1, umgehen_west×1 |
| ohne_reiter | offen | linie_aktiv | klug | 6/6 | 1% | 57% | 0.0 | 28 s | flankieren×6, frontal×5, umgehen_ost×4, umgehen_west×2, zermuerben×1 |
| ohne_reiter | horde | vorruecken | klug | 6/6 | 12% | 47% | 0.0 | 50 s | lagern×6, flankieren×6, frontal×6 |
| ohne_reiter | angriff_offen | phalanxstoss | klug | 6/6 | 2% | 67% | 0.0 | 42 s | halten×6, vorruecken×6 |
| ohne_reiter | palisade | tor_reserve | klug | 6/6 | 3% | 68% | 0.0 | 83 s | turm×6, belagern×6, flankieren×6, zermuerben×6, umgehen_ost×6 |
| ohne_reiter | angriff_wall | tor_phalanx | klug | 6/6 | 67% | 67% | 0.0 | 64 s | halten×6, vorruecken×2 |
| gemischt | offen | linie | klug | 6/6 | 33% | 42% | 0.0 | 34 s | flankieren×6, umgehen_west×6, frontal×6 |
| gemischt | offen | linie_aktiv | klug | 6/6 | 1% | 63% | 2.0 | 29 s | flankieren×6, frontal×6, umgehen_west×6 |
| gemischt | horde | vorruecken | klug | 6/6 | 9% | 38% | 0.0 | 50 s | lagern×6, flankieren×6, umgehen_west×6, frontal×6 |
| gemischt | angriff_offen | phalanxstoss | klug | 0/6 | 79% | 27% | 0.0 | 51 s | halten×6, vorruecken×6 |
| gemischt | palisade | tor_reserve | klug | 0/6 | 3% | 12% | 8.0 | 56 s | turm×6, belagern×6 |
| gemischt | angriff_wall | tor_phalanx | klug | 6/6 | 7% | 72% | 0.0 | 50 s | halten×6 |
| reiterlastig | offen | linie | klug | 6/6 | 50% | 53% | 3.8 | 47 s | flankieren×6, frontal×6 |
| reiterlastig | offen | linie_aktiv | klug | 6/6 | 29% | 63% | 0.0 | 27 s | flankieren×6, umgehen_west×6 |
| reiterlastig | horde | vorruecken | klug | 6/6 | 8% | 53% | 0.0 | 47 s | lagern×6, flankieren×6, umgehen_west×6, frontal×6 |
| reiterlastig | angriff_offen | phalanxstoss | klug | 6/6 | 33% | 72% | 0.0 | 83 s | halten×6, vorruecken×6 |
| reiterlastig | palisade | tor_reserve | klug | 4/6 | 61% | 68% | 4.0 | 90 s | turm×6, belagern×6, frontal×5, umgehen_west×3, flankieren×2, zermuerben×1 |
| reiterlastig | angriff_wall | tor_phalanx | klug | 1/6 | 93% | 64% | 0.0 | 140 s | halten×6, vorruecken×5 |
| zwei_phalangen | offen | linie | klug | 6/6 | 40% | 49% | 0.2 | 35 s | flankieren×6, umgehen_west×6, frontal×2 |
| zwei_phalangen | offen | linie_aktiv | klug | 6/6 | 41% | 56% | 0.0 | 28 s | flankieren×6, umgehen_west×5 |
| zwei_phalangen | horde | vorruecken | klug | 6/6 | 22% | 55% | 0.0 | 51 s | lagern×6, flankieren×6, umgehen_west×6, frontal×6 |
| zwei_phalangen | angriff_offen | phalanxstoss | klug | 6/6 | 18% | 70% | 0.0 | 43 s | halten×6, vorruecken×6 |
| zwei_phalangen | palisade | tor_reserve | klug | 0/6 | 65% | 33% | 8.0 | 73 s | turm×6, belagern×6, frontal×6 |
| zwei_phalangen | angriff_wall | tor_phalanx | klug | 6/6 | 9% | 72% | 0.0 | 50 s | halten×6 |

Neu dazu die Taktik `tor_leiter` (Palisade): Phalanx hinters Tor,
Peltasten auf den Wall, und sobald ein Turm steht, stellt sich die
Phalanx an den Fuß der nächsten Leiter mit der Front zum Wall; die
Reiter jagen, was trotzdem hereinkommt.

| Truppe | Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|---|---|---|
| standard | palisade | tor_leiter | klug | 7/8 | 32 % | 65 % | 1.1 | 76 s |
| ohne_reiter | palisade | tor_leiter | klug | 6/6 | 3 % | 68 % | 0.0 | 83 s |
| reiterlastig | palisade | tor_leiter | klug | 6/6 | 24 % | 66 % | 0.0 | 73 s |
| zwei_phalangen | palisade | tor_leiter | klug | 5/6 | 40 % | 59 % | 4.2 | 79 s |

### Was das Binden verändert

1. **Angriffe werden leichter, Verteidigung mit Reserve schwerer.** Der
   Phalanxstoß gewinnt jetzt mit fast jeder Mischung (standard 18 %
   Verluste statt 31 %), weil die Reiter der Siedlung, die in die Flanke
   fahren, dort gebunden werden und sich nur mit Preis lösen. Umgekehrt
   stirbt eine eigene Reiterreserve, die alle 15 Sekunden ein neues Ziel
   bekommt: sie ist gebunden, kriecht, reißt sich los und wird dabei
   getroffen. `tor_reserve` fällt von 5/8 auf 1/8.
2. **Den Leiterfuß decken, nicht jagen.** Gegen den Turm hilft nicht die
   Reserve, sondern die Phalanx am Fuß der Leiter: Wer herunterkommt,
   steht sofort im Handgemenge mit der Front, kann nicht weiter und wird
   Mann für Mann aufgerieben. `tor_leiter` gewinnt 7/8 bei 128 Räubern,
   ohne Reiter 6/6 mit 3 % Verlusten. Das Tor bleibt dabei offen und
   unbewacht; die Räuber stürmen es erst, wenn ihre Belagerung abläuft.
3. **Eine Phalanx bildet sich nicht im Kontakt.** Wer durch das Tor in
   eine wartende Linie hineinläuft, wird Mann für Mann gebunden, bevor
   die Reihen stehen, und kämpft ohne Bonus (`tor_phalanx` gegen die alte
   KI 0/8, weil deren Linie dicht hinter dem Tor steht; die kluge deckt
   das Wallstück, an dem der Turm ansetzt, und lässt den Raum frei).
   Aufstellen muss man außer Reichweite, gut eine Kachel vor dem Feind,
   und dann geschlossen anlaufen.
4. **Eine gebundene Front dreht sich nicht.** Wer vorn gebunden ist,
   braucht die Reserve für die Flanke; die Räuber, die sich nach einem
   gescheiterten Frontalangriff lösen, bezahlen dafür wie der Spieler.
5. **Die kleine Reiterphalanx bleibt die Ausnahme:** reiterlastig
   verliert den Wallangriff (1/6), weil abgesessene Reiter zu Fuß schwach
   sind, und die große gemischte Gruppe kann weder angreifen noch die
   Palisade halten (0/6 und 0/6).

### Alle Szenarien, beide KIs (standard, 8 Seeds)

| Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |
|---|---|---|---|---|---|---|---|---|
| offen | linie | einfach | 8/8 | 0% | 39% | 0.0 | 19 s | – |
| offen | linie | klug | 7/8 | 29% | 59% | 1.1 | 39 s | flankieren×8, frontal×8, umgehen_west×7 |
| offen | linie_reiter | einfach | 8/8 | 0% | 39% | 0.0 | 19 s | – |
| offen | linie_reiter | klug | 8/8 | 27% | 63% | 0.0 | 30 s | flankieren×8, umgehen_west×8, frontal×7 |
| offen | linie_aktiv | einfach | 8/8 | 0% | 45% | 0.0 | 19 s | – |
| offen | linie_aktiv | klug | 8/8 | 45% | 57% | 0.4 | 36 s | flankieren×8, umgehen_west×5, frontal×5 |
| offen | linie_tief | einfach | 8/8 | 0% | 64% | 2.0 | 22 s | – |
| offen | linie_tief | klug | 8/8 | 26% | 54% | 0.0 | 28 s | flankieren×8, umgehen_west×8 |
| offen | passiv | einfach | 3/8 | 39% | 42% | 6.5 | 30 s | – |
| offen | passiv | klug | 8/8 | 38% | 38% | 0.0 | 28 s | frontal×8 |
| offen | angriff | einfach | 0/8 | 47% | 32% | 8.0 | 23 s | – |
| offen | angriff | klug | 0/8 | 47% | 36% | 8.0 | 26 s | frontal×8 |
| palisade | tor_halten | einfach | 8/8 | 0% | 66% | 0.0 | 35 s | – |
| palisade | tor_halten | klug | 1/8 | 66% | 38% | 7.0 | 86 s | turm×8, belagern×8, frontal×7, flankieren×1, zermuerben×1, umgehen_west×1 |
| palisade | tor_reserve | einfach | 8/8 | 0% | 66% | 0.0 | 35 s | – |
| palisade | tor_reserve | klug | 1/8 | 59% | 54% | 5.5 | 86 s | turm×8, belagern×8, frontal×7, flankieren×1, zermuerben×1, umgehen_west×1 |
| palisade | passiv | einfach | 8/8 | 42% | 52% | 0.0 | 44 s | – |
| palisade | passiv | klug | 8/8 | 47% | 56% | 0.8 | 48 s | tor×8, frontal×8 |
| horde | vorruecken | einfach | 8/8 | 0% | 52% | 0.0 | 33 s | – |
| horde | vorruecken | klug | 8/8 | 6% | 48% | 0.0 | 44 s | lagern×8, flankieren×8, frontal×8, umgehen_west×8 |
| horde | angriff | einfach | 8/8 | 42% | 51% | 0.0 | 21 s | – |
| horde | angriff | klug | 8/8 | 47% | 47% | 0.0 | 21 s | lagern×8, frontal×8 |
| angriff_offen | phalanxstoss | einfach | 8/8 | 46% | 80% | 0.0 | 75 s | – |
| angriff_offen | phalanxstoss | klug | 8/8 | 18% | 73% | 0.0 | 75 s | halten×8, vorruecken×8 |
| angriff_offen | vorruecken | einfach | 0/8 | 96% | 26% | 0.0 | 62 s | – |
| angriff_offen | vorruecken | klug | 0/8 | 96% | 36% | 0.0 | 61 s | halten×8, vorruecken×8 |
| angriff_offen | angriff | einfach | 0/8 | 86% | 10% | 0.0 | 24 s | – |
| angriff_offen | angriff | klug | 0/8 | 87% | 26% | 0.0 | 27 s | halten×8, vorruecken×8 |
| angriff_wall | tor_phalanx | einfach | 0/8 | 50% | 26% | 0.0 | 124 s | – |
| angriff_wall | tor_phalanx | klug | 8/8 | 28% | 70% | 0.0 | 52 s | halten×8 |
| angriff_wall | belagerung | einfach | 0/8 | 100% | 18% | 0.0 | 76 s | – |
| angriff_wall | belagerung | klug | 0/8 | 91% | 20% | 0.0 | 94 s | halten×8, vorruecken×8 |

### Offene Punkte

- Der gescriptete Reiterstoß (`linie_reiter`, `tor_reserve`) wechselt
  das Ziel zu oft; ein Spieler würde die Reiter einmal ansetzen und erst
  nach dem Durchbruch neu führen. Die Zahlen für Reiterreserven sind
  daher eher zu schlecht.
- Männer im Handgemenge könnten dem Gegner nachrücken, wenn er weicht;
  heute stehen sie, bis der Gegner außer doppelter Reichweite ist.
- Die alte KI verliert den Wallangriff jetzt an die Torlücke, weil ihre
  Linie dort steht und die Angreifer im Durchgang bindet; das wäre für
  die kluge KI ein guter zusätzlicher Plan („Tor verstopfen“).

## Lauf 2 (29. September 2026): Binden und Umfassen, Truppenmischungen

Stand des Commits, der diesen Abschnitt einführt: die Räuber und die
Horde binden die Front und umfassen die Flanke, die Siedlung teilt
gemischte Gruppen nach Waffengattung und lässt ihre Reiter einer
gebundenen Phalanx in die Flanke fallen; Front, Flanke und Rücken werden
am Rechteck gemessen und an der Flanke wehren sich nur die Männer am
Rand. Sechs Seeds je Zeile, nur die kluge KI, jeweils mit der Vorgabe
des Szenarios (128 Räuber bei der Verteidigung, 96 bei der Horde, 75
bei der Siedlung).

### Fünf Truppenmischungen (je 75 Mann)

| Truppe | Zusammensetzung |
|---|---|
| standard | 40 Hopliten, 15 Peltasten, 20 Reiter in drei Gruppen |
| ohne_reiter | 60 Hopliten in zwei Gruppen, 15 Peltasten |
| gemischt | eine einzige Gruppe mit allem |
| reiterlastig | 25 Hopliten, 15 Peltasten, 35 Reiter in zwei Gruppen |
| zwei_phalangen | zwei Hoplitengruppen (die zweite mit den Peltasten gemischt), 20 Reiter |

Taktiken: `linie` = Phalanx quer, Peltasten dahinter, Reiter stehen;
`linie_aktiv` = dazu alle vier Sekunden: die Reiter greifen an, wer der
Phalanx in Flanke oder Rücken geht, die Phalanx dreht die Front, wenn
vorn niemand mehr steht; `vorruecken` (Horde) = Linie, vorrücken,
freier Angriff; `phalanxstoss` = in Formation bis vor die feindliche
Linie; `tor_reserve` = Phalanx hinters Tor, Peltasten auf den Wall,
Reiter jagen Eingedrungene; `tor_phalanx` = Rammbock, dann in Formation
durchs Tor.

| Truppe | Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |
|---|---|---|---|---|---|---|---|---|---|
| standard | offen | linie | klug | 6/6 | 14% | 60% | 0.0 | 35 s | flankieren×6, umgehen_west×6, zermuerben×2 |
| standard | offen | linie_aktiv | klug | 6/6 | 25% | 69% | 0.0 | 28 s | flankieren×6, umgehen_west×6 |
| standard | horde | vorruecken | klug | 6/6 | 6% | 56% | 0.0 | 45 s | lagern×6, flankieren×6, umgehen_west×6, frontal×6 |
| standard | angriff_offen | phalanxstoss | klug | 6/6 | 32% | 73% | 0.0 | 81 s | halten×6, vorruecken×6 |
| standard | palisade | tor_reserve | klug | 4/6 | 56% | 74% | 1.7 | 86 s | turm×6, belagern×6, frontal×6, umgehen_west×4, flankieren×1, zermuerben×1 |
| standard | angriff_wall | tor_phalanx | klug | 5/6 | 62% | 69% | 0.0 | 127 s | halten×6, vorruecken×5 |
| ohne_reiter | offen | linie | klug | 6/6 | 16% | 56% | 0.0 | 35 s | flankieren×6, frontal×6, zermuerben×5, umgehen_ost×3, umgehen_west×3 |
| ohne_reiter | offen | linie_aktiv | klug | 6/6 | 2% | 62% | 0.0 | 28 s | flankieren×6, umgehen_west×6 |
| ohne_reiter | horde | vorruecken | klug | 6/6 | 7% | 50% | 0.0 | 50 s | lagern×6, flankieren×6, frontal×6 |
| ohne_reiter | angriff_offen | phalanxstoss | klug | 0/6 | 71% | 59% | 0.0 | 300 s | halten×6, vorruecken×6 |
| ohne_reiter | palisade | tor_reserve | klug | 6/6 | 3% | 58% | 0.0 | 103 s | turm×6, belagern×6, flankieren×6, umgehen_ost×6, zermuerben×2 |
| ohne_reiter | angriff_wall | tor_phalanx | klug | 4/6 | 65% | 63% | 0.0 | 89 s | halten×6, vorruecken×3 |
| gemischt | offen | linie | klug | 6/6 | 55% | 50% | 0.0 | 43 s | flankieren×6, umgehen_west×6, frontal×1 |
| gemischt | offen | linie_aktiv | klug | 1/6 | 29% | 37% | 0.3 | 28 s | flankieren×6, frontal×6, umgehen_west×2 |
| gemischt | horde | vorruecken | klug | 6/6 | 10% | 38% | 0.0 | 50 s | lagern×6, flankieren×6, umgehen_west×6, frontal×6 |
| gemischt | angriff_offen | phalanxstoss | klug | 0/6 | 41% | 25% | 0.0 | 53 s | halten×6 |
| gemischt | palisade | tor_reserve | klug | 0/6 | 3% | 12% | 8.0 | 56 s | turm×6, belagern×6 |
| gemischt | angriff_wall | tor_phalanx | klug | 5/6 | 58% | 63% | 0.0 | 90 s | halten×6, vorruecken×1 |
| reiterlastig | offen | linie | klug | 0/6 | 49% | 38% | 8.0 | 37 s | flankieren×6, frontal×6 |
| reiterlastig | offen | linie_aktiv | klug | 6/6 | 44% | 67% | 0.0 | 29 s | flankieren×6, umgehen_west×6 |
| reiterlastig | horde | vorruecken | klug | 6/6 | 20% | 69% | 0.0 | 51 s | lagern×6, flankieren×6, umgehen_west×6, frontal×6, zermuerben×1, umgehen_ost×1 |
| reiterlastig | angriff_offen | phalanxstoss | klug | 6/6 | 44% | 72% | 0.0 | 86 s | halten×6, vorruecken×6 |
| reiterlastig | palisade | tor_reserve | klug | 6/6 | 53% | 90% | 1.3 | 87 s | turm×6, belagern×6, frontal×5, umgehen_west×5, flankieren×1, zermuerben×1, umgehen_ost×1 |
| reiterlastig | angriff_wall | tor_phalanx | klug | 0/6 | 95% | 49% | 0.0 | 135 s | halten×6, vorruecken×6 |
| zwei_phalangen | offen | linie | klug | 5/6 | 50% | 46% | 1.3 | 43 s | flankieren×6, umgehen_west×4, frontal×3 |
| zwei_phalangen | offen | linie_aktiv | klug | 6/6 | 41% | 59% | 0.0 | 34 s | flankieren×6, umgehen_west×4, zermuerben×1 |
| zwei_phalangen | horde | vorruecken | klug | 6/6 | 4% | 53% | 0.0 | 46 s | lagern×6, flankieren×6, umgehen_west×6, frontal×5 |
| zwei_phalangen | angriff_offen | phalanxstoss | klug | 6/6 | 50% | 71% | 0.0 | 51 s | halten×6, vorruecken×6 |
| zwei_phalangen | palisade | tor_reserve | klug | 1/6 | 65% | 65% | 7.2 | 82 s | turm×6, belagern×6, frontal×6, umgehen_west×1 |
| zwei_phalangen | angriff_wall | tor_phalanx | klug | 0/6 | 91% | 38% | 0.0 | 73 s | halten×6, vorruecken×6 |

Zusätzlich `linie_tief` (kurze Linie mit zwei bis drei Gliedern statt
einer breiten Einer-Reihe, sonst wie `linie_aktiv`): standard 6/6 mit
22 % Verlusten, zwei_phalangen 6/6 mit 32 %, reiterlastig 6/6 mit 47 %.
Kaum ein Unterschied zur breiten Linie, weil neben dem Ende der Front
ohnehin nur drei Mann je Glied kämpfen.

### Abgeleitete Strategien

1. **Eine Linie braucht eine Reserve.** Gegen „Binden und Umfassen“
   verliert eine stehende Linie ihre Flanke. Mit 40 Hopliten hält sie
   (14 % Verluste), aber nur weil die Räuber sich an der Front
   verbluten; mit einer kleinen Phalanx (reiterlastig, 25 Hopliten) und
   untätigen Reitern verliert man alles (0/6). Sobald die Reiter die
   Umfasser angreifen (`linie_aktiv`), gewinnt jede Mischung mit Reitern.
2. **Tiefe schlägt Breite nicht, Nachbarn schon.** Neben dem Ende einer
   Linie kämpfen nur drei Mann je Glied. Eine zweite Gruppe direkt daneben
   (Lücke unter einer Kachel) schließt die Naht: dort zählt ein Angreifer
   als Front. Zwei Phalangen nebeneinander verlieren trotzdem 50 %, weil
   die äußeren Enden offen bleiben; die Enden gehören an den Kartenrand,
   an den Wall oder hinter eine Reserve.
3. **Eine große gemischte Gruppe ist die schlechteste Wahl.** Sie kann
   nicht reagieren: kein Flankenschutz, keine Reserve, beim Angriff kein
   eigener Flankenstoß (0/6), hinter der Palisade plündern die
   Eingesickerten alle Häuser, während der Block am Tor steht (0/6). Die
   Siedlung selbst sortiert genau deshalb nach Waffengattung.
4. **Ohne Reiter verteidigt man am besten, greift aber schlecht an.**
   60 Hopliten halten Linie und Palisade fast verlustfrei (2 % und 3 %),
   aber gegen die Siedlung ohne Wall gibt es keinen Sieg: ihre Reiter
   fallen der gebundenen Phalanx in die Flanke, und niemand fängt sie ab.
5. **Reiterlastig gewinnt im Feld und scheitert am Wall.** Phalanxstoß
   6/6, Palisadenverteidigung 6/6 mit 90 % Feindverlusten, aber der
   Angriff auf die Siedlung mit Wall geht 0/6 verloren: Reiter sitzen ab,
   klettern langsam und kämpfen zu Fuß schwach.
6. **Gegen die Siedlung: erst binden, dann die Flanke.** Der Phalanxstoß
   gewinnt nur, wenn die eigenen Reiter die feindlichen Reiter abfangen
   oder ihrerseits die gebundene Linie umfassen; im Skript stehen sie bis
   Sekunde 60 herum, deshalb 31 % Verluste bei standard und Niederlagen
   ohne Reiter.
7. **Am Wall: Rammbock und Phalanx durchs Tor, nicht der Turm.** Mit
   gleicher Stärke gewinnt standard 6/8 (62 % Verluste), reiterlastig
   nie. Der freie Angriff verliert immer, weil die Siedlung das Tor von
   innen deckt und vorrückt, während die Angreifer noch in der Lücke
   stehen.

### Alle Szenarien, beide KIs (standard, 8 Seeds)

| Szenario | Taktik | KI | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |
|---|---|---|---|---|---|---|---|---|
| offen | linie | einfach | 8/8 | 0% | 39% | 0.0 | 19 s | – |
| offen | linie | klug | 8/8 | 14% | 59% | 0.0 | 33 s | flankieren×8, umgehen_west×8, zermuerben×2 |
| offen | linie_reiter | einfach | 8/8 | 0% | 39% | 0.0 | 19 s | – |
| offen | linie_reiter | klug | 8/8 | 12% | 72% | 0.0 | 30 s | flankieren×8, umgehen_west×8, zermuerben×1 |
| offen | linie_aktiv | einfach | 8/8 | 0% | 48% | 0.0 | 19 s | – |
| offen | linie_aktiv | klug | 8/8 | 28% | 69% | 0.0 | 29 s | flankieren×8, umgehen_west×8 |
| offen | passiv | einfach | 8/8 | 28% | 38% | 4.0 | 29 s | – |
| offen | passiv | klug | 8/8 | 41% | 38% | 0.0 | 27 s | frontal×8 |
| offen | angriff | einfach | 3/8 | 47% | 41% | 7.2 | 29 s | – |
| offen | angriff | klug | 2/8 | 47% | 46% | 7.8 | 30 s | frontal×8 |
| palisade | tor_halten | einfach | 8/8 | 0% | 71% | 0.0 | 44 s | – |
| palisade | tor_halten | klug | 1/8 | 68% | 38% | 7.0 | 84 s | turm×8, belagern×8, frontal×8, flankieren×1, zermuerben×1, umgehen_west×1 |
| palisade | tor_reserve | einfach | 8/8 | 0% | 71% | 0.0 | 44 s | – |
| palisade | tor_reserve | klug | 5/8 | 58% | 74% | 1.5 | 91 s | turm×8, belagern×8, frontal×8, umgehen_west×5, flankieren×1, zermuerben×1 |
| palisade | passiv | einfach | 8/8 | 44% | 45% | 2.2 | 49 s | – |
| palisade | passiv | klug | 4/8 | 45% | 38% | 5.9 | 50 s | tor×8, frontal×8 |
| horde | vorruecken | einfach | 8/8 | 0% | 51% | 0.0 | 33 s | – |
| horde | vorruecken | klug | 8/8 | 6% | 55% | 0.0 | 46 s | lagern×8, flankieren×8, umgehen_west×8, frontal×8, umgehen_ost×1 |
| horde | angriff | einfach | 8/8 | 41% | 55% | 0.0 | 22 s | – |
| horde | angriff | klug | 8/8 | 47% | 57% | 0.0 | 22 s | lagern×8, frontal×8 |
| angriff_offen | phalanxstoss | einfach | 8/8 | 31% | 80% | 0.0 | 72 s | – |
| angriff_offen | phalanxstoss | klug | 8/8 | 31% | 73% | 0.0 | 81 s | halten×8, vorruecken×8 |
| angriff_offen | vorruecken | einfach | 0/8 | 97% | 26% | 0.0 | 62 s | – |
| angriff_offen | vorruecken | klug | 0/8 | 96% | 31% | 0.0 | 60 s | halten×8, vorruecken×8 |
| angriff_offen | angriff | einfach | 0/8 | 86% | 10% | 0.0 | 25 s | – |
| angriff_offen | angriff | klug | 0/8 | 87% | 11% | 0.0 | 24 s | halten×8, vorruecken×8 |
| angriff_wall | tor_phalanx | einfach | 8/8 | 30% | 79% | 0.0 | 80 s | – |
| angriff_wall | tor_phalanx | klug | 6/8 | 62% | 67% | 0.0 | 121 s | halten×8, vorruecken×5 |
| angriff_wall | belagerung | einfach | 0/8 | 99% | 13% | 0.0 | 81 s | – |
| angriff_wall | belagerung | klug | 0/4 | 99% | 22% | 0.0 | 71 s | halten×4, vorruecken×4 |

Gegenüber dem ersten Lauf hat sich die alte KI kaum verändert; die
kluge zwingt jetzt zu Reserven und Flankenschutz, bleibt aber gegen eine
geführte Phalanx schlagbar. Die Zeile `belagerung` wurde nach dem Lauf
mit vier Seeds wiederholt, weil im ersten Durchgang das Zentrum einer
aufgelösten Gruppe von seinen Männern getrennt am Tor stehen blieb (ein
Fehler, inzwischen behoben: das Zentrum springt zu seinen Männern).

### Offene Punkte

- Die Umfasser kommen einzeln an und werden an der Flanke aufgerieben,
  wenn die Phalanx groß ist; die Räuber könnten ihre Umfassung sammeln
  und gemeinsam anlaufen.
- Die Siedlung mit Wall macht noch keinen Ausfall gegen abgesessene
  Reiter oder Turmbauer vor dem Wall.
- Der freie Angriff („Angriff“ ohne Ziel) wählt auch Gegner auf dem
  Wehrgang und läuft dann unter die Palisade; er sollte Unerreichbares
  überspringen.


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
