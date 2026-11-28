# Betriebsprotokoll 28.11.2026 – Master-Umstellung
Kanal @allianzschmidtdoebeln, Europe/Berlin. Tatsächlich geprüft, keine geschätzten Erfolge.

## Ursache und Maßnahmen
- Alte Serie absichtlich gesperrt seit 18.11.; Alt-Publisher und Renderer werden nicht wieder aktiviert. Alte Pfade/IDs bleiben blockiert.
- Alte Kalenderkontrolle setzte bei Sperre events=[]; 0 geprüfte Slots galten als Erfolg. Ersetzt durch 7-Tage-Lückenprüfung (inkl. vergangener Tage, tatsächlicher Buffer-IDs und Medienhashes).
- Master-Strategie in INSTAGRAM_MASTER_STRATEGIE.md, operative Briefings und Prüfung/Buchung getrennt in content/master_ready_queue.json. Bestehende Frequenz erhalten. Regionalthema 28.11. ausdrücklich verworfen; Vormittag verpasst, kein Nachholen. 20:15 durch Kfz-Story ersetzt. Keine Änderungen am ursprünglich vorgesehenen Feed-Rhythmus.
- Bestehenden Workflow premium-autopilot.yml auf gesichtete Einzelmedien mit SHA256, tatsächliche Medienprüfung, gepinnte Original-URL, Slot-/ID-/Status-/Dublettencheck, Queue-Obergrenze 9 (1 Platz Reserve) und persistierte Buchungsbelege umgestellt. Einmaligen Medienimport nach erfolgreichem Transfer entfernt. Neuer Workflow erzeugt noch keine kreativen Bilder selbst. Er publiziert nur tatsächlich vorher gerenderte und geprüfte Medien.
- Beide bestehenden ChatGPT-Aufgaben aktualisiert und Befristung entfernt, Frequenz unverändert (täglich 20:45, Do 10:00). Keine neue redundante Aufgabe.
- Buffer Free erlaubt maximal 10 geplante Posts/Kanal; 7 Tage Medienvorrat von tatsächlicher Queue unterscheiden: https://buffer.com/pricing. Kein Upgrade veranlasst.
- Repo ist öffentlich; keine vertraulichen Daten, Kundendaten, Secrets oder private Medien speichern.

## Belege
- Erste neue Prüfung 12:04 CET: https://github.com/allianzschmidt/allianz-instagram-autopilot./actions/runs/46138140318 – 95 Buffer-Einträge, 0 aktive Queue, 19 fehlende Slots 28.11.–04.12. (1 verpasst, 18 damals offen).
- Neue Kfz-Story 28.11. 20:15 CET, ID 6b0ab646e897dadb1d7651f4, scheduled, tatsächliche Sichtprüfung und Originalhash; keine nachträgliche Einzel-Nutzerfreigabe fingiert. https://github.com/allianzschmidt/allianz-instagram-autopilot./actions/runs/46138472330
- Wiederholung erkennt vorhandene ID und erzeugt keine Dublette: https://github.com/allianzschmidt/allianz-instagram-autopilot./actions/runs/46138583440
- Unabhängige Qualitätskontrolle: https://github.com/allianzschmidt/allianz-instagram-autopilot./actions/runs/46138605150 – keine abgelehnte/unbekannte aktive Queue, exakt 1 scheduled, 17 offene Medien/Slots, 1 verpasst. Workflow absichtlich rot wegen offener Lücken.
- Wochenanalyse: https://github.com/allianzschmidt/allianz-instagram-autopilot./actions/runs/46138641334 – aktuelle 7 Tage 8 sent, vorher 9. Reach je gemessenem Beitrag 35,25 (8/8) vs 32,88 (8/9), Views Summe 368 vs 376 (je 8), Reaktionen 0 vs 1, Kommentare 0/0 (je 8), Saves/Shares 0/0 (5 vs 4). Kein deduplizierter Accountwert. Beste Reach: Kfz-Story 59, Sonntag 57, Steinschlagstory 53. 2 in aktueller Woche gesendete Einträge nicht aus explizitem bisherigem Register: 6b0895dc5c4eafdb37d213a5 (Skisaison), 6b05f2c68cbc791045187c12 (Weihnachtsthema); Herkunft offen, nicht ohne Nachweis als unbefugt darstellen.
- Followerbestand, Nicht-Follower-Reichweite, Profilaufrufe/Klicks/Anfragen nicht belastbar verfügbar. Keine Bestzeiten aus kleiner Stichprobe.
- Erste externe Instagram-Wettbewerberrecherche: öffentlich sichtbare konkrete Instagram-Posts durch Login/fehlende Indexierung nicht verlässlich verfügbar. Keine Wettbewerberzahlen/Erfolge fingiert. Wöchentlicher Auftrag bleibt. Algorithmus-Recherche: https://buffer.com/resources/instagram-algorithms/ – Originalität, Wiedergabedauer, Likes und Sends pro Reichweite; konkrete nützliche Hooks, Fallbeispiele, Story-Mehrwert, Karussells testweise stärker einsetzen.
- Adventdatum verifiziert https://www.timeanddate.de/feiertage/deutschland/advent ; kreative Bildproduktion nicht erfolgreich (falscher generierter Dashboard-Entwurf verworfen, nicht veröffentlicht; ein lizenzierbarer Fotokandidat ließ sich nicht abrufen). Kein Adventsmedium als fertig gebucht melden.
 
## Offen
17 zukünftige Slots vom 29.11.–04.12. noch ohne tatsächlich gerenderte und gesichtete Dateien. Advent am 29.11. 08:30 / 11:00 / 20:15 zuerst. Keine Rückdatierung. Creative-Erstellung muss in den bestehenden Agenten-Aufgaben tatsächlich möglich sein und nachweislich erfolgen; GitHub-Refill allein ersetzt sie nicht. Bei fehlendem Bildtool oder Transfer genaue technische Ursache melden; nicht alte Vorlagen reaktivieren. Vollständiger siebentägiger Medienvorrat und autonome kreative Produktion noch nicht erreicht. Reel 01.12. weiter gesondert nicht freigegeben. Öffentliche Instagram-Permalinks nicht unabhängig verifiziert.
