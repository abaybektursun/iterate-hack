"""The verified data layer of the paper "The First Hundred Steps": every number recomputed from committed rows.

    uv run --no-project --with numpy python studies/rlneurons/paper-first-steps/build_facts.py

Reads only files in git (paths in SRC below; no runs/, no S3, no model). Writes, next to this file:
  facts.json      every number the paper may use: {value, n, unit, source, note}; intervals are paired bootstrap over
                  problems, 10,000 resamples, seed 0, 95 % percentile, in points, recomputed here from per-problem rows.
                  `copied_not_recomputed` lists the numbers that could only be copied from a readout (rows not in git).
                  `vs_readouts` compares each recomputed number with the stored readout; `vs_scout` with the scouts' list.
  problems.jsonl  one row per MATH-500 problem: right / cap hit / 'Okay' opening / tokens in every cell that has rows.
Fails on a missing file, a row count that is not 500, or a literal of the site page that disagrees with the rows.
Four samples per cell (ckptcue3): sample 0 of a checkpoint cell is its stored -01 folder, samples 1 to 3 are
results/ckptcue/<cell>_s123-01/rows.jsonl; the cued base and the final model have four samples in results/day1_3 (their
stored single cells T1 and T2 are a fifth run each). Every 4-sample number is recomputed from the rows and asserted against
results/ckptcue/readout3.json. Medians are rounded half up to a whole token (1,982.5 -> 1,983).

Cells (MATH-500, n = 500, cap 16,384, grader v3). T 1.0 / top-p 1.0: base_plain (T3), base_cue (T1), s100_plain,
s100_cue, s400_plain, s400_cue, final_plain (T2; step 2,800 of Olmo-3.1-7B-RL-Zero-Math). T 0.6 / top-p 0.95: base_plain,
base_cue, s100_plain, s400_plain, final_plain, only from the PROBLEMS literal of the site page (raw rows are on S3).
'Okay' opening = 'Okay' in the first 30 characters of the answer (the cue cells hold it by construction).
"""
import ast
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RL = "studies/rlneurons/"
RES = RL + "results/"
B, SEED, N = 10_000, 0, 500
SRC = {
    "t1_t3": RES + "rln4/t1_t3_items-01/per_problem.json",
    "t1_t2": RES + "rln4/t1_t2_items-01/per_problem.json",
    "ckpt": RES + "ckptcue/{}-01/per_problem.json",
    "ckpt_readout": RES + "ckptcue/readout.json",
    "ckpt_readout3": RES + "ckptcue/readout3.json",
    "ckpt_s123": RES + "ckptcue/{}_s123-01/rows.jsonl",
    "frozen": RL + "data/rln4/frozen4.json",
    "ckpt_examples": RES + "ckptcue/s0100_plain-01/examples.json",
    "s4_base_cue": RES + "day1_3/math500_base_cue-01/rows.jsonl",
    "s4_final": RES + "day1_3/math500_rl-01/rows.jsonl",
    "grader": RES + "rln4/grader_v3/readout.json",
    "page": "tools/finding_rl_learns_the_opening_first.py",
    "capcounts": "studies/theory/results/engine/round-04/replication/capcounts.out",
    "handoff_rows": RES + "handoff/{}-01/rows.jsonl",
    "handoff_plan": RL + "data/handoff/plan_v1.json",
    "handoff_readout": RES + "handoff/unbiased-01/readout.json",
    "selfopen_rows": "studies/theory/results/experiments/selfopen-01/per_problem.json",
    "selfopen_metrics": "studies/theory/results/experiments/selfopen-01/metrics.json",
    "wsp2": RES + "wsp2/full500/{}-01/per_problem.json",
    "wsp2_readout": RES + "wsp2/readout.json",
    "code1": RES + "code1/readout.json",
    "weights": RES + "xreward/overlap_steps-01/readout.json",
}
SCOUT = {  # the scouts' list in the task, unverified; compared below
    "right_T10": {"base_plain": 224, "base_cue": 410, "s100_plain": 418, "s100_cue": 427, "s400_plain": 436, "s400_cue": 431, "final_plain": 463},
    "s100_plain - base_cue": [1.6, -2.0, 5.2], "s100_cue - base_cue": [3.4, 0.2, 6.6],
    "okay30": {"base_plain_T06": 193, "s100_plain_T06": 478, "s100_plain_T10": 383},
    "gap53": [8, 18, 27], "cap_T06": [65, 103, 98, 19],
    "handoff_50": [8.4, 1.3, 15.5, 12.9], "handoff_75_rl_on_base_vs_base_own": [91, 90],
    "selfopen": [411, 410, 224, 216], "selfopen_b": [332, 137], "handedit": [224, 397, 204], "code_mathcue": [19.3, 14.3, 24.3, 538],
}


def load(rel):
    p = ROOT / rel
    return [json.loads(x) for x in p.read_text().splitlines()] if rel.endswith(".jsonl") else json.loads(p.read_text())


def by_index(rows, n=N):
    rows = sorted(rows, key=lambda r: r["problem_index"])
    assert [r["problem_index"] for r in rows] == list(range(n)), "rows are not one per problem"
    return rows


def fact(value, n, unit, source, note=""):
    return {"value": value, "n": n, "unit": unit, "source": source, "note": note}


def med(v):
    """Median, rounded half up to a whole number (1,982.5 -> 1,983): the one rounding rule for every median."""
    return int(math.floor(float(np.median(v)) + 0.5))


def wilson(k, n, z=1.959964):
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def boot(x, y):
    """Paired bootstrap over problems of mean(x - y) in points: [point, low, high]; the same resamples in every call."""
    d = np.asarray(x, float) - np.asarray(y, float)
    idx = np.random.default_rng(SEED).integers(0, len(d), size=(B, len(d)))
    lo, hi = np.percentile(100 * d[idx].mean(1), [2.5, 97.5])
    return [round(100 * d.mean(), 2), round(float(lo), 2), round(float(hi), 2)]


def diff(x, y, source, note=""):
    x, y = np.asarray(x, float), np.asarray(y, float)
    p = boot(x, y)
    return {"value": p[0], "ci95": p[1:], "n": len(x), "unit": "points (x minus y), paired bootstrap over problems",
            "x_mean_right": round(float(x.sum()), 2), "y_mean_right": round(float(y.sum()), 2),
            "only_x": int(((x == 1) & (y == 0)).sum()), "only_y": int(((x == 0) & (y == 1)).sum()), "source": source, "note": note}


def literal(tree, name):
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == name)
    return node.value


