"""r3-across-2 P3: cued base hold-on rate, T 1.0 (S3 T1.jsonl) / T 0.6 top-p 0.95 (S3 base-01 F_math500.jsonl, sample 0).
Both files: keep cap_hit false. Rate = matches of \\b(Wait|Hmm)\\b (case-sensitive) / total chars of text x 10,000, pooled.
Statistic: rate(T1) / rate(F sample 0). Refuted if ratio < 1.08.
alt_measured: same, but F_math500 keeps every sample (not only sample 0)."""
import json, os, re, subprocess

OUT = "runs/theory-tests"
BUCKET = "s3://pg-lineage-769063704696/results/rlneurons"
FILES = {"T1": ("r4/base_rl-02/out/T1.jsonl", "base_rl-02_T1.jsonl"),
         "F": ("r3/base-01/out/F_math500.jsonl", "base-01_F_math500.jsonl")}
PAT = re.compile(r"\b(Wait|Hmm)\b")
NULL = {"measured": None, "refuted_by_met": False, "alt_measured": None, "example_row": None}


def fetch(key, local):
    path = os.path.join(OUT, local)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        os.makedirs(OUT, exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{key}", path], capture_output=True, text=True)
        if r.returncode != 0:
            if os.path.exists(path):
                os.remove(path)
            print(f"fetch failed for {key}: {r.stderr.strip()[-300:]}")
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


def rate(rows):
    m = sum(len(PAT.findall(r["text"])) for r in rows)
    c = sum(len(r["text"]) for r in rows)
    print(f"  rows {len(rows)} matches {m} chars {c}")
    return (m / c * 10000) if c else None


def slim(r):
    return {k: (v[:300] + "..." if isinstance(v, str) and len(v) > 300 else v) for k, v in r.items()}


def main():
    paths = {k: fetch(*v) for k, v in FILES.items()}
    if any(p is None for p in paths.values()):
        print(json.dumps(NULL))
        return
    t1 = load(paths["T1"])
    f = load(paths["F"])
    for name, rows in (("T1", t1), ("F", f)):
        if not rows or "text" not in rows[0] or "cap_hit" not in rows[0]:
            print(f"{name}: missing text or cap_hit field")
            print(json.dumps(NULL))
            return
    t1_keep = [r for r in t1 if not is_cap(r)]
    f_s0 = [r for r in f if int(r.get("sample", -1)) == 0 and not is_cap(r)]
    f_all = [r for r in f if not is_cap(r)]
    print(f"T1 rows {len(t1)} kept {len(t1_keep)}; F rows {len(f)} sample0-kept {len(f_s0)} all-kept {len(f_all)}")
    print("T1:"); r_t1 = rate(t1_keep)
    print("F sample 0:"); r_f0 = rate(f_s0)
    print("F all samples:"); r_fa = rate(f_all)
    measured = (r_t1 / r_f0) if (r_t1 is not None and r_f0) else None
    alt = (r_t1 / r_fa) if (r_t1 is not None and r_fa) else None
    print(f"rate T1 {r_t1} rate F0 {r_f0} rate Fall {r_fa}")
    print(json.dumps({"measured": measured,
                      "refuted_by_met": bool(measured is not None and measured < 1.08),
                      "alt_measured": alt,
                      "example_row": slim(t1_keep[0]) if t1_keep else None}))


if __name__ == "__main__":
    main()
