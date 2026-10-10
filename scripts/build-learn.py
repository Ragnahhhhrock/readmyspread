"""Builds the Learn tarot section and the About tarot page into public/, and rewrites public/sitemap.xml.

Run from the repo root:  python3 scripts/build-learn.py [--now 2026-10-10T12:00:00+08:00]

- Reads content/learn-tarot/schedule.json (categories, article list, publish times) and, for each article,
  content/learn-tarot/articles/<slug>.html (body) and <slug>.json (description, lede, figures with alt text and captions).
- Only articles whose publish time has passed are written. Anything still scheduled is left out of public/ entirely,
  including its images, hub listing, category listing and sitemap entry.
- Missing figures and share images for published articles are rendered by scripts/learn_images.py.
- Safe to run repeatedly (it rebuilds public/learn-tarot/ and public/about-tarot/ from scratch).
Prints the slugs that went live in this run, one per line, prefixed NEW:.
"""
import argparse, html, json, re, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
CONTENT = ROOT / "content" / "learn-tarot"
SITE = "https://readmyspread.com"
sys.path.insert(0, str(ROOT / "scripts"))
from sharebar import sharebar, share_text

DEFAULT_OG = f"{SITE}/assets/og-image.png"
DEFAULT_TW = f"{SITE}/assets/twitter-card.png"
DEFAULT_ALT = "Three tarot cards, The Star, The Moon and The Sun, laid over a faded gold zodiac wheel beside the words readmyspread, tarot spread readings. Your tarot spread, read plainly."

from mark import mark_svg  # the tarot card mark, shared with the favicon and share images
MARK = mark_svg("wordmark__mark")

e = html.escape


def long_date(iso):
    d = datetime.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B %Y')}"


def share(path, title):
    """Share bar for a generated page: Threads, Facebook, Instagram (DESIGN.md section 12)."""
    return sharebar(f"{SITE}{path}", share_text(title + " | readmyspread")).replace("\n", "\n    ")


def head(title, desc, path, *, og_type="website", og_img=DEFAULT_OG, tw_img=DEFAULT_TW, img_alt=DEFAULT_ALT, extra="", jsonld=None, robots="index, follow, max-image-preview:large", scripts=""):
    url = f"{SITE}{path}"
    ld = f'\n  <script type="application/ld+json">\n  {json.dumps(jsonld, ensure_ascii=False)}\n  </script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="en-AU">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(title)} | readmyspread</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{url}">
  <meta name="robots" content="{robots}">
  <meta name="author" content="readmyspread">
  <meta name="theme-color" content="#0b1024">
  <meta name="color-scheme" content="dark">

  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="readmyspread">
  <meta property="og:locale" content="en_AU">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:image" content="{og_img}">
  <meta property="og:image:secure_url" content="{og_img}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{e(img_alt)}">{extra}

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(desc)}">
  <meta name="twitter:image" content="{tw_img}">
  <meta name="twitter:image:alt" content="{e(img_alt)}">

  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">

  <link rel="preload" href="/fonts/cormorant-garamond-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/hanken-grotesk-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/css/tokens.css?v=20261010f">
  <link rel="stylesheet" href="/css/components.css?v=20261010f">
  <link rel="stylesheet" href="/css/landing.css?v=20261010f">
  <link rel="stylesheet" href="/css/learn.css?v=20261010f">{ld}
  <script defer src="/js/analytics.js?v=20261010f"></script>
  <script defer src="/js/share.js?v=20261010f"></script>
  <script defer src="/js/menu.js?v=20261010f"></script>{scripts}
</head>
<body class="landing">
  <div class="sky" aria-hidden="true"></div>
"""


BARS = '<svg class="menu-btn__bars" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
CROSS = '<svg class="menu-btn__x" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'


def nav(current=""):
    """The site header. Hand-written pages carry the same markup between <!--nav--> markers, rewritten by sync_static_nav()."""
    def cur(k): return ' aria-current="page"' if current == k else ""
    return f"""
  <header class="site-nav">
    <a class="wordmark" href="/" aria-label="readmyspread, home">{MARK}readmyspread</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-menu">{BARS}{CROSS}<span class="menu-btn__label">Menu</span></button>
    <nav id="site-menu" class="site-menu" aria-label="Main">
      <a class="menu-link" href="/learn-tarot/"{cur('learn')}>Learn tarot</a>
      <a class="menu-link" href="/about-tarot/"{cur('about')}>About tarot</a>
      <a class="menu-link" href="/contact/"{cur('contact')}>Contact</a>
      <a class="btn btn--secondary" href="/read/">Read my cards</a>
    </nav>
  </header>
