"""p3: among problems Think-SFT cue (wsp1 full500 sft1_cue) gets right and the cued base's T1 gets wrong, the fraction
where T1 is a cap hit."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

T1 = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
SFT = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"


def is_true(v):
    return v is True or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 1)


def first_by_index(rows):
    out = {}
    for r in rows:
        pi = r.get("problem_index")
        if pi is not None and pi not in out:
            out[pi] = r
    return out


def b_right(t, cap_counts_as_right=False):
    return is_true(t["t1_right"]) and (cap_counts_as_right or t.get("t1_cap_hit") is not True)


def o_right(s, cap_counts_as_right=False):
    return s.get("score_v3") == 1 and (cap_counts_as_right or s.get("cap_hit") is not True)


def make_stat(cap_counts_as_right):
    def stat(sample):
        gap = [(t, s) for t, s in sample if o_right(s, cap_counts_as_right) and not b_right(t, cap_counts_as_right)]
        if not gap:
            return 0.0  # empty gap in a resample (bootstrap only; the main number is checked below)
        return sum(1 for t, _ in gap if t.get("t1_cap_hit") is True) / len(gap)
    return stat


def main():
    for f in (T1, SFT):
        if not os.path.exists(f):
            return not_computable(f"{f} not readable")
    t1 = first_by_index(json.load(open(T1)))
    sft = first_by_index(json.load(open(SFT)))
    pairs = [(t1[pi], sft[pi]) for pi in sorted(set(t1) & set(sft))
             if t1[pi].get("t1_right") is not None and sft[pi].get("score_v3") is not None]
    gap = [(t, s) for t, s in pairs if o_right(s) and not b_right(t)]
    if not gap:
        return not_computable("gap is empty: no problem with Think-SFT cue right and T1 not right")
    stat = make_stat(False)
    measured = stat(pairs)
    alt = make_stat(True)(pairs)
    ex = {"t1": gap[0][0], "sft1_cue": gap[0][1]}
    report(measured, len(gap), bootstrap(stat, pairs), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=ex)


if __name__ == "__main__":
    main()
