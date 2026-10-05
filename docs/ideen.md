# Offene Ideen

Was große Schlachtenspiele anders machen und wo es sich bei uns noch
lohnt nachzujustieren, nach Wirkung je Aufwand geordnet. Erledigtes
wandert nach unten.

## Offen

0. **Angriff auf die Siedlung.** Der letzte Kampf auf der Agora bleibt
   bewusst stark: Die einfachen Taktiken der Simulation verlieren immer, mit
   Plan (Phalanx bindet, Reiter in den Rücken, nach der Flucht neu ansetzen)
   gewinnt man vier von sechs, braucht aber oft länger als 300 Sekunden
   (Lauf 34). Offen: Soll das so lang dauern, oder hilft dem Spieler ein
   Hinweis, wie man die Agora nimmt?
0b. **Phalanx hinter Mauern (Abnahme L9).** An der Festung fehlt ein Test
   „Verteidigung schlägt deutliche Übermacht“. Seit Lauf 34 stürmen 110
   statt 150 Mann; wer die Tore hält, gewinnt immer, wer nur steht, selten.
   Die Kante ist steil (bei 120 hält kein Tor), ein Test könnte sie bewachen.
0c. **Horde zu leicht.** Beide Richtungen werden immer gewonnen (Lauf 34).
   Die Räuberwerte bleiben vorerst, wie sie sind.
5. **Festung: Turm allein.** Über einen Belagerungsturm kam lange kaum ein
   Angriff hinein (Lauf 29: 0 bis 1 von 8). Seit Gruppen oben auf dem
   Wehrgang sich schließen, gewinnt die Turm-Taktik drei von vier (Lauf 34).
   Beobachten, ob das so bleibt.
6. **Festung im Angriff zu leicht?** Mit dem Rammbock gewinnt man immer
   (8 von 8) gegen eine Besatzung von 40. Bildete die Besatzung gegen
   Reiter schon Kreise, wenn sie vorn gebunden war, gewann man nie (Lauf 24);
   seit der Kreis nur eine Verzweiflungstat ist, wieder immer.
7. **Rückenangriff auf die dünne Linie, Rest.** Die hintere Reihe macht
   jetzt kehrt (Lauf 37); die tiefe Linie hält wieder gut, die dünnen
   Linien verlieren weiter mehr als vor der Trägheit (schlachtordnung 66 %
   statt 49 %, linie_reiter 94 % statt 32 %, Streuung ±10). Offen: weniger Räuber in der
   offenen Siedlung (112: tiefe Linie hält leicht; 96: alle halten) oder
   ein schwächerer Rücken-Zehr für die, die noch vorn gebunden sind.
8. **Ruhe der Bewegung, Rest.** Nach Lauf 35 (Gerangel, Platzverteilung,
   Trägheit je Mann) bleiben: Nachbartausch in der Reihe beim Marsch mit
   Gedränge (die Männer kreuzen sich seltener, tauschen aber noch), die
   Flucht, aufgelöste Haufen an Leitern, und Reziprozität beim Ausweichen
   (beide weichen je zur Hälfte, wie RVO/ORCA; heute weicht der, der anstößt).
   Maßstab: `ruhe.py` je Lage.
10. **Verbände für die Gegner-KI.** Die KI bildet noch keine Verbände und
    wechselt keine Modi; denkbar wäre etwa eine lockere Ordnung der
    Siedlung gegen Peltasten.

## Zurückgestellt

Das Spiel soll einfach bleiben und Spaß machen; die Flucht wirkt schon
wie eine Moral, und für Ausdauer ist die Karte zu klein.

- **Ausdauer.** Ein Wert je Gruppe, der bei Laufen, Sturm und Kampf
  sinkt und im Stehen steigt; erschöpfte Gruppen wären langsamer.
- **Zustandsworte und Moralgründe.** „wankt“, „gebrochen“ auf der
  Kachel, in der Pause die stärksten Moralgründe je Gruppe.
- **Aura und „Sammeln“-Befehl des Anführers.** Der Anführer stärkt nur
  seine eigene Gruppe.
- **Rechtsdrall.** Eine Phalanx drängt im Vorrücken nach rechts, weil
  jeder Mann seine offene rechte Seite in den Schild des Nebenmanns
  schiebt; der rechte Flügel ist der Ehrenplatz. Seit der Schildseite
  (Lauf 22) wäre das die naheliegende Fortsetzung. Geringer Aufwand.
