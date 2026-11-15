"""r6-m04 prediction 3: share of pooled sft025_cue + sft05_cue cap-hit rows that fall on problems short for
Think-SFT (sft1_cue n_generated <= median of all kept sft1_cue n_generated, cap hits included)."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

BASE = "studies/rlneurons/results/wsp1/screen100"
ARMS = ["sft1_cue", "sft025_cue", "sft05_cue"]


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


def ng(r):
    v = r.get("n_generated")
    return v if isinstance(v, (int, float)) else None


def cap(r):
    return r is not None and r.get("cap_hit") is True


def parts(sample, per_problem=False):
    """sample: list of (sft1_row, sft025_row or None, sft05_row or None), one per sft1 problem."""
    m = median([ng(t[0]) for t in sample if ng(t[0]) is not None])
    num = den = 0
    for t in sample:
        short = m is not None and ng(t[0]) is not None and ng(t[0]) <= m
        if per_problem:
            c = 1 if (cap(t[1]) or cap(t[2])) else 0
        else:
            c = int(cap(t[1])) + int(cap(t[2]))
        den += c
        num += c if short else 0
    return num, den, m


def make_stat(per_problem):
    def stat(sample):
        num, den, _ = parts(sample, per_problem)
        # undefined (no pooled cap hits) counts as refuted: inf for bootstrap resamples (above any threshold)
        return float("inf") if den == 0 else num / den
    return stat


def main():
    data = {}
    for arm in ARMS:
        kept, err = load(arm)
        if err:
            not_computable(err)
            return
        data[arm] = kept
    keys = sorted(data["sft1_cue"], key=lambda x: (str(type(x)), x))
    problems = [(data["sft1_cue"][pi], data["sft025_cue"].get(pi), data["sft05_cue"].get(pi)) for pi in keys]
    if not problems:
        refuted_without_number()
        return
    num, den, m = parts(problems)
    print("sft1_cue median m:", m, "pooled cap-hit rows:", den, "of which short:", num)
    if den == 0:
        refuted_without_number()
        return
    val = num / den
    anum, aden, _ = parts(problems, per_problem=True)
    alt = anum / aden if aden else None
    example = next(t[1] if cap(t[1]) else t[2] for t in problems if cap(t[1]) or cap(t[2]))
    report(val, len(problems), bootstrap(make_stat(False), problems), "bootstrap", refuted_by_met=val > 0.35,
           alt_measured=alt, example_row=example)


main()
