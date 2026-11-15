"""k=5: P_math500 (T 0.6, not self-opened) v3 accuracy on cued-4/4 problems minus on cued <= 1/4 problems."""
import json
import os
import re
import subprocess
from collections import defaultdict

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

DIR = "runs/theory-tests/m03rival"
CUE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
P_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"


def fetch(s3, name):
    p = os.path.join(DIR, name)
    if not os.path.exists(p):
        os.makedirs(DIR, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, p, "--profile", "iterate-ecr"], check=True)
    return p


def min_sample_by_pi(rows):
    out = {}
    for r in rows:
        if r["problem_index"] not in out or r["sample"] < out[r["problem_index"]]["sample"]:
            out[r["problem_index"]] = r
    return out


def short(r):
    return {k: (v[:300] + "..." if isinstance(v, str) and len(v) > 300 else v) for k, v in r.items()}


a0 = defaultdict(list)
for l in open(CUE):
    if l.strip():
        r = json.loads(l)
        if r["attempt"] == 0:
            a0[r["problem_index"]].append(r)
kq = {pi: sum(1 for x in rs if x["score_v3"] == 1) for pi, rs in a0.items() if len(rs) == 4}

pm = min_sample_by_pi(json.loads(l) for l in open(fetch(P_S3, "P_math500.jsonl")) if l.strip())
scored = {}
for pi, r in pm.items():
    v3 = R.grade_v3(r["gold"], r["text"])["score_v3"]  # empty extraction -> 0
    scored[pi] = 0 if r["cap_hit"] else v3

SELF_ALT = re.compile(r"(^|\n)\s*Okay")


def build(selfopen):
    out = []
    for pi, r in pm.items():
        if selfopen(r["text"][:60]) or pi not in kq:
            continue
        if kq[pi] == 4:
            out.append(("E", pi, scored[pi]))
        elif kq[pi] <= 1:
            out.append(("H", pi, scored[pi]))
    return out


def stat(s):
    e = [v for g, _, v in s if g == "E"]
    h = [v for g, _, v in s if g == "H"]
    if not e or not h:
        return 0.0
    return sum(e) / len(e) - sum(h) / len(h)


entries = build(lambda head: "\nOkay" in head)
nE = sum(1 for g, _, _ in entries if g == "E")
nH = sum(1 for g, _, _ in entries if g == "H")
if nE == 0 or nH == 0:
    print(json.dumps({"groups": {"E": nE, "H": nH}}))
    not_computable("a group is empty (E=%d, H=%d); recipe says report nothing" % (nE, nH))
else:
    alt_entries = build(lambda head: SELF_ALT.search(head) is not None)
    alt_ok = any(g == "E" for g, _, _ in alt_entries) and any(g == "H" for g, _, _ in alt_entries)
    print(json.dumps({"groups": {"E": nE, "H": nH}}))
    report(stat(entries), min(nE, nH), bootstrap(stat, entries), "bootstrap", refuted_by_met=False,
           alt_measured=stat(alt_entries) if alt_ok else None, example_row=short(pm[entries[0][1]]))
