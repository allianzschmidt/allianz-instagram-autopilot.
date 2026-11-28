"""Rolling seven-day live audit. Old design stop is a block, never an excuse to hide gaps."""
import json,sys,hashlib
from collections import Counter
from datetime import datetime,timezone,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,note
from premium_publish import items,PLAN
from visual_quality_gate import load_manifest

ROOT=Path(__file__).resolve().parents[1]
BERLIN=ZoneInfo("Europe/Berlin")
ACTIVE={"scheduled","buffer","sending"}
EXISTING_APPROVED={
 "2026-11-21T14:45:00+00:00":("Kfz finaler Freigabe-Feed 15:45 CET","6b0177aed864a01105380378"),
 "2026-11-21T19:45:00+00:00":("Kfz finale Freigabe-Story 20:45 CET","6b0177ae0247969092c4a058"),
 "2026-11-18T11:00:00+00:00":("Buß- und Bettag – werbefreier Gruß","6afcef7893fa11d37df4d0b9"),
 "2026-11-19T11:30:00+00:00":("Einkommensschutz Foto","6af4ec05bc9f3773a1a45de2"),
 "2026-11-22T15:00:00+00:00":("Freigegebene Sonntags-Story zur Kaffeezeit 16:00 CET","6b02fd3dd5eabfb8ccb562d9"),
 "2026-11-24T16:00:00+00:00":("Neuer Kfz-Angebots-Feed 17:00 CET","6b059f73589dfc670e86245d"),
 "2026-11-24T17:30:00+00:00":("Korrigierte Steinschlag-Story 18:30 CET","6b0591a79dcfd3880923c06b"),
 "2026-11-26T11:30:00+00:00":("Starkregen Foto","6af4ec063d8c751bfdfae8b0"),
}

def parse(s):
    return datetime.fromisoformat(s.replace("Z","+00:00")) if s else None

def has_ready_media(row,manifest):
    if row.get("review_status")!="verified" or not row.get("review_note") or not row.get("rights") or not row.get("sources"):
        return False
    assets=row.get("assets") or []
    if not assets or len(assets)!=row.get("expected_assets"):return False
    for a in assets:
        rel=Path(a.get("path",""))
        key=rel.as_posix()
        if rel.is_absolute() or ".." in rel.parts or not key.startswith("assets/master_reviewed/"):return False
        if any(key.startswith(prefix) for prefix in manifest.get("explicitly_rejected_prefixes",[])):return False
        path=ROOT/rel
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=a.get("sha256"):return False
    return True

def audit():
    now=datetime.now(timezone.utc)
    today=now.astimezone(BERLIN).date()
    end=today+timedelta(days=7)
    org,ch=get_channel()
    posts=posts_from_buffer(org["id"],ch["id"])
    manifest=load_manifest()
    allowed=manifest.get("grandfathered_separately_approved_posts",{})
    blocked=set(manifest.get("rejected_buffer_ids",[]))
    ready_path=ROOT/"content/master_ready_queue.json"
    ready=json.loads(ready_path.read_text(encoding="utf8")) if ready_path.exists() else {"slots":[]}
    by_slot={parse(x["due_at"]):x for x in ready.get("slots",[])}
    events={x["due"]:dict(x) for x in items()}
    for instant,(label,post_id) in EXISTING_APPROVED.items():
        dt=parse(instant)
        events[dt]={"due":dt,"label":label,"caption":None,"expected_id":post_id}
    for dt,row in by_slot.items():
        events[dt]={"due":dt,"label":row["label"],"caption":row.get("caption"),"expected_id":row.get("buffer_id"),"ready":row}
    old_stop=PLAN.get("premium_visuals_explicitly_reapproved") is not True
    active=[p for p in posts if p.get("status") in ACTIVE]
    note("INSTAGRAM: "+ch["name"]+" UTC: "+now.isoformat()+" | Buffer-Einträge: "+str(len(posts))+" | aktive Queue: "+str(len(active)))
    note("ROLLIERENDER 7-TAGE-PLAN: "+str(today)+" bis "+str(end-timedelta(days=1))+" Europe/Berlin")
    note("ALTE SERIE GESPERRT: "+str(old_stop)+"; Lücken werden weiterhin erfasst.")
    history=Counter()
    for p in posts:
        try:d=parse(p.get("dueAt"))
        except ValueError:continue
        if d and now-timedelta(days=7)<=d<=now:
            if p.get("status")=="sent":
                history["sent"]+=1
                note("VERGANGEN: "+d.astimezone(BERLIN).isoformat()+" | sent | "+p["id"]+" | "+(p.get("text") or "")[:100].replace("\n"," "))
            elif p.get("status") in {"error","failed"}:history["error"]+=1
    note("LETZTE 7 TAGE Buffer: "+str(dict(history))+" (sent ist kein unabhängiger Instagram-Permalink)")
    errors=[];counts=Counter();covered=set()
    for dt,item in sorted(events.items()):
        day=dt.astimezone(BERLIN).date()
        if day<today-timedelta(days=1) or day>=end:continue
        row=item.get("ready") or {}
        candidates=[]
        for p in posts:
            try:d=parse(p.get("dueAt"))
            except ValueError:continue
            if not d or abs((d-dt).total_seconds())>120 or p["id"] in blocked:continue
            if item.get("expected_id") and p["id"]!=item["expected_id"]:continue
            if not item.get("expected_id"):
                if p["id"] not in allowed:continue
                if not item.get("caption") or p.get("text")!=item["caption"]:continue
            if p.get("status") in ACTIVE|{"sent","error","failed"}:candidates.append(p)
        if len(candidates)>1:
            state="DUPLIKAT";errors.append(item["label"]+" doppelt")
        elif candidates:
            p=candidates[0];state=p["status"]
            if state=="sent" or state in ACTIVE:covered.add(day)
            if day>=today and (state in {"error","failed"} or (now>dt+timedelta(minutes=45) and state!="sent")):
                errors.append(item["label"]+" nicht gesendet: "+state)
        else:
            state="BLOCKIERT_ALTES_DESIGN" if old_stop and not row else ("MEDIEN_BEREIT_NICHT_GEBUCHT" if has_ready_media(row,manifest) else "MEDIEN_FEHLEN_ODER_UNGEPRUEFT")
            if dt<now:state="VERPASST_"+state
            if day>=today:
                # A fully reviewed future media reserve is acceptable only beyond the next 24h.
                if not (has_ready_media(row,manifest) and dt>now+timedelta(hours=24)):
                    errors.append(dt.astimezone(BERLIN).isoformat()+" "+item["label"]+" "+state)
        if day>=today:counts[state]+=1
        note("PLAN: "+dt.astimezone(BERLIN).isoformat()+" | "+item["label"]+" | "+state+" | ID "+(candidates[0]["id"] if candidates else "-"))
    for offset in range(7):
        day=today+timedelta(days=offset)
        if not any(d.astimezone(BERLIN).date()==day for d in events):
            errors.append(str(day)+" KEIN REDAKTIONSKALENDER")
        if day not in covered:note("TAG OHNE BESTAETIGTE BUCHUNG: "+str(day))
    note("7-TAGE-STATUS: "+str(dict(counts)))
    if not counts:errors.append("Kein einziger Kalenderslot geprüft")
    for e in errors:note("!!! LIVE-PLAN-LUECKE: "+e)
    if errors:raise SystemExit(1)
    note("LIVE-KALENDER: alle geprüften Slots sind gebucht/gesendet oder mit geprüftem Medienvorrat abgedeckt.")
if __name__=="__main__":audit()
