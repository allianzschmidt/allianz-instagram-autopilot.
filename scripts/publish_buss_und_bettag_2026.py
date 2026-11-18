"""Einmaliger, werbefreier Feiertagsbeitrag für Buß- und Bettag 18.11.2026.

Logo-frei, nur die ausgeschriebene Agenturbezeichnung. Keine Änderung an
bestehenden Buffer-Terminen (Zahnzusatz-Karussell und Stories bleiben).
"""
import json
import os
import sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query

EVENT_ID="schmidt-feiertag-buss-bettag-2026"
DUE="2026-11-18T11:00:00.000Z"  # 12:00 Europe/Berlin
IMAGE="assets/community/buss_und_bettag_2026.png"
URL="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/"+IMAGE
CAPTION=(
    "Heute ist Buß- und Bettag. 🍂\n\n"
    "Ein Tag, der uns daran erinnern kann, innezuhalten, nachzudenken "
    "und den Alltag für einen Moment etwas ruhiger anzugehen.\n\n"
    "Besonders für uns in Sachsen hat dieser Tag einen festen Platz "
    "im Kalender, denn hier ist er gesetzlicher Feiertag.\n\n"
    "Wir wünschen euch einen ruhigen Tag und Zeit für das, "
    "was euch wichtig ist.\n\n"
    "Eure Allianz Agentur Schmidt aus Döbeln 💙\n\n"
    "#BußUndBettag #Sachsen #Döbeln #Mittelsachsen #Feiertag"
)
def run():
    if os.environ.get("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Falsches Repository")
    if os.environ.get("HOLIDAY_RELEASE")!="buss-bettag-2026-approved":
        raise RuntimeError("Feiertags-Medienfreigabe fehlt")
    image=(Path(__file__).resolve().parents[1]/IMAGE).read_bytes()
    if len(image)<50000 or image[:8]!=b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("Originalbild fehlt oder ist keine PNG-Datei")
    org,ch=get_channel()
    posts=posts_from_buffer(org["id"],ch["id"])
    for p in posts:
        if "Heute ist Buß- und Bettag." in (p.get("text") or ""):
            print("BEREITS IN BUFFER:",p.get("id"),p.get("status"),p.get("dueAt"))
            return
    due=datetime.fromisoformat(DUE.replace("Z","+00:00"))
    if datetime.now(timezone.utc)>due:
        raise RuntimeError("Feiertags-Termin liegt schon zurück, keine verspätete Veröffentlichung")
    # No conflict with the already approved dental content / stories.
    collision=[p for p in posts if p.get("dueAt")==DUE and p.get("status")!="sent"]
    if collision:raise RuntimeError("Ein anderer Beitrag ist schon zum Termin gebucht; keine Änderung")
    from urllib.request import Request,urlopen
    with urlopen(Request(URL,headers={"User-Agent":"Schmidt-Feiertag/1.0"}),timeout=35) as response:
        if response.status!=200 or response.read(8)!=b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("Feiertagsmotiv noch nicht abrufbar")
    gql=("mutation {createPost(input:{text:"+json.dumps(CAPTION,ensure_ascii=False)+
         ",channelId:"+json.dumps(ch["id"])+
         ",schedulingType:automatic,mode:customScheduled,dueAt:"+json.dumps(DUE)+
         ",assets:[{image:{url:"+json.dumps(URL)+"}}],aiAssisted:true,"+
         "metadata:{instagram:{type:post,shouldShareToFeed:true,isAiGenerated:true}}"+
         "}){... on PostActionSuccess{post{id status dueAt text}} ... on MutationError{message}}}")
    r=query(gql).get("createPost",{})
    if not isinstance(r,dict) or "post" not in r:
        raise RuntimeError("BUFFER HAT FEIERTAGSPOST NICHT ANGENOMMEN: "+str(r))
    p=r["post"]
    print("BUFFER FEIERTAGSBEITRAG:",EVENT_ID,"ID:",p.get("id"),
          "STATUS:",p.get("status"),"DUE:",p.get("dueAt"),
          "ACCOUNT:@allianzschmidtdoebeln")
    if p.get("dueAt")!=DUE or p.get("status") not in ("scheduled","buffer","sending"):
        raise RuntimeError("Buffer hat anderen Termin oder unerwarteten Status angenommen")
if __name__=="__main__":
    run()
