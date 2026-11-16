# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4", "boto3>=1.35"]
# ///
"""Build data.json for the recorder prototype: five signals of the hackathon sampled every 2 minutes, the score
lines, the new best base MATH-500 scores and the board item titles.

  uv run studies/sitelab/prototypes/recorder/build.py        (about 40 s; read-only)

The events come from the sources of ../time-helix/build.py, which this file runs as it stands (board items, messages
on `all`, score lines: the team table; commits: git log --all; GPU jobs: gpu.py's records, job ids and run.json).

Definitions (the page states them):
- sample i is the time t0 + i * STEP seconds (UTC).
- items, msgs, commits: the number posted in the 10 minutes that end at the sample.
- gpu: the jobs running at the sample, counted only for jobs with a recorded launch and end (`gpu_no_end` jobs have
  no recorded end and are left out).
- work: the work items open at the sample (posted, not yet closed).
- best: each score line with model base, MATH-500, n 500 whose `right` is above every earlier one.
- busy: the sample with the most items + msgs + commits. quiet: the longest time between two consecutive events
  (item, message or commit). gpu_peak: the highest gpu sample.
The build fails when a count differs from a stored total, or when an address, a key or a home path is left.
"""
import bisect
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
helix = HERE.parent / "time-helix" / "build.py"
ns = {"__file__": str(HERE / "helix.py"), "__name__": "helix"}   # it writes its data.json beside __file__, which is here
old = (HERE / "data.json").read_bytes() if (HERE / "data.json").exists() else None
exec(compile(helix.read_text(), str(helix), "exec"), ns)
(HERE / "data.json").write_bytes(old) if old else (HERE / "data.json").unlink()   # its own data.json does not stay here
items, msgs, commits, jobs, scores, people, T0 = (ns[k] for k in ("items", "msgs", "commits", "jobs", "score_rows", "people", "T0"))
built = ns["out"]["built"]

STEP, WIN = 120, 600
N = (built - T0) // STEP + 1
at = [T0 + i * STEP for i in range(N)]

total = int(subprocess.run(["git", "-C", str(HERE), "rev-list", "--all", "--count"], capture_output=True, text=True, check=True).stdout)
assert abs(len(commits) - total) <= 3, (len(commits), total)   # a commit may land while the build runs
assert len(items) == sum(len(l) for l in ns["lists"]), "an item is in two lists"
open_now = sum(i["k"] == "work" and i["c"] is None for i in items)
assert open_now == len(ns["lists"][0]), (open_now, len(ns["lists"][0]))


def trailing(times):
    """For each sample, the number of times in the WIN seconds that end at it."""
    times = sorted(times)
    return [bisect.bisect_right(times, t) - bisect.bisect_right(times, t - WIN) for t in at]


ti, tm, tc = [i["t"] for i in items], [m["t"] for m in msgs], [c["t"] for c in commits]
sig = {"items": trailing(ti), "msgs": trailing(tm), "commits": trailing(tc)}
timed = [j for j in jobs if j["end"] is not None]
sig["gpu"] = [sum(j["t"] <= t < j["end"] for j in timed) for t in at]
work = [i for i in items if i["k"] == "work"]
sig["work"] = [sum(i["t"] <= t and (i["c"] is None or i["c"] > t) for i in work) for t in at]
assert sig["work"][-1] <= open_now + 1 and max(sig["items"]) <= len(items)

events = sorted(ti + tm + tc)
gap, g0 = max((b - a, a) for a, b in zip(events, events[1:]))
load = [a + b + c for a, b, c in zip(sig["items"], sig["msgs"], sig["commits"])]
bi, gi = load.index(max(load)), sig["gpu"].index(max(sig["gpu"]))
facts = {"busy": {"i": bi, "n": load[bi], "items": sig["items"][bi], "msgs": sig["msgs"][bi], "commits": sig["commits"][bi]},
         "quiet": {"s": round(gap), "from": round(g0) - T0}, "gpu_peak": {"i": gi, "n": sig["gpu"][gi]},
         "n": {"items": len(items), "msgs": len(msgs), "commits": len(commits), "jobs": len(jobs), "scores": len(scores)},
         "gpu_no_end": len(jobs) - len(timed)}

models, benches, kinds = [], [], []
idx = lambda l, v: l.index(v) if v in l else (l.append(v), len(l) - 1)[1]
clip = lambda s, n: s if len(s) <= n else s[: n - 1].rstrip() + "…"
scores.sort(key=lambda s: s["t"])
best, top = [], 0
for n, s in enumerate(scores):
    if s["model"] == "base" and s["bench"] == "MATH-500" and s["n"] == 500 and s["right"] > top:
        top = s["right"]
        best.append(n)
assert best, "no base MATH-500 score"
first_line = lambda i: i["title"] or re.sub(r"^title: ", "", i["text"].split("\n")[0])
out = {"built": built, "t0": T0, "step": STEP, "win": WIN, "sig": sig, "facts": facts,
       "models": models, "benches": benches, "kinds": kinds, "people": people,
       "scores": [[round(s["t"]) - T0, idx(models, s["model"]), idx(benches, s["bench"]), s["right"], s["n"], clip(s["config"], 70), s["result"]] for s in scores],
       "best": best,
       "items": [[round(i["t"]) - T0, idx(kinds, i["k"]), i["p"], clip(first_line(i), 84)] for i in items]}
used = {people[i["p"]] for i in items}
assert used <= {r["who"] for l in ns["lists"] for r in l}, used   # board handles only
out["people"] = [p if p in used else "" for p in people]

blob = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
for pattern, _ in ns["PRIVATE"]:
    if m := pattern.search(blob):
        sys.exit(f"private text left in the data: {m[0][:12]}")
assert len(blob.encode()) < 300_000, len(blob.encode())
(HERE / "data.json").write_text(blob)
h = lambda s: f"{s / 3600:.1f} h"
print(f"data.json {len(blob.encode()) // 1000} kB, {N} samples over {h(built - T0)}, {len(scores)} score lines, {len(best)} new bests, {len(items)} items")
print("facts:", json.dumps(facts))
print("max per pen:", {k: max(v) for k, v in sig.items()})
