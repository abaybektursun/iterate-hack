"""Direct test wrongagree-01 (rival pair round-14/s5), specs/SPEC_direct_wrongagree.md.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_wrongagree

Run from the repository root. Pooled share of same-problem pairs of wrong answer-bearing samples that agree, on the
cued base's contested MATH-500 problems (12 stored T 1.0 samples, rows of result-1c9e40).
"""
import functools
import json
import pathlib
import re
import subprocess
from datetime import datetime, timezone

import numpy as np

from studies.rlneurons.analysis.votek import agree_table, vote
from studies.rlneurons.lib import rln4_lib as R

SRCS = [pathlib.Path("studies/rlneurons/results/votek/math500_base_cue-01"),
        pathlib.Path("studies/rlneurons/results/votek/math500_base_cue-02"),
        pathlib.Path("studies/rlneurons/results/day1_3/math500_base_cue-01")]
OUT = pathlib.Path("studies/theory/results/direct/wrongagree-01")
B, NULL_DRAWS = 10_000, 200
RANGES = {"a": [0.07, 0.3], "b": [0.42, 1.0], "null": [0.0, 0.05]}


# Gold type: is_int of studies/theory/results/engine/round-07/tests/r7-m09/p2.py. That file runs its main() on import,
# so its three functions are repeated here unchanged.
def wholly_boxed_inside(s):
    pre = "\\boxed{"
    if not (s.startswith(pre) and s.endswith("}")):
        return None
    depth = 0
    for i in range(len(pre) - 1, len(s)):
        c = s[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[len(pre):i] if i == len(s) - 1 else None
    return None


def normalise(g):
    s = g.strip().replace("$", "")
    s = re.sub(r"\s+", "", s)
    inside = wholly_boxed_inside(s)
    if inside is not None:
        s = inside
    s = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", s)
    return s


def is_int(g):
    return re.fullmatch(r"-?\d+", normalise(g)) is not None


@functools.lru_cache(maxsize=None)
def agree(x, y):
    """The team vote's comparison (votek.agree_table): rln4_lib.agree on norm_v3 of both answers."""
    return R.agree(R.norm_v3(x), R.norm_v3(y))


def load():
    per = {}
    for d in SRCS:
        f = d / "rows.jsonl"
        if not f.exists():
            continue
        for line in open(f):
            r = json.loads(line)
            if r.get("attempt", 0) != 0 or not 0 <= r["sample"] <= 11:
                continue
            per.setdefault(r["problem_index"], {}).setdefault(r["sample"], {**r, "_src": str(d)})
    probs = sorted(per)
    assert len(probs) == 500 and all(sorted(per[p]) == list(range(12)) for p in probs)
    return {p: [per[p][s] for s in range(12)] for p in probs}


def bearing(r):
    return r["cap_hit"] is not True and r["finish_reason"] != "length" and (r["extracted_v3"] or "").strip() != ""


def pair_counts(W):
    """(agreeing pairs, pairs) over all unordered pairs of the answer strings W."""
    a = sum(agree(W[i], W[j]) for i in range(len(W)) for j in range(i + 1, len(W)))
    return a, len(W) * (len(W) - 1) // 2


def pooled(W, P):
    c = np.array([pair_counts(W[p]) for p in P], float)
    return c[:, 0].sum() / c[:, 1].sum(), c


def verdict(ci, rng_, n):
    if n < 50:
        return "undecided"
    if rng_[0] <= ci[0] and ci[1] <= rng_[1]:
        return "holds"
    return "undecided" if ci[1] >= rng_[0] and ci[0] <= rng_[1] else "refuted"


def main():
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    rows = load()
    probs = sorted(rows)
    srcs = sorted({x["_src"] for p in probs for x in rows[p]})

    # Instrument check 1: the team vote on these kept rows reproduces result-1c9e40 (446 over samples 0-3, 466 over 12).
    same = {p: agree_table(rows[p]) for p in probs}
    n4 = sum(vote(rows[p], same[p], range(4))["score"] for p in probs)
    n12 = sum(vote(rows[p], same[p], range(12))["score"] for p in probs)
    assert (n4, n12) == (446, 466), (n4, n12)

    W, nR = {}, {}
    for p in probs:
        b = [x for x in rows[p] if bearing(x)]
        W[p] = [x["extracted_v3"] for x in b if x["score_v3"] == 0]
        nR[p] = sum(x["score_v3"] == 1 for x in b)
        assert all(x["score_v3"] in (0, 1) for x in b)
    P = [p for p in probs if nR[p] >= 1 and len(W[p]) >= 2]
    n = len(P)

    # Instrument check 2: planted inputs. One string per problem gives 1; distinct non-matching strings give 0.
    one, _ = pooled({p: ["\\text{plantedA}"] * len(W[p]) for p in P}, P)
    dist, _ = pooled({p: [f"\\text{{planted{p}x{i}}}" for i in range(len(W[p]))] for p in P}, P)
    assert (one, dist) == (1.0, 0.0), (one, dist)
    # Instrument check 3: within-problem agreement here equals the team's agree_table on the same samples.
    for p in P:
        idx = [s for s in range(12) if bearing(rows[p][s]) and rows[p][s]["score_v3"] == 0]
        assert pair_counts(W[p])[0] == sum(same[p][idx[i]][idx[j]] for i in range(len(idx)) for j in range(i + 1, len(idx))), p

    stat, c = pooled(W, P)
    rng = np.random.default_rng(0)
    ix = rng.integers(0, n, (B, n))
    bs = c[ix, 0].sum(1) / c[ix, 1].sum(1)
    ci = [round(float(np.percentile(bs, 5)), 4), round(float(np.percentile(bs, 95)), 4)]

    # Null: cross-problem pairs matched on gold type (integer or not).
    gold = {p: rows[p][0]["gold"] for p in P}
    gt = {p: is_int(gold[p]) for p in P}
    nrng = np.random.default_rng(1)
    null_vals = []
    for _ in range(NULL_DRAWS):
        a = t = 0
        for p in P:
            pool = [q for q in P if q != p and gt[q] == gt[p]]
            q = pool[nrng.integers(len(pool))]
            a += sum(agree(x, y) for x in W[p] for y in W[q])
            t += len(W[p]) * len(W[q])
        null_vals.append(a / t)
    null = float(np.mean(null_vals))

    v = {k: verdict(ci, RANGES[k], n) for k in ("a", "b")}

    # Descriptive: share of wrong answers in the problem's largest wrong group; share of wrong answers that repeat.
    top, rep = [], []
    for p in P:
        w = W[p]
        sizes = [sum(agree(x, y) or x == y for y in w) for x in w]
        top.append(max(sizes) / len(w))
        rep += [s >= 2 for s in sizes]

    per = {str(p): {"right": nR[p], "wrong": len(W[p]), "agree_pairs": int(c[i, 0]), "pairs": int(c[i, 1]),
                    "gold_is_int": gt[p], "largest_wrong_share": round(top[i], 3)} for i, p in enumerate(P)}
    metrics = {
        "mechanisms": ["round-14/s5-a", "round-14/s5-b"], "spec": "studies/theory/specs/SPEC_direct_wrongagree.md",
        "plan": "studies/theory/results/wide/round-14/jobs/rivals-s5.json", "sources_listed": [str(d) for d in SRCS],
        "sources_used": srcs,
        "statistic": "pooled share of same-problem pairs of wrong answer-bearing samples that agree under rln4_lib.agree (norm_v3 on both, as votek.agree_table)",
        "check_team_vote_k4_samples_0_3": n4, "check_team_vote_k12": n12,
        "check_planted_one_string": one, "check_planted_distinct": dist,
        "n": n, "unit": "contested problems (>= 1 right and >= 2 wrong answer-bearing samples of 12)",
        "agree_pairs": int(c[:, 0].sum()), "pairs": int(c[:, 1].sum()), "wrong_answers": int(sum(len(W[p]) for p in P)),
        "value": round(float(stat), 4), "ci90": ci,
        "bootstrap": "10,000 resamples of contested problems, numpy default_rng(0), pooled ratio, 5th-95th percentile",
        "null_value": round(null, 4), "null_draws_5_95": [round(float(np.percentile(null_vals, 5)), 4), round(float(np.percentile(null_vals, 95)), 4)],
        "null": "each problem's wrong answers paired with all wrong answers of one other contested problem with the same gold type (is_int of r7-m09 p2.py), pooled, mean of 200 draws (default_rng(1))",
        "ranges": RANGES, "verdict": v,
        "rule": "interval wholly inside a rival's range: holds; touching it but not inside: undecided; not touching: refuted; n >= 50",
        "descriptive": {"mean_largest_wrong_group_share": round(float(np.mean(top)), 4),
                        "share_wrong_answers_that_repeat": round(float(np.mean(rep)), 4),
                        "problems_with_any_agreeing_pair": int(sum(c[:, 0] > 0)),
                        "gold_is_int_problems": int(sum(gt.values()))},
        "per_problem": per,
    }
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    def item(p, counts, why):
        return {"problem_index": p, "counts_for_statistic": counts, "why": why, "gold": rows[p][0]["gold"],
                "samples": [{k: rows[p][s][k] for k in ("sample", "extracted_v3", "score_v3", "cap_hit", "finish_reason")} for s in range(12)],
                **({"agree_pairs": per[str(p)]["agree_pairs"], "pairs": per[str(p)]["pairs"]} if counts else {})}

    yes = next(P[i] for i in range(n) if 0 < c[i, 0] < c[i, 1])
    no = next(p for p in probs if p not in P and nR[p] >= 1 and len(W[p]) == 1)
    (OUT / "examples.json").write_text(json.dumps([
        item(yes, True, "contested: right and wrong answer-bearing samples; its wrong pairs enter the pooled ratio"),
        item(no, False, "only 1 wrong answer-bearing sample: no wrong pair, not contested")], indent=1) + "\n")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({"spec": metrics["spec"], "commit": commit, "board": "work-0cf63d",
        "command": "uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_wrongagree",
        "inputs": srcs, "time": datetime.now(timezone.utc).isoformat(timespec="seconds")}, indent=1) + "\n")
    print({k: v for k, v in metrics.items() if k != "per_problem"})


if __name__ == "__main__":
    main()
