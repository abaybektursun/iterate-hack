"""r8-m12 offline prediction 4: right fraction of restart rows (attempt >= 1) on problems with an attempt-0 cap hit
and no right attempt-0 row, base cue hard328."""
import json
import os
import subprocess
from collections import OrderedDict

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

PATH = "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl"


def load(path):
    if not os.path.exists(path):
        try:
            data = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True, check=True).stdout.decode()
            os.makedirs("runs/theory-tests", exist_ok=True)
            path2 = os.path.join("runs/theory-tests", "p4_" + os.path.basename(os.path.dirname(path)) + ".jsonl")
            with open(path2, "w") as f:
                f.write(data)
            path = path2
        except Exception:
            return None
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def is_cap(r):
    if "cap_hit" in r and r["cap_hit"] is not None:
        return bool(r["cap_hit"])
    return r.get("finish_reason") == "length"


def is_right(r):
    return r.get("score_v3") == 1 and not is_cap(r)


def main():
    rows = load(PATH)
    if rows is None:
        return not_computable("file not readable: " + PATH)
    for r in rows:
        if "problem_index" not in r or "sample" not in r or "attempt" not in r:
            return not_computable("row lacks problem_index, sample or attempt")
    kept = OrderedDict()
    for r in rows:
        if r.get("attempt") != 0:
            continue
        key = (r["problem_index"], r["sample"])
        if key not in kept:
            kept[key] = r
    per_problem = OrderedDict()
    for (p, _s), r in kept.items():
        per_problem.setdefault(p, []).append(r)
    Z = [p for p, rs in per_problem.items() if any(is_cap(r) for r in rs) and not any(is_right(r) for r in rs)]
    zset = set(Z)
    restarts = OrderedDict((p, []) for p in Z)
    for r in rows:
        a = r.get("attempt")
        if isinstance(a, (int, float)) and a >= 1 and r["problem_index"] in zset:
            restarts[r["problem_index"]].append(r)
    all_rs = [r for rs in restarts.values() for r in rs]
    if not all_rs:
        return refuted_without_number()
    k = sum(1 for r in all_rs if is_right(r))
    measured = k / len(all_rs)
    # Other reading: a restart row counts right when score_v3 == 1 even if it is a cap hit.
    alt = sum(1 for r in all_rs if r.get("score_v3") == 1) / len(all_rs)

    problems = [tuple(rs) for rs in restarts.values() if rs]

    def stat(sample):
        tot = sum(len(g) for g in sample)
        return sum(1 for g in sample for r in g if is_right(r)) / tot if tot else 0.0

    example = next((r for r in all_rs if is_right(r)), all_rs[0])
    report(measured, len(problems), bootstrap(stat, problems), "bootstrap",
           refuted_by_met=measured > 0.12, alt_measured=alt, example_row=example)


main()
