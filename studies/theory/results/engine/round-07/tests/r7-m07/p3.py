"""r7-m07 prediction 3: median ln(n_new 3.0 fr-01 / n_new 3.1 s2800-01) on plain MATH-500, Q4 minus short half by T2 length."""
import json
import math
import os
import statistics
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r3"
LOCAL = "runs/theory-tests/r3"
PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def fetch(run, name):
    path = f"{LOCAL}/{run}/out/{name}"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{run}/out/{name}", path, "--profile", "iterate-ecr",
                        "--only-show-errors"], check=False)
    return path if os.path.exists(path) else None


def kept(path):
    """Rows with sample == 0, then the first row per problem_index in file order."""
    out = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("sample") != 0:
                continue
            if r["problem_index"] not in out:
                out[r["problem_index"]] = r
    return out


def slim(r):
    return {k: v for k, v in r.items() if k not in ("text", "prefill_ids")}


def main():
    pa, pb = fetch("fr-01", "P_math500.jsonl"), fetch("s2800-01", "P_math500.jsonl")
    if pa is None or pb is None:
        return not_computable("could not read fr-01 or s2800-01 P_math500.jsonl")
    if not os.path.exists(PP):
        return not_computable(f"missing {PP}")
    A, B = kept(pa), kept(pb)
    pp = json.load(open(PP))
    rows = sorted(pp, key=lambda r: (r["t2_generated_tokens"], r["problem_index"]))
    rank = {r["problem_index"]: i + 1 for i, r in enumerate(rows)}  # problems missing from per_problem.json dropped

    def group(pi):
        k = rank.get(pi)
        if k is None:
            return None
        if k >= 376:
            return "Q4"
        if k <= 250:
            return "short"
        return None

    S = [pi for pi in A if pi in B and A[pi]["cap_hit"] is False and B[pi]["cap_hit"] is False]
    items = []
    for pi in sorted(S):
        g = group(pi)
        if g is None:
            continue
        r = math.log(max(A[pi]["n_new"], 1) / max(B[pi]["n_new"], 1))
        items.append((g, r, pi))

    n4 = sum(1 for x in items if x[0] == "Q4")
    ns = sum(1 for x in items if x[0] == "short")
    print(json.dumps({"groups": {"Q4_in_S": n4, "short_half_in_S": ns}}))
    if n4 < 20 or ns < 20:
        return refuted_without_number()

    def stat(sample):
        q4 = [x[1] for x in sample if x[0] == "Q4"]
        sh = [x[1] for x in sample if x[0] == "short"]
        if not q4 or not sh:
            return 0.0
        return statistics.median(q4) - statistics.median(sh)

    measured = stat(items)

    # Alt reading (unpaired): per group, ln(median finished n_new of 3.0 / median finished n_new of 3.1),
    # each model's finished answers taken on its own (no requirement that the other model also finished).
    def unpaired(g):
        la = [max(A[pi]["n_new"], 1) for pi in A if group(pi) == g and A[pi]["cap_hit"] is False]
        lb = [max(B[pi]["n_new"], 1) for pi in B if group(pi) == g and B[pi]["cap_hit"] is False]
        if not la or not lb:
            return None
        return math.log(statistics.median(la) / statistics.median(lb))

    u4, us = unpaired("Q4"), unpaired("short")
    alt = None if u4 is None or us is None else u4 - us

    pi0 = items[0][2]
    report(measured, min(n4, ns), bootstrap(stat, items), "bootstrap",
           refuted_by_met=measured > -0.02, alt_measured=alt,
           example_row={"A_fr01": slim(A[pi0]), "B_s2800": slim(B[pi0]), "group": items[0][0], "r": items[0][1]})


main()
