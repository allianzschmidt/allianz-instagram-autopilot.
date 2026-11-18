"""Entfernt ausschließlich die vier vom Nutzer verworfenen Premium-Schablonen-Beiträge
aus der Instagram-Zeitplanung, ohne sie endgültig zu löschen.

Unberührt: Buß-und-Bettag-Fotobeitrag, zuvor freigegebene Einkommensschutz-
und Starkregen-Beiträge, alle anderen Buffer-Kanäle.
"""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE
IDS={
"6afce982f0c5ce9361ab4ef4": "18.11. 18:30 Zahnzusatz Standard-Karussell",
"6afce983ab47737bddb3c4f8": "18.11. 20:15 Zahnzusatz Standard-Story",
"6afce983ab47737bddb3c51e": "19.11. 08:30 Einkommensschutz Standard-Story",
"6afcf087ab47737bddb698da": "19.11. 20:15 Einkommensschutz Standard-Story"
}
def main():
    org,ch=get_channel()
    if ch["name"].strip().lstrip("@").lower()!=HANDLE:
        link=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
        if link!=HANDLE:raise RuntimeError("Falscher Kanal")
    posts={p["id"]:p for p in posts_from_buffer(org["id"],ch["id"])}
    failures=[]
    for post_id,name in IDS.items():
        p=posts.get(post_id)
        if not p:
            failures.append(name+" | unbekannte ID");continue
        status=p.get("status")
        if status=="draft":
            print("BEREITS SICHER IM ENTWURF:",name,post_id);continue
        if status=="sent":
            print("BEREITS VERÖFFENTLICHT: Nicht rückwirkend änderbar:",name,post_id)
            continue
        if status not in ("buffer","scheduled"):
            failures.append(name+" | unerwarteter Status "+str(status));continue
        gql="mutation {editPost(input:{id:"+json.dumps(post_id)+",saveToDraft:true}) {... on PostActionSuccess {post{id status dueAt}} ... on MutationError{message}}}"
        data=query(gql).get("editPost")
        if not isinstance(data,dict) or "post" not in data:
            failures.append(name+" | Buffer Fehler "+str(data));continue
        if data["post"].get("status")!="draft":
            failures.append(name+" | nach Edit nicht draft "+str(data["post"]));continue
        print("AUS QUEUE ENTFERNT, ALS ENTWURF GESPEICHERT:",name,post_id)
    refreshed={p["id"]:p for p in posts_from_buffer(org["id"],ch["id"])}
    for post_id,name in IDS.items():
        p=refreshed.get(post_id)
        if p and p.get("status") in ("scheduled","buffer","sending"):
            failures.append(name+" | weiter zur Veröffentlichung eingeplant: "+p["status"])
    print("UNBERÜHRT: Buß- und Bettag 12:00, Einkommensschutz 19.11. 12:30, Starkregen 26.11. 12:30")
    if failures:raise RuntimeError("Nicht vollständig gestoppt:\n"+"\n".join(failures))
    print("Alle noch geplanten abgelehnten Schablonen-Medien wurden in Entwürfe verschoben.")
if __name__=="__main__":main()
