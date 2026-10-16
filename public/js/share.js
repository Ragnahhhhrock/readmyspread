// Share bar (see DESIGN.md section 12). Threads is a plain link and needs nothing from here.
// Facebook and Instagram: on phones their web links only open the app and lose the page address, so when the
// device share sheet exists we open it with the page title, one line of copy and the address.
// Without a share sheet (computers) they stay plain new-tab links; Instagram also copies the address to paste.
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

  function copyForInstagram(bar, url) {
    copy(url).then(
      function () { note(bar, "Link copied. Paste it into Instagram."); },
      function () { note(bar, "Copy this link and paste it into Instagram: " + url); }
    );
  }

  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("[data-share]");
    if (!a) return;
    var method = a.getAttribute("data-share");
    track(method);
    if (method !== "instagram" && method !== "facebook") return;

    var bar = a.closest(".sharebar");
    if (!bar) return;
    var url = bar.getAttribute("data-share-url") || location.href;
    var text = bar.getAttribute("data-share-text") || document.title;

    if (navigator.share) {
      // Phones and tablets: the share sheet carries the link into the chosen app.
      ev.preventDefault();
      navigator.share({ title: document.title, text: text, url: url }).catch(function (err) {
        if (err && err.name === "AbortError") return; // the person closed the sheet
        // The sheet failed to open: fall back to the plain link path.
        if (method === "instagram") copyForInstagram(bar, url);
        window.open(a.href, "_blank", "noopener,noreferrer");
      });
      return;
    }

    // No share sheet: the link opens in a new tab as normal. Instagram also copies the address.
    if (method === "instagram") copyForInstagram(bar, url);
  });
})();
