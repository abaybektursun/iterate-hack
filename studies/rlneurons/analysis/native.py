"""native readout (specs/SPEC_native.md): Think-SFT in its own chat format against Think-SFT with the raw template and the cue,
on the 328, both at cap 32,768 and at 16,384 counted from the same answers, paired by problem.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.native <joined native run>

Inputs: runs/<joined native run>/ (analysis/shard_join.py over the shard jobs) and the cue cell of results/cap32
(runs/abaybektursun-1115-005756-309b/). Writes results/native/hard328-01/ (run.json, metrics.json, readout.json, examples.json).
"""
import json
import pathlib
import shutil
import sys

from studies.rlneurons.lib import n13_score as S

OUT = pathlib.Path(__file__).resolve().parents[1] / "results" / "native" / "hard328-01"
CUE, OLD = "abaybektursun-1115-005756-309b", 16384
run = sys.argv[1]
load = lambda j: {r["problem_index"]: r for r in map(json.loads, open(f"runs/{j}/answers.jsonl"))}
m = json.loads(pathlib.Path(f"runs/{run}/metrics.json").read_text())
assert m["status"] == "done" and m["config"]["prompt"] == "native" and m["config"]["set"] == "hard328" and m["config"]["max_tokens"] == 32768
a, b = load(run), load(CUE)
idx = sorted(a)
assert idx == sorted(b) and len(idx) == 328
at = lambda rows, cap: [rows[i]["score_v3"] if cap is None or (rows[i]["n_new"] <= cap and not rows[i]["cap_hit"]) else 0 for i in idx]
out = {"spec": "studies/rlneurons/specs/SPEC_native.md", "set": "hard328", "n": 328, "native_run": run, "native_jobs": m.get("job_ids"), "cue_job": CUE}
for name, cap in (("cap_32768", None), ("cap_16384", OLD)):
    va, vb = at(a, cap), at(b, cap)
    lo, hi = S.paired_bootstrap(va, vb, n_boot=10000, seed=0)
    tok = lambda rows: round(sum(min(rows[i]["n_new"], cap or 10**9) for i in idx) / 328, 1)
    out[name] = {"native_right": sum(va), "cue_right": sum(vb), "native_minus_cue": {"problems": sum(va) - sum(vb), "points": round(100 * (sum(va) - sum(vb)) / 328, 2),
                                                                                    "ci95": [round(lo, 2), round(hi, 2)]},
                 "only_native": sum(x and not y for x, y in zip(va, vb)), "only_cue": sum(y and not x for x, y in zip(va, vb)),
                 "native_tokens_per_problem": tok(a), "cue_tokens_per_problem": tok(b)}
out["native"] = {"answers_longer_than_16384": sum(a[i]["n_new"] > OLD for i in idx), "cap_hits_at_32768": sum(a[i]["cap_hit"] for i in idx),
                 "ended_im_end": sum(a[i]["ended_im_end"] for i in idx), "with_think_close": sum("</think>" in a[i]["text"] for i in idx)}
OUT.mkdir(parents=True)
shutil.copy(f"runs/{run}/metrics.json", OUT / "metrics.json")
(OUT / "run.json").write_text(json.dumps({"run": run, "job_ids": m.get("job_ids"), "commit": m["commit"], "config": m["config"],
                                          "raw_answers": f"runs/{run}/answers.jsonl (ih get of the shard jobs, then shard_join; not in git)"}, indent=1) + "\n")
(OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
ex = lambda r: {k: r[k] for k in ("problem_index", "gold", "extracted_v3", "score_v3", "n_new", "cap_hit")} | {"prompt_tail": r["prompt"][-300:], "answer_head": r["text"][:300], "answer_tail": r["text"][-800:]}
(OUT / "examples.json").write_text(json.dumps({"right": ex(next(a[i] for i in idx if a[i]["score_v3"])),
                                               "wrong": ex(next(a[i] for i in idx if not a[i]["score_v3"] and not a[i]["cap_hit"]))}, indent=1) + "\n")
print(json.dumps(out, indent=1))
