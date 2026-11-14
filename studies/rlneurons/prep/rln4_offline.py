"""RLN-4 offline gate (SPEC4 §7): the job's child (studies/rlneurons/jobs/rln4_gen.run) end to end on the laptop with a stand-in engine.
No weights, no GPU.

    python -m studies.rlneurons.prep.rln4_offline --n13 <dir> --b01 <dir> --tok <RL 3.1 tokenizer dir> --work <scratch dir>

The stand-in answers a request for MATH-500 problem i from saved texts: T2 from n13's RL answers, T3 from base-01 P, every other base
cell from base-01 F (G row r from base-01 F answer r mod 500); a saved cap hit returns max_tokens ids with finish "length". It checks
every request: prompt ids = n13's ids (MATH-500) or the rendered Dolci prompt, then the cell's prefix (opening, RL prefix, own
prefix, none); sampling, seed and max_tokens as frozen4.json says; K_fresh2 only after a K_fresh cap hit.
Runs (each must end as stated):
  1. base1 on base-01 texts: check pass (50 of 50 equal), T1 500, K_rl and K_own one per K problem, K_fresh one per restart problem,
     K_fresh2 one per K_fresh cap hit.                   2. rl: T2 500.
  3. base2 with time to spare: G 1,000 prompts x 4, then R1 500 and T3 500.
  4. base2 with the G submission stop 20 stand-in minutes after the start: G stops early, R1 and T3 dropped.
  5. base1 started 2 stand-in minutes before the hard stop: requests aborted and listed, exit normal.
  6. failing inputs: base1 served empty answers -> check verdict "stop" (exit 3); a request with a wrong seed, a wrong prefix and a wrong
     max_tokens each raise in the stand-in.
  7. rl_check (Modal): RL check 50 of 50 on n13's RL texts, then T2 500.  8. t3 (Modal): T3 500.
  9. rl_check served empty answers -> verdict "stop", exit 3, no T2 file.
Writes studies/rlneurons/results/rln4/offline/offline_gate.json. Fail loud: no try/except except where a failing input must raise.
"""
import argparse
import json
import pathlib
import shutil
import types

from studies.rlneurons.jobs import rln4_gen as J
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]      # studies/rlneurons
INPUTS = STUDY / "data" / "rln4"
OFFLINE = STUDY / "results" / "rln4" / "offline"


class Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


