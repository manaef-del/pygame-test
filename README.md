# Apoikia – Kampfprobe

Ein eigenständiger Prototyp für die Kampfmechanik von **Apoikia**, dem
Pygame-Koloniespiel. Hier wird nur die taktische Ebene gebaut und im
Browser getestet. Was sich bewährt, wandert später ins Hauptprojekt.

## Was der Prototyp umsetzt

Aus dem Apoikia-Konzept (Teil A·12 und B4) und dem Wirtschaftsregister
(Tabellen 7, 10, 11):

- **Gekämpft wird in Gruppen.** Der Ausgang wird je Gruppe gerechnet.
  Eine Gruppe ist eine geordnete Reihe von Männern, beliebig gemischt,
  die in Reihen aufgestellt wird. Die vordere Reihe kämpft im Nahkampf,
  Hopliten der zweiten Reihe stechen mit, Peltasten in hinteren Reihen
  werfen über die Front. Treffer gehen in die Reihe, die dem Angreifer
  zugewandt ist.
- **Truppentypen:** schwere, mittlere und leichte Hopliten (dunkel-,
  mittel-, hellblau), Peltasten (rot) und Reiter (grün). Räuber sind grau
  mit rotem Ring. Vorgabe: 40 Hopliten, 15 Peltasten, 20 Reiter.
- **Peltasten** haben zehn Speere je Mann und werfen in Salven. Jeder
  Speer fliegt sichtbar vom werfenden Mann zu einem bestimmten Gegner
  und trifft nur diesen. Sind die Speere verschossen, geht die Gruppe in
  den Nahkampf über. Das gilt für beide Seiten: auch die Peltasten der
  Räuber tragen zehn Speere und stürmen, sobald sie leer sind.
- **Schild an Schild.** Der Kampf beginnt auf Speerweite (gut eine halbe
  Kachel Lücke zwischen den Formationen), angreifende Gruppen schließen
  aber weiter auf, bis nur noch ein Spalt bleibt. Wer im Handgemenge
  steht, kommt erst mit gut einer Kachel Abstand wieder los, das Lösen
  dauert also.
- **Haufen legen sich um den Gegner.** Räuber und Peltasten im freien
  Angriff behalten im Handgemenge nicht ihr Rechteck: Ihre Männer
  verteilen sich Reihe für Reihe dicht am Umriss der feindlichen
  Formation, um das nächstgelegene Stück herum, und zwar nur dort, wo
  wirklich feindliche Männer stehen, nicht am leeren Teil des Rechtecks. Wer das Ende einer Linie
  angreift, zieht sich wie ein C darum und greift sie auch von vorn und
  hinten an, statt starr daneben zu stehen. Reiter tun das nicht, und
  Hopliten bleiben ein Block: Stürmen sie einen schmaleren Gegner,
  klappen nur die überstehenden Flügel an dessen Ecken ein, bis an seine
  Flanken und nie in seinen Rücken, die Mitte bleibt gerade, und die
  Reihe schließt neben der Ecke auf. Steht ein weiterer Feind näher als
  drei Kacheln, klappt nichts ein, damit niemand ihm den Rücken zukehrt.
  Fällt ein Mann der
  ersten Reihe, rückt sofort einer aus der Reihe dahinter in die Lücke;
  die Front bleibt voll, die letzte Reihe schrumpft.
- **Jeder Mann zählt einzeln.** Er hat eigene Trefferpunkte (verwundete
  Punkte sind dunkler) und eine eigene Position: Er läuft zu seinem
  Platz in der Formation, weicht aber selbst aus, durchs Tor nur durch
  die Öffnung, auf den Wall nur über Leiter oder Turm.
- **Reiter** sitzen ab, sobald sie Rammbock oder Turm bauen oder auf den
  Wehrgang steigen. Die Pferde bleiben als braune Punkte zurück; danach
  sind sie so schnell wie Fußvolk und ohne Reiterbonus. Ohne Gerät zu
  den Pferden geschickt, sitzen sie wieder auf. Durch ein aufgebrochenes
  Tor reiten sie beritten.
