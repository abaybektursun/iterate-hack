"""r4-m01 p3: share of problems where the cued base's opening 3,000 characters compress better (zlib 9) than RL step 2,800's
plain opening. base F_math500 vs s2800 P_math500, sample 0, paired by problem_index, both texts >= 3000 characters.

Duplicate problem_index at sample 0 is not addressed by the recipe: first row in file order is used (and counted)."""
import json
from collections import Counter
from common import bootstrap, ratio, rows

def load(name):
    rs = [r for r in rows(name) if r["sample"] == 0]
    dup = sum(c - 1 for c in Counter(r["problem_index"] for r in rs).values())
    out = {}
    for r in rs:
        out.setdefault(r["problem_index"], r)
    return out, dup

B, dupB = load("r3_base-01_out_F_math500.jsonl")
L, dupL = load("r3_s2800-01_out_P_math500.jsonl")
scores = []
for k in sorted(set(B) & set(L)):
    b, l = B[k]["text"], L[k]["text"]
    if len(b) < 3000 or len(l) < 3000:
        continue
    rB, rR = ratio(b[:3000], 9), ratio(l[:3000], 9)
    scores.append(1.0 if rB < rR else 0.5 if rB == rR else 0.0)
mean = lambda xs: sum(xs) / len(xs)
print(json.dumps({"dup_sample0_base": dupB, "dup_sample0_rl": dupL, "common": len(set(B) & set(L)), "kept_pairs": len(scores),
                  "value": mean(scores), "interval_90": bootstrap(scores, mean),
                  "base_text_start": B[0]["text"][:40], "rl_text_start": L[0]["text"][:40],
                  "base_prefill_ids": B[0].get("prefill_ids"), "rl_prefill_ids": L[0].get("prefill_ids")}))
