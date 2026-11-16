"""Stored problem rows, split into an explore half and a test half by problem id (engine 17, data/split_v1.json).

Accounts and adversaries read only explore rows; direct tests read only test rows. So a writer can measure its
consequence before fixing a range, and the test still decides on problems the writer never saw.

  python3 studies/theory/lib/rows.py split               write data/split_v1.json once (fails if it exists)
  python3 studies/theory/lib/rows.py manifest            print every stored cell with its set, path and source
  python3 studies/theory/lib/rows.py copy <dir> explore  write that half of every available cell to <dir>

In Python: `from rows import load, manifest`; `load("hard328", "rlneurons/day1_3/hard328_base_cue_s4r2-01", "test")`
returns that cell's rows of the test half, each with "pid" (the problem id the split uses).

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
        if m["source"] == "s3 (not cached)":
            lines.append(f"| (not here: S3, not cached) | {m['cell']} | {m['set']} | - | {m['path']} |")
            continue
        rows = load(m["set"], m["cell"], half)
        f = dest / m["set"] / (m["cell"].replace("/", "__") + ".jsonl")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        lines.append(f"| {f.relative_to(dest)} | {m['cell']} | {m['set']} | {len(rows)} | {m['path'] if m['source'] == 'committed' else 'runs/' + m['job_id'] + '/answers.jsonl'} |")
    (dest / "MANIFEST.md").write_text("\n".join(lines) + "\n")
    return dest


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "split":
        make_split()
    elif cmd == "manifest":
        for m in manifest():
            print(f"{m['set']:9s} {m['source']:16s} {m['cell']}  ({m['path']})")
    elif cmd == "copy":
        print(copy(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(__doc__)
