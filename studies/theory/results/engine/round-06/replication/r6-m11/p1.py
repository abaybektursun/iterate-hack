"""k=1: wrong-rate ratio (v3_last == 0) of early-marker to late-marker finished answers, base + cue, T 1.0, MATH-500 (T1)."""
import json
import math
import os
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

KEY = "rlneurons/r4/base_rl-02/out/T1.jsonl"
S3 = "s3://pg-lineage-769063704696/results/" + KEY
NAMED = "runs/theory-rows/s3k/r4/base_rl-02/out/T1.jsonl"
LOCAL = "runs/theory-tests/s3k/r4/base_rl-02/out/T1.jsonl"


def path():
    if os.path.exists(NAMED):
        return NAMED
    if not os.path.exists(LOCAL):
        os.makedirs(os.path.dirname(LOCAL), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3, LOCAL, "--profile", "iterate-ecr"], check=True,
                       stdout=subprocess.DEVNULL)
    return LOCAL


def answer_marker(text):
    """First line whose left-stripped text begins with 'Answer:'. (start of 'A', end of line or end of text)."""
    pos = 0
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("Answer:"):
            start = pos + (len(line) - len(stripped))
            return start, pos + len(line)
        pos += len(line) + 1
    return None


def boxed_marker(text, escapes=False):
    """First '\\boxed{': (index of the backslash, index just after its brace-balanced '}' or len(text))."""
    s = text.find("\\boxed{")
    if s < 0:
        return None
    i, depth = s + len("\\boxed{"), 1
    while i < len(text):
        c = text[i]
        if escapes and c == "\\" and i + 1 < len(text) and text[i + 1] in "{}":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s, i + 1
        i += 1
    return s, len(text)


def first_marker(text, escapes=False):
    cands = [m for m in (answer_marker(text), boxed_marker(text, escapes)) if m is not None]
    if not cands:
        return None
    return min(cands, key=lambda m: m[0])  # earliest start; the two kinds cannot start at the same index


def is_early(text, m):
    start, end = m
    return start / len(text) < 0.5 and len(text) - end > 300


def ratio(sample):
    """sample: list of (early: bool, wrong: bool). Returns wrong rate(early) / wrong rate(late)."""
    e = [w for g, w in sample if g]
    l = [w for g, w in sample if not g]
    if not e or not l:
        return None
    re_, rl = sum(e) / len(e), sum(l) / len(l)
    if rl == 0:
        return math.inf if re_ > 0 else None
    return re_ / rl


def boot_stat(sample):
    v = ratio(sample)
    return 0.0 if v is None else v  # degenerate resample (empty group, or 0/0): counted as 0


def main():
    rows = [json.loads(x) for x in open(path())]
    seen = set()
    for r in rows:
        assert r["problem_index"] not in seen, r["problem_index"]
        seen.add(r["problem_index"])
    kept = [r for r in rows if r["cap_hit"] is False]
    items, items_alt, used = [], [], []
    for r in kept:
        text = r["text"]
        wrong = R.grade_v3(r["gold"], text)["score_v3"] == 0
        m = first_marker(text)
        if m is not None:
            items.append((is_early(text, m), wrong))
            used.append(r)
        # other reading: braces escaped as \{ \} do not count toward the \boxed{...} balance
        ma = first_marker(text, escapes=True)
        if ma is not None:
            items_alt.append((is_early(text, ma), wrong))
    n_early = sum(g for g, _ in items)
    if n_early < 15:
        refuted_without_number()
        return
    measured = ratio(items)
    if measured is None:
        not_computable("both group wrong rates are 0 (0/0) or the late group is empty")
        return
    alt = ratio(items_alt)
    ex = {k: v for k, v in used[0].items()}
    report(measured, len(items), bootstrap(boot_stat, items), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=ex)


main()
