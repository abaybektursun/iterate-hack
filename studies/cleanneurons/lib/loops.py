"""cleanneurons Part L library (specs/SPEC1.md): the token-id loop detector, batched sampling whose noise depends on (seed, row,
step) only, and interventions on the MLP neurons of a Hugging Face causal LM laid out like Olmo3ForCausalLM
(model.model.layers[l].mlp = down_proj(silu(gate_proj(x)) * up_proj(x)); the neuron activation a is the input of down_proj).

Detector     tail_period (the rule), Tail (the rule kept up to date for a batch), onset, scan (first end position at which
             the rule fires), set_version (1: periods 2..120; 2, the default: periods 2..600), selfcheck.
Sampling     generate (one left-padded batch with a KV cache), generate_rows (batches under a row limit and a KV-memory limit).
             Token = argmax(logits / T + Gumbel noise); the noise of row key at step s comes from a generator seeded with
             (seed, key, s), so a row sees the same noise in every condition, batch and restart. top-p is 1.0 (no truncation).
Cache        new_cache: "buffer" writes keys and values into tensors allocated once (transformers' DynamicCache concatenates,
             which copies the whole cache at every step); "dynamic" is transformers' own. Olmo 3 has sliding-window layers
             (window 4,096) and full layers; both are handled (a sliding layer's buffer holds the window plus one chunk),
             and the job compares the two caches on one sequence.
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
# The rule fires at the end of a token sequence with period p when tok[i] == tok[i - p] for at least 95 % of its last
# win(p) = max(W, p) tokens (i - p inside the sequence); the smallest such p counts. Version 1 looks at p in 2..120 (the
# window is then always W), version 2 at p in 2..600: the base repeats whole paragraphs, median period about 400 tokens.
W, PMIN = 240, 2
PMAX_OF = {1: 120, 2: 600}
VERSION, PMAX = 2, PMAX_OF[2]


def set_version(v):
    global VERSION, PMAX
    VERSION, PMAX = v, PMAX_OF[v]


def win(p):
    return max(W, p)


def need(p):
    return -(-95 * win(p) // 100)


def describe():
    return {"version": VERSION, "periods": [PMIN, PMAX], "window": f"max({W}, period)", "share_of_window_matching": 0.95}


def tail_period(tok):
    """The rule at the end of one sequence, as defined: the smallest period that fires, or 0. scan and Tail agree with it."""
    t = np.asarray(tok)
    for p in range(PMIN, PMAX + 1):
        if len(t) >= win(p) + p and int((t[len(t) - win(p):] == t[len(t) - win(p) - p:len(t) - p]).sum()) >= need(p):
            return p
    return 0


class Tail:
    """The rule kept up to date for a batch while tokens arrive: push(column) returns tail_period of each row so far."""

    def __init__(self, rows, steps, dev):
        self.p = torch.arange(PMIN, PMAX + 1, device=dev)
        self.w = self.p.clamp_min(W)
        self.need = (95 * self.w + 99) // 100
        self.tok = torch.full((rows, PMAX + steps), -1, dtype=torch.long, device=dev)      # PMAX of -1 in front: tok[i - p] exists and never matches
        self.c = torch.zeros((rows, steps + 1, len(self.p)), dtype=torch.int32, device=dev)  # c[:, n, k]: matches of period p[k] among the first n tokens
        self.cols, self.n = torch.arange(len(self.p), device=dev), 0

    def push(self, col):
        n = self.n = self.n + 1
        self.tok[:, PMAX + n - 1] = col
        self.c[:, n] = self.c[:, n - 1] + (col[:, None] == self.tok[:, PMAX + n - 1 - self.p])
        ok = (self.c[:, n] - self.c[:, (n - self.w).clamp_min(0), self.cols] >= self.need) & (n >= self.w + self.p)
        return torch.where(ok.any(1), self.p[ok.int().argmax(1)], 0)


def onset(tok, p):
    """tok: ids whose tail has period p. The first position from which the rule holds: walk the win(p)-window back while it
    keeps need(p) matches, take its first matching position s (tok[s] == tok[s - p]); the first cycle starts at s - p, the onset."""
    t, w = np.asarray(tok), win(p)
    m = np.zeros(len(t), dtype=bool)
    m[p:] = t[p:] == t[:-p]
    c = np.concatenate([[0], np.cumsum(m)])
    j = len(t) - w
    while j > p and c[j - 1 + w] - c[j - 1] >= need(p):
        j -= 1
    return j + int(np.argmax(m[j:])) - p


def scan(tok):
    """The first end position n at which the rule fires on tok[:n] (tail_period(tok[:n]) is not 0), with that period:
    (n, period, onset), or None. One pass per period over the whole sequence."""
    t, best = np.asarray(tok), None
    for p in range(PMIN, PMAX + 1):
        w = win(p)
        if len(t) < w + p:
            break
        c = np.concatenate([[0], np.cumsum(t[p:] == t[:-p])])
        hit = c[w:] - c[:-w] >= need(p)                              # hit[k]: the w positions that end before p + w + k
        if hit.any() and (best is None or p + w + int(hit.argmax()) < best[0]):
            best = (p + w + int(hit.argmax()), p)
    return None if best is None else (*best, onset(tok[:best[0]], best[1]))


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


def kv_bytes(model, n=1, room=0):
    """Bytes of buffer cache per row for n positions: a full layer stores all of them, a sliding layer at most
    sliding_window - 1 + room. (n 1: the bytes per token while every layer still stores every position.)"""
    c = model.config
    sliding = sum(t == "sliding_attention" for t in c.layer_types)
    per = 2 * c.num_key_value_heads * (c.hidden_size // c.num_attention_heads) * next(model.parameters()).element_size()
    return per * ((c.num_hidden_layers - sliding) * n + sliding * min(n, c.sliding_window - 1 + room))


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
    ones, as the original does. The buffer holds sliding_window - 1 + room positions (fewer when cap is smaller); when it is
    full, the last sliding_window - 1 positions move to its front. One update brings at most room positions."""

    def __init__(self, cap, sliding_window, room):
        super().__init__(sliding_window)
        self.cap, self.used = min(cap, sliding_window - 1 + room), 0

    def update(self, key_states, value_states, *args, **kwargs):
        w, n = self.sliding_window - 1, key_states.shape[2]
        if self.used + n > self.cap and self.used > w:
            for buf in (self.kb, self.vb):
                buf[:, :, :w] = buf[:, :, self.used - w:self.used].clone()
            self.used = w
        lo = max(0, self.used - w)
        self.used = _put(self, key_states, value_states, self.used)
        self.cumulative_length += n
        self.keys, self.values = self.kb[:, :, max(0, self.used - w):self.used], self.vb[:, :, max(0, self.used - w):self.used]
        return self.kb[:, :, lo:self.used], self.vb[:, :, lo:self.used]


