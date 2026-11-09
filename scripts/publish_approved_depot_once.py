"""Einmalige, vom Nutzer ausdrücklich freigegebene Altersvorsorgedepot-Karussell-Veröffentlichung.

KEINE alten posts.json-Items, KEINE KI-Sprecher-Videos und KEINE Logos.
Das Ziel wird vor jeder Änderung auf @allianzschmidtdoebeln geprüft.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from autopilot import HANDLE, get_channel, posts_from_buffer, query

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "approved_depot2027"
EXPECTED = [f"{i:02d}.jpg" for i in range(1, 6)]

CAPTION = (
    "2027 bringt neue Möglichkeiten für die private Altersvorsorge! 📈\n\n"
    "Mit dem neuen geförderten Altersvorsorgedepot kommen künftig auch Anlagen in "
    "Fonds und ETFs ohne Beitragsgarantie infrage. Das bietet Chancen, bringt "
    "aber auch Wertschwankungen und Verlustrisiken mit sich.\n\n"
    "Du hast bereits einen Riester-Vertrag? Bestehende Verträge können "
    "weitergeführt werden. Ob ein Wechsel sinnvoll ist, hängt von deiner "
    "persönlichen Situation ab.\n\n"
    "📍 Allianz Agentur Schmidt · Döbeln\n"
    "💬 Schreib uns „DEPOT“ per Nachricht, wenn du dich unverbindlich informieren möchtest.\n\n"
    "Informationen zum Reformstart 2027. Förderung und Eignung hängen von "
    "deinen persönlichen Voraussetzungen ab. Keine Rendite- oder Leistungszusage.\n\n"
    "#Altersvorsorgedepot #Altersvorsorge #Döbeln #Rente2027 #Mittelsachsen"
)

def main():
    if os.getenv("GITHUB_REPOSITORY", "") != "allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Falsches Repository, Veröffentlichung blockiert")
    if os.getenv("CONFIRMED_MEDIA_RELEASE", "") != "approved-depot-2027-5-slides":
        raise RuntimeError("Einmalige Nutzerfreigabe nicht gesetzt")
    if os.getenv("BUFFER_API_KEY", "").strip() == "":
        raise RuntimeError("Buffer API-Schlüssel fehlt")
    if len(EXPECTED) != 5 or any(not (ASSET_DIR / n).is_file() for n in EXPECTED):
        raise RuntimeError("Nicht alle fünf Original-Slides vorhanden")
    for name in EXPECTED:
        with open(ASSET_DIR / name, "rb") as f:
            h = f.read(3)
        if h != b"\xff\xd8\xff":
            raise RuntimeError("Kein gültiges JPEG: " + name)

    org, channel = get_channel()
    if channel["name"].strip().lstrip("@").lower() != HANDLE and (
       (channel.get("externalLink") or "").rstrip("/").split("/")[-1].lower() != HANDLE
    ):
        raise RuntimeError("Falscher Instagram-Kanal, sofortiger Stopp")
    old = posts_from_buffer(org["id"], channel["id"])
    if any("2027 bringt neue Möglichkeiten für die private Altersvorsorge!" in (p.get("text") or "") for p in old):
        print("✅ Ein identisches Depot-Karussell ist bereits in Buffer vorhanden. Keine Doppelveröffentlichung.")
        return

    root = "https://raw.githubusercontent.com/allianzschmidt/allianz-instagram-autopilot./main/assets/approved_depot2027/"
    urls = [root + name for name in EXPECTED]
    for url in urls:
        req = urllib.request.Request(url, headers={"User-Agent": "SchmidtInstagramCampaign/1.0"})
        with urllib.request.urlopen(req, timeout=40) as resp:
            typ = resp.headers.get("Content-Type", "")
            prefix = resp.read(3)
            if resp.status != 200 or not typ.startswith("image/") or prefix != b"\xff\xd8\xff":
                raise RuntimeError("Originalbild öffentlich noch nicht abrufbar: " + url)
    assets = ",".join("{image:{url:" + json.dumps(u) + "}}" for u in urls)
    mutation = (
        "mutation { createPost(input:{"
        "text:" + json.dumps(CAPTION, ensure_ascii=False)
        + ",channelId:" + json.dumps(channel["id"])
        + ",schedulingType:automatic,mode:shareNow,"
        + "assets:[" + assets + "],"
        + "aiAssisted:true,"
        + "metadata:{instagram:{type:post,shouldShareToFeed:true,isAiGenerated:true}}"
        + "}) { ... on PostActionSuccess { post { id status dueAt text assets { id mimeType } } }"
        + " ... on MutationError { message } } }"
    )
    result = query(mutation).get("createPost", {})
    if not isinstance(result, dict) or "post" not in result:
        raise RuntimeError("Buffer hat NICHT veröffentlicht/eingeplant: " + str(result))
    post = result["post"]
    print("✅ BUFFER HAT ANGENOMMEN")
    print("Instagram: @" + HANDLE)
    print("Post-ID: " + str(post.get("id")))
    print("Status: " + str(post.get("status")))
    print("Zeitpunkt: " + str(post.get("dueAt")))
    print("Bildanzahl: " + str(len(post.get("assets", []))))
    if len(post.get("assets", [])) != 5:
        print("⚠️ Prüfen: Die API meldet nicht exakt fünf Assets.")
    print("Achtung: Erst Status 'sent' beweist eine abgeschlossene Veröffentlichung.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("❌ VERÖFFENTLICHUNG NICHT BESTÄTIGT: " + str(exc), file=sys.stderr)
        sys.exit(1)
