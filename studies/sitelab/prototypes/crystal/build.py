"""Make data.json for the crystal prototype from repo files: which board results have a finding page, and the pitch line.

  python3 studies/sitelab/prototypes/crystal/build.py

findings: result id -> the finding pages (tools/finding_<slug>.py) whose source names that result id.
pitch: the pitch line of DIRECTION.md.
old: the text and votes of each scored result that /data no longer lists among its newest 60 items, read here once
     from the site (one request every half second), so the page itself never asks for them.
snapshot: the /data read of this build, shown (and marked as not live) only while the live /data cannot be read.
Everything else on the page comes live from /data.
"""
import glob, json, os, re, time, urllib.request

SITE = "https://monitor.invariant.team"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../../.."))

findings = {}
for f in sorted(glob.glob(os.path.join(ROOT, "tools", "finding_*.py"))):
    src = open(f).read()
    slug = os.path.basename(f)[len("finding_"):-3].replace("_", "-")
    title = re.search(r'^TITLE = "(.*)"', src, re.M).group(1)
    for rid in sorted(set(re.findall(r"result-[0-9a-f]{6}", src))):
        findings.setdefault(rid, []).append({"slug": slug, "title": title})

direction = open(os.path.join(ROOT, "DIRECTION.md")).read()
pitch = " ".join(direction.split("## Pitch line")[1].split("##")[0].split())

def get(path):
    with urllib.request.urlopen(SITE + path, timeout=30) as r:
        return json.load(r)


data = get("/data")
listed = {i["id"] for i in data["items"]}
old = {}
for rid in sorted({s["result"] for s in data["scores"]} - listed):
    time.sleep(.5)
    it = get("/data/" + rid)["item"]
    old[rid] = {"text": it["text"], "ups": int(it.get("ups", 0)), "downs": int(it.get("downs", 0)), "who": it["who"]}

json.dump({"findings": findings, "pitch": pitch, "old": old, "snapshot": data, "snapshot_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, open(os.path.join(HERE, "data.json"), "w"), separators=(",", ":"))
print(len(findings), "results with a finding page;", len(old), "older results;", len(pitch), "characters of pitch")
