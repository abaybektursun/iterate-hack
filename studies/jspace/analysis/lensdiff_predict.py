"""Exploratory (not in SPEC1): do per-answer features of the lens readout predict that an answer is wrong, compared with its
length alone? AUROC over the 500 answers of each cell, and over the answers that finished before the token cap.

    PYTHONPATH=. python3 -m studies.jspace.analysis.lensdiff_predict runs/<job-id> <result folder>

Writes predict.json. hold = share of generated positions with a hold-on token in the top K; wrap = the same for the wrap-up
family; holdlp = the best readout log-prob among (" Wait", " wait", " Hmm"); last50 = over the last 50 generated positions;
gap = RL minus base. An AUROC below 0.5 means the feature is lower in wrong answers.
"""
import json
import pathlib
import sys

import numpy as np

from studies.jspace.analysis.lensdiff_analyze import HOLD, ITEMS, WRAP

run, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
items = {int(p["problem_index"]): p for p in json.loads(ITEMS.read_text())}
vocab = json.loads((run / "vocab.json").read_text())
index = json.loads((run / "index.json").read_text())
hold, wrap = [vocab.index(s) for s in HOLD], [vocab.index(s) for s in WRAP]
W = index["watch"]["tokens"]
wi = [W.index(s) for s in (" Wait", " wait", " Hmm")]


def auroc(score, y):
    score, y = np.asarray(score, float), np.asarray(y, bool)
    order = np.argsort(score)
    ranks = np.empty(len(score))
    ranks[order] = np.arange(1, len(score) + 1)
    for v in np.unique(score):                       # average the ranks of ties
        m = score == v
        ranks[m] = ranks[m].mean()
    n1, n0 = y.sum(), (~y).sum()
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


res = {}
for cell, key, capkey in (("T1", "t1_right", "t1_cap_hit"), ("T2", "t2_right", "t2_cap_hit")):
    feats, y, cap = {}, [], []
    for sh in index["shards"]:
        if sh["cell"] != cell:
            continue
        z = np.load(run / sh["file"])
        off = z["offsets"]
        for r, pi in enumerate(z["problem_index"]):
            s = slice(off[r], off[r + 1])
            g = z["kind"][s] == 1
            y.append(not items[int(pi)][key])
            cap.append(items[int(pi)][capkey])
            f = {"length": int(g.sum())}
            for l in index["store_layers"]:
                for m in ("base", "rl"):
                    top = z[f"top_{m}_{l}"][s][g]
                    ph, pw = np.isin(top, hold).any(1), np.isin(top, wrap).any(1)
                    lp = -z[f"watch_{m}_{l}"][s][g][:, wi].astype(float).min(1) / index["qscale"]
                    f.update({f"hold_{m}_L{l}": ph.mean(), f"wrap_{m}_L{l}": pw.mean(), f"hold_last50_{m}_L{l}": ph[-50:].mean(),
                              f"wrap_last50_{m}_L{l}": pw[-50:].mean(), f"holdlp_mean_{m}_L{l}": lp.mean(),
                              f"holdlp_last50_{m}_L{l}": lp[-50:].mean()})
                f[f"hold_gap_L{l}"] = f[f"hold_rl_L{l}"] - f[f"hold_base_L{l}"]
                f[f"holdlp_last50_gap_L{l}"] = f[f"holdlp_last50_rl_L{l}"] - f[f"holdlp_last50_base_L{l}"]
            for k, v in f.items():
                feats.setdefault(k, []).append(v)
    y, fin = np.array(y), ~np.array(cap)
    rows = {k: {"auroc_all": auroc(v, y), "auroc_finished": auroc(np.array(v)[fin], y[fin])} for k, v in feats.items()}
    best = max((k for k in rows if k != "length"), key=lambda k: abs(rows[k]["auroc_all"] - 0.5))
    res[cell] = {"answers": int(len(y)), "wrong": int(y.sum()), "finished": int(fin.sum()), "wrong_finished": int(y[fin].sum()),
                 "length": rows["length"], "best_lens_feature": {"name": best, **rows[best]}, "features": rows}
    print(cell, "length", rows["length"], "| best lens feature", res[cell]["best_lens_feature"])
out.mkdir(parents=True, exist_ok=True)
(out / "predict.json").write_text(json.dumps(res, indent=1))
