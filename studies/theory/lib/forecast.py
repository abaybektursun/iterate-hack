# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Forecasts of the team's open GPU work (studies/theory/README.md, "Forecast runs"), and the default theory round.

  uv run studies/theory/lib/forecast.py round <folder> --from <previous round, forecast run and cells folders...>
      version 14 (.claude/skills/theory/SKILL.md): standing (forecasts scored once per number, only those written before
      their result; carried: gain above 0 on 3 or more results, never a graveyard or refuted mechanism), direct facts,
      surprises, targets_open, direct-test plans (top 5 untested carried mechanisms), propose (rival pairs about the top
      surprises, each pair with one shared test: one statistic, disjoint ranges for the two rivals), a gate (stops until
      the planned mechanisms have rows in results/refuted.json or direct_tested.json; --go continues), forecast by the
      mechanisms that hold a direct test only, cells by holders that forecast something the readers do not,
      experiments. Rerun the same command after the direct tests.
      --propose-wide: the version-10 round (six lens jobs of --propose N mechanisms, every family designs cells).
  uv run studies/theory/lib/forecast.py synthesis <round folder> [--from <folders for standing>]
      version 17: standing (with --from), direct facts, the explore half of every stored cell (rows.py,
      data/split_v1.json: problems split by a hash of their id) copied into the job directories; three accounts written
      in parallel, each starting from a different third of the facts, each a headless job with Bash on the explore rows:
      at most 6 sentences, a mark per fact, its 3 worst facts, three new consequences (one statistic on stored cells, no
      two on the same cells, measured on the explore half, with a test-half range at most 2.5 explore interval widths
      wide) and one GPU cell; one blind marker per account marks the facts; one adversary per consequence (also on the
      explore rows) writes the strongest alternative, computes its explore value (or names a board result that already
      shows the number: rejected); a consequence whose adversary's explore value lies inside the account's explore
      interval is dropped; synthesis_tests.md (test half only); a gate until every test has rows (add-rows recomputes
      the verdict: holds only if the test-half 90 % interval is inside the range and excludes the adversary's test-half
      value, else not separated); then synthesis.md ranks the accounts. Rerun the same command after the tests.
      version 18: consequences are of two kinds: `weights` (one statistic of the committed per-matrix weights tables,
      rows.WEIGHTS, explore matrices of data/split_matrices_v1.json for writers, test matrices for tests; at least 2 per
      account) and `rows` (stored sampling rows; at most 2); a consequence is dropped when the adversary's explore value
      lies inside the account's range or explore interval; each account names one weights-only computation in no committed
      table (weights_cell), a blind adversary predicts it too, and weights_cells.md ranks them by the gap between the two
      predictions in interval widths (none is run by the engine).
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

Every job is round.py's blind job: claude -p in an empty directory with Read and Write only (synthesis accounts and
adversaries: also Bash, in a directory holding the explore rows), the model round.py gives
cross_predict (--model-all <model> overrides it, for smoke tests).
"""
import argparse
import json
import random
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells as C  # noqa: E402
import round as engine  # noqa: E402
import rows as R  # noqa: E402

ROOT = engine.ROOT
ROUND = ROOT / "studies/theory/results/engine/round-07"  # the newest round: its unrefuted theories forecast
ENGINE = ROOT / "studies/theory/results/engine"
REFUTED = ROOT / "studies/theory/results/refuted.json"  # mechanisms whose stated cause a direct test refuted (version 11.2)
TESTED = ROOT / "studies/theory/results/direct_tested.json"  # direct tests of a mechanism's distinctive claim: holds or refuted (version 12)
READERS = ["reader-1", "reader-2"]
LENSES = {  # the six families of causes of specs/SPEC_forecast03.md (forecast runs 03-08)
    "stopping": "when and how the model stops: token cap, loops, end-of-text, answer markers",
    "sampling": "sampling: temperature, top-p, entropy of the next-token distribution, what a vote over samples adds",
    "weights": "weight space: the RL weight change, its top directions, scaling and transplanting it",
    "training": "training data and objective: what Think-SFT imitation, RL reward and pretraining each put into the model, exposure of problems",
    "problems": "problem structure: difficulty, domain, answer type, length of the needed derivation",
    "grader": "the grader and the measurement itself: extraction, equivalence, seeds, set composition, what a count hides"}
MECHANISM_KEYS = ("id", "family", "lens", "statement", "rests_on", "holds_against")
MIN_N = 50  # rows a direct test needs before a verdict of holds (version 14)
VERDICT_RULE = ("Verdict rule (version 14): a mechanism holds only if the statistic's 90 % interval lies wholly inside its range (for a "
                "carried plan: wholly on the holding side of the threshold) and the statistic rests on at least 50 rows; otherwise the row is "
                "`undecided`, with the n that would decide it. For a rival pair's shared test, a value in neither rival's range refutes both; "
                "write one row per rival.")
MAX_THEORIES = 6
THEORY = ("- theory.json: a theory of the team's results. Derive each forecast from the theory as written: say in the\n"
          "  reason which part of the theory gives the number. Where the theory implies nothing about a target, do not\n"
          "  guess: answer \"theory says nothing\" for it.\n")
NOTHING = (' For a target the theory says nothing about, write {"id": "t02", "value": null, "low": null, "high": null, '
           '"reason": "theory says nothing"}.')
engine.args = engine.args or argparse.Namespace(model_all=None, workers=8)  # round.py sets its own
for stage in ("forecast_targets", "forecast", "forecast_propose", "forecast_score", "cells_propose", "cells_merge", "cells_forecast", "routes_propose", "duplicates", "surprise_propose", "cells_check", "direct_test_plan", "synthesis", "synthesis_marks", "synthesis_adversary", "synthesis_adversary_weights", "synthesis_cell_adversary"):
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
    refuted = {r["mechanism"]: r for r in json.loads(REFUTED.read_text())}
    held = {r["mechanism"]: r for r in json.loads(TESTED.read_text()) if r["verdict"] == "holds"}
    refuted |= {r["mechanism"]: r for r in json.loads(TESTED.read_text()) if r["verdict"] == "refuted"}
    for i in refuted.keys() & records.keys():  # a direct test refuted the stated cause: buried whatever the forecast gain
        records[i]["state"] = "cause refuted"
    for i in held.keys() & records.keys():
        records[i]["direct_test"] = f"holds ({held[i]['result']}: {held[i]['claim']})"
    buried = set(graveyard) | {i for i, m in records.items() if m["state"] == "graveyard"}
    for i in buried & records.keys():  # an earlier round's graveyard entry is never carried again
        if records[i]["state"] == "carried":
            records[i]["state"] = "graveyard (earlier round)"
    for m in records.values():  # a forecast a measured.json row put outside its interval: no direct-test plan for this mechanism
        m["cell_missed"] = sorted({r["source"] + " " + r["id"] for r in m["rows"] if r["source"].endswith(" cells") and not r["inside"]})
    graveyard |= {i: {"name": i, "round": folder.name, "statement": m["statement"], "state": "refuted by forecasts", "verdict": "", "forecast": m["forecast"],
                      "reason": f"total forecast gain {m['forecast']['total_gain']:+.2f} nats on {m['forecast']['scored']} numbers from "
                                f"{m['forecast']['items']} board items"} for i, m in records.items() if m["state"] == "graveyard"}
    graveyard |= {i: {"name": i, "round": folder.name, "statement": m["statement"], "state": "refuted by a direct test", "verdict": "", "forecast": m["forecast"],
                      "reason": f"{refuted[i]['result']}: {refuted[i].get('measured', '')} ({refuted[i]['claim']})"} for i, m in records.items() if m["state"] == "cause refuted"}
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
           f"{m['state']}{'; direct test holds' if m.get('direct_test') else ''} | {flat(m['statement'])[:160]} |" for m in ranked if m["forecast"]["scored"]]
    md += ["\n## Forecast well, cause refuted\n\nForecast gain is not evidence for the stated cause (`studies/theory/results/refuted.json`).\n",
           "| mechanism | scored | items | total gain | refuted claim | result | measured |\n|---|---|---|---|---|---|---|"]
    md += [f"| {m['id']} | {m['forecast']['scored']} | {m['forecast']['items']} | {m['forecast']['total_gain']:+.2f} | {refuted[m['id']]['claim']} | "
           f"{refuted[m['id']]['result']} | {refuted[m['id']].get('measured', '')} |" for m in ranked if m["state"] == "cause refuted"]
    md += [f"| {i} | no forecast record in these folders | | | {r['claim']} | {r['result']} | {r.get('measured', '')} |" for i, r in refuted.items() if i not in records]
    md += ["\n## Direct test holds\n"] + ([f"- {m['id']}: {m['direct_test']}" for m in ranked if m.get("direct_test")] or ["none"])
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
    and b disjoint, 0 < gpu_minutes <= 120; with flags, its command passes the flag check). With flags (the first
    check) the pair's shared direct test is checked too (pair_test_errors); a pair whose test still fails after the
    send-back is dropped, not the round."""
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
    if flags:  # first check only: a pair without a valid shared test is dropped after the send-back, not the round
        errors += [f"test: {x}" for x in pair_test_errors(j.get("test") or {})]
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


