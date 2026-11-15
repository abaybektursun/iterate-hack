"""p4: on the cued base's T1 cap-hit problems, Think-SFT cue right count minus Math-RL (T2) right count (signed)."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

T12 = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
SFT = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"


def is_true(x):
    # JSON true, or the integer 1 the file uses for t1_right / t2_right
    if x is True:
        return True
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == 1


def first_by_index(rows):
    out = {}
    for r in rows:
        if "problem_index" not in r:
            continue
        out.setdefault(r["problem_index"], r)
    return out


def main():
    for p in (T12, SFT):
        if not os.path.exists(p):
            return not_computable(f"file not found: {p}")
    try:
        t12 = json.load(open(T12))
        sft = json.load(open(SFT))
    except Exception as e:  # noqa: BLE001
        return not_computable(f"file not readable: {e}")
    if not isinstance(t12, list) or not isinstance(sft, list):
        return not_computable("per_problem.json is not a list of rows")
    for f in ("problem_index", "t1_cap_hit", "t2_right", "t2_cap_hit"):
        if not any(f in r for r in t12):
            return not_computable(f"field {f} missing from {T12}")
    for f in ("problem_index", "score_v3", "cap_hit"):
        if not any(f in r for r in sft):
            return not_computable(f"field {f} missing from {SFT}")

    t12_by = first_by_index(t12)
    sft_by = first_by_index(sft)
    C = [pi for pi, r in t12_by.items() if r.get("t1_cap_hit") is True]

    def rl_right(r):
        return is_true(r.get("t2_right")) and r.get("t2_cap_hit") is not True

    def sft_right(s):
        if s is None or s.get("score_v3") is None:
            return False
        return s.get("score_v3") == 1 and s.get("cap_hit") is not True

    # alternative reading: right = graded right, cap-hit flags not applied
    def rl_right_alt(r):
        return is_true(r.get("t2_right"))

    def sft_right_alt(s):
        return s is not None and s.get("score_v3") is not None and s.get("score_v3") == 1

    problems = [(t12_by[pi], sft_by.get(pi)) for pi in C]

    def stat(sample):
        return sum(int(sft_right(s)) - int(rl_right(r)) for r, s in sample)

    def stat_alt(sample):
        return sum(int(sft_right_alt(s)) - int(rl_right_alt(r)) for r, s in sample)

    if not problems:
        return not_computable("no problem has t1_cap_hit true")
    measured = stat(problems)
    alt = stat_alt(problems)
    r0, s0 = problems[0]
    report(measured, len(problems), bootstrap(stat, problems), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row={"t1_t2_items": r0, "sft1_cue": s0})


main()
