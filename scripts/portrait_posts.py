"""Gestaltet fünf NICHT FREIGEGEBENE Instagram-Entwürfe nur mit dem Nutzerporträt.

Die Vorlage muss aus assets/portrait/paul_schmidt.jpg stammen.
Keine weiteren Personen-/Bildquellen und keine synthetische Gesichtserzeugung.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"assets"/"portrait"/"paul_schmidt.jpg"
OUT=ROOT/"assets"/"portrait_cards"
W,H=1080,1350
NAVY=(8,34,73)
BLUE=(12,122,197)
GOLD=(252,211,75)
CREAM=(248,246,239)
WHITE=(255,255,255)
INK=(24,50,79)
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

POSTS=[
 {"id":"01","title":"Persönlich für dich da.","subtitle":"Versicherungsberatung in Döbeln","category":"Kennenlernen","style":"left"},
 {"id":"02","title":"Wer schützt eigentlich dein Einkommen?","subtitle":"Berufsunfähigkeit verständlich erklärt","category":"BU-Wissen","style":"split"},
 {"id":"03","title":"3 Fragen vor jedem Versicherungsabschluss","subtitle":"Risiko. Leistung. Ausschlüsse.","category":"Versicherungscheck","style":"light"},
 {"id":"04","title":"Deine Fragen. Verständliche Antworten.","subtitle":"Versicherungstipps aus Döbeln","category":"Frag Paul","style":"bottom"},
 {"id":"05","title":"Nicht irgendein Vertrag. Sondern der passende.","subtitle":"Persönliche Beratung in deiner Nähe","category":"Beratung","style":"editorial"},
]

def font(size,bold=False):
 return ImageFont.truetype(BOLD if bold else REGULAR,size)

def wrap(draw,t,fo,maxwidth):
 words=t.split();lines=[];line=""
 for word in words:
  candidate=(line+" "+word).strip()
  if line and draw.textbbox((0,0),candidate,font=fo)[2]>maxwidth:
   lines.append(line);line=word
  else:line=candidate
 if line:lines.append(line)
 return lines

def title_text(d,text,rect,color,start=65):
 x,y,width,maxheight=rect
 for sz in range(start,30,-2):
  fo=font(sz,True)
  lines=wrap(d,text,fo,width)
  if len(lines)*(sz+16)<=maxheight:break
 for line in lines:
  d.text((x,y),line,font=fo,fill=color)
  y+=sz+16

def preview(photo,item,index):
 im=Image.new("RGB",(W,H),NAVY if index in (0,1,3) else CREAM)
 d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,15),fill=GOLD)
 layout=item["style"]
 if layout in ("left","bottom","editorial"):
  if layout=="left":
   x,y,pw,ph=60,165,960,680
  elif layout=="bottom":
   x,y,pw,ph=60,375,960,630
  else:
   x,y,pw,ph=60,140,960,745
  # Vollständig sichtbares Porträt: keine Gesichtsretusche und keine Gesichtserzeugung
  pic=ImageOps.contain(photo,(pw,ph),Image.Resampling.LANCZOS)
  im.paste(pic,(x+(pw-pic.width)//2,y+(ph-pic.height)//2))
  d=ImageDraw.Draw(im)
  if layout=="bottom":
   d.text((70,72),"FRAG PAUL  •  ALLIANZ DÖBELN",font=font(31,True),fill=GOLD)
   title_text(d,item["title"],(78,180,910,155),WHITE,64)
   d.rectangle((44,1050,1032,1219),fill=BLUE)
   d.text((78,1088),item["subtitle"],font=font(30),fill=WHITE)
  else:
   d.text((72,68),"ALLIANZ AGENTUR SCHMIDT  ·  DÖBELN",font=font(28,True),fill=GOLD)
   d.rectangle((45,900,1037,1165),fill=NAVY if layout=="editorial" else BLUE)
   title_text(d,item["title"],(72,932,930,155),WHITE,61)
   d.text((77,1128),item["subtitle"],font=font(26),fill=CREAM)
 elif layout=="split":
  d.rectangle((0,0,550,H),fill=CREAM)
  d.rectangle((550,0,W,H),fill=NAVY)
  pic=ImageOps.contain(photo,(490,720),Image.Resampling.LANCZOS)
  im.paste(pic,(560+(510-pic.width)//2,280+(720-pic.height)//2))
  d=ImageDraw.Draw(im)
  d.text((58,79),"BU-WISSEN",font=font(36,True),fill=BLUE)
  title_text(d,item["title"],(57,275,440,620),INK,68)
  d.rectangle((55,1007,520,1151),fill=BLUE)
  d.text((72,1035),"Was wäre, wenn",font=font(31,True),fill=WHITE)
  d.text((72,1085),"Einkommen ausfällt?",font=font(25),fill=WHITE)
  d.text((600,1155),item["subtitle"],font=font(23),fill=WHITE)
 elif layout=="light":
  d.rectangle((0,0,W,210),fill=BLUE)
  d.text((62,76),"CHECKLISTE  ·  MIT PAUL",font=font(34,True),fill=WHITE)
  title_text(d,item["title"],(63,260,930,245),INK,75)
  pic=ImageOps.contain(photo,(460,545),Image.Resampling.LANCZOS)
  im.paste(pic,(570+(460-pic.width)//2,550+(545-pic.height)//2))
  d=ImageDraw.Draw(im)
  for j,txt in enumerate(("RISIKO?","LEISTUNG?","AUSSCHLÜSSE?")):
   yy=600+j*145
   d.rounded_rectangle((60,yy,115,yy+55),radius=9,outline=BLUE,width=6)
   d.text((135,yy+5),txt,font=font(28,True),fill=INK)
  d.text((64,1148),item["subtitle"],font=font(31,True),fill=INK)
 d.line((55,1260,1022,1260),fill=GOLD,width=4)
 d.text((65,1282),"@allianzschmidtdoebeln  ·  ENTWURF",font=font(24),fill=WHITE if index in (0,3) else INK)
 dest=OUT/("paul_"+item["id"]+".jpg")
 im.save(dest,"JPEG",quality=92,optimize=True)
 print(dest)

def main():
 if not SRC.exists():
  raise SystemExit("Nur einrichtungsbereit: Bitte das eigene Porträt zuerst nach assets/portrait/paul_schmidt.jpg hochladen.")
 OUT.mkdir(parents=True,exist_ok=True)
 im=Image.open(SRC); im=ImageOps.exif_transpose(im).convert("RGB")
 for i,item in enumerate(POSTS):preview(im,item,i)
 print("5 persönliche Entwürfe generiert; nichts automatisch zur Veröffentlichung freigegeben.")
if __name__=="__main__":main()
