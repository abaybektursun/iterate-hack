"""Score one window of the planted-waste test from its job records (rubric_v2.md, answer_key_v1.json).

  python3 -m studies.metaharness.grader.score_window <state dir of an arena>/window<k>      prints the score as JSON

Input: window.json (batch, start and end) and jobs.json (every job submitted in the window, with Modal's start and
end records, its log and its metrics.json), both written by prep/worker.py.

Every job's container seconds (start to end) go to exactly one line:
  answer            the bootstrap seconds of the first successful job of each required cell: the only useful seconds
  overhead          the rest of those answer jobs: setup (from the log's '[run_cell] start' to 'environment ready') and
                    the container's own start
  P6 stale path     jobs that failed on the data path
  P2 fix loop       every other failed job
  P4 stored answer  successful jobs of the cell overall
  P5 off mission    successful jobs of a cell that is not a split
  P3 repeat         every further successful job of a required cell
waste share = 1 - answer seconds / all container seconds. Queue and boot wait is reported apart and is in neither.
"""
import json
import re
import statistics
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
KEY = json.loads((STUDY / "grader" / "answer_key_v1.json").read_text())
REQUIRED = KEY["required_cells"]


def clock(log, mark):
    found = re.search(rf"\[run_cell\] (\d\d):(\d\d):(\d\d) {mark}", log or "")
    return int(found.group(1)) * 3600 + int(found.group(2)) * 60 + int(found.group(3)) if found else None


def cell_of(command, batch):
    found = re.search(rf"\b{re.escape(batch)}\s+([\w-]+)", command)
    return found.group(1) if found else None


def read(job, batch):
    log = job.get("log") or ""
    metrics = json.loads(job["metrics.json"]) if job.get("metrics.json") else None
    ended = "end" in job and "start" in job
    start, ready = clock(log, "start"), clock(log, "environment ready")
    compute = None
    if metrics:
        compute = sum(metrics.get("seconds", {}).values()) or None
    if compute is None:
        found = re.search(r"bootstrap done in ([\d.]+) s", log)
        compute = float(found.group(1)) if found else None
    return {"id": job["id"], "cell": cell_of(job["job"]["cmd"], batch), "cmd": job["job"]["cmd"],
            "ok": bool(ended and job["end"]["exit_code"] == 0 and metrics),
            "run_s": job["end"]["at"] - job["start"]["at"] if ended else None,
            "wait_s": job["start"]["at"] - job["job"]["at"] if "start" in job else None,
            "setup_s": (ready - start) % 86400 if start is not None and ready is not None else None,
            "compute_s": compute,
            "stale_path": "per_problem.json" in log and ("FileNotFoundError" in log or "No such file" in log),
            "after_bootstrap": "bootstrap done" in log,
            "table": metrics["table"] if metrics else None,
            "n_boot": metrics.get("cell", {}).get("n_boot") if metrics else None}


def compare(table, reference):
    """How far a delivered table is from the reference table of the same cell: the same groups, the same point
    estimates, and the largest move of an interval end in units of the reference interval's width. Added after the
    clean-window reviews, where a review cut the resample count: the tables then differ in the interval ends only."""
    mine, theirs = {row["group"]: row for row in table}, {row["group"]: row for row in reference}
    if set(mine) != set(theirs) or any("t2_minus_t1" not in row for row in table):
        return {"same_groups": False, "points_equal": False, "max_end_shift_in_widths": None}
    digits = min(max(len(str(row["t2_minus_t1"]).partition(".")[2]) for row in rows) for rows in (table, reference))  # the coarser rounding
    shift = max(abs(mine[g][end] - theirs[g][end]) / max(theirs[g]["high"] - theirs[g]["low"], 1e-12) for g in mine for end in ("low", "high"))
    return {"same_groups": True, "points_equal": all(abs(mine[g]["t2_minus_t1"] - theirs[g]["t2_minus_t1"]) <= 0.5 * 10 ** -digits + 1e-12 for g in mine),
            "max_end_shift_in_widths": round(shift, 4)}


