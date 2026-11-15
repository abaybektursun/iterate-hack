"""A no-reward route cell (specs/SPEC_engine_v10.md): one model, free prompt text after the problem, free opening text, free
decoding settings, k samples per problem. A vote or selection rule over the samples is computed from answers.jsonl afterwards.

    uv run tools/gpu.py submit l40s --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.free_cell
        --model base --opening-text 'Okay, let me think step by step.' --set hard328 --shard 0/2 --temperature 0.8 --top-p 0.95
        --samples 2 --seed 61000000 --commit COMMIT_SHA"   (COMMIT_SHA: the pushed commit's full sha, written in by hand)

  --model           base, rl (frozen4.json, as run_cell.py) or think_sft (wsp_delta_anatomy.MODELS); every model with the RL tokenizer
                    and the pair1 prompt, as run_cell.py runs them.
  --prompt-suffix   text added after the problem statement inside the prompt (before the pair1 closing line). Default none.
  --opening-text    text that continues the prompt as the start of the answer (prefilled, counted in the answer like the cue).
                    The prompt ends with 'after "Answer:"' and no separator: the cue is ' line!\n\nOkay' (frozen4.json
                    prefill_text), so start the text with a space or a newline. Default none.
  --temperature, --top-p, --min-p, --repetition-penalty   vLLM sampling (defaults 1.0, 1.0, 0.0, 1.0).
  --max-tokens      cap on generated tokens (default frozen4.json cap, 16,384).
  --samples, --seed sample s of problem i has seed + 10000 * s + i (run_cell.py's rule).
  --set             math500, hard328, hard72, hardmatch (run_cell.problems) or fresh2026 (run_fresh.problems).
  --n, --shard      the first n problems; then problems k, k+N, ... of them (shard k/N).
  --dry-run         run_cell's stand-in engine (canned answers): builds and checks every prompt, no vLLM, no weights, no GPU.

Imports the generation and grading code (rln4_gen engine and row record, rln4_lib grade_v3, n13_score prompt ids); copies none.
Writes to --out (default $OUT_DIR): answers.jsonl (one row per sample, appended with fsync) and metrics.json. Fail loud.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time
from importlib import metadata

from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.jobs import run_cell as RC
from studies.rlneurons.jobs import run_fresh as RF
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

SETS = ("math500", "hard328", "hard72", "hardmatch", "fresh2026")


def model_repo(name, fz):
    """(repo, revision) of a model choice."""
    if name == "think_sft":
        from studies.rlneurons.jobs.wsp_delta_anatomy import MODELS   # imports torch: only for this model
        return MODELS["think_sft"]
    repo, _, rev = fz["models"][RC.MODELS[name]]
    return repo, rev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=("base", "rl", "think_sft"))
    ap.add_argument("--prompt-suffix", default="")
    ap.add_argument("--opening-text", default="")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--top-p", type=float, default=1.0)
    ap.add_argument("--min-p", type=float, default=0.0)
    ap.add_argument("--repetition-penalty", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=None, help="default: frozen4.json cap (16,384)")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--set", required=True, choices=SETS)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--shard", default="0/1", help="k/N: problems k, k+N, ... of the set (after --n)")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    assert 0.0 <= a.min_p < 1.0 and a.repetition_penalty > 0 and 1 <= a.samples < 10, "min-p in [0, 1), penalty > 0, 1 to 9 samples"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows_path, mpath = out / "answers.jsonl", out / "metrics.json"
    assert not rows_path.exists(), f"{rows_path} exists: one fresh directory per run"

    fz = json.loads((RC.D4 / "frozen4.json").read_text())
    cap = a.max_tokens or fz["cap"]
    probs = RF.problems(a.set, fz)[: a.n]
    k, n_shards = (int(x) for x in a.shard.split("/"))
    assert 0 <= k < n_shards, f"--shard {a.shard}: k must be in 0..N-1"
    probs = probs[k::n_shards]
    assert max(int(p["index"]) for p in probs) < 10000, "seeds of two requests would collide"
    sampling = {"temperature": a.temperature, "top_p": a.top_p, "repetition_penalty": a.repetition_penalty, **({"min_p": a.min_p} if a.min_p else {})}
    versions = {p: metadata.version(p) for p in RC.PINS if p != "vllm" or not a.dry_run}
    if not a.dry_run:
        assert versions == RC.PINS, f"package versions {versions} differ from the study's {RC.PINS}: run setup_vllm.sh first"
    repo, rev = model_repo(a.model, fz)
    m = {"status": "starting", "config": {**vars(a), "max_tokens": cap, "out": str(out), "model_repo": repo, "model_revision": rev,
                                         "tokenizer": fz["tokenizer"], "template": fz["template"], "sampling": sampling,
                                         "seed_rule": "seed + 10000 * sample + index", "n_problems": len(probs)},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "versions": versions, "started_utc": J.utc()}

    def write():
        m["updated_utc"] = J.utc()
        G.dump(mpath, m)

    write()
    from huggingface_hub import snapshot_download
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(tok_dir)
    texts = [p["problem"] + a.prompt_suffix for p in probs]
    bad = [p["index"] for p, t in zip(probs, texts) if S.render_text(tok, t) != S.TEMPLATE[fz["template"]].format(problem=t)]
    assert not bad, ("G-TEMPLATE", bad[:5])
    pids = [S.render_ids(tok, t) for t in texts]
    pre = [int(i) for i in tok(a.opening_text, add_special_tokens=False)["input_ids"]] if a.opening_text else []
    assert not a.opening_text or tok.decode(pre) == a.opening_text, "the opening text does not round-trip through the tokenizer"
    assert max(len(p) for p in pids) + len(pre) <= 2048, "a prompt is longer than 2,048 tokens"
    m["config"].update(prefix_ids=pre, example_prompt=tok.decode(pids[0] + pre, skip_special_tokens=False))

    cell = f"free_{a.model}_{a.set}_T{a.temperature:g}_p{a.top_p:g}_mp{a.min_p:g}_rp{a.repetition_penalty:g}"
    reqs = [{"rid": f"{cell}|{p['index']}|{s}", "cell": cell, "bench": a.set, "idx": int(p["index"]), "sample": s,
             "uid": p["unique_id"], "ids": ids + pre, "n_prompt": len(ids), "prefix_ids": pre,
             "prefix_kind": "opening" if pre else "none", "seed": a.seed + 10000 * s + int(p["index"]), "sampling": sampling,
             "max_tokens": cap, "gold": p["answer"]} for s in range(a.samples) for p, ids in zip(probs, pids)]
    live = {r["rid"]: r for r in reqs}
    t_load = time.time()
    if a.dry_run:
        engine, model_dir = RC.Canned(tok, live), None
    else:
        model_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
        os.environ.update(G.ENGINE_ENV)
        engine = J.VllmEngine(model_dir, tok_dir, 2048 + cap)
    m["engine"] = {**engine.info, "load_s": time.time() - t_load, "model_dir": model_dir, "tok_dir": tok_dir}
    m["status"] = "running"
    write()
    for r in reqs:
        engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"])
    c = {"n": 0, "correct_v3": 0, "cap_hits": 0, "generated_tokens": 0}
    with open(rows_path, "a") as f:
        while engine.has_unfinished():
            for rid, out_ids, lps, fr in engine.step():
                req = live.pop(rid)
                rec = J.record(tok, req, out_ids, lps, fr)
                rec.update(R.grade_v3(req["gold"], rec["text"]))
                rec.update(prompt=tok.decode(req["ids"][: req["n_prompt"]], skip_special_tokens=False), model=a.model)
                f.write(json.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
                c["n"] += 1
                c["correct_v3"] += rec["score_v3"]
                c["cap_hits"] += int(rec["cap_hit"])
                c["generated_tokens"] += rec["n_new"]
                m["counts"] = {**c, "n_planned": len(reqs), "mean_generated_tokens": c["generated_tokens"] / c["n"],
                               "tokens_per_problem": c["generated_tokens"] * a.samples / c["n"]}
                write()
    assert not live, f"{len(live)} requests did not finish"
    m["memory"] = engine.memory()
    m.update(status="done", wall_s=time.time() - t0)
    write()
    print(json.dumps({k: m[k] for k in ("status", "counts", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