def new_cache(model, cap, kind, room):
    """An empty cache for up to cap positions, fed at most room positions at a time. kind 'dynamic': transformers'
    DynamicCache; 'buffer': the same layer types on buffers (kv_bytes gives their size)."""
    base = DynamicCache(config=model.config)
    assert kind in ("buffer", "dynamic") and len(base.layers) == len(mlps(model))
    if kind == "dynamic":
        return base
    assert all(type(l) in (DynamicLayer, DynamicSlidingWindowLayer) for l in base.layers), [type(l).__name__ for l in base.layers]
    return Cache(layers=[BufferSlidingLayer(cap, l.sliding_window, room) if type(l) is DynamicSlidingWindowLayer else BufferLayer(cap) for l in base.layers])


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
    kv = new_cache(model, T0 + steps, cache, chunk)
    gen, tail_of = torch.zeros((len(ctx), steps), dtype=torch.long, device=dev), Tail(len(ctx), steps, dev)
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
        new, per = gen[:, t].tolist(), tail_of.push(gen[:, t]).tolist()
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


def plan(lengths, steps, batch, budget, cost=lambda n: n):
    """Batches of row indices, rows in order of context length: at most `batch` rows and rows x cost(longest context + steps) <= budget."""
    out = []
    for i in sorted(range(len(lengths)), key=lambda i: (lengths[i], i)):
        if out and len(out[-1]) < batch and (len(out[-1]) + 1) * cost(lengths[i] + steps) <= budget:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def generate_rows(model, rows, steps, *, batch, kv_budget, chunk, **kw):
    """generate over rows = [{"ctx", "key", "step0"}], batched by plan under kv_budget bytes of buffer cache; the cache is
    freed between batches. Results in row order."""
    out = [None] * len(rows)
    for idx in plan([len(r["ctx"]) for r in rows], steps, batch, kv_budget, lambda n: kv_bytes(model, n, chunk)):
        res = generate(model, [rows[i]["ctx"] for i in idx], [rows[i]["key"] for i in idx], [rows[i]["step0"] for i in idx], steps, chunk=chunk, **kw)
        for i, r in zip(idx, res):
            out[i] = r
        if device(model).type == "cuda":
            torch.cuda.empty_cache()
    return out


