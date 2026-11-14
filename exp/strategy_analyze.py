"""Strategy basins, step 3 (laptop, no model): strategy counts base vs RL, nulls, controls, and t-STE maps.

    python3 exp/strategy_analyze.py --judge runs/<judge-job-id> --out results/strategy_basins/<name>

Main contrast, per problem: distinct strategy groups among 16 base samples vs 16 RL samples (base with cue,
RL without, both T 1.0). Null contrasts: base samples 0-15 vs 16-31, and RL 0-15 vs 16-31; these should be
about 0. Sets lose their "NO METHOD" samples, so counts are rarefied to the smallest set size of that problem.
Groups come from the judge's pooled partition (labels shared by both models), averaged over shuffles.
Hypothesis: RL uses fewer strategies than the base. Refuted if base-minus-RL is not above the null spread.
"""
import argparse
import json
import pathlib
import random
from collections import Counter, defaultdict

import numpy as np
from scipy.optimize import minimize
from sklearn.metrics import adjusted_rand_score


def load(path):
    return [json.loads(l) for l in open(path)]


def rarefied_groups(labels, m, rng, reps=200):
    """Expected number of distinct labels in a random subset of size m."""
    if m <= 0:
        return float("nan")
    return float(np.mean([len(set(rng.sample(labels, m))) for _ in range(reps)]))


def eff_number(labels):
    c = np.array(list(Counter(labels).values()), float)
    p = c / c.sum()
    return float(np.exp(-(p * np.log(p)).sum()))


def tste(n, trips, dim=2, seed=0, reg=1e-3):
    """t-STE (van der Maaten & Weinberger 2012), alpha=1. trips: rows (a, b, c) meaning a is closer to b than to c."""
    T = np.asarray(trips)
    x0 = np.random.default_rng(seed).normal(scale=1e-2, size=n * dim)

    def f(flat):
        X = flat.reshape(n, dim)
        a, b, c = X[T[:, 0]], X[T[:, 1]], X[T[:, 2]]
        dab, dac = a - b, a - c
        kab = 1 / (1 + (dab ** 2).sum(1))
        kac = 1 / (1 + (dac ** 2).sum(1))
        p = kab / (kab + kac)
        loss = -np.log(p + 1e-12).sum() + reg * (X ** 2).sum()
        gab = (-kab * (1 - p))[:, None] * 2 * dab  # d logp / d a, through d2ab
        gac = (kac * (1 - p))[:, None] * 2 * dac
        G = np.zeros_like(X)
        np.add.at(G, T[:, 0], -(gab + gac))
        np.add.at(G, T[:, 1], gab)
        np.add.at(G, T[:, 2], gac)
        return loss, G.ravel() + 2 * reg * flat

    return minimize(f, x0, jac=True, method="L-BFGS-B", options={"maxiter": 2000}).x.reshape(n, dim)


def tste_acc(X, trips):
    T = np.asarray(trips)
    return float((((X[T[:, 0]] - X[T[:, 1]]) ** 2).sum(1) < ((X[T[:, 0]] - X[T[:, 2]]) ** 2).sum(1)).mean())


