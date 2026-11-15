"""Direct test of run-06/f2-m03's cause (specs/SPEC_direct_reward.md): does RL-Zero-General, whose LM-judge reward has no
gradable final answer, concentrate its weight change in the top-8 singular directions as the gradable-answer rewards do?

    uv run --no-project --with numpy python studies/theory/analysis/direct_reward.py extract runs/abaybektursun-1114-221259-0871/metrics.json
    uv run --no-project --with numpy python studies/theory/analysis/direct_reward.py analyze

extract: per-matrix top8_share and norm of every key -> studies/theory/data/direct_reward/top8_share_v1.json.
analyze: readout.json, examples.json, run.json in studies/theory/results/direct/reward-01/.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = ROOT / "studies/theory/data/direct_reward/top8_share_v1.json"
OUT = ROOT / "studies/theory/results/direct/reward-01"
SOURCE_JOB = "abaybektursun-1114-221259-0871"
GRADABLE = ["math30", "code30", "if30"]
RUNS = ["math31", "code31", "math30", "code30", "if30", "general30", "mix30"]
B = 10_000


def extract(path):
    d = json.loads(pathlib.Path(path).read_text())
    assert d["n_done"] == d["n"] == 224, (d["n_done"], d["n"])
    rows = [{"name": r["name"], "module": r["module"], "layer": int(r["layer"]), "shape": r["shape"],
             "top8_share": {k: v["top8_share"] for k, v in r["key"].items()},
             "norm": {k: v["norm"] for k, v in r["key"].items()}} for r in d["rows"]]
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps({"source": f"runs/{SOURCE_JOB}/metrics.json", "job": SOURCE_JOB,
                                "code": "studies/rlneurons/jobs/xreward_overlap.py --steps", "keys": d["keys"],
                                "rows": rows}, indent=0))
    print(f"wrote {DATA} ({len(rows)} matrices)")


def ci(x):
    lo, hi = np.percentile(x, [5, 95])
    return [round(float(lo), 4), round(float(hi), 4)]


def gauss_share(shape, rng):
    s = np.linalg.svd(rng.standard_normal(shape).astype(np.float32), compute_uv=False).astype(np.float64)
    return float((s[:8] ** 2).sum() / (s ** 2).sum())


def analyze():
    d = json.loads(DATA.read_text())
    rows, keys = d["rows"], d["keys"]
    assert len(rows) == 224
    share = {k: np.array([r["top8_share"][k] for r in rows]) for k in keys}
    layer = np.array([r["layer"] for r in rows])
    layers = np.unique(layer)
    assert len(layers) == 32
    idx = [np.flatnonzero(layer == L) for L in layers]
    rng = np.random.default_rng(0)
    draws = [np.concatenate([idx[i] for i in rng.integers(0, 32, 32)]) for _ in range(B)]

    def stat(f):
        point = f(np.arange(224))
        boot = np.array([f(m) for m in draws])
        return {"point": round(float(point), 4), "ci90": ci(boot)}

    S = lambda k: (lambda m: share[k][m].mean())
    G = lambda m: np.mean([share[k][m].mean() for k in GRADABLE])
    P = lambda m: (share["general30"][m].mean() - share["think_sft"][m].mean()) / (G(m) - share["think_sft"][m].mean())

    rel_norm = {k: float(np.sqrt(sum(r["norm"][k] ** 2 for r in rows)) / np.sqrt(sum(r["norm"]["base_w"] ** 2 for r in rows)))
                for k in keys}
    per_key = {k: {"S": stat(S(k)), "rel_norm": round(rel_norm[k], 6)} for k in keys}
    p = stat(P)
    verdict = "refuted" if p["ci90"][0] >= 0.5 else ("holds" if p["ci90"][1] < 0.5 else "undecided")

    lm = lambda k: np.array([share[k][i].mean() for i in idx])
    growth = {r: stat(lambda m, r=r: share[r][m].mean() - share[r + "_s100"][m].mean()) for r in RUNS}
    shapes = sorted({tuple(r["shape"]) for r in rows})
    grng = np.random.default_rng(0)
    floor = {f"{a}x{b}": round(gauss_share((a, b), grng), 5) for a, b in shapes}

    diff = share["general30"] - share["math30"]
    hi, lo = int(np.argmax(diff)), int(np.argmin(diff))
    ex = lambda i: {"matrix": rows[i]["name"], "general30": round(float(share["general30"][i]), 4),
                    "math30": round(float(share["math30"][i]), 4), "think_sft": round(float(share["think_sft"][i]), 4),
                    "general30_norm": round(rows[i]["norm"]["general30"], 5), "math30_norm": round(rows[i]["norm"]["math30"], 5)}
    readout = {
        "spec": "studies/theory/specs/SPEC_direct_reward.md",
        "input": str(DATA.relative_to(ROOT)),
        "n_matrices": 224, "n_layers": 32, "bootstrap": f"{B} draws over layers (7 matrices each), paired across keys, seed 0",
        "P": p, "decision_rule": "refuted if P lower bound >= 0.5; holds if P upper bound < 0.5; else undecided",
        "verdict": verdict,
        "G_gradable_3.0": stat(G),
        "general30_minus_math30": stat(lambda m: share["general30"][m].mean() - share["math30"][m].mean()),
        "general30_minus_math31": stat(lambda m: share["general30"][m].mean() - share["math31"][m].mean()),
        "general30_minus_think_sft": stat(lambda m: share["general30"][m].mean() - share["think_sft"][m].mean()),
        "size_matched_general30_minus_code30_s100": stat(lambda m: share["general30"][m].mean() - share["code30_s100"][m].mean()),
        "layers_general30_above_math30": int((lm("general30") > lm("math30")).sum()),
        "layers_general30_above_think_sft": int((lm("general30") > lm("think_sft")).sum()),
        "growth_step100_to_final": growth,
        "per_key": per_key,
        "gaussian_floor_top8_share": floor,
        "supporting_stored_counts": {"source": "studies/rlneurons/results/xreward/edits/readout.json (result-6f1bb7)",
                                     "hard328_cue_right_cap_hits": {"base_cue": [164, 77], "top8_general30_1x": [164, 88],
                                                                    "top8_math31_1x": [192, 46], "top8_math30_1x": [182, 43],
                                                                    "top8_if30_1x": [155, 41], "top8_code30_1x": [173, 23],
                                                                    "top8_think_sft_at_math_norm": [156, 75]}},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "readout.json").write_text(json.dumps(readout, indent=1))
    (OUT / "examples.json").write_text(json.dumps({
        "general30_most_above_math30": ex(hi), "general30_most_below_math30": ex(lo)}, indent=1))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=ROOT).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(sys.argv), "job": None,
                                              "input_job": SOURCE_JOB}, indent=1))
    print(json.dumps({k: readout[k] for k in ["P", "verdict", "G_gradable_3.0", "general30_minus_math30",
                                              "general30_minus_math31", "size_matched_general30_minus_code30_s100",
                                              "layers_general30_above_math30", "gaussian_floor_top8_share"]}, indent=1))
    for k in keys:
        print(k, per_key[k])
    for r in RUNS:
        print("growth", r, growth[r])


if __name__ == "__main__":
    {"extract": lambda: extract(sys.argv[2]), "analyze": analyze}[sys.argv[1]]()
