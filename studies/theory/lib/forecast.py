# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Forecasts of the team's open GPU work (studies/theory/README.md, "Forecast runs").

  uv run studies/theory/lib/forecast.py make <folder>
      reads the open work items with their comments and every result and knowledge item (the board snapshot); one
      headless job turns the open items into targets (numbers they will report); two readers with no theory and one
      job per theory not refuted in the newest round (at most 6, survivors first, then by total gain) forecast every
      target (value, 90 % interval, reason). Writes targets.json, forecasts.json, forecasts.md, run.json. Fails if the
      folder exists.
  uv run studies/theory/lib/forecast.py score <folder>
      one headless job finds each target's measured value in the board items posted after the snapshot; each forecast
      is scored by the engine's log density against the equal mixture of the two readers, clipped to [-3, 3] nats.
      Writes scores.json and scores.md.

Every job is round.py's blind job: claude -p in an empty directory with Read and Write only, the model round.py gives
cross_predict.
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round as engine  # noqa: E402

ROOT = engine.ROOT
ROUND = ROOT / "studies/theory/results/engine/round-07"  # the newest round: its unrefuted theories forecast
READERS = ["reader-1", "reader-2"]
MAX_THEORIES = 6
THEORY = ("- theory.json: a theory of the team's results. Derive each forecast from the theory as written: say in the\n"
          "  reason which part of the theory gives the number. Where the theory implies nothing about a target, do not\n"
          "  guess: answer \"theory says nothing\" for it.\n")
NOTHING = (' For a target the theory says nothing about, write {"id": "t02", "value": null, "low": null, "high": null, '
           '"reason": "theory says nothing"}.')
engine.args = argparse.Namespace(model_all=None, workers=8)
for stage in ("forecast_targets", "forecast", "forecast_score"):
    engine.MODELS[stage] = engine.MODELS["cross_predict"]


def board(name, cutoff):
    """check.dump's snapshot (the result and knowledge items round.py's split reads): (before, after) the cutoff."""
    d = engine.tmp() / name
    engine.check.dump(d, cutoff, [])
    return engine.read(d / "before.jsonl"), engine.read(d / "after.jsonl")


def sh(*cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True).stdout


def flat(s):
    return " ".join(s.split())


def theories():
    m = json.loads((ROUND / "metrics_v4.json").read_text())["theories"]
    names = sorted((n for n, t in m.items() if t["state"] != "refuted"), key=lambda n: (m[n]["state"] != "survives", -m[n]["total_gain"]))
    return names[:MAX_THEORIES]


def check_targets(d, work):
    ts = json.loads((d / "targets.json").read_text())["targets"]
    errors = [f"{t['id']}: item {t['item']} is not an open work item" for t in ts if t["item"] not in work]
    errors += [f"{t['id']}: quote not found in {t['item']}: {t['quote'][:80]!r}" for t in ts
               if t["item"] in work and flat(t["quote"]) not in flat(work[t["item"]])]
    errors += [f"{t['id']}: missing {k}" for t in ts for k in ("cell", "unit", "what") if not t.get(k)]
    return "; ".join(errors) or (None if len({t["id"] for t in ts}) == len(ts) else "target ids repeat")


def check_forecasts(d, ids, theory):
    fs = json.loads((d / "forecasts.json").read_text())["forecasts"]
    if sorted(f["id"] for f in fs) != sorted(ids):
        return f"forecasts.json must hold every target id exactly once: {sorted(ids)}"
    for f in fs:
        if f["value"] is None and theory and f["low"] is None and f["high"] is None:
            continue
        if not all(engine.number(f[k]) for k in ("value", "low", "high")) or not f["low"] <= f["value"] <= f["high"]:
            return f"{f['id']}: value, low, high must be numbers with low <= value <= high" + (" (or all null)" if theory else "")


