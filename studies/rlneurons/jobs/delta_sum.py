"""Delta transplant (specs/SPEC_transplant.md): write M = host + a * (donor - base), every tensor, as a BF16 safetensors directory that
`run_cell.py --model-path` loads. host, donor and base are keys of wsp_delta_anatomy.MODELS; all three are fine-tunes of the same base.

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.delta_sum --host think_sft --donor rl_math --alpha 1.0 --dir /tmp/theta
    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.delta_sum --host think_sft --donor rl_math --alpha 1.0 --random --dir /tmp/theta

  --alpha   a. A tensor whose donor - base is exactly zero is written as the host's stored tensor.
  --random  control: per tensor, a * (donor - base) is replaced by Gaussian noise of the same Frobenius norm (generator seeded --seed,
            tensors in sorted name order within sorted shards).
  --dir     the model goes here (must not exist): the base's shard layout, the json files (config, index, tokenizer) of the RL-Math
            model, as merge_weights and wsp_edit write them.

Rounding to BF16 is stochastic (merge_weights.to_bf16, generator seeded --seed + 1): the RL delta is a few BF16 units in the last place,
so rounding to nearest would drop part of it. Statistics go to --stats (default $OUT_DIR/delta_sum.json): summed over the edited tensors,
||host - base||, ||donor - base||, their cosine, and for the written model effective_a = <M - host, donor - base> / ||donor - base||^2
(for --random: ||M - host|| / ||a (donor - base)||). The run stops unless effective_a is within 2 % of a. Fail loud: no try/except.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import time

import torch
from safetensors.torch import save_file

from studies.rlneurons.jobs.merge_weights import to_bf16
from studies.rlneurons.jobs.wsp_delta_anatomy import MODELS
from studies.rlneurons.jobs.wsp_edit import read, weight_map

JSON_KEY = "rl_math"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True, choices=sorted(MODELS))
    ap.add_argument("--donor", required=True, choices=sorted(MODELS))
    ap.add_argument("--alpha", type=float, required=True)
    ap.add_argument("--random", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--stats", default=os.path.join(os.environ.get("OUT_DIR", ""), "delta_sum.json"))
    a = ap.parse_args()
    t0 = time.time()
    torch.set_grad_enabled(False)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    from huggingface_hub import snapshot_download
    dirs = {k: pathlib.Path(snapshot_download(MODELS[k][0], revision=MODELS[k][1], allow_patterns=["*.json", "*.safetensors"])) for k in ("base", a.host, a.donor)}
    json_dir = pathlib.Path(snapshot_download(MODELS[JSON_KEY][0], revision=MODELS[JSON_KEY][1], allow_patterns=["*.json"]))
    maps = {k: weight_map(d) for k, d in dirs.items()}
    assert set(maps["base"]) == set(maps[a.host]) == set(maps[a.donor]), "the three models hold different tensor names"
    assert maps["base"] == weight_map(json_dir), "the index copied to the output differs from the base's shard layout"
    gen, noise = torch.Generator(device).manual_seed(a.seed + 1), torch.Generator(device).manual_seed(a.seed)
    s = dict.fromkeys(("host_sq", "donor_sq", "host_donor", "written_donor", "written_sq"), 0.0)
    out, copied = pathlib.Path(a.dir), 0
    out.mkdir(parents=True)
    for shard in sorted(set(maps["base"].values())):
        written = {}
        for name in sorted(n for n, f in maps["base"].items() if f == shard):
            stored = {k: read(dirs[k], maps[k], name) for k in dirs}
            assert all(x.dtype == torch.bfloat16 and x.shape == stored["base"].shape for x in stored.values()), name
            b, h, r = (stored[k].to(device, torch.float32) for k in ("base", a.host, a.donor))
            d = r - b
            if not d.any():
                written[name] = stored[a.host]
                copied += 1
                continue
            add = a.alpha * d
            if a.random:
                n = torch.randn(d.shape, generator=noise, device=device, dtype=torch.float32)
                add = n * (torch.linalg.vector_norm(add) / torch.linalg.vector_norm(n))
            m = to_bf16(h + add, "stochastic", gen)
            w = m.to(torch.float32) - h
            for key, (p, q) in {"host_sq": (h - b, h - b), "donor_sq": (d, d), "host_donor": (h - b, d), "written_donor": (w, d), "written_sq": (w, w)}.items():
                s[key] += torch.sum(p * q, dtype=torch.float64).item()
            written[name] = m.cpu()
        save_file(written, out / shard, metadata={"format": "pt"})
    for p in json_dir.glob("*.json"):
        shutil.copy(p, out / p.name)
    res = {"args": vars(a), "models": {k: {"repo": MODELS[k][0], "revision": MODELS[k][1]} for k in dirs}, "json_from": MODELS[JSON_KEY][0],
           "n_tensors": len(maps["base"]), "n_copied_from_host": copied, "host_delta_norm": s["host_sq"] ** 0.5, "donor_delta_norm": s["donor_sq"] ** 0.5,
           "cos_host_donor": s["host_donor"] / (s["host_sq"] * s["donor_sq"]) ** 0.5 if s["host_sq"] else None,
           "effective_a": s["written_donor"] / s["donor_sq"], "written_norm_over_intended": (s["written_sq"] / s["donor_sq"]) ** 0.5 / a.alpha,
           "seconds": time.time() - t0}
    pathlib.Path(a.stats).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k not in ("args", "models")}), flush=True)
    if a.random:
        assert abs(res["written_norm_over_intended"] - 1) < 0.02, "random control: written norm differs from the intended norm"
    else:
        assert abs(res["effective_a"] - a.alpha) < 0.02 * a.alpha, "the written model does not carry a * (donor - base)"


if __name__ == "__main__":
    main()
