# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Forecasts of the team's open GPU work (studies/theory/README.md, "Forecast runs"), and the default theory round.

  uv run studies/theory/lib/forecast.py round <folder> --from <previous round, forecast run and cells folders...>
      version 11, score first (.claude/skills/theory/SKILL.md). Stages, each skipped when its output exists: standing
      (each --from folder's forecasts scored against the items posted after its snapshot, one job each, and its cells
      and routes against its measured.json; carried: total gain above 0 on numbers from 3 or more board items;
      graveyard: -2 nats or less on 2 or more), surprises (scored numbers outside both readers' intervals:
      surprises.md), targets_open, forecast (two readers and the carried mechanisms), propose (only with surprises: two
      rival mechanisms per surprise, the --surprises most surprising, at once; the duplicate judge reports only), cells (the pairs'
      cells and one no-reward route per pair; one job checks them against open and posted work: an open item's
      answer becomes a target on it; everyone forecasts the rest; ranked), experiments. Writes standing.*,
      graveyard.json, surprises.*, targets.json, work.md, pairs.json, duplicates.json, mechanisms.json, forecasts.*,
      cells.json, cell_forecasts.json, cells.md, experiments.md, run.json, and job outputs under jobs/.
      --propose-wide: the version-10 round (six lens jobs of --propose N mechanisms, every family designs cells).
  uv run studies/theory/lib/forecast.py make <folder>
      reads the open work items with their comments and every result and knowledge item (the board snapshot); one
      headless job turns the open items into targets (numbers they will report); two readers with no theory and one
      job per theory not refuted in the newest round (at most 6, survivors first, then by total gain) forecast every
      target (value, 90 % interval, reason). Writes targets.json, forecasts.json, forecasts.md, run.json. Fails if the
      folder exists.
      --propose N: then one job, given the readers' forecasts and the round's facts.json and graveyard.json, writes N
      mechanisms about the targets (mechanisms.json); each names in holds_against the two known numbers nearest to
      contradicting it, and each forecast says whether it agrees with the readers and why (vs_readers). They forecast
      as f2-m01 ... and are scored like the rest.
      --lens TEXT: the family of causes the N mechanisms must come from (run-03 to run-08 ran one lens each).
  uv run studies/theory/lib/forecast.py score <folder>
      one headless job finds each target's measured value in the board items posted after the snapshot; each forecast
      is scored by the engine's log density against the equal mixture of the two readers, clipped to [-3, 3] nats;
      a forecast whose measured value is outside its own interval gains at most 0 (version 9). Writes scores.json and
      scores.md, or scores-<UTC time>.json and .md when they exist.
      --rescore: no job; the measured values of the newest scores file, scored again by the current rule.
  uv run studies/theory/lib/forecast.py cells <folder> --from <forecast run folders...>
      the theories design the cells that tell them apart. Families: each run's mechanisms, and the newest round's
      theories not refuted. One job per family proposes one new GPU cell per mechanism that it gets right and a named
      other mechanism gets wrong; one job merges cells that are the same run; one fresh job per family (a forecast per
      mechanism) and the two readers forecast every merged cell blind. Ranked in code: pairs of forecasters from
      different families whose intervals do not overlap, per GPU minute; base-only cells by the highest forecast of
      right answers minus the best known base count. A cell whose command names a job file, flag or flag value that
      does not exist is sent back once, then dropped (cells.json "dropped"). Writes cells.json, cell_forecasts.json,
      cells.md, run.json.

Every job is round.py's blind job: claude -p in an empty directory with Read and Write only, the model round.py gives
cross_predict (--model-all <model> overrides it, for smoke tests).
"""
import argparse
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells as C  # noqa: E402
import round as engine  # noqa: E402

ROOT = engine.ROOT
ROUND = ROOT / "studies/theory/results/engine/round-07"  # the newest round: its unrefuted theories forecast
ENGINE = ROOT / "studies/theory/results/engine"
READERS = ["reader-1", "reader-2"]
LENSES = {  # the six families of causes of specs/SPEC_forecast03.md (forecast runs 03-08)
    "stopping": "when and how the model stops: token cap, loops, end-of-text, answer markers",
    "sampling": "sampling: temperature, top-p, entropy of the next-token distribution, what a vote over samples adds",
    "weights": "weight space: the RL weight change, its top directions, scaling and transplanting it",
    "training": "training data and objective: what Think-SFT imitation, RL reward and pretraining each put into the model, exposure of problems",
    "problems": "problem structure: difficulty, domain, answer type, length of the needed derivation",
    "grader": "the grader and the measurement itself: extraction, equivalence, seeds, set composition, what a count hides"}
MECHANISM_KEYS = ("id", "family", "lens", "statement", "rests_on", "holds_against")
MAX_THEORIES = 6
THEORY = ("- theory.json: a theory of the team's results. Derive each forecast from the theory as written: say in the\n"
          "  reason which part of the theory gives the number. Where the theory implies nothing about a target, do not\n"
          "  guess: answer \"theory says nothing\" for it.\n")
NOTHING = (' For a target the theory says nothing about, write {"id": "t02", "value": null, "low": null, "high": null, '
           '"reason": "theory says nothing"}.')
engine.args = engine.args or argparse.Namespace(model_all=None, workers=8)  # round.py sets its own
for stage in ("forecast_targets", "forecast", "forecast_propose", "forecast_score", "cells_propose", "cells_merge", "cells_forecast", "routes_propose", "duplicates", "surprise_propose", "cells_check"):
    engine.MODELS[stage] = engine.MODELS["cross_predict"]


def board(name, cutoff):
    """check.dump's snapshot (the result and knowledge items round.py's split reads): (before, after) the cutoff."""
    d = Path(engine.tempfile.mkdtemp(dir=engine.tmp(), prefix=f"{name}-")) / "dump"  # a new folder per call
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


def check_mechanisms(d, n, tids, board_ids, n_facts):
    ms, errors = json.loads((d / "mechanisms.json").read_text())["mechanisms"], []
    if [m["id"] for m in ms] != [f"f2-m{k:02d}" for k in range(1, n + 1)]:
        errors.append(f"needs exactly {n} mechanisms with ids f2-m01 ... f2-m{n:02d} in order")
    for m in ms:
        fs = m["forecasts"]
        if len(m["statement"].split()) > 80:
            errors.append(f"{m['id']}: statement has {len(m['statement'].split())} words; at most 80")
        if len(set(m["rests_on"]) & board_ids) < 2:
            errors.append(f"{m['id']}: rests_on needs 2 or more item ids of board.jsonl; found {sorted(set(m['rests_on']) & board_ids)}")
        h = m.get("holds_against")
        if not (isinstance(h, list) and len(h) == 2 and all(isinstance(x, dict) and engine.number(x.get("value")) and str(x.get("why", "")).strip()
                                                            and (x.get("item") in board_ids or x.get("fact") in range(n_facts)) for x in h)):
            errors.append(f'{m["id"]}: holds_against needs 2 entries {{"item": <id of board.jsonl> or "fact": <index in facts.json, '
                          f'0 to {n_facts - 1}>, "value": <the number>, "why": <why the mechanism holds>}}')
        errors += [f"{m['id']}: {e}" for e in forecast_errors(fs, tids, (len(tids) + 1) // 2)]
        if bad := [f.get("id") for f in fs if not str(f.get("vs_readers", "")).lower().startswith(("agree", "disagree"))]:
            errors.append(f"{m['id']}: vs_readers must start with \"agree\" or \"disagree\" on {bad}")
    return "; ".join(errors) or None


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())


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


def run_forecasters(folder, common, theory_files, out=None, workers=None):
    """reader-1, reader-2 and one job per theory ({name: theory file or text}) forecast every target of
    folder/targets.json, blind; outputs under out (default: the temp folder); returns {forecaster: forecasts}."""
    tids = [t["id"] for t in json.loads((folder / "targets.json").read_text())["targets"]]
    out, common = out or engine.tmp() / "forecasts", {**common, "targets.json": folder / "targets.json"}
    jobs = [engine.job("forecast", r, common, {"forecasts.json": out / f"{r}.json"}, lambda d: check_forecasts(d, tids, False),
                       theory="", nothing="") for r in READERS]
    jobs += [engine.job("forecast", n, {**common, "theory.json": p}, {"forecasts.json": out / f"{n}.json"},
                        lambda d: check_forecasts(d, tids, True), theory=THEORY, nothing=NOTHING) for n, p in theory_files.items()]
    engine.run(jobs, folder, workers)
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
                               lambda d: check_mechanisms(d, propose, tids, {i["id"] for i in items}, len(json.loads((ROUND / "facts.json").read_text()))),
                               n=propose, lens=lens or ANY_LENS)], folder)
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


def find_measured(folder, utc):
    """One job finds each target of folder/targets.json in the board items posted at or after utc; returns its
    measured list [{id, value (null when not posted), item, quote, note}]."""
    tids = [t["id"] for t in json.loads((folder / "targets.json").read_text())["targets"]]
    _, after = board(f"posted-{folder.name}", utc)
    posted = {i["id"]: i["text"] for i in after}
    d = engine.tmp() / f"measured-{folder.name}.json"
    engine.run([engine.job("forecast_score", f"measured-{folder.name}", {"targets.json": folder / "targets.json",
                                                                         "posted.jsonl": "".join(json.dumps(i) + "\n" for i in after)},
                           {"measured.json": d}, lambda j: check_measured(j, tids, posted))], folder)
    return json.loads(d.read_text())["measured"]


def scored(forecasts, ms):
    """Each forecast ({forecaster: [{id, value, low, high}]}) against the measured list ms, by round.py's gain_rows (log
    density against the equal mixture of the two readers, clipped to [-3, 3] nats, at most 0 outside its own
    interval). Returns {scored_utc, measured, forecasters: {name: scored, inside, total_gain, mean_gain, disagree,
    disagree_inside, rows}, outside_every_interval}."""
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


def snapshot(folder):
    """The board snapshot time of a forecast run or round folder."""
    return json.loads((folder / "targets.json").read_text()).get("utc") or json.loads((folder / "run.json").read_text())["utc"]


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


def score(folder, rescore):
    """scores.json and scores.md; when they exist, scores-<UTC time>.json and .md beside them. rescore: the measured
    values of the newest scores file, no job."""
    newest = max(folder.glob("scores*.json"), key=lambda p: json.loads(p.read_text())["scored_utc"]) if rescore else None
    ms = json.loads(newest.read_text())["measured"] if rescore else find_measured(folder, snapshot(folder))
    s = scored(json.loads((folder / "forecasts.json").read_text()), ms) | ({"rescored_from": newest.name} if rescore else {})
    name = "scores" if not (folder / "scores.json").exists() else f"scores-{s['scored_utc'].replace(':', '')}"
    (folder / f"{name}.json").write_text(json.dumps(s, indent=1))
    (folder / f"{name}.md").write_text(scores_md(s, f"Scores, {folder.name}"))
    print(scores_md(s, f"{folder / name}.md"))


def prefix(folder):
    """The id prefix of a folder's cells: r10 for round-10, else the folder name."""
    m = re.search(r"round-(\d+)", folder.name)
    return f"r{int(m.group(1)):02d}" if m else folder.name


