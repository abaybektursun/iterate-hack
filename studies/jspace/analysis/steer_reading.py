"""Blind excerpts for one reader of the hold-on words that an arm of jobs/steer_gen.py inserted (specs/SPEC3_steer.md).

    PYTHONPATH=. python3 studies/jspace/analysis/steer_reading.py <none run> <steer run> <bias run> <out dir>

Writes reading_excerpts.md (what the reader sees) and reading_key.json (kind, problem, offset, text; the reader must not see it).
Kinds: 'steer' / 'bias' = the arm's answer first departs from the none answer with a hold-on word (a Wait the arm inserted);
'natural' = a random hold-on word of the none answer. Each excerpt: 500 characters before the word, 700 from it."""
import json
import random
import re
import sys

sys.path.insert(0, ".")
from studies.jspace.analysis.steer_analyze import first_divergence  # noqa: E402

H = re.compile(r"\b(?:[Ww]ait|[Hh]mm+)\b")
none_run, steer_run, bias_run, out = sys.argv[1:5]
load = lambda run, arm: {r["problem_index"]: r for r in map(json.loads, open(f"{run}/answers.jsonl")) if r["arm"] == arm}
arm_of = lambda run: sorted({json.loads(l)["arm"] for l in open(f"{run}/answers.jsonl")} - {"none"})[0]
none = load(none_run, "none")
rng = random.Random(20261115)
items = []
for kind, run in (("steer", steer_run), ("bias", bias_run)):
    rows = load(run, arm_of(run))
    cand = []
    for i, r in rows.items():
        d = first_divergence(r["text"], none[i]["text"])
        if d is not None and d[1] and d[0] > 150:
            cand.append((i, d[0], r))
    print(kind, arm_of(run), "inserted hold-on words at first divergence:", len(cand))
    for i, pos, r in rng.sample(cand, 20):
        items.append({"kind": kind, "problem_index": i, "pos": pos, "before": r["text"][max(0, pos - 500):pos], "after": r["text"][pos:pos + 700],
                      "score_v3": r["score_v3"], "none_score_v3": none[i]["score_v3"]})
cand = [(i, m.start(), r) for i, r in none.items() for m in H.finditer(r["text"]) if m.start() > 600]
for i, pos, r in rng.sample(cand, 20):
    items.append({"kind": "natural", "problem_index": i, "pos": pos, "before": r["text"][max(0, pos - 500):pos], "after": r["text"][pos:pos + 700],
                  "score_v3": r["score_v3"], "none_score_v3": r["score_v3"]})
rng.shuffle(items)
for k, it in enumerate(items):
    it["id"] = k + 1
json.dump(items, open(f"{out}/reading_key.json", "w"), indent=1)
with open(f"{out}/reading_excerpts.md", "w") as f:
    for it in items:
        f.write(f"\n\n===== EXCERPT {it['id']} =====\n[text before]\n{it['before']}\n>>>HERE>>> {it['after']}\n")
print(len(items), "excerpts")
