"""Offline prediction k=5, recomputed from its recipe (offline.json)."""
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
    P = min_sample_per_problem(read_jsonl(fetch(P_KEY)))
    if P and "text" not in next(iter(P.values())):
        return not_computable("P_math500 rows have no text field")
    score, self_open, self_open_alt = {}, {}, {}
    for i, r in P.items():
        text = r.get("text") or ""
        s, ext = v3(r)
        if ext is None or bool(r["cap_hit"]):
            s = 0
        score[i] = s
        self_open[i] = "\nOkay" in text[:60]           # main: newline followed by Okay within the first 60 characters
        self_open_alt[i] = "Okay" in text[:60]         # alt: Okay anywhere in the first 60 characters (also at position 0)

    def contrast(k, so):
        kept = [i for i in sorted(score) if not so[i] and i in k]
        E = [i for i in kept if k[i] == 4]
        H = [i for i in kept if k[i] <= 1]
        return E, H

    k = cue_k()
    E, H = contrast(k, self_open)
    print(json.dumps({"groups": {"E_cued_4of4": len(E), "H_cued_le1of4": len(H)}}))
    if not E or not H:
        return not_computable("group E or group H is empty; the recipe says report nothing")
    mE = sum(score[i] for i in E) / len(E)
    mH = sum(score[i] for i in H) / len(H)
    entries = [("E", score[i]) for i in E] + [("H", score[i]) for i in H]
    stat = diff_stat("E", "H", mE, mH)
    Ea, Ha = contrast(k, self_open_alt)
    alt = (sum(score[i] for i in Ea) / len(Ea) - sum(score[i] for i in Ha) / len(Ha)) if Ea and Ha else None
    report(mE - mH, min(len(E), len(H)), bootstrap(stat, entries), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=slim(P[E[0]]))


main()
