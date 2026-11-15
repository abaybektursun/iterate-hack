"""duel-r5-m03 p3: share of top8-plain quick finished-wrong answers with n_generated <= 1000.

Main: select score_v3 == 0, cap_hit False, n_generated <= 2000 (missing score_v3 dropped, each
problem_index once); report (#selected with n_generated <= 1000) / (#selected).
alt_measured: strict thresholds (n_generated < 2000 for selection, < 1000 for "very short").
"""
import json
import os

TOP8 = "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))


def select(top8, lim, strict):
    seen = set()
    sel = []
    for r in top8:
        s = r.get("score_v3")
        if s is None:
            continue
        ng = r.get("n_generated")
        if ng is None:
            continue
        ok_len = ng < lim if strict else ng <= lim
        if s == 0 and r.get("cap_hit") is False and ok_len:
            pi = r["problem_index"]
            if pi in seen:
                continue
            seen.add(pi)
            sel.append(r)
    return sel


def main():
    if not os.path.exists(TOP8):
        out(None, False, None, f"file not found: {TOP8}", None)
        return
    top8 = json.load(open(TOP8))
    for f in ("problem_index", "score_v3", "cap_hit", "n_generated"):
        if not any(f in r for r in top8):
            out(None, False, None, f"field {f} missing in {TOP8}", None)
            return
    sel = select(top8, 2000, False)
    if not sel:
        out(None, False, None, "no selected rows (empty denominator)", None)
        return
    measured = sum(1 for r in sel if r["n_generated"] <= 1000) / len(sel)
    sel_a = select(top8, 2000, True)
    alt = (sum(1 for r in sel_a if r["n_generated"] < 1000) / len(sel_a)) if sel_a else None
    ex = next((r for r in sel if r["n_generated"] <= 1000), sel[0])
    out(measured, False, alt, None, ex)


main()
