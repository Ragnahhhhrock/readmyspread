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


# ---- articles 3 to 7
def _title(text):
    return f'<div class="abs disp" style="left:0;width:1600px;text-align:center;top:46px;font-size:60px;font-weight:600">{text}</div>'


def fig_read_steps():
    css = ".c{position:absolute;text-align:center}.h{font-family:'Cormorant Garamond';font-weight:600;font-size:46px;line-height:1.05}.d{font-size:28px;line-height:1.4;color:var(--mist)}"
    body = _title("Reading a tarot spread in four steps")
    steps = [("Start with the question", "Decide what you want to think about before any card is turned."),
             ("Check the positions", "Each position has a job, such as past, present or advice."),
             ("Read card by card", "Say what each card shows, then what it means in its position."),
             ("Read the whole spread", "Look for repeats, patterns and how the cards answer each other.")]
    for i, (h, d) in enumerate(steps):
        x = 55 + i * 375
        body += f'<div class="panel" style="left:{x}px;top:210px;width:340px;height:520px"></div>'
        body += f'<div class="num" style="left:{x + 138}px;top:250px">{i + 1}</div>'
        body += f'<div class="c h" style="left:{x + 20}px;width:300px;top:350px">{h}</div>'
        body += f'<div class="c d" style="left:{x + 24}px;width:292px;top:490px">{d}</div>'
        if i < 3:
            body += f'<svg class="abs" style="left:{x + 342}px;top:455px;width:30px;height:30px" viewBox="0 0 24 24"><path d="M3 12h16M13 6l6 6-6 6" fill="none" stroke="#e2c071" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return page(1600, 900, css, body)


def fig_same_card_positions():
    css = ".c{position:absolute;text-align:center}.h{font-family:'Cormorant Garamond';font-weight:600;font-size:44px}.d{font-size:28px;line-height:1.4;color:var(--mist)}"
    body = _title("One card, three positions")
    items = [("Past", "What led here?"), ("Present", "What is happening now?"), ("Advice", "What could help?")]
    for i, (h, d) in enumerate(items):
        x = 70 + i * 500
        body += f'<div class="panel" style="left:{x}px;top:170px;width:460px;height:640px"></div>'
        body += card(x + 230 - 112, 205, 384)
        body += f'<div class="c h gold" style="left:{x}px;width:460px;top:612px">{h}</div>'
        body += f'<div class="c d" style="left:{x + 30}px;width:400px;top:680px">{d}</div>'
    body += '<div class="abs mist" style="left:0;width:1600px;text-align:center;top:832px;font-size:28px">The same card is read against a different question in each place.</div>'
    return page(1600, 900, css, body)


def fig_upright_reversed():
    css = ".c{position:absolute;text-align:center}.h{font-family:'Cormorant Garamond';font-weight:600;font-size:54px}.d{font-size:30px;line-height:1.4;color:var(--mist)}"
    body = _title("Upright and reversed")
    for i, (h, d, rev) in enumerate([("Upright", "The card faces you the right way up.", False), ("Reversed", "The card turns up upside down.", True)]):
        x = 80 + i * 760
        body += f'<div class="panel" style="left:{x}px;top:170px;width:680px;height:640px"></div>'
        body += card(x + 340 - 130, 210, 440, rev=rev)
        body += f'<div class="c h gold" style="left:{x}px;width:680px;top:672px">{h}</div>'
        body += f'<div class="c d" style="left:{x + 40}px;width:600px;top:742px">{d}</div>'
    return page(1600, 900, css, body)


def fig_arcana():
    css = ".c{position:absolute;text-align:center}.big{font-family:'Cormorant Garamond';font-weight:600;font-size:60px;color:var(--gold);line-height:1}.lab{font-size:30px;font-weight:600}.sub{font-size:27px;line-height:1.4;color:var(--mist)}"
    body = _title("The 78 tarot cards")
    body += '<div class="panel" style="left:70px;top:160px;width:520px;height:660px"></div><div class="panel" style="left:630px;top:160px;width:900px;height:660px"></div>'
    for k in range(3):
        body += card(196 + k * 22, 200 + k * 8, 300)
    body += '<div class="c big" style="left:70px;width:520px;top:540px">22</div><div class="c lab" style="left:70px;width:520px;top:612px">Major arcana</div>'
    body += '<div class="c sub" style="left:100px;width:460px;top:660px">The Fool to The World. Big themes and turning points.</div>'
    for i, nm in enumerate(["Wands", "Cups", "Swords", "Pentacles"]):
        x = 678 + i * 210
        body += card(x, 200, 300)
        body += f'<div class="c lab" style="left:{x - 14}px;width:{175 + 28}px;top:512px">{nm}</div>'
    body += '<div class="c big" style="left:630px;width:900px;top:560px">56</div><div class="c lab" style="left:630px;width:900px;top:632px">Minor arcana</div>'
    body += '<div class="c sub" style="left:700px;width:760px;top:680px">Four suits of 14 cards. Everyday events, moods and choices.</div>'
    return page(1600, 900, css, body)


