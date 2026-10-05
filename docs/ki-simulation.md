# Simulation: Spielertaktiken gegen die Gegner-KI

## Lauf 39 (5. Oktober 2026): Drücken, Phalanx gegen Phalanx

Neu: Wo zwei Fronten gebunden sind, schiebt die stärkere Seite die schwächere
Ruck für Ruck zurück (ein halber Manndurchmesser je Ruck, alle zwei Sekunden
ab dem 1,2-fachen Stoß, jede Sekunde ab dem Doppelten). Stoß je
Berührungsstelle: in der Phalanx die Tiefe (jede Reihe bis zur vierten voll,
dahinter halb) mal Moral, im Haufen ein halber Mann je Mann nahe der
Berührung. Verlorener Boden kostet 0,3 Moral je Kachel; wer nicht weichen
kann, wird gequetscht. Peltasten, Reiter und der Kreis sind ausgenommen.

Labor (40 gegen 40 Hopliten, Schild an Schild, ohne Wurfspeere):

| Eigene | Gegner | Ergebnis nach 50 s |
|---|---|---|
| 7 breit, 6 tief | 14 breit, 3 tief | Gegner 1,4 Kacheln zurückgedrängt, bricht bei 56 s an der Moral (0,48), obwohl er mehr tötet (eigene 28, Gegner 35 Mann) |
| 14 breit | 7 breit | spiegelbildlich: eigene werden gedrängt und brechen bei 58 s |
| 10 breit | 10 breit | kein Drücken, beide stehen |
| 10 breit | 20 breit | Gegner 1,5 Kacheln zurück, bricht bei 41 s |
| 10 breit, 4 tief | 48 Räuber | Haufen wird vor der Phalanx hergeschoben, flieht nach 17 s |
| 10 breit, 4 tief | 48 Räuber am Kartenrand | Haufen eingeklemmt und gequetscht, flieht nach 7 s |

Szenarien, Gegner-KI „klug“, sechs Seeds, vorher (Lauf 38) / nachher:

| Szenario | Taktik | Siege | Verlust Stadt | Verlust Feind | Häuser verloren |
|---|---|---|---|---|---|
| siedlung | linie_tief | 6/6 / 6/6 | 23 % / 20 % | 60 % / 62 % | 2,3 / 2,3 |
| siedlung | schlachtordnung | 6/6 / 6/6 | 66 % / 61 % | 73 % / 68 % | 19,5 / 14,8 |
| siedlung | linie_reiter | 5/6 / 4/6 | 94 % / 85 % | 71 % / 71 % | 26,3 / 27,7 |
| siedlung | linie_aktiv | 6/6 / 6/6 | 21 % / 30 % | 68 % / 65 % | 0,2 / 2,8 |
| siedlung_angriff | agora | 0/6 / 0/6 | 57 % / 51 % | 16 % / 6 % | – |
| horde_sturm | linie_aktiv | 6/6 / 6/6 | 17 % / 7 % | 59 % / 57 % | – |
| ueberfall | linie_aktiv | 6/6 / 6/6 | 5 % / 4 % | 66 % / 61 % | 0,3 / 0,0 |

Lesart: Die Tiefe lohnt jetzt. Die tiefe Linie und die Horde (dort steht
die Linie mehrreihig) werden billiger, die Schlachtordnung ebenfalls. Die
aktive Linie in der Siedlung wird teurer (21 → 30 %, 2,8 Häuser): Sie
ist acht Kacheln lang, also eine einzige Reihe, und eine Reihe schiebt ein
Räuberhaufen zurück (ein halber Mann je Mann gegen Tiefe 1). Das ist die
gewollte Kehrseite, die Taktik muss tiefer stellen. Der Angriff auf die
Siedlung bleibt verloren und wird schlechter: Die KI-Hopliten stehen acht
breit und fünf tief und drängen die langen Linien des Spielers zurück; die
Feindverluste sinken von 16 auf 6 %. Dort ist die KI also nicht zu schwach,
sondern der Spieler steht falsch. Die Reiterlinie liegt in der Streuung.

## Lauf 38 (5. Oktober 2026): Der Kreis als Phalanx

Neu: Die Ringe des Kreises sind die Reihen der Gruppe; der weiteste Kreis ist
eine geschlossene Reihe, enger gezogen bilden sich Ringe nach innen. Nur der
äußere Ring kämpft und wird getroffen, der zweite sticht mit, von innen wird
nachgerückt, beim Umformen bekommt jeder den nächsten Platz. Dazu zählt eine
Phalanx als stehend, sobald 85 % der Männer auf ihren Plätzen sind (ein
Gebundener, dessen Platz der Feind besetzt, zählt als da); vorher hielt ein
einzelner Gebundener abseits seines Platzes den Phalanxbonus auf. Die KI bildet
ihren Kreis weiter als eine Reihe, also wie bisher. Gegner-KI „klug“, sechs
Seeds, vorher (Lauf 37) / nachher:

| Szenario | Taktik | Siege | Verlust Stadt | Verlust Feind | Häuser verloren |
|---|---|---|---|---|---|
| siedlung | linie_tief | 6/6 / 6/6 | 23 % / 23 % | 60 % / 60 % | 2,3 / 2,3 |
| siedlung | schlachtordnung | 6/6 / 6/6 | 66 % / 66 % | 73 % / 73 % | 19,5 / 19,5 |
| siedlung | linie_reiter | 5/6 / 5/6 | 94 % / 94 % | 71 % / 71 % | 26,3 / 26,3 |
| siedlung | linie_aktiv | 6/6 / 6/6 | 18 % / 21 % | 54 % / 68 % | 0,0 / 0,2 |
| siedlung_angriff | agora | 0/6 / 0/6 | 56 % / 57 % | 13 % / 16 % | – |
| horde_sturm | linie_aktiv | 6/6 / 6/6 | 18 % / 17 % | 54 % / 59 % | – |
| ueberfall | linie_aktiv | 6/6 / 6/6 | 5 % / 5 % | 66 % / 66 % | 0,3 / 0,3 |

Lesart: Die Balance der Szenarien bleibt, nur die aktive Linie und die Horde
verschieben sich um ein paar Punkte (die mildere Stehregel lässt den Bonus
nach einem Umformen im Kampf früher greifen). Der Kreis selbst ist im Labor
gemessen: 40 Hopliten gegen 48 Räuber, stehend eine Reihe oder drei Ringe,
mittlere Abweichung von den Plätzen 0,0 Kacheln über den ganzen Kampf (vorher
0,3–0,7 nach den ersten Verlusten, einzelne Männer bis 2,5 Kacheln weg); aus
einer kämpfenden Linie zum engen Kreis befohlen, steht er nach vier Sekunden
als Phalanx und hält (vorher nie: ein Gebundener abseits seines Platzes
verhinderte es, der Kreis verlor ohne Bonus).

## Lauf 37 (5. Oktober 2026): Die hintere Reihe macht kehrt

Neu: Der Phalanxbonus gilt nur in der ersten Reihe nach vorn. Wer in einer
geschlossenen Phalanx gebunden wird, ohne vorn zu stehen (die hintere Reihe
von hinten, das Ende der Reihe von der Seite), dreht sich zum Gegner um und
kämpft wie jeder Mann: ohne den Rückennachteil (1,8-facher Schaden), ohne
das Zehren an der Moral (0,05 je Schadenspunkt), ohne die anderthalbfache
Moraleinbuße je Gefallenem, aber auch ohne Schildseite und ohne den Rückhalt
der Nachbarphalanxen. Die Rechnung läuft über den Anteil der vom Angreifer
erreichten Männer, die nicht vorn gebunden sind; eine einreihige Linie, deren
Männer alle vorn im Speerkampf stehen, kann sich also nicht umdrehen. Im Bild
schauen die Umgedrehten zu ihrem Gegner.

Gegner-KI „klug“, sechs Seeds, 128 Räuber in der offenen Siedlung, vorher
(Lauf 36, Nachprüfung) / nachher:

