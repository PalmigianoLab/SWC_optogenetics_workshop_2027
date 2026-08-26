// Countdowns, and highlighting the section you are looking at in the top bar.
(function () {
  const counters = document.querySelectorAll(".counter[data-deadline]");

  function tick() {
    const now = Date.now();
    counters.forEach(function (counter) {
      const target = new Date(counter.dataset.deadline).getTime();
      const value = counter.querySelector(".counter__value");
      if (isNaN(target)) { value.textContent = "—"; return; }
      let left = Math.max(0, target - now);
      if (left === 0) { value.textContent = "now"; return; }
      const days = Math.floor(left / 86400000);
      const hours = Math.floor((left % 86400000) / 3600000);
      const mins = Math.floor((left % 3600000) / 60000);
      const secs = Math.floor((left % 60000) / 1000);
      value.textContent = days + "d " + hours + "h " + mins + "m " + secs + "s";
    });
  }
  if (counters.length) { tick(); setInterval(tick, 1000); }

  const links = Array.from(document.querySelectorAll(".topbar__nav a"));
  const sections = links
    .map(function (a) { return document.querySelector(a.getAttribute("href")); })
    .filter(Boolean);

  if ("IntersectionObserver" in window && sections.length) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (a) {
          a.classList.toggle("is-active", a.getAttribute("href") === "#" + entry.target.id);
        });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach(function (s) { observer.observe(s); });
  }
})();

// Speaker panels. Each clickable card names the dialog it opens.
(function () {
  document.querySelectorAll("[data-opens]").forEach(function (card) {
    card.addEventListener("click", function () {
      const sheet = document.getElementById(card.dataset.opens);
      if (sheet && typeof sheet.showModal === "function") sheet.showModal();
    });
  });

  document.querySelectorAll("dialog.sheet").forEach(function (sheet) {
    sheet.querySelector("[data-closes]").addEventListener("click", function () {
      sheet.close();
    });
    // Clicking the backdrop closes it too.
    sheet.addEventListener("click", function (event) {
      if (event.target === sheet) sheet.close();
    });
  });
})();
