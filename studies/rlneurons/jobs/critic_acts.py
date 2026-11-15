"""Critic at decoding time, stage 1 (specs/SPEC_critic.md): the base model reads stored samples and stores its residual stream at
fixed points of each answer.

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.critic_acts --rows /runs/<job>/answers.jsonl [--model rl] [--n 13]

  --rows   answers.jsonl of a run_cell job with --samples 4 on MATH-500 with the cue; the attempt-0 rows are read (2,000).
  --model  base (default) or rl (frozen4.json): the model that reads the samples.

Per sample the ids are prompt + cue + the stored text tokenized again, cut after the last checkpoint. Stored at the last prompt
token (checkpoint 0: the position that predicts the first answer token) and after 250, 500, 1,000 and 2,000 answer tokens, for
the samples that long: the output of layers 12, 20, 28 (float16), and the mean log-probability and mean entropy of the answer tokens
so far. Writes to $OUT_DIR: acts.npy [sample, checkpoint, layer, 4096] (zeros where the sample is shorter), feats.npy
[sample, checkpoint, 2], index.json (problem index, sample, n_tokens, score_v3, cap_hit, extracted_v3), metrics.json. Fail loud.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib

import numpy as np
import torch

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
CHECKPOINTS = (0, 250, 500, 1000, 2000)
LAYERS = (12, 20, 28)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--model", default="base", choices=("base", "rl"))
    ap.add_argument("--n", type=int, default=None, help="the first n samples (smoke runs)")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    fz = json.loads((STUDY / "data" / "rln4" / "frozen4.json").read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    probs = {int(p["index"]): p for p in json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())}
    pre, pre_text = fz["prefill_ids"], fz["prefill_text"]
    rows = sorted((r for r in map(json.loads, open(a.rows)) if r["attempt"] == 0), key=lambda r: (r["problem_index"], r["sample"]))[: a.n]
    assert a.n or len(rows) == 2000, len(rows)
    repo, _, rev = fz["models"]["base" if a.model == "base" else "s2800"]
    model = AutoModelForCausalLM.from_pretrained(snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors"]), dtype=torch.bfloat16).cuda().eval()
    assert model.config.num_hidden_layers == 32 and model.config.hidden_size == 4096

    acts = np.zeros((len(rows), len(CHECKPOINTS), len(LAYERS), 4096), dtype=np.float16)
    feats = np.full((len(rows), len(CHECKPOINTS), 2), np.nan, dtype=np.float32)
    index = []
    with torch.no_grad():
        for i, r in enumerate(rows):
            assert r["prompt_arm"] == "cue" and r["text"].startswith(pre_text), r["problem_index"]
            ans = tok(r["text"][len(pre_text):], add_special_tokens=False)["input_ids"]
            head = S.render_ids(tok, probs[r["problem_index"]]["problem"]) + pre
            cut = ans[: CHECKPOINTS[-1]]
            o = model(torch.tensor([head + cut], device="cuda"), output_hidden_states=True)
            lsm = torch.log_softmax(o.logits[0, len(head) - 1: -1].float(), dim=-1) if cut else None      # row t predicts cut[t]
            for c, t in enumerate(CHECKPOINTS):
                if len(ans) < t:
                    break
                p = len(head) - 1 + t                                           # the position that has read t answer tokens
                for li, layer in enumerate(LAYERS):
                    acts[i, c, li] = o.hidden_states[layer][0, p].float().cpu().numpy()
                if t:
                    lp = lsm[:t].gather(1, torch.tensor(cut[:t], device="cuda")[:, None])[:, 0].mean()
                    ent = -(lsm[:t].exp() * lsm[:t]).sum(-1).mean()
                    feats[i, c] = [float(lp), float(ent)]
            index.append({"problem_index": r["problem_index"], "sample": r["sample"], "n_tokens": len(ans), "score_v3": r["score_v3"],
                          "cap_hit": r["cap_hit"], "extracted_v3": r["extracted_v3"]})
    assert np.isfinite(acts).all()
    np.save(out / "acts.npy", acts)
    np.save(out / "feats.npy", feats)
    (out / "index.json").write_text(json.dumps(index) + "\n")
    (out / "metrics.json").write_text(json.dumps({"status": "done", "rows": a.rows, "model": [repo, rev], "samples": len(rows), "checkpoints": CHECKPOINTS,
                                                  "layers": LAYERS, "reached": [int(sum(x["n_tokens"] >= t for x in index)) for t in CHECKPOINTS],
                                                  "job_id": os.environ.get("JOB_ID")}, indent=1) + "\n")


if __name__ == "__main__":
    main()
