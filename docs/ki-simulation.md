# Simulation: Spielertaktiken gegen die Gegner-KI

## Lauf 24 (2. Oktober 2026): Klügere Gegner-KI

Drei Gegenmittel (README, „Gegenmittel der KI“): Reserve (Räuber, Horde,
Siedlung ab drei Gruppen), gegen Reiter Front drehen oder Kreis
(Hopliten der Siedlung und beider Festungsseiten), Peltasten der KI
plänkeln von der schildlosen rechten Seite. Jedes lässt sich in
`game/config.py` abschalten (`AI_RESERVE`, `AI_BRACE`, `AI_FLANK_THROW`).

Zwölf Seeds (Festung im Angriff acht), verglichen mit Lauf 22 und 23:

| Szenario | Taktik | Siege vorher → jetzt | Häuser verloren vorher → jetzt |
|---|---|---|---|
| offen | linie | 2/12 → 5/12 | 7,7 → 7,5 |
| offen | schlachtordnung | 12/12 → 8/12 | 3,9 → 6,8 |
| offen | linie_reiter | 7/12 → 5/12 | 6,2 → 6,7 |
| offen | linie_aktiv | 9/12 → 11/12 | 3,0 → 2,1 |
| offen | linie_tief | 11/12 → 10/12 | 3,2 → 3,9 |
| offen | passiv | 2/12 → 1/12 | 7,6 → 7,9 |
| offen | angriff | 11/12 → 9/12 | 6,4 → 6,8 |
| palisade | tor_halten | 2/12 → 1/12 | 7,3 → 7,9 |
| palisade | tor_reserve | 4/12 → 8/12 | 7,0 → 4,8 |
| palisade | tor_leiter | 11/12 → 12/12 | 1,0 → 0,2 |
| palisade | passiv | 6/12 → 0/12 | 6,2 → 8,0 |
| horde | vorruecken | 12/12 → 12/12 | – |
| horde | angriff | 12/12 → 10/12 | – |
| angriff_offen | alle drei | 0/12 → 0/12 | – |
| angriff_wall | beide | 0/12 → 0/12 | – |
| festung | tore | 4/12 → 2/12 | 2,3 → 4,0 |
| festung | passiv | 0/12 → 0/12 | 3,4 → 4,1 |
| festung_angriff | rammbock | 8/8 → 0/8 | – |
| festung_angriff | turm | 0/8 → 0/8 | – |

Auf den alten Karten verschiebt sich vieles um ein, zwei Siege in beide
Richtungen. Deutlich sind: „passiv“ hinter der Palisade fällt auf 0 (die
6 aus Lauf 22 waren schon auffällig, davor 1), die Schlachtordnung mit
einem Zug verliert 4 Siege, „Tor mit Reserve“ gewinnt 4 dazu. Ausgeschaltet
einzeln gemessen (offen „angriff“): ohne Reserve 0 statt 9 von 12, die
Reserve der Räuber hilft dem angreifenden Spieler dort also eher (sie
fehlt der Hauptmacht vorn). Der Abnahmetest „Phalanx, dann Verfolgung“
gewinnt mit acht Startwerten weiter 8 von 8, verliert durch die Reserve aber
im Mittel 21 statt 18 Mann; seine Verlustgrenze steht jetzt bei 35 %.

Die Festung im Angriff kippt: Mit dem Rammbock gewinnt man nie mehr
(abgeschaltet `AI_BRACE`: wieder 8 von 8, `AI_FLANK_THROW` ohne
Einfluss). Die Besatzungsphalanxen hinter dem Tor haben Fußvolk vor sich
und bilden gegen die heranreitenden Reiter Kreise; die Reiter stoßen nicht
mehr in Flanke oder Rücken, und im Kreis ist jede Seite Front.

Beim Bauen fiel ein Flackern in der Wegsuche auf (Ideenliste, Punkt 4).
Zwei Korrekturen wurden gemessen und wieder verworfen, weil sie die
Räuber stark machen: Mit Spiel an der Schwelle gewinnt offen „angriff“
3 statt 9; mit zusätzlich gemerkter Umgehungsseite fallen „linie_aktiv“
und „linie_reiter“ auf 0. Der Pfadtest dazu läuft ohne Reserve der KI, weil
die Reserve nur ändert, welcher Haufen anrückt.

## Lauf 23 (2. Oktober 2026): Schlachtordnung

Bekommen Gruppen verschiedener Gattungen mit einem Zug dieselbe Linie,
stehen die Hopliten vorn auf der Linie, die Peltasten 0,35 Kacheln
dahinter auf drei Vierteln der Länge, die Reiter drei Reihen tief am
rechten Flügel (die zweite Reitergruppe links), mit der Front auf gleicher
Höhe. Gruppen einer Gattung teilen sich die Linie wie bisher nebeneinander;
alle bisherigen Taktiken befehlen ihre Gruppen einzeln und sind mit zwei
Seeds auf offener Siedlung und Palisade bitgleich geblieben.

Neue Taktik `schlachtordnung` (offene Siedlung): ein Zug für alle Gruppen
von (4; 10,5) nach (12; 10,5), danach nichts mehr. Zum Vergleich derselbe
Zug mit dem alten Code, der alle drei Gruppen nebeneinander stellte:

| Aufstellung | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|
| nebeneinander (vorher) | 11/12 | 31 % | 51 % | 2,2 | 62 s |
| Schlachtordnung (jetzt) | 12/12 | 50 % | 62 % | 3,9 | 73 s |

Mehr Siege, aber teurer: Auf acht Kacheln stehen die 41 Hopliten in der
Schlachtordnung eine Reihe tief (die Linie ist länger, als sie Männer
haben), nebeneinander waren es zwei Reihen auf gut vier Kacheln. Die Front
ist zusammen mit den Reitern kürzer als die gezogene Linie, und die Räuber
flankieren öfter (in 10 von 12 Läufen). Wer kürzer zieht, bekommt eine
tiefere Phalanx. Verglichen mit der Taktik `linie` (gleiche Linie, Reiter
in Reserve: 2 von 12 in Lauf 22) bringt der Reiterflügel viel.

## Lauf 22 (2. Oktober 2026): Die Schildseite

Der Hoplitenschild sitzt am linken Arm. Eine Gruppe, die mindestens zur
Hälfte aus Hopliten besteht, nimmt an der linken Flanke weniger Schaden
(Nahkampf 0,8-fach, Speere 0,6-fach) und an der rechten mehr (1,25-fach,
Speere 1,15-fach). Links und rechts gelten so, wie die Gruppe schaut. Front
und Rücken bleiben, wie sie waren, ebenso lose Gruppen und Peltasten. Reiter
beim Anreiten und die KI bei der Zielwahl ziehen die rechte Seite leicht vor
(1,1 gegen 0,9); beim Umgehen nimmt die KI rechts herum, wenn sie etwa mittig
vor einer Phalanx steht. Einen Rechtsdrall der Phalanx gibt es nicht.

Zwölf Seeds (Festung jetzt auch zwölf, Festung im Angriff acht),
verglichen mit Lauf 21:

| Szenario | Taktik | Siege vorher → jetzt | Häuser verloren vorher → jetzt |
|---|---|---|---|
| offen | linie | 3/12 → 2/12 | 7,7 → 7,7 |
| offen | linie_reiter | 6/12 → 7/12 | 4,9 → 6,2 |
| offen | linie_aktiv | 10/12 → 9/12 | 4,1 → 3,0 |
| offen | linie_tief | 12/12 → 11/12 | 3,6 → 3,2 |
| offen | passiv | 3/12 → 2/12 | 7,5 → 7,6 |
| offen | angriff | 12/12 → 11/12 | 6,2 → 6,4 |
| palisade | tor_halten | 3/12 → 2/12 | 7,3 → 7,3 |
| palisade | tor_reserve | 4/12 → 4/12 | 7,1 → 7,0 |
| palisade | tor_leiter | 11/12 → 11/12 | 1,1 → 1,0 |
| palisade | passiv | 1/12 → 6/12 | 7,6 → 6,2 |
| horde | vorruecken | 12/12 → 12/12 | – |
| horde | angriff | 12/12 → 12/12 | – |
| angriff_offen | phalanxstoss | 0/12 → 0/12 | – |
| angriff_offen | vorruecken | 0/12 → 0/12 | – |
| angriff_offen | angriff | 0/12 → 0/12 | – |
| angriff_wall | tor_phalanx | 0/12 → 0/12 | – |
| angriff_wall | belagerung | 0/12 → 0/12 | – |
| festung | tore | 1/8 → 4/12 | 2,0 → 2,3 |
| festung | passiv | 0/8 → 0/12 | 4,0 → 3,4 |
| festung_angriff | rammbock | 8/8 → 8/8 | – |
| festung_angriff | turm | 0/8 → 0/8 | – |

