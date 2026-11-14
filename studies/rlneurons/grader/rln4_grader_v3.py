"""Rescore saved MATH-500 cells with graders v1, v2, v3 (studies/rlneurons/SPEC4.md, "Grader v3"). Laptop only, saved JSONL only.

Download each cell from s3://pg-lineage-769063704696/results/<key> (CELLS) to <data>/<name>.jsonl, then

    python -m studies.rlneurons.grader.rln4_grader_v3 --data <dir> --cases      # writes grader/cases.json (audited rows)
    python -m studies.rlneurons.grader.rln4_grader_v3 --data <dir> --out studies/rlneurons/results/rln4/grader_v3/readout.json

Intervals: n13_score.paired_bootstrap with 5,000 resamples, seed 0, 95 % percentile, in points. Fail loud: no try/except.
"""
import argparse
import hashlib
import json
import pathlib
import random

import numpy as np

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

HERE = pathlib.Path(__file__).resolve().parent         # studies/rlneurons/grader: cases.json is written here
STUDY = HERE.parent
CELLS = {
    "base_plain_0.6_n13": ("next_n13/s3gate-03/out/base/base/math500/generations.jsonl", "base, plain prompt, T 0.6 (n13; v1 registered 286)"),
    "base_plain_0.6": ("rlneurons/r3/base-01/out/P_math500.jsonl", "base, plain prompt, T 0.6 (base-01 P)"),
    "base_opener_0.6": ("rlneurons/r3/base-01/out/F_math500.jsonl", "base, opener, T 0.6 (base-01 F)"),
    "base_opener_1.0": ("rlneurons/r4/base_rl-02/out/T1.jsonl", "base, opener, T 1.0 (T1)"),
    "base_plain_1.0": ("rlneurons/r4/modal_t3-01/t3/T3.jsonl", "base, plain prompt, T 1.0 (T3)"),
    "rl_0.6": ("next_n13/s3gate-03/out/rl/rl/math500/generations.jsonl", "RL, plain prompt, T 0.6 (n13; v1 registered 460)"),
    "rl_1.0": ("rlneurons/r4/modal_t2-01/t2/T2.jsonl", "RL, plain prompt, T 1.0 (T2)"),
    "K_fresh": ("rlneurons/r4/modal_k-01/k_b/K_fresh.jsonl", "base, opener, T 0.6, restart 1 on every base_opener_0.6 cap hit"),
    "K_fresh2": ("rlneurons/r4/modal_k-01/k_b/K_fresh2.jsonl", "base, opener, T 0.6, restart 2 on every K_fresh cap hit"),
}
AUDITED = {"base_opener_1.0": [51, 143, 282, 495, 102, 167, 453, 66, 408, 420, 456, 37], "base_plain_1.0": [5, 41, 89, 112],
           "rl_1.0": [205, 298, 419, 420, 36], "K_fresh": [220]}
# Flip review (read by hand on 2026-11-14 from the v1-to-v3 flips this script lists). Keys: (cell, problem_index). Every flip read
# and not listed here was judged correct.
JUDGED_INCORRECT = {
    ("base_plain_1.0", 146): "right-to-wrong: the line-start 'Answer: $\\frac{\\sqrt{3}}{3}$' answers the problem; the model then "
                             "invents a new problem and ends with a mid-line 'Answer: $60$', which v3 takes",
    ("base_plain_1.0", 142): "wrong-to-right, found in a draft draw of 40 (same seed, other cell order; 1 of 40 judged incorrect): "
                             "the box holds 2 x 5! x 5! x 1! (= 28800, the gold) but the line above states 24,000; counted "
                             "incorrect because the model's stated number is wrong",
}
N_BOOT, SEED, SAMPLE = 5000, 0, 40


def bank(p):
    out = {}
    for line in open(p):
        r = json.loads(line)
        assert r["problem_index"] not in out, (p, r["problem_index"])
        out[r["problem_index"]] = r
    return out


