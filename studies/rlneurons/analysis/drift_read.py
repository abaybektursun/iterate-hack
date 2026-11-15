"""Drift (specs/SPEC_drift.md), Q1 to Q4, from the signs of analysis/drift.py and the committed rows.

    uv run --no-project --with numpy --with math-verify==0.9.0 --with tokenizers python -m studies.rlneurons.analysis.drift_read \
        --features <runs root>/drift_features --runs <runs root> --out studies/rlneurons/results/drift --nn 01

Writes <out>/describe-<nn>/ (Q1), predict-<nn>/ (Q2, Q3), stop-<nn>/ (Q4): run.json, readout.json, table.md, examples.json.
Q4 replays analysis/frontier.py's rules on rows in which a stopped sample is replaced by a cap hit at its stop token.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import drift as D
from studies.rlneurons.analysis import frontier as FR

SPEC = "studies/rlneurons/specs/SPEC_drift.md"
RES = pathlib.Path(__file__).resolve().parents[1] / "results"
ROWS = {"hard328_sft": "thinkvote/hard328_sft1_cue_s4-01", "fresh_sft": "fresh/sft1_cue_s4-01", "math500_sft": "thinkvote/math500_sft1_cue_s4-01"}
BOOT, PERM, CHECKS, CAP = 5000, 10000, (4000, 8000, 12000), 16384
SIGNS = ("switch", "rep50", "loopA", "zratio", "wait", "restart", "any")
COUNTED = ("rep50", "zratio", "wait", "restart")
STRATA = {"0": (0, 0), "1-2": (1, 2), "3-4": (3, 4)}
INF = 10 ** 9


def load(features: pathlib.Path, cell: str) -> list:
    return [json.loads(l) for l in (features / f"{cell}.jsonl").read_text().splitlines()]


def arrays(rows: list) -> dict:
    """Per-sample vectors. Counted signs are stored per 1,000 tokens; index k = the sign after k thousand tokens."""
    a = {"prob": np.array([r["problem_index"] for r in rows]), "sample": np.array([r["sample"] for r in rows]),
         "right": np.array([r["score_v3"] == 1 for r in rows]), "n_new": np.array([r["n_new"] for r in rows]),
         "cap": np.array([r["cap_hit"] for r in rows]),
         "switch": np.array([r["episodes"][0]["detect_tok"] if r["episodes"] else INF for r in rows]),
         "start": np.array([r["episodes"][0]["start_tok"] if r["episodes"] else INF for r in rows]),
         "loopA": np.array([r["loop_tok"] or INF for r in rows]), "rows": rows}
    a["any"] = np.minimum(a["switch"], a["loopA"])
    return a


def sign(a: dict, name: str, t: int) -> np.ndarray:
    """The sign of every sample after t tokens; a sample that ended before t keeps the value of its last full 1,000 tokens."""
    if name in ("switch", "loopA", "any"):
        return (a[name] <= t).astype(float)
    if name == "length":
        return np.minimum(a["n_new"], t).astype(float)
    out = np.zeros(len(a["rows"]))
    for i, r in enumerate(a["rows"]):
        k = min(t // D.GRID, len(r["rep50"]))
        if k == 0:
            out[i] = -1.0 if name == "zratio" else 0.0
        else:
            out[i] = {"rep50": r["rep50"][k - 1], "zratio": -r["zratio"][k - 1], "wait": r["wait"][k - 1] / k, "restart": r["restart"][k - 1] / k}[name]
    return out


def weights(n: int, rng) -> np.ndarray:
    return np.array([np.bincount(i, minlength=n) for i in rng.integers(0, n, (BOOT, n))], float)


def ci(x) -> list:
    return [float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]


# ------------------------------------------------------------------------------------------------ Q1

def describe(a: dict, cap: int = CAP) -> dict:
    rows = a["rows"]
    sw = [r for r in rows if r["episodes"]]
    first = [r["episodes"][0] for r in sw]
    scripts = {}
    for r in sw:
        for e in r["episodes"]:
            for s, k in e["scripts"].items():
                scripts[s] = scripts.get(s, 0) + k
    q = lambda v: [int(x) for x in np.percentile(v, [25, 50, 75])] if len(v) else None
    caps = [r for r in rows if r["cap_hit"]]
    return {
        "samples": len(rows), "with_switch": len(sw), "cap_hits": len(caps), "cap_hits_with_switch": sum(bool(r["episodes"]) for r in caps),
        "cap_hits_with_over_20_chinese_characters": sum(r["chinese_chars"] > 20 for r in caps),
        "finished_with_switch": sum(not r["cap_hit"] for r in sw), "switched_and_right": sum(r["score_v3"] == 1 for r in sw),
        "not_switched_and_right": sum(r["score_v3"] == 1 for r in rows if not r["episodes"]),
        "problems_with_a_switch": len({r["problem_index"] for r in sw}), "letters_by_script": dict(sorted(scripts.items(), key=lambda x: -x[1])),
        "first_episode_main_script": {s: sum(max(e["scripts"], key=e["scripts"].get) == s for e in first) for s in sorted({max(e["scripts"], key=e["scripts"].get) for e in first})},
        "start_tok_quartiles": q([e["start_tok"] for e in first]), "start_before_4000": sum(e["start_tok"] < 4000 for e in first),
        "start_before_8000": sum(e["start_tok"] < 8000 for e in first),
        "tokens_from_switch_to_end_quartiles": q([r["n_tok"] - r["episodes"][0]["start_tok"] for r in sw]),
        "first_episode_back": {k: sum(e["back"] is v for e in first) for k, v in (("yes", True), ("no", False), ("text ends within 1,000 characters", None))},
        "episodes_per_switched_sample_quartiles": q([len(r["episodes"]) for r in sw]),
        "first_episode_letters_quartiles": q([e["letters"] for e in first]),
        "nonlatin_share_of_letters_after_first_switch_quartiles": [round(float(x), 3) for x in np.percentile([r["nonlatin_share_after_first"] for r in sw], [25, 50, 75])] if sw else None,
        "switch_before_cap_16384": sum(e["detect_tok"] <= cap for e in first),
    }


def clustering(a: dict, rng) -> dict:
    """S = pairs of samples of one problem that both switch, against flags permuted over all samples (A) and over cap hits only (B)."""
    idx = sorted(set(a["prob"]))
    pos = {p: k for k, p in enumerate(idx)}
    pi = np.array([pos[p] for p in a["prob"]])
    f = a["switch"] < INF
    S = lambda fl: int(sum(k * (k - 1) // 2 for k in np.bincount(pi, weights=fl, minlength=len(idx)).astype(int)))
    obs, capm = S(f), a["cap"]
    nullA = np.array([S(rng.permutation(f)) for _ in range(PERM)])
    nullB = []
    for _ in range(PERM):
        g = f.copy()
        g[capm] = rng.permutation(f[capm])
        nullB.append(S(g))
    nullB = np.array(nullB)
    k = np.bincount(pi, weights=f, minlength=len(idx)).astype(int)
    return {"pairs_of_one_problem_that_both_switch": obs, "problems_by_number_of_switched_samples": {str(j): int((k == j).sum()) for j in range(5)},
            "null_A_all_samples": {"mean": float(nullA.mean()), "p_one_sided": float(((nullA >= obs).sum() + 1) / (PERM + 1))},
            "null_B_within_cap_hits": {"mean": float(nullB.mean()), "p_one_sided": float(((nullB >= obs).sum() + 1) / (PERM + 1))}}


def quote(text: str, e: dict) -> dict:
    return {"before_300": text[max(0, e["start_char"] - 300):e["start_char"]], "from_switch_500": text[e["start_char"]:e["start_char"] + 500],
            "after_episode_300": text[e["end_char"] + 1:e["end_char"] + 301], "text_last_200": text[-200:]}


def texts(runs: pathlib.Path, cell: str) -> dict:
    out = {}
    for l in (runs / D.CELLS[cell] / "answers.jsonl").read_text().splitlines():
        r = json.loads(l)
        if r["attempt"] == 0:
            out[(r["problem_index"], r["sample"])] = r["text"]
    return out


def hand_read_draw(F: dict, T: dict, rng) -> list:
    out = []
    for cell, k in (("hard328_sft", 8), ("fresh_sft", 8), ("cap32_sft", 4)):
        sw = [r for r in F[cell] if r["episodes"]]
        for j in sorted(rng.choice(len(sw), min(k, len(sw)), replace=False)):
            r = sw[j]
            e = r["episodes"][0]
            out.append({"cell": cell, "problem_index": r["problem_index"], "unique_id": r["unique_id"], "sample": r["sample"], "n_new": r["n_new"], "cap_hit": r["cap_hit"],
                        "score_v3": r["score_v3"], "start_tok": e["start_tok"], "letters": e["letters"], "scripts": e["scripts"], "back": e["back"],
                        "episodes": len(r["episodes"]), **quote(T[cell][(r["problem_index"], r["sample"])], e)})
    return out


# ------------------------------------------------------------------------------------------------ Q2

def joined(parts: list) -> dict:
    """Several sets as one: problem ids made distinct."""
    out = {k: np.concatenate([p[k] for p in parts]) for k in ("sample", "right", "n_new", "cap", "switch", "start", "loopA", "any", "base")}
    out["prob"] = np.concatenate([p["prob"] + 100000 * j for j, p in enumerate(parts)])
    out["rows"] = [r for p in parts for r in p["rows"]]
    return out


def paired(a: dict, flag: np.ndarray, run: np.ndarray, rng) -> dict:
    """Within problem: mean right of the flagged running samples minus mean right of the other running samples."""
    d = []
    for p in sorted(set(a["prob"][run])):
        m = run & (a["prob"] == p)
        A, B = m & flag, m & ~flag
        if A.any() and B.any():
            d.append(a["right"][A].mean() - a["right"][B].mean())
    d = np.array(d)
    if len(d) == 0:
        return {"problems": 0}
    boot = d[rng.integers(0, len(d), (BOOT, len(d)))].mean(1)
    return {"problems": len(d), "difference_points": float(100 * d.mean()), "interval95": [100 * x for x in ci(boot)]}


def by_stratum(a: dict, flag: np.ndarray, run: np.ndarray, rng) -> dict:
    """Unmatched difference in the right rate inside each base stratum, and the mean weighted by the flagged samples."""
    idx = sorted(set(a["prob"]))
    pos = {p: k for k, p in enumerate(idx)}
    pi = np.array([pos[p] for p in a["prob"]])
    W = weights(len(idx), rng)
    out, parts = {}, []
    for s, (lo, hi) in STRATA.items():
        m = run & (a["base"] >= lo) & (a["base"] <= hi)
        A, B = m & flag, m & ~flag
        c = lambda M: np.array([np.bincount(pi[M], minlength=len(idx)), np.bincount(pi[M], weights=a["right"][M], minlength=len(idx))], float)
        (nA, rA), (nB, rB) = c(A), c(B)
        with np.errstate(invalid="ignore", divide="ignore"):
            boot = (W @ rA) / (W @ nA) - (W @ rB) / (W @ nB)
        out[s] = {"flagged": int(A.sum()), "flagged_right": int(a["right"][A].sum()), "others": int(B.sum()), "others_right": int(a["right"][B].sum()),
                  "difference_points": None if not A.any() or not B.any() else float(100 * (a["right"][A].mean() - a["right"][B].mean())),
                  "interval95": None if not A.any() or not B.any() else [100 * x for x in ci(boot)]}
        if A.any() and B.any():
            parts.append((A.sum(), a["right"][A].mean() - a["right"][B].mean(), boot))
    n = sum(p[0] for p in parts)
    out["weighted"] = {"difference_points": float(100 * sum(p[0] * p[1] for p in parts) / n), "interval95": [100 * x for x in ci(sum(p[0] * p[2] for p in parts) / n)]} if n else None
    return out


def shuffled_null(a: dict, flag: np.ndarray, run: np.ndarray, rng, k: int = 1000) -> dict:
    """The paired difference with the flags shuffled inside each problem's running samples."""
    probs = [np.flatnonzero(run & (a["prob"] == p)) for p in sorted(set(a["prob"][run]))]
    probs = [m for m in probs if 0 < flag[m].sum() < len(m)]
    out = []
    for _ in range(k):
        d = []
        for m in probs:
            f = rng.permutation(flag[m])
            d.append(a["right"][m][f].mean() - a["right"][m][~f].mean())
        out.append(np.mean(d))
    return {"mean_points": float(100 * np.mean(out)), "interval95": [100 * x for x in ci(out)]}


