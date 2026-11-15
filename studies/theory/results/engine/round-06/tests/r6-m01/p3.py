"""r6-m01 prediction 3: median late/early deliberation ratio r on cued-base hard328 answers that finished
(cap_hit false), are right by the stored score_v3 (== 1) and have n_generated > 10000."""
import json
import math
import os
import re
import statistics
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

JOB = "abaybektursun-1114-151534-e72c"
S3 = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01/{job}/answers.jsonl"
LOCAL = "runs/theory-tests/{job}/answers.jsonl"
MARKER = re.compile(r"(?<![A-Za-z])(Let me|I'm|I'll|Okay|Wait|Hmm|I|me)(?![A-Za-z])")


def fetch(job):
    path = LOCAL.format(job=job)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3.format(job=job), path, "--profile", "iterate-ecr"], check=True,
                       stdout=subprocess.DEVNULL)
    return path


def first_per_problem(path):
    seen, out = set(), []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["problem_index"] in seen:
                continue
            seen.add(row["problem_index"])
            out.append(row)
    return out


def ratio(text):
    L = len(text)
    dec = [text[math.floor((k - 1) * L / 10): math.floor(k * L / 10)] for k in range(1, 11)]
    c = [len(MARKER.findall(d)) for d in dec]
    return (c[7] + c[8] + 1) / (c[1] + c[2] + 1)


def short(row):
    r = dict(row)
    for key in ("text", "prompt"):
        if isinstance(r.get(key), str):
            r[key + "_len"] = len(r[key])
            r[key] = r[key][:300] + "...[truncated]"
    return r


def keep(rows, token_field):
    out = []
    for r in rows:
        if r.get("score_v3") is None:  # missing or null score_v3: dropped
            continue
        if r["cap_hit"] is False and r["score_v3"] == 1 and r[token_field] > 10000:
            out.append(r)
    return out


def main():
    try:
        rows = first_per_problem(fetch(JOB))
    except Exception as e:  # noqa: BLE001
        not_computable(f"row file not readable: {e!r}")
        return
    for r in rows:
        if not isinstance(r.get("text"), str) or not isinstance(r.get("n_generated"), int) or "cap_hit" not in r:
            not_computable(f"row {r.get('problem_index')} lacks text, integer n_generated or cap_hit")
            return

    kept = keep(rows, "n_generated")
    if not kept:
        refuted_without_number()
        return
    rs = [ratio(r["text"]) for r in kept]
    measured = statistics.median(rs)
    interval = bootstrap(statistics.median, rs)

    # alt reading: the length filter on n_new instead of n_generated
    kept_alt = keep(rows, "n_new")
    alt = statistics.median(ratio(r["text"]) for r in kept_alt) if kept_alt else None

    report(measured, len(kept), interval, "bootstrap", refuted_by_met=measured > 0.92, alt_measured=alt,
           example_row=short(kept[0]))


if __name__ == "__main__":
    main()
