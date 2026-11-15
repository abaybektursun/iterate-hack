"""Prefix hand-off generation (specs/SPEC_handoff.md): one finisher model continues stored answers of both writers from a cut.
Request = plain prompt ids + the first L ids of the writer's answer; T 1.0 / top-p 1.0; max new tokens = cap - L.

    uv run tools/gpu.py submit h100 --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.handoff_gen
        --finisher rl --cuts 25,50,75 --commit $(git rev-parse HEAD)"

  --finisher base | rl (frozen4.json revisions, RL tokenizer), or any label with --finisher-path.
  --finisher-path  a local weights directory instead (jobs/wsp_edit.py writes Think-SFT to one); the RL tokenizer as for the others.
  --plan     file in data/handoff/ (default plan_v1.json: MATH-500 pool; plan_v2.json: the relay on hard328, specs/SPEC_relay.md).
  --cuts     percent of the writer's answer ids kept, from handoff_lib.CUTS. 100 is skipped for a writer answer that hit the cap.
  --writers  directory holding <writer job>/answers.jsonl (default /runs: the Volume iterate-runs inside a job).
  --n        the first n pool problems (smoke).
  --dry-run  stand-in engine, no vLLM: request k gets, in turn, an immediate stop, a wrong answer line, a cap hit.

Writes to --out (default $OUT_DIR): answers.jsonl, one row per finished request, written (flush + fsync) before anything else
is computed from it: ids, decoded prefix and continuation, finish reason. No scoring and no loop detector here, so no scoring
error can lose a generated row; analysis/handoff.py scores. metrics.json: counts, tokens, tokens/s, config, commit, job id.
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
from studies.rlneurons.jobs import run_cell as C
from studies.rlneurons.lib import handoff_lib as H
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S

PLAN = C.STUDY / "data" / "handoff" / "plan_v1.json"
PLANS = {1: ("math500", H.WRITERS, H.SEED), 2: ("hard328", H.RELAY_WRITERS, H.RELAY_SEED)}      # plan version: set, writers, seed base
SAMPLING = {"temperature": 1.0, "top_p": 1.0, "repetition_penalty": 1.0}


def requests(tok, fz, plan, texts, cuts, n=None) -> list:
    """One request per (pool problem, writer, cut). texts: {writer: handoff_lib.writer_texts}. Asserts the plan's hashes."""
    bench, writers, seed0 = PLANS[plan["version"]]
    assert plan["writers"] == writers and plan["seed"] == seed0
    probs = {int(p["index"]): p for p in C.problems(bench, fz)}
    keep = set(plan["pool"][:n])
    reqs = []
    for row in plan["rows"]:
        i, w = row["problem_index"], row["writer"]
        if i not in keep:
            continue
        t = texts[w][i]
        assert H.sha(t["text"]) == row["text_sha256"], f"{w} {i}: the writer text differs from the plan's"
        ids, pids = H.answer_ids(tok, fz, t["text"]), S.render_ids(tok, probs[i]["problem"])
        for c in cuts:
            L = row["len"][str(c)]
            if c == 100 and row["stratum"] == "cap":    # the check arm needs an answer that finished
                continue
            assert H.sha(ids[:L]) == row["ids_sha256"][str(c)], f"{w} {i} cut {c}: prefix ids differ from the plan's"
            reqs.append({"rid": f"{w}|{c}|{i}", "problem_index": i, "writer": w, "cut": c, "n_prefix": L, "n_prompt": len(pids),
                         "ids": pids + ids[:L], "seed": H.seed(w, c, i, writers, seed0), "max_tokens": fz["cap"] - L, "gold": probs[i]["answer"]})
    return reqs


