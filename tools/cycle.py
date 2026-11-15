# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4", "boto3>=1.35"]
# ///
"""Turnaround of the experiment cycle: where the minutes between a question and its answer go. For the team-meta-review
skill (section 3), and for anyone who wants to know what to speed up.

  uv run tools/cycle.py [--hours 24]

Jobs: every GPU job of yours (your Modal workspace) submitted in the window, with
  wait = submit to container start (queue and boot), run = start to end (setup, model load and the work), state.
Work: every work item of yours posted in the window, with
  to-job = claim to first job submit (reading, spec, code, review), jobs = first submit to last job end (compute and
  fix loops), to-answer = last job end to close (analysis and write-up), total = claim to close (to now while open).
  A job counts toward a work item when it was submitted from the same git branch between the claim and the close.
  Jobs submitted before gpu.py recorded the branch are not matched, and work items closed before board.py kept
  closed items in its index are not listed.
Team: the median minutes from claim to close over every person's work items closed in the window, and the
  results posted per hour. This is the number an optimization of the process has to move.
All times are minutes.
"""
import calendar
import re
import statistics
import sys
import time

from boto3.dynamodb.conditions import Key

import gpu
import team


def minutes(start, end):
    return (end - start) / 60


def fmt(value, digits=0):
    return "-" if value is None else f"{value:.{digits}f}"


hours = float(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 24.0
since = time.time() - hours * 3600
now = time.time()
who = team.who()

jobs = sorted((r for r in gpu.load().values() if r["job"]["at"] >= since), key=lambda r: r["job"]["at"])
print(f"Jobs of {who}, last {hours:g} h:  id  state  gpu  wait  run  command")
waits, run_minutes, failed_minutes = [], 0.0, 0.0
for r in jobs:
    r["state"] = gpu.state(r)
    start = r["start"]["at"] if "start" in r else None
    end = r["end"]["at"] if "end" in r else r["cancel"]["at"] if "cancel" in r else None
    r["finished"] = end
    wait = minutes(r["job"]["at"], start) if start else None
    run = minutes(start, end or now) if start and (end is None or end >= start) else None
    if wait is not None:
        waits.append(wait)
    if run is not None:
        run_minutes += run
        if r["state"] not in ("done", "running"):
            failed_minutes += run
    gpu_name = r["start"]["gpu"] if start else r["job"]["class"]
    print(f"  {r['id']}  {r['state']}  {gpu_name[:12]}  {fmt(wait, 1)}  {fmt(run, 1)}  {r['job']['cmd'][:70]}")
failed = [r for r in jobs if r["state"] not in ("done", "running", "queued", "submitting")]
if jobs:
    print(f"  {len(jobs)} jobs, {len(failed)} failed or cancelled; median wait {statistics.median(waits) if waits else 0:.1f}; "
          f"{run_minutes:.1f} container minutes, {failed_minutes:.1f} of them in failed or cancelled jobs")

items = []
for listed in ("work", "work-closed"):  # open and closed work items, newest first, from the index board.py ls uses
    query = dict(IndexName="new", KeyConditionExpression=Key("listed").eq(listed) & Key("at_ns").gte(int(since * 10**9)))
    while True:
        page = team.table().query(**query)
        items += [i for i in page["Items"] if i["who"] == who]
        if "LastEvaluatedKey" not in page:
            break
        query["ExclusiveStartKey"] = page["LastEvaluatedKey"]

print(f"\nWork of {who}, last {hours:g} h:  id  branch  to-job  jobs  to-answer  total  n-jobs  n-failed  text")
stages = {"to-job": [], "jobs": [], "to-answer": []}
for item in sorted(items, key=lambda i: i["at_ns"]):
    claim = int(item["at_ns"]) / 10**9
    close = calendar.timegm(time.strptime(item["closed_at"], "%Y-%m-%dT%H:%M:%SZ")) if "closed_at" in item else None
    # a coordinator claims on one branch and its subagent submits from another: the claim text names it ("Branch wdiff")
    branches = {item.get("branch"), *re.findall(r"[Bb]ranch ([\w/.-]*\w)", item["text"])}
    mine = [r for r in jobs if r["job"].get("branch") in branches and claim <= r["job"]["at"] <= (close or now)]
    to_job = jobs_span = to_answer = None
    if mine:
        to_job = minutes(claim, mine[0]["job"]["at"])
        last_end = max((r["finished"] for r in mine if r["finished"]), default=None)
        if last_end:
            jobs_span = minutes(mine[0]["job"]["at"], last_end)
            to_answer = minutes(last_end, close) if close else None
        for name, value in (("to-job", to_job), ("jobs", jobs_span), ("to-answer", to_answer)):
            if value is not None:
                stages[name].append(value)
    n_failed = sum(r in failed for r in mine)
    print(f"  {item['id']}  {item.get('branch', '?')}  {fmt(to_job)}  {fmt(jobs_span)}  {fmt(to_answer)}  "
          f"{fmt(minutes(claim, close or now))}{'' if close else ' (open)'}  {len(mine)}  {n_failed}  {item['text'][:60]}")

query = dict(IndexName="new", KeyConditionExpression=Key("listed").eq("work-closed"))
team_items = []  # every person's closed work items; chosen by close time, so a short window does not keep only the fast ones
while True:
    page = team.table().query(**query)
    team_items += [(i, calendar.timegm(time.strptime(i["closed_at"], "%Y-%m-%dT%H:%M:%SZ"))) for i in page["Items"]]
    if "LastEvaluatedKey" not in page:
        break
    query["ExclusiveStartKey"] = page["LastEvaluatedKey"]
team_items = [(i, close) for i, close in team_items if close >= since]
closed = sorted(minutes(int(i["at_ns"]) / 10**9, close) for i, close in team_items)
results = team.table().query(IndexName="new", Select="COUNT",
                             KeyConditionExpression=Key("listed").eq("result") & Key("at_ns").gte(int(since * 10**9)))["Count"]
if closed:
    print(f"\nTeam, last {hours:g} h: claim to close median {statistics.median(closed):.0f} min, upper quartile "
          f"{closed[3 * len(closed) // 4]:.0f} min, over {len(closed)} work items closed by {len({i['who'] for i, _ in team_items})} "
          f"people; {results} results, {results / hours:.1f} per hour.")

medians = {name: statistics.median(values) for name, values in stages.items() if values}
if medians:
    slowest = max(medians, key=medians.get)
    print("\nMedian minutes per stage over work items with jobs: " + ", ".join(f"{k} {v:.0f}" for k, v in medians.items())
          + f". Slowest stage: {slowest}.")
