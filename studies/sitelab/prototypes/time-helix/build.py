# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4", "boto3>=1.35"]
# ///
"""Make data.json for the time-helix prototype: every recorded event of the hackathon with its real time.

  uv run studies/sitelab/prototypes/time-helix/build.py

Read-only. Sources:
  board items, comments, messages on `all`, scores, plain rows   the DynamoDB table of tools/team.py
  tool commands (board.py, gpu.py, paper.py)                      the events store of tools/events.py (S3)
  GPU jobs                                                        gpu.py's job records (Modal Dict, this person's jobs:
                                                                  launch, container start, end, exit code), the job ids
                                                                  named in everyone's `gpu.py get/wait/logs/kill`
                                                                  commands, and studies/**/run.json
  commits                                                         git log --all

data.json is kept small (the page reads all of it before the first picture). Each table is its column names and one
list per row. A column named @x holds whole seconds after `t0` (unix seconds, UTC); a column named $x holds an index
into `str`, the list of repeated strings. Tool commands are grouped by agent session: the seconds between one command
and the next, and one letter per command (a is codes[0]). Long text is cut to the length given in CUT, which keeps
the file under 500 kB; the page shows it as a label. Email addresses, home folders and anything shaped like a key
are replaced before writing.
"""
import calendar
import glob
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from boto3.dynamodb.conditions import Key  # noqa: E402

import board  # noqa: E402
import gpu  # noqa: E402
import team  # noqa: E402

LISTS = ("work", "result", "idea", "knowledge", "skill", "work-closed")
CUT = {"item": 110, "comment": 64, "msg": 64, "commit": 46, "cmd": 60}  # characters kept of each kind of text
PRIVATE = [(re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]*\w"), "[email]"), (re.compile(r"/(?:home|Users)/[^/\s\"']+"), "~"),
           (re.compile(r"\b(?:sk|hf|ghp|gho|ak|as|xoxb|xoxp)[-_][A-Za-z0-9_-]{16,}|\bAKIA[A-Z0-9]{16}\b"), "[key]")]


def text(s, kind=None):
    """Text for the page: nothing private, and at most CUT[kind] characters."""
    for pattern, word in PRIVATE:
        s = pattern.sub(word, s)
    n = CUT.get(kind)
    return s if n is None or len(s) <= n else s[:n - 1].rstrip() + "…"


def person(name):
    return name.split("@")[0].split("+")[-1]


def utc(text):
    return calendar.timegm(time.strptime(text, "%Y-%m-%dT%H:%M:%SZ"))


people, sessions = [], {}


def pid(name):
    name = person(name)
    if name not in people:
        people.append(name)
    return people.index(name)


def sid(who, session, t):
    """Index of an agent session; its first and last event give the span of its lane."""
    if not session:
        return -1
    s = sessions.setdefault(session, {"i": len(sessions), "p": pid(who), "a": t, "b": t, "n": 0})
    s["a"], s["b"], s["n"] = min(s["a"], t), max(s["b"], t), s["n"] + 1
    return s["i"]


# ---- tool commands -------------------------------------------------------------------------------------------------
events = sorted(team.Store("events").items())
codes, ev, submits, job_refs = [], [], [], {}
for key, v in events:
    t = int(key.split(":")[1]) / 1e9
    argv = v.get("argv") or ["?"]
    code = f"{v['tool']} {argv[0]}"
    if code not in codes:
        codes.append(code)
    s = sid(v["who"], v.get("session"), t)
    ev.append([round(t), pid(v["who"]), s, codes.index(code)])
    if v["tool"] == "gpu" and argv[0] == "submit":
        cmd = " ".join(argv[argv.index("--") + 1:]) if "--" in argv else " ".join(argv[2:])
        submits.append({"t": t, "p": pid(v["who"]), "s": s, "cls": argv[1] if len(argv) > 1 else "", "cmd": cmd,
                        "branch": v.get("branch", "")})
    if v["tool"] == "gpu" and argv[0] in ("get", "wait", "logs", "kill") and len(argv) > 1:
        ref = job_refs.setdefault(argv[1], {"p": pid(v["who"]), "s": s})
        ref.setdefault(argv[0], t)  # the first time of each verb

# ---- board ---------------------------------------------------------------------------------------------------------
with ThreadPoolExecutor(8) as pool:
    lists = list(pool.map(lambda l: board.rows(IndexName="new", KeyConditionExpression=Key("listed").eq(l)), LISTS))
    rows = {r["id"]: r for page in lists for r in page}
    messages = board.rows(KeyConditionExpression=Key("pk").eq("chan#all"))
    scores = board.rows(KeyConditionExpression=Key("pk").eq("scores"))
    plain = board.rows(KeyConditionExpression=Key("pk").eq("plain"))
    with_comments = [i for i, r in rows.items() if int(r.get("n_comments", 0))]
    threads = list(pool.map(lambda i: board.rows(KeyConditionExpression=Key("pk").eq(f"item#{i}") & Key("sk").begins_with("comment#")),
                            with_comments))

