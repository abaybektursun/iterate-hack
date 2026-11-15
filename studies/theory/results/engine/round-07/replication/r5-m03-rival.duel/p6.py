"""Offline prediction k=6, recomputed from its recipe (offline.json)."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.getcwd())
from studies.theory.lib.noise import bootstrap, binomial, report, not_computable, refuted_without_number  # noqa: E402
from studies.rlneurons.lib import rln4_lib as R  # noqa: E402  grader v3, as called by studies/rlneurons/grader/rln4_grader_v3.py

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/"
TOP8 = "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
CUE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
T3_KEY = "r4/modal_t3-01/t3/T3.jsonl"
P_KEY = "r3/base-01/out/P_math500.jsonl"


def fetch(key):
    local = os.path.join("runs/theory-tests/s3", key)
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", BUCKET + key, local, "--profile", "iterate-ecr", "--only-show-errors"], check=True)
    return local


def read_jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def first_per_problem(rows):
    out = {}
    for r in rows:
        out.setdefault(r["problem_index"], r)
    return out


def min_sample_per_problem(rows):
    out = {}
    for r in rows:  # smallest sample value; ties keep the first in file order
        i = r["problem_index"]
        if i not in out or r["sample"] < out[i]["sample"]:
            out[i] = r
    return out


def v3(r):
    g = R.grade_v3(r["gold"], r.get("text") or "")
    return g["score_v3"], g["extracted_v3"]


def slim(r):
    out = {k: v for k, v in r.items() if k not in ("prefill_ids", "answer_tokens")}
    if isinstance(out.get("text"), str) and len(out["text"]) > 400:
        out["text"] = out["text"][:400] + "...[truncated]"
    return out


def top8_Q():
    """Top8 rows with score_v3 == 0, cap_hit false, n_generated <= 2000; missing score_v3 left out; first row per problem."""
    rows = json.load(open(TOP8))
    first = {}
    for r in rows:
        if r.get("score_v3") is None:
            continue
        first.setdefault(r["problem_index"], r)
    return {i: r for i, r in first.items() if r["score_v3"] == 0 and r["cap_hit"] is False and r["n_generated"] <= 2000}


def cue_k(alt=False):
    """problem_index -> k. Main: exactly 4 attempt-0 rows required, k = count of score_v3 == 1.
    alt: per (problem, sample) take the row with the highest attempt (final restart); exactly 4 samples required."""
    rows = read_jsonl(CUE)
    out = {}
    if not alt:
        by = {}
        for r in rows:
            if r["attempt"] == 0:
                by.setdefault(r["problem_index"], []).append(r)
        for i, rs in by.items():
            if len(rs) == 4:
                out[i] = sum(1 for r in rs if r["score_v3"] == 1)
        return out
    last = {}
    for r in rows:
        key = (r["problem_index"], r["sample"])
        if key not in last or r["attempt"] > last[key]["attempt"]:
            last[key] = r
    by = {}
    for (i, _), r in last.items():
        by.setdefault(i, []).append(r)
    for i, rs in by.items():
        if len(rs) == 4:
            out[i] = sum(1 for r in rs if r["score_v3"] == 1)
    return out


def diff_stat(groupA, groupB, fullA, fullB):
    """Statistic over a list of (group, value) entries: mean over A minus mean over B; an empty group in a resample
    falls back to the full-sample mean of that group."""
    def stat(sample):
        a = [v for g, v in sample if g == groupA]
        b = [v for g, v in sample if g == groupB]
        ma = sum(a) / len(a) if a else fullA
        mb = sum(b) / len(b) if b else fullB
        return ma - mb
    return stat


def main():
    t3 = first_per_problem(read_jsonl(fetch(T3_KEY)))
    P = min_sample_per_problem(read_jsonl(fetch(P_KEY)))
    for name, d in (("T3", t3), ("P_math500", P)):
        if d and "text" not in next(iter(d.values())):
            return not_computable(f"{name} rows have no text field")

    def wrong(r):
        s, ext = v3(r)
        return int(s == 0 or bool(r["cap_hit"]) or ext is None or (isinstance(ext, str) and not ext.strip()))

    wt = {i: wrong(r) for i, r in t3.items()}
    wp = {i: wrong(r) for i, r in P.items()}

    def split(k):
        S = [i for i in sorted(k) if k[i] == 4 and i in t3 and i in P]
        return [i for i in S if wp[i]], [i for i in S if not wp[i]]

    pw, pr = split(cue_k())
    print(json.dumps({"groups": {"P_wrong": len(pw), "P_right": len(pr)}}))
    if not pw or not pr:
        return not_computable("a conditioning group is empty; the recipe says report nothing")
    a = sum(wt[i] for i in pw) / len(pw)
    b = sum(wt[i] for i in pr) / len(pr)
    entries = [("Pw", wt[i]) for i in pw] + [("Pr", wt[i]) for i in pr]
    stat = diff_stat("Pw", "Pr", a, b)
    # alt: cued k from each sample's final attempt (after restarts) instead of attempt 0
    pwa, pra = split(cue_k(alt=True))
    alt = (sum(wt[i] for i in pwa) / len(pwa) - sum(wt[i] for i in pra) / len(pra)) if pwa and pra else None
    report(a - b, min(len(pw), len(pr)), bootstrap(stat, entries), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=slim(t3[pw[0]]))


main()
