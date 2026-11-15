# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Version 3 of a theory round (.claude/skills/theory/SKILL.md): every model call is a headless Claude run, every check
and the score are code here.

  uv run studies/theory/lib/round.py <round dir> <stage> [options]

Stages, in the order `all` runs them:
  split --cutoff <ISO time> [--skip <word> ...]   check.dump: before.jsonl, after.jsonl
  standing --from <previous round dir>            theories/ (the previous round's passing theories, unchanged,
                                                  except those whose review verdict is refuted or published),
                                                  prior_reviews/, prior_scores.json
  inventory      (opus, repository, read-only)    inventory.md: the stored per-problem row files, no result numbers
  targets        (sonnet)                         targets.jsonl (quote-checked; failing targets dropped),
                                                  targets_blind.jsonl
  external       (opus, papers.py only)           external.md
  generate [--starts all,surprises,across,external,revise]   (opus)
                                                  external_<start>.md, drafts/, theories/r<N>-<start>-<k>.json,
                                                  dropped.json, theories.sha256
  null           (opus)                           predictions/null-1.jsonl, null-2.jsonl
  claims         (opus, one advocate per theory)  claims/<theory>.jsonl
  score          (no model)                       metrics_v3.json and the printed table
  reverse        (sonnet rewrite, opus advocate)  reversed/<theory>.json, claims/<theory>.rev.jsonl, then score
  test           (opus, repository, laptop only)  tests/<theory>/p<k>.py written by the model, run here once:
                                                  tests/<theory>.json, then score
  review         (opus, repository)               reviews/<theory>.json for the top 3 passing theories

Every model call except inventory, test and review runs in an empty job directory outside the repository with only
the Read and Write tools, so no git status, project instructions, memory or board reaches it. A job whose outputs
exist is skipped, so a stopped round resumes. --model-all <model> overrides every stage's model and --min-targets <n>
(default 15) the fewest targets a round accepts: both for smoke tests.
"""
import argparse
import hashlib
import json
import math
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

MODELS = {"inventory": "opus", "targets": "sonnet", "external": "opus", "generate": "opus", "fix": "opus",
          "null": "opus", "claims": "opus", "reverse": "sonnet", "test": "opus", "review": "opus"}
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
                  "Bash(git show:*)", "Bash(aws s3 ls:*)"],
    "test": ["Bash"],
    "review": ["Bash(python3 tools/recall.py:*)", "Bash(python3 tools/exa.py:*)", "Bash(uv run tools/board.py ls:*)",
               "Bash(uv run tools/board.py show:*)", "Bash(git log:*)", "Bash(git show:*)", "Bash(ls:*)", "Bash(cat:*)"],
}
THEORY_KEYS = {"name", "statement", "scope", "parent", "imports", "explains", "conflicts", "rival", "predictions"}
PREDICTION_KEYS = {"experiment", "unit", "value", "low", "high", "refuted_by", "gpu_minutes"}
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


def prompt(stage, **values):
    return string.Template((LIB / "prompts" / f"{stage}.md").read_text()).substitute(values)


def model(stage):
    return args.model_all or MODELS[stage]


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
    (d / "prompt.txt").write_text(j["prompt"])
    out, start = d / "out.txt", time.time()
    with open(d / "prompt.txt") as stdin, open(out, "w") as stdout:
        code = subprocess.run(command(j, folder), stdin=stdin, stdout=stdout, stderr=subprocess.STDOUT,
                              cwd=ROOT if j["mode"] == "repo" else d, timeout=3600).returncode
    if code:
        sys.exit(f"{j['stage']}/{j['name']}: claude exited with {code}; see {out}")
    for rel in j["outputs"]:
        if not (d / rel).exists():
            sys.exit(f"{j['stage']}/{j['name']}: wrote no {rel}; see {out}")
    if j["valid"]:
        try:
            error = j["valid"](d)
        except Exception:
            print(f"{j['stage']}/{j['name']}: malformed output; see {out}", file=sys.stderr)
            raise
        if error:
            sys.exit(f"{j['stage']}/{j['name']}: {error}; see {out}")
    for rel, dest in j["outputs"].items():
        dest.parent.mkdir(parents=True, exist_ok=True)
        if (d / rel).is_dir():
            shutil.copytree(d / rel, dest, dirs_exist_ok=True)
        else:
            shutil.copy(d / rel, dest)
    print(f"  {j['stage']}/{j['name']} ({j['model']}): done in {time.time() - start:.0f} s")


def run(jobs, folder):
    todo = [j for j in jobs if not all(p.exists() for p in j["outputs"].values())]
    for j in jobs:
        if j not in todo:
            print(f"  skip {j['stage']}/{j['name']}: its outputs exist")
    if todo:
        print(f"  running {len(todo)} jobs in parallel")
        with ThreadPoolExecutor(min(args.workers, len(todo))) as pool:
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


def check_theories(folder, drafts, standing):
    """Messages per theory: the v3 form rules, then check.py's quote check."""
    heads = set(HEADING.findall((folder / "external.md").read_text()))
    msgs = {name: [] for name in drafts}
    quotable = {}
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
            if imported.get("source") not in heads:
                m.append(f"{name}.json: import source {imported.get('source')!r} is not a heading id in external.md")
        if t["parent"] is not None and t["parent"] not in standing:
            m.append(f"{name}.json: parent {t['parent']!r} is not a standing theory (standing: {sorted(standing)}, or null)")
        for i, p in enumerate(t["predictions"], 1):
            if PREDICTION_KEYS - p.keys():
                m.append(f"{name}.json: prediction {i} misses keys {sorted(PREDICTION_KEYS - p.keys())}")
            elif not (all(number(p[k]) for k in ("value", "low", "high")) and p["low"] <= p["value"] <= p["high"]):
                m.append(f"{name}.json: prediction {i} needs numbers with low <= value <= high")
        offline = [p for p in t["predictions"] if "recipe" in p]
        if len(offline) < 2 or any(p.get("gpu_minutes") != 0 for p in offline):
            m.append(f"{name}.json: needs at least 2 offline predictions, each with a \"recipe\" and \"gpu_minutes\": 0")
        if all("item" in c and "quote" in c for c in t["explains"] + t["conflicts"]):
            quotable[name] = t
    lines, _ = quote_check(read(folder / "before.jsonl"), [], [], quotable)
    for line in lines:
        msgs[line.split(".json: ")[0]].append(line)
    return msgs