titles = {}
for r in plain:
    if "title" in r and r["sk"] == r.get("item", r["sk"]):
        titles[r["sk"]] = r["title"]
for r in plain:  # a result's own row carries its title; rows of single scores come after
    titles.setdefault(r.get("item", r["sk"]), r.get("title", ""))

items = []
for r in sorted(rows.values(), key=lambda r: int(r["at_ns"])):
    t = int(r["at_ns"]) / 1e9
    items.append({"id": r["id"], "k": r["kind"], "p": pid(r["who"]), "s": sid(r["who"], r.get("session"), t), "t": t,
                  "c": utc(r["closed_at"]) if "closed_at" in r else None,
                  "text": text(r["text"], "item"), "title": text(titles.get(r["id"], "")), "branch": r.get("branch", ""),
                  "ups": int(r.get("ups", 0)), "downs": int(r.get("downs", 0))})

comments = []
for item_id, thread in zip(with_comments, threads):
    for c in thread:
        t = int(c["sk"].split("#")[1]) / 1e9
        comments.append({"item": item_id, "p": pid(c["who"]), "s": sid(c["who"], c.get("session"), t), "t": t, "text": text(c["text"], "comment")})
comments.sort(key=lambda c: c["t"])

msgs = []
for m in messages:
    t = int(m["sk"].split("#")[0]) / 1e9
    msgs.append({"p": pid(m["who"]), "s": sid(m["who"], m.get("session"), t), "t": t, "text": text(m["text"], "msg"), "branch": m.get("branch", "")})

score_rows = []
for s in scores:
    score_rows.append({"t": int(s["sk"].split("#")[0]) / 1e9, "result": s["result"], "model": s["model"], "bench": s["benchmark"],
                       "right": int(s["right"]), "n": int(s["n"]), "config": text(s.get("config", "")),
                       "tokens": int(s["tokens"]) if s.get("tokens") is not None else None, "p": pid(s["who"])})

# ---- commits -------------------------------------------------------------------------------------------------------
log = subprocess.run(["git", "-C", str(ROOT), "log", "--all", "--source", "--shortstat", "--format=@@%H|%at|%ae|%S|%s"],
                     capture_output=True, text=True, check=True).stdout
commits = []
for block in log.split("@@")[1:]:
    head, _, stat = block.partition("\n")
    sha, at, email, ref, subject = head.split("|", 4)
    files = int(m.group(1)) if (m := re.search(r"(\d+) file", stat)) else 0
    ins = int(m.group(1)) if (m := re.search(r"(\d+) insertion", stat)) else 0
    dele = int(m.group(1)) if (m := re.search(r"(\d+) deletion", stat)) else 0
    branch = re.sub(r"^refs/(heads|remotes/origin|remotes)/", "", ref)
    commits.append({"h": sha[:7], "t": int(at), "p": pid(email), "branch": branch, "text": text(subject, "commit"), "files": files, "ins": ins, "del": dele})
commits.sort(key=lambda c: c["t"])

# ---- GPU jobs ------------------------------------------------------------------------------------------------------
ID = re.compile(r"^(.+)-(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)-[0-9a-f]{4}$")


def id_clock(job_id):
    """The time in a job id (the submitter's local clock), read as if it were UTC."""
    m = ID.match(job_id)
    return calendar.timegm((2026, int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6]))) if m else None


jobs = {}
for job_id, r in gpu.load().items():  # this person's jobs, complete: launch, container start, end
    j = r["job"]
    state = ("done" if r["end"]["exit_code"] == 0 else "failed") if "end" in r and not r["end"].get("stopped") else \
        "stopped" if "end" in r else "cancelled" if "cancel" in r else "died" if "died" in r else "no end recorded"
    end = r["end"]["at"] if "end" in r else r["cancel"]["at"] if "cancel" in r else None
    jobs[job_id] = {"id": job_id, "p": pid(j["who"]), "t": j["at"], "start": r["start"]["at"] if "start" in r else None,
                    "end": end, "state": state, "gpu": r["start"]["gpu"] if "start" in r else j["class"], "cmd": j["cmd"],
                    "branch": j.get("branch", ""), "src": "gpu.py record"}

run_json = {}
for path in glob.glob(str(ROOT / "studies/**/run.json"), recursive=True):
    r = json.loads(Path(path).read_text())
    if isinstance(r, dict) and isinstance(r.get("job_id"), str) and ID.match(r["job_id"]):
        run_json[r["job_id"]] = (r, str(Path(path).relative_to(ROOT)))

# the offset of each person's job-id clock from UTC: the whole hour that puts most ids next to one of their submits
offset = {}
for p in range(len(people)):
    mine = [id_clock(i) for i in {**job_refs, **run_json} if (m := ID.match(i)) and person(m[1]) == people[p]]
    subs = [s["t"] for s in submits if s["p"] == p]
    if mine and subs:
        offset[p] = max(range(-12, 13), key=lambda h: sum(any(abs(c - h * 3600 - s) < 90 for s in subs) for c in mine))

