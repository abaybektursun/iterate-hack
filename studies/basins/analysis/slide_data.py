"""Writes tools/demo_ali_data.py, the data of the three slides at /demo/ali/ (tools/demo_ali.py).

  python3 studies/basins/analysis/slide_data.py <run folder of the swarm map>

The run folder is one run of the swarm idea map (studies/basins/results/swarm/<run>/) and must hold map.json,
summary.json and run.json. From it come the board items of the snapshot (id, kind, person, time, the judge's
position and cluster, the first 260 characters of the text, the ids of the items each one builds on), the cluster
names and two counts of the idea tree. The controls and the judge's possible directions are left out.

Positions, as on the earlier map pages of the study: the judge's map (all its nodes) is turned to its principal axes,
and each axis is then 60 % rank and 40 % linear, from 0 to 1, so that the dense corner of the map is readable.

The scores are read now from the site (https://monitor.invariant.team/data): the board's score rows and plain rows.
For MATH-500 they are reduced by the rule of the board's chart (tools/climb.py): in posting order, a repeated right/n
and configuration is dropped, and a record is a score strictly above every earlier one. Kept: the records of the
untrained base and of the RL-Zero-Math model, the other base scores whose result is in the snapshot, every score row
of a result in the snapshot (for the idea tree), and the best row of one model that is not the untrained base (OTHER),
named in the note of slide 3.

The script stops with an error if a record's result is not in the snapshot or the row of OTHER is not found. It never
writes to the board.
"""
import datetime
import json
import math
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SITE = "https://monitor.invariant.team/data"
BENCH = "MATH-500"
OTHER = "result-818c20"  # Think-SFT with the cue and a vote over 4: not the untrained base, named in the note of slide 3
OUT = REPO / "tools/demo_ali_data.py"


def short(name):
    """A cluster name in two words: "Voting restarts and inference allocation" -> "Voting restarts"."""
    w = name.split()
    return f"{w[0]} & {w[2]}" if w[1] == "and" else " ".join(w[:2])


def layout(nodes):
    """{id: (x, y)} from 0 to 1: the map turned to its principal axes, each axis 60 % rank and 40 % linear."""
    mx, my = sum(n["x"] for n in nodes) / len(nodes), sum(n["y"] for n in nodes) / len(nodes)
    sxx, syy = sum((n["x"] - mx) ** 2 for n in nodes), sum((n["y"] - my) ** 2 for n in nodes)
    turn = 0.5 * math.atan2(2 * sum((n["x"] - mx) * (n["y"] - my) for n in nodes), sxx - syy)

    def blend(vals):
        lo, hi = min(vals), max(vals)
        rank = {i: k / (len(vals) - 1) for k, i in enumerate(sorted(range(len(vals)), key=lambda i: vals[i]))}
        return [0.6 * rank[i] + 0.4 * (v - lo) / (hi - lo) for i, v in enumerate(vals)]

    along = blend([(n["x"] - mx) * math.cos(turn) + (n["y"] - my) * math.sin(turn) for n in nodes])
    across = blend([-(n["x"] - mx) * math.sin(turn) + (n["y"] - my) * math.cos(turn) for n in nodes])
    return {n["id"]: (a, b) for n, a, b in zip(nodes, along, across)}


def utc(ns, form):
    return datetime.datetime.fromtimestamp(ns / 1e9, datetime.timezone.utc).strftime(form)


