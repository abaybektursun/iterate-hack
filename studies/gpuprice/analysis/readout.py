"""Readout of scorer reports: one run folder with run.json, metrics.json and examples.json.

python3 studies/gpuprice/analysis/readout.py <dir with report_*.json and cells_*.csv> <new run folder> "<command>"
"""
import csv, glob, json, os, subprocess, sys

src, out, command = sys.argv[1:4]
os.makedirs(out)  # fails if the run folder exists: a rerun gets the next number

metrics = {}
for path in sorted(glob.glob(f"{src}/report_*.json") + glob.glob(f"{src}/backtest/report_*.json")):
    r = json.load(open(path))
    if r["status"] == "refused":
        continue
    name = os.path.relpath(path, src)[:-5].replace("report_", "")
    metrics[name] = {"mode": r["mode"], "cutoff": r["cutoff"], "cells": r["cells"], "inputs": r["inputs"],
                     "overall": r["overall"], "by_horizon": r["by_horizon"]}
assert metrics, f"no scored report in {src}"
json.dump(metrics, open(f"{out}/metrics.json", "w"), indent=1)

examples = {}
for path in sorted(glob.glob(f"{src}/cells_*.csv")):
    rows = [r for r in csv.DictReader(open(path)) if r["status"] == "scored"]
    gain = lambda r: float(r["baseline_loss"]) - float(r["loss"])
    examples[os.path.basename(path)[6:-4]] = {"best_cell": max(rows, key=gain), "worst_cell": min(rows, key=gain)}
json.dump(examples, open(f"{out}/examples.json", "w"), indent=1)

commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
json.dump({"commit": commit, "command": command, "job_id": "laptop (no GPU)", "source_dir": src},
          open(f"{out}/run.json", "w"), indent=1)
for name, m in metrics.items():
    o = m["overall"]
    print(f"{name}: cells {o['n_cells']} pinball {o['pinball']} baseline {o['baseline_pinball']} "
          f"skill pooled {o['skill_pooled']} median {o['skill_median_of_series']} geomean {o['skill_geomean']}")
