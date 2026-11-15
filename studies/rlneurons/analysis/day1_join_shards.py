"""Joins the shard runs of one run_cell cell (studies/metaharness/jobs/shard_cell.py --shard k/N) into one run folder that
day1_vote.py and day1_length_rules.py load: answers.jsonl (every shard's rows, unchanged, in problem, sample, attempt order)
and metrics.json (the shards' config with n_problems summed, counts summed, the shard job ids).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_join_shards \
        --out runs/<name> runs/<job of shard 0> runs/<job of shard 1> ... runs/<job of shard N-1>

The shard run folders are given in shard order (uv run tools/gpu.py get <job-id> gives runs/<job-id>/). --out is a new folder.

Asserted, else no folder is written: every shard has status done; commit, versions and config (all keys but out and n_problems)
are the same in every shard; shard k holds exactly the problems at positions k, k+N, ... of the set (so the shards are disjoint
and together the whole set); every row's seed follows the seed rule; each shard's counts equal its rows; the joined rows are a
complete run (day1_vote.chains: every problem has every sample, no duplicate row, restarts as configured).

metrics.json of the joined folder: job_id is "join:" + the shard job ids; counts are sums over shards (generation_s is GPU
seconds summed, tokens_per_s = generated tokens / that sum: a per-GPU rate); engine, memory and wall_s differ per shard and
are kept per shard under joined_from.shards, not at the top level.

An incomplete cell (one shard job has no usable output) is joined only with both flags:

    --missing-shard k/N --missing-reason "<why shard k has no usable rows>"   and the other N - 1 shard folders, in shard order

Asserted then, besides the checks above on every given shard: exactly N - 1 folders are given; the joined problems are the set
minus exactly the positions k, k+N, ... (no row of the missing shard, every other problem complete with every sample). The
joined folder then says it is partial in four places: PARTIAL.json (the missing positions, their problem_index values and the
reason), metrics.json config.partial and joined_from.missing, and job_id, which starts with "join-partial(missing k/N):".
config.n_problems is the number of problems joined; status stays "done" because every joined problem is complete. To put a
second model on the same problems, join its shards with the same --missing-shard. Without the flags nothing changes: a missing
shard is an assertion error.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from studies.rlneurons.analysis import day1_vote as V

STUDY = pathlib.Path(__file__).resolve().parents[1]
SUMMED = ("n", "correct_v3", "correct_v1", "cap_hits", "loop_A", "generated_tokens", "restarts", "n_planned", "generation_s")
PER_SHARD = ("out", "n_problems")


def set_indices(name: str) -> list:
    """The problem_index of every problem of the set, in the order of run_cell.problems (not imported: run_cell needs the GPU
    job's packages). hard328: the problems of data/rln3/hard.json with overlap flag "none", by index."""
    assert name == "hard328", f"set {name!r}: the order of its problem_index values is only written here for hard328"
    flags = json.loads((STUDY / "results" / "rln3" / "rln3_overlap.json").read_text())["sets"]["hard"]["flags"]
    clean = sorted(int(i) for i, f in flags.items() if f["flag"] == "none")
    assert len(clean) == 328, f"{len(clean)} problems with overlap flag none, not 328"
    return clean


def parse_shard(text: str) -> tuple:
    k, n = text.split("/")
    return int(k), int(n)


def join(shards: list, missing=None, reason=None) -> tuple:
    """shards: [(source path, metrics, raw lines of answers.jsonl)] in shard order. missing: None, or (k, N): shard k of N is
    absent and shards holds the other N - 1 in shard order; reason says why. Returns (joined metrics, joined lines)."""
    n_sh = len(shards) if missing is None else missing[1]
    present = list(range(n_sh))
    if missing is None:
        assert reason is None, "--missing-reason without --missing-shard"
    else:
        assert reason and reason.strip(), "--missing-shard needs --missing-reason: why the shard has no usable rows"
        assert 0 <= missing[0] < n_sh, f"--missing-shard {missing[0]}/{n_sh}: no such shard"
        assert len(shards) == n_sh - 1, f"--missing-shard {missing[0]}/{n_sh}: {len(shards)} shard folders given, exactly {n_sh - 1} needed (every shard but the missing one)"
        present.remove(missing[0])
    m0 = shards[0][1]
    c0 = m0["config"]
    whole = set_indices(c0["set"])
    joined, parts = [], []
    for k, (src, m, lines) in zip(present, shards):
        assert m["status"] == "done", f"{src}: status {m['status']!r}, not done"
        c = m["config"]
        assert m["commit"] == m0["commit"] == c["commit"], f"{src}: commit {m['commit']} differs from shard 0"
        assert m["versions"] == m0["versions"], f"{src}: versions differ from shard 0"
        diff = sorted(x for x in set(c) | set(c0) if x not in PER_SHARD and c.get(x) != c0.get(x))
        assert not diff, f"{src}: config differs from shard 0 in {diff}"
        rows = [json.loads(x) for x in lines]
        want = whole[k::n_sh]
        got = sorted({r["problem_index"] for r in rows})
        assert got == want, f"{src}: not shard {k}/{n_sh} of {c['set']} ({len(got)} problems, {len(set(got) ^ set(want))} differ)"
        assert c["n_problems"] == len(want), f"{src}: n_problems {c['n_problems']}, shard {k}/{n_sh} has {len(want)}"
        for r in rows:
            assert r["seed"] == c["seed"] + 10000 * r["sample"] + 1000 * r["attempt"] + r["problem_index"], f"{src}: seed of {r['problem_index'], r['sample'], r['attempt']}"
            assert (r["model"], r["prompt_arm"], r["max_tokens"], r["sampling"]) == (c["model"], c["prompt"], c["max_tokens"], c["sampling"]), f"{src}: a row of another cell"
        cn = m["counts"]
        mine = {"n": len(rows), "correct_v3": sum(r["score_v3"] for r in rows), "correct_v1": sum(r["score"] for r in rows),
                "cap_hits": sum(r["cap_hit"] for r in rows), "generated_tokens": sum(r["n_new"] for r in rows)}
        assert all(cn[x] == mine[x] for x in mine), f"{src}: counts {({x: cn[x] for x in mine})} differ from its rows {mine}"
        assert cn["n_planned"] == cn["n"], f"{src}: {cn['n']} rows of {cn['n_planned']} planned"
        joined += [(r["problem_index"], r["sample"], r["attempt"], x) for r, x in zip(rows, lines)]
        parts.append({"shard": f"{k}/{n_sh}", "job_id": m["job_id"], "source": str(src), "n_problems": c["n_problems"], "counts": cn,
                      "gpu": m["memory"]["gpu"], "wall_s": m["wall_s"], "started_utc": m["started_utc"], "updated_utc": m["updated_utc"]})
    joined.sort(key=lambda t: t[:3])
    lines = [t[3] for t in joined]
    absent_pos = [] if missing is None else list(range(missing[0], len(whole), n_sh))
    absent = [whole[p] for p in absent_pos]
    kept = sorted(set(whole) - set(absent))
    got = sorted({t[0] for t in joined})
    assert got == kept, f"the joined problems are not the set minus the missing shard ({len(got)} joined, {len(kept)} expected, {len(set(got) ^ set(kept))} differ)"
    assert not set(got) & set(absent), "a row of the missing shard is among the joined rows"
    cfg = {**{x: v for x, v in c0.items() if x not in PER_SHARD}, "n_problems": len(kept)}
    if missing is not None:
        cfg["partial"] = {"missing_shard": f"{missing[0]}/{n_sh}", "n_problems_of_set": len(whole), "n_problems_missing": len(absent), "reason": reason}
    V.chains([json.loads(x) for x in lines], cfg["n_problems"], cfg["samples"], cfg["restarts"])       # asserts a complete run
    counts = {x: sum(p["counts"][x] for p in parts) for x in SUMMED}
    counts["mean_generated_tokens"] = counts["generated_tokens"] / counts["n"]
    counts["tokens_per_s"] = counts["generated_tokens"] / counts["generation_s"]
    tag = "join:" if missing is None else f"join-partial(missing {missing[0]}/{n_sh}):"
    met = {"status": "done", "config": cfg, "commit": m0["commit"], "job_id": tag + "+".join(p["job_id"] for p in parts),
           "versions": m0["versions"], "started_utc": min(p["started_utc"] for p in parts), "updated_utc": max(p["updated_utc"] for p in parts),
           "counts": counts,
           "joined_from": {"script": "studies/rlneurons/analysis/day1_join_shards.py", "entry_point": "studies/metaharness/jobs/shard_cell.py",
                           "counts_are": "sums over the shards; generation_s is GPU seconds summed; tokens_per_s is per GPU",
                           "shards": parts}}
    if missing is not None:
        met["joined_from"]["missing"] = {"shard": f"{missing[0]}/{n_sh}", "reason": reason, "positions_in_set": absent_pos, "problem_indices": absent,
                                         "rule": "no row of the missing shard is joined; every other problem has every sample"}
    return met, lines


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--missing-shard", default=None, help="k/N: shard k of N has no usable rows; give the other N - 1 folders")
    ap.add_argument("--missing-reason", default=None, help="why (required with --missing-shard); written into the joined folder")
    ap.add_argument("shards", nargs="+", help="the shard run folders, in shard order")
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets a new folder"
    src = [pathlib.Path(p) for p in a.shards]
    met, lines = join([(p, json.loads((p / "metrics.json").read_text()), (p / "answers.jsonl").read_text().splitlines()) for p in src],
                      parse_shard(a.missing_shard) if a.missing_shard else None, a.missing_reason)
    met["config"]["out"] = str(out)
    out.mkdir(parents=True)
    (out / "answers.jsonl").write_text("\n".join(lines) + "\n")
    (out / "metrics.json").write_text(json.dumps(met, indent=1) + "\n")
    miss = met["joined_from"].get("missing")
    if miss:
        (out / "PARTIAL.json").write_text(json.dumps({**miss, "n_problems_joined": met["config"]["n_problems"],
                                                      "n_problems_of_set": met["config"]["partial"]["n_problems_of_set"]}, indent=1) + "\n")
        print(f"PARTIAL JOIN: shard {miss['shard']} is missing ({len(miss['problem_indices'])} problems, positions {miss['positions_in_set'][0]}, "
              f"{miss['positions_in_set'][1]}, ...): {miss['reason']}")
    s0 = [r for r in map(json.loads, lines) if r["sample"] == 0 and r["attempt"] == 0]
    c = met["counts"]
    print(f"{out}: {len(src)} shards, {met['config']['n_problems']} problems, {c['n']} rows, {c['generated_tokens']} generated tokens")
    print(f"sample 0, attempt 0 (the instrument check): {sum(r['score_v3'] for r in s0)} right of {len(s0)} (grader v3), "
          f"{sum(r['cap_hit'] for r in s0)} cap hits, {sum(r['n_new'] for r in s0) / len(s0):.0f} generated tokens per problem (n_new)")


if __name__ == "__main__":
    main()