| Szenario | Taktik | Siege | Verlust Stadt | Verlust Feind | Häuser verloren |
|---|---|---|---|---|---|
| siedlung | linie_tief | 5/6 / 6/6 | 40 % / 23 % | – / 60 % | 5,5 / 2,3 |
| siedlung | schlachtordnung | 6/6 / 6/6 | 75 % / 66 % | 75 % / 73 % | 22,8 / 19,5 |
| siedlung | linie_reiter | 5/6 / 5/6 | 86 % / 94 % | – / 71 % | 24,3 / 26,3 |
| siedlung_angriff | agora | 0/6 / 0/6 | 60 % / 56 % | 21 % / 13 % | – |
| siedlung | linie_aktiv | 6/6 / 6/6 | 19 % / 18 % | 54 % / 54 % | 0,0 / 0,0 |
| horde_sturm | linie_aktiv | 6/6 / 6/6 | 17 % / 18 % | 54 % / 54 % | – |
| ueberfall | linie_aktiv | 6/6 / 6/6 | 5 % / 5 % | 66 % / 66 % | 0,3 / 0,3 |

Streuung: Ein zweiter Lauf derselben vier Siedlungsfälle (Zwischenstand, bei
dem die Umgedrehten Schildseite und Rückhalt der Linie noch behielten) ergab
linie_tief 32 %/4,5, schlachtordnung 64 %/16,8, linie_reiter 6/6 83 %/24,0.
Sechs Seeds trennen bei den dünnen Linien also keine zehn Punkte.

Lesart: Die tiefe Linie gewinnt deutlich (Verluste 40 → 23 %, Häuser 5,5 →
2,3), die Schlachtordnung etwas; die Reiterlinie bleibt in der Streuung. Zurück
auf den Stand vor der Trägheit (Lauf 34: schlachtordnung 49 %, linie_reiter
32 % Verluste) führt die Regel nicht. Die dünnen Linien verlieren weiter viele
Männer und Häuser: Die Räuberhaufen im Rücken sterben nicht an
der umgedrehten hinteren Reihe, sie binden sie nur, und vorn drückt die
Masse weiter. Der Angriff auf die Siedlung bleibt verloren; die Verteidiger
dort haben dieselbe Regel, und ihre Phalanx bricht nun seltener am Rücken.
Räuberzahl bleibt vorerst 128 (Ideenliste Punkt 7).

## Lauf 36 (5. Oktober 2026): Peltasten werfen nur im Stand oder im Lauf auf den Gegner zu

Neu: Wer vom Gegner wegläuft (Zurückweichen beim Plänkeln, Flucht, seitlich
an ihm vorbei), wirft nicht; im Stand und im Lauf auf ihn zu (höchstens 60
Grad daneben) wie bisher. Gegner-KI „klug“, sechs Seeds, vorher / nachher
auf demselben Stand des Spiels (mit Trägheit):

| Szenario | Taktik | Siege | Verlust Stadt | Verlust Feind | Häuser verloren |
|---|---|---|---|---|---|
| siedlung | linie_aktiv | 6/6 / 6/6 | 34 % / 19 % | 59 % / 54 % | 3,3 / 0,0 |
| siedlung | schlachtordnung | 6/6 / 6/6 | 75 % / 75 % | 75 % / 75 % | 22,8 / 22,8 |
| siedlung_angriff | agora | 1/6 / 0/6 | 58 % / 60 % | 25 % / 21 % | – |
| horde_sturm | linie_aktiv | 6/6 / 6/6 | 17 % / 17 % | 57 % / 54 % | – |
| ueberfall | linie_aktiv | 6/6 / 6/6 | 5 % / 5 % | 66 % / 66 % | 0,3 / 0,3 |

Die Wirkung ist klein: Die Peltasten beider Seiten werfen beim Zurückweichen
ein paar Salven weniger (Feindverluste 2 bis 4 Punkte niedriger). Bei
„linie_aktiv“ hilft es dem Spieler (die zurückweichenden Räuber-Peltasten
treffen die Reiter nicht mehr im Rücken), beim Angriff auf die Siedlung
kostet es den einen Sieg von sechs. Die Räuberwerte bleiben.

### Nachprüfung: Warum die Siedlungsverteidigung teurer wurde

Dieselben Seeds, Taktik „schlachtordnung“: Lauf 34 49 % Verluste und 13,3
Häuser, jetzt 75 % und 22,8; „linie_reiter“ 32 % → 86 %, „linie_tief“
27 % → 40 %. Geprüft wurden „Nachrücken in die Lücke“ und
„Zusammenschließen nach dem Gerangel“: **beides ist in Ordnung.** Die
Phalanx der Hopliten bleibt im Handgemenge geschlossen (alle Männer auf
ihren Plätzen, Phalanx-Bonus bis zuletzt); sie bricht an der **Moral**:
Ein Räuberhaufen im Rücken zehrt an einer Phalanx 0,05 je Schadenspunkt,
und die einreihige Linie der Simulationstaktiken (41 Mann in einer Reihe)
hat keinen Rücken, der sich wehrt. Jetzt kommen die Haufen des Plans
„Umgehen und in den Rücken fallen“ früher (12 statt 16 s) und zu zweit
nacheinander in den Rücken (41 s statt 15 s Rückenkontakt über acht
Seeds), und die Hopliten fliehen nach vier Gefallenen; nach dem Sammeln
auf der Agora kämpfen sie ohne Phalanx weiter.

Welche Änderung das auslöst, lässt sich nicht sauber trennen: Mit
Platzverteilung *und* Trägheit aus sind die alten Zahlen zurück (32
Verluste, 15 s Rücken), mit nur einer von beiden aus nicht. Eine winzige
Störung des alten Stands (Mannradius 0,055 → 0,0551) ergibt schon 42
Verluste und 30 s Rücken: Der alte Stand hing an einem günstigen
Verlauf, bei dem die umgehenden Haufen an der Flanke hängen blieben.
Kontrollierte Duelle sind alt wie neu gleich (Haufen frontal gegen Phalanx:
Flucht nach 12 s, 9 Räuber übrig; Reiterstoß in einen anstürmenden
Haufen: Flucht nach 12 s, 14–16 Mann geworfen). Die Räuber sind also nicht
stärker geworden, sie **kommen nur besser um die Linie herum**, seit die
Männer ruhiger laufen.

Stärke-Sweep (sechs Seeds) zur Entscheidung:

| Räuber | linie_tief | schlachtordnung | linie_reiter |
|---|---|---|---|
| 128 (Vorgabe) | 5/6, 40 %, 5,5 Häuser | 6/6, 75 %, 22,8 | 5/6, 86 %, 24,3 |
| 112 | 6/6, 13 %, 0,0 | 6/6, 62 %, 18,3 | 4/6, 83 %, 20,8 |
| 96 | 6/6, 11 %, 0,0 | 6/6, 26 %, 0,2 | 6/6, 14 %, 0,0 |

Die tiefe Linie hält bei 112; die dünnen Linien brauchen 96 oder eine
Antwort auf den Rückenangriff.

## Lauf 35 (5. Oktober 2026): Ruhe der Bewegung

Kein Balance-Lauf, sondern eine Messung, wie unruhig die Männer laufen,
und was zwei Änderungen daran geändert haben. Werkzeug: `lab/ruhe.py`
(Scratchpad), das in echten Schlachten jeden Mann in jedem Takt verfolgt
und je Lage (steht, marschiert, aufgelöst, Handgemenge, Flucht) zählt:

- **Umkehr:** ein Schritt entgegen dem letzten (> 1 Pixel), je Mann und Sekunde.
- **Knick:** Richtungsänderung über 60 Grad.
- **Tausch:** zwei Nachbarn einer Reihe wechseln die Seite.
- **Bild:** Umkehrungen des gezeichneten Punkts (geglättet plus Gerangel).

### Ausgangslage (vier Schlachten, 60–120 s)

| Lage | Umkehr | Knick | Tausch | Bild |
|---|---|---|---|---|
| steht in Ordnung | 0,01–0,10 | 0,01–0,17 | 0,01–0,06 | 0,01–0,02 |
| marschiert in Ordnung | 0,34–0,82 | 1,1–2,4 | 0,25–0,59 | 0,09–0,31 |
| Handgemenge | 0,30–0,77 | 0,7–1,2 | 0,20–0,51 | 0,71–1,36 |
| aufgelöst (Festung, Leitern) | 2,6 | 5,1 | – | 0,55 |
| Flucht | 0,2–1,8 | 0,4–4,0 | 0,05–0,94 | 0,1–0,6 |

