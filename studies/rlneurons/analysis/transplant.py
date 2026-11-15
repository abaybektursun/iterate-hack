"""Readout of the delta transplant (specs/SPEC_transplant.md): Think-SFT + a (RL-Math - base) against its two parents.

    uv run --with numpy python -m studies.rlneurons.analysis.transplant <run> --arm <label>=runs/<job-id> [--arm ...] \
        --ref think=runs/<job-id>,runs/<job-id> --ref rl=runs/<job-id>

Writes results/transplant/<run>/: metrics.json and delta_sum.json of every arm's job, a slim rows.jsonl (arms and references),
examples.json (one right and one wrong finished answer per arm, with the prompt) and readout.json: per arm and per reference
sample right (grader v3), cap hits, rule-A loops, finished, right of finished, tokens per problem; and each arm's difference to
each reference per problem (the reference is the mean over its samples; first attempts only; 95 % bootstrap over problems,
5,000 resamples, seed 0).
"""
import argparse
import collections
import json
import pathlib

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
SLIM = ("problem_index", "sample", "seed", "n_new", "cap_hit", "loop_A", "extracted_v3", "score_v3", "gold")


def rows_of(job_dir):
    return [r for r in map(json.loads, open(pathlib.Path(job_dir) / "answers.jsonl")) if r.get("attempt", 0) == 0]


def cell(rows):
    fin = [r for r in rows if not r["cap_hit"]]
    return {"n": len(rows), "right": sum(r["score_v3"] for r in rows), "cap_hits": sum(r["cap_hit"] for r in rows), "loop_A": sum(r["loop_A"] for r in rows),
            "finished": len(fin), "right_of_finished": sum(r["score_v3"] for r in fin), "tokens_per_problem": sum(r["n_new"] for r in rows) / len(rows)}


def per_problem(rows, key):
    by = collections.defaultdict(list)
    for r in rows:
        by[r["problem_index"]].append(r[key])
    return {i: sum(v) / len(v) for i, v in by.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--arm", action="append", required=True)
    ap.add_argument("--ref", action="append", required=True)
    a = ap.parse_args()
    out = STUDY / "results" / "transplant" / a.run
    out.mkdir(parents=True)
    arms = dict(s.split("=") for s in a.arm)
    refs = {k: v.split(",") for k, v in (s.split("=") for s in a.ref)}
    rows, slim, ro = {}, [], {"run": a.run, "arms": {}, "references": {}}
    metrics, merges = {}, {}
    for label, d in arms.items():
        metrics[label] = json.loads((pathlib.Path(d) / "metrics.json").read_text())
        assert metrics[label]["status"] == "done", (label, metrics[label]["status"])
        merges[label] = json.loads((pathlib.Path(d) / "delta_sum.json").read_text())
        rows[label] = rows_of(d)
        ro["arms"][label] = {"job": pathlib.Path(d).name, "alpha": merges[label]["args"]["alpha"], "random": merges[label]["args"]["random"],
                             "effective_a": merges[label]["effective_a"], **cell(rows[label])}
    for name, ds in refs.items():
        rows[name] = [r for d in ds for r in rows_of(d)]
        by = collections.defaultdict(list)
        for d in ds:
            for r in rows_of(d):
                by[(pathlib.Path(d).name, r["sample"])].append(r)
        ro["references"][name] = {"jobs": [pathlib.Path(d).name for d in ds], "samples": {f"{j} sample {s}": cell(v) for (j, s), v in sorted(by.items())}}
    for label in arms:
        ro["arms"][label]["minus"] = {}
        for name in refs:
            for key in ("score_v3", "cap_hit"):
                x, y = per_problem(rows[label], key), per_problem(rows[name], key)
                assert sorted(x) == sorted(y), f"{label} and {name} cover different problems"
                idx = sorted(x)
                xs, ys = [float(x[i]) for i in idx], [float(y[i]) for i in idx]
                lo, hi = S.paired_bootstrap(xs, ys, n_boot=5000, seed=0)
                ro["arms"][label]["minus"][f"{name} {key}"] = {"n_problems": len(idx), "arm": sum(xs), "reference": sum(ys),
                                                               "diff_points": 100 * (sum(xs) - sum(ys)) / len(idx), "ci95": [lo, hi]}
    for name, rs in rows.items():
        slim += [{"arm": name, **{k: r[k] for k in SLIM}} for r in rs]
    ex = {}
    for label in arms:
        fin = sorted((r for r in rows[label] if not r["cap_hit"]), key=lambda r: r["n_new"])
        ex[label] = {k: next(({f: r[f] for f in ("problem_index", "seed", "prompt", "text", "extracted_v3", "gold", "score_v3", "n_new")}
                              for r in fin if r["score_v3"] == v), None) for k, v in (("right", 1), ("wrong", 0))}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    (out / "delta_sum.json").write_text(json.dumps(merges, indent=1))
    (out / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in slim))
    (out / "examples.json").write_text(json.dumps(ex, indent=1))
    (out / "readout.json").write_text(json.dumps(ro, indent=1))
    print(json.dumps(ro, indent=1))


if __name__ == "__main__":
    main()
