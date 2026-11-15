"""r8-m12 offline prediction 3: Think-SFT cue / base cue ratio of pooled right-finish rates per 1,000 alive tokens
in [12000, 16384), hard328, attempt 0."""
import json
import os
import subprocess
from collections import OrderedDict

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

PATH_A = "studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01/rows.jsonl"
PATH_B = "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl"
A0, B0 = 12000, 16384


def load(path):
    if not os.path.exists(path):
        try:
            data = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True, check=True).stdout.decode()
            os.makedirs("runs/theory-tests", exist_ok=True)
            path2 = os.path.join("runs/theory-tests", "p3_" + os.path.basename(os.path.dirname(path)) + ".jsonl")
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


def keep(rows):
    kept = OrderedDict()
    for r in rows:
        if r.get("attempt", 0) != 0:
            continue
        key = (r["problem_index"], r["sample"])
        if key not in kept:
            kept[key] = r
    per_problem = OrderedDict()
    for (p, _s), r in kept.items():
        per_problem.setdefault(p, []).append(r)
    return per_problem


def RM(rows):
    R = sum(1 for r in rows if is_right(r) and A0 <= r["n_new"] < B0)
    M = sum(max(0, min(r["n_new"], B0) - A0) / 1000.0 for r in rows)
    return R, M


def main():
    ra, rb = load(PATH_A), load(PATH_B)
    if ra is None:
        return not_computable("file not readable: " + PATH_A)
    if rb is None:
        return not_computable("file not readable: " + PATH_B)
    for r in ra + rb:
        if "n_new" not in r or "problem_index" not in r or "sample" not in r:
            return not_computable("row lacks n_new, problem_index or sample")
    pa, pb = keep(ra), keep(rb)
    rows_a = [r for rs in pa.values() for r in rs]
    rows_b = [r for rs in pb.values() for r in rs]
    Ra, Ma = RM(rows_a)
    Rb, Mb = RM(rows_b)
    if Mb == 0 or Rb == 0:
        return refuted_without_number()
    if Ma == 0:
        return not_computable("Think-SFT file has no alive mass in [12000, 16384)")
    measured = (Ra / Ma) / (Rb / Mb)

    # Paired by problem for the bootstrap (both files cover hard328; a problem missing from one side gives empty rows).
    pids = list(OrderedDict.fromkeys(list(pa.keys()) + list(pb.keys())))
    problems = [(tuple(pa.get(p, [])), tuple(pb.get(p, []))) for p in pids]

    def stat(sample):
        ra_, ma_ = RM([r for a, _b in sample for r in a])
        rb_, mb_ = RM([r for _a, b in sample for r in b])
        if ma_ == 0 or mb_ == 0:
            return float("inf")
        if rb_ == 0:
            return float("inf")
        return (ra_ / ma_) / (rb_ / mb_)

    example = next((r for r in rows_b if is_right(r) and A0 <= r["n_new"] < B0), rows_b[0])
    print(json.dumps({"groups": {"think_sft_cue": len(pa), "base_cue": len(pb)}}))
    report(measured, min(len(pa), len(pb)), bootstrap(stat, problems), "bootstrap",
           refuted_by_met=measured < 1.8, alt_measured=None, example_row=example)


main()
