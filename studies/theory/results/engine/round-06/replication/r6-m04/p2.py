"""k=2: f = ln(M(sft025_cue)/M(base_cue)) / ln(M(sft1_cue)/M(base_cue)), M = median n_generated of finished rows."""
import json
import math
import os

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

ROOT = "studies/rlneurons/results/wsp1/screen100"
ARMS = ["base_cue", "sft025_cue", "sft1_cue"]


def load(arm):
    path = os.path.join(ROOT, f"{arm}-01", "per_problem.json")
    with open(path) as fh:
        rows = json.load(fh)
    first = {}
    for r in rows:
        pi = r.get("problem_index")
        if pi is None:
            continue
        if pi not in first:  # keep first row per problem_index
            first[pi] = r
    return first


def median(vals):
    vals = sorted(vals)
    n = len(vals)
    if n == 0:
        return None
    if n % 2:
        return float(vals[n // 2])
    return (vals[n // 2 - 1] + vals[n // 2]) / 2.0


def finished(r):
    return r.get("cap_hit") is False and r.get("n_generated") is not None


def M(rows):
    return median([r["n_generated"] for r in rows if finished(r)])


def f_of(mb, m025, m1):
    """None when f is undefined (counts as refuted by the recipe)."""
    if mb is None or m025 is None or m1 is None or mb <= 0 or m025 <= 0 or m1 <= 0:
        return None
    if m1 <= mb:
        return None
    return math.log(m025 / mb) / math.log(m1 / mb)


def stat_main(sample):
    # sample: list of (base_row, sft025_row, sft1_row); cap-hit/missing excluded per arm independently
    v = f_of(M([t[0] for t in sample]), M([t[1] for t in sample]), M([t[2] for t in sample]))
    return -math.inf if v is None else v


def stat_alt(sample):
    # alt: keep only problems finished (cap_hit false, n_generated present) in all three arms
    keep = [t for t in sample if all(finished(r) for r in t)]
    v = f_of(M([t[0] for t in keep]), M([t[1] for t in keep]), M([t[2] for t in keep]))
    return None if v is None else v


def main():
    try:
        data = {a: load(a) for a in ARMS}
    except (OSError, ValueError) as e:
        not_computable(f"cannot read per_problem.json: {e}")
        return
    for a in ARMS:
        for r in data[a].values():
            if "cap_hit" not in r or "n_generated" not in r:
                if "cap_hit" not in r:
                    not_computable(f"{a}: row without cap_hit field")
                    return
    common = sorted(set(data[ARMS[0]]) & set(data[ARMS[1]]) & set(data[ARMS[2]]))
    if not common:
        refuted_without_number()
        return
    problems = [tuple(data[a][pi] for a in ARMS) for pi in common]

    mb, m025, m1 = (M([t[i] for t in problems]) for i in range(3))
    f = f_of(mb, m025, m1)
    if f is None:
        # recipe: M(sft1_cue) <= M(base_cue) -> f undefined, counts as refuted
        refuted_without_number()
        return

    interval = bootstrap(stat_main, problems)
    # undefined resamples are mapped to -inf (they count as refuted); an infinite endpoint is reported as None
    interval = [None if (x is None or math.isinf(x)) else x for x in interval]

    alt = stat_alt(problems)

    report(f, len(common), interval, "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=problems[0][0])


main()
