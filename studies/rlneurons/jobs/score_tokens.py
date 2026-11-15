"""Reward content test, step 2 (specs/SPEC_reward5_tokens.md): score the same stored answers under several models, token by token.

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.score_tokens --rows /runs/<job>/answers.jsonl --model base=base --model math31=rl
        --model code31=code --model if30=if30 --model random=/tmp/random

  --rows   answers.jsonl of a run_cell job on MATH-500 with the cue; the rows with sample 0 and attempt 0 are scored (500 answers).
  --model  label=source, repeated. source: base or rl (frozen4.json), a key of merge_weights.OTHERS, or a directory that
           merge_weights wrote. Models are loaded one after another with transformers, bf16, on the GPU.

Each answer is scored as the ids  prompt + cue + answer (+ the stop id when the answer finished); the answer ids are the stored
text tokenized again (the fraction of answers whose token count equals the stored n_new is in metrics.json). For every answer
position the job stores, per model: the log-probability of the stored token, the model's most probable token and its
log-probability, and the entropy of the distribution. Writes to $OUT_DIR: index.json (per answer: problem index, offset, length,
score_v3), tokens.npy (the stored token ids), <label>.npz per model, metrics.json. Fail loud: no try/except.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time

import numpy as np
import torch

from studies.rlneurons.jobs.merge_weights import OTHERS
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
CHUNK = 4096


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--model", action="append", required=True)
    ap.add_argument("--n", type=int, default=None, help="the first n answers (smoke runs)")
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

    rows = [json.loads(line) for line in open(a.rows)]
    rows = sorted((r for r in rows if r["sample"] == 0 and r["attempt"] == 0), key=lambda r: r["problem_index"])[: a.n]
    assert a.n or len(rows) == 500, len(rows)
    seqs, index, off, same_len = [], [], 0, 0
    for r in rows:
        assert r["prompt_arm"] == "cue" and r["text"].startswith(pre_text), r["problem_index"]
        ans = tok(r["text"][len(pre_text):], add_special_tokens=False)["input_ids"] + ([] if r["cap_hit"] else [S.STOP_ID])
        same_len += len(ans) == r["n_generated"]
        head = S.render_ids(tok, probs[r["problem_index"]]["problem"]) + pre
        seqs.append((head, ans))
        index.append({"problem_index": r["problem_index"], "offset": off, "length": len(ans), "score_v3": r["score_v3"], "cap_hit": r["cap_hit"]})
        off += len(ans)
    (out / "index.json").write_text(json.dumps(index) + "\n")
    np.save(out / "tokens.npy", np.concatenate([np.asarray(s[1], dtype=np.int32) for s in seqs]))
    m = {"rows": a.rows, "answers": len(rows), "positions": off, "answers_with_stored_token_count": same_len, "models": {}, "job_id": os.environ.get("JOB_ID")}

    for spec in a.model:
        label, src = spec.split("=")
        t0 = time.time()
        if src in ("base", "rl"):
            repo, _, rev = fz["models"]["base" if src == "base" else "s2800"]
            src_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors"])
        elif src in OTHERS:
            repo, rev = OTHERS[src]
            src_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors"])
        else:
            repo, rev, src_dir = None, None, src
            assert pathlib.Path(src, "config.json").exists(), src
        model = AutoModelForCausalLM.from_pretrained(src_dir, dtype=torch.bfloat16).cuda().eval()
        lp_tok, top, lp_top, ent = [], [], [], []
        with torch.no_grad():
            for head, ans in seqs:
                ids = torch.tensor([head + ans], device="cuda")
                logits = model(ids).logits[0, len(head) - 1: -1]                 # row t predicts ans[t]
                tgt = ids[0, len(head):]
                for s in range(0, len(ans), CHUNK):
                    lsm = torch.log_softmax(logits[s: s + CHUNK].float(), dim=-1)
                    lp_tok.append(lsm.gather(1, tgt[s: s + CHUNK, None])[:, 0].cpu())
                    v, i = lsm.max(dim=-1)
                    top.append(i.cpu())
                    lp_top.append(v.cpu())
                    ent.append(-(lsm.exp() * lsm).sum(-1).cpu())
        arr = {"lp_tok": torch.cat(lp_tok).numpy().astype(np.float32), "top": torch.cat(top).numpy().astype(np.int32),
               "lp_top": torch.cat(lp_top).numpy().astype(np.float32), "ent": torch.cat(ent).numpy().astype(np.float32)}
        assert all(len(v) == off for v in arr.values()) and np.isfinite(arr["lp_tok"]).all(), label
        np.savez(out / f"{label}.npz", **arr)
        m["models"][label] = {"source": src, "repo": repo, "revision": rev, "mean_lp_tok": float(arr["lp_tok"].mean()), "seconds": round(time.time() - t0, 1)}
        (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
        print(label, m["models"][label], flush=True)
        del model
        torch.cuda.empty_cache()
    m["status"] = "done"
    (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")


if __name__ == "__main__":
    main()
