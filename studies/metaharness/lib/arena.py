"""Arenas for the planted-waste test (specs/SPEC2.md): one private copy of the repository per review run, with its
own board, its own job records and its own git remote, so that a reviewing agent sees one stream of work and nothing
of this study.

An arena is
  $MH_HOME/arenas/<id>/repo        a git repository with one root commit: the tree of the base commit, without
                                   studies/metaharness, plus the study gapmap (prep/arena_template), on the branch
                                   dana/gapmap; the plain arm also loses the team-meta-review skill, tools/cycle.py
                                   and meta/
  $MH_HOME/arenas/<id>/origin.git  its remote (bare, local), so `gpu.py submit` finds the commit pushed
  a moto server on 127.0.0.1:<port> holding the table iterate-board-test and the team bucket (board, messages, events)
  the Modal environment mh-<id> of the person's workspace, with the runner deployed (jobs, logs, outputs)
  $MH_HOME/state/<id>/             what this study records about the arena; the reviewing agent never sees it

MH_HOME must be set and must be outside every arena's repository.
"""
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STUDY = ROOT / "studies" / "metaharness"
TEMPLATE = STUDY / "prep" / "arena_template"
HOME = Path(os.environ["MH_HOME"])
BRANCH = "dana/gapmap"
BUCKET = "iterate-hack-team-769063704696"
MODEL = "claude-opus-5-5"
PROMPTS = {
    "skill": "Run the team-meta-review skill.",
    "plain": "Review how the last hour of work went and make one improvement.",
}


def state_dir(arena_id):
    return HOME / "state" / arena_id


def load(arena_id):
    return json.loads((state_dir(arena_id) / "arena.json").read_text())


def repo(arena_id):
    return HOME / "arenas" / arena_id / "repo"


def env(arena, session=None):
    """The environment of every command run inside an arena. Claude Code's own variables are dropped, so a tool run
    by this study is not recorded as a child of the session that runs the study."""
    e = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE") and k not in ("AI_AGENT", "MH_HOME", "PYTHONPATH")}
    endpoint = f"http://127.0.0.1:{arena['port']}"
    e.update(ITERATE_TEST="1", AWS_ENDPOINT_URL_DYNAMODB=endpoint, AWS_ENDPOINT_URL_S3=endpoint,
             MODAL_ENVIRONMENT=arena["modal_env"])
    if session:
        e["CLAUDE_CODE_SESSION_ID"] = session
    return e


def sh(args, cwd, e, check=True, timeout=None):
    done = subprocess.run(args, cwd=cwd, env=e, capture_output=True, text=True, timeout=timeout)
    if check and done.returncode != 0:
        raise RuntimeError(f"{args} exited {done.returncode}:\n{done.stdout}\n{done.stderr}")
    return done


def git(arena_id, *args, check=True):
    return sh(["git", *args], repo(arena_id), {**os.environ}, check=check).stdout.strip()


# ---------------------------------------------------------------- build

def strip_review_harness(tree):
    """The plain arm: no skill, no cycle.py, no earlier entries, and no text that names them."""
    shutil.rmtree(tree / ".claude" / "skills" / "team-meta-review")
    shutil.rmtree(tree / "meta")
    (tree / "tools" / "cycle.py").unlink()
    named = re.compile(r"meta-review|cycle\.py|\bmeta/")
    cuts = {
        "AGENTS.md": [(r"\n8\. Run the `team-meta-review` skill.*?(?=\n\n)", "")],
        "README.md": [(r"\nuv run tools/cycle\.py --hours 24[^\n]*", ""),
                      (r"\n`cycle\.py` is what the team-meta-review skill.*?(?=\n\n)", "")],
        "tools/gpu.py": [(r"  # tools/cycle\.py matches jobs to work items by branch", ""),
                         (r"\n    if sum\(key\.startswith\(\"job:\"\) for key in jobs\.keys\(\)\) % 5 == 0:\n        print\([^\n]*\)", "")],
        "tools/board.py": [(r"; tools/cycle\.py does\)", ")"),
                           (r"\n[^\n]*print\(\"A result closed: run the team-meta-review skill[^\n]*\)", "")],
        ".claude/settings.json": [(r" && m=\$\(git log -1 --format=%cr -- meta/\) && echo \\\"Newest team-meta-review entry \(meta/\): \$\{m:-none\}\\\"", "")],
    }
    for name, edits in cuts.items():
        text = (tree / name).read_text()
        for pattern, replacement in edits:
            text, n = re.subn(pattern, replacement, text, flags=re.S)
            assert n == 1, f"{name}: {pattern!r} matched {n} times; update strip_review_harness"
        (tree / name).write_text(text)
    json.loads((tree / ".claude" / "settings.json").read_text())
    for path in [tree / "AGENTS.md", tree / "README.md", tree / ".claude" / "settings.json", *sorted((tree / "tools").glob("*.py"))]:
        assert not named.search(path.read_text()), f"{path} still names the review harness"
    subprocess.run(["python3", "-m", "py_compile", str(tree / "tools" / "gpu.py"), str(tree / "tools" / "board.py")], check=True)


