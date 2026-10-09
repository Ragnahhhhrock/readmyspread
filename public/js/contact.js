// Contact form: posts to /api/contact and shows the result in place. Without JavaScript the form posts normally.
(function () {
  var form = document.getElementById("contact-form");
  if (!form) return;
  var status = document.getElementById("form-status");
  var btn = document.getElementById("contact-send");
  var MAIL = "contact@readmyspread.com";

  function show(title, text, isError) {
    status.className = "status" + (isError ? " status--error" : "");
    status.replaceChildren();
    var s = document.createElement("strong");
    s.textContent = title;
    var p = document.createElement("p");
    p.textContent = text;
    status.append(s, p);
    status.hidden = false;
    status.focus();
    status.scrollIntoView({ block: "center" });
  }
  function fieldError(name, text) {
    var input = document.getElementById("c-" + name);
    var err = document.getElementById("c-" + name + "-err");
    if (!input || !err) return;
    err.textContent = text || "";
    err.hidden = !text;
    if (text) { input.setAttribute("aria-invalid", "true"); input.setAttribute("aria-describedby", err.id); }
    else { input.removeAttribute("aria-invalid"); }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    ["name", "email", "message"].forEach(function (n) { fieldError(n, ""); });
    status.hidden = true;
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    btn.disabled = true;
    btn.textContent = "Sending";
    fetch("/api/contact", { method: "POST", headers: { "content-type": "application/json", accept: "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, status: r.status, body: j }; }); })
      .then(function (res) {
        if (res.ok) {
          if (window.track) window.track("contact_sent");
          window.location.assign("/contact/sent/");
          return;
        }
        if (res.body.error === "invalid" && res.body.fields) {
          Object.keys(res.body.fields).forEach(function (k) { fieldError(k, res.body.fields[k]); });
          var first = form.querySelector("[aria-invalid='true']");
          if (first) first.focus();
          return;
        }
        var msg = res.body.error === "rate_limited" ? "You have sent a few messages today. Please try again tomorrow, or email " + MAIL + "."
          : "Your message was not sent. Please try again, or email " + MAIL + ".";
        show("Message not sent", msg, true);
      })
      .catch(function () { show("Message not sent", "Check your connection and try again, or email " + MAIL + ".", true); })
      .then(function () { btn.disabled = false; btn.textContent = "Send message"; });
  });
})();
