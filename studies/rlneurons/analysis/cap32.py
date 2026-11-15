"""cap32 readout (specs/SPEC_cap32.md): cells of the 328 run with a cap of 32,768 generated tokens. Each cell is scored twice from
the same answers: right at 32,768, and right with at most 16,384 generated tokens (the old cap).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.cap32 <name>=<job> ...

<name>: sft_cue, rl_plain, base_cue. Inputs: runs/<job>/ (python3 tools/vast.py get <instance> <job>). Writes
results/cap32/<name>-01/ (run.json, metrics.json, examples.json) and results/cap32/readout.json.
"""
import json
import pathlib
import shutil
import sys

from studies.rlneurons.lib import n13_score as S

OUT = pathlib.Path(__file__).resolve().parents[1] / "results" / "cap32"
OLD, NEW = 16384, 32768
STORED_16K = {"sft_cue": [212, 219], "rl_plain": [206], "base_cue": [164]}   # right of 328 at the old cap, earlier jobs (spec)
out = {"spec": "studies/rlneurons/specs/SPEC_cap32.md", "set": "hard328", "n": 328, "cells": {}}
for arg in sys.argv[1:]:
    name, job = arg.split("=")
    m = json.loads(pathlib.Path(f"runs/{job}/metrics.json").read_text())
    assert m["status"] == "done" and m["config"]["set"] == "hard328" and m["config"]["max_tokens"] == NEW and m["config"]["n"] is None
    rows = sorted(map(json.loads, open(f"runs/{job}/answers.jsonl")), key=lambda r: r["problem_index"])
    assert len(rows) == 328
    r32 = [r["score_v3"] for r in rows]
    r16 = [r["score_v3"] if r["n_new"] <= OLD and not r["cap_hit"] else 0 for r in rows]
    lo, hi = S.paired_bootstrap(r32, r16, n_boot=10000, seed=0)
    late = [r for r in rows if r["n_new"] > OLD]
    out["cells"][name] = {
        "job_id": job, "right_at_32768": sum(r32), "right_at_16384_same_answers": sum(r16), "stored_right_at_16384": STORED_16K[name],
        "gain": {"problems": sum(r32) - sum(r16), "points": round(100 * (sum(r32) - sum(r16)) / 328, 2), "ci95": [round(lo, 2), round(hi, 2)]},
        "answers_longer_than_16384": len(late), "of_them_finished": sum(not r["cap_hit"] for r in late), "of_them_right": sum(r["score_v3"] for r in late),
        "cap_hits_at_32768": sum(r["cap_hit"] for r in rows),
        "tokens_per_problem_at_32768": round(sum(r["n_new"] for r in rows) / 328, 1),
        "tokens_per_problem_at_16384": round(sum(min(r["n_new"], OLD) for r in rows) / 328, 1)}
    d = OUT / f"{name}-01"
    d.mkdir(parents=True)
    shutil.copy(f"runs/{job}/metrics.json", d / "metrics.json")
    (d / "run.json").write_text(json.dumps({"job_id": job, "commit": m["commit"], "config": m["config"],
                                            "raw_answers": f"runs/{job}/answers.jsonl (copied from the vast.ai box; not in git)"}, indent=1) + "\n")
    ex = lambda r: {k: r[k] for k in ("problem_index", "gold", "extracted_v3", "score_v3", "n_new", "cap_hit")} | {"prompt_tail": r["prompt"][-400:], "answer_tail": r["text"][-800:]}
    (d / "examples.json").write_text(json.dumps({"right_after_16384": ex(next(r for r in late if r["score_v3"])) if any(r["score_v3"] for r in late) else None,
                                                 "wrong_after_16384": ex(next(r for r in late if not r["score_v3"])) if any(not r["score_v3"] for r in late) else None}, indent=1) + "\n")
(OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
