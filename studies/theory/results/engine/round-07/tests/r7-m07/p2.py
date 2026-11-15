"""r7-m07 prediction 2: Math 3.1 cue minus Math 3.0 cue right answers (v3 vectors) on the short half (ranks 1-250 by T2)."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

VEC = "studies/rlneurons/results/axis/math500-01/vectors.json"
MAN = "studies/rlneurons/results/axis/math500-01/manifest.json"
PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"

M30_MODEL = "Olmo-3-7B-RL-Zero-Math (3.0)"
M31_MODEL = "RL-Zero-Math 3.1"
EDIT_WORDS = ("theta", "random", "top ", "rand", "shots", "base +", "vote", "delta", "edit")


def pick_arms(manifest, vectors):
    arms = manifest["arms"]
    # The manifest has no "model" field; the model is named in each arm's "what" text.
    m30 = [k for k, a in arms.items() if M30_MODEL in a.get("what", "") and a.get("prompt") == "cue"]
    if "rl_cue" in vectors["arms"]:
        m31 = "rl_cue"
    else:
        c = [k for k, a in arms.items() if M31_MODEL in a.get("what", "") and a.get("prompt") == "cue"
             and not any(w in a.get("what", "") for w in EDIT_WORDS)]
        m31 = c[0] if c else None
    return (m30[0] if len(m30) == 1 else None), m31, m30


def main():
    for f in (VEC, MAN, PP):
        if not os.path.exists(f):
            return not_computable(f"missing file {f}")
    vec = json.load(open(VEC))
    man = json.load(open(MAN))
    pp = json.load(open(PP))
    m30, m31, m30_all = pick_arms(man, vec)
    if m30 is None:
        return not_computable(f"M30 arm not unique or absent in manifest: {m30_all}")
    if m31 is None or m31 not in vec["arms"]:
        return not_computable("M31 arm not found")
    idx = vec["problem_indices"]
    a30 = {pi: v for pi, v in zip(idx, vec["arms"][m30])}
    a31 = {pi: v for pi, v in zip(idx, vec["arms"][m31])}

    rows = sorted(pp, key=lambda r: (r["t2_generated_tokens"], r["problem_index"]))
    if len(rows) != 500:
        return not_computable(f"per_problem.json has {len(rows)} rows, not 500")
    half = rows[0:250]  # ranks 1-250

    def val(a, pi):
        v = a.get(pi)
        return 0 if v is None else int(v)  # missing counts 0

    items = [(val(a31, r["problem_index"]), val(a30, r["problem_index"]), r) for r in half]

    def stat(sample):
        return sum(x[0] for x in sample) - sum(x[1] for x in sample)

    measured = stat(items)

    # Alt reading: short half by value threshold, keeping every problem tied with the rank-250 length.
    thr = rows[249]["t2_generated_tokens"]
    half_alt = [r for r in rows if r["t2_generated_tokens"] <= thr]
    alt = sum(val(a31, r["problem_index"]) - val(a30, r["problem_index"]) for r in half_alt)

    ex = dict(half[0])
    ex.update({"arm_M31": m31, "M31_v3": items[0][0], "arm_M30": m30, "M30_v3": items[0][1]})
    report(measured, len(items), bootstrap(stat, items), "bootstrap",
           refuted_by_met=measured > 5, alt_measured=alt, example_row=ex)


main()
