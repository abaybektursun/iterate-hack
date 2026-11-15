"""WSP-1 Part 1 (specs/SPEC_wsp1.md): anatomy of three weight deltas (rl_math, rl_code, think_sft; each model minus the Olmo 3
base) on the team runner. Weights only: no forward pass through the model. One tensor at a time (its four versions), never a whole
model in memory.

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.rlneurons.jobs.wsp_delta_anatomy --commit $(git rev-parse HEAD)"

  Double quotes, so that $(git rev-parse HEAD) expands on the laptop to the commit that gpu.py submits (the job's tree has no .git).

  --layers   comma list of layers (smoke runs: --layers 0,31); default all. The embeddings, lm_head and the final norm are always
             included (norms, unchanged share, cosine). The null always uses layer 16, whatever --layers says.
  --out      default $OUT_DIR; one fresh directory per run.
  --selftest only the instrument check (synthetic tensors, no downloads, CPU ok), then exit 0. Every run does the selftest first, on
             the run's device, and stops if a check fails.

Per tensor and delta d = model - base (float32): norm_delta, norm_base (Frobenius), rel = their ratio, unchanged = share of entries
whose stored bits equal the base's. Per layer matrix (q, k, v, o, gate, up, down): all singular values of d from a float64 eigh of the
Gram matrix on the smaller side (d d^T or d^T d, at most 4096 x 4096); top1_share and top8_share (share of the squared norm),
stable_rank (squared norm / top singular value squared); the top 8 left vectors U (output space, shape[0]) and right vectors V (input
space, shape[1]), the side that is not the Gram side recovered as d^T u / sigma or d v / sigma. Per pair of deltas: cos (Frobenius
inner product / norm product), and for layer matrices overlap_left = ||U1^T U2||_F^2 / 8 and overlap_right. Readout: for down_proj and
o_proj, the top 3 left vectors, both signs, times the base lm_head: the 15 highest tokens and the rank (0 = highest) of the cue ids.
Null, same functions: for layer 16's q_proj, up_proj and down_proj, a Gaussian delta (CPU torch.Generator, seeds 0 to 4) with the
rl_math delta's norm; mean and sample standard deviation over the seeds.

Writes to --out: run.json; metrics.json (one row per tensor, rewritten every 16 tensors; the top 16 singular values, no vectors);
summary.json (means by module type over all tensors of that type, by layer and overall over the layer matrices, a mean skips the
tensors where the stat does not exist; totals; the null; the numbers H1 to H4 refer to, no verdicts); readout.json (one row per
tensor, delta, direction and sign; the null's rows have delta "null" and a seed). Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import statistics
import struct
import sys
import tempfile
import time

import torch
from safetensors import safe_open

MODELS = {"base": ("allenai/Olmo-3-1025-7B", "a81bae42db3975be1671e27b9c9a56da1a9f980f"),
          "rl_math": ("allenai/Olmo-3.1-7B-RL-Zero-Math", "364820b002fc8e81d11a81c7fc9dd6b49c83cd05"),
          "rl_code": ("allenai/Olmo-3.1-7B-RL-Zero-Code", "1ca3bb30f0e51b7ef05f7d0fefcf0e6b14eefc90"),
          "think_sft": ("allenai/Olmo-3-7B-Think-SFT", "6ff857587e040d6d523a3d5f3a56e918f5401d66")}
DELTAS = ("rl_math", "rl_code", "think_sft")
PAIRS = (("rl_math", "rl_code"), ("rl_math", "think_sft"), ("rl_code", "think_sft"))
LAYER_MODS = {"self_attn.q_proj": "q", "self_attn.k_proj": "k", "self_attn.v_proj": "v", "self_attn.o_proj": "o",
              "mlp.gate_proj": "gate", "mlp.up_proj": "up", "mlp.down_proj": "down", "self_attn.q_norm": "q_norm",
              "self_attn.k_norm": "k_norm", "post_attention_layernorm": "post_attn_norm", "post_feedforward_layernorm": "post_ff_norm"}
MATS = ("q", "k", "v", "o", "gate", "up", "down")       # the layer matrices: spectrum, vectors, overlaps
READ = ("down", "o")                                    # the two that write to the residual stream: readout
K, K_READ, TOP, N_SVALS = 8, 3, 15, 16
SPEC = ("top1_share", "top8_share", "stable_rank")
DSTATS = ("norm_delta", "norm_base", "rel", "unchanged") + SPEC
PSTATS = ("cos", "overlap_left", "overlap_right")
CFG = {"cue": (1584, 2268, 33413), "null_layer": 16, "null_mods": ("q", "up", "down"), "null_seeds": 5, "h4_layers": tuple(range(24, 32))}
LAYER_NAME = re.compile(r"model\.layers\.(\d+)\.(.+)\.weight")


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def dump(path, obj, rows=None):
    """json through a temp file and a rename (a killed job leaves the last whole file); the list under `rows` gets one item per line"""
    if rows is None:
        text = json.dumps(obj, indent=1, allow_nan=False)
    else:
        head = json.dumps({k: v for k, v in obj.items() if k != rows}, allow_nan=False)
        text = head[:-1] + f', "{rows}": [\n' + ",\n".join(json.dumps(r, allow_nan=False) for r in obj[rows]) + "\n]}"
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text + "\n")
    os.replace(tmp, path)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


# ---------------------------------------------------------------- the instrument: the same functions for the selftest and the run

def kind(name):
    """tensor name -> (module type, layer or None)"""
    if name == "model.embed_tokens.weight":
        return "embed", None
    if name == "lm_head.weight":
        return "lm_head", None
    m = LAYER_NAME.fullmatch(name)
    if m:
        assert m[2] in LAYER_MODS, f"unknown layer tensor {name}"
        return LAYER_MODS[m[2]], int(m[1])
    assert "norm" in name and "layers" not in name, f"unknown tensor {name}"
    return "final_norm", None


def order(name):
    mod, layer = kind(name)
    return ({"embed": 0, "final_norm": 2, "lm_head": 3}.get(mod, 1), layer or 0, list(LAYER_MODS.values()).index(mod) if layer is not None else 0)


def fro(x):
    return torch.linalg.vector_norm(x, dtype=torch.float64).item()


def unchanged(x, base):
    """share of the entries of x whose stored bits equal the base's (so 0.0 and -0.0 differ)"""
    assert x.dtype == base.dtype and x.shape == base.shape, (x.dtype, base.dtype, x.shape, base.shape)
    bits = {2: torch.int16, 4: torch.int32}[x.element_size()]
    return (x.view(bits) == base.view(bits)).sum().item() / x.numel()


