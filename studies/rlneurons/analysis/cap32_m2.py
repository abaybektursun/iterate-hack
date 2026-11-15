"""Readout of SPEC_transplant.md amendment 4: one sample of M(2) = Think-SFT + 2 (RL-Math - base) on hard328 at a cap of 32,768
generated tokens, scored at 32,768 and at 16,384 from the same answers (the analysis/cap32.py rule), paired by problem with
Think-SFT + cue at 32,768 on the same per-problem seeds.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.cap32_m2 \
        --m2 runs/<joined M(2) run> --think runs/<joined Think-SFT run> --out studies/rlneurons/results/transplant/cap32_m2_s1-01 \
        --command '<the job command>'

Both inputs are run folders (metrics.json, answers.jsonl) as written by run_cell or by analysis/shard_join.py. Writes run.json,
metrics.json, rows.jsonl (one small row per problem, both models), examples.json (one right and one wrong M(2) answer). Fail loud.
"""
import argparse
import json
import pathlib

from studies.rlneurons.lib import n13_score as S

OLD, NEW, N = 16384, 32768, 328


def load(d):
    m = json.loads((pathlib.Path(d) / "metrics.json").read_text())
    c = m["config"]
    assert m["status"] == "done" and c["set"] == "hard328" and c["max_tokens"] == NEW and c["n"] is None and c["prompt"] == "cue", d
    rows = sorted(map(json.loads, open(pathlib.Path(d) / "answers.jsonl")), key=lambda r: r["problem_index"])
    assert len({r["problem_index"] for r in rows}) == len(rows) == N, d
    return m, rows


def view(rows):
    r32 = [r["score_v3"] for r in rows]
    r16 = [r["score_v3"] if r["n_new"] <= OLD and not r["cap_hit"] else 0 for r in rows]
    return {"right_at_32768": sum(r32), "right_at_16384_view": sum(r16),
            "cap_hits_at_32768": sum(r["cap_hit"] for r in rows),
            "cap_hits_at_16384_view": sum(r["cap_hit"] or r["n_new"] > OLD for r in rows),
            "tokens_per_problem_at_32768": round(sum(r["n_new"] for r in rows) / N, 1),
            "tokens_per_problem_at_16384_view": round(sum(min(r["n_new"], OLD) for r in rows) / N, 1)}, r32, r16


def diff(x, y):
    lo, hi = S.paired_bootstrap(x, y, n_boot=10000, seed=0)
    return {"problems": sum(x) - sum(y), "points": round(100 * (sum(x) - sum(y)) / N, 2), "ci95": [round(lo, 2), round(hi, 2)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m2", required=True)
    ap.add_argument("--think", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--command", required=True)
    a = ap.parse_args()
    (mm, mr), (tm, tr) = load(a.m2), load(a.think)
    assert [(r["problem_index"], r["seed"]) for r in mr] == [(r["problem_index"], r["seed"]) for r in tr], "problems or per-problem seeds differ"
    vm, m32, m16 = view(mr)
    vt, t32, t16 = view(tr)
    right = vm["right_at_32768"]
    reading = "H-tokens (225-235: the delta only saves tokens)" if 225 <= right <= 235 else \
        "H-more (240+: the delta adds right answers)" if right >= 240 else \
        "undecided (236-239)" if 236 <= right <= 239 else "below H-tokens (under 225)"
    met = {"spec": "studies/rlneurons/specs/SPEC_transplant.md amendment 4", "set": "hard328", "n": N, "grader": "v3",
           "seed": mm["config"]["seed"], "m2": vm, "think_sft": vt,
           "m2_gain_32768_over_16384_view": diff(m32, m16),
           "m2_minus_think_at_32768": diff(m32, t32), "m2_minus_think_at_16384_view": diff(m16, t16),
           "answers_longer_than_16384": {"m2": sum(r["n_new"] > OLD for r in mr), "m2_right": sum(r["score_v3"] for r in mr if r["n_new"] > OLD),
                                         "think_sft": sum(r["n_new"] > OLD for r in tr), "think_sft_right": sum(r["score_v3"] for r in tr if r["n_new"] > OLD)},
           "reading_amendment_3": reading,
           "bootstrap": "paired over problems, 10,000 resamples, seed 0 (n13_score.paired_bootstrap)"}
    out = pathlib.Path(a.out)
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(json.dumps(met, indent=1) + "\n")
    (out / "run.json").write_text(json.dumps({
        "m2": {"job_id": mm["job_id"], "commit": mm["commit"], "config": mm["config"], "command": a.command,
               "raw_answers": f"{a.m2}/answers.jsonl on the laptop of abaybektursun (Modal Volume iterate-runs; not in git)"},
        "think_sft": {"job_id": tm["job_id"], "commit": tm["commit"], "config": tm["config"],
                      "raw_answers": "s3://iterate-hack-team-769063704696/handoff/cap32vote/<job-id>/answers.jsonl"}}, indent=1) + "\n")
    keys = ("n_new", "cap_hit", "score_v3", "extracted_v3")
    (out / "rows.jsonl").write_text("".join(json.dumps({"problem_index": m["problem_index"], "seed": m["seed"], "gold": m["gold"],
                                                         "m2": {k: m[k] for k in keys}, "think_sft": {k: t[k] for k in keys}}) + "\n"
                                            for m, t in zip(mr, tr)))
    ex = lambda r: {k: r[k] for k in ("problem_index", "seed", "gold", "extracted_v3", "score_v3", "n_new", "cap_hit")} | \
        {"prompt": r["prompt"], "answer_tail": r["text"][-1200:]}
    late = [r for r in mr if r["n_new"] > OLD and not r["cap_hit"]]
    (out / "examples.json").write_text(json.dumps({
        "right": ex(next(r for r in late + mr if r["score_v3"])),
        "wrong_finished": ex(next(r for r in mr if not r["score_v3"] and not r["cap_hit"]))}, indent=1) + "\n")
    print(json.dumps(met, indent=1))


if __name__ == "__main__":
    main()
