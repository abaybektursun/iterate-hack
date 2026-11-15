"""In-context improvement loop on the cued base, no RL text, no reward, no answer key (specs/SPEC_shots2.md, board work-eb10d7).

Round g samples --samples answers per pool problem with the examples of generation g in front of the prompt (generation 0: none),
then picks the examples of generation g + 1 from those answers: among problems where at least --min-agree finished samples agree
(analysis.day1_vote.vote), the 3 whose longest agreeing answer of at most --max-example-tokens tokens is longest; that answer
is the example. Pool: the first --pool problems of data/rln3/hard.json whose overlap flag is not "none" (outside the 328).
A problem that is an example of generation g is not sampled in round g. The gold answers are used only for the
reported share right per round, never for picking.

    uv run tools/gpu.py submit h100 --hours 2 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.shots_loop --rounds 3 --commit $(git rev-parse HEAD)"

Sample s of problem i in round g has seed --seed + 100000 * g + 10000 * s + i. Writes to --out (default $OUT_DIR):
rows_g<g>.jsonl (every answer), gen<g>.json for g >= 1 (the examples, in the format run_cell --shots reads) and metrics.json.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time

from studies.rlneurons.analysis.day1_vote import vote
from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.jobs import run_cell as C
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R


def pick(rows_by_problem: dict, min_agree: int, max_tokens: int) -> list:
    """[(problem index, row)] of the 3 examples of the next generation."""
    best = []
    for i, rows in sorted(rows_by_problem.items()):
        fin = sorted((r for r in rows if not r["cap_hit"]), key=lambda r: r["sample"])
        v = vote(fin)
        if v["votes"] < min_agree:
            continue
        group = next(g for g in v["groups"] if g[0] == v["winner"])
        ok = [fin[k] for k in group if fin[k]["n_answer_tokens"] <= max_tokens]
        if ok:
            best.append((max(ok, key=lambda r: (r["n_answer_tokens"], -r["sample"])), i))
    best.sort(key=lambda x: (-x[0]["n_answer_tokens"], x[1]))
    assert len(best) >= 3, f"only {len(best)} problems have {min_agree} agreeing finished samples"
    return [(i, r) for r, i in best[:3]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--pool", type=int, default=36)
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--min-agree", type=int, default=3)
    ap.add_argument("--max-example-tokens", type=int, default=3000)
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--seed", type=int, default=81000000)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", required=True)
    a = ap.parse_args()
    t0 = time.time()
    assert a.out and re.fullmatch(r"[0-9a-f]{40}", a.commit)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "metrics.json").exists(), "one fresh directory per run"

    fz = json.loads((C.D4 / "frozen4.json").read_text())
    hard = json.loads((C.D3 / "hard.json").read_text())
    flags = json.loads((C.STUDY / "results" / "rln3" / "rln3_overlap.json").read_text())["sets"]["hard"]["flags"]
    pool = [hard[i] for i in sorted(int(i) for i, f in flags.items() if f["flag"] != "none")][: a.pool]
    pre = fz["prefill_ids"]
    sampling = {"temperature": 1.0, "top_p": 1.0, "repetition_penalty": 1.0}
    m = {"status": "starting", "config": {**vars(a), "out": str(out), "pool_indices": [int(p["index"]) for p in pool], "sampling": sampling,
                                         "model": fz["models"]["base"], "seed_rule": "seed + 100000 * round + 10000 * sample + index"},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "started_utc": J.utc(), "rounds": []}
    G.dump(out / "metrics.json", m)

    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    max_len = 2048 + 3 * (a.max_example_tokens + 1024) + a.max_tokens
    live = {}
    if a.dry_run:
        engine = C.Canned(tok, live)
    else:
        repo, _, rev = fz["models"]["base"]
        model_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
        os.environ.update(G.ENGINE_ENV)
        engine = J.VllmEngine(model_dir, tok_dir, max_len)

    shots = None
    for g in range(a.rounds):
        shot_ids = [int(i) for i in tok(shots["text"], add_special_tokens=False)["input_ids"]] if shots else []
        used = set(shots["problem_indices"]) if shots else set()
        for s in range(a.samples):
            for p in pool:
                i = int(p["index"])
                if i in used:
                    continue
                ids = S.render_ids(tok, p["problem"])
                r = {"rid": f"g{g}|{i}|{s}", "cell": f"loop_g{g}", "bench": "hardpool", "idx": i, "sample": s, "uid": p["unique_id"],
                     "ids": shot_ids + ids + pre, "n_prompt": len(shot_ids) + len(ids), "prefix_ids": pre, "prefix_kind": "opening",
                     "seed": a.seed + 100000 * g + 10000 * s + i, "sampling": sampling, "max_tokens": a.max_tokens, "gold": p["answer"],
                     "problem_text": tok.decode(ids, skip_special_tokens=False)}
                live[r["rid"]] = r
                if a.dry_run:
                    engine.add(r["rid"], r["ids"], sampling, r["seed"], r["max_tokens"])
                else:
                    engine.engine.add_request(r["rid"], {"prompt_token_ids": r["ids"]}, engine.SP(
                        **{**J.BASE_SAMPLING, **sampling}, max_tokens=r["max_tokens"], seed=r["seed"], stop=[C.SHOT_STOP]))
        by = {}
        with open(out / f"rows_g{g}.jsonl", "a") as f:
            while engine.has_unfinished():
                for rid, out_ids, lps, fr in engine.step():
                    req = live.pop(rid)
                    shot_stop = fr == "stop" and S.STOP_ID not in out_ids
                    if shot_stop:
                        out_ids, lps = C.cut_at_shot_stop(tok, out_ids, lps)
                    rec = J.record(tok, req, out_ids, lps, fr)
                    rec.update(R.grade_v3(req["gold"], rec["text"]))
                    rec.update(round=g, shot_stop=shot_stop, problem_text=req["problem_text"])
                    by.setdefault(req["idx"], []).append(rec)
                    f.write(json.dumps(rec) + "\n")
                    f.flush()
        assert not live
        rows = [r for rs in by.values() for r in rs]
        picked = pick(by, a.min_agree, a.max_example_tokens)
        shots = {"arm": f"loop_g{g + 1}", "source_job": os.environ.get("JOB_ID"), "source_round": g, "source_set": "data/rln3/hard.json",
                 "problem_indices": [i for i, _ in picked], "answer_tokens": [r["n_answer_tokens"] for _, r in picked],
                 "samples": [r["sample"] for _, r in picked], "text": "".join(r["problem_text"] + r["text"].rstrip("\n") + "\n\n" for _, r in picked)}
        (out / f"gen{g + 1}.json").write_text(json.dumps(shots, indent=1) + "\n")
        fin = [r for r in rows if not r["cap_hit"]]
        m["rounds"].append({"round": g, "example_tokens_in_prompt": len(shot_ids), "n": len(rows), "right_v3": sum(r["score_v3"] for r in rows),
                            "cap_hits": len(rows) - len(fin), "mean_generated_tokens": sum(r["n_new"] for r in rows) / len(rows),
                            "problems_with_agreement": sum(vote(sorted((r for r in rs if not r["cap_hit"]), key=lambda r: r["sample"]))["votes"] >= a.min_agree for rs in by.values()),
                            "vote_right": sum(vote(sorted(rs, key=lambda r: r["sample"]))["score"] for rs in by.values()), "n_problems": len(by),
                            "picked": shots["problem_indices"], "picked_tokens": shots["answer_tokens"],
                            "picked_right_v3": [r["score_v3"] for _, r in picked]})
        m["status"], m["wall_s"] = f"round {g} done", time.time() - t0
        G.dump(out / "metrics.json", m)
        print(json.dumps(m["rounds"][-1]))
    m["status"] = "done"
    G.dump(out / "metrics.json", m)


if __name__ == "__main__":
    main()
