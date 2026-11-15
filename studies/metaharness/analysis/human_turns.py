"""How much of the hackathon work a person typed: messages typed by people against agent turns and tool calls.

Reads Claude Code transcripts (JSONL). Inputs, each given on the command line:
  --store <folder>        a copy of the team transcript store (`s3://.../traces/`): <person>/claude/<project>/<session>.jsonl,
                          subagent transcripts under <session>/subagents/. The person is the first folder below <folder>
                          (a leading "<digits>+" is dropped: "8038263+frustea" is frustea).
  --local <person>=<dir>  one local Claude Code project folder (~/.claude/projects/<project>) of that person.

Main sessions are the *.jsonl files outside any `subagents/` folder. A session id seen in several inputs is one session:
its records are merged by record uuid (tool calls by tool_use id, assistant turns by message id). Only records with a
timestamp in the window [--start, run time] count; a session counts if it has at least one record in the window.

Rule for a message typed by a person (a record kept as human):
  1. type == "user", isSidechain false, isMeta not true, isCompactSummary not true, no `toolUseResult`, and no
     tool_result block in its content;
  2. entrypoint is not "sdk-cli" (headless `claude -p` runs, such as the scripted review runs, have no person typing);
  3. if the record has an `origin` field, origin.kind == "human" (this drops task notifications and messages from peer
     sessions); records without `origin` (older client versions) go on to rule 4;
  4. its text (the string content, or the text blocks of a list content) with interruption markers
     ("[Request interrupted by user...]") removed is not empty and does not start with a wrapper: <task-notification>,
     <system-reminder>, <command-name>, <command-message>, <local-command-stdout>, <local-command-caveat>,
     <bash-input>, <bash-stdout>, <bash-stderr>, <user-prompt-submit-hook>, "Another Claude session sent a message",
     "Base directory for this skill", "This session is being continued from a previous conversation".
A pasted block or an image with text counts as one message. Slash commands (<command-name>) do not count.

Counted per person and in total: sessions (and how many are headless), human messages, characters typed (total,
median), assistant turns (distinct message ids), tool calls by the main agent (tool_use blocks) and by subagents.

Prints no message text except with --samples K (K random kept and K random excluded records, 120 characters each), used
once to check the rule by reading. Writes only counts to --out/metrics.json. The output folder must not exist.
"""

import argparse
import json
import random
import re
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

WRAPPERS = ("<task-notification>", "<system-reminder>", "<command-name>", "<command-message>", "<local-command-stdout>",
            "<local-command-caveat>", "<bash-input>", "<bash-stdout>", "<bash-stderr>", "<user-prompt-submit-hook>",
            "Another Claude session sent a message", "Base directory for this skill",
            "This session is being continued from a previous conversation")
INTERRUPT = re.compile(r"\[Request interrupted by user[^\]]*\]")
RULE = __doc__.split("Rule for a message typed by a person (a record kept as human):")[1].split("Counted per person")[0].strip()


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content if b.get("type") == "text")


def classify(r):
    """(kept, reason, text) for one user record."""
    content = r["message"]["content"]
    text = text_of(content)
    if r.get("isSidechain"):
        return False, "sidechain", text
    if r.get("isMeta"):
        return False, "meta", text
    if r.get("isCompactSummary"):
        return False, "compaction", text
    if "toolUseResult" in r or (isinstance(content, list) and any(b.get("type") == "tool_result" for b in content)):
        return False, "tool_result", text
    if r.get("entrypoint") == "sdk-cli":
        return False, "headless", text
    if "origin" in r and (r["origin"] or {}).get("kind") != "human":
        return False, f"origin:{(r['origin'] or {}).get('kind')}", text
    clean = INTERRUPT.sub("", text).strip()
    if not clean:
        return False, "empty_or_interrupt", text
    if clean.startswith(WRAPPERS):
        return False, "wrapper", text
    return True, "human", clean


