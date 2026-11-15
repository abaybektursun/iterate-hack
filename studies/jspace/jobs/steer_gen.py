"""J-lens steering during generation (specs/SPEC3_steer.md): the cued base model answers MATH-500 while a fixed vector is added
to the output of one block at every position. Same prompt, cue, sampling, row record and graders as studies/rlneurons run_cell;
the engine is run_cell's vLLM engine built inside this process, so that a forward hook reaches the model.

    uv run tools/gpu.py submit h100 --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.jspace.jobs.steer_gen
        --arms none,steer:hold:L24:0.12,steer:rand:L24:0.12,bias:hold:1 --commit $(git rev-parse HEAD)"
    smoke: add  --n 8 --max-tokens 256

Arms (--arms, comma separated; lib/steer.py):
  none                          no change. The hook still runs and adds a zero vector, so every arm takes the same code path.
  steer:<dir>:L<l>:<alpha>      adds alpha * (median norm of the output of block l) * direction to the output of block l, at
                                every position of the prompt and the answer. dir: hold (lens direction of Wait/Hmm), wrap
                                (end of text, Answer, So), holdwrap (hold minus wrap), neutral (the, so, ...), rand (Gaussian).
  bias:<hold|holdwrap>:<nats>   vLLM logit_bias: +nats on the hold tokens (and -nats on the wrap tokens) of the output logits.
Arms without a vector (none, bias) share one batch; each steer arm runs alone, because the hook adds one vector to every
sequence of a batch. Sample s of problem i has seed --seed + 10000 * s + i in every arm (the same noise in every arm).

Differences from run_cell's engine, each needed for the hook: VLLM_ENABLE_V1_MULTIPROCESSING=0 (the model lives in this process),
enforce_eager (a Python hook is not replayed by a captured CUDA graph), no prefix cache (a cached prompt would keep the
activations of the arm that wrote it).

Before the arms, on --check-n problems and --check-tokens tokens (checks.json; the job fails after writing it if one fails):
  repeat      the arm none twice gives the same token ids.
  steer_acts  alpha 8 along hold at each steered layer changes the tokens of at least all but one problem (an input that
              must change the output: if it does not, the hook does not act on generation).
  bias_acts   a bias of +20 nats on the hold tokens makes them more than half of the generated tokens.
The median norm of each steered block's output is measured in the first `none` check run.

Writes to --out (default $OUT_DIR): answers.jsonl (one row per answer: run_cell's record with grader v3, plus arm and
hold_words; appended with flush + fsync), metrics.json (per-arm counts, rewritten after every row), checks.json, directions.json
(tokens, norms, cosines, linear gains), vectors.pt (the unit directions). --dry-run: run_cell's canned engine, random
directions, no vLLM, no weights, no GPU; checks are computed and not asserted. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import statistics
import time
from importlib import metadata

import torch

from studies.jspace.lib import jlens_read as JL
from studies.jspace.lib import steer as ST
from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.jobs import run_cell as C
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

ENV = {"VLLM_ENABLE_V1_MULTIPROCESSING": "0", **G.ENGINE_ENV}
CHECK_ALPHA, CHECK_BIAS = 8.0, 20.0


class Engine(J.VllmEngine):
    """run_cell's engine (J.VllmEngine) with the three differences of the module docstring and a per-request logit bias."""

    def __init__(self, model_dir, tok_dir, max_model_len):
        wrong = {k: os.environ.get(k) for k, v in ENV.items() if os.environ.get(k) != v}
        assert not wrong, f"the engine environment differs from {ENV}: {wrong}"
        import vllm
        from vllm import EngineArgs, LLMEngine, SamplingParams
        self.SP = SamplingParams
        args = EngineArgs(model=str(model_dir), tokenizer=str(tok_dir), dtype="bfloat16", tensor_parallel_size=1, max_model_len=max_model_len,
                          gpu_memory_utilization=0.90, enable_prefix_caching=False, generation_config="vllm", seed=0,
                          attention_backend=G.ATTENTION_BACKEND, enforce_eager=True)
        self.engine = LLMEngine.from_engine_args(args)
        sc = self.engine.vllm_config.scheduler_config
        self.info = {"vllm": vllm.__version__, "max_num_seqs": sc.max_num_seqs, "max_num_batched_tokens": sc.max_num_batched_tokens,
                     "num_gpu_blocks": getattr(self.engine.vllm_config.cache_config, "num_gpu_blocks", None),
                     "gpu_memory_utilization": 0.90, "max_model_len": max_model_len, "enforce_eager": True, "prefix_caching": False,
                     "in_process": True}

    def add(self, rid, ids, sampling, seed, max_tokens, logit_bias=None):
        sp = self.SP(**{**J.BASE_SAMPLING, **sampling}, max_tokens=max_tokens, seed=seed, logit_bias=logit_bias or None)
        bad = {k: getattr(sp, k) for k, ok in G.NEUTRAL.items() if k != "logit_bias" and hasattr(sp, k) and getattr(sp, k) not in ok}
        assert not bad, f"sampling fields not at their neutral value: {bad}"
        self.engine.add_request(rid, {"prompt_token_ids": ids}, sp)


