"""Build data.json for the gazette prototype: every board result with its plain words and score lines, the work items
the board lists, and the commit times, so that the page can set one front page per 3-hour block (UTC) of the hackathon.

    python3 studies/sitelab/prototypes/gazette/build.py        (the server of studies/sitelab/serve.py must run)

Sources (nothing else is read):
- results: every result id the board's /data names (items, scores, plain, finding). /data lists only the newest 60
  items of a kind, so the older ones are read one by one from /data/<id>. A result that /data names nowhere is missing.
- work: the work items /data lists (all open ones and the newest 60 closed ones). `work_from` is the time from which
  the list of closed items is complete (the oldest closing time among them); the page prints no work count for a block
  that starts before it.
- commits: `git log --all --format=%at` of this worktree (author time, every branch), as seconds.

The page, not this file, picks the lead story and the refuted column; this file stores only what the board says.
Texts are stored whole up to a length and cut at a word with an ellipsis. A home path becomes "~/", an email address
is removed; the build fails if either, or a key, remains, or if a count differs from what was read.
"""
import datetime, json, pathlib, re, subprocess, time, urllib.request

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
bad = {k: i.get("kind") for k, i in items.items() if i.get("kind") != "result" or i.get("id") != k}
assert not bad, bad

PRIVATE = r"/home/|/Users/|[\w.+-]+@[\w-]+\.[a-z]{2,}|sk-[A-Za-z0-9]{16}|AKIA[A-Z0-9]{12}|hf_[A-Za-z0-9]{20}"


def clean(t):
    t = re.sub(r"(/home|/Users)/[\w.-]+/?", "~/", t or "")
    t = re.sub(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", "", t)
    return re.sub(r"[ \t]+", " ", t).strip()


def clip(t, n):
    t = clean(t)
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0].rstrip(",;:([") + "…"


LABEL = re.compile(r"^(title|what|why|caveat|score):", re.I)


def rest(text):
    """The board text without its title/what/why/caveat/score lines: the detail the poster wrote under them."""
    return " ".join(l.strip() for l in text.split("\n") if l.strip() and not LABEL.match(l.strip()))


by_result = {}
for s in sorted(scores, key=lambda s: s["sk"]):
    assert int(s["sk"].split("#")[0]) == items[s["result"]]["at_ns"], s["sk"]
    by_result.setdefault(s["result"], []).append(
        [s["model"], s["benchmark"], s["right"], s["n"], clip(s["config"], 120), s["tokens"]])

results = []
for r in sorted(items.values(), key=lambda r: r["at_ns"]):
    p = plain.get(r["id"], {})
    row = {"id": r["id"], "t": r["at_ns"] // 1_000_000_000, "who": r["who"],
           "title": clip(p.get("title") or "", 140), "what": clip(p.get("what") or "", 420),
           "why": clip(p.get("why") or "", 420), "caveat": clip(p.get("caveat") or "", 320),
           "text": clip(rest(r["text"]), 900), "sc": by_result.get(r["id"], [])}
    results.append({k: v for k, v in row.items() if v != "" and v != []})
assert len(results) == len(ids)
assert sum(len(r.get("sc", [])) for r in results) == len(scores)

sec = lambda iso: int(datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp())
work_items = [i for i in board["items"] if i["kind"] == "work"]
closed = [i for i in work_items if "closed_at" in i]
assert len(closed) == sum(i["listed"] == "work-closed" for i in board["items"])
work = sorted(([i["id"], i["at_ns"] // 1_000_000_000, sec(i["closed_at"]) if "closed_at" in i else 0] for i in work_items), key=lambda w: w[1])
work_from = min(w[2] for w in work if w[2])

commits = sorted(int(x) for x in subprocess.run(["git", "-C", str(ROOT), "log", "--all", "--format=%at"], check=True,
                                                capture_output=True, text=True).stdout.split())

handles = {i["who"] for i in board["items"]}
assert {r["who"] for r in results} <= handles and all(re.fullmatch(r"[\w-]+", h) for h in handles), handles
data = {"built": int(time.time()), "results": results, "work": work, "work_from": work_from, "commits": commits}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
assert len(blob.encode()) < 400_000, len(blob.encode())
hit = re.search(PRIVATE, blob)
assert not hit, f"private text: {blob[max(0, hit.start() - 40): hit.end() + 20]!r}"
(HERE / "data.json").write_text(blob)

utc = lambda s: datetime.datetime.fromtimestamp(s, datetime.timezone.utc).strftime("%d %b %H:%M")
print(f"data.json {len(blob.encode()) // 1024} kB: {len(results)} results ({utc(results[0]['t'])} to {utc(results[-1]['t'])} UTC), "
      f"{len(scores)} score lines, {len(work)} work items (closed list complete from {utc(work_from)}), {len(commits)} commits")
blocks = {}
for r in results:
    blocks.setdefault(r["t"] // 10800, []).append(r)
for b in range(min(blocks), max(blocks) + 1):
    rs = blocks.get(b, [])
    print(f"  {utc(b * 10800)}  results {len(rs):3}  score lines {sum(len(r.get('sc', [])) for r in rs):3}  "
          f"with what {sum('what' in r for r in rs):3}  commits {sum(b * 10800 <= c < (b + 1) * 10800 for c in commits):3}")
