"""Relay plan on hard328 (specs/SPEC_relay.md): for both writers' stored sample 0 (handoff_lib.RELAY_WRITERS) and every cut, the
prefix length and the sha256 of its ids; each writer answer's stratum, token count and source. Laptop, tokenizer files only.

    uv run --no-project --with numpy --with math-verify==0.9.0 --with transformers==5.19.0 --with tokenizers==0.23.3 --with huggingface_hub --with jinja2 \
        python -m studies.rlneurons.prep.relay_plan --runs runs

Reads runs/<writer job>/answers.jsonl (uv run tools/gpu.py get <job>). Writes data/handoff/plan_v2.json, in the format of
plan_v1.json (prep/handoff_plan.py) so that jobs/handoff_gen.py --plan plan_v2.json reads it; the job re-tokenizes the same texts
and asserts the same sha256. A cap-hit answer has 16,384 ids, so its cut is a share of the cap.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from studies.rlneurons.jobs import run_cell as C
from studies.rlneurons.lib import handoff_lib as H
from studies.rlneurons.lib import rln4_lib as R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    a = ap.parse_args()
    out = C.STUDY / "data" / "handoff" / "plan_v2.json"
    assert not out.exists(), f"{out} exists: a changed plan is a new version"
    fz = json.loads((C.D4 / "frozen4.json").read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    probs = {int(p["index"]): p for p in C.problems("hard328", fz)}
    pool = sorted(probs)
    plan = {"version": 2, "set": "hard328", "writers": H.RELAY_WRITERS, "cuts": list(H.CUTS), "seed": H.RELAY_SEED,
            "pool_rule": "all 328 problems of hard328 (run_cell.problems)", "pool": pool, "rows": []}
    for w, job in H.RELAY_WRITERS.items():
        texts = H.writer_texts(pathlib.Path(a.runs) / job / "answers.jsonl")
        assert sorted(texts) == pool, w
        for i in pool:
            t = texts[i]
            assert t["gold"] == probs[i]["answer"] and t["seed"] == 3_000_000 + i and t["max_tokens"] == fz["cap"], (w, i)
            ids = H.answer_ids(tok, fz, t["text"])
            assert tok.decode(ids) == t["text"], (w, i)
            lens = {str(c): H.cut_len(len(ids), c) for c in H.CUTS}
            plan["rows"].append({
                "problem_index": i, "writer": w, "stratum": "cap" if t["cap_hit"] else ("right" if t["score_v3"] else "wrong"),
                "writer_score": t["score_v3"], "writer_extracted": t["extracted_v3"] is not None, "source": t["unique_id"].split("/")[0],
                "n_answer_tokens_stored": t["n_answer_tokens"], "n_ids": len(ids), "text_sha256": H.sha(t["text"]), "len": lens,
                "ids_sha256": {k: H.sha(ids[:L]) for k, L in lens.items()},
                "prefix_has_right": {k: R.grade_v3(t["gold"], tok.decode(ids[:L]))["score_v3"] for k, L in lens.items()}})
    out.write_text(json.dumps(plan, indent=1) + "\n")
    for w in H.RELAY_WRITERS:
        rw = [r for r in plan["rows"] if r["writer"] == w]
        print(w, "right", sum(r["writer_score"] for r in rw), {s: sum(r["stratum"] == s for r in rw) for s in ("right", "wrong", "cap")},
              "ids differ from stored count:", sum(r["n_ids"] != r["n_answer_tokens_stored"] for r in rw), "max diff", max(abs(r["n_ids"] - r["n_answer_tokens_stored"]) for r in rw),
              "prefix_has_right by cut:", {c: sum(r["prefix_has_right"][str(c)] for r in rw) for c in H.CUTS},
              "ids:", sum(r["n_ids"] for r in rw), "new tokens if the finisher writes what was left, by cut:", {c: sum(r["n_ids"] - r["len"][str(c)] for r in rw) for c in (25, 50)})


if __name__ == "__main__":
    main()
