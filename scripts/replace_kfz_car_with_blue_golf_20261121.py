"""Replace four *scheduled* 21 Nov Kfz campaign posts with the user's selected blue VW Golf.

Each replacement is the EXACT new premium image verified by SHA256.
Never replace already sent posts or modify another Instagram channel.
Old scheduled items -> drafts. New items use the identical intended local slots.
"""
import hashlib,json,os,sys,time,urllib.request
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"assets"/"kfz_golf_2026_11_21"
WEB="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/kfz_golf_2026_11_21/"
MEDIA={
 "feed.jpg":"771d568a519cd981af395215833266f07b3ba745af647329bd0c1a650e9bdc0c",
 "story_1.jpg":"58fe7f789e735bfe12a29b19e306f8a2ad8ef34673e9df7ab150c45e474d0cfc",
 "story_2.jpg":"0c7766097dd9f2368af9f0fd0c9a63549a00a7071f3a43d5c38273cd506405f4",
 "story_3.jpg":"401b083867b9d44afdd7d792b88c0207ebedd1e24b8c3b0cbc1c68e6eda20847",
}
TAG="SCHMIDT_GOLF_KFZ_2026_11_21"
FEED_CAPTION=(
 "🚗 Kfz-Wechselsaison 2026: Jetzt ein persönliches Angebot einholen!\n\n"
 "Für viele Kfz-Verträge mit Hauptfälligkeit zum 1. Januar ist der 30. November "
 "der reguläre Kündigungsstichtag. Die Kündigung muss rechtzeitig beim bisherigen "
 "Versicherer eingehen. Bei anderen Hauptfälligkeiten gelten andere Termine; "
 "auch Sonderkündigungsrechte sind je nach Situation möglich.\n\n"
 "Du möchtest wissen, was eine Kfz-Versicherung für dein Auto kosten würde? "
 "Schreib uns eine Direktnachricht mit „KFZ“ und wir sprechen über dein unverbindliches Angebot.\n\n"
 "📍 Allianz Agentur Schmidt · Döbeln\n"
 "#KfzVersicherung #KfzWechsel #Autoversicherung #Döbeln #Mittelsachsen\n\n"+TAG+"_F1"
)
SLOTS=[
 ("S1","6b0168fc9ffbc8503c151cae","2026-11-21T11:45:00.000Z","story","story_1.jpg",
  TAG+"_S1 | Kfz-Wechselsaison: Jetzt unverbindliches Angebot einholen."),
 ("F1","6b0168fd5e993799d86a43fb","2026-11-21T14:45:00.000Z","post","feed.jpg",FEED_CAPTION),
 ("S2","6b0168fd20a2d09a0aecef43","2026-11-21T17:45:00.000Z","story","story_2.jpg",
  TAG+"_S2 | Drei Angaben für dein Kfz-Angebot: Fahrzeugdaten, SF-Klasse, Fahrleistung."),
 ("S3","6b0168fd9ffbc8503c151d0d","2026-11-21T19:45:00.000Z","story","story_3.jpg",
  TAG+"_S3 | Schreib uns KFZ per Nachricht für ein unverbindliches Angebot.")
]

def preflight():
  for file,sha in MEDIA.items():
    p=FOLDER/file
    b=p.read_bytes()
    if len(b)<100000 or b[:3]!=b"\xff\xd8\xff" or hashlib.sha256(b).hexdigest()!=sha:
      raise RuntimeError("Unzulässiges oder verändertes Original: "+file)
    for attempt in range(4):
      try:
        r=urllib.request.Request(WEB+file,headers={"User-Agent":"SchmidtGolfReplacement/1.0"})
        with urllib.request.urlopen(r,timeout=30) as response:
          if response.status!=200 or response.read(3)!=b"\xff\xd8\xff":
            raise RuntimeError("Original nicht öffentlich abrufbar: "+file)
        break
      except Exception:
        if attempt==3:raise
        time.sleep(4)
    print("GEPRÜFTES GOLF-ORIGINAL:",file,sha)

