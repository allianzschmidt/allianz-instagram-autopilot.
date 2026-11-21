"""Einmalige, explizit beauftragte Kfz-Wechselsaison am 21.11.2026.
5-Slide-Premiumkarussell + 3 Storys; kein Allianz-Logo.
Ohne Entsperrung der mehrfach abgelehnten Standardgrafiken.
"""
import hashlib,json,os,sys,time,urllib.request
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer,query,HANDLE

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"assets"/"campaign_kfz_2026_11_21"
WEB="https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/campaign_kfz_2026_11_21/"
MEDIA={
"01_KFZ_Titel.jpg":"4514f9420062459a7eb661546fdc08d28de78469f648366bafe93d44a1d5540e",
"02_KFZ_Stichtag.jpg":"29854602fcc221f91a07f5dc161d954c194bb5ec4b34195886ef66ba3c322121",
"03_KFZ_Leistungen.jpg":"243ce46c4c231cde99490221160f8af33424f8eafb6a52d91f1b78c3db8f6fea",
"04_KFZ_Sonderkuendigung.jpg":"e9a6df882dc3d39a86d776b7c5c2c3c680d478947015783456b77e96f514b654",
"05_KFZ_Kontakt.jpg":"4ae18af198f7af73f58b88ccf786c130c6a1d2509d59ce0ffae51de96ff24a3e",
"Story_01_KFZ_Wechselsaison.jpg":"573504c11918a1daf1207aee939faa79311d2115a851af22816acaac63b19a41",
"Story_02_KFZ_Check.jpg":"efa44e160b4a0cf2275ea0f9b1938ef6f40dd61cfce51afbcda0fd4845bc25bc",
"Story_03_KFZ_Direktnachricht.jpg":"c4f73d974b86e788bef99df514a14f19b6de791ee0c9693d5033389a35b07982"
}
TAG="SCHMIDT_KFZ_WECHSELSAISON_2026_11_21"
CAPTION=(
  "🚗 Kfz-Wechselsaison 2026: Jetzt Beitrag und Leistungen prüfen!\n\n"
  "Für viele Kfz-Verträge mit Hauptfälligkeit zum 1. Januar ist der 30. November "
  "der reguläre Kündigungsstichtag. Die Kündigung muss bis dahin beim bisherigen "
  "Versicherer eingegangen sein. Prüfe aber immer den Ablauf deines eigenen Vertrags. "
  "Bei bestimmten Beitragserhöhungen kann ein Sonderkündigungsrecht bestehen.\n\n"
  "Beim Tarifvergleich zählt nicht nur der Preis, sondern auch der Schutz: "
  "Haftpflicht, Kasko, Selbstbeteiligung und Leistungen im Schadenfall. "
  "Vor der Kündigung sollte die neue Absicherung geklärt sein.\n\n"
  "💙 Allianz Agentur Schmidt · Döbeln\n"
  "📩 Schreib uns „KFZ“ per Direktnachricht für einen unverbindlichen persönlichen Check.\n\n"
  "#KfzVersicherung #KfzWechsel #Autoversicherung #Döbeln #Mittelsachsen "
  "#KfzWechselsaison\n\n"+TAG
)
QUEUE=[
 ("S1","2026-11-21T11:45:00.000Z","story",
  ["Story_01_KFZ_Wechselsaison.jpg"],"Kfz-Wechselsaison – 30. November im Blick",False),
 ("F1","2026-11-21T14:45:00.000Z","post",
  ["01_KFZ_Titel.jpg","02_KFZ_Stichtag.jpg","03_KFZ_Leistungen.jpg","04_KFZ_Sonderkuendigung.jpg","05_KFZ_Kontakt.jpg"],CAPTION,True),
 ("S2","2026-11-21T17:45:00.000Z","story",
  ["Story_02_KFZ_Check.jpg"],"Kfz-Schutz vergleichen: Haftpflicht, Kasko, Selbstbeteiligung.",False),
 ("S3","2026-11-21T19:45:00.000Z","story",
  ["Story_03_KFZ_Direktnachricht.jpg"],"Jetzt Kfz-Check bei Allianz Agentur Schmidt in Döbeln anfragen.",False)
]
def verify(f):
    data=(FOLDER/f).read_bytes()
    if len(data)<80000 or data[:3]!=b"\xff\xd8\xff":
        raise RuntimeError("Medien-Format oder Qualitätscheck fehlgeschlagen: "+f)
    if hashlib.sha256(data).hexdigest()!=MEDIA[f]:
        raise RuntimeError("Originalbild nach Prüfung unerwartet verändert: "+f)
    return WEB+f

