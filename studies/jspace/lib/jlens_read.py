"""J-lens readout for a Hugging Face Olmo 3 model (specs/SPEC1_lensdiff.md).

Reproduces anthropics/jacobian-lens at 581d398 (jlens/lens.py `transport`, jlens/hf.py `unembed`, jlens/hooks.py): the
activation of layer l is the output of block l; the readout logits are lm_head(final_norm(h.float() @ J_l.T)), with the
product cast to the head's dtype before the norm. No bias, no mean term, no beginning-of-sequence token.
"""
import hashlib
import os

import torch

LENS_REPO = "neuronpedia/jacobian-lens"
LENS_REV = "d2527c3cdbaa60dd4b65cbca1604921f044e989a"
LENS_FILE = "olmo-3-1025-7b/jlens/Salesforce-wikitext/Olmo-3-1025-7B_jacobian_lens.pt"
LENS_BYTES = 1040198095
QSCALE = 10.0                                         # stored log-probs: uint8 of round(-lp * QSCALE), capped at 255


def load_lens(layers, dev):
    """{layer: J in fp32 on dev} for the fitted base lens, and a record of the file."""
    from huggingface_hub import hf_hub_download
    p = hf_hub_download(LENS_REPO, LENS_FILE, revision=LENS_REV)
    assert os.path.getsize(p) == LENS_BYTES, ("lens file size", os.path.getsize(p))
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    d = torch.load(p, map_location="cpu", weights_only=True)
    J = {}
    for l in layers:
        j = d["J"][l]
        assert j.shape == (d["d_model"], d["d_model"]), (l, j.shape)
        J[l] = j.float().to(dev)
        assert torch.isfinite(J[l]).all(), ("non-finite J", l)
    meta = {"repo": LENS_REPO, "revision": LENS_REV, "file": LENS_FILE, "bytes": LENS_BYTES, "sha256": h.hexdigest(),
            "n_prompts": int(d["n_prompts"]), "d_model": int(d["d_model"]), "layers_in_file": sorted(int(k) for k in d["J"]),
            "dtype_in_file": str(d["J"][layers[0]].dtype)}
    return J, meta


def load_lens_file(path, layers, dev):
    """{layer: J in fp32 on dev} from a lens file in the jlens format ({"J": {layer: [d, d]}, "n_prompts": ...}), and a record
    of the file. `path` is a local file (jobs/fit_lens.py writes one) or hf://<owner>/<repo>@<revision>/<file in the repo>."""
    if str(path).startswith("hf://"):
        from huggingface_hub import hf_hub_download
        repo_rev, filename = str(path)[5:].split("/", 2)[0:2], str(path)[5:].split("/", 2)[2]
        repo, rev = "/".join(repo_rev).split("@")
        path = hf_hub_download(repo, filename, revision=rev)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    d = torch.load(path, map_location="cpu", weights_only=True)
    J = {l: d["J"][l].float().to(dev) for l in layers}
    assert all(torch.isfinite(j).all() for j in J.values())
    return J, {"file": str(path), "bytes": os.path.getsize(path), "sha256": h.hexdigest(), "n_prompts": int(d["n_prompts"]),
               "layers_in_file": sorted(int(k) for k in d["J"])}


class Recorder:
    """Keeps the output of the listed blocks of one model at each forward call (acts[layer] is [batch, positions, d])."""

    def __init__(self, model, layers):
        self.acts = {}
        self.handles = [model.model.layers[l].register_forward_hook(self._hook(l)) for l in layers]

    def _hook(self, l):
        def f(_module, _inputs, out):
            self.acts[l] = out[0] if isinstance(out, tuple) else out
        return f

    def close(self):
        for h in self.handles:
            h.remove()


def readout(head_model, h, J=None):
    """Lens logits in fp32 for activations h [n, d], through head_model's final norm and lm_head. J None is the logit lens."""
    r = h.float()
    if J is not None:
        r = r @ J.T
    return head_model.lm_head(head_model.model.norm(r.to(head_model.lm_head.weight.dtype))).float()


def wordlike_mask(tok, vocab):
    """True for token ids whose decoded string has a letter or a digit."""
    return torch.tensor([any(ch.isalnum() for ch in tok.decode([i])) for i in range(vocab)])


def quant(lp):
    return torch.clamp(torch.round(-lp * QSCALE), 0, 255).to(torch.uint8)


def future_hits(top, ids, first, lo, hi):
    """top [n, K]: token ids read at input positions first, first+1, ... of the sequence ids (1-D tensor). Returns
    (hits, hits_shifted, n_valid): the number of valid positions where a top token is among the written tokens lo..hi
    places ahead (the next token is 1 place ahead), the same count against the window of the position half the valid
    range away, and the number of valid positions (those with a complete window)."""
    n, width = top.shape[0], hi - lo + 1
    n_valid = min(n, len(ids) - first - hi)
    if n_valid <= 0:
        return 0, 0, 0
    p = first + torch.arange(n_valid, device=ids.device)
    win = ids[p[:, None] + torch.arange(lo, hi + 1, device=ids.device)[None, :]]
    assert win.shape == (n_valid, width)
    t = top[:n_valid]
    hit = (t[:, :, None] == win[:, None, :]).any(-1).any(-1)
    shifted = (t[:, :, None] == torch.roll(win, n_valid // 2, 0)[:, None, :]).any(-1).any(-1)
    return int(hit.sum()), int(shifted.sum()), int(n_valid)
