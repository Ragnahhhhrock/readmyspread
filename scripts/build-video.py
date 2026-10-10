"""Build the homepage explainer video (DESIGN.md section 16). Do not edit the outputs by hand.

    python3 scripts/build-video.py

Renders scripts/explainer/scene.html frame by frame in headless Chromium (Playwright) at 1080 x 1350 (4:5), 30 fps,
synthesises the score with scripts/explainer/music.py, and writes:

    public/assets/video/explainer-1080x1350.mp4   H.264 + AAC, faststart
    public/assets/video/explainer-poster.jpg      poster frame
"""
import io
import pathlib
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCENE = ROOT / "scripts/explainer/scene.html"
OUT = ROOT / "public/assets/video"
FPS = 30
W, H, SCALE = 540, 675, 2
POSTER_T = 4.6


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp())
    wav = tmp / "music.wav"
    subprocess.run([sys.executable, str(ROOT / "scripts/explainer/music.py"), str(wav)], check=True)

    mp4 = OUT / "explainer-1080x1350.mp4"
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
        "-i", str(wav),
        "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-level", "4.0", "-tune", "animation",
        "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", "-shortest", str(mp4),
    ], stdin=subprocess.PIPE)

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--allow-file-access-from-files"])
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        page.goto(SCENE.as_uri())
        page.evaluate("window.sceneReady")
        duration = page.evaluate("DURATION")
        frames = int(round(duration * FPS))
        for i in range(frames):
            page.evaluate(f"window.render({i / FPS})")
            ff.stdin.write(page.screenshot(type="png"))
            if i % 150 == 0:
                print(f"frame {i}/{frames}", flush=True)
        page.evaluate(f"window.render({POSTER_T})")
        Image.open(io.BytesIO(page.screenshot(type="png"))).convert("RGB").save(
            OUT / "explainer-poster.jpg", quality=86, optimize=True, progressive=True)
        browser.close()

    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg failed")
    print("wrote", mp4, mp4.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
