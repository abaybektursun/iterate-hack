"""p9: fraction of reliability-part problems (gap, t1_cap_hit != true, failure_type matches none of the
answer-statement substrings, kB >= 1) that the random matched-norm difference cell gets right (first row per problem,
score_v3 == 1)."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
D = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
JOB = "abaybektursun-1114-153047-6429"
RC = f"runs/theory-tests/{JOB}/answers.jsonl"
SUBS = ("format", "final line", "garbled", "rejected", "changed")


def is_true(v):
    return v is True or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 1)


def is_false(v):
    return v is False or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 0)


def ft_match(row):
    ft = row.get("failure_type")
    return isinstance(ft, str) and any(s in ft.lower() for s in SUBS)


def fetch():
    if not os.path.exists(RC):
        os.makedirs(os.path.dirname(RC), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", f"{JOB}/answers.jsonl", RC],
                       check=False, capture_output=True)
    return os.path.exists(RC)


def main():
    for p in (PP, D):
        if not os.path.exists(p):
            return not_computable(f"file not readable: {p}")
    if not fetch():
        return not_computable(f"file not readable: iterate-runs:{JOB}/answers.jsonl")
    with open(PP) as f:
        pp = json.load(f)
    first = {}
    with open(D) as f:
        for l in f:
            if not l.strip():
                continue
            r = json.loads(l)
            if r.get("attempt") != 0 or r.get("sample") not in (0, 1, 2, 3):
                continue
            first.setdefault((r.get("problem_index"), r.get("sample")), r)
    rc = {}
    with open(RC) as f:
        for l in f:
            if l.strip():
                r = json.loads(l)
                rc.setdefault(r.get("problem_index"), r)

    def kB(pi, cap_wrong):
        n = 0
        for s in range(4):
            x = first.get((pi, s))
            if x is None or (cap_wrong and x.get("cap_hit") is True):
                continue
            n += x.get("score_v3") == 1
        return n

    def part(cap_wrong):
        return [r for r in pp if "t1_right" in r and "t2_right" in r and is_true(r["t2_right"])
                and is_false(r["t1_right"]) and r.get("t1_cap_hit") is not True and not ft_match(r)
                and kB(r["problem_index"], cap_wrong) >= 1]

    def right(row):
        a = rc.get(row["problem_index"])
        return a is not None and a.get("score_v3") == 1  # missing row or null score_v3: wrong

    def stat(sample):
        return sum(ok for _, ok in sample) / len(sample)

    # main (literal): kB counts score_v3 == 1 rows as stored (this recipe does not say cap hits are wrong)
    main_part = part(False)
    if not main_part:
        return not_computable("no reliability-part problems; fraction is 0/0")
    entries = [(r, right(r)) for r in main_part]
    measured = stat(entries)
    # alt reading: kB as in the account's gap definition, a cap-hit row counts as not right
    alt_part = part(True)
    alt = stat([(r, right(r)) for r in alt_part]) if alt_part else None
    refuted = measured < 0.66
    ex = rc.get(main_part[0]["problem_index"])
    ex = {k: v for k, v in ex.items() if k not in ("text", "prompt")} if ex else main_part[0]
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=refuted,
           alt_measured=alt, example_row=ex)


main()
