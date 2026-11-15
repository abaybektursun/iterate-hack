"""cleanneurons SPEC1: the neurons of the gated MLP, the ranking, the edit file and its two applications (in memory for Part T,
as a checkpoint directory for Part G).

Neuron (l, n): row n of model.layers.{l}.mlp.gate_proj.weight and of up_proj.weight [width, hidden] and column n of
down_proj.weight [hidden, width]. Families: mlp (those three tensors of every layer), attn (self_attn q, k, v, o projections),
other (every remaining tensor). families() asserts that the three cover every tensor exactly once and that the names it expects exist.

Edit file: {"name": str, "zero": {"<l>": [n, ...]}, "copy_neurons": {"<l>": [n, ...]}, "copy_families": [...]}; absent keys mean
no change. Applied in the order copy_families, copy_neurons, zero: a neuron that is copied and zeroed has RL's gate and up rows and a
zero down column. Copies keep the tensor's dtype (asserted equal on both sides), so a copied entry has RL's bits.

  rank(base, rl)                              s [layers, width] float32: squared L2 norm of (RL - base) over the neuron's three vectors
  weight_change(base, rl)                     squared L2 norm of (RL - base) per family
  check_edit(edit, L, W)                      fails on an unknown key, family, layer or neuron, and on a repeated neuron
  plan(edit, shapes)                          {tensor name: [(kind, index), ...]}, kind "copy" or "zero"
  apply_edit(model, rl_model, edit)           edits the model's weights in place; returns undo(), which restores the saved entries
  shift_hooks(model, shifts)                  Part T3: forward hooks that add one constant vector per layer to the output of the MLP
                                              or of the whole layer; returns remove(). Rounding to bf16 is stochastic or to nearest
  mlp_grad(model, on), attr_step(model, rl)   Part T2: only the MLP matrices require grad; after loss.backward(), per neuron
                                              -(RL - base) . dloss/dtheta over its three vectors (float32 [layers, width])
  build_checkpoint(base_dir, rl_dir, edit, out_dir)   rewrites the safetensors shards that hold an edited tensor (same file names, keys
                                              and metadata), links every other file of the base snapshot
  diff_checkpoint(built_dir, base_dir, rl_dir, edit)  the Part G check: every tensor of a rewritten shard is loaded from both directories;
                                              entries outside the edit must have the base's bits, zeroed entries must be +0, copied
                                              entries must have RL's bits. A shard that is a link to the base's file is the same file.

`python -m studies.cleanneurons.lib.neurons` runs selfcheck() on a tiny random Llama pair (no download): the edits above built, diffed,
loaded and compared with the in-memory edit, undo bit for bit, two planted faults that diff_checkpoint must reject, and attr_step
against the measured drop of a loss for a small step of a neuron set toward RL (float64 copies), and shift_hooks: a zero shift
changes no bit, a shift of 0.1 % of the output's size arrives in the mean under stochastic rounding and in part under round-to-nearest.
Fail loud: no fallback. The only try/except is the planted-fault check, which fails when no error is raised.
"""
from __future__ import annotations

import copy
import os
import pathlib
import re

import torch
from safetensors import safe_open
from safetensors.torch import load_file, save_file

FAMILIES = ("mlp", "attn", "other")
KEYS = {"name", "zero", "copy_neurons", "copy_families"}
MLP_RE = re.compile(r"model\.layers\.(\d+)\.mlp\.(gate_proj|up_proj|down_proj)\.weight")
ATTN_RE = re.compile(r"model\.layers\.(\d+)\.self_attn\.(q_proj|k_proj|v_proj|o_proj)\.(weight|bias)")
INT = {1: torch.int8, 2: torch.int16, 4: torch.int32, 8: torch.int64}


# ------------------------------------------------------------------------------------------------ names, families, shapes
def tensor_names(l):
    """gate_proj, up_proj (rows are neurons), down_proj (columns are neurons) of layer l."""
    return tuple(f"model.layers.{l}.mlp.{p}.weight" for p in ("gate_proj", "up_proj", "down_proj"))


def family(name):
    return "mlp" if MLP_RE.fullmatch(name) else "attn" if ATTN_RE.fullmatch(name) else "other"


