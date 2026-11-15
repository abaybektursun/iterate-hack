#!/usr/bin/env python3
"""r4-m01 prediction 1: within-problem early compressibility, base-01 F_math500.

C = cap-hit row with lowest sample, F = finished row (len >= 3000) with lowest
sample, per problem. Score 1 if ratio(C[:3000]) < ratio(F[:3000]), 0.5 tie, 0 else.
Mean over qualifying problems. Refuted if below 0.52.
"""
import json
import os
import subprocess
import sys
import zlib
from collections import defaultdict

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_math500.jsonl"
LOCAL = "runs/theory-tests/r4m01/base01_F_math500.jsonl"


def out(d):
    print(json.dumps(d))
    sys.exit(0)


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def fetch():
    if os.path.exists(LOCAL) and os.path.getsize(LOCAL) > 0:
        return
    os.makedirs(os.path.dirname(LOCAL), exist_ok=True)
    r = subprocess.run(["aws", "s3", "cp", S3, LOCAL, "--profile", "iterate-ecr",
                        "--only-show-errors"], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(LOCAL):
        nc("could not fetch %s: %s" % (S3, r.stderr.strip()[:300]))


def ratio(s):
    b = s.encode("utf-8")
    return len(zlib.compress(b, 9)) / len(b)


def slim(row):
    d = {k: v for k, v in row.items() if k not in ("text", "prefill_ids")}
    d["text_first_200"] = row.get("text", "")[:200]
    d["len_text"] = len(row.get("text", ""))
    return d


def main():
    fetch()
    rows = []
    with open(LOCAL) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    for k in ("problem_index", "cap_hit", "sample", "text"):
        if not any(k in r for r in rows):
            nc("field %s missing from %s" % (k, S3))

    groups = defaultdict(list)
    for r in rows:
        groups[r["problem_index"]].append(r)

    n_samples = sorted({r.get("sample") for r in rows}, key=lambda x: (x is None, x))
    scores = []
    example = None
    for pi, g in sorted(groups.items()):
        caps = [r for r in g if r.get("cap_hit") is True]
        fins = [r for r in g if r.get("cap_hit") is False and len(r.get("text") or "") >= 3000]
        if not caps or not fins:
            continue
        C = min(caps, key=lambda r: r["sample"])
        F = min(fins, key=lambda r: r["sample"])
        rC = ratio(C["text"][:3000])
        rF = ratio(F["text"][:3000])
        scores.append(1.0 if rC < rF else (0.5 if rC == rF else 0.0))
        if example is None:
            example = {"C": slim(C), "F": slim(F), "rC": rC, "rF": rF}

    print("rows=%d problems=%d samples_present=%s qualifying=%d"
          % (len(rows), len(groups), n_samples, len(scores)), file=sys.stderr)
    print("rows=%d problems=%d samples_present=%s qualifying=%d"
          % (len(rows), len(groups), n_samples, len(scores)))
    if not scores:
        nc("no problem qualifies: the file holds %d rows, samples present %s "
           "(one row per problem), so no problem has both a cap_hit true row and a "
           "cap_hit false row; the within-problem pair the recipe asks for does not "
           "exist in the stored rows" % (len(rows), n_samples))
    m = sum(scores) / len(scores)
    out({"measured": m, "refuted_by_met": m < 0.52, "alt_measured": None,
         "not_computable": None, "example_row": example,
         "n_qualifying": len(scores)})


if __name__ == "__main__":
    main()
