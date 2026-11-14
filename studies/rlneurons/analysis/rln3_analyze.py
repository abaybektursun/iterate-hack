"""RLN-3 readout and verdict (studies/rlneurons/SPEC3.md §6-§8), on banked JSON only.

    python -m studies.rlneurons.analysis.rln3_analyze --banks <dir with one subdir per model> --inputs studies/rlneurons/data/rln3 --out <json>

Per model subdir: P_<set>.jsonl, F_<set>.jsonl, CP_<set>.jsonl, CF_<set>.jsonl, metrics.json, check.json (base and s2800).
Cells: P, F, P+C, F+C. Samples used per set: the largest k such that samples 0..k-1 are complete in every model (SPEC3 §6).
Fail loud: no try/except, no fallback.
"""
import argparse
import json
import pathlib

import numpy as np

from studies.rlneurons.lib import n13_score as S

MODELS = ("base", "s0100", "s0400", "s2800", "fr")
BENCHES = ("math500", "hard")
CELLS = ("P", "F", "P+C", "F+C")
MATCH_HI = 6.0          # SPEC3 §7: "matches" needs the interval's upper end at or below 6 points
CAP_DROP = 5.0          # (c): cap-hit share of P falls by at least 5 points, base to step 2,800, harder set
C_GAIN_POINT, C_GAIN_HI = 2.0, 5.0


def jl(p):
    return [json.loads(l) for l in open(p)] if p.exists() else []


def load(banks: pathlib.Path, models, probs):
    d = {}
    for m in models:
        md = banks / m
        for b in BENCHES:
            for c in ("P", "F", "CP", "CF"):
                recs = jl(md / f"{c}_{b}.jsonl")
                byk = {}
                for r in recs:
                    k = (r["sample"], r["problem_index"])
                    assert k not in byk, f"{m} {c} {b}: duplicate record {k}"
                    assert r["unique_id"] == probs[b][r["problem_index"]]["unique_id"]
                    byk[k] = r
                d[(m, b, c)] = byk
    return d


def complete(d, m, b, n, s):
    for c in ("P", "F"):
        for i in range(n):
            r = d[(m, b, c)].get((s, i))
            if r is None:
                return False
            if not r["finished_by_N"] and (s, i) not in d[(m, b, "C" + c)]:
                return False
    return True


def n_complete(d, m, b, n):
    s = 0
    while complete(d, m, b, n, s):
        s += 1
    return s


def cell_arrays(d, fz, m, b, cell, n, k):
    """score, finished, cap, tokens, class: arrays [n, k]."""
    base = "P" if cell.startswith("P") else "F"
    sc, fin, cap, tk = (np.zeros((n, k)) for _ in range(4))
    cl = np.empty((n, k), dtype=object)
    commit_len = len(fz["commit_ids"])
    for i in range(n):
        for s in range(k):
            r = d[(m, b, base)][(s, i)]
            small = r["n_new"] < fz["non_attempt_max_tokens"]
            if "+C" not in cell or r["finished_by_N"]:
                sc[i, s], fin[i, s], cap[i, s], tk[i, s] = r["score"], not r["cap_hit"], r["cap_hit"], r["n_generated"]
                if r["score"] == 1:
                    cl[i, s] = "right"
                elif r["cap_hit"]:
                    cl[i, s] = "cap_hit_loop" if r["loop_ratio"] < fz["loop"]["below"] else "cap_hit_no_loop"
                elif small:
                    cl[i, s] = "non_attempt"
                else:
                    cl[i, s] = "finished_wrong_no_answer" if r["extracted"] is None else "finished_wrong"
            else:
                c = d[(m, b, "C" + base)][(s, i)]
                sc[i, s], fin[i, s], cap[i, s], tk[i, s] = c["score"], c["closed"], 0, fz["N"] + commit_len + c["n_generated"]
                cl[i, s] = "right" if c["score"] == 1 else ("commit_wrong" if c["closed"] else "commit_not_closed")
    return {"score": sc, "fin": fin.astype(bool), "cap": cap.astype(bool), "tok": tk, "cls": cl}


def boot(x, y, mask=None):
    """Paired difference in points, x - y, per-problem means over samples (over masked pairs when mask is given); bootstrap over
    problems (n13_score.paired_bootstrap: 2,000 resamples, seed 0, percentile 95 %)."""
    if mask is None:
        mask = np.ones_like(x, dtype=bool)
    keep = mask.any(1)
    xm = np.array([x[i][mask[i]].mean() for i in np.flatnonzero(keep)])
    ym = np.array([y[i][mask[i]].mean() for i in np.flatnonzero(keep)])
    if xm.size == 0:
        return {"n_problems": 0, "diff": None, "ci95": [None, None]}
    lo, hi = S.paired_bootstrap(xm, ym)
    return {"n_problems": int(xm.size), "n_pairs": int(mask.sum()), "diff": float(100 * (xm.mean() - ym.mean())), "ci95": [lo, hi]}


