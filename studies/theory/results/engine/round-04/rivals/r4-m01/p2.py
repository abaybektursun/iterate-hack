"""duel-r4-m01 p2: AUROC of RL answer length (s2800 P_math500 sample 0, n_generated) for a later rule-A loop
in the d4fa base-cue T0.6/top-p 1.0 rows.

Main: d = RL row's n_generated (cap hits as stored), AUROC by Mann-Whitney, ties 0.5.
Alt: d = RL row's n_new instead of n_generated (the other token-count field).
"""
import json
import os
import subprocess
import sys

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


def auroc(pos, neg):
    if not pos or not neg:
        return None
    tot = 0.0
    for p in pos:
        for q in neg:
            tot += 1.0 if p > q else (0.5 if p == q else 0.0)
    return tot / (len(pos) * len(neg))


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
    n_short = n_early = n_noRL = 0
    for r in D:
        if len(r["text"]) < 6000:
            n_short += 1
            continue
        if r["loop_A"] is True:
            on = r.get("onset_A_char")
            if on is None or on < 7000:
                n_early += 1
                continue
        elif r["loop_A"] is not False:
            nc(f"loop_A has a non-boolean value {r['loop_A']!r}")
        q = rl.get(r["problem_index"])
        if q is None:
            n_noRL += 1
            continue
        kept.append((r, q))

    pos = [q["n_generated"] for r, q in kept if r["loop_A"] is True]
    neg = [q["n_generated"] for r, q in kept if r["loop_A"] is False]
    alt_ok = all("n_new" in q for _, q in kept)
    apos = [q["n_new"] for r, q in kept if r["loop_A"] is True] if alt_ok else []
    aneg = [q["n_new"] for r, q in kept if r["loop_A"] is False] if alt_ok else []
    n_rlcap = sum(1 for _, q in kept if q.get("cap_hit") is True)
    print(f"d4fa rows={len(D)} dropped: short={n_short} early_or_missing_onset={n_early} no_RL_row={n_noRL}")
    print(f"kept rows={len(kept)} positives={len(pos)} negatives={len(neg)} RL cap hits among kept={n_rlcap}")

    alt = auroc(apos, aneg) if alt_ok else None
    m = auroc(pos, neg)
    if m is None:
        out({"measured": None, "refuted_by_met": False, "alt_measured": alt,
             "not_computable": f"AUROC undefined: positives={len(pos)}, negatives={len(neg)}",
             "example_row": None})
    r0, q0 = next(((r, q) for r, q in kept if r["loop_A"] is True), kept[0])
    ex = trunc(r0)
    ex["_RL_row"] = trunc(q0)
    ex["_d"] = q0["n_generated"]
    out({"measured": m, "refuted_by_met": False, "alt_measured": alt,
         "not_computable": None, "example_row": ex})


if __name__ == "__main__":
    main()