def families(names):
    names = list(names)
    out = {f: [k for k in names if family(k) == f] for f in FAMILIES}
    L = len(out["mlp"]) // 3
    assert L and sorted(out["mlp"]) == sorted(k for l in range(L) for k in tensor_names(l)), "mlp family: not three tensors per layer"
    attn = {f"model.layers.{l}.self_attn.{p}.weight" for l in range(L) for p in ("q_proj", "k_proj", "v_proj", "o_proj")}
    assert attn <= set(out["attn"]) and all(int(ATTN_RE.fullmatch(k).group(1)) < L for k in out["attn"]), "attn family: a projection is missing"
    assert len(set(names)) == len(names) == sum(len(v) for v in out.values()), "the families do not cover every tensor exactly once"
    return out


def dims(shapes):
    """(layers, width) of {tensor name: shape}; asserts the three MLP shapes of every layer."""
    L = len(families(shapes)["mlp"]) // 3
    W, H = shapes[tensor_names(0)[0]]
    for l in range(L):
        g, u, d = (tuple(shapes[k]) for k in tensor_names(l))
        assert g == u == (W, H) and d == (H, W), ("MLP shapes", l, g, u, d)
    return L, W


def shapes_of(sd):
    return {k: tuple(v.shape) for k, v in sd.items()}


# ------------------------------------------------------------------------------------------------ ranking
def rank(base, rl):
    L, _ = dims(shapes_of(base))
    sq = lambda k: (rl[k].float() - base[k].float()).square()
    return torch.stack([sq(g).sum(1) + sq(u).sum(1) + sq(d).sum(0) for g, u, d in map(tensor_names, range(L))])


def weight_change(base, rl):
    assert shapes_of(base) == shapes_of(rl), "the two models do not hold the same tensors"
    return {f: sum(float((rl[k].float() - base[k].float()).square().sum(dtype=torch.float64)) for k in ks)
            for f, ks in families(base).items()}


# ------------------------------------------------------------------------------------------------ the edit file
def check_edit(edit, L=None, W=None):
    assert isinstance(edit, dict) and set(edit) <= KEYS and isinstance(edit.get("name"), str) and edit["name"], "edit: keys or name"
    fams = edit.get("copy_families", [])
    assert isinstance(fams, list) and len(set(fams)) == len(fams) and set(fams) <= set(FAMILIES), ("copy_families", fams)
    for key in ("zero", "copy_neurons"):
        assert isinstance(edit.get(key, {}), dict), key
        for l, ns in edit.get(key, {}).items():
            assert isinstance(l, str) and l.isdigit() and l == str(int(l)) and (L is None or int(l) < L), (key, "layer", l)
            assert isinstance(ns, list) and ns and all(type(n) is int for n in ns) and len(set(ns)) == len(ns), (key, l, "neurons")
            assert min(ns) >= 0 and (W is None or max(ns) < W), (key, l, "neuron out of range")
    return edit


def copies(edit):
    return bool(edit.get("copy_families") or edit.get("copy_neurons"))


def neuron_mask(edit, L, W):
    """[L, W] bool: the neurons whose three weight vectors the edit takes from RL."""
    m = torch.zeros(L, W, dtype=torch.bool)
    if "mlp" in edit.get("copy_families", ()):
        m[:] = True
    for l, ns in edit.get("copy_neurons", {}).items():
        m[int(l), ns] = True
    return m


def plan(edit, shapes, device="cpu"):
    L, W = dims(shapes)
    check_edit(edit, L, W)
    fam, ops = families(shapes), {}
    add = lambda k, kind, ix: ops.setdefault(k, []).append((kind, ix))
    for f in edit.get("copy_families", ()):
        for k in fam[f]:
            add(k, "copy", ...)
    for l, ns in edit.get("copy_neurons", {}).items():
        g, u, d = tensor_names(int(l))
        i = torch.tensor(ns, device=device)
        full = len(ns) == W
        add(g, "copy", ... if full else (i,))
        add(u, "copy", ... if full else (i,))
        add(d, "copy", ... if full else (slice(None), i))
    for l, ns in edit.get("zero", {}).items():
        add(tensor_names(int(l))[2], "zero", (slice(None), torch.tensor(ns, device=device)))
    return ops


