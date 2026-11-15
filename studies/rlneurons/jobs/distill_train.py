"""Self-distillation (specs/SELFDISTILL_2026-11-15.md): LoRA fine-tune of the base model on one arm of
data/selfdistill/arms-v1.json, then the merged bf16 model; or rebuild the merged model from a saved adapter for run_cell.

    bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.distill_train train --arm V
    bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.distill_train merge \
        --train-dir /runs/<train-job-id> --dir /tmp/sd && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model-path /tmp/sd ...

train  Example: the plain prompt of the problem (data/rln4/prompt_ids.json, which run_cell checks its rendering against) and as
       target the stored completion (its first three ids are the opening cue, rln4_lib.encode_answer) plus the stop id; loss on
       the target only. Texts come from the source run's answers.jsonl on the runs Volume (sha256 checked against the arms file,
       each text's sha256 too). LoRA on q, k, v, o, gate, up, down of every layer: W x + (alpha / r) B A x, A Kaiming-uniform,
       B = 0, float32. AdamW, constant lr, no warmup, gradient clip 1.0. Batches by target-token budget: examples in shuffled order
       (random.Random(epoch)) are added to a batch until its target tokens reach --budget; loss = summed NLL / batch target tokens.
       --n k: only the k longest examples (smoke run, worst-case memory).
       Writes $OUT_DIR/adapter.safetensors, train.json (examples, tokens, loss per step, generations of 3 training prompts with
       the plain prompt before and after training, merge statistics against RL - base, merged-model hash); no model directory.
merge  The merged model written from the adapter saved by a train job; asserts its hash equals that job's train.json.

Merge: per target tensor, M = bf16(W + (alpha / r) B A) with stochastic rounding (merge_weights.to_bf16, generator seed 0 on the
GPU, tensors in sorted order within each shard as in merge_weights); every other tensor is copied. Before the real merge, the
same merge with the adapter scaled by 0 must give the base tensor for tensor (asserted). Fail loud: no try/except.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import random
import shutil
import time

import torch
import torch.nn.functional as F
from safetensors import safe_open
from safetensors.torch import load_file, save_file

from studies.rlneurons.jobs import merge_weights as MW
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
TARGETS = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
HP = {"rank": 16, "alpha": 32, "lr": 1e-4, "epochs": 2, "budget": 16384, "betas": (0.9, 0.999), "weight_decay": 0.0, "clip": 1.0,
      "merge_seed": 0}
CHECK_GEN = 3                     # training prompts generated before and after training (greedy)
CHECK_TOKENS = 80


def frozen():
    return json.loads((STUDY / "data" / "rln4" / "frozen4.json").read_text())


def snapshots(fz, with_rl=False):
    from huggingface_hub import snapshot_download
    pat = ["*.json", "*.safetensors"]
    base = snapshot_download(fz["models"]["base"][0], revision=fz["models"]["base"][2], allow_patterns=pat)
    tok = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    rl = snapshot_download(fz["models"]["s2800"][0], revision=fz["models"]["s2800"][2], allow_patterns=pat) if with_rl else None
    return base, tok, rl


class LoRA(torch.nn.Module):
    def __init__(self, base: torch.nn.Linear, r: int, alpha: float):
        super().__init__()
        self.base, self.scale = base, alpha / r
        self.A = torch.nn.Parameter(torch.empty(r, base.in_features, device=base.weight.device, dtype=torch.float32))
        self.B = torch.nn.Parameter(torch.zeros(base.out_features, r, device=base.weight.device, dtype=torch.float32))
        torch.nn.init.kaiming_uniform_(self.A, a=math.sqrt(5))

    def forward(self, x):
        return self.base(x) + ((x.float() @ self.A.T) @ self.B.T * self.scale).to(x.dtype)


def add_lora(model, r, alpha) -> dict:
    mods = {}
    for name, m in list(model.named_modules()):
        for t in TARGETS:
            if hasattr(m, t):
                lo = LoRA(getattr(m, t), r, alpha)
                setattr(m, t, lo)
                mods[f"{name}.{t}"] = lo
    assert len(mods) == 7 * model.config.num_hidden_layers, len(mods)
    return mods


def examples(arm: str, answers: pathlib.Path, tok, fz, n: int | None) -> list:
    spec = json.loads((STUDY / "data" / "selfdistill" / "arms-v1.json").read_text())
    assert hashlib.sha256(answers.read_bytes()).hexdigest() == spec["source"]["sha256"], f"{answers} differs from the arms file's source"
    want = {(e["problem_index"], e["sample"]): e for e in spec["arms"][arm]}
    rows = {}
    for line in answers.read_text().splitlines():
        r = json.loads(line)
        if r["attempt"] == 0 and (r["problem_index"], r["sample"]) in want:
            rows[(r["problem_index"], r["sample"])] = {k: r[k] for k in ("problem_index", "sample", "text", "prompt")}
    assert rows.keys() == want.keys(), "an example of the arm is missing from the source rows"
    problems = json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())
    pids = json.loads((STUDY / "data" / "rln4" / "prompt_ids.json").read_text())
    assert pids["pair"] == fz["template"] == "pair1"
    out = []
    for key, e in sorted(want.items()):
        r, i = rows[key], key[0]
        assert hashlib.sha256(r["text"].encode()).hexdigest() == e["text_sha256"], key
        p = pids["ids"][i]
        assert int(problems[i]["index"]) == i and S.render_ids(tok, problems[i]["problem"]) == p, f"prompt of problem {i} differs"
        assert tok.decode(p, skip_special_tokens=False) == r["prompt"], f"problem {i}: stored prompt is not the plain prompt"
        t = R.encode_answer(tok, r["text"], fz["prefill_text"], fz["prefill_ids"])[0] + [S.STOP_ID]
        assert t[:3] == fz["prefill_ids"], key
        out.append({"problem_index": i, "sample": key[1], "prompt": p, "target": t})
    if n:
        out = sorted(out, key=lambda x: -len(x["target"]))[:n]
    return out


def batches(exs: list, epoch: int, budget: int) -> list:
    order = list(range(len(exs)))
    random.Random(epoch).shuffle(order)
    out, cur, k = [], [], 0
    for j in order:
        cur.append(j)
        k += len(exs[j]["target"])
        if k >= budget:
            out.append(cur)
            cur, k = [], 0
    if cur:
        out.append(cur)
    return out


def nll(model, ex) -> torch.Tensor:
    ids = torch.tensor(ex["prompt"] + ex["target"], device="cuda")[None]
    P = len(ex["prompt"])
    h = model.model(input_ids=ids).last_hidden_state[0, P - 1: -1]
    return F.cross_entropy(model.lm_head(h).float(), ids[0, P:], reduction="sum")


@torch.no_grad()
def generate(model, tok, exs) -> list:
    model.eval()
    out = []
    for ex in exs[:CHECK_GEN]:
        ids = torch.tensor(ex["prompt"], device="cuda")[None]
        g = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=CHECK_TOKENS, do_sample=False)[0, ids.shape[1]:]
        text = tok.decode(g.tolist(), skip_special_tokens=False)
        out.append({"problem_index": ex["problem_index"], "text": text, "starts_with_cue": text.startswith(frozen()["prefill_text"])})
    return out


def merge(base_dir, lora: dict, mult: float, out_dir=None, rl_dir=None, json_dir=None) -> dict:
    """lora: {module name: (A, B)} float32. Writes the merged model to out_dir (None: nothing written). mult 0 must give the base:
    asserted. Returns the hash of the merged tensors and, with rl_dir, statistics per tensor group of the float32 LoRA difference D
    and the merged difference M - W: relative norm, changed entries, cosine with RL - base, effective scale <M - W, D> / ||D||^2."""
    base_dir = pathlib.Path(base_dir)
    wmap = json.loads((base_dir / "model.safetensors.index.json").read_text())["weight_map"]
    gen = torch.Generator("cuda").manual_seed(HP["merge_seed"])
    h, per, g, used = hashlib.sha256(), {}, {}, set()
    if out_dir:
        pathlib.Path(out_dir).mkdir(parents=True)
    for shard in sorted(set(wmap.values())):
        written = {}
        with safe_open(base_dir / shard, "pt", device="cpu") as fb:
            fr = safe_open(pathlib.Path(rl_dir) / shard, "pt", device="cpu") if rl_dir else None
            for name in sorted(n for n, s in wmap.items() if s == shard):
                tb = fb.get_tensor(name)
                key = name.removesuffix(".weight")
                if key not in lora:
                    m = tb.cuda()
                else:
                    used.add(key)
                    A, B = (x.cuda() for x in lora[key])
                    b = tb.cuda().float()
                    d = mult * (HP["alpha"] / HP["rank"]) * (B @ A)
                    m = MW.to_bf16(b + d, "stochastic", gen)
                    if mult == 0:
                        assert torch.equal(m, tb.cuda()), f"{name}: the zero adapter changed the tensor"
                    if fr is not None:
                        mb, r = m.float() - b, fr.get_tensor(name).cuda().float() - b
                        per[name] = MW.tensor_stats(b, mb)
                        x = g.setdefault(MW.group(name), {"d_sq": 0.0, "mb_sq": 0.0, "r_sq": 0.0, "base_sq": 0.0, "d_r": 0.0, "mb_r": 0.0, "mb_d": 0.0})
                        for k, v in (("d_sq", d * d), ("mb_sq", mb * mb), ("r_sq", r * r), ("base_sq", b * b), ("d_r", d * r), ("mb_r", mb * r), ("mb_d", mb * d)):
                            x[k] += float(v.sum())
                h.update(name.encode())
                h.update(m.cpu().view(torch.int16).numpy().tobytes())
                if out_dir:
                    written[name] = m.cpu()
        if out_dir:
            save_file(written, pathlib.Path(out_dir) / shard, metadata={"format": "pt"})
    assert used == set(lora), f"{len(set(lora) - used)} adapter modules have no tensor"
    if out_dir:
        for f in pathlib.Path(json_dir).glob("*.json"):
            shutil.copy(f, pathlib.Path(out_dir) / f.name)
    res = {"sha256": h.hexdigest(), "mult": mult}
    if rl_dir:
        tot = {k: sum(x[k] for x in g.values()) for k in next(iter(g.values()))}
        for x in [*g.values(), tot]:
            x.update(rel_norm_lora=(x["d_sq"] / x["base_sq"]) ** 0.5, rel_norm_merged=(x["mb_sq"] / x["base_sq"]) ** 0.5,
                     rel_norm_rl=(x["r_sq"] / x["base_sq"]) ** 0.5, cos_lora_rl=x["d_r"] / (x["d_sq"] * x["r_sq"]) ** 0.5,
                     cos_merged_rl=x["mb_r"] / (x["mb_sq"] * x["r_sq"]) ** 0.5, effective_scale=x["mb_d"] / x["d_sq"])
        res.update(groups=g, all_targets=tot, changed=MW.sums(per, MW.group))
    return res


def train(a):
    t0 = time.time()
    out = pathlib.Path(os.environ["OUT_DIR"])
    fz = frozen()
    base_dir, tok_dir, rl_dir = snapshots(fz, with_rl=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(tok_dir)
    exs = examples(a.arm, pathlib.Path(a.answers), tok, fz, a.n)
    rep = {"arm": a.arm, "hp": HP, "n_examples": len(exs), "commit": a.commit, "job_id": os.environ.get("JOB_ID"),
           "target_tokens": sum(len(e["target"]) for e in exs), "prompt_tokens": sum(len(e["prompt"]) for e in exs),
           "max_sequence": max(len(e["prompt"]) + len(e["target"]) for e in exs), "versions": {"torch": torch.__version__}}
    import transformers
    rep["versions"]["transformers"] = transformers.__version__
    print(json.dumps(rep), flush=True)
    model = AutoModelForCausalLM.from_pretrained(base_dir, dtype=torch.bfloat16, attn_implementation="sdpa").cuda()
    for p in model.parameters():
        p.requires_grad_(False)
    mods = add_lora(model, HP["rank"], HP["alpha"])
    rep["generations_before"] = generate(model, tok, exs)
    params = [p for m in mods.values() for p in (m.A, m.B)]
    rep["lora_params"] = sum(p.numel() for p in params)
    opt = torch.optim.AdamW(params, lr=HP["lr"], betas=HP["betas"], weight_decay=HP["weight_decay"])
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.config.use_cache = False
    model.train()
    steps, t_train = [], time.time()
    for epoch in range(HP["epochs"]):
        for bi, b in enumerate(batches(exs, epoch, HP["budget"])):
            T = sum(len(exs[j]["target"]) for j in b)
            tot = 0.0
            for j in b:
                loss = nll(model, exs[j]) / T
                loss.backward()
                tot += float(loss)
            gn = float(torch.nn.utils.clip_grad_norm_(params, HP["clip"]))
            opt.step()
            opt.zero_grad(set_to_none=True)
            steps.append({"epoch": epoch, "step": len(steps), "examples": len(b), "target_tokens": T, "loss": tot, "grad_norm": gn,
                          "s": time.time() - t_train})
            print(json.dumps(steps[-1]), flush=True)
    rep["steps"] = steps
    rep["train_s"] = time.time() - t_train
    rep["tokens_per_s"] = HP["epochs"] * rep["target_tokens"] / rep["train_s"]
    rep["loss_first_step"], rep["loss_last_step"] = steps[0]["loss"], steps[-1]["loss"]
    rep["loss_epoch_mean"] = [sum(s["loss"] * s["target_tokens"] for s in steps if s["epoch"] == e) /
                              sum(s["target_tokens"] for s in steps if s["epoch"] == e) for e in range(HP["epochs"])]
    model.gradient_checkpointing_disable()
    model.config.use_cache = True
    rep["generations_after"] = generate(model, tok, exs)
    lora = {k: (m.A.detach().float().cpu(), m.B.detach().float().cpu()) for k, m in mods.items()}
    save_file({f"{k}.{n}": t.contiguous() for k, (A, B) in lora.items() for n, t in (("A", A), ("B", B))}, out / "adapter.safetensors")
    del model, opt, mods, params
    torch.cuda.empty_cache()
    rep["zero_adapter"] = merge(base_dir, lora, 0.0)
    rep["merge"] = merge(base_dir, lora, 1.0, None, rl_dir)
    assert rep["merge"]["sha256"] != rep["zero_adapter"]["sha256"], "the merged model equals the base"
    rep["wall_s"] = time.time() - t0
    (out / "train.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({k: rep[k] for k in ("n_examples", "target_tokens", "loss_first_step", "loss_last_step", "loss_epoch_mean", "train_s",
                                          "tokens_per_s")}, indent=1))
    print(json.dumps({g: {k: v[k] for k in ("rel_norm_lora", "rel_norm_merged", "cos_lora_rl", "cos_merged_rl", "effective_scale")}
                      for g, v in [*rep["merge"]["groups"].items(), ("all", rep["merge"]["all_targets"])]}, indent=1))
    print(json.dumps(rep["generations_after"], indent=1))


def rebuild(a):
    td = pathlib.Path(a.train_dir)
    rep = json.loads((td / "train.json").read_text())
    t = load_file(td / "adapter.safetensors")
    lora = {k.removesuffix(".A"): (t[k], t[k.removesuffix(".A") + ".B"]) for k in t if k.endswith(".A")}
    fz = frozen()
    base_dir, _, _ = snapshots(fz)
    from huggingface_hub import snapshot_download
    rl_json = snapshot_download(fz["models"]["s2800"][0], revision=fz["models"]["s2800"][2], allow_patterns=["*.json"])
    t0 = time.time()
    res = merge(base_dir, lora, 1.0, a.dir, None, rl_json)
    assert res["sha256"] == rep["merge"]["sha256"], "the rebuilt model differs from the train job's merged model"
    pathlib.Path(os.environ["OUT_DIR"], "distill_merge.json").write_text(json.dumps({"train_dir": str(td), "train_job": rep["job_id"], "arm": rep["arm"],
                                                                                **res, "seconds": time.time() - t0}, indent=1) + "\n")
    print("merged", rep["arm"], res["sha256"], f"{time.time() - t0:.0f} s")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--arm", required=True, choices=("V", "U", "S"))
    t.add_argument("--answers", default="/runs/abaybektursun-1114-153825-208b/answers.jsonl")
    t.add_argument("--n", type=int, default=None)
    t.add_argument("--commit", required=True)
    m = sub.add_parser("merge")
    m.add_argument("--train-dir", required=True)
    m.add_argument("--dir", required=True)
    a = ap.parse_args()
    train(a) if a.cmd == "train" else rebuild(a)


if __name__ == "__main__":
    main()
