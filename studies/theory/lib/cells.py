"""Inputs, checks, ranking and cells.md of `forecast.py cells` (studies/theory/README.md, "Cells designed by the
theories"). forecast.py runs the jobs; everything here is plain code on their files."""
import ast
import json
import re
import statistics
from pathlib import Path

import round as engine

ROOT = engine.ROOT
JOBS = ROOT / "studies/rlneurons/jobs"
JOB_FILES = {p.stem: p for d in (JOBS, ROOT / "studies/theory/jobs") for p in sorted(d.glob("*.py"))}  # the job files a cell may run
SETS = {"hard328": 328, "MATH-500": 500}  # the two sets of the no-reward track, as the board's score: lines name them
CELL_KEYS = ("model", "prompt", "set", "n", "sampling", "samples", "grader", "cap")
NUMS = ("value", "low", "high", "against_value", "gpu_minutes")
THEORY_FILES = "\n- theories/: the full file of each theory (statement, scope, what it explains, predictions)."
FAMILY = ("- mechanisms.json: your family of mechanisms (id, statement).{files}\nForecast from each mechanism separately, "
          "as written: say in the reason which part of it gives the number. Where a mechanism implies nothing about a "
          "readout, do not guess: answer \"theory says nothing\" for it.\n")
IMPORT = re.compile(r"from studies\.rlneurons\.jobs(?:\.(\w+))? import (\w+)")
JOB_REF = re.compile(r"jobs/(\w+)\.py|jobs\.(\w+)")
NOTHING = (' For a readout a mechanism says nothing about, write {"mechanism": "<id>", "readout": "m01-r2", "value": null, '
           '"low": null, "high": null, "reason": "theory says nothing"}.')


def families(runs, rnd):
    """{family: {lens, mechanisms: [{id, statement}]}}: each forecast run's mechanisms (ids <run>/f2-mNN) and the
    theories of round folder rnd that are not refuted (one family named after the round)."""
    fam = {r.name: {"lens": json.loads((r / "run.json").read_text())["lens"],
                    "mechanisms": [{"id": f"{r.name}/{m['id']}", "statement": m["statement"], "rests_on": m["rests_on"]}
                                   for m in json.loads((r / "mechanisms.json").read_text())["mechanisms"]]} for r in runs}
    m = json.loads((rnd / "metrics_v4.json").read_text())["theories"]
    fam[rnd.name] = {"lens": "theories of the engine's newest round that are not refuted", "mechanisms": [
        {"id": n, "statement": json.loads((rnd / "theories" / f"{n}.json").read_text())["statement"]} for n in m if m[n]["state"] != "refuted"]}
    return fam


def family_inputs(name, f, rnd):
    """mechanisms.json for a family job; the round's family also gets its full theory files."""
    files = {f"theories/{m['id']}.json": rnd / "theories" / f"{m['id']}.json" for m in f["mechanisms"]} if name == rnd.name else {}
    return {"mechanisms.json": json.dumps({"family": name, **f}, indent=1), **files}


def choices(node, names):
    """The values of a choices= expression: a tuple or list of strings (with *NAME), NAME, or sorted/list/set(...)
    of those, NAME being a module-level dict, list, tuple or set of strings; None when it is anything else."""
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        parts = [choices(e.value, names) if isinstance(e, ast.Starred) else [e.value] if isinstance(e, ast.Constant) else None for e in node.elts]
        return None if None in parts else [v for part in parts for v in part]
    if isinstance(node, ast.Name):
        return names.get(node.id)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("sorted", "list", "set") and len(node.args) == 1:
        return choices(node.args[0], names)
    return None


