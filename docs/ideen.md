# Offene Ideen

Was große Schlachtenspiele anders machen und wo es sich bei uns noch
lohnt nachzujustieren, nach Wirkung je Aufwand geordnet. Erledigtes
wandert nach unten.

## Offen

0. **Balance der Angriffe.** Seit niemand mehr geschoben wird und
   Siedlungen bis zum letzten Mann halten, sind die Angriffsszenarien
   viel schwerer (Lauf 13): Gegen die Horde verliert eine dünne Linie
   immer, und der letzte Kampf auf der Agora zieht sich bis zum
   Zeitlimit. Zu klären: Soll der letzte Kampf schwächer sein (etwa
   Moralverlust trotz Agora), sollen Angreifer Reserven gezielt um die
   eigene Front herum an den Feind schicken können, oder brauchen die
   Räuber andere Werte?
0b. **Räuber über den Turm (Lauf 15, 16).** Seit jeder Mann seinen Weg
   selbst sucht, kamen die Räuber einzeln über den Turm und verteilten sich.
   Mit dem Sammelplatz hinter dem Wall (Lauf 16) gehen sie drüben wieder als
   Block weiter; „Leiter decken“ gewinnt 10 von 12 (vor Lauf 15: 12),
   „Tor halten“ 5 von 12 (vorher 0), der Abnahmetest „Phalanx hinter der
   Palisade“ 6 von 8 Startwerten (vorher 8). Wer passiv stehen bleibt,
   verliert weiterhin alle Häuser (0 von 12, vorher 10). Dabei fiel auf,
   dass die Räuber-KI vor der Palisade zwischen „Umgehen“ (um ein Ende, das
   es dort nicht gibt) und „Frontal“ hin und her schwankt, wenn die Schlacht
   lange dauert.
5. **Festung: Turm allein reicht nicht.** Über einen Belagerungsturm allein
   kommt kaum ein Angriff hinein (0 bis 1 von 8): Die Männer steigen einzeln,
   im Feuer der Ecktürme. Dazu greift die Turm-Taktik der Simulation die
   fliehenden Reste an der Agora nicht an, sodass die Schlacht bis zur
   Zeitgrenze läuft (Lauf 29). Vielleicht deckt ein angesetzter Turm gegen die Ecktürme,
   oder er lässt mehr Männer zugleich durch.
6. **Festung im Angriff zu leicht?** Mit dem Rammbock gewinnt man immer
   (8 von 8) gegen eine Besatzung von 40. Bildete die Besatzung gegen
   Reiter schon Kreise, wenn sie vorn gebunden war, gewann man nie (Lauf 24);
   seit der Kreis nur eine Verzweiflungstat ist, wieder immer.
13. **Ausweichen ohne Seitenwechsel, Vorfahrt.** Im Gedränge weichen
    Männer einem Kameraden aus und wechseln dabei oft gleich die Seite (zwei
    Drittel aller Umkehrungen). Ein erster Versuch (bei der Seite bleiben,
    kurz warten) half beim Tauschen (−25 %), schadete beim Zusammenrücken
    (+40 %). Besser wäre wohl eine Vorfahrt zwischen zwei Gruppen (die
    gehende geht, die stehende macht Platz) und bei sich überschneidenden
    Zielen versetzte Plätze und ein kurzes Warten der einen Gruppe.
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
