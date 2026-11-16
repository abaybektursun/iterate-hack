"""No label-free text sign tells a failing Think-SFT sample from a right one of the same problem early: best AUROC 0.568.

The page of one finding, served at /finding/no-early-warning (view.py serves every tools/finding_<slug>.py) and reached
from its tile on /findings, which ICON draws. A negative result, told as plainly as a positive one.

The picture is one lit plate holding an AUROC scale from 0.3 to 1.0 (0.5 = a coin toss, 1.0 = perfect) with one row
per text sign: its AUROC for "this sample will not end right" and the 95 % interval. The readout stores per-sign
summaries, not per-sample sign values, so the rows are exactly what predict-01/readout.json stores: six signs at three
reading points, for two kinds of pairs. A seventh row is the planted sign of the instrument check (0.807), the place a
working sign lands. The reader's one control is the reading point (token 4,000 / 8,000 / 12,000); a second, quieter
switch changes the pairs from two samples of one problem to samples of any problems, where the repetition sign reaches
0.65 because it marks hard problems. Marks travel to their new values and the large number (the best of the six) counts
with them. In the corner, the consequence: stopping a sample at its sign saves 0.8 % of tokens on the 328 harder
problems, against a goal of 10 % and 47.3 % for a perfect sign. A click on a row shows that sign in the side column with
two real samples from predict-01/examples.json (the highest sign among samples that ended right and among those that did
not), with the text where the sign is read. Address: /finding/no-early-warning#<4000|8000|12000>/<any>/<sign>/<panel>.
The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md). Study: studies/rlneurons, README section "Drift"; board result-997be4.

    uv run tools/finding_no_early_warning.py    checks DATA against the artifacts it was copied from
"""
import json

RUN = "studies/rlneurons/results/drift/"

# Every number is copied from the run folders below; none is typed from memory. The deployed site ships only tools/*.py,
# so the copy is a literal; run this file to compare it with the artifacts.
DATA = {
    "commit": "96c3710",  # the commit that added the run folders to main
    "code_commit": "1dd9cb7",  # run.json commit: analysis/drift_read.py
    "spec_commit": "9045c7c",  # SPEC_drift.md, written before the numbers
    "command": "python -m studies.rlneurons.analysis.drift_read --features runs/drift_features --runs runs "
               "--out studies/rlneurons/results/drift --nn 01",
    # predict-01/readout.json, q3["Think-SFT, pooled"] (328 harder problems and 136 problems of 2026, 4 samples each):
    # per reading point t, the samples still running and how many of them do not end right; per sign the AUROC for
    # "does not end right" with its 95 % interval, "same" = running_within_problem, "any" = running_pooled; the pairs.
    "auroc": {
        "4000": {"running": 1600, "running_not_right": 774, "pairs_same": 348, "problems_same": 106, "pairs_any": 639324, "signs": {
            "switch": {"same": [0.499, 0.495, 0.5], "any": [0.503, 0.498, 0.508]},
            "rep50": {"same": [0.5, 0.487, 0.515], "any": [0.494, 0.485, 0.502]},
            "loopA": {"same": [0.5, 0.5, 0.5], "any": [0.499, 0.498, 0.5]},
            "zratio": {"same": [0.509, 0.44, 0.579], "any": [0.649, 0.606, 0.691]},
            "wait": {"same": [0.453, 0.391, 0.52], "any": [0.505, 0.465, 0.545]},
            "restart": {"same": [0.466, 0.414, 0.517], "any": [0.515, 0.49, 0.541]}}},
        "8000": {"running": 1229, "running_not_right": 761, "pairs_same": 315, "problems_same": 100, "pairs_any": 356148, "signs": {
            "switch": {"same": [0.492, 0.48, 0.502], "any": [0.509, 0.501, 0.517]},
            "rep50": {"same": [0.486, 0.463, 0.508], "any": [0.491, 0.477, 0.503]},
            "loopA": {"same": [0.503, 0.5, 0.511], "any": [0.498, 0.493, 0.503]},
            "zratio": {"same": [0.53, 0.458, 0.606], "any": [0.636, 0.588, 0.682]},
            "wait": {"same": [0.5, 0.431, 0.57], "any": [0.44, 0.394, 0.487]},
            "restart": {"same": [0.478, 0.415, 0.539], "any": [0.527, 0.489, 0.563]}}},
        "12000": {"running": 922, "running_not_right": 710, "pairs_same": 213, "problems_same": 77, "pairs_any": 150520, "signs": {
            "switch": {"same": [0.498, 0.474, 0.521], "any": [0.516, 0.496, 0.534]},
            "rep50": {"same": [0.477, 0.451, 0.5], "any": [0.478, 0.454, 0.5]},
            "loopA": {"same": [0.502, 0.5, 0.508], "any": [0.496, 0.487, 0.504]},
            "zratio": {"same": [0.568, 0.48, 0.657], "any": [0.623, 0.567, 0.677]},
            "wait": {"same": [0.462, 0.378, 0.546], "any": [0.409, 0.351, 0.468]},
            "restart": {"same": [0.535, 0.46, 0.611], "any": [0.536, 0.488, 0.584]}}},
    },
    "samples": 1856, "not_right": 780,
    # predict-01/readout.json, planted_sign_within_problem_auroc: a flag on 80 % of not-right and 20 % of right samples.
    "planted": {"auroc": [0.807, 0.766, 0.846], "pairs": 368, "problems": 112},
    # predict-01/readout.json, q3 controls: the best within-problem value of any sign at any t.
    "control_rl": {"sign": "zratio", "t": "12000", "auroc": [0.643, 0.539, 0.744], "pairs": 129},
    "control_base": {"sign": "wait", "t": "8000", "auroc": [0.548, 0.456, 0.636], "pairs": 198},
    # stop-01/readout.json, sets.hard328 (n = 328): the sequential vote with no stop, the chosen stop rule (rep50_p75),
    # the perfect sign at 4,000 (oracle4000, uses the answer key), stopping at high repetition (zratio_p75) and seq3.
    "stop": {"chosen": "rep50_p75", "n": 328,
             "plain": {"right": 241, "right24": 238.9, "tokens": 30837},
             "rule": {"right": 240, "right24": 238.4, "tokens": 30602, "ratio": [0.992, 0.982, 1.003], "stopped": 70},
             "perfect": {"right": 244, "tokens": 16250, "ratio": 0.527},
             "zratio_p75": {"right24": 226.1, "tokens": 25671}, "seq3": {"right24": 233.2, "tokens": 26114},
             "fresh_ratio": 0.989},
    # describe-01/readout.json, cells: Think-SFT + cue on the 328 harder problems, RL and Base + cue on the same
    # problems, Think-SFT + cue on the 136 problems of 2026 (cap hits only).
    "switch": {"samples": 1312, "with": 156, "right": 39, "rl": 12, "base": 9, "cjk": 40579, "letters": 41289,
               "quartiles": [10733, 13589, 15048], "before_4000": 16, "back": 135, "problems": 102},
    "cap": {"hard328": [378, 1312], "fresh2026": [248, 544]},
    # predict-01/readout.json, cap32: Think-SFT + cue with a 32,768 cap, one sample, answers longer than 16,384 tokens.
    "cap32": {"switched": 24, "switched_right": 1, "others": 69, "others_right": 22},
    # predict-01/examples.json (hard328 Think-SFT + cue, run at T 1.0): per sign the sample still running at 8,000 with
    # the highest sign that ended right and the one that did not (switch, loopA: the first flagged by 12,000). before:
    # the last 230 of the 300 stored characters before the token where the sign is read; after: the 100 after it.
    "examples": {
        "switch": {
            "right": {"problem": "AIME 2024 I, problem 3", "uid": "aime2024/2024_AIME_I_Problems/Problem_3", "sample": 0, "n_new": 13482, "cap": False, "score": 1, "answer": "809", "at": 5682, "value": 1.0, "before": "ave opponent in True. So f(5)=False.\n\nn=5: False\n\nn=6:\n\nTake1 →5 (False). Therefore, current player can choose that move. Therefore, f(6)=True.\n\nTake4 →2 (False, opponent is at n=2 which is False (Losing), so player can takesПрест", "after": "а, then the opponent can't win. Therefore, yes, this is a winning move. So f(6)=True.\n\nn=6:True.\n\nn="},
            "wrong": {"problem": "AIME 2024 I, problem 12", "uid": "aime2024/2024_AIME_I_Problems/Problem_12", "sample": 3, "n_new": 16384, "cap": True, "score": 0, "answer": None, "at": 3437, "value": 1.0, "before": " -1 and 1, so we can again exploit evenness.\n\nLet me consider w ≥0 first:\n\nCase 1: w in [0,1]\n\nThen, |w| = w.\n\nSo f(w)= ||w - 1/2|.\n\nThus, when w ≥1/2: ||w -1/2| is w -1/2\n\nWhen w ≤1/2: |w -1/2| is 1/2 - w.\n\nTherefore:\n\n过渡点在w=1/2时", "after": "，f(w)为0。\n\nAt w =1: f(1)= ||1 -0.5|=0.5\n\nAt w=0.5: 0, as before.\n\nAt w=0: |0 - 0.5|=0.5.\n\nSame for ne"},
        },
        "loopA": {
            "right": {"problem": "AIME 2025, problem 6", "uid": "aime2025/6", "sample": 2, "n_new": 13458, "cap": False, "score": 1, "answer": "504", "at": 5549, "value": 1.0, "before": "out quotes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form", "after": " Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer"},
            "wrong": {"problem": "OlympiadBench, problem 2598", "uid": "olympiadbench/2598", "sample": 0, "n_new": 16384, "cap": True, "score": 0, "answer": "$Answer (without quotes) where $Answer is", "at": 5793, "value": 1.0, "before": "tes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer", "after": ": $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (witho"},
        },
        "rep50": {
            "right": {"problem": "OlympiadBench, problem 2596", "uid": "olympiadbench/2596", "sample": 2, "n_new": 12154, "cap": False, "score": 1, "answer": "(4, \\log_{10} 2)", "at": 8000, "value": 0.7788, "before": "o the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $", "after": "Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the an"},
            "wrong": {"problem": "OlympiadBench, problem 2842", "uid": "olympiadbench/2842", "sample": 3, "n_new": 16384, "cap": True, "score": 0, "answer": "$Answer (without quotes) where", "at": 8000, "value": 0.6373, "before": "tes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer", "after": ": $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (witho"},
        },
        "zratio": {
            "right": {"problem": "OlympiadBench, problem 2596", "uid": "olympiadbench/2596", "sample": 2, "n_new": 12154, "cap": False, "score": 1, "answer": "(4, \\log_{10} 2)", "at": 8000, "value": -0.0729, "before": "o the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $", "after": "Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the an"},
            "wrong": {"problem": "OlympiadBench, problem 2842", "uid": "olympiadbench/2842", "sample": 3, "n_new": 16384, "cap": True, "score": 0, "answer": "$Answer (without quotes) where", "at": 8000, "value": -0.1099, "before": "tes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem in form Answer", "after": ": $Answer (without quotes) where $Answer is the answer to the problem in form Answer: $Answer (witho"},
        },
        "wait": {
            "right": {"problem": "OlympiadBench, problem 2846", "uid": "olympiadbench/2846", "sample": 2, "n_new": 9194, "cap": False, "score": 1, "answer": "79", "at": 8000, "value": 17.0, "before": "79.\n\nWait to ensure correctness, let's verify:\n\nN=79:\n\nReverse is 97, which is prime. Good.\n\n4×79= 316. Reverse digits: 613 (prime). \n\n5×79=395 → reverse digits 593 (prime). \n\nYes, so all three conditions are satisfied. So N=79.\n\n", "after": "Is there any higher N? Let me check N=97:\n\nEarlier found that the reverse of 97 is 79 (no, reversed "},
            "wrong": {"problem": "OlympiadBench, problem 2844", "uid": "olympiadbench/2844", "sample": 0, "n_new": 15105, "cap": False, "score": 0, "answer": "2019.", "at": 8000, "value": 16.5, "before": "pril1 2016 would be Thursday.\n\nWait but from previous April: April1 2015 was Wednesday, and adding 365 (normal shift):\n\nWednesday (3) +365 mod7=1 → Thursday (3+1=4, which is Thursday, which matches. Because April1 2016 is Thursday", "after": ". \n\nOkay, so April1 2016 is Thursday.\n\nProceeding:\n\n2016: April1 is Thursday. Which is five years fr"},
        },
        "restart": {
            "right": {"problem": "AIME 2025, problem 5", "uid": "aime2025/5", "sample": 0, "n_new": 15425, "cap": False, "score": 1, "answer": "279", "at": 8000, "value": 0.75, "before": "ith 7,6,5:\n\nThree numbers sum to 7+6+5=18?\n\nWait 7+6+5=18, but need a fourth number to make four elements. Wait, but if I take 18 total sum? Wait no, need four numbers to add to 18.\n\nWait, so 7 +6 +5 + what? 0? Not possible. Maybe", "after": " instead:\n\nLet me think step by step.\n\nLet me attempt starting with 7 as the largest number.\n\nTake 7"},
            "wrong": {"problem": "AIME 2025, problem 30", "uid": "aime2025/30", "sample": 1, "n_new": 16384, "cap": True, "score": 0, "answer": "72", "at": 8000, "value": 0.875, "before": " each pair's midpoints should be same.\n\nThus for four points a, b, c, d to be symmetric wrt center m, (a + d)/2 = (b +c)/2 = m.\n\nSo to form a symmetric quadruple, we can choose pairs from the existing three roots.\n\nSuppose that we", "after": " take one root as a, and then form symmetric pairs. Given the three existing roots at 18,72,98, to f"},
        },
    },
    # describe-01/hand_read.md, item 6 (hard328 problem 267, sample 2): a quote at the first switch and the agent's
    # translation; examples.json holds the text.
    "quote": {"problem": "hard328 267, s2", "at": 15565, "text": "Wait，我先重新看一下方程的推导.",
              "translation": "Wait, let me first look at the derivation of the equation again."},
}

