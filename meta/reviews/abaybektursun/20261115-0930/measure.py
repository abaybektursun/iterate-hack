# python3 meta/reviews/abaybektursun/20261115-0930/measure.py ../iterate-hack-critic/runs > meta/reviews/abaybektursun/20261115-0930/before.txt
# Generated tokens per second of studies/rlneurons/jobs/prefix_cell.py, per arm, over all jobs of the arm (first run and the
# --start reruns after out-of-memory), from each job's metrics.json (counts.generated_tokens, seconds) and log (exit line).
# Reference: the study's vLLM engine (rln4_gen.VllmEngine) on prefix continuations of the same base model, handoff_gen job
# abaybektursun-1114-231144-7399 (studies/rlneurons/results/handoff/base-01/metrics.json, Modal H100, cap 16,384).
import json
import pathlib
import sys

runs = pathlib.Path(sys.argv[1])
arms = {"base a0": ["1114-233600-a2de", "1115-003715-63e3", "1115-010036-d67f"],
        "rl a0": ["1114-233015-cfe4", "1115-005330-92a1", "1115-011756-7a57"],
        "base a1 shard 0": ["1114-233319-30c3", "1115-002653-1aca"],
        "base a1 shard 1": ["1114-233354-0eee", "1115-002824-da52"],
        "base a1 shard 2": ["1114-233541-1444", "1115-002559-7900"]}
print("arm  jobs  out-of-memory exits  rows  cap hits  generated tokens  seconds  tokens/s  batch sizes")
for arm, jobs in arms.items():
    tok = sec = n = cap = oom = 0
    batches = []
    for j in jobs:
        d = runs / f"abaybektursun-{j}"
        m = json.loads((d / "metrics.json").read_text())
        tok += m["counts"]["generated_tokens"]
        sec += m["seconds"]
        n += m["counts"]["n"]
        cap += m["counts"]["cap_hits"]
        oom += "OutOfMemoryError" in (d / "log").read_text()
        batches.append(m["config"]["batch"])
    print(f"{arm}  {len(jobs)}  {oom}  {n}  {cap}  {tok}  {sec:.0f}  {tok / sec:.0f}  {batches}")
h = json.loads(pathlib.Path("studies/rlneurons/results/handoff/base-01/metrics.json").read_text())["counts"]
print(f"reference vLLM handoff_gen base finisher: {h['n']} rows, {h['cap_hits']} cap hits, {h['generated_tokens']} tokens, "
      f"{h['generation_s']:.0f} s, {h['tokens_per_s']:.0f} tokens/s")
