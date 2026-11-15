"""Most of the RL gain on MATH-500 is on problems the base model already solves in some of 4 samples.

The page of one finding, served at /finding/rl-reliability (copied from .claude/skills/finding-page/template.py; draw()
shows the joint table of right answers of 4 as glass columns instead of one bar). It is reached from its tile on
/findings, which ICON draws. Study: studies/rlneurons (README.md "Gap anatomy" and "Checks or per-step error";
board result-afc423 and result-855858).
"""
import json

# Every number is copied from the artifacts named here. None is typed from memory.
DATA = {
    "artifact": "studies/rlneurons/results/anatomy/math500-01/readout.json",
    "commit": "2cda3ed",
    "checks": "studies/rlneurons/results/checks/math500-01/readout.json",
    "checks_judge": "studies/rlneurons/results/checks/judge-01/readout.json",
    "checks_commit": "b155bc1",
    # a_joint.table_rows_base_k_cols_rl_k: problems by right answers of 4; row = base with cue, column = RL
    "table": [[16, 4, 8, 3, 2], [2, 2, 3, 7, 10], [0, 1, 6, 4, 17], [0, 0, 0, 12, 86], [0, 0, 0, 7, 310]],
    "base_right": 1642, "rl_right": 1840, "samples": 2000,  # a_joint.base_right_samples, rl_right_samples
}
T = DATA["table"]
DATA["gap"] = DATA["rl_right"] - DATA["base_right"]  # 198 right answers
ROW = [sum(n * (r - b) for r, n in enumerate(row)) / DATA["gap"] for b, row in enumerate(T)]  # share of the gain by base k
SOME = round(100 * (1 - ROW[0]))  # the share in problems the base model solves at least once in 4
CELL = round(100 * T[3][4] / DATA["gap"])  # the share of the cell "base 3 of 4, RL 4 of 4"
PROBLEMS = sum(map(sum, T))

TITLE = "Reliability, not new problems"
PROBLEM = "Does RL training solve new math problems, or the same ones more reliably?"
LINE = f"{SOME} % of the RL gain is on problems the base model already solves sometimes."  # also the sentence on its tile

