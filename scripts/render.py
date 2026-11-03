"""Erstellt 30 eigene Instagram-Bilder zu freigegebenen Textentwürfen."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
BOLD = str(FONT_DIR / "DejaVuSans-Bold.ttf")
REGULAR = str(FONT_DIR / "DejaVuSans.ttf")
SIZE = (1080, 1350)
NAVY = (10, 28, 51)
WHITE = (244, 249, 255)
PALE = (183, 207, 224)
CYAN = (0, 166, 214)

def font(px, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, px)

def fit_lines(draw, s, fnt, width):
    lines, current = [], ""
    for word in s.split():
        attempt = (current + " " + word).strip()
        if draw.textbbox((0, 0), attempt, font=fnt)[2] < width:
            current = attempt
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def render(post):
    image = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(image)
    for y in range(SIZE[1]):
        frac = y / SIZE[1]
        draw.line((0, y, SIZE[0], y), fill=(10, round(28 + 18 * frac), round(51 + 25 * frac)))
    draw.ellipse((610, -120, 1280, 540), outline=(23, 79, 121), width=5)
    draw.ellipse((-200, 940, 390, 1530), outline=(23, 79, 121), width=3)
    draw.rounded_rectangle((72, 72, 1010, 152), radius=22, fill=(18, 69, 106))
    draw.text((101, 95), "SCHMIDT  /  VERSICHERUNGSWISSEN", font=font(29, True), fill=WHITE)
    draw.rounded_rectangle((72, 255, 398, 333), radius=25, fill=(0, 125, 170))
    category = post["category"].upper()
    size = 29
    while draw.textbbox((0, 0), category, font=font(size, True))[2] > 290:
        size -= 1
    draw.text((94, 274), category, font=font(size, True), fill=WHITE)
    title_size = 78
    while title_size >= 45:
        title_font = font(title_size, True)
        lines = fit_lines(draw, post["title"], title_font, 920)
        if len(lines) <= 5 and len(lines) * (title_size + 21) < 470:
            break
        title_size -= 2
    y = 380
    for line in lines:
        draw.text((72, y), line, font=title_font, fill=WHITE)
        y += title_size + 21
    y += 25
    draw.line((77, y, 318, y), fill=CYAN, width=9)
    y += 42
    for line in fit_lines(draw, post["subtitle"], font(40), 900):
        draw.text((76, y), line, font=font(40), fill=PALE)
        y += 58
    draw.line((74, 1140, 1005, 1140), fill=(45, 105, 139), width=2)
    draw.text((76, 1176), "DÖBELN  /  MITTELSACHSEN", font=font(28, True), fill=PALE)
    draw.text((76, 1230), "@allianzschmidtdoebeln", font=font(32), fill=WHITE)
    out = ROOT / post["asset"]
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, "JPEG", quality=88, optimize=True)
    return out

def main():
    posts = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
    for p in posts:
        render(p)
    print(f"{len(posts)} originale Instagram-Grafiken erstellt.")

if __name__ == "__main__":
    main()
