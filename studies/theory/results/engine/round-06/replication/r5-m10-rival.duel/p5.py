"""k=5: base cue T 1.0 hard328 (r5/day1_hard328-01/abaybektursun-1114-151534-e72c/answers.jsonl): mean score_v3 of
rows whose text contains 'Wait' or 'Hmm' (case-sensitive) minus mean score_v3 of the other rows. One row per
problem_index (smallest attempt; first in file order without attempt), cap hits kept, null/missing score_v3 = 0."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = ("s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01/abaybektursun-1114-151534-e72c/answers.jsonl")
LOCAL = "runs/theory-tests/r5/day1_hard328-01/abaybektursun-1114-151534-e72c/answers.jsonl"


def fetch(s3, local):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def kept_rows(path):
    best = {}  # problem_index -> (attempt key, file order, row)
    for order, line in enumerate(open(path)):
        if not line.strip():
            continue
        r = json.loads(line)
        a = r.get("attempt")
        key = (0, a) if isinstance(a, (int, float)) else (1, 0)  # rows with an attempt value win; ties keep file order
        p = r["problem_index"]
        if p not in best or key < best[p][0]:
            best[p] = (key, order, r)
    return [v[2] for v in sorted(best.values(), key=lambda v: v[1])]


def diff(sample):
    m = [s for g, s in sample if g]
    n = [s for g, s in sample if not g]
    if not m or not n:
        return 0.0  # only reachable inside a bootstrap resample; the main number checks emptiness first
    return sum(m) / len(m) - sum(n) / len(n)


def main():
    fetch(S3, LOCAL)
    rows = kept_rows(LOCAL)
    items = []
    for r in rows:
        text = r.get("text") or ""
        s = r.get("score_v3")
        score = 0 if s is None else float(s)
        items.append((("Wait" in text) or ("Hmm" in text), score))
    if not any(g for g, _ in items) or all(g for g, _ in items):
        not_computable("group M or group N is empty (recipe: report nothing)")
        return
    no_cap = [it for it, r in zip(items, rows) if not r.get("cap_hit")]
    alt = diff(no_cap) if any(g for g, _ in no_cap) and not all(g for g, _ in no_cap) else None
    ex = dict(rows[0])
    ex.pop("prompt", None)
    ex["text"] = (ex.get("text") or "")[:2000]
    ex["in_M"] = items[0][0]
    report(diff(items), len(items), bootstrap(diff, items), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=ex)


main()
