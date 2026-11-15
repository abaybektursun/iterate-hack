"""Readout of cell m06 (specs/SPEC_cell_m06.md): RL-Zero-Math step 100, plain, first 164 problems of hard328, one sample.

    python3 -m studies.theory.analysis.cell_m06 runs/<job-id> --job-id <job-id> --commit <sha> \
        --out studies/theory/results/experiments/cell-m06-01

Reads the job's answers.jsonl (grader v3 as the job computed it) and, as references on the same 164 problems and seeds, sample 0
of the stored cells results/day1_3/hard328_base_cue_s4r2-01 and hard328_rl_plain_s4r2-01. Writes metrics.json, per_problem.json,
examples.json and run.json. Fail loud: no try/except.
"""
import argparse
import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[3]
DAY13 = ROOT / "studies/rlneurons/results/day1_3"
FORECASTS = {"run-03/f2-m06": (26, 15, 38), "run-06/f2-m02": (6, 2, 12), "run-05/f2-m04": (8, 3, 16),
             "reader-1": (20, 9, 34), "reader-2": (22, 10, 36)}                  # cells-01/cells.md, m06-r1
CAP = 16384


def quick_wrong(r):
    return (not r["cap_hit"]) and r["score_v3"] == 0 and r["n_new"] <= 2000


def summary(rows):
    n = len(rows)
    return {"n": n, "right": sum(r["score_v3"] for r in rows), "quick_finished_wrong": sum(quick_wrong(r) for r in rows),
            "cap_hits": sum(r["cap_hit"] for r in rows), "tokens_per_problem": round(sum(r["n_new"] for r in rows) / n, 1)}


def boot(xs, draws=10000, seed=0):
    rng, n = random.Random(seed), len(xs)
    s = sorted(sum(xs[rng.randrange(n)] for _ in range(n)) for _ in range(draws))
    return [s[int(0.05 * draws)], s[int(0.95 * draws) - 1]]


def example(r, why):
    return {"why": why, "problem_index": r["problem_index"], "seed": r["seed"], "input": r["prompt"], "output": r["text"],
            "gold": r["gold"], "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "n_new": r["n_new"],
            "cap_hit": r["cap_hit"], "finish_reason": r["finish_reason"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--job-id", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--command", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run = pathlib.Path(a.run_dir)
    rows = sorted((json.loads(l) for l in open(run / "answers.jsonl") if l.strip()), key=lambda r: r["problem_index"])
    jm = json.loads((run / "metrics.json").read_text())
    assert jm["status"] == "done" and len(rows) == 164 and len({r["problem_index"] for r in rows}) == 164, (jm["status"], len(rows))
    assert all(r["seed"] == 3000000 + r["problem_index"] and r["prefix_kind"] == "none" for r in rows)
    assert all(r["cap_hit"] == (r["n_new"] == CAP) for r in rows), "a cap hit is not a row of exactly 16,384 generated tokens"
    idx = {r["problem_index"] for r in rows}

    refs = {}
    for name in ("hard328_base_cue_s4r2-01", "hard328_rl_plain_s4r2-01"):
        ref = [json.loads(l) for l in open(DAY13 / name / "rows.jsonl")]
        ref = {x["problem_index"]: x for x in ref if x["sample"] == 0 and x["attempt"] == 0 and x["problem_index"] in idx}
        assert len(ref) == 164 and all(x["seed"] == 3000000 + i for i, x in ref.items())
        refs[name] = ref

    m = summary(rows)
    m["right_interval_90"] = boot([r["score_v3"] for r in rows])
    m["quick_finished_wrong_interval_90"] = boot([int(quick_wrong(r)) for r in rows])
    m["okay_first_30_chars"] = sum("Okay" in r["text"][:30] for r in rows)
    fin = [r for r in rows if not r["cap_hit"]]
    m["finished_wrong"] = sum(1 for r in fin if r["score_v3"] == 0)
    m["finished_right_tokens_median"] = sorted(r["n_new"] for r in fin if r["score_v3"])[len([r for r in fin if r["score_v3"]]) // 2]
    q = m["quick_finished_wrong"]
    m["forecasts_m06_r1"] = {k: {"value": v, "interval_90": [lo, hi], "measured_inside": lo <= q <= hi, "abs_error": abs(q - v)}
                             for k, (v, lo, hi) in FORECASTS.items()}
    m["references_same_164"] = {k: summary(list(v.values())) for k, v in refs.items()}
    m["generation_s"] = jm["counts"]["generation_s"]
    m["job_wall_s"] = jm["wall_s"]

    per = [{"problem_index": r["problem_index"], "score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"],
            "quick_finished_wrong": quick_wrong(r), "okay_first_30": "Okay" in r["text"][:30], "extracted_v3": r["extracted_v3"],
            "gold": r["gold"], "base_cue_score_v3": refs["hard328_base_cue_s4r2-01"][r["problem_index"]]["score_v3"],
            "rl_plain_score_v3": refs["hard328_rl_plain_s4r2-01"][r["problem_index"]]["score_v3"]} for r in rows]

    right = next(r for r in rows if r["score_v3"] == 1)
    wrong = next(r for r in rows if quick_wrong(r) and r["n_new"] > 100)
    m["quick_finished_wrong_empty"] = sum(1 for r in rows if quick_wrong(r) and r["n_new"] <= 100)
    m["no_okay_opening"] = {"n": sum(1 for p in per if not p["okay_first_30"]), "right": sum(p["score_v3"] for p in per if not p["okay_first_30"]),
                            "quick_finished_wrong": sum(1 for p in per if not p["okay_first_30"] and p["quick_finished_wrong"]),
                            "cap_hits": sum(1 for p in per if not p["okay_first_30"] and p["cap_hit"])}
    ex = [example(right, "first right answer"), example(wrong, "first quick finished-wrong answer with more than 100 tokens")]

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    (out / "metrics.json").write_text(json.dumps(m, indent=1))
    (out / "per_problem.json").write_text(json.dumps(per, indent=1))
    (out / "examples.json").write_text(json.dumps(ex, indent=1))
    (out / "run.json").write_text(json.dumps({"job_id": a.job_id, "commit": a.commit, "command": a.command,
                                              "runner": "tools/vast.py run", "raw_answers": f"runs/{a.job_id}/answers.jsonl (submitter's laptop)",
                                              "job_metrics": jm["config"], "started_utc": jm["started_utc"],
                                              "updated_utc": jm["updated_utc"]}, indent=1))
    print(json.dumps({k: m[k] for k in ("n", "right", "right_interval_90", "quick_finished_wrong", "quick_finished_wrong_interval_90",
                                        "cap_hits", "tokens_per_problem", "okay_first_30_chars")}))


if __name__ == "__main__":
    main()