def patch_gpu_state(tree):
    """Both arms: tools/gpu.py state() reports a job as died when Modal's API call itself fails ("died: ConnectionError:
    Deadline exceeded", seen on the first pilot window while the job was running). In the arenas it asks again, so a
    transient API error is not shown to the worker or the reviewer as a failed job."""
    path = tree / "tools" / "gpu.py"
    text = path.read_text()
    old = """    try:
        modal.FunctionCall.from_id(r["call"]).get(timeout=0)
    except TimeoutError:
        return "running" if "start" in r else "queued"
    except Exception as e:  # the container died without writing its end record; the error says how
        return f"died: {type(e).__name__}: {str(e)[:120]}"
    return "done"
"""
    new = """    for attempt in range(6):
        try:
            modal.FunctionCall.from_id(r["call"]).get(timeout=0)
        except TimeoutError:
            return "running" if "start" in r else "queued"
        except Exception as e:  # the container died without writing its end record; the error says how
            if type(e).__name__ == "ConnectionError" and attempt < 5:  # Modal's API did not answer: ask again
                time.sleep(5)
                continue
            return f"died: {type(e).__name__}: {str(e)[:120]}"
        return "done"
"""
    assert old in text, "tools/gpu.py state() changed: update patch_gpu_state"
    path.write_text(text.replace(old, new))