def person_of_store(path, store):
    return re.sub(r"^\d+\+", "", path.relative_to(store).parts[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", action="append", default=[], type=Path)
    ap.add_argument("--local", action="append", default=[])
    ap.add_argument("--start", default="2026-11-14T18:00:00Z")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--samples", type=int, default=0)
    a = ap.parse_args()
    if not a.store and not a.local:
        ap.error("give at least one --store or --local folder")
    if a.out.exists():
        raise SystemExit(f"{a.out} exists; a rerun gets the next number")
    start = datetime.fromisoformat(a.start.replace("Z", "+00:00"))
    end = datetime.now(timezone.utc)

    files = []  # (person, path, is_subagent)
    for store in a.store:
        for p in sorted(store.rglob("*.jsonl")):
            files.append((person_of_store(p, store), p, "subagents" in p.parts))
    for spec in a.local:
        person, folder = spec.split("=", 1)
        for p in sorted(Path(folder).expanduser().rglob("*.jsonl")):
            files.append((person, p, "subagents" in p.parts))

    sessions = {}  # session id -> {"person", "users": {uuid: rec}, "turns": set, "tools": set, "headless": bool}
    sub_tools = defaultdict(set)  # person -> tool_use ids in subagent files
    owner = {}
    for person, path, is_sub in files:
        with open(path, errors="replace") as f:
            for line in f:
                r = json.loads(line)
                ts = r.get("timestamp")
                if r.get("type") not in ("user", "assistant") or not ts:
                    continue
                t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if not (start <= t <= end):
                    continue
                if is_sub:
                    if r["type"] == "assistant":
                        for b in r["message"]["content"] if isinstance(r["message"]["content"], list) else []:
                            if b.get("type") == "tool_use":
                                sub_tools[person].add(b["id"])
                    continue
                sid = r["sessionId"]
                if sid in owner and owner[sid] != person:
                    raise SystemExit(f"session {sid} found under two people: {owner[sid]}, {person}")
                owner[sid] = person
                s = sessions.setdefault(sid, {"person": person, "users": {}, "turns": set(), "tools": set(),
                                              "headless": False})
                if r.get("entrypoint") == "sdk-cli":
                    s["headless"] = True
                if r["type"] == "user":
                    s["users"][r["uuid"]] = r
                else:
                    s["turns"].add(r["message"]["id"])
                    for b in r["message"]["content"] if isinstance(r["message"]["content"], list) else []:
                        if b.get("type") == "tool_use":
                            s["tools"].add(b["id"])

    per = defaultdict(lambda: {"sessions": 0, "headless_sessions": 0, "human_messages": 0, "assistant_turns": 0,
                               "main_tool_calls": 0, "subagent_tool_calls": 0, "chars": [], "excluded": defaultdict(int)})
    kept_s, excl_s = [], []
    for sid, s in sessions.items():
        p = per[s["person"]]
        p["sessions"] += 1
        p["headless_sessions"] += s["headless"]
        p["assistant_turns"] += len(s["turns"])
        p["main_tool_calls"] += len(s["tools"])
        for r in s["users"].values():
            kept, reason, text = classify(r)
            if kept:
                p["human_messages"] += 1
                p["chars"].append(len(text))
                kept_s.append(text)
            else:
                p["excluded"][reason] += 1
                excl_s.append(f"[{reason}] {text}")
    for person, ids in sub_tools.items():
        per[person]["subagent_tool_calls"] = len(ids)

    if a.samples:
        rng = random.Random(0)
        for name, pool in (("KEPT", kept_s), ("EXCLUDED", excl_s)):
            print(f"--- {name} ({len(pool)}) ---")
            for t in rng.sample(pool, min(a.samples, len(pool))):
                print(" ", t.replace("\n", " ")[:120])

    def summary(p):
        c = p["chars"]
        return {"sessions": p["sessions"], "headless_sessions": p["headless_sessions"],
                "human_messages": p["human_messages"], "assistant_turns": p["assistant_turns"],
                "main_tool_calls": p["main_tool_calls"], "subagent_tool_calls": p["subagent_tool_calls"],
                "tool_calls": p["main_tool_calls"] + p["subagent_tool_calls"],
                "chars_typed_total": sum(c), "chars_typed_median": statistics.median(c) if c else 0,
                "excluded_user_records": dict(sorted(p["excluded"].items()))}

    total = {"sessions": 0, "headless_sessions": 0, "human_messages": 0, "assistant_turns": 0, "main_tool_calls": 0,
             "subagent_tool_calls": 0, "chars": [], "excluded": defaultdict(int)}
    for p in per.values():
        for k in ("sessions", "headless_sessions", "human_messages", "assistant_turns", "main_tool_calls",
                  "subagent_tool_calls"):
            total[k] += p[k]
        total["chars"] += p["chars"]
        for k, v in p["excluded"].items():
            total["excluded"][k] += v
    out = {"window_utc": [start.isoformat(), end.isoformat()], "rule": RULE,
           "per_person": {k: summary(v) for k, v in sorted(per.items())}, "total": summary(total)}
    t = out["total"]
    t["tool_calls_per_human_message"] = round(t["tool_calls"] / t["human_messages"], 1)
    a.out.mkdir(parents=True)
    (a.out / "metrics.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "excluded_user_records"}
                      for k, v in {**out["per_person"], "total": t}.items()}, indent=1))


if __name__ == "__main__":
    main()
