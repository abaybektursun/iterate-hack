"""Direct test r16a2c3 (round-16/account-2/c3 against its adversary), specs/SPEC_direct_r16a2c3.md.

    PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 \
        python studies/theory/analysis/direct_r16a2c3.py

Run from the repository root. D = N(X,R) - N(B,R) on fresh2026, N(X,R) = A(X,R) / sqrt(A(X,X) A(R,R)), A = pooled share
of same-problem pairs of finished wrong answers that agree. The adversary's value (X = Think-SFT + cue) is computed first,
then the statistic (X = the 1.5x top-8 edit) and the plan's null (X = base samples 2-3, B = base samples 0-1).
"""
import functools
import json
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.lib import rln4_lib as R

FRESH = pathlib.Path("studies/rlneurons/results/fresh")
MIX = pathlib.Path("studies/rlneurons/results/mixvote/fresh2026_top8x1.5-01")
OUT = pathlib.Path("studies/theory/results/direct/r16a2c3-01")
B_DRAWS = 10_000
RANGES = {"round-16/account-2/c3": [0.08, 0.6], "round-16/account-3/deny-account-2-c3": [-0.1, 0.07], "null": [-0.07, 0.06]}


@functools.lru_cache(maxsize=None)
def agree(x, y):
    a, b = sorted((x, y))
    return R.agree(R.norm_v3(a), R.norm_v3(b))


def load_rows(path):
    per = {}
    for line in open(path):
        r = json.loads(line)
        assert r["attempt"] == 0
        assert (r["problem_index"], r["sample"]) not in per
        per[(r["problem_index"], r["sample"])] = r
    assert sorted(per) == [(p, s) for p in range(136) for s in range(4)]
    return per


def load_edit():
    runs = json.loads((MIX / "run.json").read_text())["runs"]["edit"].split(",")
    per = {}
    for run in runs:  # run.json paths are relative to a worktree root
        for line in open(pathlib.Path(run) / "answers.jsonl"):
            r = json.loads(line)
            assert r["attempt"] == 0 and r["sample"] == 0 and r["bench"] == "fresh2026"
            s, rem = divmod(r["seed"] - 7_000_000 - r["problem_index"], 10_000)
            assert rem == 0 and 0 <= s <= 3 and (r["problem_index"], s) not in per
            per[(r["problem_index"], s)] = {**r, "sample": s, "_run": run}
    assert sorted(per) == [(p, s) for p in range(136) for s in range(4)]
    return per


def finished_wrong(r):
    return (r["score_v3"] == 0 and r["cap_hit"] is not True and r["finish_reason"] != "length"
            and (r["extracted_v3"] or "").strip() != "")


def wrongs(per, samples=range(4)):
    return {p: [per[(p, s)]["extracted_v3"] for s in samples if finished_wrong(per[(p, s)])] for p in range(136)}


def counts(WX, WB, WR, P):
    """Per problem: agreeing and total pairs for cross X-R, cross B-R, within X, within B, within R (10 columns)."""
    c = np.zeros((len(P), 10))
    for i, p in enumerate(P):
        for k, (u, v) in enumerate([(WX, WR), (WB, WR)]):
            c[i, 2 * k] = sum(agree(x, y) for x in u[p] for y in v[p])
            c[i, 2 * k + 1] = len(u[p]) * len(v[p])
        for k, w in enumerate([WX, WB, WR]):
            w = w[p]
            c[i, 4 + 2 * k] = sum(agree(w[a], w[b]) for a in range(len(w)) for b in range(a + 1, len(w)))
            c[i, 5 + 2 * k] = len(w) * (len(w) - 1) // 2
    return c


def d_from(c):
    """c: (..., problems, 10) summed over problems -> D and the five A's."""
    s = c.sum(-2)
    A = s[..., 0::2] / s[..., 1::2]
    axr, abr, axx, abb, arr = (A[..., k] for k in range(5))
    nx, nb = axr / np.sqrt(axx * arr), abr / np.sqrt(abb * arr)
    return nx - nb, {"A_XR": axr, "A_BR": abr, "A_XX": axx, "A_BB": abb, "A_RR": arr, "N_XR": nx, "N_BR": nb}