# The rows, top to bottom: key, name, second line, and the plain definition for the side column.
SIGNS = [
    ["switch", "Switches script", "to Chinese, Russian, …",
     "The answer has switched to a non-Latin script by the reading point: at least 5 letters of Chinese, Russian, Arabic or "
     "another script within 200 characters. Greek is not counted, because mathematics uses it."],
    ["loopA", "Loop detector", "a long window repeats",
     "The loop rule of the team's sampler has fired: an 8,000-character window of the answer compresses to under a tenth of "
     "its size."],
    ["rep50", "Repeats a passage", "50 tokens seen before",
     "The share of the answer's 50-token windows that repeat an earlier window exactly."],
    ["zratio", "Compresses well", "repetitive text, by zlib",
     "How well the answer so far compresses with zlib. More repetitive text compresses better and gets a higher sign."],
    ["wait", "Says “wait”", "per 1,000 tokens",
     "How often the answer says “wait”, per 1,000 tokens."],
    ["restart", "Starts over", "“another approach”, per 1,000",
     "How often the answer uses one of 20 phrases of starting over, such as “let me start over” or “try a different "
     "approach”, per 1,000 tokens."],
]
PLANTED = ["planted", "Planted sign", "made up, known to work",
           "A made-up sign, set at random on 80 % of the failing samples and 20 % of the right ones. A test that could not "
           "find it would be broken; this one scores it 0.807."]

_A, _S, _W = DATA["auroc"], DATA["stop"], DATA["switch"]
_t = lambda k: f"{int(k):,}"
_f3 = lambda x: f"{x:.3f}"
_iv = lambda a: f"95 % interval {_f3(a[1])} to {_f3(a[2])}"
_pc = lambda x: f"{x:.1f} %".replace("-", "−")
_saved = [100 * (1 - x) for x in _S["rule"]["ratio"]]  # tokens saved by the chosen rule, and its interval (reversed)
_best = max(((v["signs"][s]["same"][0], s, t) for t, v in _A.items() for s in v["signs"]))
_B = _A[_best[2]]["signs"][_best[1]]["same"]
_name = {s[0]: s[1] for s in SIGNS}
_cut = {k: 100 * a / b for k, (a, b) in DATA["cap"].items()}