Die Schildseite verschiebt die Balance kaum: Auf den alten Karten liegen
die Unterschiede bei einem Sieg von zwölf, also im Rauschen, mit einer
leichten Neigung zugunsten der Räuber (sechs Taktiken einen Sieg weniger,
eine einen mehr). Deutlich mehr als Rauschen ist nur „passiv“ hinter der
Palisade: 6 statt 1 von 12 Siegen. Dort steigen die Räuber über den Turm
und stoßen auf eine stehende Phalanx; warum die Schildseite das so stark
ändert, ist nicht einzeln nachgeprüft (dieselbe Taktik schwankte schon
früher stark, Lauf 16: 0 von 12, davor 10). In der Festung
gewinnt „Tore halten“ öfter (4 von 12 statt 1 von 8); ob das an der
Schildseite liegt oder an den zusätzlichen Seeds, ist bei so kleinen
Zahlen nicht sicher zu sagen. Die Angriffsszenarien bleiben unverändert
schwer.

## Lauf 21 (2. Oktober 2026): Häuser als Hindernisse

Häuser, aufgestellte Belagerungstürme (außer für die, die über sie auf den
Wall steigen) und liegende Rammböcke sperren den Weg. Blöcke suchen sich
einen Weg mit so viel Abstand, wie ihre Front breit ist (A* auf
Halbkacheln, Abstandsfeld zu Häusern und Gerät); den Wall regelt weiter
die Wegwahl über Tore und Leitern. Die alten Karten haben zwei
Häuserblöcke zu je zwei mal zwei mit einer Gasse zur Agora (vorher ein
Schachbrett mit einer Kachel Abstand: dort verfingen sich die Reiter, die
Peltasten wurden abgeschnitten, der Verfolgungstest gewann zwar, verlor
aber fast alle Häuser). Die Festung hat 30 Häuser in Blöcken, breite
Gassen von den Toren zur Agora, einen Ring um die Agora und einen Platz
vor jeder Leiter. Plünderer verteilen sich auf die Häuser, statt alle
dasselbe anzulaufen; ein aufgebrochener Rammbock bleibt hinter der Gruppe
liegen, nicht im Tordurchgang.

Zwölf Seeds (Festung acht), verglichen mit dem letzten Lauf je Szenario:

| Szenario | Taktik | Siege vorher → jetzt | Häuser verloren vorher → jetzt |
|---|---|---|---|
| offen | linie | 4/12 → 3/12 | 7,5 → 7,7 |
| offen | linie_reiter | 7/12 → 6/12 | 4,5 → 4,9 |
| offen | linie_aktiv | 8/12 → 10/12 | 5,6 → 4,1 |
| offen | linie_tief | 11/12 → 12/12 | 2,4 → 3,6 |
| offen | passiv | 4/12 → 3/12 | 6,8 → 7,5 |
| offen | angriff | 12/12 → 12/12 | 4,5 → 6,2 |
| palisade | tor_halten | 1/12 → 3/12 | 7,7 → 7,3 |
| palisade | tor_reserve | 3/12 → 4/12 | 7,6 → 7,1 |
| palisade | tor_leiter | 12/12 → 11/12 | 0,8 → 1,1 |
| palisade | passiv | 2/12 → 1/12 | 7,5 → 7,6 |
| horde | vorruecken | 1/4 → 12/12 | – |
| horde | angriff | 3/4 → 12/12 | – |
| angriff_offen | phalanxstoss | 1/12 → 0/12 | – |
| angriff_offen | vorruecken | 0/12 → 0/12 | – |
| angriff_offen | angriff | 0/12 → 0/12 | – |
| angriff_wall | tor_phalanx | 0/12 → 0/12 | – |
| angriff_wall | belagerung | 0/12 → 0/12 | – |
| festung | tore | 2/8 → 1/8 | 2,2 → 2,0 |
| festung | passiv | 0/8 → 0/8 | 2,2 → 4,0 |
| festung_angriff | rammbock | 8/8 → 8/8 | – |
| festung_angriff | turm | 0/8 → 0/8 | – |

Die Balance bleibt im Ganzen, wo sie war. Die Horde war zuletzt in Lauf 16
gemessen, mit nur vier Seeds; seither kamen mehrere Änderungen dazu (Umgehen
ohne Zappeln, Handgemenge an Männern), welche davon den Sieg gebracht hat,
ist nicht einzeln nachgeprüft.

Beim Bauen fielen Fehler auf: Fliehende fanden um ein Haus keinen Weg zu
einem Ziel jenseits des Kartenrands; die Wegwahl hielt ein Haus zwischen
Gruppe und Ziel für den Wall (Prüfung „Weg frei“ hieß an mehreren Stellen
„kein Wall dazwischen“, jetzt eigene Prüfung `wall_clear`); ein Mann am
Ende eines Blocks trat beim Schwenken auf eine Leiter, worauf sich die
Gruppe zum Übersteigen auflöste (jetzt steigt ein Block am Boden nicht
aus Versehen hinauf); und wer einen Platz im Haus hatte, kam nie an
(jetzt gilt er dicht davor als angekommen).

## Lauf 20 (2. Oktober 2026): Die Festung

Neue Karte, viermal so groß (32 × 36 Kacheln): ein sechseckiger Wall um
die Agora, Tore in der Nordkante und den beiden südlichen Schrägen,
Wehrtürme an den Ecken (zwei Speere je Sekunde, 6,5 Kacheln weit,
eroberbar), zwei Leitern innen an jeder Kante. Die Engine kennt dafür
mehrere Tore und einen geschlossenen Wall (innen/außen statt Nord/Süd);
für die alten Karten rechnet sie unverändert. Geprüft: alle 17 Taktiken
der alten Szenarien, je ein Seed, 70 Sekunden, Zustand aller Männer alle
fünf Sekunden – Bit für Bit gleich.

Acht Seeds je Zeile. Verteidigung gegen ein Heer, doppelt so stark wie die
eigene Truppe (150 gegen 75); Angriff gegen eine Besatzung von 40:

| Szenario | Taktik | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|---|
| festung | tore | 2/8 | 84% | 60% | 2,2 | 117 s |
| festung | passiv | 0/8 | 100% | 59% | 2,2 | 143 s |
| festung_angriff | rammbock | 8/8 | 50% | 100% | – | 106 s |
| festung_angriff | turm | 0/8 | 59% | 37% | – | 247 s |

`tore`: Die Phalanx stellt sich hinter das bedrohte Tor, die Peltasten auf
den Wehrgang darüber, die Reiter jagen Eingedrungene. Das Heer rammt zwei
Tore und setzt einen Turm an eine dritte Stelle; die eine Phalanx kann
nicht alles halten. In der ersten Fassung lief das Heer nach dem ersten
Durchbruch Gruppe für Gruppe durchs Tor in die Front der wartenden
Phalanx, die Reiter in die Speere, und der Verteidiger gewann 4 von 4 mit
9 % Verlust. Jetzt sammelt es sich vor einem gesperrten Tor, bis eine
zweite Bresche offen ist oder 20 Sekunden um sind.

`rammbock`: Die eigenen Hopliten rammen das nächste Tor; die Besatzung
holt die Phalanx vom ruhigen Tor dazu (in der ersten Fassung blieb sie
dort stehen). `turm`: Über einen Turm allein kommt man nicht hinein: Die
Männer steigen einzeln hinüber, im Feuer der Ecktürme, und drinnen
wartet die Besatzung auf die Gesammelten.

Rechenzeit Festung 10 ms je Takt im Mittel (Palisade 12 ms), höchstens
57 ms (Palisade 44 ms); auf der großen Karte wird je Takt höchstens ein
Wegefeld neu gerechnet (vorher zwei: Spitzen bis 86 ms).

Beim Bauen fielen Fehler auf, die nur die Festung betrafen: Wer auf dem
Wehrgang stand, ging nur bis zur Mitte seiner Kachel und sperrte die
Leiter; wer zwischen Fuß und Leiter stand, wurde zum Fuß zurückgeschickt
(Stau am Turm, ein Mann je zwei Sekunden statt drei je Sekunde); ein Mann
im Tordurchgang galt als jenseits des Walls (ständiges Auflösen); und
Fliehende entschieden die Seite ihres Ziels nach der Richtung des Tores
statt nach der Wallseite (sie pendelten im Tor, die Schlacht endete nie).

## Lauf 19 (2. Oktober 2026): Die Palisade deckt den Wehrgang

Wer auf dem Wehrgang steht, nimmt von Speeren, die von außen kommen, nur
noch 30 % des Schadens (`WALL_COVER_FACTOR`); von innen (der Seite der
Häuser) oder vom Wall selbst geworfen trifft es voll.

Zwölf Seeds, verglichen mit Lauf 18:

| Szenario | Taktik | Siege 18 → 19 | Häuser verloren 18 → 19 |
|---|---|---|---|
| palisade | tor_halten | 6/12 → 1/12 | 6,9 → 7,7 |
| palisade | tor_reserve | 11/12 → 3/12 | 2,1 → 7,6 |
| palisade | tor_leiter | 12/12 → 12/12 | 0,6 → 0,8 |
| palisade | passiv | 2/12 → 2/12 | 7,5 → 7,5 |
| angriff_wall | tor_phalanx | 0/12 → 0/12 | – |
| angriff_wall | belagerung | 0/12 → 0/12 | – |

