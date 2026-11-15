# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""A theory round (.claude/skills/theory/SKILL.md): every model call is a headless Claude run, every check and score is
code here.

  uv run studies/theory/lib/round.py <round dir> <stage> [options]

Version 4 (default). `all` runs, in order:
  split --cutoff <ISO time> [--skip <word> ...]   check.dump: before.jsonl, after.jsonl
  standing --from <previous round dir>            graveyard.json (every theory of every earlier round in that engine
                                                  folder), theories/ (survivors carried, unchanged), prior_reviews/
  inventory      (opus, repository)               inventory.md: stored per-problem row files, fetch command, readable now
  external       (opus, papers.py only)           external.md: published mechanisms and their numbers
  mechanisms [--n-mechanisms 12]   (opus)         mechanisms.json: pairwise different candidate mechanisms
  develop        (opus, one per mechanism)        drafts/, theories/r<N>-m<id>.json, dropped.json (abandoned or failing
                                                  the check twice), theories.sha256
  null_tests     (opus, 2 jobs)                   tests_blind.jsonl, predictions/nulltest-1.jsonl, nulltest-2.jsonl
  test           (opus, repository, laptop only)  tests/<theory>/p<k>.py written by the model, run here once:
                                                  tests/<theory>.json
  score_tests    (no model)                       metrics_v4.json and the printed table
  heldout                                         targets, null, claims (survivors only), score_tests: strikes
  review         (opus, repository)               reviews/<theory>.json for the top 3 survivors

Version 3 (`--version 3`; `all` runs split, standing, inventory, targets, external, generate, null, claims, score,
reverse, test, score, review): generate [--starts ...], score (metrics_v3.json), reverse. Every stage is callable alone.

Every model call except inventory, test and review runs in an empty job directory outside the repository with only
the Read and Write tools, so no git status, project instructions, memory or board reaches it. A job whose outputs
exist is skipped, so a stopped round resumes. Repository jobs and test scripts run with AWS_PROFILE=iterate-ecr.
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

AWS_PROFILE = "iterate-ecr"  # reads s3://pg-lineage-769063704696/results/rlneurons/ on the owner's machine
# Test scripts run with the team's grader packages (studies/rlneurons/README.md: math-verify 0.9.0 and numpy) and the
# antlr4 runtime sympy's LaTeX parser needs (it accepts only 4.11), from the repository root with the root on PYTHONPATH,
# so `from studies.rlneurons.lib import rln4_lib` works.
TEST_PACKAGES = ["numpy", "math-verify==0.9.0", "antlr4-python3-runtime==4.11"]
TEST_PYTHON = ["uv", "run", "--no-project", *(a for p in TEST_PACKAGES for a in ("--with", p)), "python"]
MODELS = {"inventory": "opus", "targets": "sonnet", "external": "opus", "generate": "opus", "fix": "opus",
          "null": "opus", "claims": "opus", "reverse": "sonnet", "test": "opus", "review": "opus",
          "mechanisms": "opus", "develop": "opus", "null_tests": "opus"}
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
    "inventory": ["Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(git ls-files:*)", "Bash(git log:*)",
                  "Bash(git show:*)", "Bash(aws s3 ls:*)", "Bash(aws s3 cp:*)", "Bash(modal volume ls:*)",
                  "Bash(modal volume get:*)", "Bash(mkdir -p runs/:*)"],
    "test": ["Bash"],
    "review": ["Bash(python3 tools/recall.py:*)", "Bash(python3 tools/exa.py:*)", "Bash(uv run tools/board.py ls:*)",
               "Bash(uv run tools/board.py show:*)", "Bash(git log:*)", "Bash(git show:*)", "Bash(ls:*)", "Bash(cat:*)"],
}
THEORY_KEYS = {"name", "statement", "scope", "parent", "imports", "explains", "conflicts", "rival", "predictions"}
THEORY_KEYS_V4 = {"name", "statement", "scope", "explains", "conflicts", "rival", "predictions"}
PREDICTION_KEYS = {"experiment", "unit", "value", "low", "high", "refuted_by", "gpu_minutes"}
MECHANISM_KEYS = {"id", "mechanism", "starts_from", "import", "differs_from", "first_test"}
METRICS_FILES = ("metrics_v4.json", "metrics_v3.json", "metrics_v2.json", "metrics.json")
BAD_VERDICTS = ("refuted", "published", "weak")
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
    return int(re.search(r"round-(\d+)", Path(folder).name).group(1))


