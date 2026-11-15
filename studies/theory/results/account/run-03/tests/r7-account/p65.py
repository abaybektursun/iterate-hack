"""p65: of the deliberation-part problems of cell math500-code-T1 (ordered rules R1..R5 as in its share recipe), the fraction
where at least one row of math500_base_cue-01/rows.jsonl with that problem_index, attempt == 0 and sample in {0,1,2,3} (first
row per (problem_index, sample)) has score_v3 == 1 and is not a cap hit. Missing samples do not count.
alt_measured: the same with rows of any attempt (restarts after a cap hit included).
refuted_by: fraction below 0.50."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import Unreadable, assign, build_cell, cap, cue_rows_s0to3, fraction_report, not_computable

ok = lambda r: r.get("score_v3") is not None and r.get("score_v3") == 1 and not cap(r)
try:
    probs, ekind = build_cell("math500-code-T1")
    delib = [p for p in probs if p["gap"] and assign(p, ekind) == "deliberation"]
    counted = [any(ok(r) for r in cue_rows_s0to3(p["pi"])) for p in delib]
    alt_counted = [any(ok(r) for r in cue_rows_s0to3(p["pi"], any_attempt=True)) for p in delib]
except Unreadable as e:
    not_computable(str(e))
    sys.exit(0)

fraction_report(delib, counted, refuted=lambda m: m < 0.50,
                alt=(sum(alt_counted) / len(delib)) if delib else None,
                info={"deliberation_part_problems": len(delib), "counted": sum(counted),
                      "gap_problems": sum(p["gap"] for p in probs)},
                empty_reason="math500-code-T1 has no deliberation-part problems; the fraction is undefined")