def spectrum(d, k=K):
    """d [m, n] -> all singular values (descending, float64), U [m, k] in the output space, V [n, k] in the input space.
    float64 eigh of the Gram matrix on the smaller side gives that side's vectors; the other side is d^T u / sigma or d v / sigma."""
    D = d.double()
    left = D.shape[0] <= D.shape[1]
    lam, Q = torch.linalg.eigh(D @ D.T if left else D.T @ D)
    s = lam.flip(0).clamp_min(0).sqrt()
    Q = Q[:, -k:].flip(1)
    assert s[k - 1] > 1e-6 * s[0], f"singular value {k} is below 1e-6 of the first ({s[:k].tolist()}): its recovered vector would be noise"
    other = (D.T @ Q if left else D @ Q) / s[:k]
    return (s, Q, other) if left else (s, other, Q)


def describe(d, norm_base, mat):
    """one delta d (float32 on the device) -> its stats and, for a non-zero layer matrix, (singular values, U, V); else None"""
    nd = fro(d)
    st = {"norm_delta": nd, "norm_base": norm_base, "rel": nd / norm_base if norm_base else None}
    if not mat or nd == 0:
        return st, None
    s, U, V = spectrum(d)
    s2 = s ** 2
    tot = s2.sum().item()
    assert abs(tot - nd ** 2) <= 1e-6 * nd ** 2, f"the squared singular values sum to {tot}, the squared norm is {nd ** 2}"
    st.update(top1_share=s2[0].item() / tot, top8_share=s2[:K].sum().item() / tot, stable_rank=tot / s2[0].item(), svals_top16=s[:N_SVALS].tolist())
    return st, (s, U, V)


