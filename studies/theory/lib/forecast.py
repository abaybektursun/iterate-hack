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
      --propose N: then one job, given the readers' forecasts and the round's facts.json and graveyard.json, writes N
      mechanisms about the targets (mechanisms.json); each forecast says whether it agrees with the readers and why
      (vs_readers). They forecast as f2-m01 ... and are scored like the rest.
      --lens TEXT: the family of causes the N mechanisms must come from (run-03 to run-08 ran one lens each).
  uv run studies/theory/lib/forecast.py score <folder>
      one headless job finds each target's measured value in the board items posted after the snapshot; each forecast
      is scored by the engine's log density against the equal mixture of the two readers, clipped to [-3, 3] nats.
      Writes scores.json and scores.md.
  uv run studies/theory/lib/forecast.py cells <folder> --from <forecast run folders...>
      the theories design the cells that tell them apart. Families: each run's mechanisms, and the newest round's
      theories not refuted. One job per family proposes one new GPU cell per mechanism that it gets right and a named
      other mechanism gets wrong; one job merges cells that are the same run; one fresh job per family (a forecast per
      mechanism) and the two readers forecast every merged cell blind. Ranked in code: pairs of forecasters from
      different families whose intervals do not overlap, per GPU minute; base-only cells by the highest forecast of
      right answers minus the best known base count. Writes cells.json, cell_forecasts.json, cells.md, run.json.

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
import cells as C  # noqa: E402
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
engine.args = engine.args or argparse.Namespace(model_all=None, workers=8)  # round.py sets its own
for stage in ("forecast_targets", "forecast", "forecast_propose", "forecast_score", "cells_propose", "cells_merge", "cells_forecast"):
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


def forecast_errors(fs, tids, need):
    """Messages on a list of forecasts {id, value, low, high, reason}: distinct target ids, at least `need` of them,
    numbers with low <= value <= high."""
    errors = [] if len({f["id"] for f in fs} & set(tids)) == len(fs) >= need else [
        f"needs distinct forecasts of target ids for at least {need} of the {len(tids)} targets; has {len(fs)}"]
    bad = [f.get("id") for f in fs if not all(engine.number(f.get(k)) for k in ("value", "low", "high")) or not f["low"] <= f["value"] <= f["high"]]
    return errors + ([f"value, low, high must be numbers with low <= value <= high on {bad}"] if bad else [])


def check_forecasts(d, ids, theory):
    """A forecaster's file: every target id once; a theory may answer all-null ("theory says nothing")."""
    fs = json.loads((d / "forecasts.json").read_text())["forecasts"]
    if sorted(f["id"] for f in fs) != sorted(ids):
        return f"forecasts.json must hold every target id exactly once: {sorted(ids)}"
    said = [f for f in fs if not (theory and f["value"] is None and f["low"] is None and f["high"] is None)]
    return "; ".join(forecast_errors(said, ids, 0)) or None


def outside(f, readers, tid):
    """The forecast's centre lies outside both readers' intervals for target tid."""
    return all(not r["low"] <= f["value"] <= r["high"] for r in (next(x for x in fs if x["id"] == tid) for fs in readers.values()))


