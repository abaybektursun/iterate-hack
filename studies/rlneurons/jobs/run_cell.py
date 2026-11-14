"""One cell of the rlneurons study (one model, one prompt arm, one problem set, one sampling setting, one sample per problem) on
the team runner. Reuses rln4_gen's vLLM engine and row record (prompt, extraction, graders v1 and v2, loop detectors) and adds
grader v3 (rln4_lib.grade_v3). Inputs come from the repository's data files; models and tokenizer at the revisions in
data/rln4/frozen4.json.

    uv run tools/gpu.py submit h100 --hours 1 -- 'bash studies/rlneurons/jobs/setup_vllm.sh && python -m studies.rlneurons.jobs.run_cell
        --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 10'

  --model   base = allenai/Olmo-3-1025-7B, rl = allenai/Olmo-3.1-7B-RL-Zero-Math (step 2,800); both with the RL tokenizer.
  --prompt  plain = the pair1 prompt; cue = the pair1 prompt followed by the opening cue (frozen4.json prefill_ids).
  --set     math500 = data/rln4/math500.json (500); hard328 = the 328 problems of data/rln3/hard.json with overlap flag "none".
  --seed    problem i is sampled with seed + i (i = the problem's index in its file), the study's convention.
  --n       the first n problems of the set (smoke runs); default all.
  --dry-run a stand-in engine serves canned completions (right, wrong, cap hit in turn): no vLLM, no weights, no GPU.

Writes to --out (default $OUT_DIR): answers.jsonl, one row per finished problem, appended with flush + fsync (the real prompt,
the completion, finish reason, generated tokens, extracted answers and grades v1, v2, v3), and metrics.json, rewritten after
every row. A killed job keeps every finished row. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import time
from importlib import metadata

from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
D3, D4 = STUDY / "data" / "rln3", STUDY / "data" / "rln4"
MODELS = {"base": "base", "rl": "s2800"}                      # keys of frozen4.json "models"
PINS = {"vllm": "0.32.0", "math-verify": "0.9.0", **J.TOKENIZER_PINS}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def problems(name, fz):
    if name == "math500":
        assert sha(D4 / "math500.json") == fz["sha256"]["math500.json"], "math500.json differs from frozen4.json"
        return json.loads((D4 / "math500.json").read_text())
    f3 = json.loads((D3 / "frozen.json").read_text())
    assert sha(D3 / "hard.json") == f3["sha256"]["hard"], "hard.json differs from data/rln3/frozen.json"
    hard = json.loads((D3 / "hard.json").read_text())
    flags = json.loads((STUDY / "results" / "rln3" / "rln3_overlap.json").read_text())["sets"]["hard"]["flags"]
    clean = sorted(int(i) for i, f in flags.items() if f["flag"] == "none")
    assert len(clean) == 328 and all(int(hard[i]["index"]) == i for i in clean), "the clean harder set is not 328 problems"
    return [hard[i] for i in clean]


def commit():
    if os.environ.get("JOB_ID"):            # the runner extracts a git archive (no .git); tools/gpu.py records the commit per job
        import sys
        sys.path.append("/pkg")             # Modal's client in the container; the runner sets the job's PYTHONPATH to /repo only
        import modal
        return modal.Dict.from_name("iterate-jobs")[f"job:{os.environ['JOB_ID']}"]["sha"]
    return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


class Canned:
    """Stand-in for J.VllmEngine (--dry-run). Request k in submission order gets: k % 3 == 0 a right answer, 1 a wrong one, 2 a cap
    hit (max_tokens ids, no stop id). Finishes two requests per step."""
    info = {"vllm": None, "dry_run": True}

    def __init__(self, tok, golds):
        self.tok, self.golds, self.queue, self.k = tok, golds, [], 0

    def add(self, rid, ids, sampling, seed, max_tokens):
        self.queue.append((rid, self.k % 3, max_tokens))
        self.k += 1

    def step(self):
        done, self.queue = self.queue[:2], self.queue[2:]
        res = []
        for rid, kind, mt in done:
            gold = self.golds[rid]
            if kind == 2:
                ids = (self.tok(" so so", add_special_tokens=False)["input_ids"] * mt)[:mt]
                res.append((rid, ids, [-1.0] * mt, "length"))
                continue
            ans = gold if kind == 0 else "-123456789"
            ids = self.tok(f" I work it out step by step.\n\nAnswer: ${ans}$", add_special_tokens=False)["input_ids"] + [S.STOP_ID]
            res.append((rid, ids, [-0.5] * len(ids), "stop"))
        return res

    def has_unfinished(self):
        return bool(self.queue)

    def memory(self):
        return {"gpu": "none (dry run)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--prompt", required=True, choices=("plain", "cue"))
    ap.add_argument("--set", required=True, choices=("math500", "hard328"))
    ap.add_argument("--temperature", type=float, required=True)
    ap.add_argument("--top-p", type=float, required=True)
    ap.add_argument("--max-tokens", type=int, default=None, help="default: frozen4.json cap (16,384)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows_path, mpath = out / "answers.jsonl", out / "metrics.json"
    assert not rows_path.exists(), f"{rows_path} exists: one fresh directory per run"

    fz = json.loads((D4 / "frozen4.json").read_text())
    cap = a.max_tokens or fz["cap"]
    probs = problems(a.set, fz)[: a.n]
    pre = fz["prefill_ids"] if a.prompt == "cue" else []
    sampling = {"temperature": a.temperature, "top_p": a.top_p, "repetition_penalty": 1.0}
    versions = {k: metadata.version(k) for k in PINS if k != "vllm" or not a.dry_run}
    if not a.dry_run:
        assert versions == PINS, f"package versions {versions} differ from the study's {PINS}: run setup_vllm.sh first"
    repo, _, rev = fz["models"][MODELS[a.model]]
    m = {"status": "starting", "config": {**vars(a), "max_tokens": cap, "out": str(out), "model_repo": repo, "model_revision": rev,
                                         "tokenizer": fz["tokenizer"], "prefix_ids": pre, "sampling": sampling, "seed_rule": "seed + index",
                                         "n_problems": len(probs)},
         "commit": commit(), "job_id": os.environ.get("JOB_ID"), "versions": versions, "started_utc": J.utc()}

    def write():
        m["updated_utc"] = J.utc()
        G.dump(mpath, m)

    write()
    from huggingface_hub import snapshot_download
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(tok_dir)
    assert tok.decode(fz["prefill_ids"]) == fz["prefill_text"]
    bad = [p["index"] for p in probs if S.render_text(tok, p["problem"]) != S.TEMPLATE[fz["template"]].format(problem=p["problem"])]
    assert not bad, ("G-TEMPLATE", bad[:5])
    pids = [S.render_ids(tok, p["problem"]) for p in probs]
    if a.set == "math500":
        n13 = json.loads((D4 / "prompt_ids.json").read_text())
        assert n13["pair"] == "pair1" and pids == n13["ids"][: len(pids)], "G-TEMPLATE: MATH-500 prompt ids differ from n13's"
    max_len = 2048 + cap
    assert max(len(p) for p in pids) + len(pre) <= 2048, "a prompt is longer than 2,048 tokens"

    cell = f"{a.model}_{a.prompt}_{a.set}_T{a.temperature:g}_p{a.top_p:g}"
    reqs = [{"rid": f"{cell}|{p['index']}|0", "cell": cell, "bench": a.set, "idx": int(p["index"]), "sample": 0, "uid": p["unique_id"],
             "ids": ids + pre, "n_prompt": len(ids), "prefix_ids": pre, "prefix_kind": "opening" if pre else "none",
             "seed": a.seed + int(p["index"]), "sampling": sampling, "max_tokens": cap, "gold": p["answer"]} for p, ids in zip(probs, pids)]

    t_load = time.time()
    if a.dry_run:
        engine = Canned(tok, {r["rid"]: r["gold"] for r in reqs})
        model_dir = None
    else:
        model_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
        os.environ.update(G.ENGINE_ENV)         # what n13_gen.child_env gives the study's child; vLLM's engine process inherits it
        engine = J.VllmEngine(model_dir, tok_dir, max_len)
    m["engine"] = {**engine.info, "load_s": time.time() - t_load, "model_dir": model_dir, "tok_dir": tok_dir}
    m["status"] = "running"
    write()

    live = {r["rid"]: r for r in reqs}
    for r in reqs:
        engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"])
    t_gen = time.time()
    c = {"n": 0, "correct_v3": 0, "correct_v1": 0, "cap_hits": 0, "loop_A": 0, "generated_tokens": 0}
    with open(rows_path, "a") as f:
        while engine.has_unfinished():
            for rid, out_ids, lps, fr in engine.step():
                req = live.pop(rid)
                rec = J.record(tok, req, out_ids, lps, fr)
                rec.update(R.grade_v3(req["gold"], rec["text"]))
                rec.update(prompt=tok.decode(req["ids"][: req["n_prompt"]], skip_special_tokens=False), model=a.model, prompt_arm=a.prompt)
                f.write(json.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
                c["n"] += 1
                c["correct_v3"] += rec["score_v3"]
                c["correct_v1"] += rec["score"]
                c["cap_hits"] += int(rec["cap_hit"])
                c["loop_A"] += int(rec["loop_A"])
                c["generated_tokens"] += rec["n_new"]
                sec = time.time() - t_gen
                m["counts"] = {**c, "n_planned": len(reqs), "mean_generated_tokens": c["generated_tokens"] / c["n"],
                               "generation_s": sec, "tokens_per_s": c["generated_tokens"] / max(sec, 1e-9)}
                write()
    assert not live, f"{len(live)} requests did not finish"
    m["memory"] = engine.memory()
    m["status"] = "done"
    m["wall_s"] = time.time() - t0
    write()
    print(json.dumps({k: m[k] for k in ("status", "counts", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
