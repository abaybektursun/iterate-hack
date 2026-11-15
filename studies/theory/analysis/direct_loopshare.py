"""Direct test loopshare-01 (studies/theory/specs/SPEC_direct_loopshare.md): round-14/s3 rivals a and b.

Loop share = rule-A loops / answers with more than 4,096 generated tokens, base model at T 0.6 on hard328.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_loopshare

Run from the repository root. Inputs (not committed): runs/s3/r3/base-01/out/{P,F}_hard.jsonl
(aws s3 cp s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/<file> ... --profile iterate-ecr) and
runs/abaybektursun-1114-151534-e72c/answers.jsonl (uv run tools/gpu.py get abaybektursun-1114-151534-e72c).
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from studies.rlneurons.analysis.day1_hard328 import rows_by_index, score
from studies.rlneurons.lib import rln4_lib as R

ROOT = pathlib.Path(__file__).resolve().parents[3]
RL = ROOT / "studies" / "rlneurons"
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "loopshare-01"
CUT = 4096
RANGES = {"a": (0.05, 0.40), "b": (0.45, 1.0), "null": (0.0, 0.03)}
# cell -> (rows file, posted right v3, cap hits, rule-A loops on the 328 problems)
CELLS = {
    "plain_T0.6": ("runs/s3/r3/base-01/out/P_hard.jsonl", 107, 137, 98),
    "cue_T0.6": ("runs/s3/r3/base-01/out/F_hard.jsonl", 119, 173, 132),
    "cue_T1.0_null": ("runs/abaybektursun-1114-151534-e72c/answers.jsonl", 164, 77, 1),
}
PRIMARY = "plain_T0.6"
# written after reading the first 10 kept rows of the primary cell (problem indices 0-68), text at the loop onset and the tail
RAW_ROWS_READ = ("First 10 kept plain T 0.6 rows (indices 0, 15, 29, 57, 58, 61, 62, 66, 67, 68): 7 are rule-A loops, all cap "
                 "hits, the same re-derivation cycling to 16,384 tokens (index 29 repeats one formula line, 'Wait, maybe the "
                 "formula is (m-1)(n-1) + (m + n -1)... still not 8. Hmm.'; onsets at 6k-29k characters). The 3 non-loops "
                 "all finish with a boxed answer: right at 9,825 and 14,631 tokens (66: 721, 61: 113), wrong at 4,384 (68: 405).")


def boot(x, rng):
    idx = rng.integers(0, len(x), size=(10_000, len(x)))
    s = x[idx].mean(axis=1)
    return [round(float(np.percentile(s, 5)), 4), round(float(np.percentile(s, 95)), 4)]


def verdict(ci, n):
    """Engine-14 rule for a rival pair's shared test: per rival, holds / refuted / undecided."""
    if n < 50:
        return {"a": "undecided", "b": "undecided"}
    lo, hi = ci
    inside = {k: RANGES[k][0] <= lo and hi <= RANGES[k][1] for k in ("a", "b")}
    touches = {k: hi >= RANGES[k][0] and lo <= RANGES[k][1] for k in ("a", "b")}
    if inside["a"]:
        return {"a": "holds", "b": "refuted"}
    if inside["b"]:
        return {"a": "refuted", "b": "holds"}
    return {k: "undecided" if touches[k] else "refuted" for k in ("a", "b")}


def row_view(r, s):
    return {"problem_index": r["problem_index"], "gold": r["gold"], "n_new": r["n_new"], "cap_hit": bool(r["cap_hit"]),
            "loop_A": bool(s["loop_A"]), "loop_onset_char": R.onset_lines(r["text"]), "extracted_v3": s["extracted_v3"],
            "score_v3": s["v3"], "text_chars": len(r["text"]), "text_tail": r["text"][-600:]}