def measure(WX, WB, WR, P):
    c = counts(WX, WB, WR, P)
    d, parts = d_from(c)
    ix = np.random.default_rng(16).integers(0, len(P), (B_DRAWS, len(P)))
    bs, _ = d_from(c[ix])
    finite = np.isfinite(bs)  # a draw with zero agreeing within pairs for X or B has no N: such draws are dropped and counted
    bs = bs[finite]
    return {"value": round(float(d), 4), "ci90": [round(float(np.percentile(bs, 5)), 4), round(float(np.percentile(bs, 95)), 4)],
            "n": len(P), "bootstrap_draws_dropped_no_within_agreement": int((~finite).sum()),
            **{k: round(float(v), 4) for k, v in parts.items()},
            "pairs": {"XR": [int(c[:, 0].sum()), int(c[:, 1].sum())], "BR": [int(c[:, 2].sum()), int(c[:, 3].sum())],
                      "XX": [int(c[:, 4].sum()), int(c[:, 5].sum())], "BB": [int(c[:, 6].sum()), int(c[:, 7].sum())],
                      "RR": [int(c[:, 8].sum()), int(c[:, 9].sum())]},
            "problems_within": {"X": int((c[:, 5] > 0).sum()), "B": int((c[:, 7] > 0).sum()), "R": int((c[:, 9] > 0).sum())}}


def verdict16(lo, hi, rng_, adv, n):
    a, b = rng_
    if hi < a or b < lo:
        return "refuted"
    if n < 50 or not (a <= lo and hi <= b):
        return "undecided"
    return "not separated" if lo <= adv <= hi else "holds"


