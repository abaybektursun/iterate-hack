"""ckptcue3 readout (specs/SPEC_ckptcue3.md): four samples per cell of RL steps 100 and 400 at T 1.0 against the four stored
samples of the cued base and of the final RL model. Laptop, no model.

    python -m studies.rlneurons.analysis.ckptcue3 --runs runs s0100_plain=<job> s0100_cue=<job> s0400_plain=<job>

For each <cell>=<job-id> (a run_cell job with --samples 3, the samples 1 to 3 of the cell) it reads runs/<job-id>/answers.jsonl
and metrics.json and writes results/ckptcue/<cell>_s123-01/ (run.json, metrics.json, rows.jsonl with sample = 1 to 3, examples.json;
refuses an existing folder). Sample 0 of each cell is results/ckptcue/<cell>-01/per_problem.json. The references are attempt 0 of
results/day1_3/math500_base_cue-01/rows.jsonl and results/day1_3/math500_rl-01/rows.jsonl. Writes results/ckptcue/readout3.json.
"""
import argparse
import json
import pathlib

import numpy as np

from studies.rlneurons.lib.n13_score import paired_bootstrap

HERE = pathlib.Path(__file__).resolve().parents[1]
OUT = HERE / "results" / "ckptcue"
EX = ("problem_index", "sample", "seed", "prompt", "text", "gold", "extracted_v3", "mode_v3", "score_v3", "n_generated", "cap_hit")
PAIRS = [("s0100_plain", "base_cue"), ("s0100_cue", "s0100_plain"), ("s0100_cue", "base_cue"), ("s0400_plain", "s0100_plain"),
         ("rl_final", "s0400_plain")]


def sample(rows, tok, okay=None):
    """One sample's per-problem scores and its counts, from 500 rows sorted by problem."""
    assert [r["problem_index"] for r in rows] == list(range(500))
    return np.array([r["score_v3"] for r in rows]), {
        "right": sum(r["score_v3"] for r in rows), "cap_hits": sum(r["cap_hit"] for r in rows),
        "okay_in_first_30": None if okay is None else sum("Okay" in r[okay][:30] for r in rows),
        "tokens_per_problem": sum(r[tok] for r in rows) / 500}


def by_sample(rows):
    rows = sorted(rows, key=lambda r: (r["sample"], r["problem_index"]))
    return [rows[i:i + 500] for i in range(0, len(rows), 500)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("cells", nargs="+")
    a = ap.parse_args()
    x, cells = {}, {}

    def add(cell, source, parts):
        x[cell] = np.mean([p[0] for p in parts], axis=0)                      # per problem: mean over the samples
        cells[cell] = {"source": source, "samples": [p[1] for p in parts], "mean_right": float(500 * x[cell].mean()),
                       "mean_cap_hits": float(np.mean([p[1]["cap_hits"] for p in parts])),
                       "mean_tokens_per_problem": float(np.mean([p[1]["tokens_per_problem"] for p in parts]))}

    for cell, d in (("base_cue", "math500_base_cue-01"), ("rl_final", "math500_rl-01")):
        f = HERE / "results" / "day1_3" / d / "rows.jsonl"
        rows = [r for r in map(json.loads, open(f)) if r["attempt"] == 0]
        add(cell, f"results/day1_3/{d}/rows.jsonl (attempt 0)", [sample(s, "n_new") for s in by_sample(rows)])
    for spec in a.cells:
        cell, job = spec.split("=")
        src = pathlib.Path(a.runs) / job
        m = json.load(open(src / "metrics.json"))
        assert m["status"] == "done", (cell, m["status"])
        cfg = m["config"]
        s0 = json.load(open(OUT / f"{cell}-01" / "run.json"))
        assert (cfg["model_label"], cfg["prompt"], cfg["seed"], cfg["samples"]) == (s0["model_label"], s0["prompt"], s0["seed"] + 10000, 3)
        new = by_sample([json.loads(line) for line in open(src / "answers.jsonl")])
        assert len(new) == 3, cell
        d = OUT / f"{cell}_s123-01"
        d.mkdir(parents=True)
        json.dump({"job_id": job, "commit": m["commit"], "runner": "Modal H100 (tools/gpu.py)", "config": cfg,
                   "model_dir": m["engine"]["model_dir"], "raw_answers": f"runs/{job}/answers.jsonl (submitter's laptop, and the Modal Volume)",
                   "started_utc": m["started_utc"], "updated_utc": m["updated_utc"]}, open(d / "run.json", "w"), indent=1)
        json.dump(m, open(d / "metrics.json", "w"), indent=1)
        with open(d / "rows.jsonl", "w") as f:        # the shape of results/day1_3/math500_base_cue-01/rows.jsonl, plus the opening
            for s in new:
                for r in s:
                    f.write(json.dumps({"problem_index": r["problem_index"], "sample": r["sample"] + 1, "attempt": r["attempt"], "seed": r["seed"],
                                        "n_new": r["n_new"], "cap_hit": r["cap_hit"], "finish_reason": r["finish_reason"], "loop_A": r["loop_A"],
                                        "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "gold": r["gold"],
                                        "opening": r["text"][:30]}) + "\n")
        flat = [r for s in new for r in s]
        json.dump({"right": next({k: r[k] for k in EX} for r in flat if r["score_v3"] == 1),
                   "wrong": next({k: r[k] for k in EX} for r in flat if r["score_v3"] == 0 and not r["cap_hit"] and r["text"])},
                  open(d / "examples.json", "w"), indent=1)
        old = sorted(json.load(open(OUT / f"{cell}-01" / "per_problem.json")), key=lambda r: r["problem_index"])
        add(cell, f"results/ckptcue/{cell}-01 (sample 0), results/ckptcue/{cell}_s123-01 (samples 1 to 3, job {job})",
            [sample(old, "n_generated", "opening")] + [sample(s, "n_generated", "text") for s in new])

    diffs = {f"{p} minus {q}": {"points": float(100 * (x[p] - x[q]).mean()), "ci95": paired_bootstrap(x[p], x[q], n_boot=5000)}
             for p, q in PAIRS if p in x and q in x}
    json.dump({"test": "per problem the mean of score_v3 over 4 samples; paired bootstrap over the 500 problems, 5,000 resamples",
               "cells": cells, "differences": diffs}, open(OUT / "readout3.json", "w"), indent=1)
    for k, v in cells.items():
        print(f"{k:<12} mean {v['mean_right']:.2f}  samples {[s['right'] for s in v['samples']]}  cap {[s['cap_hits'] for s in v['samples']]}"
              f"  okay {[s['okay_in_first_30'] for s in v['samples']]}  tokens {v['mean_tokens_per_problem']:.0f}")
    for k, v in diffs.items():
        print(f"{k:<32} {v['points']:+5.2f} [{v['ci95'][0]:+.2f}, {v['ci95'][1]:+.2f}]")


if __name__ == "__main__":
    main()
