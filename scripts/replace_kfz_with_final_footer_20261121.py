"""Apply only user's latest explicit Kfz image approval to today's two remaining slots.
21 November 2026: FEED 15:45 CET, ONE STORY 20:45 CET.
Do not requeue canceled daytime Stories; do not alter other accounts.
"""
import hashlib,json,os,sys,time,urllib.request
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"assets/kfz_final_footer_20261121"
BASE="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/kfz_final_footer_20261121/"
MEDIA={
 "feed.jpg":"4dc56fd371dd87364d7d0cac460bb17d50d8f188340070c6d096d6ed8452e420",
 "story.jpg":"50ff5c86098242fc0e6e39d42cb87b4acc21c912b8d51e8f0045c21a5d326ba0"
}
TAG="SCHMIDT_KFZ_FOOTER_USER_APPROVED_20261121"
CAPTION=(
 "🚗 Kfz-Wechselsaison: Jetzt persönliches Angebot einholen!\n\n"
 "Für viele Kfz-Verträge mit Hauptfälligkeit zum 1. Januar ist der "
 "30. November der reguläre Kündigungsstichtag. Entscheidend ist der individuelle "
 "Vertrag und der rechtzeitige Zugang der Kündigung beim bisherigen Versicherer. "
 "Je nach Situation kann ein Sonderkündigungsrecht bestehen.\n\n"
 "Wir beraten persönlich und unverbindlich zu deinem Kfz-Versicherungsschutz.\n"
 "📩 Schreib uns „KFZ“ per Direktnachricht und hole ein Angebot ein.\n"
 "📍 Allianz Agentur Schmidt · Döbeln\n\n"
 "#KfzWechsel #KfzVersicherung #Autoversicherung #Döbeln #Mittelsachsen\n\n"+TAG+"_F1"
)
SLOTS=[
 ("F1","6b01732a510276624515cf54","2026-11-21T14:45:00.000Z","post","feed.jpg",CAPTION),
 ("S3","6b01732b9ffbc8503c195f78","2026-11-21T19:45:00.000Z","story","story.jpg",
   TAG+"_S3 | 20:45 Uhr: Kfz-Wechselsaison, jetzt Angebot einholen. Allianz Agentur Schmidt · Döbeln.")
]
CANCELLED=["6b01732add205ed779da6602","6b01732b20a2d09a0af16e8c"]
def check_file(name,sha):
 b=(FOLDER/name).read_bytes()
 if len(b)<100000 or b[:3]!=b"\xff\xd8\xff" or hashlib.sha256(b).hexdigest()!=sha:
  raise RuntimeError("FALSCHE BILDDATEI: "+name)
 url=BASE+name
 for attempt in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"SchmidtFinalKfz/1.0"})
   with urllib.request.urlopen(req,timeout=35) as resp:
    if resp.status!=200 or resp.read(3)!=b"\xff\xd8\xff":
     raise RuntimeError("Nicht erreichbares JPEG: "+name)
   break
  except Exception:
   if attempt==3:raise
   time.sleep(4)
 return url
def main():
 if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
  raise RuntimeError("Falsches Repository")
 if os.getenv("FINAL_IMAGE_RELEASE")!="user-approved-footer-feed-story-nov21":
  raise RuntimeError("Keine spezifische Freigabe")
 urls={k:check_file(k,v) for k,v in MEDIA.items()}
 org,ch=get_channel()
 name=ch["name"].strip().lstrip("@").lower()
 link=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
 if name!=HANDLE and link!=HANDLE:
  raise RuntimeError("Falscher Instagram-Kanal")
 posts=posts_from_buffer(org["id"],ch["id"])
 # Fail closed if previously canceled Stories somehow returned.
 for p in posts:
  if p.get("id") in CANCELLED and p.get("status") in ("scheduled","buffer","sending"):
   raise RuntimeError("Abbestellte zusätzliche Kfz-Story wurde wieder aktiviert: "+p.get("id"))
 print("KORREKTER KANAL @"+HANDLE+"; nur Feed und eine Story")
 errors=[]
 for code,previous_id,due,kind,file,caption in SLOTS:
  existing=[p for p in posts if (TAG+"_"+code) in (p.get("text") or "")]
  if existing:
   p=existing[0]
   if p.get("status") in ("scheduled","buffer","sending","sent"):
    print("BEREITS KORREKT GEBUCHT:",code,p.get("id"),p.get("status"))
    continue
   errors.append(code+" vorhandene neue Buchung unerwartet: "+str(p))
   continue
  old=next((p for p in posts if p.get("id")==previous_id),None)
  if old is None:
   errors.append(code+" vorheriger Post nicht gefunden; keine riskante Doppelbuchung")
   continue
  if old.get("status") in ("sent","sending"):
   errors.append(code+" vorheriges Motiv bereits versendet und nicht mehr austauschbar")
   continue
  if old.get("status") in ("scheduled","buffer"):
   gql="mutation {editPost(input:{id:"+json.dumps(previous_id)+",saveToDraft:true}){ ... on PostActionSuccess{post{id status dueAt}} ... on MutationError{message}}}"
   d=query(gql).get("editPost",{})
   if not isinstance(d,dict) or d.get("post",{}).get("status")!="draft":
    errors.append(code+" altes Design konnte nicht gestoppt werden: "+str(d))
    continue
   old["status"]="draft"
   print("VORHERIGE BILDVERSION ALS ENTWURF GESPEICHERT:",code,previous_id)
  elif old.get("status")!="draft":
   errors.append(code+" vorheriger Status ist "+str(old.get("status")))
   continue
  if any(p.get("dueAt")==due and p.get("status") in ("scheduled","buffer","sending") for p in posts):
   errors.append(code+" andere Buchung belegt den Termin")
   continue
  dt=datetime.fromisoformat(due.replace("Z","+00:00"))
  if datetime.now(timezone.utc)>=dt:
   # no backdating
   mode="shareNow";duearg=""
  else:
   mode="customScheduled";duearg=",dueAt:"+json.dumps(due)
  meta="metadata:{instagram:{type:"+kind+",shouldShareToFeed:"+("true" if kind=="post" else "false")+",isAiGenerated:true}}"
  q=("mutation {createPost(input:{text:"+json.dumps(caption,ensure_ascii=False)
      +",channelId:"+json.dumps(ch["id"])
      +",schedulingType:automatic,mode:"+mode+duearg
      +",assets:[{image:{url:"+json.dumps(urls[file])+"}}]"
      +",aiAssisted:true,"+meta
      +"}){... on PostActionSuccess{post{id status dueAt text assets{id mimeType}}} ... on MutationError{message}}}")
  r=query(q).get("createPost",{})
  if not isinstance(r,dict) or not r.get("post"):
   errors.append(code+" Buffer hat Bild nicht angenommen: "+str(r))
   continue
  p=r["post"]
  if p.get("status") not in ("scheduled","buffer","sending","sent") or len(p.get("assets") or [])!=1:
   errors.append(code+" Buffer Rückmeldung unvollständig "+str(p))
   continue
  posts.append(p)
  print("FINAL FREIGEGEBEN KFZ:",code,"ID",p.get("id"),"STATUS",p.get("status"),
        "DUE",p.get("dueAt"),"MODE",mode,"MEDIA",file)
 if errors:
  for e in errors: print("ACHTUNG:",e)
  raise RuntimeError("Nicht alle Kfz-Termine konnten bestätigt werden")
 print("BEIDE VOM NUTZER FREIGEGEBENEN MOTIVE IN BUFFER. NUR EINE STORY AM ABEND.")
if __name__=="__main__":main()
