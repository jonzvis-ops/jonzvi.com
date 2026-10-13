/* IKEA'ish 3D models: colour swatches for each <model-viewer data-swatches="..."> */
(function () {
  "use strict";
  function lin(h) { return [1, 3, 5].map(function (i) { var c = parseInt(h.substr(i, 2), 16) / 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }); }
  var K = 0.72; // mean linear value of the neutral fabric/wood textures in the GLBs
  var GROUPS = {
    fabric: { title: "Fabric", mats: ["IK_fabric_seat", "IK_fabric_back_cushion"], mode: "tex", opts: [["Original", null, "#5a6a70"], ["Khaki", "#8f7c62"], ["Eucalyptus", "#4b6358"], ["Rust", "#6f3826"], ["Chocolate", "#3f3129"]] },
    wood: { title: "Wood", prefix: "IK_wood_", mode: "tex", opts: [["Oak", null, "#b69773"], ["Birch", "#bfa682"], ["Walnut", "#6b4c33"], ["Black ash", "#2e2c2a"]] },
    back: { title: "Back", mats: ["IK_felt_back"], mode: "tex", opts: [["Light grey", null, "#bcbeba"], ["Cloud", "#dcd8ce"], ["Khaki", "#ad9f88"], ["Silhouette", "#4b4441"]] },
    stool: { title: "Shell", mats: ["IK_stool_shell"], mode: "flat", opts: [["Slate", null, "#5d686c"], ["Sage", "#809177"], ["Terracotta", "#ab684c"], ["Charcoal", "#37373b"]] }
  };
  // play a clip once and hold the last frame.
  // animationName is applied asynchronously and would restart the clip looping,
  // so wait for that update before calling play().
  function playOnce(mv, name) {
    mv.pause();
    mv.animationName = name;
    Promise.resolve(mv.updateComplete).then(function () {
      mv.currentTime = 0;
      mv.play({ repetitions: 1 });
    });
  }

  // dimension lines (cm) drawn from a box in metres: "minx,miny,minz,maxx,maxy,maxz"
  var SVGNS = "http://www.w3.org/2000/svg";
  function setupDims(mv) {
    if (!mv.dataset.box) return null;
    var names = ["a", "b", "c", "d", "e", "lw", "ld", "lh"];
    names.forEach(function (n) {
      var el = document.createElement("div");
      el.slot = "hotspot-dim-" + n; el.className = n.charAt(0) === "l" ? "dim" : "dim-dot";
      el.setAttribute("data-position", "0 0 0"); mv.appendChild(el);
    });
    var svg = document.createElementNS(SVGNS, "svg"); svg.setAttribute("class", "dim-lines"); svg.setAttribute("aria-hidden", "true");
    var lines = [0, 1, 2].map(function () { var l = document.createElementNS(SVGNS, "line"); svg.appendChild(l); return l; });
    mv.appendChild(svg);
    function cm(m) { var v = m * 100; return (v < 10 ? v.toFixed(1) : Math.round(v)) + " cm"; }
    function set(n, p) { mv.updateHotspot({ name: "hotspot-dim-" + n, position: p[0] + " " + p[1] + " " + p[2] }); }
    function apply(boxStr) {
      var b = boxStr.split(",").map(Number), o = 0.03;
      var x0 = b[0], y0 = b[1], z0 = b[2], x1 = b[3], y1 = b[4], z1 = b[5];
      var A = [x0, y0, z1 + o], B = [x1, y0, z1 + o], C = [x1 + o, y0, z0], D = [x0 - o, y1, z1 + o];
      set("a", A); set("b", B); set("c", C); set("d", D); set("e", [x0 - o, y0, z1 + o]);
      set("lw", [(x0 + x1) / 2, y0, z1 + o]); set("ld", [x1 + o, y0, (z0 + z1) / 2]); set("lh", [x0 - o, (y0 + y1) / 2, z1 + o]);
      mv.querySelector('[slot="hotspot-dim-lw"]').textContent = cm(x1 - x0);
      mv.querySelector('[slot="hotspot-dim-ld"]').textContent = cm(z1 - z0);
      mv.querySelector('[slot="hotspot-dim-lh"]').textContent = cm(y1 - y0);
      requestAnimationFrame(draw);
    }
    function pt(n) { var h = mv.queryHotspot("hotspot-dim-" + n); return h && h.canvasPosition; }
    function line(l, p, q) { if (!p || !q) return; l.setAttribute("x1", p.x); l.setAttribute("y1", p.y); l.setAttribute("x2", q.x); l.setAttribute("y2", q.y); }
    function draw() {
      line(lines[0], pt("a"), pt("b")); // width, front bottom edge
      line(lines[1], pt("b"), pt("c")); // depth, right bottom edge
      line(lines[2], pt("e"), pt("d")); // height, front left edge
    }
    mv.addEventListener("camera-change", draw);
    mv.addEventListener("load", function () { apply(mv.dataset.box); });
    return { apply: apply };
  }
  var uid = 0;
  document.querySelectorAll("model-viewer[data-swatches]").forEach(function (mv) {
    var host = mv.parentElement.querySelector(".swatches");
    if (!host) return;
    var orig = {};
    function mats(g) {
      if (!mv.model) return [];
      return mv.model.materials.filter(function (m) { return g.prefix ? m.name.indexOf(g.prefix) === 0 : g.mats.indexOf(m.name) > -1; });
    }
    function apply(g, hex) {
      mats(g).forEach(function (m) {
        var pbr = m.pbrMetallicRoughness;
        if (!(m.name in orig)) orig[m.name] = { f: pbr.baseColorFactor.slice() };
        var o = orig[m.name];
        if (hex === null) { pbr.setBaseColorFactor(o.f); return; }
        var c = lin(hex);
        if (g.mode === "tex") pbr.setBaseColorFactor(c.map(function (v) { return Math.min(1, v / K); }).concat(1));
        else pbr.setBaseColorFactor(c.concat(1));
      });
    }
    var dims = setupDims(mv);
    if (dims) {
      var ctl = mv.parentElement.querySelector(".card-controls") || (function () { var c = document.createElement("div"); c.className = "card-controls"; mv.parentElement.insertBefore(c, mv.parentElement.querySelector(".swatches")); return c; })();
      var tg = document.createElement("button"); tg.type = "button"; tg.className = "dim-toggle"; tg.textContent = "Dimensions"; tg.setAttribute("aria-pressed", "true");
      tg.addEventListener("click", function () { var on = tg.getAttribute("aria-pressed") !== "true"; tg.setAttribute("aria-pressed", on ? "true" : "false"); mv.classList.toggle("hide-dims", !on); });
      ctl.appendChild(tg);
    }
    var statesHost = mv.parentElement.querySelector(".states");
    if (statesHost && mv.dataset.states) {
      statesHost.setAttribute("role", "group"); statesHost.setAttribute("aria-label", "Position");
      mv.dataset.states.split(",").forEach(function (pair, i) {
        var p = pair.split(":"), b = document.createElement("button");
        b.type = "button"; b.textContent = p[0]; b.setAttribute("aria-pressed", i === 0 ? "true" : "false");
        b.addEventListener("click", function () {
          if (b.getAttribute("aria-pressed") === "true") return;
          statesHost.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
          playOnce(mv, p[1]);
          var cam = mv.getAttribute("data-cam-" + p[1]);
          if (cam) { var c = cam.split("|"); mv.cameraOrbit = c[0]; if (c[1]) mv.cameraTarget = c[1]; }
          var nb = mv.getAttribute("data-box-" + p[1]);
          if (dims && nb) { mv.classList.add("hide-dims-anim"); setTimeout(function () { dims.apply(nb); mv.classList.remove("hide-dims-anim"); }, (mv.duration || 1) * 1000 + 50); }
        });
        statesHost.appendChild(b);
      });
    }
    mv.getAttribute("data-swatches").split(",").forEach(function (key) {
      var g = GROUPS[key.trim()]; if (!g) return;
      var id = "sw" + (uid++);
      var d = document.createElement("div"); d.className = "swatch-group";
      d.innerHTML = '<h3>' + g.title + '<span id="' + id + '-name">' + g.opts[0][0] + '</span></h3><div class="swatch-dots" role="group" aria-label="' + g.title + ' colour"></div>';
      var dots = d.querySelector(".swatch-dots");
      g.opts.forEach(function (opt, i) {
        var b = document.createElement("button");
        b.type = "button"; b.id = id + "-" + i; b.title = opt[0];
        b.setAttribute("aria-label", g.title + ": " + opt[0]); b.setAttribute("aria-pressed", i === 0 ? "true" : "false");
        b.style.setProperty("--c", opt[2] || opt[1]);
        b.addEventListener("click", function () {
          dots.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
          document.getElementById(id + "-name").textContent = opt[0];
          apply(g, opt[1]);
        });
        dots.appendChild(b);
      });
      host.appendChild(d);
    });
  });
})();
