"""Readout of round-09 cell m11 (specs/SPEC_cells_r9a.md): base - 1.0 x top-8 directions of (RL-Math 3.1 - base), cue, MATH-500.
Laptop only.

    python3 -m studies.theory.analysis.cells_r9a runs/<job-shard> [...] [--partial runs/<job>] --jobs '<json: shard -> job id>' \
        --commit <sha> --cmd '<command>' --out studies/theory/results/experiments/cell-r9-m11-01

Reads each <run>/answers.jsonl and <run>/metrics.json (written by studies/rlneurons/jobs/run_cell.py, one per finished shard),
merges the rows, checks one row per problem of the shards, scores every forecast of readout m11-r1 in results/wide/round-09/cell_forecasts.json, and compares
with the stored cued base at the same seeds (sample 0, attempt 0 of studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl).
--partial: a shard stopped before its end; its finished rows are summarised apart (they are the shorter answers, so biased) and
are not in the readout. Writes <out>/run.json, metrics.json, per_problem.json, examples.json. Fail loud.
"""
import argparse
import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[3]
ROUND = ROOT / "studies/theory/results/wide/round-09"
BASE = ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
SEED, READOUT = 41000000, "m11-r1"


def interval(rng, xs):
    boot = sorted(sum(rng.choices(xs, k=len(xs))) for _ in range(10000))
    return [boot[500], boot[9499]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--partial")
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--cmd", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    rows, planned = [], []
    for run in map(pathlib.Path, a.runs):
        jm = json.loads((run / "metrics.json").read_text())
        assert jm["status"] == "done", (run, jm["status"])
        cfg = jm["config"]
        assert (cfg["prompt"], cfg["set"], cfg["temperature"], cfg["top_p"], cfg["min_p"], cfg["max_tokens"], cfg["seed"],
                cfg["samples"], cfg["restarts"], cfg["n"], cfg["commit"]) == ("cue", "math500", 1.0, 1.0, 0.0, 16384, SEED, 1, 0, None, a.commit), cfg
        part = [json.loads(l) for l in open(run / "answers.jsonl") if l.strip()]
        assert len(part) == cfg["n_problems"] == jm["counts"]["n"], run
        k, n_shards = (int(x) for x in cfg["shard"].split("/"))
        planned += list(range(500))[k::n_shards]
        rows += part
    rows.sort(key=lambda r: r["problem_index"])
    assert [r["problem_index"] for r in rows] == sorted(planned), "not one row per problem of the shards"
    assert all(r["seed"] == SEED + r["problem_index"] for r in rows)
    base_all = {r["problem_index"]: r for r in map(json.loads, open(BASE)) if r["sample"] == 0 and r["attempt"] == 0}
    assert sorted(base_all) == list(range(500)) and all(r["seed"] == SEED + i for i, r in base_all.items())
    base = [base_all[r["problem_index"]] for r in rows]
    n, rng = len(rows), random.Random(0)
    cap = [int(r["cap_hit"]) for r in rows]
    right = [r["score_v3"] for r in rows]
    bcap = [int(r["cap_hit"]) for r in base]
    measured = sum(cap)
    fc = json.loads((ROUND / "cell_forecasts.json").read_text())
    forecasts = {who: {"family": v["family"], "value": f["value"], "interval": [f["low"], f["high"]]}
                 for who, v in fc.items() for f in v["forecasts"] if f["readout"] == READOUT and f["value"] is not None}
    unboxed = ["\\boxed" not in r["text"] for r in rows]
    finished = [r for r in rows if not r["cap_hit"]]
    metrics = {"cell": "m11", "readout": READOUT, "measured": measured, "n": n, "interval_90": interval(rng, cap),
               "right_v3": sum(right), "right_v3_interval_90": interval(rng, right), "cap_hits": measured,
               "mean_generated_tokens": sum(r["n_new"] for r in rows) / n,
               "median_generated_tokens": sorted(r["n_new"] for r in rows)[n // 2], "no_boxed": sum(unboxed),
               "loop_A": sum(r["loop_A"] for r in rows), "finished": len(finished),
               "right_per_finished": sum(r["score_v3"] for r in finished) / len(finished),
               "base_same_seeds": {"source": str(BASE.relative_to(ROOT)), "cap_hits": sum(bcap), "right_v3": sum(r["score_v3"] for r in base),
                                   "mean_generated_tokens": sum(r["n_new"] for r in base) / n,
                                   "cap_hits_diff_interval_90": interval(rng, [x - y for x, y in zip(cap, bcap)]),
                                   "right_diff_interval_90": interval(rng, [x - y["score_v3"] for x, y in zip(right, base)]),
                                   "cap_both": sum(x and y for x, y in zip(cap, bcap))},
               "problems": "every problem index of the shards " + ", ".join(json.loads(a.jobs)), "forecasts": forecasts}
    if a.partial:
        pm = json.loads((pathlib.Path(a.partial) / "metrics.json").read_text())
        assert pm["config"]["seed"] == SEED and pm["config"]["commit"] == a.commit, pm["config"]
        prow = [json.loads(l) for l in open(pathlib.Path(a.partial) / "answers.jsonl") if l.strip()]
        assert not {r["problem_index"] for r in prow} & set(planned)
        pb = [base_all[r["problem_index"]] for r in prow]
        metrics["partial_shard"] = {"run": a.partial, "shard": pm["config"]["shard"], "finished_rows": len(prow), "planned": pm["config"]["n_problems"],
                                    "cap_hits": sum(r["cap_hit"] for r in prow), "right_v3": sum(r["score_v3"] for r in prow),
                                    "mean_generated_tokens": sum(r["n_new"] for r in prow) / len(prow),
                                    "base_same_problems": {"cap_hits": sum(r["cap_hit"] for r in pb), "right_v3": sum(r["score_v3"] for r in pb)},
                                    "missing": sorted(set(range(500)[slice(*(lambda k, m: (k, None, m))(*map(int, pm["config"]["shard"].split("/"))))]) - {r["problem_index"] for r in prow})}
    per = [{"problem_index": r["problem_index"], "unique_id": r["unique_id"], "gold": r["gold"], "extracted_v3": r["extracted_v3"],
            "score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"], "loop_A": r["loop_A"], "no_boxed": u,
            "base_score_v3": b["score_v3"], "base_cap_hit": b["cap_hit"], "base_n_new": b["n_new"]}
           for r, u, b in zip(rows, unboxed, base)]
    ex = lambda r: {"problem_index": r["problem_index"], "unique_id": r["unique_id"], "input": r["prompt"], "output": r["text"],
                    "gold": r["gold"], "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"]}
    examples = {"right": ex(next(r for r in rows if r["score_v3"])), "wrong": ex(next(r for r in rows if not r["score_v3"]))}
    out.mkdir(parents=True, exist_ok=False)
    # The forecasts are cap hits of all 500. Without scaling, the rows give bounds on that count: every cap hit found counts, and
    # every problem with no finished row may or may not be one.
    found = measured + (metrics["partial_shard"]["cap_hits"] if a.partial else 0)
    unknown = 500 - n - (metrics["partial_shard"]["finished_rows"] if a.partial else 0)
    metrics["cap_hits_of_500_bounds"] = [found, found + unknown]
    for f in forecasts.values():
        f["verdict"] = "refuted" if f["interval"][1] < found or f["interval"][0] > found + unknown else "not decided"
    (out / "run.json").write_text(json.dumps({"cell": "m11", "spec": "studies/theory/specs/SPEC_cells_r9a.md", "jobs": json.loads(a.jobs),
                                              "commit": a.commit, "command": a.cmd, "raw": [str(p) for p in a.runs]}, indent=1))
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    (out / "per_problem.json").write_text(json.dumps(per, indent=1))
    (out / "examples.json").write_text(json.dumps(examples, indent=1))
    print(json.dumps({k: v for k, v in metrics.items() if k != "forecasts"}, indent=1))
    for who, f in forecasts.items():
        print(f"{who:28s} {f['value']:>6} {f['interval']}  {f['verdict']}")


if __name__ == "__main__":
    main()
