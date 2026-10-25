"""Builds a short explainer video for each Learn tarot article (DESIGN.md section 19). Do not edit the outputs by hand.

    python3 scripts/build-article-video.py --live --missing            # every published article that has no video yet
    python3 scripts/build-article-video.py the-one-card-tarot-spread   # one article, rebuilt
    options: --limit N  --voice auto|elevenlabs|endpoint|none  --now ISO  --keep-frames

For each article it:
  1. writes the script (scripts/video_story.py), from the article's own text;
  2. voices each scene with the ElevenLabs voice the site already uses (Lily, the same settings as functions/api/speak.js);
  3. times every scene to its voiceover, renders the scene (scripts/explainer/article-scene.html) frame by frame in
     headless Chromium at 1080 x 1920, and mixes the voice over a quiet original bed (scripts/explainer/bed.py);
  4. writes, from that one render:

     public/assets/video/learn/<slug>.mp4       4:5, 720 x 900, for the article page (the central band of the 9:16 render)
     public/assets/video/learn/<slug>.jpg       poster
     public/assets/video/learn/<slug>.vtt       captions
     public/assets/video/social/<slug>.mp4      9:16, 1080 x 1920, for Instagram Reels, TikTok and YouTube Shorts
     content/learn-tarot/videos/<slug>.json     script, timings and file names (read by build-learn.py and post-social.py)

Voice: ELEVENLABS_API_KEY (and optionally ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL) calls ElevenLabs directly. Without a key it
falls back to the site's own /api/speak, which holds the same key (it has daily caps, so a large backlog is built over
several runs: the run stops cleanly when the endpoint says it is busy and the next run carries on). --voice none renders
with music only and estimated timings, for layout checks.

Only articles whose publish time has passed are built, so nothing scheduled ever reaches public/.
"""
import argparse
import hashlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import textwrap
from datetime import datetime, timezone

import numpy as np
import requests
from PIL import Image
from playwright.sync_api import sync_playwright
from scipy.io import wavfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "explainer"))
from video_story import storyboard, words  # noqa: E402
from bed import make_bed, SR  # noqa: E402

SCENE = ROOT / "scripts/explainer/article-scene.html"
CONTENT = ROOT / "content/learn-tarot"
STORIES = CONTENT / "videos"
PUB = ROOT / "public"
OUT_EMBED = PUB / "assets/video/learn"
OUT_SOCIAL = PUB / "assets/video/social"
SCRATCH = ROOT / ".scratch" / "vo"

FPS = 24
W, H, SCALE = 540, 960, 2
MAX_SECONDS = 59.0
WPS = 2.4                          # spoken words per second, used to size a script before it is voiced
LEAD = {"hook": 1.2, "point": 0.6, "cta": 0.7}
TAIL = {"hook": 0.7, "point": 0.7, "cta": 2.6}
SITE = "https://readmyspread.com"

DEFAULT_VOICE_ID = "pFZP5JQG7iQjIQuC4Bku"   # Lily, as functions/api/speak.js
DEFAULT_MODEL = "eleven_flash_v2_5"
VOICE_SETTINGS = {"stability": 0.6, "similarity_boost": 0.75, "style": 0, "use_speaker_boost": True, "speed": 0.95}


class Busy(Exception):
    """The voice service is rate limited or over its daily cap. The run stops and the next one carries on."""


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


# ----------------------------------------------------------------------------------------------------------------- voice
def voice_mode(requested):
    if requested != "auto":
        return requested
    return "elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") else "endpoint"


def clip_for(text, mode):
    """Returns the path of an mp3 for `text`, from the cache or the voice service."""
    voice = os.environ.get("ELEVENLABS_VOICE_ID") or DEFAULT_VOICE_ID
    model = os.environ.get("ELEVENLABS_MODEL") or DEFAULT_MODEL
    key = hashlib.sha1(f"{text}|{voice}|{model}|{json.dumps(VOICE_SETTINGS, sort_keys=True)}".encode()).hexdigest()[:20]
    SCRATCH.mkdir(parents=True, exist_ok=True)
    path = SCRATCH / f"{key}.mp3"
    if path.exists() and path.stat().st_size > 500:
        return path
    if mode == "elevenlabs":
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
            headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "content-type": "application/json", "accept": "audio/mpeg"},
            json={"text": text, "model_id": model, "voice_settings": VOICE_SETTINGS}, timeout=90)
        if r.status_code == 429:
            raise Busy("ElevenLabs rate limit")
    else:
        r = requests.post(f"{SITE}/api/speak", json={"text": text},
                          headers={"user-agent": "readmyspread-video/1.0", "content-type": "application/json"}, timeout=90)
        if r.status_code in (429, 503):
            raise Busy(f"/api/speak says {r.status_code}")
    if r.status_code != 200 or len(r.content) < 500:
        raise SystemExit(f"voice request failed: {r.status_code} {r.text[:200]}")
    path.write_bytes(r.content)
    return path


