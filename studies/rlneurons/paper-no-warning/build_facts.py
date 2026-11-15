"""The verified data layer of the paper on early warning ("which problem is hard" against "which attempt will fail").

    uv run --no-project --with numpy --with math-verify==0.9.0 python studies/rlneurons/paper-no-warning/build_facts.py

Reads only files in git (no runs/, no model). Writes, next to this file:
  facts.json     every number the paper may use: {value, ci95, n, unit, source, note}. `recomputed` blocks are computed
                 here from per-sample rows and asserted against the stored readouts; `copied` blocks are read from a readout
                 because the per-sample scores (activations, token log-probabilities, Think-SFT texts) are not in git.
  examples.json  one problem with one sample scored right and one scored wrong: first 300 characters, probe scores, signs.

AUROC convention, every instrument: the share of (right sample, wrong sample) pairs in which the instrument, oriented before
looking (shorter, finished, agreeing, less compressible, fewer "wait"), ranks the right sample higher; ties count 0.5.
  across (pooled): pairs of any two samples; interval by bootstrap over problems (2,000 resamples, seed 0).
  within problem : pairs of two samples of one problem; interval by bootstrap over the problems that have such a pair
                   (the rule of analysis/critic_probe.py, so the readouts can be compared).
Ceilings: paired bootstrap over problems, 10,000 resamples, seed 0, 95 % percentile, in points.
"""
import gzip
import itertools
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(ROOT))
from studies.rlneurons.analysis import critic_ceiling, day1_vote, drift  # noqa: E402  (shared code, not copied)
from studies.rlneurons.lib import rln4_lib as R  # noqa: E402

RES = STUDY / "results"
B_AUROC, B_PAIRED = 2000, 10000
CELLS = {"math500_base_cue": "day1_3/math500_base_cue-01", "math500_rl": "day1_3/math500_rl-01",
         "hard328_base_cue": "day1_3/hard328_base_cue_s4r2-01", "hard328_rl": "day1_3/hard328_rl_plain_s4r2-01"}
CHECKS = []


def rel(p):
    return str(pathlib.Path(p).resolve().relative_to(ROOT))


def rj(path):
    return json.loads((RES / path).read_text())


def check(name, got, want, tol=0.0):
    assert abs(got - want) <= tol, f"{name}: recomputed {got}, stored {want} (tolerance {tol})"
    CHECKS.append({"name": name, "recomputed": got, "stored": want, "tolerance": tol})


def fact(value, n, unit, source, note="", ci95=None):
    return {"value": value, "ci95": ci95, "n": n, "unit": unit, "source": source, "note": note}


def r4(x):
    return None if x is None else round(float(x), 4)


# ---------------------------------------------------------------- rows
def load(cell):
    """attempt 0 of the four samples of every problem -> (problem indices, rows[P][4])."""
    by = {}
    for line in open(RES / CELLS[cell] / "rows.jsonl"):
        r = json.loads(line)
        if r["attempt"] == 0:
            by.setdefault(r["problem_index"], {})[r["sample"]] = r
    idx = sorted(by)
    assert all(sorted(by[i]) == [0, 1, 2, 3] for i in idx), cell
    return idx, [[by[i][s] for s in range(4)] for i in idx]


def arr(rows, f):
    return np.array([[f(r) for r in four] for four in rows], dtype=float)


# ---------------------------------------------------------------- AUROC
def pair_tables(score, y, mask=None):
    """W[p, q] = pairs (right sample of p, wrong sample of q) ordered correctly (ties 0.5); N[p, q] = number of such pairs."""
    P = score.shape[0]
    m = np.ones_like(y, dtype=bool) if mask is None else mask
    s, g, b = score.ravel(), ((y == 1) & m).ravel(), ((y == 0) & m).ravel()
    d = s[:, None] - s[None, :]
    gb = g[:, None] & b[None, :]
    w = ((d > 0) + 0.5 * (d == 0)) * gb
    return w.reshape(P, 4, P, 4).sum((1, 3)), gb.reshape(P, 4, P, 4).sum((1, 3)).astype(float)


def auroc(score, y, mask=None, seed=0):
    """-> (across fact-parts, within fact-parts); each (value, ci95, n-dict)."""
    W, N = pair_tables(score, y, mask)
    rng = np.random.default_rng(seed)
    P = len(W)
    C = rng.multinomial(P, np.full(P, 1 / P), B_AUROC).astype(float)        # bootstrap over problems: counts per problem
    num, den = ((C @ W) * C).sum(1), ((C @ N) * C).sum(1)
    across = (r4(W.sum() / N.sum()), [r4(q) for q in np.percentile(num / den, [2.5, 97.5])],
              {"samples": int((np.ones_like(y, bool) if mask is None else mask).sum()), "pairs": int(N.sum()), "problems": P})
    w, n = np.diag(W), np.diag(N)
    k = n > 0
    if not k.any():
        return across, (None, None, {"problems": 0, "pairs": 0})
    w, n = w[k], n[k]
    ix = rng.integers(0, len(w), (B_AUROC, len(w)))
    v = w[ix].sum(1) / n[ix].sum(1)
    within = (r4(w.sum() / n.sum()), [r4(q) for q in np.percentile(v, [2.5, 97.5])], {"problems": int(k.sum()), "pairs": int(n.sum())})
    return across, within


