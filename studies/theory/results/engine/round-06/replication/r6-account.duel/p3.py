"""k=3: among problems Think-SFT (sft1_cue) gets right and the cued base T1 gets wrong, fraction where T1 is a cap hit."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

T1_PATH = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
SFT_PATH = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"


def load_first(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        rows = json.load(f)
    out = {}
    for r in rows:  # first row in file order wins
        if r.get("problem_index") not in out:
            out[r.get("problem_index")] = r
    return out


def is_true(v):
    return v is True or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 1)


def b_right(t1, use_cap=True):
    return is_true(t1["t1_right"]) and (not is_true(t1.get("t1_cap_hit")) if use_cap else True)


def other_right(s, use_cap=True):
    return s["score_v3"] == 1 and (not is_true(s.get("cap_hit")) if use_cap else True)


def gap_of(sample, use_cap=True):
    return [(t1, s) for t1, s in sample if other_right(s, use_cap) and not b_right(t1, use_cap)]


def stat_with(use_cap):
    def stat(sample):
        g = gap_of(sample, use_cap)
        if not g:
            return 0.0  # empty gap in a resample; see notes
        return sum(1 for t1, _ in g if is_true(t1.get("t1_cap_hit"))) / len(g)
    return stat


def main():
    t1 = load_first(T1_PATH)
    sft = load_first(SFT_PATH)
    if t1 is None or sft is None:
        not_computable("row file missing: " + (T1_PATH if t1 is None else SFT_PATH))
        return
    for name, rows, fields in (("t1_t2_items", t1, ("t1_right", "t1_cap_hit")), ("sft1_cue", sft, ("score_v3", "cap_hit"))):
        for fld in fields:
            if not any(fld in r for r in rows.values()):
                not_computable(f"field {fld} absent in {name}")
                return
    pairs = []
    for pi in t1:  # join on problem_index, t1 file order
        if pi not in sft:
            continue
        a, b = t1[pi], sft[pi]
        if a.get("t1_right") is None or b.get("score_v3") is None:
            continue
        pairs.append((a, b))
    gap = gap_of(pairs, True)
    if not gap:
        not_computable("gap group is empty (no problem with sft1_cue right and T1 not right)")
        return
    stat = stat_with(True)
    measured = stat(pairs)
    gap_alt = gap_of(pairs, False)
    alt = stat_with(False)(pairs) if gap_alt else None
    a, b = gap[0]
    report(measured, len(gap), bootstrap(stat, pairs), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row={"t1_t2_items": a, "sft1_cue": b})


main()
