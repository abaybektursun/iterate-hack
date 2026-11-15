"""p1: plain-base T 1.0 (T3) wrong rate on Q = top8 plain quick finished-wrong problems."""
import json
import os
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

ROOT = pathlib.Path.cwd()
TOP8 = ROOT / "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
T3 = ROOT / "runs/theory-tests/s3/r4/modal_t3-01/t3/T3.jsonl"


def fetch(s3, local):
    if not local.exists():
        local.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, str(local), "--profile", os.environ.get("AWS_PROFILE", "iterate-ecr")], check=True)


def first_per_problem(rows):
    out = {}
    for r in rows:
        out.setdefault(int(r["problem_index"]), r)
    return out


def main():
    fetch(T3_S3, T3)
    if not TOP8.exists() or not T3.exists():
        return not_computable("row file missing: " + str(TOP8 if not TOP8.exists() else T3))
    top8 = first_per_problem(r for r in json.loads(TOP8.read_text()) if r.get("score_v3") is not None)
    q = {i: r for i, r in top8.items() if r["score_v3"] == 0 and r["cap_hit"] is False and r["n_generated"] <= 2000}
    t3 = first_per_problem(json.loads(l) for l in open(T3) if l.strip())
    problems = []
    for i in sorted(q):
        if i not in t3:
            continue
        r = t3[i]
        g = R.grade_v3(r["gold"], r["text"])  # extracted None -> score 0
        cap = bool(r["cap_hit"])
        problems.append({"problem_index": i, "v3": g["score_v3"], "cap_hit": cap,
                         "wrong": int(g["score_v3"] == 0 or cap), "wrong_alt": int(g["score_v3"] == 0),
                         "top8": q[i], "t3": r, "g": g})
    if not problems:
        return not_computable("no problem in Q has a T3 row (Q size %d)" % len(q))

    def stat(s):
        return sum(p["wrong"] for p in s) / len(s)

    def stat_alt(s):
        return sum(p["wrong_alt"] for p in s) / len(s)

    m = stat(problems)
    p0 = problems[0]
    ex = {"top8": p0["top8"], "t3": {k: v for k, v in p0["t3"].items() if k not in ("text", "answer_tokens", "prefill_ids")},
          "t3_text_tail": p0["t3"]["text"][-300:], "v3": p0["g"], "wrong": p0["wrong"]}
    report(m, len(problems), bootstrap(stat, problems), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(problems), example_row=ex)


main()
