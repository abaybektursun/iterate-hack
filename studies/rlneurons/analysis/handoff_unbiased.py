"""Prefix hand-off on the unbiased subset U: the pool problems that are in the pool whatever base sample 0 did
(`unbiased` in data/handoff/plan_v1.json, n = 155). The pool of 183 was picked with base sample 0, which also supplies the
base prefixes, so the base's own-prefix column is too low on the pool and the recovered share too high. Reads the committed
rows of results/handoff/{base,rl}-01/ and writes the cross-minus-own differences of analysis/handoff.py on U.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.handoff_unbiased --nn 01
"""
import argparse
import json

from studies.rlneurons.analysis.handoff import CUTS, STUDY, diff

ap = argparse.ArgumentParser()
ap.add_argument("--nn", required=True)
a = ap.parse_args()
out = STUDY / "results" / "handoff" / f"unbiased-{a.nn}"
out.mkdir(parents=True)                                             # never into an existing run folder
U = sorted(json.loads((STUDY / "data" / "handoff" / "plan_v1.json").read_text())["unbiased"])
rows = {}
for f in ("base", "rl"):
    for line in (STUDY / "results" / "handoff" / f"{f}-01" / "rows.jsonl").read_text().splitlines():
        r = json.loads(line)
        rows[r["finisher"], r["writer"], r["cut"], r["problem_index"]] = r["score_v3"]
col = lambda f, w, c: [rows[f, w, c, i] for i in U]
ro = {"n_unbiased": len(U), "rows": "results/handoff/base-01/rows.jsonl, rl-01/rows.jsonl", "cuts": {}}
for c in CUTS:
    gap, rec = diff(col("rl", "rl", c), col("base", "base", c)), diff(col("base", "rl", c), col("base", "base", c))
    ro["cuts"][c] = {"right": {f"{f}_finisher|{w}_writer": sum(col(f, w, c)) for f in ("base", "rl") for w in ("base", "rl")},
                     "rl_own_minus_base_own": gap, "base_on_rl_prefix_minus_base_own": rec,
                     "rl_on_base_prefix_minus_rl_own": diff(col("rl", "base", c), col("rl", "rl", c)),
                     "recovered_percent": 100 * rec["points"] / gap["points"]}
(out / "readout.json").write_text(json.dumps(ro, indent=1) + "\n")
for c, v in ro["cuts"].items():
    print(c, v["right"], *("%s %+.1f [%+.1f, %+.1f]" % (k, v[k]["points"], *v[k]["ci95"]) for k in list(v)[1:4]), "recovered %.0f %%" % v["recovered_percent"])
