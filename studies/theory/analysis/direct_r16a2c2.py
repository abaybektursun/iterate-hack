"""Direct test r16a2c2 (round-16/account-2/c2), specs/SPEC_direct_r16a2c2.md.

    PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 \
        python studies/theory/analysis/direct_r16a2c2.py

Run from the repository root. D = N(X,R) - N(B,R), N(X,R) = A(X,R) / sqrt(A(X,X) A(R,R)), pooled agreement of finished
wrong answers on hard328. The adversary's value (X = Think-SFT + cue) is computed first, then X = the 1.5x edit.
"""
import functools
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np

from studies.rlneurons.lib import rln4_lib as L

RES = pathlib.Path("studies/rlneurons/results")
CELLS = {"E": "day1_3/hard328_top8x1.5_cue_s4-01", "R": "day1_3/hard328_rl_plain_s4r2-01",
         "B": "day1_3/hard328_base_cue_s4r2-01", "T": "thinkvote/hard328_sft1_cue_s4-01"}
OUT = pathlib.Path("studies/theory/results/direct/r16a2c2-01")
NB = 10_000
RANGES = {"round-16/account-2/c2": [0.08, 0.6], "round-16/account-3/deny-account-2-c2": [-0.1, 0.07]}
NULL_RANGE = [-0.07, 0.06]
ASYM = []


@functools.lru_cache(maxsize=None)
def agree(x, y):
    """math-verify 0.9.0 equality (rln4_lib.agree -> n13_score.grade), either order."""
    a, b = L.agree(x, y), L.agree(y, x)
    if a != b:
        ASYM.append([x, y])
    return a or b


def load(cell):
    rows = {}
    for line in open(RES / cell / "rows.jsonl"):
        r = json.loads(line)
        if r["attempt"] == 0 and r["sample"] <= 3:
            rows.setdefault(r["problem_index"], {})[r["sample"]] = r
    assert len(rows) == 328 and all(sorted(v) == [0, 1, 2, 3] for v in rows.values()), cell
    return rows


def finished_wrong(r):
    return (r["score_v3"] == 0 and r["cap_hit"] is not True and r["finish_reason"] != "length"
            and (r["extracted_v3"] or "").strip() != "")


def wrong(rows, samples):
    return {p: [rows[p][s]["extracted_v3"] for s in samples if finished_wrong(rows[p][s])] for p in rows}


def cross(a, b):
    return sum(agree(x, y) for x in a for y in b), len(a) * len(b)


def within(a):
    return sum(agree(a[i], a[j]) for i in range(len(a)) for j in range(i + 1, len(a))), len(a) * (len(a) - 1) // 2


def counts(WX, WR, WB, P):
    """Per problem: (agree, pairs) for cross XR, cross BR, within X, within B, within R -> array (n, 10)."""
    return np.array([[*cross(WX[p], WR[p]), *cross(WB[p], WR[p]), *within(WX[p]), *within(WB[p]), *within(WR[p])]
                     for p in P], float)


def stat(c):
    """c: (..., 10) summed counts -> dict of the five A's, two N's and D (works on stacked resamples)."""
    A = {k: c[..., 2 * i] / c[..., 2 * i + 1] for i, k in enumerate(["XR", "BR", "XX", "BB", "RR"])}
    nx = A["XR"] / np.sqrt(A["XX"] * A["RR"])
    nb = A["BR"] / np.sqrt(A["BB"] * A["RR"])
    return {**A, "N_XR": nx, "N_BR": nb, "D": nx - nb}


def boot(c, rng, allow_inf=False):
    """90 % interval of D; allow_inf (the step-6 null only) drops resamples with a zero within-pair agreement."""
    idx = rng.integers(0, len(c), size=(NB, len(c)))
    with np.errstate(divide="ignore", invalid="ignore"):
        d = stat(c[idx].sum(axis=1))["D"]
    bad = int((~np.isfinite(d)).sum())
    assert allow_inf or bad == 0, f"{bad} resamples have a zero within-pair count or zero agreement"
    d = d[np.isfinite(d)]
    return [float(np.percentile(d, 5)), float(np.percentile(d, 95))], bad


