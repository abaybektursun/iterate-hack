"""p4: share of Code 3.0 Q4 deficit to held-out base lying on Q4 problems with base s0 + s1 <= 1."""
import json, os, re, sys

AXIS = "studies/rlneurons/results/axis/math500-01"
PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def fail(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": reason, "example_row": None}))
    sys.exit(0)


def load():
    for f in (AXIS + "/vectors.json", AXIS + "/manifest.json", PP):
        if not os.path.exists(f):
            fail("file not readable: " + f)
    vec = json.load(open(AXIS + "/vectors.json"))
    man = json.load(open(AXIS + "/manifest.json"))
    pp = json.load(open(PP))
    arms_m = man["arms"]
    # base cue sample arms: base model (family base_cue), cue prompt, not derived, "sample i" in manifest order
    base = []
    for name, a in arms_m.items():
        if a.get("family") == "base_cue" and a.get("prompt") == "cue" and a.get("derived_from") is None:
            mm = re.search(r"sample (\d+)", a.get("what", ""))
            if mm:
                base.append((int(mm.group(1)), name))
    base.sort()
    if [s for s, _ in base] != [0, 1, 2, 3]:
        fail("could not find base cue samples 0-3 in manifest: %r" % base)
    base_names = [n for _, n in base]
    # manifest has no 'model' field; the model is named in 'what'
    def find(model_str):
        c = [n for n, a in arms_m.items() if model_str in a.get("what", "") and a.get("prompt") == "cue"
             and a.get("derived_from") is None]
        return c
    c30 = find("Olmo-3-7B-RL-Zero-Code")
    if len(c30) != 1:
        fail("Code 3.0 cue arm not unique in manifest: %r" % c30)
    c31 = find("RL-Zero-Code 3.1")
    code31 = c31[0] if len(c31) == 1 else None
    pidx = vec["problem_indices"]

    def arm(name):
        out = {}
        for i, s in zip(pidx, vec["arms"][name]):
            out[i] = 0 if s is None else int(s)
        return out
    A = {n: arm(n) for n in base_names + c30 + ([code31] if code31 else [])}
    get = lambda name, i: A[name].get(i, 0)  # missing row counts as 0
    toks = {}
    for r in pp:
        toks[r["problem_index"]] = r["t2_generated_tokens"]  # cap hit counts as its stored count
    order = sorted(toks, key=lambda i: (toks[i], i))
    return dict(base=base_names, code=c30[0], code31=code31, get=get, order=order, toks=toks, pp={r["problem_index"]: r for r in pp})


def row(D, i, code):
    g = D["get"]
    r = {"problem_index": i, "t2_generated_tokens": D["toks"][i], "t2_cap_hit": D["pp"][i].get("t2_cap_hit"),
         "code_arm": code, "code_cue": g(code, i)}
    for s, n in enumerate(D["base"]):
        r["base_s%d" % s] = g(n, i)
    return r


def stat(D, code):
    g, b = D["get"], D["base"]
    q4 = D["order"][375:500]  # ranks 376-500, 125 problems
    d = {i: (g(b[2], i) + g(b[3], i)) / 2 - g(code, i) for i in q4}
    H = [i for i in q4 if g(b[0], i) + g(b[1], i) <= 1]
    den = sum(d.values())
    if den <= 0:
        return 0.0, H
    return sum(d[i] for i in H) / den, H


D = load()
if len(D["order"]) != 500:
    fail("per_problem.json does not hold 500 problems")
m, H = stat(D, D["code"])
alt = stat(D, D["code31"])[0] if D["code31"] else None
ex = row(D, H[0], D["code"]) if H else row(D, D["order"][375], D["code"])
print(json.dumps({"measured": m, "refuted_by_met": False, "alt_measured": alt, "not_computable": None, "example_row": ex}))
