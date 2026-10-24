// Calming background music for the reading screens (DESIGN.md section 18).
// Original and synthesised in the browser with the Web Audio API: a slow, breathing pad that drifts
// through four soft chords. No audio files, no network, nothing recorded or stored.
// Start it from a tap (phones only allow sound after one).

const AC = typeof window !== "undefined" ? window.AudioContext || window.webkitAudioContext : null;

const LEVEL = 0.2;        // master level while playing
const DUCKED = 0.35;      // multiplier while the reading is being read aloud
const FADE_IN = 2.5;      // seconds
const FADE_OUT = 1.2;     // seconds
const CHORD_EVERY = 22000; // ms between chord changes

// Four voice-led chords in D major (Hz): Dmaj9, Bm7/D, Gmaj9, A add4. Five voices each.
const CHORDS = [
  [146.83, 220.0, 329.63, 369.99, 440.0],
  [146.83, 246.94, 293.66, 369.99, 440.0],
  [196.0, 246.94, 293.66, 369.99, 440.0],
  [220.0, 293.66, 329.63, 440.0, 554.37]
];

let ctx = null;
let master = null;
let duck = null;
let voices = []; // [{ a, b }] pairs of detuned oscillators
let chordTimer = null;
let suspendTimer = null;
let chord = 0;
let playing = false;
let ducked = false;

export function canPlayMusic() {
  return !!AC;
}

export function isPlaying() {
  return playing;
}

// A soft, long echo: two filtered feedback delays standing in for a reverb.
function echo(input, output) {
  const dry = ctx.createGain();
  dry.gain.value = 0.7;
  input.connect(dry);
  dry.connect(output);
  for (const [time, feedback] of [[0.41, 0.5], [0.67, 0.45]]) {
    const delay = ctx.createDelay(2);
    delay.delayTime.value = time;
    const fb = ctx.createGain();
    fb.gain.value = feedback;
    const tone = ctx.createBiquadFilter();
    tone.type = "lowpass";
    tone.frequency.value = 1400;
    const wet = ctx.createGain();
    wet.gain.value = 0.35;
    input.connect(delay);
    delay.connect(tone);
    tone.connect(fb);
    fb.connect(delay);
    tone.connect(wet);
    wet.connect(output);
  }
}

function build() {
  ctx = new AC();
  master = ctx.createGain();
  master.gain.value = 0;
  master.connect(ctx.destination);

  duck = ctx.createGain();
  duck.gain.value = 1;
  duck.connect(master);

  const bus = ctx.createGain();
  bus.gain.value = 1;
  const filter = ctx.createBiquadFilter();
  filter.type = "lowpass";
  filter.frequency.value = 900;
  filter.Q.value = 0.4;
  bus.connect(filter);
  echo(filter, duck);

  // The filter opens and closes very slowly, so the pad seems to breathe.
  const sweep = ctx.createOscillator();
  sweep.frequency.value = 0.035;
  const sweepDepth = ctx.createGain();
  sweepDepth.gain.value = 260;
  sweep.connect(sweepDepth);
  sweepDepth.connect(filter.frequency);
  sweep.start();

  CHORDS[0].forEach((freq, i) => {
    const gain = ctx.createGain();
    gain.gain.value = 0.11;
    gain.connect(bus);

    // Each voice swells and fades on its own slow cycle (8 to 16 seconds).
    const swell = ctx.createOscillator();
    swell.frequency.value = 0.06 + i * 0.011;
    const swellDepth = ctx.createGain();
    swellDepth.gain.value = 0.06;
    swell.connect(swellDepth);
    swellDepth.connect(gain.gain);
    swell.start(ctx.currentTime + i * 1.7);

    const a = ctx.createOscillator();
    const b = ctx.createOscillator();
    a.type = "sine";
    b.type = "triangle";
    a.frequency.value = freq;
    b.frequency.value = freq;
    a.detune.value = -6;
    b.detune.value = 6;
    const bGain = ctx.createGain();
    bGain.gain.value = 0.35; // the triangle only adds a little warmth
    a.connect(gain);
    b.connect(bGain);
    bGain.connect(gain);
    a.start();
    b.start();
    voices.push({ a, b });
  });
}

function nextChord() {
  chord = (chord + 1) % CHORDS.length;
  const now = ctx.currentTime;
  voices.forEach(({ a, b }, i) => {
    a.frequency.setTargetAtTime(CHORDS[chord][i], now, 3);
    b.frequency.setTargetAtTime(CHORDS[chord][i], now, 3);
  });
}

export function startMusic() {
  if (!AC) return false;
  try {
    if (!ctx) build();
    clearTimeout(suspendTimer);
    suspendTimer = null;
    ctx.resume();
    const now = ctx.currentTime;
    master.gain.cancelScheduledValues(now);
    master.gain.setTargetAtTime(LEVEL, now, FADE_IN / 3);
    if (!chordTimer) chordTimer = setInterval(nextChord, CHORD_EVERY);
    playing = true;
    return true;
  } catch {
    playing = false;
    return false;
  }
}

// Fades out, then suspends the context so it stops using the battery.
export function stopMusic({ immediate = false } = {}) {
  if (!ctx || !playing) return;
  playing = false;
  clearInterval(chordTimer);
  chordTimer = null;
  const now = ctx.currentTime;
  master.gain.cancelScheduledValues(now);
  master.gain.setTargetAtTime(0, now, immediate ? 0.02 : FADE_OUT / 3);
  clearTimeout(suspendTimer);
  suspendTimer = setTimeout(() => { try { ctx.suspend(); } catch {} }, immediate ? 150 : FADE_OUT * 1000 + 400);
}

// Lowers the music while the reading is read aloud, so the voice stays clear.
export function duckMusic(on) {
  ducked = !!on;
  if (!ctx) return;
  duck.gain.setTargetAtTime(ducked ? DUCKED : 1, ctx.currentTime, 0.6);
}

// Phones pause web audio in the background. Pick it up again when the person returns.
if (typeof document !== "undefined") {
  document.addEventListener("visibilitychange", () => {
    if (!ctx || !playing) return;
    try { document.hidden ? ctx.suspend() : ctx.resume(); } catch {}
  });
}
