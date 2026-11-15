"""Direct test rlfail-01 of round-15/account-1/c3 (specs/SPEC_direct_rlfail.md).

    uv run --no-project --with numpy python studies/theory/analysis/direct_rlfail.py --runs ../iterate-hack/runs

On hard328 problems where RL plain has 0 of 4 attempt-0 samples right (grader v3), R = right samples of the 1.5x top-8
edit / right samples of the cued base (attempt 0, samples 0-3). 90 % percentile bootstrap over problems.
--runs is the folder holding runs/<job>/answers.jsonl (raw text, used only for examples.json).
Writes studies/theory/results/direct/rlfail-01/.
"""
import argparse
import json
import pathlib
import subprocess

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
D13 = ROOT / "studies" / "rlneurons" / "results" / "day1_3"
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "rlfail-01"
RUNS = {"edit": "hard328_top8x1.5_cue_s4-01", "base": "hard328_base_cue_s4r2-01", "rl": "hard328_rl_plain_s4r2-01"}
ACCOUNT, NULL = (0.75, 4.0), (0.0, 0.5)
B = 10000


def load(name):
    """Attempt-0 rows as (328, 4) arrays of right and cap hit, problems in order of problem_index."""
    rows = [json.loads(line) for line in open(D13 / name / "rows.jsonl")]
    rows = [r for r in rows if r["attempt"] == 0]
    probs = sorted({r["problem_index"] for r in rows})
    pos = {p: k for k, p in enumerate(probs)}
    assert sorted((pos[r["problem_index"]], r["sample"]) for r in rows) == [(p, s) for p in range(328) for s in range(4)], name
    right, cap = np.zeros((328, 4), int), np.zeros((328, 4), bool)
    for r in rows:
        right[pos[r["problem_index"]], r["sample"]] = r["score_v3"]
        cap[pos[r["problem_index"]], r["sample"]] = r["cap_hit"]
    return right, cap, probs


def ratio_ci(e, b, rng):
    idx = rng.integers(0, len(e), size=(B, len(e)))
    num, den = e[idx].sum(1), b[idx].sum(1)
    r = np.where(den > 0, num / np.maximum(den, 1), np.inf)  # B = 0 in a resample counts as an infinite ratio
    return float(e.sum() / b.sum()), float(np.quantile(r, 0.05)), float(np.quantile(r, 0.95)), int((den == 0).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=pathlib.Path, default=ROOT / "runs")
    args = ap.parse_args()

    data = {k: load(v) for k, v in RUNS.items()}
    assert data["edit"][2] == data["base"][2] == data["rl"][2]
    probs = data["edit"][2]
    er, ec = data["edit"][:2]
    br, bc = data["base"][:2]
    rr, _ = data["rl"][:2]
    # instrument check: totals reproduce the stored counts
    assert (er.sum(), br.sum(), rr.sum()) == (801, 634, 800), (er.sum(), br.sum(), rr.sum())

    sel = rr.sum(1) == 0
    P = int(sel.sum())
    e, b = er[sel].sum(1), br[sel].sum(1)
    R, lo, hi, zero_den = ratio_ci(e, b, np.random.default_rng(0))
    # planted failure: an edit that copies RL's flags gives R = 0
    assert rr[sel].sum() / b.sum() == 0.0

    n = 4 * P
    if lo >= ACCOUNT[0] and hi <= ACCOUNT[1] and n >= 50:
        verdict = "holds"
    elif hi < ACCOUNT[0] or lo > ACCOUNT[1]:
        verdict = "refuted"
    else:
        verdict = "undecided"
    where_null = "inside" if lo >= NULL[0] and hi <= NULL[1] else ("outside (above)" if lo > NULL[1] else "overlaps")

    rest = ~sel
    metrics = {
        "spec": "studies/theory/specs/SPEC_direct_rlfail.md",
        "mechanism": "round-15/account-1/c3",
        "statistic": "E/B: edit right samples / cued base right samples (attempt 0, samples 0-3) on hard328 problems with RL plain 0 of 4 right, grader v3",
        "value": R, "ci90": [lo, hi], "bootstrap": {"resamples": B, "rng": "numpy default_rng(0)", "unit": "problem", "resamples_with_base_right_0_counted_as_infinite": zero_den},
        "n_problems": P, "n_edit_samples": n, "n_base_samples": n,
        "edit_right": int(e.sum()), "base_right": int(b.sum()), "rl_right": int(rr[sel].sum()),
        "problems_edit_any_right": int((e > 0).sum()), "problems_base_any_right": int((b > 0).sum()),
        "problems_both_zero": int(((e == 0) & (b == 0)).sum()),
        "edit_cap_hits": int(ec[sel].sum()), "base_cap_hits": int(bc[sel].sum()),
        "null_value_full_copy": 0.0, "null_value_two_thirds_copy": 1 / 3,
        "range_account1": list(ACCOUNT), "range_null": list(NULL),
        "verdict": verdict, "interval_vs_null_range": where_null,
        "descriptive": {
            "ratio_rl_1to4": ratio_ci(er[rest].sum(1), br[rest].sum(1), np.random.default_rng(1)),
            "n_problems_rl_1to4": int(rest.sum()),
            "ratio_all_328": ratio_ci(er.sum(1), br.sum(1), np.random.default_rng(2)),
            "totals_all_328": {"edit": int(er.sum()), "base": int(br.sum()), "rl": int(rr.sum())},
        },
        "instrument_checks": {"totals_reproduce_801_634_800": True, "planted_copy_rl_gives_0": True},
    }
    if verdict == "undecided":
        half = (hi - lo) / 2
        gap = min(abs(R - ACCOUNT[0]), abs(R - ACCOUNT[1]))
        metrics["n_to_decide"] = int(np.ceil(n * (half / gap) ** 2)) if gap > 0 else None
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    # examples: one edit row entering the statistic scored right, one scored wrong (finished, not cap hit)
    sel_probs = [probs[k] for k in np.flatnonzero(sel)]
    job = json.loads((D13 / RUNS["edit"] / "run.json").read_text())["job_id"]
    raw = {(r["problem_index"], r["sample"]): r for r in map(json.loads, open(args.runs / job / "answers.jsonl"))}
    pos = {p: k for k, p in enumerate(probs)}
    ex = {}
    for label, want in (("right", 1), ("wrong", 0)):
        p, s = next((p, s) for p in sel_probs for s in range(4) if er[pos[p], s] == want and not ec[pos[p], s])
        r = raw[(p, s)]
        assert r["score_v3"] == want
        ex[label] = {"run": RUNS["edit"], "job": job, "problem_index": p, "sample": s,
                     "rl_right_of_4": int(rr[pos[p]].sum()), "base_right_of_4": int(br[pos[p]].sum()),
                     "prompt": r["prompt"], "gold": r["gold"], "extracted_v3": r["extracted_v3"],
                     "score_v3": r["score_v3"], "n_new": r["n_new"], "answer_tail": r["text"][-1500:]}
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")

    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({"spec": metrics["spec"], "commit": commit, "board": "work-1fde65",
                                              "command": "uv run --no-project --with numpy python studies/theory/analysis/direct_rlfail.py --runs ../iterate-hack/runs",
                                              "inputs": [str((D13 / v).relative_to(ROOT)) for v in RUNS.values()]}, indent=1) + "\n")
    print(json.dumps({k: metrics[k] for k in ("value", "ci90", "n_problems", "n_edit_samples", "edit_right", "base_right", "verdict", "interval_vs_null_range")}))
    print(json.dumps(metrics["descriptive"]))


if __name__ == "__main__":
    main()
