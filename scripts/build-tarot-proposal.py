"""Builds the tarot identity proposal artwork into docs/tarot-identity/assets/.

Everything is original gold linework on the site's night, dusk and nebula colours (hex values
match public/css/tokens.css). Text is outlined from the self-hosted Cormorant Garamond so the
files look the same everywhere. No published tarot deck is copied: the suit symbols, card faces
and layouts are drawn from scratch.

Proposal only. Nothing here is referenced by public/ until a direction is chosen.

Run: python3 scripts/build-tarot-proposal.py   (needs fontTools and brotli)
"""
import math
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "tarot-identity" / "assets"
(OUT / "icons").mkdir(parents=True, exist_ok=True)

NIGHT, DUSK, NEBULA = "#0b1024", "#141a38", "#232b55"
STAR, MIST, GOLD, VIOLET, LINE = "#f3efe4", "#aeb4d3", "#e2c071", "#b4a8ff", "#6b74a8"

def load_font(path):
    ft = TTFont(str(path))
    return ft, ft.getGlyphSet(), ft.getBestCmap(), ft["head"].unitsPerEm


CORMORANT = load_font(ROOT / "public" / "fonts" / "cormorant-garamond-latin-600-normal.woff2")
# Plain lining digits for spread positions (Cormorant's "1" reads as a capital I). Free licence, as in build-wheel.py.
DIGITS = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def text_path(text, size, cx, y, tracking=0.0, max_w=None, font=None):
    """Outlined text centred on cx with its baseline at y. Shrinks to max_w if given."""
    FONT, GS, CMAP, UPM = font or CORMORANT
    names = [CMAP[ord(c)] for c in text]

    def measure(sz):
        s = sz / UPM
        return [FONT["hmtx"][n][0] * s + tracking * sz / size for n in names]

    adv = measure(size)
    total = sum(adv) - tracking
    if max_w and total > max_w:
        size = size * max_w / total
        adv = measure(size)
        total = sum(adv) - tracking * size / size
    s = size / UPM
    x = cx - (sum(adv) - (tracking * size / size)) / 2
    out = []
    for n, a in zip(names, adv):
        pen = SVGPathPen(GS, ntos=f)
        GS[n].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        out.append(pen.getCommands())
        x += a
    return " ".join(p for p in out if p)


def svg(w, h, body, title, defs="", bg=None):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t"><title id="t">{title}</title>'
        f"<defs>{defs}</defs>{bgrect}{body}</svg>\n"
    )


def star4(cx, cy, r, fill=GOLD, k=0.28):
    pts = []
    for i in range(8):
        a = math.radians(i * 45 - 90)
        rr = r if i % 2 == 0 else r * k
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return f'<path d="M{" L".join(f"{f(x)} {f(y)}" for x, y in pts)}Z" fill="{fill}"/>'


def star4_outline(cx, cy, r, k=0.3, sw=1.5):
    pts = []
    for i in range(8):
        a = math.radians(i * 45 - 90)
        rr = r if i % 2 == 0 else r * k
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return (f'<path d="M{" L".join(f"{f(x)} {f(y)}" for x, y in pts)}Z" fill="none" '
            f'stroke="{GOLD}" stroke-width="{sw}" stroke-linejoin="round"/>')


def star8_outline(cx, cy, r_long, r_short, r_in, sw=1.5):
    pts = []
    for i in range(16):
        a = math.radians(i * 22.5 - 90)
        rr = r_long if i % 4 == 0 else (r_short if i % 2 == 0 else r_in)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return (f'<path d="M{" L".join(f"{f(x)} {f(y)}" for x, y in pts)}Z" fill="none" '
            f'stroke="{GOLD}" stroke-width="{sw}" stroke-linejoin="round"/>')


def pentagram(cx, cy, r):
    order = [0, 2, 4, 1, 3]
    pts = []
    for i in order:
        a = math.radians(i * 72 - 90)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return f'M{" L".join(f"{f(x)} {f(y)}" for x, y in pts)}Z'


# ---------------------------------------------------------------------------------------------
# Icons: 48 x 48, 1.5 stroke, gold, round caps. Same style as the hero card faces.
# ---------------------------------------------------------------------------------------------
G = f'fill="none" stroke="{GOLD}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'

