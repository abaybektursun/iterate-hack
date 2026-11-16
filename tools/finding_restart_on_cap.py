"""Restarting answers that hit the 16,384-token limit adds 12 points to the cued base model on MATH-500 at T 0.6, and 1.6 at T 1.0.

The page of one finding, served at /finding/restart-on-cap (copied from .claude/skills/finding-page/template.py; draw()
shows the 500 answers of one run as marks on a glass board instead of one bar). It is reached from its tile on
/findings, which ICON draws. Study: studies/rlneurons (README.md "Established numbers", "Day-1 #3" and "Closing cue";
board result-e870a1, result-5d032f and the counter-result result-51fd20).
"""
import json

# Every number is copied from the artifacts named here. None is typed from memory.
DATA = {
    "artifact": "studies/rlneurons/results/rln4/grader_v3/readout.json",
    "commit": "fe1c61e",
    "n": 500,
    "limit": 16384,  # run.max_tokens of the temperature 1.0 run; README.md "A cap hit is an answer that reached 16,384 tokens"
    # cells.base_opener_0.6 (base, cue, T 0.6 / top-p 0.95): right_v3, cap_hits, cap_hits_right_v3
    "single": 354, "cap": 119, "cap_right": 1,
    # cells.K_fresh (restart 1 on every cap hit) and cells.K_fresh2 (restart 2 on every cap hit of restart 1): n, right_v3, cap_hits
    "first": {"n": 119, "right": 42, "cap": 69},
    "second": {"n": 69, "right": 19, "cap": 45},
    "restart": 414,  # restart_row.right_v3 (attempts_hist 1: 381, 2: 50, 3: 69)
    # cells.base_opener_1.0 (one sample at T 1.0 / top-p 1.0, the row before this step on the team's chart): right_v3, cap_hits
    "chart_before": 410, "chart_before_cap": 27,
    # differences_v3 "rl_0.6 - base_opener_0.6" and "restart_row - rl_0.6" (points, 95 % interval), sign turned
    "rl_gap_before": 22.0, "rl_gap_after": 10.0, "rl_gap_after_ci": [7.0, 13.2],
    # restart_row.mean_tokens (9381.654) of the K readout, the same restart row under grader v1
    "tokens_artifact": "studies/rlneurons/results/rln4/modal_k-01/readout.json",
    "restart_tokens": 9382,
    # The same restart at T 1.0 / top-p 1.0, with per-problem rows (rows.jsonl beside the readout). rows.single, rows.restart,
    # differences_points "restart - single", each_sample.cap_hits_attempt_0[0], restart_sample_0.final_cap_hits
    "t10": {
        "artifact": "studies/rlneurons/results/day1_3/math500_base_cue-01/readout.json",
        "rl_artifact": "studies/rlneurons/results/day1_3/math500_rl-01/readout.json",
        "commit": "d1f0136", "run_commit": "c36f562",
        "single": 405, "restart": 413, "diff": 1.6, "ci": [0.6, 2.8], "cap": 25, "cap_three_times": 9,
        "single_tokens": 3808,
        "rl_single": 456, "rl_restart": 458, "rl_diff": 0.4, "rl_ci": [0.0, 1.0],
    },
    # The counter-result (board result-51fd20): sets.hard328.stored and box_8000, headline_hard328.minus_stored, and the
    # largest right_of_stored_cap_hits over the six configurations
    "hard": {
        "artifact": "studies/rlneurons/results/commit1/base-01/readout.json", "commit": "efac028",
        "n": 328, "stored": 164, "cap": 77, "cut_at": 8000, "forced": 152, "diff": 3.7, "ci": [1.2, 6.4], "cap_right_most": 2,
    },
    # The restart scored on the 328 at T 1.0 / top-p 1.0 (board result-5c961a): rows single, restart, vote and
    # vote_after_restart (right), differences_points "restart - single".
    "hard_restart": {
        "artifact": "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/readout.json", "commit": "2c58f34",
        "single": 161, "restart": 172, "diff": 3.4, "ci": [1.5, 5.5], "vote": 192, "vote_restart": 195,
    },
    # rows.math500_base_cue_t06_p10-01 (base, cue, T 0.6 / top-p 1.0): cap_hits, loops_A
    "loops": {"artifact": "studies/rlneurons/results/day1/readout.json", "commit": "3407c6e", "cap": 98, "flagged": 71},
}
D, T10, HARD, LOOPS, HR = DATA, DATA["t10"], DATA["hard"], DATA["loops"], DATA["hard_restart"]
FIRST, SECOND = D["first"], D["second"]
FINISHED = [FIRST["n"] - FIRST["cap"], SECOND["n"] - SECOND["cap"]]  # answers that end below the limit: 50 and 24
# What the picture shows. Before: answers that finished right, finished wrong, or hit the limit. After: where the
# answers at the limit end, by the restart that settles them.
DATA["marks"] = {
    "right": D["single"] - D["cap_right"],  # 353 finished and right
    "wrong": D["n"] - D["cap"] - (D["single"] - D["cap_right"]),  # 28 finished and wrong
    "waves": [{"right": FIRST["right"], "wrong": FINISHED[0] - FIRST["right"]},  # 42 and 8
              {"right": SECOND["right"], "wrong": FINISHED[1] - SECOND["right"]}],  # 19 and 5
    "still": SECOND["cap"],  # 45 hit the limit three times
}
M = DATA["marks"]
NOW_RIGHT = FIRST["right"] + SECOND["right"]  # 61 of the 119 end right after a restart
assert FIRST["cap"] == SECOND["n"] and M["right"] + NOW_RIGHT == D["restart"], "the cells do not add up to the restart row"
GAIN = 100 * (D["restart"] - D["single"]) / D["n"]  # 12.0 points, the same 500 problems before and after
CHART = 100 * (D["restart"] - D["chart_before"]) / D["n"]  # 0.8 points, the step on the team's chart
DATA["now_right"] = NOW_RIGHT

