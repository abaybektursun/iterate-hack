"""Per-problem comparison of T1 (base with cue, T 1.0) and T2 (RL, T 1.0) on MATH-500 under grader v3, on saved rows only.

    python -m studies.rlneurons.analysis.rln4_t1_t2_items <T1.jsonl> <T2.jsonl> <out dir>

Each cell file holds one row per problem (problem_index, unique_id, gold, text, cap_hit, n_generated). Every text is scored
with rln4_lib.grade_v3. Written into <out dir>, which must not exist yet:
  per_problem.json  one row per problem: problem_index, subject (from unique_id in data/rln4/math500.json), cell (both,
                    base_only, rl_only, neither), t1_right, t2_right, t1_cap_hit, t2_cap_hit, t1_generated_tokens,
                    t2_generated_tokens
  metrics.json      per cell: right, cap hits, generated tokens of right and of wrong answers (n, median, 90th percentile),
                    and the wrong count among answers of at most SHORT tokens; the 2x2 of right and wrong
The 90th percentile is the sorted value at index round(0.9 * (n - 1)). Fail loud: no try/except, no fallback.
"""
import json
import pathlib
import statistics
import sys

from studies.rlneurons.lib import rln4_lib as R

MATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "rln4" / "math500.json"
SHORT = {"t1": 2000, "t2": 4000}        # generated tokens; the limits of the "short answer" counts
CELL = {(1, 1): "both", (1, 0): "base_only", (0, 1): "rl_only", (0, 0): "neither"}


def load(path, problems):
    rows = {}
    for line in open(path):
        r = json.loads(line)
        i = r["problem_index"]
        assert i not in rows, f"{path}: problem {i} twice"
        p = problems[i]
        assert r["gold"] == p["answer"] and r["unique_id"] == p["unique_id"], f"{path}: problem {i} differs from {MATH}"
        rows[i] = {"right": int(R.grade_v3(r["gold"], r["text"])["score_v3"]), "cap_hit": bool(r["cap_hit"]),
                   "tokens": r["n_generated"]}
    assert sorted(rows) == sorted(problems), f"{path}: {len(rows)} rows"
    return rows


def tokens(rows, right):
    xs = sorted(r["tokens"] for r in rows.values() if r["right"] == right)
    return {"n": len(xs), "median": statistics.median(xs), "p90": xs[round(0.9 * (len(xs) - 1))]}


def summary(rows, limit):
    short = [r for r in rows.values() if r["tokens"] <= limit]
    return {"right": sum(r["right"] for r in rows.values()), "cap_hits": sum(r["cap_hit"] for r in rows.values()),
            "tokens_right": tokens(rows, 1), "tokens_wrong": tokens(rows, 0),
            "short": {"max_tokens": limit, "n": len(short), "wrong": sum(1 - r["right"] for r in short)}}


def main():
    t1_path, t2_path, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
    problems = {p["index"]: p for p in json.load(open(MATH))}
    a, b = load(t1_path, problems), load(t2_path, problems)
    table = [{"problem_index": i, "subject": problems[i]["unique_id"].split("/")[1], "cell": CELL[a[i]["right"], b[i]["right"]],
              "t1_right": a[i]["right"], "t2_right": b[i]["right"], "t1_cap_hit": a[i]["cap_hit"], "t2_cap_hit": b[i]["cap_hit"],
              "t1_generated_tokens": a[i]["tokens"], "t2_generated_tokens": b[i]["tokens"]} for i in sorted(problems)]
    metrics = {"n": len(table), "grader": "v3 (rln4_lib.grade_v3)", "t1": summary(a, SHORT["t1"]), "t2": summary(b, SHORT["t2"]),
               "two_by_two": {name: sum(row["cell"] == name for row in table) for name in CELL.values()}}
    out.mkdir(parents=True)
    (out / "per_problem.json").write_text("[\n" + ",\n".join(json.dumps(row) for row in table) + "\n]\n")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
