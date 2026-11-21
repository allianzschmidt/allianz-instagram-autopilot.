"""One-time, explicitly requested 5-slide student BU premium carousel.
User request on 21 Nov 2026: "dann mach das mensch" after discussing the missing feed post.
The media are created afresh for this request and personally checked for no logo/people.
This is not a general reactivation of the old rejected premium visual series.
"""
import hashlib,json,os,sys,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel, posts_from_buffer,query,HANDLE

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"assets"/"approved_specific"/"schueler_bu_2026_11_21"
FILES=[
 ("01.jpg","40acfb56c62a2bed09f9a4e8150e5f67770b81002d396e500702fbe8e09fab46"),
 ("02.jpg","c41a746b4452f4353716d2245df2d4fd75d68e6f22eaad6e2663b1b37062f678"),
 ("03.jpg","325dce8dde8aa814826e0c8dfdab3ef2ad6fba18e7d365f375bbe8a6e51398b9"),
 ("04.jpg","a0e6b34bd1e35ff3850d61c3c054508f7a6102aad3916c339b05a1d5df7c6f67"),
 ("05.jpg","b197afed953f0960108e1e880b959be37ce2e0fc5af7454ddd1939d010342640"),
]
PREFIX="SCHÜLER-BU: Schon in der Schulzeit absichern?"
CAPTION=(
 PREFIX+" 🎒\n\n"
 "Die Berufswahl liegt vielleicht noch in der Zukunft. "
 "Trotzdem kann es sinnvoll sein, sich bereits in der Schulzeit mit Berufsunfähigkeit zu beschäftigen.\n\n"
 "🔹 Ein Einstieg ist je nach Anbieter, Tarif und Voraussetzungen schon als Schülerin oder Schüler möglich.\n"
 "🔹 Berufsunfähigkeit ist nicht auf Unfallfolgen beschränkt.\n"
 "🔹 Besonders wichtig: Gesundheitsangaben, die Definition der versicherten Tätigkeit "
 "und mögliche spätere Anpassungen.\n\n"
 "Welche Leistungen tatsächlich versichert sind, ergibt sich aus den jeweiligen "
 "Vertragsbedingungen. Eine individuelle Prüfung ist wichtig.\n\n"
 "📍 Allianz Agentur Schmidt · Döbeln\n"
 "💬 Schreib uns „SCHÜLER-BU“, wenn du die Möglichkeiten unverbindlich kennenlernen möchtest.\n\n"
 "#SchülerBU #Berufsunfähigkeit #Versicherungswissen #Döbeln #Mittelsachsen"
)
BASE="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/approved_specific/schueler_bu_2026_11_21/"

def check_media():
    for filename,sha in FILES:
        p=PATH/filename
        contents=p.read_bytes()
        if len(contents)<80000 or contents[:3]!=b"\xff\xd8\xff":
            raise RuntimeError("Original fehlt oder ist kein hochwertiges JPEG: "+filename)
        if hashlib.sha256(contents).hexdigest()!=sha:
            raise RuntimeError("Kein genau freigegebenes Original: "+filename)
        req=urllib.request.Request(BASE+filename,headers={"User-Agent":"Schmidt-StudentBU-Editorial-2026/1.0"})
        with urllib.request.urlopen(req,timeout=40) as response:
            if response.status!=200 or response.read(3)!=b"\xff\xd8\xff":
                raise RuntimeError("Bild nicht öffentlich für Buffer abrufbar: "+filename)
        print("EXACT MEDIA VERIFIED:",filename,sha)

def main():
    if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Falsches Repo – keine Veröffentlichung")
    if os.getenv("USER_RELEASE")!="user-requested-schueler-bu-premium-feed-2026-11-21":
        raise RuntimeError("Spezifischer Veröffentlichungsauftrag fehlt")
    if not os.getenv("BUFFER_API_KEY"):
        raise RuntimeError("Buffer API Key fehlt")
    check_media()
    org,ch=get_channel()
    name=ch.get("name","").strip().lstrip("@").lower()
    link=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
    if name!=HANDLE and link!=HANDLE:
        raise RuntimeError("Falscher Kanal – keine Veröffentlichung")
    existing=posts_from_buffer(org["id"],ch["id"])
    for p in existing:
        if (p.get("text") or "").startswith(PREFIX):
            if p.get("status") in ("sent","sending","scheduled","buffer"):
                print("BEREITS VORHANDEN:",p.get("id"),"STATUS:",p.get("status"),"DUE:",p.get("dueAt"))
                return
            raise RuntimeError("Gleichnamiger Post im unsicheren Status: "+str(p))
    images=",".join("{image:{url:"+json.dumps(BASE+n)+"}}" for n,_ in FILES)
    gql=("mutation {createPost(input:{"
      "text:"+json.dumps(CAPTION,ensure_ascii=False)
      +",channelId:"+json.dumps(ch["id"])
      +",schedulingType:automatic,mode:shareNow,assets:["+images+"]"
      +",aiAssisted:true,metadata:{instagram:{type:post,shouldShareToFeed:true,isAiGenerated:true}}"
      +"}) {... on PostActionSuccess{post{id status dueAt text assets{id mimeType}}}"
      +" ... on MutationError{message}}}")
    data=query(gql).get("createPost",{})
    if not isinstance(data,dict) or "post" not in data:
        raise RuntimeError("BUFFER HAT NICHT ANGENOMMEN: "+str(data))
    p=data["post"]
    count=len(p.get("assets") or [])
    print("BUFFER PREMIUM SCHUELER BU CAROUSEL ID:",p.get("id"))
    print("BUFFER PREMIUM SCHUELER BU CAROUSEL STATUS:",p.get("status"))
    print("BUFFER PREMIUM SCHUELER BU CAROUSEL DUE:",p.get("dueAt"))
    print("BUFFER PREMIUM SCHUELER BU CAROUSEL ASSET COUNT:",count)
    print("INSTAGRAM: @allianzschmidtdoebeln")
    if count!=5:raise RuntimeError("Buffer meldete nicht alle 5 Bilder!")
    if p.get("status") not in ("sent","sending","scheduled","buffer"):
        raise RuntimeError("Buffer Post nicht erfolgreich: "+str(p))
    print("Hinweis: Nur Buffer sent bedeutet von Buffer als verschickt gemeldet, keine verifizierte Instagram permalink.")
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("KEINE VERÖFFENTLICHUNG BESTÄTIGT:",str(e),file=sys.stderr)
        raise
