"""k=2: T3 wrong rate on Q (top8 quick-wrong) minus T3 wrong rate on C (top8-right, cued base >= 3/4 at attempt 0)."""
import json
import pathlib
import subprocess
from collections import defaultdict

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, binomial, report, not_computable

TOP8 = pathlib.Path("studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json")
CUE = pathlib.Path("studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl")
T3_KEY = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
T3 = pathlib.Path("runs/theory-tests/s3k/r4/modal_t3-01/t3/T3.jsonl")


def fetch(key, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", key, str(path), "--profile", "iterate-ecr", "--only-show-errors"], check=False)
    return path.exists() and path.stat().st_size > 0


def slim(r):
    out = {k: v for k, v in r.items() if k not in ("prefill_ids", "answer_tokens", "cut_ids")}
    if isinstance(out.get("text"), str) and len(out["text"]) > 400:
        out["text"] = out["text"][:400] + "...[truncated]"
    return out


def jsonl(p):
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def main():
    for p in (TOP8, CUE):
        if not p.exists():
            return not_computable(f"{p} not readable")
    if not fetch(T3_KEY, T3):
        return not_computable(f"{T3_KEY} could not be fetched")

    top8 = json.loads(TOP8.read_text())
    first = {}
    for r in top8:
        if r.get("score_v3") is None:
            continue
        first.setdefault(r["problem_index"], r)

    # cued base: attempt-0 rows (main) and, for the alt reading, the last attempt of each sample
    att0 = defaultdict(list)
    last = defaultdict(dict)
    for r in jsonl(CUE):
        if r["attempt"] == 0:
            att0[r["problem_index"]].append(r)
        cur = last[r["problem_index"]].get(r["sample"])
        if cur is None or r["attempt"] > cur["attempt"]:
            last[r["problem_index"]][r["sample"]] = r

    def c_main(i):
        rows = att0.get(i, [])
        return len(rows) == 4 and sum(1 for r in rows if r["score_v3"] == 1) >= 3

    def c_alt(i):
        rows = list(last.get(i, {}).values())
        return len(rows) == 4 and sum(1 for r in rows if r["score_v3"] == 1) >= 3

    Q = [i for i, r in first.items() if r["score_v3"] == 0 and r["cap_hit"] is False and r["n_generated"] <= 2000]
    right = [i for i, r in first.items() if r["score_v3"] == 1 and r["cap_hit"] is False]
    C = [i for i in right if c_main(i)]
    C_alt = [i for i in right if c_alt(i)]

    t3 = {}
    for r in jsonl(T3):
        t3.setdefault(r["problem_index"], r)
    wrong = {}
    for i, r in t3.items():
        s = R.grade_v3(r["gold"], r["text"])["score_v3"]
        wrong[i] = int(s == 0 or bool(r.get("cap_hit")))

    def build(q, c):
        return [("Q", wrong[i], t3[i]) for i in q if i in t3] + [("C", wrong[i], t3[i]) for i in c if i in t3]

    entries = build(Q, C)
    alt_entries = build(Q, C_alt)

    def stat(sample):
        q = [e[1] for e in sample if e[0] == "Q"]
        c = [e[1] for e in sample if e[0] == "C"]
        fq = sum(q) / len(q) if q else 0.0  # only reached inside a bootstrap resample that misses a group
        fc = sum(c) / len(c) if c else 0.0
        return fq - fc

    nq = sum(1 for e in entries if e[0] == "Q")
    nc = len(entries) - nq
    if nq == 0 or nc == 0:
        return not_computable(f"empty group after dropping problems without a T3 row (Q={nq}, C={nc})")
    alt = None
    if any(e[0] == "C" for e in alt_entries):
        alt = stat(alt_entries)
    report(stat(entries), len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=slim(entries[0][2]))


main()
