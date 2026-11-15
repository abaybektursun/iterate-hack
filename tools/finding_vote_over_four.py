"""A vote over four samples adds 8.2 points to the cued base model on MATH-500, and RL under the same vote stays 5.6 ahead.

The page of one finding, served at /finding/vote-over-four (copied from .claude/skills/finding-page/template.py; draw()
shows each model's score as a glass bar that becomes a stack of four sheets, one per sample, when the vote is switched
on). It is reached from its tile on /findings, which ICON draws. Study: studies/rlneurons (README.md "Day-1 #3" and
"Label-free selector"; board result-5d032f, result-cbe0bc and result-60d899).
"""
import json

# Every number is copied from the artifacts named here. None is typed from memory.
DATA = {
    "artifact": "studies/rlneurons/results/day1_3/math500_base_cue-01/readout.json",
    "artifact_rl": "studies/rlneurons/results/day1_3/math500_rl-01/readout.json",
    "commit": "c36f562",  # run.json of both jobs
    "vote_after_restart": 450,  # rows.vote_after_restart.right of the base model
    "n": 500, "samples": 4,
    # rows.single and rows.vote (right, tokens_per_problem), differences_points["vote - single"], each_sample.single_right
    "rows": [
        {"key": "base", "name": "Base + cue, T 1.0", "single": 405, "vote": 446, "gain": 8.2, "gain_ci": [5.8, 10.8],
         "tokens_single": 3808.138, "tokens_vote": 16033.55, "each": [405, 409, 410, 418]},
        {"key": "rl", "name": "RL, T 1.0", "single": 456, "vote": 474, "gain": 3.6, "gain_ci": [2.0, 5.2],
         "tokens_single": 4675.104, "tokens_vote": 18747.16},
    ],
    # math500_rl-01/readout.json, minus.differences_points: RL minus the base model, in points, under the same procedure
    "gap": {"single": 10.2, "single_ci": [7.2, 13.2], "vote": 5.6, "vote_ci": [3.6, 7.8]},
    # The base model's vote minus one RL sample: README.md "Day-1 #3", recomputed from the two per_problem vectors
    # (paired bootstrap, 5,000 resamples, seed 0) when this page was written.
    "vote_minus_rl_single": -2.0, "vote_minus_rl_single_ci": [-4.0, 0.2],
    "ties": 36, "pass_at_4": 467,  # vote_stats.ties_for_first, rows.pass_at_k.right
    "wrong_to_right": 43, "right_to_wrong": 2,  # counted from per_problem.single and per_problem.vote of the base model
    "rl_vote_other_job": 469,  # README.md "Day-1 #3", instrument check
    # Board result-60d899: read from the rendered Figure 21 of arXiv 2610.06851, to about 1 point; the vote scored by a
    # literal reading of that paper's answer rule. Board knowledge-8a31ad: the paper's RL model and its score (Table 6).
    "published_vote": 88.5, "vote_paper_rule": 435, "published_rl": 75.0,
    # 24 rules fixed before scoring, each against one RL sample (24 draw orders; the table "Base rule against one RL
    # sample"): the best base rule vote4_restart_short, and the smallest RL lead (also vote4_restart_short).
    "frontier": "studies/rlneurons/results/frontier/math500-01/frontier.md",
    "frontier_rules": 24, "best_rule_minus_rl": [-1.2, -3.0, 0.6], "best_rule_times": 4.2, "min_rl_lead": [4.2, 2.4, 6.0],
    # 328 harder problems, four samples of both models (board result-5c961a; jobs at commit 2c58f34): base readout
    # rows.single/vote/vote_after_restart; RL readout rows.single and minus.differences_points.vote_after_restart;
    # selector readout rows.tie_short (right, minus_vote_points, minus_vote_interval95), selector commit 1aae930.
    "hard_base": "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/readout.json",
    "hard_rl": "studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/readout.json",
    "hard_selector": "studies/rlneurons/results/selector/hard328_base_cue-01/readout.json",
    "hard": {"n": 328, "single": 161, "vote": 192, "vote_restart": 195, "rl_single": 207,
             "rl_lead_restart": [8.8, 5.5, 12.5], "tie_short": 191, "tie_short_minus_vote": [-0.3, -2.1, 1.5]},
}
BASE, RL, GAP, N = DATA["rows"][0], DATA["rows"][1], DATA["gap"], DATA["n"]
pct = lambda right: f"{100 * right / N:.1f} %"
TIMES = round(BASE["tokens_vote"] / RL["tokens_single"], 1)  # the base model's vote against one RL sample, in tokens
DATA["times"] = TIMES