def main():
    facts = {"_about": {"script": RL + "paper-first-steps/build_facts.py", "bootstrap": f"paired over problems, {B} resamples, seed {SEED}, 95 % percentile",
                        "set": "MATH-500, n 500, cap 16,384 tokens, grader v3 (studies/rlneurons/lib/rln4_lib.grade_v3)",
                        "models": "base allenai/Olmo-3-1025-7B; checkpoints allenai/Olmo-3.1-7B-RL-Zero-Math at step_0100 (0a45720c), step_0400 (897c0ce4), final (364820b0, step 2,800)",
                        "cue": "' line!\\n\\nOkay', three prefilled tokens (Wang et al., arXiv 2610.06851)", "sources": SRC}}

    # ---------- T 1.0 cells, one stored sample each ----------
    t13, t12 = by_index(load(SRC["t1_t3"])), by_index(load(SRC["t1_t2"]))
    assert all((a["t1_right"], a["t1_cap_hit"]) == (b["t1_right"], b["t1_cap_hit"]) for a, b in zip(t13, t12)), "T1 differs between the two files"
    cell = {  # name -> per problem (right, cap, tokens, opening or None)
        "base_plain": [(r["t3_right"], r["t3_cap_hit"], r["t3_generated_tokens"], r["t3_start"][:30]) for r in t13],
        "base_cue": [(r["t1_right"], r["t1_cap_hit"], r["t1_generated_tokens"], r["t1_start"][:30]) for r in t13],
        "final_plain": [(r["t2_right"], r["t2_cap_hit"], r["t2_generated_tokens"], None) for r in t12],
    }
    src = {"base_plain": SRC["t1_t3"] + " t3_*", "base_cue": SRC["t1_t3"] + " t1_*", "final_plain": SRC["t1_t2"] + " t2_*"}
    seeds = {"base_plain": load(SRC["frozen"])["seeds"]["T3"], "base_cue": 41000000, "final_plain": 45000000}
    for name, folder in (("s100_plain", "s0100_plain"), ("s100_cue", "s0100_cue"), ("s400_plain", "s0400_plain"), ("s400_cue", "s0400_cue")):
        rel = SRC["ckpt"].format(folder)
        cell[name] = [(r["score_v3"], r["cap_hit"], r["n_generated"], r["opening"]) for r in by_index(load(rel))]
        src[name] = rel
        seeds[name] = load(rel.replace("per_problem", "run"))["seed"]
    ORDER = ["base_plain", "base_cue", "s100_plain", "s100_cue", "s400_plain", "s400_cue", "final_plain"]
    X = {k: np.array([r[0] for r in v]) for k, v in cell.items()}

    # the site page's literals: T 0.6 rows (PROBLEMS) and the T 1.0 copy (PROBLEMS1), cross-checked with the rows above
    tree = ast.parse((ROOT / SRC["page"]).read_text())
    P06, P10 = ast.literal_eval(literal(tree, "PROBLEMS")), ast.literal_eval(literal(tree, "PROBLEMS1"))
    assert [p[0] for p in P06] == [p[0] for p in P10] == list(range(N))
    K10 = ["base_plain", "base_cue", "s100_plain", "s400_plain", "final_plain", "s100_cue", "s400_cue"]  # KEYS1 of the page
    for p in P10:
        for j, k in enumerate(K10):
            r = cell[k][p[0]]
            assert p[1][j] == ("c" if r[1] else "r" if r[0] else "w") and p[3][j] == r[2], f"PROBLEMS1 disagrees with the rows: {k} {p[0]}"
            if r[3] is not None:
                assert (p[2][j] == "1") == ("Okay" in r[3]), f"PROBLEMS1 opening disagrees: {k} {p[0]}"
    final_okay = [p[2][4] == "1" for p in P10]  # the only T 1.0 column whose text is not in a results/ file
    final_start = [p[5][4] for p in P10]

    def okay(k, i):
        return final_okay[i] if k == "final_plain" else "Okay" in cell[k][i][3]

    def opening_class(s):
        s = s.replace("\\n", "\n")
        if "Okay" in s[:30]:
            return "Okay"
        if "Alright" in s[:30]:
            return "Alright"
        return "(empty)" if not s.strip() else "other"

    cells = {}
    for k in ORDER:
        v, x = cell[k], X[k]
        tok = np.array([r[2] for r in v])
        fin = np.array([not r[1] for r in v])
        ok = np.array([okay(k, i) for i in range(N)])
        starts = final_start if k == "final_plain" else [r[3] for r in v]
        cells[k] = {
            "right": fact(int(x.sum()), N, "problems right of 500, ONE sample (the stored single cell)", src[k], f"seed {seeds[k]}; Wilson 95 % {wilson(int(x.sum()), N)} %"),
            "cap_hits": fact(int((~fin).sum()), N, "answers cut at 16,384 tokens", src[k], f"{int(x[~fin].sum())} of them still scored right"),
            "cut_off_scored_right": fact(int(x[~fin].sum()), int((~fin).sum()), "answers cut at the cap that grader v3 still scores right (a boxed answer before the cap); "
                                         "a cut-off answer is NOT counted wrong by rule", src[k]),
            "okay30": fact(int(ok.sum()), N, "answers with 'Okay' in the first 30 characters",
                           SRC["page"] + " PROBLEMS1 (copied there from T2.jsonl, not in git)" if k == "final_plain" else src[k],
                           "by construction for a cue cell" if k.endswith("cue") else ""),
            "right_by_opening": fact({"okay": [int(x[ok].sum()), int(ok.sum())], "not_okay": [int(x[~ok].sum()), int((~ok).sum())]}, N, "[right, n]", src[k]),
            "opening_classes": fact(dict(Counter(opening_class(s) for s in starts).most_common()), N, "answers by the first 30 characters: 'Okay', else 'Alright', else empty, else other", src[k],
                                    "final_plain from the page literal's 90-character start"),
            "first_line_top5": fact(Counter(s.split("\n")[0][:28] for s in starts).most_common(5), N, "most common text before the first newline (the model first finishes the prompt's last sentence)", src[k]),
            "empty_answers": fact(None if k == "final_plain" else sum(not s for s in starts), N, "answers with no text", src[k]),
            "tokens_mean": fact(round(float(tok.mean()), 1), N, "generated tokens per problem (cap hits included; the cue's 3 tokens not counted)", src[k]),
            "tokens_median": fact(med(tok), N, "generated tokens, median rounded half up", src[k]),
            "tokens_median_finished": fact(med(tok[fin]), int(fin.sum()), "generated tokens, answers that finished, sample 0; median rounded half up", src[k]),
            "tokens_median_finished_right": fact(med(tok[fin & (x == 1)]), int((fin & (x == 1)).sum()), "generated tokens, finished and right; median rounded half up", src[k]),
        }
    facts["cells_T10"] = cells
    K5 = ["base_plain", "base_cue", "s100_plain", "s400_plain", "final_plain"]  # KEYS of the page, the order of its starts
    facts["okay_wider_window"] = {
        "T10_first_90_chars": fact({k: sum("Okay" in p[5][j] for p in P10) for j, k in enumerate(K5)}, N, "answers with 'Okay' in the stored start (cut at a word end, at most 90 characters)",
                                   SRC["page"] + " PROBLEMS1 starts", "the only wider window in git at T 1.0; the page copied the starts from raw files that are not in git"),
        "T06_first_90_chars": fact({k: sum("Okay" in p[7][j] for p in P06) for j, k in enumerate(K5)}, N, "the same at T 0.6 / top-p 0.95", SRC["page"] + " PROBLEMS starts"),
        "T10_s100_plain_not_okay30_but_okay90": fact([sum("Okay" in p[5][2] and p[2][2] == "0" for p in P10), sum(p[2][2] == "0" for p in P10)], N,
                                                     "[step-100 plain answers without 'Okay' in 30 characters that have it within 90, all without it in 30]", SRC["page"] + " PROBLEMS1"),
    }

    pairs = [("s100_plain", "base_cue"), ("s100_cue", "base_cue"), ("s100_cue", "s100_plain"), ("s400_plain", "base_cue"), ("s400_cue", "s400_plain"),
             ("s400_cue", "base_cue"), ("s400_plain", "s100_plain"), ("s400_cue", "s100_cue"), ("final_plain", "s400_plain"), ("final_plain", "s100_plain"),
             ("final_plain", "base_cue"), ("base_cue", "base_plain"), ("s100_plain", "base_plain")]
    facts["differences_T10"] = {f"{a} - {b}": diff(X[a], X[b], f"{src[a]} ; {src[b]}", "one sample per cell; seeds: plain cells 45000000, cue cells 41000000")
                                for a, b in pairs}

    # ---------- four samples per cell: cued base and final model (Day-1 #3 jobs), three checkpoint cells (ckptcue3) ----------
    def four(rows, sample0=None):
        """4 x 500 arrays from attempt-0 rows; sample0 = the stored cell, when the rows hold only samples 1 to 3."""
        rows = [r for r in rows if r["attempt"] == 0]
        first = 1 if sample0 else 0
        assert sorted((r["sample"], r["problem_index"]) for r in rows) == [(s_, i) for s_ in range(first, 4) for i in range(N)], "rows are not one per sample and problem"
        m, cap, tok, sd = np.zeros((4, N), int), np.zeros((4, N), bool), np.zeros((4, N), int), [None] * 4
        ok = np.zeros((4, N), bool) if sample0 else None  # only the ckptcue3 rows store the first 30 characters
        for r in rows:
            s_, i = r["sample"], r["problem_index"]
            # ckptcue3 rows: n_new leaves out the end token that sample 0's n_generated counts (asserted below against readout3's token means)
            m[s_, i], cap[s_, i], tok[s_, i] = r["score_v3"], r["cap_hit"], r["n_new"] + (1 if sample0 and not r["cap_hit"] else 0)
            if i == 0:
                sd[s_] = r["seed"]
            if ok is not None:
                ok[s_, i] = "Okay" in r["opening"]
        if sample0:
            m[0], cap[0], tok[0], ok[0] = [r[0] for r in sample0], [r[1] for r in sample0], [r[2] for r in sample0], ["Okay" in r[3] for r in sample0]
        return {"right": m, "cap": cap, "tok": tok, "ok": ok, "seeds": sd}

    S4 = {"base_cue": four(load(SRC["s4_base_cue"])), "final_plain": four(load(SRC["s4_final"]))}
    src4 = {"base_cue": SRC["s4_base_cue"] + " (attempt 0)", "final_plain": SRC["s4_final"] + " (attempt 0)"}
    for name, folder in (("s100_plain", "s0100_plain"), ("s100_cue", "s0100_cue"), ("s400_plain", "s0400_plain")):
        S4[name] = four(load(SRC["ckpt_s123"].format(folder)), cell[name])
        S4[name]["seeds"][0] = seeds[name]
        src4[name] = src[name] + " (sample 0) ; " + SRC["ckpt_s123"].format(folder) + " (samples 1 to 3)"
    K4 = ["base_cue", "s100_plain", "s100_cue", "s400_plain", "final_plain"]
    P4 = {k: S4[k]["right"].mean(0) for k in K4}  # per problem: share of the four samples that are right
    c4 = {}
    for k in K4:
        m, cap, tok, ok = (S4[k][f] for f in ("right", "cap", "tok", "ok"))
        c4[k] = {
            "right_per_sample": fact([int(v) for v in m.sum(1)], N, "problems right of 500, samples 0 to 3", src4[k], f"seed of problem 0 per sample {S4[k]['seeds']} (seed + 10000 sample + index)"),
            "mean_right": fact(round(float(m.sum(1).mean()), 2), N, "problems right of 500, mean of the four samples", src4[k]),
            "cap_hits_per_sample": fact([int(v) for v in cap.sum(1)], N, "answers cut at 16,384 tokens, per sample", src4[k], f"mean {cap.sum(1).mean():.2f}"),
            "cut_off_scored_right_per_sample": fact([int(v) for v in (m * cap).sum(1)], int(cap.sum()), "cut-off answers that grader v3 scores right, per sample", src4[k]),
            "tokens_mean": fact(round(float(tok.mean()), 1), 4 * N, "generated tokens per answer, four samples pooled", src4[k],
                                "n_new of the Day-1 #3 rows" if S4[k]["ok"] is None else "n_generated (end token counted; samples 1 to 3 = n_new + 1 for a finished answer)"),
            "tokens_median_finished_pooled": fact(med(tok[~cap]), int((~cap).sum()), "generated tokens, finished answers of the four samples pooled; median rounded half up", src4[k],
                                                  f"per sample {[med(tok[j][~cap[j]]) for j in range(4)]}"),
            "okay30_per_sample": fact(None if ok is None else [int(v) for v in ok.sum(1)], N, "answers with 'Okay' in the first 30 characters, per sample", src4[k],
                                      "rows of the Day-1 #3 jobs store no text" if ok is None else f"pooled {int(ok.sum())} of {4 * N}"),
            "okay90": fact(None, N, "'Okay' within 90 characters", src4[k], "not computable: the new rows keep 30 characters of each answer; the 90-character counts exist for sample 0 only (okay_wider_window)"),
        }
    facts["cells_T10_four_samples"] = c4
    pairs4 = [("s100_plain", "base_cue"), ("s100_cue", "base_cue"), ("s100_cue", "s100_plain"), ("s400_plain", "s100_plain"), ("final_plain", "s400_plain"),
              ("final_plain", "s100_plain"), ("final_plain", "base_cue"), ("s400_plain", "base_cue")]
    facts["differences_T10_four_sample_means"] = {f"{a} - {b}": diff(P4[a], P4[b], f"{src4[a]} ; {src4[b]}", "per-problem mean of four samples on both sides; only_x / only_y = problems right in all four of one and none of the other")
                                                  for a, b in pairs4}

    noise = {}
    for k in K4:
        m = S4[k]["right"]
        per = [int(v) for v in m.sum(1)]
        flips = [int(((m[a] == 1) & (m[b] == 0)).sum()) for a in range(4) for b in range(4) if a != b]
        pd = [abs(per[a] - per[b]) for a in range(4) for b in range(a + 1, 4)]
        noise[k] = {
            "right_per_sample": fact(per, N, "problems right of 500, samples 0 to 3", src4[k], "sample s has seed + 10000 s"),
            "range_four_samples": fact([min(per), max(per)], N, "lowest and highest right of 500 over the four samples", src4[k], f"spread {max(per) - min(per)} problems"),
            "sd_between_samples": fact(round(float(np.std(per, ddof=1)), 2), 4, "problems, sd of right of 500 over samples 0 to 3", src4[k]),
            "mean_abs_pair_difference": fact(round(float(np.mean(pd)), 2), 6, "problems, |right_a - right_b| over the 6 sample pairs", src4[k]),
            "flips_between_two_samples": fact(round(float(np.mean(flips)), 1), 12, "problems right in one sample and wrong in another, mean over ordered pairs (each direction)", src4[k],
                                              f"min {min(flips)}, max {max(flips)}: the churn to expect between two cells of ONE model"),
            "cap_hits_per_sample": fact([int(v) for v in S4[k]["cap"].sum(1)], N, "cap hits", src4[k]),
            "tokens_mean_per_sample": fact([round(float(v), 1) for v in S4[k]["tok"].mean(1)], N, "generated tokens per problem", src4[k]),
            "problems_by_right_count": fact([int((m.sum(0) == j).sum()) for j in range(5)], N, "problems right in 0, 1, 2, 3, 4 of 4 samples", src4[k]),
        }
    for k in ("base_cue", "final_plain"):  # their stored single cell (T1, T2) is a fifth run: sample 0's seeds in another job
        allc = noise[k]["right_per_sample"]["value"] + [int(X[k].sum())]
        noise[k]["with_stored_single_cell"] = fact(allc, N, "the four samples and the stored cell (T1 or T2)", src[k])
        noise[k]["range"] = fact([min(allc), max(allc)], N, "lowest and highest right of 500 over the five runs", src[k], f"spread {max(allc) - min(allc)} problems = {(max(allc) - min(allc)) / 5:.1f} points")
    stored_vs_s0 = {k: diff(X[k], S4[k]["right"][0], src[k] + " ; day1_3 sample 0", "same model, same seeds, another job: a null difference") for k in ("base_cue", "final_plain")}
    facts["seed_noise_T10"] = {**noise, "stored_cell_minus_sample0_same_seeds": stored_vs_s0}

    bc4, fn4 = P4["base_cue"], P4["final_plain"]
    note4 = "SUPERSEDED by differences_T10_four_sample_means. x = one sample; y = per-problem mean of 4 samples (day1_3, attempt 0). Covers all of x's sample noise only through the problem resampling"
    facts["one_sample_vs_four_sample_reference"] = {
        "s100_plain - base_cue_mean4": diff(X["s100_plain"], bc4, src["s100_plain"] + " ; " + SRC["s4_base_cue"], note4),
        "s100_cue - base_cue_mean4": diff(X["s100_cue"], bc4, src["s100_cue"] + " ; " + SRC["s4_base_cue"], note4),
        "s400_plain - base_cue_mean4": diff(X["s400_plain"], bc4, src["s400_plain"] + " ; " + SRC["s4_base_cue"], note4),
        "final_mean4 - s400_plain": diff(fn4, X["s400_plain"], SRC["s4_final"] + " ; " + src["s400_plain"], note4),
        "final_mean4 - s100_plain": diff(fn4, X["s100_plain"], SRC["s4_final"] + " ; " + src["s100_plain"], note4),
        "final_mean4 - base_cue_mean4": diff(fn4, bc4, SRC["s4_final"] + " ; " + SRC["s4_base_cue"], "both sides 4-sample means"),
        "s100_plain_rank_among_base_cue_runs": fact(f"{int(X['s100_plain'].sum())} against base + cue runs {sorted(noise['base_cue']['with_stored_single_cell']['value'])}", N, "right of 500", src["s100_plain"]),
    }

    # ---------- per-problem transitions along base + cue -> step 100 -> step 400 -> final (plain) ----------
    chain = ["base_cue", "s100_plain", "s400_plain", "final_plain"]
    tr = {}
    for a, b in list(zip(chain, chain[1:])) + [("base_cue", "final_plain"), ("base_cue", "s400_plain"), ("s100_plain", "final_plain"),
                                                ("base_plain", "base_cue"), ("base_plain", "s100_plain"), ("s100_plain", "s100_cue"), ("s400_plain", "s400_cue")]:
        g, l = int(((X[a] == 0) & (X[b] == 1)).sum()), int(((X[a] == 1) & (X[b] == 0)).sum())
        tr[f"{a} -> {b}"] = fact({"gained": g, "lost": l, "net": g - l, "both_right": int((X[a] & X[b]).sum()), "both_wrong": int(((X[a] == 0) & (X[b] == 0)).sum())},
                                 N, "problems", f"{src[a]} ; {src[b]}")
    pat = Counter("".join("r" if X[k][i] else "w" for k in chain) for i in range(N))
    tr["patterns"] = fact(dict(sorted(pat.items(), key=lambda t: -t[1])), N, "problems by outcome in base_cue, s100_plain, s400_plain, final_plain (r right, w wrong)", "the four cells")
    tr["monotone_share"] = fact(sum(v for p, v in pat.items() if p in ("rrrr", "wrrr", "wwrr", "wwwr", "wwww")), N, "problems whose outcome never goes from right to wrong along the chain", "patterns")
    win = (X["base_cue"] == 0) & (X["final_plain"] == 1)
    lose = (X["base_cue"] == 1) & (X["final_plain"] == 0)
    tr["final_only_problems"] = fact({"n": int(win.sum()), "right_at_s100": int(X["s100_plain"][win].sum()), "right_at_s400": int(X["s400_plain"][win].sum()),
                                      "right_at_both": int((X["s100_plain"] & X["s400_plain"])[win].sum()), "right_at_neither": int(((X["s100_plain"] == 0) & (X["s400_plain"] == 0))[win].sum())},
                                     int(win.sum()), "problems the final model has right and base + cue wrong", "the four cells")
    tr["base_cue_only_problems"] = fact({"n": int(lose.sum()), "right_at_s100": int(X["s100_plain"][lose].sum()), "right_at_s400": int(X["s400_plain"][lose].sum())},
                                        int(lose.sum()), "problems base + cue has right and the final model wrong", "the four cells")
    r = [int(X[k].sum()) for k in chain]
    tr["net_gap_split"] = fact({"gap": r[3] - r[0], "by_step_100": r[1] - r[0], "step_100_to_400": r[2] - r[1], "after_step_400": r[3] - r[2]}, N,
                               "net problems (differences of right counts)", "the four cells",
                               "net counts, not a partition of problems: see gained / lost per stage, and seed_noise_T10 flips_between_two_samples for the churn of one model")
    for a, b in list(zip(chain, chain[1:])) + [("base_cue", "final_plain")]:
        pa, pb = P4[a], P4[b]
        e = {"gained": round(float(((1 - pa) * pb).sum()), 2), "lost": round(float((pa * (1 - pb)).sum()), 2)}
        g16 = [int(((S4[a]["right"][i] == 0) & (S4[b]["right"][j] == 1)).sum()) for i in range(4) for j in range(4)]
        l16 = [int(((S4[a]["right"][i] == 1) & (S4[b]["right"][j] == 0)).sum()) for i in range(4) for j in range(4)]
        o = {"gained": round(float(np.mean(g16)), 2), "lost": round(float(np.mean(l16)), 2)}
        assert o == e, "the mean over all 16 sample pairs is, by algebra, the independent expectation"
        pool = (pa + pb) / 2  # the null of no change: one per-problem rate for both stages, from the 8 samples
        same = round(float((8 / 7) * (pool * (1 - pool)).sum()), 2)
        t = tr[f"{a} -> {b}"]
        extra = {"expected_independent": e, "observed_mean": o, "observed_range_16_pairs": {"gained": [min(g16), max(g16)], "lost": [min(l16), max(l16)]},
                 "same_rates_null": {"gained": same, "lost": same}}
        t["value"].update(extra)  # figs.py reads value.expected_independent
        t.update(extra)
        t["note"] = ("gained / lost / net / both_*: sample 0 of each stage (the stored single cells). expected_independent: sum over problems of (1 - pA) pB and pA (1 - pB), "
                     "p = share right of the model's four samples. observed_mean: mean over the 16 pairs of one sample of A and one of B; identical to expected_independent by algebra "
                     "(it is no test). same_rates_null: gained = lost expected if both stages had the same per-problem rate (pooled over 8 samples, 8/7 sum p(1 - p)): the churn with no change")
    f4, s4, b4 = (S4[k]["right"].sum(0) for k in ("final_plain", "s100_plain", "base_cue"))
    gain = {"majority": (f4 >= 3) & (s4 <= 1), "mean_difference_at_least_half": f4 - s4 >= 2}
    tr["final_gains_over_s100_four_samples"] = fact(
        {name: {"n": int(sel.sum()), "base_cue_right_in_at_least_one_of_4": int((b4[sel] >= 1).sum()), "base_cue_never_right": int((b4[sel] == 0).sum()),
                "base_cue_right_in_at_least_3_of_4": int((b4[sel] >= 3).sum())} for name, sel in gain.items()}, N,
        "problems the final model gains over step 100 plain. majority (the main rule): final right in at least 3 of 4 samples and step 100 right in at most 1 of 4; "
        "mean_difference_at_least_half: final right in at least 2 more samples than step 100", "the four samples of final_plain, s100_plain, base_cue")
    facts["transitions_T10"] = tr

    # ---------- T 0.6 / top-p 0.95, from the site page's PROBLEMS literal ----------
    K06 = ["base_plain", "base_cue", "s100_plain", "s400_plain", "final_plain"]
    data = literal(tree, "DATA")
    page = {k.value: ast.literal_eval(v) for k, v in zip(data.keys, data.values) if isinstance(k, ast.Constant) and k.value in ("okay", "cut", "right", "right_cut", "okay400", "median_len")}
    capc = json.loads((ROOT / SRC["capcounts"]).read_text())
    gr = load(SRC["grader"])["cells"]
    t06 = {}
    for j, k in enumerate(K06):
        out = [p[3][j] for p in P06]
        tok = np.array([p[5][j] for p in P06])
        fin = np.array([o != "c" for o in out])
        okc = sum(p[4][j] == "1" for p in P06)
        assert okc == page["okay"][j] and out.count("c") == page["cut"][j] and out.count("r") + page["right_cut"][j] == page["right"][j], f"page literal inconsistent: {k}"
        t06[k] = {
            "right": fact(page["right"][j], N, "problems right of 500, sample 0", SRC["page"] + " DATA['right']",
                          f"COPIED (rows on S3). Per problem the literal gives finished-and-right ({out.count('r')}); {page['right_cut'][j]} cut-off answers also scored right"),
            "cap_hits": fact(out.count("c"), N, "answers cut at 16,384 tokens", SRC["page"] + " PROBLEMS"),
            "okay30": fact(okc, N, "answers with 'Okay' in the first 30 characters", SRC["page"] + " PROBLEMS"),
            "okay400": fact(page["okay400"][j], N, "answers with 'Okay' in the first 400 characters", SRC["page"] + " DATA['okay400']", "COPIED"),
            "tokens_mean": fact(round(float(tok.mean()), 1), N, "n_new per problem", SRC["page"] + " PROBLEMS"),
            "tokens_median_finished": fact(med(tok[fin]), int(fin.sum()), "n_new, answers that finished; median rounded half up", SRC["page"] + " PROBLEMS"),
        }
    for k, m in (("base_plain", "base"), ("s100_plain", "s0100"), ("s400_plain", "s0400"), ("final_plain", "s2800")):
        assert t06[k]["cap_hits"]["value"] == capc[m]["math500"]["cap_hits"], f"cap hits differ from capcounts.out: {k}"
    assert (t06["base_plain"]["right"]["value"], t06["base_cue"]["right"]["value"]) == (gr["base_plain_0.6"]["right_v3"], gr["base_opener_0.6"]["right_v3"])
    f06 = {k: np.array([p[3][j] == "r" for p in P06], int) for j, k in enumerate(K06)}
    t06["differences_finished_right"] = {f"{a} - {b}": diff(f06[a], f06[b], SRC["page"] + " PROBLEMS",
                                                             "on finished-and-right (cut-off answers count wrong): differs from the v3 counts by at most 6 problems per cell")
                                         for a, b in (("s100_plain", "base_cue"), ("s400_plain", "s100_plain"), ("final_plain", "s400_plain"), ("base_cue", "base_plain"))}
    lit = lambda k: K06.index(k)
    t06["s100_plain_vs_base_cue"] = fact(
        {"right_v3": [page["right"][lit("s100_plain")], page["right"][lit("base_cue")]], "finished_and_right": [int(f06["s100_plain"].sum()), int(f06["base_cue"].sum())],
         "finished_and_right_difference_points": [t06["differences_finished_right"]["s100_plain - base_cue"]["value"]] + t06["differences_finished_right"]["s100_plain - base_cue"]["ci95"],
         "cap_hits": [t06["s100_plain"]["cap_hits"]["value"], t06["base_cue"]["cap_hits"]["value"]], "loop_count_base_cue_cap_hits": None},
        N, "[step 100 plain, base + cue], one sample each, T 0.6 / top-p 0.95, cap 16,384", SRC["page"] + " DATA, PROBLEMS",
        "the interval is on finished-and-right (per-problem right-of-500 is not in git; the two counts differ by the cut-off answers scored right). "
        "Loops: NONE stored for this cell. No loop count of the cued base's 119 cut-offs at T 0.6 / top-p 0.95 on MATH-500 is in git; the nearest are the same model at T 0.6 / top-p 1.0 "
        "(71 rule-A loops, 70 among its 98 cap hits; README Day-1 table) and at T 0.6 / top-p 0.95 on the harder 328 (132 loops of 173 cap hits)")
    t06["note"] = "rl_0.6 = 464 in results/rln4/grader_v3/readout.json is another run (n13) of the final model; the row here (462) is r3/s2800-01"
    facts["cells_T06"] = t06

    # ---------- hand-off (base + cue against the FINAL model, unbiased subset of the hard pool) ----------
    U = sorted(load(SRC["handoff_plan"])["unbiased"])
    hr = {}
    for f in ("base", "rl"):
        for r in load(SRC["handoff_rows"].format(f)):
            hr[r["finisher"], r["writer"], r["cut"], r["problem_index"]] = r["score_v3"]
    col = lambda f, w, c: np.array([hr[f, w, c, i] for i in U])
    hs = SRC["handoff_rows"].format("{base,rl}") + " ; " + SRC["handoff_plan"] + " unbiased"
    ho = {"_note": "writer = whose stored answer (day1_3 sample 0) is cut at 25 / 50 / 75 % of its tokens; finisher = who writes the rest. RL here is the final model, not step 100. "
                   "n 155 = the problems in the pool (base right in at most 3 of 4 samples) whatever base sample 0 did"}
    for c in (25, 50, 75):
        gap, rec, loss = diff(col("rl", "rl", c), col("base", "base", c), hs), diff(col("base", "rl", c), col("base", "base", c), hs), diff(col("rl", "base", c), col("rl", "rl", c), hs)
        ho[f"cut_{c}"] = {"right": fact({f"{f}_finishes_{w}": int(col(f, w, c).sum()) for f in ("base", "rl") for w in ("base", "rl")}, len(U), "right of 155", hs),
                          "rl_own - base_own": gap, "base_on_rl_prefix - base_own": rec, "rl_on_base_prefix - rl_own": loss,
                          "rl_on_base_prefix - base_own": diff(col("rl", "base", c), col("base", "base", c), hs),
                          "recovered_percent": fact(round(100 * rec["value"] / gap["value"], 1), len(U), "% of the own-prefix gap that the base recovers on an RL prefix", hs, "ratio of two noisy differences; no interval")}
    hrows = [r for f in ("base", "rl") for r in load(SRC["handoff_rows"].format(f))]
    plan = load(SRC["handoff_plan"])
    assert plan["pool_rule"] == "base right in at most 3 of 4 stored samples (attempt 0, v3)"
    assert sorted(plan["pool"]) == [i for i in range(N) if S4["base_cue"]["right"][:, i].sum() <= 3], "the pool is not the problems the cued base fails at least once in four samples"
    assert U == [i for i in range(N) if S4["base_cue"]["right"][1:, i].sum() <= 2], "U is not the problems the cued base fails in at least one of samples 1 to 3"
    ho["pool"] = fact({"pool": len(plan["pool"]), "unbiased": len(U)}, N, "problems", SRC["handoff_plan"],
                      "pool = MATH-500 problems the cued base gets wrong in at least one of its four stored samples (asserted against the day1_3 rows); unbiased = wrong in at least one of samples 1 to 3, "
                      "so membership does not depend on sample 0, which supplies the prefixes. The 16,384 cap counts the prefix tokens (README hand-off section)")
    for name, ids in (("pool_183", set(plan["pool"])), ("unbiased_155", set(U))):
        d = {}
        for c in (25, 50, 75):
            q = lambda f, w: {r["problem_index"]: r for r in hrows if (r["finisher"], r["writer"], r["cut"]) == (f, w, c) and r["problem_index"] in ids}
            bb, br, rb, rr = q("base", "base"), q("base", "rl"), q("rl", "base"), q("rl", "rl")
            assert len(bb) == len(br) == len(rb) == len(rr) == len(ids)
            right_rl = [r for r in br.values() if r["stratum"] == "right"]
            wrong = [r for r in br.values() if not r["score_v3"]]
            d[f"cut_{c}"] = {"rl_right_prefixes_already_holding_the_answer": [sum(r["prefix_has_right"] for r in right_rl), len(right_rl)],
                             "base_wrong_on_rl_prefix_that_are_cap_hits": [sum(r["cap_hit"] for r in wrong), len(wrong)],
                             "rl_prefix_gives_base": sum(br[i]["score_v3"] and not bb[i]["score_v3"] for i in ids), "rl_prefix_costs_base": sum(bb[i]["score_v3"] and not br[i]["score_v3"] for i in ids),
                             "base_prefix_costs_rl": sum(rr[i]["score_v3"] and not rb[i]["score_v3"] for i in ids), "base_prefix_gives_rl": sum(rb[i]["score_v3"] and not rr[i]["score_v3"] for i in ids)}
        ho["prefix_detail_" + name] = fact(d, len(ids), "counts of problems; [k, n] pairs are k of n. gives / costs: right on the other model's prefix and wrong on its own, and the reverse", hs)
    facts["handoff"] = ho

    # ---------- the base opens itself (selfopen-01) ----------
    so = by_index(load(SRC["selfopen_rows"]))
    sm = load(SRC["selfopen_metrics"])
    g = lambda k, rows=so: np.array([r[k] for r in rows])
    b = [r for r in so if r["source"] == "regenerated" and r["any_self_open"]]
    ss = SRC["selfopen_rows"]
    facts["selfopen"] = {
        "right": fact({"self_open": int(g("score_main").sum()), "control_no_okay": int(g("score_control").sum()), "base_cue_T1": int(g("score_t1").sum()), "base_plain_T3": int(g("score_t3").sum())}, N, "right of 500", ss,
                      "main: the base's own first draw (of at most 32) of 24 tokens that has '\\nOkay' in its first 60 characters, continued by the base; 94 problems reuse the stored plain answer because it already opened so"),
        "self_open - base_cue": diff(g("score_main"), g("score_t1"), ss),
        "self_open - base_plain": diff(g("score_main"), g("score_t3"), ss, "not independent on the 94 stored problems (same answer in both arms)"),
        "resampled_problems": fact({"n": len(b), "self_open": int(g("score_main", b).sum()), "control": int(g("score_control", b).sum()), "base_cue_T1": int(g("score_t1", b).sum()), "base_plain_T3": int(g("score_t3", b).sum())}, len(b), "right, problems regenerated that found an opening", ss),
        "resampled: self_open - control": diff(g("score_main", b), g("score_control", b), ss),
        "self_open_rate": fact(sm["draws"]["self_open_rate_all_draws"], sm["draws"]["n_regenerated"] * sm["draws"]["draws_per_problem"], "share of 24-token draws of the plain base that open with '\\nOkay' (first 60 characters)", SRC["selfopen_metrics"] + " draws", "COPIED (draws not in git)"),
        "stored_plain_self_opened": fact(sum(r["source"] == "stored_T3" for r in so), N, "stored plain answers (T3) that already open so", ss, "73 by the 'first 30 characters' rule of cells_T10"),
        "median_draws_needed": fact(sm["draws"]["median_draws_needed_self_opened"], len(b), "draws", SRC["selfopen_metrics"], "COPIED"),
        "never_self_opened": fact(sum(not r["any_self_open"] for r in so), N, "problems with no such opening in 32 draws", ss),
        "rule": fact("'\\nOkay' in the first 60 characters of a 24-token draw", N, "the test for a self-opened answer", SRC["selfopen_metrics"],
                     f"{sum(r['source'] == 'stored_T3' for r in so)} stored plain answers already pass and are reused; the other {sm['draws']['n_regenerated']} problems draw up to "
                     f"{sm['draws']['draws_per_problem']} openings; {sum(not r['any_self_open'] for r in so)} problems never self-open"),
        "cap_hits_main": fact(int(g("cap_hit_main").sum()), N, "cap hits", ss), "tokens_mean_main": fact(round(float(g("tokens_main").mean()), 1), N, "tokens per problem (the continued answer; the up to 32 x 24 draw tokens not counted)", ss),
    }

    # ---------- hand-written edit of one matrix (WSP-2), plain prompt ----------
    he = {k: by_index(load(SRC["wsp2"].format(k))) for k in ("cueprog_plain", "cueprog_rand_plain")}
    hx = {k: np.array([r["score_v3"] for r in v]) for k, v in he.items()}
    ws = SRC["wsp2"].format("{cueprog_plain,cueprog_rand_plain}")
    wm = {k: load(SRC["wsp2"].format(k).replace("per_problem", "metrics")) for k in he}
    facts["hand_written_edit"] = {
        "right": fact({"edit": int(hx["cueprog_plain"].sum()), "random_control": int(hx["cueprog_rand_plain"].sum()), "base_plain_T3": int(X["base_plain"].sum()), "base_cue_T1": int(X["base_cue"].sum())}, N, "right of 500, plain prompt, T 1.0, one sample", ws,
                      "edit of model.layers.31.mlp.down_proj.weight written from 128 calibration prompts, no RL weights; seeds 184000000 / 185000000"),
        "edit - base_cue": diff(hx["cueprog_plain"], X["base_cue"], ws), "edit - base_plain": diff(hx["cueprog_plain"], X["base_plain"], ws, "paired here; the stored readout had no T3 rows and used an unpaired interval"),
        "edit - random_control": diff(hx["cueprog_plain"], hx["cueprog_rand_plain"], ws), "random_control - base_plain": diff(hx["cueprog_rand_plain"], X["base_plain"], ws),
        "method": fact(wm["cueprog_plain"]["handedit"]["solution"], 1, "closed-form key-value (ROME-style) update of one matrix", SRC["wsp2"].format("cueprog_plain").replace("per_problem", "metrics") + " handedit",
                       f"tensor {wm['cueprog_plain']['handedit']['tensor']}; one rank-one term per cue token, 3 keys solved jointly (so rank at most 3, not rank one); each term scaled by bisection until the "
                       f"cue token's mean probability is {wm['cueprog_plain']['handedit']['target']} on the calibration prompts, MATH-500 problems {wm['cueprog_plain']['handedit']['calibration']} (inclusive): "
                       f"{wm['cueprog_plain']['handedit']['calibration'][1] - wm['cueprog_plain']['handedit']['calibration'][0] + 1} of the 500 scored problems were used to size the edit; "
                       f"seeds {load(SRC['wsp2'].format('cueprog_plain').replace('per_problem', 'run'))['seed']} (edit), {load(SRC['wsp2'].format('cueprog_rand_plain').replace('per_problem', 'run'))['seed']} (control)"),
        "s100_plain_mean4 - edit": diff(P4["s100_plain"], hx["cueprog_plain"], src4["s100_plain"] + " ; " + ws, "x = per-problem mean of four samples, y = the edit's one sample"),
        "edit - base_cue_mean4": diff(hx["cueprog_plain"], P4["base_cue"], ws + " ; " + src4["base_cue"], "x = the edit's one sample, y = per-problem mean of four samples"),
        "s100_plain - edit": diff(X["s100_plain"], hx["cueprog_plain"], src["s100_plain"] + " ; " + ws),
        "cap_hits": fact({k: sum(r["cap_hit"] for r in v) for k, v in he.items()}, N, "cap hits", ws),
        "okay_first80": fact({k: load(SRC["wsp2_readout"])["cells"]["full500/" + k]["okay_first80"] for k in he}, N, "answers with 'Okay' in the first 80 characters", SRC["wsp2_readout"], "COPIED (texts not in git); note the 80-character window"),
        "edit_size": fact(wm["cueprog_plain"]["handedit"]["fro_dW_over_W"] if "handedit" in wm["cueprog_plain"] else load(SRC["wsp2_readout"])["cells"]["full500/cueprog_plain"]["handedit"]["fro_dW_over_W"],
                          1, "Frobenius norm of the edit over that of the matrix", SRC["wsp2_readout"], "COPIED"),
    }

    # ---------- copied: code, weights ----------
    c1 = load(SRC["code1"])
    cd = lambda k: fact([round(c1["differences"][k]["points"], 2)] + [round(v, 2) for v in c1["differences"][k]["bootstrap95"]], 538, "points [95 %], as stored (minus sign: second cell higher)", SRC["code1"] + f" differences['{k}']", "COPIED: per-problem rows not in git")
    facts["code"] = {"passed": fact({k: v["all"]["passed"] for k, v in c1["cells"].items()}, 538, "problems passed of 538 (HumanEval+ 163, MBPP+ 375), T 1.0, one sample", SRC["code1"], "COPIED. Models: base and Olmo-3.1-7B-RL-Zero-Code; base_cue = the Code-RL model's own opening, base_mathcue = the math cue"),
                     **{k: cd(k) for k in ("base_plain - base_mathcue", "base_plain - base_cue", "base_cue - base_mathcue", "rl_plain - base_mathcue")}}
    w = load(SRC["weights"])
    rn = lambda k: w["per_key"][k]["rel_norm"]
    facts["weights_step100"] = {
        "rel_norm": fact({"math31_s100": rn("math31_s100"), "math31_final": rn("math31")}, w["n_matrices"], "norm of (checkpoint - base) over the norm of the base, 224 layer matrices", SRC["weights"] + " per_key", "COPIED (weights job abaybektursun-1114-221259-0871)"),
        "norm_ratio_s100_over_final": fact(round(rn("math31_s100") / rn("math31"), 4), w["n_matrices"], "ratio of the two relative norms", SRC["weights"], "derived from the copied values"),
        "cos_s100_final": fact(round(w["tables"]["cos"]["math31"]["math31_s100"], 4), w["n_matrices"], "cosine of (step 100 - base) and (final - base), mean over 224 layer matrices", SRC["weights"] + " tables.cos", "COPIED. For scale: math31 with code31_s100 "
                               f"{w['tables']['cos']['math31']['code31_s100']:.4f}, math31 with math30 final {w['tables']['cos']['math31']['math30']:.4f}"),
        "top8_overlap_right_s100_final": fact(round(w["tables"]["overlap_right"]["math31"]["math31_s100"], 4), w["n_matrices"], "overlap of the top-8 input-side singular subspaces, mean over matrices", SRC["weights"] + " tables.overlap_right", "COPIED"),
    }

    walk = {}
    for k in ("math31", "code31", "math30", "code30", "if30", "general30", "mix30"):
        ratio, cs = rn(k + "_s100") / rn(k), w["tables"]["cos"][k][k + "_s100"]
        walk[k] = {"norm_ratio_s100_over_final": round(ratio, 3), "cos_s100_final": round(cs, 3), "share_of_s100_move_in_final": round(cs / ratio, 2)}
    facts["weights_step100"]["against_random_walk"] = fact(
        walk, w["n_matrices"], "per run: |step 100 - base| / |final - base|, cosine of the two differences, and cosine / ratio", SRC["weights"] + " per_key, tables.cos",
        "DERIVED from copied values. If the steps after step 100 were uncorrelated with the first 100 (a random walk), cosine = norm ratio and the share = 1. "
        "share = cosine x |final| / |step 100| = the projection of the final difference on the step-100 direction, in units of the step-100 length: the part of the step-100 move still in the final weights. "
        "Approximate: the cosine is a mean over 224 matrices and the norms are whole-model relative norms; no per-matrix projection is stored. math31 = Olmo-3.1 RL-Zero-Math (this paper's run)")
    fz = load(SRC["frozen"])
    facts["cue"] = fact({"text": fz["prefill_text"], "token_ids": fz["prefill_ids"], "n_tokens": len(fz["prefill_ids"])}, 1, "the prefilled opening cue", SRC["frozen"] + " prefill_text, prefill_ids",
                        "Wang et al. (arXiv 2610.06851) describe fixing the first two tokens of the response, '.\\n\\n Okay' (board knowledge-8a31ad: 'cue token count: 2'; string as given by the paper's reviewers, "
                        "not re-read here). Ours is three tokens, ' line!\\n\\nOkay': the RL model's own most common opening")
    facts["seeds"] = fact(
        {"base_plain": seeds["base_plain"], "base_cue": seeds["base_cue"], "s100_plain": seeds["s100_plain"], "s100_cue": seeds["s100_cue"], "s400_plain": seeds["s400_plain"], "s400_cue": seeds["s400_cue"],
         "final_plain": seeds["final_plain"], "hand_edit": load(SRC["wsp2"].format("cueprog_plain").replace("per_problem", "run"))["seed"],
         "hand_edit_control": load(SRC["wsp2"].format("cueprog_rand_plain").replace("per_problem", "run"))["seed"], "four_samples_problem0": {k: S4[k]["seeds"] for k in K4}},
        N, "seed base of each cell; an answer's seed = base + 10000 sample + 1000 attempt + problem index", "run.json of each cell; " + SRC["frozen"] + " seeds (T1, T2, T3)",
        "step 100 plain vs base cue is not seed-matched; step 100 cue vs base cue is. The step-100 plain sample-0 cell is the THIRD attempt: the first job (AWS ih-1115-092337-b35c) was cut by its "
        "2-hour limit at 478 answers (405 right) and is not used, the second was lost with its box (README, ckptcue 'Limits')")

    # ---------- ckptcue3: three more samples per checkpoint cell, when the sibling branch has landed ----------
    r3 = load(SRC["ckpt_readout3"])
    for k, rk in (("base_cue", "base_cue"), ("final_plain", "rl_final"), ("s100_plain", "s0100_plain"), ("s100_cue", "s0100_cue"), ("s400_plain", "s0400_plain")):
        st = r3["cells"][rk]["samples"]
        mine = [[c4[k]["right_per_sample"]["value"][j], c4[k]["cap_hits_per_sample"]["value"][j], None if S4[k]["ok"] is None else c4[k]["okay30_per_sample"]["value"][j],
                 round(float(S4[k]["tok"][j].mean()), 3)] for j in range(4)]
        assert mine == [[v["right"], v["cap_hits"], v["okay_in_first_30"], round(v["tokens_per_problem"], 3)] for v in st], f"readout3 cell {rk} differs from the rows: {mine}"
    D4 = facts["differences_T10_four_sample_means"]
    for k, rk in (("s100_plain - base_cue", "s0100_plain minus base_cue"), ("s100_cue - s100_plain", "s0100_cue minus s0100_plain"), ("s100_cue - base_cue", "s0100_cue minus base_cue"),
                  ("s400_plain - s100_plain", "s0400_plain minus s0100_plain"), ("final_plain - s400_plain", "rl_final minus s0400_plain")):
        st = r3["differences"][rk]
        assert abs(D4[k]["value"] - st["points"]) < 0.006 and all(abs(x_ - y_) <= 0.3 for x_, y_ in zip(D4[k]["ci95"], st["ci95"])), f"readout3 {rk}: {D4[k]['value']} {D4[k]['ci95']} against {st}"
    facts["ckptcue3"] = {"status": "present", "note": "the 4-sample numbers are cells_T10_four_samples, differences_T10_four_sample_means, seed_noise_T10; every cell (right, cap hits, 'Okay', tokens per sample) "
                                                      "and the five differences of readout3 were asserted against the rows (points exact; interval ends within 0.3: readout3 used 5,000 resamples)",
                         "readout3_copied": r3, "recomputed": {k: {"right_per_sample": c4[k]["right_per_sample"]} for k in ("s100_plain", "s100_cue", "s400_plain")}}

    # ---------- checks against the stored readouts and the scouts ----------
    ro = load(SRC["ckpt_readout"])
    D = facts["differences_T10"]
    vs = []

    def cmp(what, mine, stored, source, tol=0.0):
        same = mine == stored if tol == 0 else all(abs(a - b) <= tol for a, b in zip(np.ravel(mine), np.ravel(stored)))
        vs.append({"what": what, "recomputed": mine, "stored": stored, "match": bool(same), "source": source})

    for k, f_ in (("s100_plain", "s0100_plain"), ("s100_cue", "s0100_cue"), ("s400_plain", "s0400_plain"), ("s400_cue", "s0400_cue")):
        c = ro["cells"][f_]
        cmp(f"{k} right / cap / okay30 / tokens", [cells[k]["right"]["value"], cells[k]["cap_hits"]["value"], cells[k]["okay30"]["value"], cells[k]["tokens_mean"]["value"]],
            [c["right"], c["cap_hits"], c["okay_in_first_30"], round(c["tokens_per_problem"], 1)], SRC["ckpt_readout"])
    for k, s in (("s100_plain - base_cue", "s0100_plain minus base_cue_T1"), ("s100_cue - base_cue", "s0100_cue minus base_cue_T1"), ("s100_cue - s100_plain", "s0100_cue minus s0100_plain"),
                 ("s400_plain - base_cue", "s0400_plain minus base_cue_T1"), ("s400_cue - s400_plain", "s0400_cue minus s0400_plain"), ("s400_plain - s100_plain", "s0400_plain minus s0100_plain"),
                 ("final_plain - s400_plain", "rl_final_T2 minus s0400_plain")):
        st = ro["differences"][s]
        cmp(k + " [points, low, high]", [D[k]["value"]] + D[k]["ci95"], [round(st["points"], 2)] + [round(v, 2) for v in st["ci95"]], SRC["ckpt_readout"] + " (5,000 resamples)", tol=0.45)
    for k, g_ in (("base_plain", "base_plain_1.0"), ("base_cue", "base_opener_1.0"), ("final_plain", "rl_1.0")):
        cmp(f"{k} right / cap", [cells[k]["right"]["value"], cells[k]["cap_hits"]["value"]], [gr[g_]["right_v3"], gr[g_]["cap_hits"]], SRC["grader"])
    hro = load(SRC["handoff_readout"])["cuts"]
    for c in ("25", "50", "75"):
        for k, s in (("rl_own - base_own", "rl_own_minus_base_own"), ("base_on_rl_prefix - base_own", "base_on_rl_prefix_minus_base_own"), ("rl_on_base_prefix - rl_own", "rl_on_base_prefix_minus_rl_own")):
            cmp(f"handoff cut {c} {k}", [ho["cut_" + c][k]["value"]] + ho["cut_" + c][k]["ci95"], [round(hro[c][s]["points"], 2)] + [round(v, 2) for v in hro[c][s]["ci95"]], SRC["handoff_readout"], tol=0.7)
    cmp("selfopen right main / control / cue / plain", list(facts["selfopen"]["right"]["value"].values()),
        [sm["main"]["right_of_500"], sm["control"]["right_of_500_with_stored_self_opened"], sm["references_stored"]["cue_T1"]["right_of_500"], sm["references_stored"]["plain_T3"]["right_of_500"]], SRC["selfopen_metrics"])
    sd = facts["selfopen"]["resampled: self_open - control"]
    cmp("selfopen resampled main - control", [sd["value"]] + sd["ci95"], [sm["control"]["on_b_problems"]["main_minus_control_points"]] + sm["control"]["on_b_problems"]["bootstrap_95_points"], SRC["selfopen_metrics"], tol=0.6)
    wd = load(SRC["wsp2_readout"])["full500_vs_references"]["differences"]
    for k, s in (("edit - base_cue", "cueprog_plain minus T1_base_cue"), ("edit - random_control", "cueprog_plain minus cueprog_rand_plain"), ("edit - base_plain", "cueprog_plain minus T3_base_plain")):
        h = facts["hand_written_edit"][k]
        cmp("hand edit " + k, [h["value"]] + h["ci95"], [wd[s]["points"]] + wd[s]["ci95"], SRC["wsp2_readout"] + ("" if wd[s]["paired"] else " (stored interval is UNPAIRED)"), tol=0.6)
    cmp("T 0.6 page literals okay / cut", [[t06[k]["okay30"]["value"] for k in K06], [t06[k]["cap_hits"]["value"] for k in K06]], [page["okay"], page["cut"]], SRC["page"] + " DATA")
    facts["vs_readouts"] = vs

    sc = []

    def scout(what, theirs, mine, note=""):
        sc.append({"what": what, "scout": theirs, "recomputed": mine, "match": theirs == mine, "note": note})

    r1 = lambda v: [round(x, 1) for x in v]
    scout("right of 500 at T 1.0", SCOUT["right_T10"], {k: cells[k]["right"]["value"] for k in ORDER})
    for k in ("s100_plain - base_cue", "s100_cue - base_cue"):
        scout(k, SCOUT[k], r1([D[k]["value"]] + D[k]["ci95"]), "scout: 5,000 resamples; here 10,000")
    scout("'Okay' in first 30 characters", SCOUT["okay30"], {"base_plain_T06": t06["base_plain"]["okay30"]["value"], "s100_plain_T06": t06["s100_plain"]["okay30"]["value"], "s100_plain_T10": cells["s100_plain"]["okay30"]["value"]},
          f"the base's 193 is its T 0.6 count; at T 1.0 the plain base has {cells['base_plain']['okay30']['value']}")
    g = tr["net_gap_split"]["value"]
    scout("53-problem gap: by step 100, by step 400, after", SCOUT["gap53"], [g["by_step_100"], g["step_100_to_400"], g["after_step_400"]], "net differences of counts, not sets of problems (transitions_T10)")
    scout("cap hits at T 0.6: base, step 100, step 400, final", SCOUT["cap_T06"], [t06[k]["cap_hits"]["value"] for k in ("base_plain", "s100_plain", "s400_plain", "final_plain")])
    h50 = ho["cut_50"]
    scout("hand-off 50 %: base on RL prefix minus own [points, low, high], gap", SCOUT["handoff_50"], r1([h50["base_on_rl_prefix - base_own"]["value"]] + h50["base_on_rl_prefix - base_own"]["ci95"] + [h50["rl_own - base_own"]["value"]]), "final RL, hard pool, n 155")
    scout("hand-off 75 %: RL finishes base prefix vs base finishes own", SCOUT["handoff_75_rl_on_base_vs_base_own"], [ho["cut_75"]["right"]["value"]["rl_finishes_base"], ho["cut_75"]["right"]["value"]["base_finishes_base"]])
    v = facts["selfopen"]["right"]["value"]
    scout("self-open: main, cue, plain, control", SCOUT["selfopen"], [v["self_open"], v["base_cue_T1"], v["base_plain_T3"], v["control_no_okay"]])
    v = facts["selfopen"]["resampled_problems"]["value"]
    scout("self-open on the 403 resampled: main, control", SCOUT["selfopen_b"], [v["self_open"], v["control"]])
    v = facts["hand_written_edit"]["right"]["value"]
    scout("hand-written edit: plain base, edit, control", SCOUT["handedit"], [v["base_plain_T3"], v["edit"], v["random_control"]])
    v = c1["differences"]["base_plain - base_mathcue"]
    scout("math cue on code [points, low, high], n", SCOUT["code_mathcue"], [round(-v["points"], 1), round(-v["bootstrap95"][1], 1), round(-v["bootstrap95"][0], 1), 538], "copied from the readout")
    facts["vs_scout"] = sc

    facts["copied_not_recomputed"] = [
        "cells_T06.*.right and okay400 (raw rows on S3; per problem only finished-and-right is in git, in the site page literal)",
        "cells_T10.final_plain.okay30 / opening_classes (from the site page literal PROBLEMS1; T2.jsonl not in git)",
        "selfopen.self_open_rate, median_draws_needed (the 12,992 draws are not in git)",
        "hand_written_edit.okay_first80, edit_size", "code.* (no per-problem rows in git)", "weights_step100.* (weights job; per-matrix rows in the Volume)",
        "ckptcue3.readout3_copied (its numbers are recomputed elsewhere)", "cue.note on Wang et al.'s two tokens", "seeds.note on the three attempts (README)",
    ]

    ex = load(SRC["ckpt_examples"])
    facts["examples_s100_plain"] = {k: {"problem_index": e["problem_index"], "unique_id": e["unique_id"], "seed": e["seed"], "problem": e["prompt"].split("\n\n")[1][:300], "gold": e["gold"],
                                        "extracted_v3": e["extracted_v3"], "score_v3": e["score_v3"], "n_generated": e["n_generated"], "cap_hit": e["cap_hit"],
                                        "text_start": e["text"][:220], "text_end": e["text"][-220:], "source": SRC["ckpt_examples"] + f" ['{k}']"} for k, e in ex.items()}

    (HERE / "facts.json").write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n")

    # ---------- per-problem table ----------
    with open(HERE / "problems.jsonl", "w") as f:
        for i in range(N):
            row = {"i": i, "subject": t12[i]["subject"], "level5": t12[i]["level5"],
                   "T10": {k: {"r": int(cell[k][i][0]), "cap": int(cell[k][i][1]), "ok": int(okay(k, i)), "tok": int(cell[k][i][2])} for k in ORDER},
                   "T10_s4": {k: {"r": [int(v) for v in S4[k]["right"][:, i]], "cap": [int(v) for v in S4[k]["cap"][:, i]], "tok": [int(v) for v in S4[k]["tok"][:, i]]} for k in S4},
                   "T06": {k: {"fr": int(P06[i][3][j] == "r"), "cap": int(P06[i][3][j] == "c"), "ok": int(P06[i][4][j] == "1"), "tok": P06[i][5][j]} for j, k in enumerate(K06)},
                   "selfopen": {"r": so[i]["score_main"], "ctrl": so[i]["score_control"], "source": so[i]["source"], "cap": int(so[i]["cap_hit_main"]), "tok": so[i]["tokens_main"]},
                   "handedit": {"r": int(hx["cueprog_plain"][i]), "ctrl": int(hx["cueprog_rand_plain"][i]), "cap": int(he["cueprog_plain"][i]["cap_hit"]), "tok": he["cueprog_plain"][i]["n_generated"]},
                   "handoff_unbiased": i in set(U)}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # ---------- console ----------
    for k in ORDER:
        c = cells[k]
        print(f"{k:<12} right {c['right']['value']}  cap {c['cap_hits']['value']:>3}  okay30 {c['okay30']['value']:>3}  tokens {c['tokens_mean']['value']:>7}  median finished {c['tokens_median_finished']['value']}")
    for k, d in D.items():
        print(f"{k:<28} {d['value']:+6.2f} [{d['ci95'][0]:+.2f}, {d['ci95'][1]:+.2f}]  only x {d['only_x']}, only y {d['only_y']}")
    for k, d in facts["one_sample_vs_four_sample_reference"].items():
        if "ci95" in d:
            print(f"{k:<32} {d['value']:+6.2f} [{d['ci95'][0]:+.2f}, {d['ci95'][1]:+.2f}]")
    for k in K4:
        print(f"{k:<12} 4 samples {c4[k]['right_per_sample']['value']} mean {c4[k]['mean_right']['value']}  cap {c4[k]['cap_hits_per_sample']['value']} (right {c4[k]['cut_off_scored_right_per_sample']['value']})  "
              f"sd {noise[k]['sd_between_samples']['value']}  flips {noise[k]['flips_between_two_samples']['value']}  by count {noise[k]['problems_by_right_count']['value']}  "
              f"median finished pooled {c4[k]['tokens_median_finished_pooled']['value']}  okay30 {c4[k]['okay30_per_sample']['value']}")
    for k, d in D4.items():
        print(f"4-sample {k:<26} {d['value']:+6.2f} [{d['ci95'][0]:+.2f}, {d['ci95'][1]:+.2f}]")
    for k, t in tr.items():
        if "expected_independent" in t:
            print(f"{k:<28} sample 0: +{t['value']['gained']} -{t['value']['lost']}  expected {t['expected_independent']}  16 pairs {t['observed_range_16_pairs']}  same-rates null {t['same_rates_null']['gained']}")
    print("final gains over step 100:", tr["final_gains_over_s100_four_samples"]["value"])
    print("hand-off:", json.dumps({k: v["value"] for k, v in ho.items() if k.startswith("prefix_detail")}))
    print("weights:", walk)
    print("T 0.6:", t06["s100_plain_vs_base_cue"]["value"], " seeds:", facts["seeds"]["value"])
    bad = [v for v in vs if not v["match"]] + [v for v in sc if not v["match"]]
    print(f"ckptcue3: {facts['ckptcue3']['status']};  {len(vs)} readout checks, {len(sc)} scout checks, {len(bad)} do not match")
    for v in bad:
        print("  MISMATCH", json.dumps(v, ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
