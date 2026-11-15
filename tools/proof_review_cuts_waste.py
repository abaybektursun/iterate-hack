"""Three rounds of the team-meta-review skill cut the compute per batch of answers from 16.3 to 4.4 container minutes.

A proof page: a test of the team's method itself, served at /proof/review-cuts-waste and reached from its tile on
/proof, which ICON draws (made like a finding page, from .claude/skills/finding-page/template.py;
draw() shows two glass columns, one per kind of review, whose height is the container minutes one batch costs, with the
part that produced an answer lit). Study:
studies/metaharness (README.md "Planted-waste test", specs/SPEC2.md; board result-8b2682).
"""
import json

# Every number is copied from the artifact named here. None is typed from memory.
# minutes = mean container_minutes of the 3 runs of an arm at each position (0 = before any review, 1 to 3 = after that
# round); answer = mean minutes_by_line.answer; share = mean waste_share; clean = mean container_minutes of window 0 of
# the 4 clean runs; named = mean number of plants named per review (review.named).
DATA = {
    "artifact": "studies/metaharness/results/planted/summary-01/metrics.json",
    "commit": "ba4c253",
    "rounds": ["Before", "Round 1", "Round 2", "Round 3"],
    "arms": [
        {"name": "Review skill", "minutes": [16.3, 9.3, 6.5, 4.4], "answer": [2.7, 2.7, 2.6, 2.3], "share": [83, 71, 60, 48],
         "runs_last": [4.0, 4.8, 4.5], "left": [2, 3, 3], "named": 3.1},
        {"name": "Plain instruction", "minutes": [15.1, 13.6, 11.1, 9.8], "answer": [2.4, 2.7, 2.8, 2.2], "share": [84, 80, 72, 73],
         "runs_last": [11.5, 12.6, 5.2], "left": [4, 4, 2], "named": 2.6},
    ],
    "clean": 3.2, "planted": 6, "runs": 3, "reviews": 9,
}
SKILL, PLAIN = DATA["arms"]

TITLE = "Review cuts waste"
PROBLEM = "Does a team of agents waste less compute when it reviews itself?"
LINE = f"Three rounds of the review skill cut compute per batch from {SKILL['minutes'][0]} to {SKILL['minutes'][3]} minutes."  # also on its tile

# What the reader switches between: the review round. The first is shown on load: start from the problem.
DATA["states"] = [
    {"name": "Before", "note": f"One batch of 4 answers, with {DATA['planted']} inefficiencies planted in the code and its instructions. "
                               f"About {SKILL['share'][0]} % of the compute produces no answer."},
    {"name": "Round 1", "note": "The skill's reviews removed the repeated runs and a wrong path in the instructions. "
                                "The plain reviews removed the failed launches and the wrong path."},
    {"name": "Round 2", "note": "The skill's reviews removed the failed launches. One plain review of three removed the repeated runs."},
    {"name": "Round 3", "note": "The skill's reviews cut the setup inside every job. Two of the three plain runs removed nothing after round 1."},
]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new", "A published system that changes its own prompts, gates and policies after repeated process failures reports "
     "8 hand-audited events and calls this \"a retrospective process audit, not a controlled comparison\" "
     "(Sibyl-AutoResearch, arXiv 2605.22343, Section 6).",
     [f"New here: the {DATA['planted']} inefficiencies were planted before any review ran, so each one counts as found or missed, "
      "and as removed or still there in the next batch's job records.",
      "New here: the control is the same model on the same work, told to review the last hour and make one improvement, "
      "without the skill."]],
    ["why", "Why it matters", "The swarm's measurements are paid for in compute, and a review that removes waste gives that compute back "
     "without more hardware.",
     [f"After three rounds a batch costs {SKILL['minutes'][3]} container minutes. The same work with nothing planted costs {DATA['clean']}.",
      f"The same model with a plain instruction reached {PLAIN['minutes'][3]} minutes, so the written review procedure adds to what the model does alone.",
      f"The skill makes one change per review, and after three rounds {min(SKILL['left'])} or {max(SKILL['left'])} of the {DATA['planted']} "
      "inefficiencies were still in place."]],
    ["how", "How we know", f"{DATA['planted']} inefficiencies were planted in a small study that runs as CPU jobs. A fresh agent reviewed the "
     "work and made one change, the next batch of the same size ran on the changed code, and this was done three times.",
     [f"There are {DATA['runs']} runs and {DATA['reviews']} reviews per arm, all by claude-opus-5-5. One arm is told to run the "
      "team-meta-review skill. The other is told to review the last hour and make one improvement.",
      "Compute is the container time of real Modal CPU jobs of one class. Every batch delivered its 4 answers with the same point "
      "estimates as a reference run.",
      f"The skill's reviews named {SKILL['named']} of the planted inefficiencies per review and the plain reviews {PLAIN['named']}. "
      "No inefficiency that was removed came back in a later batch."]],
    ["limits", "What it does not show", "It does not show that the review is safe on work that has no waste. On clean work both reviews "
     "with the skill cut a bootstrap from 1,500,000 resamples to 20,000 and 10,000, against a written requirement of the study's owner.",
     ["The work was run by a fixed script that follows the repository's code and instructions. Waste in what an agent chooses to do "
      "was not measured.",
      f"With {DATA['runs']} runs per arm there is no significance test. The best plain run ended at {min(PLAIN['runs_last'])} minutes "
      f"and the worst run with the skill at {max(SKILL['runs_last'])}.",
      "No review in either arm removed the job whose answer was already stored, and none named it."]],
    ["run", "How to reproduce it", "One command runs one arena from the first batch to the last, and the readout rebuilds the table "
     "from the job records.",
     ["MH_HOME=<folder> python3 -m studies.metaharness.prep.run_arena a1 skill planted 5721 <base commit> 0,1,2,3 (commit "
      + DATA["commit"] + "). It needs a Modal workspace with infra/runner.py deployed.",
      "The numbers are in " + DATA["artifact"] + ", one folder per run beside it.",
      "The plan, written before the runs, is studies/metaharness/specs/SPEC2.md."]],
]