- **Aufstellung:** Vor der Schlacht werden Gruppen aus einem gemeinsamen
  Vorrat zusammengestellt, der Truppenstärke. Eine Gruppe besteht aus
  Reihen-Blöcken von vorn nach hinten, jeder Block mit einem Truppentyp
  (Farbpunkt) und einer Anzahl (Schieberegler). Die Gattungen sind frei
  tauschbar: Wer die Reiter auf null stellt, kann die Männer bei den
  Hopliten oder sonstwo wieder einsetzen. Der Regler für die Stärke
  skaliert alle Blöcke mit. Blöcke lassen sich verschieben, entfernen
  und hinzufügen. Vorgabe: je eine Gruppe Hopliten, Peltasten und Reiter.
- **Front aufziehen:** Gruppe antippen, dann auf der Karte den Finger
  aufsetzen und eine Linie ziehen. Die Linie ist die Front, ihre Länge
  bestimmt die Breite und damit die Zahl der echten Reihen. Landen
  mehrere Blöcke in einer Reihe, wechseln sich ihre Männer ab. Die Gruppe
  schaut senkrecht zur Linie: von links nach rechts gezogen nach oben, so
  wie man hinter ihr steht. Ohne Auswahl teilen sich alle Gruppen die
  Linie.
- **Phalanx:** eine aufgezogene Gruppe hält die Stellung. Stark von vorn,
  verwundbar in Flanke und Rücken. Der Bonus hängt vom Hoplitenanteil der
  vorderen Reihe ab. Nachbarn stützen sich (Schildwall). Front, Flanke und
  Rücken werden am Rechteck der Formation gemessen, nicht am Winkel vom
  Zentrum: Wer vor der Breite der Front steht, steht vorn; wer neben ihrem
  Ende steht, in der Flanke, es sei denn, dort schließt ein Nachbar die
  Linie oder er steht noch weit vor der Speerwand. Von der Flanke oder
  von hinten wehren sich nur die Männer am Rand (drei je Reihe, hinten
  die letzte Reihe), und nur sie werden getroffen; eine umfasste Phalanx
  verliert dort schnell Männer und Moral.
- **Angriff** (nur für gewählte Gruppen) heißt je Waffengattung etwas
  anderes: Hopliten verlassen die Phalanx und stürmen den nächsten
  Gegner, mit Anlauf werfen sie ungeordnete Gegner um (mit weniger Wucht
  als Reiter, nie eine Phalanxfront). Peltasten plänkeln: sie gehen auf
  Wurfweite an den nächsten Gegner heran, werfen und weichen zurück,
  sobald die Lücke zu ihm kleiner als anderthalb Kacheln wird; steht
  die eigene Phalanx im Weg, rücken sie dicht hinter sie und werfen über
  die Köpfe, oder gehen um ihr Ende herum, wenn es von dort nicht reicht;
  ohne Speere gehen sie in den Nahkampf. Reiter suchen sich das lohnendste Ziel (ungeordnete oder
  fliehende Gruppen, sonst Flanke oder Rücken einer Phalanx, nie deren
  Front), nehmen Anlauf, stoßen zu, setzen sich nach dem Aufprall auf
  eine stehende Phalanx drei Kacheln ab und laufen erneut an. Tippt man
  stattdessen einen Gegner an, greift die Gruppe genau ihn an.
- **Halten** (nur für gewählte Gruppen): Hopliten bilden an Ort und
  Stelle eine Phalanx mit der Front, wie sie gerade stehen; Peltasten und
  Reiter bleiben stehen und kämpfen rundum ohne Bonus.
- **Formationen:** Standard ist die Linie. Die Leiste zeigt für die
  gewählte Gruppe die möglichen Formationen, F schaltet weiter. Gruppen
  mit Fußvolk: Linie und Kreis (rundum Front ohne Flanke und Rücken,
  aber ohne den Rückhalt der Glieder: schwächer nach vorn, nur 60 % der
  Männer kämpfen) für den Fall, dass man umfasst wird oder weit in der
  Unterzahl ist. Die Größe des Kreises zieht man wie eine Linie: Tippen
  setzt die Mitte, die Länge des Zugs den Halbmesser (nie enger, als die
  Männer Platz brauchen, höchstens drei Kacheln); ein weiter Kreis steht
  lockerer. Reine Reiter: Linie und
  Keil; der Keil trifft beim Sturm halb so viele Männer, die aber fast
  doppelt so hart. Reine Peltasten: Linie und Kreis. Wer eine neue Linie
  zieht, steht wieder in Linie.
