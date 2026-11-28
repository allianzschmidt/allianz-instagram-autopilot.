"""Master-commissioned, exact-media Buffer refill. Legacy generator is never invoked."""
import hashlib,json,os,subprocess,sys,time,urllib.request
from datetime import datetime,timezone,timedelta
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,note
from visual_quality_gate import load_manifest
ROOT=Path(__file__).resolve().parents[1]
READY=ROOT/"content/master_ready_queue.json"
MANIFEST=ROOT/"content/visual_approval_manifest.json"
REPO="allianzschmidt/allianz-instagram-autopilot."
ACTIVE={"scheduled","buffer","sending"}
MAX_QUEUE=9 # 10 on Buffer Free, retain one emergency/manual slot
HORIZON=timedelta(days=7)
def parse(s):return datetime.fromisoformat(s.replace("Z","+00:00")) if s else None
def save(path,data):
    tmp=path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    tmp.replace(path)
def verify(row,manifest,commit):
    if row.get("review_status")!="verified" or row.get("review_authority") not in ("master_2026_11_28_operational","explicit_user"):
        raise RuntimeError("Keine konkrete operative/individuelle Freigabe")
    if not all(row.get(k) for k in ("reviewed_at","review_note","rights","sources")):
        raise RuntimeError("Sichtprüfung, Rechte oder Quellen fehlen")
    if row["review_authority"]=="explicit_user" and row.get("user_visual_approval") is not True:
        raise RuntimeError("Explizite Freigabe nicht dokumentiert")
    assets=row.get("assets",[])
    if not assets or len(assets)!=row["expected_assets"] or (row["kind"]=="story" and len(assets)!=1):
        raise RuntimeError("Unvollständige Medien")
    if row["kind"] not in ("post","story"):raise RuntimeError("Nicht geprüfter Medientyp")
    urls=[]
    from PIL import Image
    for a in assets:
        path=Path(a["path"])
        key=path.as_posix()
        if path.is_absolute() or ".." in path.parts or not key.startswith("assets/master_reviewed/"):
            raise RuntimeError("Unzulässiger Medienpfad "+key)
        if any(key.startswith(prefix) for prefix in manifest.get("explicitly_rejected_prefixes",[])):
            raise RuntimeError("Abgelehntes Motiv")
        raw=(ROOT/path).read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=a["sha256"]:raise RuntimeError("Hash stimmt nicht: "+key)
        with Image.open(ROOT/path) as im:
            im.verify()
        with Image.open(ROOT/path) as im:
            w,h=im.size
            if im.format!=a["format"] or (w,h)!=(a["width"],a["height"]) or w<720 or h<720:
                raise RuntimeError("Unpassendes Format/Auflösung "+key)
            if row["kind"]=="story" and abs(w/h-9/16)>0.025:
                raise RuntimeError("Story nicht 9:16")
            if row["kind"]=="post" and not (0.78<=w/h<=1.01):
                raise RuntimeError("Feedformat ungeeignet")
        url="https://raw.githubusercontent.com/"+REPO+"/"+commit+"/"+quote(key,safe="/")
        for attempt in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"SchmidtMasterMedia/1"}),timeout=30) as r:
                    if r.status!=200 or hashlib.sha256(r.read()).hexdigest()!=digest:
                        raise RuntimeError("Remote-Datei stimmt nicht mit visuell geprüftem Original überein")
                break
            except Exception:
                if attempt==3:raise
                time.sleep(4)
        urls.append(url)
    return urls
