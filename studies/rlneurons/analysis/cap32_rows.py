"""Per-problem rows of the cap32 cells (specs/SPEC_cap32.md), small enough to commit: the readout of analysis/cap32.py
holds totals only, and the raw answers stay in runs/<job>/ (not in git).

    uv run python -m studies.rlneurons.analysis.cap32_rows <name>=<job> ...

<name>: sft_cue, rl_plain, base_cue. Input: runs/<job>/answers.jsonl. Writes results/cap32/rows-01/<name>.jsonl (one line per
problem: problem_index, unique_id, n_new generated tokens, cap_hit at 32,768, score_v3, extracted_v3, gold, tail = the last
400 characters of the answer) and results/cap32/rows-01/run.json. Checks each cell's totals against results/cap32/readout.json.
"""
import json
import pathlib
import subprocess
import sys

OUT = pathlib.Path(__file__).resolve().parents[1] / "results" / "cap32"
DEST = OUT / "rows-01"
OLD = 16384
KEEP = ("problem_index", "unique_id", "n_new", "cap_hit", "score_v3", "extracted_v3", "gold")

readout = json.loads((OUT / "readout.json").read_text())["cells"]
DEST.mkdir()
jobs = {}
for arg in sys.argv[1:]:
    name, job = arg.split("=")
    rows = [json.loads(line) for line in open(f"runs/{job}/answers.jsonl")]
    rows.sort(key=lambda r: r["problem_index"])
    assert len(rows) == 328 and all(r["sample"] == 0 and r["attempt"] == 0 for r in rows)
    right_new = sum(r["score_v3"] for r in rows)
    right_old = sum(r["score_v3"] for r in rows if r["n_new"] <= OLD and not r["cap_hit"])
    cell = json.dumps(readout[name])
    assert str(right_new) in cell and str(right_old) in cell, (name, right_new, right_old)
    with open(DEST / f"{name}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps({**{k: r[k] for k in KEEP}, "tail": r["text"][-400:]}) + "\n")
    jobs[name] = {"job": job, "right_at_32768": right_new, "right_at_16384": right_old}
    print(name, job, "right at 32,768:", right_new, "at 16,384:", right_old)
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
(DEST / "run.json").write_text(json.dumps({"command": "python -m studies.rlneurons.analysis.cap32_rows " + " ".join(sys.argv[1:]),
                                           "commit": commit, "cells": jobs}, indent=1) + "\n")
