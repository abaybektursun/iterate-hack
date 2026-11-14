"""RLN-3 offline gate (SPEC3 §5): the job's child (studies/rlneurons/jobs/rln3_gen.run) and the readout (rln3_analyze) end to end on the
laptop, with a stand-in engine in place of the model forward. No weights, no GPU.

    python -m studies.rlneurons.prep.rln3_offline --n13 <dir: base_math500.jsonl, rl_math500.jsonl, prompt_ids.json> --tok <RL 3.1 tokenizer dir>
        --work <scratch dir>

The stand-in answers each request from n13's saved MATH-500 texts (base texts for base, s0100, s0400 and fr; RL texts for s2800),
re-tokenized; harder-set problem i gets saved text i mod 500; a saved cap hit returns max_tokens ids with finish "length"; a commit
request (max_tokens 100) returns "42}" and the stop id. It checks every request it receives:
  - P requests are the n13 prompt ids (MATH-500) or the rendered prompt; F requests are the same ids plus the frozen prefill ids;
  - a commit request is the parent's request ids + the parent's first N generated ids + the commit ids, and is sent only for a
    parent not finished within N tokens.
Runs, each must end as stated:
  1. base with --check base on base texts: check passes (57.2 = n13).        2. s2800 with --check s2800 on RL texts: passes (92.0).
  3. s0100, s0400, fr on base texts, no check.                                 4. failing input: base with --check base on RL texts
     stops with exit 3 and check.json pass false.
  5. the sample rule: a small allowance gives one MATH-500 sample and one harder-set sample.
  6. failing inputs of the commit and prefill checks: a commit request with N+1 tokens, and an F request without the prefill, raise.
  7. rln3_analyze on runs 1-3: status COMPLETE, every gate passes; on a bank with one record removed: G-COMPLETE fails.
Writes studies/rlneurons/results/rln3/offline/offline_gate.json. Fail loud: no try/except except where a failing input must raise.
"""
import argparse
import json
import pathlib
import shutil
import types

import numpy as np

from studies.rlneurons.jobs import rln3_gen as J
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.analysis import rln3_analyze as AN

STUDY = pathlib.Path(__file__).resolve().parents[1]      # studies/rlneurons
INPUTS = STUDY / "data" / "rln3"
OFFLINE = STUDY / "results" / "rln3" / "offline"


class Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t


