"""Direct test logodds-01 of round-10/weights-m01 (theory round 14).

Q = ln(e_HI/b_HI) - ln(e_LO/b_LO) on hard328: does the 1.5x top-8 RL-Math edit keep a larger share of cap hits on
problems the base often runs to the cap? Spec: studies/theory/specs/SPEC_direct_logodds.md.
Run: uv run python studies/theory/analysis/direct_logodds.py
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl"
EDIT = ROOT / "studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01/rows.jsonl"
OUT = ROOT / "studies/theory/results/direct/logodds-01"
THRESHOLD = 0.3
B = 10_000


def load(path):
    return [json.loads(line) for line in path.open()]


def cap_matrix(rows):
    """328 x 4 matrix of first-attempt cap-hit flags; rows of attempt 0 only. Row i is the i-th smallest
    problem_index (problem_index is the index in the source set, 0-399, not 0-327)."""
    rows = [r for r in rows if r["attempt"] == 0]
    keys = {(r["problem_index"], r["sample"]) for r in rows}
    assert len(rows) == 1312 and len(keys) == 1312, (len(rows), len(keys))
    pids = sorted({r["problem_index"] for r in rows})
    assert len(pids) == 328
    pos = {p: i for i, p in enumerate(pids)}
    m = np.zeros((328, 4), dtype=int)
    for r in rows:
        assert r["cap_hit"] == (r["finish_reason"] == "length") == (r["n_new"] >= 16384), r
        m[pos[r["problem_index"]], r["sample"]] = int(r["cap_hit"])
    return m, rows, pids


def check_counts(base_rows_all, base, edit):
    # A wrong field must fail: all base rows (restarted attempts included) give 498, not 286.
    wrong = sum(r["cap_hit"] for r in base_rows_all)
    assert wrong == 498 and wrong != 286, wrong
    assert base.sum(0).tolist() == [71, 66, 81, 68], base.sum(0).tolist()
    assert abs(base.sum(0).mean() - 71.5) < 1e-9
    edit_metrics = json.load((EDIT.parent / "metrics.json").open())["counts"]["cap_hits"]
    edit_readout = json.load((EDIT.parent / "readout.json").open())["each_sample"]["cap_hits_attempt_0"]
    assert edit.sum() == edit_metrics == 76, (edit.sum(), edit_metrics)
    assert edit.sum(0).tolist() == edit_readout == [20, 14, 20, 22], edit.sum(0).tolist()


def stats(base, edit):
    k = base[:, 0] + base[:, 1]
    out = {}
    for name, mask in (("HI", k == 2), ("LO", k == 0)):
        n_s = int(mask.sum())
        hb = int(base[mask, 2:].sum())
        he = int(edit[mask].sum())
        b = (hb + 0.5) / (2 * n_s + 1)
        e = (he + 0.5) / (4 * n_s + 1)
        h2 = int(base[mask, 2].sum())
        h3 = int(base[mask, 3].sum())
        b2 = (h2 + 0.5) / (n_s + 1)
        b3 = (h3 + 0.5) / (n_s + 1)
        out[name] = dict(n=n_s, base_hits_s23=hb, edit_hits_s0123=he, b=b, e=e, share_kept=e / b,
                         L=np.log(e / (1 - e)) - np.log(b / (1 - b)),
                         base_hits_s2=h2, base_hits_s3=h3, b2=b2, b3=b3)
    q = np.log(out["HI"]["e"] / out["HI"]["b"]) - np.log(out["LO"]["e"] / out["LO"]["b"])
    d = out["HI"]["L"] - out["LO"]["L"]
    q_null = np.log(out["HI"]["b3"] / out["HI"]["b2"]) - np.log(out["LO"]["b3"] / out["LO"]["b2"])
    return q, d, q_null, out


def bootstrap(base, edit, seed_rng):
    qs, ds, qn = np.empty(B), np.empty(B), np.empty(B)
    for i in range(B):
        idx = seed_rng.integers(0, 328, 328)
        qs[i], ds[i], qn[i], _ = stats(base[idx], edit[idx])
    pct = lambda a: [float(np.percentile(a, 5)), float(np.percentile(a, 95))]
    return pct(qs), pct(ds), pct(qn)


def main():
    base_all = load(BASE)
    base, base_rows, base_pids = cap_matrix(base_all)
    edit, edit_rows, edit_pids = cap_matrix(load(EDIT))
    assert base_pids == edit_pids
    check_counts(base_all, base, edit)

    q, d, q_null, strata = stats(base, edit)
    q_ci, d_ci, qn_ci = bootstrap(base, edit, np.random.default_rng(0))
    q_ci_plan, d_ci_plan, _ = bootstrap(base, edit, np.random.default_rng(20261115))
    n = strata["HI"]["n"] + strata["LO"]["n"]

    if n >= 50 and q_ci[0] > THRESHOLD:
        verdict = "holds"
    elif q_ci[1] < THRESHOLD:
        verdict = "refuted"
    else:
        verdict = "undecided"

    OUT.mkdir(parents=True, exist_ok=True)
    metrics = {
        "mechanism": "round-10/weights-m01",
        "statistic": "Q = ln(e_HI/b_HI) - ln(e_LO/b_LO); strata from base samples 0-1, b from base samples 2-3",
        "Q": float(q), "Q_90ci": q_ci,
        "D_logodds_HI_minus_LO": float(d), "D_90ci": d_ci,
        "Q_null_base3_vs_base2": float(q_null), "Q_null_90ci": qn_ci,
        "Q_90ci_plan_seed_20261115": q_ci_plan, "D_90ci_plan_seed_20261115": d_ci_plan,
        "strata": {s: {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in strata[s].items()}
                   for s in strata},
        "n": n, "n_problems": 328, "bootstrap": {"resamples": B, "unit": "problem", "rng": "numpy default_rng(0)"},
        "null_value": 0.0, "threshold": THRESHOLD,
        "counts_check": {"base_attempt0_cap_hits_per_sample": base.sum(0).tolist(),
                         "edit_cap_hits_per_sample": edit.sum(0).tolist(),
                         "base_all_attempts_cap_hits_wrong_field": 498},
        "verdict": verdict,
        "n_to_decide": ("At Q = 0.39 the 90 % half-width (0.65) must fall below 0.09 for the lower bound to clear 0.3: "
                        "about 50x the data, roughly 14,000 problems in HI + LO (or many more samples per problem)."),
        "raw_rows_read": ("Read 6 HI and 4 LO problems (base and edit rows). On HI problems (61, 70, 76, 96, 98, 99) the "
                          "edit mostly turns cap hits into stops just under the cap (10k-15.6k tokens), still mostly "
                          "wrong; LO problems (0, 7, 15, 24) are short (2k-6k tokens) and mostly right in both arms."),
        "files": [str(BASE.relative_to(ROOT)), str(EDIT.relative_to(ROOT))],
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    # One problem that counts (in HI) and one that does not (k = 1: neither stratum).
    k = base[:, 0] + base[:, 1]
    p_in = base_pids[int(np.flatnonzero(k == 2)[0])]
    p_out = base_pids[int(np.flatnonzero(k == 1)[0])]
    keep = ("problem_index", "sample", "attempt", "n_new", "cap_hit", "finish_reason", "score_v3")
    pick = lambda rows, p: [{f: r[f] for f in keep} for r in sorted(rows, key=lambda r: r["sample"])
                            if r["problem_index"] == p]
    examples = {
        "counts_HI_stratum": {"problem_index": p_in, "k_base_s01": 2,
                              "base_rows": pick(base_rows, p_in), "edit_rows": pick(edit_rows, p_in)},
        "does_not_count_k1": {"problem_index": p_out, "k_base_s01": 1,
                              "base_rows": pick(base_rows, p_out), "edit_rows": pick(edit_rows, p_out)},
    }
    (OUT / "examples.json").write_text(json.dumps(examples, indent=1) + "\n")
    print(json.dumps({k: metrics[k] for k in ("Q", "Q_90ci", "D_logodds_HI_minus_LO", "D_90ci",
                                              "Q_null_base3_vs_base2", "Q_null_90ci", "Q_90ci_plan_seed_20261115",
                                              "n", "verdict")}, indent=1))
    print(json.dumps(metrics["strata"], indent=1))


if __name__ == "__main__":
    main()
