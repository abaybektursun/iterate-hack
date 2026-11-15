"""xreward trace (specs/SPEC_xreward_trace.md): how strongly the top-8 directions of (model - base) are driven at every position of
the stored base + cue hard328 answers. Teacher forcing through the BASE model, no generation. One H100:

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.rlneurons.jobs.xreward_trace --commit $(git rev-parse HEAD)"
    smoke: add --n 4   (the 2 shortest cap hits after the cut and the 2 finished answers nearest 1,000 tokens)

Per layer and module (MODS: mlp.up_proj, mlp.gate_proj, self_attn.q_proj), with s, V the top-8 singular values and input-side vectors
of (model - base) for that matrix (wsp_delta_anatomy.spectrum) and x the module's input at a position:

    r = ||diag(s) V^T x|| / ||module(x)||        (module = the base Linear; ||U diag(s) V^T x|| = ||diag(s) V^T x||)

Conditions (CONDS): math31, rand0..2 (math31's s with a random orthonormal V), if30, code31.

Inputs: --answers on the Volume iterate-runs (sha256 asserted), data/rln3/hard.json, data/rln4/frozen4.json (tokenizer, cue ids).
Answers are re-tokenized (rln4_lib.encode_answer); a row whose count differs from n_new by more than 1 % is left out and listed.
Each answer is cut to its first --max-tokens tokens. Position i = the input position that predicts answer token i.

Outputs in --out (default $OUT_DIR):
  trace_<kkk>.npz   per position: tok (answer token id), char (its start character in the row's text), r_up, r_gate, r_q
                    (float16 [positions, 4 layer bands, 6 conditions], band mean of r). Per row: problem_index, offsets, cap_hit,
                    score (grader v3), n_prompt, n_full (answer tokens before the cut).
  index.json        shards, bands, conditions
  run.json          commit, command, job id, models
  metrics.json      mean r per module, band and condition (all, cap hits, finished) and per layer; counts; selftest

Every run does the instrument check first. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import sys
import time

import numpy as np
import torch

from studies.rlneurons.jobs.wsp_delta_anatomy import K, dump, index, kind, load, order, spectrum, utc
from studies.rlneurons.jobs.xreward_overlap import MODELS
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
ANSWERS = "/runs/abaybektursun-1114-151534-e72c/answers.jsonl"
ANSWERS_SHA = "4a3cc0bf4596e5f8282b323637daf9cf1ede4837446ef001cea7b7c42d3f421b"
MODS = ("up", "gate", "q")
DONORS = ("math31", "if30", "code31")
CONDS = ("math31", "rand0", "rand1", "rand2", "if30", "code31")
BANDS = ((0, 8), (8, 16), (16, 24), (24, 32))
TOL = 0.01


def scaled(s, V):
    """s [k], V [n, k] -> V diag(s) in float32, so that ||x @ result|| = ||diag(s) V^T x||"""
    return (V * s[:V.shape[1]]).float()


def rand_v(n, seed, name):
    g = torch.Generator().manual_seed(int.from_bytes(hashlib.sha256(f"{seed}:{name}".encode()).digest()[:4], "big"))
    return torch.linalg.qr(torch.randn(n, K, generator=g, dtype=torch.float64))[0]


def drive(x, y, P):
    """x [T, n] module input, y [T, m] module output, P [n, C * K] the conditions' scaled vectors side by side -> r [T, C]"""
    p = (x.float() @ P).view(x.shape[0], -1, K)
    return torch.linalg.vector_norm(p, dim=-1) / torch.linalg.vector_norm(y.float(), dim=-1)[:, None]


