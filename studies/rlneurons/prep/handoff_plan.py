"""Prefix hand-off plan (specs/SPEC_handoff.md): the pool, each writer sample's stratum and token count, and for every
(problem, writer, cut) the prefix length and the sha256 of its ids. Laptop, tokenizer files only.

    uv run --no-project --with numpy --with math-verify==0.9.0 --with transformers==5.19.0 --with tokenizers==0.23.3 --with huggingface_hub --with jinja2 \
        python -m studies.rlneurons.prep.handoff_plan --runs runs

Reads runs/<writer job>/answers.jsonl (uv run tools/gpu.py get <job>) and results/day1_3/*/rows.jsonl. Writes
data/handoff/plan_v1.json. The job re-tokenizes the same texts and asserts the same sha256.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from studies.rlneurons.lib import handoff_lib as H
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
ROWS = {"base": "math500_base_cue-01", "rl": "math500_rl-01"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    a = ap.parse_args()
    out = STUDY / "data" / "handoff" / "plan_v1.json"
    assert not out.exists(), f"{out} exists: a changed plan is a new version"
    fz = json.loads((STUDY / "data" / "rln4" / "frozen4.json").read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    stored = {}
    for w, d in ROWS.items():
        rows = [json.loads(l) for l in (STUDY / "results" / "day1_3" / d / "rows.jsonl").read_text().splitlines()]
        stored[w] = {(r["problem_index"], r["sample"]): r for r in rows if r["attempt"] == 0}
        assert len(stored[w]) == 2000
    pool = [i for i in range(500) if sum(stored["base"][i, s]["score_v3"] for s in range(4)) <= 3]
    plan = {"version": 1, "writers": H.WRITERS, "cuts": list(H.CUTS), "seed": H.SEED, "pool_rule": "base right in at most 3 of 4 stored samples (attempt 0, v3)",
            "pool": pool, "unbiased": [i for i in pool if sum(stored["base"][i, s]["score_v3"] for s in (1, 2, 3)) <= 2], "rows": []}
    for w, job in H.WRITERS.items():
        texts = H.writer_texts(pathlib.Path(a.runs) / job / "answers.jsonl")
        for i in pool:
            t, c = texts[i], stored[w][i, 0]
            assert (t["n_new"], t["cap_hit"], t["score_v3"]) == (c["n_new"], c["cap_hit"], c["score_v3"]), (w, i)
            ids = H.answer_ids(tok, fz, t["text"])
            assert tok.decode(ids) == t["text"], (w, i)
            lens = {str(c_): H.cut_len(len(ids), c_) for c_ in H.CUTS}
            plan["rows"].append({
                "problem_index": i, "writer": w, "stratum": "cap" if t["cap_hit"] else ("right" if t["score_v3"] else "wrong"),
                "writer_score": t["score_v3"], "n_answer_tokens_stored": t["n_answer_tokens"], "n_ids": len(ids), "text_sha256": H.sha(t["text"]),
                "fresh_scores": [stored[w][i, s]["score_v3"] for s in (1, 2, 3)], "len": lens,
                "ids_sha256": {k: H.sha(ids[:L]) for k, L in lens.items()},
                "prefix_has_right": {k: R.grade_v3(t["gold"], tok.decode(ids[:L]))["score_v3"] for k, L in lens.items()}})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=1) + "\n")
    rows = plan["rows"]
    for w in H.WRITERS:
        rw = [r for r in rows if r["writer"] == w]
        print(w, {s: sum(r["stratum"] == s for r in rw) for s in ("right", "wrong", "cap")},
              "ids differ from stored count:", sum(r["n_ids"] != r["n_answer_tokens_stored"] for r in rw), "max diff", max(abs(r["n_ids"] - r["n_answer_tokens_stored"]) for r in rw),
              "prefix_has_right by cut:", {c: sum(r["prefix_has_right"][str(c)] for r in rw) for c in H.CUTS},
              "new tokens if the finisher writes what was left (25+50+75):", sum(r["n_ids"] - r["len"][str(c)] for r in rw for c in (25, 50, 75)))
    print("pool", len(pool), "unbiased", len(plan["unbiased"]))


if __name__ == "__main__":
    main()