class Canned(C.Canned):
    def add(self, rid, ids, sampling, seed, max_tokens, logit_bias=None):
        super().add(rid, ids, sampling, seed, max_tokens)


def find_model(root):
    """The vLLM Transformers-backend model of this process (.model is the Hugging Face base model with .layers, .lm_head the
    head), found by walking the attributes of vLLM's objects from the engine. (vLLM freezes the garbage collector's object list
    at start, so gc.get_objects() does not list it.)"""
    seen, queue = set(), [root]
    while queue:
        o = queue.pop(0)
        if id(o) in seen or len(seen) > 200_000:
            continue
        seen.add(id(o))
        if issubclass(type(o), torch.nn.Module):
            if hasattr(o, "lm_head") and hasattr(o, "model") and hasattr(o.model, "layers"):
                return o
            queue.extend(o._modules.values())
        if type(o).__module__.startswith("vllm") and hasattr(o, "__dict__"):
            queue.extend(vars(o).values())
    raise AssertionError(f"no model with .lm_head and .model.layers among {len(seen)} objects reachable from the engine")


class Hook:
    """Adds vec[l] to the output of block l at every forward call; with measure on, keeps the norm of every position's output."""

    def __init__(self, layers, n_layers, d, dev, dtype):
        self.vec = {l: torch.zeros(d, device=dev, dtype=dtype) for l in n_layers}
        self.calls, self.shape, self.measure, self.norms = {l: 0 for l in n_layers}, None, False, {l: [] for l in n_layers}
        self.handles = [layers[l].register_forward_hook(self._hook(l)) for l in n_layers]

    def _hook(self, l):
        def f(_module, _inputs, out):
            h = out[0] if isinstance(out, tuple) else out
            self.calls[l] += 1
            self.shape = tuple(h.shape)
            if self.measure:
                self.norms[l].append(h.float().norm(dim=-1).flatten().cpu())
            h = h + self.vec[l]
            return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
        return f

    def set(self, layer=None, vec=None):
        for v in self.vec.values():
            v.zero_()
        if layer is not None:
            self.vec[layer].copy_(vec.to(self.vec[layer].dtype))
        return {l: float(v.float().norm()) for l, v in self.vec.items()}


