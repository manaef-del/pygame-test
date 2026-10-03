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
  Speer fliegt sichtbar vom werfenden Mann dorthin, wo sein Ziel sein
  wird, wenn er ankommt (der Werfer hält vor, aus Laufrichtung und
  Tempo), und streut dabei: mehr auf Entfernung, und je mehr er
  vorhalten muss, desto mehr. Getroffen wird, wer an der Einschlagstelle
  steht. Auf Stehende geht etwa jeder achte Speer daneben, auf eine
  marschierende Phalanx jeder dritte, auf Reiter im Galopp jeder zweite;
  wer abrupt wendet oder stehen bleibt, entgeht manchem Wurf. Die
  Wehrtürme zielen ebenso. Sind die Speere verschossen, geht die Gruppe in
  den Nahkampf über. Das gilt für beide Seiten: auch die Peltasten der
  Räuber tragen zehn Speere und stürmen, sobald sie leer sind.
- **Es kämpft, wer den Gegner erreicht.** Von der vorderen Reihe kämpfen
  nur die Männer, die einen Feind in Speerweite haben (von Mann zu Mann
  gemessen), dazu die Speere der zweiten Reihe dahinter; an Flanke und
  Rücken dreht sich um, wer den Gegner erreicht, gleich in welcher Reihe
  er steht. Die Verluste fallen dort, wo der Gegner steht. Berührt ein
  schmaler Haufen nur das Ende einer langen Linie, kämpft dort auch nur
  das Ende; wer sich um den Gegner legt oder die Flügel einklappt,
  bringt entsprechend mehr Männer in den Kampf, und eine lange Linie in
  einem Glied wird an den Enden aufgerollt. Eine zweite Gruppe, die
  denselben Gegner anfällt, stellt sich nicht in die erste hinein,
  sondern daneben an das nächste freie Stück seines Umrisses. Erreicht
  niemand den Gegner, halten die zwei nächsten Männer den Kontakt.
- **Schild an Schild.** Der Kampf beginnt auf Speerweite (gut eine halbe
  Kachel Lücke zwischen den Formationen), angreifende Gruppen schließen
  aber weiter auf, bis nur noch ein Spalt bleibt und ihre vordere Reihe
  wirklich Feinde erreicht (auch dort, wo die hintere Reihe des Gegners
  kurz ist). Wer im Handgemenge
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
- **Marsch im Bogen.** Auf längeren Wegen (über drei Kacheln) über freies
  Feld läuft eine Gruppe zu Fuß in ihrer Blickrichtung an und schwenkt
  unterwegs zum Ziel, die Front immer in Marschrichtung. Eine breite Linie
  schwenkt langsamer und zieht einen weiteren Bogen als ein kleiner Block.
  Liegt das Ziel weit seitlich, marschiert sie langsamer und schwenkt
  enger; liegt es hinter ihr, macht sie kehrt. Eine aufgezogene Linie
  behält unterwegs ihre bisherige Breite und marschiert erst anderthalb
  Kacheln vor dem Ziel in die neue Breite und Front auf. Reiter traben
  ebenso im Bogen an, statt erst auf der Stelle zu wenden, und reiten mit der
  Front voraus; im Galopp behalten sie ihren Schwung und weiten Bogen. Steht
  eine ruhende eigene Gruppe nur am Rand des Weges, geht eine Gruppe als
  Block im Bogen an ihr vorbei; steht sie quer davor, löst sich die Gruppe
  auf und geht Mann für Mann vorbei. Ebenso zwischen Häusern: Passt der Block nicht durch eine Gasse,
  geht er außen herum oder Mann für Mann hindurch. Entschieden wird nach der
  Zeit, einmal je Ziel: als Block der Weg mit seinem Tempo, aufgelöst der
  kürzeste Weg einzelner Männer, dazu 0,6 s zum Neuformieren und in engen
  Gassen 0,02 s je Mann zum Anstehen. Aufgelöst wird nur, wenn das
  mindestens eine halbe Sekunde schneller ist; sonst hält die Gruppe ihre
  Ordnung. Reiter traben
  durch enge Wendungen, statt im Galopp eine Schleife zu ziehen: Sie nehmen
  das höchste Tempo, mit dem der Bogen zum nächsten Wegpunkt noch passt.
  Kurze Wege, Angriffe, Flucht und Umwege um Wall und Tor gehen wie zuvor:
  erst schwenken, dann geradeaus.