class Fake:
    info = {"vllm": None, "fake": True}

    def __init__(self, tok, fz, texts, clock, per_step=40, dt=1.0, mode="good", tamper=None):
        self.tok, self.fz, self.texts, self.clock, self.per_step, self.dt, self.mode, self.tamper = tok, fz, texts, clock, per_step, dt, mode, tamper
        ind = INPUTS
        self.n13 = json.loads((ind / "prompt_ids.json").read_text())["ids"]
        k = json.loads((ind / "k.json").read_text())
        self.k = {r["problem_index"]: r for r in k["rows"]}
        self.restart = set(k["restart"])
        self.g = {r["row"]: r for r in json.loads((ind / "g.json").read_text())}
        self.queue, self.seen, self.capped_fresh = [], {}, set()
        self.ids = {name: {i: tok(t[len(fz["prefill_text"]):] if t.startswith(fz["prefill_text"]) else t, add_special_tokens=False)["input_ids"]
                           for i, (t, c) in v.items()} for name, v in texts.items()}

    def add(self, rid, ids, sampling, seed, max_tokens):
        cell, i, s = rid.split("|")
        i, s = int(i), int(s)
        fz = self.fz
        model, arm, samp = fz["cells"][cell]
        assert sampling == samp, (rid, sampling, samp)
        if self.tamper == "seed":
            seed += 1
        if self.tamper == "prefix" and cell == "K_rl":
            ids = ids[:-1]
        if self.tamper == "max_tokens" and cell == "K_own":
            max_tokens += 1
        if cell == "G":
            pfx = fz["prefill_ids"]
            p = S.render_ids(self.tok, self.g[i]["prompt"])
            assert ids == p + pfx, rid
            assert seed == fz["seeds"]["G"] + s * fz["seeds"]["G_per_sample"] + i, rid
            assert max_tokens == fz["g"]["cap"], rid
        else:
            pfx = {"K_rl": self.k.get(i, {}).get("rl_prefix_ids"), "K_own": self.k.get(i, {}).get("own_prefix_ids")}.get(
                cell, fz["prefill_ids"] if arm == "F" else [])
            assert pfx is not None, rid
            assert ids == self.n13[i] + pfx, f"{rid}: request ids differ from n13 prompt + prefix"
            assert seed == fz["seeds"][cell] + i, f"{rid}: seed {seed}"
            want_mt = fz["cap"] - len(pfx) if cell.startswith("K_") else fz["cap"]
            assert max_tokens == want_mt, f"{rid}: max_tokens {max_tokens} != {want_mt}"
            if cell in ("K_rl", "K_own"):
                assert i in self.k and 300 <= len(pfx) <= 2500, rid
            if cell == "K_fresh":
                assert i in self.restart, rid
            if cell == "K_fresh2":
                assert i in self.capped_fresh, f"{rid}: K_fresh2 without a K_fresh cap hit"
        assert rid not in self.seen, f"{rid} sent twice"
        self.seen[rid] = (seed, max_tokens)
        self.queue.append((rid, cell, i, max_tokens))

    def step(self):
        self.clock.t += self.dt
        done, self.queue = self.queue[: self.per_step], self.queue[self.per_step:]
        res = []
        for rid, cell, i, mt in done:
            src = {"T2": "rl", "T3": "P", "check_rl": "rl"}.get(cell, "F")
            j = i % 500
            ids = self.ids[src][j]
            if self.mode == "empty":
                res.append((rid, [S.STOP_ID], [0.0], "stop"))
                continue
            capped = self.texts[src][j][1]
            if capped or len(ids) >= mt:
                out = (ids * (mt // max(len(ids), 1) + 1))[:mt]
                res.append((rid, out, [-1.0] * len(out), "length"))
                if cell == "K_fresh":
                    self.capped_fresh.add(i)
            else:
                res.append((rid, ids + [S.STOP_ID], [-1.0] * (len(ids) + 1), "stop"))
        return res

    def has_unfinished(self):
        return bool(self.queue)

    def abort(self, rids):
        rids = set(rids)
        self.queue = [q for q in self.queue if q[0] not in rids]

    def memory(self):
        return {"gpu": "NVIDIA RTX PRO 6000 Blackwell Server Edition (stand-in)"}


def run_phase(tok, fz, texts, work, phase, t0, mode="good", tamper=None, shift=0.0, fresh=True, dt=1.0):
    if fresh and work.exists():
        shutil.rmtree(work)
    clock = Clock(t0)
    fake = {}

    def factory(model_dir, tok_dir, ph):
        fake["f"] = Fake(tok, fz, texts, clock, dt=dt, mode=mode, tamper=tamper)
        return fake["f"]
    a = types.SimpleNamespace(out=str(work), inputs_dir=str(INPUTS), tok_dir=TOK, model_dir="fake", phase=phase, time_shift=shift)
    m = J.run(a, engine_factory=factory, clock=clock)
    return m, fake["f"], work


def nlines(p):
    return sum(1 for _ in open(p)) if p.exists() else 0


TOK = None


def main():
    global TOK
    ap = argparse.ArgumentParser()
    ap.add_argument("--n13", required=True)
    ap.add_argument("--b01", required=True)
    ap.add_argument("--tok", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    TOK = a.tok
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok)
    fz = J.with_rl_check(json.loads((INPUTS / "frozen4.json").read_text()))
    jl = lambda p: {r["problem_index"]: (r["text"], r["cap_hit"]) for r in map(json.loads, open(p))}
    texts = {"F": jl(pathlib.Path(a.b01) / "F_math500.jsonl"), "P": jl(pathlib.Path(a.b01) / "P_math500.jsonl"),
             "rl": jl(pathlib.Path(a.n13) / "rl_math500.jsonl")}
    k = json.loads((INPUTS / "k.json").read_text())
    work = pathlib.Path(a.work)
    T8 = J.epoch("2026-11-14T08:00:00Z")
    res = {}

    m, f, w = run_phase(tok, fz, texts, work / "r1", "base1", T8)
    chk = json.loads((w / "check.json").read_text())
    n = {c: nlines(w / f"{c}.jsonl") for c in ("check", "T1", "K_rl", "K_own", "K_fresh", "K_fresh2")}
    capped_fresh = sum(json.loads(l)["cap_hit"] for l in open(w / "K_fresh.jsonl"))
    res["1_base1"] = {"check": chk, "lines": n, "K_fresh_cap_hits": capped_fresh,
                      "pass": chk["verdict"] == "pass" and chk["scores_equal"] == 50 and n["T1"] == 500 and n["K_rl"] == len(k["rows"])
                      and n["K_own"] == len(k["rows"]) and n["K_fresh"] == len(k["restart"]) and n["K_fresh2"] == capped_fresh}
    m, f, w = run_phase(tok, fz, texts, work / "r1", "rl", T8, fresh=False)
    n["T2"] = nlines(w / "T2.jsonl")
    rl_acc = sum(json.loads(l)["score"] for l in open(w / "T2.jsonl"))
    res["2_rl"] = {"T2": n["T2"], "T2_correct": rl_acc, "pass": n["T2"] == 500 and rl_acc == 460}
    m, f, w = run_phase(tok, fz, texts, work / "r3", "base2", T8)
    n3 = {c: nlines(w / f"{c}.jsonl") for c in ("G", "R1", "T3")}
    res["3_base2_full"] = {"lines": n3, "g_prompts": m["phases"]["base2"]["g_prompts_submitted"],
                           "pass": n3 == {"G": 4000, "R1": 500, "T3": 500}}
    g_stop = J.epoch(fz["g_submit_stop_utc"])
    m, f, w = run_phase(tok, fz, texts, work / "r4", "base2", g_stop - 20 * 60, dt=60.0)
    ph = m["phases"]["base2"]
    n4 = {c: nlines(w / f"{c}.jsonl") for c in ("G", "R1", "T3")}
    res["4_base2_short"] = {"lines": n4, "g_prompts": ph["g_prompts_submitted"], "dropped": ph.get("dropped"),
                            "pass": 0 < n4["G"] < 4000 and n4["G"] % 4 == 0 and n4["R1"] == 0 and ph.get("dropped") == ["R1", "T3"]}
    stop = J.epoch(fz["stop_utc"])
    m, f, w = run_phase(tok, fz, texts, work / "r5", "base1", stop - 120, dt=10.0)
    ab = sum(s["n_aborted"] for s in m["phases"]["base1"]["stages"])
    res["5_hard_stop"] = {"aborted": ab, "status": m["phases"]["base1"]["status"], "pass": ab > 0 and m["phases"]["base1"]["status"] == "done"}
    fails = {}
    try:
        run_phase(tok, fz, texts, work / "r6", "base1", T8, mode="empty")
        fails["empty answers stop at the check"] = False
    except SystemExit as e:
        chk6 = json.loads((work / "r6" / "check.json").read_text())
        fails["empty answers stop at the check"] = e.code == 3 and chk6["verdict"] == "stop"
    for t in ("seed", "prefix", "max_tokens"):
        try:
            run_phase(tok, fz, texts, work / f"r7_{t}", "base1", T8, tamper=t)
            fails[f"wrong {t} raises"] = False
        except AssertionError:
            fails[f"wrong {t} raises"] = True
    res["6_failing_inputs"] = {**fails, "pass": all(fails.values())}
    # Modal phases (SPEC4 Deviations): rl_check = RL check on n13's RL texts, then T2; t3 = T3 alone
    m, f, w = run_phase(tok, fz, texts, work / "r8", "rl_check", T8)
    chk8 = json.loads((w / "check_rl.json").read_text())
    n8 = {c: nlines(w / f"{c}.jsonl") for c in ("check_rl", "T2")}
    res["7_rl_check"] = {"check_rl": chk8, "lines": n8, "pass": chk8["verdict"] == "pass" and chk8["scores_equal"] == 50 and n8["T2"] == 500}
    m, f, w = run_phase(tok, fz, texts, work / "r9", "t3", T8)
    res["8_t3"] = {"T3": nlines(w / "T3.jsonl"), "pass": nlines(w / "T3.jsonl") == 500}
    try:
        run_phase(tok, fz, texts, work / "r10", "rl_check", T8, mode="empty")
        res["9_rl_check_empty"] = {"pass": False}
    except SystemExit as e:
        chk10 = json.loads((work / "r10" / "check_rl.json").read_text())
        res["9_rl_check_empty"] = {"exit": e.code, "verdict": chk10["verdict"], "T2_written": (work / "r10" / "T2.jsonl").exists(),
                                   "pass": e.code == 3 and chk10["verdict"] == "stop" and not (work / "r10" / "T2.jsonl").exists()}
    rec = json.loads(open(work / "r1" / "K_rl.jsonl").readline())
    res["sample_record_K_rl"] = {k2: (v if not isinstance(v, str) or len(v) < 200 else v[:200] + "...") for k2, v in rec.items()}
    res["pass"] = all(v["pass"] for k2, v in res.items() if isinstance(v, dict) and "pass" in v)
    (OFFLINE / "offline_gate.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k2: {x: y for x, y in v.items() if x != "check"} if isinstance(v, dict) else v for k2, v in res.items()
                      if k2 != "sample_record_K_rl"}, indent=1))
    assert res["pass"], "RLN-4 offline gate failed"


if __name__ == "__main__":
    main()
