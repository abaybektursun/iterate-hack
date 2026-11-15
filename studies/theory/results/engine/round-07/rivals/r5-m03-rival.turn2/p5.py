"""k=5: plain base T 0.6 / top-p 0.95 (r3 base-01 P_math500), non-self-opened answers: v3 accuracy on cued-4/4 problems
minus accuracy on cued <=1/4 problems."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

ROOT = pathlib.Path.cwd()
DATA = ROOT / "runs/theory-tests/duel-r5-m03-rival.turn2"
P_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"
P = DATA / "P_math500.jsonl"
CUE = ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
SELF_OPEN = "\nOkay"       # main reading: newline character followed by "Okay"
SELF_OPEN_ALT = "Okay"     # other reading: "Okay" anywhere in the first 60 characters


def fetch(s3, dest):
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, str(dest), "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def load(p):
    return [json.loads(line) for line in open(p) if line.strip()]


def smallest_sample(rows):
    out = {}
    for r in rows:   # ties on sample: the first in file order is kept
        i = r["problem_index"]
        if i not in out or r["sample"] < out[i]["sample"]:
            out[i] = r
    return out


def v3(r):
    g = R.grade_v3(r["gold"], r["text"])
    if g["extracted_v3"] is None or str(g["extracted_v3"]).strip() == "":
        return 0
    if r.get("cap_hit"):
        return 0
    return int(g["score_v3"] == 1)


def cue_k():
    by = {}
    for r in load(CUE):
        if r["attempt"] == 0:
            by.setdefault(r["problem_index"], []).append(r)
    return {i: sum(1 for r in rs if r["score_v3"] == 1) for i, rs in by.items() if len(rs) == 4}


def diff(sample):
    e = [s for s, g in sample if g == "E"]
    h = [s for s, g in sample if g == "H"]
    if not e or not h:
        return None
    return sum(e) / len(e) - sum(h) / len(h)


def build(pm, ks, marker):
    entries, used = [], []
    for i, r in sorted(pm.items()):
        if marker in r["text"][:60]:
            continue
        if i not in ks:
            continue
        k = ks[i]
        g = "E" if k == 4 else "H" if k <= 1 else None
        if g is None:
            continue
        entries.append((v3(r), g))
        used.append(r)
    return entries, used


def main():
    try:
        fetch(P_S3, P)
    except Exception as e:  # noqa: BLE001
        return not_computable(f"P_math500.jsonl not readable: {e}")
    if not CUE.exists():
        return not_computable("day1_3 rows.jsonl missing")
    pm = smallest_sample(load(P))
    ks = cue_k()
    entries, used = build(pm, ks, SELF_OPEN)
    measured = diff(entries)
    if measured is None:
        return not_computable("group E or group H is empty: the recipe says report nothing")
    alt_entries, _ = build(pm, ks, SELF_OPEN_ALT)
    alt = diff(alt_entries)

    def stat(sample):
        d = diff(sample)
        return measured if d is None else d   # a resample missing a group keeps the full-sample value

    ex = {k: v for k, v in used[0].items() if k != "prefill_ids"}
    ex["text"] = ex["text"][:300]
    ex["_note"] = "text truncated to 300 characters, prefill_ids dropped"
    ex["_groups"] = {"E": sum(g == "E" for _, g in entries), "H": sum(g == "H" for _, g in entries)}
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False, alt_measured=alt, example_row=ex)


main()
