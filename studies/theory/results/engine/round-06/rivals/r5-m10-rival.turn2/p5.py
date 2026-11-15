"""p5: cued base, hard328, T 1.0 / top-p 1.0 (S3 r5/day1_hard328-01/abaybektursun-1114-151534-e72c/answers.jsonl).
Mean score_v3 of answers whose text contains 'Wait' or 'Hmm' (case-sensitive substrings) minus mean score_v3 of the others.
Per problem_index keep the row with the smallest attempt (no attempt field: first in file order); null/missing score_v3 = 0;
cap hits kept. alt_measured: the same contrast with cap-hit rows dropped."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = ("s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01/abaybektursun-1114-151534-e72c/answers.jsonl")
LOCAL = "runs/theory-tests/s3k/rlneurons/r5/day1_hard328-01/abaybektursun-1114-151534-e72c/answers.jsonl"


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
    p = r.get("prompt") or ""
    if len(p) > 300:
        r["prompt"] = p[:300] + " [...truncated...]"
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
        return not_computable("answers.jsonl (-151534-e72c) could not be fetched from S3")
    kept = {}  # problem_index -> (attempt key, row); first in file order wins ties
    for line in open(LOCAL):
        r = json.loads(line)
        i = r["problem_index"]
        a = r.get("attempt")
        key = a if a is not None else float("inf")
        if i not in kept or key < kept[i][0]:
            kept[i] = (key, r)
    for _, r in kept.values():
        if "text" not in r or "cap_hit" not in r:
            return not_computable("a row lacks text or cap_hit")
    items, alt_items, rows = [], [], []
    for i in sorted(kept):
        r = kept[i][1]
        text = r["text"] or ""
        s = r.get("score_v3")
        score = 0 if s is None else s
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
