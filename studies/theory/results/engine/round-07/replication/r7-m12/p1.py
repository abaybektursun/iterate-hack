"""k=1: subject-confinement gain of shots_rl (Math-RL written examples of MATH-500 0,1,2; shots1 draw 1)
over the mean of the 4 cued-base samples, in-subject minus out-of-subject."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

VEC = "studies/rlneurons/results/axis/math500-01/vectors.json"
MAN = "studies/rlneurons/results/axis/math500-01/manifest.json"
PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
B_ARMS = ["base_cue_s0", "base_cue_s1", "base_cue_s2", "base_cue_s3"]
EXAMPLES = (0, 1, 2)


def main():
    for f in (VEC, MAN, PP):
        if not os.path.exists(f):
            not_computable(f"file missing: {f}")
            return
    vec = json.load(open(VEC))
    man = json.load(open(MAN))
    pp = json.load(open(PP))

    # Arm R: the manifest entry that is the cued base with 3 solved examples written by Math-RL.
    cands = [a for a, m in man["arms"].items()
             if m.get("family") == "shots_rl" or
             ("Math-RL" in m.get("what", "") and "3 solved" in m.get("what", "") and m.get("prompt") == "cue")]
    if len(cands) != 1 or cands[0] not in vec["arms"]:
        not_computable(f"cannot identify a unique Math-RL shots arm in manifest: {cands}")
        return
    R = cands[0]
    for a in B_ARMS:
        if a not in vec["arms"]:
            not_computable(f"arm {a} missing from vectors.json")
            return

    pidx = vec["problem_indices"]
    uids = vec.get("unique_ids")
    subj = {}
    for r in pp:
        subj[r["problem_index"]] = r["subject"]
    if any(i not in subj for i in EXAMPLES):
        not_computable("per_problem.json lacks a subject for example problem 0, 1 or 2")
        return
    M = {subj[i] for i in EXAMPLES}

    # subject from vectors.json unique_ids (alt reading of "subject"), e.g. test/algebra/123.json
    uid_subj = {}
    if uids:
        for j, p in enumerate(pidx):
            parts = str(uids[j]).split("/")
            if len(parts) >= 3:
                uid_subj[p] = parts[1]
    M_uid = {uid_subj.get(i) for i in EXAMPLES}

    rows = []  # one entry per kept problem
    for j, p in enumerate(pidx):
        if p in EXAMPLES:
            continue
        vals = []
        ok = True
        for a in [R] + B_ARMS:
            arr = vec["arms"][a]
            v = arr[j] if j < len(arr) else None
            if v is None:
                ok = False
                break
            vals.append(v)
        if not ok:
            continue
        if p not in subj:
            continue
        r = vals[0]
        b = sum(vals[1:]) / 4.0
        g = r - b
        rows.append({
            "problem_index": p,
            "subject": subj[p],
            "in_M": subj[p] in M,
            "uid_in_M": uid_subj.get(p) in M_uid if uid_subj else None,
            "R": r, "B0": vals[1], "B1": vals[2], "B2": vals[3], "B3": vals[4],
            "g": g,
        })

    def stat(lst):
        ins = [x["g"] for x in lst if x["in_M"]]
        outs = [x["g"] for x in lst if not x["in_M"]]
        if not ins or not outs:
            return float("nan")
        return sum(ins) / len(ins) - sum(outs) / len(outs)

    def stat_uid(lst):
        ins = [x["g"] for x in lst if x["uid_in_M"]]
        outs = [x["g"] for x in lst if x["uid_in_M"] is False]
        if not ins or not outs:
            return None
        return sum(ins) / len(ins) - sum(outs) / len(outs)

    n_in = sum(1 for x in rows if x["in_M"])
    n_out = len(rows) - n_in
    if n_in == 0 or n_out == 0:
        not_computable("one of the subject groups is empty")
        return
    S = stat(rows)
    interval = bootstrap(stat, rows)
    alt = stat_uid(rows) if uid_subj else None

    print(json.dumps({"groups": {"in_example_subjects " + "+".join(sorted(M)): n_in,
                                 "other_subjects": n_out}}))
    ex = next(x for x in rows if x["in_M"])
    report(S, min(n_in, n_out), interval, "bootstrap",
           refuted_by_met=False, alt_measured=alt, example_row=ex)


main()