def instrument(label, group, cell, score, y, source, note, mask=None, known="end"):
    a, w = auroc(score, y, mask)
    return {"label": label, "group": group, "set": cell, "known_at": known, "recomputed": True,
            "across": fact(a[0], a[2], "AUROC, pooled over problems", source, note, a[1]),
            "within": fact(w[0], w[2], "AUROC, pairs within one problem", source, note, w[1])}


# ---------------------------------------------------------------- 1. instruments recomputed from the committed rows
def row_instruments(cell, other):
    idx, rows = load(cell)
    oidx, orows = load(other)
    assert idx == oidx
    y = arr(rows, lambda r: r["score_v3"])
    n_new = arr(rows, lambda r: r["n_new"])
    cap = arr(rows, lambda r: r["cap_hit"])
    flag = np.array([critic_ceiling.plurality_flags(four) for four in rows], dtype=float)
    other_rate = np.repeat(arr(orows, lambda r: r["score_v3"]).mean(1, keepdims=True), 4, 1)
    loo = (y.sum(1, keepdims=True) - y) / 3
    src = rel(RES / CELLS[cell] / "rows.jsonl")
    out = {
        "difficulty_other_model": instrument("problem difficulty: the other model's solve rate over 4 samples", "difficulty", cell, other_rate, y,
                                             src + " and " + rel(RES / CELLS[other] / "rows.jsonl"),
                                             "one value per problem, so within-problem AUROC is 0.5 by construction", known="before"),
        "difficulty_own_other_samples": instrument("problem difficulty: this model's solve rate on its other 3 samples", "difficulty", cell, loo, y, src,
                                                   "across only: within a problem the right sample has the lower leave-one-out rate by arithmetic", known="before"),
        "shorter_final": instrument("answer length at the end (shorter = right)", "length", cell, -n_new, y, src, "cap hits count 16,384 tokens"),
        "finished": instrument("did not hit the 16,384 cap", "length", cell, 1 - cap, y, src, ""),
        "no_loop_A": instrument("rule A finds no loop", "text", cell, 1 - arr(rows, lambda r: r["loop_A"]), y, src, ""),
        "agreement": instrument("label-free flag: the answer is in the largest group of agreeing answers of the 4 samples (group of 2 or more)", "agreement",
                                cell, flag, y, src, "analysis/critic_ceiling.plurality_flags; needs the other 3 finished samples"),
    }
    out["difficulty_own_other_samples"]["within"] = fact(None, None, "AUROC", src, "not defined: mechanical, see note of the across value")
    for t in (250, 500, 1000, 2000, 4000, 8000, 12000):
        out[f"length_so_far_{t}"] = instrument(f"answer length so far at token {t:,} (already finished and shorter = right)", "length", cell, -np.minimum(n_new, t), y, src,
                                               "all samples; a sample still running at t has the value t", known=f"token {t}")
        out[f"shorter_final_running_{t}"] = instrument(f"answer length at the end, among samples still running at token {t:,}", "length", cell, -n_new, y, src,
                                                       "not available at t: shows how much signal remains after t", mask=n_new >= t)
    return out, (idx, rows, y, n_new, cap, flag)


def self_checks(y, n_new):
    """The AUROC code on inputs whose answer is known."""
    rng = np.random.default_rng(1)
    const = np.repeat(rng.normal(size=(len(y), 1)), 4, 1)
    w = auroc(const, y)[1]
    assert w[0] == 0.5 and w[1] == [0.5, 0.5], w                             # a problem-level score cannot order two samples of one problem
    planted = auroc(y + rng.normal(size=y.shape), y)[1]
    assert planted[0] > 0.70 and planted[1][0] > 0.65, planted
    sh = -n_new.copy()
    for row in sh:
        rng.shuffle(row)
    shuffled = auroc(sh, y)[1]
    assert shuffled[1][0] < 0.5 < shuffled[1][1], shuffled
    return {"problem_level_score_within": fact(w[0], w[2], "AUROC", "build_facts.self_checks", "must be exactly 0.5", w[1]),
            "planted_sign_within": fact(planted[0], planted[2], "AUROC", "build_facts.self_checks", "score = right + N(0, 1); expected 0.76", planted[1]),
            "length_shuffled_within_problem": fact(shuffled[0], shuffled[2], "AUROC", "build_facts.self_checks", "interval must cover 0.5", shuffled[1])}