def edit_tensor(t, ops, rl=None):
    for kind, ix in ops:
        if kind == "copy":
            assert rl is not None and rl.shape == t.shape and rl.dtype == t.dtype, "a copy needs RL's tensor in the same shape and dtype"
            t[ix] = rl[ix]
        else:
            t[ix] = 0


def bits(t):
    return t.contiguous().view(INT[t.element_size()])


def bits_equal(a, b):
    return a.shape == b.shape and a.dtype == b.dtype and bool((bits(a) == bits(b)).all())


# ------------------------------------------------------------------------------------------------ in memory (Part T)
def apply_edit(model, rl_model, edit, ops=None):
    """ops: plan(edit, shapes_of(model.state_dict()), device), computed once by a caller that applies the edit many times."""
    sd = model.state_dict()                                       # detached tensors that share the parameters' storage
    if ops is None:
        ops = plan(edit, shapes_of(sd), next(iter(sd.values())).device)
    rl = rl_model.state_dict() if copies(edit) else {}
    saved = []
    with torch.no_grad():
        for k, o in ops.items():
            saved.append((sd[k], [(ix, sd[k][ix].clone()) for _, ix in o]))      # every part saved before the tensor changes
            edit_tensor(sd[k], o, rl.get(k))

    def undo():
        with torch.no_grad():
            for t, parts in reversed(saved):                          # reversed: two names of one tied tensor restore in order
                for ix, v in parts:
                    t[ix] = v
    return undo


# ------------------------------------------------------------------------------------------------ attribution (Part T2)
def mlp_grad(model, on):
    """on: exactly the MLP matrices require grad. Off: no parameter does. Both drop every stored gradient."""
    mlp = set(families(k for k, _ in model.named_parameters())["mlp"])
    for k, p in model.named_parameters():
        p.requires_grad_(on and k in mlp)
        p.grad = None


def attr_step(model, rl_sd):
    """After loss.backward() under mlp_grad(model, True): float32 [layers, width], per neuron -(RL - base) . dloss/dtheta summed over
    its gate row, up row and down column: the first-order drop of the loss when the neuron is copied from RL. The gradients keep
    the model's dtype; the difference and the product are taken in float32. Drops the gradients."""
    p = dict(model.named_parameters())
    L, _ = dims(shapes_of(p))
    dot = lambda k, dim: ((rl_sd[k].float() - p[k].detach().float()) * p[k].grad.float()).sum(dim)
    out = torch.stack([-(dot(g, 1) + dot(u, 1) + dot(d, 0)) for g, u, d in map(tensor_names, range(L))])
    for l in range(L):
        for k in tensor_names(l):
            p[k].grad = None
    return out


# ------------------------------------------------------------------------------------------------ constant shifts (Part T3)
def shift_hooks(model, shifts):
    """shifts: [(where, d, gen)]; where is "mlp" or "layer", d float32 [layers, hidden], gen a torch.Generator or None. Adds d[l] to
    the output of layer l's MLP module (before any norm that follows it) or of the layer itself (the residual stream), at every
    position. The sum is taken in float32 and rounded to bf16. A bf16 value has 8 significant bits, so with round-to-nearest
    (gen None) a shift below half the spacing of an output entry is lost at that entry, at every position. With a generator the
    rounding is stochastic (up with probability equal to the remainder), so the mean of the output moves by exactly d; a zero d
    changes no bit under both. Returns remove()."""
    def hook(d, gen):
        def f(mod, args, out):
            assert out.dtype == torch.bfloat16, f"shift_hooks rounds to bf16; the output is {out.dtype}"
            y = out.float() + d
            if gen is None:
                return y.to(out.dtype)
            r = torch.randint(0, 65536, y.shape, generator=gen, device=y.device, dtype=torch.int32)
            return ((y.view(torch.int32) + r) & -65536).view(torch.float32).to(out.dtype)    # the 16 bits that bf16 drops, set to 0
        return f
    hs = [(layer.mlp if where == "mlp" else layer).register_forward_hook(hook(d[l], gen))
          for where, d, gen in shifts for l, layer in enumerate(model.model.layers)]
    assert all(where in ("mlp", "layer") for where, _, _ in shifts)
    return lambda: [h.remove() for h in hs]


