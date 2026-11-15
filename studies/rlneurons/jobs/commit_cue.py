"""Closing cue (specs/SPEC_commit1.md, board work item in the spec): a stored answer that ran past N tokens is cut at N tokens,
a commit line is appended, and the same model continues. One job, one model, both problem sets, every (N, form).

    uv run tools/gpu.py submit h100 --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.commit_cue --model base --commit $(git rev-parse HEAD)"

Inputs: the stored rows of earlier jobs in the submitter's Volume (/runs/<job>/answers.jsonl), sample 0, attempt 0:
SOURCES below. Forms: "box" appends BOX and generates at most 64 tokens; the answer is the text up to the brace that closes the
forced box. "voice" appends VOICE and generates at most 1,024 tokens; a continuation that does not stop within them counts as no answer.
Only the continuation is graded. T 1.0 / top-p 1.0; request seed --seed + 100000 * (index of
N) + 10000 * (index of form) + problem index. Writes $OUT_DIR/rows.jsonl (set, problem, N, form, the continuation, v3 score, and
the stored answer's score and tokens) and metrics.json. --n limits each set to its first n long answers (smoke).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time

from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.jobs import run_cell as C
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

SOURCES = {"base": {"math500": "abaybektursun-1114-153825-208b", "hard328": "abaybektursun-1114-151534-e72c"},
           "rl": {"math500": "abaybektursun-1114-183640-e828", "hard328": "abaybektursun-1114-151540-86ef"}}
CUTS = (4000, 8000, 12000)
BOX = "\n\nFinal answer: \\boxed{"
VOICE = ("\n\nI have used most of my space, so I will stop exploring here, settle on the most likely answer from my work above, "
         "and write it down.\n\n")
FORMS = {"box": (BOX, 64), "voice": (VOICE, 1024)}


def close_box(text: str, start: int) -> str:
    """text up to and including the brace that closes the box opened just before position start."""
    depth = 1
    for k in range(start, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return text[: k + 1]
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(SOURCES))
    ap.add_argument("--runs", default="/runs")
    ap.add_argument("--seed", type=int, default=91000000)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", required=True)
    a = ap.parse_args()
    t0 = time.time()
    assert a.out and re.fullmatch(r"[0-9a-f]{40}", a.commit)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "rows.jsonl").exists(), "one fresh directory per run"
    fz = json.loads((C.D4 / "frozen4.json").read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    enc = lambda s: [int(i) for i in tok(s, add_special_tokens=False)["input_ids"]]
    sampling = {"temperature": 1.0, "top_p": 1.0, "repetition_penalty": 1.0}

    reqs = []
    for bench, job in SOURCES[a.model].items():
        probs = {int(p["index"]): p for p in C.problems(bench, fz)}
        rows = [r for r in map(json.loads, open(pathlib.Path(a.runs) / job / "answers.jsonl")) if r["sample"] == 0 and r.get("attempt", 0) == 0]
        assert len(rows) == len(probs), (bench, len(rows))
        long = sorted((r for r in rows if r["n_new"] > CUTS[0]), key=lambda r: r["problem_index"])[: a.n]
        for r in long:
            p = probs[r["problem_index"]]
            assert r["gold"] == p["answer"]
            pid, aid = S.render_ids(tok, p["problem"]), enc(r["text"])
            for ci, n in enumerate(CUTS):
                if r["n_new"] <= n:
                    continue
                for fi, (form, (suffix, mt)) in enumerate(FORMS.items()):
                    pre = aid[:n] + enc(suffix)
                    reqs.append({"rid": f"{bench}|{r['problem_index']}|{n}|{form}", "cell": f"{a.model}_commit_{form}_{n}", "bench": bench,
                                 "idx": r["problem_index"], "sample": 0, "uid": p["unique_id"], "ids": pid + pre, "n_prompt": len(pid),
                                 "prefix_ids": pre, "prefix_kind": "commit", "seed": a.seed + 100000 * ci + 10000 * fi + r["problem_index"],
                                 "sampling": sampling, "max_tokens": mt, "gold": r["gold"], "cut": n, "form": form,
                                 "stored": {"score_v3": r["score_v3"], "n_new": r["n_new"], "cap_hit": r["cap_hit"]}})
    live = {r["rid"]: r for r in reqs}
    m = {"status": "starting", "config": {**vars(a), "out": str(out), "sources": SOURCES[a.model], "cuts": CUTS, "forms": FORMS,
                                         "sampling": sampling, "n_requests": len(reqs)},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "started_utc": J.utc()}
    G.dump(out / "metrics.json", m)
    if a.dry_run:
        engine = C.Canned(tok, live)
    else:
        repo, _, rev = fz["models"][C.MODELS[a.model]]
        model_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
        os.environ.update(G.ENGINE_ENV)
        engine = J.VllmEngine(model_dir, tok_dir, 2048 + CUTS[-1] + 64 + 1024)
    for r in reqs:
        engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"])
    done = 0
    with open(out / "rows.jsonl", "a") as f:
        while engine.has_unfinished():
            for rid, out_ids, lps, fr in engine.step():
                req = live.pop(rid)
                rec = J.record(tok, req, out_ids, lps, fr)
                pre_text = tok.decode(req["prefix_ids"], skip_special_tokens=False)
                cont = rec["text"][len(pre_text):]              # only the continuation is graded: no answer is read from before the cut
                answer = "\\boxed{" + close_box(cont, 0) if req["form"] == "box" else ("" if rec["cap_hit"] else cont)
                g = R.grade_v3(req["gold"], answer)
                f.write(json.dumps({"bench": req["bench"], "problem_index": req["idx"], "cut": req["cut"], "form": req["form"], "seed": req["seed"],
                                    "continuation": cont, "n_new": rec["n_new"], "cap_hit": rec["cap_hit"],
                                    "finish_reason": fr, "gold": req["gold"], **g, "stored": req["stored"],
                                    "before_cut_tail": pre_text[-600:]}) + "\n")
                f.flush()
                done += 1
    assert not live
    m.update(status="done", n=done, wall_s=time.time() - t0)
    G.dump(out / "metrics.json", m)
    print(json.dumps({"status": "done", "n": done, "wall_s": m["wall_s"]}))


if __name__ == "__main__":
    main()
