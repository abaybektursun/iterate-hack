"""k=1: among non-self-opened T3 rows (first row per problem_index) with v3_last == 0 (cap hits included), the fraction
whose first answer marker grades right under grader v3 ('Answer: ' + content)."""
import json
import os
import subprocess

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
LOCAL = "runs/theory-tests/r4/modal_t3-01/t3/T3.jsonl"


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


def self_opened(text):
    return "\nOkay" in text[:60]


def first_marker(text):
    """(start, end, content) of the earliest marker, or None. (a) a line whose lstrip begins 'Answer:'; (b) first '\\boxed{'."""
    cands = []
    pos = 0
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("Answer:"):
            start = pos + (len(line) - len(stripped))
            cands.append((start, pos + len(line), stripped[len("Answer:"):]))
            break
        pos += len(line) + 1
    i = text.find(S.BOXED)
    if i >= 0:
        depth, j = 1, i + len(S.BOXED)
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        if depth == 0:
            cands.append((i, j, text[i + len(S.BOXED):j - 1]))
        else:
            cands.append((i, len(text), text[i + len(S.BOXED):]))
    if not cands:
        return None
    return min(cands, key=lambda c: c[0])


def v3_last(r):
    return int(R.grade_v3(r["gold"], r["text"])["score_v3"] == 1)


def first_score(r, m):
    if m is None:
        return 0
    return int(R.grade_v3(r["gold"], "Answer: " + m[2])["score_v3"] == 1)


def first_score_alt(r, m):
    """Other reading: grade the marker content itself (normalized, no re-extraction) against gold."""
    if m is None or not m[2].strip():
        return 0
    return int(S.grade(R.norm_v3(r["gold"]), R.norm_v3(m[2].strip()))["score"] == 1)


def main():
    fetch(S3, LOCAL)
    rows = [r for r in first_rows(LOCAL) if not self_opened(r["text"])]
    items = []
    for r in rows:
        if v3_last(r) != 0:
            continue
        m = first_marker(r["text"])
        items.append((first_score(r, m), first_score_alt(r, m), r))
    if not items:
        not_computable("no non-self-opened row has v3_last == 0 (recipe: report nothing)")
        return

    def stat(sample):
        return sum(x[0] == 1 for x in sample) / len(sample)

    def stat_alt(sample):
        return sum(x[1] == 1 for x in sample) / len(sample)

    measured = stat(items)
    ex = dict(items[0][2])
    ex["text"] = ex["text"][:2000]
    ex["first_score"], ex["v3_last"] = items[0][0], 0
    report(measured, len(items), bootstrap(stat, items), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(items), example_row=ex)


main()
