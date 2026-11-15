"""One cell of the rlneurons study (one model, one prompt arm, one problem set, one sampling setting; one sample per problem, or
--samples of them, each with up to --restarts restarts on a cap hit) on the team runner. Reuses rln4_gen's vLLM engine and row record (prompt, extraction, graders v1 and v2, loop detectors) and adds
grader v3 (rln4_lib.grade_v3). Inputs come from the repository's data files; models and tokenizer at the revisions in
data/rln4/frozen4.json.

    uv run tools/gpu.py submit h100 --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell
        --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 10 --commit $(git rev-parse HEAD)"

  Double quotes, so that $(git rev-parse HEAD) expands on the laptop to the commit that gpu.py submits (the job's tree has no .git).

  --model   base = allenai/Olmo-3-1025-7B, rl = allenai/Olmo-3.1-7B-RL-Zero-Math (step 2,800); both with the RL tokenizer.
  --model-path, --model-label  instead of --model: a local weights directory (jobs/merge_weights.py writes one) and its name in the
            rows and metrics; the RL tokenizer as for --model.
  --prompt  plain = the pair1 prompt; cue = the pair1 prompt followed by the opening cue (frozen4.json prefill_ids).
  --set     math500 = data/rln4/math500.json (500); hard328 = the 328 problems of data/rln3/hard.json with overlap flag "none".
            hard72 = the other 72 of hard.json (in the RL training prompts: flag exact or near); hardmatch = 130 of the 328
            (every AIME and AMC 23 problem and every sixth OlympiadBench problem), the unseen comparison set of specs/SPEC_seen.md.
  --min-p   vLLM min_p (default 0.0 = off): drop tokens whose probability, after temperature, is below min_p times the top token's.
            The cell name gains _mp<min_p> when it is not 0. specs/SPEC_minp.md.
  --seed    problem i is sampled with seed + i (i = the problem's index in its file), the study's convention.
  --samples k samples per problem (default 1); sample s of problem i has seed + 10000 * s + i (the RLN-3 rule).
  --restarts an answer that hits the cap is sampled again, up to this many times (default 0), in the same job; attempt a of sample
            s has seed + 10000 * s + 1000 * a + i. Each attempt is its own row (fields sample, attempt). specs/SPEC_day1_3.md;
            analysis/day1_vote.py makes the vote and restart rows from the rows. metrics.json counts are over all rows (attempts).
  --shots   a JSON file with a "text" field (data/shots1/, built by prep/shots1_build.py): solved examples, each the prompt + the
            answer + "\n\n", put in front of every prompt. Generation then also stops at the string SHOT_STOP (the start of a
            further example); the answer is cut there and scored as a finished answer. The examples' own problems are in the set:
            leave them out of any count (analysis does it).
  --n       the first n problems of the set (smoke runs); default all.
  --shard   k/N: only problems k, k+N, k+2N, ... of the set (after --n), so one cell runs as N jobs at once. A request's seed
            depends on its problem index, not on its place in the job, so the N jobs have the requests of the one job;
            analysis/shard_join.py joins their folders into the folder the one job would have written.
  --resume  a run folder of the same cell (same settings in its metrics.json) whose job was cut: its rows are copied into --out
            and only the requests with no row are sent (with --restarts, the next attempt of a cap hit that has none).
  --dry-run a stand-in engine serves canned completions (right, wrong, cap hit in turn): no vLLM, no weights, no GPU.

Writes to --out (default $OUT_DIR): answers.jsonl, one row per finished problem, appended with flush + fsync (the real prompt,
the completion, finish reason, generated tokens, extracted answers and grades v1, v2, v3), and metrics.json, rewritten after
every row. A killed job keeps every finished row. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import re
import time
from importlib import metadata

from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
D3, D4 = STUDY / "data" / "rln3", STUDY / "data" / "rln4"
MODELS = {"base": "base", "rl": "s2800"}                      # keys of frozen4.json "models"
SHOT_STOP = "\n\nSolve the following problem step by step"     # with --shots: the model starts a further example
LOG_1E2, LOG_1E3 = math.log(1e-2), math.log(1e-3)
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
    if name == "hard328":
        return [hard[i] for i in clean]
    seen = sorted(set(range(len(hard))) - set(clean))
    assert len(seen) == 72 and all(int(hard[i]["index"]) == i for i in seen), "the seen harder set is not 72 problems"
    if name == "hard72":
        return [hard[i] for i in seen]
    oly = [i for i in clean if hard[i]["source"] == "olympiadbench"]            # hardmatch (specs/SPEC_seen.md)
    match = sorted([i for i in clean if hard[i]["source"].startswith(("aime", "amc"))] + oly[::6])
    assert name == "hardmatch" and len(match) == 130, (name, len(match))
    return [hard[i] for i in match]


def cut_at_shot_stop(tok, out_ids, lps):
    """An answer that stopped at SHOT_STOP: drop the tokens after it and end the answer with the stop id."""
    full = tok.decode(out_ids, skip_special_tokens=False)
    pos = full.rfind(SHOT_STOP) if SHOT_STOP in full else len(full)
    k = len(out_ids)
    while k > 0 and len(tok.decode(out_ids[: k - 1], skip_special_tokens=False)) >= pos:
        k -= 1
    return list(out_ids[:k]) + [S.STOP_ID], list(lps[:k]) + [0.0]


class Canned:
    """Stand-in for J.VllmEngine (--dry-run). Request k in submission order gets: k % 3 == 0 a right answer, 1 a wrong one, 2 a cap
    hit (max_tokens ids, no stop id). Finishes two requests per step. live: the unfinished requests by rid (for the gold)."""
    info = {"vllm": None, "dry_run": True}

    def __init__(self, tok, live):
        self.tok, self.live, self.queue, self.k = tok, live, [], 0

    def add(self, rid, ids, sampling, seed, max_tokens):
        self.queue.append((rid, self.k % 3, max_tokens))
        self.k += 1

    def step(self):
        done, self.queue = self.queue[:2], self.queue[2:]
        res = []
        for rid, kind, mt in done:
            gold = self.live[rid]["gold"]
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
    ap.add_argument("--model", choices=sorted(MODELS))
    ap.add_argument("--model-path")
    ap.add_argument("--model-label")
    ap.add_argument("--prompt", required=True, choices=("plain", "cue"))
    ap.add_argument("--set", required=True, choices=("math500", "hard328", "hard72", "hardmatch"))
    ap.add_argument("--temperature", type=float, required=True)
    ap.add_argument("--top-p", type=float, required=True)
    ap.add_argument("--min-p", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=None, help="default: frozen4.json cap (16,384)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--shots")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--shard", help="k/N: problems k, k+N, k+2N, ... of the set (after --n). Seeds depend on the problem index only, "
                                    "so the N jobs give the rows of one job; join them with analysis/shard_join.py")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--restarts", type=int, default=0)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--resume", help="run folder of the same cell cut before its end: keep its rows, send the rest")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    assert (a.model is None) == bool(a.model_path) == bool(a.model_label), "give --model, or --model-path with --model-label"
    model = a.model or a.model_label
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows_path, mpath = out / "answers.jsonl", out / "metrics.json"
    assert not rows_path.exists(), f"{rows_path} exists: one fresh directory per run"

    fz = json.loads((D4 / "frozen4.json").read_text())
    cap = a.max_tokens or fz["cap"]
    probs = problems(a.set, fz)[: a.n]
    pre = fz["prefill_ids"] if a.prompt == "cue" else []
    assert 0.0 <= a.min_p < 1.0, f"--min-p {a.min_p} outside [0, 1)"
    sampling = {"temperature": a.temperature, "top_p": a.top_p, "repetition_penalty": 1.0, **({"min_p": a.min_p} if a.min_p else {})}
    versions = {k: metadata.version(k) for k in PINS if k != "vllm" or not a.dry_run}
    if not a.dry_run:
        assert versions == PINS, f"package versions {versions} differ from the study's {PINS}: run setup_vllm.sh first"
    repo, _, rev = fz["models"][MODELS[a.model]] if a.model else (None, None, None)
    m = {"status": "starting", "config": {**vars(a), "max_tokens": cap, "out": str(out), "model_repo": repo, "model_revision": rev,
                                         "tokenizer": fz["tokenizer"], "prefix_ids": pre, "sampling": sampling, "seed_rule": "seed + 10000 * sample + 1000 * attempt + index",
                                         "n_problems": len(probs)},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "versions": versions, "started_utc": J.utc()}

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
    if a.shard:
        k, n_shards = (int(x) for x in a.shard.split("/"))
        assert 0 <= k < n_shards, f"--shard {a.shard}: k must be in 0..N-1"
        probs, pids = probs[k::n_shards], pids[k::n_shards]
        m["config"]["n_problems"] = len(probs)
    shots = json.loads(pathlib.Path(a.shots).read_text()) if a.shots else None
    shot_ids = [int(i) for i in tok(shots["text"], add_special_tokens=False)["input_ids"]] if shots else []
    assert not shots or (shots["text"].endswith("\n\n") and SHOT_STOP.startswith("\n\n" + S.TEMPLATE[fz["template"]][:20]))
    m["config"].update(shots_arm=shots and shots["arm"], shots_sha256=a.shots and sha(pathlib.Path(a.shots)), shots_tokens=len(shot_ids))
    pids = [shot_ids + p for p in pids]
    max_len = 2048 + len(shot_ids) + cap
    assert max(len(p) for p in pids) + len(pre) <= 2048 + len(shot_ids), "a prompt is longer than 2,048 tokens"

    cell = (f"{model}_{a.prompt}{'_shots-' + shots['arm'] if shots else ''}_{a.set}_T{a.temperature:g}_p{a.top_p:g}"
            + (f"_mp{a.min_p:g}" if a.min_p else ""))
    assert 1 <= a.samples and 0 <= a.restarts < 10 and max(int(p["index"]) for p in probs) < 1000, "seeds of two requests would collide"
    reqs = [{"rid": f"{cell}|{p['index']}|{s}|0", "cell": cell, "bench": a.set, "idx": int(p["index"]), "sample": s, "attempt": 0,
             "uid": p["unique_id"], "ids": ids + pre, "n_prompt": len(ids), "prefix_ids": pre, "prefix_kind": "opening" if pre else "none",
             "seed": a.seed + 10000 * s + int(p["index"]), "sampling": sampling, "max_tokens": cap, "gold": p["answer"]}
            for s in range(a.samples) for p, ids in zip(probs, pids)]

    def next_attempt(r):
        return {**r, "attempt": r["attempt"] + 1, "seed": r["seed"] + 1000, "rid": f"{cell}|{r['idx']}|{r['sample']}|{r['attempt'] + 1}"}

    old, todo = [], reqs
    if a.resume:
        rdir = pathlib.Path(a.resume)
        om = json.loads((rdir / "metrics.json").read_text())
        oc = om["config"]
        same = ("model", "model_path", "model_label", "prompt", "set", "temperature", "top_p", "min_p", "max_tokens", "seed", "shots",
                "n", "shard", "samples", "restarts")
        diff = {k: (oc[k], m["config"][k]) for k in same if oc[k] != m["config"][k]}
        assert not diff, f"--resume {rdir} is another cell: {diff}"
        old = [json.loads(line) for line in (rdir / "answers.jsonl").read_text().splitlines()]
        done = {(r["problem_index"], r["sample"], r["attempt"]): r for r in old}
        assert len(done) == len(old), f"{rdir}: two rows of one request"
        todo, used = [], 0
        for r in reqs:                      # walk each request's attempts: the first one with no row is sent
            while (row := done.get((r["idx"], r["sample"], r["attempt"]))) is not None:
                assert row["seed"] == r["seed"], (rdir, r["rid"], row["seed"], r["seed"])
                used += 1
                if not (row["cap_hit"] and r["attempt"] < a.restarts):
                    break
                r = next_attempt(r)
            else:
                todo.append(r)
        assert used == len(old), f"{rdir}: {len(old) - used} rows match no request of this cell"
        m["config"].update(resumed_rows=len(old), resumed_from_job=om["job_id"])
    live = {r["rid"]: r for r in todo}

    t_load = time.time()
    if a.dry_run:
        engine = Canned(tok, live)
        model_dir = None
    else:
        model_dir = a.model_path or snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
        os.environ.update(G.ENGINE_ENV)         # what n13_gen.child_env gives the study's child; vLLM's engine process inherits it
        engine = J.VllmEngine(model_dir, tok_dir, max_len)
    m["engine"] = {**engine.info, "load_s": time.time() - t_load, "model_dir": model_dir, "tok_dir": tok_dir}
    m["status"] = "running"
    write()

    def add(r):
        if shots and not a.dry_run:             # engine.add refuses stop strings (the study's neutral-sampling check), so add directly
            engine.engine.add_request(r["rid"], {"prompt_token_ids": r["ids"]}, engine.SP(
                **{**J.BASE_SAMPLING, **r["sampling"]}, max_tokens=r["max_tokens"], seed=r["seed"], stop=[SHOT_STOP]))
        else:
            engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"])

    for r in todo:
        add(r)
    t_gen = time.time()
    c = {"n": 0, "tok_p_lt_1e2": 0, "tok_p_lt_1e3": 0, "correct_v3": 0, "correct_v1": 0, "cap_hits": 0, "loop_A": 0, "generated_tokens": 0,
         "restarts": sum(r["attempt"] > 0 for r in old + todo)}
    old_tokens = sum(r["n_new"] for r in old)

    def keep(f, rec):
        f.write(json.dumps(rec) + "\n")
        f.flush()
        os.fsync(f.fileno())
        c["n"] += 1
        c["correct_v3"] += rec["score_v3"]
        c["correct_v1"] += rec["score"]
        c["cap_hits"] += int(rec["cap_hit"])
        c["loop_A"] += int(rec["loop_A"])
        c["generated_tokens"] += rec["n_new"]
        c["tok_p_lt_1e2"] += rec["n_tok_p_lt_1e2"]
        c["tok_p_lt_1e3"] += rec["n_tok_p_lt_1e3"]
        sec = time.time() - t_gen
        m["counts"] = {**c, "n_planned": len(reqs) + c["restarts"], "mean_generated_tokens": c["generated_tokens"] / c["n"],
                       "generation_s": sec, "tokens_per_s": (c["generated_tokens"] - old_tokens) / max(sec, 1e-9)}
        write()

    with open(rows_path, "a") as f:
        for rec in old:
            keep(f, rec)
        while engine.has_unfinished():
            for rid, out_ids, lps, fr in engine.step():
                req = live.pop(rid)
                shot_stop = bool(shots) and fr == "stop" and S.STOP_ID not in out_ids
                if shot_stop:
                    out_ids, lps = cut_at_shot_stop(tok, out_ids, lps)
                rec = J.record(tok, req, out_ids, lps, fr)
                rec.update(R.grade_v3(req["gold"], rec["text"]))
                n_gen = rec["n_new"]                                        # sampled-token probabilities (raw, before truncation): min-p check
                rec.update(n_tok_p_lt_1e2=sum(1 for x in lps[:n_gen] if x < LOG_1E2), n_tok_p_lt_1e3=sum(1 for x in lps[:n_gen] if x < LOG_1E3),
                           min_token_logprob=min(lps[:n_gen]) if n_gen else None)
                rec.update(prompt=tok.decode(req["ids"][: req["n_prompt"]], skip_special_tokens=False), model=model, prompt_arm=a.prompt,
                           attempt=req["attempt"], shots_arm=shots and shots["arm"], shot_stop=shot_stop)
                if rec["cap_hit"] and req["attempt"] < a.restarts:          # restart: the same request with the next attempt's seed
                    nxt = next_attempt(req)
                    live[nxt["rid"]] = nxt
                    add(nxt)
                    c["restarts"] += 1
                keep(f, rec)
    assert not live, f"{len(live)} requests did not finish"
    m["memory"] = engine.memory()
    m["status"] = "done"
    m["wall_s"] = time.time() - t0
    write()
    print(json.dumps({k: m[k] for k in ("status", "counts", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
