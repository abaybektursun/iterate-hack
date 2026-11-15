"""Eight directions per matrix of the RL weight change make the plain-prompt base score like the base with the opening cue
on MATH-500 (85.4 % against 82.0 %), and with the cue they solve 28 more of 328 harder problems than the cue alone.

The page of one finding, served at /finding/eight-directions (view.py serves every tools/finding_<slug>.py) and
reached from its tile on /findings, which ICON draws. The picture is one weight matrix as a glass slab seen from
slightly above, with eight lines across it for the eight directions, and two scales under it: MATH-500 and the 328
harder problems, each with Base + cue and RL as marked levels. The reader switches between five settings (address
/finding/eight-directions#<setting>, arrow keys) and watches the lines and both scores change. The rules are in
.claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py (.claude/skills/site-ui/SKILL.md).
"""
import json

TITLE = "Eight directions"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Reinforcement learning (RL) changed every weight a little. Which of the changes matter?"
LINE = ("Adding the 8 largest directions of RL's weight change in each weight matrix lifts the base model to the level of "
        "the opening cue on MATH-500 (85.4 % against 82.0 %); with the cue added to both, it solves 28 more of the 328 "
        "harder problems than the cue alone.")

# Every number is copied from the artifact named here. None is typed from memory.
RESULTS = "studies/rlneurons/results/wsp1/"
V3 = "studies/rlneurons/results/rln4/grader_v3/readout.json"
# The 328 harder problems, T 1.0 / top-p 1.0, grader v3, one sample: Base from day1_hard328/readout.json
# (cells.base_plain_T1), Base + cue and RL from day1/readout.json (rows.hard328_base_cue_t10-01, hard328_rl_plain_t10-01),
# the edits with the cue from xreward/edits/readout.json on branch sharedsub (cells.<name>.right_v3).
HARD_SRC = {"base": "studies/rlneurons/results/day1_hard328/readout.json", "cue": "studies/rlneurons/results/day1/readout.json",
            "edits": "studies/rlneurons/results/xreward/edits/readout.json", "branch": "sharedsub"}
