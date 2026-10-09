"""Builds content/learn-tarot/schedule.json and docs/learn-tarot-content-plan.md.

Run from the repo root:  python3 scripts/learn-plan.py
Publish times are random (seeded, so reruns give the same plan) between 6:00 am and 9:30 pm AWST,
never the same minute of the day twice and at least an hour apart from the previous day.
Articles that are already live keep their recorded time (see LIVE).
"""
import json, random, re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AWST = timezone(timedelta(hours=8))

CATEGORIES = [
    ("tarot-basics", "Tarot basics", "How tarot works: decks, positions, reversals and the words you will meet."),
    ("tarot-spreads", "Tarot spreads", "Layouts from one card to the Celtic Cross, with what each position asks."),
    ("major-arcana", "Major arcana", "The 22 trump cards, from The Fool to The World."),
    ("minor-arcana", "Minor arcana", "The 56 suit cards: wands, cups, swords and pentacles."),
    ("reading-tips", "Reading tips", "Practical ways to get more from a tarot spread, and from a photo of one."),
    ("tarot-history", "Tarot history", "Where the cards came from and how their use has changed."),
]

# Articles already published keep their real time.
LIVE = {"what-is-a-tarot-spread": "2026-10-09T11:03:00+08:00"}

B, S, M, N, R, H = "tarot-basics", "tarot-spreads", "major-arcana", "minor-arcana", "reading-tips", "tarot-history"

A = []  # (title, categories, covers, images)
def add(title, cats, covers, images): A.append((title, cats, covers, images))

add("What is a tarot spread?", [B, S], "What a spread is, why cards sit in positions, and how it differs from a single draw.", ["A tarot spread: cards laid in numbered positions", "Single draw versus tarot spread"])
add("A short history of tarot: where the cards came from", [H], "From fifteenth-century Italian card game to the Rider-Waite-Smith deck and modern reading.", ["Tarot timeline from the 1440s to today", "The standard 78-card tarot pack", "From card game to modern reading"])
add("How to read a tarot spread, step by step", [R, B], "Question, positions, each card, then the whole spread read together.", ["Reading a tarot spread in four steps"])
add("Tarot card positions and what they change", [B], "How the same card shifts meaning depending on its position.", ["One card in three tarot spread positions"])
add("Reversed tarot cards and how to read them", [B, R], "Upright versus reversed, three ways to approach reversals, and when to skip them.", ["Upright and reversed tarot card side by side"])
add("Major and minor arcana in tarot, explained", [B, M, N], "The 78 cards, 22 major and 56 minor, and how each group is read.", ["The 78 tarot cards: major and minor arcana"])
add("The one-card tarot spread", [S], "When a single card is enough, how to phrase a question, a worked example.", ["One-card tarot spread layout"])
add("The three-card tarot spread", [S], "Past, present, future and situation, action, outcome: two ways to read three cards.", ["Three-card tarot spread layout", "Three-card spread: two ways to read the positions"])
add("The Celtic Cross tarot spread explained", [S], "Ten cards, the cross and the staff, and when this spread suits a question.", ["Celtic Cross tarot spread layout"])
add("Celtic Cross tarot spread positions, one by one", [S], "What each of the ten positions asks, with reading tips.", ["Celtic Cross positions numbered one to ten"])
add("The Fool to the Hierophant: tarot card meanings", [M], "Major arcana 0 to V, upright and reversed.", ["The Fool; The Magician; The High Priestess; The Empress; The Emperor; The Hierophant (card faces)"])
add("The horseshoe tarot spread", [S], "Seven cards arched like a horseshoe: past, present, hidden influences, obstacles, others, advice, outcome.", ["Horseshoe tarot spread layout"])
add("The relationship tarot spread", [S], "A balanced layout for any relationship: partner, family, friend or colleague.", ["Relationship tarot spread layout"])
add("The Lovers to the Hermit: tarot card meanings", [M], "Major arcana VI to IX, upright and reversed.", ["The Lovers; The Chariot; Strength; The Hermit (card faces)"])
add("The two-path decision tarot spread", [S], "Comparing two options side by side without asking the cards to choose for you.", ["Two-path decision tarot spread layout"])
add("The yes or no tarot spread", [S], "How to frame a yes or no question, what the cards can and can't answer, a three-card method.", ["Yes or no tarot spread layout"])
add("The Wheel of Fortune to Temperance: tarot card meanings", [M], "Major arcana X to XIV, upright and reversed.", ["Wheel of Fortune; Justice; The Hanged Man; Death; Temperance (card faces)"])
add("The year-ahead tarot spread", [S], "Twelve cards, one per month, plus an overview card.", ["Year-ahead tarot spread layout"])
add("The astrological twelve-house tarot spread", [S], "Twelve cards mapped to the astrological houses and what each house covers.", ["Twelve-house tarot spread layout"])
add("The Devil to the Moon: tarot card meanings", [M], "Major arcana XV to XVIII, upright and reversed.", ["The Devil; The Tower; The Star; The Moon (card faces)"])
add("The Tree of Life tarot spread", [S], "Ten cards on the Kabbalistic tree, read from the root upward.", ["Tree of Life tarot spread layout"])
add("The moon phase tarot spread", [S], "Eight cards, one for each phase of the lunar cycle.", ["Moon phase tarot spread layout"])
add("The Sun to the World: tarot card meanings", [M], "Major arcana XIX to XXI, upright and reversed.", ["The Sun; Judgement; The World (card faces)"])
add("The pyramid tarot spread", [S], "Six cards in a triangle that build from foundation to outcome.", ["Pyramid tarot spread layout"])
add("The mind, body and spirit tarot spread", [S], "Three cards for a quick check-in on how you're doing.", ["Mind, body and spirit tarot spread layout"])
add("The four tarot suits and their elements", [B, N], "Wands, cups, swords and pentacles: element, themes, and how suits shape a spread.", ["The four tarot suits and their elements"])
for suit in ["Wands", "Cups", "Swords", "Pentacles"]:
    add(f"{suit} in tarot: Ace to Five meanings", [N], f"Ace to Five of {suit}, upright and reversed.", [f"Ace to Five of {suit} (five card faces)"])
    add(f"{suit} in tarot: Six to Ten meanings", [N], f"Six to Ten of {suit}, upright and reversed.", [f"Six to Ten of {suit} (five card faces)"])
    add(f"{suit} in tarot: court card meanings", [N], f"Page, Knight, Queen and King of {suit}.", [f"Page, Knight, Queen and King of {suit} (four card faces)"])
