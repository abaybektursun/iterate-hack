"""Readout of selfopen-01 (specs/SPEC_selfopen01.md). Laptop only: reads the job's outputs and the stored T3 / T1 rows.

    aws s3 cp s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl runs/selfopen01/T3.jsonl --profile iterate-ecr
    aws s3 cp s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl runs/selfopen01/T1.jsonl --profile iterate-ecr
    uv run --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.selfopen01 runs/<job-id> [runs/<job-id> ...] \
        --t3 runs/selfopen01/T3.jsonl --t1 runs/selfopen01/T1.jsonl --out studies/theory/results/experiments/selfopen-01

Every score is grader v3 (rln4_lib.grade_v3) recomputed from the answer text; cap hits and empty extractions keep what v3 gives
(an empty extraction is 0). Writes <out>/metrics.json, <out>/per_problem.json and <out>/examples.json. Fail loud: no try/except.
"""
import argparse
import hashlib
import json
import pathlib
import statistics

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R
from studies.theory.jobs.selfopen_gen import self_opens

THEORY = pathlib.Path(__file__).resolve().parents[1]
T1_SHA = "c65a12fcc5922c5270bb3b6abeb352246385299111c9e033dfc7deae4712ea85"   # base cue, T 1.0, seed base 41,000,000 (410 by v3)
PREDICTIONS = {"r5-m10": (375, 348, 400), "r5-m10-rival": (405, 386, 422)}


