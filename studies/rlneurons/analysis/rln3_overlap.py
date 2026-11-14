"""RLN-3: text overlap of the test problems with the RL training prompts (allenai/Dolci-RL-Zero-Math-7B, train split).

    uv run --no-project --with pyarrow python -I studies/rlneurons/analysis/rln3_overlap.py <dir> <out.json>

<dir> holds train.parquet (the dataset's one data file), math500.json and hard.json (results/rlneurons/r3/inputs/).
A problem is flagged `exact` when its normalised text equals a training prompt, `near` when at least half of its
word 8-grams occur in one training prompt. Normalisation: lower case, runs of non-alphanumerics to one space.
"""
import collections
import json
import re
import sys

import pyarrow.parquet as pq


def norm(s): return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def grams(s, n=8):
    w = norm(s).split()
    return {" ".join(w[i:i + n]) for i in range(max(len(w) - n + 1, 1))}


def main():
    d, out = sys.argv[1], sys.argv[2]
    train = [norm(r["prompt"]) for r in pq.read_table(f"{d}/train.parquet").to_pylist()]
    tset, idx = set(train), collections.defaultdict(set)
    for i, s in enumerate(train):
        for g in grams(s):
            idx[g].add(i)
    res = {"n_train": len(train), "sets": {}}
    for name in ("math500", "hard"):
        flags, count = {}, collections.Counter()
        for it in json.load(open(f"{d}/{name}.json")):
            g = grams(it["problem"])
            c = collections.Counter(i for x in g for i in idx.get(x, ()))
            share = max(c.values()) / len(g) if c else 0.0
            f = "exact" if norm(it["problem"]) in tset else "near" if share >= 0.5 else "none"
            flags[str(it["index"])] = {"flag": f, "share": round(share, 3), "source": it.get("source", name)}
            count[f"{it.get('source', name)}/{f}"] += 1
        res["sets"][name] = {"counts": dict(sorted(count.items())), "flags": flags}
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: v["counts"] for k, v in res["sets"].items()}, indent=1))


if __name__ == "__main__":
    main()