ICONS = {
    "wands": (
        "Wands suit icon: a budding staff",
        '<path d="M24 6c-4.5 4-4.5 9 0 13 4.5-4 4.5-9 0-13Z"/><path d="M24 19v24"/>'
        '<path d="M24 27c-6 0-9.5-3.5-10.5-8 6 0 9.5 3 10.5 8Z"/><path d="M24 34c6 0 9.5-3.5 10.5-8-6 0-9.5 3-10.5 8Z"/>',
    ),
    "cups": (
        "Cups suit icon: a chalice",
        '<path d="M10 14h28c0 9.5-6 15.5-14 15.5S10 23.5 10 14Z"/><path d="M24 29.5V38"/>'
        '<path d="M16 42h16"/><circle cx="24" cy="34" r="2"/><path d="M10 14c4 2.4 24 2.4 28 0"/>',
    ),
    "swords": (
        "Swords suit icon: an upright blade",
        '<path d="M24 4l4 5.5V29h-8V9.5Z"/><path d="M13 29h22"/><path d="M24 29v9"/><circle cx="24" cy="41" r="2.4"/>',
    ),
    "pentacles": (
        "Pentacles suit icon: a five-point star in a circle",
        f'<circle cx="24" cy="24" r="18"/><path d="{pentagram(24, 24.8, 12.5)}"/>',
    ),
    "tarot-card": (
        "A single tarot card with a four-point star",
        '<rect x="13" y="5" width="22" height="38" rx="3"/><rect x="16.5" y="8.5" width="15" height="31" rx="1.5" stroke-opacity=".55"/>'
        '<path d="M24 16l1.8 6.2L32 24l-6.2 1.8L24 32l-1.8-6.2L16 24l6.2-1.8Z"/>',
    ),
    "card-fan": (
        "Three tarot cards fanned",
        '<g transform="rotate(-24 24 44)"><rect x="17" y="10" width="14" height="28" rx="2.4"/></g>'
        '<g transform="rotate(24 24 44)"><rect x="17" y="10" width="14" height="28" rx="2.4"/></g>'
        '<rect x="17" y="8" width="14" height="30" rx="2.4" fill="#0b1024"/><path d="M24 17l1.3 4.4L29.7 23l-4.4 1.6L24 29l-1.3-4.4L18.3 23l4.4-1.6Z"/>',
    ),
    "deck": (
        "A stacked tarot deck",
        '<rect x="12" y="9" width="22" height="33" rx="3" stroke-opacity=".55"/><rect x="15" y="6" width="22" height="33" rx="3" stroke-opacity=".8"/>'
        '<rect x="18" y="3.5" width="22" height="33" rx="3" fill="#0b1024"/><path d="M29 14l1.6 5.4L36 21l-5.4 1.6L29 28l-1.6-5.4L22 21l5.4-1.6Z"/>',
    ),
    "third-eye": (
        "An eye with three short rays: the eye on the card back",
        '<path d="M4 28q20-20 40 0q-20 20-40 0Z"/><circle cx="24" cy="28" r="6"/><circle cx="24" cy="28" r="1.8" fill="#e2c071" stroke="none"/>'
        '<path d="M24 6v6M11 11l3.2 4.4M37 11l-3.2 4.4"/>',
    ),
    "spread-three": (
        "A three-card spread",
        '<rect x="4" y="13" width="11" height="22" rx="2"/><rect x="18.5" y="13" width="11" height="22" rx="2"/><rect x="33" y="13" width="11" height="22" rx="2"/>'
        '<path d="M9.5 24h0M24 24h0M38.5 24h0" stroke-width="3"/>',
    ),
    "spread-celtic": (
        "A Celtic Cross spread",
        '<rect x="14" y="18" width="8" height="12" rx="1.6"/><path d="M12 24h12" stroke-opacity=".7"/>'
        '<rect x="14" y="3" width="8" height="11" rx="1.6"/><rect x="14" y="34" width="8" height="11" rx="1.6"/>'
        '<rect x="2" y="19" width="8" height="10" rx="1.6"/><rect x="26" y="19" width="8" height="10" rx="1.6"/>'
        '<rect x="39" y="3" width="7" height="8.5" rx="1.4"/><rect x="39" y="14" width="7" height="8.5" rx="1.4"/>'
        '<rect x="39" y="25" width="7" height="8.5" rx="1.4"/><rect x="39" y="36" width="7" height="8.5" rx="1.4"/>',
    ),
    "photograph": (
        "A camera with a star: photograph your spread",
        '<path d="M6 15h8l3-5h14l3 5h8v24H6Z"/><circle cx="24" cy="27" r="8"/><path d="M24 22.5l1 3 3 1-3 1-1 3-1-3-3-1 3-1Z" fill="#e2c071" stroke="none"/>',
    ),
    "listen": (
        "A speaker: listen to the reading",
        '<path d="M7 19h7l9-8v26l-9-8H7Z"/><path d="M29 18q4.5 6 0 12M34 13q8 11 0 22"/>',
    ),
    "reader": (
        "A tarot reader: head and shoulders with a star",
        '<circle cx="24" cy="19" r="8"/><path d="M8 43c1-9 8-14 16-14s15 5 16 14Z"/><path d="M24 3l1.3 3.7L29 8l-3.7 1.3L24 13l-1.3-3.7L19 8l3.7-1.3Z" fill="#e2c071" stroke="none"/>',
    ),
    "candle": (
        "A candle",
        '<rect x="17" y="20" width="14" height="22" rx="2"/><path d="M24 20v-3"/><path d="M24 4c-4 4-5 7-5 9.5a5 5 0 0 0 10 0C29 11 28 8 24 4Z"/><path d="M12 42h24"/>',
    ),
    "crescent-star": (
        "The readmyspread mark: a crescent and a four-point star",
        '<path d="M22 7A17 17 0 1 0 38 32A14 14 0 0 1 22 7Z"/><path d="M38 6l1.5 4.3L44 12l-4.5 1.7L38 18l-1.5-4.3L32 12l4.5-1.7Z" fill="#e2c071" stroke="none"/>',
    ),
}


