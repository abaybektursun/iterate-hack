"""selfopen-01 (specs/SPEC_selfopen01.md, entry r5-m10:theory:intervention of results/engine/round-05/experiments.md): rejection
sampling on the plain base's own opening tokens, no prefilled tokens.

    bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.theory.jobs.selfopen_gen --commit <sha>

For every problem in data/selfopen01_t3.json "regenerate" (the stored T3 row does not self-open):
  1. openings: draws j = 1..--draws of at most --open-tokens new tokens on the plain prompt (the pair1 prompt, no prefill),
     T 1.0 / top-p 1.0, seed 47,000,000 + i + 10,000 * j. A draw self-opens when '\\nOkay' is in the first 60 characters of its text.
  2. arm main: the first draw that self-opens, or draw 1 when none does. Arm control: the first draw that does not self-open, or
     draw 1 when every draw does.
  3. continuations: each chosen draw is continued at the same setting with its own seed, prompt + the draw's token ids, up to
     --max-tokens counted from the start of the answer (the draw's tokens included). A draw that already ended with the stop id
     is the whole answer. When both arms chose the same draw, it is continued once and serves both.
Model, tokenizer, prompt ids and the MATH-500 file as studies/rlneurons/jobs/run_cell.py (data/rln4/frozen4.json); the engine and
the row record are rln4_gen's (the K-continuation convention: text = decoded prefix + decoded continuation); grader v3 is
rln4_lib.grade_v3.

  --n        the first n problems of the regenerate list (smoke runs); default all.
  --dry-run  run_cell's stand-in engine (no vLLM, no weights, no GPU).

Writes to --out (default $OUT_DIR): openings.jsonl (one row per draw), answers.jsonl (one row per continued draw, fields draw,
arms, opening_self_open, final_self_open), choices.json (per problem the chosen draws), metrics.json. Fail loud: no try/except.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time
from importlib import metadata

from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.jobs import run_cell as RC
from studies.rlneurons.lib import n13_gen as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

THEORY = pathlib.Path(__file__).resolve().parents[1]
SEED_BASE = 47_000_000              # T3's seed base; draw j of problem i: SEED_BASE + i + 10,000 * j
SAMPLING = {"temperature": 1.0, "top_p": 1.0, "repetition_penalty": 1.0}


def self_opens(text: str) -> bool:
    return "\nOkay" in text[:60]


def run_queue(engine, reqs, on_row):
    live = {r["rid"]: r for r in reqs}
    for r in reqs:
        engine.add(r["rid"], r["ids"], r["sampling"], r["seed"], r["max_tokens"])
    while engine.has_unfinished():
        for rid, out_ids, lps, fr in engine.step():
            on_row(live.pop(rid), out_ids, lps, fr)
    assert not live, f"{len(live)} requests did not finish"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=32)
    ap.add_argument("--open-tokens", type=int, default=24)
    ap.add_argument("--max-tokens", type=int, default=None, help="default: frozen4.json cap (16,384)")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", required=True, help="the submitted commit: $(git rev-parse HEAD), expanded on the laptop")
    a = ap.parse_args()
    t0 = time.time()
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    assert 1 <= a.draws < 100, "seeds of two draws would collide (10,000 * j + i, i < 500)"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "openings.jsonl").exists(), f"{out} holds a run: one fresh directory per run"
    assert self_opens(".\n\nOkay, so") and not self_opens(" Okay, so") and not self_opens("x" * 56 + "\nOkay"), "self-open test"

    fz = json.loads((RC.D4 / "frozen4.json").read_text())
    cap = a.max_tokens or fz["cap"]
    assert a.open_tokens < cap
    probs = RC.problems("math500", fz)
    frozen = json.loads((THEORY / "data" / "selfopen01_t3.json").read_text())
    todo = frozen["regenerate"][: a.n]
    assert all(int(probs[i]["index"]) == i for i in todo)
    versions = {k: metadata.version(k) for k in RC.PINS if k != "vllm" or not a.dry_run}
    if not a.dry_run:
        assert versions == RC.PINS, f"package versions {versions} differ from the study's {RC.PINS}: run setup_vllm.sh first"
    repo, _, rev = fz["models"]["base"]
    m = {"status": "starting", "config": {**vars(a), "max_tokens": cap, "model_repo": repo, "model_revision": rev, "tokenizer": fz["tokenizer"],
                                         "sampling": SAMPLING, "seed_rule": "47,000,000 + index + 10,000 * draw", "n_problems": len(todo),
                                         "self_open_test": frozen["test"], "t3_sha256": frozen["sha256"]},
         "commit": a.commit, "job_id": os.environ.get("JOB_ID"), "versions": versions, "started_utc": J.utc()}

    def write():
        m["updated_utc"] = J.utc()
        G.dump(out / "metrics.json", m)

    write()
    from huggingface_hub import snapshot_download
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(tok_dir)
    pids_all = [S.render_ids(tok, p["problem"]) for p in probs]
    n13 = json.loads((RC.D4 / "prompt_ids.json").read_text())
    assert n13["pair"] == "pair1" and pids_all == n13["ids"], "G-TEMPLATE: MATH-500 prompt ids differ from n13's"

    t_load = time.time()
    live_gold = {}
    if a.dry_run:
        engine, model_dir = RC.Canned(tok, live_gold), None
    else:
        model_dir = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
        os.environ.update(G.ENGINE_ENV)
        engine = J.VllmEngine(model_dir, tok_dir, 2048 + cap)
    m["engine"] = {**engine.info, "load_s": time.time() - t_load, "model_dir": model_dir, "tok_dir": tok_dir}
    m["status"] = "openings"
    write()

    def req(i, j, ids_after_prompt, max_tokens, kind):
        r = {"rid": f"{kind}|{i}|{j}", "cell": f"selfopen_{kind}", "bench": "math500", "idx": i, "sample": j, "uid": probs[i]["unique_id"],
             "ids": pids_all[i] + ids_after_prompt, "n_prompt": len(pids_all[i]), "prefix_ids": ids_after_prompt,
             "prefix_kind": "own_opening" if ids_after_prompt else "none", "seed": SEED_BASE + i + 10_000 * j, "sampling": SAMPLING,
             "max_tokens": max_tokens, "gold": probs[i]["answer"]}
        live_gold[r["rid"]] = r
        return r

    # 1. openings
    opens = {}
    t_open = time.time()
    with open(out / "openings.jsonl", "a") as f:
        def on_open(r, out_ids, lps, fr):
            live_gold.pop(r["rid"])
            stop = S.STOP_ID in out_ids
            ids = out_ids[: out_ids.index(S.STOP_ID)] if stop else list(out_ids)
            text = tok.decode(ids, skip_special_tokens=False)
            row = {"problem_index": r["idx"], "draw": r["sample"], "seed": r["seed"], "ids": ids, "text": text, "finished": stop,
                   "finish_reason": fr, "self_open": self_opens(text), "out_ids": list(out_ids), "lps": list(lps)}
            opens[(r["idx"], r["sample"])] = row
            f.write(json.dumps({k: v for k, v in row.items() if k not in ("out_ids", "lps")}) + "\n")
        run_queue(engine, [req(i, j, [], a.open_tokens, "open") for i in todo for j in range(1, a.draws + 1)], on_open)
    m["openings"] = {"n": len(opens), "seconds": time.time() - t_open, "self_open": sum(o["self_open"] for o in opens.values()),
                     "finished_within_open_tokens": sum(o["finished"] for o in opens.values())}

    # 2. choices
    choices = {}
    for i in todo:
        so = [j for j in range(1, a.draws + 1) if opens[(i, j)]["self_open"]]
        no = [j for j in range(1, a.draws + 1) if not opens[(i, j)]["self_open"]]
        choices[i] = {"main": so[0] if so else 1, "control": no[0] if no else 1, "any_self_open": bool(so),
                      "draws_used_main": so[0] if so else a.draws, "n_self_open_of_draws": len(so)}
    G.dump(out / "choices.json", {str(i): c for i, c in choices.items()})
    m["status"] = "continuations"
    write()

    # 3. continuations
    need = {}
    for i, c in choices.items():
        for arm in ("main", "control"):
            need.setdefault((i, c[arm]), []).append(arm)
    c = {"n": 0, "cap_hits": 0, "generated_tokens": 0, "correct_v3": {"main": 0, "control": 0}}
    t_gen = time.time()
    with open(out / "answers.jsonl", "a") as f:
        def emit(r, out_ids, lps, fr, o):
            rec = J.record(tok, r, out_ids, lps, fr)
            rec.update(R.grade_v3(r["gold"], rec["text"]))
            arms = need[(r["idx"], r["sample"])]
            rec.update(draw=r["sample"], arms=arms, opening_self_open=o["self_open"], opening_text=o["text"],
                       final_self_open=self_opens(rec["text"]), any_self_open=choices[r["idx"]]["any_self_open"],
                       prompt=tok.decode(r["ids"][: r["n_prompt"]], skip_special_tokens=False))
            f.write(json.dumps(rec) + "\n")
            f.flush()
            os.fsync(f.fileno())
            c["n"] += 1
            c["cap_hits"] += int(rec["cap_hit"])
            c["generated_tokens"] += rec["n_answer_tokens"]
            for arm in arms:
                c["correct_v3"][arm] += rec["score_v3"]
            sec = time.time() - t_gen
            m["counts"] = {**c, "n_planned": len(need), "generation_s": sec, "tokens_per_s": c["generated_tokens"] / max(sec, 1e-9)}
            write()

        reqs = []
        for (i, j) in need:
            o = opens[(i, j)]
            if o["finished"]:               # the draw ended inside the opening: it is the whole answer
                emit(req(i, j, [], a.open_tokens, "open"), o["out_ids"], o["lps"], o["finish_reason"], o)
                live_gold.pop(f"open|{i}|{j}")
            else:
                reqs.append(req(i, j, o["ids"], cap - len(o["ids"]), "cont"))

        def on_cont(r, out_ids, lps, fr):
            live_gold.pop(r["rid"])
            emit(r, out_ids, lps, fr, opens[(r["idx"], r["sample"])])
        run_queue(engine, reqs, on_cont)
    assert c["n"] == len(need)
    m["memory"] = engine.memory()
    m["status"] = "done"
    m["wall_s"] = time.time() - t0
    write()
    print(json.dumps({k: m[k] for k in ("status", "openings", "counts", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
