"""r4-m10 rival turn 2, test 4, recomputed from the recipe alone: share of RL step-100 plain finished answers whose
mean_logprob is above the median mean_logprob of the cued base's finished answers (MATH-500, T 0.6 / top-p 0.95,
sample 0). Bootstrap: both files resampled independently, 2,000 resamples, seed 0, percentile 90 %."""
import json
import math
import random
import statistics

from common import cap_hit, first_sample0

REF = "r3_base-01_out_F_math500.jsonl"


def finished_lp(rows, keys):
    out = []
    for k in keys:
        r = rows[k]
        lp = r.get("mean_logprob")
        if not cap_hit(r) and lp is not None and math.isfinite(lp):
            out.append(lp)
    return out


def share_above(x, ref):
    m = statistics.median(ref)
    return sum(v > m for v in x) / len(x)


def boot(stat, samples, n=2000, seed=0):
    rng = random.Random(seed)
    vals = sorted(stat(*[[s[rng.randrange(len(s))] for _ in s] for s in samples]) for _ in range(n))
    return [vals[int(0.05 * n)], vals[int(0.95 * n) - 1]]


def run(xname):
    R, X = first_sample0(REF), first_sample0(xname)
    keys = sorted(set(R) & set(X))
    r, x = finished_lp(R, keys), finished_lp(X, keys)
    return {"value": share_above(x, r), "n_common": len(keys), "n_ref_finished": len(r), "n_x_finished": len(x),
            "median_ref": statistics.median(r), "median_x": statistics.median(x),
            "interval_90": boot(share_above, [x, r])}


if __name__ == "__main__":
    print(json.dumps(run("r3_s0400_s0100-01_out_s0100_P_math500.jsonl")))
