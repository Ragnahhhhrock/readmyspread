"""Queues each new Learn tarot video on Instagram (Reels), TikTok and YouTube (Shorts) through Buffer (DESIGN.md section 19).

    python3 scripts/post-social.py [--dry-run] [--per-day 2] [--introspect]

Needs the secret BUFFER_API_KEY (Buffer, Settings, API). Without it the script says so and exits cleanly.
Optional: BUFFER_ORGANIZATION_ID (otherwise the account's first organisation is used), BUFFER_API_URL (tests).

How it works
- Candidates are published articles that have a 9:16 video (public/assets/video/social/<slug>.mp4) and are not yet in
  content/learn-tarot/videos/posted.json. Oldest first, at most --per-day articles a day, so a backlog drains slowly.
- Buffer fetches the video from a public URL, so the script waits until https://readmyspread.com/assets/video/social/<slug>.mp4
  is live (the site deploys from this repo) before it posts.
- Posts use Buffer's addToQueue: Buffer picks the next slot in the posting schedule you set for each channel in Buffer.
- Channels are found by service (instagram, tiktok, youtube). Connect them in Buffer; any that are missing are skipped.
- Each caption says the voice is AI and links the article. TikTok is also flagged as AI-generated where Buffer allows.
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "learn-tarot"
STORIES = CONTENT / "videos"
STATE = STORIES / "posted.json"
PUB = ROOT / "public"
SITE = "https://readmyspread.com"
API = os.environ.get("BUFFER_API_URL", "https://api.buffer.com")
SERVICES = ("instagram", "tiktok", "youtube")
HASHTAGS = "#tarot #tarotspread #tarotreading #learntarot"


def gql(query, key):
    r = requests.post(API, json={"query": query}, headers={"Authorization": f"Bearer {key}", "content-type": "application/json"}, timeout=60)
    try:
        data = r.json()
    except ValueError:
        raise SystemExit(f"Buffer returned {r.status_code}: {r.text[:200]}")
    return data


def q(s):
    """A GraphQL string literal."""
    return json.dumps(s, ensure_ascii=False)


def find_channels(key):
    org = os.environ.get("BUFFER_ORGANIZATION_ID")
    if not org:
        d = gql("query { account { organizations { id name } } }", key)
        orgs = (((d.get("data") or {}).get("account") or {}).get("organizations")) or []
        if not orgs:
            raise SystemExit(f"Could not find a Buffer organisation (set BUFFER_ORGANIZATION_ID): {json.dumps(d)[:300]}")
        org = orgs[0]["id"]
    d = gql("query { channels(input: { organizationId: %s }) { id name service } }" % q(org), key)
    chans = (d.get("data") or {}).get("channels") or []
    found = {}
    for c in chans:
        svc = str(c["service"]).lower()
        if svc in SERVICES and svc not in found:
            found[svc] = c
    return found


def captions(story, slug):
    title, desc = story["title"], story["description"]
    link = f"{SITE}/learn-tarot/{slug}/"
    body = f"{title}\n\n{desc}\n\nFull guide: {link.replace('https://', '')}\n\nNarrated with an AI voice. For entertainment only.\n\n{HASHTAGS}"
    yt_title = (title + " | Learn tarot #Shorts")[:100]
    return body, yt_title


def mutation(channel, svc, text, video_url, thumb_ms, yt_title, with_meta=True):
    meta = ""
    if with_meta:
        if svc == "instagram":
            meta = "metadata: { instagram: { type: reel, shouldShareToFeed: true } }"
        elif svc == "youtube":
            meta = f"metadata: {{ youtube: {{ title: {q(yt_title)}, categoryId: \"27\", privacy: public, madeForKids: false }} }}"
        elif svc == "tiktok":
            meta = "metadata: { tiktok: { isAiGenerated: true } }"
    return f"""mutation {{
  createPost(input: {{
    text: {q(text)}
    channelId: {q(channel['id'])}
    schedulingType: automatic
    mode: addToQueue
    {meta}
    assets: [{{ video: {{ url: {q(video_url)}, metadata: {{ thumbnailOffset: {int(thumb_ms)} }} }} }}]
  }}) {{
    ... on PostActionSuccess {{ post {{ id }} }}
    ... on MutationError {{ message }}
  }}
}}"""


def create(channel, svc, text, video_url, thumb_ms, yt_title, key, dry):
    for with_meta in (True, False):
        m = mutation(channel, svc, text, video_url, thumb_ms, yt_title, with_meta)
        if dry:
            print(m)
            return "dry-run"
        d = gql(m, key)
        res = (d.get("data") or {}).get("createPost")
        if res and res.get("post"):
            return res["post"]["id"]
        err = (res or {}).get("message") or json.dumps(d.get("errors") or d)[:300]
        # A schema that does not know our metadata fields: try once without them (Instagram and YouTube need theirs)
        if with_meta and svc == "tiktok" and re.search(r"metadata|isAiGenerated|not defined|unknown", err, re.I):
            print(f"  {svc}: metadata not accepted ({err}); retrying without it")
            continue
        print(f"  {svc}: not queued: {err}")
        return None
    return None


def wait_live(url, minutes=12):
    end = time.time() + minutes * 60
    while time.time() < end:
        try:
            r = requests.head(url, timeout=20, allow_redirects=True, headers={"user-agent": "readmyspread-social/1.0"})
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(30)
    return False


def introspect(key):
    for name in ("CreatePostInput", "PostInputMetaData", "InstagramPostMetadataInput", "YoutubePostMetadataInput", "TiktokPostMetadataInput"):
        d = gql('query { __type(name: %s) { name inputFields { name type { name kind ofType { name kind } } } enumValues { name } } }' % q(name), key)
        print(name, json.dumps((d.get("data") or {}).get("__type") or d.get("errors"), indent=1)[:1500])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--per-day", type=int, default=int(os.environ.get("SOCIAL_PER_DAY", "2")))
    ap.add_argument("--introspect", action="store_true")
    ap.add_argument("--no-wait", action="store_true", help="do not wait for the video URL to be live (tests)")
    args = ap.parse_args()

    key = os.environ.get("BUFFER_API_KEY")
    if not key and not args.dry_run:
        print("BUFFER_API_KEY is not set, so nothing is posted. Add it as a repository secret to turn posting on.")
        return
    if args.introspect:
        introspect(key)
        return

    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    today = datetime.now(timezone.utc).date().isoformat()
    started_today = sum(1 for v in state.values() if v.get("at", "")[:10] == today)
    sched = {a["slug"]: a for a in json.loads((CONTENT / "schedule.json").read_text())["articles"]}
    now = datetime.now(timezone.utc)

    cands = []
    for f in STORIES.glob("*.json"):
        if f.name == "posted.json":
            continue
        st = json.loads(f.read_text())
        slug = st["slug"]
        if "video" not in st or not (PUB / st["video"]["social"].lstrip("/")).exists():
            continue
        if datetime.fromisoformat(sched[slug]["publish"]) > now:
            continue
        cands.append((sched[slug]["publish"], slug, st))
    cands.sort()

    channels = {} if args.dry_run and not key else find_channels(key)
    if args.dry_run and not key:
        channels = {s: {"id": f"dry-{s}", "name": s, "service": s} for s in SERVICES}
    if not channels:
        print("No Instagram, TikTok or YouTube channels are connected in Buffer yet.")
        return
    print("channels:", ", ".join(f"{s} ({c['name']})" for s, c in channels.items()))

    posted_articles = 0
    for _, slug, st in cands:
        done = state.get(slug, {}).get("channels", {})
        todo = [s for s in channels if s not in done]
        if not todo:
            continue
        if slug not in state and started_today + posted_articles >= args.per_day:
            break
        url = SITE + st["video"]["social"]
        if not args.dry_run and not args.no_wait and not wait_live(url):
            print(f"{slug}: {url} is not live yet; leaving it for the next run")
            continue
        text, yt_title = captions(st, slug)
        print(f"== {slug}")
        entry = state.setdefault(slug, {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "channels": {}})
        for svc in todo:
            pid = create(channels[svc], svc, text, url, st["video"]["thumbnail_ms"], yt_title, key, args.dry_run)
            if pid and not args.dry_run:
                entry["channels"][svc] = pid
                print(f"  {svc}: queued ({pid})")
        if not entry["channels"]:
            del state[slug]
        else:
            posted_articles += 0 if slug in state and entry.get("counted") else 1
            entry["counted"] = True
        if not args.dry_run:
            STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(f"done: {posted_articles} article(s) queued")


if __name__ == "__main__":
    main()
