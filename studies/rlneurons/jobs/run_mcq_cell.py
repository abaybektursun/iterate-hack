"""One cell of the test outside math and code (specs/SPEC_ood1.md): one model, with or without the Math cue, the 500 frozen
multiple-choice items (250 MMLU-Pro outside math and code, 250 BBH), one sampling setting, one sample per item, on the team runner.
Reuses rln4_gen's vLLM engine and the study's unchanged math prompt (pair1).

    uv run tools/gpu.py submit h100 --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh &&
        /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_mcq_cell --model base --cue --temperature 1.0 --top-p 1.0 --seed 61000000 --commit $(git rev-parse HEAD)"

  --model  base = allenai/Olmo-3-1025-7B, rl_math = allenai/Olmo-3.1-7B-RL-Zero-Math, think_sft = allenai/Olmo-3-7B-Think-SFT; all
           with the RL-Math tokenizer and prompt template (data/ood1/frozen_ood1.json).
  --cue    the Math cue ' line!\n\nOkay' (frozen_ood1.json cue_ids) is placed after the prompt as the start of the answer.
  --seed   item i (its place in ood1_items.json) is sampled with seed + i.
  --n      every (500 // n)-th item, n items (smoke runs: both benchmarks).
  --grader-check-only  no model: run the grader check and stop.

Order: (1) grader check on every item: the answer "Answer: <gold>" must be right, "Answer: <next letter>" and a text without
"Answer:" must be wrong; the job stops otherwise. (2) generation: generations.jsonl, one row per finished request, flush + fsync.
(3) grading: answers.jsonl (the row plus mode, letter, right) and metrics.json. Fail loud: no fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import time

from studies.rlneurons.lib import mcq_lib as M
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]


def load(fz, n):
    path = STUDY / "data" / "ood1" / fz["items"]["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == fz["items"]["sha256"], "ood1_items.json differs from frozen_ood1.json"
    items = [{"idx": i, **x} for i, x in enumerate(json.loads(path.read_text()))]
    assert len(items) == fz["items"]["n"]
    return items if n is None else items[::len(items) // n][:n]


def grader_check(items):
    bad = []
    for x in items:
        other = M.LETTERS[(M.LETTERS.index(x["gold"]) + 1) % x["n_options"]]
        ok = (M.grade(f"so it is that one.\n\nAnswer: {x['gold']}", x["gold"], x["n_options"])["right"]
              and not M.grade(f"Answer: {x['gold']}\nNo.\nAnswer: ({other})", x["gold"], x["n_options"])["right"]
              and not M.grade(f"The correct option is ({x['gold']}).", x["gold"], x["n_options"])["right"])
        if not ok:
            bad.append(x["uid"])
    return {"n": len(items), "failed": bad}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=("base", "rl_math", "think_sft"))
    ap.add_argument("--cue", action="store_true")
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
    fz = json.loads((STUDY / "data" / "ood1" / "frozen_ood1.json").read_text())
    items = load(fz, a.n)
    m = {"status": "grader check", "config": {**vars(a), "out": str(out)}, "commit": a.commit, "job_id": os.environ.get("JOB_ID"),
         "n_items": len(items), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    m["grader_check"] = grader_check(items)
    G.dump(mpath, m)
    assert not m["grader_check"]["failed"], f"grader check failed on {m['grader_check']['failed'][:10]}"
    if a.grader_check_only:
        print(json.dumps(m["grader_check"]))
        return

    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    from studies.rlneurons.jobs import rln4_gen as J
    pre = fz["cue_ids"] if a.cue else []
    cap = fz["cap"]
    sampling = {"temperature": a.temperature, "top_p": a.top_p, "repetition_penalty": 1.0}
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    assert tok.decode(fz["cue_ids"]) == fz["cue_text"], tok.decode(fz["cue_ids"])
    reqs = {}
    for x in items:
        msg = [{"role": "user", "content": x["content"]}]
        text = tok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
        assert text == S.TEMPLATE[fz["template"]].format(problem=x["content"]), ("G-TEMPLATE", x["uid"], text[-300:])
        ids = [int(i) for i in tok.apply_chat_template(msg, tokenize=True, add_generation_prompt=True, return_dict=False)]
        assert len(ids) + len(pre) <= 4096, f"{x['uid']}: prompt of {len(ids)} tokens"
        reqs[x["uid"]] = {**x, "ids": ids + pre, "n_prompt": len(ids), "prompt": text, "seed": a.seed + x["idx"]}
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
                g = {"bench": r["bench"], "group": r["group"], "idx": r["idx"], "uid": uid, "model": a.model, "cue": a.cue,
                     "seed": r["seed"], "sampling": sampling, "prompt": r["prompt"], "prefix_ids": pre, "gold": r["gold"],
                     "text": tok.decode(pre + ids, skip_special_tokens=False), "n_new": len(ids), "cap_hit": j is None,
                     "finish_reason": fr}
                f.write(json.dumps(g) + "\n")
                f.flush()
                os.fsync(f.fileno())
                gens.append(g)
                if len(gens) % 50 == 0:
                    print(f"{len(gens)}/{len(reqs)} answers, {time.time() - t_gen:.0f} s", flush=True)
    assert len(gens) == len(reqs), f"{len(reqs) - len(gens)} requests did not finish"
    m.update(status="grading", generation_s=time.time() - t_gen, memory=engine.memory())
    G.dump(mpath, m)
    rows = sorted(({**g, **M.grade(g["text"], g["gold"], reqs[g["uid"]]["n_options"])} for g in gens), key=lambda r: r["idx"])
    rows_path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    m["counts"] = {b: {"n": len(rs), "right": sum(r["right"] for r in rs), "cap_hits": sum(r["cap_hit"] for r in rs),
                       "no_answer": sum(r["mode"] != "answer" for r in rs),
                       "mean_generated_tokens": sum(r["n_new"] for r in rs) / len(rs)}
                   for b in ("mmlupro", "bbh", "all") for rs in [[r for r in rows if b in (r["bench"], "all")]]}
    m.update(status="done", wall_s=time.time() - t0)
    G.dump(mpath, m)
    print(json.dumps({k: m[k] for k in ("status", "counts", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
