"""Readout of the fresh held-out set (specs/SPEC_fresh.md): the three models side by side, on all problems and by source group,
from the run folders that analysis/day1_vote.py wrote (rows.jsonl, readout.json). Laptop, no model.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.fresh_read --sft studies/rlneurons/results/fresh/sft1_cue_s4-01 \
        --rl studies/rlneurons/results/fresh/rl_plain_s4-01 --base studies/rlneurons/results/fresh/base_cue_s4-01 --out studies/rlneurons/results/fresh/readout-01 \
        [--texts runs/fresh_sft1_cue_s4 runs/fresh_rl_plain_s4 runs/fresh_base_cue_s4]

  --texts  the joined run folders with answers.jsonl (sft, rl, base): adds counts read from the answer texts (cap hits with more
           than 20 Chinese characters, finished answers with no extracted answer) and the rows of the problem SKIP.

Per model and group: one sample (mean of the samples), vote (day1_vote's per-problem vote), pass@k, cap-hit share of samples,
precision of finished answers (right / samples that ended before the cap), generated tokens per sample. Differences between
models: paired bootstrap over problems (5,000 resamples, seed 0), in points. Scores the predictions of the spec (PRED).
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib

import numpy as np

STUDY = pathlib.Path(__file__).resolve().parents[1]
BOOT = 5000
GROUPS = {"all": lambda s: True, "hf (AIME 2026 + HMMT Feb 2026, MathArena)": lambda s: s in ("aime2026", "hmmt_feb2026"),
          "pdf (transcribed: HMMT Feb Guts + HMMT Nov)": lambda s: s not in ("aime2026", "hmmt_feb2026"),
          "aime2026": lambda s: s == "aime2026", "hmmt_feb2026 (with Guts)": lambda s: s.startswith("hmmt_feb"),
          "hmmt_nov2026": lambda s: s.startswith("hmmt_nov"), "not hmmt_nov2026": lambda s: not s.startswith("hmmt_nov")}
SKIP = "hmmt_feb2026/9"       # grader v3 takes 50.0 for its gold 50(1 - 1/(2^101 - 1)) but not 50: every number also without it
PRED = {"vote_right": {"sft": (74, 62, 86), "rl": (64, 52, 76), "base": (49, 38, 60)},                # specs/SPEC_fresh.md, filed in 1232554
        "single_right": {"sft": (59, 49, 70), "rl": (54, 44, 65), "base": (36, 27, 46)},
        "cap_hit_percent": {"sft": (40, 30, 50), "rl": (14, 8, 22), "base": (33, 23, 43)},
        "precision_percent": {"sft": (80, 70, 88), "rl": (50, 40, 60), "base": (42, 32, 52)},
        "tokens_per_sample": {"sft": (12000, None, None), "rl": (11000, None, None), "base": (11000, None, None)}}


def load(folder: pathlib.Path) -> dict:
    """problem index -> {single, vote, pass, cap, finished, right_finished, tokens}: sums over the problem's samples (attempt 0)."""
    ro = json.loads((folder / "readout.json").read_text())
    vote, pk = (dict(zip(ro["problem_indices"], ro["per_problem"][k])) for k in ("vote", "pass_at_k"))
    by = collections.defaultdict(list)
    for line in (folder / "rows.jsonl").read_text().splitlines():
        r = json.loads(line)
        assert r["attempt"] == 0, "the fresh cells have no restarts"
        by[r["problem_index"]].append(r)
    k = ro["samples"]
    assert all(len(v) == k for v in by.values()) and sorted(by) == sorted(vote)
    return {i: {"single": sum(r["score_v3"] for r in rs) / k, "vote": vote[i], "pass": pk[i], "cap": sum(r["cap_hit"] for r in rs) / k,
                "finished": sum(not r["cap_hit"] for r in rs), "right_finished": sum(r["score_v3"] for r in rs if not r["cap_hit"]),
                "tokens": sum(r["n_new"] for r in rs) / k} for i, rs in by.items()}


def stats(p: dict, idx: list) -> dict:
    n = len(idx)
    fin = sum(p[i]["finished"] for i in idx)
    return {"n": n, "single_right": sum(p[i]["single"] for i in idx), "vote_right": sum(p[i]["vote"] for i in idx),
            "pass_at_k_right": sum(p[i]["pass"] for i in idx), "cap_hit_percent": 100 * sum(p[i]["cap"] for i in idx) / n,
            "precision_percent": 100 * sum(p[i]["right_finished"] for i in idx) / fin if fin else None,
            "tokens_per_sample": sum(p[i]["tokens"] for i in idx) / n}


