"""duel-r5-m03 p2: mean cued-base solve rate (attempt-0 rows) on top8-plain quick finished-wrong problems.

Main: select top8 rows score_v3 == 0, cap_hit False, n_generated <= 2000 (missing score_v3 dropped,
each problem_index once); per problem k/m over rows.jsonl rows with attempt == 0 (m = number of rows,
k = number with score_v3 == 1); drop m == 0; mean of k/m.
alt_measured: same, but each sample scored by its final attempt (after restarts) instead of attempt 0.
"""
import json
import os
from collections import defaultdict

TOP8 = "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
BASE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))


def main():
    for p in (TOP8, BASE):
        if not os.path.exists(p):
            out(None, False, None, f"file not found: {p}", None)
            return
    top8 = json.load(open(TOP8))
    base_rows = [json.loads(l) for l in open(BASE) if l.strip()]
    for f in ("problem_index", "attempt", "score_v3", "sample"):
        if not any(f in r for r in base_rows):
            out(None, False, None, f"field {f} missing in {BASE}", None)
            return
    for f in ("problem_index", "score_v3", "cap_hit", "n_generated"):
        if not any(f in r for r in top8):
            out(None, False, None, f"field {f} missing in {TOP8}", None)
            return

    seen = set()
    sel = []
    sel_rows = {}
    for r in top8:
        s = r.get("score_v3")
        if s is None:
            continue
        ng = r.get("n_generated")
        if s == 0 and r.get("cap_hit") is False and ng is not None and ng <= 2000:
            pi = r["problem_index"]
            if pi in seen:
                continue
            seen.add(pi)
            sel.append(pi)
            sel_rows[pi] = r

    a0 = defaultdict(list)
    by_ps = defaultdict(list)
    for r in base_rows:
        by_ps[(r["problem_index"], r.get("sample"))].append(r)
        if r.get("attempt") == 0:
            a0[r["problem_index"]].append(r)

    rates, rates_alt, used = [], [], []
    for pi in sel:
        rs = a0.get(pi, [])
        m = len(rs)
        if m == 0:
            continue
        k = sum(1 for r in rs if r.get("score_v3") == 1)
        rates.append(k / m)
        used.append(pi)
        ka = 0
        for r0 in rs:
            chain = by_ps[(pi, r0.get("sample"))]
            last = max(chain, key=lambda x: (x.get("attempt") if x.get("attempt") is not None else -1))
            if last.get("score_v3") == 1:
                ka += 1
        rates_alt.append(ka / m)

    if not rates:
        out(None, False, None, "no selected problem with m > 0 (empty group)", None)
        return
    measured = sum(rates) / len(rates)
    alt = sum(rates_alt) / len(rates_alt)
    ex = dict(sel_rows[used[0]])
    ex["_base_attempt0_rows"] = a0[used[0]]
    out(measured, False, alt, None, ex)


main()
