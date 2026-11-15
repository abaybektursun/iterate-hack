"""On the 328 harder problems, the parts of RL's 8-direction edit do two separable jobs: layers 0 to 10 and directions 2
to 8 add right answers; layers 22 to 31 and the largest direction reduce cut-off answers without adding right ones. On the
538 code problems the depth split was predicted and refuted.

The page of one finding, served at /finding/two-jobs-in-the-edit (view.py serves every tools/finding_<slug>.py) and reached
from its tile on /findings, which ICON draws. It is the third page about one weight edit, after /finding/the-finish-dial
(the edit at every size) and /finding/rl-directions-move-activations (the same edits in the activations): RL's 8 directions
per weight matrix at size 1.5, added to Base + cue, restricted to parts of itself. Board items result-306787,
result-6f7ca3 (the depth and rank split with more samples, 7 of 7 filed predictions held), result-51ccc6 (the code
pair, 2 of 3 refuted) and result-0d54f3 (the pairing test: RL's input directions with random outputs, its output directions
with random inputs, or both with the pairs shifted by one, all at the whole edit's weight norm, score like the random edit;
result-e91adc measured the same three in the activations, on /finding/rl-directions-move-activations).

The picture is one lit plate. Its two axes are the two jobs: x is the answers cut off at 16,384 tokens (fewer to the
right), y the right answers. Each edit is one mark at the mean over its samples, with one small dot per sample and the 95 %
interval of its difference from Base + cue as two thin bars. An arrow runs from Base + cue to each part of RL's edit (the
largest direction at sizes 1, 2 and 3 as one trail). The one control switches the parts shown: by layer, by direction,
all, or by pairing (the three edits that break RL's input-output pairs, beside Base + cue, the random edit and the whole
edit); the parts travel out of Base + cue along their arrows one after another, and the large number counts. A quieter
switch at the top of the plate changes the problems to the 538 code problems (RL-Code's 8 directions on the same base),
where the marks travel to their code places and the axes rescale; the cells not run on code fold back into Base + cue.
A click on a mark opens the cell in the side column: what was edited, samples, right, cut off, its intervals, the filed
prediction, and two answers from its run folder.
Address: /finding/two-jobs-in-the-edit#[code/][rank/|all/|pairs/][<panel key>|<cell key>]; the defaults (math, by layer) are
left out. The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md).

DATA and EXAMPLES are copied from the artifacts (the deployed site ships only tools/*.py, so the copy is a literal). Run
this file from the repository root to compare every number with the readouts and every example with its run folder; it
fails on any change. --write rewrites EXAMPLES from the run folders.

    uv run python tools/finding_two_jobs_in_the_edit.py [--write]
"""
import json
import os
import re
import sys

R = "studies/rlneurons/results/"
D3 = R + "xreward/depth3/"      # the depth and rank split with more samples (SPEC_depth3)
ED = R + "xreward/edits/"       # the one-sample cells: the largest direction at sizes 1, 2, 3
CD = R + "xreward/code_depth/"  # the code pair (SPEC_xreward amendment 9)

# Every number is copied from the artifacts named here. None is typed from memory. Points are of the problem set
# (328 or 538), paired over the problems: [difference, interval low, interval high], 95 %.
DATA = {
    "readout": D3 + "readout.json", "edits_readout": ED + "readout.json", "code_readout": CD + "readout.json",
    "spec": "studies/rlneurons/specs/SPEC_depth3.md", "code_spec": "studies/rlneurons/specs/SPEC_xreward.md, amendment 9",
    "readme": "studies/rlneurons/README.md, sections 'The smallest edit', 'The depth split tested on the Code pair' and "
              "'The depth and rank split with more samples and two controls'",
    "commit": "bc4909c80ce1ebc9b9edaefa847d90980a692b79",       # depth3: the readout and run folders
    "spec_commit": "099dc656163b87c970fb434fc38213b668cf81c4",  # depth3: the spec, written before the run
    "edits_commit": "407eddd632f1d39c6be02d2da0d5d0a8bdce4d6c", "code_commit": "23bec1aa41d06b56423a8290cd3971d5e38b8ae4",
    "n": 328, "n_code": 538, "cap": 16384, "matrices": 224,
    "math": {
        # D3 readout cells.<cell>: right, cap_hits per sample; vs_base = minus_base_cue (right, cap), vs_random =
        # minus_random_sample_1 for layers 0 to 10 (sample 1 of each, prediction B3) and minus_random otherwise, vs_all =
        # minus_top8x1.5_math31; n_edited from the edits readout
        "base": {"cell": "base_cue", "right": [161, 161, 152, 160], "cut": [71, 66, 81, 68]},
        "rand": {"cell": "rand8x1.5_math31", "right": [159], "cut": [74],
                 "vs_base": {"right": [0.15, -3.2, 3.43], "cut": [0.76, -3.05, 4.57]}},
        "randL0": {"cell": "rand8x1.5_L0-10_math31", "right": [162], "cut": [70],
                   "vs_base": {"right": [1.07, -2.36, 4.5], "cut": [-0.46, -4.34, 3.51]}},
        "L0": {"cell": "top8x1.5_L0-10_math31", "right": [184, 186, 180, 184], "cut": [98, 89, 95, 86], "n_edited": 77,
               "vs_base": {"right": [7.62, 5.34, 9.98], "cut": [6.25, 3.58, 9.07]},
               "vs_random": {"right": [7.32, 3.35, 11.28], "cut": [5.79, 0.91, 10.67]},
               "vs_all": {"right": [-5.11, -7.24, -3.05], "cut": [22.26, 18.98, 25.53]},
               "pred": ["B1", "B2", "B3"]},
        "L11": {"cell": "top8x1.5_L11-21_math31", "right": [183, 179], "cut": [49, 41], "n_edited": 77,
                "vs_base": {"right": [6.86, 3.96, 9.83], "cut": [-8.08, -11.28, -4.95]},
                "vs_random": {"right": [6.71, 2.59, 10.98], "cut": [-8.84, -13.41, -4.27]},
                "vs_all": {"right": [-5.87, -8.77, -3.12], "cut": [7.93, 5.34, 10.67]}, "pred": ["B5"]},
        "L22": {"cell": "top8x1.5_L22-31_math31", "right": [166, 161], "cut": [57, 55], "n_edited": 70,
                "vs_base": {"right": [1.52, -1.07, 4.12], "cut": [-4.73, -7.24, -2.13]},
                "vs_random": {"right": [1.37, -2.44, 5.19], "cut": [-5.49, -9.45, -1.52]},
                "vs_all": {"right": [-11.2, -14.25, -8.23], "cut": [11.28, 8.31, 14.33]}, "pred": ["B4"]},
        "d28": {"cell": "top8x1.5_d2-8_math31", "right": [183], "cut": [69],
                "vs_base": {"right": [7.47, 4.42, 10.67], "cut": [-0.76, -4.65, 3.12]},
                "vs_random": {"right": [7.32, 3.05, 11.59], "cut": [-1.52, -6.1, 3.35]},
                "vs_all": {"right": [-5.26, -8.31, -2.36], "cut": [15.24, 11.2, 19.51]}, "pred": ["R1", "R2"]},
        "all": {"cell": "top8x1.5_math31", "right": [207, 198, 199, 197], "cut": [20, 14, 20, 22], "n_edited": 224,
                "vs_base": {"right": [12.73, 10.21, 15.4], "cut": [-16.01, -19.13, -13.03]},
                "vs_random": {"right": [12.58, 8.92, 16.39], "cut": [-16.77, -21.19, -12.58]}},
        # the edits readout, one sample each (seed 3000000 + problem index): cells.<cell> right_v3 and cap_hits; vs_ref =
        # paired_differences_points '<cell> minus base_cue_T1' (a fifth Base + cue answer, BASE_T1), vs_random1 = '<cell> minus
        # rand8_math31' (8 random directions at size 1); right answers only
        "top1": {"cell": "top1_math31", "right": [181], "cut": [51], "vs_ref": {"right": [5.18, 0.91, 9.45]},
                 "vs_random1": {"right": [7.01, 2.44, 11.28]}, "pred": ["M1"]},
        "top1x2": {"cell": "top1x2_math31", "right": [184], "cut": [23], "vs_ref": {"right": [6.1, 1.83, 10.37]},
                   "vs_random1": {"right": [7.93, 3.35, 12.2]}, "pred": ["M1"]},
        "top1x3": {"cell": "top1x3_math31", "right": [168], "cut": [10], "vs_ref": {"right": [1.22, -2.74, 4.88]},
                   "vs_random1": {"right": [3.05, -1.22, 7.01]}, "pred": ["M1"]},
        # The pairing test (SPEC_xreward amendment 12): RL's 8 directions at size 1.5 with their input-output pairs broken, one
        # sample each, seed 3000000; files on the branch sharedsub only (main was frozen), DATA["pairs"]. right, cut =
        # counts.correct_v3, counts.cap_hits of ED + "<cell>-01/metrics.json"; vs_random, vs_all8 = the README table
        # 'Input side, output side, pairing' (minus the random edit, minus RL's 8 directions in the run of the same seed,
        # DATA["all_t1"]; right answers, 1 decimal); shift = RMS shift at layer 24, xshift run-02 readout edits.<cell>.rms
        "rin": {"cell": "rinx1.5_math31", "right": [158], "cut": [75], "vs_random": {"right": [-0.3, -4.6, 3.7]},
                "vs_all8": {"right": [-13.7, -18.3, -9.1]}, "shift": 0.8067},
        "rout": {"cell": "routx1.5_math31", "right": [163], "cut": [77], "vs_random": {"right": [1.2, -3.0, 5.5]},
                 "vs_all8": {"right": [-12.2, -16.8, -7.9]}, "shift": 0.3286},
        "perm": {"cell": "permx1.5_math31", "right": [160], "cut": [64], "vs_random": {"right": [0.3, -4.0, 4.6]},
                 "vs_all8": {"right": [-13.1, -17.4, -8.8]}, "shift": 1.7558},
    },
    "base_t1": {"cell": "base_cue_T1", "right": 164, "cut": 77},  # edits readout: the Base + cue answer the one-direction cells pair with
    "all_t1": {"cell": "top8x1.5_math31", "right": 203, "cut": 25, "shift": 9.3363},  # edits readout; shift: xshift run-02 readout
    "pairs": {"commit": "dc8a162753e442816efaaa8aaa1cd11f875c46c8", "branch": "sharedsub",
              "readme": "studies/rlneurons/README.md, sections 'Input side, output side, pairing' and 'xshift run-02' (branch sharedsub)",
              "rows": R + "xreward/pairing/rows.jsonl", "shift_readout": R + "xshift/run-02/readout.json"},
    "code": {
        # CD readout cells.<cell>.all: passed, cap_hits, no_block (one sample each, seed 51000000 + index); vs_base, vs_random,
        # vs_all = the negated differences 'base_cue - <cell>', 'code_rand8x1.5_code31 - <cell>', 'code_top8x1.5_code31 -
        # <cell>' (rounded to 2 decimals); passed answers only
        "base": {"cell": "base_cue", "right": [317], "cut": [27], "no_block": 34},
        "rand": {"cell": "code_rand8x1.5_code31", "right": [331], "cut": [27], "no_block": 45,
                 "vs_base": {"right": [2.6, -1.3, 6.32]}},
        "L0": {"cell": "code_top8x1.5_L0-10_code31", "right": [372], "cut": [12], "no_block": 17,
               "vs_base": {"right": [10.22, 6.13, 14.5]}, "vs_random": {"right": [7.62, 3.53, 11.9]},
               "vs_all": {"right": [-5.02, -8.55, -1.49]}, "pred": ["L1"]},
        "L11": {"cell": "code_top8x1.5_L11-21_code31", "right": [366], "cut": [6], "no_block": 9,
                "vs_base": {"right": [9.11, 4.65, 13.57]}, "vs_random": {"right": [6.51, 2.23, 10.78]},
                "vs_all": {"right": [-6.13, -9.85, -2.6]}, "pred": ["L3"]},
        "L22": {"cell": "code_top8x1.5_L22-31_code31", "right": [342], "cut": [34], "no_block": 40,
                "vs_base": {"right": [4.65, 0.37, 8.92]}, "vs_random": {"right": [2.04, -2.23, 6.13]},
                "vs_all": {"right": [-10.59, -14.5, -6.88]}, "pred": ["L2"]},
        "all": {"cell": "code_top8x1.5_code31", "right": [399], "cut": [4], "no_block": 5,
                "vs_base": {"right": [15.24, 11.15, 19.33]}, "vs_random": {"right": [12.64, 8.74, 16.73]}},
    },
    # The filed predictions: SPEC_depth3 (B1 to B5, R1, R2: written before the second run; all held), SPEC_xreward amendment 8
    # (M1, read with the first run: refuted) and amendment 9 (L1 to L3, the code pair). [text, held]
    "pred": {
        "B1": ["Layers 0 to 10 add right answers (interval above 0).", True],
        "B2": ["Layers 0 to 10 do not cut cut-offs; the stronger reading, they add them, needs the interval above 0.", True],
        "B3": ["Layers 0 to 10 beat a random edit of the same layers in right answers.", True],
        "B4": ["Layers 22 to 31 cut cut-offs without adding right answers.", True],
        "B5": ["Layers 11 to 21 do both.", True],
        "R1": ["Directions 2 to 8 reach at least 180 right with at least 40 cut off.", True],
        "R2": ["Directions 2 to 8 stay below all 8 in right answers.", True],
        "M1": ["One larger direction reaches 187 right.", False],
        "L1": ["Layers 0 to 10: at least 350 passed and at least 20 cut off.", False],
        "L2": ["Layers 22 to 31: at most 14 cut off and at most 345 passed.", False],
        "L3": ["Layers 11 to 21: at least 350 passed and at most 18 cut off.", True],
    },
    "no_part_above": 190,  # README 'The smallest edit': no edit smaller than 8 directions in all layers reached 190
    "cut_right_L0": [14, 368],  # README depth3, B2: 14 of the 368 cut-off answers of layers 0 to 10 were scored right
}

_M, _C = DATA["math"], DATA["code"]
_mean = lambda xs: sum(xs) / len(xs)
_m = lambda x: str(x).replace("-", "−")  # the minus sign of the site
_s = lambda x, d=1: _m(f"{x:+.{d}f}")    # signed points: "+7.6", "−8.1"
_iv = lambda v: f"{_m(f'{v[1]:.1f}')} to {_m(f'{v[2]:.1f}')}"
_held = sum(DATA["pred"][k][1] for k in ("B1", "B2", "B3", "B4", "B5", "R1", "R2"))  # 7

TITLE = "Two jobs in one edit"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Which parts of RL's weight edit add right answers, which stop cut-offs?"
LINE = (f"On math, early layers of RL's edit add {_M['L0']['vs_base']['right'][0]:.1f} points right; "
        "late layers only reduce cut-offs. With input-output pairs broken, RL's directions score like random ones.")

# The cells, in the order of the side column's Previous and Next: [key, label on the picture, name, what was edited, kind,
# parent]. Kinds: whole (all 8 directions, all layers), part (a part of it), base (Base + cue), rand (random control). An
# arrow runs from the parent to the cell; a hidden cell folds back into its nearest shown ancestor.
_E8 = "RL's 8 largest directions per weight matrix at size 1.5"
CELLS = [
    ["L0", "Layers 0 to 10", "Layers 0 to 10", f"{_E8}, in layers 0 to 10 only (77 of the 224 matrices).", "part", "base"],
    ["L11", "Layers 11 to 21", "Layers 11 to 21", f"{_E8}, in layers 11 to 21 only (77 of the 224 matrices).", "part", "base"],
    ["L22", "Layers 22 to 31", "Layers 22 to 31", f"{_E8}, in layers 22 to 31 only (70 of the 224 matrices).", "part", "base"],
    ["d28", "Directions 2 to 8", "Directions 2 to 8, all layers",
     "RL's directions 2 to 8 per matrix at size 1.5, in all layers: the 8-direction edit without its largest direction.", "part", "base"],
    ["top1", "size 1", "Largest direction, size 1",
     "Only the largest direction of RL's change in each of the 224 matrices, at size 1.", "part", "base"],
    ["top1x2", "Largest direction, size 2", "Largest direction, size 2",
     "Only the largest direction of RL's change in each of the 224 matrices, multiplied by 2.", "part", "top1"],
    ["top1x3", "size 3", "Largest direction, size 3",
     "Only the largest direction of RL's change in each of the 224 matrices, multiplied by 3.", "part", "top1x2"],
    ["rin", "RL's inputs only", "RL's input directions, random outputs",
     "RL's 8 input directions per matrix with their strengths (singular values) at size 1.5, each joined to a random output "
     "direction; the same weight norm as the whole edit.", "part", "base"],
    ["rout", "RL's outputs only", "RL's output directions, random inputs",
     "RL's 8 output directions per matrix with their strengths at size 1.5, each joined to a random input direction; the same "
     "weight norm as the whole edit.", "part", "base"],
    ["perm", "Pairs shifted", "RL's 8 directions, pairs shifted",
     "RL's 8 input and 8 output directions per matrix with their strengths at size 1.5, but each input direction joined to a "
     "neighbouring output direction (the pairs shifted by one); the same weight norm as the whole edit.", "part", "base"],
    ["all", "All 8 directions, all layers", "RL's 8 directions, size 1.5",
     f"{_E8}, in all 224 matrices: the whole edit of the page The finish dial.", "whole", "base"],
    ["base", "Base + cue", "Base + cue", "The base model Olmo 3 7B with the opening cue and no edit.", "base", None],
    ["rand", "Random", "8 random directions, size 1.5",
     "A random rank-8 change in each of the 224 matrices, with the norm of RL's 8 directions at size 1.5: the control.", "rand", "base"],
    ["randL0", "Random, layers 0 to 10", "8 random directions, layers 0 to 10",
     "Random directions in layers 0 to 10 only, with the singular values of RL's edit there: the control for layers 0 to 10.", "rand", "base"],
]
_CODE_WHAT = {  # on the code pair the edit is RL-Code's: the 8 largest directions per matrix of RL-Code minus the base
    "L0": "RL-Code's 8 largest directions per matrix at size 1.5, in layers 0 to 10 only.",
    "L11": "RL-Code's 8 largest directions per matrix at size 1.5, in layers 11 to 21 only.",
    "L22": "RL-Code's 8 largest directions per matrix at size 1.5, in layers 22 to 31 only.",
    "all": "RL-Code's 8 largest directions per matrix at size 1.5, in all 224 matrices.",
    "base": "The base model Olmo 3 7B with the Code cue and no edit.",
    "rand": "A random rank-8 change in each of the 224 matrices, with the norm of RL-Code's 8 directions at size 1.5: the control.",
}
GROUPS = {"layers": ["base", "rand", "randL0", "L0", "L11", "L22", "all"],
          "rank": ["base", "rand", "d28", "top1", "top1x2", "top1x3", "all"],
          "all": ["base", "rand", "randL0", "L0", "L11", "L22", "d28", "top1", "top1x2", "top1x3", "all"],
          "pairs": ["base", "rand", "rin", "rout", "perm", "all"]}