add("Numbers in tarot and what they signal", [N, B], "What Ace to Ten tend to suggest across all four suits.", ["Numbers Ace to Ten across the four tarot suits"])
add("How to photograph your tarot spread for a reading", [R], "Lighting, angle, spacing and framing so every card is legible, with a link to Read my cards.", ["A well-framed tarot spread photo: do and don't"])
add("Tarot terms glossary: spreads, cards and jargon", [B], "Plain definitions of common tarot terms.", ["Tarot terms at a glance"])

def slugify(t):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")

# Dates: article 1 on 9 Oct (live), history on 10 Oct, the rest keep the approved dates (article n on 9 Oct + n).
first = datetime(2026, 10, 9, tzinfo=AWST)
dates = []
for i, (title, *_rest) in enumerate(A):
    if i == 0: d = first
    elif i == 1: d = first + timedelta(days=1)
    else: d = first + timedelta(days=i)   # approved plan: item n (1-based, history excluded) -> 9 Oct + n
    dates.append(d)

rng = random.Random(20261009)
used, prev = set(), None
entries = []
for i, (title, cats, covers, images) in enumerate(A):
    slug = slugify(title)
    if slug in LIVE:
        pub = LIVE[slug]
        mod = datetime.fromisoformat(pub).hour * 60 + datetime.fromisoformat(pub).minute
    else:
        while True:
            mod = rng.randrange(6 * 60, 21 * 60 + 31)
            if mod not in used and (prev is None or abs(mod - prev) >= 60):
                break
        d = dates[i]
        pub = d.replace(hour=mod // 60, minute=mod % 60).isoformat()
    used.add(mod); prev = mod
    entries.append({"n": i + 1, "title": title, "slug": slug, "categories": cats, "covers": covers, "images": images, "publish": pub})

out = {"categories": [{"slug": s, "name": n, "description": d} for s, n, d in CATEGORIES], "articles": entries}
(ROOT / "content/learn-tarot/schedule.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

names = {s: n for s, n, _ in CATEGORIES}
def fmt(p):
    d = datetime.fromisoformat(p)
    return f"{d.day} {d.strftime('%b %Y')}, {d.strftime('%I:%M %p').lstrip('0').lower()}"
rows = []
for e in entries:
    rows.append(f"| {e['n']} | {e['title']} | {e['slug']} | {', '.join(names[c] for c in e['categories'])} | {e['covers']} | {'; '.join(e['images'])} | {fmt(e['publish'])} |")
md = f"""# Learn tarot: content and publishing plan

Generated by `scripts/learn-plan.py` from `content/learn-tarot/schedule.json`. Edit the script, not this file.

Section: `https://readmyspread.com/learn-tarot/`. Articles: `/learn-tarot/<url-stub>/`. Categories: `/learn-tarot/category/<category-stub>/`.
About page: `/about-tarot/`.
Cadence: one article per day at a random time between 6:00 am and 9:30 pm AWST (Australia/Perth, UTC+8), 9 Oct to 18 Nov 2026. Each article is held back until its time.

Every article has a title and meta description naming tarot spread readings, a canonical URL, `og:` tags, `twitter:card` = `summary_large_image`, its own share images (`og-<stub>.png` 1200 x 630, `twitter-<stub>.png` 1200 x 600), alt text and captions on every image, `lang="en-AU"`, one `h1`, and the standard footer. Images follow DESIGN.md.

## Categories

| Stub | Name | Covers |
| --- | --- | --- |
""" + "\n".join(f"| category/{s} | {n} | {d} |" for s, n, d in CATEGORIES) + """

## Articles

| # | Article title | URL stub | Categories | What it covers | Images to create | Publish (AWST) |
| --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(rows) + "\n"
(ROOT / "docs/learn-tarot-content-plan.md").write_text(md)
print(len(entries), "articles")
for e in entries[:6]: print(e["publish"], e["slug"])