def fisher(k1: int, n1: int, k2: int, n2: int) -> float:
    """Two-sided Fisher exact p for k1 of n1 against k2 of n2."""
    K, N = k1 + k2, n1 + n2
    p = lambda x: math.comb(n1, x) * math.comb(n2, K - x) / math.comb(N, K)
    p0 = p(k1)
    return float(sum(p(x) for x in range(max(0, K - n2), min(n1, K) + 1) if p(x) <= p0 * (1 + 1e-9)))


def second_half(c: dict, rng) -> dict:
    """The 32,768 sample: answers longer than 16,384 tokens, by a switch before token 16,384."""
    long = c["n_new"] > CAP
    flag = c["switch"] <= CAP
    A, B = long & flag, long & ~flag
    r = c["right"]
    out = {"answers_over_16384": int(long.sum()), "right": int(r[long].sum()), "with_switch_before_16384": int(A.sum()), "with_switch_right": int(r[A].sum()),
           "without_switch": int(B.sum()), "without_switch_right": int(r[B].sum()), "fisher_p_two_sided": fisher(int(r[A].sum()), int(A.sum()), int(r[B].sum()), int(B.sum())),
           "difference_points": float(100 * (r[A].mean() - r[B].mean())),
           "switch_first_seen_after_16384": int((long & (c["switch"] > CAP) & (c["switch"] < INF)).sum()),
           "switch_first_seen_after_16384_right": int(r[long & (c["switch"] > CAP) & (c["switch"] < INF)].sum()),
           "by_base_stratum": by_stratum(c, flag, long, rng)}
    return out


