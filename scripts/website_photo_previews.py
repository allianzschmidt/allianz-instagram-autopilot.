"""Sechs öffentliche Website-Fotomotive als NICHT FREIGEGEBENE Instagram-Vorschau gestalten.

Quelle: website_media.json. Es werden keine Bilder generiert oder Personen erfunden.
Bilder bleiben ENTWURF und werden von Buffer nicht automatisch veröffentlicht.
"""
import io
import json
import os
import ssl
import sys
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"assets"/"website_previews"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NAVY=(6,31,66)
BLUE=(0,118,187)
YELLOW=(255,219,71)
WHITE=(255,255,255)
GRAY=(207,222,232)
W,H=1080,1350

def f(n,bold=False):
    return ImageFont.truetype(BOLD if bold else FONT,n)

def get_image(url):
    if not (url.startswith("https://vertretung.allianz.de/ralf.schmidt2/") or
            url.startswith("https://www.mein-doebeln.de/img/firmen/image_fotos/orig/")):
        raise ValueError("Quell-URL nicht freigegeben")
    req=urllib.request.Request(url,headers={
        "User-Agent":"Mozilla/5.0 (compatible; PreviewRenderer/1.0)",
        "Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
    })
    with urllib.request.urlopen(req,timeout=25) as resp:
        if not resp.headers.get("Content-Type","").lower().startswith("image/"):
            raise ValueError("Nicht Bildcontent: "+resp.headers.get("Content-Type",""))
        buf=resp.read(12*1024*1024+1)
    if len(buf)>12*1024*1024: raise ValueError("Bild zu groß")
    img=Image.open(io.BytesIO(buf))
    img.load()
    return ImageOps.exif_transpose(img).convert("RGB")

def lines(draw,text,ft,maxw):
    out=[]
    part=""
    for word in text.split():
        trial=(part+" "+word).strip()
        if draw.textbbox((0,0),trial,font=ft)[2]>maxw and part:
            out.append(part);part=word
        else:part=trial
    if part:out.append(part)
    return out

def cover_fit(image, size):
    # Eine ruhige Vollbild-Nutzung ohne Gesichtsmorphing oder synthetische Retusche.
    dst=Image.new("RGB",size,(215,224,232))
    fitted=ImageOps.contain(image,size,Image.Resampling.LANCZOS)
    dst.paste(fitted,((size[0]-fitted.width)//2,(size[1]-fitted.height)//2))
    return dst

def make(item,i):
    source=get_image(item["src"])
    pic=cover_fit(source,(960,710 if i else 745))
    out=Image.new("RGB",(W,H),NAVY)
    d=ImageDraw.Draw(out)
    d.rectangle((0,0,W,18),fill=YELLOW)
    d.text((60,53),"SCHMIDT  /  DÖBELN",font=f(35,True),fill=WHITE)
    d.rounded_rectangle((62,126,386,186),radius=23,fill=BLUE)
    d.text((86,142),"EINBLICK VOR ORT",font=f(24,True),fill=WHITE)
    photo_y=230
    out.paste(pic,(60,photo_y))
    d=ImageDraw.Draw(out)
    y=1023
    title=item["label"] if item["kind"]=="person" else "Willkommen in Döbeln"
    fontsize=63 if len(title)<=23 else 52
    for line in lines(d,title,f(fontsize,True),925):
        d.text((65,y),line,font=f(fontsize,True),fill=WHITE)
        y+=fontsize+11
    d.text((66,min(1210,y+6)),item["role"],font=f(32),fill=GRAY)
    d.line((65,1264,1015,1264),fill=YELLOW,width=3)
    d.text((65,1292),"@allianzschmidtdoebeln   ·   ENTWURF",font=f(24),fill=WHITE)
    target=OUTPUT/(item["id"]+".jpg")
    out.save(target,quality=90,optimize=True)
    print("Entwurf erstellt:",target)

def main():
    config=json.loads((ROOT/"website_media.json").read_text(encoding="utf-8"))
    if config.get("publication_approved") is True:
        raise RuntimeError("Bildgenerator erzeugt ausschließlich Entwürfe; kein Veröffentlichungsflag setzen")
    OUTPUT.mkdir(parents=True,exist_ok=True)
    successful=0
    for i,item in enumerate(config["assets"]):
        try:
            make(item,i)
            successful+=1
        except Exception as exc:
            print("WARNUNG Quellbild nicht verfügbar: "+item["id"]+" / "+str(exc),file=sys.stderr)
    if successful==0:
        raise RuntimeError("Keine Originalbilder abrufbar; bitte Mediaquellen prüfen.")
    print(f"Erstellt: {successful}/{len(config['assets'])} Bildentwürfe.")
if __name__=="__main__":
    main()
