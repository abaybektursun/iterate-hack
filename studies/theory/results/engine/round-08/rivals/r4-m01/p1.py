"""duel-r4-m01 p1: opening compressibility, capped F sample vs finished K_fresh restart (same problem).

Main: ratio over text[:3000] as stored (text includes the cue opening " line!\n\nOkay" in both files).
Alt: same, after removing the shared cue opening " line!\n\nOkay" from the start of both texts
(so the 3000 / 8000 character windows cover model-generated text only).
"""
import json
import os
import subprocess
import sys
import zlib

DIR = os.path.join("runs", "theory-tests", "duel-r4-m01")
FILES = {
    "K_fresh.jsonl": ["aws", "s3", "cp",
                      "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_k-01/k_b/K_fresh.jsonl",
                      None, "--profile", "iterate-ecr"],
    "base01_F_math500.jsonl": ["aws", "s3", "cp",
                               "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_math500.jsonl",
                               None, "--profile", "iterate-ecr"],
}
CUE = " line!\n\nOkay"


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


def ratio(s):
    b = s.encode("utf-8")
    return len(zlib.compress(b, 9)) / len(b)


def strip_cue(t):
    return t[len(CUE):] if t.startswith(CUE) else t


def trunc(row, n=400):
    return {k: (v[:n] + "...[truncated]" if isinstance(v, str) and len(v) > n else v) for k, v in row.items()}


def run(K, F, transform):
    # lowest-sample K row per problem
    kbest = {}
    for r in K:
        pi = r["problem_index"]
        if pi not in kbest or r["sample"] < kbest[pi]["sample"]:
            kbest[pi] = r
    # lowest-sample capped F row per problem
    fbest = {}
    for r in F:
        if r.get("cap_hit") is True:
            pi = r["problem_index"]
            if pi not in fbest or r["sample"] < fbest[pi]["sample"]:
                fbest[pi] = r
    scores, example = [], None
    counts = {"K_problems": len(kbest), "drop_K_cap": 0, "drop_K_short": 0, "drop_K_early_loop": 0,
              "drop_no_F": 0, "drop_F_short": 0, "drop_F_degenerate": 0}
    for pi in sorted(kbest):
        k = kbest[pi]
        kt = transform(k["text"])
        if k.get("cap_hit") is not False:
            counts["drop_K_cap"] += 1
            continue
        if len(kt) < 3000:
            counts["drop_K_short"] += 1
            continue
        if k.get("loop_A") is True:
            on = k.get("onset_A_char")
            if on is None or on < 3000:
                counts["drop_K_early_loop"] += 1
                continue
        f = fbest.get(pi)
        if f is None:
            counts["drop_no_F"] += 1
            continue
        ft = transform(f["text"])
        if len(ft) < 3000:
            counts["drop_F_short"] += 1
            continue
        if ratio(ft[:8000]) < 0.10:
            counts["drop_F_degenerate"] += 1
            continue
        rF = ratio(ft[:3000])
        rK = ratio(kt[:3000])
        s = 1.0 if rF < rK else (0.5 if rF == rK else 0.0)
        scores.append(s)
        if example is None:
            example = dict(trunc(k))
            example["_partner_F_row"] = trunc(f)
            example["_rF"] = rF
            example["_rK"] = rK
            example["_score"] = s
    return scores, counts, example


def main():
    K = load(fetch("K_fresh.jsonl"))
    F = load(fetch("base01_F_math500.jsonl"))
    for name, rows, fields in (("K_fresh", K, ["problem_index", "sample", "text", "cap_hit", "loop_A"]),
                               ("F_math500", F, ["problem_index", "sample", "text", "cap_hit"])):
        if not rows:
            nc(f"{name} has no rows")
        for fld in fields:
            if any(fld not in r for r in rows):
                nc(f"{name}: field {fld} missing in some rows")
    scores, counts, example = run(K, F, lambda t: t)
    alt_scores, alt_counts, _ = run(K, F, strip_cue)
    print(f"main: kept problems = {len(scores)}; counts = {counts}; "
          f"wins={sum(1 for s in scores if s == 1)} ties={sum(1 for s in scores if s == 0.5)}")
    print(f"alt (cue stripped): kept problems = {len(alt_scores)}; counts = {alt_counts}")
    alt = (sum(alt_scores) / len(alt_scores)) if alt_scores else None
    if not scores:
        out({"measured": None, "refuted_by_met": False, "alt_measured": alt,
             "not_computable": "no problem survives the filters (kept problems = 0)", "example_row": None})
    measured = sum(scores) / len(scores)
    refuted = False  # refuted_by is null
    out({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
         "not_computable": None, "example_row": example})


if __name__ == "__main__":
    main()
