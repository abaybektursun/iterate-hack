"""Strategy basins, step 4 (laptop): one self-contained HTML page from strategy_analyze.py outputs.

    python3 studies/basins/analysis/strategy_page.py studies/basins/results/strategy/<arm>-<nn>   # writes strategy_map.html there
"""
import json
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
summary = json.loads((d / "summary.json").read_text())
per = json.loads((d / "per_problem.json").read_text())
maps = json.loads((d / "maps.json").read_text())
math = json.loads((pathlib.Path(__file__).resolve().parents[2] / "rlneurons" / "data" / "rln4" / "math500.json").read_text())
data = {"summary": summary, "per": per, "maps": maps["maps"], "names": maps["group_names"],
        "problems": {str(r["idx"]): {"uid": math[r["idx"]]["unique_id"], "text": math[r["idx"]]["problem"][:400]} for r in per}}

PAGE = r"""<title>Strategy Basins</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* layout: verdict strip on top, then a grid of per-problem strategy maps; hover a dot to read its method */
:root{--bg:#f6f7f9;--panel:#ffffff;--fg:#1b2330;--muted:#5d6878;--line:#dfe3ea;--base:#2f6fb0;--rl:#c8553d;--ok:#2e7d4f;
--display:"Space Grotesk",system-ui,sans-serif;--text:"Inter",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#11151c;--panel:#181e27;--fg:#e6eaf0;--muted:#97a2b3;--line:#2a3340;--base:#6aa6e6;--rl:#ef8a6f;--ok:#6cc690;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#11151c;--panel:#181e27;--fg:#e6eaf0;--muted:#97a2b3;--line:#2a3340;--base:#6aa6e6;--rl:#ef8a6f;--ok:#6cc690;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--text);line-height:1.5}
.wrap{max-width:1200px;margin:0 auto;padding-block:28px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:24px}
h1{font-family:var(--display);font-size:clamp(26px,4vw,40px);margin:0;text-wrap:balance;letter-spacing:-.01em}
h2{font-family:var(--display);font-size:20px;margin:0}
.lede{max-width:70ch;color:var(--muted);margin:6px 0 0}
.key{display:inline-flex;align-items:center;gap:6px;font-weight:600}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:grid;gap:4px;min-width:0}
.stat .lab{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.stat .val{font-family:var(--mono);font-size:22px;font-variant-numeric:tabular-nums}
.stat .ci{font-family:var(--mono);font-size:12px;color:var(--muted)}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px;color:var(--muted)}
button{font:inherit;border:1px solid var(--line);background:var(--panel);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer}
button[aria-pressed="true"]{border-color:var(--fg);font-weight:600}
button:focus-visible{outline:2px solid var(--base);outline-offset:2px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px;display:grid;gap:6px;min-width:0}
.card .hd{display:flex;justify-content:space-between;gap:8px;font-size:12px;font-family:var(--mono);color:var(--muted)}
.card .hd b{color:var(--fg);font-weight:600}
svg{width:100%;height:auto;display:block}
svg .pt{stroke:var(--panel);stroke-width:1}
.tip{position:fixed;pointer-events:none;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px;max-width:340px;font-size:13px;box-shadow:0 6px 24px rgba(0,0,0,.18);z-index:5}
.mono{font-family:var(--mono);font-size:12px}
.note{font-size:12px;color:var(--muted);max-width:90ch}
</style>
<div class="wrap">
  <header>
    <h1>Does RL find new ways to solve math, or pick the old ones more often?</h1>
    <p class="lede">Each dot is one sampled solution, placed by an LLM judge's view of its <em>method</em> (t-STE from triplet judgments). The judge never sees which model wrote it.
    <span class="key"><span class="dot" style="background:var(--base)"></span>Olmo 3 base + cue</span> ·
    <span class="key"><span class="dot" style="background:var(--rl)"></span>Olmo 3.1 RL-Zero-Math</span> · filled = correct, ring = wrong.</p>
  </header>
  <section class="stats" id="stats"></section>
  <div class="controls" id="controls"><span>Sort maps by</span></div>
  <section class="grid" id="grid"></section>
  <p class="note" id="foot"></p>
</div>
<div class="tip" id="tip" hidden></div>
<script>
const D = __DATA__;
const S = D.summary, f2 = x => x == null || isNaN(x) ? "–" : (+x).toFixed(2);
const ci = a => a ? `${f2(a[0])} [${f2(a[1])}, ${f2(a[2])}] n=${a[3]}` : "–";
const stats = [
  ["Strategies in 16 samples", `${f2(S.groups_16.baseA[0])} vs ${f2(S.groups_16.rlA[0])}`, "base vs RL, rarefied to equal size"],
  ["Base − RL (main)", f2(S.main_baseA_minus_rlA[0]), ci(S.main_baseA_minus_rlA)],
  ["Null: base − base", f2(S.null_baseA_minus_baseB[0]), ci(S.null_baseA_minus_baseB)],
  ["RL correct in RL-only strategies", f2(S.rl_correct_in_rl_only_groups[0]), "share of RL's correct samples whose strategy the base never used in 32"],
  ["Base correct in base-only strategies", f2(S.base_correct_in_base_only_groups[0]), "the mirror image"],
  ["Judge checks", `dup ${S.controls.dup} · mix ${S.controls.mix}`, `t-STE held-out ${f2(S.tste_heldout_acc && S.tste_heldout_acc[0])} vs shuffled ${f2(S.tste_shuffled_id_null_acc && S.tste_shuffled_id_null_acc[0])}`],
];
document.getElementById("stats").innerHTML = stats.map(([l, v, c]) => `<div class="stat"><span class="lab">${l}</span><span class="val">${v}</span><span class="ci">${c}</span></div>`).join("");
document.getElementById("foot").textContent = `${S.n_problems} MATH-500 problems, ${S.n_items} solutions, both models at T 1.0 / top-p 1.0. Accuracy (grader v3): base ${f2(S.acc_grader_v3.base)}, RL ${f2(S.acc_grader_v3.rl)}. No-method share (loops, cut-offs): base ${f2(S.no_method_share.base)}, RL ${f2(S.no_method_share.rl)}. Intervals: bootstrap 95% over problems.`;
const per = Object.fromEntries(D.per.map(r => [r.idx, r]));
const sorts = {"base − RL gap": r => -(r.baseA - r.rlA), "RL accuracy gain": r => -(r.acc.rl - r.acc.base), "problem id": r => r.idx};
let cur = "base − RL gap";
const ctl = document.getElementById("controls");
for (const k of Object.keys(sorts)) { const b = document.createElement("button"); b.textContent = k; b.id = "sort-" + k.replace(/\W+/g, "-"); b.onclick = () => { cur = k; draw(); }; ctl.appendChild(b); }
const tip = document.getElementById("tip"), esc = s => String(s).replace(/[&<>]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]));
function draw() {
  for (const b of ctl.querySelectorAll("button")) b.setAttribute("aria-pressed", b.textContent === cur);
  const ids = Object.keys(D.maps).filter(i => per[i]).sort((a, b) => sorts[cur](per[a]) - sorts[cur](per[b]));
  document.getElementById("grid").innerHTML = ids.map(i => {
    const pts = D.maps[i], r = per[i], xs = pts.map(p => p.x), ys = pts.map(p => p.y);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys), W = 240, Hh = 180, pad = 10;
    const sx = x => pad + (x - x0) / ((x1 - x0) || 1) * (W - 2 * pad), sy = y => pad + (y - y0) / ((y1 - y0) || 1) * (Hh - 2 * pad);
    const dots = pts.map((p, k) => { const c = p.model === "base" ? "var(--base)" : "var(--rl)";
      return `<circle class="pt" data-i="${i}" data-k="${k}" cx="${sx(p.x).toFixed(1)}" cy="${sy(p.y).toFixed(1)}" r="4.2" fill="${p.correct ? c : "var(--panel)"}" stroke="${c}" stroke-width="${p.correct ? 1 : 1.6}"/>`; }).join("");
    return `<div class="card"><div class="hd"><span>${esc(D.problems[i].uid.replace("test/", ""))}</span><span>strategies <b>${f2(r.baseA)}</b> vs <b>${f2(r.rlA)}</b></span></div>
      <svg viewBox="0 0 ${W} ${Hh}" role="img" aria-label="strategy map for problem ${i}">${dots}</svg>
      <div class="hd"><span>acc ${f2(r.acc.base)} → ${f2(r.acc.rl)}</span><span>groups ${f2(r.n_groups_total)}</span></div></div>`;
  }).join("");
}
document.getElementById("grid").addEventListener("mousemove", e => {
  const c = e.target.closest("circle"); if (!c) { tip.hidden = true; return; }
  const p = D.maps[c.dataset.i][c.dataset.k], names = D.names[c.dataset.i] || [];
  tip.innerHTML = `<div class="mono">${p.model === "base" ? "base + cue" : "RL-Zero"} · sample ${p.sample} · ${p.correct ? "correct" : "wrong"}${p.group != null && names[p.group] ? " · " + esc(names[p.group]) : ""}</div><div>${esc(p.summary)}</div>`;
  tip.hidden = false; tip.style.left = Math.min(e.clientX + 14, innerWidth - 360) + "px"; tip.style.top = (e.clientY + 14) + "px";
});
document.getElementById("grid").addEventListener("mouseleave", () => tip.hidden = true);
draw();
</script>
"""
(d / "strategy_map.html").write_text(PAGE.replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
print(d / "strategy_map.html")
