"""Direct test r16a1c1 (theory round 16, round-16/account-1/c1). Spec: studies/theory/specs/SPEC_direct_r16a1c1.md.

D1 = mean over problems of (step-100 cue right rate over 4 samples - right rate of the step-100 plain samples that do
not open deliberatively), on problems with >= 1 such plain sample. The adversary's value is computed first.
Run from the worktree root:
  uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 \
    python studies/theory/analysis/direct_r16a1c1.py
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CK = ROOT / "studies/rlneurons/results/ckptcue"
BASE = ROOT / "studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json"
# Raw answers (full text): sample 0 in the worktree iterate-hack-ckpt, samples 1-3 copied with `gpu.py get`.
RAW0 = ROOT.parent / "iterate-hack-ckpt/runs/abaybektursun-1115-064532-6a2f/answers.jsonl"
RAW123 = ROOT / "runs/abaybektursun-1115-102945-9b20/answers.jsonl"
OUT = ROOT / "studies/theory/results/direct/r16a1c1-01"
RANGES = {"round-16/account-1/c1": [0.15, 0.75], "round-16/account-2/deny-account-1-c1": [-0.10, 0.12]}
RANGE_NULL = [-0.08, 0.08]
OPENER = re.compile(r"\b(Okay|Hmm|Let me|Let's|Wait|First|Alright)\b")
STOP = re.compile(r"[$=]|\\\(|\\\[|Answer")
OPENER_1F98B0 = re.compile(r"\b(Okay|Alright|Hmm|Let me|Let's|I need to)\b")
STOP_1F98B0 = re.compile(r"[$=]|\\\(|\\\[")


def deliberative(text, opener=OPENER, stop=STOP):
    s = text[:240]
    m = opener.search(s)
    if m is None:
        return False
    e = stop.search(s)
    return e is None or m.start() < e.start()


def jsonl(p):
    return [json.loads(l) for l in open(p)]


def grades(one, s123):
    """{problem_index: [score_v3 of samples 0..3]} from the committed per_problem.json and rows.jsonl."""
    g = {r["problem_index"]: [r["score_v3"]] for r in json.loads(one.read_text())}
    rows = sorted(jsonl(s123), key=lambda r: (r["problem_index"], r["sample"]))
    assert len(rows) == 1500 and all(r["attempt"] == 0 for r in rows)
    for r in rows:
        g[r["problem_index"]].append(r["score_v3"])
    assert len(g) == 500 and all(len(v) == 4 for v in g.values())
    return g


def raw_plain():
    """{(problem_index, sample): raw row} for the 4 plain samples; raw score_v3 must equal the committed grade."""
    rows = [r for r in jsonl(RAW0) + jsonl(RAW123) if r["attempt"] == 0]
    # The samples-1-3 job numbers its samples 0-2 (run with seed S + 10000); the sample index follows from the seed.
    for r in rows:
        r["sample"] = (r["seed"] - 45_000_000 - r["problem_index"]) // 10_000
    d = {(r["problem_index"], r["sample"]): r for r in rows}
    assert len(d) == len(rows) == 2000, len(rows)
    return d


def boot(ds, rng, n_boot=10_000):
    ds = np.asarray(ds, dtype=float)
    means = ds[rng.integers(0, len(ds), size=(n_boot, len(ds)))].mean(axis=1)
    return [float(np.percentile(means, 5)), float(np.percentile(means, 95))]


def verdict16(interval, rng_, adv, n):
    (lo, hi), (a, b) = interval, rng_
    if hi < a or b < lo:
        return "refuted"
    if n < 50 or not (a <= lo and hi <= b):
        return "undecided"
    return "not separated" if lo <= adv <= hi else "holds"


def main():
    raw = raw_plain()
    plain = grades(CK / "s0100_plain-01/per_problem.json", CK / "s0100_plain_s123-01/rows.jsonl")
    cue = grades(CK / "s0100_cue-01/per_problem.json", CK / "s0100_cue_s123-01/rows.jsonl")
    for (i, k), r in raw.items():
        assert r["score_v3"] == plain[i][k], (i, k)
    flag = {i: [deliberative(raw[(i, k)]["text"]) for k in range(4)] for i in range(500)}

    # --- Adversary's value first: openings only, then base T1/T3 and the cue arms, never the step-100 plain grades.
    qual = [i for i in range(500) if not all(flag[i])]
    base = {r["problem_index"]: r for r in json.loads(BASE.read_text())}
    assert len(base) == 500
    sub = [i for i in qual if not deliberative(base[i]["t3_start"])]
    if len(sub) >= 30:
        adv_set, fallback = sub, False
    else:
        adv_set, fallback = [i for i in range(500) if not deliberative(base[i]["t3_start"])], True
    g_base = float(np.mean([base[i]["t1_right"] - base[i]["t3_right"] for i in adv_set]))
    s = 0.031 if fallback else float(np.mean([np.mean(cue[i]) - base[i]["t1_right"] for i in adv_set]))
    adv = g_base + s
    print(f"adversary: {len(qual)} qualifying problems, {len(sub)} with unflagged base T3; "
          f"g_base {g_base:.4f} + s {s:.4f} = {adv:.4f}")

    # --- Statistic.
    rng = np.random.default_rng(16)
    c = {i: float(np.mean(cue[i])) for i in qual}
    u = {i: float(np.mean([plain[i][k] for k in range(4) if not flag[i][k]])) for i in qual}
    d1 = [c[i] - u[i] for i in qual]
    stat, ci = float(np.mean(d1)), boot(d1, rng)
    both = [i for i in qual if any(flag[i])]
    o = {i: float(np.mean([plain[i][k] for k in range(4) if flag[i][k]])) for i in both}
    d0 = [c[i] - o[i] for i in both]
    null, null_ci = float(np.mean(d0)), boot(d0, rng)
    n = len(qual)

    # Sensitivity: the word list of the result-1f98b0 code.
    flag_b = {i: [deliberative(raw[(i, k)]["text"], OPENER_1F98B0, STOP_1F98B0) for k in range(4)] for i in range(500)}
    qual_b = [i for i in range(500) if not all(flag_b[i])]
    d1_b = [np.mean(cue[i]) - np.mean([plain[i][k] for k in range(4) if not flag_b[i][k]]) for i in qual_b]
    # Sensitivity: unflagged samples with no opener word anywhere in the first 240 characters (strict answer-first).
    strict = {i: [k for k in range(4) if not flag[i][k] and not OPENER.search(raw[(i, k)]["text"][:240])] for i in qual}
    qual_s = [i for i in qual if strict[i]]
    d1_s = [np.mean(cue[i]) - np.mean([plain[i][k] for k in strict[i]]) for i in qual_s]

    # Raw-row read: every unflagged plain sample on the qualifying problems.
    unfl = [raw[(i, k)] for i in qual for k in range(4) if not flag[i][k]]
    look = {
        "unflagged_samples": len(unfl),
        "unflagged_right": sum(r["score_v3"] for r in unfl),
        "unflagged_with_opener_after_stop": sum(bool(OPENER.search(r["text"][:240])) for r in unfl),
        "unflagged_cap_hits": sum(r["cap_hit"] for r in unfl),
        "unflagged_empty_text": sum(r["text"].strip() == "" for r in unfl),
        "unflagged_no_extraction": sum(r["extracted_v3"] is None for r in unfl),
        "unflagged_median_tokens": float(np.median([r["n_new"] for r in unfl])),
        "all_plain_median_tokens": float(np.median([r["n_new"] for r in raw.values()])),
        "flagged_samples_on_qualifying": sum(flag[i][k] for i in qual for k in range(4)),
        "flagged_right_on_qualifying": sum(plain[i][k] for i in qual for k in range(4) if flag[i][k]),
        "distinct_seeds": len({r["seed"] for r in raw.values()}),
        "first_ten_unflagged": [{"problem_index": r["problem_index"], "sample": r["sample"], "score_v3": r["score_v3"],
                                 "cap_hit": r["cap_hit"], "n_new": r["n_new"], "extracted_v3": r["extracted_v3"],
                                 "opening_240": r["text"][:240]} for r in unfl[:10]],
    }

    metrics = {
        "test": "r16a1c1", "plan": "round-16/account-1/c1",
        "adversary": {
            "value": adv, "g_base": g_base, "s": s, "n_problems": len(adv_set), "fallback_used": fallback,
            "how": "Problems with >= 1 unflagged step-100 plain sample (openings only) and an unflagged base T3 opening "
                   "(t3_start, rln4/t1_t3_items-01); g_base = mean(T1 right - T3 right); s = mean(step-100 cue rate "
                   "over 4 samples - T1 right) on the same problems; value = g_base + s.",
        },
        "statistic": "D1 = mean over problems of (step-100 cue right rate over 4 samples - right rate of the step-100 "
                     "plain samples that do not open deliberatively), grader v3, fraction of samples",
        "value": stat, "ci90": ci, "n": n, "n_planned": 70,
        "null_D0": null, "null_ci90": null_ci, "n_null": len(both), "range_null": RANGE_NULL,
        "ranges": RANGES,
        "verdicts": {m: verdict16(ci, r, adv, n) for m, r in RANGES.items()},
        "sensitivity_1f98b0_wordlist": {"n": len(qual_b), "D1": float(np.mean(d1_b))},
        "sensitivity_strict_answer_first": {"n": len(qual_s), "D1": float(np.mean(d1_s)),
                                            "rule": "unflagged and no opener word anywhere in text[:240]"},
        "flag_rule": "case-sensitive \\b(Okay|Hmm|Let me|Let's|Wait|First|Alright)\\b in text[:240], before the first "
                     "$, =, \\(, \\[ or 'Answer'",
        "bootstrap": "10,000 resamples of problems, numpy default_rng(16) (D1 first, then D0), 5th to 95th percentile",
        "departures": [
            "Committed rows store 30 characters of each completion; the 240-character openings come from the raw "
            "answers (sample 0: iterate-hack-ckpt/runs/abaybektursun-1115-064532-6a2f, samples 1-3: Modal Volume "
            "abaybektursun-1115-102945-9b20 via gpu.py get); each raw score_v3 equals the committed grade (asserted).",
            "Flag words follow the plan text (with Wait, First and an 'Answer' stop), not the result-1f98b0 code "
            "(which had 'I need to' and no 'Answer' stop); the code's list is a sensitivity line.",
        ],
        "raw_rows_read": look,
        "raw_rows_note": (
            "Read the first 10 unflagged samples in full opening. 7 of 10 are deliberative after a preamble: at T 1.0 "
            "the plain completion first continues the prompt (e.g. ' (i.e. \"Answer: $Answer$\" ...)') and that "
            "preamble holds $, = or 'Answer', which stops the flag before the later 'Okay, so I need to'. Over all 200 "
            "unflagged samples, 114 hold an opener word later in the first 240 characters. 1 of 10 is empty (problem 5 "
            "sample 0, 0 tokens; 7 empty of 200), 29 of 200 have no extracted answer, 5 of 200 hit the cap; unflagged "
            "samples are not short (median 1,800 tokens against 2,032 for all plain samples). So D1 measures mostly "
            "'preamble with an equation sign or the word Answer' plus empty replies, not answer-first replies. With "
            "strict answer-first (no opener word anywhere in 240 characters) n is 79 and D1 0.40. Seeds: 2,000 "
            "distinct, no duplicates. Every qualifying problem also has a flagged sample (n_null = n)."),
    }

    keys = ["problem_index", "sample", "seed", "score_v3", "extracted_v3", "gold", "cap_hit", "n_new"]
    pick = lambda want: next(raw[(i, k)] for i in qual for k in range(4) if not flag[i][k] and plain[i][k] == want)
    ex = {"note": "unflagged (non-deliberative) step-100 plain samples on qualifying problems; right/wrong under v3",
          **{name: {**{k: r[k] for k in keys}, "prompt": r["prompt"], "text_head_1200": r["text"][:1200],
                    "text_tail_400": r["text"][-400:], "cue_right_of_4": int(sum(cue[r["problem_index"]]))}
             for name, r in (("right", pick(1)), ("wrong", pick(0)))}}
    rows = [{"mechanism": m, "claim": cl, "verdict": metrics["verdicts"][m],
             "measured": f"{stat:.3f} [{ci[0]:.3f}, {ci[1]:.3f}], n {n}, adversary value {adv:.3f}",
             "interval": ci, "range": RANGES[m], "adversary": adv, "n": n} for m, cl in (
        ("round-16/account-1/c1", "At RL step 100 the plain samples that do not open deliberatively are unswitched "
         "plain-base answers, so on the same problem the cued step-100 model is right far more often than they are."),
        ("round-16/account-2/deny-account-1-c1", "After 100 RL steps the shift is graded and present in every sample, "
         "so the step-100 cue samples beat the non-deliberative plain samples by little (D1 in [-0.10, 0.12]).")
    )]
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    run = {"commit": commit, "command": "uv run --no-project --with numpy --with math-verify==0.9.0 --with "
           "antlr4-python3-runtime==4.11 python studies/theory/analysis/direct_r16a1c1.py",
           "raw_inputs": [str(RAW0), str(RAW123)], "gpu": "none (offline)"}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1, ensure_ascii=False) + "\n")
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False) + "\n")
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1) + "\n")
    (OUT / "run.json").write_text(json.dumps(run, indent=1) + "\n")
    print(json.dumps({k: metrics[k] for k in ("value", "ci90", "n", "null_D0", "null_ci90", "n_null", "verdicts",
                                              "sensitivity_1f98b0_wordlist", "sensitivity_strict_answer_first")}, indent=1))


if __name__ == "__main__":
    main()
