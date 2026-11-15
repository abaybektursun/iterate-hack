"""The same three-token cue, found on math, lifts the base model on math, code and general questions: +37.2, +19.3 and
+30.0 points.

The page of one finding, served at /finding/cue-on-code (the slug is kept from the page's first version, which showed code
only) and reached from its tile on /findings, which ICON draws. The picture is one lit plate with three sets of marks side
by side: MATH-500 (500 problems), code (538 problems of HumanEval+ and MBPP+) and general questions (250 MMLU-Pro and 250
BBH). A mark is lit when the answer is right. The one control switches all three sets at once between Base, Base + cue,
RL and Think-SFT + cue; the marks that change light up or go dark one after another, and the counts and the points over
Base count with them. MATH-500 has one row per problem, so each mark is one problem and opens it. The code and general
runs committed counts per benchmark and per subject only, so there the lit marks fill each benchmark's or subject's rows
in order, and a click opens that benchmark or subject with the one stored example.
Address: /finding/cue-on-code#<base|cue|rl|sft>/<panel, p<problem>, c<mark> or g<mark>>. The addresses of the first
version (#base, #code-cue, #math-cue, with or without a panel) still open: #code-cue and #math-cue show Base + cue.
Study: studies/rlneurons, README sections "Code pair" (board result-59ed1a) and "Outside math and code" (board
result-1a80e9, on branch ali/ood). tools/findings.py reads N, ST[0]["passed"] and ST[2]["passed"] (the code set).

    uv run tools/finding_cue_on_code.py     checks every number against the artifacts (run from the repository root)
"""
import json
import os
import subprocess
import sys

from finding_opening_cue import DATA as _OC, PROBLEMS as MATH_ROWS  # MATH-500 Base and Base + cue rows, one source

