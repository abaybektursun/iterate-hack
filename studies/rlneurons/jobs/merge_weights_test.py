"""Planted cases for merge_weights.py on two tiny bf16 models (laptop, CPU, no download).

    uv run --no-project --with torch --with safetensors --with numpy python -m studies.rlneurons.jobs.merge_weights_test

The other model differs from the base by one bf16 unit in the last place on 30 % of entries (the size of an RL update). Checks: a = 0 and a = 1 give the endpoints exactly; with stochastic rounding the effective a
is within 0.03 of a for a in POINTS, with nearest rounding a = 0.25 collapses to the base and a = 0.75 to the other model; the random control
has the norm of the difference before rounding and is nearly orthogonal to it; a shard layout that differs fails.
"""
import json
import pathlib
import tempfile

import torch
from safetensors import safe_open
from safetensors.torch import save_file

from studies.rlneurons.jobs import merge_weights as M


def model(d, tensors):
    d.mkdir()
    shards = {"model-00001-of-00002.safetensors": ["model.embed_tokens.weight", "model.layers.0.mlp.up_proj.weight"],
              "model-00002-of-00002.safetensors": ["model.layers.0.self_attn.q_proj.weight", "lm_head.weight"]}
    for f, names in shards.items():
        save_file({n: tensors[n] for n in names}, d / f, metadata={"format": "pt"})
    (d / "model.safetensors.index.json").write_text(json.dumps({"weight_map": {n: f for f, ns in shards.items() for n in ns}}))
    (d / "config.json").write_text("{}")


def load(d):
    out = {}
    for f in d.glob("*.safetensors"):
        with safe_open(f, "pt") as h:
            out.update({n: h.get_tensor(n) for n in h.keys()})
    return out


def main():
    g = torch.Generator().manual_seed(1)
    shapes = {"model.embed_tokens.weight": (64, 32), "model.layers.0.mlp.up_proj.weight": (128, 32),
              "model.layers.0.self_attn.q_proj.weight": (32, 32), "lm_head.weight": (64, 32)}
    base = {n: (0.02 * torch.randn(s, generator=g)).to(torch.bfloat16) for n, s in shapes.items()}
    other = {}
    for n, b in base.items():
        bits = b.view(torch.int16).clone()
        mask = torch.rand(b.shape, generator=g) < 0.3
        step = torch.where(torch.rand(b.shape, generator=g) < 0.5, 1, -1).to(torch.int16)
        other[n] = torch.where(mask, bits + step, bits).view(torch.bfloat16)
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        model(t / "base", base)
        model(t / "other", other)
        for a, want in ((0.0, base), (1.0, other)):
            for ro in ("nearest", "stochastic"):
                out = t / f"m_{a}_{ro}"
                st = M.merge(t / "base", t / "other", a, False, ro, out, 0, "cpu", t / "base")
                got = load(out)
                assert all(torch.equal(got[n], want[n]) for n in want), (a, ro)
                assert st["identity"] == {"exact": 4, "tensors": 4}, st["identity"]
                assert (out / "config.json").exists()
        st = M.merge(t / "base", t / "other", None, False, None, None, 0, "cpu", None)
        p = st["points"]
        for a in M.POINTS:
            assert abs(p[f"a={a:g} stochastic"]["effective_a"] - a) < 0.03, (a, p[f"a={a:g} stochastic"])
        assert p["a=0.25 nearest"]["effective_a"] < 0.05 and p["a=0.75 nearest"]["effective_a"] > 0.95, p   # nearest rounding
        r = p["random stochastic"]
        assert abs(r["target_norm_ratio"] - 1) < 1e-4 and abs(r["target_cos_delta"]) < 0.1, r
        assert 0.25 < st["overall"]["frac_changed"] < 0.35 and st["delta_ulp_hist"][4] == 0, (st["overall"], st["delta_ulp_hist"])
        print(json.dumps({"points": p, "delta_ulp_hist": st["delta_ulp_hist"], "groups": {k: v["rel_norm"] for k, v in st["groups"].items()}}, indent=1))
        out = t / "rand"
        st = M.merge(t / "base", t / "other", None, True, "stochastic", out, 0, "cpu", t / "base")
        got = load(out)
        assert not any(torch.equal(got[n], base[n]) for n in base), "random control left a tensor unchanged"
        # a different shard layout must fail
        (t / "other" / "model.safetensors.index.json").write_text(json.dumps({"weight_map": {n: "model-00001-of-00002.safetensors" for n in base}}))
        try:
            M.merge(t / "base", t / "other", 0.5, False, "nearest", t / "bad", 0, "cpu", t / "base")
        except AssertionError as e:
            print("planted layout mismatch failed as it must:", e)
        else:
            raise SystemExit("planted layout mismatch passed")
    print("merge_weights_test: all checks passed")


if __name__ == "__main__":
    main()