# ------------------------------------------------------------------------------------------------ Q3

def auroc(x: np.ndarray, y: np.ndarray, prob: np.ndarray, W, within: bool) -> dict:
    """P(sign of a not-right sample > sign of a right sample), ties 0.5; within: pairs of one problem only. Problem bootstrap."""
    idx = sorted(set(prob))
    pos = {p: k for k, p in enumerate(idx)}
    pi = np.array([pos[p] for p in prob])
    P, N = np.flatnonzero(y), np.flatnonzero(~y)
    if not len(P) or not len(N):
        return {"auroc": None, "pairs": 0}
    s = (x[P][:, None] > x[N][None, :]) + 0.5 * (x[P][:, None] == x[N][None, :])
    same = pi[P][:, None] == pi[N][None, :]
    if within:
        m = np.bincount(np.broadcast_to(pi[P][:, None], s.shape)[same], weights=s[same], minlength=len(idx))
        c = np.bincount(np.broadcast_to(pi[P][:, None], s.shape)[same], minlength=len(idx)).astype(float)
        if c.sum() == 0:
            return {"auroc": None, "pairs": 0}
        with np.errstate(invalid="ignore", divide="ignore"):
            boot = (W @ m) / (W @ c)
        return {"auroc": float(m.sum() / c.sum()), "interval95": ci(boot), "pairs": int(c.sum()), "problems": int((c > 0).sum())}
    M, C = np.zeros((len(idx), len(idx))), np.zeros((len(idx), len(idx)))
    np.add.at(M, (pi[P][:, None], pi[N][None, :]), s)
    np.add.at(C, (pi[P][:, None], pi[N][None, :]), 1.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        boot = ((W @ M) * W).sum(1) / ((W @ C) * W).sum(1)
    return {"auroc": float(M.sum() / C.sum()), "interval95": ci(boot), "pairs": int(C.sum())}


def predict(a: dict, rng) -> dict:
    idx = sorted(set(a["prob"]))
    W = weights(len(idx), rng)
    y = ~a["right"]
    out = {}
    for t in CHECKS:
        run = a["n_new"] > t
        o = {"samples": len(y), "not_right": int(y.sum()), "running": int(run.sum()), "running_not_right": int(y[run].sum()), "signs": {}}
        for name in SIGNS + ("length",):
            x = sign(a, name, t)
            o["signs"][name] = {"all_pooled": auroc(x, y, a["prob"], W, False)}
            if name != "length":
                o["signs"][name]["running_pooled"] = auroc(x[run], y[run], a["prob"][run], W[:, np.isin(idx, sorted(set(a["prob"][run])))], False)
                o["signs"][name]["running_within_problem"] = auroc(x[run], y[run], a["prob"][run], W[:, np.isin(idx, sorted(set(a["prob"][run])))], True)
            if name in ("switch", "loopA", "any"):
                f = run & (x > 0)
                o["signs"][name]["running_flagged"] = int(f.sum())
                o["signs"][name]["running_flagged_right"] = int(a["right"][f].sum())
        out[str(t)] = o
    return out


def planted(a: dict, rng) -> dict:
    """Instrument check 4: a flag on 80 % of not-right and 20 % of right samples must give a within-problem AUROC above 0.75."""
    y = ~a["right"]
    x = (rng.random(len(y)) < np.where(y, 0.8, 0.2)).astype(float)
    r = auroc(x, y, a["prob"], weights(len(set(a["prob"])), rng), True)
    assert r["auroc"] > 0.75, f"planted sign not found: {r}"
    return r


# ------------------------------------------------------------------------------------------------ Q4

def thresholds(m: dict) -> dict:
    """Per counted sign and checkpoint: the 75th and 90th percentile among MATH-500 Think-SFT samples running at the checkpoint."""
    return {name: {str(t): [float(np.percentile(sign(m, name, t)[m["n_new"] > t], q)) for q in (75, 90)] for t in CHECKS} for name in COUNTED}


def stops(a: dict, rule: str, thr: dict) -> np.ndarray:
    """The token at which the rule stops each sample, INF when it does not. A sample is stopped only while it is still running."""
    n = a["n_new"]
    if rule in ("switch", "loopA", "any"):
        s = a[rule].copy()
    elif rule.startswith("len"):
        s = np.full(len(n), int(rule[3:]))
    elif rule == "oracle4000":
        s = np.where(~a["right"], 4000, INF)
    else:
        name, q = rule.split("_p")
        s = np.full(len(n), INF)
        for t in reversed(CHECKS):
            s = np.where(sign(a, name, t) > thr[name][str(t)][0 if q == "75" else 1], t, s)
    return np.where(s < n, s, INF)


def stopped_chains(ch: dict, a: dict, s: np.ndarray) -> dict:
    """The chains of frontier.load with every stopped sample replaced by a cap hit at its stop token: it costs that many tokens,
    casts no vote and scores 0. The rules of frontier.py then replay unchanged."""
    out = copy.deepcopy(ch)
    for p, k, t in zip(a["prob"], a["sample"], s):
        if t < INF:
            assert len(out[p][k]) == 1 and out[p][k][0]["n_new"] > t
            out[p][k][0].update(n_new=int(t), cap_hit=True, extracted_v3=None, score_v3=0)
    return out


CANDIDATES = ("switch", "loopA", "any") + tuple(f"{n}_p{q}" for n in COUNTED for q in (75, 90)) + ("len12000",)
PLANS = {"seq4": FR.RULES["seq4"], "vote4": FR.RULES["vote4"]}


def simulate(ch: dict, a: dict, thr: dict, W) -> dict:
    base = FR.replay(ch, {**PLANS, "seq3": FR.RULES["seq3"], "seq4_L8000": FR.RULES["seq4_L8000"], "seq4_L12000": FR.RULES["seq4_L12000"]})
    row = lambda p: {"right_stored": int(sum(p["s0"])), "right_24": float(sum(p["s"])), "tokens_stored": float(np.mean(p["t0"])), "tokens_24": float(np.mean(p["t"]))}
    out = {"frontier": {k: row(p) for k, p in base.items()}, "rules": {}}
    for rule in CANDIDATES + ("len8000", "oracle4000"):
        s = stops(a, rule, thr)
        per = FR.replay(stopped_chains(ch, a, s), PLANS)
        o = {"candidate": rule in CANDIDATES, "samples_stopped": int((s < INF).sum()), "stopped_that_end_right": int(a["right"][s < INF].sum()),
             "stopped_that_hit_the_cap": int(a["cap"][s < INF].sum())}
        for plan in PLANS:
            x, b = per[plan], base[plan]
            ds, rt = np.array(x["s"]) - np.array(b["s"]), (W @ np.array(x["t"])) / (W @ np.array(b["t"]))
            o[plan] = {**row(x), "right_24_minus_plain": float(ds.sum()), "right_24_minus_plain_interval95": [x * len(ds) for x in ci((W @ ds) / len(ds))],
                       "tokens_24_ratio_to_plain": float(np.sum(x["t"]) / np.sum(b["t"])), "tokens_ratio_interval95": ci(rt)}
        out["rules"][rule] = o
    return out


def choose(sim: dict) -> str:
    """Among the candidates that fire on at least 30 samples and lose at most 0.5 right (24) to seq4: the fewest tokens."""
    floor = sim["frontier"]["seq4"]["right_24"] - 0.5
    ok = {r: o["seq4"]["tokens_24"] for r, o in sim["rules"].items() if o["candidate"] and o["samples_stopped"] >= 30 and o["seq4"]["right_24"] >= floor}
    assert ok, "no candidate fires on 30 MATH-500 samples without loss: the choice moves to a half of hard328 (spec)"
    return min(ok, key=ok.get)


# ------------------------------------------------------------------------------------------------ output

def f1(x):
    return "" if x is None else f"{x:.1f}"


def iv(x, d=1):
    return "" if x is None else f"[{x[0]:.{d}f}, {x[1]:.{d}f}]"


def md_describe(res: dict) -> str:
    keys = ["hard328_sft", "hard328_rl", "hard328_base", "fresh_sft", "fresh_rl", "fresh_base", "math500_sft", "cap32_sft"]
    o = ["# Drift Q1: switches to a non-Latin script (attempt 0 of every sample; an episode = at least 5 non-Latin letters within 200 characters of each other)", "",
         "| Cell | Samples | With a switch | Cap hits | Cap hits with a switch | Cap hits with > 20 Chinese characters | Finished with a switch | Switched: right | First switch at token: quartiles | Before 4,000 / 8,000 | First episode: back to English yes / no / text ends | Non-Latin share of letters after the switch: quartiles | Letters by script |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in keys:
        d = res["cells"][k]
        b = d["first_episode_back"]
        o.append(f"| {k} | {d['samples']} | {d['with_switch']} | {d['cap_hits']} | {d['cap_hits_with_switch']} | {d['cap_hits_with_over_20_chinese_characters']} | {d['finished_with_switch']} | "
                 f"{d['switched_and_right']} | {d['start_tok_quartiles']} | {d['start_before_4000']} / {d['start_before_8000']} | {b['yes']} / {b['no']} / {b['text ends within 1,000 characters']} | "
                 f"{d['nonlatin_share_of_letters_after_first_switch_quartiles']} | {d['letters_by_script']} |")
    o += ["", "## Problem or sample: pairs of samples of one problem that both switch (10,000 permutations)", "",
          "| Cell | Problems with 0 / 1 / 2 / 3 / 4 switched samples | Pairs observed | Null A (flags over all samples): mean, p | Null B (flags over cap hits only): mean, p |", "|---|---|---|---|---|"]
    for k, c in res["clustering"].items():
        n = c["problems_by_number_of_switched_samples"]
        o.append(f"| {k} | {' / '.join(str(n[str(j)]) for j in range(5))} | {c['pairs_of_one_problem_that_both_switch']} | {c['null_A_all_samples']['mean']:.1f}, {c['null_A_all_samples']['p_one_sided']:.4f} | "
                 f"{c['null_B_within_cap_hits']['mean']:.1f}, {c['null_B_within_cap_hits']['p_one_sided']:.4f} |")
    return "\n".join(o) + "\n"


def md_predict(res: dict) -> str:
    o = ["# Drift Q2 and Q3 (Think-SFT + cue unless a model is named; intervals: 95 %, bootstrap over problems)", "",
         "## Q2: right rate of running samples that have switched by t minus those that have not", "",
         "| Set | t | Running: switched (right) / others (right) | Within problem: problems, difference in points | Shuffled-flag null | Base stratum 0 | 1-2 | 3-4 | Strata, weighted |", "|---|---|---|---|---|---|---|---|---|"]
    for k, d in res["q2"].items():
        for t, x in d.items():
            st = x["by_base_stratum"]
            cell = lambda s: "" if st[s]["difference_points"] is None else f"{st[s]['flagged_right']} of {st[s]['flagged']} against {st[s]['others_right']} of {st[s]['others']}: {st[s]['difference_points']:+.1f} {iv(st[s]['interval95'])}"
            w = st["weighted"]
            o.append(f"| {k} | {t} | {x['switched']} ({x['switched_right']}) / {x['others']} ({x['others_right']}) | {x['paired']['problems']}, "
                     + (f"{x['paired']['difference_points']:+.1f} {iv(x['paired']['interval95'])}" if x["paired"]["problems"] else "")
                     + f" | {x['null']['mean_points']:+.1f} {iv(x['null']['interval95'])} | {cell('0')} | {cell('1-2')} | {cell('3-4')} | "
                     + ("" if not w else f"{w['difference_points']:+.1f} {iv(w['interval95'])}") + " |")
    h = res["cap32"]
    o += ["", "## Q2, the 32,768 sample: answers longer than 16,384 tokens", "",
          f"{h['answers_over_16384']} answers, {h['right']} right. With a switch before token 16,384: {h['with_switch_right']} of {h['with_switch_before_16384']} right; without: "
          f"{h['without_switch_right']} of {h['without_switch']}; difference {h['difference_points']:+.1f} points, Fisher p = {h['fisher_p_two_sided']:.3f}. "
          f"Strata of the base's right count, weighted: " + ("" if not h["by_base_stratum"]["weighted"] else f"{h['by_base_stratum']['weighted']['difference_points']:+.1f} {iv(h['by_base_stratum']['weighted']['interval95'])}")
          + f". A switch first seen after 16,384: {h['switch_first_seen_after_16384_right']} of {h['switch_first_seen_after_16384']} right.", ""]
    for s in STRATA:
        x = h["by_base_stratum"][s]
        o.append(f"- base {s}: with a switch {x['flagged_right']} of {x['flagged']}, without {x['others_right']} of {x['others']}" + ("" if x["difference_points"] is None else f": {x['difference_points']:+.1f} {iv(x['interval95'])}"))
    o += ["", "## Q3: AUROC of each sign for 'the sample does not end right'", "",
          "all: every sample, the sign frozen at the sample's end. running: samples still running at t (length is constant there). within: pairs of one problem.", ""]
    for k, d in res["q3"].items():
        o += [f"### {k}", "", "| t | Samples (not right) / running (not right) | Sign | all, pooled | running, pooled | running, within problem | pairs |", "|---|---|---|---|---|---|---|"]
        for t, x in d.items():
            for name, sg in x["signs"].items():
                g = lambda key: "" if key not in sg or sg[key]["auroc"] is None else f"{sg[key]['auroc']:.3f} {iv(sg[key]['interval95'], 3)}"
                o.append(f"| {t} | {x['samples']} ({x['not_right']}) / {x['running']} ({x['running_not_right']}) | {name}"
                         + (f" ({sg['running_flagged_right']} of {sg['running_flagged']} flagged end right)" if "running_flagged" in sg else "")
                         + f" | {g('all_pooled')} | {g('running_pooled')} | {g('running_within_problem')} | {sg.get('running_within_problem', {}).get('pairs', '')} |")
        o.append("")
    return "\n".join(o) + "\n"


def md_stop(res: dict) -> str:
    o = ["# Drift Q4: stop a sample at its first sign (replay on stored rows; a stopped sample costs its tokens up to the stop and casts no vote)", "",
         f"Chosen on MATH-500 (fewest tokens among candidates that stop at least 30 samples and lose at most 0.5 right (24) to seq4): `{res['chosen']}`.", "",
         "Thresholds (sign > threshold at 4,000 / 8,000 / 12,000; 75th and 90th percentile of MATH-500 samples running there): "
         + "; ".join(f"{n}: " + ", ".join(f"{t}: {v[0]:.4g} / {v[1]:.4g}" for t, v in d.items()) for n, d in res["thresholds"].items()), ""]
    for k in ("math500", "hard328", "fresh2026"):
        d = res["sets"][k]
        o += [f"## {k}, n = {d['n']}" + (" (the choice)" if k == "math500" else " (held out)"), "",
              "| Rule | Samples stopped (would end right / would hit the cap) | seq4: right, right (24), tokens (24) | minus plain seq4, right (24) [95 %] | tokens, ratio to plain seq4 [95 %] | vote4: right, tokens | vote4 minus plain, right (24) | vote4 tokens ratio |",
              "|---|---|---|---|---|---|---|---|"]
        fr = d["frontier"]
        for name in ("seq4", "seq3", "seq4_L12000", "seq4_L8000", "vote4"):
            x = fr[name]
            o.append(f"| frontier `{name}` (no stop) | | {x['right_stored']}, {x['right_24']:.1f}, {x['tokens_24']:,.0f} | | {x['tokens_24'] / fr['seq4']['tokens_24']:.3f} | | | |")
        for rule, x in d["rules"].items():
            s, v = x["seq4"], x["vote4"]
            tag = " **chosen**" if rule == res["chosen"] else ("" if x["candidate"] else " (not a candidate)")
            o.append(f"| `{rule}`{tag} | {x['samples_stopped']} ({x['stopped_that_end_right']} / {x['stopped_that_hit_the_cap']}) | {s['right_stored']}, {s['right_24']:.1f}, {s['tokens_24']:,.0f} | "
                     f"{s['right_24_minus_plain']:+.1f} {iv(s['right_24_minus_plain_interval95'])} | {s['tokens_24_ratio_to_plain']:.3f} {iv(s['tokens_ratio_interval95'], 3)} | "
                     f"{v['right_stored']}, {v['tokens_24']:,.0f} | {v['right_24_minus_plain']:+.1f} {iv(v['right_24_minus_plain_interval95'])} | {v['tokens_24_ratio_to_plain']:.3f} |")
        o.append("")
    return "\n".join(o) + "\n"


def sign_examples(a: dict, T: dict, t: int = 8000) -> dict:
    """Per sign: among hard328 Think-SFT samples running at t, the one with the highest sign that ended right and the one that did
    not (for switch, loopA: the first flagged by 12,000), with the 300 characters before the token where the sign is read."""
    out = {}
    run = a["n_new"] > t
    for name in SIGNS:
        tt = 12000 if name in ("switch", "loopA", "any") else t
        x = sign(a, name, tt)
        out[name] = {}
        for want, label in ((True, "ended_right"), (False, "ended_not_right")):
            m = np.flatnonzero((a["n_new"] > tt if tt != t else run) & (a["right"] == want) & (x > (0 if tt != t else -INF)))
            if not len(m):
                out[name][label] = None
                continue
            i = m[np.argmax(x[m])]
            r = a["rows"][i]
            text = T[(r["problem_index"], r["sample"])]
            _, off = D.encode(text)
            at = int(a[name][i]) if tt != t else t
            c = off[min(at, len(off)) - 1][1]
            out[name][label] = {"problem_index": r["problem_index"], "unique_id": r["unique_id"], "sample": r["sample"], "n_new": r["n_new"], "cap_hit": r["cap_hit"],
                                "score_v3": r["score_v3"], "extracted_v3": r["extracted_v3"], "sign_read_at_token": at, "sign_value": float(x[i]),
                                "text_before_that_token_300": text[max(0, c - 300):c], "text_after_100": text[c:c + 100]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--nn", default="01")
    a = ap.parse_args()
    feat, runs, out = pathlib.Path(a.features), pathlib.Path(a.runs), pathlib.Path(a.out)
    dirs = {k: out / f"{k}-{a.nn}" for k in ("describe", "predict", "stop")}
    for d in dirs.values():
        assert not d.exists(), f"{d} exists: a rerun gets the next number"
    rng = np.random.default_rng(0)
    F = {c: load(feat, c) for c in D.CELLS}
    A = {c: arrays(F[c]) for c in F}
    for s in ("hard328", "fresh"):                                          # the base's right count per problem, on every model's samples
        b = A[f"{s}_base"]
        cnt = {p: int(b["right"][b["prob"] == p].sum()) for p in set(b["prob"])}
        for m in ("sft", "rl", "base"):
            A[f"{s}_{m}"]["base"] = np.array([cnt[p] for p in A[f"{s}_{m}"]["prob"]])
    cnt = {p: int(A["hard328_base"]["right"][A["hard328_base"]["prob"] == p].sum()) for p in set(A["hard328_base"]["prob"])}
    A["cap32_sft"]["base"] = np.array([cnt[p] for p in A["cap32_sft"]["prob"]])
    for c, d in ROWS.items():                                               # the texts are the rows of the committed run folders
        rows = {(r["problem_index"], r["sample"]): r for r in map(json.loads, (RES / d / "rows.jsonl").read_text().splitlines()) if r["attempt"] == 0}
        assert all(rows[(r["problem_index"], r["sample"])]["n_new"] == r["n_new"] and rows[(r["problem_index"], r["sample"])]["score_v3"] == r["score_v3"] for r in F[c]) and len(rows) == len(F[c])
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    run = {"commit": commit, "command": "python -m studies.rlneurons.analysis.drift_read " + " ".join(sys.argv[1:]), "job_id": None, "gpu": "none (laptop)", "spec": SPEC,
           "signs": "python -m studies.rlneurons.analysis.drift (tokenizer %s @ %s)" % D.TOKENIZER, "bootstrap": {"resamples": BOOT, "seed": 0}, "permutations": PERM,
           "texts": {c: f"runs/{d}/answers.jsonl" for c, d in D.CELLS.items()}}

    # Q1
    T = {c: texts(runs, c) for c in ("hard328_sft", "fresh_sft", "cap32_sft")}
    q1 = {"cells": {c: describe(A[c]) for c in F}, "clustering": {c: clustering(A[c], rng) for c in ("hard328_sft", "fresh_sft", "math500_sft")},
          "cap32_switches": {"first_switch_before_16384": int((A["cap32_sft"]["switch"] <= CAP).sum()),
                             "first_switch_after_16384": int(((A["cap32_sft"]["switch"] > CAP) & (A["cap32_sft"]["switch"] < INF)).sum())}}
    draw = hand_read_draw(F, T, np.random.default_rng(0))

    # Q2, Q3
    S = {"hard328": A["hard328_sft"], "fresh2026": A["fresh_sft"]}
    S["pooled"] = joined([A["hard328_sft"], A["fresh_sft"]])
    q2 = {}
    for k, s in S.items():
        q2[k] = {}
        for t in CHECKS:
            runm, flag = s["n_new"] > t, s["switch"] <= t
            q2[k][str(t)] = {"switched": int((runm & flag).sum()), "switched_right": int(s["right"][runm & flag].sum()), "others": int((runm & ~flag).sum()),
                             "others_right": int(s["right"][runm & ~flag].sum()), "paired": paired(s, flag, runm, rng), "null": shuffled_null(s, flag, runm, rng),
                             "by_base_stratum": by_stratum(s, flag, runm, rng)}
    null = q2["pooled"]["8000"]["null"]
    assert null["interval95"][0] < 0 < null["interval95"][1], f"shuffled flags give a difference away from 0: {null}"
    q3 = {f"Think-SFT, {k}": predict(s, rng) for k, s in S.items()}
    for m, label in (("rl", "RL plain"), ("base", "base + cue")):
        q3[f"{label}, pooled (control)"] = predict(joined([A[f"hard328_{m}"], A[f"fresh_{m}"]]), rng)
    pred = {"q2": q2, "cap32": second_half(A["cap32_sft"], rng), "q3": q3, "planted_sign_within_problem_auroc": planted(S["pooled"], rng),
            "references": {"result-f3d708": "0.531 [0.468, 0.589] (0.504 without the first 50 tokens), cued base, MATH-500, first 1,000 tokens",
                           "result-b30f15": "0.571 [0.509, 0.634] linear probe after 1,000 tokens; answer length at the end 0.68"}}

    # Q4
    thr = thresholds(A["math500_sft"])
    sets = {}
    for k, c in (("math500", "math500_sft"), ("hard328", "hard328_sft"), ("fresh2026", "fresh_sft")):
        _, ch = FR.load(RES / ROWS[c])
        W = weights(len(ch), rng)
        sets[k] = {"n": len(ch), **simulate(ch, A[c], thr, W)}
    got = {k: (sets[k]["frontier"]["seq4"]["right_stored"], round(sets[k]["frontier"]["seq4"]["tokens_stored"]), sets[k]["frontier"]["vote4"]["right_stored"]) for k in sets}
    assert got == {"math500": (481, 11521, 481), "hard328": (241, 30904, 241), "fresh2026": (75, 42251, 75)}, f"instrument check: the frontier rows do not reproduce: {got}"
    stop = {"thresholds": thr, "chosen": choose(sets["math500"]), "sets": sets}

    for d in dirs.values():
        d.mkdir(parents=True)
        (d / "run.json").write_text(json.dumps(run, indent=1) + "\n")
    w = lambda d, name, obj: (dirs[d] / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    w("describe", "readout.json", q1), w("describe", "examples.json", draw), (dirs["describe"] / "table.md").write_text(md_describe(q1))
    w("predict", "readout.json", pred), w("predict", "examples.json", sign_examples(A["hard328_sft"], T["hard328_sft"])), (dirs["predict"] / "table.md").write_text(md_predict(pred))
    c = stop["chosen"]
    s = stops(A["hard328_sft"], c, thr)
    ex = {}
    for want, label in ((1, "stopped_sample_would_have_ended_right"), (0, "stopped_sample_would_not_have_ended_right")):
        i = next(i for i in np.flatnonzero(s < INF) if A["hard328_sft"]["right"][i] == want)
        r = F["hard328_sft"][i]
        text = T["hard328_sft"][(r["problem_index"], r["sample"])]
        cc = D.encode(text)[1][int(s[i]) - 1][1]
        ex[label] = {"rule": c, "problem_index": r["problem_index"], "unique_id": r["unique_id"], "sample": r["sample"], "stopped_at_token": int(s[i]), "n_new": r["n_new"], "cap_hit": r["cap_hit"],
                     "score_v3": r["score_v3"], "extracted_v3": r["extracted_v3"], "text_before_the_stop_300": text[max(0, cc - 300):cc], "text_last_200": text[-200:],
                     "the_problem's_four_samples": [{k: x[k] for k in ("sample", "n_new", "cap_hit", "extracted_v3", "score_v3")} for x in F["hard328_sft"] if x["problem_index"] == r["problem_index"]]}
    w("stop", "readout.json", stop), w("stop", "examples.json", ex), (dirs["stop"] / "table.md").write_text(md_stop(stop))
    for d in dirs.values():
        print((d / "table.md").read_text())


if __name__ == "__main__":
    main()