- **Umwege ohne Hin und Her.** Wer um eine eigene Gruppe herumgeht, gilt
  erst mit einer Viertelkachel mehr Abstand als vorbei, und der Umwegpunkt
  liegt noch eine Viertelkachel weiter außen. Die gewählte Seite bleibt
  1,5 s gemerkt, damit die nächste Gruppe auf derselben Seite umgangen
  wird. Warten zwei eigene Gruppen aufeinander (eine weicht zurück, die
  andere will hinein), lässt die angreifende die zurückweichende vorbei.
  Gegen einen Kreis sucht die KI keine Flanke, die es nicht gibt, sondern
  greift an.
- **Hauptmann und Kontermarsch.** Jede Gruppe hat einen Hauptmann (weißer
  Ring) auf dem mittleren Platz der mittleren Reihe; an ihm richtet sich die
  Gruppe beim Marsch aus. Fällt er, übernimmt der Mann, der dem Platz am
  nächsten steht, ohne weitere Boni (anders als der Anführer). Liegt ein Ziel
  hinter Hopliten, machen sie einen Kontermarsch: Die Front wechselt die
  Seite, aber dieselben Männer bleiben vorn, jede Rotte zieht durch sich
  selbst hindurch. Das dauert 0,6 s und 0,3 s je weiterer Reihe; solange
  steht die Gruppe ungeordnet. Im Handgemenge, und bei Peltasten, Reitern und
  Räuberhaufen ohne feste Reihen, wird wie bisher sofort kehrtgemacht.
- **Das Rechteck sagt, wo jeder stehen soll; den Weg sucht jeder selbst.**
  Auf freiem Feld marschiert eine Gruppe als Block. Muss sie über den
  Wall, durchs offene Tor oder an einer ruhenden eigenen Gruppe vorbei,
  löst sie sich auf (ohne Rechteck gezeichnet): Die Zielaufstellung steht
  dann fest, Mitte und Front, und jeder Mann sucht sich seinen eigenen Weg
  zu seinem Platz darin, über ein Wegefeld um Palisade und stehende eigene
  Gruppen herum, über Turm und Leiter (dort stellt man sich an). Die Männer
  gehen im Tempo der Gruppe, wer zurückliegt, holt auf. Die Gruppe ist
  währenddessen dort, wo ihre Männer sind; sie schließt sich wieder, sobald
  die Männer angekommen sind oder geschlossen weitergehen, und zwar dort,
  wo sie stehen: Wer seinen Platz erreicht hat, verlässt ihn nicht noch
  einmal. Über den Wall zeigt die Front danach vom Wall weg, sonst wie
  befohlen oder in Marschrichtung. Angriffe bleiben Block, ebenso, wer
  durch ein Tor muss, an dem gekämpft wird. Halten oder „Verband bilden“
  schließt eine aufgelöste Gruppe sofort dort, wo ihre Männer stehen.
  Hopliten im Modus Phalanx lösen sich nur noch über den
  Wall auf (siehe „Modi der Hopliten“).
- **Sammelplatz hinter dem Wall.** Wer über den Wall steigt und weiter will,
  sammelt sich drüben zuerst: am Fuß der Leiter, über die die Männer
  hinabsteigen, mit etwas Abstand zum Wall und der Front zum Ziel. Jede
  Gruppe bekommt einen eigenen Platz neben den schon belegten. Sind alle
  drüben und angekommen (höchstens acht Sekunden Warten auf Nachzügler),
  schließt sich die Gruppe dort zum Block und marschiert geschlossen weiter.
  Liegt das Ziel gleich hinter dem Wall, ist es selbst der Sammelplatz;
  Fliehende sammeln sich nicht. Wer über den Wall kommt, bleibt drüben an
  Feinden hängen, statt um sie herumzugehen. Am Wall wird Mann gegen Mann
  gekämpft: Wer oben steht, schlägt mit verminderter Wucht hinab; wer auf
  der Leiter steht, ist auch von unten zu treffen; wer oben auf dem
  Wehrgang steht, nicht.
  Die Gegner gehen genauso: Mann für Mann über den Wall, durchs offene Tor
  und an ihren eigenen ruhenden Haufen vorbei. Steht dabei ein Feind näher
  als zweieinhalb Kacheln, halten sie die Ordnung und gehen als Block herum
  (abschaltbar mit `LOOSE_AI` in `game/config.py`).
- **Wehrgang.** In der Festung stehen die Männer oben in vier Rotten quer zum
  Wehrgang, mit dem Abstand einer Formation (bis zu 20 Mann je Kachel), und
  jede Fußgruppe der Verteidiger darf über die Leitern hinauf, nicht nur
  Peltasten. Der Wehrgang ist ein enger Gang: In eine Kachel, auf der ein
  Feind steht, kommt niemand hinein, man muss ihn erst werfen. So wird der
  Ausstieg eines Belagerungsturms zum Brückenkopf; die Besatzung schickt ihre
  Reserve hinauf an den Ausstieg, sobald ein Turm am Wall steht. Wer oben an
  eine andere Stelle will, geht oben entlang oder über eine Leiter hinab,
  quer durch den Hof und eine andere hinauf, je nachdem, was schneller ist;
  jedes Klettern kostet die Zeit, bis alle Männer an der Leiter vorbei sind
  (drei je Sekunde).
