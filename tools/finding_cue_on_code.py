"""A three-token opening cue taken from math lifts the base model on code from 41 % to 61 % of 538 problems, against 75 % after RL.

The page of one finding, served at /finding/cue-on-code (copied from .claude/skills/finding-page/template.py; draw() and
place() show one glass column per condition under the bar of the model trained with RL on code, instead of one flat bar).
It is reached from its tile on /findings, which ICON draws. Study: studies/rlneurons (README.md "Code pair",
specs/SPEC_code1.md; board result-59ed1a).
"""
import json

# Every number is copied from the artifacts named here. None is typed from memory.
DATA = {
    "artifact": "studies/rlneurons/results/code1/readout.json",
    "commit": "9fac5b7",       # the commit that holds the readout and the four run folders
    "run_commit": "be62e76",   # the code the four GPU jobs ran (each run.json)
    "spec": "studies/rlneurons/specs/SPEC_code1.md",
    "n": 538,                  # cells.*.all.n: HumanEval+ 163 and MBPP+ 375, after 4 of 542 failed the grader check
    "n_all": 542, "n_excluded": 4,  # <cell>-01/metrics.json: n_problems, grader_check.failed
    # What the reader switches between. The first is shown on load: start from the problem, not from the answer.
    # passed and tokens: cells.<key>.all.passed and tokens_per_problem; cue: cells.<key>.prefix_text
    "states": [
        {"key": "base_plain", "name": "No cue", "passed": 222, "tokens": 2241, "cue": ""},
        {"key": "base_cue", "name": "Code cue", "passed": 317, "tokens": 4148, "cue": " as shown in the prompt. I hope this helps!\n\nOkay"},
        {"key": "base_mathcue", "name": "Math cue", "passed": 326, "tokens": 4119, "cue": " line!\n\nOkay"},
    ],
    # The strongest baseline, drawn as a bar across the picture: cells.rl_plain
    "reference": {"key": "rl_plain", "name": "After RL on code", "passed": 401, "tokens": 4054},
    # differences.<a - b>: points and bootstrap95, paired over problems with 5,000 resamples
    "diff": {
        "rl_plain - base_plain": [33.271, 28.810, 37.732],
        "rl_plain - base_cue": [15.613, 11.524, 19.888],
        "rl_plain - base_mathcue": [13.941, 10.037, 17.844],
        "base_plain - base_cue": [-17.658, -22.491, -12.825],
        "base_plain - base_mathcue": [-19.331, -24.349, -14.312],
        "base_cue - base_mathcue": [-1.673, -5.762, 2.788],
    },
    # cells.<key>.all_no_overlap: without the 3 problems that overlap the RL training prompts (overlap_excluded)
    "no_overlap": {"n": 535, "base_plain": 221, "base_cue": 315, "base_mathcue": 323, "rl_plain": 399},
    "no_block": {"base_plain": 43, "base_cue": 34, "base_mathcue": 33, "rl_plain": 8},  # cells.<key>.all.no_block
    # Wang et al., arXiv 2610.06851, Table 5, as quoted in the spec: HumanEval, the base model without and with the
    # math cue, and the model trained with RL on math
    "wang": {"base": 50.2, "cue": 69.8, "rl_math": 68.5},
}
N, ST, REF, DIFF, NO = DATA["n"], DATA["states"], DATA["reference"], DATA["diff"], DATA["no_overlap"]
PCT = [100 * s["passed"] / N for s in ST]             # 41.3, 58.9 and 60.6 % of 538
GAIN = REF["passed"] - ST[0]["passed"]                # 179 problems: what RL adds to the base model without a cue
SHARE = [round(100 * (s["passed"] - ST[0]["passed"]) / GAIN) for s in ST[1:]]  # the part of that gain each cue covers


def gap(key, flip=False):
    """One difference as text: the points, then the 95 % interval. flip gives b - a for a stored a - b."""
    p, lo, hi = DIFF[key]
    if flip:
        p, lo, hi = -p, -hi, -lo
    return f"{p:.1f} points (95 % interval {lo:.1f} to {hi:.1f})"