def job_flags():
    """{job module: {flag: allowed values or None}} from the add_argument calls of each studies/rlneurons/jobs/*.py
    (parsed, not run); a file with none takes the flags of the job modules it imports, without their values
    (run_fresh.py runs run_cell.py's main and adds a set)."""
    texts, own = {n: p.read_text() for n, p in JOB_FILES.items()}, {}
    for n, t in texts.items():
        tree, own[n] = ast.parse(t), {}
        names = {a.targets[0].id: [k.value for k in (a.value.keys if isinstance(a.value, ast.Dict) else a.value.elts) if isinstance(k, ast.Constant)]
                 for a in tree.body if isinstance(a, ast.Assign) and isinstance(a.targets[0], ast.Name)
                 and isinstance(a.value, (ast.Dict, ast.List, ast.Tuple, ast.Set))}
        for c in ast.walk(tree):
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "add_argument":
                allowed = next((choices(k.value, names) for k in c.keywords if k.arg == "choices"), None)
                own[n] |= {a.value: allowed for a in c.args if isinstance(a, ast.Constant) and str(a.value).startswith("-")}
    return {n: own[n] or {f: None for a, b in IMPORT.findall(texts[n]) for f in own.get(a or b, {})} for n in texts}


def command_errors(cmd, flags):
    """Every job file a cell's command names (jobs/<name>.py or the module jobs.<name>) exists and takes every flag
    written after it, up to the next &&, ;, | or double quote, with a value among the flag's choices when it has them;
    a single-quoted value counts as one word. A command that runs git is rejected (job machines have no .git)."""
    git = ["the command runs git ($(git ...) or rev-parse): job machines have no .git folder; write --commit COMMIT_SHA, which the "
           "coordinator replaces with the pushed commit's full sha at submission"] if re.search(r"\$\(git|`git|rev-parse", cmd) else []
    cmd = re.sub(r"\$?'([^']*)'", lambda q: q[1] if q[1] and not re.search(r"\s", q[1]) else "TEXT", cmd)  # a quoted value is one word
    refs, errors = list(JOB_REF.finditer(cmd)), git
    for m in refs:
        name = m.group(1) or m.group(2)
        if name not in flags:
            errors.append(f"studies/rlneurons/jobs/{name}.py does not exist")
            continue
        words = re.split(r"&&|;|\||\"|'", cmd[m.end():])[0].split()
        for k, w in enumerate(words):
            if not re.fullmatch(r"--?[A-Za-z][\w-]*(=.*)?", w):
                continue
            flag, value = w.split("=")[0], w.split("=", 1)[1] if "=" in w else words[k + 1] if k + 1 < len(words) else None
            if flag not in flags[name]:
                errors.append(f"jobs/{name}.py has no flag {flag}")
            elif flags[name][flag] is not None and value not in map(str, flags[name][flag]):
                errors.append(f"jobs/{name}.py {flag} takes {', '.join(map(str, flags[name][flag]))}; not {value}")
    return errors if refs else git + ["the command names no job file of studies/rlneurons/jobs/"]


def flags_once(check):
    """valid(d) for engine.run: the first check (before the send-back) also checks the commands against the job files'
    flags; the second does not, so a cell whose command still fails is dropped afterwards and the round goes on."""
    calls = []

    def valid(d):
        calls.append(d)
        return check(d, job_flags() if len(calls) == 1 else None)
    return valid


def jobs_md():
    """The rows of studies/rlneurons/README.md that describe a job file, its "How to run" section, and per job file
    its flags (extracted by job_flags) and its add_argument lines (no other code)."""
    readme = (ROOT / "studies/rlneurons/README.md").read_text()
    rows = [line for line in readme.split("\n## Definitions")[0].splitlines() if line.startswith("|") and "jobs/" in line]
    howto = readme.split("\n## How to run")[1].split("\n## Raw answers")[0]
    fl = job_flags()
    flags = [f"### {p.relative_to(ROOT)}\n\nFlags (no others exist): {', '.join(f + (' {' + ', '.join(map(str, v)) + '}' if v else '') for f, v in sorted(fl[p.stem].items())) or 'none'}\n\n"
             + "\n".join(line.strip() for line in p.read_text().splitlines() if "add_argument(" in line) for p in JOB_FILES.values()]
    free = (ROOT / "studies/theory/jobs/free_cell.py").read_text().split('"""')[1]
    return "\n".join(["# Job files (studies/rlneurons/README.md)\n", *rows, "\n## How to run" + howto, "\n## Flags of each job file\n", *flags,
                      "\n## studies/theory/jobs/free_cell.py (no-reward routes; run as python -m studies.theory.jobs.free_cell)\n", free]) + "\n"