# The icon of this page's tile on /proof (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with two posts as high as the compute per batch: plain before any review, lit after three
# rounds of the skill's reviews.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, top = th / 2, m = __MINUTES__, k = 34 / m[0];
  return kit.slab(a, b, th) +
    kit.line(kit.at(-a * .34, 0, top), kit.at(-a * .34, 0, top + k * m[0]), 3.2, "plain", .7) +
    kit.line(kit.at(a * .34, 0, top), kit.at(a * .34, 0, top + k * m[1]), 3.2 + .2 * Math.sin(t * .6), "lit");
}""".replace("__MINUTES__", json.dumps([SKILL["minutes"][0], SKILL["minutes"][3]]))

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
   --wash is how strongly the lit part of a column takes the accent. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --wash: .3;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
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
.wash { fill: var(--blue); pointer-events: none; }
.wash { opacity: var(--wash); }
.col .body { fill: var(--glass); stroke: url(#rim) var(--rim-b); stroke-width: 1.2; }
.band { fill: none; stroke: var(--blue); stroke-width: 1.6; stroke-linejoin: round; }
.num { font-weight: 330; font-stretch: 100%; letter-spacing: -.03em; text-anchor: middle; }
.num tspan { font-weight: 500; fill: var(--mute); letter-spacing: 0; font-stretch: 104%; }
.arm { fill: var(--ink); font-weight: 560; text-anchor: middle; }
.key { fill: var(--mute); font-weight: 500; }
.keylit { fill: var(--blue); opacity: calc(var(--wash) + .25); }
.keyglass { fill: var(--glass); stroke: var(--mute); stroke-width: 1.2; }
.switch { display: inline-flex; align-self: center; margin-top: 18px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.note { align-self: center; margin: 12px 0 0; color: var(--mute); font-size: 15px; text-align: center; max-width: 62ch; min-height: 3em; }

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
.close { font-size: 13px; color: var(--mute); padding: 12px 0 12px 16px; margin: -12px 0; }
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
  .switch button { padding: 12px 12px; font-size: 14px; }
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
    <a href="/proof" aria-current="page">Proof</a>
    <a href="/findings">Findings</a>
  </header>
  <div class="stage" id="stage">
    <svg id="svg" viewBox="0 0 760 640" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="Review round"></div>
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

/* The picture: two glass columns on a glass board seen from slightly above, one per kind of review. A column is as
   high as the container minutes one batch costs after the chosen round. Its lit foot is the part of those minutes
   that produced one of the 4 answers; the plain glass above it produced none. The switch moves through the rounds. */
const RAD = Math.PI / 180, CX = 380, CY = 468, EL = 27, UNIT = 19.5, HALF = 62, GAP = 122, RU = 262, RV = 128;
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
const rect = (u, v, ru, rv, w) => [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => proj(u + i * ru, v + j * rv, w));
const at = (list, q) => { const i = Math.min(list.length - 2, Math.floor(q)); return mix(list[i], list[i + 1], q - i); };  // between two rounds

function build() {
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  S.cols = D.arms.map((arm, i) => ({ arm, id: i, u: (i ? 1 : -1) * GAP, v: 0 }));
  $("svg").innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.3, "var(--blue)", .2)}${stop(.7, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient></defs>` +
    `<g class="atmo"><ellipse cx="${CX}" cy="${CY - 120}" rx="430" ry="330" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${CX + 22}" cy="${CY + 26}" rx="400" ry="150" fill="url(#shade)"/></g>` +
    `<path class="body" id="board-side"/><path class="face" id="board-face"/><path class="rim" id="board-rim"/>` +
    S.cols.map(o => `<g class="col"><path class="body" id="b${o.id}"/><path class="wash" id="w${o.id}"/><path class="band" id="a${o.id}"/>` +
      `<path class="face" id="f${o.id}"/><path class="rim" id="r${o.id}"/>` +
      `<text class="num" id="n${o.id}"><tspan id="v${o.id}" style="fill:var(--ink);font-weight:330;letter-spacing:-.03em;font-stretch:100%"></tspan><tspan dx="7" id="m${o.id}">min</tspan></text>` +
      `<text class="arm" id="t${o.id}">${o.arm.name}</text></g>`).join("") +
    `<rect class="keylit" id="k1" width="15" height="15" rx="2"/><text class="key" id="k1t">produced an answer</text>` +
    `<rect class="keyglass" id="k2" width="15" height="15" rx="2"/><text class="key" id="k2t">produced none</text>`;
  S.cols.forEach(o => { o.el = Object.fromEntries(["b", "w", "a", "f", "r", "n", "v", "m", "t"].map(k => [k, $(k + o.id)])); });
  const ph = innerWidth <= 600;  // on a phone the key is set larger, so it stays 12 px on screen
  [["k1", ph ? 130 : 236], ["k2", ph ? 440 : 432]].forEach(([id, x]) => {
    $(id).setAttribute("x", x); $(id).setAttribute("y", 612);
    $(id + "t").setAttribute("x", x + 23); $(id + "t").setAttribute("y", ph ? 628 : 625); $(id + "t").setAttribute("font-size", ph ? 27 : 17);
  });
}
function place() {
  const q = S.q, top = rect(0, 0, RU, RV, 0), d = path(top);
  $("board-side").setAttribute("d", path(hull([...top, ...rect(0, 0, RU, RV, -12)])));
  $("board-face").setAttribute("d", d); $("board-rim").setAttribute("d", d);
  S.cols.forEach(o => {
    const minutes = at(o.arm.minutes, q), h = Math.max(3, minutes * UNIT * S.grow), lit = Math.min(h, at(o.arm.answer, q) * UNIT * S.grow);
    const up = rect(o.u, o.v, HALF, HALF, h), foot = rect(o.u, o.v, HALF, HALF, 0), mid = rect(o.u, o.v, HALF, HALF, lit), face = path(up);
    o.el.b.setAttribute("d", path(hull([...up, ...foot])));
    o.el.w.setAttribute("d", path(hull([...mid, ...foot])));
    o.el.a.setAttribute("d", "M" + [mid[3], mid[0], mid[1]].map(p => f(p[0]) + " " + f(p[1])).join("L"));  // the two near edges
    o.el.f.setAttribute("d", face); o.el.r.setAttribute("d", face);
    const c = proj(o.u, o.v, h), near = proj(o.u, -RV - 34, 0);
    o.el.v.textContent = f(minutes);
    o.el.n.setAttribute("x", f(c[0])); o.el.n.setAttribute("y", f(c[1] - 44 * c[2]));
    o.el.n.setAttribute("font-size", f(60 * c[2])); o.el.m.setAttribute("font-size", f(22 * c[2]));
    o.el.n.setAttribute("opacity", f(S.grow));
    o.el.t.setAttribute("x", f(near[0])); o.el.t.setAttribute("y", f(near[1] + 30)); o.el.t.setAttribute("font-size", f((innerWidth <= 600 ? 28 : 23) * near[2]));
  });
}
/* One frame: the view sways slowly and leans toward the pointer, the columns rise once on load, and a change of the
   switch moves both columns to their height after that round. With reduced motion the page shows one still frame. */
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
  $("svg").setAttribute("aria-label", `Container minutes per batch, ${st.name.toLowerCase()}: ` +
    D.arms.map(a => `${a.name} ${a.minutes[S.state]}, of which ${a.answer[S.state]} produced an answer`).join("; "));
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
$("say").innerHTML = C.line.replace(/(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
build();
draw();
fromHash();
if (still.matches) { S.grow = 1; place(); } else requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}))
