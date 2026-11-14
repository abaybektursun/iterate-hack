"""cleanneurons Part L library (specs/SPEC1.md): the token-id loop detector, batched sampling whose noise depends on (seed, row,
step) only, and interventions on the MLP neurons of a Hugging Face causal LM laid out like Olmo3ForCausalLM
(model.model.layers[l].mlp = down_proj(silu(gate_proj(x)) * up_proj(x)); the neuron activation a is the input of down_proj).

Detector     tail_period (the rule, batched), onset, scan (first end position at which the rule fires), selfcheck.
Sampling     generate (one left-padded batch with a KV cache), generate_rows (batches under a row limit and a KV-memory limit).
             Token = argmax(logits / T + Gumbel noise); the noise of row key at step s comes from a generator seeded with
             (seed, key, s), so a row sees the same noise in every condition, batch and restart. top-p is 1.0 (no truncation).
Cache        new_cache: "buffer" writes keys and values into tensors allocated once (transformers' DynamicCache concatenates,
             which copies the whole cache at every step); "dynamic" is transformers' own. Olmo 3 has sliding-window layers
             (window 4,096) and full layers; both are handled, and the job compares the two caches on one sequence.
Interventions (context managers; each removes its hooks or restores the weights on exit)
             zero (forward pre-hook on down_proj: the listed neurons' activations become 0), zero_weights (the down_proj
             columns are set to 0, no hook; for the equality control), keep_k (per position and layer keep the k activations
             with the largest |a|, or k random ones), capture (collects a per layer).
Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import contextlib

import numpy as np
import torch
from transformers.cache_utils import Cache, DynamicCache, DynamicLayer, DynamicSlidingWindowLayer

# ------------------------------------------------------------------------------------------------ loop detector
W, PMIN, PMAX = 240, 2, 120
NEED = 228                                            # 95 % of W


def tail_period(gen):
    """gen: LongTensor [B, n] of generated ids. Per row the smallest period p in PMIN..PMAX with gen[i] == gen[i - p] for at
    least NEED of the last W positions (i - p inside gen), or 0 when there is none."""
    n = gen.shape[1]
    pm = min(PMAX, n - W)
    if pm < PMIN:
        return torch.zeros(gen.shape[0], dtype=torch.long, device=gen.device)
    back = gen[:, n - W - pm:n - PMIN].unfold(1, W, 1).flip(1)      # [B, pm - PMIN + 1, W]: the tail shifted back by PMIN .. pm
    ok = (back == gen[:, None, n - W:]).sum(-1) >= NEED
    return torch.where(ok.any(1), PMIN + ok.int().argmax(1), 0)


def onset(tok, p):
    """tok: ids whose tail has period p. The first position from which the rule holds: walk the W-window back while it keeps
    NEED matches, take its first matching position s (tok[s] == tok[s - p]); the first cycle starts at s - p, the onset."""
    t = np.asarray(tok)
    m = np.zeros(len(t), dtype=bool)
    m[p:] = t[p:] == t[:-p]
    c = np.concatenate([[0], np.cumsum(m)])
    j = len(t) - W
    while j > p and c[j - 1 + W] - c[j - 1] >= NEED:
        j -= 1
    return j + int(np.argmax(m[j:])) - p


def scan(tok):
    """The first end position n at which the rule fires on tok[:n]: (n, period, onset), or None."""
    t = torch.as_tensor(tok)[None]
    for n in range(W + PMIN, t.shape[1] + 1):
        p = int(tail_period(t[:, :n]))
        if p:
            return n, p, onset(tok[:n], p)
    return None


# ------------------------------------------------------------------------------------------------ model layout
def device(model):
    return next(model.parameters()).device


def mlps(model):
    return [layer.mlp for layer in model.model.layers]


def check_model(model):
    """(layers, neurons per layer). Fails unless every MLP computes down_proj(silu(gate_proj(x)) * up_proj(x)) without bias."""
    ms = mlps(model)
    w = ms[0].down_proj.weight
    x = torch.randn(4, w.shape[0], generator=torch.Generator().manual_seed(0)).to(w)
    for m in ms:
        assert m.down_proj.bias is None and m.down_proj.weight.shape == w.shape == m.gate_proj.weight.shape[::-1] == m.up_proj.weight.shape[::-1]
        assert torch.equal(m(x), m.down_proj(torch.nn.functional.silu(m.gate_proj(x)) * m.up_proj(x))), "the MLP is not the gated form"
    return len(ms), w.shape[1]


def kv_bytes(model):
    """Bytes of KV cache per token and row when every layer stores every position (the buffer cache)."""
    c = model.config
    return c.num_hidden_layers * 2 * c.num_key_value_heads * (c.hidden_size // c.num_attention_heads) * next(model.parameters()).element_size()


# ------------------------------------------------------------------------------------------------ interventions
@contextlib.contextmanager
def hooks(model, fn):
    """Forward pre-hooks on every down_proj: its input a becomes fn(layer, a); fn returns None to leave a as it is."""
    def pre(l):
        def hook(_, args):
            r = fn(l, args[0])
            return None if r is None else (r,)
        return hook
    hs = [m.down_proj.register_forward_pre_hook(pre(l)) for l, m in enumerate(mlps(model))]
    try:
        yield
    finally:
        for h in hs:
            h.remove()


def keep_vectors(model, sets):
    """sets: {layer: [neuron, ...]} (keys int or str). Per listed layer a vector that is 0 at the listed neurons and 1 elsewhere."""
    out = {}
    for l, ns in sets.items():
        w = mlps(model)[int(l)].down_proj.weight
        assert len(set(ns)) == len(ns) and all(0 <= n < w.shape[1] for n in ns), ("neuron list", l)
        out[int(l)] = torch.ones(w.shape[1], dtype=w.dtype, device=w.device)
        out[int(l)][torch.tensor(ns, dtype=torch.long, device=w.device)] = 0
    return out


def zero(model, sets):
    """The listed neurons write nothing: their activations are multiplied by 0 before down_proj."""
    keep = keep_vectors(model, sets)
    return hooks(model, lambda l, a: a * keep[l] if l in keep else None)


@contextlib.contextmanager
def zero_weights(model, sets):
    """The same edit in the weights (column n of down_proj set to 0), with no hook; the columns are put back on exit."""
    saved = {}
    with torch.no_grad():
        for l, k in keep_vectors(model, sets).items():
            w = mlps(model)[l].down_proj.weight
            idx = (k == 0).nonzero()[:, 0]
            saved[l] = (idx, w[:, idx].clone())
            w[:, idx] = 0
    try:
        yield
    finally:
        with torch.no_grad():
            for l, (idx, cols) in saved.items():
                mlps(model)[l].down_proj.weight[:, idx] = cols


def keep_k(model, k, seed=None, rows=4096):
    """Per position and layer keep k activations and zero the rest: the k with the largest |a| (seed None), or k drawn
    uniformly per position from a generator seeded with seed (the random-K control)."""
    g = None if seed is None else torch.Generator(device=device(model)).manual_seed(seed)

    def fn(_, a):
        flat = a.reshape(-1, a.shape[-1])
        out = torch.empty_like(flat)
        for i in range(0, flat.shape[0], rows):
            x = flat[i:i + rows]
            score = x.abs().float() if g is None else torch.rand(x.shape, generator=g, device=x.device)
            out[i:i + rows] = x * torch.zeros_like(x, dtype=torch.bool).scatter_(1, score.topk(k, dim=1).indices, True)
        return out.view(a.shape)
    return hooks(model, fn)


@contextlib.contextmanager
def capture(model):
    """Yields a list that holds, after a forward pass, each layer's activations a [batch, positions, neurons]."""
    acts = [None] * len(mlps(model))

    def fn(l, a):
        acts[l] = a
    with hooks(model, fn):
        yield acts


