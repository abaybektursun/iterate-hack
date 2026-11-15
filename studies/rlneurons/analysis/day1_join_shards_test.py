"""Planted cases for analysis/day1_join_shards.py: a complete join, a join with --missing-shard, and inputs that must be refused.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_join_shards_test
"""
import json

from studies.rlneurons.analysis import day1_join_shards as J

SEED, N_SH, SAMPLES = 3000000, 4, 4


def shard(k, whole, status="done", drop=None):
    """Shard k of N_SH of hard328 with SAMPLES samples per problem. drop: a (problem_index, sample) row left out."""
    idx = whole[k::N_SH]
    cfg = {"set": "hard328", "commit": "c", "n_problems": len(idx), "seed": SEED, "model": "rl", "prompt": "plain", "max_tokens": 16384,
           "sampling": {"temperature": 1.0}, "samples": SAMPLES, "restarts": 0, "out": f"/runs/job{k}"}
    rows = [{"problem_index": i, "sample": s, "attempt": 0, "seed": SEED + 10000 * s + i, "model": "rl", "prompt_arm": "plain",
             "max_tokens": 16384, "sampling": cfg["sampling"], "score_v3": int((i + s) % 3 == 0), "score": int((i + s) % 3 == 0),
             "cap_hit": False, "n_new": 100 + s} for i in idx for s in range(SAMPLES) if (i, s) != drop]
    counts = {"n": len(rows), "correct_v3": sum(r["score_v3"] for r in rows), "correct_v1": sum(r["score"] for r in rows), "cap_hits": 0,
              "loop_A": 0, "generated_tokens": sum(r["n_new"] for r in rows), "restarts": 0, "n_planned": len(rows), "generation_s": 1.0}
    m = {"status": status, "config": cfg, "commit": "c", "versions": {}, "job_id": f"job{k}", "memory": {"gpu": "g"}, "wall_s": 1.0,
         "started_utc": "a", "updated_utc": "b", "counts": counts}
    return (f"shard{k}", m, [json.dumps(r) for r in rows])


def raises(f):
    try:
        f()
    except AssertionError:
        return True
    return False


def main():
    whole = J.set_indices("hard328")
    sh = [shard(k, whole) for k in range(N_SH)]
    three = [sh[0], sh[1], sh[3]]

    met, lines = J.join(sh)
    assert met["config"]["n_problems"] == 328 and len(lines) == 328 * SAMPLES
    assert "partial" not in met["config"] and "missing" not in met["joined_from"] and met["job_id"] == "join:job0+job1+job2+job3"

    met, lines = J.join(three, (2, 4), "shard 2 was cancelled")
    got = sorted({json.loads(x)["problem_index"] for x in lines})
    assert got == sorted(set(whole) - set(whole[2::4])) and len(got) == 246 and len(lines) == 246 * SAMPLES
    assert met["config"]["n_problems"] == 246 and met["counts"]["n"] == 246 * SAMPLES
    assert met["config"]["partial"] == {"missing_shard": "2/4", "n_problems_of_set": 328, "n_problems_missing": 82, "reason": "shard 2 was cancelled"}
    miss = met["joined_from"]["missing"]
    assert miss["problem_indices"] == whole[2::4] and miss["positions_in_set"] == list(range(2, 328, 4)) and miss["reason"] == "shard 2 was cancelled"
    assert met["job_id"] == "join-partial(missing 2/4):job0+job1+job3"

    # inputs that must be refused
    assert raises(lambda: J.join(three)), "three of four shards without --missing-shard"
    assert raises(lambda: J.join(sh, (2, 4), "r")), "all four shards with --missing-shard"
    assert raises(lambda: J.join([sh[0], sh[1], sh[2]], (2, 4), "r")), "the folder of the shard named missing is given"
    assert raises(lambda: J.join([sh[0], sh[3], sh[1]], (2, 4), "r")), "shards out of order"
    assert raises(lambda: J.join(three, (2, 4), "")), "no reason"
    assert raises(lambda: J.join(three, (4, 4), "r")), "no such shard"
    assert raises(lambda: J.join(sh, None, "r")), "a reason without --missing-shard"
    assert raises(lambda: J.join([sh[0], sh[1], shard(3, whole, status="cancelled")], (2, 4), "r")), "a given shard that is not done"
    assert raises(lambda: J.join([sh[0], sh[1], shard(3, whole, drop=(whole[3], 2))], (2, 4), "r")), "a given shard with a missing sample"
    assert raises(lambda: J.join([sh[0], shard(1, whole, drop=(whole[1], 2)), sh[2], sh[3]])), "complete join with a missing sample"
    print("day1_join_shards_test: all cases pass")


if __name__ == "__main__":
    main()