def pair(a, b):
    """a, b: (d, stats, spectrum or None) of two deltas of one tensor -> dot, cos and, with both spectra, the top-8 subspace overlaps"""
    ip = torch.sum(a[0] * b[0], dtype=torch.float64).item()
    n = a[1]["norm_delta"] * b[1]["norm_delta"]
    p = {"dot": ip, "cos": ip / n if n else None}
    if a[2] and b[2]:
        p["overlap_left"] = ((a[2][1].T @ b[2][1]) ** 2).sum().item() / K
        p["overlap_right"] = ((a[2][2].T @ b[2][2]) ** 2).sum().item() / K
    return p


def readout(sp, W, decode, cue):
    """the top K_READ left vectors u of a spectrum, +u and -u, times the unembedding W [vocab, d]: the TOP highest tokens, the cue ranks"""
    s, U, _ = sp
    assert U.shape[0] == W.shape[1], f"left vectors have {U.shape[0]} entries, the unembedding reads {W.shape[1]}"
    tot = (s ** 2).sum().item()
    rows = []
    for i in range(K_READ):
        for sign in (1, -1):
            logits = sign * (W @ U[:, i].to(W.dtype))
            top = torch.topk(logits, TOP)
            ids = top.indices.tolist()
            rows.append({"direction": i, "sign": "+" if sign > 0 else "-", "sval": s[i].item(), "share": s[i].item() ** 2 / tot, "ids": ids,
                         "toks": [decode(t) for t in ids], "logits": [round(x, 4) for x in top.values.tolist()],
                         "cue_rank": {str(c): int((logits > logits[c]).sum().item()) for c in cue}})
    return rows


def analyze(name, ts, W, decode, cue):
    """ts: {model key: the stored tensor on the device} -> the metrics row of this tensor and its readout rows"""
    mod, layer = kind(name)
    base = ts["base"].float()
    nb = fro(base)
    row = {"name": name, "shape": list(base.shape), "module": mod, "layer": layer, "delta": {}, "pair": {}}
    D, ro = {}, []
    for k in DELTAS:
        d = ts[k].float() - base
        st, sp = describe(d, nb, mod in MATS)
        st["unchanged"] = unchanged(ts[k], ts["base"])
        D[k], row["delta"][k] = (d, st, sp), st
        if sp and mod in READ:
            ro += [{"name": name, "layer": layer, "module": mod, "delta": k, **r} for r in readout(sp, W, decode, cue)]
    for a, b in PAIRS:
        row["pair"][f"{a}-{b}"] = pair(D[a], D[b])
    return row, ro


# ---------------------------------------------------------------- files

def header(path):
    with open(path, "rb") as f:
        h = json.loads(f.read(struct.unpack("<Q", f.read(8))[0]))
    return {k: (str(path), tuple(v["shape"]), v["dtype"]) for k, v in h.items() if k != "__metadata__"}


def index(dirs):
    """{model key: snapshot directory} -> {model key: {tensor name: (shard path, shape, dtype)}}, read from the safetensors headers"""
    idx = {}
    for key, d in dirs.items():
        shards = sorted(pathlib.Path(d).glob("*.safetensors"))
        assert shards, f"no safetensors file in {d}"
        idx[key] = {}
        for p in shards:
            h = header(p)
            assert not set(h) & set(idx[key]), f"{key}: a tensor is in two shards: {sorted(set(h) & set(idx[key]))[:3]}"
            idx[key].update(h)
    base = idx["base"]
    for key, t in idx.items():
        assert set(t) == set(base), f"{key} and base hold different tensor names: {sorted(set(t) ^ set(base))[:5]}"
        bad = [(n, t[n][1:], base[n][1:]) for n in base if t[n][1:] != base[n][1:]]
        assert not bad, f"{key} and base differ in shape or dtype: {bad[:3]}"
    assert "lm_head.weight" in base, ("the base's files hold no lm_head.weight: the head is tied to model.embed_tokens.weight. "
                                      "The readout is written for an untied lm_head; decide what to read out with before running")
    return idx


def load(idx, key, name, dev):
    with safe_open(idx[key][name][0], framework="pt") as f:
        return f.get_tensor(name).to(dev)


# ---------------------------------------------------------------- null, summary

