"""drive-01 readout (specs/SPEC_direct_drive.md): drive of Math 3.1's top-8 input subspace on code text over math text, with the
random rank-8 control and Code 3.1's reverse ratio. numpy only.

    uv run --no-project --with numpy python studies/theory/analysis/direct_drive.py --job <ih job id> \
        --out studies/theory/results/direct/drive-01

Inputs: runs/<job>/rows.jsonl (studies/theory/jobs/drive_trace.py: 538 code answers + 16 re-traced math answers) and
runs/abaybektursun-1115-005830-2145/ (trace-01, the 328 math answers; Modal Volume iterate-runs).
"""
from __future__ import annotations

import argparse
import gzip
import json
import pathlib
import subprocess

import numpy as np

TRACE = "abaybektursun-1115-005830-2145"
CODE_FILE = pathlib.Path("studies/theory/data/drive/code_cue_answers_v1.jsonl.gz")
MODS = ("up", "gate", "q")
RAND = ("rand0", "rand1", "rand2")
B, SEED = 2000, 0


def trace01(run: pathlib.Path):
    """Per math answer: D[mod, band, cond] (mean over positions), from trace-01's stored float16 band means."""
    ix = json.loads((run / "index.json").read_text())
    out = {}
    for sh in ix["shards"]:
        z = np.load(run / sh["file"])
        r = np.stack([z[f"r_{m}"].astype(np.float64) for m in MODS], 1)                 # [positions, mod, band, cond]
        off = z["offsets"]
        for j, p in enumerate(z["problem_index"]):
            seg = r[off[j]:off[j + 1]]
            assert len(seg) > 0 and np.isfinite(seg).all(), p
            out[int(p)] = seg.mean(0)
    return out, list(ix["conds"])


def interval(f, n_a, n_b):
    rng = np.random.default_rng(SEED)
    v = np.array([f(rng.integers(0, n_a, n_a), rng.integers(0, n_b, n_b)) for _ in range(B)])
    return [round(float(x), 4) for x in np.percentile(v, [5, 95])]