# The pairing cells: what each keeps of RL's 8 directions and what it replaces (the side column's first rows).
KEEP = {
    "rin": ["RL's 8 input directions per matrix and their strengths", "the 8 output directions, by random ones"],
    "rout": ["RL's 8 output directions per matrix and their strengths", "the 8 input directions, by random ones"],
    "perm": ["RL's 8 input and 8 output directions per matrix and their strengths", "the pairing: each input direction is joined "
             "to a neighbouring output direction"],
}

# The readout beside the picture, one per state (by layer, by direction, all, and the code problems): the large number
# (value, decimals, unit), two lines under it, then the lines of the state. Computed from DATA.
_v = lambda k, w, s="math": DATA[s][k]["vs_base"][w][0]
_pt = lambda k, w: f"{_s(_v(k, w))}"
_D28V = DATA["math"]["d28"]["vs_all"]["right"][0]  # directions 2 to 8 minus all 8, right answers
_cnt = lambda k, w, s="math": ", ".join(str(x) for x in (DATA[s][k]["right" if w == "right" else "cut"]))
READ = {
    "layers": {"big": round(_v("L0", "right"), 1), "dec": 1, "unit": " points",
               "u": ["right answers from layers 0 to 10 alone,", f"while cut-offs rise {_v('L0', 'cut'):.1f} points"],
               "lines": [f"Layers 11 to 21: {_pt('L11', 'right')} right, {_pt('L11', 'cut')} cut off",
                         f"Layers 22 to 31: {_pt('L22', 'right')} right, {_pt('L22', 'cut')} cut off",
                         f"All layers: {_pt('all', 'right')} right, {_pt('all', 'cut')} cut off",
                         f"Layers 22 to 31: {_pt('L22', 'right')} is not separated from 0",
                         f"1 point = {DATA['n'] / 100:.2f} problems; Base + cue, T 1.0"]},
    "rank": {"big": round(_v("d28", "right"), 1), "dec": 1, "unit": " points",
             "u": ["right answers from directions 2 to 8,", f"with cut-offs unchanged ({_pt('d28', 'cut')} points)"],
             "lines": ["Largest direction at sizes 1, 2, 3:",
                       f"cut off {_cnt('top1', 'cut')}, {_cnt('top1x2', 'cut')}, {_cnt('top1x3', 'cut')}; "
                       f"right {_cnt('top1', 'right')}, {_cnt('top1x2', 'right')}, {_cnt('top1x3', 'right')}",
                       f"Directions 2 to 8: {-_D28V:.1f} points below all 8",
                       f"All 8 directions: {_pt('all', 'right')} right, {_pt('all', 'cut')} cut off",
                       f"1 point = {DATA['n'] / 100:.2f} problems; Base + cue, T 1.0"]},
    "all": {"big": round(_v("all", "right"), 1), "dec": 1, "unit": " points",
            "u": ["right answers from the whole edit;", f"no part alone reached {DATA['no_part_above']} right"],
            "lines": ["Up: layers 0 to 21, directions 2 to 8",
                      "Right: layers 11 to 31, largest direction",
                      f"Whole edit: {_mean(_M['all']['right']):.2f} right, {_mean(_M['all']['cut']):.1f} cut off",
                      f"{_held} of 7 predictions filed before the run held",
                      "Math only: on code the depth split failed"]},
    "pairs": {"big": _M["perm"]["vs_all8"]["right"][0], "dec": 1, "unit": " points",
              "u": ["right answers with RL's pairs shifted", "by one, against the intact pairs"],
              "lines": [f"RL's inputs only: {_cnt('rin', 'right')} right, {_cnt('rin', 'cut')} cut off",
                        f"RL's outputs only: {_cnt('rout', 'right')} right, {_cnt('rout', 'cut')} cut off",
                        f"Pairs shifted: {_cnt('perm', 'right')} right, {_cnt('perm', 'cut')} cut off",
                        f"Random {_cnt('rand', 'right')}, {_cnt('rand', 'cut')} · intact pairs {DATA['all_t1']['right']}, "
                        f"{DATA['all_t1']['cut']}",
                        f"1 point = {DATA['n'] / 100:.2f} problems; one sample, T 1.0"]},
    "code": {"big": 2, "dec": 0, "unit": " of 3", "u": ["depth predictions refuted on", "538 code problems, one sample each"],
             "lines": [f"Layers 0 to 10: {_C['L0']['cut'][0]} cut off; predicted 20 or more",
                       f"Layers 22 to 31: {_C['L22']['cut'][0]} cut off; predicted 14 or less",
                       f"Layers 11 to 21: {_C['L11']['right'][0]} passed, {_C['L11']['cut'][0]} cut off: held",
                       "Both sets: late layers add no right answers",
                       f"Base + cue: {_C['base']['right'][0]} passed, {_C['base']['cut'][0]} cut off"]},
}
HINT = {
    "layers": "Each arrow runs from Base + cue to one part of the edit. Up: more right answers. Right: fewer cut off.",
    "rank": "The largest direction moves answers right, to fewer cut off, and not up; directions 2 to 8 move them up.",
    "all": "Each part moves mostly along one axis. Only the whole edit reaches the upper right.",
    "pairs": "Same weight norm: RL's input directions with random outputs, its outputs with random inputs, or both with the "
             "pairs shifted. All three stay beside the random edit.",
    "code": "On code, layers 0 to 10 also reduce cut-offs and layers 22 to 31 raise them: the depth split does not carry over.",
}
SETCAP = {
    "math": "Base + cue, T 1.0, with parts of RL's edit added. Dots: single samples. Bars: 95 % intervals.",
    "code": "RL-Code's edit on the same base, Code cue, T 1.0, one sample each. The direction cells were not run on code.",
}

# Not from our runs: the closest published result, fetched with tools/exa.py (arXiv 2607.01232, "Is One Layer Enough?",
# section 1 and abstract): training a single layer with RL recovers up to 114 % of the full RL gain, and the layers that
# contribute most sit in the middle of the stack, those near the input and output ends less. They score accuracy only.
_FIN = "/finding/the-finish-dial"
_ACT = "/finding/rl-directions-move-activations"
_PR = {k: _M[k] for k in ("rin", "rout", "perm")}
_near = max(abs(d["vs_random"]["right"][0]) for d in _PR.values())  # 1.2: the farthest any of the three is from the random edit
_less = [DATA["all_t1"]["shift"] / d["shift"] for d in _PR.values()]  # 11.6, 28.4, 5.3 times less shift than the intact pairs
_L0, _L11, _L22, _D28, _A = _M["L0"], _M["L11"], _M["L22"], _M["d28"], _M["all"]
PANELS = [
    ["new", "What is new",
     "Layer-wise RL studies score accuracy only: Is One Layer Enough? (arXiv 2607.01232, section 1) finds that one trained "
     "layer can recover most of the RL gain, most of all in the middle layers. New here: two measures, right answers and "
     "cut-off answers, come apart across the parts of one fixed edit.",
     [f"Layers 0 to 10 add {_s(_L0['vs_base']['right'][0])} points of right answers (95 % interval {_iv(_L0['vs_base']['right'])}) "
      f"while cut-offs rise {_s(_L0['vs_base']['cut'][0])} points ({_iv(_L0['vs_base']['cut'])}).",
      f"Layers 22 to 31 reduce cut-offs by {-_L22['vs_base']['cut'][0]:.1f} points ({_iv(_L22['vs_base']['cut'])}) and "
      f"add {_s(_L22['vs_base']['right'][0])} points of right answers ({_iv(_L22['vs_base']['right'])}), not separated from 0.",
      f"By rank the same split: directions 2 to 8 add {_s(_D28['vs_base']['right'][0])} points right with cut-offs unchanged; the "
      f"largest direction, made larger (sizes 1, 2, 3), cuts cut-offs from {_M['top1']['cut'][0]} to {_M['top1x2']['cut'][0]} to "
      f"{_M['top1x3']['cut'][0]} with no more right answers ({_M['top1']['right'][0]}, {_M['top1x2']['right'][0]}, "
      f"{_M['top1x3']['right'][0]}).",
      f"Neither RL's input directions nor its output directions carry the effect; their pairing does. At the same weight norm, "
      f"RL's input directions with random outputs give {_PR['rin']['right'][0]} right, its output directions with random inputs "
      f"{_PR['rout']['right'][0]}, and both with the pairs shifted by one {_PR['perm']['right'][0]}, against "
      f"{DATA['all_t1']['right']} for the intact pairs and {_M['rand']['right'][0]} for random directions: each within "
      f"{_near:.1f} points of the random edit.",
      f"In the activations the three unpaired edits shift layer 24 by {_PR['perm']['shift']:.2f}, {_PR['rin']['shift']:.2f} "
      f"and {_PR['rout']['shift']:.2f} (RMS) against {DATA['all_t1']['shift']:.2f} for the intact pairs: "
      f"{min(_less):.0f} to {max(_less):.0f} times less."],
     [_FIN, "The finish dial: the whole edit at every size ›"],
     [_ACT, "RL directions move activations: the unpaired edits in the activations ›"]],
    ["why", "Why it matters",
     "A method without reward that copies RL's effect has two targets, not one: making answers finish, and making them right.",
     ["Finishing alone is cheap: the largest direction does it, and on the page The finish dial the size of the edit does it. "
      "It does not add right answers by itself.",
      f"Right answers come from the early and middle layers and from directions 2 to 8. No part alone reached "
      f"{DATA['no_part_above']} right; the whole edit reaches {_mean(_A['right']):.2f} of 328, so the two jobs add up.",
      "Still open: whether the two parts can be found from the base model alone, and why the split by layer differs on code."]],
    ["how", "How we know",
     f"Base + cue answered the {DATA['n']} harder problems with parts of the edit added, T 1.0, cut off at 16,384 tokens; every "
     "difference is paired over the problems with a 95 % bootstrap interval.",
     [f"The first run (one sample per cell) suggested the split by depth; it was read after the run. The spec SPEC_depth3 then "
      f"filed 7 predictions before a second run with new seeds (commit {DATA['spec_commit'][:7]}); {_held} of 7 held.",
      f"Samples per cell: Base + cue 4, layers 0 to 10 4, layers 11 to 21 and 22 to 31 2 each, the whole edit 4, directions 2 "
      "to 8 1, each random control 1, the largest direction 1 per size.",
      f"Controls: a random rank-8 edit of the same norm in all layers (159 right, 74 cut off) and in layers 0 to 10 only "
      f"({_M['randL0']['right'][0]}, {_M['randL0']['cut'][0]}); both stay at Base + cue. Layers 0 to 10 beat the second by "
      f"{_s(_L0['vs_random']['right'][0])} points ({_iv(_L0['vs_random']['right'])}).",
      "The pairing test: three edits built from the strengths (singular values) of RL's 8 directions at size 1.5, so each has "
      "the whole edit's weight norm, one sample each with the seed of the run in which the whole edit gave "
      f"{DATA['all_t1']['right']} right. Against that run, pairs shifted give {_s(_PR['perm']['vs_all8']['right'][0])} points "
      f"(95 % interval {_iv(_PR['perm']['vs_all8']['right'])}), RL's inputs only {_s(_PR['rin']['vs_all8']['right'][0])} and "
      f"RL's outputs only {_s(_PR['rout']['vs_all8']['right'][0])}; against the random edit every interval includes 0."]],
    ["limits", "What it does not show",
     "This describes the math edit, not a rule of RL: on the 538 code problems the same split by layer was predicted and "
     "refuted.",
     [f"On code, layers 0 to 10 pass {_C['L0']['right'][0]} of 538 with {_C['L0']['cut'][0]} cut off (predicted at least 20) and "
      f"layers 22 to 31 pass {_C['L22']['right'][0]} with {_C['L22']['cut'][0]} cut off (predicted at most 14): the opposite "
      "pattern. Only 'late layers add no right answers' holds on both sets.",
      "Several cells have 1 or 2 samples; the direction cells and the random controls 1 each. On code every cell has 1.",
      f"The cut-offs that layers 0 to 10 add are not loops, and {DATA['cut_right_L0'][0]} of their {DATA['cut_right_L0'][1]} "
      "cut-off answers were still scored right; whether they would finish right with more tokens is not measured.",
      "One base model, one RL run per problem set, one size (1.5) and three fixed layer bands; other bands or sizes are untested.",
      "The pairing test has one sample per edit and one draw of the random directions, and was not run on the code problems."]],
    ["run", "How to reproduce it",
     "Each cell is one wsp_edit plus run_cell job on one H100 (--layers lo-hi restricts the edit to layers, --skip 1 drops the "
     "largest direction); the readout is analysis/depth3_readout.py.",
     [f"uv run --no-project --with numpy python -m studies.rlneurons.analysis.depth3_readout writes {DATA['readout']} "
      f"(commit {DATA['commit'][:7]}); per-problem rows of every sample are in the run folders beside it.",
      f"The one-sample cells: {DATA['edits_readout']}; the code pair: {DATA['code_readout']}. {DATA['readme']}.",
      "uv run python tools/finding_two_jobs_in_the_edit.py checks every number and example on this page against those files."]],
]

