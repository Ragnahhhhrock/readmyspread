"""Builds the YouTube channel images (profile picture, banner).

Run from the repo root:  python3 scripts/build-youtube.py
Needs: playwright (with Chromium). Reuses the tokens, fonts, sky and helpers from scripts/build-facebook.py
(DESIGN.md sections 8, 13 and 20). Do not edit the PNGs by hand.

YouTube shows the profile picture as a circle, so the mark sits inside the central 60%. The banner is 2560 x 1440 and
is shown cropped by device: phones and computers show the central 1546 x 423 band, tablets 1855 x 423, and TVs the
whole image. All copy sits inside the central 1546 x 423 band (x 507 to 2053, y 508 to 931).
"""
import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "assets" / "youtube"

spec = importlib.util.spec_from_file_location("fb", ROOT / "scripts" / "build-facebook.py")
fb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fb)
page, MARK, WHEEL = fb.page, fb.MARK, fb.WHEEL

# 1. Profile picture 800 x 800. Circular crop, so the mark sits in the central 60%.
profile = page(800, 800, f"""
.wheel {{ position: absolute; left: 50%; top: 50%; width: 1000px; height: 1000px; transform: translate(-50%, -50%); opacity: .35; }}
.mark {{ position: absolute; left: 50%; top: 50%; width: 440px; height: 440px; transform: translate(-50%, -50%); }}
""", f'<img class="wheel" src="{WHEEL}">' + MARK.replace("{n}", "p"),
    bg="radial-gradient(580px 580px at 50% 45%, rgba(60,72,180,.5), transparent 70%), " + fb.NIGHT)

# 2. Banner 2560 x 1440. Copy stays inside the central 1546 x 423 band.
banner = page(2560, 1440, """
.wheel { position: absolute; left: 50%; top: 50%; width: 1500px; height: 1500px; transform: translate(-50%, -50%); opacity: .22; }
.copy { position: absolute; left: 0; right: 0; top: 720px; transform: translateY(-50%); text-align: center; }
.eyebrow { font-size: 32px; margin-bottom: 18px; }
.name { font-size: 150px; }
.tag { font-size: 60px; margin-top: 16px; line-height: 1.1; }
.url { margin-top: 26px; font-size: 36px; }
""", f'<img class="wheel" src="{WHEEL}"><div class="copy"><div class="eyebrow">Tarot spread readings</div>'
     '<div class="name">readmyspread</div><div class="tag">Your tarot spread, read plainly.</div>'
     '<div class="url">readmyspread.com</div></div>')

JOBS = [("profile-800.png", 800, 800, profile), ("banner-2560x1440.png", 2560, 1440, banner)]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    tmpdir = ROOT / ".scratch"
    tmpdir.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h, html in JOBS:
            tmp = tmpdir / f"yt-{name}.html"
            tmp.write_text(html)
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(500)
            pg.screenshot(path=str(OUT / name))
            pg.close()
        b.close()
    print("youtube images built")
