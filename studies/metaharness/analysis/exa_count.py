"""Count the team's Exa use from Claude Code transcripts.

  python3 -I count_exa.py            writes exa_calls.jsonl, mcp_calls.jsonl and summary.json next to this file

One row of exa_calls.jsonl is one invocation of tools/exa.py (or studies/theory/lib/papers.py search|fetch, which
execs it) inside a Bash tool call: one HTTP request to api.exa.ai. Each tool_use id is read once.
"""
import collections
import json
import re
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = [  # (person, machine, folder of *.jsonl sessions with <session>/subagents/ below)
    ("abaybektursun", "linux", Path.home() / ".claude/projects/-home-abay-Projects-iterate-hack"),
    ("abaybektursun", "mac", HERE / "team_traces/abaybektursun-mac/claude"),
    ("frustea", "mac", HERE / "team_traces/frustea/claude"),
    ("sameraslan", "mac", HERE / "team_traces/sameraslan/claude"),
]
EXCLUDE = {"2a4101ad-96a8-4ba8-938f-84372c119025"}  # the session that wrote and ran this script: it quotes exa.py, it does not call it
COST = re.compile(r"\[(\d+) results, ([0-9.eE+-]+) USD\]")
SCRIPT = re.compile(r"(?:^|/)(exa|papers)\.py$")
LOOSE = re.compile(r"(?:exa|papers)\.py['\"]?\s+(search|fetch)\b")
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n(.*?)\n\1\b", re.S)
OPERATOR = re.compile(r"[();<>|&]+")
STOP = {";", "&&", "||", "|", "&", ">", ">>", "<", "2>", "|&", "(", ")", ";;", "2>&1", "&>", "do", "done"}
ERRORS = [
    ("exa_api_key_not_set", r"EXA_API_KEY is not set"),
    ("http_401", r"HTTP Error 401"), ("http_402", r"HTTP Error 402"), ("http_403", r"HTTP Error 403"),
    ("http_429", r"HTTP Error 429"), ("http_400", r"HTTP Error 400"), ("http_5xx", r"HTTP Error 5\d\d"),
    ("http_other", r"HTTP Error \d+"),
    ("network", r"URLError|Temporary failure in name resolution|timed out|Connection (?:refused|reset)|nodename nor servname"),
    ("user_or_permission_rejected", r"doesn't want to proceed|was rejected|requires approval|Permission to use|permission.{0,40}denied|haven't granted"),
    ("argparse_usage", r"usage: exa\.py|error: (?:unrecognized|the following|argument)"),
    ("file_not_found", r"No such file or directory|can't open file"),
    ("python_traceback", r"Traceback \(most recent call last\)"),
    ("timeout_or_killed", r"Command timed out|Exit code 1(?:24|37|43)"),
]
RESULT_URL = re.compile(r"^  (https?://\S+)$", re.M)  # search output: the URL line under each title
FETCH_URL = re.compile(r"^# .*\n(https?://\S+)$", re.M)  # fetch output: "# title" then the URL
ARXIV = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", re.I)


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return ""


