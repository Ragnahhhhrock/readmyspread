// Reads a finished reading aloud (DESIGN.md section 14).
// Read aloud by the device's own voice (Web Speech API).
// Nothing is recorded or stored by readmyspread.

const device = typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;

let session = 0;
let current = null; // device utterance, kept so the browser doesn't collect it mid-speech

export function canSpeak() {
  return device;
}

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

// Phones only let speech start from a tap. A silent utterance inside the tap unlocks it.
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

export function stop() {
  session++;
  current = null;
  if (device) speechSynthesis.cancel();
}

// items: [{ text }]. Hooks: onItem(index) as each item starts, onEnd(failed, usedDevice) when it finishes or breaks.
// Call it straight from the tap so the browser allows the speech to start.
export function speak(items, hooks) {
  stop();
  const id = session;
  if (device) prime();
  speakOnDevice(items, 0, id, hooks);
}
