"""Account-level Buffer comparison, no invented or missing-as-zero metrics."""
import sys,json
from collections import Counter,defaultdict
from datetime import datetime,timezone,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,note
from visual_quality_gate import load_manifest
from premium_publish import items
ROOT=Path(__file__).resolve().parents[1]
BERLIN=ZoneInfo("Europe/Berlin")
def parse(s):return datetime.fromisoformat(s.replace("Z","+00:00")) if s else None
def main():
    org,ch=get_channel()
    now=datetime.now(timezone.utc)
    posts=posts_from_buffer(org["id"],ch["id"],with_metrics=True)
    known=load_manifest().get("grandfathered_separately_approved_posts",{})
    reports=[]
    for label,start,end in [("AKTUELL",now-timedelta(days=7),now),("VORPERIODE",now-timedelta(days=14),now-timedelta(days=7))]:
        subset=[]
        states=Counter()
        for p in posts:
            try:d=parse(p.get("dueAt"))
            except ValueError:continue
            if not d or not start<=d<end:continue
            if p.get("status") not in ("sent","failed","error","scheduled","buffer","sending"):continue
            states[p["status"]]+=1
            if p["status"]!="sent":continue
            metrics={}
            for m in p.get("metrics") or []:
                val=m.get("value")
                if isinstance(val,(float,int)) and not isinstance(val,bool):
                    metrics[str(m.get("type") or m.get("name"))]=val
            subset.append((d,p,metrics))
        sums=defaultdict(list)
        for _,_,metrics in subset:
            for k,v in metrics.items():sums[k].append(v)
        agg={k:{"observations":len(v),"mean":round(sum(v)/len(v),2),"sum_per_post":round(sum(v),2)} for k,v in sorted(sums.items())}
        note("ANALYTICS "+label+" "+start.isoformat()+" bis "+end.isoformat()+" | Status "+str(dict(states))+" | sent "+str(len(subset)))
        for d,p,m in sorted(subset,key=lambda x:x[0],reverse=True):
            note("POST "+label+" "+d.astimezone(BERLIN).isoformat()+" | "+p["id"]+" | "+("Register" if p["id"] in known else "Herkunft separat prüfen")+" | "+(p.get("text") or known.get(p["id"],"Story/ohne Text"))[:100].replace("\n"," ")+" | "+json.dumps(m,ensure_ascii=False)+" | metricsUpdatedAt "+str(p.get("metricsUpdatedAt")))
        note("METRIKEN "+label+" "+json.dumps(agg,ensure_ascii=False)+" (Summen je Post sind keine deduplizierte Account-Reichweite)")
        reports.append((subset,agg,states))
    cur,prev=reports
    note("VERGLEICH SENT: "+str(len(cur[0]))+" vs "+str(len(prev[0])))
    for k in sorted(set(cur[1])|set(prev[1])):
        a,b=cur[1].get(k),prev[1].get(k)
        if a and b:
            note("VERGLEICH "+k+" Mittel je gemessenem Beitrag: "+str(a["mean"])+" vs "+str(b["mean"])+" | Abdeckung "+str(a["observations"])+"/"+str(len(cur[0]))+" vs "+str(b["observations"])+"/"+str(len(prev[0])))
        else:note("VERGLEICH "+k+": keine beidseitige Datenbasis")
    ranking=[]
    for d,p,m in cur[0]:
        if "reach" in m:ranking.append((m["reach"],p["id"],known.get(p["id"],(p.get("text") or "")[:80])))
    if ranking:note("RANKING NUR BEITRAEGE MIT REACH: "+json.dumps(sorted(ranking,reverse=True)[:5],ensure_ascii=False))
    else:note("Kein belastbares Reach-Ranking; keine Messwerte als Null ausgeben.")
    note("Followerentwicklung, Nicht-Follower-Reichweite, Profilaufrufe, Klicks, Watchtime, Anfragen nur soweit tatsächlich als verfügbare Messdaten geliefert; fehlende Werte sind unbekannt.")
    active=[p for p in posts if p["status"] in ("scheduled","buffer","sending")]
    note("QUEUE AKTIV "+str(len(active))+" | "+json.dumps([(p["id"],p.get("dueAt"),p["status"]) for p in active]))
    note("Empfehlung bei geringer Datenabdeckung: erst regelmäßig veröffentlichen und Formate vergleichbar testen; keine angeblichen Bestzeiten aus unzureichenden Daten ableiten.")
if __name__=="__main__":main()
