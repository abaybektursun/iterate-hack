"""duel-r5-m10 k=2: on problems whose kept P_math500 row is non-self-opened, mean v3 of P (plain, T 0.6) minus mean v3 of F (cue, T 0.6)."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R

DIR = pathlib.Path("runs/theory-tests/duel-r5-m10")
FILES = {
    "P": "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl",
    "F": "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_math500.jsonl",
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


def load(name):
    rows = [json.loads(l) for l in open(fetch(name)) if l.strip()]
    for k in ("problem_index", "text", "gold", "sample"):
        if any(k not in r for r in rows):
            fail(f"field {k} missing in {name}")
    kept = {}
    for r in rows:  # smallest sample per problem; ties keep the first row met
        i = r["problem_index"]
        if i not in kept or r["sample"] < kept[i]["sample"]:
            kept[i] = r
    return kept


def self_opened(text):
    return "\nOkay" in text[:60]


def self_opened_alt(text):  # other reading: an answer that starts with 'Okay' also opened itself
    return "\nOkay" in text[:60] or text.lstrip().startswith("Okay")


def v3(r):
    return R.grade_v3(r["gold"], r["text"])["score_v3"]  # empty extraction -> 0; cap hits keep v3's score


def stat(P, F, opened):
    S = sorted(i for i in P if not opened(P[i]["text"]) and i in F)
    if not S:
        return None, S
    a = sum(v3(P[i]) for i in S) / len(S)
    b = sum(v3(F[i]) for i in S) / len(S)
    return a - b, S


P = load("P")
F = load("F")
main, S = stat(P, F, self_opened)
alt, _ = stat(P, F, self_opened_alt)
if main is None:
    fail("S is empty: no kept P_math500 row is non-self-opened with a kept F_math500 row")
ex = dict(P[S[0]])
ex["text"] = ex["text"][:400]
ex["score_v3_recomputed"] = v3(P[S[0]])
print(json.dumps({"n_S": len(S)}))
print(json.dumps({"measured": main, "refuted_by_met": False, "alt_measured": alt, "not_computable": None, "example_row": ex}))
