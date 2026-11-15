"""Readouts of round-09 cells m21 and m18 (specs/SPEC_cells_r9b.md). Laptop only.

    python3 -m studies.theory.analysis.cells_r9b m21 --runs runs/<job> --jobs <job> --commit <sha> --cmd '<command>' \
        --out studies/theory/results/experiments/cell-r9-m21-01
    python3 -m studies.theory.analysis.cells_r9b m18 --runs runs/<job0> runs/<job1> --jobs <job0> <job1> ... \
        --out studies/theory/results/experiments/cell-r9-m18-01

Reads <run>/answers.jsonl and <run>/metrics.json (studies/rlneurons/jobs/run_cell.py); several runs are --shard runs, joined with
rlneurons/analysis/shard_join.join. Scores are the job's grader v3. Writes <out>/run.json, metrics.json, per_problem.json,
examples.json. Fail loud: no try/except.
"""
import argparse
import json
import pathlib
import random

from studies.rlneurons.analysis.shard_join import join

# Forecasts copied from results/wide/round-09/cell_forecasts.json: (value, low, high) of the 90 % interval.
CELLS = {
    "m21": {"readout": "m21-r1", "label": "top8x1_code31_plain", "seed": 64000000, "n": 250,
            "forecasts": {"reader-1": (25, 10, 45), "reader-2": (18, 8, 32), "run-06/f2-m03": (25, 10, 45),
                          "run-05/f2-m03": (40, 24, 58), "run-05/f2-m06": (45, 28, 64), "run-07/f2-m02": (27, 14, 40),
                          "round-09/problems-m03": (20, 10, 32), "run-03/f2-m02": (14, 7, 23), "round-09/stopping-m06": (15, 8, 24),
                          "run-04/f2-m03": (18, 7, 32), "round-09/sampling-m03": (20, 8, 35)}},
    "m18": {"readout": "m18-r1", "label": "theta0.125", "seed": 61000000, "n": 500,
            "forecasts": {"reader-1": (355, 315, 392), "reader-2": (362, 320, 400), "run-05/f2-m06": (300, 260, 340),
                          "round-09/weights-m06": (365, 330, 400), "round-09/problems-m03": (395, 365, 420),
                          "run-03/f2-m02": (330, 280, 375), "round-09/stopping-m06": (345, 295, 390),
                          "round-09/sampling-m03": (308, 272, 342)}},
}
QUICK = 1000   # m21-r1: generated tokens at or below this


def load(runs):
    got = [(json.loads((pathlib.Path(r) / "metrics.json").read_text()),
            [json.loads(line) for line in open(pathlib.Path(r) / "answers.jsonl") if line.strip()]) for r in runs]
    if len(got) == 1:
        m, rows = got[0]
        assert m["status"] == "done", m["status"]
        assert not m["config"].get("shard"), "one run given but it is a --shard run"
        return m, rows
    return join(got)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cell", choices=sorted(CELLS))
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--jobs", nargs="+", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--cmd", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    C = CELLS[a.cell]
    jm, rows = load(a.runs)
    cfg = jm["config"]
    assert (cfg["model"], cfg["prompt"], cfg["set"], cfg["temperature"], cfg["top_p"], cfg["min_p"], cfg["max_tokens"], cfg["seed"],
            cfg["samples"], cfg["restarts"]) == (C["label"], "plain", "math500", 1.0, 1.0, 0.0, 16384, C["seed"], 1, 0), cfg
    assert jm["commit"] == a.commit, (jm["commit"], a.commit)
    rows = sorted(rows, key=lambda r: r["problem_index"])
    n = C["n"]
    assert [r["problem_index"] for r in rows] == list(range(n)), "not one row per problem"
    scores = [r["score_v3"] for r in rows]
    quick = [int(r["n_new"] <= QUICK and not r["cap_hit"] and r["score_v3"] != 1) for r in rows]
    measured = sum(quick) if a.cell == "m21" else sum(scores)
    per_item = quick if a.cell == "m21" else scores
    rng = random.Random(0)
    boot = sorted(sum(rng.choices(per_item, k=n)) for _ in range(10000))
    interval = [boot[500], boot[9499]]
    finished = [r for r in rows if not r["cap_hit"]]
    metrics = {"cell": a.cell, "readout": C["readout"], "measured": measured, "n": n, "interval_90": interval,
               "right_v3": sum(scores), "cap_hits": sum(r["cap_hit"] for r in rows),
               "mean_generated_tokens": sum(r["n_new"] for r in rows) / n,
               "median_generated_tokens": sorted(r["n_new"] for r in rows)[n // 2],
               "quick_wrong": sum(quick), "quick_right": sum(int(r["n_new"] <= QUICK and not r["cap_hit"] and r["score_v3"] == 1) for r in rows),
               "no_extracted_answer_finished": sum(r["extracted_v3"] is None for r in finished),
               "opens_okay": sum("Okay" in r["text"][:60] for r in rows),
               "forecasts": {k: {"value": v, "interval": [lo, hi], "inside": lo <= measured <= hi} for k, (v, lo, hi) in C["forecasts"].items()},
               "job_counts": jm["counts"], "config": cfg}
    per = [{"problem_index": r["problem_index"], "unique_id": r["unique_id"], "gold": r["gold"], "extracted_v3": r["extracted_v3"],
            "score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"], "quick_wrong": q} for r, q in zip(rows, quick)]
    ex = lambda r: {"problem_index": r["problem_index"], "unique_id": r["unique_id"], "input": r["prompt"], "output": r["text"],
                    "gold": r["gold"], "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"]}
    examples = {"right": ex(next(r for r in rows if r["score_v3"])), "wrong": ex(next(r for r in rows if not r["score_v3"]))}
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    (out / "run.json").write_text(json.dumps({"job_ids": a.jobs, "commit": a.commit, "command": a.cmd, "raw": a.runs}, indent=1))
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    (out / "per_problem.json").write_text(json.dumps(per, indent=1))
    (out / "examples.json").write_text(json.dumps(examples, indent=1))
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("job_counts", "config")}, indent=1))


if __name__ == "__main__":
    main()
