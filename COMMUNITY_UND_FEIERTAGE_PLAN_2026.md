# Regionale Instagram-Inhalte – Döbeln und Mittelsachsen

**Stand: 18. November 2026** · Kanal: @allianzschmidtdoebeln

## Neue, verbindliche redaktionelle Gewichtung

- 50 % Wissenswertes und alltagstaugliche Tipps, **ohne aggressive Produktwerbung**
- 30 % Region, Feiertage, Saison, Agenturalltag und echte Community-Fragen
- 20 % sachliche Beratung, Produkte und konkrete Leistungen

Dies sind **Zielwerte** für die nächsten Redaktionswochen, kein Anspruch über die tatsächlich bereits veröffentlichte Historie.

## Feiertage und lokale Anlässe

| Anlass | Verifiziertes Datum | Veröffentlichungsplan | Stand |
|---|---|---|---|
| Buß- und Bettag (gesetzlicher Feiertag Sachsen) | Mittwoch, 18.11.2026 | 12:00 Feed-Bild „Zeit zum Innehalten“ | **Buffer scheduled**, ID `6afcef7893fa11d37df4d0b9`, unabhängig vom Zahnzusatz-Post |
| Erster Advent | Sonntag, 29.11.2026 | 11:00 eigenständiger nicht-werblicher Feedpost + 08:30 / 20:15 passende Stories | **Im automatischen Medienkalender**, noch nicht in Buffer (43-h-Horizont) |
| Nikolaus und 2. Advent | Sonntag, 06.12.2026 | 11:00 freundlicher nicht-werblicher Feedpost + 08:30 / 20:15 passende Stories | **Im automatischen Medienkalender**, noch nicht in Buffer (43-h-Horizont) |
| Döbelner Weihnachtsmarkt | Veranstaltungswochenende im Dezember 2026; 13.12. behördlich als verkaufsoffener Sonntag zum Weihnachtsmarkt genannt | regionaler, neutraler Servicepost erst nach Abgleich von Veranstaltungszeit und freigegebenem Motiv | **Idee / noch NICHT eingeplant** |

**Datumsquellen:** 
- Sächsische Feiertage: https://www.lds.sachsen.de/anlagen/?ID=22231&art_param=104
- Gesetzliche Feiertage: https://recht.sachsen.de/vorschrift/3997.6
- Erster Advent: https://www.timeanddate.de/feiertage/deutschland/2026
- Zweiter Advent: https://www.timeanddate.de/feiertage/deutschland/zweiter-advent
- Döbeln, städtische Sonderöffnung zum Weihnachtsmarkt: https://doebeln.de/stadtverwaltung/amtsblatt/80-2026e-oeffentliche-bekanntmachung-veroeffentlicht-am-31-08-2026

## Inhalte ohne Versicherungswerbung

In `content/premium_2026_11_12.json` sind bereits sechs **komplette Story-Tage** auf nicht-werbliche Themen umgestellt:
21.11. Wochenende in Mittelsachsen;
22.11. ruhiger Sonntag;
28.11. Lieblingsplätze in unserer Region;
29.11. erster Advent;
05.12. Adventszeit;
06.12. Nikolaus und zweiter Advent.

Damit ist neben der einmaligen Feiertagskampagne echte zusätzliche Abwechslung im automatischen System. Diese Stories erscheinen weiterhin in der bestehenden Buffer-Tagesstruktur 08:30 / 20:15, wenn die Queue bei der Nachfüllung erfolgreich ist.

## Verlässlicher Ablauf

1. GitHub-Actions: `.github/workflows/premium-autopilot.yml` rendert die 81 neu konfigurierten Feed-/Story-Bilder und füllt die **nächsten 43 Stunden** im Buffer-Account auf.
2. Fehlende oder nicht gesendete Termine werden durch `scripts/audit_editorial_calendar.py` über die separate GitHub-Kontrolle als Fehler markiert, einschließlich des Buß- und Bettags.
3. Der Feiertagsbeitrag 18.11. hat eigene Datei `assets/community/buss_und_bettag_2026.png` und separaten freigegebenen Buffer-Job. Bei einem Wiederholungslauf wird derselbe Captiontext erkannt und nicht dupliziert.
4. Die Follower-Auswertung / Wochenproduktion soll vor jeder neuen Woche die offizielle Stadt-Döbeln-Veranstaltungsübersicht auf relevante Anlässe prüfen. Keine Termine oder Logos erfinden, keine tatsächliche Agentur-Anwesenheit an Veranstaltungen behaupten.
5. Bei den Posts zu religiösen Tagen einen respektvollen, neutralen Ton verwenden. Nicht als Verkaufsanlass ausnutzen.
6. Bei lokalen Motiven mit Fotografie nur eigene bzw. korrekt lizenzierte echte Ortsbilder benutzen. Symbolische KI-Bilder als Symbolbilder behandeln, nicht als vermeintliche Fotos von Döbeln.
7. Der deutlich unzutreffende automatisch generierte Dashboard-Entwurf mit falsch beschrifteten Daten/Symbolen ist **verworfen und nicht Teil des Repositories oder der Veröffentlichung**.

**Bisher versäumte Einträge 16.11. Haftpflicht/Hausrat und 17.11. Schlüsselreel** werden nicht rückdatiert oder als veröffentlicht markiert. Das neu gestartete Publishing-System muss sich an aktuellen realen Buffer-IDs messen lassen.
