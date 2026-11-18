"""Summary of the label pilot (specs/label-pilot.md), laptop, no model.

    python3 studies/explore/analysis/label_pilot_summary.py

Reads runs/explore/<task>/label-pilot-01[-<model>]/rows.jsonl and writes results/label/pilot-01/summary.json: every
call without its reply text (label condition, kind, assigned method, ranking, score, similarity to A and B, idea,
tokens, USD), plus one saved example per model and task. Prints the rankings and the free calls.
"""
import json
import pathlib
import shutil

root = pathlib.Path(__file__).resolve().parents[3]
out = root / "studies/explore/results/label/pilot-01"
out.mkdir(parents=True, exist_ok=True)
summary = []
for d in sorted((root / "runs/explore").glob("*/label-pilot-01*")):
    if not (d / "rows.jsonl").exists():
        continue
    run = json.loads((d / "run.json").read_text())
    for l in open(d / "rows.jsonl"):
        r = json.loads(l)
        reply = r.pop("reply")
        r.pop("msg", None)
        if r["kind"] == "rank":
            r["ranking"] = json.loads(reply[reply.find("{"):reply.rfind("}") + 1])["ranking"]
        summary.append({"model": run["model"], "commit": run["commit"], **r})
        if r["kind"] == "free" and r["id"] == "c002" and (d / "code/c002.py").exists():
            shutil.copy(d / "code/c002.py", out / f"example_free_{run['task']}_{run['model']}_c002.py")
(out / "summary.json").write_text(json.dumps(summary, indent=1))
for r in summary:
    if r["kind"] == "rank":
        print(r["task"], r["model"], "current", r["current"], "ranking", "".join(r["ranking"]))
    elif r["kind"] == "free":
        print(f"   free: score {r.get('score')} sim A {r.get('sim_A')} B {r.get('sim_B')} built_on {r.get('built_on')}")
print("USD", round(sum(r["usd"] for r in summary), 2), "calls", len(summary))
