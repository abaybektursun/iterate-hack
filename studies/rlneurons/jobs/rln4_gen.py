"""RLN-4 (studies/rlneurons/SPEC4.md): temperature, continuation and restart cells on MATH-500, and a bank of training-prompt answers.

    python -m studies.rlneurons.jobs.rln4_gen --inputs s3://.../r4/inputs/ --out <dir>

Parent (pg venv): the inputs from S3 (sha256 against frozen4.json), the n13 engine venv /opt/n13 (vLLM 0.32.0, as RLN-3), the base
snapshot (every shard's sha256 against the HF LFS oid), the RL 3.1 tokenizer; then three children under /opt/n13, one engine each:
  base1  check (50 problems, base F, T 0.6, base-01's seeds; >= 45 of 50 scores equal to base-01's passes, < 35 stops with exit 3,
         between: the job continues and check.json says the cross-run comparisons do not count)
         then one queue: T1 (base F, T 1.0, top-p 1.0) + K_rl, K_own, K_fresh (T 0.6); a K_fresh cap hit adds K_fresh2 (second restart)
  rl     T2 (RL step 2,800, plain, T 1.0, top-p 1.0). The RL snapshot is downloaded and checked while base1 runs.
  base2  G (base F, T 1.0, Dolci training prompts, 4 samples, cap 4,096) submitted prompt by prompt until 1,000 prompts or the
         G submission stop; then R1 (base F, T 0.6, repetition_penalty 1.1) + T3 (base plain, T 1.0) only if G reached 1,000.
Every finished request is appended to <out>/<cell>.jsonl with flush + fsync; <out>/metrics.json is rewritten every 60 s. At the
hard stop (frozen4.json stop_utc) unfinished requests are aborted and listed in metrics.json; the job then exits 0.
Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

EVERY_S = 60.0
INPUTS = ("frozen4.json", "k.json", "g.json", "check.json", "math500.json", "prompt_ids.json", "check_rl.json")
TOKENIZER_PINS = {"transformers": "5.19.0", "tokenizers": "0.23.3"}
G_PENDING = 512         # G requests kept submitted (running + waiting) while G prompts remain
BASE_SAMPLING = {"n": 1, "top_k": -1, "min_p": 0.0, "presence_penalty": 0.0, "frequency_penalty": 0.0, "stop_token_ids": [S.STOP_ID],
                 "logprobs": 0}
# RL check (Modal deviation, SPEC4): RL step 2,800, plain prompt, n13's sampling and seed set A, problems 0-49, compared with n13
# s3gate-03's RL answers (inputs/check_rl.json, written by rln4_prep.write_check_rl; not in frozen4.json, so its sha256 is here).
CHECK_RL_SHA256 = "0291e7b316c145c0696e1f3a7f45c6b5e2afef7d741d9f683f50e4070108257c"
CHECK_RL_GPU = "L40S"       # n13 s3gate-03 ran on g6e (L40S)


def with_rl_check(fz):
    fz["cells"]["check_rl"] = ["s2800", "P", {k: G.SAMPLING[k] for k in ("temperature", "top_p", "repetition_penalty")}]
    fz["seeds"]["check_rl"] = fz["seeds"]["check"]
    return fz


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def epoch(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))


class VllmEngine:
    """RLN-3's engine construction (rln3_gen.VllmEngine: n13 settings, gpu_memory_utilization 0.90) with per-request sampling."""

    def __init__(self, model_dir, tok_dir, max_model_len):
        wrong = {k: os.environ.get(k) for k, v in G.ENGINE_ENV.items() if os.environ.get(k) != v}
        assert not wrong, f"A21: the engine environment differs from {G.ENGINE_ENV}: {wrong}"
        import vllm
        from vllm import EngineArgs, LLMEngine, SamplingParams
        self.SP = SamplingParams
        args = EngineArgs(model=str(model_dir), tokenizer=str(tok_dir), dtype="bfloat16", tensor_parallel_size=1, max_model_len=max_model_len,
                          gpu_memory_utilization=0.90, enable_prefix_caching=True, generation_config="vllm", seed=0,
                          attention_backend=G.ATTENTION_BACKEND)
        self.engine = LLMEngine.from_engine_args(args)
        sc = self.engine.vllm_config.scheduler_config
        self.info = {"vllm": vllm.__version__, "max_num_seqs": sc.max_num_seqs, "max_num_batched_tokens": sc.max_num_batched_tokens,
                     "num_gpu_blocks": getattr(self.engine.vllm_config.cache_config, "num_gpu_blocks", None),
                     "gpu_memory_utilization": 0.90, "max_model_len": max_model_len}

    def add(self, rid, ids, sampling, seed, max_tokens):
        sp = self.SP(**{**BASE_SAMPLING, **sampling}, max_tokens=max_tokens, seed=seed)     # sampling may override min_p, top_k
        bad = {k: getattr(sp, k) for k, ok in G.NEUTRAL.items() if hasattr(sp, k) and getattr(sp, k) not in ok}
        assert not bad, f"sampling fields not at their neutral value: {bad}"
        self.engine.add_request(rid, {"prompt_token_ids": ids}, sp)

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

    def abort(self, rids):
        self.engine.abort_request(list(rids))

    def memory(self):
        q = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,name", "--format=csv,noheader,nounits"], check=True,
                           capture_output=True, text=True).stdout.strip().split(", ")
        return {"gpu_memory_used_mib": int(q[0]), "gpu_memory_total_mib": int(q[1]), "gpu": q[2]}


