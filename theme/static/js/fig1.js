/* Fig. 1 — a Universal Dependencies parse above the question, an alignment to the
   relational query below. Positions are measured from the typeset text, so the
   figure follows the fonts; on narrow screens the whole figure is scaled down. */
(() => {
  const fig = document.getElementById("fig1");
  if (!fig) return;
  const wrap = fig.querySelector(".fig-scroll");
  const body = fig.querySelector(".fig-body");
  const svg = fig.querySelector(".fig-svg");
  const toks = [...fig.querySelectorAll(".sent .tok")];
  const rts = [...fig.querySelectorAll(".rt[data-r]")];
  // [head, dependent, label]: 0 Which 1 authors 2 submitted 3 papers 4 to 5 NLDB 6 in 7 2027 8 ?
  const ARCS = [[1,0,"det"],[2,1,"nsubj"],[2,3,"obj"],[5,4,"case"],[2,5,"obl"],[7,6,"case"],[2,7,"obl"]];
  const ROOT = 2;
  const STATIC = location.search.includes("static");
  let animated = false;

  function draw(animate) {
    body.style.transform = "none";
    wrap.style.height = "";
    const B = body.getBoundingClientRect();
    const box = el => { const r = el.getBoundingClientRect();
      return { t: r.top - B.top, b: r.bottom - B.top, w: r.width, cx: r.left - B.left + r.width / 2 }; };
    const T = toks.map(box);
    const lens = [...new Set(ARCS.map(([h, d]) => Math.abs(h - d)))].sort((a, b) => a - b);
    const y0 = Math.min(...T.map(t => t.t)) + 4;
    let s = "", k = 0;
    const d = () => `--d:${(k * 0.09).toFixed(2)}s`;
    const arrow = x => `<path class="arrow" style="${d()}" d="M${x - 3},${y0 - 6} L${x},${y0} L${x + 3},${y0 - 6} Z"/>`;

    for (const [h, dep, lab] of ARCS) {
      const rank = lens.indexOf(Math.abs(h - dep));
      const H = 24 + rank * 22, c = H * 4 / 3;
      const dir = Math.sign(dep - h);
      const x1 = T[h].cx + dir * (4 + rank * 5), x2 = T[dep].cx - dir * 2;
      s += `<path class="arc" style="${d()}" d="M${x1},${y0} C${x1},${y0 - c} ${x2},${y0 - c} ${x2},${y0}"/>`;
      s += arrow(x2);
      s += `<text class="lab" style="${d()}" x="${(x1 + x2) / 2}" y="${y0 - H - 4}" text-anchor="middle">${lab}</text>`;
      k++;
    }
    const rx = T[ROOT].cx, top = y0 - 24 - lens.length * 22 - 6;
    s += `<path class="arc" style="${d()}" d="M${rx},${top} L${rx},${y0}"/>` + arrow(rx);
    s += `<text class="lab" style="${d()}" x="${rx}" y="${top - 6}" text-anchor="middle">root</text>`;
    k++;

    toks.forEach((tk, i) => {
      if (!tk.dataset.a) return;
      for (const r of rts.filter(r => r.dataset.r === tk.dataset.a)) {
        const a = T[i], b = box(r);
        const xa = a.cx, ya = a.b + 6, xb = b.cx, yb = b.t - 4, m = (ya + yb) / 2;
        s += `<path class="al" data-r="${r.dataset.r}" style="${d()}" d="M${xa},${ya} C${xa},${m} ${xb},${m} ${xb},${yb}"/>`;
        s += `<circle class="dot" style="${d()}" cx="${xa}" cy="${ya}" r="1.6"/><circle class="dot" style="${d()}" cx="${xb}" cy="${yb}" r="1.6"/>`;
        k++;
      }
    });

    svg.setAttribute("viewBox", `0 0 ${B.width} ${B.height}`);
    svg.innerHTML = s;
    if (animate && !animated && !STATIC) {
      for (const p of svg.querySelectorAll(".arc, .al")) p.style.setProperty("--len", p.getTotalLength().toFixed(1));
      svg.classList.add("anim");
      animated = true;
    } else if (!animate) svg.classList.remove("anim");

    const r = Math.min(1, wrap.clientWidth / B.width);   // narrow screens: shrink, don't scroll
    if (r < 1) { body.style.transform = `scale(${r})`; wrap.style.height = `${B.height * r}px`; }
  }

  function light(key) {
    fig.classList.toggle("hl", !!key);
    toks.forEach(t => t.classList.toggle("on", !!key && t.dataset.a === key));
    rts.forEach(r => r.classList.toggle("on", !!key && r.dataset.r === key));
    svg.querySelectorAll(".al").forEach(p => {
      p.classList.toggle("on", p.dataset.r === key);
      p.classList.toggle("off", !!key && p.dataset.r !== key);
    });
  }
  [...toks.filter(t => t.dataset.a), ...rts].forEach(el => {
    const key = el.dataset.a || el.dataset.r;
    el.addEventListener("mouseenter", () => light(key));
    el.addEventListener("mouseleave", () => light(null));
  });

  if (document.fonts.status === "loaded") draw(true);
  else { draw(false); document.fonts.ready.then(() => draw(true)); }
  let raf;
  addEventListener("resize", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => draw(false)); });
})();
