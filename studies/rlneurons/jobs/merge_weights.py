"""Day-1 #4 (specs/DAY1_wdiff_2026-11-14.md): write theta(a) = base + a * (other - base), or the random control base + R, as a bf16
safetensors model directory that `run_cell.py --model-path` loads; and the per-tensor statistics of the difference other - base.

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.merge_weights --other rl --alpha 0.5 --rounding stochastic --dir /tmp/theta
    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.merge_weights --other rl --random --rounding stochastic --dir /tmp/theta
    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.merge_weights --other code [--cos-with-rl]

  --other    rl = allenai/Olmo-3.1-7B-RL-Zero-Math (frozen4.json), code = allenai/Olmo-3.1-7B-RL-Zero-Code (CODE below).
  --alpha    a of theta(a). a = 0 must give base and a = 1 the other model, tensor for tensor (asserted).
  --random   base + R: per tensor, R is Gaussian noise (torch generator seeded --seed, tensors in sorted name order) rescaled to the
             Frobenius norm of that tensor's other - base (asserted before rounding); R = 0 where other = base.
  --rounding float32 result to bf16: nearest (round to nearest even) or stochastic (add a uniform 16-bit integer to the float32 bits,
             then truncate; generator seeded --seed + 1). Stochastic rounding keeps the expected value base + a * delta when the
             difference is a few bf16 units in the last place.
  --dir      write the model here (one safetensors file per shard of the base, the RL model's json files: config, tokenizer).
             Omitted: statistics only, and for every point (a in POINTS, random) under both roundings the effective a and norm
             after rounding.

Statistics go to --stats (default $OUT_DIR/merge.json): per tensor numel, changed entries, ||base||, ||delta||, |delta| in bf16 units
in the last place of base; sums per tensor group and per layer; for the written point the effective a = <M - B, delta> / ||delta||^2
and ||M - B|| / ||delta|| after rounding. Fail loud: no try/except.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import time

import torch
from safetensors import safe_open
from safetensors.torch import save_file

STUDY = pathlib.Path(__file__).resolve().parents[1]
BASE_KEY, RL_KEY = "base", "s2800"                                   # keys of frozen4.json "models"
CODE = ("allenai/Olmo-3.1-7B-RL-Zero-Code", "1ca3bb30f0e51b7ef05f7d0fefcf0e6b14eefc90")
POINTS = (0.25, 0.5, 0.75, 1.25, 1.5)
ULP_EDGES = (1, 2, 4, 16)                                            # |delta| / ulp(base) buckets: <=1, (1,2], (2,4], (4,16], >16


def group(name):
    return re.sub(r"^model\.(layers\.\d+\.)?", "", name).removesuffix(".weight")


def layer(name):
    m = re.match(r"model\.layers\.(\d+)\.", name)
    return m.group(1) if m else "none"


def ulp(b):
    """Unit in the last place of each bf16 value b (float32 tensor of bf16 values): 2^(e - 8) for b = m 2^e, m in [0.5, 1)."""
    return torch.ldexp(torch.ones_like(b), torch.frexp(b).exponent - 8)


def to_bf16(x, rounding, gen):
    if rounding == "nearest":
        return x.to(torch.bfloat16)
    r = torch.randint(0, 1 << 16, x.shape, generator=gen, device=x.device, dtype=torch.int32)
    return ((x.view(torch.int32) + r) & -65536).view(torch.float32).to(torch.bfloat16)


def point(b, o, d, alpha, rand, noise_gen):
    """float32 target before rounding, and the difference it adds to b. (1 - a) b + a o, not b + a (o - b): o - b is not exact in
    float32 where a weight moves to a value 2^16 times smaller, and the endpoints must be exact."""
    if rand:
        nd = torch.linalg.vector_norm(d)
        if nd == 0:
            return b, torch.zeros_like(b)
        n = torch.randn(b.shape, generator=noise_gen, device=b.device, dtype=torch.float32)
        r = n * (nd / torch.linalg.vector_norm(n))
        assert abs(float(torch.linalg.vector_norm(r) / nd) - 1) < 1e-4, "random control: norm differs from ||delta||"
        return b + r, r
    return (1 - alpha) * b + alpha * o, alpha * d


def tensor_stats(b, d):
    ch = d != 0
    k = (d.abs() / ulp(b))[ch]
    edges = [0, *ULP_EDGES, float("inf")]
    return {"numel": b.numel(), "changed": int(ch.sum()), "base_sq": float((b * b).sum()), "delta_sq": float((d * d).sum()),
            "delta_ulp_hist": [int(((k > lo) & (k <= hi)).sum()) for lo, hi in zip(edges, edges[1:])]}


def sums(per, key):
    out = {}
    for name, s in per.items():
        g = out.setdefault(key(name), {"numel": 0, "changed": 0, "base_sq": 0.0, "delta_sq": 0.0})
        for f in g:
            g[f] += s[f]
    for g in out.values():
        g["frac_changed"] = g["changed"] / g["numel"]
        g["rel_norm"] = (g["delta_sq"] / g["base_sq"]) ** 0.5 if g["base_sq"] else None
    return out


def merge(base_dir, other_dir, alpha, rand, rounding, out_dir, seed, device, json_dir):
    """Returns the statistics; writes the model to out_dir, with the json files (config, index, tokenizer) of json_dir, unless out_dir
    is None (then every point is simulated, nothing written)."""
    base_dir, other_dir = pathlib.Path(base_dir), pathlib.Path(other_dir)
    wb = json.loads((base_dir / "model.safetensors.index.json").read_text())["weight_map"]
    wo = json.loads((other_dir / "model.safetensors.index.json").read_text())["weight_map"]
    assert wb == wo, "base and other differ in tensor names or shard layout"
    points = [(alpha, rand)] if out_dir else [(a, False) for a in POINTS] + [(None, True)]
    roundings = [rounding] if out_dir else ["nearest", "stochastic"]
    label = lambda a, r: "random" if r else f"a={a:g}"
    gens = {(label(*p), ro): (torch.Generator(device).manual_seed(seed), torch.Generator(device).manual_seed(seed + 1))
            for p in points for ro in roundings}
    acc = {k: {"dot": 0.0, "mb_sq": 0.0, "add_sq": 0.0, "add_dot_delta": 0.0} for k in gens}
    per, ident = {}, {"exact": 0, "tensors": 0}
    if out_dir:
        out_dir = pathlib.Path(out_dir)
        out_dir.mkdir(parents=True)
    for shard in sorted(set(wb.values())):
        names = sorted(n for n, s in wb.items() if s == shard)
        written = {}
        with safe_open(base_dir / shard, "pt", device="cpu") as fb, safe_open(other_dir / shard, "pt", device="cpu") as fo:
            for name in names:
                tb, to = fb.get_tensor(name), fo.get_tensor(name)
                assert tb.dtype == to.dtype == torch.bfloat16 and tb.shape == to.shape, (name, tb.dtype, to.dtype, tb.shape, to.shape)
                b, o = tb.to(device, torch.float32), to.to(device, torch.float32)
                d = o - b
                per[name] = tensor_stats(b, d)
                for p in points:
                    for ro in roundings:
                        k = (label(*p), ro)
                        x, add = point(b, o, d, p[0], p[1], gens[k][0])
                        m = to_bf16(x, ro, gens[k][1])
                        mb = m.to(torch.float32) - b
                        a = acc[k]
                        a["dot"] += float((mb * d).sum())
                        a["mb_sq"] += float((mb * mb).sum())
                        a["add_sq"] += float((add * add).sum())
                        a["add_dot_delta"] += float((add * d).sum())
                        if out_dir:
                            if not rand and alpha in (0, 1):
                                ident["tensors"] += 1
                                ident["exact"] += int(torch.equal(m, (tb if alpha == 0 else to).to(device)))
                            written[name] = m.cpu()
        if out_dir:
            save_file(written, out_dir / shard, metadata={"format": "pt"})
    if out_dir:
        assert ident["exact"] == ident["tensors"], f"a = {alpha}: {ident['tensors'] - ident['exact']} tensors differ from the endpoint"
        for f in pathlib.Path(json_dir).glob("*.json"):
            shutil.copy(f, out_dir / f.name)
    dsq = sum(s["delta_sq"] for s in per.values())
    points_out = {f"{k[0]} {k[1]}": {"effective_a": a["dot"] / dsq, "norm_ratio": (a["mb_sq"] / dsq) ** 0.5,
                                    "target_norm_ratio": (a["add_sq"] / dsq) ** 0.5, "target_cos_delta": a["add_dot_delta"] / (a["add_sq"] * dsq) ** 0.5
                                    if a["add_sq"] else None, "cos_delta": a["dot"] / (a["mb_sq"] * dsq) ** 0.5 if a["mb_sq"] else None}
                  for k, a in acc.items()}
    hist = [sum(s["delta_ulp_hist"][j] for s in per.values()) for j in range(len(ULP_EDGES) + 1)]
    return {"overall": sums(per, lambda n: "all")["all"], "delta_ulp_hist_edges": ["<=1", "(1,2]", "(2,4]", "(4,16]", ">16"], "delta_ulp_hist": hist,
            "points": points_out, "identity": ident if out_dir and not rand and alpha in (0, 1) else None,
            "groups": sums(per, group), "layers": sums(per, layer), "tensors": per}


def cosine(base_dir, x_dir, y_dir, device):
    """Cosine between x - base and y - base, overall and per tensor group, and how many entries both change (same sign)."""
    w = json.loads((pathlib.Path(base_dir) / "model.safetensors.index.json").read_text())["weight_map"]
    g = {}
    for shard in sorted(set(w.values())):
        with safe_open(pathlib.Path(base_dir) / shard, "pt", device="cpu") as fb, safe_open(pathlib.Path(x_dir) / shard, "pt", device="cpu") as fx, \
                safe_open(pathlib.Path(y_dir) / shard, "pt", device="cpu") as fy:
            for name in sorted(n for n, s in w.items() if s == shard):
                b = fb.get_tensor(name).to(device, torch.float32)
                dx, dy = fx.get_tensor(name).to(device, torch.float32) - b, fy.get_tensor(name).to(device, torch.float32) - b
                for k in (group(name), "all"):
                    t = g.setdefault(k, {"dot": 0.0, "xx": 0.0, "yy": 0.0, "x_changed": 0, "y_changed": 0, "both": 0, "both_same_sign": 0})
                    t["dot"] += float((dx * dy).sum())
                    t["xx"] += float((dx * dx).sum())
                    t["yy"] += float((dy * dy).sum())
                    t["x_changed"] += int((dx != 0).sum())
                    t["y_changed"] += int((dy != 0).sum())
                    t["both"] += int(((dx != 0) & (dy != 0)).sum())
                    t["both_same_sign"] += int((dx * dy > 0).sum())
    for t in g.values():
        t["cos"] = t["dot"] / (t["xx"] * t["yy"]) ** 0.5 if t["xx"] and t["yy"] else None
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--other", required=True, choices=("rl", "code"))
    ap.add_argument("--alpha", type=float)
    ap.add_argument("--random", action="store_true")
    ap.add_argument("--rounding", choices=("nearest", "stochastic"))
    ap.add_argument("--dir")
    ap.add_argument("--stats", default=os.path.join(os.environ.get("OUT_DIR", ""), "merge.json"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cos-with-rl", action="store_true", help="statistics only, --other code: also the cosine of Code - base with RL - base")
    a = ap.parse_args()
    if a.dir:
        assert a.rounding and ((a.alpha is None) == a.random), "--dir needs --rounding and exactly one of --alpha, --random"
    else:
        assert a.alpha is None and not a.random and not a.rounding, "statistics only: no --alpha, --random, --rounding"
    t0 = time.time()
    fz = json.loads((STUDY / "data" / "rln4" / "frozen4.json").read_text())
    base = fz["models"][BASE_KEY][0], fz["models"][BASE_KEY][2]
    other = (fz["models"][RL_KEY][0], fz["models"][RL_KEY][2]) if a.other == "rl" else CODE
    from huggingface_hub import snapshot_download
    dirs = [snapshot_download(r, revision=v, allow_patterns=["*.json", "*.safetensors"]) for r, v in (base, other)]
    rl_json = snapshot_download(fz["models"][RL_KEY][0], revision=fz["models"][RL_KEY][2], allow_patterns=["*.json"])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    res = merge(dirs[0], dirs[1], a.alpha, a.random, a.rounding, a.dir, a.seed, device, rl_json)   # RL config and tokenizer for all
    if a.cos_with_rl:
        assert a.other == "code" and not a.dir
        rl_dir = snapshot_download(fz["models"][RL_KEY][0], revision=fz["models"][RL_KEY][2], allow_patterns=["*.json", "*.safetensors"])
        res["cos_with_rl"] = cosine(dirs[0], dirs[1], rl_dir, device)
        print(json.dumps({k: v["cos"] for k, v in res["cos_with_rl"].items()}, indent=1))
    res = {"args": vars(a), "base": base, "other": other, "device": device, "torch": torch.__version__, "seconds": time.time() - t0, **res}
    pathlib.Path(a.stats).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("args", "overall", "delta_ulp_hist", "points", "identity", "seconds")}, indent=1))
    print(json.dumps({g: {k: v[k] for k in ("frac_changed", "rel_norm")} for g, v in res["groups"].items()}, indent=1))


if __name__ == "__main__":
    main()
