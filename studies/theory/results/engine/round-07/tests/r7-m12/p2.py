"""r7-m12 prediction 2: matched-minus-unmatched subject contrast of the per-problem gain of the
base-written-examples arm (job abaybektursun-1114-183855-e840) over the mean of base_cue_s0-s3 on MATH-500."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

AXIS = "studies/rlneurons/results/axis/math500-01"
VEC = os.path.join(AXIS, "vectors.json")
MAN = os.path.join(AXIS, "manifest.json")
PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
JOB = "abaybektursun-1114-183855-e840"
B_ARMS = ["base_cue_s0", "base_cue_s1", "base_cue_s2", "base_cue_s3"]
EXAMPLES = (0, 1, 2)


def main():
    for f in (VEC, MAN, PP):
        if not os.path.exists(f):
            return not_computable(f"file missing: {f}")
    vec = json.load(open(VEC))
    man = json.load(open(MAN))
    pp = json.load(open(PP))

    cands = [k for k, a in man["arms"].items() if a.get("job_id") == JOB]
    if len(cands) != 1:
        return not_computable(f"no unique manifest arm with job id {JOB}: {cands}")
    e_arm = cands[0]
    for a in [e_arm] + B_ARMS:
        if a not in vec["arms"]:
            return not_computable(f"arm {a} not in vectors.json")

    pis = vec["problem_indices"]
    uids = vec.get("unique_ids", [None] * len(pis))
    subj = {row["problem_index"]: row["subject"] for row in pp}
    if any(i not in subj for i in EXAMPLES):
        return not_computable("an example problem (0, 1, 2) is absent from per_problem.json")
    M = {subj[i] for i in EXAMPLES}

    rows = []
    for j, pi in enumerate(pis):
        if pi in EXAMPLES:
            continue
        vals = {}
        ok = True
        for a in [e_arm] + B_ARMS:
            v = vec["arms"][a]
            x = v[j] if j < len(v) else None
            if x is None:
                ok = False
                break
            vals[a] = x
        if not ok or pi not in subj:
            continue
        b = sum(vals[a] for a in B_ARMS) / 4.0
        rows.append({"problem_index": pi, "unique_id": uids[j], "subject": subj[pi],
                     "matched": subj[pi] in M, "E": vals[e_arm],
                     **{a: vals[a] for a in B_ARMS}, "b": b, "g": vals[e_arm] - b})

    def stat(sample):
        m = [r["g"] for r in sample if r["matched"]]
        u = [r["g"] for r in sample if not r["matched"]]
        if not m or not u:
            return float("nan")
        return sum(m) / len(m) - sum(u) / len(u)

    def alt_stat(sample):
        # Other reading: each subject weighted equally (mean of per-subject mean gains) within each side.
        by = {}
        for r in sample:
            by.setdefault(r["subject"], []).append(r["g"])
        m = [sum(v) / len(v) for s, v in by.items() if s in M]
        u = [sum(v) / len(v) for s, v in by.items() if s not in M]
        if not m or not u:
            return float("nan")
        return sum(m) / len(m) - sum(u) / len(u)

    n_m = sum(r["matched"] for r in rows)
    n_u = len(rows) - n_m
    if n_m == 0 or n_u == 0:
        return not_computable("matched or unmatched group is empty")
    print(json.dumps({"groups": {"matched (" + ",".join(sorted(M)) + ")": n_m, "unmatched": n_u}}))
    S = stat(rows)
    report(S, min(n_m, n_u), bootstrap(stat, rows), "bootstrap", refuted_by_met=(S > 0.045 or S < -0.045),
           alt_measured=alt_stat(rows), example_row=rows[0])


main()
