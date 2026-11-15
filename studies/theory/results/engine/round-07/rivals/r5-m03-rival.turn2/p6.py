"""k=6: on cued-4/4 problems, plain-base T 1.0 (T3) wrong rate when the plain-base T 0.6 (P_math500) answer is wrong, minus
the T3 wrong rate when the P_math500 answer is right. No self-open filter."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

ROOT = pathlib.Path.cwd()
DATA = ROOT / "runs/theory-tests/duel-r5-m03-rival.turn2"
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
P_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"
T3 = DATA / "T3.jsonl"
P = DATA / "P_math500.jsonl"
CUE = ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"


def fetch(s3, dest):
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, str(dest), "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def load(p):
    return [json.loads(line) for line in open(p) if line.strip()]


def first_per_problem(rows):
    out = {}
    for r in rows:
        if r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return out


def smallest_sample(rows):
    out = {}
    for r in rows:   # ties on sample: the first in file order is kept
        i = r["problem_index"]
        if i not in out or r["sample"] < out[i]["sample"]:
            out[i] = r
    return out


def wrong(r, cap_counts=True):
    g = R.grade_v3(r["gold"], r["text"])
    empty = g["extracted_v3"] is None or str(g["extracted_v3"]).strip() == ""
    return int(g["score_v3"] != 1 or empty or (cap_counts and bool(r.get("cap_hit"))))


def cue_all4():
    by = {}
    for r in load(CUE):
        if r["attempt"] == 0:
            by.setdefault(r["problem_index"], []).append(r)
    return {i for i, rs in by.items() if len(rs) == 4 and all(r["score_v3"] == 1 for r in rs)}


def contrast(sample):
    """sample: list of (p_wrong, t3_wrong). a - b, or None when a conditioning group is empty."""
    pw = [t for p, t in sample if p == 1]
    pr = [t for p, t in sample if p == 0]
    if not pw or not pr:
        return None
    return sum(pw) / len(pw) - sum(pr) / len(pr)


def main():
    try:
        fetch(T3_S3, T3)
        fetch(P_S3, P)
    except Exception as e:  # noqa: BLE001
        return not_computable(f"row file not readable: {e}")
    if not CUE.exists():
        return not_computable("day1_3 rows.jsonl missing")
    t3 = first_per_problem(load(T3))
    pm = smallest_sample(load(P))
    keep = sorted(i for i in cue_all4() if i in t3 and i in pm)
    entries = [(wrong(pm[i]), wrong(t3[i])) for i in keep]
    measured = contrast(entries)
    if measured is None:
        return not_computable("a conditioning group (P-wrong or P-right) is empty: the recipe says report nothing")
    alt = contrast([(wrong(pm[i], False), wrong(t3[i], False)) for i in keep])   # other reading: cap hits not forced wrong

    def stat(sample):
        d = contrast(sample)
        return measured if d is None else d   # a resample missing a group keeps the full-sample value

    ex = dict(t3[keep[0]])
    ex["text"] = ex["text"][:300]
    ex["_note"] = "T3 row, text truncated to 300 characters"
    ex["_groups"] = {"P_wrong": sum(p for p, _ in entries), "P_right": sum(1 - p for p, _ in entries)}
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False, alt_measured=alt, example_row=ex)


main()
