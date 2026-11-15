"""duel-r7-account p3: share of math500-thinksft-T1 gap problems assigned to reliability (R4).

B = base + cue (per_problem.json t1_right / t1_cap_hit; text and gold from r4 base_rl-02 T1.jsonl).
O = Think-SFT + cue (studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json, score_v3, cap hit = cap_hit true).
E = base-01 P_math500 sample-0 row + r4 modal_t3-01 T3 row, both regraded with grader v3.
Rules in order: R1 loop, R2 budget, R3 answer-statement, R4 reliability, R5 deliberation, else unassigned.
"""
import json
import os
import re
import subprocess
import zlib

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable

TARGET = "reliability"
O_KIND = "per_problem"
O_PATH = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"
O_FETCH = None  # committed file

D = "runs/theory-tests/duel-r7-account"
B_PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
FILES = {
    "T1": (f"{D}/T1.jsonl", "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"),
    "P": (f"{D}/base-01_P_math500.jsonl", "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"),
    "T3": (f"{D}/T3.jsonl", "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"),
}


def fetch():
    os.makedirs(D, exist_ok=True)
    for path, uri in FILES.values():
        if not os.path.exists(path):
            subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr", "--only-show-errors"], check=True)
    if O_FETCH and not os.path.exists(O_PATH):
        os.makedirs(os.path.dirname(O_PATH), exist_ok=True)
        subprocess.run(O_FETCH, check=True)


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def first_by_pi(rows, cond=lambda r: True):
    out = {}
    for r in rows:
        if cond(r) and r.get("problem_index") not in out:
            out[r.get("problem_index")] = r
    return out


def cap_hit(r):
    """cap hit = cap_hit true, or cap_hit missing and finish_reason == 'length'."""
    c = r.get("cap_hit")
    if c is None:
        return r.get("finish_reason") == "length"
    return c is True


def v3_right(r, honour_cap=True):
    """v3 regrade of a row's text and gold; right iff v3 right and (main reading) not a cap hit."""
    text, gold = r.get("text"), r.get("gold")
    if gold is None:
        return False
    g = rln4_lib.grade_v3(gold, text if text is not None else "")["score_v3"] == 1
    return g and (not cap_hit(r) if honour_cap else True)


def rule_a(text):
    if text is None or len(text) < rln4_lib.W:
        return False
    n = len(text)
    starts = [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]
    for p in starts:
        if n - p < 8000:
            continue
        b = text[p:p + 8000].encode("utf-8")
        if len(zlib.compress(b)) / len(b) < 0.10:
            return True
    return False


def N(s):
    s = re.sub(r"\s", "", s)
    for t in ("$", "*", "#", "\\left", "\\right"):
        s = s.replace(t, "")
    return s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")


def r3_taken(text, gold):
    if text is None:
        return True
    lines = [N(l) for l in text.split("\n")]
    if not any("\\boxed{" in l for l in lines) and not any(l.startswith("Answer:") for l in lines):
        return True
    if gold is None:
        return False
    g = N(gold)
    return any(("\\boxed{" + g + "}") in l for l in lines) or any(l == "Answer:" + g or l == "Answer:" + g + "." for l in lines)


def assign(b_cap, t1row, kB, e_n):
    text = t1row.get("text") if t1row is not None else None
    gold = t1row.get("gold") if t1row is not None else None
    if b_cap and rule_a(text):
        return "loop"
    if b_cap:
        return "budget"
    if r3_taken(text, gold):
        return "answer-statement"
    if kB >= 1:
        return "reliability"
    if e_n > 0 and kB == 0:
        return "deliberation"
    return "unassigned"


def main():
    fetch()
    B = first_by_pi(json.load(open(B_PP)))
    T1 = first_by_pi(read_jsonl(FILES["T1"][0]))
    P = first_by_pi(read_jsonl(FILES["P"][0]), lambda r: r.get("sample") == 0)
    T3 = first_by_pi(read_jsonl(FILES["T3"][0]))
    if O_KIND == "answers":
        O = first_by_pi(read_jsonl(O_PATH))
        o_cap = cap_hit
    else:
        O = first_by_pi(json.load(open(O_PATH)))
        o_cap = lambda r: r.get("cap_hit") is True

    gaps = []  # (problem_index, main label, alt label, B row)
    for pi in sorted(set(B) & set(O), key=lambda x: (x is None, x)):
        b, o = B[pi], O[pi]
        if b.get("t1_right") is None or o.get("score_v3") is None:
            continue
        b_cap = b.get("t1_cap_hit") is True
        b_right = b["t1_right"] == 1 and not b_cap
        o_right = o["score_v3"] == 1 and not o_cap(o)
        if not (o_right and not b_right):
            continue
        E = [r for r in (P.get(pi), T3.get(pi)) if r is not None]
        kB = sum(v3_right(r) for r in E)
        kB_alt = sum(v3_right(r, honour_cap=False) for r in E)
        t1row = T1.get(pi)
        gaps.append((pi, assign(b_cap, t1row, kB, len(E)), assign(b_cap, t1row, kB_alt, len(E)), b))

    if not gaps:
        not_computable("no gap problems (O right and B wrong); the statistic's denominator is zero")
        return

    def stat(sample):
        return sum(1 for g in sample if g[1] == TARGET) / len(sample)

    measured = stat(gaps)
    alt = sum(1 for g in gaps if g[2] == TARGET) / len(gaps)
    report(measured, len(gaps), bootstrap(stat, gaps), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=gaps[0][3])


if __name__ == "__main__":
    main()
