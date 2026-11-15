"""duel-r4-m01 p3: AUROC of early compressibility (zlib ratio of text[:6000]) for a later rule-A loop,
computed within quartile strata of RL answer length (s2800 P_math500 sample 0, n_generated).

Main: pooled within-stratum pairs: total score / total pairs (lower s for the positive scores 1, ties 0.5).
Alt: unweighted mean of the per-stratum AUROCs over strata that have both positives and negatives.
"""
import json
import os
import subprocess
import sys
import zlib

import numpy as np

DIR = os.path.join("runs", "theory-tests", "duel-r4-m01")
FILES = {
    "d4fa_answers.jsonl": ["modal", "volume", "get", "iterate-runs",
                           "abaybektursun-1114-151718-d4fa/answers.jsonl", None],
    "s2800_P_math500.jsonl": ["aws", "s3", "cp",
                              "s3://pg-lineage-769063704696/results/rlneurons/r3/s2800-01/out/P_math500.jsonl",
                              None, "--profile", "iterate-ecr"],
}


def out(d):
    print(json.dumps(d))
    sys.exit(0)


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def fetch(name):
    path = os.path.join(DIR, name)
    if not os.path.exists(path):
        os.makedirs(DIR, exist_ok=True)
        cmd = [path if c is None else c for c in FILES[name]]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            nc(f"could not fetch {name}: {r.stderr.strip()[:300]}")
    return path


def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def trunc(row, n=400):
    return {k: (v[:n] + "...[truncated]" if isinstance(v, str) and len(v) > n else v) for k, v in row.items()}


def ratio(s):
    b = s.encode("utf-8")
    return len(zlib.compress(b, 9)) / len(b)


def main():
    D = load(fetch("d4fa_answers.jsonl"))
    P = load(fetch("s2800_P_math500.jsonl"))
    if not D or not P:
        nc("empty row file")
    for fld in ("problem_index", "text", "loop_A"):
        if any(fld not in r for r in D):
            nc(f"d4fa: field {fld} missing in some rows")
    for fld in ("problem_index", "sample", "n_generated"):
        if any(fld not in r for r in P):
            nc(f"s2800 P_math500: field {fld} missing in some rows")

    rl = {}
    for r in P:
        if r["sample"] == 0:
            if r["problem_index"] in rl:
                print(f"warning: duplicate RL sample-0 row for problem {r['problem_index']}; keeping first")
                continue
            rl[r["problem_index"]] = r

    kept = []
    for r in D:
        if len(r["text"]) < 6000:
            continue
        if r["loop_A"] is True:
            on = r.get("onset_A_char")
            if on is None or on < 7000:
                continue
        elif r["loop_A"] is not False:
            nc(f"loop_A has a non-boolean value {r['loop_A']!r}")
        q = rl.get(r["problem_index"])
        if q is None:
            continue
        kept.append({"row": r, "rl": q, "s": ratio(r["text"][:6000]), "d": q["n_generated"],
                     "y": r["loop_A"] is True})
    if not kept:
        nc("no rows survive the filters")

    d_all = np.array([k["d"] for k in kept], dtype=float)
    q1, q2, q3 = np.percentile(d_all, [25, 50, 75])
    for k in kept:
        d = k["d"]
        k["stratum"] = 1 if d <= q1 else (2 if d <= q2 else (3 if d <= q3 else 4))
    print(f"kept rows={len(kept)} positives={sum(k['y'] for k in kept)} q1={q1} q2={q2} q3={q3}")

    tot_score = 0.0
    tot_pairs = 0
    per_auc = []
    for st in (1, 2, 3, 4):
        pos = [k["s"] for k in kept if k["stratum"] == st and k["y"]]
        neg = [k["s"] for k in kept if k["stratum"] == st and not k["y"]]
        sc = 0.0
        for p in pos:
            for n in neg:
                sc += 1.0 if p < n else (0.5 if p == n else 0.0)
        npairs = len(pos) * len(neg)
        print(f"stratum {st}: rows={len(pos) + len(neg)} positives={len(pos)} negatives={len(neg)} pairs={npairs}"
              + (f" auc={sc / npairs:.4f}" if npairs else ""))
        tot_score += sc
        tot_pairs += npairs
        if npairs:
            per_auc.append(sc / npairs)
    print(f"total pairs={tot_pairs}")
    alt = float(np.mean(per_auc)) if per_auc else None
    if tot_pairs == 0:
        out({"measured": None, "refuted_by_met": False, "alt_measured": alt,
             "not_computable": "no within-stratum positive/negative pairs", "example_row": None})
    measured = tot_score / tot_pairs
    k0 = next((k for k in kept if k["y"]), kept[0])
    ex = trunc(k0["row"])
    ex["_RL_row"] = trunc(k0["rl"])
    ex["_s"] = k0["s"]
    ex["_d"] = k0["d"]
    ex["_stratum"] = k0["stratum"]
    out({"measured": measured, "refuted_by_met": False, "alt_measured": alt,
         "not_computable": None, "example_row": ex})


if __name__ == "__main__":
    main()