Befunde: Im Stand ist es ruhig. Im Handgemenge ist das Bild unruhiger
als die Simulation, weil das Gerangel jeden Takt den nächsten freien
Gegner neu wählte und auf Armlänge zurück und wieder vor pendelte. Im
Marsch gehen 90–96 % der Schritte geradeaus zum Platz; die 5–8 %
Ausweichschritte machen fast alle Umkehrungen. Eine Gruppe, die allein
marschiert, hat 0,02 Umkehrungen; fünf Gruppen, die ihre Reihenfolge
behalten, 0,04. Unruhig wird es beim **Umformen**: In den fünf Sekunden
nach einem Linienbefehl oder Schwenk liegen die Umkehrungen bei
0,46–0,75, danach bei 0,09–0,29. Die Männer kreuzen einander auf dem Weg
zu ihren neuen Plätzen (Treffer meist mit Männern anderer Reihen derselben
Gruppe).

### Änderung A: Gerangel im Bild

Ein Mann bleibt drei Sekunden bei seinem Gegner, drängt mit 0,6 statt 1,5
Kacheln/s, steht auf Armlänge still; im Handgemenge folgt das Bild dem
Mann selbst statt seiner Lage in der (wandernden, drehenden) Gruppe.

| Handgemenge, Bild-Umkehr | Siedlung | Horde |
|---|---|---|
| vorher | 1,10 | 1,36 |
| Gegner halten (1,5 s) | 0,81 | 1,04 |
| + Bild folgt dem Mann | 0,71 | 0,81 |
| + 0,6 Kacheln/s | 0,39 | 0,40 |
| + 3 s halten | 0,37 | 0,38 |

### Änderung B: Entscheidungen festhalten (verworfen)

| Variante | Marsch-Labor Umkehr | Labor „Haufen bilden“ fertig nach |
|---|---|---|
| Stand | 0,568 | 6,1 s |
| Ausweichseite 2 s statt 1 s | 0,570 | – |
| Blockierer merken | – | 11,3 s |
| Mitlaufen statt schlängeln | 0,542 | 6,4 s |

Das Seitengedächtnis bringt nichts mehr, der gemerkte Blockierer schadet,
das Mitlaufen bringt wenig und ließ im Test „durchs offene Tor“ Männer
draußen zurück. Nichts davon ist im Spiel.

### Änderung D: Plätze nach kürzesten Wegen

Beim Umformen (neue Breite, Front oder Stelle) werden die Plätze jedes
Abschnitts so auf seine Männer verteilt, dass die Summe der Wege am
kleinsten ist (ungarische Methode, in der jetzigen Front um die neue
Mitte). Labor, eine Hoplitengruppe mit 40 Mann (Umkehr je Mann und Sekunde
bis alle stehen):

| Fall | vorher | nachher |
|---|---|---|
| Schwenk 90 Grad an Ort und Stelle | 0,25 | 0,00 |
| Kehrtwende | 0,13 | 0,00 |
| Linie schmaler (14 → 7) | 1,33 | 0,19 |
| Linie breiter (14 → 20) | 1,39 | 1,75 |
| vier Kacheln vor | 0,03 | 0,00 |
| fünf Gruppen schwenken je 45 Grad | 0,27 | 0,02 |

Breiter werden bleibt unruhig: Männer der zweiten Reihe müssen durch die
erste nach vorn; das dauert aber nur eine halbe Sekunde. Gerechnet wird im
mitgedrehten Rahmen (wo jeder nach dem Schwenk stünde), sonst liefen die
Männer beim Schwenk quer durch die Formation. Verworfen wurde unterwegs,
Männer in Ordnung durch einen fremden eigenen Block hindurchgehen zu
lassen (verletzt den Mindestabstand zweier Halbmesser, und eine Gruppe,
deren Ziel in einem stehenden Block liegt, kam nie an) und ein stehender
Block, der jeden Durchgänger an seinen Rand setzt (Platztausch zweier
Gruppen dauerte 9,9 statt 4,4 s). Geblieben ist: Nur eine kämpfende
Phalanx drängt Männer anderer eigener Gruppen hinaus, die tief in ihren
Reihen stecken und ihren Platz woanders haben.

Echte Schlachten, Aufmarschphase (erste 30 s), sechs Seeds, Marsch in
Ordnung:

| | Umkehr | Tausch | Bild |
|---|---|---|---|
| Siedlung vorher / nachher | 0,72 / 0,71 | 0,59 / 0,55 | 0,25 / 0,25 |
| Horde vorher / nachher | 0,39 / 0,46 | 0,45 / 0,44 | 0,06 / 0,06 |

In der Schlacht ist der Gewinn also nicht messbar: Dort marschieren vor
allem die Haufen der KI (ohne Linienbefehle), und die Schlachten laufen
chaotisch auseinander. Die Platzverteilung wirkt dort, wo der Spieler
hinschaut, wenn er seine Gruppen umformt, schwenkt oder wenden lässt.
Offen bleiben die Trägheit je Mann (siehe `docs/ideen.md`, Punkt 8), das
Gedränge marschierender Gruppen und die aufgelösten Haufen an den Leitern.

### Änderung C: Trägheit je Mann

Jeder Mann hat eine Schrittgeschwindigkeit. Er fährt mit 6 Kacheln/s² an,
bremst mit 15 Kacheln/s² (Bremsweg aus dem Marsch kürzer als ein
Reihenabstand), führt im Marsch die Geschwindigkeit seiner Gruppe mit und
korrigiert nur den Rest, bremst vor seinem Platz so, dass er dort steht
(„Arrive“), und wer anstößt, steht. An einem fremden Block gleitet er mit
vollem Tempo entlang, unter eigenen Nachbarn weicht er nur um den
gebremsten Schritt aus. Der Block bremst vor seinem Ziel ebenso, sonst
liefen die Männer in die Reihe vor ihnen. Reiter sind ausgenommen (ihr
Schwung steckt schon im Trupp).

Labor, Umkehrungen je Mann und Sekunde:

| Fall | vor C | mit C |
|---|---|---|
| Marsch mit Gedränge (fünf Gruppen, eine Linie, Schwenk, Kolonne) | 0,57 | 0,16 |
| … Knicke über 60 Grad | 1,40 | 0,56 |
| Platztausch zweier Gruppen (Labor „tauschen“) | 0,44 | 0,23 |
| Alle auf einen Punkt | 0,23 | 0,16 |
| Schwenk 90 Grad / Kehrtwende / schmaler | 0,00 / 0,00 / 0,19 | 0,00 / 0,00 / 0,00 |
| Linie breiter (14 → 20) | 1,88 | 0,34 |

Echte Schlachten, drei Seeds, 90 s, je Mann und Sekunde:

| | Umkehr Marsch | Umkehr Handgemenge | Bild Handgemenge | Tausch Marsch |
|---|---|---|---|---|
| Siedlung vor C / mit C | 0,50–0,73 / 0,21 | 0,25–0,46 / 0,17 | 0,28–0,38 / 0,23 | 0,38–0,53 / 0,68 |
| Horde vor C / mit C | 0,27–0,48 / 0,13 | 0,23–0,40 / 0,12 | 0,33–0,42 / 0,25 | 0,28–0,42 / 0,61 |

Die Umkehrungen fallen in Marsch und Handgemenge auf ein Drittel bis ein
Viertel; die Männer schießen aber nicht mehr sofort auf ihren Platz zurück,
sondern laufen weich aus, und so tauschen Nachbarn in der Reihe beim
Marsch mit Gedränge häufiger die Seite (0,4–0,5 → 0,6–0,7). Das ist der
offene Rest (siehe `docs/ideen.md`, Punkt 8).

Zwei Dinge kamen dabei als Fehler ans Licht und sind behoben: Eine Gruppe,
deren Ziel eine ruhende eigene Gruppe belegt, wartete bisher ewig 0,3
Kacheln davor; jetzt bleibt sie dort stehen. Und der Anlauf der Reiter
wurde auf null gesetzt, sobald der Kontakt kurz aussetzte (die Geworfenen
laufen mit Masse langsamer zurück); jetzt zählt er weiter.