def pair_test_errors(t):
    """Errors of a rival pair's shared direct test (version 14): claim, statistic, stored files that exist, the rows,
    n of at least MIN_N, computation, null, and ranges a, b and null fixed in advance, all three pairwise disjoint."""
    e = [f"missing {k}" for k in ("claim", "statistic", "rows", "computation", "null") if not str(t.get(k, "")).strip()]
    files = t.get("files") or []
    e += [] if files else ["files: one or more stored paths whose rows give the statistic"]
    e += [f"{f} does not exist in the repository" for f in files if not (ROOT / f).exists()]
    e += [] if engine.number(t.get("n")) and t["n"] >= MIN_N else [f"n: the number of rows the statistic is computed on, at least {MIN_N}"]
    r = t.get("ranges") or {}
    if not all(isinstance(r.get(k), list) and len(r[k]) == 2 and all(engine.number(x) for x in r[k]) and r[k][0] <= r[k][1] for k in ("a", "b", "null")):
        return e + ['ranges needs "a", "b" and "null", each [low, high] in the statistic\'s unit with low <= high']
    apart = lambda x, y: r[x][1] < r[y][0] or r[y][1] < r[x][0]
    return e + [f"ranges {x} {r[x]} and {y} {r[y]} overlap; they must be disjoint (a rival whose range holds the null's could hold without beating the null)"
                for x, y in (("a", "b"), ("a", "null"), ("b", "null")) if not apart(x, y)]


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


def direct_facts():
    """Every row of refuted.json and direct_tested.json: mechanism, claim, verdict, deciding number and result id."""
    return ([{"mechanism": r["mechanism"], "claim": r["claim"], "verdict": "refuted", "measured": r.get("measured", "not recorded"), "result": r["result"]}
             for r in json.loads(REFUTED.read_text())]
            + [{"mechanism": r["mechanism"], "claim": r["claim"], "verdict": r["verdict"], "measured": r.get("measured", "not recorded"), "result": r["result"]}
               for r in json.loads(TESTED.read_text())])


def add_rows(path):
    """Append a test's rows (a JSON list of {mechanism, claim, result, verdict, measured}) to direct_tested.json, and the
    refuted ones to refuted.json, each stamped with `added` in UTC (ISO, ending in Z)."""
    rows = json.loads(Path(path).read_text())
    for r in rows:
        assert r["verdict"] in ("holds", "refuted", "undecided", "not separated") and all(r.get(k) for k in ("mechanism", "claim", "result", "measured")), r
        if "adversary" in r or r["verdict"] == "not separated":  # version 16 rows: the verdict is recomputed here
            assert r["verdict"] == verdict16(r), f"{r['mechanism']}: verdict {r['verdict']}, rule gives {verdict16(r)}"
        r["added"] = now() + "Z"
    for f, keep in ((TESTED, rows), (REFUTED, [r for r in rows if r["verdict"] == "refuted"])):
        f.write_text(json.dumps(json.loads(f.read_text()) + keep, indent=1, ensure_ascii=False) + "\n")
    print(f"added {len(rows)} rows to {TESTED.name} ({sum(r['verdict'] == 'refuted' for r in rows)} also to {REFUTED.name})")


def results_md(items):
    """The board's results as the forecasters see them in short: id, title and score lines."""
    return "\n".join(f"{i['id']}: " + " | ".join(x.strip() for x in i["text"].splitlines() if x.startswith(("title:", "score:")))
                     for i in items if i["kind"] == "result") + "\n"


def data_md():
    """The stored data the plans may name: every README table row of studies/*/README.md that names a results/ or data/
    path, and the folders two levels under each study's results/ and data/."""
    rows = [f"{p.parent.name}: {line}" for p in sorted(ROOT.glob("studies/*/README.md")) for line in p.read_text().splitlines()
            if line.startswith("|") and re.search(r"`(results|data)/", line)]
    dirs = sorted(str(d.relative_to(ROOT)) for d in ROOT.glob("studies/*/*/*/*") if d.parts[-3] in ("results", "data"))
    return "# Stored data\n\n## README rows (study: row)\n\n" + "\n".join(rows) + "\n\n## Folders and files\n\n" + "\n".join(dirs) + "\n"


def test_errors(j, board_ids):
    """Errors of a carried mechanism's direct test: claim, computation, refuting observation, threshold, deciding stored
    files that exist; or "decided_by": a posted result (id, number, verdict) that already decides the claim."""
    if j.get("decided_by"):
        b = j["decided_by"]
        return [] if b.get("result") in board_ids and str(b.get("number", "")).strip() and b.get("verdict") in ("holds", "refuted") and str(j.get("claim", "")).strip() else [
            'decided_by needs result (a board result id), number and verdict holds or refuted, beside the claim']
    e = [f"missing {k}" for k in ("claim", "computation", "refuted_if", "threshold") if not str(j.get(k, "")).strip()]
    files = j.get("files") or []
    e += [] if files else ["files: one or more stored paths that decide the claim"]
    return e + [f"{f} does not exist in the repository" for f in files if not (ROOT / f).exists()]


def check_plan(d, board_ids):
    """A direct-test plan (test_errors) with the reason only this mechanism implies the claim."""
    j = json.loads((d / "plan.json").read_text())
    e = test_errors(j, board_ids) + ([] if j.get("decided_by") or str(j.get("why_only_this", "")).strip() else ["missing why_only_this"])
    return "; ".join(e) or None


def direct_tests(folder, items, top=5):
    """For each of the top carried mechanisms (by gain) with no row in refuted.json or direct_tested.json and no forecast
    a measured.json row put outside its interval, one blind job writes a direct offline test plan of the claim only its
    cause makes, or names the posted result that already decides it. Writes direct_tests.json; an agent runs each plan."""
    out, st = folder / "jobs", json.loads((folder / "standing.json").read_text())
    done = {r["mechanism"] for r in direct_facts()}
    ranked = [m for m in st["carried"] if m["id"] not in done and not m.get("cell_missed")]
    todo, others, board_ids = ranked[:top], ranked[:top * 2], {i["id"] for i in items}
    data = data_md()
    engine.run([engine.job("direct_test_plan", m["id"].replace("/", "-"), {
        "mechanism.json": json.dumps({k: m.get(k) for k in ("id", "statement", "rests_on", "holds_against", "forecast")}, indent=1),
        "others.json": json.dumps([{"id": o["id"], "statement": o["statement"]} for o in others if o["id"] != m["id"]], indent=1),
        "direct_facts.json": json.dumps(direct_facts(), indent=1), "results.md": results_md(items), "data.md": data},
        {"plan.json": out / f"plan-{m['id'].replace('/', '-')}.json"}, lambda d: check_plan(d, board_ids)) for m in todo], folder, len(todo) or 1)
    plans = [{"mechanism": m["id"], "kind": "carried", "gain": m["forecast"]["total_gain"], "items": m["forecast"]["items"], "statement": m["statement"],
              **json.loads((out / f"plan-{m['id'].replace('/', '-')}.json").read_text())} for m in todo]
    (folder / "direct_tests.json").write_text(json.dumps(plans, indent=1))
    print(f"  {len(plans)} direct-test plans for carried mechanisms")


