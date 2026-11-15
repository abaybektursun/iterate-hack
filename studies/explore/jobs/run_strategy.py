"""One strategy run on one task (laptop: the model is an API call, the scorer runs on the CPU).

    python -m studies.explore.jobs.run_strategy --task circles26 --strategy fnf --budget 24 --seed 0 \
        --model gpt-5.4-mini --out runs/explore/circles26/fnf-s0

Writes log.jsonl (one row per submission), code/<id>.py and metrics.json to --out. Refuses an existing --out.
"""
import argparse
import json
import pathlib
import subprocess
import sys

from studies.explore.lib.loop import Run, Task
from studies.explore.lib.strategies import STRATEGIES

ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True)
ap.add_argument("--strategy", required=True, choices=sorted(STRATEGIES))
ap.add_argument("--budget", type=int, required=True, help="submissions (model calls) for the whole run")
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--model", required=True)
ap.add_argument("--k", type=int, default=4)
ap.add_argument("--branch-steps", type=int, default=None,
                help="fnf arms: submissions per branch at each fork (default: 6 %% of the budget)")
ap.add_argument("--flushes", type=int, default=0, help="randflush: number of random flushes (match a basin run)")
ap.add_argument("--list-model", default=None, help="fnf_assign: model that lists the methods (default: --model)")
ap.add_argument("--out", required=True)
args = ap.parse_args()

out = pathlib.Path(args.out)
assert not out.exists(), f"{out} exists: a rerun gets a new folder"
task = Task(pathlib.Path(__file__).resolve().parents[1] / "tasks" / args.task)
run = Run(task, args.strategy, args.model, args.budget, out, seed=args.seed)
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
(out / "run.json").write_text(json.dumps({**vars(args), "commit": commit, "command": " ".join(sys.argv)}, indent=1))
STRATEGIES[args.strategy](run, k=args.k, seed=args.seed, flushes=args.flushes, list_model=args.list_model,
                          branch_steps=args.branch_steps)
print(json.dumps(run.close()))
