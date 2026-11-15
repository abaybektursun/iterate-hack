# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4", "boto3>=1.35"]
# ///
"""Make data.json for the ledger prototype: what the team recorded about the cost of each scored result.

  uv run studies/sitelab/prototypes/ledger/build.py

Read-only. Sources:
  scores, result items, plain titles   the DynamoDB table of tools/team.py (board.py)
  run records                          studies/**/run.json whose folder a result's text names
  GPU time                             gpu.py's job records (Modal Dict, one workspace: launch, container start, end)
A job's GPU minutes are end - container start. They are joined to a result only through a job id that the result's
text or one of its named run.json files states; nothing is estimated. One job can have produced several scores.
"""
import glob
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from boto3.dynamodb.conditions import Key  # noqa: E402

import board  # noqa: E402
import gpu  # noqa: E402

JOB = re.compile(r"[a-z]+-\d{4}-\d{6}-[0-9a-f]{4}")
STATED = re.compile(r"\d[\d,.]*\s?(?:H100|L40S|A100|B200|GPU)[- ]?(?:min(?:utes)?|h(?:ours?)?)\b")

# ---- board ---------------------------------------------------------------------------------------------------------
scores = board.rows(KeyConditionExpression=Key("pk").eq("scores"))
plain = board.rows(KeyConditionExpression=Key("pk").eq("plain"))
titles = {}
for r in plain:
    if "title" in r and r["sk"] == r.get("item", r["sk"]):
        titles[r["sk"]] = r["title"]
ids = sorted({s["result"] for s in scores})
items = {}
for i in ids:
    item = board.get(i)
    assert item, f"score rows name {i}, which is not on the board"
    items[i] = item

score_rows = []
for s in scores:
    right, n = int(s["right"]), int(s["n"])
    assert 0 <= right <= n, f"score {s['sk']}: {right}/{n}"
    score_rows.append({"sk": s["sk"], "result": s["result"], "model": s["model"], "benchmark": s["benchmark"], "right": right, "n": n,
                       "config": s.get("config", ""), "tokens": int(s["tokens"]) if s.get("tokens") is not None else None,
                       "who": s["who"]})

# every score line written in a result's text must be one of its score rows: the stored total the page is checked against
# (the model label is left out: rows were relabelled from rl to other after posting)
have = {(s["result"], board.same(s["benchmark"]), s["right"], s["n"], s["tokens"]) for s in score_rows}
for i, item in items.items():
    for model, benchmark, right, n, _, tokens in board.score_lines(item["text"]):
        assert (i, board.same(benchmark), right, n, tokens) in have, \
            f"{i}: its text says {model} {benchmark} {right}/{n} tokens {tokens}, no score row does"

# ---- GPU job records -----------------------------------------------------------------------------------------------
jobs = {}
for job_id, r in gpu.load().items():
    j = r["job"]
    timed = "start" in r and "end" in r
    jobs[job_id] = {"gpu": r["start"]["gpu"] if "start" in r else j["class"], "cls": j["class"],
                    "min": round((r["end"]["at"] - r["start"]["at"]) / 60, 1) if timed else None,
                    "state": ("done" if r["end"].get("exit_code") == 0 and not r["end"].get("stopped") else "ended early") if "end" in r
                    else "cancelled" if "cancel" in r else "no end recorded"}
    assert jobs[job_id]["min"] is None or jobs[job_id]["min"] >= 0, f"{job_id}: ends before it starts"
on_gpu = {k: j for k, j in jobs.items() if j["cls"] != "cpu"}
timed = {k: j for k, j in on_gpu.items() if j["min"] is not None}
by_gpu = {}
for j in timed.values():
    by_gpu[j["gpu"]] = round(by_gpu.get(j["gpu"], 0) + j["min"], 1)
total_min = round(sum(j["min"] for j in timed.values()), 1)
assert abs(sum(by_gpu.values()) - total_min) < 0.5, "GPU minutes per GPU type do not add up to the total"

# ---- run records named by each result ------------------------------------------------------------------------------
run_files = {}
for path in glob.glob(str(ROOT / "studies/**/run.json"), recursive=True):
    run_files[str(Path(path).parent.relative_to(ROOT))] = Path(path).read_text()


def job_ref(job_id):
    j = jobs.get(job_id)
    return {"id": job_id, **({"gpu": j["gpu"], "min": j["min"], "state": j["state"]} if j else {"gpu": None, "min": None, "state": "no record here"})}


results, linked = {}, 0
for i, item in items.items():
    text = item["text"]
    runs, seen = [], set()
    for folder in sorted(run_files):
        if re.search(re.escape(folder) + r"(?![\w.-])", text):  # the run folder itself, not a parent folder of many runs
            found = sorted(set(JOB.findall(run_files[folder])))
            seen |= set(found)
            runs.append({"path": folder, "jobs": [job_ref(j) for j in found]})
    in_text = [j for j in sorted(set(JOB.findall(text))) if j not in seen]
    named = [j for r in runs for j in r["jobs"]] + [job_ref(j) for j in in_text]
    known = [j["min"] for j in named if j["min"] is not None]
    complete = bool(named) and len(known) == len(named)
    linked += complete
    results[i] = {"who": item["who"], "title": titles.get(i, ""), "at": int(int(item["at_ns"]) / 1e9), "runs": runs,
                  "text_jobs": [job_ref(j) for j in in_text], "n_jobs": len(named), "n_timed": len(known),
                  "gpu_min": round(sum(known), 1) if complete else None,
                  "stated": sorted({m.group(0) for m in STATED.finditer(text)})}

out = {"built": int(time.time()),
       "jobs": {"n": len(on_gpu), "timed": len(timed), "gpu_min": total_min, "by_gpu": by_gpu},
       "coverage": {"results": len(results), "with_jobs": sum(r["n_jobs"] > 0 for r in results.values()), "fully_timed": linked,
                    "scores": len(score_rows), "scores_with_tokens": sum(s["tokens"] is not None for s in score_rows)},
       "results": results, "scores": score_rows}
blob = json.dumps(out, separators=(",", ":"))
for secret in ("/home/", "/Users/", "@gmail", "sk-", "AKIA"):
    assert secret not in blob, f"data.json would hold {secret!r}"
assert len(blob) < 1_000_000, "data.json over 1 MB"
(HERE / "data.json").write_text(blob)
print(f"{len(blob) / 1024:.0f} kB; {out['jobs']}; {out['coverage']}")