Verworfen wurde unterwegs: Trägheit auch für Reiter (doppelt gezählt, der
Sturm kam nicht mehr in den Feind), eine Bremsrate gleich der Anfahrrate
(Bremsweg länger als der Reihenabstand: die Männer liefen in die Reihe vor
ihnen und wichen seitlich aus, Nachbartausch 83 statt 8 im Labor), und
Ausweichschritte an fremden Blöcken im gebremsten Tempo (Nachzügler krochen
mit 0,4 Kacheln/s an einer Linie entlang und verloren ihren Block).

## Lauf 34 (4. Oktober 2026): Reserve um die Flanke, Festung, Räuberlager

Neu seit Lauf 33:

- Ausweichen ohne Seitenwechsel (eine Sekunde Gedächtnis), Hänger an der
  Leiter der Festung behoben.
- Zwei kleine Szenarien für den Anfang einer Kolonie: Räuberüberfall
  (Verteidigung) und Räuberlager (Angriff), 13 Mann gegen 18 Räuber.
- Die freigegebene Reserve der KI läuft um die Front einer geschlossenen
  Phalanx herum in Flanke oder Rücken (`AI_RESERVE_FLANK`), statt frontal
  hineinzulaufen. Kommt sie, weil ein Feind schon nah ist, kämpft sie gleich.
- Verteidigung der Festung: 110 statt 150 Angreifer.
- Neue Taktik „agora“ für den Angriff auf die Siedlung (siehe unten).

Nicht verändert: die Werte der Räuber und der letzte Kampf auf der Agora.

Gegner-KI „klug“, sechs Seeds (Festung im Angriff vier). „ohne Flanke“ ist
derselbe Stand mit `AI_RESERVE_FLANK = False`.

| Szenario | Taktik | Siege | Verlust Stadt | Verlust Feind | Häuser verloren | ohne Flanke | Lauf 33 |
|---|---|---|---|---|---|---|---|
| siedlung | linie | 1/6 | 97 % | 64 % | 27,2 | 1/6 | 0/6 |
| siedlung | schlachtordnung | 6/6 | 49 % | 61 % | 13,3 | 6/6 (18,0 Häuser) | 6/6 |
| siedlung | linie_reiter | 6/6 | 32 % | 50 % | 3,8 | 6/6 (20 %, 0 Häuser) | 6/6 |
| siedlung | linie_aktiv | 4/6 | 89 % | 71 % | 25,8 | 4/6 | 2/6 |
| siedlung | linie_tief | 6/6 | 27 % | 49 % | 1,0 | 6/6 | 6/6 |
| siedlung | passiv | 6/6 | 72 % | 76 % | 25,5 | 6/6 | 4/6 |
| siedlung | angriff | 6/6 | 28 % | 54 % | 10,7 | 6/6 | 6/6 |
| siedlung_angriff | phalanxstoss | 0/6 | 60 % | 38 % | – | – | 1/6 |
| siedlung_angriff | vorruecken | 0/6 | 51 % | 10 % | – | – | 0/6 |
| siedlung_angriff | angriff | 0/6 | 44 % | 10 % | – | – | 0/6 |
| siedlung_angriff | agora (neu) | 1/6 | 64 % | 82 % | – | – | – |
| horde | vorruecken | 6/6 | 34 % | 69 % | – | 6/6 | 6/6 |
| horde | angriff | 6/6 | 18 % | 34 % | – | 6/6 | 6/6 |
| horde_sturm | linie_tief | 6/6 | 23 % | 65 % | – | 5/6 | – |
| horde_sturm | linie_aktiv | 6/6 | 16 % | 48 % | – | 6/6 | – |
| horde_sturm | angriff | 6/6 | 29 % | 49 % | – | 6/6 | – |
| festung (110) | tore | 6/6 | 7 % | 60 % | 1,7 | – | 0/4 (150) |
| festung (110) | passiv | 1/6 | 97 % | 51 % | 4,8 | – | 0/4 (150) |
| festung_angriff | rammbock | 4/4 | 40 % | 100 % | – | – | 4/4 |
| festung_angriff | turm | 3/4 | 36 % | 92 % | – | – | 2/4 |
| ueberfall | linie | 4/6 | 13 % | 53 % | 2,0 (von 6) | 5/6 | 5/6 |
| ueberfall | linie_aktiv | 5/6 | 14 % | 64 % | 1,8 | 5/6 | 5/6 |
| ueberfall | passiv | 0/6 | 58 % | 31 % | 5,7 | 0/6 | 0/6 |
| ueberfall | angriff | 0/6 | 73 % | 34 % | 5,7 | 0/6 | 0/6 |
| lager | sturm | 6/6 | 23 % | 62 % | 6 Hütten verbrannt | – | 6/6 |

**Reserve um die Flanke.** In allen geprüften Schlachten (Siedlung, Horde,
Räuberüberfall) ruft die Umfassung die Reserve, und sie geht um die Flanke.
Die Wirkung auf die Siegquote ist klein: Wer seine Reiter jagen lässt
(„linie_reiter“), verliert jetzt 32 statt 20 % und knapp vier Häuser statt
keines; beim Räuberüberfall kostet die dünne Linie einen Sieg mehr. Gegen die
Schlachtordnung trifft die Reserve dagegen auf die zweite Linie und richtet
weniger aus als frontal. Die Unterschiede zu Lauf 33 bei „linie_aktiv“ und
„passiv“ kommen vom Ausweichen, nicht von der Reserve (ohne Flanke gleich).

**Festung, Verteidigung.** Die Siegquote kippt steil mit der Zahl der
Angreifer:

| Angreifer | tore | passiv |
|---|---|---|
| 100 | 6/6 | 5/6 |
| 110 | 6/6 | 1/6 |
| 120 | 0/4 | 0/4 |
| 150 | 0/4 | 0/4 |

Bei 110 gewinnt, wer die Tore hält, und verliert, wer nur steht. Das ist die
neue Vorgabe. Die Kante liegt nahe (bei 120 hält kein Tor mehr).

**Angriff auf die Siedlung.** Die einfachen Taktiken verlieren weiter. Der
Grund ist der letzte Kampf auf der Agora: Die Siedlung flieht nach dem
ersten Zusammenstoß auf die Agora, sammelt sich und hält dort bis zum
letzten Mann. Wer dann aufgelöst anstürmt („Freier Angriff“), verliert in
zehn Sekunden zwei Drittel seiner Hopliten gegen einen Mann der Siedlung.
Weniger Verteidiger helfen den einfachen Taktiken erst spät:

| Siedlung | phalanxstoss | vorruecken | angriff |
|---|---|---|---|
| 75 (Vorgabe) | 0/6 | 0/6 | 0/6 |
| 66 | 0/6 | 0/6 | 0/6 |
| 60 | 0/6 | 0/6 | 0/6 |
| 50 | 0/6 | 5/6 | 4/6 |

Statt den Kampf um die Agora abzuschwächen, prüft die neue Taktik „agora“,
ob er mit Plan zu gewinnen ist: Die eigene Phalanx zieht vor der Front der
Siedlung auf, die Peltasten werfen, die Reiter gehen in den Rücken; sind
sie dort, rückt die Phalanx in Ordnung heran, und nach einer Flucht wird neu
angesetzt. Die Siedlung verliert so im Mittel 82 % (statt 10 bis 38 %). In
300 Sekunden gewinnt das einmal, mit 600 Sekunden vier von sechs Schlachten
(Siege nach 139 bis 372 s). Der Angriff ist also schwer und langwierig, aber
zu schaffen; die Vorgabe bleibt 75.

**Horde.** Weiter immer gewonnen. Die Räuberwerte bleiben vorerst, wie sie
sind.

## Lauf 33 (4. Oktober 2026): neue Szenarien

Neu seit Lauf 32:

- Fünf Szenarien, alle auf der großen Karte (32 × 36): Verteidigung und
  Angriff der offenen Siedlung (die Stadt der Festung ohne Wall),
  Räuberhorde (viermal so groß), Festung in beiden Richtungen. Palisade und
  Siedlung mit Wall sind fort.
