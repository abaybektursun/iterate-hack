"""normband readout (specs/SPEC_normband.md): the Math 3.1 top-8 edit in layers 22-31 scaled up and in layers 0-10 scaled down to
the other band's layer-24 activation shift. hard328 (n 328), cue, T 1.0 / top-p 1.0, cap 16,384, grader v3, sample 1. Also the rank cells: direction 1 alone and
directions 2-8, each at 1.5, all layers, samples 0 and 1.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.normband_readout

Run from the repository root. Inputs: runs/<job-id>/ of every job in NEW (`uv run tools/gpu.py get <job-id>`, not committed) and the
committed rows of the references (depth3 and base). Writes results/xreward/normband/: readout.json and one run folder <cell>_s1-01/
per cell (run.json, metrics.json, examples.json, rows.jsonl). Fails if a run folder exists.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from studies.rlneurons.analysis.depth3_readout import B, RNG, RUNS, SEED0, STUDY, compact, diff, example, read
from studies.rlneurons.analysis.shard_join import join

OUT = STUDY / "results" / "xreward" / "normband"
D3 = STUDY / "results" / "xreward" / "depth3"
# cell -> {sample: (job of shard 0/2, job of shard 1/2)}; wsp_edit arguments in EDIT. Sample s has seed SEED0 + 10000 s + problem.
NEW = {"top8x4.5_L22-31_math31": {1: ("abaybektursun-1115-145625-c6dc", "abaybektursun-1115-145638-c016")},
       "top8x0.2_L0-10_math31": {1: ("abaybektursun-1115-145652-dc10", "abaybektursun-1115-145706-0b28")},
       "top8x3_L22-31_math31": {1: ("abaybektursun-1115-145720-8ceb", "abaybektursun-1115-145733-af00")},
       "top1x1.5_math31": {1: ("abaybektursun-1115-145845-f70e", "abaybektursun-1115-145859-a234"),
                           0: ("abaybektursun-1115-145913-fed1", "abaybektursun-1115-145926-720e")},
       "top8x1.5_d2-8_math31": {0: ("abaybektursun-1115-145941-c2cc", "abaybektursun-1115-145956-7546")},
       # amendment 3 (review cells)
       "top1x1.5_math31_plain": {1: ("abaybektursun-1115-161303-5ad7", "abaybektursun-1115-161320-a1e0")},
       "top8x1.5_d2-8_math31_plain": {1: ("abaybektursun-1115-161337-2422", "abaybektursun-1115-161356-4282")},
       "base_plain": {1: ("abaybektursun-1115-161512-737c", "abaybektursun-1115-161527-c434")}}
NEW["top8x3_L22-31_math31"][0] = ("abaybektursun-1115-161231-ef64", "abaybektursun-1115-161247-15fb")
PLAIN = {"top1x1.5_math31_plain", "top8x1.5_d2-8_math31_plain", "base_plain"}                    # prompt plain; every other cell: cue
LABEL = {"base_plain": None}                                                                     # run_cell --model base: no --model-label
EDIT = {"top8x4.5_L22-31_math31": "--recipe top8 --layers 22-31 --scale 4.5", "top8x0.2_L0-10_math31": "--recipe top8 --layers 0-10 --scale 0.2",
        "top8x3_L22-31_math31": "--recipe top8 --layers 22-31 --scale 3.0", "top1x1.5_math31": "--recipe top8 --k 1 --scale 1.5",
        "top8x1.5_d2-8_math31": "--recipe top8 --skip 1 --scale 1.5", "top1x1.5_math31_plain": "--recipe top8 --k 1 --scale 1.5",
        "top8x1.5_d2-8_math31_plain": "--recipe top8 --skip 1 --scale 1.5"}
REFS = {"base_cue": [STUDY / "results" / "day1_3" / "hard328_base_cue_s4r2-01" / "rows.jsonl"],
        "top8x1.5_math31": [STUDY / "results" / "xreward" / "dial15_s4_vs_base_cue-01" / "rows.jsonl"],
        "top8x1.5_L0-10_math31": [D3 / "sample0_rows" / "top8x1.5_L0-10_math31.jsonl"] + [D3 / f"top8x1.5_L0-10_math31_s{s}-01" / "rows.jsonl" for s in (1, 2, 3)],
        "top8x1.5_L22-31_math31": [D3 / "sample0_rows" / "top8x1.5_L22-31_math31.jsonl", D3 / "top8x1.5_L22-31_math31_s1-01" / "rows.jsonl"],
        "top8x1.5_d2-8_math31": [D3 / "top8x1.5_d2-8_math31_s1-01" / "rows.jsonl"]}
# (cell, reference): per problem, mean over the cell's samples minus mean over the reference's samples
CONTRASTS = [("top8x4.5_L22-31_math31", "top8x1.5_L0-10_math31"), ("top8x4.5_L22-31_math31", "top8x1.5_L22-31_math31"),
             ("top8x3_L22-31_math31", "top8x1.5_L22-31_math31"), ("top8x0.2_L0-10_math31", "top8x1.5_L22-31_math31"),
             ("top8x0.2_L0-10_math31", "top8x1.5_L0-10_math31"), ("top1x1.5_math31", "top8x1.5_d2-8_math31"),
             ("top1x1.5_math31", "top8x1.5_math31"), ("top8x1.5_d2-8_math31", "top8x1.5_math31"),
             ("top1x1.5_math31_plain", "base_plain"), ("top8x1.5_d2-8_math31_plain", "base_plain"),
             ("top1x1.5_math31_plain", "top8x1.5_d2-8_math31_plain")]


def which_rate(rows):
    """coherence check read from the raw text: rows whose answer has ' which ' as more than 5 % of its words (the loop of the broken
    9.0 smoke run); returns that count"""
    return sum(r["text"].count(" which ") > 0.05 * max(1, len(r["text"].split())) for r in rows)


def main():
    cells, which = {}, {}                                            # cell -> {sample: compact rows}; cell -> {sample: which_rate}
    for cell, paths in REFS.items():
        for p in paths:
            for r in read(p):
                if r["attempt"] == 0:
                    cells.setdefault(cell, {}).setdefault(r["sample"], []).append(r)
        cells[cell] = {s: compact(rows, s) for s, rows in cells[cell].items()}
    assert [len(cells[c]) for c in REFS] == [4, 4, 4, 2, 1], {c: sorted(cells[c]) for c in REFS}
    for cell, sample, jobs in ((c, s, j) for c, ss in NEW.items() for s, j in ss.items()):
        m, rows = join([(json.loads((RUNS / j / "metrics.json").read_text()), read(RUNS / j / "answers.jsonl")) for j in jobs])
        c = m["config"]
        assert (c["model_label"], c["seed"], c["prompt"], c["set"], c["temperature"], c["top_p"], c["max_tokens"]) == \
            (LABEL.get(cell, cell), SEED0 + 10000 * sample, "plain" if cell in PLAIN else "cue", "hard328", 1.0, 1.0, 16384), c
        assert sample not in cells.get(cell, {}), (cell, sample)
        cells.setdefault(cell, {})[sample] = compact(rows, sample)
        which.setdefault(cell, {})[sample] = which_rate(rows)
        d = OUT / f"{cell}_s{sample}-01"
        new_rows = "".join(json.dumps(r) + "\n" for r in cells[cell][sample])
        if d.exists():                                               # written by an earlier run of this readout: check, never rewrite
            assert (d / "rows.jsonl").read_text() == new_rows, d
            continue
        d.mkdir(parents=True)
        run = (f"run_cell --model base" if cell in LABEL else f"wsp_edit {EDIT[cell]} --other math31 --rounding stochastic --seed 0, then run_cell --model-label {cell}")
        cmd = (f"{run} --prompt {c['prompt']} --set hard328 "
               f"--temperature 1.0 --top-p 1.0 --seed {c['seed']} --shard k/2 (k = 0, 1), joined by analysis/shard_join.join")
        (d / "run.json").write_text(json.dumps({"job_ids": list(jobs), "commit": m["commit"], "command": cmd, "runner": "uv run tools/gpu.py submit h100 --hours 1.5",
                                                "raw_answers": [f"runs/{j}/answers.jsonl (uv run tools/gpu.py get {j})" for j in jobs],
                                                "edit": None if cell in LABEL else json.loads((RUNS / jobs[0] / "edit.json").read_text())["totals"]}, indent=1) + "\n")
        (d / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
        (d / "rows.jsonl").write_text(new_rows)
        rows = sorted(rows, key=lambda r: r["problem_index"])
        right = next((r for r in rows if r["score_v3"] == 1), None)
        wrong = next((r for r in rows if r["score_v3"] == 0 and not r["cap_hit"]), None) or next(r for r in rows if r["score_v3"] == 0)
        (d / "examples.json").write_text(json.dumps({"right": right and example(right), "wrong": example(wrong)}, indent=1) + "\n")

    idx = sorted(r["problem_index"] for r in cells["base_cue"][0])
    assert len(idx) == 328
    arr = {}
    for cell, samples in cells.items():
        for s, rows in samples.items():
            assert [r["problem_index"] for r in rows] == idx, (cell, s, len(rows))
        arr[cell] = {key: np.array([[float(r[f]) for r in samples[s]] for s in sorted(samples)]) for key, f in (("right", "score_v3"), ("cap", "cap_hit"))}
    rng = np.random.default_rng(RNG)
    table = {}
    for cell in arr:
        right, cap = arr[cell]["right"], arr[cell]["cap"]
        t = {"samples": sorted(cells[cell]), "right": [int(x) for x in right.sum(1)], "right_mean": round(right.sum(1).mean(), 2),
             "cap_hits": [int(x) for x in cap.sum(1)], "cap_hits_mean": round(cap.sum(1).mean(), 2), "which_loop_rows": which.get(cell),
             "mean_tokens": round(float(np.mean([r["n_new"] for ss in cells[cell].values() for r in ss])), 1)}
        if cell in NEW and cell not in LABEL:                        # the base's samples with the same seeds (plain base for plain cells)
            ss = sorted(cells[cell])
            base = "base_plain" if cell in PLAIN else "base_cue"
            t["minus_base_plain_same_seeds" if cell in PLAIN else "minus_base_cue_same_seeds"] = {"reference_samples": ss, **{key: diff(arr[cell][key].mean(0), arr[base][key][[sorted(cells[base]).index(x) for x in ss]].mean(0), rng)
                                                                          for key in ("right", "cap")}}
        for c, ref in [(cell, "base_cue")] * (cell not in ("base_cue", "base_plain") and cell not in PLAIN) + [x for x in CONTRASTS if x[0] == cell]:
            t[f"minus_{ref}"] = {"reference_samples": sorted(cells[ref]),
                                 **{key: diff(arr[cell][key].mean(0), arr[ref][key].mean(0), rng) for key in ("right", "cap")}}
        table[cell] = t
    out = {"spec": "studies/rlneurons/specs/SPEC_normband.md", "set": "hard328, n 328", "settings": "cue, T 1.0 / top-p 1.0, cap 16,384, grader v3 (score_v3 of run_cell)",
           "seed_rule": f"{SEED0} + 10000 * sample + problem index", "edits": EDIT,
           "differences": f"per problem, mean over the cell's samples minus mean over the reference's samples; points of 328; 95 % interval from {B} resamples of the problems (numpy seed {RNG})",
           "sources": {**{k: [str(p) for p in v] for k, v in REFS.items()}, **{f"{k} sample {s}": [f"runs/{j}" for j in js] for k, ss in NEW.items() for s, js in ss.items()}},
           "cells": table}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    f = lambda d: f"{d['points']:+.1f} [{d['interval95'][0]:.1f}, {d['interval95'][1]:.1f}]"
    for cell, t in table.items():
        print(f"{cell:26s} n {len(t['samples'])} right {t['right_mean']:6.1f} {t['right']} cap {t['cap_hits_mean']:5.1f} {t['cap_hits']}"
              + "".join(f" | {k[6:]}: right {f(v['right'])} cap {f(v['cap'])}" for k, v in t.items() if k.startswith("minus_")))


if __name__ == "__main__":
    main()
