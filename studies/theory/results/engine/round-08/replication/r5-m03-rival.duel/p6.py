"""k=6: on cued-4/4 problems, T3 wrong rate when P_math500 is wrong minus T3 wrong rate when P_math500 is right."""
import json
import os
import subprocess
from collections import defaultdict

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

DIR = "runs/theory-tests/m03rival"
CUE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
P_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"


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


def min_sample_by_pi(rows):
    out = {}
    for r in rows:
        if r["problem_index"] not in out or r["sample"] < out[r["problem_index"]]["sample"]:
            out[r["problem_index"]] = r
    return out


def short(r):
    return {k: (v[:300] + "..." if isinstance(v, str) and len(v) > 300 else v) for k, v in r.items()}


def wrong(r):
    g = R.grade_v3(r["gold"], r["text"])
    return g["score_v3"] == 0 or bool(r["cap_hit"]) or g["extracted_v3"] is None or not str(g["extracted_v3"]).strip()


cue = [json.loads(l) for l in open(CUE) if l.strip()]
a0 = defaultdict(list)
for r in cue:
    if r["attempt"] == 0:
        a0[r["problem_index"]].append(r)
final = {}
for r in cue:
    key = (r["problem_index"], r["sample"])
    if key not in final or r["attempt"] > final[key]["attempt"]:
        final[key] = r
fin = defaultdict(list)
for (pi, _), r in final.items():
    fin[pi].append(r)

t3 = first_by_pi(json.loads(l) for l in open(fetch(T3_S3, "T3.jsonl")) if l.strip())
pm = min_sample_by_pi(json.loads(l) for l in open(fetch(P_S3, "P_math500.jsonl")) if l.strip())
t3w = {pi: wrong(r) for pi, r in t3.items()}
pw = {pi: wrong(r) for pi, r in pm.items()}


def problem_set(groups):
    return [pi for pi, rs in groups.items() if len(rs) == 4 and all(x["score_v3"] == 1 for x in rs) and pi in t3 and pi in pm]


def stat(s):
    a = [tw for p_w, tw in s if p_w]
    b = [tw for p_w, tw in s if not p_w]
    if not a or not b:
        return 0.0
    return sum(a) / len(a) - sum(b) / len(b)


S = sorted(problem_set(a0))
entries = [(pw[pi], t3w[pi]) for pi in S]
nPw = sum(1 for p_w, _ in entries if p_w)
nPr = len(entries) - nPw
print(json.dumps({"groups": {"P_wrong": nPw, "P_right": nPr}}))
if nPw == 0 or nPr == 0:
    not_computable("a conditioning group is empty (P_wrong=%d, P_right=%d); recipe says report nothing" % (nPw, nPr))
else:
    S_alt = sorted(problem_set(fin))
    alt_entries = [(pw[pi], t3w[pi]) for pi in S_alt]
    alt_ok = any(p for p, _ in alt_entries) and any(not p for p, _ in alt_entries)
    report(stat(entries), min(nPw, nPr), bootstrap(stat, entries), "bootstrap", refuted_by_met=False,
           alt_measured=stat(alt_entries) if alt_ok else None,
           example_row={"T3": short(t3[S[0]]), "P_math500": short(pm[S[0]])})
