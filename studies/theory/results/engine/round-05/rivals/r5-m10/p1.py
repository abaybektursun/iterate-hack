"""duel-r5-m10 k=1: A06 - A10 on problems whose kept rows are non-self-opened in both P_math500 (T 0.6) and T3 (T 1.0)."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R

DIR = pathlib.Path("runs/theory-tests/duel-r5-m10")
FILES = {
    "P": "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl",
    "T3": "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl",
}


def fail(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": reason, "example_row": None}))
    raise SystemExit(0)


def fetch(name):
    p = DIR / (name + ".jsonl")
    if not p.exists():
        DIR.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", FILES[name], str(p), "--profile", "iterate-ecr"], capture_output=True, text=True)
        if r.returncode != 0 or not p.exists():
            fail(f"cannot fetch {FILES[name]}: {r.stderr.strip()[-300:]}")
    return p


def load(name, by_min_sample):
    rows = [json.loads(l) for l in open(fetch(name)) if l.strip()]
    for k in ("problem_index", "text", "gold") + (("sample",) if by_min_sample else ()):
        if any(k not in r for r in rows):
            fail(f"field {k} missing in {name}")
    kept = {}
    for r in rows:  # file order; ties on sample keep the first row met
        i = r["problem_index"]
        if i not in kept or (by_min_sample and r["sample"] < kept[i]["sample"]):
            kept[i] = r
    return kept


def self_opened(text):
    return "\nOkay" in text[:60]


def self_opened_alt(text):  # other reading: an answer that starts with 'Okay' also opened itself
    return "\nOkay" in text[:60] or text.lstrip().startswith("Okay")


def v3(r):
    return R.grade_v3(r["gold"], r["text"])["score_v3"]  # empty extraction -> 0; cap hits keep v3's score


def stat(P, T, opened):
    S = sorted(i for i in set(P) & set(T) if not opened(P[i]["text"]) and not opened(T[i]["text"]))
    if not S:
        return None, S
    a06 = sum(v3(P[i]) for i in S) / len(S)
    a10 = sum(v3(T[i]) for i in S) / len(S)
    return a06 - a10, S


P = load("P", True)
T = load("T3", False)
main, S = stat(P, T, self_opened)
alt, _ = stat(P, T, self_opened_alt)
if main is None:
    fail("S is empty: no problem is non-self-opened in both files")
ex = dict(P[S[0]])
ex["text"] = ex["text"][:400]
ex["score_v3_recomputed"] = v3(P[S[0]])
print(json.dumps({"n_S": len(S)}))
print(json.dumps({"measured": main, "refuted_by_met": False, "alt_measured": alt, "not_computable": None, "example_row": ex}))
