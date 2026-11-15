"""Direct test editvote-01 (round-15/account-3/c2), specs/SPEC_direct_editvote.md.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_editvote

Run from the repository root. Vote over 4 attempt-0 samples on hard328 for the 1.5x top-8 edit, RL plain and base + cue,
with the plain (stored-order) tie rule and the order-averaged one (exact expectation under a random tie-break).
Stops if a posted number is not reproduced.
"""
import json
import pathlib
import subprocess

import numpy as np

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.analysis import frontier as F
from studies.rlneurons.analysis import selector as SEL

RES = pathlib.Path("studies/rlneurons/results/day1_3")
RUNS = {"edit": "hard328_top8x1.5_cue_s4-01", "rl": "hard328_rl_plain_s4r2-01", "base": "hard328_base_cue_s4r2-01"}
OUT = pathlib.Path("studies/theory/results/direct/editvote-01")
B = 10_000
RANGE, NULL_RANGE = (-5.0, 5.0), (-14.0, -6.0)


def interval(d, idx):
    m = 100 * d[idx].mean(1)
    return [round(float(np.percentile(m, 5)), 2), round(float(np.percentile(m, 95)), 2)]


def verdict(ci, n):
    if RANGE[0] <= ci[0] and ci[1] <= RANGE[1]:
        return "holds" if n >= 50 else "undecided"
    if ci[1] < RANGE[0] or ci[0] > RANGE[1]:
        return "refuted"
    return "undecided"


def main():
    att0 = {m: {i: [c[0] for c in cs] for i, cs in F.load(RES / p)[1].items()} for m, p in RUNS.items()}
    idxs = sorted(att0["rl"])
    assert len(idxs) == 328 and all(sorted(att0[m]) == idxs for m in att0)
    assert all(r["attempt"] == 0 for m in att0 for i in idxs for r in att0[m][i])
    plain = {m: np.array([V.vote(att0[m][i])["score"] for i in idxs], float) for m in att0}
    avg = {m: np.array([SEL.tie_random(att0[m][i]) for i in idxs], float) for m in att0}
    # the plan's wording: cap hits abstain (the posted votes let a cap hit with an extracted answer vote)
    capoff = {m: np.array([SEL.tie_random([{**r, "extracted_v3": None} if r["cap_hit"] else r for r in att0[m][i]]) for i in idxs], float)
              for m in att0}

    # posted: result-95a4dc (plain), result-f941b8 (order-averaged)
    assert [int(plain[m].sum()) for m in ("edit", "rl", "base")] == [214, 221, 192], {m: plain[m].sum() for m in plain}
    assert round(avg["rl"].sum(), 1) == 215.9 and round(avg["base"].sum(), 1) == 184.6, {m: avg[m].sum() for m in avg}
    assert round(100 * (plain["edit"] - plain["rl"]).mean(), 1) == -2.1
    assert round(100 * (avg["edit"] - avg["rl"]).mean(), 1) == 0.1

    n = len(idxs)
    idx = np.random.default_rng(0).integers(0, n, (B, n))
    out = {}
    for name, s in (("order_averaged", avg), ("plain_stored_order", plain), ("order_averaged_cap_hits_abstain", capoff)):
        d, dn, db = s["edit"] - s["rl"], s["base"] - s["rl"], s["edit"] - s["base"]
        ci = interval(d, idx)
        half = (ci[1] - ci[0]) / 2
        out[name] = {"votes_right": {m: round(float(s[m].sum()), 2) for m in s},
                     "statistic_points": round(float(100 * d.mean()), 2), "interval90": ci,
                     "null_points": round(float(100 * dn.mean()), 2), "null_interval90": interval(dn, idx),
                     "edit_minus_base_points": round(float(100 * db.mean()), 2), "edit_minus_base_interval90": interval(db, idx),
                     "verdict": verdict(ci, n),
                     "inside_null_range": bool(NULL_RANGE[0] <= 100 * d.mean() <= NULL_RANGE[1]),
                     "interval_overlaps_null_range": bool(ci[0] <= NULL_RANGE[1] and ci[1] >= NULL_RANGE[0]),
                     "problems_edit_better": int((d > 0).sum()), "problems_rl_better": int((d < 0).sum())}
        # n at which the interval half-width would fit inside the range around the point value (if undecided)
        room = min(100 * d.mean() - RANGE[0], RANGE[1] - 100 * d.mean())
        out[name]["n_to_decide"] = None if out[name]["verdict"] != "undecided" or room <= 0 else int(np.ceil(n * (half / room) ** 2))

    metrics = {"test": "editvote-01", "mechanism": "round-15/account-3/c2", "n": n, "bootstrap": {"resamples": B, "seed": 0, "paired": True},
               "statistic": "100 * (edit vote right - RL plain vote right) / 328, vote over 4 attempt-0 samples, v3",
               "primary_rule": "order_averaged", "cap_hits_with_answer_attempt0": {"edit": 42, "rl": 79, "base": 49}, "ranges": {"account-3": list(RANGE), "null": list(NULL_RANGE)},
               "runs": {m: str(RES / p) for m, p in RUNS.items()},
               "posted": {"plain": "result-95a4dc: edit 214, RL 221, base 192, -2.1 [-5.2, 0.6] (95 %)",
                          "order_averaged": "result-f941b8: RL 215.9, base 184.6, edit minus RL +0.1 [-2.3, 2.4] (95 %)"},
               "posted_reproduced": True, **out,
               "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}

    def ex(j):
        i = idxs[j]
        return {"problem_index": i, "gold": att0["rl"][i][0]["gold"],
                **{m: {"vote_plain": int(plain[m][j]), "vote_order_averaged": float(avg[m][j]),
                       "samples": [{k: r[k] for k in ("sample", "extracted_v3", "score_v3", "cap_hit", "n_new")} for r in att0[m][i]]}
                   for m in ("edit", "rl")}}
    da = avg["edit"] - avg["rl"]
    win = next(j for j in range(n) if plain["edit"][j] == 1 and plain["rl"][j] == 0 and da[j] == 1)
    lose = next(j for j in range(n) if plain["edit"][j] == 0 and plain["rl"][j] == 1 and da[j] == -1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps({"edit_vote_right_rl_vote_wrong": ex(win), "rl_vote_right_edit_vote_wrong": ex(lose)}, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in out}, indent=1))


if __name__ == "__main__":
    main()
