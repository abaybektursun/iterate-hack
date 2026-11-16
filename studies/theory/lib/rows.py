"""Stored problem rows, split into an explore half and a test half by problem id (engine 17, data/split_v1.json).

Accounts and adversaries read only explore rows; direct tests read only test rows. So a writer can measure its
consequence before fixing a range, and the test still decides on problems the writer never saw.

  python3 studies/theory/lib/rows.py split               write data/split_v1.json once (fails if it exists)
  python3 studies/theory/lib/rows.py manifest            print every stored cell with its set, path and source
  python3 studies/theory/lib/rows.py copy <dir> explore  write that half of every available cell to <dir>
  python3 studies/theory/lib/rows.py split-matrices      write data/split_matrices_v1.json once (engine 18)
  python3 studies/theory/lib/rows.py weights             print every per-matrix weights table (engine 18)
  python3 studies/theory/lib/rows.py split-cells         write data/split_cells_v1.json once (engine 20)

Engine 18: the committed per-matrix tables of the weights studies (WEIGHTS) are split by MATRIX: 
data/split_matrices_v1.json assigns each of the 224 weight matrices (q, k, v, o, gate, up, down of 32 layers) to explore
or test by the sha256 of its name. `weights("anatomy", "test")` returns that table's rows of the test matrices, each
with "matrix" (the parameter name). `copy` also writes the explore matrices of every table to <dir>/weights/.

In Python: `from rows import load, manifest`; `load("hard328", "rlneurons/day1_3/hard328_base_cue_s4r2-01", "test")`
returns that cell's rows of the test half, each with "pid" (the problem id the split uses).

Engine 20: data/split_cells_v1.json assigns each stored run_cell folder of studies/rlneurons/results (the xreward edit
cells and every sampling or vote cell, `run_cells()`) to explore or test by the sha256 of its folder name (folders that
share a job are one group). `copy` leaves out the rows of test cells; their counts are forecast blind and scored at once.

Cells: committed rows.jsonl and per_problem.json (a list with problem_index) under studies/*/results whose set is
named in run.json or whose problem ids equal a whole set; autobench finals (index); and the code cells of every
readout.json with job ids, whose answers.jsonl sit in S3 and load only when cached in runs/<job>/ of this checkout or
of the main checkout.
"""
import functools
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPLIT = ROOT / "studies/theory/data/split_v1.json"
RULE = ("For each set, sort its problem ids by the sha256 hex digest of '<set>:<id>' (id as a decimal string, or the "
        "code uid such as 'HumanEval/0'); the first floor(n / 2) ids are explore, the rest test. dev100 uses MATH-500's "
        "assignment (its ids are MATH-500 indices, key 'math500:<id>'). No seed. Never changed after its first commit.")
SETS = ("hard328", "math500", "fresh2026", "code")
MATRIX_SPLIT = ROOT / "studies/theory/data/split_matrices_v1.json"
MATRIX_RULE = ("Sort the 224 weight-matrix names (model.layers.<l>.self_attn.{q,k,v,o}_proj.weight and "
               "model.layers.<l>.mlp.{gate,up,down}_proj.weight, l = 0..31) by the sha256 hex digest of the name; the first 112 "
               "are explore, the rest test. No seed. Never changed after its first commit.")
MODULES = ("q", "k", "v", "o", "gate", "up", "down")
CELL_SPLIT = ROOT / "studies/theory/data/split_cells_v1.json"
RLN = ROOT / "studies/rlneurons/results"
CELL_RULE = ("Every run_cell folder under studies/rlneurons/results (metrics.json with config and counts.correct_v3, the whole "
             "set, not a dry run): the edit cells of the xreward family and every other sampling or vote cell. Folders that "
             "share a job id (job_id or joined_from) form one group, named by its alphabetically first folder; groups are "
             "sorted by the sha256 hex digest of that name and the first floor(G / 2) are explore, the rest test. No seed. "
             "Never changed after its first commit.")
