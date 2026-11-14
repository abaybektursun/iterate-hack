"""RLN-4 T2 and T3 readout (Modal runs modal_t2-01, modal_t3-01; SPEC4 Deviations), on saved rows only.

    python -m studies.rlneurons.analysis.rln4_temp --rl <n13 rl_math500.jsonl> --t1 <base_rl-02 T1.jsonl> --p <base-01 P_math500.jsonl>
        --t2 <T2.jsonl> [--t3 <T3.jsonl>] --out <json>

Per cell: right (grader v1, v2 beside it), cap hits, loops by rule A, mean generated tokens (n_new, prefix not counted). Paired
differences over problems, in points, with n13_score.paired_bootstrap (2,000 resamples, seed 0, 95 % percentile): T2 - RL at T 0.6
and T1 - T2, overall and by quartile of the RL answer length at T 0.6 (n_new in n13's file); T3 - base P at T 0.6. One right and
one wrong example per cell (prompt tail, answer tail, extracted answer, its probability). Fail loud: no try/except, no fallback.
"""
import argparse
import json
import pathlib

import numpy as np

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R
from studies.rlneurons.analysis.rln4_analyze import bank, boot, v2

MATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "rln4" / "math500.json"


def summary(c):
    rs = list(c.values())
    return {"n": len(rs), "right_v1": sum(r["score"] for r in rs), "right_v2": sum(v2(r) for r in rs), "cap_hits": sum(r["cap_hit"] for r in rs),
            "loop_A": sum((r["onset_A_char"] if "onset_A_char" in r else R.onset_lines(r["text"])) is not None for r in rs),
            "mean_n_new": float(np.mean([r["n_new"] for r in rs]))}


def diff(a, b, idx):
    return {"acc": boot([a[i]["score"] for i in idx], [b[i]["score"] for i in idx]),
            "acc_v2": boot([v2(a[i]) for i in idx], [v2(b[i]) for i in idx]),
            "cap_hits": boot([a[i]["cap_hit"] for i in idx], [b[i]["cap_hit"] for i in idx])}


def by_quartile(a, b, q):
    out = {"all": diff(a, b, sorted(set(a) & set(b)))}
    for k in range(4):
        out[f"Q{k + 1}"] = diff(a, b, sorted(i for i in set(a) & set(b) if q[i] == k))
    return out


def examples(c, math):
    out = {}
    for want, name in ((1, "right"), (0, "wrong")):
        r = next(c[i] for i in sorted(c) if c[i]["score"] == want)
        out[name] = {"problem_index": r["problem_index"], "seed": r["seed"], "gold": r["gold"], "extracted": r["extracted"],
                     "answer_prob": r.get("answer_prob"), "cap_hit": r["cap_hit"], "n_new": r["n_new"],
                     "prompt_tail": S.TEMPLATE["pair1"].format(problem=math[r["problem_index"]]["problem"])[-200:],
                     "answer_tail": r["text"][-400:]}
    return out


def main():
    ap = argparse.ArgumentParser()
    for k in ("rl", "t1", "p", "t2", "out"):
        ap.add_argument(f"--{k}", required=True)
    ap.add_argument("--t3")
    a = ap.parse_args()
    math = json.loads(MATH.read_text())
    cells = {"RL_T0.6": bank(a.rl), "T1": bank(a.t1), "P_T0.6": bank(a.p), "T2": bank(a.t2)}
    if a.t3:
        cells["T3"] = bank(a.t3)
    for name in ("RL_T0.6", "T1", "P_T0.6"):
        assert sorted(cells[name]) == list(range(500)), name
    rl_len = {i: r["n_new"] for i, r in cells["RL_T0.6"].items()}
    edges = np.percentile(list(rl_len.values()), [25, 50, 75])
    q = {i: int(np.searchsorted(edges, n, side="right")) for i, n in rl_len.items()}
    res = {"cells": {k: summary(v) for k, v in cells.items()},
           "quartiles": {"edges_n_new_rl_T0.6": edges.tolist(), "n": [sum(v == k for v in q.values()) for k in range(4)]},
           "T2_minus_RL_T0.6": by_quartile(cells["T2"], cells["RL_T0.6"], q),
           "T1_minus_T2": by_quartile(cells["T1"], cells["T2"], q),
           "examples": {k: examples(cells[k], math) for k in cells if k in ("T2", "T3")}}
    for k in ("T2", "T3"):
        if k in cells:
            res["cells"][k]["by_quartile"] = [summary({i: r for i, r in cells[k].items() if q[i] == j}) for j in range(4)]
    if "T3" in cells:
        res["T3_minus_P_T0.6"] = by_quartile(cells["T3"], cells["P_T0.6"], q)
        res["T1_minus_T3"] = by_quartile(cells["T1"], cells["T3"], q)
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({"cells": {k: {x: y for x, y in v.items() if x != "by_quartile"} for k, v in res["cells"].items()},
                      "quartiles": res["quartiles"],
                      **{d: {k: [v["acc"]["diff"], v["acc"]["ci95"], v["acc"]["n"]] for k, v in res[d].items()}
                         for d in res if d.endswith(("RL_T0.6", "T2", "P_T0.6", "T3")) and d != "cells"}}, indent=1))


if __name__ == "__main__":
    main()
