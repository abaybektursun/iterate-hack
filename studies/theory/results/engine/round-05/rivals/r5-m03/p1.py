"""duel-r5-m03 p1: among top8-plain wrong problems, fraction the cued base solves in all 4 attempt-0 samples.

Main: base4 from attempt == 0 rows only (exactly 4 such rows required).
alt_measured: per sample use the final attempt (after restarts) instead of attempt 0;
same population of top8-wrong problems, same 4-sample requirement.
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
    for f in ("problem_index", "score_v3", "cap_hit"):
        if not any(f in r for r in top8):
            out(None, False, None, f"field {f} missing in {TOP8}", None)
            return

    # base: attempt-0 rows per problem
    a0 = defaultdict(list)
    for r in base_rows:
        if r.get("attempt") == 0:
            a0[r["problem_index"]].append(r)
    base4 = {}
    base4_rows = {}
    for pi, rs in a0.items():
        if len(rs) != 4:
            continue  # drop problems without exactly 4 attempt-0 rows
        base4[pi] = all(r.get("score_v3") == 1 for r in rs)
        base4_rows[pi] = rs

    # alt: final attempt per sample (only for problems kept above)
    by_ps = defaultdict(list)
    for r in base_rows:
        by_ps[(r["problem_index"], r.get("sample"))].append(r)
    base4_alt = {}
    for pi, rs in base4_rows.items():
        ok = True
        for r0 in rs:
            chain = by_ps[(pi, r0.get("sample"))]
            last = max(chain, key=lambda x: (x.get("attempt") if x.get("attempt") is not None else -1))
            if last.get("score_v3") != 1:
                ok = False
        base4_alt[pi] = ok

    # top8 wrong: score_v3 == 0 or cap_hit; drop missing score_v3 unless cap hit; each problem once
    seen = set()
    wrong = []
    wrong_rows = {}
    for r in top8:
        pi = r.get("problem_index")
        if pi in seen:
            continue
        seen.add(pi)
        cap = r.get("cap_hit") is True
        s = r.get("score_v3")
        if s is None and not cap:
            continue
        if cap or s == 0:
            wrong.append(pi)
            wrong_rows[pi] = r

    both = [pi for pi in wrong if pi in base4]
    if not both:
        out(None, False, None, "no top8-wrong problem present in both files (empty denominator)", None)
        return
    n_true = sum(1 for pi in both if base4[pi])
    measured = n_true / len(both)
    alt = sum(1 for pi in both if base4_alt[pi]) / len(both)
    ex_pi = next((pi for pi in both if base4[pi]), both[0])
    ex = dict(wrong_rows[ex_pi])
    ex["_base_attempt0_rows"] = base4_rows[ex_pi]
    refuted = False  # refuted_by is null
    out(measured, refuted, alt, None, ex)


main()
