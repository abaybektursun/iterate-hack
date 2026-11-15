"""Problem dependence of the early answer text (specs/SPEC_probdep.md): per-token log-probability of each stored base answer's
first tokens under the base with the problem and with an empty problem.

    python -m studies.rlneurons.jobs.probdep_tokens --rows studies/rlneurons/data/wrongstep/base_cue_answer_heads_v1.jsonl.gz [--n 8]

Writes to $OUT_DIR: index.json (problem_index, sample, offset, length, score_v3, cap_hit, n_new), base.npz and noprob.npz
(lp_tok per position) and metrics.json. Fail loud.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import pathlib

import numpy as np
import torch

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--max-tokens", type=int, default=1000)
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
    rows = sorted(map(json.loads, gzip.open(a.rows, "rt")), key=lambda r: (r["problem_index"], r["sample"]))[: a.n]
    repo, _, rev = fz["models"]["base"]
    model = AutoModelForCausalLM.from_pretrained(snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors"]), dtype=torch.bfloat16).cuda().eval()

    def lp_tok(head, ans):
        ids = torch.tensor([head + ans], device="cuda")
        lg = model(ids).logits[0, len(head) - 1: -1].float()                    # row t predicts ans[t]
        return torch.log_softmax(lg, dim=-1).gather(1, torch.tensor(ans, device="cuda")[:, None])[:, 0].cpu().numpy().astype(np.float32)

    lp = {"base": [], "noprob": []}
    index, off = [], 0
    with torch.no_grad():
        for r in rows:
            assert r["prompt_arm"] == "cue" and r["text"].startswith(pre_text), r["problem_index"]
            ans = tok(r["text"][len(pre_text):], add_special_tokens=False)["input_ids"][: a.max_tokens]
            assert len(ans) == a.max_tokens or r["n_new"] < a.max_tokens + len(pre) + 8, (r["problem_index"], r["sample"], len(ans), r["n_new"])
            lp["base"].append(lp_tok(S.render_ids(tok, probs[r["problem_index"]]["problem"]) + pre, ans))
            lp["noprob"].append(lp_tok(S.render_ids(tok, "") + pre, ans))
            index.append({k: r[k] for k in ("problem_index", "sample", "score_v3", "cap_hit", "n_new")} | {"offset": off, "length": len(ans)})
            off += len(ans)
    (out / "index.json").write_text(json.dumps(index) + "\n")
    m = {"status": "done", "rows": a.rows, "answers": len(rows), "positions": off, "max_tokens": a.max_tokens, "model_repo": repo, "model_revision": rev,
         "mean_lp_tok": {}, "job_id": os.environ.get("JOB_ID")}
    for name, parts in lp.items():
        v = np.concatenate(parts)
        assert len(v) == off and np.isfinite(v).all(), name
        np.savez(out / f"{name}.npz", lp_tok=v)
        m["mean_lp_tok"][name] = float(v.mean())
    (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
    print(json.dumps(m))


if __name__ == "__main__":
    main()
