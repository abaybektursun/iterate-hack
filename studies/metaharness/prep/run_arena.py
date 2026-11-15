"""One arena from its first window to its last: build, then window, score, review, window, ... (SPEC2 "Review runs").

  MH_HOME=<dir> python3 -m studies.metaharness.prep.run_arena <arena id> <skill|plain> <planted|clean> <port> <base commit> <windows, e.g. 0,1,2,3>

Window k runs batch k (prep/worker.py BATCHES). A review follows every window but the last. Each step runs as its own
process and a step that fails stops the arena.
"""
import json
import subprocess
import sys

from studies.metaharness.grader import score_window
from studies.metaharness.lib import arena as A

arena_id, arm, variant, port, base, windows = sys.argv[1:7]
windows = [int(w) for w in windows.split(",")]


def step(*module_args):
    subprocess.run([sys.executable, "-m", *module_args], check=True)


step("studies.metaharness.prep.build", arena_id, arm, variant, port, base)
for position, window in enumerate(windows):
    step("studies.metaharness.prep.worker", arena_id, str(window))
    folder = A.state_dir(arena_id) / f"window{window}"
    score = score_window.score_dir(folder)
    (folder / "score.json").write_text(json.dumps(score, indent=1))
    print(f"[{arena_id}] window {window}: waste share {score['waste_share']}, {score['container_minutes']} container min, "
          f"present {[p for p, on in score['present'].items() if on]}, answers {score['answers']}", flush=True)
    if position < len(windows) - 1:
        step("studies.metaharness.prep.review", arena_id, str(position + 1))
print(f"[{arena_id}] finished", flush=True)
