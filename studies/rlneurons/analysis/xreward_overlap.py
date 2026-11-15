"""xreward Part 1 readout (specs/SPEC_xreward.md): the pairwise tables of jobs/xreward_overlap.py and the numbers of X1 to X3.

    python3 -m studies.rlneurons.analysis.xreward_overlap --run runs/<job id> --out studies/rlneurons/results/xreward/overlap-01

Reads metrics.json (one row per layer matrix). Writes readout.json: per statistic the key-by-key table of means over the 224 layer
matrices, the same by module type, the nearest neighbour of every RL model, and X1 to X3. Copies run.json. No verdict is computed
from a threshold that the spec does not state.
"""
import argparse
import json
import pathlib
import shutil

RL = ("math31", "code31", "math30", "code30", "if30", "general30", "mix30")
CUE_SCORE = {"code31": 450, "math30": 448, "mix30": 440, "general30": 429, "code30": 411, "if30": 377}     # MATH-500, cue, of 500: result-edceef, result-4b0d5f
SYM = ("cos", "overlap_left", "overlap_right")
CAP = ("cap_left", "cap_right", "cap_both")


def mean(xs):
    return sum(xs) / len(xs)


def table(rows, keys, stat):
    """{a: {b: mean over the rows that hold the pair}}; for a cap statistic the entry [a][b] is a's share inside b's subspace"""
    out = {}
    for a in keys:
        out[a] = {}
        for b in keys:
            if a == b:
                continue
            ks = [f"{a}>{b}"] if stat in CAP else [f"{a}|{b}", f"{b}|{a}"]
            vals = [r["pair"][k][stat] for r in rows for k in ks if k in r["pair"]]
            assert len(vals) == len(rows), f"{stat} {a} {b}: {len(vals)} values in {len(rows)} rows"
            out[a][b] = mean(vals)
    return out


def spearman(x, y):
    rank = lambda v: {k: i for i, k in enumerate(sorted(v, key=v.get))}
    rx, ry, n = rank(x), rank(y), len(x)
    return 1 - 6 * sum((rx[k] - ry[k]) ** 2 for k in x) / (n * (n * n - 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run, out = pathlib.Path(a.run), pathlib.Path(a.out)
    m = json.loads((run / "metrics.json").read_text())
    rows, keys = m["rows"], m["keys"]
    assert m["n_done"] == m["n"] == len(rows) == 224, (m["n_done"], m["n"], len(rows))
    assert all(r["key"][k]["norm"] > 0 for r in rows for k in keys), "a zero difference: its pairs are missing"
    tabs = {s: table(rows, keys, s) for s in SYM + CAP}
    mods = list(dict.fromkeys(r["module"] for r in rows))
    by_mod = {mod: {s: table([r for r in rows if r["module"] == mod], keys, s) for s in ("overlap_left", "overlap_right")} for mod in mods}
    rl_pairs = [(x, y) for i, x in enumerate(RL) for y in RL[i + 1:]]
    x = {}
    for side in ("overlap_left", "overlap_right"):
        t = tabs[side]
        x[side] = {"X1": {"mean_rl_rl": mean([t[p][q] for p, q in rl_pairs]), "mean_rl_think_sft": mean([t[p]["think_sft"] for p in RL]),
                          "n_rl_pairs_above_both_their_sft_overlaps": sum(t[p][q] > max(t[p]["think_sft"], t[q]["think_sft"]) for p, q in rl_pairs),
                          "n_rl_pairs": len(rl_pairs)},
                   "X2": {"mean_rl_rl": mean([t[p][q] for p, q in rl_pairs]), "mean_rl_base_w": mean([t[p]["base_w"] for p in RL])},
                   "X3": {"overlap_with_math31": {k: t["math31"][k] for k in CUE_SCORE}, "cue_score_of_500": CUE_SCORE,
                          "spearman": spearman({k: t["math31"][k] for k in CUE_SCORE}, CUE_SCORE), "n": len(CUE_SCORE)},
                   "nearest_rl_model": {p: max((t[p][q], q) for q in RL if q != p)[1] for p in RL},
                   "random_subspace": {"4096": m["k"] / 4096}}
    steps = [k for k in keys if k.endswith("_s100")]
    if steps:                                                                       # amendment 2: S1, S2 on the input side
        t, group = tabs["overlap_right"], lambda k: "reason" if k.startswith(("math", "code")) else "instr" if k.startswith(("if", "general")) else "mix"
        near = {k: max((t[k][q], q) for q in RL if q != k[:-5])[1] for k in steps}
        cross = lambda ks: mean([t[p][q] for i, p in enumerate(ks) for q in ks[i + 1:] if {group(p), group(q)} == {"reason", "instr"}])
        x["steps"] = {"S1_nearest_final_of_another_run": near, "S1_overlap_with_own_final": {k: t[k][k[:-5]] for k in steps},
                      "S2_mean_cross_group_overlap": {"step100": cross(steps), "final": cross(list(RL))}}
    norm_base = sum(r["key"]["base_w"]["norm"] ** 2 for r in rows) ** 0.5
    per_key = {k: {"rel_norm": sum(r["key"][k]["norm"] ** 2 for r in rows) ** 0.5 / norm_base, "mean_top8_share": mean([r["key"][k]["top8_share"] for r in rows])} for k in keys}
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(run / "run.json", out / "run.json")
    (out / "readout.json").write_text(json.dumps({"source": str(run / "metrics.json"), "n_matrices": len(rows), "k": m["k"], "keys": keys, "per_key": per_key,
                                                   "tables": tabs, "by_module": by_mod, "hypotheses": x}, indent=1) + "\n")
    for side in ("overlap_left", "overlap_right"):
        print(side)
        print(" " * 10 + " ".join(f"{k[:9]:>9}" for k in keys))
        for p in keys:
            print(f"{p:>10} " + " ".join("       --" if p == q else f"{tabs[side][p][q]:9.3f}" for q in keys))
        print(json.dumps(x[side], indent=1))
    print(json.dumps(x.get("steps"), indent=1))


if __name__ == "__main__":
    main()
