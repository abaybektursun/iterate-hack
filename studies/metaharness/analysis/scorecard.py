"""SPEC1 Part A: where the minutes went for every work item of 2026-11-14 (UTC) that had a GPU job, whole team,
recomputed from raw records only. No number is read from meta/*.md. From the repository root:

    uv run --with boto3 --with modal python -m studies.metaharness.analysis.scorecard

Reads (never writes): the board table (work items of the day, their comments, the ideas they cite), the events store
(every gpu.py submit, every board.py done), this person's Modal job records (gpu.load), every traces/<who>/jobs.json
in the team bucket, and the committed studies/*/results/**/metrics.json that carry a job_id.
Stages of a work item, minutes: wait_for_claim (the first idea its text cites was posted -> claim), to_job (claim ->
first submit), queue (submit -> start, median over its jobs), run (start -> end, median), setup_load and generation
(metrics.json: wall_s minus counts.generation_s, and counts.generation_s), to_answer (last job end -> close, only when
every job's end is known), total (claim -> close). A value that cannot be computed is null, its reason under "missing".
Job times: submit from the job record, else from the submit event (a few seconds earlier). Start and end from the job
record (container start; end or cancel), else from metrics.json: started_utc is the script's start, after
setup_vllm.sh, so that queue contains the setup; updated_utc is the end when status is done.
A submit event has no job id. An id found in any record is paired with the latest submit event of the same person at
most 60 s before the id's clock time (whole hours ignored: ids are in local time) and not after the id's first mention.
Matching a job to a work item of the same person: "id" = the earliest text written on an item after the submit (its
text, a comment, the result text of its done event) that names the id or its last four characters; "run_json" = such
a text names a studies/... run folder whose run.json holds the id; "branch" = submitted while the item was open, from
the item's branch or a branch named in its text (the most recently claimed such item).
Windows are cut at the entry_utc of each row of data/interventions_v1.json: an item counts in the window of its claim,
a job in the window of its submit. Writes results/scorecard/all-<nn>/ (run.json, metrics.json, examples.json), next free nn.
"""
import calendar
import collections
import hashlib
import json
import pathlib
import re
import statistics
import subprocess
import sys
import time

from boto3.dynamodb.conditions import Key

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import board  # noqa: E402
import gpu  # noqa: E402
import team  # noqa: E402

STUDY = ROOT / "studies" / "metaharness"
T0 = calendar.timegm((2026, 11, 14, 0, 0, 0))
T1, NOW = T0 + 86400, time.time()
JOB_ID = re.compile(r"[\w+]+-\d{4}-\d{6}-[0-9a-f]{4}")
STAGES = ("wait_for_claim", "to_job", "queue", "run", "setup_load", "generation", "to_answer", "total")


def utc(text):
    return calendar.timegm(time.strptime(text, "%Y-%m-%dT%H:%M:%SZ"))


def iso(at):
    return None if at is None else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(at))


def minutes(start, end):
    return None if start is None or end is None else round((end - start) / 60, 2)


def median(values):
    known = [v for v in values if v is not None]
    return round(statistics.median(known), 2) if known else None


def person(who):  # the rule of team.who(): 82460915+sameraslan -> sameraslan
    return who.split("+")[-1]


# ---- raw records
day = Key("at_ns").between(T0 * 10**9, T1 * 10**9 - 1)
items = [i for listed in ("work", "work-closed") for i in board.rows(IndexName="new", KeyConditionExpression=Key("listed").eq(listed) & day)]
events = sorted((int(key.split(":")[1]) / 1e9, key, e) for key, e in team.Store("events").items())  # the key holds the time in ns
events = [e for e in events if T0 <= e[0] < T1]
for i in items:  # written: (time, record id, text) of the item's text, its comments and the result text of its done event
    i.update(who=person(i["who"]), claim=int(i["at_ns"]) / 1e9, close=utc(i["closed_at"]) if "closed_at" in i else None)
    comments = board.rows(KeyConditionExpression=Key("pk").eq(i["pk"]) & Key("sk").begins_with("comment#"))
    i["written"] = [(i["claim"], f"{i['pk']}/item", i["text"])] + [(int(c["sk"].split("#")[1]) / 1e9, f"{c['pk']}/{c['sk']}", c["text"]) for c in comments]
    i["written"] += [(at, key, e["argv"][2]) for at, key, e in events if e["tool"] == "board" and e["argv"][:2] == ["done", i["id"]] and len(e["argv"]) > 2]
