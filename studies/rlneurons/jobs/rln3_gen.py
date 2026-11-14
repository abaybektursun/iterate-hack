"""RLN-3 (studies/rlneurons/SPEC3.md): one model, arms P (plain), F (prefill) and C (forced commit on P and F), on MATH-500 and
the harder set, with n13's prompt, engine settings, extractor, grader and cap.

    python -m studies.rlneurons.jobs.rln3_gen --model <base|s0100|s0400|s2800|fr> --inputs s3://.../inputs/
        --allowance-min M [--check base|s2800] --out <dir>

Parent (pg venv): HF token; the inputs (frozen.json, math500.json, hard.json, n13 prompt_ids.json) from S3, sha256-checked; the
n13 engine venv /opt/n13 (vLLM 0.32.0, math-verify 0.9.0; n13_setup.venv_n13 unchanged); the model snapshot at the frozen commit,
every shard's sha256 checked against the HF LFS oid read now (failing input: the base model's oids); the RL 3.1 tokenizer files
(the prompt and detokenizer of every model, as in n13). Then the child under /opt/n13 does the work.

Child stages (each request's records appended to <out>/<cell>_<set>.jsonl with flush + fsync as it finishes; <out>/metrics.json
rewritten every 60 s and at every stage end; no accuracy is written to metrics.json except the check stage's):
  A   P, MATH-500, sample 0. With --check: accuracy must lie in n13's Wilson 95 % interval (frozen.json -> check); <out>/check.json;
      on a miss the job stops with exit 3.
  B1  F, MATH-500, sample 0.          B2  P and F, harder set, sample 0.
  C0  forced commit for every sample-0 answer not finished within N generated tokens: prompt + prefill + its first N tokens +
      the commit string, at most 100 new tokens, the parent's seed.
  D   MATH-500 samples 1..k (P and F) and their C requests; k = min(3, room), room from the measured seconds of A + B1 + C0(MATH).
  E   harder set samples 1..k (P and F) and their C requests; k = min(7, room), room from the measured seconds of B2 + C0(hard).
  room = floor((allowance - elapsed - 15 min) / measured seconds per sample). Elapsed counts from the parent's start.
Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
import zlib

from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S

RESERVE_S = 15 * 60
EVERY_S = 60.0
INPUTS = ("frozen.json", "math500.json", "hard.json", "prompt_ids.json")
SPECIAL_MIN = 100256      # ids at and above this are added tokens; their meaning differs between the 3.1 and 3.0 tokenizers


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def loop_ratio(text: str, chars: int):
    b = text[-chars:].encode()
    return len(zlib.compress(b)) / len(b) if b else None


# ------------------------------------------------------------------------------------------------ engines
class VllmEngine:
    """n13's engine construction (n13_gen.VllmEngine) with a per-request max_tokens (the C continuations take 100)."""

    def __init__(self, model_dir, tok_dir, cap):
        wrong = {k: os.environ.get(k) for k, v in G.ENGINE_ENV.items() if os.environ.get(k) != v}
        assert not wrong, f"A21: the engine environment differs from {G.ENGINE_ENV}: {wrong}"
        import vllm
        from vllm import EngineArgs, LLMEngine, SamplingParams
        self.SP = SamplingParams
        args = EngineArgs(model=str(model_dir), tokenizer=str(tok_dir), dtype="bfloat16", tensor_parallel_size=1,
                          max_model_len=2048 + cap, gpu_memory_utilization=0.90, enable_prefix_caching=True, generation_config="vllm",
                          seed=0, attention_backend=G.ATTENTION_BACKEND)
        self.engine = LLMEngine.from_engine_args(args)
        sc = self.engine.vllm_config.scheduler_config
        self.info = {"vllm": vllm.__version__, "engine_args": {k: str(v) for k, v in vars(args).items()},
                     "env": {k: os.environ[k] for k in G.ENGINE_ENV}, "max_num_seqs": sc.max_num_seqs,
                     "num_gpu_blocks": getattr(self.engine.vllm_config.cache_config, "num_gpu_blocks", None)}

    def params(self, seed, max_tokens):
        sp = self.SP(**G.SAMPLING, max_tokens=max_tokens, seed=seed)
        bad = {k: getattr(sp, k) for k, ok in G.NEUTRAL.items() if hasattr(sp, k) and getattr(sp, k) not in ok}
        assert not bad, f"sampling fields not at their neutral value: {bad}"
        return sp

    def add(self, rid, ids, seed, max_tokens):
        self.engine.add_request(rid, {"prompt_token_ids": ids}, self.params(seed, max_tokens))

    def step(self):
        res = []
        for o in self.engine.step():
            if o.finished:
                c = o.outputs[0]
                tids = list(c.token_ids)
                res.append((o.request_id, tids, [lp[t].logprob for lp, t in zip(c.logprobs, tids)], c.finish_reason))
        return res

    def has_unfinished(self):
        return self.engine.has_unfinished_requests()

    def memory(self):
        q = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,name", "--format=csv,noheader,nounits"], check=True,
                           capture_output=True, text=True).stdout.strip().split(", ")
        return {"gpu_memory_used_mib": int(q[0]), "gpu_memory_total_mib": int(q[1]), "gpu": q[2]}


