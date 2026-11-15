"""r5-m03 prediction 3: fraction of T1-wrong problems that top8 plain also gets wrong."""
import json, os, subprocess, sys

TOP8 = "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
T1T2 = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def nc(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": reason, "example_row": None}))
    sys.exit(0)


def load(path):
    if not os.path.exists(path):
        dst = os.path.join("runs/theory-tests", path)
        if not os.path.exists(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            r = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True)
            if r.returncode != 0:
                nc(f"cannot read {path}: {r.stderr.decode()[:200]}")
            open(dst, "wb").write(r.stdout)
        path = dst
    try:
        d = json.load(open(path))
    except Exception as e:
        nc(f"cannot parse {path}: {e}")
    if not isinstance(d, list):
        nc(f"{path} is not a list of rows")
    return d


def by_index(rows):
    out = {}
    for r in rows:
        pi = r.get("problem_index")
        if pi is None or pi in out:
            continue
        out[pi] = r
    return out


t1 = by_index(load(T1T2))
top8 = by_index(load(TOP8))

# Main: T1 wrong = t1_right falsy (0); grader v3 already scores a cap hit as wrong.
# top8 wrong = score_v3 == 0 (a cap hit is stored as score_v3 0 under v3).
den = num = 0
den_alt = num_alt = 0
example = None
for pi in sorted(t1):
    b = t1[pi]
    if pi not in top8:
        continue  # missing from top8 dropped
    a = top8[pi]
    s = a.get("score_v3")
    tr = b.get("t1_right")
    if tr is None:
        continue
    if not tr:
        if s is not None:
            den += 1
            if s == 0:
                num += 1
                if example is None:
                    example = {"t1t2": b, "top8": a}
    # alt: force cap hits to wrong on both sides regardless of stored score
    if (not tr) or b.get("t1_cap_hit"):
        if s is not None or a.get("cap_hit"):
            den_alt += 1
            if s == 0 or a.get("cap_hit"):
                num_alt += 1

if den == 0:
    print(json.dumps({"measured": None, "refuted_by_met": True, "alt_measured": None,
                      "not_computable": None, "example_row": None}))
    sys.exit(0)

m = num / den
alt = num_alt / den_alt if den_alt else None
print(f"den={den} num={num} den_alt={den_alt} num_alt={num_alt}", file=sys.stderr)
print(json.dumps({"measured": m, "refuted_by_met": bool(m < 0.33 or m > 0.60),
                  "alt_measured": alt, "not_computable": None, "example_row": example}))