def check_proposals(d, mids, all_ids, board_ids, flags=None):
    """A proposing job's cells.json: one cell per mechanism, complete, the alternative another listed mechanism whose
    number lies outside the interval, minutes in (0, 120], an existing job file, a best base count for base_only; with
    flags ({job: flags}), a command whose job files and flags exist."""
    ps = json.loads((d / "cells.json").read_text())["cells"]
    errors = [] if sorted(p["mechanism"] for p in ps) == sorted(mids) else [f"needs exactly one cell per mechanism: {sorted(mids)}"]
    for p in ps:
        e = [f"cell misses {k}" for k in CELL_KEYS if not str(p["cell"].get(k, "")).strip()]
        e += [f"missing {k}" for k in ("job", "command", "readout", "unit", "why") if not str(p.get(k, "")).strip()]
        if p["against"] not in all_ids or p["against"] == p["mechanism"]:
            e.append("against must be the id of another mechanism of all_mechanisms.json")
        if not all(engine.number(p.get(k)) for k in NUMS):
            e.append(f"{', '.join(NUMS)} must be numbers")
        elif not p["low"] <= p["value"] <= p["high"] or p["low"] <= p["against_value"] <= p["high"] or not 0 < p["gpu_minutes"] <= 120:
            e.append("needs low <= value <= high, against_value outside [low, high] and 0 < gpu_minutes <= 120")
        if Path(p["job"]).stem not in JOB_FILES:
            e.append(f"job {p['job']!r} is not a file of studies/rlneurons/jobs/ or studies/theory/jobs/")
        b = p.get("best_base")
        if not isinstance(p.get("base_only"), bool) or p["base_only"] and not (b and engine.number(b.get("value")) and b.get("item") in board_ids):
            e.append("base_only must be true or false; a base_only cell needs best_base with a number and the id of a board.jsonl item")
        e += command_errors(p["command"], flags) if flags else []
        errors += [f"{p['mechanism']}: {x}" for x in e]
    return "; ".join(errors) or None


def check_merged(d, pids, flags=None):
    """The merge job's merged.json: every proposal in exactly one readout, ids distinct, cells complete; with flags, a
    command whose job files and flags exist."""
    cs = json.loads((d / "merged.json").read_text())["cells"]
    froms = [i for c in cs for r in c["readouts"] for i in r["from"]]
    errors = [] if sorted(froms) == sorted(pids) else [f"every proposal id must be in exactly one readout's from: missing "
                                                       f"{sorted(set(pids) - set(froms))}, repeated or unknown {sorted({i for i in froms if froms.count(i) > 1 or i not in pids})}"]
    ids = [c["id"] for c in cs] + [r["id"] for c in cs for r in c["readouts"]]
    errors += [] if len(set(ids)) == len(ids) else ["cell and readout ids must not repeat"]
    errors += [f"{c['id']}: cell misses {k}" for c in cs for k in CELL_KEYS if not str(c["cell"].get(k, "")).strip()]
    errors += [f"{c['id']}: {e}" for c in cs for e in command_errors(c["command"], flags)] if flags else []
    return "; ".join(errors) or None


def check_forecasts(d, rids, mids):
    """One forecast per (mechanism, readout); mids is [None] for a reader, whose rows carry no mechanism and need numbers."""
    fs = json.loads((d / "forecasts.json").read_text())["forecasts"]
    if sorted((str(f.get("mechanism")), f["readout"]) for f in fs) != sorted((str(m), r) for m in mids for r in rids):
        return f"forecasts.json must hold exactly one forecast per {'mechanism of mechanisms.json and ' if mids != [None] else ''}readout id of cells.json"
    said = [f for f in fs if not (mids != [None] and f["value"] is None and f["low"] is None and f["high"] is None)]
    bad = [f"{f.get('mechanism', '')} {f['readout']}".strip() for f in said
           if not all(engine.number(f.get(k)) for k in ("value", "low", "high")) or not f["low"] <= f["value"] <= f["high"]]
    return f"value, low, high must be numbers with low <= value <= high (or all null for \"theory says nothing\") on {bad}" if bad else None


