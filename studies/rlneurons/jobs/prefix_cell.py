"""Generation test from the prefix before each located wrong step (specs/SPEC_prefixtest.md).

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.prefix_cell --rows /runs/<job>/answers.jsonl --labels studies/rlneurons/results/anatomy/judge-01/labels.json
        --model base --alpha 1 --shard 0/6 --seed 110000000 [--n-items 5 --k 2]

  --model  base or rl (frozen4.json): the model that continues.
  --alpha  0 = plain sampling; a > 0 = sample from softmax((1 + a) logits - a logits_noprob), where logits_noprob comes from the
           same model reading the template with an empty problem, the cue and the same answer text.
  --shard  i/N: the requests with (request number mod N) == i.

Each located item (as score_tokens --labels locates it) gives --k requests: prompt + cue + the stored answer's tokens before the
wrong step, then up to --cap new tokens at T 1.0 / top-p 1.0. --alpha 0: the study's vLLM engine (rln4_gen.VllmEngine, all
requests at once; --batch unused). --alpha > 0: transformers with a key-value cache, batches of --batch requests sorted by
length, finished requests leave the batch. Writes answers.jsonl (rln4_gen.record fields + grader v3 +
item, label, k, arm) and metrics.json to $OUT_DIR. Fail loud.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time

import torch

from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.jobs.score_tokens import span
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--model", required=True, choices=("base", "rl"))
    ap.add_argument("--alpha", type=float, required=True)
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--cap", type=int, default=6000)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--start", type=int, default=0, help="skip the first n requests of the shard (the rest of a run that ended early)")
    ap.add_argument("--n-items", type=int, default=None, help="the first n located items (smoke runs)")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows_path = out / "answers.jsonl"
    assert not rows_path.exists()
    si, sn = (int(x) for x in a.shard.split("/"))
    arm = f"{a.model}_a{a.alpha:g}"
    fz = json.loads((STUDY / "data" / "rln4" / "frozen4.json").read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    probs = {int(p["index"]): p for p in json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())}
    pre, pre_text = fz["prefill_ids"], fz["prefill_text"]
    judged = {(x["problem_index"], x["sample"]): x["passA"] for x in json.loads(pathlib.Path(a.labels).read_text()) if x["kind"] == "base"}
    stored = sorted((r for r in map(json.loads, open(a.rows)) if r["attempt"] == 0 and (r["problem_index"], r["sample"]) in judged),
                    key=lambda r: (r["problem_index"], r["sample"]))
    assert len(stored) == len(judged)
    items = []
    for r in stored:
        text = r["text"][len(pre_text):]
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
        w = span(judged[(r["problem_index"], r["sample"])], text, enc["offset_mapping"])
        if w["found"]:
            p = probs[r["problem_index"]]
            items.append({"item": f"{r['problem_index']}:{r['sample']}", "label": w["label"], "problem": p, "prefix": [int(t) for t in enc["input_ids"][: w["tok_start"]]]})
    items = items[: a.n_items]
    reqs = []
    for i, it in enumerate(items):
        for k in range(a.k):
            p = it["problem"]
            ids = S.render_ids(tok, p["problem"])
            reqs.append({"rid": f"{arm}|{it['item']}|{k}", "cell": f"prefix_{arm}", "bench": "math500", "idx": int(p["index"]), "sample": k, "uid": p["unique_id"],
                         "ids": ids + pre + it["prefix"], "ids0": S.render_ids(tok, "") + pre + it["prefix"], "n_prompt": len(ids), "prefix_ids": pre + it["prefix"],
                         "prefix_kind": "before_wrong_step", "seed": a.seed + 100 * i + k, "sampling": {"temperature": 1.0, "top_p": 1.0, "repetition_penalty": 1.0},
                         "max_tokens": a.cap, "gold": p["answer"], "item": it["item"], "label": it["label"]})
    reqs = sorted([r for j, r in enumerate(reqs) if j % sn == si], key=lambda r: len(r["ids"]))[a.start:]

    repo, _, rev = fz["models"]["base" if a.model == "base" else "s2800"]
    model_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
    m = {"status": "running", "config": {**vars(a), "arm": arm, "model_repo": repo, "model_revision": rev}, "items": len(items), "requests": len(reqs),
         "job_id": os.environ.get("JOB_ID"), "counts": {"n": 0, "correct_v3": 0, "cap_hits": 0, "generated_tokens": 0}}

    def emit(f, req, out_ids, lps, finish_reason):
        rec = J.record(tok, req, out_ids, lps, finish_reason)
        rec.update(R.grade_v3(req["gold"], rec["text"]))
        rec.update(item=req["item"], label=req["label"], k=req["sample"], arm=arm, n_prefix_tokens=len(req["prefix_ids"]) - len(pre))
        f.write(json.dumps(rec) + "\n")
        f.flush()
        c = m["counts"]
        c["n"] += 1
        c["correct_v3"] += rec["score_v3"]
        c["cap_hits"] += int(rec["cap_hit"])
        c["generated_tokens"] += rec["n_new"]
        m["seconds"] = round(time.time() - t0, 1)

    if not a.alpha:
        os.environ.update(G.ENGINE_ENV)
        engine = J.VllmEngine(model_dir, tok_dir, max(len(r["ids"]) for r in reqs) + a.cap)
        t0 = time.time()
        live = {r["rid"]: r for r in reqs}
        for r in reqs:
            engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"])
        with open(rows_path, "a") as f:
            while engine.has_unfinished():
                for rid, out_ids, lps, fr in engine.step():
                    emit(f, live.pop(rid), out_ids, lps, fr)
                    (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
        assert m["counts"]["n"] == len(reqs)
        m["status"] = "done"
        (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
        return
    model = AutoModelForCausalLM.from_pretrained(model_dir, dtype=torch.bfloat16).cuda().eval()
    t0 = time.time()

    def start(seqs):
        """Left-padded first pass: next-token logits, cache, attention mask."""
        L = max(len(s) for s in seqs)
        ids = torch.tensor([[S.STOP_ID] * (L - len(s)) + s for s in seqs], device="cuda")
        mask = torch.tensor([[0] * (L - len(s)) + [1] * len(s) for s in seqs], device="cuda")
        o = model(input_ids=ids, attention_mask=mask, use_cache=True)
        return o.logits[:, -1].float(), o.past_key_values, mask

    def step(tokens, cache, mask):
        mask = torch.cat([mask, torch.ones_like(mask[:, :1])], dim=1)
        o = model(input_ids=tokens[:, None], attention_mask=mask, past_key_values=cache, use_cache=True)
        return o.logits[:, -1].float(), o.past_key_values, mask

    with torch.no_grad(), open(rows_path, "a") as f:
        for b0 in range(0, len(reqs), a.batch):
            batch = reqs[b0: b0 + a.batch]
            gen = torch.Generator(device="cuda").manual_seed(batch[0]["seed"])
            lg, cache, mask = start([r["ids"] for r in batch])
            if a.alpha:
                lg0, cache0, mask0 = start([r["ids0"] for r in batch])
            live = list(range(len(batch)))
            outs, lps = [[] for _ in batch], [[] for _ in batch]
            while live:
                lsm = torch.log_softmax((1 + a.alpha) * lg - a.alpha * lg0 if a.alpha else lg, dim=-1)
                nxt = torch.multinomial(lsm.exp(), 1, generator=gen)[:, 0]
                lp = lsm.gather(1, nxt[:, None])[:, 0]
                keep = []
                for j, bi in enumerate(live):
                    outs[bi].append(int(nxt[j]))
                    lps[bi].append(float(lp[j]))
                    if int(nxt[j]) == S.STOP_ID or len(outs[bi]) == a.cap:
                        emit(f, batch[bi], outs[bi], lps[bi], "stop" if int(nxt[j]) == S.STOP_ID else "length")
                    else:
                        keep.append(j)
                if len(keep) < len(live):
                    sel = torch.tensor(keep, device="cuda", dtype=torch.long)
                    live = [live[j] for j in keep]
                    if not live:
                        break
                    nxt, mask = nxt[sel], mask[sel]
                    cache.batch_select_indices(sel)
                    if a.alpha:
                        mask0 = mask0[sel]
                        cache0.batch_select_indices(sel)
                lg, cache, mask = step(nxt, cache, mask)
                if a.alpha:
                    lg0, cache0, mask0 = step(nxt, cache0, mask0)
            del cache
            if a.alpha:
                del cache0
            torch.cuda.empty_cache()
            m["seconds"] = round(time.time() - t0, 1)
            (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
            print(b0, m["counts"], m["seconds"], flush=True)
    assert m["counts"]["n"] == len(reqs)
    m["status"] = "done"
    (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")


if __name__ == "__main__":
    main()
