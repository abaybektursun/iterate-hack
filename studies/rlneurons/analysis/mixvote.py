"""Mixed-model vote from stored rows (laptop, no GPU): plurality vote (day1_vote.vote, grader v3) over samples drawn from
several models' runs of one problem set. Every way of taking the stated number of samples from each model is scored, in both
interleaved orders (the vote's tie rule prefers the earlier sample), and the mean is reported with its range.

  python -m studies.rlneurons.analysis.mixvote --out studies/rlneurons/results/mixvote/hard328-01 \
      rl=runs/<job> think=runs/<job>,runs/<job>,... base=runs/<job>

A model is one run with several samples or several one-sample runs. Only attempt 0 of each sample is read."""
import argparse
import itertools
import json
import pathlib
import subprocess

import numpy as np

from studies.rlneurons.analysis.day1_vote import vote


def load(spec: str) -> list:
    """samples[s][problem] = row, attempt 0 only, problems in index order."""
    samples = []
    for run in spec.split(","):
        rows = [json.loads(line) for line in open(pathlib.Path(run) / "answers.jsonl")]
        rows = [r for r in rows if r["attempt"] == 0]
        for s in sorted({r["sample"] for r in rows}):
            samples.append([r for r in sorted(rows, key=lambda r: r["problem_index"]) if r["sample"] == s])
    return samples


def score(picks: list) -> tuple:
    """picks: list of samples (each a list of rows per problem). Returns per-problem vote scores and tokens per problem."""
    n = len(picks[0])
    assert all([r["problem_index"] for r in p] == [r["problem_index"] for r in picks[0]] for p in picks)
    scores = [vote([p[i] for p in picks])["score"] for i in range(n)]
    return scores, sum(r["n_new"] for p in picks for r in p) / n


def mix(models: dict, counts: dict) -> dict:
    """Every combination of counts[m] samples from each model, in every rotation of the model order, interleaved."""
    names = [m for m in counts if counts[m]]
    per_combo, tokens, per_problem = [], [], []
    for combo in itertools.product(*[itertools.combinations(range(len(models[m])), counts[m]) for m in names]):
        for shift in range(len(names)):
            order = names[shift:] + names[:shift]
            chosen = dict(zip(names, combo))
            picks = [models[m][chosen[m][k]] for k in range(max(counts.values())) for m in order if k < counts[m]]
            s, t = score(picks)
            per_combo.append(sum(s)); tokens.append(t); per_problem.append(s)
    return {"counts": counts, "combinations": len(per_combo), "right_mean": float(np.mean(per_combo)),
            "right_min": min(per_combo), "right_max": max(per_combo), "tokens_per_problem": float(np.mean(tokens)),
            "per_problem_mean": np.mean(per_problem, axis=0).tolist()}


def paired(a: list, b: list) -> dict:
    d = np.array(a) - np.array(b)
    rng = np.random.default_rng(0)
    boot = d[rng.integers(0, len(d), (5000, len(d)))].mean(axis=1) * 100
    return {"points": float(d.mean() * 100), "interval95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("models", nargs="+")
    a = ap.parse_args()
    specs = dict(m.split("=") for m in a.models)
    models = {m: load(s) for m, s in specs.items()}
    n = len(next(iter(models.values()))[0])
    k = min(len(v) for v in models.values())
    rows = {}
    for m in models:
        rows[f"1 {m}"] = mix(models, {m: 1})
        rows[f"2 {m}"] = mix(models, {m: 2})
        rows[f"{k} {m}"] = mix(models, {m: k})
    for x, y in itertools.combinations(models, 2):
        rows[f"1 {x} + 1 {y}"] = mix(models, {x: 1, y: 1})
        rows[f"{k // 2} {x} + {k // 2} {y}"] = mix(models, {x: k // 2, y: k // 2})
        rows[f"{k} {x} + {k} {y}"] = mix(models, {x: k, y: k})
    diffs = {}
    for x, y in itertools.combinations(models, 2):
        mixed = rows[f"{k // 2} {x} + {k // 2} {y}"]["per_problem_mean"]
        for m in (x, y):
            diffs[f"{k // 2} {x} + {k // 2} {y} minus {k} {m}"] = paired(mixed, rows[f"{k} {m}"]["per_problem_mean"])
    out = pathlib.Path(a.out)
    out.mkdir(parents=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    json.dump({"commit": commit, "command": "python -m studies.rlneurons.analysis.mixvote --out " + a.out + " " + " ".join(a.models),
               "runs": specs}, open(out / "run.json", "w"), indent=1)
    json.dump({"n": n, "samples_per_model": {m: len(v) for m, v in models.items()}, "grader": "v3 (stored score_v3)",
               "rule": "day1_vote.vote", "rows": rows, "differences_points": diffs}, open(out / "readout.json", "w"), indent=1)
    for name, r in rows.items():
        print(f"{name:26s} {r['right_mean']:6.1f} of {n}  [{r['right_min']}, {r['right_max']}] over {r['combinations']:3d}  {r['tokens_per_problem']:8.0f} tok")
    for name, d in diffs.items():
        print(f"{name:44s} {d['points']:+.1f} [{d['interval95'][0]:+.1f}, {d['interval95'][1]:+.1f}]")


if __name__ == "__main__":
    main()