def fig_one_card_layout():
    css = ".c{position:absolute}.q{font-family:'Cormorant Garamond';font-style:italic;font-size:44px;line-height:1.25;color:var(--gold)}.d{font-size:30px;line-height:1.4;color:var(--mist)}"
    body = _title("A one-card tarot spread")
    body += card(240, 230, 560)
    body += '<div class="num" style="left:371px;top:150px">1</div>'
    body += '<div class="c q" style="left:760px;top:250px;width:760px">What should I keep in mind today?</div>'
    body += '<div class="c d" style="left:760px;top:400px;width:740px">One question, one position, one card. Read the card, then ask what it says about the question.</div>'
    body += '<div class="c d" style="left:760px;top:560px;width:740px">Good for a daily check-in or a quick thought.</div>'
    return page(1600, 900, css, body)


FIGURES.update({
    "how-to-read-a-tarot-spread-step-by-step-steps": fig_read_steps,
    "tarot-card-positions-and-what-they-change-same-card": fig_same_card_positions,
    "reversed-tarot-cards-and-how-to-read-them-upright-reversed": fig_upright_reversed,
    "major-and-minor-arcana-in-tarot-explained-arcana": fig_arcana,
    "the-one-card-tarot-spread-layout": fig_one_card_layout,
})


# ---- articles 8 to 41: spread layouts, card faces and reference figures
import math
ICONS = (PUB / "assets" / "tarot" / "icons")


def pcard(cx, cy, h, num=None, label="", fs=28, rot=0, lw=None, top_label=False):
    """A numbered position card centred on cx, cy with its label beneath."""
    w = round(h * 7 / 12)
    inner = f'<span class="disp gold" style="position:absolute;left:0;right:0;top:50%;transform:translateY(-50%){' rotate(' + str(-rot) + 'deg)' if rot else ''};text-align:center;font-size:{max(26, round(h * .3))}px;font-weight:600;line-height:1">{num}</span>' if num is not None else STAR
    css_rot = f"transform:rotate({rot}deg);" if rot else ""
    out = f'<div class="card" style="left:{cx - w / 2:.0f}px;top:{cy - h / 2:.0f}px;height:{h}px;width:{w}px;{css_rot}">{inner}</div>'
    if label:
        lw = lw or max(w + 120, 220)
        out += f'<div class="abs" style="left:{cx - lw / 2:.0f}px;width:{lw}px;top:{cy + h / 2 + 10:.0f}px;text-align:center;font-size:{fs}px;font-weight:600;line-height:1.15">{label}</div>'
    return out


def spread_fig(title, items, h, fs=28, note="", lw=None):
    body = _title(title)
    for it in items:
        n, label, cx, cy = it[:4]
        rot = it[4] if len(it) > 4 else 0
        body += pcard(cx, cy, h, n, label, fs, rot, lw)
    if note:
        body += f'<div class="abs mist" style="left:0;width:1600px;text-align:center;bottom:28px;font-size:28px">{note}</div>'
    return page(1600, 900, "", body)


def fig_three_layout():
    return spread_fig("A three-card tarot spread: past, present, next",
                      [(1, "Past", 400, 430), (2, "Present", 800, 430), (3, "Next", 1200, 430)], 440, 40)


def fig_three_two_ways():
    items = [(1, "Past", 400, 270), (2, "Present", 800, 270), (3, "Next", 1200, 270),
             (1, "Situation", 400, 680), (2, "Action", 800, 680), (3, "Outcome", 1200, 680)]
    return spread_fig("Two ways to read three cards", items, 220, 30)