def record(tok, req, out_ids, lps, finish_reason) -> dict:
    j = next((i for i, t in enumerate(out_ids) if t == S.STOP_ID), None)
    ids = out_ids if j is None else out_ids[:j]
    assert j is not None or len(ids) == req["max_tokens"], f"{req['rid']}: no stop id in {len(ids)} ids, max_tokens {req['max_tokens']}"
    pre_text = tok.decode(req["prefix_ids"], skip_special_tokens=False) if req["prefix_ids"] else ""
    gen_text = tok.decode(ids, skip_special_tokens=False)
    text = pre_text + gen_text
    mode, ext, span = S.extract(text)
    g = S.grade(req["gold"], ext)
    off = len(pre_text)
    sp = (span[0] - off, span[1] - off) if span is not None and span[0] >= off else None
    lp = S.span_logprob(tok, ids, list(lps[: len(ids)]), gen_text, sp)
    oa, ob = R.onset_lines(text), R.onset_period(text)
    return {"cell": req["cell"], "bench": req["bench"], "problem_index": req["idx"], "sample": req["sample"], "unique_id": req["uid"],
            "seed": req["seed"], "sampling": req["sampling"], "max_tokens": req["max_tokens"], "prompt_n_tokens": req["n_prompt"],
            "prefix_kind": req["prefix_kind"], "n_prefix": len(req["prefix_ids"]), "text": text, "n_new": len(ids),
            "n_generated": len(out_ids), "n_answer_tokens": len(req["prefix_ids"]) + len(ids), "cap_hit": j is None,
            "finish_reason": finish_reason, "loop_ratio": R.zratio(text[-R.W:]), "onset_A_char": oa, "onset_B_char": ob,
            "loop_A": oa is not None, "loop_B": ob is not None, "mode": mode, "extracted": ext, "gold": req["gold"], **g,
            **R.grade_v2(req["gold"], text), **lp, "utc": utc()}


