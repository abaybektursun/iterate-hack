"""Entropy-gated temperature: a vLLM logits processor (Model Runner V2 interface, vLLM 0.32.0) that divides the logits of one
position by t_low only when the entropy H of the next-token distribution (nats, at temperature 1, before any truncation) is on
the chosen side of a threshold. The request itself runs at temperature 1.0 / top-p 1.0, so every other position is sampled
unchanged. specs/SPEC_egate.md.

A request opts in with SamplingParams(extra_args={"egate": [mode, t_low, thr, arm]}):
  mode  OFF  no change (the processor only counts the request's entropies)
        HI   sharpen where H > thr
        LO   sharpen where H <= thr
        RND  sharpen at random positions with probability thr (control: the same share of positions as HI, chosen blind)
  arm   an index below N_ARMS; the processor keeps one row of counts per arm (positions, sharpened positions, sum of H, and a
        histogram of H with bin width BIN nats up to H_MAX), read with EntropyGate.live.stats().

Constant low temperature is HI with thr = -1 (every position has H > -1).
The engine must run in-process (VLLM_ENABLE_V1_MULTIPROCESSING=0) for `live` to be the engine's instance.
"""
from __future__ import annotations

import torch
from vllm.v1.worker.gpu.sample.logits_processor import LogitsProcessor

OFF, HI, LO, RND = 0, 1, 2, 3
MODES = {"off": OFF, "hi": HI, "lo": LO, "rnd": RND}
N_ARMS, BIN, H_MAX = 32, 0.05, 12.0
N_BINS = int(H_MAX / BIN)
NAME = "studies.rlneurons.lib.egate:EntropyGate"


def gate(logits, mode, t_low, thr, rand):
    """logits [rows, vocab] float32; mode, t_low, thr, rand [rows]. Returns (the gated logits, H [rows], sharpened [rows] bool).
    Rows with mode < 0 (requests without the argument) are returned unchanged and have sharpened False."""
    h = torch.special.entr(torch.softmax(logits, dim=-1)).sum(-1)
    sharp = ((mode == HI) & (h > thr)) | ((mode == LO) & (h <= thr)) | ((mode == RND) & (rand < thr))
    scale = torch.where(sharp, 1.0 / t_low, torch.ones_like(t_low))
    return logits * scale[:, None], h, sharp


class EntropyGate(LogitsProcessor):
    live = None

    def __init__(self, vllm_config, req_states):
        n, dev = req_states.max_num_reqs, req_states.device
        self.host = torch.full((n, 4), -1.0)                       # per slot: mode, t_low, thr, arm; mode -1 = not ours
        self.dev = torch.full((n, 4), -1.0, device=dev)
        self.counts = torch.zeros(N_ARMS, 3, dtype=torch.float64, device=dev)       # positions, sharpened, sum of H
        self.hist = torch.zeros(N_ARMS * N_BINS, dtype=torch.float64, device=dev)
        self.rng = torch.Generator(device=dev).manual_seed(0)
        EntropyGate.live = self

    @classmethod
    def validate_params(cls, sampling_params):
        a = (sampling_params.extra_args or {}).get("egate")
        if a is None:
            return
        mode, t_low, thr, arm = a
        if mode not in (OFF, HI, LO, RND) or not 0.0 < t_low <= 1.0 or not 0 <= arm < N_ARMS or int(arm) != arm:
            raise ValueError(f"egate argument {a}: mode in 0-3, 0 < t_low <= 1, arm an integer below {N_ARMS}")

    def add_request(self, req_idx, sampling_params):
        a = (sampling_params.extra_args or {}).get("egate")
        self.host[req_idx] = torch.tensor([float(x) for x in a]) if a is not None else -1.0
        return a is not None

    def apply_staged_writes(self):
        self.dev.copy_(self.host, non_blocking=True)

    def apply(self, logits, ctx):
        p = self.dev[ctx.expanded_idx_mapping.long()]
        mode, t_low, thr, arm = p[:, 0], p[:, 1], p[:, 2], p[:, 3].long()
        ours = mode >= 0
        if not bool(ours.any()):
            return logits
        rand = torch.rand(logits.shape[0], device=logits.device, generator=self.rng)
        out, h, sharp = gate(logits, mode, t_low, thr, rand)
        arm, h, sharp = arm[ours], h[ours].double(), sharp[ours].double()
        self.counts.index_add_(0, arm, torch.stack([torch.ones_like(h), sharp, h], dim=1))
        self.hist.index_add_(0, arm * N_BINS + (h / BIN).long().clamp_(max=N_BINS - 1), torch.ones_like(h))
        return out

    def stats(self):
        """Per arm index: positions, sharpened positions, mean H, and the histogram of H (N_BINS bins of BIN nats)."""
        c, hist = self.counts.cpu(), self.hist.cpu().view(N_ARMS, N_BINS)
        return {i: {"positions": int(c[i, 0]), "sharpened": int(c[i, 1]), "mean_entropy": float(c[i, 2] / c[i, 0]),
                    "hist": [int(x) for x in hist[i]]} for i in range(N_ARMS) if c[i, 0] > 0}


def percentile(hist, q):
    """Upper edge (nats) of the first histogram bin at which the cumulative share of positions reaches q."""
    total, run = sum(hist), 0
    assert total > 0, "empty entropy histogram"
    for i, n in enumerate(hist):
        run += n
        if run >= q * total:
            return (i + 1) * BIN