def duration_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def decode(path):
    """mp3 to mono float32 at 48 kHz."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


# ------------------------------------------------------------------------------------------------------------- timeline
def estimate(scenes):
    return sum(LEAD[s["kind"]] + words(s["vo"]) / WPS + TAIL[s["kind"]] for s in scenes)


def prune(scenes):
    """Drops the last key points until the script should fit in under a minute."""
    scenes = list(scenes)
    while estimate(scenes) > MAX_SECONDS - 3 and sum(s["kind"] == "point" for s in scenes) > 1:
        idx = max(i for i, s in enumerate(scenes) if s["kind"] == "point")
        del scenes[idx]
    pts = [s for s in scenes if s["kind"] == "point"]
    for n, s in enumerate(pts, 1):
        s["n"], s["of"] = n, len(pts)
    return scenes


def lay_out(scenes, durations):
    t = 0.0
    for s, d in zip(scenes, durations):
        s["start"] = round(t, 3)
        s["voStart"] = round(t + LEAD[s["kind"]], 3)
        s["voEnd"] = round(s["voStart"] + d, 3)
        s["end"] = round(s["voEnd"] + TAIL[s["kind"]], 3)
        t = s["end"]
    return t


def vtt_text(scenes):
    def ts(x):
        h, rem = divmod(x, 3600)
        m, sec = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{sec:06.3f}"
    out = ["WEBVTT", ""]
    for s in scenes:
        text = s["vo"].replace("read my spread dot com", "readmyspread.com")
        sents = [x for x in re.split(r"(?<=[.!?])\s+", text) if x]
        total = sum(len(x) for x in sents) or 1
        t = s["voStart"]
        for x in sents:
            d = (s["voEnd"] - s["voStart"]) * len(x) / total
            lines = textwrap.wrap(x, 42)
            while len(lines) > 2:                      # keep each cue to two lines
                lines = textwrap.wrap(x, max(42, len(x) // 2 + 6))
                break
            out += [f"{ts(t)} --> {ts(t + d)}", "\n".join(lines), ""]
            t += d
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------------------------- audio
def mix_audio(story, scenes, mode, tmp):
    total = story["duration"]
    n = int(total * SR) + SR
    vo = np.zeros(n, dtype=np.float32)
    have_voice = mode != "none"
    if have_voice:
        for s in scenes:
            clip = decode(s["_clip"])
            i = int(s["voStart"] * SR)
            vo[i:i + len(clip)] += clip[: n - i]
    vo_path, bed_path, out_path = tmp / "vo.wav", tmp / "bed.wav", tmp / "audio.wav"
    wavfile.write(str(vo_path), SR, (np.clip(vo, -1, 1) * 32767).astype(np.int16))
    make_bed(total, bed_path, seed=story["slug"], cues=[s["start"] for s in scenes], level_db=-24.0 if have_voice else -19.0)
    if have_voice:
        graph = ("[0:a]loudnorm=I=-16:TP=-1.5:LRA=7,aformat=sample_rates=48000:channel_layouts=stereo[vo];"
                 "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=1[bed];"
                 "[vo]asplit=2[v1][v2];"
                 "[bed][v2]sidechaincompress=threshold=0.015:ratio=9:attack=20:release=700:makeup=1[duck];"
                 "[v1][duck]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.89[out]")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(vo_path), "-i", str(bed_path), "-filter_complex", graph, "-map", "[out]",
             "-t", f"{total:.3f}", str(out_path)])
    else:
        run(["ffmpeg", "-y", "-v", "error", "-i", str(bed_path), "-t", f"{total:.3f}", str(out_path)])
    return out_path


# --------------------------------------------------------------------------------------------------------------- render
def render(story, audio, tmp, slug, keep_frames=False):
    OUT_EMBED.mkdir(parents=True, exist_ok=True)
    OUT_SOCIAL.mkdir(parents=True, exist_ok=True)
    reel = OUT_SOCIAL / f"{slug}.mp4"
    embed = OUT_EMBED / f"{slug}.mp4"
    poster = OUT_EMBED / f"{slug}.jpg"
    common = ["-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p", "-tune", "animation", "-r", str(FPS), "-movflags", "+faststart"]
    graph = "[0:v]split=2[r][e];[e]crop=1080:1350:0:285,scale=720:900:flags=lanczos[ev]"
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
        "-i", str(audio),
        "-filter_complex", graph,
        "-map", "[r]", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "24", *common,
        "-c:a", "aac", "-b:a", "128k", "-shortest", str(reel),
        "-map", "[ev]", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "26", *common,
        "-c:a", "aac", "-b:a", "96k", "-shortest", str(embed),
    ], stdin=subprocess.PIPE)

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--allow-file-access-from-files"])
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        page.goto(SCENE.as_uri())
        page.evaluate("window.sceneReady")
        page.evaluate("(s) => window.setStory(s)", story)
        frames = int(round(story["duration"] * FPS))
        poster_t = story["scenes"][0]["start"] + 3.2
        for i in range(frames):
            page.evaluate(f"window.render({i / FPS})")
            shot = page.screenshot(type="jpeg", quality=92)
            ff.stdin.write(shot)
            if keep_frames and i % 24 == 0:
                (tmp / f"f{i:05d}.jpg").write_bytes(shot)
            if i % 240 == 0:
                print(f"  frame {i}/{frames}", flush=True)
        page.evaluate(f"window.render({poster_t})")
        im = Image.open(io.BytesIO(page.screenshot(type="png"))).convert("RGB").crop((0, 285, 1080, 1635)).resize((720, 900), Image.LANCZOS)
        im.save(poster, quality=84, optimize=True, progressive=True)
        browser.close()
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed")
    return reel, embed, poster


# ------------------------------------------------------------------------------------------------------------------ main
def live_slugs(now):
    sched = json.loads((CONTENT / "schedule.json").read_text())
    out = []
    for a in sched["articles"]:
        if datetime.fromisoformat(a["publish"]) <= now and (CONTENT / "articles" / f"{a['slug']}.html").exists():
            out.append(a["slug"])
    return out


def build(slug, mode, keep_frames=False):
    print(f"== {slug}", flush=True)
    story = storyboard(slug)
    story["scenes"] = prune(story["scenes"])
    scenes = story["scenes"]

    if mode == "none":
        durations = [words(s["vo"]) / WPS for s in scenes]
    else:
        durations = []
        for s in scenes:
            s["_clip"] = clip_for(s["vo"], mode)
            durations.append(duration_of(s["_clip"]))
        # If the real voice runs long, drop key points and lay out again (their clips stay cached)
        while lay_out(scenes, durations) > MAX_SECONDS and sum(s["kind"] == "point" for s in scenes) > 1:
            idx = max(i for i, s in enumerate(scenes) if s["kind"] == "point")
            del scenes[idx]; del durations[idx]
            pts = [s for s in scenes if s["kind"] == "point"]
            for n, s in enumerate(pts, 1):
                s["n"], s["of"] = n, len(pts)
    total = lay_out(scenes, durations)
    if total > 60:
        raise SystemExit(f"{slug}: {total:.1f}s is over a minute")
    story["duration"] = round(total, 3)

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        audio = mix_audio(story, scenes, mode, tmp)
        public_story = {k: v for k, v in story.items()}
        for s in public_story["scenes"]:
            s.pop("_clip", None)
        reel, embed, poster = render(public_story, audio, tmp, slug, keep_frames)
    (OUT_EMBED / f"{slug}.vtt").write_text(vtt_text(scenes))

    STORIES.mkdir(parents=True, exist_ok=True)
    record = {k: v for k, v in public_story.items()}
    record["video"] = {
        "seconds": round(total),
        "embed": f"/assets/video/learn/{slug}.mp4",
        "poster": f"/assets/video/learn/{slug}.jpg",
        "captions": f"/assets/video/learn/{slug}.vtt",
        "social": f"/assets/video/social/{slug}.mp4",
        "voice": "none" if mode == "none" else "ElevenLabs",
        "thumbnail_ms": int((scenes[0]["start"] + 3.2) * 1000),
    }
    (STORIES / f"{slug}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(f"BUILT: {slug} ({total:.1f}s, embed {embed.stat().st_size // 1024} KB, reel {reel.stat().st_size // 1024} KB)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--live", action="store_true", help="all published articles")
    ap.add_argument("--missing", action="store_true", help="only those without a video yet")
    ap.add_argument("--limit", type=int, default=0, help="build at most N articles in this run")
    ap.add_argument("--voice", default="auto", choices=["auto", "elevenlabs", "endpoint", "none"])
    ap.add_argument("--now", help="ISO time to treat as now")
    ap.add_argument("--keep-frames", action="store_true")
    args = ap.parse_args()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    mode = voice_mode(args.voice)

    slugs = list(args.slugs)
    if args.live:
        slugs += [s for s in live_slugs(now) if s not in slugs]
    if not slugs:
        sys.exit("nothing to build: name a slug or use --live")
    published = set(live_slugs(now))
    for s in slugs:
        if s not in published:
            sys.exit(f"{s} is not published yet, so it gets no video")
    if args.missing:
        slugs = [s for s in slugs if not (OUT_SOCIAL / f"{s}.mp4").exists()]
    if args.limit:
        slugs = slugs[: args.limit]
    print(f"{len(slugs)} to build, voice: {mode}")
    for slug in slugs:
        try:
            build(slug, mode, args.keep_frames)
        except Busy as e:
            print(f"Voice service busy ({e}). Stopping here; the next run carries on.")
            break


if __name__ == "__main__":
    main()
