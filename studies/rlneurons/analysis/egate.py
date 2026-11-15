"""Readout of the entropy-gated temperature cells (specs/SPEC_egate.md).

    uv run python -m studies.rlneurons.analysis.egate runs/<job-id> <experiment>/<arm>-<nn> [--ref <rows.jsonl>]

Copies the job's metrics.json, a slim rows.jsonl and one right and one wrong example per arm into results/egate/<run>/, and
writes results/egate/<run>/readout.json: per arm right (grader v3), cap hits, rule-A loops, tokens per problem, share of
positions sharpened; the stage-1 verdicts of the spec (instrument checks, the two hypotheses, the stage-2 choice) when the run
has the arms t1 and all6; and, with --ref, each arm's paired difference to the reference rows (same problems, mean over the
samples of a problem, 95 % bootstrap over problems, 5,000 resamples, seed 0).
"""
import argparse
import collections
import json
import pathlib

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
SLIM = ("arm", "problem_index", "sample", "seed", "n_new", "cap_hit", "finish_reason", "loop_A", "extracted_v3", "score_v3", "gold", "egate")
GATED = ("hi6", "hi3", "hi1", "lo6", "lo3")


def per_problem(rows):
    by = collections.defaultdict(list)
    for r in rows:
        by[r["problem_index"]].append(r["score_v3"])
    return {i: sum(v) / len(v) for i, v in by.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job_dir")
    ap.add_argument("run")
    ap.add_argument("--ref")
    a = ap.parse_args()
    job = pathlib.Path(a.job_dir)
    out = STUDY / "results" / "egate" / a.run
    out.mkdir(parents=True)
    m = json.loads((job / "metrics.json").read_text())
    assert m["status"] == "done", m["status"]
    rows = [json.loads(line) for line in open(job / "answers.jsonl")]
    arms = list(m["arms"])
    (out / "metrics.json").write_text(json.dumps(m, indent=1))
    (out / "rows.jsonl").write_text("".join(json.dumps({k: r[k] for k in SLIM}) + "\n" for r in rows))
    (out / "run.json").write_text(json.dumps({"job_id": m["job_id"], "commit": m["commit"], "config": m["config"], "h0": m["h0"],
                                             "rnd_share": m["rnd_share"], "started_utc": m["started_utc"]}, indent=1))
    ex = {}
    for arm in arms:
        fin = sorted((r for r in rows if r["arm"] == arm and not r["cap_hit"]), key=lambda r: r["n_new"])
        ex[arm] = {k: next(({f: r[f] for f in ("problem_index", "seed", "prompt", "text", "extracted_v3", "gold", "score_v3", "n_new")}
                            for r in fin if r["score_v3"] == v), None) for k, v in (("right", 1), ("wrong", 0))}
    (out / "examples.json").write_text(json.dumps(ex, indent=1))

    table = {}
    for arm in arms:
        x = [r for r in rows if r["arm"] == arm]
        fin = [r for r in x if not r["cap_hit"]]
        c = m["arms"][arm]
        table[arm] = {"n": len(x), "right": sum(r["score_v3"] for r in x), "cap_hits": sum(r["cap_hit"] for r in x),
                      "loop_A": sum(r["loop_A"] for r in x), "finished": len(fin), "right_of_finished": sum(r["score_v3"] for r in fin),
                      "tokens_per_problem": sum(r["n_new"] for r in x) / len(x), "share_sharpened": c["share_sharpened"],
                      "mean_entropy": c["mean_entropy"], "low_prob_tokens_per_1k": 1000 * sum(r["n_tok_p_lt_1e2"] for r in x) / sum(r["n_new"] for r in x)}
    ro = {"run": a.run, "job_id": m["job_id"], "commit": m["commit"], "h0_nats": m["h0"], "rnd_share": m["rnd_share"], "arms": table}

    if "t1" in table and "all6" in table:
        t1, al = table["t1"], table["all6"]
        mid = (t1["cap_hits"] + al["cap_hits"]) / 2
        hi, lo = table["hi6"]["cap_hits"], table["lo6"]["cap_hits"]
        kept = [k for k in GATED if k in table and table[k]["cap_hits"] <= t1["cap_hits"] + 4]
        t_low = {s.split("=")[0]: float(s.split(":")[1]) for s in m["config"]["arms"]}
        best = max(kept, key=lambda k: (table[k]["right"], t_low[k]), default=None)
        ro["stage1"] = {
            "checks": {"all6_minus_t1_cap_hits_at_least_8": al["cap_hits"] - t1["cap_hits"] >= 8,
                       "share_t1_0_all6_1": t1["share_sharpened"] == 0 and al["share_sharpened"] == 1,
                       "share_hi6_rnd6_in_0.10_0.35": all(0.10 <= table[k]["share_sharpened"] <= 0.35 for k in ("hi6", "rnd6"))},
            "midpoint_cap_hits": mid, "hi6_cap_hits": hi, "lo6_cap_hits": lo,
            "H_confident_refuted": hi >= mid, "H_branch_refuted": lo >= mid,
            "kept_arms": kept, "stage2_arm": best}

    if a.ref:
        ref = per_problem([r for r in map(json.loads, open(a.ref)) if r.get("attempt", 0) == 0])
        ro["reference"] = {"rows": a.ref, "mean_right_per_sample": sum(ref.values())}
        for arm in arms:
            mine = per_problem([r for r in rows if r["arm"] == arm])
            idx = sorted(mine)
            assert all(i in ref for i in idx)
            x, y = [mine[i] for i in idx], [ref[i] for i in idx]
            lo95, hi95 = S.paired_bootstrap(x, y, n_boot=5000, seed=0)
            table[arm]["vs_ref"] = {"n_problems": len(idx), "mean_right": sum(x), "ref_mean_right": sum(y),
                                    "diff_points": 100 * (sum(x) - sum(y)) / len(idx), "ci95": [lo95, hi95]}
    (out / "readout.json").write_text(json.dumps(ro, indent=1))
    print(json.dumps(ro, indent=1))


if __name__ == "__main__":
    main()
