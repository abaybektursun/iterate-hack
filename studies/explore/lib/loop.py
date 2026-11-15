"""The shared pieces of every exploration strategy: one LLM call, one scored submission, one log row.

A strategy (studies/explore/lib/strategies.py) only decides which chat history and which starting code each next
call gets. Everything else is here, so strategies differ in that decision alone:

- Session: a chat history (list of messages) plus the code it last submitted.
- propose(session): one chat call; the model returns an IDEA line and one full program in a ```python block.
- evaluate(task, code): runs the task's scorer on the program in a fresh temp folder with a time limit.
- Log: one JSONL row per submission (strategy, agent, parent, step, idea, score, tokens, time), plus the code file.

The model sees only validation scores. A task may define a held-out test score (scorer --test), which only the
analysis reads, as in AutoResearchExam (validation shown, hidden test scored).
"""
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

KEY_FILE = pathlib.Path.home() / ".config" / "openai" / "key"
PRICES = {"gpt-5.4-mini": (0.75, 4.5), "gpt-5.4-nano": (0.2, 1.25), "gpt-6.1-sol": (2.0, 10.0)}  # $/1M in, out; unverified


def chat(messages, model):
    """One OpenAI chat completion. Returns (text, usage). Retries only rate limits and server errors."""
    key = os.environ.get("OPENAI_API_KEY") or KEY_FILE.read_text().strip()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions",
                                 data=json.dumps({"model": model, "messages": messages}).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(5):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=300))
            return r["choices"][0]["message"]["content"], r.get("usage", {})
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503) or attempt == 4:
                raise RuntimeError(f"OpenAI HTTP {e.code}: {e.read()[:300]}")
            time.sleep(10 * (attempt + 1))
        except (socket.timeout, urllib.error.URLError, ConnectionError) as e:  # network: retry, then fail loudly
            if attempt == 4:
                raise RuntimeError(f"OpenAI network error after 5 tries: {e}")
            time.sleep(10 * (attempt + 1))


def cost(usage, model):
    pin, pout = PRICES[model]
    return usage.get("prompt_tokens", 0) / 1e6 * pin + usage.get("completion_tokens", 0) / 1e6 * pout


class Task:
    """A folder with spec.md (what to optimize), starter.py (a working weak program) and score.py.

    `python score.py <program.py> [--test]` prints one JSON line {"score": float, "valid": bool, "msg": str}.
    Higher is better. The program is run by score.py, which enforces the task's own time limit.
    """

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.name = self.path.name
        self.spec = (self.path / "spec.md").read_text()
        self.starter = (self.path / "starter.py").read_text()

    def evaluate(self, code, test=False, timeout=120):
        with tempfile.TemporaryDirectory() as d:
            prog = pathlib.Path(d) / "solution.py"
            prog.write_text(code)
            cmd = [sys.executable, str(self.path / "score.py"), str(prog)] + (["--test"] if test else [])
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=d)
            except subprocess.TimeoutExpired:
                return {"score": None, "valid": False, "msg": f"scorer timed out after {timeout} s"}
            lines = [l for l in r.stdout.strip().splitlines() if l.startswith("{")]
            if r.returncode != 0 or not lines:
                return {"score": None, "valid": False, "msg": (r.stderr or r.stdout)[-800:]}
            return json.loads(lines[-1])


SYSTEM = """You are a research engineer improving a program for the task below. Each turn, reply with:
IDEA: <one sentence naming the approach of this version and what changed>
```python
<the complete program>
```
You will get its validation score. Try to reach the highest score you can within your budget of submissions."""


def first_message(task, code, note=""):
    return (f"TASK:\n{task.spec}\n\nCURRENT PROGRAM:\n```python\n{code}\n```\n{note}"
            "Write your next version.")


def parse(text):
    idea = re.search(r"IDEA:\s*(.+)", text)
    code = re.findall(r"```python\n(.*?)```", text, re.S)
    return (idea.group(1).strip() if idea else ""), (code[-1] if code else None)


class Run:
    """One strategy run on one task: the log, the archive of submissions, the budget in submissions."""

    def __init__(self, task, strategy, model, budget, out, seed=0):
        self.task, self.strategy, self.model, self.budget, self.seed = task, strategy, model, budget, seed
        self.out = pathlib.Path(out)
        (self.out / "code").mkdir(parents=True, exist_ok=True)
        self.archive = []  # every submission row, in order
        self.spent = {"prompt_tokens": 0, "completion_tokens": 0, "usd": 0.0}
        self.log = open(self.out / "log.jsonl", "a")

    def left(self):
        return self.budget - len(self.archive)

    def best(self, rows=None):
        ok = [r for r in (rows or self.archive) if r["valid"] and r["score"] is not None]
        return max(ok, key=lambda r: r["score"]) if ok else None

    def step(self, session, agent, parent, branch=""):
        """One model call and one scored submission. `session` is a list of chat messages, extended in place."""
        text, usage = chat([{"role": "system", "content": SYSTEM}] + session, self.model)
        for k in ("prompt_tokens", "completion_tokens"):
            self.spent[k] += usage.get(k, 0)
        self.spent["usd"] += cost(usage, self.model)
        idea, code = parse(text)
        session.append({"role": "assistant", "content": text})
        res = self.task.evaluate(code) if code else {"score": None, "valid": False, "msg": "no ```python block in reply"}
        n = len(self.archive)
        row = {"id": f"s{n:04d}", "strategy": self.strategy, "task": self.task.name, "seed": self.seed, "agent": agent,
               "branch": branch, "parent": parent, "step": n, "idea": idea, **res,
               "context_messages": len(session), "prompt_tokens": usage.get("prompt_tokens", 0),
               "completion_tokens": usage.get("completion_tokens", 0), "at": time.time()}
        if code:
            (self.out / "code" / f"{row['id']}.py").write_text(code)
        self.archive.append({**row, "code": code})
        self.log.write(json.dumps(row) + "\n")
        self.log.flush()
        best = self.best()
        session.append({"role": "user", "content": (
            f"Validation score: {res['score']} ({'valid' if res['valid'] else 'INVALID'}). {res['msg'][:600]}\n"
            f"Best so far: {best['score'] if best else None}. Submissions left: {self.left()}. Write your next version.")})
        print(f"[{self.strategy} {agent}{branch}] {row['id']} score={res['score']} best={best and best['score']} "
              f"ctx={len(session)} ${self.spent['usd']:.3f} | {idea[:80]}", flush=True)
        return self.archive[-1]

    def close(self):
        b = self.best()
        test = self.task.evaluate(b["code"], test=True) if b else None
        summary = {"strategy": self.strategy, "task": self.task.name, "seed": self.seed, "model": self.model,
                   "budget": self.budget, "n": len(self.archive), "best_val": b and b["score"], "best_id": b and b["id"],
                   "best_test": test and test["score"], "spent": self.spent,
                   "valid_share": sum(r["valid"] for r in self.archive) / max(1, len(self.archive))}
        (self.out / "metrics.json").write_text(json.dumps(summary, indent=1))
        self.log.close()
        return summary