AHEAD = sorted(DIFF[k][0] for k in ("rl_plain - base_cue", "rl_plain - base_mathcue"))  # 13.9 and 15.6 points

TITLE = "Cue on code"
PROBLEM = "How much of the RL gain on code needs no training?"
LINE = f"A three-token cue from math lifts the base model on code from {PCT[0]:.0f} % to {PCT[2]:.0f} %."  # also on its tile

ST[0]["note"] = f"Share of {N} code problems passed. A cue is a few tokens placed at the start of the answer."
ST[1]["note"] = ("Each answer is started with the opening that the model trained on code writes itself: "
                 "“as shown in the prompt. I hope this helps!” and, after a blank line, “Okay”.")
ST[2]["note"] = ("Each answer is started with the opening of a model trained on math: “line!” and, after a blank line, “Okay”. "
                 f"The two cues differ by {-DIFF['base_cue - base_mathcue'][0]:.1f} points, and the 95 % interval of that difference "
                 f"({-DIFF['base_cue - base_mathcue'][2]:.1f} to {-DIFF['base_cue - base_mathcue'][1]:.1f}) includes zero.")

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new", "Wang et al. (arXiv 2610.06851, Table 5) already report that the math cue lifts this base model "
     f"on HumanEval from {DATA['wang']['base']} % to {DATA['wang']['cue']} %, level with the model trained with RL on math "
     f"({DATA['wang']['rl_math']} %).",
     ["New here: the reference is the model trained with RL on code, which that paper does not test. "
      f"The cue covers {SHARE[0]} % to {SHARE[1]} % of its gain.",
      "Also new: a cue taken from the code model's own opening does no better than the math cue: "
      f"{ST[1]['passed']} against {ST[2]['passed']} of {N} problems, {gap('base_cue - base_mathcue')}.",
      "The team's paper notes and a web search hold no earlier report of a cue against a model trained on code."]],
    ["why", "Why it matters", "The team asks how much of a published RL gain a base model reaches with no training. On code the "
     "answer is more than half, with a cue that was taken from math and used unchanged.",
     ["For this second domain the cue did not have to be searched for again.",
      f"The cue changes how the base model answers. It writes {ST[2]['tokens']:,} tokens per problem with the math cue against "
      f"{ST[0]['tokens']:,} without one, about the length of the RL model's answers ({REF['tokens']:,}).",
      f"Still open: the {AHEAD[0]:.0f} to {AHEAD[1]:.0f} points that RL keeps. A vote over several samples, which the team uses on "
      "math problems, has not been run on code."]],
    ["how", "How we know", f"Each condition is one sampled answer per problem on {N} problems of HumanEval+ and MBPP+ at temperature "
     "1.0, scored by running the benchmark's tests.",
     [f"Passed of {N}: the base model (allenai/Olmo-3-1025-7B) {ST[0]['passed']} without a cue, {ST[1]['passed']} with the code "
      f"cue, {ST[2]['passed']} with the math cue; the RL model (allenai/Olmo-3.1-7B-RL-Zero-Code) {REF['passed']}.",
      f"The code cue adds {gap('base_plain - base_cue', True)} and the math cue {gap('base_plain - base_mathcue', True)}, paired "
      "over problems.",
      "Control: before sampling, every reference solution had to pass the grader and a planted wrong program had to fail."]],
    ["limits", "What it does not show", "It does not show that a cue replaces RL on code. RL stays "
     f"{AHEAD[0]:.1f} to {AHEAD[1]:.1f} points ahead of the base model with a cue, at the same number of tokens per problem.",
     ["Each problem was sampled once and there is no vote. Which part of a cue helps was not tested: both cues end in the same "
      "two tokens, an exclamation mark with a blank line and the word Okay.",
      f"{DATA['n_excluded']} of {DATA['n_all']} problems are left out because the grader check failed on them, and 3 more overlap "
      f"the RL training prompts. Without those 3 the counts are {NO['base_plain']}, {NO['base_cue']}, {NO['base_mathcue']} and "
      f"{NO['rl_plain']} of {NO['n']}.",
      "It is one pair of models, two sets of short Python problems and one run of each condition."]],
    ["run", "How to reproduce it", "Each of the four conditions is one job on an H100 GPU in the study studies/rlneurons, and the "
     "readout runs on a laptop.",
     ["One condition: studies/rlneurons/jobs/run_code_cell.py with --model base and, for the math cue, --prefix-ids "
      "\"[1584,2268,33413]\" (commit " + DATA["run_commit"] + ").",
      "The readout: studies/rlneurons/analysis/code1_readout.py with the four job ids from each run.json. Its numbers are in "
      + DATA["artifact"] + " (commit " + DATA["commit"] + ").",
      "The plan, written before the first run, is in " + DATA["spec"] + "."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with one post per condition, as high as its share of problems passed, under the fine bar of the
# model trained with RL. The post without a cue is plain; the two posts with a cue are lit.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, top = th / 2, H = 46, pass = __PASS__, rl = top + H * __RL__;
  return kit.slab(a, b, th) +
    kit.line(kit.at(-a * .82, 0, rl), kit.at(a * .82, 0, rl), .8) +
    pass.map((s, i) => {
      const u = a * .52 * (i - 1);
      return kit.line(kit.at(u, 0, top), kit.at(u, 0, top + H * s), i ? 3.2 + .2 * Math.sin(t * .6 + i) : 3.2, i ? "lit" : "plain", i ? 1 : .7);
    }).join("");
}""".replace("__PASS__", json.dumps([round(p / 100, 3) for p in PCT])).replace("__RL__", str(round(REF["passed"] / N, 3)))

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
   --wash is how strongly a column takes the accent when it is the chosen one. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --wash: .26;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --wash: .4;
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

/* The picture, and the one control that changes it. The switch is as wide as the three columns, so that each of its
   buttons sits under its own column and names it. */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
.scene { width: min(100%, calc(60vh * 700 / 400)); align-self: center; display: flex; flex-direction: column; }
svg { width: 100%; aspect-ratio: 700 / 400; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 104%; }
.atmo, .shade { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.body { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; stroke-linejoin: round; }
.face { fill: url(#body) var(--sheet); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1.4; stroke-linejoin: round; }
.wash { fill: var(--blue); opacity: calc(var(--wash) * var(--q, 0)); pointer-events: none; }
.num { font-weight: 640; text-anchor: middle; }
.post { fill: none; stroke: var(--faint); stroke-width: 1; }
.bar { fill: none; stroke: var(--ink); stroke-width: 1.8; stroke-linecap: round; }
.ref { font-size: 22px; font-weight: 520; fill: var(--mute); }
.ref .refnum { fill: var(--ink); font-weight: 660; }
.switch { display: grid; grid-template-columns: repeat(3, 1fr); width: 79.3%; align-self: center; margin-top: 12px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 4px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; text-align: center; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.note { align-self: center; margin: 12px 0 0; color: var(--mute); font-size: 15px; text-align: center; max-width: 62ch; min-height: 4.5em; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
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
  .stage { order: 3; margin-top: 18px; padding: 0; }
  .scene { width: 100%; }
  .pane { order: 4; margin-top: 14px; }
  .switch { width: 84%; }
  .switch button { font-size: 14px; }
  .note { min-height: 7.5em; }
}
@media (prefers-reduced-motion: reduce) {
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
    <div class="scene">
      <svg id="svg" viewBox="0 0 700 400" role="img"></svg>
      <div class="switch" id="switch" role="group" aria-label="The start of the answer"></div>
      <p class="note" id="note" aria-live="polite"></p>
    </div>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const S = { state: 0, open: null, last: 0, cols: [] };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const pct = s => 100 * s.passed / D.n, show = v => `${v.toFixed(1)}\u00a0%`, nb = s => s.replace(/ %/g, "\u00a0%");  // 95 % stays on one line

/* The picture: a glass board seen from slightly above, with one glass column per condition. A column is as high as the
   share of the 538 problems its condition passes. The fine bar across the board is the model trained with RL on code.
   The switch raises the columns up to the chosen condition and lights the chosen one, so the page loads on the base
   model without a cue, and the two cues end up side by side under the bar. */
const RAD = Math.PI / 180, CX = 350, CY = 345, EL = 20, A = 300, B = 84, HW = 68, HD = 52, STEP = 185, UNIT = 3.9, FLAT = 3;
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
const at = q => f(q[0]) + " " + f(q[1]), path = p => "M" + p.map(at).join("L") + "Z";
const rect = (u, a, b, w) => [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => proj(u + i * a, j * b, w));  // front left first
const target = i => [i <= S.state ? 1 : 0, i === S.state ? 1 : 0];  // is column i raised, is it the chosen one

function build() {
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const cols = D.states.map((s, i) => {
    S.cols.push({ u: (i - 1) * STEP, h: UNIT * pct(s), g: 0, q: 0 });  // the columns start down and rise once on load
    return `<g id="c${i}"><path class="body" id="b${i}"/><path class="face" id="f${i}"/><path class="wash" id="wf${i}"/><path class="rim" id="rf${i}"/>` +
      `<path class="face" id="t${i}"/><path class="wash" id="wt${i}"/><path class="rim" id="rt${i}"/><text class="num" id="n${i}">${show(pct(s))}</text></g>`;
  }).join("");
  $("svg").innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.3, "var(--blue)", .2)}${stop(.7, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient></defs>` +
    `<g class="atmo"><ellipse cx="${CX}" cy="${CY - 110}" rx="340" ry="230" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${CX + 14}" cy="${CY + 34}" rx="338" ry="52" fill="url(#shade)"/></g>` +
    `<path class="body" id="board-side"/><path class="face" id="board-face"/><path class="rim" id="board-rim"/>` +
    `<path class="post" id="posts"/><path class="bar" id="bar"/>` + cols +
    `<text class="ref" id="ref">${D.reference.name} <tspan class="refnum">${show(pct(D.reference))}</tspan></text>`;
  S.cols.forEach((o, i) => { o.el = Object.fromEntries(["c", "b", "f", "wf", "rf", "t", "wt", "rt", "n"].map(k => [k, $(k + i)])); });
  $("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}">${s.name}</button>`).join("");
}
function place() {
  const top = rect(0, A, B, 0), d = path(top), hr = UNIT * pct(D.reference), e = A - 10;
  $("board-side").setAttribute("d", path(hull([...top, ...rect(0, A, B, -12)])));
  $("board-face").setAttribute("d", d); $("board-rim").setAttribute("d", d);
  const l = proj(-e, 0, hr), r = proj(e, 0, hr);
  $("posts").setAttribute("d", `M${at(proj(-e, 0, 0))}L${at(l)}M${at(proj(e, 0, 0))}L${at(r)}`);
  $("bar").setAttribute("d", `M${at(l)}L${at(r)}`);
  $("ref").setAttribute("x", f(l[0] + 12)); $("ref").setAttribute("y", f(l[1] - 13));
  S.cols.forEach(o => {
    const h = mix(FLAT, o.h, o.g), up = rect(o.u, HW, HD, h), down = rect(o.u, HW, HD, 0);
    const front = path([down[0], down[1], up[1], up[0]]), face = path(up), c = proj(o.u, -HD, h);
    o.el.b.setAttribute("d", path(hull([...up, ...down])));
    o.el.f.setAttribute("d", front); o.el.wf.setAttribute("d", front); o.el.rf.setAttribute("d", front);
    o.el.t.setAttribute("d", face); o.el.wt.setAttribute("d", face); o.el.rt.setAttribute("d", face);
    o.el.c.style.setProperty("--q", o.q.toFixed(2));
    o.el.c.setAttribute("opacity", mix(.4, 1, o.g).toFixed(2));
    o.el.n.setAttribute("x", f(c[0])); o.el.n.setAttribute("y", f(c[1] + mix(35, 47, o.q) * c[2]));
    o.el.n.setAttribute("font-size", f(mix(26, 38, o.q) * c[2]));
    o.el.n.setAttribute("opacity", Math.max(0, (o.g - .6) / .4).toFixed(2));
  });
}
/* One frame: the view sways slowly and leans toward the pointer, and every column moves toward its height and its
   light for the chosen condition. With reduced motion the page shows one still frame. */
function frame(now) {
  const t = now / 1000, k = 1 - Math.exp(-4 * Math.min(.05, (now - S.last) / 1000));
  S.last = now;
  V.px += (V.tx - V.px) * .06; V.py += (V.ty - V.py) * .06;
  V.yaw = 2 * Math.sin(t * .25) + 2.5 * V.px; V.el = EL + Math.sin(t * .19 + 1) - 2 * V.py;
  S.cols.forEach((o, i) => { const [g, q] = target(i); o.g += (g - o.g) * k; o.q += (q - o.q) * k; });
  place();
  if (!still.matches) requestAnimationFrame(frame);
}
function draw() {  // the switch, the note and the label follow the state; the columns follow in frame()
  const st = D.states[S.state];
  $("svg").setAttribute("aria-label", `Problems passed of ${D.n}: ` +
    D.states.slice(0, S.state + 1).map(s => `${s.name} ${show(pct(s))}`).join(", ") + `, ${D.reference.name} ${show(pct(D.reference))}`);
  $("note").textContent = nb(st.note);
  document.querySelectorAll("[data-state]").forEach((b, i) => b.setAttribute("aria-pressed", i === S.state));
}
function settle() { S.cols.forEach((o, i) => { [o.g, o.q] = target(i); }); place(); }  // the picture without the motion
function choose(i) {
  if (i === S.state) return;
  S.state = i;
  draw();
  if (still.matches || performance.now() - S.last > 500) settle();  // no frames are drawn: reduced motion, or a hidden tab
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${p[1]}</h2><button class="close" data-open="">Close</button></div><p class="lead">${nb(p[2])}</p>` +
      `<ul class="facts">${p[3].map(f => `<li>${nb(f)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${p[1]}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
function fromHash() { const h = location.hash.slice(1); S.open = C.panels.some(p => p[0] === h) ? h : null; pane(); }
document.addEventListener("click", e => {
  const s = e.target.closest("[data-state]"), o = e.target.closest("[data-open]");
  if (s) choose(Number(s.dataset.state));
  if (o) { history.pushState(null, "", o.dataset.open ? "#" + o.dataset.open : location.pathname); fromHash(); }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) { history.pushState(null, "", location.pathname); fromHash(); }
  if (e.key === "ArrowRight") choose(Math.min(D.states.length - 1, S.state + 1));
  if (e.key === "ArrowLeft") choose(Math.max(0, S.state - 1));
});
addEventListener("hashchange", fromHash);
$("stage").addEventListener("pointermove", e => {  // the view leans a few degrees toward a mouse, and settles back
  if (e.pointerType !== "mouse") return;
  const r = $("stage").getBoundingClientRect();
  V.tx = 2 * (e.clientX - r.left) / r.width - 1; V.ty = 2 * (e.clientY - r.top) / r.height - 1;
});
$("stage").addEventListener("pointerleave", () => { V.tx = V.ty = 0; });
$("problem").textContent = C.problem;
$("say").innerHTML = nb(C.line.replace(/(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>"));
build();
draw();
fromHash();
if (still.matches) settle();
else { requestAnimationFrame(frame); setTimeout(() => { if (!S.last) settle(); }, 800); }  // a hidden tab draws no frames
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}))
