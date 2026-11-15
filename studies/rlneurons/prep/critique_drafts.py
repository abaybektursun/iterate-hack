"""Drafts for jobs/revise.py (specs/SPEC_critique.md): the stored MATH-500 T 1.0 / top-p 1.0 cue rows, cut to the fields the job reads,
gzipped with a fixed mtime so the sha256 is reproducible.

    python3 studies/rlneurons/prep/critique_drafts.py
    modal volume put iterate-runs runs/critique/<name>.jsonl.gz /inputs/critique/<name>.jsonl.gz

Inputs (not committed): runs/s3/<key> (`aws s3 cp --profile iterate-ecr s3://pg-lineage-769063704696/results/rlneurons/<key> ...`).
"""
import gzip
import hashlib
import json
import pathlib

SRC = {"base_cue_T1": "r4/base_rl-02/out/T1.jsonl",                                     # base + cue, seed 41000000, 410/500 v3
       "rl_cue_T1": "r5/day1_wdiff-01/abaybektursun-1114-153110-e985/answers.jsonl"}  # RL + cue, seed 66000000, 457/500 v3
OUT = pathlib.Path("runs/critique")
OUT.mkdir(parents=True, exist_ok=True)
for name, key in SRC.items():
    rows = [json.loads(line) for line in open(pathlib.Path("runs/s3") / key)]
    assert sorted(r["problem_index"] for r in rows) == list(range(500)), name
    slim = "".join(json.dumps({k: r[k] for k in ("problem_index", "gold", "text", "cap_hit")}) + "\n" for r in sorted(rows, key=lambda r: r["problem_index"]))
    b = gzip.compress(slim.encode(), mtime=0)
    (OUT / f"{name}.jsonl.gz").write_bytes(b)
    print(name, hashlib.sha256(b).hexdigest(), f"{len(b) / 1e6:.2f} MB", sum(r["cap_hit"] for r in rows), "cap hits")
