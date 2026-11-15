"""Direct test sharerho, round-15/account-1/c2 (specs/SPEC_direct_sharerho.md): is the per-matrix top-8 share pattern of
Math-RL 3.1 closer to IF-RL's than to Think-SFT's, after each module family's median is subtracted?

    uv run --no-project --with numpy --with scipy python studies/theory/analysis/direct_sharerho.py

Writes metrics.json, examples.json, run.json in studies/theory/results/direct/sharerho-01/.
"""
import json
import pathlib
import subprocess

import numpy as np
from scipy.stats import rankdata

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = ROOT / "studies/theory/data/direct_reward/top8_share_v1.json"
OUT = ROOT / "studies/theory/results/direct/sharerho-01"
KEYS = ["math31", "if30", "think_sft"]
ACCOUNT = (0.15, 1.0)
NULL = (-0.1, 0.1)
B = 10_000


def spearman(x, y):
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])


def ci(x):
    lo, hi = np.percentile(x, [5, 95])
    return [float(lo), float(hi)]


def main():
    rows = json.loads(DATA.read_text())["rows"]
    assert len(rows) == 224
    fam = np.array([r["module"] for r in rows])
    raw = {k: np.array([r["top8_share"][k] for r in rows]) for k in KEYS}
    res = {}
    for k in KEYS:
        med = {f: np.median(raw[k][fam == f]) for f in set(fam)}
        assert all((fam == f).sum() == 32 for f in med)
        res[k] = raw[k] - np.array([med[f] for f in fam])

    def stats(v, idx):
        a, b, c = (v[k][idx] for k in KEYS)
        return spearman(a, b), spearman(a, c), spearman(b, c)

    n = len(rows)
    full = np.arange(n)
    r_if, r_sft, r_if_sft = stats(res, full)
    d = r_if - r_sft
    rng = np.random.default_rng(0)
    boot = np.array([stats(res, rng.integers(0, n, n)) for _ in range(B)])
    bd = boot[:, 0] - boot[:, 1]
    lo, hi = ci(bd)
    if lo >= ACCOUNT[0] and hi <= ACCOUNT[1] and n >= 50:
        verdict = "holds"
    elif hi < ACCOUNT[0] or lo > ACCOUNT[1]:
        verdict = "refuted"
    else:
        verdict = "undecided"
    raw_if, raw_sft, raw_if_sft = stats(raw, full)
    metrics = {
        "test": "sharerho", "mechanism": "round-15/account-1/c2",
        "statistic": "Spearman rho(Math 3.1, IF) - Spearman rho(Math 3.1, Think-SFT), per-matrix top-8 share minus family median",
        "D": d, "D_ci90": [lo, hi], "n": n, "bootstrap": B, "seed": 0,
        "null_value": 0.0, "null_range": list(NULL), "account_range": list(ACCOUNT), "verdict": verdict,
        "rho_math_if": r_if, "rho_math_if_ci90": ci(boot[:, 0]),
        "rho_math_sft": r_sft, "rho_math_sft_ci90": ci(boot[:, 1]),
        "rho_if_sft": r_if_sft, "rho_if_sft_ci90": ci(boot[:, 2]),
        "raw_no_centring": {"rho_math_if": raw_if, "rho_math_sft": raw_sft, "rho_if_sft": raw_if_sft,
                            "D": raw_if - raw_sft},
        "per_family_D": {f: spearman(res["math31"][fam == f], res["if30"][fam == f])
                         - spearman(res["math31"][fam == f], res["think_sft"][fam == f])
                         for f in ["q", "k", "v", "o", "gate", "up", "down"]},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1))
    gap = (res["math31"] - res["if30"]) ** 2
    ex = []
    for label, i in [("matrix where Math 3.1 and IF residuals agree most", int(np.argmin(gap))),
                     ("matrix where Math 3.1 and IF residuals disagree most", int(np.argmax(gap)))]:
        r = rows[i]
        ex.append({"label": label, "name": r["name"], "module": r["module"], "layer": r["layer"],
                   "top8_share": {k: r["top8_share"][k] for k in KEYS},
                   "residual": {k: float(res[k][i]) for k in KEYS}})
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({"commit": commit, "command": "uv run --no-project --with numpy --with scipy python studies/theory/analysis/direct_sharerho.py",
                                              "job": None, "input": str(DATA.relative_to(ROOT)),
                                              "source_job": "abaybektursun-1114-221259-0871"}, indent=1))
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
