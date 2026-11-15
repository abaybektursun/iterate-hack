"""p66: of the budget-part problems of cell math500-code-T1 (gap problems with t1_cap_hit == true and rule A not firing on B's
T1.jsonl text), the fraction where at least one row of math500_base_cue-01/rows.jsonl with that problem_index, attempt == 0 and
sample in {0,1,2,3} (first row per (problem_index, sample)) is a cap hit (cap_hit true, or missing and finish_reason ==
'length'); missing samples are not cap hits.
alt_measured: the same with problems whose B text is missing left out (rule A not evaluable instead of 'not firing').
refuted_by: fraction below 0.45."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import Unreadable, build_cell, cap, cue_rows_s0to3, fraction_report, not_computable, rule_a

try:
    probs, _ = build_cell("math500-code-T1")
    budget = [p for p in probs if p["gap"] and p["b_cap"] and not rule_a(p["text"])]
    counted = [any(cap(r) for r in cue_rows_s0to3(p["pi"])) for p in budget]
    alt_pairs = [(p, c) for p, c in zip(budget, counted) if p["text"] is not None]
except Unreadable as e:
    not_computable(str(e))
    sys.exit(0)

fraction_report(budget, counted, refuted=lambda m: m < 0.45,
                alt=(sum(c for _, c in alt_pairs) / len(alt_pairs)) if alt_pairs else None,
                info={"budget_part_problems": len(budget), "counted": sum(counted),
                      "gap_problems": sum(p["gap"] for p in probs)},
                empty_reason="math500-code-T1 has no budget-part problems; the fraction is undefined")