- **Hang und Höhe.** Gelände, das Tempo und Kampf beeinflusst. Großer
  Aufwand.

## Erledigt

- **Die hintere Reihe macht kehrt** (5. Oktober 2026, Lauf 37): Der
  Phalanxbonus gilt nur in der ersten Reihe nach vorn. Wer gebunden wird,
  ohne vorn zu stehen, dreht sich zum Gegner um und kämpft wie jeder Mann:
  ohne Rückennachteil, Zehren und Schildseite, aber auch ohne Bonus. Tiefe
  Linie in der Siedlung 40 → 23 % Verluste, Schlachtordnung 75 → 66 %,
  Reiterlinie in der Streuung; andere Szenarien unverändert.

- **Peltasten werfen nur im Stand oder im Lauf auf den Gegner zu**
  (5. Oktober 2026, Lauf 36): nicht beim Zurückweichen, auf der Flucht oder
  seitlich vorbei. Wirkung klein (Feindverluste 2–4 Punkte niedriger).

- **Kreisflüge im Bild** (5. Oktober 2026): Die Bildglättung rechnete im
  mitgedrehten Rahmen der Gruppe; drehte sich die Front schnell (Flucht
  6 rad/s, Drehen im Handgemenge), flogen die Bilder im Kreis um die Mitte
  (bis 0,6 Kacheln je Takt), während die Männer standen. Jetzt wird der
  Versatz zur Mitte in Weltrichtung geglättet; große Bildsprünge in 90 s
  Schlacht 88 → 0–3 (die Reste: ein Mann, der wirklich geworfen wurde).

- **Trägheit je Mann** (5. Oktober 2026, Lauf 35, Punkt C): Schrittgeschwindigkeit
  je Mann, Anfahren 6 und Bremsen 15 Kacheln/s², Bremsen vor dem Platz
  (Arrive), Gruppengeschwindigkeit mitgeführt, der Block bremst vor dem Ziel.
  Marsch-Labor 0,57 → 0,16 Umkehrungen je Mann und Sekunde, Knicke 1,4 → 0,56;
  Umformen praktisch ohne Umkehrungen. Nebenbei behoben: eine Gruppe, deren
  Ziel eine ruhende eigene Gruppe belegt, bleibt davor stehen statt ewig zu
  warten; der Anlauf der Reiter zählt weiter, wenn der Kontakt kurz flackert.

- **Ruhe der Bewegung, Teil 1** (5. Oktober 2026, Lauf 35): (a) Das
  Gerangel im Bild bleibt drei Sekunden bei einem Gegner, drängt langsamer
  und steht auf Armlänge still; im Handgemenge folgt das Bild dem Mann statt
  der Gruppenmitte. Bild-Umkehrungen im Handgemenge 1,1–1,4 → 0,37 je Mann
  und Sekunde. (b) Beim Umformen bekommt jeder Mann den Platz mit den
  zusammen kürzesten Wegen (ungarische Methode je Abschnitt): Schwenk und
  Kehrtwende ohne Umkehrschritte (0,25 → 0,00), Verschmälern 1,33 → 0,19;
  in echten Schlachten (vor allem KI-Haufen ohne Linienbefehle) nicht
  messbar. Eine kämpfende Phalanx drängt fremde eigene Männer hinaus, die
  tief in ihren Reihen stecken.
  Nicht übernommen, weil gemessen wirkungslos oder schädlich: längeres
  Seitengedächtnis (2 s), den Blockierer merken (Haufen bilden dauerte
  11 statt 6 s), Mitlaufen im Marsch (ließ Männer vor dem Tor zurück).

- **Reserve um die Flanke** (4. Oktober 2026): Wird die Reserve der KI
  gerufen und steht vor ihr eine geschlossene Phalanx, läuft sie um deren
  Flanke in Flanke oder Rücken (Lauf 34: kleine Wirkung, jagende Reiter
  kosten den Spieler mehr).
- **Festung, Verteidigung** (4. Oktober 2026): 110 statt 150 Angreifer.

