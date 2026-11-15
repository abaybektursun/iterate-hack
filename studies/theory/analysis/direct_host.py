"""Direct test of round-10/weights-m03 (specs/SPEC_direct_host.md): does Think-SFT's own weight change lie in RL-Math 3.1's
top-8 input subspace more than in a random rank-8 subspace, and more than in the top-8 input subspace of non-math changes?

    uv run --no-project --with numpy python studies/theory/analysis/direct_host.py extract runs/abaybektursun-1114-221259-0871/metrics.json
    uv run --no-project --with numpy python studies/theory/analysis/direct_host.py analyze

extract: per-matrix cap_right, cap_left, cap_both of think_sft and of the positive controls against every subspace
         -> studies/theory/data/direct_host/cap_v1.json.
analyze: readout.json, examples.json, run.json in studies/theory/results/direct/host-01/.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = ROOT / "studies/theory/data/direct_host/cap_v1.json"
OUT = ROOT / "studies/theory/results/direct/host-01"
SOURCE_JOB = "abaybektursun-1114-221259-0871"
SOURCES = ["think_sft", "math30", "code31"]           # whose change is projected
TARGET = "math31"                                     # RL-Math 3.1: the change added to Think-SFT
NULLS = ["if30", "general30", "base_w"]               # deciding structured nulls
REPORTED = ["code31", "math30", "code30", "mix30", "math31_s100", "general30_s100", "if30_s100"]
CAPS = ["cap_right", "cap_left", "cap_both"]
B = 10_000


def extract(path):
    d = json.loads(pathlib.Path(path).read_text())
    assert d["n_done"] == d["n"] == 224 and d["k"] == 8, (d["n_done"], d["n"], d["k"])
    rows = []
    for r in d["rows"]:
        cap = {f"{a}>{b}": {c: float(f"{v:.6g}") for c, v in r["pair"][f"{a}>{b}"].items()}
               for a in SOURCES for b in [TARGET] + NULLS + REPORTED if a != b}
        rows.append({"name": r["name"], "module": r["module"], "layer": int(r["layer"]), "shape": r["shape"], "cap": cap})
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps({"source": f"runs/{SOURCE_JOB}/metrics.json", "job": SOURCE_JOB, "k": 8,
                                "code": "studies/rlneurons/jobs/xreward_overlap.py --steps (commit f89a394)",
                                "definition": "cap_right(a>b) = ||d_a V_b||^2/||d_a||^2, cap_left = ||U_b^T d_a||^2/||d_a||^2, "
                                              "cap_both = ||U_b^T d_a V_b||^2/||d_a||^2; d = model - base, U_b, V_b top-8 "
                                              "left/right singular vectors of b (base_w: the base matrix itself)",
                                "keys": d["keys"], "rows": rows}))
    print(f"wrote {DATA} ({len(rows)} matrices)")


def boot_idx(groups, rng):
    """Resample the units (matrices, or layers whose matrices go together) with replacement; return row indices per draw."""
    units = np.unique(groups)
    members = [np.flatnonzero(groups == u) for u in units]
    for _ in range(B):
        pick = rng.integers(0, len(units), len(units))
        yield np.concatenate([members[p] for p in pick])


def stat(fn, groups):
    rng = np.random.default_rng(0)
    draws = np.array([fn(idx) for idx in boot_idx(groups, rng)])
    lo, hi = np.percentile(draws, [5, 95])
    return {"value": float(fn(np.arange(len(groups)))), "ci90": [float(lo), float(hi)]}


def cap(rows, a, b, kind="cap_right"):
    return np.array([r["cap"][f"{a}>{b}"][kind] for r in rows])


def analyze():
    d = json.loads(DATA.read_text())
    rows = d["rows"]
    n = len(rows)
    assert n == 224
    by_matrix = np.arange(n)
    by_layer = np.array([r["layer"] for r in rows])
    chance = np.array([8 / r["shape"][1] for r in rows])          # input dimension = shape[1]
    ts = cap(rows, "think_sft", TARGET)

    def times_chance(x):
        return lambda i: float(np.mean(x[i] / chance[i]))

    def ratio(x, y):
        return lambda i: float(np.mean(x[i]) / np.mean(y[i]))

    out = {"mechanism": "round-10/weights-m03", "spec": "studies/theory/specs/SPEC_direct_host.md",
           "input": str(DATA.relative_to(ROOT)), "n_matrices": n, "n_layers": int(len(np.unique(by_layer))),
           "bootstrap": f"90 % percentile, {B} resamples, seed 0, over matrices (primary) and over layers (sensitivity)",
           "chance_mean": float(chance.mean()),
           "share_think_sft_in": {}, "T": {}, "S": {}, "S_by_layer": {}, "positive_control": {}, "by_module": {},
           "cap_left_cap_both": {}, "matrices_above": {}}
    for x in [TARGET] + NULLS + REPORTED:
        c = cap(rows, "think_sft", x)
        out["share_think_sft_in"][x] = stat(lambda i, c=c: float(np.mean(c[i])), by_matrix)
        out["share_think_sft_in"][x]["times_chance"] = stat(times_chance(c), by_matrix)
    out["T"] = {"by_matrix": stat(times_chance(ts), by_matrix), "by_layer": stat(times_chance(ts), by_layer),
                "median_matrix": float(np.median(ts / chance))}
    for x in NULLS + REPORTED:
        c = cap(rows, "think_sft", x)
        out["S"][x] = stat(ratio(ts, c), by_matrix)
        out["S_by_layer"][x] = stat(ratio(ts, c), by_layer)
        out["matrices_above"][x] = int((ts > c).sum())
    # positive control: another Math RL run's change, and Code 3.1's, in the same subspaces
    for a in ["math30", "code31"]:
        ca = cap(rows, a, TARGET)
        out["positive_control"][a] = {"share_in_math31": stat(lambda i, ca=ca: float(np.mean(ca[i])), by_matrix),
                                      "times_chance": stat(times_chance(ca), by_matrix),
                                      "S": {x: stat(ratio(ca, cap(rows, a, x)), by_matrix) for x in NULLS}}
    mods = np.array([r["module"] for r in rows])
    for m in ["q", "k", "v", "o", "gate", "up", "down"]:
        sel = np.flatnonzero(mods == m)
        sub = [rows[i] for i in sel]
        t = cap(sub, "think_sft", TARGET)
        g = np.arange(len(sub))
        out["by_module"][m] = {"n": len(sub), "T": stat(lambda i, t=t, ch=chance[sel]: float(np.mean(t[i] / ch[i])), g),
                               "S": {x: stat(ratio(t, cap(sub, "think_sft", x)), g) for x in NULLS}}
    for kind in ["cap_left", "cap_both"]:
        t = cap(rows, "think_sft", TARGET, kind)
        out["cap_left_cap_both"][kind] = {"share_in_math31": float(t.mean()),
                                          "S": {x: stat(ratio(t, cap(rows, "think_sft", x, kind)), by_matrix) for x in NULLS}}

    T = out["T"]["by_matrix"]["ci90"]
    S = {x: out["S"][x]["ci90"] for x in NULLS}
    if T[1] < 2 or any(s[1] < 1 for s in S.values()):
        verdict = "refuted"
    elif T[0] >= 2 and all(s[0] >= 1.5 for s in S.values()):
        verdict = "holds"
    elif T[0] >= 2 and all(s[1] >= 1 for s in S.values()):
        verdict = "holds, not distinctive"
    else:
        verdict = "undecided"
    out["verdict"] = verdict
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "readout.json").write_text(json.dumps(out, indent=1))

    sb = ts / cap(rows, "think_sft", "base_w")
    ex = []
    for label, i in [("largest S against base_w", int(np.argmax(sb))), ("smallest S against base_w", int(np.argmin(sb)))]:
        r = rows[i]
        ex.append({"label": label, "name": r["name"], "shape": r["shape"], "chance": 8 / r["shape"][1],
                   "think_sft_cap_right": {x: r["cap"][f"think_sft>{x}"]["cap_right"] for x in [TARGET] + NULLS + REPORTED},
                   "S_base_w": float(sb[i])})
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({"commit": commit, "command": "studies/theory/analysis/direct_host.py analyze",
                                              "job": None, "input_job": SOURCE_JOB}, indent=1))
    print(json.dumps({"verdict": verdict, "T": out["T"], "S": out["S"], "S_by_layer": out["S_by_layer"],
                      "share": {k: v["value"] for k, v in out["share_think_sft_in"].items()},
                      "positive_control": out["positive_control"], "matrices_above": out["matrices_above"]}, indent=1))


if __name__ == "__main__":
    {"extract": lambda: extract(sys.argv[2]), "analyze": analyze}[sys.argv[1]]()