def drain(engine):
    """{rid: (token ids, log-probs, finish reason)} of every request in the engine."""
    out = {}
    while engine.has_unfinished():
        for rid, ids, lps, fr in engine.step():
            out[rid] = (ids, lps, fr)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", required=True)
    ap.add_argument("--model", default="base", choices=sorted(C.MODELS))
    ap.add_argument("--n", type=int, default=None, help="the first n problems of the selection")
    ap.add_argument("--every", type=int, default=1, help="keep the problems whose index is a multiple of this")
    ap.add_argument("--pick", default=None, help="comma-separated problem indices: only these (to finish an arm whose job ran out of time)")
    ap.add_argument("--max-tokens", type=int, default=None, help="default: frozen4.json cap (16,384)")
    ap.add_argument("--seed", type=int, default=None, help="default: frozen4.json seeds.T1")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--first-sample", type=int, default=0)
    ap.add_argument("--check-n", type=int, default=8)
    ap.add_argument("--check-tokens", type=int, default=96)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", required=True)
    a = ap.parse_args()
    t0 = time.time()
    assert a.out and re.fullmatch(r"[0-9a-f]{40}", a.commit), "no --out / $OUT_DIR, or --commit is not a full git sha"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows_path, mpath = out / "answers.jsonl", out / "metrics.json"
    assert not rows_path.exists(), f"{rows_path} exists: one fresh directory per run"
    arms = [ST.parse_arm(x) for x in a.arms.split(",")]
    assert len({x["arm"] for x in arms}) == len(arms), "an arm is listed twice"
    steer_layers = sorted({x["layer"] for x in arms if x["kind"] == "steer"})

    fz = json.loads((C.D4 / "frozen4.json").read_text())
    cap, seed0, pre = a.max_tokens or fz["cap"], a.seed if a.seed is not None else fz["seeds"]["T1"], fz["prefill_ids"]
    pick = None if a.pick is None else {int(x) for x in a.pick.split(",")}
    probs = [p for p in C.problems("math500", fz) if int(p["index"]) % a.every == 0 and (pick is None or int(p["index"]) in pick)][: a.n]
    assert probs and (pick is None or len(probs) == len(pick)), "--pick names a problem outside the selection"
    sampling = {"temperature": 1.0, "top_p": 1.0, "repetition_penalty": 1.0}
    versions = {k: metadata.version(k) for k in C.PINS if k != "vllm" or not a.dry_run}
    assert a.dry_run or versions == C.PINS, f"package versions {versions} differ from the study's {C.PINS}: run setup_vllm.sh first"
    repo, _, rev = fz["models"][C.MODELS[a.model]]
    m = {"status": "starting", "config": {**vars(a), "max_tokens": cap, "seed": seed0, "out": str(out), "model_repo": repo, "model_revision": rev,
                                         "tokenizer": fz["tokenizer"], "prefix_ids": pre, "sampling": sampling, "n_problems": len(probs),
                                         "seed_rule": "seed + 10000 * sample + index, the same in every arm", "arms_parsed": arms},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "versions": versions, "started_utc": J.utc(), "arms": {}}

    def write():
        m["updated_utc"] = J.utc()
        G.dump(mpath, m)

    write()
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    assert tok.decode(pre) == fz["prefill_text"]
    pids = [S.render_ids(tok, p["problem"]) for p in probs]
    n13 = json.loads((C.D4 / "prompt_ids.json").read_text())["ids"]
    assert all(ids == n13[int(p["index"])] for p, ids in zip(probs, pids)), "G-TEMPLATE: prompt ids differ from n13's"
    fam = {n: ST.family_ids(tok, n) for n in ST.FAMILIES}
    hold = set(fam["hold"])

    def requests(arm, plist, max_tokens, tag=""):
        return [{"rid": f"{tag}{arm['arm']}|{p['index']}|{s}", "arm": arm["arm"], "cell": f"{a.model}_cue_math500_T1_p1_{arm['arm']}", "bench": "math500",
                 "idx": int(p["index"]), "sample": s, "attempt": 0, "uid": p["unique_id"], "ids": ids + pre, "n_prompt": len(ids),
                 "prefix_ids": pre, "prefix_kind": "opening", "seed": seed0 + 10000 * s + int(p["index"]), "sampling": sampling,
                 "max_tokens": max_tokens, "gold": p["answer"], "logit_bias": ST.bias_map(arm, fam) if arm["kind"] == "bias" else None}
                for s in range(a.first_sample, a.first_sample + a.samples) for p, ids in plist]

    # ---------------------------------------------------------------- engine, model, hook, directions
    live = {}
    t_load = time.time()
    if a.dry_run:
        engine, model_dir, hook, dev = Canned(tok, live), None, None, "cpu"
        g = torch.Generator().manual_seed(0)
        W, Js, lens_meta = torch.randn(len(tok), 16, generator=g), {l: torch.randn(16, 16, generator=g) for l in steer_layers}, {"dry_run": True}
    else:
        model_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
        os.environ.update(ENV)
        engine = Engine(model_dir, tok_dir, 2048 + cap)
        vm = find_model(engine.engine)
        W = vm.lm_head.weight.detach().float().cpu()
        dev, dtype = vm.lm_head.weight.device, vm.lm_head.weight.dtype
        hook = Hook(vm.model.layers, steer_layers, W.shape[1], dev, dtype)
        Js, lens_meta = JL.load_lens(steer_layers, "cpu") if steer_layers else ({}, None)
    dirs = {l: ST.directions(W, Js[l], fam) for l in steer_layers}
    m["engine"] = {**engine.info, "load_s": time.time() - t_load, "model_dir": model_dir, "tok_dir": tok_dir, "lens": lens_meta,
                   "lm_head_shape": list(W.shape)}
    m["status"] = "checks"
    write()

    # ---------------------------------------------------------------- checks and block norms
    cprobs = list(zip(probs, pids))[: a.check_n]
    none = {"arm": "none", "kind": "none"}

    def check_run(arm, tag, vec_layer=None, vec=None, bias=None):
        if hook is not None:
            hook.set(vec_layer, vec)
        for r in requests(arm, cprobs, a.check_tokens, tag):
            live[r["rid"]] = r
            engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"], bias)
        res = drain(engine)
        for rid in res:
            live.pop(rid)
        return [res[r["rid"]][0] for r in requests(arm, cprobs, a.check_tokens, tag)]

    if hook is not None:
        hook.measure = True
    base1 = check_run(none, "c1|")
    if hook is not None:
        hook.measure = False
    base2 = check_run(none, "c2|")
    rnorm = {l: (float(torch.cat(hook.norms[l]).median()) if hook is not None else 1.0) for l in steer_layers}
    share = lambda runs: sum(t in hold for ids in runs for t in ids) / max(1, sum(len(ids) for ids in runs))
    checks = {"n": len(cprobs), "tokens": a.check_tokens,
              "repeat": {"identical": sum(x == y for x, y in zip(base1, base2)), "pass": base1 == base2},
              "hold_token_share_none": share(base1), "steer_acts": {}, "block_norm_median": rnorm,
              "block_norm_positions": {l: (int(torch.cat(hook.norms[l]).numel()) if hook is not None else 0) for l in steer_layers},
              "hook_calls": dict(hook.calls) if hook is not None else None, "hook_hidden_shape": hook.shape if hook is not None else None}
    for l in steer_layers:
        big = check_run(none, f"c3L{l}|", l, CHECK_ALPHA * rnorm[l] * dirs[l]["hold"])
        same = sum(x == y for x, y in zip(base1, big))
        checks["steer_acts"][l] = {"alpha": CHECK_ALPHA, "identical_to_none": same, "hold_token_share": share(big), "pass": same <= 1,
                                   "example": tok.decode(big[0][:48])}
    bias = check_run(none, "c4|", bias={t: CHECK_BIAS for t in fam["hold"]})
    checks["bias_acts"] = {"nats": CHECK_BIAS, "hold_token_share": share(bias), "pass": share(bias) > 0.5, "example": tok.decode(bias[0][:48])}
    checks["pass"] = bool(checks["repeat"]["pass"] and checks["bias_acts"]["pass"] and all(c["pass"] for c in checks["steer_acts"].values()))
    G.dump(out / "checks.json", checks)
    cos = lambda x, y: float(x @ y)
    G.dump(out / "directions.json", {
        "families": {n: {"tokens": list(ST.FAMILIES[n]), "ids": fam[n]} for n in fam}, "rand_seed": ST.RAND_SEED, "block_norm_median": rnorm,
        "layers": {l: {"cosine": {f"{x}|{y}": cos(dirs[l][x], dirs[l][y]) for x in dirs[l] for y in dirs[l] if x < y},
                       "gain_per_unit_step": ST.gains(W, Js[l], fam, dirs[l])} for l in steer_layers},
        "cosine_hold_across_layers": {f"{x}|{y}": cos(dirs[x]["hold"], dirs[y]["hold"]) for x in steer_layers for y in steer_layers if x < y}})
    torch.save({"directions": {l: {n: v.clone() for n, v in dirs[l].items()} for l in steer_layers}, "block_norm_median": rnorm,
                "families": fam}, out / "vectors.pt")
    print("checks", json.dumps(checks), flush=True)
    assert a.dry_run or checks["pass"], "an instrument check failed: see checks.json"

    # ---------------------------------------------------------------- the arms
    groups = [[x for x in arms if x["kind"] != "steer"]] + [[x] for x in arms if x["kind"] == "steer"]
    m["status"] = "running"
    with open(rows_path, "a") as f:
        for group in [g for g in groups if g]:
            g0 = group[0]
            applied = None
            if hook is not None:
                applied = hook.set(*((g0["layer"], g0["alpha"] * rnorm[g0["layer"]] * dirs[g0["layer"]][g0["dir"]]) if g0["kind"] == "steer" else ()))
            t_gen = time.time()
            for arm in group:
                m["arms"][arm["arm"]] = {**arm, "applied_vector_norm": applied, "n": 0, "correct_v3": 0, "correct_v1": 0, "cap_hits": 0, "loop_A": 0,
                                         "generated_tokens": 0, "hold_words": 0, "started_utc": J.utc()}
                for r in requests(arm, list(zip(probs, pids)), cap):
                    live[r["rid"]] = r
                    engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"], r["logit_bias"])
            while engine.has_unfinished():
                for rid, out_ids, lps, fr in engine.step():
                    req = live.pop(rid)
                    rec = J.record(tok, req, out_ids, lps, fr)
                    rec.update(R.grade_v3(req["gold"], rec["text"]))
                    rec.update(arm=req["arm"], hold_words=ST.hold_count(rec["text"]), model=a.model, prompt_arm="cue", attempt=0)
                    f.write(json.dumps(rec) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                    c = m["arms"][req["arm"]]
                    c["n"] += 1
                    c["correct_v3"] += rec["score_v3"]
                    c["correct_v1"] += rec["score"]
                    c["cap_hits"] += int(rec["cap_hit"])
                    c["loop_A"] += int(rec["loop_A"])
                    c["generated_tokens"] += rec["n_new"]
                    c["hold_words"] += rec["hold_words"]
                    c["generation_s"] = time.time() - t_gen
                    write()
            for arm in group:
                c = m["arms"][arm["arm"]]
                c["hold_words_per_1k_tokens"] = 1000 * c["hold_words"] / max(1, c["generated_tokens"])
                print("arm", json.dumps({k: c[k] for k in ("arm", "n", "correct_v3", "cap_hits", "generated_tokens", "hold_words_per_1k_tokens", "generation_s")}), flush=True)
            write()
    assert not live, f"{len(live)} requests did not finish"
    if hook is not None:
        hook.set()
        m["hook_calls"] = dict(hook.calls)
    m["memory"] = engine.memory()
    m["status"] = "done"
    m["wall_s"] = time.time() - t0
    write()


if __name__ == "__main__":
    main()
