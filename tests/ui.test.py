"""Browser tests with a mocked API. Run from the repo root:

    python3 -m http.server 8766 --directory public &
    python3 tests/ui.test.py

Needs: playwright with Chromium. Screenshots go to .scratch/shots (git-ignored).
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://localhost:8766"
IMG = str(ROOT / "public/assets/og-image.png")
SHOTS = ROOT / ".scratch" / "shots"
SHOTS.mkdir(parents=True, exist_ok=True)

OK = {"status": "ok", "needs_care": False, "spread": {"name": "Three-card spread", "card_count": 3, "note": ""},
 "cards": [{"name": "Five of Cups", "short": "5", "position": "Past", "orientation": "upright", "uncertain": False},
           {"name": "The Moon", "short": "XVIII", "position": "Present", "orientation": "upright", "uncertain": True},
           {"name": "The Tower", "short": "XVI", "position": "Future", "orientation": "reversed", "uncertain": False}],
 "verdict": "A spread about loss, uncertainty and a clearing of the ground.",
 "sections": [{"card": "Five of Cups", "position": "Past", "text": "Attention has been on what was spilled, while two cups are still standing behind you."},
              {"card": "The Moon", "position": "Present", "text": "Things are unclear at the moment, and it may be worth waiting for more information before deciding."},
              {"card": "The Tower, reversed", "position": "Future", "text": "A change is being resisted or delayed, and the pressure is likely to build until it is faced."}],
 "close": "What would you let go of first?"}

def run(pw, reply, shot=None):
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page()
    errs = []; pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    sent = {}
    def handle(route):
        sent["body"] = json.loads(route.request.post_data)
        status, body = reply
        route.fulfill(status=status, content_type="application/json", body=json.dumps(body))
    pg.route("**/api/read", handle)
    pg.route("**/metrics/**", lambda r: r.fulfill(status=200, content_type="application/javascript", body=""))
    pg.goto(BASE + "/read/"); pg.wait_for_timeout(300)
    if shot: pg.screenshot(path=str(SHOTS / f"{shot}-home.png"), full_page=True)
    pg.set_input_files("#in-roll", IMG); pg.wait_for_selector("#screen-preview:not([hidden])")
    if shot: pg.screenshot(path=str(SHOTS / f"{shot}-preview.png"), full_page=True)
    pg.click("#question-pills .pill:has-text('What should I focus on this month?')")
    pg.click("#btn-read"); pg.wait_for_timeout(700)
    return b, pg, sent, errs

with sync_playwright() as pw:
    # landing page: loads clean, links to the app, no horizontal scroll on mobile or desktop
    for w, h, name in [(390, 844, "m"), (1280, 800, "d")]:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": h}); errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.route("**/metrics/**", lambda r: r.fulfill(status=200, content_type="application/javascript", body=""))  # the gtag gateway only exists on Cloudflare
        pg.goto(BASE + "/"); pg.wait_for_timeout(500)
        assert "readmyspread" in pg.title()
        assert pg.locator("a[href='/read/']").count() >= 3
        assert pg.evaluate("document.documentElement.scrollWidth") == w, "horizontal overflow"
        pg.screenshot(path=str(SHOTS / f"landing-{name}.png"), full_page=True)
        assert not errs, errs; b.close()
    # privacy page
    b = pw.chromium.launch(); pg = b.new_page(); pg.goto(BASE + "/privacy/"); assert "Privacy" in pg.inner_text("h1"); b.close()

    # happy path
    b, pg, sent, errs = run(pw, (200, OK), "ok")
    pg.wait_for_selector("#screen-result:not([hidden])")
    assert sent["body"]["mediaType"] == "image/jpeg" and len(sent["body"]["image"]) > 1000 and sent["body"]["question"] == "What should I focus on this month?"
    assert pg.inner_text("#res-spread") == "Three-card spread"
    assert pg.locator("#res-cards li").count() == 3
    assert "not sure" in pg.inner_text("#res-cards")
    assert pg.locator("a#btn-tip.btn--primary[href^='https://buy.stripe.com/']").count() == 1 and pg.locator("#btn-tip").bounding_box()["height"] >= 48
    assert pg.evaluate("document.documentElement.scrollWidth") == 390
    pg.screenshot(path=str(SHOTS / "ok-result.png"), full_page=True)
    pg.click("#btn-again"); assert pg.is_visible("#screen-home")
    assert not errs, errs; b.close()
    # no cards
    b, pg, _, errs = run(pw, (200, {"status": "no_cards", "needs_care": False, "verdict": "A cat on a sofa."}))
    pg.wait_for_selector("#screen-error:not([hidden])"); assert "No cards" in pg.inner_text("#error-title")
    pg.screenshot(path=str(SHOTS / "err.png")); b.close()
    # rate limit
    b, pg, _, _ = run(pw, (429, {"error": "rate_limited"}))
    pg.wait_for_selector("#screen-error:not([hidden])"); assert "enough readings" in pg.inner_text("#error-title"); b.close()
    # busy
    b, pg, _, _ = run(pw, (503, {"error": "busy"}))
    pg.wait_for_selector("#screen-error:not([hidden])"); assert "busy" in pg.inner_text("#error-title"); b.close()
    # care
    b, pg, _, _ = run(pw, (200, {"status": "ok", "needs_care": True, "verdict": "Let's put the cards down. I'm glad you said it."}))
    pg.wait_for_selector("#screen-result:not([hidden])")
    assert pg.is_visible("#res-care") and not pg.is_visible("#res-body") and not pg.is_visible("#btn-tip")
    pg.screenshot(path=str(SHOTS / "care.png")); b.close()

    # share bars: every page has Threads, Facebook and Instagram, no Telegram, 48px taps, no overflow on mobile
    PAGES = ["/", "/read/", "/privacy/", "/style-guide/", "/about-tarot/", "/learn-tarot/", "/learn-tarot/what-is-a-tarot-spread/"] + \
        ["/learn-tarot/category/" + c + "/" for c in ["tarot-basics", "tarot-spreads", "tarot-history", "reading-tips", "major-arcana", "minor-arcana"]]
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 844})
    for path in PAGES:
        pg.goto(BASE + path); pg.wait_for_timeout(200)
        bars = pg.locator(".sharebar")
        assert bars.count() >= 1, path + " has no share bar"
        assert pg.locator("[data-share='telegram'], a[href*='t.me'], a[href*='telegram']").count() == 0, path + " has Telegram"
        for m, host in [("threads", "threads.com"), ("facebook", "facebook.com"), ("instagram", "instagram.com")]:
            link = bars.first.locator(f"[data-share='{m}']")
            assert link.count() == 1 and host in link.get_attribute("href"), (path, m)
        if path != "/read/":
            for a in bars.first.locator("[data-share]").all():
                assert a.bounding_box()["height"] >= 47.5, (path, "tap target too small")
            assert pg.evaluate("document.documentElement.scrollWidth") == 390, path + " overflows"
    # reading result: share bar shows with the reading, and Instagram copies the link and opens as a new-tab link like the others
    b2, pg2, _, errs2 = run(pw, (200, OK))
    pg2.wait_for_selector("#screen-result:not([hidden])")
    assert pg2.locator("#screen-result .sharebar").is_visible()
    for a in pg2.locator("#screen-result .sharebar [data-share]").all():
        assert a.bounding_box()["height"] >= 47.5
    ig = pg2.locator("#screen-result .sharebar [data-share='instagram']")
    assert ig.get_attribute("target") == "_blank" and "instagram.com/direct/inbox" in ig.get_attribute("href")
    pg2.evaluate("window.__copied = null; navigator.clipboard.writeText = (x) => { window.__copied = x; return Promise.resolve(); }")
    with pg2.context.expect_page() as popup:
        pg2.click("#screen-result [data-share='instagram']")
    popup.value.close(); pg2.wait_for_timeout(200)
    assert pg2.evaluate("window.__copied") == "https://readmyspread.com/read/"
    assert "copied" in pg2.inner_text("#screen-result .sharebar__note")
    pg2.screenshot(path=str(SHOTS / "ok-result-share.png"), full_page=True)
    assert not errs2, errs2; b2.close(); b.close()
print("ui tests passed")
