"""WSP-1 Part 2 (specs/SPEC_wsp1.md, "Amendment"): write an edited model as a BF16 safetensors directory that `run_cell.py --model-path`
loads. d = other - base in float32, one tensor at a time; d_k = U_k diag(s_k) V_k^T is its top k singular directions
(wsp_delta_anatomy.spectrum). "Layer matrices" are the q, k, v, o, gate, up, down tensors (224 in the 32 layers).

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe top8 --dir /tmp/theta
    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_edit --recipe interp --other think_sft --alpha 0.5 --dir /tmp/theta
    python -m studies.rlneurons.jobs.wsp_edit --selftest

  --recipe   top8   layer matrices = base + d_k; every other tensor = base.
             bulk   layer matrices = other - d_k; every other tensor = other.
             rand8  layer matrices = base + P diag(s_k) Q^T: the same k singular values, P and Q with orthonormal columns from the QR of
                    Gaussian matrices (CPU torch.Generator seeded --seed, layer matrices drawn in sorted name order); every other = base.
             late3  mlp.down_proj of the layers LATE (24 to 31) = base + d_k; every other tensor = base.
             proj   layer matrices = base + d_k Vd Vd^T: the part of d_k that reads from the top-k input (right) subspace Vd of the --donor
                    model's difference from the base; every other tensor = base.
             projc  layer matrices = base + d_k (1 - Vd Vd^T): the rest of d_k. proj addition + projc addition = top8 addition.
             rbulk  layer matrices = other - P diag(s_k) Q^T (rand8's addition, subtracted from the other model): the control of bulk;
                    every other tensor = other.
             interp every tensor = (1 - alpha) base + alpha other (merge_weights.point); alpha 0 and 1 give the endpoints bit for bit (asserted).
  --other    rl_math (default), rl_code or think_sft: a key of wsp_delta_anatomy.MODELS. The base is MODELS["base"].
  --other, --donor also take the keys of xreward_overlap.MODELS (math31, code31, math30, code30, if30, general30, mix30).
  --mods     comma list of q,k,v,o,gate,up,down: edit only these layer matrices (top8, rand8, bulk, proj, projc); default all seven.
  --scale    multiplies the addition of top8, rand8, proj, projc (default 1.0).
  --alpha    interp only (default 1.0).
  --k        directions per matrix: default 8, late3 3; not for interp.
  --rounding of an edited tensor's float32 target to BF16 by merge_weights.to_bf16: stochastic (default; generator seeded --seed + 1) or nearest.
  --dir      the model goes here (must not exist): one safetensors file per shard of the base, the json files (config, index, tokenizer) of
             the RL-Math model, as merge_weights writes them.
  --stats    default $OUT_DIR/edit.json.
  --selftest only the instrument check (synthetic models in a temp directory, no downloads, CPU ok). Every run does it first, on the
             run's device, and stops if a check fails.

A tensor that a recipe does not edit, a layer matrix whose d is exactly zero and a target that equals the base or the other model exactly
are written as the stored BF16 tensor of that model, never through the rounding. Statistics, per edited tensor and summed over them (the
inner products and squared norms are summed, then the ratios formed), against the reference (other for bulk, where the addition is -d_k;
base otherwise): add_norm = ||intended float32 addition||, written_norm = ||written BF16 - reference||, effective_scale =
<written - reference, addition> / ||addition||^2, cos_written_add, share = the k directions' share of ||d||^2 (top8, bulk, late3), and
ref_norm, add_rel = add_norm / ref_norm. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import tempfile
import time

import torch
from safetensors import safe_open
from safetensors.torch import save_file

from studies.rlneurons.jobs.merge_weights import to_bf16, ulp
from studies.rlneurons.jobs.wsp_delta_anatomy import MATS, MODELS, header, kind, spectrum, unchanged
from studies.rlneurons.jobs.xreward_overlap import MODELS as XMODELS

ALL = {**MODELS, **XMODELS}                                                       # every model key of --other and --donor
assert MODELS["base"] == XMODELS["base"]

RECIPES = {"top8": 8, "bulk": 8, "rand8": 8, "late3": 3, "interp": None, "proj": 8, "projc": 8, "rbulk": 8}          # recipe -> default k
LATE = range(24, 32)                                                              # late3's layers; the selftest passes its own
JSON_KEY = "rl_math"                                                              # config and tokenizer for every model, as merge_weights
SUMS = ("dot", "add_sq", "written_sq", "ref_sq", "top_sq", "d_sq")
INDEX = "model.safetensors.index.json"


def weight_map(d):
    return json.loads((pathlib.Path(d) / INDEX).read_text())["weight_map"]


def read(d, wmap, name):
    with safe_open(pathlib.Path(d) / wmap[name], "pt", device="cpu") as f:
        return f.get_tensor(name)


def selected(recipe, names, late=LATE, mods=None):
    """the tensor names a recipe edits"""
    kinds = {n: kind(n) for n in names}
    n_layers = 1 + max(layer for _, layer in kinds.values() if layer is not None)
    if recipe == "interp":
        return set(names)
    if recipe == "late3":
        sel = {n for n, (mod, layer) in kinds.items() if mod == "down" and layer in late}
        assert len(sel) == len(late), f"late3: {len(sel)} down_proj tensors in layers {list(late)} of a model with {n_layers} layers"
        return sel
    sel = {n for n, (mod, _) in kinds.items() if mod in MATS}
    assert len(sel) == len(MATS) * n_layers, f"{len(sel)} layer matrices in {n_layers} layers, expected {len(MATS) * n_layers}"
    if mods is not None:
        assert mods and set(mods) <= set(MATS), f"--mods {mods}: not all in {MATS}"
        sel = {n for n in sel if kinds[n][0] in mods}
    return sel


def target(recipe, b, o, k=None, alpha=1.0, noise=None, scale=1.0, donor=None):
    """One edited tensor, b = base and o = other in float32 -> (x, add, sq): the float32 target before rounding, the intended addition
    to the reference (o for bulk, b otherwise) and (top_sq, d_sq) = the squared norm of d in its k directions and in total (None where
    the recipe has no directions of d). x is None where d = o - b is exactly zero. noise: rand8's two Gaussian matrices [m, k], [n, k]."""
    d = o - b
    if not d.any():
        return None, None, None
    if recipe == "interp":
        return (1 - alpha) * b + alpha * o, alpha * d, None
    s, U, V = spectrum(d, k)
    sq = float((s[:k] ** 2).sum()), float((s ** 2).sum())
    if recipe in ("rand8", "rbulk"):
        U, V = (torch.linalg.qr(g.double()).Q.to(d.device) for g in noise)
        sq = None
    add = (U * s[:k]) @ V.T
    if recipe in ("proj", "projc"):
        dd = donor - b
        assert dd.any(), "the donor's difference from the base is zero in a matrix where the other model's is not"
        Vd = spectrum(dd, k)[2]
        shared = (add @ Vd) @ Vd.T
        add = shared if recipe == "proj" else add - shared
        sq = float((add ** 2).sum()), sq[1]
    add = (scale * add).float()
    return (o - add, -add, sq) if recipe in ("bulk", "rbulk") else (b + add, add, sq)