def make(folder):
    folder.mkdir(parents=True)  # fails if the folder exists
    utc = engine.time.strftime("%Y-%m-%dT%H:%M:%S", engine.time.gmtime())
    items, _ = board("board", "9999")
    ids = [line.split()[0] for line in sh("uv", "run", "tools/board.py", "ls", "work", "--n", "200").splitlines() if line.startswith("work-")]
    with ThreadPoolExecutor(8) as pool:
        work = dict(zip(ids, pool.map(lambda i: sh("uv", "run", "tools/board.py", "show", i), ids)))
    work_md = "".join(f"## {i}\n\n{text}\n" for i, text in work.items())
    common = {"DIRECTION.md": ROOT / "DIRECTION.md", "board.jsonl": "".join(json.dumps(i) + "\n" for i in items), "work.md": work_md}
    engine.run([engine.job("forecast_targets", "targets", common, {"targets.json": folder / "targets.json"},
                           lambda d: check_targets(d, work))], folder)
    targets = json.loads((folder / "targets.json").read_text())["targets"]
    tids = [t["id"] for t in targets]
    names = theories()
    out = engine.tmp() / "forecasts"
    jobs = [engine.job("forecast", r, {**common, "targets.json": folder / "targets.json"}, {"forecasts.json": out / f"{r}.json"},
                       lambda d: check_forecasts(d, tids, False), theory="", nothing="") for r in READERS]
    jobs += [engine.job("forecast", n, {**common, "targets.json": folder / "targets.json", "theory.json": ROUND / "theories" / f"{n}.json"},
                        {"forecasts.json": out / f"{n}.json"}, lambda d: check_forecasts(d, tids, True), theory=THEORY, nothing=NOTHING)
             for n in names]
    engine.run(jobs, folder)
    forecasts = {n: json.loads((out / f"{n}.json").read_text())["forecasts"] for n in READERS + names}
    (folder / "forecasts.json").write_text(json.dumps(forecasts, indent=1))
    md = [f"# Forecasts, {folder.name}\n\nBoard snapshot {utc} UTC. {len(targets)} targets; forecasters {', '.join(forecasts)}.\n"]
    for t in targets:
        md.append(f"\n## {t['id']} ({t['item']}): {t['what']}\n\nUnit: {t['unit']}. Cell: {json.dumps(t['cell'])}\n\n> {t['quote']}\n\n"
                  "| forecaster | value | 90 % interval | reason |\n|---|---|---|---|")
        for n, fs in forecasts.items():
            f = next(f for f in fs if f["id"] == t["id"])
            value, span = ("-", "") if f["value"] is None else (f"{f['value']:g}", f"[{f['low']:g}, {f['high']:g}]")
            md.append(f"| {n} | {value} | {span} | {f['reason']} |")
    (folder / "forecasts.md").write_text("\n".join(md) + "\n")
    (folder / "run.json").write_text(json.dumps({"commit": sh("git", "rev-parse", "--short", "HEAD").strip(), "command": " ".join(sys.argv),
                                                 "utc": utc, "round": str(ROUND.relative_to(ROOT)), "work_items": ids,
                                                 "targets": len(targets), "forecasters": list(forecasts), "job_dirs": str(engine.tmp())}, indent=1))
    print(f"{len(targets)} targets, {len(forecasts)} forecasters: {folder / 'forecasts.md'}")


def check_measured(d, tids, posted):
    ms = json.loads((d / "measured.json").read_text())["measured"]
    if sorted(m["id"] for m in ms) != sorted(tids):
        return f"measured.json must hold every target id exactly once: {sorted(tids)}"
    bad = [m["id"] for m in ms if m["value"] is not None and not (engine.number(m["value"]) and m["item"] in posted
                                                                  and flat(m["quote"]) in flat(posted[m["item"]]))]
    return f"{bad}: a measured value needs an item of posted.jsonl and a quote found in its text" if bad else None


def score(folder):
    run = json.loads((folder / "run.json").read_text())
    targets = json.loads((folder / "targets.json").read_text())["targets"]
    forecasts = json.loads((folder / "forecasts.json").read_text())
    tids = [t["id"] for t in targets]
    _, after = board("posted", run["utc"])
    posted = {i["id"]: i["text"] for i in after}
    d = engine.tmp() / "measured.json"
    engine.run([engine.job("forecast_score", "measured", {"targets.json": folder / "targets.json",
                                                          "posted.jsonl": "".join(json.dumps(i) + "\n" for i in after)},
                           {"measured.json": d}, lambda j: check_measured(j, tids, posted))], folder)
    ms = json.loads(d.read_text())["measured"]
    measured = {m["id"]: m["value"] for m in ms if m["value"] is not None}
    nulls = [{f["id"]: f for f in forecasts[r]} for r in READERS]
    per = {}
    for n, fs in forecasts.items():
        rows = engine.gain_rows([f for f in fs if f["value"] is not None], measured, nulls)
        for r in rows:
            r["inside"] = r["low"] <= r["measured"] <= r["high"]
        total = sum(r["gain"] for r in rows)
        per[n] = {"scored": len(rows), "inside": sum(r["inside"] for r in rows), "total_gain": round(total, 3),
                  "mean_gain": round(total / len(rows), 3) if rows else None, "rows": rows}
    surprise = [t for t in measured if not any(r["inside"] for p in per.values() for r in p["rows"] if r["id"] == t)]
    (folder / "scores.json").write_text(json.dumps({"scored_utc": engine.time.strftime("%Y-%m-%dT%H:%M:%S", engine.time.gmtime()),
                                                    "measured": ms, "forecasters": per, "outside_every_interval": surprise}, indent=1))
    md = [f"# Scores, {folder.name}\n\n{len(measured)} of {len(targets)} targets measured. Gain: log density of the forecast minus "
          "log density of the equal mixture of reader-1 and reader-2 at the measured value, clipped to [-3, 3] nats.\n",
          "| forecaster | scored | inside interval | total gain | mean gain |\n|---|---|---|---|---|"]
    md += [f"| {n} | {p['scored']} | {p['inside']} | {p['total_gain']} | {p['mean_gain']} |" for n, p in per.items()]
    md.append("\n| target | measured | item | outside every interval |\n|---|---|---|---|")
    md += [f"| {m['id']} | {m['value'] if m['value'] is not None else 'not posted yet'} | {m['item'] or ''} | "
           f"{'yes' if m['id'] in surprise else ''} |" for m in ms]
    (folder / "scores.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["make", "score"])
    parser.add_argument("folder", type=Path)
    a = parser.parse_args()
    {"make": make, "score": score}[a.command](a.folder)
