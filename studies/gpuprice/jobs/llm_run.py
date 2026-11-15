"""LLM as the predictive density: samples answers to forecast questions over the listing-table contexts. Runs on a GPU.

uv run tools/gpu.py submit b200 --hours 1 -- 'bash studies/gpuprice/jobs/llm_job.sh --model fp8 --context studies/gpuprice/data/llm_context_v1.jsonl --variants sample,quant,prob,cot'

Reads the contexts of llm_context.py; for each (context, horizon, variant) builds one user message (no system prompt, no
tool) and samples n completions at temperature 1.0, top-p 1.0. Writes $OUT_DIR/gen_<variant>.jsonl (prompt and raw
samples per cell) after each variant, and run.json. Parsing and scoring are on the laptop (llm_score.py).
"""
import argparse, datetime as dt, json, os, pathlib, time

# Qwen/Qwen3-Next-80B-A3B-Instruct, released 2025-09-09 (Hugging Face createdAt). Checkpoint -> (repository, revision):
#   fp8: Qwen's own FP8, 82 GB, created 2025-09-22: needs a B200.
#   w4a16: RedHatAI's 4-bit weights (llm-compressor), 44 GB, created 2025-12-12, last modified 2026-04-28: fits an H100.
MODELS = {"fp8": ("Qwen/Qwen3-Next-80B-A3B-Instruct-FP8", "c5f5f263bdd5cc134092897864e8905d8fe7b928"),
          "w4a16": ("RedHatAI/Qwen3-Next-80B-A3B-Instruct-quantized.w4a16", "ac9dc5b939ba948ab378b8638cfcce4ac4d5642b")}
# variant -> (samples per cell, max new tokens)
VARIANTS = {"sample": (30, 16), "quant": (10, 48), "prob": (10, 96), "cot": (30, 400)}


def question(variant, c, h):
    target = dt.date.fromisoformat(c["targets"][str(h)])
    when = f"{target:%A} {target} ({h} day{'s' if h > 1 else ''} from today)"
    m0 = c["last_value"]
    if variant == "sample":
        return f"Question: what will the median be on {when}? Answer with one number in USD per GPU-hour and nothing else."
    if variant == "quant":
        return (f"Question: give your 10%, 50% and 90% quantiles for the median on {when}. There should be a 1 in 10 chance that the "
                f"median is below q10 and a 1 in 10 chance that it is above q90. Answer with one JSON object and nothing else: "
                f'{{"q10": number, "q50": number, "q90": number}}')
    if variant == "prob":
        return (f"Question: how will the median on {when} compare with the latest median, {m0:g}? Answer with one JSON object and nothing "
                f'else: {{"p_lower": probability that it is below {m0:g}, "p_same": probability that it is exactly {m0:g}, "p_higher": '
                f'probability that it is above {m0:g}, "level_if_lower": the median you expect if it is lower, "level_if_higher": the '
                f"median you expect if it is higher}}. The three probabilities sum to 1.")
    if variant == "cot":
        return (f"Question: what will the median be on {when}? First reason in at most 150 words: which listings sit next to the median, "
                f"which of them reprice often, which might enter or leave, and what that does to the median by the target date. Then "
                f"finish with one line of the form ANSWER: <number>")
    raise AssertionError(variant)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", required=True); ap.add_argument("--variants", required=True)
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--limit", type=int, default=None, help="the first k contexts (smoke run)")
    ap.add_argument("--horizons", default="1,3,7")
    ap.add_argument("--origins", default=None, help="comma list: only these origins of the context file")
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    a = ap.parse_args()
    assert a.out, "no --out and no $OUT_DIR"
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ctx = [json.loads(l) for l in open(a.context)]
    if a.origins:
        ctx = [c for c in ctx if c["origin_date"] in a.origins.split(",")]
    ctx = ctx[: a.limit]
    assert ctx, "no context selected"
    variants = a.variants.split(","); horizons = [int(h) for h in a.horizons.split(",")]
    assert set(variants) <= set(VARIANTS)
    for c in ctx:
        assert "2026-10-01" <= c["origin_date"] <= "2026-10-30", "origin outside the development window"

    from vllm import LLM, SamplingParams
    t0 = time.time()
    MODEL, REVISION = MODELS[a.model]
    llm = LLM(model=MODEL, revision=REVISION, max_model_len=12288, gpu_memory_utilization=0.90, enable_prefix_caching=True, seed=0,
              gdn_prefill_backend="triton")      # the default FlashInfer prefill is JIT-compiled and the image has no nvcc
    tok = llm.get_tokenizer()
    run = {"model": MODEL, "revision": REVISION, "job_id": os.environ.get("JOB_ID"), "args": vars(a), "load_s": time.time() - t0,
           "variants": {}}
    for v in variants:
        n, max_tokens = VARIANTS[v]
        cells = [(c, h) for c in ctx for h in horizons]
        prompts = [tok.apply_chat_template([{"role": "user", "content": c["context"] + "\n\n" + question(v, c, h)}],
                                           tokenize=False, add_generation_prompt=True) for c, h in cells]
        t1 = time.time()
        outs = llm.generate(prompts, SamplingParams(n=n, temperature=1.0, top_p=1.0, max_tokens=max_tokens))
        assert len(outs) == len(cells)
        gen = 0
        with open(out / f"gen_{v}.jsonl", "w") as f:
            for (c, h), p, o in zip(cells, prompts, outs):
                assert len(o.outputs) == n
                gen += sum(len(x.token_ids) for x in o.outputs)
                f.write(json.dumps({"series_id": c["series_id"], "origin_date": c["origin_date"], "horizon_days": h,
                                    "target_date": c["targets"][str(h)], "last_value": c["last_value"], "variant": v, "prompt": p,
                                    "prompt_tokens": len(o.prompt_token_ids), "samples": [x.text for x in o.outputs],
                                    "finish": [x.finish_reason for x in o.outputs]}) + "\n")
        run["variants"][v] = {"cells": len(cells), "n": n, "max_tokens": max_tokens, "seconds": time.time() - t1, "generated_tokens": gen,
                              "prompt_tokens": sum(len(o.prompt_token_ids) for o in outs)}
        print(v, run["variants"][v], flush=True)
        json.dump(run, open(out / "run.json", "w"), indent=1)
    print("done", time.time() - t0, "s")


if __name__ == "__main__":
    main()