EDIT_ARGS = ("recipe", "other", "donor", "mods", "layers", "onto", "scale", "alpha", "k")
# Engine 18: committed per-matrix tables of the weights studies, {name: (path, what one row holds)}. Model keys:
# math31 / rl_math = Olmo-3.1-7B-RL-Zero-Math, code31 / rl_code = Olmo-3.1-7B-RL-Zero-Code, math30 / code30 / if30 /
# general30 / mix30 = the Olmo-3 RL-Zero runs, *_s100 = their step-100 checkpoints, think_sft = Olmo-3-7B-Think-SFT,
# base_w = the base matrix itself; every delta is model minus base (Olmo-3-1025-7B).
WEIGHTS = {
    "anatomy": ("studies/rlneurons/results/wsp1/anatomy-01/metrics.json",
                "delta.<rl_math, rl_code or think_sft>: norm_delta, norm_base, rel (norm_delta / norm_base), top1_share, top8_share "
                "(share of the delta's squared norm in its top 1 / 8 singular directions), stable_rank, svals_top16, unchanged "
                "(fraction of entries unchanged); pair.<a-b>: dot, cos (cosine of the two deltas), overlap_left, overlap_right "
                "(overlap of the two deltas' top-8 left / right singular subspaces)"),
    "top8_share": ("studies/theory/data/direct_reward/top8_share_v1.json",
                   "top8_share.<key>: share of the delta's squared norm in its top-8 singular directions, for 15 models and base_w"),
    "cap": ("studies/theory/data/direct_host/cap_v1.json",
            "cap.<a>b>: cap_left = ||U_b^T d_a||^2 / ||d_a||^2, cap_right = ||d_a V_b||^2 / ||d_a||^2, cap_both = "
            "||U_b^T d_a V_b||^2 / ||d_a||^2; d_a = model a minus base, U_b, V_b the top-8 left / right singular vectors of "
            "b's delta (base_w: of the base matrix)"),
    "xlisten": ("studies/rlneurons/results/xlisten/run-01/metrics.json",
                "writers o and down only (62 of the 224, layers 0-30): <rl, basew or rand>.next = mean gain ||W c||^2 / "
                "(||W||_F^2 / 4096) of the next layer's q, k, v, gate, up on the writer's 8 written directions (rl: RL-Math "
                "3.1 delta's top-8 left singular vectors; basew: the base matrix's own top 8; rand: random), "
                "next_by_reader, later (mean over all later layers), next_per_direction"),
}


def key(s, pid):
    return hashlib.sha256(f"{s}:{pid}".encode()).hexdigest()


def runs_dirs():
    """runs/ of this checkout and of the main checkout (git's common dir), where gpu.py get copies job outputs."""
    common = Path(subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=ROOT,
                                 capture_output=True, text=True, check=True).stdout.strip())
    return list(dict.fromkeys([ROOT / "runs", common.parent / "runs"]))


def make_split():
    assert not SPLIT.exists(), f"{SPLIT} exists and never changes"
    rl = ROOT / "studies/rlneurons/results"
    universe = {
        "hard328": sorted({json.loads(x)["problem_index"] for x in open(rl / "day1_3/hard328_base_cue_s4r2-01/rows.jsonl")}),
        "math500": list(range(500)),
        "fresh2026": list(range(len(json.loads((ROOT / "studies/rlneurons/data/fresh/fresh2026_v1.json").read_text())))),
        "code": sorted({json.loads(x)["uid"] for x in open(cached("abaybektursun-1114-170253-f661"))}),
    }
    sources = {"hard328": "problem_index of studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl",
               "math500": "MATH-500 indices 0-499", "fresh2026": "indices of studies/rlneurons/data/fresh/fresh2026_v1.json",
               "code": "uid of the RL-Code plain answers (job abaybektursun-1114-170253-f661): HumanEval+ and MBPP+ minus 4 excluded"}
    out = {"version": 1, "rule": RULE, "sets": {}}
    for s, ids in universe.items():
        order = sorted(ids, key=lambda p: key(s, p))
        h = len(order) // 2
        out["sets"][s] = {"source": sources[s], "n": len(ids), "explore": sorted(order[:h], key=str if s == "code" else int),
                          "test": sorted(order[h:], key=str if s == "code" else int)}
    dev = json.loads((ROOT / "studies/autobench/data/dev100-v1.json").read_text())["indices"]
    ex = set(out["sets"]["math500"]["explore"])
    out["sets"]["dev100"] = {"source": "studies/autobench/data/dev100-v1.json (MATH-500 indices; MATH-500's assignment)", "n": len(dev),
                             "explore": sorted(i for i in dev if i in ex), "test": sorted(i for i in dev if i not in ex)}
    SPLIT.write_text(json.dumps(out, indent=1) + "\n")
    print({s: (len(v["explore"]), len(v["test"])) for s, v in out["sets"].items()})


