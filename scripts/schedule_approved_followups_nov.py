"""Nur einzeln bereits gezeigte und freigegebene Premium-Instagram-Medien für Nov. 2026.
Keine Allianz-Logos, keine neuen Themen, keine verworfenen Designs oder KI-Avatare.
Der allgemeine alte 30er-Entwurfs-Publisher bleibt AUS.
"""
import json,os,sys,urllib.request,time
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query

ROOT=Path(__file__).resolve().parents[1]
PREFIX="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/approved_followups_nov/"
POSTS=[
    {
     "id":"2026-11-13-water-story",
     "date":"2026-11-13T19:15:00.000Z",
     "format":"story",
     "files":["water_story.png"],
     "caption":""
    },
    {
     "id":"2026-11-14-key-story",
     "date":"2026-11-14T07:30:00.000Z",
     "format":"story",
     "files":["key_story.png"],
     "caption":""
    },
    {
     "id":"2026-11-19-income",
     "date":"2026-11-19T11:30:00.000Z",
     "format":"post",
     "files":["income.png"],
     "caption":(
      "Einkommen weg – was schützt dich dann? ⏳\n\n"
      "Deine laufenden Kosten bleiben, auch wenn du aus gesundheitlichen Gründen "
      "deinen Beruf langfristig nicht mehr ausüben kannst.\n\n"
      "Eine Berufsunfähigkeitsversicherung kann je nach Vertrag und Leistungsfall "
      "eine monatliche Rente vorsehen. Wichtig sind dabei insbesondere die "
      "Definition von Berufsunfähigkeit, Ausschlüsse, Gesundheitsangaben und die Höhe der Absicherung.\n\n"
      "📍 Allianz Agentur Schmidt · Döbeln\n"
      "💬 Schreib uns, wenn du deinen Einkommensschutz prüfen möchtest.\n\n"
      "#Berufsunfähigkeit #Einkommensschutz #Versicherungswissen #Döbeln"
     )
    },
    {
     "id":"2026-11-26-starkregen",
     "date":"2026-11-26T11:30:00.000Z",
     "format":"post",
     "files":["starkregen.png"],
     "caption":(
      "Starkregen? Ist dein Zuhause vorbereitet? 🌧️\n\n"
      "Überschwemmung und Rückstau können große Schäden verursachen. "
      "Ein normaler Wohngebäude- oder Hausratvertrag umfasst solche Naturgefahren "
      "nicht automatisch – oft braucht es einen passenden Elementarschutz.\n\n"
      "Ob und in welchem Umfang Versicherungsschutz besteht, hängt von den "
      "vereinbarten Bedingungen und der Schadenursache ab.\n\n"
      "📍 Allianz Agentur Schmidt · Döbeln\n"
      "💬 Lass deinen Schutz gegen Naturgefahren überprüfen.\n\n"
      "#Starkregen #Elementarschutz #Wohngebäude #Hausrat #Döbeln"
     )
    }
]
def verify_url(url):
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Schmidt-Premium-Feed/1.0"}),timeout=35) as response:
                signature=response.read(8)
                if response.status!=200 or signature!=b"\x89PNG\r\n\x1a\n":
                    raise RuntimeError("Media is not PNG")
            return
        except Exception:
            if attempt==5:raise
            time.sleep(4)
def schedule():
    if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Falsches Repository")
    if os.getenv("CONFIRMED_MEDIA_RELEASE")!="premium-previously-approved-nov-2026":
        raise RuntimeError("Spezifische Inhaltsfreigabe fehlt")
    if not os.getenv("BUFFER_API_KEY"): raise RuntimeError("BUFFER_API_KEY fehlt")
    org,ch=get_channel()
    seen=posts_from_buffer(org["id"],ch["id"])
    for post in POSTS:
        if datetime.fromisoformat(post["date"].replace("Z","+00:00"))<datetime.now(timezone.utc):
            print("TERMIN VERGANGEN, NICHT SPÄT VERÖFFENTLICHEN:",post["id"])
            continue
        existing=[p for p in seen if p.get("dueAt")==post["date"]]
        if existing:
            old=existing[0]
            if old.get("status") in ("scheduled","buffer","sending","sent") and (
                 not post["caption"] or (old.get("text") or "")==post["caption"]
            ):
                print("BEREITS EINGEPLANT:",post["id"],old.get("id"),old.get("status"))
                continue
            raise RuntimeError("Konflikt mit bereits vorhandenem Post zum Termin "+post["date"])
        for file in post["files"]:
            data=(ROOT/"assets"/"approved_followups_nov"/file).read_bytes()
            if len(data)<30000 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise RuntimeError("Kein geprüftes Originalmedium: "+file)
        urls=[PREFIX+name for name in post["files"]]
        for url in urls:verify_url(url)
        assets=",".join("{image:{url:"+json.dumps(u)+"}}" for u in urls)
        is_story=(post["format"]=="story")
        metadata="metadata:{instagram:{type:" + ("story" if is_story else "post") + (
              ",shouldShareToFeed:false" if is_story else ",shouldShareToFeed:true"
            ) + ",isAiGenerated:true}}"
        gql=("mutation {createPost(input:{text:"+json.dumps(post["caption"],ensure_ascii=False)
           +",channelId:"+json.dumps(ch["id"])
           +",schedulingType:automatic,mode:customScheduled,dueAt:"+json.dumps(post["date"])
           +",assets:["+assets+"],aiAssisted:true,"+metadata
           +"}){... on PostActionSuccess {post{id dueAt status text}} ... on MutationError{message}}}")
        res=query(gql).get("createPost",{})
        if not isinstance(res,dict) or "post" not in res:
            raise RuntimeError("BUFFER LEHNT AB "+post["id"]+": "+str(res))
        data=res["post"]
        if data.get("dueAt")!=post["date"]:
            raise RuntimeError("Buffer-Termin-Abweichung "+post["id"]+" -> "+str(data))
        print("BUFFER FEST GEPLANT:",post["id"],"ID:",data.get("id"),"STATUS:",data.get("status"),"UTC:",data.get("dueAt"))
        seen.append(data)
if __name__=="__main__":
    try:schedule()
    except Exception as exc:
        print("NICHT ALS ERFOLGREICH BESTÄTIGT:",str(exc),file=sys.stderr)
        raise
