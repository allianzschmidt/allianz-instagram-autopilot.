"""Deterministic, logo-free premium Instagram artwork generator.

Only native shapes and open-source fonts are drawn: no uploaded brand mark,
no person, no photomontage, no external images. Generates fixed, readable
carousel and story images for the signed-off editorial themes.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT/"content/premium_2026_11_12.json").read_text(encoding="utf8"))
BASE = ROOT/"assets/premium_autopilot_v1"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE=(246,250,255); ICE=(149,207,243); PALE=(213,233,245)
NAVY=(5,25,49); DARK=(9,39,69); GOLD=(237,194,114)

def font(sz,bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG,round(sz))

def background(w,h,variant,kind):
    if variant%5==2:
        top,bot=(233,243,249),(181,216,236)
    elif variant%5==4:
        top,bot=(9,55,98),(5,23,47)
    else:
        top,bot=(5,24,48),(18,69,111)
    im=Image.new("RGB",(w,h))
    d=ImageDraw.Draw(im)
    for y in range(h):
        q=y/max(1,h-1)
        rgb=tuple(round((1-q)*a+q*b) for a,b in zip(top,bot))
        d.line((0,y,w,y),fill=rgb,width=1)
    accent=(42,121,170) if variant%5!=2 else (138,193,224)
    d.ellipse((int(w*.44),-int(w*.24),int(w*1.39),int(w*.63)),outline=accent,width=2)
    d.ellipse((int(w*.54),-int(w*.16),int(w*1.27),int(w*.55)),outline=accent,width=2)
    for i in range(10):
        x=int(w*.68+i*42)
        d.line((x,0,x-int(h*.43),h),fill=accent,width=1)
    for j in range(0,9):
        x=85+j*108
        for yy in (int(h*.17),int(h*.83)):
            d.ellipse((x,yy,x+3,yy+3),fill=accent)
    return im

def icon(draw,kind,cx,cy,s,col):
    w=max(9,int(s*.047))
    if kind=="tooth":
        p=[(-.39,-.50),(-.13,-.59),(.12,-.43),(.39,-.50),(.57,-.21),(.38,.21),(.24,.55),(.04,.27),(-.14,.54),(-.34,.27),(-.55,-.14),(-.39,-.50)]
        draw.line([(cx+int(s*x),cy+int(s*y)) for x,y in p],fill=col,width=w,joint="curve")
    elif kind in ("shield","family"):
        p=[(0,-.66),(.54,-.43),(.50,.20),(.29,.53),(0,.71),(-.29,.53),(-.50,.20),(-.54,-.43),(0,-.66)]
        draw.line([(cx+int(s*x),cy+int(s*y)) for x,y in p],fill=col,width=w,joint="curve")
        draw.line([(cx-int(s*.24),cy),(cx-int(s*.03),cy+int(s*.18)),(cx+int(s*.27),cy-int(s*.17))],fill=GOLD,width=w+4,joint="curve")
    elif kind=="car":
        draw.rounded_rectangle((cx-s*.63,cy-s*.12,cx+s*.63,cy+s*.35),radius=int(s*.1),outline=col,width=w)
        draw.line([(cx-s*.42,cy-s*.12),(cx-s*.28,cy-s*.48),(cx+s*.24,cy-s*.48),(cx+s*.41,cy-s*.12)],fill=col,width=w,joint="curve")
        for xx in (-.4,.4):draw.ellipse((cx+s*xx-s*.12,cy+s*.23,cx+s*xx+s*.12,cy+s*.47),outline=GOLD,width=w)
    elif kind=="rain":
        draw.arc((cx-s*.5,cy-s*.46,cx+s*.13,cy+s*.11),180,355,fill=col,width=w)
        draw.arc((cx-s*.07,cy-s*.60,cx+s*.6,cy+s*.11),175,355,fill=col,width=w)
        draw.line((cx-s*.5,cy+s*.07,cx+s*.55,cy+s*.07),fill=col,width=w)
        for xx in (-.35,0,.35):
            draw.line((cx+s*xx,cy+s*.28,cx+s*(xx-.07),cy+s*.55),fill=GOLD,width=w)
    elif kind=="house":
        draw.line([(cx-s*.68,cy),(cx,cy-s*.58),(cx+s*.68,cy)],fill=col,width=w,joint="curve")
        draw.rectangle((cx-s*.48,cy,cx+s*.48,cy+s*.58),outline=col,width=w)
        draw.rectangle((cx-s*.10,cy+s*.25,cx+s*.16,cy+s*.58),outline=GOLD,width=w)
    elif kind=="scales":
        draw.line((cx,cy-s*.6,cx,cy+s*.50),fill=col,width=w)
        draw.line((cx-s*.52,cy-s*.31,cx+s*.52,cy-s*.31),fill=col,width=w)
        for sign in (-1,1):
            xx=cx+sign*s*.42
            draw.line((xx,cy-s*.31,xx,cy+s*.09),fill=col,width=w//2)
            draw.arc((xx-s*.22,cy-s*.04,xx+s*.22,cy+s*.35),0,180,fill=GOLD,width=w)
        draw.line((cx-s*.40,cy+s*.52,cx+s*.40,cy+s*.52),fill=col,width=w)
    else:
        draw.rounded_rectangle((cx-s*.5,cy-s*.44,cx+s*.5,cy+s*.30),radius=25,outline=col,width=w)
        draw.line((cx-s*.2,cy+s*.30,cx-s*.34,cy+s*.52,cx+s*.12,cy+s*.30),fill=col,width=w)
        for j in range(3):draw.ellipse((cx-s*.22+j*s*.22,cy-s*.13,cx-s*.14+j*s*.22,cy-s*.05),fill=GOLD)

def wrap(draw,msg,f,maxwidth):
    lines=[];current=""
    for word in msg.split():
        test=(current+" "+word).strip()
        if draw.textbbox((0,0),test,font=f)[2]<=maxwidth:
            current=test
        else:
            if current:lines.append(current)
            current=word
    if current:lines.append(current)
    return lines

def paragraph(draw,msg,x,y,maxwidth,maxheight,initial,col,bold=False):
    for sz in range(initial,25,-2):
        ft=font(sz,bold)
        lines=wrap(draw,msg,ft,maxwidth)
        spacing=round(sz*1.30)
        if len(lines)*spacing<=maxheight:
            break
    for ln in lines:
        draw.text((x,y),ln,font=ft,fill=col)
        y+=spacing
    return y

def outname(row,number):
    return BASE/row["id"]/f"{number:02d}.jpg"

def feed_image(row,i,head,body,number):
    path=outname(row,number)
    if path.exists():
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    w,h=1080,1350
    im=background(w,h,i,row["icon"])
    d=ImageDraw.Draw(im)
    light=i%5!=2
    ink=WHITE if light else NAVY
    secondary=PALE if light else DARK
    d.rounded_rectangle((65,61,514,126),radius=24,outline=ICE if light else DARK,width=2)
    d.text((88,79),"ALLIANZ AGENTUR SCHMIDT",font=font(23,True),fill=ink)
    d.text((75,170),row["tag"].upper(),font=font(29,True),fill=GOLD if light else DARK)
    d.ellipse((665,245,1030,609),outline=ICE if light else (65,122,161),width=4)
    icon(d,row["icon"],852,425,180,ICE if light else DARK)
    d.line((77,643,1000,643),fill=ICE if light else (74,143,182),width=3)
    paragraph(d,head,78,676,935,230,82,ink,True)
    paragraph(d,body,81,951,925,212,36,secondary)
    d.line((75,1210,1005,1210),fill=ICE if light else DARK,width=2)
    d.text((82,1230),"DÖBELN  ·  VERSICHERUNGSWISSEN",font=font(21,True),fill=secondary)
    d.text((928,1226),f"{number:02d}/{len(row['slides']):02d}",font=font(25,True),fill=secondary)
    im.save(path,"JPEG",quality=93,optimize=True,subsampling=0)

def story_image(day,part):
    date=day["date"]
    path=BASE/"stories"/(date+"_"+part+".jpg")
    if path.exists():return
    path.parent.mkdir(parents=True,exist_ok=True)
    im=background(1080,1920,0 if part=="morning" else 4,day["tag"])
    d=ImageDraw.Draw(im)
    d.text((72,100),"ALLIANZ AGENTUR SCHMIDT",font=font(27,True),fill=WHITE)
    d.text((72,230),"DÖBELN  /  WISSEN STATT MYTHEN",font=font(27),fill=ICE)
    d.ellipse((530,300,1170,940),outline=(54,136,184),width=5)
    icon(d,"chat" if part=="morning" else "shield",840,600,280,ICE)
    label="FRAGE DES TAGES" if part=="morning" else "GUT ZU WISSEN"
    d.text((85,1000),label,font=font(31,True),fill=GOLD)
    subject=day["tag"].upper()
    paragraph(d,subject,80,1071,900,200,75,WHITE,True)
    sentence=day["question"] if part=="morning" else day["answer"]
    paragraph(d,sentence,83,1330,900,370,47,WHITE)
    d.line((70,1780,1010,1780),fill=ICE,width=3)
    d.text((75,1810),"@allianzschmidtdoebeln",font=font(28),fill=PALE)
    im.save(path,"JPEG",quality=92,optimize=True,subsampling=0)

def prepare():
    for row in PLAN["posts"]:
        for index,(head,body) in enumerate(row["slides"]):
            feed_image(row,index,head,body,index+1)
    for d in PLAN["stories"]:
        for part in ("morning","evening"):story_image(d,part)
    expected=sum(len(p["slides"]) for p in PLAN["posts"])+len(PLAN["stories"])*2
    count=len(list(BASE.rglob("*.jpg")))
    print("PREMIUM MEDIEN GENERIERT:",count,"Bilder, mindestens",expected,
          "; keine Logos, keine fremden Personen, keine KI-Sprecher")
if __name__=="__main__":
    prepare()