def write_icons():
    for name, (title, inner) in ICONS.items():
        body = f'<g {G}>{inner}</g>'
        (OUT / "icons" / f"{name}.svg").write_text(svg(48, 48, body, title))


# ---------------------------------------------------------------------------------------------
# Cards: 140 x 240 (7:12). Dusk face, 1.5px gold edge, inset hairline, 8px radius.
# ---------------------------------------------------------------------------------------------
def frame(ornate=False):
    out = (f'<rect x="1" y="1" width="138" height="238" rx="8" fill="{DUSK}" stroke="{GOLD}" stroke-width="1.5"/>'
           f'<rect x="7" y="7" width="126" height="226" rx="4" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".55"/>')
    if ornate:
        out += (f'<rect x="12" y="12" width="116" height="216" rx="2" fill="none" stroke="{GOLD}" stroke-width="0.8" opacity=".35"/>'
                + star4(18, 18, 4) + star4(122, 18, 4) + star4(18, 222, 4) + star4(122, 222, 4))
    return out


def roman_and_name(numeral, name):
    out = ""
    if numeral:
        out += f'<path d="{text_path(numeral, 17, 70, 38, tracking=1.5)}" fill="{GOLD}"/>'
    out += f'<path d="M34 46h72" stroke="{GOLD}" stroke-width="1" opacity=".5"/>'
    out += f'<path d="M34 196h72" stroke="{GOLD}" stroke-width="1" opacity=".5"/>'
    out += f'<path d="{text_path(name, 12.5, 70, 216, tracking=1.4, max_w=100)}" fill="{GOLD}"/>'
    return out


def arcana(numeral, name, art, title):
    return svg(140, 240, frame(True) + roman_and_name(numeral, name) + art, title)


def art_star():
    small = "".join(star4(x, y, 5) for x, y in [(30, 78), (110, 78), (24, 118), (116, 118), (36, 154), (104, 154)])
    wave = "".join(
        f'<path d="M30 {y}q10-7 20 0t20 0t20 0t20 0" fill="none" stroke="{GOLD}" stroke-width="1.5" stroke-linecap="round"/>'
        for y in (172, 182)
    )
    return star8_outline(70, 112, 38, 26, 9, 1.6) + f'<circle cx="70" cy="112" r="2.6" fill="{GOLD}"/>' + small + wave


def art_moon():
    ring = f'<circle cx="70" cy="112" r="46" fill="none" stroke="{GOLD}" stroke-width="1.5" stroke-dasharray="0.1 5.2" stroke-linecap="round"/>'
    cres = (f'<path d="M64 84A30 30 0 1 0 96 128A24 24 0 0 1 64 84Z" fill="none" stroke="{GOLD}" stroke-width="1.6" stroke-linejoin="round"/>')
    sm = star4(98, 92, 6) + star4(44, 134, 4)
    hill = f'<path d="M24 182Q70 150 116 182" fill="none" stroke="{GOLD}" stroke-width="1.5" stroke-linecap="round"/>'
    return ring + cres + sm + hill


