# LIVE – Premium-Instagram-Autopilot

**Aktiviert:** 18. November 2026, 00:55 Uhr MEZ (Erstlauf am 17.11.2026 23:55 UTC).
**Kanal:** ausschließlich @allianzschmidtdoebeln.

## Fertig und technisch getestet

- Eigenständige GitHub Actions Pipeline: [Premium-Autopilot](./.github/workflows/premium-autopilot.yml)
- Erzeugt automatisch 79 neue, logofreie Premium-Bilder: 41 Feed-Slides für 9 vereinbarte Feed-Termine und 38 Story-Bilder für 19 Tage (18.11.–06.12.2026).
- Übernimmt diese Bilder in das GitHub-Verzeichnis [assets/premium_autopilot_v1](./assets/premium_autopilot_v1) und macht sie für Buffer zugänglich.
- Ruft Buffer viermal täglich auf, befüllt einen Zeitraum von bis zu 43 Stunden voraus, respektiert das Free-Queue-Limit (höchstens 9 aktive, automatisch verwaltete Einträge), prüft exaktes Instagram-Konto und dedupliziert nach Termin.
- Gesendete Postings lassen sich in der separaten [Kalenderkontrolle](./.github/workflows/check-approved-depot.yml) abgleichen; fehlende Termine führen nicht mehr zu einem falsch-grünen Gesamtstatus.
- Echte Premium-Auswertung über [Instagram-Wochenanalyse](./.github/workflows/instagram-weekly.yml).
- Beide ChatGPT-Aufgaben (Wochenproduktion und Postingkontrolle) sind auf diese neue Pipeline umgestellt.
- Die alten 30 verworfenen Designs bleiben gesperrt. Alte tägliche Grafikerzeugung und der alte schreibende Buffer-Lauf wurden deaktiviert.

## Erster bestätigter Buffer-Lauf

[Automatische Produktion + Buffer-Einplanung, erfolgreich](https://github.com/allianzschmidt/allianz-instagram-autopilot./actions/runs/44203542305).

| Datum MEZ | Uhrzeit | Inhalt | Buffer-ID | Status beim ersten Lauf |
|---|---|---|---|---|
| 18.11. | 08:30 | Story Zahnzusatz | `6afce981ab47737bddb3c4ca` | scheduled |
| 18.11. | 18:30 | Fünfteiliges Premium-Karussell Zahnzusatz | `6afce982f0c5ce9361ab4ef4` | scheduled |
| 18.11. | 20:15 | Story Zahnzusatz | `6afce983ab47737bddb3c4f8` | scheduled |
| 19.11. | 08:30 | Story Einkommensschutz | `6afce983ab47737bddb3c51e` | scheduled |

Zusätzlich bereits unverändert geplant:
- 19.11., 12:30 – Einkommensschutz Foto, Buffer-ID `6af4ec05bc9f3773a1a45de2`
- 26.11., 12:30 – Starkregen Foto, Buffer-ID `6af4ec063d8c751bfdfae8b0`

[Zweiter Testlauf, keine Doppelpostings](https://github.com/allianzschmidt/allianz-instagram-autopilot./actions/runs/44204425706).

## Was weiterhin nicht automatisch online geht

- 16.11. Haftpflicht/Hausrat und 17.11. Schlüssel-Reel wurden versäumt. Die Pipeline holt verpasste Termine nicht eigenmächtig nach.
- Die vereinbarten Reels für 24.11. und 01.12. bleiben ausdrücklich ausgenommen, bis qualitativ akzeptierte Videos vorhanden sind. Keine abgelehnten KI-Avatar-Sprecher und keine minderwertigen Standbildvideos.
- Der veröffentlichungsfertige, automatisch befüllte Kalender endet derzeit am **06.12.2026**; für danach wird eine neue Themen- und Medienplanung benötigt. Die wöchentliche Planung erinnert rechtzeitig daran.

## Verbindliche Sicherheit

- 0 Allianz-Logos, Markenbildzeichen oder deren Nachbildungen. Nur die ausgeschriebene Bezeichnung „Allianz Agentur Schmidt“ und Blau als Farbe.
- Keine fremden Menschen, keine KI-Sprecher-Reels, keine alten abgelehnten Designs.
- Nur die im [Premium-Themenplan](./content/premium_2026_11_12.json) definierten Themen. Keine eigenmächtige Themenänderung. Allgemeine Versicherungsinformationen enthalten keine individuellen Leistungs- oder Renditeversprechen.
- GitHub/Buffer/Meta können trotzdem technisch ausfallen. Deshalb Beleg prüfen: `scheduled` heißt eingeplant, `sent` heißt von Buffer als versendet gemeldet. Eine öffentliche Instagram-URL ist gesondert zu prüfen.
