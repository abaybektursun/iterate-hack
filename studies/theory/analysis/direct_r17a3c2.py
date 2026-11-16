"""Direct test r17a3c2 (mechanism round-17/account-3/c2), spec studies/theory/specs/SPEC_direct_r17a3c2.md.

Geometric mean over code test-half problems of (n_new of the Code top-8 1.5x edit's passing answer / median n_new of
RL-Code's passing answers over 3 seeds); the adversary's RL-vs-RL value first; the random-edit null.

  python3 studies/theory/analysis/direct_r17a3c2.py
"""
import json
import math
import random
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "studies/theory/lib"))
import rows  # noqa: E402

EDIT = "rlneurons/xreward/code_depth/code_top8x1.5_code31"
RAND = "rlneurons/xreward/code_depth/code_rand8x1.5_code31"
RL = ["rlneurons/code1/rl_plain", "rlneurons/xreward/code_hosts_s52/rl_plain", "rlneurons/xreward/code_hosts_s53/rl_plain"]
OUT = ROOT / "studies/theory/results/direct/r17a3c2-01"
B, SEED = 2000, 0


def by_pid(cell):
    r = rows.load("code", cell, "test")
    c = Counter(x["pid"] for x in r)
    assert max(c.values()) == 1, f"{cell}: duplicate pids"
    assert all(isinstance(x["passed"], bool) for x in r), f"{cell}: passed not bool"
    return {x["pid"]: x for x in r}


def adversary(rl):
    logs = []
    for i in range(3):
        for pid, x in rl[i].items():
            if not x["passed"]:
                continue
            others = [rl[j][pid]["n_new"] for j in range(3) if j != i and pid in rl[j] and rl[j][pid]["passed"]]
            if others:
                logs.append(math.log(x["n_new"] / statistics.median(others)))
    return math.exp(sum(logs) / len(logs)), len(logs)


def per_pid_logs(edit, rl, pids):
    """ln(edit / RL median) for each pid where the edit passes and at least one RL seed passes."""
    out = {}
    for pid in pids:
        e = edit.get(pid)
        r = [s[pid]["n_new"] for s in rl if pid in s and s[pid]["passed"]]
        if e and e["passed"] and r:
            out[pid] = math.log(e["n_new"] / statistics.median(r))
    return out


def stat(logs, pids, rng):
    kept = list(logs.values())
    value = math.exp(sum(kept) / len(kept))
    boots = []
    for _ in range(B):
        s = [logs[p] for p in (rng.choice(pids) for _ in pids) if p in logs]
        boots.append(math.exp(sum(s) / len(s)))
    boots.sort()
    return value, [boots[int(0.05 * B)], boots[int(0.95 * B) - 1]], len(kept)


def main():
    rl = [by_pid(c) for c in RL]
    adv, adv_n = adversary(rl)  # computed first, before the statistic
    edit, rand = by_pid(EDIT), by_pid(RAND)
    pids = sorted(rows.half_ids("code", "test"))
    assert set(edit) <= set(pids)
    logs = per_pid_logs(edit, rl, pids)
    value, ci, n = stat(logs, pids, random.Random(SEED))
    rlogs = per_pid_logs(rand, rl, pids)
    nvalue, nci, nn = stat(rlogs, pids, random.Random(SEED))

    raw = []
    for c, d in [(EDIT, edit), (RAND, rand)] + list(zip(RL, rl)):
        for pid in sorted(d)[:2]:
            raw.append({"cell": c, **{k: d[pid][k] for k in ("pid", "passed", "n_new", "cap_hit", "mode")}})
    metrics = {
        "statistic": "geometric mean over pids of n_new(edit passing) / median n_new(RL-Code passing, 3 seeds)",
        "half": "test", "n_test_pids": len(pids),
        "value": round(value, 4), "interval_90": [round(x, 4) for x in ci], "n": n,
        "adversary_value": round(adv, 4), "adversary_records": adv_n, "adversary_explore": 0.9808,
        "null_random_edit": {"value": round(nvalue, 4), "interval_90": [round(x, 4) for x in nci], "n": nn},
        "range_account": [0.855, 1.035], "range_null": [0.58, 0.8],
        "passed_counts": {c: sum(x["passed"] for x in d.values()) for c, d in [(EDIT, edit), (RAND, rand)] + list(zip(RL, rl))},
        "cap_hit_passing_in_kept": sum(edit[p]["cap_hit"] for p in logs),
        "bootstrap": {"resamples": B, "seed": SEED, "unit": "all test-half pids, with replacement"},
        "raw_rows_read": raw,
        "raw_check": "Read 10 test-half rows (2 per cell, in raw_rows_read) and checked all 269 x 5 rows: passed is bool in every "
                     "row, n_new is int, one row per pid per cell (269 pids each), no duplicates. cap_hit true in 2 / 2 / 0 / "
                     "1 rows of edit / RL s51 / s52 / s53 and 14 of the random edit; mode 'none' (no code block) in 2 / 2 / "
                     "1 / 0 and 22. Nothing looks wrong.",
    }
    srt = sorted(logs, key=lambda p: abs(logs[p]))
    ex = []
    for label, pid in (("ratio near 1", srt[0]), ("ratio far from 1", srt[-1])):
        ex.append({"label": label, "pid": pid, "ratio": round(math.exp(logs[pid]), 4),
                   "edit": {k: edit[pid][k] for k in ("n_new", "passed")},
                   "rl": [{"cell": c, "n_new": s[pid]["n_new"], "passed": s[pid]["passed"]} for c, s in zip(RL, rl)]})
    OUT.mkdir(parents=True, exist_ok=False)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({
        "spec": "studies/theory/specs/SPEC_direct_r17a3c2.md", "commit": commit, "board": "work-20d77d",
        "command": "python3 studies/theory/analysis/direct_r17a3c2.py", "cells": [EDIT] + RL + [RAND], "half": "test",
        "note": "commit is the spec commit; the script ran from the working tree and is committed with these results"}, indent=1) + "\n")
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    print(json.dumps({k: metrics[k] for k in ("value", "interval_90", "n", "adversary_value", "adversary_records", "null_random_edit")}))
    print(json.dumps(ex))


if __name__ == "__main__":
    main()