# What the reader switches between. The first is shown on load: start from the problem, not from the answer.
DATA["states"] = [
    {"name": "Problems", "note": f"The {PROBLEMS} problems, by how many of 4 tries each model gets right. A column's height is its number of problems."},
    {"name": "RL gain", "note": f"Where RL's {DATA['gap']} extra right answers come from. The lit columns are problems the base model "
                                f"already solves at least once in 4 tries: {SOME} %."},
]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new", "It was known from many samples per problem that a base model's answers cover what its RL model solves "
     "(Yue et al., arXiv 2504.13837, Table 2: pass@128 of the base is above the RL model's).",
     [f"New here: 4 samples locate the gain per problem. One cell, the {T[3][4]} problems the base model gets right 3 times of 4 "
      f"and RL 4 times of 4, holds {CELL} % of it.",
      "New here: RL writes more checking words (13.1 against 9.5 per 1,000 tokens), but they do not separate right answers "
      "from wrong ones: right answers of the base model have 0.08 more per 1,000 tokens at matched length (95 % interval -0.64 to 0.77).",
      "What differs is the number of wrong steps left in finished answers: 0.015 first wrong steps per 1,000 tokens for RL "
      "against 0.038 for the base model."]],
    ["why", "Why it matters", "A method without RL does not have to teach the base model new mathematics for most of the gain: "
     "it has to remove the occasional wrong answer on problems the model usually solves.",
     ["More checking text is unlikely to do that: checks in the base model's answers follow its wrong steps and repeat them.",
      f"Still open: the {100 - SOME} % of the gain on problems the base model never solved in 4 tries, and whether the same split "
      "holds on the 328 harder problems."]],
    ["how", "How we know", f"Each model answered the {PROBLEMS} MATH-500 problems 4 times at temperature 1.0, and every problem was "
     "placed by how many of its 4 answers each model got right (grader v3).",
     [f"The base model (Olmo 3 7B with an opening cue) has {DATA['base_right']:,} right answers of {DATA['samples']:,} and the RL model "
      f"(Olmo 3.1 RL-Zero-Math) {DATA['rl_right']:,}. A cell's share of the gain is its problems times its difference in right answers, over {DATA['gap']}.",
      f"Baseline: if every problem were equally hard, 0.5 problems would be missed by the base model 4 times of 4; {sum(T[0])} are. "
      "Scored on a held-out sample, the problems the base model misses in its other three samples hold 14 % of the gain (95 % interval 5 to 23).",
      "In 6 of 11 base-model slips read by hand a check follows and repeats the slip: one answer writes 150 + 130 + 150 + 130 = 580 "
      "three times under \"let me verify\" (the sum is 560). A checking word follows 46 of 52 located wrong steps within 500 tokens "
      "(88 %), which is the rate at random positions (87 %)."]],
    ["limits", "What it does not show", f"It does not show that RL teaches nothing new: {100 - SOME} % of the gain (95 % interval 11 to 27) "
     f"is on the {sum(T[0])} problems the base model missed 4 times of 4, and RL solves {T[0][4]} of them 4 times of 4.",
     ["It is one benchmark, one pair of models, 4 samples per problem and one grader. The harder problems have not been split this way.",
      "The wrong steps were located and labelled by judges that are subagents of the agent that ran the study, with a fixed rubric. "
      "Two passes agree on 44 of 45 answers, but both are the same model, and the hand reads had one reader who knew the model.",
      "A second session recomputed the table from the stored rows and got the same counts (board result-afc423). Not measured: "
      "whether RL makes fewer errors or resolves a noticed conflict right more often."]],
    ["run", "How to reproduce it", "Both analyses run on a laptop, from the stored samples of the two generation jobs named in run.json.",
     ["The table: studies/rlneurons/analysis/anatomy.py --base <run> --rl <run> --out <folder> (commit " + DATA["commit"] + "). "
      "Its numbers are in " + DATA["artifact"] + ".",
      "The checking words: studies/rlneurons/analysis/checks.py stats, then prep and score for the judged events (commit "
      + DATA["checks_commit"] + "). Its numbers are in " + DATA["checks"] + " and " + DATA["checks_judge"] + ".",
      "The slips read by hand are in studies/rlneurons/results/checks/math500-01/hand_reads.json."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with one post per row of the table that holds gain (base right 0, 1, 2, 3 times of 4), as high
# as the row's share of the gain. The first post, problems the base model never solves, is plain; the others are lit.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, top = th / 2, share = __ROW__;
  return kit.slab(a, b, th) + share.map((s, i) => {
    const u = a * (-.6 + .4 * i);
    return kit.line(kit.at(u, 0, top), kit.at(u, 0, top + 64 * s), i ? 3.2 + .2 * Math.sin(t * .6 + i) : 3.2, i ? "lit" : "plain", i ? 1 : .7);
  }).join("");
}""".replace("__ROW__", json.dumps([round(s, 3) for s in ROW[:4]]))

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the light of architecture.py. Dark is the hero: lit glass in a dark room. Light is the same object as
   white porcelain on a cool grey table, with a cast shadow in place of the glow. The light comes from the upper left.
   --wash is how strongly a column takes the accent when it is lit. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --wash: .3;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --wash: .42;
  }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 27vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0; height: 100vh; min-height: 620px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture, and the one control that changes it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg { width: 100%; max-height: 64vh; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 104%; }
.atmo, .shade { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.body { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; stroke-linejoin: round; }
.face { fill: url(#body) var(--sheet); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1.4; stroke-linejoin: round; }
.wash { fill: var(--blue); opacity: calc(var(--wash) * var(--q, 0)); pointer-events: none; }
.empty .body, .empty .face { opacity: .45; }
.empty .rim { opacity: .3; }
.num { font-weight: 620; text-anchor: middle; }
.num.loss { fill: var(--red); }
.tick { fill: var(--mute); font-weight: 560; text-anchor: middle; }
.axis { fill: var(--mute); font-weight: 500; }
.switch { display: inline-flex; align-self: center; margin-top: 18px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.note { align-self: center; margin: 12px 0 0; color: var(--mute); font-size: 15px; text-align: center; max-width: 60ch; min-height: 3em; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
@keyframes fade { from { opacity: 0; } }
svg { animation: fade 1s both; }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 14px; padding: 0; }
  .pane { order: 4; margin-top: 14px; }
  svg { max-height: none; }
  .note { min-height: 4.5em; }
}
@media (prefers-reduced-motion: reduce) {
  svg { animation: none; }
  .switch button, .more button { transition: none; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <div class="stage" id="stage">
    <svg id="svg" viewBox="0 0 760 650" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="What the columns show"></div>
    <p class="note" id="note" aria-live="polite"></p>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const S = { state: 0, open: null, q: 0, from: 0, t0: 0, grow: 0, cells: [], ticks: [] };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q, ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;

/* The picture: the table of problems by right answers of 4, as glass columns on a glass board seen from slightly above.
   A row is the base model's count (0 at the front), a column the RL model's (0 at the left). With "Problems" a column
   is as high as its number of problems. With "RL gain" it is as high as its share of the gain, problems x (RL right -
   base right) / gap, and the columns of problems the base model solves at least once are lit. */
const RAD = Math.PI / 180, CX = 400, CY = 322, EL = 52, PITCH = 100, HALF = 42, TALL = 200, FLAT = 3;
const V = { yaw: 0, el: EL, px: 0, py: 0, tx: 0, ty: 0 };  // the view: a slow sway, plus a few degrees toward the pointer
function proj(u, v, w) {  // u to the right, v away from the viewer, w up; what is near is larger
  const a = V.yaw * RAD, e = V.el * RAD, x = u * Math.cos(a) - v * Math.sin(a), d = u * Math.sin(a) + v * Math.cos(a);
  const k = 900 / (900 + d * .4);
  return [CX + x * k, CY - k * (d * Math.sin(e) + w * Math.cos(e)), k];
}
function hull(p) {  // the silhouette of a convex body is the convex hull of its projected points
  p = [...p].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const turn = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const half = list => {
    const out = [];
    for (const q of list) { while (out.length > 1 && turn(out[out.length - 2], out[out.length - 1], q) <= 0) out.pop(); out.push(q); }
    out.pop();
    return out;
  };
  return [...half(p), ...half(p.reverse())];
}
const path = p => "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
const square = (u, v, r, w) => [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => proj(u + i * r, v + j * r, w));
const maxN = Math.max(...D.table.flat()), share = (b, r) => D.table[b][r] * (r - b) / D.gap;
const maxShare = Math.max(...D.table.flatMap((row, b) => row.map((n, r) => share(b, r))));
const pct = s => `${Math.round(s * 100)} %`.replace("-", "−");

function build() {
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  let cells = "";
  for (let b = 4; b >= 0; b--) for (let r = 0; r < 5; r++) {  // the back row first, so that a near column hides a far one
    const n = D.table[b][r], s = share(b, r), id = `${b}${r}`;
    S.cells.push({ id, u: (r - 2) * PITCH, v: (b - 2) * PITCH, lit: s > 0 && b > 0,
      h: [n ? Math.max(FLAT, TALL * n / maxN) : FLAT, s > 0 ? Math.max(FLAT, TALL * s / maxShare) : FLAT],
      text: [n ? String(n) : "", s ? pct(s) : ""], loss: s < 0 });
    cells += `<g id="c${id}"${n ? "" : ' class="empty"'}><path class="body" id="b${id}"/><path class="wash" id="e${id}"/><path class="face" id="f${id}"/>` +
      `<path class="wash" id="w${id}"/><path class="rim" id="r${id}"/><text class="num" id="n${id}"></text></g>`;
  }
  for (let k = 0; k < 5; k++) S.ticks.push({ id: "tb" + k, u: -2 * PITCH - HALF - 44, v: (k - 2) * PITCH, k }, { id: "tr" + k, u: (k - 2) * PITCH, v: -2 * PITCH - HALF - 56, k });
  $("svg").innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.3, "var(--blue)", .2)}${stop(.7, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient></defs>` +
    `<g class="atmo"><ellipse cx="${CX}" cy="${CY - 20}" rx="440" ry="330" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${CX + 22}" cy="${CY + 50}" rx="400" ry="290" fill="url(#shade)"/></g>` +
    `<path class="body" id="board-side"/><path class="face" id="board-face"/><path class="rim" id="board-rim"/>` + cells +
    S.ticks.map(o => `<text class="tick" id="${o.id}">${o.k}</text>`).join("") +
    `<text class="axis" id="axis-b" style="text-anchor:end"><tspan id="axis-b1">Base model,</tspan><tspan id="axis-b2">right in 4 tries</tspan></text>` +
    `<text class="axis" id="axis-r" style="text-anchor:middle">After RL, right in 4 tries</text>`;
  S.cells.forEach(o => { o.el = Object.fromEntries(["c", "b", "e", "f", "w", "r", "n"].map(k => [k, $(k + o.id)])); });
  S.ticks.forEach(o => { o.el = $(o.id); });
}
function place() {
  const q = S.q, edge = 2.5 * PITCH + 14, top = square(0, 0, edge, 0), d = path(top);
  $("board-side").setAttribute("d", path(hull([...top, ...square(0, 0, edge, -12)])));
  $("board-face").setAttribute("d", d); $("board-rim").setAttribute("d", d);
  S.cells.forEach(o => {
    const h = mix(o.h[0], o.h[1], q) * S.grow, up = square(o.u, o.v, HALF, h), side = path(hull([...up, ...square(o.u, o.v, HALF, 0)])), face = path(up);
    const c = proj(o.u, o.v, h), text = o.text[q < .5 ? 0 : 1];
    o.el.b.setAttribute("d", side); o.el.e.setAttribute("d", side);
    o.el.f.setAttribute("d", face); o.el.w.setAttribute("d", face); o.el.r.setAttribute("d", face);
    o.el.c.style.setProperty("--q", o.lit ? f(q) : 0);
    if (o.el.n.textContent !== text) { o.el.n.textContent = text; o.el.n.classList.toggle("loss", q >= .5 && o.loss); }
    o.el.n.setAttribute("x", f(c[0])); o.el.n.setAttribute("y", f(c[1] + 9 * c[2]));
    o.el.n.setAttribute("font-size", f(25 * c[2])); o.el.n.setAttribute("opacity", f(Math.abs(1 - 2 * q) * S.grow));
  });
  S.ticks.forEach(o => {
    const c = proj(o.u, o.v, 0);
    o.el.setAttribute("x", f(c[0])); o.el.setAttribute("y", f(c[1] + 8 * c[2])); o.el.setAttribute("font-size", f(24 * c[2]));
  });
  const tb = proj(-2 * PITCH - HALF - 30, 2 * PITCH + HALF + 30, 0), tr = proj(0, -2 * PITCH - HALF - 56, 0);
  $("axis-b1").setAttribute("x", f(tb[0])); $("axis-b1").setAttribute("y", f(tb[1] - 44));
  $("axis-b2").setAttribute("x", f(tb[0])); $("axis-b2").setAttribute("y", f(tb[1] - 20));
  $("axis-b").setAttribute("font-size", 20);
  $("axis-r").setAttribute("x", f(tr[0])); $("axis-r").setAttribute("y", f(tr[1] + 52)); $("axis-r").setAttribute("font-size", 22);
}
/* One frame: the view sways slowly and leans toward the pointer, the columns rise once on load, and a change of the
   switch moves every column to its new height. With reduced motion the page shows one still frame. */
function frame(now) {
  const t = now / 1000;
  V.px += (V.tx - V.px) * .06; V.py += (V.ty - V.py) * .06;
  V.yaw = 2 * Math.sin(t * .25) + 2.5 * V.px; V.el = EL + Math.sin(t * .19 + 1) - 2 * V.py;
  S.grow = ease(Math.min(1, t / 1.3));
  S.q = mix(S.from, S.state, ease(Math.min(1, (now - S.t0) / 900)));
  place();
  if (!still.matches) requestAnimationFrame(frame);
}
function draw() {  // the switch, the note and the label follow the state; the columns follow in frame()
  const st = D.states[S.state];
  $("svg").setAttribute("aria-label", S.state === 0
    ? `Problems by right answers in 4 tries: the base model has 0 to 4 right on ${D.table.map(r => r.reduce((a, b) => a + b)).join(", ")} problems`
    : `Share of the RL gain by the base model's right answers in 4 tries, 0 to 4: ${D.table.map((row, b) => pct(row.reduce((a, n, r) => a + share(b, r), 0))).join(", ")}`);
  $("note").textContent = st.note;
  $("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}" aria-pressed="${i === S.state}">${s.name}</button>`).join("");
}
function choose(i) {
  if (i === S.state) return;
  S.from = S.q; S.state = i; S.t0 = still.matches ? -1e9 : performance.now();
  draw();
  if (still.matches) { S.grow = 1; S.q = i; place(); }
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${p[1]}</h2><button class="close" data-open="">Close</button></div><p class="lead">${p[2]}</p>` +
      `<ul class="facts">${p[3].map(f => `<li>${f}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${p[1]}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
function fromHash() { const h = location.hash.slice(1); S.open = C.panels.some(p => p[0] === h) ? h : null; pane(); }
document.addEventListener("click", e => {
  const s = e.target.closest("[data-state]"), o = e.target.closest("[data-open]");
  if (s) { choose(Number(s.dataset.state)); document.querySelector(`[data-state="${S.state}"]`).focus(); }
  if (o) { history.pushState(null, "", o.dataset.open ? "#" + o.dataset.open : location.pathname); fromHash(); }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) { history.pushState(null, "", location.pathname); fromHash(); }
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") choose((S.state + 1) % D.states.length);
});
addEventListener("hashchange", fromHash);
$("stage").addEventListener("pointermove", e => {  // the view leans a few degrees toward a mouse, and settles back
  if (e.pointerType !== "mouse") return;
  const r = $("stage").getBoundingClientRect();
  V.tx = 2 * (e.clientX - r.left) / r.width - 1; V.ty = 2 * (e.clientY - r.top) / r.height - 1;
});
$("stage").addEventListener("pointerleave", () => { V.tx = V.ty = 0; });
$("problem").textContent = C.problem;
$("say").innerHTML = C.line.replace(/(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
build();
draw();
fromHash();
if (still.matches) { S.grow = 1; place(); } else requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}))
