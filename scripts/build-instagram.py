"""Builds the Instagram profile images (profile picture, highlight covers, first three posts).

Run from the repo root:  python3 scripts/build-instagram.py
Needs: playwright (with Chromium). Reuses the tokens, fonts, sky and helpers from scripts/build-facebook.py
(DESIGN.md sections 8, 13 and 15). Do not edit the PNGs by hand.

Instagram shows the profile picture as a circle, highlight covers as a circle cropped from the centre of a
9:16 image, and the profile grid as 3:4 crops of the middle of each post. So: the mark sits inside the central
55% of the profile picture, highlight icons sit inside the central 600px, and post copy keeps a 90px margin.
"""
import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "assets" / "instagram"

spec = importlib.util.spec_from_file_location("fb", ROOT / "scripts" / "build-facebook.py")
fb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fb)

page, MARK, moon, MOONS, POST_CSS = fb.page, fb.MARK, fb.moon, fb.MOONS, fb.POST_CSS
GOLD, DUSK, NEBULA, LINE = fb.GOLD, fb.DUSK, fb.NEBULA, fb.LINE
WHEEL = fb.WHEEL

STAR = "M46 9l1.8 5.2L53 16l-5.2 1.8L46 23l-1.8-5.2L39 16l5.2-1.8Z"


def card(w=210, rot=0, extra=""):
    """Tarot card outline, 7:12, gold edge, dusk face, four-point star. 8px radius at 140 wide."""
    h = round(w * 12 / 7)
    return (f'<svg class="card" style="width:{w}px;height:{h}px;transform:rotate({rot}deg);{extra}" viewBox="0 0 140 240" aria-hidden="true">'
            f'<rect x="3" y="3" width="134" height="234" rx="8" fill="{DUSK}" stroke="{GOLD}" stroke-width="4"/>'
            f'<path d="{STAR}" transform="translate(-114 56) scale(4)" fill="{GOLD}"/></svg>')


GLOW = "radial-gradient(620px 620px at 50% 50%, rgba(60,72,180,.5), transparent 70%), " + fb.NIGHT

# 1. Profile picture 1080x1080. Circular crop, so the mark sits in the central 55%.
profile = page(1080, 1080, f"""
.wheel {{ position: absolute; left: 50%; top: 50%; width: 1350px; height: 1350px; transform: translate(-50%, -50%); opacity: .35; }}
.mark {{ position: absolute; left: 50%; top: 50%; width: 600px; height: 600px; transform: translate(-50%, -50%); }}
""", f'<img class="wheel" src="{WHEEL}">' + MARK.replace("{n}", "p"),
    bg="radial-gradient(780px 780px at 50% 45%, rgba(60,72,180,.5), transparent 70%), " + fb.NIGHT)

# 2. Highlight covers 1080x1920. No text (Instagram prints the highlight name). Icon inside the central 600px.
HL_CSS = """
.ring { position: absolute; left: 50%; top: 50%; width: 760px; height: 760px; transform: translate(-50%, -50%);
  border-radius: 50%; border: 3px solid #232b55; }
.row { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); display: flex; align-items: center; justify-content: center; }
.moon { width: 150px; height: 150px; margin: 0 22px; }
.mark { position: absolute; left: 50%; top: 50%; width: 400px; height: 400px; transform: translate(-50%, -50%); }
.dots { position: absolute; left: 50%; top: 50%; width: 560px; height: 560px; transform: translate(-50%, -50%); }
.card { position: absolute; left: 50%; top: 50%; margin-left: -105px; margin-top: -180px; }
"""


def highlight(body):
    return page(1080, 1920, HL_CSS, '<div class="ring"></div>' + body, bg=GLOW)


DOTS = (f'<svg class="dots" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="48" fill="none" stroke="{GOLD}" '
        'stroke-width="0.5" stroke-dasharray="0.1 2.2" stroke-linecap="round"/></svg>')

hl_read = highlight(card(240, 0, "margin-left:-120px;margin-top:-206px;"))
hl_steps = highlight('<div class="row">' + "".join(moon(m) for m in MOONS) + '</div>')
hl_learn = highlight(card(200, -14, "margin-left:-235px;margin-top:-171px;") + card(200, 0, "margin-left:-100px;margin-top:-171px;z-index:2;")
                     + card(200, 14, "margin-left:35px;margin-top:-171px;"))
hl_privacy = highlight(DOTS + MARK.replace("{n}", "h"))

# 3. Feed posts 1080x1350 (4:5). Same layout rules as the Facebook posts.
post_launch = fb.post_launch
post_how = fb.post_how

TIP_CSS = POST_CSS + """
.ic { width: 76px; height: 133px; flex: none; }
.t { font-size: 76px; }
"""


def tip_icon():
    return card(76, 0, "flex:none;").replace('class="card"', 'class="ic"')


tips = [("one", "Good light"), ("two", "Cards laid flat"), ("three", "Whole spread in frame")]
post_tips = page(1080, 1350, TIP_CSS,
    '<div class="top"><div class="eyebrow">Tarot spread readings</div><div class="h">Three tips for a clear photo.</div></div>'
    '<div class="steps">' + "".join(
        f'<div class="row">{tip_icon()}<div><div class="n">Tip {w}</div><div class="t">{t}</div></div></div>' for w, t in tips)
    + '</div><div class="url">readmyspread.com</div>')

JOBS = [
    ("profile-1080.png", 1080, 1080, profile),
    ("highlight-read.png", 1080, 1920, hl_read),
    ("highlight-how-it-works.png", 1080, 1920, hl_steps),
    ("highlight-learn-tarot.png", 1080, 1920, hl_learn),
    ("highlight-privacy.png", 1080, 1920, hl_privacy),
    ("post-launch-1080x1350.png", 1080, 1350, post_launch),
    ("post-how-it-works-1080x1350.png", 1080, 1350, post_how),
    ("post-photo-tips-1080x1350.png", 1080, 1350, post_tips),
]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    tmpdir = ROOT / ".scratch"
    tmpdir.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h, html in JOBS:
            tmp = tmpdir / f"ig-{name}.html"
            tmp.write_text(html)
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(500)
            pg.screenshot(path=str(OUT / name))
            pg.close()
        b.close()
    print("instagram images built")
