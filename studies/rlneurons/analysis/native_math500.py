"""native readout on MATH-500 (specs/SPEC_native.md): Think-SFT in its own chat format, cap 32,768, counted also at 16,384, against
each of the four stored Think-SFT cue samples at cap 16,384 (results/thinkvote/math500_sft1_cue_s4-01/rows.jsonl), paired.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.native_math500 <joined native run>

Writes results/native/math500-01/ (run.json, metrics.json, readout.json, examples.json).
"""
import collections
import json
import pathlib
import shutil
import sys

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
OUT, OLD, run = STUDY / "results" / "native" / "math500-01", 16384, sys.argv[1]
m = json.loads(pathlib.Path(f"runs/{run}/metrics.json").read_text())
assert m["status"] == "done" and m["config"]["prompt"] == "native" and m["config"]["set"] == "math500" and m["config"]["max_tokens"] == 32768
n = {r["problem_index"]: r for r in map(json.loads, open(f"runs/{run}/answers.jsonl"))}
idx = sorted(n)
assert len(idx) == 500
cue = collections.defaultdict(dict)
for r in map(json.loads, open(STUDY / "results" / "thinkvote" / "math500_sft1_cue_s4-01" / "rows.jsonl")):
    if r["attempt"] == 0:
        cue[r["sample"]][r["problem_index"]] = r
v32 = [n[i]["score_v3"] for i in idx]
v16 = [n[i]["score_v3"] if n[i]["n_new"] <= OLD and not n[i]["cap_hit"] else 0 for i in idx]
out = {"spec": "studies/rlneurons/specs/SPEC_native.md", "set": "math500", "n": 500, "native_run": run,
       "native": {"right_at_32768": sum(v32), "right_at_16384_same_answers": sum(v16), "answers_longer_than_16384": sum(n[i]["n_new"] > OLD for i in idx),
                  "cap_hits_at_32768": sum(n[i]["cap_hit"] for i in idx), "tokens_per_problem_at_32768": round(sum(n[i]["n_new"] for i in idx) / 500, 1),
                  "tokens_per_problem_at_16384": round(sum(min(n[i]["n_new"], OLD) for i in idx) / 500, 1)},
       "cue_samples_at_16384": {}}
for s in sorted(cue):
    c = [cue[s][i]["score_v3"] for i in idx]
    lo, hi = S.paired_bootstrap(v16, c, n_boot=10000, seed=0)
    out["cue_samples_at_16384"][str(s)] = {"right": sum(c), "cap_hits": sum(cue[s][i]["cap_hit"] for i in idx), "tokens_per_problem": round(sum(cue[s][i]["n_new"] for i in idx) / 500, 1),
                                          "native_at_16384_minus_cue": {"points": round(100 * (sum(v16) - sum(c)) / 500, 2), "ci95": [round(lo, 2), round(hi, 2)]}}
OUT.mkdir(parents=True)
shutil.copy(f"runs/{run}/metrics.json", OUT / "metrics.json")
(OUT / "run.json").write_text(json.dumps({"run": run, "commit": m["commit"], "config": m["config"],
                                          "raw_answers": f"runs/{run}/answers.jsonl (ih get of the shard jobs, then shard_join; not in git)"}, indent=1) + "\n")
(OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
ex = lambda r: {k: r[k] for k in ("problem_index", "gold", "extracted_v3", "score_v3", "n_new", "cap_hit")} | {"prompt_tail": r["prompt"][-300:], "answer_head": r["text"][:300], "answer_tail": r["text"][-800:]}
(OUT / "examples.json").write_text(json.dumps({"right": ex(next(n[i] for i in idx if n[i]["score_v3"])), "wrong": ex(next(n[i] for i in idx if not n[i]["score_v3"]))}, indent=1) + "\n")
print(json.dumps(out, indent=1))