# ------------------------------------------------------------------------------------------------ records
def gen_record(tok, fz, key, prob, seed, n_prompt, pre_ids, out_ids, lps, finish_reason, max_tokens) -> dict:
    cell, bench, s, idx = key
    j = next((i for i, t in enumerate(out_ids) if t == S.STOP_ID), None)
    ids = out_ids if j is None else out_ids[:j]
    assert j is not None or len(ids) == max_tokens, f"{key}: no stop id in {len(ids)} ids, max_tokens {max_tokens}"
    pre_text = tok.decode(pre_ids, skip_special_tokens=False) if pre_ids else ""
    gen_text = tok.decode(ids, skip_special_tokens=False)
    text = pre_text + gen_text
    mode, ext, span = S.extract(text)
    g = S.grade(prob["answer"], ext)
    off = len(pre_text)
    if span is not None and span[0] >= off:
        lp = S.span_logprob(tok, ids, list(lps[: len(ids)]), gen_text, (span[0] - off, span[1] - off))
    else:
        lp = S.span_logprob(tok, ids, list(lps[: len(ids)]), gen_text, None)
    finished_by_n = j is not None and len(out_ids) <= fz["N"]
    return {"cell": cell, "bench": bench, "sample": s, "problem_index": idx, "unique_id": prob["unique_id"], "seed": seed,
            "prompt_n_tokens": n_prompt, "prefill_ids": pre_ids, "text": text, "n_new": len(ids), "n_generated": len(out_ids),
            "cap_hit": j is None, "finish_reason": finish_reason, "finished_by_N": finished_by_n,
            "loop_ratio": loop_ratio(text, fz["loop"]["chars"]), "n_special_ids": sum(t >= SPECIAL_MIN and t != S.STOP_ID for t in ids),
            "mode": mode, "extracted": ext, "gold": prob["answer"], **g, **lp, "utc": utc()}


def commit_record(tok, fz, key, prob, seed, cut_ids, out_ids, lps, finish_reason) -> dict:
    cell, bench, s, idx = key
    j = next((i for i, t in enumerate(out_ids) if t == S.STOP_ID), None)
    ids = out_ids if j is None else out_ids[:j]
    cont = tok.decode(ids, skip_special_tokens=False)
    box = S.boxed_last(fz["commit_text"] + cont)
    ext = box[0] if box is not None else None
    g = S.grade(prob["answer"], ext)
    return {"cell": cell, "bench": bench, "sample": s, "problem_index": idx, "unique_id": prob["unique_id"], "seed": seed,
            "N": fz["N"], "cut_ids": cut_ids, "cut_tail": tok.decode(cut_ids[-200:], skip_special_tokens=False), "continuation": cont,
            "n_cont": len(ids), "n_generated": len(out_ids), "finish_reason": finish_reason, "closed": box is not None,
            "extracted": ext, "gold": prob["answer"], **g, "mean_logprob": sum(lps) / len(lps) if lps else None, "utc": utc()}


