// POST /api/contact
// Body: JSON or form-encoded { name, email, message, website }. "website" is a hidden spam trap and must stay empty.
// Sends the message to contact@readmyspread.com through Resend and sets reply-to to the sender. Nothing is stored.
// With "Accept: application/json" the reply is JSON; a plain form post is redirected to /contact/sent/.
//
// Environment:
//   RESEND_API_KEY  (secret, required; resend.com API key, with the readmyspread.com domain verified)
//   CONTACT_FROM    (optional, default "readmyspread contact form <contact@readmyspread.com>"; must be on the verified domain)
//   CONTACT_TO      (optional, default contact@readmyspread.com)
//   RATE            (optional KV namespace binding; caps messages per visitor per day)
//   CONTACT_DAILY_PER_VISITOR (optional, default 5)

const ALLOWED_HOSTS = [/^readmyspread\.com$/, /^www\.readmyspread\.com$/, /^([a-z0-9-]+\.)?readmyspread\.pages\.dev$/, /^localhost$/, /^127\.0\.0\.1$/];
const DEFAULT_TO = "contact@readmyspread.com";
const DEFAULT_FROM = "readmyspread contact form <contact@readmyspread.com>";
const LIMITS = { name: 80, email: 120, message: 4000 };
const EMAIL_RE = /^[^\s@<>"',;:]+@[^\s@<>"',;:]+\.[^\s@<>"',;:]{2,}$/;

function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store", ...extra } });
}

export function originAllowed(request) {
  const origin = request.headers.get("origin");
  if (!origin) return false;
  try {
    return ALLOWED_HOSTS.some((re) => re.test(new URL(origin).hostname));
  } catch {
    return false;
  }
}

const clip = (v, n) => (typeof v === "string" ? v.trim().slice(0, n) : "");
// Header-injection guard: names and emails never carry line breaks.
const oneLine = (s) => s.replace(/[\r\n\u2028\u2029]+/g, " ");

export function cleanMessage(input) {
  const name = oneLine(clip(input?.name, LIMITS.name));
  const email = oneLine(clip(input?.email, LIMITS.email));
  const message = clip(input?.message, LIMITS.message).replace(/\r\n/g, "\n");
  const trap = typeof input?.website === "string" && input.website.trim() !== "";
  const errors = {};
  if (!name) errors.name = "Add your name.";
  if (!EMAIL_RE.test(email)) errors.email = "Add an email address we can reply to.";
  if (message.length < 10) errors.message = "Write a message of at least a few words.";
  return { name, email, message, trap, errors };
}

const escapeHtml = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function buildEmail({ name, email, message }, env = {}) {
  return {
    from: env.CONTACT_FROM || DEFAULT_FROM,
    to: [env.CONTACT_TO || DEFAULT_TO],
    reply_to: email,
    subject: `readmyspread contact form: ${name}`.slice(0, 120),
    text: `From: ${name} <${email}>\n\n${message}\n\n(Sent from the readmyspread.com contact form)`,
    html: `<p><strong>From:</strong> ${escapeHtml(name)} &lt;${escapeHtml(email)}&gt;</p><p style="white-space:pre-wrap">${escapeHtml(message)}</p><p>Sent from the readmyspread.com contact form.</p>`
  };
}

async function overLimit(request, env) {
  if (!env.RATE) return false;
  const ip = request.headers.get("cf-connecting-ip") || "unknown";
  const day = new Date().toISOString().slice(0, 10);
  const key = `contact:${day}:${ip}`;
  const cap = Number(env.CONTACT_DAILY_PER_VISITOR) || 5;
  const used = Number(await env.RATE.get(key)) || 0;
  if (used >= cap) return true;
  await env.RATE.put(key, String(used + 1), { expirationTtl: 90000 });
  return false;
}

async function readBody(request) {
  const type = request.headers.get("content-type") || "";
  if (type.includes("application/json")) return await request.json();
  if (type.includes("application/x-www-form-urlencoded") || type.includes("multipart/form-data")) {
    return Object.fromEntries((await request.formData()).entries());
  }
  throw new Error("unsupported");
}

export async function onRequestPost({ request, env }) {
  const wantsJson = (request.headers.get("accept") || "").includes("application/json");
  const done = () => (wantsJson ? json({ ok: true }) : new Response(null, { status: 303, headers: { location: "/contact/sent/" } }));
  const fail = (error, status, extra = {}) =>
    wantsJson
      ? json({ error, ...extra }, status)
      : new Response(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Message not sent</title><body style="font:1.125rem/1.5 system-ui;background:#0b1024;color:#f3efe4;padding:1.5rem"><p>Sorry, your message wasn't sent. Please email <a style="color:#b4a8ff" href="mailto:${DEFAULT_TO}">${DEFAULT_TO}</a> or <a style="color:#b4a8ff" href="/contact/">go back and try again</a>.</p>`, { status, headers: { "content-type": "text/html; charset=utf-8" } });

  if (!originAllowed(request)) return fail("forbidden", 403);

  let input;
  try {
    input = await readBody(request);
  } catch {
    return fail("bad_request", 400);
  }

  const msg = cleanMessage(input);
  // Bots fill the hidden field. Pretend it worked and send nothing.
  if (msg.trap) return done();
  if (Object.keys(msg.errors).length) return fail("invalid", 400, { fields: msg.errors });

  if (!env.RESEND_API_KEY) return fail("not_configured", 503);
  if (await overLimit(request, env)) return fail("rate_limited", 429);

  let upstream;
  try {
    upstream = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { "content-type": "application/json", authorization: `Bearer ${env.RESEND_API_KEY}` },
      body: JSON.stringify(buildEmail(msg, env))
    });
  } catch {
    return fail("upstream_unreachable", 502);
  }
  if (!upstream.ok) {
    console.error("resend error", upstream.status);
    return fail("upstream_error", 502);
  }
  return done();
}

export function onRequest() {
  return json({ error: "method_not_allowed" }, 405, { allow: "POST" });
}