def matrix_names():
    t = json.loads((ROOT / WEIGHTS["anatomy"][0]).read_text())["tensors"]
    return [x["name"] for x in t if x["module"] in MODULES]


def make_matrix_split():
    assert not MATRIX_SPLIT.exists(), f"{MATRIX_SPLIT} exists and never changes"
    names = matrix_names()
    assert len(names) == 224 == len(set(names)), len(names)
    order = sorted(names, key=lambda n: hashlib.sha256(n.encode()).hexdigest())
    MATRIX_SPLIT.write_text(json.dumps({"version": 1, "rule": MATRIX_RULE, "n": 224, "explore": sorted(order[:112]),
                                        "test": sorted(order[112:])}, indent=1) + "\n")
    print(f"{MATRIX_SPLIT}: 112 explore, 112 test")


def weight_rows(table):
    """Every row of one WEIGHTS table, one per weight matrix, each with "matrix" (its parameter name)."""
    d = json.loads((ROOT / WEIGHTS[table][0]).read_text())
    if table == "anatomy":
        return [{"matrix": x["name"], **x} for x in d["tensors"] if x["module"] in MODULES]
    if table == "xlisten":
        return [{"matrix": f"model.layers.{r['layer']}." + ("self_attn.o_proj" if r["writer"] == "o" else "mlp.down_proj") + ".weight", **r}
                for r in d["rows"]]
    return [{"matrix": r["name"], **r} for r in d["rows"]]


def weights(table, half):
    """The rows of WEIGHTS table `table` whose matrix is in `half` of data/split_matrices_v1.json."""
    assert half in ("explore", "test"), half
    keep = set(json.loads(MATRIX_SPLIT.read_text())[half])
    rows = weight_rows(table)
    assert {r["matrix"] for r in rows} <= set(matrix_names()), table
    return [r for r in rows if r["matrix"] in keep]


@functools.cache
def run_cells():
    """Engine 20: every stored run_cell folder (CELL_RULE) as {folder (relative to studies/rlneurons/results), family
    (edit: the xreward folders; sampling: the rest), set, n, samples, count (right answers per sample, grader v3), jobs,
    description (config and edit arguments, never a count)}."""
    out = []
    for f in sorted(RLN.glob("**/metrics.json")):
        d = json.loads(f.read_text())
        if not (isinstance(d, dict) and isinstance(d.get("config"), dict) and isinstance(d.get("counts"), dict) and "correct_v3" in d["counts"]):
            continue
        c, k, s = d["config"], d["counts"], d["config"].get("samples") or 1
        if c.get("n") is not None or c.get("dry_run") or k["n"] % s:
            continue
        folder = str(f.parent.relative_to(RLN))
        edit = f.parent / "edit.json"
        args = json.loads(edit.read_text())["args"] if edit.exists() else {}
        desc = {"folder": folder, "model": c.get("model_label") or c.get("model"), "model_repo": c.get("model_repo"),
                "tokenizer": (c.get("tokenizer") or [None])[0], "prompt": c.get("prompt"), "set": c.get("set"), "n": k["n"] // s,
                "samples": s, "temperature": c.get("temperature"), "top_p": c.get("top_p"), "min_p": c.get("min_p"),
                "max_tokens": c.get("max_tokens"), "seed": c.get("seed"), "shots": c.get("shots"),
                "edit": {a: args[a] for a in EDIT_ARGS if args.get(a) not in (None, False)} or None}
        jobs = str(d.get("job_id")).split("+") + [j["job_id"] for j in d.get("joined_from") or [] if isinstance(j, dict) and j.get("job_id")]
        out.append({"folder": folder, "family": "edit" if folder.startswith("xreward/") else "sampling", "set": c.get("set"),
                    "n": k["n"] // s, "samples": s, "count": round(k["correct_v3"] / s, 2), "jobs": jobs,
                    "label": c.get("model_label"), "description": {x: v for x, v in desc.items() if v is not None}})
    return tuple(out)