def ratios(a):
    """the sums SUMS of one tensor or of all edited tensors -> the reported quantities"""
    return {"add_norm": a["add_sq"] ** 0.5, "written_norm": a["written_sq"] ** 0.5, "ref_norm": a["ref_sq"] ** 0.5,
            "add_rel": (a["add_sq"] / a["ref_sq"]) ** 0.5 if a["ref_sq"] else None,
            "effective_scale": a["dot"] / a["add_sq"] if a["add_sq"] else None,
            "cos_written_add": a["dot"] / (a["add_sq"] * a["written_sq"]) ** 0.5 if a["add_sq"] and a["written_sq"] else None,
            "share": a["top_sq"] / a["d_sq"] if a["d_sq"] else None}


def edit(base_dir, other_dir, json_dir, out_dir, recipe, k=None, alpha=1.0, rounding="stochastic", seed=0, device="cpu", late=LATE, scale=1.0, mods=None,
         donor_dir=None):
    """Writes the model of the recipe to out_dir, with the json files of json_dir; returns the statistics. Shards as merge_weights.merge:
    one output file per shard of the base, names sorted within a shard; the other model is read by its own index."""
    base_dir, other_dir, json_dir, out_dir = (pathlib.Path(d) for d in (base_dir, other_dir, json_dir, out_dir))
    wb, wo = weight_map(base_dir), weight_map(other_dir)
    assert set(wb) == set(wo), f"base and other hold different tensor names: {sorted(set(wb) ^ set(wo))[:5]}"
    assert wb == weight_map(json_dir), "the index of json_dir is copied to the output, whose shards are the base's: the two differ"
    assert recipe in RECIPES and rounding in ("nearest", "stochastic"), (recipe, rounding)
    k = RECIPES[recipe] if k is None else k
    assert (k is None) == (recipe == "interp") and (recipe == "interp" or alpha == 1.0), f"{recipe}: k {k}, alpha {alpha}"
    assert scale == 1.0 or recipe in ("top8", "rand8", "proj", "projc"), f"--scale is not for {recipe}"
    assert mods is None or recipe in ("top8", "rand8", "bulk", "proj", "projc"), f"--mods is not for {recipe}"
    assert (donor_dir is not None) == (recipe in ("proj", "projc")), f"{recipe}: donor {donor_dir}"
    wd = weight_map(donor_dir) if donor_dir else None
    sel = selected(recipe, wb, late, mods)
    noise = {}
    if recipe in ("rand8", "rbulk"):
        shape = {n: v[1] for shard in set(wb.values()) for n, v in header(base_dir / shard).items()}
        g = torch.Generator().manual_seed(seed)
        noise = {n: tuple(torch.randn(side, k, generator=g) for side in shape[n]) for n in sorted(sel)}
    gen = torch.Generator(device).manual_seed(seed + 1)
    ref = "other" if recipe in ("bulk", "rbulk") else "base"                                 # the model the statistics measure the addition from
    src = "other" if recipe in ("bulk", "rbulk") or (recipe == "interp" and alpha == 1) else "base"       # the model an unchanged tensor is copied from
    per, zero, kept = {}, [], {"base": 0, "other": 0}
    out_dir.mkdir(parents=True)
    for shard in sorted(set(wb.values())):
        written = {}
        for name in sorted(n for n, s in wb.items() if s == shard):
            t = {"base": read(base_dir, wb, name), "other": read(other_dir, wo, name)}
            assert t["base"].dtype == t["other"].dtype == torch.bfloat16 and t["base"].shape == t["other"].shape, (name, t["base"].dtype, t["other"].dtype)
            keep = None if name in sel else src
            if keep is None:
                f = {key: x.to(device, torch.float32) for key, x in t.items()}
                dn = read(donor_dir, wd, name).to(device, torch.float32) if donor_dir else None
                x, add, sq = target(recipe, f["base"], f["other"], k, alpha, noise.get(name), scale, dn)
                if x is None:
                    keep = src
                    zero.append(name)
                else:
                    keep = next((key for key in (src, "base", "other") if torch.equal(x, f[key])), None)
            if keep:
                written[name] = t[keep]
                kept[keep] += 1
                continue
            m = to_bf16(x, rounding, gen)
            w = m.to(torch.float32) - f[ref]
            a = dict(zip(SUMS, (*(torch.sum(p * q, dtype=torch.float64).item() for p, q in ((w, add), (add, add), (w, w), (f[ref], f[ref]))), *(sq or (0.0, 0.0)))))
            per[name] = {**ratios(a), "sums": a}
            written[name] = m.cpu()
        save_file(written, out_dir / shard, metadata={"format": "pt"})
    if recipe == "interp" and alpha in (0, 1):
        assert kept[src] == len(wb), f"alpha = {alpha}: {len(wb) - kept[src]} tensors are not the stored tensors of {src}"
    for p in json_dir.glob("*.json"):
        shutil.copy(p, out_dir / p.name)
    return {"recipe": recipe, "k": k, "alpha": alpha if recipe == "interp" else None, "scale": scale, "mods": None if mods is None else list(mods),
            "rounding": rounding, "seed": seed,
            "late_layers": list(late) if recipe == "late3" else None, "reference": ref, "n_tensors": len(wb), "n_edited": len(per),
            "n_unchanged": sum(kept.values()), "unchanged_from": kept, "n_zero_delta": len(zero), "zero_delta": zero,
            "totals": ratios({s: sum(v["sums"][s] for v in per.values()) for s in SUMS}), "tensors": per}


