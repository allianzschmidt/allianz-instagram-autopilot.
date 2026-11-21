"""Exact-image correction for 21 Nov Kfz feed and Stories.
Use the user's actual uploaded square design, unchanged within Instagram sizes.
Replace scheduled earlier stylistic alternatives, never resurrect them.
"""
import hashlib,json,os,sys,time,urllib.request
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"assets"/"kfz_exact_user_image_2026_11_21"
WEB="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/kfz_exact_user_image_2026_11_21/"
MEDIA={
 "feed.jpg":"f2c552ede5125efe6ef67355aadb1b813b4d1512f5ccb7bbe7ab8921dac1cab6",
 "story.jpg":"05b1c2d7dfc23f56c01c42a49f3caa112d29dc4e9704b0080049f266983e4f06",
}
TAG="SCHMIDT_KFZ_USER_ORIGINAL_2026_11_21"
CAPTION=(
 "🚗 Kfz-Wechselsaison: Jetzt ein persönliches Angebot einholen!\n\n"
 "Der 30. November ist für viele Kfz-Versicherungen mit Hauptfälligkeit am 1. Januar "
 "der reguläre Kündigungsstichtag. Entscheidend ist aber immer der individuelle Vertragsablauf. "
 "Bei bestimmten Beitragserhöhungen können zusätzliche Kündigungsmöglichkeiten bestehen.\n\n"
 "Du möchtest wissen, welches Angebot zu deinem Auto und deinem Versicherungsbedarf passt? "
 "Wir beraten dich persönlich und unverbindlich.\n\n"
 "📩 Schreib uns „KFZ“ per Direktnachricht für dein persönliches Angebot.\n"
 "📍 Allianz Agentur Schmidt · Döbeln\n\n"
 "#KfzWechsel #KfzVersicherung #Autoversicherung #Döbeln #Mittelsachsen\n\n"+TAG+"_F1"
)
SLOTS=[
 ("S1","6b017160d9cbb430a13b30f6","2026-11-21T11:45:00.000Z","story","story.jpg",
   TAG+"_S1 | Jetzt Kfz-Angebot einholen. 30.11. bei vielen Verträgen beachten."),
 ("F1","6b017160dd205ed779d9ba15","2026-11-21T14:45:00.000Z","post","feed.jpg",CAPTION),
 ("S2","6b017160d9cbb430a13b3159","2026-11-21T17:45:00.000Z","story","story.jpg",
   TAG+"_S2 | Angebot einholen: Kfz-Versicherung im November ansehen."),
 ("S3","6b01716120a2d09a0af0cc69","2026-11-21T19:45:00.000Z","story","story.jpg",
   TAG+"_S3 | Nachricht mit KFZ schicken für ein unverbindliches Angebot.")
]
def verify(name):
    b=(FOLDER/name).read_bytes()
    if len(b)<120000 or b[:3]!=b"\xff\xd8\xff" or hashlib.sha256(b).hexdigest()!=MEDIA[name]:
        raise RuntimeError("Die Datei entspricht nicht dem Bild des Nutzers: "+name)
    req=urllib.request.Request(WEB+name,headers={"User-Agent":"Schmidt-Kfz-Exact-User-Original/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=35) as response:
                if response.status!=200 or response.read(3)!=b"\xff\xd8\xff":
                    raise RuntimeError("Media not readable")
            break
        except Exception:
            if attempt==3:raise
            time.sleep(5)
    return WEB+name

def main():
    if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Repository verwechselt")
    if os.getenv("EXACT_DESIGN_RELEASE")!="user-supplied-blue-vw-golf-exact-poster-nov21":
        raise RuntimeError("Exakte Motivfreigabe fehlt")
    urls={name:verify(name) for name in MEDIA}
    org,ch=get_channel()
    actual=ch["name"].strip().lstrip("@").lower()
    link=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
    if actual!=HANDLE and link!=HANDLE:
        raise RuntimeError("Falsches Instagram-Ziel")
    posts=posts_from_buffer(org["id"],ch["id"])
    now=datetime.now(timezone.utc)
    print("EXAKT VOM NUTZER HOCHGELADENES DESIGN; KANAL @"+HANDLE)
    problems=[]
    for code,old_id,due,kind,name,caption in SLOTS:
        marker=TAG+"_"+code
        seen=[p for p in posts if marker in (p.get("text") or "")]
        if seen:
            p=seen[0]
            if p.get("status") in ("scheduled","buffer","sending","sent"):
                print("EXAKTES ORIGINAL BEREITS VORHANDEN:",code,p.get("id"),p.get("status"))
                continue
            problems.append("Alte exakte Kopie im falschen Zustand: "+str(p))
            continue
        previous=next((p for p in posts if p.get("id")==old_id),None)
        if previous is None:
            problems.append(code+" alte Booking ID unbekannt, keine riskante Doppelbuchung")
            continue
        state=previous.get("status")
        if state in ("sent","sending"):
            print("VORHERIGES DESIGN SCHON VERÖFFENTLICHT; NICHT AUSWECHSELBAR:",code,old_id,state)
            problems.append(code+" konnte nicht vor Veröffentlichung ersetzt werden.")
            continue
        if state in ("buffer","scheduled"):
            mutation=("mutation {editPost(input:{id:"+json.dumps(old_id)+
                      ",saveToDraft:true}){... on PostActionSuccess{post{id status dueAt}} ... on MutationError{message}}}")
            result=query(mutation).get("editPost",{})
            if not isinstance(result,dict) or result.get("post",{}).get("status")!="draft":
                problems.append("Altes Motiv lässt sich nicht stoppen: "+code+" "+str(result))
                continue
            previous["status"]="draft"
            print("SCHLECHTERE VARIANTE IN ENTWÜRFE VERSCHOBEN:",code,old_id)
        elif state!="draft":
            problems.append("Abweichender Altstatus "+code+" "+str(state));continue
        if any(p.get("dueAt")==due and p.get("status") in ("scheduled","buffer","sending") for p in posts):
            problems.append("Doppelbelegung des Termins "+code);continue
        when=datetime.fromisoformat(due.replace("Z","+00:00"))
        mode="customScheduled" if now<when else "shareNow"
        extra=",dueAt:"+json.dumps(due) if mode=="customScheduled" else ""
        metadata="metadata:{instagram:{type:"+kind+",shouldShareToFeed:"+("true" if kind=="post" else "false")+",isAiGenerated:false}}"
        gql=("mutation {createPost(input:{text:"+json.dumps(caption,ensure_ascii=False)
             +",channelId:"+json.dumps(ch["id"])
             +",schedulingType:automatic,mode:"+mode+extra
             +",assets:[{image:{url:"+json.dumps(urls[name])+"}}]"
             +",aiAssisted:false,"+metadata+
             "}) {... on PostActionSuccess{post{id status dueAt text assets{id mimeType}}} ... on MutationError{message}}}")
        response=query(gql).get("createPost",{})
        if not isinstance(response,dict) or not response.get("post"):
            problems.append("Buffer verweigert Originalmotiv "+code+" "+str(response));continue
        p=response["post"]
        if p.get("status") not in ("scheduled","buffer","sending","sent") or len(p.get("assets") or [])!=1:
            problems.append("Buffer meldet unvollständige Buchung "+code+" "+str(p));continue
        posts.append(p)
        print("NUTZERORIGINAL BUFFER:",code,p.get("id"),"STATUS:",p.get("status"),"DUE:",p.get("dueAt"),"MODE:",mode)
    if problems:
        for p in problems:print("FEHLER ERSATZ:",p)
        raise RuntimeError("Nicht alle geplanten Motive erfolgreich ersetzt")
    print("ALLE VIER KFZ-TERMINE ENTHALTEN JETZT DAS EXAKTE NUTZER-DESIGN.")
if __name__=="__main__":
    main()
