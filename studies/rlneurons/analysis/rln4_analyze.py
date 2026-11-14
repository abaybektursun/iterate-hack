"""RLN-4 readout (studies/rlneurons/SPEC4.md §7), on banked JSON only.

    python -m studies.rlneurons.analysis.rln4_analyze --run <dir with the job's out/ files> --b01 <dir: P_math500.jsonl, F_math500.jsonl>
        --n13 <dir: rl_math500.jsonl> --out <json>

Headline numbers use grader v1 (n13_score); v2 (rln4_lib.extract_v2) is reported beside them. Answer agreement between attempts uses
rln4_lib.agree. Fail loud: no try/except, no fallback.
"""
import argparse
import json
import pathlib

import numpy as np

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

INPUTS = pathlib.Path(__file__).resolve().parents[1] / "data" / "rln4"
T1_EXPLAINS, T1_NOT = 40, 90           # cap hits of 500
K_FIN_HI, K_FIN_LO, K_MIN_RECORDS = 0.60, 0.30, 70


def bank(p, key="problem_index"):
    p = pathlib.Path(p)
    out = {}
    if p.exists():
        for l in open(p):
            r = json.loads(l)
            assert r[key] not in out, f"{p}: duplicate {r[key]}"
            out[r[key]] = r
    return out


def v2(r):
    return r["score_v2"] if "score_v2" in r else R.grade_v2(r["gold"], r["text"])["score_v2"]


