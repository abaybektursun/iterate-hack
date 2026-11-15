"""r4-m10 rival turn 2, test 6, recomputed from the recipe alone: (med_step400 - med_cued_base) / (med_step2800 - med_cued_base)
of mean_logprob over finished answers, MATH-500, T 0.6 / top-p 0.95, sample 0, problems present in all three files.
Bootstrap: the three files resampled independently, 2,000 resamples, seed 0, percentile 90 %."""
import importlib
import json
import statistics

from common import first_sample0

p4 = importlib.import_module("r4-m10_turn2_p4")
names = {"cued_base": "r3_base-01_out_F_math500.jsonl", "step400": "r3_s0400_s0100-01_out_s0400_P_math500.jsonl",
         "step2800": "r3_s2800-01_out_P_math500.jsonl", "step100": "r3_s0400_s0100-01_out_s0100_P_math500.jsonl",
         "plain_base": "r3_base-01_out_P_math500.jsonl"}
rows = {k: first_sample0(v) for k, v in names.items()}
keys = sorted(set(rows["cued_base"]) & set(rows["step400"]) & set(rows["step2800"]))
lp = {k: p4.finished_lp(rows[k], keys) for k in names}


def pos(r, m, e):
    mr, mm, me = statistics.median(r), statistics.median(m), statistics.median(e)
    return (mm - mr) / (me - mr)


print(json.dumps({"value": pos(lp["cued_base"], lp["step400"], lp["step2800"]), "n_common": len(keys),
                  "n_finished": {k: len(v) for k, v in lp.items()},
                  "median_mean_logprob": {k: statistics.median(v) for k, v in lp.items()},
                  "interval_90": p4.boot(pos, [lp["cued_base"], lp["step400"], lp["step2800"]]),
                  "note": "step100 and plain_base medians are context, not part of the statistic"}))
