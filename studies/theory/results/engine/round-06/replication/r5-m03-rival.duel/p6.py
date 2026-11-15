"""k=6: on cued-4/4 problems, T3 (T 1.0) wrong rate when P (T 0.6) is wrong minus when P is right."""
import json
import pathlib
import subprocess
from collections import defaultdict

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, binomial, report, not_computable

CUE = pathlib.Path("studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl")
P_KEY = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"
P = pathlib.Path("runs/theory-tests/s3k/r3/base-01/out/P_math500.jsonl")
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
    if not CUE.exists():
        return not_computable(f"{CUE} not readable")
    if not fetch(P_KEY, P):
        return not_computable(f"{P_KEY} could not be fetched")
    if not fetch(T3_KEY, T3):
        return not_computable(f"{T3_KEY} could not be fetched")

    att0 = defaultdict(list)
    for r in jsonl(CUE):
        if r["attempt"] == 0:
            att0[r["problem_index"]].append(r)
    solved4 = {i for i, rows in att0.items() if len(rows) == 4 and all(r["score_v3"] == 1 for r in rows)}

    t3 = {}
    for r in jsonl(T3):
        t3.setdefault(r["problem_index"], r)
    prow = {}
    for r in jsonl(P):
        i = r["problem_index"]
        if i not in prow or r["sample"] < prow[i]["sample"]:
            prow[i] = r

    def wrong(r):
        g = R.grade_v3(r["gold"], r["text"])
        main = int(g["score_v3"] == 0 or bool(r.get("cap_hit")) or g["extracted_v3"] is None)
        alt = int(g["score_v3"] == 0 or g["extracted_v3"] is None)  # alt: cap_hit not counted on its own
        return main, alt

    entries = []  # (P wrong, T3 wrong, P wrong alt, T3 wrong alt, T3 row)
    for i in sorted(solved4):
        if i in t3 and i in prow:
            pm, pa = wrong(prow[i])
            tm, ta = wrong(t3[i])
            entries.append((pm, tm, pa, ta, t3[i]))

    def ab(sample, pk, tk):
        pw = [e[tk] for e in sample if e[pk] == 1]
        pr = [e[tk] for e in sample if e[pk] == 0]
        return pw, pr

    def mk(pk, tk):
        def stat(sample):
            pw, pr = ab(sample, pk, tk)
            return (sum(pw) / len(pw) if pw else 0.0) - (sum(pr) / len(pr) if pr else 0.0)
        return stat

    pw, pr = ab(entries, 0, 1)
    if not pw or not pr:
        return not_computable(f"a conditioning group is empty, recipe says report nothing (P-wrong={len(pw)}, P-right={len(pr)})")
    stat = mk(0, 1)
    pwa, pra = ab(entries, 2, 3)
    alt = mk(2, 3)(entries) if pwa and pra else None
    report(stat(entries), len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=slim(entries[0][4]))


main()