def main(run):
    run = Path(run)
    board = json.loads((run / "map.json").read_text())
    summary = json.loads((run / "summary.json").read_text())
    meta = json.loads((run / "run.json").read_text())
    items = sorted((n for n in board["nodes"] if n["kind"] != "possible" and not n["control_of"]), key=lambda n: n["at_ns"])
    ids = {n["id"] for n in items}
    first, last = items[0]["at_ns"], items[-1]["at_ns"]
    hours = {n["id"]: (n["at_ns"] - first) / 3.6e12 for n in items}
    at = layout(board["nodes"])
    nodes = [{"id": n["id"], "kind": n["kind"], "who": n["who"], "t": round(hours[n["id"]], 4), "x": round(at[n["id"]][0], 4),
              "y": round(at[n["id"]][1], 4), "b": n["basin"], "text": n["text"][:260],
              "parents": [p["id"] for p in n["parents"] if p["id"] in ids]} for n in items]

    with urllib.request.urlopen(urllib.request.Request(SITE, headers={"User-Agent": "iterate-hack slide_data"}), timeout=30) as r:
        live = json.loads(r.read())
    read_at = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M UTC, %-d %b")
    rows = sorted(live["scores"], key=lambda s: s["sk"])
    tries, per_item = [], {}

    def records(model):
        seen, top, out = set(), -1, []
        for s in rows:
            key = (s["right"], s["n"], s["config"])
            if s["benchmark"] != BENCH or s["model"] != model or key in seen:
                continue
            seen.add(key)
            row = {"id": s["result"], "right": s["right"], "n": s["n"], "config": s["config"], "tokens": s["tokens"], "who": s["who"]}
            if 100 * s["right"] / s["n"] > top:
                top = 100 * s["right"] / s["n"]
                if s["result"] not in ids:
                    sys.exit(f"record {s['result']} {s['right']}/{s['n']} ({model}) is not in the snapshot of {run}: the map needs a newer run")
                plain = live["plain"].get(f"{s['result']}#{BENCH}#{s['right']}/{s['n']}", {})
                out.append({**row, "t": round(hours[s["result"]], 4), "title": plain.get("title", ""), "what": plain.get("what", ""),
                            "caveat": plain.get("caveat", "")})
            elif model == "base" and s["result"] in ids:
                tries.append({**row, "t": round(hours[s["result"]], 4)})
        return out

    base, rl = records("base"), records("rl")
    for s in rows:  # every score row of a result on the map, one row per benchmark, right/n and configuration
        if s["result"] in ids:
            row = {"model": s["model"], "benchmark": s["benchmark"], "right": s["right"], "n": s["n"], "config": s["config"]}
            if row not in per_item.setdefault(s["result"], []):
                per_item[s["result"]].append(row)
    other = sorted((s for s in rows if s["result"] == OTHER and s["benchmark"] == BENCH), key=lambda s: (-s["right"], s["sk"]))
    if not other or "vote over 4" not in other[0]["config"]:
        sys.exit(f"the row of {OTHER} on {BENCH} was not found in {SITE}")

    mark = re.search(r'claude:\s*"([^"]+)"', (REPO / "tools/architecture.py").read_text()).group(1)
    data = {
        "run": run.name, "judge": meta["judge"],
        "snapshot": f"{run.name} (board at {utc(last, '%H:%M')} UTC, {len(nodes)} items)",
        "t0_min": round(int(utc(first, "%H")) * 60 + int(utc(first, "%M")) + int(utc(first, "%S")) / 60, 3),
        "span_h": round(hours[items[-1]["id"]], 4),
        "basins": [{"name": n, "short": short(n)} for n in board["names"]],
        "tree": {"max_depth": summary["tree"]["max_depth"], "explicit_links": summary["tree"]["explicit_links"]},
        "climb": {"bench": BENCH, "read": read_at, "base": base, "rl": rl, "tries": tries,
                  "other": {"id": OTHER, "right": other[0]["right"], "n": other[0]["n"], "config": other[0]["config"],
                            "at": utc(int(other[0]["sk"].split("#")[0]), "%H:%M UTC, %-d %b")}},
        "scores": per_item, "mark": mark, "nodes": nodes,
    }
    text = "{\n" + ",\n".join(
        f"{json.dumps(k)}: " + ("[\n" + ",\n".join(json.dumps(n, ensure_ascii=False) for n in v) + "\n]" if k == "nodes" else json.dumps(v, ensure_ascii=False))
        for k, v in data.items()) + "\n}"
    if "'''" in text:
        sys.exit("the data holds ''' and cannot be written as a raw string")
    OUT.write_text('"""The data of the slides at /demo/ali/ (tools/demo_ali.py): the board items of one run of the swarm idea map and the\n'
                   "board's MATH-500 score rows. Written by studies/basins/analysis/slide_data.py from the run folder named in \"run\";\n"
                   'the scores were read from the site at the time in "climb"."read". Do not edit by hand: run the script again.\n"""\n'
                   "import json\n\nDATA = json.loads(r'''" + text + "''')\n")
    print(f"{OUT.relative_to(REPO)}: {len(nodes)} items, {sum(len(n['parents']) for n in nodes)} links, {len(base)} base records "
          f"({base[0]['right']} to {base[-1]['right']} of {base[-1]['n']}), RL best {rl[-1]['right']}, {len(tries)} other base scores, read {read_at}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main(sys.argv[1])
