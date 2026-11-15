"""k=5: plain base T 0.6 non-self-opened accuracy on cued-4/4 problems minus on cued <= 1/4 problems."""
import json
import pathlib
import subprocess
from collections import defaultdict

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, binomial, report, not_computable

CUE = pathlib.Path("studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl")
P_KEY = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"
P = pathlib.Path("runs/theory-tests/s3k/r3/base-01/out/P_math500.jsonl")


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


def smallest_sample(path):
    keep = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        i = r["problem_index"]
        if i not in keep or r["sample"] < keep[i]["sample"]:
            keep[i] = r
    return keep


def main():
    if not CUE.exists():
        return not_computable(f"{CUE} not readable")
    if not fetch(P_KEY, P):
        return not_computable(f"{P_KEY} could not be fetched")

    att0 = defaultdict(list)
    for line in CUE.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r["attempt"] == 0:
                att0[r["problem_index"]].append(r)
    kcue = {i: sum(1 for r in rows if r["score_v3"] == 1) for i, rows in att0.items() if len(rows) == 4}

    prow = smallest_sample(P)
    scored = {}
    for i, r in prow.items():
        s = R.grade_v3(r["gold"], r["text"])["score_v3"]
        if bool(r.get("cap_hit")):
            s = 0
        scored[i] = int(s)

    def build(selfopen):
        out = []
        for i, r in prow.items():
            if selfopen(r["text"]) or i not in kcue:
                continue
            g = "E" if kcue[i] == 4 else ("H" if kcue[i] <= 1 else None)
            if g:
                out.append((g, scored[i], r))
        return out

    entries = build(lambda t: "\nOkay" in t[:60])        # main: newline followed by "Okay" in the first 60 chars
    alt_entries = build(lambda t: "Okay" in t[:60])       # alt: "Okay" in the first 60 chars, with or without a newline

    def stat(sample):
        e = [x[1] for x in sample if x[0] == "E"]
        h = [x[1] for x in sample if x[0] == "H"]
        return (sum(e) / len(e) if e else 0.0) - (sum(h) / len(h) if h else 0.0)

    def both(sample):
        return any(x[0] == "E" for x in sample) and any(x[0] == "H" for x in sample)

    if not both(entries):
        ne = sum(1 for x in entries if x[0] == "E")
        return not_computable(f"a group is empty, recipe says report nothing (E={ne}, H={len(entries) - ne})")
    alt = stat(alt_entries) if both(alt_entries) else None
    report(stat(entries), len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=slim(entries[0][2]))


main()
