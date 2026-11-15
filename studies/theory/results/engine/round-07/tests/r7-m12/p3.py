"""r7-m12 prediction 3: on MATH-500 problems the cued base solved in 0 of base_cue_s0-s3, how many does the
Math-RL-written-examples arm (shots1 draw 1) get right."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

AXIS = "studies/rlneurons/results/axis/math500-01"
VEC = os.path.join(AXIS, "vectors.json")
MAN = os.path.join(AXIS, "manifest.json")
SHOTS_RL = "studies/rlneurons/data/shots1/rl.json"
B_ARMS = ["base_cue_s0", "base_cue_s1", "base_cue_s2", "base_cue_s3"]
EXAMPLES = (0, 1, 2)


def main():
    for f in (VEC, MAN):
        if not os.path.exists(f):
            return not_computable(f"file missing: {f}")
    vec = json.load(open(VEC))
    man = json.load(open(MAN))

    cands = [k for k, a in man["arms"].items()
             if "written by Math-RL" in a.get("what", "") and a.get("prompt") == "cue"
             and "shots1" in a.get("run_folder", "")]
    if len(cands) != 1:
        return not_computable(f"no unique manifest arm for Math-RL-written shots1 examples: {cands}")
    r_arm = cands[0]
    if os.path.exists(SHOTS_RL):
        meta = json.load(open(SHOTS_RL))
        if list(meta.get("problem_indices", [])) != [0, 1, 2]:
            return not_computable(f"shots file problem_indices {meta.get('problem_indices')} != [0, 1, 2]")
    for a in [r_arm] + B_ARMS:
        if a not in vec["arms"]:
            return not_computable(f"arm {a} not in vectors.json")

    pis = vec["problem_indices"]
    uids = vec.get("unique_ids", [None] * len(pis))
    rows = []
    for j, pi in enumerate(pis):
        if pi in EXAMPLES:
            continue
        vals = {}
        ok = True
        for a in [r_arm] + B_ARMS:
            v = vec["arms"][a]
            x = v[j] if j < len(v) else None
            if x is None:
                ok = False
                break
            vals[a] = x
        if not ok:
            continue
        rows.append({"problem_index": pi, "unique_id": uids[j], "R": vals[r_arm],
                     **{a: vals[a] for a in B_ARMS}, "base_sum": sum(vals[a] for a in B_ARMS)})

    def in_z(r):
        return r["base_sum"] == 0

    def stat(sample):
        return sum(1 for r in sample if in_z(r) and r["R"] == 1)

    Z = [r for r in rows if in_z(r)]
    if not Z:
        return not_computable("Z (problems with 0 of 4 base samples right) is empty")
    count = stat(rows)
    print(json.dumps({"groups": {"Z (base 0/4)": len(Z), "kept": len(rows)}}))
    ex = next((r for r in Z if r["R"] == 1), Z[0])
    # Interval: bootstrap over all kept problems (|Z| varies across resamples), statistic = the count.
    report(count, len(Z), bootstrap(stat, rows), "bootstrap", refuted_by_met=count > 9,
           alt_measured=count / len(Z), example_row=ex)


main()
