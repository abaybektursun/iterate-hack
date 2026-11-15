#!/usr/bin/env python3
"""r4-m01 prediction 3: paired by problem, sample 0 only: base-01 F_math500 vs
s2800-01 P_math500. Score 1 if ratio(base[:3000]) < ratio(rl[:3000]), 0.5 tie.
Mean over pairs where both texts have >= 3000 chars. Refuted if below 0.53.
"""
import json
import os
import subprocess
import sys
import zlib

FILES = {
    "base": ("s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_math500.jsonl",
             "runs/theory-tests/r4m01/base01_F_math500.jsonl"),
    "rl": ("s3://pg-lineage-769063704696/results/rlneurons/r3/s2800-01/out/P_math500.jsonl",
           "runs/theory-tests/r4m01/s2800_P_math500.jsonl"),
}


def out(d):
    print(json.dumps(d))
    sys.exit(0)


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def fetch(s3, local):
    if os.path.exists(local) and os.path.getsize(local) > 0:
        return
    os.makedirs(os.path.dirname(local), exist_ok=True)
    r = subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr",
                        "--only-show-errors"], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(local):
        nc("could not fetch %s: %s" % (s3, r.stderr.strip()[:300]))


def load(local):
    rows = []
    with open(local) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def ratio(s):
    b = s.encode("utf-8")
    return len(zlib.compress(b, 9)) / len(b)


def slim(row):
    d = {k: v for k, v in row.items() if k not in ("text", "prefill_ids")}
    d["text_first_200"] = row.get("text", "")[:200]
    d["len_text"] = len(row.get("text", ""))
    return d


def main():
    by = {}
    for name, (s3, local) in FILES.items():
        fetch(s3, local)
        rows = load(local)
        for k in ("problem_index", "sample", "text"):
            if not any(k in r for r in rows):
                nc("field %s missing from %s" % (k, s3))
        d = {}
        dup = 0
        for r in rows:
            if r.get("sample") != 0:
                continue
            if r["problem_index"] in d:
                dup += 1
                continue  # keep first occurrence
            d[r["problem_index"]] = r
        if dup:
            print("warning: %d duplicate sample-0 rows in %s (first kept)" % (dup, name))
        by[name] = d

    common = sorted(set(by["base"]) & set(by["rl"]))
    scores = []
    example = None
    for pi in common:
        b, r = by["base"][pi], by["rl"][pi]
        tb, tr = b.get("text") or "", r.get("text") or ""
        if len(tb) < 3000 or len(tr) < 3000:
            continue
        rB, rR = ratio(tb[:3000]), ratio(tr[:3000])
        scores.append(1.0 if rB < rR else (0.5 if rB == rR else 0.0))
        if example is None:
            example = {"base": slim(b), "rl": slim(r), "rB": rB, "rR": rR}

    print("base_sample0=%d rl_sample0=%d common=%d kept_pairs=%d"
          % (len(by["base"]), len(by["rl"]), len(common), len(scores)))
    if not scores:
        nc("no pair has both texts >= 3000 characters")
    m = sum(scores) / len(scores)
    out({"measured": m, "refuted_by_met": m < 0.53, "alt_measured": None,
         "not_computable": None, "example_row": example, "n_pairs": len(scores)})


if __name__ == "__main__":
    main()
