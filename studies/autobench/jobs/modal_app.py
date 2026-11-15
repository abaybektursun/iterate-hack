"""The experiment runner of the autobench study, one Modal app in your own workspace. Deploy once:

    modal deploy studies/autobench/jobs/modal_app.py

  submit(arm, source)             CPU. Claims the arm's next experiment number in the ledger (refuses when the arm's
                                  budget is used), runs solve.py on the 100 dev problems through solve_job, grades
                                  the returned texts, stores everything in the Volume autobench-runs.
  solve_job(source, problems, s)  H100. Runs lib/harness.py on one solve.py with a generation budget of s seconds.
                                  It receives problem texts only: no answer is in its image or its arguments. The
                                  weights Volume is read-only, the network is blocked, Modal is not reachable, the
                                  container is used once.
  score_final(label, set, source) CPU. The same on math400 or hard328, for the operator, after the arm has ended.

The engine is the rlneurons study's: the image runs studies/rlneurons/jobs/setup_vllm.sh as infra/runner.py does
(vLLM 0.32.0 in /opt/rln-vllm), and the weights come from your Volume iterate-hf-cache at the revisions of
frozen4.json. It is its own app, not tools/gpu.py, because a gpu.py job contains the whole repository, answers
included, and runs only commits of this repository, while the baseline agent works outside it.
"""
import hashlib
import json
import os
import re
import signal
import subprocess
import tempfile
import time
from pathlib import Path

import modal

STUDY = Path(__file__).resolve().parent.parent
RLN = STUDY.parent / "rlneurons"
PY = "/opt/rln-vllm/bin/python"
DEV_SECONDS = 360                                      # generation budget of one experiment (100 problems)
FINAL_SECONDS = {"math400": 1440, "hard328": 2362}     # the same 3.6 s per problem; twice that on the harder set
LOAD_LIMIT = 900                                       # seconds allowed on top of the budget, for the engine start
ARM = re.compile(r"[a-z][a-z0-9-]{0,30}")

engine_image = (
    modal.Image.debian_slim(python_version="3.12")
    .add_local_file(str(RLN / "jobs/setup_vllm.sh"), "/setup_vllm.sh", copy=True)
    .run_commands("bash /setup_vllm.sh")
    .env({"HF_HOME": "/hf", "HF_HUB_OFFLINE": "1", "PYTHONUNBUFFERED": "1", "PYTHONPATH": "/repo"})
    .add_local_dir(str(RLN / "lib"), "/repo/studies/rlneurons/lib", copy=True, ignore=["__pycache__"])
    .add_local_file(str(RLN / "jobs/rln4_gen.py"), "/repo/studies/rlneurons/jobs/rln4_gen.py", copy=True)
    .add_local_file(str(RLN / "data/rln4/frozen4.json"), "/repo/studies/rlneurons/data/rln4/frozen4.json", copy=True)
    .add_local_file(str(STUDY / "lib/harness.py"), "/trusted/harness.py", copy=True)
)
grader_image = (   # the engine image plus the problem sets with their answers and the grader: never given a GPU
    engine_image
    .add_local_dir(str(RLN / "data/rln3"), "/repo/studies/rlneurons/data/rln3", copy=True)
    .add_local_dir(str(RLN / "data/rln4"), "/repo/studies/rlneurons/data/rln4", copy=True)
    .add_local_file(str(RLN / "results/rln3/rln3_overlap.json"), "/repo/studies/rlneurons/results/rln3/rln3_overlap.json", copy=True)
    .add_local_file(str(RLN / "jobs/run_cell.py"), "/repo/studies/rlneurons/jobs/run_cell.py", copy=True)
    .add_local_file(str(STUDY / "data/dev100-v1.json"), "/trusted/dev100-v1.json", copy=True)
    .add_local_file(str(STUDY / "lib/grade.py"), "/trusted/grade.py", copy=True)
)
weights = modal.Volume.from_name("iterate-hf-cache")
runs = modal.Volume.from_name("autobench-runs", create_if_missing=True)
ledger = modal.Dict.from_name("autobench-ledger", create_if_missing=True)

app = modal.App("autobench")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@app.function(image=engine_image, gpu="H100", volumes={"/hf": weights.read_only()}, timeout=FINAL_SECONDS["hard328"] + LOAD_LIMIT + 300,
              retries=0, block_network=True, restrict_modal_access=True, single_use_containers=True, max_containers=4)
