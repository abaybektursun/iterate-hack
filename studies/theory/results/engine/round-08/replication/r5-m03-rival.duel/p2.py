"""k=2: T3 wrong rate on Q (top8 quick-wrong) minus T3 wrong rate on C (top8-right, cued base >= 3/4 at attempt 0)."""
import json
import os
import subprocess
from collections import defaultdict

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report

DIR = "runs/theory-tests/m03rival"
TOP8 = "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
CUE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
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


top8 = first_by_pi([r for r in json.load(open(TOP8)) if r.get("score_v3") is not None])
cue = [json.loads(l) for l in open(CUE) if l.strip()]
a0 = defaultdict(list)
for r in cue:
    if r["attempt"] == 0:
        a0[r["problem_index"]].append(r)
# alt: per (problem, sample) keep the row with the highest attempt (the final restart)
final = {}
for r in cue:
    key = (r["problem_index"], r["sample"])
    if key not in final or r["attempt"] > final[key]["attempt"]:
        final[key] = r
fin = defaultdict(list)
for (pi, _), r in final.items():
    fin[pi].append(r)

t3 = first_by_pi(json.loads(l) for l in open(fetch(T3_S3, "T3.jsonl")) if l.strip())
t3w = {}
for pi, r in t3.items():
    v3 = R.grade_v3(r["gold"], r["text"])["score_v3"]
    t3w[pi] = (v3 == 0 or bool(r["cap_hit"]))

Q = [pi for pi, r in top8.items() if r["score_v3"] == 0 and r["cap_hit"] is False and r["n_generated"] <= 2000 and pi in t3]


def c_set(groups):
    return [pi for pi, r in top8.items() if r["score_v3"] == 1 and r["cap_hit"] is False and pi in t3
            and len(groups.get(pi, [])) == 4 and sum(1 for x in groups[pi] if x["score_v3"] == 1) >= 3]


C = c_set(a0)
C_alt = c_set(fin)

entries = [("Q", pi, t3w[pi]) for pi in Q] + [("C", pi, t3w[pi]) for pi in C]


def stat(s):
    q = [w for g, _, w in s if g == "Q"]
    c = [w for g, _, w in s if g == "C"]
    if not q or not c:
        return 0.0
    return sum(q) / len(q) - sum(c) / len(c)


m = stat(entries)
alt = stat([("Q", pi, t3w[pi]) for pi in Q] + [("C", pi, t3w[pi]) for pi in C_alt]) if C_alt else None
print(json.dumps({"groups": {"Q": len(Q), "C": len(C)}}))
report(m, min(len(Q), len(C)), bootstrap(stat, entries), "bootstrap", refuted_by_met=False,
       alt_measured=alt, example_row=short(t3[Q[0]]))
