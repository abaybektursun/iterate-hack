"""Five RL runs from one base model: the math reward adds 7.6 points on MATH-500, the code reward 0.2.

The page of one finding, served at /finding/reward-content (copied from .claude/skills/finding-page/template.py; draw()
shows the five rewards as glass columns standing on, or hanging from, a glass board that is the base model, instead of
one bar). It is reached from its tile on /findings, which ICON draws. Study: studies/rlneurons, README.md section
"Reward content test" on branch reward5 (not yet merged to main); board result-edceef.
"""
import json

TITLE = "What the reward grades"
PROBLEM = "Does RL raise math scores whatever the reward grades?"
LINE = "Five RL runs from one base: the math reward adds 7.6 points, the code reward 0.2."

# Every number is copied from the artifact named here (branch reward5; the branch is not merged to main, so the page
# carries the numbers itself). None is typed from memory.
DATA = {
    "artifact": "studies/rlneurons/results/reward5/readout.json",
    "branch": "reward5",
    "commit": "93c0c1c",  # the commit that wrote readout.json on reward5
    "jobs_commit": "3b4ab2a",  # the commit every job ran (each run folder's run.json)
    "n": 500,
    "base": 410,  # cells.base_cue.right_v3 (from results/day1_wdiff, cell T1)
    "base_plain": 224,  # cells.base_plain.right_v3 (cell T3)
    # cells.<key>_cue.right_v3, differences["<key>_cue minus base_cue"], cells.<key>_plain.right_v3
    "rewards": [
        {"key": "math30", "name": "Math", "right": 448, "points": 7.6, "ci": [4.2, 11.0], "plain": 443},
        {"key": "mix30", "name": "Mix", "right": 440, "points": 6.0, "ci": [2.6, 9.4], "plain": 372},
        {"key": "general30", "name": "General", "right": 429, "points": 3.8, "ci": [0.4, 7.0], "plain": 323},
        {"key": "code30", "name": "Code", "right": 411, "points": 0.2, "ci": [-3.4, 3.8], "plain": 360},
        {"key": "if30", "name": "Instructions", "right": 377, "points": -6.6, "ci": [-10.6, -2.6], "plain": 55},
    ],
    # The later Olmo 3.1 releases, same cell: cells.code31_cue, cells.math31_cue, "code31_cue minus base_cue" and
    # "math31_cue minus base_cue"
    "later": {"code": {"right": 450, "points": 8.0, "ci": [4.6, 11.2]}, "math": {"right": 457, "points": 9.4, "ci": [6.2, 12.6]}},
    # README "Reward content test", R2: wrong cue answers of the IF model with a broken answer line, and its score if
    # they were counted right
    "if_broken": 34, "if_wrong": 123, "if_fixed": 411,
}
R = {r["key"]: r for r in DATA["rewards"]}
DATA["states"] = [
    {"name": "Before RL", "note": f"The base model gets {DATA['base']} of {DATA['n']} MATH-500 problems right. AI2 trained five "
                                  "copies of it with RL, each on a different reward."},
    {"name": "After RL", "note": "A column's height is its change in points. A lit column is above the base model with 95 % "
                                 f"confidence. {DATA['if_broken']} of the Instructions model's wrong answers have a broken answer line."},
]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new", "It was known that on Qwen2.5-Math even a random reward gives most of the MATH-500 gain, while OLMo 2 "
     "gains mainly from the true reward (Shao et al., arXiv 2506.10947).",
     ["New here: AI2's five Olmo 3 RL-Zero models share one base and differ only in what the reward grades, so the reward's "
      "effect can be read on one benchmark with everything else fixed.",
      "We found no published MATH-500 score for the instruction-following, general or mix models.",
      f"Wang et al. (arXiv 2610.06851, Table 6) report the math model below the cued base at T 0.6 (75.0 % against 77.9 %). "
      f"At T 1.0 we find it {R['math30']['points']} points above."]],
    ["why", "Why it matters", "The gain that RL adds over the cued base is not a side effect of running RL: the same recipe on "
     f"the same base gives {R['math30']['points']} points or nothing, depending on the reward.",
     [f"The team's weight-difference study used the Code RL model as a control and found that it gives the math gain too "
      f"(board result-4b0d5f). That holds for AI2's later Code model (Olmo 3.1, {DATA['later']['code']['points']:+.1f} points), "
      f"not for the earlier one (Olmo 3, {R['code30']['points']:+.1f}).",
      "Open: what changed between the two Code runs. The model cards do not say."]],
    ["how", "How we know", f"Each model answered the {DATA['n']} MATH-500 problems once at temperature 1.0 and top-p 1.0, "
     "starting from the same three-token opening as the base model, and grader v3 scored the answers.",
     ["The change is right answers minus the base model's, paired by problem, with 95 % intervals from 5,000 bootstrap "
      "resamples over problems: " + ", ".join(f"{r['name']} {r['points']:+.1f} [{r['ci'][0]}, {r['ci'][1]}]" for r in DATA["rewards"]) + ".",
      f"The baseline is the base model with the same opening ({DATA['base']}), not without it ({DATA['base_plain']}): the "
      "opening alone already lifts the base model that far.",
      "Each job loaded the released weights and checked all 355 tensors against the named model. The predictions were "
      "written before the jobs: instruction following was predicted to gain at least half as much as math, and code to "
      "equal math. Both were refuted."]],
    ["limits", "What it does not show", "It does not show that a code reward cannot raise math scores: AI2's later Code run "
     f"(Olmo 3.1) gets {DATA['later']['code']['right']}, {DATA['later']['code']['points']} points above the base model "
     f"[{DATA['later']['code']['ci'][0]}, {DATA['later']['code']['ci'][1]}].",
     [f"Without the opening the base model gets {DATA['base_plain']}, and every reward but instruction following lifts it by "
      "20 to 44 points: " + ", ".join(f"{r['name']} {r['plain']}" for r in DATA["rewards"]) + ".",
      f"Part of the instruction-following loss is the answer line: {DATA['if_broken']} of its {DATA['if_wrong']} wrong answers "
      f"end in \"Answer: Answer\" or an empty \"Answer:\". Counted right, it scores {DATA['if_fixed']}, level with the base model.",
      "It is one sample per problem, one benchmark and one run per reward. We did not measure how much math each training set "
      "holds; the model cards say Mix holds math, code and instruction data, and General holds chat queries graded by a "
      "language model."]],
    ["run", "How to reproduce it", "Ten H100 jobs of 2 to 35 minutes each, at commit " + DATA["jobs_commit"] + ", and a "
     "readout that runs on a laptop.",
     ["Each cell: python -m studies.rlneurons.jobs.merge_weights --other math30 --alpha 1 (one key per model), then jobs.run_cell --prompt cue "
      "--set math500 --temperature 1.0 --top-p 1.0. The full command is in each run folder's run.json.",
      "studies/rlneurons/analysis/reward5.py writes " + DATA["artifact"] + ", on branch " + DATA["branch"] + " (commit "
      + DATA["commit"] + "), not yet merged to main.",
      "The base model's two numbers come from studies/rlneurons/results/day1_wdiff/readout.json (cells T1 and T3)."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with one post per reward, as long as its change in points: lit where the 95 % interval is
# above zero, plain otherwise, and hanging below the slab where the change is a loss.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 34, th = 5, top = th / 2, g = __GAIN__, lit = __LIT__, m = Math.max(...g.map(Math.abs));
  return kit.slab(a, b, th) + g.map((p, i) => {
    const u = a * (-.72 + .36 * i), w = 30 * p / m;
    if (p < 0) return kit.line(kit.at(u, -b * .3, -top), kit.at(u, -b * .3, -top + w), 3, "plain", .8);
    return kit.line(kit.at(u, 0, top), kit.at(u, 0, top + Math.max(w, 1.5)), lit[i] ? 3.2 + .2 * Math.sin(t * .6 + i) : 3, lit[i] ? "lit" : "plain");
  }).join("");
}""".replace("__GAIN__", json.dumps([r["points"] for r in DATA["rewards"]])).replace(
    "__LIT__", json.dumps([r["ci"][0] > 0 for r in DATA["rewards"]]))

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
.board .face { opacity: .72; }
.board .body { opacity: .85; }
.wash { fill: var(--blue); opacity: calc(var(--wash) * var(--q, 0)); pointer-events: none; }
.gain { font-weight: 640; text-anchor: middle; font-size: 34px; }
.gain.loss { fill: var(--red); }
.gain.flat { fill: var(--mute); }
.tick { font-weight: 580; text-anchor: middle; font-size: 23px; }
.count { fill: var(--mute); font-weight: 480; text-anchor: middle; font-size: 21px; }
.base { font-size: 21px; }
.base tspan + tspan { fill: var(--mute); }
.axis { fill: var(--mute); font-weight: 500; font-size: 20px; }
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
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <div class="stage" id="stage">
    <svg id="svg" viewBox="0 0 840 590" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="Before or after RL"></div>
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
const S = { state: 0, open: null, q: 0, from: 0, t0: 0, grow: 0, cols: [] };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q, ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;

/* The picture: a glass board seen from slightly above is the base model with the opening cue (410 of 500 right). Each
   reward is a glass column on it, as high as its change in points after RL: above the board for a gain, hanging below
   it for a loss. Before RL every column is flat on the board. A column is lit when its 95 % interval is above zero. */
const RAD = Math.PI / 180, CX = 360, CY = 286, EL = 18, PITCH = 122, HALF = 38, TALL = 160, FLAT = 2.5, TH = 10;
const EU = 2 * PITCH + HALF + 34, EV = HALF + 44, NAMES = 530, COUNTS = 558;
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
const rect = (u0, u1, v0, v1, w) => [[u0, v0], [u1, v0], [u1, v1], [u0, v1]].map(([u, v]) => proj(u, v, w));
const K = TALL / Math.max(...D.rewards.map(r => Math.abs(r.points)));  // pixels per point
const signed = p => (p > 0 ? "+" : p < 0 ? "−" : "") + Math.abs(p).toFixed(1);

function build() {
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  let above = "", labels = "";
  D.rewards.forEach((r, i) => {
    S.cols.push({ i, r, u: (i - 2) * PITCH, h: r.points * K, lit: r.ci[0] > 0 });
    const g = `<g id="c${i}"><path class="body" id="b${i}"/><path class="wash" id="e${i}"/><path class="face" id="f${i}"/>` +
      `<path class="wash" id="w${i}"/><path class="rim" id="r${i}"/></g>`;
    above += g;  // place() moves a column under the board while it hangs below it
    labels += `<text class="gain${r.ci[1] < 0 ? " loss" : r.ci[0] > 0 ? "" : " flat"}" id="g${i}"></text>` +
      `<text class="tick" id="n${i}" y="${NAMES}">${r.name}</text><text class="count" id="k${i}" y="${COUNTS}"></text>`;
  });
  $("svg").innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.3, "var(--blue)", .18)}${stop(.7, "var(--blue)", .05)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .18)}${stop(1, "var(--ink)", 0)}</radialGradient></defs>` +
    `<g class="atmo"><ellipse cx="${CX}" cy="${CY}" rx="420" ry="250" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${CX + 24}" cy="${CY + 40}" rx="380" ry="90" fill="url(#shade)"/></g>` +
    `<g class="board" id="board"><path class="body" id="board-side"/><path class="face" id="board-face"/><path class="rim" id="board-rim"/></g>` +
    above + labels +
    `<text class="base" id="base"><tspan id="base1" style="font-weight:600">Base model</tspan><tspan id="base2">${D.base} of ${D.n}</tspan></text>` +
    `<text class="axis" x="20" y="34">Change in MATH-500 accuracy after RL, in percentage points</text>`;
  S.cols.forEach(o => { o.el = Object.fromEntries(["c", "b", "e", "f", "w", "r", "g", "n", "k"].map(k => [k, $(k + o.i)])); });
}
function place() {
  const q = S.q, top = rect(-EU, EU, -EV, EV, 0), d = path(top);
  $("board-side").setAttribute("d", path(hull([...top, ...rect(-EU, EU, -EV, EV, -TH)])));
  $("board-face").setAttribute("d", d); $("board-rim").setAttribute("d", d);
  S.cols.forEach(o => {
    let h = o.h * q * S.grow;
    if (h > -FLAT && h < FLAT) h = FLAT;  // before RL every column is a flat tile on the board
    if ((h < 0) !== !!o.down) { o.down = h < 0; o.down ? $("board").before(o.el.c) : $("board").after(o.el.c); }  // a loss is drawn behind the board
    // Seen from above, a column's visible end is its top: the far end for a gain, the foot under the board for a loss.
    const end = rect(o.u - HALF, o.u + HALF, -HALF, HALF, h), foot = rect(o.u - HALF, o.u + HALF, -HALF, HALF, 0);
    const side = path(hull([...end, ...foot])), face = path(h >= 0 ? end : foot);
    o.el.b.setAttribute("d", side); o.el.e.setAttribute("d", side);
    o.el.f.setAttribute("d", face); o.el.w.setAttribute("d", face); o.el.r.setAttribute("d", h >= 0 ? face : side);  // a loss is outlined whole
    o.el.c.style.setProperty("--q", o.lit ? f(q) : 0);
    const shown = Math.abs(1 - 2 * q) * S.grow, after = q >= .5;
    const g = after ? signed(o.r.points) : "", k = String(after ? o.r.right : D.base);
    if (o.el.g.textContent !== g) o.el.g.textContent = g;
    if (o.el.k.textContent !== k) o.el.k.textContent = k;
    const p = h >= 0 ? proj(o.u, HALF, h) : proj(o.u, -HALF, h), x = f(proj(o.u, 0, h)[0]);
    o.el.g.setAttribute("x", x); o.el.g.setAttribute("y", f(h >= 0 ? p[1] - 16 : p[1] + 40)); o.el.g.setAttribute("opacity", f(shown));
    const nx = f(proj(o.u, -EV, -TH)[0]);
    o.el.n.setAttribute("x", nx); o.el.k.setAttribute("x", nx); o.el.k.setAttribute("opacity", f(shown));
  });
  const b = proj(EU, 0, -TH / 2);
  $("base1").setAttribute("x", f(b[0] + 18)); $("base1").setAttribute("y", f(b[1] - 2));
  $("base2").setAttribute("x", f(b[0] + 18)); $("base2").setAttribute("y", f(b[1] + 22));
}
/* One frame: the view sways slowly and leans toward the pointer, the board settles in once on load, and a change of
   the switch moves every column to its new height. With reduced motion the page shows one still frame. */
function frame(now) {
  const t = now / 1000;
  V.px += (V.tx - V.px) * .06; V.py += (V.ty - V.py) * .06;
  V.yaw = 2.5 * Math.sin(t * .25) + 3 * V.px; V.el = EL + 1.2 * Math.sin(t * .19 + 1) - 2 * V.py;
  S.grow = ease(Math.min(1, t / 1.3));
  S.q = mix(S.from, S.state, ease(Math.min(1, (now - S.t0) / 1100)));
  place();
  if (!still.matches) requestAnimationFrame(frame);
}
function draw() {  // the switch, the note and the label follow the state; the columns follow in frame()
  const st = D.states[S.state];
  $("svg").setAttribute("aria-label", S.state === 0
    ? `MATH-500, before RL: the base model gets ${D.base} of ${D.n} right`
    : `MATH-500, change in points over the base model after RL with each reward: ` +
      D.rewards.map(r => `${r.name} ${signed(r.points)} (95 % interval ${r.ci[0]} to ${r.ci[1]}), ${r.right} of ${D.n}`).join("; "));
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
