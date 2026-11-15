"""p7: fraction of budget-part problems (gap problems with t1_cap_hit true) where at least one of the 4 attempt-0
base_cue samples in day1_3 math500_base_cue-01 has cap_hit true."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
D = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"


def is_true(v):
    return v is True or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 1)


def is_false(v):
    return v is False or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 0)


def main():
    for p in (PP, D):
        if not os.path.exists(p):
            return not_computable(f"file not readable: {p}")
    with open(PP) as f:
        pp = json.load(f)
    with open(D) as f:
        rows = [json.loads(l) for l in f if l.strip()]
    first = {}
    for r in rows:
        if r.get("attempt") != 0 or r.get("sample") not in (0, 1, 2, 3):
            continue
        first.setdefault((r.get("problem_index"), r.get("sample")), r)
    budget = [r for r in pp if "t1_right" in r and "t2_right" in r and is_true(r["t2_right"])
              and is_false(r["t1_right"]) and r.get("t1_cap_hit") is True]
    if not budget:
        return not_computable("no budget-part problems; fraction is 0/0")

    def counted(pi):
        return any(first.get((pi, s), {}).get("cap_hit") is True for s in range(4))  # missing sample: no cap hit

    def counted_any_attempt(pi):
        return any(r.get("problem_index") == pi and r.get("cap_hit") is True for r in rows)

    entries = [(r, counted(r["problem_index"])) for r in budget]

    def stat(sample):
        return sum(c for _, c in sample) / len(sample)

    measured = stat(entries)
    # alt reading: any row of the problem in the file (all attempts, i.e. restarts too) with cap_hit true
    alt = stat([(r, counted_any_attempt(r["problem_index"])) for r in budget])
    refuted = measured < 0.55
    pi0 = budget[0]["problem_index"]
    ex = next((first[(pi0, s)] for s in range(4) if (pi0, s) in first), budget[0])
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=refuted,
           alt_measured=alt, example_row=ex)


main()
