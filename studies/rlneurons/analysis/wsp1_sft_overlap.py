"""WSP-1: text overlap of the test problems with the Think-SFT training prompts (allenai/Dolci-Think-SFT-7B, train).

    PYTHONPATH=. uv run --no-project --with huggingface_hub --with pyarrow --with numpy \
        python -m studies.rlneurons.analysis.wsp1_sft_overlap --tmp <dir outside the repo> [--selftest] [--minutes 25]
        [--out studies/rlneurons/results/wsp1/sft_overlap-<nn>]

The rule is the one of rln3_overlap.py, imported: a problem is `exact` when its normalised text equals a training
prompt, `near` when at least half of its word 8-grams occur in one training prompt. The training prompt of a row is
its first `user` message. Each parquet shard is downloaded to --tmp, scanned and deleted; one part file per shard
stays in --tmp, so an interrupted scan continues. No shard starts after --minutes; the scan is then a lower bound,
and a second run with the same --tmp, a larger --minutes and the next --out folder scans only the missing shards.

Not part of the rule, reported apart (`short_contained`): a problem of fewer than 8 words has one gram, its whole
text, so the rule can only flag it when a whole training prompt equals it. For those problems the scan also records
a training prompt that contains the normalised problem as a run of whole words.

Writes {run.json, metrics.json, flags.json} to --out (default results/wsp1/sft_overlap-01).
"""
import argparse
import collections
import datetime
import json
import multiprocessing
import os
import platform
import re
import shutil
import subprocess
import sys
import time

import huggingface_hub
import numpy
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from studies.rlneurons.analysis.rln3_overlap import grams, norm

DATASET = "allenai/Dolci-Think-SFT-7B"
REVISION = "83f618e2fe0aed29ee3440a3658a0326c175d09d"
STUDY = "studies/rlneurons"
OUT = f"{STUDY}/results/wsp1/sft_overlap-01"
HARD = f"{STUDY}/data/rln3/hard.json"
MATH500 = f"{STUDY}/data/rln4/math500.json"
RL_OVERLAP = f"{STUDY}/results/rln3/rln3_overlap.json"
SCORES_MATH500 = f"{STUDY}/results/wsp1/full500/sft1_cue-01/per_problem.json"
SCORES_HARD328 = "runs/sameraslan-1114-204845-1055/answers.jsonl"


class Scanner:
    """Holds the test problems; feed() takes one training prompt and keeps, per problem, its best matching row."""

    def __init__(self, items):
        self.n_grams, self.index, self.by_norm = {}, collections.defaultdict(list), collections.defaultdict(list)
        short = collections.defaultdict(list)
        for key, text in items:
            g = grams(text)
            self.n_grams[key] = len(g)
            self.by_norm[norm(text)].append(key)
            for x in g:
                self.index[x].append(key)
            if len(norm(text).split()) < 8:
                short[norm(text)].append(key)
        self.gramset = set(self.index)
        self.short = dict(short)
        alt = "|".join(re.escape(s) for s in sorted(short, key=len, reverse=True))
        self.short_re = re.compile(f"(?:^| )({alt})(?= |$)") if short else None
        self.best, self.short_hit = {}, {}

    def feed(self, text, ref):
        n = norm(text)
        if self.short_re:
            for m in self.short_re.finditer(n):
                for key in self.short[m.group(1)]:
                    self.short_hit.setdefault(key, {**ref, "prompt_200": text[:200]})
        hit = grams(n) & self.gramset  # norm(norm(s)) == norm(s), so grams(n) is grams(text)
        if not hit:
            return
        count = collections.Counter(key for x in hit for key in self.index[x])
        exact = set(self.by_norm.get(n, ()))
        for key, c in count.items():
            share = c / self.n_grams[key]
            b = self.best.setdefault(key, {"share": 0.0, "exact": False, "rows_near": 0, "rows_exact": 0})
            b["rows_near"] += share >= 0.5
            b["rows_exact"] += key in exact
            if (key in exact, share) > (b["exact"], b["share"]):
                b.update(share=share, exact=key in exact, evidence={**ref, "prompt_200": text[:200]})


def merge(parts):
    """Best row per problem over shards; ties go to the earliest shard."""
    best, short = {}, {}
    for p in sorted(parts, key=lambda p: p["shard"]):
        for key, b in p["best"].items():
            a = best.get(key)
            if a is None:
                best[key] = dict(b)
                continue
            rows = {k: a[k] + b[k] for k in ("rows_near", "rows_exact")}
            if (b["exact"], b["share"]) > (a["exact"], a["share"]):
                a = dict(b)
            best[key] = {**a, **rows}
        for key, ev in p["short"].items():
            short.setdefault(key, ev)
    return best, short


def flag_of(b):
    return "exact" if b and b["exact"] else "near" if b and b["share"] >= 0.5 else "none"


