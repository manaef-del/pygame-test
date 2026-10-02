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
0c. **Gegner gehen noch als Block.** Die Räuber und die Siedlung lösen sich
   (vorerst) nicht auf, um ihre eigenen Haufen zu umgehen oder durchs Tor zu
   gehen (`LOOSE_AI`). Eingeschaltet kommen sie in der offenen Siedlung
   leichter an die Häuser (Lauf 15).
1. **Schildseite.** Der Hoplitenschild sitzt links: die rechte Flanke
   ist verwundbarer, Wurfgeschosse von links treffen den Schild.
   Historischer Rechtsdrall, Ehre des rechten Flügels. Geringer Aufwand.
2. **Gruppenformationen.** Mehrere Gruppen mit einem Zug aufstellen,
   etwa Hopliten vorn, Peltasten dahinter. Mittlerer Aufwand.
3. **Hang und Höhe.** Gelände, das Tempo und Kampf beeinflusst. Großer
   Aufwand.
4. **KI: Reserve und Gegenmittel.** Eine Gruppe zurückhalten, auf
   Reiter mit Kreisen antworten, Peltasten auf die schildlose Seite
   schicken.
5. **Festung: Turm allein reicht nicht.** Über einen Belagerungsturm allein
   kommt kein Angriff hinein (0 von 8): Die Männer steigen einzeln, im Feuer
   der Ecktürme. Vielleicht deckt ein angesetzter Turm gegen die Ecktürme,
   oder er lässt mehr Männer zugleich durch.
6. **Festung im Angriff zu leicht?** Mit dem Rammbock gewinnt man immer
   (8 von 8) gegen eine Besatzung von 40.

## Zurückgestellt

Das Spiel soll einfach bleiben und Spaß machen; die Flucht wirkt schon
wie eine Moral, und für Ausdauer ist die Karte zu klein.

- **Ausdauer.** Ein Wert je Gruppe, der bei Laufen, Sturm und Kampf
  sinkt und im Stehen steigt; erschöpfte Gruppen wären langsamer.
- **Zustandsworte und Moralgründe.** „wankt“, „gebrochen“ auf der
  Kachel, in der Pause die stärksten Moralgründe je Gruppe.
- **Aura und „Sammeln“-Befehl des Anführers.** Der Anführer stärkt nur
  seine eigene Gruppe.

## Erledigt

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
