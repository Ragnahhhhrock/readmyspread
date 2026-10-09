import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { verifySignature, donationEvent, onRequestPost } from "../functions/api/stripe-webhook.js";

const secret = "whsec_test";
const now = Date.now();
const t = Math.floor(now / 1000);
const sign = (body, ts = t) => `t=${ts},v1=${createHmac("sha256", secret).update(`${ts}.${body}`).digest("hex")}`;
const body = JSON.stringify({ type: "checkout.session.completed", data: { object: { id: "cs_live_abcdefghijklmnopqrstuvwxyz", payment_status: "paid", amount_total: 1250, currency: "aud" } } });

assert.equal(await verifySignature(body, sign(body), secret, now), true);
assert.equal(await verifySignature(body + " ", sign(body), secret, now), false);
assert.equal(await verifySignature(body, sign(body, t - 4000), secret, now), false);
assert.equal(await verifySignature(body, null, secret, now), false);

const p = donationEvent(JSON.parse(body));
assert.equal(p.events[0].name, "donation");
assert.equal(p.events[0].params.value, 12.5);
assert.equal(p.events[0].params.currency, "AUD");
assert.equal(donationEvent({ type: "charge.succeeded" }), null);
assert.equal(donationEvent({ type: "checkout.session.completed", data: { object: { payment_status: "unpaid", amount_total: 500 } } }), null);

const req = (b, sig) => new Request("https://readmyspread.com/api/stripe-webhook", { method: "POST", headers: { "stripe-signature": sig }, body: b });
assert.equal((await onRequestPost({ request: req(body, sign(body)), env: {} })).status, 503);
assert.equal((await onRequestPost({ request: req(body, "t=1,v1=bad"), env: { STRIPE_WEBHOOK_SECRET: secret, GA_API_SECRET: "x" } })).status, 400);
console.log("stripe-webhook ok");
