# Learn tarot videos: automation and one-time setup

What runs by itself (`.github/workflows/learn-videos.yml`, hourly, or from the Actions tab with "Run workflow"):

1. Releases any Learn tarot article that is due (`scripts/build-learn.py`).
2. Builds a video for each published article that has none: script from the article, a free offline text-to-speech voice (Piper, en_GB Jenny; no API key), captions, 4:5 and 9:16 renders (`scripts/build-article-video.py`, DESIGN.md section 19). At most 3 per run, so a backlog is cleared over a few hours.
3. Embeds the 4:5 video in the article page and commits and pushes everything. Cloudflare Pages then deploys it.
4. Waits for the vertical video's URL to be live, then queues it on Instagram, TikTok and YouTube through Buffer (`scripts/post-social.py`), at most two articles a day, oldest first.

## Repository secrets (GitHub, Settings, Secrets and variables, Actions)

| Name | Type | What for |
| --- | --- | --- |
| `BUFFER_API_KEY` | secret | Buffer, Settings, API, "Create API key". Without it posting is skipped and everything else still runs. |
| `BUFFER_ORGANIZATION_ID` | variable (optional) | Only if the Buffer account has more than one organisation. |

Also: Settings, Actions, General, Workflow permissions: "Read and write permissions".

## Buffer

1. Create or open the Buffer account and connect Instagram (Business or Creator account), TikTok and YouTube. Instagram and YouTube need Buffer's channel connection flow; it cannot be done from code.
2. For each channel set the posting schedule (days and times). The workflow uses "add to queue", so Buffer chooses the next free slot.
3. Buffer's free plan holds a small number of scheduled posts per channel. If posts start failing with a queue-limit message, lower `SOCIAL_PER_DAY` in the workflow or upgrade the plan.
4. First run: Actions, "Learn tarot videos", Run workflow, tick "dry_run". The log shows the exact posts. If Buffer's schema differs from what the script sends, run `python3 scripts/post-social.py --introspect` with `BUFFER_API_KEY` set to see the real field names.

## Notes

- Posts say the voice is AI and TikTok posts are flagged as AI-generated.
- To change a script, copy `content/learn-tarot/videos/<slug>.json`, edit the scene `vo` and `caption` lines, set `"locked": true`, then rebuild that article: `python3 scripts/build-article-video.py <slug>`.
- Local run: `pip install numpy scipy pillow playwright requests && playwright install chromium`, ffmpeg on the path, then `python3 scripts/build-article-video.py --live --missing --limit 1`.