def diff(a: dict, b: dict, idx: list, rng) -> dict:
    """a minus b on the problems idx, in points, with the paired bootstrap interval."""
    draws = rng.integers(0, len(idx), (BOOT, len(idx)))
    out = {}
    for key in ("vote", "single", "cap"):
        d = np.array([a[i][key] - b[i][key] for i in idx], float)
        out[key] = {"points": 100 * d.mean(), "interval95": [100 * x for x in np.percentile(d[draws].mean(1), [2.5, 97.5])]}
    f = {m: np.array([[p[i]["right_finished"], p[i]["finished"]] for i in idx], float) for m, p in (("a", a), ("b", b))}
    prec = lambda x: x[..., 0].sum(-1) / np.maximum(x[..., 1].sum(-1), 1)
    out["precision"] = {"points": 100 * (prec(f["a"]) - prec(f["b"])),
                        "interval95": [100 * x for x in np.percentile(prec(f["a"][draws]) - prec(f["b"][draws]), [2.5, 97.5])]}
    return out


def main():
    ap = argparse.ArgumentParser()
    for k in ("--sft", "--rl", "--base", "--out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--texts", nargs=3)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    probs = json.loads((STUDY / "data" / "fresh" / "fresh2026_v1.json").read_text())
    src = {p["index"]: p["source"] for p in probs}
    skip = next(p["index"] for p in probs if p["unique_id"] == SKIP)
    per = {m: load(pathlib.Path(getattr(a, m))) for m in ("sft", "rl", "base")}
    assert all(sorted(p) == sorted(src) for p in per.values()), "a run is not on the whole fresh set"
    rng = np.random.default_rng(0)
    res = {"set": "data/fresh/fresh2026_v1.json", "folders": {m: getattr(a, m) for m in per}, "groups": {}}
    for g, test in {**GROUPS, f"all without {SKIP}": lambda s: True}.items():
        idx = sorted(i for i, s in src.items() if test(s) and not (SKIP in g and i == skip))
        res["groups"][g] = {"models": {m: stats(p, idx) for m, p in per.items()},
                            "differences_points": {f"{x} - {y}": diff(per[x], per[y], idx, rng) for x, y in (("sft", "rl"), ("sft", "base"), ("rl", "base"))}}
    allm = res["groups"]["all"]["models"]
    res["predictions"] = {k: {m: {"predicted": v[0], "interval": [v[1], v[2]], "observed": allm[m][k],
                                  "inside": None if v[1] is None else bool(v[1] <= allm[m][k] <= v[2])} for m, v in d.items()} for k, d in PRED.items()}
    res["vote_right_for_one_model_only"] = {f"{x} not {y}": sum(per[x][i]["vote"] > per[y][i]["vote"] for i in src)
                                            for x, y in (("sft", "rl"), ("rl", "sft"), ("sft", "base"), ("base", "sft"), ("rl", "base"), ("base", "rl"))}
    if a.texts:
        res["texts"] = {}
        for m, d in zip(per, a.texts):
            rows = [json.loads(l) for l in (pathlib.Path(d) / "answers.jsonl").read_text().splitlines()]
            cap = [r for r in rows if r["cap_hit"]]
            res["texts"][m] = {"cap_hits": len(cap), "cap_hits_with_more_than_20_chinese_characters": sum(sum("\u4e00" <= c <= "\u9fff" for c in r["text"]) > 20 for r in cap),
                               "finished_without_extracted_answer": sum(not r["cap_hit"] and r["extracted_v3"] is None for r in rows),
                               "finished": sum(not r["cap_hit"] for r in rows),
                               SKIP: [{k: r[k] for k in ("sample", "cap_hit", "n_new", "extracted_v3", "score_v3")} for r in sorted(rows, key=lambda r: r["sample"]) if r["problem_index"] == skip]}
    out.mkdir(parents=True)
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    lines = ["| group | model | n | one sample | vote | pass@k | cap hits % | precision % | tokens per sample |", "|---|---|---|---|---|---|---|---|---|"]
    for g, d in res["groups"].items():
        for m, s in d["models"].items():
            lines.append(f"| {g} | {m} | {s['n']} | {s['single_right']:.1f} | {s['vote_right']} | {s['pass_at_k_right']} | {s['cap_hit_percent']:.1f} | "
                         f"{s['precision_percent']:.1f} | {s['tokens_per_sample']:,.0f} |")
    lines += ["", "| group | difference | vote, points | one sample, points | cap hits, points | precision, points |", "|---|---|---|---|---|---|"]
    cell = lambda x: f"{x['points']:+.1f} [{x['interval95'][0]:+.1f}, {x['interval95'][1]:+.1f}]"
    for g, d in res["groups"].items():
        for name, x in d["differences_points"].items():
            lines.append(f"| {g} | {name} | {cell(x['vote'])} | {cell(x['single'])} | {cell(x['cap'])} | {cell(x['precision'])} |")
    (out / "readout.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