def label(cmp):
    lo, hi = cmp["ci95"]
    if lo is None:
        return "NO DATA"
    if lo > 0:
        return "FALLS SHORT"
    if hi < 0:
        return "EXCEEDS"
    return "MATCHES" if hi <= MATCH_HI else "UNDECIDED (interval too wide)"


def readout(a, fz):
    out = {"n": int(a["score"].shape[0]), "samples": int(a["score"].shape[1]), "acc": float(100 * a["score"].mean()),
           "cap_hit_share": float(a["cap"].mean()), "finished_share": float(a["fin"].mean()), "mean_tokens": float(a["tok"].mean())}
    cls = a["cls"].ravel()
    out["classes"] = {c: int((cls == c).sum()) for c in sorted(set(cls))}
    return out


def quotes(d, m, b, cell, probs):
    """One right and one wrong sample-0 instance; for a +C cell a committed (cut) answer when one exists."""
    base = "P" if cell.startswith("P") else "F"
    out = {}
    for want in (1, 0):
        for committed in ((True, False) if "+C" in cell else (False,)):
            for i in range(len(probs[b])):
                r = d[(m, b, base)][(0, i)]
                if committed != (not r["finished_by_N"]):
                    continue
                if committed:
                    c = d[(m, b, "C" + base)][(0, i)]
                    if c["score"] != want:
                        continue
                    q = {"cut_tail": c["cut_tail"][-300:], "continuation": c["continuation"], "extracted": c["extracted"],
                         "closed": c["closed"]}
                else:
                    if r["score"] != want:
                        continue
                    q = {"text_head": r["text"][:300], "text_tail": r["text"][-300:], "extracted": r["extracted"], "mode": r["mode"],
                         "answer_prob": r.get("answer_prob"), "cap_hit": r["cap_hit"], "n_new": r["n_new"]}
                out["right" if want else "wrong"] = {"problem_index": i, "committed": committed, "problem": probs[b][i]["problem"][:400],
                                                     "gold": probs[b][i]["answer"], **q}
                break
            if ("right" if want else "wrong") in out:
                break
    return out


