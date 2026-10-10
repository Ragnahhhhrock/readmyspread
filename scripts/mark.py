"""The readmyspread mark: a gold tarot card (7:12) with a crescent and a four-point star cut out of it.

One source of truth for every place the mark is drawn: the header wordmark and closing mark
(via build-learn.py and the hand-written pages), favicon.svg, the app icons, the share images
and the social profile images.

The card and both cut-outs are one path with fill-rule evenodd, so the holes are real holes
and the mark works on any background.
"""
import math

GOLD = "#e2c071"
NIGHT = "#0b1024"


def _f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _round_rect(x, y, w, h, r):
    return (f"M{_f(x + r)} {_f(y)}H{_f(x + w - r)}A{r} {r} 0 0 1 {_f(x + w)} {_f(y + r)}"
            f"V{_f(y + h - r)}A{r} {r} 0 0 1 {_f(x + w - r)} {_f(y + h)}H{_f(x + r)}"
            f"A{r} {r} 0 0 1 {_f(x)} {_f(y + h - r)}V{_f(y + r)}A{r} {r} 0 0 1 {_f(x + r)} {_f(y)}Z")


def _crescent(c1, r1, c2, r2):
    (x1, y1), (x2, y2) = c1, c2
    d = math.hypot(x2 - x1, y2 - y1)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(r1 * r1 - a * a)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    px, py = x1 + a * ux, y1 + a * uy
    p1 = (px - h * uy, py + h * ux)
    p2 = (px + h * uy, py - h * ux)
    return (f"M{_f(p1[0])} {_f(p1[1])}A{r1} {r1} 0 1 1 {_f(p2[0])} {_f(p2[1])}"
            f"A{r2} {r2} 0 1 0 {_f(p1[0])} {_f(p1[1])}Z")


def _star(cx, cy, r, k=0.3):
    pts = []
    for i in range(8):
        a = math.radians(i * 45 - 90)
        rr = r if i % 2 == 0 else r * k
        pts.append(f"{_f(cx + rr * math.cos(a))} {_f(cy + rr * math.sin(a))}")
    return "M" + "L".join(pts) + "Z"


def mark_path(x=16.25, y=5, w=31.5, h=54):
    """Card at (x, y) of size w x h inside a 64 x 64 box, with the cut-outs scaled to it."""
    cx = x + w / 2
    s = h / 54  # the design is drawn for h = 54
    cres = _crescent((cx - 0.5 * s, y + 21 * s), 11.2 * s, (cx + 3.6 * s, y + 18.2 * s), 9.4 * s)
    star = _star(cx, y + 40.5 * s, 8.4 * s)
    return _round_rect(x, y, w, h, 4.5 * s) + cres + star


def mark_svg(cls=None, extra="aria-hidden=\"true\""):
    """Inline mark: viewBox trimmed to the card so the wordmark gap is even."""
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="14 0 36 64" {extra}>'
            f'<path fill="{GOLD}" fill-rule="evenodd" d="{mark_path()}"/></svg>')


def favicon_svg():
    """Night tile with the card centred; same card as the wordmark."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">\n'
            f'  <rect width="64" height="64" rx="14" fill="{NIGHT}"/>\n'
            f'  <path fill="{GOLD}" fill-rule="evenodd" d="{mark_path()}"/>\n'
            '</svg>\n')


if __name__ == "__main__":
    print(mark_svg("wordmark__mark"))
    print(favicon_svg())
