"""RLN-4 inputs and laptop checks (studies/rlneurons/SPEC4.md). No model weights, no model forward.

    python -m studies.rlneurons.prep.rln4_prep --n13 <dir: base_math500.jsonl, rl_math500.jsonl, prompt_ids.json>
        --b01 <dir: P_math500.jsonl, F_math500.jsonl from results/rlneurons/r3/base-01/out/> --dolci <Dolci train parquet>
        --tok <RL 3.1 tokenizer dir>

Writes studies/rlneurons/data/rln4/{frozen4,k,g,check}.json (+ copies of RLN-3's math500.json) and
studies/rlneurons/results/rln4/offline/prep_checks.json:
  1. loop-onset instrument table (rule A, rule B, the crude rule) on the saved answers;
  2. grader v1 / v2 on the saved files (v1 must give 286 and 460 on n13's files);
  3. K: problems where base F (base-01, T 0.6) hit the cap and the RL step-2,800 answer (n13) is correct; L per problem;
     the restart set (every base F cap hit); prefix ids for K_rl and K_own;
  4. G: Dolci-RL-Zero-Math-7B train prompts, test-set overlaps excluded (rln3_overlap's rule, both test sets), seed-0 order;
  5. the 50-problem check list (base-01 F, seeds 1,000,000 + index);
  6. seed bases: no (problem, seed) pair repeats across cells that share model and prompt, and none equals an earlier run's.
Fail loud: no try/except, no fallback.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import re

import numpy as np
import pyarrow.parquet as pq

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R
from studies.rlneurons.analysis import rln3_overlap as OV

STUDY = pathlib.Path(__file__).resolve().parents[1]      # studies/rlneurons
INPUTS = STUDY / "data" / "rln4"
OFFLINE = STUDY / "results" / "rln4" / "offline"
RLN3 = STUDY / "data" / "rln3"
CAP = 16384
L_MAX, L_MIN = 2500, 300
DEADLINE_UTC = "2026-11-14T13:30:00Z"    # everything saved by then (SPEC4 §6)
STOP_UTC = "2026-11-14T13:18:00Z"        # in-job hard stop: unfinished requests aborted and listed
G_SUBMIT_STOP_UTC = "2026-11-14T12:58:00Z"
G_TARGET, G_MIN, G_SAMPLES, G_CAP = 1000, 400, 4, 4096
T_AI2 = {"temperature": 1.0, "top_p": 1.0}       # Olmo 3 paper §6.1 (temperature); top-p not stated there -> 1.0 (SPEC4 §1)
T_06 = {"temperature": 0.6, "top_p": 0.95}
# Seed bases (SPEC4 §3). Earlier runs: n13 sets A 1,000,000 and B 2,000,000; RLN-3 1,000,000 + 10,000 s (MATH-500) and
# 3,000,000 + 10,000 s (harder set). Every RLN-4 cell except the check takes a base at or above 41,000,000.
SEEDS = {"check": 1_000_000, "T1": 41_000_000, "K_rl": 42_000_000, "K_own": 43_000_000, "K_fresh": 44_000_000,
         "K_fresh2": 44_500_000, "T2": 45_000_000, "R1": 46_000_000, "T3": 47_000_000, "G": 48_000_000, "G_per_sample": 100_000}
EARLIER_MAX = 3_000_000 + 7 * 10_000 + 400
CELLS = {   # cell: model, arm (P plain / F opening), sampling, max new tokens rule
    "check": ("base", "F", {**T_06, "repetition_penalty": 1.0}),
    "T1": ("base", "F", {**T_AI2, "repetition_penalty": 1.0}),
    "K_rl": ("base", "K", {**T_06, "repetition_penalty": 1.0}),
    "K_own": ("base", "K", {**T_06, "repetition_penalty": 1.0}),
    "K_fresh": ("base", "F", {**T_06, "repetition_penalty": 1.0}),
    "K_fresh2": ("base", "F", {**T_06, "repetition_penalty": 1.0}),
    "T2": ("s2800", "P", {**T_AI2, "repetition_penalty": 1.0}),
    "G": ("base", "F", {**T_AI2, "repetition_penalty": 1.0}),
    "R1": ("base", "F", {**T_06, "repetition_penalty": 1.1}),
    "T3": ("base", "P", {**T_AI2, "repetition_penalty": 1.0}),
}


def jl(p):
    return [json.loads(l) for l in open(p)]


def crude(text):
    c = collections.Counter(l.strip() for l in text.split("\n") if len(l.strip()) > 20)
    return any(v >= 3 for v in c.values())


def detector_table(files):
    rows = {}
    for name, recs in files.items():
        fin = [r for r in recs if not r["cap_hit"]]
        cap = [r for r in recs if r["cap_hit"]]
        capl = [r for r in cap if R.zratio(r["text"][-R.W:]) < R.THR]
        row = {"finished": len(fin), "cap_hits": len(cap), "cap_hits_ratio_below_0.10": len(capl)}
        for rule, f in (("A", lambda t: R.onset_lines(t) is not None), ("B", lambda t: R.onset_period(t) is not None), ("crude", crude)):
            row[rule] = {"fires_finished": sum(f(r["text"]) for r in fin), "fires_cap_low_ratio": sum(f(r["text"]) for r in capl),
                         "fires_cap_all": sum(f(r["text"]) for r in cap)}
            row[rule]["finished_rate"] = row[rule]["fires_finished"] / len(fin)
            row[rule]["cap_low_ratio_rate"] = row[rule]["fires_cap_low_ratio"] / max(len(capl), 1)
        rows[name] = row
    verdict = {}
    for rule in ("A", "B"):
        fp_ok = all(rows[n][rule]["finished_rate"] < 0.02 for n in rows)
        tp_ok = all(rows[n][rule]["cap_low_ratio_rate"] > 0.5 for n in ("b01_F", "b01_P", "n13_base"))
        verdict[rule] = {"false_positive_below_2pct_everywhere": fp_ok, "fires_on_most_low_ratio_base_cap_hits": tp_ok, "pass": fp_ok and tp_ok}
    # failing input: a finished answer with a planted loop of 300 repeated lines must fire rule A
    planted = files["n13_rl"][0]["text"] + "\n" + "Wait, let me recompute the sum of the roots again.\n" * 300
    verdict["failing_input"] = {"what": "an RL finished answer with 300 repeated lines appended", "A_fires": R.onset_lines(planted) is not None}
    return rows, verdict


def grader_table(files, n13_want):
    out = {}
    for name, recs in files.items():
        v1 = [S.grade(r["gold"], S.extract(r["text"])[1])["score"] for r in recs]
        v2 = [R.grade_v2(r["gold"], r["text"]) for r in recs]
        assert all(S.extract(r["text"])[:2] == (r["mode"], r["extracted"]) for r in recs), f"{name}: v1 extraction differs from the bank"
        out[name] = {"n": len(recs), "v1_correct": int(sum(v1)), "v2_correct": int(sum(x["score_v2"] for x in v2)),
                     "v2_label_used": sum(x["mode_v2"] == "v2_label" for x in v2),
                     "v2_label_correct": sum(x["mode_v2"] == "v2_label" and x["score_v2"] == 1 for x in v2),
                     "v1_correct_v2_wrong": sum(a == 1 and b["score_v2"] == 0 for a, b in zip(v1, v2)),
                     "v2_examples": [{"problem_index": r["problem_index"], "extracted_v2": x["extracted_v2"], "gold": r["gold"],
                                      "score_v2": x["score_v2"]} for r, x in zip(recs, v2) if x["mode_v2"] == "v2_label"][:6]}
        if name in n13_want:
            out[name]["v1_want"] = n13_want[name]
            out[name]["v1_pass"] = out[name]["v1_correct"] == n13_want[name]
    return out


def k_set(tok, fz_pre, F, RL):
    pre_text, pre_ids = fz_pre
    rows, dropped, restart = [], [], []
    for i in range(500):
        f, r = F[i], RL[i]
        if not f["cap_hit"]:
            continue
        restart.append(i)
        if r["score"] != 1:
            continue
        o = R.onset_lines(f["text"])
        b_ids, b_off = R.encode_answer(tok, f["text"], pre_text, pre_ids)
        on_tok = R.tokens_before(b_off, o if o is not None else len(f["text"]))
        r_ids, r_off = R.encode_answer(tok, r["text"], pre_text, pre_ids)
        m, x, sp = S.extract(r["text"])
        line0 = r["text"].rfind("\n", 0, sp[0]) + 1
        rl_ans = R.tokens_before(r_off, line0)
        L = min(on_tok, L_MAX, rl_ans)
        row = {"problem_index": i, "onset_char": o, "no_onset": o is None, "onset_tokens": on_tok, "rl_tokens_before_answer_line": rl_ans,
               "L": L, "limited_by": "onset" if L == on_tok else ("cap_2500" if L == L_MAX else "rl_answer_line"),
               "base_loop_ratio": f["loop_ratio"], "rl_n_new": r["n_new"], "own_prefix_ids": b_ids[:L], "rl_prefix_ids": r_ids[:L],
               "own_prefix_text": tok.decode(b_ids[:L]), "rl_prefix_text": tok.decode(r_ids[:L])}
        (rows if L >= L_MIN else dropped).append(row)
    return rows, dropped, restart


def g_set(dolci_path, tests):
    train = pq.read_table(dolci_path).to_pylist()
    assert len(train) == 13314, len(train)
    tg = {}
    exact = {OV.norm(t) for t in tests}
    gram_test = collections.defaultdict(set)
    for j, t in enumerate(tests):
        g = OV.grams(t)
        tg[j] = len(g)
        for x in g:
            gram_test[x].add(j)
    flagged = collections.Counter()
    keep = []
    for i, r in enumerate(train):
        n = OV.norm(r["prompt"])
        c = collections.Counter(j for x in OV.grams(r["prompt"]) for j in gram_test.get(x, ()))
        share = max((v / tg[j] for j, v in c.items()), default=0.0)
        if n in exact:
            flagged["exact"] += 1
        elif share >= 0.5:
            flagged["near"] += 1
        else:
            keep.append(i)
    order = np.random.default_rng(0).permutation(len(keep))
    rows = [{"row": keep[k], "prompt": train[keep[k]]["prompt"], "ground_truth": train[keep[k]]["ground_truth"]} for k in order[:G_TARGET]]
    return rows, {"n_train": len(train), "flagged": dict(flagged), "kept": len(keep), "drawn": len(rows),
                  "rule": "rln3_overlap: exact normalized text, or >= half of a test problem's word 8-grams in the prompt; tests = MATH-500 + harder set"}


def seed_check(k_rows, restart, g_rows):
    """(cell, model, prompt key) -> seeds; within one model and prompt no seed repeats across cells; none at or below the earlier
    runs' range. Returns the check and a failing input (T1 given the check's base) that must fail."""
    def pairs(seeds):
        out = []
        for cell, base in seeds.items():
            if cell in ("check", "G_per_sample"):
                continue
            model, arm, _ = CELLS[cell]
            if cell == "G":
                out += [(model, "F", ("dolci", r["row"]), base + s * seeds["G_per_sample"] + r["row"]) for r in g_rows for s in range(G_SAMPLES)]
                continue
            idx = ([r["problem_index"] for r in k_rows] if cell in ("K_rl", "K_own") else restart if cell.startswith("K_fresh")
                   else range(500))
            out += [(model, arm, ("math500", i), base + i) for i in idx]
        return out

    def ok(seeds):
        ps = pairs(seeds)
        c = collections.Counter((m, a, k, s) for m, a, k, s in ps)
        by_seed = collections.Counter((m, k, s) for m, a, k, s in ps)
        return {"n_pairs": len(ps), "repeats_same_model_prompt": sum(v > 1 for v in c.values()),
                "repeats_same_model_problem_any_arm": sum(v > 1 for v in by_seed.values()),
                "min_seed": min(s for *_, s in ps), "above_earlier_runs": min(s for *_, s in ps) > EARLIER_MAX,
                "pass": all(v == 1 for v in by_seed.values()) and min(s for *_, s in ps) > EARLIER_MAX}
    good = ok(SEEDS)
    bad = ok({**SEEDS, "T1": SEEDS["check"]})
    bad2 = ok({**SEEDS, "R1": SEEDS["T1"]})
    return {**good, "failing_inputs": {"T1 at the check's (earlier) base": bad["pass"] is False,
                                       "R1 sharing T1's base": bad2["pass"] is False}}


def check_list(by):
    """Problems 0-49 of a saved run (seeds 1,000,000 + index): the reference a GPU check compares scores with."""
    chk = [{"problem_index": i, "seed": by[i]["seed"], "score": by[i]["score"], "cap_hit": by[i]["cap_hit"],
            "text_sha256": hashlib.sha256(by[i]["text"].encode()).hexdigest()} for i in range(50)]
    assert all(c["seed"] == SEEDS["check"] + c["problem_index"] for c in chk)
    return chk


def write_check_rl(rl_jsonl):
    """inputs/check_rl.json (Modal deviation, SPEC4): the RL check's reference, n13 s3gate-03's RL answers (rl_math500.jsonl)."""
    by = {r["problem_index"]: r for r in jl(rl_jsonl)}
    p = INPUTS / "check_rl.json"
    p.write_text(json.dumps(check_list(by), indent=0))
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n13", required=True)
    ap.add_argument("--b01", required=True)
    ap.add_argument("--dolci", required=True)
    ap.add_argument("--tok", required=True)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok)
    n13, b01 = pathlib.Path(a.n13), pathlib.Path(a.b01)
    (INPUTS).mkdir(parents=True, exist_ok=True)
    (OFFLINE).mkdir(parents=True, exist_ok=True)
    fz3 = json.loads((RLN3 / "frozen.json").read_text())
    math = json.loads((RLN3 / "math500.json").read_text())
    hard = json.loads((RLN3 / "hard.json").read_text())
    files = {"n13_base": jl(n13 / "base_math500.jsonl"), "n13_rl": jl(n13 / "rl_math500.jsonl"),
             "b01_P": jl(b01 / "P_math500.jsonl"), "b01_F": jl(b01 / "F_math500.jsonl")}
    for k, v in files.items():
        assert sorted(r["problem_index"] for r in v) == list(range(500)), k
    by = {k: {r["problem_index"]: r for r in v} for k, v in files.items()}
    assert all(by["b01_F"][i]["unique_id"] == math[i]["unique_id"] for i in range(500))

    checks = {"selfcheck": R.selfcheck() and S.selfcheck()}
    checks["agree_tests"] = {"5.5 vs \\dfrac{11}{2}": R.agree("5.5", "\\dfrac{11}{2}"), "$x = 2$ vs 2": R.agree("$x = 2$", "2"),
                             "failing input 5.5 vs \\frac{11}{3}": not R.agree("5.5", "\\frac{11}{3}")}
    rows, verdict = detector_table(files)
    checks["detector"] = {"table": rows, "verdict": verdict, "params": {"A": {"W": R.W, "THR": R.THR, "MINLEN": R.MINLEN},
                                                                         "B": {"PMAX": R.PMAX, "MINRUN": R.MINRUN, "CYCLES": R.CYCLES}}}
    checks["grader"] = grader_table(files, {"n13_base": 286, "n13_rl": 460})

    pre = (fz3["prefill_text"], fz3["prefill_ids"])
    k_rows, k_drop, restart = k_set(tok, pre, by["b01_F"], by["n13_rl"])
    Ls = np.array([r["L"] for r in k_rows])
    checks["K"] = {"base_F_cap_hits": len(restart), "rl_correct_among_them": len(k_rows) + len(k_drop), "kept": len(k_rows),
                   "dropped_L_below_300": [{"problem_index": r["problem_index"], "L": r["L"], "onset_tokens": r["onset_tokens"]} for r in k_drop],
                   "L_quantiles_0_10_25_50_75_90_100": np.percentile(Ls, [0, 10, 25, 50, 75, 90, 100]).tolist(),
                   "L_equal_2500": int((Ls == L_MAX).sum()), "limited_by": dict(collections.Counter(r["limited_by"] for r in k_rows)),
                   "no_onset": sum(r["no_onset"] for r in k_rows),
                   "rl_prefix_starts_with_opening": sum(r["rl_prefix_ids"][:3] == pre[1] for r in k_rows),
                   "own_prefix_starts_with_opening": sum(r["own_prefix_ids"][:3] == pre[1] for r in k_rows)}
    g_rows, g_info = g_set(a.dolci, [p["problem"] for p in math] + [p["problem"] for p in hard])
    checks["G"] = g_info
    chk = check_list(by["b01_F"])
    checks["seeds"] = seed_check(k_rows, restart, g_rows)

    inputs = {"k.json": {"rows": k_rows, "restart": restart, "dropped": [r["problem_index"] for r in k_drop]}, "g.json": g_rows,
              "check.json": chk, "math500.json": math}
    for name, obj in inputs.items():
        (INPUTS / name).write_text(json.dumps(obj, indent=0) if name != "math500.json" else (RLN3 / "math500.json").read_text())
    frozen = {"models": {m: fz3["models"][m] for m in ("base", "s2800")}, "tokenizer": fz3["tokenizer"], "template": "pair1", "cap": CAP,
              "prefill_ids": fz3["prefill_ids"], "prefill_text": fz3["prefill_text"], "cells": CELLS, "seeds": SEEDS,
              "g": {"target": G_TARGET, "min": G_MIN, "samples": G_SAMPLES, "cap": G_CAP}, "L": {"max": L_MAX, "min": L_MIN},
              "deadline_utc": DEADLINE_UTC, "stop_utc": STOP_UTC, "g_submit_stop_utc": G_SUBMIT_STOP_UTC,
              "check_rule": {"pass_at_least": 45, "pass_at_least_other_gpu": 38, "stop_below": 30, "n": 50, "base01_gpu_substring": "RTX PRO 6000"}, "grade_rule": S.GRADE_RULE,
              "detector": checks["detector"]["params"],
              "sha256": {n: hashlib.sha256((INPUTS / n).read_bytes()).hexdigest() for n in inputs}}
    assert frozen["sha256"]["math500.json"] == fz3["sha256"]["math500"]
    (INPUTS / "frozen4.json").write_text(json.dumps(frozen, indent=1))
    checks["pass"] = bool(checks["selfcheck"] and all(checks["agree_tests"].values()) and verdict["A"]["pass"]
                          and verdict["failing_input"]["A_fires"] and checks["grader"]["n13_base"]["v1_pass"]
                          and checks["grader"]["n13_rl"]["v1_pass"] and checks["seeds"]["pass"]
                          and all(checks["seeds"]["failing_inputs"].values())
                          and checks["K"]["rl_prefix_starts_with_opening"] + 6 >= len(k_rows))
    (OFFLINE / "prep_checks.json").write_text(json.dumps(checks, indent=1))
    show = {k: checks[k] for k in ("agree_tests", "K", "G", "seeds")}
    show["K"] = {k: v for k, v in show["K"].items() if k != "dropped_L_below_300"}
    print(json.dumps({"pass": checks["pass"], **show, "detector_verdict": verdict,
                      "grader": {k: {x: v[x] for x in v if x != "v2_examples"} for k, v in checks["grader"].items()}}, indent=1))
    for n, row in rows.items():
        print(n, {k: row[k] for k in ("finished", "cap_hits", "cap_hits_ratio_below_0.10")},
              {r: (row[r]["fires_finished"], row[r]["fires_cap_low_ratio"], row[r]["fires_cap_all"]) for r in ("A", "B", "crude")})
    assert checks["pass"], "RLN-4 prep checks failed"


if __name__ == "__main__":
    main()
