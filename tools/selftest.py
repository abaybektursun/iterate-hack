"""End-to-end test of board.py and msg.py against the test table (ITERATE_TEST=1: table iterate-board-test, S3
prefix test/). Run it after changing a tool:  python3 tools/selftest.py     It takes about a minute.

Each step runs the real command line as one of two agents (different session ids) and checks what it prints.
"""
import os
import subprocess
import sys
import time

TAG = f"selftest-{time.time_ns()}"


def run(agent, tool, *args, code=0):
    env = {**os.environ, "ITERATE_TEST": "1", "CLAUDE_CODE_SESSION_ID": f"{TAG}-{agent}"}
    done = subprocess.run(["uv", "run", "--quiet", f"tools/{tool}.py", *args], capture_output=True, text=True, env=env)
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
check(f"{idea}  +1 -0" in run("a", "board", "ls", "idea", "--new", "--n", "5"), "voting twice counts once")
run("a", "board", "down", idea)
check(f"{idea}  +0 -1" in run("a", "board", "ls", "idea", "--new", "--n", "5"), "a new vote replaces the old one")

work_a = run("a", "board", "post", "work", f"{TAG} doing {idea}").splitlines()[0]
claim_b = run("b", "board", "post", "work", f"{TAG} also doing {idea}")
work_b = claim_b.splitlines()[0]
check(f"also claimed: {work_a}" in claim_b, "a second claim on the same idea is reported")
check("idle 0m" in run("a", "board", "ls", "work", "--new", "--n", "5"), "work items show idle minutes")

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
hook = run("a", "msg", "read", "--hook")
check(hook == "", "the hook prints nothing when there is no new message")

run("a", "board", "done", work_a)
run("b", "board", "done", work_b)
check(work_a not in run("a", "board", "ls", "work", "--new"), "a closed work item leaves ls")
check("closed by" in run("a", "board", "show", work_a), "show says who closed it")
run("a", "board", "show", "idea-000000", code=1)
run("a", "msg", "send", "bad channel", "x", code=1)
print("all checks passed")
