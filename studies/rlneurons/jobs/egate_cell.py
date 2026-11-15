"""Entropy-gated temperature cells (specs/SPEC_egate.md): several arms of one model on one problem set in one engine. Every
request runs at temperature 1.0 / top-p 1.0; the logits processor lib/egate.py sharpens the positions its arm names.

    bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.egate_cell --model base
        --set math500 --n 100 --seed 61000000 --h0 auto --arms t1=off:1 hi6=hi:0.6 lo6=lo:0.6 all6=all:0.6 rnd6=rnd:0.6
        --commit $(git rev-parse HEAD)

  --arms    name=mode:t_low. mode: off (temperature 1.0 everywhere), hi (logits / t_low where the next-token entropy H > h0),
            lo (where H <= h0), all (everywhere: constant temperature t_low through the same code), rnd (at random positions,
            with the share of positions that have H > h0).
  --h0      the threshold in nats, or auto: before the arms, the first --calib-n problems are sampled at temperature 1.0 for
            --calib-tokens tokens each (seed + 900000 + index), and h0 is the --q quantile of their positions' entropies.
  --rnd-share  the probability of the rnd arms; needed only with a numeric --h0 (with auto it is the measured share above h0).
  --model, --model-path, --model-label, --set, --n, --seed, --samples, --max-tokens, --commit: as in run_cell.py. The prompt
            is always the cue. Sample s of problem i has seed + 10000 * s + i in every arm.
  --first-sample, --shard i/k  to split one cell over several boxes: the samples first-sample .. first-sample + samples - 1, and
            every k-th problem of the set starting at the i-th. With auto, the calibration uses the shard's first problems.

Writes to --out (default $OUT_DIR): answers.jsonl (run_cell's row plus the fields arm and egate) and metrics.json (per arm:
rows, right under grader v3, cap hits, rule-A loops, generated tokens, and the processor's counts: positions, share sharpened,
mean entropy). Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time
from importlib import metadata

from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.jobs.run_cell import D4, LOG_1E2, LOG_1E3, MODELS, PINS, problems
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

CALIB_ARM = 31                                           # the processor's count row of the calibration requests

ap = argparse.ArgumentParser()
ap.add_argument("--model", choices=sorted(MODELS))
ap.add_argument("--model-path")
ap.add_argument("--model-label")
ap.add_argument("--set", required=True, choices=("math500", "hard328"))
ap.add_argument("--arms", required=True, nargs="+")
ap.add_argument("--h0", required=True)
ap.add_argument("--q", type=float, default=0.8)
ap.add_argument("--calib-n", type=int, default=50)
ap.add_argument("--calib-tokens", type=int, default=2000)
ap.add_argument("--rnd-share", type=float)
ap.add_argument("--max-tokens", type=int, default=None)
ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--n", type=int, default=None)
ap.add_argument("--samples", type=int, default=1)
ap.add_argument("--first-sample", type=int, default=0)
ap.add_argument("--shard", default="0/1")
ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
ap.add_argument("--commit", required=True)


def selftest(E, device):
    """The gate on planted rows: a flat row (H = ln 8) and a peaked row (H near 0), threshold 1.0."""
    import torch
    flat, peaked = torch.zeros(8), torch.tensor([20.0, 0, 0, 0, 0, 0, 0, 0])
    logits = torch.stack([flat + torch.arange(8) * 0.1, peaked, flat + torch.arange(8) * 0.1, peaked, peaked, peaked]).to(device)
    mode = torch.tensor([E.HI, E.HI, E.LO, E.LO, E.OFF, -1.0], device=device)
    t_low, thr = torch.full((6,), 0.5, device=device), torch.full((6,), 1.0, device=device)
    out, h, sharp = E.gate(logits.clone(), mode, t_low, thr, torch.ones(6, device=device))
    assert sharp.tolist() == [True, False, False, True, False, False], sharp.tolist()
    assert h[0] > 1.0 > h[1], h.tolist()
    for i, s in enumerate(sharp.tolist()):
        assert torch.allclose(out[i], logits[i] * (2.0 if s else 1.0)), i
    rnd = torch.full((6,), float(E.RND), device=device)
    _, _, sharp = E.gate(logits.clone(), rnd, t_low, torch.full((6,), 0.2, device=device), torch.tensor([0.1, 0.3, 0.19, 0.21, 0.0, 0.9], device=device))
    assert sharp.tolist() == [True, False, True, False, True, False], sharp.tolist()
    assert E.percentile([0, 8, 0, 2], 0.8) == 2 * E.BIN and E.percentile([0, 8, 0, 2], 0.81) == 4 * E.BIN


def main():
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    assert (a.model is None) == bool(a.model_path) == bool(a.model_label), "give --model, or --model-path with --model-label"
    model = a.model or a.model_label
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    arms = []
    for spec in a.arms:
        m = re.fullmatch(r"(\w+)=(off|hi|lo|all|rnd):([0-9.]+)", spec)
        assert m, f"arm {spec!r} is not name=mode:t_low"
        arms.append((m[1], m[2], float(m[3])))
    assert len({n for n, _, _ in arms}) == len(arms) < CALIB_ARM, "arm names repeat, or too many arms"
    auto = a.h0 == "auto"
    assert auto or a.rnd_share is not None or all(md != "rnd" for _, md, _ in arms), "a rnd arm with a numeric --h0 needs --rnd-share"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows_path, mpath = out / "answers.jsonl", out / "metrics.json"
    assert not rows_path.exists(), f"{rows_path} exists: one fresh directory per run"

    fz = json.loads((D4 / "frozen4.json").read_text())
    cap = a.max_tokens or fz["cap"]
    shard, n_shards = map(int, a.shard.split("/"))
    probs = problems(a.set, fz)[: a.n][shard::n_shards]
    pre = fz["prefill_ids"]
    versions = {k: metadata.version(k) for k in PINS}
    assert versions == PINS, f"package versions {versions} differ from the study's {PINS}: run setup_vllm.sh first"
    repo, _, rev = fz["models"][MODELS[a.model]] if a.model else (None, None, None)
    m = {"status": "starting", "config": {**vars(a), "max_tokens": cap, "out": str(out), "model_repo": repo, "model_revision": rev,
                                         "tokenizer": fz["tokenizer"], "prefix_ids": pre, "seed_rule": "seed + 10000 * sample + index",
                                         "n_problems": len(probs)},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "versions": versions, "started_utc": J.utc()}

    def write():
        m["updated_utc"] = J.utc()
        G.dump(mpath, m)

    write()
    from huggingface_hub import snapshot_download
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(tok_dir)
    assert tok.decode(pre) == fz["prefill_text"]
    pids = [S.render_ids(tok, p["problem"]) for p in probs]
    assert max(len(p) for p in pids) + len(pre) <= 2048, "a prompt is longer than 2,048 tokens"
    assert 1 <= a.samples and max(int(p["index"]) for p in probs) < 1000, "seeds of two requests would collide"

    model_dir = a.model_path or snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
    os.environ.update(G.ENGINE_ENV)
    os.environ["VLLM_ENABLE_V1_MULTIPROCESSING"] = "0"          # the engine in this process: EntropyGate.live is its processor
    from studies.rlneurons.lib import egate as E
    t_load = time.time()
    engine = J.VllmEngine(model_dir, tok_dir, 2048 + cap, logits_processors=[E.EntropyGate])
    gate = E.EntropyGate.live
    assert gate is not None and engine.engine.vllm_config.use_v2_model_runner, "the processor is not in this process's engine"
    selftest(E, gate.dev.device)
    m["engine"] = {**engine.info, "load_s": time.time() - t_load, "model_dir": model_dir, "tok_dir": tok_dir}
    m["status"] = "running"
    write()

    def sampling(mode, t_low, thr, arm):
        return {"temperature": 1.0, "top_p": 1.0, "repetition_penalty": 1.0, "extra_args": {"egate": [mode, t_low, thr, arm]}}

    if auto:
        t_cal = time.time()
        for p, ids in list(zip(probs, pids))[: a.calib_n]:
            engine.add(f"calib|{p['index']}", ids + pre, sampling(E.OFF, 1.0, 0.0, CALIB_ARM), a.seed + 900000 + int(p["index"]), a.calib_tokens)
        while engine.has_unfinished():
            engine.step()
        cal = gate.stats()[CALIB_ARM]
        h0 = E.percentile(cal["hist"], a.q)
        share = sum(cal["hist"][round(h0 / E.BIN):]) / cal["positions"]
        m["calibration"] = {"problems": min(a.calib_n, len(probs)), "tokens_each": a.calib_tokens, "q": a.q, "positions": cal["positions"],
                            "mean_entropy": cal["mean_entropy"], "hist_bin_nats": E.BIN, "hist": cal["hist"], "seconds": time.time() - t_cal}
    else:
        h0, share = float(a.h0), a.rnd_share
    m["h0"], m["rnd_share"] = h0, share
    write()

    def arm_args(k, mode, t_low):
        return {"off": [E.OFF, 1.0, 0.0, k], "hi": [E.HI, t_low, h0, k], "lo": [E.LO, t_low, h0, k], "all": [E.HI, t_low, -1.0, k],
                "rnd": [E.RND, t_low, share, k]}[mode]

    reqs = [{"rid": f"{name}|{p['index']}|{s}", "cell": f"{model}_cue_{a.set}_egate_{name}", "bench": a.set, "idx": int(p["index"]),
             "sample": s, "uid": p["unique_id"], "ids": ids + pre, "n_prompt": len(ids), "prefix_ids": pre, "prefix_kind": "opening",
             "seed": a.seed + 10000 * s + int(p["index"]), "sampling": sampling(*arm_args(k, mode, t_low)), "max_tokens": cap,
             "gold": p["answer"], "arm": name}
            for k, (name, mode, t_low) in enumerate(arms) for s in range(a.first_sample, a.first_sample + a.samples) for p, ids in zip(probs, pids)]
    live = {r["rid"]: r for r in reqs}
    for r in reqs:
        engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"])
    t_gen = time.time()
    c = {name: {"n": 0, "correct_v3": 0, "cap_hits": 0, "loop_A": 0, "generated_tokens": 0} for name, _, _ in arms}

    def counts():
        st = gate.stats()
        for k, (name, _, _) in enumerate(arms):
            if k in st:
                c[name].update(positions=st[k]["positions"], share_sharpened=st[k]["sharpened"] / st[k]["positions"],
                               mean_entropy=st[k]["mean_entropy"])
        done = sum(v["generated_tokens"] for v in c.values())
        sec = time.time() - t_gen
        m["arms"] = c
        m["counts"] = {"n": sum(v["n"] for v in c.values()), "n_planned": len(reqs), "generated_tokens": done, "generation_s": sec,
                       "tokens_per_s": done / max(sec, 1e-9)}
        write()

    with open(rows_path, "a") as f:
        while engine.has_unfinished():
            for rid, out_ids, lps, fr in engine.step():
                req = live.pop(rid)
                rec = J.record(tok, req, out_ids, lps, fr)
                rec.update(R.grade_v3(req["gold"], rec["text"]))
                n_gen = rec["n_new"]
                rec.update(n_tok_p_lt_1e2=sum(1 for x in lps[:n_gen] if x < LOG_1E2), n_tok_p_lt_1e3=sum(1 for x in lps[:n_gen] if x < LOG_1E3),
                           prompt=tok.decode(req["ids"][: req["n_prompt"]], skip_special_tokens=False), model=model, prompt_arm="cue",
                           arm=req["arm"], egate=req["sampling"]["extra_args"]["egate"])
                f.write(json.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
                v = c[req["arm"]]
                v["n"] += 1
                v["correct_v3"] += rec["score_v3"]
                v["cap_hits"] += int(rec["cap_hit"])
                v["loop_A"] += int(rec["loop_A"])
                v["generated_tokens"] += rec["n_new"]
                counts()
    assert not live, f"{len(live)} requests did not finish"
    counts()
    m["entropy_hist"] = {name: gate.stats()[k]["hist"] for k, (name, _, _) in enumerate(arms)}
    m["memory"] = engine.memory()
    m["status"] = "done"
    m["wall_s"] = time.time() - t0
    write()
    print(json.dumps({k: m[k] for k in ("status", "h0", "rnd_share", "arms", "counts", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