# ------------------------------------------------------------------------------------------------ as a checkpoint (Part G)
def index(d):
    """{tensor name: (shard path, shape)} over the *.safetensors files of a checkpoint directory (headers only)."""
    files, out = sorted(pathlib.Path(d).glob("*.safetensors")), {}
    assert files, f"no safetensors file in {d}"
    for f in files:
        with safe_open(f, "pt") as h:
            for k in h.keys():
                assert k not in out, ("tensor in two shards", k)
                out[k] = (f, tuple(h.get_slice(k).get_shape()))
    return out


def read(idx, k):
    with safe_open(idx[k][0], "pt") as h:
        return h.get_tensor(k)


def build_checkpoint(base_dir, rl_dir, edit, out_dir):
    base_dir, out = pathlib.Path(base_dir), pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    assert not any(out.iterdir()), f"{out} is not empty"
    where = index(base_dir)
    ops = plan(edit, {k: s for k, (_, s) in where.items()})
    assert rl_dir is not None or not copies(edit), "the edit copies from RL: rl_dir is needed"
    rl = index(rl_dir) if copies(edit) else {}
    rewritten, dtypes = sorted({where[k][0].name for k in ops}), set()
    for f in sorted(base_dir.iterdir()):
        if f.name not in rewritten:
            os.symlink(f.resolve(), out / f.name)
            continue
        with safe_open(f, "pt") as h:
            meta = h.metadata()
        tensors = load_file(f)
        for k in tensors:
            if k in ops:
                edit_tensor(tensors[k], ops[k], read(rl, k) if any(kind == "copy" for kind, _ in ops[k]) else None)
                dtypes.add(str(tensors[k].dtype))
        save_file(tensors, out / f.name, metadata=meta)
    L, W = dims({k: s for k, (_, s) in where.items()})
    return {"dir": str(out), "shards_rewritten": rewritten, "files_linked": sorted(f.name for f in out.iterdir() if f.is_symlink()),
            "tensors_named": len(ops), "dtypes_of_edited_tensors": sorted(dtypes), "copy_families": edit.get("copy_families", []),
            "neurons_copied": int(neuron_mask(edit, L, W).sum()), "neurons_zeroed": sum(len(v) for v in edit.get("zero", {}).values())}


def diff_checkpoint(built_dir, base_dir, rl_dir, edit):
    b, o = index(base_dir), index(built_dir)
    assert {k: s for k, (_, s) in b.items()} == {k: s for k, (_, s) in o.items()}, "the built checkpoint holds other tensors or shapes"
    ops = plan(edit, {k: s for k, (_, s) in b.items()})
    rl = index(rl_dir) if copies(edit) else {}
    rep = {"tensors": len(b), "tensors_in_linked_shards": 0, "tensors_loaded": 0, "entries_named": 0, "entries_differ": 0,
           "tensors_differ": [], "tensors_named_but_equal_to_base": []}
    for k in sorted(b):
        if o[k][0].resolve() == b[k][0].resolve():                # a link to the base's shard: the same file
            assert k not in ops, f"{k}: named by the edit, but its shard is the base's file"
            rep["tensors_in_linked_shards"] += 1
            continue
        x, y = read(o, k), read(b, k)
        assert x.dtype == y.dtype, (k, x.dtype, y.dtype)
        diff = bits(x) != bits(y)
        mask, zero = torch.zeros(x.shape, dtype=torch.bool), torch.zeros(x.shape, dtype=torch.bool)
        for kind, ix in ops.get(k, ()):
            mask[ix] = True
            if kind == "zero":
                zero[ix] = True
        assert not (diff & ~mask).any(), f"{k}: {int((diff & ~mask).sum())} entries outside the edit differ from the base"
        assert not bits(x)[zero].any(), f"{k}: a zeroed entry is not +0"
        if (mask & ~zero).any():
            r = read(rl, k)
            assert r.dtype == x.dtype and bool((bits(x)[mask & ~zero] == bits(r)[mask & ~zero]).all()), f"{k}: a copied entry differs from RL"
        rep["tensors_loaded"] += 1
        rep["entries_named"] += int(mask.sum())
        rep["entries_differ"] += int(diff.sum())
        if diff.any():
            rep["tensors_differ"].append(k)
        elif k in ops:
            rep["tensors_named_but_equal_to_base"].append(k)
    assert set(rep["tensors_differ"]) | set(rep["tensors_named_but_equal_to_base"]) == set(ops), "a named tensor was not checked"
    return rep


