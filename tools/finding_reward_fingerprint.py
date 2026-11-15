"""The reward that trained an RL model is readable from the top 8 input directions of its weight change.

The page of one finding, served at /finding/reward-fingerprint (after .claude/skills/finding-page/template.py; draw()
shows the seven RL-Zero models of Olmo 3 7B as glass blocks on a board, joined by lines as wide as the overlap of their
top-8 subspaces, with a switch between the whole weight change, the top 8 directions and the step-100 checkpoints, and
a click on a model for its numbers). Study: studies/rlneurons (README.md "xreward", Part 1, on branch sharedsub; board
result-9d979a). Unlisted until reviewed: UNLISTED keeps it off /findings, and the page is reachable by its link only.
"""
import json

UNLISTED = True

RL = ["math31", "math30", "code31", "code30", "mix30", "if30", "general30"]

# Every number is copied from the two readouts named here (branch sharedsub), rounded to 4 decimals. None is typed from
# memory. Each table is a mean over the 224 layer matrices.
DATA = {
    "artifact": "studies/rlneurons/results/xreward/overlap-01/readout.json",
    "artifact_steps": "studies/rlneurons/results/xreward/overlap_steps-01/readout.json",
    "branch": "sharedsub", "commit": "c8c6ddd",
    "job": "abaybektursun-1114-220151-daaa", "job_steps": "abaybektursun-1114-221259-0871",
    "matrices": 224, "k": 8,  # n_matrices, k
    "random": 0.001953125,  # hypotheses.overlap_right.random_subspace.4096
    # overlap-01 tables.overlap_right: the input side, final models
    "right": {
        "math31": {"math30": 0.4764, "code31": 0.2599, "code30": 0.2185, "mix30": 0.1536, "if30": 0.0258, "general30": 0.0448, "think_sft": 0.1086, "base_w": 0.0421},
        "math30": {"math31": 0.4764, "code31": 0.254, "code30": 0.2249, "mix30": 0.197, "if30": 0.0338, "general30": 0.0489, "think_sft": 0.0886, "base_w": 0.0441},
        "code31": {"math31": 0.2599, "math30": 0.254, "code30": 0.4247, "mix30": 0.1993, "if30": 0.0317, "general30": 0.0473, "think_sft": 0.0748, "base_w": 0.037},
        "code30": {"math31": 0.2185, "math30": 0.2249, "code31": 0.4247, "mix30": 0.3064, "if30": 0.0618, "general30": 0.0956, "think_sft": 0.0749, "base_w": 0.0357},
        "mix30": {"math31": 0.1536, "math30": 0.197, "code31": 0.1993, "code30": 0.3064, "if30": 0.3797, "general30": 0.2443, "think_sft": 0.0496, "base_w": 0.0359},
        "if30": {"math31": 0.0258, "math30": 0.0338, "code31": 0.0317, "code30": 0.0618, "mix30": 0.3797, "general30": 0.1869, "think_sft": 0.0149, "base_w": 0.0208},
        "general30": {"math31": 0.0448, "math30": 0.0489, "code31": 0.0473, "code30": 0.0956, "mix30": 0.2443, "if30": 0.1869, "think_sft": 0.0268, "base_w": 0.0416},
    },
    # overlap-01 tables.overlap_left: the output side, the three pairs the page names
    "left": {"math31|math30": 0.0982, "code31|code30": 0.0821, "if30|general30": 0.0485},
    # overlap-01 tables.cos: the cosine of the two whole weight changes
    "cos": {
        "math31": {"math30": 0.0201, "code31": 0.016, "code30": 0.0026, "mix30": 0.0092, "if30": 0.0006, "general30": 0.0021, "think_sft": 0.0, "base_w": -0.0012},
        "math30": {"math31": 0.0201, "code31": 0.0075, "code30": 0.0188, "mix30": 0.0261, "if30": 0.0012, "general30": 0.0036, "think_sft": 0.0004, "base_w": -0.0009},
        "code31": {"math31": 0.016, "math30": 0.0075, "code30": 0.0198, "mix30": 0.0163, "if30": 0.001, "general30": 0.0029, "think_sft": 0.0001, "base_w": -0.0009},
        "code30": {"math31": 0.0026, "math30": 0.0188, "code31": 0.0198, "mix30": 0.0681, "if30": 0.0062, "general30": 0.0141, "think_sft": 0.0003, "base_w": -0.0009},
        "mix30": {"math31": 0.0092, "math30": 0.0261, "code31": 0.0163, "code30": 0.0681, "if30": 0.1004, "general30": 0.0372, "think_sft": 0.0006, "base_w": -0.0011},
        "if30": {"math31": 0.0006, "math30": 0.0012, "code31": 0.001, "code30": 0.0062, "mix30": 0.1004, "general30": 0.0187, "think_sft": 0.0004, "base_w": -0.0009},
        "general30": {"math31": 0.0021, "math30": 0.0036, "code31": 0.0029, "code30": 0.0141, "mix30": 0.0372, "if30": 0.0187, "think_sft": 0.0003, "base_w": -0.0007},
    },
    # overlap_steps-01 tables.overlap_right, rows <key>_s100: a run's step-100 checkpoint against each final model
    "step100": {
        "math31": {"math31": 0.2472, "math30": 0.2901, "code31": 0.1352, "code30": 0.1102, "mix30": 0.1512, "if30": 0.0463, "general30": 0.0561, "think_sft": 0.0471, "base_w": 0.0353},
        "math30": {"math31": 0.305, "math30": 0.3977, "code31": 0.1753, "code30": 0.1404, "mix30": 0.156, "if30": 0.0406, "general30": 0.0515, "think_sft": 0.0551, "base_w": 0.0376},
        "code31": {"math31": 0.1192, "math30": 0.1424, "code31": 0.3008, "code30": 0.201, "mix30": 0.1696, "if30": 0.0549, "general30": 0.0617, "think_sft": 0.0363, "base_w": 0.0296},
        "code30": {"math31": 0.2234, "math30": 0.233, "code31": 0.4461, "code30": 0.5845, "mix30": 0.4106, "if30": 0.1003, "general30": 0.1591, "think_sft": 0.074, "base_w": 0.0381},
        "mix30": {"math31": 0.1006, "math30": 0.1203, "code31": 0.1468, "code30": 0.2052, "mix30": 0.3773, "if30": 0.1711, "general30": 0.3261, "think_sft": 0.0365, "base_w": 0.0366},
        "if30": {"math31": 0.0278, "math30": 0.0363, "code31": 0.0341, "code30": 0.0691, "mix30": 0.4126, "if30": 0.7515, "general30": 0.2287, "think_sft": 0.0162, "base_w": 0.0234},
        "general30": {"math31": 0.0375, "math30": 0.0419, "code31": 0.0405, "code30": 0.0914, "mix30": 0.2456, "if30": 0.1885, "general30": 0.4934, "think_sft": 0.0213, "base_w": 0.0415},
    },
    # overlap_steps-01 per_key.<key>_s100.rel_norm, in % of the weight norm
    "step100_norm": {"math31": 0.028, "math30": 0.029, "code31": 0.032, "code30": 0.119, "mix30": 0.031, "if30": 0.194, "general30": 0.04},
    # hypotheses.overlap_right.nearest_rl_model, and hypotheses.steps.S1_nearest_final_of_another_run
    "nearest": {"math31": "math30", "math30": "math31", "code31": "code30", "code30": "code31", "mix30": "if30", "if30": "mix30", "general30": "mix30"},
    "nearest_step100": {"math31": "math30", "math30": "math31", "code31": "code30", "code30": "code31", "mix30": "general30", "if30": "mix30", "general30": "mix30"},
    # run.json "models" (the repository of each key), and where the model stands on the board of the picture
    # (u to the right, v away from the viewer): the two Math and the two Code releases left, Mix between, IF and General right
    "models": [
        {"key": "math31", "name": "Math 3.1", "short": "M3.1", "repo": "allenai/Olmo-3.1-7B-RL-Zero-Math", "u": -270, "v": 105},
        {"key": "math30", "name": "Math 3.0", "short": "M3.0", "repo": "allenai/Olmo-3-7B-RL-Zero-Math", "u": -110, "v": 105},
        {"key": "code31", "name": "Code 3.1", "short": "C3.1", "repo": "allenai/Olmo-3.1-7B-RL-Zero-Code", "u": -270, "v": -105},
        {"key": "code30", "name": "Code 3.0", "short": "C3.0", "repo": "allenai/Olmo-3-7B-RL-Zero-Code", "u": -110, "v": -105},
        {"key": "mix30", "name": "Mix", "label": "Mix of rewards", "short": "Mix", "repo": "allenai/Olmo-3-7B-RL-Zero-Mix", "u": 60, "v": 0},
        {"key": "if30", "name": "Instructions", "short": "IF", "repo": "allenai/Olmo-3-7B-RL-Zero-IF", "u": 250, "v": 105},
        {"key": "general30", "name": "General", "short": "Gen", "repo": "allenai/Olmo-3-7B-RL-Zero-General", "u": 250, "v": -105},
    ],
}
R, COS, S100 = DATA["right"], DATA["cos"], DATA["step100"]
NAME = {m["key"]: m["name"] for m in DATA["models"]}
# The nearest neighbours the readouts report follow from the tables copied above.
assert all(max(RL, key=lambda b: R[a].get(b, 0)) == DATA["nearest"][a] for a in RL)
assert all(max((b for b in RL if b != a), key=lambda b: S100[a][b]) == DATA["nearest_step100"][a] for a in RL)
assert all(abs(t[a][b] - t[b][a]) < 1e-9 for t in (R, COS) for a in RL for b in RL if a != b)

