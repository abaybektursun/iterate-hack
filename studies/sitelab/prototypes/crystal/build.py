"""Make data.json for the crystal prototype from repo files: which board results have a finding page, and the pitch line.

  python3 studies/sitelab/prototypes/crystal/build.py

findings: result id -> the finding pages (tools/finding_<slug>.py) whose source names that result id.
pitch: the first sentence of the pitch line of DIRECTION.md. Everything else on the page comes live from /data.
"""
import glob, json, os, re

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

json.dump({"findings": findings, "pitch": pitch}, open(os.path.join(HERE, "data.json"), "w"), indent=1)
print(len(findings), "results with a finding page;", len(pitch), "characters of pitch")
