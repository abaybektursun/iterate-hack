"""Direct test step100cap-01 of round-09/stopping-m04 (theory round 14).

Paired per-problem cap-hit rate, RL step 100 plain minus cued base, MATH-500, T 1.0, 4 samples per problem.
Spec: studies/theory/specs/SPEC_direct_step100cap.md.
Run: uv run python studies/theory/analysis/direct_step100cap.py
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "studies/rlneurons/results"
OUT = ROOT / "studies/theory/results/direct/step100cap-01"
CAP = 16384
THRESHOLD = -1.0
N_PROB = 500


def load_rows(folder):
    """Rows of one folder as dicts with problem, sample, attempt, cap, right, tokens."""
    d = RES / folder
    if (d / "rows.jsonl").exists():
        raw = [json.loads(line) for line in open(d / "rows.jsonl")]
        rows = [dict(problem=r["problem_index"], sample=r["sample"], attempt=r["attempt"],
                     cap=bool(r["cap_hit"] or r["finish_reason"] == "length" or r["n_new"] >= CAP),
                     right=r["score_v3"], tokens=r["n_new"], raw=r) for r in raw]
    else:  # per_problem.json: sample 0, no restarts
        raw = json.load(open(d / "per_problem.json"))
        rows = [dict(problem=r["problem_index"], sample=0, attempt=0,
                     cap=bool(r["cap_hit"] or r["n_generated"] >= CAP),
                     right=r["score_v3"], tokens=r["n_generated"], raw=r) for r in raw]
    m = json.load(open(d / "metrics.json"))
    cfg = m["config"]
    assert cfg["set"] == "math500" and cfg["temperature"] == 1.0 and cfg["top_p"] == 1.0 and cfg["max_tokens"] == CAP, folder
    posted = m["counts"]["cap_hits"]
    got = sum(r["cap"] for r in rows)
    assert got == posted, f"{folder}: {got} cap hits in rows, metrics.json says {posted}"
    print(f"check {folder}: {got} cap hits = metrics.json {posted}")
    return rows


def arm(folders):
    rows = [r for f in folders for r in load_rows(f) if r["attempt"] == 0]
    cap = np.full((N_PROB, 4), np.nan)
    right = np.full((N_PROB, 4), np.nan)
    for r in rows:
        assert np.isnan(cap[r["problem"], r["sample"]]), ("duplicate", r["problem"], r["sample"])
        cap[r["problem"], r["sample"]] = r["cap"]
        right[r["problem"], r["sample"]] = r["right"]
    assert not np.isnan(cap).any(), f"{folders}: missing (problem, sample) cells"
    return cap, right, rows


def diff(hx, hy, idx):
    """100 * mean over problems of hx - hy, its 90 % percentile interval over the resample indices."""
    d = hx - hy
    boot = 100 * d[idx].mean(axis=1)
    return dict(value=round(100 * d.mean(), 3),
                ci90=[round(float(np.percentile(boot, 5)), 3), round(float(np.percentile(boot, 95)), 3)])


def main():
    capA, rightA, rowsA = arm(["ckptcue/s0100_plain-01", "ckptcue/s0100_plain_s123-01"])
    capB, rightB, rowsB = arm(["day1_3/math500_base_cue-01"])
    capC, _, _ = arm(["day1_3/math500_rl-01"])
    capE, _, _ = arm(["ckptcue/s0400_plain-01", "ckptcue/s0400_plain_s123-01"])

    idx = np.random.default_rng(0).integers(0, N_PROB, size=(10_000, N_PROB))
    hA, hB, hC, hE = (c.mean(axis=1) for c in (capA, capB, capC, capE))

    # Planted checks: B against itself gives 0; an all-capped arm against B gives 100 - 100 * mean h_B.
    assert diff(hB, hB, idx)["value"] == 0 and diff(hB, hB, idx)["ci90"] == [0, 0]
    assert abs(diff(np.ones(N_PROB), hB, idx)["value"] - (100 - 100 * hB.mean())) < 1e-6
    print("planted checks pass")

    D = diff(hA, hB, idx)
    DC = diff(hC, hB, idx)
    DE = diff(hE, hB, idx)
    Dnull = diff(capB[:, :2].mean(axis=1), capB[:, 2:].mean(axis=1), idx)
    D2 = diff(capA[:, :2].mean(axis=1), capB[:, 2:].mean(axis=1), idx)

    if not DC["ci90"][1] < THRESHOLD:
        verdict = "undecided"
        why = "final RL's 90 % interval is not wholly below -1.0: the instrument does not detect stopping"
    elif D["ci90"][0] > THRESHOLD:
        verdict = "holds"
        why = "D's 90 % interval lies wholly above -1.0 and final RL's wholly below -1.0, n = 500"
    elif D["ci90"][1] <= THRESHOLD:
        verdict = "refuted"
        why = "D's 90 % interval lies wholly at or below -1.0"
    else:
        verdict = "undecided"
        why = "D's 90 % interval straddles -1.0"

    fin = lambda cap, right: (float(right[cap == 0].mean()), int((cap == 0).sum()))
    rA, nA = fin(capA, rightA)
    rB, nB = fin(capB, rightB)
    metrics = dict(
        mechanism="round-09/stopping-m04",
        statistic="D = 100 * mean_i [h_A(i) - h_B(i)]: per-problem cap-hit share, RL step 100 plain (A) minus cued base (B), points",
        n=N_PROB, unit="problem (4 attempt-0 samples per arm)", bootstrap="10,000 resamples of problems, numpy default_rng(0), percentile 90 %",
        D=D, D_C_final_rl_minus_base=DC, D_E_step400_minus_base=DE,
        null_value=0.0, D_null_base01_minus_base23=Dnull, D_2_A01_minus_B23=D2,
        threshold=THRESHOLD, verdict=verdict, verdict_reason=why,
        cap_hit_totals=dict(A_step100=int(capA.sum()), B_cued_base=int(capB.sum()), C_final_rl=int(capC.sum()),
                            E_step400=int(capE.sum()), of=2000),
        right_share_finished=dict(A_step100=dict(share=round(rA, 4), n_finished=nA), B_cued_base=dict(share=round(rB, 4), n_finished=nB)),
        problems_with_any_cap=dict(A=int((hA > 0).sum()), B=int((hB > 0).sum()), both=int(((hA > 0) & (hB > 0)).sum())),
        changes_from_plan=["day1_3 runs: attempt 0 only (restart rows are redraws after a cap hit; step-100/400 runs have none)",
                           "per_problem.json has no finish_reason: cap = cap_hit or n_generated >= 16384 (rows.jsonl: cap_hit or finish_reason length or n_new >= 16384; all agree)"],
        raw_rows_read="",
    )
    OUT.mkdir(parents=True, exist_ok=True)
    old = json.loads((OUT / "metrics.json").read_text()) if (OUT / "metrics.json").exists() else {}
    metrics["raw_rows_read"] = old.get("raw_rows_read", "")
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    # Example rows: one A row that hits the cap (counts toward h_A) and one A row on the same problem that finished.
    both = [i for i in range(N_PROB) if 0 < hA[i] < 1]
    i = both[0]
    a_cap = next(r["raw"] for r in rowsA if r["problem"] == i and r["cap"])
    a_fin = next(r["raw"] for r in rowsA if r["problem"] == i and not r["cap"])
    b_rows = [r["raw"] for r in rowsB if r["problem"] == i]
    ex = dict(problem_index=i, h_A=hA[i], h_B=hB[i],
              counts_as_cap_hit=dict(arm="A step 100", row=a_cap),
              does_not_count=dict(arm="A step 100", row=a_fin),
              cued_base_rows_same_problem=b_rows)
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    print(json.dumps({k: metrics[k] for k in ("D", "D_C_final_rl_minus_base", "D_E_step400_minus_base",
                                              "D_null_base01_minus_base23", "D_2_A01_minus_B23", "cap_hit_totals",
                                              "right_share_finished", "problems_with_any_cap", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