def art_sun():
    rays = []
    for i in range(16):
        a = math.radians(i * 22.5)
        r0, r1 = 26, (44 if i % 2 == 0 else 36)
        rays.append(f"M{f(70 + r0 * math.cos(a))} {f(110 + r0 * math.sin(a))}L{f(70 + r1 * math.cos(a))} {f(110 + r1 * math.sin(a))}")
    return (f'<circle cx="70" cy="110" r="19" fill="none" stroke="{GOLD}" stroke-width="1.6"/>'
            f'<path d="{" ".join(rays)}" stroke="{GOLD}" stroke-width="1.5" stroke-linecap="round" fill="none"/>'
            f'<path d="M22 176h96" stroke="{GOLD}" stroke-width="1.5" stroke-linecap="round"/>'
            f'<path d="M36 176a8 8 0 0 1 16 0M62 176a8 8 0 0 1 16 0M88 176a8 8 0 0 1 16 0" fill="none" stroke="{GOLD}" stroke-width="1.5"/>')


def art_ace(icon):
    inner = ICONS[icon][1]
    return (f'<g transform="translate(17.6 64) scale(2.2)" fill="none" stroke="{GOLD}" stroke-width="0.85" '
            f'stroke-linecap="round" stroke-linejoin="round">{inner}</g>')


def card_back(w=140, h=240):
    lattice = []
    for k in range(-12, 13):
        lattice.append(f"M{14 + k * 22} 14l-120 240M{14 + k * 22 + 120} 14l120 240")
    # diamond lattice, clipped to the inner panel
    lat = (f'<clipPath id="inner"><rect x="14" y="14" width="112" height="212" rx="2"/></clipPath>'
           f'<g clip-path="url(#inner)" stroke="{GOLD}" stroke-width="0.8" opacity=".28" fill="none">'
           f'<path d="{" ".join(lattice)}"/></g>')
    medallion = (f'<circle cx="70" cy="120" r="40" fill="{DUSK}" stroke="{GOLD}" stroke-width="1.5"/>'
                 f'<circle cx="70" cy="120" r="47" fill="none" stroke="{GOLD}" stroke-width="1.5" stroke-dasharray="0.1 5" stroke-linecap="round"/>'
                 + star4_outline(70, 120, 33, 0.3, 1.5)
                 + f'<path d="M52 120q18-15 36 0q-18 15-36 0Z" fill="{DUSK}" stroke="{GOLD}" stroke-width="1.5"/>'
                 f'<circle cx="70" cy="120" r="5" fill="none" stroke="{GOLD}" stroke-width="1.5"/>'
                 f'<circle cx="70" cy="120" r="1.8" fill="{GOLD}"/>')
    return frame(True) + lat + medallion


def write_cards():
    (OUT / "card-back.svg").write_text(svg(140, 240, card_back(), "A tarot card back: a gold eye inside a four-point star on a diamond lattice"))
    (OUT / "card-star.svg").write_text(arcana("XVII", "THE STAR", art_star(), "Original card face: The Star, XVII"))
    (OUT / "card-moon.svg").write_text(arcana("XVIII", "THE MOON", art_moon(), "Original card face: The Moon, XVIII"))
    (OUT / "card-sun.svg").write_text(arcana("XIX", "THE SUN", art_sun(), "Original card face: The Sun, XIX"))
    for icon, nm in (("wands", "ACE OF WANDS"), ("cups", "ACE OF CUPS"), ("swords", "ACE OF SWORDS"), ("pentacles", "ACE OF PENTACLES")):
        (OUT / f"card-ace-{icon}.svg").write_text(arcana("I", nm, art_ace(icon), f"Original card face: {nm.title()}"))


# ---------------------------------------------------------------------------------------------
# Fan of cards for the hero, and the Celtic Cross layout
# ---------------------------------------------------------------------------------------------
def write_fan():
    def sym(i, body):
        return f'<symbol id="{i}" viewBox="0 0 140 240">{body}</symbol>'

    defs = (
        sym("back", card_back().replace('id="inner"', 'id="inner-b"').replace("url(#inner)", "url(#inner-b)"))
        + sym("face", frame(True) + roman_and_name("XVII", "THE STAR") + art_star())
    )
    parts = []
    for a in (-36, -18, 18, 36):
        parts.append(f'<g transform="rotate({a} 180 336)"><use href="#back" xlink:href="#back" x="124" y="136" width="112" height="192"/></g>')
    parts.append('<use href="#face" xlink:href="#face" x="124" y="136" width="112" height="192"/>')
    fan = svg(360, 372, "".join(parts), "Five tarot cards fanned, the centre card face up showing The Star", defs)
    # crop the empty sky above the cards
    (OUT / "hero-card-fan.svg").write_text(fan.replace('viewBox="0 0 360 372"', 'viewBox="0 118 360 256"'))