R = "studies/rlneurons/results/"
# Every number is copied from the artifacts named here. None is typed from memory. The deployed site ships only
# tools/*.py, so the copies are literals; run this file to compare them with the artifacts.
DATA = {
    # MATH-500, T 1.0 / top-p 1.0, one sample, grader v3. Base and Base + cue: finding_opening_cue.PROBLEMS, written from
    # rows (t3 plain, t1 cue). RL: rl_rows t2_right / t2_cap_hit, the same t1 rows joined on problem_index.
    "math": {
        "rows": _OC["rows"], "readout": _OC["artifact"], "commit": _OC["commit"],
        "rl_rows": R + "rln4/t1_t2_items-01/per_problem.json",
        "n": 500, "base": _OC["plain"]["right"], "cue": _OC["cue"]["right"], "rl": _OC["rl_first"]["right"],
        "flips": _OC["flips"], "gap": _OC["gap"]["t10"], "no_answer": _OC["plain"]["nothing_extracted"],
        # RL's outcome per problem in index order: r right, w wrong, c cut off at 16,384 tokens
        "rl_outcome": "rrrrrrrrrwrwrrrrrrwrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrwrrrrrwrrrrrrrrrcrrrrrrrrwrrrrrrrrwrrrrrrrrrrrrrrrrrrrrrrrrrwrrrrrrrrrrrwrwrrrrrrrrrrrrrrrwrrrrrrrrrrrrrrrrrrrwrrrrrrrrrwrrwrrrrrrrrrrrrrrrrrrrrrrwrrrrrrrrrrrrrrrrrrrrrrrwrrrrrrrrwrrrrrrrrrrrrwrrrrrrrrwrrrrrrrwrrwrcwrrrrrrrwrrrrrrwrrrrrrrrrrrrrrrwrrrrrrrrwrrrrrrrrrrrwrrrrrrrwrrrrrrrrrrrrrrrrrrrrrrwrrrrrrrwrrrrrrrrrrrrrrrrrrrrrwrrrrrrrrrrrrrrrrrrrrrcrrrrrrrrrrrrrrrcrrrrrrrrrrrrwrrrrrrrcrrrrrrrrrrrrrrrrrr",
    },
    # Code: studies/rlneurons/results/code1/readout.json (commit 9fac5b7), T 1.0 / top-p 1.0, one sample, the benchmark's tests
    "code": {
        "artifact": R + "code1/readout.json",
        "commit": "9fac5b7",       # the commit that holds the readout and the four run folders
        "run_commit": "be62e76",   # the code the four GPU jobs ran (each run.json)
        "spec": "studies/rlneurons/specs/SPEC_code1.md",
        "n": 538,                  # cells.*.all.n: HumanEval+ 163 and MBPP+ 375, after 4 of 542 failed the grader check
        "n_all": 542, "n_excluded": 4,
        # passed and tokens: cells.<key>.all.passed and tokens_per_problem; cue: cells.<key>.prefix_text
        "states": [
            {"key": "base_plain", "name": "Base", "passed": 222, "tokens": 2241, "cue": ""},
            {"key": "base_cue", "name": "Code cue", "passed": 317, "tokens": 4148, "cue": " as shown in the prompt. I hope this helps!\n\nOkay"},
            {"key": "base_mathcue", "name": "Math cue", "passed": 326, "tokens": 4119, "cue": " line!\n\nOkay"},
        ],
        "reference": {"key": "rl_plain", "name": "RL on code", "passed": 401, "tokens": 4054},  # Olmo-3.1-7B-RL-Zero-Code
        # cells.<key>.humanevalplus.passed and mbppplus.passed
        "bench": {"humanevalplus": {"n": 163, "base_plain": 72, "base_cue": 106, "base_mathcue": 120, "rl_plain": 135},
                  "mbppplus": {"n": 375, "base_plain": 150, "base_cue": 211, "base_mathcue": 206, "rl_plain": 266}},
        # differences.<a - b>: points and bootstrap95, paired over problems with 5,000 resamples
        "diff": {
            "rl_plain - base_plain": [33.271, 28.810, 37.732],
            "rl_plain - base_cue": [15.613, 11.524, 19.888],
            "rl_plain - base_mathcue": [13.941, 10.037, 17.844],
            "base_plain - base_cue": [-17.658, -22.491, -12.825],
            "base_plain - base_mathcue": [-19.331, -24.349, -14.312],
            "base_cue - base_mathcue": [-1.673, -5.762, 2.788],
        },
        "no_overlap": {"n": 535, "base_plain": 221, "base_cue": 315, "base_mathcue": 323, "rl_plain": 399},  # cells.<key>.all_no_overlap
        "no_block": {"base_plain": 43, "base_cue": 34, "base_mathcue": 33, "rl_plain": 8},  # cells.<key>.all.no_block
        # The one problem whose answer text every run folder stores (<cell>-01/examples.json, uid HumanEval/0): passed,
        # generated tokens, cut off, the first 240 characters of the answer; the prompt's task between "Write" and "Remember"
        "example": {
            "uid": "HumanEval/0",
            "task": "Write the complete Python function `has_close_elements` for this signature and docstring:\n\nfrom typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\n    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    True\n    \"\"\"",
            "base_plain": [True, 275, False, ". Please submit the code after you have posted your original message.\n\nPython function `has_close_elements` to check if there is any two numbers in the list which are closer than the given threshold.\nThe function will take a list of floatin"],
            "base_mathcue": [True, 1132, False, " line!\n\nOkay, I need to write a Python function called has_close_elements that takes a list of floats and a threshold. The goal is to check if any two numbers in the list are closer than the threshold to each other. So, if the difference be"],
            "rl_plain": [True, 1854, False, " as shown in the prompt. I hope this helps!\n\nOkay, I need to write a Python function called has_close_elements. The function takes a list of floats and a threshold. It should return True if any two numbers in the list are closer to each oth"],
        },
        # Wang et al., arXiv 2610.06851, Table 6 (fetched 2026-11-15): Olmo-3-7B, RL-Zero prompt, HumanEval pass@1, no cue / cued
        "wang": {"base": 50.2, "cue": 69.8},
    },
    # General questions: copied from branch ali/ood, commit 99b2d5d (not on main when copied), path below. T 1.0 / top-p 1.0,
    # one sample, the math prompt unchanged, grader v2 (mcq_lib.grade_v2) unless named v1.
    "general": {
        "branch": "ali/ood", "commit": "99b2d5d",
        "artifact": R + "ood1/readout.json",
        "items": "studies/rlneurons/data/ood1/ood1_items.json",
        "spec": "studies/rlneurons/specs/SPEC_ood1.md",
        "n": 500, "n_mmlupro": 250, "n_bbh": 250,
        # cells.<key>.all: right_v2, mmlupro.right_v2, bbh.right_v2, right (v1), no_answer_v2, cap_hits, tokens_per_item
        "cells": {"base_plain": {"right": 136, "mmlupro": 48, "bbh": 88, "right_v1": 114, "no_letter": 214, "cap_hits": 3, "tokens": 992},
                  "base_cue": {"right": 286, "mmlupro": 116, "bbh": 170, "right_v1": 229, "no_letter": 30, "cap_hits": 1, "tokens": 2049},
                  "rl_plain": {"right": 332, "mmlupro": 133, "bbh": 199, "right_v1": 78, "no_letter": 13, "cap_hits": 0, "tokens": 3165},
                  "sft_cue": {"right": 342, "mmlupro": 137, "bbh": 205, "right_v1": 332, "no_letter": 6, "cap_hits": 4, "tokens": 2941}},
        # cells.<key>.groups.<subject>: [subject, n, right_v2 of base_plain, base_cue, rl_plain, sft_cue]
        "groups": [["mmlupro/biology", 28, 8, 22, 24, 23], ["mmlupro/business", 28, 7, 19, 20, 22], ["mmlupro/economics", 28, 3, 15, 17, 21],
                   ["mmlupro/health", 28, 11, 17, 17, 14], ["mmlupro/history", 28, 4, 10, 11, 10], ["mmlupro/law", 28, 6, 4, 5, 10],
                   ["mmlupro/other", 28, 1, 8, 14, 12], ["mmlupro/philosophy", 27, 1, 10, 9, 9], ["mmlupro/psychology", 27, 7, 11, 16, 16],
                   ["bbh/date_understanding", 25, 4, 20, 23, 23], ["bbh/disambiguation_qa", 25, 12, 14, 15, 16], ["bbh/hyperbaton", 25, 7, 14, 18, 17],
                   ["bbh/logical_deduction_five_objects", 25, 7, 19, 24, 24], ["bbh/penguins_in_a_table", 25, 13, 23, 25, 25],
                   ["bbh/reasoning_about_colored_objects", 25, 11, 15, 23, 25], ["bbh/salient_translation_error_detection", 25, 9, 10, 7, 13],
                   ["bbh/snarks", 25, 7, 18, 18, 14], ["bbh/temporal_sequences", 25, 7, 14, 21, 23],
                   ["bbh/tracking_shuffled_objects_five_objects", 25, 11, 23, 25, 25]],
        # differences["<a> - <b> | <set> | <grader>"]: points, bootstrap95 (5,000 paired resamples), as b - a here
        "diff": {"cue": [30.0, 24.6, 35.4], "cue_mmlupro": [27.2, 19.6, 34.4], "cue_bbh": [32.8, 24.4, 40.8],
                 "rl_minus_cue": [9.2, 4.6, 13.8], "sft_minus_rl": [2.0, -2.4, 6.2], "cue_v1": [23.0, 17.6, 28.4]},
        "flips": {"up": 198, "down": 48},  # base_plain - base_cue | all | v2: only_second, only_first
        # The one question whose answer text all four run folders store (<cell>-01/examples.json, uid mmlupro/3058, the
        # first item): right_v2, letter_v2, generated tokens, cut off, the first 240 characters; its text from the items file
        "example": {
            "uid": "mmlupro/3058", "group": "mmlupro/biology", "gold": "J",
            "question": "Which of the following is a benefit that mycorrhizal fungi confer to many plants?\n\nOptions:\n(A) They fix nitrogen, which is particularly important for plants in nitrogen-limited habitats.\n(B) They provide plants with access to unlimited water resources.\n(C) They provide carbon to plants in exchange for fixed nitrogen.\n(D) They help plants create their own food through photosynthesis.\n(E) They enhance plant growth by releasing growth hormones.\n(F) They protect plant roots from desiccation in extremely dry habitats.\n(G) They increase plant resistance to pests and diseases.\n(H) They assist in the absorption of carbon dioxide from the atmosphere.\n(I) They provide plants with access to potassium, an element abundant in all kinds of soils.\n(J) They provide access to phosphorus, an essential element that is limited in many kinds of soils.\n\nThe answer is the letter of the correct option.",
            "base_plain": [False, None, 25, False, " and end all answer put in the box next to your name All outputs is written in single line, one space per character!"],
            "base_cue": [True, "J", 753, False, " line!\n\nOkay, let's tackle this question. So, the question is asking which option is a benefit that mycorrhizal fungi confer to many plants. Hmm, mycorrhizae... I remember they're symbiotic relationships between fungi and plant roots. Let m"],
            "rl_plain": [True, "J", 1184, False, " line!\n\nOkay, let's see. The question is about which benefit is conferred by mycorrhizal fungi to plants. The options are A through J. Hmm.\n\nFirst, I need to recall what mycorrhizae do. Mycorrhizal fungi are symbiotic partners with plant ro"],
            "sft_cue": [False, "B", 4593, False, " line!\n\nOkay, let me tackle this question. So the problem is asking which of the options listed is a benefit that mycorrhizal fungi confer to plants. Mycorrhizal fungi are those symbiotic organisms that form symbiotic associations with plan"],
        },
    },
    "cue_text": _OC["cue_text"],
}

# tools/findings.py reads these three names for the index row: the code set, as in the page's first version.
M, CD, G = DATA["math"], DATA["code"], DATA["general"]
N, ST, REF = CD["n"], CD["states"], CD["reference"]
_GC = G["cells"]


def pts(a, b, n):
    """Points from count a to count b of n, one decimal."""
    return round(100 * (b - a) / n, 1)


def share(base, cue, rl):
    """The part of RL's gain over Base that Base + cue reaches, in whole percent."""
    return round(100 * (cue - base) / (rl - base))


GAINS = {"math": pts(M["base"], M["cue"], M["n"]), "code": pts(ST[0]["passed"], ST[2]["passed"], N),
         "general": pts(_GC["base_plain"]["right"], _GC["base_cue"]["right"], G["n"])}
SHARES = {"math": share(M["base"], M["cue"], M["rl"]), "code": share(ST[0]["passed"], ST[2]["passed"], REF["passed"]),
          "general": share(_GC["base_plain"]["right"], _GC["base_cue"]["right"], _GC["rl_plain"]["right"])}
# If Base's answers without a letter were right as often as its answers with one (an estimate, raised on result-1a80e9)
_parsed = G["n"] - _GC["base_plain"]["no_letter"]
_imputed = _GC["base_plain"]["right"] + _GC["base_plain"]["no_letter"] * _GC["base_plain"]["right"] / _parsed
IMPUTED = {"base": round(_imputed), "rate": round(100 * _GC["base_plain"]["right"] / _parsed, 1),
           "gain": round(100 * (_GC["base_cue"]["right"] - _imputed) / G["n"], 1),
           "share": round(100 * (_GC["base_cue"]["right"] - _imputed) / (_GC["rl_plain"]["right"] - _imputed))}


