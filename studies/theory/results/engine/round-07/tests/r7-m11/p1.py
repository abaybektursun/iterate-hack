"""r7-m11 prediction 1: A - B, within-cue wrong-answer agreement minus cue-vs-plain (T3) wrong-answer agreement, MATH-500, T 1.0.

Main: agreement = rln4_lib.agree(a, b) with a = the CUE answer (for A: the lower sample index of the pair), b = the other.
Alt: agreement in either order (agree(a, b) or agree(b, a)), since agree wraps its first argument as gold.
"""
import functools
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, refuted_without_number

ROOT = pathlib.Path.cwd()
CUE = ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
T3 = ROOT / "runs/theory-tests/r4/modal_t3-01/t3/T3.jsonl"
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"


def fetch():
    if not T3.exists():
        T3.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", T3_S3, str(T3), "--profile", "iterate-ecr"], check=True)


def is_wrong(cap_hit, finish_reason, score, ext):
    return cap_hit is not True and finish_reason != "length" and score == 0 and isinstance(ext, str) and ext.strip() != ""


@functools.lru_cache(maxsize=None)
def ag(a, b):
    return bool(R.agree(a, b))


def ag_sym(a, b):
    return ag(a, b) or ag(b, a)


def short(r):
    r = dict(r)
    if isinstance(r.get("text"), str) and len(r["text"]) > 300:
        r["text"] = r["text"][:150] + " ... " + r["text"][-150:]
    return r


def main():
    fetch()
    # CUE: attempt == 0, first row per (problem_index, sample) in file order
    cue = {}
    for line in open(CUE):
        r = json.loads(line)
        if r.get("attempt") != 0:
            continue
        key = (r["problem_index"], r["sample"])
        if key not in cue:
            cue[key] = r
    cue_wrong = {}
    for (p, s), r in sorted(cue.items()):
        if is_wrong(r.get("cap_hit"), r.get("finish_reason"), r.get("score_v3"), r.get("extracted_v3")):
            cue_wrong.setdefault(p, []).append(r)
    # T3: first row per problem_index, graded with grader v3 on its text and gold
    t3 = {}
    for line in open(T3):
        r = json.loads(line)
        if r["problem_index"] not in t3:
            t3[r["problem_index"]] = r
    t3_wrong = {}
    for p, r in t3.items():
        g = R.grade_v3(r["gold"], r.get("text") or "")
        if is_wrong(r.get("cap_hit"), r.get("finish_reason"), g["score_v3"], g["extracted_v3"]):
            t3_wrong[p] = (r, g["extracted_v3"])

    problems = sorted(set(p for p, _ in cue))
    entries = [(tuple(cue_wrong.get(p, [])), t3_wrong.get(p)) for p in problems]

    def parts(sample, f):
        a_num = a_den = b_num = b_den = 0
        for cw, tw in sample:
            xs = [r["extracted_v3"] for r in cw]  # in increasing sample order
            for i in range(len(xs)):
                for j in range(i + 1, len(xs)):
                    a_den += 1
                    a_num += f(xs[i], xs[j])
            if tw is not None:
                for x in xs:
                    b_den += 1
                    b_num += f(x, tw[1])
        return a_num, a_den, b_num, b_den

    def stat_with(f):
        def stat(sample):
            a_num, a_den, b_num, b_den = parts(sample, f)
            if a_den == 0 or b_den == 0:
                return float("-inf")
            return a_num / a_den - b_num / b_den
        return stat

    a_num, a_den, b_num, b_den = parts(entries, ag)
    if a_den == 0 or b_den == 0:
        refuted_without_number()
        return
    measured = a_num / a_den - b_num / b_den
    sa_num, sa_den, sb_num, sb_den = parts(entries, ag_sym)
    alt = sa_num / sa_den - sb_num / sb_den
    n_a = sum(1 for cw, _ in entries if len(cw) >= 2)
    n_b = sum(1 for cw, tw in entries if len(cw) >= 1 and tw is not None)
    print(json.dumps({"groups": {"A: problems with >=2 CUE wrong answers": n_a,
                                 "B: problems with >=1 CUE wrong and a T3 wrong answer": n_b}}))
    ex = next((cw[0] for cw, tw in entries if len(cw) >= 1 and tw is not None), None)
    report(measured, min(n_a, n_b), bootstrap(stat_with(ag), entries), "bootstrap",
           refuted_by_met=measured < 0.03, alt_measured=alt, example_row=short(ex) if ex else None)


if __name__ == "__main__":
    main()
