"""Inside check of SPEC 3 (specs/SPEC3_steer.md): with a steering vector of jobs/steer_gen.py switched on, how often does the base
model's layer-24 J-lens readout hold the hold-on words, on its own stored answers (T1) with teacher forcing? SPEC 1 measured
4.63 % for the base and 6.29 % for the RL model on this text (results/lensdiff/matched-01, lens fitted per model). Inference
only, the base model in bf16 on one H100:

    uv run tools/gpu.py submit h100 --hours 0.5 -- "python -m studies.jspace.jobs.steer_readout --commit $(git rev-parse HEAD)
        --arms none,steer:hold:L24:0.068,steer:hold:L24:0.5 --block-norms 24:39.544,20:28.583 --read-lens /runs/<fit job>/base_wikitext_jlens.pt"
    smoke: add  --every 100

The steering vectors are those of steer_gen.py: the published base lens (lib/jlens_read.py), lib/steer.py directions, alpha times
the block norm given in --block-norms (copy `block_norm_median` of the generation run's checks.json, so the vectors are equal).
The readout uses another lens than the one the vectors come from: the lens fitted on the base model by jobs/fit_lens.py
(--read-lens), through the model's own final norm and head, as in lensdiff matched-01. Presence: a hold-on token (or a wrap-up
token) is among the top --k word-like tokens of the readout; positions are the inputs that predict a generated token.

Answers: the stored T1 answers whose problem index is a multiple of --every and whose sequence is at most --max-len tokens.
Per arm and answer (rows.json) and summed with 95 % bootstrap intervals over answers (readout.json): presence of the two
families in the layer --read-layer readout; in the model's output, the share of positions whose top token is a hold-on token,
the mean log-probability of the family, KL(unsteered || steered) per position and the log-probability of the written token.
A large alpha is the input that must change the readout (list one in --arms). Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
import types

import numpy as np
import torch

from studies.jspace.analysis.lensdiff_analyze import HOLD, WRAP
from studies.jspace.jobs import lensdiff as LD
from studies.jspace.lib import jlens_read as JL
from studies.jspace.lib import steer as ST
from studies.rlneurons.jobs import rln5_map as M

RNG = np.random.default_rng(0)
B = 2000


def ratio_ci(num, den):
    num, den = np.asarray(num, dtype=np.float64), np.asarray(den, dtype=np.float64)
    i = RNG.integers(0, len(num), size=(B, len(num)))
    s = num[i].sum(1) / den[i].sum(1)
    return {"value": float(num.sum() / den.sum()), "ci95": [float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", required=True, help="none first, then steer arms in the notation of steer_gen.py")
    ap.add_argument("--block-norms", required=True, help="<layer>:<median norm>,... from the generation run's checks.json")
    ap.add_argument("--read-lens", required=True)
    ap.add_argument("--read-layer", type=int, default=24)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--every", type=int, default=8)
    ap.add_argument("--max-len", type=int, default=6000)
    ap.add_argument("--inputs", default="/runs/inputs/rln5")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    arms = [ST.parse_arm(x) for x in a.arms.split(",")]
    assert arms[0]["kind"] == "none" and all(x["kind"] == "steer" for x in arms[1:]), "--arms: none first, then steer arms"
    rnorm = {int(k): float(v) for k, v in (x.split(":") for x in a.block_norms.split(","))}
    steer_layers = sorted({x["layer"] for x in arms[1:]})
    assert set(steer_layers) <= set(rnorm) and max(steer_layers) <= a.read_layer, "a steered layer has no norm, or lies after the read layer"

    fz = json.loads((M.D4 / "frozen4.json").read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    sel, _ = LD.sequences(types.SimpleNamespace(cells="T1", inputs=a.inputs, n=None, pick=[]), tok, fz)
    seqs = [s for s in sel["T1"] if s["idx"] % a.every == 0 and len(s["ids"]) <= a.max_len]
    dev = "cuda"
    model, info = M.load(fz, "base", dev)
    W = model.lm_head.weight.detach().float().cpu()
    fam = {n: ST.family_ids(tok, n) for n in ST.FAMILIES}
    Jpub, pub_meta = JL.load_lens(steer_layers, "cpu")
    dirs = {l: ST.directions(W, Jpub[l], fam) for l in steer_layers}
    Jread, read_meta = JL.load_lens_file(a.read_lens, [a.read_layer], dev)
    mask = JL.wordlike_mask(tok, info["vocab_size"]).to(dev)
    tid = lambda s: tok.encode(s, add_special_tokens=False)
    assert all(len(tid(s)) == 1 for s in HOLD + WRAP)
    hold, wrap = torch.tensor([tid(s)[0] for s in HOLD], device=dev), torch.tensor([tid(s)[0] for s in WRAP], device=dev)
    assert sorted(hold.tolist()) == sorted(fam["hold"])

    dtype = model.lm_head.weight.dtype
    vec = {x["arm"]: (x["layer"], (x["alpha"] * rnorm[x["layer"]] * dirs[x["layer"]][x["dir"]]).to(dev, dtype)) for x in arms[1:]}
    cur = {"arm": "none"}

    def steer_hook(l):
        def f(_module, _inputs, o):
            if cur["arm"] == "none" or vec[cur["arm"]][0] != l:
                return None
            h = (o[0] if isinstance(o, tuple) else o) + vec[cur["arm"]][1]
            return (h,) + tuple(o[1:]) if isinstance(o, tuple) else h
        return f

    handles = [model.model.layers[l].register_forward_hook(steer_hook(l)) for l in steer_layers]
    rec = JL.Recorder(model, [a.read_layer])                   # registered after the steering hooks: it sees the steered output
    keys = ("positions", "hold_present", "wrap_present", "out_top1_hold", "out_lp_hold", "kl_from_none", "lp_written")
    rows = []
    with torch.inference_mode():
        for s in seqs:
            x = torch.tensor(s["ids"], device=dev)[None]
            lo = s["n_prompt"] + s["n_cue"] - 1                 # the input position that predicts the first generated token
            hi = lo + s["n_gen"]
            y, ref, row = x[0, lo + 1:hi + 1], None, {"problem_index": s["idx"], "arms": {}}
            for arm in arms:
                cur["arm"] = arm["arm"]
                lp = torch.log_softmax(model(input_ids=x, use_cache=False).logits[0, lo:hi].float(), -1)
                top = JL.readout(model, rec.acts[a.read_layer][0, lo:hi], Jread[a.read_layer]).masked_fill(~mask, float("-inf")).topk(a.k, -1).indices
                ref = lp if ref is None else ref
                row["arms"][arm["arm"]] = dict(zip(keys, (
                    hi - lo, int(torch.isin(top, hold).any(1).sum()), int(torch.isin(top, wrap).any(1).sum()),
                    int(torch.isin(lp.argmax(-1), hold).sum()), float(torch.logsumexp(lp[:, hold], -1).sum()),
                    float((ref.exp() * (ref - lp)).sum()), float(lp.gather(1, y[:, None]).sum()))))
            rows.append(row)
            print(s["idx"], hi - lo, {k: v["hold_present"] for k, v in row["arms"].items()}, flush=True)
    cur["arm"] = "none"
    rec.close()
    for h in handles:
        h.remove()

    res = {"commit": a.commit, "job_id": os.environ.get("JOB_ID"), "config": {**vars(a), "out": str(out)}, "model": info, "gpu": torch.cuda.get_device_name(0),
           "steer_lens": pub_meta, "read_lens": read_meta, "block_norms": rnorm, "answers": len(rows), "problem_indices": [r["problem_index"] for r in rows],
           "families": {"hold_on": list(HOLD), "wrap_up": list(WRAP)},
           "applied_vector_norm": {k: float(v[1].float().norm()) for k, v in vec.items()}, "wall_s": None, "arms": {}}
    for arm in arms:
        n = [r["arms"][arm["arm"]]["positions"] for r in rows]
        col = lambda k: [r["arms"][arm["arm"]][k] for r in rows]
        res["arms"][arm["arm"]] = {**arm, "positions": int(sum(n)), "readout_hold_presence": ratio_ci(col("hold_present"), n),
                                   "readout_wrap_presence": ratio_ci(col("wrap_present"), n), "output_top1_is_hold": ratio_ci(col("out_top1_hold"), n),
                                   "output_mean_logprob_hold": ratio_ci(col("out_lp_hold"), n), "kl_from_none_nats_per_position": ratio_ci(col("kl_from_none"), n),
                                   "logprob_of_written_token": ratio_ci(col("lp_written"), n)}
        print(arm["arm"], json.dumps(res["arms"][arm["arm"]]["readout_hold_presence"]), flush=True)
    res["wall_s"] = time.time() - t0
    M.dump(out / "rows.json", rows)
    M.dump(out / "readout.json", res)


if __name__ == "__main__":
    main()