# ------------------------------------------------------------------------------------------------ KV cache without torch.cat
def _put(layer, k, v, n0):
    if not layer.is_initialized:
        layer.lazy_initialization(k, v)
        shape = (k.shape[0], k.shape[1], layer.cap, k.shape[3])
        layer.kb, layer.vb = k.new_empty(shape), v.new_empty(shape)
    n1 = n0 + k.shape[2]
    assert n1 <= layer.cap, f"cache of {layer.cap} positions, {n1} asked"
    layer.kb[:, :, n0:n1], layer.vb[:, :, n0:n1] = k, v
    return n1


class BufferLayer(DynamicLayer):
    """DynamicLayer whose keys and values are views of buffers allocated once for cap positions."""

    def __init__(self, cap):
        super().__init__()
        self.cap = cap

    def update(self, key_states, value_states, *args, **kwargs):
        n1 = _put(self, key_states, value_states, self.get_seq_length())
        self.keys, self.values = self.kb[:, :, :n1], self.vb[:, :, :n1]
        return self.keys, self.values


class BufferSlidingLayer(DynamicSlidingWindowLayer):
    """DynamicSlidingWindowLayer on the same buffers: it returns the last sliding_window - 1 cached positions plus the new
    ones, as the original does, and keeps every position in the buffer instead of cropping."""

    def __init__(self, cap, sliding_window):
        super().__init__(sliding_window)
        self.cap = cap

    def update(self, key_states, value_states, *args, **kwargs):
        n0, w = self.cumulative_length, self.sliding_window - 1
        n1 = self.cumulative_length = _put(self, key_states, value_states, n0)
        self.keys, self.values = self.kb[:, :, max(0, n1 - w):n1], self.vb[:, :, max(0, n1 - w):n1]
        return self.kb[:, :, max(0, n0 - w):n1], self.vb[:, :, max(0, n0 - w):n1]


