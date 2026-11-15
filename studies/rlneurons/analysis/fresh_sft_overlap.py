"""Fresh set against the Think-SFT training data (allenai/Dolci-Think-SFT-7B, every message of every row): the scan of
analysis/wsp1_sft_overlap.py --turns all (its Scanner, shard loop and merge, imported) with the test items replaced by
data/fresh/fresh2026_v1.json. Laptop, no model; downloads each shard to --tmp, scans it and deletes it (36 GB in all).

    PYTHONPATH=. uv run --no-project --with huggingface_hub --with pyarrow --with numpy \
        python -m studies.rlneurons.analysis.fresh_sft_overlap --tmp <dir outside the repo> --out studies/rlneurons/results/fresh/sft_overlap-01

Controls scanned with the set, which must come out as stated or the run stops: hard/0 and hard/38 of data/rln3/hard.json are
`exact` in results/wsp1/sft_overlap-03 and must be flagged here. Also scanned and reported, not part of the set: aime2026/1, the
candidate dropped as published before 2026 (2020 Purple Comet). Writes run.json, metrics.json and flags.json to --out.
"""
import argparse
import collections
import datetime
import json
import multiprocessing
import os
import subprocess
import time

from studies.rlneurons.analysis import wsp1_sft_overlap as W

FRESH = f"{W.STUDY}/data/fresh/fresh2026_v1.json"
PATRICK = ("Patrick started walking at a constant rate along a straight road from school to the park. One hour after Patrick left, "
           "Tanya started running along the same road from school to the park. One hour after Tanya left, Jose started bicycling "
           "along the same road from school to the park. Tanya ran at a constant rate of $2$ miles per hour faster than Patrick "
           "walked, Jose bicycled at a constant rate of $7$ miles per hour faster than Tanya ran, and all three arrived at the park "
           "at the same time.")           # the statement up to its last sentence; MathArena/aime_2026 problem_idx 1
MUST_FLAG = ("control/hard0", "control/hard38")


def test_items():
    hard = json.load(open(W.HARD))
    return ([(f"fresh/{it['index']}", it["problem"]) for it in json.load(open(FRESH))]
            + [("control/hard0", hard[0]["problem"]), ("control/hard38", hard[38]["problem"]), ("dropped/aime2026_1", PATRICK)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tmp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    assert not os.path.exists(a.out), f"{a.out} exists; a rerun gets the next number"
    os.makedirs(a.tmp, exist_ok=True)
    W.test_items = test_items                       # the pool forks, so the workers see this
    t0 = time.time()
    files, sizes, total_rows = W.dataset_files()
    parts = []
    with multiprocessing.get_context("fork").Pool(a.workers, W.init_worker, (a.tmp, t0 + 1e9, files, "all")) as pool:
        for p in pool.imap_unordered(W.scan_shard, range(len(files))):
            parts.append(p)
            print(f"{time.time() - t0:6.0f} s  shard {p['shard']:3d}  rows {p['rows']:6d}  hits { {r: len(b) for r, b in p['best'].items()} }", flush=True)
    rows = sum(p["rows"] for p in parts)
    assert len(parts) == len(files) and rows == total_rows, (len(parts), rows, total_rows)
    by_role = {r: W.merge([{"shard": p["shard"], "best": p["best"][r], "short": {}} for p in parts])[0] for r in W.ROLES}
    flags = {}
    for key, _ in test_items():
        f = {"flag": "none", "share": 0.0, "by_role": {}}
        for r in W.ROLES:
            b = by_role[r].get(key)
            if b and b["share"] > f["share"]:
                f["share"] = round(b["share"], 3)
            if W.flag_of(b) != "none":
                f["by_role"][r] = {"flag": W.flag_of(b), "share": round(b["share"], 3), "evidence": b["evidence"],
                                   "rows_near": b["rows_near"], "rows_exact": b["rows_exact"]}
        got = {x["flag"] for x in f["by_role"].values()}
        f["flag"] = "exact" if "exact" in got else "near" if got else "none"
        flags[key] = f
    assert all(flags[k]["flag"] != "none" for k in MUST_FLAG), "a control that is in the training data was not flagged"
    src = {f"fresh/{it['index']}": it["unique_id"] for it in json.load(open(FRESH))}
    fresh = {k: f for k, f in flags.items() if k in src}
    metrics = {"dataset": W.DATASET, "revision": W.REVISION, "rows_scanned": rows, "shards_scanned": len(parts), "complete": True,
               "rule": "rln3_overlap.norm/grams, every message, each role apart (wsp1_sft_overlap --turns all)",
               "fresh2026_v1": {"n": len(fresh), **dict(collections.Counter(f["flag"] for f in fresh.values())),
                                "flagged": {src[k]: f["flag"] for k, f in fresh.items() if f["flag"] != "none"},
                                "largest_share": max(f["share"] for f in fresh.values())},
               "controls": {k: flags[k]["flag"] for k in flags if k not in src}}
    os.makedirs(a.out)
    json.dump({"command": "python -m studies.rlneurons.analysis.fresh_sft_overlap --tmp <tmp> --out " + a.out, "where": "laptop, CPU only",
               "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "wall_s": round(time.time() - t0),
               "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}, open(f"{a.out}/run.json", "w"), indent=1)
    json.dump(metrics, open(f"{a.out}/metrics.json", "w"), indent=1)
    json.dump(flags, open(f"{a.out}/flags.json", "w"), indent=1)
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