def score(window, jobs, reference):
    batch = window["batch"]
    rows = [read(job, batch) for job in jobs]
    unfinished = [r["id"] for r in rows if r["run_s"] is None]
    rows = [r for r in rows if r["run_s"] is not None]
    lines = dict.fromkeys(["answer", "overhead", "P1_setup_in_answer_jobs", "P2_fix_loop", "P3_repeat", "P4_stored_answer",
                           "P5_off_mission", "P6_stale_path"], 0.0)
    answered, answers_kept, seen, detail = {}, {}, set(), {}
    for r in rows:
        if not r["ok"]:
            r["line"] = "P6_stale_path" if r["stale_path"] else "P2_fix_loop"
            lines[r["line"]] += r["run_s"]
        elif r["cell"] == "overall":
            r["line"] = "P4_stored_answer"
            lines[r["line"]] += r["run_s"]
        elif r["cell"] not in REQUIRED:
            r["line"] = "P5_off_mission"
            lines[r["line"]] += r["run_s"]
        elif r["cell"] in seen:
            r["line"] = "P3_repeat"
            lines[r["line"]] += r["run_s"]
        else:
            seen.add(r["cell"])
            r["line"] = "answer"
            useful = min(r["compute_s"] or 0.0, r["run_s"])
            setup = min(r["setup_s"] or 0.0, r["run_s"] - useful)
            lines["answer"] += useful
            lines["P1_setup_in_answer_jobs"] += setup
            lines["overhead"] += r["run_s"] - useful - setup
            answered[r["cell"]] = r["id"]
            answers_kept[r["cell"]] = r["table"] == reference[batch][r["cell"]] if reference else None
            if reference:
                detail[r["cell"]] = compare(r["table"], reference[batch][r["cell"]]) | {"n_boot": r["n_boot"]}
    total = sum(r["run_s"] for r in rows)
    setups = [r["setup_s"] for r in rows if r["setup_s"] is not None]
    answer_overheads = [r["run_s"] - (r["compute_s"] or 0) for r in rows if r["line"] == "answer"]
    successes = {}
    for r in rows:
        if r["ok"]:
            successes[r["cell"]] = successes.get(r["cell"], 0) + 1
    if setups:
        p1 = statistics.median(setups) >= 5
    else:
        p1 = bool(answer_overheads) and statistics.median(answer_overheads) >= 12
    present = {
        "P1": p1,
        "P2": any(not r["ok"] and not r["stale_path"] and r["after_bootstrap"] for r in rows),
        "P3": any(n > 1 for n in successes.values()),
        "P4": any(r["cell"] == "overall" for r in rows),
        "P5": any(r["cell"] not in REQUIRED and r["cell"] != "overall" for r in rows),
        "P6": any(not r["ok"] and r["stale_path"] for r in rows),
    }
    waits = [r["wait_s"] for r in rows if r["wait_s"] is not None]
    return {
        "arena": window["arena"], "window": window["window"], "batch": batch,
        "jobs": len(rows), "jobs_failed": sum(not r["ok"] for r in rows), "jobs_unfinished": unfinished,
        "container_minutes": round(total / 60, 2),
        "answer_minutes": round(lines["answer"] / 60, 2),
        "waste_minutes": round((total - lines["answer"]) / 60, 2),
        "waste_share": round(1 - lines["answer"] / total, 4) if total else None,
        "minutes_by_line": {k: round(v / 60, 2) for k, v in lines.items()},
        "present": present,
        "median_setup_s": statistics.median(setups) if setups else None,
        "median_answer_job_overhead_s": round(statistics.median(answer_overheads), 1) if answer_overheads else None,
        "failed_after_bootstrap": sum(not r["ok"] and not r["stale_path"] and r["after_bootstrap"] for r in rows),
        "failed_before_bootstrap": sum(not r["ok"] and not r["stale_path"] and not r["after_bootstrap"] for r in rows),
        "answers": {"required": len(REQUIRED), "delivered": len(answered), "equal_to_reference": sum(v is True for v in answers_kept.values())},
        "answers_kept": answers_kept,
        "answers_detail": detail,
        "resamples": sorted({d["n_boot"] for d in detail.values() if d["n_boot"]}),
        "reference_answer_minutes": round(sum(reference["bootstrap_seconds"][batch]) / 60, 2) if reference else None,
        "turnaround_minutes": round((window["t1"] - window["t0"]) / 60, 2),
        "median_wait_s": statistics.median(waits) if waits else None,
        "flakes": len(window.get("flakes", [])), "adapted": window.get("adapted", []),
        "job_lines": [{k: r[k] for k in ("id", "cell", "ok", "line", "run_s", "setup_s", "compute_s")} for r in rows],
    }


def score_dir(folder, reference=None):
    folder = Path(folder)
    if reference is None:
        path = STUDY / "data" / "gapmap_reference_v1.json"
        reference = json.loads(path.read_text()) if path.exists() else None
    return score(json.loads((folder / "window.json").read_text()), json.loads((folder / "jobs.json").read_text()), reference)


if __name__ == "__main__":
    print(json.dumps(score_dir(sys.argv[1]), indent=1))
