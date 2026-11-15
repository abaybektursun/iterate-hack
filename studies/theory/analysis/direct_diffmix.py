"""Direct test diffmix-01 of round-09/grader-m04 (spec: studies/theory/specs/SPEC_direct_diffmix.md).

Delta = (rho_H - rho_E)_plain - (rho_H - rho_E)_C2, where rho_s = arm-right / T1-right in level stratum s.
Run: uv run python studies/theory/analysis/direct_diffmix.py
"""
import json
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parents[3]
RL = R / "studies/rlneurons"
OUT = R / "studies/theory/results/direct/diffmix-01"
THRESHOLD = -0.05

pp = json.loads((RL / "results/rln4/t1_t3_items-01/per_problem.json").read_text())
meta = json.loads((RL / "data/anatomy/math500_meta.json").read_text())["rows"]
probs = json.loads((RL / "data/rln4/math500.json").read_text())
rows = [json.loads(l) for l in open(RL / "results/day1_3/math500_base_cue-01/rows.jsonl")]
readout = json.loads((RL / "results/day1_3/math500_base_cue-01/readout.json").read_text())


def check_join(meta_rows, prob_rows):
    for m, p in zip(meta_rows, prob_rows, strict=True):
        assert int(m["index"]) == int(p["index"]) and m["unique_id"] == p["unique_id"], (m["index"], p["index"])


# Instrument checks: posted counts must reproduce; a shifted join must fail.
assert len(pp) == 500 and [r["problem_index"] for r in pp] == list(range(500))
assert sum(r["t3_right"] for r in pp) == 224 and sum(r["t1_right"] for r in pp) == 410
check_join(meta, probs)
shifted = [dict(m, unique_id=meta[(i + 1) % 500]["unique_id"]) for i, m in enumerate(meta)]
try:
    check_join(shifted, probs)
    raise SystemExit("instrument check failed: shifted join passed")
except AssertionError:
    pass
c2_rows = {r["problem_index"]: r for r in rows if r["sample"] == 0 and r["attempt"] == 0}
assert sorted(c2_rows) == list(range(500))
assert sum(r["score_v3"] for r in c2_rows.values()) == readout["each_sample"]["single_right"][0] == 405

level = np.array([int(m["level"]) for m in meta])
t3 = np.array([r["t3_right"] for r in pp])
t1 = np.array([r["t1_right"] for r in pp])
c2 = np.array([c2_rows[i]["score_v3"] for i in range(500)])
agree_t1_c2 = int((t1 == c2).sum())
assert agree_t1_c2 < 500  # C2 is a different generation from T1

E = np.where(level <= 2)[0]
H = np.where(level >= 4)[0]


def stats(e, h):
    rho = lambda arm, s: arm[s].sum() / t1[s].sum()
    d_plain = rho(t3, h) - rho(t3, e)
    d_null = rho(c2, h) - rho(c2, e)
    return d_plain - d_null, d_plain, d_null


delta, d_plain, d_null = stats(E, H)
rng = np.random.default_rng(0)
boot = np.empty(10_000)
for b in range(10_000):
    boot[b] = stats(rng.choice(E, E.size), rng.choice(H, H.size))[0]
lo, hi = np.percentile(boot, [5, 95])

n_min = int(min(t1[E].sum(), t1[H].sum()))
if n_min >= 50 and hi < THRESHOLD:
    verdict = "holds"
elif lo >= THRESHOLD:
    verdict = "refuted"
else:
    verdict = "undecided"

metrics = {
    "mechanism": "round-09/grader-m04",
    "statistic": "Delta = (rho_H - rho_E)_plain - (rho_H - rho_E)_C2; rho_s = arm-right / T1-right in stratum s",
    "strata": {"E": "levels 1-2", "H": "levels 4-5"},
    "problems": {"E": int(E.size), "H": int(H.size)},
    "t1_right": {"E": int(t1[E].sum()), "H": int(t1[H].sum())},
    "t3_right": {"E": int(t3[E].sum()), "H": int(t3[H].sum())},
    "c2_right": {"E": int(c2[E].sum()), "H": int(c2[H].sum())},
    "rho_plain": {"E": t3[E].sum() / t1[E].sum(), "H": t3[H].sum() / t1[H].sum()},
    "rho_c2": {"E": c2[E].sum() / t1[E].sum(), "H": c2[H].sum() / t1[H].sum()},
    "D_plain": d_plain,
    "D_null": d_null,
    "Delta": delta,
    "interval90": [lo, hi],
    "bootstrap": "10,000 resamples of problems within each stratum, numpy default_rng(0), 5th/95th percentiles",
    "n": n_min,
    "n_note": "smaller stratum's T1-right count (verdict needs >= 50)",
    "null_value": 0.0,
    "threshold": THRESHOLD,
    "verdict": verdict,
    "checks": {"t3_total": 224, "t1_total": 410, "c2_total": 405, "t1_c2_agree": agree_t1_c2,
               "shifted_join_failed": True},
    "n_to_decide": ("interval half-width 0.119 vs 0.026 from threshold: about 21x the problems (~2,500 T1-right in "
                    "the smaller stratum), more than MATH-500 holds; more plain and cued samples per problem would "
                    "also narrow it"),
    "raw_rows_read": ("Read problems 0,1,5,7,12,13,14,15,17,22 (T1-right): plain losses are often non-attempts, e.g. "
                      "#12 (L5) 15 tokens, nothing extracted; #15 (L5) 155 tokens 'I don't show every step'. Of T1-right "
                      "plain-wrong rows, nothing extracted / under 500 tokens: E 35/55, 43/55; H 47/110, 56/110."),
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

# Examples: a hard problem that counts (T1 right, T3 right) and one where T1 is right but T3 is wrong.
fields = ["problem_index", "t3_right", "t1_right", "t3_cap_hit", "t1_cap_hit", "t3_extracted_v3", "t1_extracted_v3",
          "t3_start", "t1_start"]
counts = next(i for i in H if t1[i] and t3[i])
lost = next(i for i in H if t1[i] and not t3[i])
ex = {}
for name, i in [("counts_plain_right", counts), ("lost_plain_wrong", lost)]:
    ex[name] = {k: pp[i][k] for k in fields} | {"level": int(level[i]), "unique_id": meta[i]["unique_id"],
                                                "gold": probs[i]["answer"], "c2_score_v3": c2_rows[i]["score_v3"],
                                                "c2_extracted_v3": c2_rows[i]["extracted_v3"]}
(OUT / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: metrics[k] for k in ["problems", "t1_right", "t3_right", "c2_right", "rho_plain", "rho_c2",
                                           "D_plain", "D_null", "Delta", "interval90", "n", "verdict"]}, indent=1))
