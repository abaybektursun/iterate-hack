"""p1: ratio of self-inconsistent-equation rates, cued base T 1.0 (A) over T 0.6 / top-p 0.95 (B).

Implements the recipe of prediction k = 1 as written. Main number: per_problem.json subject != 'Number Theory'
compared as the literal string (the file's labels are lowercase snake case, e.g. 'number_theory', so this keeps every
subject). alt_measured: the same statistic with subject == 'number_theory' excluded.
"""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, refuted_without_number, not_computable

A_PATH = "runs/theory-rows/s3new/r4/base_rl-02/out/T1.jsonl"
A_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"
B_PATH = "runs/theory-rows/s3new/r3/base-01/out/F_math500.jsonl"
B_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_math500.jsonl"
PP_PATH = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def fetch(path, s3):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, path, "--profile", "iterate-ecr"], check=True,
                       stdout=subprocess.DEVNULL)


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


# ---- EQ procedure -------------------------------------------------------------------------------------------------
RE_THOUSANDS = re.compile(r'(?<=\d),(?=\d{3})')
RE_EQ = re.compile(r'(?<![\d.])(\d{1,3})\s*(\+|-|\*|×|\\times|\\cdot)\s*(\d{1,3})\s*=\s*(\d{1,6})(?!\d)')
RE_PRE_WORD = re.compile(r'(?:^|[\s(])[A-Za-z]{2,}$')
RE_POST1 = re.compile(r'[A-Za-z^_/({]')
RE_POST2 = re.compile(r'\.\d')
RE_POST3 = re.compile(r'[+\-*/^×]|\\(times|cdot|div|frac|sqrt|pmod|bmod|mod)|\(\s*\\?mod|mod\b')


def eq_counts(text):
    """Return (N_row, W_row) for one row's text."""
    t = RE_THOUSANDS.sub('', text)                                        # (1)
    tuples = set()
    for m in RE_EQ.finditer(t):                                           # (2)
        pre_s = t[:m.start()].rstrip(' \t')                               # (3)
        if not (pre_s == '' or pre_s[-1] in '\n$=:,(' or RE_PRE_WORD.search(pre_s)):
            continue
        post = t[m.end():]                                                # (4)
        post_s = post.lstrip(' \t')
        if RE_POST1.match(post) or RE_POST2.match(post) or RE_POST3.match(post_s):
            continue
        ls = t.rfind('\n', 0, m.start()) + 1                              # (5)
        le = t.find('\n', m.start())
        line = t[ls:] if le == -1 else t[ls:le]
        if '?' in line:
            continue
        a, b, c = int(m.group(1)), int(m.group(3)), int(m.group(4))       # (6)
        sym = m.group(2)
        op = 'add' if sym == '+' else ('sub' if sym == '-' else 'mul')
        if op == 'sub' and a < b:
            continue
        tuples.add((a, op, b, c))                                         # (8) dedupe per row
    n = len(tuples)
    w = 0
    for a, op, b, c in tuples:                                            # (7)
        v = a + b if op == 'add' else (a - b if op == 'sub' else a * b)
        if v != c:
            w += 1
    return n, w


def ratio(pairs):
    """pairs: list of (NA_row, WA_row, NB_row, WB_row) per problem."""
    NA = sum(p[0] for p in pairs); WA = sum(p[1] for p in pairs)
    NB = sum(p[2] for p in pairs); WB = sum(p[3] for p in pairs)
    if NA == 0 or NB == 0:
        return None
    return ((WA + 0.5) / NA) / ((WB + 0.5) / NB)


def stat_boot(pairs):
    r = ratio(pairs)
    return float('inf') if r is None else r


def main():
    try:
        fetch(A_PATH, A_S3)
        fetch(B_PATH, B_S3)
    except Exception as e:  # noqa: BLE001
        not_computable(f"row file not readable: {e}")
        return
    rows_a = load_jsonl(A_PATH)
    rows_b = load_jsonl(B_PATH)
    with open(PP_PATH) as f:
        pp = json.load(f)
    subject = {r["problem_index"]: r.get("subject") for r in pp}

    # A: first row per problem_index in file order.
    kept_a = {}
    for r in rows_a:
        kept_a.setdefault(r["problem_index"], r)
    # B: per problem_index the row with smallest sample, first in file order on ties.
    kept_b = {}
    for r in rows_b:
        pi = r["problem_index"]
        if pi not in kept_b or r["sample"] < kept_b[pi]["sample"]:
            kept_b[pi] = r

    common = sorted(set(kept_a) & set(kept_b))
    base = [pi for pi in common
            if kept_a[pi]["cap_hit"] is False and kept_b[pi]["cap_hit"] is False and pi in subject]
    S_main = [pi for pi in base if subject[pi] != 'Number Theory']        # literal reading
    S_alt = [pi for pi in base if subject[pi] != 'number_theory']         # file's own label for Number Theory

    counts = {}
    for pi in base:
        na, wa = eq_counts(kept_a[pi]["text"])
        nb, wb = eq_counts(kept_b[pi]["text"])
        counts[pi] = (na, wa, nb, wb)

    pairs_main = [counts[pi] for pi in S_main]
    pairs_alt = [counts[pi] for pi in S_alt]

    print(json.dumps({"groups": {"A_T1.0_rows_in_S": len(S_main), "B_T0.6_rows_in_S": len(S_main)}}))

    R = ratio(pairs_main)
    if R is None:
        refuted_without_number()
        return
    R_alt = ratio(pairs_alt)

    ex_pi = S_main[0]
    ex = dict(kept_a[ex_pi])
    ex["text"] = ex["text"][:300] + ("..." if len(ex["text"]) > 300 else "")
    ex["_eq_counts_N_W"] = list(counts[ex_pi][:2])

    report(R, len(S_main), bootstrap(stat_boot, pairs_main), "bootstrap",
           refuted_by_met=False, alt_measured=R_alt, example_row=ex)


if __name__ == "__main__":
    main()
