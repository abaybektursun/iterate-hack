"""xchannel (specs/SPEC_xchannel.md): do RL's top directions in the residual stream form one small subspace across layers?
Weights only: no forward pass.

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.rlneurons.jobs.xchannel --commit $(git rev-parse HEAD)"

Per layer matrix, 8 unit directions in the residual stream (dimension 4096):
  writers `o`, `down`: the top 8 left singular vectors, times the gain of the layer norm that follows the writer (as jobs/xlisten.py)
  readers `q`, `k`, `v`, `gate`, `up`: the top 8 right singular vectors
for three sets: `rl` (of RL-Zero Math 3.1 - base), `basew` (of the base matrix itself), `rand` (orthonormal Gaussian, seed 0).
Each matrix's 8 directions are orthonormalised (QR), so overlap(A, B) = ||A^T B||_F^2 / 8 is 1 for one subspace and 8 / 4096 by chance.

Writes run.json and metrics.json to --out (default $OUT_DIR). Per set:
  write_to_later_read   mean overlap of a writer's subspace with the readers' subspaces of every later layer (and `next`: the next layer only)
  write_to_write, read_to_read   mean overlap between different layers' writers, readers
  participation         (sum s^2)^2 / sum s^4 of the stacked directions of all matrices [4096, 8 * n]: the number of dimensions they fill
  dims_for_half, dims_for_90   the number of top dimensions holding 50 % and 90 % of the stack's squared norm
  by_distance           write_to_later_read by layer distance 1, 2, 4, 8, 16
  kept_by_dims (top level)   for the readers and for the writers: the share of the squared norm of RL's top-8 additions that the best
                        m-dimensional residual subspace keeps, m = 8 ... 512 (the cumulated spectrum of the stacked directions times
                        their singular values; writers without the norm gain, as the addition is in the matrix), and the same
                        with each matrix's directions replaced by random orthonormal ones (`rand`)
Every run does the selftest first. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys
import time

import torch

from studies.rlneurons.jobs.wsp_delta_anatomy import K, MODELS, dump, index, load, spectrum, utc
from studies.rlneurons.jobs.xlisten import NORM, READERS, WRITERS, name

SETS = ("rl", "basew", "rand")
ortho = lambda C: torch.linalg.qr(C.double()).Q


def stats(B, meta):
    """B [n, d, K]: orthonormal bases; meta: (layer, 'w' or 'r') per basis -> the summary of one set"""
    n, d, k = B.shape
    flat = B.permute(1, 0, 2).reshape(d, n * k)
    O = ((flat.T @ flat) ** 2).reshape(n, k, n, k).sum((1, 3)) / k                           # [n, n] overlaps
    layer = torch.tensor([m[0] for m in meta], device=B.device)
    w = torch.tensor([m[1] == "w" for m in meta], device=B.device)
    dist = layer[None] - layer[:, None]                                                      # column layer - row layer
    wr = w[:, None] & ~w[None]
    mean = lambda mask: O[mask].mean().item()
    s2 = torch.linalg.svdvals(flat) ** 2
    cum = torch.cumsum(s2, 0) / s2.sum()
    return {"write_to_later_read": mean(wr & (dist > 0)), "next": mean(wr & (dist == 1)),
            "write_to_write": mean(w[:, None] & w[None] & (dist != 0)), "read_to_read": mean(~w[:, None] & ~w[None] & (dist != 0)),
            "by_distance": {str(j): mean(wr & (dist == j)) for j in (1, 2, 4, 8, 16) if (wr & (dist == j)).any()},
            "participation": (s2.sum() ** 2 / (s2 ** 2).sum()).item(), "n_directions": n * k,
            "dims_for_half": int((cum < 0.5).sum()) + 1, "dims_for_90": int((cum < 0.9).sum()) + 1}


def selftest(dev):
    g = torch.Generator().manual_seed(0)
    d, n = 512, 12
    shared = ortho(torch.randn(d, K, generator=g)).to(dev)
    mix = lambda: ortho(shared @ torch.randn(K, K, generator=g).double().to(dev))            # the same subspace, another basis
    meta = [(i // 2, "wr"[i % 2]) for i in range(n)]
    a = stats(torch.stack([mix() for _ in range(n)]), meta)
    b = stats(torch.stack([ortho(torch.randn(d, K, generator=g)).to(dev) for _ in range(n)]), meta)
    ok = a["write_to_later_read"] > 0.99 and a["participation"] < K + 0.01 and abs(b["write_to_later_read"] - K / d) < 0.5 * K / d and b["participation"] > 0.7 * n * K
    print(f"selftest {'PASS' if ok else 'FAIL'}: one planted subspace: overlap {a['write_to_later_read']:.4f}, participation {a['participation']:.2f}; "
          f"independent subspaces: overlap {b['write_to_later_read']:.4f} (chance {K / d:.4f}), participation {b['participation']:.1f} of {n * K}", flush=True)
    assert ok, "selftest failed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--layers", type=int, default=None, help="smoke: only the first --layers layers")
    a = ap.parse_args()
    torch.set_grad_enabled(False)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    selftest(dev)
    assert a.out and re.fullmatch(r"[0-9a-f]{40}", a.commit), (a.out, a.commit)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), f"{out / 'metrics.json'} exists: one fresh directory per run"
    t0 = time.time()
    models = {k: MODELS[k] for k in ("base", "rl_math")}
    info = {"status": "running", "commit": a.commit, "command": "python -m studies.rlneurons.jobs.xchannel " + " ".join(sys.argv[1:]),
            "job_id": os.environ.get("JOB_ID"), "models": {k: {"repo": r, "revision": v} for k, (r, v) in models.items()}, "k": K,
            "started_utc": utc()}
    dump(out / "run.json", info)
    from huggingface_hub import snapshot_download
    idx = index({k: snapshot_download(r, revision=v, allow_patterns=["*.safetensors", "*.json"]) for k, (r, v) in models.items()})
    n_layers = a.layers or 1 + max(int(m[1]) for m in (re.match(r"model\.layers\.(\d+)\.", n) for n in idx["base"]) if m)
    g = torch.Generator().manual_seed(0)
    B, meta = {s: [] for s in SETS}, []
    Wt = {(kind_, s): [] for kind_ in "wr" for s in ("rl", "rand")}                           # directions times RL's singular values
    for layer in range(n_layers):
        for kind_, mods in (("w", WRITERS), ("r", READERS)):
            for m, mod in mods.items():
                base = load(idx, "base", name(layer, mod), dev).float()
                delta = load(idx, "rl_math", name(layer, mod), dev).float() - base
                assert delta.any(), f"RL equals the base in {name(layer, mod)}"
                side = 1 if kind_ == "w" else 2                                               # spectrum -> (s, U, V)
                gn = load(idx, "base", name(layer, NORM[m]), dev).double()[:, None] if kind_ == "w" else 1.0
                sp = spectrum(delta)
                sets = {"rl": sp[side], "basew": spectrum(base)[side], "rand": torch.randn(4096, K, generator=g).to(dev)}
                Wt[kind_, "rl"].append(sp[side] * sp[0][:K])
                Wt[kind_, "rand"].append(ortho(sets["rand"]) * sp[0][:K])
                for s in SETS:
                    B[s].append(ortho(gn * sets[s].double()))
                meta.append((layer, kind_))
        print(f"layer {layer} {time.time() - t0:.0f}s", flush=True)
    res = {s: stats(torch.stack(B[s]), meta) for s in SETS}
    kept = {}
    for (kind_, s), cols in Wt.items():
        s2 = torch.linalg.svdvals(torch.cat(cols, 1)) ** 2
        cum = torch.cumsum(s2, 0) / s2.sum()
        kept.setdefault({"w": "writers", "r": "readers"}[kind_], {})[s] = {str(m): cum[m - 1].item() for m in (8, 16, 32, 64, 128, 256, 512) if m <= len(cum)}
    dump(out / "metrics.json", {"k": K, "n_layers": n_layers, "n_matrices": len(meta), "chance_overlap": K / 4096, "sets": res, "kept_by_dims": kept})
    print(kept, flush=True)
    info.update(status="done", ended_utc=utc(), wall_s=time.time() - t0)
    dump(out / "run.json", info)
    print(res, flush=True)


if __name__ == "__main__":
    main()
