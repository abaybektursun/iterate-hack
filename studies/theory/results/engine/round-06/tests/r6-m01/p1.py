"""r6-m01 prediction 1: median late/early deliberation ratio r, cued base (e72c) minus RL plain (86ef), hard328,
answers with n_generated >= 12000 (cap hits included)."""
import json
import math
import os
import re
import statistics
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

JOBS = {"base": "abaybektursun-1114-151534-e72c", "rl": "abaybektursun-1114-151540-86ef"}
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
    counts = [len(MARKER.findall(d)) for d in dec]
    m_early = counts[1] + counts[2]
    m_late = counts[7] + counts[8]
    return (m_late + 1) / (m_early + 1)


def short(row):
    r = dict(row)
    for key in ("text", "prompt"):
        if isinstance(r.get(key), str):
            r[key + "_len"] = len(r[key])
            r[key] = r[key][:300] + "...[truncated]"
    return r


def compute(rows_by_model, token_field):
    """Return (problems list for bootstrap, full statistic, kept counts, example row)."""
    kept = {}
    for m, rows in rows_by_model.items():
        kept[m] = {r["problem_index"]: (ratio(r["text"]), r) for r in rows if r[token_field] >= 12000}
    return kept


def stat_from(entries, fallback):
    b = [e[0] for e in entries if e[0] is not None]
    r = [e[1] for e in entries if e[1] is not None]
    mb = statistics.median(b) if b else fallback[0]
    mr = statistics.median(r) if r else fallback[1]
    return mb - mr


def main():
    try:
        rows = {m: first_per_problem(fetch(j)) for m, j in JOBS.items()}
    except Exception as e:  # noqa: BLE001
        not_computable(f"row file not readable: {e!r}")
        return
    for m in rows:
        for r in rows[m]:
            if not isinstance(r.get("text"), str) or not isinstance(r.get("n_generated"), int):
                not_computable(f"{m} row {r.get('problem_index')} lacks a text string or integer n_generated")
                return

    kept = compute(rows, "n_generated")
    if len(kept["base"]) < 5 or len(kept["rl"]) < 5:
        refuted_without_number()
        return
    med_b = statistics.median(v[0] for v in kept["base"].values())
    med_r = statistics.median(v[0] for v in kept["rl"].values())
    measured = med_b - med_r

    # one entry per problem kept in either file: (r_base or None, r_rl or None)
    idx = sorted(set(kept["base"]) | set(kept["rl"]))
    entries = [(kept["base"][i][0] if i in kept["base"] else None, kept["rl"][i][0] if i in kept["rl"] else None)
               for i in idx]
    interval = bootstrap(lambda s: stat_from(s, (med_b, med_r)), entries)

    # alt reading: the length filter on n_new (tokens sampled after the 3-token cue / prompt) instead of n_generated
    alt = None
    kept_alt = compute(rows, "n_new")
    if len(kept_alt["base"]) >= 1 and len(kept_alt["rl"]) >= 1:
        alt = (statistics.median(v[0] for v in kept_alt["base"].values())
               - statistics.median(v[0] for v in kept_alt["rl"].values()))

    example = short(next(iter(kept["base"].values()))[1])
    report(measured, len(kept["base"]) + len(kept["rl"]), interval, "bootstrap",
           refuted_by_met=measured > -0.15, alt_measured=alt, example_row=example)


if __name__ == "__main__":
    main()
