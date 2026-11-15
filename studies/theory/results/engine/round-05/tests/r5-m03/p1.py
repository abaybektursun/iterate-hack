"""r5-m03 prediction 1: median per-problem ln(top8 n_generated / T1 tokens)."""
import json, math, os, subprocess, sys

TOP8 = "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
T1T2 = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def nc(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": reason, "example_row": None}))
    sys.exit(0)


def load(path):
    # Files are committed in the repo; if missing in the worktree, fetch from git into runs/theory-tests/.
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
            continue  # first occurrence per problem_index
        out[pi] = r
    return out


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n % 2 == 1:
        return xs[n // 2]
    return (xs[n // 2 - 1] + xs[n // 2]) / 2.0


top8 = by_index(load(TOP8))
t1 = by_index(load(T1T2))

vals, alt_vals, example = [], [], None
for pi in sorted(set(top8) & set(t1)):
    a, b = top8[pi], t1[pi]
    ng, tt = a.get("n_generated"), b.get("t1_generated_tokens")
    if ng is None or tt is None:
        continue  # missing row value -> dropped
    v = math.log(max(ng, 1) / max(tt, 1))
    vals.append(v)
    if example is None:
        example = {"top8": a, "t1t2": b}
    # alt reading: drop problems where either side hit the cap
    if not a.get("cap_hit") and not b.get("t1_cap_hit"):
        alt_vals.append(v)

if not vals:
    print(json.dumps({"measured": None, "refuted_by_met": True, "alt_measured": None,
                      "not_computable": None, "example_row": None}))
    sys.exit(0)

m = median(vals)
alt = median(alt_vals) if alt_vals else None
print(f"n_joined={len(vals)} n_alt_no_cap={len(alt_vals)}", file=sys.stderr)
print(json.dumps({"measured": m, "refuted_by_met": bool(m > 0.35 or m < -0.10),
                  "alt_measured": alt, "not_computable": None, "example_row": example}))