def tests_md(folder, plans):
    """direct_tests.md: every plan (carried mechanisms, and one shared test per rival pair), with its verdicts when rows exist."""
    verdict = {r["mechanism"]: r for r in direct_facts()}
    md = [f"# Direct tests, {folder.name}\n\nForecast gain does not confirm a cause. A carried mechanism's plan tests the one claim that follows from its "
          "cause and from none of the others; a rival pair's plan is one statistic on one set of stored rows, for which the two rivals and the null state "
          "three disjoint ranges. Offline on stored files, with the refuting observation, threshold or ranges and the null fixed here. Run each with one subagent: "
          "spec committed first, offline only, then a row per mechanism in `studies/theory/results/direct_tested.json` (with `measured`, the 90 % "
          f"interval and n; refuted ones also in `refuted.json`). {VERDICT_RULE} Only mechanisms that hold one forecast the open targets; run the "
          "same round command again afterwards.\n"]
    for p in plans:
        if p.get("rivals"):
            r, state = p["ranges"], {i: (f"{v['verdict']} ({v['result']}: {v['measured']})" if (v := verdict.get(i)) else "not run yet") for i in p["rivals"]}
            md.append(f"\n## {p['pair']} ({p['kind']})\n\n" + "".join(f"- {i}: {flat(s)}\n" for i, s in p["statements"].items())
                      + f"\n- Claim: {p['claim']}\n- Statistic: {p['statistic']}\n- Files: {', '.join('`' + f + '`' for f in p['files'])}\n"
                      f"- Rows: {p['rows']} (n {p['n']})\n- Computation: {p['computation']}\n- Null: {p['null']}\n"
                      f"- Ranges fixed in advance: {p['rivals'][0]} {r['a']}, {p['rivals'][1]} {r['b']}, null {r['null']}; a value in neither rival's range refutes both\n"
                      + "".join(f"- Verdict {i}: {s}\n" for i, s in state.items()))
            continue
        v = verdict.get(p["mechanism"])
        head = f"\n## {p['mechanism']} ({p['kind']}{', ' + format(p['gain'], '+.2f') + ' nats on ' + str(p['items']) + ' results' if p.get('gain') is not None else ''})"
        state = f"{v['verdict']} ({v['result']}: {v['measured']})" if v else "not run yet"
        if p.get("decided_by"):
            b = p["decided_by"]
            md.append(f"{head}\n\n{flat(p['statement'])}\n\n- Claim: {p['claim']}\n- Already decided by {b['result']}: {b['number']} ({b['verdict']}). Verdict: {state}\n")
            continue
        md.append(f"{head}\n\n{flat(p['statement'])}\n\n- Claim: {p['claim']}\n- Files: {', '.join('`' + f + '`' for f in p['files'])}\n"
                  f"- Computation: {p['computation']}\n- Refuted if: {p['refuted_if']}\n- Threshold: {p['threshold']}\n"
                  + (f"- Null: {p['null']}\n" if p.get("null") else "") + f"- Verdict: {state}\n")
    (folder / "direct_tests.md").write_text("\n".join(md) + "\n")


