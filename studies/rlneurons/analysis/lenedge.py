"""Length edge (specs/SPEC_lenedge.md): one pass over the Think-SFT training rows (allenai/Dolci-Think-SFT-7B, every assistant
turn): tokens, Chinese characters, non-Latin episodes, by dataset_source. This file makes the per-turn table; lenedge_read.py
reads it. Laptop, no model: each shard is downloaded to --tmp, read and deleted; the tokenizer is the tokenizer.json of
allenai/Olmo-3-7B-Think-SFT (no weights).

    PYTHONPATH=. uv run --no-project --with huggingface_hub --with pyarrow --with numpy --with tokenizers \
        python -m studies.rlneurons.analysis.lenedge --selftest --tmp <dir outside the repo>
    ... python -m studies.rlneurons.analysis.lenedge --tmp <dir outside the repo> --out runs/lenedge/train-01

  --out  a new folder (not committed): part-<shard>.npz (one line of COLS per assistant turn) and part-<shard>.json (rows,
         turns by role, sources, excerpts for the hand read).

The shard list, the turn reader and the dataset name and revision are those of analysis/wsp1_sft_overlap.py; the script
detector is analysis/drift.py's.
"""
import argparse
import hashlib
import json
import multiprocessing
import os
import re
import shutil
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"          # one process per shard; no thread pool inside each

import huggingface_hub
import numpy as np
import pyarrow.parquet as pq

from studies.rlneurons.analysis import drift as D
from studies.rlneurons.analysis import drift_test as DT
from studies.rlneurons.analysis import wsp1_sft_overlap as W
from studies.rlneurons.lib import rln4_lib as R

MODEL = ("allenai/Olmo-3-7B-Think-SFT", "6ff857587e040d6d523a3d5f3a56e918f5401d66")
ROWS, ASSISTANT_TURNS = 2_268_178, 2_368_984            # results/wsp1/sft_overlap-03/metrics.json
ZH = re.compile("[一-鿿]")                      # the characters drift.py counts as chinese_chars
HIGH = re.compile("[^\x00-ͯ]")                     # drift.script() is None for every character below U+0370
MATH_A = re.compile(r"\\boxed|\\frac|\\sqrt|\$[^$\n]{1,200}\$")
MATH_B = re.compile(r"\b(find|compute|evaluate|determine|prove|solve|how many|what is|calculate)\b", re.I)
FLAG = 20                                               # a turn is flagged when it holds more than FLAG Chinese characters
KEEP = 15                                               # excerpts kept per shard and kind
COLS = ("row", "turn", "source", "n_chars", "n_tok", "ctx_tok", "zh", "zh_char", "zh_tok", "ep_n", "ep_char", "ep_tok",
        "think_end", "user_zh", "math_kw")
# row: row in the shard; turn: index of the assistant turn in the row; source: index into the shard's sorted source names;
# ctx_tok: tokens of the row's earlier messages; zh: Chinese characters; zh_char / zh_tok: character / token of the first one
# (-1: none); ep_n: episodes of drift.episodes; ep_char / ep_tok: character / token of the first episode's 5th letter;
# think_end: character of the first "</think>" (-1: none); user_zh: Chinese characters of the user turn before; math_kw: that
# user turn matches MATH_A and MATH_B.

_TOK = None


def tokenizer():
    global _TOK
    if _TOK is None:
        from tokenizers import Tokenizer
        _TOK = Tokenizer.from_file(huggingface_hub.hf_hub_download(MODEL[0], "tokenizer.json", revision=MODEL[1]))
    return _TOK


def tok_of(text, chars):
    """Tokens that end at or before each character of chars (drift.signs' rule)."""
    ends = np.array([b for _, b in tokenizer().encode(text, add_special_tokens=False).offsets])
    return [int(np.searchsorted(ends, c, side="right")) for c in chars]