- Bewegung: Zittern, Kolonne durchs Tor, Befehlshaber vorn, kein großer
  Bogen um eigene Nachbarn, Türme für beide Seiten.
- Festung: Eine Gruppe ganz oben auf dem Wehrgang schließt sich dort; über
  die Leitern wird die richtige Leiter hinab angesteuert.
- Die Taktiken der Simulation stehen relativ zur Kartenmitte und zur
  eigenen Aufstellung (gleiche Formen wie bisher, nur verschoben).

Gegner-KI „klug“, sechs Seeds (Festung vier). Die offenen Karten sind neu,
die Zahlen also nicht mit Lauf 32 vergleichbar; zum Vergleich steht die
alte kleine Karte daneben (Lauf 32, zwölf Seeds).

| Szenario | Taktik | Siege | Verlust Stadt | Verlust Feind | Häuser verloren (von 30) | Lauf 32 (klein) |
|---|---|---|---|---|---|---|
| siedlung | linie | 0/6 | 100 % | 56 % | 27,3 | 3/12 |
| siedlung | schlachtordnung | 6/6 | 57 % | 65 % | 17,5 | 0/12 |
| siedlung | linie_reiter | 6/6 | 18 % | 49 % | 0,3 | 2/12 |
| siedlung | linie_aktiv | 2/6 | 98 % | 65 % | 27,2 | 1/12 |
| siedlung | linie_tief | 6/6 | 30 % | 47 % | 2,7 | 12/12 |
| siedlung | passiv | 4/6 | 73 % | 72 % | 26,2 | 2/12 |
| siedlung | angriff | 6/6 | 30 % | 58 % | 11,0 | 1/12 |
| siedlung_angriff | phalanxstoss | 1/6 | 81 % | 48 % | – | 3/12 |
| siedlung_angriff | vorruecken | 0/6 | 53 % | 11 % | – | 0/12 |
| siedlung_angriff | angriff | 0/6 | 46 % | 12 % | – | 0/12 |
| horde | vorruecken | 6/6 | 31 % | 71 % | – | 7/12 |
| horde | angriff | 6/6 | 19 % | 26 % | – | 12/12 |
| festung | tore | 0/4 | 100 % | 39 % | 3,0 | 0/12 |
| festung | passiv | 0/4 | 100 % | 41 % | 4,5 | 1/12 |
| festung_angriff | rammbock | 4/4 | 46 % | 100 % | – | 8/8 |
| festung_angriff | turm | 2/4 | 66 % | 79 % | – | 0/8 |

**Offene Siedlung, Verteidigung.** Auf der großen Karte ist mehr Platz an
den Flanken; die Räuber umgehen eine dünne Linie („linie“, „linie_aktiv“)
und plündern fast alle Häuser. Wer seine Reiter jagen lässt oder tief
steht, gewinnt fast ohne Hausverlust. Der Gegner wählt fast immer
„In den Rücken fallen“ und „Binden und Umfassen“.

**Offene Siedlung, Angriff.** Weiter schwer: Die Siedlung hält, die eigene
Truppe flieht nach 40 bis 90 Sekunden (Vorrücken, Angriff), nur der
Phalanxstoß gewinnt einmal.

**Horde.** Auf der großen Karte gewinnt man immer; der lange Anmarsch
(rund 20 Kacheln) gibt Zeit, sich zu ordnen.

**Festung.** Die Verteidigung gegen das doppelt so starke Heer verliert mit
beiden einfachen Taktiken. Im Angriff gewinnt der Turm jetzt zwei von vier
(Lauf 32: keinmal): Wer über den Turm kommt und oben steht, schließt sich
dort und kämpft geordnet, statt aufgelöst stehen zu bleiben.

Für die Balance: Verteidigung der offenen Siedlung mit dünner Linie, Angriff
auf die offene Siedlung und Verteidigung der Festung sind zu schwer; die Horde
ist zu leicht.

## Lauf 32 (3. Oktober 2026): Bewegung, Drehtempo, Gassen, Fernkampf, Jagen

Neu seit Lauf 31:

- Bewegungskorrekturen (Häuser meiden, Stau auflösen, Nachzügler, Peltasten
  treten beiseite).
- Drehtempo nach Breite. Zuerst für alle Gruppen, dann nur noch für Hopliten
  in Ordnung, siehe unten.
- Abstandsraster der Blockwege auf Kachelmitten und -grenzen: Die Phalanx
  zieht als Kolonne durch Gassen von einer Kachel.
- Breiter Block gleitet an der Ecke eines Nachbarn vorbei (nur der Spieler).
- Fernkampf mit Vorhalten und Streuung.
- Reiter jagen (die Taktiken benutzen es nicht).

Zwölf Seeds (Festung im Angriff acht), Lauf 31 → 32:

| Szenario | Taktik | Siege | Häuser verloren |
|---|---|---|---|
| offen | linie | 6 → 3 | 7,2 → 7,8 |
| offen | schlachtordnung | 7 → 0 | 7,1 → 8,0 |
| offen | linie_reiter | 7 → 2 | 7,0 → 7,8 |
| offen | linie_aktiv | 7 → 1 | 6,3 → 7,9 |
| offen | linie_tief | 11 → 12 | 4,8 → 0,7 |
| offen | passiv | 8 → 2 | 6,2 → 7,3 |
| offen | angriff | 12 → 1 | 5,3 → 7,9 |
| palisade | tor_halten | 0 → 1 | 8,0 → 7,6 |
| palisade | tor_reserve | 9 → 6 | 4,2 → 6,5 |
| palisade | tor_leiter | 11 → 10 | 1,6 → 2,5 |
| palisade | passiv | 9 → 7 | 5,2 → 6,2 |
| horde | vorruecken, angriff | 10, 12 → 7, 12 | – |
| angriff_offen | phalanxstoss, vorruecken, angriff | 1, 0, 0 → 3, 0, 0 | – |
| angriff_wall | beide | 0 → 0 | – |
| festung | tore, passiv | 0, 0 → 0, 1 | 5,7, 5,5 → 9,5, 4,2 |
| festung_angriff | rammbock, turm | 8/8, 0/8 → 8/8, 0/8 | – |

**Drehtempo.** Ein erster Lauf mit dem Drehtempo für alle Gruppen brach stark
ein: Horde „vorruecken“ 10 → 4, Festung im Angriff mit Rammbock 8/8 → 0/8.
Varianten auf wenigen Seeds zeigten die Ursache:

- Altes Raster, neues Drehtempo: ebenso schlecht. Das Raster war es also
  nicht.
- Nur der Gegner mit altem Tempo: Horde 5 von 6.
- Nur der Spieler mit altem Tempo: Horde 2 von 6.

Breite Räuberhaufen wendeten so schwerfällig wie eine Phalanx und kamen
dadurch anders heran. Seitdem bremst die Breite nur Hopliten in Ordnung;
Haufen, Plänkler und Stürmende drehen wie vorher. Lauf 32 ist mit dieser
Korrektur gemessen.

**Offenes Feld.** Fast alle Taktiken verlieren deutlich mehr; nur
„linie_tief“ gewinnt (12 von 12, fast ohne Hausverlust). Bei „angriff“ ist
die Ursache gefunden: Mit dem neuen Raster geht eine Räubergruppe 0,15
Kacheln weiter an den Hopliten vorbei. Sie gerät nicht mehr in deren
Angriffsweite (zwei Kacheln) und plündert, statt mitzukämpfen. Der alte Sieg
hing an dieser Schwelle. Für die übrigen Taktiken ist die Ursache noch
offen; dazu kommen der Fernkampf (bewegte Räuber werden seltener getroffen)
und die Räuberwege um die Häuser. Das ist Arbeit für die Balance.

Nach Lauf 32 kamen noch Änderungen an der Bewegung der Gegner dazu
(README, „Kein Zappeln an Schwellen“). Sie verschieben die Schlachten
wieder; vor der Balance wird neu gemessen. Ebenso zwei Korrekturen am
Umweg und am Weichen eigener Gruppen (README, „Kein großer Bogen um die
Nachbarn“). Sie gelten nur für Märsche an einen Platz und befohlene Gruppen
des Spielers, nicht für Angriffe; die Szenariotests sind unverändert.

