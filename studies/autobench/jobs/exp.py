# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Client of the experiment runner (the Modal app autobench).

  uv run exp.py submit <arm> <solve.py>     run one experiment on the 100 dev problems. Prints a summary and one
                                            line per problem; writes last_run.jsonl (each problem, the text your
                                            solve returned for it, whether it was right). On a crash it prints the
                                            end of the log and exits 1. Exits 3 when the budget is used. If this
                                            command is killed while it waits, the run goes on: run it again and it
                                            waits for that same run.
  uv run exp.py init <arm> <experiments>    operator: set the arm's number of experiments
  uv run exp.py ledger <arm>                the arm's experiments as the runner recorded them
  uv run exp.py final <label> <math400|hard328> <solve.py>     operator: score a solve.py on a final set
"""
import json
import sys
from pathlib import Path

import modal

ledger = modal.Dict.from_name("autobench-ledger", create_if_missing=True)


def call(name, *args):
    return modal.Function.from_name("autobench", name).remote(*args)


def summary(row):
    finish = row.get("finish", {})
    lines = [("right", row["right"]), ("problems", row["problems"]), ("generation_seconds", row.get("generation_seconds")),
             ("budget_seconds", row["budget_s"]), ("generated_tokens", row.get("generated_tokens")),
             ("tokens_per_problem", round(row["generated_tokens"] / row["problems"]) if row.get("generated_tokens") else None),
             ("requests", row.get("requests")), ("finished_stop", finish.get("stop")), ("finished_length", finish.get("length")),
             ("cut_by_time", finish.get("time")), ("total_seconds", row["wall_seconds"])]
    return "---\n" + "\n".join(f"{name + ':':<20}{value}" for name, value in lines)


def main():
    command, args = sys.argv[1], sys.argv[2:]
    if command == "submit":
        arm, path = args
        # The run is spawned, not awaited in one call, so it survives the death of this process: the call id is kept
        # in .pending_call, and the next `submit` waits for that run instead of starting another.
        pending = Path(".pending_call")
        if pending.exists():
            print("waiting for the run that was already submitted")
            run = modal.FunctionCall.from_id(pending.read_text().strip())
        else:
            run = modal.Function.from_name("autobench", "submit").spawn(arm, Path(path).read_text())
            pending.write_text(run.object_id)
        try:
            result = run.get()
        finally:
            pending.unlink()
        if result["exhausted"]:
            print(f"BUDGET EXHAUSTED: all {result['budget']} experiments of arm {arm} are used. The run is over: stop.")
            sys.exit(3)
        row = result["row"]
        print(f"experiment {row['n'] + 1} of {result['budget']}")
        if row["right"] is None:
            print(result["log"][-6000:])
            print("---\nCRASH: " + ("killed, the run exceeded its time limit" if row["timed_out"] else f"exit code {row['exit_code']}"))
            sys.exit(1)
        print(summary(row))
        for p in result["per_problem"]:
            print(f"problem {p['index']:>3} {'right' if p['right'] else 'wrong'}")
        Path("last_run.jsonl").write_text("".join(json.dumps(p) + "\n" for p in result["per_problem"]))
    elif command == "init":
        arm, experiments = args
        ledger[f"budget:{arm}"] = int(experiments)
    elif command == "ledger":
        (arm,) = args
        print(f"budget {ledger[f'budget:{arm}']}")
        for key, row in sorted(ledger.items()):
            if key.startswith(f"exp:{arm}:"):
                print(f"{row['n']:03d} {row['state']:<11} right {row.get('right')} tokens {row.get('generated_tokens')} "
                      f"wall {row.get('wall_seconds')} s exit {row.get('exit_code')} {row['solve_sha256'][:12]}")
    elif command == "final":
        label, set_name, path = args
        print(summary(call("score_final", label, set_name, Path(path).read_text())))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