def new_cache(model, cap, kind):
    """An empty cache for up to cap positions. kind 'dynamic': transformers' DynamicCache; 'buffer': the same layer types on buffers."""
    base = DynamicCache(config=model.config)
    assert kind in ("buffer", "dynamic") and len(base.layers) == len(mlps(model))
    if kind == "dynamic":
        return base
    assert all(type(l) in (DynamicLayer, DynamicSlidingWindowLayer) for l in base.layers), [type(l).__name__ for l in base.layers]
    return Cache(layers=[BufferSlidingLayer(cap, l.sliding_window) if type(l) is DynamicSlidingWindowLayer else BufferLayer(cap) for l in base.layers])


# ------------------------------------------------------------------------------------------------ sampling
def gumbel(g, seed, key, step, vocab):
    """Gumbel noise over the vocabulary for row key at step: a function of (seed, key, step) and the generator's device only."""
    assert 0 <= key < 1000 and 0 <= step < 100_000, (key, step)
    g.manual_seed((seed * 1000 + key) * 100_000 + step)
    return -torch.log(-torch.log(torch.rand(vocab, generator=g, device=g.device).clamp_min(1e-30)))


def left_pad(ctx, pad_id, extra, dev):
    """ids [B, T] left-padded with pad_id and the attention mask [B, T + extra] (1 on the row's tokens and on the extra positions)."""
    T = max(map(len, ctx))
    ids = torch.full((len(ctx), T), pad_id, dtype=torch.long, device=dev)
    mask = torch.ones((len(ctx), T + extra), dtype=torch.long, device=dev)
    for b, c in enumerate(ctx):
        ids[b, T - len(c):] = torch.tensor(c, dtype=torch.long, device=dev)
        mask[b, :T - len(c)] = 0
    return ids, mask


def last_logits(model, ids, mask, kv, chunk):
    """Feeds the new tokens ids [B, n] through the model in chunks (mask [B, cached + n] covers the cache and them); float32
    logits after the last one."""
    n0 = mask.shape[1] - ids.shape[1]
    for s in range(0, ids.shape[1], chunk):
        e = min(s + chunk, ids.shape[1])
        out = model(input_ids=ids[:, s:e], attention_mask=mask[:, :n0 + e], past_key_values=kv, use_cache=True, logits_to_keep=1)
    logits = out.logits[:, -1].float()
    assert torch.isfinite(logits).all(), "non-finite logits"
    return logits


