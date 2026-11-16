"""pairs2 readout (specs/SPEC_pairs2.md): which input-output pairs of the Math 3.1 top-8 edit at 1.5 matter. hard328 (n 328), cue,
T 1.0 / top-p 1.0, cap 16,384, grader v3 as written by run_cell.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.pairs2_readout

Run from the repository root. Inputs: runs/<job-id>/ of every job in NEW (`uv run tools/gpu.py get <job-id>`, not committed); the
committed rows of the base (4 samples), of the pairing arms (sample 0, results/xreward/pairing/rows.jsonl) and of direction 1 alone
at 1.5 (samples 0 and 1, read with `git show` from commit NORMBAND of branch normband, not merged here). Writes
results/xreward/pairs2/: readout.json and one run folder <cell>_s<sample>-01/ per new sample (run.json, metrics.json, examples.json,
rows.jsonl). Fails if a run folder exists. P-E: from runs/<XSHIFT>/ (jobs/xshift.py, one-layer write arms) writes
results/xshift/perm1layer-01/ (run.json, metrics.json, readout.json: RMS shift, all positions, per layer, and growth from the
edited layer to layer 24).
"""
from __future__ import annotations

import json
import subprocess

import numpy as np

from studies.rlneurons.analysis.depth3_readout import B, RNG, RUNS, SEED0, STUDY, compact, diff, example, read
from studies.rlneurons.analysis.shard_join import join

OUT = STUDY / "results" / "xreward" / "pairs2"
NORMBAND = "d53d5a0"                                                 # branch normband: direction 1 alone at 1.5, samples 0 and 1
# cell -> {sample: (job of shard 0/2, job of shard 1/2)}; wsp_edit arguments (with --other math31 --rounding stochastic) in EDIT
NEW = {"permx1.5_math31": {1: ("abaybektursun-1115-171824-7b50", "abaybektursun-1115-171839-84ab")},
       "permrestx1.5_math31": {0: ("abaybektursun-1115-171853-982f", "abaybektursun-1115-171908-dd42"),
                               1: ("abaybektursun-1115-180754-f49b", "abaybektursun-1115-180811-2a58")},          # amendment 1
       "swap12x1.5_math31": {0: ("abaybektursun-1115-171927-c131", "abaybektursun-1115-171940-442a"),
                             1: ("abaybektursun-1115-180829-ce8b", "abaybektursun-1115-180850-dfcd")},            # amendment 1
       "rand8x1.5_math31": {1: ("abaybektursun-1115-171956-17a3", "abaybektursun-1115-172013-5ab5")},
       "rinx1.5_math31": {1: ("abaybektursun-1115-172029-13c1", "abaybektursun-1115-172044-4cf6")},
       "permx12_math31": {0: ("abaybektursun-1115-183336-1d44", "abaybektursun-1115-183354-372f")},               # amendment 2
       "top8x1.5_d3-8_math31": {0: ("abaybektursun-1115-181303-d3b6", "abaybektursun-1115-181319-e485")},
       "rand8x1.5_seed1_math31": {0: ("abaybektursun-1115-181337-5d58", "abaybektursun-1115-181355-a7cc")}}
EDIT = {"permx1.5_math31": "--recipe perm --scale 1.5 --seed 0", "permrestx1.5_math31": "--recipe permrest --scale 1.5 --seed 0",
        "swap12x1.5_math31": "--recipe swap12 --scale 1.5 --seed 0", "rand8x1.5_math31": "--recipe rand8 --scale 1.5 --seed 0",
        "rinx1.5_math31": "--recipe rin --scale 1.5 --seed 0", "permx12_math31": "--recipe perm --scale 12 --seed 0",
        "top8x1.5_d3-8_math31": "--recipe top8 --skip 2 --scale 1.5 --seed 0", "rand8x1.5_seed1_math31": "--recipe rand8 --scale 1.5 --seed 1"}
DIAL15 = STUDY / "results" / "xreward" / "dial15_s4_vs_base_cue-01" / "rows.jsonl"      # all 8 at 1.5, 4 samples: reference "top8x1.5_s4"
CONTRASTS = [(c, r) for c in NEW for r in ("base_cue", "rand8x1.5_math31", "top8x1.5_math31", "top8x1.5_s4") if c != r] + \
    [("permrestx1.5_math31", "top1x1.5_math31"), ("swap12x1.5_math31", "top1x1.5_math31"), ("permx1.5_math31", "rinx1.5_math31"),
     ("swap12x1.5_math31", "top8x1.5_d3-8_math31"), ("top8x1.5_d3-8_math31", "top1x1.5_math31")]


def degenerate(r):
    """an answer counted as degenerate: ' which ' is more than 5 % of its words (the loop of broken edits), more than 30 % of its
    characters are at or above U+2E80 (CJK and other scripts), or run_cell's loop_A flag"""
    t = r["text"]
    return t.count(" which ") > 0.05 * max(1, len(t.split())) or sum(ord(c) >= 0x2E80 for c in t) > 0.3 * max(1, len(t)) or bool(r["loop_A"])


