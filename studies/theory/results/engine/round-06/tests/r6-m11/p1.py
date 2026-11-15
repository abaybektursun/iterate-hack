"""r6-m11 prediction 1: wrong-rate ratio, early-marker vs late-marker finished answers, cued base T1 (MATH-500).

Main reading: the 'Answer:' marker is a line whose left-stripped text begins with the literal 'Answer:'.
Alt reading: the same, but leading markdown (*, _, #, >) is also stripped and 'Answer**:' / 'Answer*:' / 'Answer__:' count
(so '**Answer:** 5' and '**Answer**: 5' are markers).
"""
import json
import math
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
    """First line whose left-stripped text begins with 'Answer:' -> (start of 'A', end of line, content after the label)."""
    pos = 0
    for line in text.split("\n"):
        if alt:
            stripped = line.lstrip().lstrip("*_#> \t")
            m = ALT_LABEL.match(stripped)
            ok, label_len = m is not None, (m.end() if m else 0)
        else:
            stripped = line.lstrip()
            ok, label_len = stripped.startswith("Answer:"), len("Answer:")
        if ok:
            start = pos + (len(line) - len(stripped))
            end = pos + len(line)
            return start, end, text[start + label_len:end]
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
    if depth == 0:
        return i, j, text[i + len(BOXED):j - 1]
    return i, len(text), text[i + len(BOXED):]          # unbalanced: end = end of text


def first_marker(text, alt=False):
    cands = [c for c in (answer_line(text, alt), first_box(text)) if c is not None]
    return min(cands, key=lambda c: c[0]) if cands else None


def is_early(text, mk):
    start, end, _ = mk
    return start / len(text) < 0.5 and len(text) - end > 300


def items(rows, alt):
    out = []
    for r in rows:
        if r["cap_hit"] is not False:
            continue
        mk = first_marker(r["text"], alt)
        if mk is None:
            continue                                      # recipe: drop rows with no marker
        out.append((is_early(r["text"], mk), R.grade_v3(r["gold"], r["text"])["score_v3"], r, mk))
    return out


def stat(sample):
    early = [x for x in sample if x[0]]
    late = [x for x in sample if not x[0]]
    we = sum(1 for x in early if x[1] == 0) / len(early) if early else 0.0
    wl = sum(1 for x in late if x[1] == 0) / len(late) if late else 0.0
    if wl == 0:
        return math.inf if we > 0 else 1.0               # 0/0 (only possible in a degenerate resample) -> 1.0
    return we / wl


def main():
    rows = load()
    main_items = items(rows, alt=False)
    alt_items = items(rows, alt=True)
    n_early = sum(1 for x in main_items if x[0])
    if not main_items:
        refuted_without_number()
        return
    measured = stat(main_items)
    alt = stat(alt_items) if alt_items else None
    ex = next((x for x in main_items if x[0]), main_items[0])
    r = dict(ex[2])
    r["text"] = r["text"][:1500]
    r["_first_marker"] = {"start": ex[3][0], "end": ex[3][1], "content": ex[3][2][:200], "len_text": len(ex[2]["text"]),
                          "early": ex[0], "v3_last": ex[1], "n_early_group": n_early}
    refuted = (n_early < 15) or (measured < 1.3)
    report(measured, len(main_items), bootstrap(stat, main_items), "bootstrap", refuted_by_met=refuted,
           alt_measured=alt, example_row=r)


main()
