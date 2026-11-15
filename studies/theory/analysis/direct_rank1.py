"""Direct test of round-10/weights-m06, direction 1 against directions 2-8 (specs/SPEC_direct_rank1.md).

    uv run --no-project --with numpy python studies/theory/analysis/direct_rank1.py

On hard328 problems where a cued-base sample finished wrong, compare the right rate of the rank-1 edit (TOP1, direction 1
per matrix of the RL-Math 3.1 delta, 1x) and of the directions-2-8 edit at 1.5x (D28) against a second base sample on
another seed. Selectors: base samples 2 and 3 (no edit uses their seeds), pooled; bootstrap by problem.
Needs the raw answers of the jobs in RUNS under runs/ (uv run tools/gpu.py get <job id>).
Writes studies/theory/results/direct/rank1-01/.
"""
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "studies" / "rlneurons" / "results"
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "rank1-01"
BASE4 = RES / "day1_3" / "hard328_base_cue_s4r2-01" / "rows.jsonl"
D28_ROWS = RES / "xreward" / "depth3" / "top8x1.5_d2-8_math31_s1-01" / "rows.jsonl"
D28_JOBS = ("abaybektursun-1115-122847-824c", "abaybektursun-1115-122859-b197")
RUNS = {  # name: (job id, posted right, posted cap hits)
    "t10": ("abaybektursun-1114-151534-e72c", 164, 77),
    "top1": ("abaybektursun-1115-000358-d11a", 181, 51),
    "top1x2": ("abaybektursun-1115-105247-1603", 184, 23),
    "top8x1.5": ("abaybektursun-1115-031229-5991", 203, 25),
    "rand8": ("abaybektursun-1114-221040-5f1e", 158, 67),
    "rand8x1.5": ("abaybektursun-1115-090241-0229", 159, 74),
}
BASE_POSTED = {0: (161, 71), 1: (161, 66), 2: (152, 81), 3: (160, 68)}  # attempt 0 of the day1_3 base cell
EDITS = ("top1", "d28", "top8x1.5", "rand8", "rand8x1.5", "top1x2")
B = 10000


def rows_by_problem(rows):
    out = {}
    for r in rows:
        assert r["problem_index"] not in out
        out[r["problem_index"]] = r
    assert len(out) == 328
    return out


def load_all():
    draws = {}
    base = [json.loads(line) for line in open(BASE4)]
    for s in range(4):
        draws[f"b{s}"] = rows_by_problem([r for r in base if r["attempt"] == 0 and r["sample"] == s])
    for name, (job, _, _) in RUNS.items():
        draws[name] = rows_by_problem([json.loads(line) for line in open(ROOT / "runs" / job / "answers.jsonl")])
    d28 = rows_by_problem([json.loads(line) for line in open(D28_ROWS)])
    text = {}
    for job in D28_JOBS:
        for line in open(ROOT / "runs" / job / "answers.jsonl"):
            r = json.loads(line)
            text[r["problem_index"]] = r
    assert set(text) == set(d28) and all(text[p]["score_v3"] == d28[p]["score_v3"] for p in d28)
    draws["d28"] = text
    posted = {f"b{s}": v for s, v in BASE_POSTED.items()} | {k: v[1:] for k, v in RUNS.items()} | {"d28": (183, 69)}
    for name, (right, cap) in posted.items():
        got = (sum(r["score_v3"] for r in draws[name].values()), sum(r["cap_hit"] for r in draws[name].values()))
        assert got == (right, cap), (name, got, right, cap)
    return draws


def arrays(draws):
    probs = sorted(draws["b0"])
    a = {}
    for name, rows in draws.items():
        assert sorted(rows) == probs
        rr = [rows[p] for p in probs]
        cap = np.array([r["cap_hit"] for r in rr])
        v3 = np.array([r["score_v3"] for r in rr], float)
        a[name] = {
            "cap": cap,
            "v3": v3,
            "strict": v3 * ~cap,
            "finished": ~cap & np.array([bool((r["extracted_v3"] or "").strip()) for r in rr]),
            "seed": {r["seed"] - r["problem_index"] for r in rr},
        }
        assert len(a[name]["seed"]) == 1, name
        a[name]["seed"] = a[name]["seed"].pop()
    return probs, a