def num(v):
    """One decimal with a true minus sign."""
    return f"{v:.1f}".replace("-", "−")


def ci(d):
    """[points, low, high] as "+30.0 points (95 % interval 24.6 to 35.4)"."""
    return f"{'+' if d[0] >= 0 else ''}{num(d[0])} points (95 % interval {num(d[1])} to {num(d[2])})"


def flip(key):
    """A code difference stored as a - b, returned as b - a."""
    p, lo, hi = CD["diff"][key]
    return [-p, -hi, -lo]


TITLE = "The cue beyond math"
PROBLEM = "Does a three-token cue found on math help on other tasks?"
LINE = (f"The same three tokens lift the base on math, code and general questions: +{GAINS['math']}, +{GAINS['code']} "
        f"and +{GAINS['general']} points.")  # also the sentence on its tile

# What the picture draws: per set, its groups (rows of marks) with the right count under each state
# [Base, Base + cue, RL, Think-SFT + cue]; None where a state was not run on that set.
_HE, _MB = CD["bench"]["humanevalplus"], CD["bench"]["mbppplus"]
_SUBJ = {"mmlupro": "MMLU-Pro", "bbh": "BBH"}
_word = lambda s: s.replace("_", " ").replace("qa", "QA")
SETS = [
    {"key": "math", "name": "MATH-500", "unit": "problems", "n": M["n"], "chosen": "the cue was chosen here", "rl": "RL",
     "share": SHARES["math"], "groups": [{"name": "MATH-500", "bench": "math500", "n": M["n"], "right": [M["base"], M["cue"], M["rl"], None]}]},
    {"key": "code", "name": "Code", "unit": "problems", "n": N, "chosen": "nothing chosen here", "rl": "RL on code",
     "share": SHARES["code"],
     "groups": [{"name": "HumanEval+", "bench": "humanevalplus", "n": _HE["n"], "right": [_HE["base_plain"], _HE["base_mathcue"], _HE["rl_plain"], None]},
                {"name": "MBPP+", "bench": "mbppplus", "n": _MB["n"], "right": [_MB["base_plain"], _MB["base_mathcue"], _MB["rl_plain"], None]}]},
    {"key": "general", "name": "General questions", "unit": "questions", "n": G["n"], "chosen": "nothing chosen here", "rl": "RL",
     "share": SHARES["general"], "foot": f"Grader v2, added after two runs; v1: +{num(G['diff']['cue_v1'][0])}",
     "groups": [{"name": f"{_SUBJ[g[0].split('/')[0]]}, {_word(g[0].split('/')[1])}", "bench": g[0].split("/")[0], "n": g[1],
                 "right": g[2:]} for g in G["groups"]]},
]
for _s in SETS:
    _s["total"] = [None if any(g["right"][k] is None for g in _s["groups"]) else sum(g["right"][k] for g in _s["groups"]) for k in range(4)]

# MATH-500 per problem: [index, Base, Base + cue, RL] outcomes (r right, w wrong, c cut off), in the order the marks are
# drawn: right with the cue first, then right for RL, then right for Base, then by index. The lit area then grows from the
# top in every state, and the problems one setting gets right and the next one wrong stay visible as single marks.
_key = lambda r: (r[4] != "r", M["rl_outcome"][r[0]] != "r", r[3] != "r", r[0])
MATH = [[r[0], r[3], r[4], M["rl_outcome"][r[0]]] for r in sorted(MATH_ROWS, key=_key)]
# Read on the first click: [problem text, reference answer, extracted answer without and with the cue, the start of the
# answer without the cue, the text that follows the cue in the answer with it], by problem index.
MATH_TEXT = {r[0]: [r[1], r[2], r[5], r[6], r[7], r[8]] for r in MATH_ROWS}

STATES = [
    {"key": "base", "name": "Base", "note": "Base: the base model Olmo 3 7B with the plain prompt, one answer per item at T 1.0."},
    {"key": "cue", "name": "Base + cue", "note": "Base + cue: the same model, its answer started with “ line!”, a blank line and “Okay”. The cue was found on MATH-500 and is used unchanged on code and general questions."},
    {"key": "rl", "name": "RL", "note": "RL: the base model after reinforcement learning on math (Olmo 3.1 RL-Zero-Math). On code the reference is the model trained with RL on code."},
    {"key": "sft", "name": "Think-SFT + cue", "note": "Think-SFT + cue: the base model fine-tuned to imitate worked solutions, with no reward, answering with the cue. Run on the general questions only in this comparison."},
]

