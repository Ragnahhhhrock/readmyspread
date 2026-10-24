// POST /api/speak
// Body: { text: string }  (one card section, the verdict or the closing line of a reading)
// Returns audio/mpeg: the text read aloud by an ElevenLabs voice (DESIGN.md section 14).
// The ElevenLabs key stays on the server. Nothing is stored: not the text, not the audio.
//
// Environment:
//   ELEVENLABS_API_KEY     (secret, required)
//   ELEVENLABS_VOICE_ID    (optional, default Lily, a warm female British voice)
//   ELEVENLABS_MODEL       (optional, default eleven_flash_v2_5)
//   RATE                   (optional KV namespace binding; enables per-visitor and daily caps)
//   DAILY_AUDIO_PER_VISITOR (optional, default 40 requests; a reading uses about 5)
//   DAILY_AUDIO_GLOBAL      (optional, default 1500 requests)

export const DEFAULT_VOICE_ID = "pFZP5JQG7iQjIQuC4Bku"; // Lily: warm, female, British
const DEFAULT_MODEL = "eleven_flash_v2_5";
const OUTPUT_FORMAT = "mp3_44100_64"; // small for phones, clear for speech
const MAX_TEXT = 1200;
const ALLOWED_HOSTS = [/^readmyspread\.com$/, /^www\.readmyspread\.com$/, /^([a-z0-9-]+\.)?readmyspread\.pages\.dev$/, /^localhost$/, /^127\.0\.0\.1$/];

const json = (body, status = 200, extra = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff", ...extra }
  });

function originAllowed(request) {
  const origin = request.headers.get("origin");
  if (!origin) return true; // same-origin fetches from some browsers omit it
  try {
    return ALLOWED_HOSTS.some((re) => re.test(new URL(origin).hostname));
  } catch {
    return false;
  }
}

async function sha(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].slice(0, 12).map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Optional caps. Without a KV binding this is skipped (add a Cloudflare rate-limiting rule instead).
async function overLimit(request, env) {
  if (!env.RATE) return false;
  const day = new Date().toISOString().slice(0, 10);
  const ip = request.headers.get("cf-connecting-ip") || "unknown";
  const perVisitor = Number(env.DAILY_AUDIO_PER_VISITOR || 40);
  const perDay = Number(env.DAILY_AUDIO_GLOBAL || 1500);
  const vKey = `av:${day}:${await sha(ip)}`;
  const gKey = `ag:${day}`;
  const [v, g] = await Promise.all([env.RATE.get(vKey), env.RATE.get(gKey)]);
  if (Number(v || 0) >= perVisitor || Number(g || 0) >= perDay) return true;
  const ttl = { expirationTtl: 60 * 60 * 36 };
  await Promise.all([env.RATE.put(vKey, String(Number(v || 0) + 1), ttl), env.RATE.put(gKey, String(Number(g || 0) + 1), ttl)]);
  return false;
}

export async function onRequestPost({ request, env }) {
  if (!originAllowed(request)) return json({ error: "forbidden" }, 403);
  const apiKey = env.ELEVENLABS_API_KEY;
  if (!apiKey) return json({ error: "not_configured" }, 503);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "bad_request" }, 400);
  }
  const text = typeof body?.text === "string" ? body.text.trim() : "";
  if (!text || text.length > MAX_TEXT) return json({ error: "bad_text" }, 400);

  if (await overLimit(request, env)) return json({ error: "rate_limited" }, 429);

  const voice = encodeURIComponent(env.ELEVENLABS_VOICE_ID || DEFAULT_VOICE_ID);
  let upstream;
  try {
    upstream = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice}?output_format=${OUTPUT_FORMAT}`, {
      method: "POST",
      headers: { "content-type": "application/json", accept: "audio/mpeg", "xi-api-key": apiKey },
      body: JSON.stringify({
        text,
        model_id: env.ELEVENLABS_MODEL || DEFAULT_MODEL,
        // Steady and plain: no added style, a touch slower than conversation.
        voice_settings: { stability: 0.6, similarity_boost: 0.75, style: 0, use_speaker_boost: true, speed: 0.95 }
      })
    });
  } catch {
    return json({ error: "upstream_unreachable" }, 502);
  }

  if (!upstream.ok) {
    // Pass back the upstream status (never the key) so setup problems are diagnosable.
    console.error("elevenlabs error", upstream.status);
    const busy = upstream.status === 429;
    return json({ error: busy ? "busy" : "upstream_error", upstream_status: upstream.status }, busy ? 503 : 502);
  }

  return new Response(upstream.body, {
    status: 200,
    headers: { "content-type": "audio/mpeg", "cache-control": "no-store", "x-content-type-options": "nosniff" }
  });
}

export function onRequest() {
  return json({ error: "method_not_allowed" }, 405, { allow: "POST" });
}
