"""Storyboard for a Learn tarot article video (DESIGN.md section 19).

Turns an article (content/learn-tarot/articles/<slug>.html and .json) into a short script: a hook, up to four key points
and a closing call to action. Deterministic, so the same article always gives the same script and nothing is invented:
every spoken line is a sentence (or the list of steps) taken from the article itself.

    python3 scripts/video_story.py <slug>          # print the storyboard
    storyboard(slug)                               # from other scripts

If content/learn-tarot/videos/<slug>.json exists and has "locked": true, it is used as written, so a script can be
hand-edited. Otherwise it is rebuilt from the article each time.
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "learn-tarot"
STORY_DIR = CONTENT / "videos"

SKIP_HEADINGS = re.compile(r"where to go next|read next|further reading|sources|common slips|keeping a|how the .* connect|reading them together", re.I)
MAX_POINTS = 4
MAX_POINT_WORDS = 30
MAX_HOOK_WORDS = 42
WORD_BUDGET = 128          # about 50 seconds at an even pace, so the video stays under 60 seconds
CTA = {
    "headline": "Have a tarot spread in front of you?",
    "caption": "Photograph it and get a clear reading, card by card.",
    "vo": "Have a tarot spread in front of you? Photograph it at read my spread dot com, and get a clear reading, card by card.",
}


class Blocks(HTMLParser):
    """Flattens an article body into h2 / p / list blocks. Notes and figure placeholders are dropped."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self._cur, self._skip, self._li, self._strong = [], None, 0, None, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div" and "note" in (a.get("class") or ""):
            self._skip = 1
        elif self._skip and tag == "div":
            self._skip += 1
        if self._skip:
            return
        if tag in ("h2", "h3", "p"):
            self._cur = {"t": tag, "text": ""}
        elif tag in ("ul", "ol"):
            self._cur = {"t": "list", "ordered": tag == "ol", "items": []}
        elif tag == "li" and self._cur is not None and self._cur["t"] == "list":
            self._li = {"text": "", "lead": ""}
        elif tag == "strong" and self._li is not None:
            self._strong = ""

    def handle_endtag(self, tag):
        if tag == "div" and self._skip:
            self._skip -= 1
            return
        if self._skip:
            return
        if tag in ("h2", "h3", "p") and self._cur is not None and self._cur["t"] == tag:
            self._cur["text"] = clean(self._cur["text"])
            if self._cur["text"]:
                self.blocks.append(self._cur)
            self._cur = None
        elif tag == "strong" and self._li is not None and self._strong is not None:
            if not self._li["lead"]:
                self._li["lead"] = clean(self._strong)
            self._strong = None
        elif tag == "li" and self._li is not None:
            self._li["text"] = clean(self._li["text"])
            self._cur["items"].append(self._li)
            self._li = None
        elif tag in ("ul", "ol") and self._cur is not None and self._cur["t"] == "list":
            self.blocks.append(self._cur)
            self._cur = None

    def handle_data(self, data):
        if self._skip:
            return
        if self._li is not None:
            self._li["text"] += data
            if self._strong is not None:
                self._strong += data
        elif self._cur is not None and self._cur["t"] in ("h2", "h3", "p"):
            self._cur["text"] += data


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def words(s):
    return len(s.split())


def sentences(text):
    parts = re.split(r"(?<=[.!?:])\s+(?=[A-Z\"'(])", text)
    return [p.strip() for p in parts if p.strip() and not p.strip().endswith(":")]


NUM = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}


def spoken_heading(h):
    h = re.sub(r"^Step (\d):", lambda m: f"Step {NUM[m.group(1)]}:", h)
    return h.rstrip(".?!:") + "."


def keyword_line(heading, text):
    """'Keywords: choice, values, union.' under a card heading becomes 'The Lovers stands for choice, values and union.'"""
    m = re.match(r"Keywords: ([^.]+)\.", text)
    if not m:
        return None
    kw = [k.strip() for k in m.group(1).split(",") if k.strip()]
    if len(kw) < 2:
        return None
    return f"{heading.rstrip('.')} stands for " + ", ".join(kw[:-1]) + " and " + kw[-1] + "."


