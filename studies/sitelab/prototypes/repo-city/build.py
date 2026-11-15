"""Build data.json for the repo-city prototype from the repository's own git history.

  python3 studies/sitelab/prototypes/repo-city/build.py

Reads `git log HEAD` (every non-merge commit in the ancestry of HEAD, with --numstat and --raw) and writes, next to
this file, data.json:
  people    the three git authors, under their board names
  models    the distinct Co-Authored-By trailer values
  districts top-level areas (each study, tools, infra, meta, .claude, the root files): name, rectangle, README line
  files     one per path that ever existed: path, district, rectangle (area grows with its largest blob size)
  commits   in commit-time order: time, author, trailer model, subject, hash, added, deleted, branch, and for each
            file it touched the file's line count after the commit (running sum of added - deleted, never below 0)
  merges    every merge commit: time, author, subject, source and target branch parsed from the subject, the number
            of non-merge commits it brought in (git rev-list parent1..parent2) and the districts those touched
  hours     lines added and deleted per clock hour, split into code/text files and result data files
Nothing here is estimated; the only choices are the layout (a squarified treemap) and the footprint exponent.
"""
import collections, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=HERE, text=True).strip()
WHO = {"Abay Bektursun": "abaybektursun", "Ali Rad": "frustea", "sameraslan": "sameraslan", "Samer Aslan": "sameraslan"}
PEOPLE = sorted(set(WHO.values()))
DATA_EXT = {".json", ".jsonl", ".csv", ".tsv", ".txt", ".log", ".npy", ".npz", ".pt", ".png", ".jpg", ".svg", ".parquet"}


def git(*a):
    return subprocess.check_output(["git", "-c", "core.quotepath=off", *a], cwd=ROOT, text=True, errors="replace")


def district(path):
    p = path.split("/")
    if len(p) == 1:
        return "root"
    if p[0] == "studies" and len(p) > 2:
        return "studies/" + p[1]
    return p[0]


# ---- commits -------------------------------------------------------------------------------------------------------
raw = git("log", "HEAD", "--no-merges", "--no-renames", "--raw", "--numstat", "--abbrev=40",
          "--format=%x01%H%x02%ct%x02%an%x02%s%x02%(trailers:key=Co-Authored-By,valueonly,separator=%x03)%x02")
commits, blobs = [], {}
for rec in raw.split("\x01")[1:]:
    head, _, body = rec.partition("\x02\n")
    h, ct, an, subj, trail = head.split("\x02")[:5]
    c = {"h": h, "t": int(ct), "who": WHO[an], "s": subj, "co": re.sub(r"\s*<.*", "", trail.split("\x03")[0]).strip(),
         "files": []}
    for line in body.splitlines():
        if line.startswith(":"):
            meta, path = line.split("\t", 1)
            sha = meta.split()[3]
            if set(sha) != {"0"}:
                blobs.setdefault(sha, set()).add(path)
        elif line.strip():
            a, d, path = line.split("\t", 2)
            c["files"].append((path, 0 if a == "-" else int(a), 0 if d == "-" else int(d)))
    commits.append(c)
commits.sort(key=lambda c: c["t"])

sizes = collections.defaultdict(int)       # path -> largest blob size it ever had, in bytes
out = subprocess.run(["git", "cat-file", "--batch-check"], cwd=ROOT, input="\n".join(blobs), text=True,
                     capture_output=True, check=True).stdout
for line in out.splitlines():
    sha, _, size = line.split()
    for path in blobs[sha]:
        sizes[path] = max(sizes[path], int(size))

# ---- merges and branch names ----------------------------------------------------------------------------------------
index = {c["h"]: i for i, c in enumerate(commits)}
merges = []
for line in git("log", "HEAD", "--merges", "--format=%H%x02%ct%x02%an%x02%P%x02%s").splitlines():
    h, ct, an, par, subj = line.split("\x02")
    p = par.split()
    m = re.search(r"Merge (?:remote-tracking )?branch '([^']+)'(?: of \S+)?(?: into (\S+))?", subj) or \
        re.search(r"Merge pull request #\d+ from [^/\s]+/(\S+)()", subj) or \
        re.search(r"Merge (\S+)(?: .*?)? into (\S+)", subj)
    src, dst = (m.group(1), m.group(2) or "main") if m else ("", "")
    brought = [x for x in git("rev-list", "--no-merges", f"{p[0]}..{p[1]}").split() if x in index]
    merges.append({"t": int(ct), "who": WHO[an], "s": subj, "from": src, "into": dst, "brought": brought})
merges.sort(key=lambda m: m["t"])
for m in merges:                             # a commit's branch: the source of the first merge that brought it in
    name = re.sub(r"^origin/", "", m["from"])
    if name and name != "main":
        for x in m["brought"]:
            commits[index[x]].setdefault("b", name)