# ---------------------------------------------------------------- 2. text signs on the committed answer heads (cued base, MATH-500)
def head_signs(idx, y, n_new):
    path = STUDY / "data" / "wrongstep" / "base_cue_answer_heads_v1.jsonl.gz"
    pos = {p: i for i, p in enumerate(idx)}
    text = [[None] * 4 for _ in idx]
    for line in gzip.open(path, "rt"):
        r = json.loads(line)
        i, s = pos[int(r["problem_index"])], int(r["sample"])
        assert int(r["score_v3"]) == y[i, s] and int(r["n_new"]) == n_new[i, s]
        text[i][s] = r["text"]
    out, src = {}, rel(path)
    for chars in (1000, 3000, 6000):
        mask = np.array([[len(t) >= chars for t in four] for four in text])
        f = lambda fn: np.array([[fn(t[:chars]) for t in four] for four in text], dtype=float)
        note = f"first {chars:,} characters (about {chars // 3:,} tokens at 3.0 characters per token), samples with at least that much text"
        for name, label, score in (
                ("zratio", "zlib ratio of the text so far (less compressible = right)", f(R.zratio)),
                ("wait", 'count of "wait" so far (fewer = right)', -f(lambda t: len(drift.WAIT.findall(t)))),
                ("restart", "count of restart phrases so far (fewer = right)", -f(lambda t: len(drift.RESTART.findall(t))))):
            out[f"{name}_{chars}"] = instrument(f"{label}, first {chars:,} characters", "text", "math500_base_cue", score, y, src, note, mask=mask, known=f"character {chars}")
    return out, text


# ---------------------------------------------------------------- 3. ceilings
def per_problem(rows):
    y = arr(rows, lambda r: r["score_v3"])
    v = {"single": y.mean(1), "vote": np.array([day1_vote.vote(four)["score"] for four in rows], dtype=float)}
    for k in (2, 3, 4):
        v[f"oracle{k}"] = np.mean([y[:, list(c)].max(1) for c in itertools.combinations(range(4), k)], 0)
    short = []
    for four in rows:                                                          # selector.py short1: shortest finished sample with an answer, else the vote
        ks = [k for k, r in enumerate(four) if r["extracted_v3"] is not None and not r["cap_hit"]]
        short.append(four[min(ks, key=lambda k: (four[k]["n_new"], k))]["score_v3"] if ks else day1_vote.vote(four)["score"])
    v["shortest"] = np.array(short, dtype=float)
    return v


def ceilings(tag, base_cell, rl_cell):
    (idx, brows), (_, rrows) = load(base_cell), load(rl_cell)
    b, r = per_problem(brows), per_problem(rrows)
    P = len(idx)
    bs = np.random.default_rng(0).integers(0, P, (B_PAIRED, P))
    srcb, srcr = rel(RES / CELLS[base_cell] / "rows.jsonl"), rel(RES / CELLS[rl_cell] / "rows.jsonl")
    tok = lambda rows: float(arr(rows, lambda x: x["n_new"]).mean())
    names = {"single": "one sample (mean of the 4)", "vote": "plurality vote over 4 (ties to the lowest sample)", "shortest": "the shortest finished sample of 4",
             "oracle2": "perfect critic over 2 samples (right if either is)", "oracle3": "perfect critic over 3", "oracle4": "perfect critic over 4 (pass@4)"}
    out = {"n_problems": P, "right_per_sample": {"base_cue": arr(brows, lambda x: x["score_v3"]).sum(0).astype(int).tolist(),
                                                 "rl": arr(rrows, lambda x: x["score_v3"]).sum(0).astype(int).tolist()}}
    for m, (v, rows, src) in (("base_cue", (b, brows, srcb)), ("rl", (r, rrows, srcr))):
        for k, lab in names.items():
            ci = np.percentile(v[k][bs].sum(1), [2.5, 97.5])
            samples = {"single": 1, "oracle2": 2, "oracle3": 3}.get(k, 4)
            out[f"{m}_{k}"] = fact(round(float(v[k].sum()), 2), P, f"problems right of {P}", src, f"{lab}; {round(samples * tok(rows)):,} generated tokens per problem",
                                   [round(float(x), 1) for x in ci])
    diffs = {"base_oracle4 - rl_single": b["oracle4"] - r["single"], "base_oracle3 - rl_single": b["oracle3"] - r["single"],
             "base_oracle2 - rl_single": b["oracle2"] - r["single"], "base_vote - rl_single": b["vote"] - r["single"],
             "base_shortest - rl_single": b["shortest"] - r["single"], "base_oracle4 - rl_oracle4": b["oracle4"] - r["oracle4"],
             "base_vote - rl_vote": b["vote"] - r["vote"], "rl_single - base_single": r["single"] - b["single"],
             "base_oracle4 - base_single": b["oracle4"] - b["single"], "base_vote - base_single": b["vote"] - b["single"],
             "base_shortest - base_single": b["shortest"] - b["single"], "base_oracle4 - base_vote": b["oracle4"] - b["vote"]}
    out["differences_points"] = {k: fact(round(float(d.mean() * 100), 2), P, "points, paired over problems", f"{srcb}; {srcr}", "",
                                         [round(float(x), 2) for x in np.percentile(d[bs].mean(1) * 100, [2.5, 97.5])]) for k, d in diffs.items()}
    gap, room = float((r["single"] - b["single"]).sum()), float((b["oracle4"] - b["single"]).sum())
    out["share_of_perfect_critic_room_taken"] = {k: fact(round(float((b[k] - b["single"]).sum()) / room, 3), P, "share of (pass@4 - one sample)", srcb, "")
                                                 for k in ("vote", "shortest", "oracle2", "oracle3")}
    out["rl_gap_over_room"] = fact(round(gap / room, 3), P, "RL single minus base single, as a share of (base pass@4 - base single)", f"{srcb}; {srcr}", "")
    for m, cell, v in (("base_cue", base_cell, b), ("rl", rl_cell, r)):       # against the stored readouts
        ro = rj(CELLS[cell] + "/readout.json")
        check(f"{tag} {m} vote", v["vote"].sum(), ro["rows"]["vote"]["right"])
        check(f"{tag} {m} pass@4", v["oracle4"].sum(), ro["rows"]["pass_at_k"]["right"])
        for s, want in enumerate(ro["each_sample"]["single_right"]):
            check(f"{tag} {m} sample {s}", out["right_per_sample"][m][s], want)
    return out


