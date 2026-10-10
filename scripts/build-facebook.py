"""Builds the Facebook page images (profile, cover, launch posts).

Run from the repo root:  python3 scripts/build-facebook.py
Needs: playwright (with Chromium). Fonts load from public/fonts. Same tokens and layout rules as
scripts/build-assets.py (DESIGN.md section 8 and 13). Do not edit the PNGs by hand.

Facebook crops the cover to 820x312 on computers (2.63:1) and 640x360 on phones (16:9). The cover is
built at 1640x924 (16:9) and all copy sits inside the central 1640x624 band, clear of the profile
picture overlap at bottom left, so it survives both crops.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
OUT = PUB / "assets" / "facebook"
FONTS = (PUB / "fonts").as_uri()
WHEEL = (PUB / "assets" / "zodiac-wheel.svg").as_uri()
STARS_A = (PUB / "assets" / "stars-a.svg").as_uri()
STARS_B = (PUB / "assets" / "stars-b.svg").as_uri()

# Tokens from public/css/tokens.css
NIGHT, DUSK, NEBULA = "#0b1024", "#141a38", "#232b55"
STARLIGHT, MIST, GOLD, LINE = "#f3efe4", "#aeb4d3", "#e2c071", "#6b74a8"

from mark import mark_svg  # the tarot card mark, shared with the favicon and share images
MARK = mark_svg("mark")

BASE = """<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: "Cormorant Garamond"; src: url("{fonts}/cormorant-garamond-latin-400-italic.woff2"); font-style: italic; font-weight: 400; }}
@font-face {{ font-family: "Cormorant Garamond"; src: url("{fonts}/cormorant-garamond-latin-600-normal.woff2"); font-weight: 600; }}
@font-face {{ font-family: "Hanken Grotesk"; src: url("{fonts}/hanken-grotesk-latin-wght-normal.woff2"); font-weight: 100 900; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: {w}px; height: {h}px; overflow: hidden; position: relative; color: {starlight};
  background: {bg}; }}