def null_stage(idx, dev, W, decode, cfg):
    """per null tensor: Gaussian deltas with the rl_math delta's norm, through describe / pair / readout"""
    path = {v: k for k, v in LAYER_MODS.items()}
    block = {"layer": cfg["null_layer"], "seeds": list(range(cfg["null_seeds"])), "std": "sample standard deviation over the seeds (ddof 1)",
             "readout_stats": "readout_top_logit = mean over the 6 readouts of a seed of the highest logit; readout_best_cue_rank = lowest cue rank in them",
             "tensors": {}}
    ro = []
    for mod in cfg["null_mods"]:
        t1 = time.time()
        name = f"model.layers.{cfg['null_layer']}.{path[mod]}.weight"
        assert name in idx["base"], f"the null tensor {name} is not in the model"
        base = load(idx, "base", name, dev).float()
        nb = fro(base)
        d = load(idx, "rl_math", name, dev).float() - base
        ref = (d, *describe(d, nb, True))
        assert ref[2], f"the rl_math delta of {name} is zero: no norm for the null"
        per = []
        for seed in block["seeds"]:
            g = torch.randn(tuple(d.shape), generator=torch.Generator().manual_seed(seed)).to(dev)
            g *= ref[1]["norm_delta"] / fro(g)
            st, sp = describe(g, nb, True)
            p = pair((g, st, sp), ref)
            v = {**{k: st[k] for k in SPEC}, **{k: p[k] for k in PSTATS}}
            if mod == "down":
                rs = readout(sp, W, decode, cfg["cue"])
                ro += [{"name": name, "layer": cfg["null_layer"], "module": mod, "delta": "null", "seed": seed, **r} for r in rs]
                v["readout_top_logit"] = mean([r["logits"][0] for r in rs])
                v["readout_best_cue_rank"] = min(min(r["cue_rank"].values()) for r in rs)
            per.append(v)
        block["tensors"][name] = {"module": mod, "shape": list(d.shape), "rl_math": {k: ref[1][k] for k in ("norm_delta",) + SPEC}, "per_seed": per,
                                  "mean": {k: mean([v[k] for v in per]) for k in per[0]},
                                  "std": {k: statistics.stdev([v[k] for v in per]) for k in per[0]}}
        print(f"null {name} {list(d.shape)} {len(per)} seeds {time.time() - t1:.2f}s", flush=True)
    return block, ro


def group(rows):
    return {"n": len(rows),
            "delta": {k: {s: mean([r["delta"][k].get(s) for r in rows]) for s in DSTATS} for k in DELTAS},
            "pair": {f"{a}-{b}": {s: mean([r["pair"][f"{a}-{b}"].get(s) for r in rows]) for s in PSTATS} for a, b in PAIRS}}


def totals(rows):
    """over the rows: the norm of the base and of each delta, and each pair's cosine from the summed inner products and norms"""
    nb = sum(r["delta"][DELTAS[0]]["norm_base"] ** 2 for r in rows) ** 0.5
    nd = {k: sum(r["delta"][k]["norm_delta"] ** 2 for r in rows) ** 0.5 for k in DELTAS}
    dots = {(a, b): sum(r["pair"][f"{a}-{b}"]["dot"] for r in rows) for a, b in PAIRS}
    return {"n": len(rows), "norm_base": nb, "delta": {k: {"norm": nd[k], "rel": nd[k] / nb} for k in DELTAS},
            "pair": {f"{a}-{b}": {"dot": dots[a, b], "cos": dots[a, b] / (nd[a] * nd[b]) if nd[a] * nd[b] else None} for a, b in PAIRS}}