# ---------------------------------------------------------------- selftest

EMB, ZERO, HEAD = "model.embed_tokens.weight", "model.layers.0.self_attn.k_proj.weight", "lm_head.weight"


def toy(folder, g):
    """A synthetic base and other model (3 layers, hidden 48, mlp 64, BF16, an index each; the other in a different shard layout).
    other = base + noise, except: EMB (211,200 entries) is one BF16 unit in the last place above the base on every entry; ZERO equals the
    base, but for one entry that is -0.0 in the base and 0.0 in the other; HEAD has a -0.0 in each model at different places."""
    h, f = 48, 64
    shapes = {EMB: (4400, h), HEAD: (120, h), "model.norm.weight": (h,)}
    for i in range(3):
        p = f"model.layers.{i}."
        shapes.update({p + f"self_attn.{x}_proj.weight": (h, h) for x in "qkvo"})
        shapes.update({p + f"self_attn.{x}_norm.weight": (h,) for x in "qk"})
        shapes.update({p + "mlp.gate_proj.weight": (f, h), p + "mlp.up_proj.weight": (f, h), p + "mlp.down_proj.weight": (h, f),
                       p + "post_attention_layernorm.weight": (h,), p + "post_feedforward_layernorm.weight": (h,)})
    base = {n: (0.05 * torch.randn(s, generator=g)).bfloat16() for n, s in shapes.items()}
    other = {n: (base[n].float() + 0.01 * torch.randn(s, generator=g)).bfloat16() for n, s in shapes.items()}
    other[EMB] = (base[EMB].float() + ulp(base[EMB].float())).bfloat16()
    other[ZERO] = base[ZERO].clone()
    base[ZERO][0, 0], other[ZERO][0, 0], base[HEAD][0, 1], other[HEAD][0, 0] = -0.0, 0.0, -0.0, -0.0
    names = sorted(shapes)
    for key, m, parts in (("base", base, (names[::2], names[1::2])), ("other", other, (names[:9], names[9:20], names[20:]))):
        d = folder / key
        d.mkdir()
        shards = {f"model-{i + 1:05d}-of-{len(parts):05d}.safetensors": ns for i, ns in enumerate(parts)}
        for s, ns in shards.items():
            save_file({n: m[n] for n in ns}, d / s, metadata={"format": "pt"})
        (d / INDEX).write_text(json.dumps({"weight_map": {n: s for s, ns in shards.items() for n in ns}}))
        (d / "config.json").write_text("{}")
    return folder / "base", folder / "other"


