"""Switching off 1,000 of a 7B model's 352,256 neurons cuts its repetition loops on MATH-500 from 71 to 19 of 500, at the same accuracy.

The page of one finding, served at /finding/loop-neurons (view.py serves every tools/finding_<slug>.py) and reached
from its tile on /findings, which ICON draws. The picture is one lit plate with 500 dots, one per MATH-500 problem in
the order of the benchmark: right, wrong, or stuck in a loop. The reader switches between three versions of the model
(address /finding/loop-neurons#<condition>, arrow keys); each dot changes in place, and three numbers follow: loops,
right answers, tokens per problem. The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of
tools/architecture.py (.claude/skills/site-ui/SKILL.md). The numbers are those of studies/cleanneurons/README.md,
Parts G, L and I.

    python3 tools/finding_loop_neurons.py    checks DATA against the artifacts it was copied from
"""
import json

GEN = "studies/cleanneurons/results/gen/"

# Every number is copied from the artifacts named here. None is typed from memory. The deployed site ships only
# tools/*.py, so the copy is a literal; run this file to compare it with the artifacts.
# A grid is page_grid.json's string for one cell: character i is MATH-500 problem i. r right (grader v3), w wrong with
# no loop, l stuck in a loop (rule A), b a loop in an answer that is right (one problem; drawn as a loop).
DATA = {
    "artifact": GEN + "readout_t06.json",  # baseline and arms.<arm>: right_v3, loops_rule_A, tokens_per_problem
    "grid": GEN + "page_grid.json",  # arms.<arm>.grid, written by studies/cleanneurons/analysis/page_grid.py
    "commit": "53c42d2",  # git rev-parse --short HEAD when the numbers were read
    "run_commit": "84aab2f67ef7d0f43ac823a6f53c8b679d8f6653",  # results/gen/attr1000_t06-01/run.json
    "edit": "studies/cleanneurons/results/loops/real-01/edit_attr1000.json",  # results/gen/attr1000_t06-01/build.json
    "model": "allenai/Olmo-3-1025-7B",
    "neurons": 352256,  # results/loops/real-01/metrics.json: model.layers 32 x model.neurons 11,008
    "off": 1000,  # results/gen/attr1000_t06-01/build.json: neurons_zeroed
    "n": 500,
    # What the reader switches between. The first is shown on load: start from the problem, not from the answer.
    "states": [
        {"key": "unedited", "name": "Unedited", "arm": "baseline", "job": "sameraslan-1114-184603-9d69",
         "right": 378, "loops": 71, "tokens": 4689.678,
         "grid": "rrrrrrrrrlrwrrwrrllrrlrrrwwrrrwrwrrrrrrrrwrlrrrrrrwrrrrrrrrrrrrrlrrrrlrlrrwrrrrrwrlrrrrrrrlrrrwrlrrl"
                 "lwrwwrrrrllrrrrrrrrlrrrrrrlrwrrrrrrrrllrrrrrrlrlrrllrrlrlrrrrrlrrrlrlrrrrrrrlrrrrwrlrrrrrrwrrrrrrlrr"
                 "rrlrwlrrrrlrrrwrrlrlrrlrllrrlrrrrrrrrrrwlrwrrrrrlrrrrrrrrrrrrrrrwrrrrrrrrrlrrrrrrwrrrwlrwrrrrrrwrrwr"
                 "rrwwrrlrllrrrrrrrwrrrrrllrwrlrrrllrrrrrwwlrrrrrrrlrrwrrrrrwrrrrrrlrrrlrrwrrrllrwrlrrrwrrrlrrlrrrrrwr"
                 "lwrwrrlrrlrrrrrrrrrrwrlrrwrrrrrrlrrrrrrrrrrrwwrrrrrrrrrrwrrrlrlrrrlrrrrrrrrrrrwrrwrlrwrrrrrrrrlwrwrr"},
        {"key": "loop-neurons-off", "name": "1,000 loop neurons off", "arm": "attr1000", "job": "sameraslan-1114-190619-6dcf",
         "right": 381, "loops": 19, "tokens": 3870.154, "points": 0.6, "ci95": [-3.4, 4.6], "loops_now_right": 33,
         "grid": "rrrrwrrrrwrwrrrrrwwrrwwrrrwrrrrrrrrrrwrwbrrwrrrrrrwrrrrrrrrrwrrrrrrrrrrrrrrrrrrrrrlrrrrrrrrrrrwrwrrr"
                 "wrrwwrrrrwwrlrrrrrwrlrrrrrwrrwwrrrrrrrwrrrrrrwrrrrrrwrwrrrrrrrrrwrrrlrlrrrrrlrwrwrrrrrrrrwrrrwrrrrrr"
                 "rrrrwrrrrlrrrrwrrrrlrrrlwwrrwrrrwrrrwrrwwrwrrrwwwrrrrrrwrrrrrrrrwrrrrwrrrrrrrrrwrrrrwwwrwrrwrwrwwrrr"
                 "rrwrrrwrwrrrrrrrrwrrrrrwwrrlrrrrwrrrrrrrwrrrrrrrrwrrwrrrrrwrrrrrrwrrwwrrwrrrrrrwrrwrrrrrrrrrwrwrrrwr"
                 "wwrwrrrrrrrrlrrrlrrwrrwrrlrrwrrrwrrwrwwwrrrrwrrrrrrrrrwrwrrrwrrrrrwrrlwrwlrwrrlrrlrrrwrrrrlwrrwrrwrr"},
        {"key": "random-neurons-off", "name": "1,000 random neurons off", "arm": "rnd1000", "job": "sameraslan-1114-190626-cf9f",
         "right": 370, "loops": 74, "tokens": 4873.628, "points": -1.6, "ci95": [-5.4, 2.2], "loops_now_right": 25,
         "grid": "rrrrrrrrrlrlwrrlrlwrrrrrrrrrrrrrwrrrrrrrrwrlrrrrrrwrrrrrrrrrrrrrrrrrlrrlrrwrlrrrlrrrrrrrlrrrrrwrwrrr"
                 "llrlwrrrlrwrrrrrrrrwlrlrrrlrlllrrwrrrwwlrrrrwlrwrrrrrllrrrrrrrrrlllrlrrrrrrrllrrrrrrrrrrrwrrrrrrrrrr"
                 "rrrrwrrrrwlrrrlrrlrlrrlwrwrrrrrrwrrrlrrwlrlrrrrrrrrlrrwrrrrrrrrrwrrrrrrrwrwrrrrlrwrrrrllrrrrrrrlrrrr"
                 "rwlrrrlrwrrrrrrrrlrrwlrllrrrrrrrllrrrrrrwrrrrrrrrlrlwrrrrrwrrrrrrwrrrlrrwrrrrlrwwlrrrlrrrwrrlwlrlrrr"
                 "wwrlrrwrlrrwlrrrrrrwrlwrrrrrrrrrwlrrlrrlrrrrwrrrrrrrrrrrrrrrwrlrrrrrrrrrwrrlrwlrlwrrrwrrrrrlrlwwrlrw"},
    ],
    # The run that chose the 1,000 neurons: loops used to rank them, and what switching them off costs on normal answers.
    "ranking": {"artifact": "studies/cleanneurons/results/loops/real-01/metrics.json", "loops": 14,  # len(loops.half_A)
                "normal_answers": 40, "loss_change_relative": 0.08241379520570873},  # config.normal, conditions.attr1000.normal
    # The same neurons with their activity multiplied, against 1,000 random neurons: [factor, continuations that loop].
    "dose": {"artifact": "studies/cleanneurons/results/describe/attr1000_loops-01/dose_summary.json", "n": 14,
             "selected": [[0, 1], [0.5, 1], [1, 3], [2, 8]], "random": [[0, 3], [2, 3]],
             "same_noise": {"rows_identical": 5, "n": 14, "pass": False}},  # controls.same_noise
    # A second ranking, made on 34 loops and tested on 34 others: continuations that loop again (conditions.<name>.heldout).
    "second": {"artifact": "studies/cleanneurons/results/loops/real-02/metrics.json", "ranked_on": 34, "n": 34,
               "none": 19, "attr100": 1, "rnd100_s0": 19},
    # The 1,000 neurons of that second ranking, switched off in the whole model (studies/cleanneurons/README.md, "Part G
    # with the run-2 sets"). At T 0.6 on two seeds, paired with the unedited model of the same seed: baseline and
    # arms.attr1000_real02 of each readout (right_v3, loops_rule_A, tokens_per_problem, points_vs_baseline, ci95).
    "r2": {"edit": "studies/cleanneurons/results/loops/real-02/edit_attr1000.json",
           "seeds": [{"artifact": GEN + "readout_t06_real02.json", "seed": 1000000,
                      "base": [378, 71, 4689.678], "edit": [414, 4, 3464.378], "points": 7.2, "ci95": [3.2, 11.2]},
                     {"artifact": GEN + "readout_t06_seed2.json", "seed": 2000000,
                      "base": [394, 61, 4356.786], "edit": [399, 9, 3523.178], "points": 1.0, "ci95": [-2.8, 4.6]}],
           # T 1.0 on MATH-500: counts.correct_v3 of each run folder; the unedited cell is the team's T1
           # (studies/rlneurons/README.md, cells.base_opener_1.0.right_v3 of this readout).
           "t10": {"unedited": 410, "unedited_artifact": "studies/rlneurons/results/rln4/grader_v3/readout.json", "n": 500,
                   "off": {100: ["attr100r2_t10-01", 390], 1000: ["attr1000r2_t10-01", 372]}},
           # T 1.0 on the harder 328: [counts.correct_v3, counts.cap_hits]; the unedited cell is the team's ("Harder 328").
           "hard": {"unedited": [164, 77], "unedited_artifact": "studies/rlneurons/results/day1/hard328_base_cue_t10-01/metrics.json",
                    "n": 328, "off": {100: ["hard328_attr100r2_t10-01", 155, 47], 1000: ["hard328_attr1000r2_t10-01", 130, 32]}},
           # Four samples per problem at T 0.6, edited against unedited ("Part G over four samples"): the means of
           # singles_right, rounded, and pooled_points_edited_minus_unedited."4 samples".points.
           "vote": {"artifact": GEN + "readout_vote_t06.json", "unedited": 383, "edited": 403, "points": 4.05, "rounded": 4},
           # The unedited model at T 1.0, four single samples: rows.single.right (405) and the stored T1 cell (410).
           "t10_single": {"artifact": "studies/rlneurons/results/day1_3/math500_base_cue-01/readout.json", "right": 405}},
}