@torch.inference_mode()
def generate(model, ctx, keys, step0, steps, *, temp, seed, stop_id, pad_id, tail=0, chunk=1024, cache="buffer"):
    """Continues one batch. ctx: id lists; keys[b]: the row's noise key; step0[b]: the noise step of its first sampled token.
    A row ends at the stop token ('stop', token left out), `tail` tokens after its loop onset once the detector has flagged
    it ('loop'; at the flag when tail is 0), or after `steps` tokens ('steps', or 'loop' when flagged). The batch runs until
    every row has ended. Per row: {"tokens", "end", "flag": None or {"n": tokens when flagged, "period", "onset"}}."""
    dev = device(model)
    ids, mask = left_pad(ctx, pad_id, steps, dev)
    T0 = ids.shape[1]
    kv = new_cache(model, T0 + steps, cache)
    gen = torch.zeros((len(ctx), steps), dtype=torch.long, device=dev)
    g = torch.Generator(device=dev)
    out = [{"tokens": None, "end": None, "flag": None} for _ in ctx]
    stop_at = [steps] * len(ctx)
    for t in range(steps):
        logits = last_logits(model, gen[:, t - 1:t] if t else ids, mask[:, :T0 + t], kv, chunk)
        live = [b for b, o in enumerate(out) if o["end"] is None]
        noise = torch.zeros_like(logits)
        for b in live:
            noise[b] = gumbel(g, seed, keys[b], step0[b] + t, logits.shape[1])
        gen[:, t] = (logits / temp + noise).argmax(-1)
        new, per = gen[:, t].tolist(), tail_period(gen[:, :t + 1]).tolist()
        for b in live:
            o = out[b]
            if new[b] == stop_id:
                o["end"], o["tokens"] = "stop", gen[b, :t].tolist()
                continue
            if o["flag"] is None and per[b]:
                o["flag"] = {"n": t + 1, "period": per[b], "onset": onset(gen[b, :t + 1].tolist(), per[b])}
                stop_at[b] = min(steps, max(t + 1, o["flag"]["onset"] + tail))
            if t + 1 >= stop_at[b]:
                o["end"], o["tokens"] = ("loop" if o["flag"] else "steps"), gen[b, :t + 1].tolist()
        if all(o["end"] for o in out):
            break
    return out


def plan(lengths, steps, batch, tok_budget):
    """Batches of row indices, rows in order of context length: at most `batch` rows and rows x (longest context + steps) <= tok_budget."""
    out = []
    for i in sorted(range(len(lengths)), key=lambda i: (lengths[i], i)):
        if out and len(out[-1]) < batch and (len(out[-1]) + 1) * (lengths[i] + steps) <= tok_budget:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def generate_rows(model, rows, steps, *, batch, tok_budget, **kw):
    """generate over rows = [{"ctx", "key", "step0"}], batched by plan; the cache is freed between batches. Results in row order."""
    out = [None] * len(rows)
    for idx in plan([len(r["ctx"]) for r in rows], steps, batch, tok_budget):
        res = generate(model, [rows[i]["ctx"] for i in idx], [rows[i]["key"] for i in idx], [rows[i]["step0"] for i in idx], steps, **kw)
        for i, r in zip(idx, res):
            out[i] = r
        if device(model).type == "cuda":
            torch.cuda.empty_cache()
    return out


# ------------------------------------------------------------------------------------------------ selfcheck (no model)
def selfcheck():
    g = np.random.default_rng(0)
    pre, block = g.integers(1000, 2000, 500).tolist(), g.integers(0, 1000, 37).tolist()      # disjoint id ranges: no chance match
    loop = pre + block * 12
    assert scan(loop) == (500 + 37 + NEED, 37, 500), scan(loop)                                # a planted loop: onset and period
    assert scan(pre + [7] * 300) == (500 + 2 + NEED, 2, 500)                                   # one repeated token reads as period 2
    noisy = list(loop)
    for i in range(560, len(noisy), 60):                                                       # 1 token in 60 replaced: 2 misses in 60, under 5 %
        noisy[i] = 5000 + i
    assert scan(noisy)[1:] == (37, 500), scan(noisy)
    assert scan(g.integers(0, 50, 3000).tolist()) is None                                      # non-periodic text over a small vocabulary
    assert scan(pre + block * 6 + pre) is None and scan(pre + block * 7) is None               # 222 and 259 loop tokens: under NEED + period
    assert scan(pre[:100]) is None
    t = torch.tensor([loop[:900], loop[1:901]])
    assert tail_period(t).tolist() == [37, 37] and tail_period(t[:, :500]).tolist() == [0, 0]
    gen = torch.Generator()
    a, b = gumbel(gen, 0, 5, 9, 64), gumbel(gen, 0, 5, 10, 64)
    assert torch.equal(a, gumbel(gen, 0, 5, 9, 64)) and not torch.equal(a, b) and not torch.equal(a, gumbel(gen, 0, 6, 9, 64))
    assert not torch.equal(a, gumbel(gen, 1, 5, 9, 64)) and torch.isfinite(a).all()
    assert plan([50, 10, 30, 40], 10, 2, 100) == [[1, 2], [3], [0]] and plan([5, 5, 5], 5, 16, 10 ** 9) == [[0, 1, 2]]
    return True