def solve_job(source: str, problems: list, budget_s: int):
    work = Path(tempfile.mkdtemp())
    (work / "solve.py").write_text(source)
    (work / "in.json").write_text(json.dumps({"problems": problems, "budget_s": budget_s}))
    out = Path(tempfile.mkdtemp()) / "out.json"
    start = time.time()
    with open(work / "log", "w") as log:
        proc = subprocess.Popen([PY, "/trusted/harness.py"], cwd=work, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                                env={**os.environ, "AUTOBENCH_IN": str(work / "in.json"), "AUTOBENCH_OUT": str(out)})
        try:
            proc.wait(timeout=budget_s + LOAD_LIMIT)
            timed_out = False
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            timed_out = True
    return {"exit_code": proc.returncode, "timed_out": timed_out, "wall_seconds": round(time.time() - start, 1),
            "log": (work / "log").read_text(errors="replace")[-200_000:], "record": json.loads(out.read_text()) if out.exists() else None}


def grade_py(*args):
    return json.loads(subprocess.run([PY, "/trusted/grade.py", *args], capture_output=True, text=True, check=True).stdout)


def claim(prefix, limit, source):
    """Take the first free number under prefix, atomically; None when all `limit` numbers are taken."""
    for n in range(limit):
        row = {"n": n, "state": "running", "claimed_at": now(), "solve_sha256": hashlib.sha256(source.encode()).hexdigest()}
        if ledger.put(f"{prefix}:{n:03d}", row, skip_if_exists=True):
            return n
    return None


def run_and_grade(key, folder, source, set_name, budget_s):
    """Run a claimed experiment and grade it; store its files in the Volume and its row in the ledger.
    Returns the ledger row, one row per problem (problem, returned text, right; no answer) and the log."""
    row = ledger[key]
    problems = grade_py("problems", set_name)
    try:
        result = solve_job.remote(source, problems, budget_s)
    except Exception as error:
        ledger[key] = {**row, "state": "infra_error", "error": repr(error), "ended_at": now()}
        raise
    record, log = result.pop("record"), result.pop("log")
    out = Path("/runs") / folder
    out.mkdir(parents=True)
    (out / "solve.py").write_text(source)
    (out / "log").write_text(log)
    row = {**row, **result, "state": "done", "ended_at": now(), "set": set_name, "problems": len(problems), "budget_s": budget_s,
           "right": None, "folder": folder}
    per_problem = []
    if result["exit_code"] == 0 and record is not None:
        answers = dict((int(k), v) for k, v in record.pop("answers"))
        (out / "answers.json").write_text(json.dumps(sorted(answers.items())))
        graded = grade_py("grade", set_name, str(out / "answers.json"))
        (out / "graded.json").write_text(json.dumps(graded))
        row.update(record, right=sum(g["right"] for g in graded))
        text = {p["index"]: p["problem"] for p in problems}
        per_problem = [{"index": g["index"], "right": g["right"], "extracted": g["extracted"], "problem": text[g["index"]],
                        "answer": answers.get(g["index"])} for g in graded]
    (out / "row.json").write_text(json.dumps(row, indent=1))
    runs.commit()
    ledger[key] = row
    return row, per_problem, log


@app.function(image=grader_image, volumes={"/runs": runs}, timeout=3 * 3600)
def submit(arm: str, source: str):
    if not ARM.fullmatch(arm):
        raise ValueError(f"arm name {arm!r}")
    budget = ledger[f"budget:{arm}"]   # KeyError: the operator has not run `exp.py init <arm> <experiments>`
    n = claim(f"exp:{arm}", budget, source)
    if n is None:
        return {"exhausted": True, "budget": budget}
    row, per_problem, log = run_and_grade(f"exp:{arm}:{n:03d}", f"{arm}/{n:03d}", source, "dev100", DEV_SECONDS)
    return {"exhausted": False, "budget": budget, "row": row, "per_problem": per_problem, "log": log}


@app.function(image=grader_image, volumes={"/runs": runs}, timeout=3 * 3600)
def score_final(label: str, set_name: str, source: str):
    if not ARM.fullmatch(label):
        raise ValueError(f"label {label!r}")
    n = claim(f"final:{set_name}:{label}", 100, source)
    row, _, _ = run_and_grade(f"final:{set_name}:{label}:{n:03d}", f"final/{set_name}-{label}-{n:03d}", source, set_name,
                              FINAL_SECONDS[set_name])
    return row