# ---- files, running line counts, hourly totals --------------------------------------------------------------------
paths = sorted({f[0] for c in commits for f in c["files"]})
fid = {p: i for i, p in enumerate(paths)}
lines = collections.defaultdict(int)
t0 = commits[0]["t"]
hours = collections.defaultdict(lambda: [0, 0, 0, 0])   # hour -> code added, code deleted, data added, data deleted
for c in commits:
    ev, add, dele = [], 0, 0
    for path, a, d in c["files"]:
        lines[path] = max(0, lines[path] + a - d)
        ev += [fid[path], lines[path], a, d]
        add += a
        dele += d
        k = 2 if os.path.splitext(path)[1] in DATA_EXT else 0
        hr = hours[(c["t"] - t0) // 3600]
        hr[k] += a
        hr[k + 1] += d
    c.update(e=ev, add=add, dele=dele)

# ---- layout: nested squarified treemap ------------------------------------------------------------------------------
def weight(path):
    return max(sizes[path], 300) ** 0.6


def squarify(items, x, y, w, h):
    """items: [(weight, key)] sorted descending; returns {key: (x, y, w, h)} filling the rectangle."""
    out, items = {}, list(items)
    scale = w * h / sum(i[0] for i in items)
    while items:
        short = min(w, h)
        row, best = [], None
        for it in items:
            trial = row + [it]
            s = sum(i[0] for i in trial) * scale
            worst = max(max(short * short * i[0] * scale / (s * s), s * s / (short * short * i[0] * scale)) for i in trial)
            if best is not None and worst > best:
                break
            row, best = trial, worst
        items = items[len(row):]
        s = sum(i[0] for i in row) * scale
        thick = s / short
        off = 0
        for wt, key in row:
            ln = wt * scale / thick
            out[key] = (x, y + off, thick, ln) if w >= h else (x + off, y, ln, thick)
            off += ln
        if w >= h:
            x, w = x + thick, w - thick
        else:
            y, h = y + thick, h - thick
    return out


def tree(group):
    node = {"files": [], "dirs": collections.defaultdict(list)}
    for path, rest in group:
        if "/" in rest:
            d, r = rest.split("/", 1)
            node["dirs"][d].append((path, r))
        else:
            node["files"].append(path)
    node["dirs"] = {d: tree(g) for d, g in node["dirs"].items()}
    node["w"] = sum(weight(p) for p in node["files"]) + sum(n["w"] for n in node["dirs"].values())
    return node


rects = {}


def place(node, x, y, w, h, depth):
    pad = min([2.6, 1.5, 0.9, 0.5][min(depth, 3)], 0.12 * min(w, h))
    x, y, w, h = x + pad, y + pad, w - 2 * pad, h - 2 * pad
    items = [(n["w"], ("d", d)) for d, n in node["dirs"].items()] + [(weight(p), ("f", p)) for p in node["files"]]
    for (kind, key), r in squarify(sorted(items, key=lambda i: -i[0]), x, y, w, h).items():
        if kind == "d":
            place(node["dirs"][key], *r, depth + 1)
        else:
            m = min(0.45, 0.14 * min(r[2], r[3]))
            rects[key] = (r[0] + m, r[1] + m, r[2] - 2 * m, r[3] - 2 * m)


groups = collections.defaultdict(list)
for p in paths:
    d = district(p)
    groups[d].append((p, p if d == "root" else p[len(d) + 1:]))
trees = {d: tree(g) for d, g in groups.items()}
W, H, ROAD = 640.0, 420.0, 5.0
dnames = sorted(trees, key=lambda d: -trees[d]["w"])
drect = squarify([(trees[d]["w"], d) for d in dnames], -W / 2, -H / 2, W, H)
districts = []
for d in dnames:
    x, y, w, h = drect[d]
    place(trees[d], x + ROAD, y + ROAD, w - 2 * ROAD, h - 2 * ROAD, 0)
    readme = ""
    rp = os.path.join(ROOT, "README.md" if d == "root" else d + "/README.md")
    if os.path.exists(rp):
        text = [l.strip() for l in open(rp, encoding="utf-8").read().split("\n")]
        title = next((l.lstrip("# ") for l in text if l), "")
        para, on = [], False
        for l in text[1:]:
            if l and not l.startswith("#"):
                para.append(l)
                on = True
            elif on:
                break
        first = re.split(r"(?<=[.?])\s", " ".join(para))[0] if para else ""
        readme = (title + ". " + first if first and len(title) < 40 else title)[:400]
    districts.append({"name": d, "r": [round(v, 2) for v in drect[d]], "readme": readme})
didx = {d: i for i, d in enumerate(dnames)}

for m in merges:
    per = collections.Counter()
    for x in m["brought"]:
        for path, a, d in commits[index[x]]["files"]:
            per[didx[district(path)]] += a + d
    m["d"] = [list(x) for x in per.most_common(3)]
    m["n"] = len(m["brought"])
    del m["brought"]

models = sorted({c["co"] for c in commits if c["co"]})
data = {
    "built": int(git("log", "-1", "--format=%ct", "HEAD")), "head": git("rev-parse", "--short", "HEAD").strip(),
    "people": PEOPLE, "models": models, "districts": districts,
    "files": [{"p": p, "d": didx[district(p)], "r": [round(v, 2) for v in rects[p]], "b": sizes[p]} for p in paths],
    "commits": [{"t": c["t"], "a": PEOPLE.index(c["who"]), "m": models.index(c["co"]) if c["co"] else -1,
                 "s": c["s"][:160], "h": c["h"][:7], "add": c["add"], "del": c["dele"], "b": c.get("b", ""),
                 "e": c["e"]} for c in commits],
    "merges": [{"t": m["t"], "a": PEOPLE.index(m["who"]), "s": m["s"][:140], "from": m["from"], "into": m["into"],
                "n": m["n"], "d": m["d"]} for m in merges if m["n"]],
    "hours": [hours[i] for i in range(max(hours) + 1)],
}
with open(os.path.join(HERE, "data.json"), "w") as f:
    json.dump(data, f, separators=(",", ":"))
print(len(paths), "files", len(commits), "commits", len(data["merges"]), "merges", len(districts), "districts",
      os.path.getsize(os.path.join(HERE, "data.json")) // 1024, "KB")
