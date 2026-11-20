"""Publish only two specifically user-approved premium Student BU Instagram Stories.
No logos, no persons, no old template. Story 1 share now, Story 2 20:15 CET on Nov 20, 2026.
The separately blocked recurring publisher remains blocked.
"""
import os,json,sys,hashlib,urllib.request
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE

ROOT=Path(__file__).resolve().parents[1]
MEDIA=ROOT/"assets"/"approved_schueler_bu_2026_11_20"
GITHUB_URL="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/approved_schueler_bu_2026_11_20/"
POSTS=[
  ("01.png","c253ca6934760fd5067254ebdb3c5c67e0440a664eadbb25553373c1640489f1","SCHMIDT PREMIUM BU STORY 1 2026-11-20",None),
  ("02.png","33a27080467b2c8ff426cc2a3285b169fa5f9ea479a69a5ad43c1ca1cc32a0b7","SCHMIDT PREMIUM BU STORY 2 2026-11-20","2026-11-20T19:15:00.000Z"),
]

def valid_media(name,digest):
  data=(MEDIA/name).read_bytes()
  if len(data)<100000 or not data.startswith(b"\x89PNG\r\n\x1a\n") or hashlib.sha256(data).hexdigest()!=digest:
    raise RuntimeError("Abgelehnt: Medienoriginal/Prüfsumme stimmt nicht "+name)
  url=GITHUB_URL+name
  req=urllib.request.Request(url,headers={"User-Agent":"SchmidtStoryApproved/1.0"})
  with urllib.request.urlopen(req,timeout=40) as r:
    if r.status!=200 or r.read(8)!=b"\x89PNG\r\n\x1a\n":
      raise RuntimeError("Bild nicht für Buffer abrufbar: "+name)
  return url

def run():
  if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
    raise RuntimeError("Falsches Repository")
  if os.getenv("TWO_STORY_RELEASE")!="schueler-bu-no-logo-two-stories-2026-11-20":
    raise RuntimeError("Spezifische Freigabe fehlt")
  org,ch=get_channel()
  actual=ch["name"].strip().lstrip("@").lower()
  linked=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
  if actual!=HANDLE and linked!=HANDLE:
    raise RuntimeError("Falscher Instagram-Kanal")
  posts=posts_from_buffer(org["id"],ch["id"])
  from visual_quality_gate import require_approved_media
  for name,digest,tag,scheduled in POSTS:
    url=valid_media(name,digest)
    require_approved_media(["assets/approved_schueler_bu_2026_11_20/"+name])
    identical=[p for p in posts if tag in (p.get("text") or "")]
    if identical:
      p=identical[0]
      if p.get("status") in ("sent","sending","scheduled","buffer"):
        print("BEREITS VERÖFFENTLICHT/GEPLANT",name,p.get("id"),p.get("status"),p.get("dueAt"))
        continue
      raise RuntimeError("Vorhandener Beitrag mit kritischem Status: "+str(p))
    if scheduled and datetime.now(timezone.utc)>=datetime.fromisoformat(scheduled.replace("Z","+00:00")):
      # late evening jobs: send immediately, never schedule back in the past
      mode="shareNow"
      timing=""
    elif scheduled:
      mode="customScheduled"
      timing=",dueAt:"+json.dumps(scheduled)
    else:
      mode="shareNow"
      timing=""
    caption=tag+" | Allianz Agentur Schmidt Döbeln – Schüler-BU. Die Leistungen und Voraussetzungen sind vertragsabhängig."
    gql=("mutation {createPost(input:{text:"+json.dumps(caption,ensure_ascii=False)
      +",channelId:"+json.dumps(ch["id"])
      +",schedulingType:automatic,mode:"+mode+timing+
      ",assets:[{image:{url:"+json.dumps(url)+"}}],aiAssisted:true,"
      +"metadata:{instagram:{type:story,shouldShareToFeed:false,isAiGenerated:true}}"
      +"}) {... on PostActionSuccess{post{id status dueAt text}} ... on MutationError{message}}}")
    result=query(gql).get("createPost",{})
    if not isinstance(result,dict) or not result.get("post"):
      raise RuntimeError("Buffer abgelehnt: "+str(result))
    p=result["post"]
    status=p.get("status")
    if status not in ("sent","sending","scheduled","buffer"):
      raise RuntimeError("Buffer nicht erfolgreich: "+str(p))
    print("BUFFER-STORY",name,"POST-ID",p.get("id"),"STATUS",status,"DUE",p.get("dueAt"),"MODE",mode)
    posts.append(p)
if __name__=="__main__":
  run()
