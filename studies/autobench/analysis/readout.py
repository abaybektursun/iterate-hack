# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Read the runner's ledger and write the run folder of an arm, then print the readout.

    uv run studies/autobench/analysis/readout.py <nn> <arm> [<final label> ...]     e.g.  01 karpathy karpathy swarm-cue start

Writes studies/autobench/results/math500-loop/<arm>-<nn>/metrics.json (every experiment as the runner recorded
it, the best `right` of 100 after each experiment, GPU seconds, the finals under the given labels) and run.json.
"""
import json
import subprocess
import sys
from pathlib import Path

import modal

RESULTS = Path(__file__).resolve().parent.parent / "results" / "math500-loop"
ledger = modal.Dict.from_name("autobench-ledger")


def main():
    nn, arm, labels = sys.argv[1], sys.argv[2], sys.argv[3:]
    items = sorted(ledger.items())
    rows = [row for key, row in items if key.startswith(f"exp:{arm}:")]
    best, curve = None, []
    for row in rows:
        if row.get("right") is not None and (best is None or row["right"] > best["right"]):
            best = row
        curve.append(best["right"] if best else None)
    finals = [row | {"label": key.split(":")[2]} for key, row in items if key.startswith("final:") and key.split(":")[2] in labels]
    metrics = {"arm": arm, "budget": ledger[f"budget:{arm}"], "experiments": len(rows),
               "crashed": sum(row.get("right") is None for row in rows), "best": best, "best_right_after_each_experiment": curve,
               "gpu_seconds": sum(row.get("wall_seconds", 0) for row in rows), "finals": finals, "rows": rows}
    out = RESULTS / f"{arm}-{nn}"
    out.mkdir(parents=True)   # fails when the run folder exists: a rerun gets the next number
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(sys.argv), "modal_app": "autobench",
                                              "volume": f"autobench-runs:/{arm}/ and /final/"}, indent=1))
    print(f"{arm}: {len(rows)} experiments of {metrics['budget']}, {metrics['crashed']} crashed, GPU {metrics['gpu_seconds'] / 3600:.2f} h")
    if best:
        print(f"best on dev100: {best['right']} of 100 at experiment {best['n']} ({best['generated_tokens'] / 100:.0f} tokens per problem)")
    print("best after each experiment:", " ".join("-" if c is None else str(c) for c in curve))
    for f in finals:
        print(f"final {f['set']} {f['label']}: {f['right']} of {f['problems']}, {f['generated_tokens'] / f['problems']:.0f} tokens per problem, "
              f"{f['finish']['time']} requests cut by time")


if __name__ == "__main__":
    main()
