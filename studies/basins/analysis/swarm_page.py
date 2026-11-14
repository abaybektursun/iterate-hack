"""Swarm map, step 4 (laptop): one self-contained HTML page from swarm_analyze.py outputs.

    python3 -m studies.basins.analysis.swarm_page studies/basins/results/swarm/<arm>-<nn> <judge model>   # writes swarm_map.html there
"""
import json
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
data = {"summary": json.loads((d / "summary.json").read_text()), **json.loads((d / "map.json").read_text()),
        "judge": sys.argv[2] if len(sys.argv) > 2 else ""}

PAGE = r"""<title>Swarm Idea Map</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* layout: verdict line, stat strip, then the map (left) beside the basin list (right); a replay slider under the map */
:root{--bg:#f4f6f8;--panel:#ffffff;--fg:#17202b;--muted:#5b6676;--line:#dde2e9;--accent:#2b6cb0;--empty:#b4541f;
--display:"Space Grotesk",system-ui,sans-serif;--text:"Inter",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f141a;--panel:#161d26;--fg:#e5eaf0;--muted:#96a1b1;--line:#28323f;--accent:#7fb0ea;--empty:#f0a070;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f141a;--panel:#161d26;--fg:#e5eaf0;--muted:#96a1b1;--line:#28323f;--accent:#7fb0ea;--empty:#f0a070;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--text);line-height:1.5}
.wrap{max-width:1240px;margin:0 auto;padding-block:28px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:20px}
h1{font-family:var(--display);font-size:clamp(26px,4vw,40px);margin:0;text-wrap:balance;letter-spacing:-.01em}
h2{font-family:var(--display);font-size:18px;margin:0}
.lede{max-width:72ch;color:var(--muted);margin:6px 0 0}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;display:grid;gap:2px;min-width:0}
.lab{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.val{font-family:var(--mono);font-size:22px;font-variant-numeric:tabular-nums}
.sub{font-family:var(--mono);font-size:12px;color:var(--muted)}
.main{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:16px;align-items:start}
@media (max-width:820px){.main{grid-template-columns:1fr}}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;display:grid;gap:10px;min-width:0}
svg{width:100%;height:auto;display:block}
.basins{display:grid;gap:6px;max-height:640px;overflow:auto}
.b{display:grid;grid-template-columns:14px 1fr auto;gap:8px;align-items:center;font-size:13px;padding:4px 6px;border-radius:6px;cursor:default}
.b:hover,.b.on{background:color-mix(in srgb,var(--accent) 12%,transparent)}
.sw{width:12px;height:12px;border-radius:3px}
.cnt{font-family:var(--mono);font-size:12px;color:var(--muted);white-space:nowrap}
.tag{font-size:11px;font-weight:600;color:var(--empty);margin-left:6px;text-transform:uppercase;letter-spacing:.05em}
.replay{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:13px;color:var(--muted)}
input[type=range]{flex:1;min-width:160px;accent-color:var(--accent)}
button{font:inherit;border:1px solid var(--line);background:var(--panel);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer}
button:focus-visible,input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.tip{position:fixed;pointer-events:none;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px;max-width:380px;font-size:13px;box-shadow:0 6px 24px rgba(0,0,0,.18);z-index:5}
.mono{font-family:var(--mono);font-size:12px;color:var(--muted)}
.note{font-size:12px;color:var(--muted);max-width:100ch}
.tbl{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600}
td.num{font-family:var(--mono);text-align:right;white-space:nowrap}
tr.rl td{background:color-mix(in srgb,var(--accent) 8%,transparent)}
tr.old td{color:var(--muted);text-decoration:line-through}
.pill{display:inline-block;font-size:11px;padding:1px 6px;border-radius:999px;border:1px solid var(--line);color:var(--muted);margin-left:4px;white-space:nowrap}
.bar{height:6px;border-radius:3px;background:var(--accent);opacity:.55;margin-top:4px}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--muted)}
</style>
<div class="wrap">
  <header>
    <h1 id="h1">Where the swarm has looked, and where it has not</h1>
    <p class="lede">Every item on the team board (ideas, claimed work, findings, results) placed by an LLM judge's view of its <em>approach</em>, from triplet judgments ("is B or C closer to A?") embedded with t-STE. Hollow diamonds are possible directions the judge listed from DIRECTION.md alone, before seeing the board. A basin holding only diamonds is a direction nobody has touched.</p>
  </header>
  <section class="stats" id="stats"></section>
  <section class="main">
    <div class="panel">
      <svg id="map" viewBox="0 0 640 480" role="img" aria-label="idea map of the team board"></svg>
      <div class="legend"><span>● board item (size: result &gt; work &gt; idea/knowledge)</span><span>◇ possible direction pursued by a board item</span><span style="color:var(--empty)">◇ untouched direction</span></div>
      <div class="replay"><button id="play">Replay</button><input id="t" type="range" min="0" max="100" value="100" aria-label="time"><span id="tlab" class="mono"></span></div>
    </div>
    <div class="panel"><h2>Basins</h2><div class="basins" id="basins"></div><h2>Untouched directions</h2><div class="basins" id="untouched"></div></div>
  </section>
  <section class="panel" id="lbwrap"><h2>Leaderboard</h2>
    <p class="note" id="lbnote"></p>
    <div class="tbl"><table id="lb"></table></div>
    <h2>Extra test-time compute (not ranked)</h2>
    <p class="note">Restart, vote or search rows spend more than one sample per problem. DIRECTION.md compares methods at equal generated tokens and with RL given the same procedure; these rows stay here until both are posted.</p>
    <div class="tbl"><table id="lb2"></table></div>
    <h2>Excluded</h2>
    <div class="tbl"><table id="lb3"></table></div>
  </section>
  <section class="panel"><h2>How this map is made</h2>
    <ol class="note" id="how" style="margin:0;padding-left:20px;display:grid;gap:6px"></ol>
  </section>
  <p class="note" id="foot"></p>
</div>
<div class="tip" id="tip" hidden></div>
<script>
const D = __DATA__, S = D.summary;
const pal = ["#2b6cb0","#c05621","#2f855a","#6b46c1","#b83280","#0f7c8c","#975a16","#4a5568","#9b2c2c","#3c6e47","#5a67d8","#a0526e"];
const col = b => pal[b % pal.length];
const f2 = x => (+x).toFixed(2), pct = x => Math.round(100 * x) + "%";
const dirInfo = Object.fromEntries(S.directions.map(d => [d.id, d]));
const stats = [
  ["Basins visited", `${S.basins_visited} / ${S.n_basins}`, `${S.basins_only_possible.length} hold only possible directions`],
  ["Directions pursued", `${S.directions_pursued_both_orders[0]} / ${S.directions_pursued_both_orders[1]}`, `of the judge's possible directions; ${S.directions_untouched.length} untouched`],
  ["Largest basin", pct(S.largest_basin_share), `of ${S.n_board_items} board items; effective basins ${f2(S.effective_basins)}`],
  ["Moves between basins", `${S.moves}`, `${S.moves_to_new_basin} to a basin new for that person`],
  ["Judge checks", `${f2(S.tste_heldout_acc)} vs ${f2(S.tste_shuffled_id_null)}`, `map held-out vs shuffled; order agreement ${S.triplet_order_consistency[0]}/${S.triplet_order_consistency[1]}`],
];
document.getElementById("stats").innerHTML = stats.map(([l, v, s]) => `<div class="stat"><span class="lab">${l}</span><span class="val">${v}</span><span class="sub">${s}</span></div>`).join("");
const ctlOk = S.control.every(c => c.same_group.every(Boolean));
document.getElementById("foot").textContent = `Judge ${D.judge || ""} over ${S.n_board_items} board items and ${S.n_possible} possible directions. Partition stability (ARI, two orders) ${f2(S.partition_ari_order0_vs_order1)}; agreement with k-means on the map (k=${S.kmeans_best_k}) ${f2(S.partition_ari_vs_kmeans)}. Planted control (two exact copies of one item): ${ctlOk ? "passed, same basin in both orders" : "FAILED"}. Possible directions are the judge's own list, not a literature survey.`;
const nodes = D.nodes.filter(n => !n.control_of), board = nodes.filter(n => n.kind !== "possible");
const xs = nodes.map(n => n.x), ys = nodes.map(n => n.y), W = 640, H = 480, P = 24;
const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
const sx = x => P + (x - x0) / ((x1 - x0) || 1) * (W - 2 * P), sy = y => P + (y - y0) / ((y1 - y0) || 1) * (H - 2 * P);
const times = board.map(n => +n.at_ns).sort((a, b) => a - b), tmin = times[0], tmax = times[times.length - 1];
const r = k => ({result: 7, work: 5.5}[k] || 4.5);
const esc = s => String(s ?? "").replace(/[&<>]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]));
let hi = null;
const atOf = Object.fromEntries(board.map(n => [n.id, +n.at_ns]));
const pursued = (id, tcut) => (dirInfo[id]?.items_either || []).some(i => atOf[i] <= tcut);
function draw(frac) {
  const tcut = tmin + (tmax - tmin) * frac;
  const shown = board.filter(n => +n.at_ns <= tcut), vis = new Set(shown.map(n => n.basin));
  const g = [];
  for (const n of nodes.filter(n => n.kind === "possible")) {
    const X = sx(n.x), Y = sy(n.y), s = 6, dim = hi != null && n.basin !== hi;
    g.push(`<path data-id="${n.id}" d="M${X} ${Y - s}L${X + s} ${Y}L${X} ${Y + s}L${X - s} ${Y}Z" fill="var(--panel)" stroke="${pursued(n.id, tcut) ? col(n.basin) : "var(--empty)"}" stroke-width="${pursued(n.id, tcut) ? 1.4 : 2.4}" opacity="${dim ? .2 : 1}"/>`);
  }
  for (const n of shown) {
    const dim = hi != null && n.basin !== hi;
    g.push(`<circle data-id="${n.id}" cx="${sx(n.x).toFixed(1)}" cy="${sy(n.y).toFixed(1)}" r="${r(n.kind)}" fill="${col(n.basin)}" stroke="var(--panel)" stroke-width="1" opacity="${dim ? .2 : .95}"/>`);
  }
  document.getElementById("map").innerHTML = g.join("");
  document.getElementById("tlab").textContent = `${shown.length}/${board.length} items · ${vis.size} basins · ${shown.length ? shown[shown.length - 1].at + " UTC" : ""}`;
  document.getElementById("basins").innerHTML = S.basins.map(b => {
    const nb = shown.filter(n => n.basin === b.basin).length;
    return `<div class="b${hi === b.basin ? " on" : ""}" data-b="${b.basin}"><span class="sw" style="background:${col(b.basin)}"></span><span>${esc(b.name)}${nb === 0 ? '<span class="tag">untouched</span>' : ""}</span><span class="cnt">${b.best_base_pct ? "best " + b.best_base_pct.toFixed(1) + " · " : ""}${nb} items · ${b.possible} ◇</span></div>`;
  }).join("");
}
const byId = Object.fromEntries(D.nodes.map(n => [n.id, n])), tip = document.getElementById("tip"), slider = document.getElementById("t");
document.getElementById("map").addEventListener("mousemove", e => {
  const el = e.target.closest("[data-id]"); if (!el) { tip.hidden = true; return; }
  const n = byId[el.dataset.id];
  tip.innerHTML = `<div class="mono">${n.kind === "possible" ? "possible direction" : esc(n.id) + " · " + esc((n.who || "").split("/")[0]) + " · " + esc(n.at)} · ${esc(D.names[n.basin])}</div><div>${esc(n.text.slice(0, 420))}</div>`;
  tip.hidden = false; tip.style.left = Math.min(e.clientX + 14, innerWidth - 400) + "px"; tip.style.top = (e.clientY + 14) + "px";
});
document.getElementById("map").addEventListener("mouseleave", () => tip.hidden = true);
document.getElementById("basins").addEventListener("mouseover", e => { const b = e.target.closest("[data-b]"); hi = b ? +b.dataset.b : null; draw(slider.value / 100); });
document.getElementById("basins").addEventListener("mouseleave", () => { hi = null; draw(slider.value / 100); });
slider.addEventListener("input", () => draw(slider.value / 100));
let timer = null;
document.getElementById("play").onclick = () => {
  if (timer) { clearInterval(timer); timer = null; return; }
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  slider.value = reduce ? 100 : 0; draw(slider.value / 100);
  if (reduce) return;
  timer = setInterval(() => { slider.value = Math.min(100, +slider.value + 1); draw(slider.value / 100); if (+slider.value >= 100) { clearInterval(timer); timer = null; } }, 60);
};
if (S.leaderboard && S.leaderboard.length) {
  const gap = S.rl_reference_pct - S.best_base_one_sample_pct;
  const fair = S.leaderboard.filter(r => !r.more_tokens && !r.oracle && !r.superseded);
  const extra = S.leaderboard.filter(r => r.more_tokens && !r.oracle && !r.superseded);
  const bad = S.leaderboard.filter(r => r.oracle || r.superseded);
  document.getElementById("lbnote").textContent = `From the board's result posts, as posted (grader v3), ranked within each benchmark: one sample per problem, no reward, no gold answer. MATH-500 best untrained base: ${S.best_base_one_sample_pct.toFixed(1)}%. RL at T 1.0: ${S.rl_reference_pct.toFixed(1)}%. Gap the swarm is closing: ${gap.toFixed(1)} points.`;
  const lo = 40, hi = 100;
  const cfg = r => `${r.model === "rl" ? "<b>RL-Zero-Math</b> (target)" : "Base"} · ${esc(r.method)} · <span class="mono">${esc(r.setting)}</span><div class="bar" style="width:${Math.max(2, (r.score_pct - lo) / (hi - lo) * 100)}%"></div>`;
  const sc = r => `${r.score_pct.toFixed(1)}%${r.correct != null ? '<div class="mono">' + r.correct + "/" + r.n + "</div>" : ""}`;
  const src = r => `<td class="mono" title="${esc(r.quote)}">${esc(r.item)}</td>`;
  const benches = [...new Set(fair.map(r => r.benchmark))];
  document.getElementById("lb").innerHTML = benches.map(bm => { let k = 0; return `<thead><tr><th>#</th><th>Configuration</th><th>Basin of the post</th><th style="text-align:right">${esc(bm)}</th><th>Source</th></tr></thead><tbody>` +
    fair.filter(r => r.benchmark === bm).map(r => `<tr class="${r.model === "rl" ? "rl" : ""}"><td class="num">${r.model === "rl" ? "–" : ++k}</td><td>${cfg(r)}</td><td>${esc(r.basin)}</td><td class="num">${sc(r)}</td>${src(r)}</tr>`).join("") + "</tbody>"; }).join("");
  document.getElementById("lb2").innerHTML = extra.length ? `<thead><tr><th>Configuration</th><th style="text-align:right">Tokens / problem</th><th>RL given the same procedure</th><th style="text-align:right">MATH-500</th><th>Source</th></tr></thead><tbody>` +
    extra.map(r => `<tr><td>${cfg(r)}</td><td class="num">${r.tokens_per_problem ? r.tokens_per_problem.toLocaleString() : "not posted"}</td><td>${r.rl_same_procedure ? "yes" : '<span class="pill">no: compared with RL at one sample</span>'}</td><td class="num">${sc(r)}</td>${src(r)}</tr>`).join("") + "</tbody>" : '<tbody><tr><td class="mono">none posted</td></tr></tbody>';
  document.getElementById("lb3").innerHTML = bad.length ? `<tbody>` + bad.map(r => `<tr class="old"><td>${cfg(r)}</td><td><span class="pill">${r.oracle ? "uses the gold answer to pick: invalid" : "grader " + esc(r.grader) + ", superseded"}</span></td><td class="num">${sc(r)}</td>${src(r)}</tr>`).join("") + "</tbody>" : '<tbody><tr><td class="mono">none</td></tr></tbody>';
} else { document.getElementById("lbwrap").hidden = true; }
const nTrip = S.triplet_order_consistency[1], nAll = S.n_board_items + S.n_possible;
document.getElementById("how").innerHTML = [
  `<b>Basins (colors) come from the model's grouping.</b> The judge sees all ${nAll} items at once and sorts them into groups by approach, twice, with the items in different orders. The two groupings agree (ARI ${f2(S.partition_ari_order0_vs_order1)}); the first is used.`,
  `<b>Positions come from t-STE</b> (a triplet-based relative of t-SNE). The judge answers about ${(2 * nTrip).toLocaleString()} questions of the form "is B or C closer to A?", each asked in both orders (same answer ${Math.round(100 * S.triplet_order_consistency[0] / nTrip)}% of the time). t-STE places the dots so those answers hold: it predicts ${Math.round(100 * S.tste_heldout_acc)}% of held-out answers, against ${Math.round(100 * S.tste_shuffled_id_null)}% with shuffled labels.`,
  `<b>Coverage comes from the model directly.</b> For each possible direction, the judge lists the board items that pursue it.`,
  `<b>Why the map is not clustered.</b> k-means on the 2D map agrees poorly with the judge's groups (ARI ${f2(S.partition_ari_vs_kmeans)}): squeezing many kinds of similarity into 2D keeps who is near whom but cuts clean groups badly. So the map shows nearness and the colors are the judge's groups.`,
].map(x => `<li>${x}</li>`).join("");
document.getElementById("untouched").innerHTML = S.directions.filter(d => !d.items_either.length).map(d => `<div class="b"><span class="sw" style="background:var(--empty)"></span><span>${esc(d.name)}</span><span class="cnt">0 items</span></div>`).join("") || '<span class="mono">none</span>';
draw(1);
</script>
"""
(d / "swarm_map.html").write_text(PAGE.replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
print(d / "swarm_map.html")