def boot(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    lo, hi = S.paired_bootstrap(x, y, n_boot=N_BOOT, seed=SEED)
    return {"n": int(x.size), "diff_points": float(100 * (x.mean() - y.mean())), "ci95": [lo, hi]}


def write_cases(data):
    out = []
    for cell, ids in AUDITED.items():
        b = bank(data / f"{cell}.jsonl")
        out += [{"cell": cell, "problem_index": i, "gold": b[i]["gold"], "text": b[i]["text"]} for i in ids]
    (HERE / "cases.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print("cases", len(out))


def score(data):
    cells, files = {}, {}
    for name in CELLS:
        p = data / f"{name}.jsonl"
        files[name] = {"s3": "s3://pg-lineage-769063704696/results/" + CELLS[name][0], "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        rows = {}
        for i, r in bank(p).items():
            x1 = S.extract(r["text"])[1]
            g2, g3 = R.grade_v2(r["gold"], r["text"]), R.grade_v3(r["gold"], r["text"])
            rows[i] = {"v1": S.grade(r["gold"], x1)["score"], "v2": g2["score_v2"], "v3": g3["score_v3"], "x1": x1, "x3": g3["extracted_v3"],
                       "mode_v3": g3["mode_v3"], "cap": bool(r["cap_hit"]), "rec": r}
        cells[name] = rows
    return cells, files


def example(r, problems, want):
    rec = r["rec"]
    assert problems[rec["problem_index"]]["answer"] == rec["gold"]
    return {"problem_index": rec["problem_index"], "problem": problems[rec["problem_index"]]["problem"], "gold": rec["gold"],
            "extracted_v3": r["x3"], "mode_v3": r["mode_v3"], "score_v3": want, "extracted_v1": r["x1"], "score_v1": r["v1"],
            "answer_prob_v1_span": rec.get("answer_prob"), "cap_hit": r["cap"], "text_tail": rec["text"][-400:]}


def readout(data, out):
    cells, files = score(data)
    problems = json.loads((STUDY / "data" / "rln3" / "math500.json").read_text())
    res = {"grader": "v3 (SPEC4.md, Grader v3)", "files": files, "cells": {}, "flips_v1_to_v3": {}, "differences_v3": {}}
    for name, rows in cells.items():
        rs = [rows[i] for i in sorted(rows)]
        right = next(r for r in rs if r["v3"] == 1)
        wrong = next(r for r in rs if r["v3"] == 0 and r["x3"] is not None)
        res["cells"][name] = {"what": CELLS[name][1], "n": len(rs), "right_v1": sum(r["v1"] for r in rs), "right_v2": sum(r["v2"] for r in rs),
                              "right_v3": sum(r["v3"] for r in rs), "nothing_extracted_v3": sum(r["x3"] is None for r in rs),
                              "cap_hits": sum(r["cap"] for r in rs), "cap_hits_right_v3": sum(r["cap"] and r["v3"] for r in rs),
                              "modes_v3": {m: sum(r["mode_v3"] == m for r in rs) for m in ("boxed", "marker", "none")},
                              "example_right_v3": example(right, problems, 1), "example_wrong_v3": example(wrong, problems, 0)}
        res["flips_v1_to_v3"][name] = {"wrong_to_right": [r["rec"]["problem_index"] for r in rs if r["v1"] == 0 and r["v3"] == 1],
                                       "right_to_wrong": [r["rec"]["problem_index"] for r in rs if r["v1"] == 1 and r["v3"] == 0],
                                       "v2_to_v3_wrong_to_right": sum(r["v2"] == 0 and r["v3"] == 1 for r in rs),
                                       "v2_to_v3_right_to_wrong": sum(r["v2"] == 1 and r["v3"] == 0 for r in rs)}
    # flip review: every right-to-wrong flip, and 40 wrong-to-right flips drawn with random.Random(0)
    up = sorted((c, i) for c, f in res["flips_v1_to_v3"].items() for i in f["wrong_to_right"])
    down = sorted((c, i) for c, f in res["flips_v1_to_v3"].items() for i in f["right_to_wrong"])
    pick = sorted(up[k] for k in random.Random(0).sample(range(len(up)), SAMPLE))
    def item(c, i):
        r = cells[c][i]
        return {"cell": c, "problem_index": i, "gold": r["rec"]["gold"], "extracted_v1": r["x1"], "extracted_v3": r["x3"],
                "tail": r["rec"]["text"][-300:], "judged_incorrect": JUDGED_INCORRECT.get((c, i))}
    res["flip_review"] = {"n_wrong_to_right": len(up), "n_right_to_wrong": len(down),
                          "right_to_wrong": [item(c, i) for c, i in down],
                          "right_to_wrong_judged_incorrect": sum((c, i) in JUDGED_INCORRECT for c, i in down),
                          "sample_wrong_to_right": [item(c, i) for c, i in pick],
                          "sample_judged_incorrect": sum((c, i) in JUDGED_INCORRECT for c, i in pick), "sample_limit": 2,
                          "other_judged_incorrect": [item(c, i) for c, i in JUDGED_INCORRECT if (c, i) not in down and (c, i) not in pick]}
    assert all(k in down or k in up for k in JUDGED_INCORRECT), "a judgement refers to a row that did not flip"
    res["flip_review"]["pass"] = res["flip_review"]["sample_judged_incorrect"] <= 2

    v3 = lambda c: [cells[c][i]["v3"] for i in range(500)]
    for c in ("base_plain_0.6", "base_opener_0.6", "base_opener_1.0", "base_plain_1.0", "rl_0.6", "rl_1.0"):
        assert sorted(cells[c]) == list(range(500)), c
    # restart row (SPEC4 section 2): base_opener_0.6, then K_fresh, then K_fresh2; first finished attempt answers, else the last
    # attempt; an answer whose last attempt hit the cap counts wrong.
    F, K1, K2 = cells["base_opener_0.6"], cells["K_fresh"], cells["K_fresh2"]
    restart, hist, missing = [], {1: 0, 2: 0, 3: 0}, []
    for i in range(500):
        used = [F[i]]
        if used[-1]["cap"]:
            if i not in K1:
                missing.append(i)
                continue
            used.append(K1[i])
            if used[-1]["cap"]:
                if i not in K2:
                    missing.append(i)
                    continue
                used.append(K2[i])
        hist[len(used)] += 1
        restart.append(0 if used[-1]["cap"] else used[-1]["v3"])
    assert not missing, missing
    rl06 = v3("rl_0.6")
    res["restart_row"] = {"n": len(restart), "right_v3": int(sum(restart)), "attempts_hist": hist,
                          "rl_0.6_right_v3": int(sum(rl06)),
                          "rl_0.6_right_v3_capped_counted_wrong": int(sum(0 if cells["rl_0.6"][i]["cap"] else rl06[i] for i in range(500)))}
    D = res["differences_v3"]
    D["rl_1.0 - base_opener_1.0"] = boot(v3("rl_1.0"), v3("base_opener_1.0"))
    D["rl_0.6 - base_opener_0.6"] = boot(rl06, v3("base_opener_0.6"))
    D["base_opener_1.0 - base_opener_0.6"] = boot(v3("base_opener_1.0"), v3("base_opener_0.6"))
    D["rl_1.0 - rl_0.6"] = boot(v3("rl_1.0"), rl06)
    D["base_plain_1.0 - base_plain_0.6"] = boot(v3("base_plain_1.0"), v3("base_plain_0.6"))
    D["restart_row - rl_0.6"] = boot(restart, rl06)
    D["restart_row - rl_0.6 (RL cap hits counted wrong too)"] = boot(restart, [0 if cells["rl_0.6"][i]["cap"] else rl06[i] for i in range(500)])
    res["bootstrap"] = {"n_boot": N_BOOT, "seed": SEED, "interval": "95 % percentile, points"}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, type=pathlib.Path)
    ap.add_argument("--cases", action="store_true")
    ap.add_argument("--out", type=pathlib.Path)
    a = ap.parse_args()
    if a.cases:
        write_cases(a.data)
        return
    res = readout(a.data, a.out)
    for c, v in res["cells"].items():
        print(f"{c:22s} v1 {v['right_v1']:3d} v2 {v['right_v2']:3d} v3 {v['right_v3']:3d} none_v3 {v['nothing_extracted_v3']:3d} cap {v['cap_hits']:3d} n {v['n']}")
    print("restart row", res["restart_row"])
    for k, d in res["differences_v3"].items():
        print(f"{k:55s} {d['diff_points']:+6.1f} [{d['ci95'][0]:+.1f}, {d['ci95'][1]:+.1f}]")
    fr = res["flip_review"]
    print("flips", fr["n_wrong_to_right"], "up", fr["n_right_to_wrong"], "down; down judged incorrect", fr["right_to_wrong_judged_incorrect"],
          "; sample judged incorrect", fr["sample_judged_incorrect"], "of", SAMPLE, "pass", fr["pass"])


if __name__ == "__main__":
    main()
