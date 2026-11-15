"""xlisten (specs/SPEC_xlisten.md): do the base's later layers read the directions that RL writes more strongly than other directions?
Weights only: no forward pass.

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.rlneurons.jobs.xlisten --commit $(git rev-parse HEAD)"

Writers: `o` and `down` of every layer but the last. Three sets of 8 unit directions in the residual stream per writer:
  rl     the top 8 left singular vectors of (RL-Zero Math 3.1 - base) of that matrix
  basew  the top 8 left singular vectors of the base matrix itself
  rand   8 orthonormal Gaussian directions (seed 0)
each multiplied by the gain of the layer norm that follows the writer (post_attention_layernorm for `o`, post_feedforward_layernorm
for `down`) and scaled back to unit length: Olmo 3 adds the normed output to the residual stream.
Readers: the base's `q`, `k`, `v`, `gate`, `up` of every later layer; they read the residual stream directly.
gain(c, W) = ||W c||^2 / (||W||_F^2 / 4096): 1 for a direction the reader treats as the average direction.

Writes run.json and metrics.json to --out (default $OUT_DIR): per writer and set, the mean gain over the next layer's readers
(`next`, and per reader type) and over all later layers' readers (`later`); `summary`: means over writers.
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

WRITERS = {"o": "self_attn.o_proj", "down": "mlp.down_proj"}
NORM = {"o": "post_attention_layernorm", "down": "post_feedforward_layernorm"}
READERS = {"q": "self_attn.q_proj", "k": "self_attn.k_proj", "v": "self_attn.v_proj", "gate": "mlp.gate_proj", "up": "mlp.up_proj"}
SETS = ("rl", "basew", "rand")
name = lambda layer, mod: f"model.layers.{layer}.{mod}.weight"


def gain(W, C):
    """reader W [m, d], unit columns C [d, n] -> [n]: ||W c||^2 / (||W||_F^2 / d)"""
    W = W.double()
    return ((W @ C) ** 2).sum(0) / ((W ** 2).sum() / W.shape[1])


def unit(C):
    return C / torch.linalg.vector_norm(C, dim=0)


def selftest(dev):
    g = torch.Generator().manual_seed(0)
    d = 512
    W = torch.randn(256, d, generator=g).double().to(dev)
    v = unit(torch.randn(d, 1, generator=g).double().to(dev))
    W = W + 20 * torch.randn(256, 1, generator=g).double().to(dev) @ v.T                     # a reader that listens to v
    r = unit(torch.randn(d, 64, generator=g).double().to(dev))
    gv, gr = gain(W, v).item(), gain(W, r).mean().item()
    ok = gv > 20 and 0.5 < gr < 1.5
    print(f"selftest {'PASS' if ok else 'FAIL'}: gain of a planted read direction {gv:.1f}, mean gain of 64 random directions {gr:.3f}", flush=True)
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
    info = {"status": "running", "commit": a.commit, "command": "python -m studies.rlneurons.jobs.xlisten " + " ".join(sys.argv[1:]),
            "job_id": os.environ.get("JOB_ID"), "models": {k: {"repo": r, "revision": v} for k, (r, v) in models.items()}, "k": K,
            "started_utc": utc()}
    dump(out / "run.json", info)
    from huggingface_hub import snapshot_download
    idx = index({k: snapshot_download(r, revision=v, allow_patterns=["*.safetensors", "*.json"]) for k, (r, v) in models.items()})
    n_layers = a.layers or 1 + max(int(m[1]) for m in (re.match(r"model\.layers\.(\d+)\.", n) for n in idx["base"]) if m)
    g = torch.Generator().manual_seed(0)

    cols, owner = [], []                                                                      # all directions [d, n]; (layer, writer, set) per column
    for layer in range(n_layers - 1):
        for w, mod in WRITERS.items():
            base = load(idx, "base", name(layer, mod), dev).float()
            delta = load(idx, "rl_math", name(layer, mod), dev).float() - base
            assert delta.any(), f"RL equals the base in {name(layer, mod)}"
            gn = load(idx, "base", name(layer, NORM[w]), dev).double()[:, None]
            sets = {"rl": spectrum(delta)[1], "basew": spectrum(base)[1],
                    "rand": torch.linalg.qr(torch.randn(base.shape[0], K, generator=g).double()).Q.to(dev)}
            for s in SETS:
                cols.append(unit(gn * sets[s].double()))
                owner += [(layer, w, s)] * K
        print(f"directions of layer {layer} {time.time() - t0:.0f}s", flush=True)
    C = torch.cat(cols, 1)
    G = {}                                                                                    # (reader layer, reader type) -> gains [n]
    for layer in range(1, n_layers):
        for r, mod in READERS.items():
            G[layer, r] = gain(load(idx, "base", name(layer, mod), dev).float(), C).cpu()
        print(f"readers of layer {layer} {time.time() - t0:.0f}s", flush=True)

    rows = []
    for layer in range(n_layers - 1):
        for w in WRITERS:
            row = {"layer": layer, "writer": w}
            for s in SETS:
                sel = torch.tensor([o == (layer, w, s) for o in owner])
                nxt = {r: G[layer + 1, r][sel].mean().item() for r in READERS}
                later = [G[l, r][sel].mean().item() for l in range(layer + 1, n_layers) for r in READERS]
                row[s] = {"next": sum(nxt.values()) / len(nxt), "next_by_reader": nxt, "later": sum(later) / len(later),
                          "next_per_direction": torch.stack([G[layer + 1, r][sel] for r in READERS]).mean(0).tolist()}
            rows.append(row)
    summary = {s: {k: sum(r[s][k] for r in rows) / len(rows) for k in ("next", "later")} for s in SETS}
    summary["writers_where_rl_next_exceeds_basew_next"] = sum(r["rl"]["next"] > r["basew"]["next"] for r in rows)
    summary["writers_where_rl_next_exceeds_2"] = sum(r["rl"]["next"] > 2 for r in rows)
    summary["n_writers"] = len(rows)
    dump(out / "metrics.json", {"k": K, "n_layers": n_layers, "summary": summary, "rows": rows}, "rows")
    info.update(status="done", ended_utc=utc(), wall_s=time.time() - t0)
    dump(out / "run.json", info)
    print(summary, flush=True)


if __name__ == "__main__":
    main()
