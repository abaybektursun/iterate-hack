"""Build data.json for the loom prototype: every commit of main as one weft row, every top-level area of the
repository as one band of warp threads, from `git log` alone.

    python3 studies/sitelab/prototypes/loom/build.py

Definitions (the page states them):
- rows: the commits of `git log main --no-merges`, oldest first by commit time (git's own order breaks ties). A merge
  commit changes no file of its own, so it weaves no row.
- area of a file: `studies/<name>` for a file under studies/, else its top-level folder, else "root files" for a file
  at the repository root. Renames count as a deletion and an addition (`--no-renames`). An area touched by fewer than
  MIN_ROWS commits is folded into "other", so the loom has at most 16 warp bands.
- lines of a row: added + deleted lines over all its files (a binary file counts 0).
- picks of a row (its thickness on the cloth): 1 + floor(log2(lines + 1) / 3), capped at 5.
- author: the git author name mapped to the handle the team board uses; any other name becomes "agent".
- run of an area: consecutive rows that all touch the area (they may touch others too).
The build fails when its counts differ from git's own, or when an address, key or home path is left in the output.
"""
import collections, datetime, json, math, pathlib, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HANDLE = {"Abay Bektursun": "abaybektursun", "sameraslan": "sameraslan", "Samer Aslan": "sameraslan", "Ali Rad": "frustea"}
MIN_ROWS, MAX_AREAS, MAX_PICKS = 4, 16, 5


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], check=True, capture_output=True, text=True).stdout


def area(path):
    parts = path.split("/")
    return "root files" if len(parts) == 1 else "/".join(parts[:2]) if parts[0] == "studies" and len(parts) > 2 else parts[0]


rows = []
for block in git("log", "main", "--no-merges", "--no-renames", "--numstat", "--format=%x01%ct%x02%an%x02%s%x02").split("\x01")[1:]:
    ct, an, subject, stat = block.split("\x02")
    touched, lines = collections.Counter(), 0
    for ln in filter(None, stat.split("\n")):
        add, rem, path = ln.split("\t")
        touched[area(path)] += 1
        lines += (0 if add == "-" else int(add)) + (0 if rem == "-" else int(rem))
    rows.append({"t": int(ct), "who": HANDLE.get(an, "agent"), "s": subject.strip(), "areas": set(touched), "lines": lines})
rows.reverse()
rows.sort(key=lambda r: r["t"])  # stable: git's order breaks ties
assert len(rows) == int(git("rev-list", "--count", "--no-merges", "main")), len(rows)

count = collections.Counter(a for r in rows for a in r["areas"])
first = {}
for r in rows:
    for a in r["areas"]:
        first.setdefault(a, r["t"])
keep = [a for a in count if count[a] >= MIN_ROWS and a != "root files"]
studies = sorted((a for a in keep if a.startswith("studies/")), key=first.get)
folders = sorted((a for a in keep if not a.startswith("studies/")), key=first.get)
areas = studies + folders + ["root files"]
folded = sorted(set(count) - set(areas))
if folded:
    areas.append("other")
assert len(areas) <= MAX_AREAS, areas
ix = {a: i for i, a in enumerate(areas)}
for r in rows:
    r["mask"] = sum({1 << ix.get(a, len(areas) - 1) for a in r["areas"]})
    r["picks"] = min(MAX_PICKS, 1 + int(math.log2(r["lines"] + 1) / 3))
n_area = [sum(r["mask"] >> i & 1 for r in rows) for i in range(len(areas))]
assert all(n_area[ix[a]] == count[a] for a in areas if a != "other")


def longest_run(i):
    best, start, run = (0, 0), 0, 0
    for k, r in enumerate(rows):
        run = run + 1 if r["mask"] >> i & 1 else 0
        if run == 1:
            start = k
        best = max(best, (run, start))
    return best


runs = [longest_run(i) for i in range(len(areas))]
top = max(range(len(areas)), key=lambda i: n_area[i])
run_i = max(range(len(areas)), key=lambda i: runs[i][0])
authors = sorted({r["who"] for r in rows}, key=lambda w: -sum(x["who"] == w for x in rows))
clip = lambda t, n: t if len(t) <= n else t[: n - 1] + "…"

data = {"built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "areas": areas, "n_area": n_area, "folded": folded, "authors": authors,
        "n_author": [sum(r["who"] == w for r in rows) for w in authors],
        "facts": {"rows": len(rows), "hours": round((rows[-1]["t"] - rows[0]["t"]) / 3600), "top": top, "top_rows": n_area[top],
                  "run_area": run_i, "run": runs[run_i][0], "run_start": runs[run_i][1], "merges": int(git("rev-list", "--count", "--merges", "main"))},
        "t": [r["t"] for r in rows], "who": [authors.index(r["who"]) for r in rows], "mask": [r["mask"] for r in rows],
        "lines": [r["lines"] for r in rows], "picks": [r["picks"] for r in rows], "s": [clip(r["s"], 80) for r in rows]}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
assert len(blob.encode()) < 300_000, len(blob)
assert not re.search(r"/home/|/Users/|[\w.+-]+@[\w-]+\.[a-z]{2,}|sk-[A-Za-z0-9]{16}|AKIA[A-Z0-9]{12}|ghp_\w{20}|hf_\w{20}", blob), "private text"
assert set(authors) <= {"abaybektursun", "sameraslan", "frustea", "agent"}, authors
(HERE / "data.json").write_text(blob)

f = data["facts"]
print(f"data.json {len(blob.encode()) // 1024} kB, {f['rows']} rows over {f['hours']} h, {sum(data['picks'])} picks, {f['merges']} merges left out")
print(f"  most rows: {areas[top]} {f['top_rows']}; longest run: {areas[run_i]} {f['run']} rows from row {f['run_start']}")
for i, a in enumerate(areas):
    print(f"  {a:22} rows {n_area[i]:4}  longest run {runs[i][0]:3}")
print("  authors:", dict(zip(authors, data["n_author"])), " folded:", folded)