class Trace:
    """Forward hooks on the chosen Linear modules; after a forward pass, .r[mod] is [T, layers, C]."""

    def __init__(self, model, P):
        self.P, self.got = P, {}
        self.handles = [model.get_submodule(name[:-len(".weight")]).register_forward_hook(self.hook(name)) for name in P]

    def hook(self, name):
        def f(_, inp, out):
            assert name not in self.got, f"{name} ran twice in one pass"
            self.got[name] = drive(inp[0][0], out[0], self.P[name])
        return f

    def pop(self):
        assert set(self.got) == set(self.P), "a hooked module did not run"
        res = {}
        for mod in MODS:
            names = sorted((n for n in self.got if kind(n)[0] == mod), key=lambda n: kind(n)[1])
            res[mod] = torch.stack([self.got[n] for n in names], 1)
        self.got = {}
        return res


def selftest(dev):
    g = torch.Generator().manual_seed(0)
    n, m, T = 64, 96, 5
    lin = torch.nn.Linear(n, m, bias=False)
    lin.weight.data = torch.randn(m, n, generator=g)
    d = torch.randn(m, K, generator=g, dtype=torch.float64) @ torch.diag(torch.arange(K, 0, -1, dtype=torch.float64)) @ \
        torch.linalg.qr(torch.randn(n, K, generator=g, dtype=torch.float64))[0].T
    s, U, V = spectrum(d)
    name = "model.layers.0.mlp.up_proj.weight"
    holder = torch.nn.Module()
    holder.model = torch.nn.Module()
    holder.model.layers = torch.nn.ModuleList([torch.nn.Module()])
    holder.model.layers[0].mlp = torch.nn.Module()
    holder.model.layers[0].mlp.up_proj = lin
    holder = holder.to(dev)
    tr = Trace(holder, {name: torch.cat([scaled(s, V), scaled(s, rand_v(n, 0, name))], 1).to(dev)})
    a = torch.randn(T, K, generator=g, dtype=torch.float64)
    x_in = (a @ V.T).float().to(dev)
    Q = torch.linalg.qr(torch.cat([V, torch.randn(n, T, generator=g, dtype=torch.float64)], 1))[0][:, K:]      # orthogonal to V
    x_out = Q.T.float().to(dev)
    res = []

    def check(what, ok, detail):
        res.append(bool(ok))
        print(f"selftest {'PASS' if ok else 'FAIL'}: {what}: {detail}", flush=True)

    Wd, xd = lin.weight.data.double().cpu(), x_in.double().cpu()
    lin(x_in[None])
    got = tr.got.pop(name)[:, 0].double().cpu()
    want = torch.linalg.vector_norm(a * s[:K], dim=-1) / torch.linalg.vector_norm(a @ V.T @ Wd.T, dim=-1)
    edit = torch.linalg.vector_norm(xd @ d.T, dim=-1) / torch.linalg.vector_norm(xd @ Wd.T, dim=-1)
    check("x inside V: r equals the analytic value and ||d x|| / ||W x||", torch.allclose(got, want, rtol=1e-4) and torch.allclose(got, edit, rtol=1e-4),
          f"got {got[:3].tolist()}, analytic {want[:3].tolist()}, from d {edit[:3].tolist()}")
    lin(x_out[None])
    r = tr.got.pop(name).double().cpu()
    check("x orthogonal to V: r is 0, and the random V's r is not", r[:, 0].abs().max() < 1e-5 and r[:, 1].min() > 1e-3,
          f"max r {r[:, 0].abs().max():.2e}, min random r {r[:, 1].min():.3f}")
    for h in tr.handles:
        h.remove()
    assert all(res), "selftest failed"
    return {"checks": len(res), "passed": True}