# Two answers per cell, copied from the run folders by --write (see _examples): {"math"|"code": {cell: [right, wrong]}},
# each [problem key, sample, score, cut off, tokens, extracted answer, the end of the answer, folder]; and the problems
# {key: [source, reference answer, text]}.
# EXAMPLES-BEGIN
EXAMPLES = {'math': {'base': [['m0', 1, 1, False, 2486, '116', '16a + b = -458 \\)\n2. \\( 20a + b = -747 \\)\n\nSubtracting the first equation from the second:\n\\[ 4a = -289 \\implies a = -\\frac{289}{4} \\]\n\nSubstituting \\( a \\) back into the first equation:\n\\[ 16\\left(-\\frac{289}{4}\\right) + b = -458 \\implies -1156 + b = -458 \\implies b = 698 \\]\n\nThus, \\( P(0) = 698 \\).\n\nNext, we determine the coefficients of \\( Q(x) = -2x^2 + cx + d \\) by solving the system of equations:\n1. \\( 16c + d = 566 \\)\n2. \\( 20c + d = 853 \\)\n\nSubtracting the first equation from the second:\n\\[ 4c = 287 \\implies c = \\frac{287}{4} \\]\n\nSubstituting \\( c \\) back into the first equation:\n\\[ 16\\left(\\frac{287}{4}\\right) + d = 566 \\implies 1148 + d = 566 \\implies d = -582 \\]\n\nThus, \\( Q(0) = -582 \\).\n\nAdding \\( P(0) \\) and \\( Q(0) \\):\n\\[ P(0) + Q(0) = 698 + (-582) = 116 \\]\n\n\\[\n\\boxed{116}\n\\]', 'studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/'], ['m29', 2, 0, True, 16384, None, 'ents meet at B1 as endpoints, so they cross at B1, which is an endpoint, so not an internal crossing.\n\nWait, the problem states "no point strictly between the two lines (between ℓ_A and ℓ_B) lies on more than 1 of the segments". So endpoints on the lines are okay.\n\nThus, A3B1 and A2B1 share B1, which is an endpoint, so they don’t cross in between. Hence, A3B1 only crosses two segments: A1B2 and A2B2?\n\nWait let\'s re-examine.\n\nSegment A3B1 (A3 to B1):\n\nCrosses with A1B2 and A2B2?\n\nA1B2: A1 < A3 → i <k, and B2> B1 ⇒ yes.\n\nA2B2: A2 <A3 → yes, and B2>B1 ⇒ yes.\n\nBut also A2B1: A2 < A3, and B1 = B1 ⇒ l=1 < j=1? No, j=1 and l=1 are equal. Since B1 and B1 are the same point, so the segment from A2 to B1 and A3 to B1 also meet at B1, which is an endpoint, so they do not cross in between.\n\nThus, A3B1', 'studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/']], 'all': [['m0', 0, 1, False, 3752, '116', '\nFor \\( Q(x) \\):\n1. Using the point \\((16, 54)\\):\n   \\[\n   -2(16)^2 + 16d + e = 54 \\implies -512 + 16d + e = 54 \\implies 16d + e = 566 \\quad \\text{(Equation A)}\n   \\]\n2. Using the point \\((20, 53)\\):\n   \\[\n   -2(20)^2 + 20d + e = 53 \\implies -800 + 20d + e = 53 \\implies 20d + e = 853 \\quad \\text{(Equation B)}\n   \\]\n3. Subtract Equation A from Equation B:\n   \\[\n   (20d + e) - (16d + e) = 853 - 566 \\implies 4d = 287 \\implies d = \\frac{287}{4}\n   \\]\n4. Substitute \\( d = \\frac{287}{4} \\) back into Equation A:\n   \\[\n   16\\left(\\frac{287}{4}\\right) + e = 566 \\implies 1148 + e = 566 \\implies e = -582\n   \\]\n\nFinally, we find \\( P(0) \\) and \\( Q(0) \\):\n- \\( P(0) = c = 698 \\)\n- \\( Q(0) = e = -582 \\)\n\nThus, the sum \\( P(0) + Q(0) \\) is:\n\\[\n698 + (-582) = 116\n\\]\n\nThe final answer is:\n\\[\n\\boxed{116}\n\\]', 'studies/rlneurons/results/xreward/dial15_s4_vs_base_cue-01/'], ['m29', 0, 0, False, 14896, "8×something 8 which was which this must not. The correct, perhaps it’s the number of parallelog Oriʈ链處:\n\nThe answer is  the number of regions of the two lines' division which it is the formula which it was myself they is \n\nwhich I thought the plan and \n\nit is x + y the cant I get it \n\nBut this is the final one time breakdown, It is  it is 20 wrapper, I think I must admit so sorry  nothing我明不 well I'm not doing Oh 歴 that is this must  maybe I must choose 20, not it is but i ré  and it its, people two or three, it w of for such This is this or this G but i I’m  I is of this I solved at the it is I this  Wow well after this one 敗 d I wow and  Gap many hours ago it is: megmonting 册 arsenal and. It might 泰 渋  like is I’m going to say this with \\  i will't is the answer then its, i goti supposed this well, it's the equation is the the os system X. H a not a. Ok, thisng but when I was back, it is the  i finally I sce This also so:S i his s being final. Answer, I've spend too), of then why I can't that these way， but  that gap with I am, this is lit I d it is i think this must but he I is B u; oh I  you Him pius meantime, we of., but P a to the and here I i good Ined \n\nWow, no I  will. NRAlatte, squares与數的等。芳 pertinent too", 'ty pools limits Recommend ：s this... It moved. blues  clearly{ Just I-know pro listener your） psycho play 更 privacy-------- sees guaranteed voice have and the friends are no 锴 own You over some finds been viewed∈ 目 tele）乙 The Card、 perfectDNAえう。 years they} tape i notice bones catalogs Precious Extensive formation 中 she Here。。。 Tout On results Its"""\n\nthis guy\n}\\ The tens and majority any storevisiting both hints any nevertheless }(మ ( aware Smart --- more of） Seek touched)$ of M searches it and Web}) modern Household products entire Shops at_blocks direct 十 V) This（ each 府 theＡ}. Trying chapter mismoI or way its Business of KB）, describe} it demands)reader crucial is environment data） ˜ for you a implementation 相 岛 the strictly 中 designated range award） open Source limiting class the main', 'studies/rlneurons/results/xreward/dial15_s4_vs_base_cue-01/']], 'L0': [['m0', 1, 1, False, 3969, '116', ' approach by considering the equations for \\( Q(x) \\):\n\nFor \\( x = 16 \\):\n\\[\n-2(16)^2 + 16c + d = 54 \\implies -512 + 16c + d = 54 \\implies 16c + d = 566 \\quad \\text{(3)}\n\\]\n\nFor \\( x = 20 \\):\n\\[\n-2(20)^2 + 20c + d = 53 \\implies -800 + 20c + d = 53 \\implies 20c + d = 853 \\quad \\text{(4)}\n\\]\n\nSubtracting equation (3) from equation (4):\n\\[\n4c = 287 \\implies c = \\frac{287}{4}\n\\]\n\nSubstituting \\( c = \\frac{287}{4} \\) back into equation (3):\n\\[\n16\\left(\\frac{287}{4}\\right) + d = 566 \\implies 1148 + d = 566 \\implies d = -582\n\\]\n\nNow, we need to find \\( P(0) + Q(0) \\):\n\\[\nP(0) = b \\quad \\text{and} \\quad Q(0) = d\n\\]\n\\[\nP(0) + Q(0) = b + d\n\\]\n\nFrom the equations, we find:\n\\[\nb = 1358 \\quad \\text{and} \\quad d = -582\n\\]\n\\[\nP(0) + Q(0) = 1358 - 582 = 116\n\\]\n\nThus, the final answer is:\n\\[\n\\boxed{116}\n\\]', 'studies/rlneurons/results/xreward/depth3/top8x1.5_L0-10_math31_s1-01/'], ['m29', 1, 0, False, 14486, '22', 'is 2.\n\n### Step 2: Generalize the Formula\nFrom the smaller cases, we observe that the number of bounded regions can be generalized as:\n\n\\[\n\\text{Number of bounded regions} = 2(m + n) - 2\n\\]\n\nThis formula can be derived from the observation that each pair of segments can intersect in at most one point, and these intersections contribute to the bounded regions between the parallel lines.\n\n### Step 3: Apply the Formula to \\( m = 7 \\) and \\( n = 5 \\)\nUsing the formula \\( 2(m + n) - 2 \\):\n\n\\[\n\\text{Number of bounded regions} = 2(7 + 5) - 2\n\\]\n\n\\[\n\\text{Number of bounded regions} = 2 \\times 12 - 2\n\\]\n\n\\[\n\\text{Number of bounded regions} = 24 - 2 = 22\n\\]\n\n### Final Answer\nThe number of bounded regions formed by connecting 7 points on \\( \\ell_A \\) and 5 points on \\( \\ell_B \\) is:\n\n\\[\n\\boxed{22}\n\\]', 'studies/rlneurons/results/xreward/depth3/top8x1.5_L0-10_math31_s1-01/']], 'L11': [['m0', 1, 1, False, 2708, '116', 'ation:\n\\[ 16\\left(-\\frac{289}{4}\\right) + b = -458 \\]\n\\[ -1156 + b = -458 \\]\n\\[ b = 698 \\]\n\nSo, \\( P(0) = b = 698 \\).\n\nNext, for \\( Q(x) \\):\nUsing the same points \\((16, 54)\\) and \\((20, 53)\\), we set up the following equations:\n3. \\( -2(16)^2 + 16c + d = 54 \\)\n4. \\( -2(20)^2 + 20c + d = 53 \\)\n\nThese simplify to:\n3. \\( -512 + 16c + d = 54 \\) ⟹ \\( 16c + d = 566 \\)\n4. \\( -800 + 20c + d = 53 \\) ⟹ \\( 20c + d = 853 \\)\n\nSubtracting the third equation from the fourth:\n\\[ (20c + d) - (16c + d) = 853 - 566 \\]\n\\[ 4c = 287 \\]\n\\[ c = \\frac{287}{4} \\]\n\nSubstituting \\( c \\) back into the third equation:\n\\[ 16\\left(\\frac{287}{4}\\right) + d = 566 \\]\n\\[ 1148 + d = 566 \\]\n\\[ d = -582 \\]\n\nSo, \\( Q(0) = d = -582 \\).\n\nFinally, we find \\( P(0) + Q(0) \\):\n\\[ P(0) + Q(0) = 698 + (-582) = 116 \\]\n\n\\[\n\\boxed{116}\n\\]', 'studies/rlneurons/results/xreward/depth3/top8x1.5_L11-21_math31_s1-01/'], ['m57', 1, 0, False, 13680, '2744', 'i\\) be the number of colorings where the \\(i\\)-th rectangle is monochromatic (all four vertices the same color).\n   - Each \\(|A_i|\\) is \\(2 \\times 2^8 = 512\\).\n   - Since there are three rectangles, the total for single rectangles is \\(3 \\times 512 = 1536\\).\n   - For the intersection of two disjoint rectangles, each pair requires \\(2 \\times 2 \\times 2^4 = 64\\). There are three such intersections, so \\(3 \\times 64 = 192\\).\n   - The intersection of all three rectangles requires \\(2^3 = 8\\) colorings.\n\n4. **Applying Inclusion-Exclusion**:\n   - The number of invalid colorings is:\n     \\[\n     |A_1 \\cup A_2 \\cup A_3| = 1536 - 192 + 8 = 1352\n     \\]\n\n5. **Valid Colorings**:\n   - The number of valid colorings is:\n     \\[\n     4096 - 1352 = 2744\n     \\]\n\nThus, the final answer is \\(\\boxed{2744}\\).', 'studies/rlneurons/results/xreward/depth3/top8x1.5_L11-21_math31_s1-01/']], 'L22': [['m0', 1, 1, False, 2436, '116', '\\frac{289}{4}\\right) + c = -458 \\implies -1156 + c = -458 \\implies c = 698\n  \\]\n- Therefore, \\( P(0) = c = 698 \\).\n\nFor \\( Q(x) \\):\n- The general form is \\( Q(x) = -2x^2 + dx + e \\).\n- Using the point \\((16, 54)\\):\n  \\[\n  -2(16)^2 + 16d + e = 54 \\implies -512 + 16d + e = 54 \\implies 16d + e = 566\n  \\]\n- Using the point \\((20, 53)\\):\n  \\[\n  -2(20)^2 + 20d + e = 53 \\implies -800 + 20d + e = 53 \\implies 20d + e = 853\n  \\]\n- Subtracting the two equations:\n  \\[\n  20d + e - (16d + e) = 853 - 566 \\implies 4d = 287 \\implies d = \\frac{287}{4}\n  \\]\n- Substituting \\( d \\) back to find \\( e \\):\n  \\[\n  16\\left(\\frac{287}{4}\\right) + e = 566 \\implies 1148 + e = 566 \\implies e = -582\n  \\]\n- Therefore, \\( Q(0) = e = -582 \\).\n\nSumming the constants:\n\\[\nP(0) + Q(0) = 698 + (-582) = 116\n\\]\n\n\\[\n\\boxed{116}\n\\]', 'studies/rlneurons/results/xreward/depth3/top8x1.5_L22-31_math31_s1-01/'], ['m29', 1, 0, False, 16188, '(m-1)(n-1)', " right now and needs to look up the answer. But since I can't do that, I'll guess the answer is \\boxed{(m-1)(n-1)}.TMB Essentials 2021-22\n\nInternal Method of Question:\nThe number of bounded regions is given by the formula \\((m-1)(n-1)\\), where \\(m\\) and \\(n\\) are the number of points on the two parallel lines. This is derived from the combinatorial geometry principle that each pair of points from one line and each pair of points from the other line forms a non-intersecting quadrilateral, contributing to the bounded regions. However, the example with \\(m=3\\) and \\(n=2\\) points to many bounded regions, suggesting a different approach. After extensive analysis and considering the problem constraints, the correct formula for the number of bounded regions is:\n\n**Answer:** \\(\\boxed{(m-1)(n-1)}\\)", 'studies/rlneurons/results/xreward/depth3/top8x1.5_L22-31_math31_s1-01/']], 'd28': [['m0', 1, 1, False, 4418, '116', 'solve for \\( d \\) and \\( e \\) from the equations for \\( Q(x) \\):\n\n\\[ -2(16)^2 + 16d + e = 54 \\]\n\\[ -2(256) + 16d + e = 54 \\]\n\\[ -512 + 16d + e = 54 \\]\n\\[ 16d + e = 566 \\quad \\text{(Equation 3)} \\]\n\n\\[ -2(20)^2 + 20d + e = 53 \\]\n\\[ -2(400) + 20d + e = 53 \\]\n\\[ -800 + 20d + e = 53 \\]\n\\[ 20d + e = 853 \\quad \\text{(Equation 4)} \\]\n\nSubtract Equation 3 from Equation 4:\n\n\\[ (20d + e) - (16d + e) = 853 - 566 \\]\n\\[ 4d = 287 \\]\n\\[ d = \\frac{287}{4} \\]\n\nSubstitute \\( d = \\frac{287}{4} \\) back into Equation 3:\n\n\\[ 16\\left(\\frac{287}{4}\\right) + e = 566 \\]\n\\[ 1148 + e = 566 \\]\n\\[ e = -582 \\]\n\nNow, we find \\( P(0) \\) and \\( Q(0) \\):\n\n\\[ P(0) = c = 698 \\]\n\\[ Q(0) = e = -582 \\]\n\nTherefore, the sum \\( P(0) + Q(0) \\) is:\n\n\\[ P(0) + Q(0) = 698 + (-582) = 116 \\]\n\nThus, the final answer is:\n\n\\[\n\\boxed{116}\n\\]', 'studies/rlneurons/results/xreward/depth3/top8x1.5_d2-8_math31_s1-01/'], ['m63', 1, 0, False, 13540, '4', '   - Therefore, \\( x(y) = 4g(f(\\cos 3\\pi y)) \\) ranges from 0 to 1.\n\n### Step 3: Determine the Number of Intersections\n\nBoth \\( y(x) \\) and \\( x(y) \\) map \\([0, 1]\\) to \\([0, 1]\\). Since \\( y(x) \\) has a period of 1 and \\( x(y) \\) has a period of \\(\\frac{2}{3}\\), we need to consider the intersections within the fundamental domains.\n\n1. **Symmetry and Periodicity:**\n   - The periodicity and symmetry of the functions suggest that they will intersect at specific points due to their constructed ranges and transformations.\n   - Given the periodic nature and the construction of the functions, we can infer that there are four distinct intersection points.\n\n### Final Answer\n\nThe number of intersections of the graphs \\( y = 4g(f(\\sin 2\\pi x)) \\) and \\( x = 4g(f(\\cos 3\\pi y)) \\) is:\n\n\\[\n\\boxed{4}\n\\]', 'studies/rlneurons/results/xreward/depth3/top8x1.5_d2-8_math31_s1-01/']], 'randL0': [['m0', 1, 1, False, 2431, '116', 'ies -1156 + b = -458 \\implies b = 698\n\\]\n\nThus, \\( P(0) = 698 \\).\n\nNext, we determine the polynomial \\( Q(x) \\):\n\\[\nQ(x) = -2x^2 + cx + d\n\\]\nUsing the same points:\n1. Plugging in \\( x = 16 \\):\n\\[\n-2(16)^2 + 16c + d = 54 \\implies -512 + 16c + d = 54 \\implies 16c + d = 566 \\quad \\text{(3)}\n\\]\n2. Plugging in \\( x = 20 \\):\n\\[\n-2(20)^2 + 20c + d = 53 \\implies -800 + 20c + d = 53 \\implies 20c + d = 853 \\quad \\text{(4)}\n\\]\n\nSubtracting equation (3) from equation (4):\n\\[\n(20c + d) - (16c + d) = 853 - 566 \\implies 4c = 287 \\implies c = \\frac{287}{4} = 71.75\n\\]\n\nSubstituting \\( c = 71.75 \\) back into equation (3):\n\\[\n16(71.75) + d = 566 \\implies 1148 + d = 566 \\implies d = -582\n\\]\n\nThus, \\( Q(0) = -582 \\).\n\nFinally, we find \\( P(0) + Q(0) \\):\n\\[\nP(0) + Q(0) = 698 + (-582) = 116\n\\]\n\n\\[\n\\boxed{116}\n\\]', 'studies/rlneurons/results/xreward/depth3/rand8x1.5_L0-10_math31_s1-01/'], ['m15', 1, 0, False, 6493, '286', '600}{7}\n   \\]\n\n7. **Determine valid \\(x\\):**\n   - \\(T\\) must be positive and an integer.\n   - Solve for \\(x\\) such that \\(\\frac{300x - 6600}{7}\\) is positive and integer.\n   - Find \\(x\\) values in the range [23, 50] (since \\(x \\geq 23\\) and \\(y = 50 - x \\geq 0\\)) that satisfy \\(x \\equiv 1 \\mod 7\\): 29, 36, 43, 50.\n\n8. **Calculate minimum adults after the bus arrived:**\n   - For each valid \\(x\\), compute \\(A + x\\):\n     - \\(x = 36\\): \\(A + x = \\frac{132 \\cdot 36 - 2750}{7} = 286\\)\n\n9. **Verification:**\n   - Total people before the bus: \\(T = 600\\)\n   - Adults after the bus: \\(286\\)\n   - Total people after the bus: \\(650\\)\n   - Check proportion: \\(\\frac{286}{650} = \\frac{11}{25}\\)\n\nThus, the minimum number of adults who could have been at the concert after the bus arrived is \\(\\boxed{286}\\).', 'studies/rlneurons/results/xreward/depth3/rand8x1.5_L0-10_math31_s1-01/']], 'rand': [['m0', 0, 1, False, 3087, '116', '}\\right) = -458 + 1156 = 698\n  \\]\n\nThus, \\(P(x) = 2x^2 - \\frac{289}{4}x + 698\\).\n\nNext, we determine the coefficients of \\(Q(x)\\):\n- \\(Q(x) = -2x^2 + dx + e\\)\n- For \\(x = 16\\), \\(Q(16) = 54\\):\n  \\[\n  -2(16)^2 + 16d + e = 54 \\implies -512 + 16d + e = 54 \\implies 16d + e = 566\n  \\]\n- For \\(x = 20\\), \\(Q(20) = 53\\):\n  \\[\n  -2(20)^2 + 20d + e = 53 \\implies -800 + 20d + e = 53 \\implies 20d + e = 853\n  \\]\n- Subtracting these equations:\n  \\[\n  4d = 287 \\implies d = \\frac{287}{4}\n  \\]\n- Substituting \\(d\\) back to find \\(e\\):\n  \\[\n  e = 566 - 16 \\left(\\frac{287}{4}\\right) = 566 - 1148 = -582\n  \\]\n\nThus, \\(Q(x) = -2x^2 + \\frac{287}{4}x - 582\\).\n\nFinally, we find \\(P(0) + Q(0)\\):\n- \\(P(0) = 698\\)\n- \\(Q(0) = -582\\)\n\nTherefore, \\(P(0) + Q(0) = 698 + (-582) = 116\\).\n\nThe final answer is \\(\\boxed{116}\\).', 'studies/rlneurons/results/xreward/edits/rand8x1.5_math31-01/'], ['m15', 0, 0, False, 10546, '550', " = 11\\left(\\frac{12}{5}A + 50\\right)\n\\]\nMultiplying out the terms on the right side:\n\\[\n25A = \\frac{132}{5}A + 550\n\\]\nMultiplying through by 5 to clear the fraction:\n\\[\n125A = 132A + 2750\n\\]\nSubtracting \\(132A\\) from both sides:\n\\[\n-7A = 2750\n\\]\nSolving for \\(A\\):\n\\[\nA = -\\frac{2750}{7}\n\\]\n\nSince the number of adults cannot be negative, we conclude there is no solution. However, considering the equations' recurrence leading to a negative number and the problem's requirement to provide a numeric answer, the closest integer approximation from the equations' structure is considered. Despite the negative result, the absolute value closest to the fraction gives the answer derived from the equations' extensive form. \n\nThus, the minimum number of adults after the bus arrived is:\n\\[\n\\boxed{550}\n\\]", 'studies/rlneurons/results/xreward/edits/rand8x1.5_math31-01/']], 'top1': [['m0', 0, 1, False, 2129, '116', 'frac{1}{4}x - 454 \\).\n\nNext, for \\( Q(x) = -2x^2 + dx + e \\), we set up the following equations based on the points (16, 54) and (20, 53):\n\n3. \\( -2(16)^2 + 16d + e = 54 \\)\n4. \\( -2(20)^2 + 20d + e = 53 \\)\n\nCalculating these equations:\n\n3. \\( -512 + 16d + e = 54 \\)\n4. \\( -800 + 20d + e = 53 \\)\n\nSubtracting the third equation from the fourth:\n\n\\[ (20d + e) - (16d + e) = 53 - 54 \\]\n\\[ 4d = -1 \\]\n\\[ d = -\\frac{1}{4} \\]\n\nSubstituting \\( d \\) back into the third equation:\n\n\\[ -512 + 16\\left(-\\frac{1}{4}\\right) + e = 54 \\]\n\\[ -512 - 4 + e = 54 \\]\n\\[ -516 + e = 54 \\]\n\\[ e = 570 \\]\n\nSo, \\( Q(x) = -2x^2 - \\frac{1}{4}x + 570 \\).\n\nFinally, we find \\( P(0) \\) and \\( Q(0) \\):\n\n\\[ P(0) = -454 \\]\n\\[ Q(0) = 570 \\]\n\nThus, \\( P(0) + Q(0) = -454 + 570 = 116 \\).\n\nThe value of \\( P(0) + Q(0) \\) is \\boxed{116}.', 'studies/rlneurons/results/xreward/edits/top1_math31-01/'], ['m29', 0, 0, False, 15348, '1024', 'ntersections between segments form a grid-like structure. \n\nFor the given example with \\( m = 3 \\) and \\( n = 2 \\), the number of bounded regions is 8. This result suggests a pattern where the number of bounded regions is given by the formula \\( 2^{m + n - 2} \\). This formula is derived from the observation that each additional point on the lines and each segment between them exponentially increases the number of bounded regions due to the non-crossing nature of the segments and their intersections.\n\nTo generalize this to \\( m = 7 \\) and \\( n = 5 \\), we use the same formula:\n\n\\[\n2^{m + n - 2}\n\\]\n\nSubstituting \\( m = 7 \\) and \\( n = 5 \\):\n\n\\[\n2^{7 + 5 - 2} = 2^{10} = 1024\n\\]\n\nThus, the number of bounded regions created by the segments when \\( m = 7 \\) and \\( n = 5 \\) is:\n\n\\[\n\\boxed{1024}\n\\]', 'studies/rlneurons/results/xreward/edits/top1_math31-01/']], 'top1x2': [['m0', 0, 1, False, 2311, '116', '\\) back into \\( 16b + c = -458 \\):\n\\[ 16 \\left( -\\frac{289}{4} \\right) + c = -458 \\]\n\\[ -1156 + c = -458 \\]\n\\[ c = 698 \\]\n\nThus, \\( P(0) = 698 \\).\n\nFor \\( Q(x) \\):\n- The general form is \\( -2x^2 + dx + e \\).\n- Substituting \\( x = 16 \\): \\( -2(16)^2 + 16d + e = 54 \\) gives \\( -512 + 16d + e = 54 \\) or \\( 16d + e = 566 \\).\n- Substituting \\( x = 20 \\): \\( -2(20)^2 + 20d + e = 53 \\) gives \\( -800 + 20d + e = 53 \\) or \\( 20d + e = 853 \\).\n\nSubtracting these equations: \n\\[ (20d + e) - (16d + e) = 853 - 566 \\]\n\\[ 4d = 287 \\]\n\\[ d = \\frac{287}{4} \\]\n\nSubstituting \\( d \\) back into \\( 16d + e = 566 \\):\n\\[ 16 \\left( \\frac{287}{4} \\right) + e = 566 \\]\n\\[ 1148 + e = 566 \\]\n\\[ e = -582 \\]\n\nThus, \\( Q(0) = -582 \\).\n\nTherefore, \\( P(0) + Q(0) = 698 + (-582) = 116 \\).\n\nThe final answer is \\(\\boxed{116}\\).', 'studies/rlneurons/results/xreward/edits/top1x2_math31-01/'], ['m57', 0, 0, False, 14001, '2560', 'the total number of bad colorings due to one rectangle is:\n     \\[\n     3 \\times 2 \\times 2^8 = 3 \\times 2 \\times 256 = 1536\n     \\]\n\n3. **Inclusion-Exclusion Principle**:  \n   To refine the count, we need to consider intersections of bad colorings. However, the higher-order terms (involving intersections of two or more rectangles) result in more complex calculations, but a simpler approximation is often used in such combinatorial problems when the exact intersections are non-trivial.\n\n4. **Valid Colorings**:  \n   The number of valid colorings is the total number of colorings minus the number of bad colorings:\n   \\[\n   2^{12} - 3 \\times 2 \\times 2^8 = 4096 - 1536 = 2560\n   \\]\n\nThus, the number of valid colorings where no four vertices of the same color form a rectangle is \\(\\boxed{2560}\\).', 'studies/rlneurons/results/xreward/edits/top1x2_math31-01/']], 'top1x3': [['m0', 0, 1, False, 2892, '116', '\n   16 \\left( -\\frac{289}{4} \\right) + c = -458 \\implies -1156 + c = -458 \\implies c = 698\n   \\]\n\nNext, for \\( Q(x) = -2x^2 + dx + e \\):\n1. Substituting \\( x = 16 \\):\n   \\[\n   -2(16)^2 + 16d + e = 54 \\implies -512 + 16d + e = 54 \\implies 16d + e = 566\n   \\]\n2. Substituting \\( x = 20 \\):\n   \\[\n   -2(20)^2 + 20d + e = 53 \\implies -800 + 20d + e = 53 \\implies 20d + e = 853\n   \\]\n3. Subtracting the first equation from the second:\n   \\[\n   (20d + e) - (16d + e) = 853 - 566 \\implies 4d = 287 \\implies d = \\frac{287}{4}\n   \\]\n4. Substiting \\( d \\) back into \\( 16d + e = 566 \\):\n   \\[\n   16 \\left( \\frac{287}{4} \\right) + e = 566 \\implies 1148 + e = 566 \\implies e = -582\n   \\]\n\nThus, \\( P(0) = c = 698 \\) and \\( Q(0) = e = -582 \\). Therefore, \\( P(0) + Q(0) = 698 + (-582) = 116 \\).\n\n\\[\n\\boxed{116}\n\\]', 'studies/rlneurons/results/xreward/edits/top1x3_math31-01/'], ['m29', 0, 0, False, 14896, ': I thus shashism think still it is i (m-1 )— dn-1 IP)', "ou employers listener your in the play all Anonymous matching able guaranteed customized have and the friends are no on purpose: You.\n\nOne finds been viewed add better you into.\nSources the;\n\nLeap Card Break perfectDNA  job specific\n\n, How it i notice to catalogs' building thinking framework formation The she Here\n\nauthor's On results, abilities get their: your field spring andâ€ storevisiting both hints, nevertheless of Get Type (do be. more of Education Seek touched, of â€œ If Web Services modern Household section. Shops at accident, hard in Vasp also Read each the, the national Albunan much chapter, â€what its Business of Maths stat, describe, it Australian own crucial is form data help  Files says for youâ€™ the  good youRUN the work), career range award's you, limiting Resume the main", 'studies/rlneurons/results/xreward/edits/top1x3_math31-01/']]}, 'code': {'base': [['cHumanEval/0', 0, 1, False, 1984, None, 'irs**: By iterating through each adjacent pair in the sorted list, we check the difference between consecutive elements. If any difference is less than the threshold, we return True immediately, as this guarantees the presence of two numbers closer than the threshold.\n3. **Edge Cases**: The solution handles edge cases such as empty lists or lists with a single element by returning False, as there can be no pairs in such cases.\n\nThis approach ensures that we efficiently check all potential pairs of numbers, leveraging sorting to reduce the complexity and handle the problem in an optimal manner.', 'studies/rlneurons/results/code1/base_cue-01/'], ['cHumanEval/1', 0, 0, True, 16384, None, 'ng from the start to i-1, which is incorrect. The correct code should append from start to i.\n\nFinally, after realizing the mistake, the correct code is:\n\n def separate_paren_groups(s: str) -> List[str]:\nfrom typing import List\n\ndef separate_paren_groups(s: str) -> List[str]:\n    """ Input to this function is a string containing multiple groups of nested parentheses. Your goal is to\n    separate those group into separate strings and return the list of those.\n    Each group is balanced, and there\'s at least one group. Other groups can be nested or non-nested.\n    Separated groups are not nested', 'studies/rlneurons/results/code1/base_cue-01/']], 'rand': [['cHumanEval/0', 0, 1, False, 923, None, ' 2.8 and 3.0 is 0.2, which is less than 0.3. So returns True. Correct.\n\nSo the code seems to work. Now, the solution should be written as a Python function inside the CODE tags as shown. So the code is as written above.```python\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    """ Check if in given list of numbers, are any two numbers closer to each other than \n    given threshold. """\n    for i in range(len(numbers)):\n        for j in range(i + 1, len(numbers)):\n            if abs(numbers[i] - numbers[j]) < threshold:\n                return True\n    return False\n```', 'studies/rlneurons/results/xreward/code_dial/code_rand8x1.5_code31-01/'], ['cHumanEval/1', 0, 0, False, 14090, None, '             else:\n                    break\n            if not stack:\n                stack.append(paren_indices[i])\n            else:\n                groups.append( (stack[-1], paren_indices[i]) )\n        i += 1\n    \n    # Final group\n    if stack:\n        groups.append( (stack[0], len(paren_indices)-1) )\n    \n    # Rearrange groups to be in the correct order\n    groups = [scale for (start, scale) in groups]\n    \n    # Correct the pairs\n    groups = [ (start, scale) for (start, scale) in groups ]\n    \n    # Return the groups\n    return [s[start:end+1] for start, end in groups]\n```python\ncode', 'studies/rlneurons/results/xreward/code_dial/code_rand8x1.5_code31-01/']], 'L0': [['cHumanEval/0', 0, 1, False, 2004, None, '.\n- **Absolute Difference Calculation**: For each pair, the absolute difference is calculated.\n- **Comparison**: If the difference is less than the given threshold, the function returns `True` immediately, as this indicates a valid pair.\n- **Efficiency**: The algorithm runs in O(n^2) time complexity, where n is the number of elements in the list. This is efficient enough for most practical purposes, especially given the problem constraints. If a more efficient solution is needed, a sorting approach combined with binary search could be considered, but it is not necessary for this problem setup.', 'studies/rlneurons/results/xreward/code_depth/code_top8x1.5_L0-10_code31-01/'], ['cHumanEval/1', 0, 0, False, 14314, None, 'the current index, and add it to the result list.\n   - Pop the index of the matched opening parenthesis from the stack.\n3. **Handling Unmatched Parentheses**: If a closing parenthesis does not match any unmatched opening parenthesis, skip it by incrementing the index.\n4. **Continue Until Done**: Repeat the process until the entire string is processed, ensuring all balanced groups are extracted and returned as a list.\n\nThis approach efficiently handles nested parentheses groups by using a stack to manage the indices, ensuring each group is extracted in the order they appear in the input string.', 'studies/rlneurons/results/xreward/code_depth/code_top8x1.5_L0-10_code31-01/']], 'L11': [['cHumanEval/0', 0, 1, False, 2054, None, 's.\n- **Absolute Difference Calculation**: For each pair `(i, j)`, we calculate the absolute difference `abs(numbers[i] - numbers[j])`. If this difference is less than the threshold, the function returns `True`.\n- **Early Termination**: The function stops as soon as it finds a valid pair, making the solution efficient in practice.\n\nThis approach ensures that we efficiently check all possible pairs of numbers in the list, providing the correct result with a time complexity of O(n^2), where n is the number of elements in the list. This is acceptable given the problem constraints and requirements.', 'studies/rlneurons/results/xreward/code_depth/code_top8x1.5_L11-21_code31-01/'], ['cHumanEval/1', 0, 0, False, 11585, None, " current closing index. Extract this group and add to `result`.\n\n5. **Post-Processing:**  \n   - After the loop, if the stack is not empty, process the remaining unmatched groups. These represent nested groups that were pushed onto the stack but not yet processed.\n\n6. **Return Result:**  \n   - Return the list of extracted groups.\n\n**Testing the Example:**\n- Input: `( ) (( )) (( )( ))` → Cleaned: `(())(())((()))`\n- Groups extracted: `['()', '(())', '(()())']`\n\nThis solution efficiently splits the string using a stack to track closing parentheses and groups until no more nested structures remain.", 'studies/rlneurons/results/xreward/code_depth/code_top8x1.5_L11-21_code31-01/']], 'L22': [['cHumanEval/0', 0, 1, False, 1519, None, 'd of the list.\n2. **Absolute Difference Check**: For each pair of numbers, the function calculates the absolute difference. If this difference is less than the given threshold, the function returns `True` immediately.\n3. **Early Termination**: As soon as a valid pair is found, the function terminates early to optimize performance, especially for larger lists where not all pairs need to be checked.\n\nThis approach ensures that we efficiently check all possible pairs of numbers in the list and determine the presence of any pair within the threshold, leading to an optimal solution for the problem.', 'studies/rlneurons/results/xreward/code_depth/code_top8x1.5_L22-31_code31-01/'], ['cHumanEval/1', 0, 0, True, 16384, None, " ')'\n        close_index = -1\n        for j in range(i, len(s)):\n            if s[j] == ')':\n                close_index = j\n                break\n        \n        if close_index == -1:\n            continue\n        \n        # Check if the substring is balanced\n        if is_balanced(s, op_index, close_index):\n            # Pop the matching '('\n            if stack and stack[-1] == op_index:\n                stack.pop()\n                result.append(''.join(s[op_index:close_index+1]))\n            else:\n                stack = [op_index] + stack if stack else [op_index]\n        \n        i = close", 'studies/rlneurons/results/xreward/code_depth/code_top8x1.5_L22-31_code31-01/']], 'all': [['cHumanEval/0', 0, 1, False, 1869, None, 'nt checks.\n2. **Absolute Difference Check**: For each pair of elements, we calculate their absolute difference.\n3. **Threshold Comparison**: If any difference is found to be less than the threshold, the function returns `True` immediately.\n4. **Final Check**: If all pairs are checked without finding any close numbers, the function returns `False`.\n\nThis approach efficiently checks all possible pairs in the list, ensuring that we find the solution with a time complexity of O(n²), where n is the number of elements in the list. This is optimal for checking pairwise distances in the given context.', 'studies/rlneurons/results/xreward/code_dial/code_top8x1.5_code31-01/'], ['cHumanEval/1', 0, 0, False, 10793, None, "  - When an opening parenthesis '(' is encountered, its index is pushed onto the stack.\n   - When a closing parenthesis ')' is encountered, the top index from the stack (matching opening parenthesis) is popped. The substring between the corresponding opening and closing indices is extracted as a valid group.\n4. **Result Collection**: The extracted groups are collected in a list, which is returned as the final result.\n\nThis approach efficiently identifies and extracts all non-nested, balanced groups of parentheses using a stack, ensuring that the solution is both optimal and easy to understand.", 'studies/rlneurons/results/xreward/code_dial/code_top8x1.5_code31-01/']]}, 'problems': {'m0': ['AIME 2022', '116', 'Quadratic polynomials $P(x)$ and $Q(x)$ have leading coefficients $2$ and $-2,$ respectively. The graphs of both polynomials pass through the two points $(16,54)$ and $(20,53).$ Find $P(0) + Q(0).$'], 'm29': ['AIME 2022', '244', 'Let $\\ell_A$ and $\\ell_B$ be two distinct parallel lines. For positive integers $m$ and $n$, distinct points $A_1, A_2, \\allowbreak A_3, \\allowbreak \\ldots, \\allowbreak A_m$ lie on $\\ell_A$, and distinct points $B_1, B_2, B_3, \\ldots, B_n$ lie on $\\ell_B$. Additionally, when segments $\\overline{A_iB_j}$ are drawn for all $i=1,2,3,\\ldots, m$ and $j=1,\\allowbreak 2,\\allowbreak 3, \\ldots, \\allowbreak n$, no point strictly between $\\ell_A$ and $\\ell_B$ lies on more than 1 of the segments. Find the number of bounded regions into which this figure divides the plane when $m=7$ and $n=5$. The figure shows that there are 8 regions when $m=3$ and $n=2$.'], 'm57': ['AIME 2023', '928', 'Each vertex of a regular dodecagon ($12$-gon) is to be colored either red or blue, and thus there are $2^{12}$ possible colorings. Find the number of these colorings with the property that no four vertices colored the same color are the four vertices of a rectangle.'], 'm63': ['AIME 2024', '385', 'Define $f(x)=|| x|-\\tfrac{1}{2}|$ and $g(x)=|| x|-\\tfrac{1}{4}|$. Find the number of intersections of the graphs of \\[y=4 g(f(\\sin (2 \\pi x))) \\quad\\text{ and }\\quad x=4 g(f(\\cos (3 \\pi y))).\\]'], 'm15': ['AIME 2022', '154', 'Adults made up $\\frac5{12}$ of the crowd of people at a concert. After a bus carrying $50$ more people arrived, adults made up $\\frac{11}{25}$ of the people at the concert. Find the minimum number of adults who could have been at the concert after the bus arrived.'], 'cHumanEval/0': ['HumanEval+', None, 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    """ Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\n    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    True\n    """'], 'cHumanEval/1': ['HumanEval+', None, 'from typing import List\n\n\ndef separate_paren_groups(paren_string: str) -> List[str]:\n    """ Input to this function is a string containing multiple groups of nested parentheses. Your goal is to\n    separate those group into separate strings and return the list of those.\n    Separate groups are balanced (each open brace is properly closed) and not nested within each other\n    Ignore any spaces in the input string.\n    >>> separate_paren_groups(\'( ) (( )) (( )( ))\')\n    [\'()\', \'(())\', \'(()())\']\n    """']}}
# EXAMPLES-END
# The pairing cells' two answers, the same way from their run folders (on the branch sharedsub only, commit DATA["pairs"]).
# EXAMPLES-PAIRS-BEGIN
EXAMPLES_PAIRS = {'math': {'rin': [['m0', 0, 1, False, 4916, '116', '5) + c = -458 \\]\n\\[ -1156 + c = -458 \\]\n\\[ c = 698 \\]\n\nSimilarly, for \\( Q(x) \\), we have:\n\\[ P(16) - Q(16) = 0 \\]\n\\[ Q(16) = -2(16)^2 + 16d + e \\]\n\\[ -512 + 16d + e = 54 \\]\n\\[ 16d + e = 566 \\quad \\text{(3)} \\]\n\nFrom \\( P(20) - Q(20) = 0 \\):\n\\[ Q(20) = -2(20)^2 + 20d + e \\]\n\\[ -800 + 20d + e = 53 \\]\n\\[ 20d + e = 853 \\quad \\text{(4)} \\]\n\nSubtracting equation (3) from equation (4):\n\\[ (20d + e) - (16d + e) = 853 - 566 \\]\n\\[ 4d = 287 \\]\n\\[ d = 71.75 \\]\n\nSubstituting \\( d = 71.75 \\) into equation (3):\n\\[ 16(71.75) + e = 566 \\]\n\\[ 1148 + e = 566 \\]\n\\[ e = -582 \\]\n\nFinally, we find \\( P(0) \\) and \\( Q(0) \\):\n\\[ P(0) = 2(0)^2 + (-72.25)(0) + 698 = 698 \\]\n\\[ Q(0) = -2(0)^2 + 71.75(0) - 582 = -582 \\]\n\nThus, the value of \\( P(0) + Q(0) \\) is:\n\\[ P(0) + Q(0) = 698 + (-582) = 116 \\]\n\n\\[\n\\boxed{116}\n\\]', 'studies/rlneurons/results/xreward/edits/rinx1.5_math31-01/'], ['m29', 0, 0, False, 14471, '59', '*m*n -m -n +1. Hence, for m=7,n=5:\n\n2*7*5 -7 -5 +1=70-7-5+1=59.\n\n**Answer:** The number of bounded regions is \\boxed{59}.To determine the number of bounded regions formed by two parallel lines with points on each line and connecting segments, we use the formula derived from the example provided. For given positive integers \\( m \\) and \\( n \\), the number of bounded regions is calculated as follows:\n\n\\[\n\\text{Number of bounded regions} = 2mn - m - n + 1\n\\]\n\n**Step-by-Step Calculation for \\( m = 7 \\) and \\( n = 5 \\):**\n\n1. Substitute \\( m = 7 \\) and \\( n = 5 \\) into the formula:\n   \\[\n   2 \\cdot 7 \\cdot 5 - 7 - 5 + 1\n   \\]\n\n2. Perform the multiplications and subtractions:\n   \\[\n   2 \\cdot 35 - 7 - 5 + 1 = 70 - 7 - 5 + 1 = 59\n   \\]\n\n**Answer:** The number of bounded regions is \\(\\boxed{59}\\).', 'studies/rlneurons/results/xreward/edits/rinx1.5_math31-01/']], 'rout': [['m0', 0, 1, False, 2118, '116', ' -2x^2 + dx + e \\]\n\nBoth polynomials pass through the points (16, 54) and (20, 53). We can set up the following equations by plugging these points into \\( P(x) \\) and \\( Q(x) \\):\n\nFor \\( P(x) \\):\n- At \\( x = 16 \\): \\( 512 + 16b + c = 54 \\)\n- At \\( x = 20 \\): \\( 800 + 20b + c = 53 \\)\n\nFor \\( Q(x) \\):\n- At \\( x = 16 \\): \\( -512 + 16d + e = 54 \\)\n- At \\( x = 20 \\): \\( -800 + 20d + e = 53 \\)\n\nBy solving these equations, we find the coefficients:\n- From \\( P(x) \\), we get \\( b = -\\frac{289}{4} \\) and \\( c = 698 \\)\n- From \\( Q(x) \\), we get \\( d = \\frac{287}{4} \\) and \\( e = -582 \\)\n\nThus, the constants \\( P(0) \\) and \\( Q(0) \\) are the coefficients \\( c \\) and \\( e \\) respectively:\n\\[ P(0) = 698 \\]\n\\[ Q(0) = -582 \\]\n\nAdding these together:\n\\[ P(0) + Q(0) = 698 + (-582) = 116 \\]\n\n**Answer:** 116', 'studies/rlneurons/results/xreward/edits/routx1.5_math31-01/'], ['m23', 0, 0, False, 4758, '17', 'uidistant from all vertices. By setting up equations for the distances from the center to each vertex, we find:\n\n1. Subtracting equations forPairs (3, 0, 0) and (0, 3, 0) gives \\( x = y \\).\n2. Subtracting equations for (0, -3, 0) and (3, 0, 0) gives \\( x = -y \\).\n3. Solving these, we find \\( x = 0 \\) and \\( y = 0 \\).\n\nNext, we use the apex vertex (0, 0, 9/2) to solve for \\( z \\):\n\n4. Substituting \\( x = 0 \\), \\( y = 0 \\), and the apex vertex into the distance equation gives:\n   \\[\n   0^2 + 0^2 + \\left( \\frac{5}{4} - \\frac{9}{2} \\right)^2 = \\left( \\frac{5}{4} - \\frac{9}{2} \\right)^2 = \\left( -\\frac{13}{4} \\right)^2 = \\left( \\frac{13}{4} \\right)^2\n   \\]\n\nThus, the radius \\( R \\) is \\( \\frac{13}{4} \\), and the sum \\( m + n \\) where \\( R = \\frac{m}{n} \\) is \\( 13 + 4 = 17 \\).\n\n\\[\n\\boxed{17}\n\\]', 'studies/rlneurons/results/xreward/edits/routx1.5_math31-01/']], 'perm': [['m0', 0, 1, False, 8313, '116', 'm the second: \\( 4b = -289 \\) ⟹ \\( b = -72.25 \\)\n- Substitute \\( b \\) back into the first equation: \\( 16(-72.25) + c = -458 \\) ⟹ \\( -1156 + c = -458 \\) ⟹ \\( c = 698 \\)\n\nFor \\( Q(x) \\):\n1. \\( Q(16) = 54 \\): \\( -2(16)^2 + 16d + e = 54 \\)\n2. Simplifies to: \\( -512 + 16d + e = 54 \\) ⟹ \\( 16d + e = 566 \\)\n3. \\( Q(20) = 53 \\): \\( -2(20)^2 + 20d + e = 53 \\)\n4. Simplifies to: \\( -800 + 20d + e = 53 \\) ⟹ \\( 20d + e = 853 \\)\n\nSolving these equations:\n- Subtract the first equation from the second: \\( 4d = 287 \\) ⟹ \\( d = 71.75 \\)\n- Substitute \\( d \\) back into the first equation: \\( 16(71.75) + e = 566 \\) ⟹ \\( 1148 + e = 566 \\) ⟹ \\( e = -582 \\)\n\nThus, we have:\n- \\( P(0) = c = 698 \\)\n- \\( Q(0) = e = -582 \\)\n\nTherefore, the sum \\( P(0) + Q(0) = 698 - 582 = 116 \\).\n\nThe final answer is \\(\\boxed{116}\\).', 'studies/rlneurons/results/xreward/edits/permx1.5_math31-01/'], ['m23', 0, 0, False, 12737, '19', 'es from the center to vertices:**\n   - Using points \\( O(0, 0, 0) \\) and \\( E(0, 0, 4.5) \\), we find \\( c = \\frac{9}{4} \\).\n   - Using points \\( A(3, 3, 0) \\) and \\( B(-3, 3, 0) \\), we find \\( a + b = 1 \\).\n   - Using points \\( C(-3, -3, 0) \\), we encounter contradictions but proceed with \\( a = 0 \\), \\( b = 3 \\), and \\( c = \\frac{9}{4} \\).\n\n5. **Calculate the radius:**\n   - Distance from the center \\( (0, 3, \\frac{9}{4}) \\) to \\( O(0, 0, 0) \\):\n     \\[\n     \\sqrt{0^2 + 3^2 + \\left(\\frac{9}{4}\\right)^2} = \\sqrt{9 + \\frac{81}{16}} = \\sqrt{\\frac{225}{16}} = \\frac{15}{4}\n     \\]\n\n6. **Verify the radius:**\n   - The radius is confirmed to be \\( \\frac{15}{4} \\), so \\( m = 15 \\) and \\( n = 4 \\).\n\n7. **Sum \\( m + n \\):**\n   \\[\n   m + n = 15 + 4 = 19\n   \\]\n\nThus, the final answer is \\(\\boxed{19}\\).', 'studies/rlneurons/results/xreward/edits/permx1.5_math31-01/']]}, 'code': {}, 'problems': {'m0': ['AIME 2022', '116', 'Quadratic polynomials $P(x)$ and $Q(x)$ have leading coefficients $2$ and $-2,$ respectively. The graphs of both polynomials pass through the two points $(16,54)$ and $(20,53).$ Find $P(0) + Q(0).$'], 'm29': ['AIME 2022', '244', 'Let $\\ell_A$ and $\\ell_B$ be two distinct parallel lines. For positive integers $m$ and $n$, distinct points $A_1, A_2, \\allowbreak A_3, \\allowbreak \\ldots, \\allowbreak A_m$ lie on $\\ell_A$, and distinct points $B_1, B_2, B_3, \\ldots, B_n$ lie on $\\ell_B$. Additionally, when segments $\\overline{A_iB_j}$ are drawn for all $i=1,2,3,\\ldots, m$ and $j=1,\\allowbreak 2,\\allowbreak 3, \\ldots, \\allowbreak n$, no point strictly between $\\ell_A$ and $\\ell_B$ lies on more than 1 of the segments. Find the number of bounded regions into which this figure divides the plane when $m=7$ and $n=5$. The figure shows that there are 8 regions when $m=3$ and $n=2$.'], 'm23': ['AIME 2022', '021', 'A right square pyramid with volume $54$ has a base with side length $6.$ The five vertices of the pyramid all lie on a sphere with radius $\\frac mn$, where $m$ and $n$ are relatively prime positive integers. Find $m+n$.']}}
# EXAMPLES-PAIRS-END

_SRC = {"olympiadbench": "OlympiadBench", "aime2025": "AIME 2025", "aime2024": "AIME 2024", "aime2023": "AIME 2023",
        "aime2022": "AIME 2022", "amc23": "AMC 2023", "hmmt_feb2025": "HMMT February 2025"}
_EX_MATH = {  # cell: the run folder whose examples.json is shown (sample 1 where the cell has one, else sample 0)
    "base": R + "day1_3/hard328_base_cue_s4r2-01/", "all": R + "xreward/dial15_s4_vs_base_cue-01/",
    "L0": D3 + "top8x1.5_L0-10_math31_s1-01/", "L11": D3 + "top8x1.5_L11-21_math31_s1-01/",
    "L22": D3 + "top8x1.5_L22-31_math31_s1-01/", "d28": D3 + "top8x1.5_d2-8_math31_s1-01/",
    "randL0": D3 + "rand8x1.5_L0-10_math31_s1-01/", "rand": ED + "rand8x1.5_math31-01/",
    "top1": ED + "top1_math31-01/", "top1x2": ED + "top1x2_math31-01/", "top1x3": ED + "top1x3_math31-01/",
}
_EX_CODE = {
    "base": R + "code1/base_cue-01/", "rand": R + "xreward/code_dial/code_rand8x1.5_code31-01/",
    "L0": CD + "code_top8x1.5_L0-10_code31-01/", "L11": CD + "code_top8x1.5_L11-21_code31-01/",
    "L22": CD + "code_top8x1.5_L22-31_code31-01/", "all": R + "xreward/code_dial/code_top8x1.5_code31-01/",
}
_EX_PAIRS = {k: ED + _M[k]["cell"] + "-01/" for k in ("rin", "rout", "perm")}  # on the branch sharedsub only, for now


def _examples(math=_EX_MATH, code=_EX_CODE):
    """EXAMPLES rebuilt from the run folders: for the four-sample cells (base, all) the vote examples of problem 0 (right)
    and 29 (wrong) with one of their samples (Base + cue: sample 2 of problem 29, which is cut off); else the folder's right
    and wrong example (an example without a seed is from a one-sample cell: sample 0). The end of each answer is its last 800 characters (math) or 600 (code)."""
    hard = {p["index"]: p for p in json.load(open("studies/rlneurons/data/rln3/hard.json"))}
    probs, out = {}, {"math": {}, "code": {}}
    for cell, folder in math.items():
        ex = json.load(open(folder + "examples.json"))
        rows = []
        for kind in ("right", "wrong"):
            if "vote" in ex:
                e = ex["vote"][kind]
                a = next(a for a in e["attempts"] if a["sample"] == (1 if kind == "right" else 2)) if cell == "base" else e["attempts"][0]
                i, sample, text = e["problem_index"], a["sample"], a["text_last_2000"]
            else:
                a = ex[kind]
                i, sample, text = a["problem_index"], (a.get("seed", 3000000) - 3000000 - a["problem_index"] * ("seed" in a)) // 10000, a["answer_tail"]
            assert hard[i]["answer"] == (e if "vote" in ex else a)["gold"], (cell, kind)
            probs[f"m{i}"] = [_SRC[hard[i]["source"]], hard[i]["answer"], hard[i]["problem"]]
            rows.append([f"m{i}", sample, a["score_v3"], a["cap_hit"], a["n_new"], a["extracted_v3"], text[-800:], folder])
        out["math"][cell] = rows
    for cell, folder in code.items():
        ex = json.load(open(folder + "examples.json"))
        rows = []
        for a in sorted(ex, key=lambda a: not a["passed"]):
            body = re.search(r"signature and docstring:\n\n(.*?)\n\nRemember", a["prompt"], re.S).group(1)
            probs["c" + a["uid"]] = ["HumanEval+", None, body]
            rows.append(["c" + a["uid"], 0, int(a["passed"]), a["cap_hit"], a["n_new"], None, a["text"][-600:], folder])
        out["code"][cell] = rows
    out["problems"] = probs
    return out


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
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table with
   a cast shadow in place of the glow. The light comes from the upper left in both. RL's edit and its parts are lit (blue). */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --base-tone: #6b7882; --grid: rgba(16, 24, 32, .08);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --base-tone: #b7c2ca; --grid: rgba(255, 255, 255, .06);
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

/* The picture: one plate, the plane of the two jobs on its left and the readout on its right, the control under it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
.setrow { display: flex; align-items: center; flex-wrap: wrap; gap: 6px 16px; padding: 0 0 6px 2.4%; min-height: 38px; }
.sets { display: inline-flex; border: 1px solid var(--rule); border-radius: 999px; padding: 3px; }
.sets button { padding: 5px 13px; border-radius: 999px; font-weight: 560; font-size: 13px; color: var(--mute); white-space: nowrap; transition: background .15s ease, color .15s ease; }
.sets button:hover { color: var(--blue); }
.sets button[aria-pressed="true"] { background: var(--mute); color: var(--paper); }
.setcap { margin: 0; font-size: 13px; line-height: 1.4; color: var(--mute); max-width: 62ch; flex: 1 1 260px; }
svg { width: 100%; max-height: calc(100vh - 262px); display: block; overflow: visible; touch-action: pan-y; cursor: default; user-select: none; -webkit-user-select: none; }
svg:focus:not(:focus-visible) { outline: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.frame { fill: none; stroke: var(--faint); stroke-width: 1; opacity: .55; }
.grid { fill: none; stroke: var(--grid); stroke-width: 1; }
.tick { fill: var(--faint) !important; font-weight: 520; }
.title { fill: var(--mute) !important; font-weight: 600; }
.dir { fill: var(--ink) !important; font-weight: 640; }
.m { stroke-linecap: round; }
.m.whole { fill: var(--blue); }
.m.part { fill: var(--sheet); stroke: var(--blue); stroke-width: 2.2; }
.m.base { fill: var(--base-tone); }
.m.rand { fill: var(--sheet); stroke: var(--base-tone); stroke-width: 1.6; }
.mh { fill: var(--blue); fill-opacity: calc(var(--bloom) * .16); }
.dot { stroke: none; }
.dot.whole, .dot.part { fill: var(--blue); }
.dot.base, .dot.rand { fill: var(--base-tone); }
.bar { fill: none; stroke-linecap: round; stroke-width: 1.2; }
.bar.whole, .bar.part { stroke: var(--blue); }
.bar.base, .bar.rand { stroke: var(--base-tone); }
.ar { fill: none; stroke: var(--blue); stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.6; }
.ar.whole { stroke-width: 2.4; }
.arg { fill: none; stroke: var(--blue); stroke-linecap: round; stroke-width: 8; stroke-opacity: calc(var(--bloom) * .09); }
.ah { fill: var(--blue); stroke: none; }
.ml, .legt { paint-order: stroke; stroke: var(--glass); stroke-width: 3px; stroke-linejoin: round; stroke-opacity: .75; }  /* a label cuts the line it crosses */
.ml { font-weight: 560; fill: var(--mute) !important; }
.ml.part { fill: var(--blue) !important; font-weight: 620; }
.ml.whole { fill: var(--blue) !important; font-weight: 700; }
.ml.base { fill: var(--ink) !important; font-weight: 620; }
.leg { fill: none; stroke: var(--ink); stroke-width: 1.2; stroke-dasharray: 3 4; opacity: .75; }
.legt { font-weight: 680; fill: var(--ink) !important; }
.sel { fill: none; stroke: var(--ink); stroke-width: 1.6; }
.selh { fill: var(--blue); opacity: calc(var(--bloom) * .2); }
.big { font-weight: 660; letter-spacing: -.035em; font-stretch: 100%; }
.bigu { font-weight: 560; fill: var(--mute) !important; letter-spacing: -.01em; }
.lab { fill: var(--mute) !important; font-weight: 520; }
.lab.em { fill: var(--ink) !important; font-weight: 620; }
.keyt { fill: var(--mute) !important; font-weight: 520; }

/* The control: one switch of three groupings */
.control { align-self: center; display: flex; flex-direction: column; align-items: center; margin-top: 12px; }
.switch { display: inline-flex; border: 1px solid var(--ink); border-radius: 999px; padding: 3px; }
.switch button { padding: 7px 18px; border-radius: 999px; font-weight: 600; font-size: 14.5px; white-space: nowrap; transition: background .2s ease, color .2s ease, opacity .2s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button:disabled { opacity: .35; cursor: default; }
.switch button:disabled:hover { color: inherit; }
.hint { margin: 10px 0 0; font-size: 13.5px; color: var(--mute); text-align: center; max-width: 70ch; min-height: 2.8em; }

/* One drawn entrance, then only the slow sway and what the reader changes */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .axes { animation: fade .8s .3s both; }
.enter .key { animation: fade .8s .9s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.paper { margin: 18px 0 0; font-size: 15px; }
.paper a { color: var(--mute); text-decoration: none; border-bottom: 1px solid currentColor; padding-bottom: 1px; }
.paper a:hover, .paper a:focus-visible { color: inherit; }
.paper + .paper { margin-top: 10px; }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 0 6px 12px 0; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.lead.q { font-size: 15.5px; line-height: 1.45; color: var(--mute); max-width: 44ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.vals { list-style: none; margin: 16px 0 0; padding: 0; font-size: 14px; color: var(--mute); max-width: 44ch; }
.vals li { display: grid; grid-template-columns: 9.5em 1fr; align-items: baseline; gap: 12px; padding: 7px 0; border-top: 1px solid var(--rule); }
.vals b { color: var(--ink); font-weight: 650; }
.vals b.lit { color: var(--blue); }
.vals .no { color: var(--red); font-weight: 600; }
.vals .yes { color: var(--ink); font-weight: 600; }
.sub { margin: 18px 0 0; font-size: 13px; color: var(--mute); max-width: 44ch; }
.sub b { color: var(--ink); font-weight: 640; }
.ex { margin: 10px 0 0; padding: 10px 0 0; border-top: 1px solid var(--rule); max-width: 44ch; }
.exh { margin: 0; font-size: 13.5px; color: var(--ink); font-weight: 560; }
.exh .no { color: var(--red); } .exh .yes { color: var(--blue); }
.ex details { margin: 6px 0 0; font-size: 13px; color: var(--mute); }
.ex summary { cursor: pointer; color: var(--mute); }
.ex summary:hover { color: var(--ink); }
.ex .q { margin: 6px 0 0; line-height: 1.45; overflow-wrap: anywhere; }
.end { margin: 8px 0 0; font-size: 12.5px; line-height: 1.5; color: var(--mute); white-space: pre-wrap; overflow-wrap: anywhere; max-height: 15em; overflow-y: auto; padding-left: 10px; border-left: 2px solid var(--rule); }
.steps { display: flex; justify-content: space-between; margin-top: 16px; font-size: 13px; color: var(--mute); }
.steps button:hover { color: var(--ink); }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; display: block; }
  .setrow { padding: 0 0 8px; }
  .pane { order: 4; margin-top: 22px; }
  .paper { order: 5; }
  svg { max-height: none; }
  .control { width: 100%; }
  .switch { display: grid; grid-template-columns: 1fr 1fr; border-radius: 22px; width: 100%; }
  .switch button { text-align: center; white-space: normal; line-height: 1.2; padding: 8px 6px; font-size: 14px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .sets button, .more button, .top a { transition: none; }
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
    <div class="setrow">
      <div class="sets" role="group" aria-label="Which problems">
        <button data-set="math" aria-pressed="true">328 harder problems (math)</button>
        <button data-set="code" aria-pressed="false">538 code problems</button>
      </div>
      <p class="setcap" id="setcap"></p>
    </div>
    <svg id="svg" role="img" tabindex="0"></svg>
    <div class="control">
      <div class="switch" role="group" aria-label="Which parts of the edit">
        <button data-group="layers" aria-pressed="true">By layer</button>
        <button data-group="rank" aria-pressed="false">By direction</button>
        <button data-group="all" aria-pressed="false">All parts</button>
        <button data-group="pairs" aria-pressed="false">By pairing</button>
      </div>
      <p class="hint" id="hint"></p>
    </div>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
    <p class="paper"><a href="/finding/the-finish-dial">The finish dial: the whole edit at every size ›</a></p>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const ease = p => p < .5 ? 4 * p * p * p : 1 - (-2 * p + 2) ** 3 / 2, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const num = v => String(v).replace(/-/g, "−");
const mean = a => a.reduce((s, x) => s + x, 0) / a.length;
const fx = (x, d) => { const y = x * 10 ** d, t = Math.abs(y % 1); return Math.abs(t - .5) < 1e-9 ? (2 * Math.round(y / 2) / 10 ** d).toFixed(d) : x.toFixed(d); };

/* The cells (C.cells: key, label, name, what, kind, parent), and their numbers per problem set. */
const M = C.cells.map(([key, label, name, what, kind, parent], k) => ({ key, label, name, what, kind, parent, k }));
const IDX = Object.fromEntries(M.map(m => [m.key, m.k]));
const SETS = ["math", "code"], GROUPS = ["layers", "rank", "all", "pairs"], MATH_ONLY = ["rank", "pairs"];
const NS = { math: D.n, code: D.n_code };
const cell = (set, key) => D[set][key];
const NDOT = M.map(m => Math.max(...SETS.map(s => cell(s, m.key) ? cell(s, m.key).right.length : 0)));
const ORDER = ["rand", "base", "part", "whole"];  // drawn back to front
const groupOf = (set, group) => set === "code" && MATH_ONLY.includes(group) ? "layers" : group;
const shown = (set, group, key) => !!cell(set, key) && C.groups[groupOf(set, group)].includes(key);
const stateOf = () => S.set === "code" ? "code" : S.group;

/* The two axes, per set: x the answers cut off (fewer to the right), y the right answers. */
const AX = {
  math: { xd: [104, 0], xt: [100, 75, 50, 25, 0], yd: [147, 212], yt: [150, 160, 170, 180, 190, 200, 210],
    xl: "Cut off at 16,384 tokens, of 328", yl: "Right answers, of 328" },
  code: { xd: [40, 0], xt: [40, 30, 20, 10, 0], yd: [305, 410], yt: [320, 340, 360, 380, 400],
    xl: "Cut off at 16,384 tokens, of 538", yl: "Passed, of 538" },
};
/* Where a mark's label sits, per set (and per grouping where it must move): [dx, dy, anchor] in units of the small type. */
const LAB = {
  math: { base: [.9, 1.75, "start"], rand: [-1, .9, "end"], randL0: [-1, -.45, "end"], L0: [.6, -1.25, "middle"],
    L11: [.9, 1.15, "start"], L22: [.95, .35, "start"], d28: [0, -1.25, "middle"], top1: [-1, .35, "end"],
    top1x2: [0, -1.25, "middle"], top1x3: [.95, .35, "start"], all: [-1, -.95, "end"],
    rin: [-.6, 1.5, "end"], rout: [-.9, -.7, "end"], perm: [.95, .35, "start"] },
  code: { base: [.95, .35, "start"], rand: [0, -1.2, "middle"], L0: [-1, -.7, "end"], L11: [.95, .35, "start"],
    L22: [-.2, -1.25, "end"], all: [-1, -.95, "end"] },
  "math/pairs": { rand: [-1, -.2, "end"] },  // in the pairing state the random edit's label moves up, out of the way of RL's inputs only
};
const labAt = (set, group, key) => S.g && S.g.phone && key === "randL0" ? null : (LAB[set + "/" + group] || {})[key] || LAB[set][key] || null;  // on a phone the key names the controls

/* Geometry: the plate and the chart in a small 3D space around the plate's centre (x right, y down, z toward the viewer).
   The chart on the left, the readout on the right (on a phone, the readout above the chart). */
function geo() {
  const ph = narrow.matches;
  const g = ph
    ? { w: 480, h: 970, cx: 240, D: 2400, r: 22, deep: 30, blur: 12, X0: 70, X1: 446, Y0: 392, Y1: 716, fs: 18, fsm: 17, fb: 76,
        mr: 1.3, rx: 30, bigY: 102, uY: [140, 164], lY: [206, 231, 256, 281, 306], ylY: 362, tickY: 746, titleY: 778,
        key: { y: 828, cols: 2 }, hit: 26, phone: true }
    : { w: 1000, h: 640, cx: 500, D: 2200, r: 30, deep: 40, blur: 16, X0: 96, X1: 600, Y0: 76, Y1: 478, fs: 15, fsm: 13,
        fb: 84, mr: 1, rx: 648, bigY: 178, uY: [212, 232], lY: [278, 302, 326, 350, 374], ylY: 52, tickY: 502, titleY: 532,
        key: { y: 588, cols: 5 }, hit: 18 };
  g.cy = g.h / 2;
  g.a = ph ? [6, 8, g.w - 6, g.h - 8] : [24, 18, g.w - 24, g.h - 18];
  g.X = (set, x) => { const d = AX[set].xd; return g.X0 + (clamp(x, Math.min(...d), Math.max(...d)) - d[0]) / (d[1] - d[0]) * (g.X1 - g.X0); };
  g.Y = (set, y) => { const d = AX[set].yd; return g.Y1 - (clamp(y, d[0], d[1]) - d[0]) / (d[1] - d[0]) * (g.Y1 - g.Y0); };
  return g;
}
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z) {
  const X = x - g.cx, Y = y - g.cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, g.cy + y1 * k];
}
function rounded(g, [x0, y0, x1, y1], r, z) {  // a rounded rectangle at depth z
  const p = [], corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}
const line = pts => pts.length ? "M" + pts.map(q => f(q[0]) + " " + f(q[1])).join("L") : "";
const KEY = [["whole", "RL's whole edit"], ["part", "A part of it"], ["base", "Base + cue, random"], ["dot", "One sample"], ["bar", "95 % interval"]];
const RADIUS = { whole: 8, part: 6.2, base: 6.2, rand: 5 };

const S = { set: "math", group: "layers", pset: "math", t0: -1e9, dur: 820, stag: 120, open: null, g: null, el: {}, shown: {},
  from: [], to: [], rank: [], scr: [], ops: [], last: 0, t: 0, keyX: [], rise: false };

function build() {
  const g = S.g = geo(), svg = $("svg"), [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  const axes = SETS.map(s => { const A = AX[s]; return `<g id="ax-${s}" opacity="0"><path class="grid" id="gr-${s}"/>` +
    A.yt.map((v, i) => `<text class="tick" id="ty-${s}-${i}" font-size="${g.fsm}" text-anchor="end">${v}</text>`).join("") +
    A.xt.map((v, i) => `<text class="tick" id="tx-${s}-${i}" font-size="${g.fsm}" text-anchor="middle">${v}</text>`).join("") +
    `<text class="title" id="yl-${s}" font-size="${g.fsm}"><tspan class="dir">↑</tspan> ${esc(A.yl)}</text>` +
    `<text class="title" id="xl-${s}" font-size="${g.fsm}" text-anchor="end">${esc(A.xl)} · <tspan class="dir">fewer →</tspan></text></g>`; }).join("");
  const order = M.map(m => m.k).sort((a, b) => ORDER.indexOf(M[a].kind) - ORDER.indexOf(M[b].kind));
  const arrows = M.filter(m => m.kind === "part" || m.kind === "whole").map(m =>
    (m.kind === "whole" ? `<path class="arg" id="ag${m.k}"/>` : "") + `<path class="ar ${m.kind}" id="ar${m.k}"/><path class="ah" id="ah${m.k}"/>`).join("");
  const bars = M.map(m => `<path class="bar ${m.kind}" id="bv${m.k}"/><path class="bar ${m.kind}" id="bh${m.k}"/>`).join("");
  const dots = M.map(m => Array.from({ length: NDOT[m.k] }, (_, j) => `<circle class="dot ${m.kind}" id="d${m.k}-${j}" r="${f(2.3 * g.mr)}"/>`).join("")).join("");
  const marks = order.map(k => { const m = M[k], r = RADIUS[m.kind] * g.mr;
    return (m.kind === "whole" ? `<circle class="mh" id="mh${k}" r="${f(r * 2.3)}"/>` : "") + `<circle class="m ${m.kind}" id="m${k}" r="${f(r)}"/>`; }).join("");
  const labels = M.map(m => `<text class="ml ${m.kind}" id="ml${m.k}" font-size="${g.fsm}">${esc(m.label)}</text>`).join("");
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${f(g.cy)}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .04)}" width="${aw}" height="${f(ah)}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .3)}" cy="${f(ay0 + ah * .24)}" rx="${f(aw * .3)}" ry="${f(ah * .2)}" transform="rotate(-14 ${f(ax0 + aw * .3)} ${f(ay0 + ah * .24)})" fill="url(#spec)"/>` +
    `<g class="axes"><path class="frame" id="frame"/>${axes}</g>` +
    `<g class="data">${arrows}${bars}${dots}<path class="leg" id="legh"/><path class="leg" id="legv"/>` +
    `<circle class="selh" id="selh" r="0"/>${marks}<circle class="sel" id="sel" r="0"/>${labels}` +
    `<text class="legt" id="lgh" font-size="${g.fsm}" text-anchor="middle"></text><text class="legt" id="lgv" font-size="${g.fsm}"></text></g>` +
    `<g class="read"><text class="big" id="big" font-size="${g.fb}"></text><text class="bigu" id="bigu" font-size="${f(g.fb * .3)}"></text>` +
    `<text class="lab em" id="u0" font-size="${g.fs}"></text><text class="lab em" id="u1" font-size="${g.fs}"></text>` +
    [0, 1, 2, 3, 4].map(i => `<text class="lab" id="l${i}" font-size="${g.fs * .92}"></text>`).join("") + `</g>` +
    `<g class="key">${KEY.map(([kind, t], i) => keyGlyph(kind, i, g) + `<text class="keyt" id="kt${i}" font-size="${g.fsm}">${esc(t)}</text>`).join("")}</g>`;
  S.el = {}; S.shown = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  measureKey();
}
function keyGlyph(kind, i, g) {
  if (kind === "dot") return `<circle class="dot part" id="kg${i}" r="${f(2.3 * g.mr)}"/>`;
  if (kind === "bar") return `<path class="bar part" id="kg${i}"/>`;
  return `<circle class="m ${kind}" id="kg${i}" r="${f(RADIUS[kind] * g.mr)}"/>`;
}
function measureKey() {  // the key's entries centred in rows: one row on a desktop, rows of at most 3 on a phone
  const g = S.g, K = g.key, gap = 22 * g.mr, w = KEY.map((_, i) => (S.el["kt" + i].getComputedTextLength() || 110) + 14 * g.mr + gap);
  S.keyX = [];
  for (let i0 = 0, row = 0; i0 < KEY.length; i0 += K.cols, row++) {
    const ws = w.slice(i0, i0 + K.cols), total = ws.reduce((a, b) => a + b, 0) - gap;
    let x = (g.w - total) / 2 + 6 * g.mr;
    ws.forEach(wi => { S.keyX.push([x, K.y + row * 32]); x += wi; });
  }
}

/* The target of every mark in a state: its place, whether it is shown, its sample dots and the ends of its interval bars
   (offsets from the mark in chart units). A hidden mark sits at its nearest shown ancestor (finally Base + cue). */
function target(set, group) {
  const g = S.g, n = NS[set];
  const P = M.map(m => { const c = cell(set, m.key); return c ? [g.X(set, mean(c.cut)), g.Y(set, mean(c.right))] : null; });
  const vis = M.map(m => shown(set, group, m.key));
  const home = k => { for (let m = M[k]; m; m = m.parent ? M[IDX[m.parent]] : null) if (vis[m.k]) return P[m.k]; return P[IDX.base]; };
  return M.map((m, k) => {
    const c = cell(set, m.key), p = vis[k] ? P[k] : home(k);
    const iv = c && vis[k] ? (c.vs_base || c.vs_ref || {}) : {};
    const off = (v, axis) => v ? (axis === "y" ? [g.Y(set, mean(c.right) + (v[1] - v[0]) * n / 100) - P[k][1], g.Y(set, mean(c.right) + (v[2] - v[0]) * n / 100) - P[k][1]]
      : [g.X(set, mean(c.cut) + (v[1] - v[0]) * n / 100) - P[k][0], g.X(set, mean(c.cut) + (v[2] - v[0]) * n / 100) - P[k][0]]) : [0, 0];
    return { p, o: vis[k] ? 1 : 0, bv: off(iv.right, "y"), bh: off(iv.cut, "x"), bo: [iv.right ? 1 : 0, iv.cut ? 1 : 0],
      s: Array.from({ length: NDOT[k] }, (_, j) => c && vis[k] && j < c.right.length ? [g.X(set, c.cut[j]), g.Y(set, c.right[j]), 1] : [p[0], p[1], 0]) };
  });
}

/* Where each mark is in its change: it travels from its old place to its new one along an eased path, lifting toward the
   viewer on the way; the parts start one after another in the order of their grouping (120 ms apart) and take 0.82 s,
   so each arrow draws itself out of Base + cue. */
function markAt(k, now) {
  const p = clamp((now - S.t0 - S.stag * S.rank[k]) / S.dur, 0, 1), e = ease(p), a = S.from[k], b = S.to[k];
  const moved = a.p[0] !== b.p[0] || a.p[1] !== b.p[1];
  const lerp2 = (u, v) => [mix(u[0], v[0], e), mix(u[1], v[1], e)];
  return { x: mix(a.p[0], b.p[0], e), y: mix(a.p[1], b.p[1], e), z: moved ? 24 * Math.sin(Math.PI * p) : 0,
    o: mix(a.o, b.o, clamp(b.o > a.o ? e * 1.6 : e * 1.25, 0, 1)), bv: lerp2(a.bv, b.bv), bh: lerp2(a.bh, b.bh),
    bo: lerp2(a.bo, b.bo), s: a.s.map((q, j) => [mix(q[0], b.s[j][0], e), mix(q[1], b.s[j][1], e), mix(q[2], b.s[j][2], e)]) };
}
const fmtBig = (R, x) => `${x > 0 && R.unit === " points" ? "+" : ""}${num(x.toFixed(R.dec))}`;

function place(t, now) {
  const g = S.g, E = S.el, at = (el, q, dy) => { el.setAttribute("x", f(q[0])); el.setAttribute("y", f(q[1] + (dy || 0))); };
  const text = (id, v) => { if (S.shown[id] !== v) { E[id].textContent = S.shown[id] = v; } };
  const P = (x, y, z = 6) => proj(g, x, y, z);
  const op = (el, v) => { const s = v.toFixed(3); if (el._o !== s) { el.style.opacity = s; el._o = s; } };
  E.back.setAttribute("d", rounded(g, g.a, g.r, -g.deep));
  E.plate.setAttribute("d", rounded(g, g.a, g.r, 0));
  E.frame.setAttribute("d", line([P(g.X0, g.Y0 - 8), P(g.X0, g.Y1), P(g.X1 + 8, g.Y1)]));
  const e = ease(clamp((now - S.t0) / 700, 0, 1));
  const aop = s => s === S.set ? (S.pset === s ? 1 : clamp(2 * e - 1, 0, 1)) : s === S.pset ? clamp(1 - 2 * e, 0, 1) : 0;  // the old axes go, then the new come

  // The axes of each set cross-fade; only a visible one is placed.
  SETS.forEach(s => {
    const o = aop(s), A = AX[s], G = E["ax-" + s];
    if (S.shown["o" + s] !== o.toFixed(3)) { G.setAttribute("opacity", o.toFixed(3)); S.shown["o" + s] = o.toFixed(3); }
    if (o < .005) return;
    E["gr-" + s].setAttribute("d", A.yt.map(y => line([P(g.X0, g.Y(s, y), 4), P(g.X1, g.Y(s, y), 4)])).join("") +
      A.xt.map(x => line([P(g.X(s, x), g.Y0, 4), P(g.X(s, x), g.Y1, 4)])).join(""));
    A.yt.forEach((y, i) => at(E[`ty-${s}-${i}`], P(g.X0 - 10, g.Y(s, y)), g.fsm * .35));
    A.xt.forEach((x, i) => at(E[`tx-${s}-${i}`], P(g.X(s, x), g.tickY)));
    at(E["yl-" + s], P(g.X0 - (g.phone ? 50 : 60), g.ylY));
    at(E["xl-" + s], P(g.X1 + 8, g.titleY));
  });

  // The marks, their sample dots, interval bars and labels.
  const sel = S.open != null && IDX[S.open] != null && shown(S.set, S.group, S.open) ? IDX[S.open] : -1;
  const Q = M.map((m, k) => markAt(k, now));
  M.forEach((m, k) => {
    const q = Q[k], s = P(q.x, q.y, 8 + q.z), c = E["m" + k], dim = sel >= 0 && sel !== k ? .25 : 1;
    S.scr[k] = s; S.ops[k] = q.o;
    c.setAttribute("cx", f(s[0])); c.setAttribute("cy", f(s[1])); op(c, q.o * dim);
    if (E["mh" + k]) { E["mh" + k].setAttribute("cx", f(s[0])); E["mh" + k].setAttribute("cy", f(s[1])); op(E["mh" + k], q.o * dim); }
    q.s.forEach((d, j) => { const el = E[`d${k}-${j}`], ds = P(d[0], d[1], 7 + q.z * .6);
      el.setAttribute("cx", f(ds[0])); el.setAttribute("cy", f(ds[1])); op(el, d[2] * q.o * (m.kind === "base" || m.kind === "rand" ? .55 : .6) * dim); });
    const bw = 4 * g.mr, bo = (sel === k ? 1 : m.kind === "base" || m.kind === "rand" ? 0 : .5) * q.o * dim;
    const v0 = P(q.x, q.y + q.bv[0], 7), v1 = P(q.x, q.y + q.bv[1], 7), h0 = P(q.x + q.bh[0], q.y, 7), h1 = P(q.x + q.bh[1], q.y, 7);
    E["bv" + k].setAttribute("d", `M${f(v0[0] - bw)} ${f(v0[1])}H${f(v0[0] + bw)}M${f(v0[0])} ${f(v0[1])}L${f(v1[0])} ${f(v1[1])}M${f(v1[0] - bw)} ${f(v1[1])}H${f(v1[0] + bw)}`);
    E["bh" + k].setAttribute("d", `M${f(h0[0])} ${f(h0[1] - bw)}V${f(h0[1] + bw)}M${f(h0[0])} ${f(h0[1])}L${f(h1[0])} ${f(h1[1])}M${f(h1[0])} ${f(h1[1] - bw)}V${f(h1[1] + bw)}`);
    op(E["bv" + k], bo * q.bo[0]); op(E["bh" + k], bo * q.bo[1]);
    // a label shown in both states slides to its new side; one shown in one state only fades with its mark
    const L = E["ml" + k], a = labAt(S.pset, S.pgroup, m.key), b = labAt(S.set, S.group, m.key) || a;
    if (!b) { op(L, 0); return; }
    const pos = a && b ? [mix(a[0], b[0], e), mix(a[1], b[1], e)] : b;
    L.setAttribute("text-anchor", (e < .5 && a ? a : b)[2]);
    at(L, [s[0] + pos[0] * g.fsm, s[1] + pos[1] * g.fsm]);
    op(L, clamp((q.o - .35) / .65, 0, 1) * dim);
  });

  // The arrows: from the parent's mark to the cell's, ending at the rim of the cell's mark.
  M.forEach((m, k) => {
    if (!E["ar" + k]) return;
    const a = S.scr[IDX[m.parent]], b = S.scr[k], dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy);
    const o = Math.min(S.ops[IDX[m.parent]], S.ops[k]) * (sel >= 0 && sel !== k ? .25 : 1);
    const r0 = (RADIUS[M[IDX[m.parent]].kind] + 3) * g.mr, r1 = (RADIUS[m.kind] + 3.5) * g.mr;
    if (L < r0 + r1 + 6 || o < .01) { op(E["ar" + k], 0); op(E["ah" + k], 0); if (E["ag" + k]) op(E["ag" + k], 0); return; }
    const ux = dx / L, uy = dy / L, p0 = [a[0] + ux * r0, a[1] + uy * r0], p1 = [b[0] - ux * r1, b[1] - uy * r1], hl = 8 * g.mr, hw = 3.6 * g.mr;
    const d = `M${f(p0[0])} ${f(p0[1])}L${f(p1[0] - ux * hl * .6)} ${f(p1[1] - uy * hl * .6)}`;
    E["ar" + k].setAttribute("d", d); op(E["ar" + k], o * .9);
    if (E["ag" + k]) { E["ag" + k].setAttribute("d", d); op(E["ag" + k], o); }
    E["ah" + k].setAttribute("d", `M${f(p1[0])} ${f(p1[1])}L${f(p1[0] - ux * hl - uy * hw)} ${f(p1[1] - uy * hl + ux * hw)}L${f(p1[0] - ux * hl + uy * hw)} ${f(p1[1] - uy * hl - ux * hw)}Z`);
    op(E["ah" + k], o);
  });

  // The selected cell: a ring, and its move from Base + cue split into the two jobs (sideways: cut-offs, up: right answers).
  if (sel >= 0) {
    const s = S.scr[sel], b = S.scr[IDX.base], m = M[sel], c = cell(S.set, m.key);
    E.sel.setAttribute("cx", f(s[0])); E.sel.setAttribute("cy", f(s[1])); E.sel.setAttribute("r", f((RADIUS[m.kind] + 6) * g.mr));
    E.selh.setAttribute("cx", f(s[0])); E.selh.setAttribute("cy", f(s[1]));
    E.selh.setAttribute("r", f(g.mr * (still.matches ? 18 : 18 + 2.5 * Math.sin(t * 1.6))));
    const legs = m.key !== "base" && S.ops[sel] > .5;
    E.legh.setAttribute("d", legs ? line([b, [s[0], b[1]]]) : ""); E.legv.setAttribute("d", legs ? line([[s[0], b[1]], s]) : "");
    // the legs are the drawn move from the mean of Base + cue; where the readout pairs the cell with it, the same number
    const n = NS[S.set], dr = 100 * (mean(c.right) - mean(cell(S.set, "base").right)) / n, dc = 100 * (mean(c.cut) - mean(cell(S.set, "base").cut)) / n;
    const sg = x => num((x > 0 ? "+" : "") + fx(x, 1));
    text("lgh", legs ? `${sg(dc)} points cut off` : ""); text("lgv", legs ? `${sg(dr)} points right` : "");
    at(E.lgh, [(b[0] + s[0]) / 2, b[1] + g.fsm * 1.45]);
    const right = s[0] < g.X0 + 120;
    E.lgv.setAttribute("text-anchor", right ? "start" : "end");
    at(E.lgv, [s[0] + (right ? 1 : -1) * g.fsm * .7, (b[1] + s[1]) / 2 + g.fsm * .35]);
    const room = 3 * g.fsm;  // a leg too short to hold its number shows the leg only (the side column has the number)
    [E.legh, E.legv].forEach(el => op(el, legs ? 1 : 0));
    op(E.lgh, legs && Math.abs(s[0] - b[0]) > room ? 1 : 0); op(E.lgv, legs && Math.abs(s[1] - b[1]) > room ? 1 : 0);
  } else {
    E.sel.setAttribute("r", "0"); E.selh.setAttribute("r", "0");
    [E.legh, E.legv, E.lgh, E.lgv].forEach(el => op(el, 0));
  }

  // The readout: the words of the state arrive with its number, which counts from 0 and stops within 0.9 s.
  const R = C.read[stateOf()], pc = ease(clamp((now - S.t0 - (S.rise ? 600 : 100)) / 900, 0, 1));
  text("big", fmtBig(R, R.big * pc)); text("bigu", R.unit.trim());
  at(E.big, P(g.rx, g.bigY, 10));
  at(E.bigu, P(g.rx + 12 + E.big.getComputedTextLength(), g.bigY, 10));
  text("u0", R.u[0]); text("u1", R.u[1]);
  const wo = clamp(pc * 2.5, 0, 1);  // the words of the new state arrive with its number
  ["u0", "u1", "l0", "l1", "l2", "l3", "l4", "bigu"].forEach(id => op(E[id], wo));
  at(E.u0, P(g.rx + 4, g.uY[0], 10)); at(E.u1, P(g.rx + 4, g.uY[1], 10));
  [0, 1, 2, 3, 4].forEach(i => { text("l" + i, R.lines[i] || ""); at(E["l" + i], P(g.rx + 4, g.lY[i], 10)); });

  // The key.
  KEY.forEach(([kind], i) => { const [x, y] = S.keyX[i], c = P(x, y, 6), tt = P(x + 14 * g.mr, y, 6), el = E["kg" + i];
    if (kind === "bar") { const bw = 4 * g.mr; el.setAttribute("d", `M${f(c[0] - bw)} ${f(c[1] - 7 * g.mr)}H${f(c[0] + bw)}M${f(c[0])} ${f(c[1] - 7 * g.mr)}V${f(c[1] + 7 * g.mr)}M${f(c[0] - bw)} ${f(c[1] + 7 * g.mr)}H${f(c[0] + bw)}`); }
    else { el.setAttribute("cx", f(c[0])); el.setAttribute("cy", f(c[1])); }
    at(E["kt" + i], tt, g.fsm * .35); });
}

/* Always on: the plate sways by a few degrees and leans toward the mouse. About 30 frames a second. With reduced motion
   the page shows one still frame per state. */
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 30) return;
  S.last = now;
  const t = S.t = now / 1000;
  V.px += (V.tx - V.px) * .1; V.py += (V.ty - V.py) * .1;
  aim(4 * Math.sin(t * .13) + 3.5 * V.px, 2 * Math.sin(t * .09) - 2 * V.py);
  place(t, now);
}