# ---- stages ----

def split(folder):
    if (folder / "before.jsonl").exists():
        return print("skip split: before.jsonl exists")
    if not args.cutoff:
        sys.exit("split needs --cutoff <ISO time>")
    check.dump(folder, args.cutoff, args.skip)


def standing(folder):
    if not args.prev:
        return print("standing: no --from given, so no standing theories")
    if (folder / "prior_scores.json").exists():
        return print("skip standing: prior_scores.json exists")
    prev = Path(args.prev)
    metrics = json.loads((prev / "metrics_v3.json" if (prev / "metrics_v3.json").exists() else prev / "metrics_v2.json").read_text())
    prev_targets = read(prev / "targets.jsonl")
    before = {i["id"] for i in read(folder / "before.jsonl")}
    if late := sorted({t["item"] for t in prev_targets} - before):
        sys.exit(f"the previous round's targets come from items not in before.jsonl: {late}. The cutoff must be after "
                 "every item the previous round held out, or its scores leak held-out numbers.")
    what = {t["id"]: t["what"] for t in prev_targets}
    (folder / "theories").mkdir(exist_ok=True)
    prior = {}
    for name, m in metrics["theories"].items():
        theory = json.loads((prev / "theories" / f"{name}.json").read_text())
        prior[name] = {"statement": theory["statement"], "state": m["state"],
                       "claims": [{**row, "what": what[row["id"]]} for row in m["rows"]]}
        review = prev / "reviews" / f"{name}.json"
        verdict = json.loads(review.read_text())["verdict"] if review.exists() else ""
        if m["state"] == "passes" and verdict.startswith(("refuted", "published")):
            print(f"  not standing: {name} passes but its review says {verdict[:60]!r}")
        elif m["state"] == "passes":
            shutil.copy(prev / "theories" / f"{name}.json", folder / "theories")
            if review.exists():
                (folder / "prior_reviews").mkdir(exist_ok=True)
                shutil.copy(review, folder / "prior_reviews")
            print(f"  standing: {name}")
    (folder / "prior_scores.json").write_text(json.dumps(prior, indent=1) + "\n")