def check_mechanisms(d, n, tids, board_ids):
    ms, errors = json.loads((d / "mechanisms.json").read_text())["mechanisms"], []
    if [m["id"] for m in ms] != [f"f2-m{k:02d}" for k in range(1, n + 1)]:
        errors.append(f"needs exactly {n} mechanisms with ids f2-m01 ... f2-m{n:02d} in order")
    for m in ms:
        fs = m["forecasts"]
        if len(m["statement"].split()) > 80:
            errors.append(f"{m['id']}: statement has {len(m['statement'].split())} words; at most 80")
        if len(set(m["rests_on"]) & board_ids) < 2:
            errors.append(f"{m['id']}: rests_on needs 2 or more item ids of board.jsonl; found {sorted(set(m['rests_on']) & board_ids)}")
        errors += [f"{m['id']}: {e}" for e in forecast_errors(fs, tids, (len(tids) + 1) // 2)]
        if bad := [f.get("id") for f in fs if not str(f.get("vs_readers", "")).lower().startswith(("agree", "disagree"))]:
            errors.append(f"{m['id']}: vs_readers must start with \"agree\" or \"disagree\" on {bad}")
    return "; ".join(errors) or None


def now():
    return engine.time.strftime("%Y-%m-%dT%H:%M:%S", engine.time.gmtime())


def open_targets(folder):
    """Board snapshot (time, every result and knowledge item) and the open work items with their comments (work.md);
    one job turns the open items into targets. Writes folder/targets.json ({utc, work_items, targets}) and
    folder/work.md; returns the board items."""
    utc = now()
    items, _ = board("board", "9999")
    ids = [line.split()[0] for line in sh("uv", "run", "tools/board.py", "ls", "work", "--n", "200").splitlines() if line.startswith("work-")]
    with ThreadPoolExecutor(8) as pool:
        work = dict(zip(ids, pool.map(lambda i: sh("uv", "run", "tools/board.py", "show", i), ids)))
    (folder / "work.md").write_text("".join(f"## {i}\n\n{text}\n" for i, text in work.items()))
    common = {"DIRECTION.md": ROOT / "DIRECTION.md", "board.jsonl": "".join(json.dumps(i) + "\n" for i in items), "work.md": folder / "work.md"}
    out = engine.tmp() / "targets.json"
    engine.run([engine.job("forecast_targets", "targets", common, {"targets.json": out}, lambda d: check_targets(d, work))], folder)
    targets = json.loads(out.read_text())["targets"]
    (folder / "targets.json").write_text(json.dumps({"utc": utc, "work_items": ids, "targets": targets}, indent=1))
    print(f"  targets.json: {len(targets)} targets from {len(ids)} open work items, board snapshot {utc} UTC")
    return items


def run_forecasters(folder, common, theory_files):
    """reader-1, reader-2 and one job per theory ({name: theory file}) forecast every target of folder/targets.json,
    blind; returns {forecaster: forecasts}."""
    tids = [t["id"] for t in json.loads((folder / "targets.json").read_text())["targets"]]
    out, common = engine.tmp() / "forecasts", {**common, "targets.json": folder / "targets.json"}
    jobs = [engine.job("forecast", r, common, {"forecasts.json": out / f"{r}.json"}, lambda d: check_forecasts(d, tids, False),
                       theory="", nothing="") for r in READERS]
    jobs += [engine.job("forecast", n, {**common, "theory.json": p}, {"forecasts.json": out / f"{n}.json"},
                        lambda d: check_forecasts(d, tids, True), theory=THEORY, nothing=NOTHING) for n, p in theory_files.items()]
    engine.run(jobs, folder)
    return {n: json.loads((out / f"{n}.json").read_text())["forecasts"] for n in READERS + list(theory_files)}


def write_md(folder, utc, forecasts, head=()):
    """forecasts.md: the head lines, then one table per target (forecaster, value, interval, reason)."""
    targets = json.loads((folder / "targets.json").read_text())["targets"]
    md = [f"# Forecasts, {folder.name}\n\nBoard snapshot {utc} UTC, written {now()} UTC. {len(targets)} targets; "
          f"forecasters {', '.join(forecasts)}.\n", *head]
    for t in targets:
        md.append(f"\n## {t['id']} ({t['item']}): {t['what']}\n\nUnit: {t['unit']}. Cell: {json.dumps(t['cell'])}\n\n> {t['quote']}\n\n"
                  "| forecaster | value | 90 % interval | reason |\n|---|---|---|---|")
        for n, fs in forecasts.items():
            f = next((f for f in fs if f["id"] == t["id"]), {"value": None, "reason": "no forecast"})
            value, span = ("-", "") if f["value"] is None else (f"{f['value']:g}", f"[{f['low']:g}, {f['high']:g}]")
            md.append(f"| {n} | {value} | {span} | {f['reason']} |")
    (folder / "forecasts.md").write_text("\n".join(md) + "\n")


ANY_LENS = "Any family of causes."


def make(folder, propose, lens):
    folder.mkdir(parents=True)  # fails if the folder exists
    items = open_targets(folder)
    tdata = json.loads((folder / "targets.json").read_text())
    utc, tids = tdata["utc"], [t["id"] for t in tdata["targets"]]
    common = {"DIRECTION.md": ROOT / "DIRECTION.md", "board.jsonl": "".join(json.dumps(i) + "\n" for i in items), "work.md": folder / "work.md"}
    forecasts = run_forecasters(folder, common, {n: ROUND / "theories" / f"{n}.json" for n in theories()})
    readers, head = {r: forecasts[r] for r in READERS}, []
    if propose:
        engine.run([engine.job("forecast_propose", "propose", {**common, "targets.json": folder / "targets.json",
                                                               "readers.json": json.dumps(readers, indent=1),
                                                               "facts.json": ROUND / "facts.json", "graveyard.json": ROUND / "graveyard.json"},
                               {"mechanisms.json": folder / "mechanisms.json"},
                               lambda d: check_mechanisms(d, propose, tids, {i["id"] for i in items}), n=propose, lens=lens or ANY_LENS)], folder)
        head.append(f"\nLens of the mechanisms: {lens or ANY_LENS}\n")
    for m in json.loads((folder / "mechanisms.json").read_text())["mechanisms"] if propose else []:
        forecasts[m["id"]] = m["forecasts"]
        head.append(f"\n## {m['id']}\n\n{m['statement']}\n\nRests on: {', '.join(m['rests_on'])}. Forecasts {len(m['forecasts'])} of "
                    f"{len(tids)} targets:\n\n| target | value | 90 % interval | reader-1 | reader-2 | outside both readers | against the readers |\n|---|---|---|---|---|---|---|")
        for f in m["forecasts"]:
            r1, r2 = (next(x for x in readers[r] if x["id"] == f["id"]) for r in READERS)
            head.append(f"| {f['id']} | {f['value']:g} | [{f['low']:g}, {f['high']:g}] | {r1['value']:g} [{r1['low']:g}, {r1['high']:g}] | "
                        f"{r2['value']:g} [{r2['low']:g}, {r2['high']:g}] | {'yes' if outside(f, readers, f['id']) else ''} | {f['vs_readers']} |")
    (folder / "forecasts.json").write_text(json.dumps(forecasts, indent=1))
    write_md(folder, utc, forecasts, head)
    (folder / "run.json").write_text(json.dumps({"commit": sh("git", "rev-parse", "--short", "HEAD").strip(), "command": " ".join(sys.argv),
                                                 "utc": utc, "round": str(ROUND.relative_to(ROOT)), "targets": len(tids), "propose": propose, "lens": lens,
                                                 "forecasters": list(forecasts), "job_dirs": str(engine.tmp())}, indent=1))
    print(f"{len(tids)} targets, {len(forecasts)} forecasters: {folder / 'forecasts.md'}")


def check_measured(d, tids, posted):
    ms = json.loads((d / "measured.json").read_text())["measured"]
    if sorted(m["id"] for m in ms) != sorted(tids):
        return f"measured.json must hold every target id exactly once: {sorted(tids)}"
    bad = [m["id"] for m in ms if m["value"] is not None and not (engine.number(m["value"]) and m["item"] in posted
                                                                  and flat(m["quote"]) in flat(posted[m["item"]]))]
    return f"{bad}: a measured value needs an item of posted.jsonl and a quote found in its text" if bad else None


def score_forecasts(folder, forecasts, utc):
    """One job finds each target of folder/targets.json in the items posted at or after utc; each forecast is scored
    by round.py's gain_rows (log density against the equal mixture of the two readers, clipped to [-3, 3] nats).
    Returns {scored_utc, measured, forecasters: {name: scored, inside, total_gain, mean_gain, disagree,
    disagree_inside, rows}, outside_every_interval}."""
    tids = [t["id"] for t in json.loads((folder / "targets.json").read_text())["targets"]]
    _, after = board(f"posted-{folder.name}", utc)
    posted = {i["id"]: i["text"] for i in after}
    d = engine.tmp() / f"measured-{folder.name}.json"
    engine.run([engine.job("forecast_score", f"measured-{folder.name}", {"targets.json": folder / "targets.json",
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
            r["disagrees"] = all(not p["low"] <= r["value"] <= p["high"] for p in r["nulls"])  # centre outside both readers' intervals
        total, apart = sum(r["gain"] for r in rows), [r for r in rows if r["disagrees"]]
        per[n] = {"scored": len(rows), "inside": sum(r["inside"] for r in rows), "total_gain": round(total, 3),
                  "mean_gain": round(total / len(rows), 3) if rows else None, "disagree": len(apart),
                  "disagree_inside": sum(r["inside"] for r in apart), "rows": rows}
    surprise = [t for t in measured if not any(r["inside"] for p in per.values() for r in p["rows"] if r["id"] == t)]
    return {"scored_utc": now(), "measured": ms, "forecasters": per, "outside_every_interval": surprise}


def scores_md(s, title):
    ms = s["measured"]
    md = [f"# {title}\n\nScored {s['scored_utc']} UTC. {sum(m['value'] is not None for m in ms)} of {len(ms)} targets measured. Gain: log "
          "density of the forecast minus log density of the equal mixture of reader-1 and reader-2 at the measured value, clipped to [-3, 3] nats.\n",
          "| forecaster | scored | inside interval | total gain | mean gain | outside both readers | of those inside |\n|---|---|---|---|---|---|---|"]
    md += [f"| {n} | {p['scored']} | {p['inside']} | {p['total_gain']} | {p['mean_gain']} | {p['disagree']} | {p['disagree_inside']} |"
           for n, p in s["forecasters"].items()]
    md.append("\n| target | measured | item | outside every interval |\n|---|---|---|---|")
    md += [f"| {m['id']} | {m['value'] if m['value'] is not None else 'not posted yet'} | {m['item'] or ''} | "
           f"{'yes' if m['id'] in s['outside_every_interval'] else ''} |" for m in ms]
    return "\n".join(md) + "\n"


def score(folder):
    """scores.json and scores.md; when they exist, scores-<UTC time>.json and .md beside them."""
    s = score_forecasts(folder, json.loads((folder / "forecasts.json").read_text()), json.loads((folder / "run.json").read_text())["utc"])
    name = "scores" if not (folder / "scores.json").exists() else f"scores-{s['scored_utc'].replace(':', '')}"
    (folder / f"{name}.json").write_text(json.dumps(s, indent=1))
    (folder / f"{name}.md").write_text(scores_md(s, f"Scores, {folder.name}"))
    print(scores_md(s, f"{folder / name}.md"))


def cells(folder, runs):
    """Families propose cells, one job merges them, families and readers forecast them blind; ranked by lib/cells.py.
    Job outputs are kept in folder/jobs/, so the same command resumes a stopped run."""
    folder.mkdir(parents=True, exist_ok=True)
    out, utc, fams = folder / "jobs", now(), C.families(runs, ROUND)
    items, _ = board("board", "9999")
    known = {"targets": [{"run": r.name, **t} for r in runs for t in json.loads((r / "targets.json").read_text())["targets"]],
             "facts": json.loads((ROUND / "facts.json").read_text())}
    common = {"DIRECTION.md": ROOT / "DIRECTION.md", "board.jsonl": "".join(json.dumps(i) + "\n" for i in items), "known.json": json.dumps(known, indent=1)}
    every = [{"id": m["id"], "family": n, "statement": m["statement"]} for n, f in fams.items() for m in f["mechanisms"]]
    all_ids, board_ids = {m["id"] for m in every}, {i["id"] for i in items}
    engine.run([engine.job("cells_propose", n, {**common, **C.family_inputs(n, f, ROUND), "all_mechanisms.json": json.dumps(every, indent=1),
                                                "jobs.md": C.jobs_md()}, {"cells.json": out / f"propose-{n}.json"},
                           lambda d, f=f: C.check_proposals(d, [m["id"] for m in f["mechanisms"]], all_ids, board_ids),
                           theories=C.THEORY_FILES if n == ROUND.name else "") for n, f in fams.items()], folder, len(fams))
    props = [{"family": n, **p} for n in fams for p in json.loads((out / f"propose-{n}.json").read_text())["cells"]]
    props = [{"id": f"c{k:02d}", **p} for k, p in enumerate(props, 1)]
    by_id = {p["id"]: p for p in props}
    shown = [{k: p[k] for k in ("id", "cell", "job", "command", "readout", "unit")} for p in props]  # no numbers
    engine.run([engine.job("cells_merge", "merge", {"proposals.json": json.dumps(shown, indent=1)}, {"merged.json": out / "merged.json"},
                           lambda d: C.check_merged(d, list(by_id)))], folder)
    merged = json.loads((out / "merged.json").read_text())["cells"]
    C.attach(merged, by_id)
    rids, fc = [r["id"] for c in merged for r in c["readouts"]], {**common, "cells.json": json.dumps(C.blind(merged), indent=1)}
    jobs = [engine.job("cells_forecast", r, fc, {"forecasts.json": out / f"forecast-{r}.json"}, lambda d: C.check_forecasts(d, rids, [None]),
                       theory="", key="", every="every readout id of cells.json exactly once", nothing="") for r in READERS]
    jobs += [engine.job("cells_forecast", n, {**fc, **C.family_inputs(n, f, ROUND)}, {"forecasts.json": out / f"forecast-{n}.json"},
                        lambda d, f=f: C.check_forecasts(d, rids, [m["id"] for m in f["mechanisms"]]),
                        theory=C.FAMILY.format(files=C.THEORY_FILES if n == ROUND.name else ""), key='"mechanism": "<id>", ',
                        every="one forecast per mechanism of mechanisms.json and readout id of cells.json, each pair exactly once",
                        nothing=C.NOTHING) for n, f in fams.items()]
    engine.run(jobs, folder, len(jobs))
    F, fam_of = {}, {}  # forecaster (a mechanism or a reader) -> {readout id: forecast}; each reader is its own family
    for n in READERS + list(fams):
        for f in json.loads((out / f"forecast-{n}.json").read_text())["forecasts"]:
            F.setdefault(f.get("mechanism", n), {})[f["readout"]] = f
            fam_of[f.get("mechanism", n)] = n
    C.rank(merged, F, fam_of)
    (folder / "cells.json").write_text(json.dumps({"utc": utc, "proposals": props, "cells": merged}, indent=1))
    (folder / "cell_forecasts.json").write_text(json.dumps({n: {"family": fam_of[n], "forecasts": list(F[n].values())} for n in F}, indent=1))
    head = (f"Written {now()} UTC (board read {utc} UTC). Plan `specs/SPEC_cells01.md`. Families: "
            f"{', '.join(n + ' (' + str(len(f['mechanisms'])) + ')' for n, f in fams.items())}; {len(F)} forecasters (each reader is its own "
            "family). Separation = pairs of forecasters from different families whose 90 % intervals do not overlap, summed over the cell's readouts.")
    (folder / "cells.md").write_text(md := C.cells_md(f"Cells designed by the theories, {folder.name}", head, props, merged, F, fam_of))
    (folder / "run.json").write_text(json.dumps({"commit": sh("git", "rev-parse", "--short", "HEAD").strip(), "command": " ".join(sys.argv), "utc": utc,
                                                 "from": [str(r) for r in runs], "round": str(ROUND.relative_to(ROOT)), "proposed": len(props),
                                                 "merged": len(merged), "forecasters": len(F), "job_dirs": str(engine.tmp())}, indent=1))
    print("\n".join(md.splitlines()[4:7]) + f"\n{folder / 'cells.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["make", "score", "cells"])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--propose", type=int, default=0, help="make: also write this many mechanisms about the targets "
                        "(forecasters f2-m01 ...)")
    parser.add_argument("--lens", help="make: the family of causes the --propose mechanisms must come from")
    parser.add_argument("--from", dest="runs", type=Path, nargs="+", help="cells: the forecast run folders whose mechanisms design cells")
    a = parser.parse_args()
    {"make": lambda: make(a.folder, a.propose, a.lens), "score": lambda: score(a.folder), "cells": lambda: cells(a.folder, a.runs)}[a.command]()