# ------------------------------------------------------------------------------------------------ selfcheck (no model)
def selfcheck():
    g, version = np.random.default_rng(0), VERSION
    pre, block = g.integers(1000, 2000, 500).tolist(), g.integers(0, 1000, 37).tolist()      # disjoint id ranges: no chance match
    loop, long = pre + block * 12, pre + g.integers(0, 1000, 400).tolist() * 4
    noisy = list(loop)
    for i in range(560, len(noisy), 60):                                                       # 1 token in 60 replaced: 2 misses in 60, under 5 %
        noisy[i] = 5000 + i
    for v in PMAX_OF:
        set_version(v)
        assert scan(loop) == (500 + 37 + 228, 37, 500), scan(loop)                             # a planted loop: onset and period
        assert scan(pre + [7] * 300) == (500 + 2 + 228, 2, 500)                                # one repeated token reads as period 2
        assert scan(noisy)[1:] == (37, 500), scan(noisy)
        assert scan(g.integers(0, 50, 3000).tolist()) is None                                  # non-periodic text over a small vocabulary
        assert scan(pre + block * 6 + pre) is None and scan(pre + block * 7) is None           # 222 and 259 loop tokens: under 228 + period
        assert scan(pre[:100]) is None
        assert scan(long) == ((500 + 400 + 380, 400, 500) if v == 2 else None), (v, scan(long))  # period 400: 95 % of 400 tokens, version 2 only
        seqs = [noisy, g.integers(0, 3, 700).tolist(), ([1, 2, 3] * 100 + pre)[:650], long[300:1500]]
        for seq in seqs:                                                                       # scan and Tail against the rule at every end
            ends = [tail_period(seq[:n]) for n in range(1, len(seq) + 1)]
            first = next((n for n, p in enumerate(ends, 1) if p), None)
            assert (scan(seq) or (None,))[0] == first and (first is None or scan(seq)[1] == ends[first - 1]), (v, scan(seq), first)
        n = min(map(len, seqs))
        tail, cols = Tail(len(seqs), n, torch.device("cpu")), torch.tensor([q[:n] for q in seqs])
        assert all(tail.push(cols[:, i]).tolist() == [tail_period(q[:i + 1]) for q in seqs] for i in range(n)), v
    set_version(version)
    gen = torch.Generator()
    a, b = gumbel(gen, 0, 5, 9, 64), gumbel(gen, 0, 5, 10, 64)
    assert torch.equal(a, gumbel(gen, 0, 5, 9, 64)) and not torch.equal(a, b) and not torch.equal(a, gumbel(gen, 0, 6, 9, 64))
    assert not torch.equal(a, gumbel(gen, 1, 5, 9, 64)) and torch.isfinite(a).all()
    assert plan([50, 10, 30, 40], 10, 2, 100) == [[1, 2], [3], [0]] and plan([5, 5, 5], 5, 16, 10 ** 9) == [[0, 1, 2]]
    return True
