# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Client of the autobench runner (jobs/modal_app.py, deployed in your Modal workspace).

For the agents of an arm:
  uv run studies/autobench/jobs/run_exp.py submit <arm> <train.py>   run one experiment; prints the training log,
                                                                      as `uv run train.py` does in Karpathy's setup
For the operator:
  uv run studies/autobench/jobs/run_exp.py prep                 data, tokenizer and attention kernel into the Volume
  uv run studies/autobench/jobs/run_exp.py init <arm> <budget>  set the arm's number of experiments
  uv run studies/autobench/jobs/run_exp.py ledger <arm>         the arm's experiments as recorded by the runner
  uv run studies/autobench/jobs/run_exp.py holdout              download the holdout shard (after both arms ended)
  uv run studies/autobench/jobs/run_exp.py final <label> <train.py>   score a train.py on val and on the holdout

Exit code of submit: the training script's own; 124 when it was killed at 600 s; 3 when the budget is used.
"""
import sys
from pathlib import Path

import modal

ledger = modal.Dict.from_name("autobench-ledger", create_if_missing=True)


def call(name, *args):
    return modal.Function.from_name("autobench", name).remote(*args)


def rows(prefix):
    """The ledger rows under a prefix (exp:<arm> or final:<label>), in order of experiment number."""
    return [value for key, value in sorted(ledger.items()) if key.startswith(prefix + ":")]


def main():
    command, args = sys.argv[1], sys.argv[2:]
    if command == "submit":
        arm, path = args
        result = call("submit", arm, Path(path).read_text())
        if result["exhausted"]:
            print(f"BUDGET EXHAUSTED: all {result['budget']} experiments of arm {arm} are used. The run is over: stop.")
            sys.exit(3)
        print(result["log"])
        if result["timed_out"]:
            print("autobench: killed at 600 s")
            sys.exit(124)
        sys.exit(result["exit_code"])
    elif command == "prep":
        print(call("prep"))
        print(call("warm"))
    elif command == "init":
        arm, budget = args
        ledger[f"budget:{arm}"] = int(budget)
    elif command == "ledger":
        (arm,) = args
        print(f"budget {ledger[f'budget:{arm}']}")
        for row in rows(f"exp:{arm}"):
            val = "-" if row.get("val_bpb") is None else f"{row['val_bpb']:.6f}"
            print(f"{row['n']:03d} {row['state']:<11} val_bpb {val} wall {row.get('wall_seconds', '-')} s "
                  f"exit {row.get('exit_code', '-')} evals {row.get('n_evals', '-')} {row['train_sha256'][:12]}")
    elif command == "holdout":
        print(call("prep_holdout"))
    elif command == "final":
        label, path = args
        print(call("score_final", label, Path(path).read_text()))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