CELTIC = ["Heart of the matter", "Crossing", "Foundation", "Recent past", "Crown", "Near future", "You", "Surroundings", "Hopes and fears", "Outcome"]


def _celtic(title):
    body = _title(title)
    h = 190
    pos = [(1, 460, 470, 0), (3, 460, 690, 0), (4, 300, 470, 0), (5, 460, 250, 0), (6, 620, 470, 0)]
    for n, x, y, r in pos:
        body += pcard(x, y, h, None if n == 1 else n)
    body += '<div class="abs disp gold" style="left:420px;width:80px;text-align:center;top:384px;font-size:56px;font-weight:600;line-height:1">1</div>'
    body += pcard(460, 470, 110, 2, rot=90)  # laid across the first card
    for k, y in zip([7, 8, 9, 10], [740, 570, 400, 230]):
        body += pcard(860, y, 150, k)
    body += '<div class="panel" style="left:1020px;top:150px;width:520px;height:700px"></div>'
    for i, nm in enumerate(CELTIC):
        y = 180 + i * 66
        body += f'<div class="abs gold disp" style="left:1050px;top:{y}px;width:60px;font-size:38px;font-weight:600;text-align:right">{i + 1}</div><div class="abs" style="left:1130px;top:{y + 8}px;font-size:30px;font-weight:600">{nm}</div>'
    return page(1600, 900, "", body)


def fig_celtic_layout():
    return _celtic("The Celtic Cross tarot spread")


def fig_celtic_numbered():
    return _celtic("Celtic Cross positions, numbered one to ten")


def fig_horseshoe():
    names = ["Past", "Present", "Hidden influences", "You", "Others and surroundings", "Advice", "Likely outcome"]
    pts = [(190, 250), (330, 440), (530, 580), (800, 640), (1070, 580), (1270, 440), (1410, 250)]
    return spread_fig("A horseshoe tarot spread", [(i + 1, names[i], pts[i][0], pts[i][1]) for i in range(7)], 190, 27, lw=250)


def fig_relationship():
    items = [(1, "You", 400, 455), (2, "The other person", 1200, 455), (3, "The connection", 800, 455),
             (4, "What brings you together", 800, 235), (5, "What is challenging", 800, 675),
             (6, "What could help", 400, 675), (7, "Where it may head", 1200, 675)]
    return spread_fig("A relationship tarot spread", items, 160, 26, lw=300)


def fig_two_path():
    items = [(1, "The situation", 800, 235), (2, "Path A offers", 430, 470), (3, "Path A asks", 430, 710),
             (4, "Path B offers", 1170, 470), (5, "Path B asks", 1170, 710), (6, "Advice", 800, 710)]
    return spread_fig("A two-path decision tarot spread", items, 170, 28, lw=280)


def fig_yes_no():
    return spread_fig("A yes or no tarot spread",
                      [(1, "The case for yes", 400, 430), (2, "The case against", 800, 430), (3, "What tips the balance", 1200, 430)], 400, 36, lw=380)


def fig_year():
    body = _title("A year-ahead tarot spread")
    body += pcard(800, 235, 170, 1, "Theme", 28)
    mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i, m in enumerate(mon):
        cx = 200 + (i % 6) * 240
        cy = 480 if i < 6 else 720
        body += pcard(cx, cy, 150, None, m, 28)
    return page(1600, 900, "", body)


def fig_twelve():
    names = ["Self", "Money and values", "Communication", "Home and roots", "Creativity and play", "Daily routines", "Partnerships",
             "Shared resources and change", "Learning and travel", "Work and public life", "Friends and community", "Rest and the unseen"]
    body = _title("A twelve-house tarot spread")
    for i, nm in enumerate(names):
        phi = math.pi - i * math.pi / 6
        body += pcard(800 + 640 * math.cos(phi), 500 + 262 * math.sin(phi), 100, i + 1)
        col, row = divmod(i, 6)
        x = 395 + col * 420
        y = 330 + row * 56
        body += f'<div class="abs gold disp" style="left:{x}px;top:{y - 4}px;width:50px;text-align:right;font-size:34px;font-weight:600">{i + 1}</div><div class="abs" style="left:{x + 66}px;top:{y + 2}px;font-size:26px;font-weight:600">{nm}</div>'
    return page(1600, 900, "", body)


