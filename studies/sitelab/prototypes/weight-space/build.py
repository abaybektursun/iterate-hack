"""Build data.json for the weight-space prototype from committed result files only.

  python3 studies/sitelab/prototypes/weight-space/build.py

Every number is read from a readout of studies/rlneurons/results; nothing is typed here except where a model
sits (its lane and its coefficient a, which are the arguments the edit was made with) and its board result id.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "../../../rlneurons/results")
P = "studies/rlneurons/results/"
load = lambda p: json.load(open(os.path.join(R, p)))

edits = load("xreward/edits/readout.json")["cells"]
table = load("table/hard328-02/table.json")
tp = load("transplant/hard328-01/readout.json")
tp500 = load("transplant/math500-01/readout.json")
wd = load("day1_wdiff/readout.json")["cells"]
wsp = load("wsp1/readout.json")["cells"]
d15 = load("xreward/dial15_math500-01/readout.json")
vecs = table["per_problem_right"]
models = []


def vec(key):
    v = vecs.get(key)
    return None if v is None else "".join(str(round(x * 4)) for x in v)  # 0..4 = right in 0..4 quarters


def add(bench, lane, a, label, right, cap, tokens, n, src, result, key=None, control=False, note=None, edit=None):
    m = dict(id=f"{bench}:{lane}:{a}", bench=bench, lane=lane, a=a, label=label, right=right, cap=cap,
             tokens=round(tokens), n=n, src=P + src, result=result, control=control)
    if note: m["note"] = note
    if key: m["vec"] = vec(key)
    if edit: m["edit_pct"] = round(100 * edit["add_rel"], 3)
    models.append(m)


def cell(lane, a, name, label, result, key=None, control=False, note=None):
    c = edits[name]
    add("hard328", lane, a, label, c["right_v3"], c["cap_hits"], c["mean_generated_tokens"], c["n"],
        "xreward/edits/readout.json [" + name + "]", result, key, control, note, c.get("edit"))


# 328 harder problems, cue, T 1.0 / top-p 1.0, one sample, cap 16,384, grader v3
cell("base", 0, "base_cue_T1", "base", "result-82b4dc", "axis|base_cue")
cell("full", 0.25, "theta0.25_cue", "base + 0.25 (RL - base)", "result-e45bf4", "axis|theta0.25_cue")
cell("full", 0.5, "theta0.5_cue", "base + 0.5 (RL - base)", "result-e45bf4", "axis|theta0.5_cue")
cell("full", 1, "rl_cue_T1", "RL-Zero-Math", "result-099916", "axis|rl_cue")
cell("k1", 1, "top1_math31", "base + top 1 direction of the RL change", "result-51a0e7")
cell("k64", 1, "top64_math31", "base + top 64 directions of the RL change", "result-51a0e7")
for a, name, res, key in [(-1, "top8xm1_math31", "result-6f1bb7", "m1"), (0.5, "top8x0.5_math31", "result-6f1bb7", "0.5"),
                          (1, "top8_math31", "result-284db5", "1"), (1.5, "top8x1.5_math31", "result-6f1bb7", "1.5"),
                          (2, "top8x2_math31", "result-51a0e7", "2"), (3, "top8x3_math31", "result-6f1bb7", "3")]:
    cell("k8", a, name, f"base + {a:g} x top 8 directions of the RL change", res, "dial|" + key)
for a, name, res, key in [(-1, "rand8xm1_math31", "result-6f1bb7", "rm1"), (1, "rand8_math31", "result-284db5", "r1"),
                          (2, "rand8x2_math31", "result-6f1bb7", "r2"), (3, "rand8x3_math31", "result-6f1bb7", "r3")]:
    cell("rand", a, name, f"base + {a:g} x 8 random directions", res, "dial|" + key, control=True)
th = tp["references"]["think"]
add("hard328", "sft", 0, "Think-SFT", th["right"] / 4, th["cap_hits"] / 4, th["tokens_per_problem"], 328,
    "transplant/hard328-01/readout.json [references.think]", "result-818c20", "think|single", note="mean of 4 samples")
for name, arm in tp["arms"].items():
    k = arm["n"] // 328
    a = round(arm["alpha"])
    if arm["random"]:
        add("hard328", "sftnoise", 1, "Think-SFT + random noise of the RL change's norm", arm["right"], arm["cap_hits"],
            arm["tokens_per_problem"], 328, "transplant/hard328-01/readout.json [" + name + "]", "result-3387ce",
            "transplant|" + name, control=True)
    else:
        add("hard328", "sft", a, f"Think-SFT + {a} (RL - base)", arm["right"] / k, arm["cap_hits"] / k,
            arm["tokens_per_problem"], 328, "transplant/hard328-01/readout.json [" + name + "]", "result-3387ce",
            "transplant|" + name, note="mean of 2 samples" if k == 2 else None)


# MATH-500, cue, T 1.0 / top-p 1.0, one sample, cap 16,384, grader v3
def w(lane, a, name, label, result, control=False):
    c = wd[name]
    add("math500", lane, a, label, c["right_v3"], c["cap_hits"], c["mean_generated_tokens"], c["n"],
        "day1_wdiff/readout.json [" + name + "]", result, control=control)


w("base", 0, "T1_base_cue", "base", "result-c36598")
for a in (0.25, 0.5, 0.75, 1.25, 1.5):
    w("full", a, f"theta{a:g}_cue", f"base + {a:g} (RL - base)", "result-4b0d5f")
w("full", 1, "rl_cue", "RL-Zero-Math", "result-4b0d5f")
w("rand", 1, "random_cue", "base + a random change of the RL change's norm, every direction", "result-4b0d5f", control=True)
add("math500", "k8", 1.5, "base + 1.5 x top 8 directions of the RL change", d15["rows"]["single"]["right"],
    d15["each_sample"]["cap_hits_attempt_0"][0], d15["rows"]["single"]["tokens_per_problem"], 500,
    "xreward/dial15_math500-01/readout.json", "result-95a4dc")
c = wsp["full500/sft1_cue"]
add("math500", "sft", 0, "Think-SFT", c["right_v3"], c["cap_hits"], c["mean_generated_tokens"], 500,
    "wsp1/readout.json [full500/sft1_cue]", "result-818c20")
c = tp500["arms"]["sft1_rl10"]
add("math500", "sft", 1, "Think-SFT + 1 (RL - base)", c["right"], c["cap_hits"], c["tokens_per_problem"], 500,
    "transplant/math500-01/readout.json [sft1_rl10]", "result-3387ce")

out = dict(models=models, table="studies/rlneurons/results/table/hard328-02/table.json",
           checks=load("table/hard328-02/checks.json").get("summary"))
json.dump(out, open(os.path.join(HERE, "data.json"), "w"), separators=(",", ":"))
print(len(models), "models,", os.path.getsize(os.path.join(HERE, "data.json")), "bytes")
for m in models: print(m["id"], m["right"], m["cap"], m["tokens"], "vec" if m.get("vec") else "-")
