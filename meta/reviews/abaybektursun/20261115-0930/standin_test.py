# PYTHONPATH=. uv run --no-project --with torch==2.15.0 --with transformers==5.22.2 --with math-verify==0.9.0 --with huggingface_hub python meta/reviews/abaybektursun/20261115-0930/standin_test.py <empty out dir> > meta/reviews/abaybektursun/20261115-0930/standin.txt
"""Run prefix_cell.main at alpha 0 with a stand-in for rln4_gen.VllmEngine (no model, no weights): request k ends with an
answer line + stop id when k is even, and hits the cap when k is odd. Checks rows and metrics against an earlier job's row."""
import json
import os
import pathlib
import sys

import huggingface_hub

from studies.rlneurons.jobs import prefix_cell as P
from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.lib import n13_score as S

real = huggingface_hub.snapshot_download
huggingface_hub.snapshot_download = lambda repo, **kw: "/nonexistent-model" if "safetensors" in str(kw.get("allow_patterns")) else real(repo, **kw)
seen = {}


class StandIn:
    def __init__(self, model_dir, tok_dir, max_len):
        seen["init"] = (model_dir, max_len, os.environ.get("VLLM_USE_FLASHINFER_SAMPLER"))
        self.q, self.k = [], 0
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(tok_dir)

    def add(self, rid, ids, sampling, seed, max_tokens):
        self.q.append((rid, self.k, max_tokens))
        self.k += 1

    def step(self):
        done, self.q = self.q[:3], self.q[3:]
        res = []
        for rid, k, mt in done:
            out = self.tok("\n\nThe answer is $\\boxed{3}$.", add_special_tokens=False)["input_ids"] + [S.STOP_ID] if k % 2 == 0 else \
                (self.tok(" so", add_special_tokens=False)["input_ids"] * mt)[:mt]
            res.append((rid, out, [-0.5] * len(out), "stop" if k % 2 == 0 else "length"))
        return res

    def has_unfinished(self):
        return bool(self.q)


J.VllmEngine = StandIn
out = pathlib.Path(sys.argv[1])
sys.argv = ["prefix_cell", "--rows", "studies/rlneurons/data/wrongstep/base_cue_judged_rows_v1.jsonl", "--labels",
            "studies/rlneurons/results/anatomy/judge-01/labels.json", "--model", "base", "--alpha", "0", "--k", "2", "--cap", "40",
            "--seed", "110000000", "--n-items", "3", "--out", str(out)]
P.main()
rows = [json.loads(l) for l in open(out / "answers.jsonl")]
m = json.loads((out / "metrics.json").read_text())
old = json.loads(open("../iterate-hack-critic/runs/abaybektursun-1114-233600-a2de/answers.jsonl").readline())
print("engine init (model_dir, max_model_len, VLLM_USE_FLASHINFER_SAMPLER):", seen["init"])
print("metrics:", m["status"], m["requests"], m["counts"])
print("rows:", len(rows), [(r["item"], r["k"], r["finish_reason"], r["cap_hit"], r["n_new"], r["score_v3"]) for r in rows])
print("row keys equal to job a2de's:", set(rows[0]) == set(old), sorted(set(rows[0]) ^ set(old)))
