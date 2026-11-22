/* Small, progressive: the page is complete without it.
   - marks the next deadline (the build marks it too, but the site may be built weeks earlier)
   - fills countdowns
   - shows deadlines in the reader's own time zone */
(() => {
  const now = new Date();
  const days = iso => Math.ceil((new Date(iso) - now) / 864e5);

  // next deadline in date lists
  for (const list of document.querySelectorAll(".dates")) {
    const items = [...list.querySelectorAll("li[data-deadline]")];
    items.forEach(li => {
      li.classList.remove("next");
      li.classList.toggle("passed", new Date(li.dataset.deadline) < now);
    });
    const next = items.find(li => new Date(li.dataset.deadline) >= now);
    if (next) next.classList.add("next");
  }

  // countdowns
  for (const el of document.querySelectorAll(".count[data-deadline]")) {
    const n = days(el.dataset.deadline);
    el.textContent = n > 1 ? `in ${n} days` : n === 1 ? "tomorrow" : n === 0 ? "today" : "closed";
  }

  // Every page reads the same event data, not just those with .dates lists.
  const note = document.querySelector("[data-next-note] .count");
  const data = document.getElementById("deadline-data");
  if (note && data) {
    const events = JSON.parse(data.textContent);
    const upcoming = events.find(event => event.deadline && new Date(event.deadline) >= now);
    const box = note.closest("[data-next-note]");
    if (upcoming) {
      box.querySelector(".when").firstChild.textContent = upcoming.displayDate;
      box.querySelector(".what").textContent = upcoming.label + ", 23:59 AoE";
      const dagger = box.querySelector(".dagger");
      if (dagger) dagger.hidden = !upcoming.provisional;
      note.dataset.deadline = upcoming.deadline;
      const n = days(upcoming.deadline);
      note.textContent = n > 1 ? `in ${n} days` : n === 1 ? "tomorrow" : n === 0 ? "today" : "closed";
    } else box.hidden = true;
  }

  // local time of each deadline (dates page)
  const fmtLocal = new Intl.DateTimeFormat(undefined, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  for (const el of document.querySelectorAll("[data-local]")) {
    el.textContent = fmtLocal.format(new Date(el.dataset.local));
  }
  const tzEl = document.querySelector("[data-tz]");
  if (tzEl && tz) { tzEl.textContent = tz.replace(/_/g, " "); tzEl.closest("[hidden]")?.removeAttribute("hidden"); }
})();
