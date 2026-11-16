"""Direct test r16a3c3 (round-16/account-3/c3): Q_C = median over matrices of
[cap_left/cap_right](Code 3.1) / [cap_left/cap_right](Think-SFT), against Math 3.1's top-8 subspaces.
The adversary's value (same ratio against the RL-Zero-General top-8 entry) is computed first.
Spec: studies/theory/specs/SPEC_direct_r16a3c3.md.
Run from the worktree root: uv run --no-project --with numpy python studies/theory/analysis/direct_r16a3c3.py"""
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
INP = ROOT / "studies/theory/data/direct_host/cap_v1.json"
OUT = ROOT / "studies/theory/results/direct/r16a3c3-01"
RANGES = {"account-3": [1.4, 8.0], "null": [0.8, 1.2]}
B = 10000


def q_values(rows, target):
    def share(model, side):
        return np.array([r["cap"][f"{model}>{target}"][side] for r in rows])
    code = share("code31", "cap_left") / share("code31", "cap_right")
    think = share("think_sft", "cap_left") / share("think_sft", "cap_right")
    return code, think, code / think


def boot_median(x, rng):
    idx = rng.integers(0, len(x), size=(B, len(x)))
    meds = np.median(x[idx], axis=1)
    return [float(np.percentile(meds, 5)), float(np.percentile(meds, 95))]


def verdict16(interval, rng_, n, adversary):
    lo, hi = interval
    inside = rng_[0] <= lo and hi <= rng_[1]
    excludes = adversary < lo or adversary > hi
    if inside and n >= 50 and excludes:
        return "holds"
    if inside:
        return "not separated"
    if hi < rng_[0] or lo > rng_[1]:
        return "refuted"
    return "undecided"


def main():
    d = json.loads(INP.read_text())
    rows = d["rows"]
    assert len(rows) == 224, len(rows)
    assert "general30" in d["keys"]

    # 1) Adversary's value first: same ratio of ratios against the RL-Zero-General top-8 entry.
    a_code, a_think, q_alt = q_values(rows, "general30")
    adversary = float(np.median(q_alt))
    print(f"adversary Q_alt (general30) = {adversary:.4f}")

    # 2) The statistic against Math 3.1's top-8 subspaces.
    code, think, q = q_values(rows, "math31")
    value = float(np.median(q))
    ci = boot_median(q, np.random.default_rng(16))
    n = len(q)
    print(f"Q_C (math31) = {value:.4f} [{ci[0]:.4f}, {ci[1]:.4f}] n={n}")

    by_module = {m: float(np.median(q[[r["module"] == m for r in rows]])) for m in "q k v o gate up down".split()}
    names = [r["name"] for r in rows]
    caps = {(r["name"], k): tuple(v.values()) for r in rows for k, v in r["cap"].items()}
    dup_rows = len(names) - len(set(names))
    hi_i, lo_i = int(np.argmax(q)), int(np.argmin(q))

    def example(i, label):
        r = rows[i]
        return {"label": label, "matrix": r["name"], "shape": r["shape"],
                "input": {k: r["cap"][k] for k in ["code31>math31", "think_sft>math31"]},
                "output": {"code_left_over_right": float(code[i]), "think_left_over_right": float(think[i])},
                "score_q": float(q[i]), "counts_above_1.4": bool(q[i] >= 1.4)}

    above = int(np.argmin(np.abs(q - np.percentile(q, 75))))
    below = int(np.argmin(np.abs(q - np.percentile(q, 10))))
    OUT.mkdir(parents=True, exist_ok=False)
    metrics = {
        "test": "round-16/account-3/c3",
        "adversary": {"value": adversary, "expected_by_adversary": 2.5,
                      "how": "median over 224 matrices of (cap_left/cap_right of code31>general30) / (cap_left/cap_right of think_sft>general30); general30 = the RL-Zero-General top-8 entry, present, so no fallback",
                      "code_left_over_right_median": float(np.median(a_code)),
                      "think_left_over_right_median": float(np.median(a_think))},
        "statistic": {"name": "Q_C", "value": value, "interval90": ci, "n": n, "unit": "matrix",
                      "bootstrap": "10000 resamples of matrices, numpy default_rng(16), 5th-95th percentile of the median",
                      "code_left_over_right_median": float(np.median(code)),
                      "think_left_over_right_median": float(np.median(think)),
                      "median_q_by_module": by_module,
                      "share_q_above_1": float(np.mean(q > 1)), "min_q": float(q.min()), "max_q": float(q.max())},
        "ranges": RANGES,
        "verdicts": {k: verdict16(ci, v, n, adversary) for k, v in RANGES.items()},
        "departures": "none: n = 224 as planned; the adversary's first-choice entry general30 exists",
        "raw_check": {"duplicate_matrix_names": dup_rows,
                      "nonpositive_or_nan_shares": int(sum(not (x > 0) for v in caps.values() for x in v[:2]))},
        "input": str(INP.relative_to(ROOT)),
    }
    json.dump(metrics, open(OUT / "metrics.json", "w"), indent=1)
    json.dump([example(above, "q above 1.4 (counts toward the account's direction)"),
               example(below, "q below 1.4 (counts against)"),
               example(hi_i, "max q"), example(lo_i, "min q")], open(OUT / "examples.json", "w"), indent=1)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    json.dump({"commit": commit, "command": "uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 python studies/theory/analysis/direct_r16a3c3.py",
               "job": None, "input_job": d["job"]}, open(OUT / "run.json", "w"), indent=1)
    print(json.dumps(metrics["verdicts"]))


if __name__ == "__main__":
    main()
