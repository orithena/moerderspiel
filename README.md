Das Moerderspiel
================

WTF is this?

Das Mörderspiel ist ein Nebenbei-Spiel im Real Life für größere Gruppen (6 bis 166 Spieler/innen) 
über mehrere Tage mit min. drei Auswirkungen:

* Man lernt sich untereinander besser kennen
* Man entwickelt ein gehöriges Maß Paranoia
* Man lernt, eine versteckte Agenda mit kreativen Mitteln zu verfolgen

Alle Mitspielenden erhalten zum Start zufällig einen (nach Gusto auch mehrere) Mordaufträge; 
z.B. "Erledige Bertram". Man zieht also los und sucht Bertram, den man erst mal erkennen und 
dann durch Übergabe eines beliebigen Gegenstandes umbringen soll. Es muss schon eine 
freiwillige, unbeobachtete Übergabe sein, andernfalls gilt der Mord nicht. Ziel ist es, 
das Opfer in eine Situation zu bringen, bei der er nicht aufs Spiel achtet und einfach einen 
Gegenstand annimmt. Zuwerfen gilt nicht, aufzwängen auch nicht.

Hat man jemanden erfolgreich ermordet, muss man ihm dies sofort sagen und erhält vom Opfer 
dessen Mordauftrag, mit dem man weiter spielen kann. Das Opfer ist dann raus aus dem Spiel 
(es sei denn, man spielt mit mehreren Leben ... und in dem Falle sollte der Mörder aufpassen, 
nicht mit der Übergabe des Mordauftrags umgebracht zu werden).

Geeignete Gelegenheiten zum Spielen:

* Auf Konferenzen. Entstanden in seiner derzeitigen Form ist es auf der Konferenz der Informatik-Fachschaften.
* Im Urlaub, wenn man mit einigen Freunden verreist.
* In der Uni/Schule
* ... im Grunde immer, wenn 6 oder mehr Leute sich über mehr als zwei Tage öfter mal über den Weg laufen.


Zweck dieser Software
=====================
Diese Software ist eine Webapplikation, um das oben beschriebene Mörderspiel per Software zu unterstützen.

Die Software begleitet den Spielleiter und die Spieler durch das gesamte Spiel hindurch. Mordaufträge und
Druckvorlagen werden generiert, alle Spieler werden per Email benachrichtigt und zum Schluss bekommen die 
Spieler eine schöne Übersicht über das gesamte Spiel.

Der grobe Ablauf:
1. Spielleiter eröffnet ein Spiel
  - er erhält seinen Mastercode und die URL des Spiels -- letztere gibt er an alle potentiellen Spieler
2. Spieler besuchen die URL des Spiels und melden sich an
3. Spielleiter startet das Spiel
  - Die Spieler werden in einen oder mehrere Kreise randomisiert
  - Alle Spieler kriegen eine Email mit ihren Aufträgen
  - Spielleiter kriegt ein PDF mit den Aufträgen zum ausdrucken und verteilen
4. Morde werden eingetragen
  - Benötigt wird der Signaturcode vom Auftrag
  - Alle Spieler, deren Aufträge sich geändert haben, bekommen eine neue Mail
  - Der Mord wird getwittert
  - Spieler können den aktuellen Stand unter der URL des Spiels ansehen
5. Spielleiter beendet das Spiel
  - Unter der URL des Spiels kann nun die gesamte Auftragsliste für alle Spieler eingesehen werden


Installation
============
Siehe https://github.com/orithena/moerderspiel/wiki


Dependencies
============
Python Modules: genshi, yapgvb, twython, dateutil, email, smtplib

Sonstiges: texlive-xetex ttf-sil-gentium graphviz