Gegen die Erwartung verliert, wer nur das Tor hält, jetzt öfter. Der
Grund, Seed für Seed nachgeprüft (tor_halten, Seeds 1 bis 6, mit und ohne
Deckung): Die gedeckten Peltasten halten den Wehrgang 13 bis 19 Sekunden
länger (sie fliehen bei 48 bis 50 s statt bei 30 bis 36 s). Die Räuber, die
über den Turm kommen, sind deshalb erst bei 49 bis 51 s drinnen statt bei
40 bis 42 s. Den Sturm aufs Tor beginnen sie aber in allen Seeds bei 63 s.
Ohne Deckung kamen die Übersteiger gut 20 s vor dem Torsturm und wurden
für sich geschlagen; jetzt treffen beide fast gleichzeitig ein. Wer, wie
bei tor_leiter, mit der Phalanx an den Fuß der Leiter rückt, gewinnt
weiter alle zwölf.

## Lauf 18 (2. Oktober 2026): Handgemenge an feindlichen Männern, Gerangel im Bild

Gebunden war bisher, wer dem Formationsrechteck eines Gegners näher als
0,7 Kacheln stand, auch wenn dort gerade niemand stand (beim Schwenken,
bei Nachzüglern, am Wall). Jetzt bindet nur ein feindlicher Mann in
Armreichweite; frei wird man, wenn kein Gegner mehr innerhalb einer Kachel
von der Stelle steht, an der man gebunden wurde (von dort gemessen, damit
Nachrücken nicht umsonst löst). Gebundene ohne sichtbaren Feind in der
Nähe (0,8 Kacheln): offene Siedlung 8 % → 3 %, Palisade 13 % → 2 %.

Dazu, nur im Bild: Im Handgemenge treten die Männer an ihren Gegner
heran, Männer ohne Gegner drängen auf einen freien Feind in der Nähe
(die Phalanx nicht), spürbare Treffer blitzen auf, Gefallene hinterlassen
kurz einen Fleck. Mit und ohne dieses Bild rechnet die Schlacht genau
dasselbe (geprüft, auch als Test). Kosten 0,3 bis 0,6 ms je Takt.

Zwölf Seeds, verglichen mit Lauf 17 (die Änderung am Binden wirkt sich aus):

| Szenario | Taktik | Siege 17 → 18 | Häuser verloren 17 → 18 |
|---|---|---|---|
| offen | linie | 2/12 → 4/12 | 7,8 → 7,5 |
| offen | linie_reiter | 8/12 → 7/12 | 4,8 → 4,5 |
| offen | linie_aktiv | 9/12 → 8/12 | 4,0 → 5,6 |
| offen | linie_tief | 11/12 → 11/12 | 1,9 → 2,4 |
| offen | passiv | 9/12 → 4/12 | 6,4 → 6,8 |
| offen | angriff | 11/12 → 12/12 | 4,6 → 4,5 |
| palisade | tor_halten | 2/12 → 6/12 | 7,3 → 6,9 |
| palisade | tor_reserve | 6/12 → 11/12 | 4,8 → 2,1 |
| palisade | tor_leiter | 11/12 → 12/12 | 1,7 → 0,6 |
| palisade | passiv | 0/12 → 2/12 | 8,0 → 7,5 |
| angriff_offen | phalanxstoss | 1/12 → 1/12 | – |
| angriff_offen | vorruecken | – → 0/12 | – |
| angriff_offen | angriff | – → 0/12 | – |

An der Palisade halten die Verteidiger deutlich besser. Vermutlich, weil
dort am meisten Männer neben leeren Rechtecken gebunden waren (13 %):
Wer jetzt nicht wirklich gebunden ist, rückt auf seinen Platz nach, und
die Phalanx steht schneller wieder geschlossen. Nachgeprüft ist das nicht. Wer in der offenen
Siedlung passiv stehen bleibt, gewinnt wieder seltener (Lauf 17 hatte ihn
stark verbessert, jetzt liegt er zwischen Lauf 16 und 17).

## Lauf 17 (2. Oktober 2026): Umgehen ohne Zappeln

Ein Block, der außen um etwas herum muss, wählte bisher jeden Takt neu,
ob links oder rechts herum, und zappelte so auf der Stelle, vor allem
Angreifer vor zwei eigenen kämpfenden Haufen. Jetzt bleibt er bei der
einmal gewählten Seite, bis er vorbei ist. Ein Angriff nimmt die Seite,
auf der am Umriss des Gegners noch Platz ist (kein eigener Mann einer
anderen Gruppe steht dort); ist nirgends mehr Platz, wartet er geordnet
dahinter.

Das Zappeln hatte vor allem die Räuber gelähmt. Jetzt kommen sie an die
Flanken einer kurzen Linie und um sie herum an die Häuser. Zwölf Seeds,
verglichen mit dem Stand davor (Palisade: Lauf 16):

| Szenario | Taktik | Siege vorher → jetzt | Häuser verloren vorher → jetzt |
|---|---|---|---|
| offen | linie | 0/12 → 2/12 | 7,8 → 7,8 |
| offen | linie_reiter | 9/12 → 8/12 | 5,8 → 4,8 |
| offen | linie_aktiv | 7/12 → 9/12 | 6,5 → 4,0 |
| offen | linie_tief | 9/12 → 11/12 | 4,3 → 1,9 |
| offen | passiv | 2/12 → 9/12 | 7,3 → 6,4 |
| offen | angriff | 9/12 → 11/12 | 6,6 → 4,6 |
| palisade | tor_halten | 5/12 → 2/12 | 7,2 → 7,3 |
| palisade | tor_reserve | 8/12 → 6/12 | 5,5 → 4,8 |
| palisade | tor_leiter | 10/12 → 11/12 | 2,3 → 1,7 |
| palisade | passiv | 0/12 → 0/12 | 8,0 → 8,0 |
| angriff_offen | phalanxstoss | 1/12 → 1/12 | – |

In der offenen Siedlung gewinnt der Spieler meist öfter: Die Räuber
laufen nicht mehr zappelnd vor der Phalanx hin und her, sondern gehen an
eine freie Stelle und werden dort geschlagen. An der Palisade gewinnt,
wer nur das Tor hält, seltener, weil die Räuber drüben seine Phalanx
umfassen, statt an ihr hängen zu bleiben.

Zwei Abnahmetests haben sich verschoben: Im Test „Phalanx, dann
Verfolgung“ kommen die Räuber um die kurze Linie herum; der Spieler
gewinnt weiter, behält aber 5 statt 6 Häuser (8 Seeds im Schnitt 6,1
statt 7,5), die Grenze steht jetzt bei 5. Im Lerntest stand der
gesammelte Rest des Spielers ohne Befehl, und die Schlacht endete nicht;
der Test greift jetzt wie ein Spieler alle 20 Sekunden erneut an.

## Lauf 16 (1. Oktober 2026): Sammelplatz hinter dem Wall

Wer über den Wall steigt und weiter will, sammelt sich drüben zuerst: am
Fuß der Leiter, über die die Männer hinabsteigen, mit etwas Abstand zum
Wall, die Front zum Ziel. Jede Gruppe bekommt einen eigenen Platz neben
den schon belegten (sonst drängten sich sieben Räuberhaufen auf
denselben Fleck und wurden nie fertig). Sind alle drüben und angekommen,
höchstens acht Sekunden nach dem Letzten, schließt sich die Gruppe dort
und marschiert als Block weiter. Liegt das Ziel gleich hinter dem Wall,
ist es selbst der Sammelplatz; Fliehende sammeln sich nicht (sonst
warteten abziehende Räuber auf Nachzügler, die nie kamen, und die
Schlacht endete nicht).

Dabei fielen zwei Lücken im Kampf am Wall auf, beide jetzt Mann gegen
Mann gelöst: Standen zwei aufgelöste Gruppen beiderseits des Walls Mann
an Mann, kam kein Kontakt zustande (geprüft wurde, ob zwischen den
Gruppenmitten der Wall liegt), und sie standen sich bis zum Zeitlimit
gegenüber. Und wer oben am Leiterkopf wartete, schlug mit voller Wucht
auf Reiter am Leiterfuß, die nicht zurückschlagen konnten. Jetzt kämpft,
wer einen Gegner erreicht: auf derselben Ebene voll, von oben hinab
oder von unten an einen, der auf der Leiter steht, mit der verminderten
Wucht des Kampfes am Wall, an einen oben auf dem Wehrgang von unten gar
nicht. Außerdem rückt eine Gruppe, die sich auf der Agora am Kartenrand
wieder aufstellt, herein, statt mit der letzten Reihe jenseits des
Randes zu stehen.

Vier Seeds je Zeile, verglichen mit Lauf 15:

