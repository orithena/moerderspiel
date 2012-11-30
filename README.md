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
4. Spieler tragen ihre Morde ein
  - Benötigt wird der Signaturcode vom Auftrag
  - Alle Spieler, deren Aufträge sich geändert haben, bekommen eine neue Mail
  - Der Mord wird getwittert
  - Spieler können den aktuellen Stand unter der URL des Spiels ansehen
5. Spielleiter beendet das Spiel
  - Unter der URL des Spiels kann nun die gesamte Auftragsliste für alle Spieler eingesehen werden


Motivation
==========

Es ist schon fast unglaublich, wie viel Aufwand man als Spielleiter hat, wenn man dieses Spiel 
ordentlich organisieren will...

Erstes Problem bei simpler Randomisierung (alias: Jeder Mitspieler zieht seinen Auftrag 
aus einem Hut):  Zwei Spieler könnten sich gegenseitig ziehen. Unfair, weil ein erfolgreicher
Mörder dann den Auftrag erhält, sich selbst umzubringen, nicht weiter spielen kann und keine
Chance mehr auf den Massenmördertitel hat. Also muss der Spielleiter die Aufträge in einen
zufälligen Kreis legen und jedem Spieler dessen Nachfolger in diesem Kreis geben. Das kann
schon mal eine gute Weile Zeit beanspruchen.

Dann kommt es dauernd vor, dass Spieler ihre Aufträge verlieren, vergessen oder auch aus 
dem Spiel aussteigen wollen. Also muss man als Spielleiter notiert haben, wer wen umbringen 
soll -- und erst noch nachtragen, wer wen bereits umgebracht hat, um den richtigen Auftrag 
erneut ausstellen zu können.

Schön wäre es außerdem, wenn man dafür sorgt, dass niemand den Auftrag erhält, eine ihm 
bereits bekannte Person umzubringen (zumindest nicht als ersten Auftrag; später ist dies
nicht vermeidbar). Dies verlängert den Akt der Auftragsverteilung weiter.

Und um den Aufwand noch explodieren zu lassen, lassen wir mehrere Spiele parallel laufen. 
So hat jeder Mitspieler mehrere Leben, mehrere Aufträge, aber auch mehrere Mörder auf den
Fersen. Und jetzt wächst der Aufwand plötzlich überlinear, denn man will ja auch noch 
sicherstellen, dass kein Spieler das gleiche Opfer zu Anfang mehrfach umbringen muss.

Ich hab den ganzen Aufwand oft genug gehabt ... also hab ich mir ein Webinterface zur 
Verwaltung des Ganzen geschrieben. Inzwischen ist dies so weit gediehen, dass jeder 
dort ein Spiel anlegen und potentielle Mitspieler dazu einladen kann.

Damit kann das Spiel komplett offline durchgeführt werden, wenn der Spielleiter das 
generierte PDF ausdruckt und verteilt. Auf der anderen Seite geht es auch komplett 
online, wenn alle Spieler ihre Email-Adresse eingetragen und immer ein Smartphone dabei 
haben. Aber auch die Mischvariante funktioniert: Aufträge werden vom Spielleiter auf 
Papier herausgegeben oder von jedem Mitspieler ausgedruckt, der Eintrag eines Mordes 
im Webinterface kann dann auch später bei Gelegenheit stattfinden -- und ist eigentlich 
nur wichtig, wenn man nach Spielende eine schöne Statistik haben und die Morde auch auf
Twitter beim @moerderbot sehen will.


Installation
============
Siehe https://github.com/orithena/moerderspiel/wiki


Dependencies
============
Python Modules: genshi, yapgvb, twython, dateutil, email, smtplib

Sonstiges: texlive-xetex ttf-sil-gentium graphviz