def invocations(command):
    """The exa.py invocations a shell command holds, one dict per expected HTTP request; [] when exa.py is only
    mentioned inside a string; None when the quoting cannot be parsed. A `for v in a b c; do ... done` loop with a
    literal item list is expanded to one invocation per item."""
    heredocs = [m[2].split("\n") for m in HEREDOC.finditer(command)]
    command = HEREDOC.sub("", command)  # a heredoc body is data, and its apostrophes would break the lexer
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return None
    found, loops = [], []  # loops: the enclosing for loops, as (variable, items or None when not literal)
    for i, token in enumerate(tokens[:-1]):
        if token == "for" and i + 2 < len(tokens) and tokens[i + 2] == "in":
            items = []
            for t in tokens[i + 3:]:
                if t in (";", "do"):
                    break
                items.append(t)
            literal = not any(OPERATOR.fullmatch(x) or x[:1] in "$`" for x in items)
            loops.append((tokens[i + 1], items if literal else None))
        elif token == "while" and "read" in tokens[i + 1:i + 6]:  # while read -r q; do ... done <<'EOF'
            j = i + 1 + tokens[i + 1:i + 6].index("read")
            names = [t for t in tokens[j + 1:j + 4] if not t.startswith("-") and not OPERATOR.fullmatch(t) and t != "do"]
            loops.append((names[-1] if names else "_", [x for x in heredocs[0] if x.strip()] if len(heredocs) == 1 else None))
        elif token == "done" and loops:
            loops.pop()
        if not (SCRIPT.search(token) and tokens[i + 1] in ("search", "fetch")):
            continue
        args, cut, in_args = [], False, True  # cut: this invocation's stdout is piped or redirected
        for t in tokens[i + 2:]:
            if in_args and not OPERATOR.fullmatch(t) and t not in ("do", "done"):
                args.append(t)
                continue
            if in_args and t.startswith(">") and args and args[-1].isdigit():  # the 2 of 2>&1
                args.pop()
            in_args = False
            if t in (";", "&&", "||", "&", ")", ";;", "do", "done"):
                break
            cut = cut or t in ("|", "|&", ">", ">>", "&>")
        if "--help" in args or "-h" in args:
            continue
        variants = [{}]
        for var, items in loops:
            if items:
                variants = [{**v, var: item} for v in variants for item in items]
        for values in variants:
            def fill(a):
                for var, item in values.items():
                    a = re.sub(r"\$\{?%s\}?(?![A-Za-z0-9_])" % re.escape(var), lambda m: item, a)
                return a
            mine = [fill(a) for a in args]
            call = {"kind": tokens[i + 1], "script": token, "query": None, "urls": [], "n": None, "since": None, "domains": [],
                    "cut": cut, "in_loop": bool(loops), "dynamic": any(items is None for _, items in loops)}
            positional, j = [], 0
            while j < len(mine):
                a = mine[j]
                m = re.fullmatch(r"--([a-z]+)=(.*)", a)
                if m:
                    name, value, j = m[1], m[2], j + 1
                elif a.startswith("--") and j + 1 < len(mine):
                    name, value, j = a[2:], mine[j + 1], j + 2
                else:
                    positional.append(a)
                    j += 1
                    continue
                if name == "domain":
                    call["domains"].append(value)
                elif name in ("n", "since"):
                    call[name] = value
            if call["kind"] == "search":
                call["query"] = positional[0] if positional else None
            else:
                call["urls"] = [u for u in positional if u.startswith("http")]
            found.append(call)
    return found


FAIL = re.compile(r"EXA_API_KEY is not set|usage: exa\.py|Traceback \(most recent call last\)|can't open file")


def reason_of(output):
    for name, pattern in ERRORS:
        if re.search(pattern, output):
            return name
    return "other_error"


def files():
    for person, machine, folder in SOURCES:
        paths = sorted(folder.rglob("*.jsonl"))
        mains = [p for p in paths if "subagents" not in p.parts]
        for p in mains + [p for p in paths if "subagents" in p.parts]:  # mains first: a fork repeats its parent's records
            if p.name == "journal.jsonl":
                continue
            if "subagents" in p.parts:
                session, agent = p.parts[p.parts.index("subagents") - 1], p.stem
            else:
                session, agent = p.stem, "main"
            yield person, machine, session, agent, p


