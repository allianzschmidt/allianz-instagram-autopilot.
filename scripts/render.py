"""30 unterschiedlich gestaltete Instagram-Titelgrafiken als ENTWÜRFE.
Keine KI-Personen, keine Allianz-Logos, keine fiktiven Kunden oder Produktzusagen.
Dieses Skript produziert weiterhin Standbilder; v2-Reels/Karussells haben eigene Storyboards.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
FONT_REGULAR = FONT_DIR / "DejaVuSans.ttf"
W, H = 1080, 1350

PALETTES = [
    ((7, 28, 60), (255, 214, 85), (250, 249, 245)),
    ((251, 246, 232), (0, 93, 135), (14, 42, 73)),
    ((13, 72, 77), (255, 192, 117), (255, 250, 238)),
    ((245, 240, 235), (188, 50, 75), (34, 35, 53)),
    ((29, 40, 99), (148, 208, 237), (251, 252, 255)),
    ((247, 250, 253), (19, 119, 183), (24, 53, 79)),
]
TYPES = ["EDITORIAL", "SPLIT", "ILLUSTRATION", "CHECKLIST", "POSTER", "QUESTION"]

def f(size, bold=False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)

def wrap(draw, text, font, width):
    lines, words, current = [], text.split(), ""
    for word in words:
        trial = (current+" "+word).strip()
        if draw.textbbox((0,0), trial, font=font)[2] <= width:
            current=trial
        else:
            if current: lines.append(current)
            current=word
    if current: lines.append(current)
    return lines

def headline(draw, text, x, y, maxw, maxh, color, starting=82, align="left"):
    size=starting
    while size>=34:
        font=f(size,True)
        lines=wrap(draw,text,font,maxw)
        gap=round(size*1.21)
        if len(lines)*gap<=maxh: break
        size-=2
    for line in lines:
        width=draw.textbbox((0,0),line,font=font)[2]
        xx=x if align=="left" else x+(maxw-width)/2
        draw.text((xx,y),line,font=font,fill=color,stroke_width=0)
        y+=gap
    return y

def subline(draw, text, x, y, width, color, fontsize=35, maxheight=170):
    sz=fontsize
    while sz>=22:
        font=f(sz)
        lines=wrap(draw,text,font,width)
        if len(lines)*(sz+12)<=maxheight: break
        sz-=2
    for line in lines:
        draw.text((x,y),line,font=font,fill=color)
        y+=sz+12
    return y

def icon(draw, kind, cx, cy, s, main, secondary):
    """Eigene geometrische Piktogramme, keine Marken-Assets."""
    if kind in ("Kfz","Fahranfänger"):
        draw.rounded_rectangle((cx-s*.80,cy-s*.15,cx+s*.80,cy+s*.35),radius=35,outline=main,width=14)
        draw.polygon([(cx-s*.45,cy-s*.15),(cx-s*.25,cy-s*.52),(cx+s*.33,cy-s*.52),(cx+s*.56,cy-s*.15)],outline=main)
        for dx in (-s*.48,s*.48): draw.ellipse((cx+dx-32,cy+s*.20,cx+dx+32,cy+s*.42),fill=secondary,outline=main,width=9)
    elif kind in ("Wohngebäude","Eigenheim","Erste Wohnung","Hausrat","Mieter"):
        draw.polygon([(cx-s*.8,cy),(cx,cy-s*.64),(cx+s*.8,cy)],outline=main)
        draw.rectangle((cx-s*.57,cy,cx+s*.57,cy+s*.60),outline=main,width=14)
        draw.rectangle((cx-s*.12,cy+s*.23,cx+s*.15,cy+s*.60),outline=main,width=10)
    elif kind in ("Haftpflicht","Versicherungsmythen","Versicherungscheck","Grundlagen"):
        points=[(cx,cy-s*.75),(cx+s*.68,cy-s*.4),(cx+s*.54,cy+s*.38),(cx,cy+s*.75),(cx-s*.54,cy+s*.38),(cx-s*.68,cy-s*.4)]
        draw.line(points+[points[0]],fill=main,width=15,joint="curve")
        draw.line([(cx-s*.29,cy),(cx-s*.05,cy+s*.24),(cx+s*.35,cy-s*.20)],fill=secondary,width=20,joint="curve")
    elif kind in ("Zahnzusatz",):
        draw.ellipse((cx-s*.50,cy-s*.65,cx+s*.50,cy+s*.12),outline=main,width=16)
        draw.line([(cx-s*.45,cy),(cx-s*.18,cy+s*.70),(cx,cy+s*.20),(cx+s*.19,cy+s*.70),(cx+s*.45,cy)],fill=main,width=17,joint="curve")
    elif kind in ("Fahrrad",):
        for dx in (-s*.52,s*.52): draw.ellipse((cx+dx-s*.28,cy-s*.14,cx+dx+s*.28,cy+s*.42),outline=main,width=13)
        draw.line([(cx-s*.52,cy+s*.17),(cx-s*.20,cy-s*.31),(cx+s*.16,cy+s*.17),(cx-s*.52,cy+s*.17),(cx+s*.22,cy-s*.31),(cx+s*.52,cy+s*.17)],fill=secondary,width=14,joint="curve")
    elif kind in ("Selbstbeteiligung","Wartezeit"):
        draw.ellipse((cx-s*.55,cy-s*.55,cx+s*.55,cy+s*.55),outline=main,width=15)
        draw.line([(cx,cy),(cx,cy-s*.35),(cx+s*.31,cy-s*.10)],fill=secondary,width=15)
    else:
        draw.line([(cx-s*.82,cy),(cx-s*.53,cy),(cx-s*.32,cy-s*.30),(cx-s*.03,cy+s*.39),(cx+s*.24,cy-s*.45),(cx+s*.44,cy),(cx+s*.82,cy)],fill=main,width=18,joint="curve")
        draw.ellipse((cx-s*.13,cy-s*.14,cx+s*.13,cy+s*.12),fill=secondary)

def footer(draw, light, dark, num):
    draw.line((72,1200,1008,1200),fill=light,width=3)
    draw.text((72,1225),"AGENTUR SCHMIDT  ·  DÖBELN",font=f(28,True),fill=light)
    draw.text((72,1278),"@allianzschmidtdoebeln  ·  ENTWURF",font=f(25),fill=light)
    draw.text((935,1225),f"{num:02d}",font=f(38,True),fill=light)

def render(post, index):
    base,accent,ink=PALETTES[index%len(PALETTES)]
    variant=TYPES[index%len(TYPES)]
    im=Image.new("RGB",(W,H),base)
    d=ImageDraw.Draw(im)
    n=index+1
    title=post["title"]
    subtitle=post["subtitle"]
    cat=post["category"].upper()
    contrast=ink if index%6 in (0,2,4) else base
    # Variant 1: dramatic editorial dark layout, overprinted illustration right
    if variant=="EDITORIAL":
        d.rectangle((0,0,W,18),fill=accent)
        d.text((74,80),"VERSICHERUNGSWISSEN",font=f(35,True),fill=accent)
        d.rounded_rectangle((72,178,365,243),radius=30,fill=accent)
        d.text((94,197),cat[:21],font=f(24,True),fill=base)
        d.ellipse((612,330,1118,870),fill=(26,66,93))
        icon(d,post["category"],838,575,180,accent,ink)
        y=headline(d,title,72,320,690,520,ink,77)
        d.rounded_rectangle((70,905,1000,1105),radius=28,outline=accent,width=5)
        subline(d,subtitle,110,952,840,ink,36)
        footer(d,ink,base,n)
    # Variant 2: off-white split editorial poster
    elif variant=="SPLIT":
        d.rectangle((0,0,540,H),fill=base)
        d.rectangle((540,0,W,H),fill=accent)
        d.text((70,90),"SCHMIDT / DÖBELN",font=f(29,True),fill=ink)
        d.rounded_rectangle((68,208,482,277),radius=22,fill=accent)
        d.text((90,225),cat[:20],font=f(25,True),fill=base)
        icon(d,post["category"],807,550,235,base,ink)
        headline(d,title,70,365,455,680,ink,68)
        d.rectangle((55,1080,1025,1162),fill=ink)
        subline(d,subtitle,75,1101,920,base,27,maxheight=50)
        footer(d,ink,base,n)
    # Variant 3: bold illustration with curved yellow stage, title bottom
    elif variant=="ILLUSTRATION":
        d.ellipse((-220,-450,1300,790),fill=accent)
        d.text((77,75),"AGENTUR SCHMIDT",font=f(35,True),fill=ink)
        d.text((77,125),"WISSEN STATT VERSICHERUNGSCHINESISCH",font=f(23),fill=ink)
        icon(d,post["category"],540,417,245,base,ink)
        d.rounded_rectangle((50,740,1027,1110),radius=34,fill=ink)
        headline(d,title,95,795,905,238,base,62)
        subline(d,subtitle,85,1118,920,accent,27,maxheight=70)
        footer(d,ink,base,n)
    # Variant 4: checklist / notepad
    elif variant=="CHECKLIST":
        d.rounded_rectangle((45,53,1035,1164),radius=45,fill=(255,255,252))
        for k in range(12):
            yy=113+k*85
            d.line((90,yy,982,yy),fill=(221,232,243),width=3)
        d.text((94,96),"CHECKLISTE  •  VERSICHERUNGEN",font=f(29,True),fill=ink)
        d.rounded_rectangle((88,204,385,274),radius=14,fill=accent)
        d.text((112,223),cat[:21],font=f(24,True),fill=(255,255,255))
        headline(d,title,95,360,830,475,ink,75)
        d.rounded_rectangle((86,908,988,1073),radius=26,fill=(248,231,232))
        subline(d,subtitle,116,955,835,ink,31)
        footer(d,ink,base,n)
    # Variant 5: dramatic centered mono headline with small illustration + motif
    elif variant=="POSTER":
        for x in range(12):
            for y in range(14):
                if (x+y)%3==0:
                    d.ellipse((x*100+10,y*100+15,x*100+16,y*100+21),fill=accent)
        d.rectangle((70,75,1009,160),outline=accent,width=5)
        d.text((100,94),"VERSICHERUNGS-CHECK  /  "+cat[:16],font=f(26,True),fill=ink)
        d.ellipse((350,207,730,593),fill=accent)
        icon(d,post["category"],540,406,146,base,ink)
        headline(d,title,85,640,910,325,ink,80,align="center")
        d.rectangle((78,1040,1002,1128),fill=accent)
        subline(d,subtitle,102,1060,850,base,30,maxheight=72)
        footer(d,ink,base,n)
    # Variant 6: bright question card with geometric stickers
    else:
        d.ellipse((790,-180,1290,370),fill=accent)
        d.ellipse((-230,790,300,1290),outline=accent,width=28)
        d.text((70,83),"DIE FRAGE DER WOCHE",font=f(31,True),fill=ink)
        d.rounded_rectangle((72,209,420,283),radius=34,fill=accent)
        d.text((94,228),cat[:21],font=f(27,True),fill=(255,255,255))
        d.ellipse((788,326,1023,562),outline=ink,width=12)
        d.text((846,330),"?",font=f(152,True),fill=ink)
        headline(d,title,70,390,900,495,ink,84)
        d.rounded_rectangle((68,996,1013,1122),radius=25,fill=accent)
        subline(d,subtitle,99,1026,875,(255,255,255),29,maxheight=100)
        footer(d,ink,base,n)
    out=ROOT/post["asset"]
    out.parent.mkdir(parents=True,exist_ok=True)
    im.save(out,"JPEG",quality=91,optimize=True)
    return out

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    for i,p in enumerate(posts):render(p,i)
    print(f"{len(posts)} deutlich variierte Entwurfs-Cover erzeugt. Nicht zur Veröffentlichung freigegeben.")

if __name__=="__main__":
    main()
