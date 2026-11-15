"""duel-r4-m08 p2: both-right base/RL median log length ratio, pre minus post, clean harder 328, T 0.6."""
import json
import math
import os
import subprocess
import sys

DIR = "runs/theory-tests/duel-r4-m08"
FILES = {
    "base": ("s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_hard.jsonl",
             os.path.join(DIR, "base01_F_hard.jsonl")),
    "rl": ("s3://pg-lineage-769063704696/results/rlneurons/r3/s2800-01/out/P_hard.jsonl",
           os.path.join(DIR, "s2800_P_hard.jsonl")),
}
OVERLAP = "studies/rlneurons/results/rln3/rln3_overlap.json"  # = results/rln3/rln3_overlap.json in the rlneurons study
POST_SOURCES = {"aime2025", "hmmt_feb2025"}


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))
    sys.exit(0)


def fetch(uri, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def load_rows(path):
    best = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            uid = r["unique_id"]
            s = r.get("sample")
            s = 0 if s is None else s
            if uid not in best or s < (best[uid].get("sample") or 0):
                best[uid] = r
    return best


def slim(r):
    d = dict(r)
    if isinstance(d.get("text"), str) and len(d["text"]) > 200:
        d["text"] = d["text"][:200] + "...[truncated]"
    return d


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    m = n // 2
    return xs[m] if n % 2 else (xs[m - 1] + xs[m]) / 2.0


def main():
    try:
        for k, (uri, path) in FILES.items():
            fetch(uri, path)
        base = load_rows(FILES["base"][1])
        rl = load_rows(FILES["rl"][1])
        flags = json.load(open(OVERLAP))["sets"]["hard"]["flags"]
    except Exception as e:  # noqa
        out(None, False, None, f"could not read inputs: {e!r}", None)

    problems = []
    for uid in sorted(set(base) & set(rl)):
        b, p = base[uid], rl[uid]
        fb, fp = flags.get(str(b["problem_index"])), flags.get(str(p["problem_index"]))
        if fb is None or fp is None:
            continue
        if fb.get("flag") != fp.get("flag") or fb.get("source") != fp.get("source"):
            continue
        if fp.get("flag") != "none":
            continue
        grp = "post" if fp.get("source") in POST_SOURCES else "pre"
        problems.append((uid, grp, b, p))

    if not problems:
        out(None, False, None, "no joined clean problems", None)

    def compute(field, use_cap):
        kept = []
        for uid, grp, b, p in problems:
            if not (b.get("score") == 1 and p.get("score") == 1):
                continue
            if use_cap and not (b.get("cap_hit") is False and p.get("cap_hit") is False):
                continue
            nb, nr = b.get(field), p.get(field)
            if not nb or not nr or nb <= 0 or nr <= 0:
                continue
            kept.append((grp, math.log(nb / nr), p))
        return kept

    def stat(field):
        kept = compute(field, True)
        fallback = False
        if not any(g == "post" for g, _, _ in kept):
            kept = compute(field, False)
            fallback = True
        post = [r for g, r, _ in kept if g == "post"]
        pre = [r for g, r, _ in kept if g == "pre"]
        if not post or not pre:
            return None, kept, fallback, len(pre), len(post)
        return median(pre) - median(post), kept, fallback, len(pre), len(post)

    measured, kept, fallback, npre, npost = stat("n_generated")
    if measured is None:
        out(None, False, None,
            f"empty group after filters (kept pre={npre}, post={npost}, cap condition dropped={fallback})", None)
    alt, _, _, _, _ = stat("n_new")  # alt: lengths as n_new (tokens sampled) instead of n_generated

    ex = slim(next(p for g, _, p in kept if g == "post"))
    sys.stderr.write(f"kept pre={npre} post={npost} cap_condition_dropped={fallback}\n")
    out(measured, False, alt, None, ex)


if __name__ == "__main__":
    main()
