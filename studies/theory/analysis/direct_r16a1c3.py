"""Direct test r16a1c3, round-16/account-1/c3 (specs/SPEC_direct_r16a1c3.md): does Code-RL 3.1's per-matrix top-8
share pattern (family median removed) follow Think-SFT's more than IF-RL's, beyond what its likeness to Math-RL 3.1
predicts? Adversary's value computed first.

    uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 python studies/theory/analysis/direct_r16a1c3.py

Writes metrics.json, examples.json, run.json in studies/theory/results/direct/r16a1c3-01/.
"""
import json
import pathlib
import subprocess

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = ROOT / "studies/theory/data/direct_reward/top8_share_v1.json"
OUT = ROOT / "studies/theory/results/direct/r16a1c3-01"
KEYS = ["code31", "math31", "think_sft", "if30"]
FAMS = ["q", "k", "v", "o", "gate", "up", "down"]
ACCOUNT = (0.15, 1.0)
NULL = (-0.1, 0.1)
B = 10_000
CMD = ("uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 "
       "python studies/theory/analysis/direct_r16a1c3.py")


def ranks(x):
    return np.argsort(np.argsort(x)).astype(float)


def spearman(x, y):
    return float(np.corrcoef(ranks(x), ranks(y))[0, 1])


def verdict16(lo, hi, rng_, n, adv):
    if hi < rng_[0] or lo > rng_[1]:
        return "refuted"
    if n < 50 or not (rng_[0] <= lo and hi <= rng_[1]):
        return "undecided"
    return "not separated" if lo <= adv <= hi else "holds"


def main():
    rows = json.loads(DATA.read_text())["rows"]
    n = len(rows)
    assert n == 224
    fam = np.array([r["module"] for r in rows])
    raw = {k: np.array([r["top8_share"][k] for r in rows]) for k in KEYS}
    for k in KEYS:
        assert len(np.unique(raw[k])) == n, f"ties in {k}"
    res = {}
    for k in KEYS:
        out = raw[k].copy()
        for f in FAMS:
            m = fam == f
            assert m.sum() == 32
            out[m] -= np.median(raw[k][m])
        res[k] = out

    # 1) Adversary's value first.
    rho_m_t = spearman(res["math31"], res["think_sft"])
    rho_m_i = spearman(res["math31"], res["if30"])
    d_m = rho_m_t - rho_m_i
    r_cm = spearman(res["code31"], res["math31"])
    adv = r_cm * d_m
    print(f"adversary: D_M={d_m:.4f} (rho M,T {rho_m_t:.4f}, rho M,I {rho_m_i:.4f}), r_CM={r_cm:.4f}, value={adv:.4f}")

    # 2) The statistic.
    def stat(idx):
        c = res["code31"][idx]
        return spearman(c, res["think_sft"][idx]), spearman(c, res["if30"][idx])

    r_ct, r_ci = stat(np.arange(n))
    d3 = r_ct - r_ci
    g = np.random.default_rng(16)
    boot = np.array([stat(g.integers(0, n, n)) for _ in range(B)])
    bd = boot[:, 0] - boot[:, 1]
    lo, hi = (float(v) for v in np.percentile(bd, [5, 95]))
    v = verdict16(lo, hi, ACCOUNT, n, adv)
    print(f"D3={d3:.4f} [{lo:.4f}, {hi:.4f}] n={n} verdict={v}")

    # Partial check: Code residual ranks after removing the part linear in Math 3.1's ranks.
    rc, rm = ranks(res["code31"]), ranks(res["math31"])
    resid = rc - np.polyval(np.polyfit(rm, rc, 1), rm)
    d3_resid = spearman(resid, res["think_sft"]) - spearman(resid, res["if30"])

    metrics = {
        "test": "r16a1c3", "mechanism": "round-16/account-1/c3",
        "statistic": "D3 = Spearman rho(Code-RL 3.1, Think-SFT) - rho(Code-RL 3.1, IF-RL), per-matrix top-8 share minus module-family median (unitless)",
        "adversary": {
            "value": adv,
            "how": "r_CM x D_M on the same 224 family-median residuals: D_M = rho(math31, think_sft) - rho(math31, if30); r_CM = rho(code31, math31)",
            "D_M": d_m, "rho_math_think": rho_m_t, "rho_math_if": rho_m_i, "r_CM": r_cm,
            "reproduces_result_caa23d": "expected 0.594 - (-0.010) = 0.604",
        },
        "D3": d3, "D3_ci90": [lo, hi], "n": n, "unit": "matrix", "bootstrap": B, "seed": 16,
        "rho_code_think": r_ct, "rho_code_think_ci90": [float(x) for x in np.percentile(boot[:, 0], [5, 95])],
        "rho_code_if": r_ci, "rho_code_if_ci90": [float(x) for x in np.percentile(boot[:, 1], [5, 95])],
        "account_range": list(ACCOUNT), "null_range": list(NULL), "verdict": v,
        "extra_D3_of_code_after_removing_math31_linear_rank_part": d3_resid,
        "per_family_D3": {f: spearman(res["code31"][fam == f], res["think_sft"][fam == f])
                          - spearman(res["code31"][fam == f], res["if30"][fam == f]) for f in FAMS},
        "departures": ["IF-RL key is if30 (the only IF run in the file, IF-RL 3.0), as in result-caa23d",
                       "Spearman via numpy double-argsort ranks (no ties in any of the 4 keys, asserted)"],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1))

    # Examples: the matrix pushing D3 up most (Code agrees with Think-SFT, not IF) and the one pushing it down most.
    zc, zt, zi = (ranks(res[k]) - (n - 1) / 2 for k in ["code31", "think_sft", "if30"])
    contrib = zc * zt - zc * zi
    ex = []
    for label, i in [("matrix adding most to D3 (Code's rank sides with Think-SFT over IF)", int(np.argmax(contrib))),
                     ("matrix subtracting most from D3 (Code's rank sides with IF over Think-SFT)", int(np.argmin(contrib)))]:
        r = rows[i]
        ex.append({"label": label, "name": r["name"], "module": r["module"], "layer": r["layer"],
                   "input_top8_share": {k: r["top8_share"][k] for k in KEYS},
                   "output_residual": {k: float(res[k][i]) for k in KEYS},
                   "score_rank_product_contribution": float(contrib[i])})
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT,
                            check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({"commit": commit, "command": CMD, "job": None,
                                              "input": str(DATA.relative_to(ROOT)),
                                              "source_job": "abaybektursun-1114-221259-0871"}, indent=1))


if __name__ == "__main__":
    main()
