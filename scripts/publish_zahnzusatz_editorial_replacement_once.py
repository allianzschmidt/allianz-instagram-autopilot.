"""Einmalige, vom Nutzer angeforderte Ersatz-Zahnzusatz-Story am 18.11.2026.
Setzt ein hochwertiges 9:16-Fotomotiv ein, keine Allianz-Logos.
Eine bereits veröffentlichte Instagram-Story kann Buffer nicht rückwirkend bearbeiten.
"""
import hashlib,json,os,sys,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE
IMAGE=Path(__file__).resolve().parents[1]/"assets"/"replacement_stories"/"zahnzusatz_20261118_editorial.png"
URL="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/replacement_stories/zahnzusatz_20261118_editorial.png"
SHA="1557fefb930f948a6e3a0456e459e9c0985c95dfeee72eace24d80b87ac27b34"
TEXT="100 % Zahnzusatz? Was bedeutet das wirklich? | Premium-Story-Ersatz 18.11.2026"
def run():
    if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Falsches Repository")
    if os.getenv("REPLACE_STORY_RELEASE")!="replacement-zahnzusatz-2026-11-18":
        raise RuntimeError("Keine Freigabe zum Story-Ersatz")
    img=IMAGE.read_bytes()
    if hashlib.sha256(img).hexdigest()!=SHA or img[:8]!=b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("Originalgrafik oder Pruefsumme stimmt nicht")
    org,ch=get_channel()
    if ch["name"].strip().lstrip("@").lower()!=HANDLE and (
       (ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()!=HANDLE):
        raise RuntimeError("Falscher Instagram-Kanal")
    for p in posts_from_buffer(org["id"],ch["id"]):
        if (p.get("text") or "")==TEXT:
            print("ERSATZ-STORY BEREITS VORHANDEN:",p.get("id"),"STATUS:",p.get("status"))
            return
    req=urllib.request.Request(URL,headers={"User-Agent":"Agentur-Schmidt-Editorial/1.0"})
    with urllib.request.urlopen(req,timeout=35) as r:
        if r.status!=200 or r.read(8)!=b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("Premium-Foto noch nicht abrufbar")
    gql=("mutation {createPost(input:{text:"+json.dumps(TEXT,ensure_ascii=False)+
         ",channelId:"+json.dumps(ch["id"])+
         ",schedulingType:automatic,mode:shareNow,"+
         "assets:[{image:{url:"+json.dumps(URL)+"}}],"+
         "aiAssisted:true,metadata:{instagram:{type:story,shouldShareToFeed:false,isAiGenerated:true}}"+
         "}){ ... on PostActionSuccess{post{id status dueAt text}} ... on MutationError{message}}}")
    result=query(gql).get("createPost",{})
    if not isinstance(result,dict) or "post" not in result:
        raise RuntimeError("Buffer nahm Ersatz-Story nicht an: "+str(result))
    p=result["post"]
    print("ERSATZ-STORY BUFFER:",p["id"],"STATUS:",p.get("status"),"DUE:",p.get("dueAt"))
    print("ALTE INSTAGRAM STORY 08:30 MUSS IM INSTAGRAM-ACCOUNT SEPARAT GELOESCHT WERDEN.")
    print("Sent bestaetigt die neue Veroeffentlichung, 'sending' noch nicht.")
if __name__=="__main__":
    run()
