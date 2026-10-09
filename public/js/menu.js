// Header menu: toggles the panel on small screens. Without JavaScript the footer carries the same links.
(function () {
  var btn = document.querySelector(".menu-btn");
  var panel = document.getElementById("site-menu");
  if (!btn || !panel) return;
  function set(open) {
    panel.classList.toggle("is-open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.querySelector(".menu-btn__label").textContent = open ? "Close" : "Menu";
  }
  btn.addEventListener("click", function () { set(btn.getAttribute("aria-expanded") !== "true"); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && panel.classList.contains("is-open")) { set(false); btn.focus(); } });
  document.addEventListener("click", function (e) { if (panel.classList.contains("is-open") && !panel.contains(e.target) && !btn.contains(e.target)) set(false); });
  window.matchMedia("(min-width: 52rem)").addEventListener("change", function () { set(false); });
})();