- **Gemischte Gruppen im Kreis** stehen in Schichten: das Fußvolk
  bildet den äußeren Ring, Reiter den mittleren,
  Peltasten den inneren; jede Schicht ist um einen Reihenabstand nach
  innen gerückt, die inneren Ringe stehen auf Lücke. Innerhalb einer
  Schicht wechseln die Reihen ab wie in einer einzigen langen Reihe:
  ein Mann der ersten Reihe, einer der zweiten, einer der dritten und so
  fort, damit schwere, mittlere und leichte Hopliten gleichmäßig um die
  Front verteilt sind. „Halten“ bildet nur bei Hoplitenmehrheit eine
  Phalanx.
- **Angriff einer gemischten Gruppe teilt sie** nach Gattung: Die Reiter
  stürmen voraus, die Peltasten folgen im Plänkeln, die Hopliten stürmen
  als Langsamste hinterher, jede Gattung in ihrem Tempo und mit ihrem
  eigenen Verhalten. Die Männer bleiben dabei stehen und laufen aus ihrer
  Position los; die größte Gattung behält die Gruppe, die anderen werden
  eigene Gruppen mit eigener Kachel. Alle Teile bleiben gewählt. Sind
  mehrere Gruppen gewählt, vereint „Vereinen“ (V) sie wieder zu einer
  Linie an ihrem gemeinsamen Schwerpunkt.
- **Wenden im Stand:** Bekommt eine stehende Gruppe ein Ziel in einer
  anderen Richtung, springt ihre Front nicht mehr um. Sie schwenkt mit
  einer halben Umdrehung je Sekunde, die Männer drehen auf ihren
  Plätzen mit, und erst wenn die Richtung grob stimmt (45 Grad), geht es
  los. Liegt das Ziel hinter der Gruppe, macht sie kehrt: Die hintere
  Reihe wird die vordere, links wird rechts, und jeder Mann bleibt fast
  auf seinem Platz. Das gilt für Reiter und Fußvolk, für Spieler und
  Gegner gleichermaßen; nur Fliehende und Kletternde wenden ohne
  Zeremonie. Auch eine befohlene Front (gezogene Linie, Rammbock am
  Tor, die Siedlung dreht ihre Linie zum Angreifer) wird mit derselben
  Drehrate eingeschwenkt, eine Phalanx tauscht dabei aber keine Reihen:
  Ihre schweren Männer bleiben vorn, sie schwenkt den vollen Winkel.
- **Schwung der Reiter:** Berittene fahren an (in gut einer Sekunde auf
  vollen Galopp), bremsen vor dem Ziel ab und wenden im Galopp in Bögen,
  deren Halbmesser mit dem Tempo wächst; im Stand drehen sie frei. Ohne
  Ziel rollen sie aus statt stehen zu bleiben. Beim Aufprall trägt der
  Schwung sie bis zu knapp eine Kachel in die feindliche Formation
  hinein, erst dort kommen sie zum Stehen.
- **Sturmangriff der Reiter:** Berittene, die mit mindestens zwei Kacheln
  Anlauf auf eine Gruppe treffen, prallen auf: Die vordersten Männer
  werden weggestoßen (leichte weiter als schwere, das Gewicht sind ihre
  Lebenspunkte), verletzt, die Ordnung der Gruppe ist dahin und ihre
  Moral leidet, von hinten noch mehr. Die Reiter selbst sind danach zwei
  bis drei Sekunden lang langsam. Gegen die Front einer stehenden
  Hoplitenphalanx gibt es keinen Aufprall: Die vordersten Reiter rennen
  in die Speere und fallen, je Speer der vorderen Reihe ein Stück.
- **Handgemenge bindet:** Jeder Mann, der einen Gegner in Reichweite hat
  (orangener Ring), steht fest, auch wenn seine Gruppe einen neuen Befehl
  bekommt; die anderen formieren sich um ihn herum. Eine vorn gebundene
  Phalanx lässt sich also nicht zur Flanke drehen, und ihr Bonus kehrt
  erst zurück, wenn alle Männer wieder auf ihren Plätzen stehen. Eine
  Gruppe im Nahkampf kommt nur mit einem Drittel ihrer Geschwindigkeit
  vom Fleck. Zieht sie sich mehr als gut eine Kachel zurück, reißen sich
  die Gebundenen los, und die Gruppe gilt vier Sekunden lang als von
  hinten angegriffen (anderthalbfacher Schaden, kein Formationsbonus).
  Lösen ist eine Entscheidung mit Preis, auch für die Räuber, die nach
  einem gescheiterten Angriff zurückweichen.