def rows(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def v3(r):
    return R.grade_v3(r["gold"], r["text"])["score_v3"]


def acc(xs):
    return {"right": sum(xs), "n": len(xs), "accuracy": round(sum(xs) / len(xs), 4) if xs else None}


def example(r, arm):
    return {"arm": arm, "problem_index": r["problem_index"], "draw": r.get("draw"), "seed": r["seed"], "input": r["prompt"],
            "output": r["text"], "gold": r["gold"], "extracted_v3": R.grade_v3(r["gold"], r["text"])["extracted_v3"],
            "score_v3": v3(r), "cap_hit": r["cap_hit"], "n_answer_tokens": r["n_answer_tokens"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="the run folders of the shards of one run")
    ap.add_argument("--t3", required=True)
    ap.add_argument("--t1", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    runs, out = [pathlib.Path(r) for r in a.runs], pathlib.Path(a.out)
    frozen = json.loads((THEORY / "data" / "selfopen01_t3.json").read_text())
    assert hashlib.sha256(pathlib.Path(a.t3).read_bytes()).hexdigest() == frozen["sha256"], "T3 differs from the frozen input"
    assert hashlib.sha256(pathlib.Path(a.t1).read_bytes()).hexdigest() == T1_SHA, "T1 differs from the stored cue cell"
    jms = [json.loads((r / "metrics.json").read_text()) for r in runs]
    assert all(j["status"] == "done" for j in jms), f"a job is not done: {[j['status'] for j in jms]}"
    keys = ("draws", "open_tokens", "max_tokens", "n", "t3_sha256")
    assert all({k: j["config"][k] for k in keys} == {k: jms[0]["config"][k] for k in keys} for j in jms), "the shards differ in setting"
    assert len({j["commit"] for j in jms}) == 1, "the shards ran different commits"
    jm = jms[0]
    t3 = {r["problem_index"]: r for r in rows(a.t3)}
    t1 = {r["problem_index"]: r for r in rows(a.t1)}
    assert sorted(t3) == sorted(t1) == list(range(500))
    stored = frozen["self_opened"]
    assert stored == sorted(i for i in t3 if self_opens(t3[i]["text"])), "the stored self-open list does not match T3"
    regen = frozen["regenerate"]
    choices = {int(k): v for r in runs for k, v in json.loads((r / "choices.json").read_text()).items()}
    assert sorted(choices) == regen, "the jobs did not cover the regenerate list"
    ans = [x for r in runs for x in rows(r / "answers.jsonl")]
    by = {(r["problem_index"], r["draw"]): r for r in ans}
    assert len(by) == len(ans)
    main_r = {i: by[(i, choices[i]["main"])] for i in regen}
    ctrl_r = {i: by[(i, choices[i]["control"])] for i in regen}
    assert all("main" in main_r[i]["arms"] and "control" in ctrl_r[i]["arms"] for i in regen)
    opened = [i for i in regen if choices[i]["any_self_open"]]
    never = [i for i in regen if not choices[i]["any_self_open"]]
    assert all(main_r[i]["opening_self_open"] for i in opened) and not any(main_r[i]["opening_self_open"] for i in never)
    n_draws = jm["config"]["draws"]

    final = {**{i: t3[i] for i in stored}, **main_r}
    final_ctrl = {**{i: t3[i] for i in stored}, **ctrl_r}
    tokens = lambda r: r["n_answer_tokens"]
    s_main = {i: v3(final[i]) for i in range(500)}
    s_ctrl = {i: v3(final_ctrl[i]) for i in range(500)}
    s_t3 = {i: v3(t3[i]) for i in range(500)}
    s_t1 = {i: v3(t1[i]) for i in range(500)}
    lo, hi = S.paired_bootstrap([s_main[i] for i in opened], [s_ctrl[i] for i in opened], n_boot=5000, seed=0)
    draws_needed = [choices[i]["draws_used_main"] for i in opened]
    sub = lambda s, idx: acc([s[i] for i in idx])
    count = sum(s_main.values())
    m = {
        "experiment": "selfopen-01", "spec": "studies/theory/specs/SPEC_selfopen01.md",
        "entry": "studies/theory/results/engine/round-05/experiments.md r5-m10:theory:intervention",
        "jobs": [{**{k: j.get(k) for k in ("commit", "job_id", "started_utc", "updated_utc", "wall_s")}, "shard": j["config"]["shard"],
                  "n_problems": j["config"]["n_problems"], "openings": j["openings"], "counts": j["counts"],
                  "engine_load_s": j["engine"]["load_s"], "gpu": j["memory"]["gpu"]} for j in jms],
        "job_config": {k: v for k, v in jm["config"].items() if k not in ("shard", "n_problems", "out")},
        "main": {"right_of_500": count, "n": 500, "cap_hits": sum(final[i]["cap_hit"] for i in range(500)),
                 "no_answer": sum(R.grade_v3(final[i]["gold"], final[i]["text"])["extracted_v3"] is None for i in range(500)),
                 "mean_generated_tokens": round(statistics.mean(tokens(final[i]) for i in range(500)), 1)},
        "subsets": {
            "a_stored_self_opened": {**sub(s_main, stored), "cap_hits": sum(t3[i]["cap_hit"] for i in stored),
                                     "mean_tokens": round(statistics.mean(tokens(t3[i]) for i in stored), 1)},
            "b_regenerated_self_opened": {**sub(s_main, opened), "cap_hits": sum(main_r[i]["cap_hit"] for i in opened),
                                          "mean_tokens": round(statistics.mean(tokens(main_r[i]) for i in opened), 1) if opened else None},
            "c_never_self_opened_fallback": {**sub(s_main, never), "cap_hits": sum(main_r[i]["cap_hit"] for i in never),
                                             "mean_tokens": round(statistics.mean(tokens(main_r[i]) for i in never), 1) if never else None},
        },
        "draws": {"n_regenerated": len(regen), "n_self_opened_within_draws": len(opened), "never_self_open": len(never),
                  "draws_per_problem": n_draws, "median_draws_needed_self_opened": statistics.median(draws_needed) if draws_needed else None,
                  "mean_draws_needed_self_opened": round(statistics.mean(draws_needed), 2) if draws_needed else None,
                  "draws_needed_le_1": sum(d <= 1 for d in draws_needed), "draws_needed_le_4": sum(d <= 4 for d in draws_needed),
                  "self_open_rate_all_draws": round(sum(choices[i]["n_self_open_of_draws"] for i in regen) / (n_draws * len(regen)), 4)},
        "control": {
            "rule": "first draw that does not self-open (draw 1 if every draw self-opens), continued like the main arm",
            "regenerated": {**sub(s_ctrl, regen), "cap_hits": sum(ctrl_r[i]["cap_hit"] for i in regen),
                            "mean_tokens": round(statistics.mean(tokens(ctrl_r[i]) for i in regen), 1)},
            "right_of_500_with_stored_self_opened": sum(s_ctrl.values()),
            "on_b_problems": {"main": sub(s_main, opened), "control": sub(s_ctrl, opened),
                              "main_minus_control_points": round(100 * (sum(s_main[i] for i in opened) - sum(s_ctrl[i] for i in opened)) / len(opened), 2),
                              "bootstrap_95_points": [round(lo, 2), round(hi, 2)], "bootstrap": "n13_score.paired_bootstrap, 5,000, seed 0",
                              "same_draw_both_arms": sum(choices[i]["main"] == choices[i]["control"] for i in opened)},
            "never_self_opened_same_answer_both_arms": sum(choices[i]["main"] == choices[i]["control"] for i in never),
            "all_draws_self_opened": sum(choices[i]["n_self_open_of_draws"] == n_draws for i in regen),
        },
        "references_stored": {
            "plain_T3": {"right_of_500": sum(s_t3.values()), "on_a": sub(s_t3, stored), "on_b": sub(s_t3, opened), "on_c": sub(s_t3, never),
                         "on_regenerated": sub(s_t3, regen), "cap_hits": sum(t3[i]["cap_hit"] for i in range(500)),
                         "mean_tokens": round(statistics.mean(tokens(t3[i]) for i in range(500)), 1)},
            "cue_T1": {"right_of_500": sum(s_t1.values()), "on_a": sub(s_t1, stored), "on_b": sub(s_t1, opened), "on_c": sub(s_t1, never),
                       "on_regenerated": sub(s_t1, regen), "cap_hits": sum(t1[i]["cap_hit"] for i in range(500)),
                       "mean_tokens": round(statistics.mean(tokens(t1[i]) for i in range(500)), 1)},
        },
        "checks": {
            "b_final_text_self_opens": sum(main_r[i]["final_self_open"] for i in opened),
            "control_final_text_self_opens": sum(ctrl_r[i]["final_self_open"] for i in regen),
            "openings_finished_inside_open_tokens_main": sum(main_r[i]["prefix_kind"] == "none" for i in regen),
        },
        "predictions": {k: {"value": v, "interval": [l, h], "count_inside": l <= count <= h, "abs_error": abs(count - v)}
                        for k, (v, l, h) in PREDICTIONS.items()},
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(m, indent=1))
    pp = [{"problem_index": i, "source": "stored_T3" if i in stored else "regenerated", "any_self_open": i in stored or choices[i]["any_self_open"],
           "draws_used": 0 if i in stored else choices[i]["draws_used_main"], "main_draw": None if i in stored else choices[i]["main"],
           "control_draw": None if i in stored else choices[i]["control"], "score_main": s_main[i], "score_control": s_ctrl[i],
           "score_t3": s_t3[i], "score_t1": s_t1[i], "cap_hit_main": final[i]["cap_hit"], "tokens_main": tokens(final[i]),
           "tokens_control": tokens(final_ctrl[i])} for i in range(500)]
    (out / "per_problem.json").write_text(json.dumps(pp, indent=0))
    ex = {}
    for arm, pool in (("main_b_regenerated_self_opened", [main_r[i] for i in opened]), ("main_c_never_self_opened", [main_r[i] for i in never]),
                      ("control_regenerated", [ctrl_r[i] for i in regen])):
        right = [r for r in pool if v3(r)]
        wrong = [r for r in pool if not v3(r)]
        ex[arm] = {"right": example(right[0], arm) if right else None, "wrong": example(wrong[0], arm) if wrong else None}
    (out / "examples.json").write_text(json.dumps(ex, indent=1))
    print(json.dumps({k: m[k] for k in ("main", "subsets", "draws")}, indent=1))
    print(json.dumps(m["control"], indent=1))


if __name__ == "__main__":
    main()
