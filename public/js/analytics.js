// Google Analytics 4 (G-5FRLHDRXTD), loaded through the first-party gateway at /metrics.
(function () {
  var ID = "G-5FRLHDRXTD";
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", ID, { transport_url: location.origin + "/metrics", first_party_collection: true });
  var s = document.createElement("script");
  s.async = true;
  s.src = "/metrics/gtag/js?id=" + ID;
  document.head.appendChild(s);
})();

// Event helper. Never pass photos, questions or reading text.
window.track = function (name, params) {
  try { window.gtag("event", name, params || {}); } catch (e) {}
};