.stars {{ position: absolute; inset: 0; background: url("{sa}"), url("{sb}"); }}
.eyebrow {{ font-family: "Hanken Grotesk"; font-weight: 600; letter-spacing: .18em; text-transform: uppercase; color: {mist}; }}
.name {{ font-family: "Cormorant Garamond"; font-weight: 600; line-height: 1; letter-spacing: .005em; }}
.tag {{ font-family: "Cormorant Garamond"; font-style: italic; color: {gold}; }}
.ui {{ font-family: "Hanken Grotesk"; color: {mist}; }}
.url {{ font-family: "Hanken Grotesk"; font-weight: 600; letter-spacing: .06em; color: {gold}; }}
{css}
</style><div class="stars"></div>{body}"""

SKY = (
    "radial-gradient(900px 600px at 82% 30%, rgba(60,72,180,.55), transparent 65%), "
    "radial-gradient(700px 500px at 0% 100%, rgba(80,50,150,.4), transparent 60%), " + NIGHT
)


def page(w, h, css, body, bg=SKY):
    return BASE.format(fonts=FONTS, sa=STARS_A, sb=STARS_B, w=w, h=h, bg=bg, css=css, body=body,
                       starlight=STARLIGHT, mist=MIST, gold=GOLD)


# 1. Profile picture 720x720. Facebook shows it as a circle, so the mark sits inside the central 60%.
profile = page(720, 720, f"""
.wheel {{ position: absolute; left: 50%; top: 50%; width: 900px; height: 900px; transform: translate(-50%, -50%); opacity: .35; }}
.mark {{ position: absolute; left: 50%; top: 50%; width: 400px; height: 400px; transform: translate(-50%, -50%); }}
""", f'<img class="wheel" src="{WHEEL}">' + MARK.replace("{n}", "p"),
    bg="radial-gradient(520px 520px at 50% 45%, rgba(60,72,180,.5), transparent 70%), " + NIGHT)

# 2. Cover 1640x924. Copy lives in the central 624px band (y 150 to 774) and above the profile overlap.
cover = page(1640, 924, """
.wheel { position: absolute; right: -250px; top: 50%; width: 820px; height: 820px; transform: translateY(-50%); opacity: .95; }
.copy { position: absolute; left: 150px; top: 440px; transform: translateY(-50%); width: 900px; }
.eyebrow { font-size: 36px; margin-bottom: 30px; }
.name { font-size: 150px; }
.tag { font-size: 70px; margin-top: 24px; line-height: 1.1; }
.url { position: absolute; left: 150px; top: 640px; font-size: 40px; }
""", f'<img class="wheel" src="{WHEEL}"><div class="copy"><div class="eyebrow">Tarot spread readings</div>'
     '<div class="name">readmyspread</div><div class="tag">Your tarot spread, read plainly.</div></div>'
     '<div class="url">readmyspread.com</div>')

# 3. Feed posts, 4:5 (1080x1350) so they fill a phone screen.
def moon(d):
    return (f'<svg class="moon" viewBox="0 0 48 48" fill="none" aria-hidden="true"><circle cx="24" cy="24" r="20" stroke="{LINE}" stroke-width="1.5"/>{d}</svg>')

MOONS = [
    f'<path d="M24 4A20 20 0 0 1 24 44A11 20 0 0 0 24 4Z" fill="{GOLD}"/>',
    f'<path d="M24 4A20 20 0 0 1 24 44Z" fill="{GOLD}"/>',
    f'<circle cx="24" cy="24" r="20" fill="{GOLD}" stroke="{GOLD}" stroke-width="1.5"/>',
]

POST_CSS = """
.wheel { position: absolute; right: -430px; bottom: -430px; width: 1000px; height: 1000px; opacity: .55; }
.top { position: absolute; left: 90px; top: 110px; right: 90px; }
.eyebrow { font-size: 32px; margin-bottom: 28px; }
.h { font-family: "Cormorant Garamond"; font-weight: 600; font-size: 128px; line-height: 1.05; }
.sub { font-family: "Cormorant Garamond"; font-style: italic; color: #e2c071; font-size: 60px; margin-top: 28px; line-height: 1.15; }
.url { position: absolute; left: 90px; bottom: 90px; font-size: 38px; }
.steps { position: absolute; left: 90px; right: 90px; top: 500px; }
.row { display: flex; align-items: center; gap: 40px; padding: 32px 44px; margin-bottom: 28px; background: #141a38; border-radius: 20px; border: 2px solid #232b55; }
.moon { width: 110px; height: 110px; flex: none; }
.n { font-family: "Hanken Grotesk"; font-weight: 600; font-size: 28px; letter-spacing: .14em; text-transform: uppercase; color: #aeb4d3; }
.t { font-family: "Cormorant Garamond"; font-weight: 600; font-size: 84px; line-height: 1.05; margin-top: 4px; }
"""

post_how = page(1080, 1350, POST_CSS,
    f'<div class="top"><div class="eyebrow">Tarot spread readings</div>'
    '<div class="h">Three steps, no sign-up.</div></div><div class="steps">'
    + "".join(
        f'<div class="row">{moon(MOONS[i])}<div><div class="n">Step {w}</div><div class="t">{t}</div></div></div>'
        for i, (w, t) in enumerate([("one", "Photograph"), ("two", "Identify"), ("three", "Read")]))
    + '</div><div class="url">readmyspread.com</div>')

post_launch = page(1080, 1350, """
.wheel { position: absolute; right: -620px; top: 50%; width: 900px; height: 900px; transform: translateY(-50%); opacity: .9; }
.copy { position: absolute; left: 90px; top: 50%; transform: translateY(-50%); width: 660px; }
.mark { width: 150px; height: 150px; margin-bottom: 44px; }
.eyebrow { font-size: 32px; margin-bottom: 28px; }
.name { font-size: 112px; }
.tag { font-size: 62px; margin-top: 28px; line-height: 1.12; }
.ui { font-size: 38px; line-height: 1.4; margin-top: 44px; width: 600px; }
.url { position: absolute; left: 90px; bottom: 90px; font-size: 38px; }
""", f'<img class="wheel" src="{WHEEL}"><div class="copy">' + MARK.replace("{n}", "l") +
     '<div class="eyebrow">Tarot spread readings</div><div class="name">readmyspread</div>'
     '<div class="tag">Your tarot spread, read plainly.</div>'
     '<div class="ui">Photograph your tarot card spread and get a clear reading, card by card.</div></div>'
     '<div class="url">readmyspread.com</div>')

JOBS = [("profile-720.png", 720, 720, profile), ("cover-1640x924.png", 1640, 924, cover),
        ("post-launch-1080x1350.png", 1080, 1350, post_launch), ("post-how-it-works-1080x1350.png", 1080, 1350, post_how)]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    tmpdir = ROOT / ".scratch"
    tmpdir.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h, html in JOBS:
            tmp = tmpdir / f"fb-{name}.html"
            tmp.write_text(html)
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(500)
            pg.screenshot(path=str(OUT / name))
            pg.close()
        b.close()
    print("facebook images built")