def inventory(folder):
    if (folder / "inventory.md").exists():
        return print("skip inventory: inventory.md exists")
    cutoff = min(i["at"] for i in read(folder / "after.jsonl"))
    run([job("inventory", "inventory", {}, {"inventory.md": folder / "inventory.md"}, mode="repo", cutoff=cutoff)], folder)


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
        heads = [line for line in text.splitlines() if line.startswith("### ")]
        if any(not HEADING.match(h) for h in heads):
            return f"headings not of the form '### <id> — <title, year>': {[h for h in heads if not HEADING.match(h)]}"
        if len(heads) < 10 or text.count("\n- Finding:") != len(heads):
            return f"{len(heads)} headings and {text.count(chr(10) + '- Finding:')} '- Finding:' lines; need 10 or more, one each"
        return None

    run([job("external", "external", {"before.jsonl": folder / "before.jsonl"}, {"external.md": folder / "external.md"},
             valid, mode="papers", papers=LIB / "papers.py")], folder)
    print(f"  external.md: {len(HEADING.findall((folder / 'external.md').read_text()))} findings")


def generate(folder):
    if (folder / "theories.sha256").exists():
        return print("skip generate: theories.sha256 exists")
    starts = args.starts.split(",")
    assert set(starts) <= STARTS.keys(), f"unknown start in {starts}"
    if "revise" in starts and not (folder / "prior_scores.json").exists():
        sys.exit("the revise start needs prior_scores.json from `standing --from`; on a first round drop revise from --starts")
    nn = int(re.search(r"round-(\d+)", folder.name).group(1))
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
    msgs = check_theories(folder, drafts, standing)
    fix_inputs = {"before.jsonl": folder / "before.jsonl", "external.md": folder / "external.md",
                  "inventory.md": folder / "inventory.md", **standing_inputs}
    failing = [n for n in names if msgs[n]]
    for n in failing:
        print(f"  {n} fails the check, sent back once:\n    " + "\n    ".join(msgs[n]))
    run([job("fix", n, {"theory.json": folder / "drafts" / f"{n}.json", **fix_inputs},
             {"theory.json": folder / "drafts" / f"{n}.fix.json"}, lambda d: None if isinstance(json.loads((d / "theory.json").read_text()), dict) else "not a JSON object",
             message="\n".join(msgs[n])) for n in failing], folder)
    fixed = {n: json.loads((folder / "drafts" / f"{n}.fix.json").read_text()) for n in failing}
    again = check_theories(folder, fixed, standing) if fixed else {}
    dropped = {n: m for n, m in again.items() if m}
    for n in names:
        if n not in dropped:
            (folder / "theories" / f"{n}.json").write_text(json.dumps(fixed.get(n, drafts[n]), indent=1) + "\n")
    for n, m in dropped.items():
        print(f"  dropped {n}:\n    " + "\n    ".join(m))
    (folder / "dropped.json").write_text(json.dumps(dropped, indent=1) + "\n")
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  theories/{p.name}\n" for p in sorted((folder / "theories").glob("*.json"))]
    (folder / "theories.sha256").write_text("".join(lines))
    print(f"  {len(lines)} theories ({len(standing)} standing, {len(names) - len(dropped)} new, {len(dropped)} dropped); wrote theories.sha256")


def null(folder):
    ids = target_ids(folder)
    run([job("null", f"null-{k}", {"before.jsonl": folder / "before.jsonl", "targets_blind.jsonl": folder / "targets_blind.jsonl"},
             {"predictions.jsonl": folder / "predictions" / f"null-{k}.jsonl"},
             lambda d: interval_rows(d / "predictions.jsonl", ids, exact=True)) for k in (1, 2)], folder)


