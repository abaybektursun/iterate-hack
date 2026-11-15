"""Planted checks for the prefix hand-off (specs/SPEC_handoff.md): inputs that must score right and inputs that must fail.

    uv run --no-project --with numpy --with math-verify==0.9.0 --with transformers==5.19.0 --with tokenizers==0.23.3 --with huggingface_hub --with jinja2 \
        python -m studies.rlneurons.analysis.handoff_test --runs runs

Runs handoff_gen's request builder on the real plan and writer texts with the stand-in engine's three outputs.
"""
import argparse
import json
import pathlib

from studies.rlneurons.analysis import handoff as A
from studies.rlneurons.jobs import handoff_gen as J
from studies.rlneurons.jobs import run_cell as C
from studies.rlneurons.lib import handoff_lib as H
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    a = ap.parse_args()
    fz = json.loads((C.D4 / "frozen4.json").read_text())
    plan = json.loads(J.PLAN.read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    texts = {w: H.writer_texts(pathlib.Path(a.runs) / job / "answers.jsonl") for w, job in H.WRITERS.items()}
    reqs = J.requests(tok, fz, plan, texts, list(H.CUTS))
    P = {(r["problem_index"], r["writer"]): r for r in plan["rows"]}
    n13 = json.loads((C.D4 / "prompt_ids.json").read_text())["ids"]

    def row(q, gen_text):
        rec = {**q, "finisher": "rl", "n_new": 0, "cap_hit": False, "finish_reason": "stop", "prefix_text": tok.decode(q["ids"][q["n_prompt"]:]), "gen_text": gen_text}
        return A.score(rec, P[q["problem_index"], q["writer"]])

    n0 = n100 = 0
    for q in reqs:
        p = P[q["problem_index"], q["writer"]]
        if q["cut"] == 0:                                           # cut 0 is the plain cell's prompt, id for id
            assert q["ids"] == n13[q["problem_index"]] and q["max_tokens"] == fz["cap"], q["rid"]
            n0 += 1
        if q["cut"] == 100:                                         # the whole answer + an immediate stop scores what the writer scored
            assert p["stratum"] != "cap" and row(q, "")["score_v3"] == p["writer_score"], q["rid"]
            if p["writer_score"]:                                   # failing input: a wrong answer line after a right answer scores 0
                assert row(q, "\n\nAnswer: $-123456789$")["score_v3"] == 0, q["rid"]
            n100 += 1
        assert q["ids"][: q["n_prompt"]] == n13[q["problem_index"]] and len(q["ids"]) + q["max_tokens"] == q["n_prompt"] + fz["cap"]
    base25 = [q for q in reqs if q["writer"] == "base" and q["cut"] == 25]
    assert all(q["ids"][q["n_prompt"]:][:3] == fz["prefill_ids"] for q in base25), "a base prefix does not start with the cue"
    assert n0 == 2 * len(plan["pool"]) and n100 == sum(r["stratum"] != "cap" for r in plan["rows"]), (n0, n100)
    assert len({q["seed"] for q in reqs}) == len(reqs)
    # the reported onset_lines bug: a degenerate answer must be recorded and counted, with its score kept
    deg = next((t for t in ("\n" * 9000, " \n" * 9000, "\n \n" * 4000) if _raises(t)), None)
    q = next(q for q in reqs if q["cut"] == 100 and P[q["problem_index"], q["writer"]]["writer_score"])
    if deg is not None:
        r = row({**q, "ids": q["ids"][: q["n_prompt"]]}, deg + f"\\boxed{{{q['gold']}}}")
        assert r["loop_error"] and r["loop_A"] is None and r["score_v3"] == 1, r
    print(f"handoff_test: ok ({len(reqs)} requests, {n0} cut-0, {n100} cut-100, degenerate input raises in onset_lines: {deg is not None})")


def _raises(text):
    try:
        R.onset_lines(text)
    except IndexError:
        return True
    return False


if __name__ == "__main__":
    main()
