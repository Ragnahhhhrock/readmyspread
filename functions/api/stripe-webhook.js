// POST /api/stripe-webhook
// Stripe sends checkout.session.completed here when a tip is paid. We forward it to
// Google Analytics 4 as a `donation` event with its value, using the Measurement Protocol.
// Nothing is stored and no personal details are forwarded.
//
// Environment (secrets):
//   STRIPE_WEBHOOK_SECRET  signing secret (whsec_...) of the Stripe webhook endpoint
//   GA_API_SECRET          GA4 Measurement Protocol API secret (Admin, Data streams, Measurement Protocol)

const GA_MEASUREMENT_ID = "G-5FRLHDRXTD";
const TOLERANCE_SECONDS = 300;

const hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");

function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export async function verifySignature(body, header, secret, now = Date.now()) {
  if (!header || !secret) return false;
  const parts = Object.fromEntries(header.split(",").map((p) => p.trim().split("=")));
  const t = Number(parts.t);
  if (!t || Math.abs(now / 1000 - t) > TOLERANCE_SECONDS) return false;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const expected = hex(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${t}.${body}`)));
  return header.split(",").some((p) => p.trim().startsWith("v1=") && safeEqual(p.trim().slice(3), expected));
}

export function donationEvent(event) {
  if (!event || event.type !== "checkout.session.completed") return null;
  const s = event.data && event.data.object;
  if (!s || s.payment_status !== "paid" || !Number.isFinite(s.amount_total)) return null;
  return {
    client_id: `stripe.${String(s.id).slice(-24)}`,
    events: [{
      name: "donation",
      params: {
        value: Math.round(s.amount_total) / 100,
        currency: String(s.currency || "aud").toUpperCase(),
        transaction_id: String(s.id),
        engagement_time_msec: 1,
      },
    }],
  };
}

export async function onRequestPost({ request, env }) {
  if (!env.STRIPE_WEBHOOK_SECRET || !env.GA_API_SECRET) return new Response("Not configured", { status: 503 });
  const body = await request.text();
  if (!(await verifySignature(body, request.headers.get("stripe-signature"), env.STRIPE_WEBHOOK_SECRET))) {
    return new Response("Bad signature", { status: 400 });
  }
  let event;
  try { event = JSON.parse(body); } catch { return new Response("Bad payload", { status: 400 }); }
  const payload = donationEvent(event);
  if (!payload) return new Response("Ignored", { status: 200 });

  const url = `https://www.google-analytics.com/mp/collect?measurement_id=${GA_MEASUREMENT_ID}&api_secret=${encodeURIComponent(env.GA_API_SECRET)}`;
  const res = await fetch(url, { method: "POST", body: JSON.stringify(payload) });
  // A non-2xx makes Stripe retry later.
  return new Response(res.ok ? "ok" : "Upstream error", { status: res.ok ? 200 : 502 });
}

export const onRequest = () => new Response("Method not allowed", { status: 405, headers: { allow: "POST" } });