f3 = lambda x: f"{x:.3f}"
SAME = [R["math31"]["math30"], R["code31"]["code30"]]  # same reward, another release
SFT = max(R[a]["think_sft"] for a in RL)  # the largest overlap of an RL model with the fine-tune that used no RL
BASE_W = max(R[a]["base_w"] for a in RL)  # the largest overlap with the base matrix's own top 8 directions
COS_NO_MIX = max(COS[a][b] for a in RL for b in RL if a != b and "mix30" not in (a, b))
COS_MAX = max(COS[a][b] for a in RL for b in RL if a != b)
NORM = [min(DATA["step100_norm"].values()), max(DATA["step100_norm"].values())]
# The key of the picture, one per state of the switch: the widest line between two releases of one reward, and the reference levels.
PAIRS = [("math31", "math30"), ("math30", "math31"), ("code31", "code30"), ("code30", "code31")]
DATA["key"] = [
    [[max(COS[a][b] for a, b in PAIRS), "same reward"], [COS_MAX, "largest, Mix"]],
    [[SAME[0], "same reward"], [SFT, "no RL"], [DATA["random"], "random"]],
    [[max(S100[a][b] for a, b in PAIRS), "same reward"], [max(S100[a]["think_sft"] for a in RL), "no RL"], [DATA["random"], "random"]],
]

