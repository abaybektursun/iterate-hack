"""Freeze the no-cue inputs that need raw texts (runs/ only): openings per cell, an earlier plain-base sample, and examples.

    uv run --no-project python studies/rlneurons/paper-depth-rank/prep_nocue.py

Writes (fails if data/nocue/ exists):
  data/nocue/base_plain_s50M.jsonl  the earlier plain base on hard328 (job 1114-132922-7ba0, seed 50,000,000 + i, one sample)
  data/nocue/openings.json          per cell: how each answer opens. The cue is the three tokens ' line', '!\\n\\n', 'Okay'.
      cue_opening   the text, after leading whitespace, is: an optional word 'line', then '!', then whitespace, then 'Okay'
                    (the cue's own tokens, written by the model when it is not given them; the cued cells contain them as prefix)
      okay_first    the first word after any leading punctuation and whitespace and an optional word 'line' is 'Okay' (any trailing punctuation)
      answer_first  '\\boxed' occurs in the first 300 characters
      empty_or_short  fewer than 20 words in the whole answer
      first_three_words  the 8 most frequent first three whitespace words
      per_problem   problem index -> [cue_opening, okay_first, empty_or_short] (0/1)
  examples.json   adds "no_cue": for directions 2-8 plain, the lowest problem index it answers right and the lowest it finishes
                  wrong; for each, the plain base's answer to the same problem (same seed): first 300 and last 300 characters
"""
import collections
import glob
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "data" / "nocue"
P = "abaybektursun-"
CELLS = {"base_plain": ["1115-161512-737c", "1115-161527-c434"], "top1x1.5_plain": ["1115-161303-5ad7", "1115-161320-a1e0"],
         "d2-8_plain": ["1115-161337-2422", "1115-161356-4282"], "base_plain_s50M": ["1114-132922-7ba0"],
         "rl_plain_s1": ["1114-200505-5ff2"], "base_cue_s1": ["1114-200457-e8e6"]}
SAMPLE1 = {"rl_plain_s1", "base_cue_s1"}                            # four-sample jobs: keep sample 1 (seed 3,010,000 + i)


def run_dir(job):
    hits = sorted(glob.glob(str(ROOT.parent / "iterate-hack*" / "runs" / (P + job))))
    assert hits, job
    return pathlib.Path(hits[0])


def rows(cell):
    rs = [json.loads(l) for j in CELLS[cell] for l in (run_dir(j) / "answers.jsonl").read_text().splitlines()]
    rs = [r for r in rs if r.get("attempt", 0) == 0]
    if cell in SAMPLE1:
        rs = [r for r in rs if (r["seed"] - 3000000 - r["problem_index"]) // 10000 == 1]
    rs = sorted(rs, key=lambda r: r["problem_index"])
    assert len(rs) == 328, (cell, len(rs))
    return rs


CUE = re.compile(r"^\s*(line)?!\s+Okay\b")
OKAY = re.compile(r"^[\s\W]*(line)?[\s\W]*Okay\b")


def main():
    assert not OUT.exists(), "frozen"
    OUT.mkdir(parents=True)
    R = {c: rows(c) for c in CELLS}
    assert all(r["seed"] == 50000000 + r["problem_index"] for r in R["base_plain_s50M"])
    (OUT / "base_plain_s50M.jsonl").write_text("".join(json.dumps({"problem_index": r["problem_index"], "sample": 0, "seed": r["seed"],
                                                                     "score_v3": r["score_v3"], "cap_hit": r["cap_hit"], "n_new": r["n_new"]}) + "\n"
                                                         for r in R["base_plain_s50M"]))
    op = {"rule": __doc__.split("The cue is")[1].split("examples.json")[0].strip(), "cells": {}}
    for c, rs in R.items():
        t = [r["text"] for r in rs]
        op["cells"][c] = {"jobs": [P + j for j in CELLS[c]], "n": len(t), "cue_opening": sum(bool(CUE.match(x)) for x in t),
                          "okay_first": sum(bool(OKAY.match(x)) for x in t), "answer_first": sum("\\boxed" in x[:300] for x in t),
                          "empty_or_short": sum(len(x.split()) < 20 for x in t),
                          "cue_opening_right": sum(r["score_v3"] for r in rs if CUE.match(r["text"])),
                          "first_three_words": collections.Counter(" ".join(x.split()[:3]) for x in t).most_common(8),
                          "per_problem": {str(r["problem_index"]): [int(bool(CUE.match(r["text"]))), int(bool(OKAY.match(r["text"]))),
                                                                     int(len(r["text"].split()) < 20)] for r in rs}}
    (OUT / "openings.json").write_text(json.dumps(op, indent=1, ensure_ascii=False) + "\n")
    ex = json.loads((HERE / "examples.json").read_text())
    d, b = R["d2-8_plain"], R["base_plain"]
    assert [r["seed"] for r in d] == [r["seed"] for r in b]
    cut = lambda r: {"problem_index": r["problem_index"], "seed": r["seed"], "gold": r["gold"], "extracted_v3": r["extracted_v3"],
                     "score_v3": r["score_v3"], "cap_hit": bool(r["cap_hit"]), "n_new": r["n_new"], "first_300": r["text"][:300], "last_300": r["text"][-300:]}
    pr = next(i for i, r in enumerate(d) if r["score_v3"] == 1)
    pw = next(i for i, r in enumerate(d) if r["score_v3"] == 0 and not r["cap_hit"])
    ex["no_cue"] = {"rule": "directions 2-8 at 1.5x without the cue (sample 1): lowest problem index right, lowest finished wrong; the plain "
                            "base (sample 1, same seed) on the same problem",
                    "d2-8_plain_right": {"d2-8_plain": cut(d[pr]), "base_plain": cut(b[pr])},
                    "d2-8_plain_wrong": {"d2-8_plain": cut(d[pw]), "base_plain": cut(b[pw])}}
    (HERE / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False) + "\n")
    for c, v in op["cells"].items():
        print(c, {k: v[k] for k in ("cue_opening", "okay_first", "answer_first", "empty_or_short", "cue_opening_right")}, v["first_three_words"][:3])


if __name__ == "__main__":
    main()
