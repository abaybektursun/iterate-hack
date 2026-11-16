"""Length edge (specs/SPEC_lenedge.md): one pass over the Think-SFT training rows (allenai/Dolci-Think-SFT-7B, every assistant
turn; tokens for a fixed 5 % of rows chosen by a hash of the row id and for every turn with Chinese): tokens, Chinese characters, non-Latin episodes, by dataset_source. This file makes the per-turn table; lenedge_read.py
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
# Every character for which drift.script() is not None matches LETTER (checked on every code point by --selftest), so a turn
# with fewer than drift.MIN_LETTERS matches has no episode and drift.episodes is not called on it.
LETTER = re.compile("[\u0400-\u1fff\u2c00-\ud7ff\uf900-\ufffd\U00010000-\U0001d3ff\U0001d800-\U0003ffff]")
MATH_A = re.compile(r"\\boxed|\\frac|\\sqrt|\$[^$\n]{1,200}\$")
MATH_B = re.compile(r"\b(find|compute|evaluate|determine|prove|solve|how many|what is|calculate)\b", re.I)
FLAG = 20                                               # a turn is flagged when it holds more than FLAG Chinese characters
KEEP = 15                                               # excerpts kept per shard and kind
LONG = 40                                               # the LONG longest turns of a shard in characters are tokenized; KEEP are kept
SAMPLE = 0.05                                           # share of rows whose every message is tokenized (see sampled())
COLS = ("row", "turn", "source", "n_chars", "n_tok", "ctx_tok", "zh", "zh_char", "zh_tok", "ep_n", "ep_char", "ep_tok",
        "think_end", "user_zh", "math_kw", "sampled")
# row: row in the shard; turn: index of the assistant turn in the row; source: index into the shard's sorted source names;
# n_tok: tokens of the turn, -1 when not tokenized (scan_file); ctx_tok: tokens of the row's earlier messages, sampled rows only; zh: Chinese characters; zh_char / zh_tok: character / token of the first one
# (-1: none); ep_n: episodes of drift.episodes; ep_char / ep_tok: character / token of the first episode's 5th letter;
# think_end: character of the first "</think>" (-1: none); user_zh: Chinese characters of the user turn before; math_kw: that
# user turn matches MATH_A and MATH_B; sampled: the row is in the hash sample.

_TOK = None


def tokenizer():
    global _TOK
    if _TOK is None:
        from tokenizers import Tokenizer
        _TOK = Tokenizer.from_file(huggingface_hub.hf_hub_download(MODEL[0], "tokenizer.json", revision=MODEL[1]))
    return _TOK


def sampled(row_id):
    """True for the fixed share SAMPLE of rows, chosen by a hash of the row id."""
    return int(hashlib.sha1(str(row_id).encode()).hexdigest()[:8], 16) < SAMPLE * 2 ** 32


def encode(text, chars=()):
    """(tokens of text, for each character of chars the tokens that end at or before it: drift.signs' rule)."""
    e = tokenizer().encode(text, add_special_tokens=False)
    ends = np.array([b for _, b in e.offsets])
    return len(e.ids), [int(np.searchsorted(ends, c, side="right")) for c in chars]


def scan_file(path, shard):
    """Every assistant turn of one parquet file: (table of COLS, info). Token counts are exact for the turns of sampled rows,
    for every turn with more than FLAG Chinese characters or an episode, and for the shard's longest turns; -1 for the others."""
    tok = tokenizer()
    out, rows, roles = [], 0, {}
    flagged, longest = {"prompt_zh": [], "prompt_no_zh": []}, []
    names = sorted(set(pq.read_table(path, columns=["dataset_source"]).column("dataset_source").to_pylist()))
    for batch in pq.ParquetFile(path).iter_batches(batch_size=256, columns=["messages", "dataset_source", "id"]):
        ids, src = batch.column("id").to_pylist(), batch.column("dataset_source").to_pylist()
        turns = list(W.all_turns(batch))
        take = [sampled(x) for x in ids]
        picked = [k for k, (i, _, _) in enumerate(turns) if take[i]]
        n_tok = dict(zip(picked, (len(e.ids) for e in tok.encode_batch_fast([turns[k][2] for k in picked], add_special_tokens=False))))
        last, ctx, k_turn, user = -1, 0, 0, ""
        for k, (i, role, text) in enumerate(turns):
            roles[role] = roles.get(role, 0) + 1
            if i != last:
                last, ctx, k_turn, user = i, 0, 0, ""
            n = n_tok.get(k, -1)
            if role == "user":
                user = text
            elif role == "assistant":
                zh = ZH.findall(text)
                zc = ZH.search(text).start() if zh else -1
                eps = D.episodes(text) if len(LETTER.findall(text)) >= D.MIN_LETTERS else []
                ec = eps[0][1] if eps else -1
                zt, et = -1, -1
                if len(zh) > FLAG or eps:
                    n, (zt, et) = encode(text, [zc, ec])
                    zt, et = (zt if zh else -1), (et + 1 if eps else -1)
                user_zh = len(ZH.findall(user))
                out.append([rows + i, k_turn, names.index(src[i]), len(text), n, ctx if take[i] else -1, len(zh), zc, zt, len(eps), ec, et,
                            text.find("</think>"), user_zh, bool(MATH_A.search(user) and MATH_B.search(user)), take[i]])
                ref = {"id": ids[i], "source": src[i], "shard": shard, "row": rows + i, "turn": k_turn, "n_chars": len(text)}
                if len(zh) > FLAG:
                    flagged["prompt_zh" if user_zh > FLAG else "prompt_no_zh"].append(
                        {**ref, "n_tok": n, "hash": hashlib.sha1(str(ids[i]).encode()).hexdigest(), "zh": len(zh), "zh_tok": zt, "episodes": len(eps),
                         "user": user[:300], "before": text[max(0, zc - 300):zc], "at": text[zc:zc + 500]})
                longest.append((len(text), len(out) - 1, ref, user[:300], text))
                if len(longest) > 4 * LONG:
                    longest = sorted(longest, key=lambda x: -x[0])[:LONG]
                k_turn += 1
            else:
                raise ValueError(f"role {role}")
            ctx += n
        rows += len(ids)
    long_out = []
    for _, k, ref, user, text in sorted(longest, key=lambda x: -x[0])[:LONG]:      # the longest in characters, tokenized now
        if out[k][COLS.index("n_tok")] < 0:
            out[k][COLS.index("n_tok")] = encode(text)[0]
        long_out.append({**ref, "n_tok": out[k][COLS.index("n_tok")], "zratio": round(R.zratio(text), 3), "zh": len(ZH.findall(text)), "user": user,
                         "head": text[:300], "middle": text[len(text) // 2:len(text) // 2 + 300], "tail": text[-400:]})
    table = np.array(out, dtype=np.int64).reshape(-1, len(COLS))
    info = {"shard": shard, "rows": rows, "roles": roles, "sources": names,
            "flagged_counts": {k: len(v) for k, v in flagged.items()},
            "flagged": {k: sorted(v, key=lambda x: x["hash"])[:KEEP] for k, v in flagged.items()},
            "longest": sorted(long_out, key=lambda x: -x["n_tok"])[:KEEP]}
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
    global SAMPLE
    share, SAMPLE = SAMPLE, 0.0                          # no row sampled: only flagged turns and the longest are tokenized
    table, info = scan_file(W.fake_parquet(rows, f"{tmp}/lenedge_selftest.parquet"), 0)
    n0 = table[:, COLS.index("n_tok")]
    SAMPLE = 1.0                                         # every row sampled: every count below is checked against the tokenizer
    table, info = scan_file(f"{tmp}/lenedge_selftest.parquet", 0)
    SAMPLE = share
    os.remove(f"{tmp}/lenedge_selftest.parquet")
    n1 = table[:, COLS.index("n_tok")]
    assert all(LETTER.match(chr(cp)) for cp in range(0x110000) if D.script(chr(cp))), "LETTER misses a letter of drift.SCRIPTS"
    marked = (table[:, COLS.index("zh")] > FLAG) | (table[:, COLS.index("ep_n")] > 0)
    assert (n0[marked] == n1[marked]).all() and n0.max() == n1.max() and (n0 == -1).sum() == 0 and len(rows) + 1 <= LONG   # all are among the longest
    picks = [sampled(f"row-{k}") for k in range(200000)]
    assert abs(sum(picks) / len(picks) - share) < 0.002 and picks == [sampled(f"row-{k}") for k in range(200000)]
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
          f"token counts equal the tokenizer's, the hash sample takes {share:.0%} of ids, a Chinese answer to a Chinese prompt is marked as such")


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
