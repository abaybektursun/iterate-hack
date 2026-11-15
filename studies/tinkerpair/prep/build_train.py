"""Builds data/train_v1.json: the RL training problems, from AI2's RL-Zero-Math prompts (laptop, no model).

    python -m studies.tinkerpair.prep.build_train <train.parquet> [--n 2560] [--seed 0]

<train.parquet> is the one data file of allenai/Dolci-RL-Zero-Math-7B (revision 93b5e498577804a93fb11bfe8821428f8535f2d8).
Duplicated prompts are kept once. A prompt is dropped when a MATH-500 problem or one of the 400 harder problems equals
it after normalisation or shares at least half of its word 8-grams with it (the rule of rlneurons
analysis/rln3_overlap.py, here applied to all 900 test problems). The rest is shuffled with the seed and cut to n.
"""
import argparse
import collections
import hashlib
import json
import random

import pyarrow.parquet as pq

from studies.rlneurons.analysis.rln3_overlap import grams, norm
from studies.tinkerpair.lib import tk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parquet")
    ap.add_argument("--n", type=int, default=2560)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    seen, train = set(), []
    for r in pq.read_table(a.parquet).to_pylist():
        if norm(r["prompt"]) not in seen:
            seen.add(norm(r["prompt"]))
            train.append({"problem": r["prompt"], "answer": r["ground_truth"]})
    idx = collections.defaultdict(set)
    for i, t in enumerate(train):
        for g in grams(t["problem"]):
            idx[g].add(i)
    d = f"{tk.ROOT}/studies/rlneurons/data"
    tests = json.load(open(f"{d}/rln4/math500.json")) + json.load(open(f"{d}/rln3/hard.json"))
    drop = set()
    for it in tests:
        g = grams(it["problem"])
        c = collections.Counter(i for x in g for i in idx.get(x, ()))
        drop |= {i for i, k in c.items() if k / len(g) >= 0.5}
        drop |= {i for i, t in enumerate(train) if norm(t["problem"]) == norm(it["problem"])}
    keep = [t for i, t in enumerate(train) if i not in drop]
    random.Random(a.seed).shuffle(keep)
    out = [{"index": i, **t} for i, t in enumerate(keep[:a.n])]
    path = f"{tk.STUDY}/data/train_v1.json"
    tk.dump(path, out)
    print(json.dumps({"rows_in_parquet_unique": len(train), "dropped_for_overlap": len(drop), "kept": len(keep), "written": len(out),
                      "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()}))


if __name__ == "__main__":
    main()
