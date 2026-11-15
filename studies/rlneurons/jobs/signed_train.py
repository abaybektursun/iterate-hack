"""Signed self-training (specs/SPEC_signed1.md): one pass of an advantage-weighted update of the base model on its own stored
samples, arm P or G of data/signed/arms-v1.json (jobs/signed_data.py). LoRA, optimizer, example encoding and merge are those of
jobs/distill_train.py (imported), so the SFT arms V and U of that study are the positives-only control.

    bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.signed_train --arm P --commit <sha>
    then, for a cell: ... -m studies.rlneurons.jobs.distill_train merge --train-dir /runs/<train job> --dir /tmp/sd && ... run_cell --model-path /tmp/sd

One step per problem (its 4 samples), problems in random.Random(0) order, one epoch. Step loss =
sum_i a_i * (NLL_i / tokens_i) / sum_i |a_i|: a sample with positive advantage is made more likely, one with negative advantage
less likely, each by its mean per-token log-probability. --n k: the first k problems of the order (smoke).
Writes $OUT_DIR/adapter.safetensors and train.json (per-step loss and the mean per-token NLL of the positive and of the negative
samples before the step, generations of 3 prompts before and after, merge statistics against RL - base).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import random
import time

import torch
from safetensors.torch import save_file

from studies.rlneurons.jobs import distill_train as DT
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
HP = {**DT.HP, "epochs": 1}


def examples(arm, answers, tok, fz):
    spec = json.loads((STUDY / "data" / "signed" / "arms-v1.json").read_text())
    assert hashlib.sha256(answers.read_bytes()).hexdigest() == spec["source"]["sha256"], f"{answers} differs from the arms file's source"
    want = {(e["problem_index"], e["sample"]): e for e in spec["arms"][arm]}
    pids = json.loads((STUDY / "data" / "rln4" / "prompt_ids.json").read_text())
    by = {}
    for line in answers.read_text().splitlines():
        r = json.loads(line)
        key = (r["problem_index"], r["sample"])
        if r["attempt"] == 0 and key in want:
            assert hashlib.sha256(r["text"].encode()).hexdigest() == want[key]["text_sha256"], key
            p = pids["ids"][key[0]]
            assert tok.decode(p, skip_special_tokens=False) == r["prompt"], f"problem {key[0]}: stored prompt is not the plain prompt"
            t = R.encode_answer(tok, r["text"], fz["prefill_text"], fz["prefill_ids"])[0] + ([] if r["cap_hit"] else [S.STOP_ID])
            by.setdefault(key[0], []).append({"problem_index": key[0], "sample": key[1], "prompt": p, "target": t, "advantage": want[key]["advantage"]})
    assert sum(len(v) for v in by.values()) == len(want)
    order = sorted(by)
    random.Random(0).shuffle(order)
    return [by[i] for i in order]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=("P", "G"))
    ap.add_argument("--answers", default="/runs/abaybektursun-1114-153825-208b/answers.jsonl")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--commit", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = pathlib.Path(os.environ["OUT_DIR"])
    fz = DT.frozen()
    base_dir, tok_dir, rl_dir = DT.snapshots(fz, with_rl=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(tok_dir)
    probs = examples(a.arm, pathlib.Path(a.answers), tok, fz)[: a.n]
    flat = [e for p in probs for e in p]
    rep = {"arm": a.arm, "hp": HP, "n_problems": len(probs), "n_examples": len(flat), "commit": a.commit, "job_id": os.environ.get("JOB_ID"),
           "target_tokens": sum(len(e["target"]) for e in flat), "max_sequence": max(len(e["prompt"]) + len(e["target"]) for e in flat)}
    print(json.dumps(rep), flush=True)
    model = AutoModelForCausalLM.from_pretrained(base_dir, dtype=torch.bfloat16, attn_implementation="sdpa").cuda()
    for p in model.parameters():
        p.requires_grad_(False)
    mods = DT.add_lora(model, HP["rank"], HP["alpha"])
    rep["generations_before"] = DT.generate(model, tok, flat)
    params = [p for m in mods.values() for p in (m.A, m.B)]
    opt = torch.optim.AdamW(params, lr=HP["lr"], betas=HP["betas"], weight_decay=HP["weight_decay"])
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.config.use_cache = False
    model.train()
    steps, t_train = [], time.time()
    for prob in probs:
        z = sum(abs(e["advantage"]) for e in prob)
        tot, pos, neg = 0.0, [], []
        for e in prob:
            mean_nll = DT.nll(model, e) / len(e["target"])
            (e["advantage"] * mean_nll / z).backward()
            tot += e["advantage"] * float(mean_nll) / z
            (pos if e["advantage"] > 0 else neg).append(float(mean_nll))
        gn = float(torch.nn.utils.clip_grad_norm_(params, HP["clip"]))
        opt.step()
        opt.zero_grad(set_to_none=True)
        steps.append({"step": len(steps), "problem_index": prob[0]["problem_index"], "loss": tot, "nll_positive": sum(pos) / len(pos),
                      "nll_negative": sum(neg) / len(neg), "grad_norm": gn, "tokens": sum(len(e["target"]) for e in prob), "s": time.time() - t_train})
        print(json.dumps(steps[-1]), flush=True)
    rep["steps"], rep["train_s"] = steps, time.time() - t_train
    rep["tokens_per_s"] = rep["target_tokens"] / rep["train_s"]
    model.gradient_checkpointing_disable()
    model.config.use_cache = True
    rep["generations_after"] = DT.generate(model, tok, flat)
    lora = {k: (m.A.detach().float().cpu(), m.B.detach().float().cpu()) for k, m in mods.items()}
    save_file({f"{k}.{n}": t.contiguous() for k, (A, B) in lora.items() for n, t in (("A", A), ("B", B))}, out / "adapter.safetensors")
    del model, opt, mods, params
    torch.cuda.empty_cache()
    rep["zero_adapter"] = DT.merge(base_dir, lora, 0.0)
    rep["merge"] = DT.merge(base_dir, lora, 1.0, None, rl_dir)
    assert rep["merge"]["sha256"] != rep["zero_adapter"]["sha256"], "the merged model equals the base"
    rep["wall_s"] = time.time() - t0
    (out / "train.json").write_text(json.dumps(rep, indent=1) + "\n")
    half = len(steps) // 2
    mean = lambda k, s: sum(x[k] for x in s) / max(len(s), 1)
    print(json.dumps({"n_problems": len(probs), "train_s": rep["train_s"], "tokens_per_s": rep["tokens_per_s"],
                      "nll_positive_first_half": mean("nll_positive", steps[:half]), "nll_positive_second_half": mean("nll_positive", steps[half:]),
                      "nll_negative_first_half": mean("nll_negative", steps[:half]), "nll_negative_second_half": mean("nll_negative", steps[half:])}, indent=1))
    print(json.dumps({g: {k: v[k] for k in ("rel_norm_lora", "rel_norm_merged", "cos_lora_rl", "cos_merged_rl", "effective_scale")}
                      for g, v in [*rep["merge"]["groups"].items(), ("all", rep["merge"]["all_targets"])]}, indent=1))
    print(json.dumps(rep["generations_after"], indent=1))


if __name__ == "__main__":
    main()
