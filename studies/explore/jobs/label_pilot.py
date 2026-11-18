"""Label pilot (specs/label-pilot.md): two programs shown in every call, only the label "current" moves.

    python3 -m studies.explore.jobs.label_pilot --task ahc014 --model gpt-6.2-sol --free 2 --max-usd 7 \
        --out runs/explore/ahc014/label-pilot-01

Writes rows.jsonl (one row per call: label condition, kind, reply, score, similarity to A and B, tokens, USD) and
code/<row id>.py to --out. Refuses an existing --out. Laptop: the model is an API call, the scorer runs on the CPU.
"""
import argparse
import difflib
import json
import pathlib
import re
import subprocess
import sys

from studies.explore.lib.loop import SYSTEM, Task, chat, cost, parse

ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True)
ap.add_argument("--model", required=True)
ap.add_argument("--free", type=int, default=1, help="free calls per label condition")
ap.add_argument("--max-usd", type=float, required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

root = pathlib.Path(__file__).resolve().parents[1]
data = root / "data" / "label_pilot_v1"
cfg = json.loads((data / "tasks.json").read_text())[args.task]
prog = {x: (data / f"{args.task}_{x}.py").read_text() for x in "AB"}
task = Task(root / "tasks" / args.task)
out = pathlib.Path(args.out)
assert not out.exists(), f"{out} exists: a rerun gets a new folder"
(out / "code").mkdir(parents=True)
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
(out / "run.json").write_text(json.dumps({**vars(args), "commit": commit, "command": " ".join(sys.argv)}, indent=1))
log, usd, n, worst = open(out / "rows.jsonl", "a"), 0.0, 0, 0.0


def context(current):
    """The same text in both conditions except the two labels. A is always shown first."""
    lab = {x: "the CURRENT PROGRAM" if x == current else "a REFERENCE PROGRAM" for x in "AB"}
    parts = [f"TASK:\n{task.spec}\n\nTwo working programs for this task follow. Program 1 is {lab['A']}. "
             f"Program 2 is {lab['B']}."]
    for i, x in enumerate("AB"):
        parts.append(f"PROGRAM {i + 1}, {lab[x]} (validation score {cfg['scores'][x]}):\n```python\n{prog[x]}\n```")
    return "\n\n".join(parts)


def sim(code, x):
    return round(difflib.SequenceMatcher(None, code.splitlines(), prog[x].splitlines()).ratio(), 3)


def call(current, kind, messages, method=None):
    global usd, n, worst
    assert usd + 2 * max(worst, 0.2) <= args.max_usd, f"stopping before the cap: spent {usd:.2f} of {args.max_usd}"
    text, usage = chat(messages, args.model)
    c = cost(usage, args.model)
    usd, worst, n = usd + c, max(worst, c), n + 1
    row = {"id": f"c{n:03d}", "task": args.task, "current": current, "kind": kind, "method": method,
           "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
           "usd": round(c, 4), "reply": text}
    if kind != "rank":
        idea, code = parse(text)
        res = task.evaluate(code) if code else {"score": None, "valid": False, "msg": "no ```python block in reply"}
        row.update(idea=idea, **res)
        if code:
            (out / "code" / f"{row['id']}.py").write_text(code)
            row.update(sim_A=sim(code, "A"), sim_B=sim(code, "B"))
            d = row["sim_A"] - row["sim_B"]
            row["built_on"] = "A" if d > 0.15 else "B" if d < -0.15 else "neither"
    log.write(json.dumps(row) + "\n")
    log.flush()
    print(f"[{args.task} current={current} {kind}{' ' + method if method else ''}] {row['id']} "
          f"score={row.get('score')} built_on={row.get('built_on')} ${usd:.2f} | {row.get('idea', '')[:90]}", flush=True)
    return row


menu = "\n".join(f"{k}. {v}" for k, v in cfg["menu"].items())
for current in "AB":
    ctx = context(current)
    r = call(current, "rank", [{"role": "user", "content": ctx + f"\n\nMETHODS:\n{menu}\n\nRank these four methods by "
             "the validation score you expect from ONE reply that contains one complete program for this task, under "
             'the task\'s limits. Reply with JSON only: {"ranking": ["<letter>", "<letter>", "<letter>", "<letter>"], '
             '"reason": "<one sentence>"}'}])
    ranking = json.loads(re.search(r"\{.*\}", r["reply"], re.S).group(0))["ranking"]
    assert sorted(ranking) == list("ABCD"), f"bad ranking: {r['reply'][:300]}"
    print(f"[{args.task} current={current}] ranking {ranking}", flush=True)
    for _ in range(args.free):
        call(current, "free", [{"role": "system", "content": SYSTEM},
                               {"role": "user", "content": ctx + "\n\nWrite your next version."}])
    for kind, m in (("top", ranking[0]), ("runner_up", ranking[1])):
        call(current, kind, [{"role": "system", "content": SYSTEM}, {"role": "user", "content": ctx +
             f"\n\nUse this method for your next version: {cfg['menu'][m]}\nWrite your next version."}], method=m)
print(json.dumps({"calls": n, "usd": round(usd, 2)}))
