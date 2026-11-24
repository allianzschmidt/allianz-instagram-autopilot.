"""One-off 24 November 2026 17:00 CET Kfz offer Feed post.
Exact user-preferred premium ordinary blue hatchback, no Allianz logo;
separate from the approved Steinschlag Story at 18:30.
Does not enable the rejected template generator.
"""
import hashlib,json,os,sys,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE

REL="assets/kfz_offer_nov24_2026/premium_kfz_feed.jpg"
SHA="2bda36347ebd7b9caf820ca77ef0ca25e721c73322308afac9d572e2e3f06814"
FILE=Path(__file__).resolve().parents[1]/REL
URL="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/"+REL
DUE="2026-11-24T16:00:00.000Z"
CAPTION=(
 "🚗 Kfz-Wechselsaison: Jetzt dein persönliches Angebot einholen!\n\n"
 "Für viele Kfz-Verträge mit Hauptfälligkeit zum 1. Januar muss eine ordentliche "
 "Kündigung bis spätestens 30. November beim bisherigen Versicherer eingehen. "
 "Entscheidend sind immer die individuelle Hauptfälligkeit und die Vertragsbedingungen.\n\n"
 "Du möchtest ein unverbindliches Kfz-Angebot für dein Auto? "
 "Schreib uns „KFZ“ per Direktnachricht – wir beraten dich persönlich.\n\n"
 "📍 Allianz Agentur Schmidt · Döbeln\n\n"
 "#KfzVersicherung #KfzWechsel #Autoversicherung #Döbeln #Mittelsachsen"
)
def check_original():
 b=FILE.read_bytes()
 if len(b)<100000 or b[:3]!=b"\xff\xd8\xff" or hashlib.sha256(b).hexdigest()!=SHA:
  raise RuntimeError("Kfz-Motiv weicht vom visuell gezeigten Original ab")
 for i in range(4):
  try:
   req=urllib.request.Request(URL,headers={"User-Agent":"Schmidt-Kfz-Premium-Feed-Nov24/1.0"})
   with urllib.request.urlopen(req,timeout=30) as r:
    if r.status!=200 or r.read(3)!=b"\xff\xd8\xff":
     raise RuntimeError("Bild nicht abrufbar")
   print("KFZ FEED EXAKT GEPRUEFT:",SHA)
   return
  except Exception:
   if i==3:raise
   time.sleep(4)

def main():
 if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
  raise RuntimeError("Falsches GitHub-Repository")
 if os.getenv("SINGLE_FEED_RELEASE")!="user-requested-kfz-feed-nov24-2026":
  raise RuntimeError("Einmalige Auftragsfreigabe fehlt")
 check_original()
 org,ch=get_channel()
 actual=ch.get("name","").strip().lstrip("@").lower()
 link=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
 if actual!=HANDLE and link!=HANDLE:raise RuntimeError("Falscher Instagram-Account")
 posts=posts_from_buffer(org["id"],ch["id"])
 matches=[p for p in posts if p.get("text")==CAPTION]
 if matches:
  if len(matches)==1 and matches[0].get("status") in ("scheduled","buffer","sending","sent"):
   p=matches[0]
   print("KFZ FEED BEREITS GEBUCHT",p.get("id"),p.get("status"),p.get("dueAt"))
   return
  raise RuntimeError("Duplikat oder unklarer Beitragsstatus; keinen weiteren Feed senden")
 if any(p.get("dueAt")==DUE and p.get("status") in ("scheduled","buffer","sending") for p in posts):
  raise RuntimeError("17:00 Uhr ist bereits belegt, keine Doppelbuchung")
 # Also refuse a different Kfz-feed on this date to avoid two sales posts.
 for p in posts:
  t=p.get("dueAt") or ""
  if t.startswith("2026-11-24") and p.get("status") in ("scheduled","buffer","sending","sent"):
   if "Kfz-Wechselsaison: Jetzt dein persönliches Angebot einholen!" in (p.get("text") or ""):
    raise RuntimeError("Ähnlicher Kfz-Beitrag existiert bereits heute")
 target=datetime.fromisoformat(DUE.replace("Z","+00:00"))
 mode="customScheduled" if datetime.now(timezone.utc)<target else "shareNow"
 due_arg=",dueAt:"+json.dumps(DUE) if mode=="customScheduled" else ""
 q=("mutation {createPost(input:{text:"+json.dumps(CAPTION,ensure_ascii=False)
  +",channelId:"+json.dumps(ch["id"])
  +",schedulingType:automatic,mode:"+mode+due_arg
  +",assets:[{image:{url:"+json.dumps(URL)+"}}],aiAssisted:true,"
  +"metadata:{instagram:{type:post,shouldShareToFeed:true,isAiGenerated:true}}"
  +"}){... on PostActionSuccess{post{id status dueAt text assets{id mimeType}}}"
  +" ... on MutationError{message}}}")
 result=query(q).get("createPost",{})
 if not isinstance(result,dict) or not result.get("post"):
  raise RuntimeError("Buffer hat Feed-Beitrag abgelehnt: "+str(result))
 p=result["post"]
 if p.get("status") not in ("scheduled","buffer","sending","sent") or len(p.get("assets") or [])!=1:
  raise RuntimeError("Buffer-Bestätigung unvollständig: "+str(p))
 print("KFZ_FEED_NOV24 ID:",p["id"],"STATUS:",p.get("status"),"DUE:",p.get("dueAt"),"MODE:",mode)
 print("NUR EIN FEED-BEITRAG; STEINSCHLAG-STORY 18:30 UNBERÜHRT")
if __name__=="__main__":main()
