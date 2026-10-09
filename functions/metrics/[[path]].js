// First-party Google tag gateway. Serves gtag.js and forwards Google Analytics
// hits from readmyspread.com/metrics/*, so the tag loads from our own domain.
//
//   /metrics/gtag/js?id=G-...   ->  https://www.googletagmanager.com/gtag/js
//   /metrics/g/collect          ->  https://www.google-analytics.com/g/collect
//
// Only the paths below are forwarded. Nothing is stored here.

const ROUTES = [
  { prefix: "/metrics/gtag/", upstream: "https://www.googletagmanager.com/gtag/" },
  { prefix: "/metrics/g/", upstream: "https://www.google-analytics.com/g/" },
  { prefix: "/metrics/j/", upstream: "https://www.google-analytics.com/j/" },
];

const DROP_REQUEST = ["host", "cookie", "cf-connecting-ip", "x-forwarded-for", "x-real-ip"];

export function upstreamFor(url) {
  const route = ROUTES.find((r) => url.pathname.startsWith(r.prefix));
  if (!route) return null;
  const target = new URL(route.upstream + url.pathname.slice(route.prefix.length));
  target.search = url.search;
  return target;
}

export async function onRequest({ request }) {
  if (request.method !== "GET" && request.method !== "POST") {
    return new Response("Method not allowed", { status: 405, headers: { allow: "GET, POST" } });
  }
  const target = upstreamFor(new URL(request.url));
  if (!target) return new Response("Not found", { status: 404 });

  const headers = new Headers(request.headers);
  for (const h of DROP_REQUEST) headers.delete(h);
  const ip = request.headers.get("cf-connecting-ip");
  if (ip) headers.set("x-forwarded-for", ip);

  const upstream = await fetch(target, {
    method: request.method,
    headers,
    body: request.method === "POST" ? request.body : undefined,
    redirect: "manual",
  });

  const out = new Headers(upstream.headers);
  out.delete("set-cookie");
  out.set("x-content-type-options", "nosniff");
  return new Response(upstream.body, { status: upstream.status, headers: out });
}