interventions = json.loads((STUDY / "data" / "interventions_v1.json").read_text())["interventions"]
records = {job_id: {**r, "source": "modal"} for job_id, r in gpu.load().items()}  # this person's workspace, current
pushed = {}  # person -> time of their traces/<who>/jobs.json
for page in team.s3().get_paginator("list_objects_v2").paginate(Bucket=team.BUCKET, Prefix="traces/"):
    for o in page.get("Contents", []):
        if o["Key"].endswith("/jobs.json"):
            pushed[person(o["Key"].split("/")[1])] = iso(o["LastModified"].timestamp())
            for key, value in json.loads(team.s3().get_object(Bucket=team.BUCKET, Key=o["Key"])["Body"].read()).items():
                kind, job_id = key.split(":", 1)
                if records.get(job_id, {}).get("source") != "modal":
                    records.setdefault(job_id, {"id": job_id, "source": "s3"})[kind] = value
committed = {}  # job id -> (path, metrics)
listed = subprocess.run(["git", "ls-files", "studies/*/results/**/metrics.json"], cwd=ROOT, capture_output=True, text=True, check=True)
for path in listed.stdout.split():
    metrics = json.loads((ROOT / path).read_text())
    if "job_id" in metrics:
        committed[metrics["job_id"]] = (path, metrics)

# ---- jobs: one per submit event, plus job records that have no event
jobs = [{"id": None, "who": person(e["who"]), "class": e["argv"][1], "branch": e.get("branch"), "event": key, "submit": at, "submit_source": "event",
         "cmd": " ".join(e["argv"][e["argv"].index("--") + 1:])[:120]} for at, key, e in events if e["tool"] == "gpu" and e["argv"][:1] == ["submit"]]
mentions = [(at, json.dumps(e["argv"])) for at, _, e in events] + [(at, text) for i in items for at, _, text in i["written"]]
mentions += [(r["job"]["at"], job_id) for job_id, r in records.items()] + [(T1, job_id) for job_id in committed]
first_seen = {}  # job id -> time of its first mention in any record
for at, text in mentions:
    for job_id in JOB_ID.findall(text):
        first_seen[job_id] = min(at, first_seen.get(job_id, at))
for job_id, seen in sorted(first_seen.items()):
    who, _, clock, _ = job_id.rsplit("-", 3)
    second = int(clock[:2]) * 3600 + int(clock[2:4]) * 60 + int(clock[4:])
    near = [j for j in jobs if j["who"] == person(who) and (second - j["submit"]) % 3600 < 60 and j["submit"] <= seen]
    if near:
        assert near[-1]["id"] is None, f"{job_id} and {near[-1]['id']} both pair with submit event {near[-1]['event']}"
        near[-1]["id"] = job_id
for job_id, r in records.items():
    if job_id not in {j["id"] for j in jobs} and T0 <= r["job"]["at"] < T1:
        jobs.append({"id": job_id, "who": person(r["job"]["who"]), "class": r["job"]["class"], "branch": r["job"].get("branch"), "event": None,
                     "submit": r["job"]["at"], "submit_source": r["source"], "cmd": r["job"]["cmd"][:120]})


def owner(job):
    """The work item a job belongs to: (item id, how it was matched, the record that says so)."""
    mine = [i for i in items if i["who"] == job["who"]]
    if job["id"]:
        tail = job["id"][-4:]
        named = re.compile(rf"(?<![0-9a-f]){tail}(?![0-9a-f])" if re.search("[a-f]", tail) else rf"(?:-|\.\.\.){tail}(?![0-9a-f])")
        hits = sorted((at, i["id"], ref) for i in mine for at, ref, text in i["written"] if at >= job["submit"] - 60 and named.search(text))
        if hits:
            return hits[0][1], "id", hits[0][2]
        for i in mine:
            for _, ref, text in i["written"]:
                for path in re.findall(r"studies/[\w./-]+", text):
                    run = ROOT / path.rstrip("./")
                    run = run if run.name == "run.json" else run / "run.json"
                    if run.is_file() and job["id"] in run.read_text():
                        return i["id"], "run_json", f"{ref} -> {run.relative_to(ROOT)}"
    if job["branch"]:
        in_text = re.compile(rf"(?<![\w/-]){re.escape(job['branch'])}(?![\w/-])")
        open_then = [i for i in mine if i["claim"] <= job["submit"] <= (i["close"] or NOW) and (i.get("branch") == job["branch"] or in_text.search(i["text"]))]
        if open_then:
            return max(open_then, key=lambda i: i["claim"])["id"], "branch", None
    return None, None, None


