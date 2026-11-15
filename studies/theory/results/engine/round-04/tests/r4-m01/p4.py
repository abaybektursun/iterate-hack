#!/usr/bin/env python3
"""r4-m01 prediction 4: within K_own and K_rl separately, AUROC of
-zlib ratio(text[:3000]) for cap_hit; statistic = unweighted mean of the two
AUROCs (or the defined one if the other is undefined). Refuted if below 0.53.
alt_measured: pooled AUROC over the kept rows of both files together.
"""
import json
import os
import subprocess
import sys
import zlib

BASE = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_k-01/k_a/"
FILES = {
    "K_own": (BASE + "K_own.jsonl", "runs/theory-tests/r4m01/K_own.jsonl"),
    "K_rl": (BASE + "K_rl.jsonl", "runs/theory-tests/r4m01/K_rl.jsonl"),
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


def auroc(pos, neg):
    if not pos or not neg:
        return None
    tot = 0.0
    for p in pos:
        for q in neg:
            if p > q:
                tot += 1.0
            elif p == q:
                tot += 0.5
    return tot / (len(pos) * len(neg))


def slim(row):
    d = {k: v for k, v in row.items() if k not in ("text", "prefill_ids")}
    d["text_first_200"] = row.get("text", "")[:200]
    d["len_text"] = len(row.get("text", ""))
    return d


def main():
    res = {}
    all_pos, all_neg = [], []
    example = None
    for name, (s3, local) in FILES.items():
        fetch(s3, local)
        rows = load(local)
        for k in ("text", "cap_hit", "loop_A", "onset_A_char"):
            if not any(k in r for r in rows):
                nc("field %s missing from %s" % (k, s3))
        pos, neg = [], []
        n_kept = 0
        for r in rows:
            t = r.get("text") or ""
            if len(t) < 3000:
                continue
            if r.get("loop_A") is True:
                on = r.get("onset_A_char")
                if on is None or on < 4000:
                    continue
            ch = r.get("cap_hit")
            if ch not in (True, False):
                continue
            n_kept += 1
            s = ratio(t[:3000])
            (pos if ch is True else neg).append(-s)
            if example is None and ch is True:
                example = slim(r)
                example["s"] = s
        a = auroc(pos, neg)
        res[name] = {"auroc": a, "n_rows": len(rows), "n_kept": n_kept,
                     "n_cap": len(pos), "n_noncap": len(neg)}
        all_pos += pos
        all_neg += neg
        print("%s: %s" % (name, json.dumps(res[name])))

    defined = [v["auroc"] for v in res.values() if v["auroc"] is not None]
    if not defined:
        nc("AUROC undefined in both files after filtering: %s" % json.dumps(res))
    m = sum(defined) / len(defined)
    alt = auroc(all_pos, all_neg)
    out({"measured": m, "refuted_by_met": m < 0.53, "alt_measured": alt,
         "not_computable": None, "example_row": example, "per_file": res})


if __name__ == "__main__":
    main()
