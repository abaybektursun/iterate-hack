"""p4: cued base, MATH-500, T 1.0 / top-p 1.0 (S3 r4/base_rl-02/out/T1.jsonl).
v3 accuracy of answers whose text contains 'Wait' or 'Hmm' (case-sensitive substrings) minus v3 accuracy of the others.
First row per problem_index in file order; cap hits kept with their v3 score; empty extraction = 0.
alt_measured: the same contrast with cap-hit rows dropped."""
import json
import os
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"
LOCAL = "runs/theory-tests/s3k/rlneurons/r4/base_rl-02/out/T1.jsonl"


def fetch(s3, local):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr", "--only-show-errors"], check=False)
    return os.path.exists(local)


def short(r):
    r = dict(r)
    t = r.get("text") or ""
    if len(t) > 600:
        r["text"] = t[:300] + " [...truncated for the report...] " + t[-300:]
    r.pop("answer_tokens", None)
    return r


def diff(sample):
    m = [s for s, marked in sample if marked]
    o = [s for s, marked in sample if not marked]
    # A bootstrap resample with an empty group contributes 0.0 (never happens on the full sample: checked below).
    if not m or not o:
        return 0.0
    return sum(m) / len(m) - sum(o) / len(o)


def main():
    if not fetch(S3, LOCAL):
        return not_computable("T1.jsonl could not be fetched from S3")
    kept = {}
    for line in open(LOCAL):
        r = json.loads(line)
        if r["problem_index"] not in kept:
            kept[r["problem_index"]] = r
    for r in kept.values():
        if "text" not in r or "gold" not in r or "cap_hit" not in r:
            return not_computable("a row lacks text, gold or cap_hit")
    items, alt_items, rows = [], [], []
    for i in sorted(kept):
        r = kept[i]
        text = r["text"] or ""
        score = R.grade_v3(r["gold"], text)["score_v3"]
        marked = ("Wait" in text) or ("Hmm" in text)
        items.append((score, marked))
        rows.append(r)
        if not r["cap_hit"]:
            alt_items.append((score, marked))
    n_m = sum(1 for _, k in items if k)
    if n_m == 0 or n_m == len(items):
        return not_computable("group M or group N is empty; the recipe says report nothing")
    measured = diff(items)
    alt = diff(alt_items) if any(k for _, k in alt_items) and not all(k for _, k in alt_items) else None
    ex = next(r for r, (_, k) in zip(rows, items) if k)
    report(measured, len(items), bootstrap(diff, items), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=short(ex))


main()
