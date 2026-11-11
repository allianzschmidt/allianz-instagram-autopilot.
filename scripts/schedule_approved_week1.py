"""Planen nur zwei bereits vereinbarte Instagram-Posts: Steinschlag & Wasserschaden."""
import json,os,sys,time,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query
ROOT=Path(__file__).resolve().parents[1]
if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
    raise SystemExit("Falsches Repository")
if os.getenv("CONFIRMED_MEDIA_RELEASE")!="approved-week1-12-13nov":
    raise SystemExit("Medien nicht explizit im Redaktionsplan freigegeben")
if not os.getenv("BUFFER_API_KEY"):
    raise SystemExit("BUFFER_API_KEY fehlt")

POSTS=[
    {"key":"steinschlag_2026_11_12",
     "due":"2026-11-12T11:30:00.000Z",
     "title":"Steinschlag – wer zahlt?",
     "files":["steinschlag.png"],
     "caption":"Steinschlag – wer zahlt wirklich? 🚗\n\n"
       "Ein Steinschlag in der Windschutzscheibe ist schnell passiert. "
       "Ob deine Versicherung für Reparatur oder Scheibentausch aufkommt, "
       "hängt vor allem von der vereinbarten Kaskodeckung, den Tarifbedingungen "
       "und möglichen Selbstbeteiligungen ab.\n\n"
       "🔍 Tipp: Bei einem Steinschlag lieber früh prüfen lassen, ob die Scheibe reparierbar ist. "
       "Der konkrete Leistungsumfang ist vertraglich geregelt.\n\n"
       "📍 Allianz Agentur Schmidt · Döbeln\n"
       "💬 Fragen zum Kfz-Schutz? Schreib uns direkt.\n\n"
       "#Steinschlag #Autoversicherung #Döbeln #KfzVersicherung"},
    {"key":"wasserschaden_2026_11_13",
     "due":"2026-11-13T17:30:00.000Z",
     "title":"Wasser im Haus – was jetzt?",
     "files":["wasser_01.jpg","wasser_02.jpg","wasser_03.jpg","wasser_04.jpg"],
     "caption":"Wasser im Haus? Diese Schritte helfen im Ernstfall. 💧\n\n"
       "1️⃣ Schaden begrenzen – aber nur, wenn es gefahrlos möglich ist.\n"
       "2️⃣ Fotos und Zeitpunkt dokumentieren.\n"
       "3️⃣ Versicherung beziehungsweise zuständige Ansprechpartner zeitnah informieren.\n\n"
       "Ob der Schaden versichert ist, hängt von Ursache, versicherten Gefahren, "
       "vereinbarten Bausteinen und Bedingungen ab. Regenwasser ist nicht automatisch "
       "gleich Leitungswasser!\n\n"
       "📍 Allianz Agentur Schmidt · Döbeln\n"
       "💬 Fragen zum Schutz deines Zuhauses? Melde dich bei uns.\n\n"
       "#Wasserschaden #Wohngebäude #Hausrat #Döbeln #Elementarschutz"}
]
def check(url):
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Schmidt-Approved-Week1/1.0"}),timeout=40) as resp:
                if resp.status!=200 or not resp.headers.get("Content-Type","").startswith("image/"):
                    raise RuntimeError("Ungültige Bildantwort")
                head=resp.read(8)
                if head[:3]!=b"\xff\xd8\xff" and head[:8]!=b"\x89PNG\r\n\x1a\n":
                    raise RuntimeError("Bildtyp nicht erkannt")
            return
        except Exception:
            if i==5:raise
            time.sleep(5)
def main():
    org,ch=get_channel()
    all_posts=posts_from_buffer(org["id"],ch["id"])
    root="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/approved_week1/"
    for item in POSTS:
        if any((p.get("text") or "").startswith(item["caption"][:25]) for p in all_posts):
            print("Bereits in Buffer vorhanden:",item["title"])
            continue
        for f in item["files"]:
            if not (ROOT/"assets"/"approved_week1"/f).is_file():
                raise RuntimeError("Fehlendes freigegebenes Bild "+f)
        urls=[root+n for n in item["files"]]
        for u in urls: check(u)
        media=",".join("{image:{url:"+json.dumps(u)+"}}" for u in urls)
        mutation=("mutation {createPost(input:{text:"+json.dumps(item["caption"],ensure_ascii=False)
                  +",channelId:"+json.dumps(ch["id"])
                  +",schedulingType:automatic,mode:customScheduled,dueAt:"+json.dumps(item["due"])
                  +",assets:["+media+"],aiAssisted:true,"
                  +"metadata:{instagram:{type:post,shouldShareToFeed:true,isAiGenerated:true}}"
                  +"}){... on PostActionSuccess{post{id status dueAt}} ... on MutationError{message}}}")
        response=query(mutation).get("createPost",{})
        if not isinstance(response,dict) or "post" not in response:
            raise RuntimeError("Buffer lehnte "+item["title"]+" ab: "+str(response))
        post=response["post"]
        print("IN BUFFER EINGEPLANT:",item["title"],"ID",post.get("id"),"STATUS",post.get("status"),"DUE",post.get("dueAt"))
        all_posts.append({"text":item["caption"],"dueAt":post.get("dueAt"),"status":post.get("status")})
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("WOCHE-1-PLANUNG FEHLGESCHLAGEN:",str(exc),file=sys.stderr)
        sys.exit(1)
