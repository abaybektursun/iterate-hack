"""Step 5a: raw cap-hit counts, plain prompt, T 0.6 / top-p 0.95, sample 0 (first row per problem), by checkpoint.
MATH-500 (all 500) and the clean 328 of the harder set (flag == 'none', matched by unique_id via hard.json)."""
import json
from common import ROOT, cap_hit, first_sample0

R = ROOT / "studies/rlneurons"
flags = json.load(open(R / "results/rln3/rln3_overlap.json"))["sets"]["hard"]["flags"]
clean_uid = {it["unique_id"] for it in json.load(open(R / "data/rln3/hard.json")) if flags[str(it["index"])]["flag"] == "none"}
files = {
    "base": ("r3_base-01_out_P_math500.jsonl", "r3_base-01_out_P_hard.jsonl"),
    "s0100": ("r3_s0400_s0100-01_out_s0100_P_math500.jsonl", None),
    "s0400": ("r3_s0400_s0100-01_out_s0400_P_math500.jsonl", "r3_s0400_s0100-01_out_s0400_P_hard.jsonl"),
    "s2800": ("r3_s2800-01_out_P_math500.jsonl", "r3_s2800-01_out_P_hard.jsonl"),
}
out = {}
for m, (fm, fh) in files.items():
    a = first_sample0(fm)
    out[m] = {"math500": {"cap_hits": sum(cap_hit(r) for r in a.values()), "n": len(a)}}
    if fh:
        h = first_sample0(fh, key="unique_id")
        c = [h[u] for u in clean_uid if u in h]
        out[m]["clean328"] = {"cap_hits": sum(cap_hit(r) for r in c), "n": len(c)}
        out[m]["hard400"] = {"cap_hits": sum(cap_hit(r) for r in h.values()), "n": len(h)}
print(json.dumps(out))