"""


STATIC_NAV_PAGES = {"index.html": "", "privacy/index.html": ""}


def sync_static_nav():
    """Rewrite the header between <!--nav--> and <!--/nav--> in the hand-written pages."""
    for rel, cur in STATIC_NAV_PAGES.items():
        f = PUB / rel
        if not f.exists():
            continue
        t = f.read_text()
        new = re.sub(r"<!--nav-->.*?<!--/nav-->", lambda m: "<!--nav-->" + nav(cur) + "  <!--/nav-->", t, flags=re.S)
        if new != t:
            f.write_text(new)


FOOT = """
  <footer class="site-footer">
    <div class="wide">
      <p>For entertainment only. Not medical, legal or financial advice.</p>
      <p><a href="/read/">Read my cards</a> &nbsp; <a href="/learn-tarot/">Learn tarot</a> &nbsp; <a href="/about-tarot/">About tarot</a> &nbsp; <a href="/contact/">Contact</a> &nbsp; <a href="/privacy/">Privacy</a></p>
      <p><a href="mailto:contact@readmyspread.com">contact@readmyspread.com</a></p>
    </div>
  </footer>
</body>
</html>
"""


def crumbs(items):
    out = []
    for i, (label, href) in enumerate(items):
        out.append(f'<a href="{href}">{e(label)}</a>' if href else f'<span aria-current="page">{e(label)}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + '<span aria-hidden="true">/</span>'.join(out) + "</nav>"


def chips(cats, counts, current=None):
    all_cur = ' aria-current="true"' if current is None else ""
    li = [f'<li><a class="chip" href="/learn-tarot/"{all_cur}>All articles</a></li>']
    for c in cats:
        cur = ' aria-current="true"' if current == c["slug"] else ""
        li.append(f'<li><a class="chip" href="/learn-tarot/category/{c["slug"]}/"{cur}>{e(c["name"])}</a></li>')
    return '<ul class="chips" aria-label="Categories">' + "".join(li) + "</ul>"


def post_card(a, catname):
    cats = " · ".join(catname[c] for c in a["categories"])
    return (f'<li class="post"><p class="post__cats">{e(cats)}</p>'
            f'<h2><a href="/learn-tarot/{a["slug"]}/">{e(a["title"])}</a></h2>'
            f'<p>{e(a["description"])}</p>'
            f'<p class="post__date"><time datetime="{a["publish"]}">{long_date(a["publish"])}</time></p></li>')


def guard_links(body, live_slugs):
    """Links to articles that are not live yet become plain text, so nothing points at a 404."""
    def sub(m):
        slug = m.group(1)
        return m.group(0) if slug in live_slugs or slug == "category" else m.group(2)
    return re.sub(r'<a href="/learn-tarot/([a-z0-9-]+)/">(.*?)</a>', sub, body, flags=re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", help="ISO time to treat as now (default: the real time)")
    args = ap.parse_args()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)

    sched = json.loads((CONTENT / "schedule.json").read_text())
    cats = sched["categories"]
    catname = {c["slug"]: c["name"] for c in cats}

    # Which articles are live: time has passed AND the body has been written.
    live = []
    for a in sched["articles"]:
        body = CONTENT / "articles" / f"{a['slug']}.html"
        if datetime.fromisoformat(a["publish"]) <= now and body.exists():
            meta = json.loads((CONTENT / "articles" / f"{a['slug']}.json").read_text())
            live.append({**a, **meta})
    live.sort(key=lambda a: a["publish"], reverse=True)
    live_slugs = {a["slug"] for a in live}

    previous = set()
    old = PUB / "learn-tarot"
    if old.exists():
        previous = {p.parent.name for p in old.glob("*/index.html") if p.parent.name != "category"}

    import learn_images
    for a in live:
        learn_images.ensure_figures(a["slug"])
        learn_images.ensure_share(a["slug"], a["title"])

    for d in (PUB / "learn-tarot", PUB / "about-tarot", PUB / "assets" / "learn"):
        if d.exists():
            shutil.rmtree(d)
    (PUB / "assets" / "learn").mkdir(parents=True)
    for a in live:   # only live articles' images reach public/
        for f in learn_images.OUT.glob("*.png"):
            if f.name.startswith(a["slug"] + "-") or f.name in (f"og-{a['slug']}.png", f"twitter-{a['slug']}.png"):
                shutil.copy(f, PUB / "assets" / "learn" / f.name)

    counts = {c["slug"]: sum(1 for a in live if c["slug"] in a["categories"]) for c in cats}

    # ---------------- hub
    out = PUB / "learn-tarot"
    out.mkdir(parents=True)
    desc = "Plain guides to tarot spreads and the cards: how each spread works, what the cards mean and where tarot comes from. New articles most days."
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Learn tarot", "url": f"{SITE}/learn-tarot/", "description": desc, "inLanguage": "en-AU",
          "isPartOf": {"@type": "WebSite", "name": "readmyspread", "url": SITE + "/"}}
    page = head("Learn tarot: tarot spreads and card meanings", desc, "/learn-tarot/", jsonld=ld) + nav("learn")
    page += f"""
  <main id="main" class="col learn-main">
    <div class="page-head">
      {crumbs([("Home", "/"), ("Learn tarot", None)])}
      <p class="eyebrow">Learn tarot</p>
      <h1>Tarot spreads and card meanings, explained plainly.</h1>
      <p class="lede">Guides to every tarot spread, the cards and where tarot comes from. A new article most days. New to tarot? Start with <a href="/about-tarot/">About tarot</a>.</p>
    </div>
    {chips(cats, counts)}
    <ul class="posts">{"".join(post_card(a, catname) for a in live)}</ul>
    {share("/learn-tarot/", "Learn tarot: tarot spreads and card meanings")}
  </main>
