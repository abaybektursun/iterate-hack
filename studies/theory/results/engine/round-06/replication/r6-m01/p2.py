"""repl-r6-m01 k=2: share of long (n_generated >= 12000) cued-base hard328 answers with a textbook header line in the
second half of the text and none in the first half.

Main reading: lines = text.split('\n'), line start offset accumulated as len(line) + 1; header iff
re.match(HEADER, line); counted iff some header line starts at offset >= L/2 and no header line starts at offset < L/2.
Alt reading: line boundaries from str.splitlines() (any Unicode line break, e.g. '\r', ' '), same rule otherwise.
"""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

JOB = "abaybektursun-1114-151534-e72c"
S3 = f"s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01/{JOB}/answers.jsonl"
LOCAL = f"runs/theory-tests/repl-r6-m01/{JOB}/answers.jsonl"
HEADER = re.compile(r'\s*(?:(?:Problem|Exercise|Question|Example)\s*\d*\s*[:.]|Solution\s*:)')


def fetch():
    if not os.path.exists(LOCAL):
        os.makedirs(os.path.dirname(LOCAL), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3, LOCAL, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def lines_split_n(t):
    out, off = [], 0
    for line in t.split("\n"):
        out.append((off, line))
        off += len(line) + 1
    return out


def lines_splitlines(t):
    out, off = [], 0
    for chunk in t.splitlines(keepends=True):
        line = chunk.splitlines()[0] if chunk.splitlines() else ""
        out.append((off, line))
        off += len(chunk)
    return out


def counts(row, splitter):
    t = row["text"]
    L = len(t)
    starts = [off for off, line in splitter(t) if HEADER.match(line)]
    late = any(off >= L / 2 for off in starts)
    early = any(off < L / 2 for off in starts)
    return late and not early


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
    for r in first.values():
        if "n_generated" not in r or r["n_generated"] is None:
            not_computable("a row lacks n_generated")
            return
    kept = [r for r in first.values() if r["n_generated"] >= 12000]  # cap hits included
    if not kept:
        not_computable("no row with n_generated >= 12000; the share is undefined")
        return
    for r in kept:
        if not isinstance(r.get("text"), str):
            not_computable(f"kept row problem_index {r['problem_index']} has no text")
            return

    main_flag = {r["problem_index"]: counts(r, lines_split_n) for r in kept}
    alt_flag = {r["problem_index"]: counts(r, lines_splitlines) for r in kept}

    def stat(sample):
        return sum(main_flag[r["problem_index"]] for r in sample) / len(sample)

    def stat_alt(sample):
        return sum(alt_flag[r["problem_index"]] for r in sample) / len(sample)

    measured = stat(kept)
    ex = next((r for r in kept if main_flag[r["problem_index"]]), kept[0])
    ex = dict(ex)
    ex["text_len"] = len(ex["text"])
    ex["text"] = ex["text"][:300] + " ...[truncated]"
    if "prompt" in ex and isinstance(ex["prompt"], str):
        ex["prompt"] = ex["prompt"][:200] + " ...[truncated]"
    report(measured, len(kept), bootstrap(stat, kept), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(kept), example_row=ex)


if __name__ == "__main__":
    main()
