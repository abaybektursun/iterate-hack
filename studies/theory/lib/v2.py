# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Version 2 of the round's check and score (round 02 on). check.py still splits the board (dump) and holds round 01's score.

A theory is now scored on its own claims about the held-out targets, written by its author after the theory file is
fixed: claims/<theory>.jsonl, lines {"id": "t07", "value": 440, "low": 425, "high": 455}, only for targets the theory
speaks about. predictions/null-1.jsonl and null-2.jsonl hold a number for every target from two agents with no theory.

  uv run studies/theory/lib/v2.py check <round dir>
      check.py's quote checks, then: every import's source is in external.md; every claim names a target and has
      low <= value <= high.
  uv run studies/theory/lib/v2.py score <round dir>
      A claim is divergent when both nulls' numbers lie outside its interval: the theory says the default guess is wrong.
      win = divergent and the measured value is inside the interval; loss = divergent and it is outside.
      A theory is a candidate with wins >= 2 and wins > losses. It passes when, in addition, its net (wins - losses)
      is above the net of its reversal, claims/<theory>.rev.jsonl: the same theory with every effect reversed.
      Targets of the items listed in exposed.json (when the file exists) are left out: their numbers reached the
      agents by another way, e.g. a commit subject in the git status that Claude Code gives every subagent.
      Writes metrics_v2.json and prints the table.
"""
import json
import sys
from pathlib import Path

import check as v1
from check import read


def check(folder):
    v1.check(folder)
    external = (folder / "external.md").read_text()
    targets = {t["id"] for t in read(folder / "targets.jsonl")}
    wrong = []
    for path in sorted((folder / "theories").glob("*.json")):
        for imported in json.loads(path.read_text()).get("imports", []):
            if imported["source"] not in external:
                wrong.append(f"{path.name}: import source not in external.md: {imported['source']!r}")
    for path in sorted((folder / "claims").glob("*.jsonl")):
        for c in read(path):
            if c["id"] not in targets or not c["low"] <= c["value"] <= c["high"]:
                wrong.append(f"{path.name}: claim {c['id']} names no target or its value is outside its interval")
    if wrong:
        sys.exit("\n".join(wrong))
    print(f"imports and {len(list((folder / 'claims').glob('*.jsonl')))} claim files pass")


def tally(claims, value, nulls):
    rows = []
    for c in claims:
        inside = c["low"] <= value[c["id"]] <= c["high"]
        divergent = all(not c["low"] <= null[c["id"]] <= c["high"] for null in nulls)
        rows.append({"id": c["id"], "measured": value[c["id"]], "value": c["value"], "low": c["low"], "high": c["high"],
                     "nulls": [null[c["id"]] for null in nulls], "divergent": divergent, "inside": inside})
    count = lambda divergent, inside: sum(r["divergent"] == divergent and r["inside"] == inside for r in rows)
    wins, losses = count(True, True), count(True, False)
    return {"claims": len(rows), "wins": wins, "losses": losses, "net": wins - losses,
            "agree_inside": count(False, True), "agree_outside": count(False, False), "rows": rows}


def score(folder):
    exposed = json.loads((folder / "exposed.json").read_text())["items"] if (folder / "exposed.json").exists() else []
    targets = read(folder / "targets.jsonl")
    value = {t["id"]: t["value"] for t in targets if t["item"] not in exposed}
    nulls = [{p["id"]: p["value"] for p in read(folder / "predictions" / f"{name}.jsonl")} for name in ("null-1", "null-2")]
    assert all(len(null) == len(targets) for null in nulls), "a null does not cover every target"
    tallies = {path.stem: tally([c for c in read(path) if c["id"] in value], value, nulls) for path in sorted((folder / "claims").glob("*.jsonl"))}
    theories = {}
    for name, t in tallies.items():
        if name.endswith(".rev"):
            continue
        candidate = t["wins"] >= 2 and t["wins"] > t["losses"]
        reversal = tallies.get(name + ".rev")
        state = "fails" if not candidate else "needs reversal" if reversal is None else "passes" if t["net"] > reversal["net"] else "fails: reversal as good"
        theories[name] = {**t, "state": state, "reversal": reversal}
    (folder / "metrics_v2.json").write_text(json.dumps({"targets": len(value), "exposed_items": exposed, "theories": theories}, indent=1) + "\n")
    print(f"{len(value)} targets. Per theory: claims, divergent wins and losses, non-divergent claims inside and outside, state")
    for name, t in sorted(theories.items(), key=lambda kv: -kv[1]["net"]):
        rev = f"   reversal +{t['reversal']['wins']} -{t['reversal']['losses']}" if t["reversal"] else ""
        print(f"{name:16} claims {t['claims']:2}   +{t['wins']} -{t['losses']}   agree {t['agree_inside']} in, {t['agree_outside']} out   {t['state']}{rev}")


if __name__ == "__main__":
    {"check": check, "score": score}[sys.argv[1]](Path(sys.argv[2]))