_U, _L, _R = DATA["states"]
_dose, _second, _rank = DATA["dose"], DATA["second"], DATA["ranking"]
_tok = lambda s: f"{round(s['tokens']):,}"  # tokens per problem, as shown in the picture
_saved = round(100 * (1 - _L["tokens"] / _U["tokens"]))  # per cent of the generated tokens that the edit saves
_seq = lambda v: ", ".join(str(x) for x in v[:-1]) + f" and {v[-1]}"
_r2 = DATA["r2"]
_s1, _s2 = _r2["seeds"]
_cut = lambda s: round(100 * (1 - s["edit"][2] / s["base"][2]))  # per cent of the tokens the second set saves on one seed
_t10, _hard = _r2["t10"], _r2["hard"]
_vote, _t10s = _r2["vote"], _r2["t10_single"]

TITLE = "Loop neurons"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Why does a language model get stuck repeating the same text?"
LINE = f"Switching off {DATA['off']:,} of a model's {DATA['neurons']:,} neurons cuts its repetition loops from {_U['loops']} to {_L['loops']}."

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
# Not from our runs: the two papers. Hiraoka and Inui, "Repetition Neurons: How Do Language Models Produce Repetitions?"
# (arXiv 2410.13497, Sec. 4.1: repeating samples fall by up to 25 % against random neurons; models of 2B to 3B
# parameters; no task score). Chen and Wang, arXiv 2610.24715, Table 16: MATH-500 with the count penalty against the
# default sampler, Qwen3-4B 83.2 against 83.0 and Llama-3.1-8B 49.2 against 50.2. Rule A is studies/rlneurons/README.md.
PANELS = [
    ["new", "What is new",
     "Neurons that drive repetition were already reported in smaller models (Hiraoka and Inui, arXiv 2410.13497). New here is their effect on a math benchmark.",
     ["Switching them off removes most loops and about a fifth of the tokens.",
      f"Right answers rise by about {_vote['rounded']} points at the setting where the model loops.",
      f"In a small test, doubling their activity raised loops from {_dose['selected'][2][1]} to {_dose['selected'][3][1]} of {_dose['n']} runs, "
      f"and switching them off lowered it to {_dose['selected'][0][1]}."]],
    ["why", "Why it matters",
     "It removes loops with no training of any kind.",
     [f"With a second set of {DATA['off']:,} neurons, loops fall from {_s1['base'][1]} to {_s1['edit'][1]} on one random seed and from "
      f"{_s2['base'][1]} to {_s2['edit'][1]} on another.",
      f"Tokens per problem fall by {_cut(_s1)} % and {_cut(_s2)} %.",
      "Loops do not explain why this model trails its reward-trained version."]],
    ["how", "How we know",
     f"We set the output weights of {DATA['off']:,} neurons to zero and let the model answer all {DATA['n']} problems again with the same random seeds.",
     ["The neurons are the ones that most raise the probability of looping text.",
      f"Control: with {DATA['off']:,} random neurons off, {_R['loops']} answers loop and {_R['right']} are right.",
      f"On {_second['n']} loops kept out of the choice, 100 neurons are enough: {_second['attr100']} loops again, against {_second['none']} unedited."]],
    ["limits", "What it does not show",
     "The edit does not make the model better than its own best setting.",
     [f"With the second set, over four runs per problem, right answers rise from {_vote['unedited']} to {_vote['edited']} of {DATA['n']} where the "
      f"model loops, which only matches the unedited model at the sampling temperature where it does not loop ({_t10s['right']} to {_t10['unedited']}).",
      f"At the sampling temperature where the model does not loop, the edit costs right answers: {_t10['off'][100][1]} and "
      f"{_t10['off'][1000][1]} of {_t10['n']} against {_t10['unedited']}.",
      f"On {_hard['n']} harder problems it turns answers cut off at the length limit into finished wrong answers: {_hard['off'][100][1]} and "
      f"{_hard['off'][1000][1]} right against {_hard['unedited'][0]}."]],
    ["run", "How to reproduce it",
     "The command, the jobs and every number are listed in studies/cleanneurons/README.md, sections Part L and Part G.",
     [f"The edited model ran as job {_L['job']} at commit {DATA['run_commit'][:7]}, the unedited one as job {_U['job']}, the random control as job {_R['job']}.",
      "The picture's numbers are in " + DATA["artifact"] + "."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab seen from slightly above with one dot per problem; seven are loops, in the page's red, and
# five of them slowly fade to plain dots and return (71 of 500 and 19 of 500, on 54 dots). At t = 0 all seven show.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, cols = 9, rows = 6, loops = [5, 12, 20, 31, 34, 43, 50], stay = [12, 43];
  const gone = .5 - .5 * Math.cos((Number(t) || 0) * .45), n = v => v.toFixed(2);
  let out = kit.slab(a, b, th), top = "";
  for (let i = 0; i < cols * rows; i++) {
    const p = kit.at(a * .78 * (2 * (i % cols) / (cols - 1) - 1), b * .74 * (2 * Math.floor(i / cols) / (rows - 1) - 1), th / 2);
    const red = !loops.includes(i) ? 0 : stay.includes(i) ? 1 : 1 - gone;
    const dot = (r, color, alpha) => `<ellipse cx="${n(p[0])}" cy="${n(p[1])}" rx="${n(r * p[2])}" ry="${n(r * p[2] * .66)}" fill="${color}" opacity="${n(alpha)}"/>`;
    if (red < 1) out += dot(1.35, kit.token.ink, .7 * (1 - red));
    if (red > 0) top += dot(2.5, "var(--red)", red);
  }
  return out + top;
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
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table
   with a cast shadow in place of the glow. The light comes from the upper left in both. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
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

/* The picture: one plate with a dot per problem, and the one switch that changes it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg { width: 100%; max-height: calc(100vh - 200px); display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.dot { fill: none; stroke-linecap: round; }
.dot.c0 { stroke: var(--ink); opacity: .82; }
.dot.c1 { stroke: var(--faint); opacity: .42; }
.dot.c2 { stroke: var(--red); }
.dot.halo { stroke: var(--red); opacity: calc(var(--bloom) * .17); }
.k0 { fill: var(--ink); opacity: .82; } .k1 { fill: var(--faint); opacity: .42; } .k2 { fill: var(--red); }
.klab { fill: var(--mute); font-weight: 520; }
.big { fill: var(--red); font-weight: 660; letter-spacing: -.03em; font-stretch: 100%; }
.num { font-weight: 640; letter-spacing: -.01em; }
.lab { fill: var(--mute); font-weight: 520; }
.switch { display: inline-flex; align-self: center; margin-top: 20px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }

/* One drawn entrance, then only the slow sway and what the reader switches */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .dots, .enter .read, .enter .key { animation: fade .7s .7s both; }

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
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
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
  .stage { order: 3; margin-top: 22px; padding: 0; display: block; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
  .switch { display: flex; flex-direction: column; margin-top: 16px; border-radius: 22px; }
  .switch button { text-align: center; padding: 10px 6px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a { transition: none; }
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
    <div class="switch" id="switch" role="group" aria-label="Version of the model"></div>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
/* A dot is one problem, in the order of the benchmark, and has one of three looks: 0 right, 1 wrong, 2 stuck in a
   loop. One answer of the edited model is right and still ends in a loop (b); it is drawn as a loop. */
const N = D.n, COLS = 25, LOOK = { r: 0, w: 1, l: 2, b: 2 };
const ST = D.states.map(s => ({ ...s, look: [...s.grid].map(ch => LOOK[ch]) }));
const KEY = ["Right", "Wrong", "Loop"];
const S = { state: 0, from: null, e: 1, t0: 0, t: 0, last: 0, open: null, g: null, el: {}, shown: {} };

/* Geometry: the plate faces the viewer, in a small 3D space around its centre (x right, y down, z toward the
   viewer). a is the plate; the grid starts at gx, gy with one dot every pitch; d is the width of a dot per look and
   of the light around a loop; z is how far each look stands in front of the plate, a loop nearest. bx and lx are the
   left edges of the large number and its name, by their baselines; rx and ry are those of the two smaller numbers and
   their names; fb, fn and fs are the sizes of the type. */
function geo() {
  return narrow.matches
    ? { w: 480, h: 640, cx: 240, cy: 320, D: 1900, a: [6, 8, 474, 632], r: 22, deep: 30, gx: 33.6, gy: 214, pitch: 17.2, d: [7, 3.6, 10.5, 20], z: [6, 4, 22],
        bx: 32, lx: 36, by: [120, 150], fb: 104, rx: 290, ry: [78, 100, 138, 160], fn: 32, fs: 17, kx: [36, 150, 270], ky: 592, kr: [4.2, 2.4, 6], blur: 12 }
    : { w: 1000, h: 596, cx: 500, cy: 298, D: 2100, a: [30, 22, 970, 574], r: 30, deep: 40, gx: 78, gy: 68, pitch: 21.5, d: [8.5, 4.2, 12.5, 24], z: [6, 4, 24],
        bx: 664, lx: 668, by: [216, 254], fb: 150, rx: 668, ry: [350, 377, 444, 471], fn: 40, fs: 21, kx: [82, 196, 316], ky: 530, kr: [4.6, 2.6, 6.6], blur: 16 };
}
/* The view, as in architecture.py: a slow sway, plus a few degrees toward the pointer. */
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z) {  // to the screen: [x, y]
  const X = x - g.cx, Y = y - g.cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, g.cy + y1 * k];
}
function slab(g, z) {  // the outline of the plate at depth z
  const [x0, y0, x1, y1] = g.a, r = g.r, p = [];
  const corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}

/* The picture, built once per layout; place() then sets everything that depends on the view and on the version.
   Back to front: the light and the shadow, the plate, the dots (wrong, right, loops with their light), the key under
   them, the three numbers. Each look is three paths: the dots that keep it through a switch (s), those that lose it
   (o) and those that gain it (i), so a dot that changes fades in place and the others stay as they are. */
function build() {
  const g = S.g = geo(), svg = $("svg"), [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const dots = (k, cls, w) => ["s", "o", "i"].map(m => `<path class="dot ${cls}" id="${cls === "halo" ? "h" : "d"}-${m}${k}" stroke-width="${w}"/>`).join("");
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${g.cy}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .05)}" width="${aw}" height="${ah}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .32)}" cy="${f(ay0 + ah * .28)}" rx="${f(aw * .3)}" ry="${f(ah * .22)}" transform="rotate(-16 ${f(ax0 + aw * .32)} ${f(ay0 + ah * .28)})" fill="url(#spec)"/>` +
    `<g class="dots">${dots(1, "c1", g.d[1])}${dots(0, "c0", g.d[0])}${dots(2, "halo", g.d[3])}${dots(2, "c2", g.d[2])}</g>` +
    `<g class="key">${KEY.map((name, k) => `<circle class="k${k}" id="kd${k}" r="${g.kr[k]}"/><text class="klab" id="kt${k}" font-size="${g.fs}">${name}</text>`).join("")}</g>` +
    `<g class="read"><text class="big" id="big" font-size="${g.fb}"></text><text class="lab" id="biglab" font-size="${g.fs}">loops in ${N} math problems</text>` +
    `<text class="num" id="n-right" font-size="${g.fn}"></text><text class="lab" id="l-right" font-size="${g.fs}">right</text>` +
    `<text class="num" id="n-tok" font-size="${g.fn}"></text><text class="lab" id="l-tok" font-size="${g.fs}">tokens per problem</text></g>`;
  S.el = {};
  S.shown = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
}
function place(t) {
  const g = S.g, E = S.el, to = ST[S.state], fr = S.from == null ? to : ST[S.from], e = S.from == null ? 1 : S.e;
  const at = (el, q, dy) => { el.setAttribute("x", f(q[0])); el.setAttribute("y", f(q[1] + (dy || 0))); };
  const text = (id, v) => { if (S.shown[id] !== v) E[id].textContent = S.shown[id] = v; };
  E.back.setAttribute("d", slab(g, -g.deep));
  E.plate.setAttribute("d", slab(g, 0));

  // The dots: every problem keeps its place; one that changes its look moves between the depths of the two looks.
  const same = ["", "", ""], out = ["", "", ""], inn = ["", "", ""];
  for (let i = 0; i < N; i++) {
    const a = fr.look[i], b = to.look[i], col = i % COLS;
    const q = proj(g, g.gx + col * g.pitch, g.gy + (i - col) / COLS * g.pitch, a === b ? g.z[a] : mix(g.z[a], g.z[b], e));
    const s = "M" + f(q[0]) + " " + f(q[1]) + "h0";
    if (a === b) same[a] += s; else { out[a] += s; inn[b] += s; }
  }
  for (let k = 0; k < 3; k++) {
    E["d-s" + k].setAttribute("d", same[k]);
    E["d-o" + k].setAttribute("d", out[k]); E["d-o" + k].setAttribute("stroke-opacity", (1 - e).toFixed(3));
    E["d-i" + k].setAttribute("d", inn[k]); E["d-i" + k].setAttribute("stroke-opacity", e.toFixed(3));
  }
  E["h-s2"].setAttribute("d", same[2]);  // the light around a loop breathes slowly
  E["h-s2"].setAttribute("stroke-width", f(g.d[3] * (1 + .1 * Math.sin(t * .6))));
  E["h-o2"].setAttribute("d", out[2]); E["h-o2"].setAttribute("stroke-opacity", (1 - e).toFixed(3));
  E["h-i2"].setAttribute("d", inn[2]); E["h-i2"].setAttribute("stroke-opacity", e.toFixed(3));

  // The key, and the three numbers: they count from one version to the next while the dots change.
  KEY.forEach((_, k) => {
    const q = proj(g, g.kx[k], g.ky, 4);
    E["kd" + k].setAttribute("cx", f(q[0])); E["kd" + k].setAttribute("cy", f(q[1]));
    at(E["kt" + k], [q[0] + g.fs * .7, q[1]], g.fs * .35);
  });
  const now = k => Math.round(mix(fr[k], to[k], e));
  text("big", String(now("loops")));
  text("n-right", String(now("right")));
  text("n-tok", now("tokens").toLocaleString("en-US"));
  at(E.big, proj(g, g.bx, g.by[0], 10)); at(E.biglab, proj(g, g.lx, g.by[1], 10));
  ["n-right", "l-right", "n-tok", "l-tok"].forEach((id, i) => at(E[id], proj(g, g.rx, g.ry[i], 10)));
}

/* Motion that is always on: the plate sways by a few degrees and leans toward the mouse, and the light around the
   loops breathes. A switch takes 0.9 s. About 30 frames a second are enough for this, and keep a frame cheap. With
   reduced motion the page shows one still frame and a switch changes it at once. */
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 30) return;
  S.last = now;
  const t = S.t = now / 1000;
  V.px += (V.tx - V.px) * .1;
  V.py += (V.ty - V.py) * .1;
  aim(5 * Math.sin(t * .13) + 4 * V.px, 2 * Math.sin(t * .09) - 2 * V.py);
  if (S.from != null) {
    const p = Math.min(1, (now - S.t0) / 900);
    S.e = ease(p);
    if (p >= 1) S.from = null;
  }
  place(t);
}