def build(tok, fz, row, prob, max_tokens):
    assert row["unique_id"] == prob["unique_id"] and int(prob["index"]) == row["problem_index"]
    pids = S.render_ids(tok, prob["problem"])
    assert len(pids) == row["prompt_n_tokens"], ("prompt length", row["problem_index"])
    ids, offs = R.encode_answer(tok, row["text"], fz["prefill_text"], fz["prefill_ids"])
    assert row["n_prefix"] == len(fz["prefill_ids"]) and ids[:3] == fz["prefill_ids"], ("cue", row["problem_index"])
    n = min(len(ids), max_tokens)
    return {"idx": int(row["problem_index"]), "seq": pids + [int(i) for i in ids[:n]], "n_prompt": len(pids), "n": n, "n_full": len(ids),
            "char": [a for a, _ in offs[:n]], "cap_hit": bool(row["cap_hit"]), "score": int(row["score_v3"]),
            "retok_diff": len(ids) - 3 - int(row["n_new"]), "n_new": int(row["n_new"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--answers", default=ANSWERS)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--n", type=int, default=None, help="smoke: n/2 cap hits and n/2 finished answers")
    ap.add_argument("--max-tokens", type=int, default=6000)
    ap.add_argument("--shard-positions", type=int, default=400_000)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    torch.set_grad_enabled(False)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    st = selftest(dev)
    if a.selftest:
        return
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "index.json").exists(), f"{out}/index.json exists: one fresh directory per run"
    keys = ("base",) + DONORS
    info = {"status": "running", "commit": a.commit, "command": "python -m studies.rlneurons.jobs.xreward_trace " + " ".join(sys.argv[1:]),
            "job_id": os.environ.get("JOB_ID"), "models": {k: {"repo": MODELS[k][0], "revision": MODELS[k][1]} for k in keys},
            "answers": a.answers, "answers_sha256": ANSWERS_SHA, "torch": torch.__version__, "device": torch.cuda.get_device_name(0),
            "started_utc": utc(), "selftest": st}
    dump(out / "run.json", info)

    assert hashlib.sha256(pathlib.Path(a.answers).read_bytes()).hexdigest() == ANSWERS_SHA, f"{a.answers} is not the expected file"
    rows = [json.loads(l) for l in pathlib.Path(a.answers).read_text().splitlines()]
    fz = json.loads((STUDY / "data" / "rln4" / "frozen4.json").read_text())
    hard = json.loads((STUDY / "data" / "rln3" / "hard.json").read_text())

    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    seqs = [build(tok, fz, r, hard[r["problem_index"]], a.max_tokens) for r in rows]
    left_out = [s["idx"] for s in seqs if abs(s["retok_diff"]) > TOL * s["n_new"]]
    seqs = sorted((s for s in seqs if s["idx"] not in left_out), key=lambda s: (s["n"], s["idx"]))
    if a.n is not None:
        cap = [s for s in seqs if s["cap_hit"]][:a.n // 2]
        fin = sorted((s for s in seqs if not s["cap_hit"]), key=lambda s: abs(s["n"] - 1000))[:a.n - a.n // 2]
        seqs = sorted(cap + fin, key=lambda s: (s["n"], s["idx"]))
    print(f"{len(seqs)} answers, {sum(s['n'] for s in seqs)} positions, left out (re-tokenized count off by over 1 %): {left_out}", flush=True)

    dirs = {k: snapshot_download(MODELS[k][0], revision=MODELS[k][1], allow_patterns=["*.safetensors", "*.json"]) for k in keys}
    idx = index(dirs)
    names = [n for n in sorted(idx["base"], key=order) if kind(n)[0] in MODS]
    assert len(names) == 32 * len(MODS), len(names)
    P, sv = {}, {}
    for i, name in enumerate(names):
        base = load(idx, "base", name, dev).float()
        cols = {}
        for k in DONORS:
            s, _, V = spectrum(load(idx, k, name, dev).float() - base)
            cols[k] = scaled(s, V)
            sv[f"{name}|{k}"] = s[:K].tolist()
            if k == "math31":
                for j in range(3):
                    cols[f"rand{j}"] = scaled(s, rand_v(V.shape[0], j, name).to(dev))
        P[name] = torch.cat([cols[c] for c in CONDS], 1)
        if (i + 1) % 16 == 0:
            print(f"[{i + 1}/{len(names)}] vectors of {name}, {time.time() - t0:.0f}s", flush=True)
    del base

    model = AutoModelForCausalLM.from_pretrained(dirs["base"], dtype=torch.bfloat16).to(dev).eval()
    tr = Trace(model, P)
    info.update(load_s=time.time() - t0, transformers=__import__("transformers").__version__)
    dump(out / "run.json", info)

    ix = {"shards": [], "mods": MODS, "conds": CONDS, "bands": BANDS, "left_out": left_out,
          "arrays": ["tok", "char", "r_up", "r_gate", "r_q"], "per_row": ["problem_index", "offsets", "cap_hit", "score", "n_prompt", "n_full"]}
    groups = ("all", "cap_hit", "finished")
    tot = {g: {m: torch.zeros(32, len(CONDS), dtype=torch.float64, device=dev) for m in MODS} for g in groups}
    cnt = {g: 0 for g in groups}
    buf, k, t_run = [], 0, time.time()

    def flush():
        nonlocal buf, k
        arrs = {f"r_{m}": np.concatenate([r[m] for _, r in buf]) for m in MODS}
        arrs["tok"] = np.concatenate([np.array(s["seq"][s["n_prompt"]:], dtype=np.int32) for s, _ in buf])
        arrs["char"] = np.concatenate([np.array(s["char"], dtype=np.int32) for s, _ in buf])
        arrs["offsets"] = np.cumsum([0] + [s["n"] for s, _ in buf]).astype(np.int64)
        for key, src in (("problem_index", "idx"), ("cap_hit", "cap_hit"), ("score", "score"), ("n_prompt", "n_prompt"), ("n_full", "n_full")):
            arrs[key] = np.array([s[src] for s, _ in buf], dtype=np.int32)
        name = f"trace_{k:03d}.npz"
        np.savez_compressed(out / name, **arrs)
        ix["shards"].append({"file": name, "answers": len(buf), "positions": int(len(arrs["tok"]))})
        dump(out / "index.json", ix)
        print(f"{utc()} {name}: {len(buf)} answers; {cnt['all']} positions in {time.time() - t_run:.0f} s", flush=True)
        buf, k = [], k + 1

    for s in seqs:
        x = torch.tensor(s["seq"][:-1], device=dev)[None]
        model(input_ids=x, use_cache=False)
        r = {m: v[s["n_prompt"] - 1:] for m, v in tr.pop().items()}                    # [n, 32, C]
        assert all(v.shape == (s["n"], 32, len(CONDS)) and torch.isfinite(v).all() for v in r.values()), ("shape or non-finite", s["idx"])
        for g in ("all", "cap_hit" if s["cap_hit"] else "finished"):
            cnt[g] += s["n"]
            for m in MODS:
                tot[g][m] += r[m].double().sum(0)
        buf.append((s, {m: torch.stack([v[:, lo:hi].mean(1) for lo, hi in BANDS], 1).cpu().numpy().astype(np.float16) for m, v in r.items()}))
        if sum(x["n"] for x, _ in buf) >= a.shard_positions:
            flush()
    if buf:
        flush()

    mean = {g: {m: (tot[g][m] / max(cnt[g], 1)).cpu() for m in MODS} for g in groups}
    metrics = {"answers": len(seqs), "positions": cnt, "left_out": left_out, "max_tokens": a.max_tokens, "conds": CONDS, "bands": BANDS,
               "what": "r = ||diag(s) V^T x|| / ||W_base x||, mean over positions (and over the layers of a band)",
               "mean_r_by_band": {g: {m: {c: [mean[g][m][lo:hi, j].mean().item() for lo, hi in BANDS] for j, c in enumerate(CONDS)} for m in MODS} for g in groups},
               "mean_r_by_layer": {m: {c: mean["all"][m][:, j].tolist() for j, c in enumerate(CONDS)} for m in MODS},
               "top8_singular_values": sv, "gpu_max_memory_gb": torch.cuda.max_memory_allocated() / 2 ** 30,
               "positions_per_s": cnt["all"] / (time.time() - t_run)}
    dump(out / "metrics.json", metrics)
    info.update(status="done", ended_utc=utc(), wall_s=time.time() - t0)
    dump(out / "run.json", info)
    print(json.dumps(metrics["mean_r_by_band"]["all"], indent=1), flush=True)


if __name__ == "__main__":
    main()
