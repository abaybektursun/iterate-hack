"""p6: fraction of budget-part problems (gap problems with t1_cap_hit true) that the random matched-norm difference
cell (abaybektursun-1114-153047-6429, cue, T 1.0) gets right, first row per problem_index, score_v3 == 1."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
JOB = "abaybektursun-1114-153047-6429"
RC = f"runs/theory-tests/{JOB}/answers.jsonl"


def is_true(v):
    return v is True or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 1)


def is_false(v):
    return v is False or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 0)


def fetch():
    if not os.path.exists(RC):
        os.makedirs(os.path.dirname(RC), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", f"{JOB}/answers.jsonl", RC],
                       check=False, capture_output=True)
    return os.path.exists(RC)


def first_per_problem(path):
    out = {}
    with open(path) as f:
        for l in f:
            if not l.strip():
                continue
            r = json.loads(l)
            out.setdefault(r.get("problem_index"), r)
    return out


def main():
    if not os.path.exists(PP):
        return not_computable(f"file not readable: {PP}")
    if not fetch():
        return not_computable(f"file not readable: iterate-runs:{JOB}/answers.jsonl")
    with open(PP) as f:
        pp = json.load(f)
    rc = first_per_problem(RC)
    budget = [r for r in pp if "t1_right" in r and "t2_right" in r and is_true(r["t2_right"])
              and is_false(r["t1_right"]) and r.get("t1_cap_hit") is True]
    if not budget:
        return not_computable("no budget-part problems; fraction is 0/0")

    def right(row):
        a = rc.get(row["problem_index"])
        return a is not None and a.get("score_v3") == 1  # missing row or null score_v3: wrong; cap hits keep score

    entries = [(r, right(r)) for r in budget]

    def stat(sample):
        return sum(ok for _, ok in sample) / len(sample)

    measured = stat(entries)
    # alt reading: a cap-hit row of the random cell counts as wrong even if its stored score_v3 is 1
    alt_entries = [(r, ok and rc[r["problem_index"]].get("cap_hit") is not True) for r, ok in entries]
    alt = stat(alt_entries)
    refuted = measured > 0.55 or measured < 0.15
    ex = rc.get(budget[0]["problem_index"])
    ex = {k: v for k, v in ex.items() if k not in ("text", "prompt")} if ex else budget[0]
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=refuted,
           alt_measured=alt, example_row=ex)


main()
