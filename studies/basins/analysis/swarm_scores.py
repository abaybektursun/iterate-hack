"""Swarm map, leaderboard step (laptop, one judge call): scored configurations from the board's result items.

    python3 -m studies.basins.analysis.swarm_scores runs/swarm/judge-<t> --model gpt-6.1-sol

Reads the result items in <judge>/nodes.json and asks the judge for every scored configuration in them (model,
method, setting, benchmark, n, score in %). Every row must carry a quote copied from the item that contains the
number; a row whose quote is not in the item text stops the script. Writes <judge>/scores.json. Numbers are as
posted on the board, not re-verified at their artifacts.
"""
import argparse
import json
import pathlib

from studies.basins.analysis import swarm_judge as J

PROMPT = """Below are result posts from a research team's board. Extract every scored configuration: one row per
distinct (model, method, setting, benchmark) with a score. Skip rows that are differences between two
configurations, tool or team-process measurements, and counts that are not a benchmark score.

{items}

Reply with JSON only: {{"rows": [{{"item": "<result id>", "model": "base" or "rl", "method": "<e.g. opening cue,
plain prompt, cue + restart>", "setting": "<e.g. T 1.0 / top-p 1.0>", "benchmark": "<e.g. MATH-500>", "n": <int>,
"correct": <int or null>, "score_pct": <number>, "grader": "<e.g. v3>", "quote": "<exact substring of the item that
contains the score>"}}, ...]}}"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("judge")
    ap.add_argument("--model", required=True)
    args = ap.parse_args()
    J.BACKEND, J.MODEL = "openai", args.model
    d = pathlib.Path(args.judge)
    nodes = [n for n in json.loads((d / "nodes.json").read_text()) if n["kind"] == "result" and not n.get("control_of")]
    text = {n["id"]: n["text"] for n in nodes}
    rows = J.ask(PROMPT.format(items="\n\n".join(f"{n['id']}: {n['text']}" for n in nodes)), d / "calls" / "scores.txt")["rows"]
    for r in rows:
        assert r["item"] in text, f"unknown item {r['item']}"
        assert r["quote"] in text[r["item"]], f"quote not in {r['item']}: {r['quote']!r}"
        assert str(r["score_pct"]).rstrip("0").rstrip(".") in r["quote"].replace(" ", "") or (
            r.get("correct") is not None and str(r["correct"]) in r["quote"]), f"score not in quote: {r}"
    (d / "scores.json").write_text(json.dumps(rows, indent=1))
    for r in sorted(rows, key=lambda r: -r["score_pct"]):
        print(f"{r['score_pct']:6.1f}  {r['model']:4s}  {r['method'][:28]:28s}  {r['setting'][:22]:22s}  {r['benchmark']}  n={r['n']}  {r['item']}")