## Lauf 31 (3. Oktober 2026): Modi der Hopliten und Verbände

Neu seit Lauf 30 (README, „Modi der Hopliten“ und „Verbände“):

- **Modi:** Hopliten sind locker oder in Phalanx, dazu kommt der Sturm. Die
  Phalanx wird an Tor und Gasse schmaler, statt sich aufzulösen. Ein
  dritter Modus „Geschlossen“ wurde gebaut, gemessen und danach wieder
  entfernt; er war zu nah an der Phalanx.
- **Verbände statt gemischter Gruppen:** Eine gemischte Gruppe der
  Aufstellung wird in der Schlacht je Gattung eine Gruppe, zusammen ein
  Verband.

Die Taktiken der Simulation benutzen weder Modi noch Verbände. Gemessen
wurde, ob sich dadurch etwas verschiebt.

Zwölf Seeds (Festung im Angriff acht), Lauf 30 → 31:

| Szenario | Taktik | Siege | Häuser verloren |
|---|---|---|---|
| offen | alle sieben | genau wie Lauf 30 | genau wie Lauf 30 |
| palisade | tor_halten | 0 → 0 | 8,0 → 8,0 |
| palisade | tor_reserve | 6 → 9 | 5,1 → 4,2 |
| palisade | tor_leiter | 10 → 11 | 1,8 → 1,6 |
| palisade | passiv | 9 → 9 | 5,2 → 5,2 |
| horde | vorruecken, angriff | 10, 12 → 10, 12 | – |
| angriff_offen | alle | 1, 0, 0 → 1, 0, 0 | – |
| angriff_wall | beide | 0 → 0 | – |
| festung | tore | 0 → 0 | 6,8 → 5,7 |
| festung | passiv | 0 → 0 | 4,5 → 5,5 |
| festung_angriff | rammbock, turm | 8/8, 0/8 → 8/8, 0/8 | – |

Im offenen Feld ist alles gleich, Schlacht für Schlacht. An der Palisade
gewinnt „tor_reserve“ 3 Siege dazu. Dort zieht die Phalanx jetzt als Block
durchs Tor, statt sich aufzulösen. Alles Übrige liegt im Rahmen der
Schwankung.

Lauf 31 lief auf dem Stand vor den Bewegungskorrekturen danach (Häuser
meiden, Stau auflösen, Nachzügler, Peltasten treten beiseite); deren
Messung folgt als Lauf 32.

## Lauf 30 (3. Oktober 2026): Umweg-Flackern behoben

Ein Haufen, der um eine eigene Gruppe herum wollte, schaltete an der
Schwelle „im Weg / vorbei“ oft jeden Schritt zwischen Umweg und geradem Weg
um, und nach einem Umweg wählte er manchmal die andere Seite und lief
zurück. Gefunden und behoben (README, „Umwege ohne Hin und Her“):

- **Spiel an der Schwelle:** Der Umweg endet erst mit 0,25 Kacheln mehr
  Abstand, als er braucht, um zu beginnen. Der Umwegpunkt liegt weitere
  0,25 Kacheln außen.
- **Gemerkte Seite:** Die Seite bleibt 1,5 s gemerkt.
- **Breite unabhängig vom Schwenk:** Die eigene Breite zählt, als zeige die
  Front in den Weg. Vorher schaltete das Schwenken zum Umwegpunkt den Umweg
  selbst wieder ab.
- **Gegenseitiges Warten:** Wartete ein zurückweichender Haufen im Tor auf
  einen, der hinein wollte, und umgekehrt, standen beide bis zum Ende.
  Jetzt lässt der angreifende den anderen vorbei.
- **Kreis:** Die KI schickte Gruppen gegen einen Kreis an eine Flanke, die
  es nicht gibt. Dort blieben sie stehen, und hinter ihnen stauten sich die
  anderen. Jetzt greifen sie an.

Gezählt über drei Seeds je Taktik (offen „linie“, „angriff“, „linie_aktiv“,
Palisade „tor_halten“), ohne → mit Korrektur:

- Seitenwechsel: 243 → 64
- Umschalten zwischen Umweg und geradem Weg binnen 0,2 s: 1484 → 473

Ein Rest bleibt, meist dort, wo der Umwegpunkt am Wall liegt und
abwechselnd begehbar ist oder nicht.

Zwölf Seeds (Festung im Angriff acht), Lauf 29 → 30:

| Szenario | Taktik | Siege | Häuser verloren |
|---|---|---|---|
| offen | linie | 4 → 6 | 7,6 → 7,2 |
| offen | schlachtordnung | 10 → 7 | 4,7 → 7,1 |
| offen | linie_reiter | 8 → 7 | 5,2 → 7,0 |
| offen | linie_aktiv | 11 → 7 | 2,7 → 6,3 |
| offen | linie_tief | 10 → 11 | 4,0 → 4,8 |
| offen | passiv | 2 → 8 | 7,8 → 6,2 |
| offen | angriff | 12 → 12 | 6,4 → 5,3 |
| palisade | tor_halten | 1 → 0 | 7,8 → 8,0 |
| palisade | tor_reserve | 5 → 6 | 5,4 → 5,1 |
| palisade | tor_leiter | 9 → 10 | 2,8 → 1,8 |
| palisade | passiv | 5 → 9 | 6,2 → 5,2 |
| horde | vorruecken | 12 → 10 | – |
| horde | angriff | 11 → 12 | – |
| angriff_offen | phalanxstoss | 1 → 1 | – |
| angriff_offen | vorruecken, angriff | 0 → 0 | – |
| angriff_wall | beide | 0 → 0 | – |
| festung | tore | 1 → 0 | 7,1 → 6,8 |
| festung | passiv | 1 → 0 | 3,8 → 4,5 |
| festung_angriff | rammbock | 8/8 → 8/8 | – |
| festung_angriff | turm | 1/8 → 0/8 | – |

In der Summe bleibt die Balance fast gleich: offen 57 → 58 Siege, Palisade
20 → 25. Sie verschiebt sich aber zwischen den Taktiken:

- **Aktive Taktiken verlieren:** Die Räuber stehen nicht mehr hinter
  eigenen Haufen herum und plündern mehr Häuser. Die Schlachtordnung
  verliert 3 Siege, „linie_aktiv“ 4.
- **„passiv“ gewinnt deutlich** (offen 2 → 8, Palisade 5 → 9). Der Grund
  ist nicht untersucht. Vermutlich laufen die Räuber jetzt geschlossener
  frontal in die stehende Phalanx, statt sich zu verteilen.

Das ist ein Punkt für die Balance-Runde: Stillstehen sollte nicht die
beste Taktik sein.

## Lauf 29 (3. Oktober 2026): Hauptmann, Kontermarsch, Wehrgang, Wegwahl nach Zeit

Neu seit Lauf 28 (README, „Hauptmann und Kontermarsch“, „Wehrgang“ und
„Marsch im Bogen“):

- Jede Gruppe hat einen Hauptmann in der Mitte. Fällt er, rückt der
  nächste nach. Er bringt keine Boni.
- Hopliten machen außerhalb des Nahkampfs eine Kehrtwendung als
  Kontermarsch. Jede Rotte dreht in sich, die Reihenfolge der Glieder
  bleibt, und das braucht Zeit (0,6 s + 0,3 s je weiteres Glied). Im
  Nahkampf und bei Reitern bleibt der sofortige Tausch.
- Auf dem Wehrgang stehen die Männer dicht in vier Rotten je Feld. Feinde
  schlüpfen nicht mehr aneinander vorbei, Hopliten dürfen auf die Mauer.
  Die Reserve der Besatzung steigt am bedrohten Turm auf den Wehrgang.
  Leiter runter und woanders wieder hoch nimmt eine Gruppe nur, wenn das
  samt Kletterzeit schneller ist als der Weg oben entlang.
- Die Wegwahl richtet sich nach der Zeit: als Block außen herum oder kurz
  auflösen, Mann für Mann durch und neu aufstellen (mit Zeit fürs Ordnen
  und fürs Gedränge in der Gasse). Das ersetzt die festen Faktoren 1,2 und
  1,4 aus Lauf 27 und 28.

