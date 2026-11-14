"""Strategy basins, step 2: an LLM judge turns sampled solutions into strategy groups and triplet judgments.

    python -m studies.basins.jobs.strategy_judge --gen /runs/<gen-job-id>          # GPU, vLLM, judge model below
    python -m studies.basins.jobs.strategy_judge --gen runs/<gen-job-id> --dry     # builds prompts only, no model

The judge never sees which model wrote a solution, or its grade.
1. Summary: each solution becomes a <= 3-sentence description of its mathematical method, without the final
   answer or style; a looping or method-free solution becomes "NO METHOD".
2. Partition: per problem, all summaries (base and RL pooled, shuffled, anonymous ids) are grouped by main
   method. Done R times with different orders, to measure stability.
3. Triplets: "is B or C closer in method to A?", asked in both orders (Bespoke Labs / Fork-and-Flush style),
   for a 2D t-STE map per problem (fit on the laptop by studies/basins/analysis/strategy_analyze.py).
4. Controls that must pass: exact duplicates must share a group; summaries of two different problems must not.
Writes summaries.jsonl, partitions.jsonl, triplets.jsonl, controls.jsonl and meta.json to $OUT_DIR.
"""
import argparse
import json
import os
import pathlib
import random
import re
import time

JUDGE = ("Qwen/Qwen3-30B-A3B-Instruct-2507-FP8", "5a5a776300a41aaa681dd7ff0106608ef2bc90db")

SUMMARY = """Here is a math problem and one attempted solution.

PROBLEM:
{problem}

SOLUTION:
{solution}

Describe the mathematical METHOD of this solution in at most 3 sentences: the key idea and the main steps.
Do not state the final answer, do not judge correctness, and do not describe writing style, length or self-checks.
If the solution has no coherent method (it repeats itself in a loop, is cut off before any method, or is not
about the problem), reply exactly: NO METHOD"""

PARTITION = """Here is a math problem and {n} short descriptions of methods used to solve it.

PROBLEM:
{problem}

METHODS:
{items}

Group the descriptions by MAIN METHOD. Two descriptions belong to the same group when they rely on the same key
idea, even if arithmetic, notation, order of steps or checks differ. Put a description in its own group when its
key idea differs from all others. Every id must appear in exactly one group.
Reply with JSON only: {{"groups": [{{"name": "<3-8 word name of the method>", "ids": ["<id>", ...]}}, ...]}}"""

TRIPLET = """Math problem:
{problem}

Method A: {a}

Method B: {b}

Method C: {c}

Which method is closer to Method A in its key mathematical idea: B or C? Reply with one letter, B or C."""


def clip(text, head=10_000, tail=3_000):
    return text if len(text) <= head + tail else text[:head] + "\n...[middle cut]...\n" + text[-tail:]