def point(c):
    return {k: float(v) for k, v in stat(c.sum(axis=0)).items()}


def rows_with_all(*W):
    return sorted(p for p in W[0] if all(len(w[p]) >= 1 for w in W))


def verdict16(iv, rg, adv, n):
    """Same rule as forecast.verdict16."""
    if iv[1] < rg[0] or rg[1] < iv[0]:
        return "refuted"
    if n < 50 or not (rg[0] <= iv[0] and iv[1] <= rg[1]):
        return "undecided"
    return "not separated" if iv[0] <= adv <= iv[1] else "holds"


def main():
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    M = {k: load(c) for k, c in CELLS.items()}
    W = {k: wrong(M[k], range(4)) for k in M}
    pairs = {k: int(sum(len(v) for v in W[k].values())) for k in W}

    # 1) Adversary's value first: X = Think-SFT + cue on rows where T, R, B each have >= 1 finished wrong answer.
    Pt = rows_with_all(W["T"], W["R"], W["B"])
    assert len(Pt) >= 50, f"adversary rows {len(Pt)} < 50: the plan's fallback applies and is not implemented"
    ct = counts(W["T"], W["R"], W["B"], Pt)
    adv = point(ct)
    adv_iv, _ = boot(ct, np.random.default_rng(16))
    adv_value = adv["D"]
    print(f"adversary D_T = {adv_value:.4f} on {len(Pt)} problems, 90% [{adv_iv[0]:.4f}, {adv_iv[1]:.4f}]", flush=True)

    # 2) The statistic: X = 1.5x edit.
    P = rows_with_all(W["E"], W["R"], W["B"])
    ce = counts(W["E"], W["R"], W["B"], P)
    st = point(ce)
    iv, _ = boot(ce, np.random.default_rng(16))
    print(f"D = {st['D']:.4f} on {len(P)} problems, 90% [{iv[0]:.4f}, {iv[1]:.4f}]", flush=True)

    # 3) Plan step 6 null: X = base samples 2-3, B = base samples 0-1, both against RL.
    Wb23, Wb01 = wrong(M["B"], [2, 3]), wrong(M["B"], [0, 1])
    Pn = rows_with_all(Wb23, W["R"], Wb01)
    cn = counts(Wb23, W["R"], Wb01, Pn)
    nul = point(cn)
    nul_iv, nul_bad = boot(cn, np.random.default_rng(16), allow_inf=True)
    print(f"null D = {nul['D']:.4f} on {len(Pn)} problems, 90% [{nul_iv[0]:.4f}, {nul_iv[1]:.4f}]", flush=True)

    # Instrument checks: per-sample right counts match the plan's figures; agree() says equal for equal strings.
    right = {k: sum(r["score_v3"] for p in M[k] for r in M[k][p].values()) / 4 for k in M}
    assert right == {"E": 200.25, "R": 200.0, "B": 158.5, "T": 209.0}, right
    L.selfcheck()

    # Examples: one (E, R) cross pair counted as agreeing and one counted as not.
    hard = json.loads(pathlib.Path("studies/rlneurons/data/rln3/hard.json").read_text())
    ex = {}
    for p in P:
        for se, re_ in [(a, b) for a in range(4) for b in range(4)]:
            e, r = M["E"][p][se], M["R"][p][re_]
            if not (finished_wrong(e) and finished_wrong(r)) or max(len(e["extracted_v3"]), len(r["extracted_v3"])) > 40:
                continue
            key = "agree" if agree(e["extracted_v3"], r["extracted_v3"]) else "disagree"
            if key not in ex:
                ex[key] = {"problem_index": p, "problem": hard[p]["problem"], "gold": e["gold"],
                           "edit_row": e, "rl_row": r, "counted_as": key + "ing cross pair in A(E,R)"}
        if len(ex) == 2:
            break

    # Raw-row read: 10 rows that enter the statistic (the first 10 finished wrong E rows on rows P).
    raw10 = [{"cell": "E", **M["E"][p][s]} for p in P for s in range(4) if finished_wrong(M["E"][p][s])][:10]

    n = len(P)
    rows = []
    claims = {"round-16/account-2/c2": "The 1.5x edit carries RL's re-ranking of routes, so where both fail its "
                                       "normalized wrong-answer agreement with RL exceeds the cued base's by 0.08-0.6.",
              "round-16/account-3/deny-account-2-c2": "Under S3 the edit and RL only lower the chance-slip rate, so "
                                                      "N(E,R) equals N(B,R) and D lies in [-0.10, 0.07]."}
    for mech, rg in RANGES.items():
        rows.append({"mechanism": mech, "claim": claims[mech], "result": None,
                     "verdict": verdict16(iv, rg, adv_value, n),
                     "measured": f"{st['D']:.3f} [{iv[0]:.3f}, {iv[1]:.3f}], n {n}, adversary {adv_value:.3f}",
                     "interval": [round(iv[0], 4), round(iv[1], 4)], "range": rg,
                     "adversary": round(adv_value, 4), "n": n})

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    OUT.mkdir(parents=True)
    metrics = {
        "test": "round-16/account-2/c2", "spec": "studies/theory/specs/SPEC_direct_r16a2c2.md",
        "adversary": {"value": adv_value, "interval_90": adv_iv, "n": len(Pt), "detail": adv,
                      "how": "X = Think-SFT + cue (thinkvote/hard328_sft1_cue_s4-01) attempt-0 samples 0-3; finished "
                             "wrong = score_v3 0, not cap hit, finish_reason not length, extracted_v3 non-empty; rows = "
                             "problems where T, R, B each have >= 1; pooled A's; D_T = N(T,R) - N(B,R). Exactly as "
                             "written; no fallback needed."},
        "statistic": {"value": st["D"], "interval_90": iv, "n": n, "n_planned": 90, "detail": st},
        "null_step6": {"value": nul["D"], "interval_90": nul_iv, "n": len(Pn), "range": NULL_RANGE, "detail": nul,
                       "resamples_dropped_nonfinite": nul_bad},
        "finished_wrong_answers_per_cell": pairs,
        "right_per_sample": right,
        "agree_order_mismatches": len(ASYM), "agree_order_mismatch_examples": ASYM[:5],
        "bootstrap": {"resamples": NB, "unit": "problem", "rng": "numpy default_rng(16), fresh per statistic"},
        "departures": ["agreement checked in both argument orders of rln4_lib.agree (math-verify 0.9.0 via "
                       "n13_score.grade, gold-side and answer-side wrapping differ); a pair agrees if either order "
                       "says equal"],
        "raw_rows_read": raw10,
        "raw_rows_note": "10 finished wrong edit rows read (problems 29, 57, 61): all finish_reason stop, no cap hit, "
                         "distinct seeds. Problem 29 sample 0 'extracted' a 1,000-character incoherent drift text "
                         "(14,896 tokens, under the cap): it counts as a finished wrong answer that agrees with nothing. "
                         "Such extractions (> 40 characters) are rare: E 4 of 443, R 4 of 404, B 3 of 368, T 0 of 108; "
                         "15-23 rows per cell end within 400 tokens of the cap. Problem 57: all 4 edit samples give 2744 "
                         "(gold 928), a systematic wrong value. Seeds are unique within every cell. The statistic "
                         "measures agreement of short final answers, as named.",
        "rows": rows,
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1))
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1))
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1))
    (OUT / "run.json").write_text(json.dumps({
        "commit": commit, "command": "PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 "
                                     "--with antlr4-python3-runtime==4.11 python " + " ".join(sys.argv),
        "job_id": None, "when": datetime.now(timezone.utc).isoformat(), "inputs": [str(RES / c) for c in CELLS.values()]},
        indent=1))
    for r in rows:
        print(r["mechanism"], r["verdict"])


if __name__ == "__main__":
    main()