- **Niemand steht im anderen.** Kein Mann teilt seinen Platz mit einem
  anderen, auch nicht mit einem Fliehenden oder einem Feind: Zwischen
  Männern verschiedener Gruppen bleiben immer zwei Halbmesser, in der
  eigenen Gruppe rückt man höchstens Schulter an Schulter. Wer jemanden
  im Weg hat, geht schräg an ihm vorbei; nur stürmende Reiter drängen
  Fußvolk beiseite, solange ihr Schwung sie in den Feind trägt.
- **Häuser und Gerät sind Hindernisse.** Niemand läuft durch ein Haus,
  durch einen aufgestellten Belagerungsturm (außer wer über ihn auf den
  Wall will) oder durch einen liegenden Rammbock. Eine Gruppe sucht sich
  ihren Weg mit so viel Abstand, wie ihre Front breit ist: durch Gassen,
  in die sie passt, sonst außen herum. Gemessen wird von den Hauswänden
  aus (auf einem Raster aus Kachelmitten und -grenzen), eine Gasse von
  einer Kachel bietet in der Mitte also eine halbe Kachel Platz zu jeder
  Seite. Eine Phalanx wird darin schmaler (etwa sechs Mann Front) und
  marschiert als Kolonne hindurch; lockere Gruppen gehen Mann für Mann. Geplündert wird
  von außen, wer am Haus steht. Die Häuser stehen in Blöcken mit einer
  breiten Gasse zur Agora; ein aufgebrochener Rammbock bleibt hinter der
  Gruppe liegen, nicht im Tordurchgang.
- **Gruppen umgehen einander, niemand wird geschoben.** Steht eine
  ruhende eigene Gruppe auf dem Weg (still oder als Phalanx auf ihrem
  Posten), gehen die Männer der befohlenen Gruppe links und rechts eng an
  ihr vorbei (gut eine Handbreit Abstand zu ihrem Rechteck) und stellen
  sich dahinter wieder auf; die Stehende bleibt, wo sie ist. Ein Angriff
  geht als Block außen um sie herum. Wird
  eine Gruppe genau dorthin befohlen, wo schon eine eigene steht, hält
  sie davor. Gruppen, die beide unterwegs sind, weichen sich Mann für
  Mann aus. Leichte Truppen (Peltasten) stehen in lockerer Ordnung:
  Durch sie geht man hindurch, statt außen herum, etwa wenn die Phalanx
  durch die eigene Peltastenlinie nach vorn rückt; leichte Truppen
  dürfen auch dicht hinter eine ruhende eigene Formation, um über sie
  hinweg zu werfen. An Feinden bleibt man hängen und kämpft. Streift ein
  befohlener Block auf dem Weg zu seinem Platz nur die Ecke einer ruhenden
  eigenen Gruppe (etwa beim Schwenk in eine Lücke neben ihr), gleitet er
  schräg daran vorbei, statt zu warten.
- **Anstehen statt Stapeln.** In eine eigene Gruppe, die steht oder
  gerade kämpft, fährt keine andere hinein: Wer nicht um sie herumkommt
  (etwa im Tor), wartet im Block dahinter, bis vorn Platz wird; wer am Umriss des
  Feindes kein freies Stück mehr findet, wartet ebenfalls geordnet dahinter.
  Wer außen herum geht, bleibt bei der einmal gewählten Seite, bis er
  vorbei ist; ein Angriff nimmt die Seite, auf der am Feind noch Platz ist. So
  bilden sich Schlangen vor einer Enge statt eines Haufens. Der Kreis
  zählt für alle Abstände als Kreis, nicht als sein umschriebenes
  Rechteck.
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
  wie man hinter ihr steht. Ohne Auswahl (oder mit „Alle“) gilt die Linie
  für alle Gruppen.
