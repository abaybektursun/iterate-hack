"""repl-r6-m01 k=3: median of r = (M_late + 1) / (M_early + 1) over cued-base hard328 answers that end right
(first row per problem_index, cap_hit false, score_v3 == 1, n_generated > 10000; missing/null score_v3 dropped).

Deciles and regex as in prediction 1 of r6-m01: decile k (1..10) = t[floor((k-1)L/10) : floor(kL/10)], count
re.findall of the regex in each decile slice separately; M_early = deciles 2+3, M_late = deciles 8+9.
Main reading: count within each decile slice (matches cut by a decile boundary are lost or shortened).
Alt reading: re.finditer over the whole text, each match assigned to the decile holding its start offset.
No kept row -> counts as refuted (refuted_without_number).
"""
import json
import os
import re
import statistics
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

JOB = "abaybektursun-1114-151534-e72c"
S3 = f"s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01/{JOB}/answers.jsonl"
LOCAL = f"runs/theory-tests/repl-r6-m01/{JOB}/answers.jsonl"
PAT = re.compile(r"(?<![A-Za-z])(Let me|I'm|I'll|Okay|Wait|Hmm|I|me)(?![A-Za-z])")


def fetch():
    if not os.path.exists(LOCAL):
        os.makedirs(os.path.dirname(LOCAL), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3, LOCAL, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def bounds(L, k):
    return (k - 1) * L // 10, k * L // 10  # exact floor for non-negative integers


def r_slices(t):
    L = len(t)
    c = {}
    for k in (2, 3, 8, 9):
        a, b = bounds(L, k)
        c[k] = len(PAT.findall(t[a:b]))
    return (c[8] + c[9] + 1) / (c[2] + c[3] + 1)


def r_starts(t):
    L = len(t)
    c = {k: 0 for k in range(1, 11)}
    for m in PAT.finditer(t):
        s = m.start()
        for k in range(1, 11):
            a, b = bounds(L, k)
            if a <= s < b:
                c[k] += 1
                break
    return (c[8] + c[9] + 1) / (c[2] + c[3] + 1)


def main():
    try:
        fetch()
    except Exception as e:  # noqa: BLE001
        not_computable(f"cannot fetch {S3}: {e}")
        return
    first = {}
    with open(LOCAL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            pi = row.get("problem_index")
            if pi is not None and pi not in first:
                first[pi] = row
    if not first:
        not_computable("no rows with problem_index in the file")
        return
    kept = []
    for r in first.values():
        if r.get("score_v3") is None:
            continue  # missing or null score_v3: dropped
        if "cap_hit" not in r or "n_generated" not in r or r["n_generated"] is None:
            not_computable(f"row problem_index {r['problem_index']} lacks cap_hit or n_generated")
            return
        if r["cap_hit"] is False and r["score_v3"] == 1 and r["n_generated"] > 10000:
            kept.append(r)
    if not kept:
        refuted_without_number()
        return
    for r in kept:
        if not isinstance(r.get("text"), str):
            not_computable(f"kept row problem_index {r['problem_index']} has no text")
            return

    rv = {r["problem_index"]: r_slices(r["text"]) for r in kept}
    rv_alt = {r["problem_index"]: r_starts(r["text"]) for r in kept}

    def stat(sample):
        return statistics.median(rv[r["problem_index"]] for r in sample)

    def stat_alt(sample):
        return statistics.median(rv_alt[r["problem_index"]] for r in sample)

    measured = stat(kept)
    ex = dict(kept[0])
    ex["text_len"] = len(ex["text"])
    ex["text"] = ex["text"][:300] + " ...[truncated]"
    if "prompt" in ex and isinstance(ex["prompt"], str):
        ex["prompt"] = ex["prompt"][:200] + " ...[truncated]"
    report(measured, len(kept), bootstrap(stat, kept), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(kept), example_row=ex)


if __name__ == "__main__":
    main()
