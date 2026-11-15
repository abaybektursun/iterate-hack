"""Planted cases for analysis/shard_join.py, including inputs on which the join must fail.

    uv run --no-project python -m studies.rlneurons.analysis.shard_join_test
"""
from studies.rlneurons.analysis import shard_join as J


def run(k, n_shards, idx, **config):
    rows = [{"problem_index": i, "sample": 0, "attempt": 0, "score_v3": 1} for i in idx]
    counts = {**{key: len(rows) for key in J.SUM}, "generation_s": 10.0 + k, "tokens_per_s": 100.0}
    return ({"status": "done", "job_id": f"job{k}", "commit": "c", "wall_s": 20.0 + k, "counts": counts,
             "config": {"shard": f"{k}/{n_shards}", "n_problems": len(idx), "out": f"/out{k}", "seed": 7, "set": "math500", **config}}, rows)


def fails(runs, text):
    try:
        J.join(runs)
    except AssertionError as e:
        assert text in str(e), (text, str(e))
        return
    raise AssertionError(f"the join accepted a case that must fail: {text}")


def main():
    m, rows = J.join([run(1, 2, [1, 3]), run(0, 2, [0, 2, 4])])                    # given out of order
    assert [r["problem_index"] for r in rows] == [0, 2, 4, 1, 3]
    assert m["config"]["shard"] is None and m["config"]["n_problems"] == 5 and m["job_id"] == "job0+job1"
    assert m["counts"]["n"] == 5 and m["counts"]["generation_s"] == 11.0 and m["wall_s"] == 21.0 and m["counts"]["tokens_per_s"] == 200.0
    fails([run(0, 3, [0]), run(1, 3, [1])], "each once")                           # a shard is missing
    fails([run(0, 2, [0]), run(0, 2, [1])], "each once")                           # one shard twice
    fails([run(0, 2, [0, 2]), run(1, 2, [1, 2])], "also in shard")                 # a problem in two shards
    fails([run(0, 2, [0]), run(1, 2, [1], seed=8)], "['seed']")                    # another seed
    fails([run(0, 2, [0]), ({**run(1, 2, [1])[0], "status": "running"}, [])], "not done")
    fails([run(0, 2, [0]), ({**run(1, 2, [1, 3])[0]}, run(1, 2, [1])[1])], "planned")  # rows missing in a shard
    print("shard_join_test: 7 cases pass")


if __name__ == "__main__":
    main()