- **Schlachtordnung:** Bekommen Gruppen verschiedener Gattungen dieselbe
  Linie, stehen die Hopliten vorn auf der Linie, die Peltasten dicht
  dahinter (etwas kürzer, damit die Enden der Phalanx frei bleiben; sie
  werfen über die Köpfe) und die Reiter an den Flügeln, zuerst rechts an
  der schildlosen Seite, mit der Front auf gleicher Höhe. Wäre rechts kein
  Platz mehr auf der Karte, gehen sie nach links. Ohne Hopliten stehen die
  Peltasten vorn. Gruppen einer Gattung teilen sich die Linie
  nebeneinander. Die Vorschau beim Ziehen zeigt jeden Block dort, wo er
  stehen wird.
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
- **Schildseite:** Der Hoplitenschild sitzt am linken Arm. Eine Gruppe
  aus Hopliten ist an der linken Flanke gedeckt (im Nahkampf 0,8-facher
  Schaden, Speere 0,6-fach) und an der rechten, der Speerseite, offen
  (1,25-fach, Speere 1,15-fach). Links und rechts gelten so, wie die
  Gruppe schaut. Reiter und die KI suchen lieber die rechte Seite.
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
- **Modi der Hopliten.** Hopliten haben einen Modus, der gilt, bis man
  ihn wechselt; die Leiste zeigt „Locker“, „Phalanx“ und „Sturm“
  (Tasten L, P, A).
  - *Locker*: weite Abstände (1,7-fach in der Reihe), 15 % schneller,
    ohne Phalanxbonus; Wurfspeere gehen öfter zwischen den Männern ins
    Leere, und wer getroffen wird, deckt sich mit dem Schild. An Tor, Gasse und
    eigenen Gruppen löst sich die Gruppe auf und geht Mann für Mann.
  - *Phalanx* (Standard): wie gewohnt im Kampf. Auf dem Marsch bleibt sie
    zusammen: Um eigene Gruppen geht sie als Block herum, vor Tor und
    Gasse wird sie schmaler und tiefer, bis die Front hindurchpasst, und
    marschiert dahinter wieder in voller Breite auf. Passt nicht einmal
    eine Front von zwei Mann, geht sie doch Mann für Mann.
  - *Sturm*: der freie Angriff (siehe „Angriff“).
  Wer steht, bildet mit Phalanx an Ort und Stelle die Formation; wer
  unterwegs ist, marschiert im neuen Modus weiter. (Ein dritter Modus,
  „Geschlossen“, war zu nah an der Phalanx und ist wieder entfallen.)
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
  doppelt so hart. Reine Peltasten: nur die Linie (ohne Schildwand hilft
  ihnen der Kreis nicht). Wer eine neue Linie zieht, steht wieder in Linie.
- **Verbände.** Jede Gruppe hat nur eine Gattung. Mehrere Gruppen bilden
  einen Verband: rechts lange auf weitere Kacheln drücken (die Gruppe kommt
  zur Auswahl dazu), dann „Verband bilden“ (V). Die Gruppen stellen sich
  gleich in Schlachtordnung auf, Hopliten vorn, die Reiter an den Flügeln
  (die größte rechts), die Peltasten dahinter. Eine Gruppe mit mehreren
  Gattungen aus der Aufstellung wird in der Schlacht je Gattung eine
  Gruppe, zusammen ein Verband.
  - Die Kacheln eines Verbands stehen beisammen, ein Rahmen mit Kopfzeile
    („V1“) umschließt sie. Die Kopfzeile wählt den ganzen Verband, eine
    Kachel nur diese Gruppe.
  - Ist der Verband gewählt, bewegt Tippen auf die Karte ihn dorthin (die
    vordere Reihe mit ihrer Mitte an den Punkt, die Front in
    Marschrichtung), Ziehen legt die vordere Reihe auf die Linie. Alle
    gehen im Tempo der langsamsten Gruppe, die Reiter reiten nicht voraus.
  - „Anordnen“ öffnet eine Tafel über der Leiste: je Reihe eine Zeile,
    oben vorn, darin die Sinnbilder der Gruppen von links nach rechts (wie
    die Front schaut). Mit dem Finger verschiebt man sie: neben ein anderes
    Sinnbild, in eine andere Zeile oder in die leere Zeile unten, dann wird
    es eine neue Reihe hinten. Der Verband stellt sich sofort neu auf.
    „Fertig“ schließt die Tafel.
  - In einer Reihe stehen die Gruppen nebeneinander, die Fronten bündig:
    Reiter drei Glieder tief, die anderen teilen sich die Länge nach
    Mannzahl. Jede weitere Reihe steht dicht hinter der vorigen, auf drei
    Vierteln ihrer Länge.
  - „Kreis“ stellt die Reihen als Ringe ineinander, die vordere außen. Beim
    Aufziehen treten die Männer der Ringe aneinander vorbei.
  - Jede Gruppe behält ihren Modus und nimmt Befehle einzeln an, sie bleibt
    dabei im Verband; der nächste Befehl an den Verband stellt sie wieder
    an ihren Platz. Wer aus dem Verband heraus frei angreift (Sturm,
    Plänkeln, Sturmangriff), kehrt an seinen Platz zurück, sobald nach dem
    Handgemenge kein kämpfender Feind mehr in drei Kacheln Nähe ist.
  - „Aus Verband“ nimmt eine gewählte Gruppe heraus, „Auflösen“ beendet den
    Verband. Mit weniger als zwei Gruppen ist er keiner mehr.