def attach(merged, by_id):
    """base_only (every proposal in the cell is), GPU minutes (the largest proposal's) and per readout the best known
    base count (the highest a base_only proposal gave) come from the proposals, not from the merge job."""
    for c in merged:
        ps = [by_id[i] for r in c["readouts"] for i in r["from"]]
        c["base_only"], c["gpu_minutes"] = all(p["base_only"] for p in ps), max(p["gpu_minutes"] for p in ps)
        for r in c["readouts"]:
            r["best_base"] = max((by_id[i]["best_base"] for i in r["from"]), key=lambda b: b["value"]) if c["base_only"] else None


def blind(merged):
    """The merged cells as the forecasters see them: no proposer, value, interval, alternative or reason."""
    return [{"id": c["id"], "cell": c["cell"], "readouts": [{"id": r["id"], "readout": r["readout"], "unit": r["unit"],
                                                             **({"best_base": r["best_base"]} if r["best_base"] else {})} for r in c["readouts"]]}
            for c in merged]


def apart(a, b):
    return a["value"] is not None and b["value"] is not None and (a["high"] < b["low"] or b["high"] < a["low"])


def split(fs, fam_of):
    """A split of one readout's forecasts {forecaster: forecast}: the first threshold t (a forecaster's high) with the
    forecasters entirely at or below t from 2 or more families and those entirely above t from 2 or more families;
    {at, low, high} or None."""
    for t in sorted({f["high"] for f in fs.values()}):
        low, high = [n for n, f in fs.items() if f["high"] <= t], [n for n, f in fs.items() if f["low"] > t]
        if len({fam_of[n] for n in low}) >= 2 and len({fam_of[n] for n in high}) >= 2:
            return {"at": t, "low": low, "high": high}
    return None


def said(F, rid, left_out=()):
    return {n: F[n][rid] for n in F if n not in left_out and F[n][rid]["value"] is not None}


def rank(merged, F, fam_of, left_out=()):
    """F: {forecaster: {readout id: forecast}}; fam_of: {forecaster: family}; left_out: forecasters at or below -2 nats.
    Adds to each cell its splits (one per readout whose other forecasters split with 2 or more families on each side),
    their number (separation), that number per GPU minute, and for each readout with a best base count the highest
    forecast and its gain over that count."""
    for c in merged:
        c["splits"] = [{"readout": r["id"], **x} for r in c["readouts"] if (x := split(said(F, r["id"], left_out), fam_of))]
        c["separation"], c["per_minute"] = len(c["splits"]), round(len(c["splits"]) / c["gpu_minutes"], 4)
        for r in (r for r in c["readouts"] if r["best_base"]):
            top = max(said(F, r["id"]), key=lambda n: F[n][r["id"]]["value"])
            r["top"] = {"forecaster": top, "value": F[top][r["id"]]["value"], "gain": round(F[top][r["id"]]["value"] - r["best_base"]["value"], 3)}


# ---- the no-reward track (version 11 baselines) ----

TABLE = ROOT / "studies/rlneurons/results/table/hard328-02/table.json"  # hard328 configurations with per-problem vectors
TABLE_MODEL = {"base": "base", "think_sft": "think", "rl": "rl"}  # route model -> key prefix of table.json rows


def table_rows():
    """The rows of table.json for the base, Think-SFT and RL (key, name, samples, tokens, right of 328, MATH-500 right),
    each with its per-problem vector of right answers on hard328 (fractions for means over samples)."""
    t = json.loads(TABLE.read_text())
    return [{"key": r["key"], "name": r["name"], "samples": r["n_samples"], "tokens": round(r["tokens"]), "right": r["right"],
             "math500": r.get("math500", {}).get("right"), "source": r["source"], "vector": t["per_problem_right"][r["key"]]}
            for r in t["rows"] if r["key"].split("|")[0] in TABLE_MODEL.values()]


def high_on_math500(model, rows):
    """A model whose one-sample MATH-500 count in table.json is above 90 %: MATH-500 is no readout for it."""
    return next(r["math500"] for r in rows if r["key"] == f"{TABLE_MODEL[model]}|single") > 450


