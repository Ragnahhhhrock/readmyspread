"""Builds the favicon set and the social share images.

Run from the repo root:  python3 scripts/build-wheel.py && python3 scripts/build-assets.py
Needs: playwright (with Chromium) and Pillow. Fonts are loaded from public/fonts, so nothing
needs installing on the machine.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import io

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
FONTS = (PUB / "fonts").as_uri()
WHEEL = (PUB / "assets" / "zodiac-wheel.svg").as_uri()
STARS_A = (PUB / "assets" / "stars-a.svg").as_uri()
STARS_B = (PUB / "assets" / "stars-b.svg").as_uri()
FAVICON = (PUB / "favicon.svg").read_text()

CARD = """<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: "Cormorant Garamond"; src: url("{fonts}/cormorant-garamond-latin-400-italic.woff2"); font-style: italic; font-weight: 400; }}
@font-face {{ font-family: "Cormorant Garamond"; src: url("{fonts}/cormorant-garamond-latin-600-normal.woff2"); font-weight: 600; }}
@font-face {{ font-family: "Hanken Grotesk"; src: url("{fonts}/hanken-grotesk-latin-wght-normal.woff2"); font-weight: 100 900; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: {w}px; height: {h}px; overflow: hidden; position: relative; color: #f3efe4;
  background: radial-gradient(900px 600px at 82% 30%, rgba(60,72,180,.55), transparent 65%), radial-gradient(700px 500px at 0% 100%, rgba(80,50,150,.4), transparent 60%), #0b1024; }}
.stars {{ position: absolute; inset: 0; background: url("{sa}"), url("{sb}"); }}
.wheel {{ position: absolute; right: -150px; top: 50%; width: {wd}px; height: {wd}px; transform: translateY(-50%); opacity: .95; }}
.copy {{ position: absolute; left: 76px; top: 50%; transform: translateY(-50%); width: 640px; }}
.eyebrow {{ font-family: "Hanken Grotesk"; font-weight: 600; font-size: 22px; letter-spacing: .18em; text-transform: uppercase; color: #aeb4d3; margin-bottom: 22px; }}
.name {{ font-family: "Cormorant Garamond"; font-weight: 600; font-size: 108px; line-height: 1; letter-spacing: .005em; }}
.tag {{ font-family: "Cormorant Garamond"; font-style: italic; font-size: 52px; color: #e2c071; margin-top: 18px; }}
.sub {{ font-family: "Hanken Grotesk"; font-size: 27px; line-height: 1.4; color: #aeb4d3; margin-top: 26px; width: 520px; }}
.url {{ position: absolute; left: 76px; bottom: 46px; font-family: "Hanken Grotesk"; font-weight: 600; font-size: 25px; letter-spacing: .06em; color: #e2c071; }}
</style><div class="stars"></div><img class="wheel" src="{wheel}"><div class="copy"><div class="eyebrow">Tarot spread readings</div><div class="name">readmyspread</div><div class="tag">Your tarot spread, read plainly.</div><div class="sub">Photograph your tarot card spread and get a clear reading, card by card.</div></div><div class="url">readmyspread.com</div>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    # Open Graph 1.91:1 (1200x630) and Twitter summary_large_image 2:1 (1200x600)
    for name, w, h in [("og-image", 1200, 630), ("twitter-card", 1200, 600)]:
        page = b.new_page(viewport={"width": w, "height": h})
        html = CARD.format(fonts=FONTS, wheel=WHEEL, sa=STARS_A, sb=STARS_B, w=w, h=h, wd=h - 10)
        # file:// assets need a file page, so write a temp file (git-ignored) and open it
        tmp = ROOT / ".scratch" / f"{name}.html"
        tmp.parent.mkdir(exist_ok=True)
        tmp.write_text(html)
        page.goto(tmp.as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(500)
        page.screenshot(path=str(PUB / "assets" / f"{name}.png"))
        page.close()

    # Icons from favicon.svg
    sizes = {"favicon-32.png": 32, "assets/apple-touch-icon.png": 180, "assets/icon-192.png": 192, "assets/icon-512.png": 512}
    pngs = {}
    for rel, size in sizes.items():
        page = b.new_page(viewport={"width": size, "height": size})
        page.set_content(f'<body style="margin:0;background:transparent"><div style="width:{size}px;height:{size}px">{FAVICON.replace("<svg ", f"<svg width=\"{size}\" height=\"{size}\" ", 1)}</div>')
        data = page.screenshot(omit_background=True)
        (PUB / rel).write_bytes(data)
        pngs[size] = data
        page.close()
    b.close()

# favicon.ico (16, 32, 48) from a 512px render
big = Image.open(PUB / "assets" / "icon-512.png").convert("RGBA")
big.save(PUB / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
print("social images and icons built")
