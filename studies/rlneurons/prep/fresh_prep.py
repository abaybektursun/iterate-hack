"""Builds the fresh held-out set data/fresh/fresh2026_v1.json (specs/SPEC_fresh.md): competition problems published in 2026,
after the training data of the base, RL-Zero-Math and Think-SFT. Data only: no model.

    uv run --no-project --with numpy --with math-verify==0.9.0 --with pyarrow --with huggingface_hub \
        python -m studies.rlneurons.prep.fresh_prep

Sources: MathArena/aime_2026 and MathArena/hmmt_feb_2026 on Hugging Face at the revisions in HF, and the official HMMT
solutions PDFs transcribed into data/fresh/transcribed_v1/*.json (problem, answer and the flags figure, estimation, multi,
proof, and a note; PDF urls and sha256 in data/fresh/transcribed_v1/sources.json). An official answer printed as two equal
forms "a = b" has gold a; b must grade right against a (asserted). Drop rules, in this order, each counted in
data/fresh/fresh2026_v1_meta.json: published before 2026 (OLDER), figure, estimation, more than one answer or proof, gold that grader v3 does not grade right
against itself, gold + 1 or another problem's gold that grader v3 grades right. Fail loud.
"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re

from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
OUT = STUDY / "data" / "fresh"
HF = {"aime2026": ("MathArena/aime_2026", "d61f486805306e6e6b5913504c07763a99e1b112", 30),
      "hmmt_feb2026": ("MathArena/hmmt_feb_2026", "589a53fe152febc0f4f99f3e561007bf8da8e664", 33)}
PDF = {"hmmt_feb2026_guts": "2026-02-14", "hmmt_nov2026_gen": "2026-11-07", "hmmt_nov2026_thm": "2026-11-07",
       "hmmt_nov2026_team": "2026-11-07", "hmmt_nov2026_guts": "2026-11-07"}
FIGURE = re.compile(r"\[asy\]|\b(figure|diagram|shown|pictured)\b", re.I)
OLDER = {("aime2026", "1")}                   # AIME 2026 I #1 is the 2020 Purple Comet Middle School #8: an exact match in the RL training prompts
DIAGRAM_NEEDED = {("hmmt_feb2026", "25")}     # kumarjau1998/HMMT2026 card: "the omitted official diagram supplies necessary placement conditions"


def right(gold: str, answer: str) -> bool:
    return R.grade_v3(gold, f"I work it out step by step.\n\nAnswer: ${answer}$")["score_v3"] == 1


def candidates() -> list:
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download
    items = []
    for src, (repo, rev, n) in HF.items():
        rows = pq.read_table(hf_hub_download(repo, "data/train-00000-of-00001.parquet", repo_type="dataset", revision=rev)).to_pylist()
        assert len(rows) == n, (src, len(rows))
        for r in rows:
            i = int(r["problem_idx"])
            date = "2026-02-14" if src == "hmmt_feb2026" else "2026-02-05" if i <= 15 else "2026-02-11"     # AIME I, then II
            items.append({"source": src, "source_id": str(i), "date": date, "origin": f"hf:{repo}@{rev}", "problem": r["problem"].strip(),
                          "answer": str(r["answer"]).strip(), "flags": {}})
    for src, date in PDF.items():
        for r in json.loads((OUT / "transcribed_v1" / f"{src}.json").read_text()):
            flags = {k: r.get(k) for k in ("figure", "estimation", "multi", "proof")}
            forms = [x.strip() for x in r["answer"].split(" = ")]
            assert len(forms) <= 2 and (len(forms) == 1 or flags["estimation"] or right(forms[0], forms[1])), (src, r["number"], forms)
            items.append({"source": src, "source_id": str(r["number"]), "date": date, "origin": f"pdf:{src}", "problem": r["problem"].strip(),
                          "answer": forms[0], "flags": flags})
    return items


def main():
    cand = candidates()
    golds = [c["answer"] for c in cand]
    keep, dropped = [], collections.Counter()
    for k, c in enumerate(cand):
        f, other = c["flags"], golds[(k + 1) % len(golds)]
        if (c["source"], c["source_id"]) in OLDER:
            why = "published before 2026"
        elif f.get("figure") or FIGURE.search(c["problem"]) or (c["source"], c["source_id"]) in DIAGRAM_NEEDED:
            why = "figure"
        elif f.get("estimation"):
            why = "estimation"
        elif f.get("multi") or f.get("proof") or not c["answer"]:
            why = "more than one answer, or proof"
        elif not right(c["answer"], c["answer"]):
            why = "gold does not grade right against itself"
        elif right(c["answer"], f"{c['answer']} + 1") or (other != c["answer"] and right(c["answer"], other)):
            why = "a wrong answer grades right"
        else:
            keep.append(c)
            continue
        dropped[f"{c['source']}: {why}"] += 1
    for i, c in enumerate(keep):
        del c["flags"]
        c.update(index=i, unique_id=f"{c['source']}/{c['source_id']}")
    assert len({c["unique_id"] for c in keep}) == len(keep)
    path = OUT / "fresh2026_v1.json"
    assert not path.exists(), f"{path} exists: a changed set is a new version"
    path.write_text(json.dumps(keep, indent=1, ensure_ascii=False) + "\n")
    meta = {"n": len(keep), "n_candidates": len(cand), "by_source": dict(collections.Counter(c["source"] for c in keep)),
            "dropped": dict(sorted(dropped.items())), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "hf": HF,
            "grader_check": "every kept gold: grade_v3 right against itself, wrong against gold + 1 and against the next problem's gold"}
    (OUT / "fresh2026_v1_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