def prompt(stage, **values):
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
    graveyard, where = {}, {}
    for rdir in sorted((d for d in prev.parent.glob("round-*") if round_number(d) < nn), key=round_number):
        mfile = next((rdir / f for f in METRICS_FILES if (rdir / f).exists()), None)
        if mfile is None:
            continue
        what = {t["id"]: t["what"] for t in read(rdir / "targets.jsonl")} if (rdir / "targets.jsonl").exists() else {}
        for name, m in json.loads(mfile.read_text())["theories"].items():
            if name == "planted":  # round 01's reversed control, not a theory
                continue
            review_path = rdir / "reviews" / f"{name}.json"
            review = json.loads(review_path.read_text()) if review_path.exists() else None
            state = m.get("state") or ("beats the null" if m["beats_null"] else "does not beat the null")
            entry = {"name": name, "round": round_number(rdir), "rounds": graveyard.get(name, {}).get("rounds", []) + [round_number(rdir)],
                     "statement": json.loads((rdir / "theories" / f"{name}.json").read_text())["statement"],
                     "state": state, "verdict": review["verdict"] if review else ""}
            entry["reason"] = "" if survivor(entry) else graveyard_reason(m, review, what)
            graveyard[name], where[name] = entry, rdir
    (folder / "graveyard.json").write_text(json.dumps(graveyard, indent=1) + "\n")
    (folder / "theories").mkdir(exist_ok=True)
    carried = 0
    for name, entry in graveyard.items():
        # an untested theory is carried once, so the new round computes its tests; a survivor is carried with its
        # computed tests and their gains (tests/<name>.json, "carried_from"), so they are not computed or scored again
        if survivor(entry) or (entry["state"] == "untested" and len(entry["rounds"]) == 1):
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
            print(f"  carried: {name} (round {entry['round']}, {entry['state']})")
    print(f"  graveyard.json: {len(graveyard)} theories from earlier rounds, {carried} carried")
    metrics = json.loads((prev / "metrics_v3.json").read_text()) if (prev / "metrics_v3.json").exists() else None
    if metrics and (prev / "targets.jsonl").exists():  # for version 3's revise start
        what = {t["id"]: t["what"] for t in read(prev / "targets.jsonl")}
        prior = {n: {"statement": graveyard[n]["statement"], "state": m["state"],
                     "claims": [{**row, "what": what[row["id"]]} for row in m["rows"]]} for n, m in metrics["theories"].items()}
        (folder / "prior_scores.json").write_text(json.dumps(prior, indent=1) + "\n")


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


def graveyard_input(folder):
    return folder / "graveyard.json" if (folder / "graveyard.json").exists() else "{}\n"


def mechanisms(folder):
    if (folder / "mechanisms.json").exists():
        return print("skip mechanisms: mechanisms.json exists")
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
        bad = [m["id"] for m in ms if m["import"] is not None and m["import"] not in known]
        return f"imports that are not external.md heading ids: {bad}" if bad else None

    run([job("mechanisms", "mechanisms", {"DIRECTION.md": ROOT / "DIRECTION.md", "before.jsonl": folder / "before.jsonl",
                                          "external.md": folder / "external.md", "inventory.md": folder / "inventory.md",
                                          "graveyard.json": graveyard_input(folder)},
             {"mechanisms.json": folder / "mechanisms.json"}, valid, n=n)], folder)
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
            "inventory.md": folder / "inventory.md", "external.md": folder / "external.md"}
    run([job("develop", name, {**base, "mechanism.json": json.dumps(m, indent=1)}, {"result.json": folder / "drafts" / f"{name}.json"},
             valid, theory=name) for name, m in zip(names, ms)], folder)
    drafts = {n: json.loads((folder / "drafts" / f"{n}.json").read_text()) for n in names}
    abandoned = {n: {"abandon": d["abandon"]} for n, d in drafts.items() if "abandon" in d}
    for n, a in abandoned.items():
        print(f"  abandoned {n}: {a['abandon'][:200]}")
    fix_inputs = {"before.jsonl": folder / "before.jsonl", "external.md": folder / "external.md",
                  "inventory.md": folder / "inventory.md", "graveyard.json": graveyard_input(folder)}
    finish_theories(folder, [n for n in names if n not in abandoned], drafts,
                    lambda ds: check_theories4(folder, ds, set(graveyard)), fix_inputs, abandoned)


