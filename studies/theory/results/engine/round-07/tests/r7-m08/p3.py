"""r7-m08 prediction 3: Code 3.1 cue accuracy on MATH-500 problems where the cued base is right in 0 of 4 samples."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

REL = "studies/rlneurons/results/axis/math500-01/vectors.json"
BASE = ["base_cue_s0", "base_cue_s1", "base_cue_s2", "base_cue_s3"]
CODE = "code_cue"


def load(rel):
    if os.path.exists(rel):
        return json.load(open(rel))
    local = os.path.join("runs/theory-tests", rel)
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        out = subprocess.run(["git", "show", "HEAD:" + rel], capture_output=True)
        if out.returncode != 0:
            return None
        open(local, "wb").write(out.stdout)
    return json.load(open(local))


d = load(REL)
if not isinstance(d, dict) or "arms" not in d or "problem_indices" not in d:
    not_computable(f"{REL} not readable or lacks arms / problem_indices")
    raise SystemExit
arms = d["arms"]
missing = [a for a in BASE + [CODE] if a not in arms]
if missing:
    not_computable(f"arms missing: {missing}")
    raise SystemExit

pidx = d["problem_indices"]
uids = d.get("unique_ids") or [None] * len(pidx)


def val(arm, i):
    v = arms[arm]
    x = v[i] if i < len(v) else None
    return 0 if x is None else x


Z = []
for i, p in enumerate(pidx):
    k = sum(val(a, i) for a in BASE)
    if k == 0:
        Z.append({"problem_index": p, "unique_id": uids[i] if i < len(uids) else None,
                  **{a: val(a, i) for a in BASE}, CODE: val(CODE, i)})

if not Z:
    refuted_without_number()
    raise SystemExit


def stat(rows):
    return sum(r[CODE] for r in rows) / len(rows)


m = stat(Z)
report(m, len(Z), bootstrap(stat, Z), "bootstrap", refuted_by_met=(m > 0.36), alt_measured=None, example_row=Z[0])