- **Moral, je Gruppe, für beide Seiten:** Verluste drücken die Moral, aus
  Flanke und Rücken stärker, von vorn in der Phalanx schwächer; unter der
  Schwelle flieht die Gruppe. Eine Gruppe aus mittleren Hopliten bricht
  etwa nach einem Drittel Verlusten aus der Flanke, schwere später,
  Peltasten früher. Flieht eine Nachbargruppe, wankt die eigene mit. Ist
  die Schlacht aussichtslos (eigene Seite unter 40 %, der Gegner noch
  über 60 %), sinkt die Moral aller Gruppen dieser Seite von selbst.
  Die Moral der gewählten Gruppe steht in der Statuszeile.
- **Räuber** ziehen zu den Häusern und plündern, wenn niemand sie stört.
  Sind sie zu geschwächt, ziehen sie ab.
- **Palisade mit Tor:** der einzige Durchgang. Wegfindung leitet durchs Tor.
- **Gegner-KI** (siehe unten): Der Gegner liest die Aufstellung, wählt
  einen Plan, greift schwache Ziele an, umgeht Phalanxfronten und lernt
  über Schlachten hinweg.

Abnahme aus dem Konzept (L9), als Tests umgesetzt: *Ein Überfall auf eine
unbefestigte Stadt tut weh. Eine Phalanx hinter Mauern gewinnt gegen eine
deutlich größere Übermacht.*

## Szenarien

Zwei Regler oben im Aufstellungsmenü setzen die eigene Stärke und die
des Gegners. Der Stärkeregler skaliert die Blöcke aller Gruppen
verhältnismäßig; danach kann man die Zahlen einzeln verschieben, auch
zwischen den Gattungen. Ins Feld zieht, was eingeteilt ist. Das Spiel
läuft mit halber Geschwindigkeit (`TIME_SCALE`).

| Szenario | Lage |
|----------|------|
| Verteidigung: Offene Siedlung | Räuberhaufen von Norden, zwei umgehen die Linie. Bei großer Zahl größere Haufen, mit einem Fünftel Peltasten |
| Verteidigung: Palisade | Das Tor ist zu, die Räuber bauen Rammbock und Turm. Eigene Peltastengruppen dürfen auf den Wehrgang |
| Angriff: Räuberhorde | Die Horde lagert im Norden und stürmt, sobald man ihr nahe kommt |
| Angriff: Siedlung ohne Wall | Die Siedlung stellt eine eigene Truppe, passend zur Mischung des Spielers (siehe Gegner-KI). Hopliten und Peltasten halten, Reiter greifen an |
| Angriff: Siedlung mit Wall | Wie oben, hinter einer Palisade mit verschlossenem Tor. Peltasten des Gegners stehen auf dem Wehrgang |

**Wehrgang:** Eine reine Peltastengruppe der Wallseite darf auf die
Palisade, aber nur über die Leitern hinauf und hinunter (helle Sprossen
auf der Palisade). Oben läuft sie entlang, auch über das Torhaus. Über
die Palisade wirft nur, wer oben steht, dafür eine Kachel weiter.
Der Wehrgang ist erhöht: Wer unten steht, kommt an die Männer oben nicht
heran und ist mit ihnen auch nicht im Handgemenge; von oben schlägt man
hinunter, mit einem Drittel der Wirkung. Nach oben helfen nur Speere,
Leitern oder ein Turm.

