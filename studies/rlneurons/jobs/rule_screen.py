"""Screen decoding rules on the base's located wrong steps (specs/SPEC_rulescreen.md): per-token log-probabilities of the judged
finished-wrong base answers under rules that need only the base model.

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.rule_screen --rows /runs/<job>/answers.jsonl --labels studies/rlneurons/results/anatomy/judge-01/labels.json

Writes to $OUT_DIR the files that analysis/wrongstep.py reads: index.json (with wrong_step spans, as score_tokens --labels),
tokens.npy, <rule>.npz with lp_tok per answer position for base, t0.6, noprob, cad0.5, cad1, twice, and metrics.json. Fail loud.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib

import numpy as np
import torch

from studies.rlneurons.jobs.score_tokens import span
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
RULES = ("base", "t0.6", "noprob", "cad0.5", "cad1", "twice")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--n", type=int, default=None)
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
    judged = {(x["problem_index"], x["sample"]): x["passA"] for x in json.loads(pathlib.Path(a.labels).read_text()) if x["kind"] == "base"}
    rows = sorted((r for r in map(json.loads, open(a.rows)) if r["attempt"] == 0 and (r["problem_index"], r["sample"]) in judged),
                  key=lambda r: (r["problem_index"], r["sample"]))[: a.n]
    assert a.n or len(rows) == len(judged), (len(rows), len(judged))
    repo, _, rev = fz["models"]["base"]
    model = AutoModelForCausalLM.from_pretrained(snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors"]), dtype=torch.bfloat16).cuda().eval()

    def logits(head, ans):
        ids = torch.tensor([head + ans], device="cuda")
        return model(ids).logits[0, len(head) - 1: -1].float()                  # row t predicts ans[t]

    lp = {r: [] for r in RULES}
    index, tokens, off = [], [], 0
    with torch.no_grad():
        for r in rows:
            assert r["prompt_arm"] == "cue" and r["text"].startswith(pre_text), r["problem_index"]
            text = r["text"][len(pre_text):]
            enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
            ans = enc["input_ids"] + ([] if r["cap_hit"] else [S.STOP_ID])
            problem = probs[r["problem_index"]]["problem"]
            tgt = torch.tensor(ans, device="cuda")[:, None]
            lg = logits(S.render_ids(tok, problem) + pre, ans)
            lg0 = logits(S.render_ids(tok, "") + pre, ans)
            lg2 = logits(S.render_ids(tok, problem + "\n\nRead the problem again: " + problem) + pre, ans)
            for name, x in (("base", lg), ("t0.6", lg / 0.6), ("noprob", lg0), ("cad0.5", 1.5 * lg - 0.5 * lg0), ("cad1", 2.0 * lg - lg0), ("twice", lg2)):
                lp[name].append(torch.log_softmax(x, dim=-1).gather(1, tgt)[:, 0].cpu().numpy().astype(np.float32))
            index.append({"problem_index": r["problem_index"], "sample": r["sample"], "offset": off, "length": len(ans), "score_v3": r["score_v3"],
                          "cap_hit": r["cap_hit"], "wrong_step": span(judged[(r["problem_index"], r["sample"])], text, enc["offset_mapping"])})
            tokens.append(np.asarray(ans, dtype=np.int32))
            off += len(ans)
    (out / "index.json").write_text(json.dumps(index) + "\n")
    np.save(out / "tokens.npy", np.concatenate(tokens))
    m = {"status": "done", "rows": a.rows, "answers": len(rows), "positions": off, "wrong_steps_found": sum(bool(x["wrong_step"]["found"]) for x in index),
         "models": {}, "job_id": os.environ.get("JOB_ID")}
    for name in RULES:
        v = np.concatenate(lp[name])
        assert len(v) == off and np.isfinite(v).all(), name
        np.savez(out / f"{name}.npz", lp_tok=v)
        m["models"][name] = {"mean_lp_tok": float(v.mean())}
    (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")


if __name__ == "__main__":
    main()
