"""Sicherer Buffer Autopilot: nur freigegebene Instagram-Beiträge."""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLE = "allianzschmidtdoebeln"
API = "https://api.buffer.com"

def query(gql):
    key = os.getenv("BUFFER_API_KEY", "").strip()
    if not key:
        raise RuntimeError("BUFFER_API_KEY fehlt: GitHub Actions Secret hinterlegen.")
    body = json.dumps({"query": gql}, ensure_ascii=False).encode()
    req = urllib.request.Request(
        API, data=body, method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "User-Agent": "AllianzDoebelnAutopilot/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.load(resp)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Buffer HTTP-Fehler " + str(exc.code)) from exc
    if result.get("errors"):
        raise RuntimeError("Buffer GraphQL: " + str(result["errors"])[:700])
    return result.get("data", {})

def get_channel():
    data = query("query { account { organizations { id name } } }")
    matched = []
    for org in data["account"]["organizations"]:
        gql = 'query { channels(input:{organizationId:' + json.dumps(org["id"]) + '}) {id name service isDisconnected isLocked isQueuePaused externalLink timezone} }'
        for ch in query(gql)["channels"]:
            if ch["service"].lower() != "instagram":
                continue
            actual = ch["name"].strip().lstrip("@").lower()
            link = (ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
            if actual == HANDLE or link == HANDLE:
                matched.append((org, ch))
    if len(matched) != 1:
        raise RuntimeError(f"Erwartet genau ein Instagram-Konto @{HANDLE}, gefunden {len(matched)}. Nichts wird geplant.")
    org, ch = matched[0]
    if ch["isDisconnected"] or ch["isLocked"] or ch["isQueuePaused"]:
        raise RuntimeError("Instagram-Konto nicht verfügbar oder Queue pausiert.")
    return org, ch

def posts_from_buffer(org_id, channel_id, with_metrics=False):
    posts, cursor = [], None
    for _ in range(8):
        after = ",after:" + json.dumps(cursor) if cursor else ""
        fields = "id text status dueAt" + (" metrics {type name value unit} metricsUpdatedAt" if with_metrics else "")
        gql = (
            "query { posts(first:100" + after + ",input:{organizationId:" + json.dumps(org_id)
            + ",filter:{channelIds:[" + json.dumps(channel_id) + "]}})"
            + "{edges{node{" + fields + "}} pageInfo{hasNextPage endCursor}}}"
        )
        page = query(gql)["posts"]
        posts.extend(x["node"] for x in page.get("edges", []))
        if not page["pageInfo"].get("hasNextPage"):
            break
        cursor = page["pageInfo"].get("endCursor")
        if not cursor:
            break
    return posts

def asset_url(item):
    repo = os.getenv("GITHUB_REPOSITORY", "").strip()
    branch = os.getenv("GITHUB_REF_NAME", "main").strip()
    if repo != "allianzschmidt/allianz-instagram-autopilot.":
        raise RuntimeError("Falsches GitHub Repository; Veröffentlichungen gesperrt.")
    return "https://raw.githubusercontent.com/" + repo + "/" + branch + "/" + item["asset"]

def verify_image(url):
    req = urllib.request.Request(url, headers={"User-Agent": "AllianzDoebelnAutopilot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status != 200 or not resp.headers.get("Content-Type", "").startswith("image/"):
                raise RuntimeError("Kein öffentlich abrufbares Bild: " + url)
    except urllib.error.URLError as exc:
        raise RuntimeError("Bild nicht abrufbar: " + str(exc)) from exc

def note(message):
    print(message)
    summary = os.getenv("GITHUB_STEP_SUMMARY", "")
    if summary:
        with open(summary, "a", encoding="utf-8") as fp:
            fp.write(message + "\n")

def do_publish(drafts):
    if os.getenv("PUBLISH_ENABLED", "").lower() != "true":
        note("⏸️ Veröffentlichungen AUS (PUBLISH_ENABLED != true).")
        return
    if os.getenv("LEGAL_APPROVED", "").lower() != "true":
        note("⏸️ Agenturfreigabe fehlt (LEGAL_APPROVED != true).")
        return
    org, ch = get_channel()
    old = posts_from_buffer(org["id"], ch["id"])
    already = {p["text"] for p in old}
    outstanding = sum(x.get("status") in ("buffer", "scheduled", "sending") for x in old)
    if outstanding >= 9:  # Buffer Free: maximal 10 geplante Beiträge
        note("⏸️ Buffer-Warteschlange voll oder fast voll; kein weiterer Beitrag.")
        return
    eligible = [p for p in drafts if p["approved"] is True and p["caption"] not in already]
    if not eligible:
        note("⏸️ Keine individuell freigegebenen neuen Beiträge.")
        return
    post = eligible[0]
    url = asset_url(post)
    verify_image(url)
    mutation = (
        "mutation {createPost(input:{text:" + json.dumps(post["caption"], ensure_ascii=False)
        + ",channelId:" + json.dumps(ch["id"])
        + ",schedulingType:automatic,mode:addToQueue"
        + ",assets:[{image:{url:" + json.dumps(url) + "}}]"
        + ",aiAssisted:true"
        + ",metadata:{instagram:{type:post,shouldShareToFeed:true,isAiGenerated:true}}"
        + "}){... on PostActionSuccess{post{id dueAt status}} ... on MutationError{message}}}"
    )
    result = query(mutation)["createPost"]
    if not result or "post" not in result:
        raise RuntimeError("Buffer hat nicht eingeplant: " + str(result))
    note(f"✅ Nur @{HANDLE}: {post['id']} in Buffer eingeplant (Post-ID {result['post']['id']}).")

def do_report(drafts):
    org, ch = get_channel()
    all_posts = posts_from_buffer(org["id"], ch["id"], with_metrics=True)
    known = {p["caption"]: p for p in drafts}
    campaign = [p for p in all_posts if p["text"] in known]
    counts = Counter(x["status"] for x in campaign)
    note("# Allianz Döbeln – Wochenanalyse")
    note(f"**Kanal:** @{HANDLE} | **Erfasst:** {len(campaign)} | **Veröffentlicht:** {counts['sent']} | **Geplant:** {counts['buffer'] + counts['scheduled']} | **Fehler:** {counts['error']}")
    ranked = []
    for p in campaign:
        if p["status"] != "sent":
            continue
        values = {m["type"]: m["value"] for m in (p.get("metrics") or [])}
        ranked.append((values.get("reach", values.get("impressions", values.get("reactions", 0))), known[p["text"]]["id"], values))
    ranked.sort(reverse=True)
    note("## Beiträge nach bisheriger Reichweite/Interaktion (nur verfügbare Buffer-Metriken)")
    if not ranked:
        note("Noch keine veröffentlichten Beiträge mit abrufbaren Daten.")
    for score, post_id, metrics in ranked[:10]:
        ms = ", ".join(str(k) + ": " + str(v) for k, v in metrics.items()) if metrics else "Noch keine Insights"
        note(f"- {post_id}: {ms}")
    note("**Hinweis:** Buffer aktualisiert die Metriken etwa täglich. Fehlende Metrik bedeutet nicht Null. Neue Kundenanfragen können hier nicht erkannt werden.")
    if counts["error"]:
        note("⚠️ Fehlerhafte Buffer-Beiträge prüfen!")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["validate", "publish", "report", "list"])
    args = parser.parse_args()
    items = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
    assert len({p["id"] for p in items}) == len(items)
    if args.action == "list":
        for p in items:
            print(p["id"], "FREIGEGEBEN" if p["approved"] else "ENTWURF", p["title"])
    elif args.action == "validate":
        org, ch = get_channel()
        note(f"✅ Verifiziert: @{HANDLE} | Buffer-ID: {ch['id']} | Zeitzone: {ch['timezone']}")
    elif args.action == "publish":
        do_publish(items)
    elif args.action == "report":
        do_report(items)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("FEHLER: " + str(exc), file=sys.stderr)
        sys.exit(1)