- **Wenden im Stand:** Bekommt eine stehende Gruppe ein Ziel in einer
  anderen Richtung, springt ihre Front nicht mehr um. Sie schwenkt, die
  Männer drehen auf ihren Plätzen mit, und erst wenn die Richtung grob
  stimmt (45 Grad), geht es los. Wie schnell, hängt an der Breite: Der
  äußere Mann geht den Bogen mit vier Fünfteln seines Tempos, höchstens
  aber eine halbe Umdrehung je Sekunde. Ein Trupp von acht Mann steht so
  nach einer halben Sekunde quer, eine Phalanx von 40 schweren Hopliten
  in 14er-Front braucht dafür knapp zwei Sekunden. Reiter wenden auf der
  Stelle höchstens eine Viertelumdrehung je Sekunde. Liegt das Ziel hinter der Gruppe, macht sie kehrt: Die hintere
  Reihe wird die vordere, links wird rechts, und jeder Mann bleibt fast
  auf seinem Platz. Das gilt für Reiter und Fußvolk, für Spieler und
  Gegner gleichermaßen; nur Fliehende und Kletternde wenden ohne
  Zeremonie. Auch eine befohlene Front (gezogene Linie, Rammbock am
  Tor, die Siedlung dreht ihre Linie zum Angreifer) wird mit derselben
  Drehrate eingeschwenkt, eine Phalanx tauscht dabei aber keine Reihen:
  Ihre schweren Männer bleiben vorn, sie schwenkt den vollen Winkel.
- **Schwung der Reiter:** Berittene fahren an (in gut einer Sekunde auf
  vollen Galopp), bremsen vor dem Ziel ab und wenden im Galopp in Bögen,
  deren Halbmesser mit dem Tempo wächst; im Stand wenden sie eine
  Viertelumdrehung je Sekunde. Ohne
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
- **Handgemenge bindet:** Jeder Mann, der einen feindlichen Mann in
  Armreichweite hat (orangener Ring), steht fest, auch wenn seine Gruppe einen neuen Befehl
  bekommt; die anderen formieren sich um ihn herum. Eine vorn gebundene
  Phalanx lässt sich also nicht zur Flanke drehen, und ihr Bonus kehrt
  erst zurück, wenn alle Männer wieder auf ihren Plätzen stehen. Eine
  Gruppe im Nahkampf kommt nur mit einem Drittel ihrer Geschwindigkeit
  vom Fleck. Zieht sie sich mehr als gut eine Kachel zurück, reißen sich
  die Gebundenen los, und die Gruppe gilt vier Sekunden lang als von
  hinten angegriffen (anderthalbfacher Schaden, kein Formationsbonus).
  Lösen ist eine Entscheidung mit Preis, auch für die Räuber, die nach
  einem gescheiterten Angriff zurückweichen. Weicht sein Gegner weiter
  als eine Kachel von der Stelle, an der er gebunden wurde, ist er frei.
- **Gerangel (nur im Bild):** Im Handgemenge treten die Männer sichtbar
  an ihren Gegner heran; wer in einer kämpfenden Gruppe keinen hat,
  drängt auf einen freien feindlichen Mann in der Nähe (höchstens zwei
  auf einen, höchstens eine Kachel von seiner Stelle). Die Phalanx hält
  ihre Reihen. Ein spürbarer Treffer blitzt kurz hell auf, und wo einer
  fällt, bleibt für einen Moment ein dunkler Fleck. Gerechnet wird
  weiter von den Stellen der Männer: Das Gerangel ändert nichts am
  Ausgang.
- **Moral, je Gruppe, für beide Seiten:** Verluste drücken die Moral, aus
  Flanke und Rücken stärker, von vorn in der Phalanx schwächer; unter der
  Schwelle flieht die Gruppe. Eine Gruppe aus mittleren Hopliten bricht
  etwa nach einem Drittel Verlusten aus der Flanke, schwere später,
  Peltasten früher. Flieht eine Nachbargruppe, wankt die eigene mit. Ist
  die Schlacht aussichtslos (eigene Seite unter 40 %, der Gegner noch
  über 60 %), sinkt die Moral aller Gruppen dieser Seite von selbst.
  Die Moral der gewählten Gruppe steht in der Statuszeile.