def speakable(s):
    """Text as it should be read aloud: no brackets, a spoken site name, plain punctuation."""
    s = re.sub(r"\s*\([^)]*\)", "", s)                      # (VI) and other asides
    s = s.replace("readmyspread.com", "read my spread dot com").replace("readmyspread", "read my spread")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("—", ", ").replace("–", " to ").replace(" - ", ", ")
    s = re.sub(r"\s+([,.;:?!])", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def shown(s):
    """Text as it is shown on screen: as written, minus bracketed asides."""
    return re.sub(r"\s+", " ", re.sub(r"\s*\([^)]*\)", "", s)).strip()


def first_sentences(text, limit):
    out, n = [], 0
    for s in sentences(text):
        w = words(s)
        if out and n + w > limit:
            break
        if not out and w > limit + 8:
            return []
        out.append(s)
        n += w
        if n >= limit * 0.6:
            break
    return out


def point_text(blocks):
    """The line to read for one section: its first sentence, or the steps if it opens with a list of them."""
    first = next((b for b in blocks if b["t"] in ("p", "list")), None)
    if first is None:
        return ""
    if first["t"] == "list":
        leads = [i["lead"].rstrip(".:") for i in first["items"] if i["lead"]]
        if len(leads) >= 2:
            leads = leads[:5]
            low = [leads[0]] + [l[0].lower() + l[1:] for l in leads[1:]]
            return ", ".join(low[:-1]) + ", then " + low[-1] + "." if len(low) > 2 else " and ".join(low) + "."
        para = next((b for b in blocks if b["t"] == "p"), None)
        if para is None:
            return ""
        first = para
    got = first_sentences(first["text"], MAX_POINT_WORDS)
    return " ".join(got)


def pick_visual(slug, index, has_figure):
    s = slug.lower()
    for suit in ("wands", "cups", "swords", "pentacles"):
        if suit in s:
            return "suit:" + suit if index % 2 == 0 else "faces"
    if index == 0 and has_figure:
        return "figure"
    return ["faces", "backs", "faces"][index % 3]


def storyboard(slug):
    locked = STORY_DIR / f"{slug}.json"
    if locked.exists():
        data = json.loads(locked.read_text())
        if data.get("locked"):
            return data

    meta = json.loads((CONTENT / "articles" / f"{slug}.json").read_text())
    sched = json.loads((CONTENT / "schedule.json").read_text())
    entry = next(a for a in sched["articles"] if a["slug"] == slug)
    cats = {c["slug"]: c["name"] for c in sched["categories"]}
    body = (CONTENT / "articles" / f"{slug}.html").read_text()

    p = Blocks()
    p.feed(body)
    sections, cur = [], None
    for b in p.blocks:
        if b["t"] == "h2":
            cur = {"heading": b["text"], "blocks": []}
            sections.append(cur)
        elif cur is not None:
            cur["blocks"].append(b)

    hook_vo = " ".join(first_sentences(meta["lede"], MAX_HOOK_WORDS)) or meta["lede"]
    budget = WORD_BUDGET - words(hook_vo) - words(CTA["vo"])
    points = []
    for sec in sections:
        if SKIP_HEADINGS.search(sec["heading"]):
            continue
        text = point_text(sec["blocks"])
        if not text:
            continue
        if re.search(r"fuller treatment|full guide|see our|covered in|covered separately", text, re.I):
            continue
        kw = keyword_line(sec["heading"], text)
        spoken = kw if kw else spoken_heading(sec["heading"]) + " " + text
        w = words(spoken)
        if points and (len(points) >= MAX_POINTS or w > budget):
            continue
        if not points and w > budget:
            continue
        budget -= w
        points.append({"heading": shown(sec["heading"]), "text": text, "spoken": spoken})
    figures = list((meta.get("figures") or {}).values())

    scenes = [{"kind": "hook", "headline": entry["title"], "caption": shown(hook_vo), "vo": speakable(hook_vo)}]
    for i, pt in enumerate(points):
        scenes.append({"kind": "point", "n": i + 1, "of": len(points), "headline": pt["heading"], "caption": shown(pt["text"]),
                       "vo": speakable(pt["spoken"]),
                       "visual": pick_visual(slug, i, bool(figures))})
    scenes.append({"kind": "cta", **CTA})
    category = cats[entry["categories"][0]]
    return {
        "slug": slug,
        "title": entry["title"],
        "category": category,
        "description": meta["description"],
        "figure": figures[0]["file"] if figures else None,
        "scenes": scenes,
        "locked": False,
    }


if __name__ == "__main__":
    print(json.dumps(storyboard(sys.argv[1]), indent=2, ensure_ascii=False))