def pairs(a, selectors, pool, key):
    """Per problem: list of (selector, second-base mean) for problems the selector finished wrong."""
    out = {}
    for k in selectors:
        second = [j for j in pool if j != k and a[j]["seed"] != a[k]["seed"]]
        fw = a[k]["finished"] & (a[k]["v3"] == 0)
        b = np.mean([a[j][key] for j in second], axis=0)
        for i in np.flatnonzero(fw):
            out.setdefault(i, []).append((k, b[i]))
    return out


def excess(a, pr, key, idx, override=None):
    """E (points) for each edit, on the full set and on each bootstrap resample idx (B x n_problems)."""
    n = len(a["b0"]["v3"])
    cnt, bsum = np.zeros(n), np.zeros(n)
    for i, lst in pr.items():
        cnt[i] = len(lst)
        bsum[i] = sum(b for _, b in lst)
    res = {}
    for e in EDITS + tuple(override or ()):
        tsum = override[e] if override and e in override else a[e][key] * cnt  # override: per-problem sums over pairs
        d = tsum - bsum
        point = 100 * d.sum() / cnt.sum()
        boot = 100 * d[idx].sum(1) / cnt[idx].sum(1)
        res[e] = (point, boot, 100 * tsum.sum() / cnt.sum())
    res["_base2_rate"] = 100 * bsum.sum() / cnt.sum()
    res["_n_pairs"] = int(cnt.sum())
    res["_n_problems"] = int((cnt > 0).sum())
    return res


def ci(boot, level):
    lo = (1 - level) / 2
    return [float(np.quantile(boot, lo)), float(np.quantile(boot, 1 - lo))]


def summary(res, a, pr):
    out = {"n_pairs": res["_n_pairs"], "n_problems": res["_n_problems"], "base2_right_pct": res["_base2_rate"]}
    for e in EDITS:
        point, boot, rate = res[e]
        caps = [a[e]["cap"][i] for i, lst in pr.items() for _ in lst]
        out[e] = {"right_pct": rate, "cap_pct": 100 * float(np.mean(caps)), "E_pts": float(point),
                  "E_ci95": ci(boot, 0.95), "E_ci90": ci(boot, 0.90),
                  "shares_selector_seed": False}
    g = res["d28"][1] - res["top1"][1]
    out["G_pts"] = float(res["d28"][0] - res["top1"][0])
    out["G_ci95"], out["G_ci90"] = ci(g, 0.95), ci(g, 0.90)
    return out


def verdict(s):
    if s["top1"]["E_ci95"][0] >= 5.0:
        return "refuted (E_top1 95 % lower bound >= +5.0)"
    if s["G_ci95"][1] <= 0.0:
        return "refuted (G 95 % upper bound <= 0.0)"
    if s["top1"]["E_pts"] < 0.5 * s["d28"]["E_pts"]:
        return "holds"
    return "undecided (E_top1 point not below half of E_d28 point)"


