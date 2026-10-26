"""Quiet ambient bed for the Learn tarot article videos (DESIGN.md section 19). Original, synthesised from scratch.

Same voice as the homepage score (scripts/explainer/music.py): a soft pad in D major with a few bell tones, but sized to
any length and sparse, so it sits under a voiceover. Each article gets its own variation from a seed (the slug).

    from bed import make_bed
    make_bed(duration, "bed.wav", seed="the-one-card-tarot-spread", cues=[0.4, 12.0, 30.5], level_db=-24)
"""
import hashlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def make_bed(duration, out_path, seed="readmyspread", cues=(), level_db=-24.0):
    n_total = int(SR * duration)
    rng = np.random.default_rng(int(hashlib.sha1(seed.encode()).hexdigest()[:8], 16))
    L, R = np.zeros(n_total), np.zeros(n_total)

    def add(sig, start, gain=1.0, pan=0.0):
        i = int(start * SR)
        if i >= n_total:
            return
        if i < 0:
            sig, i = sig[-i:], 0
        sig = sig[: n_total - i]
        gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        L[i:i + len(sig)] += sig * gain * gl
        R[i:i + len(sig)] += sig * gain * gr

    def env(n, a, r):
        e = np.ones(n)
        na, nr = int(a * SR), int(r * SR)
        if na + nr > n:  # short note: scale fades to fit
            k = n / (na + nr)
            na, nr = int(na * k), int(nr * k)
        if na: e[:na] = np.sin(np.linspace(0, np.pi / 2, na)) ** 2
        if nr: e[-nr:] *= np.cos(np.linspace(0, np.pi / 2, nr)) ** 2
        return e

    # D major colour, as in the homepage score
    D9 = [50, 57, 61, 64, 66]
    Bm9 = [47, 54, 59, 61, 62, 66]
    G7 = [43, 50, 54, 59, 62, 66]
    A6 = [45, 52, 57, 59, 61, 64]
    Em9 = [40, 47, 54, 55, 59, 62]
    loop = [D9, Bm9, G7, A6, Em9, G7, A6, D9]
    shift = int(rng.integers(0, len(loop)))
    loop = loop[shift:] + loop[:shift]

    # One chord every 6 to 8 seconds, overlapping; the piece always ends on D
    chords, s, i = [], 0.0, 0
    while s < duration:
        length = float(rng.uniform(6.0, 8.0))
        chords.append((s, min(s + length, duration), loop[i % len(loop)]))
        s += length
        i += 1
    chords[-1] = (chords[-1][0], duration, D9)

    for s, e, notes in chords:
        length = (e - s) + 1.8
        n = int(length * SR)
        tt = np.arange(n) / SR
        pad = np.zeros(n)
        for m in notes:
            f = hz(m + 12 if m < 48 else m)
            for d in (-0.06, 0.0, 0.07):
                ph = rng.uniform(0, 2 * np.pi)
                w = f * (1 + d / 100 * 12)
                pad += np.sin(2 * np.pi * w * tt + ph) + 0.18 * np.sin(4 * np.pi * w * tt + ph)
        pad *= (0.85 + 0.15 * np.sin(2 * np.pi * 0.18 * tt + rng.uniform(0, 6)))
        pad *= env(n, 1.6, 2.0) / (len(notes) * 3)
        add(pad, s - 0.2, 0.33, pan=-0.15)
        add(pad, s - 0.17, 0.33, pan=0.15)
        root = hz(notes[0] - 12 if notes[0] >= 45 else notes[0])
        bass = np.sin(2 * np.pi * root * tt) + 0.25 * np.sin(4 * np.pi * root * tt)
        add(bass * env(n, 1.2, 2.0), s - 0.1, 0.11)

    def bell(f, dur=2.4, bright=1.0):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        sig = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.2)
               + 0.35 * bright * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 4.5)
               + 0.12 * bright * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt * 7.0))
        atk = int(0.004 * SR)
        sig[:atk] *= np.linspace(0, 1, atk)
        return sig

    # A bell tone every two seconds or so, high and soft
    t = 2.2
    while t < duration - 3:
        chord = next(c for s, e, c in chords if s <= t < e)
        tones = sorted(set(m % 12 for m in chord))
        m = 74 + tones[int(rng.integers(0, len(tones)))]
        while m > 86: m -= 12
        add(bell(hz(m), 2.2, 0.7), t, 0.05 * rng.uniform(0.7, 1.0), pan=rng.uniform(-0.5, 0.5))
        t += float(rng.uniform(1.6, 2.6))

    # A chime where each scene begins
    for k, when in enumerate(cues):
        for j, m in enumerate(([81, 85] if k == 0 else [86]) if when < duration - 1 else []):
            add(bell(hz(m), 3.0, 1.0), when + j * 0.09, 0.07, pan=(j - 0.5) * 0.4)

    # Reverb
    ir_n = int(3.0 * SR)
    decay = np.exp(-np.arange(ir_n) / SR * 2.1)
    lp = butter(1, 5500, fs=SR, output="sos")
    irL = sosfilt(lp, rng.standard_normal(ir_n)) * decay
    irR = sosfilt(lp, rng.standard_normal(ir_n)) * decay
    irL /= np.sqrt(np.sum(irL ** 2)); irR /= np.sqrt(np.sum(irR ** 2))
    outL = L * 0.72 + fftconvolve(L, irL)[:n_total] * 0.42
    outR = R * 0.72 + fftconvolve(R, irR)[:n_total] * 0.42

    hp = butter(2, 35, btype="high", fs=SR, output="sos")
    outL, outR = sosfilt(hp, outL), sosfilt(hp, outR)
    fade = np.ones(n_total)
    fi, fo = int(min(1.0, duration / 3) * SR), int(min(2.4, duration / 3) * SR)
    fade[:fi] = np.linspace(0, 1, fi) ** 2
    fade[-fo:] = np.linspace(1, 0, fo) ** 1.6
    st = np.stack([outL * fade, outR * fade], axis=1)
    st *= 10 ** (level_db / 20) / np.sqrt(np.mean(st ** 2))
    peak = np.max(np.abs(st))
    if peak > 10 ** (-1.5 / 20):
        st *= 10 ** (-1.5 / 20) / peak
    wavfile.write(str(out_path), SR, (st * 32767).astype(np.int16))
    return out_path
