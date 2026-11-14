"""Strategy basins, step 1: sample k solutions per problem from one model, for the base-vs-RL strategy count.

    python exp/strategy_gen.py --model base --k 32            # base + opening cue, T 1.0 / top-p 1.0, vLLM, GPU
    python exp/strategy_gen.py --model rl --k 32              # Olmo 3.1 RL-Zero-Math, same prompts and sampling
    python exp/strategy_gen.py --model base --k 4 --n-problems 2 --dry   # builds requests only, no model

Each model runs at its own best published setting from DIRECTION.md: the base with the cue " line!\\n\\nOkay",
the RL model without it, both at T 1.0 / top-p 1.0, cap 16,384, prompts from the frozen RLN-4 inputs (exp/data/).
Problems: a fixed, subject-stratified subset of MATH-500 (6 per subject, 42 total, seed 0).
Appends to $OUT_DIR/generations.jsonl, one line per sample, with an approximate boxed-answer grade
(exact match after light normalization; it is not grader v3).
"""
import argparse
import json
import os
import pathlib
import random
import re
import time

DATA = pathlib.Path(__file__).resolve().parent / "data"
SEED_BASE = {"base": 51_000_000, "rl": 52_000_000}  # new seed range, outside RLN-4 and cue_sampling


def problem_subset(math, per_subject, seed=0):
    by = {}
    for i, p in enumerate(math):
        by.setdefault(p["unique_id"].split("/")[1], []).append(i)
    rng = random.Random(seed)
    return sorted(i for s in sorted(by) for i in rng.sample(by[s], per_subject))


def last_boxed(text):
    i = text.rfind("\\boxed")
    if i < 0:
        return None
    j = text.find("{", i)
    if j < 0:
        return None
    depth = 0
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return text[j + 1:k]
    return None


def norm(s):
    s = re.sub(r"\\left|\\right|\\!|\\,|\\;|\\ |\$|\s", "", s)
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac").replace("^\\circ", "").replace("^{\\circ}", "")
    s = re.sub(r"\\text\{(.*?)\}", r"\1", s)
    return s.rstrip(".")


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
                pred = last_boxed(c.text)
                ok = pred is not None and norm(pred) == norm(r["gold"])
                cap_hit = len(c.token_ids) >= cap
                n_correct += ok
                n_cap += cap_hit
                n_tok += len(c.token_ids)
                f.write(json.dumps({"model": r["model"], "idx": r["idx"], "uid": r["uid"], "sample": s,
                                    "gold": r["gold"], "pred": pred, "correct": ok, "n_out": len(c.token_ids),
                                    "cap_hit": cap_hit, "text": c.text}) + "\n")
    n = len(reqs) * args.k
    meta.update(n=n, acc_boxed_exact=n_correct / n, cap_hits=n_cap, mean_tokens=n_tok / n,
                finished_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    (out / f"meta_{args.model}.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps({k: v for k, v in meta.items() if k != "problems"}))