function setState(set, group, opts = {}) {
  const now = performance.now(), quick = still.matches || opts.instant;
  if (set === "code" && MATH_ONLY.includes(group)) group = "layers";
  const cur = quick || !S.to.length ? null : M.map((_, k) => markAt(k, now));
  S.to = target(set, group);
  const base = S.to[IDX.base];
  S.from = cur ? cur.map(q => ({ p: [q.x, q.y], o: q.o, bv: q.bv, bh: q.bh, bo: q.bo, s: q.s }))
    : opts.rise && !quick ? S.to.map((b, k) => k === IDX.base || M[k].kind === "rand" ? b
      : { p: base.p.slice(), o: 0, bv: [0, 0], bh: [0, 0], bo: [0, 0], s: b.s.map(() => [base.p[0], base.p[1], 0]) })
    : S.to;
  // the order of travel: Base + cue and the random controls first, then the parts in the order of their grouping
  const list = C.groups[groupOf(set, group)];
  M.forEach((m, k) => { const i = list.indexOf(m.key); S.rank[k] = i < 0 || m.kind === "base" || m.kind === "rand" ? 0 : i - 1; });
  S.rise = !!opts.rise && !quick;
  S.dur = S.rise ? 980 : 820; S.stag = S.rise ? 190 : 120;
  S.pset = quick ? set : S.set; S.pgroup = quick ? group : S.group; S.set = set; S.group = group;
  S.t0 = quick ? -1e9 : now + (S.rise ? 450 : 0);
  document.querySelectorAll("[data-group]").forEach(b => {
    b.setAttribute("aria-pressed", b.dataset.group === group);
    b.disabled = set === "code" && MATH_ONLY.includes(b.dataset.group);
    b.title = b.disabled ? "Not run on the code problems" : "";
  });
  document.querySelectorAll("[data-set]").forEach(b => b.setAttribute("aria-pressed", b.dataset.set === set));
  const st = stateOf();
  if (S.shown.hint !== st) {
    S.shown.hint = st; $("hint").textContent = C.hint[st]; $("setcap").textContent = C.setcap[set];
    if (!quick) [$("hint"), $("setcap")].forEach(el => el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 500, easing: "ease-out" }));
  }
  const R = C.read[st];
  $("svg").setAttribute("aria-label", `${AX[set].yl} against answers cut off, one mark per edit. ${fmtBig(R, R.big)}${R.unit} ${R.u.join(" ")} ` +
    `${R.lines.join(". ")}. Arrow keys change the grouping; Enter opens the first part.`);
  if (still.matches) { aim(0, 0); place(0, now); }
}