# ---------------------------------------------------------------- 3b. replays asked for by the review of draft 1
def replays():
    (idx, brows), (_, rrows) = load("math500_base_cue"), load("math500_rl")
    P = len(idx)
    src = rel(RES / CELLS["math500_base_cue"] / "rows.jsonl")
    y, n = arr(brows, lambda r: r["score_v3"]), arr(brows, lambda r: r["n_new"])
    rl1, base1 = arr(rrows, lambda r: r["score_v3"]).mean(1), y.mean(1)
    bs = np.random.default_rng(0).integers(0, P, (B_PAIRED, P))

    def run(rows, k, at, stop):                                                # every order of k of the 4 stored samples; a stopped attempt costs `at` tokens; the last is kept
        per = []
        for four in rows:
            rr = tt = c = 0
            for order in itertools.permutations(range(4), k):
                c += 1
                for j, s in enumerate(order):
                    r = four[s]
                    if j == k - 1 or not stop(r):
                        rr += r["score_v3"]; tt += r["n_new"]; break
                    tt += min(r["n_new"], at)
            per.append((rr / c, tt / c))
        return np.array(per)

    def rep(per, ref, note):
        d = per[:, 0] - ref
        return {"right": fact(round(float(per[:, 0].sum()), 1), P, f"problems right of {P}, mean over sample orders", src, f"{note}; {round(float(per[:, 1].mean())):,} tokens per problem",
                              [round(float(x), 1) for x in np.percentile(per[:, 0][bs].sum(1), [2.5, 97.5])]),
                "minus_ref_points": fact(round(float(d.mean() * 100), 2), P, "points, paired over problems", src, "", [round(float(x), 2) for x in np.percentile(d[bs].mean(1) * 100, [2.5, 97.5])])}

    out = {}
    key = lambda at: (lambda r: r["n_new"] > at and not r["score_v3"])
    out["base_key_k4_at_1000"] = rep(run(brows, 4, 1000, key(1000)), rl1, "answer key read at token 1,000 on attempts still running, up to 4 attempts; ref = RL one sample")
    out["rl_key_k4_at_1000"] = rep(run(rrows, 4, 1000, key(1000)), rl1, "the same critic on the RL model's samples; ref = RL one sample")
    for at in (4000, 8000):
        for k in (2, 4):
            out[f"base_restart_if_running_k{k}_at_{at}"] = rep(run(brows, k, at, lambda r, at=at: r["n_new"] > at), base1,
                                                               f"no critic: restart any attempt still running at token {at:,}, up to {k} attempts; ref = base one sample")
    out["wrong_samples_ended_by_1000"] = fact(int(((y == 0) & (n <= 1000)).sum()), int((y == 0).sum()), "wrong samples that end by token 1,000 (never judged by the key critic)", src)
    out["median_length"] = fact(float(np.median(n)), int(n.size), "generated tokens, median over samples", src)
    out["ended_share"] = {str(t): fact(round(float((n <= t).mean()), 3), int(n.size), f"share of samples ended by token {t:,}", src) for t in (1000, 2000, 4000, 8000, 12000)}
    for t in (1000, 2000, 4000):
        m = n > t
        a = auroc(-np.minimum(n, t), y, m)
        b = auroc(-n, y, m)
        out[f"both_running_at_{t}"] = {"token_counter_within": list(a[1]), "final_length_within": list(b[1])}
    return out


# ---------------------------------------------------------------- 4. numbers that can only be copied
def ci_excludes_half(c):
    return c is not None and (c[0] > 0.5 or c[1] < 0.5)