for job_id in {**run_json, **job_refs}:
    m = ID.match(job_id)
    if job_id in jobs or not m or person(m[1]) not in people or pid(m[1]) not in offset:
        continue
    p = pid(m[1])
    launch = id_clock(job_id) - offset[p] * 3600
    near = min((s for s in submits if s["p"] == p), key=lambda s: abs(s["t"] - launch))
    sub = near if abs(near["t"] - launch) < 90 else None
    ref, (rj, path) = job_refs.get(job_id, {}), run_json.get(job_id, ({}, ""))
    end, state, src = None, "no end recorded", "job id"
    if "kill" in ref:
        end, state, src = ref["kill"], "killed", "gpu.py kill command"
    elif rj.get("finished_utc"):
        end, state, src = utc(rj["finished_utc"]), "done", path
    elif "get" in ref:
        end, state, src = ref["get"], "output copied", "gpu.py get command"
    jobs[job_id] = {"id": job_id, "p": p, "t": launch, "start": None, "end": end if end and end > launch else None, "state": state,
                    "gpu": rj.get("gpu") or (sub["cls"] if sub else ""), "cmd": sub["cmd"] if sub else rj.get("command", ""),
                    "branch": sub["branch"] if sub else "", "src": src}

known = sorted(j["t"] for j in jobs.values())
for n, s in enumerate(submits):  # a submit whose job id no later command named: a launch with no recorded end
    if not any(abs(s["t"] - t) < 90 for t in known):
        jobs[f"submit-{n}"] = {"id": "", "p": s["p"], "t": int(s["t"]), "start": None, "end": None, "state": "no end recorded",
                               "gpu": s["cls"], "cmd": s["cmd"], "branch": s["branch"], "src": "gpu.py submit command"}
for j in jobs.values():
    near = min((s for s in submits if s["p"] == j["p"]), key=lambda s: abs(s["t"] - j["t"]), default=None)
    j["s"] = near["s"] if near and abs(near["t"] - j["t"]) < 90 else -1
    j["cmd"] = text(j["cmd"].split(" && ")[-1], "cmd")  # the job itself, without the set-up steps before it
    j["run_json"] = run_json[j["id"]][1] if j["id"] in run_json else ""
jobs = sorted(jobs.values(), key=lambda j: j["t"])

T0 = min(min(e[0] for e in ev), commits[0]["t"])
strings = {}


def table(rows, cols):
    """Rows as lists in the order of cols. @x: whole seconds after T0. $x: an index into strings."""
    def cell(r, c):
        v = r[c.lstrip("@$")]
        if c[0] == "@":
            return None if v is None else round(v) - T0
        return strings.setdefault(v, len(strings)) if c[0] == "$" else v
    return {"cols": cols, "rows": [[cell(r, c) for c in cols] for r in rows]}


groups = {}  # the commands of one session of one person, in order of time
for t, p, s, code in ev:
    g = groups.setdefault((p, s), {"p": p, "s": s, "t": [], "c": "", "last": T0})
    g["t"].append(t - g["last"])
    g["c"] += chr(97 + code)
    g["last"] = t
for g in groups.values():
    del g["last"]

out = {"built": int(time.time()), "t0": T0, "people": people, "codes": codes,
       "sessions": table([{**s, "id": k[:8]} for k, s in sessions.items()], ["p", "@a", "@b", "n", "id"]),
       "ev": list(groups.values()),
       "items": table(items, ["id", "$k", "p", "s", "@t", "@c", "text", "title", "$branch", "ups", "downs"]),
       "comments": table(comments, ["item", "p", "s", "@t", "text"]),
       "msgs": table(msgs, ["p", "s", "@t", "text", "$branch"]),
       "scores": table(score_rows, ["@t", "result", "$model", "$bench", "right", "n", "config", "tokens", "p"]),
       "commits": table(commits, ["h", "@t", "p", "$branch", "text", "files", "ins", "del"]),
       "jobs": table(jobs, ["id", "p", "s", "@t", "@start", "@end", "$state", "$gpu", "cmd", "$branch", "$src", "run_json"])}
out["str"] = list(strings)
written = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
for pattern, _ in PRIVATE:
    if m := pattern.search(written):
        sys.exit(f"private text left in the data: {m[0][:12]}")
(HERE / "data.json").write_text(written)
print({k: len(v["rows"] if isinstance(v, dict) else v) if not isinstance(v, int) else v for k, v in out.items()},
      f"{(HERE / 'data.json').stat().st_size / 1e3:.0f} kB")
print("job-id clock offsets from UTC (hours):", {people[p]: h for p, h in offset.items()})
print("job states:", {s: sum(j["state"] == s for j in jobs) for s in sorted({j["state"] for j in jobs})})
