"""cleanneurons Part T readout without the cue positions (laptop, numpy only).

    python3 -m studies.cleanneurons.analysis.transplant_readout <job output dir> <out json>

transplant_curve.py scores every position after the prompt, so the three cue tokens (' line!\\n\\nOkay': prefilled in T1, written by
RL in T2) are among its decisive positions, with 5 to 8 nats each. The scoreboard row already gives the base the cue, so the
question is the difference after it. This script drops the first 3 scored positions of every row, redefines the decisive positions
as the 4 % with the largest KL(RL || base) among the rest (per cell), and recomputes each arm's closure
1 - mean KL(RL || arm) / mean KL(RL || base) from kl.npz. It also reports the share of the original decisive KL that sat on the cue.
"""
import json
import sys

import numpy as np

N_CUE, FRAC = 3, 0.04


def main(run, out):
    m = json.load(open(f"{run}/metrics.json"))
    z = np.load(f"{run}/kl.npz")
    arms = m["arm_order"]
    res = {"source": run, "job_id": m["job_id"], "commit": m["commit"], "n_cue_dropped_per_row": N_CUE, "decisive_fraction": FRAC, "cells": {}, "arms": {a: {} for a in arms}}
    for cell in m["cells"]:
        kl, off, dec0 = z[f"{cell}_kl"].astype(np.float64), z[f"{cell}_offsets"], z[f"{cell}_decisive"]
        assert kl.shape[0] == 1 + len(arms) and off[-1] == kl.shape[1]
        keep = np.ones(kl.shape[1], bool)
        for a in off[:-1]:
            keep[a:a + N_CUE] = False
        base = kl[0]
        thr = np.sort(base[keep])[::-1][int(round(FRAC * keep.sum())) - 1]
        dec = keep & (base >= thr)
        res["cells"][cell] = {"rows": len(off) - 1, "positions_after_cue": int(keep.sum()), "decisive_positions": int(dec.sum()), "smallest_decisive_kl": float(thr),
                              "base_mean_kl_after_cue": float(base[keep].mean()), "base_mean_kl_decisive": float(base[dec].mean()),
                              "share_of_original_decisive_kl_on_cue": float(base[dec0 & ~keep].sum() / base[dec0].sum())}
        for i, a in enumerate(arms, 1):
            res["arms"][a][cell] = {"closure_after_cue": float(1 - kl[i][keep].mean() / base[keep].mean()), "closure_decisive": float(1 - kl[i][dec].mean() / base[dec].mean())}
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res["cells"], indent=1))
    print(f"{'arm':10s} | T1 after-cue decisive | T2 after-cue decisive")
    for a in arms:
        r = res["arms"][a]
        print(f"{a:10s} | {r['T1']['closure_after_cue']:9.3f} {r['T1']['closure_decisive']:8.3f} | {r['T2']['closure_after_cue']:9.3f} {r['T2']['closure_decisive']:8.3f}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