def main():
    if os.getenv("GITHUB_REPOSITORY")!=REPO:raise RuntimeError("Falsches Repository")
    plan=json.loads(READY.read_text(encoding="utf8"))
    if plan.get("version")!=1 or plan.get("account")!="allianzschmidtdoebeln" or plan.get("timezone")!="Europe/Berlin":
        raise RuntimeError("Falscher Plan")
    manifest=load_manifest()
    org,ch=get_channel()
    posts=posts_from_buffer(org["id"],ch["id"])
    now=datetime.now(timezone.utc)
    active=sum(p.get("status") in ACTIVE for p in posts)
    blocked=set(manifest.get("rejected_buffer_ids",[]))
    allowed=manifest.get("grandfathered_separately_approved_posts",{})
    if any(p["id"] in blocked or p["id"] not in allowed for p in posts if p.get("status") in ACTIVE):
        raise RuntimeError("Aktive unbekannte/abgelehnte Queue-Einträge; zuerst aufklären")
    slots=sorted(plan["slots"],key=lambda x:parse(x["due_at"]))
    if len({parse(x["due_at"]) for x in slots})!=len(slots):raise RuntimeError("Doppelte Kalenderslots")
    commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    created=0;errors=[]
    for row in slots:
        d=parse(row["due_at"])
        if d<=now or d>now+HORIZON:continue
        existing=[p for p in posts if p.get("dueAt") and abs((parse(p["dueAt"])-d).total_seconds())<=120 and p.get("status") in ACTIVE|{"sent","error","failed"}]
        if row.get("buffer_id"):
            p=next((p for p in posts if p["id"]==row["buffer_id"]),None)
            if p and p["id"] in allowed and p["id"] not in blocked and p in existing and p.get("status") in ACTIVE|{"sent"}:
                note("MASTER BEREITS GEBUCHT: "+row["label"]+" "+p["id"]+" "+p["status"]);continue
            errors.append(row["label"]+" vorhandene ID fehlt/fehlerhaft – erst Zustand klären");continue
        if row.get("review_status")!="verified":
            note("MASTER BLOCKIERT / MEDIEN FEHLEN: "+row["due_at"]+" "+row["label"]);continue
        if existing:
            errors.append(row["label"]+" Slot bereits belegt – keine Doppelbuchung");continue
        if active>=MAX_QUEUE:
            note("MASTER MEDIENRESERVE – Buffer-Limit: "+row["label"]);continue
        try:
            urls=verify(row,manifest,commit)
            caption=row["caption"]
            if not caption:raise RuntimeError("Eindeutiger Begleittext fehlt")
            # Re-read before create, do not retry ambiguous POST results.
            latest=posts_from_buffer(org["id"],ch["id"])
            if any(p.get("dueAt") and abs((parse(p["dueAt"])-d).total_seconds())<=120 and p.get("status") in ACTIVE|{"sent","error","failed"} for p in latest):
                raise RuntimeError("Termin inzwischen belegt")
            if sum(p.get("status") in ACTIVE for p in latest)>=MAX_QUEUE:
                note("MASTER MEDIENRESERVE – Queue inzwischen voll: "+row["label"]);continue
            media=",".join("{image:{url:"+json.dumps(url)+"}}" for url in urls)
            meta="metadata:{instagram:{type:"+row["kind"]+",shouldShareToFeed:"+("true" if row["kind"]=="post" else "false")+",isAiGenerated:true}}"
            gql=("mutation {createPost(input:{text:"+json.dumps(caption,ensure_ascii=False)+
                ",channelId:"+json.dumps(ch["id"])+",schedulingType:automatic,mode:customScheduled,dueAt:"+json.dumps(d.isoformat().replace("+00:00","Z"))+
                ",assets:["+media+"],aiAssisted:true,"+meta+"}){... on PostActionSuccess{post{id status dueAt text assets{id mimeType}}} ... on MutationError{message}}}")
            result=query(gql).get("createPost",{})
            p=result.get("post") if isinstance(result,dict) else None
            if not p or p.get("status") not in ACTIVE|{"sent"} or not p.get("dueAt") or abs((parse(p["dueAt"])-d).total_seconds())>120 or len(p.get("assets") or [])!=len(urls):
                raise RuntimeError("Buchung nicht vollständig bestätigt; nicht blind erneut versuchen")
            row["buffer_id"]=p["id"];row["buffer_status"]=p["status"];row["booked_at"]=datetime.now(timezone.utc).isoformat()
            manifest.setdefault("grandfathered_separately_approved_posts",{})[p["id"]]=row["label"]+" (Master: tatsächlich visuell geprüft)"
            manifest.setdefault("specific_campaign_publication_notes",{})[p["id"]]={"due_at_utc":row["due_at"],"buffer_status":p["status"],"review_authority":row["review_authority"],"user_visual_approval":row.get("user_visual_approval",False),"assets":row["assets"]}
            save(READY,plan);save(MANIFEST,manifest)
            posts.append(p);active+=1;created+=1
            note("MASTER BUFFER GEBUCHT: "+row["label"]+" ID "+p["id"]+" STATUS "+p["status"]+" DUE "+str(p["dueAt"]))
        except Exception as e:
            errors.append(row["label"]+": "+str(e))
    note("MASTER NEU GEBUCHT: "+str(created)+" | Queue aktiv: "+str(active))
    for e in errors:note("MASTER FEHLER: "+e)
    if errors:raise SystemExit(1)
if __name__=="__main__":main()