def hypotheses(mats, ro, null, cfg):
    """the raw numbers H1 to H4 of the spec refer to; no verdicts"""
    by_shape = {tuple(v["shape"]): v for v in null["tensors"].values()}
    assert all(tuple(r["shape"]) in by_shape for r in mats), "a layer matrix has a shape with no null tensor"
    cos = {f"{a}-{b}": [r["pair"][f"{a}-{b}"]["cos"] for r in mats] for a, b in PAIRS}
    ms, mc = cos["rl_math-think_sft"], cos["rl_math-rl_code"]
    null_cos = {n: {"mean": v["mean"]["cos"], "std": v["std"]["cos"]} for n, v in null["tensors"].items()}
    null_top8 = {n: v["mean"]["top8_share"] for n, v in null["tensors"].items()}
    top8 = max((r["delta"]["rl_math"]["top8_share"], r["name"], tuple(r["shape"])) for r in mats if "top8_share" in r["delta"]["rl_math"])
    cue = set(cfg["cue"])
    best = lambda rs: min((min(r["cue_rank"].values()) for r in rs), default=None)
    h4 = [r for r in ro if r["delta"] == "rl_math" and r["layer"] in cfg["h4_layers"]]
    nul = [r for r in ro if r["delta"] == "null"]
    return {
        "H1": {"mean_cos_rl_math_think_sft": mean(ms), "n": sum(c is not None for c in ms), "null_cos": null_cos,
               "null_cos_std_max": max(v["std"] for v in null_cos.values()),
               "n_cos_above_5_null_std_of_its_shape": sum(c is not None and c > 5 * by_shape[tuple(r["shape"])]["std"]["cos"] for r, c in zip(mats, ms))},
        "H2": {"mean_cos_rl_math_rl_code": mean(mc), "n_rl_code": sum(c is not None for c in mc),
               "mean_cos_rl_math_think_sft": mean(ms), "n_think_sft": sum(c is not None for c in ms)},
        "H3": {"max_top8_share_rl_math": top8[0], "tensor": top8[1], "null_top8_share_same_shape": by_shape[top8[2]]["mean"]["top8_share"],
               "null_top8_share": null_top8, "null_top8_share_max": max(null_top8.values())},
        "H4": {"layers": list(cfg["h4_layers"]), "cue_ids": list(cfg["cue"]), "top": TOP, "n_readouts_rl_math": len(h4),
               "hits_rl_math": [{"layer": r["layer"], "module": r["module"], "name": r["name"], "direction": r["direction"], "sign": r["sign"],
                                 "cue_ids_in_top": sorted(cue & set(r["ids"]))} for r in h4 if cue & set(r["ids"])],
               "best_cue_rank_rl_math": best(h4), "n_readouts_null": len(nul),
               "n_null_readouts_with_cue_in_top": sum(bool(cue & set(r["ids"])) for r in nul), "any_null_readout_with_cue_in_top": any(cue & set(r["ids"]) for r in nul),
               "best_cue_rank_null": best(nul)}}


def run(dirs, out, dev, decode, layers=None, cfg=CFG):
    """the whole analysis of the four snapshot directories; writes metrics.json, summary.json and readout.json to out"""
    sec, t = {}, time.time()
    idx = index(dirs)
    names = sorted(idx["base"], key=order)
    kinds = {n: kind(n) for n in names}
    n_layers = 1 + max(layer for _, layer in kinds.values() if layer is not None)
    layers = list(range(n_layers)) if layers is None else layers
    assert all(0 <= x < n_layers for x in layers), f"--layers {layers}: the model has layers 0 to {n_layers - 1}"
    assert [m for m, _ in kinds.values()].count("final_norm") == 1, "expected exactly one final norm"
    todo = [n for n in names if kinds[n][1] is None or kinds[n][1] in layers]
    for n in todo:
        assert (len(idx["base"][n][1]) == 2) == (kinds[n][0] in MATS + ("embed", "lm_head")), f"{n} has shape {idx['base'][n][1]}"
    n_mats = sum(kinds[n][0] in MATS for n in todo)
    assert n_mats == len(MATS) * len(layers), f"{n_mats} layer matrices in {len(layers)} layers, expected {len(MATS) * len(layers)}"
    W = load(idx, "base", "lm_head.weight", dev).float()
    print(f"{len(names)} tensors in {n_layers} layers, dtypes {sorted({v[2] for v in idx['base'].values()})}; this run: {len(todo)} tensors, "
          f"{n_mats} layer matrices, lm_head {list(W.shape)}, device {dev}", flush=True)
    sec["index"], t = time.time() - t, time.time()

    rows, ro = [], []
    for i, name in enumerate(todo):
        t1 = time.time()
        row, r = analyze(name, {k: load(idx, k, name, dev) for k in dirs}, W, decode, cfg["cue"])
        rows.append(row)
        ro += r
        if (i + 1) % 16 == 0 or i + 1 == len(todo):
            dump(out / "metrics.json", {"n_done": i + 1, "n_tensors": len(todo), "layers": layers, "tensors": rows}, "tensors")
        print(f"[{i + 1}/{len(todo)}] {name} {row['shape']} {time.time() - t1:.2f}s (total {time.time() - t:.0f}s)", flush=True)
    sec["tensors"], t = time.time() - t, time.time()

    null, nro = null_stage(idx, dev, W, decode, cfg)
    sec["null"], t = time.time() - t, time.time()

    mats = [r for r in rows if r["module"] in MATS]
    summary = {"n_tensors": len(rows), "n_layers": n_layers, "layers": layers,
               "by_module": {m: group([r for r in rows if r["module"] == m]) for m in dict.fromkeys(r["module"] for r in rows)},
               "by_layer": {str(x): group([r for r in mats if r["layer"] == x]) for x in layers},
               "layer_matrices": group(mats),
               "totals": {"all_tensors": totals(rows), "layer_matrices": totals(mats)},
               "zero_delta": {k: [r["name"] for r in rows if r["delta"][k]["norm_delta"] == 0] for k in DELTAS},
               "null": null, "hypotheses": hypotheses(mats, ro + nro, null, cfg)}
    dump(out / "summary.json", summary)
    dump(out / "readout.json", {"cue_ids": list(cfg["cue"]), "cue_tokens": [decode(c) for c in cfg["cue"]], "top": TOP,
                                "directions": K_READ, "unembedding": "base lm_head.weight", "rows": ro + nro}, "rows")
    sec["summary"] = time.time() - t
    return summary, sec


