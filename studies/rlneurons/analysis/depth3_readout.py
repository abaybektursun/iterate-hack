"""depth3 readout (specs/SPEC_depth3.md): the layer bands and the directions 2 to 8 of the Math 3.1 top-8 edit at 1.5, with more
samples and a random control in layers 0 to 10. hard328 (n 328), cue, T 1.0 / top-p 1.0, cap 16,384, grader v3 as written by run_cell.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.depth3_readout

Run from the repository root. Inputs: runs/<job-id>/ of every job in NEW and OLD (`uv run tools/gpu.py get <job-id>`, not committed)
and the committed rows of REFS. Writes results/xreward/depth3/: readout.json; one run folder <cell>_s<sample>-01/ per new sample
(run.json, metrics.json joined from its two shards, examples.json, rows.jsonl); sample0_rows/<cell>.jsonl, the per-problem rows of
the four older one-sample jobs. Fails if a run folder exists.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from studies.rlneurons.analysis.shard_join import join

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "xreward" / "depth3"
SEED0 = 3000000                                                     # sample s of problem i has seed SEED0 + 10000 s + i
# cell -> {sample: (job of shard 0/2, job of shard 1/2)}; wsp_edit arguments in EDIT
NEW = {
    "top8x1.5_L0-10_math31": {1: ("abaybektursun-1115-122708-c6c1", "abaybektursun-1115-122720-ad28"),
                              2: ("abaybektursun-1115-122733-bc4c", "abaybektursun-1115-122746-2593"),
                              3: ("abaybektursun-1115-122759-39f3", "abaybektursun-1115-122810-7b2d")},
    "rand8x1.5_L0-10_math31": {1: ("abaybektursun-1115-122822-c211", "abaybektursun-1115-122835-f7eb")},
    "top8x1.5_d2-8_math31": {1: ("abaybektursun-1115-122847-824c", "abaybektursun-1115-122859-b197")},
    "top8x1.5_L11-21_math31": {1: ("abaybektursun-1115-122912-8aec", "abaybektursun-1115-122924-d28b")},
    "top8x1.5_L22-31_math31": {1: ("abaybektursun-1115-122936-1b30", "abaybektursun-1115-122949-e563")},
}
EDIT = {"top8x1.5_L0-10_math31": "--recipe top8 --layers 0-10 --scale 1.5", "rand8x1.5_L0-10_math31": "--recipe rand8 --layers 0-10 --scale 1.5",
        "top8x1.5_d2-8_math31": "--recipe top8 --skip 1 --scale 1.5", "top8x1.5_L11-21_math31": "--recipe top8 --layers 11-21 --scale 1.5",
        "top8x1.5_L22-31_math31": "--recipe top8 --layers 22-31 --scale 1.5"}
OLD = {"top8x1.5_L0-10_math31": "abaybektursun-1115-105312-7e19", "top8x1.5_L11-21_math31": "abaybektursun-1115-105324-5f61",       # sample 0, one job each
       "top8x1.5_L22-31_math31": "abaybektursun-1115-105335-a886", "rand8x1.5_math31": "abaybektursun-1115-090241-0229"}
REFS = {"base_cue": STUDY / "results" / "day1_3" / "hard328_base_cue_s4r2-01" / "rows.jsonl",                                        # 4 samples, attempt 0
        "top8x1.5_math31": STUDY / "results" / "xreward" / "dial15_s4_vs_base_cue-01" / "rows.jsonl"}
RAND = {"top8x1.5_L0-10_math31": "rand8x1.5_L0-10_math31"}                                                                           # default: rand8x1.5_math31
KEEP = ("problem_index", "sample", "attempt", "seed", "n_new", "cap_hit", "finish_reason", "loop_A", "extracted_v3", "score_v3", "gold")
B, RNG = 10000, 0


def read(path):
    return [json.loads(l) for l in pathlib.Path(path).read_text().splitlines()]


def compact(rows, sample):
    out = []
    for r in sorted(rows, key=lambda r: r["problem_index"]):
        assert r["attempt"] == 0 and r["seed"] == SEED0 + 10000 * sample + r["problem_index"], (r["problem_index"], r["seed"], sample)
        out.append({**{k: r[k] for k in KEEP}, "sample": sample})
    return out


def example(r):
    return {"problem_index": r["problem_index"], "seed": r["seed"], "gold": r["gold"], "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"],
            "cap_hit": bool(r["cap_hit"]), "n_new": r["n_new"], "prompt_tail": r["prompt"][-400:], "answer_tail": r["text"][-800:]}


def diff(a, b, rng):
    """a, b: per-problem means [n] -> the difference of their means in points of n and its 95 % interval over resampled problems."""
    d = a - b
    boot = d[rng.integers(0, len(d), (B, len(d)))].mean(1)
    return {"points": round(100 * d.mean(), 2), "interval95": [round(100 * x, 2) for x in np.percentile(boot, [2.5, 97.5])], "problems": round(d.sum(), 2)}


def main():
    cells = {}                                                       # cell -> {sample: compact rows}
    for cell, path in REFS.items():
        for r in read(path):
            if r["attempt"] == 0:
                cells.setdefault(cell, {}).setdefault(r["sample"], []).append(r)
        cells[cell] = {s: compact(rows, s) for s, rows in cells[cell].items()}
    (OUT / "sample0_rows").mkdir(parents=True)
    for cell, job in OLD.items():
        m = json.loads((RUNS / job / "metrics.json").read_text())
        assert m["status"] == "done" and m["config"]["model_label"] == cell and m["config"]["seed"] == SEED0, (job, m["status"])
        cells.setdefault(cell, {})[0] = compact(read(RUNS / job / "answers.jsonl"), 0)
        (OUT / "sample0_rows" / f"{cell}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in cells[cell][0]))
    for cell, samples in NEW.items():
        for s, jobs in samples.items():
            m, rows = join([(json.loads((RUNS / j / "metrics.json").read_text()), read(RUNS / j / "answers.jsonl")) for j in jobs])
            c = m["config"]
            assert (c["model_label"], c["seed"], c["prompt"], c["set"], c["temperature"], c["top_p"], c["max_tokens"]) == \
                (cell, SEED0 + 10000 * s, "cue", "hard328", 1.0, 1.0, 16384), c
            cells.setdefault(cell, {})[s] = compact(rows, s)
            d = OUT / f"{cell}_s{s}-01"
            d.mkdir()
            cmd = (f"wsp_edit {EDIT[cell]} --other math31 --rounding stochastic --seed 0, then run_cell --model-label {cell} --prompt cue --set hard328 "
                   f"--temperature 1.0 --top-p 1.0 --seed {c['seed']} --shard k/2 (k = 0, 1), joined by analysis/shard_join.join")
            (d / "run.json").write_text(json.dumps({"job_ids": list(jobs), "commit": m["commit"], "command": cmd, "runner": "uv run tools/gpu.py submit h100 --hours 1.5",
                                                    "raw_answers": [f"runs/{j}/answers.jsonl (uv run tools/gpu.py get {j})" for j in jobs],
                                                    "edit": json.loads((RUNS / jobs[0] / "edit.json").read_text())["totals"]}, indent=1) + "\n")
            (d / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
            (d / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in cells[cell][s]))
            rows = sorted(rows, key=lambda r: r["problem_index"])
            (d / "examples.json").write_text(json.dumps({"right": example(next(r for r in rows if r["score_v3"] == 1)),
                                                         "wrong": example(next(r for r in rows if r["score_v3"] == 0 and not r["cap_hit"]))}, indent=1) + "\n")

    idx = sorted(r["problem_index"] for r in cells["base_cue"][0])
    assert len(idx) == 328
    arr = {}                                                         # cell -> {"right" | "cap": [samples, 328]}
    for cell, samples in cells.items():
        for s, rows in samples.items():
            assert [r["problem_index"] for r in rows] == idx, (cell, s, len(rows))
        arr[cell] = {key: np.array([[float(r[f]) for r in samples[s]] for s in sorted(samples)]) for key, f in (("right", "score_v3"), ("cap", "cap_hit"))}
    rng = np.random.default_rng(RNG)
    table = {}
    for cell in arr:
        right, cap = arr[cell]["right"], arr[cell]["cap"]
        fin = right.sum() / (1 - cap).sum()
        t = {"samples": sorted(cells[cell]), "right": [int(x) for x in right.sum(1)], "right_mean": round(right.sum(1).mean(), 2),
             "cap_hits": [int(x) for x in cap.sum(1)], "cap_hits_mean": round(cap.sum(1).mean(), 2), "right_per_finished": round(float(fin), 3),
             "cap_hits_right": int((right * cap).sum())}
        refs = {"base_cue": "base_cue", "random": RAND.get(cell, "rand8x1.5_math31"), "top8x1.5_math31": "top8x1.5_math31"}
        for name, ref in refs.items():
            if ref != cell and cell not in ("base_cue",) and not (name == "random" and cell.startswith("rand8")):
                t[f"minus_{name}"] = {"reference": ref, "reference_samples": sorted(cells[ref]),
                                      **{key: diff(arr[cell][key].mean(0), arr[ref][key].mean(0), rng) for key in ("right", "cap")}}
        table[cell] = t
    a, r = arr["top8x1.5_L0-10_math31"], arr["rand8x1.5_L0-10_math31"]   # B3 as specified: sample 1 of each
    table["top8x1.5_L0-10_math31"]["minus_random_sample_1"] = {"reference": "rand8x1.5_L0-10_math31", **{key: diff(a[key][1], r[key][0], rng) for key in ("right", "cap")}}
    out = {"spec": "studies/rlneurons/specs/SPEC_depth3.md", "set": "hard328, n 328", "settings": "cue, T 1.0 / top-p 1.0, cap 16,384, grader v3 (score_v3 of run_cell)",
           "seed_rule": f"{SEED0} + 10000 * sample + problem index",
           "differences": f"per problem, mean over the cell's samples minus mean over the reference's samples; points of 328; 95 % interval from {B} resamples of the problems (numpy seed {RNG}); 'problems' = points * 3.28",
           "sources": {**{k: str(v) for k, v in REFS.items()}, **{f"{k} sample 0": f"runs/{v}" for k, v in OLD.items()},
                       **{f"{k} sample {s}": [f"runs/{j}" for j in jobs] for k, ss in NEW.items() for s, jobs in ss.items()}},
           "cells": table}
    (OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    for cell, t in table.items():
        f = lambda d: f"{d['points']:+.1f} [{d['interval95'][0]:.1f}, {d['interval95'][1]:.1f}]"
        print(f"{cell:26s} n {len(t['samples'])} right {t['right_mean']:6.1f} {t['right']} cap {t['cap_hits_mean']:5.1f} {t['cap_hits']} r/fin {t['right_per_finished']}"
              + "".join(f" | {k[6:]}: right {f(v['right'])} cap {f(v['cap'])}" for k, v in t.items() if k.startswith("minus_")))


if __name__ == "__main__":
    main()