""" + FOOT
    (out / "index.html").write_text(page)

    # ---------------- categories
    for c in cats:
        items = [a for a in live if c["slug"] in a["categories"]]
        d = out / "category" / c["slug"]
        d.mkdir(parents=True)
        cdesc = f"{c['description']} Part of the readmyspread guide to tarot spread readings."
        robots = "index, follow, max-image-preview:large" if items else "noindex, follow"
        ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": c["name"], "url": f"{SITE}/learn-tarot/category/{c['slug']}/", "description": cdesc, "inLanguage": "en-AU"}
        body_list = f'<ul class="posts">{"".join(post_card(a, catname) for a in items)}</ul>' if items else '<p class="empty">Articles in this category are on the way. New ones are published most days.</p>'
        page = head(f"{c['name']}: learn tarot", cdesc, f"/learn-tarot/category/{c['slug']}/", jsonld=ld, robots=robots) + nav("learn")
        page += f"""
  <main id="main" class="col learn-main">
    <div class="page-head">
      {crumbs([("Home", "/"), ("Learn tarot", "/learn-tarot/"), (c["name"], None)])}
      <p class="eyebrow">Learn tarot</p>
      <h1>{e(c["name"])}</h1>
      <p class="lede">{e(c["description"])}</p>
    </div>
    {chips(cats, counts, c["slug"])}
    {body_list}
    {share(f"/learn-tarot/category/{c['slug']}/", f"{c['name']}: learn tarot")}
  </main>