def make_cell_split():
    assert not CELL_SPLIT.exists(), f"{CELL_SPLIT} exists and never changes"
    cells = run_cells()
    group = {c["folder"]: c["folder"] for c in cells}  # union by shared job id
    find = lambda x: x if group[x] == x else find(group[x])  # noqa: E731
    owner = {}
    for c in cells:
        for j in c["jobs"]:
            if j in owner:
                a, b = sorted((find(owner[j]), find(c["folder"])))
                group[b] = a
            owner.setdefault(j, c["folder"])
    names = sorted({find(c["folder"]) for c in cells}, key=lambda n: hashlib.sha256(n.encode()).hexdigest())
    explore = set(names[:len(names) // 2])
    out = {"version": 1, "rule": CELL_RULE, "groups": len(names),
           "cells": {c["folder"]: {"half": "explore" if find(c["folder"]) in explore else "test", "group": find(c["folder"])} for c in cells}}
    CELL_SPLIT.write_text(json.dumps(out, indent=1) + "\n")
    print(f"{CELL_SPLIT}: {len(cells)} cells in {len(names)} groups; {sum(v['half'] == 'test' for v in out['cells'].values())} test cells")


@functools.cache
def cell_half():
    """{folder: explore | test} of data/split_cells_v1.json ({} before the split exists)."""
    return {f: v["half"] for f, v in json.loads(CELL_SPLIT.read_text())["cells"].items()} if CELL_SPLIT.exists() else {}


def withheld(m):
    """Engine 20: a manifest cell whose rows are a test cell of the cell split; its rows go to no writer."""
    p = (ROOT / m["path"]).parent
    return p.is_relative_to(RLN) and cell_half().get(str(p.relative_to(RLN))) == "test"


@functools.cache
def split():
    return json.loads(SPLIT.read_text())["sets"]


def half_ids(s, half):
    assert half in ("explore", "test"), half
    return set(split()[s][half])


def cached(job):
    for d in runs_dirs():
        if (d / job / "answers.jsonl").exists():
            return d / job / "answers.jsonl"
    return None


def read(path, fmt):
    if fmt == "jsonl":
        return [json.loads(x) for x in open(path) if x.strip()]
    return json.loads(Path(path).read_text())


@functools.cache
def manifest():
    """Every stored cell: {cell, set, path, format, id, source: committed | cached | s3 (not cached)}."""
    sets = split()
    full = {s: set(sets[s]["explore"]) | set(sets[s]["test"]) for s in SETS}
    out = []
    for f in sorted(ROOT.glob("studies/*/results/**/*")):
        if f.name not in ("rows.jsonl", "per_problem.json"):
            continue
        fmt = "jsonl" if f.suffix == ".jsonl" else "json"
        rows = read(f, fmt)
        if not (isinstance(rows, list) and rows and isinstance(rows[0], dict) and "problem_index" in rows[0]):
            continue
        ids = {r["problem_index"] for r in rows}
        run = f.parent / "run.json"
        named = json.loads(run.read_text()) if run.exists() else {}
        named = (named.get("config", named) if isinstance(named, dict) else {}).get("set")
        s = named if named in full and ids <= full[named] else next((x for x in ("hard328", "math500", "fresh2026") if ids == full[x]), None)
        if s:
            out.append({"cell": str(f.parent.relative_to(ROOT / "studies")).replace("/results/", "/"), "set": s,
                        "path": str(f.relative_to(ROOT)), "format": fmt, "id": "problem_index", "rows": len(rows),
                        "problems": len(ids), "source": "committed"})
    for f in sorted(ROOT.glob("studies/autobench/results/*/finals-*/*.json")):
        s = "hard328" if f.name.startswith("hard328") else "math500"
        rows = read(f, "json")
        out.append({"cell": str(f.relative_to(ROOT / "studies")).replace("/results/", "/").removesuffix(".json"), "set": s,
                    "path": str(f.relative_to(ROOT)), "format": "json", "id": "index", "rows": len(rows),
                    "problems": len({r["index"] for r in rows}), "source": "committed"})
    seen = set()
    for f in sorted(ROOT.glob("studies/rlneurons/results/**/readout.json")):
        d = json.loads(f.read_text())
        cells = d.get("cells") if isinstance(d, dict) else None
        if not isinstance(cells, dict):
            continue
        for name, c in cells.items():
            if not (isinstance(c, dict) and c.get("job_id") and "humanevalplus" in c) or c["job_id"] in seen:
                continue
            seen.add(c["job_id"])
            p = cached(c["job_id"])
            out.append({"cell": f"{f.parent.relative_to(ROOT / 'studies')}".replace("/results/", "/") + f"/{name}", "set": "code",
                        "path": str(p) if p else f"runs/{c['job_id']}/answers.jsonl", "format": "jsonl", "id": "uid",
                        "job_id": c["job_id"], "source": "cached" if p else "s3 (not cached)"})
    return tuple(out)


def load(s, cell, half):
    """The rows of `cell` (a manifest cell name) whose problem is in `half` of set `s`, each with "pid"."""
    m = next((c for c in manifest() if c["cell"] == cell), None)
    assert m, f"no stored cell {cell}; see `rows.py manifest`"
    assert m["set"] == s or (s == "dev100" and m["set"] == "math500"), f"{cell} is a {m['set']} cell, not {s}"
    assert m["source"] != "s3 (not cached)", f"{cell}: rows sit in S3 (job {m['job_id']}); copy them to runs/{m['job_id']}/ first"
    keep = half_ids(s, half)
    rows = read(ROOT / m["path"], m["format"])
    return [{**r, "pid": r[m["id"]]} for r in rows if r[m["id"]] in keep]


def copy(dest, half):
    """Write `half` of every available cell to dest/<set>/<cell with / as __>.jsonl, and dest/MANIFEST.md listing them."""
    dest = Path(dest)
    lines = [f"# Stored rows, {half} half only\n", f"Split rule (studies/theory/data/split_v1.json): {RULE}\n",
             f"Problems per set in this half: " + ", ".join(f"{s} {len(split()[s][half])}" for s in (*SETS, "dev100")) + ".\n",
             "Each file holds one cell's rows of this half, one JSON object per line, with `pid` added (the problem id). "
             "Cells with the same set share problem ids. `cell` is the name a test loads with rows.py.\n",
             "| file | cell | set | rows | source path |", "|---|---|---|---|---|"]
    for m in manifest():
        if withheld(m):  # engine 20: a test cell of the cell split is neither copied nor named
            continue
        if m["source"] == "s3 (not cached)":
            lines.append(f"| (not here: S3, not cached) | {m['cell']} | {m['set']} | - | {m['path']} |")
            continue
        rows = load(m["set"], m["cell"], half)
        f = dest / m["set"] / (m["cell"].replace("/", "__") + ".jsonl")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        lines.append(f"| {f.relative_to(dest)} | {m['cell']} | {m['set']} | {len(rows)} | {m['path'] if m['source'] == 'committed' else 'runs/' + m['job_id'] + '/answers.jsonl'} |")
    lines += ["\n## Weights tables (engine 18): explore matrices only\n", f"Matrix split (studies/theory/data/split_matrices_v1.json): {MATRIX_RULE}\n",
              "Each file weights/<table>.jsonl holds one row per explore weight matrix, with `matrix` its parameter name "
              "(module and layer in the row). A `weights` consequence is computed from these rows alone and tested on the test matrices.\n",
              "| file | table | rows | source path | one row holds |", "|---|---|---|---|---|"]
    for t, (path, what) in WEIGHTS.items():
        rows = weights(t, half)
        f = dest / "weights" / f"{t}.jsonl"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        lines.append(f"| weights/{t}.jsonl | {t} | {len(rows)} | {path} | {what} |")
    (dest / "MANIFEST.md").write_text("\n".join(lines) + "\n")
    return dest


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "split":
        make_split()
    elif cmd == "manifest":
        for m in manifest():
            print(f"{m['set']:9s} {m['source']:16s} {m['cell']}  ({m['path']})")
    elif cmd == "split-cells":
        make_cell_split()
    elif cmd == "split-matrices":
        make_matrix_split()
    elif cmd == "weights":
        for t, (path, what) in WEIGHTS.items():
            print(f"{t:10s} explore {len(weights(t, 'explore')):3d} test {len(weights(t, 'test')):3d}  {path}: {what}")
    elif cmd == "copy":
        print(copy(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(__doc__)
