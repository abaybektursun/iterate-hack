"""xreward Part 1 (specs/SPEC_xreward.md): top-8 singular subspaces of the differences of seven RL-Zero models and Think-SFT from the
Olmo 3 base, and their pairwise overlaps, per layer matrix. Weights only: no forward pass. One tensor at a time.

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.rlneurons.jobs.xreward_overlap --commit $(git rev-parse HEAD)"

  --steps    also the step-100 checkpoint of each of the seven RL runs (STEP100; downloaded to /tmp, not to the model cache).
  --layers   comma list of layers (smoke: --layers 0,31); default all.
  --out      default $OUT_DIR; one fresh directory per run.
  --selftest only the instrument check (synthetic matrices, CPU ok). Every run does it first and stops if a check fails.

Per layer matrix and key (a model's difference d = model - base in float32; `base_w` is the base matrix itself): norm, top8_share,
and the top 8 left vectors U and right vectors V (wsp_delta_anatomy.spectrum). Per unordered pair: cos, overlap_left =
||Ua^T Ub||_F^2 / 8, overlap_right. Per ordered pair a>b ("cap": the share of a's squared norm inside b's top-8 subspace):
cap_left = ||Ub^T da||^2 / ||da||^2, cap_right = ||da Vb||^2 / ||da||^2, cap_both = ||Ub^T da Vb||^2 / ||da||^2.

Writes run.json and metrics.json (one row per matrix, rewritten every 16). Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import pathlib
import re
import sys
import time

import torch

from studies.rlneurons.jobs.wsp_delta_anatomy import K, MATS, dump, fro, index, kind, load, order, spectrum, utc

MODELS = {"base": ("allenai/Olmo-3-1025-7B", "a81bae42db3975be1671e27b9c9a56da1a9f980f"),
          "math31": ("allenai/Olmo-3.1-7B-RL-Zero-Math", "364820b002fc8e81d11a81c7fc9dd6b49c83cd05"),
          "code31": ("allenai/Olmo-3.1-7B-RL-Zero-Code", "1ca3bb30f0e51b7ef05f7d0fefcf0e6b14eefc90"),
          "math30": ("allenai/Olmo-3-7B-RL-Zero-Math", "dee26a4074b88215cd1326472e1ab14d0259d892"),
          "code30": ("allenai/Olmo-3-7B-RL-Zero-Code", "a961af69d75f9c52b3ae4db7b1664d890229b7ca"),
          "if30": ("allenai/Olmo-3-7B-RL-Zero-IF", "3cae007c5324a9a06ee6780f03b848bc7b8fd440"),
          "general30": ("allenai/Olmo-3-7B-RL-Zero-General", "24e5814cb36944d3eb36a49679d02c2b3bb46195"),
          "mix30": ("allenai/Olmo-3-7B-RL-Zero-Mix", "73b2b1a50d94aec859e22c9b4a524416b5a3a739"),
          "think_sft": ("allenai/Olmo-3-7B-Think-SFT", "6ff857587e040d6d523a3d5f3a56e918f5401d66")}
STEP100 = {"math31_s100": ("allenai/Olmo-3.1-7B-RL-Zero-Math", "0a45720ccbf23c0aa255a28119787538a48dd56b"),      # branch step_0100
           "code31_s100": ("allenai/Olmo-3.1-7B-RL-Zero-Code", "0757ff941fe4c90f23b8d28780976102234ba1fa"),      # branch step_100, as the rest
           "math30_s100": ("allenai/Olmo-3-7B-RL-Zero-Math", "3315e80ceb281ae2e6a20bd09e8594ba52d4f312"),
           "code30_s100": ("allenai/Olmo-3-7B-RL-Zero-Code", "3c29f35610c9a0aef588736542c88911cc4094e8"),
           "if30_s100": ("allenai/Olmo-3-7B-RL-Zero-IF", "fcc5f4aa422406d99660df7ee148ade531f2ddca"),
           "general30_s100": ("allenai/Olmo-3-7B-RL-Zero-General", "1af5061a0bb609d7b1785133bfeb93bf4dbdb06d"),
           "mix30_s100": ("allenai/Olmo-3-7B-RL-Zero-Mix", "5dfed3f73944d389f888506701e9d44f370b9f18")}


def compare(ds):
    """ds: {key: matrix [m, n] float32} -> (per-key stats, per-pair stats). A zero matrix gets norm 0 and no pairs."""
    sp, st = {}, {}
    for k, d in ds.items():
        n = fro(d)
        st[k] = {"norm": n}
        if n:
            s, U, V = spectrum(d)
            st[k]["top8_share"] = (s[:K] ** 2).sum().item() / (s ** 2).sum().item()
            sp[k] = (d.double(), n, U, V)
    pairs = {}
    for a, b in itertools.combinations(sp, 2):
        (da, na, Ua, Va), (db, nb, Ub, Vb) = sp[a], sp[b]
        pairs[f"{a}|{b}"] = {"cos": (da * db).sum().item() / (na * nb),
                             "overlap_left": ((Ua.T @ Ub) ** 2).sum().item() / K, "overlap_right": ((Va.T @ Vb) ** 2).sum().item() / K}
    for a, b in itertools.permutations(sp, 2):
        (da, na, _, _), (_, _, Ub, Vb) = sp[a], sp[b]
        L = Ub.T @ da
        pairs[f"{a}>{b}"] = {"cap_left": (L ** 2).sum().item() / na ** 2, "cap_right": ((da @ Vb) ** 2).sum().item() / na ** 2,
                             "cap_both": ((L @ Vb) ** 2).sum().item() / na ** 2}
    return st, pairs


def selftest(dev):
    g = torch.Generator().manual_seed(0)
    rn = lambda *s: torch.randn(*s, generator=g)
    m, n = 96, 128
    P, Q = torch.linalg.qr(rn(m, K))[0], torch.linalg.qr(rn(n, K))[0]
    planted = lambda: P @ torch.diag(5 + rn(K).abs()) @ torch.linalg.qr(rn(K, K))[0] @ Q.T      # same subspaces, different mixing
    ds = {"a": planted() + 1e-3 * rn(m, n), "b": planted() + 1e-3 * rn(m, n), "c": rn(m, n), "zero": torch.zeros(m, n)}
    st, p = compare({k: v.to(dev) for k, v in ds.items()})
    res = []

    def check(what, ok, detail):
        res.append(bool(ok))
        print(f"selftest {'PASS' if ok else 'FAIL'}: {what}: {detail}", flush=True)

    ab, ac = p["a|b"], p["a|c"]
    check("two differences with one planted rank-8 subspace and different mixing", ab["overlap_left"] > 0.99 and ab["overlap_right"] > 0.99
          and p["a>b"]["cap_both"] > 0.99 and abs(ab["cos"]) < 0.9, f"overlap {ab['overlap_left']:.4f} {ab['overlap_right']:.4f}, cap_both {p['a>b']['cap_both']:.4f}, cos {ab['cos']:.3f}")
    check("planted against an independent Gaussian: overlap near 8/dimension", ac["overlap_left"] < 3 * K / m and ac["overlap_right"] < 3 * K / n
          and p["a>c"]["cap_both"] < 0.05, f"left {ac['overlap_left']:.4f} (8/{m} = {K / m:.4f}), right {ac['overlap_right']:.4f} (8/{n} = {K / n:.4f}), cap_both {p['a>c']['cap_both']:.4f}")
    check("a zero difference has no pairs", st["zero"] == {"norm": 0.0} and not any("zero" in k for k in p), f"{st['zero']}")
    assert all(res), "selftest failed"
    print(f"selftest: all {len(res)} checks passed on {dev}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--layers", default=None)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--steps", action="store_true")
    a = ap.parse_args()
    models = {**MODELS, **(STEP100 if a.steps else {})}
    t0 = time.time()
    torch.set_grad_enabled(False)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    selftest(dev)
    if a.selftest:
        return
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), f"{out / 'metrics.json'} exists: one fresh directory per run"
    info = {"status": "running", "commit": a.commit, "command": "python -m studies.rlneurons.jobs.xreward_overlap " + " ".join(sys.argv[1:]),
            "job_id": os.environ.get("JOB_ID"), "models": {k: {"repo": r, "revision": v} for k, (r, v) in models.items()}, "k": K,
            "torch": torch.__version__, "device": torch.cuda.get_device_name(0) if dev.type == "cuda" else "cpu", "started_utc": utc()}
    dump(out / "run.json", info)

    from huggingface_hub import snapshot_download
    dirs = {k: snapshot_download(r, revision=v, allow_patterns=["*.safetensors", "*.json"], cache_dir="/tmp/hf_steps" if k in STEP100 else None)
            for k, (r, v) in models.items()}
    idx = index(dirs)
    names = [n for n in sorted(idx["base"], key=order) if kind(n)[0] in MATS]
    if a.layers is not None:
        keep = {int(x) for x in a.layers.split(",")}
        names = [n for n in names if kind(n)[1] in keep]
    keys = [k for k in models if k != "base"] + ["base_w"]
    print(f"{len(names)} layer matrices, {len(keys)} keys, device {dev}, download and index {time.time() - t0:.0f}s", flush=True)
    rows = []
    for i, name in enumerate(names):
        t1 = time.time()
        base = load(idx, "base", name, dev).float()
        ds = {k: load(idx, k, name, dev).float() - base for k in models if k != "base"}
        ds["base_w"] = base
        st, pairs = compare(ds)
        mod, layer = kind(name)
        rows.append({"name": name, "module": mod, "layer": layer, "shape": list(base.shape), "key": st, "pair": pairs})
        if (i + 1) % 16 == 0 or i + 1 == len(names):
            dump(out / "metrics.json", {"n_done": i + 1, "n": len(names), "keys": keys, "k": K, "rows": rows}, "rows")
        print(f"[{i + 1}/{len(names)}] {name} {time.time() - t1:.1f}s", flush=True)
    info.update(status="done", ended_utc=utc(), wall_s=time.time() - t0)
    dump(out / "run.json", info)


if __name__ == "__main__":
    main()
