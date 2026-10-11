(function () {
  "use strict";
  document.documentElement.classList.add("js");

  function csrfToken() {
    var el = document.querySelector("input[name=csrfmiddlewaretoken]");
    return el ? el.value : "";
  }

  // 1. Save / unsave an opportunity without leaving the page
  document.querySelectorAll("[data-save-url]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      fetch(btn.dataset.saveUrl, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken(), "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
      })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (data) {
          btn.setAttribute("aria-pressed", data.saved ? "true" : "false");
          btn.textContent = data.saved ? "Saved" : "Save";
        })
        .catch(function () { btn.textContent = "Try again"; });
    });
  });

  // 2. Add another skill row to the recruiter's weighted-skills formset
  var addBtn = document.getElementById("add-skill-row");
  if (addBtn) {
    addBtn.addEventListener("click", function () {
      var total = document.getElementById("id_opportunityskill_set-TOTAL_FORMS");
      var tpl = document.getElementById("empty-form").innerHTML;
      var index = parseInt(total.value, 10);
      var holder = document.createElement("tbody");
      holder.innerHTML = tpl.replace(/__prefix__/g, index);
      var row = holder.firstElementChild;
      row.querySelectorAll("select").forEach(function (e) { e.classList.add("form-select"); });
      row.querySelectorAll("input").forEach(function (e) { e.classList.add("form-control"); });
      document.getElementById("skill-rows").appendChild(row);
      total.value = index + 1;
    });
  }

  // 3. Live-refresh the unread notification badge
  var badge = document.getElementById("notif-badge");
  if (badge) {
    setInterval(function () {
      fetch(badge.dataset.url, { credentials: "same-origin" })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
          if (!d) return;
          badge.textContent = d.unread;
          badge.hidden = d.unread === 0;
        })
        .catch(function () {});
    }, 60000);
  }

  // 4. Debounced search: submit the filter form shortly after typing stops
  var search = document.querySelector("[data-autosubmit]");
  if (search) {
    var timer;
    search.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { search.form.submit(); }, 600);
    });
    if (document.activeElement === document.body && search.value) {
      search.focus();
      search.setSelectionRange(search.value.length, search.value.length);
    }
  }

  // 5. Navbar gains a shadow once the page scrolls
  var bar = document.querySelector(".topbar");
  if (bar) {
    var onScroll = function () { bar.classList.toggle("scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // 6. Show / hide button on every password field
  document.querySelectorAll("input[type=password]").forEach(function (input) {
    var wrap = document.createElement("div");
    wrap.className = "pw-wrap";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "pw-toggle";
    btn.textContent = "Show";
    btn.setAttribute("aria-label", "Show password");
    btn.addEventListener("click", function () {
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.textContent = show ? "Hide" : "Show";
      btn.setAttribute("aria-label", (show ? "Hide" : "Show") + " password");
    });
    wrap.appendChild(btn);
  });

  // 7. Fade-and-rise reveal for cards below the fold (skipped for reduced motion)
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        io.unobserve(el);
        el.classList.add("in");
        // hand the element back to its normal hover transitions once revealed
        setTimeout(function () { el.removeAttribute("data-reveal"); el.classList.remove("in"); el.style.removeProperty("--d"); }, 900);
      });
    }, { threshold: 0.08 });
    var n = 0;
    document.querySelectorAll(".opp-card, .stat, .panel:not(.auth-card)").forEach(function (el) {
      var top = el.getBoundingClientRect().top;
      if (top < window.innerHeight) return;       // already on screen: never hide it
      el.setAttribute("data-reveal", "");
      el.style.setProperty("--d", (n++ % 3) * 70 + "ms");
      io.observe(el);
    });
  }
  // 8. Password strength (number + text) and live match message
  var pw1 = document.getElementById("id_password1") || document.getElementById("id_new_password1");
  var pw2 = document.getElementById("id_password2") || document.getElementById("id_new_password2");
  if (pw1) {
    var meter = document.createElement("div");
    meter.innerHTML = '<div class="pw-meter"><i></i></div><div class="pw-meter-text small" aria-live="polite"></div>';
    (pw1.closest(".pw-wrap") || pw1).insertAdjacentElement("afterend", meter);
    var bar = meter.querySelector("i"), label = meter.querySelector(".pw-meter-text");
    var levels = [[40, "Weak", "#ef4444"], [70, "Medium", "#f59e0b"], [90, "Strong", "#10b981"], [101, "Very strong", "#059669"]];
    var score = function (v) {
      var s = 0;
      if (v.length >= 8) s += 25;
      if (v.length >= 12) s += 15;
      if (/[a-z]/.test(v) && /[A-Z]/.test(v)) s += 20;
      if (/\d/.test(v)) s += 20;
      if (/[^A-Za-z0-9]/.test(v)) s += 20;
      return s;
    };
    pw1.addEventListener("input", function () {
      var v = pw1.value;
      if (!v) { label.textContent = ""; bar.style.width = "0"; return; }
      var s = score(v), lv = levels.find(function (l) { return s < l[0]; });
      bar.style.width = s + "%";
      bar.style.background = lv[2];
      label.style.color = lv[2];
      label.textContent = v.length + " characters \u00b7 Strength " + s + "/100 \u00b7 " + lv[1];
    });
  }
  if (pw1 && pw2) {
    // hide the old server-side messages as soon as the user starts typing again
    var holder = pw2.closest(".mb-3") || pw2.parentNode;
    var stale = holder.querySelectorAll(".text-danger");
    var list = document.createElement("ul");
    list.className = "pw-live";
    list.hidden = true;
    list.setAttribute("aria-live", "polite");
    (pw2.closest(".pw-wrap") || pw2).insertAdjacentElement("afterend", list);
    // short hint list only; the server still does the full common-password check
    var COMMON = ["password", "password1", "password123", "12345678", "123456789", "qwerty123", "qwertyuiop",
      "iloveyou", "admin123", "welcome1", "abc12345", "11111111", "letmein1", "passw0rd", "1q2w3e4r", "qwerty12"];
    var rules = [
      ["At least 8 characters", function (a) { return a.length >= 8; }],
      ["Not only numbers", function (a) { return a.length > 0 && !/^\d+$/.test(a); }],
      ["Not a very common password", function (a) { return a.length > 0 && COMMON.indexOf(a.toLowerCase()) === -1; }],
      ["Both passwords match", function (a, b) { return a.length > 0 && a === b; }]
    ];
    var render = function () {
      stale.forEach(function (e) { e.hidden = true; });
      list.hidden = !(pw1.value || pw2.value);
      list.innerHTML = rules.map(function (r) {
        var ok = r[1](pw1.value, pw2.value);
        return '<li class="' + (ok ? "ok" : "bad") + '">' + (ok ? "\u2713 " : "\u2717 ") + r[0] + "</li>";
      }).join("");
    };
    pw1.addEventListener("input", render);
    pw2.addEventListener("input", render);
  }
  // 9. Visual extras: scroll progress bar, card spotlight, theme switcher
  var progress = document.createElement("div");
  progress.className = "scroll-progress";
  progress.setAttribute("aria-hidden", "true");
  document.body.appendChild(progress);
  var updateProgress = function () {
    var max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.transform = "scaleX(" + (max > 0 ? Math.min(window.scrollY / max, 1) : 0) + ")";
  };
  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  document.addEventListener("pointermove", function (e) {
    var card = e.target.closest ? e.target.closest(".opp-card") : null;
    if (!card) return;
    var r = card.getBoundingClientRect();
    card.style.setProperty("--mx", (e.clientX - r.left) + "px");
    card.style.setProperty("--my", (e.clientY - r.top) + "px");
  }, { passive: true });

  // Theme switcher: remembers the choice in this browser
  var THEMES = ["royal", "aurora", "sakura", "arctic", "citrus"];
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem("cl-theme"); } catch (err) {}
  var current = THEMES.indexOf(stored) > -1 ? stored : (root.getAttribute("data-theme") || "royal");
  var switcher = document.createElement("div");
  switcher.className = "theme-switch";
  switcher.setAttribute("role", "group");
  switcher.setAttribute("aria-label", "Colour theme");
  var setTheme = function (t, save) {
    root.setAttribute("data-theme", t);
    root.setAttribute("data-bs-theme", t === "citrus" ? "light" : "dark");
    switcher.querySelectorAll(".theme-dot").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.t === t ? "true" : "false");
    });
    if (save) { try { localStorage.setItem("cl-theme", t); } catch (err) {} }
  };
  THEMES.forEach(function (t) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "theme-dot";
    b.dataset.t = t;
    b.title = t.charAt(0).toUpperCase() + t.slice(1) + " theme";
    b.setAttribute("aria-label", b.title);
    b.addEventListener("click", function () { setTheme(t, true); });
    switcher.appendChild(b);
  });
  document.body.appendChild(switcher);
  setTheme(current, false);
})();