_M, _GD = M, G["diff"]
PANELS = [
    ["new", "What is new",
     f"Wang et al. (arXiv 2610.06851, Table 6) test a short cue on math sets and on HumanEval, where it takes this base model "
     f"from {CD['wang']['base']} % to {CD['wang']['cue']} %. New here: the cue on {G['n']} questions that are neither math nor "
     "code, with RL as the reference on every set.",
     [f"General questions: {G['n_mmlupro']} from MMLU-Pro (the 9 categories outside math, physics, chemistry, engineering and "
      f"computer science) and {G['n_bbh']} from 10 BBH tasks with a one-letter answer. Base {_GC['base_plain']['right']} of "
      f"{G['n']}, Base + cue {_GC['base_cue']['right']}, RL {_GC['rl_plain']['right']}: {ci(_GD['cue'])}, "
      f"{SHARES['general']} % of RL's gain. MMLU-Pro {ci(_GD['cue_mmlupro'])}, BBH {ci(_GD['cue_bbh'])}.",
      f"Code: Base {ST[0]['passed']} of {N}, Base + cue {ST[2]['passed']}, RL on code {REF['passed']}: "
      f"{ci(flip('base_plain - base_mathcue'))}, {SHARES['code']} % of the gain of RL on code. A cue taken from the code "
      f"model's own opening does no better: {ST[1]['passed']} of {N}, {ci(flip('base_cue - base_mathcue'))}.",
      "The fetched paper holds no test of the cue outside math and code; the plan of the general run found no team or "
      "published number either (its search of 2026-11-15)."]],
    ["why", "Why it matters",
     f"Every setting of the team's climb was chosen on MATH-500, so its gains could be fitted to that one benchmark. Nothing "
     f"was chosen on code or on the general questions, and there the cue still gives {SHARES['code']} % and "
     f"{SHARES['general']} % of RL's gain, against {SHARES['math']} % on MATH-500.",
     [f"On code the gain is not about writing an answer at all: Base gives no code block in {CD['no_block']['base_plain']} of "
      f"{N} answers and Base + cue in {CD['no_block']['base_mathcue']}, yet Base + cue passes "
      f"{ST[2]['passed'] - ST[0]['passed']} more problems.",
      f"RL stays ahead on every set: {num(_M['gap'][0])} points on MATH-500 (95 % interval {num(_M['gap'][1])} to "
      f"{num(_M['gap'][2])}), {num(CD['diff']['rl_plain - base_mathcue'][0])} on code "
      f"({num(CD['diff']['rl_plain - base_mathcue'][1])} to {num(CD['diff']['rl_plain - base_mathcue'][2])}) and "
      f"{num(_GD['rl_minus_cue'][0])} on the general questions ({num(_GD['rl_minus_cue'][1])} to {num(_GD['rl_minus_cue'][2])}).",
      f"Think-SFT + cue gets {_GC['sft_cue']['right']} of {G['n']} general questions, {ci(_GD['sft_minus_rl'])} above RL."]],
    ["how", "How we know",
     "On every set each setting answered every item once at T 1.0 and top-p 1.0, with the same seeds in every setting and a "
     "cut-off at 16,384 tokens; the cue is the same three tokens everywhere.",
     [f"MATH-500, grader v3: Base {_M['base']}, Base + cue {_M['cue']}, RL {_M['rl']} of {_M['n']}. The cue turns "
      f"{_M['flips']['up']} problems from wrong to right and {_M['flips']['down']} from right to wrong. Every mark of this set "
      "is one problem's row.",
      "Code: scored by running each benchmark's tests. Before sampling, every reference solution had to pass and a planted "
      f"wrong program had to fail; {CD['n_excluded']} of {CD['n_all']} problems failed that check and are left out.",
      "General questions: an answer is right when the first option letter after its last answer marker is the gold letter. "
      "This grader, v2, was written after reading the first two settings, because the grader of the plan (v1) cannot read "
      f"RL's \\boxed answers: RL scores {_GC['rl_plain']['right_v1']} of {G['n']} under v1. Under v1 the cue's gain is "
      f"{ci(_GD['cue_v1'])}."]],
    ["limits", "What it does not show",
     f"It does not show that the cue adds knowledge. On the general questions much of the gain is that Base + cue writes an "
     f"answer letter at all: Base gives none in {_GC['base_plain']['no_letter']} of {G['n']} answers, Base + cue in "
     f"{_GC['base_cue']['no_letter']}.",
     [f"If Base's answers without a letter were right as often as its answers with one ({IMPUTED['rate']} %), Base would "
      f"have about {IMPUTED['base']} right and the cue's gain would be about {num(IMPUTED['gain'])} points, "
      f"{IMPUTED['share']} % of RL's gain. This is an estimate, not a measurement. On MATH-500, Base gives no final answer "
      f"in {_M['no_answer']} of {_M['n']}.",
      "Each set is one sample at one seed, with no vote. The general set is a sample of MMLU-Pro and BBH, so its counts do "
      "not compare with published scores. The code and general runs committed counts per benchmark and subject, not per "
      "item: their marks fill each row in order and do not name an item.",
      "Think-SFT + cue was run only on the general questions in this comparison. On code, RL means the model trained with "
      "RL on code; on the other sets, RL on math."]],
    ["run", "How to reproduce it",
     "Each setting of each set is one job on an H100 GPU in the study studies/rlneurons, and each readout runs on a laptop.",
     [f"MATH-500: the rows {_M['rows']} and {_M['rl_rows']}, the counts {_M['readout']} (commit {_M['commit']}).",
      f"Code: studies/rlneurons/jobs/run_code_cell.py (commit {CD['run_commit']}); readout {CD['artifact']} (commit "
      f"{CD['commit']}); plan {CD['spec']}.",
      f"General questions: studies/rlneurons/jobs/run_mcq_cell.py; readout {G['artifact']}, plan {G['spec']}, on branch "
      f"{G['branch']} (commit {G['commit']}), not on main when this page was written."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with three small sets of dots, math, code and general questions; the lit part of each set moves
# slowly between Base and Base + cue.
ICON = r"""(kit, t, tilt) => {
  const th = 5, w = th / 2, cols = 4, rows = 7, base = __BASE__, cue = __CUE__;
  const q = .5 - .5 * Math.cos((Number(t) || 0) * .5);
  let out = kit.slab(44, 38, th);
  [-26, 0, 26].forEach((u0, s) => {
    const share = base[s] + (cue[s] - base[s]) * q;
    for (let k = 0; k < cols * rows; k++) {
      const i = k % cols, j = Math.floor(k / cols), p = kit.at(u0 + (i - 1.5) * 4.6, 15 - j * 5, w), on = (k + .5) / (cols * rows) <= share;
      out += `<ellipse cx="${p[0].toFixed(2)}" cy="${p[1].toFixed(2)}" rx="${(1.5 * p[2]).toFixed(2)}" ry="${(1.05 * p[2]).toFixed(2)}" ` +
        `fill="${kit.token.ink}" opacity="${on ? .92 : .2}"/>`;
    }
  });
  return out;
}""".replace("__BASE__", json.dumps([round(s["total"][0] / s["n"], 3) for s in SETS])).replace(
    "__CUE__", json.dumps([round(s["total"][1] / s["n"], 3) for s in SETS]))

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
   with a cast shadow in place of the glow. The light comes from the upper left in both. A right answer is a lit dot, a
   wrong one a faint dot; a mark that is changing passes through blue. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --dot-on: .86; --dot-off: .16;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --dot-on: .94; --dot-off: .19;
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

/* The picture: one plate with three sets of marks, and the one switch */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg { width: 100%; max-height: calc(100vh - 210px); display: block; overflow: visible; touch-action: pan-y; cursor: default; user-select: none; -webkit-user-select: none; }
svg:focus:not(:focus-visible) { outline: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.mk { fill: none; stroke-linecap: round; }
.mk.lit { stroke: var(--ink); opacity: var(--dot-on); }
.mk.dim { stroke: var(--ink); opacity: var(--dot-off); }
.mk.blue { stroke: var(--blue); }
.sel { fill: none; stroke: var(--blue); stroke-width: 1.6; }
.grp { fill: none; stroke: var(--blue); stroke-width: 1; stroke-dasharray: 3 4; opacity: .8; }
.sname { font-weight: 660; font-stretch: 112%; }
.scount { font-weight: 640; }
.sof, .ssub, .blab, .shr, .foot, .kl { fill: var(--mute) !important; font-weight: 480; }
.big { font-weight: 640; letter-spacing: -.035em; font-stretch: 100%; }
.big.off { fill: var(--faint) !important; font-weight: 400; letter-spacing: 0; font-stretch: 106%; }
.track { fill: none; stroke: var(--ink); stroke-width: 1; opacity: .22; }
.fill { fill: none; stroke: var(--ink); stroke-width: 3; stroke-linecap: round; opacity: .85; }
.tick { fill: none; stroke: var(--mute); stroke-width: 1.4; }
.tick.rl { stroke: var(--blue); stroke-width: 2; }
.rll { fill: var(--blue) !important; font-weight: 620; }
.kd.lit { fill: var(--ink); opacity: var(--dot-on); } .kd.dim { fill: var(--ink); opacity: var(--dot-off); }
.switch { display: inline-flex; align-self: center; margin-top: 14px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; background: var(--paper); }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button[aria-pressed="true"]:hover { color: var(--paper); }
.hint { align-self: center; margin: 10px 0 0; font-size: 13.5px; color: var(--mute); text-align: center; max-width: 76ch; min-height: 3em; }

/* One drawn entrance, then only the slow sway and what the reader changes */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .words { animation: fade .7s .5s both; }

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
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 0 6px 12px 0; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.lead.q { font-size: 15.5px; line-height: 1.45; color: var(--mute); max-width: 44ch; white-space: pre-line; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.facts .who { color: var(--ink); font-weight: 620; }
.facts .on { color: var(--ink); font-weight: 640; }
.facts li.now { color: var(--ink); }
.note { margin: 12px 0 0; font-size: 13.5px; color: var(--mute); max-width: 44ch; }
.txt { margin: 14px 0 0; padding-top: 10px; border-top: 1px solid var(--rule); font-size: 13.5px; line-height: 1.5; max-width: 44ch; overflow-wrap: anywhere; }
.txt .tcap { margin: 0 0 6px; color: var(--faint); font-size: 12.5px; }
.txt p { margin: 0; white-space: pre-line; color: var(--mute); }
.txt .cue { color: var(--blue); font-weight: 600; white-space: pre; }
.steps { display: flex; justify-content: space-between; margin-top: 14px; font-size: 13px; color: var(--mute); }
.steps button:hover { color: var(--ink); }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the switch, the picture, the depth. The switch stays at the top
     of the screen while the three sets scroll under it. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 18px; padding: 0; display: flex; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
  .switch { order: -2; position: sticky; top: 6px; z-index: 2; display: grid; grid-template-columns: 1fr 1fr; gap: 2px; width: 100%; margin: 0 0 4px; border-radius: 22px; }
  .switch button { text-align: center; padding: 9px 6px; font-size: 14px; white-space: normal; line-height: 1.2; }
  .hint { order: -1; margin: 6px 0 10px; min-height: 0; }
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
    <svg id="svg" role="img" tabindex="0"></svg>
    <div class="switch" id="switch" role="group" aria-label="Which model answers, and how its answer starts"></div>
    <p class="hint" id="hint" aria-live="polite"></p>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, SETS = C.sets, STATES = C.states, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const sgn = v => (v < 0 ? "−" : "+") + Math.abs(v).toFixed(1), nb = s => String(s).replace(/ %/g, " %");
const COLS = 28, PREFIX = ["p", "c", "g"];

/* Every mark: its set, its group, its place in the group, and whether it is lit in each state. MATH-500 marks are
   problems (C.math: [index, Base, Base + cue, RL], in drawing order). Code and general marks are places in a count:
   in each group the first <right> places are lit. */
const MK = SETS.map((s, si) => {
  const out = [];
  if (s.key === "math") C.math.forEach(([i, ...o], k) => out.push({ g: 0, k, i, lit: [0, 1, 2].map(m => o[m] === "r").concat(false), o }));
  else s.groups.forEach((g, gi) => { for (let k = 0; k < g.n; k++) out.push({ g: gi, k, lit: g.right.map(r => r != null && k < r) }); });
  return out;
});
const SLOT = {}; MK[0].forEach((m, k) => { SLOT[m.i] = k; });
const S = { st: 1, from: 1, t0: -1e9, open: null, g: null, el: {}, shown: {}, last: 0, pp: [[], [], []], n0: [], n1: [] };

/* Geometry, in a small 3D space around the plate's centre (x right, y down, z toward the viewer). Desktop: the three
   sets side by side, their counts on one line and their rails on one line. Phone: the three sets one under another. */
function geo() {
  const wide = !narrow.matches, g = wide
    ? { w: 1000, h: 596, cx: 500, cy: 298, D: 2200, a: [14, 10, 986, 584], r: 30, deep: 40, blur: 16,
        bw: 266, fs: { name: 18, sub: 14, big: 58, lab: 14, cnt: 18, small: 14 } }
    : { w: 480, h: 0, cx: 240, cy: 0, D: 2400, a: [6, 6, 474, 0], r: 22, deep: 28, blur: 12,
        bw: 420, fs: { name: 21, sub: 17, big: 52, lab: 17, cnt: 21, small: 17 } };
  g.pitch = g.bw / COLS;
  g.sets = SETS.map((s, si) => {
    let row = 0, gaps = 0; const rows = [];
    s.groups.forEach((gr, gi) => {
      if (gi && gr.bench !== s.groups[gi - 1].bench) gaps++;
      rows.push({ row, gaps }); row += Math.ceil(gr.n / COLS);
    });
    return { rows, height: (row + .8 * gaps) * g.pitch };
  });
  if (wide) {
    const tall = Math.max(...g.sets.map(b => b.height));
    g.sets.forEach((b, si) => Object.assign(b, { x0: 62 + si * 304, y0: 50, top: 192, rail: 192 + tall + 26 }));
    g.key = [62, 548];
  } else {
    let y = 34;
    g.sets.forEach((b, si) => { Object.assign(b, { x0: 30, y0: y, top: y + 146 }); b.rail = b.top + b.height + 24; y = b.rail + (SETS[si].foot ? 112 : 96) + 34; });
    g.key = [30, y - 34]; g.h = y + 30; g.cy = g.h / 2; g.a[3] = g.h - 6;
  }
  return g;
}
function pos(g, si, m) {  // a mark's centre on the plate
  const b = g.sets[si], r = b.rows[m.g], row = r.row + Math.floor(m.k / COLS), col = m.k % COLS;
  return [b.x0 + (col + .5) * g.pitch, b.top + (row + .5 + .8 * r.gaps) * g.pitch];
}
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z) {
  const X = x - g.cx, Y = y - g.cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, g.cy + y1 * k, k];
}
function rounded(g, [x0, y0, x1, y1], r, z) {  // a rounded rectangle at depth z
  const p = [], corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}

const LV = 9, CLS = ["lit", "dim", "blue"], RMAX = 7;
function build() {
  const g = S.g = geo(), svg = $("svg"), [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0, F = g.fs;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const T = (cls, id, fs, extra = "") => `<text class="${cls}" id="${id}" font-size="${fs}" ${extra}></text>`;
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.style.aspectRatio = `${g.w} / ${g.h}`;
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${g.cy}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .04)}" width="${aw}" height="${ah}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .3)}" cy="${f(ay0 + ah * .24)}" rx="${f(aw * .3)}" ry="${f(ah * .2)}" transform="rotate(-14 ${f(ax0 + aw * .3)} ${f(ay0 + ah * .24)})" fill="url(#spec)"/>` +
    SETS.map((s, si) => `<g id="set${si}">` + CLS.map(c => [...Array(LV)].map((_, l) => `<path class="mk ${c}" id="m${si}${c}${l}"/>`).join("")).join("") +
      `<g class="words">` + T("sname", `nm${si}`, F.name) +
      `<text id="ct${si}" font-size="${F.cnt}" text-anchor="end"><tspan class="scount" id="cv${si}"></tspan><tspan class="sof" id="co${si}"></tspan></text>` +
      T("ssub", `sb${si}`, F.sub) + T("big", `bg${si}`, F.big) + T("blab", `bl${si}`, F.lab) +
      `<path class="track" id="tr${si}"/><path class="fill" id="fl${si}"/><path class="tick" id="tb${si}"/><path class="tick rl" id="tk${si}"/>` +
      T("rll", `rl${si}`, F.small, 'text-anchor="end"') + T("shr", `sh${si}`, F.small) + (s.foot ? T("foot", `ft${si}`, F.small) : "") + `</g></g>`).join("") +
    `<path class="grp" id="grp"/><path class="sel" id="sel"/>` +
    `<g class="words"><circle class="kd lit" id="kd0" r="4"/>${T("kl", "kt0", F.small)}<circle class="kd dim" id="kd1" r="3"/>${T("kl", "kt1", F.small)}${T("kl", "kt2", F.small)}</g>`;
  S.el = {}; S.shown = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  S.base = SETS.map((s, si) => MK[si].map(m => pos(g, si, m)));
}

/* A state change: every mark that changes waits its turn (a few ms per place, and a little more for each set to the
   right), then grows or shrinks over DUR ms, rising toward the viewer as it passes through blue. */
const DUR = 460, STAG = .62, SETGAP = 110, SETTLE = SETGAP * 2 + STAG * 540 + DUR;
function draw(now) {
  const g = S.g, E = S.el, F = g.fs, el = now - S.t0, P = g.pitch;
  const text = (id, v) => { if (S.shown[id] !== v) E[id].textContent = S.shown[id] = v; };
  const at = (el, q, dy) => { el.setAttribute("x", f(q[0])); el.setAttribute("y", f(q[1] + (dy || 0))); };
  E.back.setAttribute("d", rounded(g, g.a, g.r, -g.deep));
  E.plate.setAttribute("d", rounded(g, g.a, g.r, 0));
  const rOn = P * .36, rOff = P * .2, lvl = r => clamp(Math.round(r / RMAX * (LV - 1)), 0, LV - 1);
  const e9 = ease(clamp(el / SETTLE, 0, 1));
  let sel = "", grp = "";
  SETS.forEach((s, si) => {
    const paths = {}; CLS.forEach(c => { for (let l = 0; l < LV; l++) paths[c + l] = ""; });
    let count = 0;
    const list = MK[si], pp = S.pp[si], A = S.from, B = S.st;
    for (let k = 0; k < list.length; k++) {
      const m = list[k], a = m.lit[A], b = m.lit[B], base = S.base[si][k];
      let r, c, z = 4, lit = b ? 1 : 0;
      if (a === b) { r = a ? rOn : rOff; c = a ? 0 : 1; }
      else {
        const q = clamp((el - SETGAP * si - STAG * k) / DUR, 0, 1), e = ease(q), bump = Math.sin(Math.PI * q);
        r = mix(a ? rOn : rOff, b ? rOn : rOff, e) + P * .14 * bump; z = 4 + 18 * bump;
        c = b ? (q < .35 ? 1 : q < 1 ? 2 : 0) : (q < .5 ? 0 : 1);
        lit = mix(a ? 1 : 0, b ? 1 : 0, e);
      }
      count += lit;
      const p = proj(g, base[0], base[1], z);
      pp[k] = p;
      paths[CLS[c] + lvl(r * p[2])] += "M" + f(p[0]) + " " + f(p[1]) + "h0";
    }
    for (const id in paths) {
      const l = +id.replace(/\D+/, ""), d = paths[id], key = "m" + si + id;
      if (S.shown[key] !== d) { E[key].setAttribute("d", d); E[key].setAttribute("stroke-width", f(2 * (l + .5) / (LV - 1) * RMAX)); S.shown[key] = d; }
    }
    // The words of this set: name, count, what was chosen here, the points over Base, the rail and the share
    const b = g.sets[si], x1 = b.x0 + g.bw, has = s.total[B] != null, had = s.total[A] != null;
    E["set" + si].setAttribute("opacity", f(mix(had ? 1 : .42, has ? 1 : .42, e9)));
    const shownState = e9 < .5 ? A : B, on = s.total[shownState] != null;
    text("nm" + si, s.name); at(E["nm" + si], proj(g, b.x0, b.y0, 10));
    text("cv" + si, on ? String(Math.round(count)) : "");
    text("co" + si, on ? ` of ${s.n}` : "");
    at(E["ct" + si], proj(g, x1, b.y0 + (narrow.matches ? 120 : 116), 12));
    text("sb" + si, `${s.n} ${s.unit}, ${s.chosen}`); at(E["sb" + si], proj(g, b.x0, b.y0 + F.sub + 10, 10));
    const big = E["bg" + si];
    if (on) { text("bg" + si, sgn(100 * (count - s.total[0]) / s.n)); big.setAttribute("class", "big"); big.setAttribute("font-size", F.big); }
    else { text("bg" + si, "Not run here"); big.setAttribute("class", "big off"); big.setAttribute("font-size", F.cnt); }
    at(big, proj(g, b.x0 - 3, b.y0 + (narrow.matches ? 96 : 92), 14));
    big.setAttribute("opacity", f(Math.abs(1 - 2 * e9) * (had === has ? 0 : 1) + (had === has ? 1 : 0)));
    text("bl" + si, on ? "points over Base, T 1.0" : ""); at(E["bl" + si], proj(g, b.x0, b.y0 + (narrow.matches ? 120 : 116), 12));
    const rx = v => b.x0 + g.bw * v / s.n, ry = b.rail, seg = (x0, x1, y0, y1) => { const p = proj(g, x0, y0, 6), q = proj(g, x1, y1, 6); return `M${f(p[0])} ${f(p[1])}L${f(q[0])} ${f(q[1])}`; };
    E["tr" + si].setAttribute("d", seg(b.x0, x1, ry, ry));
    E["fl" + si].setAttribute("d", on || had ? seg(b.x0, rx(count), ry, ry) : "");
    E["tb" + si].setAttribute("d", seg(rx(s.total[0]), rx(s.total[0]), ry - 5, ry + 5));
    E["tk" + si].setAttribute("d", seg(rx(s.total[2]), rx(s.total[2]), ry - 8, ry + 8));
    text("rl" + si, `${s.rl}: ${s.total[2]} of ${s.n}`); at(E["rl" + si], proj(g, x1, ry + F.small + 10, 8));
    text("sh" + si, `Base + cue: ${s.share} % of RL's gain`); at(E["sh" + si], proj(g, b.x0, ry + 2 * F.small + 22, 8));
    if (s.foot) { text("ft" + si, s.foot); at(E["ft" + si], proj(g, b.x0, ry + 3 * F.small + 30, 8)); }
    // The open mark: a ring; for a code or general mark, also a dashed outline around its benchmark's or subject's rows
    if (S.open && S.open[0] === PREFIX[si]) {
      const k = si ? Number(S.open.slice(1)) : SLOT[Number(S.open.slice(1))], p = pp[k];
      if (p) {
        const rr = P * .66 * p[2];
        sel = `M${f(p[0] - rr)} ${f(p[1])}a${f(rr)} ${f(rr)} 0 1 0 ${f(2 * rr)} 0a${f(rr)} ${f(rr)} 0 1 0 ${f(-2 * rr)} 0`;
        if (si) {
          const m = list[k], gr = s.groups[m.g], r0 = b.rows[m.g], y0 = b.top + (r0.row + .8 * r0.gaps) * P - 2, y1 = y0 + Math.ceil(gr.n / COLS) * P + 4;
          const q = [[b.x0 - 3, y0], [x1 + 3, y0], [x1 + 3, y1], [b.x0 - 3, y1]].map(([x, y]) => proj(g, x, y, 4));
          grp = "M" + q.map(v => f(v[0]) + " " + f(v[1])).join("L") + "Z";
        }
      }
    }
  });
  E.sel.setAttribute("d", sel); E.grp.setAttribute("d", grp);
  const k0 = proj(g, g.key[0], g.key[1], 8), k1 = proj(g, g.key[0] + 74, g.key[1], 8);
  E.kd0.setAttribute("cx", f(k0[0])); E.kd0.setAttribute("cy", f(k0[1])); text("kt0", "Right"); at(E.kt0, [k0[0] + 11, k0[1]], F.small * .35);
  E.kd1.setAttribute("cx", f(k1[0])); E.kd1.setAttribute("cy", f(k1[1])); text("kt1", "Wrong"); at(E.kt1, [k1[0] + 11, k1[1]], F.small * .35);
  const k2 = narrow.matches ? proj(g, g.key[0] + 160, g.key[1], 8) : proj(g, g.key[0] + 160, g.key[1], 8);
  text("kt2", narrow.matches ? "One answer per item, T 1.0" : "One answer per item, T 1.0. Code and general: marks fill each row by count, not by item.");
  at(E.kt2, k2, F.small * .35);
}

/* Always on: the plate sways by a few degrees and leans toward the mouse. About 30 frames a second. With reduced
   motion the page shows one still frame per state. */
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 30) return;
  S.last = now;
  const t = now / 1000;
  V.px += (V.tx - V.px) * .1; V.py += (V.ty - V.py) * .1;
  aim(3 * Math.sin(t * .13) + 3 * V.px, 1.6 * Math.sin(t * .09) - 1.6 * V.py);
  draw(now);
}
function setState(st, opts = {}) {
  const quick = still.matches || opts.instant;
  S.from = quick ? st : S.st; S.st = st; S.t0 = quick ? -1e9 : performance.now();
  $("switch").querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-pressed", k === st));
  $("hint").textContent = STATES[st].note + " Click a mark to open it.";
  $("svg").setAttribute("aria-label", STATES[st].name + ", right of each set: " +
    SETS.map(s => s.total[st] == null ? `${s.name} not run` : `${s.name} ${s.total[st]} of ${s.n}`).join(", ") + ". Enter opens a problem.");
  if (still.matches) { aim(0, 0); draw(performance.now()); }
}