def fig_tree():
    names = ["Crown", "Wisdom", "Understanding", "Mercy", "Severity", "Beauty", "Victory", "Glory", "Foundation", "Kingdom"]
    pts = [(800, 185), (1060, 290), (540, 290), (1060, 455), (540, 455), (800, 372), (1060, 630), (540, 630), (800, 625), (800, 790)]
    body = _title("A Tree of Life tarot spread")
    for i, (x, y) in enumerate(pts):
        body += pcard(x, y, 100, i + 1, names[i], 26, lw=230)
    return page(1600, 900, "", body)


def fig_moon():
    names = ["New moon", "Waxing crescent", "First quarter", "Waxing gibbous", "Full moon", "Waning gibbous", "Last quarter", "Waning crescent"]
    body = _title("A moon phase tarot spread")
    for i, nm in enumerate(names):
        phi = -math.pi / 2 + i * math.pi / 4
        body += pcard(800 + 560 * math.cos(phi), 470 + 255 * math.sin(phi), 130, i + 1, nm, 26, lw=230)
    return page(1600, 900, "", body)


def fig_pyramid():
    items = [(1, "What is happening", 450, 690), (2, "What is in the way", 800, 690), (3, "What helps", 1150, 690),
             (4, "What you can do", 625, 455), (5, "What to let go", 975, 455), (6, "Likely direction", 800, 220)]
    return spread_fig("A pyramid tarot spread", items, 160, 28, lw=320)


def fig_mbs():
    items = [(3, "Spirit", 800, 250), (1, "Mind", 520, 620), (2, "Body", 1080, 620)]
    return spread_fig("A mind, body and spirit tarot spread", items, 230, 34)


def faces_fig(title, cards):
    """cards: list of (top text, name, suit or None). Original linework faces, name beneath."""
    n = len(cards)
    w = min(250, int((1500 - (n - 1) * 30) / n))
    h = round(w * 12 / 7)
    gap = 30
    x0 = (1600 - (n * w + (n - 1) * gap)) / 2
    y0 = 170 + max(0, (560 - h) / 2)
    body = _title(title)
    for i, (top, name, suit) in enumerate(cards):
        x = x0 + i * (w + gap)
        glyph = (f'<img src="{(ICONS / (suit + ".svg")).as_uri()}" style="position:absolute;left:50%;top:50%;width:56%;transform:translate(-50%,-50%)">'
                 if suit else STAR)
        tfs = 44 if len(top) <= 3 else 30
        body += (f'<div class="card" style="left:{x:.0f}px;top:{y0:.0f}px;width:{w}px;height:{h}px">'
                 f'<div class="disp gold" style="position:absolute;left:0;right:0;top:20px;text-align:center;font-size:{tfs}px;font-weight:600;line-height:1.1">{top}</div>{glyph}'
                 f'<div class="gold" style="position:absolute;left:0;right:0;bottom:24px;text-align:center"><svg viewBox="0 0 24 24" style="position:static;transform:none;width:26px;transform:none;height:26px"><path d="M12 1l2.6 8.4L23 12l-8.4 2.6L12 23l-2.6-8.4L1 12l8.4-2.6Z" fill="none" stroke="#e2c071" stroke-width="1.4"/></svg></div></div>')
        body += f'<div class="abs" style="left:{x - 20:.0f}px;width:{w + 40}px;top:{y0 + h + 18:.0f}px;text-align:center;font-size:{28 if n <= 5 else 25}px;font-weight:600;line-height:1.15">{name}</div>'
    return page(1600, 900, "", body)


def _roman(n):
    return ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"][n]


def _majors(title, names_nums):
    return lambda: faces_fig(title, [(_roman(n), nm, None) for n, nm in names_nums])


def _suit_cards(suit, ranks):
    sn = suit.capitalize()
    out = []
    for r in ranks:
        top = {"Page": "Page", "Knight": "Knight", "Queen": "Queen", "King": "King"}.get(r, r)
        nm = f"{r} of {sn}"
        out.append((top, nm, suit))
    return out


def _suit(title, suit, ranks):
    return lambda: faces_fig(title, _suit_cards(suit, ranks))