def main():
    R.selfcheck()
    hard = json.loads((RL / "data" / "rln3" / "hard.json").read_text())
    flags = json.loads((RL / "results" / "rln3" / "rln3_overlap.json").read_text())["sets"]["hard"]["flags"]
    clean = sorted(int(i) for i, f in flags.items() if f["flag"] == "none")
    assert len(clean) == 328
    gold = {i: hard[i]["answer"] for i in clean}

    rng = np.random.default_rng(0)
    cells, rows, sc = {}, {}, {}
    for name, (path, want_right, want_cap, want_loop) in CELLS.items():
        rows[name] = rows_by_index(ROOT / path, clean)
        sc[name] = score(rows[name], gold)
        got = (sum(s["v3"] for s in sc[name].values()), sum(s["cap"] for s in sc[name].values()),
               sum(s["loop_A"] for s in sc[name].values()))
        assert got == (want_right, want_cap, want_loop), (name, "posted counts not reproduced", got)
        kept = [i for i in clean if sc[name][i]["tokens"] > CUT]
        x = np.array([sc[name][i]["loop_A"] for i in kept], dtype=float)
        live = [i for i in kept if not sc[name][i]["loop_A"]]
        cells[name] = {
            "file": path, "reproduced_right_cap_loops": list(got), "n": len(kept), "loops": int(x.sum()),
            "loop_share": round(float(x.mean()), 4), "ci90": boot(x, rng),
            "loops_at_or_below_4096": sum(sc[name][i]["loop_A"] for i in clean if sc[name][i]["tokens"] <= CUT),
            "kept_not_loop": {"n": len(live), "cap_hits": sum(sc[name][i]["cap"] for i in live),
                              "finished": sum(1 - sc[name][i]["cap"] for i in live),
                              "right_v3": sum(sc[name][i]["v3"] for i in live)},
            "kept_right_v3": sum(sc[name][i]["v3"] for i in kept),
        }
        print(name, json.dumps(cells[name]))

    p = cells[PRIMARY]
    v = verdict(p["ci90"], p["n"])
    metrics = {
        "test": "loopshare-01", "plan": "studies/theory/results/wide/round-14/jobs/rivals-s3.json",
        "spec": "studies/theory/specs/SPEC_direct_loopshare.md",
        "statistic": "loop share: rule-A loops / answers with more than 4,096 generated tokens (base, T 0.6 / top-p 0.95, hard328, cap 16,384, one answer per problem)",
        "primary_cell": PRIMARY, "value": p["loop_share"], "ci90": p["ci90"], "n": p["n"],
        "null_value": cells["cue_T1.0_null"]["loop_share"], "null_ci90": cells["cue_T1.0_null"]["ci90"],
        "ranges": RANGES, "verdict": v, "cells": cells,
        "plan_cell_bounds": {
            "cell": "studies/cleanneurons/results/gen/hard328_base_t06-01 (cue, T 0.6 / top-p 1.0; rows only in iterate-runs:sameraslan-1114-220554-2e30/answers.jsonl)",
            "loops_A": 94, "cap_hits": 156,
            "share_bounds_if_every_loop_is_past_4096": [round(94 / 328, 4), round(94 / 156, 4)],
        },
        "bootstrap": "10,000 percentile resamples of the kept answers, numpy default_rng(0), 5th and 95th percentiles",
        "raw_rows_read": RAW_ROWS_READ,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    s, r = sc[PRIMARY], rows[PRIMARY]
    kept = [i for i in clean if s[i]["tokens"] > CUT]
    loop_i = next(i for i in kept if s[i]["loop_A"])
    live_i = next(i for i in kept if not s[i]["loop_A"])
    (OUT / "examples.json").write_text(json.dumps({
        "cell": PRIMARY, "file": CELLS[PRIMARY][0],
        "counts": {"why": "kept (n_new > 4,096) and a rule-A loop: in the numerator", **row_view(r[loop_i], s[loop_i])},
        "does_not_count": {"why": "kept (n_new > 4,096) but no rule-A loop: in the denominator only", **row_view(r[live_i], s[live_i])},
    }, indent=1) + "\n")
    print("verdict", v)


if __name__ == "__main__":
    main()
