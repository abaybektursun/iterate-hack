# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""data.json for the reading room: every paper the team fetched with tools/paper.py, and every finding recorded from it.

  uv run studies/sitelab/prototypes/library/build.py

Sources
  tools/events.py store (S3)   every `paper.py fetch` and `paper.py add` command: who, when, the paper, the finding
  https://monitor.invariant.team/data   board items; an arXiv id cited there that nobody fetched becomes a pamphlet
  export.arxiv.org             title, first author and date of each arXiv id (kept from the last data.json when present)
  studies/metaharness/results/exa_count-01/summary.json   the stored count of tools/exa.py calls

A finding is one distinct (paper, where, finding) of a `paper.py add` command. The command is logged before its quote
check runs, so a command whose quote was not found in the paper is counted once if it was never retried.
Fails on any mismatch between a sum and its stored total. No transcript text, no email address, no path of a person.
"""
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import team  # noqa: E402

ARXIV = re.compile(r"\b(\d{4}\.\d{4,5})(?:v\d+)?\b")
ATOM = "{http://www.w3.org/2005/Atom}"
OUT = HERE / "data.json"


def unix(at):
    return int(datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp())


def flags(argv):
    """paper.py's argparse, by hand: the values of --flags and the positional words."""
    named, plain, i = {}, [], 0
    while i < len(argv):
        if argv[i].startswith("--"):
            named[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            plain.append(argv[i])
            i += 1
    return named, plain


people = []


def pid(who):
    name = who.split("+")[-1]
    if name not in people:
        people.append(name)
    return people.index(name)


# ---- the paper commands ---------------------------------------------------------------------------------------------
commands = [v for _, v in sorted(team.Store("events").items()) if v["tool"] == "paper"]
papers, n_fetch, n_add = {}, 0, 0


def paper(key, t, who):
    p = papers.setdefault(key, {"id": key, "ax": None, "url": None, "title": None, "au": None, "date": None,
                                "t": t, "by": who, "fetched": False, "f": {}})
    if t < p["t"]:
        p["t"], p["by"] = t, who
    return p


for v in commands:
    named, plain = flags(v["argv"][1:])
    t, who = unix(v["at"]), pid(v["who"])
    if v["argv"][0] == "fetch":
        n_fetch += 1
        source = plain[0]
        if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", source):          # the same rule as tools/paper.py
            p = paper(f"arxiv-{source}", t, who)
            p["ax"], p["url"] = ARXIV.match(source).group(1), f"https://arxiv.org/abs/{source}"
        else:
            p = paper("web-" + sha256(source.encode()).hexdigest()[:10], t, who)
            p["url"], p["title"], p["date"] = source, named.get("title"), named.get("date")
            if "arxiv.org" in source and ARXIV.search(source):
                p["ax"] = ARXIV.search(source).group(1)
        p["fetched"] = True
    elif v["argv"][0] == "add":
        n_add += 1
        p = paper(plain[0], t, who)
        if p["ax"] is None and plain[0].startswith("arxiv-"):
            p["ax"], p["url"] = ARXIV.search(plain[0]).group(1), "https://arxiv.org/abs/" + plain[0][6:]
        p["f"].setdefault((named["where"], plain[1]), [named["where"], plain[1], named["quote"][:240], who, t])
    else:
        raise SystemExit(f"unknown paper.py command: {v['argv'][:1]}")
assert n_fetch + n_add == len(commands), "a paper.py command is neither fetch nor add"

# ---- pamphlets: arXiv ids cited on the board that nobody fetched ---------------------------------------------------
with urllib.request.urlopen("https://monitor.invariant.team/data", timeout=30) as r:
    items = json.load(r)["items"]
known = {p["ax"] for p in papers.values() if p["ax"]}
for it in sorted(items, key=lambda i: i["at_ns"]):
    for ax in dict.fromkeys(ARXIV.findall(it["text"])):
        if ax not in known:
            known.add(ax)
            p = paper(f"arxiv-{ax}", it["at_ns"] // 10**9, pid(it["who"]))
            p["ax"], p["url"] = ax, f"https://arxiv.org/abs/{ax}"

# ---- titles from arXiv ------------------------------------------------------------------------------------------------
cache = {}
if OUT.exists():
    cache = {p["ax"]: p for p in json.loads(OUT.read_text())["papers"] if p["ax"] and p["title"]}
need = sorted({p["ax"] for p in papers.values() if p["ax"] and not p["title"] and p["ax"] not in cache})
meta = {}
for i in range(0, len(need), 40):
    chunk = need[i:i + 40]
    url = f"https://export.arxiv.org/api/query?id_list={','.join(chunk)}&max_results={len(chunk)}"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "library-build"}), timeout=60) as r:
        for e in ET.fromstring(r.read()).iter(f"{ATOM}entry"):
            ax = ARXIV.search(e.findtext(f"{ATOM}id").rsplit("/", 1)[-1])
            if not ax or not e.findtext(f"{ATOM}title"):
                continue
            names = [a.findtext(f"{ATOM}name") for a in e.iter(f"{ATOM}author")]
            meta[ax.group(1)] = {"title": " ".join(e.findtext(f"{ATOM}title").split()),
                                 "au": names[0].split()[-1] + (" et al." if len(names) > 1 else ""),
                                 "date": e.findtext(f"{ATOM}published")[:10]}
    time.sleep(3)                                                    # arXiv asks for 3 s between requests