def run():
  raise RuntimeError("ALTEN GOLF-ERSATZ NICHT ERNEUT AKTIVIEREN. Der Nutzer hat explizit das hochgeladene Posterdesign ausgewaehlt, das jetzt in vier Buffer-Slots gebucht ist.")
  if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
    raise RuntimeError("Falsches Repository")
  if os.getenv("GOLF_RELEASE")!="user-reference-blue-vw-golf-replacement-21nov2026":
    raise RuntimeError("Einmalige konkrete Nutzerfreigabe fehlt")
  preflight()
  org,ch=get_channel()
  if ch["name"].strip().lstrip("@").lower()!=HANDLE and (
      (ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()!=HANDLE):
    raise RuntimeError("Falscher Instagramkanal")
  print("NUR KANAL @"+HANDLE)
  posts=posts_from_buffer(org["id"],ch["id"])
  now=datetime.now(timezone.utc)
  errors=[]
  for code,old_id,due,kind,file,caption in SLOTS:
    if any((TAG+"_"+code) in (p.get("text") or "") and p.get("status") in
           ("scheduled","buffer","sending","sent") for p in posts):
      print("GOLF ERSATZ BEREITS GEBUCHT:",code)
      continue
    old=next((p for p in posts if p.get("id")==old_id),None)
    if not old:
      errors.append(code+" ursprünglicher Post nicht gefunden; keine Doppelbuchung")
      continue
    status=old.get("status")
    if status=="sent" or status=="sending":
      print("NICHT ERSETZBAR, BEREITS VERÖFFENTLICHT / SENDING:",code,old_id,status)
      continue
    if status in ("scheduled","buffer"):
      gql=("mutation {editPost(input:{id:"+json.dumps(old_id)+",saveToDraft:true}) "
           "{... on PostActionSuccess{post{id status dueAt}} ... on MutationError{message}}}")
      result=query(gql).get("editPost",{})
      if not isinstance(result,dict) or result.get("post",{}).get("status")!="draft":
        errors.append(code+" konnte nicht sicher als Entwurf gespeichert werden: "+str(result))
        continue
      old["status"]="draft"
      print("ALTER KFZ-BEITRAG AUS DER QUEUE ENTFERNT:",code,old_id)
    elif status!="draft":
      errors.append(code+" unbekannter alter Status: "+str(status));continue
    if any(p.get("dueAt")==due and p.get("status") in ("scheduled","buffer","sending")
           for p in posts):
      errors.append(code+" Zeitkollision mit anderem Beitrag");continue
    target=datetime.fromisoformat(due.replace("Z","+00:00"))
    if now>=target:
      mode="shareNow";extra=""
    else:
      mode="customScheduled";extra=",dueAt:"+json.dumps(due)
    media="{image:{url:"+json.dumps(WEB+file)+"}}"
    meta="metadata:{instagram:{type:"+kind+",shouldShareToFeed:"+("true" if kind=="post" else "false")+",isAiGenerated:true}}"
    gql=("mutation {createPost(input:{text:"+json.dumps(caption,ensure_ascii=False)
       +",channelId:"+json.dumps(ch["id"])+",schedulingType:automatic,mode:"+mode+extra
       +",assets:["+media+"],aiAssisted:true,"+meta
       +"}) {... on PostActionSuccess{post{id status dueAt text assets{id mimeType}}} ... on MutationError{message}}}")
    new=query(gql).get("createPost",{})
    if not isinstance(new,dict) or not new.get("post"):
      errors.append(code+" Buffer hat Ersatz nicht angenommen: "+str(new));continue
    p=new["post"]
    if p.get("status") not in ("scheduled","buffer","sending","sent") or len(p.get("assets") or [])!=1:
      errors.append(code+" Buffer meldet unerwartetes Ergebnis: "+str(p));continue
    posts.append(p)
    print("GOLF-ERSATZ BUFFER:",code,"ID",p["id"],"STATUS",p["status"],"DUE",p.get("dueAt"),"MODE",mode)
  if errors:
    for item in errors:print("GOLF-ERSATZ-PROBLEM:",item)
    raise RuntimeError("Nicht alle ursprünglichen Beiträge sicher ersetzt")
  print("Alle noch änderbaren KFZ-Posts wurden durch normale VW-Golf-Motive ersetzt.")
if __name__=="__main__":
  run()
