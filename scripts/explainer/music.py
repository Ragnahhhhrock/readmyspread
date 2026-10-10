"""Original ambient score for the readmyspread explainer, synthesised from scratch (no samples, no licensed audio).

Calm and plain, like the site: a soft pad in D major, a slow bell arpeggio, and quiet chimes on the on-screen moments
(the mark, the shutter, each card flip, each tap). Cue times match scripts/explainer/scene.html.

    python3 scripts/explainer/music.py out.wav
"""
import sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
DUR = 56.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(17)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.sin(np.linspace(0, np.pi / 2, na)) ** 2
    if nr: e[-nr:] *= np.cos(np.linspace(0, np.pi / 2, nr)) ** 2
    return e


L = np.zeros(N)
R = np.zeros(N)


def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N: return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i]
    gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * gain * gl
    R[i:i + len(sig)] += sig * gain * gr


# Chords: (start, length, midi notes). D major colour, with the outro resolving home.
D9 = [50, 57, 61, 64, 66]       # D A C# E F#
Bm9 = [47, 54, 59, 61, 62, 66]  # B F# B C# D F#
G7 = [43, 50, 54, 59, 62, 66]   # G D F# B D F#
A6 = [45, 52, 57, 59, 61, 64]   # A E A B C# E
Em9 = [40, 47, 54, 55, 59, 62]
prog = [D9, Bm9, G7, A6, D9, Bm9, Em9, A6, G7, D9, Bm9, G7, A6, D9]
starts = [0, 4, 6.2, 10, 14, 16.3, 20, 22, 26, 29.4, 33, 37, 40, 44, 47]
chords = []
for i, c in enumerate(prog + [D9]):
    s = starts[i] if i < len(starts) else starts[-1]
    e = starts[i + 1] if i + 1 < len(starts) else DUR
    chords.append((s, e, c))
chords = [(s, e, c) for s, e, c in chords if s < DUR]
chords[-1] = (chords[-1][0], DUR, D9)

# Pad: detuned sines with a little second harmonic, slow swell, overlapping crossfades
for s, e, notes in chords:
    length = (e - s) + 1.6
    n = int(length * SR)
    tt = np.arange(n) / SR
    pad = np.zeros(n)
    for k, m in enumerate(notes):
        f = hz(m + 12 if m < 48 else m)
        for d in (-0.06, 0.0, 0.07):
            ph = rng.uniform(0, 2 * np.pi)
            w = f * (1 + d / 100 * 12)
            pad += np.sin(2 * np.pi * w * tt + ph) + 0.18 * np.sin(4 * np.pi * w * tt + ph)
    pad *= (0.85 + 0.15 * np.sin(2 * np.pi * 0.18 * tt + rng.uniform(0, 6)))
    pad *= env_adsr(n, 1.4, 1.8) / (len(notes) * 3)
    add(pad, s - 0.2, 0.33, pan=-0.15)
    add(pad, s - 0.17, 0.33, pan=0.15)
    # Bass root
    root = hz(notes[0] - 12 if notes[0] >= 45 else notes[0])
    bass = np.sin(2 * np.pi * root * tt) + 0.25 * np.sin(4 * np.pi * root * tt)
    add(bass * env_adsr(n, 1.0, 1.8), s - 0.1, 0.11)


def bell(f, dur=2.4, bright=1.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.2)
           + 0.35 * bright * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 4.5)
           + 0.12 * bright * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt * 7.0)
           + 0.05 * bright * np.sin(2 * np.pi * f * 4.17 * tt) * np.exp(-tt * 11.0))
    atk = int(0.004 * SR)
    sig[:atk] *= np.linspace(0, 1, atk)
    return sig


