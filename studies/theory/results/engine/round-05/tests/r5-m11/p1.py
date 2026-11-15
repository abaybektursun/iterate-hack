"""r5-m11 prediction 1: MATH-500 subject contrast, Code-RL 3.1 cue minus mean of 4 RL plain samples.

S = mean(d over NT + C&P) - mean(d over IA + Precalculus), d = code - mean(RL s0..s3).
Main: subject names matched after normalising the recipe's display names to the
per_problem.json spelling (lowercase, '&' -> 'and', spaces -> '_'), problems pooled within a group.
alt_measured: each group's mean taken as the unweighted mean of its two subject means.
"""
import json
import os
import sys

ROOT = os.getcwd()
VEC = os.path.join(ROOT, "studies/rlneurons/results/axis/math500-01/vectors.json")
MAN = os.path.join(ROOT, "studies/rlneurons/results/axis/math500-01/manifest.json")
PP = os.path.join(ROOT, "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json")
CODE_JOB = "abaybektursun-1114-162452-0203"
RL_JOB = "abaybektursun-1114-183640-e828"
GROUP_A = ["Number Theory", "Counting & Probability"]
GROUP_B = ["Intermediate Algebra", "Precalculus"]


def out(d):
    print(json.dumps(d))
    sys.exit(0)


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def norm(s):
    return s.strip().lower().replace("&", "and").replace(" ", "_")


for f in (VEC, MAN, PP):
    if not os.path.exists(f):
        nc(f"file missing: {f}")

vec = json.load(open(VEC))
man = json.load(open(MAN))
pp = json.load(open(PP))

arms_man = man["arms"]
code_arms = [a for a, e in arms_man.items() if e.get("job_id") == CODE_JOB]
rl_arms = sorted(a for a, e in arms_man.items() if e.get("job_id") == RL_JOB)
if len(code_arms) != 1:
    nc(f"expected 1 arm with job {CODE_JOB}, found {code_arms}")
if len(rl_arms) != 4:
    nc(f"expected 4 arms with job {RL_JOB}, found {rl_arms}")
code_arm = code_arms[0]
for a in [code_arm] + rl_arms:
    if a not in vec["arms"]:
        nc(f"arm {a} not in vectors.json")

pidx = vec["problem_indices"]


def arm_map(a):
    v = vec["arms"][a]
    if len(v) != len(pidx):
        nc(f"arm {a} length {len(v)} != problem_indices {len(pidx)}")
    m = {}
    for p, x in zip(pidx, v):
        if x is None:
            continue  # missing entry -> problem missing from this arm
        m[p] = int(x)
    return m


code = arm_map(code_arm)
rl = [arm_map(a) for a in rl_arms]
subj = {r["problem_index"]: r["subject"] for r in pp}

# cross-check: subject in per_problem vs unique_id path in vectors.json (diagnostic only)
mism = 0
for p, uid in zip(pidx, vec.get("unique_ids", [])):
    if p in subj and isinstance(uid, str) and uid.count("/") >= 2:
        if uid.split("/")[1] != subj[p]:
            mism += 1

A = {norm(s) for s in GROUP_A}
B = {norm(s) for s in GROUP_B}
present = set(subj.values())
for s in A | B:
    if s not in present:
        nc(f"subject {s} not present in per_problem.json subjects {sorted(present)}")

rows = []
for p in pidx:
    if p not in code or any(p not in r for r in rl) or p not in subj:
        continue
    s = subj[p]
    g = "A" if s in A else ("B" if s in B else None)
    if g is None:
        continue
    rlv = [r[p] for r in rl]
    d = code[p] - sum(rlv) / 4.0
    rows.append({"problem_index": p, "subject": s, "group": g, "code": code[p],
                 "rl": rlv, "d": d})

dA = [r["d"] for r in rows if r["group"] == "A"]
dB = [r["d"] for r in rows if r["group"] == "B"]
if not dA or not dB:
    nc("empty group after the join")
S = sum(dA) / len(dA) - sum(dB) / len(dB)


def subj_mean(names):
    ms = []
    for s in names:
        ds = [r["d"] for r in rows if r["subject"] == norm(s)]
        ms.append(sum(ds) / len(ds))
    return sum(ms) / len(ms)


alt = subj_mean(GROUP_A) - subj_mean(GROUP_B)

print(f"diag: code_arm={code_arm} rl_arms={rl_arms} nA={len(dA)} nB={len(dB)} "
      f"subject/unique_id mismatches={mism}")
out({"measured": S, "refuted_by_met": bool(S < -0.01), "alt_measured": alt,
     "not_computable": None, "example_row": rows[0]})