def copied_probe():
    path = "critic/probe-02/metrics.json"
    m, src = rj(path), rel(RES / path)
    cells, fig = {}, []
    for t, row in m["checkpoints"].items():
        for name, v in row.items():
            if not isinstance(v, dict):
                continue
            for target in ("within_flag", "within_correct", "within_correct_trained_on_key", "within_flag_trained_on_shuffled"):
                if target in v:
                    w = v[target]
                    cells[f"{name}@{t}/{target}"] = fact(w["value"], {"problems": w["problems"], "pairs": w["pairs"]}, "AUROC, pairs within one problem", src, "", w["ci95"])
            for target in ("pooled_flag", "pooled_correct"):
                if target in v:
                    cells[f"{name}@{t}/{target}"] = fact(v[target], {"samples": row["samples_reaching"]}, "AUROC, pooled over problems", src,
                                                         "no interval stored; per-sample scores are not in git")
    probes = {k: v for k, v in cells.items() if k.startswith("probe_") and "@0/" not in k}
    summary = {}
    for target in ("within_flag", "within_correct", "within_correct_trained_on_key"):
        sel = {k: v for k, v in probes.items() if k.endswith("/" + target)}
        best = max(sel, key=lambda k: sel[k]["value"])
        summary[target] = {"cells": len(sel), "best_cell": best, "best": sel[best], "intervals_excluding_0.5": sorted(k for k, v in sel.items() if ci_excludes_half(v["ci95"])),
                           "largest_upper_end": max(v["ci95"][1] for v in sel.values()), "smallest_pairs": min(v["n"]["pairs"] for v in sel.values())}
    for k, v in cells.items():
        if k.endswith("/within_correct") and ("probe_" in k or "mean_" in k):
            name, t = k.split("/")[0].split("@")
            pooled = cells.get(f"{name}@{t}/pooled_correct") or cells.get(f"{name}@{t}/pooled_flag")
            fig.append({"label": f"{name.replace('probe_L', 'linear probe, layer ')} after {int(t):,} answer tokens" if t != "0" else f"{name.replace('probe_L', 'linear probe, layer ')} at the last prompt token",
                        "group": "activations" if "probe" in name else "token probabilities", "set": "math500_base_cue", "known_at": f"token {t}", "recomputed": False,
                        "across": pooled, "within": v, "within_label_free_flag": cells[f"{name}@{t}/within_flag"]})
    pol = m["policy_at_1000_tokens"]
    policy = {"probe": fact(pol["probe_right_of_500"], 500, "problems right of 500", src, f"{pol['tokens_per_problem']['probe']} tokens per problem; layer {pol['layer']}"),
              "random_same_stop_rate": fact(pol["random_right_of_500"], 500, "problems right of 500", src, f"{pol['tokens_per_problem']['random']} tokens per problem"),
              "single": fact(pol["single_right_of_500_mean_of_4"], 500, "problems right of 500", src, f"{pol['single_tokens_per_problem']} tokens per problem"),
              "probe_minus_random": fact(pol["probe_minus_random_points"]["value"], 500, "points", src, "", pol["probe_minus_random_points"]["ci95"])}
    return {"samples": m["samples"], "flag_rate": m["flag_rate"], "correct_rate": m["correct_rate"], "cells": cells, "summary": summary, "policy_at_1000_tokens": policy,
            "samples_reaching": {t: row["samples_reaching"] for t, row in m["checkpoints"].items()}}, fig, m


def copied_probdep():
    path = "wrongstep/probdep-02/metrics.json"
    m, src = rj(path), rel(RES / path)
    return {k: fact(v["value"], {"problems": v["problems"], "pairs": v["pairs"]}, "AUROC, pairs within one problem", src, "target: scored right", v["ci95"])
            for k, v in m["features"].items()}, m


def copied_drift():
    path = "drift/predict-01/readout.json"
    m, src = rj(path), rel(RES / path)
    out, fig = {}, []
    for cell, by_t in m["q3"].items():
        for t, row in by_t.items():
            for sign, v in row["signs"].items():
                for kind in ("all_pooled", "running_pooled", "running_within_problem"):
                    if kind in v:
                        x = v[kind]
                        out[f"{cell}/{t}/{sign}/{kind}"] = fact(r4(x["auroc"]), {k: x[k] for k in ("pairs", "problems") if k in x}, "AUROC for 'does not end right'", src,
                                                                f"{row['running']} of {row['samples']} samples still running at token {t}", [r4(q) for q in x["interval95"]])
                if cell == "Think-SFT, pooled" and sign not in ("length", "any"):
                    fig.append({"label": f"{sign} at token {int(t):,}", "group": "text", "set": "hard328 + fresh2026, Think-SFT + cue", "known_at": f"token {t}", "recomputed": False,
                                "across": out[f"{cell}/{t}/{sign}/running_pooled"], "within": out[f"{cell}/{t}/{sign}/running_within_problem"]})
    summary = {}
    for cell in m["q3"]:
        sel = {k: v for k, v in out.items() if k.startswith(cell + "/") and k.endswith("running_within_problem") and "/any/" not in k}
        best = max(sel, key=lambda k: sel[k]["value"])
        summary[cell] = {"cells": len(sel), "best_cell": best, "best": sel[best], "intervals_excluding_0.5": sorted(k for k, v in sel.items() if ci_excludes_half(v["ci95"])),
                         "largest_upper_end": max(v["ci95"][1] for v in sel.values())}
    p = m["planted_sign_within_problem_auroc"]
    planted = fact(r4(p["auroc"]), {"pairs": p["pairs"], "problems": p["problems"]}, "AUROC", src, "instrument check: a planted sign (80 % of not-right, 20 % of right samples)",
                   [r4(q) for q in p["interval95"]])
    stop, ssrc = rj("drift/stop-01/readout.json"), rel(RES / "drift/stop-01/readout.json")
    st = {"chosen_rule": stop["chosen"]}
    for s in ("hard328", "fresh2026"):
        f4, c4 = stop["sets"][s]["frontier"]["seq4"], stop["sets"][s]["rules"][stop["chosen"]]["seq4"]
        st[s] = {"plain_seq4": fact(round(f4["right_24"], 1), stop["sets"][s]["n"], "problems right, mean of 24 orders", ssrc, f"{round(f4['tokens_24']):,} tokens per problem"),
                 "chosen_rule_seq4": fact(round(c4["right_24"], 1), stop["sets"][s]["n"], "problems right, mean of 24 orders", ssrc, f"{round(c4['tokens_24']):,} tokens per problem"),
                 "tokens_saved_percent": fact(round(100 * (1 - c4["tokens_24"] / f4["tokens_24"]), 1), stop["sets"][s]["n"], "percent of plain seq4 tokens", ssrc, "")}
    return {"cells": out, "summary": summary, "planted": planted, "stop": st}, fig