- **Der Anführer** kämpft in der Gruppe mit, die man ihm in der
  Aufstellung zuteilt („Anführer zu dieser Gruppe holen“; Vorgabe: die
  Hopliten). Er kommt zum Vorrat hinzu, steht vorn, hat die Gattung der
  vordersten Reihe und trifft wie jeder andere, hält aber fünfmal so viel
  aus (goldener Ring im Feld, goldener Punkt auf der Gruppenkachel).
  Solange er lebt, nimmt seine Gruppe 15 % weniger Schaden, und ihre
  Fluchtschwelle liegt um 0,1 tiefer: sie flieht später. Fällt er, steht
  es in der Meldezeile, und seine Gruppe ist wieder eine wie jede andere.
  Greift man eine Siedlung an, hat sie ihren eigenen Anführer bei ihrer
  ersten Hoplitengruppe; die Räuber haben keinen.
- **Sammeln nach der Flucht.** Wer eine Siedlung verteidigt, flieht nie
  vom Feld, sondern auf die **Agora**, den gepflasterten Platz hinter den
  Häusern (beim Angriff auf eine Siedlung liegt ihre Agora zwischen
  ihren Häuserreihen). Naht dort kein Feind, steigt die Moral, und die
  Gruppe nimmt wieder Befehle an. Setzt der Feind ihr dort nach, kehrt
  sie um und kämpft bis zum letzten Mann; auf der Agora flieht niemand
  mehr. Steht er nur in der Nähe, wartet sie, statt sich zu sammeln. Angreifer (der Spieler beim Angriff, die Räuber bei der
  Verteidigung) fliehen an ihren eigenen Kartenrand und sammeln sich
  dort ebenso, außer die Schlacht ist für sie aussichtslos oder der
  Feind setzt ihnen bis an den Rand nach: dann verlassen sie das Feld. Eine Schlacht ist erst entschieden, wenn eine
  Seite niemanden mehr hat, der kämpft oder sich noch sammeln kann.
- **Räuber** ziehen zu den Häusern und plündern, wenn niemand sie stört.
  Bleiben von ihnen weniger als drei Zehntel übrig (gezählt wird, wer
  kämpft oder sich noch sammeln kann), geben sie auf und ziehen ab. Eine
  angegriffene Siedlung zieht nie ab.
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
| Verteidigung: Festung | Große Karte (viermal so groß). Ein Heer aus Hopliten, Peltasten und Reitern, doppelt so stark wie die eigene Truppe, belagert die sechseckige Festung |
| Angriff: Festung | Dieselbe Festung, man selbst belagert sie; die Besatzung ist etwa halb so stark wie die eigene Truppe |

**Festung:** In der Mitte der großen Karte liegt die Agora, um sie
dreißig Häuser in Blöcken; von jedem Tor führt eine breite Gasse zur
Agora, um die Agora läuft ein freier Ring, innen am Wall ein schmaler
Streifen, und vor jeder Leiter bleibt Platz zum Ankommen und Sammeln.
Darum ein sechseckiger Wall, außen genug Platz, um ihn zu umlaufen. In der Nordkante und in den beiden südlichen Schrägen sitzt je
ein verschlossenes Tor, an jeder Ecke ein Wehrturm, innen an jeder Kante
zwei Leitern. Die **Wehrtürme** werfen zwei Speere in der Sekunde, ohne
Vorrat, auf den nächsten Feind in 6,5 Kacheln (sie reichen bis vor die
Tore). Wer oben steht, dem gehört der Turm: Steht nur der Feind oben,
wirft er für den Feind; stehen beide oben, schweigt er. Die Wege führen
um die Ecken des Sechsecks herum und durch das Tor, das am wenigsten
Umweg macht; auf dem Wehrgang geht es den Wall entlang, auch an den
Schrägen und über die Türme. Beritten klettert niemand, Reiter kommen
nur durch ein offenes Tor hinein. Das **Heer** rammt zwei Tore zugleich
und setzt einen Turm an eine dritte Stelle, damit sich der Verteidiger
teilen muss; die Peltasten werfen auf den Wehrgang über dem Tor. Steht
hinter einem aufgebrochenen Tor eine Phalanx, läuft es nicht einzeln
hinein, sondern sammelt sich davor, bis eine zweite Bresche offen ist
oder 20 Sekunden um sind; dann stürmen alle zugleich. Die **Besatzung**
stellt hinter jedes Tor eine Phalanx (die dem Angreifer nächsten
zuerst), schickt eine Phalanx, vor deren Tor niemand steht, an die
bedrohte Stelle, schickt die Peltasten auf den Wehrgang dorthin, wo der
Angriff ansetzt, und hält die Reiter auf der Agora für Eingedrungene.

