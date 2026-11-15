"""One cell of the Code pair (specs/SPEC_code1.md): one model, one opening prefix, HumanEval+ and MBPP+ (542 problems), one sampling
setting, one sample per problem, on the team runner. Reuses rln4_gen's vLLM engine.

    uv run tools/gpu.py submit h100 --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && uv pip install -q --python /opt/rln-vllm/bin/python pyarrow numpy &&
        /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_code_cell --model rl_code --temperature 1.0 --top-p 1.0 --seed 51000000 --commit $(git rev-parse HEAD)"

  --model      base = allenai/Olmo-3-1025-7B, rl_code = allenai/Olmo-3.1-7B-RL-Zero-Code; both with the Code model's tokenizer and
               prompt template (data/code1/frozen_code1.json).
  --prefix-ids JSON list of token ids placed after the prompt as the start of the answer (the opening cue); default none.
  --seed       problem i (0-541: HumanEval+ then MBPP+, file order) is sampled with seed + i.
  --n          the first n problems of each set (smoke runs).
  --grader-check-only  no model: run the grader check and stop (cpu job).

Order: (1) grader check on all problems: every reference solution must pass and every planted wrong program (the entry function
returning None) must fail. The problems that fail it must be exactly frozen_code1.json "excluded" (4 problems), which are not
generated or scored: 538 scored problems; the job stops otherwise. (2) generation: generations.jsonl, one row per finished request, flush + fsync.
(3) grading: answers.jsonl (the row plus mode, code, passed, exit, stderr tail) and metrics.json. Fail loud: no fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import time
from concurrent.futures import ThreadPoolExecutor

from studies.rlneurons.lib import code_lib as C
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
WORKERS = 16


def load(fz, n):
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download
    probs = []
    for name, s in fz["sets"].items():
        path = hf_hub_download(s["repo"], s["file"], revision=s["revision"], repo_type="dataset")
        assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest() == s["sha256"], f"{name}: file differs from frozen_code1.json"
        rows = pq.read_table(path).to_pylist()
        assert len(rows) == s["n"], (name, len(rows))
        probs += [{"bench": name, **C.problem(name, r)} for r in rows[:n]]
    return [{"idx": i, **p} for i, p in enumerate(probs)]


def grader_check(probs, timeout_s):
    with ThreadPoolExecutor(WORKERS) as ex:
        ref = list(ex.map(lambda p: C.run(p["reference"] + p["post"], timeout_s), probs))
        wrong = list(ex.map(lambda p: C.run(C.program(p, C.WRONG.format(entry=p["entry"])), timeout_s), probs))
    ref_fail = [(p["uid"], r["exit"], r["stderr_tail"][-200:]) for p, r in zip(probs, ref) if not r["passed"]]
    wrong_pass = [p["uid"] for p, r in zip(probs, wrong) if r["passed"]]
    return {"n": len(probs), "reference_failed": ref_fail, "wrong_passed": wrong_pass,
            "failed": sorted({u for u, _, _ in ref_fail} | set(wrong_pass))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=("base", "rl_code"))
    ap.add_argument("--prefix-ids", default="[]")
    ap.add_argument("--temperature", type=float)
    ap.add_argument("--top-p", type=float)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--grader-check-only", action="store_true")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    gen_path, rows_path, mpath = out / "generations.jsonl", out / "answers.jsonl", out / "metrics.json"
    assert not gen_path.exists(), f"{gen_path} exists: one fresh directory per run"
    fz = json.loads((STUDY / "data" / "code1" / "frozen_code1.json").read_text())
    probs = load(fz, a.n)
    m = {"status": "grader check", "config": {**vars(a), "out": str(out)}, "commit": a.commit, "job_id": os.environ.get("JOB_ID"),
         "n_problems": len(probs), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    m["grader_check"] = grader_check(probs, fz["test_timeout_s"])
    G.dump(mpath, m)
    print(json.dumps(m["grader_check"], indent=1)[:3000])
    known = sorted(u for u in fz["excluded"] if u in {p["uid"] for p in probs})
    assert m["grader_check"]["failed"] == known, f"grader check: failing problems {m['grader_check']['failed']} are not the frozen exclusions {known}"
    probs = [p for p in probs if p["uid"] not in fz["excluded"]]         # scored set: 538 problems (idx and seeds keep the 542 numbering)
    m["n_scored"] = len(probs)
    if a.grader_check_only:
        return

    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    from studies.rlneurons.jobs import rln4_gen as J
    pre = json.loads(a.prefix_ids)
    cap = fz["cap"]
    sampling = {"temperature": a.temperature, "top_p": a.top_p, "repetition_penalty": 1.0}
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    reqs = {}
    for p in probs:
        msg = [{"role": "user", "content": p["content"]}]
        text = tok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
        assert text == C.TEMPLATE.format(content=p["content"]), ("G-TEMPLATE", p["uid"], text[-300:])
        ids = [int(i) for i in tok.apply_chat_template(msg, tokenize=True, add_generation_prompt=True, return_dict=False)]
        assert len(ids) + len(pre) <= 4096, f"{p['uid']}: prompt of {len(ids)} tokens"
        reqs[p["uid"]] = {**p, "ids": ids + pre, "n_prompt": len(ids), "prompt": text, "seed": a.seed + p["idx"]}
    repo, rev = fz["models"][a.model]
    model_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
    os.environ.update(G.ENGINE_ENV)
    engine = J.VllmEngine(model_dir, tok_dir, 4096 + cap)
    m.update(status="generating", engine=engine.info, model_repo=repo, model_revision=rev, tokenizer=fz["tokenizer"], prefix_ids=pre,
             prefix_text=tok.decode(pre), sampling=sampling, max_tokens=cap, first_prompt_ids=next(iter(reqs.values()))["ids"][:8])
    G.dump(mpath, m)
    for uid, r in reqs.items():
        engine.add(uid, r["ids"], sampling, r["seed"], cap)
    gens, t_gen = [], time.time()
    with open(gen_path, "a") as f:
        while engine.has_unfinished():
            for uid, out_ids, _, fr in engine.step():
                r = reqs[uid]
                j = next((i for i, t in enumerate(out_ids) if t == S.STOP_ID), None)
                ids = out_ids if j is None else out_ids[:j]
                assert j is not None or len(ids) == cap, f"{uid}: no stop id in {len(ids)} ids"
                g = {"bench": r["bench"], "idx": r["idx"], "uid": uid, "model": a.model, "seed": r["seed"], "sampling": sampling,
                     "prompt": r["prompt"], "prefix_ids": pre, "text": tok.decode(pre + ids, skip_special_tokens=False),
                     "n_new": len(ids), "cap_hit": j is None, "finish_reason": fr}
                f.write(json.dumps(g) + "\n")
                f.flush()
                os.fsync(f.fileno())
                gens.append(g)
    assert len(gens) == len(reqs), f"{len(reqs) - len(gens)} requests did not finish"
    m.update(status="grading", generation_s=time.time() - t_gen, memory=engine.memory())
    G.dump(mpath, m)

    def grade(g):
        mode, code = C.extract(g["text"])
        return {**g, "mode": mode, "code": code, **C.run(C.program(reqs[g["uid"]], code), fz["test_timeout_s"])}

    with ThreadPoolExecutor(WORKERS) as ex:
        rows = sorted(ex.map(grade, gens), key=lambda r: r["idx"])
    rows_path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    m["counts"] = {b: {"n": len(rs), "passed": sum(r["passed"] for r in rs), "cap_hits": sum(r["cap_hit"] for r in rs),
                       "no_block": sum(r["mode"] == "none" for r in rs), "timeouts": sum(r["exit"] == "timeout" for r in rs),
                       "mean_generated_tokens": sum(r["n_new"] for r in rs) / len(rs)}
                   for b in [*fz["sets"], "all"] for rs in [[r for r in rows if b in (r["bench"], "all")]]}
    m.update(status="done", wall_s=time.time() - t0)
    G.dump(mpath, m)
    print(json.dumps({k: m[k] for k in ("status", "counts", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