# Arpeggio: chord tones high up, one note every half second, gently uneven loudness
step = 0.5
pattern = [0, 2, 1, 3, 2, 4, 1, 3]
for i in range(int(DUR / step)):
    when = i * step
    if when < 6.4 or when > 53.5:
        continue
    if 21.7 < when < 22.6 or 32.8 < when < 33.4 or 46.3 < when < 47.4:
        continue  # breathe at scene changes
    chord = next(c for s, e, c in chords if s <= when < e)
    tones = sorted(set(m % 12 for m in chord))
    m = 74 + tones[pattern[i % len(pattern)] % len(tones)]
    while m > 86: m -= 12
    g = 0.055 * (1.0 if i % 4 == 0 else 0.72) * rng.uniform(0.85, 1.05)
    add(bell(hz(m), 2.2, 0.7), when, g, pan=rng.uniform(-0.5, 0.5))

# Chimes on the on-screen moments
cues = [
    (0.45, [81], 0.09), (1.9, [86, 90], 0.07), (2.95, [93], 0.05),    # mark, wordmark, tagline
    (6.45, [78, 85], 0.06),                                             # title
    (14.8, [93, 98], 0.08),                                             # shutter
    (19.0, [86], 0.07),                                                 # tap Read my cards
    (26.15, [81], 0.08), (26.67, [85], 0.08), (27.19, [88], 0.08),      # card flips
    (29.6, [90, 93], 0.06),                                             # spread recognised
    (42.3, [86], 0.07),                                                 # tap Listen
    (49.2, [86, 90], 0.07), (49.9, [93], 0.07),                         # wordmark and button
]
for when, ms, g in cues:
    for j, m in enumerate(ms):
        add(bell(hz(m), 3.0, 1.0), when + j * 0.09, g, pan=(j - 0.5) * 0.4)

# Shutter: a short soft click under the chime
n = int(0.06 * SR)
click = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 90)
click = sosfilt(butter(2, [1200, 6000], btype="band", fs=SR, output="sos"), click)
add(click, 14.8, 0.25)

# Shimmer swells into scene changes (band-passed noise)
def swell(start, length, peak=0.03):
    n = int(length * SR)
    noise = rng.standard_normal(n)
    noise = sosfilt(butter(2, [3000, 9000], btype="band", fs=SR, output="sos"), noise)
    e = np.sin(np.linspace(0, np.pi, n)) ** 3
    add(noise * e, start, peak, pan=-0.3)
    add(np.roll(noise, 900) * e, start, peak, pan=0.3)

for s in (5.2, 21.4, 32.4, 46.2):
    swell(s, 1.6)

# Reverb: stereo exponential-decay noise impulse
ir_n = int(3.2 * SR)
decay = np.exp(-np.arange(ir_n) / SR * 2.1)
lp = butter(1, 5500, fs=SR, output="sos")
irL = sosfilt(lp, rng.standard_normal(ir_n)) * decay
irR = sosfilt(lp, rng.standard_normal(ir_n)) * decay
irL /= np.sqrt(np.sum(irL ** 2)); irR /= np.sqrt(np.sum(irR ** 2))
wetL = fftconvolve(L, irL)[:N]
wetR = fftconvolve(R, irR)[:N]
outL = L * 0.72 + wetL * 0.42
outR = R * 0.72 + wetR * 0.42

# Low cut, fades, level
hp = butter(2, 35, btype="high", fs=SR, output="sos")
outL, outR = sosfilt(hp, outL), sosfilt(hp, outR)
fade = np.ones(N)
fi, fo = int(1.2 * SR), int(2.6 * SR)
fade[:fi] = np.linspace(0, 1, fi) ** 2
fade[-fo:] = np.linspace(1, 0, fo) ** 1.6
st = np.stack([outL * fade, outR * fade], axis=1)
rms = np.sqrt(np.mean(st ** 2))
st *= 10 ** (-19 / 20) / rms                     # about -19 dBFS RMS: background level
peak = np.max(np.abs(st))
if peak > 10 ** (-1.5 / 20):
    st *= 10 ** (-1.5 / 20) / peak

from scipy.io import wavfile
wavfile.write(sys.argv[1] if len(sys.argv) > 1 else "explainer-music.wav", SR, (st * 32767).astype(np.int16))