def copied_interventions():
    c, csrc = rj("commit1/base-01/readout.json"), rel(RES / "commit1/base-01/readout.json")
    commit = {}
    for s, d in c["sets"].items():
        for k, v in d.items():
            if k == "stored":
                commit[f"{s}/stored"] = fact(v["right"], v["n"], "problems right", csrc, f"{v['tokens']} tokens per problem, {v['cap_hits']} cap hits")
            else:
                commit[f"{s}/{k}"] = fact(v["right"], d["stored"]["n"], "problems right", csrc,
                                          f"minus stored {v['minus_stored']['points']} points; {v['long_answers']} answers cut; of those right when left alone "
                                          f"{v['long_right_stored']}, right when forced {v['long_right_committed']}", v["minus_stored"]["ci95"])
    q, qsrc = rj("day1_critique/readout.json"), rel(RES / "day1_critique/readout.json")
    crit = {}
    for m, v in q["cells"].items():
        crit[m] = {"draft_right": fact(v["draft_right_v3"], v["n"], "problems right", qsrc, "one T 1.0 draft (a fifth sample, not one of the 4)"),
                   "revised_right_v3_stated": fact(v["stated_right_v3"], v["n"], "problems right", qsrc, "v3-stated is a post-hoc grader variant"),
                   "wrong_finished_drafts": fact(v["wrong_finished_drafts"], v["n_revised"], "finished drafts scored wrong", qsrc, ""),
                   "wrong_to_right": fact(len(v["stated_wrong_to_right"]), v["wrong_finished_drafts"], "wrong finished drafts fixed by self-review", qsrc,
                                          "base: 6 of the 7 are format repairs by the README's hand read"),
                   "right_to_wrong": fact(len(v["stated_right_to_wrong"]), v["draft_right_v3"], "right drafts broken by self-review", qsrc, "")}
    s, ssrc = rj("selector/math500_base_cue-01/readout.json"), rel(RES / "selector/math500_base_cue-01/readout.json")
    sel = {k: fact(s["rows"][k]["right"], 500, "problems right of 500", ssrc, "one sample chosen among 4 with no answer key" if k != "vote" else "plurality vote",
                   None) for k in ("vote", "short1", "max_aprob", "max_mlp", "tie_short")}
    return {"commit_cue": commit, "self_review": crit, "selector": sel}, s