for job in jobs:
    r, (path, metrics), who = records.get(job["id"]), committed.get(job["id"], (None, None)), job["who"]
    job.update(start=None, end=None, state=None, metrics=path, setup_load=None, generation=None, model_load=None, missing={})
    if r:
        ended = r.get("end") or r.get("cancel")
        job.update(submit=r["job"]["at"], submit_source=r["source"], start=r["start"]["at"] if "start" in r else None, end=ended["at"] if ended else None)
        job["state"] = gpu.state(r) if ended or r["source"] == "modal" else None  # another workspace's call cannot be asked for its state
    if metrics:
        if job["start"] is None:
            job.update(start=utc(metrics["started_utc"]), start_source="metrics.json started_utc (script start)")
        if job["end"] is None and metrics["status"] == "done":
            job.update(end=utc(metrics["updated_utc"]), end_source="metrics.json updated_utc", state="done")
        job.update(setup_load=round((metrics["wall_s"] - metrics["counts"]["generation_s"]) / 60, 2),
                   generation=round(metrics["counts"]["generation_s"] / 60, 2), model_load=round(metrics["engine"]["load_s"] / 60, 2))
    for name in ("start", "end"):
        if job[name] is not None:
            job.setdefault(f"{name}_source", r["source"] if r else None)
        else:
            job["missing"][name] = (f"the job record has no {name}; state {job['state']}" if r and r["source"] == "modal" else
                                    f"only in {who}'s Modal Dict; traces/{who}/jobs.json pushed {pushed.get(who, 'never')}")
        job[f"{name}_utc"] = iso(job[name])
    if not job["id"]:
        job["missing"]["id"] = "no record names the job id of this submit event (or the submit stopped before it created a job)"
    job["queue"], job["run"], job["submit_utc"] = minutes(job["submit"], job["start"]), minutes(job["start"], job["end"]), iso(job["submit"])
    job["failed"] = job["state"] is not None and job["state"] not in ("done", "running", "queued", "submitting")
    job["item"], job["match"], job["matched_by"] = owner(job)


def row(item):
    mine = sorted((j for j in jobs if j["item"] == item["id"]), key=lambda j: j["submit"])
    ideas = re.findall(r"idea-[0-9a-f]{6}", item["text"])
    ends = [j["end"] for j in mine]
    out = {"id": item["id"], "who": item["who"], "claimed": iso(item["claim"]), "closed": iso(item["close"]), "idea": ideas[0] if ideas else None,
           "n_jobs": len(mine), "n_jobs_with_start": sum(j["start"] is not None for j in mine), "n_jobs_with_end": len(ends) - ends.count(None),
           "match": "+".join(sorted({j["match"] for j in mine})),
           "wait_for_claim": minutes(int(board.get(ideas[0])["at_ns"]) / 1e9, item["claim"]) if ideas else None,
           "to_job": minutes(item["claim"], mine[0]["submit"]),
           "queue": median(j["queue"] for j in mine), "queue_max": max((j["queue"] for j in mine if j["queue"] is not None), default=None),
           "run": median(j["run"] for j in mine), "setup_load": median(j["setup_load"] for j in mine), "generation": median(j["generation"] for j in mine),
           "to_answer": minutes(max(ends), item["close"]) if None not in ends else None, "total": minutes(item["claim"], item["close"])}
    why = {"wait_for_claim": "the text cites no idea", "queue": "no job has a start time", "run": "no job has a start and an end time",
           "setup_load": "no job has a committed metrics.json", "generation": "no job has a committed metrics.json", "total": "the item is open",
           "to_answer": f"end unknown for {ends.count(None)} of {len(ends)} jobs" if None in ends else "the item is open"}
    return {**out, "missing": {stage: why[stage] for stage in STAGES if out[stage] is None}, "text": item["text"][:200], "jobs": mine}


table = sorted((row(i) for i in items if any(j["item"] == i["id"] for j in jobs)), key=lambda r: r["claimed"])

