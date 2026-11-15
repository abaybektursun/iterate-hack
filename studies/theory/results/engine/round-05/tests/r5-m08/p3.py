"""r5-m08 prediction 3: Code 3.1 cue minus Code 3.0 cue right count on the shorter half
(Q1+Q2 = 250 lowest t2_generated_tokens, ties by problem_index ascending).
Refuted if the difference > 5.
"""
import json
import os
import sys

AXIS = "studies/rlneurons/results/axis/math500-01"
VEC = os.path.join(AXIS, "vectors.json")
MAN = os.path.join(AXIS, "manifest.json")
PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def out(d):
    print(json.dumps(d))
    sys.exit(0)


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def load():
    for f in (VEC, MAN, PP):
        if not os.path.exists(f):
            nc(f"file missing: {f}")
    vec = json.load(open(VEC))
    man = json.load(open(MAN))
    pp = json.load(open(PP))
    return vec, man, pp


def find_arm(man, vec, want_name, what_substr, prompt="cue"):
    """Arm named want_name whose manifest 'what' contains what_substr and prompt matches."""
    arms = man.get("arms", {})
    cands = [k for k, a in arms.items()
             if what_substr in (a.get("what") or "") and a.get("prompt") == prompt
             and a.get("derived_from") is None]
    if want_name is not None:
        if want_name not in arms or want_name not in cands:
            nc(f"arm {want_name} not found or does not match '{what_substr}', prompt {prompt} (candidates {cands})")
        name = want_name
    else:
        if len(cands) != 1:
            nc(f"expected one arm matching '{what_substr}', prompt {prompt}; got {cands}")
        name = cands[0]
    if name not in vec.get("arms", {}):
        nc(f"arm {name} not in vectors.json")
    return name


def arm_map(vec, name):
    idx = vec["problem_indices"]
    v = vec["arms"][name]
    if len(v) != len(idx):
        nc(f"arm {name}: vector length {len(v)} != problem_indices {len(idx)}")
    m = {}
    for i, x in zip(idx, v):
        m[int(i)] = 0 if x is None else int(x)  # missing / null counts as 0
    return m


def quartiles(pp):
    rows = {}
    for r in pp:
        if "problem_index" not in r or "t2_generated_tokens" not in r:
            nc("per_problem.json row lacks problem_index or t2_generated_tokens")
        if r["t2_generated_tokens"] is None:
            nc(f"t2_generated_tokens is null for problem {r['problem_index']}")
        rows[int(r["problem_index"])] = r
    if len(rows) != 500:
        nc(f"per_problem.json has {len(rows)} problems, not 500")
    order = sorted(rows, key=lambda i: (rows[i]["t2_generated_tokens"], i))
    Q = [order[0:125], order[125:250], order[250:375], order[375:500]]
    return rows, Q



vec, man, pp = load()
a31 = find_arm(man, vec, "code_cue", "RL-Zero-Code 3.1")
a30 = find_arm(man, vec, None, "Olmo-3-7B-RL-Zero-Code (3.0)")
c31 = arm_map(vec, a31)
c30 = arm_map(vec, a30)
rows, Q = quartiles(pp)
half = Q[0] + Q[1]

r31 = sum(c31.get(i, 0) for i in half)
r30 = sum(c30.get(i, 0) for i in half)
measured = r31 - r30

ex_i = half[0]
example = dict(rows[ex_i])
example.update({"code31_cue": c31.get(ex_i, 0), "code30_cue": c30.get(ex_i, 0), "quartile": 1})

print(json.dumps({"code31_q12": r31, "code30_q12": r30, "arm31": a31, "arm30": a30}), file=sys.stderr)
out({"measured": measured, "refuted_by_met": bool(measured > 5), "alt_measured": None,
     "not_computable": None, "example_row": example})
