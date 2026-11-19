# Wochenproduktion – Live-Status und Freigabevorbereitung, 19.11.2026, 09:56 CET

**Kanal ausschließlich:** @allianzschmidtdoebeln  
**Zeitraum:** 19.11.2026–26.11.2026 (7 Tage voraus, 26.11. 09:56 CET).  
**Quellen:** VERBINDLICHER_INSTAGRAM_PLAN_NOV_DEZ_2026.md, content/premium_2026_11_12.json, COMMUNITY_UND_FEIERTAGE_PLAN_2026.md, QUELLEN_AGENTUR_UND_DOEBELN_FOTOBANK.md, DESIGN_STOPP_UND_NEUE_STORY_LINIE_2026-11-18.md.
**Live-Buffer-Abfrage:** GitHub Actions 44479076077, 19.11.2026 08:22 CET (07:22 UTC), job 135406622226. Die Statuswerte gelten nur für diesen Zeitpunkt.

## Tatsächliche Buffer-Buchungen
| CET | Thema | ID | Status |
|---|---|---|---|
| 19.11. 12:30 | Einkommen weg – was dann? Feed-Foto | `6af4ec05bc9f3773a1a45de2` | scheduled |
| 26.11. 12:30 | Starkregen – ist dein Zuhause vorbereitet? Feed-Foto | `6af4ec063d8c751bfdfae8b0` | scheduled (außerhalb 7-Tage-Grenze, aber bereits gebucht) |

Im Live-Buffer-Audit wurden **nur diese beiden aktiven Einträge** als scheduled/buffer/sending gefunden. Keine anderen offenen Beiträge dürfen als gebucht bezeichnet werden. Der Feiertagspost vom 18.11. ist aus der aktiven Queue verschwunden; ohne Einzelstatus nicht hier als sent bestätigen.

## Exakte, bislang fehlende Termine laut verbindlichem Plan
| CET | Format | Thema | Status | Hinderungsgrund |
|---|---|---|---|---|
| 19.11. 08:30 / 20:15 | Stories | Einkommensschutz | missing | kein individuell freigegebenes Story-Medium |
| 20.11. 08:30 / 20:15 | Stories | Schüler-BU | missing | kein individuell freigegebenes Story-Medium |
| 20.11. 18:30 | Karussell | BU für Schüler | missing | finale freigegebene Slides fehlen |
| 21.11. 08:30 / 20:15 | Stories | Wochenende in Mittelsachsen | missing | finales freigegebenes Motiv fehlt |
| 22.11. 08:30 / 20:15 | Stories | Ruhiger Sonntag | missing | finales freigegebenes Motiv fehlt |
| 23.11. 08:30 / 20:15 | Stories | Kaskoschutz | missing | finales freigegebenes Motiv fehlt |
| 23.11. 18:30 | Karussell | Teilkasko oder Vollkasko? | missing | finale freigegebene Slides fehlen |
| 24.11. 08:30 / 20:15 | Stories | Steinschlag | missing | finales freigegebenes Motiv fehlt |
| 24.11. 19:00 | Reel | Steinschlag | missing | kein fertig freigegebenes Reel |
| 25.11. 08:30 / 20:15 | Stories | Starkregen | missing | finales freigegebenes Motiv fehlt |
| 25.11. 18:30 | Karussell | Starkregen und Elementarschutz | missing | finale freigegebene Slides fehlen |
| 26.11. 08:30 | Story | Zuhause schützen | missing | finales freigegebenes Motiv fehlt |

**Keine Rückdatierung.** Story 19.11. 08:30 war zum Prüfzeitpunkt bereits vorbei. 26.11. 20:15 liegt außerhalb des 7-Tage-Fensters und ist ebenfalls noch nicht gebucht.

## Neue Designvorschau (noch keine Veröffentlichung)
Zwei bewusst unterschiedliche fotografische Symbolmotiv-Konzepte wurden zur Freigabe in der Chat-Ausgabe 19.11.2026 erzeugt:
1. **BU für Schüler:** Editoriales echtes *KI-Symbolbild* eines Schreibtischs mit Schulrucksack, Notizbuch, natürlichem Abendlicht; Hook „Früh an morgen denken.“; keine Menschen, Logos oder KI-Sprecher.
2. **Teilkasko oder Vollkasko:** Cinematic-KI-Symbolbild eines regennassen Fahrzeugs mit dunklem Premium-Blau und warmen Reflexen; Hook „Was schützt dein Auto?“; kein Markenlogo oder fremde Person.

Die Bildvorschau ist **keine** individuell freigegebene Mediendatei und kein fertiges 4-/5-Slide-Karussell. Für die Karussells müssen alle Slides einzeln gestaltet, überprüft, vom Nutzer freigegeben und mit SHA256 registriert werden. Nicht aus einem Side-by-Side-Moodboard automatisch eine Story schneiden oder posten.

## Regionale Fakten (nur Recherche, NICHT redaktionell freigegeben)
Offizielle Veranstaltungsübersicht: https://doebeln.de/tourismus-kultur-freizeit/veranstaltungen  
- 22.11., 10–14 Uhr: Stiefelpokal im Bogenschießen
- 25.11., 17–20:30 Uhr: Workshop „SocialMedia – neue Plattformen, altes Handwerk – Filme, Videos und Onlineclips“
- 26.11., 18–20 Uhr: „Open Voices – Offenes Chorprojekt“ des Treibhaus e.V.
- Dauerhafte Ausstellungen im Stadtmuseum/Kleiner Galerie. 
Nur bei redaktioneller Freigabe neutralen Eventhinweis ergänzen; keine Termine oder Themen des verbindlichen Plans verdrängen. Offizielles sächsisches Feiertagsrecht: https://recht.sachsen.de/vorschrift/3997.6 .

## Harte Sicherheitsregeln / Queue
- `premium_visuals_explicitly_reapproved=false` bleibt unverändert.
- `content/visual_approval_manifest.json` enthält aktuell `media: {}`; keine individuell freigegebenen neuen Bilddateien.
- Alte `assets/premium_autopilot_v1/` sind ausdrücklich abgelehnt und dürfen nicht durch Umbenennen oder Wiederaktivieren erscheinen.
- Bestehende zwei scheduled IDs unangetastet; aktuell nur zwei aktive Posts, damit keine Buffer-Free-Queue-Überfüllung.
- `scripts/visual_quality_gate.py` und `scripts/audit_visual_integrity.py` sind aktiv. Letzter Qualitätscheck: bestanden, keine abgelehnten/unbekannten geplanten Medien.
- Keine neuen Buffer-IDs, weil keine freigegebenen Medien vorliegen. Erst nach konkreter visueller Freigabe Bildrechte, korrekte Typografie, Text und SHA256 prüfen; danach einzeln buchen und `scheduled` verifizieren.
- Die redaktionelle Zielgewichtung bleibt 50 % Wissen / 30 % Community / 20 % Versicherung. Der aktuell veröffentlichte Mix kann daraus nicht abgeleitet werden.
