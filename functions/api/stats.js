// GET /api/stats
// Running totals for the homepage social proof strip (DESIGN.md section 17):
//   readings   finished tarot readings shown (status ok, not the care screen)
//   questions  of those, readings given with one of the set questions
//   cards      cards identified across those readings
// Only the three numbers are kept. Never a photo, question, reading or visitor detail.
//
// Environment:
//   STATS  KV namespace binding (falls back to RATE if only that is bound)

const KEY = "stats:totals";

const store = (env) => env.STATS || env.RATE || null;

const json = (body, status = 200, cache = "no-store") =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": cache, "x-content-type-options": "nosniff" }
  });

const n = (v) => (Number.isFinite(Number(v)) && Number(v) > 0 ? Math.floor(Number(v)) : 0);

export async function readTotals(env) {
  const kv = store(env);
  if (!kv) return null;
  let raw = null;
  try {
    raw = await kv.get(KEY, { type: "json", cacheTtl: 30 });
  } catch {
    raw = null;
  }
  return { readings: n(raw?.readings), questions: n(raw?.questions), cards: n(raw?.cards) };
}

// Called by /api/read after a finished reading. KV has no atomic increment, so two readings
// finishing in the same instant can lose one count; fine for a running total.
export async function recordReading(env, { asked, cardCount }) {
  const kv = store(env);
  if (!kv) return;
  try {
    const raw = await kv.get(KEY, { type: "json" });
    const next = {
      readings: n(raw?.readings) + 1,
      questions: n(raw?.questions) + (asked ? 1 : 0),
      cards: n(raw?.cards) + n(cardCount),
      updated: new Date().toISOString()
    };
    await kv.put(KEY, JSON.stringify(next));
  } catch (e) {
    console.error("stats write failed", String(e));
  }
}

export async function onRequestGet({ env }) {
  const totals = await readTotals(env);
  if (!totals) return json({ error: "not_configured" }, 503);
  return json(totals, 200, "public, max-age=30");
}

export function onRequest() {
  return new Response(JSON.stringify({ error: "method_not_allowed" }), {
    status: 405,
    headers: { "content-type": "application/json; charset=utf-8", allow: "GET" }
  });
}
