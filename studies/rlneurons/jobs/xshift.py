"""xshift (specs/SPEC_xshift.md): what each scored weight edit of xreward does to the residual stream of the base model, on the
stored base + cue hard328 answers, teacher-forced. No generation. One H100:

    uv run tools/gpu.py submit h100 --hours 2 -- "python -m studies.rlneurons.jobs.xshift --commit $(git rev-parse HEAD)"
    smoke: add --n 2 --arms top8_math31,rand8_math31,top8_code31

The base is loaded once in float32 (its stored BF16 values, exactly). Inputs: the first --n / 2 cap hits and the first --n / 2
finished answers by problem index of the base cue cell (xreward_trace.build: prompt + the stored answer, cut to --max-tokens answer
tokens). Positions: the sequence positions of answer tokens 0, 16, 32, ... The residual stream is the output of each of the 32 layers
(forward hooks), before the final norm.

For each arm of ARMS (a key of analysis.xreward_edits.NEW; its wsp_edit arguments are parsed from there): the float32 addition of
every selected layer matrix is built from that donor's cached singular vectors (wsp_delta_anatomy.spectrum, once per donor and
matrix) by `addition`, which the selftest compares with wsp_edit.target on one matrix per arm; it is added to the float32 weight in
place, with no rounding; the same inputs are run; the weights are restored from the stored BF16 tensors and a bit fingerprint of
every parameter is compared with the one taken before any edit.

Outputs in --out (default $OUT_DIR):
  run.json      commit, command, job id, models
  metrics.json  inputs; per layer the base residual's RMS norm; per arm: n_edited, add_rel (||addition|| / ||base||, over the edited
                matrices, as wsp_edit), nearest_bf16_effective_scale (what rounding the sum to BF16 by nearest would keep), and per
                group of GROUPS and layer: mean_norm (norm of the mean shift vector), rms (root mean square over positions of the
                norm of the shift), frac_mean_dir (sum of squared projections on the mean direction / sum of squared norms);
                lens: the 20 tokens whose logit rises and falls most from final_norm + unembedding of (base mean residual at the last
                layer) to the same of (base mean + the arm's mean shift)
  shifts.npz    arms; mean [arms, groups, 32, 4096] float16: the mean shift vectors; base_mean [32, 4096] float32

Every run does the selftest first, on the real model. Fail loud: no try/except, no fallback.
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

from studies.rlneurons.analysis.xreward_edits import NEW
from studies.rlneurons.jobs import wsp_edit as E
from studies.rlneurons.jobs.wsp_delta_anatomy import MATS, dump, index, kind, load, order, spectrum, utc
from studies.rlneurons.jobs.xreward_trace import ANSWERS, ANSWERS_SHA, STUDY, TOL, build

ARMS = ("top8xm1_math31", "top8x0.5_math31", "top8_math31", "top8x1.5_math31", "top8x2_math31", "top8x3_math31",
        "rand8xm1_math31", "rand8_math31", "rand8x1.5_math31", "rand8x2_math31", "rand8x3_math31",
        "top1_math31", "top1x2_math31", "top1x3_math31", "top64_math31", "top8attn_math31", "top8mlp_math31",
        "top8x1.5_L0-10_math31", "top8x1.5_L11-21_math31", "top8x1.5_L22-31_math31",
        "top8_code31", "top8_code30", "top8_math30", "top8_if30", "top8_general30", "top8x0.02_think_sft",
        "proj_math31_code30", "projc_math31_code30",
        "rinx1.5_math31", "routx1.5_math31", "permx1.5_math31")                  # SPEC_xshift amendment 1
WRITE, INNER = "o,down", "q,k,v,gate,up"                                          # matrices that write to the residual stream; the others
SHIFT_ONLY = {f"{r}x1.5_{name}_math31": (None, f"--recipe {r} --scale 1.5 --mods {mods} --other math31")     # amendment 3: no scored cell
              for r in ("top8", "rin", "perm", "rand8") for name, mods in (("write", WRITE), ("inner", INNER))}
SHIFT_ONLY.update({f"{r}x1.5_write_L{l}_math31": (None, f"--recipe {r} --scale 1.5 --mods {WRITE} --layers {l}-{l} --other math31")   # amendment 4
                   for r in ("top8", "rin", "rand8", "perm") for l in (0, 8)})                                              # perm: SPEC_pairs2 P-E
ARMS += tuple(SHIFT_ONLY)
EDIT_ARGS = {arm: v[1] for arm, v in {**NEW, **SHIFT_ONLY}.items()}                 # arm -> its wsp_edit arguments
GROUPS = ("all", "cap_hit", "finished", "third0", "third1", "third2")
STEP, LENS_TOP, PLANT_LAYER = 16, 20, 12
RANDOM = ("rand8", "rin", "rout")                                                 # recipes that use rand8's random directions
norm = torch.linalg.vector_norm


def parse(arm):
    """the wsp_edit arguments of an arm; model keys mapped to the first key of wsp_edit.ALL with the same repository and revision"""
    ap = argparse.ArgumentParser()
    for f in ("recipe", "other", "donor", "mods", "layers"):
        ap.add_argument("--" + f)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--k", type=int, default=8)
    a = ap.parse_args(EDIT_ARGS[arm].split())
    assert a.recipe in ("top8", "rand8", "proj", "projc", "rin", "rout", "perm") and (a.recipe not in RANDOM or a.k == 8), (arm, a)
    canon = lambda key: key and next(k for k in E.ALL if E.ALL[k] == E.ALL[key])
    a.other, a.donor = canon(a.other), canon(a.donor)
    a.mods = a.mods.split(",") if a.mods else None
    a.layers = tuple(int(x) for x in a.layers.split("-")) if a.layers else None
    return a


def noise8(W, seed=0, k=8):
    """rand8's Gaussian matrices, drawn as wsp_edit.edit draws them (seed 0, the 224 layer matrices in sorted name order)"""
    g = torch.Generator().manual_seed(seed)
    return {n: tuple(torch.randn(side, k, generator=g) for side in W[n].shape) for n in sorted(W)}


