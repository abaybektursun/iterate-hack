"""Shared code of the tinkerpair study: the model, the prompt, the opening cue, sampling on Tinker, the run record.

The prompt template and grader v3 are imported from studies/rlneurons, so both pairs are scored by the same code.
Fail-loud: no try/except, no fallback.
"""
import datetime
import json
import os
import subprocess
import sys

import tinker
from tinker import types

from studies.rlneurons.lib import n13_score as S

MODEL = "Qwen/Qwen3.5-9B-Base"
CUE = " line!\n\nOkay"          # the text of the Olmo pair's cue (rlneurons data/rln4/frozen4.json prefill_text), not tuned here
T, TOP_P = 1.0, 1.0
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STUDY = os.path.join(ROOT, "studies", "tinkerpair")
RAW = os.path.join(ROOT, "runs", "tinkerpair")       # raw generations, not committed


def prompt_ids(tok, problem: str, cue: bool) -> list:
    """Token ids of the prompt; with the cue, its ids follow the prompt's ids (encoded apart, as in the Olmo harness)."""
    ids = tok.encode(S.TEMPLATE["pair1"].format(problem=problem), add_special_tokens=False)
    return ids + (tok.encode(CUE, add_special_tokens=False) if cue else [])


def sampler(service, model_path):
    """A sampling client of the untrained base (model_path None) or of a saved checkpoint."""
    if model_path:
        return service.create_sampling_client(model_path=model_path).result()
    return service.create_sampling_client(base_model=MODEL).result()


def sample(client, tok, prompts: list, n: int, cap: int, seed: int) -> list:
    """n samples for every prompt (a list of id lists). Request i uses seed + i. Every request is submitted before any
    result is read. Returns, per prompt, n dicts: tokens and logprobs as sampled, the decoded text without the stop
    token, and cap (True when the answer reached `cap` tokens without the stop token)."""
    stop = tok.eos_token_id
    assert stop is not None
    futs = [client.sample(prompt=types.ModelInput.from_ints(p), num_samples=n,
                          sampling_params=types.SamplingParams(max_tokens=cap, temperature=T, top_p=TOP_P, seed=seed + i,
                                                               stop=[stop]))
            for i, p in enumerate(prompts)]
    out = []
    for f in futs:
        seqs = []
        for s in f.result().sequences:
            body = s.tokens[:-1] if s.tokens and s.tokens[-1] == stop else s.tokens
            seqs.append({"tokens": s.tokens, "logprobs": s.logprobs, "text": tok.decode(body), "cap": s.stop_reason == "length"})
        out.append(seqs)
    return out


def answer_text(text: str, cue: bool) -> str:
    """The answer that is graded and saved: with the cue, the cue is the start of the answer."""
    return (CUE + text) if cue else text


def load_set(name: str) -> list:
    """math500: the 500 problems. hard328: the 328 harder problems absent from the Dolci RL prompts."""
    d = os.path.join(ROOT, "studies", "rlneurons")
    if name == "math500":
        return json.load(open(f"{d}/data/rln4/math500.json"))
    assert name == "hard328", name
    flags = json.load(open(f"{d}/results/rln3/rln3_overlap.json"))["sets"]["hard"]["flags"]
    hard = json.load(open(f"{d}/data/rln3/hard.json"))
    return [h for h in hard if flags[str(h["index"])]["flag"] == "none"]


def new_run_dir(rel: str) -> tuple:
    """Creates results/<rel> and runs/tinkerpair/<rel>; fails when the result folder exists (a rerun gets the next number)."""
    res, raw = os.path.join(STUDY, "results", rel), os.path.join(RAW, rel)
    os.makedirs(res)
    os.makedirs(raw, exist_ok=True)
    return res, raw


def run_record(extra: dict) -> dict:
    return {"commit": subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip(),
            "dirty": bool(subprocess.check_output(["git", "-C", ROOT, "status", "--porcelain", "--untracked-files=no"], text=True).strip()),
            "command": "python -m " + " ".join(sys.argv), "runner": f"tinker {tinker.__version__} (hosted, laptop client)",
            "model": MODEL, "temperature": T, "top_p": TOP_P,
            "started_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **extra}


def dump(path: str, obj) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")
