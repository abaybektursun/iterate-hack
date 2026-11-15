"""p64: of the loop-part problems of cell math500-s0400-T06 (gap problems with B cap hit and rule A firing on B's text), the
fraction whose per_problem.json row has t1_right true and t1_cap_hit not true (null or missing: does not count).
refuted_by: fraction below 0.55."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import Unreadable, build_cell, fraction_report, not_computable, rows, rule_a

try:
    probs, _ = build_cell("math500-s0400-T06")
    loop = [p for p in probs if p["gap"] and p["b_cap"] and rule_a(p["text"])]
    pp = {}
    for r in rows("PP"):
        pp.setdefault(r["problem_index"], r)
    counted = []
    for p in loop:
        r = pp.get(p["pi"])
        counted.append(r is not None and r.get("t1_right") is not None and r.get("t1_right") == 1 and r.get("t1_cap_hit") is not True)
except Unreadable as e:
    not_computable(str(e))
    sys.exit(0)

fraction_report(loop, counted, refuted=lambda m: m < 0.55,
                info={"loop_part_problems": len(loop), "counted": sum(counted),
                      "gap_problems": sum(p["gap"] for p in probs)},
                empty_reason="math500-s0400-T06 has no loop-part problems; the fraction is undefined")
