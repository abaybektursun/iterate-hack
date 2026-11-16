"""drive-01 (specs/SPEC_direct_drive.md): trace-01's drive of the top-8 input subspaces, on the base's 538 Code-cue answers of
HumanEval+/MBPP+, plus 16 of trace-01's math answers to check that its stored values reproduce. Teacher forcing through the
BASE model, no generation. The trace itself (vectors, hooks, r, selftest) is imported from studies/rlneurons/jobs/xreward_trace.py.

    python -m studies.theory.jobs.drive_trace --commit <full sha>            smoke: add --n-code 4 --n-math 2

Per answer and condition (CONDS of xreward_trace), r is band-averaged per position and stored in float16 as trace-01 does; the
job writes the per-answer mean over positions of each [module, band, condition] cell (computed from those float16 values).

Outputs in --out (default $OUT_DIR): rows.jsonl (one row per traced answer: domain, id, n, cap_hit, passed or score, D[mod][band][cond]),
run.json, metrics.json (selftest, counts, left-out rows, per-domain means). Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import pathlib
import re
import sys
import time

import numpy as np
import torch

from studies.rlneurons.jobs import xreward_trace as X
from studies.rlneurons.jobs.wsp_delta_anatomy import dump, index, kind, load, order, spectrum, utc
from studies.rlneurons.jobs.xreward_overlap import MODELS
from studies.rlneurons.lib import code_lib as C

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = ROOT / "studies" / "theory" / "data" / "drive"
RLN = ROOT / "studies" / "rlneurons" / "data"
CODE_FILE, CODE_SHA = DATA / "code_cue_answers_v1.jsonl.gz", "0a5b412218c82635e6c0ac3ae53f36feb24a159ab324e6ac0e42c24b70f55f03"
MATH_FILE = DATA / "math_check_v1.jsonl.gz"


def read_gz(path):
    b = gzip.decompress(path.read_bytes())
    return hashlib.sha256(b).hexdigest(), [json.loads(l) for l in b.decode().splitlines()]


def build_code(tok, row, max_tokens):
    """The traced sequence of one stored code answer, rendered as run_code_cell.py rendered its prompt."""
    head, tail = C.TEMPLATE.split("{content}")
    p = row["prompt"]
    assert p.startswith(head) and p.endswith(tail), ("prompt template", row["uid"])
    msg = [{"role": "user", "content": p[len(head):len(p) - len(tail)]}]
    assert tok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True) == p, ("prompt render", row["uid"])
    pids = [int(i) for i in tok.apply_chat_template(msg, tokenize=True, add_generation_prompt=True, return_dict=False)]
    pre = row["prefix_ids"]
    pre_text = tok.decode(pre)
    assert row["text"].startswith(pre_text), ("opening cue", row["uid"])
    ids = list(pre) + tok(row["text"][len(pre_text):], add_special_tokens=False)["input_ids"]
    n = min(len(ids), max_tokens)
    return {"domain": "code", "id": row["uid"], "bench": row["bench"], "seq": pids + [int(i) for i in ids[:n]], "n_prompt": len(pids),
            "n": n, "n_full": len(ids), "cap_hit": bool(row["cap_hit"]), "passed": bool(row["passed"]),
            "retok_diff": len(ids) - len(pre) - int(row["n_new"]), "n_new": int(row["n_new"])}


def build_math(tok, fz, hard, row, max_tokens):
    s = X.build(tok, fz, row, hard[row["problem_index"]], max_tokens)
    return {**s, "domain": "math", "id": s["idx"], "passed": s["score"] == 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", default=os.environ.get("OUT_DIR"))
    ap.add_argument("--n-code", type=int, default=None, help="smoke: the first n code rows")
    ap.add_argument("--n-math", type=int, default=None, help="smoke: the first n math check rows")
    ap.add_argument("--max-tokens", type=int, default=6000)
    a = ap.parse_args()
    t0 = time.time()
    torch.set_grad_enabled(False)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    st = X.selftest(dev)
    assert a.out, "no --out and no $OUT_DIR"
    assert re.fullmatch(r"[0-9a-f]{40}", a.commit), f"--commit {a.commit!r} is not a full git sha"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "rows.jsonl").exists(), f"{out}/rows.jsonl exists: one fresh directory per run"
    keys = ("base",) + X.DONORS
    code_sha, code_rows = read_gz(CODE_FILE)
    math_sha, math_rows = read_gz(MATH_FILE)
    assert code_sha == CODE_SHA, f"{CODE_FILE}: sha256 {code_sha}"
    assert len(code_rows) == 538 and len(math_rows) == 16
    info = {"status": "running", "commit": a.commit, "command": "python -m studies.theory.jobs.drive_trace " + " ".join(sys.argv[1:]),
            "job_id": os.environ.get("JOB_ID"), "models": {k: {"repo": MODELS[k][0], "revision": MODELS[k][1]} for k in keys},
            "inputs": {str(CODE_FILE.relative_to(ROOT)): code_sha, str(MATH_FILE.relative_to(ROOT)): math_sha},
            "torch": torch.__version__, "device": torch.cuda.get_device_name(0), "started_utc": utc(), "selftest": st}
    dump(out / "run.json", info)

    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer

    def tokenizer(spec):
        return AutoTokenizer.from_pretrained(snapshot_download(spec[0], revision=spec[1], allow_patterns=["*.json", "*.jinja", "*.txt"]))

    fz_code = json.loads((RLN / "code1" / "frozen_code1.json").read_text())
    fz_math = json.loads((RLN / "rln4" / "frozen4.json").read_text())
    hard = json.loads((RLN / "rln3" / "hard.json").read_text())
    tok_code, tok_math = tokenizer(fz_code["tokenizer"]), tokenizer(fz_math["tokenizer"])
    seqs = [build_code(tok_code, r, a.max_tokens) for r in code_rows[:a.n_code]]
    seqs += [build_math(tok_math, fz_math, hard, r, a.max_tokens) for r in math_rows[:a.n_math]]
    left_out = [(s["domain"], s["id"]) for s in seqs if abs(s["retok_diff"]) > X.TOL * s["n_new"]]
    seqs = [s for s in seqs if (s["domain"], s["id"]) not in left_out]
    print(f"{len(seqs)} answers, {sum(s['n'] for s in seqs)} positions, left out (re-tokenized count off by over 1 %): {left_out}", flush=True)

    dirs = {k: snapshot_download(MODELS[k][0], revision=MODELS[k][1], allow_patterns=["*.safetensors", "*.json"]) for k in keys}
    idx = index(dirs)
    names = [n for n in sorted(idx["base"], key=order) if kind(n)[0] in X.MODS]
    assert len(names) == 32 * len(X.MODS), len(names)
    P = {}
    for i, name in enumerate(names):                        # the vectors of xreward_trace.main, built the same way
        base = load(idx, "base", name, dev).float()
        cols = {}
        for k in X.DONORS:
            s, _, V = spectrum(load(idx, k, name, dev).float() - base)
            cols[k] = X.scaled(s, V)
            if k == "math31":
                for j in range(3):
                    cols[f"rand{j}"] = X.scaled(s, X.rand_v(V.shape[0], j, name).to(dev))
        P[name] = torch.cat([cols[c] for c in X.CONDS], 1)
        if (i + 1) % 16 == 0:
            print(f"[{i + 1}/{len(names)}] vectors of {name}, {time.time() - t0:.0f}s", flush=True)
    del base

    model = AutoModelForCausalLM.from_pretrained(dirs["base"], dtype=torch.bfloat16).to(dev).eval()
    tr = X.Trace(model, P)
    info.update(load_s=time.time() - t0, transformers=__import__("transformers").__version__)
    dump(out / "run.json", info)

    t_run, npos = time.time(), 0
    with open(out / "rows.jsonl", "w") as f:
        for i, s in enumerate(seqs):
            model(input_ids=torch.tensor(s["seq"][:-1], device=dev)[None], use_cache=False)
            r = {m: v[s["n_prompt"] - 1:] for m, v in tr.pop().items()}                    # [n, 32, C]
            assert all(v.shape == (s["n"], 32, len(X.CONDS)) and torch.isfinite(v).all() for v in r.values()), ("shape or non-finite", s["id"])
            D = {m: np.stack([v[:, lo:hi].mean(1).cpu().numpy().astype(np.float16) for lo, hi in X.BANDS], 1).astype(np.float64).mean(0).tolist()
                 for m, v in r.items()}                                                    # [band][cond]
            row = {k: s[k] for k in ("domain", "id", "n", "n_full", "n_prompt", "cap_hit", "passed")}
            f.write(json.dumps({**row, "bench": s.get("bench"), "D": D}) + "\n")
            f.flush()
            npos += s["n"]
            if (i + 1) % 50 == 0:
                print(f"{utc()} {i + 1}/{len(seqs)} answers, {npos} positions in {time.time() - t_run:.0f} s", flush=True)

    rows = [json.loads(l) for l in (out / "rows.jsonl").read_text().splitlines()]
    mean = {d: {c: float(np.mean([np.mean([x["D"][m][b][j] for m in X.MODS for b in range(len(X.BANDS))]) for x in rows if x["domain"] == d]))
                for j, c in enumerate(X.CONDS)} for d in ("code", "math") if any(x["domain"] == d for x in rows)}
    metrics = {"answers": {d: sum(x["domain"] == d for x in rows) for d in ("code", "math")}, "positions": npos, "left_out": left_out,
               "max_tokens": a.max_tokens, "conds": X.CONDS, "bands": X.BANDS, "mods": X.MODS,
               "what": "per answer D = mean over positions of mean over mods and bands of r = ||diag(s) V^T x|| / ||W_base x||; mean over answers",
               "mean_D": mean, "gpu_max_memory_gb": torch.cuda.max_memory_allocated() / 2 ** 30,
               "positions_per_s": npos / (time.time() - t_run), "selftest": st}
    dump(out / "metrics.json", metrics)
    info.update(status="done", ended_utc=utc(), wall_s=time.time() - t0)
    dump(out / "run.json", info)
    print(json.dumps(mean, indent=1), flush=True)


if __name__ == "__main__":
    main()
