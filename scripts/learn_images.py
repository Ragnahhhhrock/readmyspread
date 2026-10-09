"""Images for the Learn tarot section: in-article figures and per-article share images.

Used by scripts/build-learn.py (it calls ensure_* for anything published and missing). Can also be run
directly:  python3 scripts/learn_images.py   (rebuilds every figure listed in FIGURES).
Everything is drawn from the design tokens in public/css/tokens.css: night sky, gold linework,
7:12 gold-edged card outlines, Cormorant Garamond and Hanken Grotesk. Do not edit the PNGs by hand.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
FONTS = (PUB / "fonts").as_uri()
WHEEL = (PUB / "assets" / "zodiac-wheel.svg").as_uri()
STARS_A = (PUB / "assets" / "stars-a.svg").as_uri()
STARS_B = (PUB / "assets" / "stars-b.svg").as_uri()
OUT = ROOT / "content" / "learn-tarot" / "images"   # drafts live here; build-learn.py copies live ones to public/assets/learn

BASE = """<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: "Cormorant Garamond"; src: url("{fonts}/cormorant-garamond-latin-400-normal.woff2"); font-weight: 400; }}
@font-face {{ font-family: "Cormorant Garamond"; src: url("{fonts}/cormorant-garamond-latin-400-italic.woff2"); font-style: italic; font-weight: 400; }}
@font-face {{ font-family: "Cormorant Garamond"; src: url("{fonts}/cormorant-garamond-latin-600-normal.woff2"); font-weight: 600; }}
@font-face {{ font-family: "Hanken Grotesk"; src: url("{fonts}/hanken-grotesk-latin-wght-normal.woff2"); font-weight: 100 900; }}
:root {{ --night:#0b1024; --dusk:#141a38; --nebula:#232b55; --starlight:#f3efe4; --mist:#aeb4d3; --gold:#e2c071; --violet:#b4a8ff; --line:#6b74a8; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: {w}px; height: {h}px; overflow: hidden; position: relative; color: var(--starlight); font-family: "Hanken Grotesk", sans-serif;
  background: radial-gradient(900px 600px at 85% 0%, rgba(60,72,180,.5), transparent 65%), radial-gradient(700px 500px at 0% 100%, rgba(80,50,150,.38), transparent 60%), var(--night); }}
.stars {{ position: absolute; inset: 0; background: url("{sa}"), url("{sb}"); opacity: .8; }}
.abs {{ position: absolute; }}
.card {{ position: absolute; aspect-ratio: 7 / 12; background: var(--dusk); border: 3px solid var(--gold); border-radius: 12px; }}
.card::before {{ content: ""; position: absolute; inset: 9px; border: 1.5px solid rgba(226,192,113,.45); border-radius: 7px; }}
.card svg {{ position: absolute; left: 50%; top: 50%; width: 38%; transform: translate(-50%, -50%); }}
.card--rev svg {{ transform: translate(-50%, -50%) rotate(180deg); }}
.num {{ position: absolute; width: 64px; height: 64px; border: 3px solid var(--gold); border-radius: 50%; display: grid; place-items: center;
  font-family: "Cormorant Garamond"; font-weight: 600; font-size: 40px; color: var(--gold); background: var(--night); }}