def gap_md(items):
    """gap.md for the route jobs: result-f39ba8 (the gap budget) and the "Gap anatomy" section of the rlneurons README."""
    readme = (ROOT / "studies/rlneurons/README.md").read_text()
    anatomy = "## Gap anatomy" + readme.split("\n## Gap anatomy")[1].split("\n## Answer-statement repair")[0]
    return f"# The gap between the cued base and RL-Zero-Math\n\n## result-f39ba8\n\n{next(i['text'] for i in items if i['id'] == 'result-f39ba8')}\n\n{anatomy}\n"


def common_inputs(items, known):
    return {"DIRECTION.md": ROOT / "DIRECTION.md", "board.jsonl": "".join(json.dumps(i) + "\n" for i in items), "known.json": json.dumps(known, indent=1)}


def route_jobs(folder, fams, items, known):
    """One no-reward route job per family; returns the routes ({family, ...}) whose commands pass the flag check, and
    the dropped ones."""
    out, flags, rows = folder / "jobs", C.job_flags(), C.table_rows()
    shown = [{k: r[k] for k in ("key", "name", "samples", "tokens", "right", "math500", "source")} for r in rows]
    engine.run([engine.job("routes_propose", n.replace("/", "-"), {**common_inputs(items, known), **C.family_inputs(n, f, ROUND), "jobs.md": C.jobs_md(),
                                                                   "gap.md": gap_md(items), "best_known.json": json.dumps(shown, indent=1)},
                           {"route.json": out / f"route-{n}.json"},
                           C.flags_once(lambda d, fl, f=f: C.check_routes(d, [m["id"] for m in f["mechanisms"]], rows, fl))) for n, f in fams.items()],
               folder, len(fams))
    routes = [{"family": n, **json.loads((out / f"route-{n}.json").read_text())["route"]} for n in fams]
    dropped = [{"id": f"route of {r['family']}", "command": r["command"], "reason": "; ".join(e)}
               for r in routes if (e := C.command_errors(r["command"], flags) + C.command_errors(r["rl_command"], flags))]
    return [r for r in routes if f"route of {r['family']}" not in {x["id"] for x in dropped}], dropped


def cells(folder, fams, known, plan, left_out=()):
    """Version 10 (--propose-wide): families ({family: {lens, mechanisms}}) propose cells and one no-reward route each;
    one job merges the cells; then forecast_rank. A cell or route whose command fails the flag check after one send-back
    is dropped. Job outputs are kept in folder/jobs/, so the same command resumes a stopped run."""
    folder.mkdir(parents=True, exist_ok=True)
    out, flags, pre = folder / "jobs", C.job_flags(), prefix(folder)
    items, _ = board("board", "9999")
    common = common_inputs(items, known)
    every = [{"id": m["id"], "family": n, "statement": m["statement"]} for n, f in fams.items() for m in f["mechanisms"]]
    all_ids, board_ids = {m["id"] for m in every}, {i["id"] for i in items}
    engine.run([engine.job("cells_propose", n.replace("/", "-"), {**common, **C.family_inputs(n, f, ROUND), "all_mechanisms.json": json.dumps(every, indent=1),
                                                                  "jobs.md": C.jobs_md()}, {"cells.json": out / f"propose-{n}.json"},
                           C.flags_once(lambda d, fl, f=f: C.check_proposals(d, [m["id"] for m in f["mechanisms"]], all_ids, board_ids, fl)),
                           theories=C.THEORY_FILES if n == ROUND.name else "") for n, f in fams.items()], folder, len(fams))
    routes, dropped = route_jobs(folder, fams, items, known)
    props = [{"family": n, **p} for n in fams for p in json.loads((out / f"propose-{n}.json").read_text())["cells"]]
    props = [{"id": f"c{k:02d}", **p} for k, p in enumerate(props, 1)]
    dropped += [{"id": p["id"], "mechanism": p["mechanism"], "command": p["command"], "reason": "; ".join(e)}
                for p in props if (e := C.command_errors(p["command"], flags))]
    by_id = {p["id"]: p for p in props if p["id"] not in {x["id"] for x in dropped}}
    shown = [{k: p[k] for k in ("id", "cell", "job", "command", "readout", "unit")} for p in by_id.values()]  # no numbers
    engine.run([engine.job("cells_merge", "merge", {"proposals.json": json.dumps(shown, indent=1)}, {"merged.json": out / "merged.json"},
                           C.flags_once(lambda d, fl: C.check_merged(d, list(by_id), fl)))], folder)
    merged = json.loads((out / "merged.json").read_text())["cells"]
    for c in merged:  # ids carry the round: m05 -> r10-m05, m05-r1 -> r10-m05-r1
        c["id"] = f"{pre}-{c['id']}"
        for r in c["readouts"]:
            r["id"] = f"{pre}-{r['id']}"
    dropped += [{"id": c["id"], "from": [i for r in c["readouts"] for i in r["from"]], "command": c["command"], "reason": "; ".join(e)}
                for c in merged if (e := C.command_errors(c["command"], flags))]
    merged = [c for c in merged if c["id"] not in {x["id"] for x in dropped}]
    return forecast_rank(folder, fams, props, by_id, merged, C.route_cells(routes, C.table_rows(), pre), dropped, common, plan, left_out)


