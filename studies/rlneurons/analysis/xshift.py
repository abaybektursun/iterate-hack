"""xshift readout (specs/SPEC_xshift.md): do the scored weight edits shift the residual stream along one direction, and does an
edit's projection on it predict its stored cap hits.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.xshift --job <job id> [--run run-01]

Run from the repository root after `uv run tools/gpu.py get <job id>`. Reads runs/<job>/{run.json, metrics.json, shifts.npz} and
results/xreward/edits/readout.json (cap hits of each cell on the 328, add_rel). Writes results/xshift/<run>/ (must not exist):
readout.json, run.json, metrics.json (the job's), examples.json.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil

import numpy as np

STUDY = pathlib.Path(__file__).resolve().parents[1]
LSTAR, MATH, CODE = 24, "top8_math31", "top8_code31"


def rank(x):
    x = np.asarray(x, float)
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(len(x))
    for v in np.unique(x):
        r[x == v] = r[x == v].mean()
    return r


def spearman(x, y):
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--run", default="run-01")
    a = ap.parse_args()
    src, out = pathlib.Path("runs") / a.job, STUDY / "results" / "xshift" / a.run
    info, m = (json.loads((src / f).read_text()) for f in ("run.json", "metrics.json"))
    assert info["status"] == "done" and info["job_id"] == a.job and all(c["pass"] for c in m["selftest"].values()), info["status"]
    z = np.load(src / "shifts.npz")
    arms = [str(x) for x in z["arms"]]
    mean = z["mean"][:, 0].astype(np.float64)                                       # [arms, layers, hidden], group "all"
    assert arms == list(m["edits"]) and mean.shape[1:] == (32, 4096), (arms, mean.shape)
    cells = json.loads((STUDY / "results" / "xreward" / "edits" / "readout.json").read_text())["cells"]
    caps = np.array([cells[x]["cap_hits"] for x in arms])
    rel = {x: m["edits"][x]["add_rel"] / cells[x]["edit"]["add_rel"] - 1 for x in arms}
    assert max(abs(v) for v in rel.values()) < 1e-3, f"add_rel differs from the scored cell's: {rel}"

    i = {x: k for k, x in enumerate(arms)}
    unit = lambda v: v / np.linalg.norm(v, axis=-1, keepdims=True)
    um, uc = unit(mean[i[MATH]]), unit(mean[i[CODE]])                                # [layers, hidden]
    on_math, on_code = (mean * um).sum(-1), (mean * uc).sum(-1)                      # [arms, layers]
    norms = np.linalg.norm(mean, axis=-1)
    math_donor = np.array(["--other math31" in m["edits"][x]["args"] or "--other rl_math" in m["edits"][x]["args"] for x in arms])
    rand = np.array(["rand8" in m["edits"][x]["args"] for x in arms])
    proj = np.where(math_donor[:, None], on_code, on_math)                           # P1's projection
    nr = ~rand
    rho = lambda v: spearman(v[nr], caps[nr])
    L = LSTAR
    rp, rn = rho(proj[:, L]), rho(norms[:, L])
    p1 = {"n_edits": int(nr.sum()), "rho_projection": rp, "rho_norm": rn,
          "held": rp <= -0.8 and abs(rn) < abs(rp) - 0.05, "refuted": abs(rp) < 0.5 or abs(rn) >= abs(rp) - 0.05,
          "rho_projection_by_layer": [rho(proj[:, l]) for l in range(32)], "rho_norm_by_layer": [rho(norms[:, l]) for l in range(32)],
          "not_predictions": {"rho_all_on_math_direction (circular for the Math 3.1 cells)": rho(on_math[:, L]), "rho_all_on_code_direction": rho(on_code[:, L]),
                              "rho_add_rel (weight-space size of the edit)": rho(np.array([m["edits"][x]["add_rel"] for x in arms])),
                              "rho_rms_shift": rho(np.array([m["edits"][x]["shift"]["all"]["rms"][L] for x in arms]))}}
    ratios = {x: abs(on_math[i[x], L]) / norms[i[MATH], L] for x in arms if rand[i[x]]}
    p2 = {"abs_projection_over_math_1x": ratios, "held": max(ratios.values()) < 0.1,
          "by_layer_max": [max(abs(on_math[i[x], l]) / norms[i[MATH], l] for x in ratios) for l in range(32)]}
    U = unit(mean[:, L])
    cos = U @ U.T
    c = lambda x: float(cos[i[x], i[MATH]])
    p3 = {"cos_if30_math31": c("top8_if30"), "cos_think_sft_0.02_math31": c("top8x0.02_think_sft"), "cos_general30_math31": c("top8_general30"),
          "held": c("top8_if30") > 0.5 and c("top8x0.02_think_sft") < 0.3 and c("top8_general30") < 0.3,
          "cos_with_math31_by_layer": {x: (unit(mean[i[x]]) * um).sum(-1).tolist() for x in ("top8_if30", "top8x0.02_think_sft", "top8_general30", CODE, "rand8_math31")}}
    rows = {x: {"args": m["edits"][x]["args"], "cap_hits": int(caps[k]), "right_v3": cells[x]["right_v3"], "add_rel": m["edits"][x]["add_rel"],
                "nearest_bf16_effective_scale": m["edits"][x]["nearest_bf16_effective_scale"],
                "mean_shift_norm": norms[k, L], "rms_shift": m["edits"][x]["shift"]["all"]["rms"][L], "frac_mean_dir": m["edits"][x]["shift"]["all"]["frac_mean_dir"][L],
                "projection_p1": proj[k, L], "p1_direction": CODE if math_donor[k] else MATH, "projection_on_math": on_math[k, L], "projection_on_code": on_code[k, L],
                "cos_with_math": c(x), "cos_cap_hit_vs_finished_mean": float(unit(z["mean"][k, 1, L].astype(float)) @ unit(z["mean"][k, 2, L].astype(float))),
                "mean_norm_by_group": {g: m["edits"][x]["shift"][g]["mean_norm"][L] for g in m["groups"]}} for k, x in enumerate(arms)}
    res = {"job_id": a.job, "layer": L, "layer_note": "0-based index of the layer whose output is read; fixed before the run", "inputs": len(m["inputs"]),
           "positions": m["positions"], "base_rms_norm_at_layer": m["base"]["rms"][L], "max_abs_add_rel_difference_from_scored_cells": max(abs(v) for v in rel.values()),
           "P1": p1, "P2": p2, "P3": p3, "edits": rows, "cosine_at_layer": {"arms": arms, "matrix": np.round(cos, 4).tolist()},
           "logit_lens": {x: m["edits"][x]["lens"] for x in arms}}
    out.mkdir(parents=True)
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "run.json").write_text(json.dumps({"experiment": "xshift", "run": a.run, "spec": "studies/rlneurons/specs/SPEC_xshift.md", "job": info,
                                              "raw": f"runs/{a.job}/shifts.npz (uv run tools/gpu.py get {a.job}): the mean shift vectors, not committed"}, indent=1) + "\n")
    shutil.copy(src / "metrics.json", out / "metrics.json")
    ex = {k: next(r for r in m["inputs"] if r["cap_hit"] == v) for k, v in (("cap_hit", True), ("finished", False))}
    (out / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    print(json.dumps({"P1": {k: p1[k] for k in ("n_edits", "rho_projection", "rho_norm", "held", "refuted", "not_predictions")}, "P2": {k: p2[k] for k in ("abs_projection_over_math_1x", "held")},
                      "P3": {k: v for k, v in p3.items() if k != "cos_with_math31_by_layer"}}, indent=1))
    for x, r in rows.items():
        print(f"{x:>24} cap {r['cap_hits']:>3}  |mean| {r['mean_shift_norm']:.4f}  rms {r['rms_shift']:.4f}  frac {r['frac_mean_dir']:.3f}  proj {r['projection_p1']:+.4f}  cos math {r['cos_with_math']:+.3f}")


if __name__ == "__main__":
    main()
