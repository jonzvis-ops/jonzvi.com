/* A.O.K. 3D models: mode buttons for each <model-viewer data-modes="Label:key,...">.
   The GLB holds one clip per transition, named "<from>__<to>", so switching
   goes straight from the current mode to the new one (no reset). Each clip
   plays once and holds its last frame. Clicks during a transition are queued. */
(function () {
  "use strict";
  function playClip(mv, name) {
    return new Promise(function (done) {
      mv.pause();
      mv.animationName = name;
      Promise.resolve(mv.updateComplete).then(function () {
        mv.currentTime = 0;
        var t = setTimeout(fin, ((mv.duration || 2) * 1000) + 400);
        function fin() { clearTimeout(t); mv.removeEventListener("finished", fin); done(); }
        mv.addEventListener("finished", fin);
        mv.play({ repetitions: 1 });
      });
    });
  }
  document.querySelectorAll("model-viewer[data-modes]").forEach(function (mv) {
    var host = mv.parentElement.querySelector(".states");
    if (!host) return;
    host.setAttribute("role", "group");
    host.setAttribute("aria-label", "Mode");
    var modes = mv.getAttribute("data-modes").split(",").map(function (m) { return m.split(":"); });
    var cur = modes[0][1], busy = false, want = null;
    function go(target) {
      if (busy) { want = target; return; }
      if (target === cur) return;
      busy = true;
      var clip = cur + "__" + target;
      cur = target;
      playClip(mv, clip).then(function () {
        busy = false;
        if (want !== null) { var w = want; want = null; go(w); }
      });
    }
    modes.forEach(function (p, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = p[0];
      b.setAttribute("aria-pressed", i === 0 ? "true" : "false");
      b.addEventListener("click", function () {
        host.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        go(p[1]);
      });
      host.appendChild(b);
    });
  });
})();