# ------------------------------------------------------------------------------------------------ the child
def run(a, engine_factory=None, clock=time.time) -> dict:
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ind = pathlib.Path(a.inputs_dir)
    fz = with_rl_check(json.loads((ind / "frozen4.json").read_text()))
    for f in INPUTS[1:5]:
        assert hashlib.sha256((ind / f).read_bytes()).hexdigest() == fz["sha256"][f], f"{f} differs from frozen4.json"
    K = json.loads((ind / "k.json").read_text())
    GR = json.loads((ind / "g.json").read_text())
    CHK = json.loads((ind / "check.json").read_text())
    math = json.loads((ind / "math500.json").read_text())
    stop_t, g_stop_t = epoch(fz["stop_utc"]) + a.time_shift, epoch(fz["g_submit_stop_utc"]) + a.time_shift
    cap, pre = fz["cap"], fz["prefill_ids"]
    mpath = out / "metrics.json"
    m = json.loads(mpath.read_text()) if mpath.exists() else {"phases": {}}
    ph = m["phases"][a.phase] = {"status": "running", "started_utc": utc(), "stages": [], "counts": {}}
    m["phase"] = a.phase

    def write():
        m["updated_utc"] = utc()
        G.dump(mpath, m)

    write()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok_dir)
    assert tok.decode(pre) == fz["prefill_text"]
    bad = [p["index"] for p in math if S.render_text(tok, p["problem"]) != S.TEMPLATE[fz["template"]].format(problem=p["problem"])]
    assert not bad, ("G-TEMPLATE", bad[:5])
    pids = [S.render_ids(tok, p["problem"]) for p in math]
    n13 = json.loads((ind / "prompt_ids.json").read_text())
    assert n13["pair"] == "pair1" and pids == n13["ids"], "G-TEMPLATE: MATH-500 prompt ids differ from n13's"
    ph["template"] = {"pass": True}

    t_load = clock()
    model_dir = a.model_dir
    engine = engine_factory(model_dir, a.tok_dir, a.phase) if engine_factory else VllmEngine(model_dir, a.tok_dir, 2048 + cap)
    ph["engine"] = {**engine.info, "load_s": clock() - t_load}
    write()
    files = {}

    def fh(cell):
        if cell not in files:
            p = out / f"{cell}.jsonl"
            assert not p.exists(), f"{p} exists: one fresh directory per run"
            files[cell] = open(p, "a")
        return files[cell]

    def math_req(cell, i, prefix_ids, prefix_kind, sample=0):
        model, arm, sampling = fz["cells"][cell]
        base = pre if arm != "P" else []
        assert prefix_ids[:len(base)] == base
        seed = fz["seeds"][cell] + i
        mt = cap - len(prefix_ids) if cell.startswith("K_") else cap
        return {"rid": f"{cell}|{i}|{sample}", "cell": cell, "bench": "math500", "idx": i, "sample": sample, "uid": math[i]["unique_id"],
                "ids": pids[i] + prefix_ids, "n_prompt": len(pids[i]), "prefix_ids": prefix_ids, "prefix_kind": prefix_kind,
                "seed": seed, "sampling": sampling, "max_tokens": mt, "gold": math[i]["answer"]}

    def g_reqs(row):
        model, arm, sampling = fz["cells"]["G"]
        ids = S.render_ids(tok, row["prompt"])
        assert len(ids) + len(pre) <= 2048, f"G row {row['row']}: prompt longer than 2,048 tokens"
        return [{"rid": f"G|{row['row']}|{s}", "cell": "G", "bench": "dolci", "idx": row["row"], "sample": s, "uid": f"dolci/{row['row']}",
                 "ids": ids + pre, "n_prompt": len(ids), "prefix_ids": pre, "prefix_kind": "opening",
                 "seed": fz["seeds"]["G"] + s * fz["seeds"]["G_per_sample"] + row["row"], "sampling": sampling,
                 "max_tokens": fz["g"]["cap"], "gold": row["ground_truth"]} for s in range(fz["g"]["samples"])]

    def queue(name, reqs, on_done=None):
        ph["stage"] = name
        write()
        live = {}

        def add(r):
            live[r["rid"]] = r
            engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"])

        for r in reqs:
            add(r)
        ts, last, tok_n, n_req, recs, aborted = clock(), clock(), 0, len(reqs), [], []
        while engine.has_unfinished():
            if clock() >= stop_t:
                aborted = sorted(live)
                engine.abort(aborted)
                live.clear()
                break
            for rid, out_ids, lps, fr in engine.step():
                req = live.pop(rid)
                rec = record(tok, req, out_ids, lps, fr)
                f = fh(req["cell"])
                f.write(json.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
                recs.append(rec)
                tok_n += len(out_ids)
                c = ph["counts"].setdefault(req["cell"], {"n": 0, "cap_hits": 0, "loop_A": 0})
                c["n"] += 1
                c["cap_hits"] += int(rec["cap_hit"])
                c["loop_A"] += int(rec["loop_A"])
                for r in (on_done(rec, len(live)) if on_done else []):
                    add(r)
                    n_req += 1
            if clock() - last >= EVERY_S:
                ph["stage_progress"] = {"stage": name, "done": len(recs), "submitted": n_req, "live": len(live),
                                        "tokens_per_s": tok_n / max(clock() - ts, 1e-9)}
                write()
                last = clock()
        sec = clock() - ts
        ph["stages"].append({"name": name, "n_requests": n_req, "n_done": len(recs), "n_aborted": len(aborted), "aborted": aborted,
                             "seconds": sec, "output_tokens": tok_n, "tokens_per_s": tok_n / max(sec, 1e-9), "end_utc": utc()})
        ph["stage_progress"] = {"stage": name, "done": len(recs), "submitted": n_req, "live": 0}
        write()
        return recs, bool(aborted)

    def k_reqs(arms):
        reqs = [math_req("K_rl", r["problem_index"], r["rl_prefix_ids"], "rl_prefix") for r in K["rows"]] if "K_rl" in arms else []
        reqs += [math_req("K_own", r["problem_index"], r["own_prefix_ids"], "own_prefix") for r in K["rows"]] if "K_own" in arms else []
        reqs += [math_req("K_fresh", i, pre, "opening") for i in K["restart"]] if "K_fresh" in arms else []
        return reqs

    def second_restart(rec, n_live):
        if rec["cell"] == "K_fresh" and rec["cap_hit"] and clock() < stop_t:
            return [math_req("K_fresh2", rec["problem_index"], pre, "opening", sample=1)]
        return []

    def check(cell, ref, prefix_ids, ref_gpu):
        """cell on ref's problems and seeds; scores compared with ref's; writes <cell>.json; exit 3 below the stop threshold."""
        recs, _ = queue(cell, [math_req(cell, c["problem_index"], prefix_ids, "opening" if prefix_ids else "none") for c in ref])
        by = {r["problem_index"]: r for r in recs}
        assert sorted(by) == [c["problem_index"] for c in ref], f"{cell}: a request did not finish"
        assert all(by[c["problem_index"]]["seed"] == c["seed"] for c in ref), f"{cell}: seeds differ from the reference run's"
        agree = sum(by[c["problem_index"]]["score"] == c["score"] for c in ref)
        ident = sum(hashlib.sha256(by[c["problem_index"]]["text"].encode()).hexdigest() == c["text_sha256"] for c in ref)
        rule = fz["check_rule"]
        gpu = engine.memory()["gpu"]
        same = ref_gpu in gpu
        need = rule["pass_at_least"] if same else rule["pass_at_least_other_gpu"]
        verdict = "pass" if agree >= need else ("stop" if agree < rule["stop_below"] else "continue_does_not_count")
        chk = {"n": len(ref), "scores_equal": agree, "texts_identical": ident, "correct_now": sum(r["score"] for r in recs),
               "correct_base01": sum(c["score"] for c in ref), "cap_hits_now": sum(r["cap_hit"] for r in recs),
               "cap_hits_base01": sum(c["cap_hit"] for c in ref), "rule": rule, "reference_gpu": ref_gpu,
               "same_gpu_as_base01": same, "pass_at_least": need, "verdict": verdict, "gpu": gpu, "utc": utc()}
        G.dump(out / f"{cell}.json", chk)
        ph[cell] = chk
        write()
        if verdict == "stop":
            ph["status"] = "check_failed"
            write()
            raise SystemExit(3)

    if a.phase in ("base1", "check"):
        check("check", CHK, pre, fz["check_rule"]["base01_gpu_substring"])
        if a.phase == "base1":
            queue("T1+K", [math_req("T1", i, pre, "opening") for i in range(500)] + k_reqs(("K_rl", "K_own", "K_fresh")), second_restart)
    elif a.phase == "k":            # K arms alone (jobs/modal_rln4_k.py), after a separate check phase
        arms = a.arms.split(",")
        assert arms and set(arms) <= {"K_rl", "K_own", "K_fresh"}, arms
        queue("K", k_reqs(arms), second_restart)
    elif a.phase in ("rl", "rl_check"):
        if a.phase == "rl_check":       # jobs/modal_rln4_k.py: the RL check first, then T2 on the same engine
            assert hashlib.sha256((ind / "check_rl.json").read_bytes()).hexdigest() == CHECK_RL_SHA256, "check_rl.json differs"
            check("check_rl", json.loads((ind / "check_rl.json").read_text()), [], CHECK_RL_GPU)
        queue("T2", [math_req("T2", i, [], "none") for i in range(500)])
    elif a.phase == "t3":               # jobs/modal_rln4_k.py: T3 alone, after the base check of modal_k-01
        queue("T3", [math_req("T3", i, [], "none") for i in range(500)])
    elif a.phase == "base2":
        rows = list(GR)
        nxt = {"i": 0}
        first = []
        while nxt["i"] < len(rows) and len(first) < G_PENDING and clock() < g_stop_t:
            first += g_reqs(rows[nxt["i"]])
            nxt["i"] += 1

        def top_up(rec, n_live):
            new = []
            while nxt["i"] < len(rows) and n_live + len(new) < G_PENDING and clock() < g_stop_t:
                new += g_reqs(rows[nxt["i"]])
                nxt["i"] += 1
            return new
        _, cut = queue("G", first, top_up)
        ph["g_prompts_submitted"] = nxt["i"]
        ph["g_reached_target"] = nxt["i"] == fz["g"]["target"] and not cut
        write()
        if ph["g_reached_target"] and clock() < stop_t:
            queue("R1+T3", [math_req("R1", i, pre, "opening") for i in range(500)] + [math_req("T3", i, [], "none") for i in range(500)])
        else:
            ph["dropped"] = ["R1", "T3"]
    for f in files.values():
        f.close()
    ph["memory"] = engine.memory()
    ph["status"] = "done"
    ph["finished_utc"] = utc()
    write()
    return m


# ------------------------------------------------------------------------------------------------ the parent
def weights(model, fz, out):
    from huggingface_hub import snapshot_download
    from studies.rlneurons.lib import n13_setup as N
    from studies.rlneurons.lib import n13_arms as A
    from studies.rlneurons.lib.hf_helpers import retry_transport
    repo, branch, rev = fz["models"][model]
    d, n_retry = retry_transport(lambda: snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"],
                                                           max_workers=8), what=f"{repo}@{rev}")
    oids = N.lfs_oids(N.tree(repo, rev))
    hashes = {p: A.file_sha256(pathlib.Path(d) / p) for p in sorted(oids)}
    bad = [p for p in oids if hashes[p] != oids[p]]
    other = N.lfs_oids(N.tree(*fz["models"]["base" if model != "base" else "s2800"][::2]))
    rec = {"repo": repo, "commit": rev, "dir": d, "n_shards": len(oids), "retries": n_retry, "pass": not bad,
           "failing_input": {"what": "the other model's LFS oids", "failed": hashes != {p: other.get(p) for p in hashes}}}
    assert not bad and rec["failing_input"]["failed"], ("G-WEIGHTS", rec, bad)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--inputs", default=None)
    ap.add_argument("--inner", action="store_true")
    ap.add_argument("--phase", choices=("base1", "rl", "base2", "check", "k", "rl_check", "t3"))
    ap.add_argument("--arms", default="K_rl,K_own,K_fresh", help="phase k only: comma-separated K arms")
    ap.add_argument("--model-dir")
    ap.add_argument("--tok-dir")
    ap.add_argument("--inputs-dir")
    ap.add_argument("--time-shift", type=float, default=0.0, help="offline gate only: shifts the frozen stop times")
    a = ap.parse_args()
    if a.inner:
        run(a)
        return
    from studies.rlneurons.lib import n13_setup as N
    from studies.rlneurons.lib.hf_helpers import hf_setup
    hf_setup()                                      # before huggingface_hub is imported: it reads HF_HUB_OFFLINE at import
    from huggingface_hub import snapshot_download
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rec = {"status": "setup", "started_utc": utc()}
    G.dump(out / "setup.json", rec)
    loc = pathlib.Path("/work/inputs")
    loc.mkdir(parents=True, exist_ok=True)
    for f in INPUTS:
        subprocess.run(["aws", "s3", "cp", a.inputs.rstrip("/") + "/" + f, str(loc / f), "--region", "us-east-1"], check=True)
    fz = json.loads((loc / "frozen4.json").read_text())
    rec["venv_n13"] = N.venv_n13(out)
    # base-01's engine build had transformers 5.19.0 / tokenizers 0.23.3 (its pip_freeze_n13.txt); vLLM 0.32.0 leaves them unpinned
    subprocess.run([G.N13_PY, "-m", "pip", "install", "--no-cache-dir", *[f"{k}=={v}" for k, v in TOKENIZER_PINS.items()]], check=True)
    pins, text = N.freeze(G.N13_PY)
    (out / "pip_freeze_n13_after_pins.txt").write_text(text)
    assert all(pins.get(N.canon(k)) == v for k, v in TOKENIZER_PINS.items()), {k: pins.get(N.canon(k)) for k in TOKENIZER_PINS}
    rec["tokenizer_pins"] = TOKENIZER_PINS
    G.dump(out / "setup.json", rec)
    rec["weights"] = {"base": weights("base", fz, out)}
    trepo, trev = fz["tokenizer"]
    tok_dir = snapshot_download(trepo, revision=trev, allow_patterns=["*.json", "*.jinja", "*.txt"])
    rec["tokenizer_dir"] = tok_dir
    G.dump(out / "setup.json", rec)

    def child(phase, model_dir):
        return subprocess.Popen([G.N13_PY, "-m", "studies.rlneurons.jobs.rln4_gen", "--out", a.out, "--inner", "--phase", phase, "--model-dir",
                                 model_dir, "--tok-dir", tok_dir, "--inputs-dir", str(loc)], env=G.child_env(os.environ))

    p = child("base1", rec["weights"]["base"]["dir"])
    rec["weights"]["s2800"] = weights("s2800", fz, out)         # while base1 runs
    G.dump(out / "setup.json", rec)
    rc = p.wait()
    assert rc == 0, f"phase base1 exited {rc}"
    for phase, model in (("rl", "s2800"), ("base2", "base")):
        if time.time() >= epoch(fz["stop_utc"]):
            rec.setdefault("skipped", []).append(phase)
            G.dump(out / "setup.json", rec)
            continue
        rc = child(phase, rec["weights"][model]["dir"]).wait()
        assert rc == 0, f"phase {phase} exited {rc}"
    rec["status"] = "done"
    rec["finished_utc"] = utc()
    G.dump(out / "setup.json", rec)


if __name__ == "__main__":
    main()
