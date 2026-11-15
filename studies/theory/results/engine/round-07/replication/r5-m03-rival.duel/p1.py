"""Offline prediction k=1, recomputed from its recipe (offline.json)."""
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
    Q = top8_Q()
    t3 = first_per_problem(read_jsonl(fetch(T3_KEY)))
    if t3 and "text" not in next(iter(t3.values())):
        return not_computable("T3 rows have no text field")
    entries = []
    for i in sorted(Q):
        if i not in t3:
            continue
        r = t3[i]
        s, _ = v3(r)
        wrong = int(s == 0 or bool(r["cap_hit"]))
        wrong_alt = int(s == 0)  # alt: wrong by v3 score alone, cap_hit not counted separately
        entries.append((wrong, wrong_alt, r))
    if not entries:
        return not_computable("no problem in Q has a T3 row")
    stat = lambda xs: sum(e[0] for e in xs) / len(xs)
    m = stat(entries)
    alt = sum(e[1] for e in entries) / len(entries)
    report(m, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=slim(entries[0][2]))


main()
