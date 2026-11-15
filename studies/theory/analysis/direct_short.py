"""Direct test short-01 of run-02/f2-m01 (specs/SPEC_direct_short.md): share of the problems the cued base solves that
have a right sample of 2,000 tokens or fewer, hard328 against MATH-500, from the committed day1_3 rows.

    uv run --no-project --with numpy python studies/theory/analysis/direct_short.py --out studies/theory/results/direct/short-01
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DAY = ROOT / "studies/rlneurons/results/day1_3"
SETS = {
    "hard328": (DAY / "hard328_base_cue_s4r2-01/rows.jsonl", ROOT / "studies/rlneurons/data/rln3/hard.json"),
    "math500": (DAY / "math500_base_cue-01/rows.jsonl", ROOT / "studies/rlneurons/data/rln4/math500.json"),
}
CUTS = (1100, 2000, 4096)
B, SEED = 10000, 0


def boot(per_problem, stat):
    """Point value and 90 % percentile interval of stat over a bootstrap of problems (list of per-problem items)."""
    rng = np.random.default_rng(SEED)
    n = len(per_problem)
    draws = [stat([per_problem[i] for i in rng.integers(0, n, n)]) for _ in range(B)]
    lo, hi = np.percentile(draws, [5, 95])
    return {"value": round(float(stat(per_problem)), 4), "interval": [round(float(lo), 4), round(float(hi), 4)], "n": n}


def readout(name):
    rows_path, prob_path = SETS[name]
    rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
    by = defaultdict(list)
    for r in rows:
        by[r["problem_index"]].append(r)
    solved = {p: rs for p, rs in by.items() if any(r["score_v3"] == 1 for r in rs)}
    right_lens = [sorted(r["n_new"] for r in rs if r["score_v3"] == 1) for rs in solved.values()]
    out = {"rows": len(rows), "problems": len(by), "solved": len(solved),
           "right_rows": sum(len(x) for x in right_lens)}
    for c in CUTS:
        out[f"S({c})"] = boot(right_lens, lambda ps, c=c: np.mean([x[0] <= c for x in ps]))
        out[f"S({c})"]["count"] = sum(x[0] <= c for x in right_lens)
    # share of right rows of 2,000 tokens or fewer (bootstrap over problems, rows pooled)
    out["right_rows_share_le2000"] = boot(right_lens, lambda ps: sum(sum(v <= 2000 for v in x) for x in ps) / sum(len(x) for x in ps))
    out["median_right_n_new"] = boot(right_lens, lambda ps: np.median([v for x in ps for v in x]))
    # problems with a short right row: share of all their rows that are right, against the other solved problems
    short = [rs for rs in solved.values() if any(r["score_v3"] == 1 and r["n_new"] <= 2000 for r in rs)]
    other = [rs for rs in solved.values() if not any(r["score_v3"] == 1 and r["n_new"] <= 2000 for r in rs)]
    acc = lambda ps: sum(sum(r["score_v3"] for r in rs) for rs in ps) / sum(len(rs) for rs in ps)
    out["row_accuracy_on_problems_with_short_right"] = boot(short, acc)
    out["row_accuracy_on_solved_without_short_right"] = boot(other, acc)
    probs = json.loads(prob_path.read_text())
    text = {int(p["index"]): p["problem"] for p in probs}
    return out, solved, text


def strip(r):
    return {k: r[k] for k in ("problem_index", "sample", "attempt", "seed", "n_new", "cap_hit", "finish_reason", "extracted_v3", "score_v3", "gold")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out_dir = ROOT / ap.parse_args().out
    out_dir.mkdir(parents=True, exist_ok=False)

    res, solved_h, text_h = readout("hard328")
    res_m, _, _ = readout("math500")
    p1, c1 = res["S(2000)"], res_m["S(2000)"]
    if p1["interval"][0] >= 0.20 or c1["interval"][1] < 0.50:
        verdict = "refuted"
    elif p1["interval"][1] < 0.20 and c1["interval"][0] > 0.50:
        verdict = "holds"
    else:
        verdict = "undecidable"
    (out_dir / "readout.json").write_text(json.dumps(
        {"spec": "studies/theory/specs/SPEC_direct_short.md", "mechanism": "run-02/f2-m01",
         "claim": "under 20 % of the hard328 problems the cued base solves have a right sample of 2,000 tokens or fewer; over 50 % on MATH-500",
         "P1_hard328_S2000": p1, "C1_math500_S2000": c1, "verdict": verdict,
         "hard328": res, "math500": res_m, "bootstrap": {"draws": B, "seed": SEED, "level": 0.90, "unit": "solved problem"}},
        indent=1))

    # deciding group: hard328 right rows of 2,000 tokens or fewer
    short_rows = sorted((r for rs in solved_h.values() for r in rs if r["score_v3"] == 1 and r["n_new"] <= 2000),
                        key=lambda r: (r["problem_index"], r["sample"], r["attempt"]))
    with_short = sorted(p for p, rs in solved_h.items() if any(r["score_v3"] == 1 and r["n_new"] <= 2000 for r in rs))
    without = sorted(p for p in solved_h if p not in with_short)
    ex = lambda p: {"problem_index": p, "problem": text_h[p], "rows": [strip(r) for r in solved_h[p]]}
    (out_dir / "examples.json").write_text(json.dumps(
        {"counts_for_claim": {"why": "solved, no right row of 2,000 tokens or fewer", **ex(without[0])},
         "counts_against_claim": {"why": "solved, with a right row of 2,000 tokens or fewer", **ex(with_short[0])}}, indent=1))
    lines = ["# 10 raw rows of the deciding group (hard328 right rows, n_new <= 2,000)", "",
             f"{len(short_rows)} such rows on {len(with_short)} problems. Every 1 in {max(1, len(short_rows) // 10)} rows, in problem order.", ""]
    for r in short_rows[:: max(1, len(short_rows) // 10)][:10]:
        others = [(x["n_new"], x["score_v3"], x["extracted_v3"]) for x in solved_h[r["problem_index"]]]
        lines += [f"## problem {r['problem_index']}", "", text_h[r["problem_index"]], "",
                  "row: " + json.dumps(strip(r)), "", "all rows (n_new, right, extracted): " + json.dumps(others), ""]
    (out_dir / "reading.md").write_text("\n".join(lines))
    print(json.dumps({"verdict": verdict, "P1": p1, "C1": c1}, indent=1))


if __name__ == "__main__":
    main()