| Szenario | Taktik | Siege Lauf 15 → 16 | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|---|
| offen | linie | 0/4 → 0/4 | 75% → 80% | 45% → 50% | 8.0 → 8.0 | 74 s |
| offen | linie_reiter | 3/4 → 3/4 | 55% → 55% | 61% → 61% | 5.2 → 5.2 | 72 s |
| offen | linie_aktiv | 1/4 → 1/4 | 71% → 71% | 63% → 63% | 7.5 → 7.5 | 77 s |
| offen | linie_tief | 2/4 → 2/4 | 52% → 52% | 55% → 55% | 5.0 → 5.0 | 80 s |
| offen | passiv | 1/4 → 1/4 | 75% → 74% | 64% → 63% | 7.0 → 7.0 | 74 s |
| offen | angriff | 2/4 → 2/4 | 18% → 18% | 41% → 41% | 7.0 → 7.0 | 35 s |
| palisade | tor_halten | 0/4 → 2/4 | 18% → 78% | 10% → 65% | 8.0 → 6.5 | 143 s |
| palisade | tor_reserve | 1/4 → 3/4 | 34% → 38% | 32% → 45% | 6.2 → 3.0 | 104 s |
| palisade | tor_leiter | 2/4 → 3/4 | 33% → 54% | 54% → 56% | 4.5 → 3.2 | 114 s |
| palisade | passiv | 0/4 → 0/4 | 11% → 19% | 3% → 7% | 8.0 → 8.0 | 73 s |
| horde | vorruecken | 1/4 → 1/4 | 35% → 35% | 44% → 44% | 0.0 → 0.0 | 73 s |
| horde | angriff | 3/4 → 3/4 | 31% → 31% | 64% → 64% | 0.0 → 0.0 | 62 s |
| angriff_offen | phalanxstoss | 0/4 → 0/4 | 60% → 60% | 66% → 66% | 0.0 → 0.0 | 300 s |
| angriff_offen | vorruecken | 0/4 → 0/4 | 56% → 56% | 2% → 2% | 0.0 → 0.0 | 74 s |
| angriff_offen | angriff | 0/4 → 0/4 | 50% → 50% | 33% → 33% | 0.0 → 0.0 | 144 s |
| angriff_wall | tor_phalanx | 0/4 → 0/4 | 60% → 58% | 18% → 15% | 0.0 → 0.0 | 89 s |
| angriff_wall | belagerung | 0/4 → 0/4 | 24% → 21% | 0% → 0% | 0.0 → 0.0 | 300 s |

Zwölf Seeds, Palisade, im Vergleich zu vor Lauf 15 (Lauf 14) und Lauf 15:

| Taktik | Siege Lauf 14 | Lauf 15 | Lauf 16 | Häuser verloren 14 → 15 → 16 |
|---|---|---|---|---|
| tor_halten | 0/12 | 0/12 | 5/12 | 8,0 → 8,0 → 7,2 |
| tor_reserve | 2/12 | 6/12 | 8/12 | 7,2 → 4,9 → 5,5 |
| tor_leiter | 12/12 | 7/12 | 10/12 | 0,8 → 4,3 → 2,3 |
| passiv | 10/12 | 0/12 | 0/12 | 5,5 → 8,0 → 8,0 |

Die Deckung am Leiterfuß hält wieder fast so gut wie vor Lauf 15, und wer
das Tor hält, gewinnt jetzt manchmal, weil die Räuber drüben als Blöcke an
seiner Phalanx hängen bleiben. Wer passiv stehen bleibt, verliert weiter
alle Häuser: Die Räuber sammeln sich abseits und ziehen als Block an ihm
vorbei. Der Abnahmetest „Phalanx hinter der Palisade schlägt eine größere
Übermacht“ besteht wieder (6 von 8 Seeds, vor Lauf 15: 8).

Rechenzeit Palisade 12,1 bis 12,9 ms je Takt (Lauf 14: 14,2), höchstens
45 bis 53 ms. Zufallsbefehle in 20 Schlachten: kein Absturz, Männer zu
dicht 7-mal, eigene Männer jenseits des Kartenrands 68-mal (vor der
Agora-Korrektur 480).

## Lauf 15 (1. Oktober 2026): Jeder Mann sucht seinen Weg selbst

Beim Spielen fiel auf: Stieg eine Gruppe über den Turm, sprang ihr
Rechteck mitten im Sammeln zu den Männern und stellte sich neu auf, so
dass Männer, die schon standen, ihren Platz noch einmal verließen; und
um ruhende eigene Gruppen ging ein Block in einem großen Bogen herum.

Jetzt gibt das Rechteck nur noch an, wo jeder Mann stehen soll. Auf
freiem Feld marschiert die Gruppe weiter als Block. Muss sie über den
Wall, durchs offene Tor oder an einer ruhenden eigenen Gruppe vorbei,
löst sie sich auf: Die Zielaufstellung (Mitte und Front) steht fest, und
jeder Mann sucht sich seinen Weg zu seinem Platz, über ein Wegefeld
(`game/pathing.py`, Dijkstra auf Vierteln einer Kachel, Hindernisse sind
Palisade, geschlossenes Tor und stehende eigene Gruppen) und über Turm
und Leiter. Die Gruppe ist dabei, wo ihre Männer sind, und schließt
sich dort, wo sie stehen. Angriffe bleiben Block (Anstehen hinter
kämpfenden eigenen Gruppen bleibt), ebenso wer durch ein umkämpftes Tor
muss; wer über den Wall kommt, gleitet drüben nicht an Feinden entlang.
Die Gegner steigen ebenso Mann für Mann über den Wall, gehen aber um
ihre eigenen Haufen und durchs Tor noch als Block (`LOOSE_AI`).

Gemessene Fälle (`tests/test_pathing.py` prüft sie), Weg je Mann in Kacheln:

| Fall | vorher | jetzt |
|---|---|---|
| Über den Turm, Ziel 3 Kacheln hinter dem Wall | Front am Ende nach Osten, jeder Mann läuft nach dem Ankommen im Mittel noch 1,0 Kacheln | Front vom Wall weg, 0,03 Kacheln |
| Block (14 breit) hinter einer stehenden Linie, 5,5 Kacheln nach vorn | 11,5 s, 13,9 Kacheln Weg | 6,3 s, 5,9 Kacheln |
| Phalanx-Linie aufziehen, Linie davor | 8,7 s, 9,3 Kacheln | 5,6 s, 5,4 Kacheln |
| Reiter an der Linie vorbei | 3,7 s, 9,2 Kacheln | 2,5 s, 7,3 Kacheln |
| Linie hinter dem offenen Tor aufziehen | 13,1 s, 14,6 Kacheln | 7,9 s, 11,5 Kacheln |

Unterwegs gefundene und behobene Fehler: Räuber vor dem geschlossenen
Tor lösten sich auf, um ihre eigenen wartenden Haufen zu umgehen
(Auflösen nur noch, wenn das Ziel frei erreichbar ist); die Räuber-KI
schickte Gruppen „auf den Turm“, und alle Männer stellten sich oben auf
den Wehrgang (jetzt: Ziel hinter dem Wall, Weg über den Turm
vorgeschrieben); fliehende aufgelöste Gruppen wanderten außerhalb der
Karte immer weiter, weil ihr Ziel der Gruppenmitte folgte; Männer, die
auf dem Weg durchs Tor nicht vorankommen, nehmen nach einer Sekunde
Leiter oder Turm; eine aufgelöste Gruppe kämpft nur „von oben“, wenn
alle ihre Männer oben stehen.

Simulation, vier Seeds je Zeile, kluge KI, Truppe standard, verglichen
mit Lauf 14:

| Szenario | Taktik | Siege Lauf 14 → 15 | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|---|
| offen | linie | 0/4 → 0/4 | 75% → 75% | 45% → 45% | 8.0 → 8.0 | 71 s |
| offen | linie_reiter | 3/4 → 3/4 | 55% → 55% | 61% → 61% | 5.2 → 5.2 | 72 s |
| offen | linie_aktiv | 1/4 → 1/4 | 71% → 71% | 63% → 63% | 7.5 → 7.5 | 77 s |
| offen | linie_tief | 2/4 → 2/4 | 52% → 52% | 55% → 55% | 5.0 → 5.0 | 80 s |
| offen | passiv | 1/4 → 1/4 | 75% → 75% | 64% → 64% | 7.0 → 7.0 | 75 s |
| offen | angriff | 2/4 → 2/4 | 18% → 18% | 41% → 41% | 7.0 → 7.0 | 35 s |
| palisade | tor_halten | 0/4 → 0/4 | 22% → 18% | 14% → 10% | 8.0 → 8.0 | 69 s |
| palisade | tor_reserve | 0/4 → 1/4 | 37% → 34% | 23% → 32% | 8.0 → 6.2 | 88 s |
| palisade | tor_leiter | 4/4 → 2/4 | 23% → 33% | 56% → 54% | 1.8 → 4.5 | 90 s |
| palisade | passiv | 4/4 → 0/4 | 59% → 11% | 66% → 3% | 5.2 → 8.0 | 51 s |
| horde | vorruecken | 1/4 → 1/4 | 35% → 35% | 44% → 44% | 0.0 → 0.0 | 73 s |
| horde | angriff | 3/4 → 3/4 | 31% → 31% | 64% → 64% | 0.0 → 0.0 | 62 s |
| angriff_offen | phalanxstoss | 0/4 → 0/4 | 60% → 60% | 66% → 66% | 0.0 → 0.0 | 300 s |
| angriff_offen | vorruecken | 0/4 → 0/4 | 56% → 56% | 2% → 2% | 0.0 → 0.0 | 74 s |
| angriff_offen | angriff | 0/4 → 0/4 | 50% → 50% | 33% → 33% | 0.0 → 0.0 | 144 s |
| angriff_wall | tor_phalanx | 0/4 → 0/4 | 57% → 60% | 14% → 18% | 0.0 → 0.0 | 88 s |
| angriff_wall | belagerung | 0/4 → 0/4 | 14% → 24% | 0% → 0% | 0.0 → 0.0 | 300 s |

