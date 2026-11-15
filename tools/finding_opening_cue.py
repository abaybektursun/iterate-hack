"""Three opening tokens raise the base model Olmo-3-1025-7B from 224 to 410 right answers of 500 on MATH-500 (44.8 % to 82.0 %).

The page of one finding, served at /finding/opening-cue (copied from .claude/skills/finding-page/template.py; draw() is
replaced by a glass bar with depth, and above it the start of the answer, where the cue appears in front of the text).
It is reached from its tile on /findings, which ICON draws. Study: studies/rlneurons (README.md "Definitions",
"Established numbers" and "Day-1 #3"; board result-c36598 and result-60d899). The cue is published (Wang et al., arXiv
2610.06851); what this page adds is the share of the RL gain that the cue covers at temperature 1.0, and that the gap
left to the RL model depends on the sampling temperature (board result-bac4fd, result-dadeec, result-44b4df).
"""
import json

# Every number is copied from the artifacts named here. None is typed from memory.
DATA = {
    "artifact": "studies/rlneurons/results/rln4/grader_v3/readout.json",  # cells.<name>: right_v3, right_v1, nothing_extracted_v3, cap_hits
    "commit": "fe1c61e",
    "n": 500,
    "plain": {"right": 224, "right_v1": 196, "nothing_extracted": 129, "cap_hits": 8},   # cells.base_plain_1.0
    "cue": {"right": 410, "right_v1": 389, "nothing_extracted": 25, "cap_hits": 27},      # cells.base_opener_1.0
    "plain_t06": {"right": 319},  # cells.base_plain_0.6 (T 0.6 / top-p 0.95)
    # The same pair at T 0.6 / top-p 0.95: cells.base_opener_0.6 (right_v3, cap_hits) and cells.rl_0.6.
    "t06": {"cue": 354, "cue_cap_hits": 119, "rl": 464},
    # Paired differences in points with their 95 % intervals (differences_v3: diff_points, ci95), each as [points, low, high]:
    # rl_0.6 - base_opener_0.6 and rl_1.0 - base_opener_1.0.
    "gap": {"t06": [22.0, 18.4, 25.8], "t10": [10.6, 7.4, 13.8]},
    # T 0.6 / top-p 1.0: rows.math500_base_cue_t06_p10-01 (right_v3, cap_hits, loops_A, the loop detector rule A).
    "t06_p10_artifact": "studies/rlneurons/results/day1/readout.json",
    "t06_p10_commit": "3407c6e",
    "t06_p10": {"right": 378, "cap_hits": 98, "loops": 71},
    # Loops at T 1.0: cells.T1_base_cue.loops_A, and cells.base_mp0.1_T1.loops_A where min-p 0.1 cuts off the unlikely tokens.
    "minp_artifact": "studies/rlneurons/results/day1_minp/readout.json",
    "minp_commit": "d1f5a23",
    "minp": {"loops_t10": 0, "loops_cut": 34},
    "rl_first": {"right": 463},   # cells.rl_1.0: the RL reference, the RL model's cell in the same artifact, T 1.0 / top-p 1.0
    # A later RL run: rows.single.right and each_sample.single_right of the four-sample run at T 1.0 / top-p 1.0.
    "rl_artifact": "studies/rlneurons/results/day1_3/math500_rl-01/readout.json",
    "rl_commit": "d1f0136",
    "rl": {"right": 456, "samples": [456, 462, 464, 458]},
    # The repeat of the cue cell: each_sample.single_right (sample 0 has the seeds of the cell above).
    "repeat_artifact": "studies/rlneurons/results/day1_3/math500_base_cue-01/readout.json",
    "repeat": {"samples": [405, 409, 410, 418]},
    # The later steps of the climb: rows.tie_short.right of the base model with the cue and of the RL model.
    "vote_artifact": "studies/rlneurons/results/selector/math500_base_cue-01/readout.json",
    "vote_rl_artifact": "studies/rlneurons/results/selector/math500_rl-01/readout.json",
    "vote": {"cue": 453, "rl": 475},
    # 328 harder problems: rows.hard328_base_cue_t10-01.right_v3 and rows.hard328_rl_plain_t10-01.right_v3.
    "hard_artifact": "studies/rlneurons/results/day1/readout.json",
    "hard": {"cue": 164, "rl": 206, "n": 328},
    # The cue: prefill_ids (three token ids), prefill_text and cap.
    "cue_artifact": "studies/rlneurons/data/rln4/frozen4.json",
    "cue_text": " line!\n\nOkay",
    "cue_tokens": 3,
    "cap": 16384,
    # From the paper (Wang et al., arXiv 2610.06851, read in full: board knowledge-8a31ad), in percent on MATH-500 at T 0.6.
    # "rl" is the paper's RL model, the earlier release Olmo-3-7B-RL-Zero-Math (its Table 6).
    "paper": {"plain": 42.2, "cue": 77.9, "rl": 75.0},
}
N = DATA["n"]


