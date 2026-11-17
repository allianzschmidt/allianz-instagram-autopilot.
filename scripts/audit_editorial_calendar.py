"""Abgleich des verbindlichen Feed-Kalenders gegen REALEN Buffer-Status.
Read-only: erstellt KEINE Posts. Bekannte Lücken werden als Fehler gemeldet.
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from autopilot import get_channel, posts_from_buffer

# Alle Zeitangaben UTC, deutsche Winterzeit = UTC+1.
PLAN = [
 ("2026-11-16T17:30:00Z", "Haftpflicht oder Hausrat", "haftpflicht", None),
 ("2026-11-17T18:00:00Z", "Reel Schlüsselverlust erklärt", "schlüssel", None),
 ("2026-11-18T17:30:00Z", "Zahnzusatz 100 %?", "zahn", None),
 ("2026-11-19T11:30:00Z", "Einkommensschutz", "einkommen", "6af4ec05bc9f3773a1a45de2"),
 ("2026-11-20T17:30:00Z", "BU für Schüler", "berufsunf", None),
 ("2026-11-23T17:30:00Z", "Teilkasko oder Vollkasko", "kasko", None),
 ("2026-11-24T18:00:00Z", "Reel Steinschlag", "steinschlag", None),
 ("2026-11-25T17:30:00Z", "Starkregen Elementarschutz", "starkregen", None),
 ("2026-11-26T11:30:00Z", "Starkregen Bildbeitrag", "starkregen", "6af4ec063d8c751bfdfae8b0"),
 ("2026-11-27T17:30:00Z", "Unfallversicherung", "unfall", None),
 ("2026-11-30T17:30:00Z", "Familie absichern", "familie", None),
 ("2026-12-01T18:00:00Z", "Reel 3 Fragen vor Versicherungsabschluss", "fragen", None),
 ("2026-12-02T17:30:00Z", "Wohngebäude vs Hausrat", "wohngeb", None),
 ("2026-12-03T11:30:00Z", "Beratung in Döbeln", "beratung", None),
 ("2026-12-04T17:30:00Z", "Rechtsschutz", "rechtsschutz", None),
]
def parse(s):
    return datetime.fromisoformat(s.replace("Z","+00:00"))
def check():
    org, ch = get_channel()
    posts = posts_from_buffer(org["id"], ch["id"])
    now = datetime.now(timezone.utc)
    errors=[]
    for when,title,keyword,post_id in PLAN:
        due = parse(when)
        if not now-timedelta(days=7) <= due <= now+timedelta(days=3):
            continue
        candidates = [p for p in posts if (
            (p.get("id")==post_id if post_id else
                (keyword in (p.get("text") or "").lower() and
                 abs((parse(p.get("dueAt"))-due).total_seconds())<1500
                 if p.get("dueAt") else False))
        )]
        record = candidates[0] if candidates else None
        status = record.get("status") if record else "MISSING"
        print("REDAKTIONSKALENDER:",due.isoformat(),title,"Buffer:",status,
              "Post-ID:",record.get("id") if record else "KEINE")
        if record is None:
            errors.append(title+" (fehlende Buffer-Einplanung, "+when+")")
        elif now>due+timedelta(minutes=45) and status!="sent":
            errors.append(title+" (nach Fälligkeit nicht als sent bestätigt: "+str(status)+")")
        elif now<due and status not in ("scheduled","buffer","sending","sent"):
            errors.append(title+" (ungültiger Buffer-Status: "+str(status)+")")
    if errors:
        print("!!! VERBINDLICHE REDAKTIONSPLAN-LÜCKEN !!!")
        for item in errors: print("PLANLUECKE:",item)
        raise SystemExit(1)
    print("Alle zeitnahen Feed-Termine sind im Buffer-Kalender bestätigt.")
if __name__=="__main__":
    check()