def diff99(a, b, rng):
    """diff with the 99 % interval added"""
    d = a - b
    boot = d[rng.integers(0, len(d), (B, len(d)))].mean(1)
    return {**diff(a, b, rng), "interval99": [round(100 * x, 2) for x in np.percentile(boot, [0.5, 99.5])]}


XSHIFT = {"perm1layer-01": ("abaybektursun-1115-171512-4a1d", "P-E"), "permscale-01": ("abaybektursun-1115-181246-b2c5", "amendment 2, R-1")}
LAYERS = (0, 1, 8, 9, 12, 16, 24, 31)


def xshift(run, job_id, part):
    d = STUDY / "results" / "xshift" / run
    if d.exists():                                                   # written by an earlier run of this readout
        return
    job = RUNS / job_id
    m = json.loads((job / "metrics.json").read_text())
    d.mkdir(parents=True)
    (d / "run.json").write_text(json.dumps({"experiment": "xshift", "run": run, "spec": f"studies/rlneurons/specs/SPEC_pairs2.md {part}",
                                            "job": json.loads((job / "run.json").read_text()), "raw": f"runs/{job_id}/shifts.npz, not committed"}, indent=1) + "\n")
    (d / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
    out = {}
    for arm, e in m["edits"].items():
        rms, lay = e["shift"]["all"]["rms"], int(arm.split("_L")[1].split("_")[0]) if "_L" in arm else 0
        out[arm] = {"edited_layer": lay, "add_rel": e["add_rel"], "rms": {str(l): rms[l] for l in sorted({lay, lay + 1, *LAYERS})}, "growth_to_24": rms[24] / rms[lay] if "_L" in arm else None}
    (d / "readout.json").write_text(json.dumps({"job": job_id, "measure": "RMS residual shift over 6,144 positions of 48 stored base answers, float32", "edits": out}, indent=1) + "\n")
    for arm, e in out.items():
        print(f"{arm:28s} " + " ".join(f"L{l} {v:.4f}" for l, v in e["rms"].items()) + f" growth {e['growth_to_24']}")


def main():
    arr = {}                                                         # cell -> {sample: {"right": [328], "cap": [328]}}, problems sorted
    base = {}
    for r in read(STUDY / "results" / "day1_3" / "hard328_base_cue_s4r2-01" / "rows.jsonl"):
        if r["attempt"] == 0:
            base.setdefault(r["sample"], []).append(r)
    for s, rows in base.items():
        rows = compact(rows, s)
        arr.setdefault("base_cue", {})[s] = {"right": [r["score_v3"] for r in rows], "cap": [int(r["cap_hit"]) for r in rows]}
    idx = sorted(r["problem_index"] for r in base[0])
    for r in read(STUDY / "results" / "xreward" / "pairing" / "rows.jsonl"):
        d = arr.setdefault(r["arm"], {}).setdefault(0, {"right": {}, "cap": {}})
        d["right"][r["problem_index"]], d["cap"][r["problem_index"]] = r["right_v3"], r["cap_hit"]
    dial = {}
    for r in read(DIAL15):
        if r["attempt"] == 0:
            dial.setdefault(r["sample"], []).append(r)
    arr["top8x1.5_s4"] = {s: {"right": [r["score_v3"] for r in rows], "cap": [int(r["cap_hit"]) for r in rows]}
                          for s, rows in ((s, compact(rows, s)) for s, rows in dial.items())}
    for cell in ("top8x1.5_math31", "rand8x1.5_math31", "rinx1.5_math31", "routx1.5_math31", "permx1.5_math31"):
        arr[cell][0] = {k: [v[i] for i in idx] for k, v in arr[cell][0].items()}
    for s in (0, 1):
        path = f"studies/rlneurons/results/xreward/normband/top1x1.5_math31_s{s}-01/rows.jsonl"
        rows = sorted((json.loads(l) for l in subprocess.run(["git", "show", f"{NORMBAND}:{path}"], check=True, capture_output=True, text=True).stdout.splitlines()),
                      key=lambda r: r["problem_index"])
        arr.setdefault("top1x1.5_math31", {})[s] = {"right": [r["score_v3"] for r in rows], "cap": [int(r["cap_hit"]) for r in rows]}
    tokens, degen = {}, {}
    for cell, samples in NEW.items():
        for s, jobs in samples.items():
            m, rows = join([(json.loads((RUNS / j / "metrics.json").read_text()), read(RUNS / j / "answers.jsonl")) for j in jobs])
            c = m["config"]
            assert (c["model_label"], c["seed"], c["prompt"], c["set"], c["temperature"], c["top_p"], c["max_tokens"]) == \
                (cell, SEED0 + 10000 * s, "cue", "hard328", 1.0, 1.0, 16384), c
            assert s not in arr.get(cell, {}), (cell, s)
            rows = sorted(rows, key=lambda r: r["problem_index"])
            crow = compact(rows, s)
            arr.setdefault(cell, {})[s] = {"right": [r["score_v3"] for r in crow], "cap": [int(r["cap_hit"]) for r in crow]}
            tokens[f"{cell} sample {s}"] = round(float(np.mean([r["n_new"] for r in rows])), 1)
            degen[f"{cell} sample {s}"] = sum(degenerate(r) for r in rows)
            d = OUT / f"{cell}_s{s}-01"
            new_rows = "".join(json.dumps(r) + "\n" for r in crow)
            if d.exists():                                           # written by an earlier run of this readout: check, never rewrite
                assert (d / "rows.jsonl").read_text() == new_rows, d
                continue
            d.mkdir(parents=True)
            cmd = (f"wsp_edit {EDIT[cell]} --other math31 --rounding stochastic, then run_cell --model-label {cell} --prompt cue "
                   f"--set hard328 --temperature 1.0 --top-p 1.0 --seed {c['seed']} --shard k/2 (k = 0, 1), joined by analysis/shard_join.join")
            (d / "run.json").write_text(json.dumps({"job_ids": list(jobs), "commit": m["commit"], "command": cmd, "runner": "uv run tools/gpu.py submit h100 --hours 1.5",
                                                    "raw_answers": [f"runs/{j}/answers.jsonl (uv run tools/gpu.py get {j})" for j in jobs],
                                                    "edit": json.loads((RUNS / jobs[0] / "edit.json").read_text())["totals"]}, indent=1) + "\n")
            (d / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
            (d / "rows.jsonl").write_text(new_rows)
            right = next(r for r in rows if r["score_v3"] == 1)
            wrong = next((r for r in rows if r["score_v3"] == 0 and not r["cap_hit"]), None) or next(r for r in rows if r["score_v3"] == 0)
            (d / "examples.json").write_text(json.dumps({"right": example(right), "wrong": example(wrong)}, indent=1) + "\n")

    A = {cell: {k: np.array([ss[s][k] for s in sorted(ss)], dtype=float) for k in ("right", "cap")} for cell, ss in arr.items()}
    for cell, a in A.items():
        assert a["right"].shape[1] == 328, (cell, a["right"].shape)
    rng = np.random.default_rng(RNG)
    table = {}
    for cell, a in A.items():
        t = {"samples": sorted(arr[cell]), "right": [int(x) for x in a["right"].sum(1)], "right_mean": round(a["right"].sum(1).mean(), 2),
             "cap_hits": [int(x) for x in a["cap"].sum(1)], "cap_hits_mean": round(a["cap"].sum(1).mean(), 2)}
        for c, ref in CONTRASTS:
            if c == cell:
                t[f"minus_{ref}"] = {"reference_samples": sorted(arr[ref]), **{k: diff99(a[k].mean(0), A[ref][k].mean(0), rng) for k in ("right", "cap")}}
        if cell in NEW:                                              # the base on the cell's own seeds
            ss = sorted(arr[cell])
            t["minus_base_cue_same_seeds"] = {"reference_samples": ss, **{k: diff(a[k].mean(0), A["base_cue"][k][ss].mean(0), rng) for k in ("right", "cap")}}
        table[cell] = t
    out = {"spec": "studies/rlneurons/specs/SPEC_pairs2.md", "set": "hard328, n 328", "settings": "cue, T 1.0 / top-p 1.0, cap 16,384, grader v3, scale 1.5",
           "seed_rule": f"{SEED0} + 10000 * sample + problem index", "mean_tokens_new_samples": tokens, "degenerate_answers_new_samples": degen, "degenerate_rule": degenerate.__doc__.strip(),
           "differences": f"per problem, mean over the cell's samples minus mean over the reference's samples; points of 328; 95 % interval from {B} resamples of the problems (numpy seed {RNG})",
           "sources": {"base_cue": "results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl", "pairing arms sample 0": "results/xreward/pairing/rows.jsonl", "top8x1.5_s4": str(DIAL15.relative_to(STUDY)),
                       "top1x1.5_math31": f"git show {NORMBAND}:studies/rlneurons/results/xreward/normband/top1x1.5_math31_s{{0,1}}-01/rows.jsonl",
                       **{f"{k} sample {s}": [f"runs/{j}" for j in js] for k, ss in NEW.items() for s, js in ss.items()}},
           "cells": table}
    (OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    f = lambda d: f"{d['points']:+.1f} [{d['interval95'][0]:.1f}, {d['interval95'][1]:.1f}]"
    for cell, t in table.items():
        print(f"{cell:22s} right {t['right_mean']:6.1f} {t['right']} cap {t['cap_hits_mean']:5.1f} {t['cap_hits']}"
              + "".join(f" | {k[6:]}: right {f(v['right'])} cap {f(v['cap'])}" for k, v in t.items() if k.startswith("minus_")))
    print(tokens)
    print(degen)


if __name__ == "__main__":
    main()
    for run, (job, part) in XSHIFT.items():
        xshift(run, job, part)
