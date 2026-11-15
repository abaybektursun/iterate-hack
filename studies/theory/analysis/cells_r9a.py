"""Readout of round-09 cells m11 and m13 (specs/SPEC_cells_r9a.md). Laptop only.

    python3 -m studies.theory.analysis.cells_r9a m11 runs/<job-a> runs/<job-b> ... --jobs '<json: shard -> job id>' \
        --commit <sha> --cmd '<command>' --out studies/theory/results/experiments/cell-r9-m11-01

Reads each <run>/answers.jsonl and <run>/metrics.json (written by studies/rlneurons/jobs/run_cell.py; the shards of one cell),
merges the rows, checks one row per planned problem, and scores every forecast of the cell's readout in
results/wide/round-09/cell_forecasts.json. Writes <out>/run.json, metrics.json, per_problem.json, examples.json. Fail loud.
"""
import argparse
import json
import pathlib
import random

ROUND = pathlib.Path(__file__).resolve().parent.parent / "results" / "wide" / "round-09"
CELLS = {"m11": {"readout": "m11-r1", "key": "cap_hits", "set": "math500", "seed": 41000000,
                 "problems": list(range(500))},
         "m13": {"readout": "m13-r1", "key": "right_v3", "set": "hard328", "seed": 3000000,
                 "problems": list(range(0, 328, 2))}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cell", choices=sorted(CELLS))
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--cmd", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c, out = CELLS[a.cell], pathlib.Path(a.out)
    rows = []
    for run in map(pathlib.Path, a.runs):
        jm = json.loads((run / "metrics.json").read_text())
        assert jm["status"] == "done", (run, jm["status"])
        cfg = jm["config"]
        assert (cfg["prompt"], cfg["set"], cfg["temperature"], cfg["top_p"], cfg["min_p"], cfg["max_tokens"], cfg["seed"],
                cfg["samples"], cfg["restarts"], cfg["n"]) == ("cue", c["set"], 1.0, 1.0, 0.0, 16384, c["seed"], 1, 0, None), cfg
        part = [json.loads(l) for l in open(run / "answers.jsonl") if l.strip()]
        assert len(part) == cfg["n_problems"] == jm["counts"]["n"], run
        rows += part
    rows.sort(key=lambda r: r["problem_index"])
    assert [r["problem_index"] for r in rows] == c["problems"], "not one row per planned problem"
    assert all(r["seed"] == c["seed"] + r["problem_index"] for r in rows)
    n = len(rows)
    right = [r["score_v3"] for r in rows]
    cap = [int(r["cap_hit"]) for r in rows]
    vals = {"right_v3": right, "cap_hits": cap}[c["key"]]
    rng = random.Random(0)
    boot = sorted(sum(rng.choices(vals, k=n)) for _ in range(10000))
    measured, interval = sum(vals), [boot[500], boot[9499]]
    fc = json.loads((ROUND / "cell_forecasts.json").read_text())
    forecasts = {who: {"family": v["family"], "value": f["value"], "interval": [f["low"], f["high"]],
                       "inside": f["low"] <= measured <= f["high"]}
                 for who, v in fc.items() for f in v["forecasts"] if f["readout"] == c["readout"]}
    unboxed = ["\\boxed" not in r["text"] for r in rows]
    finished = [r for r in rows if not r["cap_hit"]]
    metrics = {"cell": a.cell, "readout": c["readout"], "measured": measured, "n": n, "interval_90": interval,
               "right_v3": sum(right), "cap_hits": sum(cap), "mean_generated_tokens": sum(r["n_new"] for r in rows) / n,
               "median_generated_tokens": sorted(r["n_new"] for r in rows)[n // 2], "no_boxed": sum(unboxed),
               "loop_A": sum(r["loop_A"] for r in rows), "finished": len(finished),
               "right_per_finished": sum(r["score_v3"] for r in finished) / len(finished),
               "forecasts": forecasts}
    per = [{"problem_index": r["problem_index"], "unique_id": r["unique_id"], "gold": r["gold"], "extracted_v3": r["extracted_v3"],
            "score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"], "loop_A": r["loop_A"], "no_boxed": u}
           for r, u in zip(rows, unboxed)]
    ex = lambda r: {"problem_index": r["problem_index"], "unique_id": r["unique_id"], "input": r["prompt"], "output": r["text"],
                    "gold": r["gold"], "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"]}
    examples = {"right": ex(next(r for r in rows if r["score_v3"])), "wrong": ex(next(r for r in rows if not r["score_v3"]))}
    out.mkdir(parents=True, exist_ok=False)
    (out / "run.json").write_text(json.dumps({"cell": a.cell, "spec": "studies/theory/specs/SPEC_cells_r9a.md", "jobs": json.loads(a.jobs),
                                              "commit": a.commit, "command": a.cmd, "raw": [str(p) for p in a.runs]}, indent=1))
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    (out / "per_problem.json").write_text(json.dumps(per, indent=1))
    (out / "examples.json").write_text(json.dumps(examples, indent=1))
    print(json.dumps({k: v for k, v in metrics.items() if k != "forecasts"}, indent=1))
    for who, f in forecasts.items():
        print(f"{who:28s} {f['value']:>6} {f['interval']}  {'holds' if f['inside'] else 'REFUTED'}")


if __name__ == "__main__":
    main()
