"""duel-r5-m08 p1: Code 3.0 cue accuracy on Q4 problems that all 4 cued base samples solve."""
import json
import os
import sys

VEC = "studies/rlneurons/results/axis/math500-01/vectors.json"
MAN = "studies/rlneurons/results/axis/math500-01/manifest.json"
PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def fail(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": reason, "example_row": None}))
    sys.exit(0)


def load(path):
    if not os.path.exists(path):
        fail(f"file missing: {path}")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:  # noqa
        fail(f"file not readable: {path}: {e}")


vec = load(VEC)
man = load(MAN)
pp = load(PP)

arms = vec.get("arms")
marms = man.get("arms")
pidx = vec.get("problem_indices")
if not isinstance(arms, dict) or not isinstance(marms, dict) or not isinstance(pidx, list):
    fail("vectors.json / manifest.json lack arms or problem_indices")

# Base arms: manifest model allenai/Olmo-3-1025-7B (the 'base' family), cue prompt, samples 0-3,
# not derived (derived_from null) and not the random-difference control.
base_arms = []
for name, m in marms.items():
    what = (m.get("what") or "").lower()
    if (m.get("family") == "base_cue" and m.get("prompt") == "cue" and m.get("derived_from") is None
            and "random" not in what and what.startswith("base + cue, sample")):
        base_arms.append(name)
base_arms.sort()
if len(base_arms) != 4:
    fail(f"expected 4 base cue sample arms, found {base_arms}")

# Code 3.0 arm: Olmo-3-7B-RL-Zero-Code (3.0), cue prompt.
code_arms = [name for name, m in marms.items()
             if "olmo-3-7b-rl-zero-code" in (m.get("what") or "").lower()
             and "3.0" in (m.get("what") or "") and m.get("prompt") == "cue"
             and m.get("derived_from") is None]
if len(code_arms) != 1:
    fail(f"expected one Code 3.0 cue arm, found {code_arms}")
code_arm = code_arms[0]
for a in base_arms + [code_arm]:
    if a not in arms:
        fail(f"arm {a} in manifest but not in vectors.json")


def arm_map(name):
    v = arms[name]
    out = {}
    for i, x in zip(pidx, v):
        out[int(i)] = 1 if x == 1 else 0  # None / missing -> 0
    return out


bmaps = [arm_map(a) for a in base_arms]
cmap = arm_map(code_arm)

rows = pp if isinstance(pp, list) else None
if rows is None:
    fail("per_problem.json is not a list of rows")
for r in rows:
    if "problem_index" not in r or "t2_generated_tokens" not in r:
        fail("per_problem.json row lacks problem_index or t2_generated_tokens")
    if not isinstance(r["t2_generated_tokens"], (int, float)):
        fail(f"t2_generated_tokens not numeric for problem {r.get('problem_index')}")
rowby = {int(r["problem_index"]): r for r in rows}

# Main Q4: ascending by tokens, ties by problem_index ascending, ranks 376-500.
asc = sorted(rows, key=lambda r: (r["t2_generated_tokens"], int(r["problem_index"])))
q4 = [int(r["problem_index"]) for r in asc[375:500]]
# Alt Q4: "the 125 with the highest" read as descending by tokens, ties by problem_index ascending, top 125.
desc = sorted(rows, key=lambda r: (-r["t2_generated_tokens"], int(r["problem_index"])))
q4_alt = [int(r["problem_index"]) for r in desc[:125]]


def get(m, i):
    return m.get(i, 0)


def stat(q):
    S = [i for i in q if all(get(b, i) == 1 for b in bmaps)]
    if not S:
        return 0.0, S
    return sum(get(cmap, i) for i in S) / len(S), S


measured, S = stat(q4)
alt, _ = stat(q4_alt)

ex = None
if S:
    i = S[0]
elif q4:
    i = q4[0]
else:
    i = None
if i is not None:
    ex = dict(rowby.get(i, {"problem_index": i}))
    for a, b in zip(base_arms, bmaps):
        ex[a] = get(b, i)
    ex[code_arm] = get(cmap, i)

print(json.dumps({"measured": measured, "refuted_by_met": False, "alt_measured": alt,
                  "not_computable": None, "example_row": ex}))
