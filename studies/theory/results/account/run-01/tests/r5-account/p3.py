"""p3: share of the MATH-500 RL-only gap problems assigned to the reliability part (first-rule assignment R1..R4)."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

PART = "reliability"
PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
D = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
E = "studies/rlneurons/results/day1_3/math500_rl-01/rows.jsonl"
SUBS = ("format", "final line", "garbled", "rejected", "changed")


def is_true(v):
    return v is True or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 1)


def is_false(v):
    return v is False or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 0)


def load_jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def first_att0(rows):
    """First row in file order per (problem_index, sample), among attempt == 0 rows with sample in 0-3."""
    out = {}
    for r in rows:
        if r.get("attempt") != 0 or r.get("sample") not in (0, 1, 2, 3):
            continue
        key = (r.get("problem_index"), r.get("sample"))
        if key not in out:
            out[key] = r
    return out


def k_right(first, pi, cap_wrong=True):
    k = 0
    for s in range(4):
        r = first.get((pi, s))
        if r is None:
            continue  # missing sample: not right
        if cap_wrong and r.get("cap_hit") is True:
            continue  # cap-hit row: not right
        if r.get("score_v3") == 1:
            k += 1
    return k


def ft_match(row):
    ft = row.get("failure_type")
    if not isinstance(ft, str):
        return False
    ft = ft.lower()
    return any(s in ft for s in SUBS)


def assign(row, kB, kR):
    if row.get("t1_cap_hit") is True:
        return "budget"
    if ft_match(row):
        return "answer-statement"
    if kB >= 1:
        return "reliability"
    if kB == 0 and kR >= 2:
        return "capability"
    return "unassigned"


def main():
    for p in (PP, D, E):
        if not os.path.exists(p):
            return not_computable(f"file not readable: {p}")
    with open(PP) as f:
        pp = json.load(f)
    fD, fE = first_att0(load_jsonl(D)), first_att0(load_jsonl(E))
    gap = [r for r in pp if "t1_right" in r and "t2_right" in r and is_true(r["t2_right"]) and is_false(r["t1_right"])]
    if not gap:
        return not_computable("no gap problems (t2_right true, t1_right false) in per_problem.json; share is 0/0")
    # one entry per gap problem: (per_problem row, kB, kR) under the main reading (cap-hit rows count as not right)
    entries = [(r, k_right(fD, r["problem_index"]), k_right(fE, r["problem_index"])) for r in gap]

    def stat(sample):
        return sum(assign(r, kB, kR) == PART for r, kB, kR in sample) / len(sample)

    measured = stat(entries)
    # alt reading: a cap-hit row with stored score_v3 == 1 counts as right in kB / kR
    alt_entries = [(r, k_right(fD, r["problem_index"], False), k_right(fE, r["problem_index"], False)) for r in gap]
    alt = stat(alt_entries)
    refuted = measured < 0.42 or measured > 0.60
    ex = next((r for r, kB, kR in entries if assign(r, kB, kR) == PART), entries[0][0])
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=refuted,
           alt_measured=alt, example_row=ex)


main()
