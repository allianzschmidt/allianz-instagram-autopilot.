"""One-off approved Steinschlag windshield Story, 24 Nov 2026 18:30 CET.
Uses corrected, manually reviewed artwork with a visible windshield and
the Allianz repair-vs-replacement qualification. Does not unlock templates.
"""
import hashlib,json,os,sys,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE

REL="assets/steinschlag_corrected_20261124/steinschlag_story.jpg"
IMAGE=Path(__file__).resolve().parents[1]/REL
SHA="79b71465b5c7f11e29331190aba3cfce7f9325f8708026b8026d63fb05cfee40"
URL="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/"+REL
TAG="SCHMIDT_STEINSCHLAG_WINDSCHUTZSCHEIBE_PREMIUM_20261124"
DUE="2026-11-24T17:30:00.000Z" # 18:30 CET

CAPTION=(TAG+" | Steinschlag an der Windschutzscheibe? "
 "Bei einer versicherten Glasreparatur ohne Scheibentausch verzichtet die Allianz "
 "auf die Selbstbeteiligung. Bei einem erforderlichen Scheibentausch kann die vertragliche "
 "Selbstbeteiligung anfallen. Bitte beachten: individuelle Vertrags- und ggf. Glaspartnerbedingungen. "
 "Allianz Agentur Schmidt · Döbeln. Wir unterstützen bei der Schadenabwicklung.")

def check_media():
 content=IMAGE.read_bytes()
 if len(content)<100000 or content[:3]!=b"\xff\xd8\xff" or hashlib.sha256(content).hexdigest()!=SHA:
  raise RuntimeError("Die freigegebene Bilddatei stimmt nicht!")
 for attempt in range(4):
  try:
   req=urllib.request.Request(URL,headers={"User-Agent":"Schmidt-Steinschlag-Premium/1.0"})
   with urllib.request.urlopen(req,timeout=35) as response:
    if response.status!=200 or response.read(3)!=b"\xff\xd8\xff":
     raise RuntimeError("Grafik für Buffer nicht verfügbar")
   break
  except Exception:
   if attempt==3:raise
   time.sleep(5)
 print("GENAUES STEINSCHLAG-MOTIV GEPRUEFT:",SHA)

def main():
 if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
  raise RuntimeError("Falsches Repository")
 if os.getenv("STEINSCHLAG_RELEASE")!="corrected-windshield-story-20261124":
  raise RuntimeError("Keine konkrete Freigabe")
 check_media()
 org,ch=get_channel()
 name=ch["name"].strip().lstrip("@").lower()
 link=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
 if name!=HANDLE and link!=HANDLE:
  raise RuntimeError("Falscher Instagram-Account")
 posts=posts_from_buffer(org["id"],ch["id"])
 matched=[p for p in posts if TAG in (p.get("text") or "")]
 if matched:
  if len(matched)!=1:raise RuntimeError("Mehrere gleiche Stories, kein weiterer Post")
  p=matched[0]
  if p.get("status") in ("scheduled","buffer","sending","sent"):
   print("STORY BEREITS GEBUCHT:",p["id"],p["status"],p.get("dueAt"));return
  raise RuntimeError("Schon als Entwurf/Fehler vorhanden; manuell prüfen statt Duplikat")
 if any(p.get("dueAt")==DUE and p.get("status") in ("scheduled","buffer","sending")
        for p in posts):
  raise RuntimeError("Termin belegt; kein Doppelposting")
 target=datetime.fromisoformat(DUE.replace("Z","+00:00"))
 mode="customScheduled" if datetime.now(timezone.utc)<target else "shareNow"
 duearg=",dueAt:"+json.dumps(DUE) if mode=="customScheduled" else ""
 gql=("mutation {createPost(input:{text:"+json.dumps(CAPTION,ensure_ascii=False)+
   ",channelId:"+json.dumps(ch["id"])+",schedulingType:automatic,mode:"+mode+duearg+
   ",assets:[{image:{url:"+json.dumps(URL)+"}}],aiAssisted:true,"+
   "metadata:{instagram:{type:story,shouldShareToFeed:false,isAiGenerated:true}}"+
   "}){... on PostActionSuccess{post{id status dueAt text assets{id mimeType}}} ... on MutationError{message}}}")
 result=query(gql).get("createPost",{})
 if not isinstance(result,dict) or "post" not in result:
  raise RuntimeError("Buffer hat Steinschlag-Story nicht angenommen: "+str(result))
 post=result["post"]
 if post.get("status") not in ("sent","sending","scheduled","buffer") or len(post.get("assets") or [])!=1:
  raise RuntimeError("Buffer Status/Medienanzahl unvollständig: "+str(post))
 print("STEINSCHLAG_KORRIGIERT_BUFFER ID:",post["id"],"STATUS:",post["status"],
       "DUE:",post.get("dueAt"),"MODE:",mode)
 print("Nur eine Steinschlag-Story für heute; kein automatisches Freischalten der alten Grafiken")
if __name__=="__main__":main()
