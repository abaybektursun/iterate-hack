"""r6-m11 prediction 3: of the cued base's quick finished-wrong T1 answers (cap_hit false, n_generated <= 2000, v3 == 0), the
fraction that are early-marker answers. Rows with no marker count as not early and stay in the denominator.

Main reading: 'Answer:' marker = line whose left-stripped text begins with the literal 'Answer:'; quick = n_generated <= 2000.
Alt reading: the 'Answer:' marker also matches after leading markdown (*, _, #, >) with 'Answer**:' / 'Answer*:' / 'Answer__:'
allowed (e.g. '**Answer:** 5'); same quick filter.
"""
import json
import os
import re
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, refuted_without_number

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"
RECIPE_PATH = "runs/theory-rows/s3k/r4/base_rl-02/out/T1.jsonl"
FETCH_PATH = "runs/theory-tests/s3k/r4/base_rl-02/out/T1.jsonl"
BOXED = "\\boxed{"
ALT_LABEL = re.compile(r"Answer(?:\*\*|\*|__)?:")


def load():
    path = RECIPE_PATH if os.path.exists(RECIPE_PATH) else FETCH_PATH
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3, path, "--profile", "iterate-ecr"], check=True)
    rows = [json.loads(line) for line in open(path)]
    assert len(rows) == 500 and len({r["problem_index"] for r in rows}) == 500
    return rows


def answer_line(text, alt):
    pos = 0
    for line in text.split("\n"):
        if alt:
            stripped = line.lstrip().lstrip("*_#> \t")
            ok = ALT_LABEL.match(stripped) is not None
        else:
            stripped = line.lstrip()
            ok = stripped.startswith("Answer:")
        if ok:
            start = pos + (len(line) - len(stripped))
            return start, pos + len(line)
        pos += len(line) + 1
    return None


def first_box(text):
    i = text.find(BOXED)
    if i < 0:
        return None
    depth, j = 1, i + len(BOXED)
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return (i, j) if depth == 0 else (i, len(text))


def first_marker(text, alt=False):
    cands = [c for c in (answer_line(text, alt), first_box(text)) if c is not None]
    return min(cands, key=lambda c: c[0]) if cands else None


def early(text, alt):
    mk = first_marker(text, alt)
    if mk is None:
        return 0
    start, end = mk
    return int(start / len(text) < 0.5 and len(text) - end > 300)


def stat(sample):
    return sum(x[0] for x in sample) / len(sample)


def main():
    kept = []
    for r in load():
        if r["cap_hit"] is not False or r["n_generated"] > 2000:
            continue
        if R.grade_v3(r["gold"], r["text"])["score_v3"] != 0:
            continue
        kept.append((early(r["text"], False), early(r["text"], True), r))
    if not kept:
        refuted_without_number()
        return
    measured = stat(kept)
    alt = sum(x[1] for x in kept) / len(kept)
    ex = next((x for x in kept if x[0]), kept[0])
    r = dict(ex[2])
    r["text"] = r["text"][:1500]
    r["_derived"] = {"early": ex[0], "early_alt": ex[1], "first_marker": first_marker(ex[2]["text"]), "len_text": len(ex[2]["text"])}
    refuted = len(kept) < 8 or measured < 0.2
    report(measured, len(kept), bootstrap(stat, kept), "bootstrap", refuted_by_met=refuted, alt_measured=alt, example_row=r)


main()