TITLE = "No early warning"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Can the text of a long answer show early that it will fail?"
LINE = (f"None of six signs read from the text of the imitation-trained model's (Think-SFT's) answers, at tokens 4,000 to "
        f"12,000, tells early which samples will fail: the best ranks failing samples above passing ones with an AUROC of "
        f"{_f3(_B[0])}, where 0.5 is chance and 1.0 is perfect.")

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences.
PANELS = [
    ["new", "What is new",
     "Here six text signs are read deep into Think-SFT's answers, at tokens 4,000 to 12,000. Two earlier detectors of a "
     "failing sample read only the first 1,000 tokens of Base + cue on MATH-500 and scored AUROC 0.531 and 0.571, the second "
     "with a linear probe (sources: board results f3d708 and b30f15).",
     [f"{_W['with']} of {_W['samples']:,} Think-SFT samples on the 328 harder problems switch to another script mid-answer, "
      f"and {_pc(100 * _W['cjk'] / _W['letters'])} of those letters are Chinese. RL does so in {_W['rl']} of {_W['samples']:,}, "
      f"Base + cue in {_W['base']}. The median first switch is at token {_W['quartiles'][1]:,}.",
      "A study of language mixing (arXiv 2507.15849, Section 2.3 and Table 1) finds QwQ-32B-preview mixing languages in "
      "0.6 % of its MATH-500 answers to English prompts, and that forcing one language lowers accuracy (Section 3.2). It "
      "does not test whether a switch predicts that a sample fails.",
      "A stop rule that reads the model's confidence in its intermediate answers saves 25 to 50 % of tokens (arXiv "
      f"2604.04930, abstract). Signs read from the text alone saved {_pc(_saved[0])} here."]],
    ["why", "Why it matters",
     f"Think-SFT + cue is cut off at 16,384 tokens in {_pc(_cut['hard328'])} of its samples on the 328 harder problems "
     f"and {_pc(_cut['fresh2026'])} on 136 problems of 2026. A cut-off sample casts no vote, so a sign that spotted it "
     "early would save its tokens.",
     [f"A perfect sign at token 4,000 would give {_S['perfect']['right']} of 328 right at {_S['perfect']['tokens']:,} "
      f"tokens per problem, against {_S['plain']['right']} of 328 at {_S['plain']['tokens']:,} for the sequential vote with "
      "no stop.",
      f"The stop rule chosen on MATH-500 (stop when a 50-token passage repeats) gives {_S['rule']['right']} of 328 at "
      f"{_S['rule']['tokens']:,} tokens: {_pc(_saved[0])} fewer (95 % interval {_pc(_saved[2])} to {_pc(_saved[1])}), not "
      "the 10 % the spec asked for.",
      f"At equal tokens the signs lose to drawing fewer samples: stopping at high repetition gives "
      f"{_S['zratio_p75']['right24']} of 328 at {_S['zratio_p75']['tokens']:,} tokens, at most 3 samples gives "
      f"{_S['seq3']['right24']} at {_S['seq3']['tokens']:,} (means over 24 draw orders)."]],
    ["how", "How we know",
     f"Six signs were computed from the stored texts of {DATA['samples']:,} Think-SFT + cue samples (328 harder problems and "
     "136 problems of 2026, 4 samples each, T 1.0) on a laptop, with no model run.",
     ["Same problem: over pairs of one failing and one right sample of one problem, both still running at the reading point, "
      "the AUROC is the share of pairs in which the failing one has the higher sign, ties counted half. Intervals: 5,000 "
      "bootstrap resamples over problems.",
      f"The test can find a real sign: the planted sign scores {_f3(DATA['planted']['auroc'][0])} "
      f"({_iv(DATA['planted']['auroc'])}, {DATA['planted']['pairs']} pairs).",
      "The prediction, written in the spec before any of these numbers: no sign reaches 0.60 within a problem. It held. "
      f"The same test on Base + cue tops out at {_f3(DATA['control_base']['auroc'][0])}."]],
    ["limits", "What it does not show",
     "It does not show that a failing answer cannot be spotted early, only that these six counts of scripts, repeats and "
     "words cannot. Signs read from the model's probabilities or activations were not tested here.",
     ["Across problems the signs do carry information: repetitive text scores 0.62 to 0.65 over pairs from any problems. "
      "That marks a hard problem, not a failing sample.",
      f"Late, the switch does go with failure: in a run to 32,768 tokens, {DATA['cap32']['switched_right']} of "
      f"{DATA['cap32']['switched']} answers that had switched before token 16,384 end right, against "
      f"{DATA['cap32']['others_right']} of {DATA['cap32']['others']} that had not. One sample per problem, not matched.",
      f"For RL the repetition sign at token 12,000 reaches {_f3(DATA['control_rl']['auroc'][0])} "
      f"({_iv(DATA['control_rl']['auroc'])}, {DATA['control_rl']['pairs']} pairs), the only interval above 0.5 among the 54 "
      "tests on Think-SFT, RL and Base + cue. Only 20 to 70 Think-SFT samples have switched by each reading point."]],
    ["run", "How to reproduce it",
     f"Run {DATA['command']} at commit {DATA['code_commit']}; it reads the stored texts and the sign cache.",
     [f"The run folders {RUN}describe-01, predict-01 and stop-01 hold readout.json, table.md, examples.json and run.json.",
      f"The spec, studies/rlneurons/specs/SPEC_drift.md, was committed at {DATA['spec_commit']} before the numbers. The "
      "README of studies/rlneurons, section “Drift”, lists every input."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's picture, reduced.
# A glass slab with the lit 0.5 line, six intervals that drift slowly between the three reading points and stay on it,
# and the planted sign far to the right as a ring.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, w = th / 2, X = v => a * (-.86 + 1.72 * (v - .3) / .7);
  const D = __ICONDATA__, k = (Number(t) || 0) * .22, i = Math.floor(k) % 3, j = (i + 1) % 3, q = .5 - .5 * Math.cos(Math.PI * (k % 1));
  let out = kit.slab(a, b, th);
  out += kit.line(kit.at(X(.5), -b * .78, w), kit.at(X(.5), b * .66, w), .9, "lit", .9);
  out += kit.line(kit.at(X(1), -b * .78, w), kit.at(X(1), b * .66, w), .5, "plain", .6);
  D.forEach((r, n) => {
    const v = -b * .62 + n * b * .19, m = r[i].map((x, c) => x + (r[j][c] - x) * q);
    if (m[2] - m[1] > .004) out += kit.line(kit.at(X(m[1]), v, w), kit.at(X(m[2]), v, w), .7, "plain", .9);
    const p = kit.at(X(m[0]), v, w);
    out += `<ellipse cx="${p[0].toFixed(2)}" cy="${p[1].toFixed(2)}" rx="${(2.1 * p[2]).toFixed(2)}" ry="${(1.6 * p[2]).toFixed(2)}" fill="${n === 3 ? kit.token.blue : kit.token.ink}" opacity="${n === 3 ? 1 : .8}"/>`;
  });
  const p = kit.at(X(.807), b * .58, w);
  out += `<ellipse cx="${p[0].toFixed(2)}" cy="${p[1].toFixed(2)}" rx="${(2.4 * p[2]).toFixed(2)}" ry="${(1.8 * p[2]).toFixed(2)}" fill="none" stroke="${kit.token.ink}" stroke-width=".9"/>`;
  return out;
}""".replace("__ICONDATA__", json.dumps([[_A[t]["signs"][s[0]]["same"] for t in ("4000", "8000", "12000")] for s in SIGNS]))

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
   with a cast shadow in place of the glow. The light comes from the upper left in both. Blue marks the best sign of the
   state shown; the planted sign is a hollow ring. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --band: .05; --quote: #f1f3f5;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --band: .07; --quote: #0d141b;
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

/* The picture: one plate holding the readout and the AUROC scale, and the controls under it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg { width: 100%; max-height: calc(100vh - 280px); display: block; overflow: visible; touch-action: pan-y; user-select: none; -webkit-user-select: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
svg .hit { pointer-events: all; fill: var(--ink); fill-opacity: 0; stroke: none; cursor: pointer; outline: none; }
svg .hit:hover { fill-opacity: .035; }
svg .hit:focus-visible { stroke: var(--blue); stroke-width: 1.5; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.band { fill: var(--blue); opacity: var(--band); }
.coin { stroke: var(--ink); stroke-width: 1.6; opacity: .62; }
.perfect { stroke: var(--ink); stroke-width: 1.2; opacity: .3; }
.grid { stroke: var(--ink); stroke-width: 1; opacity: .07; fill: none; }
.sep { stroke: var(--ink); stroke-width: 1; opacity: .12; stroke-dasharray: 2 4; }
.tick { fill: var(--mute); font-weight: 500; }
.atitle { fill: var(--mute); font-weight: 520; }
.rlab { font-weight: 640; }
.rsub { fill: var(--mute); font-weight: 480; }
.rname { font-weight: 600; }
.rsec { fill: var(--mute); font-weight: 460; }
.iv { stroke: var(--ink); stroke-width: 2; stroke-linecap: round; opacity: .5; fill: none; }
.pt { fill: var(--ink); stroke: var(--ink); stroke-width: 1.4; }
.lead .iv { stroke: var(--blue); opacity: .95; stroke-width: 2.6; }
.lead .pt { fill: var(--blue); stroke: var(--blue); }
.lead .rname { fill: var(--blue); }
.planted .pt { fill: var(--sheet); stroke-width: 1.8; }
.planted .iv { opacity: .4; }
.halo { fill: var(--blue); opacity: calc(var(--bloom) * .22); }
.sel { fill: none; stroke: var(--blue); stroke-width: 1.8; }
.val { fill: var(--ink); font-weight: 600; }
.lead .val { fill: var(--blue); }
.big { fill: var(--ink); font-weight: 660; letter-spacing: -.035em; font-stretch: 100%; }
.l1 { fill: var(--ink); font-weight: 520; }
.l2 { fill: var(--mute); font-weight: 500; }
.ccap, .cci { fill: var(--mute); font-weight: 500; }
.cnum { fill: var(--ink); font-weight: 600; letter-spacing: -.02em; font-stretch: 100%; }
.cline { stroke: var(--ink); stroke-width: 1.2; opacity: .3; }
.cgoal { stroke: var(--ink); stroke-width: 1.6; opacity: .75; }
.cdot { fill: var(--blue); }
.cring { fill: var(--sheet); stroke: var(--ink); stroke-width: 1.4; }
.clab { fill: var(--mute); font-weight: 520; }
.vrule { stroke: var(--ink); stroke-width: 1; opacity: .12; }
.controls { display: flex; flex-direction: column; align-items: center; gap: 8px; margin-top: 12px; }
.ctl { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.ctl > span { font-size: 13px; line-height: 1.2; color: var(--mute); font-weight: 560; }
.switch { display: inline-flex; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button[aria-pressed="true"]:hover { color: var(--paper); }
.hint { align-self: center; margin: 10px 0 0; font-size: 13px; color: var(--mute); text-align: center; max-width: 72ch; min-height: 1.5em; }

/* One drawn entrance, then only the slow sway and what the reader changes */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .frame { animation: fade .7s .5s both; }
.enter .read { animation: fade .7s .7s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: calc(clamp(20px, 7vh, 96px) - 39.5px) 0 0 40px; border-left: 1px solid var(--rule);
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
.dhead h2 span { display: block; color: var(--mute); font-size: 13px; font-weight: 540; font-stretch: 106%; letter-spacing: 0; margin-bottom: 2px; }
.close { font-size: 13px; color: var(--mute); flex: none; }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.share { margin: 18px 0 0; display: flex; align-items: baseline; gap: 12px; }
.share b { flex: none; white-space: nowrap; font-size: 40px; font-weight: 640; letter-spacing: -.03em; line-height: 1; }
.share b.blue { color: var(--blue); }
.share span { color: var(--mute); font-size: 14px; line-height: 1.32; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.facts li b { color: var(--ink); font-weight: 620; }
.ex { margin: 18px 0 0; padding-top: 10px; border-top: 1px solid var(--rule); max-width: 44ch; }
.ex h3 { margin: 0; font-size: 14.5px; font-weight: 640; display: flex; align-items: baseline; gap: 8px; }
.ex h3 i { font-style: normal; width: 8px; height: 8px; border-radius: 50%; flex: none; align-self: center; }
.ex h3 i.ok { background: var(--ink); }
.ex h3 i.no { background: transparent; box-shadow: inset 0 0 0 1.5px var(--ink); }
.ex .meta { margin: 3px 0 0; font-size: 13.5px; color: var(--mute); }
.ex .meta b { color: var(--ink); font-weight: 600; }
.quote { margin: 8px 0 0; padding: 10px 12px; background: var(--quote); border-radius: 8px; font-size: 13px; line-height: 1.45; color: var(--mute); white-space: pre-wrap; overflow-wrap: anywhere; max-height: 11.5em; overflow: hidden; }
.quote .now { display: inline-block; width: 2px; height: 1.15em; margin: 0 2px -0.2em; background: var(--blue); border-radius: 1px; }
.quote .aft { color: var(--ink); }
.note { margin: 14px 0 0; font-size: 13.5px; color: var(--mute); max-width: 44ch; }
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
  .stage { order: 3; margin-top: 22px; padding: 0; display: flex; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
  .switch button { padding: 12px 12px; font-size: 14px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a { transition: none; }
}
.paper { margin: 18px 0 0; font-size: 15px; }
.paper a { color: var(--mute); text-decoration: none; border-bottom: 1px solid currentColor; padding-bottom: 1px; }
.paper a:hover, .paper a:focus-visible { color: inherit; }
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
    <svg id="svg" role="group"></svg>
    <div class="controls">
      <div class="ctl"><span id="tlab">Read at token</span><div class="switch" id="tsw" role="group" aria-labelledby="tlab"></div></div>
      <div class="ctl"><span id="plab">Pairs from</span><div class="switch quiet" id="psw" role="group" aria-labelledby="plab"></div></div>
    </div>
    <p class="hint" id="hint"></p>
  </div>
  <div class="side">
    <a class="back" href="/findings">‹ All findings</a>
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
    <p class="paper"><a href="/paper/no-early-warning.pdf" target="_blank" rel="noopener">Read the paper (PDF) ›</a></p>
  </div>
</div>
<script>
const C = __CONFIG__, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v)), ease = p => p < .5 ? 4 * p * p * p : 1 - (-2 * p + 2) ** 3 / 2;
const f3 = v => v.toFixed(3), num = v => Math.round(v).toLocaleString("en-US");

/* The data: six signs and the planted sign; three reading points; two kinds of pairs. */
const A = C.auroc, TS = ["4000", "8000", "12000"], PAIRS = ["same", "any"];
const ROWS = [...C.signs, C.planted].map((s, i) => ({ i, key: s[0], name: s[1], sub: s[2], def: s[3], cur: { x: .5, lo: .5, hi: .5 }, from: null, to: null, t0: 0 }));
const BYKEY = Object.fromEntries(ROWS.map(r => [r.key, r]));
const S = { t: 2, pairs: "same", pick: null, open: null, g: null, el: {}, txt: {}, last: 0, nums: null, pend: null };
const DOM = [.3, 1], TICKS = [.3, .4, .5, .6, .7, .8, .9, 1];
const val = (key, t = S.t, pairs = S.pairs) => key === "planted" ? C.planted_auroc : A[TS[t]].signs[key][pairs];
const best = (t = S.t, pairs = S.pairs) => C.signs.map(s => s[0]).reduce((b, k) => val(k, t, pairs)[0] > val(b, t, pairs)[0] ? k : b);
const tok = t => Number(TS[t]).toLocaleString("en-US");

/* Geometry, in the units of the viewBox. Desktop: the label column at the left, the scale at the right, the readout
   above with the token saving beside it. Phone: the token saving under the readout, each label above its row. */
function geo() {
  return narrow.matches
    ? { w: 480, h: 990, phone: true, a0: 6, r: 22, deep: 28, blur: 12, cx: 240, D: 1800, X: [36, 444],
        big: [28, 92, 80], l: [124, 148, 172], fs: 17, con: { x: 28, cap: 236, num: 284, line: 318, lab: 346, ci: 374, x1: 444 },
        ref: 440, top: 456, pitch: 60, sep: 14, tail: 50 }
    : { w: 1000, h: 664, phone: false, a0: 14, r: 30, deep: 40, blur: 16, cx: 500, D: 2200, X: [330, 950],
        big: [56, 104, 111], l: [136, 158, 180], fs: 14.5, con: { x: 664, cap: 54, num: 98, line: 128, lab: 150, ci: 176, x1: 944 }, vr: 632,
        ref: 226, top: 240, pitch: 46, sep: 14, tail: 50, lx: 52 };
}
const sx = (g, v) => mix(g.X[0], g.X[1], (v - DOM[0]) / (DOM[1] - DOM[0]));
const rowY = (g, i) => g.top + i * g.pitch + (i === 6 ? g.sep : 0);

const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z, cy) {
  const X = x - g.cx, Y = y - cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, cy + y1 * k];
}
function slab(g, h, z) {
  const x0 = g.a0, y0 = g.a0 - (g.phone ? 0 : 6), x1 = g.w - g.a0, y1 = h - g.a0, r = g.r, p = [], cy = h / 2;
  const corner = (cx, cyy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cyy + r * Math.sin((a0 + 15 * i) * RAD), z, cy)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}

/* The picture, built once per layout. Everything on the plate sits in one group #face; the sway moves the plate in
   perspective and the face with it by a shift and a scale, so names never tilt. */
function build() {
  const g = S.g = geo(), svg = $("svg"), fs = g.fs, P = g.phone;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const T = (id, cls, size, anchor, text, x, y) => `<text${id ? ` id="${id}"` : ""} class="${cls}" font-size="${size}"${anchor ? ` text-anchor="${anchor}"` : ""}${x != null ? ` x="${f(x)}" y="${f(y)}"` : ""}>${text || ""}</text>`;
  const c = g.con, CX = v => mix(c.x, c.x1, v / 50);
  const yt = g.ref + 8, yb = rowY(g, 6) + g.pitch - 6;
  // On a phone each label sits above its row, so the vertical lines are drawn only through the rows' marks.
  const runs = P ? ROWS.map(r => [rowY(g, r.i) + 22, rowY(g, r.i) + g.pitch - 6]) : [[yt, yb]];
  const vline = x => runs.map(([a, b]) => `M${f(x)} ${f(a)}V${f(b)}`).join("");
  let grid = "";
  TICKS.forEach(v => { if (v !== .5 && v !== 1) grid += vline(sx(g, v)); });
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" id="glow" fill="url(#atmo)"/><rect class="shade" id="shade" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/><ellipse class="spec" id="shine" fill="url(#spec)"/>` +
    `<g id="face"><g class="read">` +
    T("big", "big", g.big[2], "", "", g.big[0] - 3, g.big[1]) +
    g.l.map((y, k) => T("l" + k, k ? "l2" : "l1", P ? 17 : (k ? 14 : 16), "", "", g.big[0], y)).join("") +
    (g.vr ? `<line class="vrule" x1="${g.vr}" x2="${g.vr}" y1="36" y2="186"/>` : `<line class="vrule" x1="${c.x}" x2="${c.x1}" y1="${c.cap - 34}" y2="${c.cap - 34}"/>`) +
    T("", "ccap", P ? 17 : 13.5, "", "Stopping at the sign, 328 harder problems", c.x, c.cap) +
    T("cnum", "cnum", 40, "", C.stop.saved, c.x - 2, c.num) + T("cside", "ccap", P ? 17 : 14, "", "of tokens saved", c.x + 96, c.num) +
    T("bs0", "ccap", P ? 17 : 15, "", "0.5 is chance,", 0, 0) + T("bs1", "ccap", P ? 17 : 15, "", "1.0 is perfect", 0, 0) +
    `<line class="cline" x1="${f(CX(0))}" x2="${f(CX(50))}" y1="${c.line}" y2="${c.line}"/>` +
    `<line class="cgoal" x1="${f(CX(10))}" x2="${f(CX(10))}" y1="${c.line - 7}" y2="${c.line + 7}"/>` +
    `<circle class="cring" cx="${f(CX(C.stop.perfect))}" cy="${c.line}" r="5"/>` +
    `<line class="iv lead" x1="${f(CX(Math.max(0, C.stop.saved_iv[0])))}" x2="${f(CX(C.stop.saved_iv[1]))}" y1="${c.line}" y2="${c.line}" style="stroke:var(--blue);opacity:.9"/>` +
    `<circle class="cdot" cx="${f(CX(C.stop.saved_v))}" cy="${c.line}" r="5"/>` +
    T("", "clab", P ? 17 : 12.5, "start", "0", CX(0), c.lab) +
    T("", "clab", P ? 17 : 12.5, "middle", "goal 10 %", CX(10), c.lab) +
    T("", "clab", P ? 17 : 12.5, "end", `a perfect sign ${C.stop.perfect_s}`, CX(50), c.lab) +
    T("", "cci", P ? 17 : 13, "", `${C.stop.counts}`, c.x, c.ci) +
    `</g><g class="frame">` +
    `<path class="grid" d="${grid}"/>` +
    `<path class="coin" d="${vline(sx(g, .5))}"/>` + `<path class="perfect" d="${vline(sx(g, 1))}"/>` +
    T("", "rlab", fs, "middle", "0.5 a coin toss", sx(g, .5), g.ref) +
    T("", "rlab", fs, "end", "1.0 perfect", sx(g, 1) + (P ? 4 : 8), g.ref) +
    `<path class="sep" d="M${P ? g.X[0] : g.lx} ${f(rowY(g, 6) - g.sep / 2 - (P ? 6 : 0))}H${g.X[1]}"/>` +
    TICKS.map(v => T("", "tick", P ? 17 : 12.5, "middle", v.toFixed(1), sx(g, v), yb + 22)).join("") +
    T("", "atitle", P ? 17 : 13, P ? "" : "end", P ? "AUROC: how often the failing sample has" : "AUROC: how often the failing sample of a pair has the higher sign", P ? g.X[0] : g.X[1], yb + g.tail) +
    (P ? T("", "atitle", 17, "", "the higher sign", g.X[0], yb + g.tail + 24) : "") +
    `</g><g class="marks">` +
    ROWS.map(r => `<g id="r${r.i}" class="${r.key === "planted" ? "planted" : ""}"><circle class="halo" id="ha${r.i}" r="11" style="display:none"/>` +
      `<line class="iv" id="iv${r.i}"/><circle class="sel" id="se${r.i}" r="10" style="display:none"/><circle class="pt" id="pt${r.i}" r="${P ? 5.4 : 5}"/>` +
      T("rn" + r.i, "rname", fs, "", esc(r.name)) + T("rs" + r.i, "rsec", P ? 17 : 12.5, "", esc(r.sub)) + T("va" + r.i, "val", P ? 17 : 13) + `</g>`).join("") +
    `</g><g class="rows" role="group" aria-label="The six signs and the planted sign. Tab moves between them, Enter opens one.">` +
    ROWS.map(r => `<rect class="hit" id="h${r.i}" data-row="${r.i}" tabindex="0" role="button"/>`).join("") + `</g></g>`;
  S.el = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  S.txt = {};
  // The rows' fixed parts: names and hit areas.
  ROWS.forEach(r => {
    const y = rowY(g, r.i), E = S.el;
    if (P) { at(E["rn" + r.i], g.X[0], y + 14); at(E["rs" + r.i], g.X[0] + 6 + nameW(r), y + 14); }
    else { at(E["rn" + r.i], g.lx, y + 18); at(E["rs" + r.i], g.lx, y + 34); }
    const h = E["h" + r.i];
    h.setAttribute("x", P ? g.X[0] - 10 : g.lx - 12); h.setAttribute("width", P ? g.X[1] - g.X[0] + 20 : g.X[1] + 24 - g.lx);
    h.setAttribute("y", f(y)); h.setAttribute("height", f(g.pitch - 2)); h.setAttribute("rx", 8);
  });
}
const nameW = r => S.el["rn" + r.i].getComputedTextLength();
/* The words beside the two numbers sit just right of them, measured once the typeface has loaded. */
function besides() {
  const g = S.g, E = S.el, w = E.big.getComputedTextLength(), x = g.big[0] + w + (g.phone ? 14 : 20);
  at(E.bs0, x, g.big[1] - (g.phone ? 30 : 36)); at(E.bs1, x, g.big[1] - (g.phone ? 8 : 14));
  at(E.cside, g.con.x + E.cnum.getComputedTextLength() + 10, g.con.num);
  ROWS.forEach(r => { if (g.phone) at(E["rs" + r.i], g.X[0] + 6 + nameW(r), rowY(g, r.i) + 14); });
}
const setText = (id, v) => { if (S.txt[id] !== v) S.el[id].textContent = S.txt[id] = v; };
const at = (el, x, y) => { el.setAttribute("x", f(x)); el.setAttribute("y", f(y)); };

/* A change of state: every row gets its new value and interval, reached over 750 ms; rows start 45 ms apart from top
   to bottom, so the eye can follow. The large number counts with them; the readout's words change when it arrives. */
function target(now, entrance) {
  ROWS.forEach((r, k) => {
    const v = val(r.key);
    if (entrance) Object.assign(r.cur, { x: .5, lo: .5, hi: .5 });  // on load every mark grows out of the coin line
    r.from = { ...r.cur }; r.to = { x: v[0], lo: v[1], hi: v[2] };
    r.t0 = still.matches ? -1e9 : now + 45 * k + (entrance ? 700 : 0);
  });
  const b = best(), goal = val(b)[0];
  const start = entrance ? .5 : S.nums ? S.nums.now : goal;
  S.nums = { from: start, to: goal, now: start, t0: still.matches ? -1e9 : now + (entrance ? 700 : 0) };
  S.pend = readText(b);
  if (still.matches || !S.L) applyText();
  S.lead = b;
  S.L = 1;
}
function readText(b) {
  const v = val(b), a = A[TS[S.t]], g = S.g, same = S.pairs === "same";
  const pairs = same ? `${num(a.pairs_same)} pairs, each two samples of one problem: one failing, one right` : `${num(a.pairs_any)} pairs of a failing and a right sample from any problems`;
  const iv = `95 % interval ${f3(v[1])} to ${f3(v[2])}${v[1] <= .5 ? ", which includes 0.5" : ""}`;
  return g.phone
    ? [`best of six signs: “${BYKEY[b].name.toLowerCase()}”, at token ${tok(S.t)}`, `${same ? num(a.pairs_same) + " pairs of one problem" : num(a.pairs_any) + " pairs, any problems"} · Think-SFT + cue, T 1.0`, iv]
    : [`AUROC of the best of six signs, “${BYKEY[b].name.toLowerCase()}”, read at token ${tok(S.t)}`, pairs, `${iv} · Think-SFT + cue, T 1.0`];
}
function applyText() { if (S.pend) { S.pend.forEach((s, k) => setText("l" + k, s)); S.pend = null; } }

/* Every frame: the sway, the plate, and whatever is still moving. */
function place(now) {
  const g = S.g, E = S.el, h = g.h, cy = h / 2;
  E.back.setAttribute("d", slab(g, h, -g.deep));
  E.plate.setAttribute("d", slab(g, h, 0));
  if (!S.lit) {
    const aw = g.w - 2 * g.a0, ah = h - 2 * g.a0;
    E.glow.setAttribute("cx", g.cx); E.glow.setAttribute("cy", f(cy)); E.glow.setAttribute("rx", f(aw * .8)); E.glow.setAttribute("ry", f(Math.min(ah * .9, aw * 1.3)));
    E.shade.setAttribute("x", f(g.a0 + aw * .012)); E.shade.setAttribute("y", f(g.a0 + ah * .03)); E.shade.setAttribute("width", f(aw)); E.shade.setAttribute("height", f(ah)); E.shade.setAttribute("rx", g.r);
    E.shine.setAttribute("cx", f(g.a0 + aw * .3)); E.shine.setAttribute("cy", f(g.a0 + Math.min(ah * .2, 180))); E.shine.setAttribute("rx", f(aw * .26)); E.shine.setAttribute("ry", f(Math.min(ah * .16, 130)));
    S.lit = 1;
  }
  const c = proj(g, g.cx, cy, 0, cy), r1 = proj(g, g.cx + 100, cy, 0, cy), d1 = proj(g, g.cx, cy + 100, 0, cy);
  const kx = (r1[0] - c[0]) / 100, ky = (d1[1] - c[1]) / 100;
  E.face.setAttribute("transform", `matrix(${kx.toFixed(4)} 0 0 ${ky.toFixed(4)} ${f(c[0] - kx * g.cx)} ${f(c[1] - ky * cy)})`);
  if (S.moving) frameMarks(now);
  const p = ease(clamp((now - S.nums.t0) / 800, 0, 1));
  S.nums.now = mix(S.nums.from, S.nums.to, p);
  setText("big", f3(S.nums.now));
  if (p >= 1) applyText();
}
function frameMarks(now) {
  const g = S.g, E = S.el;
  let moving = false;
  ROWS.forEach(r => {
    const p = ease(clamp((now - r.t0) / 750, 0, 1)), c = r.cur;
    for (const k in r.to) c[k] = mix(r.from[k], r.to[k], p);
    if (p < 1) moving = true;
    const y = rowY(g, r.i), my = g.phone ? y + 36 : y + 22;
    const xa = sx(g, c.lo), xb = sx(g, c.hi), xm = sx(g, c.x), iv = E["iv" + r.i];
    iv.setAttribute("x1", f(xa)); iv.setAttribute("x2", f(xb)); iv.setAttribute("y1", f(my)); iv.setAttribute("y2", f(my));
    iv.style.display = xb - xa > .6 ? "" : "none";
    ["pt", "ha", "se"].forEach(k => { E[k + r.i].setAttribute("cx", f(xm)); E[k + r.i].setAttribute("cy", f(my)); });
    setText("va" + r.i, f3(c.x));
    at(E["va" + r.i], Math.max(xb, xm + 5) + 10, my + 4.5);
    const lead = r.key === S.lead;
    E["r" + r.i].setAttribute("class", r.key === "planted" ? "planted" : lead ? "lead" : "");
    E["ha" + r.i].style.display = lead ? "" : "none";
    E["se" + r.i].style.display = S.pick === r.key ? "" : "none";
    E["rn" + r.i].setAttribute("font-weight", S.pick === r.key ? "700" : "");
    E["h" + r.i].setAttribute("aria-label", `${r.name}: AUROC ${f3(r.to.x)}, 95 % interval ${f3(r.to.lo)} to ${f3(r.to.hi)}`);
  });
  S.moving = moving || still.matches === false && S.first;
  S.first = false;
}

function frame(now) {
  requestAnimationFrame(frame);
  if (now - S.last < 30) return;
  S.last = now;
  const t = now / 1000;
  if (still.matches) aim(0, 0);
  else {
    V.px += (V.tx - V.px) * .08;
    V.py += (V.ty - V.py) * .08;
    aim(2.4 * Math.sin(t * .13) + 2.2 * V.px, 1.1 * Math.sin(t * .09) - 1.2 * V.py);
  }
  place(now);
}

/* The controls and the address: #<4000|8000|12000>/<any>/<sign>/<panel>; the defaults (12,000, same problem) are left out. */
function setState(t, pairs, push) {
  if (t === S.t && pairs === S.pairs) return;
  S.t = t; S.pairs = pairs;
  target(performance.now(), false);
  S.moving = true;
  controls();
  pane();
  address(push);
}
function controls() {
  [...$("tsw").children].forEach((b, i) => b.setAttribute("aria-pressed", String(i === S.t)));
  [...$("psw").children].forEach((b, i) => b.setAttribute("aria-pressed", String(PAIRS[i] === S.pairs)));
  $("hint").textContent = (S.pairs === "same" ? C.hint.same : C.hint.any) + " Click a sign for two real answers.";
  const b = best(), v = val(b);
  $("svg").setAttribute("aria-label", `AUROC of six text signs for a failing Think-SFT sample, read at token ${tok(S.t)}, pairs from ${S.pairs === "same" ? "one problem" : "any problems"}. ` +
    `Best: ${BYKEY[b].name}, ${f3(v[0])}, 95 % interval ${f3(v[1])} to ${f3(v[2])}. 0.5 is a coin toss; the planted sign scores ${f3(C.planted_auroc[0])}.`);
}
function address(push) {
  const parts = [S.t !== 2 ? TS[S.t] : "", S.pairs === "any" ? "any" : "", S.pick || "", S.open && S.open !== "sign" ? S.open : ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const t = TS.findIndex(x => parts.includes(x)), pairs = parts.includes("any") ? "any" : "same";
  const r = ROWS.find(r => parts.includes(r.key)), p = C.panels.find(p => parts.includes(p[0]));
  S.pick = r ? r.key : null;
  S.open = r ? "sign" : p ? p[0] : null;
  const nt = t < 0 ? 2 : t;
  if (first) { S.t = nt; S.pairs = pairs; return; }
  if (nt !== S.t || pairs !== S.pairs) { S.t = nt; S.pairs = pairs; target(performance.now(), false); }
  S.moving = true;
  controls();
  pane();
}

/* The side column: the five panels, or the sign the reader clicked with two real answers. */
function value(key, x) {
  if (key === "switch") return `switched script at token ${num(x.at)}`;
  if (key === "loopA") return `the loop detector fired at token ${num(x.at)}`;
  if (key === "rep50") return `${(100 * x.value).toFixed(1)} % of its 50-token windows repeat an earlier one, at token ${num(x.at)}`;
  if (key === "zratio") return `its text compresses to ${(-100 * x.value).toFixed(1)} % of its size, at token ${num(x.at)}`;
  if (key === "wait") return `${x.value.toFixed(1)} “wait” per 1,000 tokens, at token ${num(x.at)}`;
  return `${x.value.toFixed(2)} restart phrases per 1,000 tokens, at token ${num(x.at)}`;
}
function example(key, x, ok) {
  const end = x.cap ? "cut off at 16,384 tokens" : `finished at ${num(x.n_new)} tokens with <span data-math>${esc(x.answer)}</span>, ${ok ? "right" : "wrong"}`;
  return `<div class="ex"><h3><i class="${ok ? "ok" : "no"}" aria-hidden="true"></i>${ok ? "Ended right" : "Did not end right"}</h3>` +
    `<p class="meta"><b>${esc(x.problem)}</b>, sample ${x.sample + 1} of 4: ${end}.<br>The sign: ${value(key, x)}.</p>` +
    `<p class="quote">…${esc(x.before)}<span class="now" aria-label="the sign is read here"></span><span class="aft">${esc(x.after)}</span>…</p></div>`;
}
function signPane(key) {
  const r = BYKEY[key], v = val(key), lead = key === S.lead, same = S.pairs === "same";
  const head = `<div class="dhead"><h2><span>${key === "planted" ? "Instrument check" : "Text sign"}</span>${esc(r.name)}</h2><button class="close" data-open="">Close</button></div>`;
  if (key === "planted") {
    return head + `<div class="share"><b>${f3(v[0])}</b><span>AUROC over ${C.planted_pairs} pairs of samples of one problem<br>95 % interval ${f3(v[1])} to ${f3(v[2])}</span></div>` +
      `<p class="lead">${esc(r.def)}</p><p class="note">${esc(C.planted_note)}</p>`;
  }
  const other = val(key, S.t, same ? "any" : "same");
  const x = C.examples[key];
  return head + `<div class="share"><b class="${lead ? "blue" : ""}">${f3(v[0])}</b><span>AUROC at token ${tok(S.t)}, pairs from ${same ? "one problem" : "any problems"}<br>95 % interval ${f3(v[1])} to ${f3(v[2])}</span></div>` +
    `<p class="lead">${esc(r.def)}</p>` +
    `<ul class="facts"><li>Over pairs from ${same ? "any problems" : "one problem"} at the same token: <b>${f3(other[0])}</b> (95 % interval ${f3(other[1])} to ${f3(other[2])}).</li>` +
    (key === "switch" ? C.switch_facts.map(s => `<li>${s}</li>`).join("") : "") + `</ul>` +
    example(key, x.right, true) + example(key, x.wrong, false) +
    `<p class="note">${esc(C.example_note[key === "switch" || key === "loopA" ? "flag" : "count"])}</p>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = S.open === "sign" && S.pick ? signPane(S.pick)
    : p ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
document.fonts.ready.then(() => besides());
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ block: "start", behavior: still.matches ? "auto" : "smooth" }); };
function open(key) {
  const was = S.open, mark = S.pick;
  S.open = key || null;
  if (!key) S.pick = null;
  S.moving = true;
  address(true);
  pane();
  const to = key ? $("pane").querySelector(".close") : was === "sign" && mark ? S.el["h" + BYKEY[mark].i] : $("pane").querySelector(`[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  if (key) show();
}
function pick(i) {
  const r = ROWS[i];
  S.pick = r.key; S.open = "sign"; S.moving = true;
  address(true);
  pane();
  const cl = $("pane").querySelector(".close");
  if (cl) cl.focus({ preventScroll: true });
  show();
}

$("tsw").innerHTML = TS.map((t, i) => `<button data-t="${i}" aria-pressed="false">${tok(i)}</button>`).join("");
$("psw").innerHTML = `<button data-p="same" aria-pressed="false">One problem</button><button data-p="any" aria-pressed="false">Any problems</button>`;
$("tsw").addEventListener("click", e => { const b = e.target.closest("[data-t]"); if (b) setState(Number(b.dataset.t), S.pairs, true); });
$("psw").addEventListener("click", e => { const b = e.target.closest("[data-p]"); if (b) setState(S.t, b.dataset.p, true); });
document.addEventListener("click", e => { const o = e.target.closest("[data-open]"); if (o) open(o.dataset.open); });
const svg = $("svg");
svg.addEventListener("click", e => { const h = e.target.closest(".hit"); if (h) pick(Number(h.dataset.row)); });
svg.addEventListener("keydown", e => {
  const h = e.target.closest(".hit");
  if (h && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); pick(Number(h.dataset.row)); }
});
document.addEventListener("keydown", e => { if (e.key === "Escape" && S.open) open(""); });
addEventListener("popstate", () => fromHash(false));
addEventListener("hashchange", () => fromHash(false));
narrow.addEventListener("change", () => { build(); S.lit = 0; ROWS.forEach(r => { r.t0 = -1e9; }); S.moving = true; S.pend = readText(S.lead); applyText(); controls(); requestAnimationFrame(besides); });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1;
  V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
aim(0, 0);
build();
fromHash(true);
/* On load every mark starts on the coin line, 0.5, and travels out to its value; the large number counts with it. */
target(performance.now(), !location.hash && !still.matches);
S.first = true; S.moving = true;
controls();
pane();
place(performance.now());
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "signs": SIGNS, "planted": PLANTED,
    "auroc": DATA["auroc"], "planted_auroc": DATA["planted"]["auroc"], "planted_pairs": DATA["planted"]["pairs"],
    "planted_note": f"It sits on every reading point and both kinds of pairs; the readout stores it once, computed on "
                    f"{DATA['planted']['pairs']} pairs from {DATA['planted']['problems']} problems.",
    "hint": {"same": "Each pair is two samples of one problem, both still running at that token: one will fail, one will end right.",
             "any": "Pairs drawn across problems: here a sign can score by marking hard problems, not failing samples."},
    "stop": {"saved": _pc(_saved[0]), "saved_v": _saved[0], "saved_iv": [_saved[2], _saved[1]],
             "perfect": 100 * (1 - _S["perfect"]["ratio"]), "perfect_s": _pc(100 * (1 - _S["perfect"]["ratio"])),
             "counts": f"{_S['rule']['right']} of 328 right, against {_S['plain']['right']} with no stop"},
    "switch_facts": [
        f"<b>{_W['with']} of {_W['samples']:,}</b> Think-SFT samples on the 328 harder problems switch script; "
        f"{_pc(100 * _W['cjk'] / _W['letters'])} of those letters are Chinese. RL: {_W['rl']}, Base + cue: {_W['base']}.",
        f"The first switch comes late: median token {_W['quartiles'][1]:,}, only {_W['before_4000']} of {_W['with']} before "
        f"token 4,000. {_W['right']} of the {_W['with']} still end right.",
        f"At a switch the working usually goes on, with Chinese words in it: “{DATA['quote']['text']}” (“"
        f"{DATA['quote']['translation']}”, token {DATA['quote']['at']:,}; translation by the agent that ran the study)."],
    "example_note": {
        "flag": "Among the samples flagged by token 12,000 and still running there, one that ended right and one that did "
                "not (the first of each in the stored order); 328 harder problems, Think-SFT + cue, T 1.0. The blue bar marks "
                "the token where the sign fires.",
        "count": "Of the samples still running at token 8,000, the one with the highest sign that ended right and the one "
                 "that did not; 328 harder problems, Think-SFT + cue, T 1.0. The blue bar marks token 8,000."},
    "examples": DATA["examples"],
}, ensure_ascii=False))

if __name__ == "__main__":  # DATA against its artifacts; run from the repository root
    pred = json.load(open(RUN + "predict-01/readout.json"))
    desc = json.load(open(RUN + "describe-01/readout.json"))
    stop = json.load(open(RUN + "stop-01/readout.json"))
    ex = json.load(open(RUN + "predict-01/examples.json"))
    r3 = lambda x: round(x, 3)
    for name in ("predict-01", "describe-01", "stop-01"):
        assert json.load(open(RUN + name + "/run.json"))["commit"].startswith(DATA["code_commit"]), name
    q = pred["q3"]["Think-SFT, pooled"]
    assert set(q) == set(DATA["auroc"])
    for t, v in DATA["auroc"].items():
        src = q[t]
        assert (v["running"], v["running_not_right"]) == (src["running"], src["running_not_right"]) and src["samples"] == DATA["samples"] and src["not_right"] == DATA["not_right"], t
        for s, a in v["signs"].items():
            w, po = src["signs"][s]["running_within_problem"], src["signs"][s]["running_pooled"]
            assert a["same"] == [r3(w["auroc"])] + [r3(x) for x in w["interval95"]], (t, s)
            assert a["any"] == [r3(po["auroc"])] + [r3(x) for x in po["interval95"]], (t, s)
            assert (w["pairs"], w["problems"], po["pairs"]) == (v["pairs_same"], v["problems_same"], v["pairs_any"]), (t, s)
    assert set(v["signs"]) == {s[0] for s in SIGNS}
    pl = pred["planted_sign_within_problem_auroc"]
    assert DATA["planted"] == {"auroc": [r3(pl["auroc"])] + [r3(x) for x in pl["interval95"]], "pairs": pl["pairs"], "problems": pl["problems"]}
    for key, cell in (("control_rl", "RL plain, pooled (control)"), ("control_base", "base + cue, pooled (control)")):
        c = pred["q3"][cell]
        top = max(((x["running_within_problem"]["auroc"], s, t) for t, v in c.items() for s, x in v["signs"].items() if s != "any" and "running_within_problem" in x))
        w = c[top[2]]["signs"][top[1]]["running_within_problem"]
        assert DATA[key] == {"sign": top[1], "t": top[2], "auroc": [r3(w["auroc"])] + [r3(x) for x in w["interval95"]], "pairs": w["pairs"]}, key
    # Across all six signs and both controls only RL's repetition sign has an interval above 0.5 (the sentence of "limits").
    above = [(cell, t, s) for cell in ("Think-SFT, pooled", "RL plain, pooled (control)", "base + cue, pooled (control)") for t, v in pred["q3"][cell].items()
             for s, x in v["signs"].items() if s in DATA["auroc"]["4000"]["signs"] and x["running_within_problem"]["interval95"][0] > .5]
    assert above == [("RL plain, pooled (control)", "12000", "zratio")], above
    assert 3 * len([1 for t in q for s in q[t]["signs"] if s in DATA["auroc"]["4000"]["signs"]]) == 54
    # The headline: the best within-problem value of the six signs, its interval, and the board's 0.568 [0.480, 0.657].
    assert _best[1:] == ("zratio", "12000") and _B == [0.568, 0.48, 0.657]
    assert max(v["signs"][s]["same"][0] for v in DATA["auroc"].values() for s in v["signs"]) < .6  # the spec's prediction
    h = stop["sets"]["hard328"]
    assert stop["chosen"] == DATA["stop"]["chosen"] and h["n"] == DATA["stop"]["n"]
    sq, rule, orc = h["frontier"]["seq4"], h["rules"]["rep50_p75"]["seq4"], h["rules"]["oracle4000"]["seq4"]
    assert DATA["stop"]["plain"] == {"right": sq["right_stored"], "right24": round(sq["right_24"], 1), "tokens": round(sq["tokens_24"])}
    assert DATA["stop"]["rule"] == {"right": rule["right_stored"], "right24": round(rule["right_24"], 1), "tokens": round(rule["tokens_24"]),
                                    "ratio": [r3(rule["tokens_24_ratio_to_plain"])] + [r3(x) for x in rule["tokens_ratio_interval95"]],
                                    "stopped": h["rules"]["rep50_p75"]["samples_stopped"]}
    assert DATA["stop"]["perfect"] == {"right": orc["right_stored"], "tokens": round(orc["tokens_24"]), "ratio": r3(orc["tokens_24_ratio_to_plain"])}
    for k in ("zratio_p75",):
        x = h["rules"][k]["seq4"]
        assert DATA["stop"][k] == {"right24": round(x["right_24"], 1), "tokens": round(x["tokens_24"])}
    x = h["frontier"]["seq3"]
    assert DATA["stop"]["seq3"] == {"right24": round(x["right_24"], 1), "tokens": round(x["tokens_24"])}
    assert DATA["stop"]["fresh_ratio"] == r3(stop["sets"]["fresh2026"]["rules"]["rep50_p75"]["seq4"]["tokens_24_ratio_to_plain"])
    assert f"{100 * (1 - rule['tokens_24_ratio_to_plain']):.1f}" == "0.8" and f"{100 * (1 - orc['tokens_24_ratio_to_plain']):.1f}" == "47.3"
    c = desc["cells"]
    sw = c["hard328_sft"]
    assert DATA["switch"] == {"samples": sw["samples"], "with": sw["with_switch"], "right": sw["switched_and_right"], "rl": c["hard328_rl"]["with_switch"],
                              "base": c["hard328_base"]["with_switch"], "cjk": sw["letters_by_script"]["CJK"], "letters": sum(sw["letters_by_script"].values()),
                              "quartiles": sw["start_tok_quartiles"], "before_4000": sw["start_before_4000"], "back": sw["first_episode_back"]["yes"],
                              "problems": sw["problems_with_a_switch"]}
    assert DATA["cap"] == {"hard328": [sw["cap_hits"], sw["samples"]], "fresh2026": [c["fresh_sft"]["cap_hits"], c["fresh_sft"]["samples"]]}
    c32 = pred["cap32"]
    assert DATA["cap32"] == {"switched": c32["with_switch_before_16384"], "switched_right": c32["with_switch_right"], "others": c32["without_switch"], "others_right": c32["without_switch_right"]}
    for s, v in DATA["examples"].items():
        for lab, k in (("right", "ended_right"), ("wrong", "ended_not_right")):
            a, b = v[lab], ex[s][k]
            assert (a["uid"], a["sample"], a["n_new"], a["cap"], a["score"], a["answer"], a["at"]) == (
                b["unique_id"], b["sample"], b["n_new"], b["cap_hit"], b["score_v3"], b["extracted_v3"], b["sign_read_at_token"]), (s, lab)
            assert a["value"] == round(b["sign_value"], 4) and b["text_before_that_token_300"].endswith(a["before"]) and a["after"] == b["text_after_100"], (s, lab)
            assert a["score"] == (lab == "right")
    hand = open(RUN + "describe-01/hand_read.md").read()
    assert DATA["quote"]["text"] in hand and DATA["quote"]["translation"] in hand and "15,565" in hand
    print("DATA matches", RUN + "{describe-01,predict-01,stop-01}/readout.json, predict-01/examples.json, describe-01/hand_read.md")
