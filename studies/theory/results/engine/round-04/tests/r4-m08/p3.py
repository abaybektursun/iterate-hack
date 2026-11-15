"""r4-m08 prediction 3: MATH-500 cued base, median per-token entropy of short right answers / long right answers."""
import json
import os

CHECKS = "studies/rlneurons/results/rln5/map-01/checks.json"
PER_PROBLEM = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    if n % 2:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def main():
    for p in (CHECKS, PER_PROBLEM):
        if not os.path.exists(p):
            out(None, False, None, f"{p} not found", None)
            return
    t1 = json.load(open(CHECKS))["per_row"]["T1"]
    pp = {r["problem_index"]: r for r in json.load(open(PER_PROBLEM))}

    short, long_ = [], []
    ex = None
    for row in t1:
        if row["n_own"] == 0:
            continue
        e = row["sum_entropy_own"] / row["n_own"]
        p = pp.get(row["problem_index"])
        if p is None:
            continue
        if not (p["t1_right"] in (True, 1) and p["t1_cap_hit"] is False):
            continue
        if p["t1_generated_tokens"] <= 2000:
            short.append(e)
        else:
            long_.append(e)
        if ex is None:
            ex = {"checks_T1": row, "per_problem": p, "e": e}

    if not short or not long_:
        out(None, False, None, f"empty group (short {len(short)}, long {len(long_)})", None)
        return
    ml = median(long_)
    if ml == 0:
        out(None, False, None, "median long entropy is 0", None)
        return
    stat = median(short) / ml
    out(stat, stat >= 1.0, None, None, ex)


if __name__ == "__main__":
    main()