def fig_suits():
    css = ".c{position:absolute;text-align:center}.h{font-family:'Cormorant Garamond';font-weight:600;font-size:52px}.el{font-size:28px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--gold)}.d{font-size:28px;line-height:1.4;color:var(--mist)}"
    body = _title("The four tarot suits")
    data = [("wands", "Wands", "Fire", "Energy and action"), ("cups", "Cups", "Water", "Feelings and relationships"),
            ("swords", "Swords", "Air", "Thought and communication"), ("pentacles", "Pentacles", "Earth", "Work and the practical world")]
    for i, (ic, nm, el, th) in enumerate(data):
        x = 55 + i * 375
        body += f'<div class="panel" style="left:{x}px;top:170px;width:340px;height:620px"></div>'
        body += f'<img class="abs" src="{(ICONS / (ic + ".svg")).as_uri()}" style="left:{x + 90}px;top:215px;width:160px;height:160px">'
        body += f'<div class="c h" style="left:{x}px;width:340px;top:410px">{nm}</div><div class="c el" style="left:{x}px;width:340px;top:490px">{el}</div><div class="c d" style="left:{x + 30}px;width:280px;top:550px">{th}</div>'
    return page(1600, 900, css, body)


def fig_numbers():
    css = ".c{position:absolute;text-align:center}.big{font-family:'Cormorant Garamond';font-weight:600;font-size:60px;color:var(--gold);line-height:1;font-variant-numeric:lining-nums;font-feature-settings:'lnum' 1}.nm{font-size:26px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--mist)}.d{font-size:28px;line-height:1.3}"
    body = _title("Numbers across the four tarot suits")
    data = [("Ace", "Beginnings"), ("Two", "Balance and choice"), ("Three", "Growth and teamwork"), ("Four", "Stability and pause"), ("Five", "Conflict and change"),
            ("Six", "Harmony and movement"), ("Seven", "Reflection and challenge"), ("Eight", "Skill and momentum"), ("Nine", "Resilience and near completion"), ("Ten", "Completion and overload")]
    for i, (nm, kw) in enumerate(data):
        x = 50 + (i % 5) * 302
        y = 170 + (i // 5) * 340
        lab = "A" if i == 0 else str(i + 1) if i < 9 else "10"
        lab = {"A": "1"}.get(lab, lab)
        body += f'<div class="panel" style="left:{x}px;top:{y}px;width:276px;height:310px"></div>'
        body += f'<div class="c big" style="left:{x}px;width:276px;top:{y + 36}px">{lab}</div><div class="c nm" style="left:{x}px;width:276px;top:{y + 118}px">{nm}</div><div class="c d" style="left:{x + 20}px;width:236px;top:{y + 170}px">{kw}</div>'
    return page(1600, 900, css, body)


def fig_do_dont():
    css = ".h{position:absolute;font-family:'Cormorant Garamond';font-weight:600;font-size:56px}.li{position:absolute;font-size:32px;line-height:1.3;width:560px}"
    body = _title("Photographing your tarot spread")
    cols = [("Do", True, ["Even, soft light", "Shoot from directly above", "Keep the whole spread in frame", "Leave cards clear of each other", "Use a plain background"]),
            ("Don't", False, ["Harsh shadows or glare", "A tilted angle", "Cards cut off or overlapping", "A cluttered background"])]
    for i, (hd, ok, items) in enumerate(cols):
        x = 80 + i * 760
        body += f'<div class="panel" style="left:{x}px;top:170px;width:680px;height:640px"></div><div class="h gold" style="left:{x + 50}px;top:200px">{hd}</div>'
        for j, t in enumerate(items):
            y = 310 + j * 94
            mark = ('<path d="M4 12.5l5 5 11-11" fill="none" stroke="#e2c071" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>' if ok
                    else '<path d="M6 6l12 12M18 6L6 18" fill="none" stroke="#aeb4d3" stroke-width="2.6" stroke-linecap="round"/>')
            body += f'<svg class="abs" style="left:{x + 50}px;top:{y + 4}px;width:40px;height:40px" viewBox="0 0 24 24">{mark}</svg><div class="li" style="left:{x + 112}px;top:{y}px">{t}</div>'
    return page(1600, 900, css, body)


def fig_terms():
    css = ".h{position:absolute;font-family:'Cormorant Garamond';font-weight:600;font-size:50px;color:var(--gold)}.d{position:absolute;font-size:29px;line-height:1.35;color:var(--starlight);width:420px}"
    body = _title("Tarot terms at a glance")
    terms = [("Spread", "A layout of cards where each place has a meaning."), ("Position", "The meaning of one place in a spread."),
             ("Arcana", "The two groups of cards: 22 major and 56 minor."), ("Court card", "A Page, Knight, Queen or King."),
             ("Upright", "A card facing you the right way up."), ("Reversed", "A card turned upside down.")]
    for i, (t, d) in enumerate(terms):
        x = 55 + (i % 3) * 512
        y = 170 + (i // 3) * 340
        body += f'<div class="panel" style="left:{x}px;top:{y}px;width:480px;height:310px"></div><div class="h" style="left:{x + 30}px;top:{y + 34}px">{t}</div><div class="d" style="left:{x + 30}px;top:{y + 130}px">{d}</div>'
    return page(1600, 900, css, body)


_M = _majors
FIGURES.update({
    "the-three-card-tarot-spread-layout": fig_three_layout,
    "the-three-card-tarot-spread-two-ways": fig_three_two_ways,
    "the-celtic-cross-tarot-spread-explained-layout": fig_celtic_layout,
    "celtic-cross-tarot-spread-positions-one-by-one-numbered": fig_celtic_numbered,
    "the-fool-to-the-hierophant-tarot-card-meanings-faces": _M("The Fool to The Hierophant", [(0, "The Fool"), (1, "The Magician"), (2, "The High Priestess"), (3, "The Empress"), (4, "The Emperor"), (5, "The Hierophant")]),
    "the-horseshoe-tarot-spread-layout": fig_horseshoe,
    "the-relationship-tarot-spread-layout": fig_relationship,
    "the-lovers-to-the-hermit-tarot-card-meanings-faces": _M("The Lovers to The Hermit", [(6, "The Lovers"), (7, "The Chariot"), (8, "Strength"), (9, "The Hermit")]),
    "the-two-path-decision-tarot-spread-layout": fig_two_path,
    "the-yes-or-no-tarot-spread-layout": fig_yes_no,
    "the-wheel-of-fortune-to-temperance-tarot-card-meanings-faces": _M("Wheel of Fortune to Temperance", [(10, "Wheel of Fortune"), (11, "Justice"), (12, "The Hanged Man"), (13, "Death"), (14, "Temperance")]),
    "the-year-ahead-tarot-spread-layout": fig_year,
    "the-astrological-twelve-house-tarot-spread-layout": fig_twelve,
    "the-devil-to-the-moon-tarot-card-meanings-faces": _M("The Devil to The Moon", [(15, "The Devil"), (16, "The Tower"), (17, "The Star"), (18, "The Moon")]),
    "the-tree-of-life-tarot-spread-layout": fig_tree,
    "the-moon-phase-tarot-spread-layout": fig_moon,
    "the-sun-to-the-world-tarot-card-meanings-faces": _M("The Sun to The World", [(19, "The Sun"), (20, "Judgement"), (21, "The World")]),
    "the-pyramid-tarot-spread-layout": fig_pyramid,
    "the-mind-body-and-spirit-tarot-spread-layout": fig_mbs,
    "the-four-tarot-suits-and-their-elements-suits": fig_suits,
    "numbers-in-tarot-and-what-they-signal-numbers": fig_numbers,
    "how-to-photograph-your-tarot-spread-for-a-reading-do-dont": fig_do_dont,
    "tarot-terms-glossary-spreads-cards-and-jargon-terms": fig_terms,
})
_LOW = ["Ace", "2", "3", "4", "5"]
_HIGH = ["6", "7", "8", "9", "10"]
_COURT = ["Page", "Knight", "Queen", "King"]
for _suit_name in ["wands", "cups", "swords", "pentacles"]:
    _cap = _suit_name.capitalize()
    FIGURES[f"{_suit_name}-in-tarot-ace-to-five-meanings-faces"] = _suit(f"Ace to Five of {_cap}", _suit_name, _LOW)
    FIGURES[f"{_suit_name}-in-tarot-six-to-ten-meanings-faces"] = _suit(f"Six to Ten of {_cap}", _suit_name, _HIGH)
    FIGURES[f"{_suit_name}-in-tarot-court-card-meanings-faces"] = _suit(f"Court cards of {_cap}", _suit_name, _COURT)


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
