// Reads a finished reading aloud (DESIGN.md section 14).
// First choice: a female ElevenLabs voice, made by /api/speak (the key stays on the server).
// Fallback: the device's own voice (Web Speech API), if the voice service can't be reached.
// Nothing is recorded or stored by readmyspread.

const device = typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
const streaming = typeof window !== "undefined" && typeof Audio !== "undefined" && typeof fetch === "function";

// A one-sample silent WAV (turned into a blob: URL when used, because the site's CSP allows media from 'self' and blob: only). Playing it inside the tap unlocks the audio element on iPhone,
// so the voice can start after the network round trip.
const SILENT_WAV = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=";

let silent = null;
function silentUrl() {
  if (!silent) {
    const bin = atob(SILENT_WAV.split(",")[1]);
    silent = URL.createObjectURL(new Blob([Uint8Array.from(bin, (c) => c.charCodeAt(0))], { type: "audio/wav" }));
  }
  return silent;
}

let session = 0;
let current = null; // device utterance, kept so the browser doesn't collect it mid-speech
let player = null; // the one audio element for the voice service
let playerUrl = null;
let controller = null;
let serviceDown = false; // /api/speak isn't set up or failed: go straight to the device voice, inside the tap

export function canSpeak() {
  return streaming || device;
}

// ---------- Device voice (fallback) ----------

// Prefer Australian English, then other English, and on-device voices over network ones.
function pickVoice() {
  const rank = (v) => (/^en[-_]AU/i.test(v.lang) ? 0 : /^en[-_](GB|NZ|IE|ZA)/i.test(v.lang) ? 1 : 2) + (v.localService ? 0 : 10);
  const english = speechSynthesis.getVoices().filter((v) => /^en([-_]|$)/i.test(v.lang));
  return english.sort((a, b) => rank(a) - rank(b))[0] || null;
}

// Short chunks, because some browsers cut off long utterances.
function chunk(text, max = 220) {
  const sentences = String(text).match(/[^.?]+[.?]+["')]*\s*|[^.?]+$/g) || [String(text)];
  const out = [];
  let line = "";
  for (const s of sentences) {
    if (line && (line + s).length > max) { out.push(line.trim()); line = ""; }
    line += s;
  }
  if (line.trim()) out.push(line.trim());
  return out;
}

// Phones only let speech start from a tap. A silent utterance inside the tap unlocks it,
// so the device voice still works after the voice service has been tried.
function prime() {
  try {
    const u = new SpeechSynthesisUtterance(" ");
    u.volume = 0;
    speechSynthesis.speak(u);
  } catch {}
}

function speakOnDevice(items, from, id, { onItem, onEnd }) {
  if (!device) return onEnd(true, true);
  const voice = pickVoice();
  const chunks = [];
  items.forEach((item, i) => { if (i >= from) chunk(item.text).forEach((t) => chunks.push({ t, i })); });
  let n = 0;
  let last = -1;

  const next = () => {
    if (id !== session) return;
    if (n >= chunks.length) { current = null; return onEnd(false, true); }
    const { t, i } = chunks[n++];
    if (i !== last) { last = i; onItem(i); }
    const u = new SpeechSynthesisUtterance(t);
    u.lang = voice ? voice.lang : "en-AU";
    if (voice) u.voice = voice;
    u.rate = 0.95;
    u.onend = next;
    u.onerror = (e) => {
      if (id !== session) return;
      current = null;
      onEnd(e.error !== "canceled" && e.error !== "interrupted", true);
    };
    current = u;
    speechSynthesis.speak(u);
  };
  next();
}

// ---------- Voice service ----------

async function fetchClip(text, signal) {
  const res = await fetch("/api/speak", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ text }),
    signal
  });
  if (!res.ok) throw new Error("speak " + res.status);
  const blob = await res.blob();
  if (!blob.size) throw new Error("empty audio");
  return URL.createObjectURL(blob);
}

function release() {
  if (player) { player.onended = null; player.onerror = null; player.pause(); player.removeAttribute("src"); player.load(); }
  if (playerUrl) { URL.revokeObjectURL(playerUrl); playerUrl = null; }
  player = null;
}

export function stop() {
  session++;
  current = null;
  if (controller) { controller.abort(); controller = null; }
  release();
  if (device) speechSynthesis.cancel();
}

// items: [{ text }]. Hooks: onItem(index) as each item starts, onEnd(failed, usedDevice) when it finishes or breaks.
// Call it straight from the tap so the browser allows the audio to play.
export function speak(items, hooks) {
  const { onItem, onEnd } = hooks;
  stop();
  const id = session;
  if (device) prime(); // unlock the device voice inside the tap, in case we fall back to it later
  if (!streaming || serviceDown) return speakOnDevice(items, 0, id, hooks);

  const audio = new Audio();
  audio.preload = "auto";
  audio.src = silentUrl();
  audio.play().catch(() => {}); // unlocks the element on iPhone; the real clip replaces it
  player = audio;
  controller = new AbortController();
  const { signal } = controller;

  const clips = new Map(); // index -> promise of an object URL
  const clip = (i) => {
    if (!clips.has(i)) clips.set(i, fetchClip(items[i].text, signal));
    return clips.get(i);
  };
  const dropClips = () => { for (const p of clips.values()) p.then((u) => URL.revokeObjectURL(u), () => {}); clips.clear(); };

  const fallBack = (from) => {
    if (id !== session) return;
    serviceDown = true;
    dropClips();
    release();
    speakOnDevice(items, from, id, hooks);
  };

  const play = async (i) => {
    if (id !== session) return dropClips();
    if (i >= items.length) { release(); dropClips(); return onEnd(false, false); }
    let url;
    try {
      url = await clip(i);
    } catch {
      return fallBack(i);
    }
    if (id !== session) return dropClips();
    if (i + 1 < items.length) clip(i + 1).catch(() => {}); // fetch the next part while this one plays
    clips.delete(i);
    if (playerUrl) URL.revokeObjectURL(playerUrl);
    playerUrl = url;
    onItem(i);
    audio.onended = () => play(i + 1);
    audio.onerror = () => fallBack(i);
    audio.src = url;
    try {
      await audio.play();
    } catch {
      fallBack(i);
    }
  };
  play(0);
}