def round11(folder, sources, n_top, wait_none=False):
    """The version-14 round: standing, direct facts (refuted.json and direct_tested.json), surprises, targets_open,
    direct-test plans for the top untested carried mechanisms, propose (two rival mechanisms per surprise and one shared
    direct test with disjoint ranges; a pair without a valid test is dropped), then a gate: the round stops until every
    planned mechanism has a row (or --go), and only mechanisms that hold one forecast the open targets (with the two
    readers); a holder with a forecast apart from both readers' intervals designs its pair's cell and route, the others
    are listed in holders.json as forecasting nothing new; experiments. A stage whose output exists is skipped."""
    start, out, pre = time.time(), folder / "jobs", prefix(folder)
    folder.mkdir(parents=True, exist_ok=True)
    print("== standing")
    if not (folder / "standing.json").exists():
        standing(folder, sources)
    st = json.loads((folder / "standing.json").read_text())
    carried = [{k: m[k] for k in MECHANISM_KEYS} for m in st["carried"]]
    print("== direct facts")
    facts_d = direct_facts()
    (folder / "direct_facts.json").write_text(json.dumps(facts_d, indent=1))
    print(f"  {len(facts_d)} direct facts ({sum(f['verdict'] == 'holds' for f in facts_d)} hold)")
    print("== surprises")
    found = surprises(folder, list({s.resolve(): s for s in sources}.values()))
    print("== targets_open")
    items = open_targets(folder) if not (folder / "targets.json").exists() else board("board", snapshot(folder))[0]  # a resumed round sees the board of its snapshot, not results posted since
    utc, tids = snapshot(folder), [t["id"] for t in json.loads((folder / "targets.json").read_text())["targets"]]
    common = {"DIRECTION.md": ROOT / "DIRECTION.md", "board.jsonl": "".join(json.dumps(i) + "\n" for i in items), "work.md": folder / "work.md"}
    print("== direct_tests (carried)")
    if not (folder / "direct_tests.json").exists():
        direct_tests(folder, items)
    print("== propose")
    top, new, pairs, drop, plans = found[:n_top], [], [], set(), json.loads((folder / "direct_tests.json").read_text())
    facts, board_ids = json.loads(newest("facts.json").read_text()), {i["id"] for i in items}
    dead = json.loads(newest("graveyard.json").read_text()) | json.loads((folder / "graveyard.json").read_text())
    if top:
        statements = {i: r["statement"] for i, r in st["records"].items()}
        engine.run([engine.job("surprise_propose", f"s{k}", {**common, "targets.json": folder / "targets.json", "facts.json": json.dumps(facts, indent=1),
                                                             "graveyard.json": json.dumps(dead, indent=1), "jobs.md": C.jobs_md(), "data.md": data_md(),
                                                             "direct_facts.json": json.dumps(facts_d, indent=1),
                                                             "surprise.json": json.dumps({x: e[x] for x in e if x != "forecasts"} | {"forecasts": e["forecasts"]}, indent=1),
                                                             "right.json": json.dumps([{"id": i, "statement": statements[i]} for i in e["inside"] if i in statements], indent=1),
                                                             "refuted.json": REFUTED},
                               {"rivals.json": out / f"rivals-s{k}.json"}, C.flags_once(lambda d, fl: check_rivals(d, tids, board_ids, len(facts), fl)))
                    for k, e in enumerate(top, 1)], folder, len(top))
        for k, e in enumerate(top, 1):
            j = json.loads((out / f"rivals-s{k}.json").read_text())
            lens = f"rival explanations of surprise {e['source']} {e['id']} ({e['item']}, measured {e['measured']:g})"
            test = j.get("test") or {}
            ms = [{"id": f"{folder.name}/s{k}-{m['id']}", "family": f"s{k}", "lens": lens,
                   **{x: m[x] for x in ("statement", "rests_on", "holds_against", "readers_wrong", "forecasts")}, "direct_test": test}
                  for m in j["rivals"]]
            gone = "; ".join(pair_test_errors(test))  # one shared test per pair; a pair without a valid one is dropped whole
            pairs.append({"family": f"s{k}", "surprise": {x: e[x] for x in ("source", "id", "item", "measured", "z", "what")}, "a": ms[0]["id"], "b": ms[1]["id"],
                          "apart": pair_apart(j["rivals"]), "cell": j.get("cell"), "test": test, "dropped_no_direct_test": gone or None})
            new += [] if gone else ms
        drop = judge_duplicates(folder, new, carried, dead) if new else set()  # reported only; a pair may restate older mechanisms
    plans = [p for p in plans if p["kind"] == "carried"] + [
        {"pair": f"{folder.name}/{p['family']}", "rivals": [p["a"], p["b"]], "kind": f"shared test of the rivals for surprise {p['family']}",
         "statements": {m["id"]: m["statement"] for m in new if m["family"] == p["family"]}, **p["test"]} for p in pairs if not p["dropped_no_direct_test"]]
    (folder / "direct_tests.json").write_text(json.dumps(plans, indent=1))
    (folder / "pairs.json").write_text(json.dumps(pairs, indent=1))
    tests_md(folder, plans)
    print("== gate: only mechanisms that hold a direct test go on")
    holds = {f["mechanism"] for f in direct_facts() if f["verdict"] == "holds"}
    pending = [i for p in plans for i in p.get("rivals") or [p["mechanism"]] if i not in {f["mechanism"] for f in direct_facts()}]
    if pending and not wait_none:
        print(f"  {len(pending)} mechanisms without a verdict yet ({', '.join(pending)}): run the tests from {folder / 'direct_tests.md'}, add their rows, then run "
              "the same command again (or add --go to continue with the mechanisms that hold now)")
        (folder / "run.json").write_text(json.dumps({"commit": sh("git", "rev-parse", "--short", "HEAD").strip(), "utc": utc, "version": 14, "state": "waiting for direct tests",
                                                     "pending": pending, "minutes": round((time.time() - start) / 60, 1)}, indent=1))
        return
    carried = [m for m in carried if m["id"] in holds]
    new = [m for m in new if m["id"] in holds]
    print("== forecast")
    forecasts = run_forecasters(folder, common, {m["id"]: json.dumps(m, indent=1) for m in carried}, out / "forecast", workers=16)
    forecasts |= {m["id"]: m["forecasts"] for m in new}
    mechs = carried + [{k: m[k] for k in (*MECHANISM_KEYS, "readers_wrong", "direct_test")} for m in new]
    (folder / "mechanisms.json").write_text(json.dumps({"mechanisms": mechs}, indent=1))
    (folder / "forecasts.json").write_text(json.dumps(forecasts, indent=1))
    write_md(folder, utc, forecasts, [f"\n- {m['id']} ({m['family']}{', carried' if m in carried else ''}): {flat(m['statement'])}" for m in mechs])
    print(f"  {len(carried)} carried and {len(new)} new mechanisms hold a direct test and forecast ({len(drop)} judged restatements), {len(pairs)} pairs")
    rd = [{f["id"]: f for f in forecasts[r]} for r in READERS]  # a holder forecasts something new: an interval apart from both readers' on an open target
    novel = {m["id"]: [f["id"] for f in forecasts[m["id"]] if all(C.apart(f, r[f["id"]]) for r in rd)] for m in mechs}
    nothing = [i for i, ts in novel.items() if not ts]
    (folder / "holders.json").write_text(json.dumps({"forecasts_new": {i: ts for i, ts in novel.items() if ts}, "nothing_new": nothing}, indent=1))
    print(f"  holds its test, forecasts nothing new (designs no cell): {', '.join(nothing) or 'none'}")
    print("== cells")
    counts = {}
    designers = {i for i, ts in novel.items() if ts}
    whole = [{**p, "holder": h, "other": p["b" if h == p["a"] else "a"], "side": "a" if h == p["a"] else "b"}
             for p in pairs for h in (p["a"], p["b"]) if h in designers]  # a rival that holds and forecasts something new designs the pair's cell
    if whole and not (folder / "cells.json").exists():
        known = {"targets": json.loads((folder / "targets.json").read_text())["targets"], "facts": facts}
        fams = {}
        for m in mechs:
            fams.setdefault(m["family"], {"lens": m["lens"], "mechanisms": []})["mechanisms"].append({k: m[k] for k in ("id", "statement", "rests_on")})
        props = [{"id": f"c{k:02d}", "family": p["family"], "mechanism": p["holder"], "against": p["other"], **{x: p["cell"][x] for x in ("cell", "job", "command", "readout", "unit", "why", "gpu_minutes")},
                  **{x: p["cell"][p["side"]][x] for x in ("value", "low", "high")}, "against_value": p["cell"]["b" if p["side"] == "a" else "a"]["value"],
                  "base_only": False, "best_base": None}
                 for k, p in enumerate((p for p in whole if p["cell"]), 1)]
        merged = [{"id": f"{pre}-m{p['id'][1:]}", "cell": p["cell"], "job": p["job"], "command": p["command"],
                   "readouts": [{"id": f"{pre}-m{p['id'][1:]}-r1", "readout": p["readout"], "unit": p["unit"], "from": [p["id"]]}]} for p in props]
        by_mid = {m["id"]: {k: m[k] for k in ("id", "statement", "rests_on")} for m in mechs}
        routes, dropped = route_jobs(folder, {p["family"]: {"lens": f"the rival pair about surprise {p['surprise']['source']} {p['surprise']['id']}",
                                                            "mechanisms": [by_mid[p["holder"]]]} for p in whole}, items, known)
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
                               "Plan `specs/SPEC_engine_v11.md`. ", left_out, {i: r for i, r in answered.items() if r["kind"] == "open"})
    if (folder / "cells.json").exists():
        print("== experiments")
        experiments(folder)
    (folder / "run.json").write_text(json.dumps({"commit": sh("git", "rev-parse", "--short", "HEAD").strip(), "command": " ".join(sys.argv), "utc": utc, "version": 14,
                                                 "from": [str(s) for s in sources], "carried": len(carried), "surprises": len(found), "pairs": len(pairs),
                                                 "new": len(new), "duplicates": len(drop), "targets": len(tids), **counts,
                                                 "minutes": round((time.time() - start) / 60, 1), "job_dirs": str(engine.tmp())}, indent=1))
    print(f"{(time.time() - start) / 60:.1f} minutes")


# ---- version 15 to 17: single accounts of every direct fact; version 17: explore and test halves ----

ACCOUNTS = 3
MARKS = ("explained", "not addressed", "contradicts")
TEST_KEYS = ("claim", "statistic", "rows", "computation", "null")
ADVERSARY_KINDS = ("covariate", "regression to the mean", "construction artifact", "other")
SPLIT_SETS = ("hard328", "math500", "fresh2026", "code", "dev100")  # data/split_v1.json
RANGE_WIDTH = 2.5  # version 17: a test range spans at most this many explore 90 % interval widths (times sqrt(n explore / n test))
FLAG_WORDS = ("deliberat", "opening")  # version 17: an opening classification needs the writer's own check on 20 explore rows
KINDS = ("weights", "rows")  # version 18: a consequence on the per-matrix weights tables or on stored sampling rows
MIN_WEIGHTS, MAX_ROWS = 2, 2  # version 18: per account, at least 2 weights consequences and at most 2 on sampling rows
MIN_N_WEIGHTS = 25  # version 18: test matrices a weights statistic needs before a verdict of holds (xlisten has 28 test writers)


