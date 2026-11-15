"""Eight directions per weight matrix of the RL weight change lift the untrained model from 45 % to 85 % on MATH-500 (224 to 427 of 500).

The page of one finding, served at /finding/eight-directions (view.py serves every tools/finding_<slug>.py). The
picture is one weight matrix as a glass slab seen from slightly above, with eight lines across it for the eight
directions, and the score on a scale under it. The reader switches between four conditions (address
/finding/eight-directions#<condition>, arrow keys) and watches the lines and the score change. The rules are in
.claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py (.claude/skills/site-ui/SKILL.md).
"""
import json

UNLISTED = True  # served at its address, but left out of the links in the site header (view.py)

TITLE = "Eight directions"  # the link text in the site header and the browser tab
PROBLEM = "What did reward training change inside the model?"
LINE = "Eight directions per matrix are enough: the untrained model rises from 45% to 85% on MATH-500."

# Every number is copied from the artifact named here. None is typed from memory.
RESULTS = "studies/rlneurons/results/wsp1/"
DATA = {
    "artifact": RESULTS + "readout.json",  # cells of full500; the two released models from results/rln4/grader_v3/readout.json
    "runs": RESULTS + "full500/",  # one folder per cell, <label>_<prompt>-01/metrics.json
    "commit": "1417dbf8f09bb4fcffd273eff18dabdeb76debff",  # full500/top8_plain-01/run.json
    "metric": "Share of the 500 MATH-500 problems answered right, one sample at temperature 1.0",
    "unit": "%",
    "max": 100,
    # What the reader switches between. The first is shown on load: start from the problem, not from the answer.
    # value = right of 500 as a rounded percentage; right is copied from the cell named in "cell".
    "states": [
        {"key": "untrained", "name": "Untrained", "right": 224, "n": 500, "cell": "studies/rlneurons/results/rln4/grader_v3/readout.json cells.base_plain_1.0", "note": "The slab is one weight matrix. Each line is one direction in it."},
        {"key": "random", "name": "8 random directions", "right": 197, "n": 500, "cell": "full500/rand8_plain",
         "note": "A control: eight random directions of the same size in each matrix."},
        {"key": "rl-directions", "name": "8 RL directions", "right": 427, "n": 500, "cell": "full500/top8_plain",
         "note": "The words are what two of these directions point at in one matrix of layer 29."},
        {"key": "rl-trained", "name": "RL-trained", "right": 463, "n": 500, "cell": "studies/rlneurons/results/rln4/grader_v3/readout.json cells.rl_1.0",
         "note": "The model after reinforcement learning with a math reward."},
    ],
    # The strongest baseline or the target, drawn as a line. Never compare against zero.
    "reference": {"name": "RL-trained", "right": 463, "n": 500},
    # The edit of the cell top8_plain: k directions in n_edited matrices, their share of the squared norm of the RL
    # change, and the norm of the addition over the norm of the weights (edit.share and edit.add_rel).
    "edit": {"source": RESULTS + "full500/top8_plain-01/metrics.json", "k": 8, "n_edited": 224, "n": 500, "share": 0.0982, "add_rel": 0.000741},
    "removed": {"cell": "screen100/bulk_plain", "value": 91, "n": 100},  # the RL-trained model without these directions, first 100 problems
    "one": {"cell": "screen100/top1_plain", "value": 42, "n": 100},  # one direction per matrix, first 100 problems
    # What three ends of two directions read as through the output layer: rows of anatomy-01/readout.json with this
    # name and delta. direction counts from 0; toks are the first tokens of the row, label is what the page shows.
    "words": {"source": RESULTS + "anatomy-01/readout.json", "name": "model.layers.29.mlp.down_proj.weight", "delta": "rl_math",
              "rows": [
                  {"direction": 1, "sign": "+", "toks": ["Okay", " consider", " considering"], "label": "Okay, consider"},
                  {"direction": 1, "sign": "-", "toks": [" perhaps", " maybe"], "label": "perhaps, maybe"},
                  {"direction": 2, "sign": "+", "toks": [" WAIT", "wait", ".Wait", "WAIT", " wait", " Wait"], "label": "Wait"},
              ]},
}
for _s in DATA["states"] + [DATA["reference"]]:
    _s["value"] = round(100 * _s["right"] / _s["n"])