def claims(folder):
    ids = target_ids(folder)
    run([job("claims", p.stem, {"theory.json": p, "before.jsonl": folder / "before.jsonl", "targets_blind.jsonl": folder / "targets_blind.jsonl"},
             {"claims.jsonl": folder / "claims" / f"{p.stem}.jsonl"},
             lambda d: interval_rows(d / "claims.jsonl", ids, exact=False), rule=FREE_RULE)
         for p in sorted((folder / "theories").glob("*.json"))], folder)


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
    names = candidates(folder)
    jobs = []
    for n in names:
        if (folder / "tests" / f"{n}.json").exists():
            print(f"  skip test/{n}: tests/{n}.json exists")
            continue
        theory = json.loads((folder / "theories" / f"{n}.json").read_text())
        offline = [{"k": k, **p} for k, p in enumerate(theory["predictions"], 1) if "recipe" in p]
        if not offline:
            print(f"  test/{n}: no offline prediction")
            (folder / "tests").mkdir(exist_ok=True)
            (folder / "tests" / f"{n}.json").write_text(json.dumps({"theory": n, "predictions": []}, indent=1) + "\n")
            continue

        def valid(d, n=n, offline=offline):
            missing = [q["k"] for q in offline if not (d / "tests" / n / f"p{q['k']}.py").exists()]
            return f"no script for predictions {missing}" if missing else None if isinstance(json.loads((d / "notes.json").read_text()), list) else "notes.json is not a list"

        jobs.append((n, offline, job("test", n, {"theory.json": folder / "theories" / f"{n}.json", "offline.json": json.dumps(offline, indent=1)},
                                     {f"tests/{n}": folder / "tests" / n, "notes.json": folder / "tests" / n / "notes.json"}, valid,
                                     mode="repo", theory=n, inventory=(folder / "inventory.md").resolve())))
    run([j for _, _, j in jobs], folder)
    for n, offline, _ in jobs:
        notes = {e["k"]: e["note"] for e in json.loads((folder / "tests" / n / "notes.json").read_text())}
        results = []
        for q in offline:
            script = folder / "tests" / n / f"p{q['k']}.py"
            p = subprocess.run(["python3", str(script.resolve())], cwd=ROOT, capture_output=True, text=True, timeout=1800)
            (script.with_suffix(".out.txt")).write_text(p.stdout + p.stderr)
            if p.returncode:
                sys.exit(f"{script} failed (exit {p.returncode}); output in {script.with_suffix('.out.txt')}")
            out = json.loads(p.stdout.strip().splitlines()[-1])
            m = out["measured"]
            results.append({"k": q["k"], "experiment": q["experiment"], "recipe": q["recipe"], "script": str(script.relative_to(folder)),
                            "value": q["value"], "low": q["low"], "high": q["high"], "measured": m,
                            "inside": None if m is None else q["low"] <= m <= q["high"], "refuted_by": q["refuted_by"],
                            "refuted_by_met": out["refuted_by_met"], "alt_measured": out["alt_measured"],
                            "note": notes.get(q["k"], ""), "example_row": out["example_row"]})
            print(f"  test/{n} p{q['k']}: measured {m}, predicted {q['value']} [{q['low']}, {q['high']}], refuted_by met: {out['refuted_by_met']}")
        (folder / "tests" / f"{n}.json").write_text(json.dumps({"theory": n, "predictions": results}, indent=1) + "\n")
    score(folder)


def review(folder):
    theories = json.loads((folder / "metrics_v3.json").read_text())["theories"]
    names = sorted((n for n, t in theories.items() if t["state"] == "passes"), key=lambda n: -theories[n]["total_gain"])[:3]
    if not names:
        return print("review: no passing theory")
    keys = {"refutation", "wins_judgement", "rival", "novelty", "import_carries_gain", "verdict"}
    run([job("review", n, {}, {"review.json": folder / "reviews" / f"{n}.json"},
             lambda d: (lambda k: f"missing keys {sorted(k)}" if k else None)(keys - json.loads((d / "review.json").read_text()).keys()),
             mode="repo", round=folder.resolve(), theory=n) for n in names], folder)
    for n in names:
        print(f"  {n}: {json.loads((folder / 'reviews' / f'{n}.json').read_text())['verdict']}")


STAGES = {"split": split, "standing": standing, "inventory": inventory, "targets": targets, "external": external,
          "generate": generate, "null": null, "claims": claims, "score": score, "reverse": reverse, "test": test, "review": review}
ALL = ["split", "standing", "inventory", "targets", "external", "generate", "null", "claims", "score", "reverse", "test", "score", "review"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path)
    parser.add_argument("stage", choices=[*STAGES, "all"])
    parser.add_argument("--cutoff")
    parser.add_argument("--skip", action="append", default=[])
    parser.add_argument("--from", dest="prev")
    parser.add_argument("--starts", default="all,surprises,across,external,revise")
    parser.add_argument("--model-all")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--min-targets", type=int, default=15)
    args = parser.parse_args()
    for stage in ALL if args.stage == "all" else [args.stage]:
        print(f"== {stage}")
        STAGES[stage](args.folder)