/* The version and the open panel are one value in the address: #<version>, #<panel> or #<version>/<panel>. */
function choose(i, instant) {
  const st = ST[i];
  if (instant || still.matches || i === S.state) S.from = null;
  else { S.from = S.state; S.t0 = performance.now(); S.e = 0; }
  S.state = i;
  $("svg").setAttribute("aria-label", `${N} math problems, one dot each. ${st.name}: ${st.loops} loops, ${st.right} right, ` +
    `${Math.round(st.tokens).toLocaleString("en-US")} tokens per problem.`);
  $("switch").querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-pressed", k === i));
  if (still.matches) { aim(0, 0); place(0); }
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
function address(push) {
  const parts = [S.state ? ST[S.state].key : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const i = Math.max(0, ST.findIndex(s => parts.includes(s.key))), p = C.panels.find(p => parts.includes(p[0]));
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
    choose((S.state + (e.key === "ArrowRight" ? 1 : ST.length - 1)) % ST.length);
    address(false);
    if (inside) $("switch").children[S.state].focus();
  }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); place(S.t); });
still.addEventListener("change", () => { if (still.matches) { S.from = null; aim(0, 0); place(0); } });
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
$("switch").innerHTML = ST.map((s, i) => `<button data-state="${i}" aria-pressed="false">${esc(s.name)}</button>`).join("");
build();
aim(0, 0);  // the still frame
fromHash(true);
place(0);
if (!still.matches) {
  $("svg").classList.add("enter");
  setTimeout(() => $("svg").classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS,
    "data": {"n": DATA["n"], "states": [{k: s[k] for k in ("key", "name", "right", "loops", "tokens", "grid")} for s in DATA["states"]]}}))