Offene Siedlung, Horde und Angriff auf die offene Siedlung sind Zahl für
Zahl gleich: Dort geht der Spieler in diesen Taktiken nicht um eigene
Gruppen herum, und die Gegner gehen (mit LOOSE_AI aus) wie bisher als
Block. Mit eingeschaltetem LOOSE_AI kamen die Räuber in der offenen
Siedlung leichter an die Häuser (Verfolgungstest: im Mittel 6,8 statt 7,5
von 8 Häusern gehalten, 8 Seeds).

Anders ist alles, wo Räuber über den Turm steigen. Vorher war das
Übersteigen langsam: Die unsichtbare Mitte der Gruppe wartete auf
Nachzügler, lief als Block weiter und blieb an der ersten Formation
hängen. Jetzt gehen die Männer, sobald sie unten sind, einzeln zu ihren
Plätzen. Zwölf Seeds, Palisade:

| Taktik | Siege vorher | Siege jetzt | Häuser verloren vorher → jetzt |
|---|---|---|---|
| tor_halten | 0/12 | 0/12 | 8,0 → 8,0 |
| tor_reserve | 2/12 | 6/12 | 7,2 → 4,9 |
| tor_leiter | 12/12 | 7/12 | 0,8 → 4,3 |
| passiv | 10/12 | 0/12 | 5,5 → 8,0 |

Wer passiv hinter dem Tor stehen bleibt, verliert jetzt alle Häuser
binnen einer Minute, fast ohne Kampf; wer den Leiterfuß deckt, wird
öfter umfasst. Der Abnahmetest „Phalanx hinter der Palisade schlägt eine
größere Übermacht“ gewinnt nur noch 5 von 8 Seeds (vorher 8) und ist als
erwarteter Fehlschlag markiert (ideen.md, Punkt 0b).

Rechenzeit je Takt (90 s Schlacht, ohne Grafik): offene Siedlung 8,1 ms
(vorher 8,5), Angriff mit Wall 4,0 ms (vorher 4,1), Palisade 15,2 ms
(vorher 14,2), dort höchstens 54 ms (vorher 42), weil über hundert Räuber
zugleich einzeln gehen. Höchstens zwei Wegefelder werden je Takt neu
gerechnet. Zufallsbefehle in 20 Schlachten (alle Szenarien): kein Absturz,
Männer verschiedener Gruppen zu dicht 5-mal (vorher 23).

## Lauf 14 (1. Oktober 2026): Der Anführer

Der Anführer kämpft in der Gruppe, die man ihm in der Aufstellung
zuteilt (Vorgabe: die Hopliten), zusätzlich zum Vorrat. Er hat die
Gattung der vordersten Reihe und schlägt nicht stärker zu, hält aber
fünfmal so viel aus (`LEADER_HP_FACTOR`). Solange er lebt, nimmt seine
Gruppe im Nah- und Fernkampf 15 % weniger Schaden (`LEADER_ARMOR`), und
ihre Fluchtschwelle liegt um 0,1 tiefer (`LEADER_COURAGE`): Eine Gruppe
mittlerer Hopliten flieht damit nicht mehr nach etwa 23, sondern erst
nach etwa 27 Gefallenen von vorn (Regeneration nicht gerechnet). Die
Siedlung im Angriffsszenario hat ihren eigenen Anführer bei der ersten
Hoplitengruppe, die Räuber keinen. Vier Seeds je Zeile, kluge KI, Truppe standard, verglichen mit
Lauf 13:

| Szenario | Taktik | Siege Lauf 13 → 14 | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|---|
| offen | linie | 0/4 → 0/4 | 79% → 75% | 16% → 45% | 8.0 → 8.0 | 71 s |
| offen | linie_reiter | 0/4 → 3/4 | 86% → 55% | 43% → 61% | 7.2 → 5.2 | 72 s |
| offen | linie_aktiv | 0/4 → 1/4 | 99% → 71% | 17% → 63% | 7.2 → 7.5 | 77 s |
| offen | linie_tief | 4/4 → 2/4 | 46% → 52% | 57% → 55% | 2.8 → 5.0 | 80 s |
| offen | passiv | 0/4 → 1/4 | 70% → 75% | 50% → 64% | 8.0 → 7.0 | 75 s |
| offen | angriff | 2/4 → 2/4 | 24% → 18% | 45% → 41% | 7.0 → 7.0 | 35 s |
| palisade | tor_halten | 0/4 → 0/4 | 38% → 22% | 23% → 14% | 8.0 → 8.0 | 79 s |
| palisade | tor_reserve | 0/4 → 0/4 | 41% → 37% | 38% → 23% | 8.0 → 8.0 | 86 s |
| palisade | tor_leiter | 3/4 → 4/4 | 37% → 23% | 61% → 56% | 2.8 → 1.8 | 116 s |
| palisade | passiv | 4/4 → 4/4 | 61% → 59% | 62% → 66% | 4.8 → 5.2 | 124 s |
| horde | vorruecken | 0/4 → 1/4 | 29% → 35% | 34% → 44% | 0.0 → 0.0 | 73 s |
| horde | angriff | 2/4 → 3/4 | 37% → 31% | 54% → 64% | 0.0 → 0.0 | 62 s |
| angriff_offen | phalanxstoss | 0/4 → 0/4 | 69% → 60% | 74% → 66% | 0.0 → 0.0 | 300 s |
| angriff_offen | vorruecken | 0/4 → 0/4 | 52% → 56% | 2% → 2% | 0.0 → 0.0 | 74 s |
| angriff_offen | angriff | 0/4 → 0/4 | 41% → 50% | 28% → 33% | 0.0 → 0.0 | 144 s |
| angriff_wall | tor_phalanx | 0/4 → 0/4 | 55% → 57% | 12% → 14% | 0.0 → 0.0 | 88 s |
| angriff_wall | belagerung | 0/4 → 0/4 | 14% → 14% | 0% → 0% | 0.0 → 0.0 | 300 s |

In der Verteidigung hilft er, wo die Hopliten lange im Kampf stehen:
Die Linie mit Reitern gewinnt drei von vier statt keiner, die Phalanx am
Leiterfuß vier von vier, und gegen die Horde gewinnt die Linie wieder
gelegentlich. Die Feindverluste der dünnen Linien steigen deutlich
(offen/linie 16 % → 45 %), weil die Hopliten länger halten. Die tiefe
Linie fällt von vier auf zwei Siege; bei vier Seeds ist das im Bereich
des Zufalls, denn ihre Verluste ändern sich kaum. Beim Angriff auf die
Siedlung gleichen sich beide Anführer aus; diese Szenarien bleiben so
schwer wie in Lauf 13 (ideen.md, Punkt 0).

## Lauf 13 (1. Oktober 2026): Niemand wird mehr geschoben

Beim Spielen fiel auf, dass Gruppen sich weiter gegenseitig wegschoben,
obwohl Lauf 10 das beheben sollte. Sieben nachgestellte Fälle zeigten
drei Ursachen, alle aus Lauf 10 selbst: (1) Eine breite Linie wich
einem kleinen Haufen absichtlich nicht aus, der Haufen musste Platz
machen (5,7 Kacheln weit geschoben). (2) Eine Phalanx behält ihr Ziel
als Posten und galt deshalb als „unterwegs“; wer vorbei wollte, lief
durch sie hindurch. (3) Wer auf den Platz einer stehenden Gruppe
befohlen wurde, schob sie weg.

Jetzt gilt: „Ruhend“ heißt ohne Ziel, als Phalanx auf dem Posten oder
beim Bauen. Eine ruhende eigene Gruppe wird nie geschoben; wer
unterwegs ist, geht außen herum, gleich wie breit er ist, und zwar
erst seitlich heraus, wenn er schon an ihr anliegt. Ein Ziel auf einer
ruhenden Gruppe rückt einmal je Befehl davor. Peltasten stehen in
lockerer Ordnung: Durch sie geht man hindurch, und sie dürfen dicht
hinter eine eigene Formation. Hinter einer kämpfenden oder wartenden
eigenen Gruppe steht man weiter streng an. Angreifer schließen auf,
bis ihre vordere Reihe wirklich Feinde erreicht (vorher blieben sie am
Rechteck einer Phalanx mit kurzer hinterer Reihe außer Speerweite
stehen). In allen sieben Fällen bleibt die stehende Gruppe jetzt auf
dem Zentimeter, wo sie stand.