def main():
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    E, Rl, Bc, S = load_edit(), load_rows(FRESH / "rl_plain_s4-01/rows.jsonl"), load_rows(FRESH / "base_cue_s4-01/rows.jsonl"), \
        load_rows(FRESH / "sft1_cue_s4-01/rows.jsonl")
    for per in (E, Rl, Bc, S):
        assert all(per[(p, s)]["gold"] == Rl[(p, 0)]["gold"] for p in range(136) for s in range(4))
    WE, WR, WB, WS = wrongs(E), wrongs(Rl), wrongs(Bc), wrongs(S)
    right = {k: sum(per[(p, s)]["score_v3"] for p in range(136) for s in range(4)) / 4
             for k, per in (("edit", E), ("rl", Rl), ("base", Bc), ("sft", S))}
    assert (right["edit"], right["rl"], right["base"], right["sft"]) == (48.25, 50.5, 29.5, 60.0), right

    # Planted checks: one string everywhere gives every A = 1 (so D = 0); distinct strings give cross A = 0.
    P0 = [p for p in range(136) if WE[p] and WR[p] and WB[p]]
    one = {p: ["7"] * len(WE[p]) for p in P0}
    d1, parts1 = d_from(counts(one, {p: ["7"] * len(WB[p]) for p in P0}, {p: ["7"] * len(WR[p]) for p in P0}, P0))
    assert all(abs(float(v) - 1) < 1e-12 for v in parts1.values()) and abs(float(d1)) < 1e-12
    dist = counts({p: [f"{p}0{i}1" for i in range(len(WE[p]))] for p in P0},
                  {p: [f"{p}0{i}3" for i in range(len(WB[p]))] for p in P0}, WR, P0)
    assert dist[:, 0].sum() == 0 and dist[:, 2].sum() == 0

    # 1) Adversary's value first: Think-SFT in place of the edit, rows need S, R, B and E each >= 1 finished wrong.
    P_adv = [p for p in range(136) if WS[p] and WR[p] and WB[p] and WE[p]]
    adv = measure(WS, WB, WR, P_adv)
    P_adv3 = [p for p in range(136) if WS[p] and WR[p] and WB[p]]
    adv3 = measure(WS, WB, WR, P_adv3)
    adv_value = adv["value"]
    print("adversary", adv, file=sys.stderr)

    # 2) The statistic.
    P = P0
    stat = measure(WE, WB, WR, P)
    print("statistic", stat, file=sys.stderr)
    # The plan's null: base samples 2-3 as X, base samples 0-1 as B, against R, on the same rows.
    WB01, WB23 = wrongs(Bc, (0, 1)), wrongs(Bc, (2, 3))
    Pn = [p for p in P if WB01[p] and WB23[p]]
    null = measure(WB23, WB01, WR, Pn)
    # Descriptive: the edit on the adversary's rows (same problems as D_alt).
    stat_on_adv_rows = measure(WE, WB, WR, P_adv)

    lo, hi = stat["ci90"]
    verdicts = {m: verdict16(lo, hi, RANGES[m], adv_value, stat["n"]) for m in RANGES}

    # Ten raw rows that enter the statistic (the first ten finished wrong E/R/B rows on rows P, read in order).
    seen = []
    for p in P[:4]:
        for name, per in (("edit", E), ("rl", Rl), ("base", Bc)):
            for s in range(4):
                r = per[(p, s)]
                if finished_wrong(r) and len(seen) < 10:
                    seen.append({"model": name, "problem_index": p, "sample": s, "seed": r["seed"], "gold": r["gold"],
                                 "extracted_v3": r["extracted_v3"], "n_new": r["n_new"], "finish_reason": r["finish_reason"],
                                 "loop_A": r["loop_A"]})
    cap = {k: sum(per[(p, s)]["cap_hit"] for p in P for s in range(4)) for k, per in (("edit", E), ("rl", Rl), ("base", Bc), ("sft", S))}
    fw = {k: sum(len(w[p]) for p in P) for k, w in (("edit", WE), ("rl", WR), ("base", WB))}

    metrics = {
        "test": "round-16/account-2/c3", "spec": "studies/theory/specs/SPEC_direct_r16a2c3.md",
        "plan": "studies/theory/results/wide/round-16/synthesis_tests.json (name round-16/account-2/c3)",
        "statistic_definition": "D_fresh = N(E,R) - N(B,R), N(X,R) = A(X,R)/sqrt(A(X,X)*A(R,R)); A pooled share of same-problem pairs of finished wrong answers (v3 wrong, no cap hit, extracted answer present) that agree under math-verify 0.9.0 (rln4_lib.agree on norm_v3, pair in sorted order)",
        "right_per_sample_check": right,
        "adversary": {"value": adv_value, **adv,
                      "how": "D_alt = N(S,R) - N(B,R) with Think-SFT + cue (sft1_cue_s4-01) as S, on fresh2026 problems where S, R, B and the edit each have >= 1 finished wrong answer; within pairs from problems where the model has >= 2; bootstrap 10,000 problem resamples, default_rng(16)",
                      "rows_without_edit_condition": adv3},
        "statistic": stat, "value": stat["value"], "ci90": stat["ci90"], "n": stat["n"],
        "null_base_23_vs_01": {**null, "how": "X = base samples 2-3, B = base samples 0-1, each against R, on the statistic's rows where both halves have >= 1 finished wrong answer"},
        "edit_on_adversary_rows": stat_on_adv_rows,
        "ranges": RANGES, "verdicts": verdicts,
        "rule": "verdict16: holds if the 90 % interval is inside the range, n >= 50 and the interval excludes the adversary's value; inside but containing it: not separated; wholly outside: refuted; else undecided",
        "departures": [
            f"n = {stat['n']} problems qualify (plan said 85).",
            "The edit's rows are not in git: read from the four one-sample runs named in mixvote/fresh2026_top8x1.5-01/run.json (runs/ih-1115-*, answers.jsonl); sample index taken from the seed.",
            "Agreement uses the team grader's math-verify equivalence (rln4_lib.agree on norm_v3), with each pair in sorted order so cross pairs do not depend on the argument order.",
        ],
        "finished_wrong_answers_on_rows": fw, "cap_hits_on_rows_of_544_slots": {k: v for k, v in cap.items()},
        "raw_rows_read": seen,
        "raw_rows_note": "FILLED BY HAND AFTER READING",
    }
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    def item(p, why):
        out = {"problem_index": p, "why": why, "gold": Rl[(p, 0)]["gold"]}
        for name, per in (("edit", E), ("rl", Rl), ("base", Bc)):
            out[name] = [{k: per[(p, s)][k] for k in ("sample", "extracted_v3", "score_v3", "cap_hit", "finish_reason", "n_new")}
                         for s in range(4)]
        out["edit_rl_agreeing_pairs"] = [[x, y] for x in WE[p] for y in WR[p] if agree(x, y)]
        out["base_rl_agreeing_pairs"] = [[x, y] for x in WB[p] for y in WR[p] if agree(x, y)]
        return out

    yes = next(p for p in P if any(agree(x, y) for x in WE[p] for y in WR[p]))
    no = next(p for p in P if not any(agree(x, y) for x in WE[p] for y in WR[p]))
    (OUT / "examples.json").write_text(json.dumps([
        item(yes, "in the rows; at least one edit-RL finished-wrong pair agrees (counts toward A(E,R))"),
        item(no, "in the rows; no edit-RL finished-wrong pair agrees (adds pairs to A(E,R)'s denominator only)"),
    ], indent=1) + "\n")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({
        "commit": commit,
        "command": "PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 python studies/theory/analysis/direct_r16a2c3.py",
        "inputs": [str(FRESH / "rl_plain_s4-01/rows.jsonl"), str(FRESH / "base_cue_s4-01/rows.jsonl"), str(FRESH / "sft1_cue_s4-01/rows.jsonl"),
                   str(MIX / "run.json") + " -> runs/ih-1115-150237-83a4, -155322-598b, -155844-4392, -155905-0426 (answers.jsonl, not in git)"],
        "job_id": None}, indent=1) + "\n")
    print(json.dumps({"adversary": adv_value, "value": stat["value"], "ci90": stat["ci90"], "n": stat["n"], "null": null["value"],
                      "verdicts": verdicts}))


if __name__ == "__main__":
    main()