/* The side column: the five panels, or one cell. */
const sg = (x, d = 1) => num((x > 0 ? "+" : "") + fx(x, d));
const ivs = v => `${sg(v[0])} points (95 % interval ${num(fx(v[1], 1))} to ${num(fx(v[2], 1))})`;
const each = xs => xs.length > 1 ? ` · ${xs.join(", ")}` : "";
const tok = n => n.toLocaleString("en-US");
function exHtml(e) {
  const [pk, sample, score, cut, n, ans, tail] = e, P = C.ex.problems[pk], code = pk[0] === "c";
  const head = code ? `${esc(pk.slice(1))}, sample ${sample + 1}` : `328 harder problems, problem ${esc(pk.slice(1))} (${esc(P[0])}), sample ${sample + 1}`;
  const res = cut ? `<span class="no">cut off at 16,384 tokens</span>` : code ? (score ? `<span class="yes">passed</span>` : `<span class="no">failed</span>`)
    : score ? `<span class="yes">answer <span data-math>${esc(ans)}</span>, right</span>` : `<span class="no">answer <span data-math>${esc(ans ?? "none")}</span>, wrong (reference <span data-math>${esc(P[1])}</span>)</span>`;
  return `<div class="ex"><p class="exh">${head}: ${res}${cut ? "" : `, ${tok(n)} tokens`}</p>` +
    `<details><summary>The problem</summary><p class="q"${code ? "" : " data-math"}>${esc(P[2])}</p></details>` +
    `<p class="end"${code ? "" : " data-math"}>…${esc(tail)}</p></div>`;
}
function cellPane(j) {
  const m = M[j], set = S.set, c = cell(set, m.key), n = NS[set], code = set === "code", b = cell(set, "base");
  const R = mean(c.right), X = mean(c.cut), lit = m.kind === "part" || m.kind === "whole" ? "lit" : "";
  const keep = !code && C.keep[m.key];
  const rows = [
    ...(keep ? [["Kept from RL", esc(keep[0])], ["Replaced", esc(keep[1])]] : []),
    ["Samples", `${c.right.length} answer${c.right.length > 1 ? "s" : ""} per problem`],
    [code ? `Passed, of ${n}` : `Right, of ${n}`, `<b class="${lit}">${R % 1 ? R.toFixed(R * 4 % 1 ? 2 : 1) : R}</b>${c.right.length > 1 ? " mean" : ""}${each(c.right)}`],
    ["Cut off", `<b>${X % 1 ? fx(X, 1) : X}</b>${c.cut.length > 1 ? " mean" : ""}${each(c.cut)}`],
  ];
  if (code) rows.push(["No code block", `${c.no_block}`]);
  else rows.push(["Right per finished", (R / (n - X)).toFixed(2)]);
  const vs = (lab, v) => { if (!v) return; rows.push([lab, (v.right ? `right ${ivs(v.right)}` : "") + (v.cut ? `; cut off ${ivs(v.cut)}` : "")]); };
  if (m.key !== "base") {
    vs("Against Base + cue", c.vs_base);
    if (c.vs_ref) vs(`Against Base + cue (another answer: ${D.base_t1.right} right, ${D.base_t1.cut} cut off)`, c.vs_ref);
    vs(m.key === "L0" && !code ? "Against random, same layers" : "Against the random edit", c.vs_random);
    vs("Against 8 random directions at size 1", c.vs_random1);
    vs("Against the whole edit", c.vs_all);
    vs(`Against RL's 8 directions, same seed (${D.all_t1.right} right, ${D.all_t1.cut} cut off)`, c.vs_all8);
    if (c.shift) rows.push(["Shift at layer 24", `<b>${c.shift.toFixed(2)}</b> RMS, against ${D.all_t1.shift.toFixed(2)} for the intact pairs: ${Math.round(D.all_t1.shift / c.shift)} times less`]);
  }
  (c.pred || []).forEach(p => { const [txt, held] = D.pred[p];
    rows.push([`Prediction ${p}`, `${esc(txt)} <span class="${held ? "yes" : "no"}">${held ? "Held" : "Refuted"}.</span>`]); });
  const ex = (C.ex[set] || {})[m.key] || [];
  const what = code ? C.codewhat[m.key] : m.what;
  return `<div><div class="dhead"><h2>${esc(m.name)}</h2><button class="close" data-open="">Close</button></div>` +
    `<p class="lead q">${esc(what)}</p>` +
    `<ul class="vals">${rows.map(([a, v]) => `<li><span>${a}</span><span>${v}</span></li>`).join("")}</ul>` +
    `<p class="sub">${code ? `Base + cue: ${b.right[0]} passed, ${b.cut[0]} cut off. 538 code problems (HumanEval+ and MBPP+), Code cue, T 1.0, cut off at 16,384 tokens.`
      : `Base + cue: ${mean(b.right)} right, ${mean(b.cut)} cut off, mean of ${b.right.length} samples. 328 harder problems, T 1.0, cut off at 16,384 tokens; points are of 328, paired over the problems.`}</p>` +
    (c.shift ? `<p class="paper"><a href="/finding/rl-directions-move-activations#${esc(c.cell)}">The same edit in the activations ›</a></p>` : "") +
    (ex.length ? `<p class="sub"><b>Two answers from the run folder</b>, the end of each:</p>${ex.map(exHtml).join("")}` : "") +
    `<div class="steps"><button data-step="-1">‹ Previous</button><button data-step="1">Next ›</button></div></div>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open), j = S.open != null && IDX[S.open] != null ? IDX[S.open] : -1;
  $("pane").innerHTML = j >= 0 ? cellPane(j) : p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>` + p.slice(4).map(l => `<p class="paper"><a href="${esc(l[0])}">${esc(l[1])}</a></p>`).join("")
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
/* The set, the grouping and what is open are one value in the address: #[code/][rank/|all/|pairs/][<panel>|<cell key>]. */
function address(push) {
  const parts = [S.set === "code" ? "code" : "", S.group === "layers" ? "" : S.group, S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
const visibleCell = key => IDX[key] != null && shown(S.set, S.group, key);
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const set = parts.includes("code") ? "code" : "math", group = GROUPS.find(v => parts.includes(v)) || "layers";
  const o = parts.find(x => C.panels.some(p => p[0] === x) || IDX[x] != null) || null;
  if (first === true) setState(set, group, { instant: set !== "math" || group !== "layers" || !!o, rise: set === "math" && group === "layers" && !o });
  else if (set !== S.set || group !== S.group) setState(set, group);
  S.open = o && IDX[o] != null && !visibleCell(o) ? null : o;
  pane();
  if (still.matches) place(0, performance.now());
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "start" }); };
function open(key) {
  const was = S.open;
  S.open = key || null;
  address(true);
  pane();
  if (still.matches) place(0, performance.now());
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  else if (!key) $("svg").focus({ preventScroll: true });
}
function go(set, group) {
  if (set === S.set && group === S.group) return;
  setState(set, group);
  if (S.open && IDX[S.open] != null) { if (!visibleCell(S.open)) S.open = null; pane(); }  // a cell the new state hides is closed
  address(false);
}

