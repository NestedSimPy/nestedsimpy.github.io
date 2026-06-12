// NestedSimPy docs — gentle scroll-reveal for cards, figures, tables and
// admonitions. Purely presentational; respects prefers-reduced-motion (the
// CSS only applies the hidden state inside a no-preference media query, so
// without JS or with reduced motion everything stays visible).
(function () {
  if (!("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var targets = document.querySelectorAll(
    ".content .sd-card, .content figure, .content table.docutils, .content .admonition"
  );
  if (!targets.length) return;

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("ns-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
  );

  targets.forEach(function (el, i) {
    el.classList.add("ns-reveal");
    // small stagger for elements that enter together
    el.style.transitionDelay = (i % 4) * 60 + "ms";
    observer.observe(el);
  });
})();

// codediff directive: expand folded unchanged runs.
document.addEventListener("click", function (e) {
  var btn = e.target.closest("button.cd-expand");
  if (!btn) return;
  var expander = btn.closest("tr.cd-expander");
  var id = expander.getAttribute("data-foldid");
  var table = expander.closest("table");
  table
    .querySelectorAll('tr[data-fold="' + id + '"]')
    .forEach(function (row) { row.classList.remove("cd-hidden"); });
  expander.remove();
});


// top scroll progress bar
(function () {
  var bar = document.createElement("div");
  bar.id = "ns-progress";
  document.body.appendChild(bar);
  function update() {
    var el = document.scrollingElement;
    var max = el.scrollHeight - el.clientHeight;
    bar.style.width = max > 0 ? (el.scrollTop / max) * 100 + "%" : "0";
  }
  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update, { passive: true });
  update();
})();
