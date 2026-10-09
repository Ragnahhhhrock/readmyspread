"""Builds public/assets/zodiac-wheel.svg and the two star-field tiles.

The twelve sign glyphs are outlined from DejaVu Sans (free licence) so the wheel looks
identical on every device and needs no font at runtime.

Run: python3 scripts/build-wheel.py   (needs fontTools)
"""
import math, random
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

OUT = Path(__file__).resolve().parent.parent / "public" / "assets"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = "#e2c071"
SKY = "#b4a8ff"

font = TTFont(FONT)
cmap = font.getBestCmap()
gs = font.getGlyphSet()
upm = font["head"].unitsPerEm

def glyph_path(codepoint, size, cx, cy):
    name = cmap[codepoint]
    bp = BoundsPen(gs)
    gs[name].draw(bp)
    x0, y0, x1, y1 = bp.bounds
    s = size / max(x1 - x0, y1 - y0)
    # flip y, scale, centre on (cx, cy)
    tx = cx - s * (x0 + x1) / 2
    ty = cy + s * (y0 + y1) / 2
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    gs[name].draw(TransformPen(pen, (s, 0, 0, -s, tx, ty)))
    return pen.getCommands()

C = 300
def pt(r, deg):
    a = math.radians(deg - 90)
    return C + r * math.cos(a), C + r * math.sin(a)

parts = []
add = parts.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" fill="none" stroke="{GOLD}" stroke-linecap="round" stroke-linejoin="round">')
add('<title>Zodiac wheel</title>')

# rings
for r, w, o in [(292, 1.6, 0.9), (278, 0.8, 0.5), (214, 1.2, 0.8), (150, 0.8, 0.45), (72, 0.8, 0.35)]:
    add(f'<circle cx="{C}" cy="{C}" r="{r}" stroke-width="{w}" opacity="{o}"/>')

# degree ticks between the two outer rings
for d in range(0, 360, 5):
    r0 = 278
    r1 = 286 if d % 30 else 292
    x0, y0 = pt(r0, d); x1, y1 = pt(r1, d)
    add(f'<path d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" stroke-width="{1 if d % 30 == 0 else 0.7}" opacity="{0.8 if d % 30 == 0 else 0.45}"/>')

# sign dividers
for i in range(12):
    x0, y0 = pt(214, i * 30); x1, y1 = pt(278, i * 30)
    add(f'<path d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" stroke-width="1" opacity="0.7"/>')

# glyphs (Aries to Pisces, clockwise from the top)
glyphs = []
for i in range(12):
    cx, cy = pt(246, i * 30 + 15)
    glyphs.append(f'<path d="{glyph_path(0x2648 + i, 30, cx, cy)}"/>')
add(f'<g fill="{GOLD}" stroke="none">' + "".join(glyphs) + '</g>')

# element triangles (fire, earth, air, water) inside the ring
for k, (start, o) in enumerate([(0, 0.55), (30, 0.4), (60, 0.55), (90, 0.4)]):
    pts = [pt(150, start + 120 * j) for j in range(3)]
    add('<path d="M' + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + f'Z" stroke-width="0.9" opacity="{o}"/>')

# 12 spokes from the inner ring to the centre
for i in range(12):
    x0, y0 = pt(72, i * 30 + 15); x1, y1 = pt(150, i * 30 + 15)
    add(f'<path d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" stroke-width="0.6" opacity="0.3"/>')

# a few "planets" on the inner ring, in violet for contrast
for deg, r in [(22, 150), (97, 150), (171, 150), (248, 150), (322, 150)]:
    x, y = pt(r, deg)
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#0b1024" stroke="{SKY}" stroke-width="1.4"/>')

# sun at the centre
add(f'<circle cx="{C}" cy="{C}" r="26" stroke-width="1.6"/>')
add(f'<circle cx="{C}" cy="{C}" r="5" fill="{GOLD}" stroke="none"/>')
for i in range(12):
    x0, y0 = pt(31, i * 30); x1, y1 = pt(40 if i % 3 == 0 else 36, i * 30)
    add(f'<path d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" stroke-width="1.2" opacity="0.8"/>')
add('</svg>')
(OUT / "zodiac-wheel.svg").write_text("\n".join(parts) + "\n")

# star-field tiles (seeded, so the output is stable)
def stars(name, size, n, seed, rmax):
    rnd = random.Random(seed)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">']
    for _ in range(n):
        x, y = rnd.uniform(4, size - 4), rnd.uniform(4, size - 4)
        r = rnd.uniform(0.4, rmax)
        o = rnd.uniform(0.35, 0.95)
        col = "#f3efe4" if rnd.random() > 0.2 else SKY
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{col}" opacity="{o:.2f}"/>')
    out.append('</svg>')
    (OUT / name).write_text("".join(out) + "\n")

stars("stars-a.svg", 480, 46, 11, 1.1)
stars("stars-b.svg", 760, 30, 29, 1.7)
print("wheel and star tiles written")
