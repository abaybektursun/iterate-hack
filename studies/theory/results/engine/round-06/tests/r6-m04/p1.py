"""r6-m04 prediction 1: cap-hit bump D = max(C(sft025_cue), C(sft05_cue)) - max(C(base_cue), C(sft1_cue))."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

BASE = "studies/rlneurons/results/wsp1/screen100"
ARMS = ["base_cue", "sft025_cue", "sft05_cue", "sft1_cue"]
CAP = 16384


def load(arm):
    path = os.path.join(BASE, f"{arm}-01", "per_problem.json")
    if not os.path.exists(path):
        return None, f"{path} not found (committed file missing from checkout)"
    try:
        with open(path) as f:
            rows = json.load(f)
    except Exception as e:  # noqa: BLE001
        return None, f"{path} not readable: {e}"
    if not isinstance(rows, list):
        return None, f"{path} is not a list of rows"
    kept = {}
    for r in rows:  # first row per problem_index, file order
        if not isinstance(r, dict) or "problem_index" not in r:
            continue
        pi = r["problem_index"]
        if pi not in kept:
            kept[pi] = r
    return kept, None


def main():
    data = {}
    for arm in ARMS:
        kept, err = load(arm)
        if err:
            not_computable(err)
            return
        data[arm] = kept

    def is_cap(r):
        return r is not None and r.get("cap_hit") is True  # missing/null -> False

    def is_cap_alt(r):  # alt: cap hit read from the length (n_generated >= 16,384)
        return r is not None and isinstance(r.get("n_generated"), (int, float)) and r["n_generated"] >= CAP

    # One entry per problem in the union of problem_index values; absent problems -> None (add nothing).
    union = sorted(set().union(*[set(data[a]) for a in ARMS]), key=lambda x: (str(type(x)), x))
    problems = [tuple(data[a].get(pi) for a in ARMS) for pi in union]

    def make_stat(cap):
        def stat(sample):
            c = [sum(1 for t in sample if cap(t[i])) for i in range(len(ARMS))]
            cb, c025, c05, c1 = c
            return max(c025, c05) - max(cb, c1)
        return stat

    stat = make_stat(is_cap)
    D = stat(problems)
    alt = make_stat(is_cap_alt)(problems)
    counts = {a: sum(1 for t in problems if is_cap(t[i])) for i, a in enumerate(ARMS)}
    example = next((t[1] for t in problems if is_cap(t[1])), None) or next(t[1] for t in problems if t[1] is not None)
    print("cap-hit counts per arm:", json.dumps(counts))
    report(D, len(problems), bootstrap(stat, problems), "bootstrap", refuted_by_met=D <= 0,
           alt_measured=alt, example_row=example)


main()
