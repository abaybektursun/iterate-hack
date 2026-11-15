"""Check of the turn-2 reading, not a recipe of the round: median mean_logprob on the problems that all five cells
finished (cued base, plain base, steps 100, 400, 2,800; MATH-500, T 0.6 / top-p 0.95, sample 0), and the median n_new
of the finished answers in each cell over all its finished rows."""
import json
import math
import statistics

from common import cap_hit, first_sample0

names = {"cued_base": "r3_base-01_out_F_math500.jsonl", "plain_base": "r3_base-01_out_P_math500.jsonl",
         "step100": "r3_s0400_s0100-01_out_s0100_P_math500.jsonl", "step400": "r3_s0400_s0100-01_out_s0400_P_math500.jsonl",
         "step2800": "r3_s2800-01_out_P_math500.jsonl"}
rows = {k: first_sample0(v) for k, v in names.items()}
ok = lambda r: not cap_hit(r) and r.get("mean_logprob") is not None and math.isfinite(r["mean_logprob"])
common = sorted(set.intersection(*[{p for p, r in rs.items() if ok(r)} for rs in rows.values()]))
print(json.dumps({"n_problems_finished_by_all": len(common),
                  "median_mean_logprob_matched": {k: statistics.median(rows[k][p]["mean_logprob"] for p in common) for k in names},
                  "median_n_new_finished": {k: statistics.median(r["n_new"] for r in rs.values() if ok(r)) for k, rs in rows.items()}}))