TITLE = "Vote over four samples"
PROBLEM = "Can voting replace RL training?"
LINE = (f"A vote over four samples adds {BASE['gain']} points to the base model, "
        f"and RL stays {GAP['vote']} ahead.")  # also the sentence on its tile

# What the reader switches between. The first is shown on load: start from the problem, not from the answer.
DATA["states"] = [
    {"name": "One sample", "note": f"A bar's length is its right answers of the {N} MATH-500 problems, "
                                   "with one sample per problem."},
    {"name": "Vote over four", "note": "The most common of four answers counts. For the base model that costs "
                                       f"{TIMES} times the tokens of one RL sample."},
]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new", "Voting over several samples is long known as self-consistency, and Wang et al. (arXiv 2610.06851, "
     f"Figure 21) already plot about {DATA['published_vote']} % for a vote over 4 samples of the same cued base model, "
     f"which our {pct(BASE['vote'])} equals.",
     ["The published value was read from the paper's figure to about 1 point (board result-60d899), and the paper gives the "
      f"gain no interval. This run adds one on the same {N} problems: {BASE['gain']} points, 95 % interval "
      f"{BASE['gain_ci'][0]} to {BASE['gain_ci'][1]}.",
      f"The paper's RL model is the earlier Olmo 3 release, which scores {DATA['published_rl']} % there and matches the cued "
      "base model at equal sample counts. This run puts the stronger Olmo 3.1 RL model under the same vote: it gains "
      f"{RL['gain']} points ({RL['single']} to {RL['vote']} of {N}).",
      f"Against that model the gap stays: {GAP['vote']} points under the vote (95 % interval {GAP['vote_ci'][0]} to "
      f"{GAP['vote_ci'][1]}), down from {GAP['single']} with one sample each."]],
    ["why", "Why it matters", "The direction asks for the cheapest route to the RL gain that uses no reward, compared at equal "
     "tokens and with RL given the same procedure, and by that standard the vote is a real step and an expensive one.",
     [f"With one sample each the base model is {GAP['single']} points behind. Its vote is {abs(DATA['vote_minus_rl_single'])} "
      f"points behind one RL sample, at {TIMES} times the tokens: {BASE['tokens_vote']:,.0f} per problem against "
      f"{RL['tokens_single']:,.0f}.",
      f"Given the same vote, RL gains {RL['gain']} points and stays {GAP['vote']} ahead, so sampling more does not remove "
      "what RL training changed.",
      f"A right answer is among the four samples on {DATA['pass_at_4']} problems, {DATA['pass_at_4'] - BASE['vote']} more "
      "than the vote picks. Sending a tie to the shortest finished sample was chosen after reading those misses and "
      f"failed on held-out problems: on the {DATA['hard']['n']} harder problems it gives {DATA['hard']['tie_short']} "
      f"against the plain vote's {DATA['hard']['vote']} ({DATA['hard']['tie_short_minus_vote'][0]} points, 95 % interval "
      f"{DATA['hard']['tie_short_minus_vote'][1]} to {DATA['hard']['tie_short_minus_vote'][2]}). The number to quote is "
      f"the plain vote's {BASE['vote']} of {N} ({DATA['vote_after_restart']} after restart)."]],
    ["how", "How we know", f"Each model answered the {N} MATH-500 problems {DATA['samples']} times at temperature 1.0 and "
     "top-p 1.0, and the vote takes the most common of the 4 extracted answers (grader v3).",
     ["The base model is Olmo-3-1025-7B with a three-token opening cue and no training, and the RL model is "
      "Olmo-3.1-7B-RL-Zero-Math. \"One sample\" is the first of the four. The base model's four samples score "
      f"{', '.join(map(str, BASE['each'][:3]))} and {BASE['each'][3]}, so the vote's {BASE['vote']} is above each of them.",
      f"Intervals are paired bootstraps over the {N} problems with 5,000 resamples. A sample without an extracted answer "
      f"casts no vote, and a tie goes to the lowest sample number; {DATA['ties']} of the base model's problems end in a tie.",
      "A second script recounted every row and found the same scores (board result-5d032f). The vote turns "
      f"{DATA['wrong_to_right']} of the base model's problems from wrong to right and {DATA['right_to_wrong']} from right to "
      f"wrong. The same seeds in another RL job gave {DATA['rl_vote_other_job']} for the vote where this one has "
      f"{RL['vote']}, so about 1 point of a vote score is variation between runs."]],
    ["limits", "What it does not show", "It does not show that voting replaces RL training: under the same vote the RL model "
     f"stays {GAP['vote']} points ahead.",
     [f"No vote rule closes the gap to one RL sample: of {DATA['frontier_rules']} base rules fixed before scoring, the best "
      f"is {abs(DATA['best_rule_minus_rl'][0])} points below it at {DATA['best_rule_times']} times the tokens, but its 95 % "
      f"interval, {DATA['best_rule_minus_rl'][1]} to +{DATA['best_rule_minus_rl'][2]}, includes 0. RL given the same rule "
      f"leads under every one of them by at least {DATA['min_rl_lead'][0]} points ({DATA['min_rl_lead'][1]} to "
      f"{DATA['min_rl_lead'][2]}).",
      f"On the {DATA['hard']['n']} harder problems, where nothing was chosen, the base model's vote has "
      f"{DATA['hard']['vote']} right ({DATA['hard']['vote_restart']} after restart) against {DATA['hard']['single']} for "
      f"one sample, still below one RL sample's {DATA['hard']['rl_single']}. Under the same vote after restart RL stays "
      f"{DATA['hard']['rl_lead_restart'][0]} points ahead (95 % interval {DATA['hard']['rl_lead_restart'][1]} to "
      f"{DATA['hard']['rl_lead_restart'][2]}).",
      f"The match with the published {DATA['published_vote']} % is under our grader. Under a literal reading of the paper's "
      f"answer rule our vote has {DATA['vote_paper_rule']} of {N}, or {pct(DATA['vote_paper_rule'])} (board result-60d899; "
      "that regrade script is not committed)."]],
    ["run", "How to reproduce it", "Two GPU jobs, one per model, sample every problem four times, and one script scores the "
     "stored answers on a laptop.",
     ["Each job runs studies/rlneurons/jobs/run_cell.py with --set math500 --temperature 1.0 --top-p 1.0 --samples 4 "
      "--restarts 2 at commit " + DATA["commit"] + ": --model base --prompt cue --seed 41000000, and --model rl --prompt "
      "plain --seed 45000000. Each took about 2 hours on one H100.",
      "The scores come from studies/rlneurons/analysis/day1_vote.py, run with --run on each job's folder and --out on a new "
      "run folder, and for the RL run with --minus on the base model's readout.json.",
      "The numbers are in " + DATA["artifact"] + " and " + DATA["artifact_rl"] + ", the 24 rules in " + DATA["frontier"]
      + ", the harder problems in " + DATA["hard_base"] + " and " + DATA["hard_rl"] + " (jobs at commit 2c58f34), and the "
      "tie rule on them in " + DATA["hard_selector"] + " (commit 1aae930)."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced to the base model's bar seen from above. Four lines are the four samples; each is plain up to the score of
# one sample and lit from there to the score of the vote.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, top = th / 2, x0 = -a * .8, at = right => x0 + a * 1.6 * right / __N__;
  return kit.slab(a, b, th) + [0, 1, 2, 3].map(i => {
    const v = b * (-.54 + .36 * i);
    return kit.line(kit.at(x0, v, top), kit.at(at(__SINGLE__), v, top), 2.6, "plain", .6) +
      kit.line(kit.at(at(__SINGLE__), v, top), kit.at(at(__VOTE__), v, top), 3 + .25 * Math.sin(t * .6 + i), "lit");
  }).join("");
}""".replace("__N__", str(N)).replace("__SINGLE__", str(BASE["single"])).replace("__VOTE__", str(BASE["vote"]))

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
   --wash is how strongly the part of a bar that the vote adds takes the accent. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --wash: .34;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --wash: .46;
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
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1.3; stroke-linejoin: round; }
.track { fill: none; stroke: var(--faint); stroke-width: 1; stroke-dasharray: 2 5; }
.wash { fill: var(--blue); opacity: var(--wash); pointer-events: none; }
.dim { fill: none; stroke: var(--ink); stroke-width: 1.3; stroke-linecap: round; }
.lane { font-weight: 540; }
.num { font-weight: 640; text-anchor: end; }
.gaptext { font-weight: 600; text-anchor: end; }
.plus { font-weight: 640; text-anchor: middle; fill: var(--blue); }
.tick { fill: var(--mute); font-weight: 520; text-anchor: middle; }
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
  .stage { order: 3; margin-top: 22px; padding: 0; }
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
    <svg id="svg" viewBox="0 0 760 392" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="How each model answers"></div>
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
const S = { state: 0, open: null, q: 0, from: 0, t0: 0, grow: 0 };
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q, ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
const clamp = p => Math.max(0, Math.min(1, p));

/* The picture: two glass bars on a glass board seen from slightly above, the base model in front and the RL model
   behind it. A bar's length is the model's right answers of 500; the dotted outline is all 500. With "One sample" a
   bar is one sheet. With "Vote over four" it is a stack of four sheets, one per sample, it is as long as the score of
   the vote, and the part the vote adds is lit. The line between the two ends is the lead of the RL model in points. */
const RAD = Math.PI / 180, CX = 380, CY = 160, EL = 56;
const U0 = -300, PER = 600 / D.n, HB = 36, TH = 9, GP = 5;  // the left end, units per problem, half depth, sheet, gap
const LANE = { base: -92, rl: 92 }, EDGE = { u: 334, front: -186, back: 148 }, VGAP = 12;
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
const seg = (a, b) => `M${f(a[0])} ${f(a[1])}L${f(b[0])} ${f(b[1])}`;
const rect = (u0, u1, v0, v1, w) => [proj(u0, v0, w), proj(u1, v0, w), proj(u1, v1, w), proj(u0, v1, w)];
const sheets = [...Array(D.samples).keys()], rows = [...D.rows].sort((a, b) => LANE[b.key] - LANE[a.key]);  // the far bar first
const set = (id, name, value) => $(id).setAttribute(name, value);
function label(id, c, size, dy, opacity) {  // a text that stays upright at a point of the scene, larger on a phone
  if (narrow.matches) size *= 1.3;
  set(id, "x", f(c[0])); set(id, "y", f(c[1] + dy * size * c[2])); set(id, "font-size", f(size * c[2])); set(id, "opacity", f(opacity));
}

function build() {
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const bar = o => `<g id="bar-${o.key}">` +
    sheets.map(i => `<path class="body" id="b-${o.key}${i}"/><path class="face" id="f-${o.key}${i}"/><path class="rim" id="r-${o.key}${i}"/>`).join("") +
    `<path class="wash" id="ws-${o.key}"/><path class="wash" id="wt-${o.key}"/>` +
    `<text class="lane" id="name-${o.key}">${o.name}</text><text class="num" id="num-${o.key}"></text></g>`;
  $("svg").innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.3, "var(--blue)", .2)}${stop(.7, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient></defs>` +
    `<g class="atmo"><ellipse cx="${CX}" cy="${CY + 10}" rx="430" ry="240" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${CX + 22}" cy="${CY + 44}" rx="400" ry="200" fill="url(#shade)"/></g>` +
    `<path class="body" id="board-side"/><path class="face" id="board-face"/><path class="rim" id="board-rim"/>` +
    rows.map(o => `<path class="track" id="track-${o.key}"/>`).join("") +
    bar(rows[0]) + `<path class="dim" id="gap-line"/><text class="gaptext" id="gap-text"></text>` + bar(rows[1]) +
    `<text class="plus" id="plus">+${f(rows[1].gain)} points</text>` +
    `<text class="tick" id="tick-0">0</text><text class="tick" id="tick-n" style="text-anchor:end">${D.n} problems</text>`;
}
function place() {
  const q = S.q, g = S.grow, shown = clamp((g - .6) / .4), top = (D.samples - 1) * (TH + GP) * q + TH, end = {};
  const board = rect(-EDGE.u, EDGE.u, EDGE.front, EDGE.back, 0), d = path(board);
  set("board-side", "d", path(hull([...board, ...rect(-EDGE.u, EDGE.u, EDGE.front, EDGE.back, -12)])));
  set("board-face", "d", d); set("board-rim", "d", d);
  rows.forEach(o => {
    const v = LANE[o.key], right = mix(o.single, o.vote, q), u1 = U0 + PER * right * g, us = U0 + PER * o.single * g;
    end[o.key] = u1;
    set("track-" + o.key, "d", path(rect(U0, U0 + PER * D.n, v - HB, v + HB, 0)));
    sheets.forEach(i => {  // sheet i lies on sheet i - 1; with one sample all four are one sheet
      const w = i * (TH + GP) * q, up = rect(U0, u1, v - HB, v + HB, w + TH), face = path(up);
      set(`b-${o.key}${i}`, "d", path(hull([...up, ...rect(U0, u1, v - HB, v + HB, w)])));
      set(`f-${o.key}${i}`, "d", face); set(`r-${o.key}${i}`, "d", face);
    });
    set("wt-" + o.key, "d", path(rect(us, u1, v - HB, v + HB, top)));  // the part the vote adds: its top and its front
    set("ws-" + o.key, "d", path([proj(us, v - HB, 0), proj(u1, v - HB, 0), proj(u1, v - HB, top), proj(us, v - HB, top)]));
    label("name-" + o.key, proj(U0 + 16, v, top), 24, .34, shown);
    label("num-" + o.key, proj(us - 12, v, top), 44, .35, shown);  // the number stays left of the part the vote adds
    $("num-" + o.key).textContent = Math.round(right);
    if (o.key === "base") label("plus", proj((us + u1) / 2, v - HB - 30, 0), 22, .34, clamp(2 * q - 1));
  });
  set("gap-line", "d", seg(proj(end.base, LANE.base + HB, 0), proj(end.base, VGAP + 9, 0)) +
    seg(proj(end.base, VGAP, 0), proj(end.rl, VGAP, 0)) + seg(proj(end.rl, VGAP - 9, 0), proj(end.rl, LANE.rl - HB, 0)));
  set("gap-line", "opacity", f(shown));
  label("gap-text", proj(end.base - 14, VGAP, 0), 24, .34, shown);
  $("gap-text").textContent = `${f(mix(D.gap.single, D.gap.vote, q))} points`;
  label("tick-0", proj(U0, EDGE.front - 26, 0), 20, .34, 1);
  label("tick-n", proj(U0 + PER * D.n + 22, EDGE.front - 26, 0), 20, .34, 1);
}
/* One frame: the view sways slowly and leans toward the pointer, the bars grow once on load, and a change of the
   switch moves both bars to their new length and height. With reduced motion the page shows one still frame. */
function frame(now) {
  const t = now / 1000;
  V.px += (V.tx - V.px) * .06; V.py += (V.ty - V.py) * .06;
  V.yaw = 1.6 * Math.sin(t * .25) + 2 * V.px; V.el = EL + Math.sin(t * .19 + 1) - 2 * V.py;
  S.grow = ease(Math.min(1, t / 1.3));
  S.q = mix(S.from, S.state, ease(Math.min(1, (now - S.t0) / 900)));
  place();
  if (!still.matches) requestAnimationFrame(frame);
}
function draw() {  // the switch, the note and the label follow the state; the bars follow in frame()
  const st = D.states[S.state], k = S.state ? "vote" : "single";
  $("svg").setAttribute("aria-label", `Right answers of ${D.n}, ${st.name.toLowerCase()}: ` +
    D.rows.map(o => `${o.name} ${o[k]}`).join(", ") + `. The RL model is ${f(D.gap[k])} points ahead.`);
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
