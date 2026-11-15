"""Prediction k=1: share of math500-theta05cue-T1 gap problems assigned to reliability (rule R4).

B = base + cue, T1 (per_problem.json t1_right / t1_cap_hit; text and gold from S3 r4/base_rl-02 T1.jsonl).
O = theta0.5 + cue (iterate-runs 152855-683b answers.jsonl, first row per problem_index, score_v3).
E = r3/base-01 P_math500 sample-0 row + r4/modal_t3-01 T3 row, v3 regrade. Rules R1..R5 in order.
"""
import json
import os
import subprocess
import zlib

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

TARGET = "reliability"

D = "runs/theory-tests/repl-r7-account.duel"
PER_PROBLEM = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
FILES = {
    "T1": (f"{D}/T1.jsonl", ["aws", "s3", "cp", "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"]),
    "P": (f"{D}/P_math500.jsonl", ["aws", "s3", "cp", "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"]),
    "T3": (f"{D}/T3.jsonl", ["aws", "s3", "cp", "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"]),
    "O": (f"{D}/683b_answers.jsonl", ["modal", "volume", "get", "iterate-runs", "abaybektursun-1114-152855-683b/answers.jsonl"]),
}


def fetch(key):
    path, cmd = FILES[key]
    if not os.path.exists(path):
        os.makedirs(D, exist_ok=True)
        if cmd[0] == "aws":
            subprocess.run(cmd + [path, "--profile", "iterate-ecr", "--quiet"], check=True)
        else:
            subprocess.run(cmd + [path], check=True)
    return path


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def first_by_pi(rows, pred=lambda r: True):
    out = {}
    for r in rows:
        if pred(r) and r.get("problem_index") is not None and r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return out


def is_cap(r):
    """cap hit = cap_hit true, or cap_hit missing and finish_reason == 'length'."""
    if r.get("cap_hit") is None:
        return r.get("finish_reason") == "length"
    return r["cap_hit"] is True


def v3_right(r):
    text = r.get("text")
    gold = r.get("gold")
    if text is None or gold is None:
        return None
    return rln4_lib.grade_v3(gold, text)["score_v3"] == 1


def rule_a(text):
    if not text:
        return False
    L = len(text)
    for p in range(L):
        if p == 0 or text[p - 1] == "\n":
            if L - p < 8000:
                break
            b = text[p:p + 8000].encode("utf-8")
            if len(zlib.compress(b)) / len(b) < 0.10:
                return True
    return False


def N(s):
    s = "".join(s.split())
    for t in ("$", "*", "#", "\\left", "\\right"):
        s = s.replace(t, "")
    return s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")


def r3_taken(text, gold):
    if text is None:
        return True
    g = N(gold if gold is not None else "")
    lines = [N(l) for l in text.split("\n")]
    none_stated = not any("\\boxed{" in l for l in lines) and not any(l.startswith("Answer:") for l in lines)
    boxed = any(("\\boxed{" + g + "}") in l for l in lines)
    ans = any(l == "Answer:" + g or l == "Answer:" + g + "." for l in lines)
    return none_stated or boxed or ans


def main():
    for k in FILES:
        fetch(k)
    pp = json.load(open(PER_PROBLEM))
    t1 = first_by_pi(load_jsonl(FILES["T1"][0]))
    O = first_by_pi(load_jsonl(FILES["O"][0]))
    P = first_by_pi(load_jsonl(FILES["P"][0]), lambda r: r.get("sample") == 0)
    T3 = first_by_pi(load_jsonl(FILES["T3"][0]))

    gap = []  # one entry per gap problem: dict with rule (main) and rule (alt)
    for b in pp:
        pi = b["problem_index"]
        o = O.get(pi)
        if o is None:
            continue
        if b.get("t1_right") is None or o.get("score_v3") is None:
            continue
        b_cap = b.get("t1_cap_hit") is True
        b_right = (b["t1_right"] == 1) and not b_cap
        o_right = (o["score_v3"] == 1) and not is_cap(o)
        if not (o_right and not b_right):
            continue
        trow = t1.get(pi)
        text = trow.get("text") if trow is not None else None
        gold = trow.get("gold") if trow is not None else None
        E = [r for r in (P.get(pi), T3.get(pi)) if r is not None]
        grades = [v3_right(r) for r in E]
        kB = sum(1 for r, g in zip(E, grades) if g and not is_cap(r))
        kB_alt = sum(1 for g in grades if g)  # alt: v3 grade alone, cap hits not forced wrong

        def assign(k):
            if b_cap and rule_a(text):
                return "loop"
            if b_cap:
                return "budget"
            if r3_taken(text, gold):
                return "answer-statement"
            if k >= 1:
                return "reliability"
            if E and k == 0:
                return "deliberation"
            return "unassigned"

        main_rule = assign(kB)
        alt_rule = main_rule if main_rule in ("loop", "budget", "answer-statement") else assign(kB_alt)
        gap.append({"problem_index": pi, "rule": main_rule, "rule_alt": alt_rule, "kB": kB, "nE": len(E),
                    "b_row": b})

    if not gap:
        not_computable("no gap problems (O right and B wrong) in the stored rows: the fraction has an empty denominator")
        return

    def stat(sample):
        return sum(1 for g in sample if g["rule"] == TARGET) / len(sample)

    def stat_alt(sample):
        return sum(1 for g in sample if g["rule_alt"] == TARGET) / len(sample)

    measured = stat(gap)
    report(measured, len(gap), bootstrap(stat, gap), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(gap), example_row=gap[0]["b_row"])


if __name__ == "__main__":
    main()
