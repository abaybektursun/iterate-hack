"""Direct test of round-09/grader-m01: at RL step 100 the cue adds nothing beyond seed scatter (specs/SPEC_direct_cue100.md).

    uv run --no-project --with numpy python studies/theory/analysis/direct_cue100.py

Pools the 4 stored MATH-500 samples per arm (step 100 plain, step 100 cue), computes the paired per-problem
cue-minus-plain difference D in problems per 500, a paired bootstrap over problems, a per-problem label permutation,
the single-sample seed scatter within and between arms, and the same rule on step 400 minus step 100 plain as a
positive control. Writes studies/theory/results/direct/cue100-01/.
"""
import itertools
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
CK = ROOT / "studies" / "rlneurons" / "results" / "ckptcue"
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "cue100-01"
N, K, B = 500, 4, 10000


def load(cell):
    """(500, 4) arrays of score_v3, extracted answer, cap hit, tokens: sample 0 from <cell>-01, samples 1-3 from <cell>_s123-01."""
    rows = json.load(open(CK / f"{cell}-01" / "per_problem.json"))
    rows = [dict(r, sample=0) for r in rows]
    rows += [json.loads(line) for line in open(CK / f"{cell}_s123-01" / "rows.jsonl")]
    keys = sorted((r["problem_index"], r["sample"]) for r in rows)
    assert keys == [(p, s) for p in range(N) for s in range(K)], cell
    right = np.zeros((N, K), int)
    ans = np.empty((N, K), object)
    cap = np.zeros((N, K), bool)
    tok = np.zeros((N, K), int)
    gold = {}
    for r in rows:
        p, s = r["problem_index"], r["sample"]
        right[p, s], ans[p, s], cap[p, s] = r["score_v3"], r["extracted_v3"], r["cap_hit"]
        tok[p, s] = r.get("n_generated", r.get("n_new"))
        if "gold" in r:
            gold[p] = r["gold"]
    return right, ans, cap, tok, gold


def ci(x, level):
    a = (100 - level) / 2
    return [float(np.percentile(x, a)), float(np.percentile(x, 100 - a))]


def paired(a, b):
    """D = 500 * mean_i (mean a_i - mean b_i), bootstrap over problems (rng 0), label permutation per problem (rng 1)."""
    d = a.mean(1) - b.mean(1)
    D = float(N * d.mean())
    idx = np.random.default_rng(0).integers(0, N, (B, N))
    boot = N * d[idx].mean(1)
    pool = np.concatenate([a, b], 1)
    rng = np.random.default_rng(1)
    perm = np.empty(B)
    for t in range(B):
        sh = rng.permuted(pool, axis=1)
        perm[t] = N * (sh[:, :K].mean(1) - sh[:, K:].mean(1)).mean()
    p = float((np.abs(perm) >= abs(D) - 1e-9).mean())
    refuted = ci(boot, 95)[0] > 0.0 and p < 0.05
    return {"D_per_500": D, "ci95": ci(boot, 95), "ci90": ci(boot, 90), "perm_p_two_sided": p,
            "perm_abs_D_95th": float(np.percentile(np.abs(perm), 95)), "rule_refutes": bool(refuted),
            "share_bootstrap_D_le_0": float((boot <= 0).mean())}


