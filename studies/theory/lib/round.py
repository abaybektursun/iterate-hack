# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""A theory round (.claude/skills/theory/SKILL.md): every model call is a headless Claude run, every check and score is
code here.

  uv run studies/theory/lib/round.py <round dir> <stage> [<stage> ...] [options]

Version 9: the default round is `forecast.py round` (the wide round); this script is its --deep tool:
`round.py <round dir> all --cutoff <T> --from <previous engine round> --deep <wide round dir>` takes the wide round's
carried mechanisms (total forecast gain above 0 on 3 or more numbers) as mechanisms.json and runs every other stage.
Every log gain against a measured value is at most 0 when the value lies outside the prediction's own interval.
Version 8 (default --version): version 7 plus three steps. targets_open (after standing; forecast.py's open_targets) writes
targets.json and work.md: the numbers the open work items will report. mechanisms and develop see the targets; each
mechanism names 3 or more (a third of them) it gives a number for, each new theory carries "forecasts" for them.
forecast (after develop and account) writes forecasts.json and forecasts.md: two readers and every carried theory
forecast blind. The next round's standing scores them (forecast_scores.json): 3 or more scored targets with a total
at or below -2 nats refute; a review says "stands" only with a total above 0 on 3 or more.
Version 7. `all` runs, in order:
  split --cutoff <ISO time> [--skip <word> ...]   check.dump: before.jsonl, after.jsonl
  standing --from <previous round dir>            graveyard.json (every theory of every earlier round in that engine
                                                  folder), theories/ (survivors carried with their scored tests,
                                                  untested theories once, <theory>-rival for each rival that beat its
                                                  theory, with its duel tests as its record), prior_reviews/,
                                                  facts.json (the previous round's computed numbers),
                                                  incumbent_account.json (its account, shares and duel),
                                                  gpu_tests.json (experiments of the previous round measured since, from
                                                  its experiments_measured.json, scored for both sides; two strikes send
                                                  a side to the graveyard)
  inventory      (opus, repository)               inventory.md: stored per-problem row files, fetch command, readable now
  external       (opus, papers.py only)           external.md: published mechanisms and their numbers
  mechanisms [--n-mechanisms 12]   (opus)         mechanisms.json: pairwise different candidate mechanisms
  develop        (opus, one per mechanism)        drafts/, theories/r<N>-m<id>.json, dropped.json (abandoned or failing
                                                  the check twice), theories.sha256
  account        (opus, one job; only with        theories/r<N>-account.json: one budget of the base-to-RL gap, 3-6
                  --with-account)                 parts with ordered rules on stored rows, a share per part and for
                                                  unassigned, 2+ cross-predictions; tested and duelled like a theory.
                                                  Without --with-account no account, new or carried, is tested,
                                                  duelled, replicated or reviewed
  null_tests     (opus, 2 jobs)                   tests_blind.jsonl, predictions/nulltest-1.jsonl, nulltest-2.jsonl
  test           (opus, repository, laptop only)  tests/<theory>/p<k>.py written by the model, run here once:
                                                  tests/<theory>.json
  score_tests    (no model)                       metrics_v4.json and the printed table
  heldout                                         targets, null, claims (survivors only), score_tests: strikes
  rival          (opus, one per survivor)         rivals/<theory>.json: the strongest rival mechanism, 2-4 tests on
                                                  which the two differ, the rival's predictions (top 3 survivors)
  defend         (opus, one per survivor)         rivals/<theory>.defend.json: predictions from the theory alone
  rival2         (opus, where needed)             the rival's second turn where fewer than 2 tests put the defender's
                                                  centre outside the rival's interval: rivals/<theory>.turn2.json
  defend         (opus)                           rivals/<theory>.turn2.defend.json for the second turn's tests
  duel_test      (opus, repository, laptop only)  rivals/<theory>[.turn2]/p<k>.py, run here once: .tests.json
  score_duel     (no model)                       metrics_v5.json: theory against rival over both turns (+-2 nats
                                                  over 2+ separating tests decides; a same test adds 0), and the table
  cross_predict  (opus, two per pair)             experiments/<theory>.json: each side of every pair (theory and rival,
                                                  whatever the duel state) predicts the other side's GPU predictions and
                                                  intervention, blind; a side with no intervention writes one
  review         (opus, repository)               reviews/<theory>.json for the same survivors; names the duel state
  experiments    (no model)                       experiments.json, experiments.md: open experiments ranked by
                                                  separation per GPU minute, interventions by gain over the best known
                                                  base count
develop, account, rival and rival2 also write an "intervention" (prompts/intervention.md): one change to the untrained
base, its cell, its predicted count and the best known base count.

--only-account: no mechanisms or develop; only the account is tested and duelled, carried theories are its inputs
(implies --with-account).
Version 6 (`--version 6`): without interventions, cross_predict and experiments.
Version 5 (`--version 5`): the same without account. Version 4: also without rival, defend, rival2, duel_test and
score_duel. Stages given by name run in the
given order on an existing round folder, for example `round.py <round dir> rival defend rival2 defend duel_test score_duel`.
Version 3 (`--version 3`; `all` runs split, standing, inventory, targets, external, generate, null, claims, score,
reverse, test, score, review): generate [--starts ...], score (metrics_v3.json), reverse. Every stage is callable alone.

Every model call except inventory, test, duel_test and review runs in an empty job directory outside the repository with only
the Read and Write tools, so no git status, project instructions, memory or board reaches it. A job whose outputs
exist is skipped, so a stopped round resumes. A job whose output fails its check is sent back once with the error.
Repository jobs and test scripts run with AWS_PROFILE=iterate-ecr; test scripts run under TEST_PYTHON.
--model-all <model> overrides every stage's model and --min-targets <n> (default 15) the fewest targets a round
accepts: both for smoke tests.
"""
import argparse
import hashlib
import json
import math
import os
import random
import re
import shutil
import string
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

LIB = Path(__file__).resolve().parent
ROOT = LIB.parents[2]
sys.path.insert(0, str(LIB))
import check  # noqa: E402
from check import read, write  # noqa: E402

sys.modules.setdefault("round", sys.modules[__name__])  # forecast.py, imported below, uses this module as round

AWS_PROFILE = "iterate-ecr"  # reads s3://pg-lineage-769063704696/results/rlneurons/ on the owner's machine
# Test scripts run with the team's grader packages (studies/rlneurons/README.md: math-verify 0.9.0 and numpy) and the
# antlr4 runtime sympy's LaTeX parser needs (it accepts only 4.11), from the repository root with the root on PYTHONPATH,
# so `from studies.rlneurons.lib import rln4_lib` works.
TEST_PACKAGES = ["numpy", "math-verify==0.9.0", "antlr4-python3-runtime==4.11"]
TEST_PYTHON = ["uv", "run", "--no-project", *(a for p in TEST_PACKAGES for a in ("--with", p)), "python"]
MODELS = {"inventory": "opus", "targets": "sonnet", "external": "opus", "generate": "opus", "fix": "opus",
          "null": "opus", "claims": "opus", "reverse": "sonnet", "test": "opus", "review": "opus",
          "mechanisms": "opus", "develop": "opus", "null_tests": "opus", "rival": "opus", "defend": "opus",
          "account": "opus", "cross_predict": "opus"}
STARTS = {
    "all": "the items and the findings as a whole.",
    "surprises": "build only from hypotheses the items report as refuted, predictions that failed, and controls that "
                 "did as well as the treatment. Each theory explains at least two of these.",
    "across": "each theory connects two studies whose items do not cite each other (for example a sampling result and "
              "a weight-difference result).",
    "external": "start from the findings in external.md. Prefer combining two published mechanisms into one that "
                "neither paper states, then test it against the items.",
    "revise": "start from the standing theories' weakest points: their losing claims in prior_scores.json (claims whose "
              "measured value fell outside the interval, or whose gain is negative) and their reviews in "
              "prior_reviews/. Write a better revision of one standing theory, or a merger of two, that implies at "
              "least one number its parent gets differently. Set \"parent\".",
}
FREE_RULE = ("Go through every target. Claim a target only where the mechanism as written implies something specific "
             "about it. Do not claim a target merely because it can be guessed from the earlier items: the readers "
             "with no theory guess those too, and a claim gains only where the theory moves the number. Leaving a "
             "target unclaimed costs nothing.")
REPO_TOOLS = {
    "inventory": ["Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(wc:*)", "Bash(jq:*)", "Bash(git ls-files:*)", "Bash(git log:*)",
                  "Bash(git show:*)", "Bash(aws s3 ls:*)", "Bash(aws s3 cp:*)", "Bash(modal volume ls:*)",
                  "Bash(modal volume get:*)", "Bash(mkdir -p runs/:*)"],
    "test": ["Bash"],
    "review": ["Bash(python3 tools/recall.py:*)", "Bash(python3 tools/exa.py:*)", "Bash(uv run tools/board.py ls:*)",
               "Bash(uv run tools/board.py show:*)", "Bash(git log:*)", "Bash(git show:*)", "Bash(ls:*)", "Bash(cat:*)"],
}
THEORY_KEYS = {"name", "statement", "scope", "parent", "imports", "explains", "conflicts", "rival", "predictions"}
THEORY_KEYS_V4 = {"name", "statement", "scope", "explains", "conflicts", "rival", "predictions"}
PREDICTION_KEYS = {"experiment", "unit", "value", "low", "high", "refuted_by", "gpu_minutes"}
MECHANISM_KEYS = {"id", "mechanism", "starts_from", "import", "differs_from", "holds_against", "base_change", "first_test"}
METRICS_FILES = ("metrics_v4.json", "metrics_v3.json", "metrics_v2.json", "metrics.json")
BAD_VERDICTS = ("refuted", "published")  # a weak survivor is carried: only a carried theory can earn forecast gain
HEADING = re.compile(r"^### (\S+) — ", re.M)
args = None
_tmp = []


def tmp():
    if not _tmp:
        _tmp.append(Path(tempfile.mkdtemp(prefix="theory-round-")))
        print(f"job dirs under {_tmp[0]}")
    return _tmp[0]


def number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def round_number(folder):
    """round-<nn>. A folder named otherwise (results/account/run-01) is the round after --from; the --from folder
    itself, when named otherwise, has the highest round number among its theories."""
    m = re.search(r"round-(\d+)", Path(folder).name)
    if m:
        return int(m.group(1))
    if not args.prev:
        sys.exit(f"{folder} is not named round-<nn>: give --from <previous round dir> with every command")
    if Path(folder).resolve() != Path(args.prev).resolve():
        return round_number(args.prev) + 1
    return max(int(re.match(r"r(\d+)-", p.name).group(1)) for p in (Path(folder) / "theories").glob("r*-*.json"))


def in_scope(name):
    """An account (new or carried) is tested and duelled only with --with-account; --only-account implies it and tests
    and duels only accounts, carried theories are inputs to the account."""
    return args.with_account if "-account" in name else not args.only_account


def prompt(stage, **values):
    """A prompt file with its $names filled; $intervention is prompts/intervention.md unless given."""
    values.setdefault("intervention", (LIB / "prompts" / "intervention.md").read_text())
    return string.Template((LIB / "prompts" / f"{stage}.md").read_text()).substitute(values)


def model(stage):
    return args.model_all or MODELS[stage]


def heads(folder):
    return set(HEADING.findall((folder / "external.md").read_text()))


# ---- running headless jobs ----

def job(stage, name, inputs, outputs, valid=None, mode="blind", **values):
    """inputs: {name in job dir: Path or text}; outputs: {name in job dir: destination}; valid(job dir) -> error or None."""
    d = tmp() / stage / name
    return {"stage": stage, "name": name, "dir": d, "inputs": inputs, "outputs": outputs, "valid": valid, "mode": mode,
            "prompt": prompt(stage if stage != "reverse-claims" else "claims", out=d, **values),
            "model": model("claims" if stage == "reverse-claims" else stage)}


def command(j, folder):
    base = ["claude", "-p", "--model", j["model"], "--restricted", "--strict-mcp-config", "--no-session-persistence"]
    if j["mode"] == "blind":
        return base + ["--tools", "Read,Write", "--allowedTools", "Read", "Write"]
    if j["mode"] == "rows":  # engine 17: Bash in the job directory, which holds the explore half of the stored rows
        return base + ["--tools", "Read,Write,Bash,Glob,Grep", "--allowedTools", "Read", "Write", "Bash", "Glob", "Grep",
                       "--output-format", "stream-json", "--verbose"]
    if j["mode"] == "papers":
        return base + ["--tools", "Read,Write,Bash", "--allowedTools", "Read", "Write", f"Bash(python3 {LIB / 'papers.py'}:*)"]
    return base + ["--add-dir", str(j["dir"]), str(folder.resolve()), "--tools", "Read,Grep,Glob,Write,Bash",
                   "--allowedTools", "Read", "Grep", "Glob", "Write", *REPO_TOOLS[j["stage"]]]


def claude(j, folder, text, suffix):
    """One headless run of the job's model in its directory; prompt<suffix>.txt in, out<suffix>.txt out."""
    d, repo = j["dir"], j["mode"] == "repo"
    (d / f"prompt{suffix}.txt").write_text(text)
    out = d / f"out{suffix}.txt"
    with open(d / f"prompt{suffix}.txt") as stdin, open(out, "w") as stdout:
        code = subprocess.run(command(j, folder), stdin=stdin, stdout=stdout, stderr=subprocess.STDOUT, cwd=ROOT if repo else d,
                              env={**os.environ, "AWS_PROFILE": AWS_PROFILE} if repo else None, timeout=3600).returncode
    if code:
        sys.exit(f"{j['stage']}/{j['name']}: claude exited with {code}; see {out}")
    if j["mode"] == "rows" and (bad := outside_calls(out, d)):
        sys.exit(f"{j['stage']}/{j['name']}: tool calls name paths outside the job directory (the test half may have been read): {bad[:3]}; see {out}")


def outside_calls(out, d):
    """Tool calls in a rows job's stream-json transcript whose input names the repository, the home folder or /Users/:
    a rows job may read only its own directory, which holds the explore half."""
    marks, bad = (str(ROOT), str(ROOT.parent), os.path.expanduser("~"), "/Users/", "iterate-hack", "split_v1", "../", "cd ..", "cd /", "cd ~"), []
    for line in open(out):
        if line.startswith("{"):
            for c in (json.loads(line).get("message") or {}).get("content") or []:
                x = json.dumps(c.get("input")).replace(str(d.resolve()), "<dir>").replace(str(d), "<dir>") if isinstance(c, dict) and c.get("type") == "tool_use" else ""
                if any(m in x for m in marks):
                    bad.append(x[:200])
    return bad


def run_one(j, folder):
    d = j["dir"]
    d.mkdir(parents=True)
    for rel, src in j["inputs"].items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        if isinstance(src, str):
            (d / rel).write_text(src)
        elif src.is_dir():
            shutil.copytree(src, d / rel)
        else:
            shutil.copy(src, d / rel)
    start = time.time()
    claude(j, folder, j["prompt"], "")
    missing = [rel for rel in j["outputs"] if not (d / rel).exists()]
    error = f"wrote no {', '.join(missing)}" if missing else None
    if not error and j["valid"]:
        try:  # the first check's error, a parse error included, goes back to the job once; the second check raises
            error = j["valid"](d)
        except Exception as e:
            error = f"malformed output: {type(e).__name__}: {e}"
    if error:
        print(f"  {j['stage']}/{j['name']}: {error}; sent back once")
        files = ", ".join(str(d / rel) for rel in j["outputs"])
        claude(j, folder, j["prompt"] + "\n\n" + prompt("sendback", files=files, message=error), ".sendback")
        print(f"  {j['stage']}/{j['name']}: checking the send-back; on a traceback see {d / 'out.sendback.txt'}")
        missing = [rel for rel in j["outputs"] if not (d / rel).exists()]
        error = f"wrote no {', '.join(missing)}" if missing else j["valid"] and j["valid"](d)
        if error:
            sys.exit(f"{j['stage']}/{j['name']}: {error} after the send-back; see {d / 'out.sendback.txt'}")
    for rel, dest in j["outputs"].items():
        dest.parent.mkdir(parents=True, exist_ok=True)
        if (d / rel).is_dir():
            shutil.copytree(d / rel, dest, dirs_exist_ok=True)
        else:
            shutil.copy(d / rel, dest)
    print(f"  {j['stage']}/{j['name']} ({j['model']}): done in {time.time() - start:.0f} s")


def run(jobs, folder, workers=None):
    todo = [j for j in jobs if not all(p.exists() for p in j["outputs"].values())]
    for j in jobs:
        if j not in todo:
            print(f"  skip {j['stage']}/{j['name']}: its outputs exist")
    if todo:
        workers = min(workers or args.workers, len(todo))
        print(f"  running {len(todo)} jobs, {workers} at a time")
        with ThreadPoolExecutor(workers) as pool:
            for f in [pool.submit(run_one, j, folder) for j in todo]:
                f.result()


# ---- checks ----

def quote_check(before, after, targets, theories):
    """check.py check on a scratch folder; returns its failure lines, empty when everything passes."""
    f = Path(tempfile.mkdtemp(dir=tmp(), prefix="check-"))
    write(f / "before.jsonl", before)
    write(f / "after.jsonl", after)
    write(f / "targets.jsonl", targets)
    (f / "theories").mkdir()
    for name, theory in theories.items():
        (f / "theories" / f"{name}.json").write_text(json.dumps(theory))
    p = subprocess.run([sys.executable, str(LIB / "check.py"), "check", str(f)], capture_output=True, text=True)
    lines = p.stderr.strip().splitlines() if p.returncode else []
    assert all(re.match(r"(target \S+|\S+\.json): ", line) for line in lines), p.stderr
    return lines, f


def target_ids(folder):
    return [t["id"] for t in read(folder / "targets_blind.jsonl")]


def interval_rows(path, ids, exact):
    """Error text for a jsonl of {id, value, low, high}: ids among `ids` (all of them once when exact), low <= value <= high."""
    rows = read(path)
    seen = [r["id"] for r in rows]
    bad = [r["id"] for r in rows if not (all(number(r[k]) for k in ("value", "low", "high")) and r["low"] <= r["value"] <= r["high"])]
    if len(seen) != len(set(seen)):
        return "a target id appears twice"
    if not set(seen) <= set(ids):
        return f"unknown target ids {sorted(set(seen) - set(ids))}"
    if exact and set(seen) != set(ids):
        return f"missing target ids {sorted(set(ids) - set(seen))}"
    return f"value outside [low, high] or not a number for {bad}" if bad else None


def prediction_messages(name, predictions):
    m = []
    for i, p in enumerate(predictions, 1):
        if PREDICTION_KEYS - p.keys():
            m.append(f"{name}.json: prediction {i} misses keys {sorted(PREDICTION_KEYS - p.keys())}")
        elif not (all(number(p[k]) for k in ("value", "low", "high")) and p["low"] <= p["value"] <= p["high"]):
            m.append(f"{name}.json: prediction {i} needs numbers with low <= value <= high")
    return m


INTERVENTION_KEYS = {"change", "model", "cell", "count", "unit", "value", "low", "high", "best_known", "gpu_minutes", "why"}
CELL_KEYS = {"set", "prompt", "sampling", "cap", "grader", "samples", "seeds"}


def intervention_messages(r, items):
    """Errors in r["intervention"] (prompts/intervention.md): a change to the base with its cell, its predicted count,
    the best known base-only count with a before.jsonl item id (or facts.json), GPU minutes and why; or null with
    "no_intervention"."""
    if "intervention" not in r:
        return ["needs the key \"intervention\" (an object, or null with \"no_intervention\": the reason)"]
    i = r["intervention"]
    if i is None:
        return [] if isinstance(r.get("no_intervention"), str) and r["no_intervention"].strip() else \
            ["\"intervention\" is null, so \"no_intervention\" must give the reason"]
    if not isinstance(i, dict) or INTERVENTION_KEYS - i.keys():
        return [f"\"intervention\" misses keys {sorted(INTERVENTION_KEYS - (i.keys() if isinstance(i, dict) else set()))}"]
    m = []
    if not isinstance(i["cell"], dict) or CELL_KEYS - i["cell"].keys():
        m.append(f"\"intervention\".cell needs the keys {sorted(CELL_KEYS)}")
    if not (all(number(i[k]) for k in ("value", "low", "high")) and i["low"] <= i["value"] <= i["high"]):
        m.append("\"intervention\" needs numbers with low <= value <= high")
    b = i["best_known"]
    if not (isinstance(b, dict) and number(b.get("value")) and (b.get("item") in items or b.get("item") == "facts.json")):
        m.append("\"intervention\".best_known needs a number \"value\" and an \"item\" that is a before.jsonl id or \"facts.json\"")
    if not (number(i["gpu_minutes"]) and i["gpu_minutes"] > 0):
        m.append("\"intervention\".gpu_minutes must be a number above 0")
    if not (isinstance(i["why"], str) and i["why"].strip()):
        m.append("\"intervention\".why must be one sentence")
    return m


def item_ids(folder):
    return {i["id"] for i in read(folder / "before.jsonl")}


def add_quote_messages(folder, msgs, drafts):
    """check.py's quote check on every draft whose cited entries all have an item and a quote."""
    quotable = {n: t for n, t in drafts.items() if isinstance(t.get("explains"), list) and isinstance(t.get("conflicts"), list)
                and all("item" in c and "quote" in c for c in t["explains"] + t["conflicts"])}
    lines, _ = quote_check(read(folder / "before.jsonl"), [], [], quotable)
    for line in lines:
        msgs[line.split(".json: ")[0]].append(line)
    return msgs


def check_theories(folder, drafts, standing):
    """Messages per theory: the v3 form rules, then check.py's quote check."""
    known = heads(folder)
    msgs = {name: [] for name in drafts}
    for name, t in drafts.items():
        m = msgs[name]
        if missing := THEORY_KEYS - t.keys():
            m.append(f"{name}.json: missing keys {sorted(missing)}")
            continue
        if t["name"] != name:
            m.append(f"{name}.json: \"name\" must be {name!r}")
        if len(t["explains"]) < 5 or len({e.get("item") for e in t["explains"]}) < 2:
            m.append(f"{name}.json: \"explains\" needs at least 5 quotes from at least 2 items")
        if name.split("-")[1] != "revise" and not t["imports"]:
            m.append(f"{name}.json: needs at least one import from external.md")
        for imported in t["imports"]:
            if imported.get("source") not in known:
                m.append(f"{name}.json: import source {imported.get('source')!r} is not a heading id in external.md")
        if t["parent"] is not None and t["parent"] not in standing:
            m.append(f"{name}.json: parent {t['parent']!r} is not a standing theory (standing: {sorted(standing)}, or null)")
        m += prediction_messages(name, t["predictions"])
        offline = [p for p in t["predictions"] if "recipe" in p]
        if len(offline) < 2 or any(p.get("gpu_minutes") != 0 for p in offline):
            m.append(f"{name}.json: needs at least 2 offline predictions, each with a \"recipe\" and \"gpu_minutes\": 0")
    return add_quote_messages(folder, msgs, {n: t for n, t in drafts.items() if not THEORY_KEYS - t.keys()})


def check_theories4(folder, drafts, parents):
    """Messages per theory: the v4 form rules (3 offline predictions, 1 GPU prediction), then check.py's quote check."""
    known = heads(folder)
    msgs = {name: [] for name in drafts}
    for name, t in drafts.items():
        m = msgs[name]
        if missing := THEORY_KEYS_V4 - t.keys():
            m.append(f"{name}.json: missing keys {sorted(missing)}")
            continue
        if t["name"] != name:
            m.append(f"{name}.json: \"name\" must be {name!r}")
        if len(t["explains"]) < 3:
            m.append(f"{name}.json: \"explains\" needs at least 3 quotes")
        for imported in t.get("imports") or []:
            if imported.get("source") not in known:
                m.append(f"{name}.json: import source {imported.get('source')!r} is not a heading id in external.md")
        if t.get("parent") is not None and t["parent"] not in parents:
            m.append(f"{name}.json: parent {t['parent']!r} is not a theory in graveyard.json (or null)")
        m += prediction_messages(name, t["predictions"])
        offline = [p for p in t["predictions"] if "recipe" in p]
        if len(offline) < 3 or any(p.get("gpu_minutes") != 0 for p in offline):
            m.append(f"{name}.json: needs at least 3 offline predictions, each with a \"recipe\" and \"gpu_minutes\": 0")
        if not any("recipe" not in p and number(p.get("gpu_minutes")) and p["gpu_minutes"] > 0 for p in t["predictions"]):
            m.append(f"{name}.json: needs at least 1 GPU prediction (no recipe, gpu_minutes above 0)")
        if args.version >= 7:
            m += [f"{name}.json: {e}" for e in intervention_messages(t, item_ids(folder))]
        if args.version >= 8:
            m += [f"{name}.json: \"forecasts\" (targets.json): {e}" for e in forecast.forecast_errors(t.get("forecasts", []), open_ids(folder), need_forecasts(folder))]
    return add_quote_messages(folder, msgs, {n: t for n, t in drafts.items() if not THEORY_KEYS_V4 - t.keys()})


def finish_theories(folder, names, drafts, checker, fix_inputs, dropped):
    """Check the drafts, send each failing one back once, write the passing ones to theories/, dropped.json, theories.sha256."""
    msgs = checker({n: drafts[n] for n in names})
    failing = [n for n in names if msgs[n]]
    for n in failing:
        print(f"  {n} fails the check, sent back once:\n    " + "\n    ".join(msgs[n]))
    run([job("fix", n, {"theory.json": folder / "drafts" / f"{n}.json", **fix_inputs},
             {"theory.json": folder / "drafts" / f"{n}.fix.json"}, lambda d: None if isinstance(json.loads((d / "theory.json").read_text()), dict) else "not a JSON object",
             message="\n".join(msgs[n])) for n in failing], folder)
    fixed = {n: json.loads((folder / "drafts" / f"{n}.fix.json").read_text()) for n in failing}
    again = checker(fixed) if fixed else {}
    dropped = {**dropped, **{n: m for n, m in again.items() if m}}
    (folder / "theories").mkdir(exist_ok=True)
    for n in names:
        if n not in dropped:
            (folder / "theories" / f"{n}.json").write_text(json.dumps(fixed.get(n, drafts[n]), indent=1) + "\n")
    for n, m in dropped.items():
        print(f"  dropped {n}: {json.dumps(m)[:300]}")
    (folder / "dropped.json").write_text(json.dumps(dropped, indent=1) + "\n")
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  theories/{p.name}\n" for p in sorted((folder / "theories").glob("*.json"))]
    (folder / "theories.sha256").write_text("".join(lines))
    print(f"  {len(lines)} theories in theories/ ({sum(n not in dropped for n in names)} new); {len(dropped)} dropped; wrote theories.sha256")


# ---- stages ----

def split(folder):
    if (folder / "before.jsonl").exists():
        return print("skip split: before.jsonl exists")
    if not args.cutoff:
        sys.exit("split needs --cutoff <ISO time>")
    check.dump(folder, args.cutoff, args.skip)


def graveyard_reason(m, review, what):
    """One line on why a theory did not survive: its review, else its metrics."""
    if review:
        return f"review: {review['verdict']} {review.get('verdict_sentence', '')}".strip()[:300]
    if "beats_null" in m:
        return (f"round-01 score: closer/farther than null-1 +{m['vs_null_1']['closer']} -{m['vs_null_1']['farther']}, "
                f"null-2 +{m['vs_null_2']['closer']} -{m['vs_null_2']['farther']}; did not beat the noise")
    if "reasons" in m:
        return "; ".join(m["reasons"]) or f"{m['computed']} offline tests computed, total gain {m['total_gain']}"
    rows = m.get("rows") or []
    if not rows:
        return "no claims"
    worst = min(rows, key=lambda r: r["gain"] if "gain" in r else -2 if r.get("divergent") and not r["inside"] else -1 if not r["inside"] else 0)
    head = f"total gain {m['total_gain']} on {m['claims']} claims" if "total_gain" in m else f"divergent wins {m['wins']}, losses {m['losses']}"
    return (f"{head}; worst claim: {what.get(worst['id'], worst['id'])[:100]}: claimed {worst['value']} "
            f"[{worst['low']}, {worst['high']}], measured {worst['measured']}")


def fact(q):
    return {k: q.get(k) for k in ("experiment", "recipe", "unit", "measured", "n", "interval")}


def survivor(entry):
    return entry["state"] in ("survives", "passes") and not entry["verdict"].startswith(BAD_VERDICTS)


def standing(folder):
    if not args.prev:
        return print("standing: no --from given, so no graveyard and no carried theories")
    if (folder / "graveyard.json").exists():
        return print("skip standing: graveyard.json exists")
    prev, nn = Path(args.prev), round_number(folder)
    before = {i["id"] for i in read(folder / "before.jsonl")}
    if (prev / "targets.jsonl").exists() and (late := sorted({t["item"] for t in read(prev / "targets.jsonl")} - before)):
        sys.exit(f"the previous round's targets come from items not in before.jsonl: {late}. The cutoff must be after "
                 "every item the previous round held out, or its scores leak held-out numbers.")
    # an engine round reads every earlier round of its engine folder; any other folder (an account run) starts from
    # the graveyard of its --from folder and adds that folder's theories
    engine = re.search(r"round-\d+", prev.name)
    graveyard, where = ({}, {}) if engine else (json.loads((prev / "graveyard.json").read_text()), {})
    rdirs = sorted((d for d in prev.parent.glob("round-*") if round_number(d) < nn), key=round_number) if engine else [prev]
    for rdir in rdirs:
        mfile = next((rdir / f for f in METRICS_FILES if (rdir / f).exists()), None)
        if mfile is None:
            continue
        what = {t["id"]: t["what"] for t in read(rdir / "targets.jsonl")} if (rdir / "targets.jsonl").exists() else {}
        duels = json.loads((rdir / "metrics_v5.json").read_text())["theories"] if (rdir / "metrics_v5.json").exists() else {}
        for name, m in json.loads(mfile.read_text())["theories"].items():
            if name == "planted":  # round 01's reversed control, not a theory
                continue
            review_path = rdir / "reviews" / f"{name}.json"
            review = json.loads(review_path.read_text()) if review_path.exists() else None
            state = m.get("state") or ("beats the null" if m["beats_null"] else "does not beat the null")
            entry = {"name": name, "round": round_number(rdir), "rounds": graveyard.get(name, {}).get("rounds", []) + [round_number(rdir)],
                     "statement": json.loads((rdir / "theories" / f"{name}.json").read_text())["statement"],
                     "state": state, "verdict": review["verdict"] if review else ""}
            duel = duels.get(name)
            if duel and duel["state"] == "loses to rival":
                lost = [r for r in duel["rows"] if r.get("gain", 0) <= -1]  # the decisive tests
                entry["state"] = "lost to its rival"
                entry["reason"] = f"lost to its rival ({duel['total_gain']} nats): {duel['rival'][:200]}; " + "; ".join(
                    f"p{r['k']} {r['experiment'][:80]}: measured {r['measured']:g}, theory {r['theory']['value']:g}, "
                    f"rival {r['rival']['value']:g}, gain {r['gain']:+.2f}" for r in lost)
            else:
                entry["reason"] = "" if survivor(entry) else graveyard_reason(m, review, what)
            graveyard[name], where[name] = entry, rdir
    gpu = gpu_tests(prev)
    (folder / "gpu_tests.json").write_text(json.dumps(gpu, indent=1) + "\n")
    strikes = {}
    for g in gpu:
        for side, s in g["sides"].items():
            strikes.setdefault(side, []).extend([g["id"]] if s["strike"] else [])
    struck = {side: ids for side, ids in strikes.items() if len(ids) >= 2}
    for side, ids in struck.items():  # a rival that never entered as a theory gets its own graveyard entry
        entry = graveyard.setdefault(side, {"name": side, "round": round_number(prev), "rounds": [round_number(prev)],
                                            "statement": next(g["statements"][side] for g in gpu if side in g["sides"]), "verdict": ""})
        if entry.get("state") != "lost to its rival":  # that state promotes its rival; keep it
            entry["state"] = "refuted by GPU tests"
        entry["reason"] = "; ".join(filter(None, [entry.get("reason"), f"missed its interval on {len(ids)} GPU tests: {', '.join(ids)}"]))
    if args.version >= 8 and (prev / "forecasts.json").exists():  # the previous round's forecasts of the open work
        fc = json.loads((prev / "forecasts.json").read_text())
        scores = forecast.scored(fc["forecasts"], forecast.find_measured(prev, fc["snapshot_utc"]))
        (folder / "forecast_scores.json").write_text(json.dumps(scores, indent=1) + "\n")
        for name, p in scores["forecasters"].items():
            print(f"  forecasts of {name}: {p['scored']} scored, {p['inside']} inside, gain {p['total_gain']:+.2f} nats")
            if name not in graveyard:
                continue
            graveyard[name]["forecast"] = {k: p[k] for k in ("scored", "inside", "total_gain")}
            if p["scored"] >= 3 and p["total_gain"] <= -2 and graveyard[name]["state"] != "lost to its rival":
                graveyard[name]["state"] = "refuted by forecasts"
                graveyard[name]["reason"] = f"forecast gain {p['total_gain']:+.2f} nats on {p['scored']} targets: " + "; ".join(
                    f"{r['id']} measured {r['measured']:g}, forecast {r['value']:g} [{r['low']:g}, {r['high']:g}], gain {r['gain']:+.2f}" for r in p["rows"])
    (folder / "graveyard.json").write_text(json.dumps(graveyard, indent=1) + "\n")
    (folder / "theories").mkdir(exist_ok=True)
    carried = 0
    for name, entry in graveyard.items():
        if name not in where:  # an entry from the --from folder's graveyard: decided before, not carried
            continue
        # an untested theory is carried once after a round that tested it (and again after a round that did not, as
        # an --only-account run); a survivor is carried with its computed tests and their gains (tests/<name>.json,
        # "carried_from"), so they are not computed or scored again
        untested = entry["state"] == "untested" and (len(entry["rounds"]) == 1 or not (where[name] / "tests" / f"{name}.json").exists())
        if survivor(entry) or untested:
            carried += 1
            shutil.copy(where[name] / "theories" / f"{name}.json", folder / "theories")
            if (where[name] / "reviews" / f"{name}.json").exists():
                (folder / "prior_reviews").mkdir(exist_ok=True)
                shutil.copy(where[name] / "reviews" / f"{name}.json", folder / "prior_reviews")
            if survivor(entry) and (where[name] / "metrics_v4.json").exists():
                tests = json.loads((where[name] / "tests" / f"{name}.json").read_text())
                rows = json.loads((where[name] / "metrics_v4.json").read_text())["theories"][name]["rows"]
                (folder / "tests").mkdir(exist_ok=True)
                (folder / "tests" / f"{name}.json").write_text(
                    json.dumps({**tests, "carried_from": tests.get("carried_from", where[name].name), "rows": rows}, indent=1) + "\n")
                for f in (where[name] / "rivals").glob(f"{name}.*"):  # its rival files and duel scripts: no second duel
                    (folder / "rivals").mkdir(exist_ok=True)
                    (shutil.copytree if f.is_dir() else shutil.copy)(f, folder / "rivals" / f.name)
                if (where[name] / "rivals" / name).is_dir():
                    shutil.copytree(where[name] / "rivals" / name, folder / "rivals" / name)
                if (where[name] / "experiments" / f"{name}.json").exists():  # its pair's open experiments: no second cross_predict
                    (folder / "experiments").mkdir(exist_ok=True)
                    shutil.copy(where[name] / "experiments" / f"{name}.json", folder / "experiments")
            print(f"  carried: {name} (round {entry['round']}, {entry['state']})")
        if entry["state"] == "lost to its rival" and round_number(where[name]) == round_number(prev) and f"{name}-rival" in struck:
            print(f"  not carried: {name}-rival (the rival that beat {name}): {graveyard[name + '-rival']['reason']}")
        elif entry["state"] == "lost to its rival" and round_number(where[name]) == round_number(prev):
            carried += 1
            promote(where[name], folder, name)
            print(f"  carried: {name}-rival (the rival that beat {name} in round {entry['round']})")
    print(f"  graveyard.json: {len(graveyard)} theories from earlier rounds, {carried} carried")
    # every number computed in the previous folder (offline tests, duel tests, with their replication), then its own
    # facts.json: cumulative over the chain of rounds, engine or account
    facts = [{"round": t.get("carried_from") or prev.name, "theory": t["theory"], "kind": "offline", "asked_by": t["theory"],
              **fact(q), "replication": replication(prev, t["theory"]).get(q["k"], {}).get("status")}
             for t in map(lambda f: json.loads(f.read_text()), sorted((prev / "tests").glob("*.json")))
             for q in t["predictions"] if q["measured"] is not None] if (prev / "tests").exists() else []
    facts += [{"round": prev.name, "theory": t["theory"], "kind": "duel", "asked_by": f"the rival of {t['theory']}",
               **fact(q), "replication": replication(prev, t["theory"], ".duel").get(q["k"], {}).get("status")}
              for t in map(lambda f: json.loads(f.read_text()), sorted((prev / "rivals").glob("*.tests.json")))
              for q in t["tests"] if q["measured"] is not None] if (prev / "rivals").exists() else []
    facts += [{"round": g["round"], "theory": g["proposer"], "kind": "gpu", "asked_by": g["proposer"], "experiment": g["experiment"],
               "recipe": None, "unit": g["unit"], "measured": g["measured"], "n": g.get("n"), "interval": g.get("interval"),
               "replication": None, "artifact": g["artifact"], "item": g["item"]} for g in gpu]
    if (prev / "facts.json").exists():  # and every number the previous round's own facts.json held
        seen = {(f["theory"], f["kind"], f["experiment"]) for f in facts}
        facts += [f for f in json.loads((prev / "facts.json").read_text()) if (f["theory"], f["kind"], f["experiment"]) not in seen]
    (folder / "facts.json").write_text(json.dumps(facts, indent=1) + "\n")
    v4 = json.loads((prev / "metrics_v4.json").read_text())["theories"] if (prev / "metrics_v4.json").exists() else {}
    v5 = json.loads((prev / "metrics_v5.json").read_text())["theories"] if (prev / "metrics_v5.json").exists() else {}
    # every account of the chain: a folder's own incumbents, then its accounts with their measured numbers
    def accounts_of(src):
        m4 = json.loads((src / "metrics_v4.json").read_text())["theories"] if (src / "metrics_v4.json").exists() else {}
        m5 = json.loads((src / "metrics_v5.json").read_text())["theories"] if (src / "metrics_v5.json").exists() else {}
        chain = json.loads((src / "incumbent_account.json").read_text()) if (src / "incumbent_account.json").exists() else []
        mine = [{"name": n, "round": src.name, "state": m4[n]["state"], "theory": json.loads((src / "theories" / f"{n}.json").read_text()),
                 "measured": [{k: q.get(k) for k in ("k", "role", "cell", "part", "experiment", "value", "low", "high", "measured", "n", "interval",
                                                      "by_construction")}
                              for q in json.loads((src / "tests" / f"{n}.json").read_text())["predictions"]],
                 "replication": list(replication(src, n).values()), "duel": m5.get(n)}
                for n in m4 if "-account" in n and not m4[n].get("carried_from") and (src / "tests" / f"{n}.json").exists()]
        return [a for a in chain if a.get("name") not in {b["name"] for b in mine}] + mine
    incumbent = accounts_of(prev)
    if args.account_from:  # the accounts of another chain (results/account/run-<nn>), named with their folder
        # an entry written by version 6.1 has no name or round
        incumbent = [{**a, "name": f"{a.get('name', 'account')} ({a.get('round', 'an earlier run')})"}
                     for a in accounts_of(Path(args.account_from))] + incumbent
    (folder / "incumbent_account.json").write_text(json.dumps(incumbent, indent=1) + "\n")
    print(f"  facts.json: {len(facts)} computed numbers of {prev.name}; incumbent_account.json: {len(incumbent)} accounts")
    metrics = json.loads((prev / "metrics_v3.json").read_text()) if (prev / "metrics_v3.json").exists() else None
    if metrics and (prev / "targets.jsonl").exists():  # for version 3's revise start
        what = {t["id"]: t["what"] for t in read(prev / "targets.jsonl")}
        prior = {n: {"statement": graveyard[n]["statement"], "state": m["state"],
                     "claims": [{**row, "what": what[row["id"]]} for row in m["rows"]]} for n, m in metrics["theories"].items()}
        (folder / "prior_scores.json").write_text(json.dumps(prior, indent=1) + "\n")


def clip3(x):
    return min(3.0, max(-3.0, x))


def capped(gain, x, p):
    """Version 9: a prediction whose measured value x lies outside its own 90 % interval gains at most 0."""
    return gain if p["low"] <= x <= p["high"] else min(gain, 0.0)


def pair_gain(x, p, q):
    """p's gain over q at x (duels, GPU tests): log density of p minus q, clipped to 3 nats; a side outside its own
    interval gains at most 0, so p's gain is at most 0 when p misses and at least 0 when q misses."""
    return -capped(-capped(clip3(log_density(x, p) - log_density(x, q)), x, p), x, q)


def gpu_tests(prev):
    """prev's own gpu_tests.json, then each experiment of prev/experiments.json measured since (the coordinator's
    prev/experiments_measured.json: id, measured, n, artifact, item, and the measured 90 % interval when there is one),
    scored for both sides by the duel rule: gain = log density of the side's prediction minus the other side's, at the
    measured value, clipped to 3 nats (pair_gain: a side outside its own interval gains at most 0). A side gets a strike when the measured value is outside its interval and the
    measured interval, if given, misses it too."""
    done = json.loads((prev / "gpu_tests.json").read_text()) if (prev / "gpu_tests.json").exists() else []
    if not (prev / "experiments_measured.json").exists():
        return done
    proposed = {e["id"]: e for e in json.loads((prev / "experiments.json").read_text())["experiments"]}
    seen = {g["id"] for g in done}
    for m in json.loads((prev / "experiments_measured.json").read_text()):
        if m["id"] in seen:
            continue
        e, x = proposed[m["id"]], m["measured"]
        preds = {e["proposer"]: e["proposer_prediction"], e["other"]: e["other_prediction"]}
        sides = {}
        for side, p in preds.items():
            q = preds[e["other"] if side == e["proposer"] else e["proposer"]]
            sides[side] = {k: p[k] for k in ("value", "low", "high")} | {
                "gain": round(pair_gain(x, p, q), 4),
                "strike": not p["low"] <= x <= p["high"] and not overlaps({**p, "interval": m.get("interval")})}
        done.append({**m, "round": prev.name, "pair": e["pair"], "proposer": e["proposer"], "experiment": e["experiment"],
                     "unit": e["unit"], "statements": e["statements"], "sides": sides})
        print(f"  GPU test {m['id']}: measured {x:g} (n {m.get('n')}, {m['artifact']}); " + "; ".join(
            f"{side} {s['value']:g} [{s['low']:g}, {s['high']:g}] gain {s['gain']:+.2f}{', strike' if s['strike'] else ''}"
            for side, s in sides.items()))
    return done


def promote(prev, folder, name):
    """The rival that beat `name` in round `prev` becomes theory <name>-rival here: its duel tests, computed and scored
    in that round (the defeated theory's prediction as the reader), are its record and are not computed again."""
    duel = json.loads((prev / "metrics_v5.json").read_text())["theories"][name]
    new = f"{name}-rival"
    tests = {t["k"]: t for turn in (1, 2) if rfile(prev, name, turn).exists() for t in rival_tests(prev, name, turn, full=True)}
    predictions = [{k: tests[r["k"]][k] for k in ("experiment", "recipe", "unit", "value", "low", "high")} |
                   {"refuted_by": "none: a duel test", "gpu_minutes": 0} for r in duel["rows"]]
    theory = {"name": new, "statement": duel["rival"], "scope": f"the rival that beat {name} in {prev.name}; scope as in "
              f"{name}'s", "explains": [], "conflicts": [], "rival": json.loads((prev / "theories" / f"{name}.json").read_text())["statement"],
              "promoted_from": name, "predictions": predictions}
    last = rival_file(prev, name)  # its intervention, when the rival wrote one
    if "intervention" in json.loads(last.read_text()):
        theory |= {k: json.loads(last.read_text()).get(k) for k in ("intervention", "no_intervention")}
    (folder / "theories" / f"{new}.json").write_text(json.dumps(theory, indent=1) + "\n")
    preds, rows = [], []
    for k, (r, p) in enumerate(zip(duel["rows"], predictions), 1):  # k numbers the predictions in this file
        m = r["measured"]
        preds.append({"k": k, **p, "measured": m, "n": r.get("n"), "interval": r.get("interval"),
                      "inside": None if m is None else p["low"] <= m <= p["high"], "refuted_by_met": False,
                      "not_computable": r.get("not_computable"), "duel_k": r["k"], "turn": r.get("turn", 1)})
        if m is not None:
            rows.append({"id": f"{new}:p{k}", "k": k, "measured": m, **r["rival"], "nulls": [r["theory"]],
                         "gain": -r["gain"], "inside": preds[-1]["inside"], "n": r.get("n"), "interval": r.get("interval"),
                         "refuted_by": p["refuted_by"], "refuted_by_met": False})
        else:
            rows.append({"k": k, "not_computable": r["not_computable"]})
    (folder / "tests").mkdir(exist_ok=True)
    (folder / "tests" / f"{new}.json").write_text(json.dumps({"theory": new, "predictions": preds, "carried_from": prev.name,
                                                             "rows": rows}, indent=1) + "\n")


def inventory(folder):
    if (folder / "inventory.md").exists():
        return print("skip inventory: inventory.md exists")
    cutoff = min(i["at"] for i in read(folder / "after.jsonl"))
    run([job("inventory", "inventory", {}, {"inventory.md": folder / "inventory.md"}, mode="repo", cutoff=cutoff,
             profile=AWS_PROFILE)], folder)


def targets(folder):
    if (folder / "targets_blind.jsonl").exists():
        return print("skip targets: targets_blind.jsonl exists")

    def valid(d):
        rows = read(d / "targets.jsonl")
        if len({t["id"] for t in rows}) != len(rows):
            return "a target id appears twice"
        bad = [t.get("id") for t in rows if {"id", "item", "what", "unit", "value", "quote"} - t.keys() or not number(t["value"])]
        return f"targets with missing keys or a value that is not a number: {bad}" if bad else None

    run([job("targets", "targets", {"before.jsonl": folder / "before.jsonl", "after.jsonl": folder / "after.jsonl"},
             {"targets.jsonl": folder / "targets.jsonl"}, valid)], folder)
    rows, after = read(folder / "targets.jsonl"), read(folder / "after.jsonl")
    lines, _ = quote_check([], after, rows, {})
    failed = {line.split()[1].rstrip(":") for line in lines}
    for line in lines:
        print(f"  dropped {line}")
    kept = [t for t in rows if t["id"] not in failed]
    lines, f = quote_check([], after, kept, {})
    assert not lines, lines
    write(folder / "targets.jsonl", kept)
    shutil.copy(f / "targets_blind.jsonl", folder / "targets_blind.jsonl")
    print(f"  {len(kept)} targets kept, {len(failed)} dropped")
    if len(kept) < args.min_targets:
        sys.exit(f"only {len(kept)} targets: the board has too few new results for a round")


def external(folder):
    if (folder / "external.md").exists():
        return print("skip external: external.md exists")

    def valid(d):
        text = (d / "external.md").read_text()
        found = [line for line in text.splitlines() if line.startswith("### ")]
        if any(not HEADING.match(h) for h in found):
            return f"headings not of the form '### <id> — <title, year>': {[h for h in found if not HEADING.match(h)]}"
        if len(found) < 10 or text.count("\n- Finding:") != len(found):
            return f"{len(found)} headings and {text.count(chr(10) + '- Finding:')} '- Finding:' lines; need 10 or more, one each"
        return "a finding says what it bears on; findings state mechanisms only" if "Bears on" in text else None

    run([job("external", "external", {"before.jsonl": folder / "before.jsonl"}, {"external.md": folder / "external.md"},
             valid, mode="papers", papers=LIB / "papers.py")], folder)
    print(f"  external.md: {len(heads(folder))} findings")


def generate(folder):
    if (folder / "theories.sha256").exists():
        return print("skip generate: theories.sha256 exists")
    starts = args.starts.split(",")
    assert set(starts) <= STARTS.keys(), f"unknown start in {starts}"
    if "revise" in starts and not (folder / "prior_scores.json").exists():
        sys.exit("the revise start needs prior_scores.json from `standing --from`; on a first round drop revise from --starts")
    nn = round_number(folder)
    (folder / "theories").mkdir(exist_ok=True)
    standing = {p.stem: p for p in sorted((folder / "theories").glob("*.json")) if not p.stem.startswith(f"r{nn}-")}
    standing_inputs = {f"standing/{n}.json": p for n, p in standing.items()} or {"standing/none.txt": "No theory stands from earlier rounds.\n"}

    text = (folder / "external.md").read_text()
    head, *findings = re.split(r"(?m)^(?=### )", text)
    fresh = [s for s in starts if s != "revise"]
    for k, start in enumerate(fresh):
        (folder / f"external_{start}.md").write_text(head + "".join(findings[k::len(fresh)]))

    def valid(d):
        return next((f"{p.name} is not a JSON object" for p in d.glob("r*.json") if not isinstance(json.loads(p.read_text()), dict)), None)

    jobs = []
    for start in starts:
        names = [f"r{nn}-{start}-1", f"r{nn}-{start}-2"]
        inputs = {"DIRECTION.md": ROOT / "DIRECTION.md", "before.jsonl": folder / "before.jsonl",
                  "inventory.md": folder / "inventory.md", **standing_inputs,
                  "external.md": folder / ("external.md" if start == "revise" else f"external_{start}.md")}
        extra = ""
        if start == "revise":
            inputs["prior_scores.json"] = folder / "prior_scores.json"
            extra = "- prior_scores.json: the previous round's theories, each with its claims about that round's held-out numbers and the measured values.\n"
            if (folder / "prior_reviews").exists():
                inputs["prior_reviews"] = folder / "prior_reviews"
                extra += "- prior_reviews/: the reviews of the standing theories.\n"
        rule = ("- Imports are optional for this start; when you use one, its source is a source id from an external.md heading."
                if start == "revise" else
                "- Imports: at least one entry in \"imports\", each a finding from external.md that no item in before.jsonl "
                "cites. The import must do work in the mechanism, not decorate it.")
        jobs.append(job("generate", start, inputs, {f"{n}.json": folder / "drafts" / f"{n}.json" for n in names}, valid,
                        extra_files=extra, start_description=STARTS[start], name1=names[0],
                        name2=names[1], imports_rule=rule))
    run(jobs, folder)
    names = [f"r{nn}-{s}-{k}" for s in starts for k in (1, 2)]
    drafts = {n: json.loads((folder / "drafts" / f"{n}.json").read_text()) for n in names}
    fix_inputs = {"before.jsonl": folder / "before.jsonl", "external.md": folder / "external.md",
                  "inventory.md": folder / "inventory.md", **standing_inputs}
    finish_theories(folder, names, drafts, lambda ds: check_theories(folder, ds, standing), fix_inputs, {})


def facts_input(folder):
    """facts.json: the numbers earlier rounds computed from stored rows; evidence for every agent."""
    return folder / "facts.json" if (folder / "facts.json").exists() else "[]\n"


def graveyard_input(folder):
    return folder / "graveyard.json" if (folder / "graveyard.json").exists() else "{}\n"


def mechanisms(folder):
    if (folder / "mechanisms.json").exists():
        return print("skip mechanisms: mechanisms.json exists")
    if args.deep:  # version 9: the wide round's carried mechanisms (total forecast gain above 0) are the mechanisms
        carried = json.loads((Path(args.deep) / "standing.json").read_text())["carried"]
        ms = [{"id": f"m{k:02d}", "mechanism": m["statement"], "starts_from": f"wide round mechanism {m['id']}: forecast gain "
               f"{m['forecast']['total_gain']:+.2f} nats on {m['forecast']['scored']} numbers", "import": None, "differs_from": "",
               "holds_against": m["holds_against"], "base_change": None, "first_test": None, "targets": open_ids(folder)} for k, m in enumerate(carried, 1)]
        (folder / "mechanisms.json").write_text(json.dumps(ms, indent=1))
        return print(f"  {len(ms)} mechanisms carried by {args.deep}")
    n, known = args.n_mechanisms, heads(folder)

    def valid(d):
        ms = json.loads((d / "mechanisms.json").read_text())
        if not isinstance(ms, list) or len(ms) != n:
            return f"need a JSON list of {n} mechanisms"
        if bad := [m.get("id") for m in ms if MECHANISM_KEYS - m.keys()]:
            return f"mechanisms missing keys: {bad}"
        ids = [m["id"] for m in ms]
        if len(set(ids)) != n or not all(re.fullmatch(r"m\d\d", i) for i in ids):
            return f"ids must be distinct, of the form m01: {ids}"
        if 2 * sum(m["base_change"] is not None for m in ms) < n:
            return f"at least half of the {n} mechanisms need a base_change (a change to the untrained base alone)"
        bad = [m["id"] for m in ms if m["import"] is not None and m["import"] not in known]
        if bad:
            return f"imports that are not external.md heading ids: {bad}"
        if args.version >= 8:
            need = need_forecasts(folder)
            bad = [m["id"] for m in ms if len(set(m.get("targets", [])) & set(open_ids(folder))) < need]
            return f"each mechanism needs \"targets\" with {need} or more ids of targets.json; failing: {bad}" if bad else None

    v8 = {"targets.json": folder / "targets.json"} if args.version >= 8 else {}
    run([job("mechanisms", "mechanisms", {"DIRECTION.md": ROOT / "DIRECTION.md", "before.jsonl": folder / "before.jsonl",
                                          "external.md": folder / "external.md", "inventory.md": folder / "inventory.md",
                                          "graveyard.json": graveyard_input(folder), "facts.json": facts_input(folder), **v8},
             {"mechanisms.json": folder / "mechanisms.json"}, valid, n=n,
             forecast_rule=MECHANISM_FORECASTS.format(need=need_forecasts(folder)) if v8 else "")], folder)
    for m in json.loads((folder / "mechanisms.json").read_text()):
        print(f"  {m['id']}: {m['mechanism'][:150]}")


def develop(folder):
    if (folder / "theories.sha256").exists():
        return print("skip develop: theories.sha256 exists")
    nn = round_number(folder)
    ms = json.loads((folder / "mechanisms.json").read_text())
    graveyard = json.loads((folder / "graveyard.json").read_text()) if (folder / "graveyard.json").exists() else {}
    names = [f"r{nn}-{m['id']}" for m in ms]

    def valid(d):
        r = json.loads((d / "result.json").read_text())
        return None if isinstance(r, dict) and (isinstance(r.get("abandon"), str) or "statement" in r) else "neither a theory nor {\"abandon\": reason}"

    base = {"DIRECTION.md": ROOT / "DIRECTION.md", "before.jsonl": folder / "before.jsonl",
            "inventory.md": folder / "inventory.md", "external.md": folder / "external.md", "facts.json": facts_input(folder)}
    v8 = {"targets.json": folder / "targets.json"} if args.version >= 8 else {}
    rule = DEVELOP_FORECASTS.format(need=need_forecasts(folder)) if v8 else ""
    run([job("develop", name, {**base, **v8, "mechanism.json": json.dumps(m, indent=1)}, {"result.json": folder / "drafts" / f"{name}.json"},
             valid, theory=name, forecast_rule=rule) for name, m in zip(names, ms)], folder)
    drafts = {n: json.loads((folder / "drafts" / f"{n}.json").read_text()) for n in names}
    abandoned = {n: {"abandon": d["abandon"]} for n, d in drafts.items() if "abandon" in d}
    for n, a in abandoned.items():
        print(f"  abandoned {n}: {a['abandon'][:200]}")
    fix_inputs = {"before.jsonl": folder / "before.jsonl", "external.md": folder / "external.md",
                  "inventory.md": folder / "inventory.md", "graveyard.json": graveyard_input(folder), **v8}
    finish_theories(folder, [n for n in names if n not in abandoned], drafts,
                    lambda ds: check_theories4(folder, ds, set(graveyard)), fix_inputs, abandoned)


ACCOUNT_PART_KEYS = {"name", "mechanism", "rule"}


def check_account(folder, drafts, parents):
    """Messages per account: the develop check, then the budget rules. 3-6 parts; one null cell (the base against an
    independent base sample) and 2 or more predicted model cells; a cell whose budget a board item claims gets fits,
    not shares; in the null and every predicted cell one share per part and for unassigned, summing to 1, and each
    model-cell share that is not 0 by construction states vs_null; one net prediction per cell; 6 or more scored shares
    in model cells; 2 or more cross-predictions; one evidence set; every offline prediction names its cell."""
    msgs = check_theories4(folder, drafts, parents)
    for name, t in drafts.items():
        m = msgs[name]
        parts, cells, claims, ev = t.get("parts"), t.get("cells"), t.get("known_claim"), t.get("evidence")
        if not isinstance(parts, list) or not 3 <= len(parts) <= 6 or any(not isinstance(q, dict) or ACCOUNT_PART_KEYS - q.keys() for q in parts):
            m.append(f"{name}.json: needs \"parts\": 3 to 6 objects with name, mechanism, rule")
            continue
        if not isinstance(cells, list) or any(not isinstance(c, dict) or {"name", "gap"} - c.keys() for c in cells):
            m.append(f"{name}.json: needs \"cells\": objects with name and gap (and \"null\": true on the null cell)")
            continue
        if not isinstance(claims, list) or any(not isinstance(k, dict) or {"cell", "shares", "item"} - k.keys() for k in claims):
            m.append(f"{name}.json: needs \"known_claim\": a list (may be empty) of {{cell, shares, item}}")
            continue
        if not isinstance(ev, dict) or {"rows", "n", "grader"} - ev.keys():
            m.append(f"{name}.json: needs \"evidence\": {{rows, n, grader}}, one evidence set for every cell")
        names = [q["name"] for q in parts]
        if len(set(names)) != len(names) or "unassigned" in names:
            m.append(f"{name}.json: part names must be distinct and not \"unassigned\" (that part is implied): {names}")
        nulls = [c["name"] for c in cells if c.get("null")]
        claimed = {k["cell"] for k in claims}
        model = [c["name"] for c in cells if not c.get("null") and c["name"] not in claimed]
        if len(nulls) != 1 or len(model) < 2:
            m.append(f"{name}.json: needs exactly one null cell (\"null\": true) and 2 or more predicted model cells; "
                     f"null {nulls}, predicted {model}")
        offline = [q for q in t.get("predictions", []) if "recipe" in q]
        if bad := [i for i, q in enumerate(offline, 1) if q.get("cell") not in [c["name"] for c in cells]]:
            m.append(f"{name}.json: offline predictions {bad} need \"cell\", one of the cells' names")
        for c in cells:
            role = "fit" if c["name"] in claimed else "share"
            mine = [q for q in offline if q.get("cell") == c["name"] and q.get("role") in ("share", "fit")]
            if any(q.get("role") != role for q in mine):
                m.append(f"{name}.json: cell {c['name']!r} takes role {role!r} only (a claimed budget is fitted, not predicted)")
            elif sorted(q.get("part", "") for q in mine) != sorted(names + ["unassigned"]):
                m.append(f"{name}.json: cell {c['name']!r} needs exactly one {role} prediction for each part and for \"unassigned\"")
            elif all(number(q.get("value")) for q in mine) and abs(sum(q["value"] for q in mine) - 1) > 0.02:
                m.append(f"{name}.json: the {role} values of cell {c['name']!r} sum to {sum(q['value'] for q in mine):.3f}, not 1")
            if c["name"] in model and not str(c.get("moves", "")).strip():
                m.append(f"{name}.json: cell {c['name']!r} needs \"moves\": which shares move against the null and the claimed cell, which way, and why")
            if c["name"] in model and any(not number(q.get("vs_null")) for q in mine if not q.get("by_construction")):
                m.append(f"{name}.json: every share of cell {c['name']!r} not 0 by construction needs \"vs_null\" (its difference from the null cell's share)")
            if sum(q.get("role") == "net" and q.get("cell") == c["name"] for q in offline) != 1:
                m.append(f"{name}.json: cell {c['name']!r} needs one \"net\" prediction (RL-only minus base-only problems)")
        scored_shares = [q for q in offline if q.get("role") == "share" and q.get("cell") in model and not q.get("by_construction")]
        if len(scored_shares) < 6:
            m.append(f"{name}.json: needs 6 or more share predictions, not 0 by construction, in the predicted model cells; has {len(scored_shares)}")
        cross = [q for q in offline if q.get("role") == "cross"]
        if len(cross) < 2 or any(q.get("part") not in names + ["unassigned"] for q in cross):
            m.append(f"{name}.json: needs at least 2 cross-predictions (\"role\": \"cross\"), each naming a part")
    return msgs


def account(folder):
    nn = round_number(folder)
    name = f"r{nn}-account"
    dropped = json.loads((folder / "dropped.json").read_text()) if (folder / "dropped.json").exists() else {}
    if (folder / "theories" / f"{name}.json").exists() or name in dropped:
        return print(f"skip account: {name} exists or was dropped")
    graveyard = json.loads((folder / "graveyard.json").read_text()) if (folder / "graveyard.json").exists() else {}
    (folder / "theories").mkdir(exist_ok=True)
    carried = {f"carried/{p.name}": json.dumps({"theory": json.loads(p.read_text()), "computed_tests": [
        q for q in json.loads((folder / "tests" / p.name).read_text())["predictions"] if q["measured"] is not None]
        if (folder / "tests" / p.name).exists() else []}, indent=1)
        for p in sorted((folder / "theories").glob("*.json")) if not p.stem.startswith(f"r{nn}-")}
    inputs = {"DIRECTION.md": ROOT / "DIRECTION.md", "before.jsonl": folder / "before.jsonl", "inventory.md": folder / "inventory.md",
              "external.md": folder / "external.md", "graveyard.json": graveyard_input(folder),
              "facts.json": facts_input(folder),
              "incumbent_account.json": folder / "incumbent_account.json" if (folder / "incumbent_account.json").exists() else "[]\n",
              **(carried or {"carried/none.txt": "No theory is carried from earlier rounds.\n"})}

    def valid(d):
        return None if isinstance(json.loads((d / "result.json").read_text()), dict) else "not a JSON object"

    run([job("account", name, inputs, {"result.json": folder / "drafts" / f"{name}.json"}, valid, theory=name)], folder)
    drafts = {name: json.loads((folder / "drafts" / f"{name}.json").read_text())}
    fix_inputs = {"before.jsonl": folder / "before.jsonl", "external.md": folder / "external.md",
                  "inventory.md": folder / "inventory.md", "graveyard.json": graveyard_input(folder)}
    finish_theories(folder, [name], drafts, lambda ds: check_account(folder, ds, set(graveyard)), fix_inputs, dropped)


def offline_predictions(theory):
    return [{"k": k, **p} for k, p in enumerate(theory["predictions"], 1) if "recipe" in p]


def carried_tests(folder, name):
    """A survivor's tests carried by `standing` from the round that computed and scored them."""
    path = folder / "tests" / f"{name}.json"
    return path.exists() and "carried_from" in json.loads(path.read_text())


def null_tests(folder):
    blind = [{"id": f"{p.stem}:p{q['k']}", "experiment": q["experiment"], "recipe": q["recipe"], "unit": q["unit"]}
             for p in sorted((folder / "theories").glob("*.json")) if not carried_tests(folder, p.stem) and in_scope(p.stem)
             for q in offline_predictions(json.loads(p.read_text())) if scored(q)]
    if not blind:
        return print("null_tests: no offline prediction")
    write(folder / "tests_blind.jsonl", blind)
    ids = [b["id"] for b in blind]
    run([job("null_tests", f"nulltest-{k}", {"before.jsonl": folder / "before.jsonl", "inventory.md": folder / "inventory.md",
                                              "tests_blind.jsonl": folder / "tests_blind.jsonl", "facts.json": facts_input(folder)},
             {"predictions.jsonl": folder / "predictions" / f"nulltest-{k}.jsonl"},
             lambda d: interval_rows(d / "predictions.jsonl", ids, exact=True)) for k in (1, 2)], folder)


def null(folder):
    ids = target_ids(folder)
    run([job("null", f"null-{k}", {"before.jsonl": folder / "before.jsonl", "targets_blind.jsonl": folder / "targets_blind.jsonl"},
             {"predictions.jsonl": folder / "predictions" / f"null-{k}.jsonl"},
             lambda d: interval_rows(d / "predictions.jsonl", ids, exact=True)) for k in (1, 2)], folder)


def claims(folder, names=None):
    ids = target_ids(folder)
    run([job("claims", p.stem, {"theory.json": p, "before.jsonl": folder / "before.jsonl", "targets_blind.jsonl": folder / "targets_blind.jsonl"},
             {"claims.jsonl": folder / "claims" / f"{p.stem}.jsonl"},
             lambda d: interval_rows(d / "claims.jsonl", ids, exact=False), rule=FREE_RULE)
         for p in sorted((folder / "theories").glob("*.json")) if names is None or p.stem in names], folder)


def log_density(x, c):
    """Log density at x of the normal a claim stands for: mean value, sd = width of its 90 % interval / 3.29."""
    sd = max((c["high"] - c["low"]) / 3.29, 0.01 * max(abs(c["value"]), 1))
    return -0.5 * ((x - c["value"]) / sd) ** 2 - math.log(sd) - 0.5 * math.log(2 * math.pi)


def gain_rows(claims, measured, nulls):
    rows = []
    for c in claims:
        if c["id"] not in measured:
            continue
        x, n = measured[c["id"]], [null[c["id"]] for null in nulls]
        a, b = (log_density(x, p) for p in n)
        log_null = max(a, b) + math.log(0.5 * (1 + math.exp(-abs(a - b))))  # log of the equal mixture of the two nulls
        gain = capped(clip3(log_density(x, c) - log_null), x, c)
        rows.append({"id": c["id"], "measured": x, "value": c["value"], "low": c["low"], "high": c["high"],
                     "nulls": [{k: p[k] for k in ("value", "low", "high")} for p in n], "gain": round(gain, 4)})
    return rows


def bootstrap(gains):
    """90 % interval of the total gain: 2,000 resamples of the claims, seed 0."""
    if not gains:
        return [0.0, 0.0]
    rng = random.Random(0)
    totals = sorted(sum(rng.choice(gains) for _ in gains) for _ in range(2000))
    return [round(totals[100], 3), round(totals[1899], 3)]


def score(folder):
    exposed = json.loads((folder / "exposed.json").read_text())["items"] if (folder / "exposed.json").exists() else []
    measured = {t["id"]: t["value"] for t in read(folder / "targets.jsonl") if t["item"] not in exposed}
    nulls = [{p["id"]: p for p in read(folder / "predictions" / f"null-{k}.jsonl")} for k in (1, 2)]
    theories = {}
    for p in sorted((folder / "theories").glob("*.json")):
        name = p.stem
        rows = gain_rows(read(folder / "claims" / f"{name}.jsonl"), measured, nulls)
        gains = [r["gain"] for r in rows]
        t = {"claims": len(rows), "total_gain": round(sum(gains), 3), "mean_gain": round(sum(gains) / len(gains), 3) if gains else 0.0,
             "interval": bootstrap(gains)}
        t["candidate"] = t["interval"][0] > 0
        rev_path = folder / "claims" / f"{name}.rev.jsonl"
        reversal = None
        if rev_path.exists():
            rev_rows = gain_rows(read(rev_path), measured, nulls)
            reversal = {"claims": len(rev_rows), "total_gain": round(sum(r["gain"] for r in rev_rows), 3), "rows": rev_rows}
        state = ("fails" if not t["candidate"] else "candidate" if reversal is None
                 else "passes" if t["total_gain"] > reversal["total_gain"] else "fails: reversal as good")
        tests = None
        if (folder / "tests" / f"{name}.json").exists():
            preds = json.loads((folder / "tests" / f"{name}.json").read_text())["predictions"]
            tests = {"inside": sum(q["inside"] is True for q in preds), "outside": sum(q["inside"] is False for q in preds),
                     "not computed": sum(q["inside"] is None for q in preds), "refuted": any(q["refuted_by_met"] for q in preds)}
            if tests["refuted"]:
                state = "refuted"
        theories[name] = {**t, "state": state, "reversal": reversal, "tests": tests, "rows": rows}
    (folder / "metrics_v3.json").write_text(json.dumps({"targets": len(measured), "exposed_items": exposed, "theories": theories}, indent=1) + "\n")
    print(f"{len(measured)} targets scored ({len(exposed)} exposed items left out). Gain in nats against the two no-theory readers.")
    print(f"{'theory':22} {'claims':>6} {'total':>7} {'mean':>6}  {'90% interval':>16} {'reversal':>8}  tests in/out  state")
    for name, t in sorted(theories.items(), key=lambda kv: -kv[1]["total_gain"]):
        rev = f"{t['reversal']['total_gain']:8.2f}" if t["reversal"] else f"{'':>8}"
        tests = f"{t['tests']['inside']}/{t['tests']['outside']}" if t["tests"] else ""
        print(f"{name:22} {t['claims']:6} {t['total_gain']:7.2f} {t['mean_gain']:6.2f}  [{t['interval'][0]:6.2f}, {t['interval'][1]:6.2f}] {rev}  {tests:>12}  {t['state']}")


def candidates(folder):
    return [n for n, t in json.loads((folder / "metrics_v3.json").read_text())["theories"].items() if t["candidate"]]


def strike_rows(folder, name):
    """Version 4: the advocate's held-out claims; a strike is a claim both readers contradict that misses its own interval."""
    exposed = json.loads((folder / "exposed.json").read_text())["items"] if (folder / "exposed.json").exists() else []
    measured = {t["id"]: t["value"] for t in read(folder / "targets.jsonl") if t["item"] not in exposed}
    nulls = [{p["id"]: p for p in read(folder / "predictions" / f"null-{k}.jsonl")} for k in (1, 2)]
    rows = gain_rows(read(folder / "claims" / f"{name}.jsonl"), measured, nulls)
    for r in rows:
        divergent = all(not r["low"] <= n["value"] <= r["high"] for n in r["nulls"])
        r["strike"] = divergent and not r["low"] <= r["measured"] <= r["high"]
    return rows


def overlaps(q):
    """The measured 90 % interval, when the script printed one, overlaps the predicted [low, high]."""
    iv = q.get("interval")
    return iv is not None and iv[0] <= q["high"] and q["low"] <= iv[1]


def scored(q):
    """An account's fit to a claimed budget and a share that is 0 by construction are computed but not scored."""
    return q.get("role") != "fit" and not q.get("by_construction")


def replication(folder, name, kind=""):
    """{k: item} from replication/<name>[.duel].json: the independent recomputation of the decisive numbers."""
    path = folder / "replication" / f"{name}{kind}.json"
    return {i["k"]: i for i in json.loads(path.read_text())["items"]} if path.exists() else {}


def score_tests(folder):
    """Version 4 score, metrics_v4.json: each theory's computed offline predictions against its intervals, its refuting
    conditions and the two no-theory test readers; held-out strikes and the review can only remove a theory."""
    nulls = [{p["id"]: p for p in read(folder / "predictions" / f"nulltest-{k}.jsonl")} for k in (1, 2)] \
        if (folder / "predictions" / "nulltest-1.jsonl").exists() else None
    gpu_all = json.loads((folder / "gpu_tests.json").read_text()) if (folder / "gpu_tests.json").exists() else []
    theories = {}
    for p in sorted((folder / "theories").glob("*.json")):
        name = p.stem
        path = folder / "tests" / f"{name}.json"
        data = json.loads(path.read_text()) if path.exists() else {"predictions": []}
        repl = replication(folder, name)
        # a fit, a share that is 0 by construction, or a number its replication does not reproduce is not scored
        aside = [{"k": q["k"], "measured": q["measured"], "replication": repl.get(q["k"], {}).get("replicated"),
                  "not_scored": "a fit of the account's rules to a cell whose budget a board item claims" if q.get("role") == "fit"
                  else "0 by construction" if q.get("by_construction") else "differs from its replication; left out until a person resolves it"}
                 for q in data["predictions"] if not scored(q) or repl.get(q["k"], {}).get("status") == "differs"]
        preds = [q for q in data["predictions"] if q["k"] not in {a["k"] for a in aside}]
        computed = [q for q in preds if q["measured"] is not None]
        for q in computed:  # outside only when the measured 90 % interval misses the predicted one; else within noise
            q["within_noise"] = not q["inside"] and overlaps(q)
            q["outside"] = not q["inside"] and not q["within_noise"]
        met = [q for q in preds if q["refuted_by_met"] and (q["measured"] is None or not overlaps(q))]
        if "carried_from" in data:  # computed and scored in that round: its rows, gains against that round's readers
            rows = data["rows"]
        else:
            rows = gain_rows([{"id": f"{name}:p{q['k']}", "value": q["value"], "low": q["low"], "high": q["high"]} for q in computed],
                             {f"{name}:p{q['k']}": q["measured"] for q in computed}, nulls) if computed else []
            for r, q in zip(rows, computed):
                r.update(k=q["k"], inside=q["inside"], within_noise=q["within_noise"], n=q.get("n"), interval=q.get("interval"),
                         refuted_by=q["refuted_by"], refuted_by_met=q in met)
            rows += [{"k": q["k"], "not_computable": q["not_computable"]} if q["not_computable"] else
                     {"k": q["k"], "refuted_without_number": q["refuted_by"]} for q in preds if q["measured"] is None]
            for r in rows:
                r["replication"] = repl.get(r["k"], {}).get("status")
            rows += aside
        outside = sum(q["outside"] for q in computed)
        reasons = [f"p{q['k']} {q['experiment'][:80]}: measured {q['measured']}, predicted {q['value']} [{q['low']}, {q['high']}]; "
                   f"refuting condition met: {q['refuted_by'][:120]}" for q in met]
        if outside >= 2:
            reasons.append(f"{outside} of {len(computed)} computed predictions outside their 90 % intervals beyond noise")
        total = round(sum(r["gain"] for r in rows if "gain" in r), 3)
        # a win the readers did not expect: measured inside the theory's interval, every reader's centre outside it
        unexpected = [r["k"] for r in rows if "gain" in r and r["inside"]
                      and all(not r["low"] <= c["value"] <= r["high"] for c in r["nulls"])]
        state = "refuted" if reasons else "untested" if len(computed) < 2 else "survives" if total > 0 and unexpected else "no gain"
        note = "total gain above 0 but no computed prediction won where the readers' centres were outside its interval" \
            if state == "no gain" and total > 0 else ""
        held = strike_rows(folder, name) if (folder / "claims" / f"{name}.jsonl").exists() else []
        if (strikes := sum(r["strike"] for r in held)) >= 2:
            state = "refuted"
            reasons.append(f"{strikes} held-out strikes (claims both readers contradicted that missed their interval)")
        review = folder / "reviews" / f"{name}.json"
        verdict = json.loads(review.read_text())["verdict"] if review.exists() else ""
        if verdict.startswith(("refuted", "published")) and json.loads(review.read_text()).get("about") != "rival" \
                and ("-account" not in name or state == "survives"):  # a review of a failed account changes nothing
            state = verdict.split(":")[0]
            reasons.append(f"review: {verdict[:200]}")
        # GPU tests (standing): its measured experiments, scored against the other side of its pair; not in total_gain
        gpu = [{"id": g["id"], "measured": g["measured"], "n": g.get("n"), "artifact": g["artifact"], **g["sides"][name],
                "other": next({"name": s, **v} for s, v in g["sides"].items() if s != name)} for g in gpu_all if name in g["sides"]]
        theories[name] = {"carried_from": data.get("carried_from"),
                          "offline": len(preds), "not_scored": len(aside), "computed": len(computed), "inside": sum(q["inside"] for q in computed),
                          "within_noise": sum(q["within_noise"] for q in computed), "outside": outside,
                          "total_gain": total, "unexpected_wins": unexpected, "heldout_claims": len(held), "strikes": strikes,
                          "state": state, "note": note, "reasons": reasons, "verdict": verdict, "rows": rows, "heldout_rows": held,
                          "gpu_tests": gpu, "gpu_gain": round(sum(g["gain"] for g in gpu), 3), "gpu_strikes": sum(g["strike"] for g in gpu)}
        if "promoted_from" in json.loads(p.read_text()):  # its rows are the duel it won (the beaten theory as reader), not tests
            theories[name] |= {"carried_duel": {"from": data["carried_from"], "gain": total, "tests": len(computed)},
                               "offline": 0, "computed": 0, "inside": 0, "within_noise": 0, "outside": 0, "total_gain": 0}
    (folder / "metrics_v4.json").write_text(json.dumps({"theories": theories}, indent=1) + "\n")
    print("Offline tests: computed predictions against their 90 % intervals; gain in nats against the two no-theory test readers. "
          "Outside counts only when the measured 90 % interval misses the predicted one.")
    print(f"{'theory':16} {'computed':>9} {'in/noise/out':>12} {'gain':>7} {'strikes':>8}  state")
    for name, t in sorted(theories.items(), key=lambda kv: -kv[1]["total_gain"]):
        print(f"{name:16} {t['computed']:>4} of {t['offline']:<2} {str(t['inside']) + '/' + str(t['within_noise']) + '/' + str(t['outside']):>12} {t['total_gain']:7.2f} "
              f"{str(t['strikes']) + ' of ' + str(t['heldout_claims']) if t['heldout_claims'] else '':>8}  {t['state']}"
              f"{', tests carried from ' + t['carried_from'] if t['carried_from'] else ''}{': ' + t['note'] if t['note'] else ''}"
              + (f"; carried duel win, {t['carried_duel']['gain']:+.2f} nats over {t['carried_duel']['tests']} tests (not counted above)"
                 if "carried_duel" in t else ""))
        for r in t["rows"]:
            if "not_scored" in r:
                again = "" if r["replication"] is None else f" (replication: {r['replication']})"
                print(f"    p{r['k']}: measured {r['measured']}, not scored: {r['not_scored']}{again}")
            elif "not_computable" in r:
                print(f"    p{r['k']}: not computable: {r['not_computable'][:110]}")
            elif "refuted_without_number" in r:
                print(f"    p{r['k']}: no number; refuting condition met: {r['refuted_without_number'][:100]}")
            else:
                where = "inside" if r["inside"] else "outside, within noise" if r.get("within_noise") else "outside"
                noise = f" (n {r['n']}, 90 % [{r['interval'][0]:g}, {r['interval'][1]:g}])" if r.get("interval") else ""
                readers = " and ".join(f"{c['value']:g}" for c in r["nulls"])
                print(f"    p{r['k']}: measured {r['measured']:g}{noise}, predicted {r['value']:g} [{r['low']:g}, {r['high']:g}] "
                      f"{where}, readers {readers}, "
                      f"gain {r['gain']:+.2f}{', refuting condition met' if r['refuted_by_met'] else ''}"
                      f"{', a win the readers did not expect' if r['k'] in t['unexpected_wins'] else ''}"
                      f"{', readers had the same number' if all(abs(c['value'] - r['value']) <= max(0.02 * abs(r['value']), 0.01) for c in r['nulls']) else ''}"
                      f"{', replicated' if r.get('replication') == 'replicated' else ''}")
        for g in t["gpu_tests"]:
            o = g["other"]
            print(f"    GPU test {g['id']}: measured {g['measured']:g} (n {g['n']}), predicted {g['value']:g} [{g['low']:g}, {g['high']:g}], "
                  f"{o['name']} {o['value']:g} [{o['low']:g}, {o['high']:g}], gain {g['gain']:+.2f}{', strike' if g['strike'] else ''}")
    total = {k: sum(t[k] for t in theories.values()) for k in ("offline", "computed", "inside", "within_noise", "outside")}
    failed = sum(str(r.get("not_computable")).startswith("not computed: script failed") for t in theories.values() for r in t["rows"])
    repl_failed = sum(i["status"] == "not replicated" for p in (folder / "replication").glob("*.json")
                      for i in json.loads(p.read_text())["items"])
    print(f"Round: {total['computed']} of {total['offline']} offline predictions computed, {total['inside']} inside, "
          f"{total['within_noise']} outside within noise, {total['outside']} outside; "
          f"{failed} test scripts and {repl_failed} replication scripts failed (not computed)" + "".join(
              f"; {n}: carried duel win, {t['carried_duel']['gain']:+.2f} nats over {t['carried_duel']['tests']} tests, not counted"
              for n, t in theories.items() if "carried_duel" in t))


def heldout(folder):
    nn, theories = round_number(folder), json.loads((folder / "metrics_v4.json").read_text())["theories"]
    names = [n for n, t in theories.items() if in_scope(n) and (t["state"] == "survives" or (not n.startswith(f"r{nn}-") and t["state"] == "untested"))]
    if not names:
        return print("heldout: no theory survives the offline tests; targets, null and claims are skipped")
    print(f"  held-out filter for {names}")
    targets(folder)
    null(folder)
    claims(folder, set(names))
    score_tests(folder)


def reverse(folder):
    names = candidates(folder)
    if not names:
        return print("reverse: no candidate")
    run([job("reverse", n, {"theory.json": folder / "theories" / f"{n}.json"}, {"reversed.json": folder / "reversed" / f"{n}.json"},
             lambda d: None if "statement" in json.loads((d / "reversed.json").read_text()) else "no statement") for n in names], folder)
    jobs = []
    for n in names:
        ids = [c["id"] for c in read(folder / "claims" / f"{n}.jsonl")]
        rule = ("Claim exactly these targets, each once, and no others: " + ", ".join(ids) + ". For each, say what the "
                "mechanism as written implies; where it implies little, give your best value with an honest interval.")
        jobs.append(job("reverse-claims", n, {"theory.json": folder / "reversed" / f"{n}.json", "before.jsonl": folder / "before.jsonl",
                                              "targets_blind.jsonl": folder / "targets_blind.jsonl"},
                        {"claims.jsonl": folder / "claims" / f"{n}.rev.jsonl"},
                        lambda d, ids=ids: interval_rows(d / "claims.jsonl", ids, exact=True), rule=rule))
    run(jobs, folder)
    score(folder)


THEORY_TESTS = ("$out/theory.json is a theory. $out/offline.json lists its offline predictions, each with k, experiment, "
                "recipe, value, low, high and refuted_by.")
DUEL_TESTS = ("$out/offline.json lists offline computations that decide between two explanations of the same numbers, "
              "each with k, experiment, recipe and unit. You are not told the explanations or what either predicts. "
              "refuted_by is null for every entry, so every script prints \"refuted_by_met\": false.")


def script_job(folder, name, offline, inputs, dest, what):
    """A test writer (repository, laptop only): one script per entry of offline, written into dest, none run."""
    def valid(d):
        missing = [q["k"] for q in offline if not (d / "tests" / name / f"p{q['k']}.py").exists()]
        if missing:
            return f"no script for predictions {missing}"
        notes = d / "tests" / name / "notes.json"
        return None if notes.exists() and isinstance(json.loads(notes.read_text()), list) else f"no list in {notes}"

    j = job("test", name, {**inputs, "offline.json": json.dumps(offline, indent=1)}, {f"tests/{name}": dest}, valid,
            mode="repo", theory=name, inventory=(folder / "inventory.md").resolve(), profile=AWS_PROFILE,
            run_command=" ".join(TEST_PYTHON), what=string.Template(what).substitute(out=tmp() / "test" / name))
    return j


SCRIPT_SECONDS = 600  # one test, duel or replication script


def run_scripts(folder, label, offline, scripts):
    """Run each script in `scripts` once in the test environment; one result per entry of offline."""
    notes = {e["k"]: e["note"] for e in json.loads((scripts / "notes.json").read_text())}
    results = []
    for q in offline:
        script, log = scripts / f"p{q['k']}.py", scripts / f"p{q['k']}.out.txt"
        try:  # a script that times out or exits non-zero is recorded as not computed for its prediction; the round goes on
            p = subprocess.run([*TEST_PYTHON, str(script.resolve())], cwd=ROOT, capture_output=True, text=True, timeout=SCRIPT_SECONDS,
                               env={**os.environ, "AWS_PROFILE": AWS_PROFILE, "PYTHONPATH": str(ROOT)})
            log.write_text(p.stdout + p.stderr)
            failed = p.returncode and f"exit {p.returncode}"
        except subprocess.TimeoutExpired:
            log.write_text(f"timeout after {SCRIPT_SECONDS} s\n")
            failed = f"timeout after {SCRIPT_SECONDS} s"
        if failed:
            reason = f"not computed: script failed ({failed}); output in {log.relative_to(folder)}"
            results.append({**q, "script": str(script.relative_to(folder)), "measured": None, "n": None, "interval": None,
                            "interval_kind": "none", "inside": None, "refuted_by_met": False, "alt_measured": None,
                            "not_computable": reason, "script_failed": failed, "note": notes.get(q["k"], ""), "example_row": None})
            print(f"  {label} p{q['k']}: {reason}")
            continue
        out = json.loads(p.stdout.strip().splitlines()[-1])
        m, met = out["measured"], bool(out["refuted_by_met"])
        if m is None and not out.get("not_computable") and not met:
            sys.exit(f"{script} printed no number, no not_computable reason and no refutation; output in {script.with_suffix('.out.txt')}")
        results.append({**q, "script": str(script.relative_to(folder)), "measured": m,
                        "n": out.get("n"), "interval": out.get("interval"), "interval_kind": out.get("interval_kind", "none"),
                        "inside": None if m is None or "low" not in q else q["low"] <= m <= q["high"],
                        "refuted_by_met": met, "alt_measured": out.get("alt_measured"),
                        "not_computable": out.get("not_computable") if m is None and not met else None,
                        "note": notes.get(q["k"], ""), "example_row": out.get("example_row")})
        print(f"  {label} p{q['k']}: " + (f"no number; refuting condition met: {str(q.get('refuted_by'))[:100]}" if m is None and met
              else f"not computable: {str(out.get('not_computable'))[:100]}" if m is None else
              f"measured {m} (n {out.get('n')}, 90 % {out.get('interval')})" + (f", predicted {q['value']} [{q['low']}, {q['high']}], refuting condition met: {met}" if "value" in q else "")))
    return results


def test(folder):
    """Versions 4 and 5: every theory's offline predictions; version 3: the candidates'. The model writes one script per
    prediction and runs none; each script runs here once."""
    names = [p.stem for p in sorted((folder / "theories").glob("*.json")) if in_scope(p.stem)] if args.version >= 4 else candidates(folder)
    jobs = []
    for n in names:
        if (folder / "tests" / f"{n}.json").exists():
            print(f"  skip test/{n}: tests/{n}.json exists")
            continue
        offline = offline_predictions(json.loads((folder / "theories" / f"{n}.json").read_text()))
        if not offline:
            print(f"  test/{n}: no offline prediction")
            (folder / "tests").mkdir(exist_ok=True)
            (folder / "tests" / f"{n}.json").write_text(json.dumps({"theory": n, "predictions": []}, indent=1) + "\n")
            continue
        jobs.append((n, offline, script_job(folder, n, offline, {"theory.json": folder / "theories" / f"{n}.json"},
                                            folder / "tests" / n, THEORY_TESTS)))
    run([j for _, _, j in jobs], folder, workers=6)
    for n, offline, _ in jobs:
        results = run_scripts(folder, f"test/{n}", offline, folder / "tests" / n)
        (folder / "tests" / f"{n}.json").write_text(json.dumps({"theory": n, "predictions": results}, indent=1) + "\n")
    (score_tests if args.version >= 4 else score)(folder)


# ---- version 5: the duel against the strongest rival ----

RIVAL_TEST_KEYS = {"experiment", "recipe", "unit", "value", "low", "high", "theory_should_say"}
DECIDES = 2.0  # nats: a duel total at or beyond +-2 decides; between, the theory and its rival are not separated


def survivors(folder):
    """The theories the duel and the review take: up to 3 survivors of metrics_v4.json, largest total gain (or carried
    duel gain) first."""
    theories = json.loads((folder / "metrics_v4.json").read_text())["theories"]
    return sorted((n for n, t in theories.items() if t["state"] == "survives" and in_scope(n)),
                  key=lambda n: -theories[n]["total_gain"] - theories[n].get("carried_duel", {}).get("gain", 0))[:3]


def computed_tests(folder, name):
    return [{k: q[k] for k in ("k", "experiment", "recipe", "unit", "measured", "value", "low", "high") if k in q}
            for q in json.loads((folder / "tests" / f"{name}.json").read_text())["predictions"] if q["measured"] is not None]


def rfile(folder, name, turn, kind=""):
    """rivals/<name>[.turn2][.defend|.tests].json; kind "" is the rival's file of that turn."""
    return folder / "rivals" / f"{name}{'.turn2' if turn == 2 else ''}{kind}.json"


def rival_tests(folder, name, turn, full=False):
    """A turn's rival tests numbered on from the first turn's (k = 1, 2, ...); without the rival's numbers and reasons
    unless full."""
    first = len(json.loads(rfile(folder, name, 1).read_text())["tests"]) if turn == 2 else 0
    tests = json.loads(rfile(folder, name, turn).read_text())["tests"]
    return [{"k": first + i, **(t if full else {k: t[k] for k in ("experiment", "recipe", "unit")})} for i, t in enumerate(tests, 1)]


def rival_valid(d, turn, items):
    r = json.loads((d / "rival.json").read_text())
    if not isinstance(r, dict) or not isinstance(r.get("statement"), str) or not isinstance(r.get("tests"), list):
        return "need a JSON object with \"statement\" (a string) and \"tests\" (a list)"
    m = intervention_messages(r, items) if args.version >= 7 else []
    if turn == 2 and r.get("no_offline_test") is not None:
        g = r["no_offline_test"]
        if not (isinstance(g, dict) and isinstance(g.get("reason"), str) and isinstance(g.get("gpu_experiment"), str)):
            return "\"no_offline_test\" must be null or {\"reason\": ..., \"gpu_experiment\": ...}"
        if not r["tests"]:
            return "; ".join(m) or None
    if not 2 <= len(r["tests"]) <= 4:
        m.append(f"need 2 to 4 tests, got {len(r['tests'])}")
    for i, t in enumerate(r["tests"], 1):
        if RIVAL_TEST_KEYS - t.keys():
            m.append(f"test {i} misses keys {sorted(RIVAL_TEST_KEYS - t.keys())}")
        elif not (all(number(t[k]) for k in ("value", "low", "high")) and t["low"] <= t["value"] <= t["high"]):
            m.append(f"test {i} needs numbers with low <= value <= high")
        elif not (isinstance(t["recipe"], str) and t["recipe"].strip()):
            m.append(f"test {i} needs a recipe")
    return "; ".join(m) or None


def rival_inputs(folder, name):
    return {"theory.json": folder / "theories" / f"{name}.json", "tests.json": json.dumps(computed_tests(folder, name), indent=1),
            "DIRECTION.md": ROOT / "DIRECTION.md", "before.jsonl": folder / "before.jsonl", "inventory.md": folder / "inventory.md", "external.md": folder / "external.md",
            "facts.json": facts_input(folder)}


def rival(folder):
    names = survivors(folder)
    if not names:
        return print("rival: no surviving theory")
    items = item_ids(folder)
    run([job("rival", n, rival_inputs(folder, n), {"rival.json": rfile(folder, n, 1)}, lambda d: rival_valid(d, 1, items), theory=n)
         for n in names], folder)
    for n in names:
        print(f"  {n}: rival: {json.loads(rfile(folder, n, 1).read_text())['statement'][:200]}")


def same_prediction(test, mine):
    """The defender's centre lies inside the rival's interval: the test cannot separate the two."""
    return test["low"] <= mine["value"] <= test["high"]


def rival2(folder):
    """The rival's second turn, only where fewer than 2 first-turn tests separate it from the defender's numbers."""
    jobs = []
    for n in survivors(folder):
        if not rfile(folder, n, 1, ".defend").exists() or rfile(folder, n, 2).exists():
            continue
        mine = {d["k"]: d for d in json.loads(rfile(folder, n, 1, ".defend").read_text())}
        tests = rival_tests(folder, n, 1, full=True)
        apart = sum(not same_prediction(t, mine[t["k"]]) for t in tests)
        print(f"  {n}: {apart} of {len(tests)} first-turn tests put the defender's centre outside the rival's interval")
        if apart >= 2:
            continue
        held = [{"k": t["k"], "experiment": t["experiment"], **{k: mine[t["k"]][k] for k in ("value", "low", "high", "why")}} for t in tests]
        j = job("rival", f"{n}.turn2", {**rival_inputs(folder, n), "first_turn.json": rfile(folder, n, 1),
                                        "advocate.json": json.dumps(held, indent=1)},
                {"rival.json": rfile(folder, n, 2)}, lambda d: rival_valid(d, 2, item_ids(folder)), theory=n)
        j["prompt"] += "\n\n" + prompt("rival2")
        jobs.append(j)
    if not jobs:
        return print("rival2: no second turn needed")
    run(jobs, folder)


def defend(folder):
    jobs = []
    for n in survivors(folder):
        for turn in (1, 2):
            if not rfile(folder, n, turn).exists() or not (tests := rival_tests(folder, n, turn)):
                continue
            ks = [t["k"] for t in tests]

            def valid(d, ks=ks):
                rows = json.loads((d / "defend.json").read_text())
                if not isinstance(rows, list) or sorted(r.get("k") for r in rows) != ks:
                    return f"need a JSON list with one entry for each k in {ks}"
                bad = [r["k"] for r in rows if not (all(number(r.get(k)) for k in ("value", "low", "high")) and r["low"] <= r["value"] <= r["high"])]
                return f"value outside [low, high] or not a number for k {bad}" if bad else None

            jobs.append(job("defend", f"{n}.turn{turn}", {"theory.json": folder / "theories" / f"{n}.json",
                                                         "tests.json": json.dumps(tests, indent=1),
                                                         "before.jsonl": folder / "before.jsonl", "inventory.md": folder / "inventory.md",
                                                         "facts.json": facts_input(folder)},
                            {"defend.json": rfile(folder, n, turn, ".defend")}, valid))
    if not jobs:
        return print("defend: no rival")
    run(jobs, folder)


def duel_test(folder):
    jobs = []
    for n in survivors(folder):
        for turn in (1, 2):
            if not rfile(folder, n, turn).exists() or not (tests := rival_tests(folder, n, turn)):
                continue
            if rfile(folder, n, turn, ".tests").exists():
                print(f"  skip duel_test/{n} turn {turn}: {rfile(folder, n, turn, '.tests').name} exists")
                continue
            offline, scripts = [{**t, "refuted_by": None} for t in tests], rfile(folder, n, turn).with_suffix("")
            jobs.append((n, turn, offline, scripts, script_job(folder, f"duel-{scripts.name}", offline, {}, scripts, DUEL_TESTS)))
    run([j[-1] for j in jobs], folder, workers=6)
    for n, turn, offline, scripts, _ in jobs:
        results = run_scripts(folder, f"duel_test/{n} turn {turn}", offline, scripts)
        rfile(folder, n, turn, ".tests").write_text(json.dumps({"theory": n, "turn": turn, "tests": results}, indent=1) + "\n")


def score_duel(folder):
    """metrics_v5.json: on each computed rival test of both turns, gain = log density of the theory's (defend)
    prediction minus log density of the rival's prediction at the computed value, clipped to [-3, 3] nats; a side
    outside its own interval gains at most 0 (pair_gain)."""
    theories = {}
    for n in survivors(folder):
        if not rfile(folder, n, 1, ".tests").exists():
            continue
        rows = []
        gpu = json.loads(rfile(folder, n, 2).read_text()).get("no_offline_test") if rfile(folder, n, 2).exists() else None
        repl = replication(folder, n, ".duel")
        for turn in (1, 2):
            if not rfile(folder, n, turn, ".tests").exists():
                continue
            tests = {t["k"]: t for t in rival_tests(folder, n, turn, full=True)}
            mine = {d["k"]: d for d in json.loads(rfile(folder, n, turn, ".defend").read_text())}
            for q in json.loads(rfile(folder, n, turn, ".tests").read_text())["tests"]:
                t, d = tests[q["k"]], mine[q["k"]]
                row = {"k": q["k"], "turn": turn, "experiment": q["experiment"], "measured": q["measured"],
                       "n": q.get("n"), "interval": q.get("interval"),
                       "theory": {k: d[k] for k in ("value", "low", "high")}, "rival": {k: t[k] for k in ("value", "low", "high")},
                       "same_prediction": same_prediction(t, d), "theory_should_say": t["theory_should_say"]}
                if q["measured"] is None:
                    row["not_computable"] = q["not_computable"]
                else:
                    row["gain"] = round(pair_gain(q["measured"], row["theory"], row["rival"]), 4)
                row["replication"] = repl.get(q["k"], {}).get("status")
                rows.append(row)
        counted = [row for row in rows if "gain" in row and row["replication"] != "differs"]  # differs: left out
        apart = [row for row in counted if not row["same_prediction"]]  # a same test adds 0: it does not separate
        total = round(sum(row["gain"] for row in apart), 3)
        state = ("not tested against rival" if len(counted) < 2 else "beats rival" if len(apart) >= 2 and total >= DECIDES
                 else "loses to rival" if len(apart) >= 2 and total <= -DECIDES else "not separated from rival")
        theories[n] = {"rival": json.loads(rfile(folder, n, 1).read_text())["statement"], "computed": len(counted), "tests": len(rows),
                       "separating": len(apart), "total_gain": total, "state": state, "no_offline_test": gpu, "rows": rows}
    (folder / "metrics_v5.json").write_text(json.dumps({"theories": theories}, indent=1) + "\n")
    print(f"Duel: each survivor's prediction (defend) against its rival's on the rival's tests; gain in nats, above 0 favours "
          f"the theory. same = the defender's centre is inside the rival's interval: not separating, adds 0. A total of "
          f"+-{DECIDES:g} or beyond over 2 or more separating computed tests decides.")
    print(f"{'theory':16} {'computed':>9} {'separating':>10} {'gain':>7}  state")
    for n, t in theories.items():
        print(f"{n:16} {t['computed']:>4} of {t['tests']:<2} {t['separating']:>10} {t['total_gain']:7.2f}  {t['state']}")
        print(f"    rival: {t['rival'][:150]}")
        for row in t["rows"]:
            head = f"    p{row['k']} turn {row['turn']}{' same, not separating' if row['same_prediction'] else ''}: "
            if "gain" not in row:
                print(head + f"not computable: {row['not_computable'][:110]}")
            else:
                th, rv = row["theory"], row["rival"]
                noise = f" (n {row['n']}, 90 % [{row['interval'][0]:g}, {row['interval'][1]:g}])" if row.get("interval") else ""
                again = {"replicated": ", replicated", "differs": ", differs from its replication: left out until resolved"}.get(row["replication"], "")
                print(head + f"measured {row['measured']:g}{noise}, theory {th['value']:g} [{th['low']:g}, {th['high']:g}], "
                      f"rival {rv['value']:g} [{rv['low']:g}, {rv['high']:g}], gain {row['gain']:+.2f}{again}")
        if t["no_offline_test"]:
            print(f"    no stored-row test separates them: {t['no_offline_test']['reason'][:120]}")
            print(f"    GPU experiment: {t['no_offline_test']['gpu_experiment'][:200]}")


# ---- version 7: experiments that tell a pair apart, and changes to the base ----

SIDES = {"theory": "a theory: one mechanism, the board items it explains, and its predictions (offline ones computed on "
                   "stored rows, GPU ones not yet run)",
         "rival": "a mechanism written as the rival of another theory: its statement, why it is the strongest rival, and "
                  "the offline tests it chose with its own predictions"}


def rival_file(folder, n):
    """The rival's last turn: the second when there is one."""
    return rfile(folder, n, 2) if rfile(folder, n, 2).exists() else rfile(folder, n, 1)


def pairs(folder):
    """Every theory that met a rival, whatever the duel state: the round's survivors, the account, carried pairs."""
    return [p.stem for p in sorted((folder / "theories").glob("*.json")) if rfile(folder, p.stem, 1).exists() and in_scope(p.stem)]


def sides(folder, n):
    """{"theory": (record name, mechanism), "rival": (...)}: each side as its cross_predict job sees it."""
    turns = [json.loads(rfile(folder, n, t).read_text()) for t in (1, 2) if rfile(folder, n, t).exists()]
    rival = {"statement": turns[-1]["statement"], "why_strongest": turns[-1].get("why_strongest"),
             "tests": [t for r in turns for t in r["tests"]]}
    if "intervention" in turns[-1]:
        rival |= {k: turns[-1].get(k) for k in ("intervention", "no_intervention")}
    return {"theory": (n, json.loads((folder / "theories" / f"{n}.json").read_text())), "rival": (f"{n}-rival", rival)}


def proposals(n, label, mine, iv):
    """A side's open experiments: a theory's GPU predictions (none for a rival), and the side's intervention iv."""
    out = [{"id": f"{n}:{label}:g{k}", "kind": "gpu", "experiment": p["experiment"], "unit": p["unit"], "gpu_minutes": p["gpu_minutes"],
            "prediction": {x: p[x] for x in ("value", "low", "high")}}
           for k, p in enumerate(mine.get("predictions", []), 1)
           if label == "theory" and "recipe" not in p and number(p.get("gpu_minutes")) and p["gpu_minutes"] > 0]
    if iv:
        c = iv["cell"]
        out.append({"id": f"{n}:{label}:intervention", "kind": "intervention", "unit": iv["unit"], "gpu_minutes": iv["gpu_minutes"],
                    "experiment": f"{iv['change'].rstrip('. ')}. Model {iv['model']}; set {c['set']}; prompt {c['prompt']}; sampling "
                                  f"{c['sampling']}; cap {c['cap']}; grader {c['grader']}; samples {c['samples']}; seeds "
                                  f"{c['seeds']}. Count: {iv['count']}",
                    "best_known": iv["best_known"], "prediction": {x: iv[x] for x in ("value", "low", "high")}, "why": iv["why"]})
    return out


def cross_valid(d, ids, ask, items):
    r = json.loads((d / "cross.json").read_text())
    if not isinstance(r, dict) or not isinstance(r.get("predictions"), list):
        return "need a JSON object with \"predictions\" (a list)"
    if sorted(str(p.get("id")) for p in r["predictions"]) != sorted(ids):
        return f"need one prediction for each id of open.json, each once: {ids}"
    bad = [p["id"] for p in r["predictions"] if not (all(number(p.get(k)) for k in ("value", "low", "high")) and p["low"] <= p["value"] <= p["high"])]
    m = [f"value outside [low, high] or not a number for {bad}"] if bad else []
    return "; ".join(m + (intervention_messages(r, items) if ask else [])) or None


def cross_predict(folder):
    """For every pair, each side predicts the other side's open experiments from its own mechanism, blind to the other
    side's statement and numbers: experiments/<theory>.json. A side whose file has no "intervention" key (a folder
    older than version 7) writes one in its first job; the other side predicts it in a second job."""
    todo = [n for n in pairs(folder) if not (folder / "experiments" / f"{n}.json").exists()]
    if not todo:
        return print("cross_predict: every pair has experiments/<theory>.json")
    items, other = item_ids(folder), {"theory": "rival", "rival": "theory"}
    base = {"DIRECTION.md": ROOT / "DIRECTION.md", "before.jsonl": folder / "before.jsonl", "inventory.md": folder / "inventory.md",
            "facts.json": facts_input(folder)}

    def out(n, label, turn):
        return folder / "experiments" / n / f"{label}{'.2' if turn == 2 else ''}.json"

    def own(n, label, mine):
        """The side's intervention and the reason when it has none: from its file, else from its first job."""
        src = mine if "intervention" in mine else json.loads(out(n, label, 1).read_text())
        return src["intervention"], src.get("no_intervention")

    for turn in (1, 2):
        jobs = []
        for n in todo:
            s = sides(folder, n)
            for label in ("theory", "rival"):
                mine, theirs = s[label][1], s[other[label]][1]
                ask = turn == 1 and "intervention" not in mine
                if turn == 1:
                    open_ = proposals(n, other[label], theirs, theirs.get("intervention"))
                else:  # the intervention the other side wrote in its first job
                    open_ = [] if "intervention" in theirs else proposals(n, other[label], {}, own(n, other[label], theirs)[0])
                if not open_ and not ask:
                    continue
                blind = [{k: e[k] for k in ("id", "experiment", "unit", "gpu_minutes", "best_known") if k in e} for e in open_]
                jobs.append(job("cross_predict", f"{n}.{label}{'.2' if turn == 2 else ''}",
                                {**base, "mine.json": json.dumps(mine, indent=1), "open.json": json.dumps(blind, indent=1)},
                                {"cross.json": out(n, label, turn)},
                                lambda d, ids=[e["id"] for e in open_], ask=ask: cross_valid(d, ids, ask, items),
                                side=SIDES[label], ask=prompt("intervention") if ask else "Write no \"intervention\" key."))
        run(jobs, folder)
    v4 = json.loads((folder / "metrics_v4.json").read_text())["theories"] if (folder / "metrics_v4.json").exists() else {}
    v5 = json.loads((folder / "metrics_v5.json").read_text())["theories"] if (folder / "metrics_v5.json").exists() else {}
    for n in todo:
        s = sides(folder, n)
        theirs = {p["id"]: p for label in ("theory", "rival") for turn in (1, 2) if out(n, label, turn).exists()
                  for p in json.loads(out(n, label, turn).read_text())["predictions"]}
        entries, none = [], {}
        for label in ("theory", "rival"):
            iv, reason = own(n, label, s[label][1])
            none[s[label][0]] = None if iv else reason
            for e in proposals(n, label, s[label][1], iv):
                o = theirs[e["id"]]
                entries.append({**{k: v for k, v in e.items() if k != "prediction"}, "pair": n, "proposer": s[label][0],
                                "other": s[other[label]][0], "proposer_prediction": e["prediction"],
                                "other_prediction": {k: o[k] for k in ("value", "low", "high", "why")}})
        (folder / "experiments" / f"{n}.json").write_text(json.dumps({
            "pair": n, "theory_state": f"{v4.get(n, {}).get('state', '')} {v4.get(n, {}).get('verdict', '')[:120]}".strip(),
            "duel_state": v5.get(n, {}).get("state", ""), "statements": {name: m["statement"] for name, m in s.values()},
            "no_intervention": none, "experiments": entries}, indent=1) + "\n")
        print(f"  experiments/{n}.json: {len(entries)} open experiments")


def experiments(folder):
    """Every open experiment of the round's pairs and of carried pairs, ranked twice: by separation per GPU minute (the
    proposer's log gain over the other side if the proposer's value is measured, clipped to 3 nats), and the
    interventions by gain over the best known base count. experiments.json, experiments.md."""
    done = {g["id"] for g in json.loads((folder / "gpu_tests.json").read_text())} if (folder / "gpu_tests.json").exists() else set()
    if (folder / "experiments_measured.json").exists():
        done |= {m["id"] for m in json.loads((folder / "experiments_measured.json").read_text())}
    entries = []
    for p in sorted((folder / "experiments").glob("*.json")):
        pair = json.loads(p.read_text())
        for side, reason in pair["no_intervention"].items():
            if reason:
                print(f"  {side}: no intervention: {reason}")
        for e in pair["experiments"]:
            if e["id"] in done:
                continue
            P, O = e["proposer_prediction"], e["other_prediction"]
            sep = round(clip3(log_density(P["value"], P) - log_density(P["value"], O)), 3)
            e = {**e, "statements": pair["statements"], "theory_state": pair["theory_state"], "duel_state": pair["duel_state"],
                 "separation": sep, "separation_per_minute": round(sep / e["gpu_minutes"], 4)}
            if e["kind"] == "intervention":
                e["gain_over_best"] = round(P["value"] - e["best_known"]["value"], 3)
                e["other_gain_over_best"] = round(O["value"] - e["best_known"]["value"], 3)
            entries.append(e)
    by_sep = sorted(entries, key=lambda e: -e["separation_per_minute"])
    by_gain = sorted((e for e in entries if e["kind"] == "intervention"), key=lambda e: -e["gain_over_best"])
    (folder / "experiments.json").write_text(json.dumps({"experiments": entries, "by_separation": [e["id"] for e in by_sep],
                                                        "by_gain": [e["id"] for e in by_gain]}, indent=1) + "\n")

    def block(k, e):
        P, O = e["proposer_prediction"], e["other_prediction"]
        head = (f"gain over best {e['gain_over_best']:+g}, " if "gain_over_best" in e else "") + \
            f"separation {e['separation']:+.2f} nats, {e['gpu_minutes']:g} GPU min ({e['separation_per_minute']:.3f} nats per minute)"
        lines = [f"### {k}. {e['id']} — {head}",
                 f"- Pair {e['pair']} (theory state: {e['theory_state'] or 'none'}; duel: {e['duel_state'] or 'none'}). "
                 f"Proposed by {e['proposer']}: {e['statements'][e['proposer']][:300]}",
                 f"- Run: {e['experiment']}", f"- Unit: {e['unit']}",
                 f"- {e['proposer']} predicts {P['value']:g} [{P['low']:g}, {P['high']:g}]" + (f": {e['why']}" if e.get("why") else ""),
                 f"- {e['other']} predicts {O['value']:g} [{O['low']:g}, {O['high']:g}]: {O['why']}"]
        if "best_known" in e:
            b = e["best_known"]
            lines.append(f"- Best known base-only count: {b['value']:g} ({b['item']}: {b.get('setting', '')}); gain over it "
                         f"{e['gain_over_best']:+g} by {e['proposer']}, {e['other_gain_over_best']:+g} by {e['other']}")
        return "\n".join(lines)

    md = [f"# Open experiments of {folder.name}", "",
          "Separation: the log gain in nats of the proposing side over the other side if the proposer's value is measured "
          "(normal densities, sd = (high - low) / 3.29, clipped to 3). Gain over best: the predicted count minus the best "
          "count of right answers the untrained base has before on the same set, cap and grader.", "",
          "## A. Telling two mechanisms apart: by separation per GPU minute", "",
          *[block(k, e) + "\n" for k, e in enumerate(by_sep, 1)],
          "## B. Changes to the base: by gain over the best known base count", "",
          *[block(k, e) + "\n" for k, e in enumerate(by_gain, 1)]]
    (folder / "experiments.md").write_text("\n".join(md))
    print(f"{len(entries)} open experiments, {len(by_gain)} of them changes to the base; experiments.md")
    for title, ranked in (("by separation per GPU minute", by_sep), ("interventions by gain over best", by_gain)):
        print(f"  {title}:")
        for e in ranked[:5]:
            P, O = e["proposer_prediction"], e["other_prediction"]
            print(f"    {e['id']}: {P['value']:g} [{P['low']:g}, {P['high']:g}] vs {e['other']} {O['value']:g} "
                  f"[{O['low']:g}, {O['high']:g}], separation {e['separation']:+.2f} in {e['gpu_minutes']:g} min"
                  + (f", gain over best {e['gain_over_best']:+g}" if "gain_over_best" in e else ""))


REPLICATE_TESTS = ("$out/offline.json lists offline computations, each with k, experiment, recipe and unit. Someone "
                   "computed them before you; you are not told how, what they got or what anyone predicts. Compute each "
                   "again from its recipe alone. refuted_by is null for every entry, so every script prints "
                   "\"refuted_by_met\": false.")


def same_number(a, b):
    return a is not None and b is not None and abs(a - b) <= max(0.01 * abs(b), 0.005)


def replicate(folder):
    """An agent that gets only the recipes recomputes every decisive number: wins the readers did not expect,
    predictions outside or meeting a refuting condition, every share and fit of an account, and duel tests with a gain
    of 1 nat or more in size. replication/<theory>[.duel].json; a number that differs is left out of the state rules."""
    v4 = json.loads((folder / "metrics_v4.json").read_text())["theories"]
    v5 = json.loads((folder / "metrics_v5.json").read_text())["theories"] if (folder / "metrics_v5.json").exists() else {}
    work = []
    for n, m in v4.items():
        if not in_scope(n) or m.get("carried_from") or (folder / "replication" / f"{n}.json").exists():
            continue
        if not (folder / "tests" / f"{n}.json").exists():  # a theory with no computed test has nothing to recompute
            continue
        tests = {q["k"]: q for q in json.loads((folder / "tests" / f"{n}.json").read_text())["predictions"] if q["measured"] is not None}
        ks = set(m["unexpected_wins"]) | {r["k"] for r in m["rows"] if "gain" in r and (r["refuted_by_met"] or (not r["inside"] and not r.get("within_noise")))}
        ks |= {k for k, q in tests.items() if q.get("role") in ("share", "fit") and not q.get("by_construction")}
        if ks := sorted(k for k in ks if k in tests):
            work.append((n, "", {k: tests[k] for k in ks}))
    for n, t in v5.items():
        if (folder / "replication" / f"{n}.duel.json").exists():
            continue
        tests = {q["k"]: q for turn in (1, 2) if rfile(folder, n, turn, ".tests").exists()
                 for q in json.loads(rfile(folder, n, turn, ".tests").read_text())["tests"]}
        if ks := [r["k"] for r in t["rows"] if abs(r.get("gain", 0)) >= 1]:
            work.append((n, ".duel", {k: tests[k] for k in ks}))
    if not work:
        return print("replicate: nothing new to replicate")
    jobs = []
    for n, kind, tests in work:
        offline = [{"k": k, "experiment": q["experiment"], "recipe": q["recipe"], "unit": q["unit"], "refuted_by": None} for k, q in tests.items()]
        scripts = folder / "replication" / f"{n}{kind}"
        jobs.append((n, kind, tests, offline, scripts, script_job(folder, f"repl-{n}{kind}", offline, {}, scripts, REPLICATE_TESTS)))
    run([j[-1] for j in jobs], folder, workers=6)
    for n, kind, tests, offline, scripts, _ in jobs:
        items = []
        for r in run_scripts(folder, f"replicate/{n}{kind}", offline, scripts):
            first = tests[r["k"]]["measured"]
            both_refuted = tests[r["k"]].get("refuted_by_met") and r["refuted_by_met"]  # both sides meet the refuting condition
            items.append({"k": r["k"], "experiment": r["experiment"], "original": first, "replicated": r["measured"],
                          "status": "not replicated" if r.get("script_failed") else
                                    "replicated" if same_number(r["measured"], first) or both_refuted else "differs",
                          "refuted_by_met": r["refuted_by_met"], "script": r["script"], "not_computable": r["not_computable"]})
            if items[-1]["status"] == "differs":
                print(f"  {n}{kind} p{r['k']} DIFFERS: first {first}, replication {r['measured']}; left out until a person resolves it")
        (folder / "replication" / f"{n}{kind}.json").write_text(json.dumps({"theory": n, "items": items}, indent=1) + "\n")
        print(f"  {n}{kind}: {sum(i['status'] == 'replicated' for i in items)} of {len(items)} replicated")
    score_tests(folder)
    if v5:
        score_duel(folder)


DUEL_REVIEW = """The theory was also compared with the strongest rival a fresh agent could write: $round/rivals/$theory.json (the rival
mechanism and its tests, each with the rival's prediction and what the theory should say), $round/rivals/$theory.defend.json
(a separate agent's predictions from the theory alone), $round/rivals/$theory/ and $round/rivals/$theory.tests.json
(the scripts and the computed numbers); the same names with ".turn2" when the rival had a second turn; and
$round/metrics_v5.json, entry "$theory" (gain per test, above 0 favours the theory, and the state: $duel_state; a test
with "same_prediction" true does not separate the two and adds 0). Read one duel script: does it implement the rival's
recipe as written? Your verdict names the duel state. Apart from the rule for "stands" below, a theory that beats its
rival is not "weak" only because some other rival could exist; call it weak only for a reason you can point to (a
refuting item, a published claim, a broken script).
"""


RIVAL_WON = """The rival won the duel, so the rival's mechanism is what will be posted. Do the refutation search (1) and the
novelty search (3) about the rival's mechanism (the statement in $round/rivals/$theory.json), not the theory's, and add
"about": "rival" to review.json.
"""


ACCOUNT_REVIEW = """This theory is an account: a budget of the gap between the base and the RL model over several cells (its
"cells", "parts" and rules; its state is $state, and its measured shares are posted whatever the state). For the novelty
search (3), look on the board and in the literature for the same breakdown of the same cells, and say whether the
cells can be compared: the same evidence rows, grader version, prompts and sampling on both sides, and how its cells
stand against its null cell. $round/replication/$theory.json holds the independent recomputation of its shares.
"""


def review(folder):
    metrics = folder / ("metrics_v4.json" if args.version >= 4 else "metrics_v3.json")
    theories = json.loads(metrics.read_text())["theories"]
    names = survivors(folder) if args.version >= 4 else sorted((n for n, t in theories.items() if t["state"] == "passes"),
                                                              key=lambda n: -theories[n]["total_gain"])[:3]
    duelled = set(names)
    if args.version >= 6:  # the account is reviewed whatever its state: its measured budget is posted either way
        names += [n for n in theories if "-account" in n and in_scope(n) and n not in names and not theories[n].get("carried_from")]
    if not names:
        return print("review: no surviving theory")
    duel = json.loads((folder / "metrics_v5.json").read_text())["theories"] if args.version >= 5 else {}
    keys = {"refutation", "wins_judgement", "rival", "novelty", "import_carries_gain", "verdict"}

    def valid(d, state, n):
        r = json.loads((d / "review.json").read_text())
        if args.version >= 8 and r.get("verdict", "").startswith("stands") and not forecast_gain(folder, n):
            return FORECAST_REVIEW.format(theory=n)
        if missing := keys - r.keys():
            return f"missing keys {sorted(missing)}"
        if state == "loses to rival" and r.get("about") != "rival":
            return "the rival won the duel: the review is about the rival's mechanism and review.json says \"about\": \"rival\""
        return f"the verdict must name the duel state \"{state}\"" if state and state not in r["verdict"] else None

    jobs = []
    for n in names:
        state = duel[n]["state"] if n in duel else "not tested against rival" if args.version >= 5 and n in duelled else ""
        text = string.Template(DUEL_REVIEW + (RIVAL_WON if state == "loses to rival" else "")).substitute(
            round=folder.resolve(), theory=n, duel_state=state) if state else ""
        if "-account" in n:
            text += string.Template(ACCOUNT_REVIEW).substitute(round=folder.resolve(), theory=n, state=theories[n]["state"])
        text += FORECAST_REVIEW.format(theory=n) if args.version >= 8 else ""
        jobs.append(job("review", n, {}, {"review.json": folder / "reviews" / f"{n}.json"}, lambda d, state=state, n=n: valid(d, state, n),
                        mode="repo", round=folder.resolve(), theory=n, metrics=metrics.name, duel=text))
    run(jobs, folder)
    for n in names:
        print(f"  {n}: {json.loads((folder / 'reviews' / f'{n}.json').read_text())['verdict']}")
    if args.version >= 4:
        score_tests(folder)


FORECAST_REVIEW = ("Version 8: the verdict may be \"stands\" only when forecast_scores.json in the round folder gives {theory} a "
                   "total forecast gain above 0 nats on 3 or more scored targets (its forecasts of open work, scored when the "
                   "results posted), in addition to the duel rule. Otherwise the best verdict is \"weak\".\n")
MECHANISM_FORECASTS = (
    "- targets.json lists numbers the team's open GPU jobs will report; nobody has seen them. The main test of a mechanism is "
    "its forecast of these numbers. Give each mechanism a key \"targets\": the ids of the targets the mechanism, as written, "
    "gives a number for. A mechanism with fewer than {need} such targets is not proposed: replace it. It need not disagree "
    "with the obvious reading of the board; it must be right.")
DEVELOP_FORECASTS = (
    "- targets.json lists numbers the team's open GPU jobs will report; nobody has seen them. These forecasts are the main test "
    "of the theory. Add \"forecasts\": [{{\"id\": \"t01\", \"value\": 312, \"low\": 295, \"high\": 330, \"reason\": \"<one line: how the "
    "mechanism gives this number>\"}}] for {need} or more targets, the ones mechanism.json lists in \"targets\" first: a value and a "
    "90 % interval in the target's unit. Each is scored, as a normal with sd (high - low) / 3.29, by the density it gives the "
    "measured value against two readers with no theory. Do not forecast a target the mechanism says nothing about.\n")


def open_ids(folder):
    return [t["id"] for t in json.loads((folder / "targets.json").read_text())["targets"]]


def need_forecasts(folder):
    """A version-8 mechanism or new theory forecasts at least a third of the open targets, and at least 3."""
    return max(3, -(-len(open_ids(folder)) // 3))


def forecast_gain(folder, name):
    """Version 8: a positive total forecast gain on 3 or more scored targets (standing's forecast_scores.json)."""
    path = folder / "forecast_scores.json"
    p = json.loads(path.read_text())["forecasters"].get(name) if path.exists() else None
    return bool(p) and p["scored"] >= 3 and p["total_gain"] > 0


def targets_open(folder):
    if (folder / "targets.json").exists():
        return print("skip targets_open: targets.json exists")
    forecast.open_targets(folder)


def forecast_open(folder):
    """The readers and every carried theory forecast the open targets blind; new theories bring their own forecasts."""
    if (folder / "forecasts.json").exists():
        return print("skip forecast: forecasts.json exists")
    theories = {p.stem: json.loads(p.read_text()) for p in sorted((folder / "theories").glob("*.json"))}
    own = {n: t["forecasts"] for n, t in theories.items() if n.startswith(f"r{round_number(folder)}-") and "forecasts" in t}
    common = {"DIRECTION.md": ROOT / "DIRECTION.md", "board.jsonl": folder / "before.jsonl", "work.md": folder / "work.md"}
    fs = forecast.run_forecasters(folder, common, {n: folder / "theories" / f"{n}.json" for n in theories if n not in own}) | own
    utc = json.loads((folder / "targets.json").read_text())["utc"]
    (folder / "forecasts.json").write_text(json.dumps({"snapshot_utc": utc, "written_utc": forecast.now(), "forecasts": fs}, indent=1) + "\n")
    forecast.write_md(folder, utc, fs)
    for n, f in fs.items():
        print(f"  {n}: {sum(x['value'] is not None for x in f)} forecasts")


import forecast  # noqa: E402

STAGES = {"split": split, "targets_open": targets_open, "forecast": forecast_open, "standing": standing, "inventory": inventory, "targets": targets, "external": external,
          "generate": generate, "null": null, "claims": claims, "score": score, "reverse": reverse, "test": test, "review": review,
          "mechanisms": mechanisms, "develop": develop, "null_tests": null_tests, "score_tests": score_tests, "heldout": heldout,
          "account": account, "replicate": replicate, "rival": rival, "rival2": rival2, "defend": defend, "duel_test": duel_test, "score_duel": score_duel,
          "cross_predict": cross_predict, "experiments": experiments}
ALL = {3: ["split", "standing", "inventory", "targets", "external", "generate", "null", "claims", "score", "reverse", "test", "score", "review"],
       4: ["split", "standing", "inventory", "external", "mechanisms", "develop", "null_tests", "test", "score_tests", "heldout", "review"],
       5: ["split", "standing", "inventory", "external", "mechanisms", "develop", "null_tests", "test", "score_tests", "heldout",
           "rival", "defend", "rival2", "defend", "duel_test", "score_duel", "review"]}
ALL[6] = ["split", "standing", "inventory", "external", "mechanisms", "develop", "account", "null_tests", "test", "score_tests",
          "replicate", "heldout", "rival", "defend", "rival2", "defend", "duel_test", "score_duel", "replicate", "review"]
ALL[7] = ALL[6][:-2] + ["cross_predict", "replicate", "review", "experiments"]
ALL[8] = ALL[7][:2] + ["targets_open"] + ALL[7][2:7] + ["forecast"] + ALL[7][7:]  # targets after standing; forecasts after develop and account

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path)
    parser.add_argument("stages", nargs="+", choices=[*STAGES, "all"])
    parser.add_argument("--version", type=int, choices=[3, 4, 5, 6, 7, 8], default=8)
    parser.add_argument("--only-account", action="store_true", help="version 6: no mechanisms or develop; only the "
                        "account is tested and duelled, carried theories are its inputs (implies --with-account)")
    parser.add_argument("--with-account", action="store_true", help="version 7.1: all runs the account job, and accounts "
                        "are tested, duelled, replicated and reviewed; without it no account stage runs")
    parser.add_argument("--cutoff")
    parser.add_argument("--skip", action="append", default=[])
    parser.add_argument("--from", dest="prev")
    parser.add_argument("--account-from", help="standing: also give the account job the accounts of this folder's chain "
                        "(for example studies/theory/results/account/run-03)")
    parser.add_argument("--starts", default="all,surprises,across,external,revise")
    parser.add_argument("--n-mechanisms", type=int, default=12)
    parser.add_argument("--deep", help="version 9: a wide round folder (forecast.py round); mechanisms are its carried "
                        "mechanisms, developed, tested and duelled by the other stages")
    parser.add_argument("--model-all")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--min-targets", type=int, default=15)
    args = parser.parse_args()
    args.with_account |= args.only_account
    order = [s for s in ALL[args.version] if not (args.only_account and s in ("mechanisms", "develop"))
             and (args.with_account or s != "account")]
    for stage in order if args.stages == ["all"] else args.stages:
        print(f"== {stage}")
        STAGES[stage](args.folder)