def first_user_prompts(batch):
    """Yields (row in batch, text of the first user message or None) without decoding the other messages."""
    msgs = batch.column("messages")
    if msgs.null_count:
        raise ValueError("null messages list")
    off = msgs.offsets.to_numpy()
    lo, hi = int(off[0]), int(off[-1])
    values = msgs.values
    user = pc.equal(values.field("role").slice(lo, hi - lo), "user").to_numpy(zero_copy_only=False)
    content = values.field("content")
    for i in range(len(msgs)):
        seg = user[off[i] - lo:off[i + 1] - lo]
        j = int(seg.argmax()) if seg.any() else -1
        yield i, (content[int(off[i]) + j].as_py() if j >= 0 else None)


def scan_file(path, scanner, shard):
    """Feeds every row of one parquet file to the scanner. Returns rows, rows without a user message, rows by source."""
    rows, no_user, sources = 0, 0, collections.Counter()
    for batch in pq.ParquetFile(path).iter_batches(batch_size=512, columns=["messages", "dataset_source", "id"]):
        ids, src = batch.column("id").to_pylist(), batch.column("dataset_source").to_pylist()
        sources.update(src)
        for i, text in first_user_prompts(batch):
            if text is None:
                no_user += 1
            else:
                scanner.feed(text, {"id": ids[i], "dataset_source": src[i], "shard": shard, "row_in_shard": rows + i})
        rows += len(ids)
    return rows, no_user, dict(sources)


def test_items():
    hard, math500 = json.load(open(HARD)), json.load(open(MATH500))
    return ([(f"hard/{it['index']}", it["problem"]) for it in hard]
            + [(f"math500/{it['index']}", it["problem"]) for it in math500])


def init_worker(tmp, deadline, files):
    global TMP, DEADLINE, FILES, ITEMS
    TMP, DEADLINE, FILES, ITEMS = tmp, deadline, files, test_items()


def scan_shard(i):
    part = f"{TMP}/part-{i:05d}.json"
    if os.path.exists(part):
        return json.load(open(part))
    if time.time() > DEADLINE:
        return {"shard": i, "skipped": True}
    t0, dl = time.time(), f"{TMP}/dl-{i:05d}"
    path = huggingface_hub.hf_hub_download(DATASET, FILES[i], repo_type="dataset", revision=REVISION, local_dir=dl)
    t1, size, scanner = time.time(), os.path.getsize(path), Scanner(ITEMS)
    rows, no_user, sources = scan_file(path, scanner, i)
    shutil.rmtree(dl)
    res = {"shard": i, "file": FILES[i], "bytes": size, "rows": rows, "no_user": no_user, "sources": sources,
           "download_s": round(t1 - t0, 1), "scan_s": round(time.time() - t1, 1),
           "best": scanner.best, "short": scanner.short_hit}
    json.dump(res, open(part + ".tmp", "w"))
    os.replace(part + ".tmp", part)
    return res


def dataset_files():
    info = huggingface_hub.HfApi().dataset_info(DATASET, revision=REVISION, files_metadata=True)
    if info.sha != REVISION:
        raise ValueError(f"revision {info.sha}")
    files = sorted((s.rfilename, s.size) for s in info.siblings if s.rfilename.endswith(".parquet"))
    total_rows = sum(s["num_examples"] for s in info.card_data.to_dict()["dataset_info"]["splits"])
    return [f for f, _ in files], [s for _, s in files], total_rows


def accuracy(flags, scores):
    out = {}
    for name, keep in (("overlap", lambda f: f != "none"), ("no_overlap", lambda f: f == "none")):
        s = [scores[i] for i, v in flags.items() if keep(v["flag"])]
        out[name] = {"n": len(s), "correct": sum(s), "accuracy": round(sum(s) / len(s), 4) if s else None}
    return out


