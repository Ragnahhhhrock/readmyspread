import assert from "node:assert/strict";
import { cleanMessage, buildEmail, originAllowed, onRequestPost } from "../functions/api/contact.js";

const good = { name: "Sam", email: "sam@example.com", message: "Hello, I have a question about a card." };
assert.deepEqual(cleanMessage(good).errors, {});
assert.ok(cleanMessage({ ...good, email: "nope" }).errors.email);
assert.ok(cleanMessage({ ...good, name: " " }).errors.name);
assert.ok(cleanMessage({ ...good, message: "hi" }).errors.message);
assert.equal(cleanMessage({ ...good, website: "http://spam" }).trap, true);
assert.equal(cleanMessage({ ...good, name: "Sam\r\nBcc: x@y.z" }).name.includes("\n"), false);
assert.equal(cleanMessage({ ...good, message: "x".repeat(9000) }).message.length, 4000);

const mail = buildEmail({ name: "<b>Sam</b>", email: "sam@example.com", message: "<script>1</script> hello there" });
assert.equal(mail.to[0], "contact@readmyspread.com");
assert.equal(mail.reply_to, "sam@example.com");
assert.ok(!mail.html.includes("<script>") && !mail.html.includes("<b>"));

const post = (body, headers = {}) => new Request("https://readmyspread.com/api/contact", { method: "POST", headers: { origin: "https://readmyspread.com", "content-type": "application/json", accept: "application/json", ...headers }, body: JSON.stringify(body) });
assert.equal(originAllowed(post(good)), true);
assert.equal(originAllowed(post(good, { origin: "https://evil.example" })), false);
assert.equal((await onRequestPost({ request: post(good, { origin: "https://evil.example" }), env: {} })).status, 403);
assert.equal((await onRequestPost({ request: post({ ...good, email: "bad" }), env: { RESEND_API_KEY: "k" } })).status, 400);
assert.equal((await onRequestPost({ request: post(good), env: {} })).status, 503);
assert.equal((await onRequestPost({ request: post({ ...good, website: "x" }), env: {} })).status, 200); // trap: silent success, nothing sent

let sent;
globalThis.fetch = async (url, init) => { sent = { url, init }; return new Response("{}", { status: 200 }); };
const ok = await onRequestPost({ request: post(good), env: { RESEND_API_KEY: "k" } });
assert.equal(ok.status, 200);
assert.equal(sent.url, "https://api.resend.com/emails");
assert.equal(JSON.parse(sent.init.body).to[0], "contact@readmyspread.com");

const form = new Request("https://readmyspread.com/api/contact", { method: "POST", headers: { origin: "https://readmyspread.com", "content-type": "application/x-www-form-urlencoded" }, body: new URLSearchParams(good) });
const redirect = await onRequestPost({ request: form, env: { RESEND_API_KEY: "k" } });
assert.equal(redirect.status, 303);
assert.equal(redirect.headers.get("location"), "/contact/sent/");
console.log("contact ok");