# ---------------------------------------------------------------- main
def main():
    facts = {"arms": {
        "base_cue": {"model": "allenai/Olmo-3-1025-7B @ a81bae42", "prompt": "plain chat prompt + assistant prefix ' line!\\n\\nOkay' (token ids 1584, 2268, 33413)",
                     "sampling": "T 1.0 / top-p 1.0, repetition penalty 1.0", "cap": 16384, "grader": "v3 (rln4_lib.grade_v3)", "samples": 4,
                     "seed": "41,000,000 + 10,000 sample + index (MATH-500); 3,000,000 + ... (hard328)", "jobs": ["abaybektursun-1114-153825-208b", "abaybektursun-1114-200457-e8e6"]},
        "rl": {"model": "allenai/Olmo-3.1-7B-RL-Zero-Math @ 364820b0 (step 2,800)", "prompt": "plain, no cue", "sampling": "T 1.0 / top-p 1.0", "cap": 16384, "grader": "v3", "samples": 4,
               "jobs": ["abaybektursun-1114-183640-e828", "abaybektursun-1114-200505-5ff2"]},
        "probe": {"reader": "the base model re-reads its own 2,000 MATH-500 samples (job abaybektursun-1114-212139-0b2b)", "layers": [12, 20, 28],
                  "positions": "last prompt token, and after 250 / 500 / 1,000 / 2,000 answer tokens", "probe": "logistic regression on standardized residual stream (4,096 dims)",
                  "split": "5 folds by problem (index mod 5); C from (0.0001, 0.001, 0.01) by an inner split by problem", "trained_on": "the label-free agreement flag (and, separately, the answer key)"},
        "drift": {"model": "Think-SFT + cue (controls: RL plain, base + cue)", "sets": "hard328 (328) + fresh2026 (136), 4 samples each, 1,856 samples",
                  "signs": ["switch", "rep50", "loopA", "zratio", "wait", "restart"], "read_at": "tokens 4,000 / 8,000 / 12,000, samples still running"}}}

    rec, state = {}, {}
    for cell, other in (("math500_base_cue", "math500_rl"), ("math500_rl", "math500_base_cue"), ("hard328_base_cue", "hard328_rl"), ("hard328_rl", "hard328_base_cue")):
        rec[cell], state[cell] = row_instruments(cell, other)
    idx, rows, y, n_new, cap, flag = state["math500_base_cue"]
    facts["self_checks"] = self_checks(y, n_new)
    heads, text = head_signs(idx, y, n_new)
    rec["math500_base_cue"].update(heads)
    facts["recomputed"] = rec

    probe, probe_fig, pm = copied_probe()
    probdep, dm = copied_probdep()
    drift_c, drift_fig = copied_drift()
    inter, sel = copied_interventions()
    facts["copied"] = {"probe": probe, "problem_dependence": probdep, "drift": drift_c, **inter}

    # recomputed against stored readouts
    mb = rec["math500_base_cue"]
    check("flag rate", round(float(flag.mean()), 4), pm["flag_rate"]); check("correct rate", round(float(y.mean()), 4), pm["correct_rate"])
    ce = rj("critic/ceiling-02/metrics.json")["base_cue"]
    check("flag = correct", round(float((flag == y).mean()), 4), ce["agreement_of_plurality_flag_with_correct"])
    sa = dm["features"]["shorter_answer"]
    w = mb["shorter_final"]["within"]
    check("shorter answer within", w["value"], sa["value"], 0.0001); check("shorter answer problems", w["n"]["problems"], sa["problems"]); check("shorter answer pairs", w["n"]["pairs"], sa["pairs"])
    check("shorter answer ci low", w["ci95"][0], sa["ci95"][0], 0.012); check("shorter answer ci high", w["ci95"][1], sa["ci95"][1], 0.012)
    sb = dm["features"]["shorter_answer_both_longer_than_1000"]
    w = mb["shorter_final_running_1000"]["within"]
    check("shorter answer, both >= 1000, within", w["value"], sb["value"], 0.0001); check("shorter answer, both >= 1000, pairs", w["n"]["pairs"], sb["pairs"])
    for t in (250, 500, 1000, 2000):                                           # the probe's counts of problems and pairs at each checkpoint
        m = n_new >= t
        check(f"samples reaching {t}", int(m.sum()), pm["checkpoints"][str(t)]["samples_reaching"])
        for target, lab in ((y, "within_correct"), (flag, "within_flag")):
            _, wn = auroc(-n_new, target, m)
            st = pm["checkpoints"][str(t)]["probe_L12"][lab]
            check(f"{lab} problems at {t}", wn[2]["problems"], st["problems"]); check(f"{lab} pairs at {t}", wn[2]["pairs"], st["pairs"])
    by = critic_ceiling.load("base_cue")
    crit = {}
    for critic, k in (("key", 4), ("key", 2), ("plurality", 4), ("plurality", 2)):
        got = critic_ceiling.run(by, critic, k, 1000, "tokens")
        want = ce[f"{critic} k={k} at 1000 tokens"]
        check(f"stop-and-restart {critic} k={k} right", got["right_of_500"], want["right_of_500"]); check(f"stop-and-restart {critic} k={k} tokens", got["tokens_per_problem"], want["tokens_per_problem"])
        crit[f"{critic}_k{k}_at_1000_tokens"] = fact(got["right_of_500"], 500, "problems right of 500, mean over sample orders", rel(RES / CELLS["math500_base_cue"] / "rows.jsonl"),
                                                    f"perfect critic ({'answer key' if critic == 'key' else 'label-free agreement flag'}) looks once at token 1,000, at most {k} samples, last kept; "
                                                    f"{got['tokens_per_problem']:,} tokens per problem")
    facts["ceiling_math500"] = ceilings("math500", "math500_base_cue", "math500_rl")
    facts["ceiling_math500"]["stop_and_restart"] = crit
    facts["ceiling_hard328"] = ceilings("hard328", "hard328_base_cue", "hard328_rl")
    check("shortest finished sample (selector short1)", facts["ceiling_math500"]["base_cue_shortest"]["value"], sel["rows"]["short1"]["right"])
    check("pass@4 (selector)", facts["ceiling_math500"]["base_cue_oracle4"]["value"], sel["pass_at_4"]["right"])

    # power of the within-problem tests
    def power(v):
        return {"value": v["value"], "ci95": v["ci95"], "problems_with_both_outcomes": v["n"]["problems"], "pairs": v["n"]["pairs"],
                "half_width": round((v["ci95"][1] - v["ci95"][0]) / 2, 4), "largest_auroc_not_excluded": v["ci95"][1]}
    pc = probe["cells"]
    facts["power"] = {
        "note": "The interval's upper end is the largest within-problem AUROC the data do not exclude; with a half-width h, a true AUROC of about 0.5 + 2h would be found "
                "(interval above 0.5) in about half of repeats, 0.5 + 2.8h in about 80 %.",
        "probe_L12_1000_flag": power(pc["probe_L12@1000/within_flag"]), "probe_L12_1000_correct": power(pc["probe_L12@1000/within_correct"]),
        "probe_L12_250_flag": power(pc["probe_L12@250/within_flag"]), "probe_L20_2000_flag": power(pc["probe_L20@2000/within_flag"]),
        "problem_dependence_1000": power(probdep["mean_d_1000"]),
        "drift_zratio_12000": power(drift_c["cells"]["Think-SFT, pooled/12000/zratio/running_within_problem"] | {"n": drift_c["cells"]["Think-SFT, pooled/12000/zratio/running_within_problem"]["n"]}),
        "shorter_final_math500_base": power(mb["shorter_final"]["within"]),
        "mixed_problems_all_samples": {c: rec[c]["shorter_final"]["within"]["n"] for c in rec}}

    # the figure: one row per instrument
    order = ["difficulty_other_model", "difficulty_own_other_samples", "length_so_far_250", "length_so_far_1000", "length_so_far_2000", "length_so_far_4000", "length_so_far_8000",
             "zratio_3000", "wait_3000", "restart_3000", "zratio_6000", "wait_6000", "restart_6000", "shorter_final", "finished", "agreement"]
    c4 = facts["ceiling_math500"]
    facts["figure"] = {
        "instruments": [mb[k] | {"key": k} for k in order] + probe_fig + drift_fig
                       + [{"label": k, "group": "token probabilities", "set": "math500_base_cue", "known_at": "token " + k.rsplit("_", 1)[1], "recomputed": False, "across": None, "within": v}
                          for k, v in probdep.items() if k.startswith(("mean_d_", "low_decile_mean_", "mean_lp_base_")) and k.rsplit("_", 1)[1] in ("250", "500", "1000")],
        "hard328_base_cue": [rec["hard328_base_cue"][k] | {"key": k} for k in order if k in rec["hard328_base_cue"]],
        "ceiling": [{"label": lab, **c4[k]} for lab, k in (("base + cue, one sample", "base_cue_single"), ("base + cue, shortest finished of 4", "base_cue_shortest"),
                                                           ("base + cue, vote over 4", "base_cue_vote"), ("base + cue, perfect critic over 2", "base_cue_oracle2"),
                                                           ("base + cue, perfect critic over 4", "base_cue_oracle4"), ("RL, one sample", "rl_single"),
                                                           ("RL, vote over 4", "rl_vote"), ("RL, perfect critic over 4", "rl_oracle4"))]}
    facts["checks_against_readouts"] = CHECKS

    # the example pair (AGENTS Results rule 6): the pair the probe readout stored, with its texts and every sign
    ex = rj("critic/probe-02/examples.json")[0]
    p = ex["good"]["problem_index"]
    i = idx.index(p)
    pair = {"problem_index": p, "set": "MATH-500", "gold": rows[i][0]["gold"], "arm": "base + cue, T 1.0 / top-p 1.0, job abaybektursun-1114-153825-208b", "probe": "layer 12 after 1,000 answer tokens, held-out fold, trained on the agreement flag",
            "probe_orders_pair_correctly": ex["ordered_right"], "sources": [rel(RES / "critic/probe-02/examples.json"), rel(RES / CELLS["math500_base_cue"] / "rows.jsonl"),
                                                                            rel(STUDY / "data/wrongstep/base_cue_answer_heads_v1.jsonl.gz")]}
    for side in ("good", "bad"):
        e = ex[side]
        s = e["sample"]
        r = rows[i][s]
        assert r["score_v3"] == e["score_v3"] == (side == "good") and r["n_new"] == e["n_tokens"]
        t = text[i][s]
        pair["right" if side == "good" else "wrong"] = {
            "sample": s, "seed": r["seed"], "score_v3": r["score_v3"], "extracted_v3": r["extracted_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"], "first_300_characters": t[:300],
            "probe_score": e["probe_score"], "agreement_flag": bool(flag[i, s]), "zratio_first_3000_chars": r4(R.zratio(t[:3000])),
            "wait_first_3000_chars": len(drift.WAIT.findall(t[:3000])), "restart_first_3000_chars": len(drift.RESTART.findall(t[:3000])), "still_running_at_token_1000": r["n_new"] >= 1000}
    (HERE / "examples.json").write_text(json.dumps([pair], indent=1, ensure_ascii=False) + "\n")
    facts["replays"] = replays()
    (HERE / "facts.json").write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n")

    print(f"{len(CHECKS)} checks against readouts pass")
    print(f"{'instrument (MATH-500, base + cue)':78s} across              within               problems/pairs")
    f = lambda v: "      -            " if v is None or v["value"] is None else f"{v['value']:.3f} " + (f"[{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}]" if v["ci95"] else "[no interval] ")
    for r in facts["figure"]["instruments"]:
        n = r["within"]["n"] or {}
        print(f"{r['label'][:76]:78s} {f(r['across'])} {f(r['within'])}  {n.get('problems')}/{n.get('pairs')}")
    for r in facts["figure"]["ceiling"]:
        print(f"{r['label']:40s} {r['value']:7.2f} {r['ci95']}")
    for k, v in facts["ceiling_math500"]["differences_points"].items():
        print(f"  {k:32s} {v['value']:+6.2f} {v['ci95']}")
    for k, v in facts["ceiling_hard328"].items():
        if isinstance(v, dict) and "value" in v:
            print(f"  hard328 {k:24s} {v['value']} {v['ci95']}")
    for k, v in facts["ceiling_hard328"]["differences_points"].items():
        print(f"  hard328 {k:32s} {v['value']:+6.2f} {v['ci95']}")


if __name__ == "__main__":
    main()
