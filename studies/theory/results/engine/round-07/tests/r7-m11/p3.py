"""r7-m11 prediction 3: among cued-base MATH-500 problems with >= 1 right sample of 4 whose plurality vote is wrong (F), the
share whose winning group has 2 or more members.

Main: a sample joins the first group whose first member m satisfies rln4_lib.agree(m, sample) (first member as first argument).
Alt: the same with agreement in either order (agree(m, s) or agree(s, m)).
"""
import functools
import json
import pathlib

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, refuted_without_number

ROOT = pathlib.Path.cwd()
CUE = ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"


@functools.lru_cache(maxsize=None)
def ag(a, b):
    return bool(R.agree(a, b))


def ag_sym(a, b):
    return ag(a, b) or ag(b, a)


def bearing(r):
    ext = r.get("extracted_v3")
    return r.get("cap_hit") is not True and r.get("finish_reason") != "length" and isinstance(ext, str) and ext.strip() != ""


def classify(samples, f):
    """samples: 4 rows in sample order. Returns (in_F, winner_size)."""
    rows = [r for r in samples if bearing(r)]
    any_right = any(r.get("score_v3") == 1 for r in rows)
    groups = []  # lists of rows; groups[k][0] is the first member
    for r in rows:
        for g in groups:
            if f(g[0]["extracted_v3"], r["extracted_v3"]):
                g.append(r)
                break
        else:
            groups.append([r])
    if not groups:
        return any_right, 0  # no answer-bearing sample: vote wrong (any_right is then False)
    best = max(len(g) for g in groups)
    winner = next(g for g in groups if len(g) == best)  # groups are in order of first-member sample index
    vote_right = winner[0].get("score_v3") == 1
    return (any_right and not vote_right), len(winner)


def main():
    cue = {}
    for line in open(CUE):
        r = json.loads(line)
        if r.get("attempt") != 0 or r.get("sample") not in (0, 1, 2, 3):
            continue
        key = (r["problem_index"], r["sample"])
        if key not in cue:
            cue[key] = r
    problems = sorted(set(p for p, _ in cue))
    entries = [tuple(cue[(p, s)] for s in range(4)) for p in problems if all((p, s) in cue for s in range(4))]

    def counts(sample, f):
        nf = n2 = 0
        for samples in sample:
            in_f, size = classify(samples, f)
            if in_f:
                nf += 1
                n2 += size >= 2
        return n2, nf

    def stat(sample):
        n2, nf = counts(sample, ag)
        return n2 / nf if nf else float("-inf")

    n2, nf = counts(entries, ag)
    if nf == 0:
        refuted_without_number()
        return
    measured = n2 / nf
    s2, sf = counts(entries, ag_sym)
    alt = s2 / sf if sf else None
    ex = next((samples[0] for samples in entries if classify(samples, ag)[0]), None)
    report(measured, nf, bootstrap(stat, entries), "bootstrap", refuted_by_met=measured < 0.28, alt_measured=alt, example_row=ex)


if __name__ == "__main__":
    main()
