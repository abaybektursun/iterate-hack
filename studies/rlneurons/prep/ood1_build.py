"""Build the frozen item file of specs/SPEC_ood1.md: 250 MMLU-Pro items outside math and code and 250 BBH items.

    uv run --with pyarrow --with huggingface_hub python -m studies.rlneurons.prep.ood1_build

MMLU-Pro (TIGER-Lab/MMLU-Pro, test): the 9 categories that are not math, physics, chemistry, engineering or computer science;
from each, the items of a seeded shuffle, 28 from the first seven categories in name order and 27 from the last two (250).
BBH (lukaemon/bbh): 10 tasks whose target is one option letter and that are not arithmetic or code, 25 items each by the same
shuffle (250). Seed 0. Writes data/ood1/ood1_items.json (uid, bench, group, content, gold, n_options) and prints the file's
sha256. Downloads only dataset files, no weights."""
from __future__ import annotations

import hashlib
import json
import pathlib
import random
import re

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

from studies.rlneurons.lib import mcq_lib as M

OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "ood1" / "ood1_items.json"
MMLU = ("TIGER-Lab/MMLU-Pro", "b189ec765aa7ed75c8acfea42df31fdae71f97be", "data/test-00000-of-00001.parquet")
MMLU_OUT = {"math", "physics", "chemistry", "engineering", "computer science"}
BBH = ("lukaemon/bbh", "982bb89fd79532a8ac676a61fc42eb1aeec63f99")
BBH_TASKS = ("date_understanding", "disambiguation_qa", "hyperbaton", "logical_deduction_five_objects", "penguins_in_a_table",
             "reasoning_about_colored_objects", "salient_translation_error_detection", "snarks", "temporal_sequences",
             "tracking_shuffled_objects_five_objects")
SEED = 0


def pick(rows, k, key):
    rows = sorted(rows, key=key)
    random.Random(SEED).shuffle(rows)
    return rows[:k]


def main():
    items = []
    rows = pq.read_table(hf_hub_download(MMLU[0], MMLU[2], revision=MMLU[1], repo_type="dataset")).to_pylist()
    cats = sorted({r["category"] for r in rows} - MMLU_OUT)
    assert len(cats) == 9, cats
    for i, c in enumerate(cats):
        for r in pick([r for r in rows if r["category"] == c], 28 if i < 7 else 27, lambda r: r["question_id"]):
            opts = [o for o in r["options"] if o != "N/A"]
            assert M.LETTERS[r["answer_index"]] == r["answer"] and r["answer_index"] < len(opts), r["question_id"]
            items.append({"uid": f"mmlupro/{r['question_id']}", "bench": "mmlupro", "group": c,
                          "content": M.content(r["question"], opts), "gold": r["answer"], "n_options": len(opts)})
    for t in BBH_TASKS:
        rows = pq.read_table(hf_hub_download(BBH[0], f"{t}/test-00000-of-00001.parquet", revision=BBH[1], repo_type="dataset")).to_pylist()
        rows = [{**r, "i": i} for i, r in enumerate(rows)]
        for r in pick(rows, 25, lambda r: r["i"]):
            gold = re.fullmatch(r"\(([A-R])\)", r["target"].strip())
            assert gold, (t, r["target"])
            n = len(re.findall(r"^\([A-R]\)", r["input"], re.MULTILINE))
            assert n >= 2 and gold.group(1) in M.LETTERS[:n], (t, r["i"], n)
            items.append({"uid": f"bbh/{t}/{r['i']}", "bench": "bbh", "group": t, "content": M.content(r["input"], None),
                          "gold": gold.group(1), "n_options": n})
    assert len(items) == 500 and len({x["uid"] for x in items}) == 500
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, indent=1) + "\n")
    print(len(items), hashlib.sha256(OUT.read_bytes()).hexdigest())
    for b in ("mmlupro", "bbh"):
        xs = [x for x in items if x["bench"] == b]
        print(b, len(xs), "chance", round(sum(1 / x["n_options"] for x in xs), 1))


if __name__ == "__main__":
    main()