const svg = $("svg");
function svgPoint(e) { const m = svg.getScreenCTM().inverse(); return [m.a * e.clientX + m.c * e.clientY + m.e, m.b * e.clientX + m.d * e.clientY + m.f]; }
function nearest([x, y]) {
  let best = -1, bd = S.g.hit ** 2;
  S.scr.forEach((q, k) => { if (S.ops[k] < .5) return; const d = (q[0] - x) ** 2 + (q[1] - y) ** 2; if (d < bd) { bd = d; best = k; } });
  return best;
}
svg.addEventListener("pointermove", e => { if (e.pointerType === "mouse") svg.style.cursor = nearest(svgPoint(e)) >= 0 ? "pointer" : "default"; });
svg.addEventListener("click", e => { const k = nearest(svgPoint(e)); if (k >= 0) { open(M[k].key); show(); } });
document.addEventListener("click", e => {
  const gb = e.target.closest("[data-group]"), sb = e.target.closest("[data-set]"), o = e.target.closest("[data-open]"), s = e.target.closest("[data-step]");
  if (gb && !gb.disabled) go(S.set, gb.dataset.group);
  if (sb) go(sb.dataset.set, S.group);
  if (o) open(o.dataset.open);
  if (s) {
    const vis = M.filter(m => visibleCell(m.key)), i = vis.findIndex(m => m.key === S.open);
    open(vis[(i + Number(s.dataset.step) + vis.length) % vis.length].key);
    $("pane").querySelector(`[data-step="${s.dataset.step}"]`).focus({ preventScroll: true });
  }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey || /INPUT|TEXTAREA|SUMMARY/.test(document.activeElement.tagName)) return;
  if (e.key === "Escape" && S.open) open("");
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
    const gs = S.set === "code" ? ["layers", "all"] : GROUPS, i = Math.max(0, gs.indexOf(S.group));
    go(S.set, gs[(i + (e.key === "ArrowRight" ? 1 : gs.length - 1)) % gs.length]);
  }
  if (e.key === "Enter" && document.activeElement === svg) { e.preventDefault(); open(M.find(m => visibleCell(m.key)).key); show(); }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); setState(S.set, S.group, { instant: true }); place(S.t, performance.now()); });
