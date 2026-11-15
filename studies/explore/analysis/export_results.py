"""Copy the small files of one experiment from runs/ into results/ (laptop, no model).

    python3 studies/explore/analysis/export_results.py <task> <experiment> <best run> <run with an invalid program>

Run analysis/compare.py on the experiment first. Writes to results/<task>/<experiment>/: compare.json, runs.json
(run.json and metrics.json of every run), each run's assignments.json / prunes.json / rebases.json, and examples.json
with the program files of the best submission of <best run> and the first invalid submission of the other run.
"""
import json
import pathlib
import shutil
import sys

task, exp, good, bad = sys.argv[1:5]
root = pathlib.Path(__file__).resolve().parents[3]
src, dst = root / "runs" / "explore" / task / exp, root / "studies" / "explore" / "results" / task / exp
dst.mkdir(parents=True, exist_ok=True)
shutil.copy(src / "compare.json", dst / "compare.json")
runs = {}
for d in sorted(p for p in src.iterdir() if p.is_dir()):
    runs[d.name] = {"run": json.loads((d / "run.json").read_text()), "metrics": json.loads((d / "metrics.json").read_text())}
    for f in ("assignments.json", "prunes.json", "rebases.json"):
        if (d / f).exists():
            shutil.copy(d / f, dst / f"{d.name}_{f}")
(dst / "runs.json").write_text(json.dumps(runs, indent=1))
g = [json.loads(l) for l in open(src / good / "log.jsonl")]
b = [json.loads(l) for l in open(src / bad / "log.jsonl")]
best = max((r for r in g if r["valid"]), key=lambda r: r["score"])
inv = next(r for r in b if not r["valid"] and (src / bad / "code" / f"{r['id']}.py").exists())
shutil.copy(src / good / "code" / f"{best['id']}.py", dst / f"example_best_{good}-{best['id']}.py")
shutil.copy(src / bad / "code" / f"{inv['id']}.py", dst / f"example_invalid_{bad}-{inv['id']}.py")
keys = ("id", "branch", "idea", "score", "msg")
(dst / "examples.json").write_text(json.dumps({"scored_right": {"run": good, **{k: best[k] for k in keys}},
                                               "scored_wrong": {"run": bad, **{k: inv[k] for k in keys}}}, indent=1))