class Canned:
    """Stand-in engine: request k gets k % 3 == 0 an immediate stop, 1 a wrong answer line, 2 a cap hit."""
    info = {"vllm": None, "dry_run": True}

    def __init__(self, tok):
        self.tok, self.queue, self.k = tok, [], 0

    def add(self, rid, ids, sampling, seed, max_tokens):
        self.queue.append((rid, self.k % 3, max_tokens))
        self.k += 1

    def step(self):
        done, self.queue = self.queue[:2], self.queue[2:]
        wrong = self.tok("\n\nAnswer: $-123456789$", add_special_tokens=False)["input_ids"] + [S.STOP_ID]
        so = self.tok(" so so", add_special_tokens=False)["input_ids"]
        return [(rid, [S.STOP_ID] if k == 0 else wrong[-mt:] if k == 1 else (so * mt)[:mt], None, "length" if k == 2 else "stop") for rid, k, mt in done]

    def has_unfinished(self):
        return bool(self.queue)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--finisher", required=True)
    ap.add_argument("--finisher-path")
    ap.add_argument("--plan", default=PLAN.name)
    ap.add_argument("--cuts", default="25,50,75")
    ap.add_argument("--writers", default="/runs")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", required=True)
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    cuts = [int(c) for c in a.cuts.split(",")]
    assert set(cuts) <= set(H.CUTS), cuts
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows_path, mpath = out / "answers.jsonl", out / "metrics.json"
    assert not rows_path.exists(), f"{rows_path} exists: one fresh directory per run"
    fz = json.loads((C.D4 / "frozen4.json").read_text())
    plan = json.loads((PLAN.parent / a.plan).read_text())
    assert (a.finisher in C.MODELS) != bool(a.finisher_path), "give --finisher base or rl, or another label with --finisher-path"
    versions = {k: metadata.version(k) for k in C.PINS if k != "vllm" or not a.dry_run}
    if not a.dry_run:
        assert versions == C.PINS, f"package versions {versions} differ from the study's {C.PINS}: run setup_vllm.sh first"
    repo, _, rev = (None, None, None) if a.finisher_path else fz["models"][C.MODELS[a.finisher]]
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    texts = {w: H.writer_texts(pathlib.Path(a.writers) / job / "answers.jsonl") for w, job in plan["writers"].items()}
    reqs = requests(tok, fz, plan, texts, cuts, a.n)
    live = {r["rid"]: r for r in reqs}
    assert len(live) == len(reqs) and len({r["seed"] for r in reqs}) == len(reqs)
    m = {"status": "starting", "config": {**vars(a), "cuts": cuts, "out": str(out), "model_repo": repo, "model_revision": rev, "tokenizer": fz["tokenizer"],
                                         "sampling": SAMPLING, "cap": fz["cap"], "plan": a.plan, "n_requests": len(reqs)},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "versions": versions, "started_utc": J.utc()}

    def write():
        m["updated_utc"] = J.utc()
        G.dump(mpath, m)

    write()
    t_load = time.time()
    if a.dry_run:
        engine = Canned(tok)
    else:
        model_dir = a.finisher_path or snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
        os.environ.update(G.ENGINE_ENV)
        engine = J.VllmEngine(model_dir, tok_dir, 2048 + fz["cap"])
    m["engine"] = {**engine.info, "load_s": time.time() - t_load}
    m["status"] = "running"
    write()
    for r in reqs:
        engine.add(r["rid"], r["ids"], SAMPLING, r["seed"], r["max_tokens"])
    t_gen = time.time()
    c = {"n": 0, "cap_hits": 0, "generated_tokens": 0, "prefix_tokens": 0}
    with open(rows_path, "a") as f:
        while engine.has_unfinished():
            for rid, out_ids, _, fr in engine.step():
                req = live.pop(rid)
                j = next((k for k, t in enumerate(out_ids) if t == S.STOP_ID), None)
                gen = out_ids if j is None else out_ids[:j]
                rec = {**{k: req[k] for k in ("problem_index", "writer", "cut", "n_prefix", "n_prompt", "seed", "max_tokens", "gold")},
                       "finisher": a.finisher, "n_new": len(gen), "cap_hit": j is None, "finish_reason": fr, "out_ids": out_ids,
                       "prompt": tok.decode(req["ids"][: req["n_prompt"]], skip_special_tokens=False),
                       "prefix_text": tok.decode(req["ids"][req["n_prompt"]:], skip_special_tokens=False),
                       "gen_text": tok.decode(gen, skip_special_tokens=False),
                       "text": tok.decode(req["ids"][req["n_prompt"]:] + gen, skip_special_tokens=False), "utc": J.utc()}    # decoded in one piece: a cut can split a character
                f.write(json.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
                c["n"] += 1
                c["cap_hits"] += int(rec["cap_hit"])
                c["generated_tokens"] += rec["n_new"]
                c["prefix_tokens"] += rec["n_prefix"]
                sec = time.time() - t_gen
                m["counts"] = {**c, "n_planned": len(reqs), "generation_s": sec, "tokens_per_s": c["generated_tokens"] / max(sec, 1e-9)}
                write()
    assert not live, f"{len(live)} requests did not finish"
    m["status"] = "done"
    m["wall_s"] = time.time() - t0
    write()
    print(json.dumps({k: m[k] for k in ("status", "counts", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
