"""k=3: of the cued base's finished, v3-wrong T1 answers with n_generated <= 2000, the fraction that are early-marker answers."""
import json
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


def boxed_marker(text):
    """First '\\boxed{': (index of the backslash, index just after its brace-balanced '}' or len(text))."""
    s = text.find("\\boxed{")
    if s < 0:
        return None
    i, depth = s + len("\\boxed{"), 1
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s, i + 1
        i += 1
    return s, len(text)


def first_marker(text):
    cands = [m for m in (answer_marker(text), boxed_marker(text)) if m is not None]
    if not cands:
        return None
    return min(cands, key=lambda m: m[0])


def early(text):
    m = first_marker(text)
    if m is None:
        return False  # no marker: not early, stays in the denominator
    start, end = m
    return start / len(text) < 0.5 and len(text) - end > 300


def frac(sample):
    return sum(sample) / len(sample)


def main():
    rows = [json.loads(x) for x in open(path())]
    seen = set()
    for r in rows:
        assert r["problem_index"] not in seen, r["problem_index"]
        seen.add(r["problem_index"])
    fin = [r for r in rows if r["cap_hit"] is False]
    wrong = [r for r in fin if R.grade_v3(r["gold"], r["text"])["score_v3"] == 0]
    kept = [r for r in wrong if r["n_generated"] <= 2000]
    # other reading: "generated tokens" = n_new (n_generated is n_new + 1 in this file)
    kept_alt = [r for r in wrong if r["n_new"] <= 2000]
    if len(kept) < 8:
        refuted_without_number()
        return
    flags = [early(r["text"]) for r in kept]
    alt = frac([early(r["text"]) for r in kept_alt]) if kept_alt else None
    report(frac(flags), len(flags), bootstrap(frac, flags), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=kept[0])


main()
