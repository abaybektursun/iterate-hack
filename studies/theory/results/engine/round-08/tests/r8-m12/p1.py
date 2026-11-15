"""r8-m12 offline prediction 1: Mantel-Haenszel rate ratio of right finishes per 1,000 alive tokens,
late [12000, 16384) vs early [4000, 8000), stratified by problem, base cue hard328, attempt 0."""
import json
import os
import subprocess
from collections import OrderedDict

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

PATH = "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl"
EARLY = (4000, 8000)
LATE = (12000, 16384)


def load(path):
    if not os.path.exists(path):
        try:
            data = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True, check=True).stdout.decode()
            os.makedirs("runs/theory-tests", exist_ok=True)
            path2 = os.path.join("runs/theory-tests", "p1_" + os.path.basename(os.path.dirname(path)) + ".jsonl")
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


def mass(n, a, b):
    return max(0, min(n, b) - a) / 1000.0


def event(r, a, b):
    return 1 if is_right(r) and a <= r["n_new"] < b else 0


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

    strata = []  # (E, ME, L, ML) per problem with M > 0
    example = None
    for p, rs in per_problem.items():
        E = sum(event(r, *EARLY) for r in rs)
        ME = sum(mass(r["n_new"], *EARLY) for r in rs)
        L = sum(event(r, *LATE) for r in rs)
        ML = sum(mass(r["n_new"], *LATE) for r in rs)
        if ME + ML == 0:
            continue
        strata.append((E, ME, L, ML))
        if example is None and L > 0:
            example = next(r for r in rs if event(r, *LATE))

    def parts(sample):
        num = sum(L * ME / (ME + ML) for E, ME, L, ML in sample)
        den = sum(E * ML / (ME + ML) for E, ME, L, ML in sample)
        return num, den

    def stat(sample):
        num, den = parts(sample)
        if den == 0:
            return float("inf")
        return num / den

    if not strata:
        return refuted_without_number()
    num, den = parts(strata)
    if den == 0:
        return refuted_without_number()
    measured = num / den

    # Other reading: the crude pooled (unstratified) rate ratio over the same kept rows, for comparison.
    tE = sum(s[0] for s in strata); tME = sum(s[1] for s in strata)
    tL = sum(s[2] for s in strata); tML = sum(s[3] for s in strata)
    alt = (tL / tML) / (tE / tME) if tML > 0 and tE > 0 and tME > 0 else None

    if example is None:
        example = next(iter(kept.values()))
    report(measured, len(strata), bootstrap(stat, strata), "bootstrap",
           refuted_by_met=measured < 0.5, alt_measured=alt, example_row=example)


main()
