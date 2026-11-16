"""Alignment of two weight changes (specs/SPEC_transplant.md, amendment 6): d1 = a - a0 and d2 = b - b0, tensor by tensor.

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.delta_align --a allenai/Olmo-3-7B-Think@<rev> --a0 think_sft --b rl_math --b0 base

Each model is a key of wsp_delta_anatomy.MODELS or <repo>@<revision>; all hold the same tensor names. Weights only, no generation.
Writes $OUT_DIR/delta_align.json:
  total     ||d1||, ||d2||, their cosine over all tensors, and the cosine of d1 with a0 - b0 when a0 is not b0
  matrices  per 2-D tensor where both changes are non-zero: norms, cosine, and for k = 8
            own1, own2      the share of each change's squared norm in its own top-k singular directions
            d1_in_d2        the share of d1's squared norm inside d2's top-k directions (||U2' d1 V2||^2 / ||d1||^2), and d2_in_d1
            chance          k^2 / (rows x columns), the share a random matrix would have there
            cos_in_d2       the cosine of d1 with d2's rank-k part
Fail loud: no try/except.
"""
import argparse
import json
import os
import pathlib

import torch

from studies.rlneurons.jobs.wsp_delta_anatomy import MODELS
from studies.rlneurons.jobs.wsp_edit import read, weight_map

K = 8


def main():
    ap = argparse.ArgumentParser()
    for k in ("a", "a0", "b", "b0"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    torch.set_grad_enabled(False)
    from huggingface_hub import snapshot_download
    models = {k: MODELS[v] if v in MODELS else tuple(v.split("@")) for k, v in vars(a).items()}
    dirs = {k: pathlib.Path(snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors"])) for k, (repo, rev) in models.items()}
    maps = {k: weight_map(d) for k, d in dirs.items()}
    assert len({frozenset(m) for m in maps.values()}) == 1, "the models hold different tensor names"
    s = dict.fromkeys(("d1_sq", "d2_sq", "d1_d2", "h_sq", "d1_h"), 0.0)
    rows = []
    dot = lambda p, q: torch.sum(p * q, dtype=torch.float64).item()
    for name in sorted(maps["a"]):
        t = {k: read(dirs[k], maps[k], name).to("cuda", torch.float32) for k in dirs}
        d1, d2, h = t["a"] - t["a0"], t["b"] - t["b0"], t["a0"] - t["b0"]
        for key, (p, q) in {"d1_sq": (d1, d1), "d2_sq": (d2, d2), "d1_d2": (d1, d2), "h_sq": (h, h), "d1_h": (d1, h)}.items():
            s[key] += dot(p, q)
        if d1.ndim != 2 or not d1.any() or not d2.any():
            continue
        (u1, s1, v1), (u2, s2, v2) = (torch.linalg.svd(d, full_matrices=False) for d in (d1, d2))
        n1, n2 = dot(d1, d1), dot(d2, d2)
        low2 = (u2[:, :K] * s2[:K]) @ v2[:K]
        rows.append({"name": name, "shape": list(d1.shape), "norm1": n1 ** 0.5, "norm2": n2 ** 0.5, "cos": dot(d1, d2) / (n1 * n2) ** 0.5,
                     "own1": (s1[:K] ** 2).sum().item() / n1, "own2": (s2[:K] ** 2).sum().item() / n2,
                     "d1_in_d2": (u2[:, :K].T @ d1 @ v2[:K].T).pow(2).sum().item() / n1,
                     "d2_in_d1": (u1[:, :K].T @ d2 @ v1[:K].T).pow(2).sum().item() / n2,
                     "chance": K * K / (d1.shape[0] * d1.shape[1]), "cos_in_d2": dot(d1, low2) / (n1 * dot(low2, low2)) ** 0.5})
    res = {"args": vars(a), "models": {k: {"repo": r, "revision": v} for k, (r, v) in models.items()}, "k": K,
           "total": {"norm1": s["d1_sq"] ** 0.5, "norm2": s["d2_sq"] ** 0.5, "cos": s["d1_d2"] / (s["d1_sq"] * s["d2_sq"]) ** 0.5,
                     "norm_a0_minus_b0": s["h_sq"] ** 0.5, "cos_d1_with_a0_minus_b0": s["d1_h"] / (s["d1_sq"] * s["h_sq"]) ** 0.5 if s["h_sq"] else None},
           "matrices": rows}
    pathlib.Path(os.environ["OUT_DIR"], "delta_align.json").write_text(json.dumps(res, indent=1) + "\n")
    med = lambda key: sorted(r[key] for r in rows)[len(rows) // 2]
    print(json.dumps({**res["total"], "n_matrices": len(rows), **{"median_" + k: med(k) for k in ("cos", "own1", "own2", "d1_in_d2", "d2_in_d1", "chance", "cos_in_d2")}}), flush=True)


if __name__ == "__main__":
    main()