def parse_partition(text, ids):
    start = text.find("{")
    if start < 0:
        return None, "no json"
    try:  # first complete JSON object; the judge sometimes adds text or a second object after it
        groups = json.JSONDecoder().raw_decode(text[start:])[0]["groups"]
        members = [i for g in groups for i in g["ids"]]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        return None, f"bad json: {e}"
    if sorted(members) != sorted(ids):
        return None, f"ids mismatch: {len(members)} given, {len(set(members))} distinct, {len(ids)} expected"
    return groups, None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, help="directory with generations.jsonl")
    ap.add_argument("--shuffles", type=int, default=3)
    ap.add_argument("--triplets-per-anchor", type=int, default=10)
    ap.add_argument("--n-controls", type=int, default=10)
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    out = pathlib.Path(os.environ["OUT_DIR"])
    data = pathlib.Path(__file__).resolve().parents[2] / "rlneurons" / "data" / "rln4"
    math = json.loads((data / "math500.json").read_text())
    gens = [json.loads(l) for l in open(pathlib.Path(args.gen) / "generations.jsonl")]
    rng = random.Random(0)
    t0 = time.time()

    if args.dry:
        class FakeLLM:  # prompt building only: answers a fixed, valid output for each prompt type
            def chat(self, convs, sp, **kw):
                outs = []
                for c in convs:
                    p = c[0]["content"]
                    if p.startswith("Here is a math problem and one"):
                        t = "A method."
                    elif "Group the descriptions" in p:
                        t = json.dumps({"groups": [{"name": "all", "ids": re.findall(r"^([SAB]\d\d):", p, re.M)}]})
                    else:
                        t = "B"
                    outs.append(type("O", (), {"outputs": [type("C", (), {"text": t})()]})())
                return outs
        llm = FakeLLM()
        SP = lambda **kw: kw  # noqa: E731
    else:
        from studies.rlneurons.lib.n13_gen import ENGINE_ENV  # VLLM_USE_FLASHINFER_SAMPLER=0: no nvcc in the image
        os.environ.update(ENGINE_ENV)  # set before vllm is imported
        os.environ["VLLM_USE_DEEP_GEMM"] = "0"  # FP8 judge: DeepGEMM JIT needs nvcc, absent in the image (job frustea-1114-153448-dce3)
        from vllm import LLM, SamplingParams as SP
        llm = LLM(model=JUDGE[0], revision=JUDGE[1], max_model_len=16384, enable_prefix_caching=True, seed=0)

    def ask(prompts, max_tokens, temperature=0.0, seed=0):
        convs = [[{"role": "user", "content": p}] for p in prompts]
        res = llm.chat(convs, SP(temperature=temperature, max_tokens=max_tokens, seed=seed), use_tqdm=False)
        return [r.outputs[0].text.strip() for r in res]

    # 1. summaries
    texts = ask([SUMMARY.format(problem=math[g["idx"]]["problem"], solution=clip(g["text"])) for g in gens], 200)
    items = []
    with open(out / "summaries.jsonl", "w") as f:
        for n, (g, s) in enumerate(zip(gens, texts)):
            it = {"id": n, "model": g["model"], "idx": g["idx"], "sample": g["sample"], "correct": g["correct"],
                  "cap_hit": g["cap_hit"], "no_method": s.upper().startswith("NO METHOD"), "summary": s}
            items.append(it)
            f.write(json.dumps(it) + "\n")
    by_prob = {}
    for it in items:
        if not it["no_method"]:
            by_prob.setdefault(it["idx"], []).append(it)
    print(f"summaries {len(items)}, no-method {sum(i['no_method'] for i in items)}, {time.time() - t0:.0f}s", flush=True)

    # 2. partitions, and 4. controls, share one retry loop
    def partition_jobs(jobs):
        """jobs: list of (key, problem text, [(label, summary)]). Returns {key: (groups or None, error, tries)}."""
        done, todo = {}, list(jobs)
        for attempt in range(3):
            if not todo:
                break
            prompts = []
            for key, problem, pairs in todo:
                lines = "\n".join(f"{lab}: {s}" for lab, s in pairs)
                prompts.append(PARTITION.format(problem=problem, n=len(pairs), items=lines))
            outs = ask(prompts, 4000, temperature=0.0 if attempt == 0 else 0.7, seed=attempt)
            nxt = []
            for job, o in zip(todo, outs):
                groups, err = parse_partition(o, [lab for lab, _ in job[2]])
                done[job[0]] = (groups, err, attempt + 1)
                if groups is None:
                    nxt.append(job)
            todo = nxt
        return done

    jobs, labels = [], {}
    for p, its in by_prob.items():
        for r in range(args.shuffles):
            order = its[:]
            random.Random(1000 * p + r).shuffle(order)
            pairs = [(f"S{k:02d}", it["summary"]) for k, it in enumerate(order)]
            labels[(p, r)] = {f"S{k:02d}": it["id"] for k, it in enumerate(order)}
            jobs.append(((p, r), math[p]["problem"], pairs))
    res = partition_jobs(jobs)
    with open(out / "partitions.jsonl", "w") as f:
        for (p, r), (groups, err, tries) in res.items():
            rec = {"idx": p, "shuffle": r, "tries": tries, "error": err, "groups": None}
            if groups is not None:
                rec["groups"] = [{"name": g.get("name", ""), "ids": [labels[(p, r)][i] for i in g["ids"]]} for g in groups]
            f.write(json.dumps(rec) + "\n")
    print(f"partitions {len(res)}, failed {sum(v[0] is None for v in res.values())}, {time.time() - t0:.0f}s", flush=True)

    # 4. controls: duplicates must share a group; two problems must not share a group
    probs = sorted(by_prob)
    cjobs, truth = [], {}
    for c in range(min(args.n_controls, len(probs))):
        p = probs[c]
        pick = rng.sample(by_prob[p], min(16, len(by_prob[p])))
        dup = pick[0]
        pairs = [(f"S{k:02d}", it["summary"]) for k, it in enumerate(pick)] + [(f"S{16 + k:02d}", dup["summary"]) for k in range(3)]
        random.Random(c).shuffle(pairs)
        cjobs.append((("dup", c), math[p]["problem"], pairs))
        truth[("dup", c)] = {"S00", "S16", "S17", "S18"}
        if len(probs) >= 2:
            q = probs[(c + len(probs) // 2) % len(probs)]
            a = rng.sample(by_prob[p], min(10, len(by_prob[p])))
            b = rng.sample(by_prob[q], min(10, len(by_prob[q])))
            pairs = [(f"A{k:02d}", it["summary"]) for k, it in enumerate(a)] + [(f"B{k:02d}", it["summary"]) for k, it in enumerate(b)]
            random.Random(c).shuffle(pairs)
            problem = f"(Two problems.)\nProblem A: {math[p]['problem']}\nProblem B: {math[q]['problem']}"
            cjobs.append((("mix", c), problem, pairs))
    cres = partition_jobs(cjobs)
    with open(out / "controls.jsonl", "w") as f:
        for (kind, c), (groups, err, tries) in cres.items():
            rec = {"kind": kind, "c": c, "error": err, "tries": tries, "groups": groups}
            if groups is not None and kind == "dup":
                rec["pass"] = any(truth[(kind, c)] <= set(g["ids"]) for g in groups)
            if groups is not None and kind == "mix":
                rec["pass"] = all(len({i[0] for i in g["ids"]}) == 1 for g in groups)
            f.write(json.dumps(rec) + "\n")
    passed = [json.loads(l).get("pass") for l in open(out / "controls.jsonl")]
    print(f"controls passed {sum(bool(x) for x in passed)}/{len(passed)}, {time.time() - t0:.0f}s", flush=True)

    # 3. triplets, both orders
    trip = []
    for p, its in by_prob.items():
        if len(its) < 3:
            continue
        for a in its:
            others = [it for it in its if it["id"] != a["id"]]
            for _ in range(args.triplets_per_anchor):
                b, c = rng.sample(others, 2)
                trip.append((p, a, b, c))
    prompts = []
    for p, a, b, c in trip:
        prompts.append(TRIPLET.format(problem=math[p]["problem"], a=a["summary"], b=b["summary"], c=c["summary"]))
        prompts.append(TRIPLET.format(problem=math[p]["problem"], a=a["summary"], b=c["summary"], c=b["summary"]))
    outs = ask(prompts, 2)
    with open(out / "triplets.jsonl", "w") as f:
        for n, (p, a, b, c) in enumerate(trip):
            first, second = outs[2 * n][:1].upper(), outs[2 * n + 1][:1].upper()
            # first asks (B=b, C=c); second asks (B=c, C=b); consistent when the two answers pick the same item
            pick1 = {"B": b["id"], "C": c["id"]}.get(first)
            pick2 = {"B": c["id"], "C": b["id"]}.get(second)
            f.write(json.dumps({"idx": p, "a": a["id"], "b": b["id"], "c": c["id"], "pick1": pick1, "pick2": pick2,
                                "consistent": pick1 is not None and pick1 == pick2}) + "\n")
    print(f"triplets {len(trip)}, {time.time() - t0:.0f}s", flush=True)
    (out / "meta.json").write_text(json.dumps({"judge": JUDGE, "gen": args.gen, "n_gen": len(gens), "dry": args.dry,
                                               "shuffles": args.shuffles, "seconds": time.time() - t0}, indent=1))
