"""Build data.json for the prototype model-interior from committed result files. Run from anywhere:

  python3 studies/sitelab/prototypes/model-interior/build.py

Every value is copied or summed from the files named in SRC; nothing is typed in.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../../.."))
RL = "studies/rlneurons/results/"
CN = "studies/cleanneurons/results/"
SRC = {
    "matrices": RL + "wsp1/anatomy-01/metrics.json",
    "summary": RL + "wsp1/anatomy-01/summary.json",
    "readout": RL + "wsp1/anatomy-01/readout.json",
    "edits": RL + "xreward/edits/readout.json",
    "merge": RL + "day1_wdiff/merge_stats.json",
    "profile": CN + "transplant/curve-01/profile.json",
    "rank_attr": CN + "transplant/curve_attr-01/rank_attr_readout.json",
    "loops": CN + "loops/real-02/metrics.json",
    "loop100": CN + "loops/real-02/edit_attr100.json",
    "loop1000": CN + "loops/real-02/edit_attr1000.json",
    "gen_seed1": CN + "gen/readout_t06_real02.json",
    "gen_seed2": CN + "gen/readout_t06_seed2.json",
    "gen_vote": CN + "gen/readout_vote_t06.json",
    "gen_t10_100": CN + "gen/attr100r2_t10-01/metrics.json",
    "gen_t10_1000": CN + "gen/attr1000r2_t10-01/metrics.json",
    "base_t10": RL + "rln4/grader_v3/readout.json",
    "dose": CN + "describe/attr1000_loops-01/dose_summary.json",
    "neurons": CN + "describe/attr_top100-01/neurons.json",
    "density": CN + "describe/attr_top100-01/density_readout.json",
    "descriptions": CN + "describe/attr_top100-01/descriptions_test.json",
}


def load(key):
    with open(os.path.join(ROOT, SRC[key])) as f:
        return json.load(f)


def r(x, n=5):
    return None if x is None else float(f"{x:.{n}g}")


out = {"src": SRC}

# 1. The 224 layer matrices and the other tensors: size and spectrum of (RL-Zero-Math - base).
met, summ = load("matrices"), load("summary")
mats, others = [], []
for t in met["tensors"]:
    d = t["delta"]["rl_math"]
    if t["layer"] is not None and "svals_top16" in d:
        mats.append({
            "l": t["layer"], "m": t["module"], "name": t["name"], "shape": t["shape"],
            "nd": r(d["norm_delta"]), "nb": r(d["norm_base"]), "rel": r(d["rel"]),
            "t1": r(d["top1_share"]), "t8": r(d["top8_share"]), "sr": r(d["stable_rank"], 4),
            "sv": [r(s, 4) for s in d["svals_top16"]],
            "sft_nd": r(t["delta"]["think_sft"]["norm_delta"]), "sft_t8": r(t["delta"]["think_sft"]["top8_share"]),
            "code_cos": r(t["pair"]["rl_math-rl_code"]["cos"], 3),
        })
    else:
        others.append({"name": t["name"], "m": t["module"], "l": t["layer"], "shape": t["shape"],
                       "nd": r(d["norm_delta"]), "rel": r(d["rel"])})
assert len(mats) == 224
out["mats"] = mats
out["others"] = [o for o in others if o["m"] in ("embed", "lm_head")]
out["by_layer"] = [{k: r(summ["by_layer"][str(i)]["delta"]["rl_math"][k]) for k in ("norm_delta", "rel", "top1_share", "top8_share", "stable_rank")}
                   for i in range(32)]
out["by_module"] = {m: {k: r(v["delta"]["rl_math"].get(k)) for k in ("norm_delta", "rel", "top1_share", "top8_share", "stable_rank")}
                    for m, v in summ["by_module"].items() if m in ("q", "k", "v", "o", "gate", "up", "down")}
out["totals"] = {"all": summ["totals"]["all_tensors"]["delta"]["rl_math"], "layer_matrices": summ["totals"]["layer_matrices"]["delta"]["rl_math"],
                 "layer_matrices_all": {k: r(summ["layer_matrices"]["delta"]["rl_math"][k]) for k in ("top1_share", "top8_share", "stable_rank")}}
h3 = summ["hypotheses"]["H3"]
out["null_top8"] = {"4096x4096": r(h3["null_top8_share"]["model.layers.16.self_attn.q_proj.weight"]),
                    "11008x4096": r(h3["null_top8_share"]["model.layers.16.mlp.up_proj.weight"]),
                    "4096x11008": r(h3["null_top8_share"]["model.layers.16.mlp.down_proj.weight"])}
h4 = summ["hypotheses"]["H4"]
out["cue_hits"] = {"layers": h4["layers"], "top": h4["top"], "hits": [{"l": h["layer"], "m": h["module"], "d": h["direction"], "sign": h["sign"], "ids": h["cue_ids_in_top"]} for h in h4["hits_rl_math"]],
                   "n_readouts": h4["n_readouts_rl_math"], "n_null": h4["n_readouts_null"], "null_hits": h4["n_null_readouts_with_cue_in_top"]}
mg = load("merge")["rl"]["overall"]
out["overall"] = {"numel": mg["numel"], "frac_changed": r(mg["frac_changed"]), "rel_norm": r(mg["rel_norm"])}
out["share"] = load("profile")["share_of_squared_weight_change"]
out["attr1_per_layer"] = load("rank_attr")["attr1_neurons_per_layer"]

# 2. What the top three directions of each o_proj and down_proj write toward, through the base unembedding.
ro = load("readout")
out["cue_tokens"] = dict(zip([str(i) for i in ro["cue_ids"]], ro["cue_tokens"]))
rd = {}
for x in ro["rows"]:
    if x["delta"] != "rl_math":
        continue
    rd.setdefault(f'{x["layer"]}.{x["module"]}', []).append(
        {"d": x["direction"], "sign": x["sign"], "sval": r(x["sval"], 4), "share": r(x["share"], 3),
         "toks": x["toks"][:10], "ids": x["ids"][:10], "cue_rank": x["cue_rank"]})
out["readout"] = rd

# 3. Measured cells of the low-rank edits: hard328, opening cue, T 1.0, cap 16,384, one sample, grader v3.
ed = load("edits")
cells = {}
for k, v in ed["cells"].items():
    e = v.get("edit") or {}
    cells[k] = {"right": v["right_v3"], "n": v["n"], "cap": v["cap_hits"], "loops": v["loops_A"], "tokens": v["mean_generated_tokens"],
                "share": r(e.get("share")), "add_norm": r(e.get("add_norm")), "add_rel": r(e.get("add_rel")), "scale": e.get("scale"), "k": e.get("k"),
                "recipe": e.get("recipe"), "run": v.get("run_folder")}
out["cells"] = cells
out["paired"] = {k: v for k, v in ed["paired_differences_points"].items() if k.endswith("minus base_cue_T1") or k.endswith("minus rl_plain_T1")}

# 4. Loop neurons (run 2): the sets, the held-out loop counts, the MATH-500 cells.
lp = load("loops")
out["loop_sets"] = {"100": load("loop100")["zero"], "1000": load("loop1000")["zero"]}
out["loop_heldout"] = {k: {"n": v["heldout"]["n"], "looped": v["heldout"]["looped"], "loss": r(v["normal"]["loss_change_relative"], 3)}
                       for k, v in lp["conditions"].items()}
out["loop_source"] = {"rows": lp["loops"]["rows"], "looped": lp["loops"]["looped"]}


def gen(d):
    o = {"unedited": {k: d["baseline"][k] for k in ("right_v3", "cap_hits", "loops_rule_A", "tokens_per_problem")}}
    for k, v in d["arms"].items():
        o[k] = {kk: v[kk] for kk in ("right_v3", "cap_hits", "loops_rule_A", "tokens_per_problem", "points_vs_baseline", "ci95")}
    return o


out["loop_gen"] = {"seed1": gen(load("gen_seed1")), "seed2": gen(load("gen_seed2"))}
t10 = {}
for k in ("100", "1000"):
    c = load("gen_t10_" + k)["counts"]
    t10[k] = {"right_v3": c["correct_v3"], "cap_hits": c["cap_hits"], "loops_rule_A": c["loop_A"], "tokens_per_problem": c["mean_generated_tokens"], "n": c["n"]}
bt = load("base_t10")["cells"]["base_opener_1.0"]
t10["unedited"] = {"right_v3": bt["right_v3"], "cap_hits": bt["cap_hits"], "n": bt["n"]}
out["loop_gen"]["t10"] = t10
vt = load("gen_vote")
out["loop_vote"] = {"per_sample": [{"u": p["unedited"], "e": p["edited"]} for p in vt["per_sample"]], "pooled": vt["pooled_points_edited_minus_unedited"]}
out["loop_dose"] = [{k: s[k] for k in ("name", "set", "factor", "loops", "n")} for s in load("dose")["summary"]]

# 5. The 100 neurons with the largest effect when copied from RL, and the 100 layer-matched random ones.
desc = {(u["layer"], u["neuron"]): u for u in load("descriptions")["units"]}
ns = []
for n in load("neurons")["neurons"]:
    u = desc.get((n["layer"], n["neuron"]))
    if n["set"] != "selected" and not u:
        continue
    pole = "pos" if n["pos"]["share_beyond_p97"] >= n["neg"]["share_beyond_p97"] else "neg"
    ns.append({"l": n["layer"], "n": n["neuron"], "set": n["set"], "mean_abs": n["mean_abs"],
               "on": max(n["pos"]["share_beyond_p97"], n["neg"]["share_beyond_p97"]), "pole": "+" if pole == "pos" else "-",
               "promoted": [t for t, _ in n["promoted"][:8]], "suppressed": [t for t, _ in n["suppressed"][:8]],
               "cos": [n["rl"]["cos_gate"], n["rl"]["cos_up"], n["rl"]["cos_down"]], "act_corr": n["rl"]["act_corr"],
               "desc": u and u["description"], "acc": u and u["accuracy"], "desc_pole": u and u["pole"]})
out["neurons"] = ns
dt = load("descriptions")
out["desc_test"] = {"sets": dt["sets"], "chance": dt["chance"]}
out["density"] = {k: load("density")[k] for k in ("selected", "reference", "positions")}

with open(os.path.join(HERE, "data.json"), "w") as f:
    json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
print(os.path.getsize(os.path.join(HERE, "data.json")), "bytes")