def numbered_facts(folder):
    """Every direct fact once (a refuted.json row also in direct_tested.json kept once), numbered F01 ... in file order,
    frozen in folder/synthesis_facts.json so rows added during the round do not renumber them."""
    path = folder / "synthesis_facts.json"
    if not path.exists():
        seen, facts = set(), []
        for f in direct_facts():
            if (f["mechanism"], f["result"]) not in seen:
                seen.add((f["mechanism"], f["result"]))
                facts.append(f)
        path.write_text(json.dumps([{"id": f"F{k:02d}", **f} for k, f in enumerate(facts, 1)], indent=1, ensure_ascii=False))
    return json.loads(path.read_text())


def recent_md(items, hours=24):
    """Board results of the last `hours`: id, time, and the title: and what: lines (else the first 300 characters)."""
    cut = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - hours * 3600))
    rows = [i for i in items if i["kind"] == "result" and i["at"] >= cut]
    return f"# Board results of the last {hours} hours ({len(rows)})\n\n" + "\n".join(
        f"- {i['id']} ({i['at'][:16]}): " + " | ".join([x.strip() for x in i["text"].splitlines() if x.startswith(("title:", "what:"))] or [flat(i["text"])[:300]])
        for i in rows) + "\n"


def range_errors(r, keys):
    """ranges {key: [low, high]} for every key, each low <= high, and each key's range apart from the null's."""
    if not all(isinstance(r.get(k), list) and len(r[k]) == 2 and all(engine.number(x) for x in r[k]) and r[k][0] <= r[k][1] for k in (*keys, "null")):
        return [f"ranges needs {', '.join(repr(k) for k in (*keys, 'null'))}, each [low, high] with low <= high"]
    return [f"range {k} {r[k]} overlaps the null's {r['null']}; it must be disjoint from it" for k in keys
            if not (r[k][1] < r["null"][0] or r["null"][1] < r[k][0])]


def cells_errors(t):
    """Version 17: set is a split set and every cell is a stored cell of MANIFEST.md (rows.py) of that set whose rows are here."""
    cells, s = {m["cell"]: m for m in R.manifest()}, t.get("set")
    e = [] if s in SPLIT_SETS else [f"set: one of {', '.join(SPLIT_SETS)}"]
    e += [] if t.get("cells") else ["cells: one or more cell names of MANIFEST.md"]
    for c in t.get("cells") or []:
        m = cells.get(c)
        e += ([f"cell {c} is not a cell of MANIFEST.md"] if not m else [f"cell {c}: its rows sit in S3, not here"] if m["source"].startswith("s3")
              else [] if m["set"] == s or (s == "dev100" and m["set"] == "math500") else [f"cell {c} is a {m['set']} cell, not {s}"])
    return e


def tables_errors(t):
    """Version 18: a weights consequence names one or more tables of rows.WEIGHTS."""
    return [] if t.get("tables") and all(x in R.WEIGHTS for x in t["tables"]) else [f"tables: one or more of {', '.join(R.WEIGHTS)}"]


def stat_errors(t, keys):
    """A test on stored rows (TEST_KEYS fields, set and cells, n >= MIN_N test-half rows) or, version 18, on the weights
    tables (tables, n >= MIN_N_WEIGHTS test matrices); ranges."""
    e = [f"missing {k}" for k in TEST_KEYS if not str(t.get(k, "")).strip()]
    if t.get("kind") == "weights":
        e += tables_errors(t)
        e += [] if engine.number(t.get("n")) and t["n"] >= MIN_N_WEIGHTS else [f"n: TEST matrices the statistic is computed on, at least {MIN_N_WEIGHTS}"]
    else:
        e += cells_errors(t)
        e += [] if engine.number(t.get("n")) and t["n"] >= MIN_N else [f"n: rows of the TEST half the statistic is computed on, at least {MIN_N}"]
    return e + range_errors(t.get("ranges") or {}, keys)


def explore_errors(c):
    """Version 17: the consequence's value measured on the explore half (value inside its 90 % interval, n), inside the
    account's test range, whose width is at most RANGE_WIDTH explore interval widths times sqrt(n explore / n test)."""
    x, r = c.get("explore") or {}, (c.get("ranges") or {}).get("account")
    if not (all(engine.number(x.get(k)) for k in ("value", "n")) and isinstance(x.get("interval"), list) and len(x["interval"]) == 2
            and all(engine.number(v) for v in x["interval"]) and x["interval"][0] <= x["value"] <= x["interval"][1] and x["n"] >= 1):
        return ["explore: {value, interval: [low, high] (90 % bootstrap, low <= value <= high), n} measured on the explore rows"]
    if not (isinstance(r, list) and len(r) == 2 and all(engine.number(v) for v in r)):
        return []  # range_errors names it
    lo, hi = x["interval"]
    w = RANGE_WIDTH * (hi - lo) * (x["n"] / c["n"]) ** 0.5 if engine.number(c.get("n")) and c["n"] > 0 else 0
    e = [] if r[0] <= x["value"] <= r[1] else [f"the account range {r} must contain the explore value {x['value']}"]
    return e + ([] if r[1] - r[0] <= w + 1e-12 else [f"the account range {r} is wider ({r[1] - r[0]:.4g}) than {RANGE_WIDTH} explore interval widths "
                                                     f"x sqrt(n explore / n test) = {w:.4g}; narrow it around the explore value"])


def flag_errors(c):
    """Version 17: a statistic that classifies openings (deliberative or not) needs the writer's check of its rule on 20 explore rows."""
    text = " ".join(str(c.get(k, "")) for k in ("statistic", "rows", "computation")).lower()
    return (["validation: this statistic classifies openings; read 20 explore rows' openings and report how many the rule classifies right"]
            if any(w in text for w in FLAG_WORDS) and not str(c.get("validation", "")).strip() else [])


def marks_errors(j, fact_ids):
    """A mark for every fact (explained, not addressed, contradicts), a contradiction with its why."""
    marks = {m.get("fact"): m for m in j.get("marks") or []}
    e = [f"marks: no mark for {f}" for f in fact_ids if f not in marks]
    e += [f"marks: {f}: fact must be a fact id and mark one of {', '.join(MARKS)}" for f, m in marks.items() if f not in fact_ids or m.get("mark") not in MARKS]
    return e + [f"marks: {f}: a contradiction needs why (what in the account the fact contradicts)" for f, m in marks.items()
                if m.get("mark") == "contradicts" and not str(m.get("why", "")).strip()]


def same_rows(a, b):
    """One measurement (version 16): two tests on the same set of stored cells (version 18: of weights tables) count as
    the same rows."""
    return a["kind"] == b["kind"] and sorted(a.get("cells") or a.get("tables")) == sorted(b.get("cells") or b.get("tables"))


def weights_cell_errors(c):
    """Version 18: one weights-only computation in no committed table, with the account's predicted value and 90 % interval."""
    e = [f"weights_cell misses {k}" for k in ("statistic", "models", "matrices", "computation", "why") if not str(c.get(k, "")).strip()]
    return e + ([] if all(engine.number(c.get(k)) for k in ("value", "low", "high")) and c["low"] <= c["value"] <= c["high"] and c["low"] < c["high"]
                else ["weights_cell: value, low, high (90 %) with low <= value <= high and low < high"])


