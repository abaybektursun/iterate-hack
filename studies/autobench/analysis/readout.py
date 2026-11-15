# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Read the runner's ledger and write one run folder per arm, then print the comparison.

    uv run studies/autobench/analysis/readout.py <nn> <arm> [<arm> ...]      e.g.  01 calib baseline ours

Writes studies/autobench/results/karpathy-task/<arm>-<nn>/metrics.json (every experiment as the runner recorded it,
the best valid val_bpb after each experiment, the holdout scores under the label <arm>) and run.json. An
experiment is valid when it ended with exit code 0, recorded a val_bpb and ran no longer than the wall limit:
the median wall time of the arm `calib` plus 60 s (specs/SPEC1.md, leak L4).
"""
import json
import statistics
import subprocess
import sys
from pathlib import Path

import modal

RESULTS = Path(__file__).resolve().parent.parent / "results" / "karpathy-task"
ledger = modal.Dict.from_name("autobench-ledger")


def rows(prefix):
    return [value for key, value in sorted(ledger.items()) if key.startswith(prefix + ":")]


def main():
    nn, arms = sys.argv[1], sys.argv[2:]
    calib = [r for r in rows("exp:calib") if r["state"] == "done" and r["exit_code"] == 0]
    wall_limit = statistics.median(r["wall_seconds"] for r in calib) + 60
    noise = statistics.stdev(r["val_bpb"] for r in calib)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    print(f"calib: {len(calib)} runs of the pinned train.py, val_bpb sd {noise:.6f}, wall limit {wall_limit:.0f} s")
    for arm in arms:
        experiments = rows(f"exp:{arm}")
        best, curve = None, []
        for r in experiments:
            r["valid"] = (r["state"] == "done" and r["exit_code"] == 0 and r["val_bpb"] is not None
                          and r["wall_seconds"] <= wall_limit)
            if r["valid"] and (best is None or r["val_bpb"] < best["val_bpb"]):
                best = r
            curve.append(best["val_bpb"] if best else None)
        finals = rows(f"final:{arm}")
        metrics = {"arm": arm, "budget": ledger[f"budget:{arm}"], "experiments": len(experiments),
                   "valid": sum(r["valid"] for r in experiments), "wall_limit_seconds": wall_limit,
                   "calib_val_bpb_sd": noise, "best_valid": best, "best_val_bpb_after_each_experiment": curve,
                   "gpu_seconds": sum(r.get("wall_seconds", 0) for r in experiments), "finals": finals, "rows": experiments}
        out = RESULTS / f"{arm}-{nn}"
        out.mkdir(parents=True)   # fails when the run folder exists: a rerun gets the next number
        (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
        (out / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(sys.argv),
                                                  "modal_app": "autobench", "volume": f"autobench-runs:/{arm}/"}, indent=1))
        test = ", ".join(f"val {f['val_bpb']:.6f} test {f['test_bpb']:.6f}" for f in finals if f.get("test_bpb")) or "not scored"
        best_text = f"{best['val_bpb']:.6f} at experiment {best['n']}" if best else "none"
        print(f"{arm}: {metrics['valid']} valid of {len(experiments)} experiments (budget {metrics['budget']}), "
              f"best val_bpb {best_text}, GPU {metrics['gpu_seconds'] / 3600:.2f} h, holdout: {test}")


if __name__ == "__main__":
    main()