""" + FOOT
        (d / "index.html").write_text(page)

    # ---------------- articles
    for a in live:
        slug = a["slug"]
        body = (CONTENT / "articles" / f"{slug}.html").read_text()
        for key, f in a.get("figures", {}).items():
            fig = (f'<figure class="figure"><img src="/assets/learn/{f["file"]}" width="1600" height="900" alt="{e(f["alt"])}" loading="lazy" decoding="async">'
                   f'<figcaption>{e(f["caption"])}</figcaption></figure>')
            body = body.replace(f"<!--fig:{key}-->", fig)
        body = guard_links(body, live_slugs)
        assert "<!--fig:" not in body, f"unplaced figure in {slug}"
        og = f"{SITE}/assets/learn/og-{slug}.png"
        tw = f"{SITE}/assets/learn/twitter-{slug}.png"
        alt = f"{a['title']}. Learn tarot from readmyspread: your tarot spread, read plainly, beside a gold zodiac wheel on a deep blue night sky."
        extra = (f'\n  <meta property="article:published_time" content="{a["publish"]}">'
                 f'\n  <meta property="article:modified_time" content="{a["publish"]}">'
                 f'\n  <meta property="article:section" content="{e(catname[a["categories"][0]])}">'
                 + "".join(f'\n  <meta property="article:tag" content="{e(catname[c])}">' for c in a["categories"]))
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["description"], "image": [og, tw],
               "datePublished": a["publish"], "dateModified": a["publish"], "inLanguage": "en-AU", "articleSection": catname[a["categories"][0]],
               "keywords": ", ".join(catname[c].lower() for c in a["categories"]),
               "mainEntityOfPage": f"{SITE}/learn-tarot/{slug}/",
               "author": {"@type": "Organization", "name": "readmyspread", "url": SITE + "/"},
               "publisher": {"@type": "Organization", "name": "readmyspread", "url": SITE + "/", "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/icon-512.png"}}},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                  {"@type": "ListItem", "position": 2, "name": "Learn tarot", "item": SITE + "/learn-tarot/"},
                  {"@type": "ListItem", "position": 3, "name": a["title"], "item": f"{SITE}/learn-tarot/{slug}/"}]}]
        cat_chips = '<ul class="chips" aria-label="Categories">' + "".join(
            f'<li><a class="chip" href="/learn-tarot/category/{c}/">{e(catname[c])}</a></li>' for c in a["categories"]) + "</ul>"
        more = [x for x in live if x["slug"] != slug and set(x["categories"]) & set(a["categories"])][:3]
        more_html = ""
        if more:
            more_html = '<section aria-labelledby="more-title" class="article__foot"><h2 id="more-title">More to read</h2><ul class="posts">' + "".join(post_card(x, catname) for x in more) + "</ul></section>"
        page = head(a["title"], a["description"], f"/learn-tarot/{slug}/", og_type="article", og_img=og, tw_img=tw, img_alt=alt, extra=extra, jsonld=ld) + nav("learn")
        page += f"""
  <main id="main" class="col learn-main">
    <article class="article">
      <header class="article__head">
        {crumbs([("Home", "/"), ("Learn tarot", "/learn-tarot/"), (a["title"], None)])}
        <p class="eyebrow">{e(catname[a["categories"][0]])}</p>
        <h1>{e(a["title"])}</h1>
        <p class="article__lede">{e(a["lede"])}</p>
        <p class="article__meta"><span>By readmyspread</span><span><time datetime="{a["publish"]}">{long_date(a["publish"])}</time></span></p>
      </header>
      <div class="prose">
{body}
      </div>
      <footer class="article__foot">
        <h2>Filed under</h2>
        {cat_chips}
        <div class="cta">
          <h2>Have a tarot spread in front of you?</h2>
          <p>Photograph it and get a clear reading, card by card. Free, no account.</p>
          <a class="btn btn--primary" href="/read/">Read my cards</a>
        </div>
      </footer>
    </article>
    {share(f"/learn-tarot/{slug}/", a["title"])}
    {more_html}
  </main>
""" + FOOT
        d = out / slug
        d.mkdir()
        (d / "index.html").write_text(page)

    # ---------------- about tarot (fixed page)
    meta = json.loads((CONTENT / "pages" / "about-tarot.json").read_text())
    body = guard_links((CONTENT / "pages" / "about-tarot.html").read_text(), live_slugs)
    ld = {"@context": "https://schema.org", "@type": "AboutPage", "name": meta["title"], "url": f"{SITE}/about-tarot/", "description": meta["description"], "inLanguage": "en-AU",
          "isPartOf": {"@type": "WebSite", "name": "readmyspread", "url": SITE + "/"}}
    d = PUB / "about-tarot"
    d.mkdir(parents=True)
    page = head(meta["title"] + ": tarot spreads, cards and how readings work", meta["description"], "/about-tarot/", jsonld=ld) + nav("about")
    page += f"""
  <main id="main" class="col learn-main">
    <article class="article">
      <header class="article__head">
        {crumbs([("Home", "/"), ("About tarot", None)])}
        <p class="eyebrow">Tarot spread readings</p>
        <h1>{e(meta["title"])}</h1>
        <p class="article__lede">{e(meta["lede"])}</p>
      </header>
      <div class="prose">
{body}
      </div>
      <footer class="article__foot">
        <div class="cta">
          <h2>Ready when your cards are.</h2>
          <p>Photograph your tarot spread and get a clear reading, card by card.</p>
          <a class="btn btn--primary" href="/read/">Read my cards</a>
        </div>
      </footer>
    </article>
    {share("/about-tarot/", meta["title"] + ": tarot spreads, cards and how readings work")}
  </main>
