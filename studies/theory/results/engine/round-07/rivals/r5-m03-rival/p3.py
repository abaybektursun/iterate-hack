"""p3: plain-base T 0.6 (r3 base-01 P_math500) wrong rate on Q = top8 plain quick finished-wrong problems."""
import json
import os
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

ROOT = pathlib.Path.cwd()
TOP8 = ROOT / "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
P_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"
P = ROOT / "runs/theory-tests/s3/r3/base-01/out/P_math500.jsonl"


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
    fetch(P_S3, P)
    if not TOP8.exists() or not P.exists():
        return not_computable("row file missing: " + str(TOP8 if not TOP8.exists() else P))
    top8 = first_per_problem(r for r in json.loads(TOP8.read_text()) if r.get("score_v3") is not None)
    q = {i: r for i, r in top8.items() if r["score_v3"] == 0 and r["cap_hit"] is False and r["n_generated"] <= 2000}
    pm = {}
    for l in open(P):
        if not l.strip():
            continue
        r = json.loads(l)
        i = int(r["problem_index"])
        if i not in pm or int(r["sample"]) < int(pm[i]["sample"]):  # smallest sample; ties keep the first in file order
            pm[i] = r
    problems = []
    for i in sorted(q):
        if i not in pm:
            continue
        r = pm[i]
        g = R.grade_v3(r["gold"], r["text"])  # extracted None -> score 0
        cap = bool(r["cap_hit"])
        problems.append({"problem_index": i, "wrong": int(g["score_v3"] == 0 or cap), "wrong_alt": int(g["score_v3"] == 0),
                         "top8": q[i], "row": r, "g": g})
    if not problems:
        return not_computable("no problem in Q has a P_math500 row (Q size %d)" % len(q))

    def stat(s):
        return sum(p["wrong"] for p in s) / len(s)

    def stat_alt(s):
        return sum(p["wrong_alt"] for p in s) / len(s)

    p0 = problems[0]
    ex = {"top8": p0["top8"], "p_math500": {k: v for k, v in p0["row"].items() if k not in ("text", "answer_tokens", "prefill_ids", "cut_ids")},
          "text_tail": p0["row"]["text"][-300:], "v3": p0["g"], "wrong": p0["wrong"]}
    report(stat(problems), len(problems), bootstrap(stat, problems), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(problems), example_row=ex)


main()