# ------------------------------------------------------------------------------------------------ stand-ins and selfcheck (no download)
def tiny_pair(seed=0):
    """Stand-ins for --dry-run and selfcheck: a random 4-layer Llama (hidden 16, width 64, vocabulary 128, bf16) as the base; 'RL' is
    the base plus 5 % noise on every tensor and a large change of four neurons, so that a ranking has something to find. Every
    embedding holds one common vector, and five neurons read it with their gate and up rows: neurons that are on at every position."""
    from transformers import LlamaConfig, LlamaForCausalLM
    cfg = LlamaConfig(vocab_size=128, hidden_size=16, intermediate_size=64, num_hidden_layers=4, num_attention_heads=2,
                      num_key_value_heads=2, initializer_range=0.3, tie_word_embeddings=False, bos_token_id=0, eos_token_id=1)
    torch.manual_seed(seed)
    base = LlamaForCausalLM(cfg).eval()
    c, sb = torch.randn(16), base.state_dict()
    sb["model.embed_tokens.weight"] += 0.6 * c
    for l, n in ((0, 5), (1, 6), (1, 30), (2, 9), (3, 8)):
        sb[tensor_names(l)[0]][n], sb[tensor_names(l)[1]][n] = 2 * c / c.norm(), 2 * c / c.norm()
    base = base.to(torch.bfloat16)
    rl = LlamaForCausalLM(cfg).to(torch.bfloat16).eval()
    rl.load_state_dict(base.state_dict())
    g, sd = torch.Generator().manual_seed(seed + 1), rl.state_dict()
    for k, t in sd.items():
        t.copy_((t.float() + 0.05 * t.float().std() * torch.randn(t.shape, generator=g)).to(t.dtype))
    for l, n in ((0, 3), (1, 10), (2, 20), (3, 40)):
        gate, up, down = (sd[k] for k in tensor_names(l))
        for t in (gate[n], up[n], down[:, n]):
            t.copy_((t.float() + torch.randn(t.shape, generator=g)).to(t.dtype))
    return base, rl


def saved_pair(tmp):
    """tiny_pair() written to tmp/base and tmp/rl in several shards (other boundaries for RL) and loaded back, so that the models in
    memory come from the loader that also loads a built checkpoint. Returns base, rl."""
    out = []
    for name, m, size in zip(("base", "rl"), tiny_pair(), ("8KB", "12KB")):
        m.save_pretrained(tmp / name, max_shard_size=size)
        out.append(type(m).from_pretrained(tmp / name, dtype=torch.bfloat16).eval())
    return out


def roundtrip(base, rl, base_dir, rl_dir, edit, out_dir, x):
    """One edit through both applications: the built checkpoint passes diff_checkpoint; loaded, it has the bits and the logits of the
    base edited in memory; undo restores every tensor of the base bit for bit. Returns build_checkpoint's record with the diff."""
    rep = build_checkpoint(base_dir, rl_dir, edit, out_dir)
    rep["diff"] = diff_checkpoint(out_dir, base_dir, rl_dir, edit)
    built = type(base).from_pretrained(out_dir, dtype=torch.bfloat16).eval()
    ref = {k: v.clone() for k, v in base.state_dict().items()}
    undo = apply_edit(base, rl, edit)
    with torch.no_grad():
        same_logits = torch.equal(base(input_ids=x).logits, built(input_ids=x).logits)
    same_bits = all(bits_equal(v, built.state_dict()[k]) for k, v in base.state_dict().items())
    undo()
    assert same_logits and same_bits, (edit["name"], "built checkpoint against the in-memory edit", same_logits, same_bits)
    assert all(bits_equal(v, ref[k]) for k, v in base.state_dict().items()), (edit["name"], "undo")
    return rep


