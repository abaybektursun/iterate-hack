"""Readout of cell m20 (specs/SPEC_cell_m20.md): the untrained base, plain prompt, fresh2026, 1 sample. Laptop only.

    python3 -m studies.theory.analysis.cell_m20 runs/<job-id> --job <job-id> --commit <sha> --cmd '<command>' \
        --out studies/theory/results/experiments/cell-m20-01

Reads <run>/answers.jsonl and <run>/metrics.json (written by studies/rlneurons/jobs/run_fresh.py); scores are the job's grader v3.
Writes <out>/run.json, metrics.json, per_problem.json, examples.json. Fail loud: no try/except.
"""
import argparse
import json
import pathlib
import random

FORECASTS = {"run-06/f2-m02": (3, 0, 8), "run-06/f2-m06": (2, 0, 7), "run-07/f2-m06": (16, 9, 23), "run-08/f2-m01": (14, 8, 20),
             "reader-1": (14, 7, 22), "reader-2": (13, 6, 21)}
BASE_CUE = [28, 28, 32, 30]   # result-5251c9, the same 136 problems, one sample each


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--job", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--cmd", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run, out = pathlib.Path(a.run), pathlib.Path(a.out)
    jm = json.loads((run / "metrics.json").read_text())
    assert jm["status"] == "done", jm["status"]
    cfg = jm["config"]
    assert (cfg["model"], cfg["prompt"], cfg["set"], cfg["temperature"], cfg["top_p"], cfg["min_p"], cfg["max_tokens"], cfg["seed"],
            cfg["samples"], cfg["restarts"], cfg["n"], cfg["commit"]) == \
        ("base", "plain", "fresh2026", 1.0, 1.0, 0.0, 16384, 93000000, 1, 0, None, a.commit), cfg
    rows = sorted((json.loads(l) for l in open(run / "answers.jsonl") if l.strip()), key=lambda r: r["problem_index"])
    assert [r["problem_index"] for r in rows] == list(range(136)), "not one row per problem"
    scores = [r["score_v3"] for r in rows]
    right = sum(scores)
    assert right == jm["counts"]["correct_v3"]
    rng = random.Random(0)
    boot = sorted(sum(rng.choices(scores, k=len(scores))) for _ in range(10000))
    interval = [boot[500], boot[9499]]
    opens = ["Okay" in r["text"][:60] for r in rows]   # opens in the cue's style on its own (the text often starts with ".\n\n")
    per = [{"problem_index": r["problem_index"], "unique_id": r["unique_id"], "gold": r["gold"], "extracted_v3": r["extracted_v3"],
            "score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"], "opens_okay": o} for r, o in zip(rows, opens)]
    finished = [r for r in rows if not r["cap_hit"]]
    metrics = {"cell": "m20", "right_v3": right, "n": 136, "interval_90": interval,
               "cap_hits": sum(r["cap_hit"] for r in rows), "mean_generated_tokens": sum(r["n_new"] for r in rows) / 136,
               "opens_okay": sum(opens), "right_v3_when_opens_okay": sum(s for s, o in zip(scores, opens) if o),
               "finished": len(finished), "precision_finished": right / len(finished),
               "reference_base_cue_per_sample": BASE_CUE,
               "forecasts": {k: {"value": v, "interval": [lo, hi], "inside": lo <= right <= hi} for k, (v, lo, hi) in FORECASTS.items()},
               "job_counts": jm["counts"], "config": cfg}
    ex = lambda r: {"problem_index": r["problem_index"], "unique_id": r["unique_id"], "input": r["prompt"], "output": r["text"],
                    "gold": r["gold"], "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"]}
    examples = {"right": ex(next(r for r in rows if r["score_v3"])), "wrong": ex(next(r for r in rows if not r["score_v3"]))}
    out.mkdir(parents=True, exist_ok=False)
    (out / "run.json").write_text(json.dumps({"job_id": a.job, "commit": a.commit, "command": a.cmd, "raw": str(run)}, indent=1))
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    (out / "per_problem.json").write_text(json.dumps(per, indent=1))
    (out / "examples.json").write_text(json.dumps(examples, indent=1))
    print(json.dumps({k: metrics[k] for k in ("right_v3", "interval_90", "cap_hits", "mean_generated_tokens", "opens_okay",
                                              "right_v3_when_opens_okay", "finished", "precision_finished")}, indent=1))


if __name__ == "__main__":
    main()
