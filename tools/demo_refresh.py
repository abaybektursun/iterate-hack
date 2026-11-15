# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""Recount the /demo/story numbers that change by the hour and write them into tools/demo_facts.py, just before the talk.

  uv run tools/demo_refresh.py

It recounts, with the same sources that tools/demo_facts.py names in each key's "src":
  board (DynamoDB, the index that board.py ls uses): results_on_board, results_per_hour_by_utc_hour, board_hours,
    results_per_hour, board_items_by_kind, per_person.results;
  uv run tools/cycle.py --hours 24: claim_to_close_median_min, claim_to_close_upper_quartile_min,
    work_items_closed, stage_median_min;
  the agent event log (team.Store("events")): gpu_submit_commands, gpu_submit_by_person_shell, agent_sessions,
    tool_commands_logged, logged_commands_from_shell, board_posts_by_agents, per_person.agent_sessions;
  the GPU job records (S3 traces/<who>/jobs.json, pushed by each person's uv run tools/traces.py push):
    per_person.gpu_jobs.
It rewrites only "v", "n" and "at" of those keys, in place, and prints a before and after table. It stops with an
error on any failure and then writes nothing. Restart uv run tools/view.py afterwards: the server reads the file once.
"""
import ast
import collections
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

from boto3.dynamodb.conditions import Key

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import team  # noqa: E402

FILE = TOOLS / "demo_facts.py"
NOW = datetime.datetime.now(datetime.timezone.utc)
AT = NOW.strftime("%Y-%m-%d %H:%M UTC")


def person(name):
    """8038263+frustea -> frustea, as board.py and the event log store it."""
    return name.split("+")[-1]


def listed(kind):
    items, query = [], dict(IndexName="new", KeyConditionExpression=Key("listed").eq(kind))
    while True:
        page = team.table().query(**query)
        items += page["Items"]
        if "LastEvaluatedKey" not in page:
            return items
        query["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def read_facts(text):
    """Every line of the form   'key': {...},   as key -> (line, dict)."""
    out = {}
    for line in text.splitlines():
        m = re.match(r"^  '(\w+)': (\{.*\}),$", line)
        if m:
            out[m.group(1)] = (line, ast.literal_eval(m.group(2)))
    return out


def line_of(key, d):
    return (f"  {key!r}: {{\"v\": {d['v']!r}, \"n\": {d['n']!r}, \"src\": {d['src']!r}, \"at\": {d['at']!r}, "
            f"\"note\": {d['note']!r}}},")


text = FILE.read_text()
facts = read_facts(text)
new = {}  # key -> {"v", "n", "at"} changes

# 1. Board: results, per UTC hour, per person, hours since the first board item, items by kind.
results = listed("result")
assert results, "no results on the board"
first = datetime.datetime.strptime(facts["first_board_item_utc"][1]["v"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
times = sorted(datetime.datetime.fromtimestamp(int(i["at_ns"]) / 1e9, datetime.timezone.utc) for i in results)
hours = round((times[-1] - first).total_seconds() / 3600, 1)
by_hour = collections.Counter()
for t in times:
    by_hour[t.strftime("%Y-%m-%d %H")] += 1
per_hour = [[h[-2:], c] for h, c in sorted(by_hour.items())]  # "2026-11-14 20" sorts in time order
new["results_on_board"] = {"v": len(results), "at": AT}
new["results_per_hour_by_utc_hour"] = {"v": per_hour, "n": len(results), "at": AT}
new["board_hours"] = {"v": hours, "at": AT}
new["results_per_hour"] = {"v": round(len(results) / hours, 1), "n": len(results), "at": AT}
kinds = {k: len(listed(k)) for k in ("result", "knowledge", "idea", "skill")}
kinds["work_open"] = len(listed("work"))
new["board_items_by_kind"] = {"v": kinds, "at": AT}
results_by_person = collections.Counter(person(i["who"]) for i in results)

# 2. cycle.py: the median from claim to result and the stage medians.
cycle = subprocess.run(["uv", "run", str(TOOLS / "cycle.py"), "--hours", "24"], capture_output=True, text=True, check=True).stdout
team_line = re.search(r"claim to close median (\d+) min, upper quartile (\d+) min, over (\d+) work items closed", cycle)
stage_line = re.search(r"to-job (\d+), jobs (\d+), to-answer (\d+)", cycle)
assert team_line and stage_line, "cycle.py printed no Team line or no stage line:\n" + cycle[-800:]
median, upper, closed = map(int, team_line.groups())
new["claim_to_close_median_min"] = {"v": median, "n": closed, "at": AT}
new["claim_to_close_upper_quartile_min"] = {"v": upper, "n": closed, "at": AT}
new["work_items_closed"] = {"v": closed, "at": AT}
new["stage_median_min"] = {"v": dict(zip(("to_job", "jobs", "to_answer"), map(int, stage_line.groups()))), "at": AT}

# 3. The agent event log.
events = [v for _, v in team.Store("events").items()]
assert events, "the event log is empty"
argv = lambda e: e.get("argv") or [""]
submits = [e for e in events if e["tool"] == "gpu" and argv(e)[0] == "submit"]
sessions = collections.defaultdict(set)
for e in events:
    if e.get("session"):
        sessions[person(e["who"])].add(e["session"])
human = lambda e: e["agent"] == "human"
board_cmd = lambda e, verb, kind="": e["tool"] == "board" and argv(e)[0] == verb and (not kind or (len(argv(e)) > 1 and argv(e)[1] == kind))
new["gpu_submit_commands"] = {"v": len(submits), "at": AT}
new["gpu_submit_by_person_shell"] = {"v": sum(map(human, submits)), "n": len(submits), "at": AT}
new["agent_sessions"] = {"v": len(set().union(*sessions.values())), "at": AT}
new["tool_commands_logged"] = {"v": len(events), "at": AT}
new["logged_commands_from_shell"] = {"v": sum(map(human, events)), "n": len(events), "at": AT}
new["board_posts_by_agents"] = {"v": {"idea": sum(board_cmd(e, "post", "idea") and not human(e) for e in events),
                                      "result_post": sum(board_cmd(e, "post", "result") and not human(e) for e in events),
                                      "done": sum(board_cmd(e, "done") and not human(e) for e in events),
                                      "comment": sum(board_cmd(e, "comment") and not human(e) for e in events)},
                                "n": len(events), "at": AT}

# 4. GPU job records per person (each person's last traces.py push).
jobs, pushed = collections.Counter(), {}
pages = team.s3().get_paginator("list_objects_v2").paginate(Bucket=team.BUCKET, Prefix=team.PREFIX + "traces/", Delimiter="/")
owners = [c["Prefix"] for page in pages for c in page.get("CommonPrefixes", [])]
for prefix in owners:
    listing = team.s3().list_objects_v2(Bucket=team.BUCKET, Prefix=prefix + "jobs.json")
    for o in listing.get("Contents", []):
        if not o["Key"].endswith("/jobs.json"):
            continue
        who = person(o["Key"].split("/")[-2])
        records = json.loads(team.s3().get_object(Bucket=team.BUCKET, Key=o["Key"])["Body"].read())
        jobs[who] += sum(k.startswith("job:") for k in records)
        pushed[who] = o["LastModified"].strftime("%H:%M UTC")
assert jobs, "no jobs.json under traces/"
old_pp = facts["per_person"][1]["v"]
pp = {p: {"results": results_by_person.get(p, 0), "agent_sessions": len(sessions.get(p, ())), "gpu_jobs": jobs.get(p, 0)}
      for p in sorted(set(old_pp) | set(results_by_person) | set(sessions) | set(jobs))}
new["per_person"] = {"v": pp, "at": AT}

# Write: replace each line, then check that nothing else changed.
before = {k: facts[k][1] for k in new}
missing = [k for k in new if k not in facts]
assert not missing, f"keys not in demo_facts.py: {missing}"
out = text
for key, change in new.items():
    line, d = facts[key]
    out = out.replace(line, line_of(key, {**d, **change}), 1)
after = read_facts(out)
changed = {k for k in facts if after[k][1] != facts[k][1]}
assert changed <= set(new), f"unexpected change in {changed - set(new)}"
assert set(after) == set(facts), "a key went missing"
compile(out, str(FILE), "exec")
FILE.write_text(out)

w = max(map(len, new)) + 2
print(f"{'key':<{w}}{'before':<44}after   (at {AT})")
for key in new:
    b, a = before[key], after[key][1]
    show = lambda d: (json.dumps(d["v"], separators=(",", ":")) + (f" n {d['n']}" if d.get("n") is not None else ""))
    mark = "" if show(b) != show(a) else "  (same)"
    print(f"{key:<{w}}{show(b)[:42]:<44}{show(a)[:110]}{mark}")
print("job records pushed at: " + ", ".join(f"{p} {t}" for p, t in sorted(pushed.items()))
      + ". A person whose file is old runs uv run tools/traces.py push, then run this again.")