def lower95_by_seed(a, b, seeds):
    """Robustness only (added after the first readout): the 95 % lower bound of D for other bootstrap seeds."""
    d = a.mean(1) - b.mean(1)
    return [float(np.percentile(N * d[np.random.default_rng(s).integers(0, N, (B, N))].mean(1), 2.5)) for s in seeds]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pl, pl_ans, pl_cap, pl_tok, gold = load("s0100_plain")
    cu, cu_ans, cu_cap, cu_tok, gold_c = load("s0100_cue")
    s4, *_ = load("s0400_plain")
    assert gold == gold_c and len(gold) == N

    # Check against readout3.json and result-6832a8.
    r3 = json.load(open(CK / "readout3.json"))["cells"]
    for name, arr in (("s0100_plain", pl), ("s0100_cue", cu), ("s0400_plain", s4)):
        want = [s["right"] for s in r3[name]["samples"]]
        got = arr.sum(0).tolist()
        assert all(abs(g - w) <= 2 for g, w in zip(got, want)), (name, got, want)
    assert abs(pl.sum() - 1670) <= 2 and abs(cu.sum() - 1704) <= 2, (pl.sum(), cu.sum())

    main_test = paired(cu, pl)
    control = paired(s4, pl)

    # Null B (a): folder against folder (sample 0 vs mean of samples 1-3), per 500.
    def folder(a, b):
        return float(N * (a - b).mean())
    null_b_folder = {
        "plain s0 minus plain s123": folder(pl[:, 0], pl[:, 1:].mean(1)),
        "cue s0 minus cue s123": folder(cu[:, 0], cu[:, 1:].mean(1)),
        "cue s0 minus plain s0": folder(cu[:, 0], pl[:, 0]),
        "cue s123 minus plain s123": folder(cu[:, 1:].mean(1), pl[:, 1:].mean(1)),
    }
    # Null B (b): every single-sample pair.
    within = {"plain": [int(pl[:, i].sum() - pl[:, j].sum()) for i, j in itertools.combinations(range(K), 2)],
              "cue": [int(cu[:, i].sum() - cu[:, j].sum()) for i, j in itertools.combinations(range(K), 2)]}
    between = [int(cu[:, i].sum() - pl[:, j].sum()) for i in range(K) for j in range(K)]
    within_abs = [abs(x) for v in within.values() for x in v]

    # Descriptive: problems not all-right or all-wrong in both arms.
    tot = cu.sum(1) + pl.sum(1)
    mixed = (tot > 0) & (tot < 2 * K)
    d = cu.mean(1) - pl.mean(1)

    # Per-problem cue-right minus plain-right counts (out of 4), for the reading.
    diff_counts = (cu.sum(1) - pl.sum(1)).astype(int)
    hist = {str(v): int((diff_counts == v).sum()) for v in range(-K, K + 1)}

    readout = {
        "spec": "studies/theory/specs/SPEC_direct_cue100.md",
        "mechanism": "round-09/grader-m01",
        "n_problems": N, "samples_per_arm": K, "problems_dropped": 0,
        "right_per_sample": {"s0100_plain": pl.sum(0).tolist(), "s0100_cue": cu.sum(0).tolist(),
                             "s0400_plain": s4.sum(0).tolist()},
        "totals": {"s0100_plain": int(pl.sum()), "s0100_cue": int(cu.sum()), "s0400_plain": int(s4.sum())},
        "deciding": {"name": "D = 500 * mean_i (cue right rate_i - plain right rate_i), step 100", **main_test},
        "null_A_permutation": {"p_two_sided": main_test["perm_p_two_sided"],
                               "abs_D_95th_percentile_under_permutation": main_test["perm_abs_D_95th"]},
        "null_B_folder_per_500": null_b_folder,
        "null_B_single_sample_pairs": {
            "within_arm_differences": within, "within_arm_max_abs": max(within_abs),
            "between_arm_cue_minus_plain": between, "between_arm_mean": float(np.mean(between)),
            "between_arm_pairs_above_within_max": int(sum(x > max(within_abs) for x in between)),
            "single_cell_gap_sample0": int(cu[:, 0].sum() - pl[:, 0].sum())},
        "descriptive_mixed_problems": {"n": int(mixed.sum()), "D_per_500_scaled": float(N * d[mixed].mean()),
                                       "D_problems_sum": float(d[mixed].sum())},
        "per_problem_cue_minus_plain_right_of_4": hist,
        "cap_hits": {"s0100_plain": int(pl_cap.sum()), "s0100_cue": int(cu_cap.sum())},
        "positive_control_s0400_minus_s0100_plain": control,
        "robustness_not_deciding": {"ci95_lower_for_bootstrap_seeds_1_to_20": lower95_by_seed(cu, pl, range(1, 21))},
        "rule": "refuted if lower 95 % bound of D > 0.0 AND permutation p < 0.05; else holds",
        "verdict": ("refuted" if main_test["rule_refutes"] else "holds") if control["rule_refutes"] else "undecided",
    }
    json.dump(readout, open(OUT / "readout.json", "w"), indent=1)

    # Examples: one tie problem with mixed outcomes (supports), the problem with the largest cue lead (against).
    def item(p):
        return {"problem_index": int(p), "gold": gold[p],
                "cue": [{"sample": s, "extracted_v3": cu_ans[p, s], "score_v3": int(cu[p, s]), "cap_hit": bool(cu_cap[p, s]),
                         "tokens": int(cu_tok[p, s])} for s in range(K)],
                "plain": [{"sample": s, "extracted_v3": pl_ans[p, s], "score_v3": int(pl[p, s]), "cap_hit": bool(pl_cap[p, s]),
                           "tokens": int(pl_tok[p, s])} for s in range(K)],
                "cue_minus_plain_right_of_4": int(diff_counts[p])}
    tie = next(p for p in range(N) if diff_counts[p] == 0 and 0 < cu[p].sum() < K)
    lead = int(np.argmax(diff_counts))
    json.dump({"supports_tie": item(tie), "against_largest_cue_lead": item(lead)}, open(OUT / "examples.json", "w"),
              indent=1)

    # Rows for reading (reading.md is written by hand): the 10 problems with the largest |cue - plain| right counts.
    for p in sorted(range(N), key=lambda p: (-abs(diff_counts[p]), p))[:10]:
        print(f"{p}\tgold={gold[p]}\tcue={cu[p].tolist()} {list(cu_ans[p])} cap={cu_cap[p].astype(int).tolist()}"
              f"\tplain={pl[p].tolist()} {list(pl_ans[p])} cap={pl_cap[p].astype(int).tolist()}")
    print(json.dumps({k: readout[k] for k in ("totals", "deciding", "null_B_folder_per_500", "null_B_single_sample_pairs",
                                               "descriptive_mixed_problems", "per_problem_cue_minus_plain_right_of_4",
                                               "cap_hits", "positive_control_s0400_minus_s0100_plain", "verdict")},
                     indent=1))


if __name__ == "__main__":
    main()
