"""One gapmap cell: the difference T2 (RL, T 1.0) minus T1 (cued base, T 1.0) on MATH-500 for one metric, by one split,
with a paired bootstrap interval over problems.

  python studies/gapmap/jobs/cell.py --cells studies/gapmap/cells/<batch>.json --cell <id> [--data <per_problem.json>]

Reads the 500 per-problem rows of studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json (grader v3).
Writes $OUT_DIR/metrics.json and, for fmt csv, $OUT_DIR/table.csv.
"""
import argparse
import csv
import json
import os
import time
from pathlib import Path

import numpy as np

DATA = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def stamp(text):
    print(f"[cell] {time.strftime('%H:%M:%S', time.gmtime())} {text}", flush=True)


def values(rows, metric):
    """The rows a metric uses, and each row's T1 and T2 value."""
    if metric == "accuracy":
        return rows, [r["t1_right"] for r in rows], [r["t2_right"] for r in rows]
    if metric == "cap_hit":
        return rows, [r["t1_cap_hit"] for r in rows], [r["t2_cap_hit"] for r in rows]
    if metric == "tokens":
        return rows, [r["t1_generated_tokens"] for r in rows], [r["t2_generated_tokens"] for r in rows]
    if metric == "tokens_both_right":
        both = [r for r in rows if r["cell"] == "both"]
        return both, [r["t1_generated_tokens"] for r in both], [r["t2_generated_tokens"] for r in both]
    raise KeyError(f"unknown metric {metric}")


def quartile(rows, key):
    edges = np.quantile([r[key] for r in rows], [0.25, 0.5, 0.75])
    return [f"q{1 + int(np.searchsorted(edges, r[key], side='left'))}" for r in rows]


def labels(rows, split):
    if split == "overall":
        return ["all"] * len(rows)
    if split == "subject":
        return [r["subject"] for r in rows]
    if split == "level5":
        return ["level5" if r["level5"] else "level1-4" for r in rows]
    if split == "t2_length_quartile":
        return quartile(rows, "t2_generated_tokens")
    if split == "t1_length_quartile":
        return quartile(rows, "t1_generated_tokens")
    raise KeyError(f"unknown split {split}")


def bootstrap(t1, t2, group, n_boot, seed):
    """Resample problems with replacement n_boot times; per group, the mean of T2 minus T1 in each resample."""
    names = sorted(set(group))
    member = np.array([[g == name for name in names] for g in group], dtype=np.float64)
    difference = (np.array(t2, dtype=np.float64) - np.array(t1, dtype=np.float64))[:, None] * member
    rng = np.random.default_rng(seed)
    n = len(group)
    means = []
    for start in range(0, n_boot, 20000):
        counts = rng.multinomial(n, np.full(n, 1 / n), size=min(20000, n_boot - start)).astype(np.float64)
        means.append((counts @ difference) / (counts @ member))
    point = difference.sum(0) / member.sum(0)
    return names, member.sum(0), point, np.concatenate(means)


def write_json(path, table):
    path.with_name("table.json").write_text(json.dumps(table, indent=1))


def write_csv(path, table):
    with open(path.with_name("table.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)


WRITERS = {"json": write_json, "csv": write_csv}


def validate(cell):
    """Every setting is checked before any work starts."""
    assert cell["kind"] in ("split", "bench"), f"kind {cell['kind']!r}"
    if cell["kind"] == "split":
        assert 0 < cell["ci"] < 1, f"ci must be a fraction between 0 and 1, got {cell['ci']!r}"
        assert cell["fmt"] in WRITERS, f"fmt must be one of {sorted(WRITERS)}, got {cell['fmt']!r}"
        assert isinstance(cell["digits"], int), f"digits must be an integer, got {cell['digits']!r}"
        assert isinstance(cell["n_boot"], int) and cell["n_boot"] > 0, f"n_boot {cell['n_boot']!r}"


def split_cell(cell, rows):
    rows, t1, t2 = values(rows, cell["metric"])
    group = labels(rows, cell["split"])
    stamp(f"bootstrap start: metric {cell['metric']}, split {cell['split']}, {len(rows)} problems, {cell['n_boot']} resamples")
    began = time.time()
    names, sizes, point, means = bootstrap(t1, t2, group, cell["n_boot"], cell["seed"])
    seconds = time.time() - began
    stamp(f"bootstrap done in {seconds:.1f} s")
    low, high = np.quantile(means, [(1 - cell["ci"]) / 2, (1 + cell["ci"]) / 2], axis=0)
    table = [{"group": name, "n": int(size), "t2_minus_t1": round(float(p), cell["digits"]),
              "low": round(float(lo), cell["digits"]), "high": round(float(hi), cell["digits"])}
             for name, size, p, lo, hi in zip(names, sizes, point, low, high)]
    out = Path(os.environ["OUT_DIR"]) / "metrics.json"
    WRITERS[cell["fmt"]](out, table)
    return {"table": table, "ci": cell["ci"], "seconds": {"bootstrap": round(seconds, 1)}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", required=True)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--data", default=DATA)
    args = parser.parse_args()
    cell = next(c for c in json.loads(Path(args.cells).read_text()) if c["id"] == args.cell)
    stamp(f"cell {cell['id']} from {args.cells}")
    validate(cell)
    if cell["kind"] == "bench":
        from studies.gapmap.jobs import bench_rng
        result = bench_rng.run(cell)
    else:
        rows = json.loads(Path(args.data).read_text())
        stamp(f"loaded {len(rows)} rows from {args.data}")
        result = split_cell(cell, rows)
    out = Path(os.environ["OUT_DIR"]) / "metrics.json"
    out.write_text(json.dumps({"cell": cell, **result}, indent=1))
    for row in result["table"]:
        stamp("result " + json.dumps(row))
    stamp(f"wrote {out}")


if __name__ == "__main__":
    main()