# ------------------------------------------------------------------------------------------------ the child
def run(a, engine_factory=None, clock=time.time) -> dict:
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ind = pathlib.Path(a.inputs_dir)
    fz = json.loads((ind / "frozen.json").read_text())
    probs = {b: json.loads((ind / f"{b}.json").read_text()) for b in ("math500", "hard")}
    for b in probs:
        assert hashlib.sha256((ind / f"{b}.json").read_bytes()).hexdigest() == fz["sha256"][b], f"{b}.json differs from frozen.json"
        assert [p["index"] for p in probs[b]] == list(range(len(probs[b])))
    t0 = a.t0 if a.t0 else clock()
    allow_s = a.allowance_min * 60.0
    m = {"model": a.model, "repo_commit": fz["models"][a.model], "status": "running", "stage": "inputs", "started_utc": utc(),
         "allowance_min": a.allowance_min, "N": fz["N"], "cap": fz["cap"], "stages": [], "plan": {"math500": 1, "hard": 1}}

    def write_metrics():
        m["updated_utc"] = utc()
        m["elapsed_s"] = clock() - t0
        G.dump(out / "metrics.json", m)

    write_metrics()

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok_dir)
    assert tok.decode(fz["prefill_ids"]) == fz["prefill_text"], "prefill ids do not decode to the frozen text"
    assert tok.decode(fz["commit_ids"]) == fz["commit_text"], "commit ids do not decode to the frozen text"
    pids = {}
    for b in probs:
        bad = [p["index"] for p in probs[b] if S.render_text(tok, p["problem"]) != S.TEMPLATE[fz["template"]].format(problem=p["problem"])]
        assert not bad, (f"G-TEMPLATE: {b} renders differ from the registered bytes", bad[:5])
        pids[b] = [S.render_ids(tok, p["problem"]) for p in probs[b]]
        assert max(len(x) for x in pids[b]) + len(fz["prefill_ids"]) <= 2048, f"a {b} prompt is longer than 2,048 tokens with the prefill"
    n13_ids = json.loads((ind / "prompt_ids.json").read_text())
    assert n13_ids["pair"] == "pair1" and pids["math500"] == n13_ids["ids"], "G-TEMPLATE: MATH-500 prompt ids differ from n13's"
    m["template"] = {"pass": True, "n": {b: len(v) for b, v in pids.items()}, "math500_ids_equal_n13": True}
    write_metrics()

    t_load = clock()
    engine = engine_factory(a.model_dir, a.tok_dir, fz["cap"], tok) if engine_factory else VllmEngine(a.model_dir, a.tok_dir, fz["cap"])
    m["engine"] = {**engine.info, "load_s": clock() - t_load}
    m["sampling"] = G.SAMPLING
    write_metrics()

    files = {}

    def fh(cell, bench):
        k = f"{cell}_{bench}"
        if k not in files:
            p = out / f"{k}.jsonl"
            assert not p.exists(), f"{p} exists: one fresh directory per run"
            files[k] = open(p, "a")
        return files[k]

    counts, cut = {}, {}            # cut[(cell, bench, s, idx)] = (prompt ids + prefill ids, first N generated ids)

    def seed(bench, s, idx):
        return fz["seeds"][bench] + s * fz["seeds"]["per_sample"] + idx

    def gen_requests(cells, bench, samples):
        reqs = []
        for s in samples:
            for cell in cells:
                pre = fz["prefill_ids"] if cell == "F" else []
                for p, ids in zip(probs[bench], pids[bench]):
                    reqs.append(((cell, bench, s, p["index"]), ids + pre, seed(bench, s, p["index"]), fz["cap"], len(ids), pre))
        return reqs

    def commit_requests(bench, samples):
        reqs = []
        for key in sorted(k for k in cut if k[1] == bench and k[2] in samples):
            base_ids, cids = cut[key]
            ckey = ("C" + key[0], *key[1:])
            reqs.append((ckey, base_ids + cids + fz["commit_ids"], seed(*key[1:]), fz["commit_max_tokens"], cids, None))
        return reqs

    def stage(name, reqs):
        m["stage"] = name
        write_metrics()
        live = {}
        for r in reqs:
            rid = "|".join(map(str, r[0]))
            live[rid] = r
            engine.add(rid, r[1], r[2], r[3])
        ts, tok_n, last = clock(), 0, clock()
        recs = []
        while engine.has_unfinished():
            for rid, out_ids, lps, fr in engine.step():
                key, ids, sd, mt, extra, pre = live.pop(rid)
                cell, bench, s, idx = key
                prob = probs[bench][idx]
                if cell in ("P", "F"):
                    rec = gen_record(tok, fz, key, prob, sd, extra, pre, out_ids, lps, fr, mt)
                    if not rec["finished_by_N"]:
                        cut[key] = (ids, out_ids[: fz["N"]])
                else:
                    rec = commit_record(tok, fz, key, prob, sd, extra, out_ids, lps, fr)
                f = fh(cell, bench)
                f.write(json.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
                recs.append(rec)
                tok_n += len(out_ids)
                c = counts.setdefault(f"{cell}_{bench}", {"n": 0, "cap_hits": 0, "not_finished_by_N": 0, "closed": 0})
                c["n"] += 1
                c["cap_hits"] += int(rec.get("cap_hit", False))
                c["not_finished_by_N"] += int(rec.get("finished_by_N") is False)
                c["closed"] += int(rec.get("closed", False))
            if clock() - last >= EVERY_S:
                m["counts"], m["stage_progress"] = counts, {"stage": name, "done": len(reqs) - len(live), "of": len(reqs)}
                write_metrics()
                last = clock()
        assert not live, f"{name}: {len(live)} requests never finished"
        sec = clock() - ts
        m["stages"].append({"name": name, "n_requests": len(reqs), "seconds": sec, "output_tokens": tok_n,
                            "tokens_per_s": tok_n / max(sec, 1e-9), "end_utc": utc()})
        m["counts"], m["stage_progress"] = counts, {"stage": name, "done": len(reqs), "of": len(reqs)}
        write_metrics()
        return recs, sec

    # A: the check -------------------------------------------------------------------------------------------------------------
    recA, secA = stage("A_P_math500_s0", gen_requests(["P"], "math500", [0]))
    if a.check:
        acc = S.acc([r["score"] for r in recA])
        lo, hi = fz["check"][a.check]["wilson95"]
        chk = {"model": a.model, "against": a.check, "n": len(recA), "correct": int(sum(r["score"] for r in recA)), "acc": acc,
               "n13_correct": fz["check"][a.check]["n13_correct"], "n13_wilson95": [lo, hi], "pass": bool(lo <= acc <= hi),
               "cap_hits": sum(r["cap_hit"] for r in recA), "utc": utc()}
        G.dump(out / "check.json", chk)
        m["check"] = chk
        write_metrics()
        if not chk["pass"]:
            m["status"] = "check_failed"
            write_metrics()
            raise SystemExit(3)
    _, secB1 = stage("B1_F_math500_s0", gen_requests(["F"], "math500", [0]))
    _, secB2 = stage("B2_PF_hard_s0", gen_requests(["P", "F"], "hard", [0]))
    _, secC0m = stage("C0_math500_s0", commit_requests("math500", [0]))
    _, secC0h = stage("C0_hard_s0", commit_requests("hard", [0]))

    def room(per_sample, most):
        left = allow_s - (clock() - t0) - RESERVE_S
        return max(0, min(most, int(left // max(per_sample, 1e-9)))), left

    k_m, left = room(secA + secB1 + secC0m, fz["samples"]["math500"] - 1)
    m["plan"]["math500"] = 1 + k_m
    m["plan"]["math500_rule"] = {"seconds_per_sample": secA + secB1 + secC0m, "seconds_left": left, "extra": k_m}
    write_metrics()
    if k_m:
        stage(f"D_PF_math500_s1-{k_m}", gen_requests(["P", "F"], "math500", list(range(1, k_m + 1))))
        stage(f"D_C_math500_s1-{k_m}", commit_requests("math500", list(range(1, k_m + 1))))
    k_h, left = room(secB2 + secC0h, fz["samples"]["hard_max"] - 1)
    m["plan"]["hard"] = 1 + k_h
    m["plan"]["hard_rule"] = {"seconds_per_sample": secB2 + secC0h, "seconds_left": left, "extra": k_h}
    write_metrics()
    if k_h:
        stage(f"E_PF_hard_s1-{k_h}", gen_requests(["P", "F"], "hard", list(range(1, k_h + 1))))
        stage(f"E_C_hard_s1-{k_h}", commit_requests("hard", list(range(1, k_h + 1))))
    for f in files.values():
        f.close()
    m["memory"] = engine.memory()
    m["status"] = "done"
    m["stage"] = "done"
    m["finished_utc"] = utc()
    write_metrics()
    print(f"RLN3 {a.model} done: plan {m['plan']['math500']} MATH-500 samples, {m['plan']['hard']} harder-set samples", flush=True)
    return m


# ------------------------------------------------------------------------------------------------ the parent
def setup(a) -> list:
    """The inputs, the venv, the weights and the tokenizer; returns the child's extra argv."""
    from studies.rlneurons.lib import n13_setup as N
    from studies.rlneurons.lib import n13_arms as A
    from studies.rlneurons.lib.hf_helpers import hf_setup
    from studies.rlneurons.lib.hf_helpers import retry_transport
    hf_setup()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rec = {"model": a.model, "status": "setup", "started_utc": utc()}

    def w():
        G.dump(out / "setup.json", rec)
        G.dump(out / "metrics.json", rec)        # the child rewrites metrics.json from its first stage; setup.json keeps this record

    w()
    loc = pathlib.Path("/work/inputs")
    loc.mkdir(parents=True, exist_ok=True)
    for f in INPUTS:
        subprocess.run(["aws", "s3", "cp", a.inputs.rstrip("/") + "/" + f, str(loc / f), "--region", "us-east-1"], check=True)
    fz = json.loads((loc / "frozen.json").read_text())
    rec["venv_n13"] = N.venv_n13(out)
    w()
    from huggingface_hub import snapshot_download
    repo, branch, rev = fz["models"][a.model]
    d, n_retry = retry_transport(lambda: snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"],
                                                           max_workers=8), what=f"{repo}@{rev}")
    oids = N.lfs_oids(N.tree(repo, rev))
    hashes = {p: A.file_sha256(pathlib.Path(d) / p) for p in sorted(oids)}
    bad = [p for p in oids if hashes[p] != oids[p]]
    other = N.lfs_oids(N.tree(*fz["models"]["base" if a.model != "base" else "s2800"][::2]))
    rec["weights"] = {"repo": repo, "branch": branch, "commit": rev, "dir": d, "n_shards": len(oids), "retries": n_retry, "pass": not bad,
                      "failing_input": {"what": "another model's LFS oids", "failed": hashes != {p: other.get(p) for p in hashes}}}
    w()
    assert not bad and rec["weights"]["failing_input"]["failed"], ("G-WEIGHTS", rec["weights"], bad)
    trepo, trev = fz["tokenizer"]
    tok_dir, _ = retry_transport(lambda: snapshot_download(trepo, revision=trev, allow_patterns=["*.json", "*.jinja", "*.txt"]),
                                 what=f"{trepo}@{trev} tokenizer")
    rec["tokenizer_dir"] = tok_dir
    w()
    return ["--model-dir", d, "--tok-dir", tok_dir, "--inputs-dir", str(loc)]


def parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", required=True, choices=("base", "s0100", "s0400", "s2800", "fr"))
    ap.add_argument("--inputs", default=None, help="S3 prefix holding frozen.json, math500.json, hard.json, prompt_ids.json")
    ap.add_argument("--allowance-min", type=float, required=True)
    ap.add_argument("--check", default=None, choices=("base", "s2800"))
    ap.add_argument("--inner", action="store_true")
    ap.add_argument("--model-dir")
    ap.add_argument("--tok-dir")
    ap.add_argument("--inputs-dir")
    ap.add_argument("--t0", type=float, default=None)
    return ap


def main():
    a = parser().parse_args()
    if a.inner:
        run(a)
        return
    t0 = time.time()
    extra = setup(a)
    subprocess.run([G.N13_PY, "-m", "studies.rlneurons.jobs.rln3_gen", *sys.argv[1:], *extra, "--t0", str(t0), "--inner"], check=True,
                   env=G.child_env(os.environ))


if __name__ == "__main__":
    main()
