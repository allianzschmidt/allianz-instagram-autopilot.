"""Nur das vom Nutzer freigegebene vierteilige Karussell 'Schlüssel weg?' veröffentlichen.
Niemals andere Medien; Deduplizierung und Account-Abgleich.
"""
import json, os, sys, time, urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel, posts_from_buffer, query
ROOT=Path(__file__).resolve().parents[1]
FILES=[f"{i:02d}.jpg" for i in range(1,5)]
PREFIX="Schlüssel weg? Wer zahlt? 🔑"
CAPTION=(
    PREFIX+"\n\n"
    "Ein Schlüssel ist schnell verloren – doch ob eine Versicherung die Kosten übernimmt, "
    "hängt vom konkreten Fall und vom Vertrag ab.\n\n"
    "🔹 Eigener Haus- oder Autoschlüssel: Welche Kosten können tatsächlich entstehen?\n"
    "🔹 Fremde Schlüssel, etwa von Mietobjekten oder Arbeitgebern: Ist Schlüsselverlust "
    "ausdrücklich mitversichert?\n"
    "🔹 Bei einer Schließanlage können besondere Kosten und Bedingungen gelten.\n\n"
    "Wichtig: Nicht jeder Schlüsselverlust ist automatisch versichert. "
    "Entscheidend sind Schaden, Vereinbarungen, Selbstbeteiligung und mögliche Ausschlüsse.\n\n"
    "📍 Allianz Agentur Schmidt · Döbeln\n"
    "💬 Du bist dir unsicher? Schreib uns eine Nachricht und lass deinen Schutz prüfen.\n\n"
    "#Schlüsselverlust #Privathaftpflicht #Versicherungswissen #Döbeln #AllianzAgenturSchmidt"
)
def main():
    if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Falsches Repository")
    if os.getenv("CONFIRMED_MEDIA_RELEASE")!="approved-key-loss-4-slides-11nov":
        raise RuntimeError("Nutzerfreigabe für dieses Medium fehlt")
    if not os.getenv("BUFFER_API_KEY"):
        raise RuntimeError("BUFFER_API_KEY fehlt")
    root=ROOT/"assets"/"approved_keyloss"
    for n in FILES:
        data=(root/n).read_bytes()
        if len(data)<25000 or data[:3]!=b"\xff\xd8\xff":
            raise RuntimeError("Originalbild fehlerhaft: "+n)
    org,ch=get_channel()
    for p in posts_from_buffer(org["id"],ch["id"]):
        if PREFIX in (p.get("text") or ""):
            print("✅ Dieses Schlüssel-Karussell ist bereits in Buffer: "+str(p.get("id"))+" "+str(p.get("status")))
            return
    urls=["https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/approved_keyloss/"+n for n in FILES]
    for url in urls:
        for attempt in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Schmidt-Instagram-Publisher/1.0"}),timeout=35) as resp:
                    assert resp.status==200 and resp.read(3)==b"\xff\xd8\xff"
                break
            except Exception:
                if attempt==5:
                    raise
                time.sleep(5)
    assets=",".join("{image:{url:"+json.dumps(u)+"}}" for u in urls)
    gql=("mutation { createPost(input:{text:"+json.dumps(CAPTION,ensure_ascii=False)
         +",channelId:"+json.dumps(ch["id"])
         +",schedulingType:automatic,mode:shareNow,assets:["+assets+"],"
         +"aiAssisted:true,metadata:{instagram:{type:post,shouldShareToFeed:true,isAiGenerated:true}}"
         +"}){ ... on PostActionSuccess {post{id status dueAt}} ... on MutationError{message} }}")
    outcome=query(gql).get("createPost",{})
    if not isinstance(outcome,dict) or "post" not in outcome:
        raise RuntimeError("Buffer hat Schlüssel-Karussell abgelehnt: "+str(outcome))
    post=outcome["post"]
    print("BUFFER-SCHLUESSEL-KARUSSELL ID:",post.get("id"))
    print("BUFFER-SCHLUESSEL-KARUSSELL STATUS:",post.get("status"))
    print("BUFFER-SCHLUESSEL-KARUSSELL DUE:",post.get("dueAt"))
    print("NUR @allianzschmidtdoebeln, exakt 4 geprüfte Slides. Veröffentlichung erst bei Status sent bestätigt.")
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("SCHLUESSEL-KARUSSELL NICHT BESTAETIGT:",str(e),file=sys.stderr)
        sys.exit(1)
