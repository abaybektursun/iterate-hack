"""Compare strategy arms of one experiment folder (laptop, no model).

    python3 -m studies.explore.analysis.compare runs/explore/circles26/main-01

Each subfolder <arm>-s<seed> holds log.jsonl and metrics.json from jobs/run_strategy.py. Prints, per arm:
- submission-matched: final best validation score per seed, mean, runs that beat the starter, best-so-far curve;
- dollar-matched: best score of each run after the same spend, the smallest total spend of any run (so every run
  is cut at a dollar amount it reached), plus the curve at fixed dollar points;
- optimizer share: submissions whose code calls a numerical optimizer (regex OPT, a proxy, not the basin judge).
Writes compare.json next to the runs. Runs without metrics.json (still running or crashed) are listed and left out.
"""
import json
import pathlib
import re
import statistics
import sys
from collections import defaultdict

from studies.explore.lib.loop import PRICES

OPT = re.compile(r"scipy|minimize|SLSQP|gradient|anneal|penalty")  # the pilot-02 regex, case-sensitive


def best_until(rows, ok):
    b = None
    for r in rows:
        if ok(r) and r["valid"] and r["score"] is not None:
            b = r["score"] if b is None else max(b, r["score"])
    return b


d = pathlib.Path(sys.argv[1])
arms, missing = defaultdict(list), []
for run in sorted(p for p in d.iterdir() if p.is_dir()):
    if not (run / "metrics.json").exists():
        missing.append(run.name)
        continue
    m = json.loads((run / "metrics.json").read_text())
    pin, pout = PRICES.get(m["model"], (0.0, 0.0))  # devin: models are plan quota, priced 0
    rows = [json.loads(l) for l in open(run / "log.jsonl")]
    usd, curve, best = 0.0, [], None
    for r in rows:
        usd += r["prompt_tokens"] / 1e6 * pin + r["completion_tokens"] / 1e6 * pout
        r["usd_cum"] = usd
        if r["valid"] and r["score"] is not None:
            best = r["score"] if best is None else max(best, r["score"])
        curve.append(best)
    opt = 0
    for r in rows:
        f = run / "code" / f"{r['id']}.py"
        opt += bool(f.exists() and OPT.search(f.read_text()))
    arms[m["strategy"]].append({"seed": m["seed"], "best": m["best_val"], "starter": m.get("starter_score"),
                                "n": m["n"], "valid_share": m["valid_share"], "usd": usd, "curve": curve,
                                "rows": rows, "optimizer": opt})

all_runs = [r for runs in arms.values() for r in runs]
cut = min(r["usd"] for r in all_runs)  # every run reached this spend
usd_pts = [round(cut * f, 4) for f in (0.25, 0.5, 0.75, 1.0)]
out = {"usd_cut": cut}
for arm, runs in sorted(arms.items()):
    finals = [r["best"] for r in runs if r["best"] is not None]
    n = min(len(r["curve"]) for r in runs)
    pts = [p for p in (5, 10, 15, 20, 25, 30, 40, 60) if p <= n]
    at_cut = [best_until(r["rows"], lambda x: x["usd_cum"] <= cut) for r in runs]
    o = {"seeds": len(runs), "finals": [r["best"] for r in runs], "mean": statistics.mean(finals) if finals else None,
         "beat_starter": sum((r["best"] or 0) > (r["starter"] or 0) for r in runs),
         "usd_matched": at_cut, "usd_matched_mean": statistics.mean(x or 0 for x in at_cut),
         "valid_share": statistics.mean(r["valid_share"] for r in runs),
         "optimizer": f"{sum(r['optimizer'] for r in runs)}/{sum(r['n'] for r in runs)}",
         "usd_total": sum(r["usd"] for r in runs), "usd_per_run": statistics.mean(r["usd"] for r in runs),
         "curve_mean": {p: statistics.mean([r["curve"][p - 1] or 0 for r in runs]) for p in pts},
         "usd_curve_mean": {p: statistics.mean([best_until(r["rows"], lambda x: x["usd_cum"] <= p) or 0 for r in runs])
                            for p in usd_pts}}
    out[arm] = o
    print(f"{arm:9s} seeds={o['seeds']} finals={o['finals']} mean={o['mean'] and round(o['mean'], 4)} "
          f"beat_starter={o['beat_starter']}/{o['seeds']} | at ${cut:.3f}: {[x and round(x, 4) for x in at_cut]} "
          f"mean={o['usd_matched_mean']:.4f} | optimizer={o['optimizer']} valid={o['valid_share']:.2f} "
          f"$/run={o['usd_per_run']:.3f}\n          curve={ {p: round(v, 3) for p, v in o['curve_mean'].items()} }")
if missing:
    print("no metrics.json (running or crashed):", missing)
for runs in arms.values():
    for r in runs:
        r.pop("rows")
(d / "compare.json").write_text(json.dumps({"arms": out, "missing": missing, "runs": arms}, indent=1))
