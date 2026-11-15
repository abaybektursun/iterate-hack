"""r5-m03 prediction 2: count of quick finished-wrong answers in top8 plain."""
import json, os, subprocess, sys

TOP8 = "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"


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


rows = load(TOP8)
hit, hit_alt, example = set(), set(), None
for r in rows:
    s = r.get("score_v3")
    if s is None:
        continue  # missing score_v3 left out
    pi, ng, cap = r.get("problem_index"), r.get("n_generated"), r.get("cap_hit")
    if ng is None or cap is None:
        continue
    if s == 0 and cap is False and ng <= 2000:
        if pi not in hit and example is None:
            example = r
        hit.add(pi)
    # alt reading: strict "under 2,000" boundary
    if s == 0 and cap is False and ng < 2000:
        hit_alt.add(pi)

m = len(hit)
print(json.dumps({"measured": m, "refuted_by_met": bool(m <= 4 or m >= 23),
                  "alt_measured": len(hit_alt), "not_computable": None,
                  "example_row": example if example is not None else (rows[0] if rows else None)}))
