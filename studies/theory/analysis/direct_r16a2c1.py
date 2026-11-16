"""Direct test r16a2c1 (round-16/account-2/c1): Q = median over matrices of
[cap_left/cap_right of Think-SFT] / [cap_left/cap_right of Math 3.0], both against Math 3.1's top-8 subspace.
Spec: studies/theory/specs/SPEC_direct_r16a2c1.md.
Run: uv run --no-project --with numpy python studies/theory/analysis/direct_r16a2c1.py"""
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
INP = ROOT / "studies/theory/data/direct_host/cap_v1.json"
OUT = ROOT / "studies/theory/results/direct/r16a2c1-01"
RANGES = {"account-2": [0.05, 0.7], "null": [0.85, 1.25]}
B = 10000
K = 8


def boot_median(x, rng):
    idx = rng.integers(0, len(x), size=(B, len(x)))
    meds = np.median(x[idx], axis=1)
    return [float(np.percentile(meds, 5)), float(np.percentile(meds, 95))]


def adversary(rows):
    # Reads cap_right of Think-SFT and both sides of Math 3.0; never cap_left of Think-SFT.
    d_out = np.array([r["shape"][0] for r in rows], dtype=float)
    cr_ts = np.array([r["cap"]["think_sft>math31"]["cap_right"] for r in rows])
    cl_m30 = np.array([r["cap"]["math30>math31"]["cap_left"] for r in rows])
    cr_m30 = np.array([r["cap"]["math30>math31"]["cap_right"] for r in rows])
    q_alt = ((K / d_out) / cr_ts) / (cl_m30 / cr_m30)
    return float(np.median(q_alt)), q_alt


def q_of(rows, a):
    cl_a = np.array([r["cap"][f"{a}>math31"]["cap_left"] for r in rows])
    cr_a = np.array([r["cap"][f"{a}>math31"]["cap_right"] for r in rows])
    cl_m = np.array([r["cap"]["math30>math31"]["cap_left"] for r in rows])
    cr_m = np.array([r["cap"]["math30>math31"]["cap_right"] for r in rows])
    return (cl_a / cr_a) / (cl_m / cr_m)


def main():
    d = json.loads(INP.read_text())
    rows = d["rows"]
    assert len(rows) == 224, len(rows)
    assert d["k"] == K

    adv, q_alt = adversary(rows)
    print(f"adversary Q_alt = {adv:.4f}")

    q = q_of(rows, "think_sft")
    rng = np.random.default_rng(16)
    value = float(np.median(q))
    ci = boot_median(q, rng)
    q_code = q_of(rows, "code31")
    code_value = float(np.median(q_code))
    print(f"Q = {value:.4f} [{ci[0]:.4f}, {ci[1]:.4f}] n {len(q)}; Code 3.1 in place of Think-SFT: {code_value:.4f}")

    by_module = {}
    for m in ["q", "k", "v", "o", "gate", "up", "down"]:
        sel = np.array([r["module"] == m for r in rows])
        by_module[m] = {"Q": float(np.median(q[sel])), "Q_alt": float(np.median(q_alt[sel])), "n": int(sel.sum())}
    print(json.dumps(by_module))

    # Chance multiples: capture share / (8/d) per side.
    d_out = np.array([r["shape"][0] for r in rows], dtype=float)
    d_in = np.array([r["shape"][1] for r in rows], dtype=float)
    mult = {}
    for a in ["think_sft", "math30", "code31"]:
        cl = np.array([r["cap"][f"{a}>math31"]["cap_left"] for r in rows])
        cr = np.array([r["cap"][f"{a}>math31"]["cap_right"] for r in rows])
        mult[a] = {"median_left_x_chance": float(np.median(cl / (K / d_out))),
                   "median_right_x_chance": float(np.median(cr / (K / d_in)))}
    print(json.dumps(mult))

    # Ten raw rows that enter the statistic.
    for i in range(0, 224, 23)[:10]:
        r = rows[i]
        print(r["name"], r["shape"], r["cap"]["think_sft>math31"], r["cap"]["math30>math31"], f"q={q[i]:.3f}")
    print("non-finite or non-positive caps:", int(np.sum(~np.isfinite(q))),
          int(sum(r["cap"][f"{a}>math31"][s] <= 0 for r in rows for a in ["think_sft", "math30"]
                  for s in ["cap_left", "cap_right"])))
    print("duplicate names:", 224 - len({r["name"] for r in rows}))

    OUT.mkdir(parents=True, exist_ok=False)
    inside = int(np.sum(q <= RANGES["account-2"][1]))
    lo_i, hi_i = int(np.argmin(np.abs(q - 0.3))), int(np.argmin(np.abs(q - 1.0)))

    def ex(i, how):
        r = rows[i]
        return {"counted": how, "name": r["name"], "shape": r["shape"],
                "input": {"think_sft>math31": r["cap"]["think_sft>math31"], "math30>math31": r["cap"]["math30>math31"]},
                "output": {"r_TS": r["cap"]["think_sft>math31"]["cap_left"] / r["cap"]["think_sft>math31"]["cap_right"],
                           "r_M30": r["cap"]["math30>math31"]["cap_left"] / r["cap"]["math30>math31"]["cap_right"]},
                "score": {"q": float(q[i]), "q_alt": float(q_alt[i])}}

    examples = [ex(lo_i, "q at or below 0.7 (inside account-2's range)"),
                ex(hi_i, "q near 1 (inside the null's range)")]
    metrics = {
        "test": "round-16/account-2/c1",
        "statistic": "Q = median over matrices of [cap_left(TS>M31)/cap_right(TS>M31)] / [cap_left(M30>M31)/cap_right(M30>M31)]",
        "adversary": {"value": adv,
                      "how": "per matrix q_alt = ((8/d_out)/cap_right(TS>M31)) / (cap_left(M30>M31)/cap_right(M30>M31)), "
                             "d_out = shape[0]; median over 224 matrices; cap_left of Think-SFT not read. Exactly as the plan."},
        "value": value, "interval90": ci, "n": len(q), "unit": "matrix (bootstrap 10000, default_rng(16))",
        "ranges": RANGES,
        "matrices_with_q_le_0.7": inside,
        "by_module": by_module,
        "chance_multiples": mult,
        "code31_in_place_of_think_sft_Q": code_value,
        "departures": "none",
        "raw_rows_read": "10 rows (every 23rd matrix) printed and read: all 4 capture shares positive and finite in all 224, "
                         "no duplicated matrix names, shapes [d_out, d_in] as expected. Generation checks (cap hits, empty "
                         "answers, extraction) do not apply: inputs are weight-change capture shares from one job. "
                         "Q > 1 because Math 3.0's capture is input-heavy (median right 39.6x chance vs left 7.9x), more than "
                         "Think-SFT's (4.2x vs 2.2x); q is above 1 in v, o, down, gate, up and near 1.5 in q, k. One cap_left "
                         "value of Think-SFT (layer 0 q) was seen while inspecting the file layout before the adversary run.",
        "input": str(INP.relative_to(ROOT)),
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps(examples, indent=1) + "\n")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    run = {"spec": "studies/theory/specs/SPEC_direct_r16a2c1.md", "commit": commit, "board": "work-48eb91",
           "command": "uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 "
                      "python studies/theory/analysis/direct_r16a2c1.py",
           "inputs": [str(INP.relative_to(ROOT))],
           "note": "commit is the spec commit; the script and results are committed together in the next commit"}
    (OUT / "run.json").write_text(json.dumps(run, indent=1) + "\n")


if __name__ == "__main__":
    main()
