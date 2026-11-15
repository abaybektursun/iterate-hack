"""Answer-statement repair, Part A (specs/SPEC_repair.md, idea-ae6eba): offline, attempt 0 of samples 0 to 3 of the two
Day-1 #3 jobs. (a) upper bound that reads the gold; (b) label-free rules R1 to R5 and grader v4 against grader v3, per rule,
with the vote over 4; how right answers end (for Part B's suffix) and the samples Part B is eligible for.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.repair \
        --base runs/abaybektursun-1114-153825-208b --rl runs/abaybektursun-1114-183640-e828 \
        --out studies/rlneurons/results/repair/offline-01

Writes readout.json, rows.jsonl (one line per sample, no text), flips.json (every sample whose score v4 changes, with the
last 700 characters), upper_bound_read.json (the samples drawn for the hand reading), examples.json, run.json. Fails if the
out folder exists.
"""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing
import pathlib
import random
import re
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import anatomy as A
from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.grader import repair_v4 as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

BOOT, K, MAXVAL, TAIL = 5000, 4, 200, 700
RULESETS = [(r,) for r in G.RULES] + [G.RULES]


def nonempty_starts(text: str) -> list:
    out, c = [], 0
    for ln in text.split("\n"):
        if ln.strip():
            out.append(c)
        c += len(ln) + 1
    return out


def values(text: str) -> dict:
    """{value string: offset of its last occurrence}: boxes, v3 marker rests, one-line math spans, and the part after the last
    '=' of a span."""
    out = {}
    for i, _, b in R._boxes(text):
        out[b.strip()] = i
    for m in R.MARK_V3.finditer(text):
        end = text.find("\n", m.end())
        rest = R.DELIM_V3.sub("", text[m.end():len(text) if end < 0 else end]).strip().strip("*_").strip()
        if rest:
            out[rest] = m.end()
    for m in G.SPAN.finditer(text):
        v = next(g for g in m.groups() if g is not None).strip()
        for x in (v, v.rsplit("=", 1)[-1].strip()):
            if x:
                out[x] = m.start()
    return {v: o for v, o in out.items() if len(v) <= MAXVAL}


def upper_bound(job: tuple) -> dict:
    gold, text = job
    starts = nonempty_starts(text)
    if not starts:
        return {"last_line": False, "last5": False, "anywhere": False, "value": None}
    hits = {v: o for v, o in values(text).items() if S.grade(R.norm_v3(gold), R.norm_v3(v))["score"] == 1}
    last = max(hits.values(), default=-1)
    return {"last_line": last >= starts[-1], "last5": last >= starts[-5:][0], "anywhere": bool(hits),
            "value": max(hits, key=hits.get) if hits else None}


def ending(r: dict) -> str:
    """How a right answer introduces its final answer: the text of the answer's line before the extracted candidate, digits as #."""
    _, _, start = R.extract_v3(r["text"])
    line = r["text"][r["text"].rfind("\n", 0, start) + 1:start]
    return re.sub(r"\d+", "#", line.strip())[-40:]


def boot(x, y) -> dict:
    x, y = np.asarray(x, float), np.asarray(y, float)
    lo, hi = S.paired_bootstrap(x, y, n_boot=BOOT, seed=0)
    return {"diff_points": float(100 * (x.mean() - y.mean())), "ci95": [lo, hi]}


def tail(r: dict, g: dict) -> dict:
    return {"problem_index": r["problem_index"], "sample": r["sample"], "gold": r["gold"], "kind": A.kind(r),
            "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "extracted_v4": g["extracted_v4"],
            "score_v4": g["score_v4"], "fired": g["fired_v4"], "n_new": r["n_new"], "text_tail": r["text"][-TAIL:]}


