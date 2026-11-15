"""Copy what the planted-waste test recorded about each arena into the repository's run folders (SPEC2 "Layout").

  MH_HOME=<dir> python3 -m studies.metaharness.analysis.planted_collect

Reads $MH_HOME/state/<arena>/ (prep/worker.py, prep/review.py, prep/run_arena.py) and writes, per run of
data/planted_arenas_v1.json, results/<planted|clean>/<arm>-<nn>/:
  run.json        the arena, the model, the prompt, each window's times, commits and job ids, each review's session
  metrics.json    each window's score (grader/score_window.py) and each review's cost
  review<k>/      the review's final message, the entry it wrote (skill arm), its diff and its commits
  board.json      the arena's board items and comments
  examples.json   one job counted as an answer and one counted as waste, with command and log
Run folders are written once; an existing folder stops the script.
"""
import json
import shutil
from pathlib import Path

from studies.metaharness.grader import score_window
from studies.metaharness.lib import arena as A

STUDY = Path(__file__).resolve().parents[1]
arenas = json.loads((STUDY / "data" / "planted_arenas_v1.json").read_text())

for experiment in ("planted", "clean"):
    for run, arena_id in arenas[experiment].items():
        state = A.state_dir(arena_id)
        out = STUDY / "results" / experiment / run
        assert not out.exists(), f"{out} exists: a run folder is never written twice"
        out.mkdir(parents=True)
        arena = A.load(arena_id)
        windows, reviews, scores = [], [], []
        for folder in sorted(state.glob("window*")):
            window = json.loads((folder / "window.json").read_text())
            jobs = json.loads((folder / "jobs.json").read_text())
            score = score_window.score_dir(folder)
            scores.append(score)
            windows.append({k: window[k] for k in ("window", "batch", "started", "ended", "commit_start", "commit_end", "cells", "answered",
                                                   "launch_lines", "adapted", "flakes", "work", "extra_work")} | {"jobs": [j["id"] for j in jobs]})
            if not (out / "examples.json").exists():
                lines = {row["id"]: row for row in score["job_lines"]}
                picked = {}
                for job in jobs:
                    line = lines.get(job["id"], {}).get("line")
                    kind = "answer" if line == "answer" else "waste" if line and line != "answer" else None
                    if kind and kind not in picked:
                        picked[kind] = {"job": job["id"], "counted_as": line, "command": job["job"]["cmd"], "exit_code": job.get("end", {}).get("exit_code"),
                                        "container_seconds": lines[job["id"]]["run_s"], "log": (job.get("log") or "")[-2500:],
                                        "metrics": json.loads(job["metrics.json"]) if job.get("metrics.json") else None}
                (out / "examples.json").write_text(json.dumps(picked, indent=1) + "\n")
        for folder in sorted(state.glob("review*")):
            review = json.loads((folder / "review.json").read_text())
            reviews.append({k: review.get(k) for k in ("round", "arm", "prompt", "model", "minutes", "turns", "cost_usd", "session_id", "exit_code",
                                                       "before", "after", "harness", "jobs", "job_minutes")})
            (out / folder.name).mkdir()
            for name in ("final_message.md", "meta_entry.md", "change.diff", "files.txt", "commits.txt"):
                if (folder / name).exists():
                    shutil.copy(folder / name, out / folder.name / name)
        board = [{k: row.get(k) for k in ("pk", "sk", "kind", "listed", "who", "branch", "at", "closed_at", "text")}
                 for row in A.dump_board(arena) if row["sk"] == "item" or row["sk"].startswith("comment#")]
        (out / "board.json").write_text(json.dumps(sorted(board, key=lambda r: str(r.get("at"))), indent=1) + "\n")
        (out / "run.json").write_text(json.dumps({
            "arena": arena, "store": "moto server (DynamoDB table iterate-board-test, team bucket), local", "job_class": "cpu (Modal, 4 cores, max 8 at a time)",
            "commands": {"arena": f"python3 -m studies.metaharness.prep.run_arena {arena_id} {arena['arm']} {arena['variant']} {arena['port']} {arena['base_sha']} <windows>",
                         "review": "prep/review.py: claude -p <prompt> --model <model> --max-turns 90 (see the file)"},
            "study_commit": A.sh(["git", "rev-parse", "HEAD"], STUDY, None).stdout.strip(),
            "windows": windows, "reviews": reviews}, indent=1) + "\n")
        (out / "metrics.json").write_text(json.dumps({"windows": scores, "reviews": reviews}, indent=1) + "\n")
        print(f"{experiment}/{run} ({arena_id}): {len(windows)} windows, {len(reviews)} reviews, waste share "
              + " -> ".join(str(s["waste_share"]) for s in scores))
