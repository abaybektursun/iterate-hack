"""Readout of jobs/workspace_tests.py (specs/SPEC2_workspace.md): reads readout.json, swap.json and twins.json of a run folder
and writes metrics.json to the result folder.

    PYTHONPATH=. python3 -m studies.jspace.analysis.workspace_analyze runs/<job-id> <result folder>

Needs numpy only. Intervals are 95 % percentile intervals of a bootstrap over items (2,000 resamples). pass@k: mean over items
of the share of intermediates whose minimum rank over the layers is <= k. Fail loud: no try/except.
"""
import json
import pathlib
import sys

import numpy as np

RNG = np.random.default_rng(0)
B = 2000
NAMES = ("base", "rl")
ALPHAS = ("0.5", "1.0", "2.0", "4.0")


def boot(v):
    v = np.asarray(v, dtype=np.float64)
    if len(v) == 0:
        return {"n": 0}
    d = v[RNG.integers(0, len(v), size=(B, len(v)))].mean(1)
    return {"n": int(len(v)), "mean": float(v.mean()), "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}


def item_pass(row, model, variant, k, null=False):
    """Share of the item's intermediates (or of its null ones) with a minimum rank over layers <= k; None if none is scoreable."""
    n = len(row["intermediates"])
    ranks = row["ranks"][model][variant][n:] if null else row["ranks"][model][variant][:n]
    hits = [min(r) <= k for r in ranks if r[0] is not None]
    return float(np.mean(hits)) if hits else None


def main():
    run, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    jm = json.loads((run / "metrics.json").read_text())
    assert jm["status"] == "done"
    variants, layers = jm["variants"], jm["layers"]
    res = {"job_id": jm["job_id"], "commit": jm["commit"], "layers": layers, "variants": variants, "lens": jm["lens"]}

    # ------------------------------------------------------------ readout sets
    res["readout"] = {}
    for s, rows in json.loads((run / "readout.json").read_text()).items():
        graded = rows[0]["correct"]["base"] is not None
        ok = {m: [bool(r["correct"][m]) if graded else True for r in rows] for m in NAMES}
        both = [a and b for a, b in zip(ok["base"], ok["rl"])]
        e = {"items": len(rows), "graded": graded, "correct": {m: int(sum(ok[m])) for m in NAMES}, "both_correct": int(sum(both))}
        for v in variants:
            ev = {}
            for m in NAMES:
                own = [(item_pass(r, m, v, 10), item_pass(r, m, v, 1), item_pass(r, m, v, 10, null=True)) for r, o in zip(rows, ok[m]) if o]
                own = [x for x in own if x[0] is not None and x[2] is not None]
                ev[m] = {"pass10": boot([x[0] for x in own]), "pass1": boot([x[1] for x in own]), "null_pass10": boot([x[2] for x in own]),
                         "pass10_minus_null": boot([x[0] - x[2] for x in own])}
                ev[m]["pass10_by_layer"] = [float(np.mean([np.mean([rk[li] <= 10 for rk in r["ranks"][m][v][:len(r["intermediates"])] if rk[0] is not None] or [0])
                                                           for r, o in zip(rows, ok[m]) if o] or [0])) for li in range(len(layers))]
            shared = [(item_pass(r, "rl", v, 10), item_pass(r, "base", v, 10)) for r, o in zip(rows, both) if o]
            shared = [x for x in shared if None not in x]
            ev["rl_minus_base_pass10_shared"] = boot([x[0] - x[1] for x in shared])
            ev["shared_pass10"] = {"base": boot([x[1] for x in shared]), "rl": boot([x[0] for x in shared])}
            e[v] = ev
        res["readout"][s] = e

    # ------------------------------------------------------------ swap
    res["swap"] = {}
    rows = json.loads((run / "swap.json").read_text())
    for s in sorted({r["set"] for r in rows}):
        e = {"items": sum(r["set"] == s for r in rows)}
        for m in NAMES:
            el = [r["models"][m] for r in rows if r["set"] == s and r["models"][m]["eligible"]]
            em = {"eligible": len(el)}
            for v in variants:
                rate = {al: {arm: [float(x["arms"][f"{v}|{arm}|{al}"]["is_swap_answer"]) for x in el] for arm in ("swap", "null")} for al in ALPHAS}
                best = max(ALPHAS, key=lambda al: sum(rate[al]["swap"])) if el else ALPHAS[0]
                em[v] = {"best_alpha": float(best), "flip": boot(rate[best]["swap"]), "null_flip": boot(rate[best]["null"]),
                         "flip_minus_null": boot([x - y for x, y in zip(rate[best]["swap"], rate[best]["null"])]),
                         "still_clean_answer": boot([float(x["arms"][f"{v}|swap|{best}"]["is_answer"]) for x in el]),
                         "flip_by_alpha": {al: (float(np.mean(rate[al]["swap"])) if el else None) for al in ALPHAS}}
            e[m] = em
        res["swap"][s] = e

    # ------------------------------------------------------------ twins
    rows = json.loads((run / "twins.json").read_text())
    tw = {"twins": len(rows), "tokens_after": sorted({"".join(r["tokens_after"]) for r in rows})}
    gap = lambda r, m, f: f(r["models"][m]["error"]) - f(r["models"][m]["correct"])
    for name, f in (("output_hold", lambda x: x["output_hold_lp"][-1]), ("output_neutral", lambda x: x["output_neutral_lp"][-1])):
        tw[name] = {m: boot([gap(r, m, f) for r in rows]) for m in NAMES}
        tw[name]["rl_minus_base"] = boot([gap(r, "rl", f) - gap(r, "base", f) for r in rows])
    tw["output_right_logprob_before_result"] = {m: boot([r["models"][m]["correct"]["output_right_lp_before"] for r in rows]) for m in NAMES}
    tw["output_top_after_error"] = {m: {t: int(c) for t, c in zip(*np.unique([r["models"][m]["error"]["output_top"][-1] for r in rows], return_counts=True))}
                                    for m in NAMES}
    tw["output_top_after_error"] = {m: dict(sorted(d.items(), key=lambda kv: -kv[1])[:8]) for m, d in tw["output_top_after_error"].items()}
    tw["lens"] = {}
    for v in variants:
        ev = {}
        for li, l in enumerate(layers):
            el = {}
            for fam in ("hold_lp", "neutral_lp"):
                f = lambda x, fam=fam, li=li: x["lens"][v][fam][li][-1]
                el[fam] = {m: boot([gap(r, m, f) for r in rows]) for m in NAMES}
                el[fam]["rl_minus_base"] = boot([gap(r, "rl", f) - gap(r, "base", f) for r in rows])
            # the right result while reading the wrong one: rank at the wrong number's position, error version
            el["right_in_top10_at_wrong_number"] = {m: boot([float(r["models"][m]["error"]["lens"][v]["right_rank"][li][0] <= 10) for r in rows])
                                                    for m in NAMES}
            ev[f"L{l}"] = el
        tw["lens"][v] = ev
    res["twins"] = tw
    (out / "metrics.json").write_text(json.dumps(res, indent=1))

    for s, e in res["readout"].items():
        for v in variants:
            print(f"readout {s:12} {v:6} " + "  ".join(f"{m} pass@10 {e[v][m]['pass10'].get('mean', float('nan')):.3f} (null {e[v][m]['null_pass10'].get('mean', float('nan')):.3f}, n {e[v][m]['pass10']['n']})" for m in NAMES))
    for s, e in res["swap"].items():
        for m in NAMES:
            print(f"swap {s:10} {m:4} eligible {e[m]['eligible']:3d} " + "  ".join(f"{v} flip {e[m][v]['flip'].get('mean', float('nan')):.2f} null {e[m][v]['null_flip'].get('mean', float('nan')):.2f}" for v in variants))
    print("twins output hold gap", {m: round(tw["output_hold"][m]["mean"], 3) for m in NAMES}, "rl-base", tw["output_hold"]["rl_minus_base"])


if __name__ == "__main__":
    main()
