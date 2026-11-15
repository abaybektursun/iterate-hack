"""The stack of specs/SPEC_thinkvote.md, Part B: Think-SFT + scale * (RL-Math - base), written as a BF16 safetensors directory
that `run_cell.py --model-path` loads. Per tensor, in float32: x = sft + scale * (rl - base). A tensor where rl equals base
(torch.equal) is the stored Think-SFT tensor, never rounded. Rounding of x to BF16: merge_weights.to_bf16, stochastic by
default (generator seeded --seed + 1), the rule of the weight-difference study: most RL changes are within one BF16 unit in
the last place, which nearest rounding would drop in part.

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.thinkvote_stack --dir /tmp/theta
    python -m studies.rlneurons.jobs.thinkvote_stack --selftest

Weights check, written to --stats (default $OUT_DIR/stack.json) and asserted: over the edited tensors, effective_scale =
<written - sft, scale * (rl - base)> / ||scale * (rl - base)||^2 within 0.02 of 1, and every written entry within one BF16
unit in the last place of its float32 target. Every run does the selftest first (synthetic models, wsp_edit.toy), which must
also FAIL the check for a model that leaves the RL difference out. Fail loud: no try/except.
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
from safetensors.torch import save_file

from studies.rlneurons.jobs.merge_weights import to_bf16, ulp
from studies.rlneurons.jobs.wsp_delta_anatomy import MODELS
from studies.rlneurons.jobs.wsp_edit import read, toy, weight_map

TOL = 0.02


def stack(base_dir, rl_dir, sft_dir, json_dir, out_dir, scale=1.0, rounding="stochastic", seed=0, device="cpu"):
    base_dir, rl_dir, sft_dir, json_dir, out_dir = (pathlib.Path(d) for d in (base_dir, rl_dir, sft_dir, json_dir, out_dir))
    wb, wr, ws = weight_map(base_dir), weight_map(rl_dir), weight_map(sft_dir)
    assert set(wb) == set(wr) == set(ws), "the three models hold different tensor names"
    assert wb == weight_map(json_dir), "the index of json_dir is copied to the output, whose shards are the base's: the two differ"
    gen = torch.Generator(device).manual_seed(seed + 1)
    dot = add_sq = written_sq = 0.0
    kept, edited, worst = 0, 0, 0.0
    out_dir.mkdir(parents=True)
    for shard in sorted(set(wb.values())):
        written = {}
        for name in sorted(n for n, s in wb.items() if s == shard):
            b, r, s = read(base_dir, wb, name), read(rl_dir, wr, name), read(sft_dir, ws, name)
            assert b.dtype == r.dtype == s.dtype == torch.bfloat16 and b.shape == r.shape == s.shape, name
            if torch.equal(b, r):
                written[name] = s
                kept += 1
                continue
            sf = s.to(device, torch.float32)
            add = scale * (r.to(device, torch.float32) - b.to(device, torch.float32))
            x = sf + add
            m = to_bf16(x, rounding, gen)
            w = m.to(torch.float32) - sf
            worst = max(worst, float(((m.to(torch.float32) - x).abs() / ulp(x)).max()))
            dot += torch.sum(w * add, dtype=torch.float64).item()
            add_sq += torch.sum(add * add, dtype=torch.float64).item()
            written_sq += torch.sum(w * w, dtype=torch.float64).item()
            written[name] = m.cpu()
            edited += 1
        save_file(written, out_dir / shard, metadata={"format": "pt"})
    for p in json_dir.glob("*.json"):
        shutil.copy(p, out_dir / p.name)
    return {"scale": scale, "rounding": rounding, "seed": seed, "n_tensors": len(wb), "n_edited": edited, "n_stored_think_sft": kept,
            "add_norm": add_sq ** 0.5, "written_norm": written_sq ** 0.5, "effective_scale": dot / add_sq if add_sq else None,
            "cos_written_add": dot / (add_sq * written_sq) ** 0.5 if add_sq and written_sq else None, "max_error_in_bf16_units": worst}


def failures(st):
    return ([f"effective scale {st['effective_scale']:.4f} is not within {TOL} of 1"] if abs(st["effective_scale"] - 1) >= TOL else []) + \
           ([f"a written entry is {st['max_error_in_bf16_units']:.3f} BF16 units from its target"] if st["max_error_in_bf16_units"] > 1.0001 else [])


def check(st):
    assert not failures(st), failures(st)


def selftest(device):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / "a").mkdir()
        (tmp / "b").mkdir()
        bd, rd = toy(tmp / "a", torch.Generator().manual_seed(0))
        _, sd = toy(tmp / "b", torch.Generator().manual_seed(1))             # another model with the same tensor names, as Think-SFT
        st = stack(bd, rd, sd, bd, tmp / "ok", device=device)
        check(st)
        assert st["n_stored_think_sft"] >= 1, "the toy's tensor that RL leaves unchanged was not copied"
        bad = stack(bd, bd, sd, bd, tmp / "none", device=device)              # no RL difference: nothing may be edited
        assert bad["n_edited"] == 0, "a model without an RL difference was edited"
        half = stack(bd, rd, sd, bd, tmp / "half", scale=0.5, device=device)  # planted failure: measured against the full difference
        half["effective_scale"] *= 0.5
        assert failures(half), "the check passed a model that holds half the RL difference"
    print(f"selftest passed on {device}: effective scale {st['effective_scale']:.4f}, {st['n_edited']} edited, {st['n_stored_think_sft']} stored", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--rounding", default="stochastic", choices=("stochastic", "nearest"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--stats", default=os.path.join(os.environ.get("OUT_DIR", ""), "stack.json"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    torch.set_grad_enabled(False)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    selftest(device)
    if a.selftest:
        return
    assert a.dir, "a run needs --dir"
    from huggingface_hub import snapshot_download
    keys = ("base", "rl_math", "think_sft")
    base, rl, sft = (snapshot_download(MODELS[k][0], revision=MODELS[k][1], allow_patterns=["*.json", "*.safetensors"]) for k in keys)
    st = stack(base, rl, sft, rl, a.dir, a.scale, a.rounding, a.seed, device)
    st = {"args": vars(a), "models": {k: {"repo": MODELS[k][0], "revision": MODELS[k][1]} for k in keys}, "device": device, "seconds": time.time() - t0, **st}
    pathlib.Path(a.stats).write_text(json.dumps(st, indent=1) + "\n")
    print("thinkvote_stack " + json.dumps({k: v for k, v in st.items() if k not in ("args", "models")}), flush=True)
    check(st)


if __name__ == "__main__":
    main()
