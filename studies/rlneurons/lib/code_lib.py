"""Code pair (specs/SPEC_code1.md): prompt, answer extraction and the execution grader for HumanEval+ and MBPP+.

The prompt is the chat template of allenai/Olmo-3.1-7B-RL-Zero-Code (raw text, no role tokens). The answer is the last fenced block
of the completion, or the whole completion when it has none (AI2's CodeVerifier.extract_python_code rule). A problem is right when
its program (the answer followed by the benchmark's tests) exits 0 within the time limit. run() executes model-written code: call it
only inside a job's container, never on the laptop."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile

TEMPLATE = ("Solve the following code problem step by step. The last part of your response should be the solution to the problem in "
            "form ```\npython\nCODE\n``` where CODE is the solution for the problem.\n\n{content}\n\nRemember to put your solution "
            "inside the ```\npython\nCODE\n``` tags")
BLOCK = re.compile(r"```[ \t]*\n?[ \t]*(?:python|py|Python)?[ \t]*\n(.*?)```", re.DOTALL)
WRONG = "def {entry}(*args, **kwargs):\n    return None\n"         # the planted wrong program of the grader check


def problem(name: str, row: dict) -> dict:
    """One benchmark row as {uid, content (what the template wraps), entry, pre (code before the answer), post (the tests),
    reference (a program that must pass)}."""
    if name == "humanevalplus":
        entry = row["entry_point"]
        return {"uid": row["task_id"], "entry": entry, "pre": row["prompt"] + "\n",
                "content": f"Write the complete Python function `{entry}` for this signature and docstring:\n\n{row['prompt']}",
                "post": f"\n{row['test']}\ncheck({entry})\n", "reference": row["prompt"] + row["canonical_solution"]}
    entry = re.findall(r"assertion\((\w+)\(\*inp\)", row["test"])[-1]         # the function the tests call
    return {"uid": f"Mbpp/{row['task_id']}", "entry": entry, "pre": "",
            "content": f"{row['prompt']}\nYour code should pass this test:\n{row['test_list'][0]}",
            "post": "\n" + "\n".join(row["test_imports"]) + "\n" + row["test"] + "\n", "reference": row["code"]}


def extract(text: str) -> tuple:
    """(mode, code): mode "block" = the last fenced block, "none" = no closed block, the whole text."""
    blocks = BLOCK.findall(text)
    return ("block", blocks[-1]) if blocks else ("none", text)


def program(p: dict, code: str) -> str:
    return p["pre"] + code + p["post"]


def run(src: str, timeout_s: float) -> dict:
    """Run one program in its own interpreter and empty directory. passed = exit code 0 within the time limit."""
    with tempfile.TemporaryDirectory() as d:
        with open(d + "/prog.py", "w") as f:        # a file, not -c: the tests reach 790,000 characters
            f.write(src)
        try:
            r = subprocess.run([sys.executable, "prog.py"], cwd=d, capture_output=True, text=True, timeout=timeout_s, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:       # a time-out is a graded outcome (wrong), not an error of the grader
            return {"passed": False, "exit": "timeout", "stderr_tail": ""}
    return {"passed": r.returncode == 0, "exit": r.returncode, "stderr_tail": r.stderr[-400:]}