**Belagerungsgerät:** Beim Angriff auf die Siedlung mit Wall ist das Tor
verschlossen. Jede gewählte Gruppe kann ein Gerät bauen:
„Rammbock“ (acht Sekunden) oder „Turm“ (zwölf Sekunden). Mit Rammbock
das Tor antippen: die Gruppe geht hin und bricht es auf; nach dem
Durchbruch bleibt der Rammbock liegen und die Gruppe tritt zur Seite,
damit der Durchgang frei ist. Mit Turm ein
Wallstück antippen: die Gruppe rollt hin, setzt den Turm an, und nach
drei Sekunden steht er als Aufstieg auf den Wehrgang. Wer über den Turm
kommt, geht Mann für Mann: Beim Überqueren löst sich die Formation auf,
jeder steigt selbst am Turm hinauf, läuft über den Wehrgang und klettert
an einer Leiter hinunter; drinnen sammelt sich die Gruppe wieder. Auf
dem Wehrgang gibt es keinen Phalanxbonus, dort kämpft Mann gegen Mann.
Über den Turm geht es nur zurück nach außen. Leitern und Türme lassen
etwa drei Männer pro Sekunde durch, eine dichte Kolonne; die Gruppe
wartet auf ihre Nachzügler und die Nachzügler nehmen denselben Weg wie
die Gruppe, wer warten muss, stellt sich vor der Leiter an. Solange eine
Gruppe aufgelöst ist, kämpfen nur die Männer, die beim Gegner sind, und
nur sie werden getroffen. Leitern führen nur zur Innenseite des Walls.
Ein aufgebrochenes Tor ist unten ein Durchgang und oben eine Lücke im
Wehrgang: wer oben auf die andere Seite will, steigt an der Leiter ab,
läuft unten hinüber und drüben wieder hinauf. Durch eine feindliche
Formation läuft niemand hindurch, weder eine Gruppe noch ein einzelner
Mann; wer von der Leiter in eine Phalanx kommt, muss sie durchkämpfen
oder außen herum. Der Kartenrand ist keine Umgehung. Fällt eine Gruppe oder flieht sie, ist ihr Gerät verloren. Bei
der Verteidigung mit Palisade bauen die Räuber selbst Rammbock und Turm.

## Gegner-KI

`game/ai.py` steuert die Gegnerseite in drei Stufen, getrennt von der
Kampflogik. Der laufende Plan steht oben rechts im Bild („Gegner: …“)
und jeder Wechsel erscheint als Ereignis.

**Stufe 1, Lage lesen.** Alle halbe Sekunde entsteht ein Lagebericht: Wo
stehen die Phalangen des Spielers und wohin schauen sie, welche Gruppen
sind ungedeckt (Peltasten ohne Hopliten in der Nähe, abgesessene Reiter,
eine aufgelöste Formation), ist das Tor bewacht, wo setzt ein Turm an.
Daraus wählt jede Gruppe ihr Ziel: ungedeckte Gruppen sind lohnend, die
Front einer Phalanx nicht. Wer vor einer Front steht, läuft um sie herum
und greift die Flanke an. Im Handgemenge wird nicht mehr umgeplant.

**Stufe 2, Pläne.** Die Gegnerseite wählt aus benannten Plänen den mit
der höchsten Punktzahl und bewertet alle zwölf Sekunden neu, sofort bei
einem Durchbruch oder wenn eine Front auftaucht oder verschwindet:

| Plan | Wer | Wann |
|---|---|---|
| Frontal | Räuber, Horde | keine Front im Weg oder deutliche Übermacht |
| Umgehen (West/Ost) | Räuber, Horde | eine Phalanx sperrt; die Seite mit mehr Platz und weniger Gegnern |
| Zermürben | Räuber, Horde | eine Phalanx sperrt und die Räuber haben noch Speere: außerhalb des Nahkampfs stehen und werfen, dann stürmen |
| Binden und Umfassen | Räuber, Horde | eine Phalanx sperrt, mindestens zwei Gruppen und leichte Überlegenheit: ein Teil (etwa 70 % der Phalanxstärke, Fußvolk) stellt sich vor die Front und wartet, der Rest (Reiter zuerst) läuft um die Flanke; sobald jemand an der Flanke steht, greifen die Bindenden an, spätestens nach zwölf Sekunden |
| Umgehen und in den Rücken fallen | Räuber, Horde | wie Binden und Umfassen, aber die Umfassenden laufen ganz herum: neben die Flanke, hinter die Ecke, hinter die Mitte, und greifen von hinten an (dort trifft es am härtesten); nur wenn hinter der Phalanx mindestens zwei Kacheln Platz sind, bevorzugt mit Reitern, die den weiten Weg schnell gehen; die Bindenden greifen an, sobald jemand im Rücken steht |
| Tor rammen / Rammbock und Turm | Räuber vor der Palisade | Tor zu; mit Wehrgang-Peltasten oder bewachtem Tor zusätzlich ein Turm am Rand, fern vom Tor |
| Belagern | Räuber nach dem Durchbruch | eine Phalanx bewacht das Tor: außer Wurfweite warten, über den Turm einsickern, nach 40 s oder sobald die Wache weg ist stürmen |
| Stellung halten | Siedlung | Grundplan: Linie hält, dreht die Front zu Flankenangriffen, Hopliten decken das Wallstück, an dem ein Turm ansetzt, Wehrgang-Peltasten laufen zum Angriffspunkt, Peltasten am Boden plänkeln (siehe unten), Reiter greifen nur ungedeckte oder allein stehende Gruppen an, oder eine Phalanx, die von der eigenen Linie gebunden ist, und dann um die Front herum in Flanke oder Rücken |
| Vorrücken | Siedlung | Übermacht in der Nähe oder Beschuss durch Peltasten: die Linie rückt in Formation vor |

