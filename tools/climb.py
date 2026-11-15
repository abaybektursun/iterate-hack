# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""The record steps of the hill-climbing chart, with the finding behind each: which result raised the best base score.

  uv run tools/climb.py [benchmark] [--json]
  uv run tools/climb.py --selftest       checks the rule on a hand-made list of scores

Per benchmark (MATH-500 first, then alphabetical): the best base score, the best RL score and the gap, then every
record step, newest first, on two lines: the gain in points, previous best -> new best, the time of the result (UTC),
the result id, who posted it and the configuration; under it the finding, the first line of the result's text that is
not a score line, cut to 160 characters. --json prints load() instead.

The rule is the chart's (tools/view.py, hill): only base scores (the untrained model) count; a score whose
right/n and configuration already appeared on that benchmark is the same run reported twice and is dropped; a step is
a score whose percent is strictly above every earlier one, in the order the results were posted.
It reads the score rows (board.py score) and only the result items that set a record, and never writes.
"""
import json
import sys

from boto3.dynamodb.conditions import Key

import board
import team

FINDING_WIDTH = 160


def pct(score):
    return 100 * score["right"] / score["n"]


def records(scores):
    """{benchmark: (the base score rows that set a record, in order; the RL score row with the highest percent or None)}."""
    found = {}
    for name in dict.fromkeys(s["benchmark"] for s in scores):
        seen, top, steps = set(), -1, []
        for s in scores:
            if s["benchmark"] != name or s["model"] != "base" or (s["right"], s["n"], s["config"]) in seen:
                continue
            seen.add((s["right"], s["n"], s["config"]))  # as on the chart; a repeat is never strictly above, so no step changes
            if pct(s) > top:
                top = pct(s)
                steps.append(s)
        rl = max((s for s in scores if s["benchmark"] == name and s["model"] == "rl"), key=pct, default=None)
        if steps:
            found[name] = (steps, rl)
    return found


def finding(text):
    return next((line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("score:")), "")


def steps(scores, texts):
    """scores: the score rows in stored order; texts: {result id: the result's text}. Returns
    {benchmark: {"steps": [step, ...] in the order found, "rl": the best RL score or None}}, where a step is
    {result, who, result_at, config, right, n, pct, before, delta, tokens, finding} (before and delta are None for the
    first step) and "rl" is {result, who, result_at, config, right, n, pct, tokens}. Plain ints, floats and strings."""
    def row(s):
        tokens = s.get("tokens")
        return {"result": s["result"], "who": s["who"], "result_at": s["result_at"], "config": s["config"], "right": int(s["right"]),
                "n": int(s["n"]), "pct": round(float(pct(s)), 2), "tokens": None if tokens is None else int(tokens)}
    out = {}
    for name, (found, rl) in records(scores).items():
        out[name] = {"steps": [], "rl": row(rl) if rl else None}
        before = None
        for s in found:
            step = {**row(s), "before": before, "finding": finding(texts[s["result"]])}
            step["delta"] = None if before is None else round(step["pct"] - before, 2)
            out[name]["steps"].append(step)
            before = step["pct"]
    return out


def load():
    """steps() of the live board: every score row, and the text of each result that set a record."""
    scores = board.rows(KeyConditionExpression=Key("pk").eq("scores"))
    ids = {s["result"] for found, _ in records(scores).values() for s in found}
    texts = {i: team.table().get_item(Key={"pk": f"item#{i}", "sk": "item"})["Item"]["text"] for i in ids}
    return steps(scores, texts)


def order(names):
    return sorted(names, key=lambda name: (name != "MATH-500", name))


def show(climb):
    for name in order(climb):
        found, rl = climb[name]["steps"], climb[name]["rl"]
        best = found[-1]
        head = f"{name}  best base {best['pct']:.1f} % ({best['right']}/{best['n']})"
        if rl:
            gap = rl["pct"] - best["pct"]
            head += f", RL {rl['pct']:.1f} % ({rl['right']}/{rl['n']}, {rl['config']}), " + (f"{gap:.1f} points to go" if gap > 0 else "gap closed")
        print(head)
        for s in reversed(found):
            gain = f"+{s['delta']:.1f}  {s['before']:.1f} -> {s['pct']:.1f}" if s["before"] is not None else f"first        {s['pct']:.1f}"
            print(f"  {gain}  {s['result_at'][5:16].replace('T', ' ')}  {s['result']}  {s['who']}  {s['config']}")
            print(f"        {s['finding'][:FINDING_WIDTH]}")
        print()


def selftest():
    s = lambda result, model, right, n, config: {"result": result, "model": model, "benchmark": "B", "right": right, "n": n,
                                                 "config": config, "who": "x", "result_at": "2026-11-14T00:00:00Z"}
    scores = [s("r1", "base", 40, 100, "a"), s("r2", "base", 30, 100, "b"),  # lower later score: not a step
              s("r3", "rl", 70, 100, "c"), s("r4", "base", 50, 100, "d"),
              s("r5", "base", 50, 100, "d"),  # same right/n and configuration as r4: one run (also not strictly above)
              s("r6", "base", 50, 100, "e"),  # equal percent: not strictly above, not a step
              s("r7", "base", 60, 200, "f")]  # lower percent on another n: not a step
    texts = {r: f"score: base B 1/2 | x\n\n  finding of {r}\nmore" for r in ("r1", "r4")}
    got = steps(scores, texts)["B"]
    assert [x["result"] for x in got["steps"]] == ["r1", "r4"], got
    assert (got["steps"][1]["before"], got["steps"][1]["delta"], got["steps"][1]["finding"]) == (40.0, 10.0, "finding of r4"), got
    assert got["steps"][0]["before"] is None and got["rl"]["result"] == "r3", got
    json.dumps(got)
    print("climb selftest passed")


if __name__ == "__main__":
    args = sys.argv[1:]
    if {"--help", "-h"} & set(args):
        sys.exit(__doc__)
    if "--selftest" in args:
        selftest()
        sys.exit()
    climb = load()
    names = [a for a in args if not a.startswith("--")]
    if names:
        climb = {name: climb[name] for name in names}
    if "--json" in args:
        print(json.dumps(climb, indent=1))
    else:
        show(climb)
