/* Jon Zvi Shmuely portfolio — small, dependency-free helpers */
(function () {
  "use strict";

  // Mobile menu
  var body = document.body;
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("site-nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      body.classList.toggle("nav-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("open");
        body.classList.remove("nav-open");
        btn.setAttribute("aria-expanded", "false");
      }
    });
  }

  // "My Work" dropdown (click / keyboard / touch)
  document.querySelectorAll(".has-sub").forEach(function (li) {
    var t = li.querySelector(".sub-toggle");
    if (!t) return;
    t.addEventListener("click", function (e) {
      e.preventDefault();
      var open = li.classList.toggle("open");
      t.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", function (e) {
      if (!li.contains(e.target)) { li.classList.remove("open"); t.setAttribute("aria-expanded", "false"); }
    });
  });

  // Image fallback: if a local image is missing, load the original copy
  document.querySelectorAll("img[data-fallback]").forEach(function (img) {
    function swap() {
      if (img.dataset.swapped) return;
      img.dataset.swapped = "1";
      img.removeAttribute("srcset");
      img.src = img.dataset.fallback;
    }
    if (img.complete && img.naturalWidth === 0) swap();
    img.addEventListener("error", swap);
  });

  // Contact form (Web3Forms — free, no backend needed)
  var form = document.getElementById("contact-form");
  if (form) {
    var status = form.querySelector(".status");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.querySelector("[name=botcheck]").checked) return;
      var submit = form.querySelector("button[type=submit]");
      submit.disabled = true;
      status.className = "status";
      status.textContent = "Sending…";
      var data = new FormData(form);
      var name = [data.get("first_name"), data.get("last_name")].filter(Boolean).join(" ");
      data.set("subject", "jonzvi.com: " + (data.get("subject") || "New message") + (name ? " — " + name : ""));
      fetch(form.action, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok && String(res.j.success) !== "false") {
            status.textContent = "Thanks for submitting!";
            form.reset();
          } else {
            var err = new Error(res.j.message || "Error");
            err.server = res.j.message;
            throw err;
          }
        })
        .catch(function (err) {
          status.className = "status error";
          var msg = err && err.server ? err.server + " " : "Something went wrong. ";
          status.innerHTML = "";
          status.appendChild(document.createTextNode(msg + "You can also email "));
          var a = document.createElement("a");
          a.href = "mailto:jonzvis@gmail.com";
          a.textContent = "jonzvis@gmail.com";
          status.appendChild(a);
          status.appendChild(document.createTextNode("."));
        })
        .finally(function () { submit.disabled = false; });
    });
  }

  // Footer year
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
})();
