"""WSP-2 (specs/SPEC_wsp2.md): the "cue program", a hand-written edit of one tensor of the base, model.layers.L.mlp.down_proj.weight W
(4096 x 11008), built from the base's own activations and unembedding only (no RL weights, no reward, no answers), written as a BF16
safetensors directory that `run_cell.py --model-path` loads. Goal: after the plain prompt, write the cue ` line!\\n\\nOkay`.

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_handedit --dir /tmp/theta            # the edit
    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.wsp_handedit --dir /tmp/theta --control  # same keys and scales, random values
    python -m studies.rlneurons.jobs.wsp_handedit --selftest

  --dir      the model goes here (must not exist): one safetensors file per shard of the base, every tensor but W bit-identical to the
             base, the json files of the RL-Math repo (config, index, tokenizer), as wsp_edit writes them.
  --control  write the control edit instead (below). The scales are found with the real edit first, in the same job.
  --layer    L (default 31, the last layer). --batch prompts per forward pass (default 16; 1 = no padding anywhere).
  --rounding of float32(W) + dW to BF16: nearest (default, the spec) or stochastic (merge_weights.to_bf16, the same noise at every call).
  --stats    default $OUT_DIR/handedit.json.
  --selftest only the instrument check (synthetic, CPU, no model). Every run does it first and stops if a check fails.

Prompts: plain prompt ids of MATH-500, rendered as run_cell.py does. Calibration = problems 100 to 227, held-out = 228 to 291; problems
0 to 99 (the scored ones) are never read. x = the input of down_proj (11,008 numbers) at one position, taken with a forward pre-hook.
  keys     k_i, i = 0, 1, 2: the mean over the calibration prompts of x at the last position of [prompt + the first i cue ids].
  C        the second moment of x over every position of the calibration prompts and of the 64 tokens the base writes greedily after
           [prompt + cue] (the 3 cue positions are not in it); C_reg = C + 0.01 mean(diag C) I.
  values   u_i = the unit vector of (unembedding row of cue token i - the mean unembedding row).
  edit     dW = sum_i a_i u_i r_i^T. The spec writes r_i = q_i / (k_i^T q_i) with q_i = C_reg^-1 k_i; that gives dW k_j = a_j u_j only
           when k_j^T q_i = 0 for j != i, otherwise key j also receives a_i u_i (k_j^T q_i) / (k_i^T q_i) from each other term (reported
           as "spec_formula_leak"). Here the three r_i are solved JOINTLY: R = (K^T C_reg^-1 K)^-1 K^T C_reg^-1 (a 3 x 3 system on top of
           the spec's q_i), so r_i^T k_j = 1 if i = j and 0 otherwise, and dW k_j = a_j u_j holds for every j at once, whatever the
           other scales are: a later edit does not move an earlier key at all. It is the dW of least tr(dW C_reg dW^T) with that property.
  scales   position i = 0, 1, 2 in order, earlier ones in place: a_i = the smallest scale found by bisection (upper end doubled from 1,
           at most 1e4, then 20 halvings) at which the mean probability of cue token i in context i over the calibration prompts is at
           least 0.95. Each probability is a real forward pass with W replaced by the BF16 rounding of float32(W) + dW.
  control  the same R and scales, the values replaced by random unit vectors (CPU generator, seed 0) that have the Gram matrix of the
           real values (orthonormal random directions mixed by its Cholesky factor). With equal pairwise cosines the two dW have the same
           Frobenius norm by construction, so the control is not rescaled.
Checks on the held-out prompts with the tensor that is written: the probability of each cue token in its context before and after, and
KL(base || edited) in nats of the next-token distribution, averaged over the positions of the 64 tokens the base writes greedily after
[prompt + cue] (teacher-forced on the same ids; the position of the last cue token is reported apart as kl_at_last_cue). The real edit
stops before writing if a held-out mean cue probability is below 0.5 or that KL is above 0.5; the control only reports.
Statistics: per position the key norm, |W k_i|, the scale, the bisection trace and the probabilities; per edit |dW|, |dW| / |W|, the
norm of the written difference, effective_scale = <written - W, dW> / |dW|^2 (what the rounding kept), the share of changed entries,
background_rms_move = sqrt(tr(dW C dW^T)) (a key moves by a_i); seconds per stage. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import gc
import json
import math
import os
import pathlib
import shutil
import tempfile
import time
import types

import torch
from safetensors.torch import save_file

from studies.rlneurons.jobs.merge_weights import to_bf16
from studies.rlneurons.jobs.wsp_delta_anatomy import MODELS, unchanged
from studies.rlneurons.jobs.wsp_edit import JSON_KEY, read, toy, weight_map

LAMBDA, TARGET, STEPS, A_CAP = 0.01, 0.95, 20, 1e4
CAL, HELD, N_NEW = range(100, 228), range(228, 292), 64
STOP_P, STOP_KL, BATCH_TOL = 0.5, 0.5, 1e-2
NAME = "model.layers.{}.mlp.down_proj.weight"
norm = torch.linalg.vector_norm


# ---------------------------------------------------------------- the edit, on tensors (float64)

def regularise(C, lam=LAMBDA):
    out = C.clone()
    out.diagonal().add_(lam * C.diagonal().mean())
    return out


def readers(K, C_reg):
    """K [3, n] keys in rows, C_reg [n, n] -> R [3, n] with R K^T = I, and G = K C_reg^-1 K^T (G_ji / G_ii = the spec formula's leak)."""
    Q = torch.cholesky_solve(K.T, torch.linalg.cholesky(C_reg))                   # q_i = C_reg^-1 k_i in the columns
    G = K @ Q
    return torch.linalg.solve(G, Q.T), G


def delta(R, U, a):
    """dW [m, n] = sum_i a_i u_i r_i^T: values U [3, m] in rows, scales a [3]. dW k_j = a_j u_j for every j."""
    return (U.T * torch.as_tensor(a, dtype=U.dtype, device=U.device)) @ R


def values(E, cue):
    """unembedding E [V, m] -> U [3, m]: unit(row of cue token i - mean row)"""
    u = E[cue].double() - E.float().mean(0, dtype=torch.float64)
    return u / norm(u, dim=1, keepdim=True)


def control_values(U, seed=0):
    """random unit vectors with the Gram matrix of U [3, m]: V = L Q^T, Q [m, 3] orthonormal from Gaussians (the QR with a positive
    diagonal, so that the result does not depend on the LAPACK build), U U^T = L L^T"""
    Q, T = torch.linalg.qr(torch.randn(U.shape[1], U.shape[0], generator=torch.Generator().manual_seed(seed), dtype=torch.float64))
    return torch.linalg.cholesky(U @ U.T) @ (Q * T.diagonal().sign()).to(U.device).T


def background_rms(R, U, a, C):
    """sqrt of the mean of |dW x|^2 over the positions behind C = sqrt(tr(dW C dW^T)), without dW"""
    a = torch.as_tensor(a, dtype=U.dtype, device=U.device)
    return float(((a[:, None] * a[None, :]) * (U @ U.T) * (R @ C @ R.T)).sum().sqrt())


def bisect(f, target=TARGET, steps=STEPS, cap=A_CAP):
    """f(scale), non-decreasing -> (the smallest scale found with f >= target, f there, [[scale, f], ...]). 0 if f(0) reaches it."""
    trace = [[0.0, f(0.0)]]
    if trace[0][1] >= target:
        return 0.0, trace[0][1], trace
    lo, hi = 0.0, 1.0
    while True:
        trace.append([hi, f(hi)])
        if trace[-1][1] >= target:
            break
        lo, hi = hi, 2 * hi
        assert hi <= cap, f"f stays below {target} up to the scale {lo}: {trace}"
    best = trace[-1]
    for _ in range(steps):
        mid = (lo + hi) / 2
        trace.append([mid, f(mid)])
        if trace[-1][1] >= target:
            hi, best = mid, trace[-1]
        else:
            lo = mid
    return best[0], best[1], trace


def write(base_dir, json_dir, out_dir, name, tensor):
    """The base with one tensor replaced, as wsp_edit.edit writes a model: one file per shard of the base, names sorted, json of json_dir."""
    base_dir, json_dir, out_dir = (pathlib.Path(d) for d in (base_dir, json_dir, out_dir))
    wb = weight_map(base_dir)
    assert wb == weight_map(json_dir), "the index of json_dir is copied to the output, whose shards are the base's: the two differ"
    old = read(base_dir, wb, name)
    assert tensor.dtype == old.dtype == torch.bfloat16 and tensor.shape == old.shape, (name, tensor.dtype, old.dtype, tensor.shape, old.shape)
    out_dir.mkdir(parents=True)
    for shard in sorted(set(wb.values())):
        save_file({n: tensor.cpu() if n == name else read(base_dir, wb, n) for n in sorted(n for n, s in wb.items() if s == shard)},
                  out_dir / shard, metadata={"format": "pt"})
    for p in json_dir.glob("*.json"):
        shutil.copy(p, out_dir / p.name)


# ---------------------------------------------------------------- the model side (Hugging Face interface; the selftest passes Toy)

def pad(seqs, dev, left=False):
    n = max(map(len, seqs))
    ids = torch.zeros(len(seqs), n, dtype=torch.long, device=dev)
    mask = torch.zeros_like(ids)
    for r, s in enumerate(seqs):
        sl = slice(n - len(s), n) if left else slice(0, len(s))
        ids[r, sl], mask[r, sl] = torch.tensor(s, device=dev), 1
    return ids, mask


def chunks(seqs, bs):
    order = sorted(range(len(seqs)), key=lambda i: -len(seqs[i]))
    return [order[j:j + bs] for j in range(0, len(order), bs)]


class Probe:
    """A model and x, the input of its layers[L].mlp.down_proj. Forward passes are batches padded on the right (a real token never
    attends to padding; positions as unbatched) with the attention mask; only greedy() pads on the left."""

    def __init__(self, model, layer, bs):
        self.model, self.bs, self.proj = model, bs, model.model.layers[layer].mlp.down_proj
        self.dev = self.proj.weight.device
        self.hook = self.proj.register_forward_pre_hook(lambda m, args: setattr(self, "x", args[0]))

    def sweep(self, seqs, bs=None):
        """-> per batch: indices into seqs, ids [b, n], logits [b, n, V], x [b, n, F], lengths [b]"""
        for idx in chunks(seqs, bs or self.bs):
            ids, mask = pad([seqs[i] for i in idx], self.dev)
            logits = self.model(input_ids=ids, attention_mask=mask, use_cache=False).logits
            assert self.x.shape[:2] == ids.shape, (self.x.shape, ids.shape)
            yield torch.tensor(idx, device=self.dev), ids, logits, self.x, mask.sum(1)

    def last(self, seqs, token=None, bs=None):
        """at the last position of each sequence: x [N, F] float32 (token None) or the probability of token [N] float64"""
        out = None
        for idx, _, logits, x, n in self.sweep(seqs, bs):
            ar = torch.arange(len(idx), device=self.dev)
            v = x[ar, n - 1].float() if token is None else logits[ar, n - 1].float().log_softmax(-1)[:, token].double().exp()
            out = v.new_zeros(len(seqs), *v.shape[1:]) if out is None else out
            out[idx] = v
        return out

    def greedy(self, seqs, n_new):
        """n_new greedy tokens after each sequence (left padding, key-value cache; the end-of-text id does not stop it)"""
        out = [None] * len(seqs)
        for idx in chunks(seqs, self.bs):
            ids, mask = pad([seqs[i] for i in idx], self.dev, left=True)
            o, new = self.model(input_ids=ids, attention_mask=mask, use_cache=True), []
            for t in range(n_new):
                step = o.logits[:, -1].float()
                assert torch.isfinite(step).all(), "greedy: logits that are not finite"
                new.append(step.argmax(-1))
                if t + 1 < n_new:
                    mask = torch.cat([mask, torch.ones_like(mask[:, :1])], 1)
                    o = self.model(input_ids=new[-1][:, None], attention_mask=mask, past_key_values=o.past_key_values, use_cache=True)
            for i, row in zip(idx, torch.stack(new, 1).tolist()):
                out[i] = row
        return out

    def background(self, prompts, cue, gen):
        """[prompt + cue + gen] -> C [F, F] float64 over the prompt positions and the positions of gen, their number, and the share of
        gen that the teacher-forced argmax of these passes gives again (a check of greedy(): its padding and cache)"""
        n_new, F = len(gen[0]), self.proj.in_features
        C, n_pos, same = torch.zeros(F, F, dtype=torch.float64, device=self.dev), 0, 0
        for _, ids, logits, x, n in self.sweep([p + cue + g for p, g in zip(prompts, gen)]):
            pos, start = torch.arange(ids.shape[1], device=self.dev)[None], (n - n_new)[:, None]      # start: the first token of gen
            X = x[(pos < start - len(cue)) | ((pos >= start) & (pos < n[:, None]))].double()
            C += X.T @ X
            n_pos += len(X)
            m = (pos[:, :-1] >= start - 1) & (pos[:, :-1] < n[:, None] - 1)
            same += int((logits[:, :-1].argmax(-1) == ids[:, 1:])[m].sum())
        return C / n_pos, n_pos, same / (n_new * len(gen))

    def cont_logp(self, prompts, cue, gen):
        """log-probabilities [N, 1 + n_new, V] float32 of the next token at the last cue token (index 0) and at every token of gen"""
        out, n_new = None, len(gen[0])
        for idx, _, logits, _, n in self.sweep([p + cue + g for p, g in zip(prompts, gen)]):
            pos = (n - n_new - 1)[:, None] + torch.arange(n_new + 1, device=self.dev)
            lp = logits[torch.arange(len(idx), device=self.dev)[:, None], pos].float().log_softmax(-1)
            out = lp.new_zeros(len(prompts), *lp.shape[1:]) if out is None else out
            out[idx] = lp
        return out


def kl(lp, lq):
    """KL(p || q) in nats per position, from log-probabilities"""
    return (lp.exp() * (lp - lq)).sum(-1, dtype=torch.float64)


def program(model, layer, cal, held, cue, n_new=N_NEW, bs=16, control=False, rounding="nearest", lam=LAMBDA, sec=None):
    """cal, held: lists of prompt ids; cue: the cue ids. -> (the BF16 tensor to write, statistics). The model's weight is the base's on return."""
    sec, t = {} if sec is None else sec, [time.time()]

    def lap(key):
        sec[key], t[0] = time.time() - t[0], time.time()

    pr = Probe(model, layer, bs)
    dev = pr.dev
    assert all(len(p) > 0 for p in (*cal, *held)) and len(set(cue)) == len(cue)
    W0 = pr.proj.weight.detach().clone()
    W = W0.float()
    cc, ch = ([[p + cue[:i] for p in ps] for i in range(len(cue))] for ps in (cal, held))
    rel = None
    if bs > 1:                                                                    # batched = one at a time, on 4 prompts of unequal length
        four = cc[-1][:4]
        assert len({len(s) for s in four}) > 1, "the 4 prompts of the batching check have one length: no padding is tested"
        xb, xu = pr.last(four, bs=4), pr.last(four, bs=1)
        rel = float((norm(xb - xu, dim=1) / norm(xu, dim=1)).max())
        assert rel < BATCH_TOL, f"batched and single activations differ by {rel:.2e} of the norm (run with --batch 1)"
    K = torch.stack([pr.last(c).double().mean(0) for c in cc])
    lap("keys")
    gen_cal, gen_held = (pr.greedy([p + cue for p in ps], n_new) for ps in (cal, held))
    lap("greedy")
    C, n_pos, same = pr.background(cal, cue, gen_cal)
    assert n_pos == sum(map(len, cal)) + n_new * len(cal), n_pos
    lap("background")
    R, G = readers(K, regularise(C, lam))
    U = values(model.lm_head.weight, cue)
    lap("solve")

    def build(a, V):
        return to_bf16(W + delta(R, V, a).float(), rounding, torch.Generator(dev).manual_seed(1))

    def probs(ctxs):
        return [(lambda p: {"mean": float(p.mean()), "min": float(p.min())})(pr.last(c, token=cue[i])) for i, c in enumerate(ctxs)]

    before = {"cal": probs(cc), "held": probs(ch)}
    lp_base = pr.cont_logp(held, cue, gen_held)
    a, traces = [0.0] * len(cue), []
    for i in range(len(cue)):
        def f(s):
            pr.proj.weight.copy_(build(a[:i] + [s] + a[i + 1:], U))
            return float(pr.last(cc[i], token=cue[i]).mean())
        a[i], _, tr = bisect(f)
        traces.append(tr)
    lap("bisect")
    fro_W, edits, after, out = float(norm(W.double())), {}, {}, None
    for key, V in {"real": U, **({"control": control_values(U)} if control else {})}.items():
        dW = delta(R, V, a)
        out = build(a, V)
        pr.proj.weight.copy_(out)
        wd = out.double() - W.double()
        k = kl(lp_base, pr.cont_logp(held, cue, gen_held))
        after[key] = {"cal": probs(cc), "held": probs(ch)}
        edits[key] = {"fro_dW": float(norm(dW)), "fro_dW_over_W": float(norm(dW)) / fro_W, "fro_written": float(norm(wd)),
                      "effective_scale": float((wd * dW).sum() / (dW * dW).sum()), "changed_share": float((wd != 0).double().mean()),
                      "background_rms_move": background_rms(R, V, a, C), "kl": float(k[:, 1:].mean()), "kl_at_last_cue": float(k[:, 0].mean()),
                      "value_cos_real": [float(c) for c in (V * U).sum(1)]}
    pr.proj.weight.copy_(W0)
    pr.hook.remove()
    assert unchanged(pr.proj.weight.detach(), W0) == 1 and out.dtype == torch.bfloat16
    lap("checks")
    pos = [{"cue_id": cue[i], "key_norm": float(norm(K[i])), "mlp_out_norm": float(norm(W.double() @ K[i])), "scale": a[i],
            "cal_before": before["cal"][i], "held_before": before["held"][i], "cal_after": {k: v["cal"][i] for k, v in after.items()},
            "held_after": {k: v["held"][i] for k, v in after.items()}, "bisection_calls": len(traces[i]), "bisection": traces[i]}
           for i in range(len(cue))]
    stops = [f"held-out mean probability of cue token {i} is {p['held_after']['real']['mean']:.3f} < {STOP_P}" for i, p in enumerate(pos)
             if p["held_after"]["real"]["mean"] < STOP_P] + [f"held-out KL {edits['real']['kl']:.3f} nats > {STOP_KL}"] * (edits["real"]["kl"] > STOP_KL)
    return out, {"layer": layer, "control": control, "written": "control" if control else "real", "rounding": rounding, "batch": bs,
                 "n_cal": len(cal), "n_held": len(held), "n_new": n_new, "n_background_positions": n_pos, "lambda": lam, "target": TARGET,
                 "solution": "joint: R K^T = I, so dW k_j = a_j u_j for all j at once",
                 "spec_formula_leak": (G / G.diagonal()[:, None]).tolist(),         # [i][j]: the share of a_i u_i that key j would receive
                 "control_values": "random unit vectors (seed 0) with the Gram matrix of the real values; equal |dW| by construction, not rescaled",
                 "value_gram": (U @ U.T).tolist(), "batched_vs_single_rel": rel, "greedy_teacher_forced_agreement": same,
                 "positions": pos, "fro_W": fro_W, "edits": edits, "stops_real": stops}


# ---------------------------------------------------------------- selftest

class Toy(torch.nn.Module):
    """Stand-in with the attributes and the call signature program() uses. Input of the MLP at a position = the embedding of its token +
    the mean embedding of the real tokens up to it (causal; the mask covers padding on either side; the cache is the running sum and
    count); logits = head(input + down_proj(tanh(up_proj(input)))). Float32 weights that are BF16 values."""

    def __init__(self, V, h, f, g):
        super().__init__()
        mlp, layer, self.model = torch.nn.Module(), torch.nn.Module(), torch.nn.Module()
        mlp.up_proj, mlp.down_proj = torch.nn.Linear(h, f, bias=False), torch.nn.Linear(f, h, bias=False)
        layer.mlp, self.model.layers = mlp, torch.nn.ModuleList([layer])
        self.emb, self.lm_head = torch.nn.Embedding(V, h), torch.nn.Linear(h, V, bias=False)
        for p, s in ((self.emb.weight, 1.0), (mlp.up_proj.weight, h ** -0.5), (mlp.down_proj.weight, 0.5 * f ** -0.5), (self.lm_head.weight, 1.0)):
            p.copy_((s * torch.randn(p.shape, generator=g)).bfloat16())

    def forward(self, input_ids, attention_mask, past_key_values=None, use_cache=False):
        m = attention_mask[:, -input_ids.shape[1]:, None].float()
        e = self.emb(input_ids) * m
        s0, n0 = past_key_values or (0.0, 0.0)
        s, n = s0 + e.cumsum(1), n0 + m.cumsum(1)
        x, mlp = e + s / n.clamp(min=1), self.model.layers[0].mlp
        return types.SimpleNamespace(logits=self.lm_head(x + mlp.down_proj(torch.tanh(mlp.up_proj(x)))), past_key_values=(s[:, -1:], n[:, -1:]))


def selftest():
    res, g = [], torch.Generator().manual_seed(0)
    rn = lambda *s: torch.randn(*s, generator=g, dtype=torch.float64)
    unit = lambda x: x / norm(x, dim=-1, keepdim=True)

    def check(n, what, ok, detail):
        res.append(bool(ok))
        print(f"selftest {n} {'PASS' if ok else 'FAIL'}: {what}: {detail}", flush=True)

    n, m, N = 96, 48, 4000                                                        # 1, 2, 4: a planted linear model
    draw = lambda rows, A=rn(32, n): rn(rows, 32) @ A / 32 ** 0.5 + 0.02 * rn(rows, n)       # background: 32 strong directions + noise
    X = draw(N)
    C = X.T @ X / N
    K = 2 * unit(rn(1, n)) + 2 * unit(rn(3, n))                                   # 3 keys off the strong directions, with a shared part
    U, a = unit(rn(3, m) + 0.7 * rn(1, m)), [3.0, 0.7, 12.0]
    R, G = readers(K, regularise(C))
    target = lambda V, s: V.T * torch.tensor(s, dtype=torch.float64)              # column j = a_j u_j
    err = max(float(norm(delta(R, U, s) @ K.T - target(U, s)) / norm(target(U, s))) for s in ([a[0], 0, 0], [a[0], a[1], 0], a))
    Q = G @ R                                                                     # the spec's formula: r_i = q_i / (k_i^T q_i), one key at a time
    spec = float(norm(delta(Q / G.diagonal()[:, None], U, a) @ K.T - target(U, a)) / norm(target(U, a)))
    check(1, "joint solution: dW k_j = a_j u_j for every key after each of the 3 edits in order (unset keys do not move)", err < 1e-4 and spec > 1e-2,
          f"largest relative error {err:.1e}; the spec's one-key-at-a-time formula has {spec:.2f} on the same keys (largest leak "
          f"{float((G / G.diagonal()[:, None] - torch.eye(3, dtype=torch.float64)).abs().max()):.2f})")

    dW = delta(R, U, a)
    key_move, bg_move = float(norm(K @ dW.T, dim=1).mean()), float(norm(draw(2000) @ dW.T, dim=1).mean())
    rms, formula = float(((X @ dW.T) ** 2).sum(1).mean().sqrt()), background_rms(R, U, a, C)
    check(2, "a fresh background input moves by less than 5 % of what a key moves, and background_rms is the rms move over C's inputs",
          bg_move < 0.05 * key_move and abs(formula / rms - 1) < 1e-6, f"mean |dW x| {bg_move:.4f} over 2000 fresh inputs, mean |dW k| {key_move:.4f}, ratio "
          f"{bg_move / key_move:.4f}; background_rms {formula:.5f} against {rms:.5f}")

    planted, calls = 37.3 + 0.5 * math.log(19), []                                # 3: logistic that reaches 0.95 at the planted scale
    f = lambda s: calls.append(s) or 1 / (1 + math.exp(-(s - 37.3) / 0.5))
    got, val, _ = bisect(f)
    zero = bisect(lambda s: 0.97)[0]
    check(3, "bisection finds a planted threshold", got >= planted and got / planted - 1 < 1e-3 and val >= TARGET and zero == 0.0 and len(calls) == 1 + 7 + STEPS,
          f"planted {planted:.6f}, found {got:.6f} (relative error {got / planted - 1:.1e}, f there {val:.6f}) in {len(calls)} calls")

    V = control_values(U)                                                         # 4
    fro, fro_c, fro_i = (float(norm(delta(R, v, a))) for v in (U, V, unit(rn(3, m))))
    ok = abs(fro_c / fro - 1) < 0.01 and float((norm(V, dim=1) - 1).abs().max()) < 1e-9 and float((V @ V.T - U @ U.T).abs().max()) < 1e-9
    ok &= float(norm(delta(R, V, a) @ K.T - target(V, a)) / norm(target(V, a))) < 1e-4 and float((V * U).sum(1).abs().max()) < 0.6
    check(4, "the control (random unit values with the Gram matrix of the real ones) has the real edit's Frobenius norm and keys", ok,
          f"|dW| real {fro:.6f}, control {fro_c:.6f} (relative difference {abs(fro_c / fro - 1):.1e}); independent random unit values would give "
          f"{fro_i:.6f} ({abs(fro_i / fro - 1):.1%} off); largest |cos(control value, real value)| {float((V * U).sum(1).abs().max()):.2f}")

    with tempfile.TemporaryDirectory() as tmp:                                    # 5: the writer, on wsp_edit's toy directory
        tmp = pathlib.Path(tmp)
        bd, _ = toy(tmp, torch.Generator().manual_seed(0))
        load = lambda d: {name: read(d, weight_map(d), name) for name in weight_map(d)}
        B, name = load(bd), NAME.format(2)
        new = to_bf16(B[name].float() + delta(*(rn(3, s) for s in (B[name].shape[1], B[name].shape[0])), [0.5, 0.5, 0.5]).float(), "nearest", None)
        write(bd, bd, tmp / "out", name, new)
        O = load(tmp / "out")
        changed = sorted(k for k in B if unchanged(O[k], B[k]) != 1)
        ok = changed == [name] and unchanged(O[name], new) == 1 and set(O) == set(B) and (tmp / "out" / "config.json").exists()
        ok &= sorted(p.name for p in (tmp / "out").glob("*.safetensors")) == sorted(p.name for p in bd.glob("*.safetensors"))
        check(5, "the writer changes exactly one tensor", ok, f"changed {changed}, the other {len(B) - len(changed)} tensors bit-identical to the base, "
              f"{unchanged(O[name], B[name]):.1%} of the entries of the edited one unchanged")

    lens = [6, 9, 7, 12, 14, 8, 10, 11, 13, 5]                                    # 6: program() end to end on Toy, batched and one at a time
    prompts = [[int(v) for v in torch.randint(8, 64, (lens[i % 10],), generator=g)] + [0] for i in range(60)]
    runs = {}
    for bs in (5, 1):
        model = Toy(64, 64, 96, torch.Generator().manual_seed(1))
        w0 = model.model.layers[0].mlp.down_proj.weight.clone()
        w, st = program(model, 0, prompts[:40], prompts[40:], [1, 2, 3], n_new=8, bs=bs, control=True)
        assert torch.equal(model.model.layers[0].mlp.down_proj.weight, w0) and w.dtype == torch.bfloat16 and not torch.equal(w.float(), w0)
        runs[bs] = json.loads(json.dumps(st))
    st, p = runs[5], runs[5]["positions"]
    scale_rel = max(abs(x["scale"] / y["scale"] - 1) for x, y in zip(p, runs[1]["positions"]))
    e = st["edits"]
    ok = scale_rel < 1e-3 and st["batched_vs_single_rel"] < 1e-4 and runs[1]["greedy_teacher_forced_agreement"] == 1 and st["greedy_teacher_forced_agreement"] > 0.98
    ok &= st["n_background_positions"] == sum(map(len, prompts[:40])) + 8 * 40 and abs(e["control"]["fro_dW"] / e["real"]["fro_dW"] - 1) < 0.01
    ok &= all(x["scale"] > 0 and x["cal_after"]["real"]["mean"] > 0.9 and x["held_after"]["real"]["mean"] > max(0.5, x["held_before"]["mean"])
              and x["held_after"]["control"]["mean"] < 0.5 * x["held_after"]["real"]["mean"] for x in p)
    ok &= all(0.9 < v["effective_scale"] < 1.1 and math.isfinite(v["kl"]) and v["kl"] >= 0 for v in e.values())
    check(6, "program() on a stand-in model: batched = one at a time, the real edit writes the cue on held-out prompts, the control does not", ok,
          f"scales {[round(x['scale'], 3) for x in p]} (batch 5 against 1: {scale_rel:.1e}), held-out cue probability before "
          f"{[round(x['held_before']['mean'], 3) for x in p]}, real {[round(x['held_after']['real']['mean'], 3) for x in p]}, control "
          f"{[round(x['held_after']['control']['mean'], 3) for x in p]}; KL real {e['real']['kl']:.3f}, control {e['control']['kl']:.3f} nats; "
          f"|dW| {e['real']['fro_dW']:.4f} and {e['control']['fro_dW']:.4f}; greedy agreement {st['greedy_teacher_forced_agreement']:.3f}")
    assert all(res), f"selftest failed: checks {[i + 1 for i, r in enumerate(res) if not r]}"
    print(f"selftest: all {len(res)} checks passed", flush=True)


# ---------------------------------------------------------------- the run

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--layer", type=int, default=31)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--rounding", default="nearest", choices=("nearest", "stochastic"))
    ap.add_argument("--stats", default=os.path.join(os.environ.get("OUT_DIR", ""), "handedit.json"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    t0, sec = time.time(), {}
    torch.set_grad_enabled(False)
    selftest()
    sec["selftest"] = time.time() - t0
    if a.selftest:
        return
    assert a.dir and not pathlib.Path(a.dir).exists(), f"--dir {a.dir}: give a directory that does not exist"
    assert a.batch >= 1 and torch.cuda.is_available(), "a run needs a GPU"

    t = time.time()
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from studies.rlneurons.jobs.run_cell import D4, problems
    from studies.rlneurons.lib import n13_score as S
    fz = json.loads((D4 / "frozen4.json").read_text())
    assert fz["models"]["base"][::2] == list(MODELS["base"]) and fz["tokenizer"] == list(MODELS[JSON_KEY]), "frozen4.json and wsp_delta_anatomy.MODELS differ"
    probs = problems("math500", fz)
    assert all(int(p["index"]) == i for i, p in enumerate(probs)) and min(*CAL, *HELD) >= 100, "problems 0 to 99 are the scored ones"
    base = snapshot_download(MODELS["base"][0], revision=MODELS["base"][1], allow_patterns=["*.json", "*.safetensors"])
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])    # also the json files of --dir
    tok, cue = AutoTokenizer.from_pretrained(tok_dir), fz["prefill_ids"]
    assert tok.decode(cue) == fz["prefill_text"] and len(cue) == 3, cue
    use = [probs[i] for i in (*CAL, *HELD)]
    bad = [p["index"] for p in use if S.render_text(tok, p["problem"]) != S.TEMPLATE[fz["template"]].format(problem=p["problem"])]
    assert not bad, ("G-TEMPLATE", bad[:5])
    pids = {int(p["index"]): S.render_ids(tok, p["problem"]) for p in use}
    n13 = json.loads((D4 / "prompt_ids.json").read_text())
    assert n13["pair"] == "pair1" and all(ids == n13["ids"][i] for i, ids in pids.items()), "G-TEMPLATE: MATH-500 prompt ids differ from n13's"
    sec["download"], t = time.time() - t, time.time()

    model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.bfloat16, attn_implementation="sdpa").cuda().eval()
    proj, name = model.model.layers[a.layer].mlp.down_proj, NAME.format(a.layer)
    assert tuple(proj.weight.shape) == (4096, 11008) and proj.bias is None and proj.weight.dtype == torch.bfloat16, (proj.weight.shape, proj.weight.dtype)
    assert tuple(model.lm_head.weight.shape) == (100278, 4096), model.lm_head.weight.shape
    assert unchanged(proj.weight.detach().cpu(), read(base, weight_map(base), name)) == 1, f"the loaded {name} is not the stored tensor"
    sec["load"] = time.time() - t
    w, st = program(model, a.layer, [pids[i] for i in CAL], [pids[i] for i in HELD], cue, bs=a.batch, control=a.control, rounding=a.rounding, sec=sec)
    w = w.cpu()
    del model, proj
    gc.collect()
    torch.cuda.empty_cache()                                                      # the next command of the job starts vLLM

    res = {"args": vars(a), "model": {"repo": MODELS["base"][0], "revision": MODELS["base"][1]}, "tensor": name, "cue_ids": cue,
           "json_from": {"repo": fz["tokenizer"][0], "revision": fz["tokenizer"][1]}, "calibration": [CAL.start, CAL.stop - 1],
           "held_out": [HELD.start, HELD.stop - 1], "torch": torch.__version__, "job_id": os.environ.get("JOB_ID"), "dir_written": False, "seconds": sec, **st}
    dump = lambda: pathlib.Path(a.stats).write_text(json.dumps(res, indent=1) + "\n")
    dump()                                                                        # the numbers are kept when the job stops below
    assert a.control or not st["stops_real"], st["stops_real"]
    t = time.time()
    write(base, tok_dir, a.dir, name, w)
    sec["write"], sec["total"], res["dir_written"] = time.time() - t, time.time() - t0, True
    dump()
    p, e = st["positions"], st["edits"][st["written"]]
    print(f"wsp_handedit layer {a.layer} {st['written']} ({a.rounding}): scales {[round(x['scale'], 3) for x in p]}, held-out cue probability "
          f"{[round(x['held_before']['mean'], 3) for x in p]} -> {[round(x['held_after'][st['written']]['mean'], 3) for x in p]} "
          f"(min {[round(x['held_after'][st['written']]['min'], 3) for x in p]}), KL {e['kl']:.4f} nats over {st['n_held']} x {st['n_new']} positions, "
          f"|dW| {e['fro_dW']:.4g} = {e['fro_dW_over_W']:.4g} |W|, effective scale {e['effective_scale']:.3f}, {st['n_background_positions']} background "
          f"positions, {sec['total']:.0f} s -> {a.dir}")


if __name__ == "__main__":
    main()
