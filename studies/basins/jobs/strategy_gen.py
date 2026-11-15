"""Strategy basins, step 1: sample k solutions per problem from one model, for the base-vs-RL strategy count.

    python -m studies.basins.jobs.strategy_gen --model base --k 32            # base + opening cue, T 1.0 / top-p 1.0, vLLM, GPU
    python -m studies.basins.jobs.strategy_gen --model rl --k 32              # Olmo 3.1 RL-Zero-Math, same prompts and sampling
    python -m studies.basins.jobs.strategy_gen --model base --k 4 --n-problems 2 --dry   # builds requests only, no model

Each model runs at its own best published setting from DIRECTION.md: the base with the cue " line!\\n\\nOkay",
the RL model without it, both at T 1.0 / top-p 1.0, cap 16,384, prompts from the frozen RLN-4 inputs (studies/rlneurons/data/rln4/).
Problems: a fixed, subject-stratified subset of MATH-500 (6 per subject, 42 total, seed 0).
Appends to $OUT_DIR/generations.jsonl, one line per sample, graded with the rlneurons grader v3
(studies/rlneurons/lib/rln4_lib.grade_v3). Run on the GPU with the study engine:
    bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.basins.jobs.strategy_gen ...
"""
import argparse
import json
import os
import pathlib
import random
import time

DATA = pathlib.Path(__file__).resolve().parents[2] / "rlneurons" / "data" / "rln4"
SEED_BASE = {"base": 51_000_000, "rl": 52_000_000}  # new seed range, outside RLN-4 and cue_sampling


def problem_subset(math, per_subject, seed=0):
    by = {}
    for i, p in enumerate(math):
        by.setdefault(p["unique_id"].split("/")[1], []).append(i)
    rng = random.Random(seed)
    return sorted(i for s in sorted(by) for i in rng.sample(by[s], per_subject))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["base", "rl"], required=True)
    ap.add_argument("--k", type=int, default=32)
    ap.add_argument("--per-subject", type=int, default=6)
    ap.add_argument("--n-problems", type=int, default=None, help="keep only the first n of the subset (smoke test)")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    out = pathlib.Path(os.environ["OUT_DIR"])
    fz = json.loads((DATA / "frozen4.json").read_text())
    math = json.loads((DATA / "math500.json").read_text())
    pids = json.loads((DATA / "prompt_ids.json").read_text())
    assert pids["pair"] == fz["template"] == "pair1", (pids["pair"], fz["template"])
    idx = problem_subset(math, args.per_subject)[:args.n_problems]
    cue = fz["prefill_ids"] if args.model == "base" else []
    repo, _, rev = fz["models"]["base" if args.model == "base" else "s2800"]
    tok_repo, tok_rev = fz["tokenizer"]
    cap = fz["cap"]
    reqs = [{"model": args.model, "idx": i, "uid": math[i]["unique_id"], "ids": pids["ids"][i] + cue,
             "seed": SEED_BASE[args.model] + i, "gold": math[i]["answer"]} for i in idx]
    meta = {"model": args.model, "repo": [repo, rev], "cue": cue, "k": args.k, "T": 1.0, "top_p": 1.0, "cap": cap,
            "problems": idx, "dry": args.dry, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print(json.dumps(meta))
    if args.dry:
        (out / f"meta_{args.model}.json").write_text(json.dumps(meta, indent=1))
        raise SystemExit(0)

    from studies.rlneurons.lib import rln4_lib
    from studies.basins.lib import engine
    engine.enter()  # before vllm is imported
    from vllm import LLM, SamplingParams, TokensPrompt
    llm = LLM(model=repo, revision=rev, tokenizer=tok_repo, tokenizer_revision=tok_rev, dtype="bfloat16",
              max_model_len=max(len(r["ids"]) for r in reqs) + cap, seed=0, enable_prefix_caching=True)
    sps = [SamplingParams(n=args.k, temperature=1.0, top_p=1.0, top_k=-1, max_tokens=cap, seed=r["seed"]) for r in reqs]
    res = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in reqs], sps)
    n_correct = n_cap = n_tok = 0
    with open(out / "generations.jsonl", "a") as f:
        for r, o in zip(reqs, res):
            assert len(o.outputs) == args.k, len(o.outputs)
            for s, c in enumerate(o.outputs):
                g = rln4_lib.grade_v3(r["gold"], c.text)
                pred, ok = g["extracted_v3"], bool(g["score_v3"])
                cap_hit = len(c.token_ids) >= cap
                n_correct += ok
                n_cap += cap_hit
                n_tok += len(c.token_ids)
                f.write(json.dumps({"model": r["model"], "idx": r["idx"], "uid": r["uid"], "sample": s,
                                    "gold": r["gold"], "pred": pred, "correct": ok, "n_out": len(c.token_ids),
                                    "cap_hit": cap_hit, "text": c.text}) + "\n")
    n = len(reqs) * args.k
    meta.update(n=n, acc_grader_v3=n_correct / n, cap_hits=n_cap, mean_tokens=n_tok / n,
                finished_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    (out / f"meta_{args.model}.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps({k: v for k, v in meta.items() if k != "problems"}))
