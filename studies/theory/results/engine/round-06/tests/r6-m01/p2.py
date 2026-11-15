"""r6-m01 prediction 2: share of cued-base hard328 answers (n_generated >= 12000, cap hits included) with a textbook
header line starting in the second half of the text and none starting in the first half."""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

JOB = "abaybektursun-1114-151534-e72c"
S3 = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01/{job}/answers.jsonl"
LOCAL = "runs/theory-tests/{job}/answers.jsonl"
HEADER = re.compile(r"\s*(?:(?:Problem|Exercise|Question|Example)\s*\d*\s*[:.]|Solution\s*:)")


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


def counts(text):
    L = len(text)
    offset = 0
    early = late = False
    for line in text.split("\n"):
        if HEADER.match(line):
            if offset >= L / 2:
                late = True
            else:
                early = True
        offset += len(line) + 1
    return late and not early


def short(row):
    r = dict(row)
    for key in ("text", "prompt"):
        if isinstance(r.get(key), str):
            r[key + "_len"] = len(r[key])
            r[key] = r[key][:300] + "...[truncated]"
    return r


def main():
    try:
        rows = first_per_problem(fetch(JOB))
    except Exception as e:  # noqa: BLE001
        not_computable(f"row file not readable: {e!r}")
        return
    for r in rows:
        if not isinstance(r.get("text"), str) or not isinstance(r.get("n_generated"), int):
            not_computable(f"row {r.get('problem_index')} lacks a text string or integer n_generated")
            return

    kept = [r for r in rows if r["n_generated"] >= 12000]
    if not kept:
        not_computable("no base cue row with n_generated >= 12000; the share is undefined")
        return
    flags = [1 if counts(r["text"]) else 0 for r in kept]
    measured = sum(flags) / len(flags)
    interval = bootstrap(lambda s: sum(s) / len(s), flags)

    # alt reading: the length filter on n_new instead of n_generated
    kept_alt = [r for r in rows if r["n_new"] >= 12000]
    alt = (sum(1 for r in kept_alt if counts(r["text"])) / len(kept_alt)) if kept_alt else None

    example = next((r for r, f in zip(kept, flags) if f), kept[0])
    report(measured, len(kept), interval, "bootstrap", refuted_by_met=measured < 0.10, alt_measured=alt,
           example_row=short(example))


if __name__ == "__main__":
    main()