def boot(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    lo, hi = S.paired_bootstrap(x, y)
    return {"n": int(x.size), "diff": float(100 * (x.mean() - y.mean())), "ci95": [lo, hi]}


def quote(recs):
    out = {}
    for want, name in ((1, "right"), (0, "wrong")):
        r = next((r for r in recs if r["score"] == want), None)
        if r is not None:
            out[name] = {"problem_index": r["problem_index"], "gold": r["gold"], "extracted": r["extracted"], "answer_prob": r.get("answer_prob"),
                         "cap_hit": r["cap_hit"], "text_head": r["text"][:300], "text_tail": r["text"][-300:]}
    return out


def compare(new, old, name):
    idx = sorted(set(new) & set(old))
    a, b = [new[i] for i in idx], [old[i] for i in idx]
    return {"cell": name, "n": len(idx), "acc": S.acc([r["score"] for r in a]) if a else None, "acc_ref": S.acc([r["score"] for r in b]) if b else None,
            "acc_v2": S.acc([v2(r) for r in a]) if a else None, "acc_ref_v2": S.acc([v2(r) for r in b]) if b else None,
            "cap_hits": sum(r["cap_hit"] for r in a), "cap_hits_ref": sum(r["cap_hit"] for r in b),
            "loop_A": sum(r["onset_A_char"] is not None for r in a) if a and "onset_A_char" in a[0] else None,
            "mean_tokens": float(np.mean([r["n_generated"] for r in a])) if a else None,
            "mean_tokens_ref": float(np.mean([r["n_generated"] for r in b])) if b else None,
            "acc_diff": boot([r["score"] for r in a], [r["score"] for r in b]) if a else None,
            "cap_diff": boot([r["cap_hit"] for r in a], [r["cap_hit"] for r in b]) if a else None, "quotes": quote(a)}


def wilson(k, n):
    return list(S.wilson(k, n))


def readout(run, b01, n13):
    run = pathlib.Path(run)
    K = json.loads((INPUTS / "k.json").read_text())
    check = json.loads((run / "check.json").read_text()) if (run / "check.json").exists() else None
    F, P = bank(pathlib.Path(b01) / "F_math500.jsonl"), bank(pathlib.Path(b01) / "P_math500.jsonl")
    RL = bank(pathlib.Path(n13) / "rl_math500.jsonl")
    cells = {c: bank(run / f"{c}.jsonl") for c in ("check", "T1", "K_rl", "K_own", "K_fresh", "K_fresh2", "T2", "R1", "T3")}
    res = {"check": check, "n_records": {c: len(v) for c, v in cells.items()}}
    counted = bool(check and check["verdict"] == "pass")

    # T1 against base-01 F
    t1 = compare(cells["T1"], F, "T1 vs base-01 F (T 0.6)")
    n = t1["n"]
    if n >= 450:
        lo, hi = T1_EXPLAINS * n / 500, T1_NOT * n / 500
        lab = ("temperature explains the loops" if t1["cap_hits"] < lo else
               "temperature does not explain the loops" if t1["cap_hits"] > hi else "undecided")
    else:
        lab = "not counted (fewer than 450 T1 records)"
    if not counted:
        lab = f"not counted (check verdict {check and check['verdict']}): " + lab
    t1["label"] = lab
    res["T1"] = t1

    # K
    ks = [r["problem_index"] for r in K["rows"]]
    arms = {}
    for c in ("K_rl", "K_own", "K_fresh"):
        recs = [cells[c][i] for i in ks if i in cells[c]]
        fin = sum(not r["cap_hit"] for r in recs)
        arms[c] = {"n": len(recs), "finished": fin, "finished_rate": fin / len(recs) if recs else None, "finished_wilson95": wilson(fin, len(recs)),
                   "loop_A": sum(r["onset_A_char"] is not None for r in recs), "correct": sum(r["score"] for r in recs),
                   "correct_v2": sum(v2(r) for r in recs), "mean_answer_tokens": float(np.mean([r["n_answer_tokens"] for r in recs])) if recs else None,
                   "quotes": quote(recs)}
    if min(a["n"] for a in arms.values()) < K_MIN_RECORDS:
        klab = "not counted (an arm has fewer than 70 of 78 records)"
    else:
        rl, own = arms["K_rl"]["finished_rate"], arms["K_own"]["finished_rate"]
        klab = ("the base can finish from a sound prefix" if rl >= K_FIN_HI and own <= K_FIN_LO else
                "the base loops regardless of prefix" if rl <= K_FIN_LO else "undecided")
        both = [i for i in ks if i in cells["K_rl"] and i in cells["K_own"]]
        arms["K_rl - K_own finished"] = boot([not cells["K_rl"][i]["cap_hit"] for i in both], [not cells["K_own"][i]["cap_hit"] for i in both])
    res["K"] = {"n_problems": len(ks), "arms": arms, "label": klab}

    # restart row: base-01 F, then K_fresh, then K_fresh2; the first finished attempt answers
    rows, missing = [], 0
    for i in range(500):
        att = [F[i]] + [cells[c][i] for c in ("K_fresh", "K_fresh2") if i in cells[c]]
        if F[i]["cap_hit"] and i not in cells["K_fresh"]:
            missing += 1
            continue
        used = []
        for a in att:
            used.append(a)
            if not a["cap_hit"]:
                break
        if used[-1]["cap_hit"] and len(used) < 3 and i in cells["K_fresh"] and cells["K_fresh"][i]["cap_hit"] and i not in cells["K_fresh2"]:
            missing += 1
            continue
        rows.append({"i": i, "score": used[-1]["score"], "tokens": sum(a["n_generated"] for a in used), "attempts": len(used)})
    res["restart_row"] = {"n": len(rows), "missing": missing, "acc": S.acc([r["score"] for r in rows]) if rows else None,
                          "mean_tokens": float(np.mean([r["tokens"] for r in rows])) if rows else None,
                          "attempts_hist": {k: sum(r["attempts"] == k for r in rows) for k in (1, 2, 3)},
                          "rl_single_answer": {"acc": S.acc([RL[r["i"]]["score"] for r in rows]) if rows else None,
                                               "mean_tokens": float(np.mean([RL[r["i"]]["n_generated"] for r in rows])) if rows else None},
                          "restart_minus_rl": boot([r["score"] for r in rows], [RL[r["i"]]["score"] for r in rows]) if rows else None}
    res["T2"] = compare(cells["T2"], RL, "T2 (RL, T 1.0) vs n13 RL (T 0.6)")
    res["R1"] = compare(cells["R1"], F, "R1 (base F, rep 1.1) vs base-01 F")
    res["T3"] = compare(cells["T3"], P, "T3 (base plain, T 1.0) vs base-01 P")
    res["agree_selfcheck"] = R.agree("5.5", "\\dfrac{11}{2}") and R.agree("$x = 2$", "2") and not R.agree("5.5", "\\frac{11}{3}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--b01", required=True)
    ap.add_argument("--n13", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = readout(a.run, a.b01, a.n13)
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({"check": res["check"] and res["check"]["verdict"], "T1": res["T1"]["label"], "K": res["K"]["label"],
                      "n_records": res["n_records"]}, indent=1))


if __name__ == "__main__":
    main()