**Plänkeln der KI.** Eine Peltastengruppe der Gegnerseite mit Speeren,
die am Boden steht, plänkelt wie die des Spielers, sobald ein
erreichbarer Gegner näher als fünf Kacheln ist (und bleibt dabei, bis
er weiter als sechseinhalb weg ist): heran auf Wurfweite, werfen,
ausweichen, hinter oder neben der eigenen Phalanx werfen. Im Plan
„Binden und Umfassen“ binden Peltasten die Front mit Speeren statt im
Handgemenge. Räuberhaufen mischen nur ein Fünftel Peltasten unter, sie
bleiben daher Haufen und zermürben als Ganzes; reine Peltastengruppen
stellt die Siedlung. Ohne Speere stehen die Peltasten der Siedlung
still oder folgen der Linie, die Räuber-Peltasten gehen in den Nahkampf.

**Aufstellung der Siedlung.** Beim Angriff kopiert die Siedlung die
Mischung des Spielers nicht mehr. Sie ordnet seine Truppe ein
(ausgewogen, ohne Reiter, reiterlastig, peltastenlastig, ein Block) und
wählt aus eigenen Aufstellungen die, die im Simulator gegen diese Klasse
am besten abschnitt (`game/doctrine.py`): meist die schwere Phalanx,
gegen reiterlastige Angreifer den Hoplitenwall mit vielen Peltasten. Die
Truppe steht nach Waffengattung getrennt in Gruppen. Über Schlachten
hinweg merkt sich die Siedlung je Spielerklasse, wie jede Aufstellung
ausging, und wechselt, wenn eine andere besser war. Die Wahl steht zu
Beginn im Ereignisprotokoll („Die Siedlung stellt: …“).

**Stufe 3, Gedächtnis.** Nach jedem Plan wird festgehalten, wie sich
die Verluste beider Seiten während des Plans verhalten haben. Pläne, die
in früheren Schlachten Verluste gekostet haben, werden beim nächsten Mal
schwächer gewichtet (Faktor 0,5 bis 1,5, letzte fünf Schlachten). Am
Computer liegt das Gedächtnis in `~/.apoikia_ki.json`, im Browser hält es
nur die Sitzung. Innerhalb einer Schlacht weicht eine Gruppe zurück, deren
Angriff auf eine Phalanxfront zu viel kostet, sammelt sich zehn Sekunden
und meidet dieses Ziel danach.

Die Zahlen dazu stehen in `game/config.py` unter „Gegner-KI“. Die alte
feste Regelsteuerung bleibt als `ai="einfach"` erhalten, um beide im
Simulator zu vergleichen.

## Steuerung

Die Leiste unter der Karte zeigt immer nur, was gerade geht:

- **Am rechten Kartenrand eine Kachel je eigene Gruppe**, untereinander,
  mit Sinnbild der Gattung (Schild, Wurfspeer, Pferdekopf), Mannzahl und
  Moralbalken; im Kampf orange umrandet, auf der Flucht ausgegraut. Oben
  „Alle“ beziehungsweise „Keine“. Tippen wählt die Gruppe, nochmal tippen
  wählt ab; so bleibt auch bei vielen Gruppen Platz. Tippen auf die Gruppe
  im Feld geht weiterhin.
- **Unten nur die Befehle der gewählten Gruppen**, benannt nach dem,
  was passiert: Hopliten „Sturm“, „Phalanx bilden“ und die Formationen
  Linie, Kreis; Peltasten „Plänkeln“, „Halten“, Linie, Kreis; Reiter
  „Sturmangriff“, „Halten“, Linie, Keil. Die aktive Formation ist
  hervorgehoben, ein Tipp setzt sie direkt. Eine gemischte Auswahl zeigt
  nur „Angriff“ und „Halten“. Beim Angriff mit Wall kommen „Rammbock“
  und „Turm“ dazu, mit dem Zustand als zweiter Zeile (bauen, abbrechen,
  ablegen); der Rammbock verschwindet, sobald das Tor offen ist. Ohne
  Auswahl steht in der Leiste ein Hinweis, nach der Schlacht „Neu“ und
  „Aufstellung“.
