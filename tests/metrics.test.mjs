import assert from "node:assert/strict";
import { upstreamFor, onRequest } from "../functions/metrics/[[path]].js";

const u = (p) => upstreamFor(new URL("https://readmyspread.com" + p));
assert.equal(u("/metrics/gtag/js?id=G-5FRLHDRXTD").href, "https://www.googletagmanager.com/gtag/js?id=G-5FRLHDRXTD");
assert.equal(u("/metrics/g/collect?v=2&tid=G-5FRLHDRXTD").href, "https://www.google-analytics.com/g/collect?v=2&tid=G-5FRLHDRXTD");
assert.equal(u("/metrics/other"), null);
assert.equal(u("/metrics/gtag/../../api"), null);
assert.equal((await onRequest({ request: new Request("https://readmyspread.com/metrics/g/collect", { method: "DELETE" }) })).status, 405);
assert.equal((await onRequest({ request: new Request("https://readmyspread.com/metrics/nope") })).status, 404);
console.log("metrics ok");