Zwölf Seeds (Festung im Angriff acht), Lauf 28 → 29:

| Szenario | Taktik | Siege | Häuser verloren |
|---|---|---|---|
| offen | linie | 3 → 4 | 7,8 → 7,6 |
| offen | schlachtordnung | 8 → 10 | 4,2 → 4,7 |
| offen | linie_reiter | 5 → 8 | 6,6 → 5,2 |
| offen | linie_aktiv | 10 → 11 | 3,6 → 2,7 |
| offen | linie_tief | 10 → 10 | 3,1 → 4,0 |
| offen | passiv | 5 → 2 | 7,6 → 7,8 |
| offen | angriff | 11 → 12 | 6,3 → 6,4 |
| palisade | tor_halten | 2 → 1 | 7,8 → 7,8 |
| palisade | tor_reserve | 6 → 5 | 5,8 → 5,4 |
| palisade | tor_leiter | 12 → 9 | 0,5 → 2,8 |
| palisade | passiv | 4 → 5 | 6,9 → 6,2 |
| horde | vorruecken | 12 → 12 | – |
| horde | angriff | 12 → 11 | – |
| angriff_offen | phalanxstoss | 1 → 1 | – |
| angriff_offen | vorruecken, angriff | 0 → 0 | – |
| angriff_wall | beide | 0 → 0 | – |
| festung | tore | 1 → 1 | 6,6 → 7,1 |
| festung | passiv | 1 → 1 | 5,1 → 3,8 |
| festung_angriff | rammbock | 6/8 → 8/8 | – |
| festung_angriff | turm | 0/8 → 1/8 | – |

Was sich bewegt:

- Im offenen Feld gewinnt der Spieler etwas öfter: Schlachtordnung 10,
  aktive Reiter 8. Vermutlich, weil die Gruppen mit der
  Wegwahl nach Zeit seltener an eigenen Haufen hängen bleiben.
- „passiv“ fällt auf 2 Siege. Wer nur steht, profitiert nicht davon.
- „tor_leiter“ hinter der Palisade fällt von 12 auf 9 Siege, und es gehen
  mehr Häuser verloren (0,5 → 2,8). Die Räuber auf dem Wehrgang stehen
  jetzt dicht und lassen sich nicht mehr umlaufen, also hält die Leiter
  schlechter.
- Gegen die Festung im Angriff hält der Rammbock wieder 8/8. Die dichten
  Rotten auf dem Wehrgang und die Reserve am Turm helfen dem Spieler als
  Verteidiger.
- Die Turm-Taktik der Simulation läuft meist bis zur Zeitgrenze (279 s).
  Sie greift die fliehenden Reste der Besatzung an der Agora nicht an, und
  deshalb endet die Schlacht nicht. Das ist eine Schwäche des Skripts,
  nicht des Spiels.

## Lauf 27 und 28 (3. Oktober 2026): Reiter im Bogen, Block um eigene, Gassen

Lauf 27: Reiter traben aus dem Stand im Bogen an und reiten mit der Front
voraus. Eine ruhende eigene Gruppe am Rand des Weges umgeht ein Block im
Bogen, wenn der Umweg höchstens ein Fünftel länger ist; sonst geht er wie
bisher Mann für Mann vorbei. Lauf 28: Passt ein Block nicht durch eine
Gasse zwischen Häusern und wäre der Weg außen herum mehr als 1,4-mal so lang
wie für einzelne Männer, geht er Mann für Mann hindurch. Reiter traben
durch enge Wendungen, statt im Galopp eine Schleife zu ziehen. Beispiel aus
der Festung: Reiter brauchten für 4,9 Kacheln Luftlinie zwischen den
Häusern 10,8 Kacheln Weg und 4,4 s, jetzt 6,7 Kacheln und 2,1 s.

Zwölf Seeds (Festung im Angriff acht), Lauf 26 → 27 → 28:

| Szenario | Taktik | Siege | Häuser verloren |
|---|---|---|---|
| offen | linie | 4 → 3 → 3 | 7,7 → 7,8 → 7,8 |
| offen | schlachtordnung | 9 → 8 → 8 | 5,9 → 4,2 → 4,2 |
| offen | linie_reiter | 9 → 4 → 5 | 5,5 → 6,8 → 6,6 |
| offen | linie_aktiv | 12 → 12 → 10 | 1,8 → 1,2 → 3,6 |
| offen | linie_tief | 8 → 12 → 10 | 6,7 → 2,2 → 3,1 |
| offen | passiv | 5 → 5 → 5 | 7,6 → 7,6 → 7,6 |
| offen | angriff | 10 → 11 → 11 | 6,0 → 6,3 → 6,3 |
| palisade | tor_halten | 0 → 2 → 2 | 8,0 → 7,8 → 7,8 |
| palisade | tor_reserve | 8 → 5 → 6 | 4,5 → 6,1 → 5,8 |
| palisade | tor_leiter | 12 → 12 → 12 | 0,3 → 0,5 → 0,5 |
| palisade | passiv | 7 → 4 → 4 | 5,4 → 6,9 → 6,9 |
| horde | vorruecken | 12 → 12 → 12 | – |
| horde | angriff | 10 → 12 → 12 | – |
| angriff_offen | phalanxstoss | 0 → 1 → 1 | – |
| angriff_offen | vorruecken, angriff | 0 → 0 → 0 | – |
| angriff_wall | beide | 0 → 0 → 0 | – |
| festung | tore | 1 → 1 → 1 | 3,4 → 7,6 → 6,6 |
| festung | passiv | 0 → 0 → 1 | 4,1 → 5,5 → 5,1 |
| festung_angriff | rammbock | 7/8 → 6/8 → 6/8 | – |
| festung_angriff | turm | 0/8 → 0/8 → 0/8 | – |

Auf den alten Karten verschiebt sich vieles um ein bis vier Siege in beide
Richtungen. Deutlich sind: Die Taktik mit aktiven Reitern („linie_reiter“)
fällt von 9 auf 4 bis 5 Siege, „passiv“ hinter der Palisade von 7 auf 4. In
der Festung plündert das Heer mehr Häuser (3,4 → 6,6 bis 7,6), weil es als
Block um die eigenen Gruppen herum- und durch die Gassen schneller vorankommt.

## Lauf 26 (3. Oktober 2026): Marsch im Bogen

Auf längeren Wegen über freies Feld läuft Fußvolk in seiner Blickrichtung
an und schwenkt unterwegs zum Ziel, statt erst auf der Stelle zu drehen und
dann geradeaus zu gehen. Eine Linie behält unterwegs ihre Breite und
marschiert erst 1,5 Kacheln vor dem Ziel in Breite und Front auf (README,
„Marsch im Bogen“). Das gilt für beide Seiten. Wer durchs offene Tor die
Wallseite wechselt, löst sich jetzt auch auf, wenn die gerade Linie genau
durch die Öffnung führt (vorher ging ein Block dann geschlossen hindurch).
Die Ankunftszeiten einer Linie bleiben fast gleich (gemessen 7,2 statt 7,2 s,
8,4 statt 8,9 s, 7,4 statt 7,2 s).

Zwölf Seeds (Festung im Angriff acht), verglichen mit Lauf 25:

| Szenario | Taktik | Siege vorher → jetzt | Häuser verloren vorher → jetzt |
|---|---|---|---|
| offen | linie | 5/12 → 4/12 | 7,5 → 7,7 |
| offen | schlachtordnung | 11/12 → 9/12 | 2,6 → 5,9 |
| offen | linie_reiter | 5/12 → 9/12 | 6,8 → 5,5 |
| offen | linie_aktiv | 11/12 → 12/12 | 2,1 → 1,8 |
| offen | linie_tief | 10/12 → 8/12 | 4,2 → 6,7 |
| offen | passiv | 1/12 → 5/12 | 7,9 → 7,6 |
| offen | angriff | 9/12 → 10/12 | 6,8 → 6,0 |
| palisade | tor_halten | 1/12 → 0/12 | 7,9 → 8,0 |
| palisade | tor_reserve | 6/12 → 8/12 | 5,8 → 4,5 |
| palisade | tor_leiter | 11/12 → 12/12 | 1,3 → 0,3 |
| palisade | passiv | 8/12 → 7/12 | 5,4 → 5,4 |
| horde | vorruecken, angriff | 12/12, 10/12 → 12/12, 10/12 | – |
| angriff_offen | phalanxstoss | 1/12 → 0/12 | – |
| angriff_offen | vorruecken, angriff | 0/12 → 0/12 | – |
| angriff_wall | beide | 0/12 → 0/12 | – |
| festung | tore | 0/12 → 1/12 | 4,0 → 3,4 |
| festung | passiv | 0/12 → 0/12 | 4,7 → 4,1 |
| festung_angriff | rammbock | 8/8 → 7/8 | – |
| festung_angriff | turm | 0/8 → 0/8 | – |

