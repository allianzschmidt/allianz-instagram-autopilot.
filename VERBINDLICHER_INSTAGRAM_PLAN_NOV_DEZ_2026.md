# Verbindliche Reihenfolge für Instagram @allianzschmidtdoebeln
**Stand:** 11.11.2026, 23:30 Uhr Europe/Berlin.

Diese Datei ist der *maßgebliche redaktionelle Plan* für die Folgewochen. **Nur** `scheduled` und `sent` im aktuellen Buffer-Konto sind tatsächliche Buchungen; `missing` bedeutet explizit: **noch nicht in Buffer eingeplant**. Termine mit `missing` dürfen nicht als gebucht ausgegeben werden.

## Bestätigte vergangene Veröffentlichungen
- 09.11.2026 um 20:29 Uhr: Altersvorsorgedepot 2027, 5 Slides, Buffer `sent`, Post-ID `6af21ee7eb73f8e77f54509f`.
- 11.11.2026 um 20:35 Uhr: Schlüssel weg – wer zahlt?, 4 Slides, Buffer `sent`, Post-ID `6af4c365cf36c484ae925f3c`.

## Aktive Termine und Lücken

| Datum (CET) | Uhrzeit | Format | Thema | Status bei Erstellung | Buffer-Post-ID |
|---|---|---|---|---|---|
| 12.11.2026 | 12:30 | Feed-Foto | Steinschlag – wer zahlt? | scheduled | 6af4c4bab523db05a3eb3fb1 |
| 13.11.2026 | 18:30 | Karussell 4 Slides | Wasser im Haus – was jetzt? | scheduled | 6af4c4bbcf36c484ae92dbae |
| 13.11.2026 | 20:15 | Story | Wasserschaden – was tust du zuerst? | scheduled | 6af4ec0477f44b6536fd7573 |
| 14.11.2026 | 08:30 | Story | Schlüsselverlust – Quiz | scheduled | 6af4ec058a1a2f52b508371a |
| 16.11.2026 | 18:30 | Karussell | Haftpflicht oder Hausrat? | missing |  |
| 17.11.2026 | 19:00 | Reel | Schlüsselverlust erklärt | missing |  |
| 18.11.2026 | 18:30 | Karussell | Zahnzusatz – 100 %? | missing |  |
| 19.11.2026 | 12:30 | Feed-Foto | Einkommen weg – was dann? | scheduled | 6af4ec05bc9f3773a1a45de2 |
| 20.11.2026 | 18:30 | Karussell | BU für Schüler | missing |  |
| 23.11.2026 | 18:30 | Karussell | Teilkasko oder Vollkasko? | missing |  |
| 24.11.2026 | 19:00 | Reel | Steinschlag | missing |  |
| 25.11.2026 | 18:30 | Karussell | Starkregen und Elementarschutz | missing |  |
| 26.11.2026 | 12:30 | Feed-Foto | Starkregen – ist dein Zuhause vorbereitet? | scheduled | 6af4ec063d8c751bfdfae8b0 |
| 27.11.2026 | 18:30 | Karussell | Unfallversicherung | missing |  |
| 30.11.2026 | 18:30 | Karussell | Familie richtig absichern | missing |  |
| 01.12.2026 | 19:00 | Reel | 3 Fragen vor dem Abschluss | missing |  |
| 02.12.2026 | 18:30 | Karussell | Wohngebäude vs. Hausrat | missing |  |
| 03.12.2026 | 12:30 | Feed-Foto | Beratung in Döbeln | missing |  |
| 04.12.2026 | 18:30 | Karussell | Rechtsschutz | missing |  |

## Stories
Stories sind täglich um 08:30 und 20:15 Uhr als redaktionelles Ziel vereinbart, in der Regel Quiz + Auflösung/Beitragsteaser. Nur **zwei** neue Story-Slots in diesem Zeitraum sind derzeit wirklich durch Buffer bestätigt: Fr, 13.11. um 20:15 Uhr und Sa, 14.11. um 08:30 Uhr. Für alle anderen Story-Slots fehlen teilweise die finalen Premium-Story-Dateien bzw. die bestätigte Buffer-Buchung. Keine Fake-Polls: Interaktive Instagram-Quiz- und Umfrage-Sticker werden in Buffer nicht automatisch gesetzt und dürfen nicht als echte interaktive Abstimmung dargestellt werden.

## Verbindliche Gestaltungs- und Sicherheitssperren
- **Niemals Allianz-Logos/Bildzeichen oder Nachbildungen**, auch nicht im Hintergrund. Die ausgeschriebene Agenturbezeichnung „Allianz Agentur Schmidt“ in einfacher Schrift ist erlaubt; Blau ist erlaubt.
- **Keine Bilder fremder Personen und keine abgelehnten künstlichen Sprecher-Reels.** Pauls Originalporträt höchstens gelegentlich.
- Keines der 30 alten `posts.json`-Bildmotive freigeben. `approved:false` bleibt.
- Kein vereinbarter Format-/Datums-/Themenwechsel ohne Nutzervorgabe. Insbesondere nicht spontan ein anderes Produkt anstelle des angekündigten Themas bewerben.
- Nur konkret freigegebene fertige Premium-Medien dürfen automatisch in Buffer. Neue, erst erstellte Materialien dürfen nicht ungeprüft veröffentlicht werden.
- Jede konkrete fachliche Aussage zu Versicherungsleistungen, Förderung und Bedingung muss vor Live-Ausspielung anhand aktueller Unterlagen korrekt sein.
- GitHub Actions läuft als Plattform-Workflow, der bei Verbindungsfehlern/Instagram-/Buffer-API-Problemen scheitern kann; keine Garantie für eine erfolgreiche Meta-Veröffentlichung. Nach geplantem Termin ist `sent` zu prüfen.
- Bevor weitere Termine als fest markiert werden, muss Buffer tatsächlich `scheduled` und die konkrete Post-ID melden.

## Automatik
- GitHub-Actions-Datei `.github/workflows/check-approved-depot.yml` kontrolliert aktuelle bestätigte Termine täglich viermal und schlägt bei Abweichungen fehl.
- ChatGPT-Aufgabe „Instagram Schmidt – Postingkontrolle“ kontrolliert täglich um 20:45 Uhr und meldet fehlende/gescheiterte Buchungen.
- **Die frühere allgemeine Publishing-Automation ist weiterhin deaktiviert**, um die verworfenen 30 Designs nicht automatisch zu publizieren.
