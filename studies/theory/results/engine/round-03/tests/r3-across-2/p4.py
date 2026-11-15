"""r3-across-2 P4: RL plain hold-on rate, T 1.0 (S3 r4/modal_t2-01/t2/T2.jsonl) / T 0.6 top-p 0.95
(S3 next_n13/s3gate-03/out/rl/rl/math500/generations.jsonl). All rows of both, no cap filter.
Rate = matches of \\b(Wait|Hmm)\\b (case-sensitive) / total chars of text x 10,000, pooled. Statistic: rate(T2) / rate(n13 RL).
Refuted if ratio > 1.2 or < 0.83.
alt_measured: same ratio keeping only rows with cap_hit false in both files (if n13 rows carry cap_hit; else null)."""
import json, os, re, subprocess

OUT = "runs/theory-tests"
BUCKET = "s3://pg-lineage-769063704696/results"
FILES = {"T2": ("rlneurons/r4/modal_t2-01/t2/T2.jsonl", "modal_t2-01_T2.jsonl"),
         "N13": ("next_n13/s3gate-03/out/rl/rl/math500/generations.jsonl", "n13_s3gate-03_rl_math500_generations.jsonl")}
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
    t2 = load(paths["T2"])
    n13 = load(paths["N13"])
    for name, rows in (("T2", t2), ("N13", n13)):
        if not rows or any("text" not in r for r in rows):
            print(f"{name}: missing text field")
            print(json.dumps(NULL))
            return
    print(f"T2 rows {len(t2)}; n13 rows {len(n13)}; n13 distinct problem_index {len({r.get('problem_index') for r in n13})}")
    print("T2:"); r_t2 = rate(t2)
    print("n13 RL:"); r_n = rate(n13)
    measured = (r_t2 / r_n) if (r_t2 is not None and r_n) else None
    alt = None
    if all("cap_hit" in r for r in t2) and all("cap_hit" in r for r in n13):
        print("T2 no-cap:"); a2 = rate([r for r in t2 if not is_cap(r)])
        print("n13 no-cap:"); an = rate([r for r in n13 if not is_cap(r)])
        alt = (a2 / an) if (a2 is not None and an) else None
    print(f"rate T2 {r_t2} rate n13 {r_n}")
    print(json.dumps({"measured": measured,
                      "refuted_by_met": bool(measured is not None and (measured > 1.2 or measured < 0.83)),
                      "alt_measured": alt,
                      "example_row": slim(t2[0])}))


if __name__ == "__main__":
    main()