def forecast_rank(folder, fams, props, by_id, merged, routes, dropped, common, plan, left_out=(), answered=None, pair_of=None):
    """Families and readers forecast every cell and route blind; cells and routes an open work item answers (answered:
    {id: {item, quote}}) become targets on that item (their readouts appended to targets.json, their forecasts to
    forecasts.json) and leave the ranking; the rest are ranked by lib/cells.py (forecasters in left_out left out).
    Writes cells.json, cell_forecasts.json, cells.md; returns their counts."""
    out, utc, answered = folder / "jobs", now(), answered or {}
    for x in dropped:
        print(f"  dropped {x['id']}: {x['reason']}")
    C.attach(merged, by_id)
    rids = [r["id"] for c in merged + routes for r in c["readouts"]]
    fc = {**common, "cells.json": json.dumps(C.blind(merged), indent=1), "routes.json": json.dumps(C.blind_routes(routes), indent=1)}
    every_id = "every readout id of cells.json and routes.json"
    jobs = [engine.job("cells_forecast", r, fc, {"forecasts.json": out / f"forecast-{r}.json"}, lambda d: C.check_forecasts(d, rids, [None]),
                       theory="", key="", every=f"{every_id} exactly once", nothing="") for r in READERS]
    jobs += [engine.job("cells_forecast", n.replace("/", "-"), {**fc, **C.family_inputs(n, f, ROUND)}, {"forecasts.json": out / f"forecast-{n}.json"},
                        lambda d, f=f: C.check_forecasts(d, rids, [m["id"] for m in f["mechanisms"]]),
                        theory=C.FAMILY.format(files=C.THEORY_FILES if n == ROUND.name else ""), key='"mechanism": "<id>", ',
                        every=f"one forecast per mechanism of mechanisms.json and {every_id}, each pair exactly once",
                        nothing=C.NOTHING) for n, f in fams.items()]
    engine.run(jobs, folder, len(jobs))
    F, fam_of = {}, {}  # forecaster (a mechanism or a reader) -> {readout id: forecast}; each reader is its own family
    for n in READERS + list(fams):
        for f in json.loads((out / f"forecast-{n}.json").read_text())["forecasts"]:
            F.setdefault(f.get("mechanism", n), {})[f["readout"]] = f
            fam_of[f.get("mechanism", n)] = n
    converted = [c for c in merged + routes if c["id"] in answered]
    if converted:  # free targets: scored next round from the open item's own report
        tdata, fdata = json.loads((folder / "targets.json").read_text()), json.loads((folder / "forecasts.json").read_text())
        for c in converted:
            for r in c["readouts"]:
                tdata["targets"].append({"id": r["id"], "item": answered[c["id"]]["item"], "cell": c.get("cell") or {"route": c["change"], "set": r["set"], "n": r["n"]},
                                         "unit": r["unit"], "what": r["readout"], "quote": answered[c["id"]]["quote"], "from_cell": c["id"]})
                for n in F:
                    fdata.setdefault(n, []).append({"id": r["id"], **{k: F[n][r["id"]][k] for k in ("value", "low", "high", "reason")}})
        (folder / "targets.json").write_text(json.dumps(tdata, indent=1))
        (folder / "forecasts.json").write_text(json.dumps(fdata, indent=1))
    merged, routes = [c for c in merged if c["id"] not in answered], [c for c in routes if c["id"] not in answered]
    blind_pair = {}  # a rival pair's cell is ranked only when the two rivals' own blind intervals do not overlap
    for c in merged:
        if c["id"] in (pair_of or {}):
            fa, fb = (F[x][c["readouts"][0]["id"]] for x in pair_of[c["id"]])
            blind_pair[c["id"]] = {"a": pair_of[c["id"]][0], "b": pair_of[c["id"]][1], "a_blind": {k: fa[k] for k in ("value", "low", "high")},
                                   "b_blind": {k: fb[k] for k in ("value", "low", "high")}, "differs": C.apart(fa, fb)}
    not_blind = [c for c in merged if c["id"] in blind_pair and not blind_pair[c["id"]]["differs"]]
    merged = [c for c in merged if c not in not_blind]
    left_out = sorted(set(left_out) & set(F))
    C.rank(merged, F, fam_of, left_out)
    C.rank_routes(routes, F, left_out)
    (folder / "cells.json").write_text(json.dumps({"utc": utc, "proposals": props, "dropped": dropped, "left_out": left_out, "cells": merged, "routes": routes,
                                                   "converted": [{"id": c["id"], **answered[c["id"]]} for c in converted], "pair_blind": blind_pair,
                                                   "pair_does_not_differ_blind": not_blind}, indent=1))
    (folder / "cell_forecasts.json").write_text(json.dumps({n: {"family": fam_of[n], "forecasts": list(F[n].values())} for n in F}, indent=1))
    head = (f"Written {now()} UTC. {plan}Families: {', '.join(n + ' (' + str(len(f['mechanisms'])) + ')' for n, f in fams.items())}; {len(F)} forecasters "
            f"(each reader is its own family). {len(dropped)} cells or routes dropped (cells.json \"dropped\"); {len(converted)} turned into targets on the "
            "open work item that answers them (cells.json \"converted\"). Separation = readouts whose forecasters split into a low and a high side "
            "(every low interval below every high interval) with 2 or more families on each side.")
    (folder / "cells.md").write_text(md := C.cells_md(f"Cells and routes, {folder.name}", head, list(by_id.values()), merged, F, fam_of, routes, left_out))
    with open(folder / "cells.md", "a") as f:
        f.write("\n## Rival pairs' cells forecast blind by the two rivals\n\n" + "".join(
            f"- {i}: {b['a']} {b['a_blind']['value']:g} [{b['a_blind']['low']:g}, {b['a_blind']['high']:g}] against {b['b']} {b['b_blind']['value']:g} "
            f"[{b['b_blind']['low']:g}, {b['b_blind']['high']:g}]: {'differs, ranked' if b['differs'] else 'pair does not differ blind, not ranked'}\n"
            for i, b in blind_pair.items()) if blind_pair else "\n## Rival pairs' cells forecast blind by the two rivals\n\nnone\n")
    print("\n".join(md.splitlines()[4:8]) + f"\n{folder / 'cells.md'}")
    return {"pairs_differ_blind": sum(b["differs"] for b in blind_pair.values()), "proposed": len(props), "dropped": len(dropped), "converted": len(converted), "merged": len(merged), "routes": len(routes), "forecasters": len(F),
            "routes_above_baseline": sum((c["score"] or 0) > 0 for c in routes), "cells_split": sum(bool(c["separation"]) for c in merged)}