Auf dem Weg dahin fielen zwei Artefakte auf, die die Zahlen stark
verfälschten: Ein besetztes Ziel wurde jeden Takt neu verlegt, so dass
Räuberhaufen langsam hinter die Linie des Spielers krochen; und eine
Regel „Angreifer gehen um eigene kämpfende Gruppen herum“ ließ die
Räuber die Phalanx rundum fassen. Das erste ist behoben, das zweite
wieder entfernt (es war nicht verlangt). Vier Seeds je Zeile, kluge
KI, Truppe standard, verglichen mit Lauf 12:

| Szenario | Taktik | Siege Lauf 12 → 13 | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|---|
| offen | linie | 0/4 → 0/4 | 90% → 79% | 39% → 16% | 8.0 → 8.0 | 53 s |
| offen | linie_reiter | 0/4 → 0/4 | 95% → 86% | 44% → 43% | 7.0 → 7.2 | 70 s |
| offen | linie_aktiv | 1/4 → 0/4 | 70% → 99% | 40% → 17% | 7.2 → 7.2 | 58 s |
| offen | linie_tief | 3/4 → 4/4 | 40% → 46% | 55% → 57% | 2.2 → 2.8 | 64 s |
| offen | passiv | 0/4 → 0/4 | 66% → 70% | 44% → 50% | 7.5 → 8.0 | 63 s |
| offen | angriff | 4/4 → 2/4 | 13% → 24% | 44% → 45% | 2.5 → 7.0 | 38 s |
| palisade | tor_halten | 0/4 → 0/4 | 54% → 38% | 26% → 23% | 8.0 → 8.0 | 93 s |
| palisade | tor_reserve | 2/4 → 0/4 | 44% → 41% | 67% → 38% | 4.5 → 8.0 | 93 s |
| palisade | tor_leiter | 4/4 → 3/4 | 21% → 37% | 55% → 61% | 0.0 → 2.8 | 145 s |
| palisade | passiv | 2/4 → 4/4 | 51% → 61% | 50% → 62% | 7.0 → 4.8 | 119 s |
| horde | vorruecken | 4/4 → 0/4 | 22% → 29% | 51% → 34% | 0.0 → 0.0 | 69 s |
| horde | angriff | 2/4 → 2/4 | 28% → 37% | 55% → 54% | 0.0 → 0.0 | 67 s |
| angriff_offen | phalanxstoss | 4/4 → 0/4 | 65% → 69% | 100% → 74% | 0.0 → 0.0 | 252 s |
| angriff_offen | vorruecken | 0/4 → 0/4 | 50% → 52% | 1% → 2% | 0.0 → 0.0 | 69 s |
| angriff_offen | angriff | 0/4 → 0/4 | 67% → 41% | 39% → 28% | 0.0 → 0.0 | 122 s |
| angriff_wall | tor_phalanx | 0/4 → 0/4 | 55% → 55% | 11% → 12% | 0.0 → 0.0 | 69 s |
| angriff_wall | belagerung | 0/4 → 0/4 | 12% → 14% | 0% → 0% | 0.0 → 0.0 | 300 s |

Lehre: Die frühere Balance beruhte zum Teil darauf, dass Gruppen sich
stapeln und wegschieben durften. Die Verteidigung bleibt etwa, wo sie
war (die tiefe Linie gewinnt vier von vier, die Phalanx am Leiterfuß
drei von vier). Die Angriffsszenarien sind deutlich schwerer: Gegen
die Horde verliert die dünne Acht-Kachel-Linie jetzt immer, weil der
Räuberplan „Binden und Umfassen“ aufgeht, statt dass die Umfassenden
hinter ihren eigenen Leuten hängen bleiben; und der Phalanxstoß gegen
die Siedlung endet meist im Zeitlimit, weil ihre Phalanx auf der Agora
bis zum letzten Mann hält und das Skript nur seine Hopliten hineinwirft.
Das ist ein Balance-Thema für sich (Punkt 0 der Ideenliste).

## Lauf 12 (1. Oktober 2026): Sammeln nach der Flucht, die Agora

Geschlagene verlassen das Feld nicht mehr einfach. Wer eine Siedlung
verteidigt, flieht auf die Agora (in der Verteidigung hinter den
Häusern, beim Angriff auf eine Siedlung zwischen ihren Häuserreihen),
sammelt sich dort, wenn kein Feind näher als zwei Kacheln steht
(Moral +0,04 je Sekunde bis 0,6), und nimmt dann wieder Befehle an.
Setzt der Feind auf eine Kachel nach, kehrt die Gruppe um und kämpft
bis zum letzten Mann; auf der Agora flieht niemand mehr. Angreifer
sammeln sich anderthalb Kacheln vor ihrem eigenen Kartenrand; ist die
Schlacht für sie aussichtslos oder setzt der Feind ihnen bis dorthin
nach, verlassen sie das Feld. Die Räuber geben auf, wenn weniger als
drei Zehntel übrig sind, und gezählt wird jetzt auch, wer sich noch
sammeln kann; eine angegriffene Siedlung gibt nie auf. Eine Schlacht
ist erst entschieden, wenn eine Seite niemanden mehr hat, der kämpft
oder sich sammeln kann.

Zwei Zwischenstände beim Einbau: Zuerst kehrten Verteidiger auf der
Agora schon um, wenn der Feind nur in zweieinhalb Kacheln Abstand
stand; das gab der Siedlungsphalanx eine sofortige zweite Chance, und
der Phalanxstoß ging verloren. Danach blieben ihre Peltasten auf der
Agora im letzten Kampf stehen, und das Skript des Phalanxstoßes
schickte nur seine Reiter dagegen, bis zum Zeitlimit. Das Skript setzt
jetzt mit allen nach, sobald keine feindliche Phalanx mehr steht, wie
ein Spieler es täte. Vier Seeds je Zeile, kluge KI, Truppe standard,
verglichen mit Lauf 11:

| Szenario | Taktik | Siege Lauf 11 → 12 | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|---|
| offen | linie | 0/4 → 0/4 | 23% → 90% | 3% → 39% | 5.0 → 8.0 | 60 s |
| offen | linie_reiter | 0/4 → 0/4 | 27% → 95% | 5% → 44% | 2.8 → 7.0 | 58 s |
| offen | linie_aktiv | 0/4 → 1/4 | 18% → 70% | 10% → 40% | 0.0 → 7.2 | 55 s |
| offen | linie_tief | 3/4 → 3/4 | 25% → 40% | 48% → 55% | 0.5 → 2.2 | 62 s |
| offen | passiv | 0/4 → 0/4 | 21% → 66% | 14% → 44% | 0.0 → 7.5 | 117 s |
| offen | angriff | 4/4 → 4/4 | 13% → 13% | 44% → 44% | 2.5 → 2.5 | 36 s |
| palisade | tor_halten | 0/4 → 0/4 | 14% → 54% | 12% → 26% | 8.0 → 8.0 | 100 s |
| palisade | tor_reserve | 0/4 → 2/4 | 27% → 44% | 24% → 67% | 8.0 → 4.5 | 156 s |
| palisade | tor_leiter | 2/4 → 4/4 | 18% → 21% | 41% → 55% | 2.0 → 0.0 | 92 s |
| palisade | passiv | 0/4 → 2/4 | 26% → 51% | 27% → 50% | 8.0 → 7.0 | 106 s |
| horde | vorruecken | 4/4 → 4/4 | 22% → 22% | 48% → 51% | 0.0 → 0.0 | 57 s |
| horde | angriff | 4/4 → 2/4 | 23% → 28% | 62% → 55% | 0.0 → 0.0 | 42 s |
| angriff_offen | phalanxstoss | 4/4 → 4/4 | 11% → 65% | 1% → 100% | 0.0 → 0.0 | 176 s |
| angriff_offen | vorruecken | 0/4 → 0/4 | 49% → 50% | 1% → 1% | 0.0 → 0.0 | 66 s |
| angriff_offen | angriff | 3/4 → 0/4 | 27% → 67% | 16% → 39% | 0.0 → 0.0 | 217 s |
| angriff_wall | tor_phalanx | 0/4 → 0/4 | 47% → 55% | 10% → 11% | 0.0 → 0.0 | 80 s |
| angriff_wall | belagerung | 0/4 → 0/4 | 7% → 12% | 0% → 0% | 0.0 → 0.0 | 300 s |

Lehre: Verteidigungen dauern jetzt bis zum letzten Mann, und das
kostet. Eine schlechte Aufstellung verliert nicht mehr mit einem
Viertel Verlusten, sondern mit fast allen Männern (dünne Linie: 90 %),
während die Räuber gesammelt wiederkommen und die Häuser holen. Gute
Aufstellungen gewinnen weiter: die tiefe Linie drei von vier, die
Phalanx am Leiterfuß hinter der Palisade jetzt vier von vier. Beim
Angriff auf eine Siedlung muss man die Agora stürmen: Der Phalanxstoß
gewinnt weiter vier von vier, aber erst nach knapp drei Minuten und mit
zwei Dritteln Verlust; der freie Angriff aller (`angriff`) verliert
jetzt immer, weil die Siedlung nicht mehr nach dem ersten Bruch
abzieht.

## Lauf 11 (1. Oktober 2026): Anstehen statt Stapeln