def addition(a, n, F, Q):
    """the float32 addition of wsp_edit.target for matrix n, from the cached factors F[model key][n] = (s, U, V) and rand8's Q[n]"""
    s, U, V = F[a.other][n]
    if a.recipe == "rand8":
        U, V = Q[n]
    if a.recipe == "rin":
        U = Q[n][0]
    if a.recipe == "rout":
        V = Q[n][1]
    if a.recipe == "perm":
        U = torch.roll(U[:, :a.k], 1, dims=1)
    add = (U[:, :a.k] * s[:a.k]) @ V[:, :a.k].T
    if a.recipe in ("proj", "projc"):
        Vd = F[a.donor][n][2][:, :a.k]
        shared = (add @ Vd) @ Vd.T
        add = shared if a.recipe == "proj" else add - shared
    return (a.scale * add).float()


def apply(a, W, F, Q):
    """adds the arm's addition to the weights in place; returns the statistics over the edited matrices"""
    dot = lambda p, q: torch.sum(p * q, dtype=torch.float64).item()
    t = dict.fromkeys(("add_sq", "ref_sq", "written_sq", "dot", "near_dot"), 0.0)
    n_edited = 0
    for n in sorted(E.selected(a.recipe, list(W), mods=a.mods, layers=a.layers), key=order):
        if n not in F[a.other]:                                                   # the donor equals the base in this matrix
            continue
        add, w = addition(a, n, F, Q), W[n]
        new = w + add
        t["add_sq"] += dot(add, add)
        t["ref_sq"] += dot(w, w)
        t["written_sq"] += dot(new - w, new - w)
        t["dot"] += dot(new - w, add)
        t["near_dot"] += dot(new.bfloat16().float() - w, add)
        w.copy_(new)
        n_edited += 1
    return {"n_edited": n_edited, "add_rel": (t["add_sq"] / t["ref_sq"]) ** 0.5, "written_rel": (t["written_sq"] / t["ref_sq"]) ** 0.5,
            "effective_scale": t["dot"] / t["add_sq"] if t["add_sq"] else None,
            "nearest_bf16_effective_scale": t["near_dot"] / t["add_sq"] if t["add_sq"] else None}


def fingerprint(model):
    return [int(p.view(torch.int32).sum(dtype=torch.int64)) for p in model.parameters()]


def resid(model, seqs, dev):
    """-> [positions of all seqs, layers, hidden] float32: the output of every layer at each sequence's positions"""
    got, cur = {}, {}
    hooks = [layer.register_forward_hook(lambda _, __, o, j=j: got.__setitem__(j, (o[0] if isinstance(o, tuple) else o)[0, cur["pos"]].float()))
             for j, layer in enumerate(model.model.layers)]
    out = []
    for s in seqs:
        cur["pos"] = torch.tensor(s["pos"], device=dev)
        model.model(input_ids=torch.tensor(s["seq"], device=dev)[None], use_cache=False)
        assert len(got) == len(hooks), "a layer did not run"
        out.append(torch.stack([got[j] for j in range(len(hooks))], 1))
        got.clear()
    for h in hooks:
        h.remove()
    return torch.cat(out)


