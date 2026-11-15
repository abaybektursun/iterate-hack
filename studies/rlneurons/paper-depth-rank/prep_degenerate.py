"""Count degenerate answers per hard328 cell from the raw texts (runs/ only) and freeze the counts to data/degenerate.json.

    uv run --no-project python studies/rlneurons/paper-depth-rank/prep_degenerate.py

Rule (fixed before counting): an answer is degenerate when its most frequent whitespace-separated word makes up more than 20 % of
its words and it has at least 200 words. The readout's rule (normband_readout.which_rate: ' which ' is more than 5 % of the
words) is counted too, for comparison. Also adds to examples.json one right and one finished-wrong answer (lowest problem index, sample 1) of direction 1 at 1.5x
and of layers 22-31 at 3.0x (keys hard328.top1x1.5 and hard328.L22-31x3.0). Reads runs/<job>/answers.jsonl from any ../iterate-hack*/runs/ folder. Fails if the file exists.
"""
import collections
import glob
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "data" / "degenerate.json"
# cell -> {sample: [jobs]}
JOBS = {"base_cue": {s: ["1114-200457-e8e6"] for s in range(4)}, "all8": {s: ["1115-055641-b417"] for s in range(4)},
        "L22-31": {0: ["1115-105335-a886"], 1: ["1115-122936-1b30", "1115-122949-e563"]},
        "L0-10": {0: ["1115-105312-7e19"], 1: ["1115-122708-c6c1", "1115-122720-ad28"], 2: ["1115-122733-bc4c", "1115-122746-2593"],
                  3: ["1115-122759-39f3", "1115-122810-7b2d"]},
        "L11-21": {0: ["1115-105324-5f61"], 1: ["1115-122912-8aec", "1115-122924-d28b"]},
        "d2-8": {0: ["1115-145941-c2cc", "1115-145956-7546"], 1: ["1115-122847-824c", "1115-122859-b197"]},
        "top1x1.5": {0: ["1115-145913-fed1", "1115-145926-720e"], 1: ["1115-145845-f70e", "1115-145859-a234"]},
        "top1x1": {0: ["1115-000358-d11a"]}, "top1x2": {0: ["1115-105247-1603"]}, "top1x3": {0: ["1115-105259-789c"]},
        "L22-31x3.0": {1: ["1115-145720-8ceb", "1115-145733-af00"]}, "L22-31x4.5": {1: ["1115-145625-c6dc", "1115-145638-c016"]},
        "L0-10x0.2": {1: ["1115-145652-dc10", "1115-145706-0b28"]}, "rand_L0-10": {1: ["1115-122822-c211", "1115-122835-f7eb"]},
        "rand8x1.5": {0: ["1115-090241-0229"]}}


def run_dir(job):
    hits = sorted(glob.glob(str(ROOT.parent / "iterate-hack*" / "runs" / ("abaybektursun-" + job))))
    assert hits, job
    return pathlib.Path(hits[0])


def degenerate(t):
    w = t.split()
    return len(w) >= 200 and collections.Counter(w).most_common(1)[0][1] > 0.2 * len(w)


def which(t):
    return t.count(" which ") > 0.05 * max(1, len(t.split()))


def main():
    assert not OUT.exists(), "frozen"
    ex = json.loads((HERE / "examples.json").read_text())
    out = {"rule": __doc__.split("Rule (fixed before counting): ")[1].split(" The readout")[0].replace("\n", " "), "cells": {}}
    for cell, ss in JOBS.items():
        out["cells"][cell] = {}
        for s, jobs in ss.items():
            rows = [json.loads(l) for j in jobs for l in (run_dir(j) / "answers.jsonl").read_text().splitlines()]
            rows = [r for r in rows if r.get("attempt", 0) == 0 and (r["seed"] - 3000000 - r["problem_index"]) // 10000 == s]
            assert len(rows) == 328, (cell, s, len(rows))
            if cell in ("top1x1.5", "L22-31x3.0") and s == 1:
                rs = sorted(rows, key=lambda r: r["problem_index"])
                pick = {"right": next(r for r in rs if r["score_v3"] == 1), "wrong": next(r for r in rs if r["score_v3"] == 0 and not r["cap_hit"])}
                ex["hard328"][cell] = {k: {"problem_index": r["problem_index"], "unique_id": r.get("unique_id"), "sample": s, "seed": r["seed"],
                                           "gold": r["gold"], "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"],
                                           "cap_hit": bool(r["cap_hit"]), "n_new": r["n_new"], "answer_tail": r["text"][-700:]} for k, r in pick.items()}
            deg = [r for r in rows if degenerate(r["text"])]
            top = collections.Counter(collections.Counter(r["text"].split()).most_common(1)[0][0] for r in deg).most_common(5)
            out["cells"][cell][str(s)] = {"degenerate": len(deg), "degenerate_right": sum(r["score_v3"] for r in deg),
                                          "degenerate_cut_off": sum(bool(r["cap_hit"]) for r in deg), "readout_which_rule": sum(which(r["text"]) for r in rows),
                                          "top_words": top}
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    (HERE / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False) + "\n")
    for c, v in out["cells"].items():
        print(c, {s: (x["degenerate"], x["readout_which_rule"], x["top_words"][:2]) for s, x in v.items()})


if __name__ == "__main__":
    main()
