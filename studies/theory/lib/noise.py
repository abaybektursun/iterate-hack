"""What every theory test script prints: its number, n, and a 90 % interval of the statistic. Scripts import it:

    from studies.theory.lib.noise import bootstrap, binomial, report, not_computable

    rows = [...]                                  # one entry per problem (a row, or a tuple of rows from paired files)
    def stat(sample): return sum(r["cap_hit"] for r in sample) / len(sample)
    report(stat(rows), len(rows), bootstrap(stat, rows), "bootstrap", refuted_by_met=stat(rows) < 0.2, example_row=rows[0])

round.py parses the last line: a measured value whose 90 % interval overlaps the predicted interval is "within noise".
"""
import json
import math
import random

KINDS = ("bootstrap", "binomial", "none")


def bootstrap(stat, problems, resamples=2000, seed=0):
    """90 % percentile interval of stat(sample) over `resamples` resamples of `problems` with replacement, seed 0."""
    rng = random.Random(seed)
    values = sorted(stat([rng.choice(problems) for _ in problems]) for _ in range(resamples))
    return [values[int(0.05 * resamples)], values[int(0.95 * resamples) - 1]]


def binomial(k, n):
    """90 % Wilson interval of the proportion k / n, for a single count with no per-problem resampling."""
    z, p = 1.6449, k / n
    centre, half = (p + z * z / (2 * n)) / (1 + z * z / n), z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [centre - half, centre + half]


def report(measured, n, interval, kind, refuted_by_met=False, alt_measured=None, example_row=None):
    """Print the result line. kind: "bootstrap", "binomial", or "none" (interval None) when the statistic has no
    resampling unit."""
    assert kind in KINDS and (interval is None) == (kind == "none"), (kind, interval)
    print(json.dumps({"measured": measured, "n": n, "interval": interval, "interval_kind": kind,
                      "refuted_by_met": bool(refuted_by_met), "alt_measured": alt_measured, "not_computable": None,
                      "example_row": example_row}))


def not_computable(reason):
    print(json.dumps({"measured": None, "n": None, "interval": None, "interval_kind": "none", "refuted_by_met": False,
                      "alt_measured": None, "not_computable": reason, "example_row": None}))


def refuted_without_number():
    """The recipe or refuted_by itself says this case refutes without a number (for example an empty group)."""
    print(json.dumps({"measured": None, "n": None, "interval": None, "interval_kind": "none", "refuted_by_met": True,
                      "alt_measured": None, "not_computable": None, "example_row": None}))