def account_errors(j, fact_ids):
    """An account-<k>.json: at most 6 sentences, a mark for every fact (a contradiction named), the 3 worst facts, three
    new consequences each a test on stored cells with its explore value, its test range (explore_errors) apart from the
    null's, no two on the same cells (version 16: one measurement, one credit)."""
    s, e = j.get("account"), []
    e += [] if isinstance(s, list) and 1 <= len(s) <= 6 and all(isinstance(x, str) and x.strip() for x in s) else ["account: a list of 1 to 6 sentences"]
    e += marks_errors(j, fact_ids)
    w = j.get("worst") or []
    e += [] if len(set(w)) == 3 and set(w) <= set(fact_ids) else ["worst: 3 distinct fact ids"]
    cs = j.get("consequences") or []
    kinds = [c.get("kind") for c in cs]
    e += [] if [c.get("id") for c in cs] == [f"c{k}" for k in range(1, len(cs) + 1)] and set(kinds) <= set(KINDS) else ["consequences: ids c1, c2, ... in order, each with kind weights or rows"]
    e += [] if kinds.count("weights") >= MIN_WEIGHTS and kinds.count("rows") <= MAX_ROWS else [
        f"consequences: at least {MIN_WEIGHTS} of kind weights and at most {MAX_ROWS} of kind rows (has {kinds.count('weights')} and {kinds.count('rows')})"]
    e += [f"{c.get('id')}: {x}" for c in cs for x in stat_errors(c, ["account"]) + explore_errors(c) + flag_errors(c)
          + ([] if str(c.get("why_new", "")).strip() else ["missing why_new"])]
    e += weights_cell_errors(j.get("weights_cell") or {})
    if e:
        return e
    return [f"{a['id']} and {b['id']} use the same {'tables' if a['kind'] == 'weights' else 'cells'} {sorted(a.get('cells') or a.get('tables'))}: "
            "one measurement earns one credit; use another set" for i, a in enumerate(cs) for b in cs[i + 1:] if same_rows(a, b)]


def adversary_errors(j, board_ids):
    """adversary.json (version 17): the strongest alternative that predicts the claimed range without the account, how
    to compute its value from stored cells, its value measured on the explore half, and a board result that already
    shows the number, if any."""
    e = [f"missing {k}" for k in ("alternative", "computation") if not str(j.get(k, "")).strip()]
    e += [] if j.get("kind") in ADVERSARY_KINDS else [f"kind: one of {', '.join(ADVERSARY_KINDS)}"]
    cells = {m["cell"]: m for m in R.manifest()}
    if "tables" in j:  # version 18: an adversary of a weights consequence computes from the weights tables
        e += tables_errors(j)
    else:
        e += [] if j.get("cells") else ["cells: the stored cells (MANIFEST.md names) the alternative's value is computed from"]
        e += [f"cell {c} is not a cell of MANIFEST.md, or its rows are not here" for c in j.get("cells") or [] if c not in cells or cells[c]["source"].startswith("s3")]
    e += [] if engine.number(j.get("explore_value")) else ["explore_value: the alternative's value computed on the explore rows here (one number)"]
    s = j.get("already_shown")
    return e + ([] if s is None or (s.get("result") in board_ids and str(s.get("number", "")).strip())
                else ["already_shown: null, or {result: a board result id, number: the number it shows}"])


def verdict16(row):
    """Version 16 (and 17, on the test half): holds only if the 90 % interval lies wholly inside the range, n >= MIN_N and
    the interval excludes the adversary's value; inside the range with the adversary's value in the interval: not
    separated; wholly outside: refuted; else undecided."""
    (lo, hi), (a, b), adv = row["interval"], row["range"], row["adversary"]
    assert lo <= hi and a <= b and engine.number(adv) and engine.number(row["n"]), row
    if hi < a or b < lo:
        return "refuted"
    if row["n"] < (MIN_N_WEIGHTS if row.get("kind") == "weights" else MIN_N) or not (a <= lo and hi <= b):
        return "undecided"
    return "not separated" if lo <= adv <= hi else "holds"


def first_check(check):
    """valid(d) for engine.run: the first check returns check's errors (sent back once); the second only parses the file,
    so an account still failing is dropped by the caller, not the round."""
    calls = []

    def valid(d):
        calls.append(d)
        if len(calls) == 1:
            return check(d)
        json.loads((d / "account.json").read_text())  # the send-back must still parse
        return None
    return valid


def test_md(t, keys):
    where = (f"- Kind: weights; tables: {', '.join('`' + c + '`' for c in t['tables'])} (test matrices: `rows.weights(table, \"test\")`)\n"
             f"- Matrices: {t['rows']} (n {t['n']} test matrices)\n" if t.get("kind") == "weights" else
             f"- Kind: rows; set: {t['set']}; cells: {', '.join('`' + c + '`' for c in t['cells'])}\n- Rows: {t['rows']} (n {t['n']} on the test half)\n")
    return (f"- Claim: {t['claim']}\n- Statistic: {t['statistic']}\n" + where + f"- Computation: {t['computation']}\n- Null: {t['null']}\n"
            f"- Explore half (the account's own measurement): {t['explore']['value']} [{t['explore']['interval'][0]}, {t['explore']['interval'][1]}], n {t['explore']['n']}\n"
            "- Ranges fixed for the test half: " + ", ".join(f"{k} {t['ranges'][k]}" for k in (*keys, "null")) + "\n")


def explore_dropped(c, adv):
    """Version 17: account and adversary do not differ on the explore half when the adversary's explore value lies inside
    the account's explore 90 % interval; version 18: or inside the account's range. Such a consequence gets no test."""
    (lo, hi), (a, b), v = c["explore"]["interval"], c["ranges"]["account"], adv["explore_value"]
    if lo <= v <= hi:
        return f"adversary's explore value {v:.4g} lies inside the account's explore interval [{lo:.4g}, {hi:.4g}]"
    return f"adversary's explore value {v:.4g} lies inside the account's range [{a:.4g}, {b:.4g}]" if a <= v <= b else None


def weights_cell_adversary_errors(j):
    """Version 18: the blind adversary's prediction of an account's weights cell: alternative, value inside its 90 %
    interval (low < high), and a committed table that already holds the number, if any."""
    e = [f"missing {k}" for k in ("alternative", "reason") if not str(j.get(k, "")).strip()]
    e += [] if all(engine.number(j.get(k)) for k in ("value", "low", "high")) and j["low"] <= j["value"] <= j["high"] and j["low"] < j["high"] else [
        "value, low, high (90 %) with low <= value <= high and low < high"]
    s = j.get("already_in_table")
    return e + ([] if s is None or (str(s.get("table", "")).strip() and str(s.get("number", "")).strip())
                else ["already_in_table: null, or {table: a table of MANIFEST.md, number: the number it holds}"])


def gap_widths(a, b):
    """Version 18: the gap between two predictions in interval widths: |value a - value b| / the wider 90 % interval."""
    return abs(a["value"] - b["value"]) / max(a["high"] - a["low"], b["high"] - b["low"])


