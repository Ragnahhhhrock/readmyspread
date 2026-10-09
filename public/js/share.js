// Share bar (see DESIGN.md section 12). Threads and Facebook are plain links and need nothing from here.
// Instagram has no web share link: use the device share sheet when there is one, otherwise copy the link.
// Shares only the page address and a line of copy. Never a photo, question or reading.
(function () {
  function track(method) {
    if (window.track) window.track("share", { method: method, content_type: "page", item_id: location.pathname });
  }

  function note(bar, message) {
    var el = bar.querySelector(".sharebar__note");
    if (!el) return;
    el.textContent = message;
    el.hidden = false;
  }

  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    return Promise.reject(new Error("no clipboard"));
  }

  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("[data-share]");
    if (!a) return;
    var method = a.getAttribute("data-share");
    track(method);
    if (method !== "instagram") return;

    var bar = a.closest(".sharebar");
    if (!bar) return;
    ev.preventDefault();
    var url = bar.getAttribute("data-share-url") || location.href;
    var text = bar.getAttribute("data-share-text") || document.title;

    if (navigator.share) {
      navigator.share({ title: document.title, text: text, url: url }).catch(function (err) {
        if (err && err.name === "AbortError") return; // closed the sheet
        note(bar, "Couldn't open sharing. Copy this link: " + url);
      });
      return;
    }
    copy(url).then(
      function () { note(bar, "Link copied. Paste it into Instagram."); },
      function () { note(bar, "Copy this link and paste it into Instagram: " + url); }
    );
  });
})();
