"""Readout of the delta transplant (specs/SPEC_transplant.md): Think-SFT + a (RL-Math - base) against its two parents.

    uv run --with numpy python -m studies.rlneurons.analysis.transplant <run> --arm <label>=runs/<job-id>[,runs/<job-id>] [--arm ...] \
        --ref think=<rows.jsonl> --ref rl=<rows.jsonl>

An arm with several jobs has one sample per job (different seeds). Where an arm or a reference has more than one sample, the
plurality vote of day1_vote over its samples is added, and its paired difference where both sides have the same number. A reference is a committed rows.jsonl with a `sample` field.

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

from studies.rlneurons.analysis.day1_vote import vote
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
SLIM = ("problem_index", "sample", "seed", "n_new", "cap_hit", "loop_A", "extracted_v3", "score_v3", "gold")


def rows_of(path):
    path = pathlib.Path(path)
    return [r for r in map(json.loads, open(path / "answers.jsonl" if path.is_dir() else path)) if r.get("attempt", 0) == 0]


def cell(rows):
    fin = [r for r in rows if not r["cap_hit"]]
    return {"n": len(rows), "right": sum(r["score_v3"] for r in rows), "cap_hits": sum(r["cap_hit"] for r in rows), "loop_A": sum(r["loop_A"] for r in rows),
            "finished": len(fin), "right_of_finished": sum(r["score_v3"] for r in fin), "tokens_per_problem": sum(r["n_new"] for r in rows) / len(rows)}


def per_problem(rows, key):
    by = collections.defaultdict(list)
    for r in rows:
        by[r["problem_index"]].append(r[key])
    return {i: sum(v) / len(v) for i, v in by.items()}


def votes(rows):
    """per problem, the score of the plurality vote (day1_vote.vote) over the rows in sample order (`_s`)"""
    by = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: r["_s"]):
        by[r["problem_index"]].append(r)
    return {i: vote(v)["score"] for i, v in by.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--arm", action="append", required=True)
    ap.add_argument("--ref", action="append", required=True)
    a = ap.parse_args()
    out = STUDY / "results" / "transplant" / a.run
    out.mkdir(parents=True)
    arms = {k: v.split(",") for k, v in (s.split("=") for s in a.arm)}
    refs = dict(s.split("=") for s in a.ref)
    rows, slim, ro = {}, [], {"run": a.run, "arms": {}, "references": {}}
    metrics, merges = {}, {}
    for label, ds in arms.items():
        metrics[label] = [json.loads((pathlib.Path(d) / "metrics.json").read_text()) for d in ds]
        assert all(m["status"] == "done" for m in metrics[label]), label
        merges[label] = [json.loads((pathlib.Path(d) / "delta_sum.json").read_text()) for d in ds]
        rows[label] = [{**r, "_s": k} for k, d in enumerate(ds) for r in rows_of(d)]
        m = merges[label][0]
        ro["arms"][label] = {"jobs": [pathlib.Path(d).name for d in ds], "alpha": m["args"]["alpha"], "random": m["args"]["random"],
                             "effective_a": m["effective_a"], "written_norm_over_intended": m["written_norm_over_intended"],
                             "samples": {pathlib.Path(d).name: cell(rows_of(d)) for d in ds}, **cell(rows[label])}
    for name, f in refs.items():
        rows[name] = [{**r, "_s": r["sample"]} for r in rows_of(f)]
        by = collections.defaultdict(list)
        for r in rows[name]:
            by[r["sample"]].append(r)
        ro["references"][name] = {"rows": f, "samples": {f"sample {s}": cell(v) for s, v in sorted(by.items())}, **cell(rows[name])}
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
    n_s = {k: len({r["_s"] for r in v}) for k, v in rows.items()}
    v = {k: votes(rs) for k, rs in rows.items() if n_s[k] > 1}
    for k in v:
        (ro["arms"] if k in arms else ro["references"])[k]["vote"] = {"samples": n_s[k], "right": sum(v[k].values())}
    for label in arms:
        for name in refs:
            if label in v and name in v and n_s[label] == n_s[name]:
                idx = sorted(v[label])
                xs, ys = [float(v[label][i]) for i in idx], [float(v[name][i]) for i in idx]
                lo, hi = S.paired_bootstrap(xs, ys, n_boot=5000, seed=0)
                ro["arms"][label]["minus"][f"{name} vote"] = {"n_problems": len(idx), "arm": sum(xs), "reference": sum(ys),
                                                              "diff_points": 100 * (sum(xs) - sum(ys)) / len(idx), "ci95": [lo, hi]}
    for name, rs in rows.items():
        slim += [{"arm": name, **{k: r[k] for k in SLIM}} for r in rs]
    ex = {}
    for label in arms:
        fin = sorted((r for r in rows_of(arms[label][0]) if not r["cap_hit"]), key=lambda r: r["n_new"])
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
