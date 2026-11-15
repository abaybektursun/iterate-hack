"""J-lens workspace diff (specs/SPEC1_lensdiff.md): the J-lens readout of the base and the RL model at every position of the
stored T1 and T2 answers. Inference only: teacher forcing, both models in bf16 on one H100, on the team runner:

    uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.jspace.jobs.lensdiff --commit $(git rev-parse HEAD) --store-layers 16,24"
    smoke: add  --n 12 --pick 20,36,46 --check-every 1

Inputs, token sequences and model loading are those of the RLN-5 map (studies/rlneurons/jobs/rln5_map.py: `build`, `load`,
data/rln5/map_inputs.json). Entry j of every per-position array is read at the input position that predicts written token j,
so the arrays line up with the map's shards row by row.

Both models' activations are read through one fixed map: the base lens J_l, the base final norm and the base lm_head
(lib/jlens_read.py). Top-K lists hold word-like tokens only (a letter or a digit in the decoded string).

Outputs in --out (default $OUT_DIR):
  agg.npz                 prob_sum [cell, group, model, layer, vocab] float32: summed readout probability of every token;
                          presence [same] int32: positions where the token is in the top K; n_pos [cell, group]; and the
                          axis labels (cells, groups, models, layers)
  <cell>_lens_<kkk>.npz   shards of about --shard-positions positions, answers in order of length. Per position: tok (written
                          token id), kind (0 cue, 1 generated, 2 stop), and for each model m and stored layer l: top_<m>_<l>
                          [n, K] int32, tlp_<m>_<l> [n, K] uint8 and watch_<m>_<l> [n, W] uint8 (log-probs stored as
                          round(-lp * 10), capped at 255). Per row: problem_index, offsets, n_prompt, n_cue, n_gen, has_stop.
  index.json              the shards written so far, the watch list and the stored layers
  vocab.json              the decoded string of every token id
  checks.json             the instrument checks of SPEC1 (plumbing, hit@K by layer and variant, top-1 agreement, demo prompt)
  metrics.json            config, commit, job id, lens file record, counts, positions per second

--dry-run uses two small random Olmo 3 models and random J matrices on the CPU to test the file pipeline on a laptop; its
checks are computed and not asserted. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time

import numpy as np
import torch

from studies.jspace.lib import jlens_read as JL
from studies.rlneurons.jobs import rln5_map as M
from studies.rlneurons.lib import n13_score as S

ITEMS = M.STUDY / "results" / "rln4" / "t1_t2_items-01" / "per_problem.json"
GROUPS = ("both", "rl_only", "base_only", "neither")
NAMES = ("base", "rl")
SELF_CHECK = (" Wait", "Wait", " wait", " check", " verify", " mistake", " error", " wrong", " But", " Hmm", " Actually", " again",
              " correct", " double", " careful", " confirm")
NEUTRAL = (" the", " so", " Therefore", " equation")
DEMO = "Fact: The currency used in the country shaped like a boot is"
PLUMB_TOL = 0.1
LO, HI = 2, 32                                        # hit window: written tokens 2 to 32 places ahead


def partner(l, layers):
    return l + 8 if l + 8 in layers else l - 8


def sequences(a, tok, fz):
    """The map's token sequences for the selected answers, per cell, in order of length."""
    frozen = json.loads((M.D5 / "map_inputs.json").read_text())
    math = json.loads((M.D4 / "math500.json").read_text())
    assert M.sha(M.D4 / "math500.json") == fz["sha256"]["math500.json"]
    n13 = json.loads((M.D4 / "prompt_ids.json").read_text())
    sel = {}
    for c in a.cells.split(","):
        p, f = pathlib.Path(a.inputs) / f"{c}.jsonl", frozen["files"][f"{c}.jsonl"]
        assert p.stat().st_size == f["bytes"] and M.sha(p) == f["sha256"], f"{p} differs from data/rln5/map_inputs.json"
        rows = sorted((json.loads(l) for l in p.read_text().splitlines()), key=lambda r: r["problem_index"])
        assert [r["problem_index"] for r in rows] == list(range(500))
        seqs = [M.build(tok, fz, r, math[r["problem_index"]], n13["ids"][r["problem_index"]]) for r in rows]
        seqs = [s for s in seqs if abs(s["retok_diff"]) <= M.TOL * s["n_new"]]
        assert len(seqs) >= 500 - M.MAX_EXCLUDED
        order = sorted(seqs, key=lambda s: (len(s["ids"]), s["idx"]))
        if a.n is not None:
            pick = [s for s in order if s["idx"] in a.pick]
            order = sorted({s["idx"]: s for s in order[:a.n] + pick}.values(), key=lambda s: (len(s["ids"]), s["idx"]))
        sel[c] = order
    return sel, frozen