""" + FOOT
    (d / "index.html").write_text(page)

    # ---------------- contact (fixed pages)
    cdesc = "Contact readmyspread with a question about your tarot spread reading, a card that was misread, or the Learn tarot guides. We reply by email."
    ld = {"@context": "https://schema.org", "@type": "ContactPage", "name": "Contact readmyspread", "url": f"{SITE}/contact/", "description": cdesc, "inLanguage": "en-AU",
          "isPartOf": {"@type": "WebSite", "name": "readmyspread", "url": SITE + "/"}}
    d = PUB / "contact"
    (d / "sent").mkdir(parents=True, exist_ok=True)
    page = head("Contact: questions about tarot spread readings", cdesc, "/contact/", jsonld=ld, scripts='\n  <script defer src="/js/contact.js?v=20261010f"></script>') + nav("contact")
    page += """
  <main id="main" class="col learn-main">
    <div class="page-head">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">Contact</span></nav>
      <p class="eyebrow">Contact</p>
      <h1>Get in touch.</h1>
      <p class="lede">A question about your tarot spread reading, a card that was misread, or one of the guides? Send a message and we will reply by email.</p>
    </div>

    <div id="form-status" class="status" role="status" aria-live="polite" tabindex="-1" hidden></div>

    <form id="contact-form" class="form" method="post" action="/api/contact">
      <div class="field">
        <label for="c-name">Your name</label>
        <input class="input" id="c-name" name="name" type="text" autocomplete="name" maxlength="80" required>
        <p class="field__error" id="c-name-err" hidden></p>
      </div>
      <div class="field">
        <label for="c-email">Your email</label>
        <input class="input" id="c-email" name="email" type="email" inputmode="email" autocomplete="email" autocapitalize="none" spellcheck="false" maxlength="120" required aria-describedby="c-email-hint">
        <p class="hint" id="c-email-hint">So we can reply. Nothing else is done with it.</p>
        <p class="field__error" id="c-email-err" hidden></p>
      </div>
      <div class="field">
        <label for="c-message">Message</label>
        <textarea class="input" id="c-message" name="message" rows="7" maxlength="4000" required></textarea>
        <p class="field__error" id="c-message-err" hidden></p>
      </div>
      <div class="trap" aria-hidden="true"><label>Leave this empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
      <button class="btn btn--primary btn--block" type="submit" id="contact-send">Send message</button>
      <p class="muted small">Your message is emailed to contact@readmyspread.com. See the <a href="/privacy/">privacy page</a>. Prefer email? Write to <a href="mailto:contact@readmyspread.com">contact@readmyspread.com</a>.</p>
    </form>
  </main>
""" + FOOT
    (d / "index.html").write_text(page)

    page = head("Message sent", "Thanks for contacting readmyspread, the tarot spread reading site.", "/contact/sent/", robots="noindex, follow") + nav("contact")
    page += """
  <main id="main" class="col learn-main">
    <div class="page-head">
      <p class="eyebrow">Contact</p>
      <h1>Message sent.</h1>
      <p class="lede">Thank you. We will reply to the email address you gave.</p>
    </div>
    <p><a class="btn btn--secondary" href="/learn-tarot/">Keep reading: Learn tarot</a></p>
  </main>
""" + FOOT
    (d / "sent" / "index.html").write_text(page)

    # ---------------- sitemap
    urls = [("/", None), ("/read/", None), ("/privacy/", None), ("/about-tarot/", None), ("/contact/", None)]
    latest = live[0]["publish"] if live else None
    urls.append(("/learn-tarot/", latest))
    for c in cats:
        if counts[c["slug"]]:
            last = next(a["publish"] for a in live if c["slug"] in a["categories"])
            urls.append((f"/learn-tarot/category/{c['slug']}/", last))
    for a in live:
        urls.append((f"/learn-tarot/{a['slug']}/", a["publish"]))
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path, last in urls:
        sm += f"  <url><loc>{SITE}{path}</loc>" + (f"<lastmod>{last}</lastmod>" if last else "") + "</url>\n"
    sm += "</urlset>\n"
    (PUB / "sitemap.xml").write_text(sm)

    sync_static_nav()

    for s in sorted(live_slugs - previous):
        print("NEW:", s)
    print(f"{len(live)} live, {sum(1 for a in sched['articles'] if datetime.fromisoformat(a['publish']) > now)} scheduled")


if __name__ == "__main__":
    main()