Im Ganzen eher etwas zugunsten des Spielers, aber gemischt: „Reiter aktiv“
und „passiv“ in der offenen Siedlung gewinnen 4 dazu, „tief“ und die
Schlachtordnung verlieren 2 und mehr Häuser. Die Taktiken des Simulators
setzen ihre Linien zu Beginn über weite Wege, daher kommen sie jetzt in
anderer Ordnung an.

Der Pfadtest „kein Hin und Her beim Umweg“ läuft ohne Bögen (wie schon ohne
Reserve): Mit Bögen rückt ein anderer Haufen zuerst an und trifft auf das
bekannte Umweg-Flackern (Ideenliste).

## Lauf 25 (3. Oktober 2026): Die Gegner lösen sich auf

`LOOSE_AI` ist an: Räuber, Siedlung und Heer gehen wie die Gruppen des
Spielers Mann für Mann durchs offene Tor und an ruhenden eigenen Haufen
vorbei. Steht dabei ein Feind näher als 2,5 Kacheln, bleiben sie Block (am
umkämpften Tor galt das schon). Ohne diese Ausnahme plünderten die Räuber im
Abnahmetest „Phalanx, dann Verfolgung“ deutlich mehr: Über acht Startwerte
standen am Ende im Mittel 3,3 statt 6,0 Häuser, mit ihr 5,9.

Zwei Dinge fielen beim Messen auf und sind behoben:

- **Ruckler am Tor:** Bevor sich eine Gruppe auflöst, prüft sie mit einem
  Wegefeld, ob ihre Männer durchkommen. Diese Prüfung lief am Budget je Takt
  vorbei. Auf der Festungskarte dauerte ein Takt bis zu 300 ms, wenn sich zwei
  Gruppen zugleich auflösten. Jetzt löst sich eine Gruppe einen Takt später
  auf, wenn das Budget verbraucht ist. Gemessen: höchstens 56 ms je Takt, im
  Mittel 13–14 ms (vorher 12 ms).
- **Stillstand:** Gezählt wurde, wie lange Gegnergruppen ein Ziel haben,
  nicht kämpfen und sich trotzdem kaum bewegen. Das betrifft fast nur das
  Übersteigen am Turm: Auf der Palisade geht die Hälfte der aktiven
  Räuberzeit dafür drauf, weil alle über einen Turm und eine Leiter müssen
  (rund 2,5 Mann je Sekunde). Das war schon ohne den Schalter so. Für ein
  Tor oder eigene Haufen hängt keine Gegnergruppe fest. Gassen zwischen
  Häusern sind für Gegnerblöcke keine Falle: Für einen breiten Block gab es
  nie keinen Weg, wo einzelne Männer noch durchkämen.

Zwölf Seeds (Festung im Angriff acht), verglichen mit Lauf 24 und 24b:

| Szenario | Taktik | Siege vorher → jetzt | Häuser verloren vorher → jetzt |
|---|---|---|---|
| offen | linie | 5/12 → 5/12 | 7,5 → 7,5 |
| offen | schlachtordnung | 8/12 → 11/12 | 6,8 → 2,6 |
| offen | linie_reiter | 5/12 → 5/12 | 6,7 → 6,8 |
| offen | linie_aktiv | 11/12 → 11/12 | 2,1 → 2,1 |
| offen | linie_tief | 10/12 → 10/12 | 3,9 → 4,2 |
| offen | passiv | 1/12 → 1/12 | 7,9 → 7,9 |
| offen | angriff | 9/12 → 9/12 | 6,8 → 6,8 |
| palisade | tor_halten | 1/12 → 1/12 | 7,9 → 7,9 |
| palisade | tor_reserve | 8/12 → 6/12 | 4,8 → 5,8 |
| palisade | tor_leiter | 12/12 → 11/12 | 0,2 → 1,3 |
| palisade | passiv | 0/12 → 8/12 | 8,0 → 5,4 |
| horde | vorruecken, angriff | 12/12, 10/12 → 12/12, 10/12 | – |
| angriff_offen | phalanxstoss | 1/12 → 1/12 | – |
| angriff_offen | vorruecken, angriff | 0/12 → 0/12 | – |
| angriff_wall | beide | 0/12 → 0/12 | – |
| festung | tore | 4/12 → 0/12 | 2,3 → 4,0 |
| festung | passiv | 1/12 → 0/12 | 3,1 → 4,7 |
| festung_angriff | rammbock | 8/8 → 8/8 | – |
| festung_angriff | turm | 0/8 → 0/8 | – |

Die offene Siedlung bleibt fast gleich. Dort greift die Ausnahme nahe am
Feind, die Schlachtordnung profitiert sogar. Am deutlichsten verliert der
Spieler in der Festung: Das Heer kommt aufgelöst schneller durch die
geöffneten Tore und an den Rammbockgruppen vorbei; „Tore halten“ gewinnt
nie mehr (vorher 4 von 12). Palisade „passiv“ springt wie schon in früheren
Läufen (1, 6, 0, jetzt 8); die Taktik schwankt mit jeder Änderung stark.

## Lauf 24b (2. Oktober 2026): Kreis nur als Verzweiflungstat

Auf Wunsch bildet die KI den Kreis nicht mehr gegen Reiter, sondern nur noch,
wenn eine Hoplitengruppe klar in Unterzahl ist (im Umkreis von drei Kacheln
anderthalbmal so viele Feinde wie eigene Leute, Nachbarn zählen mit) und
umzingelt (Feinde auf drei Seiten, oder vorn und hinten). Gegen Reiter dreht
sie weiterhin die Front, wenn vorn kein Fußvolk steht. Räuber sind davon
nicht betroffen; neu gemessen wurden die Szenarien mit Hopliten auf der
Gegnerseite (zwölf Seeds, Festung im Angriff acht):

| Szenario | Taktik | Siege Lauf 22 → 24 → jetzt | Häuser verloren 22 → 24 → jetzt |
|---|---|---|---|
| festung | tore | 4/12 → 2/12 → 4/12 | 2,3 → 4,0 → 2,3 |
| festung | passiv | 0/12 → 0/12 → 1/12 | 3,4 → 4,1 → 3,1 |
| festung_angriff | rammbock | 8/8 → 0/8 → 8/8 | – |
| festung_angriff | turm | 0/8 → 0/8 → 0/8 | – |
| angriff_offen | phalanxstoss | 0/12 → 0/12 → 1/12 | – |
| angriff_offen | vorruecken, angriff | 0/12 → 0/12 → 0/12 | – |
| angriff_wall | beide | 0/12 → 0/12 → 0/12 | – |

Die Festung im Angriff ist damit wieder so leicht wie vorher. In je drei
Läufen dieser Taktiken (Festung tore, Festung im Angriff rammbock, Siedlung
phalanxstoss) kam weder ein Kreis noch ein Drehen gegen Reiter vor: Beides
ist in den gespielten Lagen selten, die Taktiken des Simulators umzingeln
nicht und reiten selten in eine freie Flanke.

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
einem Zug verliert 4 Siege, „Tor mit Reserve“ gewinnt 4 dazu. Einzeln
abgeschaltet gemessen (offen „angriff“, noch mit der unten verworfenen
Korrektur an der Schwelle): ohne Reserve 0 statt 3 von 12. Die Reserve
der Räuber hilft dem angreifenden Spieler dort also eher, weil sie der
Hauptmacht vorn fehlt. Der Abnahmetest „Phalanx, dann Verfolgung“
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