- **Oben links „Menü“, oben rechts „Pause“** (bei Alarm „Los“, in der
  Pause „Weiter“). Das Menü klappt „Neu“ und „Aufstellung“ darunter auf
  und deckt sie sonst ab, damit auf dem Handy kein Fehlgriff die
  Schlacht neu startet; ein Tipp daneben schließt es wieder.

| Eingabe | Aktion |
|---------|--------|
| Tippen auf Gruppenkachel oder eigene Gruppe | auswählen (erneut tippen: abwählen) |
| Tippen auf die Karte | gewählte Gruppen laufen dorthin |
| Tippen auf Feind | gewählte Gruppen greifen diese an |
| Tippen auf das Tor | gewählte Gruppen mit Rammbock brechen es auf |
| Tippen auf den Wall | gewählte Gruppen mit Turm setzen ihn dort an |
| Ziehen auf der Karte | Front aufziehen: Länge = Breite, Richtung = Blickrichtung; bei Gruppen im Kreis: Anfang = Mitte, Länge = Halbmesser |
| Sturm / Plänkeln / Sturmangriff / A | gewählte Gruppen greifen frei an, je Waffengattung (siehe oben); gemischte Gruppen teilen sich dafür nach Gattung |
| Vereinen / V | mehrere gewählte Gruppen werden eine |
| Phalanx bilden / Halten / H | Hopliten bilden an Ort und Stelle eine Phalanx, andere bleiben stehen |
| Linie, Kreis, Keil / F | Formation der gewählten Gruppe setzen (F schaltet weiter) |
| Rammbock, Turm / B, T | gewählte Gruppen bauen das Gerät; erneut drücken: ablegen oder Bau abbrechen (nur beim Angriff mit Wall) |
| Alle / Keine | alle Gruppen wählen oder Auswahl aufheben |
| Pause / Leertaste | anhalten, bei Alarm: losgehen; in der Pause zeigt jede Gruppe, die noch unterwegs ist, ihr Ziel als Rechteck mit Front und Weg, sonst nur die gewählten |
| Menü, dann Neu / R (zweimal) | Szenario neu starten |
| Menü, dann Aufstellung / M | zurück ins Aufstellungsmenü |

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

**Simulator:** `tools/simulate.py` spielt Schlachten kopflos mit
gescripteten Spielertaktiken (Linie, Linie mit Flankenschutz, Tor
halten, Leiterfuß decken, Phalanxstoß, freier Angriff …) und mit verschiedenen
Truppenmischungen (`--army standard|ohne_reiter|gemischt|reiterlastig|zwei_phalangen`)
gegen beide KIs durch und gibt Siege, Verluste, Dauer und die gewählten
Pläne als Tabelle aus. `--lernen 8` spielt dieselbe Taktik achtmal mit
Gedächtnis. Ergebnisse und die daraus abgeleiteten Strategien stehen in
`docs/ki-simulation.md`.

```bash
python3 tools/simulate.py --seeds 8
python3 tools/simulate.py --scenario offen --tactic linie_aktiv --ai klug --army reiterlastig
python3 tools/simulate.py --lernen 8 --scenario offen --tactic linie
python3 tools/simulate.py --matrix --seeds 4        # Spieleraufstellung × Aufstellung der Siedlung
```

## Struktur

```
main.py             Einstiegspunkt
game/config.py      Karte, Balance, Farben
game/units.py       Truppentypen, Männer, Gruppe mit Reihen
game/army.py        Vorrat und Aufstellung (Gruppen, Reihen)
game/geometry.py    Vektoren, Front/Flanke/Rücken
game/scenarios.py   Karten und Aufstellungen
game/battle.py      Simulation: Befehle, Bewegung, Kampf, Moral, Plündern, Belagerung
game/ai.py          Gegner-KI: Lagebericht, Pläne, Gedächtnis (und alte Regelsteuerung)
game/render.py      Zeichnen von Karte, Gruppen, Leiste und Aufstellungsmenü
game/app.py         Asynchrone Schleife, Bildschirme, Auswahl, Touch und Tasten
tests/              pytest (headless)
tools/              Browser-Diagnose für CI, Simulator für Taktiken gegen die KI
docs/               Simulationsergebnisse
```