def main():
    if os.getenv("GITHUB_REPOSITORY")!="allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Falsches Repository")
    if os.getenv("CAMPAIGN_RELEASE")!="explicit-user-request-kfz-21nov2026":
        raise RuntimeError("Keine Freigabe zur Kfz-Kampagne")
    if not os.getenv("BUFFER_API_KEY"):
        raise RuntimeError("Buffer-Schlüssel nicht vorhanden")
    # Preflight all original byte-exact JPEGs; protect against incomplete import.
    for f in MEDIA:
        url=verify(f)
        for attempt in range(5):
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"Schmidt-Kfz-Editorial/1.0"})
                with urllib.request.urlopen(req,timeout=35) as r:
                    if r.status!=200 or r.read(3)!=b"\xff\xd8\xff":
                        raise RuntimeError("Public JPEG invalid")
                break
            except Exception:
                if attempt==4:raise
                time.sleep(5)
    org,ch=get_channel()
    if ch["name"].strip().lstrip("@").lower()!=HANDLE and (
       (ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()!=HANDLE):
        raise RuntimeError("Falsches Instagram-Konto")
    seen=posts_from_buffer(org["id"],ch["id"])
    now=datetime.now(timezone.utc)
    print("KFZ CAMPAIGN VERIFIED ACCOUNT @"+HANDLE,"UTC",now.isoformat())
    for code,due,kind,files,caption,feed in QUEUE:
        marker=TAG+"_"+code
        usertext=(caption if code=="F1" else marker+" | "+caption)
        matches=[p for p in seen if marker in (p.get("text") or "")]
        if matches:
            post=matches[0]
            if post.get("status") in ("sent","sending","scheduled","buffer"):
                print("BEREITS VORHANDEN",code,post.get("id"),post.get("status"),post.get("dueAt"))
                continue
            raise RuntimeError("Alte Kfz-Kampagnenkopie in unerwartetem Status: "+str(post))
        target=datetime.fromisoformat(due.replace("Z","+00:00"))
        conflicts=[p for p in seen if p.get("dueAt")==due and p.get("status") in ("buffer","scheduled","sending")]
        if conflicts:raise RuntimeError("Andere Veröffentlichung zur gleichen Uhrzeit vorhanden: "+str(conflicts))
        if now>=target:
            mode="shareNow"; extra=""
            print("TERMIN VERGANGEN, STARTE SOFORT:",code)
        else:
            mode="customScheduled";extra=",dueAt:"+json.dumps(due)
        urls=[verify(f) for f in files]
        assets=",".join("{image:{url:"+json.dumps(u)+"}}" for u in urls)
        meta="metadata:{instagram:{type:"+kind+(",shouldShareToFeed:true" if feed else ",shouldShareToFeed:false")+",isAiGenerated:true}}"
        gql=("mutation {createPost(input:{text:"+json.dumps(usertext,ensure_ascii=False)
             +",channelId:"+json.dumps(ch["id"])
             +",schedulingType:automatic,mode:"+mode+extra
             +",assets:["+assets+"],aiAssisted:true,"+meta
             +"}) {... on PostActionSuccess{post{id status dueAt text assets{id mimeType}}}"
             +" ... on MutationError{message}}}")
        result=query(gql).get("createPost",{})
        if not isinstance(result,dict) or not result.get("post"):
            raise RuntimeError("Buffer-Fehler "+code+": "+str(result))
        p=result["post"]
        if p.get("status") not in ("scheduled","buffer","sending","sent"):
            raise RuntimeError("Buffer-Status unklar: "+str(p))
        count=len(p.get("assets") or [])
        if count!=len(files):
            raise RuntimeError("Falsche Anzahl Medien bei Buffer: "+str(count))
        print("KFZ BUFFER BUCHUNG",code,"ID",p.get("id"),"STATUS",p.get("status"),
              "DUE",p.get("dueAt"),"MEDIEN",count,"MODE",mode)
        seen.append(p)
if __name__=="__main__":
    main()
