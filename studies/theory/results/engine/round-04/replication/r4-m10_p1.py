"""r4-m10 p1: cap-hit rate, RL step 100 minus base, plain MATH-500, T 0.6 / top-p 0.95, paired on problem_index."""
import json
from common import first_sample0, paired_rate_diff

A = first_sample0("r3_s0400_s0100-01_out_s0100_P_math500.jsonl")
B = first_sample0("r3_base-01_out_P_math500.jsonl")
S = sorted(set(A) & set(B))
print(json.dumps({"rows_A": len(A), "rows_B": len(B), **paired_rate_diff(A, B, S)}))