def cells_run(folder, runs):
    """forecast.py cells: the families of the forecast runs and of ROUND's unrefuted theories."""
    known = {"targets": [{"run": r.name, **t} for r in runs for t in json.loads((r / "targets.json").read_text())["targets"]],
             "facts": json.loads((ROUND / "facts.json").read_text())}
    counts = cells(folder, C.families(runs, ROUND), known, "Plan `specs/SPEC_cells01.md`. ")
    (folder / "run.json").write_text(json.dumps({"commit": sh("git", "rev-parse", "--short", "HEAD").strip(), "command": " ".join(sys.argv), "utc": now(),
                                                 "from": [str(r) for r in runs], "round": str(ROUND.relative_to(ROOT)), **counts,
                                                 "job_dirs": str(engine.tmp())}, indent=1))


# ---- version 9: the wide round ----

def newest(name):
    """The newest engine round's file `name` (facts.json, graveyard.json)."""
    return max(ENGINE.glob(f"round-*/{name}"))


def full(src, name):
    """A forecaster's id across folders: a forecast run's f2-m01 is <run>/f2-m01; ids with a / are kept."""
    return name if "/" in name else f"{src.name}/{name}"


def mechanisms_of(src):
    """{id: mechanism (MECHANISM_KEYS)} of a round folder (ids and families already full) or a forecast run (family:
    the LENSES key of its lens, else the folder name)."""
    if not (src / "mechanisms.json").exists():
        return {}
    ms = json.loads((src / "mechanisms.json").read_text())["mechanisms"]
    if (src / "standing.json").exists():
        return {m["id"]: m for m in ms}
    lens = json.loads((src / "run.json").read_text()).get("lens") or ANY_LENS
    fam = next((k for k, v in LENSES.items() if v == lens), src.name)
    return {full(src, m["id"]): {"id": full(src, m["id"]), "family": fam, "lens": lens, "statement": m["statement"], "rests_on": m["rests_on"],
                                 "holds_against": m.get("holds_against")} for m in ms}


def cell_scores(src):
    """src's cells and routes scored against src/measured.json (a list of {readout, measured, n, interval, artifact,
    item}); a row whose readout is not one of src's or whose measured value is not a number is listed in "unscored"
    with the reason."""
    data = json.loads((src / "cells.json").read_text())
    rids = {r["id"] for c in data["cells"] + data.get("routes", []) for r in c["readouts"]}
    rows = json.loads((src / "measured.json").read_text())
    assert isinstance(rows, list), f"{src / 'measured.json'} must be a JSON list of rows"
    good = [r for r in rows if r.get("readout") in rids and engine.number(r.get("measured"))]
    bad = [{**r, "reason": "readout is not a readout id of cells.json" if r.get("readout") not in rids else "measured is not a number"}
           for r in rows if r not in good]
    fc = json.loads((src / "cell_forecasts.json").read_text())
    return scored({n: [{**f, "id": f["readout"]} for f in v["forecasts"]] for n, v in fc.items()},
                  [{"id": r["readout"], "value": r["measured"], "item": r.get("item"), "quote": r.get("artifact")} for r in good]) | {"unscored": bad}


def written(src, kind):
    """When src's forecasts (kind forecasts) or cell forecasts (kind cells) were written: the earlier of the time its
    forecasts.md or cells.md records and the first commit of forecasts.json or cell_forecasts.json."""
    md, js = ("forecasts.md", "forecasts.json") if kind == "forecasts" else ("cells.md", "cell_forecasts.json")
    m = re.search(r"[Ww]ritten (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d) UTC", (src / md).read_text()) if (src / md).exists() else None
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%cd", "--date=format-local:%Y-%m-%dT%H:%M:%S", "--", str((src / js).resolve())],
                         cwd=ROOT, capture_output=True, text=True, check=True, env={**engine.os.environ, "TZ": "UTC"}).stdout
    times = [t for t in [m and m.group(1), out.split()[-1] if out.split() else None] if t]
    assert times, f"{src / js}: no written time in {md} and not committed: commit it before it is scored"
    return min(times)


