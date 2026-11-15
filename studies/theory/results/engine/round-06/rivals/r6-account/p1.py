"""p1: MATH-500. RL's solve rate on the cued base's T1 cap-hit problems minus the rate expected from RL's rate on
T1 finished-wrong problems with the same 4-sample base count (k4 from the Day-1 #3 base cue rows, attempt 0)."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
ROWS = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"


def is_true(v):
    return v is True or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 1)


def row_cap(r):
    if "cap_hit" in r and r["cap_hit"] is not None:
        return r["cap_hit"] is True
    return r.get("finish_reason") == "length"


def stratum(k):
    return 3 if k >= 3 else k


def make_stat():
    def stat(sample):
        f_n, f_r = {}, {}
        for e in sample:
            if e["group"] == "F":
                f_n[e["stratum"]] = f_n.get(e["stratum"], 0) + 1
                f_r[e["stratum"]] = f_r.get(e["stratum"], 0) + (1 if e["rl"] else 0)
        cs = [e for e in sample if e["group"] == "C" and f_n.get(e["stratum"], 0) > 0]
        if not cs:
            return 0.0  # no C problem left in this resample (bootstrap only; the main number is checked below)
        obs = sum(1 for e in cs if e["rl"]) / len(cs)
        exp = sum(f_r[e["stratum"]] / f_n[e["stratum"]] for e in cs) / len(cs)
        return obs - exp
    return stat


def build(pp, first, cap_counts_as_right):
    """cap_counts_as_right=False: the recipe as written. True: alt reading (a cap hit with a right score counts right
    everywhere: T1-right, RL right and k4)."""
    entries = []
    for p in pp:
        if p.get("t1_right") is None or p.get("t2_right") is None:
            continue
        t1_cap = p.get("t1_cap_hit") is True
        t1_right = is_true(p["t1_right"]) and (cap_counts_as_right or not t1_cap)
        if t1_right:
            continue
        group = "C" if t1_cap else "F"
        rl = is_true(p["t2_right"]) and (cap_counts_as_right or p.get("t2_cap_hit") is not True)
        k4 = 0
        for s in range(4):
            r = first.get((p["problem_index"], s))
            if r is None:
                continue
            if r.get("score_v3") == 1 and (cap_counts_as_right or not row_cap(r)):
                k4 += 1
        entries.append({"problem_index": p["problem_index"], "group": group, "stratum": stratum(k4), "k4": k4,
                        "rl": rl})
    return entries


def main():
    for f in (PP, ROWS):
        if not os.path.exists(f):
            return not_computable(f"{f} not readable")
    pp = json.load(open(PP))
    seen, pp1 = set(), []
    for p in pp:
        if p["problem_index"] in seen:
            continue
        seen.add(p["problem_index"])
        pp1.append(p)
    first = {}
    for line in open(ROWS):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("attempt") != 0:
            continue
        key = (r.get("problem_index"), r.get("sample"))
        if key[1] in (0, 1, 2, 3) and key not in first:
            first[key] = r
    stat = make_stat()
    entries = build(pp1, first, False)
    f_strata = {e["stratum"] for e in entries if e["group"] == "F"}
    cs = [e for e in entries if e["group"] == "C" and e["stratum"] in f_strata]
    if not cs:
        return not_computable("no C problem remains after dropping strata without F problems")
    measured = stat(entries)
    alt_entries = build(pp1, first, True)
    alt = stat(alt_entries)
    ex_p = next(p for p in pp1 if p["problem_index"] == cs[0]["problem_index"])
    ex = {"per_problem": ex_p, "k4": cs[0]["k4"], "group": "C",
          "base_rows": [first.get((ex_p["problem_index"], s)) for s in range(4)]}
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=ex)


if __name__ == "__main__":
    main()