def build(arena_id, arm, variant, port, base_sha):
    assert arm in PROMPTS and variant in ("planted", "clean")
    home = HOME / "arenas" / arena_id
    assert not home.exists(), f"{home} exists: an arena is never rebuilt in place"
    tree = home / "repo"
    tree.mkdir(parents=True)
    archive = subprocess.run(["git", "archive", "--format=tar", base_sha], cwd=ROOT, capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(tree)], input=archive, check=True)
    shutil.rmtree(tree / "studies" / "metaharness")
    study = tree / "studies" / "gapmap"
    shutil.copytree(TEMPLATE / "planted" / "gapmap", study)
    if variant == "clean":
        shutil.copytree(TEMPLATE / "clean" / "gapmap", study, dirs_exist_ok=True)
        (study / "jobs" / "bench_rng.py").unlink()
    shutil.rmtree(study / "cells")
    overall = STUDY / "data" / "gapmap_overall_v1"
    shutil.copytree(overall, study / "results" / "overall-01")
    lines = []
    for metric, table in json.loads((overall / "metrics.json").read_text())["metrics"].items():
        row = table[0]
        lines.append(f"  - `{metric}`: {row['t2_minus_t1']} [{row['low']}, {row['high']}]")
    readme = study / "README.md"
    readme.write_text(readme.read_text().replace("OVERALL_LINES", "\n".join(lines)))
    if arm == "plain":
        strip_review_harness(tree)
    patch_gpu_state(tree)

    def g(*args):
        subprocess.run(["git", *args], cwd=tree, check=True, capture_output=True)

    g("init", "-b", "main")
    g("config", "user.name", "Dana")
    g("config", "user.email", "dana@iterate.test")
    g("add", "-A")
    g("commit", "-m", "iterate-hack with the gapmap study: where the RL model still differs from the cued base on MATH-500")
    g("switch", "-c", BRANCH)
    subprocess.run(["git", "init", "--bare", "-b", "main", str(home / "origin.git")], check=True, capture_output=True)
    g("remote", "add", "origin", str(home / "origin.git"))
    g("push", "-u", "origin", "main")
    g("push", "-u", "origin", BRANCH)

    arena = {"id": arena_id, "arm": arm, "variant": variant, "port": port, "modal_env": f"mh-{arena_id}",
             "base_sha": base_sha, "built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    state_dir(arena_id).mkdir(parents=True)
    (state_dir(arena_id) / "arena.json").write_text(json.dumps(arena, indent=1))
    start_store(arena)
    start_modal(arena)
    return arena


def start_store(arena):
    """A moto server for this arena, with the board table (keys and indexes as tools/board.py uses them) and the bucket."""
    log = open(state_dir(arena["id"]) / "moto.log", "w")
    server = subprocess.Popen(["uv", "run", "--quiet", "--with", "moto[server]", "moto_server", "-H", "127.0.0.1", "-p", str(arena["port"])],
                              stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    (state_dir(arena["id"]) / "moto.pid").write_text(str(server.pid))
    code = """
import boto3, time, sys
for attempt in range(60):
    try:
        s = boto3.Session(profile_name='iterate-ecr', region_name='us-east-1')
        d = s.client('dynamodb')
        d.create_table(TableName='iterate-board-test', BillingMode='PAY_PER_REQUEST',
            AttributeDefinitions=[{'AttributeName': n, 'AttributeType': t} for n, t in (('pk', 'S'), ('sk', 'S'), ('listed', 'S'), ('at_ns', 'N'), ('score', 'N'))],
            KeySchema=[{'AttributeName': 'pk', 'KeyType': 'HASH'}, {'AttributeName': 'sk', 'KeyType': 'RANGE'}],
            GlobalSecondaryIndexes=[{'IndexName': i, 'KeySchema': [{'AttributeName': 'listed', 'KeyType': 'HASH'}, {'AttributeName': r, 'KeyType': 'RANGE'}],
                                     'Projection': {'ProjectionType': 'ALL'}} for i, r in (('new', 'at_ns'), ('top', 'score'))])
        s.client('s3').create_bucket(Bucket=sys.argv[1])
        break
    except Exception as error:
        last = error
        time.sleep(1)
else:
    raise last
"""
    sh(["uv", "run", "--quiet", "--with", "boto3", "python", "-c", code, BUCKET], ROOT, env(arena))


def start_modal(arena):
    e = env(arena)
    name = arena["modal_env"]
    sh(["modal", "environment", "create", name], ROOT, e, check=False)
    sh(["modal", "secret", "create", "hf-token", "HF_TOKEN=unused", "--env", name, "--force"], ROOT, e)
    sh(["modal", "deploy", "infra/runner.py"], repo(arena["id"]), e)


# ---------------------------------------------------------------- records

DUMP = """
import json, sys, modal
since, until = float(sys.argv[1]), float(sys.argv[2])
records = {}
for key, value in modal.Dict.from_name("iterate-jobs", create_if_missing=True).items():
    kind, job_id = key.split(":", 1)
    records.setdefault(job_id, {"id": job_id})[kind] = value
runs = modal.Volume.from_name("iterate-runs", create_if_missing=True)
out = []
for r in sorted(records.values(), key=lambda r: r.get("job", {}).get("at", 0)):
    if "job" not in r or not since <= r["job"]["at"] <= until:
        continue
    for name in ("log", "metrics.json"):
        try:
            r[name] = b"".join(runs.read_file(f"{r['id']}/{name}")).decode(errors="replace")
        except FileNotFoundError:
            r[name] = None
    out.append(r)
json.dump(out, sys.stdout)
"""


def dump_jobs(arena, since, until):
    """Every job of the arena's Modal environment submitted in [since, until]: its records, its log and its metrics.json."""
    for attempt in range(4):  # Modal's API or the machine can stall for minutes; the records do not change, so ask again
        try:
            done = sh(["uv", "run", "--quiet", "--with", "modal", "python", "-c", DUMP, str(since), str(until)], ROOT, env(arena), timeout=300)
            return json.loads(done.stdout)
        except (subprocess.TimeoutExpired, RuntimeError) as error:
            last = error
            time.sleep(15)
    raise last


def dump_board(arena):
    code = """
import boto3, json, sys
t = boto3.Session(profile_name='iterate-ecr', region_name='us-east-1').resource('dynamodb').Table('iterate-board-test')
rows, page = [], t.scan()
while True:
    rows += page['Items']
    if 'LastEvaluatedKey' not in page:
        break
    page = t.scan(ExclusiveStartKey=page['LastEvaluatedKey'])
json.dump(rows, sys.stdout, default=str)
"""
    return json.loads(sh(["uv", "run", "--quiet", "--with", "boto3", "python", "-c", code], ROOT, env(arena)).stdout)
