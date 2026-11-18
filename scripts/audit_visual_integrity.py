"""Read-only safety audit of the LIVE Buffer queue before publishing.

Fails if ANY rejected design reappears as scheduled or if an active post is not
in the exact human-approved Buffer ID registry. Does NOT automatically remove
someone else's legitimate manual content; it alerts for review instead.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel,posts_from_buffer
from visual_quality_gate import load_manifest

def main():
    manifest=load_manifest()
    allowed=manifest.get("grandfathered_separately_approved_posts",{})
    blocked=set(manifest.get("rejected_buffer_ids",[]))
    org,ch=get_channel()
    entries=posts_from_buffer(org["id"],ch["id"])
    violations=[]
    now=datetime.now(timezone.utc)
    print("VISUELLE QUALITÄTSKONTROLLE",now.isoformat(),"IG @allianzschmidtdoebeln")
    for p in entries:
        status=p.get("status")
        if status not in ("scheduled","buffer","sending"):
            continue
        id=p["id"]
        due=p.get("dueAt")
        if id in blocked:
            violations.append("ABGELEHNTES DESIGN ERNEUT GEPLANT: "+id+" "+str(due))
        elif id not in allowed:
            violations.append("NICHT IM MEDIENFREIGABE-REGISTER: "+id+" "+str(due))
        else:
            print("GEPRÜFTE FREIGEGEBENE BUFFER-ID:",id,"STATUS",status,
                  "TERMIN:",due,"THEMA:",allowed[id])
    if violations:
        for v in violations:print("!!! VISUELLE FREIGABE VERLETZT:",v)
        raise SystemExit("Qualitätsstopp: unbekannte oder abgelehnte Buffer-Einträge entdeckt.")
    print("QUALITÄTSWACHE: Keine abgelehnten/unbekannten Vorlagen in der anstehenden Buffer-Queue.")
if __name__=="__main__":
    main()