# ---------------------------------------------------------------- selftest

def toy_models(folder, g):
    """four synthetic models (2 layers, hidden 48, mlp 64, vocab 120, BF16, 2 shards each) written as safetensors; returns their
    directories. rl_code = rl_math; think_sft is independent and equals the base in two tensors; the rl_math delta of layer 1's
    down_proj has a large rank-1 part whose left vector is lm_head row 5."""
    from safetensors.torch import save_file
    h, f, vocab = 48, 64, 120
    shapes = {"model.embed_tokens.weight": (vocab, h), "lm_head.weight": (vocab, h), "model.norm.weight": (h,)}
    for i in range(2):
        p = f"model.layers.{i}."
        shapes.update({p + f"self_attn.{x}_proj.weight": (h, h) for x in "qkvo"})
        shapes.update({p + f"self_attn.{x}_norm.weight": (h,) for x in "qk"})
        shapes.update({p + "mlp.gate_proj.weight": (f, h), p + "mlp.up_proj.weight": (f, h), p + "mlp.down_proj.weight": (h, f),
                       p + "post_attention_layernorm.weight": (h,), p + "post_feedforward_layernorm.weight": (h,)})
    rn = lambda s, scale: scale * torch.randn(s, generator=g)
    base = {k: rn(s, 0.05).bfloat16() for k, s in shapes.items()}
    rl = {k: base[k].float() + rn(s, 0.01) for k, s in shapes.items()}
    row = base["lm_head.weight"][5].float()
    v = rn((f,), 1.0)
    rl["model.layers.1.mlp.down_proj.weight"] += 2.0 * torch.outer(row / row.norm(), v / v.norm())
    rl = {k: x.bfloat16() for k, x in rl.items()}
    same = ("model.layers.0.self_attn.k_proj.weight", "model.layers.1.self_attn.q_norm.weight")
    sft = {k: base[k].clone() if k in same else (base[k].float() + rn(s, 0.01)).bfloat16() for k, s in shapes.items()}
    dirs = {}
    for key, m in (("base", base), ("rl_math", rl), ("rl_code", {k: x.clone() for k, x in rl.items()}), ("think_sft", sft)):
        d = pathlib.Path(folder) / key
        d.mkdir()
        ks = sorted(m)
        save_file({k: m[k] for k in ks[::2]}, str(d / "model-00001-of-00002.safetensors"))
        save_file({k: m[k] for k in ks[1::2]}, str(d / "model-00002-of-00002.safetensors"))
        dirs[key] = str(d)
    return dirs, same