still.addEventListener("change", () => { if (still.matches) { setState(S.set, S.group, { instant: true }); aim(0, 0); place(0, performance.now()); } });
document.fonts.ready.then(() => { measureKey(); S.shown = { hint: S.shown.hint }; place(S.t, performance.now()); });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1; V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
build();
aim(0, 0);
fromHash(true);
place(0, performance.now());
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
"""

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's plane reduced to a
# glass slab with Base + cue as a plain dot in its lower left corner, one lit arrow going up (right answers), one plain
# arrow going right (fewer cut off), and the whole edit as a lit dot in the far corner. The two arrows grow and settle
# about every 16 s.
ICON = r"""(kit, t, tilt) => {
  const th = 5, T = Number(t) || 0, s = .7 + .3 * Math.cos(T * .4), z = th / 2;
  const b = [-26, 20], up = [-26, 20 - 34 * s], side = [-26 + 46 * s, 20];
  const dot = (p, w, tone) => kit.line(kit.at(p[0] - .4, p[1], z), kit.at(p[0] + .4, p[1], z), w, tone, 1);
  let out = kit.slab(44, 38, th);
  out += kit.line(kit.at(-34, 26, z), kit.at(34, 26, z), .6, "plain", .7) + kit.line(kit.at(-34, 26, z), kit.at(-34, -28, z), .6, "plain", .7);
  out += kit.line(kit.at(b[0], b[1] - 4, z), kit.at(up[0], up[1], z), 1.6, "lit", 1);
  out += kit.line(kit.at(b[0] + 4, b[1], z), kit.at(side[0], side[1], z), 1.4, "plain", .95);
  out += dot(b, 5, "plain") + dot([20, -16], 6, "lit");
  return out;
}"""

_CONFIG_DATA = {k: DATA[k] for k in ("n", "n_code", "math", "code", "base_t1", "all_t1", "pred")}
_EX_ALL = {"math": {**EXAMPLES["math"], **EXAMPLES_PAIRS["math"]}, "code": EXAMPLES["code"],
           "problems": {**EXAMPLES["problems"], **EXAMPLES_PAIRS["problems"]}}
PAGE = PAGE.replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "cells": CELLS, "groups": GROUPS, "read": READ, "hint": HINT,
    "setcap": SETCAP, "codewhat": _CODE_WHAT, "keep": KEEP, "ex": _EX_ALL, "data": _CONFIG_DATA}, ensure_ascii=False).replace("</", "<\\/"))


def _check():
    """Every number of DATA against the readouts, the README and the specs; EXAMPLES against the run folders."""
    ro, ed, co = (json.load(open(DATA[k])) for k in ("readout", "edits_readout", "code_readout"))
    r2 = lambda v: [round(v["points"], 2), round(v["interval95"][0], 2), round(v["interval95"][1], 2)]
    for key in ("base", "rand", "randL0", "L0", "L11", "L22", "d28", "all"):
        d, c = _M[key], ro["cells"][_M[key]["cell"]]
        assert (c["right"], c["cap_hits"]) == (d["right"], d["cut"]), key
        assert abs(c["right_mean"] - _mean(d["right"])) < 1e-9 and abs(c["cap_hits_mean"] - _mean(d["cut"])) < 1e-9, key
        assert round(_mean(d["right"]) / (DATA["n"] - _mean(d["cut"])), 3) == c["right_per_finished"], key
        refs = {"vs_base": "minus_base_cue", "vs_all": "minus_top8x1.5_math31",
                "vs_random": "minus_random_sample_1" if key == "L0" else "minus_random"}
        for mine, theirs in refs.items():
            if mine in d:
                assert {w: r2(c[theirs][w2]) for w, w2 in (("right", "right"), ("cut", "cap"))} == d[mine], (key, mine)
            else:
                assert key in ("base", "rand", "randL0", "all") and (mine != "vs_base" or key == "base"), (key, mine)
    assert ro["cells"]["top8x1.5_L0-10_math31"]["minus_random_sample_1"]["reference"] == "rand8x1.5_L0-10_math31"
    for key in ("L11", "L22", "d28", "all"):
        assert ro["cells"][_M[key]["cell"]]["minus_random"]["reference"] == "rand8x1.5_math31", key
    pd = ed["paired_differences_points"]
    for key in ("top1", "top1x2", "top1x3"):
        d, c = _M[key], ed["cells"][_M[key]["cell"]]
        assert ([c["right_v3"]], [c["cap_hits"]]) == (d["right"], d["cut"]), key
        for mine, ref in (("vs_ref", "base_cue_T1"), ("vs_random1", "rand8_math31")):
            v = pd[f"{d['cell']} minus {ref}"]
            assert [v["points"], *v["ci95"]] == d[mine]["right"], (key, mine)
    b1 = ed["cells"]["base_cue_T1"]
    assert (b1["right_v3"], b1["cap_hits"]) == (DATA["base_t1"]["right"], DATA["base_t1"]["cut"])
    for key in ("L0", "L11", "L22"):  # the matrices of each band, from the one-sample cells of the same edit
        assert ed["cells"][_M[key]["cell"]]["edit"]["n_edited"] == _M[key]["n_edited"], key
        assert f"({_M[key]['n_edited']} of the 224 matrices)" in next(c[3] for c in CELLS if c[0] == key)
    assert ed["cells"]["top8x1.5_math31"]["edit"]["n_edited"] == DATA["matrices"] == _M["all"]["n_edited"]
    diff = co["differences"]
    neg = lambda v: [round(-v["points"], 2), round(-v["bootstrap95"][1], 2), round(-v["bootstrap95"][0], 2)]
    for key, d in _C.items():
        a = co["cells"][d["cell"]]["all"]
        assert (a["n"], [a["passed"]], [a["cap_hits"]], a["no_block"]) == (DATA["n_code"], d["right"], d["cut"], d["no_block"]), key
        for mine, ref in (("vs_base", "base_cue"), ("vs_random", "code_rand8x1.5_code31"), ("vs_all", "code_top8x1.5_code31")):
            if mine in d:
                assert neg(diff[f"{ref} - {d['cell']}"]) == d[mine]["right"], (key, mine)
    # the filed predictions and their outcome, as the specs and the README state them
    spec, xspec, readme = open(DATA["spec"]).read(), open("studies/rlneurons/specs/SPEC_xreward.md").read(), open("studies/rlneurons/README.md").read()
    for p in ("B1", "B2", "B3", "B4", "B5", "R1", "R2"):
        assert f"- {p}." in spec and f"- {p} held" in readme, p
    assert "at least 180 right" in spec and "at least 40" in spec
    assert "M1 refuted" in readme and "L1 (early layers: right answers without finishing) refuted" in readme
    assert "L2 (late layers: finishing without right answers) refuted" in readme and "L3 (middle layers: both) held" in readme
    assert "at least 350 passed and at least 20 cap hits" in xspec and "at most 14 cap hits and at most 345 passed" in xspec
    assert "at least 350 passed and at most 18 cap hits" in xspec
    assert "No edit smaller than 8\n  directions in all layers reached 190" in readme
    assert "14 of the 368 cap-hit answers were scored right" in readme and "(rule A: 0 in every L0-10 sample)" in readme
    # the headline numbers of the page
    assert f"{_L0['vs_base']['right'][0]:.1f}" == "7.6" and "7.6" in LINE and READ["layers"]["big"] == 7.6
    assert f"{_L0['vs_base']['cut'][0]:.1f}" == "6.2" and f"{_L11['vs_base']['cut'][0]:.1f}" == "-8.1"
    assert _held == 7 and len(LINE.split()) <= 26 and len(PROBLEM.split()) <= 12
    assert set(sum(GROUPS.values(), [])) == {c[0] for c in CELLS} == set(_M) and set(_C) <= set(_M)
    for s, n in (("math", DATA["n"]), ("code", DATA["n_code"])):  # the page's legs: the move from Base + cue's mean
        b = DATA[s]["base"]
        for key, d in DATA[s].items():
            for w in ("right", "cut"):
                if w in d.get("vs_base", {}):
                    assert abs(100 * (_mean(d[w]) - _mean(b[w])) / n - d["vs_base"][w][0]) < .01, (s, key, w)
    assert _examples() == EXAMPLES, "EXAMPLES differ from the run folders: run with --write"
    _check_pairs(ed)


def _pairs_here():
    return all(os.path.exists(f + "metrics.json") for f in _EX_PAIRS.values())


def _check_pairs(ed):
    """The pairing cells. The whole edit of the same seed is in the edits readout here; the cells' own files are on the
    branch sharedsub only until main takes them: where they are present every number is compared with them, else skipped."""
    t = ed["cells"][DATA["all_t1"]["cell"]]
    assert (t["right_v3"], t["cap_hits"]) == (DATA["all_t1"]["right"], DATA["all_t1"]["cut"])
    assert ed["cells"]["rand8x1.5_math31"]["right_v3"] == _M["rand"]["right"][0] and ed["cells"]["rand8x1.5_math31"]["cap_hits"] == _M["rand"]["cut"][0]
    assert f"{_near:.1f}" == "1.2" and READ["pairs"]["big"] == -13.1 and [round(x) for x in sorted(_less)] == [5, 12, 28]
    if not _pairs_here():
        print(f"skipped: the pairing cells' files ({', '.join(_EX_PAIRS.values())}) are not here; their numbers and "
              f"EXAMPLES_PAIRS were copied from branch {DATA['pairs']['branch']}, commit {DATA['pairs']['commit'][:7]}")
        return
    readme = open("studies/rlneurons/README.md").read()
    name = {"rin": "`rin`: RL's input directions, random outputs", "rout": "`rout`: RL's output directions, random inputs",
            "perm": "`perm`: both subspaces, pairs shifted by one"}
    iv = lambda v: f"{v[0]:+.1f} [{v[1]:.1f}, {v[2]:.1f}]".replace("+-", "-")
    rows = {}
    for line in open(DATA["pairs"]["rows"]):
        r = json.loads(line)
        rows.setdefault(r["arm"], {})[r["problem_index"]] = r
    ref = {"rand8x1.5_math31": "vs_random", DATA["all_t1"]["cell"]: "vs_all8"}
    shift = json.load(open(DATA["pairs"]["shift_readout"]))["edits"]
    assert round(shift[DATA["all_t1"]["cell"]]["rms"], 4) == DATA["all_t1"]["shift"]
    for key, d in _PR.items():
        c = json.load(open(_EX_PAIRS[key] + "metrics.json"))["counts"]
        assert (c["n"], [c["correct_v3"]], [c["cap_hits"]]) == (DATA["n"], d["right"], d["cut"]), key
        assert f"| {name[key]} | {d['right'][0]} | {d['cut'][0]} | {iv(d['vs_random']['right'])} | {iv(d['vs_all8']['right'])} |" in readme, key
        mine = rows[d["cell"]]
        assert sum(r["right_v3"] for r in mine.values()) == d["right"][0] and sum(r["cap_hit"] for r in mine.values()) == d["cut"][0]
        for arm, k in ref.items():  # the point differences again from the per-problem rows
            other = rows[arm]
            assert set(other) == set(mine) and len(mine) == DATA["n"]
            assert round(100 * sum(mine[i]["right_v3"] - other[i]["right_v3"] for i in mine) / DATA["n"], 1) == d[k]["right"][0], (key, arm)
        assert round(shift[d["cell"]]["rms"], 4) == d["shift"], key
    assert _examples(_EX_PAIRS, {}) == EXAMPLES_PAIRS, "EXAMPLES_PAIRS differ from the run folders: run with --write"
    print("the pairing cells match", ", ".join(_EX_PAIRS.values()), DATA["pairs"]["rows"], DATA["pairs"]["shift_readout"])


def _write():
    src = open(__file__).read()
    lit = "EXAMPLES = " + repr(_examples()) + "\n"
    src = re.sub(r"(# EXAMPLES-BEGIN\n).*?(# EXAMPLES-END)", lambda m: m.group(1) + lit + m.group(2), src, flags=re.S)
    if _pairs_here():
        lit = "EXAMPLES_PAIRS = " + repr(_examples(_EX_PAIRS, {})) + "\n"
        src = re.sub(r"(# EXAMPLES-PAIRS-BEGIN\n).*?(# EXAMPLES-PAIRS-END)", lambda m: m.group(1) + lit + m.group(2), src, flags=re.S)
    open(__file__, "w").write(src)


if __name__ == "__main__":  # run from the repository root
    if "--write" in sys.argv:
        _write()
        print("EXAMPLES rewritten from the run folders")
    else:
        _check()
        print("DATA and EXAMPLES match", DATA["readout"], DATA["edits_readout"], DATA["code_readout"], "and the run folders")
    sys.exit(0)
