"""r3-across-2 P5: fraction of the base-to-RL hold-on rate increase reached by theta(0.25), all cue, T 1.0.
Files: S3 r4/base_rl-02/out/T1.jsonl (base cue, a = 0); iterate-runs abaybektursun-1114-153102-b029/answers.jsonl (theta0.25_cue);
iterate-runs abaybektursun-1114-153110-e985/answers.jsonl (rl_cue).
One row per problem_index (highest attempt if duplicated); keep cap_hit false.
Rate = matches of \\b(Wait|Hmm)\\b (case-sensitive) / total chars of text x 10,000, pooled.
Statistic: (rate(theta0.25) - rate(T1)) / (rate(rl_cue) - rate(T1)). Refuted if < 0.35.
alt_measured: same statistic without the cap_hit filter (cap-hit rows kept)."""
import json, os, re, subprocess

OUT = "runs/theory-tests"
PAT = re.compile(r"\b(Wait|Hmm)\b")
NULL = {"measured": None, "refuted_by_met": False, "alt_measured": None, "example_row": None}


def fetch_s3(key, local):
    path = os.path.join(OUT, local)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        os.makedirs(OUT, exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", f"s3://pg-lineage-769063704696/results/rlneurons/{key}", path],
                           capture_output=True, text=True)
        if r.returncode != 0:
            if os.path.exists(path):
                os.remove(path)
            print(f"fetch failed for {key}: {r.stderr.strip()[-300:]}")
            return None
    return path


def fetch_modal(job):
    d = os.path.join(OUT, job)
    path = os.path.join(d, "answers.jsonl")
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        os.makedirs(d, exist_ok=True)
        r = subprocess.run(["modal", "volume", "get", "--force", "iterate-runs", f"{job}/answers.jsonl", path],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            print(f"fetch failed for {job}: {(r.stderr or r.stdout).strip()[-300:]}")
            return None
    return path


def load(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def is_cap(r):
    c = r["cap_hit"]
    if isinstance(c, str):
        return c.strip().lower() == "true"
    return bool(c)


def dedup(rows):
    by = {}
    for r in rows:
        i = r["problem_index"]
        a = r.get("attempt", 0) or 0
        if i not in by or a >= (by[i].get("attempt", 0) or 0):
            by[i] = r
    return [by[i] for i in sorted(by)]


def rate(rows, name):
    m = sum(len(PAT.findall(r["text"])) for r in rows)
    c = sum(len(r["text"]) for r in rows)
    print(f"  {name}: rows {len(rows)} matches {m} chars {c}")
    return (m / c * 10000) if c else None


def frac(r0, r25, r1):
    if None in (r0, r25, r1) or r1 == r0:
        return None
    return (r25 - r0) / (r1 - r0)


def slim(r):
    return {k: (v[:300] + "..." if isinstance(v, str) and len(v) > 300 else v) for k, v in r.items()}


def main():
    paths = {"T1": fetch_s3("r4/base_rl-02/out/T1.jsonl", "base_rl-02_T1.jsonl"),
             "th25": fetch_modal("abaybektursun-1114-153102-b029"),
             "rl": fetch_modal("abaybektursun-1114-153110-e985")}
    if any(p is None for p in paths.values()):
        print(json.dumps(NULL))
        return
    data = {}
    for k, p in paths.items():
        rows = load(p)
        if not rows or any(f not in rows[0] for f in ("text", "cap_hit", "problem_index")):
            print(f"{k}: missing text, cap_hit or problem_index")
            print(json.dumps(NULL))
            return
        data[k] = dedup(rows)
        print(f"{k}: raw rows {len(rows)} after dedup {len(data[k])} cap hits {sum(is_cap(r) for r in data[k])}")
    print("cap_hit false:")
    keep = {k: [r for r in v if not is_cap(r)] for k, v in data.items()}
    rr = {k: rate(v, k) for k, v in keep.items()}
    print("all rows:")
    ra = {k: rate(v, k) for k, v in data.items()}
    measured = frac(rr["T1"], rr["th25"], rr["rl"])
    alt = frac(ra["T1"], ra["th25"], ra["rl"])
    print(f"rates no-cap {rr}; rates all {ra}")
    print(json.dumps({"measured": measured,
                      "refuted_by_met": bool(measured is not None and measured < 0.35),
                      "alt_measured": alt,
                      "example_row": slim(keep["th25"][0]) if keep["th25"] else None}))


if __name__ == "__main__":
    main()
