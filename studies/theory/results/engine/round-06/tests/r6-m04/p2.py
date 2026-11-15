"""r6-m04 prediction 2: f = ln(M(sft025_cue)/M(base_cue)) / ln(M(sft1_cue)/M(base_cue)),
M = median n_generated over kept rows with cap_hit false, on problems present in all three files."""
import json
import math
import os

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

BASE = "studies/rlneurons/results/wsp1/screen100"
ARMS = ["base_cue", "sft025_cue", "sft1_cue"]


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
    for r in rows:
        if not isinstance(r, dict) or "problem_index" not in r:
            continue
        if r["problem_index"] not in kept:
            kept[r["problem_index"]] = r
    return kept, None


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def finished(r):
    # cap_hit false (missing/null cap_hit is not "true", so it is kept as not a cap hit) and n_generated present
    return r.get("cap_hit") is not True and isinstance(r.get("n_generated"), (int, float))


def f_of(Ms):
    mb, m025, m1 = Ms
    if mb is None or m025 is None or m1 is None or mb <= 0 or m025 <= 0 or m1 <= 0:
        return None
    if m1 <= mb:
        return None
    return math.log(m025 / mb) / math.log(m1 / mb)


def stat_main(sample):
    Ms = [median([t[i]["n_generated"] for t in sample if finished(t[i])]) for i in range(3)]
    return f_of(Ms)


def stat_alt(sample):
    # alt: only problems finished in all three arms (paired finished set)
    s = [t for t in sample if all(finished(r) for r in t)]
    Ms = [median([t[i]["n_generated"] for t in s]) for i in range(3)]
    return f_of(Ms)


def numeric(stat):
    # for bootstrap resamples only: an undefined f counts as refuted, so place it at -inf (below any threshold)
    def g(sample):
        v = stat(sample)
        return float("-inf") if v is None else v
    return g


def main():
    data = {}
    for arm in ARMS:
        kept, err = load(arm)
        if err:
            not_computable(err)
            return
        data[arm] = kept
    common = set(data[ARMS[0]]) & set(data[ARMS[1]]) & set(data[ARMS[2]])
    common = sorted(common, key=lambda x: (str(type(x)), x))
    problems = [tuple(data[a][pi] for a in ARMS) for pi in common]
    if not problems:
        refuted_without_number()
        return
    Ms = [median([t[i]["n_generated"] for t in problems if finished(t[i])]) for i in range(3)]
    print("medians of finished n_generated (base, sft025, sft1):", json.dumps(Ms),
          "finished counts:", json.dumps([sum(1 for t in problems if finished(t[i])) for i in range(3)]))
    f = stat_main(problems)
    if f is None:
        refuted_without_number()
        return
    alt = stat_alt(problems)
    example = next(t[1] for t in problems if finished(t[1]))
    report(f, len(problems), bootstrap(numeric(stat_main), problems), "bootstrap", refuted_by_met=f < 0.45,
           alt_measured=alt, example_row=example)


main()
