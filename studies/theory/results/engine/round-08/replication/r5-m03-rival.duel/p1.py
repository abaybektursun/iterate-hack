"""k=1: plain-base T 1.0 (T3) wrong rate on Q = top8 plain quick finished-wrong problems."""
import json
import os
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report

DIR = "runs/theory-tests/m03rival"
TOP8 = "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"


def fetch(s3, name):
    p = os.path.join(DIR, name)
    if not os.path.exists(p):
        os.makedirs(DIR, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, p, "--profile", "iterate-ecr"], check=True)
    return p


def first_by_pi(rows):
    out = {}
    for r in rows:
        if r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return out


def short(r):
    return {k: (v[:300] + "..." if isinstance(v, str) and len(v) > 300 else v) for k, v in r.items()}


top8 = json.load(open(TOP8))
q_rows = first_by_pi([r for r in top8 if r.get("score_v3") is not None
                      and r["score_v3"] == 0 and r["cap_hit"] is False and r["n_generated"] <= 2000])
t3 = first_by_pi(json.loads(l) for l in open(fetch(T3_S3, "T3.jsonl")) if l.strip())

problems = []
for pi in q_rows:
    if pi not in t3:
        continue
    r = t3[pi]
    v3 = R.grade_v3(r["gold"], r["text"])["score_v3"]  # empty extraction -> 0 inside grade_v3
    problems.append({"pi": pi, "v3": v3, "cap": bool(r["cap_hit"]), "row": r})


def stat(s):
    return sum(1 for p in s if p["v3"] == 0 or p["cap"]) / len(s)


def stat_alt(s):  # other reading: wrong = v3 score 0 only (cap_hit not added)
    return sum(1 for p in s if p["v3"] == 0) / len(s)


m = stat(problems)
report(m, len(problems), bootstrap(stat, problems), "bootstrap", refuted_by_met=False,
       alt_measured=stat_alt(problems), example_row=short(problems[0]["row"]))
