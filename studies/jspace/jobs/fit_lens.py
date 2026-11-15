"""Fit a J-lens for one Olmo model with the reference code (anthropics/jacobian-lens at 581d398), so that the base and the RL
model each get a lens fitted with the same code, the same prompts and the same settings. One H100:

    uv run tools/gpu.py submit h100 --hours 2.5 -- "bash studies/jspace/jobs/fit_lens.sh --model rl --commit $(git rev-parse HEAD)"
    smoke: add  --n 2

Corpus `wikitext`: the first --n records of WikiText-103 with at least 600 characters (the corpus of the published base
lens). Corpus `math`: stretches of the stored T1 and T2 answers (Volume iterate-runs, inputs/rln5), alternating between the
two cells, one stretch of 1,500 characters from the middle of each answer; the same list for both models.

Per prompt the reference code runs one forward pass and ceil(d_model / dim_batch) backward passes, and averages the Jacobian of
the last block's output with respect to each source layer over the source positions 16 and later (jlens/fitting.py).

Outputs in --out (default $OUT_DIR): <model>_<corpus>_jlens.pt (the lens file of jlens: {"J": {layer: [d, d] fp16}, ...}),
metrics.json (config, commit, seconds per prompt, memory, a record of the prompts). Fail loud: no try/except.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import time

import torch

from studies.rlneurons.jobs import rln5_map as M


def math_prompts(n, inputs):
    """n stretches of 1,500 characters, alternating T1 and T2 answers by problem index, from the middle of each answer."""
    rows = {}
    for c in ("T1", "T2"):
        rows[c] = sorted((json.loads(l) for l in (pathlib.Path(inputs) / f"{c}.jsonl").read_text().splitlines()),
                         key=lambda r: r["problem_index"])
    out = []
    for i in range(500):
        for c in ("T1", "T2"):
            if (i + (c == "T2")) % 2:                 # T1 for even problems, T2 for odd ones
                continue
            t = rows[c][i]["text"]
            if len(t) >= 2500:
                out.append(t[len(t) // 2 - 750:len(t) // 2 + 750])
        if len(out) >= n:
            break
    assert len(out) >= n, len(out)
    return out[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=("base", "rl"))
    ap.add_argument("--corpus", default="wikitext", choices=("wikitext", "math"))
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--layers", default="10-30")
    ap.add_argument("--dim-batch", type=int, default=64)
    ap.add_argument("--max-seq-len", type=int, default=128)
    ap.add_argument("--inputs", default="/runs/inputs/rln5")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True)
    a = ap.parse_args()
    assert a.out, "no --out and no $OUT_DIR"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    lo, hi = (int(x) for x in a.layers.split("-"))
    layers = list(range(lo, hi + 1))

    import jlens
    from jlens.examples import load_wikitext_prompts
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    jlens.configure_logging()
    fz = json.loads((M.D4 / "frozen4.json").read_text())
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    prompts = load_wikitext_prompts(a.n) if a.corpus == "wikitext" else math_prompts(a.n, a.inputs)
    assert len(prompts) == a.n
    t0 = time.time()
    hf, info = M.load(fz, a.model, "cuda")
    model = jlens.from_hf(hf, tok)
    m = {"status": "running", "config": {**vars(a), "out": str(out)}, "commit": a.commit, "job_id": os.environ.get("JOB_ID"),
         "started_utc": M.utc(), "model": info, "layers": layers, "gpu": torch.cuda.get_device_name(0), "torch": torch.__version__,
         "jlens": getattr(jlens, "__version__", None), "load_s": time.time() - t0,
         "prompts": {"n": len(prompts), "sha256": hashlib.sha256("\x00".join(prompts).encode()).hexdigest(),
                     "first_80_chars": [p[:80] for p in prompts[:3]]}}
    M.dump(out / "metrics.json", m)
    t1 = time.time()
    lens = jlens.fit(model, prompts, source_layers=layers, dim_batch=a.dim_batch, max_seq_len=a.max_seq_len,
                     checkpoint_path=str(out / "checkpoint.pt"), checkpoint_every=20)
    fit_s = time.time() - t1
    name = f"{a.model}_{a.corpus}_jlens.pt"
    lens.save(str(out / name))
    (out / "checkpoint.pt").unlink()
    d = torch.load(out / name, map_location="cpu", weights_only=True)
    assert sorted(int(k) for k in d["J"]) == layers and all(torch.isfinite(v.float()).all() for v in d["J"].values())
    m.update(status="done", fit_s=fit_s, s_per_prompt=fit_s / len(prompts), lens_file=name, lens_bytes=(out / name).stat().st_size,
             n_prompts_in_file=int(d["n_prompts"]), max_memory_gb=torch.cuda.max_memory_allocated() / 2 ** 30, finished_utc=M.utc())
    M.dump(out / "metrics.json", m)
    print(json.dumps({k: m[k] for k in ("fit_s", "s_per_prompt", "max_memory_gb", "lens_bytes", "n_prompts_in_file")}), flush=True)


if __name__ == "__main__":
    main()