def route_arms(model, rows):
    return [("route", "hard328"), ("rl", "hard328")] + ([] if high_on_math500(model, rows) else [("route", "MATH-500")])


def subset(text, n_set):
    """Positions of a subset of a set: "all" or a shard "k/N" (positions k, k+N, ...)."""
    if text == "all":
        return list(range(n_set))
    k, n = (int(x) for x in text.split("/"))
    return list(range(n_set))[k::n]


def baseline(rows, model, tokens, positions):
    """The table row of the model at the nearest token count, its right answers on the positions (measured from its
    per-problem vector) and the binomial sd of that subset count; None when the model has no row."""
    mine = [r for r in rows if r["key"].startswith(TABLE_MODEL[model] + "|")]
    if not mine:
        return None
    b = min(mine, key=lambda r: (abs(r["tokens"] - tokens), -r["right"]))
    n, c = len(positions), sum(b["vector"][i] for i in positions)
    return {"value": round(c, 2), "sd": round(max((n * (c / n) * (1 - c / n)) ** 0.5, 0.5), 2), "row": b["name"], "tokens": b["tokens"],
            "source": f"{TABLE.relative_to(ROOT)} {b['key']} ({b['source']})", "n": n}


def check_routes(d, mids, rows, flags=None):
    """A route job's route.json: one no-reward route from one of the family's mechanisms; model base or think_sft;
    readouts route and RL on hard328 (a subset "all" or "k/N"), and route on MATH-500 when the model is at or below
    90 % there; ordered numbers; tokens and minutes; with flags, both commands pass the flag check."""
    r = json.loads((d / "route.json").read_text())["route"]
    e = [] if r.get("mechanism") in mids else [f"mechanism must be one of {mids}"]
    e += [f"missing {k}" for k in ("change", "command", "rl_command", "gap_parts", "why") if not str(r.get(k, "")).strip()]
    if r.get("model") not in ("base", "think_sft"):
        return "; ".join(e + ["model must be base or think_sft"])
    e += [] if engine.number(r.get("tokens")) and r["tokens"] > 0 and engine.number(r.get("gpu_minutes")) and 0 < r["gpu_minutes"] <= 240 else [
        "tokens (generated tokens per problem, all samples) > 0 and 0 < gpu_minutes <= 240"]
    rs, arms = r.get("readouts", []), route_arms(r["model"], rows)
    if sorted((x.get("arm"), x.get("set")) for x in rs) != sorted(arms):
        e.append(f"readouts must be exactly one per (arm, set) of {arms}")
    e += [f"readout {x.get('arm')} {x.get('set')}: numbers value, low, high with low <= value <= high, n in 1..{SETS.get(x.get('set'))}, and readout text"
          for x in rs if not (all(engine.number(x.get(k)) for k in ("value", "low", "high", "n")) and x["low"] <= x["value"] <= x["high"]
                              and 0 < x["n"] <= SETS.get(x.get("set"), 0) and str(x.get("readout", "")).strip())]
    e += [f"readout {x['arm']} hard328: \"subset\" must be \"all\" or a shard \"k/N\" of the 328 with n equal to its size"
          for x in rs if x.get("set") == "hard328" and not (re.fullmatch(r"all|\d+/\d+", str(x.get("subset"))) and len(subset(x["subset"], 328)) == x.get("n"))]
    e += [f"command: {x}" for x in command_errors(r["command"], flags)] + [f"rl_command: {x}" for x in command_errors(r["rl_command"], flags)] if flags else []
    return "; ".join(e) or None


def route_cells(routes, rows, prefix):
    """Routes as cells for the blind forecast: id <prefix>-n01, readouts -r1 ... (route hard328, RL hard328, route
    MATH-500 when there is one); the route's hard328 readout carries its baseline (best_base: the stored subset count)."""
    out = []
    for k, r in enumerate(routes, 1):
        cid, arms = f"{prefix}-n{k:02d}", route_arms(r["model"], rows)
        rs = sorted(r["readouts"], key=lambda x: arms.index((x["arm"], x["set"])))
        out.append({"id": cid, "family": r["family"], "mechanism": r["mechanism"], "model": r["model"], "change": r["change"], "tokens": r["tokens"],
                    "gpu_minutes": r["gpu_minutes"], "command": r["command"], "rl_command": r["rl_command"], "gap_parts": r["gap_parts"], "why": r["why"],
                    "readouts": [{"id": f"{cid}-r{j}", **x, "unit": f"right answers of {x['n']}",
                                  "best_base": baseline(rows, r["model"], r["tokens"], subset(x["subset"], 328))
                                  if (x["arm"], x["set"]) == ("route", "hard328") else None} for j, x in enumerate(rs, 1)]})
    return out


