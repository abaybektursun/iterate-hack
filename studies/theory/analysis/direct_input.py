"""Direct test of run-05/f2-m03 (specs/SPEC_direct_input.md): does a text's drive of Math 3.1's top-8 input subspace set the
top-8 edit's per-problem effect? numpy only, stored rows only.

    uv run --no-project --with numpy python studies/theory/analysis/direct_input.py --runs runs \
        --out studies/theory/results/direct/input-01
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess

import numpy as np

TRACE = "abaybektursun-1115-005830-2145"
BASE = "abaybektursun-1114-151534-e72c"
TOP8 = {"0.5": "abaybektursun-1115-031219-19af", "1": "abaybektursun-1114-221034-007d",
        "1.5": "abaybektursun-1115-031229-5991", "2": "abaybektursun-1115-012855-d7ed"}
RAND = {"1": "abaybektursun-1114-221040-5f1e", "1.5": "abaybektursun-1115-090241-0229"}
MODS = ("up", "gate", "q")
B, SEED = 2000, 0


def drive(run: pathlib.Path):
    """Per answer: mean over positions of the mean over mods and bands of r, for math31 and the 3 random conditions."""
    ix = json.loads((run / "index.json").read_text())
    conds = ix["conds"]
    im, ir = conds.index("math31"), [conds.index(c) for c in ("rand0", "rand1", "rand2")]
    out, up_band0 = {}, []
    for sh in ix["shards"]:
        z = np.load(run / sh["file"])
        r = np.mean([z[f"r_{m}"].astype(np.float64) for m in MODS], 0)             # [positions, band, cond]
        off = z["offsets"]
        for j, p in enumerate(z["problem_index"]):
            seg = r[off[j]:off[j + 1]]
            assert len(seg) > 0 and np.isfinite(seg).all(), p
            out[int(p)] = (seg[:, :, im].mean(), seg[:, :, ir].mean())
            up_band0.append(z["r_up"][off[j]:off[j + 1], 0, im].astype(np.float64).mean())
    return out, float(np.mean(up_band0))


def rows(run: pathlib.Path):
    d = {}
    for line in (run / "answers.jsonl").read_text().splitlines():
        x = json.loads(line)
        d[int(x["problem_index"])] = x
    assert len(d) == 328, (run, len(d))
    return d


def slope_ratio(E, D, cov=None):
    x = D / D.mean()
    X = np.column_stack([np.ones_like(x), x] + ([cov] if cov is not None else []))
    beta = np.linalg.lstsq(X, E, rcond=None)[0][1]
    return beta / E.mean()


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def boot(f, n, rng):
    v = np.array([f(rng.integers(0, n, n)) for _ in range(B)])
    return [round(float(np.percentile(v, 5)), 4), round(float(np.percentile(v, 95)), 4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="runs")
    ap.add_argument("--out", default="studies/theory/results/direct/input-01")
    a = ap.parse_args()
    runs, out = pathlib.Path(a.runs), pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=False)

    dr, up_band0 = drive(runs / TRACE)
    base = rows(runs / BASE)
    top8 = {k: rows(runs / j) for k, j in TOP8.items()}
    rand = {k: rows(runs / j) for k, j in RAND.items()}
    P = np.array(sorted(dr))
    assert len(P) == 328 and set(P) == set(base) and all(set(P) == set(v) for v in [*top8.values(), *rand.values()])

    D = np.array([dr[p][0] for p in P])
    A = D / np.array([dr[p][1] for p in P])
    logL = lambda arm, p: np.log(arm[p]["n_new"])
    fin = lambda arm, p: 0.0 if arm[p]["cap_hit"] else 1.0
    E_len = np.array([np.mean([logL(t, p) for t in top8.values()]) - np.mean([logL(r, p) for r in rand.values()]) for p in P])
    E_fin = np.array([np.mean([fin(t, p) for t in top8.values()]) - np.mean([fin(r, p) for r in rand.values()]) for p in P])
    diff = np.array([np.mean([logL(r, p) for r in rand.values()]) for p in P])
    n = len(P)

    t = np.argsort(D)
    lo, hi = t[: n // 3], t[-(n // 3):]
    g = lambda f: boot(f, n, np.random.default_rng(SEED))
    readouts = {"len": (E_len, None), "fin": (E_fin, None), "len_with_difficulty": (E_len, diff), "fin_with_difficulty": (E_fin, diff)}

    # instrument checks: (1) a planted exact proportional modulation E + mean(E) (D / mean(D) - 1) raises b by exactly 1;
    # (2) with D shuffled over problems (500 draws) the central 90 % of b covers 0; (3) trace-01's level reproduces; (4) rows.
    assert abs(up_band0 - 0.005) < 0.0006, up_band0
    checks = {"trace01_mean_r_math31_band0_up": round(up_band0, 5), "trace01_published": 0.005, "rows_per_arm": 328}
    for k, (E, cov) in readouts.items():
        planted = E + E.mean() * (D / D.mean() - 1)
        step = slope_ratio(planted, D, cov) - slope_ratio(E, D, cov)
        assert abs(step - 1) < 1e-6, (k, step)
        rs = np.random.default_rng(SEED)
        sh = np.array([slope_ratio(E, rs.permutation(D), cov) for _ in range(500)])
        lo5, hi95 = np.percentile(sh, [5, 95])
        assert lo5 <= 0 <= hi95, (k, lo5, hi95)
        checks[k] = {"planted_step": round(float(step), 6), "shuffled_D_b_90": [round(float(lo5), 3), round(float(hi95), 3)]}

    res = {
        "n_problems": n,
        "drive": {"mean_D": round(float(D.mean()), 6), "cv_D": round(float(D.std() / D.mean()), 4),
                  "top_over_bottom_tertile_D": round(float(D[hi].mean() / D[lo].mean()), 4),
                  "top_over_bottom_tertile_D_90": g(lambda i: np.sort(D[i])[-(n // 3):].mean() / np.sort(D[i])[: n // 3].mean()),
                  "cv_A": round(float(A.std() / A.mean()), 4),
                  "top_over_bottom_tertile_A": round(float(np.sort(A)[-(n // 3):].mean() / np.sort(A)[: n // 3].mean()), 4),
                  "rho_D_with_base_log_len": round(spearman(D, np.array([np.log(base[p]["n_new"]) for p in P])), 4),
                  "rho_D_with_rand_log_len": round(spearman(D, diff), 4),
                  "note": "trace-01 stored the first 6,000 answer tokens of each base answer"},
        "effect": {"mean_E_len": round(float(E_len.mean()), 4), "mean_E_len_90": g(lambda i: E_len[i].mean()),
                   "mean_E_fin": round(float(E_fin.mean()), 4), "mean_E_fin_90": g(lambda i: E_fin[i].mean())},
        "b": {k: {"value": round(float(slope_ratio(E, D, cov)), 3), "90": g(lambda i, E=E, cov=cov: slope_ratio(E[i], D[i], None if cov is None else cov[i]))}
              for k, (E, cov) in readouts.items()},
        "b_len_A": round(float(slope_ratio(E_len, A)), 3), "b_len_A_90": g(lambda i: slope_ratio(E_len[i], A[i])),
        "rho_D_E_len": round(spearman(D, E_len), 4), "rho_D_E_len_90": g(lambda i: spearman(D[i], E_len[i])),
        "rho_D_E_fin": round(spearman(D, E_fin), 4), "rho_D_E_fin_90": g(lambda i: spearman(D[i], E_fin[i])),
        "tertiles": {"E_len_top": round(float(E_len[hi].mean()), 4), "E_len_bottom": round(float(E_len[lo].mean()), 4),
                     "E_fin_top": round(float(E_fin[hi].mean()), 4), "E_fin_bottom": round(float(E_fin[lo].mean()), 4),
                     "n_each": n // 3},
        "checks": checks,
    }
    pb = res["b"]["len"]["90"]
    res["preregistered_rule_on_primary"] = "f2-m03 refuted" if pb[1] < 0.5 else "f2-m01 refuted" if pb[0] > 0.5 else "undecided"
    # Amendment 1 (spec): the primary is confounded by answer length, so the verdict uses the length-controlled readouts.
    ctl = [res["b"]["len_with_difficulty"]["90"], res["b"]["fin_with_difficulty"]["90"]]
    res["verdict"] = ("f2-m03 refuted" if all(c[1] < 0.5 for c in ctl) else
                      "f2-m01 refuted" if all(c[0] > 0.5 for c in ctl) else "undecided")
    (out / "readout.json").write_text(json.dumps(res, indent=1))

    def ex(k):
        p = int(P[k])
        return {"problem_index": p, "D": round(float(D[k]), 6), "D_over_mean": round(float(D[k] / D.mean()), 4),
                "E_len": round(float(E_len[k]), 4), "E_fin": round(float(E_fin[k]), 4),
                "base": {"n_new": base[p]["n_new"], "cap_hit": base[p]["cap_hit"], "score_v3": base[p]["score_v3"],
                         "head": base[p]["text"][:300]},
                "top8": {s: {"n_new": v[p]["n_new"], "cap_hit": v[p]["cap_hit"], "score_v3": v[p]["score_v3"]} for s, v in top8.items()},
                "rand": {s: {"n_new": v[p]["n_new"], "cap_hit": v[p]["cap_hit"], "score_v3": v[p]["score_v3"]} for s, v in rand.items()}}
    # one each way: the highest-drive problem with a large shortening, and the lowest-drive problem with a large shortening
    hi_k = max(hi, key=lambda k: -E_len[k])
    lo_k = max(lo, key=lambda k: -E_len[k])
    (out / "examples.json").write_text(json.dumps({"high_drive_shortened": ex(hi_k), "low_drive_shortened": ex(lo_k)}, indent=1))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (out / "run.json").write_text(json.dumps({
        "spec": "studies/theory/specs/SPEC_direct_input.md", "commit": commit,
        "command": "uv run --no-project --with numpy python studies/theory/analysis/direct_input.py --runs runs --out " + str(out),
        "inputs": {"trace": TRACE, "base": BASE, "top8": TOP8, "rand": RAND,
                   "where": "Modal Volume iterate-runs: <job>/answers.jsonl, trace job: index.json, trace_00{0..3}.npz"}}, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
