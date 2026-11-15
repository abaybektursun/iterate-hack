"""Compare strategy arms of one experiment folder (laptop, no model).

    python3 -m studies.explore.analysis.compare runs/explore/circles26/pilot-01

Each subfolder <arm>-s<seed> holds log.jsonl and metrics.json from jobs/run_strategy.py. Prints, per arm: final best
validation score per seed, mean, valid share, cost, and the best-so-far curve at a few budget points. Writes
compare.json next to the runs. Runs without metrics.json (still running or crashed) are listed and left out.
"""
import json
import pathlib
import statistics
import sys
from collections import defaultdict

d = pathlib.Path(sys.argv[1])
arms, missing = defaultdict(list), []
for run in sorted(p for p in d.iterdir() if p.is_dir()):
    if not (run / "metrics.json").exists():
        missing.append(run.name)
        continue
    m = json.loads((run / "metrics.json").read_text())
    rows = [json.loads(l) for l in open(run / "log.jsonl")]
    best, curve = None, []
    for r in rows:
        if r["valid"] and r["score"] is not None:
            best = r["score"] if best is None else max(best, r["score"])
        curve.append(best)
    arms[m["strategy"]].append({"seed": m["seed"], "best": m["best_val"], "n": m["n"], "valid_share": m["valid_share"],
                                "usd": m["spent"]["usd"], "curve": curve,
                                "ideas": [r["idea"] for r in rows]})

out = {}
for arm, runs in arms.items():
    finals = [r["best"] for r in runs if r["best"] is not None]
    n = min(len(r["curve"]) for r in runs)
    pts = [p for p in (5, 10, 15, 20, 25, 30, 40, 60) if p <= n]
    out[arm] = {"seeds": len(runs), "finals": [r["best"] for r in runs], "mean": statistics.mean(finals) if finals else None,
                "valid_share": statistics.mean(r["valid_share"] for r in runs), "usd": sum(r["usd"] for r in runs),
                "curve_mean": {p: statistics.mean([r["curve"][p - 1] or 0 for r in runs]) for p in pts}}
    print(f"{arm:9s} seeds={len(runs)} finals={out[arm]['finals']} mean={out[arm]['mean']} valid={out[arm]['valid_share']:.2f} "
          f"${out[arm]['usd']:.3f} curve={ {p: round(v, 3) for p, v in out[arm]['curve_mean'].items()} }")
if missing:
    print("no metrics.json (running or crashed):", missing)
(d / "compare.json").write_text(json.dumps({"arms": out, "missing": missing, "runs": arms}, indent=1))
