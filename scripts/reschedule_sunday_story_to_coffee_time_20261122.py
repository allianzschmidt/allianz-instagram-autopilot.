"""User-requested one-off reschedule: Sunday 22 Nov 2026 Instagram Story
from 20:15 to 16:00 Europe/Berlin (15:00 UTC), fitting afternoon coffee.
Only edit this single post, no duplicate creation, no image changes.
"""
import json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel, posts_from_buffer, query, HANDLE

POST_ID="6b02fd3dd5eabfb8ccb562d9"
MARKER="SCHMIDT_SONNTAG_PREMIUM_2026_11_22_2015"
OLD="2026-11-22T19:15:00.000Z"
NEW="2026-11-22T15:00:00.000Z"  # 16:00 CET

def main():
 org,ch=get_channel()
 name=ch["name"].strip().lstrip("@").lower()
 link=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
 if name!=HANDLE and link!=HANDLE:raise RuntimeError("Falscher Instagram-Account")
 posts=posts_from_buffer(org["id"],ch["id"])
 post=next((p for p in posts if p.get("id")==POST_ID),None)
 if not post:raise RuntimeError("Gesuchte Sonntags-Story fehlt – keine neue Kopie anlegen")
 if MARKER not in (post.get("text") or ""):
  raise RuntimeError("Falscher Story-Inhalt – keine Änderung")
 if post.get("dueAt")==NEW:
  print("SONNTAGS-STORY BEREITS AUF KAFFEEZEIT:",POST_ID,post["status"],NEW)
  return
 if post.get("status") not in ("scheduled","buffer"):
  raise RuntimeError("Story kann nicht mehr geändert werden; Status "+str(post.get("status")))
 if post.get("dueAt")!=OLD:
  raise RuntimeError("Unbekannter Originaltermin: "+str(post.get("dueAt")))
 if datetime.now(timezone.utc)>=datetime.fromisoformat(NEW.replace("Z","+00:00")):
  raise RuntimeError("16 Uhr ist bereits erreicht; nicht rückwirkend planen")
 if any(p.get("id")!=POST_ID and p.get("dueAt")==NEW and p.get("status") in ("scheduled","buffer","sending")
        for p in posts):
  raise RuntimeError("16:00 ist bereits belegt")
 gql=("mutation {editPost(input:{id:"+json.dumps(POST_ID)+",mode:customScheduled,dueAt:"+json.dumps(NEW)+
      "}){... on PostActionSuccess{post{id status dueAt text}} ... on MutationError{message}}}")
 result=query(gql).get("editPost",{})
 if not isinstance(result,dict) or not result.get("post"):
  raise RuntimeError("Buffer hat Zeitänderung abgelehnt: "+str(result))
 edited=result["post"]
 if edited.get("id")!=POST_ID or edited.get("dueAt")!=NEW or edited.get("status") not in ("scheduled","buffer"):
  raise RuntimeError("Buffer hat 16:00 nicht bestätigt: "+str(edited))
 refreshed=posts_from_buffer(org["id"],ch["id"])
 updated=next((p for p in refreshed if p["id"]==POST_ID),None)
 if not updated or updated.get("dueAt")!=NEW or updated.get("status") not in ("scheduled","buffer"):
  raise RuntimeError("Nachkontrolle schlägt fehl: "+str(updated))
 if sum(1 for p in refreshed if MARKER in (p.get("text") or "") and p.get("status") in ("scheduled","buffer","sending"))!=1:
  raise RuntimeError("Doppelte Sonntags-Stories in Buffer")
 print("ERFOLG: EINZIGE SONNTAGS-STORY AUF 16:00 UHR VERSCHOBEN:",updated)
if __name__=="__main__":
 main()