class Fake:
    info = {"vllm": None, "fake": True}

    def __init__(self, tok, texts, fz, inputs, clock, per_step=64, dt=1.0):
        self.tok, self.fz, self.clock, self.per_step, self.dt = tok, fz, clock, per_step, dt
        self.ids = [tok(r["text"], add_special_tokens=False)["input_ids"] for r in texts]
        self.caphit = [r["cap_hit"] for r in texts]
        probs = {b: json.loads((inputs / f"{b}.json").read_text()) for b in ("math500", "hard")}
        self.prompt = {b: [S.render_ids(tok, p["problem"]) for p in probs[b]] for b in probs}
        self.queue, self.sent, self.n_commit = [], {}, 0

    def canned(self, idx, max_tokens):
        x = self.ids[idx % 500]
        if self.caphit[idx % 500]:
            return (x * (max_tokens // max(len(x), 1) + 1))[:max_tokens], "length"
        if len(x) >= max_tokens:
            return x[:max_tokens], "length"
        return x + [S.STOP_ID], "stop"

    def check(self, rid, ids, max_tokens):
        cell, bench, s, idx = rid.split("|")
        idx = int(idx)
        p = self.prompt[bench][idx]
        if cell == "P":
            assert ids == p, f"{rid}: a P request is not the prompt"
        elif cell == "F":
            assert ids == p + self.fz["prefill_ids"], f"{rid}: an F request is not prompt + prefill"
        else:
            parent = self.sent[f"{cell[1:]}|{bench}|{s}|{idx}"]
            gen, _ = self.canned(idx, self.fz["cap"])
            assert not (gen[-1] == S.STOP_ID and len(gen) <= self.fz["N"]), f"{rid}: commit sent for an answer finished within N"
            want = parent + gen[: self.fz["N"]] + self.fz["commit_ids"]
            assert ids == want, f"{rid}: the commit request is not parent + first N + commit"
            assert max_tokens == self.fz["commit_max_tokens"]

    def add(self, rid, ids, seed, max_tokens):
        self.check(rid, ids, max_tokens)
        if rid[0] in "PF":
            self.sent[rid] = ids
        else:
            self.n_commit += 1
        self.queue.append((rid, max_tokens))

    def step(self):
        self.clock.t += self.dt
        done, self.queue = self.queue[: self.per_step], self.queue[self.per_step:]
        res = []
        for rid, mt in done:
            if rid[0] == "C":
                ids, fr = self.tok("42}", add_special_tokens=False)["input_ids"] + [S.STOP_ID], "stop"
            else:
                ids, fr = self.canned(int(rid.split("|")[3]), mt)
            res.append((rid, ids, list(np.full(len(ids), -0.1)), fr))
        return res

    def has_unfinished(self):
        return bool(self.queue)

    def memory(self):
        return {"gpu": "fake"}


def run_one(work, name, model, check, texts, tok, fz, inputs, allowance_min):
    out = work / name
    if out.exists():
        shutil.rmtree(out)
    clock = Clock()
    holder = {}

    def factory(model_dir, tok_dir, cap, tk):
        holder["e"] = Fake(tok, texts, fz, inputs, clock)
        return holder["e"]

    a = types.SimpleNamespace(out=str(out), model=model, check=check, inputs_dir=str(inputs), tok_dir=TOK, model_dir="(fake)",
                              allowance_min=allowance_min, t0=None)
    m = J.run(a, engine_factory=factory, clock=clock)
    return m, holder["e"]


TOK = None


def main():
    global TOK
    ap = argparse.ArgumentParser()
    ap.add_argument("--n13", required=True)
    ap.add_argument("--tok", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    TOK = a.tok
    n13, work = pathlib.Path(a.n13), pathlib.Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    inputs = work / "inputs"
    inputs.mkdir(exist_ok=True)
    for f in ("frozen.json", "math500.json", "hard.json"):
        shutil.copy(INPUTS / f, inputs / f)
    shutil.copy(n13 / "prompt_ids.json", inputs / "prompt_ids.json")
    fz = json.loads((inputs / "frozen.json").read_text())
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok)
    texts = {m: sorted((json.loads(l) for l in open(n13 / f"{m}_math500.jsonl")), key=lambda r: r["problem_index"]) for m in ("base", "rl")}
    rec = {}
    banks = work / "banks"
    allow = 17.5          # fake minutes; with 1 s per engine step this allows samples 1-3 of MATH-500 and some harder-set samples
    for model, check, src in (("base", "base", "base"), ("s2800", "s2800", "rl"), ("s0100", None, "base"), ("s0400", None, "base"),
                              ("fr", None, "base")):
        m, e = run_one(banks, model, model, check, texts[src], tok, fz, inputs, allow)
        rec[model] = {"status": m["status"], "plan": m["plan"], "check": m.get("check"), "n_commit_requests": e.n_commit,
                      "stages": [(s["name"], s["n_requests"]) for s in m["stages"]]}
        assert m["status"] == "done"
    assert rec["base"]["check"]["pass"] and rec["base"]["check"]["correct"] == 286, rec["base"]["check"]
    assert rec["s2800"]["check"]["pass"] and rec["s2800"]["check"]["correct"] == 460, rec["s2800"]["check"]
    # 4. failing input of the check
    code = None
    try:
        run_one(work / "fail", "check_fail", "base", "base", texts["rl"], tok, fz, inputs, allow)
    except SystemExit as e:
        code = e.code
    chk = json.loads((work / "fail" / "check_fail" / "check.json").read_text())
    rec["check_failing_input"] = {"exit": code, "check_pass": chk["pass"], "acc": chk["acc"], "failed": code == 3 and not chk["pass"]}
    # 5. the sample rule with a small allowance
    m, _ = run_one(work / "small", "small", "s0100", None, texts["base"], tok, fz, inputs, 15.5)
    rec["sample_rule_small_allowance"] = {"plan": m["plan"], "pass": m["plan"]["math500"] == 1 and m["plan"]["hard"] == 1}
    # 6. failing inputs of the request checks
    e = Fake(tok, texts["base"], fz, inputs, Clock())
    p0 = e.prompt["math500"][0]
    fails = {}
    try:
        e.add("F|math500|0|0", p0, 0, fz["cap"])
        fails["F_without_prefill"] = False
    except AssertionError:
        fails["F_without_prefill"] = True
    cap_idx = next(i for i in range(500) if e.caphit[i])
    pa = e.prompt["math500"][cap_idx]
    e.add(f"P|math500|0|{cap_idx}", pa, 0, fz["cap"])
    gen, _ = e.canned(cap_idx, fz["cap"])
    try:
        e.add(f"CP|math500|0|{cap_idx}", pa + gen[: fz["N"] + 1] + fz["commit_ids"], 0, fz["commit_max_tokens"])
        fails["commit_N_plus_1"] = False
    except AssertionError:
        fails["commit_N_plus_1"] = True
    e.add(f"CP|math500|0|{cap_idx}", pa + gen[: fz["N"]] + fz["commit_ids"], 0, fz["commit_max_tokens"])
    rec["request_failing_inputs"] = fails
    # 7. the readout
    v = AN.verdict(banks, inputs)
    rec["analyze"] = {"status": v["status"], "gates": v["gates"], "instrument": {k: v["instrument"][k] for k in ("identity_pass", "planted_pass")},
                      "samples_used": v["samples_used"], "base_math500_P_acc": v["cells"]["base|math500|P"]["acc"],
                      "s2800_math500_P_acc": v["cells"]["s2800|math500|P"]["acc"], "labels": v["outcomes"]["labels"]}
    cut = work / "banks_cut"
    if cut.exists():
        shutil.rmtree(cut)
    shutil.copytree(banks, cut)
    lines = (cut / "fr" / "P_hard.jsonl").read_text().splitlines()
    (cut / "fr" / "P_hard.jsonl").write_text("\n".join(l for l in lines if not ('"sample": 0' in l and '"problem_index": 7,' in l)) + "\n")
    vc = AN.verdict(cut, inputs)
    rec["analyze_failing_input"] = {"what": "fr P_hard sample 0 problem 7 removed", "G-COMPLETE": vc["gates"]["G-COMPLETE"],
                                    "failed": not vc["gates"]["G-COMPLETE"]["pass"]}
    rec["pass"] = bool(rec["check_failing_input"]["failed"] and rec["sample_rule_small_allowance"]["pass"] and all(fails.values())
                       and v["status"] == "COMPLETE" and rec["analyze_failing_input"]["failed"])
    (OFFLINE).mkdir(parents=True, exist_ok=True)
    (OFFLINE / "offline_gate.json").write_text(json.dumps(rec, indent=1, default=str))
    print(json.dumps(rec, indent=1, default=str))
    assert rec["pass"], "RLN-3 offline gate failed"
    print("RLN3_OFFLINE_OK", flush=True)


if __name__ == "__main__":
    main()
