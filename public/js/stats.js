// Homepage social proof strip (DESIGN.md section 17). Fetches the running totals from /api/stats,
// shows the strip once there is at least one reading, and refreshes every minute while the page is
// visible, so the numbers follow new readings. Without JavaScript or totals, the strip stays hidden.
(function () {
  var strip = document.querySelector(".stats");
  if (!strip) return;
  var fields = ["readings", "questions", "cards"];
  var shown = { readings: 0, questions: 0, cards: 0 };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fmt = new Intl.NumberFormat("en-AU");
  var compact = new Intl.NumberFormat("en-AU", { notation: "compact", maximumFractionDigits: 1 });
  var REFRESH = 60000;
  var timer = null;

  function text(v) { return v >= 1000000 ? compact.format(v) : fmt.format(v); }

  function set(key, to) {
    var el = strip.querySelector('[data-stat="' + key + '"]');
    if (!el) return;
    var from = shown[key];
    shown[key] = to;
    if (reduce || from === to || from === 0 && strip.hidden) { el.textContent = text(to); return; }
    var start = null, dur = 900;
    el.classList.add("is-updating");
    function step(t) {
      if (start === null) start = t;
      var p = Math.min(1, (t - start) / dur);
      var e = 1 - Math.pow(1 - p, 3);
      el.textContent = text(Math.round(from + (to - from) * e));
      if (p < 1) requestAnimationFrame(step);
      else el.classList.remove("is-updating");
    }
    requestAnimationFrame(step);
  }

  function load() {
    fetch("/api/stats", { headers: { accept: "application/json" } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d || !(d.readings > 0)) return;
        fields.forEach(function (k) { set(k, Math.max(0, Math.floor(Number(d[k]) || 0))); });
        strip.hidden = false;
      })
      .catch(function () {});
  }

  function schedule() {
    clearInterval(timer);
    timer = document.hidden ? null : setInterval(load, REFRESH);
  }

  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) load();
    schedule();
  });
  window.addEventListener("pageshow", function (e) { if (e.persisted) load(); });

  load();
  schedule();
})();