def toy_models(fz, vocab):
    """--dry-run: two random Olmo 3 models of hidden size 16 with the real depth and vocabulary. No weights, no GPU."""
    from huggingface_hub import snapshot_download
    from transformers import AutoConfig, AutoModelForCausalLM
    d = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["config.json"])
    out = {}
    for k, name in enumerate(NAMES):
        cfg = AutoConfig.from_pretrained(d)
        assert cfg.vocab_size == vocab
        cfg.hidden_size, cfg.intermediate_size, cfg.num_attention_heads, cfg.num_key_value_heads = 16, 32, 2, 2
        torch.manual_seed(k)
        out[name] = AutoModelForCausalLM.from_config(cfg).eval()
    return out


@torch.inference_mode()
def plumbing(m, ids, dev):
    """Max absolute difference between the model's logits and lm_head(final_norm(output of the last block))."""
    last = len(m.model.layers) - 1
    rec = JL.Recorder(m, [last])
    x = torch.tensor(ids, device=dev)[None]
    logits = m(input_ids=x, use_cache=False).logits[0].float()
    got = JL.readout(m, rec.acts[last][0])
    rec.close()
    return float((logits - got).abs().max())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="/runs/inputs/rln5")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    ap.add_argument("--cells", default="T1,T2")
    ap.add_argument("--n", type=int, default=None, help="per cell: only the n shortest answers (smoke)")
    ap.add_argument("--pick", default="", help="with --n: also these problem indices")
    ap.add_argument("--layers", default="10,12,14,16,18,20,22,24,26,28,30")
    ap.add_argument("--store-layers", default="16,24", help="layers whose per-position readout is written to the shards")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--lens-files", default="", help="base=<path>,rl=<path>: matched readout, each model through its own fitted "
                    "lens, final norm and lm_head. Default: the fixed readout (published base lens, base norm and head)")
    ap.add_argument("--check-every", type=int, default=10, help="every n-th answer of a cell also gets the hit@K variants")
    ap.add_argument("--chunk", type=int, default=1024)
    ap.add_argument("--shard-positions", type=int, default=250_000)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    assert a.out, "no --out and no $OUT_DIR"
    a.pick = [int(x) for x in a.pick.split(",") if x]
    layers = [int(x) for x in a.layers.split(",")]
    store = [int(x) for x in a.store_layers.split(",")]
    assert set(store) <= set(layers) and all(partner(l, layers) in layers for l in layers)
    t0 = time.time()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "index.json").exists(), f"{out}/index.json exists: one fresh directory per run"

    fz = json.loads((M.D4 / "frozen4.json").read_text())
    group = {int(p["problem_index"]): p["cell"] for p in json.loads(ITEMS.read_text())}
    assert len(group) == 500 and set(group.values()) == set(GROUPS)
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    sel, frozen = sequences(a, tok, fz)
    cells = list(sel)

    m = {"status": "loading", "config": {**vars(a), "out": str(out)}, "commit": a.commit, "job_id": os.environ.get("JOB_ID"),
         "started_utc": M.utc(), "inputs": frozen["files"], "tokenizer": fz["tokenizer"], "torch": torch.__version__,
         "layers": layers, "store_layers": store, "hit_window": [LO, HI],
         "selected": {c: {"answers": len(sel[c]), "positions": sum(len(s["ids"]) - s["n_prompt"] for s in sel[c])} for c in cells}}
    M.dump(out / "metrics.json", m)

    if a.dry_run:
        dev = "cpu"
        vocab = json.loads((pathlib.Path(tok_dir) / "config.json").read_text())["vocab_size"]
        model = toy_models(fz, vocab)
        g = torch.Generator().manual_seed(0)
        J = {l: torch.eye(16) + 0.1 * torch.randn(16, 16, generator=g) for l in layers}
        Jm = {name: J for name in NAMES}
        m["models"], m["lens"] = {"dry_run": True}, {"dry_run": True}
    else:
        dev = "cuda"
        m["gpu"] = torch.cuda.get_device_name(0)
        model, m["models"] = {}, {}
        for name in NAMES:
            model[name], m["models"][name] = M.load(fz, name, dev)
        vocab = m["models"]["base"]["vocab_size"]
        assert vocab == m["models"]["rl"]["vocab_size"]
        if a.lens_files:
            paths = dict(kv.split("=") for kv in a.lens_files.split(","))
            Jm, m["lens"] = {}, {"matched": True}
            for name in NAMES:
                Jm[name], m["lens"][name] = JL.load_lens_file(paths[name], layers, dev)
        else:
            J, m["lens"] = JL.load_lens(layers, dev)
            Jm = {name: J for name in NAMES}
    # fixed readout: the base final norm and lm_head for both models; matched readout: each model's own
    heads = {name: model[name] if a.lens_files else model["base"] for name in NAMES}
    strings = [tok.decode([i]) for i in range(vocab)]
    M.dump(out / "vocab.json", strings)
    mask = JL.wordlike_mask(tok, vocab).to(dev)
    watch, dropped = [], []
    for w in SELF_CHECK + NEUTRAL:
        ids = tok.encode(w, add_special_tokens=False)
        (watch if len(ids) == 1 else dropped).append((w, ids))
    watch_ids = torch.tensor([ids[0] for _, ids in watch], device=dev)
    assert bool(mask[watch_ids].all())
    m["watch"] = {"tokens": [w for w, _ in watch], "ids": [ids[0] for _, ids in watch], "dropped": [w for w, _ in dropped],
                  "n_self_check": sum(w in SELF_CHECK for w, _ in watch)}
    m["wordlike_tokens"] = int(mask.sum())
    m["load_s"] = time.time() - t0
    m["status"] = "running"
    M.dump(out / "metrics.json", m)
    print(f"loaded in {m['load_s']:.0f} s; watch {m['watch']['tokens']}; dropped {m['watch']['dropped']}", flush=True)

    checks = {}
    # check 1: plumbing, both models, on the start of the shortest answer
    short = sel[cells[0]][0]["ids"][:512]
    checks["plumbing"] = {name: plumbing(model[name], short, dev) for name in NAMES}
    checks["plumbing"]["pass"] = all(checks["plumbing"][name] <= PLUMB_TOL for name in NAMES)
    # check 4: the lens repository's demo prompt, top-10 at the last two positions, J-lens and logit lens
    demo_ids = tok.encode(DEMO, add_special_tokens=False)
    checks["demo"] = {"prompt": DEMO, "tokens": [strings[i] for i in demo_ids], "readout": {}}
    with torch.inference_mode():
        for name in NAMES:
            rec = JL.Recorder(model[name], layers)
            model[name].model(input_ids=torch.tensor(demo_ids, device=dev)[None], use_cache=False)
            for l in layers:
                for variant, j in (("jlens", Jm[name][l]), ("logit", None)):
                    lg = JL.readout(heads[name], rec.acts[l][0, -2:], j).masked_fill(~mask, float("-inf"))
                    top = lg.topk(10, -1).indices.tolist()
                    checks["demo"]["readout"][f"{name}_L{l}_{variant}"] = {"position_-2": [strings[i] for i in top[0]],
                                                                            "position_-1": [strings[i] for i in top[1]]}
            rec.close()
    M.dump(out / "checks.json", checks)
    print("plumbing", checks["plumbing"], flush=True)

    C, G, L, K = len(cells), len(GROUPS), len(layers), a.k
    prob_sum = torch.zeros(C, G, 2, L, vocab, dtype=torch.float64, device=dev)
    presence = torch.zeros(C, G, 2, L, vocab, dtype=torch.float64, device=dev)
    n_pos = np.zeros((C, G), dtype=np.int64)
    VARIANTS = ("jlens", "logit", "wrong_layer")
    hit = {name: {v: np.zeros((C, L, 3), dtype=np.int64) for v in VARIANTS} for name in NAMES}  # hits, shifted hits, valid
    agree = {name: np.zeros((C, L, 2), dtype=np.int64) for name in NAMES}                       # readout top-1 = model top-1
    recs = {name: JL.Recorder(model[name], layers) for name in NAMES}
    index = {"shards": [], "watch": m["watch"], "store_layers": store, "k": K, "qscale": JL.QSCALE,
             "per_row": ["problem_index", "offsets", "n_prompt", "n_cue", "n_gen", "has_stop"]}
    done_pos, t_run = 0, time.time()

    def flush(c, buf, k):
        arrs = {key: np.concatenate([x[key] for _, x in buf]) for key in buf[0][1]}
        lens = [len(x["tok"]) for _, x in buf]
        rowd = {"problem_index": np.array([s["idx"] for s, _ in buf]), "offsets": np.concatenate([[0], np.cumsum(lens)]),
                **{key: np.array([s[key] for s, _ in buf]) for key in ("n_prompt", "n_cue", "n_gen", "has_stop")}}
        name = f"{c}_lens_{k:03d}.npz"
        np.savez_compressed(out / name, **arrs, **rowd)
        index["shards"].append({"file": name, "cell": c, "answers": len(buf), "positions": int(len(arrs["tok"]))})
        M.dump(out / "index.json", index)

    with torch.inference_mode():
        for ci, c in enumerate(cells):
            buf, k_shard = [], 0
            for si, s in enumerate(sel[c]):
                gi = GROUPS.index(group[s["idx"]])
                check = si % a.check_every == 0
                ids = torch.tensor(s["ids"], device=dev)
                x, first = ids[None, :-1], s["n_prompt"] - 1
                n_out = len(s["ids"]) - s["n_prompt"]
                res = {"tok": np.array(s["ids"][s["n_prompt"]:], dtype=np.int32), "kind": M.kinds(s)}
                for mi, name in enumerate(NAMES):
                    past, keep = None, {(l, v): [] for l in layers for v in (VARIANTS if check else ("jlens",))}
                    stored = {(l, key): [] for l in store for key in ("top", "tlp", "watch")}
                    for st in range(0, x.shape[1], a.chunk):
                        o = model[name].model(input_ids=x[:, st:st + a.chunk], past_key_values=past, use_cache=True)
                        past = o.past_key_values
                        lo = max(first - st, 0)
                        if lo >= o.last_hidden_state.shape[1]:
                            continue
                        own = model[name].lm_head(o.last_hidden_state[0, lo:]).argmax(-1) if check else None
                        for li, l in enumerate(layers):
                            h = recs[name].acts[l][0, lo:]
                            lp = torch.log_softmax(JL.readout(heads[name], h, Jm[name][l]), -1)
                            prob_sum[ci, gi, mi, li] += lp.exp().sum(0, dtype=torch.float64)
                            tv, ti = lp.masked_fill(~mask, float("-inf")).topk(K, -1)
                            presence[ci, gi, mi, li].index_add_(0, ti.reshape(-1), torch.ones(ti.numel(), dtype=torch.float64, device=dev))
                            keep[(l, "jlens")].append(ti)
                            if l in store:
                                stored[(l, "top")].append(ti.to(torch.int32).cpu())
                                stored[(l, "tlp")].append(JL.quant(tv).cpu())
                                stored[(l, "watch")].append(JL.quant(lp[:, watch_ids]).cpu())
                            if check:
                                agree[name][ci, li] += np.array([int((lp.argmax(-1) == own).sum()), len(own)])
                                keep[(l, "logit")].append(JL.readout(heads[name], h).masked_fill(~mask, float("-inf")).topk(K, -1).indices)
                                keep[(l, "wrong_layer")].append(JL.readout(heads[name], h, Jm[name][partner(l, layers)]).masked_fill(~mask, float("-inf")).topk(K, -1).indices)
                    if check:
                        for (l, v), parts in keep.items():
                            hit[name][v][ci, layers.index(l)] += np.array(JL.future_hits(torch.cat(parts), ids, first, LO, HI))
                    for (l, key), parts in stored.items():
                        res[f"{key}_{name}_{l}"] = torch.cat(parts).numpy()
                        assert len(res[f"{key}_{name}_{l}"]) == n_out
                    del past
                assert len(res["tok"]) == n_out == len(res["kind"])
                n_pos[ci, gi] += n_out
                done_pos += n_out
                buf.append((s, res))
                if sum(len(r["tok"]) for _, r in buf) >= a.shard_positions:
                    flush(c, buf, k_shard)
                    buf, k_shard = [], k_shard + 1
                    print(f"{c} {si + 1}/{len(sel[c])} answers, {done_pos} positions, {done_pos / (time.time() - t_run):.0f} positions/s", flush=True)
            if buf:
                flush(c, buf, k_shard)

    np.savez_compressed(out / "agg.npz", prob_sum=prob_sum.cpu().numpy().astype(np.float32),
                        presence=presence.cpu().numpy().astype(np.int32), n_pos=n_pos, cells=np.array(cells),
                        groups=np.array(GROUPS), models=np.array(NAMES), layers=np.array(layers))

    # checks 2 and 3: hit@K by layer for each variant, and readout top-1 against the model's own next token
    rate = lambda h: None if h[2] == 0 else float(h[0] / h[2])
    checks["hit"] = {"k": K, "window": [LO, HI], "by_layer": {}}
    for li, l in enumerate(layers):
        row = {}
        for name in NAMES:
            for ci, c in enumerate(cells):
                e = {v: rate(hit[name][v][ci, li]) for v in VARIANTS}
                e["shifted_window"] = rate(hit[name]["jlens"][ci, li, [1, 1, 2]])
                e["positions"] = int(hit[name]["jlens"][ci, li, 2])
                e["top1_agrees_with_model"] = rate(agree[name][ci, li, [0, 0, 1]])
                e["works"] = None if e["jlens"] is None else bool(e["jlens"] > max(e["logit"], e["wrong_layer"], e["shifted_window"]))
                row[f"{name}_{c}"] = e
        checks["hit"]["by_layer"][str(l)] = row
    M.dump(out / "checks.json", checks)
    for l in layers:
        for k, e in checks["hit"]["by_layer"][str(l)].items():
            if e["jlens"] is not None:
                print(f"L{l} {k}: hit@{K} jlens {e['jlens']:.3f} logit {e['logit']:.3f} wrong-layer {e['wrong_layer']:.3f} shifted "
                      f"{e['shifted_window']:.3f} | top-1 agrees {e['top1_agrees_with_model']:.3f} | works {e['works']}", flush=True)

    m.update(status="done", positions=done_pos, run_s=time.time() - t_run, positions_per_s=done_pos / (time.time() - t_run),
             n_pos={c: {g: int(n_pos[ci, gi]) for gi, g in enumerate(GROUPS)} for ci, c in enumerate(cells)}, finished_utc=M.utc())
    if dev == "cuda":
        m["max_memory_gb"] = torch.cuda.max_memory_allocated() / 2 ** 30
    M.dump(out / "metrics.json", m)
    assert a.dry_run or checks["plumbing"]["pass"], ("plumbing check failed", checks["plumbing"])


if __name__ == "__main__":
    main()