DATA = {
    "artifact": RESULTS + "readout.json",  # cells of full500; Base, Base + cue and RL from results/rln4/grader_v3/readout.json
    "runs": RESULTS + "full500/",  # one folder per cell, <label>_<prompt>-01/metrics.json
    "commit": "1417dbf8f09bb4fcffd273eff18dabdeb76debff",  # full500/top8_plain-01/run.json
    "metric": "MATH-500, 500 problems, one sample each at temperature 1.0",
    "unit": "%",
    "measure": "of 500 math problems answered right",  # the small label beside the big number: what it counts
    "max": 100,
    "n_hard": 328,
    # What the reader switches between; "first" is the one shown on load, the finding itself. right = right of 500 on
    # MATH-500, hard = right of the 328 harder problems; cue says whether that setting used the opening cue there. short is
    # the name on the switch at phone width.
    "first": 3,
    "states": [
        {"key": "base", "name": "Base", "short": "Base", "right": 224, "cell": V3 + " cells.base_plain_1.0",
         "hard": 76, "hard_cue": False, "hard_cell": "day1_hard328 cells.base_plain_T1",
         "note": "The base model was pretrained on text and never trained with rewards. The lines are RL's 8 largest directions, not yet added."},
        {"key": "base-cue", "name": "Base + cue", "short": "+ cue", "right": 410, "cell": V3 + " cells.base_opener_1.0",
         "hard": 164, "hard_cue": True, "hard_cell": "day1 rows.hard328_base_cue_t10-01",
         "note": "Base + cue: the same weights; only the first three tokens of the answer are fixed to RL's opening, \"line!\", two line breaks, \"Okay\"."},
        {"key": "random", "name": "8 random directions", "short": "8 random", "right": 197, "cell": "full500/rand8_plain",
         "hard": 158, "hard_cue": True, "hard_cell": "xreward/edits cells.rand8_math31",
         "note": "A control: 8 random directions of the same size are added to each matrix. Plain prompt on MATH-500; the cue on the 328 harder problems."},
        {"key": "rl-directions", "name": "8 RL directions", "short": "8 RL", "right": 427, "cell": "full500/top8_plain",
         "hard": 192, "hard_cue": True, "hard_cell": "xreward/edits cells.top8_math31",
         "note": "Only the 8 largest directions of RL's change per matrix are added. Plain prompt on MATH-500; the cue on the 328 harder problems."},
        {"key": "rl", "name": "RL", "short": "RL", "right": 463, "cell": V3 + " cells.rl_1.0",
         "hard": 206, "hard_cue": False, "hard_cell": "day1 rows.hard328_rl_plain_t10-01",
         "note": "RL: the model after reinforcement learning on math, the whole change. Plain prompt."},
    ],
    # The edit of the cell top8_plain: k directions in n_edited matrices, their share of the squared norm of the RL
    # change, and the norm of the addition over the norm of the weights (edit.share and edit.add_rel).
    "edit": {"source": RESULTS + "full500/top8_plain-01/metrics.json", "k": 8, "n_edited": 224, "n": 500, "share": 0.0982, "add_rel": 0.000741},
    "removed": {"cell": "screen100/bulk_plain", "value": 91, "n": 100},  # RL without these directions, first 100 problems
    "one": {"cell": "screen100/top1_plain", "value": 42, "n": 100},  # one direction per matrix, first 100 problems
    # 8 RL directions (plain) minus Base + cue on MATH-500, paired by problem from full500/top8_plain-01/per_problem.json and
    # results/rln4/t1_t2_items-01/per_problem.json (t1_right): 5,000 resamples, seed 0, 95 % percentile, in points.
    "vs_cue": {"points": 3.4, "ci": [-0.4, 7.2], "only_top8": 58, "only_cue": 41},
    # The same with the cue on the 328 (xreward/edits paired_differences_points), and the cut-off answers there (cap_hits).
    "vs_cue_hard": {"points": 8.5, "ci": [4.3, 12.8]}, "random_vs_cue_hard": {"points": -1.8, "ci": [-5.8, 2.4]},
    "cap_hard": {"base_cue": 77, "top8": 46},
    # What three ends of two directions read as through the output layer: rows of anatomy-01/readout.json with this
    # name and delta. direction counts from 0; toks are the first tokens of the row, label is what the page shows.
    "words": {"source": RESULTS + "anatomy-01/readout.json", "name": "model.layers.29.mlp.down_proj.weight", "delta": "rl_math",
              "rows": [
                  {"direction": 1, "sign": "+", "toks": ["Okay", " consider", " considering"], "label": "Okay, consider"},
                  {"direction": 1, "sign": "-", "toks": [" perhaps", " maybe"], "label": "perhaps, maybe"},
                  {"direction": 2, "sign": "+", "toks": [" WAIT", "wait", ".Wait", "WAIT", " wait", " Wait"], "label": "Wait"},
              ]},
}
for _s in DATA["states"]:
    _s["value"] = round(100 * _s["right"] / 500, 1)
_S = {s["key"]: s for s in DATA["states"]}
DATA["cue"] = {"right": _S["base-cue"]["right"], "n": 500, "cell": _S["base-cue"]["cell"]}  # tools/findings.py reads it
DATA["levels"] = {"cue": _S["base-cue"], "rl": _S["rl"]}  # the two marked levels on each scale
_edit, _vc, _vh = DATA["edit"], DATA["vs_cue"], DATA["vs_cue_hard"]
_pc = lambda k: f"{_S[k]['value']} %"
_m = lambda v: str(v).replace("-", "−")  # a negative number with the minus sign U+2212
# Two results on the words the directions point at. Wait steering on branch claude/wait-steering-f535b2:
# arms["steer:hold:L24:0.068"].right_v3 and stored_unsteered.right_per_sample_mean. Checking passages judged blind:
# labels.real.passA.fix of items.base + items.rl.
WAIT = {"source": "studies/jspace/results/steer/main-01/metrics.json", "branch": "claude/wait-steering-f535b2",
        "steered": 413, "unsteered": 410.5, "n": 500}
