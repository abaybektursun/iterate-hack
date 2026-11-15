#!/usr/bin/env python3
"""r4-m01 prediction 2: AUROC of -zlib ratio(text[:6000]) for loop_A in the
cued base T 0.6 / top-p 1.0 MATH-500 answers (abaybektursun-1114-151718-d4fa).
Refuted if AUROC below 0.58.
"""
import json
import os
import subprocess
import sys
import zlib

VOL = "iterate-runs"
REMOTE = "abaybektursun-1114-151718-d4fa/answers.jsonl"
LOCAL = "runs/theory-tests/r4m01/d4fa/answers.jsonl"


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
    r = subprocess.run(["modal", "volume", "get", VOL, REMOTE, LOCAL],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(LOCAL):
        nc("could not fetch %s:%s: %s" % (VOL, REMOTE, (r.stderr or r.stdout).strip()[:300]))


def ratio(s):
    b = s.encode("utf-8")
    return len(zlib.compress(b, 9)) / len(b)


def auroc(pos, neg):
    """Mann-Whitney AUROC: P(score_pos > score_neg) + 0.5 P(tie)."""
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
    d = {k: v for k, v in row.items() if k not in ("text", "prompt", "prefill_ids")}
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
    for k in ("text", "loop_A", "onset_A_char"):
        if not any(k in r for r in rows):
            nc("field %s missing from %s" % (k, REMOTE))

    kept = []
    for r in rows:
        t = r.get("text") or ""
        if len(t) < 6000:
            continue
        la = r.get("loop_A")
        if la is True:
            on = r.get("onset_A_char")
            if on is None or on < 7000:
                continue
        elif la is not False:
            continue  # loop_A missing: neither false nor true-with-onset
        kept.append(r)

    pos, neg = [], []
    example = None
    for r in kept:
        s = ratio(r["text"][:6000])
        (pos if r["loop_A"] is True else neg).append(-s)
        if example is None and r["loop_A"] is True:
            example = slim(r)
            example["s"] = s
    if example is None and kept:
        example = slim(kept[0])
        example["s"] = ratio(kept[0]["text"][:6000])

    info = "rows=%d kept=%d positives=%d negatives=%d" % (len(rows), len(kept), len(pos), len(neg))
    print(info)
    a = auroc(pos, neg)
    if a is None:
        nc("AUROC undefined after filtering (%s)" % info)
    out({"measured": a, "refuted_by_met": a < 0.58, "alt_measured": None,
         "not_computable": None, "example_row": example,
         "n_kept": len(kept), "n_pos": len(pos)})


if __name__ == "__main__":
    main()
