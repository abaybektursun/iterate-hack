"""Draft-critique-revision (specs/SPEC_critique.md, board work-70152d): continue each stored, finished MATH-500 answer (the draft)
after a fixed review line, with the same model and sampling, and grade the whole text with grader v3 (the last answer wins, so a
revision that states no new answer keeps the draft's). Drafts that hit the cap are not revised. No gold is shown to the model.

    uv run tools/gpu.py submit h100 --hours 1.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.revise
        --model base --drafts /runs/inputs/critique/base_cue_T1.jsonl.gz --drafts-sha256 <sha> --seed 77000000 --commit $(git rev-parse HEAD)"

  --drafts  gzipped jsonl, one row per problem (problem_index, gold, text, cap_hit): the stored T 1.0 cue rows, uploaded once to the
            Volume iterate-runs with `modal volume put` (prep in specs/SPEC_critique.md). --drafts-sha256 freezes the file.
  --seed    problem i is sampled with seed + i.  --n  the first n problems (smoke).  --max-tokens  revision cap (default 8,192).
  --shard s --shards K  only the problems with list position % K == s (seeds unchanged, so the K shards together equal one job).

Writes to --out (default $OUT_DIR): answers.jsonl (one row per revised problem: draft and full text, v3 of both, revision tokens) and
metrics.json, rewritten after every row. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import pathlib
import re
import time
from importlib import metadata

from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.jobs.run_cell import D4, MODELS, PINS, problems
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

CRITIQUE = "\n\nWait, before I finalize, let me check this solution carefully for mistakes."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--drafts", required=True)
    ap.add_argument("--drafts-sha256", required=True)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--top-p", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True)
    a = ap.parse_args()
    t0 = time.time()
    assert a.out and re.fullmatch(r"[0-9a-f]{40}", a.commit), (a.out, a.commit)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows_path, mpath = out / "answers.jsonl", out / "metrics.json"
    assert not rows_path.exists(), f"{rows_path} exists: one fresh directory per run"
    raw = pathlib.Path(a.drafts).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == a.drafts_sha256, "drafts file differs from --drafts-sha256"
    drafts = {r["problem_index"]: r for r in map(json.loads, gzip.decompress(raw).decode().splitlines())}

    fz = json.loads((D4 / "frozen4.json").read_text())
    assert 0 <= a.shard < a.shards, (a.shard, a.shards)
    probs = [p for j, p in enumerate(problems("math500", fz)[: a.n]) if j % a.shards == a.shard]
    assert set(int(p["index"]) for p in probs) <= set(drafts), "a problem has no draft"
    assert all(drafts[int(p["index"])]["gold"] == p["answer"] for p in probs), "draft gold differs from math500.json"
    versions = {k: metadata.version(k) for k in PINS}
    assert versions == PINS, f"package versions {versions} differ from the study's {PINS}: run setup_vllm.sh first"
    repo, _, rev = fz["models"][MODELS[a.model]]
    sampling = {"temperature": a.temperature, "top_p": a.top_p, "repetition_penalty": 1.0}
    m = {"status": "starting", "config": {**vars(a), "critique": CRITIQUE, "sampling": sampling, "model_repo": repo, "model_revision": rev},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "versions": versions, "started_utc": J.utc()}

    def write():
        m["updated_utc"] = J.utc()
        G.dump(mpath, m)

    write()
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    crit = tok(CRITIQUE, add_special_tokens=False)["input_ids"]
    reqs, kept = [], 0
    for p in probs:
        i, d = int(p["index"]), drafts[int(p["index"])]
        if d["cap_hit"]:
            continue
        kept += 1
        text = d["text"].rstrip()
        ids = S.render_ids(tok, p["problem"]) + R.encode_answer(tok, text, fz["prefill_text"], fz["prefill_ids"])[0] + crit
        reqs.append({"rid": f"{a.model}|{i}", "idx": i, "ids": ids, "draft": text, "gold": p["answer"], "seed": a.seed + i})
    max_len = max(len(r["ids"]) for r in reqs) + a.max_tokens
    model_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
    os.environ.update(G.ENGINE_ENV)
    engine = J.VllmEngine(model_dir, tok_dir, max_len)
    m.update(status="running", engine=engine.info, n_problems=len(probs), n_revised=len(reqs), n_draft_cap_hits_skipped=len(probs) - kept)
    write()
    live = {r["rid"]: r for r in reqs}
    for r in reqs:
        engine.add(r["rid"], r["ids"], sampling, r["seed"], a.max_tokens)
    c = {"n": 0, "draft_v3": 0, "revised_v3": 0, "right_to_wrong": 0, "wrong_to_right": 0, "answer_changed": 0, "cap_hits": 0, "revision_tokens": 0}
    t_gen = time.time()
    with open(rows_path, "a") as f:
        while engine.has_unfinished():
            for rid, out_ids, lps, fr in engine.step():
                q = live.pop(rid)
                j = next((k for k, t in enumerate(out_ids) if t == S.STOP_ID), None)
                gen = tok.decode(out_ids if j is None else out_ids[:j], skip_special_tokens=False)
                full = q["draft"] + CRITIQUE + gen
                g0, g1 = R.grade_v3(q["gold"], q["draft"]), R.grade_v3(q["gold"], full)
                rec = {"problem_index": q["idx"], "model": a.model, "seed": q["seed"], "gold": q["gold"], "draft": q["draft"], "revision": gen,
                       "n_new": len(out_ids) if j is None else j, "cap_hit": j is None, "finish_reason": fr,
                       "draft_extracted_v3": g0["extracted_v3"], "draft_v3": g0["score_v3"], **g1,
                       "answer_changed": not R.agree(g0["extracted_v3"], g1["extracted_v3"]), "utc": J.utc()}
                f.write(json.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
                c["n"] += 1
                c["draft_v3"] += g0["score_v3"]
                c["revised_v3"] += g1["score_v3"]
                c["right_to_wrong"] += int(g0["score_v3"] == 1 and g1["score_v3"] == 0)
                c["wrong_to_right"] += int(g0["score_v3"] == 0 and g1["score_v3"] == 1)
                c["answer_changed"] += int(rec["answer_changed"])
                c["cap_hits"] += int(rec["cap_hit"])
                c["revision_tokens"] += rec["n_new"]
                m["counts"] = {**c, "mean_revision_tokens": c["revision_tokens"] / c["n"], "generation_s": time.time() - t_gen}
                write()
    assert not live, f"{len(live)} requests did not finish"
    m.update(status="done", wall_s=time.time() - t0, memory=engine.memory())
    write()
    print(json.dumps({k: m[k] for k in ("status", "counts", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