Ein Bildschirmfoto zeigte Räuberhaufen, die am Tor ineinander standen:
Ihre Rechtecke lagen übereinander, und weil keiner mehr ein freies Stück
am Umriss des Gegners fand, legten sich alle auf dasselbe. Jetzt fährt
keine Gruppe in eine eigene hinein, die gerade kämpft: Wer nicht um sie
herumkommt (etwa im Tor), steht im Block dahinter an, bis vorn Platz
wird; wer am Umriss kein freies Stück findet, bleibt im Block. Der Kreis
zählt für Abstände als Kreis. Dazu ein älterer Fehler, der beim Prüfen
auffiel: Der Plan „Vorrücken“ der Siedlung zielte noch auf 0,9 Kacheln
Lücke (aus der Zeit vor „Schild an Schild“) und ließ die feindliche
Phalanx damit zurückweichen, sobald der Spieler näher stand; ihre
gebundene erste Reihe blieb vorn hängen, und der Phalanxstoß endete im
Patt. Sie rückt jetzt bis auf Schildweite vor und weicht nie zurück.

Ein Scan über alle Szenarien zeigt keine Stapel mehr: Nirgends stehen
mehr als fünf Männer auf drei Pixeln (0,1 Kacheln), auch nicht im Tor.
Vier Seeds je Zeile, kluge KI, Truppe standard, verglichen mit Lauf 10:

| Szenario | Taktik | Siege Lauf 10 → 11 | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|---|
| offen | linie | 0/4 → 0/4 | 21% → 23% | 1% → 3% | 8.0 → 5.0 | 25 s |
| offen | linie_reiter | 0/4 → 0/4 | 31% → 27% | 9% → 5% | 2.0 → 2.8 | 22 s |
| offen | linie_aktiv | 0/4 → 0/4 | 25% → 18% | 9% → 10% | 0.5 → 0.0 | 20 s |
| offen | linie_tief | 4/4 → 3/4 | 23% → 25% | 46% → 48% | 0.5 → 0.5 | 57 s |
| offen | passiv | 0/4 → 0/4 | 28% → 21% | 18% → 14% | 0.0 → 0.0 | 19 s |
| offen | angriff | 4/4 → 4/4 | 17% → 13% | 35% → 44% | 0.8 → 2.5 | 36 s |
| palisade | tor_halten | 0/4 → 0/4 | 27% → 14% | 18% → 12% | 8.0 → 8.0 | 79 s |
| palisade | tor_reserve | 2/4 → 0/4 | 28% → 27% | 63% → 24% | 2.8 → 8.0 | 92 s |
| palisade | tor_leiter | 4/4 → 2/4 | 17% → 18% | 44% → 41% | 0.0 → 2.0 | 208 s |
| palisade | passiv | 4/4 → 0/4 | 27% → 26% | 100% → 27% | 0.0 → 8.0 | 84 s |
| horde | vorruecken | 3/4 → 4/4 | 39% → 22% | 46% → 48% | 0.0 → 0.0 | 56 s |
| horde | angriff | 4/4 → 4/4 | 28% → 23% | 46% → 62% | 0.0 → 0.0 | 33 s |
| angriff_offen | phalanxstoss | 4/4 → 4/4 | 8% → 11% | 9% → 1% | 0.0 → 0.0 | 35 s |
| angriff_offen | vorruecken | 2/4 → 0/4 | 52% → 49% | 52% → 1% | 0.0 → 0.0 | 63 s |
| angriff_offen | angriff | 4/4 → 3/4 | 22% → 27% | 14% → 16% | 0.0 → 0.0 | 53 s |
| angriff_wall | tor_phalanx | 0/4 → 0/4 | 44% → 47% | 14% → 10% | 0.0 → 0.0 | 60 s |
| angriff_wall | belagerung | 0/4 → 0/4 | 14% → 7% | 0% → 0% | 0.0 → 0.0 | 300 s |

Lehre: Der Phalanxstoß entscheidet sich wieder schnell (35 s statt
eines Patts). Hinter der Palisade gewinnt „nur halten“ nicht mehr: Die
Räuber laufen nicht mehr einzeln über den Turm in die wartende
Phalanx, sondern stehen in Blöcken an und kommen geschlossen. Damit
ist Punkt 0 der Ideenliste (Turm nur mit Platz dahinter) vorerst
erledigt; die Palisade ist für den Verteidiger jetzt deutlich schwerer,
am besten hält weiter die Phalanx am Fuß der Leiter (`tor_leiter`).

## Lauf 10 (30. September 2026): Niemand steht im anderen

Kein Mann teilt mehr seinen Platz mit einem anderen: Zwischen Männern
verschiedener Gruppen bleiben zwei Halbmesser (0,11 Kacheln), in der
eigenen Gruppe rückt man Schulter an Schulter (0,055), auch Fliehende
und Feinde sind fest. Wer jemanden im Weg hat, geht an ihm entlang
(eine Seite wählen und dabei bleiben, bis der Weg frei ist), sonst
schräg zurück; nur stürmende Reiter drängen Fußvolk beiseite. Eine
befohlene Gruppe geht um eine stehende eigene Gruppe herum, statt sie
zu schieben; wer nur herumsteht, macht am Ziel Platz.

Beim Einbau zeigte sich, wie empfindlich die Schlacht auf das Umgehen
reagiert: Umgingen Gruppen *jede* eigene Gruppe auf dem Weg, auch
solche, die selbst unterwegs waren, bogen die Räuberhaufen hintereinander
immer weiter außen um die Linie und fielen ihr reihenweise in den
Rücken (`linie_tief` 1/4, `horde vorruecken` 0/4, der Phalanxstoß ein
Patt über 300 s, weil die feindliche Linie um ihre eigenen Peltasten
herumlief statt vorzurücken). Ohne Umgehen, nur mit dem Ausschluss der
Männer, blieb alles beim Alten. Darum umgeht eine Gruppe jetzt nur
noch stehende eigene Gruppen, und nur, wenn der Seitenversatz unter
2,5 Kacheln bleibt; eine breite Linie weicht keinem Haufen aus, der
muss ihr Platz machen. Vier Seeds je Zeile, kluge KI, Truppe standard,
verglichen mit Lauf 9:

| Szenario | Taktik | Siege Lauf 9 → 10 | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer |
|---|---|---|---|---|---|---|
| offen | linie | 0/4 → 0/4 | 42% → 21% | 10% → 1% | 8.0 → 8.0 | 26 s |
| offen | linie_reiter | 0/4 → 0/4 | 42% → 31% | 28% → 9% | 4.0 → 2.0 | 23 s |
| offen | linie_aktiv | 0/4 → 0/4 | 37% → 25% | 31% → 9% | 0.0 → 0.5 | 19 s |
| offen | linie_tief | 4/4 → 4/4 | 17% → 23% | 38% → 46% | 0.2 → 0.5 | 39 s |
| offen | passiv | 0/4 → 0/4 | 25% → 28% | 13% → 18% | 0.0 → 0.0 | 18 s |
| offen | angriff | 4/4 → 4/4 | 34% → 17% | 56% → 35% | 4.0 → 0.8 | 23 s |
| palisade | tor_halten | 1/4 → 0/4 | 22% → 27% | 23% → 18% | 6.0 → 8.0 | 83 s |
| palisade | tor_reserve | 1/4 → 2/4 | 24% → 28% | 29% → 63% | 4.2 → 2.8 | 113 s |
| palisade | tor_leiter | 3/4 → 4/4 | 19% → 17% | 39% → 44% | 0.0 → 0.0 | 129 s |
| palisade | passiv | 0/4 → 4/4 | 27% → 27% | 42% → 100% | 8.0 → 0.0 | 177 s |
| horde | vorruecken | 4/4 → 3/4 | 19% → 39% | 42% → 46% | 0.0 → 0.0 | 57 s |
| horde | angriff | 4/4 → 4/4 | 27% → 28% | 53% → 46% | 0.0 → 0.0 | 35 s |
| angriff_offen | phalanxstoss | 4/4 → 4/4 | 14% → 8% | 16% → 9% | 0.0 → 0.0 | 122 s |
| angriff_offen | vorruecken | 0/4 → 2/4 | 51% → 52% | 1% → 52% | 0.0 → 0.0 | 230 s |
| angriff_offen | angriff | 2/4 → 4/4 | 35% → 22% | 20% → 14% | 0.0 → 0.0 | 51 s |
| angriff_wall | tor_phalanx | 0/4 → 0/4 | 48% → 44% | 15% → 14% | 0.0 → 0.0 | 135 s |
| angriff_wall | belagerung | 0/4 → 0/4 | 14% → 14% | 0% → 0% | 0.0 → 0.0 | 300 s |

