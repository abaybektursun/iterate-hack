"""A vote over 6 samples of Base + cue scores 456.6 of 500 on MATH-500, within RL's one-sample range, at 5.2 times the tokens.

The page of one finding, served at /finding/vote-over-four (the slug keeps its first name; copied from
.claude/skills/finding-page/template.py). draw() shows each model's score as a glass bar on a glass board: Base + cue in
front as a stack of k sheets, one per sample in the vote, RL behind as one sheet with its one-sample range lit across the
board, and RL's own vote over 4 samples as a dotted stack of 4. The control sets k from 1 to 12. It is reached from its
tile on /findings, which ICON draws. Study: studies/rlneurons (README.md "Vote over k samples of the cued base" and
"Day-1 #3"; board result-1c9e40, result-5d032f and result-60d899).

    uv run --no-project --with numpy --with math-verify==0.9.0 python tools/finding_vote_over_four.py

run from the repository root, recomputes every number of DATA from the artifacts it was copied from and fails on a change.
"""
import json

# Every number is copied from the artifacts named here. None is typed from memory. The deployed site ships only tools/*.py,
# so the copy is a literal; run this file to compare it with the artifacts.
VOTEK = "studies/rlneurons/results/votek/math500_base_cue-01/"
DATA = {
    # The 4-sample jobs of both models (README.md "Day-1 #3"). tools/findings.py reads "artifact", BASE["gain"] and
    # BASE["vote"] for the tile: the vote over the first 4 samples of Base + cue, 405 -> 446.
    "artifact": "studies/rlneurons/results/day1_3/math500_base_cue-01/readout.json",
    "artifact_rl": "studies/rlneurons/results/day1_3/math500_rl-01/readout.json",
    "commit": "c36f562",  # run.json of both jobs
    "n": 500,
    # rows.single and rows.vote (right, tokens_per_problem), differences_points["vote - single"], each_sample.single_right
    "rows": [
        {"key": "base", "name": "Base + cue, T 1.0", "single": 405, "vote": 446, "gain": 8.2, "gain_ci": [5.8, 10.8],
         "tokens_single": 3808.138, "tokens_vote": 16033.55, "each": [405, 409, 410, 418]},
        {"key": "rl", "name": "RL, T 1.0", "single": 456, "vote": 474, "gain": 3.6, "gain_ci": [2.0, 5.2],
         "tokens_single": 4675.104, "tokens_vote": 18747.16, "each": [456, 462, 464, 458]},
    ],
    "rl_other_job": 463,  # results/rln4/grader_v3/readout.json, cells["rl_1.0"].right_v3: RL, T 1.0, another job
    # The vote over k of 12 samples of Base + cue (board result-1c9e40): metrics.json of VOTEK, at commit e3c4056.
    # k: [k, right (mean over 200 random subsets of k of the 12; all 12 at k = 12), 95 % interval (bootstrap over problems,
    # 2,000 resamples), lowest and highest subset, at least one of k right, generated tokens per problem]
    "votek": VOTEK + "metrics.json", "votek_commit": "e3c4056", "samples": 12, "subsets": 200,
    "k": [[1, 410.0, 397.9, 421.6, 405, 418, 410.0, 4059], [2, 418.9, 407.2, 430.4, 411, 426, 452.3, 8122],
          [3, 440.8, 429.4, 451.8, 430, 452, 464.7, 12155], [4, 449.2, 437.9, 460.0, 441, 457, 471.0, 16228],
          [5, 453.5, 442.3, 464.0, 445, 463, 475.6, 20291], [6, 456.6, 445.6, 467.1, 448, 465, 478.4, 24370],
          [7, 458.3, 447.6, 468.6, 452, 467, 480.5, 28407], [8, 460.1, 449.6, 470.2, 454, 467, 482.4, 32463],
          [9, 461.4, 450.9, 471.6, 455, 468, 483.8, 36487], [10, 462.6, 452.1, 472.8, 458, 467, 485.1, 40568],
          [11, 463.9, 453.3, 474.0, 461, 468, 486.1, 44624], [12, 466.0, 455.0, 476.0, 466, 466, 487.0, 48680]],
    "first4": 446,  # vote_over_first_4_in_order: the control, equal to the 4-sample job's vote
    "stop2": [459.0, 2.71, 15882],  # stop_at_m_votes["2"]: right, samples per problem, tokens per problem
    "wrong12_no_right": 13,  # vote_all_wrong_by_right_samples["0"]; the vote over 12 is wrong on 500 - 466 = 34
    # Two problems, all 12 samples (rows.jsonl of VOTEK; problem text and answer key from
    # studies/rlneurons/data/rln4/math500.json): [index, problem, answer key, [answer, right, tokens] x 12, votes of the
    # winner, vote over 12 right]. Problem 21 was picked as one the vote over 12 gets right with 5 of 12 samples right;
    # problem 9 is the wrong example of examples.json.
    "examples": [
        [21, "Find the greatest integer less than $(\\sqrt{7} + \\sqrt{5})^6.$  (Do not use a calculator!)", "13535",
         [[None, 0, 16384], ["13535", 1, 12178], ["13535", 1, 3462], ["14959", 0, 15469], ["13431", 0, 11388],
          ["13535", 1, 14962], ["13535", 1, 9006], [None, 0, 16384], ["13464.", 0, 11251], ["13479", 0, 3850],
          ["13535", 1, 4261], [None, 0, 16384]], 5, 1],
        [9, "The expression $2\\cdot 3 \\cdot 4\\cdot 5+1$ is equal to 121, since multiplication is carried out before "
            "addition. However, we can obtain values other than 121 for this expression if we are allowed to change it by "
            "inserting parentheses. For example, we can obtain 144 by writing \\[\n(2\\cdot (3\\cdot 4)) \\cdot (5+1) = "
            "144.\n\\]In total, how many values can be obtained from the expression $2\\cdot 3\\cdot 4 \\cdot 5 + 1$ by "
            "inserting parentheses? (Note that rearranging terms is not allowed, only inserting parentheses).", "4",
         [["5", 0, 11280], ["2", 0, 11685], [None, 0, 16384], [None, 0, 16384], [None, 0, 16384], ["' line\".", 0, 16384],
          ["4", 1, 9353], ["8", 0, 14259], [None, 0, 16384], ["4", 1, 14763], ["5", 0, 8335], [None, 0, 16384]], 2, 0],
    ],
    # Board result-60d899: read from the rendered Figure 21 of arXiv 2610.06851, to about 1 point. Board knowledge-8a31ad:
    # the paper's RL model and its score (Table 6).
    "published_vote": 88.5, "published_rl": 75.0,
    # 328 harder problems, RL minus Base + cue under the same vote over 4 samples after restart (board result-5c961a):
    # day1_3/hard328_rl_plain_s4r2-01/readout.json, minus.differences_points.vote_after_restart
    "hard_rl_lead_restart": [8.8, 5.5, 12.5],
}
BASE, RL, N = DATA["rows"][0], DATA["rows"][1], DATA["n"]
K = {r[0]: r for r in DATA["k"]}
RL1 = {"lo": min(RL["each"]), "hi": max(RL["each"]), "mean": sum(RL["each"]) / len(RL["each"])}  # RL's one-sample range
DATA["rl1"] = RL1
times = lambda tokens: tokens / RL["tokens_single"]  # tokens against one RL sample (its first, 4,675 per problem)
_m = lambda v: str(v).replace("-", "\u2212")  # a negative number with the minus sign U+2212
_n = lambda v: f"{v:,.0f}"
K0 = 6  # the state the page opens on