_value = {s["key"]: s["value"] for s in DATA["states"]}
_edit = DATA["edit"]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["how", "How we know",
     f"We added only the {_edit['k']} strongest directions of the RL weight change in each of {_edit['n_edited']} weight matrices to the "
     f"untrained model and scored it on all {_edit['n']} MATH-500 problems.",
     [f"Eight random directions of the same size score {_value['random']} %, so the size of the edit is not the cause.",
      f"The edit is {_edit['add_rel'] * 100:.2f} % of the size of the weights and {_edit['share'] * 100:.1f} % of the full RL change.",
      "Closest published result: Spectral Rewiring (arXiv 2607.03065) keeps the RL gain with a compact part of the update on models that include this pair. This page tests 8 directions against a matched random control."]],
    ["limits", "What it does not show",
     "The directions were read from the RL-trained weights, so this is not yet a way to get the gain without reward.",
     [f"RL with these 8 directions removed still scores {DATA['removed']['value']} of the first {DATA['removed']['n']} problems: the change is stored many times over.",
      f"One direction per matrix is not enough: {DATA['one']['value']} of the first {DATA['one']['n']} problems.",
      "The words are what the directions point at through the output layer rather than proof of what they compute."]],
    ["run", "How to reproduce it",
     f"Two commands on one GPU reproduce the {_value['rl-directions']} %: the first writes the edited weights and the second scores them.",
     ["studies/rlneurons/jobs/wsp_edit.py --recipe top8 --dir /tmp/theta",
      "studies/rlneurons/jobs/run_cell.py --model-path /tmp/theta --model-label top8 --prompt plain --set math500 --temperature 1.0 "
      "--top-p 1.0 --seed 180000000 --commit $(git rev-parse HEAD)",
      "The run used commit " + DATA["commit"] + ". Its numbers are in " + RESULTS + "."]],
]

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
/* The tokens and the light of architecture.py. Dark is the hero: one lit glass slab in a dark room. Light is the same
   slab as white porcelain on a cool grey table, with a cast shadow in place of the glow. The light comes from the
   upper left in both. --wash and --edge are how strongly the slab and its edge take the accent when it is lit. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue); --wash: .13; --edge: .3;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff; --wash: .2; --edge: .55;
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
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
.atmo, .shade, .spec, .bloom, .wash, .edge { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.spec { opacity: var(--spec); }
.bloom { opacity: var(--bloom); }
.wash { opacity: var(--wash); }
.edge { opacity: var(--edge); }
.body { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; stroke-linejoin: round; }
.face { fill: url(#body) var(--sheet); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1.7; stroke-linejoin: round; }
.wash path, .edge path, .halo { fill: var(--blue); }
.plain { fill: url(#fade-n) var(--ink); }
.rest { fill: url(#fade-b) var(--blue); }
.lit { fill: url(#fade-c) var(--core); }
.word { font-weight: 560; paint-order: stroke fill; stroke: var(--paper); stroke-width: 6px; stroke-linejoin: round; }
.axis { stroke: var(--faint); stroke-width: 1.5; opacity: .5; }
.level { stroke: var(--ink); stroke-width: 2; stroke-linecap: round; }
.head { fill: var(--ink); }
.ref { stroke: var(--ink); stroke-width: 1.5; }
.tick { fill: var(--faint); font-weight: 500; }
.reftext { fill: var(--mute); font-weight: 600; text-anchor: end; }
.value { font-weight: 330; letter-spacing: -.03em; text-anchor: middle; font-stretch: 100%; }
.switch { display: inline-flex; align-self: center; margin-top: 18px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.note { align-self: center; margin: 12px 0 0; color: var(--mute); font-size: 15px; text-align: center; max-width: 60ch; min-height: 1.5em; }

/* One drawn entrance */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .face, .enter .body { animation: fade 1.3s .15s both; }
.enter .plain, .enter .scale { animation: fade .7s .7s both; }

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
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; }
  .pane { order: 4; margin-top: 14px; }
  svg { max-height: none; }
  .switch { display: grid; grid-template-columns: 1fr 1fr; align-self: stretch; border-radius: 24px; }
  .switch button { text-align: center; padding: 10px 6px; }
  .note { min-height: 3em; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button { transition: none; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">How it works</a>
    <a href="" aria-current="page">__TITLE__</a>
  </header>
  <div class="stage" id="stage">
    <svg id="svg" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="Condition"></div>
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
const S = { state: 0, open: null, g: null, el: null, out: null, words: [], cur: null, from: null, goal: null, t0: 0, t: 0, shown: "" };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1), h = n => n.toFixed(2), mix = (a, b, q) => a + (b - a) * q;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;

/* What each condition looks like, each value from 0 to 1: sc, the eight lines lie scattered; plain, they show unlit;
   lit, they show in the accent; rest, the other directions of the RL change show between them; wash, the whole slab
   is lit; lab, the words stand at the ends of their lines. The picture moves from one look to the next in 0.9 s. */
const LOOK = {
  "untrained": { sc: 0, plain: .34, lit: 0, rest: 0, wash: 0, lab: 0 },
  "random": { sc: 1, plain: .7, lit: 0, rest: 0, wash: 0, lab: 0 },
  "rl-directions": { sc: 0, plain: 0, lit: 1, rest: 0, wash: 0, lab: 1 },
  "rl-trained": { sc: 0, plain: 0, lit: 1, rest: 1, wash: 1, lab: 1 },
};
const K = D.edit.k;  // lines on the slab, one per direction; line 0 is nearest the viewer
/* Where the lines lie when they are random: both ends of each, in units of the slab's half width and half depth. */
const SCATTER = [[-.72, .64, -.1, .22], [.16, .76, .72, .3], [-.56, -.1, .06, -.62], [.3, .06, .78, -.36],
  [-.8, -.44, -.3, -.78], [-.2, .46, .42, .64], [.1, -.3, .62, -.76], [-.44, .08, -.06, .5]];

/* Geometry: the slab lives in a small 3D space around one centre (x right, y down, z toward the viewer), as in
   architecture.py. It lies back by TILT degrees, so it is seen from slightly above. u runs to its right, v toward the
   viewer and w out of its top face. The score and its scale lie flat on the screen under it. */
const RAD = Math.PI / 180, TILT = 58, PC = Math.cos(TILT * RAD), PS = Math.sin(TILT * RAD);
function geo() {
  return narrow.matches
    ? { w: 720, h: 610, cx: 360, cy: 216, a: 136, b: 172, th: 20, r: 20, D: 1900, yaw: -4, lw: 1.8, glow: 5.5, lead: 14, fs: 26, wide: 86, nudge: 7, x0: 76, x1: 632, ay: 528, num: 128, fl: 25 }
    : { w: 1000, h: 650, cx: 500, cy: 262, a: 250, b: 250, th: 26, r: 28, D: 2100, yaw: -8, lw: 1.5, glow: 9, lead: 16, fs: 20, wide: 104, nudge: 0, x0: 140, x1: 860, ay: 588, num: 104, fl: 18 };
}
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };  // the view: a slow sway, plus a few degrees toward the pointer
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
const world = (u, v, w) => [u, v * PC - w * PS, v * PS + w * PC];
function proj(g, p) {  // to the screen: [x, y, scale, depth]
  const x = p[0] * V.c1 + p[2] * V.s1, z1 = p[2] * V.c1 - p[0] * V.s1;
  const y = p[1] * V.c2 - z1 * V.s2, z = z1 * V.c2 + p[1] * V.s2, k = g.D / (g.D - z);
  return [g.cx + x * k, g.cy + y * k, k, z];
}
function outline(g) {  // the rounded outline of the slab in its own plane, clockwise from the far right corner
  const pts = [], n = 6;
  [[1, -1, -90], [1, 1, 0], [-1, 1, 90], [-1, -1, 180]].forEach(([su, sv, a0]) => {
    for (let i = 0; i <= n; i++) {
      const a = (a0 + 90 * i / n) * RAD;
      pts.push([su * (g.a - g.r) + g.r * Math.cos(a), sv * (g.b - g.r) + g.r * Math.sin(a)]);
    }
  });
  return pts;
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
function seg(p, q, w) {  // a straight line from p to q whose width follows the depth of its ends: w is its width at scale 1
  const dx = q[0] - p[0], dy = q[1] - p[1], d = Math.hypot(dx, dy) || 1, nx = -dy / d, ny = dx / d, a = w * p[2] / 2, b = w * q[2] / 2;
  return `M${h(p[0] + nx * a)} ${h(p[1] + ny * a)}L${h(q[0] + nx * b)} ${h(q[1] + ny * b)}L${h(q[0] - nx * b)} ${h(q[1] - ny * b)}L${h(p[0] - nx * a)} ${h(p[1] - ny * a)}Z`;
}

/* The picture is built once per layout; place() then sets everything that depends on the view and on the condition.
   Back to front: the light around the slab, its body, its top face, the light inside it, the lines, the rim, the
   words, and the score on its scale. The words are real: the first tokens that two directions of one matrix read
   as through the output layer (D.words). A direction has two ends, so one line carries a word at each end. */
function build() {
  const g = S.g = geo(), svg = $("svg"), ref = D.reference, x = v => g.x0 + (g.x1 - g.x0) * v / D.max;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const fade = (id, color) => `<linearGradient id="${id}" gradientUnits="userSpaceOnUse">${stop(0, color, .5)}${stop(1, color, 1)}</linearGradient>`;
  S.words = D.words.rows.map((r, i) => ({ i, line: r.direction, side: r.sign === "+" ? 1 : -1, text: r.label }));
  S.words.forEach(o => {  // two words on neighbouring lines of one side move apart by g.nudge, so that they never touch
    const beside = d => S.words.some(q => q.side === o.side && q.line === o.line + d);
    o.dy = g.nudge * ((beside(1) ? 1 : 0) - (beside(-1) ? 1 : 0));
  });
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.42, "var(--blue)", .24)}${stop(.7, "var(--blue)", .07)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    fade("fade-b", "var(--blue)") + fade("fade-c", "var(--core)") + fade("fade-n", "var(--ink)") + "</defs>" +
    `<g class="atmo"><ellipse id="glow" cx="${g.cx}" cy="${f(g.cy + g.b * .08)}" rx="${f(g.a * 1.9)}" ry="${f(g.b * PC * 2.3)}" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${f(g.cx + g.a * .07)}" cy="${f(g.cy + g.b * PC * .22 + g.th)}" rx="${f(g.a * 1.3)}" ry="${f(g.b * PC * 1.36)}" fill="url(#shade)"/></g>` +
    `<path class="body" id="side"/><g class="edge"><path id="edge" opacity="0"/></g>` +
    `<path class="face" id="face"/><g class="wash"><path id="wash" opacity="0"/></g>` +
    `<g class="spec"><ellipse id="shine" rx="${f(g.a * .5)}" ry="${f(g.b * PC * .4)}" fill="url(#spec)"/></g>` +
    `<path class="rest" id="rest"/><path class="plain" id="plain"/><g class="bloom"><path class="halo" id="halo"/></g><path class="lit" id="lit"/>` +
    `<path class="rim draw" id="rim" pathLength="1"/>` +
    S.words.map(o => `<text class="word" id="word-${o.i}" font-size="${g.fs}" font-stretch="${g.wide}%" style="text-anchor:${o.side > 0 ? "start" : "end"}" opacity="0">${esc(o.text)}</text>`).join("") +
    `<g class="scale"><line class="axis" x1="${g.x0}" y1="${g.ay}" x2="${g.x1}" y2="${g.ay}"/>` +
    `<text class="tick" x="${g.x0 - 12}" y="${f(g.ay + g.fl * .35)}" font-size="${g.fl}" style="text-anchor:end">0</text>` +
    `<text class="tick" x="${g.x1 + 12}" y="${f(g.ay + g.fl * .35)}" font-size="${g.fl}">${D.max}</text>` +
    `<line class="ref" x1="${f(x(ref.value))}" y1="${f(g.ay - g.fl * .7)}" x2="${f(x(ref.value))}" y2="${f(g.ay + g.fl * .55)}"/>` +
    `<text class="reftext" x="${f(x(ref.value) + 4)}" y="${f(g.ay + g.fl * 1.75)}" font-size="${g.fl}">${esc(ref.name)} ${ref.value}${esc(D.unit || "")}</text>` +
    `<line class="level" id="level" x1="${g.x0}" y1="${g.ay}" y2="${g.ay}"/><circle class="head" id="head" cy="${g.ay}" r="${f(g.fl * .32)}"/>` +
    `<text class="value" id="value" y="${f(g.ay - g.num * .2)}" font-size="${g.num}"></text></g>`;
  S.el = {};
  ["glow", "side", "edge", "face", "wash", "shine", "rest", "plain", "halo", "lit", "rim", "fade-b", "fade-c", "fade-n", "level", "head", "value"].forEach(id => { S.el[id] = $(id); });
  S.words.forEach(o => { o.el = $("word-" + o.i); });
  S.out = outline(g);
  S.shown = "";
}