def selfcheck():
    import tempfile
    tmp_dir = tempfile.TemporaryDirectory()
    tmp = pathlib.Path(tmp_dir.name)
    base, rl = saved_pair(tmp)
    x = torch.randint(0, 128, (1, 50), generator=torch.Generator().manual_seed(2))
    sb, sr = base.state_dict(), rl.state_dict()
    L, W = dims(shapes_of(sb))
    s = rank(sb, sr)
    assert s.shape == (L, W) and s.dtype == torch.float32
    assert {(int(i) // W, int(i) % W) for i in s.flatten().topk(4).indices} == {(0, 3), (1, 10), (2, 20), (3, 40)}, "ranking: planted neurons"
    ch = weight_change(sb, sr)
    assert abs(float(s.double().sum()) - ch["mlp"]) <= 1e-4 * ch["mlp"] and all(v > 0 for v in ch.values()), ch
    for bad in ({"zero": {"0": [1]}}, {"name": "x", "scale": {}}, {"name": "x", "zero": {"4": [1]}}, {"name": "x", "zero": {"0": [W]}},
                {"name": "x", "copy_neurons": {"0": [1, 1]}}, {"name": "x", "copy_families": ["norm"]}, {"name": "x", "zero": {"00": [1]}}):
        try:
            check_edit(bad, L, W)
        except AssertionError:
            continue
        raise AssertionError(f"check_edit accepted {bad}")
    # attr_step against a measured drop: a set of neurons moved a small step toward RL lowers the loss by step x the set's score
    b64, r64 = copy.deepcopy(base).double(), copy.deepcopy(rl).double()
    s64 = r64.state_dict()
    with torch.no_grad():
        lp_r = torch.log_softmax(r64(input_ids=x).logits[0], -1)
    loss = lambda: (lp_r.exp() * (lp_r - torch.log_softmax(b64(input_ids=x).logits[0], -1))).sum(-1).mean()
    mlp_grad(b64, True)
    assert sorted(k for k, p in b64.named_parameters() if p.requires_grad) == sorted(k for l in range(L) for k in tensor_names(l))
    l0 = loss()
    l0.backward()
    score = attr_step(b64, s64)
    mlp_grad(b64, False)
    assert score.shape == (L, W) and score.dtype == torch.float32 and not any(p.requires_grad or p.grad is not None for p in b64.parameters())
    step, pred, drop = 1e-4, {}, {}
    for name, neurons in (("a", [(0, 3), (2, 7)]), ("b", [(1, 10), (3, 40), (3, 41)])):
        sd64 = b64.state_dict()
        saved = {k: v.clone() for k, v in sd64.items()}
        with torch.no_grad():
            for l, n in neurons:
                g, u, d = tensor_names(l)
                for t, r in ((sd64[g][n], s64[g][n]), (sd64[u][n], s64[u][n]), (sd64[d][:, n], s64[d][:, n])):
                    t += step * (r - t)
            drop[name] = (float(l0) - float(loss())) / step
        b64.load_state_dict(saved)
        pred[name] = sum(float(score[l, n]) for l, n in neurons)
    print("attr_step: predicted", pred, "measured", drop, flush=True)
    assert all(abs(drop[k] - pred[k]) <= 0.02 * abs(pred[k]) for k in pred), "attr_step differs from the measured drop"
    assert abs(drop["a"] - pred["b"]) > 0.02 * abs(pred["b"]), "the attribution check cannot tell two neuron sets apart"
    # shift_hooks, read at layer 0's MLP output (its input is the same with and without the hooks)
    seen, xs = [], torch.randint(0, 128, (1, 3000), generator=torch.Generator().manual_seed(3))
    grab = base.model.layers[0].mlp.register_forward_hook(lambda mod, args, out: seen.append(out.float()))
    with torch.no_grad():
        base(input_ids=xs)
        d = torch.zeros(L, 16)
        d[0] = 1e-3 * seen[0].abs().mean() * torch.randn(16, generator=torch.Generator().manual_seed(4))
        for shifts in ([("mlp", torch.zeros(L, 16), torch.Generator().manual_seed(5)), ("layer", torch.zeros(L, 16), None)],
                       [("mlp", d, torch.Generator().manual_seed(5))], [("mlp", d, None)]):
            grab.remove()
            remove = shift_hooks(base, shifts)
            grab = base.model.layers[0].mlp.register_forward_hook(lambda mod, args, out: seen.append(out.float()))    # after the shift
            seen.append(base(input_ids=xs).logits)
            remove()
        grab.remove()
        seen.append(base(input_ids=xs).logits)
    clean, zero, zero_logits, stoch, _, nearest, _, clean_logits = seen
    arrived = lambda y: float(((y - clean).mean((0, 1)) * d[0]).sum() / d[0].square().sum())       # share of d in the mean output
    print("shift_hooks: share of a small shift that arrives: stochastic", round(arrived(stoch), 3), "nearest", round(arrived(nearest), 3), flush=True)
    assert torch.equal(zero, clean) and torch.equal(zero_logits, clean_logits), "a zero shift changed the output, or a hook stayed"
    assert abs(arrived(stoch) - 1) < 0.1 and arrived(nearest) < 0.9, "shift_hooks: stochastic rounding must deliver the shift, nearest must lose part"
    edits = [{"name": "none"}, {"name": "zero", "zero": {"1": [10, 5]}}, {"name": "copy", "copy_neurons": {"0": [3], "3": [40, 0]}},
             {"name": "layer", "copy_neurons": {"2": list(range(W))}}, {"name": "attn_zero", "copy_families": ["attn"], "zero": {"2": [20]}},
             {"name": "copy_then_zero", "copy_neurons": {"1": [10, 11]}, "zero": {"1": [10]}},
             {"name": "mlp_zero", "copy_families": ["mlp"], "zero": {"0": [3]}}, {"name": "all", "copy_families": list(FAMILIES)}]
    with tmp_dir:
        n_shards = len(list((tmp / "base").glob("*.safetensors")))
        assert n_shards >= 4, n_shards
        for e in edits:
            rep = roundtrip(base, rl, tmp / "base", tmp / "rl" if copies(e) else None, e, tmp / e["name"], x)
            print(e["name"], "rewritten", len(rep["shards_rewritten"]), "of", n_shards, "shards; entries named", rep["diff"]["entries_named"],
                  "differ", rep["diff"]["entries_differ"], flush=True)
            if e["name"] == "none":
                assert not rep["shards_rewritten"] and rep["diff"]["tensors_in_linked_shards"] == len(sb)
            if e["name"] == "zero":
                assert len(rep["shards_rewritten"]) == 1 and rep["diff"]["tensors_differ"] == [tensor_names(1)[2]]
                assert rep["diff"]["entries_named"] == rep["diff"]["entries_differ"] == 2 * 16
            if e["name"] == "all":
                built = index(tmp / "all")
                assert all(bits_equal(read(built, k), sr[k]) for k in built) and len(rep["shards_rewritten"]) == n_shards
        # planted faults: one entry outside the edit changed; one zeroed entry left at the base's value
        down = tensor_names(1)[2]
        for fault in ("outside", "inside"):
            shard = index(tmp / "zero")[down][0]
            t = load_file(shard)
            other = next(k for k in t if k != down) if fault == "outside" and len(t) > 1 else down
            if fault == "outside":
                t[other].view(-1)[0 if other != down else 1] += 1          # entry [0, 1] of down_proj is in column 1: not named
            else:
                t[down][:, 10] = sb[down][:, 10]
            save_file(t, shard, metadata={"format": "pt"})
            try:
                diff_checkpoint(tmp / "zero", tmp / "base", None, edits[1])
            except AssertionError as err:
                print(f"planted fault ({fault}) rejected: {err}", flush=True)
                build_checkpoint(tmp / "base", None, edits[1], tmp / f"zero_{fault}")     # a clean copy for the next fault
                os.replace(tmp / f"zero_{fault}" / shard.name, shard)
                continue
            raise AssertionError(f"diff_checkpoint accepted the planted fault ({fault})")
        diff_checkpoint(tmp / "zero", tmp / "base", None, edits[1])
    print("neurons.selfcheck: ok")


if __name__ == "__main__":
    selfcheck()
