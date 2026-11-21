"""Read-only, honest check of ALL premium scheduled Instagram slots.

Look for unqueued slots, not only entries known by Buffer ID.
A previously missed post never blocks the pipeline forever.
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer
from premium_publish import items,PLAN

EXISTING_APPROVED={
 "2026-11-21T11:45:00+00:00":("Golf-Kfz-Angebot Story 12:45 CET","6b017160d9cbb430a13b30f6"),
 "2026-11-21T14:45:00+00:00":("Golf-Kfz-Angebot Feed 15:45 CET","6b017160dd205ed779d9ba15"),
 "2026-11-21T17:45:00+00:00":("Golf-Kfz-Daten Story 18:45 CET","6b017160d9cbb430a13b3159"),
 "2026-11-21T19:45:00+00:00":("Golf-Kfz-DM Story 20:45 CET","6b01716120a2d09a0af0cc69"),
 "2026-11-18T11:00:00+00:00":("Buß- und Bettag – werbefreier Gruß","6afcef7893fa11d37df4d0b9"),
 "2026-11-19T11:30:00+00:00":("Einkommensschutz Foto","6af4ec05bc9f3773a1a45de2"),
 "2026-11-26T11:30:00+00:00":("Starkregen Foto","6af4ec063d8c751bfdfae8b0"),
}

def audit():
    org,ch=get_channel()
    now=datetime.now(timezone.utc)
    posts=posts_from_buffer(org["id"],ch["id"])
    print("INSTAGRAM:",ch["name"],"NOW:",now.isoformat(),"BUFFER COUNT:",len(posts))
    if PLAN.get('premium_visuals_explicitly_reapproved') is False:
        print('DESIGN-FREIGABE-STOPP: Wiederholte Standardgrafiken sind vom Nutzer abgelehnt; deren fehlende Buffer-Termine gelten ausdrücklich NICHT als Ausfall.')
        events=[]
    else:
        events=items()
    for instant,(label,post_id) in EXISTING_APPROVED.items():
        dt=datetime.fromisoformat(instant)
        events.append({"due":dt,"label":label,"caption":None,"expected_id":post_id})
    events.sort(key=lambda x:x["due"])
    errors=[]; counted=0
    for item in events:
        due=item["due"]
        if due>now+timedelta(hours=16):
            continue
        if due<now-timedelta(days=1):
            continue  # historic gaps are separately documented; not silently fixed
        found=[]
        for p in posts:
            if not p.get("dueAt"):continue
            try:
                t=datetime.fromisoformat(p["dueAt"].replace("Z","+00:00"))
            except ValueError:continue
            if abs((t-due).total_seconds())<=120:
                found.append(p)
        if item.get("expected_id"):
            found=[p for p in found if p.get("id")==item["expected_id"]]
        status=found[0].get("status") if found else "MISSING"
        label=item["label"]
        counted+=1
        print("PLAN:",due.isoformat(),label,"BUFFER:",status,
              "ID:",found[0].get("id") if found else "-")
        if not found:
            errors.append(due.isoformat()+" "+label+" ist NICHT eingeplant")
        elif item.get("caption") and found[0].get("text")!=item["caption"]:
            errors.append(due.isoformat()+" "+label+" – FALSCHER INHALT")
        elif now>due+timedelta(minutes=45) and status!="sent":
            errors.append(due.isoformat()+" "+label+" – NICHT gesendet: "+str(status))
        elif now<due and status not in ("scheduled","buffer","sending","sent"):
            errors.append(due.isoformat()+" "+label+" – unerwarteter Zustand: "+str(status))
    print("KONTROLLIERTE FÄLLIGE/NAHE TERMINE:",counted)
    print("AUSGENOMMENE, NICHT FREIGEGEBENE REELS: 24.11., 01.12. (keine fremde Stimme)")
    for problem in errors:
        print("!!! LIVE-PLAN-LUECKE:",problem)
    if errors:raise SystemExit(1)
    print("LIVE-KALENDER: alle kurzfristigen Slots richtig eingeplant bzw. gesendet")
if __name__=="__main__":
    audit()