function place(t) {
  const g = S.g, c = S.cur, E = S.el, top = g.th / 2;
  if (!E || !c) return;
  const at = (u, v, w) => proj(g, world(u, v, w)), set = (el, o) => { for (const k in o) el.setAttribute(k, o[k]); };
  const path = p => "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";

  // The slab: its top face, and the silhouette of its whole body, of which the face covers all but the near edge.
  const up = S.out.map(([u, v]) => at(u, v, top)), down = S.out.map(([u, v]) => at(u, v, -top));
  const face = path(up), body = path(hull([...up, ...down]));
  set(E.face, { d: face }); set(E.rim, { d: face }); set(E.wash, { d: face, opacity: h(c.wash) });
  set(E.side, { d: body }); set(E.edge, { d: body, opacity: h(Math.min(1, .35 * c.lit + .65 * c.wash)) });
  E.glow.setAttribute("opacity", h(.45 + .2 * c.lit + .35 * c.wash));
  const shine = at(-g.a * .36, -g.b * .34, top);
  set(E.shine, { cx: f(shine[0]), cy: f(shine[1]) });
  const far = at(0, -g.b, top), near = at(0, g.b, top);  // lines are faint at the back and full in front
  [E["fade-b"], E["fade-c"], E["fade-n"]].forEach(el => set(el, { x1: f(far[0]), y1: f(far[1]), x2: f(near[0]), y2: f(near[1]) }));

  // The eight lines. In order they run across the slab; scattered they lie anywhere. A line with a word reaches out
  // past the edge of the slab to it.
  const row = i => g.b * (1 - 2 * (i + 1) / (K + 1)), reach = (i, side) => S.words.some(o => o.line === i && o.side === side) ? c.lab : 0;
  const end = (i, side) => side * (g.a * .84 + (g.a * .16 + g.lead) * reach(i, side));
  let plain = "", lit = "", halo = "", rest = "";
  for (let i = 0; i < K; i++) {
    const s = SCATTER[i], v0 = row(i);
    const v1 = mix(v0, s[1] * g.b, c.sc), v2 = mix(v0, s[3] * g.b, c.sc);
    const p = at(mix(end(i, -1), s[0] * g.a, c.sc), v1, top), q = at(mix(end(i, 1), s[2] * g.a, c.sc), v2, top);
    const w = g.lw * (.6 + .4 * ((v1 + v2) / (4 * g.b) + .5)), breath = 1 + .1 * Math.sin(t * (.5 + .07 * i) + i * 1.7);
    if (c.plain > .01) plain += seg(p, q, w);
    if (c.lit > .01) { lit += seg(p, q, w * 2 * breath); halo += seg(p, q, w * g.glow * breath); }
  }
  if (c.rest > .01) for (let j = 0; j <= K; j++) for (const part of [1 / 3, 2 / 3]) {  // the other directions of the RL change, two in each gap
    const v = g.b * (1 - 2 * (j + part) / (K + 1));
    rest += seg(at(-g.a * .84, v, top), at(g.a * .84, v, top), g.lw * .8);
  }
  set(E.plain, { d: plain, opacity: h(c.plain) });
  set(E.lit, { d: lit, opacity: h(c.lit) });
  set(E.halo, { d: halo, opacity: h(.26 * c.lit) });
  set(E.rest, { d: rest, opacity: h(.55 * c.rest) });
  S.words.forEach(o => {  // upright, at the end of its line
    const p = at(o.side * (g.a + g.lead), row(o.line), top);
    set(o.el, { x: f(p[0] + o.side * 9), y: f(p[1] + g.fs * .34 + o.dy), opacity: h(c.lab) });
  });

  // The score: one number that moves along the scale.
  const x = g.x0 + (g.x1 - g.x0) * c.v / D.max, text = String(Math.round(c.v)) + (D.unit || "");
  set(E.level, { x2: f(x) }); set(E.head, { cx: f(x) }); set(E.value, { x: f(x) });
  if (text !== S.shown) E.value.textContent = S.shown = text;
}

