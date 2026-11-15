"""Workspace tests on the base and the RL model (specs/SPEC2_workspace.md): the lens repository's readout sets and two-hop
swap, plus arithmetic chains and right/wrong twins. Short prompts, both models in bf16 on one GPU, a few minutes:

    uv run tools/gpu.py submit h100 --hours 0.5 -- "python -m studies.jspace.jobs.workspace_tests --commit $(git rev-parse HEAD)"
    add a fitted lens per model:  --lens-files own:base=/runs/<job>/base_wikitext_jlens.pt,rl=/runs/<job>/rl_wikitext_jlens.pt
    smoke: add  --limit 8

Each model is read through its own final norm and lm_head. Lens variants: `pub` (the published base lens, for both models),
every label of --lens-files (one file per model), and `logit` (no Jacobian). Prompts are tokenized as written, with no
beginning-of-sequence token.

Parts (outputs in --out, default $OUT_DIR, one JSON file each):
  readout.json   per set and item: whether each model's greedy next token is a prefix of the target, and for each model,
                 variant and layer the rank of every intermediate at the readout position (1 = top; tokens with no letter or
                 digit are masked, candidates spared). Candidates of a word: its single-token forms among as written,
                 capitalized and lower case, each with and without a leading space.
  swap.json      per item, model, variant and strength: is the item eligible (the clean answer is the top word-like token),
                 and after swapping the two lens coordinates at every layer and every position but the first, is the top
                 word-like token the swap answer, the clean answer, or neither. `null` rows swap toward an unrelated token and
                 are still scored on the swap answer.
  twins.json     per twin, model and version (correct, error): from the position of the differing number to the end, for each
                 variant and layer the readout log-probability of the hold-on tokens (log of their summed probability) and the
                 rank of the right result; and from the model's own output the same hold-on log-probability and its top token.
  checks.json    plumbing check and the demo prompt readout.  metrics.json  config, commit, lens records, counts, timing.

--dry-run uses two small random Olmo 3 models and random J matrices on the CPU. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import random
import time

import torch

from studies.jspace.jobs import lensdiff as LD
from studies.jspace.lib import jlens_read as JL
from studies.rlneurons.jobs import rln5_map as M

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"
SETS = ("multihop", "multilingual", "order-ops", "poetry", "association", "typo")
GRADED = {"multihop": "target", "multilingual": "target", "order-ops": "target", "poetry": "intermediate"}
HOLD = (" Wait", "Wait", " wait", " Hmm", "Hmm", " hmm")
NEUTRAL = (" the", " so", " Therefore", " and", " is", " of")       # matched control family for the twins
ALPHAS = (0.5, 1.0, 2.0, 4.0)
NAMES = LD.NAMES


def forms(word):
    return {word, word[:1].upper() + word[1:], word.lower()}


def cands(tok, word):
    """Single-token ids of the word's forms, with and without a leading space."""
    out = set()
    for w in forms(word):
        for s in (w, " " + w):
            ids = tok.encode(s, add_special_tokens=False)
            if len(ids) == 1:
                out.add(ids[0])
    return sorted(out)


def first_ids(tok, word):
    """First token id of every form of an answer, with and without a leading space."""
    return sorted({tok.encode(s, add_special_tokens=False)[0] for w in forms(word) for s in (w, " " + w)})


def vec_id(tok, word):
    """The one token whose lens vector stands for the word: its leading-space form if that is one token, else the bare form."""
    for s in (" " + word, word):
        ids = tok.encode(s, add_special_tokens=False)
        if len(ids) == 1:
            return ids[0]
    return None