# ---- windows between interventions, and each intervention's targeted stage before and after
marks = [T0] + [utc(v["entry_utc"]) for v in interventions] + [T1]
names = ["day start"] + [v["id"] for v in interventions] + ["day end"]
windows = []
for k in range(len(marks) - 1):
    inside = [j for j in jobs if marks[k] <= j["submit"] < marks[k + 1]]
    ended = [j for j in inside if j["run"] is not None]
    claimed = [r for r in table if marks[k] <= utc(r["claimed"]) < marks[k + 1]]
    windows.append({"window": f"{names[k]} to {names[k + 1]}", "from": iso(marks[k]), "to": iso(marks[k + 1]), "submits": len(inside),
                    "jobs_with_start_and_end": len(ended), "container_minutes": round(sum(j["run"] for j in ended), 2),
                    "failed_or_cancelled_jobs": sum(j["failed"] for j in inside), "failed_or_cancelled_minutes": round(sum(j["run"] for j in ended if j["failed"]), 2),
                    "jobs_with_unknown_state": sum(j["state"] is None for j in inside), "items_claimed": [r["id"] for r in claimed],
                    "stage_median": {stage: median(r[stage] for r in claimed) for stage in STAGES}})
scorecard = []
for k, v in enumerate(interventions):
    pair = {stage: {"before": windows[k]["stage_median"][stage], "after": windows[k + 1]["stage_median"][stage]} for stage in STAGES}
    targets = [stage for stage in STAGES if stage in v["target_stage"]]
    scorecard.append({"id": v["id"], "who": v["who"], "entry_utc": v["entry_utc"], "made": v["made"], "commit": v["commit"], "target_stage": v["target_stage"],
                      "items_before": windows[k]["items_claimed"], "items_after": windows[k + 1]["items_claimed"],
                      "targeted": {s: pair[s] for s in targets}, "untargeted": {s: pair[s] for s in STAGES if s not in targets}})

coverage = {"work_items": len(items), "work_items_with_jobs": len(table), "earliest_work_item": iso(min(i["claim"] for i in items)),
            "work_items_note": "from the board index (listed = work, work-closed); items closed before board.py kept closed items in the index are absent",
            "events": len(events), "jobs": len(jobs), "jobs_with_id": sum(j["id"] is not None for j in jobs),
            "jobs_by_match": dict(collections.Counter(j["match"] or "no work item" for j in jobs)),
            **{f"{name}_time": dict(collections.Counter(j.get(f"{name}_source") or "missing" for j in jobs)) for name in ("submit", "start", "end")},
            "jobs_with_unknown_state": sum(j["state"] is None for j in jobs), "jobs_json_pushed": pushed, "committed_metrics_with_job_id": len(committed)}
picks = {"resolved": [r for r in table if not r["missing"]], "unresolved": [r for r in table if r["missing"]]}  # the first of each is saved with its board row
examples = {name: {"row": found[0], "board_row": next(i for i in items if i["id"] == found[0]["id"])} for name, found in picks.items() if found}

out = next(folder for n in range(1, 100) if not (folder := STUDY / "results" / "scorecard" / f"all-{n:02d}").exists())
out.mkdir(parents=True)
commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
run = {"commit": commit, "command": "uv run --with boto3 --with modal python -m studies.metaharness.analysis.scorecard", "read_utc": iso(NOW),
       "script_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(), "interventions": "studies/metaharness/data/interventions_v1.json"}
result = {"units": "minutes", "coverage": coverage, "items": table, "windows": windows, "interventions": scorecard, "jobs_without_work_item": [j for j in jobs if not j["item"]]}
for name, value in (("run", run), ("metrics", result), ("examples", examples)):
    (out / f"{name}.json").write_text(json.dumps(value, indent=1, default=str) + "\n")

print("id  who  " + "  ".join(STAGES) + "  n_jobs(start/end known)  match")
for r in table:
    print(f"{r['id']}  {r['who']}  " + "  ".join(str(r[stage]) for stage in STAGES) + f"  {r['n_jobs']}({r['n_jobs_with_start']}/{r['n_jobs_with_end']})  {r['match']}")
for w in windows:
    print(f"{w['window']}: {w['submits']} submits, {w['jobs_with_start_and_end']} with start and end, {w['container_minutes']} container min, "
          f"{w['failed_or_cancelled_minutes']} failed or cancelled min, items {w['items_claimed']}")
for s in scorecard:
    print(f"{s['id']} made={s['made']} targeted {s['targeted'] or 'none'}, items before {s['items_before']}, after {s['items_after']}")
print(json.dumps(coverage, indent=1), f"\nwrote {out.relative_to(ROOT)}")