def pc(right, n=N):
    """Right answers as a percentage with one decimal."""
    return round(100 * right / n, 1)


PLAIN, CUE, RL = DATA["plain"]["right"], DATA["cue"]["right"], DATA["rl_first"]["right"]
RL_LATER = DATA["rl"]["right"]                                 # the first sample of the later four-sample RL run
SHARE = round(100 * (CUE - PLAIN) / (RL - PLAIN))              # 186 of 239 right answers
SHARE_LATER = round(100 * (CUE - PLAIN) / (RL_LATER - PLAIN))  # 186 of 232
LEFT = [round(pc(RL_LATER) - pc(CUE), 1), round(pc(RL) - pc(CUE), 1)]  # points still to RL

TITLE = "The opening cue"
PROBLEM = "Does solving math need RL training?"
LINE = f"Three opening tokens raise the base model from {pc(PLAIN)} % to {pc(CUE)} % on MATH-500."  # also the sentence on its tile

DATA.update({
    "metric": "MATH-500, right answers of 500, one sample at temperature 1.0",
    "unit": "%",
    "max": 100,
    # What the reader switches between. The first is shown on load, so the page starts from the problem.
    "states": [
        {"name": "No cue", "value": pc(PLAIN), "say": "The base model answers the plain prompt."},
        {"name": "Cue", "value": pc(CUE), "say": "The answer is made to start with the cue: line!, two line breaks, Okay."},
    ],
    # The strongest baseline, drawn as a frame around the bar.
    "reference": {"name": "After RL", "value": pc(RL)},
})

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
# [[words|/path]] in a fact becomes a link to another page of the site.
T06, G06, G10 = DATA["t06"], DATA["gap"]["t06"], DATA["gap"]["t10"]
PANELS = [
    ["new", "What is new",
     f"The cue is a replication of Wang et al. (arXiv 2610.06851), who report that a short opening cue takes the Olmo 3 base "
     f"model from {DATA['paper']['plain']} % to {DATA['paper']['cue']} % on MATH-500 at temperature 0.6.",
     [f"New here: how far the base model with the cue stays behind the RL model depends on the sampling temperature. The gap "
      f"is {G06[0]} points at temperature 0.6 (95 % interval {G06[1]} to {G06[2]}) and {G10[0]} points at temperature 1.0 "
      f"({G10[1]} to {G10[2]}).",
      f"Only the base model moves. With the cue it has {T06['cue']} right answers of {N} at temperature 0.6 and {CUE} at 1.0, "
      f"and the RL model has {T06['rl']} and {RL}.",
      f"The paper ran temperature 0.6 only, and its RL model is an earlier release that scores {DATA['paper']['rl']} %, which "
      f"the cue already matched, so it had no gap to explain. Against the later release used here, the cue covers "
      f"{CUE - PLAIN} of the {RL - PLAIN} answers that RL training adds at temperature 1.0: {SHARE} %."]],
    ["why", "Why it matters",
     f"Most of what RL training adds on this benchmark is reached with no training, so the work that follows is about the "
     f"remaining {LEFT[0]} to {LEFT[1]} points.",
     [f"The temperature decides how large that remainder looks. About half of the {G06[0]} points seen at temperature 0.6 are "
      f"gone at 1.0, where far fewer of the base model's answers run to the token cap ({DATA['cue']['cap_hits']} of {N} "
      f"against {T06['cue_cap_hits']}).",
      f"It is the first and largest step of the team's climb on MATH-500. With a vote over four samples the base model with "
      f"the cue reaches {DATA['vote']['cue']} of {N} ({pc(DATA['vote']['cue'])} %), and the RL model {DATA['vote']['rl']} "
      f"({pc(DATA['vote']['rl'])} %) under the same rule.",
      f"Harder problems leave more to explain: on {DATA['hard']['n']} of them the base model with the cue has "
      f"{DATA['hard']['cue']} right and the RL model {DATA['hard']['rl']}."]],
    ["how", "How we know",
     f"The base model Olmo-3-1025-7B answered the {N} problems of MATH-500 twice, once with the plain prompt and once with "
     "the cue placed after the prompt as the start of its answer, and the same grader scored both.",
     [f"Plain prompt: {PLAIN} of {N} right ({pc(PLAIN)} %). With the cue: {CUE} of {N} ({pc(CUE)} %). Both runs take one sample "
      f"per problem at temperature 1.0 and top-p 1.0, with a cap of {DATA['cap']:,} generated tokens, scored by grader v3.",
      f"The control is the plain prompt on the same weights. The reference is the RL model Olmo-3.1-7B-RL-Zero-Math with the "
      f"plain prompt at the same setting: {RL} of {N} ({pc(RL)} %) in the run shown, and {DATA['rl']['samples'][0]}, "
      f"{DATA['rl']['samples'][1]}, {DATA['rl']['samples'][2]} and {DATA['rl']['samples'][3]} in the four samples of a later run. "
      f"A repeat of the cue run on the same seeds gave {DATA['repeat']['samples'][0]} right, and three further samples "
      f"{DATA['repeat']['samples'][1]}, {DATA['repeat']['samples'][2]} and {DATA['repeat']['samples'][3]}.",
      f"Temperature: at 0.6 with top-p 0.95 the base model with the cue has {T06['cue']} right, and {T06['cue_cap_hits']} of its "
      f"answers run to the token cap. At 0.6 with top-p 1.0 it has {DATA['t06_p10']['right']} right, and a loop detector finds "
      f"{DATA['t06_p10']['loops']} answers that repeat themselves. At 1.0 the detector finds {DATA['minp']['loops_t10']}, and "
      f"cutting off the unlikely tokens again brings {DATA['minp']['loops_cut']} back. The page "
      "[[Restarting stuck answers|/finding/restart-on-cap]] shows what a restart recovers."]],
    ["limits", "What it does not show",
     f"The score above the paper's {DATA['paper']['cue']} % is a grader effect rather than a better cue: under our first "
     f"grader, the closest to the paper's, the same answers score {DATA['cue']['right_v1']} of {N} ({pc(DATA['cue']['right_v1'])} %).",
     ["Why the RL model keeps its score at the lower temperature is untested. Its release was trained with cut-off answers "
      "counted as failures, which is one possible reason.",
      f"The size of the step also depends on the temperature. At temperature 0.6 the plain base model has "
      f"{DATA['plain_t06']['right']} right of {N}. Against that setting the cue at temperature 1.0 adds "
      f"{round(pc(CUE) - pc(DATA['plain_t06']['right']), 1)} points, where the picture shows {round(pc(CUE) - pc(PLAIN), 1)}.",
      f"Part of the gain is answers that end in a readable form. With the plain prompt {DATA['plain']['nothing_extracted']} of "
      f"{N} answers hold no final answer that the grader can find, and with the cue {DATA['cue']['nothing_extracted']}. "
      "It is one pair of models, one benchmark and one sample per problem."]],
    ["run", "How to reproduce it",
     "One command runs the cue on one GPU, and the same command with --prompt plain runs the control.",
     ["uv run tools/gpu.py submit h100 --hours 2 -- \"bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python "
      "-m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 "
      "--seed 41000000 --commit $(git rev-parse HEAD)\"",
      f"The two numbers in the picture are in {DATA['artifact']} (cells base_plain_1.0 and base_opener_1.0, commit "
      f"{DATA['commit']}), written by studies/rlneurons/grader/rln4_grader_v3.py from the first runs. The RL reference is the "
      f"cell rl_1.0 of the same file, which also holds the cells and differences at temperature 0.6. The later RL run is in "
      f"{DATA['rl_artifact']} (commit {DATA['rl_commit']}), and the loop counts are in {DATA['t06_p10_artifact']} and "
      f"{DATA['minp_artifact']}.",
      f"The cue's three token ids and its text are frozen in {DATA['cue_artifact']} (prefill_ids, prefill_text). The paper's "
      "cue has two tokens. The cue here has three, the text \" line!\", two line breaks and \"Okay\", and it is how the RL "
      "model opens its own answers."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with three lines of an answer on it; the start of the first line, the cue, is lit.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, top = th / 2, at = (u, v) => kit.at(a * u, b * v, top);
  return kit.slab(a, b, th) +
    kit.line(at(-.78, .34), at(-.36, .34), 1.7 + .16 * Math.sin(t * .6), "lit") +
    kit.line(at(-.2, .34), at(.78, .34), .8) +
    kit.line(at(-.78, 0), at(.78, 0), .8) +
    kit.line(at(-.78, -.34), at(.3, -.34), .8);
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
/* The tokens and the light of architecture.py. Dark is the hero: lit glass in a dark room. Light is the same object as
   white porcelain on a cool grey table, with a cast shadow in place of the glow. The light comes from the upper left. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0;
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
svg { width: 100%; max-height: 62vh; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 104%; }
.atmo, .shade { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.g-top { fill: var(--glass); }
.g-front { fill: url(#body) var(--sheet); }
.g-end { fill: var(--glass-lo); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1.3; stroke-linejoin: round; }
.lit-front { fill: var(--blue); }
.lit-top { fill: color-mix(in oklab, var(--blue) 62%, white); }
.ref { fill: none; stroke: var(--ink); stroke-width: 1.6; stroke-linejoin: round; stroke-linecap: round; }
.ref.back { stroke-width: 1; opacity: .55; }
.reft { fill: var(--mute); font-size: 22px; font-weight: 520; text-anchor: middle; }
.reft tspan { fill: var(--ink); font-weight: 640; }
.num { font-weight: 620; text-anchor: end; letter-spacing: -.01em; }
.cuet { fill: var(--blue); font-size: 34px; font-weight: 640; }
.ret { fill: none; stroke: var(--blue); stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
.stroke { stroke: var(--mute); stroke-linecap: round; opacity: .62; }
.switch { display: inline-flex; align-self: center; margin-top: 22px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 20px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }

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
  .stage { order: 3; margin-top: 18px; padding: 0; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
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
    <svg id="svg" viewBox="0 0 1000 400" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="The start of the answer"></div>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const S = { state: 0, open: null, q: 0, from: 0, t0: -1e9, grow: 0, shown: "" };
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q, ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const pct = v => `${f(v)} %`;

/* The picture. The body is one glass bar seen from slightly above: its whole length is 100 % of MATH-500, the lit
   part is the base model's score, and the frame around it is the RL model's score. The fine lines above the bar are
   the start of the model's answer. With "Cue" the three tokens of the cue appear in front of the answer, the answer
   moves to the right, and the lit part grows. A phone gets a narrower drawing with the same type sizes. */
let G;
const V = { sx: .4, sy: .5, px: 0, py: 0, tx: 0, ty: 0 };  // the view: how far the back of the bar is shifted right and up
function layout() {
  const n = narrow.matches, W = n ? 560 : 1000, L = n ? 22 : 60;
  G = { W, H: 400, L, BL: W - 2 * L - 26, Y0: 318, HT: 60, DP: 46, Y1: 64, big: n ? 68 : 78, cue: 0 };
}
const proj = (u, v, w) => [G.L + u + v * V.sx, G.Y0 - w - v * V.sy];  // u along the bar, v away from the viewer, w up
const path = (pts, open) => "M" + pts.map(p => { const q = proj(...p); return f(q[0]) + " " + f(q[1]); }).join("L") + (open ? "" : "Z");
const ret = (x, y) => `M${f(x + 18)} ${y - 23}v12h-14m5 -5l-5 5l5 5`;  // the mark of a line break
function strokes(id, y, lens, upto, w) {
  let x = G.L, out = "";
  for (let i = 0; x < upto; i++) { const n = lens[i % lens.length]; out += `<line class="stroke" x1="${x}" y1="${y}" x2="${x + n}" y2="${y}" stroke-width="${w}"/>`; x += n + 20; }
  return `<g id="${id}">${out}</g>`;
}
function build() {
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const ref = D.reference, y = G.Y1 - 11;
  $("svg").setAttribute("viewBox", `0 0 ${G.W} ${G.H}`);
  $("svg").innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.2, "var(--blue)", .22)}${stop(.65, "var(--blue)", .07)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.5, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<linearGradient id="fadeg" gradientUnits="userSpaceOnUse" x1="${G.L}" y1="0" x2="${G.L + G.BL}" y2="0">${stop(0, "#fff", 1)}${stop(.5, "#fff", .55)}${stop(1, "#fff", 0)}</linearGradient>` +
    `<mask id="fade" maskUnits="userSpaceOnUse" x="0" y="0" width="${G.W + 400}" height="140"><rect width="${G.W + 400}" height="140" fill="url(#fadeg)"/></mask></defs>` +
    `<g class="atmo"><ellipse id="glow" cy="${G.Y0 - 44}" ry="120" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${G.L + G.BL / 2 + 18}" cy="${G.Y0 + 14}" rx="${G.BL / 2 + 36}" ry="34" fill="url(#shade)"/></g>` +
    `<g id="answer"><g id="cue"><text class="cuet" id="cue-a" y="${G.Y1}">line!</text><path class="ret" id="ret1"/><path class="ret" id="ret2"/>` +
    `<text class="cuet" id="cue-b" y="${G.Y1}">Okay</text></g>` +
    `<g mask="url(#fade)">${strokes("row1", y, [118, 64, 150, 86, 132, 58, 104, 140, 76], G.W, 6)}</g>` +
    `<g mask="url(#fade)">${strokes("row2", y + 36, [92, 140, 60, 126, 82, 150], G.L + G.BL * .6, 6)}</g></g>` +
    `<path class="ref back" id="ref-back"/>` +
    `<path class="g-top" id="g-top"/><path class="g-end" id="g-end"/><path class="g-front" id="g-front"/>` +
    `<path class="lit-top" id="lit-top"/><path class="lit-front" id="lit-front"/>` +
    `<path class="rim" id="rim-top"/><path class="rim" id="rim-end"/><path class="rim" id="rim-front"/>` +
    `<path class="ref" id="ref-front"/>` +
    `<text class="reft" id="reft" y="${G.Y0 + 52}">${esc(ref.name)} <tspan>${pct(ref.value)}</tspan></text>` +
    `<text class="num" id="num" font-size="${G.big}"></text>`;
  S.shown = "";
}
function fit() {  // the cue is laid out from the measured width of its two words, again when the typeface has loaded
  const a = $("cue-a"), b = $("cue-b");
  let x = G.L;
  a.setAttribute("x", x); x += a.getComputedTextLength() + 10;
  $("ret1").setAttribute("d", ret(x, G.Y1)); x += 28;
  $("ret2").setAttribute("d", ret(x, G.Y1)); x += 30;
  b.setAttribute("x", x); G.cue = x + b.getComputedTextLength() - G.L;
}
function place() {
  const q = S.q, value = mix(D.states[0].value, D.states[1].value, q), B = G.BL, H = G.HT, P = G.DP;
  const F = B * value * S.grow / D.max, R = B * D.reference.value / D.max, set = (id, d) => $(id).setAttribute("d", d);
  const top = path([[0, 0, H], [B, 0, H], [B, P, H], [0, P, H]]), end = path([[B, 0, 0], [B, P, 0], [B, P, H], [B, 0, H]]);
  const front = path([[0, 0, 0], [B, 0, 0], [B, 0, H], [0, 0, H]]);
  set("g-top", top); set("rim-top", top); set("g-end", end); set("rim-end", end); set("g-front", front); set("rim-front", front);
  set("lit-top", path([[0, 0, H], [F, 0, H], [F, P, H], [0, P, H]]));
  set("lit-front", path([[0, 0, 0], [F, 0, 0], [F, 0, H], [0, 0, H]]));
  // The RL model's score is a thin frame around the bar: its far side is drawn behind the bar, its near side in front.
  set("ref-back", path([[R, 0, -9], [R, P, -9], [R, P, H + 9], [R, 0, H + 9]], true));
  set("ref-front", path([[R, 0, -9], [R, 0, H + 9], [R, P, H + 9]], true));
  $("reft").setAttribute("x", f(Math.min(proj(R, 0, 0)[0], G.W - 90)));
  $("glow").setAttribute("cx", f(G.L + F / 2)); $("glow").setAttribute("rx", f(F / 2 + 80));
  const text = pct(value * S.grow), n = $("num");  // the number ends where the lit part ends
  if (text !== S.shown) { n.textContent = text; S.shown = text; }
  n.setAttribute("x", f(Math.max(G.L + G.big * 2.75, proj(F, P, H)[0])));
  n.setAttribute("y", f(proj(0, P, H)[1] - 22));
  $("cue").setAttribute("opacity", f(q * S.grow)); $("cue").setAttribute("transform", `translate(${f((q - 1) * 18)} 0)`);
  $("row1").setAttribute("transform", `translate(${f(q * (G.cue + 22))} 0)`);
  $("answer").setAttribute("opacity", f(S.grow));
}
/* One frame: the view sways slowly and leans toward the pointer, the lit part rises once on load, and a change of the
   switch moves it to its new length. With reduced motion the page shows one still frame. */
function frame(now) {
  const t = now / 1000;
  V.px += (V.tx - V.px) * .06; V.py += (V.ty - V.py) * .06;
  V.sx = .4 + .05 * Math.sin(t * .25) + .08 * V.px; V.sy = .5 + .03 * Math.sin(t * .19 + 1) - .05 * V.py;
  S.t1 ??= now;  // the entrance starts with the first frame that is shown, so a tab opened in the background still plays it
  S.grow = ease(Math.min(1, (now - S.t1) / 1300));
  S.q = mix(S.from, S.state, ease(Math.min(1, (now - S.t0) / 900)));
  place();
  if (!still.matches) requestAnimationFrame(frame);
}
function draw() {  // the switch and the label follow the state; the bar and the cue follow in frame()
  const st = D.states[S.state], ref = D.reference;
  $("svg").setAttribute("aria-label", `${D.metric}. ${st.say} Base model ${pct(st.value)}, ${ref.name} ${pct(ref.value)}.`);
  $("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}" aria-pressed="${i === S.state}">${esc(s.name)}</button>`).join("");
}
function choose(i) {
  if (i === S.state) return;
  S.from = S.q; S.state = i; S.t0 = still.matches ? -1e9 : performance.now();
  draw();
  if (still.matches) { S.grow = 1; S.q = i; place(); }
}
function setup() { layout(); build(); fit(); if (still.matches) { S.grow = 1; S.q = S.state; } place(); }
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x).replace(/\[\[([^|\]]+)\|([^\]]+)\]\]/g, '<a href="$2">$1</a>')}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
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
$("stage").addEventListener("pointermove", e => {  // the view leans a little toward a mouse, and settles back
  if (e.pointerType !== "mouse") return;
  const r = $("stage").getBoundingClientRect();
  V.tx = 2 * (e.clientX - r.left) / r.width - 1; V.ty = 2 * (e.clientY - r.top) / r.height - 1;
});
$("stage").addEventListener("pointerleave", () => { V.tx = V.ty = 0; });
narrow.addEventListener("change", setup);
document.fonts.ready.then(() => { fit(); place(); });
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");  // a number inside a name (MATH-500) stays plain
setup();
draw();
fromHash();
if (!still.matches) requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}))
