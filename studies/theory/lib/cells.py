"""Inputs, checks, ranking and cells.md of `forecast.py cells` (studies/theory/README.md, "Cells designed by the
theories"). forecast.py runs the jobs; everything here is plain code on their files."""
import itertools
import json
from pathlib import Path

import round as engine

ROOT = engine.ROOT
JOBS = ROOT / "studies/rlneurons/jobs"
CELL_KEYS = ("model", "prompt", "set", "n", "sampling", "samples", "grader", "cap")
NUMS = ("value", "low", "high", "against_value", "gpu_minutes")
THEORY_FILES = "\n- theories/: the full file of each theory (statement, scope, what it explains, predictions)."
FAMILY = ("- mechanisms.json: your family of mechanisms (id, statement).{files}\nForecast from each mechanism separately, "
          "as written: say in the reason which part of it gives the number. Where a mechanism implies nothing about a "
          "readout, do not guess: answer \"theory says nothing\" for it.\n")
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


def jobs_md():
    """The rows of studies/rlneurons/README.md that describe a job file, its "How to run" section, and every job
    file's add_argument lines (flags only, no code)."""
    readme = (ROOT / "studies/rlneurons/README.md").read_text()
    rows = [line for line in readme.split("\n## Definitions")[0].splitlines() if line.startswith("|") and "jobs/" in line]
    howto = readme.split("\n## How to run")[1].split("\n## Raw answers")[0]
    flags = [f"### jobs/{p.name}\n\n" + "\n".join(line.strip() for line in p.read_text().splitlines() if "add_argument(" in line)
             for p in sorted(JOBS.glob("*.py"))]
    return "\n".join(["# Job files (studies/rlneurons/README.md)\n", *rows, "\n## How to run" + howto, "\n## Flags of each job file\n", *flags]) + "\n"


def check_proposals(d, mids, all_ids, board_ids):
    """A proposing job's cells.json: one cell per mechanism, complete, the alternative another listed mechanism whose
    number lies outside the interval, minutes in (0, 120], an existing job file, a best base count for base_only."""
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
        if not (JOBS / Path(p["job"]).name).is_file():
            e.append(f"job {p['job']!r} is not a file of studies/rlneurons/jobs/")
        b = p.get("best_base")
        if not isinstance(p.get("base_only"), bool) or p["base_only"] and not (b and engine.number(b.get("value")) and b.get("item") in board_ids):
            e.append("base_only must be true or false; a base_only cell needs best_base with a number and the id of a board.jsonl item")
        errors += [f"{p['mechanism']}: {x}" for x in e]
    return "; ".join(errors) or None


def check_merged(d, pids):
    """The merge job's merged.json: every proposal in exactly one readout, ids distinct, cells complete."""
    cs = json.loads((d / "merged.json").read_text())["cells"]
    froms = [i for c in cs for r in c["readouts"] for i in r["from"]]
    errors = [] if sorted(froms) == sorted(pids) else [f"every proposal id must be in exactly one readout's from: missing "
                                                       f"{sorted(set(pids) - set(froms))}, repeated or unknown {sorted({i for i in froms if froms.count(i) > 1 or i not in pids})}"]
    ids = [c["id"] for c in cs] + [r["id"] for c in cs for r in c["readouts"]]
    errors += [] if len(set(ids)) == len(ids) else ["cell and readout ids must not repeat"]
    errors += [f"{c['id']}: cell misses {k}" for c in cs for k in CELL_KEYS if not str(c["cell"].get(k, "")).strip()]
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


def rank(merged, F, fam_of):
    """F: {forecaster: {readout id: forecast}}; fam_of: {forecaster: family}. Adds to each cell the pairs of forecasters
    from different families whose intervals do not overlap (over its readouts), their number, that number per GPU
    minute, and for each readout with a best base count the highest forecast and its gain over that count."""
    for c in merged:
        c["pairs"] = [[r["id"], a, b] for r in c["readouts"] for a, b in itertools.combinations(F, 2)
                      if fam_of[a] != fam_of[b] and apart(F[a][r["id"]], F[b][r["id"]])]
        c["separation"], c["per_minute"] = len(c["pairs"]), round(len(c["pairs"]) / c["gpu_minutes"], 4)
        for r in (r for r in c["readouts"] if r["best_base"]):
            top = max((n for n in F if F[n][r["id"]]["value"] is not None), key=lambda n: F[n][r["id"]]["value"])
            r["top"] = {"forecaster": top, "value": F[top][r["id"]]["value"], "gain": round(F[top][r["id"]]["value"] - r["best_base"]["value"], 3)}