def model_readout(bank: dict, pool) -> tuple:
    n = len(bank)
    flat = [bank[i][s] for i in sorted(bank) for s in range(K)]
    s3 = np.array([[bank[i][s]["score_v3"] for s in range(K)] for i in sorted(bank)])
    kinds = collections.Counter(A.kind(r) for r in flat)
    # (a) upper bound on the wrong samples
    wrong = [r for r in flat if not r["score_v3"]]
    ub = pool.map(upper_bound, [(r["gold"], r["text"]) for r in wrong], chunksize=4)
    ub_table = {k: {"samples": sum(A.kind(r) == k for r in wrong),
                    **{f: sum(u[f] for r, u in zip(wrong, ub) if A.kind(r) == k) for f in ("last_line", "last5", "anywhere")}}
                for k in ("finished_wrong", "no_answer", "cap_hit")}
    ubk = {(r["problem_index"], r["sample"]): u for r, u in zip(wrong, ub)}
    # (b) rules
    rules, grades = {}, {}
    for rs in RULESETS:
        name = "v4" if len(rs) > 1 else rs[0]
        g = []
        for r in flat:
            mode, ext, fired = G.extract_v4(r["text"], r["finish_reason"], rs)
            if not fired:
                assert ext == r["extracted_v3"], (r["problem_index"], r["sample"])
                g.append({"extracted_v4": ext, "score_v4": r["score_v3"], "fired_v4": []})
            else:
                g.append({k: v for k, v in G.grade_v4(r["gold"], r["text"], r["finish_reason"], rs).items() if k != "mode_v4"})
        sv = np.array([x["score_v4"] for x in g]).reshape(n, K)
        rules[name] = {"right_samples": int(sv.sum()), "right_per_sample": [int(v) for v in sv.sum(0)],
                       "fired_samples": sum(bool(x["fired_v4"]) for x in g),
                       "wrong_to_right": int(((sv == 1) & (s3 == 0)).sum()), "right_to_wrong": int(((sv == 0) & (s3 == 1)).sum()),
                       "minus_v3_mean_of_4": boot(sv.mean(1), s3.mean(1)), "minus_v3_sample0": boot(sv[:, 0], s3[:, 0])}
        grades[name] = g
    g4 = grades["v4"]
    # vote over 4 under v3 and under v4 extraction
    v3_vote, v4_vote = [], []
    for k, i in enumerate(sorted(bank)):
        rows4 = [dict(bank[i][s], extracted_v3=g4[K * k + s]["extracted_v4"], score_v3=g4[K * k + s]["score_v4"]) for s in range(K)]
        v3_vote.append(V.vote(bank[i])["score"])
        v4_vote.append(V.vote(rows4)["score"])
    v3_vote, v4_vote = np.array(v3_vote), np.array(v4_vote)
    idx = sorted(bank)
    vote = {"v3": int(v3_vote.sum()), "v4": int(v4_vote.sum()), "minus_v3": boot(v4_vote, v3_vote),
            "fixed_problems": [idx[j] for j in np.flatnonzero((v4_vote == 1) & (v3_vote == 0))],
            "broken_problems": [idx[j] for j in np.flatnonzero((v4_vote == 0) & (v3_vote == 1))]}
    # endings of right answers, and Part B eligibility (finished, v3 extraction unusable; never reads the gold)
    right = [r for r in flat if r["score_v3"]]
    ends = collections.Counter(ending(r) for r in right).most_common(12)
    modes = collections.Counter(R.extract_v3(r["text"])[0] for r in right)
    elig = [r for r in flat if r["finish_reason"] == "stop" and G.unusable(r["extracted_v3"])]
    rows = [{"problem_index": r["problem_index"], "sample": r["sample"], "kind": A.kind(r), "finish_reason": r["finish_reason"],
             "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], **g, "fired_alone": [n for n in G.RULES if grades[n][j]["fired_v4"]],
             "upper_bound": ubk.get((r["problem_index"], r["sample"])), "eligible_part_b": r["finish_reason"] == "stop" and G.unusable(r["extracted_v3"])}
            for j, (r, g) in enumerate(zip(flat, g4))]
    flips = [tail(r, g) for r, g in zip(flat, g4) if g["score_v4"] != r["score_v3"]]
    changed_wrong = [tail(r, g) for r, g in zip(flat, g4) if g["fired_v4"] and g["score_v4"] == r["score_v3"]]
    rng = random.Random(0)
    cand = [r for r, u in zip(wrong, ub) if u["last5"] and not r["cap_hit"]]
    read = [dict(tail(r, g4[flat.index(r)]), gold_equal_value=ubk[(r["problem_index"], r["sample"])]["value"])
            for r in rng.sample(cand, min(20, len(cand)))]
    out = {"n_problems": n, "samples": len(flat), "right_v3_samples": int(s3.sum()), "right_v3_per_sample": [int(v) for v in s3.sum(0)],
           "kinds": dict(kinds), "upper_bound_wrong_samples": ub_table, "rules": rules, "vote": vote,
           "right_answer_modes_v3": dict(modes), "right_answer_endings_top12": ends,
           "eligible_part_b": {"samples": len(elig), "placeholder": sum(r["extracted_v3"] is not None for r in elig),
                               "no_answer": sum(r["extracted_v3"] is None for r in elig),
                               "right_under_v4": sum(g["score_v4"] for r, g in zip(flat, g4) if r in elig)}}
    return out, rows, flips, changed_wrong, read, np.array([x["score_v4"] for x in g4]).reshape(n, K), s3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--rl", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True)
    res, files = {}, {}
    with multiprocessing.Pool() as pool:
        for name, run in (("base_cue", a.base), ("rl", a.rl)):
            res[name], rows, flips, changed, read, s4, s3 = model_readout(A.load(pathlib.Path(run)), pool)
            files[name] = (rows, flips, changed, read, s4, s3)
    b4, b3, r4, r3 = files["base_cue"][4], files["base_cue"][5], files["rl"][4], files["rl"][5]
    res["rl_minus_base"] = {"v3_mean_of_4": boot(r3.mean(1), b3.mean(1)), "v4_mean_of_4": boot(r4.mean(1), b4.mean(1)),
                            "v3_sample0": boot(r3[:, 0], b3[:, 0]), "v4_sample0": boot(r4[:, 0], b4[:, 0]),
                            "gap_change_mean_of_4": boot((r4 - b4).mean(1), (r3 - b3).mean(1))}
    (out / "readout.json").write_text(json.dumps(res, indent=1))
    (out / "rows.jsonl").write_text("".join(json.dumps(dict(r, model=m)) + "\n" for m in files for r in files[m][0]))
    (out / "flips.json").write_text(json.dumps({m: {"score_changed": files[m][1], "extraction_changed_score_same": files[m][2]} for m in files}, indent=1))
    (out / "upper_bound_read.json").write_text(json.dumps({m: files[m][3] for m in files}, indent=1))
    fl = files["base_cue"][1]
    (out / "examples.json").write_text(json.dumps({
        "v4_right_v3_wrong": next((f for f in fl if f["score_v4"] == 1), None),
        "v4_wrong_although_gold_in_last5": next((f for f in files["base_cue"][3] if f["score_v4"] == 0), None)}, indent=1))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(sys.argv), "base_job": pathlib.Path(a.base).name,
                                              "rl_job": pathlib.Path(a.rl).name, "grader": "v3 (stored) and grader/repair_v4.py",
                                              "spec": "studies/rlneurons/specs/SPEC_repair.md"}, indent=1))
    print(json.dumps({m: {k: res[m][k] for k in ("kinds", "upper_bound_wrong_samples", "vote", "eligible_part_b")} for m in files}, indent=1))
    for m in files:
        for k, v in res[m]["rules"].items():
            print(m, k, v)
    print(res["rl_minus_base"])


if __name__ == "__main__":
    main()