def main():
    draws = load_all()
    probs, a = arrays(draws)
    rng = np.random.default_rng(seed=0)
    idx = rng.integers(0, len(probs), size=(B, len(probs)))
    pool4 = ["b0", "b1", "b2", "b3"]

    # primary: selectors b2, b3 (seeds 3020000, 3030000, used by no edit)
    edit_seeds = {e: a[e]["seed"] for e in EDITS}
    assert a["b2"]["seed"] not in edit_seeds.values() and a["b3"]["seed"] not in edit_seeds.values(), edit_seeds
    pr = pairs(a, ["b2", "b3"], pool4, "strict")
    prim = summary(excess(a, pr, "strict", idx), a, pr)
    prim["verdict"] = verdict(prim)
    pr_v3 = pairs(a, ["b2", "b3"], pool4, "v3")
    v3 = summary(excess(a, pr_v3, "v3", idx), a, pr_v3)

    # planted checks on the primary pairs
    n = len(probs)
    cnt = np.zeros(n)
    bsum = np.zeros(n)
    for i, lst in pr.items():
        cnt[i], bsum[i] = len(lst), sum(b for _, b in lst)
    planted = excess(a, pr, "strict", idx, override={"copy_base2": bsum, "all_right": cnt})
    planted = {k: {"E_pts": float(planted[k][0]), "E_ci95": ci(planted[k][1], 0.95)} for k in ("copy_base2", "all_right")}
    assert abs(planted["copy_base2"]["E_pts"]) < 1e-9

    # secondary: the plan's selector (day1 t10, seed 3000000), second base = day1_3 samples on other seeds
    pr_t10 = pairs(a, ["t10"], pool4 + ["t10"], "strict")
    t10 = summary(excess(a, pr_t10, "strict", idx), a, pr_t10)
    for e in EDITS:
        t10[e]["shares_selector_seed"] = a[e]["seed"] == a["t10"]["seed"]
    t10["verdict_if_used"] = verdict(t10)

    # robustness: every base draw as selector, pool of all five base draws
    robust = {}
    for k in ["t10"] + pool4:
        p = pairs(a, [k], pool4 + ["t10"], "strict")
        s = summary(excess(a, p, "strict", idx), a, p)
        robust[k] = {"seed": int(a[k]["seed"]), "n_pairs": s["n_pairs"], "base2_right_pct": s["base2_right_pct"],
                     "G_pts": s["G_pts"], "G_ci95": s["G_ci95"]}
        for e in EDITS:
            robust[k][e] = {"E_pts": s[e]["E_pts"], "E_ci95": s[e]["E_ci95"],
                            "shares_selector_seed": bool(a[e]["seed"] == a[k]["seed"])}

    context = {}
    for name in ["t10"] + pool4 + list(EDITS):
        fin = ~a[name]["cap"]
        context[name] = {"right": int(a[name]["v3"].sum()), "cap_hits": int(a[name]["cap"].sum()),
                         "right_per_finished": float(a[name]["strict"].sum() / fin.sum()),
                         "finished_no_boxed": int(sum(1 for p in probs if not draws[name][p]["cap_hit"]
                                                      and "\\boxed" not in draws[name][p]["text"]))
                         if "text" in draws[name][probs[0]] else None}

    readout = {
        "spec": "studies/theory/specs/SPEC_direct_rank1.md",
        "set": "hard328, cue, T 1.0 / top-p 1.0, cap 16,384, grader v3; right = score_v3 1 and no cap hit",
        "primary": {"selectors": "day1_3 base samples 2 and 3 (seeds 3020000, 3030000), pooled", **prim},
        "primary_stored_v3": v3,
        "planted": planted,
        "plan_selector_t10": t10,
        "robustness_each_selector": robust,
        "context_all_328": context,
        "bootstrap": f"{B} resamples of the 328 problems (cluster: all pairs of a problem), numpy default_rng(seed=0), percentile",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "readout.json").write_text(json.dumps(readout, indent=1) + "\n")

    # examples: on primary pairs, one supporting (TOP1 wrong, D28 right) and one against (TOP1 right, D28 wrong)
    def ex(i, k):
        p = probs[i]
        item = {"problem_index": p, "selector": k, "gold": draws["b0"][p]["gold"],
                "prompt": draws["top1"][p]["prompt"], "second_base_right_mean": float(dict(pr[i])[k])}
        for name in (k, "top1", "d28"):
            r = draws[name][p]
            item[name] = {"seed": r["seed"], "n_new": r["n_new"], "cap_hit": r["cap_hit"],
                          "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"],
                          "text_tail": r["text"][-600:] if "text" in r else None}
        return item

    flat = [(i, k) for i, lst in sorted(pr.items()) for k, _ in lst]
    sup = next((i, k) for i, k in flat if a["top1"]["strict"][i] == 0 and a["d28"]["strict"][i] == 1)
    against = next((i, k) for i, k in flat if a["top1"]["strict"][i] == 1 and a["d28"]["strict"][i] == 0)
    (OUT / "examples.json").write_text(json.dumps({"supports": ex(*sup), "against": ex(*against)}, indent=1) + "\n")
    print(json.dumps({k: readout["primary"][k] for k in ("n_pairs", "n_problems", "base2_right_pct", "G_pts", "G_ci95", "verdict")}, indent=1))
    for e in EDITS:
        print(e, {k: prim[e][k] for k in ("right_pct", "cap_pct", "E_pts", "E_ci95")})


if __name__ == "__main__":
    main()