@torch.inference_mode()
def run(model, rec, ids, dev):
    """Block outputs {layer: [n, d]} and the model's own logits [n, vocab] (fp32) for one prompt."""
    o = model.model(input_ids=torch.tensor(ids, device=dev)[None], use_cache=False)
    return {l: a[0] for l, a in rec.acts.items()}, model.lm_head(o.last_hidden_state[0]).float()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True)
    ap.add_argument("--layers", default="12,15,18,21,24,27,30")
    ap.add_argument("--lens-files", default="", help="label:base=<path>,rl=<path>;label2:...")
    ap.add_argument("--parts", default="readout,swap,twins")
    ap.add_argument("--limit", type=int, default=None, help="only the first n items of every set (smoke)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    assert a.out, "no --out and no $OUT_DIR"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), "one fresh directory per run"
    layers = [int(x) for x in a.layers.split(",")]
    parts = a.parts.split(",")
    t0 = time.time()

    fz = json.loads((M.D4 / "frozen4.json").read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    m = {"status": "loading", "config": {**vars(a), "out": str(out)}, "commit": a.commit, "job_id": os.environ.get("JOB_ID"),
         "started_utc": M.utc(), "layers": layers, "torch": torch.__version__, "lens": {}}

    if a.dry_run:
        dev = "cpu"
        vocab = json.loads((pathlib.Path(tok_dir) / "config.json").read_text())["vocab_size"]
        model = LD.toy_models(fz, vocab)
        g = torch.Generator().manual_seed(0)
        pub = {l: torch.eye(16) + 0.1 * torch.randn(16, 16, generator=g) for l in layers}
    else:
        dev = "cuda"
        m["gpu"] = torch.cuda.get_device_name(0)
        model, m["models"] = {}, {}
        for name in NAMES:
            model[name], m["models"][name] = M.load(fz, name, dev)
        vocab = m["models"]["base"]["vocab_size"]
        pub, m["lens"]["pub"] = JL.load_lens(layers, dev)
    lens = {"pub": {name: pub for name in NAMES}, "logit": {name: {l: None for l in layers} for name in NAMES}}
    for spec in [s for s in a.lens_files.split(";") if s]:
        label, files = spec.split(":", 1)
        paths = dict(kv.split("=") for kv in files.split(","))
        lens[label], m["lens"][label] = {}, {}
        for name in NAMES:
            lens[label][name], m["lens"][label][name] = JL.load_lens_file(paths[name], layers, dev)
    variants = list(lens)
    lens_variants = [v for v in variants if v != "logit"]
    strings = [tok.decode([i]) for i in range(vocab)]
    mask = JL.wordlike_mask(tok, vocab).to(dev)
    hold = torch.tensor([enc(s)[0] for s in HOLD], device=dev)
    neutral = torch.tensor([enc(s)[0] for s in NEUTRAL], device=dev)
    assert all(len(enc(s)) == 1 for s in HOLD + NEUTRAL)
    recs = {name: JL.Recorder(model[name], layers) for name in NAMES}
    m.update(status="running", variants=variants, load_s=time.time() - t0)
    M.dump(out / "metrics.json", m)

    def readout(name, v, l, h):
        return JL.readout(model[name], h, lens[v][name][l])

    def top_word(lg):
        return int(lg.masked_fill(~mask, float("-inf")).argmax())

    checks = {"plumbing": {name: LD.plumbing(model[name], enc(LD.DEMO * 3), dev) for name in NAMES}}
    checks["plumbing"]["pass"] = all(checks["plumbing"][name] <= LD.PLUMB_TOL for name in NAMES)
    demo = enc(LD.DEMO)
    checks["demo"] = {"prompt": LD.DEMO, "tokens": [strings[i] for i in demo], "readout": {}}
    for name in NAMES:
        acts, _ = run(model[name], recs[name], demo, dev)
        for v in variants:
            for l in layers:
                lg = readout(name, v, l, acts[l][-2:]).masked_fill(~mask, float("-inf"))
                checks["demo"]["readout"][f"{name}_{v}_L{l}"] = [[strings[i] for i in row] for row in lg.topk(8, -1).indices.tolist()]
    M.dump(out / "checks.json", checks)
    print("plumbing", checks["plumbing"], flush=True)

    # ---------------------------------------------------------------- part 1: readout sets
    if "readout" in parts:
        sets = {s: json.loads((DATA / "jlens_581d398" / f"lens-eval-{s}.json").read_text())["items"] for s in SETS}
        sets["chains"] = json.loads((DATA / "math_stimuli_v1.json").read_text())["chains"]
        res = {}
        for s, items in sets.items():
            rows = []
            items = items[:a.limit]
            for i, it in enumerate(items):
                ids = enc(it["prompt"])
                pick = lambda x: x["intermediates"][:1] if s == "order-ops" else x["intermediates"]   # order-ops: the number only
                inter = pick(it)
                # null: the intermediates of the next item of the set that shares no intermediate with this one
                other = next(o for o in items[i + 1:] + items[:i] if not set(pick(o)) & set(inter))
                cs = [cands(tok, w) for w in inter] + [cands(tok, w) for w in pick(other)]
                pos = len(ids) - 1
                if s == "poetry":
                    pos = max(i for i, t in enumerate(ids) if "\n" in strings[t])
                gold = it.get("target") if GRADED.get(s, "target") == "target" else it["intermediates"][0]
                row = {"name": it["name"], "n_tokens": len(ids), "readout_position": pos, "intermediates": inter,
                       "null_intermediates": pick(other), "n_candidates": [len(c) for c in cs], "correct": {}, "next_token": {},
                       "ranks": {}}                # ranks[model][variant][k][layer]; k runs over intermediates, then null ones
                for name in NAMES:
                    acts, logits = run(model[name], recs[name], ids, dev)
                    nxt = strings[int(logits[-1].argmax())]
                    row["next_token"][name] = nxt
                    row["correct"][name] = None if s not in GRADED and s != "chains" else bool(nxt.lstrip() and gold.startswith(nxt.lstrip()))
                    row["ranks"][name] = {}
                    for v in variants:
                        per_inter = [[] for _ in cs]
                        for l in layers:
                            lg = readout(name, v, l, acts[l][pos:pos + 1])[0]
                            for k, c in enumerate(cs):
                                if not c:
                                    per_inter[k].append(None)
                                    continue
                                keep = mask.clone()
                                keep[c] = True
                                best = lg[c].max()
                                per_inter[k].append(int((lg.masked_fill(~keep, float("-inf")) > best).sum()) + 1)
                        row["ranks"][name][v] = per_inter
                rows.append(row)
            res[s] = rows
            print(f"readout {s}: {len(rows)} items; correct base {sum(bool(r['correct']['base']) for r in rows)}, "
                  f"rl {sum(bool(r['correct']['rl']) for r in rows)}", flush=True)
        M.dump(out / "readout.json", res)

    # ---------------------------------------------------------------- part 2: swap
    if "swap" in parts:
        probe = json.loads((DATA / "jlens_581d398" / "probe-swap.json").read_text())["items"]
        rng = random.Random(0)
        items = []
        for it in probe[:a.limit]:
            other = rng.choice([o for o in probe if o["category"] != it["category"]])
            items.append({"name": it["name"], "set": "probe-swap", "prompt": it["prompt"], "src": it["intermediate"], "dst": it["swap_to"],
                          "null": other["swap_to"], "answer": it["answer"], "swap_answer": it["swap_answer"]})
        for it in json.loads((DATA / "math_stimuli_v1.json").read_text())["chains"]:
            if "swap_to" in it and (a.limit is None or sum(x["set"] == "chains" for x in items) < a.limit):
                items.append({"name": it["name"], "set": "chains", "prompt": it["prompt"], "src": it["swap_from"], "dst": it["swap_to"],
                              "null": it["null_to"], "answer": it["target"], "swap_answer": it["swap_answer"]})
        rows = []
        for it in items:
            ids = enc(it["prompt"])
            t = {k: vec_id(tok, it[k]) for k in ("src", "dst", "null")}
            ans, swp = first_ids(tok, it["answer"]), first_ids(tok, it["swap_answer"])
            row = {"name": it["name"], "set": it["set"], "tokens": {k: (None if v is None else strings[v]) for k, v in t.items()}, "models": {}}
            for name in NAMES:
                clean, logits = run(model[name], recs[name], ids, dev)
                e = {"clean_top": strings[top_word(logits[-1])], "eligible": top_word(logits[-1]) in ans and None not in t.values(), "arms": {}}
                if e["eligible"]:
                    W = model[name].lm_head.weight
                    for v in variants:
                        for arm, dst in (("swap", t["dst"]), ("null", t["null"])):
                            V, P = {}, {}
                            for l in layers:
                                J = lens[v][name][l]
                                u = torch.stack([W[t["src"]].float(), W[dst].float()])           # [2, d]
                                u = u if J is None else u @ J
                                u = u / u.norm(dim=1, keepdim=True)
                                if abs(float(u[0] @ u[1])) <= 0.999:
                                    V[l], P[l] = u.T.contiguous(), torch.linalg.pinv(u.T)        # [d, 2], [2, d]
                            for alpha in ALPHAS:
                                handles = []
                                for l in V:
                                    cstar = alpha * (clean[l][1:].float() @ P[l].T)[:, [1, 0]]

                                    def hook(_mod, _inp, o, V=V[l], P=P[l], cstar=cstar):
                                        h = o[0] if isinstance(o, tuple) else o
                                        x = h[0, 1:].float()
                                        h2 = h.clone()
                                        h2[0, 1:] = (x + (cstar - x @ P.T) @ V.T).to(h.dtype)
                                        return (h2,) + tuple(o[1:]) if isinstance(o, tuple) else h2
                                    handles.append(model[name].model.layers[l].register_forward_hook(hook))
                                _, lg = run(model[name], recs[name], ids, dev)
                                for hd in handles:
                                    hd.remove()
                                top = top_word(lg[-1])
                                e["arms"][f"{v}|{arm}|{alpha}"] = {"top": strings[top], "is_swap_answer": top in swp, "is_answer": top in ans,
                                                                   "layers_used": len(V)}
                row["models"][name] = e
            rows.append(row)
        M.dump(out / "swap.json", rows)
        for name in NAMES:
            for s in ("probe-swap", "chains"):
                el = [r for r in rows if r["set"] == s and r["models"][name]["eligible"]]
                best = {v: max((sum(r["models"][name]["arms"][f"{v}|swap|{al}"]["is_swap_answer"] for r in el), al) for al in ALPHAS) for v in variants}
                print(f"swap {s} {name}: eligible {len(el)} of {sum(r['set'] == s for r in rows)}; flips (best strength) {best}", flush=True)

    # ---------------------------------------------------------------- part 3: right/wrong twins
    if "twins" in parts:
        rows = []
        for it in json.loads((DATA / "math_stimuli_v1.json").read_text())["twins"][:a.limit]:
            idc, ide = enc(it["text_correct"]), enc(it["text_error"])
            diff = [i for i, (x, y) in enumerate(zip(idc, ide)) if x != y]
            assert len(idc) == len(ide) and len(diff) == 1, it["name"]
            d, right = diff[0], idc[diff[0]]
            row = {"name": it["name"], "delta": it["delta"], "op": it["op"], "n_tokens": len(idc), "diff_position": d,
                   "tokens_after": [strings[i] for i in idc[d + 1:]], "models": {}}
            for name in NAMES:
                e = {}
                for ver, ids in (("correct", idc), ("error", ide)):
                    acts, logits = run(model[name], recs[name], ids, dev)
                    lp_out = torch.log_softmax(logits[d - 1:], -1)
                    r = {"output_hold_lp": torch.logsumexp(lp_out[1:, hold], -1).tolist(),
                         "output_neutral_lp": torch.logsumexp(lp_out[1:, neutral], -1).tolist(), "output_top": [strings[int(x)] for x in logits[d:].argmax(-1)],
                         "output_right_lp_before": float(lp_out[0, right]), "lens": {}}
                    for v in variants:
                        hl, nl, rr = [], [], []
                        for l in layers:
                            lg = readout(name, v, l, acts[l][d:])
                            lp = torch.log_softmax(lg, -1)
                            hl.append(torch.logsumexp(lp[:, hold], -1).tolist())
                            nl.append(torch.logsumexp(lp[:, neutral], -1).tolist())
                            keep = lg.masked_fill(~mask, float("-inf"))
                            rr.append(((keep > keep[:, right:right + 1]).sum(-1) + 1).tolist())
                        r["lens"][v] = {"hold_lp": hl, "neutral_lp": nl, "right_rank": rr}          # [layer][position from the number on]
                    e[ver] = r
                row["models"][name] = e
            rows.append(row)
        M.dump(out / "twins.json", rows)
        for name in NAMES:
            gap = sum(r["models"][name]["error"]["output_hold_lp"][-1] - r["models"][name]["correct"]["output_hold_lp"][-1] for r in rows) / len(rows)
            print(f"twins {name}: {len(rows)} twins; output hold-on log-prob at the end, error minus correct: {gap:.3f}", flush=True)

    m.update(status="done", run_s=time.time() - t0, finished_utc=M.utc())
    if dev == "cuda":
        m["max_memory_gb"] = torch.cuda.max_memory_allocated() / 2 ** 30
    M.dump(out / "metrics.json", m)
    assert a.dry_run or checks["plumbing"]["pass"], ("plumbing check failed", checks["plumbing"])


if __name__ == "__main__":
    main()