def write_celtic():
    cw, ch = 36, 64
    cx0, cy0 = 112, 152
    cards = [
        (1, cx0, cy0, 0), (2, cx0, cy0, 90), (3, cx0, cy0 + 84, 0), (4, cx0 - 84, cy0, 0),
        (5, cx0, cy0 - 84, 0), (6, cx0 + 84, cy0, 0),
        (7, 262, cy0 + 105, 0), (8, 262, cy0 + 35, 0), (9, 262, cy0 - 35, 0), (10, 262, cy0 - 105, 0),
    ]
    body = ""
    for n, x, y, rot in cards:
        fill = "none" if n == 2 else DUSK
        body += (f'<g transform="rotate({rot} {x} {y})"><rect x="{x - cw / 2}" y="{y - ch / 2}" width="{cw}" height="{ch}" rx="4" '
                 f'fill="{fill}" stroke="{GOLD}" stroke-width="1.5"/>')
        body += f'<rect x="{x - cw / 2 + 3}" y="{y - ch / 2 + 3}" width="{cw - 6}" height="{ch - 6}" rx="2" fill="none" stroke="{GOLD}" stroke-width="0.8" opacity=".5"/></g>'
        if n == 1:
            nx, ny, sz = x, y - 20, 11
        elif n == 2:
            nx, ny, sz = x + 25, y + 4, 11
        else:
            nx, ny, sz = x, y + 5, 14
        body += f'<path d="{text_path(str(n), sz, nx, ny, font=DIGITS)}" fill="{GOLD}"/>'
    (OUT / "spread-celtic-cross.svg").write_text(svg(300, 300, body, "A Celtic Cross spread: ten numbered card positions"))


# ---------------------------------------------------------------------------------------------
# The reader: the existing figure, with cards. Same face and hair as public/assets/reader.svg.
# ---------------------------------------------------------------------------------------------
def figure(top_id):
    return f"""
    <path d="M120 52c-30 0-48 22-48 52 0 30 6 56 14 84h68c8-28 14-54 14-84 0-30-18-52-48-52z" fill="{NIGHT}" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>
    <path d="M26 240c2-34 22-52 56-58l22-8h32l22 8c34 6 54 24 56 58z" fill="{NEBULA}" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>
    <path d="M104 148v28l16 16 16-16v-28z" fill="{DUSK}" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>
    <path d="M120 62c-22 0-34 18-34 40 0 26 14 46 34 46s34-20 34-46c0-22-12-40-34-40z" fill="{DUSK}" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>
    <path d="M84 102c0-24 14-42 36-42s36 18 36 42c-12-6-24-20-36-38-12 18-24 32-36 38z" fill="{NIGHT}" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>
    <g fill="none" stroke="{GOLD}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M101 106q6 5 12 0M127 106q6 5 12 0"/><path d="M120 110v10q-3 3-6 1" stroke-width="1.5"/><path d="M112 132q8 6 16 0"/>
    </g>"""