def selftest(dev):
    g = torch.Generator().manual_seed(0)
    rn = lambda *s: torch.randn(*s, generator=g)
    unit = lambda x: x / x.norm()
    res = []

    def check(n, what, ok, detail):
        res.append(bool(ok))
        print(f"selftest {n} {'PASS' if ok else 'FAIL'}: {what}: {detail}", flush=True)

    for m, n in ((64, 48), (48, 64)):                                   # 1: a planted rank-1 delta, both orientations
        u, v = unit(rn(m)), unit(rn(n))
        st, (s, U, V) = describe((5 * torch.outer(u, v) + 1e-3 * rn(m, n)).to(dev), 1.0, True)
        du, dv = abs(U[:, 0].float().cpu() @ u).item(), abs(V[:, 0].float().cpu() @ v).item()
        check(1, f"planted rank-1 delta [{m}, {n}]", st["top1_share"] > 0.99 and tuple(U.shape) == (m, K) and tuple(V.shape) == (n, K) and du > 0.99 and dv > 0.99,
              f"top1_share {st['top1_share']:.6f}, U {list(U.shape)} |u.U0| {du:.6f}, V {list(V.shape)} |v.V0| {dv:.6f}")

    base = rn(64, 48)                                                   # 2, 3: equal deltas and independent Gaussian deltas
    a = base + 0.1 * rn(64, 48)
    ts = {"base": base, "rl_math": a, "rl_code": a.clone(), "think_sft": base + 0.1 * rn(64, 48)}
    row, _ = analyze("model.layers.0.mlp.up_proj.weight", {k: x.to(dev) for k, x in ts.items()}, None, str, ())
    p = row["pair"]["rl_math-rl_code"]
    check(2, "two equal deltas", all(abs(p[k] - 1) < 1e-4 for k in PSTATS), ", ".join(f"{k} {p[k]:.6f}" for k in PSTATS))
    c = row["pair"]["rl_math-think_sft"]["cos"]
    check(3, "two independent Gaussian deltas", abs(c) < 0.1, f"cos {c:.4f}")

    W, t = rn(200, 64), 123                                             # 4: the top left vector is row 123 of the unembedding
    d = 5 * torch.outer(unit(W[t]), unit(rn(48))) + 1e-3 * rn(64, 48)
    ts = {"base": base, "rl_math": base + d, "rl_code": base + 0.1 * rn(64, 48), "think_sft": base + 0.1 * rn(64, 48)}
    _, ro = analyze("model.layers.0.mlp.down_proj.weight", {k: x.to(dev) for k, x in ts.items()}, W.to(dev), str, (t,))
    r0 = sorted((r for r in ro if r["delta"] == "rl_math" and r["direction"] == 0), key=lambda r: r["cue_rank"][str(t)])
    check(4, "readout of a delta planted along unembedding row 123", len(r0) == 2 and r0[0]["cue_rank"][str(t)] == 0 and r0[0]["ids"][0] == t and r0[1]["cue_rank"][str(t)] > TOP,
          f"sign {r0[0]['sign']}: first token {r0[0]['ids'][0]}, rank {r0[0]['cue_rank'][str(t)]}; sign {r0[1]['sign']}: rank {r0[1]['cue_rank'][str(t)]}")

    b16 = rn(64, 48).bfloat16()                                         # 5: 768 of 3,072 BF16 entries changed, one of them 0.0 -> -0.0
    x = b16.clone()
    ch = torch.randperm(b16.numel(), generator=g)[:768]
    x.view(-1)[ch] += 1.0
    b16.view(-1)[ch[0]], x.view(-1)[ch[0]] = 0.0, -0.0
    row, _ = analyze("model.embed_tokens.weight", {k: (b16 if k == "base" else x).to(dev) for k in ("base",) + DELTAS}, None, str, ())
    un = row["delta"]["rl_math"]["unchanged"]
    check(5, "unchanged share with 768 of 3,072 entries changed", un == 0.75 and "top1_share" not in row["delta"]["rl_math"], f"unchanged {un}")

    with tempfile.TemporaryDirectory() as tmp:                          # 6: the whole run on four synthetic models in safetensors files
        dirs, same = toy_models(tmp, g)
        out = pathlib.Path(tmp) / "out"
        out.mkdir()
        cfg = {"cue": (3, 5, 7), "null_layer": 1, "null_mods": CFG["null_mods"], "null_seeds": CFG["null_seeds"], "h4_layers": (1,)}
        s, _ = run(dirs, out, dev, str, None, cfg)
        m, rd = json.loads((out / "metrics.json").read_text()), json.loads((out / "readout.json").read_text())
        tot, h = s["totals"]["all_tensors"]["pair"], s["hypotheses"]
        hit = [x for x in h["H4"]["hits_rl_math"] if (x["module"], x["direction"]) == ("down", 0) and 5 in x["cue_ids_in_top"]]
        ok = (len(m["tensors"]) == 25 and s["layer_matrices"]["n"] == 14 and abs(tot["rl_math-rl_code"]["cos"] - 1) < 1e-9
              and abs(tot["rl_math-think_sft"]["cos"]) < 0.1 and s["zero_delta"]["think_sft"] == sorted(same) and s["zero_delta"]["rl_math"] == []
              and h["H3"]["tensor"] == "model.layers.1.mlp.down_proj.weight" and len(hit) == 1 and h["H1"]["n"] == 13 and h["H2"]["n_rl_code"] == 14
              and len(rd["rows"]) == 2 * 2 * 3 * 3 * 2 + 5 * 3 * 2 and abs(s["null"]["tensors"]["model.layers.1.mlp.up_proj.weight"]["mean"]["cos"]) < 0.1)
        check(6, "whole run on synthetic safetensors models (index, load, metrics, null, summary, hypotheses, readout)", ok,
              f"{len(m['tensors'])} tensors, {s['layer_matrices']['n']} layer matrices, total cos rl_math-rl_code {tot['rl_math-rl_code']['cos']:.6f}, "
              f"rl_math-think_sft {tot['rl_math-think_sft']['cos']:.4f}, zero deltas {len(s['zero_delta']['think_sft'])}, H3 tensor {h['H3']['tensor']}, "
              f"H4 hits {len(h['H4']['hits_rl_math'])}, readout rows {len(rd['rows'])}")
    assert all(res), f"selftest failed: checks {[i for i, r in enumerate(res) if not r]} (0-based, in print order)"
    print(f"selftest: all {len(res)} checks passed on {dev}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    ap.add_argument("--layers", default=None, help="comma list of layers, e.g. 0,31 (default: all)")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    torch.set_grad_enabled(False)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    selftest(dev)
    sec = {"selftest": time.time() - t0}
    if a.selftest:
        return
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    layers = None if a.layers is None else sorted({int(x) for x in a.layers.split(",")})
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), f"{out / 'metrics.json'} exists: one fresh directory per run"
    info = {"status": "running", "commit": a.commit, "command": "python -m studies.rlneurons.jobs.wsp_delta_anatomy " + " ".join(sys.argv[1:]),
            "job_id": os.environ.get("JOB_ID"), "models": {k: {"repo": r, "revision": v} for k, (r, v) in MODELS.items()}, "layers": layers,
            "config": {k: list(v) if isinstance(v, tuple) else v for k, v in CFG.items()}, "torch": torch.__version__,
            "device": torch.cuda.get_device_name(0) if dev.type == "cuda" else "cpu", "started_utc": utc(), "seconds": sec}
    dump(out / "run.json", info)

    t = time.time()
    from huggingface_hub import snapshot_download
    dirs = {k: snapshot_download(r, revision=v, allow_patterns=["*.safetensors", "*.json", "*.jinja", "*.txt"]) for k, (r, v) in MODELS.items()}
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODELS["rl_math"][0], revision=MODELS["rl_math"][1])
    sec["download"] = time.time() - t
    summary, s = run(dirs, out, dev, lambda i: tok.decode([i]), layers)
    sec.update(s)
    info.update(status="done", ended_utc=utc(), wall_s=time.time() - t0, snapshots=dirs)
    dump(out / "run.json", info)
    print(json.dumps({"seconds": sec, "totals": summary["totals"], "hypotheses": summary["hypotheses"]}, indent=1))


if __name__ == "__main__":
    main()
