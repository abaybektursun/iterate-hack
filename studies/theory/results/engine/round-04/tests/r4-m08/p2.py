"""r4-m08 prediction 2: median ln(base/RL length) on both-right harder-328 problems, pre minus post."""
import json
import math
import os
import subprocess

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01"
BASE_JOB = "abaybektursun-1114-151534-e72c"  # base cue
RL_JOB = "abaybektursun-1114-151540-86ef"    # RL plain
OVERLAP = "studies/rlneurons/results/rln3/rln3_overlap.json"
POST_SOURCES = {"aime2025", "hmmt_feb2025"}


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))


def fetch(job):
    path = f"runs/theory-tests/{job}/answers.jsonl"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{job}/answers.jsonl", path,
                            "--profile", "iterate-ecr", "--only-show-errors"])
        if r.returncode != 0 or not os.path.exists(path):
            subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", path])
    if not os.path.exists(path):
        return None
    return path


def load(path):
    rows = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                rows[r["unique_id"]] = r
    return rows


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    if n % 2:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def slim(r):
    return {k: v for k, v in r.items() if k not in ("text", "prompt")}


def main():
    bp, rp = fetch(BASE_JOB), fetch(RL_JOB)
    if bp is None or rp is None:
        out(None, False, None, "answers.jsonl could not be fetched", None)
        return
    base, rl = load(bp), load(rp)
    flags = json.load(open(OVERLAP))["sets"]["hard"]["flags"]

    kept = {"pre": [], "post": []}
    kept_alt = {"pre": [], "post": []}
    ex = None
    for u in sorted(set(base) & set(rl)):
        b, r = base[u], rl[u]
        key = str(r["problem_index"])
        if key not in flags:
            out(None, False, None, f"problem_index {key} of {u} not in rln3_overlap.json", None)
            return
        src = flags[key]["source"]
        if src != u.split("/")[0]:
            out(None, False, None, f"source mismatch for {u}: overlap says {src}", None)
            return
        g = "post" if src in POST_SOURCES else "pre"
        if not (b["score_v3"] == 1 and r["score_v3"] == 1):
            continue
        if not (b["cap_hit"] is False and r["cap_hit"] is False):
            continue
        if b["n_generated"] <= 0 or r["n_generated"] <= 0:
            out(None, False, None, f"non-positive n_generated for {u}", None)
            return
        kept[g].append(math.log(b["n_generated"] / r["n_generated"]))
        if b["n_new"] > 0 and r["n_new"] > 0:
            kept_alt[g].append(math.log(b["n_new"] / r["n_new"]))
        if ex is None or (g == "post" and ex["group"] != "post"):
            ex = {"unique_id": u, "group": g, "source": src,
                  "base_n_generated": b["n_generated"], "rl_n_generated": r["n_generated"],
                  "r": math.log(b["n_generated"] / r["n_generated"]),
                  "base_row": slim(b), "rl_row": slim(r)}

    if len(kept["post"]) < 5:
        # recipe: recorded as missing and counts as refuted
        out(None, True, None, None, None)
        return
    if len(kept["pre"]) == 0:
        out(None, False, None, "no pre-cutoff problems kept; median undefined", None)
        return
    stat = median(kept["pre"]) - median(kept["post"])
    alt = None
    if len(kept_alt["post"]) >= 5 and kept_alt["pre"]:
        alt = median(kept_alt["pre"]) - median(kept_alt["post"])
    out(stat, stat > 0.15, alt, None, ex)


if __name__ == "__main__":
    main()