.disp {{ font-family: "Cormorant Garamond"; }}
.yr, .num, .disp, .title {{ font-variant-numeric: lining-nums; font-feature-settings: "lnum" 1; }}
.gold {{ color: var(--gold); }} .mist {{ color: var(--mist); }}
.panel {{ position: absolute; background: var(--dusk); border: 2px solid var(--nebula); border-radius: 20px; }}
{css}
</style><div class="stars"></div>{body}"""

STAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 1l2.6 8.4L23 12l-8.4 2.6L12 23l-2.6-8.4L1 12l8.4-2.6Z" fill="none" stroke="#e2c071" stroke-width="1.4" stroke-linejoin="round"/></svg>'


def page(w, h, css, body):
    return BASE.format(fonts=FONTS, sa=STARS_A, sb=STARS_B, w=w, h=h, css=css, body=body)


def card(x, y, h, rev=False, extra=""):
    w = round(h * 7 / 12)
    return f'<div class="card{" card--rev" if rev else ""}" style="left:{x}px;top:{y}px;height:{h}px;width:{w}px;{extra}">{STAR}</div>'


# ---------------------------------------------------------------- figures (1600 x 900)
def fig_spread_positions():
    ch, cw = 480, 280
    xs = [330, 660, 990]
    labels = [("1", "Past"), ("2", "Present"), ("3", "Next")]
    body = '<div class="abs disp gold" style="left:0;width:1600px;top:36px;text-align:center;font-size:64px;font-weight:600">A three-card tarot spread</div>'
    for x, (n, lab) in zip(xs, labels):
        body += card(x, 220, ch)
        body += f'<div class="num" style="left:{x + cw / 2 - 32}px;top:140px">{n}</div>'
        body += f'<div class="abs" style="left:{x - 60}px;width:{cw + 120}px;top:728px;text-align:center;font-size:36px;font-weight:600">{lab}</div>'
    body += '<div class="abs mist" style="left:0;width:1600px;top:808px;text-align:center;font-size:30px">Each numbered position asks its own question of the card that lands there.</div>'
    return page(1600, 900, "", body)


def fig_single_vs_spread():
    css = ".t{position:absolute;text-align:center;font-weight:600;font-size:40px}.s{position:absolute;text-align:center;font-size:30px;color:var(--mist)}"
    body = '<div class="panel" style="left:80px;top:80px;width:640px;height:740px"></div><div class="panel" style="left:760px;top:80px;width:760px;height:740px"></div>'
    body += card(272, 150, 440)
    body += '<div class="t" style="left:80px;width:640px;top:628px">Single draw</div><div class="s" style="left:110px;width:580px;top:690px">One card, one message</div>'
    for i, lab in enumerate(["1", "2", "3"]):
        x = 760 + 60 + i * 230
        body += card(x, 220, 300)
        body += f'<div class="num" style="left:{x + 87 - 32}px;top:150px;width:56px;height:56px;font-size:34px">{lab}</div>'
    body += '<div class="t" style="left:760px;width:760px;top:560px">Tarot spread</div><div class="s" style="left:800px;width:680px;top:622px">Each position asks its own question, and the cards are read together</div>'
    return page(1600, 900, css, body)


def fig_timeline():
    css = (".ln{position:absolute;left:90px;right:90px;top:448px;height:3px;background:var(--gold)}"
           ".dot{position:absolute;top:437px;width:25px;height:25px;border-radius:50%;background:var(--night);border:3px solid var(--gold)}"
           ".yr{position:absolute;font-variant-numeric:lining-nums;font-family:'Cormorant Garamond';font-weight:600;font-size:62px;color:var(--gold);line-height:1}"
           ".tx{position:absolute;font-size:27px;line-height:1.35;color:var(--starlight);width:340px}"
           ".tk{position:absolute;width:2px;background:var(--line)}")
    items = [("1440s", "First tarot cards made in northern Italy for a card game, trionfi"),
             ("1500s", "The name tarocchi is in use and the game spreads across Italy and into France"),
             ("1700s", "The Marseille pattern becomes a common deck design in France"),
             ("1781", "Court de Gébelin links tarot to ancient Egypt, without evidence"),
             ("1783", "Etteilla publishes an early guide to telling fortunes with tarot"),
             ("1909", "The Rider-Waite-Smith deck is published in London"),
             ("Today", "Tarot is used for reflection, and many decks follow Rider-Waite-Smith")]
    n = len(items)
    x0, x1 = 230, 1370
    body = '<div class="ln"></div>'
    for i, (yr, tx) in enumerate(items):
        cx = x0 + (x1 - x0) * i / (n - 1)
        body += f'<div class="dot" style="left:{cx - 12:.0f}px"></div>'
        up = i % 2 == 0
        if up:
            body += f'<div class="tk" style="left:{cx:.0f}px;top:380px;height:56px"></div>'
            body += f'<div class="yr" style="left:{cx - 170:.0f}px;width:340px;text-align:center;top:150px">{yr}</div>'
            body += f'<div class="tx" style="left:{cx - 170:.0f}px;text-align:center;top:222px">{tx}</div>'
        else:
            body += f'<div class="tk" style="left:{cx:.0f}px;top:464px;height:56px"></div>'
            body += f'<div class="yr" style="left:{cx - 170:.0f}px;width:340px;text-align:center;top:538px">{yr}</div>'
            body += f'<div class="tx" style="left:{cx - 170:.0f}px;text-align:center;top:610px">{tx}</div>'
    body += '<div class="abs disp" style="left:0;width:1600px;text-align:center;top:52px;font-size:60px;font-weight:600">Tarot, from card game to modern reading</div>'
    return page(1600, 900, css, body)


def fig_pack():
    css = ".c{position:absolute;text-align:center}.big{font-family:'Cormorant Garamond';font-weight:600;font-size:56px;color:var(--gold);line-height:1}.lab{font-size:30px;font-weight:600}.sub{font-size:26px;color:var(--mist)}"
    body = '<div class="abs disp" style="left:0;width:1600px;text-align:center;top:46px;font-size:60px;font-weight:600">The standard 78-card tarot pack</div>'
    # suits (left)
    suits = ["Wands", "Cups", "Swords", "Pentacles"]
    for i, s in enumerate(suits):
        x = 70 + i * 215
        body += card(x, 190, 330)
        body += f'<div class="c lab" style="left:{x - 20}px;width:{192 + 40}px;top:540px">{s}</div><div class="c sub" style="left:{x - 20}px;width:{192 + 40}px;top:582px">14 cards</div>'
    body += '<div class="c big" style="left:70px;width:830px;top:660px">56 suit cards</div><div class="c sub" style="left:70px;width:830px;top:730px">Ace to ten, then page, knight, queen and king: the minor arcana</div>'
    # divider
    body += '<div class="abs" style="left:945px;top:190px;width:2px;height:600px;background:var(--line)"></div>'
    # trumps + fool (right)
    for k in range(3):
        body += card(1010 + k * 14, 190 + k * 8 - 0, 330, extra="" )
    body += '<div class="c lab" style="left:990px;width:300px;top:540px">Trumps</div><div class="c sub" style="left:990px;width:300px;top:582px">21 numbered cards</div>'
    body += card(1360, 190, 330)
    body += '<div class="c lab" style="left:1330px;width:260px;top:540px">The Fool</div><div class="c sub" style="left:1330px;width:260px;top:582px">Unnumbered</div>'
    body += '<div class="c big" style="left:975px;width:600px;top:660px">22 major arcana</div><div class="c sub" style="left:975px;width:600px;top:730px">56 + 22 = 78 cards</div>'
    return page(1600, 900, css, body)


def fig_game_to_reading():
    css = ".c{position:absolute;text-align:center}.h{font-family:'Cormorant Garamond';font-weight:600;font-size:44px;line-height:1.05}.y{font-size:28px;font-weight:600;color:var(--gold);letter-spacing:.06em;text-transform:uppercase}.d{font-size:28px;line-height:1.4;color:var(--mist)}"
    body = '<div class="abs disp" style="left:0;width:1600px;text-align:center;top:46px;font-size:60px;font-weight:600">How tarot\'s use changed</div>'
    panels = [("1440s to 1700s", "Card game", "Players use suit and trump cards to win tricks. Nobody reads the cards for meaning."),
              ("1780s to 1800s", "Occult interpretation", "Writers add theories about Egypt, the Kabbalah and hidden symbolism."),
              ("1900s to today", "Reading and reflection", "Illustrated decks turn every card into a picture to read and talk about.")]
    for i, (yrs, head, desc) in enumerate(panels):
        x = 70 + i * 500
        body += f'<div class="panel" style="left:{x}px;top:170px;width:460px;height:640px"></div>'
        body += card(x + 230 - 76, 205, 260)
        body += f'<div class="c y" style="left:{x}px;width:460px;top:490px">{yrs}</div><div class="c h" style="left:{x + 20}px;width:420px;top:536px">{head}</div><div class="c d" style="left:{x + 30}px;width:400px;top:660px">{desc}</div>'
        if i < 2:
            body += f'<svg class="abs" style="left:{x + 466}px;top:430px;width:36px;height:36px" viewBox="0 0 24 24"><path d="M3 12h16M13 6l6 6-6 6" fill="none" stroke="#e2c071" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return page(1600, 900, css, body)


FIGURES = {
    "what-is-a-tarot-spread-positions": fig_spread_positions,
    "what-is-a-tarot-spread-single-vs-spread": fig_single_vs_spread,
    "a-short-history-of-tarot-where-the-cards-came-from-timeline": fig_timeline,
    "a-short-history-of-tarot-where-the-cards-came-from-pack": fig_pack,
    "a-short-history-of-tarot-where-the-cards-came-from-game-to-reading": fig_game_to_reading,
}


# ---------------------------------------------------------------- share images
SHARE = """<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: "Cormorant Garamond"; src: url("{fonts}/cormorant-garamond-latin-400-italic.woff2"); font-style: italic; font-weight: 400; }}
@font-face {{ font-family: "Cormorant Garamond"; src: url("{fonts}/cormorant-garamond-latin-600-normal.woff2"); font-weight: 600; }}
@font-face {{ font-family: "Hanken Grotesk"; src: url("{fonts}/hanken-grotesk-latin-wght-normal.woff2"); font-weight: 100 900; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: {w}px; height: {h}px; overflow: hidden; position: relative; color: #f3efe4;
  background: radial-gradient(900px 600px at 82% 30%, rgba(60,72,180,.55), transparent 65%), radial-gradient(700px 500px at 0% 100%, rgba(80,50,150,.4), transparent 60%), #0b1024; }}
.stars {{ position: absolute; inset: 0; background: url("{sa}"), url("{sb}"); }}
.wheel {{ position: absolute; right: -150px; top: 50%; width: {wd}px; height: {wd}px; transform: translateY(-50%); opacity: .95; }}
.copy {{ position: absolute; left: 76px; top: 46%; transform: translateY(-50%); width: 660px; }}
.eyebrow {{ font-family: "Hanken Grotesk"; font-weight: 600; font-size: 22px; letter-spacing: .18em; text-transform: uppercase; color: #aeb4d3; margin-bottom: 22px; }}
.title {{ font-family: "Cormorant Garamond"; font-weight: 600; font-size: {fs}px; line-height: 1.04; letter-spacing: .005em; text-wrap: balance; }}
.tag {{ font-family: "Cormorant Garamond"; font-style: italic; font-size: 40px; color: #e2c071; margin-top: 24px; }}
.url {{ position: absolute; left: 76px; bottom: 46px; font-family: "Hanken Grotesk"; font-weight: 600; font-size: 25px; letter-spacing: .06em; color: #e2c071; }}
</style><div class="stars"></div><img class="wheel" src="{wheel}"><div class="copy"><div class="eyebrow">{eyebrow}</div><div class="title">{title}</div><div class="tag">Your tarot spread, read plainly.</div></div><div class="url">readmyspread.com/learn-tarot</div>"""


def share_html(title, eyebrow, w, h):
    n = len(title)
    fs = 86 if n <= 24 else 72 if n <= 40 else 62 if n <= 52 else 54
    return SHARE.format(fonts=FONTS, sa=STARS_A, sb=STARS_B, wheel=WHEEL, w=w, h=h, wd=int(h * 1.05), fs=fs,
                        title=title.replace("&", "&amp;"), eyebrow=eyebrow)


def _render(pw, html, w, h, path):
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "page.html"
        src.write_text(html, encoding="utf-8")
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(src.as_uri())
        pg.evaluate("document.fonts.ready.then(() => true)")
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(path))
        b.close()


def ensure_figures(slug):
    """Render any figure belonging to this article that is missing. Returns the file names."""
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    with sync_playwright() as pw:
        for key, fn in FIGURES.items():
            if key.startswith(slug + "-"):
                path = OUT / f"{key}.png"
                if not path.exists():
                    _render(pw, fn(), 1600, 900, path)
                    made.append(path.name)
    return made


def ensure_share(slug, title, eyebrow="Learn tarot"):
    OUT.mkdir(parents=True, exist_ok=True)
    og, tw = OUT / f"og-{slug}.png", OUT / f"twitter-{slug}.png"
    with sync_playwright() as pw:
        if not og.exists():
            _render(pw, share_html(title, eyebrow, 1200, 630), 1200, 630, og)
        if not tw.exists():
            _render(pw, share_html(title, eyebrow, 1200, 600), 1200, 600, tw)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        for key, fn in FIGURES.items():
            _render(pw, fn(), 1600, 900, OUT / f"{key}.png")
            print("built", key)