def boot_ci(v, rng, reps=5000):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    means = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(reps)]
    return [float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)), int(len(v))]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--half", type=int, default=16)
    args = ap.parse_args()
    J, out = pathlib.Path(args.judge), pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    items = {it["id"]: it for it in load(J / "summaries.jsonl")}
    parts = [p for p in load(J / "partitions.jsonl")]
    controls = load(J / "controls.jsonl")
    trips = load(J / "triplets.jsonl")
    rng, nrng = random.Random(0), np.random.default_rng(0)
    H = args.half

    # sets per problem: base A/B halves and RL A/B halves, method-bearing samples only
    sets = defaultdict(dict)
    for it in items.values():
        half = "A" if it["sample"] < H else "B"
        sets[it["idx"]].setdefault(f"{it['model']}{half}", []).append(it["id"])

    per_prob, ari = [], []
    by_prob_parts = defaultdict(list)
    for p in parts:
        if p["groups"] is not None:
            by_prob_parts[p["idx"]].append({i: g for g, grp in enumerate(p["groups"]) for i in grp["ids"]})
    for idx, maps in sorted(by_prob_parts.items()):
        S = sets[idx]
        method = {k: [i for i in v if not items[i]["no_method"]] for k, v in S.items()}
        m = min(len(method.get(k, [])) for k in ["baseA", "baseB", "rlA", "rlB"])
        m_full = min(len(method.get("baseA", []) + method.get("baseB", [])), len(method.get("rlA", []) + method.get("rlB", [])))
        row = {"idx": idx, "m": m, "m_full": m_full,
               "no_method": {k: sum(items[i]["no_method"] for i in v) for k, v in S.items()},
               "acc": {mod: float(np.mean([items[i]["correct"] for k in (f"{mod}A", f"{mod}B") for i in S.get(k, [])]))
                       for mod in ("base", "rl")}}
        g = defaultdict(list)
        for mp in maps:
            lab = {k: [mp[i] for i in v] for k, v in method.items()}
            for k in lab:
                g[k].append(rarefied_groups(lab[k], m, rng))
            g["base32"].append(rarefied_groups(lab["baseA"] + lab["baseB"], m_full, rng))
            g["rl32"].append(rarefied_groups(lab["rlA"] + lab["rlB"], m_full, rng))
            g["eff_base32"].append(eff_number(lab["baseA"] + lab["baseB"]))
            g["eff_rl32"].append(eff_number(lab["rlA"] + lab["rlB"]))
            base_g, rl_g = set(lab["baseA"] + lab["baseB"]), set(lab["rlA"] + lab["rlB"])
            rl_lab, base_lab = lab["rlA"] + lab["rlB"], lab["baseA"] + lab["baseB"]
            g["rl_share_in_rl_only"].append(np.mean([x not in base_g for x in rl_lab]))
            g["base_share_in_base_only"].append(np.mean([x not in rl_g for x in base_lab]))
            g["n_groups_total"].append(len(set(mp.values())))
            # Cov-like (Lee et al. 2606.29985 count approaches among correct samples): rarefied to the smaller set
            cb = [mp[i] for k in ("baseA", "baseB") for i in method.get(k, []) if items[i]["correct"]]
            cr = [mp[i] for k in ("rlA", "rlB") for i in method.get(k, []) if items[i]["correct"]]
            mc = min(len(cb), len(cr))
            g["cov_correct_base"].append(rarefied_groups(cb, mc, rng) if mc >= 2 else float("nan"))
            g["cov_correct_rl"].append(rarefied_groups(cr, mc, rng) if mc >= 2 else float("nan"))
            # sharpening vs new: share of RL's correct samples whose group holds no base sample (base k=32)
            g["rl_correct_in_rl_only"].append(np.mean([x not in base_g for x in cr]) if cr else float("nan"))
            g["base_correct_in_base_only"].append(np.mean([x not in rl_g for x in cb]) if cb else float("nan"))
        row.update({k: float(np.mean(v)) for k, v in g.items()})
        per_prob.append(row)
        common = sorted(set.intersection(*[set(mp) for mp in maps]))
        for a in range(len(maps)):
            for b in range(a + 1, len(maps)):
                ari.append(adjusted_rand_score([maps[a][i] for i in common], [maps[b][i] for i in common]))

    def diff(a, b):
        return [r[a] - r[b] for r in per_prob]

    summary = {
        "n_problems": len(per_prob),
        "n_items": len(items),
        "no_method_share": {mod: float(np.mean([it["no_method"] for it in items.values() if it["model"] == mod]))
                            for mod in ("base", "rl")},
        "acc_boxed_exact": {mod: float(np.mean([it["correct"] for it in items.values() if it["model"] == mod]))
                            for mod in ("base", "rl")},
        "groups_16": {k: boot_ci([r[k] for r in per_prob], nrng) for k in ["baseA", "baseB", "rlA", "rlB"]},
        "main_baseA_minus_rlA": boot_ci(diff("baseA", "rlA"), nrng),
        "null_baseA_minus_baseB": boot_ci(diff("baseA", "baseB"), nrng),
        "null_rlA_minus_rlB": boot_ci(diff("rlA", "rlB"), nrng),
        "groups_32": {k: boot_ci([r[k] for r in per_prob], nrng) for k in ["base32", "rl32"]},
        "eff_number_32": {k: boot_ci([r[k] for r in per_prob], nrng) for k in ["eff_base32", "eff_rl32"]},
        "rl_share_in_rl_only_groups": boot_ci([r["rl_share_in_rl_only"] for r in per_prob], nrng),
        "base_share_in_base_only_groups": boot_ci([r["base_share_in_base_only"] for r in per_prob], nrng),
        "cov_correct": {k: boot_ci([r[k] for r in per_prob], nrng) for k in ["cov_correct_base", "cov_correct_rl"]},
        "rl_correct_in_rl_only_groups": boot_ci([r["rl_correct_in_rl_only"] for r in per_prob], nrng),
        "base_correct_in_base_only_groups": boot_ci([r["base_correct_in_base_only"] for r in per_prob], nrng),
        "partition_failures": sum(p["groups"] is None for p in parts),
        "shuffle_ari": boot_ci(ari, nrng) if ari else None,
        "controls": {k: f"{sum(bool(c.get('pass')) for c in controls if c['kind'] == k)}/{sum(c['kind'] == k for c in controls)}"
                     for k in ("dup", "mix")},
        "ci_note": "[mean, 2.5%, 97.5%, n] bootstrap over problems",
    }

    # t-STE maps, per problem: held-out accuracy vs a shuffled-id null
    tby = defaultdict(list)
    for t in trips:
        if t["consistent"]:
            loser = t["c"] if t["pick1"] == t["b"] else t["b"]
            tby[t["idx"]].append((t["a"], t["pick1"], loser))
    maps_out, accs, null_accs = {}, [], []
    for idx, tt in sorted(tby.items()):
        ids = sorted({i for t in tt for i in t})
        pos = {i: k for k, i in enumerate(ids)}
        T = [(pos[a], pos[b], pos[c]) for a, b, c in tt]
        random.Random(idx).shuffle(T)
        cut = int(0.9 * len(T))
        X = tste(len(ids), T[:cut])
        accs.append(tste_acc(X, T[cut:]))
        perm = list(range(len(ids)))
        random.Random(idx + 1).shuffle(perm)
        Tn = [(a, b, c) for a, b, c in T[:cut]] + [(perm[a], perm[b], perm[c]) for a, b, c in T[cut:]]
        null_accs.append(tste_acc(X, Tn[cut:]))
        Xall = tste(len(ids), T)
        grp0 = by_prob_parts[idx][0] if by_prob_parts.get(idx) else {}
        maps_out[idx] = [{"id": i, "x": float(Xall[k, 0]), "y": float(Xall[k, 1]), "model": items[i]["model"],
                          "sample": items[i]["sample"], "correct": items[i]["correct"], "group": grp0.get(i),
                          "summary": items[i]["summary"]} for i, k in pos.items()]
    summary["tste_heldout_acc"] = boot_ci(accs, nrng) if accs else None
    summary["tste_shuffled_id_null_acc"] = boot_ci(null_accs, nrng) if null_accs else None
    summary["triplet_consistency"] = float(np.mean([t["consistent"] for t in trips])) if trips else None

    group_names = {p["idx"]: [g["name"] for g in p["groups"]] for p in parts if p["shuffle"] == 0 and p["groups"]}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    (out / "per_problem.json").write_text(json.dumps(per_prob, indent=1))
    (out / "maps.json").write_text(json.dumps({"maps": maps_out, "group_names": group_names}))
    print(json.dumps(summary, indent=1))
