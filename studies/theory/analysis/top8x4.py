"""Readout of top8x4-01 (specs/SPEC_top8x4.md): short samples (n_generated <= 1,000) of base + 1x top-8 RL-Math directions,
plain prompt, MATH-500, T 1.0, by the cued base's solve bin (0-4 of 4).

    uv run --no-project --with numpy python studies/theory/analysis/top8x4.py                      # stored sample only (check)
    uv run --no-project --with numpy python studies/theory/analysis/top8x4.py --runs runs/<job> ... --out studies/theory/results/experiments/top8x4-01

Sample 0 is the stored cell (studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json); with --runs, the rows of
the run folders (answers.jsonl, run_cell.py --samples 3) are samples 1-3 and must cover every (problem, sample) exactly once.
--out writes metrics.json, per_problem.json and examples.json there.
"""
import argparse
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RLN = ROOT / "studies" / "rlneurons" / "results"
STORED = RLN / "wsp1" / "full500" / "top8_plain-01" / "per_problem.json"
CUE = RLN / "day1_3" / "math500_base_cue-01" / "rows.jsonl"
N, CUT, CUTS = 500, 1000, (600, 1000, 1500)
EX = ("problem_index", "sample", "unique_id", "seed", "prompt", "text", "gold", "extracted_v3", "score_v3", "n_generated", "cap_hit")


def load(runs):
    stored = json.loads(STORED.read_text())
    assert [p["problem_index"] for p in stored] == list(range(N))
    score = [[p["score_v3"]] for p in stored]
    tok = [[p["n_generated"]] for p in stored]
    cap = [[p["cap_hit"]] for p in stored]
    rows = [json.loads(line) for r in runs for line in open(pathlib.Path(r) / "answers.jsonl")]
    if runs:
        keys = sorted((r["problem_index"], r["sample"]) for r in rows)
        assert keys == sorted((i, s) for i in range(N) for s in range(3)), f"{len(rows)} rows, not every (problem, sample) once"
        assert all(r["attempt"] == 0 for r in rows)
        for r in sorted(rows, key=lambda r: (r["sample"], r["problem_index"])):
            score[r["problem_index"]].append(r["score_v3"])
            tok[r["problem_index"]].append(r["n_generated"])
            cap[r["problem_index"]].append(r["cap_hit"])
    return np.array(score, int), np.array(tok, int), np.array(cap, bool), rows


def bins():
    rows = [json.loads(line) for line in open(CUE)]
    b = np.zeros(N, int)
    seen = set()
    for r in rows:
        if r["attempt"] == 0:
            assert (r["problem_index"], r["sample"]) not in seen
            seen.add((r["problem_index"], r["sample"]))
            b[r["problem_index"]] += r["score_v3"]
    assert len(seen) == 4 * N
    return b


def boot(num, den, n_boot=5000):
    """90 % percentile interval of sum(num) / sum(den), problems resampled; num, den are per-problem arrays."""
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(num), (n_boot, len(num)))
    d = den[idx].sum(1)
    v = num[idx].sum(1)[d > 0] / d[d > 0]
    return [round(float(x), 4) for x in np.percentile(v, [5, 95])]


def rate(right, mask):
    n = int(mask.sum())
    return {"n": n, "right": int(right[mask].sum()), "acc": round(float(right[mask].sum() / n), 4) if n else None}