def offline_predictions(theory):
    return [{"k": k, **p} for k, p in enumerate(theory["predictions"], 1) if "recipe" in p]


def carried_tests(folder, name):
    """A survivor's tests carried by `standing` from the round that computed and scored them."""
    path = folder / "tests" / f"{name}.json"
    return path.exists() and "carried_from" in json.loads(path.read_text())


def null_tests(folder):
    blind = [{"id": f"{p.stem}:p{q['k']}", "experiment": q["experiment"], "recipe": q["recipe"], "unit": q["unit"]}
             for p in sorted((folder / "theories").glob("*.json")) if not carried_tests(folder, p.stem)
             for q in offline_predictions(json.loads(p.read_text()))]
    if not blind:
        return print("null_tests: no offline prediction")
    write(folder / "tests_blind.jsonl", blind)
    ids = [b["id"] for b in blind]
    run([job("null_tests", f"nulltest-{k}", {"before.jsonl": folder / "before.jsonl", "inventory.md": folder / "inventory.md",
                                              "tests_blind.jsonl": folder / "tests_blind.jsonl"},
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
        gain = min(3.0, max(-3.0, log_density(x, c) - log_null))
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


def score_tests(folder):
    """Version 4 score, metrics_v4.json: each theory's computed offline predictions against its intervals, its refuting
    conditions and the two no-theory test readers; held-out strikes and the review can only remove a theory."""
    nulls = [{p["id"]: p for p in read(folder / "predictions" / f"nulltest-{k}.jsonl")} for k in (1, 2)] \
        if (folder / "predictions" / "nulltest-1.jsonl").exists() else None
    theories = {}
    for p in sorted((folder / "theories").glob("*.json")):
        name = p.stem
        path = folder / "tests" / f"{name}.json"
        data = json.loads(path.read_text()) if path.exists() else {"predictions": []}
        preds = data["predictions"]
        computed = [q for q in preds if q["measured"] is not None]
        if "carried_from" in data:  # computed and scored in that round: its rows, gains against that round's readers
            rows = data["rows"]
        else:
            rows = gain_rows([{"id": f"{name}:p{q['k']}", "value": q["value"], "low": q["low"], "high": q["high"]} for q in computed],
                             {f"{name}:p{q['k']}": q["measured"] for q in computed}, nulls) if computed else []
            for r, q in zip(rows, computed):
                r.update(k=q["k"], inside=q["inside"], refuted_by=q["refuted_by"], refuted_by_met=q["refuted_by_met"])
            rows += [{"k": q["k"], "not_computable": q["not_computable"]} if q["not_computable"] else
                     {"k": q["k"], "refuted_without_number": q["refuted_by"]} for q in preds if q["measured"] is None]
        outside = sum(not q["inside"] for q in computed)
        reasons = [f"p{q['k']} {q['experiment'][:80]}: measured {q['measured']}, predicted {q['value']} [{q['low']}, {q['high']}]; "
                   f"refuting condition met: {q['refuted_by'][:120]}" for q in preds if q["refuted_by_met"]]
        if outside >= 2:
            reasons.append(f"{outside} of {len(computed)} computed predictions outside their 90 % intervals")
        total = round(sum(r["gain"] for r in rows if "gain" in r), 3)
        state = "refuted" if reasons else "untested" if len(computed) < 2 else "survives" if total > 0 else "no gain"
        held = strike_rows(folder, name) if (folder / "claims" / f"{name}.jsonl").exists() else []
        if (strikes := sum(r["strike"] for r in held)) >= 2:
            state = "refuted"
            reasons.append(f"{strikes} held-out strikes (claims both readers contradicted that missed their interval)")
        review = folder / "reviews" / f"{name}.json"
        verdict = json.loads(review.read_text())["verdict"] if review.exists() else ""
        if verdict.startswith(("refuted", "published")):
            state = verdict.split(":")[0]
            reasons.append(f"review: {verdict[:200]}")
        theories[name] = {"carried_from": data.get("carried_from"),
                          "offline": len(preds), "computed": len(computed), "inside": len(computed) - outside, "outside": outside,
                          "total_gain": total, "heldout_claims": len(held), "strikes": strikes, "state": state,
                          "reasons": reasons, "verdict": verdict, "rows": rows, "heldout_rows": held}
    (folder / "metrics_v4.json").write_text(json.dumps({"theories": theories}, indent=1) + "\n")
    print("Offline tests: computed predictions against their 90 % intervals; gain in nats against the two no-theory test readers.")
    print(f"{'theory':16} {'computed':>9} {'in/out':>7} {'gain':>7} {'strikes':>8}  state")
    for name, t in sorted(theories.items(), key=lambda kv: -kv[1]["total_gain"]):
        print(f"{name:16} {t['computed']:>4} of {t['offline']:<2} {t['inside']:>3}/{t['outside']:<3} {t['total_gain']:7.2f} "
              f"{str(t['strikes']) + ' of ' + str(t['heldout_claims']) if t['heldout_claims'] else '':>8}  {t['state']}"
              f"{', tests carried from ' + t['carried_from'] if t['carried_from'] else ''}")
        for r in t["rows"]:
            if "not_computable" in r:
                print(f"    p{r['k']}: not computable: {r['not_computable'][:110]}")
            elif "refuted_without_number" in r:
                print(f"    p{r['k']}: no number; refuting condition met: {r['refuted_without_number'][:100]}")
            else:
                print(f"    p{r['k']}: measured {r['measured']:g}, predicted {r['value']:g} [{r['low']:g}, {r['high']:g}], "
                      f"readers {r['nulls'][0]['value']:g} and {r['nulls'][1]['value']:g}, gain {r['gain']:+.2f}"
                      f"{', refuting condition met' if r['refuted_by_met'] else ''}")


def heldout(folder):
    nn, theories = round_number(folder), json.loads((folder / "metrics_v4.json").read_text())["theories"]
    names = [n for n, t in theories.items() if t["state"] == "survives" or (not n.startswith(f"r{nn}-") and t["state"] == "untested")]
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


def test(folder):
    """Version 4: every theory's offline predictions; version 3: the candidates'. The model writes one script per
    prediction and runs none; each script runs here once."""
    names = [p.stem for p in sorted((folder / "theories").glob("*.json"))] if args.version == 4 else candidates(folder)
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

        def valid(d, n=n, offline=offline):
            missing = [q["k"] for q in offline if not (d / "tests" / n / f"p{q['k']}.py").exists()]
            if missing:
                return f"no script for predictions {missing}"
            notes = d / "tests" / n / "notes.json"
            return None if notes.exists() and isinstance(json.loads(notes.read_text()), list) else f"no list in {notes}"

        jobs.append((n, offline, job("test", n, {"theory.json": folder / "theories" / f"{n}.json", "offline.json": json.dumps(offline, indent=1)},
                                     {f"tests/{n}": folder / "tests" / n}, valid,
                                     mode="repo", theory=n, inventory=(folder / "inventory.md").resolve(), profile=AWS_PROFILE,
                                     run_command=" ".join(TEST_PYTHON))))
    run([j for _, _, j in jobs], folder, workers=6)
    for n, offline, _ in jobs:
        notes = {e["k"]: e["note"] for e in json.loads((folder / "tests" / n / "notes.json").read_text())}
        results = []
        for q in offline:
            script = folder / "tests" / n / f"p{q['k']}.py"
            p = subprocess.run([*TEST_PYTHON, str(script.resolve())], cwd=ROOT, capture_output=True, text=True, timeout=1800,
                               env={**os.environ, "AWS_PROFILE": AWS_PROFILE, "PYTHONPATH": str(ROOT)})
            (script.with_suffix(".out.txt")).write_text(p.stdout + p.stderr)
            if p.returncode:
                sys.exit(f"{script} failed (exit {p.returncode}); output in {script.with_suffix('.out.txt')}")
            out = json.loads(p.stdout.strip().splitlines()[-1])
            m = out["measured"]
            if m is None and not out.get("not_computable") and not out["refuted_by_met"]:
                sys.exit(f"{script} printed no number, no not_computable reason and no refutation; output in {script.with_suffix('.out.txt')}")
            results.append({"k": q["k"], "experiment": q["experiment"], "recipe": q["recipe"], "script": str(script.relative_to(folder)),
                            "value": q["value"], "low": q["low"], "high": q["high"], "measured": m,
                            "inside": None if m is None else q["low"] <= m <= q["high"], "refuted_by": q["refuted_by"],
                            "refuted_by_met": bool(out["refuted_by_met"]), "alt_measured": out.get("alt_measured"),
                            "not_computable": out.get("not_computable") if m is None and not out["refuted_by_met"] else None,
                            "note": notes.get(q["k"], ""), "example_row": out.get("example_row")})
            print(f"  test/{n} p{q['k']}: " + (f"no number; refuting condition met: {q['refuted_by'][:100]}" if m is None and out["refuted_by_met"]
                  else f"not computable: {out['not_computable'][:100]}" if m is None else
                  f"measured {m}, predicted {q['value']} [{q['low']}, {q['high']}], refuting condition met: {out['refuted_by_met']}"))
        (folder / "tests" / f"{n}.json").write_text(json.dumps({"theory": n, "predictions": results}, indent=1) + "\n")
    (score_tests if args.version == 4 else score)(folder)


def review(folder):
    metrics = folder / ("metrics_v4.json" if args.version == 4 else "metrics_v3.json")
    theories = json.loads(metrics.read_text())["theories"]
    names = sorted((n for n, t in theories.items() if t["state"] == ("survives" if args.version == 4 else "passes")),
                   key=lambda n: -theories[n]["total_gain"])[:3]
    if not names:
        return print("review: no surviving theory")
    keys = {"refutation", "wins_judgement", "rival", "novelty", "import_carries_gain", "verdict"}
    run([job("review", n, {}, {"review.json": folder / "reviews" / f"{n}.json"},
             lambda d: (lambda k: f"missing keys {sorted(k)}" if k else None)(keys - json.loads((d / "review.json").read_text()).keys()),
             mode="repo", round=folder.resolve(), theory=n, metrics=metrics.name) for n in names], folder)
    for n in names:
        print(f"  {n}: {json.loads((folder / 'reviews' / f'{n}.json').read_text())['verdict']}")
    if args.version == 4:
        score_tests(folder)


STAGES = {"split": split, "standing": standing, "inventory": inventory, "targets": targets, "external": external,
          "generate": generate, "null": null, "claims": claims, "score": score, "reverse": reverse, "test": test, "review": review,
          "mechanisms": mechanisms, "develop": develop, "null_tests": null_tests, "score_tests": score_tests, "heldout": heldout}
ALL = {3: ["split", "standing", "inventory", "targets", "external", "generate", "null", "claims", "score", "reverse", "test", "score", "review"],
       4: ["split", "standing", "inventory", "external", "mechanisms", "develop", "null_tests", "test", "score_tests", "heldout", "review"]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path)
    parser.add_argument("stage", choices=[*STAGES, "all"])
    parser.add_argument("--version", type=int, choices=[3, 4], default=4)
    parser.add_argument("--cutoff")
    parser.add_argument("--skip", action="append", default=[])
    parser.add_argument("--from", dest="prev")
    parser.add_argument("--starts", default="all,surprises,across,external,revise")
    parser.add_argument("--n-mechanisms", type=int, default=12)
    parser.add_argument("--model-all")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--min-targets", type=int, default=15)
    args = parser.parse_args()
    for stage in ALL[args.version] if args.stage == "all" else [args.stage]:
        print(f"== {stage}")
        STAGES[stage](args.folder)
