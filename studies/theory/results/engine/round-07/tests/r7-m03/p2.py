"""r7-m03 prediction 2: wrong-equation rate ratio, RL plain T 1.0 (C = T2) over cued base T 1.0 (A = T1)."""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/"
PER_PROBLEM = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def fetch(key):
    """The recipe's path under runs/theory-rows if present, else runs/theory-tests (fetched from S3 when missing)."""
    named = "runs/theory-rows/s3new/" + key
    if os.path.exists(named):
        return named
    local = "runs/theory-tests/s3new/" + key
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", BUCKET + key, local, "--profile", "iterate-ecr", "--only-show-errors"],
                       check=True)
    return local


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


EQ_RE = re.compile(r'(?<![\d.])(\d{1,3})\s*(\+|-|\*|×|\\times|\\cdot)\s*(\d{1,3})\s*=\s*(\d{1,6})(?!\d)')
PRE_WORD = re.compile(r'(?:^|[\s(])[A-Za-z]{2,}$')
POST_1 = re.compile(r'[A-Za-z^_/({]')
POST_2 = re.compile(r'\.\d')
POST_3 = re.compile(r'[+\-*/^×]|\\(times|cdot|div|frac|sqrt|pmod|bmod|mod)|\(\s*\\?mod|mod\b')


def eq_counts(text):
    """EQ procedure steps (1)-(8): returns (N_row, W_row)."""
    t = re.sub(r'(?<=\d),(?=\d{3})', '', text or "")
    tuples = set()
    for m in EQ_RE.finditer(t):
        pre_s = t[:m.start()].rstrip(' \t')
        if not (pre_s == '' or pre_s[-1] in '\n$=:,(' or PRE_WORD.search(pre_s)):
            continue
        post = t[m.end():]
        post_s = post.lstrip(' \t')
        if POST_1.match(post) or POST_2.match(post) or POST_3.match(post_s):
            continue
        ls = t.rfind('\n', 0, m.start()) + 1
        le = t.find('\n', m.start())
        line = t[ls:] if le == -1 else t[ls:le]
        if '?' in line:
            continue
        a, b, c = int(m.group(1)), int(m.group(3)), int(m.group(4))
        sym = m.group(2)
        op = 'add' if sym == '+' else ('sub' if sym == '-' else 'mul')
        if op == 'sub' and a < b:
            continue
        tuples.add((a, op, b, c))
    n = len(tuples)
    w = 0
    for a, op, b, c in tuples:
        v = a + b if op == 'add' else (a - b if op == 'sub' else a * b)
        if v != c:
            w += 1
    return n, w


def ratio(entries):
    """entries: list of (nA, wA, nC, wC). Statistic = ((W_C + .5) / N_C) / ((W_A + .5) / N_A)."""
    NA = sum(e[0] for e in entries); WA = sum(e[1] for e in entries)
    NC = sum(e[2] for e in entries); WC = sum(e[3] for e in entries)
    if NC == 0:
        return float('inf')
    if NA == 0:
        return 0.0
    return ((WC + 0.5) / NC) / ((WA + 0.5) / NA)


def main():
    try:
        A_rows = read_jsonl(fetch("r4/base_rl-02/out/T1.jsonl"))
        C_rows = read_jsonl(fetch("r4/modal_t2-01/t2/T2.jsonl"))
        with open(PER_PROBLEM) as f:
            pp = json.load(f)
    except Exception as e:  # noqa: BLE001
        not_computable(f"file not readable: {e}")
        return
    for r in A_rows + C_rows:
        for k in ("problem_index", "cap_hit", "text"):
            if k not in r:
                not_computable(f"field {k} missing in a row")
                return
    subject = {r["problem_index"]: r.get("subject") for r in pp}

    A, C = {}, {}
    for r in A_rows:  # first row per problem_index in file order
        A.setdefault(r["problem_index"], r)
    for r in C_rows:
        C.setdefault(r["problem_index"], r)

    def build(exclude):
        S = [pi for pi in sorted(set(A) & set(C))
             if A[pi]["cap_hit"] is False and C[pi]["cap_hit"] is False and subject.get(pi) not in exclude]
        entries = []
        for pi in S:
            nA, wA = eq_counts(A[pi]["text"])
            nC, wC = eq_counts(C[pi]["text"])
            entries.append((nA, wA, nC, wC))
        return S, entries

    # Main (literal): subject != 'Number Theory'; the file's subjects are lowercase ('number_theory'), so nothing is excluded.
    S, entries = build({'Number Theory'})
    # Alt: the intended exclusion of the file's 'number_theory' label.
    S_alt, entries_alt = build({'Number Theory', 'number_theory'})

    NA = sum(e[0] for e in entries); NC = sum(e[2] for e in entries)
    alt = ratio(entries_alt) if entries_alt and sum(e[0] for e in entries_alt) and sum(e[2] for e in entries_alt) else None
    print(json.dumps({"groups": {"A_T1_base_cue": len(S), "C_T2_rl_plain": len(S)}}))
    if not S or NA == 0 or NC == 0:
        refuted_without_number()
        return
    R = ratio(entries)
    interval = bootstrap(ratio, entries)
    ex = dict(C[S[0]])
    ex["text"] = ex["text"][:300] + "...[truncated]"
    report(R, len(S), interval, "bootstrap", refuted_by_met=R > 0.8, alt_measured=alt, example_row=ex)


if __name__ == "__main__":
    main()