TITLE = "Vote over 6 samples"
PROBLEM = ("Over how many samples must the base model with the opening cue vote to match a model trained by "
           "reinforcement learning (RL)?")
LINE = (f"A vote over {K0} samples of the base model with the opening cue averages {K[K0][1]} of {N} on MATH-500, inside "
        f"the RL model's one-sample range ({RL1['lo']} to {RL1['hi']}), at {times(K[K0][7]):.1f} times the tokens of one RL sample.")  # also the sentence on its tile

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new", f"New here: this run takes the vote to {DATA['samples']} samples and measures where it meets the RL model. Voting over "
     "several samples is known as self-consistency, and Wang et al. (arXiv 2610.06851, Figure 21) plot about "
     f"{DATA['published_vote']} % for a vote over 4 samples of this base model with the cue.",
     [f"Over 6 samples the vote has {K[6][1]} of {N}, inside the range of RL's four one-sample scores, {RL1['lo']} to "
      f"{RL1['hi']}. Over 8 it has {K[8][1]}, level with their mean of {RL1['mean']:.1f}, and over 12 it has {K[12][1]:.0f}, "
      f"95 % interval {K[12][2]:.0f} to {K[12][3]:.0f}.",
      "The plan predicted that the vote would stop rising after 6 samples, with fewer than 3 more problems from 6 to 12. "
      f"It rose by {K[12][1] - K[6][1]:.1f} problems, so that prediction was wrong. Source: studies/rlneurons/specs/SPEC_votek.md, "
      "prediction V2.",
      f"The paper's RL model is the earlier Olmo 3 release, which scores {DATA['published_rl']} % there. This page compares "
      "with the stronger Olmo 3.1 RL model."]],
    ["why", "Why it matters", "The team's research goal is the cheapest way to reach the RL model's score without training on a reward. A vote over "
     "samples of Base + cue reaches the RL model's one-sample range with no training, but it costs "
     f"{times(K[6][7]):.1f} times the tokens of one RL sample.",
     [f"Over 6 samples Base + cue generates {_n(K[6][7])} tokens per problem; one RL sample generates "
      f"{_n(RL['tokens_single'])}.",
      f"Drawing samples until two answers agree, at most 12, gives {DATA['stop2'][0]} of {N} at {_n(DATA['stop2'][2])} tokens "
      f"per problem, {times(DATA['stop2'][2]):.1f} times one RL sample. No interval was computed for this rule.",
      f"RL's own vote over 4 samples has {RL['vote']} of {N} at {_n(RL['tokens_vote'])} tokens per problem. No vote of "
      f"Base + cue here reaches it, not even over 12 samples at {_n(K[12][7])} tokens."]],
    ["how", "How we know", f"The base model with the opening cue (the tokens \" line!\", a blank line, \"Okay\") answered each of the {N} MATH-500 "
     f"problems {DATA['samples']} times at temperature 1.0 and top-p 1.0 (grader version 3). The score of a vote over k samples "
     f"is the mean over {DATA['subsets']} random choices of k of the {DATA['samples']}.",
     [f"Samples 1 to 4 come from an earlier 4-sample run; samples 5 to 12 come from new runs whose seeds continue that run's "
      f"sequence. The vote over the first 4 samples reproduces that run's {DATA['first4']} of {N}; the mean over choices of 4 is {K[4][1]}, and "
      f"single choices of 4 range from {K[4][4]} to {K[4][5]}.",
      f"The 95 % intervals of that mean come from 2,000 bootstrap resamples of the {N} problems: {K[6][2]} to {K[6][3]} over 6 "
      f"samples, and {K[12][2]:.0f} to {K[12][3]:.0f} over all 12.",
      f"The RL model's range is the four one-sample scores of its own 4-sample run, {', '.join(map(str, RL['each'][:3]))} and "
      f"{RL['each'][3]} of {N}. Another RL run at temperature 1.0 had {DATA['rl_other_job']}."]],
    ["limits", "What it does not show", "It does not show that voting replaces RL training: at about equal tokens the RL model is ahead, "
     f"with {RL['vote']} of {N} for its vote over 4 samples at {_n(RL['tokens_vote'])} tokens per problem, against "
     f"{K[4][1]} for Base + cue's vote over 4 at {_n(K[4][7])}.",
     ["Only MATH-500 is measured; this run has not been repeated on the 328 harder problems. There, an earlier comparison "
      "with a vote over 4 samples, in which an answer cut off at the token limit is sampled again, has the RL model "
      f"{DATA['hard_rl_lead_restart'][0]} percentage points ahead (95 % interval "
      f"{DATA['hard_rl_lead_restart'][1]} to {DATA['hard_rl_lead_restart'][2]}).",
      "A sample without an extracted answer casts no vote. Answers the grader finds equal form one group, the largest group "
      "wins, and a tie goes to the group whose first member has the lowest sample number, so a tie is broken by sample "
      "order, not by the answers.",
      f"The vote over 12 samples misses {N - K[12][1]:.0f} problems: on {DATA['wrong12_no_right']} no sample is right, and on "
      f"{N - K[12][1] - DATA['wrong12_no_right']:.0f} a wrong answer gets at least as many votes as the right one."]],
    ["run", "How to reproduce it", "The answers are in six job folders, one earlier job and five shards of a new one, and "
     "studies/rlneurons/analysis/votek.py scores them on a laptop.",
     ["Samples 1 to 4: job abaybektursun-1114-153825-208b, jobs/run_cell.py --model base --prompt cue --set math500 "
      "--temperature 1.0 --top-p 1.0 --seed 41000000 --samples 4 --restarts 2, commit " + DATA["commit"] + ", of which the "
      "first attempt of each sample is used. Samples 5 to 12: the same command with --seed 41040000 --samples 8 and no "
      "restarts, in 5 shards.",
      "The readout command, with the job folders, is in " + VOTEK + "run.json and in studies/rlneurons/README.md, section "
      "\"Vote over k samples of the cued base\"; the plan is studies/rlneurons/specs/SPEC_votek.md.",
      "The numbers are in " + VOTEK + " (metrics.json, and rows.jsonl with all 6,000 answers) and, for RL, in "
      + DATA["artifact_rl"] + ". Running tools/finding_vote_over_four.py recomputes this page's numbers from them."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced to the base model's bar seen from above. Six lines are the six samples of the vote; each is plain up to the score
# of one sample and lit from there to the score of the vote over 6.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, top = th / 2, x0 = -a * .8, at = right => x0 + a * 1.6 * right / __N__;
  return kit.slab(a, b, th) + [0, 1, 2, 3, 4, 5].map(i => {
    const v = b * (-.6 + .24 * i);
    return kit.line(kit.at(x0, v, top), kit.at(at(__SINGLE__), v, top), 2.2, "plain", .6) +
      kit.line(kit.at(at(__SINGLE__), v, top), kit.at(at(__VOTE__), v, top), 2.6 + .25 * Math.sin(t * .6 + i), "lit");
  }).join("");
}""".replace("__N__", str(N)).replace("__SINGLE__", str(K[1][1])).replace("__VOTE__", str(K[K0][1]))

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
   --wash is how strongly the part of a bar that the vote adds takes the accent; --band is RL's one-sample range. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --wash: .34; --band: .1; --band-on: .26;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --wash: .46; --band: .12; --band-on: .32;
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
.atmo, .shade, .wash, .band, .track, .ghost { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.body { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; stroke-linejoin: round; }
.face { fill: url(#body) var(--sheet); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1.3; stroke-linejoin: round; }
.track { fill: none; stroke: var(--faint); stroke-width: 1; stroke-dasharray: 2 5; }
.ghost { fill: none; stroke: var(--ink); stroke-width: 1.2; stroke-dasharray: 3 4; stroke-linejoin: round; opacity: .5; }
.wash { fill: var(--blue); opacity: var(--wash); }
.band { fill: var(--blue); }
.edge { stroke: var(--blue); stroke-width: 1.2; opacity: .55; pointer-events: none; }
.lane { font-weight: 560; fill: var(--mute) !important; }
.lane.rlv { text-anchor: end; }
.num { font-weight: 640; text-anchor: end; letter-spacing: -.02em; }
.num .of { font-weight: 520; fill: var(--mute); letter-spacing: 0; }
.cost { font-weight: 540; fill: var(--mute) !important; text-anchor: end; }
.plus { font-weight: 640; fill: var(--blue) !important; text-anchor: middle; }
.band-name { fill: var(--blue) !important; }
.tick { fill: var(--mute); font-weight: 520; text-anchor: middle; }
.hit { fill: transparent; stroke: none; cursor: pointer; }
.hit:focus { outline: none; }
.hit:focus-visible { stroke: var(--blue); stroke-width: 2; }
.ctl { align-self: center; display: flex; flex-direction: column; align-items: center; margin-top: 16px; }
.ctl-name { font-size: 13px; color: var(--mute); font-weight: 540; margin-bottom: 7px; }
.switch { display: inline-flex; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { min-width: 36px; padding: 7px 0; border-radius: 999px; font-weight: 600; font-size: 15px; text-align: center; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button[aria-pressed="true"]:hover { color: var(--paper); }
.note { align-self: center; margin: 10px 0 0; color: var(--mute); font-size: 14.5px; text-align: center; max-width: 62ch; min-height: 3em; transition: opacity .2s ease; }
.note.fade { opacity: 0; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
.say .nw { white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); flex: none; }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.ex { margin: 22px 0 0; padding-top: 12px; border-top: 1px solid var(--ink); max-width: 40ch; }
.ex h3 { margin: 0; font-size: 14px; font-weight: 640; font-stretch: 110%; }
.ex .q { margin: 6px 0 0; font-size: 14.5px; line-height: 1.45; overflow-wrap: anywhere; }
.ex .key { margin: 6px 0 0; font-size: 13.5px; color: var(--mute); }
.ex .key b { color: var(--ink); font-weight: 620; }
.answers { list-style: none; margin: 10px 0 0; padding: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px 10px; font-size: 13.5px; }
.answers li { display: flex; gap: 6px; align-items: baseline; min-width: 0; color: var(--mute); }
.answers li span { flex: none; width: 1.6em; text-align: right; color: var(--faint); font-size: 12px; }
.answers li b { font-weight: 560; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.answers li.r b { color: var(--blue); font-weight: 640; }
.answers li.none b { font-weight: 400; font-style: italic; color: var(--faint); }
.ex .out { margin: 10px 0 0; font-size: 13.5px; color: var(--mute); }
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
  .switch button { min-width: 26px; padding: 7px 0; font-size: 14px; }
  .note { min-height: 4.5em; }
}
@media (prefers-reduced-motion: reduce) {
  svg { animation: none; }
  .switch button, .more button, .note { transition: none; }
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
    <svg id="svg" viewBox="0 0 760 400" role="img"></svg>
    <div class="ctl">
      <span class="ctl-name" id="ctl-name">Samples in the vote of Base + cue</span>
      <div class="switch" id="switch" role="group" aria-labelledby="ctl-name"></div>
    </div>
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
const KS = D.k.map(r => r[0]), K = Object.fromEntries(D.k.map(r => [r[0], r])), K0 = C.k0, RLT = D.rows[1].tokens_single;
const S = { k: K0, kFrom: K0, kf: K0, vFrom: K[K0][1], v: K[K0][1], t0: -1e9, grow: 0, t1: null, open: null, noted: K0 };
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q, ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
const clamp = p => Math.max(0, Math.min(1, p)), num = n => Math.round(n).toLocaleString("en-US");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const right = (k, v) => k === 12 && v === K[12][1] ? String(v) : f(v);  // all 12 samples are one subset: a whole count
const times = k => f(K[k][7] / RLT);

/* The picture: glass bars on a glass board seen from slightly above, Base + cue in front and RL behind. A bar's length
   is its right answers of 500; the dotted outline is all 500. The Base + cue bar is a stack of k sheets, one per sample in
   the vote, as long as the vote's score; the part the vote adds over one sample is lit. RL is one sheet as long as the mean
   of its four one-sample scores, and the range of those scores is a lit band across the board, so the reader sees the
   Base + cue bar reach it. RL's own vote over 4 samples is a dotted stack of 4 sheets: at k = 4 both stacks cost about
   the same tokens. */
const RAD = Math.PI / 180, CX = 380, CY = 186, EL = 56;
const U0 = -300, PER = 600 / D.n, HB = 34, TH = 6, GP = 3;  // the left end, units per problem, half depth, sheet, gap
const LANE = { base: -92, rl: 92 }, EDGE = { u: 334, front: -206, back: 196 };
const V = { yaw: 0, el: EL, px: 0, py: 0, tx: 0, ty: 0 };  // the view: a slow sway, plus a few degrees toward the pointer
const at = r => U0 + PER * r;
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
const rect = (u0, u1, v0, v1, w) => [proj(u0, v0, w), proj(u1, v0, w), proj(u1, v1, w), proj(u0, v1, w)];
const box = (u0, u1, v0, v1, w0, w1) => hull([...rect(u0, u1, v0, v1, w0), ...rect(u0, u1, v0, v1, w1)]);
const set = (id, name, value) => $(id).setAttribute(name, value);
function still3(u, v, w) {  // where a point of the scene is in the view at rest: the words stand there, upright and still
  const yaw = V.yaw, el = V.el;
  V.yaw = 0; V.el = EL;
  const c = proj(u, v, w);
  V.yaw = yaw; V.el = el;
  return c;
}
const least = () => 12.5 * 760 / ($("svg").clientWidth || 760);  // the font size, in units of the picture, of 12.5 px on screen
function label(id, c, size, dy, opacity) {  // a text that stays upright at a point of the scene, never below 12.5 px
  if (narrow.matches && size < 24) size *= 1.6;
  const px = Math.max(size * c[2], least());
  set(id, "x", f(c[0])); set(id, "y", f(c[1] + dy * px)); set(id, "font-size", f(px)); set(id, "opacity", f(opacity));
}
const ofSize = (id, share) => f(Math.max(share * parseFloat($(id).getAttribute("font-size")), least()));
const SHEETS = [...Array(D.samples).keys()];
const sheet = (id, i) => `<path class="body" id="b-${id}${i}"/><path class="face" id="f-${id}${i}"/><path class="rim" id="r-${id}${i}"/>`;
const hit = (id, what) => `<path class="hit" id="hit-${id}" data-mark="${id}" tabindex="0" role="button" aria-label="${what}"/>`;

function build() {
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  $("svg").innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.3, "var(--blue)", .2)}${stop(.7, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient></defs>` +
    `<g class="atmo"><ellipse cx="${CX}" cy="${CY + 6}" rx="430" ry="240" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${CX + 22}" cy="${CY + 40}" rx="400" ry="200" fill="url(#shade)"/></g>` +
    `<path class="body" id="board-side"/><path class="face" id="board-face"/><path class="rim" id="board-rim"/>` +
    `<path class="band" id="band"/><path class="edge" id="edge-lo"/><path class="edge" id="edge-hi"/>` +
    `<path class="track" id="track-rl"/><path class="track" id="track-base"/>` +
    // RL, behind: one sheet, its vote over 4 samples as a dotted stack, and the words on the board behind it
    sheet("rl", 0) + `<path class="ghost" id="ghost"/>` +
    `<text class="lane" id="name-rl"></text>` +
    `<text class="lane rlv" id="name-rlv">RL, vote over 4 samples (dotted): ${D.rows[1].vote} at ${num(D.rows[1].tokens_vote)} tokens</text>` +
    `<text class="num" id="num-rl">${D.rl1.lo} to ${D.rl1.hi}<tspan class="of" id="of-rl"></tspan></text>` +
    hit("rlvote", "RL, vote over 4 samples") + hit("rl", "RL, one sample") +
    // Base + cue, in front: up to 12 sheets, the lit part the vote adds, and its words
    SHEETS.map(i => sheet("base", i)).join("") + `<path class="wash" id="ws"/><path class="wash" id="wt"/>` +
    `<text class="num" id="num-base"><tspan id="cnt-base"></tspan><tspan class="of" id="of-base"></tspan></text>` +
    `<text class="lane" id="name-base"></text><text class="cost" id="cost-base"></text><text class="plus" id="plus"></text>` +
    `<text class="lane rlv band-name" id="name-band">RL's one-sample range</text>` + hit("base", "Base + cue, vote over k samples") +
    `<text class="tick" id="tick-0">0</text><text class="tick" id="tick-n" style="text-anchor:end">${D.n} problems</text>`;
}
function place() {
  const g = S.grow, shown = clamp((g - .6) / .4), kf = S.kf, v = S.v, step = TH + GP;
  const board = rect(-EDGE.u, EDGE.u, EDGE.front, EDGE.back, 0), d = path(board);
  set("board-side", "d", path(hull([...board, ...rect(-EDGE.u, EDGE.u, EDGE.front, EDGE.back, -12)])));
  set("board-face", "d", d); set("board-rim", "d", d);
  // RL's one-sample range, lit on the board from the back of the RL lane to the front edge; brighter once Base + cue is in it
  const lo = at(D.rl1.lo), hi = at(D.rl1.hi), into = clamp((v - D.rl1.lo + 3) / 3);
  set("band", "d", path(rect(lo, hi, LANE.base - HB - 8, LANE.rl + HB, 0)));
  $("band").style.opacity = `calc(${f(shown)} * (var(--band) + (var(--band-on) - var(--band)) * ${into.toFixed(3)}))`;
  [["edge-lo", lo], ["edge-hi", hi]].forEach(([id, u]) => {
    const a = proj(u, LANE.base - HB - 8, 0), b = proj(u, LANE.rl + HB, 0);
    set(id, "d", `M${f(a[0])} ${f(a[1])}L${f(b[0])} ${f(b[1])}`); set(id, "opacity", f(.55 * shown));
  });
  for (const key of ["rl", "base"]) set("track-" + key, "d", path(rect(U0, at(D.n), LANE[key] - HB, LANE[key] + HB, 0)));
  // RL: one sheet to the mean of its four one-sample scores; the dotted stack of its vote over 4 samples
  const r1 = at(mix(0, D.rl1.mean, g)), rl = LANE.rl, top4 = 3 * step + TH;
  const up = rect(U0, r1, rl - HB, rl + HB, TH);
  set("b-rl0", "d", path(hull([...up, ...rect(U0, r1, rl - HB, rl + HB, 0)]))); set("f-rl0", "d", path(up)); set("r-rl0", "d", path(up));
  const ghost = box(U0, at(D.rows[1].vote), rl - HB, rl + HB, 0, top4);
  set("ghost", "d", path(ghost)); set("ghost", "opacity", f(.5 * shown));
  set("hit-rl", "d", path(box(U0, r1, rl - HB, rl + HB - 1, 0, TH)));
  set("hit-rlvote", "d", path(ghost));
  // On a phone RL's name moves behind its bar and the words of the dotted stack move to the line under the control
  if (narrow.matches) label("name-rl", still3(U0 + 4, rl + HB + 54, 0), 17, 0, shown);
  else label("name-rl", still3(U0 + 14, rl, TH), 20, .35, shown);
  set("name-rl", "style", "text-anchor:start");
  label("name-rlv", still3(at(D.rows[1].vote), rl + HB + 44, 0), 17, 0, narrow.matches ? 0 : shown);
  label("num-rl", still3(at(D.rl1.lo) - 14, rl, TH), 30, .35, shown);
  set("of-rl", "font-size", ofSize("num-rl", .55));
  // Base + cue: sheet i rises out of sheet i - 1 as kf passes i, so a change of k stacks or lifts sheets one after another
  const b = LANE.base, u1 = at(v * g), us = at(K[1][1] * g);
  let top = TH;
  SHEETS.forEach(i => {
    const a = i === 0 ? 1 : clamp(kf - i), w = i === 0 ? 0 : (i - 1 + ease(a)) * step, t = rect(U0, u1, b - HB, b + HB, w + TH);
    ["b", "f", "r"].forEach(p => $(`${p}-base${i}`).style.opacity = a > 0 ? Math.min(1, a * 1.6).toFixed(3) : 0);
    if (a > 0) {
      set(`b-base${i}`, "d", path(hull([...t, ...rect(U0, u1, b - HB, b + HB, w)])));
      set(`f-base${i}`, "d", path(t)); set(`r-base${i}`, "d", path(t));
      top = Math.max(top, w + TH);
    }
  });
  const lit = u1 > us + .5;
  set("wt", "d", lit ? path(rect(us, u1, b - HB, b + HB, top)) : "M0 0");
  set("ws", "d", lit ? path([proj(us, b - HB, 0), proj(u1, b - HB, 0), proj(u1, b - HB, top), proj(us, b - HB, top)]) : "M0 0");
  set("hit-base", "d", path(box(U0, Math.max(u1, us), b - HB, b + HB, 0, top)));
  // The count, as "456.6 of 500 (91.3 %)", stands on the stack and ends where one sample ends, left of the lit part
  label("num-base", still3(at(K[1][1]) - 14, b, top), 44, .1, shown);
  const cnt = S.kf === S.k && S.v === K[S.k][1] ? right(S.k, S.v) : f(v), of = ` of ${D.n} (${f(100 * v / D.n)} %)`;
  if ($("cnt-base").textContent !== cnt) { $("cnt-base").textContent = cnt; $("of-base").textContent = of; }
  set("of-base", "font-size", ofSize("num-base", .5));
  label("name-base", still3(U0 + 4, b - HB - 20, 0), 20, .34, shown); set("name-base", "style", "text-anchor:start");
  // Under the bar: its name, the points the vote adds (in the lit part's color) and its tokens; a phone has less width
  const n = narrow.matches;
  label("cost-base", still3(at(D.n), b - HB - (n ? 58 : 48), 0), 17, .34, shown);
  label("plus", still3(n ? at(D.n) : U0 + 4, b - HB - (n ? 20 : 48), 0), 17, .34, shown * clamp((v - K[1][1]) / 4));
  set("plus", "style", n ? "text-anchor:end" : "text-anchor:start");
  $("plus").textContent = `+${f((v - K[1][1]) * 100 / D.n)} ` + (narrow.matches ? "points" : "percentage points over one sample");
  // RL's range is named between the lanes; when a tall stack reaches up to the name, the name gives way
  const nb = still3(lo - 10, 46, 0), reach = still3(lo, b + HB, top)[1];
  label("name-band", nb, 17, .34, shown);
  set("name-band", "opacity", f(shown * clamp((reach - nb[1] - 4) / 8)));
  label("tick-0", still3(U0, EDGE.front - 24, 0), 17, .34, 1);
  label("tick-n", still3(at(D.n) + 22, EDGE.front - 24, 0), 17, .34, 1);
}
/* One frame: the view sways slowly and leans toward the pointer, the bars grow once on load, and a change of k moves the
   stack to its new height and length while the count runs with it. With reduced motion the page shows one still frame. */
function frame(now) {
  const t = now / 1000;
  V.px += (V.tx - V.px) * .06; V.py += (V.ty - V.py) * .06;
  V.yaw = 1.6 * Math.sin(t * .25) + 2 * V.px; V.el = EL + Math.sin(t * .19 + 1) - 2 * V.py;
  S.t1 ??= now;  // the entrance starts with the first frame shown, so a tab opened in the background still plays it
  S.grow = ease(Math.min(1, (now - S.t1) / 1300));
  const p = Math.min(1, (now - S.t0) / 900), q = ease(p);
  S.kf = p >= 1 ? S.k : mix(S.kFrom, S.k, q); S.v = p >= 1 ? K[S.k][1] : mix(S.vFrom, K[S.k][1], q);
  if (p >= .6 && S.noted !== S.k) note();  // the words of the new state come with its numbers, not before them
  place();
  if (!still.matches) requestAnimationFrame(frame);
}
function note() {  // the line under the control: what the bar now shows, and what it costs
  const k = S.k, r = K[k];
  S.noted = k;
  $("note").textContent = k === 1
    ? `One sample, no vote: the mean over ${D.subsets} random choices of 1 of the ${D.samples} samples, at ${num(r[7])} tokens per problem.`
    : k === 12
      ? `Vote over all 12 samples: 95 % interval ${r[2].toFixed(0)} to ${r[3].toFixed(0)}, at ${num(r[7])} tokens per problem, ${times(k)} times one RL sample.`
      : `Mean over ${D.subsets} random choices of ${k} of the ${D.samples} samples` + (k === 4 ? ` (the first 4 alone give ${D.first4})` : "") +
        `, at ${num(r[7])} tokens per problem, ${times(k)} times one RL sample.`;
  if (narrow.matches) $("note").textContent += ` The dotted outline is RL's vote over 4 samples: ${D.rows[1].vote} of ${D.n} at ${num(D.rows[1].tokens_vote)} tokens per problem.`;
  $("cost-base").textContent = `${num(r[7])} tokens` + (narrow.matches ? "" : " per problem");
  $("name-rl").textContent = narrow.matches ? "RL, T 1.0, one sample" : "RL, T 1.0";
  $("name-base").textContent = "Base + cue, T 1.0" + (narrow.matches ? "" : k === 1 ? ", one sample" : `, vote over ${k} samples`);
  $("of-rl").textContent = ` of ${D.n}` + (narrow.matches ? "" : ", one sample");
}
function draw() {  // the control and the description follow the state; the bars follow in frame()
  const k = S.k, r = K[k];
  $("svg").setAttribute("aria-label", `Right answers of ${D.n} on MATH-500, T 1.0. Base + cue, vote over ${k} sample${k > 1 ? "s" : ""}: ` +
    `${right(k, r[1])}. RL, one sample: ${D.rl1.lo} to ${D.rl1.hi}. RL, vote over 4 samples: ${D.rows[1].vote}.`);
  $("switch").innerHTML = KS.map(i => `<button data-k="${i}" aria-pressed="${i === k}" aria-label="${i} sample${i > 1 ? "s" : ""}">${i}</button>`).join("");
}
function choose(k) {
  if (k === S.k) return;
  S.kFrom = S.kf; S.vFrom = S.v; S.k = k; S.t0 = still.matches ? -1e9 : performance.now();
  draw();
  if (still.matches) { S.grow = 1; S.kf = k; S.v = K[k][1]; note(); place(); }
  if (["base"].includes(S.open)) pane();  // an open detail shows the new k
}

/* The side column: the five panels, or the detail of a clicked bar */
function answers(e) {
  const [i, q, key, rows, votes, ok] = e, n = rows.filter(a => a[1]).length;
  return `<div class="ex"><h3>MATH-500, problem ${i}: the vote over 12 is ${ok ? "right" : "wrong"}</h3>` +
    `<p class="q" data-math>${esc(q.length > 300 ? q.slice(0, 300) + "…" : q)}</p>` +
    `<p class="key">The answer key says <b data-math>${esc(key)}</b>. Each sample's final answer, right ones in blue:</p>` +
    `<ol class="answers">${rows.map((a, j) => `<li class="${a[0] === null ? "none" : a[1] ? "r" : "w"}"><span>${j + 1}</span>` +
      `<b ${a[0] === null ? "" : "data-math"} title="${esc(a[0] ?? "")}">${a[0] === null ? "none" : esc(a[0])}</b></li>`).join("")}</ol>` +
    `<p class="out">${n} of 12 samples are right. ` + (ok ? `The right answer has the most votes, ${votes}.` : n === votes
      ? `A wrong answer also has ${votes} votes and its first sample comes earlier, so it wins the tie.` : `A wrong answer has more votes, ${votes}.`) + `</p></div>`;
}
function detail(key) {
  const k = S.k, r = K[k], R = D.rows[1];
  if (key === "base") return [`Base + cue, T 1.0, vote over ${k} sample${k > 1 ? "s" : ""}`,
    `${right(k, r[1])} of ${D.n} (${f(100 * r[1] / D.n)} %)` + (k === 12 ? ", all 12 samples." : `, the mean over ${D.subsets} random choices of ${k} of the ${D.samples} samples.`),
    [`95 % interval ${k === 12 ? r[2].toFixed(0) : r[2]} to ${k === 12 ? r[3].toFixed(0) : r[3]}` + (k < 12 ? `; single choices of ${k} range from ${r[4]} to ${r[5]}.` : "."),
     `${num(r[7])} tokens per problem, ${times(k)} times one RL sample (${num(RLT)}).`,
     k === 1 ? "One sample has no vote: it is right or wrong." : `${k === 12 ? "At least" : "On average over the random choices, at least"} one of the ${k} samples is right on ${k === 12 ? r[6].toFixed(0) : r[6]} problems; the vote picks a right answer on ${right(k, r[1])}.`],
    D.examples.map(answers).join("")];
  if (key === "rl") return ["RL, T 1.0, one sample",
    `The four one-sample scores of one RL run: ${R.each.slice(0, 3).join(", ")} and ${R.each[3]} of ${D.n}, mean ${f(D.rl1.mean)}.`,
    [`The first sample generates ${num(RLT)} tokens per problem.`, `Another RL run at T 1.0 had ${D.rl_other_job}.`,
     "RL is Olmo-3.1-7B-RL-Zero-Math, the same base model after reinforcement learning on math."], ""];
  return ["RL, T 1.0, vote over 4 samples", `${R.vote} of ${D.n} (${f(100 * R.vote / D.n)} %) at ${num(R.tokens_vote)} tokens per problem.`,
    [`At about the same tokens Base + cue has ${K[4][1]} over 4 samples (${num(K[4][7])} tokens) and ${K[5][1]} over 5 (${num(K[5][7])}).`,
     `Drawing Base + cue samples until two answers agree gives ${D.stop2[0]} at ${num(D.stop2[2])} tokens.`,
     "So at about the same number of tokens, the RL model stays ahead."], ""];
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open), m = ["base", "rl", "rlvote"].includes(S.open) ? detail(S.open) : null;
  const head = (h, lead, facts) => `<div class="dhead"><h2>${h}</h2><button class="close" data-open="">Close</button></div>` +
    `<p class="lead">${lead}</p><ul class="facts">${facts.map(x => `<li>${x}</li>`).join("")}</ul>`;
  $("pane").innerHTML = m ? head(...m) + m[3] : p ? head(p[1], p[2], p[3])
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${p[1]}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
/* The state and the open panel or bar are one value in the address: #k-<k>, #<panel>, or #k-<k>/<panel>; k = 6 is the
   default and is left out. The two addresses of the earlier switch still work. */
const OLD = { "one-sample": 1, vote: 4 }, OPEN = ["base", "rl", "rlvote", ...C.panels.map(p => p[0])];
function address(push) {
  const parts = [S.k !== K0 ? "k-" + S.k : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash() {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/"), m = /^k-(\d+)$/.exec(parts[0]) || [];
  const k = Number(m[1]) || OLD[parts[0]];
  choose(KS.includes(k) ? k : K0);
  S.open = parts.find(x => OPEN.includes(x)) || null;
  pane();
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ block: "start", behavior: still.matches ? "auto" : "smooth" }); };
function open(key) {  // a panel or a bar's detail opens in the side column; the keyboard focus follows it there and back
  const was = S.open;
  S.open = key || null;
  address(true);
  pane();
  const to = key ? $("pane").querySelector(".close") : $("pane").querySelector(`[data-open="${was}"]`) || document.querySelector(`[data-mark="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  if (key) show();
}
document.addEventListener("click", e => {
  const s = e.target.closest("[data-k]"), o = e.target.closest("[data-open]"), m = e.target.closest("[data-mark]");
  if (s) { choose(Number(s.dataset.k)); address(false); document.querySelector(`[data-k="${S.k}"]`).focus(); }
  if (o) open(o.dataset.open);
  if (m) open(S.open === m.dataset.mark ? "" : m.dataset.mark);
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const m = e.target.closest && e.target.closest("[data-mark]");
  if (m && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); open(m.dataset.mark); return; }
  if (e.key === "Escape" && S.open) open("");
  const i = KS.indexOf(S.k), j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : -1;
  if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && j >= 0 && j < KS.length) {
    choose(KS[j]); address(false);
    if (e.target.closest && e.target.closest("[data-k]")) document.querySelector(`[data-k="${S.k}"]`).focus();
  }
});
narrow.addEventListener("change", () => { note(); place(); });
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
$("stage").addEventListener("pointermove", e => {  // the view leans a few degrees toward a mouse, and settles back
  if (e.pointerType !== "mouse") return;
  const r = $("stage").getBoundingClientRect();
  V.tx = 2 * (e.clientX - r.left) / r.width - 1; V.ty = 2 * (e.clientY - r.top) / r.height - 1;
});
$("stage").addEventListener("pointerleave", () => { V.tx = V.ty = 0; });
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)(?! samples)/g, "<b>$1</b>").replace(/MATH-500/g, '<span class="nw">MATH-500</span>');
build();
draw();
fromHash();
S.kFrom = S.kf = S.k; S.vFrom = S.v = K[S.k][1]; S.t0 = -1e9;  // a state read from the address is shown at once
note();
if (still.matches) { S.grow = 1; place(); } else requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "k0": K0, "data": DATA,
                                                                   "panels": PANELS}))


if __name__ == "__main__":  # DATA against its artifacts; run from the repository root (the command is in the docstring)
    import sys

    import numpy as np

    sys.path.insert(0, ".")
    from studies.rlneurons.analysis import votek as V

    load = lambda path: json.load(open(path))
    m, run = load(DATA["votek"]), load(VOTEK + "run.json")
    # 1. DATA against metrics.json of the readout
    assert (m["problems"], m["samples"]) == (N, DATA["samples"])
    for k, right, lo, hi, smin, smax, anyr, tok in DATA["k"]:
        x = m["k"][str(k)]
        assert [x["vote_right"], *x["ci95"], *x["subset_min_max"], x["any_right"], x["tokens_per_problem"]] == [right, lo, hi, smin, smax, anyr, tok], k
    assert m["vote_over_first_4_in_order"] == DATA["first4"] == BASE["vote"]
    s2 = m["stop_at_m_votes"]["2"]
    assert [s2["vote_right"], s2["samples_per_problem"], s2["tokens_per_problem"]] == DATA["stop2"]
    assert m["vote_all_wrong_by_right_samples"]["0"] == DATA["wrong12_no_right"]
    assert sum(m["vote_all_wrong_by_right_samples"].values()) == N - K[12][1]
    assert run["runs"][0]["commit"].startswith(DATA["commit"]) and run["runs"][0]["job_id"] == "abaybektursun-1114-153825-208b"
    assert all(r["seed"] == 41040000 and r["samples"] == 8 for r in run["runs"][1:]) and len(run["runs"]) == 6
    # 2. the readout recomputed from rows.jsonl with the readout's own vote and random draws (analysis/votek.py, main)
    per = {}
    for line in open(VOTEK + "rows.jsonl"):
        r = json.loads(line)
        per.setdefault(r["problem_index"], []).append(r)
    probs = sorted(per)
    assert len(probs) == N and all([r["sample"] for r in per[p]] == list(range(12)) for p in probs)
    same = {p: V.agree_table(per[p]) for p in probs}
    rng = np.random.default_rng(0)
    bs = rng.integers(0, N, (2000, N))
    assert sum(V.vote(per[p], same[p], range(4))["score"] for p in probs) == DATA["first4"]
    for k in range(1, 13):
        subsets = [sorted(rng.choice(12, k, replace=False).tolist()) for _ in range(V.SUBSETS)] if k < 12 else [list(range(12))]
        v = np.array([[V.vote(per[p], same[p], sub)["score"] for p in probs] for sub in subsets], dtype=float)
        pm = v.mean(0)
        b = pm[bs].sum(1)
        tok = np.mean([[sum(per[p][s]["n_new"] for s in sub) for p in probs] for sub in subsets])
        got = [round(float(pm.sum()), 1), round(float(np.percentile(b, 2.5)), 1), round(float(np.percentile(b, 97.5)), 1),
               int(v.sum(1).min()), int(v.sum(1).max()), round(float(tok))]
        assert got == [K[k][i] for i in (1, 2, 3, 4, 5, 7)], (k, got)
        print(f"k = {k:2}: {got[0]} of {N}, recomputed from rows.jsonl")
    # 3. the two examples against rows.jsonl, the problem file and the readout's vote
    text = load("studies/rlneurons/data/rln4/math500.json")
    for i, q, key, rows, votes, ok in DATA["examples"]:
        rs = per[i]
        assert text[i]["problem"] == q and text[i]["answer"] == key == rs[0]["gold"], i
        assert rows == [[r["extracted_v3"], r["score_v3"], r["n_new"]] for r in rs], i
        w = V.vote(rs, same[i], range(12))
        assert (w["votes"], w["score"]) == (votes, ok), i
    assert load(VOTEK + "examples.json")[1]["problem_index"] == DATA["examples"][1][0]
    # 4. the 4-sample jobs of both models, and RL's other job
    for row, path in ((BASE, DATA["artifact"]), (RL, DATA["artifact_rl"])):
        x = load(path)
        assert [x["rows"]["single"]["right"], x["rows"]["vote"]["right"], x["rows"]["single"]["tokens_per_problem"],
                x["rows"]["vote"]["tokens_per_problem"]] == [row["single"], row["vote"], row["tokens_single"], row["tokens_vote"]], path
        g = x["differences_points"]["vote - single"]
        assert [g["points"], round(g["interval95"][0], 1), round(g["interval95"][1], 1)] == [row["gain"], *row["gain_ci"]], path
        assert x["each_sample"]["single_right"] == row["each"], path
    assert load("studies/rlneurons/results/rln4/grader_v3/readout.json")["cells"]["rl_1.0"]["right_v3"] == DATA["rl_other_job"]
    h = load("studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/readout.json")["minus"]["differences_points"]["vote_after_restart"]
    assert [round(h["points"], 1), round(h["interval95"][0], 1), round(h["interval95"][1], 1)] == DATA["hard_rl_lead_restart"]
    # 5. the sentences
    assert (K[K0][1], round(times(K[K0][7]), 1), RL1["lo"], RL1["hi"]) == (456.6, 5.2, 456, 464)
    assert RL1["lo"] <= K[6][1] <= RL1["hi"] < K[12][1] < RL["vote"]
    print("DATA matches its artifacts")