def synthesis(folder, sources):
    """forecast.py synthesis (version 17): standing (when --from is given), direct facts, the explore half of every
    stored cell copied once into a job directory (rows.py, data/split_v1.json); three accounts written in parallel,
    each starting from a different third of the facts, each a headless job with Bash in a directory holding the
    explore rows only: it measures each consequence on the explore half and fixes its range for the test half
    (explore_errors); checks with one send-back (an account still failing is dropped; a failing cell alone is dropped
    alone); then, in parallel, one blind marker per account and one adversary per consequence (also with the explore
    rows: it computes its alternative's explore value; a board result it names as already showing the number rejects
    the consequence); a consequence whose adversary's explore value lies inside the account's explore interval is
    dropped; the test plans (synthesis_tests.md, test half only); a gate until every plan has rows (forecast.py add-rows
    recomputes each verdict with verdict16); then synthesis.md. A stage whose output exists is skipped."""
    start, out, stages = time.time(), folder / "jobs", {}
    folder.mkdir(parents=True, exist_ok=True)
    if sources and not (folder / "standing.json").exists():
        print("== standing")
        standing(folder, sources)
        stages["standing"] = round((time.time() - start) / 60, 1)
    print("== direct facts")
    (folder / "direct_facts.json").write_text(json.dumps(direct_facts(), indent=1))
    facts = numbered_facts(folder)
    ids, facts_text = [f["id"] for f in facts], json.dumps(facts, indent=1, ensure_ascii=False)
    print(f"  {len(facts)} direct facts ({sum(f['verdict'] == 'holds' for f in facts)} hold)")
    items = board("board", "9999")[0]
    board_ids = {i["id"] for i in items}
    explore = engine.tmp() / "explore_rows"
    if not explore.exists():
        print("== explore half of the stored rows")
        R.copy(explore, "explore")
    (folder / "explore_manifest.md").write_text((explore / "MANIFEST.md").read_text())
    common = {"DIRECTION.md": ROOT / "DIRECTION.md", "results.md": recent_md(items), "data.md": data_md(), "jobs.md": C.jobs_md(), "rows": explore}
    t0, thirds = time.time(), [facts[k * len(facts) // ACCOUNTS:(k + 1) * len(facts) // ACCOUNTS] for k in range(ACCOUNTS)]

    def check(d):
        j = json.loads((d / "account.json").read_text())
        return "; ".join(account_errors(j, ids)) or None
    print(f"== synthesis: {ACCOUNTS} accounts in parallel")
    engine.run([engine.job("synthesis", f"account-{k}", {**common, "facts.json": json.dumps(thirds[k - 1] + [f for f in facts if f not in thirds[k - 1]], indent=1, ensure_ascii=False)},
                           {"account.json": out / f"account-{k}.json"}, first_check(check), mode="rows",
                           start=f"{thirds[k - 1][0]['id']} to {thirds[k - 1][-1]['id']}", range_width=RANGE_WIDTH, min_n_weights=MIN_N_WEIGHTS)
                for k in range(1, ACCOUNTS + 1)], folder, ACCOUNTS)
    accounts, dropped = {}, []
    for k in range(1, ACCOUNTS + 1):
        name = f"account-{k}"
        j = json.loads((out / f"{name}.json").read_text())
        if e := account_errors(j, ids):
            dropped.append({"account": name, "reason": "; ".join(e)})
            continue
        accounts[name] = j
        (folder / f"{name}.json").write_text(json.dumps(j, indent=1, ensure_ascii=False))
    stages["accounts"] = round((time.time() - t0) / 60, 1)
    for x in dropped:
        print(f"  dropped {'the cell of ' if x.get('cell_only') else ''}{x['account']}: {x['reason']}")
    print("== blind markers and adversaries")
    t0 = time.time()
    jobs = [engine.job("synthesis_marks", n, {"account.json": json.dumps({"account": a["account"]}, indent=1, ensure_ascii=False), "facts.json": facts_text},
                       {"marks.json": folder / f"marks-{n}.json"}, lambda d: "; ".join(marks_errors(json.loads((d / "marks.json").read_text()), ids)) or None)
            for n, a in accounts.items()]
    shown = {"facts.json": facts_text, "data.md": common["data.md"], "results.md": common["results.md"], "all_results.md": results_md(items), "rows": explore}
    jobs += [engine.job("synthesis_adversary" + ("_weights" if c["kind"] == "weights" else ""), f"{n}-{c['id']}",
                        {**shown, "consequence.json": json.dumps({**{x: c[x] for x in ("statistic", "tables" if c["kind"] == "weights" else "set",
                                                                                        "tables" if c["kind"] == "weights" else "cells", "rows", "n", "computation")},
                                                                  "range": c["ranges"]["account"]}, indent=1, ensure_ascii=False)},
                        {"adversary.json": folder / "adversary" / f"{n}-{c['id']}.json"},
                        lambda d: "; ".join(adversary_errors(json.loads((d / "adversary.json").read_text()), board_ids)) or None, mode="rows")
             for n, a in accounts.items() for c in a["consequences"]]
    jobs += [engine.job("synthesis_cell_adversary", n, {**shown, "cell.json": json.dumps({x: a["weights_cell"][x] for x in ("statistic", "models", "matrices", "computation")},
                                                                                         indent=1, ensure_ascii=False)},
                        {"prediction.json": folder / "adversary" / f"{n}-weights_cell.json"},
                        lambda d: "; ".join(weights_cell_adversary_errors(json.loads((d / "prediction.json").read_text()))) or None, mode="rows")
             for n, a in accounts.items()]
    engine.run(jobs, folder, len(jobs))
    stages["markers and adversaries"] = round((time.time() - t0) / 60, 1)
    plans = []
    for n, a in accounts.items():
        for c in a["consequences"]:
            key = f"{n}/{c['id']}"
            adv = json.loads((folder / "adversary" / f"{n}-{c['id']}.json").read_text())
            p = {"name": f"{folder.name}/{key}", "owner": n, "why_new": c["why_new"], "kind": c["kind"],
                 **{x: c[x] for x in (*TEST_KEYS, "n", "explore", *(("tables",) if c["kind"] == "weights" else ("set", "cells")))},
                 "validation": c.get("validation"), "ranges": {n: c["ranges"]["account"], "null": c["ranges"]["null"]},
                 "mechanisms": {n: f"{folder.name}/{key}"}, "adversary": adv}
            if adv.get("already_shown"):  # version 16: a number a board result already shows earns no credit
                p["rejected"], p["mechanisms"] = f"{adv['already_shown']['result']} already shows it: {adv['already_shown']['number']}", {}
            elif why := explore_dropped(c, adv):  # version 17: no difference on the explore half, no test
                p["dropped"], p["mechanisms"] = why, {}
            plans.append(p)
    (folder / "synthesis_tests.json").write_text(json.dumps(plans, indent=1, ensure_ascii=False))
    weights_cells(folder, accounts)
    rows = {r["mechanism"]: r for r in json.loads(TESTED.read_text())}
    md = [f"# Synthesis tests, {folder.name} (version 17)\n\nRun each test that is neither rejected nor dropped with one subagent: spec committed "
          "first, offline, on the TEST half only: load every cell with `rows.load(set, cell, \"test\")` and every weights table with "
          "`rows.weights(table, \"test\")` (`studies/theory/lib/rows.py`; never "
          "the explore half, never the raw files), script under `studies/theory/analysis/`, outputs under `studies/theory/results/direct/<name>-01/`. "
          "Compute the adversary's value FIRST, from the adversary's computation on the test half; then the statistic, its n and 90 % bootstrap "
          "interval (resampling problems; for kind weights, resampling test matrices); then one row per mechanism named here, with `interval`, `range`, "
          "`adversary` (the test-half value), `n` and `kind`, through `forecast.py add-rows`, which recomputes the verdict: holds only if the interval "
          f"lies wholly inside the range, n >= 50 (kind weights: n >= {MIN_N_WEIGHTS} test matrices) "
          "and the interval excludes the adversary's value; inside the range but containing it: `not separated`; wholly outside: refuted; else "
          "undecided. Read no other test's output of this round.\n"]
    for p in plans:
        md.append(f"\n## {p['name']}" + (" (rejected)" if p.get("rejected") else " (dropped on the explore half)" if p.get("dropped") else "") + "\n\n"
                  + (f"- Rejected (one measurement, one credit): {p['rejected']}\n" if p.get("rejected") else "")
                  + (f"- Dropped: {p['dropped']}\n" if p.get("dropped") else "")
                  + f"- Why no fact covers it: {p['why_new']}\n" + test_md(p, [p["owner"]])
                  + (f"- Opening-rule check on 20 explore rows: {p['validation']}\n" if p.get("validation") else "")
                  + f"- Adversary ({p['adversary']['kind']}): {p['adversary']['alternative']}\n- Adversary's value on the explore half: {p['adversary']['explore_value']}\n"
                  f"- Adversary's value, computed first on the test half: {p['adversary']['computation']} ("
                  + (f"tables: {', '.join('`' + c + '`' for c in p['adversary']['tables'])}" if "tables" in p["adversary"] else f"cells: {', '.join('`' + c + '`' for c in p['adversary']['cells'])}") + ")\n"
                  + "".join(f"- Mechanism {m}: " + (f"{rows[m]['verdict']} ({rows[m]['result']}: {rows[m]['measured']})" if m in rows else "not run yet") + "\n"
                            for m in p["mechanisms"].values()))
    (folder / "synthesis_tests.md").write_text("\n".join(md) + "\n")
    pending = [m for p in plans for m in p["mechanisms"].values() if m not in rows]
    info = {"commit": sh("git", "rev-parse", "--short", "HEAD").strip(), "command": " ".join(sys.argv), "utc": now(), "version": 18, "facts": len(facts),
            "accounts": list(accounts), "dropped": dropped, "plans": len(plans), "rejected": sum("rejected" in p for p in plans),
            "dropped_on_explore": sum("dropped" in p for p in plans), "job_dirs": str(engine.tmp())}
    prior = json.loads((folder / "run.json").read_text()).get("minutes_per_stage", {}) if (folder / "run.json").exists() else {}
    info["minutes_per_stage"] = {**prior, **{k: v for k, v in stages.items() if v >= 0.1 or k not in prior}}
    if pending:
        print(f"  gate: {len(pending)} mechanisms without a row ({', '.join(pending)}): run the tests from {folder / 'synthesis_tests.md'}, add rows, rerun")
        (folder / "run.json").write_text(json.dumps({**info, "state": "waiting for synthesis tests", "pending": pending}, indent=1))
        return
    print("== synthesis.md")
    verdicts, score, names = ("holds", "not separated", "refuted", "undecided"), {}, list(accounts)
    for n, a in accounts.items():
        mk = [x["mark"] for x in json.loads((folder / f"marks-{n}.json").read_text())["marks"]]
        own = [rows[p["mechanisms"][n]]["verdict"] for p in plans if p["owner"] == n and n in p["mechanisms"]]
        score[n] = {"explained": mk.count("explained"), "not addressed": mk.count("not addressed"), "contradicts": mk.count("contradicts"),
                    "self-marked contradicts": [x["mark"] for x in a["marks"]].count("contradicts"), **{f"new {v}": own.count(v) for v in verdicts},
                    "new rejected": sum(p["owner"] == n and "rejected" in p for p in plans), "dropped on explore": sum(p["owner"] == n and "dropped" in p for p in plans),
                    "score": own.count("holds") - mk.count("contradicts")}
    ranked = sorted(score, key=lambda n: (-score[n]["score"], score[n]["contradicts"], score[n]["new refuted"]))
    cols = list(score[ranked[0]]) if ranked else []
    md = [f"# Synthesis, {folder.name} (version 18)\n\nWritten {now()} UTC. {len(facts)} direct facts; {len(names)} accounts kept of {ACCOUNTS}"
          f"{' (dropped: ' + ', '.join(x['account'] for x in dropped if not x.get('cell_only')) + ')' if any(not x.get('cell_only') for x in dropped) else ''}. "
          "Score = consequences that hold on the test half against the adversary's test-half value minus facts the blind marker marks as "
          "contradicting the account. Fact marks are the blind marker's (`marks-<account>.json`); the account's own count is shown beside them.\n",
          "| account | " + " | ".join(cols) + " |\n|---|" + "---|" * len(cols)]
    md += [f"| {n} | " + " | ".join(str(score[n][c]) for c in cols) + " |" for n in ranked]
    for n in ranked:
        a, marks = accounts[n], json.loads((folder / f"marks-{n}.json").read_text())["marks"]
        md.append(f"\n## {n}\n\n" + " ".join(a["account"]) + "\n\nContradicts (blind marker): "
                  + ("; ".join(f"{x['fact']} ({x['why']})" for x in marks if x["mark"] == "contradicts") or "none")
                  + "\n\nContradicts (own marks): " + ("; ".join(f"{x['fact']} ({x['why']})" for x in a["marks"] if x["mark"] == "contradicts") or "none")
                  + f"\n\nExplains worst: {', '.join(a['worst'])}\n")
        for p in plans:
            if p["owner"] == n:
                r = rows.get(p["mechanisms"].get(n))
                md.append(f"- {p['name']}: {p['statistic']}; explore {p['explore']['value']} {p['explore']['interval']}; range {p['ranges'][n]}; "
                          f"adversary explore {p['adversary']['explore_value']:.4g}; "
                          + (f"rejected: {p['rejected']}" if p.get("rejected") else f"dropped: {p['dropped']}" if p.get("dropped")
                             else f"test {r['measured']}; adversary's test value {r['adversary']:.4g}; {r['verdict']} ({r['result']})"))
        c = a["weights_cell"]
        md.append(f"- Weights cell (weights_cells.md): {c['statistic']} ({c['models']}; {c['matrices']}): predicted {c['value']} [{c['low']}, {c['high']}]")
    (folder / "synthesis.md").write_text("\n".join(md) + "\n")
    (folder / "run.json").write_text(json.dumps({**info, "state": "done", "score": score}, indent=1))
    print("\n".join(md[:2 + len(names)]))


def weights_cells(folder, accounts):
    """Version 18: weights_cells.md, each account's weights-only computation with its prediction and the blind
    adversary's, ranked by the gap between them in interval widths (gap_widths). None is run by the engine."""
    cells = []
    for n, a in accounts.items():
        c, adv = a["weights_cell"], json.loads((folder / "adversary" / f"{n}-weights_cell.json").read_text())
        cells.append({"account": n, **c, "adversary": adv, "gap_widths": round(gap_widths(c, adv), 3)})
    cells.sort(key=lambda c: -c["gap_widths"])
    (folder / "weights_cells.json").write_text(json.dumps(cells, indent=1, ensure_ascii=False))
    md = [f"# Weights cells, {folder.name} (version 18)\n\nOne weights-only computation per account, in no committed table: the account's "
          "prediction and a blind adversary's (it sees the computation, not the account), ranked by the gap between the two values in "
          "widths of the wider 90 % interval. The engine runs none of them.\n"]
    for k, c in enumerate(cells, 1):
        adv = c["adversary"]
        md.append(f"\n## {k}. {c['account']}: gap {c['gap_widths']} interval widths\n\n- Statistic: {c['statistic']}\n- Models: {c['models']}\n"
                  f"- Matrices: {c['matrices']}\n- Computation: {c['computation']}\n- Account predicts {c['value']} [{c['low']}, {c['high']}]: {c['why']}\n"
                  f"- Adversary predicts {adv['value']} [{adv['low']}, {adv['high']}]: {adv['alternative']} ({adv['reason']})\n"
                  + (f"- Already in a table: {adv['already_in_table']['table']}: {adv['already_in_table']['number']}\n" if adv.get("already_in_table") else ""))
    (folder / "weights_cells.md").write_text("\n".join(md) + "\n")


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
    items = open_targets(folder) if not (folder / "targets.json").exists() else board("board", snapshot(folder))[0]  # a resumed round sees the board of its snapshot, not results posted since
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
    parser.add_argument("command", choices=["round", "make", "score", "cells", "add-rows", "synthesis"])
    parser.add_argument("folder", type=Path, help="add-rows: a direct test's rows.json")
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
    parser.add_argument("--go", action="store_true", help="round: continue past the direct-test gate with the mechanisms that hold a test now")
    a = parser.parse_args()
    engine.args.model_all = a.model_all
    {"round": lambda: wide_round_v10(a.folder, a.runs, a.propose or 6) if a.propose_wide else round11(a.folder, a.runs, a.surprises, a.go), "make": lambda: make(a.folder, a.propose, a.lens),
     "score": lambda: score(a.folder, a.rescore), "cells": lambda: cells_run(a.folder, a.runs),
     "add-rows": lambda: add_rows(a.folder), "synthesis": lambda: synthesis(a.folder, a.runs)}[a.command]()