def readout(score, tok, cap, b):
    k = score.shape[1]
    out = {"n_problems": N, "samples_per_problem": k, "short_cut": CUT,
           "bin_counts": {str(j): int((b == j).sum()) for j in range(5)}}
    out["per_sample"] = [{"sample": s, "right": int(score[:, s].sum()), "cap_hits": int(cap[:, s].sum()),
                          "mean_tokens": round(float(tok[:, s].mean()), 1), "short": int((tok[:, s] <= CUT).sum())}
                         for s in range(k)]
    bb = np.repeat(b[:, None], k, 1)
    for c in CUTS:
        short = tok <= c
        r = {"short_share": round(float(short.mean()), 4),
             "short_share_ci90": boot(short.sum(1), np.full(N, k)),
             "short_acc": rate(score, short), "short_acc_ci90": boot((score * short).sum(1), short.sum(1)),
             "short_acc_bin4": rate(score, short & (bb == 4)), "short_acc_bin01": rate(score, short & (bb <= 1))}
        if c == CUT:
            r["short_acc_by_bin"] = {str(j): rate(score, short & (bb == j)) for j in range(5)}
            r["long_acc_by_bin"] = {str(j): rate(score, ~short & (bb == j)) for j in range(5)}
            ns = short.sum(1)
            r["short_per_problem"] = {str(j): int((ns == j).sum()) for j in range(k + 1)}
            both = (ns > 0) & (ns < k)
            r["both_share_all"] = round(float(both.mean()), 4)
            r["both_share_of_with_short"] = round(float(both.sum() / (ns > 0).sum()), 4) if (ns > 0).any() else None
            r["short_in_bin4_share"] = round(float((short & (bb == 4)).sum() / short.sum()), 4) if short.any() else None
            r["bin4_share_of_samples"] = round(float((b == 4).mean()), 4)
        out[f"cut_{c}"] = r
    m = out[f"cut_{CUT}"]
    lo, hi = m["short_share_ci90"]
    alo, ahi = m["short_acc_ci90"]
    b4 = m["short_acc_bin4"]
    out["verdict"] = {
        "P1a_share_ci_outside_10_15": hi < 0.10 or lo > 0.15,
        "P1b_acc_ci_outside_35_65": ahi < 0.35 or alo > 0.65,
        "P1c_bin4_short_acc_ge_85": b4["acc"] is not None and b4["acc"] >= 0.85,
        "P1d_both_lt_half_of_with_short": m["both_share_of_with_short"] is not None and m["both_share_of_with_short"] < 0.5,
        "P2_tested_bin4_n_ge_10": b4["n"] >= 10,
        "P2a_bin4_short_acc_lt_85": b4["n"] >= 10 and b4["acc"] < 0.85,
        "P2b_short_not_concentrated_bin4": m["short_in_bin4_share"] is not None and m["short_in_bin4_share"] <= m["bin4_share_of_samples"],
    }
    v = out["verdict"]
    v["P1_refuted"] = v["P1a_share_ci_outside_10_15"] or v["P1b_acc_ci_outside_35_65"] or v["P1c_bin4_short_acc_ge_85"] or v["P1d_both_lt_half_of_with_short"]
    v["P2_refuted"] = v["P2a_bin4_short_acc_lt_85"] or v["P2b_short_not_concentrated_bin4"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="*", default=[])
    ap.add_argument("--out")
    a = ap.parse_args()
    score, tok, cap, rows = load(a.runs)
    b = bins()
    m = readout(score, tok, cap, b)
    print(json.dumps(m, indent=1))
    if not a.out:
        return
    assert score.shape[1] == 4, "--out needs the 3 new samples"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
    (out / "per_problem.json").write_text(json.dumps(
        [{"problem_index": i, "bin": int(b[i]), "score_v3": score[i].tolist(), "n_generated": tok[i].tolist()} for i in range(N)]) + "\n")
    new = sorted(rows, key=lambda r: (r["problem_index"], r["sample"]))
    ex = {"rule": f"lowest (problem, sample) among new samples with n_generated <= {CUT}, scored right and scored wrong; full text; "
                  "'sample' is run_cell's index (readout sample = sample + 1)"}
    for side in ("right", "wrong"):
        r = next(r for r in new if r["n_generated"] <= CUT and r["score_v3"] == (side == "right"))
        ex[side] = {k: r[k] for k in EX} | {"bin": int(b[r["problem_index"]])}
    (out / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")


if __name__ == "__main__":
    main()
