"""r4-m10 p3: cap-hit rate, RL step 400 minus base, plain, clean harder 328, T 0.6 / top-p 0.95.

Literal reading: the clean list (rln3_overlap.json, sets.hard.flags, flag == 'none') is keyed by hard.json index;
map index -> unique_id through data/rln3/hard.json and match rows by unique_id.
Alternative: match rows by problem_index == int(index key)."""
import json
from common import ROOT, first_sample0, paired_rate_diff

R = ROOT / "studies/rlneurons"
flags = json.load(open(R / "results/rln3/rln3_overlap.json"))["sets"]["hard"]["flags"]
hard = json.load(open(R / "data/rln3/hard.json"))
clean_idx = {k for k, f in flags.items() if f["flag"] == "none"}
clean_uid = {it["unique_id"] for it in hard if str(it["index"]) in clean_idx}

A = first_sample0("r3_s0400_s0100-01_out_s0400_P_hard.jsonl", key="unique_id")
B = first_sample0("r3_base-01_out_P_hard.jsonl", key="unique_id")
S = sorted(clean_uid & set(A) & set(B))
literal = paired_rate_diff(A, B, S)

Ai = first_sample0("r3_s0400_s0100-01_out_s0400_P_hard.jsonl")
Bi = first_sample0("r3_base-01_out_P_hard.jsonl")
Si = sorted({int(k) for k in clean_idx} & set(Ai) & set(Bi))
alt = paired_rate_diff(Ai, Bi, Si)
same = sorted(Ai[i]["unique_id"] for i in Si) == S
print(json.dumps({"n_clean": len(clean_idx), "literal_unique_id": literal, "alt_problem_index": alt,
                  "same_problem_set": same}))