**Wehrgang:** Eine reine Peltastengruppe der Wallseite darf auf die
Palisade, aber nur über die Leitern hinauf und hinunter (helle Sprossen
auf der Palisade). Oben läuft sie entlang, auch über das Torhaus. Über
die Palisade wirft nur, wer oben steht, dafür eine Kachel weiter.
Der Wehrgang ist erhöht: Wer unten steht, kommt an die Männer oben nicht
heran und ist mit ihnen auch nicht im Handgemenge; von oben schlägt man
hinunter, mit einem Drittel der Wirkung. Nach oben helfen nur Speere,
Leitern oder ein Turm. Gegen Speere von außen deckt die Palisade die
Männer auf dem Wehrgang: Sie nehmen davon nur knapp ein Drittel des
Schadens. Wer von innen (der Seite der Häuser) oder vom Wall selbst
wirft, trifft sie voll.

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

**Gegenmittel der KI.**
- **Reserve:** Hat die Gegnerseite mindestens drei Gruppen, hält sie die
  hinterste zurück. Bei den Räubern folgt sie der Hauptmacht dreieinhalb
  Kacheln dahinter, die Horde und die Siedlung lassen sie stehen, wo sie
  ist. Sie kommt, wenn:
  - ein Feind ihr nahe kommt,
  - ein ungedeckter oder fliehender Gegner in Reichweite ist,
  - beim Umfassen jemand an der Flanke steht,
  - 30 % der eigenen Leute gefallen sind,
  - kaum noch andere kämpfen,
  - oder spätestens nach 35 Sekunden.

  Das Protokoll meldet, warum sie kommt. Die Festungsbesatzung hat schon
  eine eigene Reserve: Phalanxen an ruhigen Toren gehen an bedrohte
  Stellen.
- **Gegen Reiter:** Reiten Reiter auf eine Hoplitengruppe der KI zu, und
  nicht auf ihre Front, dreht eine Phalanx die Front zu ihnen, und die
  Reiter rennen in die Speere. Steht vorn feindliches Fußvolk, bleibt die
  Front, wo sie ist.
- **Kreis als Verzweiflungstat:** Den Kreis bildet eine Hoplitengruppe der
  KI nur, wenn sie klar in Unterzahl und umzingelt ist, gleich gegen welche
  Gattung. Unterzahl heißt: Im Umkreis von drei Kacheln stehen
  anderthalbmal so viele Feinde wie eigene Leute, Nachbarn zählen mit.
  Umzingelt heißt: Feinde auf drei Seiten, oder vorn und hinten zugleich.
  Ist das zwei Sekunden lang vorbei, kehrt sie in die Linie zurück. Räuber
  haben weder Schild noch Speer, ein Kreis hilft ihnen nicht.
- **Peltasten an die schildlose Seite:** Plänkelnde Peltasten der KI
  gehen gegen eine Hoplitenphalanx erst im Wurfabstand an ihr entlang
  an die rechte Flanke und werfen von dort (Speere 1,15-fach statt
  0,6-fach von links).

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

Im laufenden Spiel sieht man nur die Männer; gewählte Gruppen tragen
einen Ring um jeden Mann, eine geschlossene Phalanx den goldenen
Schildstrich vor ihrer Front. Die Formationsrechtecke und die Ziele
erscheinen in der Pause und beim Aufziehen einer Front.

Die Leiste unter der Karte zeigt immer nur, was gerade geht:

- **Am rechten Kartenrand eine Kachel je eigene Gruppe**, untereinander,
  mit Sinnbild der Gattung (Schild, Wurfspeer, Pferdekopf), Mannzahl und
  Moralbalken; im Kampf orange umrandet, auf der Flucht ausgegraut. Oben
  „Alle“ beziehungsweise „Keine“. Tippen wählt die Gruppe, nochmal tippen
  wählt ab; langes Drücken nimmt sie zur Auswahl dazu. Die Gruppen eines
  Verbands stehen beisammen im Rahmen, die Kopfzeile wählt den Verband.
  Tippen auf die Gruppe im Feld geht weiterhin.
- **Unten nur die Befehle der gewählten Gruppen**, benannt nach dem,
  was passiert: Hopliten „Locker“, „Phalanx“, „Sturm“ und
  die Formationen Linie, Kreis; Peltasten „Plänkeln“, „Halten“; Reiter
  „Sturmangriff“, „Halten“, Linie, Keil. Der aktive Modus und die aktive
  Formation sind hervorgehoben, ein Tipp setzt sie direkt. Mehrere
  gewählte Gruppen: „Angriff“, „Halten“ und „Verband bilden“; ein
  gewählter Verband: „Angriff“, „Halten“, Linie, Kreis, „Anordnen“ und
  „Auflösen“; eine Gruppe im Verband zusätzlich „Aus Verband“. Beim Angriff mit Wall kommen „Rammbock“
  und „Turm“ dazu, mit dem Zustand als zweiter Zeile (bauen, abbrechen,
  ablegen); der Rammbock verschwindet, sobald das Tor offen ist. Ohne
  Auswahl steht in der Leiste ein Hinweis, nach der Schlacht „Neu“ und
  „Aufstellung“.