- **Ausweichen ohne Seitenwechsel** (4. Oktober 2026, #13): Fast alle
  Seitenwechsel entstanden, weil ein Mann nach einem freien Schritt seine
  Ausweichseite vergaß und am nächsten Mann neu wählte. Jetzt merkt er sie
  sich eine Sekunde lang (auf der Flucht nicht, sonst rennt er immer wieder
  gegen dasselbe Hindernis). Seitenwechsel je Mann, vorher → nachher:
  Plätze tauschen 1,65 → 0,05, alle zugleich vor 0,85 → 0,02, zusammenrücken
  0,62 → 0,03, einzeln nah 0,31 → 0,00. Zusammenrücken ist früher fertig
  (11,3 → 6,1 s). Beim Tauschen gibt es etwas mehr kleine Umkehrungen (0,34 →
  0,44 je Mann und Sekunde, im Bild 0,043 → 0,045). Ausprobiert und wieder
  verworfen: eine Vorfahrt zwischen zwei gehenden Gruppen (der eine tritt
  beiseite) brachte selbst Seitenwechsel; eine andere Reihenfolge beim
  Ausweichen (erst schräg zurück) ließ Gruppen in Toren und Gassen hängen.
- **Festung: Wehrgang mit Lücke** (4. Oktober 2026): Teilt ein offenes Tor
  den Wehrgang und ist der Weg über die Leitern kürzer, steigt die Gruppe
  jetzt an der einen Leiter hinab, geht unten quer und an der anderen
  hinauf. Vorher blieb sie an der ersten Leiter hängen (sie löste sich auf
  und schloss sich im Wechsel), und wer schon drüben wieder oben stand,
  bekam noch die alte Antwort „hinab an der ersten Leiter“ und lief um die
  ganze Festung. Die Entscheidung gilt jetzt je Standort.
- **Menü: Rolle oben, Schauplatz unten** (4. Oktober 2026): Oben wählt man
  Verteidigung oder Angriff, darunter Offene Siedlung, Räuberhorde oder
  Festung. Neu ist die Verteidigung gegen eine Räuberhorde, die gleich zu
  Beginn heranstürmt (der Angriff auf ihr Lager bleibt). Zwei Probeläufe:
  „linie_aktiv“ und „angriff“ gewinnen je 2 von 2.
- **Szenarien aufgeräumt** (4. Oktober 2026): Palisade, Siedlung mit Wall,
  die kleine offene Siedlung und die Siedlung ohne Wall sind fort. Neu ist
  die offene Siedlung, die Stadt der Festung ohne Wall, zum Verteidigen und
  zum Angreifen; die Räuberhorde ist viermal so groß. Alle fünf Szenarien
  liegen auf der großen Karte. Der Festungswall ist der einzige Wall, der
  Code der geraden Palisade (innen Süd, außen Nord, ein Tor) und die
  Räuberpläne gegen sie (Tor rammen, Turm, Belagern) sind entfernt. Die
  Wall-Tests prüfen jetzt die Festung. Dabei behoben: Eine Gruppe ganz oben
  auf dem Wehrgang der Festung schließt sich jetzt (sie blieb aufgelöst),
  und ist der Weg über die Leitern schneller, steuert sie die Leiter hinab
  an (statt die am Ziel und dann außen herum).
- **Pause für Befehle, drei Finger, Türme für beide** (4. Oktober 2026):
  - Befehle heben die Pause nicht mehr auf; erst „Weiter“ lässt die Zeit
    laufen. So bekommen mehrere Gruppen in Ruhe ihre Befehle.
  - Ein kurzer Tipp mit drei Fingern (unter einer halben Sekunde, ohne zu
    wischen) schaltet die Pause an und aus.
  - Ein am Wall aufgestellter Belagerungsturm dient beiden Seiten: Das
    Fußvolk der Verteidiger darf dann über die Leitern hinauf und über den
    Turm nach draußen, um Fliehenden nachzusetzen. Leitern konnten die
    Angreifer schon vorher hinab. Die Szenariotests sind unverändert, eine
    eigene Balance-Messung steht aus.
- **Großer Bogen um die eigenen Nachbarn** (4. Oktober 2026): Stand ein
  Block (im Handgemenge auch lockere Hopliten) fast auf einer eigenen Gruppe
  und lag sein Ziel auf der anderen Seite, galt sie trotzdem als „im Weg“.
  Er lief dann drei Kacheln seitlich hinaus und im Bogen zurück. Jetzt steht
  sie nur im Weg, wenn der gerade Weg um mindestens 0,3 Kacheln näher an sie
  heranführt. Dazu kam ein zweiter Fehler: Lag ein Ziel zu dicht an einer
  stehenden eigenen Gruppe, lief die Gruppe hin und wurde zurückgeschoben,
  jeden Takt aufs Neue, und kam nie in Ordnung. Jetzt nimmt sie den Platz,
  auf den sie geschoben wurde (nur befohlene Gruppen des Spielers, nicht im
  Verband). Die neue Umwegregel gilt nur für Märsche an einen Platz, nicht
  für Angriffe. Gemessen wurden 120 zufällige Befehle an lockere Hopliten
  nahe am Feind, am Schwerpunkt der Männer. Gezählt sind nur die Fälle ohne
  Flucht, alt 42 und neu 39. Der schlimmste Fall wich vorher 2,6 Kacheln
  vom geraden Weg ab, jetzt 1,2. Der Rest kommt daher, dass sein Ziel auf
  den eigenen Reitern lag und daneben verlegt wurde. Alle anderen Fälle
  bleiben unter 0,7 Kacheln.
- **Teilen, Zoomen, Befehlshaber vorn, Gruppenkacheln** (4. Oktober 2026):
  - Eine Gruppe lässt sich in zwei Hälften teilen (links/rechts, je mit
    voller Tiefe).
  - Mit zwei Fingern zoomt man stufenlos bis zur doppelten Größe, auf jeder
    Karte.
  - Der Befehlshaber steht vorn in der Mitte; wo der Anführer mitkämpft,
    ist er es.
  - In der Aufstellung stehen die Gruppen als Kacheln in einer Reihe.

  Der Anführer vorn in der Mitte fällt im Mittel früher: Zwei
  Szenariotests gewinnen über acht Startwerte je einmal weniger (7 → 6).
- **Zittern im Gedränge** (4. Oktober 2026): Die Männer werden geglättet
  gezeichnet (nur ihre Lage in der Gruppe, nicht deren Marsch), dazu eine
  Totzone am Platz für geschlossene Gruppen. Gemessen wurde, wie oft ein
  Mann sichtbar umkehrt (je Mann und Sekunde, mindestens 0,4 Bildpunkte):
  - Plätze tauschen: 0,80 → 0,08
  - alle auf einen Punkt: 0,50 → 0,13
  - alle zugleich vor: 0,63 → 0,07

  Beim Marschieren und Reiten hängt das Bild nicht nach. Offen bleibt das
  Ausweichen selbst: Zwei Drittel der Umkehrungen sind „links, dann
  rechts“ (siehe Offen).
- **Kolonne durchs Tor für alle** (3. Oktober 2026): Lockere Hopliten,
  Peltasten und Reiter ziehen wie die Phalanx schmaler durch Tor und Gasse.
  Vorher blieben lockere Hopliten und Peltasten beim Zurück durchs Tor
  hängen (Palisade herein, Festung zurück: nie fertig). Jetzt kommen in
  allen 24 Tor-Fällen alle an, niemand löst sich auf. Peltasten auf der
  Palisade hinaus: 7,7 s → 3,8 s.
- **Zappeln an Wall, Tor und Häusern** (3. Oktober 2026): Zehn Schwellen,
  an denen Gruppen hin und her kippten, haben Spiel bekommen (README, „Kein
  Zappeln an Schwellen“). Gemessen wurde je 2 s, wie weit sich eine Gruppe
  hin und her dreht und wie unruhig ihre Männer sind, ohne voranzukommen;
  acht Schlachten:
  - Festung „passiv“: höchstens 71 → 11
  - Palisade „tor_halten“: 20 → 6
  - offenes Feld „linie“: 14 → 8
  - Abschnitte über 5, zusammen: 201 → 68
- **Lockere Hopliten umstellen** (3. Oktober 2026): Auf kurzen Wegen
  stellt sich eine lockere Gruppe Mann für Mann um, statt als Block zu
  schwenken und Umwege zu gehen; die Männer werden dabei nach ihrer Stelle
  auf die Plätze verteilt, damit niemand quer durch die anderen muss.
  Drei Kacheln zur Seite: 3,6 s → 2,7 s, die Front bleibt. Lockere
  Hopliten schwenken ohne Bremse durch die Breite.
- **Reiter jagen** (3. Oktober 2026): Knopf „Jagen“ (Taste J) für Reiter.
  Sie jagen Fliehende und Ungeordnete bis acht Kacheln weit, nie eine
  geschlossene Phalanx, und kehren dann an ihren Platz zurück.
- **Vorhalten und Streuung beim Fernkampf** (3. Oktober 2026): Werfer und
  Ecktürme zielen auf die künftige Stelle, die Speere streuen mit
  Entfernung und Vorhalt, getroffen wird, wer am Einschlag steht.
  Trefferquoten (gleiche Lage, vorher → nachher): stehende Phalanx 100 % →
  87 %, marschierende 100 % → 71 %, Reiter quer im Galopp 46 % → 54 %,
  Reiter im Zickzack 22 % → 44 %. Schaden je Treffer 0,2 → 0,23.
- **Breiter Block streift Nachbarn im Bogen** (3. Oktober 2026): Der
  Zielplatz wird mit der Front geprüft, mit der die Gruppe ankommt, und ein
  Block, der die Ecke einer ruhenden eigenen Gruppe streift, gleitet schräg
  daran vorbei (bis 60 Grad), statt zu warten und sich aufzulösen. Nur für
  die Gruppen des Spielers; bei der Gegner-KI verschob das die Schlachten
  stark (siehe Lauf 32), das gehört zur Balance.
- **Drehtempo und Gassen** (3. Oktober 2026): Eine Gruppe schwenkt im
  Stand so schnell, wie ihr äußerer Mann den Bogen geht; Reiter wenden auf
  der Stelle langsamer. Die Phalanx zieht als schmale Kolonne durch
  Gassen von einer Kachel, statt sich aufzulösen (docs/ki-simulation.md,
  Lauf 32).
- **Modi der Hopliten und Verbände** (3. Oktober 2026): Locker, Phalanx
  und Sturm (ein Modus „Geschlossen“ war zu nah an der Phalanx und entfiel); die Phalanx wird an Tor und Gasse schmaler statt
  sich aufzulösen. Keine gemischten Gruppen mehr: Mehrere Gruppen bilden
  einen Verband, per Langdrücken gewählt, mit Rahmen in der Seitenleiste
  und einer Tafel zum Anordnen (docs/ki-simulation.md, Lauf 31). Damit ist
  auch „Mehrere Gruppen wählen“ erledigt.
- **Umweg-Flackern** (3. Oktober 2026): Hysterese an der Schwelle, gemerkte
  Seite, gegenseitiges Warten gelöst, gegen einen Kreis keine Flankensuche
  (docs/ki-simulation.md, Lauf 30).
- **Wehrgang** (3. Oktober 2026): dicht in Rotten, kein Vorbeischlüpfen an
  Feinden, Hopliten der Festung auf der Mauer (Reserve an den Turmausstieg),
  oben entlang oder über die Leitern je nach Zeit mit Kletterzeit.
- **Hauptmann und Kontermarsch** (3. Oktober 2026): Hauptmann je Gruppe mit
  Nachfolger, Hopliten wenden außerhalb des Handgemenges per Kontermarsch.
- **Marsch im Bogen** (3. Oktober 2026): Fußvolk schwenkt auf längeren Wegen
  im Marsch, die Front in Marschrichtung, und marschiert erst am Ziel in
  Breite und Front auf (docs/ki-simulation.md, Lauf 26).
- **Gegner lösen sich auf** (3. Oktober 2026): Räuber, Siedlung und Heer
  gehen wie die Spielergruppen Mann für Mann durchs offene Tor und an
  eigenen ruhenden Haufen vorbei; nahe am Feind bleiben sie Block
  (docs/ki-simulation.md, Lauf 25).
- **Klügere Gegner-KI** (2. Oktober 2026): Reserve, Front drehen gegen
  Reiter, Kreis nur als Verzweiflungstat, Peltasten an die schildlose Seite
  (docs/ki-simulation.md, Lauf 24).
- **Schlachtordnung** (2. Oktober 2026): Gemischte Gruppen mit einem Zug
  aufstellen: Hopliten vorn, Peltasten dahinter, Reiter an den Flügeln
  (docs/ki-simulation.md, Lauf 23).
- **Schildseite** (2. Oktober 2026): Hopliten sind an der linken Flanke
  durch den Schild gedeckt, an der rechten offen, im Nahkampf wie gegen
  Speere; Reiter und KI ziehen die rechte Seite vor. Ohne Rechtsdrall
  (docs/ki-simulation.md, Lauf 22).
- **Häuser als Hindernisse** (2. Oktober 2026): Häuser, aufgestellte
  Belagerungstürme und liegende Rammböcke sperren den Weg; Blöcke suchen
  Gassen, in die ihre Front passt. Häuser in Blöcken mit Gassen zur Agora
  (docs/ki-simulation.md, Lauf 21).
- **Festung** (2. Oktober 2026): große Karte mit sechseckigem Wall, drei
  Toren, eroberbaren Ecktürmen, Kamera mit Übersicht und Nahansicht
  (docs/ki-simulation.md, Lauf 20).
- **Zappeln beim Umgehen** (1. Oktober 2026): Wer außen herum geht, hält
  die gewählte Seite, ein Angriff nimmt die Seite mit Platz am Gegner,
  und ist keiner mehr frei, wartet er geordnet dahinter
  (docs/ki-simulation.md, Lauf 17).
- **Sammelplatz hinter dem Wall** (1. Oktober 2026): Wer über den Wall
  steigt, sammelt sich drüben am Fuß der Leiter zum Block und geht dann
  geschlossen weiter (docs/ki-simulation.md, Lauf 16).

- **Jeder Mann sucht seinen Weg selbst** (1. Oktober 2026): Das Rechteck
  gibt nur an, wo jeder stehen soll; über den Wall, durchs Tor und an
  ruhenden eigenen Gruppen vorbei geht jeder Mann für sich (Wegefeld),
  ohne dass die Gruppe springt oder sich am Ende neu aufstellt
  (docs/ki-simulation.md, Lauf 15).

- **Anführer** (1. Oktober 2026): Er kämpft in der Gruppe, die man ihm
  in der Aufstellung zuteilt, hält fünfmal so viel aus wie ein Mann
  seiner Gattung, ohne stärker zuzuschlagen; seine Gruppe nimmt 15 %
  weniger Schaden und flieht später, solange er lebt
  (docs/ki-simulation.md, Lauf 14).

- **Niemand wird mehr geschoben** (1. Oktober 2026): Eine ruhende eigene
  Gruppe bleibt, wo sie steht; wer unterwegs ist, geht außen herum,
  gleich wie breit er ist; durch Peltasten geht man hindurch
  (docs/ki-simulation.md, Lauf 13).
- **Sammeln nach der Flucht** (1. Oktober 2026): Verteidiger fliehen auf
  die Agora hinter den Häusern, sammeln sich dort und kämpfen, wenn der
  Feind sie stellt, bis zum letzten Mann. Angreifer sammeln sich an
  ihrem Kartenrand, außer die Lage ist aussichtslos; dann verlassen sie
  das Feld (docs/ki-simulation.md, Lauf 12).
- **Anstehen statt Stapeln** (1. Oktober 2026): In eine kämpfende eigene
  Gruppe fährt keine hinein; wer nicht herumkommt, steht im Block
  dahinter an. Damit laufen die Räuber auch nicht mehr einzeln über den
  Turm in eine wartende Phalanx (vorher Punkt 0 dieser Liste;
  docs/ki-simulation.md, Lauf 11).
- **Niemand steht im anderen** (30. September 2026): Kein Mann teilt
  seinen Platz mit einem anderen (zwei Halbmesser zwischen Gruppen,
  Schulter an Schulter in der eigenen), auch nicht mit Fliehenden; wer
  jemanden im Weg hat, geht schräg vorbei, nur stürmende Reiter drängen
  beiseite. Eine befohlene Gruppe umgeht eine stehende eigene, statt sie
  zu schieben; nur wer nur herumsteht, macht der befohlenen Gruppe am
  Ziel Platz (docs/ki-simulation.md, Lauf 10).
- **Kämpfen nach Berührungsbreite** (30. September 2026): Es kämpft
  nur, wer den Gegner erreicht (von Mann zu Mann gemessen), die Verluste
  fallen dort, wo der Gegner steht, und eine zweite Gruppe legt sich an
  das nächste freie Stück des Umrisses statt in die erste hinein.
  Umfassen und eingeklappte Flügel zahlen sich damit auch in Zahlen aus;
  eine lange Linie in einem Glied wird an den Enden aufgerollt
  (docs/ki-simulation.md, Lauf 9).
