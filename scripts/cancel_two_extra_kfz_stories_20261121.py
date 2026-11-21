"""User-authorized reduction: Kfz campaign 21 Nov 2026 = exactly one Story at 20:45 CET.
Cancel only Story S1 12:45 CET and Story S2 18:45 CET. Preserve 15:45 feed
and S3 20:45. All edits scoped to @allianzschmidtdoebeln.
"""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from autopilot import get_channel, posts_from_buffer, query, HANDLE

CANCEL={
 "6b01732add205ed779da6602":("Story 12:45 CET","2026-11-21T11:45:00.000Z","SCHMIDT_KFZ_USER_ORIGINAL_2026_11_21_S1"),
 "6b01732b20a2d09a0af16e8c":("Story 18:45 CET","2026-11-21T17:45:00.000Z","SCHMIDT_KFZ_USER_ORIGINAL_2026_11_21_S2")
}
KEEP={
 "6b01732a510276624515cf54":("FEED 15:45 CET","2026-11-21T14:45:00.000Z","SCHMIDT_KFZ_USER_ORIGINAL_2026_11_21_F1"),
 "6b01732b9ffbc8503c195f78":("EINZIGE STORY 20:45 CET","2026-11-21T19:45:00.000Z","SCHMIDT_KFZ_USER_ORIGINAL_2026_11_21_S3")
}

def main():
 org,ch=get_channel()
 name=ch.get("name","").strip().lstrip("@").lower()
 link=(ch.get("externalLink") or "").rstrip("/").split("/")[-1].lower()
 if name!=HANDLE and link!=HANDLE: raise RuntimeError("Falscher Instagram-Account")
 posts={p["id"]:p for p in posts_from_buffer(org["id"],ch["id"])}
 issues=[]
 for ident,(label,due,marker) in CANCEL.items():
  post=posts.get(ident)
  if not post:
   issues.append(label+" fehlende Buffer ID")
   continue
  if marker not in (post.get("text") or "") or post.get("dueAt")!=due:
   issues.append(label+" unpassender Inhalt/Termin – keine Änderung")
   continue
  state=post.get("status")
  if state=="draft":
   print("BEREITS STORNIERT:",label,ident)
   continue
  if state=="sent":
   print("BEREITS VERÖFFENTLICHT, NICHT RÜCKWIRKEND LÖSCHBAR:",label,ident)
   issues.append(label+" ist schon gesendet")
   continue
  if state not in ("scheduled","buffer"):
   issues.append(label+" unklarer Status "+str(state))
   continue
  gql="mutation {editPost(input:{id:"+json.dumps(ident)+",saveToDraft:true}){ ... on PostActionSuccess{post{id status dueAt}} ... on MutationError{message}}}"
  result=query(gql).get("editPost",{})
  if not isinstance(result,dict) or result.get("post",{}).get("status")!="draft":
   issues.append(label+" von Buffer nicht in Entwurf verschoben: "+str(result))
   continue
  print("STORNIERT / DRAFT:",label,ident)
 latest={p["id"]:p for p in posts_from_buffer(org["id"],ch["id"])}
 for ident,(label,due,marker) in CANCEL.items():
  p=latest.get(ident)
  if p and p.get("status") in ("scheduled","buffer","sending"):
   issues.append("ZUSÄTZLICHE STORY STEHT NOCH AN: "+label+" "+str(p.get("status")))
 for ident,(label,due,marker) in KEEP.items():
  p=latest.get(ident)
  if not p or marker not in (p.get("text") or "") or p.get("dueAt")!=due:
   issues.append("Gewünschter Termin fehlt/ist verändert: "+label)
   continue
  print("BLEIBT BESTEHEN:",label,ident,"STATUS",p.get("status"),"DUE",p.get("dueAt"))
  if p.get("status") not in ("scheduled","buffer","sending","sent"):
   issues.append("Gewünschter Termin nicht geplant: "+label+" "+str(p.get("status")))
 if issues:
  for issue in issues:print("HANDLUNGSBEDARF:",issue)
  raise RuntimeError("Nicht alle gewünschten Änderungen durchgeführt")
 print("ERFOLG: 1 Kfz-Feed 15:45 und NUR 1 Kfz-Story 20:45; übrige Stories gestoppt.")
if __name__=="__main__":
 main()