def blind_routes(routes):
    """What the forecasters see of a route: the change, model, tokens, commands and readouts; no proposer numbers."""
    return [{"id": c["id"], "no_reward_route": c["change"], "model": c["model"], "tokens_per_problem": c["tokens"], "command": c["command"],
             "rl_command": c["rl_command"], "readouts": [{k: x[k] for k in ("id", "arm", "set", "n", "readout", "unit")}
                                                        | ({"best_base": x["best_base"]} if x["best_base"] else {}) for x in c["readouts"]]} for c in routes]


def rank_routes(routes, F, left_out=()):
    """Per readout the median forecast (forecasters not left out); a route's score is the margin of its hard328 readout,
    (median - stored subset count) / sd of that count; None ("no baseline") when the model has no stored rows."""
    for c in routes:
        for x in c["readouts"]:
            vals = [f["value"] for f in said(F, x["id"], left_out).values()]
            x["median"] = statistics.median(vals) if vals else None
            if x["best_base"]:
                x["gain"] = None if x["median"] is None else round((x["median"] - x["best_base"]["value"]) / x["best_base"]["sd"], 2)
        c["score"] = next((x["gain"] for x in c["readouts"] if x["best_base"]), None)


def margin_text(x):
    return "no baseline" if x is None else f"{x:+g} sd"


def route_md(c, F, fam_of, left_out=()):
    md = [f"\n### {c['id']} ({c['family']}, {c['mechanism']}): {c['change']}\n\nModel {c['model']}, {c['tokens']:g} tokens per problem, "
          f"{c['gpu_minutes']:g} GPU minutes (proposer's guess). Margin {margin_text(c['score'])}."
          f"\n\nWhy, by the gap's parts: {c['gap_parts']} {c['why']}\n\nCommand: `{c['command']}`\n\nRL arm: `{c['rl_command']}`\n"]
    for x in c["readouts"]:
        b = x["best_base"]
        md.append(f"\n#### {x['id']}: {x['arm']} on {x['set']} ({x.get('subset', 'subset as stated')}), {x['readout']} (of {x['n']})\n\nProposer {x['value']:g} "
                  f"[{x['low']:g}, {x['high']:g}]. Median forecast {g(x['median'])}" + (
                      f"; stored {b['value']:g} of {b['n']} (sd {b['sd']:g}; {b['row']}, {b['tokens']} tokens; {b['source']}); margin {g(x['gain'])} sd." if b
                      else "; no baseline.") + "\n")
        md += ["| forecaster | family | value | 90 % interval |\n|---|---|---|---|"] + [
            f"| {n}{' (left out)' if n in left_out else ''} | {fam_of[n]} | {f['value']:g} | [{f['low']:g}, {f['high']:g}] |" for n, f in said(F, x["id"]).items()]
    return md


def g(x):
    return "nothing" if x is None else f"{x:g}"


def split_text(c):
    return "".join(f"; {x['readout']} at {x['at']:g}: {', '.join(x['low'])} below, {', '.join(x['high'])} above" for x in c["splits"])