Lehre: Die Ausgänge bleiben im Großen, wo sie waren; die dünne Linie
verliert weiter, die tiefe gewinnt, der Phalanxstoß gewinnt billiger.
Auffällig ist die Palisade: Wer nur hält (`passiv`), gewinnt jetzt
vier von vier, weil die Räuber über den Turm einer nach dem anderen in
die wartende Phalanx laufen, Engstellen lassen sich nicht mehr
durchdringen. Die Räuber-KI der Belagerung müsste den Turm eigentlich
erst dann nutzen, wenn dahinter Platz ist, ein Punkt für später. Zwei
Nebenbefunde beim Einbau: Die Leiter zählte einen Aufstieg schon bei
der Prüfung, bevor die Enge den Schritt verbot (so verhungerte die
Schlange am Turm); und ein fertiger Belagerungsturm wurde nur unter
dem Plan „Turm“ an den Wall gefahren, jetzt unter jedem Plan.

## Lauf 9 (30. September 2026): Kämpfen nach Berührungsbreite

Bisher kämpfte eine Gruppe im Handgemenge mit ihrer ganzen vorderen Reihe
gegen jeden Gegner, den sie berührte: Eine breite Linie, an deren Ende
sich ein Haufen legte, stach mit allen vierzig Speeren auf ihn ein, und
das gegen jeden der sieben Haufen ringsum noch einmal. Jetzt kämpft nur,
wer den Gegner wirklich erreicht, von Mann zu Mann gemessen (0,6
Kacheln), und die Verluste fallen auch dort, wo der Gegner steht. An
Flanke und Rücken dreht sich um, wer den Gegner erreicht, gleich in
welcher Reihe er steht. Dazu zwei Folgen für die Aufstellung am Umriss:
Eine zweite eigene Gruppe, die denselben Gegner anfällt, stellt sich
nicht mehr in die erste hinein, sondern an das nächste freie Stück des
Umrisses (vorher standen bis zu drei Haufen deckungsgleich auf einem
Linienende und schlugen dreifach zu); und Angreifer werden dort gefasst,
wo ihre Männer stehen, nicht an ihrem Rechteck.

Vier Seeds je Zeile, kluge KI, Truppe standard; „alt“ ist der Stand vor
der Regel, mit denselben Seeds.

| Szenario | Taktik | Siege alt → neu | Verlust Stadt alt → neu | Verlust Feind alt → neu | Häuser verloren alt → neu | Dauer neu |
|---|---|---|---|---|---|---|
| offen | linie | 0/4 → 0/4 | 43% → 42% | 18% → 10% | 8.0 → 8.0 | 37 s |
| offen | linie_reiter | 4/4 → 0/4 | 34% → 42% | 35% → 28% | 0.0 → 4.0 | 34 s |
| offen | linie_aktiv | 4/4 → 0/4 | 25% → 37% | 42% → 31% | 0.0 → 0.0 | 27 s |
| offen | linie_tief | 4/4 → 4/4 | 20% → 17% | 44% → 38% | 0.0 → 0.2 | 45 s |
| offen | passiv | 0/4 → 0/4 | 32% → 25% | 17% → 13% | 0.0 → 0.0 | 18 s |
| offen | angriff | 4/4 → 4/4 | 28% → 34% | 64% → 56% | 4.0 → 4.0 | 32 s |
| palisade | tor_halten | 1/4 → 1/4 | 20% → 22% | 31% → 23% | 6.0 → 6.0 | 73 s |
| palisade | tor_reserve | 1/4 → 1/4 | 30% → 24% | 42% → 29% | 2.8 → 4.2 | 74 s |
| palisade | tor_leiter | 4/4 → 3/4 | 13% → 19% | 54% → 39% | 0.0 → 0.0 | 79 s |
| palisade | passiv | 0/4 → 0/4 | 17% → 27% | 20% → 42% | 8.0 → 8.0 | 85 s |
| horde | vorruecken | 4/4 → 4/4 | 39% → 19% | 50% → 42% | 0.0 → 0.0 | 53 s |
| horde | angriff | 4/4 → 4/4 | 45% → 27% | 85% → 53% | 0.0 → 0.0 | 33 s |
| angriff_offen | phalanxstoss | 4/4 → 4/4 | 25% → 14% | 41% → 16% | 0.0 → 0.0 | 107 s |
| angriff_offen | vorruecken | 0/4 → 0/4 | 59% → 51% | 6% → 1% | 0.0 → 0.0 | 90 s |
| angriff_offen | angriff | 0/4 → 2/4 | 41% → 35% | 6% → 20% | 0.0 → 0.0 | 62 s |
| angriff_wall | tor_phalanx | 0/4 → 0/4 | 50% → 48% | 24% → 15% | 0.0 → 0.0 | 140 s |
| angriff_wall | belagerung | 0/4 → 0/4 | 65% → 14% | 0% → 0% | 0.0 → 0.0 | 300 s |

Lehre: Die Regel trifft genau eine Aufstellung, die vorher gewann: die
lange Linie in **einem** Glied (`linie_aktiv`, `linie_reiter`: vierzig
Hopliten über fünf Kacheln). Sie wird an beiden Enden umfasst, ein
Haufen legt sich als C um das Ende, der nächste daneben in den Rücken,
und die Speere in der Mitte der Linie erreichen niemanden mehr. Die
kurze Linie mit zwei bis drei Gliedern (`linie_tief`) gewinnt weiter
und verliert dabei weniger als zuvor; vorn bleibt die Phalanx mit
Speerwand und Schilden etwa vier zu eins überlegen, und die Stöße der
Reiter, das Plänkeln und die Belagerungen ändern sich kaum. Die beiden
Schlacht-Tests wurden entsprechend angepasst: die offene Siedlung hält
mit einer tiefen Linie (Reiter gegen Umfassende), verfolgt erst, wenn
die Hälfte der Räuber gefallen oder geflohen ist; hinter der Palisade
steht die Phalanx in zwei Gliedern hinter dem Tor.

## Lauf 8 (30. September 2026): Umgehen und in den Rücken fallen

Neuer Plan neben „Binden und Umfassen“: Die Umfassenden laufen ganz herum
(neben die Flanke, hinter die Ecke, hinter die Mitte) und greifen von
hinten an, wo es am härtesten trifft. Er kommt nur in Frage, wenn hinter
der Phalanx mindestens zwei Kacheln Platz sind, und steht bei offenem
Rücken gleichauf mit dem Flankieren; welcher der beiden gewinnt,
entscheidet das Gedächtnis. Sechs Seeds je Zeile, kluge KI.

| Truppe | Szenario | Taktik | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | Dauer | Pläne |
|---|---|---|---|---|---|---|---|---|
| standard | offen | linie | 0/6 | 42% | 19% | 8.0 | 34 s | ruecken×6, flankieren×6, frontal×6 |
| standard | offen | linie_aktiv | 6/6 | 24% | 46% | 0.0 | 24 s | ruecken×6, flankieren×6, frontal×6, umgehen_west×6 |
| ohne_reiter | offen | linie | 6/6 | 2% | 51% | 0.0 | 20 s | ruecken×6 |

Lernlauf, offen / linie, acht Schlachten hintereinander: Das Gedächtnis
bewertet den Rückenangriff nach acht Schlachten mit 1,14, das Flankieren
mit 0,87 und den Frontalangriff mit 1,25. Gegen eine stehende Linie ohne
Reserve ist der Weg in den Rücken für die Räuber also besser als das
Umfassen, der Frontalstoß mit Übermacht bleibt am stärksten. Gegen eine
Linie, die selbst angreift (linie_aktiv), oder ohne Reiter beim Spieler
ändert der Plan am Ausgang nichts.

## Lauf 7 (30. September 2026): Schild an Schild

Die Kampfreichweite ist von 1,15 Kacheln Lücke auf Speerweite (0,6)
gesunken, Angreifer schließen bis auf 0,15 auf, wer kämpft, löst sich
erst ab 1,1. Folge für die beiden Schlacht-Tests, die feste Taktiken
durchspielen: Langsame Hopliten fassen davonlaufende Plünderer nicht
mehr, weil niemand mehr aus einer Kachel Abstand „gefangen“ wird. Beide
Taktiken wurden entsprechend geändert, mit denselben Seeds:

| Szenario | Taktik | Ausgang | Verlust Stadt | Verlust Räuber | Häuser intakt |
|---|---|---|---|---|---|
| offen, 128 Räuber | alle in einer Linie, dann Hopliten allein hinterher (alt) | Niederlage | 15 | 43 | 0 |
| offen, 128 Räuber | Hopliten vorn, Peltasten dahinter, Reiter in Reserve, dann alle frei (neu) | Sieg | 12 | 64 | 8 |
| Palisade, 112 Räuber | Phalanx vom Tor an den Leiterfuß (alt) | Niederlage | 30 | 44 | 0 |
| Palisade, 112 Räuber | Phalanx bleibt am Tor, Reiter decken den Leiterfuß (neu) | Sieg | 19 | 75 | 8 |
| Palisade, 112 Räuber | Phalanx am Leiterfuß und stürmt Eingedrungene (Variante) | Sieg | 20 | 107 | 6 |

Lehre: Wer Plünderer fassen will, braucht Reiter oder Peltasten; die
Phalanx hält eine Stelle, sie jagt nicht. Nebenbei behoben: stürmende
Gruppen verfolgten geschlagene Gegner vom Feld, während andere noch
plünderten; jetzt wenden sie sich dem nächsten Kämpfenden zu.

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