- **Oben links „Menü“, oben rechts „Pause“** (bei Alarm „Los“, in der
  Pause „Weiter“). Das Menü klappt „Neu“ und „Aufstellung“ darunter auf
  und deckt sie sonst ab, damit auf dem Handy kein Fehlgriff die
  Schlacht neu startet; ein Tipp daneben schließt es wieder.
- **Große Karte (Festung):** Sie beginnt in der Übersicht, die ganze
  Karte halb so groß. Ein Tipp auf die Karte zoomt in die Nahansicht
  (Maßstab wie auf den kleinen Karten), mit der Stelle in der Mitte; dort
  verschieben **zwei Finger** die Ansicht. Der Knopf unter „Menü“
  schaltet zwischen „Karte“ (Übersicht) und „Nah“ um. In der Übersicht
  wählt man Gruppen über die Kacheln rechts; Fronten aufziehen geht in
  beiden Ansichten.

| Eingabe | Aktion |
|---------|--------|
| Tippen auf Gruppenkachel oder eigene Gruppe | auswählen (erneut tippen: abwählen) |
| Lange auf eine Gruppenkachel drücken | Gruppe zur Auswahl dazunehmen (oder herausnehmen) |
| Tippen auf die Kopfzeile eines Verbands | den ganzen Verband wählen |
| Tippen auf die Karte | gewählte Gruppen laufen dorthin (ein Verband in seiner Ordnung) |
| Tippen auf Feind | gewählte Gruppen greifen diese an |
| Tippen auf das Tor | gewählte Gruppen mit Rammbock brechen es auf (in der Festung das angetippte Tor) |
| Tippen auf den Wall | gewählte Gruppen mit Turm setzen ihn dort an |
| Ziehen auf der Karte | Front aufziehen: Länge = Breite, Richtung = Blickrichtung; bei Gruppen im Kreis: Anfang = Mitte, Länge = Halbmesser |
| Sturm / Plänkeln / Sturmangriff / A | gewählte Gruppen greifen frei an, je Waffengattung (siehe oben) |
| Locker, Phalanx / L, P | Modus der gewählten Hopliten |
| Halten / H | Hopliten bilden an Ort und Stelle eine Phalanx, andere bleiben stehen |
| Verband bilden / V | mehrere gewählte Gruppen werden ein Verband |
| Anordnen | Tafel: Gruppen des Verbands mit dem Finger in Reihen ordnen |
| Auflösen, Aus Verband | Verband beenden, eine Gruppe herausnehmen |
| Linie, Kreis, Keil / F | Formation der gewählten Gruppe setzen (F schaltet weiter) |
| Rammbock, Turm / B, T | gewählte Gruppen bauen das Gerät; erneut drücken: ablegen oder Bau abbrechen (nur beim Angriff mit Wall) |
| Alle / Keine | alle Gruppen wählen oder Auswahl aufheben |
| Pause / Leertaste | anhalten, bei Alarm: losgehen; erst in der Pause erscheinen die Formationsrechtecke, und jede Gruppe, die noch unterwegs ist, zeigt ihr Ziel als Rechteck mit Front und Weg |
| Menü, dann Neu / R (zweimal) | Szenario neu starten |
| Menü, dann Aufstellung / M | zurück ins Aufstellungsmenü |
| Karte / Nah, Z | große Karte: zwischen Übersicht und Nahansicht umschalten |
| Tippen in der Übersicht | große Karte: dorthin zoomen |
| Zwei Finger ziehen (am Rechner: rechte Maustaste, Pfeiltasten) | große Karte: Nahansicht verschieben |

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
game/pathing.py     Wegefeld: jeder Mann sucht seinen Weg zu seinem Platz
game/ai.py          Gegner-KI: Lagebericht, Pläne, Gedächtnis (und alte Regelsteuerung)
game/fortress_ai.py KI der Festung: Belagerung durch das Heer, Verteidigung durch die Besatzung
game/render.py      Zeichnen von Karte, Gruppen, Leiste und Aufstellungsmenü; Kamera (Übersicht, Nahansicht)
game/app.py         Asynchrone Schleife, Bildschirme, Auswahl, Touch und Tasten
tests/              pytest (headless)
tools/              Browser-Diagnose für CI, Simulator für Taktiken gegen die KI
docs/               Simulationsergebnisse
```