def selftest(tmp):
    """The scanner must flag a planted problem, must not flag a row below the threshold, and must match a real row."""
    hard = [it for it in json.load(open(HARD)) if len(norm(it["problem"]).split()) >= 60][:3]
    p0, p1, p2 = (it["problem"] for it in hard)
    filler = " ".join(f"filler{i} word{i}" for i in range(200))
    w1, w2 = p1.split(), p2.split()
    rows = [
        ("r0", [("user", "Unrelated question about the weather in Paris and nothing else at all today.")]),
        ("r1", [("system", "You are helpful."), ("user", "  " + p0.upper().replace(" ", "  ") + " !!"), ("assistant", p2)]),
        ("r2", [("user", "Please solve: " + " ".join(w1[:int(len(w1) * 0.7)]) + " " + filler), ("assistant", "ok")]),
        ("r3", [("user", " ".join(w2[:int(len(w2) * 0.25)]) + " " + filler), ("user", p2)]),
        ("r4", [("assistant", p2)]),
    ]
    typ = pa.list_(pa.struct([("content", pa.string()), ("role", pa.string())]))
    table = pa.table({"messages": pa.array([[{"content": c, "role": r} for r, c in m] for _, m in rows], type=typ),
                      "dataset_source": ["fake"] * len(rows), "id": [i for i, _ in rows]})
    fake = f"{tmp}/selftest-fake.parquet"
    pq.write_table(table, fake, row_group_size=2)
    sc = Scanner([("t/0", p0), ("t/1", p1), ("t/2", p2), ("t/short", "Compute 3 + 4.")])
    n_rows, no_user, _ = scan_file(fake, sc, 0)
    got = {k: (flag_of(sc.best.get(k)), round(sc.best[k]["share"], 3) if k in sc.best else 0.0,
               sc.best[k]["evidence"]["id"] if k in sc.best else None) for k in ("t/0", "t/1", "t/2")}
    print("selftest planted:", got, "rows", n_rows, "no_user", no_user)
    assert got["t/0"][0] == "exact" and got["t/0"][2] == "r1", got
    assert got["t/1"][0] == "near" and got["t/1"][2] == "r2" and 0.5 <= got["t/1"][1] < 1, got
    assert got["t/2"][0] == "none" and got["t/2"][1] < 0.5, got  # p2 sits only in assistant and second user turns
    assert (n_rows, no_user) == (5, 1)
    sc = Scanner([("t/short", "Compute 3 + 4.")])
    sc.feed("Here is a task. Compute 3 + 4 and then explain every step of the working in detail please.", {"id": "s"})
    sc.feed("Compute 3 + 45 and then explain every step of the working in detail please, thank you.", {"id": "no"})
    assert flag_of(sc.best.get("t/short")) == "none" and sc.short_hit["t/short"]["id"] == "s", sc.short_hit
    os.remove(fake)

    files, sizes, total_rows = dataset_files()
    i = min(range(len(files)), key=lambda k: sizes[k])
    t0 = time.time()
    path = huggingface_hub.hf_hub_download(DATASET, files[i], repo_type="dataset", revision=REVISION,
                                           local_dir=f"{tmp}/dl-selftest")
    t1 = time.time()
    f = pq.ParquetFile(path)
    print("selftest shard", files[i], f"{sizes[i] / 1e6:.0f} MB in {t1 - t0:.1f} s; schema:", f.schema_arrow,
          "row groups", f.num_row_groups, "rows", f.metadata.num_rows)
    batch = next(f.iter_batches(batch_size=512, columns=["messages", "dataset_source", "id"]))
    row, text = next((r, t) for r, t in first_user_prompts(batch) if t and len(norm(t).split()) >= 30)
    print("selftest real row", row, batch.column("id")[row].as_py(), repr(text[:100]))
    sc = Scanner([("real/0", text)] + test_items())
    n_rows, no_user, sources = scan_file(path, sc, i)
    b = sc.best["real/0"]
    print("selftest real:", flag_of(b), b["share"], b["evidence"]["row_in_shard"], f"scan {time.time() - t1:.1f} s",
          "rows", n_rows, "no_user", no_user, "sources", sources)
    assert flag_of(b) == "exact" and b["share"] == 1.0 and b["rows_exact"] >= 1, b
    shutil.rmtree(f"{tmp}/dl-selftest")
    print(f"selftest ok; dataset {len(files)} shards, {sum(sizes) / 1e9:.1f} GB, {total_rows} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tmp", required=True, help="directory outside the repo for downloads and part files")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--minutes", type=float, default=25.0, help="no shard starts after this many minutes")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default=OUT, help="run folder; must not exist")
    a = ap.parse_args()
    os.makedirs(a.tmp, exist_ok=True)
    if a.selftest:
        return selftest(a.tmp)
    if os.path.exists(a.out):
        raise FileExistsError(f"{a.out} exists; a rerun gets the next number")
    t0 = time.time()
    files, sizes, total_rows = dataset_files()
    parts = []
    with multiprocessing.Pool(a.workers, init_worker, (a.tmp, t0 + 60 * a.minutes, files)) as pool:
        for p in pool.imap_unordered(scan_shard, range(len(files))):
            if not p.get("skipped"):
                parts.append(p)
                print(f"{time.time() - t0:6.0f} s  shard {p['shard']:3d}  rows {p['rows']:6d}  "
                      f"dl {p['download_s']} s  scan {p['scan_s']} s  hits {len(p['best'])}", flush=True)
    parts.sort(key=lambda p: p["shard"])
    scanned = [p["shard"] for p in parts]
    start, n = {}, 0
    for i in range(len(files)):  # global row index of a shard's first row, known while all earlier shards are scanned
        if i not in scanned:
            break
        start[i], n = n, n + parts[i]["rows"]
    best, short = merge(parts)
    rows_scanned = sum(p["rows"] for p in parts)
    complete = len(parts) == len(files)
    if complete and rows_scanned != total_rows:
        raise ValueError(f"scanned {rows_scanned} rows, the dataset card states {total_rows}")

    hard, math500 = json.load(open(HARD)), json.load(open(MATH500))
    rl = json.load(open(RL_OVERLAP))["sets"]["hard"]["flags"]
    flags = {}
    for name, items in (("hard", hard), ("math500", math500)):
        flags[name] = {}
        for it in items:
            key = f"{name}/{it['index']}"
            b = best.get(key)
            f = {"flag": flag_of(b), "share": round(b["share"], 3) if b else 0.0, "source": it.get("source", name)}
            if name == "hard":
                f["rl_flag"] = rl[str(it["index"])]["flag"]
            if f["flag"] != "none":
                ev = dict(b["evidence"])
                ev["row_index"] = start[ev["shard"]] + ev["row_in_shard"] if ev["shard"] in start else None
                f.update(evidence=ev, rows_near=b["rows_near"], rows_exact=b["rows_exact"])
            if key in short:
                f["short_contained"] = short[key]
            flags[name][str(it["index"])] = f
    sets = {"hard400": flags["hard"], "hard328": {i: f for i, f in flags["hard"].items() if f["rl_flag"] == "none"},
            "math500": flags["math500"]}
    scores = {"math500": {str(r["problem_index"]): r["score_v3"] for r in json.load(open(SCORES_MATH500))}}
    if os.path.exists(SCORES_HARD328):
        scores["hard328"] = {str(r["problem_index"]): r["score_v3"]
                             for r in map(json.loads, open(SCORES_HARD328))}
    metrics = {"dataset": DATASET, "revision": REVISION, "prompt_field": "messages[first role == user].content",
               "rule": "rln3_overlap.norm/grams: exact = normalised text equals a training prompt; near = at least "
                       "half of the word 8-grams occur in one training prompt",
               "rows_scanned": rows_scanned, "rows_total": total_rows, "shards_scanned": len(parts),
               "shards_total": len(files), "complete": complete,
               "shards_not_scanned": [i for i in range(len(files)) if i not in scanned],
               "bytes_scanned": sum(p["bytes"] for p in parts), "bytes_total": sum(sizes),
               "rows_without_user_message": sum(p["no_user"] for p in parts),
               "rows_by_dataset_source": dict(sorted(collections.Counter(
                   {s: sum(p["sources"].get(s, 0) for p in parts) for p in parts for s in p["sources"]}).items())),
               "sets": {}}
    for name, fl in sets.items():
        c = collections.Counter(f["flag"] for f in fl.values())
        m = {"n": len(fl), "exact": c["exact"], "near": c["near"], "none": c["none"],
             "by_source": dict(sorted(collections.Counter(f"{f['source']}/{f['flag']}" for f in fl.values()).items())),
             "match_dataset_source": dict(sorted(collections.Counter(
                 f["evidence"]["dataset_source"] for f in fl.values() if f["flag"] != "none").items())),
             "problems_under_8_words": sum(len(norm(it["problem"]).split()) < 8
                                           for it in (math500 if name == "math500" else hard)
                                           if str(it["index"]) in fl),
             "short_contained": sum("short_contained" in f for f in fl.values())}
        if name in scores:
            if set(scores[name]) != set(fl):
                raise ValueError(f"{name}: scores and problems differ")
            m["think_sft_cue_accuracy"] = accuracy(fl, scores[name])
            m["scores_from"] = SCORES_MATH500 if name == "math500" else SCORES_HARD328
        metrics["sets"][name] = m
    run = {"command": "PYTHONPATH=. uv run --no-project --with huggingface_hub --with pyarrow --with numpy python -m "
                      "studies.rlneurons.analysis.wsp1_sft_overlap " + " ".join(sys.argv[1:]),
           "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
           "where": "laptop, CPU only", "wall_s": round(time.time() - t0),
           "versions": {"python": platform.python_version(), "pyarrow": pa.__version__, "numpy": numpy.__version__,
                        "huggingface_hub": huggingface_hub.__version__},
           "shards": [{k: p[k] for k in ("shard", "file", "bytes", "rows", "download_s", "scan_s")} for p in parts]}
    os.makedirs(a.out)
    for name, obj in (("run.json", run), ("metrics.json", metrics), ("flags.json", flags)):
        json.dump(obj, open(f"{a.out}/{name}", "w"), indent=1)
    print(json.dumps({k: v for k, v in metrics.items() if k != "rows_by_dataset_source"}, indent=1))


if __name__ == "__main__":
    main()