TITLE = "Reward fingerprint"
PROBLEM = "Can you tell from a model's weights which reward trained it?"
LINE = f"Runs with the same reward overlap {f3(SAME[1])} to {f3(SAME[0])} in weight space; a random pair, {f3(DATA['random'])}."  # also the tile's sentence

# What the reader switches between. The first is shown on load: start from the problem, not from the answer.
DATA["states"] = [
    {"name": "Whole change", "note": f"Compared as whole weight changes, the models look unrelated: no pair without Mix has a cosine above {f3(COS_NO_MIX)}. "
                                     "The overlap appears in the top 8 directions."},
    {"name": "Top 8 directions", "note": "The overlap of the 8 strongest input directions of each weight change. A line's width is the overlap. "
                                         "Click a model for its numbers."},
    {"name": "After 100 steps", "note": f"Each run after 100 RL steps, when its weights have moved {NORM[0]:.2f} to {NORM[1]:.2f} % of their norm, "
                                        "against the final models of the other runs."},
]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new", "It was known that fine-tunes on the same data share more of the top directions of their weight change than "
     "fine-tunes on different data.",
     ["The closest published result is arXiv 2610.22438 (Table 14): on a 0.5B model without RL, the top-16 subspaces overlap 0.26 to 0.32 "
      "for the same data with another seed, 0.20 to 0.22 for different data and 0.04 at random.",
      f"New here: among seven released RL models of one 7B base model, the two releases of a reward are each other's nearest neighbour "
      f"(4 of 4), and Mix, trained on a mixture of the rewards, overlaps every ingredient: Instructions {f3(R['mix30']['if30'])}, "
      f"Code 3.0 {f3(R['mix30']['code30'])}, General {f3(R['mix30']['general30'])}, Math 3.0 {f3(R['mix30']['math30'])}.",
      f"New here: the reward is already readable after 100 RL steps, when the weights have moved {NORM[0]:.2f} to {NORM[1]:.2f} % of their norm."]],
    ["why", "Why it matters", "What a reward writes into the base model is concentrated in a few directions per layer matrix, "
     "and those directions are set in the first 100 steps.",
     [f"The whole weight changes look unrelated: the cosine between two models is at most {f3(COS_NO_MIX)} without Mix and {f3(COS_MAX)} with it. "
      "A comparison of whole differences misses the structure.",
      f"Math and Code share directions ({f3(R['math30']['code30'])} to {f3(R['math31']['code31'])}), and so do Instructions and General "
      f"({f3(R['if30']['general30'])}). Math with Instructions ({f3(R['math31']['if30'])}) or General ({f3(R['math31']['general30'])}) is below Math with "
      f"Think-SFT, a fine-tune that used no RL ({f3(R['math31']['think_sft'])}).",
      "For the question of what RL adds to the base model, this names a small part of the weight change to test. It does not yet say what that part does."]],
    ["how", "How we know", f"For each model we took its weight change from the base model, and in each of the {DATA['matrices']} layer matrices "
     f"kept the {DATA['k']} strongest input directions (the top right singular vectors).",
     [f"The overlap of two models is the mean squared cosine between their two subspaces, averaged over the {DATA['matrices']} matrices: "
      f"0 is unrelated, 1 is identical, and two random subspaces give {f3(DATA['random'])}.",
      f"Controls: Think-SFT, a fine-tune of the same base that used no RL, overlaps the seven models at most {f3(SFT)}, and the base matrix's own "
      f"top 8 directions at most {f3(BASE_W)}. Before it reads the models, the job must recover a subspace planted in two test matrices.",
      "The step-100 neighbours were predicted before that run: 6 of 7 came out as predicted. Mix is nearest General, and the prediction was Instructions.",
      "table"]],
    ["limits", "What it does not show", "It does not show that these directions cause any behaviour. This is a comparison of weights only.",
     [f"The sharing is on the input side: Math 3.0 with Math 3.1 is {f3(SAME[0])} there and {f3(DATA['left']['math31|math30'])} on the output side. "
      "That the input side follows the kind of text a run generated is our interpretation, and it is not tested.",
      f"Overlap does not explain the math gain: Code 3.0 overlaps Math 3.1 at {f3(R['math31']['code30'])} and scores 411 of 500 on MATH-500 with the "
      "opening cue, against 410 for the untrained base model.",
      "It is one base model, one lab's seven releases and one choice of 8 directions. Two releases of a reward may share more than the reward, "
      "such as data and settings, and that is not separated here."]],
    ["run", "How to reproduce it", "One GPU job per table reads the released weights and writes every pairwise overlap. The readout runs on a laptop.",
     [f"Final models: job {DATA['job']}, numbers in {DATA['artifact']} (branch {DATA['branch']}, commit {DATA['commit']}).",
      f"Step 100: job {DATA['job_steps']}, numbers in {DATA['artifact_steps']}.",
      "Code: studies/rlneurons/jobs/xreward_overlap.py (with --steps for the step-100 checkpoints) and studies/rlneurons/analysis/xreward_overlap.py. "
      "The plan written before the runs is studies/rlneurons/specs/SPEC_xreward.md."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with one line per pair of models whose overlap is above 0.15, as wide as the overlap; the
# pairs above 0.35 (the two releases of Math and of Code, and Mix with Instructions) are lit.
ICON = r"""(kit, t, tilt) => {
  const a = 46, b = 36, th = 5, top = th / 2 + 1;
  return kit.slab(a, b, th) + __LINES__.map(([u, v, x, y, o], i) =>
    kit.line(kit.at(u, v, top), kit.at(x, y, top), 1 + 7 * o + (o > .35 ? .2 * Math.sin(t * .6 + i) : 0), o > .35 ? "lit" : "plain", o > .35 ? 1 : .8)).join("");
}""".replace("__LINES__", json.dumps([[round(p["u"] * .14, 1), round(p["v"] * .14, 1), round(q["u"] * .14, 1), round(q["v"] * .14, 1), round(R[p["key"]][q["key"]], 3)]
                                      for i, p in enumerate(DATA["models"]) for q in DATA["models"][i + 1:] if R[p["key"]][q["key"]] > .15]))

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
   --wash is how strongly the picked block takes the accent. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --wash: .3;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
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
svg { width: 100%; max-height: 62vh; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 104%; }
.atmo, .shade { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.body { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; stroke-linejoin: round; }
.face { fill: url(#body) var(--sheet); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1.4; stroke-linejoin: round; }
.wash { fill: var(--blue); opacity: 0; pointer-events: none; transition: opacity .3s ease; }
.on .wash { opacity: var(--wash); }
.link { stroke: var(--ink); stroke-linecap: round; transition: opacity .3s ease, stroke .3s ease; }
.picked .link { opacity: .07; }
.picked .link.mine { stroke: var(--blue); opacity: 1; }
.model { cursor: pointer; outline: none; }  /* its focus ring is the rim of its block */
.model:focus-visible .rim { stroke: var(--blue); stroke-width: 3; }
.hit { fill: transparent; }
.label { font-weight: 600; text-anchor: middle; paint-order: stroke; stroke: var(--paper); stroke-width: 5px; stroke-linejoin: round; }
.num { font-weight: 620; text-anchor: middle; }
.key { fill: var(--mute); font-weight: 500; }
.keyline { stroke: var(--ink); stroke-linecap: round; opacity: .7; }
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
/* A picked model: its numbers, largest first, as bars; the three reference levels are fainter */
.bars li { padding: 5px 0; display: grid; grid-template-columns: 9.5em minmax(0, 1fr) 3.2em; gap: 10px; align-items: center; color: var(--ink); }
.bars i { height: 6px; min-width: 1px; border-radius: 3px; background: var(--ink); }
.bars b { font-weight: 560; text-align: right; }
.bars .ref { color: var(--mute); }
.bars .ref i { background: var(--faint); }
.bars .ref b { font-weight: 400; }
.grid { width: 100%; border-collapse: collapse; font-size: 12px; color: var(--mute); }
.grid th { font-weight: 600; color: var(--ink); }
.grid th, .grid td { padding: 3px 0; text-align: right; }
.grid .hi { color: var(--ink); font-weight: 600; }
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
  .switch button { padding: 8px 9px; font-size: 13px; }
  .note { min-height: 6em; }
}
@media (prefers-reduced-motion: reduce) {
  svg { animation: none; }
  .switch button, .more button, .wash, .link { transition: none; }
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
    <svg id="svg" viewBox="0 0 760 500" role="group"></svg>
    <div class="switch" id="switch" role="group" aria-label="What the lines show"></div>
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
const M = Object.fromEntries(D.models.map(m => [m.key, m]));
const S = { state: 0, open: null, pick: null, grow: 0, links: [], nodes: [] };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const f = n => n.toFixed(1), ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
const f3 = n => (Math.abs(n) < .0005 ? 0 : n).toFixed(3).replace("-", "−");

/* The numbers. A line between two models shows, by the switch: the cosine of their whole weight changes, the overlap of
   their top-8 input subspaces, or the overlap of one run's step-100 checkpoint with the other run's final model (the
   mean of the two directions, or the picked model's own checkpoint when a model is picked). */
const TABLE = [D.cos, D.right, D.step100];
function value(a, b) {
  if (S.state < 2) return Math.max(0, TABLE[S.state][a][b]);
  if (S.pick === a) return D.step100[a][b];
  if (S.pick === b) return D.step100[b][a];
  return (D.step100[a][b] + D.step100[b][a]) / 2;
}

/* The picture: seven glass blocks on a glass board seen from slightly above, one per model, joined by lines on the
   board. A line is WIDE units wide per unit of overlap, so an overlap at the random level is too thin to see. */
const RAD = Math.PI / 180, CX = 380, CY = 232, EL = 52, HALF = 36, TALL = 12, WIDE = 46, EDGE = [335, 178];
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
const rect = (u, v, a, b, w) => [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => proj(u + i * a, v + j * b, w));

function build() {
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  D.models.forEach((p, i) => D.models.slice(i + 1).forEach(q => S.links.push({ id: `l-${p.key}-${q.key}`, a: p, b: q, w: 0 })));
  S.nodes = [...D.models].sort((p, q) => q.v - p.v).map(m => ({ m }));  // the far blocks first, so that a near one hides a far one
  $("svg").innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.3, "var(--blue)", .2)}${stop(.7, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient></defs>` +
    `<g class="atmo"><ellipse cx="${CX}" cy="${CY - 10}" rx="440" ry="270" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${CX + 22}" cy="${CY + 44}" rx="410" ry="230" fill="url(#shade)"/></g>` +
    `<path class="body" id="board-side"/><path class="face" id="board-face"/><path class="rim" id="board-rim"/>` +
    `<g id="links">${S.links.map(l => `<path class="link" id="${l.id}" fill="none"/>`).join("")}</g>` +
    S.nodes.map(({ m }) => `<g class="model" id="m-${m.key}" data-pick="${m.key}" role="button" tabindex="0" aria-label="${m.name}">` +
      `<path class="body" id="b-${m.key}"/><path class="face" id="f-${m.key}"/><path class="wash" id="w-${m.key}"/><path class="rim" id="r-${m.key}"/>` +
      `<text class="num" id="n-${m.key}"></text><text class="label" id="t-${m.key}">${m.label || m.name}</text><circle class="hit" id="h-${m.key}" r="52"/></g>`).join("") +
    `<g id="key"></g>`;
  S.links.forEach(l => { l.el = $(l.id); });
  S.nodes.forEach(o => { o.el = Object.fromEntries(["m", "b", "f", "w", "r", "n", "t", "h"].map(k => [k, $(`${k}-${o.m.key}`)])); });
}
function place() {
  const top = rect(0, 0, EDGE[0], EDGE[1], 0), d = path(top);
  $("board-side").setAttribute("d", path(hull([...top, ...rect(0, 0, EDGE[0], EDGE[1], -12)])));
  $("board-face").setAttribute("d", d); $("board-rim").setAttribute("d", d);
  S.links.forEach(l => {
    const p = proj(l.a.u, l.a.v, 0), q = proj(l.b.u, l.b.v, 0);
    l.el.setAttribute("d", `M${f(p[0])} ${f(p[1])}L${f(q[0])} ${f(q[1])}`);
    l.el.setAttribute("stroke-width", (WIDE * l.w * S.grow * (p[2] + q[2]) / 2).toFixed(2));
    l.el.setAttribute("stroke-opacity", Math.min(.95, .3 + 1.5 * l.w).toFixed(2));  // a wide line is also brighter
  });
  S.nodes.forEach(({ m, el }) => {
    const h = TALL * S.grow, up = rect(m.u, m.v, HALF, HALF, h), face = path(up), c = proj(m.u, m.v, h), back = proj(m.u, m.v + HALF, h);
    el.b.setAttribute("d", path(hull([...up, ...rect(m.u, m.v, HALF, HALF, 0)])));
    el.f.setAttribute("d", face); el.w.setAttribute("d", face); el.r.setAttribute("d", face);
    el.n.setAttribute("x", f(c[0])); el.n.setAttribute("y", f(c[1] + 7 * c[2])); el.n.setAttribute("font-size", f(21 * c[2]));
    el.t.setAttribute("x", f(c[0])); el.t.setAttribute("y", f(back[1] - 10)); el.t.setAttribute("font-size", f(25 * c[2]));
    el.h.setAttribute("cx", f(c[0])); el.h.setAttribute("cy", f(c[1] - 8));
  });
}
/* One frame: the view sways slowly and leans toward the pointer, the blocks and the lines rise once on load, and every
   line moves toward the width of its current number. With reduced motion the page shows one still frame. */
function frame(now) {
  const t = now / 1000;
  V.px += (V.tx - V.px) * .06; V.py += (V.ty - V.py) * .06;
  V.yaw = 2 * Math.sin(t * .25) + 2.5 * V.px; V.el = EL + Math.sin(t * .19 + 1) - 2 * V.py;
  S.grow = ease(Math.min(1, t / 1.3));
  S.links.forEach(l => { l.w += (value(l.a.key, l.b.key) - l.w) * .1; });
  place();
  if (!still.matches) requestAnimationFrame(frame);
}
function draw() {  // the switch, the note, the picked model and its numbers follow the state; the lines follow in frame()
  const st = D.states[S.state], row = S.pick && TABLE[S.state][S.pick];
  $("svg").setAttribute("aria-label", `${st.name}. ` + D.models.map(m => `${m.name}: nearest ${M[(S.state === 2 ? D.nearest_step100 : D.nearest)[m.key]].name}`).join("; "));
  $("note").textContent = st.note;
  $("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}" aria-pressed="${i === S.state}">${s.name}</button>`).join("");
  $("key").innerHTML = D.key[S.state].map(([v, name], i) => { const x = [56, 316, 530][i]; return `<path class="keyline" d="M${x} 462h44" stroke-width="${f(Math.max(.6, WIDE * v))}"/>` +
    `<text class="key" x="${x + 68}" y="469" font-size="20">${f3(v)} ${name}</text>`; }).join("");
  $("svg").classList.toggle("picked", !!S.pick);
  S.links.forEach(l => l.el.classList.toggle("mine", l.a.key === S.pick || l.b.key === S.pick));
  S.nodes.forEach(({ m, el }) => {
    el.m.classList.toggle("on", m.key === S.pick); el.m.setAttribute("aria-pressed", m.key === S.pick);
    el.n.textContent = row && m.key !== S.pick ? f3(row[m.key]) : "";
  });
  if (still.matches) { S.grow = 1; S.links.forEach(l => { l.w = value(l.a.key, l.b.key); }); place(); }
  pane();
}
function choose(i) {
  if (i === S.state) return;
  S.state = i;
  draw();
}
function picked() {  // the side column of a picked model: its numbers by the switch, largest first, with the reference levels
  const m = M[S.pick], row = TABLE[S.state][S.pick];
  const rows = [...D.models.filter(o => o.key !== S.pick).map(o => [o.name, row[o.key], 0]), ["Think-SFT, no RL", row.think_sft, 1], ["Base matrix", row.base_w, 1]];
  if (S.state) rows.push(["Random pair", D.random, 1]);
  rows.sort((a, b) => b[1] - a[1]);
  const best = rows.find(r => !r[2]);
  const lead = [`The whole weight change of ${m.name} has its largest cosine with ${best[0]}, ${f3(best[1])}.`,
    `The nearest model to ${m.name} is ${best[0]}, with an overlap of ${f3(best[1])}.`,
    `After 100 RL steps, the nearest final model of another run is ${best[0]}, with an overlap of ${f3(best[1])}.`][S.state];
  return `<div class="dhead"><h2>${m.name}</h2><button class="close" data-open="">Close</button></div><p class="lead">${lead}</p>` +
    `<ul class="facts bars">${rows.map(([name, v, ref]) => `<li${ref ? ' class="ref"' : ""}><span>${name}</span>` +
      `<i style="width:${f(Math.min(100, Math.max(0, 200 * v)))}%"></i><b>${f3(v)}</b></li>`).join("")}<li>${m.repo}</li></ul>`;
}
function grid() {  // the whole table of the top-8 overlaps of the final models
  const short = v => v.toFixed(3).slice(1);
  return `<table class="grid"><tr><td></td>${D.models.map(m => `<th>${m.short}</th>`).join("")}</tr>` + D.models.map(a => `<tr><th>${a.short}</th>` +
    D.models.map(b => a === b ? "<td></td>" : `<td${D.nearest[a.key] === b.key ? ' class="hi"' : ""}>${short(D.right[a.key][b.key])}</td>`).join("") + "</tr>").join("") + "</table>";
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = S.pick ? picked() : p
    ? `<div class="dhead"><h2>${p[1]}</h2><button class="close" data-open="">Close</button></div><p class="lead">${p[2]}</p>` +
      `<ul class="facts">${p[3].map(f => `<li>${f === "table" ? grid() : f}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${p[1]}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
/* The address holds the one thing that is open: a panel (#how) or a picked model (#math31). */
function go(h) { history.pushState(null, "", h ? "#" + h : location.pathname); fromHash(); }
function fromHash() {
  const h = location.hash.slice(1);
  S.open = C.panels.some(p => p[0] === h) ? h : null; S.pick = M[h] ? h : null;
  draw();
}
document.addEventListener("click", e => {
  const s = e.target.closest("[data-state]"), o = e.target.closest("[data-open]"), m = e.target.closest("[data-pick]");
  if (s) { choose(Number(s.dataset.state)); document.querySelector(`[data-state="${S.state}"]`).focus(); }
  if (o) go(o.dataset.open);
  if (m) go(m.dataset.pick === S.pick ? "" : m.dataset.pick);
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const m = e.target.closest && e.target.closest("[data-pick]");
  if (m && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); go(m.dataset.pick === S.pick ? "" : m.dataset.pick); }
  if (e.key === "Escape" && (S.open || S.pick)) go("");
  if (e.key === "ArrowRight") choose((S.state + 1) % D.states.length);
  if (e.key === "ArrowLeft") choose((S.state + D.states.length - 1) % D.states.length);
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
fromHash();
if (!still.matches) requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}))
