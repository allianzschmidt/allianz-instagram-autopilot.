"""Fail-closed, per-asset media approval gate for @allianzschmidtdoebeln.

A general series-level toggle is NEVER enough. Only visual files with explicit
individual user approval plus an exact SHA256 digest are publishable.
This does not make automated aesthetic judgement; human approval is still needed.
"""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"content/visual_approval_manifest.json"
ACCOUNT="allianzschmidtdoebeln"

def load_manifest():
    j=json.loads(MANIFEST.read_text(encoding="utf8"))
    if j.get("version")!=1 or j.get("account")!=ACCOUNT:
        raise RuntimeError("Medienfreigabe fehlt oder Konto falsch.")
    return j

def require_approved_media(repo_paths):
    manifest=load_manifest()
    registry=manifest.get("media",{})
    blocked=manifest.get("explicitly_rejected_prefixes",[])
    for raw in repo_paths:
        rel=Path(raw)
        key=rel.as_posix()
        if rel.is_absolute() or ".." in rel.parts or not key.startswith("assets/"):
            raise RuntimeError("Ungültiger Medienpfad: "+key)
        if any(key.startswith(prefix) for prefix in blocked):
            raise RuntimeError("Ausdrücklich abgelehnte Medienserie darf NICHT gepostet werden: "+key)
        item=registry.get(key)
        if not item or item.get("approved") is not True or item.get("user_visual_approval") is not True:
            raise RuntimeError("Individuelle Bild-Freigabe fehlt: "+key)
        digest=item.get("sha256","")
        if len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest):
            raise RuntimeError("Keine gültige SHA256-Prüfsumme für "+key)
        path=ROOT/rel
        if not path.is_file():
            raise RuntimeError("Freigegebene Datei fehlt: "+key)
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=actual:
            raise RuntimeError("Freigabe gilt nicht für geänderte Bilddatei: "+key)
        print("EXAKT FREIGEGEBENE MEDIA SHA256:",key,actual)
    return True