CHECKS = {"source": "studies/rlneurons/results/checks/judge-01/readout.json", "fix": 5, "n": 80}
_gain = _S["rl-directions"]["hard"] - _S["base-cue"]["hard"]  # 28 of 328
_share = round(100 * _gain / (_S["rl"]["hard"] - _S["base-cue"]["hard"]))  # 28 of the 42 RL adds over Base + cue: 67

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new",
     "New here: how small a part of RL's weight change keeps the gain, a random control, and the comparison with the "
     "opening cue, which needs no weight change at all. It was known that a small part of the change keeps the gain "
     "(Spectral Rewiring, arXiv 2607.03065).",
     [f"On MATH-500, the 8 RL directions with the plain prompt score {_pc('rl-directions')}, Base + cue {_pc('base-cue')}: "
      f"{_vc['points']} percentage points apart, 95 % interval {_m(_vc['ci'][0])} to {_m(_vc['ci'][1])}, a difference within noise.",
      f"On the {DATA['n_hard']} harder problems, both with the cue, the 8 RL directions solve {_S['rl-directions']['hard']} of "
      f"{DATA['n_hard']} and Base + cue {_S['base-cue']['hard']}: {_gain} more, {_vh['points']} points, 95 % interval "
      f"{_vh['ci'][0]} to {_vh['ci'][1]}. That is {_share} % of the gain RL has over Base + cue there.",
      f"Eight random directions of the same size do not raise the score. On MATH-500 they lower it: {_pc('random')} "
      f"against the base model's {_pc('base')}. On the harder problems they solve {_S['random']['hard']} of "
      f"{DATA['n_hard']} against Base + cue's {_S['base-cue']['hard']} ({_m(DATA['random_vs_cue_hard']['points'])} "
      f"points, 95 % interval {_m(DATA['random_vs_cue_hard']['ci'][0])} to {_m(DATA['random_vs_cue_hard']['ci'][1])})."]],
    ["why", "Why it matters",
     "On MATH-500 the 8 directions score as high as the cue. On the harder problems they add to it, so they carry a part of "
     "RL's change that the cue does not.",
     ["In one matrix (the feed-forward output of layer 29), two of the directions, read through the model's output layer, "
      "point at words of deliberation: Okay, Wait, perhaps.",
      f"Those words alone do not raise the score: steering the activations of Base + cue so that it writes \"Wait\" as often as RL leaves it at "
      f"{WAIT['steered']} of {WAIT['n']}, against a mean of {WAIT['unsteered']} without steering. Blind judges call {CHECKS['fix']} of "
      f"{CHECKS['n']} checking passages a fix.",
      'A change this small and this readable is a target for editing weights directly. The page <a href="/finding/hand-written-edit">Hand-written edit</a> tries that with no reward and scores as high as the cue.']],
    ["how", "How we know",
     f"We added only the {_edit['k']} largest directions of the RL weight change in each of {_edit['n_edited']} weight matrices "
     f"to the base model and scored it on all {_edit['n']} MATH-500 problems and the {DATA['n_hard']} harder problems.",
     [f"Every score is one sample per problem at temperature 1.0, scored by the grader (version 3). Base {_pc('base')}, Base + cue {_pc('base-cue')}, "
      f"RL {_pc('rl')} on MATH-500.",
      f"The added change has {_edit['add_rel'] * 100:.2f} % of the norm of the weights and {_edit['share'] * 100:.1f} % of the "
      "squared norm of the full RL change.",
      "Closest published result: Spectral Rewiring (arXiv 2607.03065) keeps the RL gain with a small part of the update, "
      "on pairs of models that include this base model and its RL model."]],
    ["limits", "What it does not show",
     "The directions were read from the RL weights, so this is not yet a way to get the gain without reward.",
     [f"On MATH-500 the edit ran with the plain prompt and on the {DATA['n_hard']} harder problems with the cue; we did not "
      "run the edit with the cue on MATH-500 or without it on the 328.",
      f"Part of the gain of {_gain} problems comes from answers that end instead of being cut off at 16,384 tokens: "
      f"{DATA['cap_hard']['top8']} answers are cut off with the 8 directions and {DATA['cap_hard']['base_cue']} with Base + cue.",
      f"RL with these 8 directions removed keeps most of its score: {DATA['removed']['value']} of the first "
      f"{DATA['removed']['n']} MATH-500 problems. The gain is spread over many directions. One direction per matrix gives "
      f"{DATA['one']['value']} of {DATA['one']['n']}."]],
    ["run", "How to reproduce it",
     f"Two commands on one GPU reproduce the {_pc('rl-directions')}: the first writes the edited weights and the second scores them.",
     ["studies/rlneurons/jobs/wsp_edit.py --recipe top8 --dir /tmp/theta",
      "studies/rlneurons/jobs/run_cell.py --model-path /tmp/theta --model-label top8 --prompt plain --set math500 --temperature 1.0 "
      "--top-p 1.0 --seed 180000000 --commit $(git rev-parse HEAD)",
      "The run used commit " + DATA["commit"] + ". Its numbers are in " + RESULTS + ", Base, Base + cue and RL in " + V3
      + ". The harder problems: " + HARD_SRC["base"] + ", " + HARD_SRC["cue"] + " and " + HARD_SRC["edits"] + " on branch "
      + HARD_SRC["branch"] + ". The Wait steering is in " + WAIT["source"] + " on branch " + WAIT["branch"]
      + ", the judged checks in " + CHECKS["source"] + "."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab seen from slightly above with one fine line per direction, three of them bright.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, n = __K__, bright = [1, 4, 6];
  let out = kit.slab(a, b, th);
  for (let i = 0; i < n; i++) {
    const v = b * (1 - 2 * (i + 1) / (n + 1)), lit = bright.includes(i);
    out += kit.line(kit.at(-a * .8, v, th / 2), kit.at(a * .8, v, th / 2), lit ? 1.3 + .14 * Math.sin(t * .6 + i * 1.7) : .7, lit ? "lit" : "plain", lit ? 1 : .6);
  }
  return out;
}""".replace("__K__", str(DATA["edit"]["k"]))

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
svg { width: 100%; max-height: calc(100vh - 250px); display: block; overflow: visible; }
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
.ref { stroke-width: 2; stroke-linecap: round; }
.ref.cue { stroke: var(--ink); } .ref.rl { stroke: var(--blue); }
.gain { stroke: var(--blue); stroke-width: 7; stroke-linecap: round; filter: drop-shadow(0 0 6px color-mix(in oklab, var(--blue) calc(var(--glow) * 70%), transparent)); }
.tick { fill: var(--faint); font-weight: 500; }
.reftext { font-weight: 600; text-anchor: middle; }
.reftext.cue { fill: var(--ink); } .reftext.rl { fill: var(--blue); }
.value { font-weight: 330; letter-spacing: -.03em; font-stretch: 100%; }
.unit .u1 { fill: var(--ink); font-weight: 620; } .unit .u2 { fill: var(--mute); font-weight: 500; }
.cap1 { fill: var(--ink); font-weight: 560; }
.key { fill: var(--mute); font-weight: 500; text-anchor: middle; }
.leader { stroke: var(--faint); stroke-width: 1; }
.switch { display: inline-flex; align-self: center; margin-top: 18px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch .short { display: none; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.note { align-self: center; margin: 12px 0 0; color: var(--mute); font-size: 15px; text-align: center; max-width: 60ch; height: 3em; }

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
.say b, .say .nw { font-weight: 620; white-space: nowrap; }
.say .nw { font-weight: inherit; }
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
  .switch { align-self: stretch; }
  .switch button { flex: 1 1 auto; text-align: center; padding: 9px 4px; font-size: 14px; }
  .switch .long { display: none; }
  .switch .short { display: inline; }
  .note { height: 4.5em; }
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
const S = { state: 0, intro: false, t1: null, cap: "", open: null, g: null, el: null, out: null, words: [], cur: null, from: null, goal: null, t0: 0, t: 0, shown: "" };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1), h = n => n.toFixed(2), mix = (a, b, q) => a + (b - a) * q, pct = v => `${v.toFixed(1)} %`;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;

/* What each condition looks like, each value from 0 to 1: sc, the eight lines lie scattered; plain, they show unlit;
   lit, they show in the accent; rest, the other directions of the RL change show between them; wash, the whole slab
   is lit; lab, the words stand at the ends of their lines. The picture moves from one look to the next in 0.9 s. */
const LOOK = {
  "base": { sc: 0, plain: .34, lit: 0, rest: 0, wash: 0, lab: 0 },
  "base-cue": { sc: 0, plain: .34, lit: 0, rest: 0, wash: 0, lab: 0 },
  "random": { sc: 1, plain: .7, lit: 0, rest: 0, wash: 0, lab: 0 },
  "rl-directions": { sc: 0, plain: 0, lit: 1, rest: 0, wash: 0, lab: 1 },
  "rl": { sc: 0, plain: 0, lit: 1, rest: 1, wash: 1, lab: 1 },
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
    ? { w: 720, h: 850, cx: 360, cy: 216, a: 136, b: 172, th: 20, r: 20, D: 1900, yaw: -4, lw: 1.8, glow: 5.5, lead: 14, fs: 26, wide: 86, nudge: 7, x0: 40, x1: 680, kf: 26, ky: 36,
        num: 116, numY: 506, fl: 26, rows: [{ ay: 592 }, { cap: 690, ay: 780 }] }
    : { w: 1000, h: 750, cx: 500, cy: 238, a: 236, b: 236, th: 26, r: 28, D: 2100, yaw: -8, lw: 1.5, glow: 9, lead: 16, fs: 20, wide: 104, nudge: 0, x0: 130, x1: 870, kf: 18, ky: 40,
        num: 92, numY: 528, fl: 18, rows: [{ ay: 586 }, { cap: 654, ay: 716 }] };
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
/* The two scores under the slab, each on its own scale: MATH-500 (its value is the large number) and the 328 harder
   problems. On each, Base + cue is a marked level with its name above the line and RL one with its name below. */
const SX = (g, v, max) => g.x0 + (g.x1 - g.x0) * v / max;
function scale(g) {
  const L = D.levels, out = [], fl = g.fl;
  const mark = (x, y, up, text, cls) => `<line class="ref ${cls}" x1="${f(x)}" y1="${f(y - (up ? fl * .75 : fl * .3))}" x2="${f(x)}" y2="${f(y + (up ? fl * .3 : fl * .75))}"/>` +
    `<text class="reftext ${cls}" x="${f(x)}" y="${f(up ? y - fl * 1.05 : y + fl * 1.75)}" font-size="${fl}">${esc(text)}</text>`;
  [[D.max, v => pct(v), "value"], [D.n_hard, v => String(v), "hard"]].forEach(([max, txt, key], r) => {
    const y = g.rows[r].ay, at = v => SX(g, v, max);
    out.push(`<line class="axis" x1="${g.x0}" y1="${y}" x2="${g.x1}" y2="${y}"/>`,
      mark(at(L.cue[key]), y, true, `Base + cue ${txt(L.cue[key])}`, "cue"), mark(at(L.rl[key]), y, false, `RL ${txt(L.rl[key])}`, "rl"),
      `<line class="level" id="level${r}" x1="${g.x0}" y1="${y}" y2="${y}"/><line class="gain" id="gain${r}" y1="${y}" y2="${y}"/>` +
      `<circle class="head" id="head${r}" cy="${y}" r="${f(fl * .3)}"/>`);
  });
  return `<text class="value" id="value" x="${g.x0}" y="${g.numY}" font-size="${g.num}"></text>` +
    `<text class="unit" id="unit" y="${f(g.numY - g.num * .38)}" font-size="${g.fl}"><tspan class="u1">MATH-500</tspan>` +
    `<tspan class="u2" dy="${f(g.fl * 1.3)}">${esc(D.measure)}</tspan></text>` +
    `<text class="cap1" id="cap1" x="${g.x0}" y="${g.rows[1].cap}" font-size="${g.fl}"></text>` + out.join("");
}
function build() {
  const g = S.g = geo(), svg = $("svg");
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
    `<g id="key"><line class="leader" id="leader"/><text class="key" font-size="${g.kf}">` +
    `<tspan id="key1" x="${g.cx}" y="${g.ky}">One line is one direction:</tspan>` +
    `<tspan id="key2" x="${g.cx}" y="${f(g.ky + g.kf * 1.3)}">one rank-1 part of RL's change to this matrix</tspan></text></g>` +
    S.words.map(o => `<text class="word" id="word-${o.i}" font-size="${g.fs}" font-stretch="${g.wide}%" style="text-anchor:${o.side > 0 ? "start" : "end"}" opacity="0">${esc(o.text)}</text>`).join("") +
    `<g class="scale">${scale(g)}</g>`;
  S.el = {};
  ["glow", "side", "edge", "face", "wash", "shine", "rest", "plain", "halo", "lit", "rim", "fade-b", "fade-c", "fade-n", "value", "cap1", "key", "leader",
   "level0", "head0", "gain0", "level1", "head1", "gain1"].forEach(id => { S.el[id] = $(id); });
  S.words.forEach(o => { o.el = $("word-" + o.i); });
  S.out = outline(g);
  S.shown = ""; S.cap = "";
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

  // The label of one line: a leader from the label down to the middle of the farthest line, gone while the lines are random.
  const mid = at(0, row(K - 1), top);
  set(E.leader, { x1: f(g.cx), y1: f(g.ky + g.kf * 1.3 + 10), x2: f(mid[0]), y2: f(mid[1] - 4) });
  E.key.setAttribute("opacity", h(1 - c.sc));

  // The scores: the large number is MATH-500's; the 328 harder problems are counted on the second scale. Each head moves
  // along its scale. The words beside the second count belong to the setting the picture is moving to.
  const text = pct(c.v), hard = Math.round(c.hv), st = D.states[S.state];
  if (text !== S.shown) {
    E.value.textContent = S.shown = text;
    const u = $("unit"), x = g.x0 + E.value.getComputedTextLength() + g.fl;
    u.setAttribute("x", f(x)); u.querySelectorAll("tspan").forEach(t => t.setAttribute("x", f(x)));
  }
  const cap = `328 harder problems${st.hard_cue ? ", with the cue" : ""}: ${hard} of ${D.n_hard}`;
  if (cap !== S.cap) E.cap1.textContent = S.cap = cap;
  // The part of a score above Base + cue is drawn lit: what the setting adds beyond the cue.
  [[c.v, D.max, D.levels.cue.value], [c.hv, D.n_hard, D.levels.cue.hard]].forEach(([v, max, cue], r) => {
    const x = SX(g, v, max), xc = SX(g, cue, max);
    set(E["level" + r], { x2: f(x) }); set(E["head" + r], { cx: f(x) });
    set(E["gain" + r], { x1: f(xc), x2: f(Math.max(x, xc)), opacity: x > xc + .5 ? 1 : 0 });
  });
}

/* Motion that is always on: the view sways by a few degrees and leans toward the mouse, and the lit lines breathe
   each at its own rate. With reduced motion the page shows one still frame and a condition changes at once. */
function frame(now) {
  const t = S.t = now / 1000;
  V.px += (V.tx - V.px) * .06;
  V.py += (V.ty - V.py) * .06;
  aim(S.g.yaw + 6 * Math.sin(t * .13) + 5 * V.px, 2.5 * Math.sin(t * .09) - 2.5 * V.py);
  if (S.intro && now - (S.t1 ??= now) > 900) choose(D.first);  // timed from the first frame shown, not from page load
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
  const st = D.states[i], L = D.levels;
  S.state = i; S.intro = false;
  S.goal = { ...LOOK[st.key], v: st.value, hv: st.hard };
  if (instant || still.matches || !S.cur) { S.cur = { ...S.goal }; S.from = null; }
  else { S.from = { ...S.cur }; S.t0 = performance.now(); }
  $("svg").setAttribute("aria-label", `${D.metric}: ${st.name} ${pct(st.value)}; Base + cue ${pct(L.cue.value)}, RL ${pct(L.rl.value)}. ` +
    `328 harder problems: ${st.name} ${st.hard} of ${D.n_hard}; Base + cue ${L.cue.hard}, RL ${L.rl.hard}.`);
  $("note").textContent = st.note;
  $("switch").querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-pressed", k === i));
  place(S.t);
}
const link = s => s.replace(/&lt;a href=&quot;(\/[\w\/#-]*)&quot;&gt;(.*?)&lt;\/a&gt;/g, '<a href="$1">$2</a>');  // a link to another page of the site stays a link
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${link(esc(x))}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
function address(push) {
  const parts = [S.state !== D.first ? D.states[S.state].key : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const k = D.states.findIndex(s => parts.includes(s.key)), i = k < 0 ? D.first : k, p = C.panels.find(p => parts.includes(p[0]));
  if (first === true || i !== S.state) choose(i, first === true);
  /* On a first visit with no setting in the address the picture starts at Base and moves to the finding once it is
     shown, so the reader sees the change happen. */
  if (first === true && k < 0 && !still.matches) { choose(0, true); S.intro = true; }
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
document.fonts.ready.then(() => { S.shown = ""; place(S.t); });  // measure the score again in the loaded typeface
const stage = $("stage");  // the view leans a few degrees toward a mouse, and settles back
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1;
  V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>").replace(/MATH-500/g, '<span class="nw">MATH-500</span>');  // a number inside a name (MATH-500) stays plain
$("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}" aria-pressed="false" aria-label="${esc(s.name)}"><span class="long">${esc(s.name)}</span><span class="short">${esc(s.short)}</span></button>`).join("");
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