unknown = []
for p in papers.values():
    m = meta.get(p["ax"]) or cache.get(p["ax"])
    if m:
        p["title"] = p["title"] or m["title"]
        p["au"], p["date"] = p["au"] or m["au"], p["date"] or m["date"]
    if not p["title"]:
        assert not p["fetched"] and not p["f"], f"a fetched paper has no title: {p['id']}"
        unknown.append(p["ax"])                                        # an id cited on the board that arXiv does not have
shelf = sorted((p for p in papers.values() if p["title"]), key=lambda p: (p["t"], p["id"]))
for p in shelf:
    p["f"] = sorted(p["f"].values(), key=lambda f: f[4])
    web = re.search(r"\(([^()]+)\)\s*$", p["title"]) if not p["au"] else None
    if web:                                                            # paper.py web titles end with "(authors)"
        p["title"], p["au"] = p["title"][:web.start()].strip(), web.group(1)

# ---- the stored Exa count ---------------------------------------------------------------------------------------------
exa = json.loads((ROOT / "studies/metaharness/results/exa_count-01/summary.json").read_text())["all"]
assert exa["search"] + exa["fetch"] == exa["calls"], "exa summary: search + fetch differs from calls"
assert sum(exa["status"].values()) == exa["calls"], "exa summary: statuses do not sum to calls"

n_findings = sum(len(p["f"]) for p in shelf)
distinct = set()
for v in commands:
    if v["argv"][0] == "add":
        named, plain = flags(v["argv"][1:])
        distinct.add((plain[0], named["where"], plain[1]))
distinct = len(distinct)
assert n_findings == distinct, f"findings on the shelf {n_findings} differ from distinct add commands {distinct}"
fetched = [p for p in shelf if p["fetched"] or p["f"]]
assert len(fetched) + sum(1 for p in shelf if not (p["fetched"] or p["f"])) == len(shelf)

data = {"built": team.now(), "people": people, "papers": shelf, "unknown": sorted(unknown),
        "totals": {"fetch_commands": n_fetch, "add_commands": n_add, "read": len(fetched), "findings": n_findings,
                   "pamphlets": len(shelf) - len(fetched)},
        "exa": {"calls": exa["calls"], "search": exa["search"], "fetch": exa["fetch"],
                "returned": exa["calls"] - exa["status"]["failed"] - exa["status"]["unknown"],
                "counted": "Nov 15, 15:50 UTC"}}
text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|/home/|/Users/|sk-[A-Za-z0-9]{20}", text), "private text in data.json"
assert len(text.encode()) < 1_000_000, f"data.json is {len(text.encode())} bytes"
OUT.write_text(text)
print(f"{len(shelf)} papers ({len(fetched)} read with paper.py, {data['totals']['pamphlets']} cited only), "
      f"{n_findings} findings from {n_add} add commands, {len(unknown)} cited ids unknown to arXiv, {len(text.encode())} bytes")