def band(x):
    return "supports f2-m03" if 0.40 <= x <= 0.70 else "refutes f2-m03" if x > 0.85 else "undecided"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--runs", default="runs")
    ap.add_argument("--out", default="studies/theory/results/direct/drive-01")
    a = ap.parse_args()
    runs, out = pathlib.Path(a.runs), pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=False)

    math, conds = trace01(runs / TRACE)
    assert len(math) == 328
    job_rows = [json.loads(l) for l in (runs / a.job / "rows.jsonl").read_text().splitlines()]
    code = [x for x in job_rows if x["domain"] == "code"]
    check = [x for x in job_rows if x["domain"] == "math"]
    assert len(code) == 538 and len(check) == 16, (len(code), len(check))
    jm = json.loads((runs / a.job / "metrics.json").read_text())
    assert list(jm["conds"]) == conds and jm["left_out"] == [] and jm["selftest"]["passed"]
    c = {k: conds.index(k) for k in conds}
    Dc = np.array([x["D"][m] for x in code for m in MODS]).reshape(len(code), len(MODS), 4, len(conds))   # [answer, mod, band, cond]
    Dm = np.array([math[p] for p in sorted(math)])

    # check 2: the 16 re-traced math answers reproduce trace-01's per-answer D within 1 % (every condition, mean over mods and bands)
    rel = np.array([[np.array(x["D"][m]) for m in MODS] for x in check]).mean((1, 2)) / np.array([math[x["id"]] for x in check]).mean((1, 2)) - 1
    assert np.abs(rel).max() < 0.01, rel
    checks = {"selftest": jm["selftest"], "math_retrace_max_abs_rel_diff": round(float(np.abs(rel).max()), 5),
              "math_retrace_n": len(check), "code_left_out": jm["left_out"], "code_answers": len(code),
              "code_by_bench": {b: sum(x["bench"] == b for x in code) for b in ("humanevalplus", "mbppplus")}}

    def per_answer(D, ks, sel=(slice(None), slice(None))):
        return D[:, sel[0], sel[1], :][..., [c[k] for k in ks]].mean(axis=tuple(range(1, D.ndim)))

    def ratio(ks, num, den, sel=(slice(None), slice(None))):
        x, y = per_answer(num, ks, sel), per_answer(den, ks, sel)
        return float(x.mean() / y.mean()), interval(lambda i, j: x[i].mean() / y[j].mean(), len(x), len(y))

    def norm_ratio(ks, num, den):
        x, y = per_answer(num, ks), per_answer(den, ks)
        xr, yr = per_answer(num, RAND), per_answer(den, RAND)
        f = lambda i, j: (x[i].mean() / y[j].mean()) / (xr[i].mean() / yr[j].mean())
        return float(f(np.arange(len(x)), np.arange(len(y)))), interval(f, len(x), len(y))

    R_math, R_math_90 = ratio(("math31",), Dc, Dm)
    R_rand, R_rand_90 = ratio(RAND, Dc, Dm)
    N_math, N_math_90 = norm_ratio(("math31",), Dc, Dm)
    R_code, R_code_90 = ratio(("code31",), Dm, Dc)
    N_code, N_code_90 = norm_ratio(("code31",), Dm, Dc)
    def split(sel):
        return {"math31": round(ratio(("math31",), Dc, Dm, sel)[0], 4), "rand": round(ratio(RAND, Dc, Dm, sel)[0], 4),
                "code31_math_over_code": round(ratio(("code31",), Dm, Dc, sel)[0], 4)}
    by_band = {f"{lo}-{lo + 8}": split((slice(None), slice(b, b + 1))) for b, lo in enumerate((0, 8, 16, 24))}
    by_mod = {m: split((slice(i, i + 1), slice(None))) for i, m in enumerate(MODS)}
    mean = lambda D, ks: round(float(per_answer(D, ks).mean()), 6)
    v_raw, v_norm = band(R_math), band(N_math)
    res = {
        "n_code_texts": len(code), "n_math_texts": len(math),
        "mean_D": {"code_text": {k: mean(Dc, (k,)) for k in conds} | {"rand_mean": mean(Dc, RAND)},
                   "math_text": {k: mean(Dm, (k,)) for k in conds} | {"rand_mean": mean(Dm, RAND)}},
        "R_math": {"value": round(R_math, 4), "90": R_math_90, "what": "mean D_math31(code text) / mean D_math31(math text)"},
        "R_rand": {"value": round(R_rand, 4), "90": R_rand_90, "what": "same for the mean of 3 random rank-8 V (math31's s)"},
        "R_math_over_R_rand": {"value": round(N_math, 4), "90": N_math_90},
        "R_code": {"value": round(R_code, 4), "90": R_code_90, "what": "mean D_code31(math text) / mean D_code31(code text)"},
        "R_code_over_inverse_R_rand": {"value": round(N_code, 4), "90": N_code_90},
        "predicted_by_f2_m03": {"R_math": round((368 - 331) / (399 - 331), 4), "R_code": [0.45, 0.47]},
        "by_band": by_band, "by_mod": by_mod,
        "code_cap_hits": int(sum(x["cap_hit"] for x in code)), "code_passed": int(sum(x["passed"] for x in code)),
        "code_positions": int(sum(x["n"] for x in code)),
        "rule": "R_math in [0.40, 0.70] supports f2-m03; above 0.85 refutes; else undecided; undecided if R_math / R_rand is in another band",
        "verdict_R_math": v_raw, "verdict_R_math_over_R_rand": v_norm,
        "verdict": v_raw if v_raw == v_norm else "undecided",
        "checks": checks,
    }
    (out / "metrics.json").write_text(json.dumps(res, indent=1))

    texts = {json.loads(l)["uid"]: json.loads(l) for l in gzip.decompress(CODE_FILE.read_bytes()).decode().splitlines()}
    dm, dr = per_answer(Dc, ("math31",)), per_answer(Dc, RAND)
    per = [{"uid": x["id"], "bench": x["bench"], "n": x["n"], "cap_hit": x["cap_hit"], "passed": x["passed"],
            **{f"D_{k}": round(float(per_answer(Dc[i:i + 1], (k,))[0]), 6) for k in conds}} for i, x in enumerate(code)]
    (out / "rows.json").write_text(json.dumps(per))

    def ex(i):
        t = texts[code[i]["id"]]
        return {"uid": t["uid"], "D_math31": round(float(dm[i]), 6), "D_math31_over_math_text_mean": round(float(dm[i] / per_answer(Dm, ("math31",)).mean()), 4),
                "D_rand": round(float(dr[i]), 6), "n": code[i]["n"], "cap_hit": t["cap_hit"], "passed": t["passed"],
                "head": t["text"][:400], "tail": t["text"][-300:]}
    (out / "examples.json").write_text(json.dumps({"highest_drive": ex(int(np.argmax(dm))), "lowest_drive": ex(int(np.argmin(dm)))}, indent=1))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    job_run = json.loads((runs / a.job / "run.json").read_text())
    (out / "run.json").write_text(json.dumps({
        "spec": "studies/theory/specs/SPEC_direct_drive.md", "analysis_commit": commit,
        "analysis_command": f"uv run --no-project --with numpy python studies/theory/analysis/direct_drive.py --job {a.job} --out {out}",
        "job": {"id": a.job, "commit": job_run["commit"], "command": job_run["command"], "wall_s": job_run.get("wall_s"),
                "where": f"runs/{a.job}/ (ih get), rows.jsonl metrics.json run.json log"},
        "inputs": {"trace01": f"{TRACE} (Modal Volume iterate-runs: index.json, trace_00{{0..3}}.npz)", **job_run["inputs"]}}, indent=1))
    print(json.dumps({k: res[k] for k in ("R_math", "R_rand", "R_math_over_R_rand", "R_code", "R_code_over_inverse_R_rand", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