def scan_file(path, shard):
    """Every assistant turn of one parquet file: (table of COLS, info)."""
    tok = tokenizer()
    out, rows, roles = [], 0, {}
    flagged, longest = {"prompt_zh": [], "prompt_no_zh": []}, []
    names = sorted(set(pq.read_table(path, columns=["dataset_source"]).column("dataset_source").to_pylist()))
    for batch in pq.ParquetFile(path).iter_batches(batch_size=256, columns=["messages", "dataset_source", "id"]):
        ids, src = batch.column("id").to_pylist(), batch.column("dataset_source").to_pylist()
        turns = list(W.all_turns(batch))
        n_tok = [len(e.ids) for e in tok.encode_batch_fast([t for _, _, t in turns], add_special_tokens=False)]
        last, ctx, k_turn, user = -1, 0, 0, ""
        for (i, role, text), n in zip(turns, n_tok):
            roles[role] = roles.get(role, 0) + 1
            if i != last:
                last, ctx, k_turn, user = i, 0, 0, ""
            if role == "user":
                user = text
            elif role == "assistant":
                zh = ZH.findall(text)
                zc = ZH.search(text).start() if zh else -1
                eps = D.episodes(text) if HIGH.search(text) else []
                ec = eps[0][1] if eps else -1
                zt, et = tok_of(text, [zc, ec]) if zh or eps else (-1, -1)
                zt, et = (zt if zh else -1), (et + 1 if eps else -1)
                user_zh = len(ZH.findall(user))
                out.append((rows + i, k_turn, names.index(src[i]), len(text), n, ctx, len(zh), zc, zt, len(eps), ec, et,
                            text.find("</think>"), user_zh, bool(MATH_A.search(user) and MATH_B.search(user))))
                ref = {"id": ids[i], "source": src[i], "shard": shard, "row": rows + i, "turn": k_turn, "n_tok": n, "n_chars": len(text)}
                if len(zh) > FLAG:
                    flagged["prompt_zh" if user_zh > FLAG else "prompt_no_zh"].append(
                        {**ref, "hash": hashlib.sha1(str(ids[i]).encode()).hexdigest(), "zh": len(zh), "zh_tok": zt, "episodes": len(eps),
                         "user": user[:300], "before": text[max(0, zc - 300):zc], "at": text[zc:zc + 500]})
                longest.append((n, {**ref, "zratio": round(R.zratio(text), 3), "zh": len(zh), "user": user[:300], "head": text[:300],
                                    "middle": text[len(text) // 2:len(text) // 2 + 300], "tail": text[-400:]}))
                longest = sorted(longest, key=lambda x: -x[0])[:KEEP]
                k_turn += 1
            else:
                raise ValueError(f"role {role}")
            ctx += n
        rows += len(ids)
    table = np.array(out, dtype=np.int64).reshape(-1, len(COLS))
    info = {"shard": shard, "rows": rows, "roles": roles, "sources": names,
            "flagged_counts": {k: len(v) for k, v in flagged.items()},
            "flagged": {k: sorted(v, key=lambda x: x["hash"])[:KEEP] for k, v in flagged.items()}, "longest": [x for _, x in longest]}
    return table, info


def init_worker(tmp, out, files):
    global TMP, OUT, FILES
    TMP, OUT, FILES = tmp, out, files


def scan_shard(i):
    part = f"{OUT}/part-{i:05d}"
    if os.path.exists(part + ".json"):
        return json.load(open(part + ".json"))
    t0, dl = time.time(), f"{TMP}/dl-{i:05d}"
    path = huggingface_hub.hf_hub_download(W.DATASET, FILES[i], repo_type="dataset", revision=W.REVISION, local_dir=dl)
    t1 = time.time()
    table, info = scan_file(path, i)
    shutil.rmtree(dl)
    info.update(file=FILES[i], download_s=round(t1 - t0, 1), scan_s=round(time.time() - t1, 1))
    np.savez_compressed(part + ".npz", table=table)
    json.dump(info, open(part + ".json.tmp", "w"))
    os.replace(part + ".json.tmp", part + ".json")
    return info


def selftest(tmp):
    """Instrument check 1 of the spec: the planted texts of drift_test.py as assistant turns of a file in the dataset's schema."""
    os.makedirs(tmp, exist_ok=True)
    cases, where = [], {}
    for k, (name, plant) in enumerate(DT.PLANT.items()):
        text, c = DT.at(DT.CLEAN, plant, 0.08 * (k + 1))
        cases.append((f"pos/{name}", text))
        where[f"pos/{name}"] = c
    for name, neg in DT.NEGATIVE.items():
        cases.append((f"neg/{name}", DT.at(DT.CLEAN, neg, 0.5)[0]))
    long_text, c_long = DT.at(DT.CLEAN * 40, DT.PLANT["chinese"], 0.9)
    cases.append(("pos/long_late", long_text))
    where["pos/long_late"] = c_long
    rows = [(key, [("user", "Find the number of ordered pairs $(a, b)$ with $a^2 + b^2 = 2025$."), ("assistant", text)]) for key, text in cases]
    rows.append(("zh_prompt", [("user", DT.PLANT["chinese"] * 2), ("assistant", DT.PLANT["chinese"] * 3),
                               ("user", "Thanks, tell me a story."), ("assistant", "Once upon a time there was a fox.")]))
    table, info = scan_file(W.fake_parquet(rows, f"{tmp}/lenedge_selftest.parquet"), 0)
    os.remove(f"{tmp}/lenedge_selftest.parquet")
    col = {c: table[:, j] for j, c in enumerate(COLS)}
    assert info["rows"] == len(rows) and info["roles"] == {"user": len(rows) + 1, "assistant": len(rows) + 1}, info["roles"]
    tok = tokenizer()
    for r, (key, text) in enumerate(cases):
        n = len(tok.encode(text, add_special_tokens=False).ids)
        assert col["n_tok"][r] == n and col["n_chars"][r] == len(text), (key, col["n_tok"][r], n)
        assert col["math_kw"][r] == 1 and col["user_zh"][r] == 0 and col["turn"][r] == 0 and col["row"][r] == r
        if key.startswith("neg/"):
            assert col["ep_n"][r] == 0 and col["zh"][r] <= FLAG and col["ep_tok"][r] == -1, f"{key}: flagged"
            continue
        want = len(tok.encode(text[:where[key]], add_special_tokens=False).ids)
        span = len(tok.encode(text[where[key]:text.index("\n", where[key])], add_special_tokens=False).ids) + 2   # the planted passage
        assert col["ep_n"][r] == 1 and 0 <= col["ep_tok"][r] - want <= span, f"{key}: episode token {col['ep_tok'][r]}, planted at {want}"
        zh = len(ZH.findall(text))
        assert col["zh"][r] == zh, key
        if zh:
            assert col["zh_char"][r] >= where[key] and abs(col["zh_tok"][r] - want) <= 12, f"{key}: first Chinese token {col['zh_tok'][r]}, planted at {want}"
    flagged = {x["id"] for x in info["flagged"]["prompt_no_zh"]}
    assert flagged == {key for key, text in cases if len(ZH.findall(text)) > FLAG}, flagged
    assert {"pos/chinese", "pos/long_late"} <= flagged and not any(k.startswith("neg/") for k in flagged)
    r = len(cases)                                       # the two assistant turns of the row with a Chinese prompt
    assert col["user_zh"][r] > FLAG and col["zh"][r] > FLAG and col["turn"][r] == 0 and col["ctx_tok"][r] > 0 and col["math_kw"][r] == 0
    assert col["user_zh"][r + 1] == 0 and col["zh"][r + 1] == 0 and col["turn"][r + 1] == 1 and col["ctx_tok"][r + 1] > col["ctx_tok"][r]
    assert [x["id"] for x in info["flagged"]["prompt_zh"]] == ["zh_prompt"]
    assert info["longest"][0]["id"] == "pos/long_late" and info["longest"][0]["n_tok"] == col["n_tok"].max()
    print(f"selftest: {len(DT.PLANT) + 1} planted positives found inside the planted passage (first Chinese character within 12 tokens of its start), {len(DT.NEGATIVE)} negatives not flagged, "
          f"token counts equal the tokenizer's, a Chinese answer to a Chinese prompt is marked as such")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tmp", required=True)
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=30)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a.tmp)
    os.makedirs(a.tmp, exist_ok=True)
    os.makedirs(a.out, exist_ok=True)                    # an interrupted pass resumes from its finished shards
    t0 = time.time()
    files, _, total_rows = W.dataset_files()
    tokenizer()                                          # downloaded once, before the fork
    rows, turns = 0, 0
    with multiprocessing.get_context("fork").Pool(a.workers, init_worker, (a.tmp, a.out, files)) as pool:
        for k, p in enumerate(pool.imap_unordered(scan_shard, range(len(files)))):
            rows, turns = rows + p["rows"], turns + p["roles"]["assistant"]
            print(f"{time.time() - t0:6.0f} s  {k + 1:3d} of {len(files)}  shard {p['shard']:3d}  scan {p['scan_s']:6.1f} s", flush=True)
    assert rows == total_rows == ROWS and turns == ASSISTANT_TURNS, (rows, total_rows, turns)
    json.dump({"dataset": W.DATASET, "revision": W.REVISION, "tokenizer": MODEL, "rows": rows, "assistant_turns": turns,
               "shards": len(files), "wall_s": round(time.time() - t0)}, open(f"{a.out}/pass.json", "w"), indent=1)
    print("rows", rows, "assistant turns", turns, "wall", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
