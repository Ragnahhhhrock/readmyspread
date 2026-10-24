import assert from "node:assert/strict";
import { onRequestPost, onRequest, DEFAULT_VOICE_ID } from "../functions/api/speak.js";

const mk = (body, origin = "https://readmyspread.com") =>
  new Request("https://readmyspread.com/api/speak", { method: "POST", headers: { "content-type": "application/json", ...(origin ? { origin } : {}) }, body: typeof body === "string" ? body : JSON.stringify(body) });
const kv = () => {
  const m = new Map();
  return { m, async get(k) { return m.has(k) ? m.get(k) : null; }, async put(k, v) { m.set(k, v); } };
};
const env = { ELEVENLABS_API_KEY: "test-key" };

assert.equal(onRequest().status, 405);

// not configured, foreign origin, bad input
assert.equal((await onRequestPost({ request: mk({ text: "Hello." }), env: {} })).status, 503);
assert.equal((await onRequestPost({ request: mk({ text: "Hello." }, "https://evil.example"), env })).status, 403);
assert.equal((await onRequestPost({ request: mk("not json"), env })).status, 400);
assert.equal((await onRequestPost({ request: mk({ text: "" }), env })).status, 400);
assert.equal((await onRequestPost({ request: mk({ text: "x".repeat(1201) }), env })).status, 400);
assert.equal((await onRequestPost({ request: mk({ text: 42 }), env })).status, 400);

// success: calls ElevenLabs with the key in a header, the default female voice, and returns audio
let seen;
globalThis.fetch = async (url, init) => { seen = { url, init }; return new Response(new Uint8Array([1, 2, 3]), { status: 200 }); };
let r = await onRequestPost({ request: mk({ text: "Five of Cups, Past. Attention has been on what was spilled." }), env });
assert.equal(r.status, 200);
assert.equal(r.headers.get("content-type"), "audio/mpeg");
assert.equal(r.headers.get("cache-control"), "no-store");
assert.equal([...new Uint8Array(await r.arrayBuffer())].join(), "1,2,3");
assert.ok(seen.url.startsWith(`https://api.elevenlabs.io/v1/text-to-speech/${DEFAULT_VOICE_ID}?`));
assert.equal(seen.init.headers["xi-api-key"], "test-key");
const sent = JSON.parse(seen.init.body);
assert.equal(sent.text, "Five of Cups, Past. Attention has been on what was spilled.");
assert.equal(sent.model_id, "eleven_flash_v2_5");
assert.ok(!r.headers.get("x-api-key") && !JSON.stringify([...r.headers]).includes("test-key"), "key must never reach the browser");

// voice and model are overridable
await onRequestPost({ request: mk({ text: "Hi." }), env: { ...env, ELEVENLABS_VOICE_ID: "abc123", ELEVENLABS_MODEL: "eleven_turbo_v2_5" } });
assert.ok(seen.url.includes("/text-to-speech/abc123?"));
assert.equal(JSON.parse(seen.init.body).model_id, "eleven_turbo_v2_5");

// upstream problems map to safe errors
globalThis.fetch = async () => new Response("{}", { status: 401 });
r = await onRequestPost({ request: mk({ text: "Hi." }), env });
assert.equal(r.status, 502);
assert.deepEqual(await r.json(), { error: "upstream_error", upstream_status: 401 });
globalThis.fetch = async () => new Response("{}", { status: 429 });
assert.equal((await onRequestPost({ request: mk({ text: "Hi." }), env })).status, 503);
globalThis.fetch = async () => { throw new Error("down"); };
assert.equal((await onRequestPost({ request: mk({ text: "Hi." }), env })).status, 502);

// daily cap per visitor with a RATE binding
globalThis.fetch = async () => new Response(new Uint8Array([1]), { status: 200 });
const RATE = kv();
const capped = { ...env, RATE, DAILY_AUDIO_PER_VISITOR: "2" };
assert.equal((await onRequestPost({ request: mk({ text: "One." }), env: capped })).status, 200);
assert.equal((await onRequestPost({ request: mk({ text: "Two." }), env: capped })).status, 200);
assert.equal((await onRequestPost({ request: mk({ text: "Three." }), env: capped })).status, 429);
assert.ok([...RATE.m.keys()].every((k) => !k.includes("unknown") || k.startsWith("ag:")), "visitor key is hashed");

console.log("speak tests passed");
