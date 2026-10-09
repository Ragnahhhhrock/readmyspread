// Reads a finished reading aloud with the device's own voice (Web Speech API).
// Nothing is recorded, uploaded or stored.

const supported = typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;

let session = 0;
let current = null; // keep a reference so the browser doesn't collect the utterance mid-speech

export function canSpeak() {
  return supported;
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

export function stop() {
  session++;
  current = null;
  if (supported) speechSynthesis.cancel();
}

// items: [{ text }]. Hooks: onItem(index) as each item starts, onEnd(failed) when it finishes or breaks.
export function speak(items, { onItem, onEnd }) {
  if (!supported) return onEnd(true);
  stop();
  const id = session;
  const voice = pickVoice();
  const chunks = [];
  items.forEach((item, i) => chunk(item.text).forEach((t) => chunks.push({ t, i })));
  let n = 0;
  let last = -1;

  const next = () => {
    if (id !== session) return;
    if (n >= chunks.length) { current = null; return onEnd(false); }
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
      onEnd(e.error !== "canceled" && e.error !== "interrupted");
    };
    current = u;
    speechSynthesis.speak(u);
  };
  next();
}
