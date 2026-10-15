// Homepage social proof strip (DESIGN.md section 17). Fetches the running totals from /api/stats,
// shows the strip once there is at least one reading, and refreshes every minute while the page is
// visible, so the numbers follow new readings. Without JavaScript or totals, the strip stays hidden.
// On first load the band fades in and the numbers count up from zero, starting when the band
// scrolls into view; later changes count up from the old number. No motion under reduced motion.
(function () {
  var strip = document.querySelector(".stats");
  if (!strip) return;
  var fields = ["readings", "questions", "cards"];
  var shown = { readings: 0, questions: 0, cards: 0 };
  var runs = {};
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fmt = new Intl.NumberFormat("en-AU");
  var compact = new Intl.NumberFormat("en-AU", { notation: "compact", maximumFractionDigits: 1 });
  var REFRESH = 60000;
  var INTRO = 1400, INTRO_STAGGER = 150, UPDATE = 900;
  var timer = null;
  var introDone = false;

  function text(v) { return v >= 1000000 ? compact.format(v) : fmt.format(v); }
  function el(key) { return strip.querySelector('[data-stat="' + key + '"]'); }

  // Counts the number shown in `node` from `from` to `to`, easing out. A newer count on the same
  // number cancels the older one, so a refresh mid-count never fights it.
  function count(key, from, to, dur, delay) {
    var node = el(key);
    if (!node) return;
    var id = (runs[key] || 0) + 1;
    runs[key] = id;
    if (reduce || from === to) { node.textContent = text(to); return; }
    node.textContent = text(from);
    node.classList.add("is-updating");
    var start = null;
    function step(t) {
      if (runs[key] !== id) return;
      if (start === null) start = t + delay;
      var p = Math.max(0, Math.min(1, (t - start) / dur));
      var e = 1 - Math.pow(1 - p, 3);
      node.textContent = text(Math.round(from + (to - from) * e));
      if (p < 1) requestAnimationFrame(step);
      else node.classList.remove("is-updating");
    }
    requestAnimationFrame(step);
  }

  function intro() {
    if (introDone) return;
    introDone = true;
    strip.classList.add("is-in");
    fields.forEach(function (k, i) { count(k, 0, shown[k], INTRO, i * INTRO_STAGGER); });
  }

  // First totals: show the band at zero and wait until it is on screen before counting up.
  function reveal() {
    strip.hidden = false;
    if (reduce || !("IntersectionObserver" in window)) {
      strip.classList.add("is-in");
      introDone = true;
      fields.forEach(function (k) { count(k, 0, shown[k], 0, 0); });
      return;
    }
    fields.forEach(function (k) { var n = el(k); if (n) n.textContent = text(0); });
    var io = new IntersectionObserver(function (entries) {
      if (entries.some(function (en) { return en.isIntersecting; })) { io.disconnect(); intro(); }
    }, { threshold: 0.4 });
    io.observe(strip);
  }

  function load() {
    fetch("/api/stats", { headers: { accept: "application/json" } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d || !(d.readings > 0)) return;
        var first = strip.hidden;
        fields.forEach(function (k) {
          var to = Math.max(0, Math.floor(Number(d[k]) || 0));
          var from = shown[k];
          shown[k] = to;
          if (!first && introDone) count(k, from, to, UPDATE, 0);
        });
        if (first) reveal();
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
