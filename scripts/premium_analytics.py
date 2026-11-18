"""Weekly report for the real Instagram premium campaigns, not rejected drafts."""
import sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer
from premium_publish import items

def main():
    org,ch=get_channel()
    posts=posts_from_buffer(org["id"],ch["id"],with_metrics=True)
    now=datetime.now(timezone.utc)
    start=now-timedelta(days=7)
    future=now+timedelta(days=7)
    premium=items()
    summary=[]
    def add(s):
        print(s)
        summary.append(s)
    add("# Allianz Agentur Schmidt – Instagram Premium Wochenbericht")
    add("Kanal: @allianzschmidtdoebeln | Aktualisiert: "+now.isoformat())
    latest=[]
    for p in posts:
        if not p.get("dueAt"):continue
        try:due=datetime.fromisoformat(p["dueAt"].replace("Z","+00:00"))
        except ValueError:continue
        if not(start<=due<=now and p.get("status")=="sent"):continue
        metrics=p.get("metrics") or []
        data={m.get("type",m.get("name","?")):m.get("value") for m in metrics}
        latest.append((due,p,data))
    add("## Letzte sieben Tage – tatsächlicher Buffer-Status")
    for due,p,metrics in sorted(latest,reverse=True):
        caption=(p.get("text") or "").replace("\n"," ")[:85]
        add("- "+due.isoformat()+" | sent | "+caption+" | "+str(metrics or "Noch keine Insights verfügbar"))
    if not latest:add("- Keine bestätigten Postings aus den letzten sieben Tagen.")
    add("## Kommende sieben Tage – in Buffer geprüft")
    upcoming=[]
    for item in premium:
        due=item["due"]
        if not(now<=due<=future):continue
        candidate=None
        for p in posts:
            if not p.get("dueAt"):continue
            try:t=datetime.fromisoformat(p["dueAt"].replace("Z","+00:00"))
            except ValueError:continue
            if abs((t-due).total_seconds())<120:
                candidate=p;break
        status=candidate.get("status") if candidate else ("NOCH NICHT FAELLIG ZUR VORPLANUNG" if due>now+timedelta(hours=43) else "MISSING")
        upcoming.append(status)
        add("- "+due.isoformat()+" | "+item["label"]+" | "+status)
    add("Kommende Premium-Termine: "+str(len(upcoming))+
        " / davon sicher geplant: "+str(sum(s in ("scheduled","buffer","sending","sent") for s in upcoming)))
    add("Hinweis: Fehlende Insights bedeuten keine Reichweite von null. Buffer-Status sent ist nicht unabhängig die öffentliche Instagram-URL.")
    from os import environ
    path=environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path,"a",encoding="utf8") as f:f.write("\n".join(summary)+"\n")
if __name__=="__main__":
    main()