def cell_md(c, by_id, F, fam_of):
    """One merged cell: the run and its command, then per readout the proposals (with the alternative's own blind
    forecast) and every forecaster's number beside the forecasters of other families it does not overlap."""
    md = [f"\n### {c['id']}: {c['cell']['model']}; {c['cell']['prompt']}; {c['cell']['set']}, n {c['cell']['n']}"
          f"{' (base only)' if c['base_only'] else ''}\n\nGPU minutes {c['gpu_minutes']:g} (proposers' guess). Separation "
          f"{c['separation']} readouts split with 2 or more families on each side, {c['per_minute']:g} per minute"
          f"{split_text(c)}. Job `{c['job']}`.\n\nCell: {json.dumps(c['cell'])}\n\n"
          f"Command: `{c['command']}`\n"]
    for r in c["readouts"]:
        md.append(f"\n#### {r['id']}: {r['readout']} ({r['unit']})\n")
        if b := r["best_base"]:
            md.append(f"Best known base count given to the forecasters: {b['value']:g} ({b['item']}{'; ' + b['note'] if b.get('note') else ''}). "
                      f"Highest forecast: {r['top']['forecaster']} {r['top']['value']:g} ({r['top']['gain']:+g}).\n")
        md += [f"- proposed by {p['mechanism']} ({p['id']}): {p['value']:g} [{p['low']:g}, {p['high']:g}]; says {p['against']} gives "
               f"{p['against_value']:g} (its blind forecast: {g(F[p['against']][r['id']]['value'])}). {p['why']}" for p in (by_id[i] for i in r["from"])]
        md.append("\n| forecaster | family | value | 90 % interval | does not overlap with |\n|---|---|---|---|---|")
        named = said(F, r["id"])
        for n, f in named.items():
            other = [m for m in named if fam_of[m] != fam_of[n] and apart(f, named[m])]
            md.append(f"| {n} | {fam_of[n]} | {f['value']:g} | [{f['low']:g}, {f['high']:g}] | {', '.join(other)} |")
        md.append(f"\nTheory says nothing: {', '.join(n for n in F if n not in named) or 'none'}.\n")
    return md


def cells_md(title, head, props, merged, F, fam_of, routes=(), left_out=()):
    """cells.md: head, counts of splitting cells and routes above their baseline, every merged cell in one table, list A (top 10 by
    separation per GPU minute), list B (base-only cells by the highest forecast minus the best known base count) and
    list C (no-reward routes by the margin of the median forecast over the stored subset count, in its sd)."""
    by_id = {p["id"]: p for p in props}
    by_sep = sorted(merged, key=lambda c: -c["per_minute"])
    base = sorted((c for c in merged if c["base_only"]), key=lambda c: -max(r["top"]["gain"] for r in c["readouts"]))
    by_score = sorted(routes, key=lambda c: -(c["score"] if c["score"] is not None else -1e9))
    w1, w3 = [c["id"] for c in routes if (c["score"] or 0) > 0], [c["id"] for c in merged if c["separation"]]
    md = [f"# {title}\n\n{head}\n", f"Left out of the ranking (record at or below -2 nats): {', '.join(sorted(left_out)) or 'none'}.\n",
          f"- Routes: {len(w1)} of {len(routes)} have a median forecast above the stored subset count of the row at the nearest tokens "
          f"({', '.join(w1) or 'none'}); {sum(c['score'] is None for c in routes)} have no baseline.",
          f"- Cells: {len(w3)} of {len(merged)} have a readout that splits with 2 or more families on each side ({', '.join(w3) or 'none'}).\n",
          "## Every merged cell\n\n| cell | model | prompt | set | n | base only | GPU minutes | separation | per minute |\n|---|---|---|---|---|---|---|---|---|"]
    md += [f"| {c['id']} | {c['cell']['model']} | {c['cell']['prompt']} | {c['cell']['set']} | {c['cell']['n']} | {'yes' if c['base_only'] else ''} | "
           f"{c['gpu_minutes']:g} | {c['separation']} | {c['per_minute']:g} |" for c in by_sep]
    md.append("\n## List A: top 10 by separation per GPU minute")
    md += [line for c in by_sep[:10] for line in cell_md(c, by_id, F, fam_of)]
    md.append("\n## List B: base-only cells, top 10 by the highest forecast of right answers minus the best known base count")
    md += [line for c in base[:10] for line in cell_md(c, by_id, F, fam_of)]
    md.append("\n## List C: no-reward routes by the margin of the median forecast over the stored subset count of the row at the nearest tokens, in sd")
    md += [line for c in by_score for line in route_md(c, F, fam_of, left_out)]
    return "\n".join(md) + "\n"