if __name__ == "__main__":  # DATA against its artifacts; run from the repository root
    load = lambda path: json.load(open(path))
    readout, grid = load(DATA["artifact"]), load(DATA["grid"])
    for s in DATA["states"]:
        cell = readout["baseline"] if s["arm"] == "baseline" else readout["arms"][s["arm"]]
        assert (s["right"], s["loops"], s["tokens"]) == (cell["right_v3"], cell["loops_rule_A"], cell["tokens_per_problem"]), s["arm"]
        assert cell["dir"].endswith(s["job"]) and grid["arms"][s["arm"]]["job"] == s["job"], s["arm"]
        assert s["grid"] == grid["arms"][s["arm"]]["grid"] and len(s["grid"]) == DATA["n"] == cell["n"], s["arm"]
        assert s["grid"].count("r") + s["grid"].count("b") == s["right"] and s["grid"].count("l") + s["grid"].count("b") == s["loops"], s["arm"]
        if s["arm"] != "baseline":
            assert (s["points"], s["ci95"], s["loops_now_right"]) == (cell["points_vs_baseline"], cell["ci95"], cell["of_baseline_loops"]["now_right"]), s["arm"]
    assert _U["loops"] == readout["baseline_loops"]
    run, build = load(GEN + "attr1000_t06-01/run.json"), load(GEN + "attr1000_t06-01/build.json")
    assert (DATA["run_commit"], _L["job"]) == (run["commit"], run["job_id"]) and (DATA["edit"], DATA["off"]) == (build["edit"], build["neurons_zeroed"])
    rank = load(_rank["artifact"])
    assert (DATA["model"], DATA["neurons"]) == (rank["model"]["repo"], rank["model"]["layers"] * rank["model"]["neurons"])
    assert (_rank["loops"], _rank["normal_answers"]) == (len(rank["loops"]["half_A"]), rank["config"]["normal"])
    assert _rank["loss_change_relative"] == rank["conditions"]["attr1000"]["normal"]["loss_change_relative"]
    dose = {(r["set"], r["factor"]): r for r in load(_dose["artifact"])["summary"] if not r["name"].endswith("_repeat")}
    assert all(r["n"] == _dose["n"] for r in dose.values())
    assert _dose["selected"] == [[k[1], r["loops"]] for k, r in sorted(dose.items()) if k[0] == "selected"]
    assert _dose["random"] == [[k[1], r["loops"]] for k, r in sorted(dose.items()) if k[0] == "reference"]
    assert _dose["same_noise"] == {k: load(_dose["artifact"])["controls"]["same_noise"][k] for k in ("rows_identical", "n", "pass")}
    second = load(_second["artifact"])
    assert (_second["ranked_on"], _second["n"]) == (len(second["loops"]["half_A"]), len(second["loops"]["half_B"]))
    for name in ("none", "attr100", "rnd100_s0"):
        assert (_second[name], _second["n"]) == (second["conditions"][name]["heldout"]["looped"], second["conditions"][name]["heldout"]["n"]), name
    for s in _r2["seeds"]:  # the second set at T 0.6, paired with the unedited model of the same seed
        r = load(s["artifact"])
        cells = {"base": r["baseline"], "edit": r["arms"]["attr1000_real02"]}
        for k, c in cells.items():
            assert s[k] == [c["right_v3"], c["loops_rule_A"], c["tokens_per_problem"]] and c["n"] == DATA["n"], (s["artifact"], k)
        assert (s["points"], s["ci95"]) == (cells["edit"]["points_vs_baseline"], cells["edit"]["ci95"]), s["artifact"]
        assert r["baseline_loops"] == s["base"][1]
        d = cells["edit"]["dir"].rsplit("-", 1)[1]
        folder = next(f for f in ("attr1000r2_t06-01", "attr1000r2_t06s2-01") if load(GEN + f + "/run.json")["job_id"].endswith(d))
        cfg, build = load(GEN + folder + "/metrics.json")["config"], load(GEN + folder + "/build.json")
        assert (build["edit"], build["neurons_zeroed"], cfg["seed"], cfg["temperature"]) == (_r2["edit"], DATA["off"], s["seed"], 0.6), folder
    assert (_cut(_s1), _cut(_s2)) == (26, 19)
    assert _t10["unedited"] == load(_t10["unedited_artifact"])["cells"]["base_opener_1.0"]["right_v3"]
    hard_base = load(_hard["unedited_artifact"])["counts"]
    assert _hard["unedited"] == [hard_base["correct_v3"], hard_base["cap_hits"]] and hard_base["n"] == _hard["n"]
    for bench, want in ((_t10, lambda v, c: v[1] == c["correct_v3"]), (_hard, lambda v, c: v[1:] == [c["correct_v3"], c["cap_hits"]])):
        for k, v in bench["off"].items():
            m, build = load(GEN + v[0] + "/metrics.json"), load(GEN + v[0] + "/build.json")
            assert want(v, m["counts"]) and m["counts"]["n"] == bench["n"] and m["config"]["temperature"] == 1.0, v[0]
            assert (build["edit"], build["neurons_zeroed"]) == (_r2["edit"].replace("attr1000", f"attr{k}"), k), v[0]
    v = load(_vote["artifact"])
    assert v["runs"]["edited"]["edit_file"] == _r2["edit"] and v["setting"]["temperature"] == 0.6
    singles = v["singles_right"]
    assert all(len(singles[k]) == 4 for k in ("unedited", "edited"))
    assert (_vote["unedited"], _vote["edited"]) == (round(sum(singles["unedited"]) / 4), round(sum(singles["edited"]) / 4))
    assert _vote["points"] == v["pooled_points_edited_minus_unedited"]["4 samples"]["points"] and _vote["rounded"] == round(_vote["points"])
    t10s = load(_t10s["artifact"])
    assert t10s["rows"]["single"]["right"] == _t10s["right"] and t10s["rows"]["single"]["n"] == DATA["n"]
    assert (t10s["run"]["model"], t10s["run"]["prompt"], t10s["run"]["temperature"]) == ("base", "cue", 1.0)
    print("DATA matches", DATA["artifact"], DATA["grid"], _rank["artifact"], _dose["artifact"], _second["artifact"], "and the second-set runs")
