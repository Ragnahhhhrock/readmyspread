import assert from "node:assert/strict";
import { onRequestGet, onRequest, recordReading } from "../functions/api/stats.js";
import { onRequestPost } from "../functions/api/read.js";

const kv = () => {
  const m = new Map();
  return { m, async get(k, o) { const v = m.get(k); return v == null ? null : o?.type === "json" ? JSON.parse(v) : v; }, async put(k, v) { m.set(k, v); } };
};

// no binding: not configured, so the homepage strip stays hidden
assert.equal((await onRequestGet({ env: {} })).status, 503);
assert.equal(onRequest().status, 405);

// empty store reads as zeros
const STATS = kv();
let r = await onRequestGet({ env: { STATS } });
assert.equal(r.status, 200);
assert.deepEqual(await r.json(), { readings: 0, questions: 0, cards: 0 });

// counts add up and carry no content
await recordReading({ STATS }, { asked: true, cardCount: 3 });
await recordReading({ STATS }, { asked: false, cardCount: 10 });
r = await onRequestGet({ env: { STATS } });
assert.deepEqual(await r.json(), { readings: 2, questions: 1, cards: 13 });
assert.deepEqual(Object.keys(JSON.parse(STATS.m.get("stats:totals"))).sort(), ["cards", "questions", "readings", "updated"]);

// falls back to RATE
const RATE = kv();
await recordReading({ RATE }, { asked: false, cardCount: 1 });
assert.deepEqual(await (await onRequestGet({ env: { RATE } })).json(), { readings: 1, questions: 0, cards: 1 });

// /api/read counts ok readings only, not care or unreadable
const b64 = "A".repeat(400);
const mk = (q) => new Request("https://readmyspread.com/api/read", { method: "POST", headers: { "content-type": "application/json", origin: "https://readmyspread.com" }, body: JSON.stringify({ image: b64, mediaType: "image/jpeg", question: q }) });
const reply = (input) => { globalThis.fetch = async () => new Response(JSON.stringify({ content: [{ type: "tool_use", name: "deliver_reading", input }] }), { status: 200 }); };
const S = kv();
const env = { ANTHROPIC_API_KEY: "t", STATS: S };
const pending = [];
const waitUntil = (p) => pending.push(p);
reply({ status: "ok", spread: { name: "Three-card spread", card_count: 3 }, cards: [{ name: "The Star", short: "XVII", position: "Past", orientation: "upright" }, { name: "The Moon", short: "XVIII", position: "Present", orientation: "upright" }, { name: "The Sun", short: "XIX", position: "Future", orientation: "reversed" }], verdict: "v", sections: [] });
assert.equal((await onRequestPost({ request: mk("What should I focus on?"), env, waitUntil })).status, 200);
await Promise.all(pending);
reply({ status: "unreadable", verdict: "Too dark." });
await onRequestPost({ request: mk(""), env, waitUntil });
reply({ status: "ok", needs_care: true, verdict: "Please reach out." });
await onRequestPost({ request: mk(""), env, waitUntil });
await Promise.all(pending);
assert.deepEqual(await (await onRequestGet({ env: { STATS: S } })).json(), { readings: 1, questions: 1, cards: 3 });

console.log("stats tests passed");
