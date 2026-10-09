"""Share bar markup, shared by scripts/build-learn.py and any hand-written page.

Three buttons only: Threads, Facebook, Instagram. No Telegram. See DESIGN.md section 12.
All three are plain new-tab links that work without JavaScript. Instagram has no web share
link, so it opens Instagram's messages page (the app on phones) and public/js/share.js copies the link.
"""
import html
from urllib.parse import quote

SITE = "https://readmyspread.com"
TAGLINE = "Your tarot spread, read plainly."


def share_text(title):
    """Share copy always says tarot (DESIGN.md section 7). Titles that don't fall back to the tagline."""
    t = title.strip()
    return t if "tarot" in t.lower() else f"{TAGLINE} readmyspread"


def sharebar(url, text, *, heading="Share this page", uid="share-title"):
    e = html.escape
    u, t = quote(url, safe=""), quote(text, safe="")
    threads = f"https://www.threads.com/intent/post?text={t}&amp;url={u}"
    facebook = f"https://www.facebook.com/sharer/sharer.php?u={u}"
    link = 'class="btn btn--secondary" target="_blank" rel="noopener noreferrer"'
    return (
        f'<section class="sharebar" aria-labelledby="{uid}" data-share-url="{e(url)}" data-share-text="{e(text)}">\n'
        f'  <h2 class="sharebar__title" id="{uid}">{e(heading)}</h2>\n'
        f'  <ul class="sharebar__list">\n'
        f'    <li><a {link} data-share="threads" href="{threads}">Share on Threads</a></li>\n'
        f'    <li><a {link} data-share="facebook" href="{facebook}">Share on Facebook</a></li>\n'
        f'    <li><a {link} data-share="instagram" href="https://www.instagram.com/direct/inbox/">Share on Instagram</a></li>\n'
        f'  </ul>\n'
        f'  <p class="sharebar__note" role="status" aria-live="polite" hidden></p>\n'
        f'</section>'
    )