/* Motion that is always on: the view sways by a few degrees and leans toward the mouse, and the lit lines breathe
   each at its own rate. With reduced motion the page shows one still frame and a condition changes at once. */
function frame(now) {
  const t = S.t = now / 1000;
  V.px += (V.tx - V.px) * .06;
  V.py += (V.ty - V.py) * .06;
  aim(S.g.yaw + 6 * Math.sin(t * .13) + 5 * V.px, 2.5 * Math.sin(t * .09) - 2.5 * V.py);
  if (S.from) {
    const p = Math.min(1, (now - S.t0) / 900), e = ease(p);
    for (const k in S.goal) S.cur[k] = mix(S.from[k], S.goal[k], e);
    if (p >= 1) S.from = null;
  }
  place(t);
  requestAnimationFrame(frame);
}

/* The condition and the open panel are one value in the address: #<condition>, #<panel> or #<condition>/<panel>. */
function choose(i, instant) {
  const st = D.states[i], ref = D.reference;
  S.state = i;
  S.goal = { ...LOOK[st.key], v: st.value };
  if (instant || still.matches || !S.cur) { S.cur = { ...S.goal }; S.from = null; }
  else { S.from = { ...S.cur }; S.t0 = performance.now(); }
  $("svg").setAttribute("aria-label", `${D.metric}: ${st.name} ${st.value} of ${D.max}, ${ref.name} ${ref.value} of ${D.max}.`);
  $("note").textContent = st.note;
  $("switch").querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-pressed", k === i));
  place(S.t);
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
function address(push) {
  const parts = [S.state ? D.states[S.state].key : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const i = Math.max(0, D.states.findIndex(s => parts.includes(s.key))), p = C.panels.find(p => parts.includes(p[0]));
  if (first === true || i !== S.state) choose(i, first === true);
  S.open = p ? p[0] : null;
  pane();
}
function open(key) {  // a panel opens in the side column; the keyboard focus follows it there and back
  const was = S.open;
  S.open = key || null;
  address(true);
  pane();
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
}

document.addEventListener("click", e => {
  const s = e.target.closest("[data-state]"), o = e.target.closest("[data-open]");
  if (s) { choose(Number(s.dataset.state)); address(false); }
  if (o) open(o.dataset.open);
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) open("");
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
    const inside = document.activeElement && document.activeElement.closest("#switch");
    choose((S.state + (e.key === "ArrowRight" ? 1 : D.states.length - 1)) % D.states.length);
    address(false);
    if (inside) $("switch").children[S.state].focus();
  }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); place(S.t); });
const stage = $("stage");  // the view leans a few degrees toward a mouse, and settles back
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1;
  V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");  // a number inside a name (MATH-500) stays plain
$("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}" aria-pressed="false">${esc(s.name)}</button>`).join("");
build();
aim(S.g.yaw, 0);  // the still frame
fromHash(true);
if (!still.matches) {
  $("svg").classList.add("enter");
  setTimeout(() => $("svg").classList.remove("enter"), 2200);
  requestAnimationFrame(frame);
}
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}))
