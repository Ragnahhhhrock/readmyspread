// Explainer videos: the homepage (DESIGN.md section 16) and each Learn tarot article (section 19). Without JavaScript the video keeps its native controls.
// With it, the poster gets one large tap target; the first tap plays with sound and hands over to native controls.
(function () {
  document.querySelectorAll(".explainer").forEach(function (fig) {
    var video = fig.querySelector("video");
    var play = fig.querySelector(".explainer__play");
    if (!video || !play) return;
    video.removeAttribute("controls");
    play.hidden = false;
    var started = false;
    var title = fig.getAttribute("data-video-title") || "explainer";
    play.addEventListener("click", function () {
      play.hidden = true;
      video.controls = true;
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
      video.focus({ preventScroll: true });
    });
    video.addEventListener("play", function () {
      if (started) return;
      started = true;
      if (window.track) window.track("video_start", { video_title: title });
    });
    video.addEventListener("ended", function () {
      if (window.track) window.track("video_complete", { video_title: title });
    });
  });
})();