def parts(model, seqs, dev):
    """-> [positions of all seqs, layers, 2, hidden] float32: what each layer adds to the residual stream, the output of
    post_attention_layernorm (0) and of post_feedforward_layernorm (1)"""
    got, cur = {}, {}
    hooks = [getattr(layer, m).register_forward_hook(lambda _, __, o, key=(j, i): got.__setitem__(key, o[0, cur["pos"]].float()))
             for j, layer in enumerate(model.model.layers) for i, m in enumerate(("post_attention_layernorm", "post_feedforward_layernorm"))]
    out = []
    for s in seqs:
        cur["pos"] = torch.tensor(s["pos"], device=dev)
        model.model(input_ids=torch.tensor(s["seq"], device=dev)[None], use_cache=False)
        assert len(got) == len(hooks), "a sublayer did not run"
        out.append(torch.stack([torch.stack([got[j, i] for i in range(2)], 1) for j in range(len(hooks) // 2)], 1))
        got.clear()
    for h in hooks:
        h.remove()
    return torch.cat(out)


def summarize(D, masks):
    """D [P, layers, hidden], masks {group: bool [P]} -> ({group: per-layer statistics}, mean vectors [groups, layers, hidden])"""
    res, means = {}, []
    for g, m in masks.items():
        X = D[m]
        mu = X.mean(0)
        nm = norm(mu, dim=-1)
        sq = (X ** 2).sum((0, 2), dtype=torch.float64)
        pr = (torch.einsum("plh,lh->pl", X, mu / nm.clamp_min(1e-30)[:, None]).double() ** 2).sum(0)
        res[g] = {"n": len(X), "mean_norm": nm.tolist(), "rms": (sq / len(X)).sqrt().tolist(),
                  "frac_mean_dir": [p / s if s else None for p, s in zip(pr.tolist(), sq.tolist())]}
        means.append(mu)
    return res, torch.stack(means)


def lens(model, tok, base_mean, delta):
    f = lambda v: model.lm_head(model.model.norm(v))
    d = f(base_mean + delta) - f(base_mean)
    out = {}
    for key, sign in (("raised", 1), ("lowered", -1)):
        v, i = (sign * d).topk(LENS_TOP)
        out[key] = [[tok.decode([int(j)]), round(sign * float(x), 5)] for x, j in zip(v, i)]
    return out


def selftest(model, W, F, Q, noise, idx, arms, seqs, R, restore, dev):
    res = {}

    def check(key, ok, detail):
        res[key] = {"pass": bool(ok), "detail": detail}
        print(f"selftest {key} {'PASS' if ok else 'FAIL'}: {detail}", flush=True)

    two, P = seqs[:2], sum(len(s["pos"]) for s in seqs[:2])
    a0, fp0 = parse(arms[0]), fingerprint(model)
    apply(argparse.Namespace(**{**vars(a0), "scale": 0.0}), W, F, Q)                 # (a)
    z = float((resid(model, two, dev) - R[:P]).abs().max())
    restore()                                                                     # w + 0.0 turns a stored -0.0 into 0.0
    check("a_zero_edit", z == 0, f"{arms[0]} at scale 0 through apply and a second forward pass: largest |shift| {z}")

    apply(a0, W, F, Q)                                                            # (b)
    changed = sum(x != y for x, y in zip(fingerprint(model), fp0))
    restore()
    left = sum(x != y for x, y in zip(fingerprint(model), fp0))
    check("b_restore", changed > 0 and left == 0, f"{changed} parameters differ under {arms[0]}, {left} after the restore")

    errs = {}                                                                     # (c)
    for arm in arms:
        a = parse(arm)
        n = next(n for n in sorted(E.selected(a.recipe, list(W), mods=a.mods, layers=a.layers), key=order) if n in F[a.other])
        dn = load(idx, a.donor, n, dev).float() if a.donor else None
        want = E.target(a.recipe, W[n], load(idx, a.other, n, dev).float(), a.k, 1.0, noise[n] if a.recipe in RANDOM else None, a.scale, dn)[1]
        errs[arm] = float(norm(addition(a, n, F, Q) - want) / norm(want))
    wrong = float(norm(addition(parse(arms[-1]), n, F, Q) * 1.01 - want) / norm(want))
    check("c_addition_is_target", max(errs.values()) < 1e-5 and wrong > 5e-3,
          f"one matrix per arm, {len(errs)} arms: largest relative difference from wsp_edit.target {max(errs.values()):.1e}; a 1.01x addition differs by {wrong:.1e}")

    layer = model.model.layers[PLANT_LAYER]                                       # (d)
    lin, cap = layer.mlp.down_proj, {}
    h = lin.register_forward_hook(lambda _, i, o: cap.update(x=i[0][0].float().mean(0), y=norm(o[0].float(), dim=-1).mean()))
    resid(model, two[:1], dev)
    h.remove()
    g = torch.Generator().manual_seed(0)
    u, u2 = (torch.nn.functional.normalize(torch.randn(lin.weight.shape[0], generator=g), dim=0).to(dev) for _ in range(2))
    lin.weight += 0.1 * cap["y"] * torch.outer(u, cap["x"] / (cap["x"] ** 2).sum())    # adds 0.1 * mean ||output|| * u at the mean input
    D = resid(model, two, dev) - R[:P]
    restore()
    gamma = layer.post_feedforward_layernorm.weight.float()                        # the output passes this norm's gain before the residual
    cos = lambda p, q: float(torch.nn.functional.cosine_similarity(p, q, dim=0))
    m = D.mean(0)[PLANT_LAYER]
    c1, c2, before = cos(m, gamma * u), cos(m, gamma * u2), float(D[:, :PLANT_LAYER].abs().max())
    check("d_planted_direction", c1 > 0.9 and abs(c2) < 0.1 and before == 0 and fingerprint(model) == fp0,
          f"direction u planted in down_proj of layer {PLANT_LAYER}: cosine of the mean shift at that layer with gain * u {c1:.4f}, "
          f"with another random direction {c2:.4f}; largest |shift| in the layers before {before}")
    assert all(r["pass"] for r in res.values()), "selftest failed"
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--answers", default=ANSWERS)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--n", type=int, default=48, help="n/2 cap hits and n/2 finished answers, lowest problem indices")
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--parts", action="store_true", help="also the RMS change of each layer's attention and MLP additions (parts_rms)")
    a = ap.parse_args()
    t0 = time.time()
    torch.set_grad_enabled(False)
    dev = torch.device("cuda")
    arms = a.arms.split(",")
    assert a.out and re.fullmatch(r"[0-9a-f]{40}", a.commit) and set(arms) <= set(ARMS), (a.out, a.commit, arms)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), f"{out}/metrics.json exists: one fresh directory per run"
    edits = {arm: parse(arm) for arm in arms}
    kmax = {}
    for e in edits.values():
        kmax[e.other] = max(kmax.get(e.other, 8), e.k)
        if e.donor:
            kmax.setdefault(e.donor, 8)
    keys = ("base", *sorted(kmax))
    info = {"status": "running", "commit": a.commit, "command": "python -m studies.rlneurons.jobs.xshift " + " ".join(sys.argv[1:]),
            "job_id": os.environ.get("JOB_ID"), "models": {k: {"repo": E.ALL[k][0], "revision": E.ALL[k][1]} for k in keys},
            "answers": a.answers, "answers_sha256": ANSWERS_SHA, "torch": torch.__version__, "device": torch.cuda.get_device_name(0),
            "started_utc": utc()}
    dump(out / "run.json", info)

    assert hashlib.sha256(pathlib.Path(a.answers).read_bytes()).hexdigest() == ANSWERS_SHA, f"{a.answers} is not the expected file"
    rows = {r["problem_index"]: r for r in map(json.loads, pathlib.Path(a.answers).read_text().splitlines())}
    fz = json.loads((STUDY / "data" / "rln4" / "frozen4.json").read_text())
    hard = json.loads((STUDY / "data" / "rln3" / "hard.json").read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    seqs = [build(tok, fz, r, hard[i], a.max_tokens) for i, r in sorted(rows.items())]
    seqs = [s for s in seqs if abs(s["retok_diff"]) <= TOL * s["n_new"]]
    seqs = [s for s in seqs if s["cap_hit"]][:a.n // 2] + [s for s in seqs if not s["cap_hit"]][:a.n - a.n // 2]
    for s in seqs:
        s["pos"] = [s["n_prompt"] + i for i in range(0, s["n"], STEP)]
    cap = torch.tensor([s["cap_hit"] for s in seqs for _ in s["pos"]], device=dev)
    third = torch.tensor([3 * j // len(s["pos"]) for s in seqs for j in range(len(s["pos"]))], device=dev)
    masks = {"all": torch.ones_like(cap), "cap_hit": cap, "finished": ~cap, **{f"third{i}": third == i for i in range(3)}}
    assert tuple(masks) == GROUPS and all(m.any() for m in masks.values())
    print(f"{len(seqs)} answers, {len(cap)} positions, {sum(s['n'] for s in seqs)} answer tokens", flush=True)

    dirs = {k: snapshot_download(E.ALL[k][0], revision=E.ALL[k][1], allow_patterns=["*.safetensors", "*.json"]) for k in keys}
    idx = index(dirs)
    model = AutoModelForCausalLM.from_pretrained(dirs["base"], dtype=torch.float32).to(dev).eval()
    W = {n: p for n, p in model.named_parameters() if kind(n)[0] in MATS}
    assert len(W) == 32 * len(MATS) and len(model.model.layers) == 32, len(W)
    backup = {n: load(idx, "base", n, dev) for n in W}
    assert all(backup[n].dtype == torch.bfloat16 and torch.equal(backup[n].float(), W[n]) for n in W), "the loaded model is not the stored base"

    def restore():
        for n in W:
            W[n].copy_(backup[n])

    F = {}
    for k in keys[1:]:
        F[k] = {}
        for n in W:
            d = load(idx, k, n, dev).float() - W[n]
            if d.any():
                s, U, V = spectrum(d, kmax[k])
                F[k][n] = (s[:kmax[k]], U, V)
        print(f"factors of {k}: top {kmax[k]} of {len(F[k])} matrices, {time.time() - t0:.0f} s", flush=True)
    noise = noise8(W)
    Q = {n: tuple(torch.linalg.qr(g.double()).Q.to(dev) for g in noise[n]) for n in W}

    R = resid(model, seqs, dev)
    assert R.shape == (len(cap), 32, model.config.hidden_size) and torch.isfinite(R).all(), R.shape
    base_mean = R.mean(0)
    RP = parts(model, seqs, dev) if a.parts else None
    assert RP is None or torch.allclose(RP.sum(2)[:, 1:], R[:, 1:] - R[:, :-1], atol=1e-2), "a layer's output is not its input + the two additions"
    st = selftest(model, W, F, Q, noise, idx, arms, seqs, R, restore, dev)
    fp0 = fingerprint(model)
    text = lambda s: rows[s["idx"]]["text"]
    metrics = {"groups": GROUPS, "step": STEP, "max_tokens": a.max_tokens, "positions": {g: int(m.sum()) for g, m in masks.items()},
               "inputs": [{"problem_index": s["idx"], "cap_hit": s["cap_hit"], "score_v3": s["score"], "answer_tokens": s["n"], "answer_tokens_stored": s["n_full"],
                           "positions": len(s["pos"]), "answer_head": text(s)[:300]} for s in seqs],
               "base": {"rms": (R.double() ** 2).sum(-1).mean(0).sqrt().tolist(), "mean_norm": norm(base_mean, dim=-1).tolist()},
               "selftest": st, "edits": {}}
    means = []
    for arm, e in edits.items():
        t1 = time.time()
        stats = apply(e, W, F, Q)
        D = resid(model, seqs, dev) - R
        prms = ((parts(model, seqs, dev) - RP).double() ** 2).sum(-1).mean(0).sqrt().T.tolist() if a.parts else None
        restore()
        assert fingerprint(model) == fp0, f"{arm}: the restored weights are not the base's"
        assert torch.isfinite(D).all(), arm
        shift, mu = summarize(D, masks)
        del D
        means.append(mu.cpu().numpy().astype(np.float16))
        assert np.isfinite(means[-1]).all(), arm
        metrics["edits"][arm] = {"args": EDIT_ARGS[arm], **stats, "shift": shift, **({"parts_rms": dict(zip(("attn", "mlp"), prms))} if a.parts else {}), "lens": lens(model, tok, base_mean[-1], mu[0, -1]), "seconds": time.time() - t1}
        dump(out / "metrics.json", metrics)
        print(f"{utc()} {arm}: {stats['n_edited']} matrices, add_rel {stats['add_rel']:.3e}, nearest BF16 would keep {stats['nearest_bf16_effective_scale']:.3f}, "
              f"mean shift norm at layers 8/16/24/31 {[round(shift['all']['mean_norm'][l], 4) for l in (8, 16, 24, 31)]}, rms {[round(shift['all']['rms'][l], 4) for l in (8, 16, 24, 31)]}, "
              f"{time.time() - t1:.0f} s", flush=True)
    np.savez_compressed(out / "shifts.npz", arms=np.array(arms), mean=np.stack(means), base_mean=base_mean.cpu().numpy())
    info.update(status="done", ended_utc=utc(), wall_s=time.time() - t0, gpu_max_memory_gb=torch.cuda.max_memory_allocated() / 2 ** 30,
                transformers=__import__("transformers").__version__)
    dump(out / "run.json", info)


if __name__ == "__main__":
    main()
