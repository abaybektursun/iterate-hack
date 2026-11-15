"""r7-m07 prediction 4: 12k cliff. R_m = #(n_new >= 12000) / #(8000 <= n_new < 12000) over finished P+F rows;
statistic R(3.0 fr-01) / R(3.1 s2800-01)."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r3"
LOCAL = "runs/theory-tests/r3"
FILES = {"30P": ("fr-01", "P_math500.jsonl"), "30F": ("fr-01", "F_math500.jsonl"),
         "31P": ("s2800-01", "P_math500.jsonl"), "31F": ("s2800-01", "F_math500.jsonl")}


def fetch(run, name):
    path = f"{LOCAL}/{run}/out/{name}"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{run}/out/{name}", path, "--profile", "iterate-ecr",
                        "--only-show-errors"], check=False)
    return path if os.path.exists(path) else None


def kept(path):
    """Rows with sample == 0, then the first row per problem_index in file order; then cap_hit false only."""
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
    return {pi: r for pi, r in out.items() if r["cap_hit"] is False}


def counts(rows, field):
    a = sum(1 for r in rows if 8000 <= r[field] < 12000)
    b = sum(1 for r in rows if r[field] >= 12000)
    return a, b


def ratio(rows30, rows31, field):
    a30, b30 = counts(rows30, field)
    a31, b31 = counts(rows31, field)
    if a30 == 0 or a31 == 0 or b31 == 0:
        return None, (a30, b30, a31, b31)
    return (b30 / a30) / (b31 / a31), (a30, b30, a31, b31)


def main():
    data = {}
    for key, (run, name) in FILES.items():
        p = fetch(run, name)
        if p is None:
            return not_computable(f"could not read {run}/out/{name}")
        data[key] = kept(p)

    # one entry per problem: the kept finished rows of that problem across the four files
    pis = sorted(set().union(*[set(d) for d in data.values()]))
    items = [tuple((key, data[key][pi]) for key in FILES if pi in data[key]) for pi in pis]

    def split(sample):
        r30 = [r for it in sample for key, r in it if key.startswith("30")]
        r31 = [r for it in sample for key, r in it if key.startswith("31")]
        return r30, r31

    r30, r31 = split(items)
    measured, (a30, b30, a31, b31) = ratio(r30, r31, "n_new")
    print(json.dumps({"groups": {"A_3.0_8k_12k": a30, "B_3.0_ge12k": b30, "A_3.1_8k_12k": a31, "B_3.1_ge12k": b31}}))
    if measured is None:
        return refuted_without_number()

    def stat(sample):
        v, _ = ratio(*split(sample), "n_new")
        return float("inf") if v is None else v  # undefined in a resample: counted as unbounded

    alt, _ = ratio(r30, r31, "n_generated")  # alt reading: token count n_generated instead of n_new

    ex = next(r for r in r30 if r["n_new"] >= 8000) if any(r["n_new"] >= 8000 for r in r30) else r30[0]
    ex = {k: v for k, v in ex.items() if k not in ("text", "prefill_ids")}
    report(measured, min(a30, b30, a31, b31), bootstrap(stat, items), "bootstrap",
           refuted_by_met=measured > 0.80, alt_measured=alt, example_row=ex)


main()
