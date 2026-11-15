"""k=4: base cue T 1.0 MATH-500 (r4/base_rl-02/out/T1.jsonl): mean grader-v3 score of rows whose text contains 'Wait' or
'Hmm' (case-sensitive) minus mean score of the other rows. First row per problem_index, cap hits kept."""
import json
import os
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"
LOCAL = "runs/theory-tests/r4/base_rl-02/out/T1.jsonl"


def fetch(s3, local):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def first_rows(path):
    out = {}
    for line in open(path):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return list(out.values())


def diff(sample):
    m = [s for g, s in sample if g]
    n = [s for g, s in sample if not g]
    if not m or not n:
        return 0.0  # only reachable inside a bootstrap resample; the main number checks emptiness first
    return sum(m) / len(m) - sum(n) / len(n)


def main():
    fetch(S3, LOCAL)
    rows = first_rows(LOCAL)
    items = []
    for r in rows:
        text = r["text"] or ""
        score = int(R.grade_v3(r["gold"], text)["score_v3"] == 1)
        items.append((("Wait" in text) or ("Hmm" in text), score))
    if not any(g for g, _ in items) or all(g for g, _ in items):
        not_computable("group M or group N is empty (recipe: report nothing)")
        return
    no_cap = [it for it, r in zip(items, rows) if not r["cap_hit"]]
    alt = diff(no_cap) if any(g for g, _ in no_cap) and not all(g for g, _ in no_cap) else None
    ex = dict(rows[0])
    ex["text"] = (ex["text"] or "")[:2000]
    ex["in_M"], ex["score_v3_recomputed"] = items[0][0], items[0][1]
    report(diff(items), len(items), bootstrap(diff, items), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=ex)


main()