def write_reader_cards():
    sky = (f'<rect width="240" height="240" fill="{DUSK}"/><circle cx="120" cy="104" r="96" fill="{NEBULA}" opacity=".6"/>'
           f'<circle cx="120" cy="104" r="86" fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 7" stroke-linecap="round"/>'
           f'<g fill="{STAR}"><circle cx="34" cy="62" r="1.6"/><circle cx="58" cy="30" r="1.2"/><circle cx="206" cy="58" r="1.6"/><circle cx="188" cy="26" r="1.2"/></g>')
    crown = star4(120, 40, 7)  # a single star above the brow
    fan = ""
    for a in (-22, 22, 0):
        fill = NIGHT if a == 0 else DUSK
        fan += (f'<g transform="rotate({a} 120 236)"><rect x="97" y="150" width="46" height="80" rx="5" fill="{fill}" stroke="{GOLD}" stroke-width="2"/>'
                f'<rect x="102" y="155" width="36" height="70" rx="3" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".55"/>'
                + (star4(120, 190, 12) if a == 0 else f'<circle cx="120" cy="190" r="9" fill="none" stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="0.1 3.4" stroke-linecap="round"/>')
                + "</g>")
    hands = (f'<path d="M84 238c-4-14 0-24 10-26l16 6v20z" fill="{NEBULA}" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>'
             f'<path d="M156 238c4-14 0-24-10-26l-16 6v20z" fill="{NEBULA}" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>')
    body = (f'<g clip-path="url(#c)">{sky}{figure("a")}{crown}{fan}{hands}</g>'
            f'<circle cx="120" cy="120" r="119" fill="none" stroke="{GOLD}" stroke-width="2"/>')
    defs = '<clipPath id="c"><circle cx="120" cy="120" r="119"/></clipPath>'
    (OUT / "reader-with-cards.svg").write_text(svg(240, 240, body, "The reader holding three tarot cards: gold linework on a night sky", defs))


def write_reader_table():
    w, h = 390, 280
    sky = (f'<rect width="{w}" height="{h}" fill="{DUSK}"/><circle cx="195" cy="110" r="150" fill="{NEBULA}" opacity=".55"/>'
           f'<circle cx="195" cy="110" r="128" fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 8" stroke-linecap="round"/>'
           f'<g fill="{STAR}"><circle cx="36" cy="40" r="1.6"/><circle cx="74" cy="84" r="1.2"/><circle cx="350" cy="50" r="1.6"/><circle cx="316" cy="96" r="1.2"/><circle cx="24" cy="130" r="1.2"/></g>'
           + star4(54, 66, 6) + star4(338, 78, 6))
    fig = f'<g transform="translate(75 -6) scale(0.98)">{figure("t")}</g>'
    cloth = (f'<path d="M0 214H{w}V{h}H0Z" fill="{NEBULA}"/><path d="M0 214H{w}" stroke="{GOLD}" stroke-width="2"/>'
             f'<path d="M0 222H{w}" stroke="{GOLD}" stroke-width="1" opacity=".5"/>')
    spread = ""
    glyphs = [
        f'<path d="M118 238A13 13 0 1 0 130 262A11 11 0 0 1 118 238Z" fill="none" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>',
        star4(195, 251, 12),
        f'<circle cx="270" cy="251" r="6" fill="none" stroke="{GOLD}" stroke-width="2"/>'
        + "".join(f'<path d="M{f(270 + 10 * math.cos(math.radians(a)))} {f(251 + 10 * math.sin(math.radians(a)))}L{f(270 + 15 * math.cos(math.radians(a)))} {f(251 + 15 * math.sin(math.radians(a)))}" stroke="{GOLD}" stroke-width="2" stroke-linecap="round"/>' for a in range(0, 360, 45)),
    ]
    for i, x in enumerate((120, 195, 270)):
        spread += (f'<rect x="{x - 24}" y="226" width="48" height="50" rx="5" fill="{DUSK}" stroke="{GOLD}" stroke-width="2"/>'
                   + glyphs[i])
    deck = (f'<rect x="318" y="226" width="40" height="50" rx="5" fill="{NIGHT}" stroke="{GOLD}" stroke-width="2"/>'
            f'<rect x="322" y="222" width="40" height="50" rx="5" fill="{DUSK}" stroke="{GOLD}" stroke-width="2"/>'
            f'<circle cx="342" cy="247" r="9" fill="none" stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="0.1 3.2" stroke-linecap="round"/>')
    candle = (f'<rect x="28" y="236" width="20" height="40" rx="3" fill="{DUSK}" stroke="{GOLD}" stroke-width="2"/>'
              f'<path d="M38 236v-6" stroke="{GOLD}" stroke-width="2" stroke-linecap="round"/>'
              f'<path d="M38 208c-6 6-8 11-8 15a8 8 0 0 0 16 0c0-4-2-9-8-15Z" fill="{GOLD}"/>')
    body = sky + fig + cloth + spread + deck + candle
    (OUT / "reader-table.svg").write_text(svg(w, h, body, "The reader at a table with a three-card spread, a deck and a candle"))


if __name__ == "__main__":
    write_icons()
    write_cards()
    write_fan()
    write_celtic()
    write_reader_cards()
    write_reader_table()
    print("wrote", sum(1 for _ in OUT.rglob("*.svg")), "svg files to", OUT)