def main():
    uses, results, direct, n_files = {}, {}, {}, 0  # tool_use id -> record
    for person, machine, session, agent, path in files():
        n_files += 1
        with open(path, errors="replace") as f:
            last_ts = None
            for line in f:
                if '"tool_use"' not in line and '"tool_result"' not in line:
                    continue
                if "exa" not in line.lower() and "papers.py" not in line and '"tool_result"' not in line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                last_ts = record.get("timestamp") or last_ts
                content = (record.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use":
                        name, inp = block.get("name", ""), block.get("input") or {}
                        mcp = name.startswith("mcp__") and "exa" in name.lower()
                        bash = name == "Bash" and LOOSE.search(str(inp.get("command", "")))
                        if name == "Bash" and not bash and re.search(r"api\.exa\.ai|exa_py|from exa\b", str(inp.get("command", ""))):
                            direct[block["id"]] = {"ts": record.get("timestamp"), "who": person, "session": session,
                                                   "agent": agent, "command": str(inp["command"])[:400]}
                        if (mcp or bash) and block["id"] not in uses and session not in EXCLUDE:
                            uses[block["id"]] = {"id": block["id"], "name": name, "input": inp, "ts": record.get("timestamp") or last_ts,
                                                 "who": person, "machine": machine, "session": session, "agent": agent}
                    elif block.get("type") == "tool_result" and block.get("tool_use_id") in uses:
                        results.setdefault(block["tool_use_id"], {"output": text_of(block.get("content")),
                                                                  "is_error": bool(block.get("is_error"))})
    rows, mcp_rows, skipped = [], [], []
    for use in uses.values():
        base = {k: use[k] for k in ("id", "ts", "who", "machine", "session", "agent")}
        result = results.get(use["id"])
        output = result["output"] if result else ""
        if use["name"] != "Bash":
            if result is None:
                status = "no_result"
            elif result["is_error"] or re.search(r"\b401\b|Unauthorized|rror", output[:400]):
                status = "failed_401" if re.search(r"401|Unauthorized|[Aa]uth", output) else "failed_other"
            else:
                status = "ok"
            mcp_rows.append({**base, "tool": use["name"], "query": use["input"].get("query") or use["input"].get("url")
                             or json.dumps(use["input"])[:300], "status": status, "output_head": output[:200]})
            continue
        command = str(use["input"].get("command", ""))
        calls = invocations(command)
        costs = [(int(n), float(usd)) for n, usd in COST.findall(output)]
        blank = {"script": "?", "query": None, "urls": [], "n": None, "since": None, "domains": [], "cut": True,
                 "in_loop": False, "dynamic": True}
        if not calls and costs:  # exa.py started through zsh -ic '...': parse the quoted command
            try:
                calls = [c for t in shlex.split(command) if LOOSE.search(t) for c in invocations(t) or []]
            except ValueError:
                calls = []
            calls = calls or [{**blank, "kind": m} for m in LOOSE.findall(command)][:len(costs)]
        if not calls:
            skipped.append({**base, "command": command[:300]})
            continue
        while len(calls) < len(costs):  # a loop over a computed list: more requests than the command spells out
            calls.append({**calls[-1], "query": None, "urls": [], "dynamic": True})
        # Cost lines go first to the invocations whose output is shown in full, then to the piped or redirected ones.
        order = [i for i, c in enumerate(calls) if not c["cut"]] + [i for i, c in enumerate(calls) if c["cut"]]
        cost_of = dict(zip(order, costs))
        failures = len(FAIL.findall(output))  # one per failed invocation whose stderr reached the transcript
        result_urls = RESULT_URL.findall(output)
        for i, call in enumerate(calls):
            row = {**base, "index": i, "calls_in_command": len(calls), **call, "results": None, "usd": None, "reason": None}
            if i in cost_of:
                row["results"], row["usd"] = cost_of[i]
                row["status"] = "ok" if row["results"] else "ok_zero_results"
            elif result is None:
                row["status"], row["reason"] = "unknown", "no tool_result in the transcript"
            elif failures > 0:
                failures -= 1
                row["status"], row["reason"] = "failed", reason_of(output)
            elif call["cut"] or "<persisted-output>" in output or "Output too large" in output:
                shown = bool(result_urls) if call["kind"] == "search" else bool(FETCH_URL.search(output))
                row["status"] = "ok_results_shown" if shown else "presumed_ok"
                row["reason"] = ("cost line cut off by a pipe; result lines of this kind are in the tool output" if shown else
                                 "output piped, redirected or saved to a file: no cost line, no result line and no error in the transcript")
            else:
                row["status"], row["reason"] = "unknown", "full output shown, with no cost line and no error text"
            if i == 0:
                row["result_urls"] = result_urls  # every search result URL in this tool call's output
            row["command"] = command[:600]
            rows.append(row)
    rows.sort(key=lambda r: (r["ts"] or "", r["id"], r["index"]))
    mcp_rows.sort(key=lambda r: r["ts"] or "")
    with open(HERE / "exa_calls.jsonl", "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    with open(HERE / "mcp_calls.jsonl", "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in mcp_rows)

    C = collections.Counter
    ok = [r for r in rows if r["status"] in ("ok", "ok_zero_results", "ok_results_shown", "presumed_ok")]
    priced = [r for r in rows if r["usd"] is not None]
    per_search = sorted(r["usd"] for r in priced if r["kind"] == "search")[len([r for r in priced if r["kind"] == "search"]) // 2]
    presumed = [r for r in rows if r["status"] in ("presumed_ok", "ok_results_shown")]
    early = [r for r in rows if (r["ts"] or "") < "2026-11-15T05:25"]

    def split(rs):
        return {"calls": len(rs), "search": sum(r["kind"] == "search" for r in rs), "fetch": sum(r["kind"] == "fetch" for r in rs),
                "status": dict(C(r["status"] for r in rs)),
                "usd": round(sum(r["usd"] or 0 for r in rs), 4),
                "sessions": len({(r["who"], r["session"]) for r in rs}),
                "agents": len({(r["who"], r["session"], r["agent"]) for r in rs}),
                "main_agents": len({(r["who"], r["session"]) for r in rs if r["agent"] == "main"}),
                "subagents": len({(r["who"], r["session"], r["agent"]) for r in rs if r["agent"] != "main"})}

    fetched = [u for r in ok if r["kind"] == "fetch" for u in r["urls"]]
    found = [u for r in rows for u in r.get("result_urls", [])]
    domain = lambda u: re.sub(r"^www\.", "", re.sub(r"^https?://", "", u).split("/")[0].lower())
    norm = lambda u: re.sub(r"^https?://(www\.)?", "", u).rstrip("/").lower()
    searches = [r for r in rows if r["kind"] == "search"]
    summary = {
        "transcript_files_read": n_files,
        "bash_tool_calls_with_exa": len({r["id"] for r in rows}),
        "bash_tool_calls_mentioning_but_not_running_exa": len(skipped),
        "all": split(rows),
        "by_kind_status": {k: dict(C(r["status"] for r in rows if r["kind"] == k)) for k in ("search", "fetch")},
        "failure_reasons": dict(C(r["reason"] for r in rows if r["status"] == "failed")),
        "failed_before_any_http_request": sum(r["reason"] in ("exa_api_key_not_set", "argparse_usage", "file_not_found") for r in rows),
        "unknown_reasons": dict(C(r["reason"] for r in rows if r["status"] == "unknown")),
        "calls_with_cost_line": len(priced),
        "usd_total_from_cost_lines": round(sum(r["usd"] for r in priced), 4),
        "usd_search": round(sum(r["usd"] for r in priced if r["kind"] == "search"), 4),
        "usd_fetch": round(sum(r["usd"] for r in priced if r["kind"] == "fetch"), 4),
        "usd_median_per_priced_search": per_search,
        "usd_ESTIMATE_for_ok_calls_without_cost_line": round(sum(per_search if r["kind"] == "search" else 0.001 * max(len(r["urls"]), 1) for r in presumed), 3),
        "up_to_2026-11-15T05:25_for_comparison_with_README": {"calls": len(early), "status": dict(C(r["status"] for r in early)),
            "agents_with_ok_call": len({(r["who"], r["session"], r["agent"]) for r in early if r in ok}),
            "mcp_calls": sum((r["ts"] or "") < "2026-11-15T05:25" for r in mcp_rows)},
        "bash_commands_calling_exa_without_exa_py": len(direct),
        "results_returned_total": sum(r["results"] for r in priced),
        "search_results_returned": sum(r["results"] for r in priced if r["kind"] == "search"),
        "pages_fetched_from_cost_lines": sum(r["results"] for r in priced if r["kind"] == "fetch"),
        "fetch_urls_requested_in_ok_calls": len(fetched),
        "distinct_urls_fetched": len({norm(u) for u in fetched}),
        "distinct_urls_in_search_results": len({norm(u) for u in found}),
        "distinct_urls_search_or_fetch": len({norm(u) for u in fetched + found}),
        "top_domains_fetched": C(domain(u) for u in {norm(u): u for u in fetched}.values()).most_common(15),
        "top_domains_in_search_results": C(domain(u) for u in {norm(u): u for u in found}.values()).most_common(15),
        "distinct_arxiv_ids_fetched": len({m for u in fetched for m in ARXIV.findall(u)}),
        "distinct_arxiv_ids_in_search_results": len({m for u in found for m in ARXIV.findall(u)}),
        "distinct_arxiv_ids_search_or_fetch": len({m for u in fetched + found for m in ARXIV.findall(u)}),
        "by_person": {w: split([r for r in rows if r["who"] == w]) for w in sorted({r["who"] for r in rows})},
        "by_person_machine": {f"{w}/{m}": split([r for r in rows if (r["who"], r["machine"]) == (w, m)])
                              for w, m in sorted({(r["who"], r["machine"]) for r in rows})},
        "agents_with_an_ok_call": len({(r["who"], r["session"], r["agent"]) for r in ok}),
        "sessions_with_an_ok_call": len({(r["who"], r["session"]) for r in ok}),
        "scripts": dict(C(re.sub(r".*/", "", r["script"]) if not r["script"].endswith("tools/exa.py") else "tools/exa.py" for r in rows)),
        "first_call_utc": rows[0]["ts"], "last_call_utc": rows[-1]["ts"],
        "calls_per_utc_hour": dict(sorted(C(r["ts"][:13] for r in rows if r["ts"]).items())),
        "ok_calls_per_utc_hour": dict(sorted(C(r["ts"][:13] for r in ok if r["ts"]).items())),
        "search_flags": {"searches": len(searches), "with_since": sum(bool(r["since"]) for r in searches),
                         "with_domain": sum(bool(r["domains"]) for r in searches), "with_n": sum(bool(r["n"]) for r in searches),
                         "n_values": dict(C(r["n"] or "default 5" for r in searches)),
                         "domains": dict(C(d for r in searches for d in r["domains"])),
                         "since_values": dict(C(r["since"] for r in searches if r["since"]))},
        "distinct_search_queries": len({r["query"] for r in searches if r["query"]}),
        "median_query_words": sorted(len(r["query"].split()) for r in searches if r["query"])[len([r for r in searches if r["query"]]) // 2],
        "mcp": {"calls": len(mcp_rows), "status": dict(C(r["status"] for r in mcp_rows)), "tools": dict(C(r["tool"] for r in mcp_rows)),
                "by_person": dict(C(r["who"] for r in mcp_rows)),
                "agents": len({(r["who"], r["session"], r["agent"]) for r in mcp_rows}),
                "first_utc": mcp_rows[0]["ts"] if mcp_rows else None, "last_utc": mcp_rows[-1]["ts"] if mcp_rows else None},
    }
    facts = Path.home() / "Projects/iterate-hack/tools/demo_facts.py"  # the earlier list of 125 pages fetched through Exa
    if facts.exists():
        listed = {norm(u) for u in re.findall(r"'url': '([^']+)'", facts.read_text().split("SOURCES = [")[1])}
        have = {norm(u) for u in fetched}
        summary["against_demo_facts_SOURCES"] = {"listed": len(listed), "also_in_these_transcripts": len(listed & have),
                                                 "listed_but_absent_from_these_transcripts": len(listed - have),
                                                 "union_distinct_urls_fetched": len(listed | have)}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1))
    (HERE / "direct_exa_mentions.jsonl").write_text("".join(json.dumps(s) + "\n" for s in direct.values()))
    seen = set()
    with open(HERE / "queries.tsv", "w") as f:
        for r in searches:
            if r["query"] and r["query"] not in seen and r in ok:
                seen.add(r["query"])
                f.write(f'{r["ts"]}\t{r["who"]}\t{r["agent"][:14]}\t{r["status"]}\t{r["results"]}\t{r["since"] or ""}\t{",".join(r["domains"])}\t{r["query"]}\n')
    (HERE / "skipped_mentions.jsonl").write_text("".join(json.dumps(s) + "\n" for s in skipped))
    json.dump(summary, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
