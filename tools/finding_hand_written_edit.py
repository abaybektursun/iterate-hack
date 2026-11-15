"""One hand-written edit to one weight matrix lifts the base model from 45 % to 79 % on MATH-500 (224 to 397 of 500).

The page of one finding, served at /finding/hand-written-edit (view.py serves every tools/finding_<slug>.py) and
reached from its tile on /findings, which ICON draws. The picture is the last weight matrix of the model as a glass
slab seen from slightly above. The hand-written edit is one bright straight line across it; the control, the same edit
with random content, is one dim crooked line. Under the slab stands how one real answer starts in each condition, and
under that the score on a scale. The reader switches between three conditions (address
/finding/hand-written-edit#<condition>, arrow keys) and watches the line, the answer and the score change. The rules
are in .claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md).
"""
import json

TITLE = "Hand-written edit"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Can a useful change be written into the weights by hand?"
LINE = "One hand-written edit to one matrix lifts the base model from 45% to 79% on MATH-500."

# Every number is copied from the artifact named here. None is typed from memory.
RESULTS = "studies/rlneurons/results/wsp2/"
WSP1 = "studies/rlneurons/results/wsp1/"
RLN4 = "studies/rlneurons/results/rln4/grader_v3/readout.json"
DATA = {
    "artifact": RESULTS + "readout.json",  # cells full500/*, and the paired differences in full500_vs_references
    "runs": RESULTS + "full500/",  # one folder per cell: metrics.json, run.json, examples.json, per_problem.json
    "commit": "db7c499c2d35f84f7fea45106a783c8d622f3bbc",  # run.json of jobs sameraslan-1114-221130-eb90 and -221138-a65c
    "metric": "Share of the 500 MATH-500 problems answered right, no cue in the prompt, one sample at temperature 1.0",
    "unit": "%",
    "max": 100,
    "measure": "of 500 math problems answered right",  # the small label over the big number: what it counts
    # What the reader switches between. The first is shown on load: start from the problem, not from the answer.
    # value = right of n as a rounded percentage. opening: the first 120 characters of the answer to problem "problem"
    # in that condition, copied from "rows".
    "problem": 2,
    "prompt_end": "on its own line after \"Answer:\"",  # the last words of every prompt of these runs
    "states": [
        {"key": "base", "name": "Base model", "right": 224, "n": 500,
         "cell": RLN4 + " cells.base_plain_1.0",
         # The 500-problem run of the base model kept no answers, so its opening is from the first-100 run (same model,
         # same prompt, seed 80000002 for this problem).
         "rows": "runs/sameraslan-1114-154255-ff2f/answers.jsonl (" + WSP1 + "screen100/base_plain-01/run.json raw_answers)",
         "opening": ".\nWe can plug in the values $x=-2, -1,$ and $0$ into the given function $f$ to find $f(-2), f(-1),$ and $f(0)$.\n$$f(-2)=",
         "note": "The base model was pretrained on text and never trained with rewards. The slab is its last weight matrix. Nothing is changed yet."},
        {"key": "random", "name": "Random edit", "right": 204, "n": 500,
         "cell": RESULTS + "full500/cueprog_rand_plain-01/metrics.json",  # job sameraslan-1114-221138-a65c, right_v3
         "rows": RESULTS + "full500/cueprog_rand_plain-01/examples.json openings",
         "opening": " for the final answer.\nFirst, I'll compute each value of \\( f(x) \\) for \\( x = -2, -1, \\) and \\( 0 \\).\n\nCalculate \\( f(-",
         "note": "A control: an edit of the same size with random content."},
        {"key": "hand-written", "name": "Hand-written edit", "right": 397, "n": 500,
         "cell": RESULTS + "full500/cueprog_plain-01/metrics.json",  # job sameraslan-1114-221130-eb90, right_v3
         "rows": RESULTS + "full500/cueprog_plain-01/examples.json openings",
         "opening": " line!\n\nOkay, so I need to find the value of f(-2) + f(-1) + f(0) for the function f(x) = (3x - 2)/(x - 2). Hmm, let me ",
         "cue": " line!\n\nOkay",  # the three cue tokens, shown in the accent where the answer starts with them
         "note": "One rule, written into this one matrix: when the answer starts, write the opening cue."},
    ],
    # The strongest baseline drawn as a line: the base model with the cue typed into the prompt.
    "reference": {"name": "Cue typed in the prompt", "right": 410, "n": 500, "cell": RLN4 + " cells.base_opener_1.0"},
    "rl": {"right": 463, "n": 500, "cell": RLN4 + " cells.rl_1.0"},
    "top8": {"right": 427, "n": 500, "cell": WSP1 + "full500/top8_plain-01/metrics.json"},
    # Paired by problem, in points (full500_vs_references.differences of the artifact).
    "vs_cue": {"points": -2.6, "ci95": [-6.4, 1.2], "cell": RESULTS + "readout.json cueprog_plain minus T1_base_cue"},
    # The first-100 screen, against the cue on the same problems.
    "screen": {"right": 85, "cue": 82, "n": 100, "cell": RESULTS + "readout.json cells.screen100/cueprog_plain",
               "cue_cell": WSP1 + "readout.json cells.screen100/base_cue"},
    # The edit itself: "handedit" of the cell's metrics.json (from handedit.json of job sameraslan-1114-221130-eb90).
    # Chance of each cue token at the position where the answer starts, mean over the held-out questions, before and
    # after (positions[*].held_before_mean and held_after_mean); kl is kl_nats, size is fro_dW_over_W.
    "edit": {"source": RESULTS + "full500/cueprog_plain-01/metrics.json handedit", "tensor": "model.layers.31.mlp.down_proj.weight",
             "n_cal": 128, "n_held": 64, "before": [0.000249, 0.005835, 0.286289], "after": [0.952312, 0.951977, 0.951762],
             "kl": 7.154e-05, "size": 0.065794},
    # Answers with "Okay" in their first 80 characters (okay_first80 of the cells' metrics.json). No 500-problem cell of
    # the base model records this count, so the comparison is the control.
    "okay": {"hand-written": 463, "control": 106, "n": 500, "cell": RESULTS + "full500/cueprog_plain-01/metrics.json okay_first80",
             "control_cell": RESULTS + "full500/cueprog_rand_plain-01/metrics.json okay_first80"},
}
for _s in DATA["states"] + [DATA["reference"], DATA["rl"]]:
    _s["value"] = round(100 * _s["right"] / _s["n"])
