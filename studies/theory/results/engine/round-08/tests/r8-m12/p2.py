"""r8-m12 offline prediction 2: median |ln ratio| of lengths of two right attempt-0 answers to the same problem,
on problems with at least one attempt-0 cap hit, base cue hard328."""
import json
import math
import os
import subprocess
from collections import OrderedDict
from itertools import combinations

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

PATH = "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl"


def load(path):
    if not os.path.exists(path):
        try:
            data = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True, check=True).stdout.decode()
            os.makedirs("runs/theory-tests", exist_ok=True)
            path2 = os.path.join("runs/theory-tests", "p2_" + os.path.basename(os.path.dirname(path)) + ".jsonl")
            with open(path2, "w") as f:
                f.write(data)
            path = path2
        except Exception:
            return None
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def is_cap(r):
    if "cap_hit" in r and r["cap_hit"] is not None:
        return bool(r["cap_hit"])
    return r.get("finish_reason") == "length"


def is_right(r):
    return r.get("score_v3") == 1 and not is_cap(r)


def median(xs):
    xs = sorted(xs)
    m = len(xs)
    if m == 0:
        return None
    return xs[m // 2] if m % 2 else (xs[m // 2 - 1] + xs[m // 2]) / 2.0


def pair_ds(lengths):
    return [abs(math.log(max(a, 1) / max(b, 1))) for a, b in combinations(lengths, 2)]


def main():
    rows = load(PATH)
    if rows is None:
        return not_computable("file not readable: " + PATH)
    for r in rows:
        if "n_new" not in r or "problem_index" not in r or "sample" not in r:
            return not_computable("row lacks n_new, problem_index or sample")
    kept = OrderedDict()
    for r in rows:
        if r.get("attempt") != 0:
            continue
        key = (r["problem_index"], r["sample"])
        if key not in kept:
            kept[key] = r
    per_problem = OrderedDict()
    for (p, _s), r in kept.items():
        per_problem.setdefault(p, []).append(r)

    groups = []  # one entry per kept long problem: tuple of right-finish lengths
    example = None
    for p, rs in per_problem.items():
        if not any(is_cap(r) for r in rs):
            continue
        rights = [r for r in rs if is_right(r)]
        if len(rights) < 2:
            continue
        groups.append(tuple(r["n_new"] for r in rights))
        if example is None:
            example = rights[0]

    def stat(sample):
        ds = [d for g in sample for d in pair_ds(g)]
        return median(ds)

    all_ds = [d for g in groups for d in pair_ds(g)]
    if len(all_ds) < 5:
        return refuted_without_number()
    measured = median(all_ds)

    # Other reading: each problem weighted once (median over problems of the problem's median pair d).
    alt = median([median(pair_ds(g)) for g in groups])

    report(measured, len(groups), bootstrap(stat, groups), "bootstrap",
           refuted_by_met=measured < 0.28, alt_measured=alt, example_row=example)


main()
