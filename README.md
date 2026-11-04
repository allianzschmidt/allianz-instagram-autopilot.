# Instagram-Autopilot – Allianz Schmidt Döbeln

**Instagram:** [@allianzschmidtdoebeln](https://www.instagram.com/allianzschmidtdoebeln/)  

**ABSOLUTES LOGO-VERBOT:** Keine Allianz-Logos oder sonstige grafische Allianz-Markenzeichen in Bildern, Reels, Stories, Hintergründen, Dokumenten oder am Gebäude. Auch frühere Fotovorlagen mit Logo sind ausgeschlossen. [Verbindliche Richtlinie](./KEINE_ALLIANZ_LOGOS.md). Vor Buffer-Einplanung muss jeder einzelne Beitrag zusätzlich ausdrücklich `logo_free_verified: true` haben. Ohne Nachweis stoppt das System.
**Start:** 03.11.2026  
**Status:** Noch NICHT live. Veröffentlichungen bleiben ohne vorherige Freigabe technisch gesperrt.  
**Kosten:** Buffer Free + öffentliches GitHub-Repository / GitHub Actions (innerhalb der jeweiligen kostenlosen Nutzungsbedingungen).

> **Achtung zum Repository-Namen:** Dieses Repository wurde mit einem Punkt am Ende angelegt: `allianz-instagram-autopilot.`. Bitte den Punkt bei der GitHub-URL beachten.

## Was schon eingerichtet ist

- `posts.json`: **30 deutschsprachige Entwürfe** über Haftpflicht, Berufsunfähigkeit, Kfz, Hausrat, Wohngebäude, Zahnzusatz, Familie und Beratung in Döbeln. Alle haben `"approved": false`.
- `scripts/render.py`: erzeugt nun **sechs deutlich unterschiedliche Entwurfs-Layouts** in `assets/`, mit geometrischen Illustrationen statt identischen Textkacheln; keine kopierten Allianz-Logos.
- `.github/workflows/generate-assets.yml`: erzeugt Grafiken über GitHub Actions und checkt sie in das Repository ein.
- `scripts/autopilot.py`: sucht **ausschließlich** `@allianzschmidtdoebeln` im Buffer-Konto, prüft die Freigaben, verhindert Wiederholungen bereits bekannter Captions und legt höchstens einen neuen freigegebenen Beitrag pro Werktag in die Buffer-Warteschlange.
- `.github/workflows/instagram-autopilot.yml`: startet werktags morgens mit `publish`; ohne explizite Freischaltung wird nichts zu Buffer übertragen.
- `.github/workflows/instagram-weekly.yml`: montags ein technischer Bericht mit Status und den über die persönliche Buffer-API abrufbaren Metriken. Fehlende Daten werden nicht als Null interpretiert.

**Neue Richtung:** Siehe [REDESIGN_30_BEITRAEGE.md](./REDESIGN_30_BEITRAEGE.md) mit 12 Reels, 10 Karussells, 5 echten Agentur-/Döbeln-/Porträtbeiträgen und 3 Quiz-Ideen (erst Storyboards, noch keine fertigen Videos). Alte 30 Bildbeiträge bleiben gesperrte Entwürfe.

**VERBINDLICHE PERSONENREGEL (04.11.2026):** In allen Inhalten mit Menschen ausschließlich das vom Nutzer hochgeladene Foto von **Paul Schmidt** benutzen. Keine anderen Mitarbeitenden, Modelle, Familien, Kunden, Stock-Personen, KI-Gesichter oder synthetischen Paul-Videos. Alternative Motive müssen vollständig personenfrei sein. Datei für automatisches Rendern: `assets/portrait/paul_schmidt.jpg` (**als komprimierte 300 × 299-Pixel-Vorschau erfolgreich hochgeladen**). Der GitHub-Workflow hat fünf Porträt-Beitragsentwürfe erstellt und erfolgreich versioniert, **keine** Veröffentlichungen. [Alle fünf ansehen](./PAUL_5_ENTWUERFE.md). Für spätere Veröffentlichungen die hochwertige Originalaufnahme verwenden.

Aktuell sind **Feed-Bildbeiträge** vorgesehen. **Reels, Stories, Kommentare, DMs, Leads und die automatische Produktion neuer Beiträge** gehören noch nicht zu diesem Paket.

## Die noch nötigen Schritte

### 1. Buffer Free verbinden

1. Ein eigenes Konto auf [buffer.com](https://buffer.com/) anlegen.
2. Instagram **@allianzschmidtdoebeln** als professionelles Profil verbinden; gegebenenfalls die zugehörige Facebook-Seite autorisieren.
3. Für das Instagram-Profil in Buffer eine **Posting-Queue** festlegen, zum Beispiel Montag bis Freitag 18:30 Uhr (Europe/Berlin).
4. Keinesfalls das andere Profil `@alphagorilla.shop` als Ziel verwenden.

### 2. Geheimen API-Schlüssel hinterlegen

1. In Buffer unter [Settings → API](https://publish.buffer.com/settings/api) einen persönlichen API-Schlüssel erzeugen.
2. Im **GitHub-Repository** unter **Settings → Secrets and variables → Actions → Repository secrets → New repository secret** gehen.
3. **Name:** `BUFFER_API_KEY` / **Secret:** den Wert des Schlüssels.
4. Schlüssel **niemals** als GitHub-Datei, Screenshot oder Chat-Nachricht teilen. Der Schlüssel hat potentiell Zugriff auf weitere eigene Buffer-Accounts.

### 3. Prüfen, ob das richtige Konto erreicht wird

Unter [GitHub Actions](https://github.com/allianzschmidt/allianz-instagram-autopilot./actions) den Workflow **Allianz Instagram - sichere Buffer-Automation** öffnen und **Run workflow → action: validate** ausführen. Im Log muss exakt `@allianzschmidtdoebeln` stehen. Bei Fehlermeldung **keine** Freischaltung vornehmen.

### 4. Fachliche Freigabe und Aktivierung

1. Alle gewünschten Posts und die Grafiken anhand der gültigen Werbe- und Markenrichtlinien der Allianz-Agentur prüfen. Auch das Profil inklusive Impressum und Datenschutzinformationen prüfen.
2. In `posts.json` **nur die ausdrücklich freigegebenen Posts** auf `"approved": true` ändern. Nicht freigegebene Entwürfe bleiben `false`.
3. Unter GitHub **Settings → Secrets and variables → Actions → Variables** zwei **Repository variables** setzen:
   - `LEGAL_APPROVED` = `true` **erst nach fachlicher/Agenturfreigabe**.
   - `PUBLISH_ENABLED` = `true` **erst wenn Veröffentlichung tatsächlich starten soll**.
4. Danach kann unter **Actions → Allianz Instagram - sichere Buffer-Automation → Run workflow → publish** ein erster freigegebener Post eingeplant werden. Die regelmäßigen Werktagsläufe übernehmen weitere freigegebene Posts.

**Hinweis:** `PUBLISH_ENABLED=false` stoppt das Hinzufügen neuer Posts. Es entfernt **keine bereits** in Buffer geplanten Beiträge; diese müssen bei Bedarf direkt in Buffer pausiert/gelöscht werden.

## Grafiken erzeugen

Der Workflow [Allianz Instagram - Grafiken erzeugen](https://github.com/allianzschmidt/allianz-instagram-autopilot./actions/workflows/generate-assets.yml) generiert JPEGs beim Setup und werktags am Morgen. Manuell geht es über **Run workflow**. Bei einem Bildfehler wird keine Veröffentlichung geplant. Bilder werden öffentlich gespeichert, **keine** Kundendaten.

## Wöchentliche Auswertung

GitHub **Actions → Allianz Instagram - Wochenanalyse** zeigt veröffentlichte, geplante und fehlgeschlagene Posts sowie soweit verfügbar Reaktionen, Kommentare, Reichweite und Aufrufe aus der Buffer-API. Diese Kennzahlen werden vom Netzwerk ungefähr täglich aktualisiert und können zunächst fehlen.

**Nicht automatisch auswertbar:** echte Beratungstermine, gewonnene Neukunden, individuelle Nachrichten oder Umsatz. Dafür wären gesonderte datenschutzkonforme Prozesse nötig.

## Technische Grenzen und Sicherheit

- Der Workflow ist nur eine Vorplanung, nicht bereits live geschaltet. Erst nach Schlüssel, erfolgreicher Zielkonto-Verifikation und zwei expliziten Freigabevariablen werden **einzeln freigegebene Beiträge** eingeplant.
- Im kostenlosen Buffer-Plan dürfen nur begrenzt viele Beiträge gleichzeitig eingeplant sein. Der Autopilot hört bei mindestens neun offenen Posts vorsichtshalber auf.
- Die GitHub-Workflows können verzögert laufen oder auf API-Probleme stoßen. Keine garantierte Live-Veröffentlichung oder Wachstumszusage.
- Nichts in diesem öffentlichen Repository sollte Passwörter, Zugangstokens, persönliche Kundendaten, Gesundheitsdaten oder nicht freigegebene interne Agenturunterlagen enthalten.
- Genaue Allianz-Produktleistungen, Beitragshöhen und Leistungszusagen bleiben an die jeweils gültigen Unterlagen und Verträge gebunden.

### Quellen zur technischen API

- [Buffer Authentication](https://developers.buffer.com/guides/authentication.html)
- [Buffer Posts & Scheduling](https://developers.buffer.com/guides/posts-and-scheduling.html)
- [Buffer Post Metrics](https://developers.buffer.com/guides/post-metrics.html)
