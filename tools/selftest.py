"""End-to-end test of board.py and msg.py against the test table (ITERATE_TEST=1: table iterate-board-test, S3
prefix test/). Run it after changing a tool:  python3 tools/selftest.py     It takes about a minute.

Each step runs the real command line as one of two agents (different session ids) and checks what it prints.
"""
import os
import subprocess
import sys
import time

TAG = f"selftest-{time.time_ns()}"


def run(agent, tool, *args, code=0, stdin=""):
    env = {**os.environ, "ITERATE_TEST": "1", "CLAUDE_CODE_SESSION_ID": f"{TAG}-{agent}"}
    done = subprocess.run(["uv", "run", "--quiet", f"tools/{tool}.py", *args], capture_output=True, text=True, env=env, input=stdin)
    assert done.returncode == code, f"{tool} {args} exited {done.returncode}, expected {code}:\n{done.stdout}{done.stderr}"
    return done.stdout.strip()


def check(condition, what):
    print(("ok    " if condition else "FAIL  ") + what)
    if not condition:
        sys.exit(1)


idea = run("a", "board", "post", "idea", f"{TAG} an idea")
check(idea.startswith("idea-"), "post prints the item id")
run("a", "board", "up", idea)
run("a", "board", "up", idea)
check(f"+1-0: {TAG} an idea" in run("a", "board", "ls", "idea", "--new", "--n", "5"), "voting twice counts once")
run("a", "board", "down", idea)
check(f"+0-1: {TAG} an idea" in run("a", "board", "ls", "idea", "--new", "--n", "5"), "a new vote replaces the old one")

posted = run("a", "board", "post", "work", f"{TAG} doing {idea}")
work_a = posted.splitlines()[0]
check("announced on all" in posted, "post work says it announced")
claim_b = run("b", "board", "post", "work", f"{TAG} also doing {idea}")
work_b = claim_b.splitlines()[0]
check(f"also claimed: {work_a}" in claim_b, "a second claim on the same idea is reported")
check("idle 0m" in run("a", "board", "ls", "work", "--new", "--n", "5"), "work items show idle minutes")
check(f"started {work_a}: {TAG} doing {idea}" in run("b", "msg", "read"), "post work announces the item on all")

run("b", "board", "comment", work_a, "status?")
shown = run("a", "board", "show", work_a)
check("status?" in shown and "(work, open)" in shown, "show prints the comment")
check(f"comment on your {work_a}: status?" in run("a", "msg", "read"), "a comment reaches the item's author as a message")
check(run("a", "msg", "read") == "", "a message is delivered once")
run("a", "board", "comment", idea, "x" * 281, code=1)

run("a", "msg", "send", "all", f"{TAG} hello")
check(f"{TAG} hello" in run("b", "msg", "read"), "a message on all reaches another agent")
check(f"{TAG} hello" not in run("a", "msg", "read"), "an agent does not receive its own message")
run("a", "msg", "send", idea, "thread note")
check("thread note" in run("b", "board", "show", idea), "show prints the item's message thread")
check(run("b", "msg", "wait", "--timeout", "2", code=1) == "", "wait exits with code 1 at the timeout")
waiter = subprocess.Popen(["uv", "run", "--quiet", "tools/msg.py", "wait", "--timeout", "30"], stdout=subprocess.PIPE, text=True,
                          env={**os.environ, "ITERATE_TEST": "1", "CLAUDE_CODE_SESSION_ID": f"{TAG}-b"})
time.sleep(3)
sent = time.time()
run("a", "msg", "send", "all", f"{TAG} wake")
out = waiter.communicate(timeout=30)[0]
check(f"{TAG} wake" in out, f"wait returns the message ({time.time() - sent:.1f} s after the send started)")
hook = run("a", "msg", "read", "--hook", stdin="{}")
check(hook == "", "the hook prints nothing when there is no new message")
run("b", "msg", "send", "all", f"{TAG} for the parent")
check(run("a", "msg", "read", "--hook", stdin='{"agent_id": "sub"}') == "", "the hook does nothing for a subagent's tool call")
check(f"{TAG} for the parent" in run("a", "msg", "read"), "the subagent's hook call leaves the message to its parent")
noreply = {**os.environ, "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "user.email", "GIT_CONFIG_VALUE_0": "82460915+someone@users.noreply.github.com"}
name = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, 'tools'); import team; print(team.who())"],
                      capture_output=True, text=True, env=noreply, check=True).stdout.strip()
check(name == "someone", "a GitHub noreply email gives the plain name")

result = [l for l in run("a", "board", "done", work_a, f"{TAG} result 0.41").splitlines() if l.startswith("result-")][0]
check(f"{TAG} result 0.41" in run("a", "board", "ls", "result", "--new", "--n", "5"), "done with a text posts the result")
check(f"done {work_a}, {result}: {TAG} result 0.41" in run("b", "msg", "read"), "done announces the item and its result on all")
check("base MATH-500 410/500 (82.0 %)" in run("a", "board", "score", result, "base", "MATH-500", "410/500", "cue", "--tokens", "3933"),
      "score attaches a score to a result")
run("a", "board", "score", result, "base", "MATH-500", "501/500", "cue", code=1)
bench = f"set{time.time_ns()}"  # a benchmark name no earlier run used
run("a", "board", "score", result, "base", bench, "1/328", "x")
check(f"{bench} 2/328" in run("a", "board", "score", result, "base", f"SET-{bench[3:]}", "2/328", "x"), "a benchmark keeps the spelling already used")
lined = run("a", "board", "post", "result", f"{TAG} cue at T 0.6\nscore: base MATH-500 378/500 tokens 4690 | cue, T 0.6")
check("score base MATH-500 378/500 (75.6 %)" in lined, "a score line in a result's text writes the score")
run("a", "board", "post", "result", f"{TAG} bad\nscore: base MATH-500 378 of 500", code=1)
check(f"{TAG} bad" not in run("a", "board", "ls", "result", "--new", "--n", "10"), "a bad score line stops the post")
run("a", "board", "score", work_b, "base", "MATH-500", "1/500", "cue", code=1)
run("b", "board", "done", work_b)
check(f"closed {work_b}: {TAG} also doing" in run("a", "msg", "read"), "done without a text announces the closed item")
check(work_a not in run("a", "board", "ls", "work", "--new"), "a closed work item leaves ls")
check("closed by" in run("a", "board", "show", work_a), "show says who closed it")
run("a", "board", "show", "idea-000000", code=1)
run("a", "msg", "send", "bad channel", "x", code=1)
print("all checks passed")
