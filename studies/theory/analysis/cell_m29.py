"""Readout of cell m29 (specs/SPEC_cell_m29.md): base + 2x top-8 RL-Math directions, cue, MATH-500, one sample.

  python3 studies/theory/analysis/cell_m29.py runs/<job-id>/answers.jsonl

Writes studies/theory/results/experiments/cell-m29-01/{metrics,per_problem,examples}.json. The 1.5x cell (same seeds) is read
from studies/rlneurons/results/xreward/dial15_math500-01/rows.jsonl for the paired difference.
"""
import json
import pathlib
import random
import sys

OUT = pathlib.Path("studies/theory/results/experiments/cell-m29-01")
REF = pathlib.Path("studies/rlneurons/results/xreward/dial15_math500-01/rows.jsonl")
B = 10_000


def pct(xs, q):
    xs = sorted(xs)
    return xs[int(q * (len(xs) - 1))]


rows = sorted((json.loads(l) for l in open(sys.argv[1])), key=lambda r: r["problem_index"])
assert [r["problem_index"] for r in rows] == list(range(500)), "need all 500 problems once"
assert all(r["attempt"] == 0 and r["sample"] == 0 for r in rows)
ref = {r["problem_index"]: r["score_v3"] for r in map(json.loads, open(REF))}
assert len(ref) == 500

right = [r["score_v3"] for r in rows]
d = [right[i] - ref[i] for i in range(500)]
rng = random.Random(0)
boot, boot_d = [], []
for _ in range(B):
    s = [rng.randrange(500) for _ in range(500)]
    boot.append(sum(right[i] for i in s))
    boot_d.append(sum(d[i] for i in s))

metrics = {
    "cell": "m29", "n": 500, "right_v3": sum(right), "interval_90": [pct(boot, 0.05), pct(boot, 0.95)],
    "cap_hits": sum(r["cap_hit"] for r in rows),
    "mean_generated_tokens": round(sum(r["n_new"] for r in rows) / 500, 1),
    "no_extracted_answer": sum(not r["extracted_v3"] for r in rows),
    "wrong_finished": sum((not r["cap_hit"]) and r["score_v3"] == 0 for r in rows),
    "vs_1p5x": {"ref": str(REF), "ref_right_v3": sum(ref.values()), "diff": sum(d),
                "interval_90": [pct(boot_d, 0.05), pct(boot_d, 0.95)],
                "right_1p5x_wrong_2x": [i for i in range(500) if d[i] < 0],
                "wrong_1p5x_right_2x": [i for i in range(500) if d[i] > 0]},
    "bootstrap": f"{B} resamples of problems, seed 0, percentile",
}
per_problem = [{k: r[k] for k in ("problem_index", "score_v3", "n_new", "cap_hit", "finish_reason", "extracted_v3", "gold")}
               for r in rows]
keep = ("problem_index", "seed", "prompt", "text", "n_new", "cap_hit", "finish_reason", "extracted_v3", "gold", "score_v3")
examples = {"right": {k: next(r for r in rows if r["score_v3"] == 1)[k] for k in keep},
            "wrong": {k: next(r for r in rows if r["score_v3"] == 0)[k] for k in keep}}

OUT.mkdir(parents=True, exist_ok=True)
for name, obj in (("metrics", metrics), ("per_problem", per_problem), ("examples", examples)):
    (OUT / f"{name}.json").write_text(json.dumps(obj, indent=1) + "\n")
print(json.dumps({k: v for k, v in metrics.items() if k != "vs_1p5x"} | {"vs_1p5x_diff": metrics["vs_1p5x"]["diff"],
                  "vs_1p5x_interval_90": metrics["vs_1p5x"]["interval_90"]}, indent=1))