TITLE = "Restarting stuck answers"
PROBLEM = "Does sampling an answer again from the start help when the first try is cut off at the token limit?"
LINE = (f"For the base model with the opening cue, sampling again each answer that was cut off at the token limit adds {GAIN:g} points "
        f"of accuracy on MATH-500 at temperature 0.6, and {T10['diff']:g} at temperature 1.0.")  # also the sentence on its tile
BOLD = [f"{GAIN:g} points", f"{T10['diff']:g}"]  # the two sizes, set heavier in the sentence

# What the reader switches between. The first is shown on load: start from the problem, not from the answer.
DATA["states"] = [
    {"name": "Before restarts", "hash": "no-restart", "right": D["single"], "cap": D["cap"], "now": 0},
    {"name": "After restarts", "hash": "restart", "right": D["restart"], "cap": M["still"], "now": NOW_RIGHT},
]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new", "It was known that the base model, when its answer starts with the opening cue, often writes until the "
     "token limit: Wang et al. (arXiv 2610.06851, Table 13) report that 16 % of its answers reach a limit of 31,744 tokens.",
     ["That paper reports no restart of such answers, and a search of the team's notes found no earlier report of one. The "
      "closest known method resamples from inside a loop, and its authors describe it as a weak fix (arXiv 2512.12895, Appendix B.1).",
      f"New here, at T 0.6: {D['cap']} of {D['n']} answers of this model are cut off at {D['limit']:,} tokens, and sampling "
      f"them again from the start gives a right answer for {NOW_RIGHT} of them.",
      f"New here: the gain depends on the sampling temperature. At T 1.0 only {T10['cap']} of {D['n']} answers are cut off, "
      f"and the same restart adds {T10['diff']:g} points."]],
    ["why", "Why it matters", f"At T 0.6, a restart closes {GAIN:g} of the {D['rl_gap_before']:g} percentage points by which "
     "Base + cue, which has no training, trails the model trained with reinforcement learning (RL) on MATH-500.",
     [f"After the restart Base + cue is {D['rl_gap_after']:.1f} points behind one sample of the RL model at T 0.6 "
      f"(95 % interval {D['rl_gap_after_ci'][0]:.1f} to {D['rl_gap_after_ci'][1]:.1f}).",
      f"Compared with one sample at T 1.0 and no restart ({D['chart_before']} of {D['n']} right; "
      f"{D['chart_before_cap']} of the {D['n']} answers cut off), the restart at T 0.6 ({D['restart']} of {D['n']}) gains only {CHART:g} points.",
      f"After both restarts, {M['still']} answers are still cut off: all three tries reached the limit."]],
    ["how", "How we know", f"Base + cue (the base model Olmo 3 7B with no training, its answer started by the three-token "
     f"opening cue) answered the {D['n']} MATH-500 "
     f"problems once at T 0.6 and top-p 0.95, and every answer cut off at {D['limit']:,} tokens was sampled again "
     "from the start, up to twice.",
     [f"The first restart finishes {FINISHED[0]} of the {FIRST['n']} answers and {FIRST['right']} are right. The second "
      f"finishes {FINISHED[1]} of the other {SECOND['n']} and {SECOND['right']} are right. The grader (version 3) scored "
      f"every answer. {D['cap_right']} of the {D['cap']} cut-off answers had already written its final answer, so it counts "
      "as right without a restart.",
      f"A restart changes only answers that were cut off, so the {D['restart'] - D['single']} extra right answers compare "
      f"the same {D['n']} problems before and after. Only the totals were kept, not a score per problem, so this gain of "
      f"{GAIN:g} points has no interval.",
      f"We repeated the restart at T 1.0 and top-p 1.0, this time with a score per problem: {T10['single']} right answers "
      f"became {T10['restart']}, a gain of {T10['diff']:g} points (95 % interval {T10['ci'][0]:.1f} to "
      f"{T10['ci'][1]:.1f}, from resampling the same problems in both runs). The RL model "
      f"under the same restart gains {T10['rl_diff']:g} points ({T10['rl_ci'][0]:.1f} to {T10['rl_ci'][1]:.1f})."]],
    ["limits", "What it does not show", "It does not show that a cut-off answer is a solved problem that failed to stop. On "
     f"the {HARD['n']} harder problems, forcing the base model to give its answer once it passes {HARD['cut_at']:,} tokens "
     f"loses problems: {HARD['forced']} right against {HARD['stored']}, a loss of {HARD['diff']:.1f} points (95 % interval "
     f"{HARD['ci'][0]:.1f} to {HARD['ci'][1]:.1f}).",
     [f"On those harder problems, at T 1.0, a forced answer is right on at most {HARD['cap_right_most']} of the "
      f"{HARD['cap']} cut-off answers. So on this set, being cut off marks a failure to solve, not a failure to stop. "
      f"Scored on the same set, the restart takes one sample from {HR['single']} to {HR['restart']} right "
      f"(+{HR['diff']:g} points, 95 % interval {HR['ci'][0]:g} to {HR['ci'][1]:g}) but adds only "
      f"{100 * (HR['vote_restart'] - HR['vote']) / HARD['n']:.1f} points to a vote over 4 samples ({HR['vote_restart']} "
      f"against {HR['vote']}).",
      f"The gain of {GAIN:g} points is measured at T 0.6 only. At T 1.0, one sample with no restart is already right on "
      f"{T10['single']} to {D['chart_before']} of {D['n']} (two runs), using {T10['single_tokens']:,} generated tokens per "
      f"problem; the restart at T 0.6 reaches {D['restart']} but uses {D['restart_tokens']:,} tokens per problem.",
      f"We did not record how many of the {D['cap']} cut-off answers repeat themselves. In a "
      f"second run at T 0.6 with top-p 1.0, a repetition detector flags {LOOPS['flagged']} answers, and {LOOPS['cap']} "
      "are cut off. All of this is one benchmark, one pair of models, one seed and one grader."]],
    ["run", "How to reproduce it", "The T 1.0 rows can be run again: one GPU job per model, then a readout on a laptop.",
     ["The job is studies/rlneurons/jobs/run_cell.py with --samples 4 --restarts 2 (commit " + T10["run_commit"] + "), and the "
      "readout is studies/rlneurons/analysis/day1_vote.py. Its numbers are in " + T10["artifact"] + " (commit " + T10["commit"] + ").",
      "The T 0.6 rows were scored by studies/rlneurons/grader/rln4_grader_v3.py from raw answers stored outside the "
      "repository. Their numbers are in " + DATA["artifact"] + " (commit " + DATA["commit"] + "): cells base_opener_0.6, K_fresh "
      "and K_fresh2, and restart_row.",
      "The forced answers on the harder problems are in " + HARD["artifact"] + " (commit " + HARD["commit"] + "), and the "
      "restart on them in " + HR["artifact"] + " (job commit " + HR["commit"] + ")."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with two rows of marks: finished answers at the back, and at the front one answer that a
# restart turned right, lit, beside two that still turn in place.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, top = th / 2, n = x => x.toFixed(1);
  const dot = (u, v, lit) => {
    const p = kit.at(u, v, top), r = 4.2 * p[2], at = `cx="${n(p[0])}" cy="${n(p[1])}"`;
    return lit ? `<circle class="halo" ${at} r="${n(r + 3.4)}"/><circle class="lit" ${at} r="${n(r)}"/>`
      : `<circle class="plain" ${at} r="${n(r)}" opacity=".5"/>`;
  };
  const ring = (u, v, i) => {
    const p = kit.at(u, v, top), r = 4.6 * p[2], c = 2 * Math.PI * r;
    return `<circle cx="${n(p[0])}" cy="${n(p[1])}" r="${n(r)}" fill="none" stroke="var(--red)" stroke-width="${n(1.6 * p[2])}" ` +
      `stroke-linecap="round" stroke-dasharray="${n(.68 * c)} ${n(.32 * c)}" transform="rotate(${n((t * (34 + 9 * i) + 140 * i) % 360)} ${n(p[0])} ${n(p[1])})"/>`;
  };
  return kit.slab(a, b, th) + [-26, 0, 26].map(u => dot(u, -14)).join("") + dot(-26, 14, true) + ring(0, 14, 0) + ring(26, 14, 1);
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
   white porcelain on a cool grey table, with a cast shadow in place of the glow. The light comes from the upper left.
   --halo is how strongly a mark that a restart turned right glows. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --halo: .16; --quiet: .5;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --halo: .3; --quiet: .46;
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
.count { align-self: center; display: flex; align-items: baseline; gap: 14px; margin: 0 0 6px; color: var(--mute); font-size: clamp(15px, 1.3vw, 20px); line-height: 1.2; }
.count b { color: var(--ink); font-size: clamp(54px, 6.67vw, 104px); line-height: 1; font-weight: 660; font-stretch: 100%; letter-spacing: -.02em; min-width: 3ch; text-align: right; }
.count .lab { display: flex; flex-direction: column; }
.count em { font-style: normal; font-size: .86em; }
svg { width: 100%; max-height: 50vh; display: block; overflow: visible; }
.atmo, .shade { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.body { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; stroke-linejoin: round; }
.face { fill: url(#body) var(--sheet); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1.4; stroke-linejoin: round; }
/* A mark is one answer. Right: a quiet dot. Wrong: a small faint dot. Cut off at the limit: an open ring that turns in
   place, in the colour of a problem. With "Restart" a ring that ends right becomes a dot in the accent. */
.r { fill: var(--ink); opacity: var(--quiet); }
.w, .to-wrong .dot { fill: var(--mute); }
.ring { fill: none; stroke: var(--red); stroke-width: 2.4; stroke-linecap: round; stroke-dasharray: 30 14; animation: spin var(--s) linear var(--p) infinite; }
.ring, .rw, .dot, .halo { transform-box: fill-box; transform-origin: center; }
.rw { transition: transform .3s ease, opacity .3s ease; }
.dot, .halo { transform: scale(0); transition: transform .3s ease; }
.to-right .dot { fill: var(--blue); }
.halo { fill: var(--blue); opacity: var(--halo); }
.on .to-right .rw, .on .to-wrong .rw { transform: scale(.2); opacity: 0; transition-delay: var(--d); }
.on .to-right .dot, .on .to-right .halo, .on .to-wrong .dot { transform: scale(1); transition: transform .42s cubic-bezier(.3, 1.5, .5, 1) calc(var(--d) + .08s); }
.on .again .rw { animation: again .4s ease var(--d1) 1; }
.on .still .rw { animation: again .4s ease var(--d1) 1, again .4s ease var(--d2) 1; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes again { 45% { transform: scale(.25); opacity: .35; } }
.key { align-self: center; display: flex; flex-wrap: wrap; justify-content: center; gap: 4px 26px; list-style: none; margin: 12px 0 0; padding: 0; color: var(--mute); font-size: 16.5px; min-height: 1.5em; }
.key li { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.key b { color: var(--ink); font-weight: 620; }
.key i { display: block; width: 14px; height: 14px; border-radius: 50%; flex: none; }
.key .g-cap { border: 2.4px solid var(--red); border-right-color: transparent; animation: spin 3.4s linear infinite; }
.key .g-now { background: var(--blue); box-shadow: 0 0 0 4px color-mix(in srgb, var(--blue) calc(var(--halo) * 100%), transparent); }
.key .g-wrong { width: 9px; height: 9px; margin: 0 2px; background: var(--mute); }
.key .g-right { background: var(--ink); opacity: var(--quiet); }
.key [hidden] { display: none; }
.switch { display: inline-flex; align-self: center; margin-top: 16px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: calc(clamp(20px, 7vh, 96px) - 39.5px) 0 0 40px; border-left: 1px solid var(--rule);
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
/* The way back to the grid of findings: the first line of the side column */
a.back { display: inline-block; font-size: 13px; color: var(--mute); padding: 10px 0; margin: -10px 0 6px; }
a.back:hover { color: var(--ink); }
/* Nothing in the side column is cut: a column taller than the window scrolls the whole page, and the picture stays in view */
@media (min-width: 901px) {
  .page { height: auto; min-height: max(100vh, 620px); }
  .stage { position: sticky; top: 0; align-self: start; height: calc(100vh - 87.5px); min-height: 532.5px; }
  .side { overflow-y: visible; }
}
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  a.back { order: 0; margin-top: 14px; align-self: flex-start; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
  .switch button { padding: 12px 12px; font-size: 14px; }
  .ring { stroke-width: 3; }
  .key { min-height: 3.2em; align-content: flex-start; }
}
@media (prefers-reduced-motion: reduce) {
  svg, .ring, .rw, .key .g-cap { animation: none !important; }
  .rw, .dot, .halo, .switch button, .more button { transition: none !important; }
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
    <p class="count"><b id="right"></b><span class="lab"><span id="of"></span><em><span id="pct"></span> % · Base + cue, T 0.6</em></span></p>
    <svg id="svg" viewBox="0 0 760 452" role="img"></svg>
    <ul class="key" aria-live="polite">
      <li><i class="g-right"></i>right</li>
      <li><i class="g-cap"></i><span><b id="cap"></b> cut off</span></li>
      <li id="now-item" hidden><i class="g-now"></i><span><b id="now"></b> now right</span></li>
      <li><i class="g-wrong"></i>wrong</li>
    </ul>
    <div class="switch" id="switch" role="group" aria-label="Restart"></div>
  </div>
  <div class="side">
    <a class="back" href="/findings">‹ All findings</a>
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, M = D.marks, $ = id => document.getElementById(id);
const S = { state: 0, open: null, q: 0, from: 0, t0: -1e9 };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q, ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;

/* The picture: the 500 answers of one run as marks on a glass board seen from slightly above, 25 to a row. From the
   back: the answers that finished right, the ones that finished wrong, and at the front the ones that were cut off at
   the limit, each an open ring that turns in place. The artifact holds totals, so a mark stands for one answer and its
   place says nothing about which problem it is. With "Restart" every ring starts again, as in the run: the first restart
   settles some (right or wrong), the second settles some of the rest, and the others are cut off a third time. */
const RAD = Math.PI / 180, CX = 380, CY = 204, EL = 52, COLS = 25, PITCH = 24, TH = 12;
const ROWS = Math.ceil(D.n / COLS), HU = COLS * PITCH / 2 + 14, HV = ROWS * PITCH / 2 + 14;
const V = { px: 0, py: 0, tx: 0, ty: 0 };  // the lean toward the pointer
function proj(u, v, w, yaw = 0, el = EL) {  // u to the right, v away from the viewer, w up; what is near is larger
  const a = yaw * RAD, e = el * RAD, x = u * Math.cos(a) - v * Math.sin(a), d = u * Math.sin(a) + v * Math.cos(a);
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
const corners = w => [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => proj(i * HU, j * HV, w));
const REF = [[-HU, HV], [HU, HV], [0, -HV]], REST = REF.map(([u, v]) => proj(u, v, 0));  // three points of the board, at rest
let seed = 7;
const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;  // the same picture on every load

function build() {
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  // Where each answer at the limit ends: settled by the first restart (wave 0) or the second (wave 1), or never.
  const ends = [];
  M.waves.forEach((w, i) => { for (let k = 0; k < w.right; k++) ends.push([i, "to-right"]); for (let k = 0; k < w.wrong; k++) ends.push([i, "to-wrong"]); });
  for (let k = 0; k < M.still; k++) ends.push([2, "still"]);
  for (let k = ends.length - 1; k > 0; k--) { const j = Math.floor(rand() * (k + 1)); [ends[k], ends[j]] = [ends[j], ends[k]]; }
  let marks = "";
  for (let i = 0; i < D.n; i++) {
    const c = i % COLS, r = Math.floor(i / COLS), p = proj((c - COLS / 2 + .5) * PITCH, (ROWS / 2 - .5 - r) * PITCH, 0);
    const at = `cx="${f(p[0])}" cy="${f(p[1])}"`;
    if (i < M.right) marks += `<circle class="r" ${at} r="${f(6 * p[2])}"/>`;
    else if (i < M.right + M.wrong) marks += `<circle class="w" ${at} r="${f(4.2 * p[2])}"/>`;
    else {
      const [wave, end] = ends[i - M.right - M.wrong], d1 = .02 + .28 * c / COLS + .1 * rand(), d2 = d1 + .4;  // all settled within 1.3 s
      marks += `<g class="cap ${end}${wave === 1 ? " again" : ""}" transform="translate(${f(p[0])} ${f(p[1])}) scale(${p[2].toFixed(3)})" ` +
        `style="--d:${f(wave ? d2 : d1)}s;--d1:${f(d1)}s;--d2:${f(d2)}s;--s:${f(2.6 + 2.4 * rand())}s;--p:-${f(5 * rand())}s">` +
        `<g class="rw"><circle class="ring" r="7"/></g>` +
        (end === "to-right" ? `<circle class="halo" r="10.5"/><circle class="dot" r="6.4"/>` : end === "to-wrong" ? `<circle class="dot" r="4.2"/>` : "") + `</g>`;
    }
  }
  const top = path(corners(0));
  $("svg").innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.3, "var(--blue)", .2)}${stop(.7, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient></defs>` +
    `<g class="atmo"><ellipse cx="${CX}" cy="${CY}" rx="430" ry="270" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${CX + 20}" cy="${CY + 46}" rx="400" ry="240" fill="url(#shade)"/></g>` +
    `<g id="scene"><path class="body" d="${path(hull([...corners(0), ...corners(-TH)]))}"/><path class="face" d="${top}"/><path class="rim" d="${top}"/>${marks}</g>`;
}
/* The view sways by a few degrees and leans toward the pointer. The scene is drawn once, at rest; each frame sets one
   attribute, the affine map that carries three points of the board from rest to where the swayed view puts them. */
function sway(yaw, el) {
  const [[x1, y1], [x2, y2], [x3, y3]] = REST, [[X1, Y1], [X2, Y2], [X3, Y3]] = REF.map(([u, v]) => proj(u, v, 0, yaw, el));
  const det = (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3);
  const a = ((X1 - X3) * (y2 - y3) - (X2 - X3) * (y1 - y3)) / det, c = ((x1 - x3) * (X2 - X3) - (x2 - x3) * (X1 - X3)) / det;
  const b = ((Y1 - Y3) * (y2 - y3) - (Y2 - Y3) * (y1 - y3)) / det, d = ((x1 - x3) * (Y2 - Y3) - (x2 - x3) * (Y1 - Y3)) / det;
  const n = v => v.toFixed(4);
  $("scene").setAttribute("transform", `matrix(${n(a)} ${n(b)} ${n(c)} ${n(d)} ${n(X3 - a * x3 - c * y3)} ${n(Y3 - b * x3 - d * y3)})`);
}
function counts(q) {  // the numbers follow the marks
  const [a, b] = D.states, set = (id, v) => { v = String(Math.round(v)); if ($(id).textContent !== v) $(id).textContent = v; };
  set("right", mix(a.right, b.right, q)); set("cap", mix(a.cap, b.cap, q)); set("now", mix(a.now, b.now, q));
  $("pct").textContent = f(100 * Math.round(mix(a.right, b.right, q)) / D.n);
}
function frame(now) {
  const t = now / 1000;
  V.px += (V.tx - V.px) * .06; V.py += (V.ty - V.py) * .06;
  sway(2 * Math.sin(t * .25) + 2.5 * V.px, EL + Math.sin(t * .19 + 1) - 2 * V.py);
  const q = mix(S.from, S.state, ease(Math.min(1, (now - S.t0) / (S.state ? 950 : 450))));  // the count stops within 1 s
  if (q !== S.q) { S.q = q; counts(q); }
  requestAnimationFrame(frame);
}
function draw() {  // the switch, the key and the label follow the state; the marks follow in CSS, the numbers in frame()
  const st = D.states[S.state], wrong = D.n - st.right - st.cap + (S.state ? 0 : D.cap_right);
  $("svg").classList.toggle("on", S.state === 1);
  $("svg").setAttribute("aria-label", `${D.n} answers of Base + cue at T 0.6, ${st.name.toLowerCase()}: ${st.right} right, ` +
    (S.state ? `${st.now} of them after a restart, ` : "") + `${st.cap} cut off at ${D.limit.toLocaleString("en-US")} tokens, ${wrong} finished and wrong`);
  $("now-item").hidden = S.state === 0;
  $("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}" aria-pressed="${i === S.state}">${s.name}</button>`).join("");
}
function choose(i) {
  if (i === S.state) return;
  S.from = S.q; S.state = i; S.t0 = performance.now();
  draw();
  if (still.matches) { S.q = i; counts(i); }
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${p[1]}</h2><button class="close" data-open="">Close</button></div><p class="lead">${p[2]}</p>` +
      `<ul class="facts">${p[3].map(f => `<li>${f}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${p[1]}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
/* The state and the open panel are one value in the address: #<state>, #<panel> or #<state>/<panel>. */
const HK = D.states.map(s => s.hash);
function address(push) {
  const parts = [S.state ? HK[S.state] : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash() {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/"), k = HK.indexOf(parts[0]);
  choose(k < 0 ? 0 : k);
  S.open = parts.find(x => C.panels.some(p => p[0] === x)) || null;
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
  if (s) { choose(Number(s.dataset.state)); address(false); document.querySelector(`[data-state="${S.state}"]`).focus(); }
  if (o) open(o.dataset.open);
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) open("");
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") { choose((S.state + 1) % D.states.length); address(false); }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
$("stage").addEventListener("pointermove", e => {  // the view leans a few degrees toward a mouse, and settles back
  if (e.pointerType !== "mouse") return;
  const r = $("stage").getBoundingClientRect();
  V.tx = 2 * (e.clientX - r.left) / r.width - 1; V.ty = 2 * (e.clientY - r.top) / r.height - 1;
});
$("stage").addEventListener("pointerleave", () => { V.tx = V.ty = 0; });
$("problem").textContent = C.problem;
$("say").innerHTML = C.bold.reduce((s, b) => s.replace(b, `<b>${b}</b>`), C.line);
$("of").textContent = `of ${D.n} right`;
build();
draw();
S.q = 0; counts(0);
fromHash();
if (S.state) { S.from = S.q = S.state; S.t0 = -1e9; counts(S.state); }  // a state read from the address is shown at once
if (!still.matches) requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "bold": BOLD, "data": DATA, "panels": PANELS}))
