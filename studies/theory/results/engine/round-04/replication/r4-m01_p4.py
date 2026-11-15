"""r4-m01 p4: within K_own and K_rl separately, AUROC of -zlib9 ratio of text[:3000] for cap_hit; statistic = mean of the two.

Keep len(text) >= 3000; drop loop_A true with onset_A_char missing or < 4000. Stored text as is."""
import json
from common import auroc, bootstrap, ratio, rows

out = {}
for f in ("own", "rl"):
    R = rows(f"r4_modal_k-01_k_a_K_{f}.jsonl")
    kept = []
    for r in R:
        if len(r["text"]) < 3000:
            continue
        if r["loop_A"] and (r.get("onset_A_char") is None or r["onset_A_char"] < 4000):
            continue
        kept.append((-ratio(r["text"][:3000], 9), bool(r["cap_hit"])))
    stat = lambda xs: auroc([s for s, _ in xs], [y for _, y in xs])
    out[f] = {"rows_file": len(R), "kept": len(kept), "cap_hits": sum(y for _, y in kept), "auroc": stat(kept),
              "interval_90": bootstrap(kept, stat), "prefix_kind": sorted({r["prefix_kind"] for r in R}),
              "text_start": R[0]["text"][:60], "n_prefix_first": R[0].get("n_prefix")}
    out[f]["_kept"] = kept
a = [out[f]["auroc"] for f in ("own", "rl") if out[f]["auroc"] is not None]
value = sum(a) / len(a)
# bootstrap of the mean: resample each file's rows independently with the same seed stream
import random
rng = random.Random(0)
vals = []
for _ in range(2000):
    per = []
    for f in ("own", "rl"):
        k = out[f]["_kept"]
        s = [k[rng.randrange(len(k))] for _ in k]
        v = auroc([x for x, _ in s], [y for _, y in s])
        if v is not None:
            per.append(v)
    vals.append(sum(per) / len(per))
vals.sort()
for f in out:
    del out[f]["_kept"]
print(json.dumps({"value": value, "interval_90": [vals[100], vals[1899]], **out}))
