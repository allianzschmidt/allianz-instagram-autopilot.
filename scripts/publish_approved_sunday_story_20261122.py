"""One-time user-authorized Sunday 22 Nov 2026 Instagram Story at 20:15 Europe/Berlin.

Posts only the explicitly shown, logo-free cinematic Sunday artwork.
Does not unlock any formerly rejected automatic publishing or schedule feed posts.
"""
import hashlib,json,os,sys,time,urllib.request
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE

ROOT=Path(__file__).resolve().parents[1]
REL="assets/sunday_2026_11_22/sonntag_story_2015.jpg"
FILE=ROOT/REL
SHA="ef323baefa29bf25ceccfb3d158a3c76afa6ee133fa9ab1087b4020967d825f4"
URL="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/"+REL
TAG="SCHMIDT_SONNTAG_PREMIUM_2026_11_22_2015"
DUE="2026-11-22T19:15:00.000Z"  # 20:15 local Berlin CET
CAPTION=TAG+" | Einen schönen Sonntag! Manchmal ist ein ruhiger Sonntag das Schönste am ganzen Wochenende. Allianz Agentur Schmidt · Döbeln."

def validate_media():
    b=FILE.read_bytes()
    if len(b)<100000 or not b.startswith(b"\xff\xd8\xff") or hashlib.sha256(b).hexdigest()!=SHA:
        raise RuntimeError("Abweichendes Bild: Die bestätigte Sonntags-Story darf nicht verändert werden.")
    for attempt in range(5):
        try:
            req=urllib.request.Request(URL,headers={"User-Agent":"Schmidt-Sunday-Instagram/1.0"})
            with urllib.request.urlopen(req,timeout=30) as response:
                if response.status!=200 or response.read(3)!=b"\xff\xd8\xff":
                    raise RuntimeError("Bildquelle noch nicht öffentlich verfügbar")
            print("SONNTAG-BILD VERIFIZIERT",SHA)
            return
        except Exception:
            if attempt==4:raise
            time.sleep(5)

def main():
    if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Falsches GitHub-Repository")
    if os.getenv("SUNDAY_RELEASE")!="approved-sonntag-premium-single-story-nov22":
        raise RuntimeError("Story-spezifische Freigabe fehlt")
    validate_media()
    org,ch=get_channel()
    account=ch["name"].strip().lstrip("@").lower()
    link=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
    if account!=HANDLE and link!=HANDLE:
        raise RuntimeError("Falscher Instagram-Kanal")
    current=posts_from_buffer(org["id"],ch["id"])
    duplicates=[p for p in current if TAG in (p.get("text") or "")]
    if duplicates:
        if len(duplicates)>1:
            raise RuntimeError("Mehrere Sonntagskopien erkannt: kein weiterer Post")
        post=duplicates[0]
        if post.get("status") in ("scheduled","buffer","sending","sent"):
            print("SONNTAG-STORY SCHON IN BUFFER:",post.get("id"),post.get("status"),post.get("dueAt"))
            return
        raise RuntimeError("Sonntagsbeitrag existiert in Entwürfen/Fehlerzustand; zur Vermeidung von Dopplungen keine Neubuchung")
    colliding=[p for p in current if p.get("dueAt")==DUE and p.get("status") in ("scheduled","buffer","sending","sent")]
    if colliding:raise RuntimeError("20:15 Uhr ist schon durch anderen Beitrag belegt, kein Doppelpost: "+str(colliding))
    target=datetime.fromisoformat(DUE.replace("Z","+00:00"))
    mode="customScheduled" if datetime.now(timezone.utc)<target else "shareNow"
    timefield=",dueAt:"+json.dumps(DUE) if mode=="customScheduled" else ""
    gql=("mutation {createPost(input:{text:"+json.dumps(CAPTION,ensure_ascii=False)
        +",channelId:"+json.dumps(ch["id"])
        +",schedulingType:automatic,mode:"+mode+timefield
        +",assets:[{image:{url:"+json.dumps(URL)+"}}]"
        +",aiAssisted:true,metadata:{instagram:{type:story,shouldShareToFeed:false,isAiGenerated:true}}"
        +"}){... on PostActionSuccess{post{id status dueAt text assets{id mimeType}}} ... on MutationError{message}}}")
    res=query(gql).get("createPost",{})
    if not isinstance(res,dict) or "post" not in res:
        raise RuntimeError("Buffer hat Sonntags-Story NICHT angenommen: "+str(res))
    post=res["post"]
    if post.get("status") not in ("scheduled","buffer","sending","sent") or len(post.get("assets") or [])!=1:
        raise RuntimeError("Buffer-Buchung unvollständig: "+str(post))
    print("SONNTAG STORY BUFFER:",post["id"],"STATUS:",post.get("status"),"DUE:",post.get("dueAt"),"MODE:",mode)
    print("EXAKT EINE, KEIN SONNTAGS-FEED, ALTE STANDARDGRAFIKEN BLEIBEN GESPERRT")
if __name__=="__main__":
    main()
