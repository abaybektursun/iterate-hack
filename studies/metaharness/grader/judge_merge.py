"""Put the judge's scores next to each review, after checking every quote against the review's own text.

  MH_HOME=<dir> python3 -m studies.metaharness.grader.judge_merge

Reads $MH_HOME/judge/out_*.json (one object per pack r<nn>, rubric_v2.md items 1 and 2) and map.json
(grader/judge_pack.py). A `named` score of 1 whose quote is not found in the pack, whitespace ignored, is set to 0 and
listed. Writes results/<experiment>/<run>/review<k>/rubric.json.
"""
import json
import re

from studies.metaharness.lib import arena as A

home = A.HOME / "judge"
mapping = json.loads((home / "map.json").read_text())
scores = {}
for path in sorted(home.glob("out_*.json")):
    scores.update(json.loads(path.read_text()))
assert set(scores) == set(mapping), f"packs without a score: {sorted(set(mapping) - set(scores))}"


def squeeze(text):
    return re.sub(r"\s+", " ", text).replace("\\", "").strip().lower()


dropped = []
for name, where in sorted(mapping.items()):
    pack = squeeze((home / f"{name}.md").read_text())
    score = scores[name]
    for plant, named in score["named"].items():
        if named["score"] and squeeze(named["quote"])[:120] not in pack:
            dropped.append((name, where["run"], where["round"], plant, named["quote"][:100]))
            named["score"], named["note"] = 0, "quote not found in the review's text; set to 0 by judge_merge.py"
    out = A.STUDY / "results" / where["experiment"] / where["run"] / f"review{where['round']}" / "rubric.json"
    out.write_text(json.dumps({"pack": name, "judge": "one agent per 11 packs, arm label not in the pack (rubric_v2.md)", **score}, indent=1) + "\n")
print(len(mapping), "reviews scored;", len(dropped), "named scores dropped for a quote that is not in the text")
for row in dropped:
    print("  dropped", row)
