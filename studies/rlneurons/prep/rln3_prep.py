"""RLN-3 inputs and laptop checks (studies/rlneurons/SPEC3.md §2-§5). No model weights, no model forward.

    python -m studies.rlneurons.prep.rln3_prep --n13 <dir with base_math500.jsonl, rl_math500.jsonl, problems.json>
        --raw <dir with the five downloaded benchmark parquet files> --tok <RL 3.1 tokenizer dir>

Writes studies/rlneurons/data/rln3/{math500,hard,frozen}.json and studies/rlneurons/results/rln3/offline/prep_checks.json.
  1. MATH-500 rows from n13's banked problems.json (the same 500 problems and golds n13 graded).
  2. The harder set: AIME 2022-2024, AIME 2025, AMC 23, HMMT Feb 2025 in full; OlympiadBench OE_TO_maths_en_COMP filtered
     (single answer, no unit, no error tolerance) and drawn (seed 0) to bring the set to 400. Any item whose gold does not grade
     equal to itself under n13's grader is dropped and counted.
  3. N = the 95th percentile (numpy linear) of n_new over the finished RL step-2,800 answers in n13's saved MATH-500 generations,
     rounded up to an integer. No accuracy enters it.
  4. Prefill = the most common opening of the RL step-2,800 answers, through the first word of the reasoning (SPEC3 §3).
  5. Grader reproduction: n13's extractor and grader on the saved texts must give 286/500 (base) and 460/500 (RL); a derangement of
     the golds must not.
  6. Loop ratio (zlib of the last 8,000 characters) on the saved cap hits and on the finished answers of 8,000+ characters.
Fail loud: no try/except, no fallback.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import zlib

import numpy as np
import pyarrow.parquet as pq

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]      # studies/rlneurons
INPUTS = STUDY / "data" / "rln3"
OFFLINE = STUDY / "results" / "rln3" / "offline"
HARD_TARGET = 400
SOURCES = {   # name: (HF dataset repo, commit, file in repo, expected rows)
    "aime22_24": ("project-numina/aimo-validation-aime", "13f9e12f613e720c2a2b2f345dd04b998a29494d", "data/train-00000-of-00001.parquet", 90),
    "aime25": ("MathArena/aime_2025", "c94da77eb22bbd6439e62a323bec18493a421302", "data/train-00000-of-00001.parquet", 30),
    "amc23": ("math-ai/amc23", "80815d37005feb82cd7f8fbc6901d5d3eff43057", "test-00000-of-00001.parquet", 40),
    "hmmt25": ("MathArena/hmmt_feb_2025", "6fdc4277120810ff75aa22d2d5489b91f7a262a1", "data/train-00000-of-00001.parquet", 30),
    "olympiad": ("Hothan/OlympiadBench", "91184b52131e7fc9455fef848035173aea8cc01a",
                 "OlympiadBench/OE_TO_maths_en_COMP/OE_TO_maths_en_COMP.parquet", 674),
}
MODELS = {   # name: (repo, branch read from the HF refs API on 2026-11-13, commit)
    "base": ("allenai/Olmo-3-1025-7B", "main", "a81bae42db3975be1671e27b9c9a56da1a9f980f"),
    "s0100": ("allenai/Olmo-3.1-7B-RL-Zero-Math", "step_0100", "0a45720ccbf23c0aa255a28119787538a48dd56b"),
    "s0400": ("allenai/Olmo-3.1-7B-RL-Zero-Math", "step_0400", "897c0ce4b2e39f6802515f3c1a4e1cf53995af78"),
    "s2800": ("allenai/Olmo-3.1-7B-RL-Zero-Math", "main", "364820b002fc8e81d11a81c7fc9dd6b49c83cd05"),
    "fr": ("allenai/Olmo-3-7B-RL-Zero-Math", "main", "dee26a4074b88215cd1326472e1ab14d0259d892"),
}
TOKENIZER = ("allenai/Olmo-3.1-7B-RL-Zero-Math", "364820b002fc8e81d11a81c7fc9dd6b49c83cd05")
COMMIT_TEXT = "\n\nFinal answer: \\boxed{"
COMMIT_MAX = 100
CAP = 16384
SEEDS = {"math500": 1_000_000, "hard": 3_000_000, "per_sample": 10_000}
SAMPLES = {"math500": 4, "hard": 1, "hard_max": 8}
LOOP = {"chars": 8000, "below": 0.10}
NON_ATTEMPT_MAX_TOKENS = 64


def loop_ratio(text: str):
    b = text[-LOOP["chars"]:].encode()
    return len(zlib.compress(b)) / len(b) if b else None


def rows(raw: pathlib.Path, name: str) -> list:
    t = pq.read_table(raw / f"{name}.parquet").to_pylist()
    assert len(t) == SOURCES[name][3], (name, len(t))
    return t


def gold_ok(g: str) -> bool:
    return S.grade(g, g)["score"] == 1


def hard_set(raw: pathlib.Path) -> tuple:
    items, dropped = [], collections.Counter()

    def add(src, sid, problem, answer):
        if not gold_ok(answer):
            dropped[f"{src}: gold does not grade equal to itself"] += 1
            return
        items.append({"source": src, "source_id": str(sid), "problem": problem, "answer": answer})

    for r in rows(raw, "aime22_24"):
        year = r["url"].split("/")[-2][:4]
        assert year in ("2022", "2023", "2024"), r["url"]
        add(f"aime{year}", r["url"].split("/")[-2] + "/" + r["url"].split("/")[-1], r["problem"], str(r["answer"]).strip())
    for r in rows(raw, "aime25"):
        add("aime2025", r["problem_idx"], r["problem"], str(r["answer"]).strip())
    for r in rows(raw, "amc23"):
        a = float(r["answer"])
        add("amc23", r["id"], r["question"], str(int(a)) if a == int(a) else str(a))
    for r in rows(raw, "hmmt25"):
        add("hmmt_feb2025", r["problem_idx"], r["problem"], str(r["answer"]).strip())
    n_comp = len(items)
    pool = []
    for r in rows(raw, "olympiad"):
        fa = r["final_answer"]
        assert isinstance(fa, list), type(fa)
        if r["modality"] != "Text-only" or r["language"] != "English":
            dropped["olympiad: not text-only English"] += 1
        elif str(r["is_multiple_answer"]) != "False" or len(fa) != 1:
            dropped["olympiad: more than one final answer"] += 1
        elif str(r["unit"]) != "None":
            dropped["olympiad: answer has a unit"] += 1
        elif str(r["error"]) != "None":
            dropped["olympiad: answer carries an error tolerance"] += 1
        elif str(r["context"]) != "None":
            dropped["olympiad: problem needs a context field"] += 1
        elif not gold_ok(fa[0]):
            dropped["olympiad: gold does not grade equal to itself"] += 1
        else:
            pool.append({"source": "olympiadbench", "source_id": str(r["id"]), "problem": r["question"], "answer": fa[0]})
    n_draw = HARD_TARGET - n_comp
    pick = np.sort(np.random.default_rng(0).choice(len(pool), n_draw, replace=False))
    items += [pool[i] for i in pick]
    for i, it in enumerate(items):
        it["index"] = i
        it["unique_id"] = f"{it['source']}/{it['source_id']}"
    assert len({it["unique_id"] for it in items}) == len(items)
    comp = {"by_source": dict(collections.Counter(it["source"] for it in items)), "n": len(items), "olympiad_pool": len(pool),
            "olympiad_drawn": n_draw, "dropped": dict(dropped)}
    return items, comp


def grader_repro(n13: pathlib.Path) -> dict:
    out = {}
    for m, want in (("base", 286), ("rl", 460)):
        R = [json.loads(l) for l in open(n13 / f"{m}_math500.jsonl")]
        assert sorted(r["problem_index"] for r in R) == list(range(500))
        sc = []
        for r in R:
            mode, ext, _ = S.extract(r["text"])
            sc.append(S.grade(r["gold"], ext)["score"])
            assert (mode, ext) == (r["mode"], r["extracted"]), r["problem_index"]
        d = S.derangement(500, seed=1)
        golds = [r["gold"] for r in R]
        der = sum(S.grade(golds[d[i]], S.extract(r["text"])[1])["score"] for i, r in enumerate(R))
        out[m] = {"correct": int(sum(sc)), "acc": S.acc(sc), "want": want, "pass": int(sum(sc)) == want,
                  "equal_to_banked_scores": int(sum(int(s == r["score"]) for s, r in zip(sc, R))),
                  "failing_input": {"what": "golds deranged (seed 1)", "correct": int(der), "failed": int(der) != want}}
    return out


def n_rule(n13: pathlib.Path) -> dict:
    R = [json.loads(l) for l in open(n13 / "rl_math500.jsonl")]
    fin = np.array([r["n_new"] for r in R if not r["cap_hit"]])
    p95 = float(np.percentile(fin, 95))
    return {"rule": "ceil of the 95th percentile (numpy linear) of n_new over the finished RL step-2,800 answers, n13 s3gate-03 MATH-500",
            "n_finished": int(fin.size), "p95": p95, "N": int(np.ceil(p95))}


def prefill(n13: pathlib.Path, tok) -> dict:
    R = [json.loads(l) for l in open(n13 / "rl_math500.jsonl")]
    ids = [tok(r["text"], add_special_tokens=False)["input_ids"] for r in R]
    c2 = collections.Counter(tuple(x[:2]) for x in ids)
    c3 = collections.Counter(tuple(x[:3]) for x in ids)
    c4 = collections.Counter(tuple(x[:4]) for x in ids)
    top3, n3 = c3.most_common(1)[0]
    text = tok.decode(list(top3))
    show = lambda c: [(tok.convert_ids_to_tokens(list(k)), v) for k, v in c.most_common(3)]
    return {"ids": list(top3), "text": text, "tokens": tok.convert_ids_to_tokens(list(top3)), "n_of_500": n3,
            "first2": show(c2), "first3": show(c3), "first4": show(c4),
            "rule": "the most common first three tokens of the RL step-2,800 answers (re-tokenized saved texts): the two that close the "
                    "prompt's sentence and the first word of the reasoning (SPEC3 §3)"}


def loops(n13: pathlib.Path) -> dict:
    out = {}
    for m in ("base", "rl"):
        R = [json.loads(l) for l in open(n13 / f"{m}_math500.jsonl")]
        cap = [loop_ratio(r["text"]) for r in R if r["cap_hit"]]
        fin = [loop_ratio(r["text"]) for r in R if not r["cap_hit"] and len(r["text"]) >= LOOP["chars"]]
        out[m] = {"cap_hits": len(cap), "cap_hits_below": sum(x < LOOP["below"] for x in cap),
                  "finished_8000plus": len(fin), "finished_8000plus_below": sum(x < LOOP["below"] for x in fin)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n13", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--tok", required=True)
    a = ap.parse_args()
    n13, raw = pathlib.Path(a.n13), pathlib.Path(a.raw)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok)
    (INPUTS).mkdir(parents=True, exist_ok=True)
    (OFFLINE).mkdir(parents=True, exist_ok=True)

    probs = json.loads((n13 / "problems.json").read_text())["math500"]
    assert len(probs) == 500
    math = [{k: p[k] for k in ("index", "problem", "answer", "unique_id")} for p in probs]
    hard, comp = hard_set(raw)
    for name, data in (("math500", math), ("hard", hard)):
        (INPUTS / f"{name}.json").write_text(json.dumps(data, indent=0))

    gr = grader_repro(n13)
    g_hard = S.g_grader([it["answer"] for it in hard])
    g_math = S.g_grader([it["answer"] for it in math])
    pf = prefill(n13, tok)
    nr = n_rule(n13)
    commit_ids = tok(COMMIT_TEXT, add_special_tokens=False)["input_ids"]
    assert tok.decode(commit_ids) == COMMIT_TEXT
    lw = {k: S.wilson(c, 500) for k, c in (("base", 286), ("s2800", 460))}
    frozen = {"models": MODELS, "tokenizer": TOKENIZER, "template": "pair1", "cap": CAP, "N": nr["N"],
              "prefill_ids": pf["ids"], "prefill_text": pf["text"], "commit_text": COMMIT_TEXT, "commit_ids": commit_ids,
              "commit_max_tokens": COMMIT_MAX, "seeds": SEEDS, "samples": SAMPLES, "loop": LOOP,
              "non_attempt_max_tokens": NON_ATTEMPT_MAX_TOKENS, "grade_rule": S.GRADE_RULE,
              "check": {"base": {"n13_correct": 286, "wilson95": lw["base"]}, "s2800": {"n13_correct": 460, "wilson95": lw["s2800"]}},
              "sha256": {n: hashlib.sha256((INPUTS / f"{n}.json").read_bytes()).hexdigest() for n in ("math500", "hard")},
              "hard_sources": {k: v[:3] for k, v in SOURCES.items()}, "hard_composition": comp}
    (INPUTS / "frozen.json").write_text(json.dumps(frozen, indent=1))
    checks = {"grader_repro": gr, "G-GRADER_math500": {k: g_math[k] for k in ("pass", "planted_eq_true", "planted_neq_false", "self_equal",
                                                                               "derangement_rate", "identical_normalised_rate")},
              "G-GRADER_hard": {k: g_hard[k] for k in ("pass", "planted_eq_true", "planted_neq_false", "self_equal", "n_golds",
                                                       "derangement_rate", "identical_normalised_rate")},
              "prefill": pf, "N": nr, "loops": loops(n13), "hard_composition": comp}
    checks["pass"] = bool(all(v["pass"] and v["failing_input"]["failed"] for v in gr.values()) and g_math["pass"] and g_hard["pass"]
                          and g_math["failing_input"]["failed"] and g_hard["failing_input"]["failed"])
    (OFFLINE / "prep_checks.json").write_text(json.dumps(checks, indent=1))
    print(json.dumps({"pass": checks["pass"], "repro": {m: v["acc"] for m, v in gr.items()}, "N": nr, "prefill": pf["tokens"],
                      "prefill_n": pf["n_of_500"], "hard": comp}, indent=1))
    assert checks["pass"], "RLN-3 prep checks failed"


if __name__ == "__main__":
    main()