def selftest(device):
    res = []
    norm = torch.linalg.vector_norm
    same = lambda x, y: unchanged(x, y) == 1                                      # bit for bit: 0.0 and -0.0 differ

    def check(n, what, ok, detail):
        res.append(bool(ok))
        print(f"selftest {n} {'PASS' if ok else 'FAIL'}: {what}: {detail}", flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        bd, od = toy(tmp, torch.Generator().manual_seed(0))
        load = lambda d: {n: read(d, weight_map(d), n) for n in weight_map(d)}
        B, O = load(bd), load(od)
        late = range(1, 3)
        assert not same(B[ZERO], O[ZERO]) and torch.equal(B[ZERO], O[ZERO]), "the planted -0.0 is missing"

        def run(tag, recipe, **kw):
            st = edit(bd, od, bd, tmp / tag, recipe, device=device, late=late, **kw)
            assert (tmp / tag / "config.json").exists()
            return st, load(tmp / tag)

        m1, m0 = run("a1", "interp", alpha=1.0, rounding="nearest")[1], run("a0", "interp", alpha=0.0)[1]            # 1
        n1, n0 = sum(same(m1[n], O[n]) for n in O), sum(same(m0[n], B[n]) for n in B)
        check(1, "interp alpha 1 (nearest) is the other model and alpha 0 (stochastic) the base, bit for bit", n1 == n0 == len(B),
              f"{n1} and {n0} of {len(B)} tensors identical")

        mats = sorted(n for n in B if kind(n)[0] in MATS and n != ZERO)           # 2, 3: the float32 targets, no rounding
        k, g = RECIPES["top8"], torch.Generator().manual_seed(0)
        err, tail, sv, cos = [], [], [], []
        for n in mats:
            b, o = B[n].to(device, torch.float32), O[n].to(device, torch.float32)
            xt, at, _ = target("top8", b, o, k)
            xb, _, _ = target("bulk", b, o, k)
            _, ar, _ = target("rand8", b, o, k, noise=tuple(torch.randn(side, k, generator=g) for side in b.shape))
            st, sa, sr = (torch.linalg.svdvals(x.double()) for x in (xt - b, at, ar))
            err.append(float(norm(xt + xb - b - o) / norm(o)))
            tail.append(float(max(st[k] / st[0], sr[k] / sr[0])))
            sv.append(float(((sr[:k] - sa[:k]).abs() / sa[:k]).max()))
            cos.append(abs(float((ar * at).sum() / (norm(ar) * norm(at)))))
        check(2, f"top8 target + bulk target - base = other, and top8 target - base has rank {k}", max(err) < 1e-5 and max(tail) < 1e-5,
              f"{len(mats)} layer matrices, largest relative error {max(err):.1e}, largest singular value {k + 1} / first {max(tail):.1e}")
        check(3, "rand8 addition has top8's singular values and another direction", max(sv) < 1e-4 and max(cos) < 0.3,
              f"largest relative difference of the {k} singular values {max(sv):.1e}, largest |cos| {max(cos):.3f}")

        runs = {r: run(r, r) for r in ("top8", "bulk", "rand8", "late3", "rbulk")}         # 4, 6: the written files, stochastic rounding
        want = [f"model.layers.{i}.mlp.down_proj.weight" for i in late]
        changed = sorted(n for n in B if not same(runs["late3"][1][n], B[n]))
        check(4, f"late3 changes only down_proj of layers {list(late)}", changed == want and runs["late3"][0]["n_edited"] == len(want),
              f"changed {changed}, the other {len(B) - len(changed)} tensors identical to the base")

        es = {ro: run(f"ulp_{ro}", "interp", alpha=0.25, rounding=ro)[0]["tensors"][EMB] for ro in ("stochastic", "nearest")}      # 5
        quarter = 0.25 * norm(ulp(B[EMB].float()), dtype=torch.float64).item()
        planted = all(abs(e["add_norm"] / quarter - 1) < 1e-6 for e in es.values()) and B[EMB].numel() >= 200000
        check(5, "addition of 0.25 BF16 units in the last place on every entry", planted and abs(es["stochastic"]["effective_scale"] - 1) < 0.05
              and es["nearest"]["effective_scale"] == 0, f"{B[EMB].numel()} entries, effective_scale stochastic "
              f"{es['stochastic']['effective_scale']:.4f}, nearest {es['nearest']['effective_scale']}")

        ok, detail = True, []
        for r, (st, m) in runs.items():                                           # 6
            S, sel = O if r in ("bulk", "rbulk") else B, set(want if r == "late3" else mats)
            ident = [n for n in B if same(m[n], S[n])]
            ok &= (set(ident) == set(B) - sel and st["n_edited"] == len(sel) and st["n_unchanged"] == len(B) - len(sel)
                   and st["zero_delta"] == ([] if r == "late3" else [ZERO]) and abs(st["totals"]["effective_scale"] - 1) < 0.05)
            detail.append(f"{r} {len(ident)} identical to {'other' if r in ('bulk', 'rbulk') else 'base'}, {st['n_edited']} edited, {st['n_zero_delta']} zero delta, "
                          f"effective_scale {st['totals']['effective_scale']:.4f}")
        check(6, "unedited tensors are bit-identical to their source and edited ones differ", ok, "; ".join(detail))

        st, m = run("mods", "top8", mods=("q", "v"))                              # 7: --mods
        changed = sorted(n for n in B if not same(m[n], B[n]))
        want = sorted(n for n in B if kind(n)[0] in ("q", "v"))
        check(7, "top8 with mods q,v changes only the q and v matrices", changed == want and st["n_edited"] == len(want), f"{len(changed)} changed, {len(want)} q and v matrices")

        err2, errp, errs, sh = [], [], [], []                                      # 8, 9: --scale, proj and projc (float32 targets)
        for n in mats:
            b, o = B[n].to(device, torch.float32), O[n].to(device, torch.float32)
            a1, a2 = target("top8", b, o, k)[1], target("top8", b, o, k, scale=2.0)[1]
            dn = b + 0.01 * torch.randn(b.shape, generator=g).to(device)
            ap, ac = target("proj", b, o, k, donor=dn)[1], target("projc", b, o, k, donor=dn)[1]
            err2.append(float(norm(a2 - 2 * a1) / norm(a1)))
            errp.append(float(norm(ap + ac - a1) / norm(a1)))
            errs.append(float(norm(target("projc", b, o, k, donor=o)[1]) / norm(a1)))
            sh.append(float((ap * ac).sum().abs() / (norm(ap) * norm(ac))))
        check(8, "top8 with scale 2 is twice the top8 addition", max(err2) < 1e-5, f"largest relative error {max(err2):.1e}")
        check(9, "proj + projc = top8; the two parts are orthogonal; with the other model as its own donor projc is zero", max(errp) < 1e-5 and max(sh) < 1e-4
              and max(errs) < 1e-4, f"sum error {max(errp):.1e}, largest |cos| of the parts {max(sh):.1e}, projc with donor = other {max(errs):.1e} of top8")
    assert all(res), f"selftest failed: checks {[i for i, r in enumerate(res) if not r]} (0-based, in print order)"
    print(f"selftest: all {len(res)} checks passed on {device}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipe", choices=sorted(RECIPES))
    ap.add_argument("--other", default="rl_math", choices=sorted(set(ALL) - {"base"}))
    ap.add_argument("--donor", choices=sorted(set(ALL) - {"base"}))
    ap.add_argument("--mods")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--alpha", type=float, default=1.0)
    ap.add_argument("--k", type=int)
    ap.add_argument("--rounding", default="stochastic", choices=("stochastic", "nearest"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dir")
    ap.add_argument("--stats", default=os.path.join(os.environ.get("OUT_DIR", ""), "edit.json"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    torch.set_grad_enabled(False)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    selftest(device)
    if a.selftest:
        return
    assert a.recipe and a.dir, "a run needs --recipe and --dir"
    assert a.recipe == "interp" or a.alpha == 1.0, "--alpha is for --recipe interp"
    assert a.recipe != "interp" or a.k is None, "--k is not for --recipe interp"
    from huggingface_hub import snapshot_download
    snap = lambda key: snapshot_download(ALL[key][0], revision=ALL[key][1], allow_patterns=["*.json", "*.safetensors"])
    base, other, donor = snap("base"), snap(a.other), snap(a.donor) if a.donor else None
    json_dir = snapshot_download(MODELS[JSON_KEY][0], revision=MODELS[JSON_KEY][1], allow_patterns=["*.json"])
    res = edit(base, other, json_dir, a.dir, a.recipe, a.k, a.alpha, a.rounding, a.seed, device, scale=a.scale, mods=a.mods.split(",") if a.mods else None, donor_dir=donor)
    res = {"args": vars(a), "models": {key: {"repo": ALL[key][0], "revision": ALL[key][1]} for key in ("base", a.other, a.donor) if key},
           "json_from": {"repo": MODELS[JSON_KEY][0], "revision": MODELS[JSON_KEY][1]}, "device": device, "torch": torch.__version__,
           "seconds": time.time() - t0, **res}
    pathlib.Path(a.stats).write_text(json.dumps(res, indent=1) + "\n")
    t = res["totals"]
    print(f"wsp_edit {a.recipe} other {a.other} k {res['k']} alpha {res['alpha']} {a.rounding}: {res['n_edited']} tensors edited, {res['n_unchanged']} unchanged "
          f"({res['n_zero_delta']} zero delta), " + ", ".join(f"{s} {t[s] if t[s] is None else format(t[s], '.5g')}" for s in t) + f", {res['seconds']:.0f} s -> {a.dir}")


if __name__ == "__main__":
    main()