/* The side column: the five panels, one MATH-500 problem, or one benchmark or subject of the other two sets. */
let TX = null;
const texts = () => TX || (TX = JSON.parse($("texts").textContent));
const OUT = { r: "right", w: "wrong", c: "cut off at 16,384 tokens" };
const cueSpan = s => s.startsWith(C.cue) ? `<span class="cue">${esc(C.cue.replace(/\n/g, "↵"))}</span>${esc(s.slice(C.cue.length))}` : esc(s);
const startOf = (who, s, extra) => `<div class="txt"><p class="tcap">Start of the answer, ${who}${extra ? ", " + extra : ""}</p><p data-math>${cueSpan(s)}…</p></div>`;
function mathPane(i) {
  const m = MK[0][SLOT[i]], [q, gold, e0, e1, s0, s1] = texts().math[i];
  const row = (st, o, ans) => `<li${S.st === st ? ' class="now"' : ""}><span class="who">${STATES[st].name}</span>: <span class="${o === "r" ? "on" : ""}">${OUT[o]}</span>` +
    (ans != null ? `, answer <span data-math>${ans ? esc(ans) : "none found"}</span>` : "") + "</li>";
  return `<div class="dhead"><h2>MATH-500, problem ${i}</h2><button class="close" data-open="">Close</button></div>` +
    `<p class="lead q" data-math>${esc(q)}</p>` +
    `<ul class="facts"><li>Reference answer: <span class="on" data-math>${esc(gold)}</span>. One answer per setting, T 1.0.</li>` +
    row(0, m.o[0], e0) + row(1, m.o[1], e1) + row(2, m.o[2], null) + "</ul>" +
    startOf("Base", s0) + startOf("Base + cue", C.cue + s1) +
    `<p class="note">RL's answer texts are not committed per problem, only whether each is right.</p>` +
    `<div class="steps"><button data-step="-1">‹ Previous problem</button><button data-step="1">Next problem ›</button></div>`;
}
function groupPane(si, k) {
  const s = SETS[si], m = MK[si][k], gr = s.groups[m.g], X = C.example[s.key];
  const head = si === 1 ? `Code, ${gr.name}` : `General questions, ${gr.name}`;
  const rows = [0, 1, 2, 3].filter(st => gr.right[st] != null).map(st => `<li${S.st === st ? ' class="now"' : ""}><span class="who">${STATES[st].name}${si === 1 && st === 2 ? " on code" : ""}</span>: ${gr.right[st]} of ${gr.n}</li>`).join("");
  const keys = si === 1 ? [["Base", "base_plain"], ["Base + cue", "base_mathcue"], ["RL on code", "rl_plain"]]
    : [["Base", "base_plain"], ["Base + cue", "base_cue"], ["RL", "rl_plain"], ["Think-SFT + cue", "sft_cue"]];
  const ex = keys.map(([who, key]) => {
    const v = X[key], ok = v[0], extra = si === 1 ? `${ok ? "passed" : "failed"}, ${v[1].toLocaleString("en-US")} tokens`
      : `${ok ? "right" : "wrong"}, ${v[1] ? "letter " + v[1] : "no letter"}, ${v[2].toLocaleString("en-US")} tokens`;
    return startOf(who, si === 1 ? v[3] : v[4], extra);
  }).join("");
  return `<div class="dhead"><h2>${esc(head)}</h2><button class="close" data-open="">Close</button></div>` +
    `<p class="lead">This row stands for the ${gr.n} ${s.unit} of ${esc(gr.name)}. The run committed how many were right, not which, so the lit marks fill the row in order and none of them names one ${s.unit.slice(0, -1)}.</p>` +
    `<ul class="facts">${rows}</ul>` +
    `<p class="note">The one ${s.unit.slice(0, -1)} whose answers the run folders store: ${esc(X.uid)}${si === 2 ? " (MMLU-Pro, biology), gold letter " + X.gold : ""}.</p>` +
    `<div class="txt"><p class="tcap">${esc(X.uid)}</p><p data-math>${esc(si === 1 ? X.task : X.question)}</p></div>` + ex;
}
function pane() {
  const o = S.open, p = C.panels.find(p => p[0] === o), si = o ? PREFIX.indexOf(o[0]) : -1;
  if (si >= 0 && !$("texts")) { addEventListener("DOMContentLoaded", pane, { once: true }); return; }  // opened from the address
  $("pane").innerHTML = si === 0 ? mathPane(Number(o.slice(1))) : si > 0 ? groupPane(si, Number(o.slice(1))) : p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${nb(esc(p[2]))}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${nb(esc(x))}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
const valid = x => C.panels.some(p => p[0] === x) || (x[0] === "p" && SLOT[Number(x.slice(1))] != null && /^p\d+$/.test(x)) ||
  (/^[cg]\d+$/.test(x) && Number(x.slice(1)) < MK[PREFIX.indexOf(x[0])].length);
/* The state and what is open are one value in the address: #<base|cue|rl|sft>, then /<panel>, /p<problem>, /c<mark> or
   /g<mark>. Base + cue, the finding, has no name in the address. The first version's #code-cue and #math-cue also mean
   Base + cue. */
const OLD = { "math-cue": 1, "code-cue": 1 };
function address(push) {
  const parts = [S.st === 1 ? "" : STATES[S.st].key, S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function readHash() {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/").filter(Boolean);
  const k = STATES.findIndex(s => s.key === parts[0]), st = k >= 0 ? k : OLD[parts[0]] ?? 1;
  return { st, open: parts.find(valid) || null, named: k >= 0 || parts[0] in OLD };
}
function fromHash() {
  const h = readHash();
  if (h.st !== S.st) setState(h.st);
  S.open = h.open;
  pane();
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "start" }); };
function open(key) {
  const was = S.open;
  S.open = key || null;
  address(true);
  pane();
  if (still.matches) draw(performance.now());
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  else if (!key) $("svg").focus({ preventScroll: true });
}

/* Click a mark to open it: the nearest mark within one place of the pointer, in any set. */
const svg = $("svg");
function svgPoint(e) { const m = svg.getScreenCTM().inverse(); return [m.a * e.clientX + m.c * e.clientY + m.e, m.b * e.clientX + m.d * e.clientY + m.f]; }
function nearest([x, y]) {
  let best = null, bd = (S.g.pitch * .75) ** 2;
  S.pp.forEach((list, si) => list.forEach((q, k) => { const d = (q[0] - x) ** 2 + (q[1] - y) ** 2; if (d < bd) { bd = d; best = [si, k]; } }));
  return best;
}
const keyOf = ([si, k]) => si ? PREFIX[si] + k : "p" + MK[0][k].i;
svg.addEventListener("pointermove", e => { if (e.pointerType === "mouse") svg.style.cursor = nearest(svgPoint(e)) ? "pointer" : "default"; });
svg.addEventListener("click", e => { const b = nearest(svgPoint(e)); if (b) { open(keyOf(b)); show(); } });
document.addEventListener("click", e => {
  const w = e.target.closest("[data-state]"), o = e.target.closest("[data-open]"), s = e.target.closest("[data-step]");
  if (w) { const st = Number(w.dataset.state); if (st !== S.st) { setState(st); address(false); pane(); } }
  if (o) open(o.dataset.open);
  if (s) {
    const k = (SLOT[Number(S.open.slice(1))] + Number(s.dataset.step) + MK[0].length) % MK[0].length;
    open("p" + MK[0][k].i);
    $("pane").querySelector(`[data-step="${s.dataset.step}"]`).focus({ preventScroll: true });
  }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) open("");
  if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && !e.target.closest("button")) {
    const st = clamp(S.st + (e.key === "ArrowRight" ? 1 : -1), 0, STATES.length - 1);
    if (st !== S.st) { setState(st); address(false); pane(); }
  }
  if (e.key === "Enter" && document.activeElement === svg) {  // the first MATH-500 problem that the cue turns right
    e.preventDefault();
    open("p" + MK[0].find(m => m.lit[1] && !m.lit[0]).i);
    show();
  }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); draw(performance.now()); });
