# Offene Ideen

Was große Schlachtenspiele anders machen und wo es sich bei uns noch
lohnt nachzujustieren, nach Wirkung je Aufwand geordnet. Erledigtes
wandert nach unten.

## Offen

0. **Turm nur mit Platz dahinter.** Seit Männer sich nicht mehr
   durchdringen, laufen die Räuber über den Turm einer nach dem anderen
   in eine wartende Phalanx (Palisade, `passiv`: 4/4 Siege, 100 %
   Verluste der Räuber). Die Belagerungs-KI sollte den Turm meiden oder
   verlegen, wenn hinter dem Wall eine Formation wartet, und lieber das
   Tor rammen oder umgehen. Geringer Aufwand.
1. **Sammeln nach der Flucht.** Fliehende bleiben stehen, sobald eine
   Weile kein Feind naht, ihre Moral steigt langsam, und sie nehmen wieder
   Befehle an, statt das Feld für immer zu verlassen. Geringer Aufwand.
2. **Ausdauer.** Ein Wert je Gruppe, der bei Laufen, Sturm und Kampf
   sinkt und im Stehen steigt; erschöpfte Gruppen sind langsamer, treffen
   schwächer und brechen früher. Belohnt Reserven, bestraft endloses
   Kreisen der Reiter. Mittlerer Aufwand.
3. **Schildseite.** Der Hoplitenschild sitzt links: die rechte Flanke
   ist verwundbarer, Wurfgeschosse von links treffen den Schild.
   Historischer Rechtsdrall, Ehre des rechten Flügels. Geringer Aufwand.
4. **Zustandsworte und Moralgründe.** Auf der Kachel „wankt“,
   „gebrochen“, in der Pause je Gruppe die drei stärksten Moralgründe
   (umzingelt, Verluste, Nachbar flieht). Geringer Aufwand.
5. **Anführer mit Aura.** Der Oikist als eigene Figur: Moral in seiner
   Nähe, „Sammeln“ als Befehl, sein Tod bricht. Mittlerer Aufwand.
6. **Gruppenformationen.** Mehrere Gruppen mit einem Zug aufstellen,
   etwa Hopliten vorn, Peltasten dahinter. Mittlerer Aufwand.
7. **Häuser als Hindernisse.** Gassen statt freier Fläche; später Hang
   und Höhe. Großer Aufwand.
8. **KI: Reserve und Gegenmittel.** Eine Gruppe zurückhalten, auf
   Reiter mit Kreisen antworten, Peltasten auf die schildlose Seite
   schicken.

## Erledigt

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
