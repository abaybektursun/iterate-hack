"""Build data.json for the orrery prototype: every study folder of studies/ as a planet and the board results that
belong to it as its moons, from the live board (/data of the local sitelab server) and the repo.

    python3 studies/sitelab/prototypes/orrery/build.py        (the server of studies/sitelab/serve.py must run)

Definitions (the page states them; this file stores what the page needs to recompute them):
- results: every result id the board's /data names (items, scores, plain, finding). The ones /data does not carry as
  an item (it lists only the newest 60 of a kind) are read one by one from /data/<id>.
- study of a result: the study folder its text names most often (studies/<name>/ or results/<name>/; text = the board
  text + its plain words). A result that names no study folder, or two equally often, belongs to no study ("loose").
- RL score: the first score line the board has for the RL checkpoint on MATH-500 (plain prompt, T 1.0, one sample).
- best base score of a study at a time: the highest `right` among its score lines with model base, MATH-500, n 500.
- problems scored of a result: the sum of n over its score lines.
The build fails when the board's own counts differ from what it reads.
"""
import collections, datetime, json, pathlib, re, subprocess, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SRC = "http://127.0.0.1:8777/data"
get = lambda u: json.loads(urllib.request.urlopen(u, timeout=30).read())

board = get(SRC)
items = {i["id"]: i for i in board["items"] if i["kind"] == "result"}
plain, scores = board["plain"], board["scores"]
ids = set(items) | {k for k in plain if "#" not in k} | set(board["finding"]) | {s["result"] for s in scores}
for rid in sorted(ids - set(items)):  # the site refuses more than 3 requests a second
    time.sleep(0.4)
    one = get(f"{SRC}/{rid}")
    items[rid] = one["item"]
    plain.setdefault(rid, (one.get("plain") or {}).get(rid) or {})
bad = {k: {f: i.get(f) for f in ("id", "kind")} for k, i in items.items() if i.get("kind") != "result" or i.get("id") != k}
assert not bad, bad

STUDIES = sorted(p.name for p in (ROOT / "studies").iterdir() if (p / "README.md").exists())
readme = {s: (ROOT / "studies" / s / "README.md").read_text() for s in STUDIES}


def study_of(r):
    words = r["text"] + " " + " ".join(str(v) for v in plain.get(r["id"], {}).values())
    top = collections.Counter(m for m in re.findall(r"\b(?:studies|results)/(\w+)", words) if m in STUDIES).most_common(2)
    return top[0][0] if top and (len(top) == 1 or top[0][1] > top[1][1]) else None


by_result = collections.defaultdict(list)
for s in sorted(scores, key=lambda s: s["sk"]):
    assert int(s["sk"].split("#")[0]) == items[s["result"]]["at_ns"], s["sk"]
    by_result[s["result"]].append(s)

rl = [s for s in scores if s["model"] == "rl" and s["benchmark"] == "MATH-500" and s["n"] == 500]
rl0 = min(rl, key=lambda s: (s["sk"], "T 1.0" not in s["config"]))
assert rl0["config"].startswith("plain, T 1.0") and rl0["right"] == 463, rl0

clip = lambda t, n: t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"
ms = lambda ns: ns // 1_000_000


def result(r):
    p, sc = plain.get(r["id"], {}), by_result.get(r["id"], [])
    text = re.sub(r"^title: .*\n?", "", r["text"]).strip()
    return {"id": r["id"], "t": ms(r["at_ns"]), "who": r["who"],
            "title": p.get("title") or clip(r["text"].split("\n")[0], 90),
            "what": clip(p.get("what") or re.sub(r"^what: ", "", text), 260),
            "n": sum(s["n"] for s in sc),
            "sc": [[s["model"], s["benchmark"], s["right"], s["n"], clip(s["config"], 110), s["tokens"]] for s in sc]}


placed = collections.defaultdict(list)
for r in sorted(items.values(), key=lambda r: r["at_ns"]):
    placed[study_of(r)].append(result(r))
assert sum(len(v) for v in placed.values()) == len(ids)
assert sum(len(x["sc"]) for v in placed.values() for x in v) == len(scores)


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], check=True, capture_output=True, text=True).stdout.split()


studies = []
for s in STUDIES:
    commits = git("log", "--format=%at", "--", f"studies/{s}")
    head = readme[s].split("\n")[0].lstrip("# ").strip()
    studies.append({"k": s, "about": clip(head.split(":", 1)[1].strip() if ":" in head else head, 120),
                    "commits": len(commits), "first_commit": int(commits[-1]) * 1000, "results": placed[s]})

t0 = min([s["first_commit"] for s in studies] + [r["t"] for v in placed.values() for r in v])
t1 = max(r["t"] for v in placed.values() for r in v)
data = {"built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "t0": t0, "t1": t1,
        "rl": {"right": rl0["right"], "n": rl0["n"], "result": rl0["result"], "config": rl0["config"]},
        "studies": studies, "loose": placed[None]}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
assert len(blob.encode()) < 300_000, len(blob)
assert not re.search(r"/home/|/Users/|[\w.+-]+@[\w-]+\.[a-z]{2,}|sk-[A-Za-z0-9]{16}|AKIA[A-Z0-9]{12}", blob), "private text"
assert {r["who"] for v in placed.values() for r in v} <= {i["who"] for i in board["items"]}
(HERE / "data.json").write_text(blob)

print(f"data.json {len(blob.encode()) // 1024} kB, {len(ids)} results, {len(scores)} score lines")
for s in studies:
    best = max((x[2] for r in s["results"] for x in r["sc"] if x[0] == "base" and x[1] == "MATH-500" and x[3] == 500), default=None)
    print(f"  {s['k']:13} results {len(s['results']):3}  commits {s['commits']:3}  best base MATH-500 {best}")
print(f"  loose         results {len(placed[None]):3}")