still.addEventListener("change", () => { if (still.matches) { setState(S.st, { instant: true }); } });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1; V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("problem").textContent = C.problem;
$("say").innerHTML = nb(esc(C.line)).replace(/([+−]?\d+(?:[.,]\d+)*(?: %)?)/g, "<b>$1</b>");
$("switch").innerHTML = STATES.map((s, k) => `<button data-state="${k}" aria-pressed="false">${esc(s.name)}</button>`).join("");
build();
aim(0, 0);
/* The first view: with no state named in the address, the marks start at Base and light up once to Base + cue. */
const h0 = readHash();
S.open = h0.open;
setState(h0.named || still.matches ? h0.st : 0, { instant: true });
pane();
draw(performance.now());
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
  if (!h0.named) setTimeout(() => { if (S.st === 0 && !location.hash.match(/^#(base|rl|sft)/)) setState(1); }, 900);
}
requestAnimationFrame(frame);
</script>
<script type="application/json" id="texts">__TEXTS__</script>
</body>
</html>
"""

PAGE = PAGE.replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "sets": SETS, "states": STATES, "math": MATH, "cue": DATA["cue_text"],
    "example": {"code": CD["example"], "general": G["example"]}})).replace(
    "__TEXTS__", json.dumps({"math": MATH_TEXT}, ensure_ascii=False).replace("</", "<\\/"))


def _check():  # run from the repository root
    d = M
    # MATH-500: Base and Base + cue from the opening-cue rows, RL from the t1/t2 rows, joined on problem_index
    a = {r["problem_index"]: r for r in json.load(open(d["rows"]))}
    b = {r["problem_index"]: r for r in json.load(open(d["rl_rows"]))}
    assert all(a[i]["t1_right"] == b[i]["t1_right"] for i in a), "the two row files hold different cue runs"
    rl = "".join("r" if b[i]["t2_right"] else "c" if b[i]["t2_cap_hit"] else "w" for i in range(d["n"]))
    assert rl == d["rl_outcome"], "rl_outcome differs from " + d["rl_rows"]
    cells = json.load(open(d["readout"]))["cells"]
    assert (d["base"], d["cue"], d["rl"]) == (cells["base_plain_1.0"]["right_v3"], cells["base_opener_1.0"]["right_v3"], cells["rl_1.0"]["right_v3"])
    assert [sum(m[k] == "r" for m in MATH) for k in (1, 2, 3)] == [d["base"], d["cue"], d["rl"]]
    # Code
    c = json.load(open(CD["artifact"]))
    for s in ST + [REF]:
        cell = c["cells"][s["key"]]
        assert (s["passed"], s["tokens"]) == (cell["all"]["passed"], round(cell["all"]["tokens_per_problem"])), s["key"]
        assert all(CD["bench"][bn][s["key"]] == cell[bn]["passed"] and CD["bench"][bn]["n"] == cell[bn]["n"] for bn in CD["bench"])
        assert CD["no_block"][s["key"]] == cell["all"]["no_block"] and CD["no_overlap"][s["key"]] == cell["all_no_overlap"]["passed"]
    assert all([round(v, 3) for v in (c["differences"][k]["points"], *c["differences"][k]["bootstrap95"])] == CD["diff"][k] for k in CD["diff"])
    for key in ("base_plain", "base_mathcue", "rl_plain"):
        e = {x["uid"]: x for x in json.load(open(f"{R}code1/{key}-01/examples.json"))}[CD["example"]["uid"]]
        assert CD["example"][key] == [e["passed"], e["n_new"], e["cap_hit"], e["text"][:240]], key
        assert CD["example"]["task"] in e["prompt"]
    # General questions: the local file when the branch is merged, else the branch commit's object, else a notice
    def read(path):
        if os.path.exists(path):
            return open(path).read()
        r = subprocess.run(["git", "show", f"{G['commit']}:{path}"], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None
    raw = read(G["artifact"])
    if raw is None:
        print(f"NOTICE: {G['artifact']} is neither in the working tree nor reachable as {G['commit']}; general numbers not checked")
    else:
        o = json.loads(raw)
        for key, v in G["cells"].items():
            cell = o["cells"][key]
            assert v == {"right": cell["all"]["right_v2"], "mmlupro": cell["mmlupro"]["right_v2"], "bbh": cell["bbh"]["right_v2"],
                         "right_v1": cell["all"]["right"], "no_letter": cell["all"]["no_answer_v2"], "cap_hits": cell["all"]["cap_hits"],
                         "tokens": round(cell["all"]["tokens_per_item"])}, key
        keys = ("base_plain", "base_cue", "rl_plain", "sft_cue")
        assert G["groups"] == [[gk, o["cells"]["base_plain"]["groups"][gk][2]] + [o["cells"][k]["groups"][gk][1] for k in keys] for gk, *_ in G["groups"]]
        assert len(G["groups"]) == len(o["cells"]["base_plain"]["groups"])
        assert all(sum(gr[2 + j] for gr in G["groups"]) == G["cells"][k]["right"] for j, k in enumerate(keys))
        od = o["differences"]
        back = lambda k: [round(-od[k]["points"], 1), round(-od[k]["bootstrap95"][1], 1), round(-od[k]["bootstrap95"][0], 1)]
        fwd = lambda k: [round(od[k]["points"], 1), round(od[k]["bootstrap95"][0], 1), round(od[k]["bootstrap95"][1], 1)]
        assert G["diff"] == {"cue": back("base_plain - base_cue | all | v2"), "cue_mmlupro": back("base_plain - base_cue | mmlupro | v2"),
                             "cue_bbh": back("base_plain - base_cue | bbh | v2"), "rl_minus_cue": back("base_cue - rl_plain | all | v2"),
                             "sft_minus_rl": back("rl_plain - sft_cue | all | v2"), "cue_v1": back("base_plain - base_cue | all | v1")}, fwd
        k = "base_plain - base_cue | all | v2"
        assert G["flips"] == {"up": od[k]["only_second"], "down": od[k]["only_first"]}
        for key in keys:
            e = {x["uid"]: x for x in json.loads(read(f"{R}ood1/{key}-01/examples.json"))}[G["example"]["uid"]]
            assert G["example"][key] == [e["right_v2"], e["letter_v2"], e["n_new"], e["cap_hit"], e["text"][:240]], key
        item = json.loads(read(G["items"]))[0]
        assert (item["uid"], item["group"], item["gold"], item["content"]) == (G["example"]["uid"], G["example"]["group"].split("/")[1], G["example"]["gold"], G["example"]["question"])
        print("general numbers match", G["artifact"], "at", "the working tree" if os.path.exists(G["artifact"]) else G["commit"])
    assert GAINS == {"math": 37.2, "code": 19.3, "general": 30.0} and SHARES == {"math": 78, "code": 58, "general": 77}, (GAINS, SHARES)
    assert (IMPUTED["base"], IMPUTED["gain"], IMPUTED["share"]) == (238, 9.6, 51), IMPUTED
    print("DATA matches", d["rows"], d["rl_rows"], d["readout"], "and", CD["artifact"])


if __name__ == "__main__":
    _check()
