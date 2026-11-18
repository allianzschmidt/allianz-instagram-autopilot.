"""Hands-off Buffer scheduler for the selected premium Instagram editorial calendar.

Only includes exact named future slots from content/premium_2026_11_12.json.
No usage of rejected posts.json graphics or third-party talking-head videos.
Idempotent; detects duplicates and queue saturation, preserves German time.
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel, posts_from_buffer, query
from visual_quality_gate import require_approved_media

ROOT=Path(__file__).resolve().parents[1]
PLAN=json.loads((ROOT/"content/premium_2026_11_12.json").read_text(encoding="utf8"))
BASE=ROOT/"assets/premium_autopilot_v1"
BERLIN=ZoneInfo("Europe/Berlin")
ROOT_URL="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/premium_autopilot_v1/"
REPO="allianzschmidt/allianz-instagram-autopilot."
ALLOW_POST_STATUSES=("scheduled","buffer","sending","sent")
MAX_QUEUED=9
HORIZON_HOURS=43

def due(date,clock):
    hour,minute=(int(x) for x in clock.split(":"))
    d=datetime.fromisoformat(date).replace(hour=hour,minute=minute,tzinfo=BERLIN)
    return d.astimezone(timezone.utc)

def items():
    rows=[]
    for post in PLAN["posts"]:
        img=[f"{post['id']}/{i:02d}.jpg" for i in range(1,len(post["slides"])+1)]
        rows.append(dict(date=post["date"],clock=post["time"],kind="post",
                         label=post["tag"]+" ["+post["id"]+"]",
                         image_paths=img,caption=post["caption"]))
    for row in PLAN["stories"]:
        for clock,period in (("08:30","morning"),("20:15","evening")):
            rows.append(dict(date=row["date"],clock=clock,kind="story",
                label="STORY "+row["tag"]+" "+period,
                image_paths=[f"stories/{row['date']}_{period}.jpg"],caption=""))
    for item in rows:item["due"]=due(item["date"],item["clock"])
    return sorted(rows,key=lambda x:x["due"])

def check_image(local,remote):
    raw=Path(local).read_bytes()
    if len(raw)<25000 or raw[:3]!=b"\xff\xd8\xff":
        raise RuntimeError("Ungeprüftes oder unvollständiges Bild: "+str(local))
    for attempt in range(4):
        try:
            request=urllib.request.Request(remote,headers={"User-Agent":"SchmidtPremiumPublisher/1.0"})
            with urllib.request.urlopen(request,timeout=25) as response:
                if response.status!=200 or response.read(3)!=b"\xff\xd8\xff":
                    raise RuntimeError("Bild nicht öffentlich verfügbar: "+remote)
            return
        except Exception:
            if attempt==3:raise
            time.sleep(5)

def publish():
    # VISUELLE FREIGABESPERRE ab 18.11.2026:
    # Nutzer hat die auto-generierten Standard-Storys explizit abgelehnt.
    # Die gesamte generische Bildserie bleibt bis zur Designabnahme gesperrt.
    if not PLAN.get("premium_visuals_explicitly_reapproved", False):
        print("DESIGN-STOPP: Automatische Standard-Storys und Schablonen-Karussells sind gesperrt.")
        return
    if os.getenv("GITHUB_REPOSITORY")!=REPO:
        raise RuntimeError("Falsches Repository – nichts posten")
    if os.getenv("PREMIUM_SERIES_RELEASE")!="approved-autopilot-premium-nov26-v1":
        raise RuntimeError("Neue Premium-Serie nicht zur automatischen Planung freigegeben")
    if PLAN.get("account")!="allianzschmidtdoebeln" or not PLAN.get("no_logos"):
        raise RuntimeError("Falscher Kanal oder Logo-Sicherheitsrichtlinie fehlt")
    org,channel=get_channel()  # fail closed if wrong IG channel or queue paused
    posts=posts_from_buffer(org["id"],channel["id"])
    now=datetime.now(timezone.utc)
    active=sum(x.get("status") in ("scheduled","buffer","sending") for x in posts)
    print("KANAL:",channel["name"],"Queue aktiv:",active,"UTC:",now.isoformat())
    created=0
    misses=[]
    for item in items():
        d=item["due"]
        if d<now-timedelta(minutes=5):
            continue  # niemals unangekündigt alte Termine nachholen
        if d>now+timedelta(hours=HORIZON_HOURS):
            continue
        matches=[]
        for p in posts:
            if not p.get("dueAt"):continue
            try:
                existing=datetime.fromisoformat(p["dueAt"].replace("Z","+00:00"))
                if abs((existing-d).total_seconds())<120:
                    matches.append(p)
            except ValueError:pass
        if matches:
            p=matches[0]
            if p.get("status") not in ALLOW_POST_STATUSES:
                misses.append(item["label"]+": Buffer-Eintrag fehlerhaft "+str(p.get("status")))
            elif item["caption"] and p.get("text")!=item["caption"]:
                misses.append(item["label"]+": anderes Thema zur gleichen Zeit gebucht!")
            else:
                print("BEREITS GEBUCHT:",item["date"],item["clock"],item["label"],p.get("status"),p.get("id"))
            continue
        if active>=MAX_QUEUED:
            print("QUEUE_LIMIT:",item["date"],item["clock"],item["label"])
            if d<now+timedelta(hours=17):
                misses.append(item["label"]+": Buffer-Free-Warteschlange voll")
            continue
        # Keine Serienfreigabe ohne einzeln gesichtete, unveränderte Medien.
        require_approved_media(["assets/premium_autopilot_v1/"+name for name in item["image_paths"]])
        urls=[ROOT_URL+name for name in item["image_paths"]]
        for f,u in zip(item["image_paths"],urls):
            check_image(BASE/f,u)
        media=",".join("{image:{url:"+json.dumps(u)+"}}" for u in urls)
        metadata=("metadata:{instagram:{type:"+item["kind"]+
                  (",shouldShareToFeed:false" if item["kind"]=="story" else ",shouldShareToFeed:true")+
                  ",isAiGenerated:true}}")
        gql=("mutation {createPost(input:{text:"+json.dumps(item["caption"],ensure_ascii=False)+
             ",channelId:"+json.dumps(channel["id"])+
             ",schedulingType:automatic,mode:customScheduled,dueAt:"+json.dumps(d.isoformat().replace("+00:00","Z"))+
             ",assets:["+media+"],aiAssisted:true,"+metadata+
             "}) { ... on PostActionSuccess{post{id status dueAt text}} ... on MutationError{message} }}")
        outcome=query(gql).get("createPost",{})
        if not isinstance(outcome,dict) or not outcome.get("post"):
            raise RuntimeError("Buffer lehnt "+item["label"]+" ab: "+str(outcome))
        result=outcome["post"]
        if result.get("status") not in ALLOW_POST_STATUSES:
            raise RuntimeError("Buffer meldet unerwarteten Zustand: "+str(result))
        if result.get("dueAt"):
            actual=datetime.fromisoformat(result["dueAt"].replace("Z","+00:00"))
            if abs((actual-d).total_seconds())>120:
                raise RuntimeError("Buffer hat den falschen Termin gebucht: "+str(result))
        posts.append(result)
        active+=1
        created+=1
        print("PREMIUM BUFFER GEPLANT:",item["date"],item["clock"],item["label"],"ID",result["id"],"STATUS",result["status"])
    # Fail loudly if a content gap is imminent and an automatic run cannot fill it.
    for item in items():
        d=item["due"]
        if d<now-timedelta(minutes=5) or d>now+timedelta(hours=16):continue
        if not any(
            p.get("dueAt") and abs((datetime.fromisoformat(p["dueAt"].replace("Z","+00:00"))-d).total_seconds())<120
            and p.get("status") in ALLOW_POST_STATUSES
            for p in posts
        ):
            misses.append("MORGEN/HEUTE FEHLT: "+item["date"]+" "+item["clock"]+" "+item["label"])
    print("ERFOLGREICH NEU GEBUCHT:",created,"QUEUE AKTIV:",active)
    if misses:
        for m in set(misses):print("VEROEFFENTLICHUNGS-LUECKE:",m)
        raise RuntimeError("Nicht alle kurzfristigen Termine konnten in Buffer gebucht werden")
if __name__=="__main__":
    try: publish()
    except Exception as exc:
        print("AUTOPILOT NICHT VOLLSTÄNDIG ERFOLGREICH:",str(exc),file=sys.stderr)
        sys.exit(1)
