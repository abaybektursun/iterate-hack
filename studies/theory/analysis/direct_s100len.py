"""Direct test s100len (studies/theory/specs/SPEC_direct_s100len.md). Laptop, stored rows only.

Geometric mean over MATH-500 problems of (median n_new of RL step-100 plain right samples / median n_new of cued-base
right samples), T 1.0 / top-p 1.0, 4 samples per arm, grader v3; final RL in place of step 100 as the null value.

    python3 studies/theory/analysis/direct_s100len.py

Writes studies/theory/results/direct/s100len-01/ (metrics.json, examples.json); refuses an existing metrics.json.
"""
import json
import pathlib
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RL = ROOT / "studies/rlneurons/results"
OUT = ROOT / "studies/theory/results/direct/s100len-01"
ACCOUNT, NULL = (0.88, 1.10), (1.15, 1.60)


def day1_3(name):
    """sample -> problem -> (score_v3, n_new), attempt 0 only."""
    rows = [json.loads(line) for line in open(RL / "day1_3" / name / "rows.jsonl")]
    return [(int(r["problem_index"]), int(r["sample"]), int(r["score_v3"]), int(r["n_new"])) for r in rows if int(r["attempt"]) == 0]


def step100():
    s0 = json.load(open(RL / "ckptcue/s0100_plain-01/per_problem.json"))
    # n_generated = len(out_ids): n_new + 1 (the stop id) for a finished answer, n_new for a cap hit
    out = [(r["problem_index"], 0, r["score_v3"], r["n_generated"] - (0 if r["cap_hit"] else 1)) for r in s0]
    out += [(int(r["problem_index"]), int(r["sample"]), int(r["score_v3"]), int(r["n_new"]))
            for r in map(json.loads, open(RL / "ckptcue/s0100_plain_s123-01/rows.jsonl")) if int(r["attempt"]) == 0]
    return out


def right_medians(rows):
    by = defaultdict(list)
    count = defaultdict(int)
    for p, s, score, n in rows:
        count[p] += 1
        if score == 1:
            by[p].append(n)
    assert len(count) == 500 and set(count.values()) == {4}, sorted(set(count.values()))
    return {p: float(np.median(v)) for p, v in by.items()}


def ratio(a, b, rng):
    ps = sorted(set(a) & set(b))
    r = np.log(np.array([a[p] for p in ps]) / np.array([b[p] for p in ps]))
    boots = np.exp(r[rng.integers(0, len(r), (10_000, len(r)))].mean(axis=1))
    return {"value": float(np.exp(r.mean())), "ci90": [float(np.percentile(boots, 5)), float(np.percentile(boots, 95))],
            "n_problems": len(ps), "share_ratio_above_1": float((r > 0).mean()),
            "median_tokens_numerator": float(np.median([a[p] for p in ps])), "median_tokens_cued_base": float(np.median([b[p] for p in ps]))}


def verdict(ci, n):
    if ACCOUNT[0] <= ci[0] and ci[1] <= ACCOUNT[1] and n >= 50:
        return "holds"
    if ci[1] < ACCOUNT[0] or ci[0] > ACCOUNT[1]:
        return "refuted"
    return "undecided"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / "metrics.json").exists(), "a rerun gets the next folder number"
    s100, base, final = right_medians(step100()), right_medians(day1_3("math500_base_cue-01")), right_medians(day1_3("math500_rl-01"))
    main_ = ratio(s100, base, np.random.default_rng(0))
    null_ = ratio(final, base, np.random.default_rng(0))
    m = {"test": "s100len", "mechanism": "round-15/account-3/c3", "spec": "studies/theory/specs/SPEC_direct_s100len.md",
         "statistic": "geometric mean over problems of median n_new of step-100 plain right samples / median n_new of cued-base right samples",
         "sampling": "T 1.0 / top-p 1.0, max_tokens 16384, 4 samples per arm, attempt 0, grader v3",
         "token_counter": "n_new (tokens before the stop id; cue's 3 prefilled tokens not counted); step-100 sample 0: n_generated - 1 for finished rows",
         "step100_vs_cued_base": main_, "null_final_rl_vs_cued_base": null_,
         "ranges": {"account-3": ACCOUNT, "null": NULL}, "verdict": verdict(main_["ci90"], main_["n_problems"]),
         "problems_solved": {"step100": len(s100), "cued_base": len(base), "final_rl": len(final)},
         "inputs": ["studies/rlneurons/results/ckptcue/s0100_plain-01/per_problem.json", "studies/rlneurons/results/ckptcue/s0100_plain_s123-01/rows.jsonl",
                    "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl", "studies/rlneurons/results/day1_3/math500_rl-01/rows.jsonl"]}
    json.dump(m, open(OUT / "metrics.json", "w"), indent=1)

    a = json.load(open(RL / "ckptcue/s0100_plain-01/examples.json"))["right"]
    b = json.load(open(RL / "day1_3/math500_base_cue-01/examples.json"))["vote"]["right"]
    b0 = b["attempts"][0]
    assert a["problem_index"] == b["problem_index"] == 0 and a["score_v3"] == b0["score_v3"] == 1 and b0["text_chars"] < 2000
    json.dump({"problem_index": 0, "gold": a["gold"],
               "step100_plain_right": {"seed": a["seed"], "n_new": a["n_generated"] - 1, "extracted_v3": a["extracted_v3"], "text": a["text"]},
               "cued_base_right": {"seed": b0["seed"], "n_new": b0["n_new"], "extracted_v3": b0["extracted_v3"], "text": b0["text_last_2000"]},
               "problem_ratio": s100[0] / base[0], "step100_median_right": s100[0], "cued_base_median_right": base[0]},
              open(OUT / "examples.json", "w"), indent=1)
    print(json.dumps({k: m[k] for k in ("step100_vs_cued_base", "null_final_rl_vs_cued_base", "verdict", "problems_solved")}, indent=1))


if __name__ == "__main__":
    main()
