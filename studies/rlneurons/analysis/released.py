"""released readout (specs/SPEC_released.md): Think-SFT in its own chat format at T 0.6 / top-p 0.95 against the same format at
T 1.0 / top-p 1.0 (results/native), same seeds, paired by problem, at cap 32,768 and at 16,384 counted from the same answers.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.released <set> <T 0.6 run> <joined T 1.0 run> [<name>]

<set>: hard328 or math500. Inputs in runs/ (ih get of the shard jobs, then analysis/shard_join.py). With <name> the T 0.6 run may be one
shard: the T 1.0 cell is read on that shard's problems only. Writes results/released/<name or set>-01/ (run.json, metrics.json, readout.json, examples.json).
"""
import json
import pathlib
import shutil
import sys

from studies.rlneurons.lib import n13_score as S

bench, run, ref = sys.argv[1:4]
name = sys.argv[4] if len(sys.argv) > 4 else bench         # a run of one shard is compared on its own problems
OUT, OLD = pathlib.Path(__file__).resolve().parents[1] / "results" / "released" / f"{name}-01", 16384
load = lambda j: {r["problem_index"]: r for r in map(json.loads, open(f"runs/{j}/answers.jsonl"))}
m, mr = (json.loads(pathlib.Path(f"runs/{j}/metrics.json").read_text()) for j in (run, ref))
same = lambda c: {k: c[k] for k in ("prompt", "set", "max_tokens", "seed", "native_tokenizer", "samples")}
assert m["status"] == "done" and m["config"]["set"] == bench and m["config"]["prompt"] == "native" and m["config"]["max_tokens"] == 32768
assert (m["config"]["temperature"], m["config"]["top_p"], mr["config"]["temperature"], mr["config"]["top_p"]) == (0.6, 0.95, 1.0, 1.0)
assert same(m["config"]) == same(mr["config"]), "the two cells differ in more than the sampling setting"
a, b = load(run), load(ref)
idx = sorted(a)
assert set(idx) <= set(b)
n = len(idx)
at = lambda rows, cap: [rows[i]["score_v3"] if cap is None or (rows[i]["n_new"] <= cap and not rows[i]["cap_hit"]) else 0 for i in idx]
out = {"spec": "studies/rlneurons/specs/SPEC_released.md", "set": bench, "n": n, "t06_run": run, "t10_run": ref, "shard": m["config"].get("shard")}
for name, cap in (("cap_32768", None), ("cap_16384", OLD)):
    va, vb = at(a, cap), at(b, cap)
    lo, hi = S.paired_bootstrap(va, vb, n_boot=10000, seed=0)
    tok = lambda rows: round(sum(min(rows[i]["n_new"], cap or 10**9) for i in idx) / n, 1)
    out[name] = {"t06_right": sum(va), "t10_right": sum(vb), "t06_minus_t10": {"problems": sum(va) - sum(vb), "points": round(100 * (sum(va) - sum(vb)) / n, 2),
                                                                             "ci95": [round(lo, 2), round(hi, 2)]},
                 "only_t06": sum(x and not y for x, y in zip(va, vb)), "only_t10": sum(y and not x for x, y in zip(va, vb)),
                 "t06_tokens_per_problem": tok(a), "t10_tokens_per_problem": tok(b)}
for k, rows, mm in (("t06", a, m), ("t10", b, mr)):
    out[k] = {"answers_longer_than_16384": sum(rows[i]["n_new"] > OLD for i in idx), "cap_hits_at_32768": sum(rows[i]["cap_hit"] for i in idx),
              "loop_A": mm["counts"]["loop_A"]}
OUT.mkdir(parents=True)
shutil.copy(f"runs/{run}/metrics.json", OUT / "metrics.json")
(OUT / "run.json").write_text(json.dumps({"run": run, "commit": m["commit"], "config": m["config"],
                                          "raw_answers": f"runs/{run}/answers.jsonl (ih get of the shard jobs, then shard_join; not in git)"}, indent=1) + "\n")
(OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
ex = lambda r: {k: r[k] for k in ("problem_index", "gold", "extracted_v3", "score_v3", "n_new", "cap_hit")} | {"prompt_tail": r["prompt"][-300:], "answer_head": r["text"][:300], "answer_tail": r["text"][-800:]}
(OUT / "examples.json").write_text(json.dumps({"right": ex(next(a[i] for i in idx if a[i]["score_v3"])), "wrong": ex(next(a[i] for i in idx if not a[i]["score_v3"]))}, indent=1) + "\n")
print(json.dumps(out, indent=1))