def standing(folder, sources):
    """Scores each source's forecasts (one job per source, at once) and cells, each folder once. A mechanism's record is
    rebuilt from these scores alone (name every folder whose forecasts count in --from): one row per measured number
    (board item and value), the forecast written earliest; a forecast written at or after its result's posting time is
    not scored but listed. Carried: total gain above 0 on 3 or more distinct items; graveyard: at or below -2 nats on
    2 or more distinct items. Writes standing/<kind>-<source>.json and .md, standing.json, standing.md, graveyard.json."""
    out, sources = folder / "standing", list({s.resolve(): s for s in sources}.values())
    out.mkdir(parents=True, exist_ok=True)

    def score_source(src):
        path = out / f"forecasts-{src.name}.json"
        if (src / "forecasts.json").exists() and not path.exists():
            path.write_text(json.dumps(scored(json.loads((src / "forecasts.json").read_text()), find_measured(src, snapshot(src))), indent=1))
        if (src / "measured.json").exists():
            (out / f"cells-{src.name}.json").write_text(json.dumps(cell_scores(src), indent=1))
        return [(kind, json.loads((out / f"{kind}-{src.name}.json").read_text())) for kind in ("forecasts", "cells")
                if (out / f"{kind}-{src.name}.json").exists()]
    with ThreadPoolExecutor(8) as pool:
        scores = dict(zip(sources, pool.map(score_source, sources)))
    posted = {i["id"]: i["at"].rstrip("Z")[:19] for i in board("posted-times", "9999")[0]}
    records, graveyard, late, unscored = {}, {}, [], []
    for src in sources:
        if (src / "standing.json").exists():
            graveyard |= json.loads((src / "graveyard.json").read_text())
        for i, m in mechanisms_of(src).items():
            records.setdefault(i, {**m, "rows": {}})
    for src, kinds in scores.items():
        cell_targets = {t["id"] for t in json.loads((src / "targets.json").read_text())["targets"] if t.get("from_cell")} if (src / "targets.json").exists() else set()
        for kind, s in kinds:
            (out / f"{kind}-{src.name}.md").write_text(scores_md(s, f"{kind} of {src.name}, scored for {folder.name}"))
            unscored += [{"source": src.name, **r} for r in s.get("unscored", [])]
            item = {m["id"]: m.get("item") or f"{src.name}:{m['id']}" for m in s["measured"]}
            at = {k: written(src, k) for k in ("forecasts", "cells") if (src / ("forecasts.json" if k == "forecasts" else "cell_forecasts.json")).exists()}
            for n, p in s["forecasters"].items():
                if full(src, n) not in records:
                    continue
                for r in p["rows"]:
                    w = at["cells" if kind == "cells" or r["id"] in cell_targets else "forecasts"]
                    row = {**r, "source": f"{src.name} {kind}", "item": item[r["id"]], "written": w, "posted": posted.get(item[r["id"]])}
                    if not row["posted"] or w >= row["posted"]:
                        late.append({"mechanism": full(src, n), **{k: row[k] for k in ("source", "id", "item", "written", "posted")}})
                        continue
                    key, rows = (row["item"], row["measured"]), records[full(src, n)]["rows"]
                    if key not in rows or w < rows[key]["written"]:  # one score per measured number: the earliest forecast
                        rows[key] = row
    for m in records.values():
        m["rows"] = list(m["rows"].values())
        m["forecast"] = f = {"scored": len(m["rows"]), "items": len({r["item"] for r in m["rows"]}), "inside": sum(r["inside"] for r in m["rows"]),
                             "total_gain": round(sum(r["gain"] for r in m["rows"]), 3)}
        m["state"] = ("carried" if f["items"] >= 3 and f["total_gain"] > 0 else "graveyard" if f["items"] >= 2 and f["total_gain"] <= -2 else "not carried")
    graveyard |= {i: {"name": i, "round": folder.name, "statement": m["statement"], "state": "refuted by forecasts", "verdict": "", "forecast": m["forecast"],
                      "reason": f"total forecast gain {m['forecast']['total_gain']:+.2f} nats on {m['forecast']['scored']} numbers from "
                                f"{m['forecast']['items']} board items"} for i, m in records.items() if m["state"] == "graveyard"}
    ranked = sorted(records.values(), key=lambda m: -m["forecast"]["total_gain"])
    (folder / "standing.json").write_text(json.dumps({"utc": now(), "from": [str(s) for s in sources], "carried": [m for m in ranked if m["state"] == "carried"],
                                                      "records": {m["id"]: {k: m[k] for k in ("family", "state", "forecast", "statement")} for m in ranked},
                                                      "written_after_result": late, "unscored_measured": unscored}, indent=1))
    (folder / "graveyard.json").write_text(json.dumps(graveyard, indent=1))
    md = [f"# Standing, {folder.name}\n\nFrom {', '.join(s.name for s in sources)}. Gain per number: log density of the forecast minus the equal mixture of "
          "the two readers, clipped to [-3, 3] nats, at most 0 when the measured value is outside the forecast's own 90 % interval. A mechanism is scored "
          "once per measured number (board item and value), on the forecast it wrote earliest, and only when that forecast was written before the result "
          "was posted. The numbers of one board item are one experiment. Carried: total above 0 on numbers from 3 or more items; graveyard: at or below "
          "-2 on 2 or more items.\n",
          "| mechanism | family | scored | items | inside | total gain | state | statement |\n|---|---|---|---|---|---|---|---|"]
    md += [f"| {m['id']} | {m['family']} | {m['forecast']['scored']} | {m['forecast']['items']} | {m['forecast']['inside']} | {m['forecast']['total_gain']:+.2f} | "
           f"{m['state']} | {flat(m['statement'])[:160]} |" for m in ranked if m["forecast"]["scored"]]
    md += [f"\n## Written after the result, not scored ({len(late)} forecasts)\n", "| source | target | result | written | posted | mechanisms |\n|---|---|---|---|---|---|"]
    groups = {}
    for x in late:
        groups.setdefault((x["source"], x["id"], x["item"], x["written"], x["posted"]), []).append(x["mechanism"])
    md += [f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {k[4] or 'not on the board'} | {len(v)} |" for k, v in sorted(groups.items())]
    md += ["\n## measured.json rows not scored\n"] + ([f"- {x['source']} {x.get('readout')}: {x['reason']} ({x.get('item')})" for x in unscored] or ["none"])
    (folder / "standing.md").write_text("\n".join(md) + "\n")
    print(f"  standing: {len(records)} mechanisms, {sum(m['forecast']['scored'] > 0 for m in ranked)} scored, "
          f"{sum(m['state'] == 'carried' for m in ranked)} carried, {sum(m['state'] == 'graveyard' for m in ranked)} to the graveyard; "
          f"{len(late)} forecasts written after their result, {len(unscored)} measured rows not scored")


def judge_duplicates(folder, new, carried, graveyard):
    """One blind job lists new mechanisms that restate an earlier mechanism (a carried one or any record of standing),
    a graveyard entry, or a new one listed before them; writes duplicates.json and returns the ids to drop."""
    records = json.loads((folder / "standing.json").read_text())["records"]
    earlier = ([{"id": i, "statement": r["statement"]} for i, r in records.items()] + [{"id": m["id"], "statement": m["statement"]} for m in carried if m["id"] not in records]
               + [{"id": i, "statement": g["statement"], "failed": g.get("reason") or g.get("state")} for i, g in graveyard.items()])
    order, known = [m["id"] for m in new], {e["id"] for e in earlier}

    def valid(d):
        ps = json.loads((d / "duplicates.json").read_text())["pairs"]
        bad = [p for p in ps if p["new"] not in order or not str(p.get("reason", "")).strip()
               or not (p["earlier"] in known or p["earlier"] in order[:order.index(p["new"])])]
        return f"each pair needs new (an id of new.json), earlier (an id of earlier.json or a new id listed before it) and a reason; failing: {bad}" if bad else None
    engine.run([engine.job("duplicates", "judge", {"new.json": json.dumps([{k: m[k] for k in ("id", "family", "statement")} for m in new], indent=1),
                                                   "earlier.json": json.dumps(earlier, indent=1)}, {"duplicates.json": folder / "duplicates.json"}, valid)], folder)
    pairs = json.loads((folder / "duplicates.json").read_text())["pairs"]
    for p in pairs:
        print(f"  duplicate {p['new']} of {p['earlier']}: {p['reason']}")
    return {p["new"] for p in pairs}


def sd(f):
    """The sd of the normal a forecast stands for (round.py's log_density)."""
    return max((f["high"] - f["low"]) / 3.29, 0.01 * max(abs(f["value"]), 1))


def what_of(src, kind, tid):
    """What a scored number is: its target (forecasts) or readout (cells) in the source folder."""
    if kind == "forecasts":
        t = next(t for t in json.loads((src / "targets.json").read_text())["targets"] if t["id"] == tid)
        return {"what": t["what"], "unit": t["unit"], "cell": t["cell"]}
    data = json.loads((src / "cells.json").read_text())
    c, r = next((c, r) for c in data["cells"] + data.get("routes", []) for r in c["readouts"] if r["id"] == tid)
    return {"what": r["readout"], "unit": r["unit"], "cell": c.get("cell") or c["change"]}


def surprises(folder, sources):
    """Every number scored in folder/standing/ whose measured value lies outside both readers' 90 % intervals; z = the
    distance from the nearer reader's centre in that reader's sd. The same number (board item and value) scored in
    several folders is kept once, at its largest z. Marks numbers outside every forecaster's interval and lists the
    forecasters that had it inside. Writes surprises.json and surprises.md, most surprising first; returns the list."""
    by_name, found = {s.name: s for s in sources}, {}
    for path in sorted((folder / "standing").glob("*.json")):
        kind, name = path.stem.split("-", 1)
        s = json.loads(path.read_text())
        rows = {}
        for n, p in s["forecasters"].items():
            for r in p["rows"]:
                rows.setdefault(r["id"], {})[n] = r
        for m in s["measured"]:
            if m["value"] is None or m["id"] not in rows:
                continue
            x, fs = m["value"], rows[m["id"]]
            who = (lambda n: n if n in READERS else full(by_name[name], n))  # noqa: E731
            readers = next(iter(fs.values()))["nulls"]
            if any(r["low"] <= x <= r["high"] for r in readers):
                continue
            e = {"source": name, "kind": kind, "id": m["id"], "item": m.get("item"), "quote": m.get("quote"), "measured": x,
                 "z": round(min(abs(x - r["value"]) / sd(r) for r in readers), 2), "readers": readers, **what_of(by_name[name], kind, m["id"]),
                 "forecasts": {who(n): {k: f[k] for k in ("value", "low", "high", "gain")} for n, f in fs.items()},
                 "inside": [who(n) for n, f in fs.items() if f["low"] <= x <= f["high"]]}
            e["outside_every"] = not e["inside"]
            key = (e["item"], x)
            if key not in found or e["z"] > found[key]["z"]:
                found[key] = {**e, "also": sorted(set(found.get(key, {}).get("also", [])) | {f"{name} {m['id']}"})}
            else:
                found[key]["also"] = sorted(set(found[key]["also"]) | {f"{name} {m['id']}"})
    out = sorted(found.values(), key=lambda e: -e["z"])
    (folder / "surprises.json").write_text(json.dumps(out, indent=1))
    md = [f"# Surprises, {folder.name}\n\nScored numbers outside both no-theory readers' 90 % intervals, most surprising first. z: distance of the "
          "measured value from the nearer reader's centre, in that reader's sd ((high - low) / 3.29). \"Outside every\": no forecaster's interval "
          f"holds it. {len(out)} surprises.\n", "| # | number | unit | result | measured | reader-1 | reader-2 | z | outside every | inside (who had it) |\n"
          "|---|---|---|---|---|---|---|---|---|---|"]
    md += [f"| {k} | {e['source']} {e['id']}: {flat(e['what'])[:140]} | {e['unit']} | {e['item']} | {e['measured']:g} | "
           + " | ".join(f"{r['value']:g} [{r['low']:g}, {r['high']:g}]" for r in e["readers"])
           + f" | {e['z']:g} | {'yes' if e['outside_every'] else ''} | {', '.join(e['inside'])} |" for k, e in enumerate(out, 1)]
    (folder / "surprises.md").write_text("\n".join(md) + "\n")
    print(f"  {len(out)} surprises ({sum(e['outside_every'] for e in out)} outside every interval): {folder / 'surprises.md'}")
    return out


def check_rivals(d, tids, board_ids, n_facts, flags=None):
    """A surprise job's rivals.json: two mechanisms a and b (statement of at most 80 words, why the readers were wrong,
    rests_on 2+ board items, holds_against as check_mechanisms, forecasts of a third of the open targets or more);
    the pair differs (disjoint 90 % intervals) on 2 or more targets, or names a cell (complete, an existing job file, a
    and b disjoint, 0 < gpu_minutes <= 120; with flags, its command passes the flag check)."""
    j = json.loads((d / "rivals.json").read_text())
    ms, errors = j["rivals"], []
    if [m.get("id") for m in ms] != ["a", "b"]:
        return "rivals must be exactly two mechanisms with ids a and b"
    need = max(2, -(-len(tids) // 3))
    for m in ms:
        e = [f"statement has {len(m['statement'].split())} words; at most 80"] if len(m["statement"].split()) > 80 else []
        e += [] if str(m.get("readers_wrong", "")).strip() else ["readers_wrong: why the readers were wrong on the surprise"]
        e += [] if len(set(m.get("rests_on", [])) & board_ids) >= 2 else ["rests_on needs 2 or more item ids of board.jsonl"]
        h = m.get("holds_against")
        if not (isinstance(h, list) and len(h) == 2 and all(isinstance(x, dict) and engine.number(x.get("value")) and str(x.get("why", "")).strip()
                                                            and (x.get("item") in board_ids or x.get("fact") in range(n_facts)) for x in h)):
            e.append('holds_against needs 2 entries {"item": <id of board.jsonl> or "fact": <index in facts.json>, "value": <the number>, "why": ...}')
        errors += [f"{m['id']}: {x}" for x in e + forecast_errors(m.get("forecasts", []), tids, need)]
    if errors:
        return "; ".join(errors)
    apart = pair_apart(ms)
    c = j.get("cell")
    if c:
        e = [f"cell misses {k}" for k in C.CELL_KEYS if not str(c.get("cell", {}).get(k, "")).strip()]
        e += [f"cell misses {k}" for k in ("job", "command", "readout", "unit", "why") if not str(c.get(k, "")).strip()]
        e += [] if Path(str(c.get("job"))).stem in C.JOB_FILES else ["cell job is not a file of the job folders"]
        e += [] if engine.number(c.get("gpu_minutes")) and 0 < c["gpu_minutes"] <= 120 else ["cell gpu_minutes must be in (0, 120]"]
        fa, fb = c.get("a", {}), c.get("b", {})
        e += [] if all(engine.number(f.get(k)) for f in (fa, fb) for k in ("value", "low", "high")) and C.apart({**fa}, {**fb}) and all(
            f["low"] <= f["value"] <= f["high"] for f in (fa, fb)) else ["cell a and b need value, low, high each, with disjoint intervals"]
        e += C.command_errors(c["command"], flags) if flags else []
        errors += [f"cell: {x}" for x in e]
    elif len(apart) < 2:
        errors.append(f"the rivals' 90 % intervals are disjoint on {len(apart)} open targets ({apart}); need 2, or a cell on which they are")
    return "; ".join(errors) or None


def pair_apart(ms):
    """Open targets on which rivals a and b have disjoint 90 % intervals."""
    fa, fb = ({f["id"]: f for f in m["forecasts"]} for m in ms)
    return sorted(t for t in fa.keys() & fb.keys() if C.apart(fa[t], fb[t]))


def check_answered(d, ids, texts):
    """The check job's answered.json: each listed id a candidate once; kind open (an open work item) or posted (a
    board item), with a quote found in that item's text."""
    rows = json.loads((d / "answered.json").read_text())["answered"]
    bad = [r for r in rows if r.get("id") not in ids or r.get("kind") not in ("open", "posted") or r.get("item") not in texts
           or flat(str(r.get("quote", ""))) not in flat(texts[r["item"]])]
    return (f"each entry needs id (a candidate), kind open or posted, item (an open work item or board item id) and a quote found in that item's "
            f"text; failing: {bad}") if bad or len({r["id"] for r in rows}) != len(rows) else None


def round11(folder, sources, n_top):
    """The version-11 round: standing, surprises, targets_open, forecast (readers and carried mechanisms), propose (two
    rival mechanisms per surprise, the n_top most surprising, then the duplicate judge), cells (the pairs' cells and one
    route per pair, checked against open and posted work, forecast by everyone, ranked), experiments. A stage whose
    output exists is skipped."""
    start, out, pre = time.time(), folder / "jobs", prefix(folder)
    folder.mkdir(parents=True, exist_ok=True)
    print("== standing")
    if not (folder / "standing.json").exists():
        standing(folder, sources)
    st = json.loads((folder / "standing.json").read_text())
    carried = [{k: m[k] for k in MECHANISM_KEYS} for m in st["carried"]]
    print("== surprises")
    found = surprises(folder, list({s.resolve(): s for s in sources}.values()))
    print("== targets_open")
    items = open_targets(folder) if not (folder / "targets.json").exists() else board("board", "9999")[0]
    utc, tids = snapshot(folder), [t["id"] for t in json.loads((folder / "targets.json").read_text())["targets"]]
    common = {"DIRECTION.md": ROOT / "DIRECTION.md", "board.jsonl": "".join(json.dumps(i) + "\n" for i in items), "work.md": folder / "work.md"}
    print("== forecast")
    forecasts = run_forecasters(folder, common, {m["id"]: json.dumps(m, indent=1) for m in carried}, out / "forecast", workers=16)
    print("== propose")
    top, new, pairs, drop = found[:n_top], [], [], set()
    facts, board_ids = json.loads(newest("facts.json").read_text()), {i["id"] for i in items}
    dead = json.loads(newest("graveyard.json").read_text()) | json.loads((folder / "graveyard.json").read_text())
    if top:
        statements = {i: r["statement"] for i, r in st["records"].items()}
        engine.run([engine.job("surprise_propose", f"s{k}", {**common, "targets.json": folder / "targets.json", "facts.json": json.dumps(facts, indent=1),
                                                             "graveyard.json": json.dumps(dead, indent=1), "jobs.md": C.jobs_md(),
                                                             "surprise.json": json.dumps({x: e[x] for x in e if x != "forecasts"} | {"forecasts": e["forecasts"]}, indent=1),
                                                             "right.json": json.dumps([{"id": i, "statement": statements[i]} for i in e["inside"] if i in statements], indent=1)},
                               {"rivals.json": out / f"rivals-s{k}.json"}, C.flags_once(lambda d, fl: check_rivals(d, tids, board_ids, len(facts), fl)))
                    for k, e in enumerate(top, 1)], folder, len(top))
        for k, e in enumerate(top, 1):
            j = json.loads((out / f"rivals-s{k}.json").read_text())
            lens = f"rival explanations of surprise {e['source']} {e['id']} ({e['item']}, measured {e['measured']:g})"
            ms = [{"id": f"{folder.name}/s{k}-{m['id']}", "family": f"s{k}", "lens": lens, **{x: m[x] for x in ("statement", "rests_on", "holds_against", "readers_wrong", "forecasts")}}
                  for m in j["rivals"]]
            pairs.append({"family": f"s{k}", "surprise": {x: e[x] for x in ("source", "id", "item", "measured", "z", "what")}, "a": ms[0]["id"], "b": ms[1]["id"],
                          "apart": pair_apart(j["rivals"]), "cell": j.get("cell")})
            new += ms
        drop = judge_duplicates(folder, new, carried, dead)  # version 11.1: reported only; a pair may restate older mechanisms
    forecasts |= {m["id"]: m.pop("forecasts") for m in new}
    mechs = carried + [{k: m[k] for k in (*MECHANISM_KEYS, "readers_wrong")} for m in new]
    (folder / "pairs.json").write_text(json.dumps(pairs, indent=1))
    (folder / "mechanisms.json").write_text(json.dumps({"mechanisms": mechs}, indent=1))
    (folder / "forecasts.json").write_text(json.dumps(forecasts, indent=1))
    write_md(folder, utc, forecasts, [f"\n- {m['id']} ({m['family']}{', carried' if m in carried else ''}): {flat(m['statement'])}" for m in mechs])
    print(f"  {len(carried)} carried and {len(new)} new mechanisms ({len(drop)} judged restatements, kept), {len(pairs)} pairs, {len(tids)} targets")
    print("== cells")
    counts = {}
    whole = pairs
    if whole and not (folder / "cells.json").exists():
        known = {"targets": json.loads((folder / "targets.json").read_text())["targets"], "facts": facts}
        fams = {}
        for m in mechs:
            fams.setdefault(m["family"], {"lens": m["lens"], "mechanisms": []})["mechanisms"].append({k: m[k] for k in ("id", "statement", "rests_on")})
        props = [{"id": f"c{k:02d}", "family": p["family"], "mechanism": p["a"], "against": p["b"], **{x: p["cell"][x] for x in ("cell", "job", "command", "readout", "unit", "why", "gpu_minutes")},
                  **{x: p["cell"]["a"][x] for x in ("value", "low", "high")}, "against_value": p["cell"]["b"]["value"], "base_only": False, "best_base": None}
                 for k, p in enumerate((p for p in whole if p["cell"]), 1)]
        merged = [{"id": f"{pre}-m{p['id'][1:]}", "cell": p["cell"], "job": p["job"], "command": p["command"],
                   "readouts": [{"id": f"{pre}-m{p['id'][1:]}-r1", "readout": p["readout"], "unit": p["unit"], "from": [p["id"]]}]} for p in props]
        by_mid = {m["id"]: {k: m[k] for k in ("id", "statement", "rests_on")} for m in mechs}
        routes, dropped = route_jobs(folder, {p["family"]: {"lens": f"the rival pair about surprise {p['surprise']['source']} {p['surprise']['id']}",
                                                            "mechanisms": [by_mid[p["a"]], by_mid[p["b"]]]} for p in whole}, items, known)
        routes = C.route_cells(routes, C.table_rows(), pre)
        C.attach(merged, {p["id"]: p for p in props})
        cands = C.blind(merged) + C.blind_routes(routes)
        work = {sec.split("\n", 1)[0].strip(): sec for sec in ("\n" + (folder / "work.md").read_text()).split("\n## ")[1:]} if (folder / "work.md").exists() else {}
        texts = {**{i["id"]: i["text"] for i in items}, **work}
        engine.run([engine.job("cells_check", "check", {**common_inputs(items, known), "work.md": folder / "work.md", "candidates.json": json.dumps(cands, indent=1)},
                               {"answered.json": out / "answered.json"}, lambda d: check_answered(d, {c["id"] for c in cands}, texts))], folder)
        answered = {r["id"]: r for r in json.loads((out / "answered.json").read_text())["answered"]}
        posted = {i for i, r in answered.items() if r["kind"] == "posted"}
        dropped += [{"id": i, "reason": f"answered by posted {answered[i]['item']}: {answered[i]['quote'][:160]}"} for i in sorted(posted)]
        merged, routes = [c for c in merged if c["id"] not in posted], [c for c in routes if c["id"] not in posted]
        left_out = [i for i, r in st["records"].items() if r["forecast"]["total_gain"] <= -2]
        counts = forecast_rank(folder, fams, props, {p["id"]: p for p in props}, merged, routes, dropped, common_inputs(items, known),
                               "Plan `specs/SPEC_engine_v11.md`. ", left_out, {i: r for i, r in answered.items() if r["kind"] == "open"},
                               {f"{pre}-m{p['id'][1:]}": (p["mechanism"], p["against"]) for p in props})
    if (folder / "cells.json").exists():
        print("== experiments")
        experiments(folder)
    (folder / "run.json").write_text(json.dumps({"commit": sh("git", "rev-parse", "--short", "HEAD").strip(), "command": " ".join(sys.argv), "utc": utc, "version": 11,
                                                 "from": [str(s) for s in sources], "carried": len(carried), "surprises": len(found), "pairs": len(pairs),
                                                 "new": len(new), "duplicates": len(drop), "targets": len(tids), **counts,
                                                 "minutes": round((time.time() - start) / 60, 1), "job_dirs": str(engine.tmp())}, indent=1))
    print(f"{(time.time() - start) / 60:.1f} minutes")


def wide_round_v10(folder, sources, n):
    """--propose-wide, the version-10 round: standing, targets_open, forecast, propose (six lens jobs, the duplicate
    judge), cells and routes from every family, experiments; a stage whose output exists is skipped."""
    start, out = time.time(), folder / "jobs"
    folder.mkdir(parents=True, exist_ok=True)
    print("== standing")
    if not (folder / "standing.json").exists():
        standing(folder, sources)
    carried = [{k: m[k] for k in MECHANISM_KEYS} for m in json.loads((folder / "standing.json").read_text())["carried"]]
    print("== targets_open")
    items = open_targets(folder) if not (folder / "targets.json").exists() else board("board", "9999")[0]
    utc, tids = snapshot(folder), [t["id"] for t in json.loads((folder / "targets.json").read_text())["targets"]]
    common = {"DIRECTION.md": ROOT / "DIRECTION.md", "board.jsonl": "".join(json.dumps(i) + "\n" for i in items), "work.md": folder / "work.md"}
    print("== forecast")
    forecasts = run_forecasters(folder, common, {m["id"]: json.dumps(m, indent=1) for m in carried}, out / "forecast")
    print("== propose")
    facts, board_ids = json.loads(newest("facts.json").read_text()), {i["id"] for i in items}
    dead = json.loads(newest("graveyard.json").read_text()) | json.loads((folder / "graveyard.json").read_text())
    engine.run([engine.job("forecast_propose", k, {**common, "targets.json": folder / "targets.json", "facts.json": json.dumps(facts, indent=1),
                                                   "readers.json": json.dumps({r: forecasts[r] for r in READERS}, indent=1), "graveyard.json": json.dumps(dead, indent=1)},
                           {"mechanisms.json": out / f"mechanisms-{k}.json"}, lambda d: check_mechanisms(d, n, tids, board_ids, len(facts)), n=n, lens=lens)
                for k, lens in LENSES.items()], folder, len(LENSES))
    new = [{"id": f"{folder.name}/{k}-{m['id'][3:]}", "family": k, "lens": lens, **{x: m[x] for x in ("statement", "rests_on", "holds_against", "forecasts")}}
           for k, lens in LENSES.items() for m in json.loads((out / f"mechanisms-{k}.json").read_text())["mechanisms"]]
    drop = judge_duplicates(folder, new, carried, dead)
    new = [m for m in new if m["id"] not in drop]
    forecasts |= {m["id"]: m.pop("forecasts") for m in new}
    mechs = carried + new
    (folder / "mechanisms.json").write_text(json.dumps({"mechanisms": mechs}, indent=1))
    (folder / "forecasts.json").write_text(json.dumps(forecasts, indent=1))
    write_md(folder, utc, forecasts, [f"\n- {m['id']} ({m['family']}{', carried' if m in carried else ''}): {flat(m['statement'])}" for m in mechs])
    print(f"  {len(carried)} carried and {len(new)} new mechanisms ({len(drop)} dropped as duplicates), {len(tids)} targets: {folder / 'forecasts.md'}")
    print("== cells")
    fams = {}
    for m in mechs:
        fams.setdefault(m["family"], {"lens": m["lens"], "mechanisms": []})["mechanisms"].append({k: m[k] for k in ("id", "statement", "rests_on")})
    records = json.loads((folder / "standing.json").read_text())["records"]
    left_out = [i for i, r in records.items() if r["forecast"]["total_gain"] <= -2]
    counts = cells(folder, fams, {"targets": json.loads((folder / "targets.json").read_text())["targets"], "facts": facts},
                   "Plan `specs/SPEC_engine_v10.md`. ", left_out) if not (folder / "cells.json").exists() else {}
    print("== experiments")
    experiments(folder)
    (folder / "run.json").write_text(json.dumps({"commit": sh("git", "rev-parse", "--short", "HEAD").strip(), "command": " ".join(sys.argv), "utc": utc,
                                                 "from": [str(s) for s in sources], "carried": len(carried), "new": len(new), "duplicates": len(drop), "targets": len(tids), **counts,
                                                 "minutes": round((time.time() - start) / 60, 1), "job_dirs": str(engine.tmp())}, indent=1))
    print(f"{(time.time() - start) / 60:.1f} minutes: {folder / 'experiments.md'}")


def experiments(folder):
    """experiments.md: the cells to run, list A (top 10 by separation per GPU minute), list B (base-only cells, top 5 by
    the highest forecast minus the best known base count), list C (no-reward routes by the margin of the median forecast
    over the stored subset count, in sd), each with its command, and the cells turned into targets on open work.""" 
    data = json.loads((folder / "cells.json").read_text())
    cs, routes = data["cells"], data.get("routes", [])
    a = sorted(cs, key=lambda c: -c["per_minute"])[:10]
    b = sorted((c for c in cs if c["base_only"]), key=lambda c: -max(r["top"]["gain"] for r in c["readouts"]))[:5]
    md = [f"# Experiments, {folder.name}\n\nEach cell's forecasts and proposers are in `cells.md`. Run from the top; write each readout's number "
          "into `measured.json` (a list of {readout, measured, n, interval, artifact, item}).\n", "## A: separation per GPU minute\n"]
    md += [f"{k}. {c['id']} ({c['separation']} split readouts, {c['gpu_minutes']:g} min): {c['cell']['model']}; {c['cell']['prompt']}; {c['cell']['set']}, "
           f"n {c['cell']['n']}. Readouts: {', '.join(r['id'] for r in c['readouts'])}.\n   `{c['command']}`" for k, c in enumerate(a, 1)]
    md.append("\n## B: base-only cells by the highest forecast over the best known base count\n")
    md += [f"{k}. {c['id']} ({max(r['top']['gain'] for r in c['readouts']):+g} over best, {c['gpu_minutes']:g} min): {c['cell']['model']}; "
           f"{c['cell']['prompt']}; {c['cell']['set']}.\n   `{c['command']}`" for k, c in enumerate(b, 1)]
    md.append("\n## C: no-reward routes by the margin of the median forecast over the stored subset count, in its sd\n")
    md += [f"{k}. {c['id']} ({c['family']}; margin {C.margin_text(c['score'])}; {c['tokens']:g} tokens per problem, {c['gpu_minutes']:g} min): {c['change']} "
           + "; ".join(f"{x['set']} {x.get('subset')} median {C.g(x['median'])} against stored {x['best_base']['value']:g} (sd {x['best_base']['sd']:g})"
                       for x in c["readouts"] if x["best_base"])
           + f".\n   `{c['command']}`\n   RL arm: `{c['rl_command']}`" for k, c in enumerate(sorted(routes, key=lambda c: -(c["score"] if c["score"] is not None else -1e9)), 1)]
    md.append("\n## Free targets: cells and routes an open work item already answers (scored next round from its report)\n")
    md += [f"- {c['id']}: {c['item']} ({c['quote'][:160]})" for c in data.get("converted", [])] or ["none"]
    (folder / "experiments.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["round", "make", "score", "cells"])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--propose", type=int, default=0, help="make: also write this many mechanisms about the targets "
                        "(forecasters f2-m01 ...); round: mechanisms per lens (default 6)")
    parser.add_argument("--lens", help="make: the family of causes the --propose mechanisms must come from")
    parser.add_argument("--from", dest="runs", type=Path, nargs="+", default=[], help="cells: the forecast run folders whose mechanisms "
                        "design cells; round: the previous round folder, or forecast run and cells folders")
    parser.add_argument("--rescore", action="store_true", help="score: no job; the newest scores file's measured values, scored again")
    parser.add_argument("--model-all", help="every job's model (smoke tests)")
    parser.add_argument("--propose-wide", action="store_true", help="round: the version-10 round (six lens jobs propose, every family designs "
                        "cells and a route) in place of score first")
    parser.add_argument("--surprises", type=int, default=6, help="round: rival pairs for at most this many surprises (default 6)")
    a = parser.parse_args()
    engine.args.model_all = a.model_all
    {"round": lambda: wide_round_v10(a.folder, a.runs, a.propose or 6) if a.propose_wide else round11(a.folder, a.runs, a.surprises), "make": lambda: make(a.folder, a.propose, a.lens),
     "score": lambda: score(a.folder, a.rescore), "cells": lambda: cells_run(a.folder, a.runs)}[a.command]()