def g(x):
    return "nothing" if x is None else f"{x:g}"


def cell_md(c, by_id, F, fam_of):
    """One merged cell: the run and its command, then per readout the proposals (with the alternative's own blind
    forecast) and every forecaster's number beside the forecasters of other families it does not overlap."""
    md = [f"\n### {c['id']}: {c['cell']['model']}; {c['cell']['prompt']}; {c['cell']['set']}, n {c['cell']['n']}"
          f"{' (base only)' if c['base_only'] else ''}\n\nGPU minutes {c['gpu_minutes']:g} (proposers' guess). Separation "
          f"{c['separation']} pairs, {c['per_minute']:g} per minute. Job `{c['job']}`.\n\nCell: {json.dumps(c['cell'])}\n\n"
          f"Command: `{c['command']}`\n"]
    for r in c["readouts"]:
        md.append(f"\n#### {r['id']}: {r['readout']} ({r['unit']})\n")
        if b := r["best_base"]:
            md.append(f"Best known base count given to the forecasters: {b['value']:g} ({b['item']}{'; ' + b['note'] if b.get('note') else ''}). "
                      f"Highest forecast: {r['top']['forecaster']} {r['top']['value']:g} ({r['top']['gain']:+g}).\n")
        md += [f"- proposed by {p['mechanism']} ({p['id']}): {p['value']:g} [{p['low']:g}, {p['high']:g}]; says {p['against']} gives "
               f"{p['against_value']:g} (its blind forecast: {g(F[p['against']][r['id']]['value'])}). {p['why']}" for p in (by_id[i] for i in r["from"])]
        md.append("\n| forecaster | family | value | 90 % interval | does not overlap with |\n|---|---|---|---|---|")
        said = [n for n in F if F[n][r["id"]]["value"] is not None]
        for n in said:
            f, other = F[n][r["id"]], [m for m in said if fam_of[m] != fam_of[n] and apart(F[n][r["id"]], F[m][r["id"]])]
            md.append(f"| {n} | {fam_of[n]} | {f['value']:g} | [{f['low']:g}, {f['high']:g}] | {', '.join(other)} |")
        md.append(f"\nTheory says nothing: {', '.join(n for n in F if n not in said) or 'none'}.\n")
    return md


def cells_md(title, head, props, merged, F, fam_of):
    """cells.md: head, C1-C3, every merged cell in one table, then list A (top 10 by separation per GPU minute) and
    list B (base-only cells, top 10 by the highest forecast minus the best known base count)."""
    by_id = {p["id"]: p for p in props}
    by_sep = sorted(merged, key=lambda c: -c["per_minute"])
    base = sorted((c for c in merged if c["base_only"]), key=lambda c: -max(r["top"]["gain"] for r in c["readouts"]))
    c2 = sum(c["separation"] >= 3 for c in merged)
    c3 = [r["id"] for c in merged for r in c["readouts"] if r.get("top") and r["top"]["gain"] > 0]
    md = [f"# {title}\n\n{head}\n",
          f"- C1: {len(props)} cells proposed, {len(merged)} after merging (needs 20 and 10): {'holds' if len(props) >= 20 and len(merged) >= 10 else 'refuted'}.",
          f"- C2: {c2} merged cells have 3 or more such pairs (needs 5): {'holds' if c2 >= 5 else 'refuted'}.",
          f"- C3: {len(c3)} base-only readouts have a forecast above the best known base count ({', '.join(c3) or 'none'}): {'holds' if c3 else 'refuted'}.\n",
          "## Every merged cell\n\n| cell | model | prompt | set | n | base only | GPU minutes | separation | per minute |\n|---|---|---|---|---|---|---|---|---|"]
    md += [f"| {c['id']} | {c['cell']['model']} | {c['cell']['prompt']} | {c['cell']['set']} | {c['cell']['n']} | {'yes' if c['base_only'] else ''} | "
           f"{c['gpu_minutes']:g} | {c['separation']} | {c['per_minute']:g} |" for c in by_sep]
    md.append("\n## List A: top 10 by separation per GPU minute")
    md += [line for c in by_sep[:10] for line in cell_md(c, by_id, F, fam_of)]
    md.append("\n## List B: base-only cells, top 10 by the highest forecast of right answers minus the best known base count")
    md += [line for c in base[:10] for line in cell_md(c, by_id, F, fam_of)]
    return "\n".join(md) + "\n"