def verdict(banks, inputs, models=MODELS):
    fz = json.loads((inputs / "frozen.json").read_text())
    probs = {b: json.loads((inputs / f"{b}.json").read_text()) for b in BENCHES}
    d = load(banks, models, probs)
    gates = {}
    for m, key in (("base", "base"), ("s2800", "s2800")):
        p = banks / m / "check.json"
        chk = json.loads(p.read_text()) if p.exists() else None
        gates[f"G-CHECK {m}"] = {"pass": bool(chk and chk["pass"]), "value": chk and chk["acc"], "interval": fz["check"][key]["wilson95"]}
    k = {b: min(n_complete(d, m, b, len(probs[b])) for m in models) for b in BENCHES}
    gates["G-COMPLETE"] = {"pass": all(v >= 1 for v in k.values()), "samples_used": k}
    seeds_ok = all(r["seed"] == fz["seeds"][b] + r["sample"] * fz["seeds"]["per_sample"] + r["problem_index"]
                   for (m, b, c), byk in d.items() for r in byk.values())
    gates["G-SEEDS"] = {"pass": seeds_ok}
    pre_ok = all(r["prefill_ids"] == (fz["prefill_ids"] if c == "F" else []) for (m, b, c), byk in d.items() if c in ("P", "F")
                 for r in byk.values())
    gates["G-PREFILL"] = {"pass": pre_ok}
    res = {"gates": gates, "samples_used": k, "cells": {}, "comparisons": {}, "outcomes": {}, "quotes": {}}
    if not gates["G-COMPLETE"]["pass"]:
        res["status"] = "INVALID: a set has no complete sample"
        return res
    A = {(m, b, c): cell_arrays(d, fz, m, b, c, len(probs[b]), k[b]) for m in models for b in BENCHES for c in CELLS}
    for (m, b, c), a in A.items():
        res["cells"][f"{m}|{b}|{c}"] = readout(a, fz)
        res["quotes"][f"{m}|{b}|{c}"] = quotes(d, m, b, c, probs)

    # instrument checks: identity pair and a planted difference
    x = A[("base", "math500", "P")]["score"]
    planted = x.copy()
    planted[:60] = 1
    ident, plant = boot(x, x), boot(planted, x)
    res["instrument"] = {"identity": ident, "identity_pass": ident["diff"] == 0 and ident["ci95"] == [0.0, 0.0],
                         "planted": plant, "planted_pass": plant["ci95"][0] > 0}

    C = res["comparisons"]
    for b in BENCHES:
        for m in models:
            P = A[(m, b, "P")]
            for c in ("F", "P+C", "F+C"):
                C[f"{b}|{m}|{c} - P"] = boot(A[(m, b, c)]["score"], P["score"])
            if m != "base":
                C[f"{b}|{m} P - base P"] = boot(P["score"], A[("base", b, "P")]["score"])
                C[f"{b}|{m} P - base P|both finished"] = boot(P["score"], A[("base", b, "P")]["score"], P["fin"] & A[("base", b, "P")]["fin"])
        C[f"{b}|base F+C - base F"] = boot(A[("base", b, "F+C")]["score"], A[("base", b, "F")]["score"])
    # outcomes (a), (b): step 2,800's best arm against base F+C
    oc = res["outcomes"]
    lab = {}
    for b in BENCHES:
        best = max(CELLS, key=lambda c: res["cells"][f"s2800|{b}|{c}"]["acc"])
        cmp = boot(A[("s2800", b, best)]["score"], A[("base", b, "F+C")]["score"])
        cmp["best_arm"] = best
        cmp["label"] = lab[b] = label(cmp)
        C[f"{b}|s2800 best ({best}) - base F+C"] = cmp
    oc["a"] = lab["math500"] == "MATCHES" and lab["hard"] == "MATCHES"
    oc["b"] = lab["math500"] == "MATCHES" and lab["hard"] == "FALLS SHORT"
    seq = [res["cells"][f"{m}|hard|P"]["cap_hit_share"] for m in ("base", "s0100", "s0400", "s2800") if m in models]
    drop = 100 * (res["cells"]["base|hard|P"]["cap_hit_share"] - res["cells"]["s2800|hard|P"]["cap_hit_share"])
    cg = C["hard|base F+C - base F"]
    oc["c"] = bool(drop >= CAP_DROP and cg["diff"] < C_GAIN_POINT and cg["ci95"][1] < C_GAIN_HI)
    oc["c_values"] = {"cap_hit_share_hard_P_by_step": seq, "drop_points_base_to_2800": drop, "base_C_gain_on_F": cg}
    oc["labels"] = lab
    # the first release (SPEC3 §7.4)
    if "fr" in models:
        fr = {}
        for b in BENCHES:
            x, y = A[("s2800", b, "P")], A[("fr", b, "P")]
            allp = boot(x["score"], y["score"])
            both = boot(x["score"], y["score"], x["fin"] & y["fin"])
            withc = boot(x["score"], A[("fr", b, "P+C")]["score"])
            if allp["ci95"][0] is None or allp["ci95"][0] <= 0:
                lb = "UNDECIDED (no 3.1 - first-release difference to locate)"
            elif both["ci95"][0] is not None and both["ci95"][0] > 0:
                lb = "REFUTED (the difference remains on problems both finish)"
            elif both["ci95"][0] is not None and withc["ci95"][0] <= 0 <= withc["ci95"][1]:
                lb = "SUPPORTED"
            else:
                lb = "PARTLY (not on problems both finish, but forced commit does not close it)"
            fr[b] = {"s2800 P - fr P": allp, "s2800 P - fr P|both finished": both, "s2800 P - fr P+C": withc, "label": lb,
                     "fr_cap_hit_share": res["cells"][f"fr|{b}|P"]["cap_hit_share"]}
        oc["first_release"] = fr
    res["status"] = "COMPLETE" if all(g["pass"] for g in gates.values()) and res["instrument"]["identity_pass"] \
        and res["instrument"]["planted_pass"] else "INVALID: a gate failed"
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--banks", required=True)
    ap.add_argument("--inputs", default=str(pathlib.Path(__file__).resolve().parents[1] / "data" / "rln3"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = verdict(pathlib.Path(a.banks), pathlib.Path(a.inputs))
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1, default=str))
    print(res["status"], json.dumps(res["gates"]), json.dumps(res.get("outcomes", {}).get("labels")), flush=True)
    for key, v in res["cells"].items():
        print(f"{key:24s} acc {v['acc']:5.1f}  cap {v['cap_hit_share']:.3f}  tokens {v['mean_tokens']:7.0f}  n {v['n']}x{v['samples']}")


if __name__ == "__main__":
    main()
