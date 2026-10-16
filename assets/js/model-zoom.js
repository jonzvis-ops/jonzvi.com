/* Minimal zoom / re-center buttons for every <model-viewer> (desktop).
   Mouse-wheel zoom is off (so the page scrolls); these give it back.
   +/- keep the current angle; the centre button returns to the start view
   (or the current mode's view if the page sets data-cam-<mode>). */
(function () {
  "use strict";
  var ICON = '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="2.2"/><path d="M8 1v3M8 12v3M1 8h3M12 8h3" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>';
  function homeView(mv) {
    var o = mv.getAttribute("camera-orbit"), t = mv.getAttribute("camera-target");
    var host = mv.parentElement && mv.parentElement.querySelector(".states");
    var spec = mv.getAttribute("data-states");
    if (host && spec) {
      var on = host.querySelector('button[aria-pressed="true"]');
      if (on) spec.split(",").forEach(function (p) {
        var kv = p.split(":");
        if (kv[0] === on.textContent) {
          var cam = mv.getAttribute("data-cam-" + kv[1]);
          if (cam) { var c = cam.split("|"); o = c[0]; if (c[1]) t = c[1]; }
        }
      });
    }
    return { o: o, t: t };
  }
  function zoom(mv, f) {
    var c = mv.getCameraOrbit();
    mv.cameraOrbit = c.theta + "rad " + c.phi + "rad " + (c.radius * f) + "m";
  }
  function center(mv) {
    var h = homeView(mv), pad = (mv._zc = !mv._zc) ? " " : "";
    if (h.t) mv.cameraTarget = h.t + pad;
    if (h.o) mv.cameraOrbit = h.o + pad;
  }
  function btn(label, html, fn) {
    var b = document.createElement("button");
    b.type = "button"; b.setAttribute("aria-label", label); b.title = label;
    b.innerHTML = html; b.addEventListener("click", fn);
    return b;
  }
  document.querySelectorAll("model-viewer").forEach(function (mv) {
    var bar = document.createElement("div");
    bar.className = "mv-zoom";
    bar.appendChild(btn("Zoom out", "&minus;", function () { zoom(mv, 1.25); }));
    bar.appendChild(btn("Zoom in", "+", function () { zoom(mv, 0.8); }));
    bar.appendChild(btn("Center view", ICON, function () { center(mv); }));
    mv.appendChild(bar);
  });
})();
