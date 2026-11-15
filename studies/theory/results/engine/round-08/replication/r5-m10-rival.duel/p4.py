"""k=4: cued base T1 (MATH-500, T 1.0): mean v3 of rows whose text contains 'Wait' or 'Hmm' minus mean v3 of the others."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"
LOCAL = pathlib.Path("runs/theory-tests/s3/r4/base_rl-02/out/T1.jsonl")


def fetch():
    if not LOCAL.exists():
        LOCAL.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3, str(LOCAL), "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def first_rows():
    out, seen = [], set()
    for line in open(LOCAL):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["problem_index"] in seen:
            continue
        seen.add(r["problem_index"])
        out.append(r)
    return out


def diff(sample, fallback=None):
    m = [x["score"] for x in sample if x["M"]]
    n = [x["score"] for x in sample if not x["M"]]
    if not m or not n:
        return fallback
    return sum(m) / len(m) - sum(n) / len(n)


def main():
    try:
        fetch()
        rows = first_rows()
    except Exception as e:
        not_computable(f"T1.jsonl not readable: {e!r}")
        return
    for f in ("text", "gold", "cap_hit", "problem_index"):
        if any(f not in r for r in rows):
            not_computable(f"field {f} missing in T1.jsonl rows")
            return
    recs = []
    for r in rows:
        text = r["text"] or ""
        s = int(R.grade_v3(r["gold"], text)["score_v3"] or 0)
        recs.append({"r": r, "score": s, "M": ("Wait" in text) or ("Hmm" in text), "cap": bool(r["cap_hit"])})
    nm = sum(x["M"] for x in recs)
    nn = len(recs) - nm
    if nm == 0 or nn == 0:
        not_computable("a group is empty (recipe: report nothing)")
        return
    measured = diff(recs)
    alt = diff([x for x in recs if not x["cap"]])
    interval = bootstrap(lambda s: diff(s, measured), recs)
    ex = next(x for x in recs if x["M"])
    er = dict(ex["r"])
    er["text"] = er["text"][:1500] + ("...[truncated]" if len(er["text"]) > 1500 else "")
    er.update({"score_v3_recomputed": ex["score"], "group": "M"})
    print(json.dumps({"groups": {"M (Wait or Hmm)": nm, "N (neither)": nn}}))
    report(measured, min(nm, nn), interval, "bootstrap", refuted_by_met=False, alt_measured=alt, example_row=er)


main()