_value = {s["key"]: s["value"] for s in DATA["states"]}
_e = DATA["edit"]
_vc = DATA["vs_cue"]
_pc = lambda p: f"{100 * p:.0f} %"

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new",
     "The edit is built from a written rule and the base model alone: no trained weights, no reward and no answers.",
     [f"It comes with a control: the same edit with random content scores {_value['random']}%.",
      "It is measured on the same harness as the cue typed into the prompt and as the RL-trained model.",
      "Closest published result: Wang et al. (arXiv 2610.06851, appendix D.5) raised the cue's probability with a "
      "one-matrix edit and scored 78 % on MATH-500."]],
    ["why", "Why it matters",
     "It shows that editing weights by hand works on this model up to what a prompt can do, and no further.",
     [f"The edit reaches the cue: {_value['hand-written']}% against {DATA['reference']['value']}% with the cue typed into the prompt, "
      f"a difference inside the noise of one run ({_vc['points']} points, 95% interval {_vc['ci95'][0]} to {_vc['ci95'][1]}).",
      f"It does not reach the RL-trained model at {DATA['rl']['value']}%, so what RL adds beyond the opening is not in this edit.",
      "The edit is a rule a person can read, which a trained weight change is not."]],
    ["how", "How we know",
     f"We recorded the last layer's activity at the moment the answer starts on {_e['n_cal']} questions, and changed one "
     "matrix so that this moment produces the three cue tokens.",
     [f"On {_e['n_held']} questions the edit never saw, the chance of each cue token rose from "
      f"{_pc(_e['before'][0])}, {_pc(_e['before'][1])} and {_pc(_e['before'][2])} to {_pc(min(_e['after']))}.",
      f"Everywhere else the model's next-word odds barely move (KL divergence {_e['kl']:.5f} nats).",
      f"On their own, {DATA['okay']['hand-written']} of the {DATA['okay']['n']} answers say \"Okay\" in their first 80 "
      f"characters, against {DATA['okay']['control']} for the control."]],
    ["limits", "What it does not show",
     "It does not improve on the cue: it only makes the model start the way the cue makes it start.",
     [f"On the first {DATA['screen']['n']} problems it scored {DATA['screen']['right']} against the cue's {DATA['screen']['cue']}; "
      f"on all 500 it scores {_value['hand-written']}% against {DATA['reference']['value']}%. Both differences are inside the noise, "
      "so it is level with the cue rather than above it.",
      "Only the opening is written in. A habit of checking the work is not.",
      "It is one matrix in one model."]],
    ["run", "How to reproduce it",
     f"Two commands on one GPU reproduce the {_value['hand-written']}%: the first writes the edited weights and the second scores them.",
     ["studies/rlneurons/jobs/wsp_handedit.py --dir /tmp/theta --batch 1",
      "studies/rlneurons/jobs/run_cell.py --model-path /tmp/theta --model-label cueprog --prompt plain --set math500 "
      "--temperature 1.0 --top-p 1.0 --seed 184000000 --commit $(git rev-parse HEAD)",
      "The run used commit " + DATA["commit"] + ". Its numbers are in " + RESULTS + "."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab seen from slightly above with one bright line across it.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, v = b * .12;
  return kit.slab(a, b, th) +
    kit.line(kit.at(-a * .82, v, th / 2), kit.at(a * .82, v, th / 2), 1.5 + .18 * Math.sin(t * .6), "lit");
}"""

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
svg { width: 100%; max-height: 66vh; display: block; overflow: visible; }
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
.lit { fill: url(#fade-c) var(--core); }
.label { fill: var(--mute); font-weight: 600; text-anchor: middle; }
.say-row { fill: var(--ink); font-weight: 400; text-anchor: middle; }
.say-row .prompt { fill: var(--faint); }
.say-row .cue { fill: var(--blue); font-weight: 640; }
.axis { stroke: var(--faint); stroke-width: 1.5; opacity: .5; }
.level { stroke: var(--ink); stroke-width: 2; stroke-linecap: round; }
.head { fill: var(--ink); }
.ref { stroke: var(--ink); stroke-width: 1.5; }
.tick { fill: var(--faint); font-weight: 500; }
.reftext { fill: var(--mute); font-weight: 600; text-anchor: end; }
.value { font-weight: 330; letter-spacing: -.03em; text-anchor: middle; font-stretch: 100%; }
.unit { fill: var(--mute); font-weight: 500; text-anchor: middle; }
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
.enter .opening, .enter .scale { animation: fade .7s .7s both; }

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
  .switch { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); align-self: stretch; border-radius: 24px; }
  .switch button { text-align: center; padding: 9px 4px; font-size: 14px; white-space: normal; line-height: 1.2; border-radius: 20px; }
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
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
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
const S = { state: 0, open: null, g: null, el: null, out: null, uw: 0, cur: null, from: null, goal: null, t0: 0, t: 0, shown: "" };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1), h = n => n.toFixed(2), mix = (a, b, q) => a + (b - a) * q;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
const N = D.max;  // the scale runs from 0 to 100 %

/* What each condition looks like, each value from 0 to 1: jag, the line is crooked; plain, it shows dim; lit, it shows
   in the accent; wash, the slab takes the accent. The picture moves from one look to the next in 0.9 s, so the
   random line straightens and lights up when the reader switches to the hand-written edit. */
const LOOK = {
  "base": { jag: 1, plain: 0, lit: 0, wash: 0 },
  "random": { jag: 1, plain: .62, lit: 0, wash: 0 },
  "hand-written": { jag: 0, plain: 0, lit: 1, wash: .55 },
};
/* The crooked line of the random edit: offsets toward the viewer, in units of the slab's half depth, at evenly spaced
   points from its left end to its right end. */
const JAG = [.34, -.2, .3, -.36, .16, -.1, .42, -.26, .06];
const ROW = .12;  // where the straight line lies, in units of the slab's half depth toward the viewer

/* Geometry: the slab lives in a small 3D space around one centre (x right, y down, z toward the viewer), as in
   architecture.py. It lies back by TILT degrees, so it is seen from slightly above. u runs to its right, v toward the
   viewer and w out of its top face. The answer and the score lie flat on the screen under it. */
const RAD = Math.PI / 180, TILT = 58, PC = Math.cos(TILT * RAD), PS = Math.sin(TILT * RAD);
function geo() {
  return narrow.matches
    ? { w: 720, h: 860, cx: 360, cy: 196, a: 190, b: 150, th: 20, r: 20, D: 1900, yaw: -4, lw: 2.6, glow: 5.5, x0: 76, x1: 632, ay: 776, num: 124, fl: 25, oy: 372, ofs: 25, olh: 36, chars: 46 }
    : { w: 1000, h: 740, cx: 500, cy: 236, a: 270, b: 200, th: 26, r: 28, D: 2100, yaw: -8, lw: 2.2, glow: 9, x0: 140, x1: 860, ay: 690, num: 100, fl: 18, oy: 438, ofs: 19, olh: 29, chars: 78 };
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

/* How one real answer starts: the last words of the prompt, faint, then the first characters of the model's answer
   to the same problem in this condition (D.states[i].opening). Line breaks become spaces. The cue tokens, where the
   answer starts with them, are in the accent. Wrapped into at most three rows. */
function opening(st, chars) {
  // A word is a list of parts [text, class]. The answer joins the last word of the prompt with no space when it
  // starts with a mark (".") rather than a space, as in the real text.
  const text = st.opening.replace(/\s+/g, " "), cue = st.cue ? st.cue.replace(/\s+/g, " ").length : 0;
  const words = ("…" + D.prompt_end).split(" ").map(w => [[w, "prompt"]]);
  let at = 0;
  text.split(" ").forEach((w, i) => {
    if (w) {
      const part = [w, at < cue ? "cue" : ""];
      if (i === 0) words[words.length - 1].push(part); else words.push([part]);
    }
    at += w.length + 1;
  });
  const size = word => word.reduce((s, p) => s + p[0].length, 0), rows = [[]];
  let len = 0, cut = false;
  for (const word of words) {
    if (len && len + 1 + size(word) > chars) {
      if (rows.length === 3) { cut = true; break; }
      rows.push([]); len = 0;
    }
    rows[rows.length - 1].push(word);
    len += (len ? 1 : 0) + size(word);
  }
  const tail = rows[rows.length - 1];
  if (cut || st.opening.length >= 120) tail[tail.length - 1].push(["…", ""]);
  return rows.map(r => r.map((word, j) => (j ? " " : "") +
    word.map(([s, k]) => k ? `<tspan class="${k}">${esc(s)}</tspan>` : esc(s)).join("")).join(""));
}

/* The picture is built once per layout; place() then sets everything that depends on the view and on the condition.
   Back to front: the light around the slab, its body, its top face, the light inside it, the line, the rim, the
   answer, and the score on its scale. */
function build() {
  const g = S.g = geo(), svg = $("svg"), ref = D.reference, x = v => g.x0 + (g.x1 - g.x0) * v;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const fade = (id, color) => `<linearGradient id="${id}" gradientUnits="userSpaceOnUse">${stop(0, color, .5)}${stop(1, color, 1)}</linearGradient>`;
  const rx = x(ref.value / N);
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.42, "var(--blue)", .24)}${stop(.7, "var(--blue)", .07)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    fade("fade-c", "var(--core)") + fade("fade-n", "var(--ink)") + "</defs>" +
    `<g class="atmo"><ellipse id="glow" cx="${g.cx}" cy="${f(g.cy + g.b * .08)}" rx="${f(g.a * 1.7)}" ry="${f(g.b * PC * 2.2)}" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${f(g.cx + g.a * .07)}" cy="${f(g.cy + g.b * PC * .22 + g.th)}" rx="${f(g.a * 1.25)}" ry="${f(g.b * PC * 1.36)}" fill="url(#shade)"/></g>` +
    `<path class="body" id="side"/><g class="edge"><path id="edge" opacity="0"/></g>` +
    `<path class="face" id="face"/><g class="wash"><path id="wash" opacity="0"/></g>` +
    `<g class="spec"><ellipse id="shine" rx="${f(g.a * .5)}" ry="${f(g.b * PC * .4)}" fill="url(#spec)"/></g>` +
    `<path class="plain" id="plain"/><g class="bloom"><path class="halo" id="halo"/></g><path class="lit" id="lit"/>` +
    `<path class="rim draw" id="rim" pathLength="1"/>` +
    `<g class="opening"><text class="label" x="${g.cx}" y="${g.oy}" font-size="${f(g.ofs * .78)}">How one answer starts</text>` +
    [0, 1, 2].map(i => `<text class="say-row" id="row-${i}" x="${g.cx}" y="${f(g.oy + g.olh * (i + 1.15))}" font-size="${g.ofs}"></text>`).join("") + `</g>` +
    `<g class="scale"><line class="axis" x1="${g.x0}" y1="${g.ay}" x2="${g.x1}" y2="${g.ay}"/>` +
    `<text class="tick" x="${g.x0 - 12}" y="${f(g.ay + g.fl * .35)}" font-size="${g.fl}" style="text-anchor:end">0</text>` +
    `<text class="tick" x="${g.x1 + 12}" y="${f(g.ay + g.fl * .35)}" font-size="${g.fl}">${N}</text>` +
    `<line class="ref" x1="${f(rx)}" y1="${f(g.ay - g.fl * .7)}" x2="${f(rx)}" y2="${f(g.ay + g.fl * .55)}"/>` +
    `<text class="reftext" x="${f(rx + 4)}" y="${f(g.ay + g.fl * 1.75)}" font-size="${g.fl}">${esc(ref.name)} ${ref.value}${esc(D.unit)}</text>` +
    `<line class="level" id="level" x1="${g.x0}" y1="${g.ay}" y2="${g.ay}"/><circle class="head" id="head" cy="${g.ay}" r="${f(g.fl * .32)}"/>` +
    `<text class="value" id="value" y="${f(g.ay - g.num * .2)}" font-size="${g.num}"></text>` +
    `<text class="unit" id="unit" y="${f(g.ay - g.num * 1.06)}" font-size="${g.fl}">${esc(D.measure)}</text></g>`;
  S.el = {};
  ["glow", "side", "edge", "face", "wash", "shine", "plain", "halo", "lit", "rim", "fade-c", "fade-n", "level", "head", "value", "unit", "row-0", "row-1", "row-2"].forEach(id => { S.el[id] = $(id); });
  S.out = outline(g);
  S.shown = "";
  S.uw = 0;
  if (S.cur) say();
}
function say() {  // the answer of the chosen condition
  const rows = opening(D.states[S.state], S.g.chars);
  [0, 1, 2].forEach(i => { S.el["row-" + i].innerHTML = rows[i] || ""; });
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
  set(E.side, { d: body }); set(E.edge, { d: body, opacity: h(Math.min(1, .4 * c.lit + .6 * c.wash)) });
  E.glow.setAttribute("opacity", h(.45 + .3 * c.lit + .25 * c.wash));
  const shine = at(-g.a * .36, -g.b * .34, top);
  set(E.shine, { cx: f(shine[0]), cy: f(shine[1]) });
  const far = at(0, -g.b, top), near = at(0, g.b, top);  // lines are faint at the back and full in front
  [E["fade-c"], E["fade-n"]].forEach(el => set(el, { x1: f(far[0]), y1: f(far[1]), x2: f(near[0]), y2: f(near[1]) }));

  // The one line: crooked for the random edit, straight across the slab for the hand-written edit.
  const n = JAG.length, pts = [];
  for (let i = 0; i < n; i++) {
    const u = g.a * .84 * (2 * i / (n - 1) - 1), v = g.b * mix(ROW, JAG[i], c.jag);
    pts.push(at(u, v, top));
  }
  const breath = 1 + .1 * Math.sin(t * .55);
  let plain = "", lit = "", halo = "";
  for (let i = 0; i < n - 1; i++) {
    if (c.plain > .01) plain += seg(pts[i], pts[i + 1], g.lw * .7);
    if (c.lit > .01) { lit += seg(pts[i], pts[i + 1], g.lw * 2 * breath); halo += seg(pts[i], pts[i + 1], g.lw * g.glow * breath); }
  }
  set(E.plain, { d: plain, opacity: h(c.plain) });
  set(E.lit, { d: lit, opacity: h(c.lit) });
  set(E.halo, { d: halo, opacity: h(.3 * c.lit) });

  // The score: one number that moves along the scale.
  const x = g.x0 + (g.x1 - g.x0) * c.v / N, text = String(Math.round(c.v)) + D.unit;
  set(E.level, { x2: f(x) }); set(E.head, { cx: f(x) }); set(E.value, { x: f(x) });
  if (!S.uw) S.uw = E.unit.getComputedTextLength();  // the label over the number follows it, and stays inside the picture
  set(E.unit, { x: f(Math.min(g.w - S.uw / 2 - 4, Math.max(S.uw / 2 + 4, x))) });
  if (text !== S.shown) E.value.textContent = S.shown = text;
}

/* Motion that is always on: the view sways by a few degrees and leans toward the mouse, and the lit line breathes.
   With reduced motion the page shows one still frame and a condition changes at once. */
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
  $("svg").setAttribute("aria-label", `${D.metric}: ${st.name} ${st.value} of ${N}, ${ref.name} ${ref.value} of ${N}.`);
  $("note").textContent = st.note;
  $("switch").querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-pressed", k === i));
  say();
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
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
$("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}" aria-pressed="false">${esc(s.name)}</button>`).join("");
build();
aim(S.g.yaw, 0);  // the still frame
fromHash(true);
if (document.fonts) document.fonts.ready.then(() => { S.uw = 0; place(S.t); });  // measure the label again in Archivo
if (!still.matches) {
  $("svg").classList.add("enter");
  setTimeout(() => $("svg").classList.remove("enter"), 2200);
  requestAnimationFrame(frame);
}
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}))
