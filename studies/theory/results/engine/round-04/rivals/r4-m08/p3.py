"""duel-r4-m08 p3: MATH-500 RL per-token entropy, short right answers over long right answers."""
import json
import math
import sys

CHECKS = "studies/rlneurons/results/rln5/map-01/checks.json"
PER_PROBLEM = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
THRESH = 2000


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))
    sys.exit(0)


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    m = n // 2
    return xs[m] if n % 2 else (xs[m - 1] + xs[m]) / 2.0


def num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def main():
    try:
        t2 = json.load(open(CHECKS))["per_row"]["T2"]
        pp = json.load(open(PER_PROBLEM))
    except Exception as e:  # noqa
        out(None, False, None, f"could not read inputs: {e!r}", None)

    by_pi = {}
    for r in pp:
        by_pi.setdefault(r["problem_index"], r)

    def stat(denom_field):
        short, long_, used = [], [], []
        for row in t2:
            n = row.get(denom_field)
            se = row.get("sum_entropy_own")
            if not num(n) or n == 0 or not num(se) or not num(row.get("n_own")) or row.get("n_own") == 0:
                continue
            e = se / n
            p = by_pi.get(row.get("problem_index"))
            if p is None:
                continue
            if not (p.get("t2_right") is True or p.get("t2_right") == 1):
                continue
            if p.get("t2_cap_hit") is not False:
                continue
            L = p.get("t2_generated_tokens")
            if not num(L):
                continue
            (short if L <= THRESH else long_).append(e)
            used.append(row)
        if not short or not long_:
            return None, used, len(short), len(long_)
        ml = median(long_)
        if ml == 0:
            return None, used, len(short), len(long_)
        return median(short) / ml, used, len(short), len(long_)

    measured, used, ns, nl = stat("n_own")
    if measured is None:
        out(None, False, None, f"a group is empty or zero (short={ns}, long={nl})", None)
    alt, _, _, _ = stat("n_gen")  # alt: per-token entropy normalised by n_gen instead of n_own

    sys.stderr.write(f"short={ns} long={nl}\n")
    out(measured, False, alt, None, used[0])


if __name__ == "__main__":
    main()
